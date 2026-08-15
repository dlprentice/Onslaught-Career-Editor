//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolTable;

import java.io.BufferedWriter;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/**
 * Read-only current-database census for the four HUD route descriptive-name
 * demotion targets (2026-08-14).
 *
 * Targets (route indices from local-lab/pc-hud-static-join-20260812-v1):
 *   0x00483530 CHud__RenderControllerSlotStatusPanel        (T0, refuted)
 *   0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle (T3, half refuted)
 *   0x00485d50 CHud__RenderObjectiveStatusPanel             (T4, suspect)
 *   0x00486940 CHud__RenderObjectiveSlotFillPanel           (T5, refuted)
 *
 * Usage:
 *   -postScript GhidraInspectHudRouteDemotion.java <output-directory>
 */
public class GhidraInspectHudRouteDemotion extends GhidraScript {
    private static final String[] ENTRIES = {
        "0x00483530", "0x004858d0", "0x00485d50", "0x00486940",
    };
    private static final String[] PRE_NAMES = {
        "CHud__RenderControllerSlotStatusPanel",
        "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
        "CHud__RenderObjectiveStatusPanel",
        "CHud__RenderObjectiveSlotFillPanel",
    };
    private static final String[] POST_NAMES = {
        "CHud__RoutePanel_T0_00483530",
        "CHud__RoutePanel_T3_004858d0",
        "CHud__RoutePanel_T4_00485d50",
        "CHud__RoutePanel_T5_00486940",
    };
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final long FUNCTION_COUNT = 8329;
    private static final long INSTRUCTION_COUNT = 551143;

    private static void require(boolean value, String message) {
        if (!value) {
            throw new IllegalStateException(message);
        }
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static String clean(String value) {
        return nullable(value).replace("\\", "\\\\").replace("\r", "\\r")
            .replace("\n", "\\n").replace("\t", "\\t");
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte value : bytes) {
            result.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return result.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String sha256(String value) throws Exception {
        return sha256(value.getBytes(StandardCharsets.UTF_8));
    }

    private long functionCount() {
        long count = 0;
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            functions.next();
            count++;
        }
        return count;
    }

    private long instructionCount() {
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            instructions.next();
            count++;
        }
        return count;
    }

    private String canonicalRanges(AddressSetView body) {
        List<String> rows = new ArrayList<>();
        for (AddressRange range : body) {
            rows.add("0x" + range.getMinAddress() + "-0x" + range.getMaxAddress());
        }
        return String.join(";", rows);
    }

    private String bodyRangeDigest(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (AddressRange range : body) {
            digest.update(range.getMinAddress().toString().getBytes(StandardCharsets.UTF_8));
            digest.update((byte) ':');
            digest.update(range.getMaxAddress().toString().getBytes(StandardCharsets.UTF_8));
            digest.update((byte) ';');
        }
        return hex(digest.digest());
    }

