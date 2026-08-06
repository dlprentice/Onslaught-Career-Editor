//@category Battle Engine Aquila

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.database.mem.AddressSourceInfo;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.util.DefinedStringIterator;

/**
 * Export every string data item defined in a Ghidra program without mutating it.
 *
 * Arguments:
 *   0: output TSV
 *   1: output READY JSON
 *   2: expected executable SHA-256
 */
public class ExportDefinedStrings extends GhidraScript {

    private static final String SCHEMA = "bea.re.ghidra-defined-strings.v1";

    private static String sha256(byte[] bytes) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder result = new StringBuilder(digest.length * 2);
        for (byte value : digest) {
            result.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return result.toString();
    }

    private static String jsonString(String value) {
        StringBuilder result = new StringBuilder(value.length() + 16);
        result.append('"');
        for (int index = 0; index < value.length(); index++) {
            char ch = value.charAt(index);
            switch (ch) {
                case '"': result.append("\\\""); break;
                case '\\': result.append("\\\\"); break;
                case '\b': result.append("\\b"); break;
                case '\f': result.append("\\f"); break;
                case '\n': result.append("\\n"); break;
                case '\r': result.append("\\r"); break;
                case '\t': result.append("\\t"); break;
                default:
                    if (ch < 0x20 || ch == 0x7f || Character.isSurrogate(ch)) {
                        result.append(String.format(Locale.ROOT, "\\u%04x", (int) ch));
                    } else {
                        result.append(ch);
                    }
                    break;
            }
        }
        result.append('"');
        return result.toString();
    }

    private static void writeAtomically(Path destination, byte[] bytes) throws IOException {
        Path parent = destination.toAbsolutePath().getParent();
        Files.createDirectories(parent);
        Path temporary = Files.createTempFile(parent, destination.getFileName().toString(), ".partial");
        try {
            Files.write(temporary, bytes);
            try {
                Files.move(temporary, destination, StandardCopyOption.ATOMIC_MOVE,
                    StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException exception) {
                Files.move(temporary, destination, StandardCopyOption.REPLACE_EXISTING);
            }
        } finally {
            Files.deleteIfExists(temporary);
        }
    }

    @Override
    public void run() throws Exception {
        String[] arguments = getScriptArgs();
        if (arguments.length != 3) {
            throw new IllegalArgumentException(
                "usage: ExportDefinedStrings.java <output.tsv> <ready.json> <expected-exe-sha256>");
        }

        String actualExecutableSha256 = currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT);
        String expectedExecutableSha256 = arguments[2].toLowerCase(Locale.ROOT);
        if (!actualExecutableSha256.equals(expectedExecutableSha256)) {
            throw new IllegalStateException(
                "executable SHA-256 mismatch: expected " + expectedExecutableSha256
                    + ", got " + actualExecutableSha256);
        }

        ByteArrayOutputStream table = new ByteArrayOutputStream();
        table.write((
            "address\tfile_offset\tsection\tdata_type\tchar_count\tbyte_length\t"
                + "value_utf8_sha256\txref_count\tcode_xref_count\tfunction_entries\tvalue_json\n")
            .getBytes(StandardCharsets.UTF_8));

        long rowCount = 0;
        long utf8Bytes = 0;
        long xrefCount = 0;
        Set<String> distinctValues = new TreeSet<>();

        for (Data data : DefinedStringIterator.forProgram(currentProgram, null)) {
            monitor.checkCancelled();
            StringDataInstance instance = StringDataInstance.getStringDataInstance(data);
            String value = instance.getStringValue();
            if (value == null) {
                continue;
            }

            Address address = data.getAddress();
            AddressSourceInfo sourceInfo = currentProgram.getMemory().getAddressSourceInfo(address);
            long fileOffset = sourceInfo == null ? -1 : sourceInfo.getFileOffset();
            MemoryBlock block = currentProgram.getMemory().getBlock(address);
            String section = block == null ? "" : block.getName();
            String dataType = data.getDataType().getPathName();
            byte[] valueBytes = value.getBytes(StandardCharsets.UTF_8);

            long rowXrefs = 0;
            long codeXrefs = 0;
            Set<String> functionEntries = new TreeSet<>();
            ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(address);
            while (references.hasNext()) {
                Reference reference = references.next();
                rowXrefs++;
                Address from = reference.getFromAddress();
                if (currentProgram.getListing().getInstructionContaining(from) != null) {
                    codeXrefs++;
                }
                Function function = currentProgram.getFunctionManager().getFunctionContaining(from);
                if (function != null) {
                    functionEntries.add(function.getEntryPoint().toString());
                }
            }

            String row = String.join("\t",
                address.toString(),
                fileOffset < 0 ? "" : String.format(Locale.ROOT, "0x%08x", fileOffset),
                section,
                dataType,
                Integer.toString(value.codePointCount(0, value.length())),
                Integer.toString(data.getLength()),
                sha256(valueBytes),
                Long.toString(rowXrefs),
                Long.toString(codeXrefs),
                String.join(",", functionEntries),
                jsonString(value)) + "\n";
            table.write(row.getBytes(StandardCharsets.UTF_8));

            rowCount++;
            utf8Bytes += valueBytes.length;
            xrefCount += rowXrefs;
            distinctValues.add(value);
        }

        byte[] tableBytes = table.toByteArray();
        String tableSha256 = sha256(tableBytes);
        Path output = Path.of(arguments[0]).toAbsolutePath();
        Path ready = Path.of(arguments[1]).toAbsolutePath();
        writeAtomically(output, tableBytes);

        String readyText = "{\n"
            + "  \"schema\": \"" + SCHEMA + "\",\n"
            + "  \"status\": \"READY\",\n"
            + "  \"program\": " + jsonString(currentProgram.getName()) + ",\n"
            + "  \"executableSha256\": \"" + actualExecutableSha256 + "\",\n"
            + "  \"imageBase\": \"" + currentProgram.getImageBase().toString() + "\",\n"
            + "  \"definedStringRows\": " + rowCount + ",\n"
            + "  \"distinctValues\": " + distinctValues.size() + ",\n"
            + "  \"decodedUtf8Bytes\": " + utf8Bytes + ",\n"
            + "  \"referencesToStringStarts\": " + xrefCount + ",\n"
            + "  \"output\": {\n"
            + "    \"path\": " + jsonString(output.toString()) + ",\n"
            + "    \"bytes\": " + tableBytes.length + ",\n"
            + "    \"sha256\": \"" + tableSha256 + "\"\n"
            + "  }\n"
            + "}\n";
        writeAtomically(ready, readyText.getBytes(StandardCharsets.UTF_8));

        println("EXPORT_DEFINED_STRINGS_READY rows=" + rowCount
            + " distinct=" + distinctValues.size()
            + " sha256=" + tableSha256);
    }
}
