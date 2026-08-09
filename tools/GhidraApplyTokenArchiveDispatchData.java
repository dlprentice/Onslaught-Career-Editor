//@category Data

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.CommentType;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolTable;

import java.io.File;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.UUID;

/**
 * Preserve the exact pre-existing Generation 14 CTokenArchive::ReadNextToken
 * dispatch data units and add bounded structural labels/comments.
 *
 * This is not a generic data-carving script. It is bound to the pristine
 * specimen, exact Generation 14 campaign, exact static proof, exact external
 * authority selector, and exact current Ghidra PRE program shape.
 *
 * Modes:
 *   dry              validate PRE and publish no mutation;
 *   probe-after-one  define the pointer table, then force rollback;
 *   probe-post-inner define all POST metadata, restore PRE, then force failure;
 *   apply            define both arrays and structural metadata;
 *   readback         require exact POST without mutation.
 */
public class GhidraApplyTokenArchiveDispatchData extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.tokenarchive-dispatch-structure.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final long FUNCTION_COUNT = 8124;
    private static final long INSTRUCTION_COUNT = 549872;

    private static final String CAMPAIGN_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-14-tokenarchive-dispatch-reproof-v1/campaign.ready.json";
    private static final long CAMPAIGN_BYTES = 16930;
    private static final String CAMPAIGN_SHA256 =
        "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b";
    private static final String PROOF_RELATIVE =
        "local-lab/tokenarchive-dispatch-table-reproof-20260809-v1/proof.ready.json";
    private static final long PROOF_BYTES = 11257;
    private static final String PROOF_SHA256 =
        "182d302e45ff42b389b54c85f92576864f9ef9dc30887ee5fc6db86b307faf7f";
    private static final String AUTHORITY_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-14-tokenarchive-dispatch-reproof-authority.ready.json";
    private static final long AUTHORITY_BYTES = 8215;
    private static final String AUTHORITY_SHA256 =
        "83a5544bdde805762b01983171c336826ea62a8b2dd8be94109bef959560ff72";

    private static final String PREVIOUS_FUNCTION_ADDRESS = "0x004f57b0";
    private static final String PREVIOUS_FUNCTION_NAME = "CTokenArchive__ReadNextToken";
    private static final long PREVIOUS_FUNCTION_BYTES = 789;
    private static final String PREVIOUS_FUNCTION_MAX = "004f5ac4";
    private static final String NEXT_FUNCTION_ADDRESS = "0x004f5b70";
    private static final String NEXT_FUNCTION_NAME = "CTokenArchive__BindIndexedFieldPointer";

    private static final String PREFIX_ADDRESS = "0x004f5ac5";
    private static final String POINTER_ADDRESS = "0x004f5ac8";
    private static final String INDEX_ADDRESS = "0x004f5ae4";
    private static final String SUFFIX_ADDRESS = "0x004f5b61";
    private static final String END_ADDRESS = "0x004f5b70";
    private static final String CONSUMER_ADDRESS = "0x004f583b";
    private static final String WHOLE_SHA256 =
        "9b55806e7ca788cf70b9008ff81c64d034980f927690ecd33881a1c9cbad5510";
    private static final String PREFIX_SHA256 =
        "53e090edb4fca0626d458dbefa0ae1bcbffc511ed159f1a70641610ad0d9a200";
    private static final String POINTER_SHA256 =
        "d9bf96faa2cffa25a941f51f63255b8b6ee947dabf5792c405241eb78b4c3e2f";
    private static final String INDEX_SHA256 =
        "26d7739dc4645ebf70177e7023862e1a57cf5e421e6cf6a60100f2f5d97c0d27";
    private static final String SUFFIX_SHA256 =
        "40f0d021fa824f3b40dc646f67479997734d273d9121690b6f042c512df3a838";
    private static final String CONSUMER_SHA256 =
        "0b326a88f87630cc23d08ad9e4538d06275c6ee4a25b1f823ec218d2cc05f9ca";
    private static final long[] POINTER_TARGETS = {
        0x004f5abbL, 0x004f587eL, 0x004f588fL, 0x004f5854L,
        0x004f58aeL, 0x004f59b7L, 0x004f5904L
    };
    private static final int[] INDEX_COUNTS = {1, 2, 19, 47, 3, 37, 16};

    private static final String PREFIX_LABEL =
        "CTokenArchive__ReadNextToken_DispatchAlignPrefix";
    private static final String POINTER_LABEL =
        "CTokenArchive__ReadNextToken_DispatchTargets";
    private static final String INDEX_LABEL =
        "CTokenArchive__ReadNextToken_TokenKindByIndex";
    private static final String SUFFIX_LABEL =
        "CTokenArchive__ReadNextToken_DispatchAlignSuffix";

    private static final String PREFIX_COMMENT =
        "Three-byte x86 alignment NOP between CTokenArchive::ReadNextToken and its " +
        "consumer-bound dispatch data. Not code and not a function. Gen14 READY " +
        "9864424def44; proof 182d302e45ff.";
    private static final String POINTER_COMMENT =
        "Seven-entry pointer dispatch table consumed at 0x004F584D after the index " +
        "byte is zero-extended into ECX. Exact targets: 004F5ABB, 004F587E, " +
        "004F588F, 004F5854, 004F58AE, 004F59B7, 004F5904. Category meanings " +
        "remain unassigned. Gen14 READY 9864424def44; proof 182d302e45ff.";
    private static final String INDEX_COMMENT =
        "125-byte token-index-to-dispatch-category table consumed at 0x004F5847. " +
        "Values are bounded 0..6; counts are 1,2,19,47,3,37,16. This proves static " +
        "dispatch structure, not runtime frequencies or semantic category names. " +
        "Gen14 READY 9864424def44; proof 182d302e45ff.";
    private static final String SUFFIX_COMMENT =
        "Fifteen 0x90 alignment bytes before CTokenArchive::BindIndexedFieldPointer. " +
        "Not code and not a function. Gen14 READY 9864424def44; proof 182d302e45ff.";
    private static final String CONSUMER_COMMENT =
        "Gen14-proved dispatch consumer: INC EAX; reject index >0x7C; XOR ECX; " +
        "load one category byte from 0x004F5AE4; indirect-jump through the seven " +
        "pointers at 0x004F5AC8. Exact released structure only; token-category " +
        "semantics and runtime frequencies remain open. Proof 182d302e45ff.";

    private static class PreState {
        final Map<String, String> comments = new HashMap<>();
        final Map<String, Symbol> primarySymbols = new HashMap<>();
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

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static String json(String value) {
        return nullable(value).replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t");
    }

    private static void requireEqual(String owner, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(
                owner + " " + field + " differs: expected=" + expected + " actual=" + actual);
        }
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

    private void validateProgram() throws Exception {
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
        requireEqual("program", "function count", FUNCTION_COUNT, functionCount());
        requireEqual("program", "instruction count", INSTRUCTION_COUNT, instructionCount());
        requireEqual("program", "pointer size", 4, currentProgram.getDefaultPointerSize());
    }

    private byte[] bytes(String start, String endExclusive) throws Exception {
        Address first = toAddr(start);
        Address end = toAddr(endExclusive);
        int length = (int) end.subtract(first);
        byte[] result = new byte[length];
        requireEqual(start, "memory read", length,
            currentProgram.getMemory().getBytes(first, result));
        return result;
    }

    private void validateBytes() throws Exception {
        requireEqual("dispatch", "whole SHA-256", WHOLE_SHA256,
            sha256(bytes(PREFIX_ADDRESS, END_ADDRESS)));
        requireEqual("dispatch", "prefix SHA-256", PREFIX_SHA256,
            sha256(bytes(PREFIX_ADDRESS, POINTER_ADDRESS)));
        requireEqual("dispatch", "pointer SHA-256", POINTER_SHA256,
            sha256(bytes(POINTER_ADDRESS, INDEX_ADDRESS)));
        requireEqual("dispatch", "index SHA-256", INDEX_SHA256,
            sha256(bytes(INDEX_ADDRESS, SUFFIX_ADDRESS)));
        requireEqual("dispatch", "suffix SHA-256", SUFFIX_SHA256,
            sha256(bytes(SUFFIX_ADDRESS, END_ADDRESS)));
        requireEqual("dispatch", "consumer SHA-256", CONSUMER_SHA256,
            sha256(bytes(CONSUMER_ADDRESS, "0x004f5854")));
        requireEqual("prefix", "three-byte alignment encoding", "8d4900",
            hex(bytes(PREFIX_ADDRESS, POINTER_ADDRESS)));
        for (byte value : bytes(SUFFIX_ADDRESS, END_ADDRESS)) {
            requireEqual("suffix", "NOP byte", 0x90, value & 0xff);
        }
        ByteBuffer pointers = ByteBuffer.wrap(bytes(POINTER_ADDRESS, INDEX_ADDRESS))
            .order(ByteOrder.LITTLE_ENDIAN);
        for (int index = 0; index < POINTER_TARGETS.length; index++) {
            requireEqual("pointer", "target " + index, POINTER_TARGETS[index],
                Integer.toUnsignedLong(pointers.getInt()));
        }
        int[] counts = new int[7];
        for (byte value : bytes(INDEX_ADDRESS, SUFFIX_ADDRESS)) {
            int category = value & 0xff;
            if (category > 6) {
                throw new IllegalStateException("index category exceeds six: " + category);
            }
            counts[category]++;
        }
        requireEqual("index", "category counts", Arrays.toString(INDEX_COUNTS),
            Arrays.toString(counts));
    }

    private void validateFunctionBoundaries() {
        Function previous = getFunctionAt(toAddr(PREVIOUS_FUNCTION_ADDRESS));
        Function next = getFunctionAt(toAddr(NEXT_FUNCTION_ADDRESS));
        requireEqual("previous function", "name", PREVIOUS_FUNCTION_NAME, previous.getName());
        requireEqual("previous function", "body bytes", PREVIOUS_FUNCTION_BYTES,
            previous.getBody().getNumAddresses());
        requireEqual("previous function", "body max", PREVIOUS_FUNCTION_MAX,
            previous.getBody().getMaxAddress().toString());
        requireEqual("next function", "name", NEXT_FUNCTION_NAME, next.getName());
        if (getFunctionContaining(toAddr(POINTER_ADDRESS)) != null ||
                getFunctionContaining(toAddr(INDEX_ADDRESS)) != null) {
            throw new IllegalStateException("dispatch data overlaps a function");
        }
        Listing listing = currentProgram.getListing();
        Address cursor = toAddr(PREFIX_ADDRESS);
        Address end = toAddr(END_ADDRESS);
        while (cursor.compareTo(end) < 0) {
            if (listing.getInstructionContaining(cursor) != null) {
                throw new IllegalStateException("dispatch partition contains an instruction at " + cursor);
            }
            cursor = cursor.next();
        }
    }

    private static File requireEvidence(
            File repositoryRoot, String relative, File supplied,
            long expectedBytes, String expectedSha256) throws Exception {
        File canonical = supplied.getCanonicalFile();
        File expected = new File(repositoryRoot, relative).getCanonicalFile();
        requireEqual(relative, "canonical evidence path", expected, canonical);
        if (!canonical.isFile()) {
            throw new IllegalArgumentException("evidence is absent: " + canonical);
        }
        byte[] bytes = Files.readAllBytes(canonical.toPath());
        requireEqual(relative, "evidence bytes", expectedBytes, (long) bytes.length);
        requireEqual(relative, "evidence SHA-256", expectedSha256, sha256(bytes));
        return canonical;
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        if (output.exists()) {
            throw new IllegalArgumentException(label + " already exists: " + output);
        }
        if (output.getParentFile() == null || !output.getParentFile().isDirectory()) {
            throw new IllegalArgumentException(label + " parent is absent: " + output);
        }
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
            Files.move(stagedOutput.toPath(), output.toPath(), StandardCopyOption.ATOMIC_MOVE);
            stagedOutput = null;
            outputPublished = true;
            Files.move(stagedReady.toPath(), ready.toPath(), StandardCopyOption.ATOMIC_MOVE);
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

    private String comment(String address) {
        return currentProgram.getListing().getComment(CommentType.PLATE, toAddr(address));
    }

    private Symbol primary(String address) {
        return currentProgram.getSymbolTable().getPrimarySymbol(toAddr(address));
    }

    private void requireNoProposedLabels() {
        SymbolTable table = currentProgram.getSymbolTable();
        for (String name : Arrays.asList(PREFIX_LABEL, POINTER_LABEL, INDEX_LABEL, SUFFIX_LABEL)) {
            SymbolIterator symbols = table.getSymbols(name);
            if (symbols.hasNext()) {
                throw new IllegalStateException("proposed label already exists: " + name);
            }
        }
    }

    private PreState capturePre() throws Exception {
        validateProgram();
        validateBytes();
        validateFunctionBoundaries();
        validateExistingDataUnits();
        requireNoProposedLabels();
        PreState state = new PreState();
        for (String address : Arrays.asList(
                PREFIX_ADDRESS, POINTER_ADDRESS, INDEX_ADDRESS,
                SUFFIX_ADDRESS, CONSUMER_ADDRESS)) {
            state.comments.put(address, comment(address));
            state.primarySymbols.put(address, primary(address));
            requireEqual(address, "PRE plate comment", null, comment(address));
        }
        return state;
    }

    private static String dataSummary(Data data) {
        if (data == null) {
            return "<none>";
        }
        return data.getDataType().getPathName() + "/length=" + data.getLength() +
            "/components=" + data.getNumComponents();
    }

    private String definedDataSummary() {
        StringBuilder result = new StringBuilder();
        DataIterator iterator = currentProgram.getListing().getDefinedData(
            new AddressSet(toAddr(POINTER_ADDRESS), toAddr(SUFFIX_ADDRESS).previous()), true);
        int count = 0;
        while (iterator.hasNext()) {
            Data data = iterator.next();
            if (count > 0) result.append(',');
            result.append(data.getAddress()).append(':').append(dataSummary(data));
            count++;
        }
        return "count=" + count + "[" + result + "]";
    }

    private void validateExistingDataUnits() {
        DataIterator iterator = currentProgram.getListing().getDefinedData(
            new AddressSet(toAddr(POINTER_ADDRESS), toAddr(SUFFIX_ADDRESS).previous()), true);
        int ordinal = 0;
        while (iterator.hasNext()) {
            Data data = iterator.next();
            Address expectedAddress;
            String expectedType;
            int expectedLength;
            if (ordinal < 7) {
                expectedAddress = toAddr(POINTER_ADDRESS).add(ordinal * 4L);
                expectedType = "/pointer";
                expectedLength = 4;
            }
            else {
                expectedAddress = toAddr(INDEX_ADDRESS).add(ordinal - 7L);
                expectedType = "/byte";
                expectedLength = 1;
            }
            requireEqual("defined data " + ordinal, "address", expectedAddress, data.getAddress());
            requireEqual("defined data " + ordinal, "type", expectedType,
                data.getDataType().getPathName());
            requireEqual("defined data " + ordinal, "length", expectedLength, data.getLength());
            requireEqual("defined data " + ordinal, "components", 0, data.getNumComponents());
            ordinal++;
        }
        requireEqual("dispatch", "defined data unit count", 132, ordinal);
    }

    private Symbol addLabel(String address, String name) throws Exception {
        Symbol symbol = currentProgram.getSymbolTable().createLabel(
            toAddr(address), name, SourceType.USER_DEFINED);
        symbol.setPrimary();
        requireEqual(address, "primary label", name, primary(address).getName());
        requireEqual(address, "label source", SourceType.USER_DEFINED, primary(address).getSource());
        return symbol;
    }

    private void applyPointerPhase() throws Exception {
        Listing listing = currentProgram.getListing();
        addLabel(PREFIX_ADDRESS, PREFIX_LABEL);
        addLabel(POINTER_ADDRESS, POINTER_LABEL);
        listing.setComment(toAddr(PREFIX_ADDRESS), CommentType.PLATE, PREFIX_COMMENT);
        listing.setComment(toAddr(POINTER_ADDRESS), CommentType.PLATE, POINTER_COMMENT);
    }

    private void applyRemainingPhase() throws Exception {
        Listing listing = currentProgram.getListing();
        addLabel(INDEX_ADDRESS, INDEX_LABEL);
        addLabel(SUFFIX_ADDRESS, SUFFIX_LABEL);
        listing.setComment(toAddr(INDEX_ADDRESS), CommentType.PLATE, INDEX_COMMENT);
        listing.setComment(toAddr(SUFFIX_ADDRESS), CommentType.PLATE, SUFFIX_COMMENT);
        listing.setComment(toAddr(CONSUMER_ADDRESS), CommentType.PLATE, CONSUMER_COMMENT);
    }

    private void requireLabel(String address, String name) {
        Symbol symbol = primary(address);
        requireEqual(address, "primary label", name, symbol == null ? null : symbol.getName());
        requireEqual(address, "label source", SourceType.USER_DEFINED,
            symbol == null ? null : symbol.getSource());
    }

    private void validatePost() throws Exception {
        validateProgram();
        validateBytes();
        validateFunctionBoundaries();
        validateExistingDataUnits();
        requireLabel(PREFIX_ADDRESS, PREFIX_LABEL);
        requireLabel(POINTER_ADDRESS, POINTER_LABEL);
        requireLabel(INDEX_ADDRESS, INDEX_LABEL);
        requireLabel(SUFFIX_ADDRESS, SUFFIX_LABEL);
        requireEqual(PREFIX_ADDRESS, "plate comment", PREFIX_COMMENT, comment(PREFIX_ADDRESS));
        requireEqual(POINTER_ADDRESS, "plate comment", POINTER_COMMENT, comment(POINTER_ADDRESS));
        requireEqual(INDEX_ADDRESS, "plate comment", INDEX_COMMENT, comment(INDEX_ADDRESS));
        requireEqual(SUFFIX_ADDRESS, "plate comment", SUFFIX_COMMENT, comment(SUFFIX_ADDRESS));
        requireEqual(CONSUMER_ADDRESS, "plate comment", CONSUMER_COMMENT, comment(CONSUMER_ADDRESS));
    }

    private void deleteLabel(String address, String name, Symbol original) {
        SymbolTable table = currentProgram.getSymbolTable();
        Symbol created = table.getSymbol(name, toAddr(address), currentProgram.getGlobalNamespace());
        if (created == null || !created.delete()) {
            throw new IllegalStateException("failed to delete created label: " + name);
        }
        if (original != null) {
            original.setPrimary();
        }
    }

    private void restorePre(PreState state) throws Exception {
        Listing listing = currentProgram.getListing();
        deleteLabel(PREFIX_ADDRESS, PREFIX_LABEL, state.primarySymbols.get(PREFIX_ADDRESS));
        deleteLabel(POINTER_ADDRESS, POINTER_LABEL, state.primarySymbols.get(POINTER_ADDRESS));
        deleteLabel(INDEX_ADDRESS, INDEX_LABEL, state.primarySymbols.get(INDEX_ADDRESS));
        deleteLabel(SUFFIX_ADDRESS, SUFFIX_LABEL, state.primarySymbols.get(SUFFIX_ADDRESS));
        for (String address : state.comments.keySet()) {
            listing.setComment(toAddr(address), CommentType.PLATE, state.comments.get(address));
        }
        capturePre();
    }

    private byte[] buildOutput(String mode, String state) throws Exception {
        StringBuilder output = new StringBuilder();
        output.append("address\trole\tmode\tstate\tprimarySymbol\tsymbolSource\t")
            .append("dataLength\tcomponents\tbytesSha256\tcommentBytes\tcommentSha256\n");
        String[][] rows = {
            {PREFIX_ADDRESS, "ALIGN_PREFIX", PREFIX_LABEL, POINTER_ADDRESS},
            {POINTER_ADDRESS, "DISPATCH_POINTERS", POINTER_LABEL, INDEX_ADDRESS},
            {INDEX_ADDRESS, "TOKEN_KIND_INDEX", INDEX_LABEL, SUFFIX_ADDRESS},
            {SUFFIX_ADDRESS, "ALIGN_SUFFIX", SUFFIX_LABEL, END_ADDRESS},
            {CONSUMER_ADDRESS, "DISPATCH_CONSUMER", "", "0x004f5854"},
        };
        Listing listing = currentProgram.getListing();
        for (String[] row : rows) {
            Symbol symbol = primary(row[0]);
            Data data = listing.getDefinedDataAt(toAddr(row[0]));
            String plate = nullable(comment(row[0]));
            output.append(row[0]).append('\t').append(row[1]).append('\t')
                .append(mode).append('\t').append(state).append('\t')
                .append(symbol == null ? "" : symbol.getName()).append('\t')
                .append(symbol == null ? "" : symbol.getSource()).append('\t')
                .append(data == null ? 0 : data.getLength()).append('\t')
                .append(data == null ? 0 : data.getNumComponents()).append('\t')
                .append(sha256(bytes(row[0], row[3]))).append('\t')
                .append(plate.getBytes(StandardCharsets.UTF_8).length).append('\t')
                .append(sha256(plate.getBytes(StandardCharsets.UTF_8))).append('\n');
        }
        return output.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(
            String mode, String state, byte[] toolBytes, String toolPath,
            File output, byte[] outputBytes, boolean commitRequested,
            boolean nestedEndReturnedCommitted) throws Exception {
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schema\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"").append(json(Instant.now().toString()))
            .append("\",\n");
        ready.append("  \"mode\": \"").append(mode).append("\",\n");
        ready.append("  \"state\": \"").append(state).append("\",\n");
        ready.append("  \"tool\": {\"path\": \"").append(json(toolPath))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        ready.append("  \"campaignReadySha256\": \"").append(CAMPAIGN_SHA256).append("\",\n");
        ready.append("  \"proofReadySha256\": \"").append(PROOF_SHA256).append("\",\n");
        ready.append("  \"authorityReadySha256\": \"").append(AUTHORITY_SHA256).append("\",\n");
        ready.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"md5\": \"").append(PROGRAM_MD5)
            .append("\", \"sha256\": \"").append(PROGRAM_SHA256)
            .append("\", \"functions\": ").append(FUNCTION_COUNT)
            .append(", \"instructions\": ").append(INSTRUCTION_COUNT).append("},\n");
        ready.append("  \"partition\": {\"wholeBytes\": 171, \"dataBytes\": 153, ")
            .append("\"alignmentBytes\": 18, \"pointerTargets\": 7, ")
            .append("\"indexBytes\": 125, \"indexMax\": 6, ")
            .append("\"preExistingDefinedDataUnitsPreserved\": 132},\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"nestedEndReturnedCommitted\": ")
            .append(nestedEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback"))
            .append(",\n");
        ready.append("  \"semanticTokenKindsAuthorized\": false,\n");
        ready.append("  \"functionOrBoundaryMutationAuthorized\": false,\n");
        ready.append("  \"authorityBoundary\": ")
            .append("\"requires_external_two_replica_or_separate_live_readback\"\n");
        ready.append("}\n");
        return ready.toString().getBytes(StandardCharsets.UTF_8);
    }

    private void validateOuter(long expectedId, String phase) {
        TransactionInfo info = currentProgram.getCurrentTransactionInfo();
        if (info == null) {
            throw new IllegalStateException(phase + " outer transaction is absent");
        }
        requireEqual("transaction", phase + " id", expectedId, info.getID());
        requireEqual("transaction", phase + " status",
            TransactionInfo.Status.NOT_DONE, info.getStatus());
        requireEqual("transaction", phase + " terminated", false,
            currentProgram.hasTerminatedTransaction());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 6) {
            throw new IllegalArgumentException(
                "usage: <campaign.ready.json> <proof.ready.json> <authority.ready.json> " +
                "<out.tsv> <out.ready.json> <dry|probe-after-one|probe-post-inner|apply|readback>");
        }
        String mode = args[5].toLowerCase(Locale.ROOT);
        if (!Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
                .contains(mode)) {
            throw new IllegalArgumentException("unsupported mode: " + mode);
        }

        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File toolFile = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        requireEqual("tool", "directory", "tools", toolFile.getParentFile().getName());
        File repositoryRoot = toolFile.getParentFile().getParentFile().getCanonicalFile();
        requireEvidence(repositoryRoot, CAMPAIGN_RELATIVE, new File(args[0]),
            CAMPAIGN_BYTES, CAMPAIGN_SHA256);
        requireEvidence(repositoryRoot, PROOF_RELATIVE, new File(args[1]),
            PROOF_BYTES, PROOF_SHA256);
        requireEvidence(repositoryRoot, AUTHORITY_RELATIVE, new File(args[2]),
            AUTHORITY_BYTES, AUTHORITY_SHA256);
        File output = requireNewOutput(args[3], "output TSV");
        File ready = requireNewOutput(args[4], "READY receipt");
        requireEqual("output", "distinct paths", false, output.equals(ready));
        requireEqual("output", "shared parent", output.getParentFile(), ready.getParentFile());

        if (mode.equals("readback")) {
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", toolBytes,
                toolFile.getCanonicalPath(), output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("TOKENARCHIVE_DISPATCH_READBACK_COMPLETE data_units=132 labels=4");
            return;
        }

        PreState pre = capturePre();
        println("TOKENARCHIVE_DISPATCH_PREFLIGHT_OK data_units=132 labels=4 tool_sha256=" +
            sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            byte[] readyBytes = buildReady(mode, "PRE", toolBytes,
                toolFile.getCanonicalPath(), output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("TOKENARCHIVE_DISPATCH_DRY_COMPLETE mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        if (outer == null || currentProgram.hasTerminatedTransaction()) {
            throw new IllegalStateException("mutation requires a healthy outer Ghidra transaction");
        }
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction("TokenArchive dispatch data");
        boolean transactionEnded = false;
        boolean nestedCommitted = false;
        try {
            applyPointerPhase();
            if (mode.equals("probe-after-one")) {
                println("TOKENARCHIVE_DISPATCH_FORCED_AFTER_ONE_FAILURE rollback_required=true");
                throw new IllegalStateException(
                    "intentional TokenArchive dispatch after-one rollback probe");
            }
            applyRemainingPhase();
            boolean commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            transactionEnded = true;
            requireEqual("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");
            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore TokenArchive dispatch PRE after post-inner probe");
                boolean restoreEnded = false;
                try {
                    restorePre(pre);
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    requireEqual("transaction", "restore nested end committed", false, restoreCommitted);
                }
                finally {
                    if (!restoreEnded) currentProgram.endTransaction(restore, false);
                }
                validateOuter(outerId, "after compensating PRE restore");
                println("TOKENARCHIVE_DISPATCH_COMPENSATING_PRE_RESTORE_COMPLETE");
                println("TOKENARCHIVE_DISPATCH_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException(
                    "intentional TokenArchive dispatch post-inner rollback probe");
            }
            if (!mode.equals("apply")) {
                throw new IllegalStateException("unexpected mutation success mode");
            }
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", toolBytes,
                toolFile.getCanonicalPath(), output, outputBytes, true, nestedCommitted);
            publishPair(output, outputBytes, ready, readyBytes);
            println("TOKENARCHIVE_DISPATCH_APPLY_COMPLETE data_units=132 labels=4 " +
                "reopen_verification_required=true");
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
            println("TOKENARCHIVE_DISPATCH_MUTATION_TAINTED mode=" + mode +
                " nested_committed=" + nestedCommitted +
                " outer_rollback_required=" + !mode.equals("probe-post-inner") +
                " recovery=" + (mode.equals("probe-post-inner") ?
                    "COMPENSATING_PRE_RESTORE_VERIFIED" : "RESTORE_VERIFIED_SCRATCH_BASE"));
            throw error;
        }
    }
}
