//@category Battle Engine Aquila
//
// Read-only parity-lab export. Emits:
//   1. one inclusive row for every exact Ghidra function-body range;
//   2. aggregated static direct-call edges resolved to function entries;
//   3. a READY receipt, published last, that binds the pair by hash.
//
// Usage:
//   -postScript ExportParityLabGraph.java \
//       <body_ranges.tsv> <direct_calls.tsv> <parity_graph.ready.json>
//
// Run analyzeHeadless with -readOnly and -noanalysis. This script makes no
// program/database changes. It refuses existing outputs, writes CREATE_NEW
// sibling temporaries, then publishes hard links without clobbering.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

import java.io.BufferedWriter;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.UUID;

public class ExportParityLabGraph extends GhidraScript {

    private static final String TSV_SCHEMA = "bea-ghidra-parity-graph.v2";
    private static final String RECEIPT_SCHEMA =
        "bea-ghidra-parity-graph-receipt.v2";

    private static final class EdgeKey implements Comparable<EdgeKey> {
        final Address caller;
        final Address callee;

        EdgeKey(Address caller, Address callee) {
            this.caller = caller;
            this.callee = callee;
        }

        @Override
        public int compareTo(EdgeKey other) {
            int callerOrder = caller.compareTo(other.caller);
            return callerOrder != 0 ? callerOrder : callee.compareTo(other.callee);
        }
    }

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value
            .replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", " ");
    }

    private static String json(String value) {
        if (value == null) {
            return "";
        }
        StringBuilder result = new StringBuilder(value.length() + 16);
        for (int index = 0; index < value.length(); index++) {
            char item = value.charAt(index);
            switch (item) {
                case '"':
                    result.append("\\\"");
                    break;
                case '\\':
                    result.append("\\\\");
                    break;
                case '\b':
                    result.append("\\b");
                    break;
                case '\f':
                    result.append("\\f");
                    break;
                case '\n':
                    result.append("\\n");
                    break;
                case '\r':
                    result.append("\\r");
                    break;
                case '\t':
                    result.append("\\t");
                    break;
                default:
                    if (item < 0x20) {
                        result.append(String.format("\\u%04x", (int) item));
                    }
                    else {
                        result.append(item);
                    }
            }
        }
        return result.toString();
    }

    private static String hex(Address address) {
        return "0x" + address.toString();
    }

    private static String hex(byte[] value) {
        StringBuilder result = new StringBuilder(value.length * 2);
        for (byte item : value) {
            result.append(String.format("%02x", item & 0xff));
        }
        return result.toString();
    }

    private static String sha256(Path path) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[64 * 1024];
        try (java.io.InputStream input = Files.newInputStream(path)) {
            int read;
            while ((read = input.read(buffer)) >= 0) {
                if (read > 0) {
                    digest.update(buffer, 0, read);
                }
            }
        }
        return hex(digest.digest());
    }

    private static BufferedWriter createNewWriter(Path path) throws Exception {
        return Files.newBufferedWriter(
            path,
            StandardCharsets.UTF_8,
            StandardOpenOption.CREATE_NEW,
            StandardOpenOption.WRITE
        );
    }

    private void writeProgramIdentity(BufferedWriter writer) throws Exception {
        writer.write("# schema=" + TSV_SCHEMA + "\n");
        writer.write("# executableMd5=" + clean(currentProgram.getExecutableMD5()) + "\n");
        writer.write("# executablePath=" + clean(currentProgram.getExecutablePath()) + "\n");
        writer.write("# imageBase=" + hex(currentProgram.getImageBase()) + "\n");
        writer.write("# language=" + clean(currentProgram.getLanguageID().toString()) + "\n");
        writer.write(
            "# compilerSpec=" + clean(currentProgram.getCompilerSpec().getCompilerSpecID().toString())
                + "\n"
        );
    }

    private String rangeSha256(AddressRange range) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Address cursor = range.getMinAddress();
        Address end = range.getMaxAddress();
        byte[] buffer = new byte[64 * 1024];
        while (cursor.compareTo(end) <= 0) {
            monitor.checkCancelled();
            long remaining = end.subtract(cursor) + 1;
            int requested = (int) Math.min((long) buffer.length, remaining);
            int read = currentProgram.getMemory().getBytes(cursor, buffer, 0, requested);
            if (read != requested) {
                throw new IllegalStateException(
                    "short memory read at " + cursor + ": " + read + "/" + requested
                );
            }
            digest.update(buffer, 0, read);
            cursor = cursor.add(read);
        }
        return hex(digest.digest());
    }

    private static Path checkedFinalPath(String value) throws Exception {
        return new File(value).getCanonicalFile().toPath();
    }

    private static Path siblingTemporary(Path destination, String token) {
        return destination.resolveSibling(
            "." + destination.getFileName().toString() + "." + token + ".tmp"
        );
    }

    private static void deleteIfPresent(Path path) {
        if (path == null) {
            return;
        }
        try {
            Files.deleteIfExists(path);
        }
        catch (Exception ignored) {
            // Preserve the primary exception. An unlinked sibling temporary is
            // never a READY result and can be removed manually.
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 3) {
            throw new IllegalArgumentException(
                "usage: ExportParityLabGraph.java "
                    + "<body_ranges.tsv> <direct_calls.tsv> <parity_graph.ready.json>"
            );
        }

        Path rangesFinal = checkedFinalPath(args[0]);
        Path callsFinal = checkedFinalPath(args[1]);
        Path receiptFinal = checkedFinalPath(args[2]);
        Set<Path> destinations = new HashSet<>();
        destinations.add(rangesFinal);
        destinations.add(callsFinal);
        destinations.add(receiptFinal);
        if (destinations.size() != 3) {
            throw new IllegalArgumentException("parity-graph output paths must be distinct");
        }
        Path parent = rangesFinal.getParent();
        if (
            parent == null
                || !Files.isDirectory(parent)
                || !parent.equals(callsFinal.getParent())
                || !parent.equals(receiptFinal.getParent())
        ) {
            throw new IllegalArgumentException(
                "parity-graph outputs must share one existing canonical parent"
            );
        }
        for (Path destination : destinations) {
            if (Files.exists(destination)) {
                throw new IllegalStateException(
                    "refusing to overwrite parity-graph output: " + destination
                );
            }
        }

        String token = UUID.randomUUID().toString();
        Path rangesTemporary = siblingTemporary(rangesFinal, token);
        Path callsTemporary = siblingTemporary(callsFinal, token);
        Path receiptTemporary = siblingTemporary(receiptFinal, token);
        boolean rangesPublished = false;
        boolean callsPublished = false;
        boolean receiptPublished = false;
        int functionCount = 0;
        int rangeCount = 0;
        int callSites = 0;
        Map<EdgeKey, Integer> edges = new TreeMap<>();

        try {
            Listing listing = currentProgram.getListing();
            FunctionManager functions = currentProgram.getFunctionManager();

            try (BufferedWriter writer = createNewWriter(rangesTemporary)) {
                writeProgramIdentity(writer);
                writer.write(
                    "functionAddress\tfunctionName\trangeOrdinal\trangeMin\trangeMax"
                        + "\trangeEndExclusive\trangeBytes\trangeSha256\n"
                );
                FunctionIterator iterator = functions.getFunctions(true);
                while (iterator.hasNext()) {
                    monitor.checkCancelled();
                    Function function = iterator.next();
                    functionCount++;
                    int ordinal = 0;
                    AddressSetView body = function.getBody();
                    for (AddressRange range : body) {
                        monitor.checkCancelled();
                        ordinal++;
                        rangeCount++;
                        writer.write(
                            hex(function.getEntryPoint())
                                + "\t" + clean(function.getName(true))
                                + "\t" + ordinal
                                + "\t" + hex(range.getMinAddress())
                                + "\t" + hex(range.getMaxAddress())
                                + "\t" + hex(range.getMaxAddress().add(1))
                                + "\t" + range.getLength()
                                + "\t" + rangeSha256(range)
                                + "\n"
                        );
                    }
                }
            }

            // Instruction.getFlows() deliberately limits this graph to
            // statically resolved control-flow destinations. Computed/vtable
            // calls without a concrete target remain explicitly absent.
            FunctionIterator iterator = functions.getFunctions(true);
            while (iterator.hasNext()) {
                monitor.checkCancelled();
                Function caller = iterator.next();
                InstructionIterator instructions =
                    listing.getInstructions(caller.getBody(), true);
                while (instructions.hasNext()) {
                    monitor.checkCancelled();
                    Instruction instruction = instructions.next();
                    if (!instruction.getFlowType().isCall()) {
                        continue;
                    }
                    for (Address destination : instruction.getFlows()) {
                        Function callee = functions.getFunctionAt(destination);
                        if (callee == null || callee.isExternal()) {
                            continue;
                        }
                        EdgeKey key =
                            new EdgeKey(caller.getEntryPoint(), callee.getEntryPoint());
                        edges.put(key, edges.getOrDefault(key, 0) + 1);
                        callSites++;
                    }
                }
            }

            try (BufferedWriter writer = createNewWriter(callsTemporary)) {
                writeProgramIdentity(writer);
                writer.write(
                    "callerAddress\tcallerName\tcalleeAddress\tcalleeName\tcallSiteCount"
                        + "\tedgeKind\n"
                );
                for (Map.Entry<EdgeKey, Integer> row : edges.entrySet()) {
                    monitor.checkCancelled();
                    EdgeKey key = row.getKey();
                    Function caller = functions.getFunctionAt(key.caller);
                    Function callee = functions.getFunctionAt(key.callee);
                    writer.write(
                        hex(key.caller)
                            + "\t" + clean(caller == null ? "" : caller.getName(true))
                            + "\t" + hex(key.callee)
                            + "\t" + clean(callee == null ? "" : callee.getName(true))
                            + "\t" + row.getValue()
                            + "\tSTATIC_DIRECT\n"
                    );
                }
            }
            monitor.checkCancelled();

            long rangesBytes = Files.size(rangesTemporary);
            long callsBytes = Files.size(callsTemporary);
            String rangesSha256 = sha256(rangesTemporary);
            String callsSha256 = sha256(callsTemporary);
            try (BufferedWriter writer = createNewWriter(receiptTemporary)) {
                writer.write("{\n");
                writer.write("  \"schemaVersion\": \"" + RECEIPT_SCHEMA + "\",\n");
                writer.write("  \"program\": {\n");
                writer.write(
                    "    \"executableMd5\": \""
                        + json(clean(currentProgram.getExecutableMD5())) + "\",\n"
                );
                writer.write(
                    "    \"executablePath\": \""
                        + json(clean(currentProgram.getExecutablePath())) + "\",\n"
                );
                writer.write(
                    "    \"imageBase\": \"" + json(clean(hex(currentProgram.getImageBase())))
                        + "\",\n"
                );
                writer.write(
                    "    \"language\": \""
                        + json(clean(currentProgram.getLanguageID().toString())) + "\",\n"
                );
                writer.write(
                    "    \"compilerSpec\": \""
                        + json(
                            clean(
                                currentProgram.getCompilerSpec()
                                    .getCompilerSpecID()
                                    .toString()
                            )
                        ) + "\"\n"
                );
                writer.write("  },\n");
                writer.write("  \"bodyRanges\": {\n");
                writer.write(
                    "    \"file\": \"" + json(rangesFinal.getFileName().toString()) + "\",\n"
                );
                writer.write("    \"bytes\": " + rangesBytes + ",\n");
                writer.write("    \"sha256\": \"" + rangesSha256 + "\",\n");
                writer.write("    \"functionCount\": " + functionCount + ",\n");
                writer.write("    \"rangeCount\": " + rangeCount + "\n");
                writer.write("  },\n");
                writer.write("  \"directCalls\": {\n");
                writer.write(
                    "    \"file\": \"" + json(callsFinal.getFileName().toString()) + "\",\n"
                );
                writer.write("    \"bytes\": " + callsBytes + ",\n");
                writer.write("    \"sha256\": \"" + callsSha256 + "\",\n");
                writer.write("    \"directEdgeCount\": " + edges.size() + ",\n");
                writer.write("    \"directCallSiteCount\": " + callSites + "\n");
                writer.write("  }\n");
                writer.write("}\n");
            }
            monitor.checkCancelled();

            // No pair of file creates is crash-atomic. The READY receipt is the
            // commit marker: consumers reject the data files until this final
            // no-clobber link exists and all recorded hashes verify.
            Files.createLink(rangesFinal, rangesTemporary);
            rangesPublished = true;
            Files.createLink(callsFinal, callsTemporary);
            callsPublished = true;
            Files.createLink(receiptFinal, receiptTemporary);
            receiptPublished = true;

            println(
                "PARITY_GRAPH_OK functions=" + functionCount
                    + " ranges=" + rangeCount
                    + " directEdges=" + edges.size()
                    + " directCallSites=" + callSites
                    + " receipt=" + receiptFinal
            );
        }
        catch (Exception exception) {
            if (receiptPublished) {
                deleteIfPresent(receiptFinal);
            }
            if (callsPublished) {
                deleteIfPresent(callsFinal);
            }
            if (rangesPublished) {
                deleteIfPresent(rangesFinal);
            }
            throw exception;
        }
        finally {
            deleteIfPresent(receiptTemporary);
            deleteIfPresent(callsTemporary);
            deleteIfPresent(rangesTemporary);
        }
    }
}
