//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.OffsetReference;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ShiftedReference;
import ghidra.program.model.symbol.SourceType;
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
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Create only the 34 proof-bound MissionScript registry function boundaries.
 *
 * The immutable manifest uses half-open ranges [start,endExclusive). Ghidra's
 * AddressSet uses inclusive maxima, so every end is converted exactly once to
 * endExclusive-1 and the byte count is rechecked. No semantic name, comment,
 * signature, parameter, return type, tag, instruction, byte, data, or reference
 * is created or changed by this tool.
 *
 * Usage:
 *   -postScript GhidraApplyMissionRegistryBoundaries.java
 *       <repository_root> <out.tsv> <out.ready.json>
 *       <dry|probe-after-one|probe-post-inner|apply|readback>
 */
public class GhidraApplyMissionRegistryBoundaries extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.mission-registry-boundaries.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String TEXT_BLOCK = ".text";
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final String INSTRUCTION_LAYOUT_SHA256 =
        "ba8b9d6380c2acb63f625b95d6a08d3ae4df209a9da0fa41ae4c13c86e3f4ba2";
    private static final long PRE_FUNCTIONS = 8136;
    private static final long POST_FUNCTIONS = 8170;
    private static final long INSTRUCTIONS = 549872;
    private static final long REFERENCES = 234357;
    private static final String REFERENCES_SHA256 =
        "704d5f045abfdf899761990b23494bf78f4d214bc0f55785184ec431b41abccf";
    private static final int TARGET_COUNT = 34;

    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-missing-function-boundaries-2026-08-13.tsv";
    private static final long MANIFEST_BYTES = 7264;
    private static final String MANIFEST_SHA256 =
        "e53fd6f4c44ab7f91779e0673e91ae3701514c486594cc733025334fe6289a42";
    private static final String MANIFEST_HEADER =
        "registryIndex\tcommand\trecordVa\tentry\treachableBodyRanges\tbodyBytes" +
        "\tbodyRangeSha256\tbodyBytesSha256\tinstructionCount\texpectedDefaultName";

    private static class Target {
        final int registryIndex;
        final String command;
        final Address recordVa;
        final String entryText;
        final Address entry;
        final String rangesText;
        final AddressSet body;
        final long bodyBytes;
        final String bodyRangeSha256;
        final String bodyBytesSha256;
        final long instructionCount;
        final String expectedDefaultName;

        Target(int registryIndex, String command, Address recordVa, String entryText,
                Address entry, String rangesText, AddressSet body, long bodyBytes,
                String bodyRangeSha256, String bodyBytesSha256, long instructionCount,
                String expectedDefaultName) {
            this.registryIndex = registryIndex;
            this.command = command;
            this.recordVa = recordVa;
            this.entryText = entryText;
            this.entry = entry;
            this.rangesText = rangesText;
            this.body = body;
            this.bodyBytes = bodyBytes;
            this.bodyRangeSha256 = bodyRangeSha256;
            this.bodyBytesSha256 = bodyBytesSha256;
            this.instructionCount = instructionCount;
            this.expectedDefaultName = expectedDefaultName;
        }
    }

    private static class Snapshot {
        final long functions;
        final long instructions;
        final String instructionLayoutSha256;
        final String memorySha256;
        final long references;
        final String referencesSha256;
        final String outsideTargetSymbolsSha256;
        final Map<String, String> targetSymbols;
        final Map<String, String> functionBodies;

        Snapshot(long functions, long instructions, String instructionLayoutSha256,
                String memorySha256, long references, String referencesSha256,
                String outsideTargetSymbolsSha256, Map<String, String> targetSymbols,
                Map<String, String> functionBodies) {
            this.functions = functions;
            this.instructions = instructions;
            this.instructionLayoutSha256 = instructionLayoutSha256;
            this.memorySha256 = memorySha256;
            this.references = references;
            this.referencesSha256 = referencesSha256;
            this.outsideTargetSymbolsSha256 = outsideTargetSymbolsSha256;
            this.targetSymbols = targetSymbols;
            this.functionBodies = functionBodies;
        }
    }

    private static void require(boolean value, String message) {
        if (!value) {
            throw new IllegalStateException(message);
        }
    }

    private static void equal(String owner, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(owner + " " + field + " differs expected=" +
                expected + " actual=" + actual);
        }
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
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

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\r", "\\r")
            .replace("\n", "\\n").replace("\t", " ");
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static String json(String value) {
        return clean(value).replace("\"", "\\\"");
    }

    private static String canonical(Address address) {
        return "0x" + address.toString().toLowerCase(Locale.ROOT);
    }

    private static void digestString(MessageDigest digest, String value) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        digest.update((byte) ((bytes.length >>> 24) & 0xff));
        digest.update((byte) ((bytes.length >>> 16) & 0xff));
        digest.update((byte) ((bytes.length >>> 8) & 0xff));
        digest.update((byte) (bytes.length & 0xff));
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

    private Address parseAddress(String value, String label) {
        require(value != null && value.matches("0x[0-9a-f]{8}"),
            label + " is not one canonical address: " + value);
        Address address = toAddr(value);
        require(address != null && canonical(address).equals(value),
            label + " does not resolve canonically: " + value);
        return address;
    }

    private static long positiveLong(String value, String label) {
        try {
            long parsed = Long.parseLong(value);
            require(parsed > 0, label + " must be positive");
            return parsed;
        }
        catch (NumberFormatException error) {
            throw new IllegalArgumentException(label + " must be a decimal integer", error);
        }
    }

    private AddressSet parseHalfOpenRanges(String text, String entry) {
        require(text != null && !text.isEmpty(), "empty body ranges at " + entry);
        AddressSet body = new AddressSet();
        Address priorEndExclusive = null;
        for (String piece : text.split(";", -1)) {
            require(piece.matches("0x[0-9a-f]{8}-0x[0-9a-f]{8}"),
                "malformed half-open range at " + entry + ": " + piece);
            String[] bounds = piece.split("-", -1);
            Address start = parseAddress(bounds[0], "range start");
            Address endExclusive = parseAddress(bounds[1], "range endExclusive");
            require(start.compareTo(endExclusive) < 0,
                "empty or reversed half-open range at " + entry);
            require(priorEndExclusive == null || priorEndExclusive.compareTo(start) < 0,
                "ranges overlap or touch within one body at " + entry);
            body.addRange(start, endExclusive.subtract(1));
            priorEndExclusive = endExclusive;
        }
        equal(entry, "canonical half-open ranges", text, canonicalRanges(body));
        return body;
    }

    private List<Target> loadManifest(File repositoryRoot) throws Exception {
        File manifest = new File(repositoryRoot, MANIFEST_RELATIVE).getCanonicalFile();
        require(manifest.isFile(), "manifest is absent: " + manifest);
        byte[] raw = Files.readAllBytes(manifest.toPath());
        equal("manifest", "bytes", MANIFEST_BYTES, (long) raw.length);
        equal("manifest", "sha256", MANIFEST_SHA256, sha256(raw));
        require(raw.length > 0 && raw[0] != (byte) 0xef, "manifest has a BOM");
        String text = new String(raw, StandardCharsets.UTF_8);
        require(text.indexOf('\r') < 0 && text.endsWith("\n") && !text.endsWith("\n\n"),
            "manifest must be canonical LF text with one trailing LF");
        String[] lines = text.substring(0, text.length() - 1).split("\n", -1);
        equal("manifest", "header", MANIFEST_HEADER, lines[0]);
        equal("manifest", "row count", TARGET_COUNT, lines.length - 1);

        List<Target> targets = new ArrayList<>();
        Set<String> entries = new HashSet<>();
        Set<String> ownedAddresses = new HashSet<>();
        Address priorEntry = null;
        for (int lineNumber = 2; lineNumber <= lines.length; lineNumber++) {
            String[] fields = lines[lineNumber - 1].split("\t", -1);
            equal("manifest line " + lineNumber, "field count", 10, fields.length);
            int registryIndex = (int) positiveLong(fields[0], "registryIndex");
            require(registryIndex >= 0 && registryIndex < 144,
                "registryIndex out of range at line " + lineNumber);
            require(fields[1].matches("[A-Za-z][A-Za-z0-9]*"),
                "command is not canonical at line " + lineNumber);
            Address recordVa = parseAddress(fields[2], "recordVa");
            Address expectedRecord = toAddr(0x0064ce20L + registryIndex * 0x40L);
            equal(fields[1], "registry record address", expectedRecord, recordVa);
            Address entry = parseAddress(fields[3], "entry");
            require(entries.add(fields[3]), "duplicate entry: " + fields[3]);
            require(priorEntry == null || priorEntry.compareTo(entry) < 0,
                "manifest entries are not strictly sorted by address");
            priorEntry = entry;
            AddressSet body = parseHalfOpenRanges(fields[4], fields[3]);
            equal(fields[3], "body minimum", entry, body.getMinAddress());
            long bodyBytes = positiveLong(fields[5], "bodyBytes");
            equal(fields[3], "half-open byte count", bodyBytes, body.getNumAddresses());
            require(fields[6].matches("[0-9a-f]{64}") && fields[7].matches("[0-9a-f]{64}"),
                "manifest digest is malformed at " + fields[3]);
            long instructionCount = positiveLong(fields[8], "instructionCount");
            equal(fields[3], "default name", "FUN_" + fields[3].substring(2), fields[9]);
            AddressIterator addresses = body.getAddresses(true);
            while (addresses.hasNext()) {
                String owned = canonical(addresses.next());
                require(ownedAddresses.add(owned), "manifest bodies overlap at " + owned);
            }
            targets.add(new Target(registryIndex, fields[1], recordVa, fields[3], entry,
                fields[4], body, bodyBytes, fields[6], fields[7], instructionCount, fields[9]));
        }
        return targets;
    }

    private static String canonicalRanges(AddressSetView body) {
        StringBuilder ranges = new StringBuilder();
        for (AddressRange range : body) {
            if (ranges.length() > 0) {
                ranges.append(';');
            }
            ranges.append(canonical(range.getMinAddress()));
            ranges.append('-');
            ranges.append(canonical(range.getMaxAddress().add(1)));
        }
        return ranges.toString();
    }

    private static String bodyRangeSha256(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (AddressRange range : body) {
            digest.update(range.getMinAddress().toString().getBytes(StandardCharsets.UTF_8));
            digest.update((byte) ':');
            digest.update(range.getMaxAddress().toString().getBytes(StandardCharsets.UTF_8));
            digest.update((byte) ';');
        }
        return hex(digest.digest());
    }

    private String bodyBytesSha256(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        AddressIterator addresses = body.getAddresses(true);
        while (addresses.hasNext()) {
            digest.update(currentProgram.getMemory().getByte(addresses.next()));
        }
        return hex(digest.digest());
    }

    private long exactInstructionCount(AddressSetView body, String label) {
        AddressSet covered = new AddressSet();
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            require(body.contains(instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses half-open body at " + label + " instruction=" +
                canonical(instruction.getMinAddress()));
            covered.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
            count++;
        }
        require(covered.hasSameAddresses(body),
            "instruction coverage differs at " + label + " expected=" +
            canonicalRanges(body) + " covered=" + canonicalRanges(covered));
        return count;
    }

    private long instructionCount(AddressSetView body) {
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            instructions.next();
            count++;
        }
        return count;
    }

    private void validateEnvelope(Target target) throws Exception {
        for (AddressRange range : target.body) {
            MemoryBlock first = currentProgram.getMemory().getBlock(range.getMinAddress());
            MemoryBlock last = currentProgram.getMemory().getBlock(range.getMaxAddress());
            require(first != null && first == last && TEXT_BLOCK.equals(first.getName()) &&
                    first.isInitialized() && first.isExecute(),
                "body is not initialized executable .text at " + target.entryText);
        }
        equal(target.entryText, "half-open ranges", target.rangesText,
            canonicalRanges(target.body));
        equal(target.entryText, "body bytes", target.bodyBytes, target.body.getNumAddresses());
        equal(target.entryText, "range digest", target.bodyRangeSha256,
            bodyRangeSha256(target.body));
        equal(target.entryText, "body-byte digest", target.bodyBytesSha256,
            bodyBytesSha256(target.body));
        equal(target.entryText, "instruction count", target.instructionCount,
            exactInstructionCount(target.body, target.entryText));
        require(currentProgram.getListing().getInstructionAt(target.entry) != null,
            "entry is not an already-defined instruction: " + target.entryText);
    }

    private void validateProgramIdentity() throws Exception {
        require(currentProgram != null, "no current program");
        equal("program", "name", PROGRAM_NAME, currentProgram.getName());
        equal("program", "md5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        equal("program", "sha256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        equal("program", "image base", IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        equal("program", "language", LANGUAGE, currentProgram.getLanguageID().toString());
        equal("program", "compiler spec", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
    }

    private String memorySha256() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Memory memory = currentProgram.getMemory();
        List<MemoryBlock> blocks = new ArrayList<>(Arrays.asList(memory.getBlocks()));
        blocks.sort(Comparator.comparing(MemoryBlock::getStart)
            .thenComparing(MemoryBlock::getEnd).thenComparing(MemoryBlock::getName));
        for (MemoryBlock block : blocks) {
            String source = block.getSourceName();
            String comment = block.getComment();
            digestString(digest, block.getName().length() + ":" + sha256(block.getName()) +
                "\t" + (source == null ? -1 : source.length()) + ":" + sha256(nullable(source)) +
                "\t" + (comment == null ? -1 : comment.length()) + ":" + sha256(nullable(comment)) +
                "\t" + block.getStart() + "\t" + block.getEnd() + "\t" + block.getSize() +
                "\t" + block.isInitialized() + "\t" + block.isRead() + "\t" + block.isWrite() +
                "\t" + block.isExecute() + "\t" + block.isVolatile() +
                "\t" + block.isArtificial() + "\t" + block.isMapped() +
                "\t" + block.isOverlay() + "\t" + block.isLoaded() + "\t" + block.getType());
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
                equal("program", "memory read", size, read);
                digest.update(chunk);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    private String instructionLayoutSha256() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            digestString(digest, instruction.getAddress().toString());
            digestString(digest, Integer.toString(instruction.getLength()));
            digest.update(instruction.getBytes());
            digestString(digest, instruction.getMnemonicString());
            digestString(digest, instruction.getFlowType().toString());
            digestString(digest, String.valueOf(instruction.getFallThrough()));
            digestString(digest, Arrays.toString(instruction.getFlows()));
            digestString(digest, instruction.getFlowOverride().toString());
            digestString(digest, Boolean.toString(instruction.isLengthOverridden()));
        }
        return hex(digest.digest());
    }

    private String referenceRow(Reference reference) {
        String offsetBase = "";
        String offset = "";
        if (reference instanceof OffsetReference) {
            OffsetReference value = (OffsetReference) reference;
            offsetBase = String.valueOf(value.getBaseAddress());
            offset = Long.toString(value.getOffset());
        }
        String shift = "";
        String shiftedValue = "";
        if (reference instanceof ShiftedReference) {
            ShiftedReference value = (ShiftedReference) reference;
            shift = Integer.toString(value.getShift());
            shiftedValue = Long.toString(value.getValue());
        }
        return reference.getFromAddress() + "\t" + reference.getToAddress() + "\t" +
            reference.getOperandIndex() + "\t" + reference.getReferenceType() + "\t" +
            reference.getSource() + "\t" + reference.isPrimary() + "\t" +
            reference.getSymbolID() + "\t" + reference.isMnemonicReference() + "\t" +
            reference.isOperandReference() + "\t" + reference.isStackReference() + "\t" +
            reference.isExternalReference() + "\t" + reference.isEntryPointReference() + "\t" +
            reference.isMemoryReference() + "\t" + reference.isRegisterReference() + "\t" +
            reference.isOffsetReference() + "\t" + reference.isShiftedReference() + "\t" +
            offsetBase + "\t" + offset + "\t" + shift + "\t" + shiftedValue;
    }

    private String symbolRow(Symbol symbol) {
        String namespace = symbol.getParentNamespace() == null ? "" :
            symbol.getParentNamespace().getName(true);
        return symbol.getAddress() + "\t" + clean(symbol.getName()) + "\t" +
            clean(symbol.getName(true)) + "\t" + clean(namespace) + "\t" +
            symbol.getSymbolType() + "\t" + symbol.getSource() + "\t" +
            symbol.isPrimary() + "\t" + symbol.isDynamic() + "\t" +
            symbol.isExternal() + "\t" + symbol.isPinned();
    }

    private String functionEnvelope(Function function) throws Exception {
        AddressSetView body = function.getBody();
        return canonicalRanges(body) + "|" + body.getNumAddresses() + "|" +
            bodyRangeSha256(body) + "|" + instructionCount(body);
    }

    private Snapshot snapshot(List<Target> targets) throws Exception {
        Set<Address> targetAddresses = new HashSet<>();
        for (Target target : targets) {
            targetAddresses.add(target.entry);
        }
        Map<String, String> functionBodies = new LinkedHashMap<>();
        long functionCount = 0;
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            Function function = functions.next();
            functionCount++;
            String entry = canonical(function.getEntryPoint());
            require(functionBodies.put(entry, functionEnvelope(function)) == null,
                "duplicate function entry in snapshot: " + entry);
        }
        long instructionCount = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            instructions.next();
            instructionCount++;
        }
        List<String> references = new ArrayList<>();
        ReferenceIterator referenceIterator = currentProgram.getReferenceManager()
            .getReferenceIterator(currentProgram.getMinAddress());
        while (referenceIterator.hasNext()) {
            monitor.checkCancelled();
            references.add(referenceRow(referenceIterator.next()));
        }
        Map<String, List<String>> targetSymbolRows = new HashMap<>();
        List<String> outsideSymbols = new ArrayList<>();
        for (Symbol symbol : currentProgram.getSymbolTable().getAllSymbols(true)) {
            String row = symbolRow(symbol);
            if (targetAddresses.contains(symbol.getAddress())) {
                targetSymbolRows.computeIfAbsent(canonical(symbol.getAddress()),
                    ignored -> new ArrayList<>()).add(row);
            }
            else {
                outsideSymbols.add(row);
            }
        }
        Map<String, String> targetSymbols = new LinkedHashMap<>();
        for (Target target : targets) {
            List<String> rows = targetSymbolRows.getOrDefault(target.entryText,
                new ArrayList<>());
            Collections.sort(rows);
            targetSymbols.put(target.entryText, String.join("||", rows));
        }
        Snapshot result = new Snapshot(functionCount, instructionCount,
            instructionLayoutSha256(), memorySha256(), references.size(),
            sortedDigest(references), sortedDigest(outsideSymbols), targetSymbols,
            functionBodies);
        equal("program", "instructions", INSTRUCTIONS, result.instructions);
        equal("program", "instruction layout", INSTRUCTION_LAYOUT_SHA256,
            result.instructionLayoutSha256);
        equal("program", "memory", MEMORY_SHA256, result.memorySha256);
        equal("program", "references", REFERENCES, result.references);
        equal("program", "reference digest", REFERENCES_SHA256, result.referencesSha256);
        return result;
    }

    private Function exactFunction(Target target) {
        Function function = currentProgram.getFunctionManager().getFunctionAt(target.entry);
        return function != null && function.getEntryPoint().equals(target.entry) ? function : null;
    }

    private void validatePreTarget(Target target, Snapshot pre) {
        require(exactFunction(target) == null, "function already exists at " + target.entryText);
        AddressIterator addresses = target.body.getAddresses(true);
        while (addresses.hasNext()) {
            Address address = addresses.next();
            Function containing = currentProgram.getFunctionManager().getFunctionContaining(address);
            if (containing != null) {
                throw new IllegalStateException("target body intersects function " +
                    canonical(containing.getEntryPoint()) + " at " + canonical(address));
            }
        }
        String symbols = pre.targetSymbols.get(target.entryText);
        if (!symbols.isEmpty()) {
            String[] rows = symbols.split("\\|\\|", -1);
            require(rows.length == 1, "target has multiple PRE symbols: " + target.entryText);
            require(rows[0].contains("\tLabel\tDEFAULT\ttrue\ttrue\tfalse\tfalse"),
                "target has a non-default or non-dynamic PRE symbol: " + target.entryText +
                " symbol=" + rows[0]);
        }
    }

    private void validatePostTarget(Target target) throws Exception {
        Function function = exactFunction(target);
        require(function != null, "created function is absent at " + target.entryText);
        equal(target.entryText, "name", target.expectedDefaultName, function.getName());
        equal(target.entryText, "name source", SourceType.DEFAULT,
            function.getSymbol().getSource());
        equal(target.entryText, "signature source", SourceType.DEFAULT,
            function.getSignatureSource());
        require(function.getParameterCount() == 0 &&
                "unknown".equals(function.getCallingConventionName()) &&
                "undefined".equals(function.getReturn().getDataType().getDisplayName()) &&
                !function.hasCustomVariableStorage() && !function.hasVarArgs() &&
                !function.isInline() && !function.hasNoReturn() && !function.isThunk(),
            "created function gained semantic metadata at " + target.entryText);
        require(function.getComment() == null && function.getRepeatableComment() == null &&
                !function.getTags().iterator().hasNext(),
            "created function gained comments or tags at " + target.entryText);
        equal(target.entryText, "body ranges", target.rangesText,
            canonicalRanges(function.getBody()));
        equal(target.entryText, "body bytes", target.bodyBytes,
            function.getBody().getNumAddresses());
        equal(target.entryText, "range digest", target.bodyRangeSha256,
            bodyRangeSha256(function.getBody()));
        equal(target.entryText, "body-byte digest", target.bodyBytesSha256,
            bodyBytesSha256(function.getBody()));
        equal(target.entryText, "instructions", target.instructionCount,
            exactInstructionCount(function.getBody(), target.entryText));
    }

    private void validatePre(List<Target> targets, Snapshot pre) {
        equal("PRE", "function count", PRE_FUNCTIONS, pre.functions);
        for (Target target : targets) {
            validatePreTarget(target, pre);
        }
    }

    private void validatePost(List<Target> targets, Snapshot pre, Snapshot post) throws Exception {
        equal("POST", "function count", POST_FUNCTIONS, post.functions);
        Set<String> targetEntries = new HashSet<>();
        for (Target target : targets) {
            targetEntries.add(target.entryText);
            validatePostTarget(target);
        }
        Map<String, String> remaining = new LinkedHashMap<>(post.functionBodies);
        for (String target : targetEntries) {
            remaining.remove(target);
        }
        equal("POST", "pre-existing function bodies", pre.functionBodies, remaining);
        equal("POST", "outside-target symbols", pre.outsideTargetSymbolsSha256,
            post.outsideTargetSymbolsSha256);
        for (Target target : targets) {
            String symbols = post.targetSymbols.get(target.entryText);
            String expectedFragment = "\t" + target.expectedDefaultName + "\t" +
                target.expectedDefaultName + "\tGlobal\tFunction\tDEFAULT\ttrue\tfalse\tfalse\tfalse";
            require(symbols != null && !symbols.contains("||") && symbols.contains(expectedFragment),
                "POST target symbol differs at " + target.entryText + " actual=" + symbols);
        }
    }

    private static File newOutput(String value, String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        require(!output.exists(), label + " already exists: " + output);
        require(output.getParentFile() != null && output.getParentFile().isDirectory(),
            label + " parent is absent: " + output);
        return output;
    }

    private static File stage(File target, byte[] bytes) throws Exception {
        File partial = new File(target.getParentFile(), "." + target.getName() +
            ".partial-" + UUID.randomUUID());
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

    private static void publish(File partial, File target) throws Exception {
        Files.createLink(target.toPath(), partial.toPath());
        Files.delete(partial.toPath());
    }

    private byte[] buildTsv(String mode, String state, List<Target> targets) throws Exception {
        StringBuilder output = new StringBuilder(
            "registryIndex\tcommand\trecordVa\tentry\tmode\tstate\tname\tnameSource" +
            "\tsigSource\treachableBodyRanges\tbodyBytes\tbodyRangeSha256" +
            "\tbodyBytesSha256\tinstructionCount\tisThunk\tcommentPresent" +
            "\trepeatableCommentPresent\ttagCount\n");
        for (Target target : targets) {
            Function function = exactFunction(target);
            output.append(target.registryIndex).append('\t').append(target.command).append('\t')
                .append(canonical(target.recordVa)).append('\t').append(target.entryText).append('\t')
                .append(mode).append('\t').append(state).append('\t')
                .append(function == null ? "" : function.getName()).append('\t')
                .append(function == null ? "" : function.getSymbol().getSource()).append('\t')
                .append(function == null ? "" : function.getSignatureSource()).append('\t')
                .append(target.rangesText).append('\t').append(target.bodyBytes).append('\t')
                .append(target.bodyRangeSha256).append('\t').append(target.bodyBytesSha256)
                .append('\t').append(target.instructionCount).append('\t')
                .append(function != null && function.isThunk()).append('\t')
                .append(function != null && function.getComment() != null).append('\t')
                .append(function != null && function.getRepeatableComment() != null).append('\t')
                .append(function == null ? 0 : function.getTags().size()).append('\n');
        }
        return output.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(String mode, String state, byte[] toolBytes, File manifest,
            File output, byte[] outputBytes, Snapshot snapshot) throws Exception {
        String ready = "{\n" +
            "  \"schemaVersion\": \"" + SCHEMA + "\",\n" +
            "  \"completedAtUtc\": \"" + Instant.now().toString() + "\",\n" +
            "  \"mode\": \"" + mode + "\",\n" +
            "  \"state\": \"" + state + "\",\n" +
            "  \"program\": {\"name\": \"" + PROGRAM_NAME + "\", \"md5\": \"" +
                PROGRAM_MD5 + "\", \"sha256\": \"" + PROGRAM_SHA256 + "\", " +
                "\"functions\": " + snapshot.functions + ", \"instructions\": " +
                snapshot.instructions + ", \"instructionLayoutSha256\": \"" +
                snapshot.instructionLayoutSha256 + "\", \"memorySha256\": \"" +
                snapshot.memorySha256 + "\", \"references\": " + snapshot.references +
                ", \"referencesSha256\": \"" + snapshot.referencesSha256 + "\"},\n" +
            "  \"manifest\": {\"path\": \"" + json(manifest.getCanonicalPath()) +
                "\", \"bytes\": " + MANIFEST_BYTES + ", \"sha256\": \"" +
                MANIFEST_SHA256 + "\", \"targets\": " + TARGET_COUNT + "},\n" +
            "  \"tool\": {\"path\": \"" + json(getSourceFile().getCanonicalPath()) +
                "\", \"bytes\": " + toolBytes.length + ", \"sha256\": \"" +
                sha256(toolBytes) + "\"},\n" +
            "  \"output\": {\"path\": \"" + json(output.getCanonicalPath()) +
                "\", \"bytes\": " + outputBytes.length + ", \"sha256\": \"" +
                sha256(outputBytes) + "\"},\n" +
            "  \"outsideTargetSymbolsSha256\": \"" +
                snapshot.outsideTargetSymbolsSha256 + "\",\n" +
            "  \"boundariesChanged\": " + (state.equals("POST") ? TARGET_COUNT : 0) + ",\n" +
            "  \"namesAuthorized\": false,\n" +
            "  \"metadataAuthorized\": false\n" +
            "}\n";
        return ready.getBytes(StandardCharsets.UTF_8);
    }

    private void publishPair(File output, byte[] outputBytes, File ready, byte[] readyBytes)
            throws Exception {
        File outputPartial = null;
        File readyPartial = null;
        try {
            outputPartial = stage(output, outputBytes);
            readyPartial = stage(ready, readyBytes);
            publish(outputPartial, output);
            outputPartial = null;
            publish(readyPartial, ready);
            readyPartial = null;
        }
        finally {
            if (outputPartial != null) Files.deleteIfExists(outputPartial.toPath());
            if (readyPartial != null) Files.deleteIfExists(readyPartial.toPath());
        }
    }

    private void restorePre(List<Target> targets) {
        for (int index = targets.size() - 1; index >= 0; index--) {
            Target target = targets.get(index);
            require(currentProgram.getFunctionManager().removeFunction(target.entry),
                "failed to remove probe function at " + target.entryText);
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 4,
            "usage: <repository_root> <out.tsv> <out.ready.json> " +
            "<dry|probe-after-one|probe-post-inner|apply|readback>");
        File repositoryRoot = new File(args[0]).getCanonicalFile();
        require(repositoryRoot.isDirectory(), "repository root is absent: " + repositoryRoot);
        File output = newOutput(args[1], "TSV output");
        File ready = newOutput(args[2], "READY output");
        require(!output.equals(ready), "TSV and READY outputs must differ");
        String mode = args[3].toLowerCase(Locale.ROOT);
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
            .contains(mode), "invalid mode: " + mode);

        validateProgramIdentity();
        List<Target> targets = loadManifest(repositoryRoot);
        for (Target target : targets) {
            validateEnvelope(target);
        }
        Snapshot initial = snapshot(targets);
        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File manifest = new File(repositoryRoot, MANIFEST_RELATIVE).getCanonicalFile();

        if (mode.equals("readback")) {
            equal("readback", "function count", POST_FUNCTIONS, initial.functions);
            for (Target target : targets) {
                validatePostTarget(target);
            }
            byte[] tsv = buildTsv(mode, "POST", targets);
            publishPair(output, tsv, ready,
                buildReady(mode, "POST", toolBytes, manifest, output, tsv, initial));
            println("MISSION_REGISTRY_BOUNDARIES_READBACK_COMPLETE targets=34 " +
                "function_count=8170 loaded_state_verified=true");
            return;
        }

        validatePre(targets, initial);
        println("MISSION_REGISTRY_BOUNDARIES_PREFLIGHT_OK targets=34 functions=8136 " +
            "instructions=549872 half_open_ranges_verified=true");
        if (mode.equals("dry")) {
            byte[] tsv = buildTsv(mode, "PRE", targets);
            publishPair(output, tsv, ready,
                buildReady(mode, "PRE", toolBytes, manifest, output, tsv, initial));
            println("MISSION_REGISTRY_BOUNDARIES_DRY_COMPLETE targets=34 mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires a healthy outer Ghidra transaction");
        int transaction = currentProgram.startTransaction(
            "Create 34 MissionScript registry function boundaries");
        boolean ended = false;
        boolean nestedCommitted = false;
        try {
            int limit = mode.equals("probe-after-one") ? 1 : targets.size();
            for (int index = 0; index < limit; index++) {
                Target target = targets.get(index);
                Function function = createFunction(target.entry, null);
                require(function != null, "Ghidra failed to create " + target.entryText);
                validatePostTarget(target);
            }
            if (mode.equals("probe-after-one")) {
                println("MISSION_REGISTRY_BOUNDARIES_FORCED_AFTER_ONE_FAILURE " +
                    "rollback_required=true");
                throw new IllegalStateException(
                    "intentional Mission registry after-one rollback probe");
            }
            nestedCommitted = currentProgram.endTransaction(transaction, true);
            ended = true;
            require(!nestedCommitted, "nested transaction unexpectedly committed outer transaction");

            Snapshot post = snapshot(targets);
            validatePost(targets, initial, post);
            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore PRE after Mission registry post-inner probe");
                boolean restoreEnded = false;
                try {
                    restorePre(targets);
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    require(!restoreCommitted,
                        "restore nested transaction unexpectedly committed outer transaction");
                }
                finally {
                    if (!restoreEnded) {
                        currentProgram.endTransaction(restore, false);
                    }
                }
                Snapshot restored = snapshot(targets);
                validatePre(targets, restored);
                equal("restored PRE", "function bodies", initial.functionBodies,
                    restored.functionBodies);
                equal("restored PRE", "target symbols", initial.targetSymbols,
                    restored.targetSymbols);
                equal("restored PRE", "outside symbols", initial.outsideTargetSymbolsSha256,
                    restored.outsideTargetSymbolsSha256);
                println("MISSION_REGISTRY_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE " +
                    "targets=34");
                println("MISSION_REGISTRY_BOUNDARIES_FORCED_POST_INNER_FAILURE " +
                    "pre_restored=true");
                throw new IllegalStateException(
                    "intentional Mission registry post-inner rollback probe");
            }

            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            byte[] tsv = buildTsv(mode, "POST", targets);
            publishPair(output, tsv, ready,
                buildReady(mode, "POST", toolBytes, manifest, output, tsv, post));
            println("MISSION_REGISTRY_BOUNDARIES_APPLY_COMPLETE targets=34 " +
                "function_count=8170 reopen_verification_required=true");
        }
        catch (Exception error) {
            if (!ended) {
                try {
                    nestedCommitted = currentProgram.endTransaction(transaction, false);
                    ended = true;
                }
                catch (Exception rollbackError) {
                    error.addSuppressed(rollbackError);
                }
            }
            println("MISSION_REGISTRY_BOUNDARIES_MUTATION_TAINTED mode=" + mode +
                " nested_committed=" + nestedCommitted +
                " recovery=" + (mode.equals("probe-post-inner") ?
                    "COMPENSATING_PRE_RESTORE_VERIFIED" :
                    "RESTORE_VERIFIED_SCRATCH_BASE"));
            throw error;
        }
    }
}
