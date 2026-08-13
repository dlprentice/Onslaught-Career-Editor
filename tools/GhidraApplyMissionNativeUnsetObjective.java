//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.Undefined4DataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.listing.ReturnParameterImpl;
import ghidra.program.model.listing.Variable;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.io.File;
import java.io.InputStream;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * Create and annotate exactly the shipped Mission native UnsetObjective handler.
 *
 * The tool is deliberately bound to one pristine specimen, one Generation 19
 * campaign, one reviewed proof, one authority selector, and one byte-complete
 * listing export. It cannot be reused as a generic function-creation or rename
 * script.
 *
 * Modes:
 *   dry                validate exact PRE state, publish no mutation;
 *   probe-after-create create the natural function, then force rollback;
 *   probe-post-inner   apply the full POST state, restore PRE in a second
 *                      nested transaction, then force failure;
 *   apply              create/name/type/comment the function atomically;
 *   readback           require exact POST state without mutation.
 */
public class GhidraApplyMissionNativeUnsetObjective extends GhidraScript {
    private static final String SCHEMA =
        "bea.ghidra.mission-native-unsetobjective-promotion.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final long PRE_FUNCTION_COUNT = 8125;
    private static final long POST_FUNCTION_COUNT = 8126;
    private static final long INSTRUCTION_COUNT = 549872;

    private static final String CAMPAIGN_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-19-mission-native-unsetobjective-reproof-v1/campaign.ready.json";
    private static final long CAMPAIGN_BYTES = 27833;
    private static final String CAMPAIGN_SHA256 =
        "f83dbb6eddaa16deed5f2a2460d393dc4525a63ae243b6cac0c656056b69ab9a";
    private static final String PROOF_RELATIVE =
        "local-lab/mission-native-unsetobjective-boundary-reproof-20260809-v1/" +
        "proof.ready.json";
    private static final long PROOF_BYTES = 16268;
    private static final String PROOF_SHA256 =
        "c6ae222d26b37863ae575b5af32ddf1a64d8660cb45adb60965610704ec37858";
    private static final String AUTHORITY_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-19-mission-native-unsetobjective-reproof-authority.ready.json";
    private static final long AUTHORITY_BYTES = 12562;
    private static final String AUTHORITY_SHA256 =
        "72c22f029cd2f845c853dfbf2f5746062eed85ccc11d0291b531051c1e432360";
    private static final String MANIFEST_RELATIVE =
        "local-lab/mission-native-unsetobjective-boundary-reproof-20260809-v1/" +
        "ghidra-readonly-byte-complete/instructions.tsv";
    private static final long MANIFEST_BYTES = 220537;
    private static final String MANIFEST_SHA256 =
        "2225b37a9e83347fa0f46f45fefd4ade45be6ba021f87e51ed299ff5ebd5340d";

    private static final String ENTRY = "0x00535ee0";
    private static final String BODY_START = "0x00535ee0";
    private static final String BODY_END_EXCLUSIVE = "0x00535eed";
    private static final String BODY_END_INCLUSIVE = "0x00535eec";
    private static final long BODY_BYTES = 13;
    private static final String BODY_RANGE_DIGEST =
        "6c032733dc164b583a792a9d1b9fc951d07d9f8ec25c31591417b5dcf3b73ab1";
    private static final String BODY_SHA256 =
        "0ec7dfff6ad0dba017b45b0a9840f6b587b899e88aaedb29d1d0eabfb842b35f";
    private static final long BODY_INSTRUCTIONS = 4;
    private static final String PREFIX_START = "0x00535edd";
    private static final String PREFIX_END_INCLUSIVE = "0x00535edf";
    private static final long PREFIX_BYTES = 3;
    private static final String PREFIX_SHA256 =
        "e65ca7c06ae3e9bacd16f6d87026d2fd51447f87f8771676568af93c6313d707";
    private static final String SUFFIX_START = "0x00535eed";
    private static final String SUFFIX_END_INCLUSIVE = "0x00535eef";
    private static final long SUFFIX_BYTES = 3;
    private static final String SUFFIX_SHA256 =
        "e65ca7c06ae3e9bacd16f6d87026d2fd51447f87f8771676568af93c6313d707";

