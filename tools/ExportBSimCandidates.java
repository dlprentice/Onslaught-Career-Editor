//@category BSim

import java.io.BufferedWriter;
import java.io.File;
import java.io.InputStream;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

import ghidra.app.script.GhidraScript;
import ghidra.features.bsim.query.BSimClientFactory;
import ghidra.features.bsim.query.BSimServerInfo;
import ghidra.features.bsim.query.FunctionDatabase;
import ghidra.features.bsim.query.GenSignatures;
import ghidra.features.bsim.query.description.DatabaseInformation;
import ghidra.features.bsim.query.description.ExecutableRecord;
import ghidra.features.bsim.query.description.FunctionDescription;
import ghidra.features.bsim.query.protocol.QueryNearest;
import ghidra.features.bsim.query.protocol.ResponseNearest;
import ghidra.features.bsim.query.protocol.SimilarityNote;
import ghidra.features.bsim.query.protocol.SimilarityResult;
import ghidra.framework.Application;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;

/**
 * Read-only, deterministic, address-driven BSim candidate export.
 *
 * Usage:
 *   -postScript ExportBSimCandidates.java
 *       <database-url> <database-snapshot> <expected-database-sha256>
 *       <output-tsv> <expected-program-md5> <expected-database-name>
 *       <expected-major> <expected-minor> <expected-settings>
 *       <expected-layout> <max-results> <similarity-bound>
 *       <confidence-bound> <address> [<address> ...]
 *
 * The script has no apply/rename path. It refuses to replace an existing
 * output, writes UTF-8 to a sibling temporary file, and publishes with an
 * atomic no-clobber hard link.  ATOMIC_MOVE is deliberately not used: the
 * Windows NIO provider may replace an existing destination even without
 * REPLACE_EXISTING.
 */
public class ExportBSimCandidates extends GhidraScript {

    private static final class Candidate {
        final String executableName;
        final String executableMd5;
        final long matchAddress;
        final String matchName;
        final double similarity;
        final double significance;

        Candidate(SimilarityNote note) {
            FunctionDescription match = note.getFunctionDescription();
            ExecutableRecord executable = match.getExecutableRecord();
            executableName = nonNull(executable.getNameExec());
            executableMd5 = nonNull(executable.getMd5());
            matchAddress = match.getAddress();
            matchName = nonNull(match.getFunctionName());
            similarity = note.getSimilarity();
            significance = note.getSignificance();
        }
    }

