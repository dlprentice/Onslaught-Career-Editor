//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
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
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

/**
 * Apply exactly two Generation-12-adjudicated Battle Engine metadata changes.
 *
 * This is deliberately not a generic rename script. It is bound to the pristine
 * specimen, exact function bodies/preimages, exact Generation 12 campaign,
 * exact bounded write proof, and exact externally selected authority receipt.
 *
 * Modes:
 *   dry              validate the PRE state and publish no mutation;
 *   probe-after-one  mutate one row, then force nested-transaction rollback;
 *   probe-post-inner mutate both rows, end the nested transaction, restore the
 *                    exact validated PRE metadata in a second transaction, then
 *                    force failure;
 *   apply            mutate both rows in one nested transaction;
 *   readback         require the exact POST state without mutation.
 */
public class GhidraApplyDamageHitContracts extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.damage-hit-semantic.v1";
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
        "generation-12-level521-damage-hit-writes-v1/campaign.ready.json";
    private static final long CAMPAIGN_BYTES = 17110;
    private static final String CAMPAIGN_SHA256 =
        "9d2b903d451cb62fd6fb599b915dd57a0e6f313e610a348022fabf26ee265747";
    private static final String PROOF_RELATIVE =
        "local-lab/level521-damage-hit-write-proof-20260808-v2/proof.ready.json";
    private static final long PROOF_BYTES = 2529;
    private static final String PROOF_SHA256 =
        "ffb2e0b8692ddada364a829d52a158841e5d800742c49bd2a1710b2af135869a";
    private static final String AUTHORITY_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-12-level521-damage-hit-writes-authority.ready.json";
    private static final long AUTHORITY_BYTES = 8456;
    private static final String AUTHORITY_SHA256 =
        "c3531b495084ec73fc2b76a70be3409ca120448ba6831cbfa96a70866e182cba";

    private static final String DAMAGE_COMMENT =
        "Retail/source identity and bounded runtime contract: 0x0040A890 matches " +
        "CBattleEngine::Damage (BattleEngine.h:133; BattleEngine.cpp:2127 onward). " +
        "The 917-byte retail body and RET 0x10 prove four 4-byte explicit arguments. " +
        "Source prototype: void Damage(float amount, CThing *inByThis, BOOL " +
        "inDamageShields, int mesh_part_no); Ghidra records BOOL as int to preserve " +
        "its 32-bit ABI and keeps object types opaque. Generation 12 witnessed one " +
        "replicated invocation writing, in order, mShields +0x100, mAugValue +0x168, " +
        "mLife +0x154, mLastDamageTime +0x174, and mEnergy +0xFC, plus two zero-write " +
        "controls. Five nontrivial observation gaps and nine continuity breaks forbid " +
        "a complete write-set or universal-path claim. Rebuild state is " +
        "PARTIAL_CONTRACT, not REBUILD_READY; negative damage, lethal/StartDie, " +
        "source-flash, branch, return-context, and unobserved-path behavior remain open. " +
        "Gen12 READY 9d2b903d451c; proof ffb2e0b8692d.";

    private static final String HIT_COMMENT =
        "Retail/source identity and bounded runtime control: 0x00407350 matches " +
        "CBattleEngine::Hit (BattleEngine.h:105; BattleEngine.cpp:1014-1061). The " +
        "380-byte retail body and RET 0x8 prove two 4-byte explicit arguments. Source " +
        "prototype: void Hit(CThing *other_thing, CCollisionReport *report); Ghidra " +
        "keeps object types opaque. One gap-free Generation 12 invocation observed " +
        "zero writes to exactly seven watched Battle Engine fields. This does not prove " +
        "zero writes to other memory, other branches, or other invocations, and source " +
        "architecture does not substitute for released-runtime causality. Rebuild state " +
        "is NOT_READY. Gen12 READY 9d2b903d451c; proof ffb2e0b8692d.";

    private static class ParameterSpec {
        final String type;
        final String name;

        ParameterSpec(String type, String name) {
            this.type = type;
            this.name = name;
        }
    }

    private static class Target {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final long expectedBodyBytes;
        final String expectedBodyMin;
        final String expectedBodyMax;
        final String expectedBodyDigest;
        final String expectedBodyBytesSha256;
        final long expectedInstructionCount;
        final int expectedFrameSize;
        final int expectedLocalSize;
        final int expectedParameterSize;
        final String proposedName;
        final List<ParameterSpec> parameters;
        final String proposedSignature;
        final String proposedComment;

        Target(
                String address, String expectedName, String expectedSignature,
                long expectedBodyBytes, String expectedBodyMin, String expectedBodyMax,
                String expectedBodyDigest, String expectedBodyBytesSha256,
                long expectedInstructionCount, int expectedFrameSize,
                int expectedLocalSize, int expectedParameterSize,
                String proposedName, List<ParameterSpec> parameters,
                String proposedSignature, String proposedComment) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
            this.expectedBodyBytes = expectedBodyBytes;
            this.expectedBodyMin = expectedBodyMin;
            this.expectedBodyMax = expectedBodyMax;
            this.expectedBodyDigest = expectedBodyDigest;
            this.expectedBodyBytesSha256 = expectedBodyBytesSha256;
            this.expectedInstructionCount = expectedInstructionCount;
            this.expectedFrameSize = expectedFrameSize;
            this.expectedLocalSize = expectedLocalSize;
            this.expectedParameterSize = expectedParameterSize;
            this.proposedName = proposedName;
            this.parameters = parameters;
            this.proposedSignature = proposedSignature;
            this.proposedComment = proposedComment;
        }
    }

    private static class PreState {
        final String callingConvention;
        final DataType returnType;
        final List<ParameterSpec> parameters;
        final List<DataType> parameterTypes;
        final String localsKey;

        PreState(
                String callingConvention, DataType returnType,
                List<ParameterSpec> parameters, List<DataType> parameterTypes,
                String localsKey) {
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.parameterTypes = parameterTypes;
            this.localsKey = localsKey;
        }
    }

    private static final List<Target> TARGETS = Arrays.asList(
        new Target(
            "0x00407350", "CBattleEngine__VFunc_39_00407350",
            "undefined __thiscall CBattleEngine__VFunc_39_00407350(void * this, int * param_1, void * param_2)",
            380, "00407350", "004074cb",
            "28151a2f8b9850159b4c2f1e843f4c34e44d6258d9a79f1c4abe7a296301b210",
            "8034efee2c37c5e02579dc82d4405b758cedc96d62b27909f5c66a6cea43ae8a",
            114, 12, 4, 8, "CBattleEngine__Hit",
            Arrays.asList(
                new ParameterSpec("void*", "this"),
                new ParameterSpec("void*", "otherThing"),
                new ParameterSpec("void*", "report")),
            "void __thiscall CBattleEngine__Hit(void * this, void * otherThing, void * report)",
            HIT_COMMENT),
        new Target(
            "0x0040a890", "CBattleEngine__VFunc_40_0040a890",
            "undefined __thiscall CBattleEngine__VFunc_40_0040a890(void * this, float param_1, int param_2, int param_3)",
            917, "0040a890", "0040ac24",
            "7b3b41b512c777438736116c9c5627a3b832ad47e5f71458a265e145cd99a127",
            "224c0577b539bbf0d6fa118a6355502f9aead3bc588e59ae3bf08bdf3cd1ff91",
            233, 76, 64, 12, "CBattleEngine__Damage",
            Arrays.asList(
                new ParameterSpec("void*", "this"),
                new ParameterSpec("float", "amount"),
                new ParameterSpec("void*", "inByThis"),
                new ParameterSpec("int", "inDamageShields"),
                new ParameterSpec("int", "meshPartNo")),
            "void __thiscall CBattleEngine__Damage(void * this, float amount, void * inByThis, int inDamageShields, int meshPartNo)",
            DAMAGE_COMMENT));

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

    private static void requireEqual(String owner, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(
                owner + " " + field + " differs: expected=" + expected + " actual=" + actual);
        }
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static String json(String value) {
        return nullable(value)
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
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

    private long programFunctionCount() {
        long count = 0;
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            functions.next();
            count++;
        }
        return count;
    }

    private long programInstructionCount() {
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            instructions.next();
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
        requireEqual("program", "functions", FUNCTION_COUNT, programFunctionCount());
        requireEqual("program", "instructions", INSTRUCTION_COUNT, programInstructionCount());
    }

    private Function exactFunction(Target target) {
        Address address = toAddr(target.address);
        Function function = getFunctionAt(address);
        if (function == null || !function.getEntryPoint().equals(address)) {
            throw new IllegalStateException("exact function is missing at " + target.address);
        }
        return function;
    }

    private String bodyDigest(AddressSetView body) throws Exception {
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

    private long validatedInstructionCount(AddressSetView body, String label) {
        AddressSet covered = new AddressSet();
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (!body.contains(instruction.getMinAddress(), instruction.getMaxAddress())) {
                throw new IllegalStateException("instruction crosses body at " + label);
            }
            covered.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
            count++;
        }
        if (!covered.hasSameAddresses(body)) {
            throw new IllegalStateException("instruction coverage differs at " + label);
        }
        return count;
    }

    private static String signature(Function function) {
        return function.getSignature().getPrototypeString(true);
    }

    private static String localsKey(Function function) {
        StringBuilder result = new StringBuilder();
        Variable[] locals = function.getLocalVariables();
        result.append("count=").append(locals.length);
        for (int index = 0; index < locals.length; index++) {
            Variable local = locals[index];
            result.append('|').append(index).append(':')
                .append(nullable(local.getName())).append(':')
                .append(local.getDataType().getPathName()).append('@')
                .append(local.getVariableStorage()).append(':')
                .append(local.getSource()).append(':').append(local.getLength()).append(':')
                .append(local.getFirstUseOffset()).append(':').append(local.isValid()).append(':')
                .append(nullable(local.getComment()));
        }
        return result.toString();
    }

    private void validateCommon(Target target, Function function) throws Exception {
        AddressSetView body = function.getBody();
        requireEqual(target.address, "body bytes", target.expectedBodyBytes, body.getNumAddresses());
        requireEqual(target.address, "body minimum", target.expectedBodyMin,
            body.getMinAddress().toString().toLowerCase(Locale.ROOT));
        requireEqual(target.address, "body maximum", target.expectedBodyMax,
            body.getMaxAddress().toString().toLowerCase(Locale.ROOT));
        requireEqual(target.address, "body digest", target.expectedBodyDigest, bodyDigest(body));
        requireEqual(target.address, "body byte SHA-256", target.expectedBodyBytesSha256,
            bodyBytesSha256(body));
        requireEqual(target.address, "instruction count", target.expectedInstructionCount,
            validatedInstructionCount(body, target.address));
        requireEqual(target.address, "call fixup", null, function.getCallFixup());
        requireEqual(target.address, "repeatable comment", null, function.getRepeatableComment());
        requireEqual(target.address, "tag count", 0, function.getTags().size());
    }

    private void validatePre(Target target) throws Exception {
        Function function = exactFunction(target);
        validateCommon(target, function);
        requireEqual(target.address, "PRE name", target.expectedName, function.getName());
        requireEqual(target.address, "PRE name source", SourceType.USER_DEFINED,
            function.getSymbol().getSource());
        requireEqual(target.address, "PRE signature source", SourceType.ANALYSIS,
            function.getSignatureSource());
        requireEqual(target.address, "PRE signature", target.expectedSignature, signature(function));
        requireEqual(target.address, "PRE comment", null, function.getComment());
        requireEqual(target.address, "PRE frame", target.expectedFrameSize,
            function.getStackFrame().getFrameSize());
        requireEqual(target.address, "PRE locals", target.expectedLocalSize,
            function.getStackFrame().getLocalSize());
        requireEqual(target.address, "PRE params", target.expectedParameterSize,
            function.getStackFrame().getParameterSize());
    }

    private void validatePost(Target target) throws Exception {
        Function function = exactFunction(target);
        validateCommon(target, function);
        requireEqual(target.address, "POST name", target.proposedName, function.getName());
        requireEqual(target.address, "POST name source", SourceType.USER_DEFINED,
            function.getSymbol().getSource());
        requireEqual(target.address, "POST signature source", SourceType.USER_DEFINED,
            function.getSignatureSource());
        requireEqual(target.address, "POST signature", target.proposedSignature, signature(function));
        requireEqual(target.address, "POST comment", target.proposedComment, function.getComment());
        requireEqual(target.address, "POST parameter count", target.parameters.size(),
            function.getParameterCount());
        Parameter[] parameters = function.getParameters();
        for (int index = 0; index < parameters.length; index++) {
            requireEqual(target.address, "POST parameter name " + index,
                target.parameters.get(index).name, parameters[index].getName());
        }
    }

    private DataType dataType(String type) {
        if (type.equals("void*")) {
            return new PointerDataType(VoidDataType.dataType, currentProgram.getDataTypeManager());
        }
        if (type.equals("float")) {
            return FloatDataType.dataType;
        }
        if (type.equals("int")) {
            return IntegerDataType.dataType;
        }
        throw new IllegalArgumentException("unsupported type: " + type);
    }

    private void applyTarget(Target target) throws Exception {
        Function function = exactFunction(target);
        String localsBefore = localsKey(function);
        Variable[] parameters = new Variable[target.parameters.size()];
        for (int index = 0; index < parameters.length; index++) {
            ParameterSpec spec = target.parameters.get(index);
            parameters[index] = new ParameterImpl(spec.name, dataType(spec.type), currentProgram);
        }
        function.updateFunction(
            "__thiscall",
            new ReturnParameterImpl(VoidDataType.dataType, currentProgram),
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            false,
            SourceType.USER_DEFINED,
            parameters);
        function.setName(target.proposedName, SourceType.USER_DEFINED);
        function.setComment(target.proposedComment);
        requireEqual(target.address, "local variables changed", localsBefore, localsKey(function));
        validatePost(target);
    }

    private PreState capturePre(Target target) throws Exception {
        Function function = exactFunction(target);
        validatePre(target);
        List<ParameterSpec> parameters = new ArrayList<>();
        List<DataType> parameterTypes = new ArrayList<>();
        for (Parameter parameter : function.getParameters()) {
            parameters.add(new ParameterSpec(parameter.getDataType().getPathName(), parameter.getName()));
            parameterTypes.add(parameter.getDataType().clone(currentProgram.getDataTypeManager()));
        }
        return new PreState(
            function.getCallingConventionName(),
            function.getReturnType().clone(currentProgram.getDataTypeManager()),
            parameters,
            parameterTypes,
            localsKey(function));
    }

    private void restorePre(Target target, PreState state) throws Exception {
        Function function = exactFunction(target);
        Variable[] parameters = new Variable[state.parameters.size()];
        for (int index = 0; index < parameters.length; index++) {
            parameters[index] = new ParameterImpl(
                state.parameters.get(index).name,
                state.parameterTypes.get(index),
                currentProgram);
        }
        function.updateFunction(
            state.callingConvention,
            new ReturnParameterImpl(state.returnType, currentProgram),
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            false,
            SourceType.ANALYSIS,
            parameters);
        function.setName(target.expectedName, SourceType.USER_DEFINED);
        function.setComment(null);
        requireEqual(target.address, "restored local variables", state.localsKey, localsKey(function));
        validatePre(target);
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
            if (stagedOutput != null) {
                Files.deleteIfExists(stagedOutput.toPath());
            }
            if (stagedReady != null) {
                Files.deleteIfExists(stagedReady.toPath());
            }
        }
    }

    private byte[] buildOutput(String mode, String state) throws Exception {
        StringBuilder output = new StringBuilder();
        output.append("address\tmode\tstate\tname\tnameSource\tsigSource\tsignature\t")
            .append("bodyBytes\tbodySha256\tinstructionCount\tframeSize\tlocalSize\t")
            .append("parameterSize\tlocalsSha256\tcommentBytes\tcommentSha256\n");
        for (Target target : TARGETS) {
            Function function = exactFunction(target);
            String comment = nullable(function.getComment());
            output.append(target.address).append('\t').append(mode).append('\t')
                .append(state).append('\t').append(function.getName()).append('\t')
                .append(function.getSymbol().getSource()).append('\t')
                .append(function.getSignatureSource()).append('\t')
                .append(signature(function)).append('\t')
                .append(function.getBody().getNumAddresses()).append('\t')
                .append(bodyBytesSha256(function.getBody())).append('\t')
                .append(validatedInstructionCount(function.getBody(), target.address)).append('\t')
                .append(function.getStackFrame().getFrameSize()).append('\t')
                .append(function.getStackFrame().getLocalSize()).append('\t')
                .append(function.getStackFrame().getParameterSize()).append('\t')
                .append(sha256(localsKey(function))).append('\t')
                .append(comment.getBytes(StandardCharsets.UTF_8).length).append('\t')
                .append(sha256(comment)).append('\n');
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
        ready.append("  \"targets\": 2,\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"nestedEndReturnedCommitted\": ")
            .append(nestedEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback"))
            .append(",\n");
        ready.append("  \"semanticNamesAuthorized\": false,\n");
        ready.append("  \"authorityBoundary\": \"requires_external_two_replica_or_separate_live_readback\"\n");
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
        validateProgram();

        Set<String> names = new HashSet<>();
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            names.add(functions.next().getName());
        }

        if (mode.equals("readback")) {
            for (Target target : TARGETS) {
                validatePost(target);
            }
            validateProgram();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", toolBytes,
                toolFile.getCanonicalPath(), output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("DAMAGE_HIT_READBACK_COMPLETE rows=2");
            return;
        }

        List<PreState> preStates = new ArrayList<>();
        for (Target target : TARGETS) {
            preStates.add(capturePre(target));
            if (names.contains(target.proposedName)) {
                throw new IllegalStateException("proposed name already exists: " + target.proposedName);
            }
        }
        println("DAMAGE_HIT_PREFLIGHT_OK rows=2 tool_sha256=" + sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            byte[] readyBytes = buildReady(mode, "PRE", toolBytes,
                toolFile.getCanonicalPath(), output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("DAMAGE_HIT_DRY_COMPLETE rows=2 mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        if (outer == null || currentProgram.hasTerminatedTransaction()) {
            throw new IllegalStateException("mutation requires a healthy outer Ghidra transaction");
        }
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction("Damage and Hit semantic contracts");
        boolean transactionEnded = false;
        boolean commitRequested = false;
        boolean nestedCommitted = false;
        try {
            for (int index = 0; index < TARGETS.size(); index++) {
                monitor.checkCancelled();
                applyTarget(TARGETS.get(index));
                if (mode.equals("probe-after-one") && index == 0) {
                    println("DAMAGE_HIT_FORCED_AFTER_ONE_FAILURE rollback_required=true");
                    throw new IllegalStateException("intentional Damage/Hit after-one rollback probe");
                }
            }
            commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            transactionEnded = true;
            requireEqual("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");
            if (mode.equals("probe-post-inner")) {
                int restoreTransaction = currentProgram.startTransaction(
                    "Restore Damage and Hit PRE metadata after post-inner probe");
                boolean restoreEnded = false;
                try {
                    for (int index = 0; index < TARGETS.size(); index++) {
                        restorePre(TARGETS.get(index), preStates.get(index));
                    }
                    boolean restoreCommitted = currentProgram.endTransaction(restoreTransaction, true);
                    restoreEnded = true;
                    requireEqual("transaction", "restore nested end committed", false, restoreCommitted);
                }
                finally {
                    if (!restoreEnded) {
                        currentProgram.endTransaction(restoreTransaction, false);
                    }
                }
                for (Target target : TARGETS) {
                    validatePre(target);
                }
                validateProgram();
                validateOuter(outerId, "after compensating PRE restore");
                println("DAMAGE_HIT_COMPENSATING_PRE_RESTORE_COMPLETE rows=2");
                println("DAMAGE_HIT_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException("intentional Damage/Hit post-inner rollback probe");
            }
            if (!mode.equals("apply")) {
                throw new IllegalStateException("unexpected mutation success mode");
            }
            for (Target target : TARGETS) {
                validatePost(target);
            }
            validateProgram();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", toolBytes,
                toolFile.getCanonicalPath(), output, outputBytes, true, nestedCommitted);
            publishPair(output, outputBytes, ready, readyBytes);
            println("DAMAGE_HIT_APPLY_COMPLETE rows=2 reopen_verification_required=true");
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
            println("DAMAGE_HIT_MUTATION_TAINTED mode=" + mode +
                " nested_committed=" + nestedCommitted +
                " outer_rollback_required=" + !mode.equals("probe-post-inner") +
                " recovery=" + (mode.equals("probe-post-inner") ?
                    "COMPENSATING_PRE_RESTORE_VERIFIED" : "RESTORE_VERIFIED_SCRATCH_BASE"));
            throw error;
        }
    }
}
