//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
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
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

/**
 * Read-only current-database census for the one-row 0x0050ff10 repair.
 *
 * Usage:
 *   -postScript GhidraInspectCExplosionFactoryIdentity.java <output-directory>
 */
public class GhidraInspectCExplosionFactoryIdentity extends GhidraScript {
    private static final String ENTRY = "0x0050ff10";
    private static final String PRE_NAME = "CWorldPhysicsManager__CreatePickup";
    private static final String POST_NAME = "CWorldPhysicsManager__CreateExplosion";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final long FUNCTION_COUNT = 8170;
    private static final long INSTRUCTION_COUNT = 549872;

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

    private static String namespace(Symbol symbol) {
        return symbol.getParentNamespace() == null ? "" : symbol.getParentNamespace().getName(true);
    }

    private static String symbolRow(Symbol symbol) {
        return "0x" + symbol.getAddress() + "\t" + clean(symbol.getName()) + "\t" +
            clean(symbol.getName(true)) + "\t" + clean(namespace(symbol)) + "\t" +
            symbol.getSymbolType() + "\t" + symbol.getSource() + "\t" +
            symbol.isPrimary() + "\t" + symbol.isDynamic() + "\t" +
            symbol.isExternal() + "\t" + symbol.isPinned();
    }

    private static String referenceRow(Reference reference, Function fromFunction, boolean fromInBody) {
        return "0x" + reference.getToAddress() + "\t0x" + reference.getFromAddress() + "\t" +
            reference.getOperandIndex() + "\t" + reference.getReferenceType() + "\t" +
            reference.getSource() + "\t" + reference.isPrimary() + "\t" + fromInBody + "\t" +
            (fromFunction == null ? "" : "0x" + fromFunction.getEntryPoint()) + "\t" +
            clean(fromFunction == null ? "" : fromFunction.getName());
    }

