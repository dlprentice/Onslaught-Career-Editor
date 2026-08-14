//@category Symbol
//
// Scratch-only admission of five proved body fragments to five existing
// functions in the pristine PC retail program.  This script never creates a
// function and never changes names, signatures, comments, tags, data, bytes,
// or stored non-function symbols.  Instruction replacement and the references
// it derives are confined to the five exact repair ranges.
//
// Usage:
//   -postScript GhidraApplyFunctionFragmentRanges.java
//       <package-root> <out.tsv> <out.ready.json>
//       <dry|probe-after-one|probe-after-all|apply|readback>


import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.disassemble.Disassembler;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolType;

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
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;


public class GhidraApplyFunctionFragmentRanges extends GhidraScript {

    private static final String SCHEMA =
        "bea.ghidra.function-fragment-range-repair.v1";
    private static final String POLICY = "LIVE_FORBIDDEN";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String TEXT_BLOCK = ".text";
    private static final long PRE_FUNCTIONS = 8280;
    private static final long PRE_BODY_RANGES = 8400;
    private static final long PRE_OWNED_BYTES = 1794212;
    private static final long PRE_INSTRUCTIONS = 550991;
    private static final long PRE_REFERENCES = 234495;
    private static final long POST_FUNCTIONS = 8280;
    private static final long POST_BODY_RANGES = 8396;
    private static final long POST_OWNED_BYTES = 1795470;
    private static final long POST_INSTRUCTIONS = 551014;
    private static final long POST_REFERENCES = 234478;
    private static final int TARGET_COUNT = 5;
    private static final long REPAIR_BYTES = 1258;
    private static final long REPAIR_INSTRUCTIONS = 325;
    private static final String MANIFEST_RELATIVE =
        "static/final-a/fragment-manifest.tsv";
    private static final long MANIFEST_BYTES = 2878;
    private static final String MANIFEST_SHA256 =
        "c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0";
    private static final String MANIFEST_HEADER =
        "entry\tcurrent_name\tpre_body_ranges\trepair_ranges" +
        "\tpost_body_ranges\trepair_bytes\trepair_sha256" +
        "\trepair_instruction_count\trepair_instruction_layout_sha256" +
        "\tnormalized_sha256\tdemo_entry\tdemo_repair_ranges" +
        "\tdemo_repair_sha256\tdemo_raw_diff_bytes\towner_jump_rows" +
        "\tloose_instruction_rows_pre\truntime_grade\tmutation_scope";

    private static final String[] EXPECTED_ENTRIES = {
        "0x00462640", "0x0046ff10", "0x00482590", "0x004be420", "0x00559410"
    };
    private static final String[] EXPECTED_NAMES = {
        "CFEPMain__Process",
        "CGame__HandleEvent",
        "CHud__RenderTargetIndicatorOverlay",
        "CExplosionInitThing__SelectNextPathStepDirection",
        "CDXTexture__CreateMipmaps"
    };

    private static class Target {
        final String entryText;
        final Address entry;
        final String name;
        final String preRangesText;
        final AddressSet preBody;
        final String repairRangesText;
        final AddressSet repair;
        final String postRangesText;
        final AddressSet postBody;
        final long repairBytes;
        final String repairSha256;
        final long repairInstructions;
        final String layoutSha256;
        final AddressSet seeds;

        Target(String entryText, Address entry, String name,
                String preRangesText, AddressSet preBody,
                String repairRangesText, AddressSet repair,
                String postRangesText, AddressSet postBody,
                long repairBytes, String repairSha256,
                long repairInstructions, String layoutSha256,
                AddressSet seeds) {
            this.entryText = entryText;
            this.entry = entry;
            this.name = name;
            this.preRangesText = preRangesText;
            this.preBody = preBody;
            this.repairRangesText = repairRangesText;
            this.repair = repair;
            this.postRangesText = postRangesText;
            this.postBody = postBody;
            this.repairBytes = repairBytes;
            this.repairSha256 = repairSha256;
            this.repairInstructions = repairInstructions;
            this.layoutSha256 = layoutSha256;
            this.seeds = seeds;
        }
    }

    private static class Counts {
        final long functions;
        final long ranges;
        final long ownedBytes;
        final long instructions;
        final long references;

        Counts(long functions, long ranges, long ownedBytes,
                long instructions, long references) {
            this.functions = functions;
            this.ranges = ranges;
            this.ownedBytes = ownedBytes;
            this.instructions = instructions;
            this.references = references;
        }
    }

    private static class Snapshots {
        final Map<String, String> functionFull;
        final Map<String, String> functionMeta;
        final String instructionsOutside;
        final String referencesOutside;
        final String data;
        final String symbols;
        final String comments;
        final String memory;

        Snapshots(Map<String, String> functionFull,
                Map<String, String> functionMeta,
                String instructionsOutside, String referencesOutside,
                String data, String symbols, String comments, String memory) {
            this.functionFull = functionFull;
            this.functionMeta = functionMeta;
            this.instructionsOutside = instructionsOutside;
            this.referencesOutside = referencesOutside;
            this.data = data;
            this.symbols = symbols;
            this.comments = comments;
            this.memory = memory;
        }
    }

