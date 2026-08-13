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
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolType;

import java.io.File;
import java.io.InputStream;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * Apply only the proof-bound 0x0050ff10 explosion-factory metadata repair.
 *
 * Modes:
 *   dry              require exact PRE, publish a PRE receipt, mutate nothing;
 *   probe-after-one  rename the function, then force nested rollback;
 *   probe-post-inner apply all fields, end the nested transaction, compensate
 *                    back to PRE in a second transaction, then force failure;
 *   apply            apply the complete one-row POST;
 *   readback         require exact persistent POST without mutation.
 */
public class GhidraApplyCExplosionFactoryIdentity extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.cexplosion-factory-identity.v1";
    private static final String ENTRY = "0x0050ff10";
    private static final String PRE_NAME = "CWorldPhysicsManager__CreatePickup";
    private static final String POST_NAME = "CWorldPhysicsManager__CreateExplosion";
    private static final String PRE_PARAMETER = "pickup_type";
    private static final String POST_PARAMETER = "explosion_definition_index";
    private static final String PRE_SIGNATURE =
        "void * __cdecl CWorldPhysicsManager__CreatePickup(int pickup_type)";
    private static final String POST_SIGNATURE =
        "void * __cdecl CWorldPhysicsManager__CreateExplosion(int explosion_definition_index)";
    private static final String BODY_RANGE = "0x0050ff10-0x0050ffa7";
    private static final long BODY_BYTES = 152;
    private static final String BODY_RANGE_SHA256 =
        "c8ccd2348be7a47f2d032bdd5f3b15716f327ce90683a437caafc7b0d57bd3df";
    private static final String BODY_BYTES_SHA256 =
        "24f43aa5cdf6fff0d9d8ec700ec2de8fb221acc3fc49af3f3738e5b596160e5b";
    private static final long BODY_INSTRUCTIONS = 39;
    private static final long PRE_COMMENT_BYTES = 512;
    private static final String PRE_COMMENT_SHA256 =
        "8d6cd69dd6ccdf0bbddcfe5db0cefe85bd7387c9576ac6d4f05912ac73a716b4";
    private static final long POST_COMMENT_BYTES = 915;
    private static final String POST_COMMENT_SHA256 =
        "f512ec67c3b7851821c57906c16b08be05c45d3b525de08ebc27c244dabfc5a8";

    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final long FUNCTION_COUNT = 8170;
    private static final long INSTRUCTION_COUNT = 549872;

    private static final String TOOL_RELATIVE =
        "tools/GhidraApplyCExplosionFactoryIdentity.java";
    private static final String OWNER_RELATIVE =
        "reverse-engineering/binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.md";
    private static final long OWNER_BYTES = 6950;
    private static final String OWNER_SHA256 =
        "059e2a9a1a18b6fcf301238764e9cedc75e69fc057e7d16cb40c5f3fe0f57e31";
    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.tsv";
    private static final long MANIFEST_BYTES = 1474;
    private static final String MANIFEST_SHA256 =
        "4eb65da2e50c31dc6151c270808c2bdf83b2cea0b70f1a3ab60173ec55fbc1e8";
    private static final String REPROOF_RELATIVE =
        "local-lab/ghidra-cexplosion-identity-scratch-20260813-v7/reproof-v7/reproof.ready.json";
    private static final long REPROOF_BYTES = 4241;
    private static final String REPROOF_SHA256 =
        "fe1bfd62f94694a27c80383647f65952c0a9fbc0b85385a43c4543c20fe3db89";

    private static final String POST_COMMENT =
        "Identity correction (2026-08-13): pristine retail body " +
        "0x0050FF10..0x0050FFA7 rejects when the heap metric is below 0x32000 or " +
        "explosion_definition_index is negative, allocates 0x94 bytes through " +
        "CDXMemoryManager::Alloc, calls CComplexThing__ctor_base, clears +0x90, " +
        "installs strict CExplosion vtables 0x005E4454 and 0x005E43DC, and returns " +
        "null on rejected or allocation-null paths. All 24 pristine direct call " +
        "sites push one factory argument and caller-clean it; two CRound paths feed " +
        "the immediately returned ordinal from resolver 0x004DAA20. The separately " +
        "pinned caller-family join classifies all 24 as explosion paths. " +
        "High-confidence C1 static implementation identity and bounded cdecl " +
        "signature only; the parameter name is descriptive. Exact original source " +
        "spelling/type, runtime reachability/effects, failure frequency, full layout, " +
        "and rebuild parity remain open. CExplosion factory reproof fe1bfd62f946.";

    private static final List<String> PRE_TAGS = sorted(Arrays.asList(
        "comment-hardened", "factory", "pickup", "retail-binary-evidence",
        "signature-corrected", "signature-recovered", "static-reaudit",
        "world-physics-manager", "worldphysics-factory-tail-wave558"));
    private static final List<String> POST_TAGS = sorted(Arrays.asList(
        "comment-hardened", "explosion", "factory", "identity-corrected",
        "retail-binary-evidence", "signature-corrected", "signature-recovered",
        "static-reaudit", "world-physics-manager", "worldphysics-factory-tail-wave558"));

    private static final List<String> EXPECTED_CALLERS = sorted(Arrays.asList(
        "0x0040e040", "0x004156c3", "0x00417a92", "0x004283c5", "0x00442741",
        "0x0044797d", "0x0044cdde", "0x0044d145", "0x0044e40e", "0x00480401",
        "0x00489b89", "0x0049fca2", "0x004ba83c", "0x004d7eff", "0x004da521",
        "0x004da6ea", "0x004defdf", "0x004dfb85", "0x004f0ab5", "0x004f1089",
        "0x004f4c01", "0x004f9375", "0x004f954b", "0x004fd253"));

    private static final class PreState {
        final String name;
        final String parameter;
        final SourceType parameterSource;
        final String comment;
        final List<String> tags;

        PreState(String name, String parameter, SourceType parameterSource, String comment,
                List<String> tags) {
            this.name = name;
            this.parameter = parameter;
            this.parameterSource = parameterSource;
            this.comment = comment;
            this.tags = new ArrayList<>(tags);
        }
    }

    private static void require(boolean value, String message) {
        if (!value) {
            throw new IllegalStateException(message);
        }
    }

    private static void equal(String owner, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(owner + " " + field + " differs: expected=" +
                expected + " actual=" + actual);
        }
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static List<String> sorted(List<String> values) {
        List<String> result = new ArrayList<>(values);
        Collections.sort(result);
        return result;
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

    private static String json(String value) {
        return nullable(value).replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t");
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
                name.length() + ":" + sha256(name) +
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

    private void validateProgram() throws Exception {
        equal("program", "name", PROGRAM_NAME, currentProgram.getName());
        equal("program", "MD5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        equal("program", "SHA-256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        equal("program", "image base", IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        equal("program", "language", LANGUAGE, currentProgram.getLanguageID().toString());
        equal("program", "compiler", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        equal("program", "memory", MEMORY_SHA256, memoryDigest());
        equal("program", "functions", FUNCTION_COUNT, functionCount());
        equal("program", "instructions", INSTRUCTION_COUNT, instructionCount());
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
                equal(ENTRY, "body memory read", size, read);
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

    private Function exactFunction() {
        Address entry = toAddr(ENTRY);
        Function function = getFunctionAt(entry);
        require(function != null && function.getEntryPoint().equals(entry),
            "target function is absent");
        return function;
    }

    private List<String> tags(Function function) {
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : function.getTags()) {
            result.add(tag.getName());
        }
        Collections.sort(result);
        return result;
    }

    private void setTags(Function function, List<String> expected) {
        for (String existing : tags(function)) {
            function.removeTag(existing);
        }
        for (String tag : expected) {
            require(function.addTag(tag), "could not add tag: " + tag);
        }
        equal(ENTRY, "tag set", expected, tags(function));
    }

    private void validateCommon(Function function) throws Exception {
        AddressSetView body = function.getBody();
        equal(ENTRY, "body range", BODY_RANGE, canonicalRanges(body));
        equal(ENTRY, "body bytes", BODY_BYTES, body.getNumAddresses());
        equal(ENTRY, "body range SHA-256", BODY_RANGE_SHA256, bodyRangeDigest(body));
        equal(ENTRY, "body bytes SHA-256", BODY_BYTES_SHA256, bodyBytesDigest(body));
        equal(ENTRY, "instruction count", BODY_INSTRUCTIONS, exactInstructions(body));
        equal(ENTRY, "namespace", "Global", function.getParentNamespace().getName(true));
        equal(ENTRY, "name source", SourceType.USER_DEFINED, function.getSymbol().getSource());
        equal(ENTRY, "signature source", SourceType.USER_DEFINED, function.getSignatureSource());
        equal(ENTRY, "calling convention", "__cdecl", function.getCallingConventionName());
        equal(ENTRY, "return type", "void *", function.getReturn().getDataType().getDisplayName());
        equal(ENTRY, "return storage", "EAX:4", function.getReturn().getVariableStorage().toString());
        equal(ENTRY, "parameter count", 1, function.getParameterCount());
        Parameter parameter = function.getParameters()[0];
        equal(ENTRY, "parameter type", "int", parameter.getDataType().getDisplayName());
        equal(ENTRY, "parameter storage", "Stack[0x4]:4", parameter.getVariableStorage().toString());
        equal(ENTRY, "parameter source", SourceType.USER_DEFINED, parameter.getSource());
        equal(ENTRY, "stack parameter bytes", 4, function.getStackFrame().getParameterSize());
        equal(ENTRY, "frame size", 20, function.getStackFrame().getFrameSize());
        equal(ENTRY, "local size", 16, function.getStackFrame().getLocalSize());
        require(!function.hasCustomVariableStorage() && !function.hasVarArgs() &&
                !function.isInline() && !function.hasNoReturn() && !function.isThunk(),
            "ABI/control flags differ");
        Symbol symbol = function.getSymbol();
        require(symbol.getSymbolType() == SymbolType.FUNCTION && symbol.isPrimary() &&
                !symbol.isDynamic() && !symbol.isExternal() && !symbol.isPinned(),
            "target symbol flags differ");

        Symbol[] addressSymbols = currentProgram.getSymbolTable().getSymbols(toAddr(ENTRY));
        equal(ENTRY, "symbols at entry", 1, addressSymbols.length);
        equal(ENTRY, "entry symbol identity", symbol.getID(), addressSymbols[0].getID());
        validateCallAndInteriorCensus(function);
    }

    private void validateCallAndInteriorCensus(Function function) {
        Address entry = toAddr(ENTRY);
        AddressSetView body = function.getBody();
        List<String> callers = new ArrayList<>();
        int externalInterior = 0;
        AddressIterator addresses = body.getAddresses(true);
        while (addresses.hasNext()) {
            Address to = addresses.next();
            ReferenceIterator references = currentProgram.getReferenceManager().getReferencesTo(to);
            while (references.hasNext()) {
                Reference reference = references.next();
                if (body.contains(reference.getFromAddress())) {
                    continue;
                }
                if (to.equals(entry)) {
                    require("UNCONDITIONAL_CALL".equals(reference.getReferenceType().toString()),
                        "non-call reaches target entry from " + reference.getFromAddress());
                    callers.add("0x" + reference.getFromAddress());
                }
                else {
                    externalInterior++;
                }
            }
        }
        Collections.sort(callers);
        equal(ENTRY, "direct callers", EXPECTED_CALLERS, callers);
        equal(ENTRY, "external interior references", 0, externalInterior);
    }

    private int nameCount(String name) {
        int count = 0;
        SymbolIterator symbols = currentProgram.getSymbolTable().getSymbols(name);
        while (symbols.hasNext()) {
            symbols.next();
            count++;
        }
        return count;
    }

    private void validatePre() throws Exception {
        validateProgram();
        Function function = exactFunction();
        validateCommon(function);
        equal(ENTRY, "PRE name", PRE_NAME, function.getName());
        equal(ENTRY, "PRE signature", PRE_SIGNATURE,
            function.getSignature().getPrototypeString(true));
        equal(ENTRY, "PRE parameter", PRE_PARAMETER, function.getParameters()[0].getName());
        String comment = nullable(function.getComment());
        equal(ENTRY, "PRE comment bytes", PRE_COMMENT_BYTES,
            (long) comment.getBytes(StandardCharsets.UTF_8).length);
        equal(ENTRY, "PRE comment SHA-256", PRE_COMMENT_SHA256, sha256(comment));
        equal(ENTRY, "PRE repeatable comment", "", nullable(function.getRepeatableComment()));
        equal(ENTRY, "PRE tags", PRE_TAGS, tags(function));
        equal(PRE_NAME, "symbol census", 1, nameCount(PRE_NAME));
        equal(POST_NAME, "symbol census", 0, nameCount(POST_NAME));
    }

    private void validatePost() throws Exception {
        validateProgram();
        Function function = exactFunction();
        validateCommon(function);
        equal(ENTRY, "POST name", POST_NAME, function.getName());
        equal(ENTRY, "POST signature", POST_SIGNATURE,
            function.getSignature().getPrototypeString(true));
        equal(ENTRY, "POST parameter", POST_PARAMETER, function.getParameters()[0].getName());
        String comment = nullable(function.getComment());
        equal(ENTRY, "POST comment", POST_COMMENT, comment);
        equal(ENTRY, "POST comment bytes", POST_COMMENT_BYTES,
            (long) comment.getBytes(StandardCharsets.UTF_8).length);
        equal(ENTRY, "POST comment SHA-256", POST_COMMENT_SHA256, sha256(comment));
        equal(ENTRY, "POST repeatable comment", "", nullable(function.getRepeatableComment()));
        equal(ENTRY, "POST tags", POST_TAGS, tags(function));
        equal(PRE_NAME, "symbol census", 0, nameCount(PRE_NAME));
        equal(POST_NAME, "symbol census", 1, nameCount(POST_NAME));
    }

    private PreState capturePre() throws Exception {
        validatePre();
        Function function = exactFunction();
        return new PreState(function.getName(), function.getParameters()[0].getName(),
            function.getParameters()[0].getSource(), function.getComment(), tags(function));
    }

    private void applyPost(boolean nameOnly) throws Exception {
        Function function = exactFunction();
        validateCommon(function);
        equal(ENTRY, "apply PRE name", PRE_NAME, function.getName());
        function.setName(POST_NAME, SourceType.USER_DEFINED);
        if (nameOnly) {
            equal(ENTRY, "after-one name", POST_NAME, function.getName());
            return;
        }
        function.getParameters()[0].setName(POST_PARAMETER, SourceType.USER_DEFINED);
        function.setComment(POST_COMMENT);
        setTags(function, POST_TAGS);
        validatePost();
    }

    private void restorePre(PreState pre) throws Exception {
        Function function = exactFunction();
        validateCommon(function);
        function.setName(pre.name, SourceType.USER_DEFINED);
        function.getParameters()[0].setName(pre.parameter, pre.parameterSource);
        function.setComment(pre.comment);
        setTags(function, pre.tags);
        validatePre();
    }

    private static File requireEvidence(File repositoryRoot, String relative,
            long expectedBytes, String expectedSha256) throws Exception {
        File file = new File(repositoryRoot, relative).getCanonicalFile();
        require(file.isFile(), "evidence is absent: " + file);
        byte[] bytes = Files.readAllBytes(file.toPath());
        equal(relative, "bytes", expectedBytes, (long) bytes.length);
        equal(relative, "SHA-256", expectedSha256, sha256(bytes));
        return file;
    }

    private static String repositoryRelative(File repositoryRoot, File file)
            throws Exception {
        java.nio.file.Path root = repositoryRoot.getCanonicalFile().toPath();
        java.nio.file.Path target = file.getCanonicalFile().toPath();
        require(target.startsWith(root), "path is outside supplied repository root: " + target);
        return root.relativize(target).toString().replace(File.separatorChar, '/');
    }

    private static File newOutput(String value, String label) throws Exception {
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

    private static void publishPair(File output, byte[] outputBytes,
            File ready, byte[] readyBytes) throws Exception {
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

    private byte[] buildOutput(String mode, String state) throws Exception {
        Function function = exactFunction();
        String comment = nullable(function.getComment());
        String tagText = String.join(",", tags(function));
        String text = "address\tmode\tstate\tname\tnameSource\tsignatureSource\tsignature\t" +
            "parameterName\tparameterType\tparameterStorage\tparameterSource\tcallingConvention\treturnType\t" +
            "returnStorage\tbodyRanges\tbodyBytes\tbodyRangeSha256\tbodyBytesSha256\t" +
            "instructionCount\tcommentBytes\tcommentSha256\ttags\ttagsSha256\n" +
            ENTRY + "\t" + mode + "\t" + state + "\t" + function.getName() + "\t" +
            function.getSymbol().getSource() + "\t" + function.getSignatureSource() + "\t" +
            function.getSignature().getPrototypeString(true) + "\t" +
            function.getParameters()[0].getName() + "\t" +
            function.getParameters()[0].getDataType().getDisplayName() + "\t" +
            function.getParameters()[0].getVariableStorage() + "\t" +
            function.getParameters()[0].getSource() + "\t" +
            function.getCallingConventionName() + "\t" +
            function.getReturn().getDataType().getDisplayName() + "\t" +
            function.getReturn().getVariableStorage() + "\t" + BODY_RANGE + "\t" + BODY_BYTES + "\t" +
            BODY_RANGE_SHA256 + "\t" + BODY_BYTES_SHA256 + "\t" + BODY_INSTRUCTIONS + "\t" +
            comment.getBytes(StandardCharsets.UTF_8).length + "\t" + sha256(comment) + "\t" +
            tagText + "\t" + sha256(tagText) + "\n";
        return text.getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(String mode, String state, String toolRelative,
            byte[] toolBytes, String outputRelative, byte[] outputBytes,
            boolean commitRequested, boolean nestedCommitted) throws Exception {
        int changed = mode.equals("apply") ? 1 : 0;
        String text = "{\n" +
            "  \"schema\": \"" + SCHEMA + "\",\n" +
            "  \"completedAtUtc\": \"" + json(Instant.now().toString()) + "\",\n" +
            "  \"mode\": \"" + mode + "\",\n" +
            "  \"state\": \"" + state + "\",\n" +
            "  \"tool\": {\"path\": \"" + json(toolRelative) +
                "\", \"bytes\": " + toolBytes.length + ", \"sha256\": \"" + sha256(toolBytes) + "\"},\n" +
            "  \"owner\": {\"path\": \"" + json(OWNER_RELATIVE) +
                "\", \"bytes\": " + OWNER_BYTES + ", \"sha256\": \"" + OWNER_SHA256 + "\"},\n" +
            "  \"manifest\": {\"path\": \"" + json(MANIFEST_RELATIVE) +
                "\", \"bytes\": " + MANIFEST_BYTES + ", \"sha256\": \"" + MANIFEST_SHA256 + "\"},\n" +
            "  \"reproof\": {\"path\": \"" + json(REPROOF_RELATIVE) +
                "\", \"bytes\": " + REPROOF_BYTES + ", \"sha256\": \"" + REPROOF_SHA256 + "\"},\n" +
            "  \"program\": {\"name\": \"" + PROGRAM_NAME + "\", \"md5\": \"" + PROGRAM_MD5 +
                "\", \"sha256\": \"" + PROGRAM_SHA256 + "\", \"functions\": " + FUNCTION_COUNT +
                ", \"instructions\": " + INSTRUCTION_COUNT + ", \"memorySha256\": \"" + MEMORY_SHA256 + "\"},\n" +
            "  \"target\": {\"address\": \"" + ENTRY + "\", \"bodyBytes\": " + BODY_BYTES +
                ", \"bodySha256\": \"" + BODY_BYTES_SHA256 + "\", \"directCallers\": 24, " +
                "\"externalInteriorReferences\": 0, \"parameterSource\": \"USER_DEFINED\"},\n" +
            "  \"output\": {\"path\": \"" + json(outputRelative) +
                "\", \"bytes\": " + outputBytes.length + ", \"sha256\": \"" + sha256(outputBytes) + "\"},\n" +
            "  \"mutation\": {\"namesChanged\": " + changed +
                ", \"parameterNamesChanged\": " + changed +
                ", \"parameterSourcesChanged\": 0" +
                ", \"commentsChanged\": " + changed +
                ", \"tagSetsChanged\": " + changed +
                ", \"boundariesChanged\": 0, " +
                "\"bytesChanged\": 0, \"instructionsChanged\": 0, \"dataUnitsChanged\": 0, " +
                "\"referencesChanged\": 0},\n" +
            "  \"commitRequested\": " + commitRequested + ",\n" +
            "  \"nestedEndReturnedCommitted\": " + nestedCommitted + ",\n" +
            "  \"loadedStateVerified\": " + mode.equals("readback") + ",\n" +
            "  \"runtimeSemanticsAuthorized\": false,\n" +
            "  \"rebuildReadyAuthorized\": false,\n" +
            "  \"authorityBoundary\": \"scratch_only_until_sealed_and_fresh_live_pre_backup\"\n" +
            "}\n";
        return text.getBytes(StandardCharsets.UTF_8);
    }

    private void validateOuter(long expectedId, String phase) {
        TransactionInfo info = currentProgram.getCurrentTransactionInfo();
        require(info != null, phase + " outer transaction is absent");
        equal("transaction", phase + " id", expectedId, info.getID());
        equal("transaction", phase + " status", TransactionInfo.Status.NOT_DONE, info.getStatus());
        equal("transaction", phase + " terminated", false, currentProgram.hasTerminatedTransaction());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 4,
            "usage: <repository-root> <out.tsv> <out.ready.json> <dry|probe-after-one|probe-post-inner|apply|readback>");
        String mode = args[3].toLowerCase(Locale.ROOT);
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
            .contains(mode), "unsupported mode: " + mode);

        File repositoryRoot = new File(args[0]).getCanonicalFile();
        require(repositoryRoot.isDirectory(), "repository root is absent");
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        require(tool.getParentFile().equals(new File(repositoryRoot, "tools").getCanonicalFile()),
            "tool is not under supplied repository root");
        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File owner = requireEvidence(repositoryRoot, OWNER_RELATIVE, OWNER_BYTES, OWNER_SHA256);
        File manifest = requireEvidence(repositoryRoot, MANIFEST_RELATIVE, MANIFEST_BYTES, MANIFEST_SHA256);
        File reproof = requireEvidence(repositoryRoot, REPROOF_RELATIVE, REPROOF_BYTES, REPROOF_SHA256);
        File output = newOutput(args[1], "output TSV");
        File ready = newOutput(args[2], "READY receipt");
        String toolRelative = repositoryRelative(repositoryRoot, tool);
        String ownerRelative = repositoryRelative(repositoryRoot, owner);
        String manifestRelative = repositoryRelative(repositoryRoot, manifest);
        String reproofRelative = repositoryRelative(repositoryRoot, reproof);
        String outputRelative = repositoryRelative(repositoryRoot, output);
        String readyRelative = repositoryRelative(repositoryRoot, ready);
        equal("tool", "repository-relative path", TOOL_RELATIVE, toolRelative);
        equal("owner", "repository-relative path", OWNER_RELATIVE, ownerRelative);
        equal("manifest", "repository-relative path", MANIFEST_RELATIVE, manifestRelative);
        equal("reproof", "repository-relative path", REPROOF_RELATIVE, reproofRelative);
        require(!output.equals(ready) && output.getParentFile().equals(ready.getParentFile()),
            "output paths must be distinct siblings");
        require(!outputRelative.equals(readyRelative),
            "repository-relative output paths must be distinct");
        equal("POST comment", "bytes", POST_COMMENT_BYTES,
            (long) POST_COMMENT.getBytes(StandardCharsets.UTF_8).length);
        equal("POST comment", "SHA-256", POST_COMMENT_SHA256, sha256(POST_COMMENT));

        if (mode.equals("readback")) {
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            publishPair(output, outputBytes, ready,
                buildReady(mode, "POST", toolRelative, toolBytes,
                    outputRelative, outputBytes, false, false));
            println("CEXPLOSION_FACTORY_IDENTITY_READBACK_COMPLETE loaded_state_verified=true");
            return;
        }

        validatePre();
        println("CEXPLOSION_FACTORY_IDENTITY_PREFLIGHT_OK target=1 functions=" + FUNCTION_COUNT +
            " instructions=" + INSTRUCTION_COUNT + " tool_sha256=" + sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            publishPair(output, outputBytes, ready,
                buildReady(mode, "PRE", toolRelative, toolBytes,
                    outputRelative, outputBytes, false, false));
            println("CEXPLOSION_FACTORY_IDENTITY_DRY_COMPLETE mutations=0");
            return;
        }

        PreState pre = capturePre();
        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires a healthy outer Ghidra transaction");
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction("Correct CExplosion factory identity");
        boolean ended = false;
        boolean commitRequested = false;
        boolean nestedCommitted = false;
        try {
            applyPost(mode.equals("probe-after-one"));
            if (mode.equals("probe-after-one")) {
                println("CEXPLOSION_FACTORY_IDENTITY_FORCED_AFTER_ONE_FAILURE rollback_required=true");
                throw new IllegalStateException("intentional CExplosion factory after-one rollback probe");
            }
            commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            ended = true;
            equal("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");

            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction("Restore CExplosion factory PRE metadata");
                boolean restoreEnded = false;
                try {
                    restorePre(pre);
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    equal("transaction", "restore nested end committed", false, restoreCommitted);
                }
                finally {
                    if (!restoreEnded) currentProgram.endTransaction(restore, false);
                }
                validatePre();
                validateOuter(outerId, "after compensating PRE restore");
                println("CEXPLOSION_FACTORY_IDENTITY_COMPENSATING_PRE_RESTORE_COMPLETE target=1");
                println("CEXPLOSION_FACTORY_IDENTITY_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException("intentional CExplosion factory post-inner rollback probe");
            }

            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            publishPair(output, outputBytes, ready,
                buildReady(mode, "POST", toolRelative, toolBytes,
                    outputRelative, outputBytes, true, nestedCommitted));
            println("CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE target=1 reopen_verification_required=true");
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
            println("CEXPLOSION_FACTORY_IDENTITY_MUTATION_TAINTED mode=" + mode +
                " commit_requested=" + commitRequested +
                " nested_end_returned_committed=" + nestedCommitted);
            throw error;
        }
        finally {
            if (!ended) currentProgram.endTransaction(transaction, false);
        }
    }
}
