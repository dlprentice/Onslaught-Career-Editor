//@category Symbol
//
// Read-only, manifest-bound symbol census for prospective function creation.
// Emits one explicit row for every target, including targets with no symbol,
// and a digest of every symbol outside the target set.  The latter prevents a
// compensated symbol mutation elsewhere from hiding behind unchanged counts.
//
// Usage:
//   -postScript ExportTargetSymbolInventory.java \
//     <manifest.tsv> <manifest_sha256> <expected_count> \
//     <target_symbols.tsv> <target_symbols.ready.json>

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.symbol.Symbol;

import java.io.BufferedWriter;
import java.io.File;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.charset.CharacterCodingException;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.channels.FileChannel;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

public class ExportTargetSymbolInventory extends GhidraScript {
    private static final String SCHEMA = "bea.re.ghidra-target-symbol-inventory.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String MANIFEST_HEADER =
        "entry\texpectedRanges\texpectedBodyBytes\texpectedRangeDigest"
        + "\texpectedBodyBytesSha256\texpectedInstructionCount\texpectedIsThunk"
        + "\texpectedThunkTarget\tforbiddenEntries\tresidualEntityKeys\tquestionIds"
        + "\tcontractIds\tpromotionLane";

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\r", "\\r")
            .replace("\n", "\\n").replace("\t", " ");
    }

    private static String hex(byte[] raw) {
        StringBuilder result = new StringBuilder();
        for (byte value : raw) {
            result.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return result.toString();
    }

    private static String sha256(byte[] raw) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(raw));
    }

    private static void digestString(MessageDigest digest, String value) {
        byte[] raw = value.getBytes(StandardCharsets.UTF_8);
        digest.update((byte) ((raw.length >>> 24) & 0xff));
        digest.update((byte) ((raw.length >>> 16) & 0xff));
        digest.update((byte) ((raw.length >>> 8) & 0xff));
        digest.update((byte) (raw.length & 0xff));
        digest.update(raw);
    }

    private static String sortedDigest(List<String> rows) throws Exception {
        Collections.sort(rows);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (String row : rows) {
            digestString(digest, row);
        }
        return hex(digest.digest());
    }

    private static String strictUtf8(byte[] raw) throws CharacterCodingException {
        return StandardCharsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT)
            .decode(ByteBuffer.wrap(raw)).toString();
    }

    private static File requireInput(String value, String label) throws Exception {
        File input = new File(value).getCanonicalFile();
        if (!input.isFile()) {
            throw new IllegalArgumentException(label + " is not a file: " + input);
        }
        return input;
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        if (output.exists()) {
            throw new IllegalArgumentException(label + " already exists: " + output);
        }
        File parent = output.getParentFile();
        if (parent == null || !parent.isDirectory()) {
            throw new IllegalArgumentException(label + " parent is not an existing directory: " + output);
        }
        return output;
    }

    private static File partialFor(File output) {
        return new File(output.getParentFile(), "." + output.getName() + ".partial-" + UUID.randomUUID());
    }

    private static void force(File file) throws Exception {
        try (FileChannel channel = FileChannel.open(file.toPath(), StandardOpenOption.WRITE)) {
            channel.force(true);
        }
    }

    private static void publish(File partial, File output) throws Exception {
        Files.createLink(output.toPath(), partial.toPath());
        Files.delete(partial.toPath());
    }

    private static String json(String value) {
        StringBuilder result = new StringBuilder("\"");
        for (int index = 0; index < value.length(); index++) {
            char ch = value.charAt(index);
            switch (ch) {
                case '\\': result.append("\\\\"); break;
                case '"': result.append("\\\""); break;
                case '\b': result.append("\\b"); break;
                case '\f': result.append("\\f"); break;
                case '\n': result.append("\\n"); break;
                case '\r': result.append("\\r"); break;
                case '\t': result.append("\\t"); break;
                default:
                    if (ch < 0x20) {
                        result.append(String.format(Locale.ROOT, "\\u%04x", (int) ch));
                    } else {
                        result.append(ch);
                    }
            }
        }
        return result.append('"').toString();
    }

    private String symbolRow(Address address, Symbol symbol) {
        String namespace = symbol.getParentNamespace() == null
            ? "" : symbol.getParentNamespace().getName(true);
        return address + "\t" + clean(symbol.getName()) + "\t"
            + clean(symbol.getName(true)) + "\t" + clean(namespace) + "\t"
            + symbol.getSymbolType() + "\t" + symbol.getSource() + "\t"
            + symbol.isPrimary() + "\t" + symbol.isDynamic() + "\t"
            + symbol.isExternal() + "\t" + symbol.isPinned();
    }

    private void requireProgramIdentity() {
        if (!PROGRAM_NAME.equals(currentProgram.getName())
                || !PROGRAM_MD5.equalsIgnoreCase(currentProgram.getExecutableMD5())
                || !PROGRAM_SHA256.equalsIgnoreCase(currentProgram.getExecutableSHA256())
                || !IMAGE_BASE.equalsIgnoreCase(currentProgram.getImageBase().toString())
                || !LANGUAGE.equals(currentProgram.getLanguageID().toString())
                || !COMPILER_SPEC.equals(currentProgram.getCompilerSpec().getCompilerSpecID().toString())) {
            throw new IllegalStateException("program identity differs from the pristine BEA authority");
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 5) {
            throw new IllegalArgumentException(
                "usage: <manifest.tsv> <manifest_sha256> <expected_count> <output.tsv> <ready.json>");
        }
        requireProgramIdentity();
        File manifest = requireInput(args[0], "manifest");
        String suppliedManifestSha256 = args[1].toLowerCase(Locale.ROOT);
        if (!suppliedManifestSha256.matches("[0-9a-f]{64}")) {
            throw new IllegalArgumentException("manifest SHA-256 is malformed");
        }
        int expectedCount = Integer.parseInt(args[2]);
        if (expectedCount <= 0) {
            throw new IllegalArgumentException("expected count must be positive");
        }
        File output = requireNewOutput(args[3], "target-symbol output");
        File ready = requireNewOutput(args[4], "target-symbol READY");
        if (output.equals(ready)) {
            throw new IllegalArgumentException("output and READY must differ");
        }
        byte[] manifestBytes = Files.readAllBytes(manifest.toPath());
        String actualManifestSha256 = sha256(manifestBytes);
        if (!actualManifestSha256.equals(suppliedManifestSha256)) {
            throw new IllegalArgumentException("manifest SHA-256 mismatch");
        }
        String manifestText = strictUtf8(manifestBytes);
        if (manifestText.indexOf('\r') >= 0 || !manifestText.endsWith("\n")
                || manifestText.endsWith("\n\n")) {
            throw new IllegalArgumentException("manifest line endings are not canonical LF");
        }
        String[] lines = manifestText.substring(0, manifestText.length() - 1).split("\n", -1);
        if (lines.length != expectedCount + 1 || !MANIFEST_HEADER.equals(lines[0])) {
            throw new IllegalArgumentException("manifest header/count differs");
        }
        List<String> entries = new ArrayList<>();
        Set<Address> targets = new HashSet<>();
        for (int index = 1; index < lines.length; index++) {
            String[] fields = lines[index].split("\t", -1);
            if (fields.length != 13 || !fields[0].matches("0x[0-9a-f]{8}")) {
                throw new IllegalArgumentException("manifest row is malformed at line " + (index + 1));
            }
            Address address = toAddr(fields[0]);
            if (!currentProgram.getMemory().contains(address) || !targets.add(address)) {
                throw new IllegalArgumentException("manifest target is invalid or duplicated: " + fields[0]);
            }
            entries.add(fields[0]);
        }
        List<String> sortedEntries = new ArrayList<>(entries);
        Collections.sort(sortedEntries);
        if (!entries.equals(sortedEntries)) {
            throw new IllegalArgumentException("manifest targets are not strictly sorted");
        }

        Map<Address, List<Symbol>> targetSymbols = new HashMap<>();
        List<String> outsideRows = new ArrayList<>();
        for (Symbol symbol : currentProgram.getSymbolTable().getAllSymbols(true)) {
            monitor.checkCancelled();
            Address address = symbol.getAddress();
            if (targets.contains(address)) {
                targetSymbols.computeIfAbsent(address, ignored -> new ArrayList<>()).add(symbol);
            } else {
                outsideRows.add(symbolRow(address, symbol));
            }
        }

        int zeroSymbols = 0;
        int dynamicDefaultLabels = 0;
        int nonDynamicDefaultFunctions = 0;
        List<String> targetRows = new ArrayList<>();
        for (String entry : entries) {
            Address address = toAddr(entry);
            List<Symbol> symbols = targetSymbols.getOrDefault(address, Collections.emptyList());
            symbols.sort(Comparator.comparing(symbol -> symbolRow(address, symbol)));
            if (symbols.size() > 1) {
                throw new IllegalStateException("target has multiple symbols: " + entry);
            }
            if (symbols.isEmpty()) {
                zeroSymbols++;
                targetRows.add(entry + "\t0\t\t\t\t\t\t\t\t\t");
                continue;
            }
            Symbol symbol = symbols.get(0);
            if (symbol.getSymbolType().toString().equals("Label")
                    && symbol.getSource().toString().equals("DEFAULT") && symbol.isDynamic()) {
                dynamicDefaultLabels++;
            }
            if (symbol.getSymbolType().toString().equals("Function")
                    && symbol.getSource().toString().equals("DEFAULT") && !symbol.isDynamic()) {
                nonDynamicDefaultFunctions++;
            }
            targetRows.add(entry + "\t1\t" + symbolRow(address, symbol).substring(9));
        }

        File outputPartial = partialFor(output);
        File readyPartial = partialFor(ready);
        try {
            try (BufferedWriter writer = Files.newBufferedWriter(
                    outputPartial.toPath(), StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
                writer.write("entry\tsymbolCount\tname\tfqname\tnamespace\ttype\tsource"
                    + "\tprimary\tdynamic\texternal\tpinned\n");
                for (String row : targetRows) {
                    writer.write(row);
                    writer.write("\n");
                }
            }
            force(outputPartial);
            publish(outputPartial, output);

            byte[] toolBytes;
            try (InputStream stream = getSourceFile().getInputStream()) {
                toolBytes = stream.readAllBytes();
            }
            byte[] outputBytes = Files.readAllBytes(output.toPath());
            String outsideDigest = sortedDigest(outsideRows);
            String readyText = "{\n"
                + "  \"schemaVersion\": " + json(SCHEMA) + ",\n"
                + "  \"program\": {\"name\": " + json(PROGRAM_NAME)
                + ", \"md5\": " + json(PROGRAM_MD5)
                + ", \"sha256\": " + json(PROGRAM_SHA256)
                + ", \"imageBase\": \"0x" + IMAGE_BASE + "\", \"language\": "
                + json(LANGUAGE) + ", \"compilerSpec\": " + json(COMPILER_SPEC) + "},\n"
                + "  \"tool\": {\"path\": " + json(getSourceFile().getCanonicalPath())
                + ", \"bytes\": " + toolBytes.length + ", \"sha256\": " + json(sha256(toolBytes)) + "},\n"
                + "  \"manifest\": {\"path\": " + json(manifest.getCanonicalPath())
                + ", \"bytes\": " + manifestBytes.length + ", \"sha256\": "
                + json(actualManifestSha256) + ", \"expectedCount\": " + expectedCount + "},\n"
                + "  \"output\": {\"path\": " + json(output.getCanonicalPath())
                + ", \"bytes\": " + outputBytes.length + ", \"sha256\": "
                + json(sha256(outputBytes)) + "},\n"
                + "  \"counts\": {\"targets\": " + entries.size()
                + ", \"targetSymbols\": " + (entries.size() - zeroSymbols)
                + ", \"zeroSymbols\": " + zeroSymbols
                + ", \"dynamicDefaultLabels\": " + dynamicDefaultLabels
                + ", \"nonDynamicDefaultFunctions\": " + nonDynamicDefaultFunctions
                + ", \"outsideTargetSymbols\": " + outsideRows.size() + "},\n"
                + "  \"outsideTargetSymbolsSha256\": " + json(outsideDigest) + "\n"
                + "}\n";
            Files.writeString(readyPartial.toPath(), readyText, StandardCharsets.UTF_8,
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
            force(readyPartial);
            publish(readyPartial, ready);
            println("TARGET_SYMBOL_TOOL_OK path=" + getSourceFile().getCanonicalPath()
                + " bytes=" + toolBytes.length + " sha256=" + sha256(toolBytes));
            println("TARGET_SYMBOL_INVENTORY_OK targets=" + entries.size()
                + " targetSymbols=" + (entries.size() - zeroSymbols)
                + " outsideTargetSymbols=" + outsideRows.size()
                + " outsideTargetSymbolsSha256=" + outsideDigest);
        } finally {
            Files.deleteIfExists(outputPartial.toPath());
            Files.deleteIfExists(readyPartial.toPath());
        }
    }
}
