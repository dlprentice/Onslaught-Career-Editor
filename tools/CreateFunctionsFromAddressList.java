//@category Symbol
//
// Fail-closed function-boundary promotion for the specimen-bound BEA project.
//
// The script performs a complete read-only preflight before opening one atomic
// transaction.  It never assigns semantic names.  A caller must provide the
// exact SHA-256 and row count of an independently reviewed address list, choose
// an explicit mode, and require FUNCTION_PROMOTION_OK in the headless log.
// Ghidra headless can return exit code zero after a script exception, so process
// exit alone is not evidence that this script completed.
//
// Usage:
//   -postScript CreateFunctionsFromAddressList.java \
//       <addresses_file> <expected_sha256> <expected_count> \
//       <out_tsv> <out_ready_json> <dry|apply|readback>

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.MemoryBlock;

import java.io.File;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

public class CreateFunctionsFromAddressList extends GhidraScript {

    private static final String SCHEMA = "bea-ghidra-function-promotion.v2";
    private static final String EXPECTED_PROGRAM_NAME = "BEA.exe";
    private static final String EXPECTED_PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String EXPECTED_PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String EXPECTED_IMAGE_BASE = "00400000";
    private static final String EXPECTED_LANGUAGE = "x86:LE:32:default";
    private static final String EXPECTED_COMPILER_SPEC = "windows";
    private static final String EXPECTED_BLOCK = ".text";

    private static class Target {
        final String canonical;
        final Address address;

        Target(String canonical, Address address) {
            this.canonical = canonical;
            this.address = address;
        }
    }

    private static class Row {
        final Target target;
        final String status;
        final Function function;
        final String note;

        Row(Target target, String status, Function function, String note) {
            this.target = target;
            this.status = status;
            this.function = function;
            this.note = note;
        }
    }

    private static String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            out.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return out.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
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

    private static String json(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
    }

    private static String canonical(Address address) {
        return "0x" + address.toString().toLowerCase(Locale.ROOT);
    }

    private static String requireMode(String value) {
        String mode = value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
        if (!mode.equals("dry") && !mode.equals("apply") && !mode.equals("readback")) {
            throw new IllegalArgumentException("mode must be exactly dry, apply, or readback");
        }
        return mode;
    }

    private static void requireEqual(String field, String expected, String actual) {
        if (!expected.equals(actual)) {
            throw new IllegalStateException(
                field + " mismatch expected=" + expected + " actual=" + actual);
        }
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File file = new File(value).getCanonicalFile();
        if (file.exists()) {
            throw new IllegalArgumentException(label + " already exists: " + file);
        }
        File parent = file.getParentFile();
        if (parent == null || !parent.isDirectory()) {
            throw new IllegalArgumentException(label + " parent is not an existing directory: " + file);
        }
        return file;
    }