    private static class IntentionalProbeException extends RuntimeException {
        IntentionalProbeException(String message) {
            super(message);
        }
    }

    private static void require(boolean value, String message) {
        if (!value) {
            throw new IllegalStateException(message);
        }
    }

    private static void equal(String label, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(
                label + " mismatch expected=" + expected + " actual=" + actual);
        }
    }

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\r", "\\r")
            .replace("\n", "\\n").replace("\t", " ");
    }

    private static String json(String value) {
        return clean(value).replace("\"", "\\\"");
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

    private static void digestString(MessageDigest digest, String value) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        digest.update(ByteBuffer.allocate(4).putInt(bytes.length).array());
        digest.update(bytes);
    }

    private static String sortedDigest(List<String> rows) throws Exception {
        Collections.sort(rows);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (String row : rows) {
            digestString(digest, row);
        }
        return hex(digest.digest());
    }

    private static String canonical(Address address) {
        return "0x" + address.toString().toLowerCase(Locale.ROOT);
    }

    private Address parseAddress(String value, String label) {
        require(value != null && value.matches("0x[0-9a-fA-F]{8}"),
            label + " must be one 32-bit address: " + value);
        Address address = toAddr(value);
        require(address != null, label + " does not resolve: " + value);
        return address;
    }

    private AddressSet parseRanges(String value, String label) {
        require(value != null && !value.isEmpty(), "empty ranges for " + label);
        AddressSet result = new AddressSet();
        Address priorEnd = null;
        for (String piece : value.split(";", -1)) {
            require(piece.matches("0x[0-9a-fA-F]{8}-0x[0-9a-fA-F]{8}"),
                "malformed range for " + label + ": " + piece);
            String[] parts = piece.split("-", -1);
            Address start = parseAddress(parts[0], label + " start");
            Address end = parseAddress(parts[1], label + " end");
            require(start.compareTo(end) < 0, "empty range for " + label);
            if (priorEnd != null) {
                require(priorEnd.compareTo(start) < 0,
                    "touching or overlapping ranges for " + label);
            }
            result.addRange(start, end.subtract(1));
            priorEnd = end;
        }
        return result;
    }

    private static String canonicalRanges(AddressSetView body) {
        StringBuilder out = new StringBuilder();
        for (AddressRange range : body) {
            if (out.length() > 0) {
                out.append(';');
            }
            out.append(canonical(range.getMinAddress())).append('-')
                .append(canonical(range.getMaxAddress().add(1)));
        }
        return out.toString();
    }

    private static long nonnegativeLong(String value, String label) {
        try {
            long result = Long.parseLong(value);
            require(result >= 0, label + " must be nonnegative");
            return result;
        } catch (NumberFormatException ex) {
            throw new IllegalStateException(label + " is not an integer", ex);
        }
    }

    private static String requireHash(String value, String label) {
        require(value != null && value.matches("[0-9a-f]{64}"),
            label + " must be lowercase SHA-256");
        return value;
    }

    private AddressSet seedsFor(String entry) {
        Map<String, String[]> values = new HashMap<>();
        values.put("0x00462640", new String[] {"0x0046282b"});
        values.put("0x0046ff10", new String[] {"0x004700da"});
        values.put("0x00482590", new String[] {
            "0x00482725", "0x0048272c", "0x00482733", "0x0048273a"
        });
        values.put("0x004be420", new String[] {
            "0x004be82d", "0x004be857", "0x004be862", "0x004be86d",
            "0x004be878", "0x004be883", "0x004be8b1", "0x004be8df",
            "0x004be90e"
        });
        values.put("0x00559410", new String[] {
            "0x0055954c", "0x00559553", "0x0055955a", "0x00559561",
            "0x00559568", "0x0055956f", "0x00559576", "0x0055957d",
            "0x00559584", "0x0055958b", "0x00559592"
        });
        require(values.containsKey(entry), "no seed set for " + entry);
        AddressSet result = new AddressSet();
        for (String value : values.get(entry)) {
            Address address = parseAddress(value, "seed");
            result.add(address);
        }
        return result;
    }

    private List<Target> loadTargets(File manifest) throws Exception {
        byte[] bytes = Files.readAllBytes(manifest.toPath());
        equal("manifest bytes", MANIFEST_BYTES, (long) bytes.length);
        equal("manifest sha256", MANIFEST_SHA256, sha256(bytes));
        String text = new String(bytes, StandardCharsets.UTF_8);
        require(text.indexOf('\r') < 0 && text.endsWith("\n")
                && !text.endsWith("\n\n"),
            "manifest line endings are not canonical");
        String[] lines = text.split("\n", -1);
        equal("manifest header", MANIFEST_HEADER, lines[0]);
        equal("manifest row count", TARGET_COUNT + 2, lines.length);

        List<Target> result = new ArrayList<>();
        AddressSet allRepair = new AddressSet();
        long bytesTotal = 0;
        long instructionsTotal = 0;
        for (int index = 0; index < TARGET_COUNT; index++) {
            String[] fields = lines[index + 1].split("\t", -1);
            equal("manifest field count at row " + (index + 1), 18, fields.length);
            equal("entry order at row " + (index + 1), EXPECTED_ENTRIES[index], fields[0]);
            equal("name at row " + (index + 1), EXPECTED_NAMES[index], fields[1]);
            equal("mutation scope at row " + (index + 1),
                "BODY_RANGE_AND_BOUNDED_DISASSEMBLY_ONLY", fields[17]);
            Address entry = parseAddress(fields[0], "entry");
            AddressSet pre = parseRanges(fields[2], fields[0] + " PRE");
            AddressSet repair = parseRanges(fields[3], fields[0] + " repair");
            AddressSet post = parseRanges(fields[4], fields[0] + " POST");
            AddressSet expectedPost = new AddressSet(pre);
            expectedPost.add(repair);
            require(expectedPost.hasSameAddresses(post),
                "POST is not PRE plus repair at " + fields[0]);
            AddressSet overlap = pre.intersect(repair);
            require(overlap.isEmpty(), "repair overlaps PRE at " + fields[0]);
            AddressSet globalOverlap = allRepair.intersect(repair);
            require(globalOverlap.isEmpty(), "repair ranges overlap at " + fields[0]);
            allRepair.add(repair);
            long repairBytes = nonnegativeLong(fields[5], "repair bytes");
            equal("repair address count at " + fields[0],
                repairBytes, repair.getNumAddresses());
            long repairInstructions = nonnegativeLong(fields[7], "repair instructions");
            AddressSet seeds = seedsFor(fields[0]);
            require(repair.contains(seeds), "seed escaped repair at " + fields[0]);
            result.add(new Target(
                fields[0], entry, fields[1], fields[2], pre,
                fields[3], repair, fields[4], post, repairBytes,
                requireHash(fields[6], "repair sha256"), repairInstructions,
                requireHash(fields[8], "layout sha256"), seeds));
            bytesTotal += repairBytes;
            instructionsTotal += repairInstructions;
        }
        equal("repair byte total", REPAIR_BYTES, bytesTotal);
        equal("repair instruction total", REPAIR_INSTRUCTIONS, instructionsTotal);
        return result;
    }

    private void validateProgramIdentity() throws Exception {
        require(currentProgram != null, "no current program");
        equal("program name", PROGRAM_NAME, currentProgram.getName());
        equal("program md5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        equal("program sha256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        equal("image base", IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        equal("language", LANGUAGE, currentProgram.getLanguageID().toString());
        equal("compiler spec", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        MemoryBlock text = currentProgram.getMemory().getBlock(TEXT_BLOCK);
        require(text != null && text.isExecute(), "executable .text block missing");
    }

    private long functionCount() {
        long result = 0;
        FunctionIterator iterator =
            currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            iterator.next();
            result++;
        }
        return result;
    }

    private long instructionCount() {
        long result = 0;
        InstructionIterator iterator = currentProgram.getListing().getInstructions(true);
        while (iterator.hasNext()) {
            iterator.next();
            result++;
        }
        return result;
    }

    private long referenceCount() {
        long result = 0;
        ReferenceIterator iterator = currentProgram.getReferenceManager()
            .getReferenceIterator(currentProgram.getMinAddress());
        while (iterator.hasNext()) {
            iterator.next();
            result++;
        }
        return result;
    }

    private Counts counts() {
        long functions = 0;
        long ranges = 0;
        long bytes = 0;
        FunctionIterator iterator =
            currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            functions++;
            for (AddressRange ignored : function.getBody()) {
                ranges++;
            }
            bytes += function.getBody().getNumAddresses();
        }
        return new Counts(functions, ranges, bytes,
            instructionCount(), referenceCount());
    }

    private void validateCounts(Counts actual, boolean post, String label) {
        equal(label + " functions", post ? POST_FUNCTIONS : PRE_FUNCTIONS,
            actual.functions);
        equal(label + " body ranges", post ? POST_BODY_RANGES : PRE_BODY_RANGES,
            actual.ranges);
        equal(label + " owned bytes", post ? POST_OWNED_BYTES : PRE_OWNED_BYTES,
            actual.ownedBytes);
        equal(label + " instructions", post ? POST_INSTRUCTIONS : PRE_INSTRUCTIONS,
            actual.instructions);
        long expectedReferences = post ? POST_REFERENCES : PRE_REFERENCES;
        if (expectedReferences >= 0) {
            equal(label + " references", expectedReferences, actual.references);
        }
    }

    private String bodyBytesSha256(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        AddressIterator iterator = body.getAddresses(true);
        while (iterator.hasNext()) {
            digest.update(currentProgram.getMemory().getByte(iterator.next()));
        }
        return hex(digest.digest());
    }

    private AddressSet repairUnion(List<Target> targets) {
        AddressSet result = new AddressSet();
        for (Target target : targets) {
            result.add(target.repair);
        }
        return result;
    }

    private Function exactFunction(Target target) {
        Function function = currentProgram.getFunctionManager()
            .getFunctionAt(target.entry);
        require(function != null, "missing owner function at " + target.entryText);
        equal("owner name at " + target.entryText, target.name, function.getName());
        return function;
    }

    private void validateTargetState(Target target, boolean post) throws Exception {
        Function owner = exactFunction(target);
        AddressSetView expected = post ? target.postBody : target.preBody;
        require(owner.getBody().hasSameAddresses(expected),
            "owner body mismatch at " + target.entryText + " expected=" +
            canonicalRanges(expected) + " actual=" + canonicalRanges(owner.getBody()));
        equal("owner body text at " + target.entryText,
            post ? target.postRangesText : target.preRangesText,
            canonicalRanges(owner.getBody()));
        AddressIterator addresses = target.repair.getAddresses(true);
        while (addresses.hasNext()) {
            Address address = addresses.next();
            Function containing = currentProgram.getFunctionManager()
                .getFunctionContaining(address);
            if (post) {
                require(containing != null && containing.getEntryPoint().equals(target.entry),
                    "POST repair byte not owned by expected function at " + canonical(address));
            } else {
                require(containing == null,
                    "PRE repair byte already belongs to a function at " + canonical(address));
            }
        }
        equal("repair bytes at " + target.entryText,
            target.repairSha256, bodyBytesSha256(target.repair));
        if (post) {
            require(instructionCoverage(target.repair).hasSameAddresses(target.repair),
                "POST repair is not exactly disassembled at " + target.entryText);
            equal("repair instruction count at " + target.entryText,
                target.repairInstructions, instructionsIn(target.repair));
            equal("repair instruction layout at " + target.entryText,
                target.layoutSha256, instructionLayoutSha256(target.repair));
        }
    }

    private long instructionsIn(AddressSetView body) {
        long result = 0;
        InstructionIterator iterator =
            currentProgram.getListing().getInstructions(body, true);
        while (iterator.hasNext()) {
            iterator.next();
            result++;
        }
        return result;
    }

    private AddressSet instructionCoverage(AddressSetView body) {
        AddressSet result = new AddressSet();
        InstructionIterator iterator =
            currentProgram.getListing().getInstructions(body, true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            require(body.contains(instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses repair boundary at " +
                canonical(instruction.getMinAddress()));
            result.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
        }
        return result;
    }

    private String instructionLayoutSha256(AddressSetView body) throws Exception {
        Address start = body.getMinAddress();
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        InstructionIterator iterator =
            currentProgram.getListing().getInstructions(body, true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            String row = String.format(Locale.ROOT, "%08x:%d:%s\n",
                instruction.getAddress().subtract(start), instruction.getLength(),
                hex(instruction.getBytes()));
            digest.update(row.getBytes(StandardCharsets.US_ASCII));
        }
        return hex(digest.digest());
    }

    private String functionMeta(Function function) throws Exception {
        List<String> tags = new ArrayList<>();
        for (ghidra.program.model.listing.FunctionTag tag : function.getTags()) {
            tags.add(tag.getName());
        }
        Collections.sort(tags);
        Symbol symbol = function.getSymbol();
        return clean(function.getName()) + "|" +
            (symbol == null ? "" : symbol.getSource().toString()) + "|" +
            function.getSignatureSource() + "|" +
            clean(function.getSignature().getPrototypeString()) + "|" +
            function.getParameterCount() + "|" + function.getCallingConventionName() + "|" +
            function.hasVarArgs() + "|" + function.isThunk() + "|" +
            function.isExternal() + "|" + function.hasCustomVariableStorage() + "|" +
            function.isInline() + "|" + function.hasNoReturn() + "|" +
            function.getStackFrame().getFrameSize() + "|" +
            function.getStackFrame().getLocalSize() + "|" +
            function.getStackFrame().getParameterSize() + "|" +
            clean(function.getComment()) + "|" + clean(function.getRepeatableComment()) + "|" +
            String.join(",", tags);
    }

    private String functionFull(Function function) throws Exception {
        return functionMeta(function) + "|" + canonicalRanges(function.getBody()) + "|" +
            function.getBody().getNumAddresses() + "|" + instructionsIn(function.getBody());
    }

    private Map<String, String> functionSnapshot(boolean metadataOnly) throws Exception {
        Map<String, String> result = new LinkedHashMap<>();
        FunctionIterator iterator =
            currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            String entry = canonical(function.getEntryPoint());
            String value = metadataOnly ? functionMeta(function) : functionFull(function);
            require(result.put(entry, value) == null,
                "duplicate function entry in snapshot: " + entry);
        }
        return result;
    }

    private String instructionsOutside(AddressSetView repair) throws Exception {
        List<String> rows = new ArrayList<>();
        InstructionIterator iterator = currentProgram.getListing().getInstructions(true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            boolean intersects = repair.intersects(
                instruction.getMinAddress(), instruction.getMaxAddress());
            if (intersects) {
                require(repair.contains(
                        instruction.getMinAddress(), instruction.getMaxAddress()),
                    "instruction crosses authorized repair union at " +
                    canonical(instruction.getMinAddress()));
                continue;
            }
            rows.add(canonical(instruction.getAddress()) + "|" +
                instruction.getLength() + "|" + hex(instruction.getBytes()) + "|" +
                clean(instruction.getMnemonicString()) + "|" +
                instruction.getFlowType() + "|" +
                String.valueOf(instruction.getFallThrough()) + "|" +
                Arrays.toString(instruction.getFlows()) + "|" +
                instruction.getFlowOverride() + "|" + instruction.isLengthOverridden());
        }
        return sortedDigest(rows);
    }

    private String referencesOutside(AddressSetView repair) throws Exception {
        List<String> rows = new ArrayList<>();
        ReferenceIterator iterator = currentProgram.getReferenceManager()
            .getReferenceIterator(currentProgram.getMinAddress());
        while (iterator.hasNext()) {
            Reference reference = iterator.next();
            if (repair.contains(reference.getFromAddress())) {
                continue;
            }
            rows.add(canonical(reference.getFromAddress()) + "|" +
                canonical(reference.getToAddress()) + "|" +
                reference.getOperandIndex() + "|" + reference.getReferenceType() + "|" +
                reference.getSource() + "|" + reference.isPrimary() + "|" +
                reference.getSymbolID() + "|" + reference.isMnemonicReference() + "|" +
                reference.isOperandReference() + "|" + reference.isStackReference() + "|" +
                reference.isExternalReference() + "|" + reference.isEntryPointReference() + "|" +
                reference.isMemoryReference() + "|" + reference.isRegisterReference());
        }
        return sortedDigest(rows);
    }

    private String dataSnapshot() throws Exception {
        List<String> rows = new ArrayList<>();
        DataIterator iterator = currentProgram.getListing().getDefinedData(true);
        while (iterator.hasNext()) {
            Data data = iterator.next();
            rows.add(canonical(data.getAddress()) + "|" + data.getLength() + "|" +
                data.getDataType().getPathName() + "|" +
                clean(data.getDefaultValueRepresentation()) + "|" +
                data.isConstant() + "|" + data.isWritable() + "|" + data.isVolatile());
        }
        return sortedDigest(rows);
    }

    private String symbolSnapshot() throws Exception {
        List<String> rows = new ArrayList<>();
        for (Symbol symbol : currentProgram.getSymbolTable().getAllSymbols(true)) {
            if (symbol.getSymbolType() == SymbolType.FUNCTION || symbol.isDynamic()) {
                continue;
            }
            rows.add(canonical(symbol.getAddress()) + "|" + symbol.getName(true) + "|" +
                symbol.getSymbolType() + "|" + symbol.getSource() + "|" +
                symbol.isPrimary() + "|" + symbol.isExternal() + "|" + symbol.isPinned());
        }
        return sortedDigest(rows);
    }

    private String commentSnapshot() throws Exception {
        List<String> rows = new ArrayList<>();
        Listing listing = currentProgram.getListing();
        for (CommentType type : CommentType.values()) {
            AddressIterator iterator = listing.getCommentAddressIterator(
                type, currentProgram.getMemory(), true);
            while (iterator.hasNext()) {
                Address address = iterator.next();
                rows.add(canonical(address) + "|" + type + "|" +
                    clean(listing.getComment(type, address)));
            }
        }
        return sortedDigest(rows);
    }

    private String memorySnapshot() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
            digestString(digest, block.getName());
            if (!block.isInitialized()) {
                continue;
            }
            Address address = block.getStart();
            byte[] buffer = new byte[1024 * 1024];
            long remaining = block.getSize();
            while (remaining > 0) {
                int length = (int) Math.min(buffer.length, remaining);
                int read = currentProgram.getMemory().getBytes(address, buffer, 0, length);
                equal("memory read at " + canonical(address), length, read);
                digest.update(buffer, 0, length);
                address = address.add(length);
                remaining -= length;
            }
        }
        return hex(digest.digest());
    }

    private Snapshots snapshots(AddressSetView repair) throws Exception {
        return new Snapshots(
            functionSnapshot(false), functionSnapshot(true),
            instructionsOutside(repair), referencesOutside(repair),
            dataSnapshot(), symbolSnapshot(), commentSnapshot(), memorySnapshot());
    }

    private void validatePostSnapshots(Snapshots before, AddressSetView repair,
            List<Target> targets) throws Exception {
        Map<String, String> fullAfter = functionSnapshot(false);
        Map<String, String> metaAfter = functionSnapshot(true);
        equal("function entry set", before.functionFull.keySet(), fullAfter.keySet());
        Set<String> targetEntries = new HashSet<>();
        for (Target target : targets) {
            targetEntries.add(target.entryText);
            equal("target metadata at " + target.entryText,
                before.functionMeta.get(target.entryText), metaAfter.get(target.entryText));
        }
        for (Map.Entry<String, String> row : before.functionFull.entrySet()) {
            if (!targetEntries.contains(row.getKey())) {
                equal("non-target function at " + row.getKey(),
                    row.getValue(), fullAfter.get(row.getKey()));
            }
        }
        equal("instructions outside repair", before.instructionsOutside,
            instructionsOutside(repair));
        equal("references outside repair", before.referencesOutside,
            referencesOutside(repair));
        equal("defined data", before.data, dataSnapshot());
        equal("stored non-function symbols", before.symbols, symbolSnapshot());
        equal("comments", before.comments, commentSnapshot());
        equal("memory", before.memory, memorySnapshot());
    }

    private void clearRepairInstructions(Target target) {
        Listing listing = currentProgram.getListing();
        Set<Address> starts = new LinkedHashSet<>();
        AddressIterator addresses = target.repair.getAddresses(true);
        while (addresses.hasNext()) {
            Address address = addresses.next();
            require(listing.getDefinedDataContaining(address) == null,
                "defined data intersects repair at " + canonical(address));
            Instruction instruction = listing.getInstructionContaining(address);
            if (instruction == null) {
                continue;
            }
            require(target.repair.contains(
                    instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses target repair at " +
                canonical(instruction.getMinAddress()));
            starts.add(instruction.getMinAddress());
        }
        List<Address> descending = new ArrayList<>(starts);
        Collections.reverse(descending);
        for (Address start : descending) {
            Instruction instruction = listing.getInstructionAt(start);
            require(instruction != null, "instruction disappeared before clear");
            listing.clearCodeUnits(
                instruction.getMinAddress(), instruction.getMaxAddress(), false);
        }
        require(instructionCoverage(target.repair).isEmpty(),
            "repair retained instructions after clear at " + target.entryText);
    }

    private void disassembleSeed(Disassembler disassembler, Address seed,
            Target target) throws Exception {
        if (currentProgram.getListing().getInstructionAt(seed) != null) {
            return;
        }
        disassembler.disassemble(new AddressSet(seed, seed), target.repair, true);
        if (currentProgram.getListing().getInstructionAt(seed) != null) {
            return;
        }
        PseudoInstruction pseudo =
            new PseudoDisassembler(currentProgram).disassemble(seed);
        require(pseudo != null && pseudo.getMinAddress().equals(seed),
            "pseudo-disassembly failed at " + canonical(seed));
        require(target.repair.contains(pseudo.getMinAddress(), pseudo.getMaxAddress()),
            "pseudo-disassembly escaped repair at " + canonical(seed));
        Instruction created = currentProgram.getListing().createInstruction(
            seed, pseudo.getPrototype(), pseudo.getMemBuffer(),
            pseudo.getProcessorContext(), pseudo.getLength());
        require(created != null && created.getMinAddress().equals(seed)
                && created.getMaxAddress().equals(pseudo.getMaxAddress()),
            "pseudo instruction creation failed at " + canonical(seed));
    }

    private void ensureDisassembled(Target target) throws Exception {
        Disassembler disassembler = Disassembler.getDisassembler(
            currentProgram, monitor, message -> println(
                "FUNCTION_FRAGMENT_DISASSEMBLER message=" + clean(message)));
        AddressIterator seeds = target.seeds.getAddresses(true);
        while (seeds.hasNext()) {
            disassembleSeed(disassembler, seeds.next(), target);
        }
        AddressSet covered = instructionCoverage(target.repair);
        AddressSet remaining = new AddressSet(target.repair);
        remaining.delete(covered);
        int passes = 0;
        while (!remaining.isEmpty()) {
            monitor.checkCancelled();
            require(++passes <= target.repairBytes,
                "bounded disassembly made no progress at " + target.entryText);
            long before = remaining.getNumAddresses();
            disassembleSeed(disassembler, remaining.getMinAddress(), target);
            covered = instructionCoverage(target.repair);
            remaining = new AddressSet(target.repair);
            remaining.delete(covered);
            require(remaining.getNumAddresses() < before,
                "bounded disassembly stalled at " + target.entryText);
        }
        equal("repair instruction count after disassembly at " + target.entryText,
            target.repairInstructions, instructionsIn(target.repair));
        equal("repair layout after disassembly at " + target.entryText,
            target.layoutSha256, instructionLayoutSha256(target.repair));
    }

    private void applyOne(Target target) throws Exception {
        validateTargetState(target, false);
        clearRepairInstructions(target);
        ensureDisassembled(target);
        Function owner = exactFunction(target);
        owner.setBody(target.postBody);
        validateTargetState(target, true);
    }

    private byte[] buildTsv(List<Target> targets, String mode,
            boolean post, boolean rollbackVerified) throws Exception {
        StringBuilder out = new StringBuilder();
        out.append("entry\tname\tmode\tstatus\tpreBodyRanges\trepairRanges")
            .append("\tpostBodyRanges\trepairBytes\trepairSha256")
            .append("\trepairInstructions\trepairInstructionLayoutSha256")
            .append("\tactualBodyRanges\tactualRepairInstructions")
            .append("\tactualRepairInstructionLayoutSha256\trollbackVerified\n");
        for (Target target : targets) {
            Function function = exactFunction(target);
            long actualInstructions = post ? instructionsIn(target.repair) : 0;
            String actualLayout = post ? instructionLayoutSha256(target.repair) : "";
            out.append(target.entryText).append('\t').append(target.name).append('\t')
                .append(mode).append('\t').append(post ? "POST_VERIFIED" : "PRE_VERIFIED")
                .append('\t').append(target.preRangesText).append('\t')
                .append(target.repairRangesText).append('\t')
                .append(target.postRangesText).append('\t').append(target.repairBytes)
                .append('\t').append(target.repairSha256).append('\t')
                .append(target.repairInstructions).append('\t').append(target.layoutSha256)
                .append('\t').append(canonicalRanges(function.getBody())).append('\t')
                .append(actualInstructions).append('\t').append(actualLayout).append('\t')
                .append(rollbackVerified).append('\n');
        }
        return out.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static File requireNewOutput(File packageRoot, String value,
            String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        require(output.toPath().startsWith(packageRoot.toPath()),
            label + " escapes package root: " + output);
        require(!output.exists(), label + " already exists: " + output);
        require(output.getParentFile() != null && output.getParentFile().isDirectory(),
            label + " parent is not an existing directory");
        return output;
    }

    private static File stage(File output, byte[] bytes) throws Exception {
        File partial = new File(output.getParentFile(),
            "." + output.getName() + ".partial-" + UUID.randomUUID());
        try (FileChannel channel = FileChannel.open(partial.toPath(),
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            ByteBuffer buffer = ByteBuffer.wrap(bytes);
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
            channel.force(true);
        }
        return partial;
    }

    private static void publish(File partial, File output) throws Exception {
        Files.createLink(output.toPath(), partial.toPath());
        Files.delete(partial.toPath());
    }

    private byte[] readToolSource() throws Exception {
        try (InputStream stream = getSourceFile().getInputStream()) {
            return stream.readAllBytes();
        }
    }

    private byte[] buildReady(String mode, File manifest, byte[] manifestBytes,
            File output, byte[] outputBytes, Counts before, Counts after,
            boolean post, boolean rollbackVerified) throws Exception {
        byte[] toolBytes = readToolSource();
        StringBuilder out = new StringBuilder();
        out.append("{\n");
        out.append("  \"schema\": \"").append(SCHEMA).append("\",\n");
        out.append("  \"status\": \"READY_FOR_SCRATCH_ONLY\",\n");
        out.append("  \"policy\": \"").append(POLICY).append("\",\n");
        out.append("  \"completedAtUtc\": \"").append(Instant.now()).append("\",\n");
        out.append("  \"mode\": \"").append(json(mode)).append("\",\n");
        out.append("  \"manifest\": {\"name\": \"")
            .append(json(manifest.getName())).append("\", \"bytes\": ")
            .append(manifestBytes.length).append(", \"sha256\": \"")
            .append(sha256(manifestBytes)).append("\"},\n");
        out.append("  \"tool\": {\"name\": \"")
            .append(json(getSourceFile().getName())).append("\", \"bytes\": ")
            .append(toolBytes.length).append(", \"sha256\": \"")
            .append(sha256(toolBytes)).append("\"},\n");
        out.append("  \"output\": {\"name\": \"")
            .append(json(output.getName())).append("\", \"bytes\": ")
            .append(outputBytes.length).append(", \"sha256\": \"")
            .append(sha256(outputBytes)).append("\"},\n");
        out.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"md5\": \"").append(PROGRAM_MD5)
            .append("\", \"sha256\": \"").append(PROGRAM_SHA256).append("\"},\n");
        out.append("  \"countsBefore\": ").append(countsJson(before)).append(",\n");
        out.append("  \"countsAfter\": ").append(countsJson(after)).append(",\n");
        out.append("  \"targets\": 5,\n");
        out.append("  \"repairBytes\": 1258,\n");
        out.append("  \"postVerified\": ").append(post).append(",\n");
        out.append("  \"rollbackVerified\": ").append(rollbackVerified).append(",\n");
        out.append("  \"newFunctionsAuthorized\": false,\n");
        out.append("  \"namesSignaturesCommentsTagsDataAuthorized\": false,\n");
        out.append("  \"separateSavedReadbackRequired\": ")
            .append(mode.equals("apply")).append("\n");
        out.append("}\n");
        return out.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static String countsJson(Counts value) {
        return "{\"functions\": " + value.functions +
            ", \"bodyRanges\": " + value.ranges +
            ", \"ownedBytes\": " + value.ownedBytes +
            ", \"instructions\": " + value.instructions +
            ", \"references\": " + value.references + "}";
    }

    private void publishReceipts(String mode, File manifest,
            File output, File ready, List<Target> targets,
            Counts before, Counts after, boolean post,
            boolean rollbackVerified) throws Exception {
        byte[] manifestBytes = Files.readAllBytes(manifest.toPath());
        byte[] outputBytes = buildTsv(targets, mode, post, rollbackVerified);
        byte[] readyBytes = buildReady(mode, manifest, manifestBytes,
            output, outputBytes, before, after, post, rollbackVerified);
        File stagedOutput = null;
        File stagedReady = null;
        try {
            stagedOutput = stage(output, outputBytes);
            stagedReady = stage(ready, readyBytes);
            publish(stagedOutput, output);
            stagedOutput = null;
            publish(stagedReady, ready);
            stagedReady = null;
        } finally {
            if (stagedOutput != null) {
                Files.deleteIfExists(stagedOutput.toPath());
            }
            if (stagedReady != null) {
                Files.deleteIfExists(stagedReady.toPath());
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 4,
            "usage: <package-root> <out.tsv> <out.ready.json> " +
            "<dry|probe-after-one|probe-after-all|apply|readback>");
        File packageRoot = new File(args[0]).getCanonicalFile();
        require(packageRoot.isDirectory(), "package root is not a directory");
        File manifest = new File(packageRoot, MANIFEST_RELATIVE).getCanonicalFile();
        require(manifest.toPath().startsWith(packageRoot.toPath()),
            "manifest escapes package root");
        require(manifest.isFile(), "manifest is missing");
        File output = requireNewOutput(packageRoot, args[1], "output TSV");
        File ready = requireNewOutput(packageRoot, args[2], "READY receipt");
        require(!output.equals(ready), "output paths must differ");
        require(output.getParentFile().equals(ready.getParentFile()),
            "output paths must share one run directory");
        String mode = args[3];
        require(Arrays.asList("dry", "probe-after-one", "probe-after-all",
                "apply", "readback").contains(mode),
            "unsupported mode: " + mode);

        validateProgramIdentity();
        List<Target> targets = loadTargets(manifest);
        boolean initialPost = mode.equals("readback");
        Counts beforeCounts = counts();
        validateCounts(beforeCounts, initialPost, "initial");
        for (Target target : targets) {
            validateTargetState(target, initialPost);
        }
        AddressSet repair = repairUnion(targets);
        Snapshots before = snapshots(repair);

        if (mode.equals("dry") || mode.equals("readback")) {
            publishReceipts(mode, manifest, output, ready, targets,
                beforeCounts, beforeCounts, initialPost, false);
            println("FUNCTION_FRAGMENT_RANGES_OK mode=" + mode +
                " targets=5 functions=" + beforeCounts.functions +
                " ranges=" + beforeCounts.ranges +
                " owned=" + beforeCounts.ownedBytes);
            return;
        }

        int transaction = -1;
        boolean ended = false;
        try {
            transaction = currentProgram.startTransaction(
                "Admit five exact existing-function body fragments");
            for (int index = 0; index < targets.size(); index++) {
                applyOne(targets.get(index));
                if (mode.equals("probe-after-one") && index == 0) {
                    throw new IntentionalProbeException(
                        "forced failure after one function-body repair");
                }
            }
            Counts transientCounts = counts();
            validateCounts(transientCounts, true, "transient POST");
            validatePostSnapshots(before, repair, targets);
            if (mode.equals("probe-after-all")) {
                throw new IntentionalProbeException(
                    "forced failure after all five function-body repairs");
            }
            require(mode.equals("apply"), "unexpected mutating mode");
            boolean commitReturned = currentProgram.endTransaction(transaction, true);
            ended = true;
            require(!commitReturned,
                "nested transaction unexpectedly finalized the outer transaction");
            Counts afterCounts = counts();
            validateCounts(afterCounts, true, "POST");
            publishReceipts(mode, manifest, output, ready, targets,
                beforeCounts, afterCounts, true, false);
            println("FUNCTION_FRAGMENT_RANGES_OK mode=apply targets=5" +
                " functions=" + afterCounts.functions +
                " ranges=" + afterCounts.ranges +
                " owned=" + afterCounts.ownedBytes +
                " references=" + afterCounts.references);
        } catch (IntentionalProbeException ex) {
            if (transaction >= 0 && !ended) {
                boolean rollbackReturned =
                    currentProgram.endTransaction(transaction, false);
                ended = true;
                require(!rollbackReturned,
                    "nested rollback unexpectedly finalized outer transaction");
            }
            Counts transientState = counts();
            println("FUNCTION_FRAGMENT_RANGES_ADVERSE_CONTROL mode=" + mode +
                " transient_functions=" + transientState.functions +
                " transient_ranges=" + transientState.ranges +
                " transient_owned=" + transientState.ownedBytes +
                " recovery=RESTORE_VERIFIED_SCRATCH_BASE_REQUIRED");
            throw ex;
        } catch (Exception ex) {
            if (transaction >= 0 && !ended) {
                try {
                    currentProgram.endTransaction(transaction, false);
                    ended = true;
                } catch (Exception rollbackError) {
                    ex.addSuppressed(rollbackError);
                }
            }
            println("FUNCTION_FRAGMENT_RANGES_TAINTED mode=" + mode +
                " recovery=RESTORE_VERIFIED_SCRATCH_BASE error=" +
                clean(ex.toString()));
            throw ex;
        }
    }
}
