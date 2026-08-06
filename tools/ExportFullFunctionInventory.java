//@category Symbol
//
// Full function inventory for before/after analysis-pass diffing.
//
// Enumerates EVERY function in the program and emits one row per function with
// enough state to detect the four failure modes an aggressive analyser can
// cause: functions created, functions destroyed, function BOUNDS moved, and
// names/signatures overwritten.  The last two are the dangerous class - a
// graded name whose symbol SourceType is USER_DEFINED must survive an analysis
// pass untouched, and a name that survives on a function whose BODY changed is
// arguably worse than one that was deleted, because it silently re-points a
// reviewed label at different bytes.
//
// Usage: -postScript ExportFullFunctionInventory.java <out_functions_tsv> <out_program_tsv>

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.OffsetReference;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ShiftedReference;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolType;

import java.io.BufferedWriter;
import java.io.File;
import java.io.InputStream;
import java.nio.channels.FileChannel;
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
import java.util.UUID;

public class ExportFullFunctionInventory extends GhidraScript {

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n").replace("\t", " ");
    }

    private static String hex(byte[] raw) {
        StringBuilder sb = new StringBuilder();
        for (byte b : raw) {
            sb.append(String.format(Locale.ROOT, "%02x", b & 0xff));
        }
        return sb.toString();
    }

    private static String sha256(byte[] raw) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(raw));
    }

    private static void digestString(MessageDigest digest, String value) {
        byte[] raw = (value == null ? "" : value).getBytes(StandardCharsets.UTF_8);
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
        return new File(
            output.getParentFile(), "." + output.getName() + ".partial-" + UUID.randomUUID());
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

    // A stable digest of the exact address ranges owned by the function body.
    // Two functions with the same entry point but different bodies differ here.
    private String bodyDigest(AddressSetView body) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        for (ghidra.program.model.address.AddressRange range : body) {
            md.update(range.getMinAddress().toString().getBytes("UTF-8"));
            md.update((byte) ':');
            md.update(range.getMaxAddress().toString().getBytes("UTF-8"));
            md.update((byte) ';');
        }
        return hex(md.digest());
    }

    private String memoryDigest() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Memory memory = currentProgram.getMemory();
        List<MemoryBlock> blocks = new ArrayList<>(Arrays.asList(memory.getBlocks()));
        blocks.sort(
            Comparator.comparing(MemoryBlock::getStart)
                .thenComparing(MemoryBlock::getEnd)
                .thenComparing(MemoryBlock::getName));
        for (MemoryBlock block : blocks) {
            String blockName = block.getName();
            String sourceName = block.getSourceName();
            String blockComment = block.getComment();
            digestString(
                digest,
                blockName.length() + ":" + sha256(blockName.getBytes(StandardCharsets.UTF_8))
                    + "\t" + (sourceName == null ? -1 : sourceName.length()) + ":"
                    + sha256((sourceName == null ? "" : sourceName)
                        .getBytes(StandardCharsets.UTF_8))
                    + "\t" + (blockComment == null ? -1 : blockComment.length()) + ":"
                    + sha256((blockComment == null ? "" : blockComment)
                        .getBytes(StandardCharsets.UTF_8))
                    + "\t" + block.getStart() + "\t" + block.getEnd()
                    + "\t" + block.getSize() + "\t" + block.isInitialized()
                    + "\t" + block.isRead() + "\t" + block.isWrite()
                    + "\t" + block.isExecute() + "\t" + block.isVolatile()
                    + "\t" + block.isArtificial() + "\t" + block.isMapped()
                    + "\t" + block.isOverlay() + "\t" + block.isLoaded()
                    + "\t" + block.getType());
            if (!block.isInitialized()) {
                continue;
            }
            Address cursor = block.getStart();
            long remaining = block.getSize();
            while (remaining > 0) {
                monitor.checkCancelled();
                int size = (int) Math.min(1024 * 1024L, remaining);
                byte[] chunk = new byte[size];
                int read = memory.getBytes(cursor, chunk);
                if (read != size) {
                    throw new IllegalStateException(
                        "short initialized-memory read at " + cursor
                        + " expected=" + size + " actual=" + read);
                }
                digest.update(chunk);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 2) {
            throw new IllegalArgumentException(
                "usage: <out_functions_tsv> <out_program_tsv>");
        }

        File functionsOutput = requireNewOutput(args[0], "functions TSV");
        File programOutput = requireNewOutput(args[1], "program TSV");
        if (functionsOutput.equals(programOutput)) {
            throw new IllegalArgumentException("functions and program outputs must be distinct");
        }
        File functionsPartial = partialFor(functionsOutput);
        File programPartial = partialFor(programOutput);
        String toolPath = getSourceFile().getCanonicalPath();
        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        println(
            "INVENTORY_TOOL_OK path=" + toolPath
            + " bytes=" + toolBytes.length
            + " sha256=" + sha256(toolBytes));

        try {
            Listing listing = currentProgram.getListing();
            int total = 0;

        try (BufferedWriter bw = Files.newBufferedWriter(
                functionsPartial.toPath(), StandardCharsets.UTF_8,
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            bw.write("address\tname\tnameLen\tnameSha256\tfqname\tfqnameLen\tfqnameSha256"
                + "\tnameSource\tsigSource\tbodyBytes\tbodyMin\tbodyMax"
                + "\tbodyRanges\tbodyDigest\tinstrCount\tparamCount\tcallingConv\treturnType\tvarArgs"
                + "\tisThunk\tthunkTarget\tisExternal\tcustomStorage\tinline\tnoReturn\tframeSize"
                + "\tlocalSize\tparamSize\tsignature\tsignatureLen\tsignatureSha256"
                + "\tcommentPresent\tcommentLen"
                + "\tcommentSha256\trepeatableCommentPresent\trepeatableCommentLen"
                + "\trepeatableCommentSha256\ttagCount\ttagsSha256\ttags\n");

            FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
            while (it.hasNext()) {
                monitor.checkCancelled();
                Function fn = it.next();
                total++;

                AddressSetView body = fn.getBody();
                int instrCount = 0;
                InstructionIterator ii = listing.getInstructions(body, true);
                while (ii.hasNext()) {
                    ii.next();
                    instrCount++;
                }

                Symbol sym = fn.getSymbol();
                String nameSource = sym == null ? "NO_SYMBOL" : sym.getSource().toString();
                Function thunked = fn.isThunk() ? fn.getThunkedFunction(false) : null;
                String comment = fn.getComment();
                String repeatableComment = fn.getRepeatableComment();
                String name = fn.getName();
                String fqname = fn.getName(true);
                String signature = fn.getSignature().getPrototypeString(true);

                List<String> tagNames = new ArrayList<>();
                for (ghidra.program.model.listing.FunctionTag tag : fn.getTags()) {
                    tagNames.add(tag.getName());
                }
                Collections.sort(tagNames);
                String tags = clean(String.join(",", tagNames));
                String tagsDigest = sortedDigest(new ArrayList<>(tagNames));

                bw.write("0x" + fn.getEntryPoint().toString()
                    + "\t" + clean(name)
                    + "\t" + name.length()
                    + "\t" + sha256(name.getBytes(StandardCharsets.UTF_8))
                    + "\t" + clean(fqname)
                    + "\t" + fqname.length()
                    + "\t" + sha256(fqname.getBytes(StandardCharsets.UTF_8))
                    + "\t" + nameSource
                    + "\t" + fn.getSignatureSource().toString()
                    + "\t" + body.getNumAddresses()
                    + "\t0x" + (body.getMinAddress() == null ? "" : body.getMinAddress().toString())
                    + "\t0x" + (body.getMaxAddress() == null ? "" : body.getMaxAddress().toString())
                    + "\t" + body.getNumAddressRanges()
                    + "\t" + bodyDigest(body)
                    + "\t" + instrCount
                    + "\t" + fn.getParameterCount()
                    + "\t" + clean(fn.getCallingConventionName())
                    + "\t" + clean(fn.getReturn().getDataType().getDisplayName())
                    + "\t" + fn.hasVarArgs()
                    + "\t" + fn.isThunk()
                    + "\t" + (thunked == null ? "" : "0x" + thunked.getEntryPoint().toString())
                    + "\t" + fn.isExternal()
                    + "\t" + fn.hasCustomVariableStorage()
                    + "\t" + fn.isInline()
                    + "\t" + fn.hasNoReturn()
                    + "\t" + fn.getStackFrame().getFrameSize()
                    + "\t" + fn.getStackFrame().getLocalSize()
                    + "\t" + fn.getStackFrame().getParameterSize()
                    + "\t" + clean(signature)
                    + "\t" + signature.length()
                    + "\t" + sha256(signature.getBytes(StandardCharsets.UTF_8))
                    + "\t" + (comment != null)
                    + "\t" + (comment == null ? 0 : comment.length())
                    + "\t" + sha256(
                        (comment == null ? "" : comment).getBytes(StandardCharsets.UTF_8))
                    + "\t" + (repeatableComment != null)
                    + "\t" + (repeatableComment == null ? 0 : repeatableComment.length())
                    + "\t" + sha256(
                        (repeatableComment == null ? "" : repeatableComment)
                            .getBytes(StandardCharsets.UTF_8))
                    + "\t" + tagNames.size()
                    + "\t" + tagsDigest
                    + "\t" + tags
                    + "\n");
            }
        }
        force(functionsPartial);

        // Program-level counters.  These catch effects that never surface as a
        // function row: bytes newly disassembled, data newly defined, symbols
        // created outside function scope.
        long instrTotal = 0;
        MessageDigest instructionDigest = MessageDigest.getInstance("SHA-256");
        InstructionIterator all = listing.getInstructions(true);
        while (all.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = all.next();
            instrTotal++;
            digestString(instructionDigest, instruction.getAddress().toString());
            digestString(instructionDigest, Integer.toString(instruction.getLength()));
            instructionDigest.update(instruction.getBytes());
            digestString(instructionDigest, instruction.getMnemonicString());
            digestString(instructionDigest, instruction.getFlowType().toString());
            digestString(instructionDigest, String.valueOf(instruction.getFallThrough()));
            digestString(instructionDigest, Arrays.toString(instruction.getFlows()));
            digestString(instructionDigest, instruction.getFlowOverride().toString());
            digestString(instructionDigest, Boolean.toString(instruction.isLengthOverridden()));
        }
        long dataDefined = 0;
        MessageDigest definedDataDigest = MessageDigest.getInstance("SHA-256");
        DataIterator dit = listing.getDefinedData(true);
        while (dit.hasNext()) {
            monitor.checkCancelled();
            Data data = dit.next();
            dataDefined++;
            digestString(definedDataDigest, data.getAddress().toString());
            digestString(definedDataDigest, Integer.toString(data.getLength()));
            String dataTypePath = data.getDataType().getPathName();
            digestString(
                definedDataDigest,
                dataTypePath.length() + ":"
                    + sha256(dataTypePath.getBytes(StandardCharsets.UTF_8)));
            String valueRepresentation = data.getDefaultValueRepresentation();
            digestString(
                definedDataDigest,
                (valueRepresentation == null ? -1 : valueRepresentation.length()) + ":"
                    + sha256((valueRepresentation == null ? "" : valueRepresentation)
                        .getBytes(StandardCharsets.UTF_8)));
            digestString(definedDataDigest, Boolean.toString(data.isConstant()));
            digestString(definedDataDigest, Boolean.toString(data.isWritable()));
            digestString(definedDataDigest, Boolean.toString(data.isVolatile()));
        }
        long undefinedData = 0;
        DataIterator udit = listing.getData(true);
        while (udit.hasNext()) {
            monitor.checkCancelled();
            Data d = udit.next();
            if (!d.isDefined()) {
                undefinedData++;
            }
        }

        long userSymbols = 0;
        long analysisSymbols = 0;
        long importedSymbols = 0;
        long defaultSymbols = 0;
        List<String> nonFunctionSymbols = new ArrayList<>();
        for (Symbol s : currentProgram.getSymbolTable().getAllSymbols(true)) {
            SourceType st = s.getSource();
            if (st == SourceType.USER_DEFINED) {
                userSymbols++;
            } else if (st == SourceType.ANALYSIS) {
                analysisSymbols++;
            } else if (st == SourceType.IMPORTED) {
                importedSymbols++;
            } else {
                defaultSymbols++;
            }
            // Dynamic labels are derived presentation (for example LAB_* at a
            // newly recognized function entry), not stored non-function state.
            if (s.getSymbolType() != SymbolType.FUNCTION && !s.isDynamic()) {
                String symbolName = s.getName(true);
                nonFunctionSymbols.add(
                    s.getAddress() + "\t" + symbolName.length() + ":"
                        + sha256(symbolName.getBytes(StandardCharsets.UTF_8)) + "\t"
                        + s.getSymbolType() + "\t" + s.getSource() + "\t"
                        + s.isPrimary() + "\t" + s.isDynamic() + "\t"
                        + s.isExternal() + "\t" + s.isPinned());
            }
        }

        List<String> references = new ArrayList<>();
        ReferenceIterator referenceIterator = currentProgram.getReferenceManager()
            .getReferenceIterator(currentProgram.getMinAddress());
        while (referenceIterator.hasNext()) {
            monitor.checkCancelled();
            Reference reference = referenceIterator.next();
            String offsetBase = "";
            String offset = "";
            if (reference instanceof OffsetReference) {
                OffsetReference offsetReference = (OffsetReference) reference;
                offsetBase = String.valueOf(offsetReference.getBaseAddress());
                offset = Long.toString(offsetReference.getOffset());
            }
            String shift = "";
            String shiftedValue = "";
            if (reference instanceof ShiftedReference) {
                ShiftedReference shiftedReference = (ShiftedReference) reference;
                shift = Integer.toString(shiftedReference.getShift());
                shiftedValue = Long.toString(shiftedReference.getValue());
            }
            references.add(
                reference.getFromAddress() + "\t" + reference.getToAddress() + "\t"
                    + reference.getOperandIndex() + "\t" + reference.getReferenceType()
                    + "\t" + reference.getSource() + "\t" + reference.isPrimary()
                    + "\t" + reference.getSymbolID()
                    + "\t" + reference.isMnemonicReference()
                    + "\t" + reference.isOperandReference()
                    + "\t" + reference.isStackReference()
                    + "\t" + reference.isExternalReference()
                    + "\t" + reference.isEntryPointReference()
                    + "\t" + reference.isMemoryReference()
                    + "\t" + reference.isRegisterReference()
                    + "\t" + reference.isOffsetReference()
                    + "\t" + reference.isShiftedReference()
                    + "\t" + offsetBase + "\t" + offset
                    + "\t" + shift + "\t" + shiftedValue
            );
        }

        List<String> comments = new ArrayList<>();
        for (CommentType type : CommentType.values()) {
            AddressIterator addresses = listing.getCommentAddressIterator(
                type, currentProgram.getMemory(), true);
            while (addresses.hasNext()) {
                monitor.checkCancelled();
                Address address = addresses.next();
                String comment = listing.getComment(type, address);
                comments.add(
                    address + "\t" + type + "\t"
                        + (comment == null ? -1 : comment.length()) + ":"
                        + sha256((comment == null ? "" : comment)
                            .getBytes(StandardCharsets.UTF_8)));
            }
        }

        try (BufferedWriter bw = Files.newBufferedWriter(
                programPartial.toPath(), StandardCharsets.UTF_8,
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            bw.write("metric\tvalue\n");
            bw.write("programName\t" + clean(currentProgram.getName()) + "\n");
            bw.write("executableMD5\t"
                + clean(currentProgram.getExecutableMD5()).toLowerCase(Locale.ROOT) + "\n");
            bw.write("executableSHA256\t"
                + clean(currentProgram.getExecutableSHA256()).toLowerCase(Locale.ROOT) + "\n");
            bw.write("imageBase\t0x" + currentProgram.getImageBase() + "\n");
            bw.write("language\t" + currentProgram.getLanguageID() + "\n");
            bw.write("compilerSpec\t"
                + currentProgram.getCompilerSpec().getCompilerSpecID() + "\n");
            bw.write("memorySha256\t" + memoryDigest() + "\n");
            bw.write("functions\t" + total + "\n");
            bw.write("instructions\t" + instrTotal + "\n");
            bw.write("instructionLayoutSha256\t" + hex(instructionDigest.digest()) + "\n");
            bw.write("definedData\t" + dataDefined + "\n");
            bw.write("definedDataSha256\t" + hex(definedDataDigest.digest()) + "\n");
            bw.write("undefinedData\t" + undefinedData + "\n");
            bw.write("symbolsUserDefined\t" + userSymbols + "\n");
            bw.write("symbolsAnalysis\t" + analysisSymbols + "\n");
            bw.write("symbolsImported\t" + importedSymbols + "\n");
            bw.write("symbolsDefaultOther\t" + defaultSymbols + "\n");
            bw.write("nonFunctionSymbolsSha256\t" + sortedDigest(nonFunctionSymbols) + "\n");
            bw.write("references\t" + references.size() + "\n");
            bw.write("referencesSha256\t" + sortedDigest(references) + "\n");
            bw.write("comments\t" + comments.size() + "\n");
            bw.write("commentsSha256\t" + sortedDigest(comments) + "\n");
            bw.write("relocations\t" + currentProgram.getRelocationTable().getSize() + "\n");
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                bw.write("block:" + block.getName() + "\t0x" + block.getStart() + "-0x"
                    + block.getEnd() + " size=" + block.getSize() + " x=" + block.isExecute() + "\n");
            }
        }
        force(programPartial);
        publish(functionsPartial, functionsOutput);
        publish(programPartial, programOutput);

        println("INVENTORY_OK functions=" + total + " instructions=" + instrTotal
            + " definedData=" + dataDefined + " undefinedData=" + undefinedData
            + " userSymbols=" + userSymbols);
        } finally {
            Files.deleteIfExists(functionsPartial.toPath());
            Files.deleteIfExists(programPartial.toPath());
        }
    }
}