    private static File stageAtomic(File target, byte[] content) throws Exception {
        File parent = target.getParentFile();
        File partial = new File(parent, "." + target.getName() + ".partial-" + UUID.randomUUID());
        try (FileChannel channel = FileChannel.open(
                partial.toPath(), StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            ByteBuffer buffer = ByteBuffer.wrap(content);
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
            channel.force(true);
        }
        return partial;
    }

    private static void publishStaged(File partial, File target) throws Exception {
        if (!partial.getParentFile().equals(target.getParentFile())) {
            throw new IllegalStateException("staged and final receipts must share one directory");
        }
        // Hard-link publication is create-new: it cannot replace a target that
        // appears after preflight.  Both names refer to the already-synced bytes
        // until the private staged name is removed.
        Files.createLink(target.toPath(), partial.toPath());
        Files.delete(partial.toPath());
    }

    private static void discardStaged(File partial) throws Exception {
        if (partial != null) {
            Files.deleteIfExists(partial.toPath());
        }
    }

    private static void preflightAtomicWrite(File target, String label) throws Exception {
        File parent = target.getParentFile();
        File source = new File(parent, "." + target.getName() + ".write-probe-" + UUID.randomUUID());
        File linked = new File(parent, "." + target.getName() + ".link-probe-" + UUID.randomUUID());
        try {
            Files.write(
                source.toPath(), new byte[] { 0 },
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
            Files.createLink(linked.toPath(), source.toPath());
        } catch (Exception ex) {
            throw new IllegalStateException(
                label + " parent cannot publish a create-new receipt: " + parent, ex);
        } finally {
            Files.deleteIfExists(source.toPath());
            Files.deleteIfExists(linked.toPath());
        }
    }

    private byte[] readToolSource() throws Exception {
        try (InputStream stream = getSourceFile().getInputStream()) {
            return stream.readAllBytes();
        }
    }

    private List<Target> loadTargets(byte[] inputBytes, int expectedCount) throws Exception {
        String[] lines = new String(inputBytes, StandardCharsets.UTF_8).split("\\R", -1);
        List<Target> targets = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        int lineNumber = 0;
        for (String raw : lines) {
            lineNumber++;
            String line = raw.trim();
            int comment = line.indexOf('#');
            if (comment >= 0) {
                line = line.substring(0, comment).trim();
            }
            if (line.isEmpty()) {
                continue;
            }
            if (!line.matches("(?i)0x[0-9a-f]{8}")) {
                throw new IllegalArgumentException(
                    "line " + lineNumber + " must contain one canonical address and no name: " + raw);
            }
            Address address = toAddr(line);
            if (address == null) {
                throw new IllegalArgumentException("unresolvable address at line " + lineNumber + ": " + line);
            }
            String canonical = canonical(address);
            if (!seen.add(canonical)) {
                throw new IllegalArgumentException("duplicate target address: " + canonical);
            }
            targets.add(new Target(canonical, address));
        }
        if (targets.size() != expectedCount) {
            throw new IllegalArgumentException(
                "target count mismatch expected=" + expectedCount + " actual=" + targets.size());
        }
        return targets;
    }

    private Function exactFunction(Target target) {
        Function function = getFunctionAt(target.address);
        if (function != null && function.getEntryPoint().equals(target.address)) {
            return function;
        }
        Function containing = getFunctionContaining(target.address);
        if (containing != null && containing.getEntryPoint().equals(target.address)) {
            return containing;
        }
        return null;
    }

    private void validateTargetLocation(Target target) {
        MemoryBlock block = currentProgram.getMemory().getBlock(target.address);
        if (block == null) {
            throw new IllegalStateException("target is outside memory: " + target.canonical);
        }
        if (!EXPECTED_BLOCK.equals(block.getName()) || !block.isExecute() || !block.isInitialized()) {
            throw new IllegalStateException(
                "target is not initialized executable .text: " + target.canonical
                + " block=" + block.getName()
                + " execute=" + block.isExecute()
                + " initialized=" + block.isInitialized());
        }
        Function containing = getFunctionContaining(target.address);
        if (containing != null && !containing.getEntryPoint().equals(target.address)) {
            throw new IllegalStateException(
                "target lies inside existing function: " + target.canonical
                + " containing=" + canonical(containing.getEntryPoint()));
        }
        Instruction instruction = currentProgram.getListing().getInstructionAt(target.address);
        if (instruction == null) {
            throw new IllegalStateException(
                "target has no defined instruction; boundary promotion never disassembles: "
                + target.canonical);
        }
    }

    private void validateProgramIdentity() {
        if (currentProgram == null) {
            throw new IllegalStateException("no current Ghidra program");
        }
        requireEqual("program name", EXPECTED_PROGRAM_NAME, currentProgram.getName());
        String md5 = currentProgram.getExecutableMD5();
        requireEqual(
            "imported executable md5", EXPECTED_PROGRAM_MD5,
            md5 == null ? "" : md5.toLowerCase(Locale.ROOT));
        String sha256 = currentProgram.getExecutableSHA256();
        requireEqual(
            "imported executable sha256", EXPECTED_PROGRAM_SHA256,
            sha256 == null ? "" : sha256.toLowerCase(Locale.ROOT));
        requireEqual(
            "image base", EXPECTED_IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        requireEqual("language", EXPECTED_LANGUAGE, currentProgram.getLanguageID().toString());
        requireEqual(
            "compiler spec", EXPECTED_COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        println(
            "FUNCTION_PROMOTION_PROGRAM_OK name=" + currentProgram.getName()
            + " md5=" + EXPECTED_PROGRAM_MD5
            + " sha256=" + EXPECTED_PROGRAM_SHA256
            + " imageBase=0x" + EXPECTED_IMAGE_BASE
            + " language=" + EXPECTED_LANGUAGE
            + " compiler=" + EXPECTED_COMPILER_SPEC);
    }

    private static long instructionCount(Function function, ghidra.program.model.listing.Listing listing) {
        long count = 0;
        InstructionIterator iterator = listing.getInstructions(function.getBody(), true);
        while (iterator.hasNext()) {
            iterator.next();
            count++;
        }
        return count;
    }

    private static long programInstructionCount(ghidra.program.model.listing.Listing listing) {
        long count = 0;
        InstructionIterator iterator = listing.getInstructions(true);
        while (iterator.hasNext()) {
            iterator.next();
            count++;
        }
        return count;
    }

    private byte[] buildTsv(List<Row> rows) throws Exception {
        StringBuilder out = new StringBuilder();
        out.append("address\tstatus\tname\tnameSource\tbodyBytes\tbodyMin\tbodyMax\tbodyRanges\tinstrCount\tnote\n");
        for (Row row : rows) {
            Function function = row.function;
            AddressSetView body = function == null ? null : function.getBody();
            out.append(row.target.canonical).append('\t');
            out.append(row.status).append('\t');
            out.append(function == null ? "" : clean(function.getName())).append('\t');
            out.append(function == null || function.getSymbol() == null
                ? "" : function.getSymbol().getSource().toString()).append('\t');
            out.append(body == null ? "" : body.getNumAddresses()).append('\t');
            out.append(body == null || body.getMinAddress() == null
                ? "" : canonical(body.getMinAddress())).append('\t');
            out.append(body == null || body.getMaxAddress() == null
                ? "" : canonical(body.getMaxAddress())).append('\t');
            out.append(body == null ? "" : body.getNumAddressRanges()).append('\t');
            out.append(function == null ? "" : instructionCount(function, currentProgram.getListing())).append('\t');
            out.append(clean(row.note)).append('\n');
        }
        return out.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static String semanticTargetSha(List<Target> targets) throws Exception {
        List<String> addresses = new ArrayList<>();
        for (Target target : targets) {
            addresses.add(target.canonical);
        }
        Collections.sort(addresses);
        StringBuilder canonicalSet = new StringBuilder();
        for (String address : addresses) {
            canonicalSet.append(address).append('\n');
        }
        return sha256(canonicalSet.toString().getBytes(StandardCharsets.UTF_8));
    }

    private byte[] buildReady(
            String mode,
            String toolPath,
            int toolByteCount,
            String toolSha,
            File input,
            int inputByteCount,
            String inputSha,
            int expectedCount,
            List<Target> targets,
            File output,
            byte[] outputBytes,
            int wouldCreate,
            int created,
            int alreadyExists,
            int verified,
            long programInstructionsBefore,
            long programInstructionsAfter,
            boolean mutationCommitted) throws Exception {
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schemaVersion\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"").append(json(Instant.now().toString())).append("\",\n");
        ready.append("  \"mode\": \"").append(json(mode)).append("\",\n");
        ready.append("  \"tool\": {\n");
        ready.append("    \"path\": \"").append(json(toolPath)).append("\",\n");
        ready.append("    \"bytes\": ").append(toolByteCount).append(",\n");
        ready.append("    \"sha256\": \"").append(toolSha).append("\"\n");
        ready.append("  },\n");
        ready.append("  \"program\": {\n");
        ready.append("    \"name\": \"").append(EXPECTED_PROGRAM_NAME).append("\",\n");
        ready.append("    \"executableMd5\": \"").append(EXPECTED_PROGRAM_MD5).append("\",\n");
        ready.append("    \"executableSha256\": \"").append(EXPECTED_PROGRAM_SHA256).append("\",\n");
        ready.append("    \"imageBase\": \"0x").append(EXPECTED_IMAGE_BASE).append("\",\n");
        ready.append("    \"language\": \"").append(EXPECTED_LANGUAGE).append("\",\n");
        ready.append("    \"compilerSpec\": \"").append(EXPECTED_COMPILER_SPEC).append("\"\n");
        ready.append("  },\n");
        ready.append("  \"input\": {\n");
        ready.append("    \"path\": \"").append(json(input.getCanonicalPath())).append("\",\n");
        ready.append("    \"bytes\": ").append(inputByteCount).append(",\n");
        ready.append("    \"sha256\": \"").append(inputSha).append("\",\n");
        ready.append("    \"expectedCount\": ").append(expectedCount).append(",\n");
        ready.append("    \"semanticTargetSetSha256\": \"")
            .append(semanticTargetSha(targets)).append("\"\n");
        ready.append("  },\n");
        ready.append("  \"output\": {\n");
        ready.append("    \"path\": \"").append(json(output.getCanonicalPath())).append("\",\n");
        ready.append("    \"bytes\": ").append(outputBytes.length).append(",\n");
        ready.append("    \"sha256\": \"").append(sha256(outputBytes)).append("\"\n");
        ready.append("  },\n");
        ready.append("  \"counts\": {\n");
        ready.append("    \"targets\": ").append(targets.size()).append(",\n");
        ready.append("    \"wouldCreate\": ").append(wouldCreate).append(",\n");
        ready.append("    \"created\": ").append(created).append(",\n");
        ready.append("    \"alreadyExists\": ").append(alreadyExists).append(",\n");
        ready.append("    \"verified\": ").append(verified).append(",\n");
        ready.append("    \"programInstructionsBefore\": ")
            .append(programInstructionsBefore).append(",\n");
        ready.append("    \"programInstructionsAfter\": ")
            .append(programInstructionsAfter).append("\n");
        ready.append("  },\n");
        ready.append("  \"namesAuthorized\": false,\n");
        ready.append("  \"mutationCommitted\": ").append(mutationCommitted).append(",\n");
        ready.append("  \"allTargetsVerified\": ")
            .append(mode.equals("apply") || mode.equals("readback")).append("\n");
        ready.append("}\n");
        return ready.toString().getBytes(StandardCharsets.UTF_8);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 6) {
            throw new IllegalArgumentException(
                "usage: <addresses_file> <expected_sha256> <expected_count> "
                + "<out_tsv> <out_ready_json> <dry|apply|readback>");
        }

        File input = new File(args[0]).getCanonicalFile();
        if (!input.isFile()) {
            throw new IllegalArgumentException("address list is not a file: " + input);
        }
        String expectedSha = args[1].trim().toLowerCase(Locale.ROOT);
        if (!expectedSha.matches("[0-9a-f]{64}")) {
            throw new IllegalArgumentException("expected_sha256 must be 64 lowercase hexadecimal characters");
        }
        int expectedCount;
        try {
            expectedCount = Integer.parseInt(args[2]);
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException("expected_count must be a positive integer", ex);
        }
        if (expectedCount <= 0) {
            throw new IllegalArgumentException("expected_count must be a positive integer");
        }
        File output = requireNewOutput(args[3], "output TSV");
        File readyFile = requireNewOutput(args[4], "READY receipt");
        if (output.equals(readyFile)) {
            throw new IllegalArgumentException("output TSV and READY receipt must be distinct");
        }
        preflightAtomicWrite(output, "output TSV");
        preflightAtomicWrite(readyFile, "READY receipt");
        String mode = requireMode(args[5]);

        String toolPath = getSourceFile().getCanonicalPath();
        byte[] toolBytes = readToolSource();
        String toolSha = sha256(toolBytes);
        println(
            "FUNCTION_PROMOTION_TOOL_OK path=" + toolPath
            + " bytes=" + toolBytes.length
            + " sha256=" + toolSha);

        byte[] inputBytes = Files.readAllBytes(input.toPath());
        String actualSha = sha256(inputBytes);
        requireEqual("address-list sha256", expectedSha, actualSha);
        validateProgramIdentity();
        List<Target> targets = loadTargets(inputBytes, expectedCount);

        int presentBefore = 0;
        for (Target target : targets) {
            monitor.checkCancelled();
            validateTargetLocation(target);
            if (exactFunction(target) != null) {
                presentBefore++;
            }
        }
        if (mode.equals("readback") && presentBefore != targets.size()) {
            throw new IllegalStateException(
                "readback requires every target to exist expected=" + targets.size()
                + " actual=" + presentBefore);
        }
        println(
            "FUNCTION_PROMOTION_PREFLIGHT_OK mode=" + mode
            + " targets=" + targets.size()
            + " present=" + presentBefore
            + " missing=" + (targets.size() - presentBefore)
            + " inputSha256=" + actualSha);

        List<Row> rows = new ArrayList<>();
        int wouldCreate = 0;
        int created = 0;
        int alreadyExists = 0;
        int verified = 0;
        boolean mutationCommitted = false;
        long programInstructionsBefore = programInstructionCount(currentProgram.getListing());
        long programInstructionsAfter = programInstructionsBefore;
        File stagedOutput = null;
        File stagedReady = null;

        if (mode.equals("dry")) {
            for (Target target : targets) {
                Function function = exactFunction(target);
                if (function == null) {
                    wouldCreate++;
                    rows.add(new Row(target, "would_create", null, "dry-run; no mutation"));
                } else {
                    alreadyExists++;
                    rows.add(new Row(target, "already_exists", function, "present before dry-run"));
                }
            }
        } else if (mode.equals("readback")) {
            for (Target target : targets) {
                Function function = exactFunction(target);
                if (function == null) {
                    throw new IllegalStateException("function disappeared during readback: " + target.canonical);
                }
                verified++;
                rows.add(new Row(target, "verified", function, "exact entry-point readback"));
            }
        } else {
            int transactionId = currentProgram.startTransaction(
                "Promote " + targets.size() + " evidence-backed function boundaries");
            boolean commit = false;
            try {
                for (Target target : targets) {
                    monitor.checkCancelled();
                    validateTargetLocation(target);
                    Function function = exactFunction(target);
                    if (function != null) {
                        alreadyExists++;
                        rows.add(new Row(target, "already_exists", function, "present before apply"));
                        continue;
                    }
                    function = createFunction(target.address, null);
                    if (function == null || !function.getEntryPoint().equals(target.address)) {
                        throw new IllegalStateException("function creation failed: " + target.canonical);
                    }
                    created++;
                    rows.add(new Row(
                        target, "created", function,
                        "created over an existing defined instruction; no disassembly"));
                }
                for (Target target : targets) {
                    Function function = exactFunction(target);
                    if (function == null) {
                        throw new IllegalStateException("post-apply verification failed: " + target.canonical);
                    }
                    verified++;
                }
                if (created + alreadyExists != targets.size() || verified != targets.size()) {
                    throw new IllegalStateException(
                        "apply accounting mismatch targets=" + targets.size()
                        + " created=" + created
                        + " already=" + alreadyExists
                        + " verified=" + verified);
                }
                programInstructionsAfter = programInstructionCount(currentProgram.getListing());
                if (programInstructionsAfter != programInstructionsBefore) {
                    throw new IllegalStateException(
                        "boundary promotion changed the program instruction count before="
                        + programInstructionsBefore + " after=" + programInstructionsAfter);
                }
                byte[] outputBytes = buildTsv(rows);
                byte[] readyBytes = buildReady(
                    mode, toolPath, toolBytes.length, toolSha,
                    input, inputBytes.length, actualSha, expectedCount, targets, output, outputBytes,
                    wouldCreate, created, alreadyExists, verified,
                    programInstructionsBefore, programInstructionsAfter, true);
                stagedOutput = stageAtomic(output, outputBytes);
                stagedReady = stageAtomic(readyFile, readyBytes);
                commit = true;
            } finally {
                try {
                    currentProgram.endTransaction(transactionId, commit);
                } finally {
                    if (!commit) {
                        discardStaged(stagedOutput);
                        discardStaged(stagedReady);
                        stagedOutput = null;
                        stagedReady = null;
                    }
                }
            }
            if (!commit) {
                throw new IllegalStateException("promotion transaction rolled back");
            }
            mutationCommitted = true;
        }

        if (!mode.equals("apply")) {
            programInstructionsAfter = programInstructionCount(currentProgram.getListing());
            if (programInstructionsAfter != programInstructionsBefore) {
                throw new IllegalStateException(
                    "read-only promotion mode changed the program instruction count before="
                    + programInstructionsBefore + " after=" + programInstructionsAfter);
            }
            byte[] outputBytes = buildTsv(rows);
            byte[] readyBytes = buildReady(
                mode, toolPath, toolBytes.length, toolSha,
                input, inputBytes.length, actualSha, expectedCount, targets, output, outputBytes,
                wouldCreate, created, alreadyExists, verified,
                programInstructionsBefore, programInstructionsAfter, false);
            stagedOutput = stageAtomic(output, outputBytes);
            stagedReady = stageAtomic(readyFile, readyBytes);
        }

        try {
            publishStaged(stagedOutput, output);
            stagedOutput = null;
            publishStaged(stagedReady, readyFile);
            stagedReady = null;
        } catch (Exception ex) {
            if (mutationCommitted) {
                println(
                    "FUNCTION_PROMOTION_RECEIPT_LOST mode=" + mode
                    + " targets=" + targets.size()
                    + " input_sha256=" + actualSha
                    + " created=" + created
                    + " mutation_committed=true"
                    + " recovery=RESTORE_VERIFIED_BACKUP_BEFORE_RETRY"
                    + " error=" + clean(ex.toString()));
            }
            throw ex;
        } finally {
            discardStaged(stagedOutput);
            discardStaged(stagedReady);
        }

        println(
            "FUNCTION_PROMOTION_OK mode=" + mode
            + " targets=" + targets.size()
            + " would_create=" + wouldCreate
            + " created=" + created
            + " already_exists=" + alreadyExists
            + " verified=" + verified
            + " mutation_committed=" + mutationCommitted);
    }
}