    private static List<String> tags(Function function) {
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : function.getTags()) {
            result.add(tag.getName());
        }
        Collections.sort(result);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 1, "usage: <output-directory>");
        File directory = new File(args[0]).getCanonicalFile();
        require(directory.isDirectory(), "output directory is absent: " + directory);

        require(PROGRAM_NAME.equals(currentProgram.getName()), "program name differs");
        require(PROGRAM_MD5.equalsIgnoreCase(currentProgram.getExecutableMD5()), "MD5 differs");
        require(PROGRAM_SHA256.equalsIgnoreCase(currentProgram.getExecutableSHA256()), "SHA-256 differs");
        require(functionCount() == FUNCTION_COUNT, "function count differs");
        require(instructionCount() == INSTRUCTION_COUNT, "instruction count differs");

        Address entry = toAddr(ENTRY);
        Function function = getFunctionAt(entry);
        require(function != null && function.getEntryPoint().equals(entry), "target function is absent");
        AddressSetView body = function.getBody();
        long exactInstructionCount = exactInstructions(body);
        Parameter[] parameters = function.getParameters();
        require(parameters.length == 1, "target parameter count differs");
        require(parameters[0].getSource() == ghidra.program.model.symbol.SourceType.USER_DEFINED,
            "target parameter source differs");

        File targetFile = newOutput(directory, "target.tsv");
        try (BufferedWriter out = writer(targetFile)) {
            out.write("address\tname\tfqname\tnamespace\tnameSource\tsignatureSource\tcallingConvention" +
                "\treturnType\treturnStorage\tparameterCount\tparameterName\tparameterType" +
                "\tparameterStorage\tparameterSource\tstackParameterBytes\tcustomStorage\tvarArgs\tinline\tnoReturn" +
                "\tisThunk\tthunkTarget\tbodyRanges\tbodyBytes\tbodyRangeSha256\tbodyBytesSha256" +
                "\tinstructionCount\tcommentBytes\tcommentSha256\trepeatableCommentBytes" +
                "\trepeatableCommentSha256\ttags\ttagsSha256\n");
            String comment = nullable(function.getComment());
            String repeatable = nullable(function.getRepeatableComment());
            String tagText = String.join(",", tags(function));
            String parameterName = parameters.length == 1 ? parameters[0].getName() : "";
            String parameterType = parameters.length == 1 ? parameters[0].getDataType().getDisplayName() : "";
            String parameterStorage = parameters.length == 1 ? parameters[0].getVariableStorage().toString() : "";
            String parameterSource = parameters.length == 1 ? parameters[0].getSource().toString() : "";
            Function thunk = function.getThunkedFunction(false);
            out.write(ENTRY + "\t" + clean(function.getName()) + "\t" +
                clean(function.getName(true)) + "\t" + clean(function.getParentNamespace().getName(true)) + "\t" +
                function.getSymbol().getSource() + "\t" + function.getSignatureSource() + "\t" +
                function.getCallingConventionName() + "\t" +
                clean(function.getReturn().getDataType().getDisplayName()) + "\t" +
                clean(function.getReturn().getVariableStorage().toString()) + "\t" +
                parameters.length + "\t" + clean(parameterName) + "\t" + clean(parameterType) + "\t" +
                clean(parameterStorage) + "\t" + clean(parameterSource) + "\t" +
                function.getStackFrame().getParameterSize() + "\t" +
                function.hasCustomVariableStorage() + "\t" + function.hasVarArgs() + "\t" +
                function.isInline() + "\t" + function.hasNoReturn() + "\t" + function.isThunk() + "\t" +
                (thunk == null ? "" : "0x" + thunk.getEntryPoint()) + "\t" + canonicalRanges(body) + "\t" +
                body.getNumAddresses() + "\t" + bodyRangeDigest(body) + "\t" + bodyBytesDigest(body) + "\t" +
                exactInstructionCount + "\t" + comment.getBytes(StandardCharsets.UTF_8).length + "\t" +
                sha256(comment) + "\t" + repeatable.getBytes(StandardCharsets.UTF_8).length + "\t" +
                sha256(repeatable) + "\t" + clean(tagText) + "\t" + sha256(tagText) + "\n");
        }

        File commentFile = newOutput(directory, "pre-comment.txt");
        Files.writeString(commentFile.toPath(), nullable(function.getComment()), StandardCharsets.UTF_8,
            StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);

        File instructionsFile = newOutput(directory, "instructions.tsv");
        try (BufferedWriter out = writer(instructionsFile)) {
            out.write("address\tbytes\tmnemonic\toperands\tflowType\tfallThrough\tflows\n");
            InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                List<String> flows = new ArrayList<>();
                for (Address flow : instruction.getFlows()) {
                    flows.add("0x" + flow);
                }
                out.write("0x" + instruction.getAddress() + "\t" + hex(instruction.getBytes()) + "\t" +
                    clean(instruction.getMnemonicString()) + "\t" + clean(instruction.toString()) + "\t" +
                    instruction.getFlowType() + "\t" +
                    (instruction.getFallThrough() == null ? "" : "0x" + instruction.getFallThrough()) + "\t" +
                    String.join(",", flows) + "\n");
            }
        }

        File incomingFile = newOutput(directory, "incoming.tsv");
        int entryIncoming = 0;
        int interiorExternalIncoming = 0;
        try (BufferedWriter out = writer(incomingFile)) {
            out.write("toAddress\tfromAddress\toperandIndex\treferenceType\tsource\tprimary" +
                "\tfromInTargetBody\tfromFunctionAddress\tfromFunction\n");
            AddressIterator addresses = body.getAddresses(true);
            while (addresses.hasNext()) {
                Address to = addresses.next();
                ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(to);
                while (references.hasNext()) {
                    Reference reference = references.next();
                    boolean fromInBody = body.contains(reference.getFromAddress());
                    Function fromFunction = getFunctionContaining(reference.getFromAddress());
                    out.write(referenceRow(reference, fromFunction, fromInBody));
                    out.write("\n");
                    if (to.equals(entry) && !fromInBody) {
                        entryIncoming++;
                    }
                    if (!to.equals(entry) && !fromInBody) {
                        interiorExternalIncoming++;
                    }
                }
            }
        }

        File outgoingFile = newOutput(directory, "outgoing.tsv");
        try (BufferedWriter out = writer(outgoingFile)) {
            out.write("fromAddress\ttoAddress\toperandIndex\treferenceType\tsource\tprimary\n");
            InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
            while (instructions.hasNext()) {
                Instruction instruction = instructions.next();
                for (Reference reference : instruction.getReferencesFrom()) {
                    out.write("0x" + reference.getFromAddress() + "\t0x" + reference.getToAddress() + "\t" +
                        reference.getOperandIndex() + "\t" + reference.getReferenceType() + "\t" +
                        reference.getSource() + "\t" + reference.isPrimary() + "\n");
                }
            }
        }

        File symbolsFile = newOutput(directory, "symbols.tsv");
        SymbolTable symbolTable = currentProgram.getSymbolTable();
        List<Symbol> addressSymbols = new ArrayList<>(Arrays.asList(symbolTable.getSymbols(entry)));
        addressSymbols.sort(Comparator.comparing(GhidraInspectCExplosionFactoryIdentity::symbolRow));
        try (BufferedWriter out = writer(symbolsFile)) {
            out.write("address\tname\tfqname\tnamespace\ttype\tsource\tprimary\tdynamic\texternal\tpinned\n");
            for (Symbol symbol : addressSymbols) {
                out.write(symbolRow(symbol));
                out.write("\n");
            }
        }

        File namesFile = newOutput(directory, "name-census.tsv");
        try (BufferedWriter out = writer(namesFile)) {
            out.write("query\taddress\tname\tfqname\tnamespace\ttype\tsource\tprimary\tdynamic\texternal\tpinned\n");
            for (String query : Arrays.asList(PRE_NAME, POST_NAME)) {
                SymbolIterator symbols = symbolTable.getSymbols(query);
                while (symbols.hasNext()) {
                    out.write(query + "\t" + symbolRow(symbols.next()) + "\n");
                }
            }
        }

        File summaryFile = newOutput(directory, "summary.tsv");
        try (BufferedWriter out = writer(summaryFile)) {
            out.write("metric\tvalue\n");
            out.write("functions\t" + FUNCTION_COUNT + "\n");
            out.write("instructions\t" + INSTRUCTION_COUNT + "\n");
            out.write("entryIncomingReferences\t" + entryIncoming + "\n");
            out.write("externalInteriorReferences\t" + interiorExternalIncoming + "\n");
            out.write("symbolsAtEntry\t" + addressSymbols.size() + "\n");
        }

        println("CEXPLOSION_FACTORY_INSPECTION_OK entry=" + ENTRY + " functions=" + FUNCTION_COUNT +
            " instructions=" + INSTRUCTION_COUNT + " entry_refs=" + entryIncoming +
            " external_interior_refs=" + interiorExternalIncoming);
    }
}