    private static final String DEFAULT_NAME = "FUN_00535ee0";
    private static final String POST_NAME = "IScript__UnsetObjective";
    private static final String POST_SIGNATURE =
        "void __thiscall IScript__UnsetObjective(void * this, undefined4 unusedVmSlot0, " +
        "undefined4 unusedVmSlot1, undefined4 unusedVmSlot2)";
    private static final String POST_COMMENT =
        "Shipped Mission native registry index 30 uniquely binds UnsetObjective " +
        "to 0x00535EE0. Pristine bytes and byte-complete Ghidra listing/xref " +
        "evidence prove a 13-byte, 4-instruction function bracketed by 3 " +
        "leading and 3 trailing NOP bytes. Static contract: __thiscall with " +
        "RET 0x0C; load ECX from this+0x10, push literal 0, and call " +
        "0x004F3970. The three callee-cleaned VM stack slots are not read. " +
        "Callee semantics, runtime effects, EAX return, HUD behavior, " +
        "invalid-object handling, and the full objective-system contract are " +
        "not promoted; the Generation 19 behavioral refuter remains UNSCORED. " +
        "Gen19 READY f83dbb6eddaa; proof c6ae222d26b3. " +
        "STRUCTURAL_STATIC_ONLY.";

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    private static void requireEqual(
            String label, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(label + " " + field +
                " differs expected=" + expected + " actual=" + actual);
        }
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
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

    private static String json(String value) {
        return value.replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\r", "\\r").replace("\n", "\\n")
            .replace("\t", "\\t");
    }