    private static String nonNull(String value) {
        return value == null ? "" : value;
    }

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", " ");
    }

    private static String hex(long value) {
        return String.format(Locale.ROOT, "0x%08x", value);
    }

    private static long parseHexAddress(String value) {
        String text = value.trim().toLowerCase(Locale.ROOT);
        if (text.startsWith("0x")) {
            text = text.substring(2);
        }
        return Long.parseUnsignedLong(text, 16);
    }

    private static String digest(Path path, String algorithm) throws Exception {
        MessageDigest value = MessageDigest.getInstance(algorithm);
        try (InputStream input = Files.newInputStream(path)) {
            byte[] buffer = new byte[1024 * 1024];
            int read;
            while ((read = input.read(buffer)) >= 0) {
                value.update(buffer, 0, read);
            }
        }
        StringBuilder result = new StringBuilder();
        for (byte item : value.digest()) {
            result.append(String.format(Locale.ROOT, "%02x", item & 0xff));
        }
        return result.toString();
    }

    private String functionTopology(Function function) {
        StringBuilder result = new StringBuilder();
        for (AddressRange range : function.getBody()) {
            if (result.length() != 0) {
                result.append(';');
            }
            result.append(range.getMinAddress())
                .append('-')
                .append(range.getMaxAddress());
        }
        return result.toString();
    }

    private String functionDigest(Function function) throws Exception {
        MessageDigest value = MessageDigest.getInstance("SHA-256");
        AddressSetView body = function.getBody();
        byte[] buffer = new byte[64 * 1024];
        for (AddressRange range : body) {
            Address cursor = range.getMinAddress();
            Address end = range.getMaxAddress();
            while (cursor.compareTo(end) <= 0) {
                long remaining = end.subtract(cursor) + 1;
                int requested = (int)Math.min((long)buffer.length, remaining);
                int read = currentProgram.getMemory().getBytes(
                    cursor, buffer, 0, requested);
                if (read != requested) {
                    throw new IllegalStateException(
                        "short body read at " + cursor);
                }
                value.update(buffer, 0, read);
                cursor = cursor.add(read);
            }
        }
        StringBuilder result = new StringBuilder();
        for (byte item : value.digest()) {
            result.append(String.format(Locale.ROOT, "%02x", item & 0xff));
        }
        return result.toString();
    }

    private static void row(BufferedWriter writer, String... values)
            throws Exception {
        for (int index = 0; index < values.length; ++index) {
            if (index != 0) {
                writer.write('\t');
            }
            writer.write(clean(values[index]));
        }
        writer.write('\n');
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 14) {
            throw new IllegalArgumentException(
                "usage: <database-url> <database-snapshot> " +
                "<expected-database-sha256> <output-tsv> " +
                "<expected-program-md5> <expected-database-name> " +
                "<expected-major> <expected-minor> <expected-settings> " +
                "<expected-layout> <max-results> <similarity-bound> " +
                "<confidence-bound> <address> [...]");
        }

        String databaseUrl = args[0];
        Path databaseSnapshot =
            new File(args[1]).toPath().toAbsolutePath().normalize();
        String expectedDatabaseSha256 = args[2].toLowerCase(Locale.ROOT);
        Path output = new File(args[3]).toPath().toAbsolutePath().normalize();
        String expectedProgramMd5 = args[4].toLowerCase(Locale.ROOT);
        String expectedDatabaseName = args[5];
        short expectedMajor = Short.parseShort(args[6]);
        short expectedMinor = Short.parseShort(args[7]);
        int expectedSettings = Integer.parseInt(args[8]);
        int expectedLayout = Integer.parseInt(args[9]);
        int maxResults = Integer.parseInt(args[10]);
        double similarityBound = Double.parseDouble(args[11]);
        double confidenceBound = Double.parseDouble(args[12]);
        if (maxResults <= 0 || !Double.isFinite(similarityBound) ||
                !Double.isFinite(confidenceBound)) {
            throw new IllegalArgumentException("invalid BSim query bounds");
        }
        if (!expectedDatabaseSha256.matches("[0-9a-f]{64}") ||
                !expectedProgramMd5.matches("[0-9a-f]{32}")) {
            throw new IllegalArgumentException(
                "expected database SHA-256/program MD5 is malformed");
        }
        if (!Files.isRegularFile(databaseSnapshot)) {
            throw new IllegalArgumentException(
                "database snapshot does not exist: " + databaseSnapshot);
        }
        if (Files.isWritable(databaseSnapshot)) {
            throw new IllegalArgumentException(
                "database snapshot must be a read-only query copy");
        }
        String databaseSha256Before = digest(databaseSnapshot, "SHA-256");
        if (!databaseSha256Before.equals(expectedDatabaseSha256)) {
            throw new IllegalArgumentException(
                "database snapshot SHA-256 mismatch: " +
                databaseSha256Before);
        }
        String programMd5 =
            nonNull(currentProgram.getExecutableMD5()).toLowerCase(Locale.ROOT);
        if (!programMd5.equals(expectedProgramMd5)) {
            throw new IllegalArgumentException(
                "current program MD5 mismatch: " + programMd5);
        }
        if (Files.exists(output)) {
            throw new IllegalArgumentException(
                "refusing to replace existing output: " + output);
        }
        Path parent = output.getParent();
        if (parent == null || !Files.isDirectory(parent)) {
            throw new IllegalArgumentException(
                "output parent must already exist: " + output);
        }
        Path temporary = parent.resolve(
            output.getFileName() + ".tmp-" + UUID.randomUUID());

        URL url = BSimClientFactory.deriveBSimURL(databaseUrl);
        BSimServerInfo serverInfo = new BSimServerInfo(url);
        Path urlDatabase = new File(serverInfo.getDBName())
            .toPath().toAbsolutePath().normalize();
        if (!urlDatabase.equals(databaseSnapshot)) {
            throw new IllegalArgumentException(
                "database URL and bound snapshot path disagree");
        }
        boolean published = false;
        try {
            try (FunctionDatabase database =
                    BSimClientFactory.buildClient(url, false)) {
                if (!database.initialize()) {
                    throw new IllegalStateException(
                        "BSim database initialization failed: " +
                        database.getLastError().message);
                }
                DatabaseInformation info = database.getInfo();
                if (info == null) {
                    throw new IllegalStateException(
                        "BSim database returned no identity information");
                }
                if (database.compareLayout() != 0 ||
                        !expectedDatabaseName.equals(info.databasename) ||
                        expectedMajor != info.major ||
                        expectedMinor != info.minor ||
                        expectedSettings != info.settings ||
                        expectedLayout != info.layout_version) {
                    throw new IllegalArgumentException(
                        "BSim database identity mismatch; actual=" +
                        nonNull(info.databasename) + "," + info.major + "," +
                        info.minor + "," + info.settings + "," +
                        info.layout_version + ",compareLayout=" +
                        database.compareLayout());
                }
                int failedQueries = 0;
                try (BufferedWriter writer = Files.newBufferedWriter(
                        temporary,
                        StandardCharsets.UTF_8,
                        StandardOpenOption.CREATE_NEW,
                        StandardOpenOption.WRITE)) {
                    writer.write("# schema=bea-bsim-candidates.v2\n");
                    writer.write("# ghidraVersion=" +
                        clean(Application.getApplicationVersion()) + "\n");
                    writer.write("# programMd5=" + programMd5 + "\n");
                    writer.write("# programImageBase=" +
                        currentProgram.getImageBase() + "\n");
                    writer.write("# programLanguage=" +
                        clean(currentProgram.getLanguageID().toString()) + "\n");
                    writer.write("# programCompilerSpec=" +
                        clean(currentProgram.getCompilerSpec()
                            .getCompilerSpecID().toString()) + "\n");
                    writer.write("# databaseSnapshotName=" +
                        clean(databaseSnapshot.getFileName().toString()) + "\n");
                    writer.write("# databaseSnapshotBytes=" +
                        Files.size(databaseSnapshot) + "\n");
                    writer.write("# databaseSnapshotSha256=" +
                        databaseSha256Before + "\n");
                    writer.write("# databaseSnapshotReadOnly=true\n");
                    writer.write("# databaseName=" +
                        clean(info.databasename) + "\n");
                    writer.write("# databaseMajor=" + info.major + "\n");
                    writer.write("# databaseMinor=" + info.minor + "\n");
                    writer.write("# databaseSettings=" + info.settings + "\n");
                    writer.write("# databaseLayout=" +
                        info.layout_version + "\n");
                    writer.write("# databaseCompareLayout=0\n");
                    writer.write("# maxResults=" + maxResults + "\n");
                    writer.write("# similarityBound=" +
                        Double.toString(similarityBound) + "\n");
                    writer.write("# confidenceBound=" +
                        Double.toString(confidenceBound) + "\n");
                row(writer, "query_address", "query_entry", "query_name",
                    "query_body_bytes", "query_body_topology",
                    "query_body_sha256", "status", "rank",
                    "match_executable", "match_md5", "match_address",
                    "match_name", "similarity", "confidence");

                for (int index = 13; index < args.length; ++index) {
                    monitor.checkCancelled();
                    long requestedOffset = parseHexAddress(args[index]);
                    Address requested = currentProgram.getAddressFactory()
                        .getDefaultAddressSpace().getAddress(requestedOffset);
                    Function function = currentProgram.getFunctionManager()
                        .getFunctionAt(requested);
                    if (function == null) {
                        row(writer, hex(requestedOffset), "", "", "", "",
                            "", "NO_FUNCTION", "", "", "", "", "", "", "");
                        continue;
                    }
                    String topology = functionTopology(function);
                    String bodySha256 = functionDigest(function);

                    GenSignatures generator = new GenSignatures(false);
                    try {
                        generator.setVectorFactory(database.getLSHVectorFactory());
                        generator.openProgram(
                            currentProgram, null, null, null, null, null);
                        generator.scanFunction(function);

                        QueryNearest query = new QueryNearest();
                        query.manage = generator.getDescriptionManager();
                        query.max = maxResults;
                        query.thresh = similarityBound;
                        query.signifthresh = confidenceBound;

                        ResponseNearest response = query.execute(database);
                        if (response == null) {
                            failedQueries++;
                            row(writer, hex(requestedOffset),
                                function.getEntryPoint().toString(),
                                function.getName(),
                                Long.toString(function.getBody().getNumAddresses()),
                                topology, bodySha256, "QUERY_ERROR", "", "",
                                "", "", "", "", "",
                                database.getLastError().message);
                            continue;
                        }

                        List<Candidate> candidates = new ArrayList<>();
                        Iterator<SimilarityResult> results =
                            response.result.iterator();
                        while (results.hasNext()) {
                            SimilarityResult result = results.next();
                            Iterator<SimilarityNote> notes = result.iterator();
                            while (notes.hasNext()) {
                                candidates.add(new Candidate(notes.next()));
                            }
                        }
                        candidates.sort((left, right) -> {
                            int comparison = Double.compare(
                                right.similarity, left.similarity);
                            if (comparison != 0) {
                                return comparison;
                            }
                            comparison = Double.compare(
                                right.significance, left.significance);
                            if (comparison != 0) {
                                return comparison;
                            }
                            comparison = left.executableName.compareTo(
                                right.executableName);
                            if (comparison != 0) {
                                return comparison;
                            }
                            comparison = Long.compareUnsigned(
                                left.matchAddress, right.matchAddress);
                            if (comparison != 0) {
                                return comparison;
                            }
                            comparison = left.matchName.compareTo(
                                right.matchName);
                            if (comparison != 0) {
                                return comparison;
                            }
                            return left.executableMd5.compareTo(
                                right.executableMd5);
                        });

                        int emitted = 0;
                        for (Candidate candidate : candidates) {
                            emitted++;
                                row(writer, hex(requestedOffset),
                                    function.getEntryPoint().toString(),
                                    function.getName(),
                                    Long.toString(
                                        function.getBody().getNumAddresses()),
                                    topology, bodySha256, "MATCH",
                                    Integer.toString(emitted),
                                    candidate.executableName,
                                    candidate.executableMd5,
                                    hex(candidate.matchAddress),
                                    candidate.matchName,
                                    String.format(
                                        Locale.ROOT, "%.17g",
                                        candidate.similarity),
                                    String.format(
                                        Locale.ROOT, "%.17g",
                                        candidate.significance));
                        }
                        if (emitted == 0) {
                            row(writer, hex(requestedOffset),
                                function.getEntryPoint().toString(),
                                function.getName(),
                                Long.toString(
                                    function.getBody().getNumAddresses()),
                                topology, bodySha256, "NO_MATCH", "", "", "",
                                "", "", "", "", "");
                        }
                    }
                    catch (Exception error) {
                        failedQueries++;
                        row(writer, hex(requestedOffset),
                            function.getEntryPoint().toString(),
                            function.getName(),
                            Long.toString(function.getBody().getNumAddresses()),
                            topology, bodySha256, "EXCEPTION", "", "", "", "",
                            "", error.getClass().getName(),
                            error.getMessage());
                    }
                    finally {
                        generator.dispose();
                    }
                }
                }
                if (failedQueries != 0) {
                    throw new IllegalStateException(
                        "refusing to publish: " + failedQueries +
                        " BSim query operation(s) failed");
                }
            }
            String databaseSha256After = digest(databaseSnapshot, "SHA-256");
            if (!databaseSha256Before.equals(databaseSha256After)) {
                throw new IllegalStateException(
                    "BSim database snapshot changed during read-only query: " +
                    databaseSha256Before + " -> " + databaseSha256After);
            }
            // The sibling temp is closed and flushed before this point.  A
            // hard-link create is atomic and fails if output already exists,
            // including when two exporters race.  Do not fall back to
            // ATOMIC_MOVE: on NTFS that can silently replace an existing file.
            Files.createLink(output, temporary);
            published = true;
            try {
                Files.delete(temporary);
            }
            catch (Exception cleanupError) {
                println(
                    "BSIM_EXPORT_TEMP_CLEANUP_WARNING temporary=" + temporary +
                    " error=" + cleanupError.getClass().getName()
                );
            }
        }
        finally {
            // Once the final hard link exists, publication succeeded even if
            // removal of the sibling link is interrupted. Cleanup is idempotent
            // and must not relabel a published output as a failed query.
            if (!published) {
                Files.deleteIfExists(temporary);
            }
        }

        println("BSIM_EXPORT_OK output=" + output);
    }
}