    private String bodyBytesDigest(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (AddressRange range : body) {
            Address cursor = range.getMinAddress();
            long remaining = range.getLength();
            while (remaining > 0) {
                int size = (int) Math.min(1024 * 1024L, remaining);
                byte[] bytes = new byte[size];
                int read = currentProgram.getMemory().getBytes(cursor, bytes);
                require(read == size, "short body read at " + cursor);
                digest.update(bytes);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    private long exactInstructions(AddressSetView body) {
        AddressSet covered = new AddressSet();
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            require(body.contains(instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses target body at " + instruction.getAddress());
            covered.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
            count++;
        }
        require(covered.hasSameAddresses(body), "instruction coverage differs from body");
        return count;
    }

    private static File newOutput(File directory, String name) throws Exception {
        File output = new File(directory, name).getCanonicalFile();
        require(output.getParentFile().equals(directory), "output escaped directory: " + output);
        require(!output.exists(), "output already exists: " + output);
        return output;
    }

    private static BufferedWriter writer(File file) throws Exception {
        return Files.newBufferedWriter(file.toPath(), StandardCharsets.UTF_8,
            StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
    }

    private static List<String> tags(Function function) {
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : function.getTags()) {
            result.add(tag.getName());
        }
        Collections.sort(result);
        return result;
    }

    private void requirePreName(int index, Function function) {
        require(PRE_NAMES[index].equals(function.getName()),
            ENTRIES[index] + " PRE name differs: " + function.getName());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 1, "usage: <output-directory>");
        File directory = new File(args[0]).getCanonicalFile();
        require(directory.isDirectory(), "output directory is absent: " + directory);

        require(PROGRAM_NAME.equals(currentProgram.getName()), "program name differs");
        require(PROGRAM_MD5.equalsIgnoreCase(currentProgram.getExecutableMD5()), "MD5 differs");
        require(PROGRAM_SHA256.equalsIgnoreCase(currentProgram.getExecutableSHA256()),
            "SHA-256 differs");
        require(functionCount() == FUNCTION_COUNT, "function count differs");
        require(instructionCount() == INSTRUCTION_COUNT, "instruction count differs");

        File targetFile = newOutput(directory, "target.tsv");
        try (BufferedWriter out = writer(targetFile)) {
            out.write("address\tname\tfqname\tnamespace\tnameSource\tsignatureSource" +
                "\tsignature\tcallingConvention\treturnType\treturnStorage\tparameterCount" +
                "\tstackParameterBytes\tcustomStorage\tvarArgs\tinline\tnoReturn\tisThunk" +
                "\tthunkTarget\tbodyRanges\tbodyBytes\tbodyRangeSha256\tbodyBytesSha256" +
                "\tinstructionCount\tcommentBytes\tcommentSha256\trepeatableCommentBytes" +
                "\trepeatableCommentSha256\ttags\ttagsSha256\n");
            for (int index = 0; index < ENTRIES.length; index++) {
                Address entry = toAddr(ENTRIES[index]);
                Function function = getFunctionAt(entry);
                require(function != null && function.getEntryPoint().equals(entry),
                    "target function is absent: " + ENTRIES[index]);
                requirePreName(index, function);
                AddressSetView body = function.getBody();
                String comment = nullable(function.getComment());
                String repeatable = nullable(function.getRepeatableComment());
                String tagText = String.join(",", tags(function));
                Function thunk = function.getThunkedFunction(false);
                out.write(ENTRIES[index] + "\t" + clean(function.getName()) + "\t" +
                    clean(function.getName(true)) + "\t" +
                    clean(function.getParentNamespace().getName(true)) + "\t" +
                    function.getSymbol().getSource() + "\t" + function.getSignatureSource() + "\t" +
                    clean(function.getSignature().getPrototypeString(true)) + "\t" +
                    function.getCallingConventionName() + "\t" +
                    clean(function.getReturn().getDataType().getDisplayName()) + "\t" +
                    clean(function.getReturn().getVariableStorage().toString()) + "\t" +
                    function.getParameters().length + "\t" +
                    function.getStackFrame().getParameterSize() + "\t" +
                    function.hasCustomVariableStorage() + "\t" + function.hasVarArgs() + "\t" +
                    function.isInline() + "\t" + function.hasNoReturn() + "\t" +
                    function.isThunk() + "\t" +
                    (thunk == null ? "" : "0x" + thunk.getEntryPoint()) + "\t" +
                    canonicalRanges(body) + "\t" + body.getNumAddresses() + "\t" +
                    bodyRangeDigest(body) + "\t" + bodyBytesDigest(body) + "\t" +
                    exactInstructions(body) + "\t" +
                    comment.getBytes(StandardCharsets.UTF_8).length + "\t" + sha256(comment) +
                    "\t" + repeatable.getBytes(StandardCharsets.UTF_8).length + "\t" +
                    sha256(repeatable) + "\t" + clean(tagText) + "\t" + sha256(tagText) + "\n");
            }
        }

        for (int index = 0; index < ENTRIES.length; index++) {
            Address entry = toAddr(ENTRIES[index]);
            Function function = getFunctionAt(entry);
            require(function != null, "target vanished: " + ENTRIES[index]);
            File commentFile = newOutput(directory,
                "pre-comment-" + ENTRIES[index].substring(2) + ".txt");
            Files.writeString(commentFile.toPath(), nullable(function.getComment()),
                StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
        }

        SymbolTable symbolTable = currentProgram.getSymbolTable();
        File namesFile = newOutput(directory, "name-census.tsv");
        try (BufferedWriter out = writer(namesFile)) {
            out.write("query\taddress\tname\ttype\tsource\n");
            List<String> queries = new ArrayList<>();
            queries.addAll(Arrays.asList(PRE_NAMES));
            queries.addAll(Arrays.asList(POST_NAMES));
            for (String query : queries) {
                SymbolIterator symbols = symbolTable.getSymbols(query);
                while (symbols.hasNext()) {
                    ghidra.program.model.symbol.Symbol symbol = symbols.next();
                    out.write(query + "\t0x" + symbol.getAddress() + "\t" +
                        clean(symbol.getName()) + "\t" + symbol.getSymbolType() + "\t" +
                        symbol.getSource() + "\n");
                }
            }
        }

        File summaryFile = newOutput(directory, "summary.tsv");
        try (BufferedWriter out = writer(summaryFile)) {
            out.write("metric\tvalue\n");
            out.write("functions\t" + FUNCTION_COUNT + "\n");
            out.write("instructions\t" + INSTRUCTION_COUNT + "\n");
            out.write("targets\t" + ENTRIES.length + "\n");
        }

        println("HUD_ROUTE_DEMOTION_INSPECTION_OK targets=4 functions=" + FUNCTION_COUNT +
            " instructions=" + INSTRUCTION_COUNT);
    }
}