    private long functionCount() {
        long count = 0;
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            iterator.next();
            count++;
        }
        return count;
    }

    private long instructionCount() {
        long count = 0;
        InstructionIterator iterator = currentProgram.getListing().getInstructions(true);
        while (iterator.hasNext()) {
            iterator.next();
            count++;
        }
        return count;
    }

    private static void digestString(MessageDigest digest, String value) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        digest.update((byte) ((bytes.length >>> 24) & 0xff));
        digest.update((byte) ((bytes.length >>> 16) & 0xff));
        digest.update((byte) ((bytes.length >>> 8) & 0xff));
        digest.update((byte) (bytes.length & 0xff));
        digest.update(bytes);
    }

    private String memoryDigest() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Memory memory = currentProgram.getMemory();
        List<MemoryBlock> blocks = new ArrayList<>(Arrays.asList(memory.getBlocks()));
        blocks.sort(Comparator.comparing(MemoryBlock::getStart)
            .thenComparing(MemoryBlock::getEnd).thenComparing(MemoryBlock::getName));
        for (MemoryBlock block : blocks) {
            String name = block.getName();
            String source = block.getSourceName();
            String comment = block.getComment();
            digestString(digest,
                name.length() + ":" + sha256(name.getBytes(StandardCharsets.UTF_8)) +
                "\t" + (source == null ? -1 : source.length()) + ":" +
                sha256(nullable(source).getBytes(StandardCharsets.UTF_8)) +
                "\t" + (comment == null ? -1 : comment.length()) + ":" +
                sha256(nullable(comment).getBytes(StandardCharsets.UTF_8)) +
                "\t" + block.getStart() + "\t" + block.getEnd() + "\t" +
                block.getSize() + "\t" + block.isInitialized() + "\t" +
                block.isRead() + "\t" + block.isWrite() + "\t" + block.isExecute() +
                "\t" + block.isVolatile() + "\t" + block.isArtificial() + "\t" +
                block.isMapped() + "\t" + block.isOverlay() + "\t" + block.isLoaded() +
                "\t" + block.getType());
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
                requireEqual("program", "memory read", size, read);
                digest.update(chunk);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    private void validateProgram(long expectedFunctions) throws Exception {
        requireEqual("program", "name", PROGRAM_NAME, currentProgram.getName());
        requireEqual("program", "MD5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        requireEqual("program", "SHA-256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        requireEqual("program", "image base", IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        requireEqual("program", "language", LANGUAGE,
            currentProgram.getLanguageID().toString());
        requireEqual("program", "compiler", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        requireEqual("program", "memory", MEMORY_SHA256, memoryDigest());
        requireEqual("program", "function count", expectedFunctions, functionCount());
        requireEqual("program", "instruction count", INSTRUCTION_COUNT,
            instructionCount());
    }

    private byte[] bytes(String start, long length) throws Exception {
        byte[] result = new byte[(int) length];
        int read = currentProgram.getMemory().getBytes(toAddr(start), result);
        requireEqual(start, "memory bytes read", (int) length, read);
        return result;
    }

    private void validatePadding(
            String label, String start, long length, String expectedSha) throws Exception {
        byte[] actual = bytes(start, length);
        requireEqual(label, "SHA-256", expectedSha, sha256(actual));
        for (int index = 0; index < actual.length; index++) {
            requireEqual(label, "NOP byte " + index, 0x90, actual[index] & 0xff);
        }
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

    private String bodyBytesSha256(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        AddressIterator iterator = body.getAddresses(true);
        while (iterator.hasNext()) {
            digest.update(currentProgram.getMemory().getByte(iterator.next()));
        }
        return hex(digest.digest());
    }

    private long exactInstructionCount(AddressSetView body) {
        AddressSet covered = new AddressSet();
        long count = 0;
        InstructionIterator iterator = currentProgram.getListing().getInstructions(body, true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            require(body.contains(instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses UnsetObjective body: " + instruction.getAddress());
            covered.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
            count++;
        }
        require(covered.hasSameAddresses(body), "UnsetObjective instruction coverage differs");
        return count;
    }

    private AddressSet expectedBody() {
        return new AddressSet(toAddr(BODY_START), toAddr(BODY_END_INCLUSIVE));
    }

    private void validateBody(Function function) throws Exception {
        AddressSetView body = function.getBody();
        requireEqual(ENTRY, "entry", toAddr(ENTRY), function.getEntryPoint());
        requireEqual(ENTRY, "body bytes", BODY_BYTES, body.getNumAddresses());
        requireEqual(ENTRY, "body minimum", toAddr(BODY_START), body.getMinAddress());
        requireEqual(ENTRY, "body maximum", toAddr(BODY_END_INCLUSIVE), body.getMaxAddress());
        require(body.hasSameAddresses(expectedBody()), "UnsetObjective body addresses differ");
        requireEqual(ENTRY, "body range digest", BODY_RANGE_DIGEST,
            bodyRangeDigest(body));
        requireEqual(ENTRY, "body byte SHA-256", BODY_SHA256,
            bodyBytesSha256(body));
        requireEqual(ENTRY, "instruction count", BODY_INSTRUCTIONS,
            exactInstructionCount(body));
        requireEqual(ENTRY, "thunk", false, function.isThunk());
        requireEqual(ENTRY, "call fixup", null, function.getCallFixup());
        requireEqual(ENTRY, "repeatable comment", null, function.getRepeatableComment());
        requireEqual(ENTRY, "tag count", 0, function.getTags().size());
    }

    private void validateDecodedPreBody() throws Exception {
        AddressSet body = expectedBody();
        requireEqual(ENTRY, "decoded body SHA-256", BODY_SHA256, sha256(bytes(BODY_START, BODY_BYTES)));
        requireEqual(ENTRY, "decoded instruction count", BODY_INSTRUCTIONS,
            exactInstructionCount(body));
    }

    private void requireNoFunctionOrName() throws Exception {
        Address cursor = toAddr(BODY_START);
        Address end = toAddr(BODY_END_INCLUSIVE);
        while (cursor.compareTo(end) <= 0) {
            requireEqual(ENTRY, "PRE containing function at " + cursor, null,
                currentProgram.getFunctionManager().getFunctionContaining(cursor));
            cursor = cursor.next();
        }
        SymbolIterator symbols = currentProgram.getSymbolTable().getSymbols(POST_NAME);
        require(!symbols.hasNext(), "proposed name already exists: " + POST_NAME);
    }

    private void validatePre() throws Exception {
        validateProgram(PRE_FUNCTION_COUNT);
        validatePadding("prefix", PREFIX_START, PREFIX_BYTES, PREFIX_SHA256);
        validatePadding("suffix", SUFFIX_START, SUFFIX_BYTES, SUFFIX_SHA256);
        validateDecodedPreBody();
        requireNoFunctionOrName();
    }

    private static String signature(Function function) {
        return function.getSignature().getPrototypeString(true);
    }

    private void validatePost() throws Exception {
        validateProgram(POST_FUNCTION_COUNT);
        validatePadding("prefix", PREFIX_START, PREFIX_BYTES, PREFIX_SHA256);
        validatePadding("suffix", SUFFIX_START, SUFFIX_BYTES, SUFFIX_SHA256);
        Function function = getFunctionAt(toAddr(ENTRY));
        require(function != null, "UnsetObjective function is absent");
        validateBody(function);
        requireEqual(ENTRY, "POST name", POST_NAME, function.getName());
        requireEqual(ENTRY, "POST name source", SourceType.USER_DEFINED,
            function.getSymbol().getSource());
        requireEqual(ENTRY, "POST signature source", SourceType.USER_DEFINED,
            function.getSignatureSource());
        requireEqual(ENTRY, "POST signature", POST_SIGNATURE, signature(function));
        requireEqual(ENTRY, "POST comment", POST_COMMENT, function.getComment());
        requireEqual(ENTRY, "POST parameter count", 4, function.getParameterCount());
        Parameter[] parameters = function.getParameters();
        String[] names = {"this", "unusedVmSlot0", "unusedVmSlot1", "unusedVmSlot2"};
        String[] types = {"void *", "undefined4", "undefined4", "undefined4"};
        for (int index = 0; index < names.length; index++) {
            requireEqual(ENTRY, "POST parameter name " + index,
                names[index], parameters[index].getName());
            requireEqual(ENTRY, "POST parameter type " + index,
                types[index], parameters[index].getDataType().getDisplayName());
        }
        requireEqual(ENTRY, "POST stack parameter bytes", 12,
            function.getStackFrame().getParameterSize());
    }

    private Function createNaturalFunction() throws Exception {
        Function function = createFunction(toAddr(ENTRY), null);
        require(function != null, "natural UnsetObjective function creation failed");
        validateBody(function);
        requireEqual(ENTRY, "natural name", DEFAULT_NAME, function.getName());
        requireEqual(ENTRY, "natural name source", SourceType.DEFAULT,
            function.getSymbol().getSource());
        return function;
    }

    private void applyPost() throws Exception {
        Function function = createNaturalFunction();
        Variable[] parameters = new Variable[] {
            new ParameterImpl("this",
                new PointerDataType(VoidDataType.dataType,
                    currentProgram.getDataTypeManager()), currentProgram),
            new ParameterImpl("unusedVmSlot0", Undefined4DataType.dataType, currentProgram),
            new ParameterImpl("unusedVmSlot1", Undefined4DataType.dataType, currentProgram),
            new ParameterImpl("unusedVmSlot2", Undefined4DataType.dataType, currentProgram)
        };
        function.updateFunction(
            "__thiscall",
            new ReturnParameterImpl(VoidDataType.dataType, currentProgram),
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            false,
            SourceType.USER_DEFINED,
            parameters);
        function.setName(POST_NAME, SourceType.USER_DEFINED);
        function.setComment(POST_COMMENT);
        validatePost();
    }

    private void restorePre() throws Exception {
        Function function = getFunctionAt(toAddr(ENTRY));
        require(function != null, "UnsetObjective function is absent during PRE restore");
        function.setComment(null);
        boolean removed = currentProgram.getFunctionManager().removeFunction(toAddr(ENTRY));
        require(removed, "UnsetObjective function removal failed during PRE restore");
        Symbol lingering = currentProgram.getSymbolTable().getSymbol(
            POST_NAME, toAddr(ENTRY), currentProgram.getGlobalNamespace());
        require(lingering != null && lingering.delete(),
            "UnsetObjective label removal failed during PRE restore");
        validatePre();
    }

    private static File requireEvidence(
            File repositoryRoot, String relative, File supplied,
            long expectedBytes, String expectedSha256) throws Exception {
        File expected = new File(repositoryRoot, relative).getCanonicalFile();
        File actual = supplied.getCanonicalFile();
        requireEqual(relative, "canonical path", expected, actual);
        require(actual.isFile(), "evidence is absent: " + actual);
        byte[] bytes = Files.readAllBytes(actual.toPath());
        requireEqual(relative, "bytes", expectedBytes, (long) bytes.length);
        requireEqual(relative, "SHA-256", expectedSha256, sha256(bytes));
        return actual;
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        require(!output.exists(), label + " already exists: " + output);
        require(output.getParentFile() != null && output.getParentFile().isDirectory(),
            label + " parent is absent: " + output);
        return output;
    }

    private static void force(File file) throws Exception {
        try (FileChannel channel = FileChannel.open(file.toPath(), StandardOpenOption.WRITE)) {
            channel.force(true);
        }
    }

    private static File stage(File output, byte[] bytes) throws Exception {
        File partial = new File(output.getParentFile(),
            "." + output.getName() + ".partial-" + UUID.randomUUID());
        Files.write(partial.toPath(), bytes, StandardOpenOption.CREATE_NEW,
            StandardOpenOption.WRITE);
        force(partial);
        return partial;
    }

    private static void publishPair(
            File output, byte[] outputBytes, File ready, byte[] readyBytes) throws Exception {
        File stagedOutput = null;
        File stagedReady = null;
        boolean outputPublished = false;
        try {
            stagedOutput = stage(output, outputBytes);
            stagedReady = stage(ready, readyBytes);
            Files.createLink(output.toPath(), stagedOutput.toPath());
            Files.delete(stagedOutput.toPath());
            stagedOutput = null;
            outputPublished = true;
            Files.createLink(ready.toPath(), stagedReady.toPath());
            Files.delete(stagedReady.toPath());
            stagedReady = null;
        }
        catch (Exception error) {
            if (outputPublished && output.isFile() &&
                    sha256(Files.readAllBytes(output.toPath())).equals(sha256(outputBytes))) {
                Files.delete(output.toPath());
            }
            throw error;
        }
        finally {
            if (stagedOutput != null) Files.deleteIfExists(stagedOutput.toPath());
            if (stagedReady != null) Files.deleteIfExists(stagedReady.toPath());
        }
    }

    private byte[] buildOutput(String mode, String state) throws Exception {
        Function function = getFunctionAt(toAddr(ENTRY));
        String name = function == null ? "" : function.getName();
        String nameSource = function == null ? "" : function.getSymbol().getSource().toString();
        String sigSource = function == null ? "" : function.getSignatureSource().toString();
        String sig = function == null ? "" : signature(function);
        String comment = function == null ? "" : nullable(function.getComment());
        int params = function == null ? 0 : function.getParameterCount();
        int paramBytes = function == null ? 0 : function.getStackFrame().getParameterSize();
        StringBuilder output = new StringBuilder();
        output.append("address\tmode\tstate\tfunctionPresent\tname\tnameSource\t")
            .append("signatureSource\tsignature\tbodyBytes\tbodyRangeSha256\t")
            .append("bodySha256\tinstructionCount\tisThunk\tparameterCount\t")
            .append("stackParameterBytes\tcommentBytes\tcommentSha256\t")
            .append("functions\tinstructions\tprefixSha256\tsuffixSha256\n");
        output.append(ENTRY).append('\t').append(mode).append('\t').append(state).append('\t')
            .append(function != null).append('\t').append(name).append('\t')
            .append(nameSource).append('\t').append(sigSource).append('\t')
            .append(sig).append('\t').append(BODY_BYTES).append('\t')
            .append(BODY_RANGE_DIGEST).append('\t').append(BODY_SHA256).append('\t')
            .append(BODY_INSTRUCTIONS).append('\t')
            .append(function != null && function.isThunk()).append('\t')
            .append(params).append('\t').append(paramBytes).append('\t')
            .append(comment.getBytes(StandardCharsets.UTF_8).length).append('\t')
            .append(sha256(comment.getBytes(StandardCharsets.UTF_8))).append('\t')
            .append(functionCount()).append('\t').append(instructionCount()).append('\t')
            .append(PREFIX_SHA256).append('\t').append(SUFFIX_SHA256).append('\n');
        return output.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(
            String mode, String state, File tool, byte[] toolBytes,
            File campaign, File proof, File authority, File manifest,
            File output, byte[] outputBytes, boolean commitRequested,
            boolean nestedEndReturnedCommitted) throws Exception {
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schema\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"").append(Instant.now()).append("\",\n");
        ready.append("  \"mode\": \"").append(mode).append("\",\n");
        ready.append("  \"state\": \"").append(state).append("\",\n");
        ready.append("  \"tool\": {\"path\": \"").append(json(tool.getCanonicalPath()))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        ready.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"executableSha256\": \"").append(PROGRAM_SHA256)
            .append("\", \"memorySha256\": \"").append(MEMORY_SHA256).append("\"},\n");
        ready.append("  \"evidence\": {\n");
        appendStamp(ready, "campaign", campaign, CAMPAIGN_SHA256, true);
        appendStamp(ready, "proof", proof, PROOF_SHA256, true);
        appendStamp(ready, "authority", authority, AUTHORITY_SHA256, true);
        appendStamp(ready, "listingManifest", manifest, MANIFEST_SHA256, false);
        ready.append("  },\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"mutation\": {\"entry\": \"").append(ENTRY)
            .append("\", \"name\": \"").append(POST_NAME)
            .append("\", \"functionCreated\": ").append(state.equals("POST"))
            .append(", \"signatureAndCommentApplied\": ").append(state.equals("POST"))
            .append(", \"bytesChanged\": 0, \"instructionsChanged\": 0, ")
            .append("\"dataUnitsChanged\": 0, \"referencesChanged\": 0},\n");
        ready.append("  \"counts\": {\"functions\": ").append(functionCount())
            .append(", \"instructions\": ").append(instructionCount())
            .append(", \"bodyBytes\": ").append(BODY_BYTES)
            .append(", \"bodyInstructions\": ").append(BODY_INSTRUCTIONS)
            .append(", \"leadingNopBytes\": ").append(PREFIX_BYTES)
            .append(", \"trailingNopBytes\": ").append(SUFFIX_BYTES).append("},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"nestedEndReturnedCommitted\": ")
            .append(nestedEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback"))
            .append(",\n");
        ready.append("  \"authorityBoundary\": ")
            .append("\"requires_external_two_replica_and_separate_live_readback\",\n");
        ready.append("  \"limitations\": [\n")
            .append("    \"Only the scored boundary, shipped name, neutral ABI, and exact call shape are promoted.\",\n")
            .append("    \"No callee semantics or retail runtime behavior are promoted; the campaign contract refuter remains UNSCORED.\",\n")
            .append("    \"The three callee-cleaned VM stack slots and EAX return semantics remain unknown.\",\n")
            .append("    \"No executable bytes, instructions, data units, or references are changed.\",\n")
            .append("    \"The apply receipt precedes outer Ghidra save and is not live authority without fresh-process readback.\"\n")
            .append("  ]\n");
        ready.append("}\n");
        return ready.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static void appendStamp(
            StringBuilder ready, String label, File file,
            String expectedSha, boolean comma) throws Exception {
        byte[] bytes = Files.readAllBytes(file.toPath());
        requireEqual(label, "receipt SHA-256", expectedSha, sha256(bytes));
        ready.append("    \"").append(label).append("\": {\"path\": \"")
            .append(json(file.getCanonicalPath())).append("\", \"bytes\": ")
            .append(bytes.length).append(", \"sha256\": \"").append(expectedSha)
            .append("\"}").append(comma ? "," : "").append("\n");
    }

    private void validateOuter(long expectedId, String phase) {
        TransactionInfo info = currentProgram.getCurrentTransactionInfo();
        require(info != null, phase + " outer transaction is absent");
        requireEqual("transaction", phase + " id", expectedId, info.getID());
        requireEqual("transaction", phase + " status",
            TransactionInfo.Status.NOT_DONE, info.getStatus());
        requireEqual("transaction", phase + " terminated", false,
            currentProgram.hasTerminatedTransaction());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 7) {
            throw new IllegalArgumentException(
                "usage: <campaign.ready.json> <proof.ready.json> " +
                "<authority.ready.json> <instructions.tsv> <out.tsv> " +
                "<out.ready.json> <dry|probe-after-create|probe-post-inner|apply|readback>");
        }
        String mode = args[6].toLowerCase(Locale.ROOT);
        require(Arrays.asList(
            "dry", "probe-after-create", "probe-post-inner", "apply", "readback")
            .contains(mode), "unsupported mode: " + mode);

        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        requireEqual("tool", "directory", "tools", tool.getParentFile().getName());
        File repositoryRoot = tool.getParentFile().getParentFile().getCanonicalFile();
        File campaign = requireEvidence(repositoryRoot, CAMPAIGN_RELATIVE,
            new File(args[0]), CAMPAIGN_BYTES, CAMPAIGN_SHA256);
        File proof = requireEvidence(repositoryRoot, PROOF_RELATIVE,
            new File(args[1]), PROOF_BYTES, PROOF_SHA256);
        File authority = requireEvidence(repositoryRoot, AUTHORITY_RELATIVE,
            new File(args[2]), AUTHORITY_BYTES, AUTHORITY_SHA256);
        File manifest = requireEvidence(repositoryRoot, MANIFEST_RELATIVE,
            new File(args[3]), MANIFEST_BYTES, MANIFEST_SHA256);
        File output = requireNewOutput(args[4], "output TSV");
        File ready = requireNewOutput(args[5], "READY receipt");
        requireEqual("output", "distinct paths", false, output.equals(ready));
        requireEqual("output", "shared parent", output.getParentFile(), ready.getParentFile());

        if (mode.equals("readback")) {
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes,
                campaign, proof, authority, manifest, output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("MISSION_UNSETOBJECTIVE_READBACK_COMPLETE entry=" + ENTRY +
                " function_count=" + POST_FUNCTION_COUNT + " loaded_state_verified=true");
            return;
        }

        validatePre();
        println("MISSION_UNSETOBJECTIVE_PREFLIGHT_OK entry=" + ENTRY +
            " body_bytes=" + BODY_BYTES + " instructions=" + BODY_INSTRUCTIONS +
            " tool_sha256=" + sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            byte[] readyBytes = buildReady(mode, "PRE", tool, toolBytes,
                campaign, proof, authority, manifest, output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("MISSION_UNSETOBJECTIVE_DRY_COMPLETE entry=" + ENTRY + " mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires a healthy outer Ghidra transaction");
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction(
            "Create and annotate Mission native UnsetObjective");
        boolean transactionEnded = false;
        boolean commitRequested = false;
        boolean nestedCommitted = false;
        try {
            if (mode.equals("probe-after-create")) {
                createNaturalFunction();
                validateProgram(POST_FUNCTION_COUNT);
                println("MISSION_UNSETOBJECTIVE_FORCED_AFTER_CREATE_FAILURE rollback_required=true");
                throw new IllegalStateException(
                    "intentional Mission UnsetObjective after-create rollback probe");
            }
            applyPost();
            commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            transactionEnded = true;
            requireEqual("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");

            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore Mission native UnsetObjective PRE state after post-inner probe");
                boolean restoreEnded = false;
                try {
                    restorePre();
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    requireEqual("transaction", "restore nested end committed",
                        false, restoreCommitted);
                }
                finally {
                    if (!restoreEnded) {
                        currentProgram.endTransaction(restore, false);
                    }
                }
                validatePre();
                validateOuter(outerId, "after compensating PRE restore");
                println("MISSION_UNSETOBJECTIVE_COMPENSATING_PRE_RESTORE_COMPLETE entry=" + ENTRY);
                println("MISSION_UNSETOBJECTIVE_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException(
                    "intentional Mission UnsetObjective post-inner rollback probe");
            }

            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes,
                campaign, proof, authority, manifest, output, outputBytes,
                true, nestedCommitted);
            publishPair(output, outputBytes, ready, readyBytes);
            println("MISSION_UNSETOBJECTIVE_APPLY_COMPLETE entry=" + ENTRY +
                " function_count=" + POST_FUNCTION_COUNT +
                " reopen_verification_required=true");
        }
        catch (Exception error) {
            if (!transactionEnded) {
                try {
                    nestedCommitted = currentProgram.endTransaction(transaction, false);
                    transactionEnded = true;
                }
                catch (Exception rollbackError) {
                    error.addSuppressed(rollbackError);
                }
            }
            println("MISSION_UNSETOBJECTIVE_MUTATION_TAINTED mode=" + mode +
                " nested_committed=" + nestedCommitted +
                " outer_rollback_required=" + !mode.equals("probe-post-inner") +
                " recovery=" + (mode.equals("probe-post-inner") ?
                    "COMPENSATING_PRE_RESTORE_VERIFIED" : "RESTORE_VERIFIED_SCRATCH_BASE"));
            throw error;
        }
    }
}
