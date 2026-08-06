//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.FunctionTagManager;
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
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Apply the five evidence-adjudicated Battle Engine target-lock corrections as
 * one transaction. The exact plan hash and address set are deliberately pinned
 * here: this is not a general rename utility and cannot be pointed at another
 * cohort by changing only command-line arguments.
 *
 * Modes:
 *   dry         full preimage/proposal validation, no transaction
 *   probe-row4  apply four rows, force an exception, request one rollback
 *   probe-post-inner apply all rows, request the nested commit, then fail so
 *                the script's outer transaction must roll back
 *   apply       apply all five rows in one transaction and verify postimages
 *   readback    require the exact postimages without mutation
 */
public class GhidraApplyTargetLockCorrections extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.target-lock-semantic.v3";
    private static final String EXPECTED_PROGRAM_NAME = "BEA.exe";
    private static final String EXPECTED_PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String EXPECTED_PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String EXPECTED_IMAGE_BASE = "00400000";
    private static final String EXPECTED_LANGUAGE = "x86:LE:32:default";
    private static final String EXPECTED_COMPILER_SPEC = "windows";
    private static final String EXPECTED_MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final int EXPECTED_FUNCTION_COUNT = 8124;
    private static final int EXPECTED_INSTRUCTION_COUNT = 549872;
    private static final int EXPECTED_TARGET_COUNT = 5;
    private static final String EXPECTED_PLAN_SHA256 =
        "f6556238580a8d54b95e5603cd41e70313cebe7a9c92dff45687db7d21bc73c9";
    private static final String EXPECTED_EVIDENCE_SHA256 =
        "16c07f34feb374067ea19a9019da1f1a648778338d905928e989eced506e7ebc";
    private static final List<String> EXPECTED_ADDRESSES = Arrays.asList(
        "0x00406fc0", "0x00407060", "0x00407140", "0x004071b0", "0x00407310");
    private static final String[] HEADER = {
        "address", "expected_body_min", "expected_body_max",
        "expected_body_bytes", "expected_body_digest", "expected_body_bytes_sha256",
        "expected_instruction_count", "expected_name", "expected_namespace",
        "expected_name_source", "expected_signature_source",
        "expected_signature_sha256", "expected_prototype_key_base64",
        "expected_local_variables_key_base64", "expected_local_variables_sha256",
        "expected_call_fixup_present", "expected_call_fixup_length",
        "expected_call_fixup_sha256", "expected_frame_size", "expected_local_size",
        "expected_parameter_size", "expected_parameter_offset",
        "expected_return_address_offset",
        "expected_comment_present", "expected_comment_length",
        "expected_comment_sha256", "expected_repeatable_comment_present",
        "expected_repeatable_comment_length", "expected_repeatable_comment_sha256",
        "expected_tags", "expected_tags_sha256", "expected_tag_catalog_count",
        "expected_tag_catalog_sha256", "expected_tag_usage_sha256", "allowed_new_tags",
        "proposed_tag_catalog_count", "proposed_tag_catalog_sha256",
        "proposed_tag_usage_sha256", "proposed_name",
        "proposed_calling_convention", "proposed_return_type",
        "proposed_parameters", "proposed_signature", "proposed_comment",
        "proposed_prototype_key_base64", "proposed_comment_length", "proposed_tags"
    };

    private static class ParameterSpec {
        final String type;
        final String name;

        ParameterSpec(String type, String name) {
            this.type = type;
            this.name = name;
        }
    }

    private static class EvidenceRow {
        final String address;
        final String role;
        final String artifactPath;
        final long artifactBytes;
        final String artifactSha256;
        final String claimBoundary;

        EvidenceRow(String[] fields) {
            address = fields[0].equals("GLOBAL")
                ? "GLOBAL" : normalizeAddress(fields[0]);
            role = requireNonempty(fields[1], "evidence_role");
            artifactPath = requireNonempty(fields[2], "artifact_path");
            artifactBytes = parsePositiveLong(fields[3], "artifact_bytes");
            artifactSha256 = normalizeSha256(fields[4], "artifact_sha256");
            claimBoundary = requireNonempty(fields[5], "claim_boundary");
        }
    }

    private static class Target {
        final String address;
        final String expectedBodyMin;
        final String expectedBodyMax;
        final long expectedBodyBytes;
        final String expectedBodyDigest;
        final String expectedBodyBytesSha256;
        final long expectedInstructionCount;
        final String expectedName;
        final String expectedNamespace;
        final String expectedNameSource;
        final String expectedSignatureSource;
        final String expectedSignatureSha256;
        final String expectedPrototypeKey;
        final String expectedLocalVariablesKey;
        final String expectedLocalVariablesSha256;
        final boolean expectedCallFixupPresent;
        final long expectedCallFixupLength;
        final String expectedCallFixupSha256;
        final long expectedFrameSize;
        final long expectedLocalSize;
        final long expectedParameterSize;
        final long expectedParameterOffset;
        final long expectedReturnAddressOffset;
        final boolean expectedCommentPresent;
        final long expectedCommentLength;
        final String expectedCommentSha256;
        final boolean expectedRepeatableCommentPresent;
        final long expectedRepeatableCommentLength;
        final String expectedRepeatableCommentSha256;
        final List<String> expectedTags;
        final String expectedTagsSha256;
        final long expectedTagCatalogCount;
        final String expectedTagCatalogSha256;
        final String expectedTagUsageSha256;
        final List<String> allowedNewTags;
        final long proposedTagCatalogCount;
        final String proposedTagCatalogSha256;
        final String proposedTagUsageSha256;
        final String proposedName;
        final String proposedCallingConvention;
        final String proposedReturnType;
        final List<ParameterSpec> proposedParameters;
        final String proposedSignature;
        final String proposedPrototypeKey;
        final String proposedComment;
        final long proposedCommentLength;
        final List<String> proposedTags;

        Target(String[] fields) {
            address = normalizeAddress(fields[0]);
            expectedBodyMin = normalizeAddress(fields[1]);
            expectedBodyMax = normalizeAddress(fields[2]);
            expectedBodyBytes = parsePositiveLong(fields[3], "expected_body_bytes");
            expectedBodyDigest = normalizeSha256(fields[4], "expected_body_digest");
            expectedBodyBytesSha256 =
                normalizeSha256(fields[5], "expected_body_bytes_sha256");
            expectedInstructionCount =
                parsePositiveLong(fields[6], "expected_instruction_count");
            expectedName = requireNonempty(fields[7], "expected_name");
            expectedNamespace = requireNonempty(fields[8], "expected_namespace");
            expectedNameSource = requireNonempty(fields[9], "expected_name_source");
            expectedSignatureSource =
                requireNonempty(fields[10], "expected_signature_source");
            expectedSignatureSha256 =
                normalizeSha256(fields[11], "expected_signature_sha256");
            expectedPrototypeKey = decodeBase64(
                fields[12], "expected_prototype_key_base64");
            expectedLocalVariablesKey = decodeBase64(
                fields[13], "expected_local_variables_key_base64");
            expectedLocalVariablesSha256 =
                normalizeSha256(fields[14], "expected_local_variables_sha256");
            expectedCallFixupPresent =
                parseBoolean(fields[15], "expected_call_fixup_present");
            expectedCallFixupLength =
                parseNonnegativeLong(fields[16], "expected_call_fixup_length");
            expectedCallFixupSha256 =
                normalizeSha256(fields[17], "expected_call_fixup_sha256");
            expectedFrameSize = parseNonnegativeLong(fields[18], "expected_frame_size");
            expectedLocalSize = parseNonnegativeLong(fields[19], "expected_local_size");
            expectedParameterSize =
                parseNonnegativeLong(fields[20], "expected_parameter_size");
            expectedParameterOffset =
                parseNonnegativeLong(fields[21], "expected_parameter_offset");
            expectedReturnAddressOffset =
                parseNonnegativeLong(fields[22], "expected_return_address_offset");
            expectedCommentPresent =
                parseBoolean(fields[23], "expected_comment_present");
            expectedCommentLength =
                parseNonnegativeLong(fields[24], "expected_comment_length");
            expectedCommentSha256 =
                normalizeSha256(fields[25], "expected_comment_sha256");
            expectedRepeatableCommentPresent =
                parseBoolean(fields[26], "expected_repeatable_comment_present");
            expectedRepeatableCommentLength =
                parseNonnegativeLong(fields[27], "expected_repeatable_comment_length");
            expectedRepeatableCommentSha256 = normalizeSha256(
                fields[28], "expected_repeatable_comment_sha256");
            expectedTags = parseTags(fields[29], true, "expected_tags");
            expectedTagsSha256 = normalizeSha256(fields[30], "expected_tags_sha256");
            expectedTagCatalogCount =
                parsePositiveLong(fields[31], "expected_tag_catalog_count");
            expectedTagCatalogSha256 =
                normalizeSha256(fields[32], "expected_tag_catalog_sha256");
            expectedTagUsageSha256 =
                normalizeSha256(fields[33], "expected_tag_usage_sha256");
            allowedNewTags = parseTags(fields[34], false, "allowed_new_tags");
            proposedTagCatalogCount =
                parsePositiveLong(fields[35], "proposed_tag_catalog_count");
            proposedTagCatalogSha256 =
                normalizeSha256(fields[36], "proposed_tag_catalog_sha256");
            proposedTagUsageSha256 =
                normalizeSha256(fields[37], "proposed_tag_usage_sha256");
            proposedName = requireNonempty(fields[38], "proposed_name");
            proposedCallingConvention =
                requireNonempty(fields[39], "proposed_calling_convention");
            proposedReturnType = requireNonempty(fields[40], "proposed_return_type");
            proposedParameters = parseParameters(fields[41]);
            proposedSignature = requireNonempty(fields[42], "proposed_signature");
            proposedComment = requireNonempty(fields[43], "proposed_comment");
            proposedPrototypeKey = decodeBase64(
                fields[44], "proposed_prototype_key_base64");
            proposedCommentLength =
                parsePositiveLong(fields[45], "proposed_comment_length");
            proposedTags = parseTags(fields[46], false, "proposed_tags");
        }
    }

    private static String requireNonempty(String value, String field) {
        if (value == null || value.isEmpty()) {
            throw new IllegalArgumentException("empty " + field);
        }
        return value;
    }

    private static long parsePositiveLong(String value, String field) {
        try {
            long parsed = Long.parseLong(value);
            if (parsed <= 0) {
                throw new IllegalArgumentException(field + " must be positive");
            }
            return parsed;
        }
        catch (NumberFormatException ex) {
            throw new IllegalArgumentException("invalid " + field + ": " + value);
        }
    }

    private static long parseNonnegativeLong(String value, String field) {
        try {
            long parsed = Long.parseLong(value);
            if (parsed < 0) {
                throw new IllegalArgumentException(field + " must be nonnegative");
            }
            return parsed;
        }
        catch (NumberFormatException ex) {
            throw new IllegalArgumentException("invalid " + field + ": " + value);
        }
    }

    private static boolean parseBoolean(String value, String field) {
        if (value.equals("true")) {
            return true;
        }
        if (value.equals("false")) {
            return false;
        }
        throw new IllegalArgumentException(field + " must be exactly true or false");
    }

    private static String decodeBase64(String value, String field) {
        try {
            byte[] decoded = Base64.getDecoder().decode(requireNonempty(value, field));
            String result = new String(decoded, StandardCharsets.UTF_8);
            if (!Base64.getEncoder().encodeToString(result.getBytes(StandardCharsets.UTF_8))
                    .equals(value)) {
                throw new IllegalArgumentException("non-canonical " + field);
            }
            return result;
        }
        catch (IllegalArgumentException ex) {
            throw new IllegalArgumentException("invalid " + field, ex);
        }
    }

    private static String normalizeAddress(String value) {
        String result = value == null ? "" : value.toLowerCase(Locale.ROOT);
        if (!result.matches("0x[0-9a-f]{8}")) {
            throw new IllegalArgumentException("non-canonical address: " + value);
        }
        return result;
    }

    private static String normalizeSha256(String value, String field) {
        String result = value == null ? "" : value.toLowerCase(Locale.ROOT);
        if (!result.matches("[0-9a-f]{64}")) {
            throw new IllegalArgumentException("invalid " + field + ": " + value);
        }
        return result;
    }

    private static List<ParameterSpec> parseParameters(String value) {
        List<ParameterSpec> result = new ArrayList<>();
        if (value == null || value.isEmpty()) {
            return result;
        }
        Set<String> names = new HashSet<>();
        for (String item : value.split("\\|", -1)) {
            String[] fields = item.split(":", -1);
            if (fields.length != 2 || fields[0].isEmpty() || fields[1].isEmpty()) {
                throw new IllegalArgumentException("invalid parameter specification: " + item);
            }
            if (!Arrays.asList("void*", "float", "int", "bool").contains(fields[0])) {
                throw new IllegalArgumentException("unsupported parameter type: " + fields[0]);
            }
            if (!fields[1].matches("[A-Za-z_][A-Za-z0-9_]*") || !names.add(fields[1])) {
                throw new IllegalArgumentException("invalid or duplicate parameter name: " + fields[1]);
            }
            result.add(new ParameterSpec(fields[0], fields[1]));
        }
        return result;
    }

    private static List<String> parseTags(
            String value, boolean allowEmpty, String field) {
        if (value == null || value.isEmpty()) {
            if (allowEmpty) {
                return new ArrayList<>();
            }
            throw new IllegalArgumentException(field + " must not be empty");
        }
        List<String> result = new ArrayList<>();
        Set<String> unique = new LinkedHashSet<>();
        for (String tag : value.split(",", -1)) {
            if (tag.isEmpty() || !tag.equals(tag.trim()) || !unique.add(tag)) {
                throw new IllegalArgumentException("invalid or duplicate " + field + ": " + tag);
            }
            result.add(tag);
        }
        List<String> sorted = new ArrayList<>(result);
        Collections.sort(sorted);
        if (!result.equals(sorted)) {
            throw new IllegalArgumentException(field + " must be sorted");
        }
        return result;
    }

    private static String hex(byte[] bytes) {
        StringBuilder output = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            output.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return output.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String sha256(String value) throws Exception {
        return sha256(value.getBytes(StandardCharsets.UTF_8));
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
        List<String> sorted = new ArrayList<>(rows);
        Collections.sort(sorted);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (String row : sorted) {
            digestString(digest, row);
        }
        return hex(digest.digest());
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
            Address start = instruction.getMinAddress();
            Address end = instruction.getMaxAddress();
            if (!body.contains(start, end)) {
                throw new IllegalStateException(
                    "instruction crosses expected body at " + label + ": " + start + "-" + end);
            }
            covered.addRange(start, end);
            count++;
        }
        if (!covered.hasSameAddresses(body)) {
            throw new IllegalStateException("instruction coverage differs at " + label);
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

    private long programFunctionCount() {
        long count = 0;
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            functions.next();
            count++;
        }
        return count;
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
                        "short initialized-memory read at " + cursor);
                }
                digest.update(chunk);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    private static List<String> currentTagNames(Function function) {
        List<String> names = new ArrayList<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        Collections.sort(names);
        return names;
    }

    private static String signature(Function function) {
        return function.getSignature().getPrototypeString(true);
    }

    private static String prototypeKey(Function function) {
        StringBuilder result = new StringBuilder();
        result.append("cc=").append(function.getCallingConventionName());
        result.append("|custom=").append(function.hasCustomVariableStorage());
        result.append("|varargs=").append(function.hasVarArgs());
        result.append("|noreturn=").append(function.hasNoReturn());
        result.append("|inline=").append(function.isInline());
        result.append("|purge=").append(function.getStackPurgeSize());
        result.append("|purgeValid=").append(function.isStackPurgeSizeValid());
        result.append("|autoCount=").append(function.getAutoParameterCount());
        Parameter ret = function.getReturn();
        result.append("|return=").append(ret.getDataType().getPathName());
        result.append('/').append(ret.getFormalDataType().getPathName());
        result.append('@').append(ret.getVariableStorage());
        result.append(":forced=").append(ret.isForcedIndirect());
        result.append(":source=").append(ret.getSource());
        result.append(":commentPresent=").append(ret.getComment() != null);
        result.append(":commentLength=").append(
            ret.getComment() == null ? 0 : ret.getComment().length());
        result.append(":commentBase64=").append(Base64.getEncoder().encodeToString(
            (ret.getComment() == null ? "" : ret.getComment())
                .getBytes(StandardCharsets.UTF_8)));
        result.append("|params=");
        Parameter[] parameters = function.getParameters();
        for (int index = 0; index < parameters.length; ++index) {
            if (index > 0) {
                result.append(';');
            }
            Parameter parameter = parameters[index];
            result.append(parameter.getOrdinal()).append(':').append(parameter.getName());
            result.append(':').append(parameter.getDataType().getPathName());
            result.append('/').append(parameter.getFormalDataType().getPathName());
            result.append('@').append(parameter.getVariableStorage());
            result.append(":auto=").append(parameter.isAutoParameter());
            result.append(":autoType=").append(parameter.getAutoParameterType());
            result.append(":forced=").append(parameter.isForcedIndirect());
            result.append(":source=").append(parameter.getSource());
            result.append(":commentPresent=").append(parameter.getComment() != null);
            result.append(":commentLength=").append(
                parameter.getComment() == null ? 0 : parameter.getComment().length());
            result.append(":commentBase64=").append(Base64.getEncoder().encodeToString(
                (parameter.getComment() == null ? "" : parameter.getComment())
                    .getBytes(StandardCharsets.UTF_8)));
        }
        return result.toString();
    }

    private static String nullableText(String value) {
        return value == null ? "" : value;
    }

    private static String namespace(Function function) {
        return function.getParentNamespace().getName(true);
    }

    private static List<String> tagDefinitions(FunctionTagManager manager) {
        List<String> definitions = new ArrayList<>();
        for (FunctionTag tag : manager.getAllFunctionTags()) {
            String comment = tag.getComment();
            definitions.add(tag.getName() + "\u0000" + (comment != null) + "\u0000" +
                nullableText(comment));
        }
        Collections.sort(definitions);
        return definitions;
    }

    private static List<String> tagUsage(FunctionTagManager manager) {
        List<String> usage = new ArrayList<>();
        for (FunctionTag tag : manager.getAllFunctionTags()) {
            usage.add(tag.getName() + "\u0000" + manager.getUseCount(tag));
        }
        Collections.sort(usage);
        return usage;
    }

    private static List<String> tagNames(FunctionTagManager manager) {
        List<String> names = new ArrayList<>();
        for (FunctionTag tag : manager.getAllFunctionTags()) {
            names.add(tag.getName());
        }
        Collections.sort(names);
        return names;
    }

    private static void requireEqual(
            String address, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(
                "mismatch at " + address + " field=" + field +
                " expected=" + expected + " actual=" + actual);
        }
    }

    private static List<Target> loadPlan(byte[] planBytes) throws Exception {
        String text = new String(planBytes, StandardCharsets.UTF_8);
        if (!Arrays.equals(planBytes, text.getBytes(StandardCharsets.UTF_8))) {
            throw new IllegalArgumentException("target-lock plan is not canonical UTF-8");
        }
        if (text.indexOf('\r') >= 0 || !text.endsWith("\n")) {
            throw new IllegalArgumentException(
                "target-lock plan must use LF line endings with one final LF");
        }
        String[] rawLines = text.substring(0, text.length() - 1).split("\n", -1);
        List<String> lines = Arrays.asList(rawLines);
        if (lines.isEmpty() || !lines.get(0).equals(String.join("\t", HEADER))) {
            throw new IllegalArgumentException("target-lock plan header mismatch");
        }
        List<Target> targets = new ArrayList<>();
        for (int index = 1; index < lines.size(); ++index) {
            String line = lines.get(index);
            if (line.isEmpty()) {
                throw new IllegalArgumentException("blank plan row at line " + (index + 1));
            }
            String[] fields = line.split("\t", -1);
            if (fields.length != HEADER.length) {
                throw new IllegalArgumentException(
                    "plan column count mismatch at line " + (index + 1));
            }
            targets.add(new Target(fields));
        }
        if (targets.size() != EXPECTED_TARGET_COUNT) {
            throw new IllegalArgumentException(
                "target-lock row count mismatch expected=" + EXPECTED_TARGET_COUNT +
                " actual=" + targets.size());
        }
        List<String> addresses = new ArrayList<>();
        for (Target target : targets) {
            addresses.add(target.address);
        }
        if (!addresses.equals(EXPECTED_ADDRESSES)) {
            throw new IllegalArgumentException("target-lock address set/order mismatch");
        }
        return targets;
    }

    private List<EvidenceRow> loadEvidence(
            byte[] evidenceBytes, File repositoryRoot) throws Exception {
        String text = new String(evidenceBytes, StandardCharsets.UTF_8);
        if (!Arrays.equals(evidenceBytes, text.getBytes(StandardCharsets.UTF_8))) {
            throw new IllegalArgumentException("evidence manifest is not canonical UTF-8");
        }
        if (text.indexOf('\r') >= 0 || !text.endsWith("\n")) {
            throw new IllegalArgumentException(
                "evidence manifest must use LF line endings with one final LF");
        }
        String[] lines = text.substring(0, text.length() - 1).split("\n", -1);
        String expectedHeader =
            "address\tevidence_role\tartifact_path\tartifact_bytes\tartifact_sha256\t" +
            "claim_boundary";
        if (lines.length < 2 || !lines[0].equals(expectedHeader)) {
            throw new IllegalArgumentException("evidence manifest header/row count differs");
        }
        List<String> rawRows = new ArrayList<>();
        List<EvidenceRow> rows = new ArrayList<>();
        Set<String> unique = new HashSet<>();
        Set<String> covered = new HashSet<>();
        boolean hasGlobal = false;
        boolean hasCurrentLockHit = false;
        String rootPrefix = repositoryRoot.getCanonicalPath() + File.separator;
        for (int index = 1; index < lines.length; ++index) {
            String line = lines[index];
            if (line.isEmpty()) {
                throw new IllegalArgumentException(
                    "blank evidence row at line " + (index + 1));
            }
            String[] fields = line.split("\t", -1);
            if (fields.length != 6) {
                throw new IllegalArgumentException(
                    "evidence column count mismatch at line " + (index + 1));
            }
            EvidenceRow row = new EvidenceRow(fields);
            if (!row.role.matches("[a-z0-9][a-z0-9_-]*")) {
                throw new IllegalArgumentException("non-canonical evidence role: " + row.role);
            }
            if (row.artifactPath.indexOf('\\') >= 0 ||
                    row.artifactPath.startsWith("/") ||
                    row.artifactPath.contains(":") ||
                    row.artifactPath.contains("//") ||
                    row.artifactPath.equals(".") ||
                    row.artifactPath.startsWith("./") ||
                    row.artifactPath.contains("/../") ||
                    row.artifactPath.startsWith("../") ||
                    row.artifactPath.endsWith("/..")) {
                throw new IllegalArgumentException(
                    "non-canonical evidence artifact path: " + row.artifactPath);
            }
            if (row.artifactPath.contains(
                    "ttd-data-writes-level521-lock-state-20260803-v1")) {
                throw new IllegalArgumentException(
                    "historical lock-state lane is forbidden as current authority");
            }
            File artifact = new File(
                repositoryRoot, row.artifactPath.replace('/', File.separatorChar))
                    .getCanonicalFile();
            if (!artifact.getPath().startsWith(rootPrefix) || !artifact.isFile() ||
                    Files.isSymbolicLink(artifact.toPath())) {
                throw new IllegalArgumentException(
                    "evidence artifact escapes repository or is absent: " + row.artifactPath);
            }
            requireEqual(row.address, "evidence_bytes", row.artifactBytes,
                Files.size(artifact.toPath()));
            requireEqual(row.address, "evidence_sha256", row.artifactSha256,
                sha256(Files.readAllBytes(artifact.toPath())));
            String key = row.address + "\u0000" + row.role + "\u0000" + row.artifactPath;
            if (!unique.add(key)) {
                throw new IllegalArgumentException("duplicate evidence key: " + key);
            }
            if (row.address.equals("GLOBAL")) {
                hasGlobal = true;
            }
            else {
                covered.add(row.address);
            }
            if (row.address.equals("0x00407140") && row.artifactPath.contains(
                    "ttd-data-writes-level521-lockhit-removal-20260803-v1/" +
                    "run-e-v3-source-bound/")) {
                hasCurrentLockHit = true;
            }
            rawRows.add(line);
            rows.add(row);
        }
        List<String> sorted = new ArrayList<>(rawRows);
        Collections.sort(sorted);
        requireEqual("evidence", "canonical_row_order", sorted, rawRows);
        requireEqual("evidence", "address_coverage",
            new HashSet<>(EXPECTED_ADDRESSES), covered);
        requireEqual("evidence", "global_evidence_present", true, hasGlobal);
        requireEqual("evidence", "current_lockhit_authority_present", true,
            hasCurrentLockHit);
        println("EVIDENCE_OK rows=" + rows.size() + " artifacts=" + unique.size());
        return rows;
    }

    private Function exactFunction(String addressText) {
        Address address = toAddr(addressText);
        Function function = getFunctionAt(address);
        if (function == null || !function.getEntryPoint().equals(address)) {
            throw new IllegalStateException("exact function missing at " + addressText);
        }
        return function;
    }

    private void validateProgram() throws Exception {
        if (currentProgram == null) {
            throw new IllegalStateException("no current program");
        }
        requireEqual("program", "name", EXPECTED_PROGRAM_NAME, currentProgram.getName());
        requireEqual(
            "program", "executable_md5", EXPECTED_PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        requireEqual(
            "program", "executable_sha256", EXPECTED_PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        requireEqual(
            "program", "image_base", EXPECTED_IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        requireEqual(
            "program", "language", EXPECTED_LANGUAGE,
            currentProgram.getLanguageID().toString());
        requireEqual(
            "program", "compiler_spec", EXPECTED_COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        requireEqual(
            "program", "memory_sha256", EXPECTED_MEMORY_SHA256, memoryDigest());
        requireEqual(
            "program", "instruction_count", (long) EXPECTED_INSTRUCTION_COUNT,
            programInstructionCount());
        requireEqual(
            "program", "internal_function_count", (long) EXPECTED_FUNCTION_COUNT,
            programFunctionCount());
    }

    private void validateProposal(Target target) {
        if (!target.proposedCallingConvention.equals("__thiscall")) {
            throw new IllegalArgumentException(
                "unsupported proposed calling convention at " + target.address);
        }
        if (!Arrays.asList("void", "void*", "bool", "int", "float")
                .contains(target.proposedReturnType)) {
            throw new IllegalArgumentException(
                "unsupported proposed return type at " + target.address);
        }
        if (target.proposedParameters.isEmpty() ||
                !target.proposedParameters.get(0).type.equals("void*") ||
                !target.proposedParameters.get(0).name.equals("this")) {
            throw new IllegalArgumentException(
                "every target-lock prototype must begin with void*:this at " +
                target.address);
        }
        if (target.proposedComment.length() != target.proposedCommentLength) {
            throw new IllegalArgumentException(
                "proposed comment length differs at " + target.address);
        }
        try {
            requireEqual(target.address, "expected_tags_manifest_hash",
                target.expectedTagsSha256, sortedDigest(target.expectedTags));
            requireEqual(target.address, "expected_locals_manifest_hash",
                target.expectedLocalVariablesSha256,
                sha256(target.expectedLocalVariablesKey));
        }
        catch (Exception ex) {
            throw new IllegalArgumentException(
                "cannot validate expected tags at " + target.address, ex);
        }
        if (!target.expectedCommentPresent && target.expectedCommentLength != 0) {
            throw new IllegalArgumentException(
                "expected comment presence/length is inconsistent at " + target.address);
        }
        if (!target.expectedRepeatableCommentPresent &&
                target.expectedRepeatableCommentLength != 0) {
            throw new IllegalArgumentException(
                "expected repeatable comment presence/length is inconsistent at " +
                target.address);
        }
        if (!target.expectedCallFixupPresent && target.expectedCallFixupLength != 0) {
            throw new IllegalArgumentException(
                "expected call-fixup presence/length is inconsistent at " + target.address);
        }
    }

    private void validatePlanGlobals(List<Target> targets) {
        Target first = targets.get(0);
        for (Target target : targets) {
            requireEqual(target.address, "expected_tag_catalog_count",
                first.expectedTagCatalogCount, target.expectedTagCatalogCount);
            requireEqual(target.address, "expected_tag_catalog_sha256",
                first.expectedTagCatalogSha256, target.expectedTagCatalogSha256);
            requireEqual(target.address, "expected_tag_usage_sha256",
                first.expectedTagUsageSha256, target.expectedTagUsageSha256);
            requireEqual(target.address, "allowed_new_tags",
                first.allowedNewTags, target.allowedNewTags);
            requireEqual(target.address, "proposed_tag_catalog_count",
                first.proposedTagCatalogCount, target.proposedTagCatalogCount);
            requireEqual(target.address, "proposed_tag_catalog_sha256",
                first.proposedTagCatalogSha256, target.proposedTagCatalogSha256);
            requireEqual(target.address, "proposed_tag_usage_sha256",
                first.proposedTagUsageSha256, target.proposedTagUsageSha256);
        }
        requireEqual("plan", "proposed_tag_catalog_count",
            first.expectedTagCatalogCount + first.allowedNewTags.size(),
            first.proposedTagCatalogCount);
    }

    private void validateCatalog(List<Target> targets, boolean post) throws Exception {
        Target first = targets.get(0);
        FunctionTagManager manager =
            currentProgram.getFunctionManager().getFunctionTagManager();
        List<String> definitions = tagDefinitions(manager);
        List<String> usage = tagUsage(manager);
        long expectedCount = post
            ? first.proposedTagCatalogCount : first.expectedTagCatalogCount;
        String expectedSha = post
            ? first.proposedTagCatalogSha256 : first.expectedTagCatalogSha256;
        String expectedUsageSha = post
            ? first.proposedTagUsageSha256 : first.expectedTagUsageSha256;
        requireEqual("catalog", "count", expectedCount, (long) definitions.size());
        requireEqual("catalog", "sha256", expectedSha, sortedDigest(definitions));
        requireEqual("catalog", "usage_sha256", expectedUsageSha, sortedDigest(usage));

        Set<String> proposedUnion = new HashSet<>();
        for (Target target : targets) {
            proposedUnion.addAll(target.proposedTags);
        }
        Set<String> missing = new HashSet<>();
        for (String name : proposedUnion) {
            if (manager.getFunctionTag(name) == null) {
                missing.add(name);
            }
        }
        Set<String> allowed = new HashSet<>(first.allowedNewTags);
        requireEqual("catalog", "missing_proposed_tags",
            post ? Collections.emptySet() : allowed, missing);
        requireEqual("catalog", "allowed_new_tags_are_proposed", true,
            proposedUnion.containsAll(allowed));

        if (!post) {
            List<String> predicted = new ArrayList<>(definitions);
            Map<String, Integer> predictedUsageCounts = new HashMap<>();
            for (FunctionTag tag : manager.getAllFunctionTags()) {
                predictedUsageCounts.put(tag.getName(), manager.getUseCount(tag));
            }
            for (String name : first.allowedNewTags) {
                requireEqual("catalog", "allowed_tag_absent_" + name, null,
                    manager.getFunctionTag(name));
                predicted.add(name + "\u0000true\u0000");
                predictedUsageCounts.put(name, 0);
            }
            for (Target target : targets) {
                for (String name : target.expectedTags) {
                    Integer count = predictedUsageCounts.get(name);
                    if (count == null || count <= 0) {
                        throw new IllegalStateException(
                            "cannot predict tag removal at " + target.address + ": " + name);
                    }
                    predictedUsageCounts.put(name, count - 1);
                }
                for (String name : target.proposedTags) {
                    Integer count = predictedUsageCounts.get(name);
                    if (count == null) {
                        throw new IllegalStateException(
                            "cannot predict tag addition at " + target.address + ": " + name);
                    }
                    predictedUsageCounts.put(name, count + 1);
                }
            }
            List<String> predictedUsage = new ArrayList<>();
            for (Map.Entry<String, Integer> entry : predictedUsageCounts.entrySet()) {
                predictedUsage.add(entry.getKey() + "\u0000" + entry.getValue());
            }
            requireEqual("catalog", "predicted_post_count",
                first.proposedTagCatalogCount, (long) predicted.size());
            requireEqual("catalog", "predicted_post_sha256",
                first.proposedTagCatalogSha256, sortedDigest(predicted));
            requireEqual("catalog", "predicted_post_usage_sha256",
                first.proposedTagUsageSha256, sortedDigest(predictedUsage));
        }
        println("CATALOG_OK state=" + (post ? "POST" : "PRE") +
            " count=" + definitions.size() + " sha256=" + expectedSha +
            " usage_sha256=" + expectedUsageSha);
    }

    private void preflight(List<Target> targets) throws Exception {
        validatePlanGlobals(targets);
        validateCatalog(targets, false);
        Set<String> proposedNames = new HashSet<>();
        for (Target target : targets) {
            monitor.checkCancelled();
            validateProposal(target);
            if (!proposedNames.add(target.proposedName)) {
                throw new IllegalArgumentException(
                    "duplicate proposed name: " + target.proposedName);
            }
            Function function = exactFunction(target.address);
            AddressSetView body = function.getBody();
            requireEqual(target.address, "body_min", target.expectedBodyMin,
                "0x" + body.getMinAddress().toString());
            requireEqual(target.address, "body_max", target.expectedBodyMax,
                "0x" + body.getMaxAddress().toString());
            requireEqual(target.address, "body_bytes", target.expectedBodyBytes,
                body.getNumAddresses());
            requireEqual(target.address, "body_ranges", 1L,
                (long) body.getNumAddressRanges());
            requireEqual(target.address, "body_digest", target.expectedBodyDigest,
                bodyDigest(body));
            requireEqual(target.address, "body_bytes_sha256",
                target.expectedBodyBytesSha256, bodyBytesSha256(body));
            requireEqual(target.address, "instruction_count",
                target.expectedInstructionCount,
                validatedInstructionCount(body, target.address));
            for (AddressRange range : body) {
                MemoryBlock firstBlock = currentProgram.getMemory().getBlock(range.getMinAddress());
                MemoryBlock lastBlock = currentProgram.getMemory().getBlock(range.getMaxAddress());
                requireEqual(target.address, "body_memory_block_identity", firstBlock, lastBlock);
                requireEqual(target.address, "body_memory_block_name", ".text",
                    firstBlock == null ? "" : firstBlock.getName());
                requireEqual(target.address, "body_memory_block_execute", true,
                    firstBlock != null && firstBlock.isExecute());
                requireEqual(target.address, "body_memory_block_initialized", true,
                    firstBlock != null && firstBlock.isInitialized());
            }
            requireEqual(target.address, "is_thunk", false, function.isThunk());
            requireEqual(target.address, "is_external", false, function.isExternal());
            requireEqual(target.address, "name", target.expectedName, function.getName());
            requireEqual(target.address, "namespace", target.expectedNamespace,
                namespace(function));
            requireEqual(target.address, "name_source", target.expectedNameSource,
                function.getSymbol().getSource().toString());
            requireEqual(target.address, "signature_source", target.expectedSignatureSource,
                function.getSignatureSource().toString());
            requireEqual(target.address, "signature_sha256", target.expectedSignatureSha256,
                sha256(signature(function)));
            requireEqual(target.address, "prototype_key", target.expectedPrototypeKey,
                prototypeKey(function));
            String locals = localVariablesKey(function);
            requireEqual(target.address, "local_variables_key",
                target.expectedLocalVariablesKey, locals);
            requireEqual(target.address, "local_variables_sha256",
                target.expectedLocalVariablesSha256, sha256(locals));
            String callFixup = function.getCallFixup();
            requireEqual(target.address, "call_fixup_present",
                target.expectedCallFixupPresent, callFixup != null);
            requireEqual(target.address, "call_fixup_length",
                target.expectedCallFixupLength, (long) nullableText(callFixup).length());
            requireEqual(target.address, "call_fixup_sha256",
                target.expectedCallFixupSha256, sha256(nullableText(callFixup)));
            requireEqual(target.address, "frame_size", target.expectedFrameSize,
                (long) function.getStackFrame().getFrameSize());
            requireEqual(target.address, "local_size", target.expectedLocalSize,
                (long) function.getStackFrame().getLocalSize());
            requireEqual(target.address, "parameter_size", target.expectedParameterSize,
                (long) function.getStackFrame().getParameterSize());
            requireEqual(target.address, "parameter_offset", target.expectedParameterOffset,
                (long) function.getStackFrame().getParameterOffset());
            requireEqual(target.address, "return_address_offset",
                target.expectedReturnAddressOffset,
                (long) function.getStackFrame().getReturnAddressOffset());
            String plate = function.getComment();
            requireEqual(target.address, "comment_present", target.expectedCommentPresent,
                plate != null);
            requireEqual(target.address, "comment_length", target.expectedCommentLength,
                (long) nullableText(plate).length());
            requireEqual(target.address, "comment_sha256", target.expectedCommentSha256,
                sha256(nullableText(plate)));
            String repeatable = function.getRepeatableComment();
            requireEqual(target.address, "repeatable_comment_present",
                target.expectedRepeatableCommentPresent, repeatable != null);
            requireEqual(target.address, "repeatable_comment_length",
                target.expectedRepeatableCommentLength,
                (long) nullableText(repeatable).length());
            requireEqual(target.address, "repeatable_comment_sha256",
                target.expectedRepeatableCommentSha256,
                sha256(nullableText(repeatable)));
            requireEqual(target.address, "tags", target.expectedTags,
                currentTagNames(function));
            requireEqual(target.address, "tags_sha256", target.expectedTagsSha256,
                sortedDigest(currentTagNames(function)));
        }

        int internalFunctionCount = 0;
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            Function function = functions.next();
            ++internalFunctionCount;
            if (proposedNames.contains(function.getName())) {
                throw new IllegalStateException(
                    "proposed name already exists at " + function.getEntryPoint() +
                    ": " + function.getName());
            }
        }
        requireEqual(
            "program", "internal_function_count", EXPECTED_FUNCTION_COUNT,
            internalFunctionCount);
        println("PREFLIGHT_OK rows=" + targets.size());
    }

    private DataType dataType(String name) {
        if (name.equals("void")) {
            return VoidDataType.dataType;
        }
        if (name.equals("void*")) {
            return new PointerDataType(
                VoidDataType.dataType, currentProgram.getDataTypeManager());
        }
        if (name.equals("bool")) {
            return BooleanDataType.dataType;
        }
        if (name.equals("int")) {
            return IntegerDataType.dataType;
        }
        if (name.equals("float")) {
            return FloatDataType.dataType;
        }
        throw new IllegalArgumentException("unsupported data type: " + name);
    }

    private static String localVariablesKey(Function function) {
        StringBuilder result = new StringBuilder();
        Variable[] locals = function.getLocalVariables();
        result.append("count=").append(locals.length);
        for (int index = 0; index < locals.length; ++index) {
            Variable local = locals[index];
            String comment = local.getComment();
            result.append('|').append(index).append(':');
            result.append(nullableText(local.getName())).append(':');
            result.append(local.getDataType().getPathName()).append('@');
            result.append(local.getVariableStorage()).append(':');
            result.append(local.getSource()).append(':');
            result.append(local.getLength()).append(':');
            result.append(local.getFirstUseOffset()).append(':');
            result.append(local.isValid()).append(':');
            result.append(comment != null).append(':');
            result.append(nullableText(comment).length()).append(':');
            result.append(Base64.getEncoder().encodeToString(
                nullableText(comment).getBytes(StandardCharsets.UTF_8)));
        }
        return result.toString();
    }

    private void createAllowedTags(
            List<Target> targets, FunctionTagManager tagManager) throws Exception {
        for (String name : targets.get(0).allowedNewTags) {
            requireEqual("catalog", "pre_create_absent_" + name, null,
                tagManager.getFunctionTag(name));
            FunctionTag created = tagManager.createFunctionTag(name, "");
            if (created == null) {
                throw new IllegalStateException("failed to create exact allowed tag: " + name);
            }
            requireEqual("catalog", "created_tag_name", name, created.getName());
            requireEqual("catalog", "created_tag_comment_present_" + name, true,
                created.getComment() != null);
            requireEqual("catalog", "created_tag_comment_" + name, "",
                nullableText(created.getComment()));
        }
    }

    private void applyTarget(Target target, FunctionTagManager tagManager) throws Exception {
        Function function = exactFunction(target.address);
        String localsBefore = localVariablesKey(function);
        String repeatableBefore = function.getRepeatableComment();
        String callFixupBefore = function.getCallFixup();

        Variable[] parameters = new Variable[target.proposedParameters.size()];
        for (int index = 0; index < parameters.length; ++index) {
            ParameterSpec spec = target.proposedParameters.get(index);
            parameters[index] =
                new ParameterImpl(spec.name, dataType(spec.type), currentProgram);
        }
        function.updateFunction(
            target.proposedCallingConvention,
            new ReturnParameterImpl(dataType(target.proposedReturnType), currentProgram),
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            false,
            SourceType.USER_DEFINED,
            parameters);
        function.setName(target.proposedName, SourceType.USER_DEFINED);
        function.setComment(target.proposedComment);

        for (String existing : currentTagNames(function)) {
            function.removeTag(existing);
        }
        for (String name : target.proposedTags) {
            if (tagManager.getFunctionTag(name) == null) {
                throw new IllegalStateException(
                    "proposed tag was not pre-existing or explicitly created: " + name);
            }
            if (!function.addTag(name)) {
                throw new IllegalStateException(
                    "failed to attach exact proposed tag " + name + " at " + target.address);
            }
        }

        requireEqual(target.address, "locals_preserved", localsBefore,
            localVariablesKey(function));
        requireEqual(target.address, "repeatable_comment_preserved", repeatableBefore,
            function.getRepeatableComment());
        requireEqual(target.address, "call_fixup_preserved", callFixupBefore,
            function.getCallFixup());
        readBackTarget(target);
        println("ROW_APPLIED address=" + target.address + " force=false");
    }

    private void readBackTarget(Target target) throws Exception {
        Function function = exactFunction(target.address);
        AddressSetView body = function.getBody();
        requireEqual(target.address, "post_body_min", target.expectedBodyMin,
            "0x" + body.getMinAddress().toString());
        requireEqual(target.address, "post_body_max", target.expectedBodyMax,
            "0x" + body.getMaxAddress().toString());
        requireEqual(target.address, "post_body_bytes", target.expectedBodyBytes,
            body.getNumAddresses());
        requireEqual(target.address, "post_body_ranges", 1L,
            (long) body.getNumAddressRanges());
        requireEqual(target.address, "post_body_digest", target.expectedBodyDigest,
            bodyDigest(body));
        requireEqual(target.address, "post_body_bytes_sha256",
            target.expectedBodyBytesSha256, bodyBytesSha256(body));
        requireEqual(target.address, "post_instruction_count",
            target.expectedInstructionCount, validatedInstructionCount(body, target.address));
        requireEqual(target.address, "post_is_thunk", false, function.isThunk());
        requireEqual(target.address, "post_is_external", false, function.isExternal());
        requireEqual(target.address, "post_namespace", target.expectedNamespace,
            namespace(function));
        requireEqual(target.address, "post_name", target.proposedName, function.getName());
        requireEqual(target.address, "post_name_source", SourceType.USER_DEFINED.toString(),
            function.getSymbol().getSource().toString());
        requireEqual(target.address, "post_signature_source",
            SourceType.USER_DEFINED.toString(), function.getSignatureSource().toString());
        requireEqual(target.address, "post_calling_convention",
            target.proposedCallingConvention, function.getCallingConventionName());
        requireEqual(target.address, "post_signature", target.proposedSignature,
            signature(function));
        requireEqual(target.address, "post_signature_sha256", sha256(target.proposedSignature),
            sha256(signature(function)));
        requireEqual(target.address, "post_prototype_key", target.proposedPrototypeKey,
            prototypeKey(function));
        String locals = localVariablesKey(function);
        requireEqual(target.address, "post_local_variables_key",
            target.expectedLocalVariablesKey, locals);
        requireEqual(target.address, "post_local_variables_sha256",
            target.expectedLocalVariablesSha256, sha256(locals));
        String callFixup = function.getCallFixup();
        requireEqual(target.address, "post_call_fixup_present",
            target.expectedCallFixupPresent, callFixup != null);
        requireEqual(target.address, "post_call_fixup_length",
            target.expectedCallFixupLength, (long) nullableText(callFixup).length());
        requireEqual(target.address, "post_call_fixup_sha256",
            target.expectedCallFixupSha256, sha256(nullableText(callFixup)));
        requireEqual(target.address, "post_frame_size", target.expectedFrameSize,
            (long) function.getStackFrame().getFrameSize());
        requireEqual(target.address, "post_local_size", target.expectedLocalSize,
            (long) function.getStackFrame().getLocalSize());
        requireEqual(target.address, "post_parameter_size", target.expectedParameterSize,
            (long) function.getStackFrame().getParameterSize());
        requireEqual(target.address, "post_parameter_offset", target.expectedParameterOffset,
            (long) function.getStackFrame().getParameterOffset());
        requireEqual(target.address, "post_return_address_offset",
            target.expectedReturnAddressOffset,
            (long) function.getStackFrame().getReturnAddressOffset());

        String plate = function.getComment();
        requireEqual(target.address, "post_comment_present", true, plate != null);
        requireEqual(target.address, "post_comment_length", target.proposedCommentLength,
            (long) nullableText(plate).length());
        requireEqual(target.address, "post_comment_sha256", sha256(target.proposedComment),
            sha256(nullableText(plate)));
        requireEqual(target.address, "post_comment", target.proposedComment,
            nullableText(plate));
        String repeatable = function.getRepeatableComment();
        requireEqual(target.address, "post_repeatable_comment_present",
            target.expectedRepeatableCommentPresent, repeatable != null);
        requireEqual(target.address, "post_repeatable_comment_length",
            target.expectedRepeatableCommentLength,
            (long) nullableText(repeatable).length());
        requireEqual(target.address, "post_repeatable_comment_sha256",
            target.expectedRepeatableCommentSha256, sha256(nullableText(repeatable)));
        requireEqual(target.address, "post_tags", target.proposedTags,
            currentTagNames(function));
        requireEqual(target.address, "post_tags_sha256", sortedDigest(target.proposedTags),
            sortedDigest(currentTagNames(function)));
    }

    private void readBackAll(List<Target> targets) throws Exception {
        for (Target target : targets) {
            monitor.checkCancelled();
            readBackTarget(target);
            int nameMatches = 0;
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                Function function = functions.next();
                if (function.getName().equals(target.proposedName)) {
                    ++nameMatches;
                    requireEqual(target.address, "post_name_owner", target.address,
                        "0x" + function.getEntryPoint().toString());
                }
            }
            requireEqual(target.address, "post_name_match_count", 1L, (long) nameMatches);
            println("READBACK_OK address=" + target.address);
        }
        requireEqual("program", "post_internal_function_count",
            (long) EXPECTED_FUNCTION_COUNT, programFunctionCount());
    }

    private static String requireMode(String value) {
        if (Arrays.asList(
                "dry", "probe-row4", "probe-post-inner", "apply", "readback")
                .contains(value)) {
            return value;
        }
        throw new IllegalArgumentException(
            "mode must be dry, probe-row4, probe-post-inner, apply, or readback");
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File file = new File(value).getCanonicalFile();
        if (file.exists()) {
            throw new IllegalArgumentException(label + " already exists: " + file);
        }
        File parent = file.getParentFile();
        if (parent == null || !parent.isDirectory()) {
            throw new IllegalArgumentException(
                label + " parent is not an existing directory: " + file);
        }
        return file;
    }

    private static void preflightAtomicWrite(File target, String label) throws Exception {
        File parent = target.getParentFile();
        File source = new File(
            parent, "." + target.getName() + ".write-probe-" + UUID.randomUUID());
        File linked = new File(
            parent, "." + target.getName() + ".link-probe-" + UUID.randomUUID());
        try {
            Files.write(source.toPath(), new byte[] { 0 },
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
            Files.createLink(linked.toPath(), source.toPath());
        }
        catch (Exception ex) {
            throw new IllegalStateException(
                label + " parent cannot publish a create-new receipt: " + parent, ex);
        }
        finally {
            Files.deleteIfExists(source.toPath());
            Files.deleteIfExists(linked.toPath());
        }
    }

    private static File stageAtomic(File target, byte[] content) throws Exception {
        File partial = new File(
            target.getParentFile(), "." + target.getName() + ".partial-" + UUID.randomUUID());
        try (FileChannel channel = FileChannel.open(
                partial.toPath(), StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            ByteBuffer buffer = ByteBuffer.wrap(content);
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
            channel.force(true);
        }
        return partial;
    }

    private static void publishStaged(File partial, File target) throws Exception {
        if (!partial.getParentFile().equals(target.getParentFile())) {
            throw new IllegalStateException(
                "staged and final receipts must share one directory");
        }
        Files.createLink(target.toPath(), partial.toPath());
        try {
            Files.deleteIfExists(partial.toPath());
        }
        catch (Exception ignored) {
            // The create-new hardlink is the publication boundary. A stale
            // same-content partial is cleanup debt, not publication failure.
        }
    }

    private static void discardStaged(File partial) {
        if (partial != null) {
            try {
                Files.deleteIfExists(partial.toPath());
            }
            catch (Exception ignored) {
                // Partials are never authority; do not mask the causal error.
            }
        }
    }

    private static void deleteExactPublished(
            File target, byte[] expected, Exception causal) {
        try {
            if (target.isFile() &&
                    sha256(Files.readAllBytes(target.toPath())).equals(sha256(expected))) {
                Files.delete(target.toPath());
            }
        }
        catch (Exception cleanup) {
            causal.addSuppressed(cleanup);
        }
    }

    private static String json(String value) {
        StringBuilder output = new StringBuilder();
        for (int index = 0; index < value.length(); ++index) {
            char ch = value.charAt(index);
            switch (ch) {
                case '\\': output.append("\\\\"); break;
                case '"': output.append("\\\""); break;
                case '\b': output.append("\\b"); break;
                case '\f': output.append("\\f"); break;
                case '\n': output.append("\\n"); break;
                case '\r': output.append("\\r"); break;
                case '\t': output.append("\\t"); break;
                default:
                    if (ch < 0x20) {
                        output.append(String.format(Locale.ROOT, "\\u%04x", (int) ch));
                    }
                    else {
                        output.append(ch);
                    }
            }
        }
        return output.toString();
    }

    private byte[] buildOutput(
            List<Target> targets, String mode, String state, String status) throws Exception {
        StringBuilder output = new StringBuilder();
        output.append(
            "address\tmode\tstate\tstatus\tname\tnamespace\tname_source\t" +
            "signature_source\tsignature_sha256\tprototype_key_base64\t" +
            "local_variables_key_base64\tlocal_variables_sha256\t" +
            "call_fixup_present\tcall_fixup_length\tcall_fixup_sha256\t" +
            "frame_size\tlocal_size\tparameter_size\tparameter_offset\t" +
            "return_address_offset\t" +
            "comment_present\tcomment_length\tcomment_sha256\t" +
            "repeatable_comment_present\trepeatable_comment_length\t" +
            "repeatable_comment_sha256\ttags\ttags_sha256\tbody_min\tbody_max\t" +
            "body_bytes\tbody_digest\tbody_bytes_sha256\tinstruction_count\n");
        for (Target target : targets) {
            Function function = exactFunction(target.address);
            AddressSetView body = function.getBody();
            String plate = function.getComment();
            String repeatable = function.getRepeatableComment();
            String locals = localVariablesKey(function);
            String callFixup = function.getCallFixup();
            List<String> tags = currentTagNames(function);
            output.append(target.address).append('\t').append(mode).append('\t')
                .append(state).append('\t').append(status).append('\t')
                .append(function.getName()).append('\t').append(namespace(function)).append('\t')
                .append(function.getSymbol().getSource()).append('\t')
                .append(function.getSignatureSource()).append('\t')
                .append(sha256(signature(function))).append('\t')
                .append(Base64.getEncoder().encodeToString(
                    prototypeKey(function).getBytes(StandardCharsets.UTF_8))).append('\t')
                .append(Base64.getEncoder().encodeToString(
                    locals.getBytes(StandardCharsets.UTF_8))).append('\t')
                .append(sha256(locals)).append('\t')
                .append(callFixup != null).append('\t')
                .append(nullableText(callFixup).length()).append('\t')
                .append(sha256(nullableText(callFixup))).append('\t')
                .append(function.getStackFrame().getFrameSize()).append('\t')
                .append(function.getStackFrame().getLocalSize()).append('\t')
                .append(function.getStackFrame().getParameterSize()).append('\t')
                .append(function.getStackFrame().getParameterOffset()).append('\t')
                .append(function.getStackFrame().getReturnAddressOffset()).append('\t')
                .append(plate != null).append('\t').append(nullableText(plate).length())
                .append('\t').append(sha256(nullableText(plate))).append('\t')
                .append(repeatable != null).append('\t')
                .append(nullableText(repeatable).length()).append('\t')
                .append(sha256(nullableText(repeatable))).append('\t')
                .append(String.join(",", tags)).append('\t').append(sortedDigest(tags))
                .append('\t').append("0x").append(body.getMinAddress())
                .append('\t').append("0x").append(body.getMaxAddress())
                .append('\t').append(body.getNumAddresses())
                .append('\t').append(bodyDigest(body))
                .append('\t').append(bodyBytesSha256(body))
                .append('\t').append(validatedInstructionCount(body, target.address))
                .append('\n');
        }
        return output.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(
            String mode, byte[] toolBytes, String toolPath, File plan, byte[] planBytes,
            File evidence, byte[] evidenceBytes, int evidenceRows,
            File output, byte[] outputBytes, List<Target> targets,
            boolean commitRequested, boolean rollbackRequested,
            boolean transactionEndReturnedCommitted) throws Exception {
        List<String> catalog = tagDefinitions(
            currentProgram.getFunctionManager().getFunctionTagManager());
        List<String> usage = tagUsage(
            currentProgram.getFunctionManager().getFunctionTagManager());
        boolean post = mode.equals("apply") || mode.equals("readback");
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schemaVersion\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"")
            .append(json(Instant.now().toString())).append("\",\n");
        ready.append("  \"mode\": \"").append(mode).append("\",\n");
        ready.append("  \"tool\": {\"path\": \"").append(json(toolPath))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        ready.append("  \"plan\": {\"path\": \"").append(json(plan.getCanonicalPath()))
            .append("\", \"bytes\": ").append(planBytes.length)
            .append(", \"sha256\": \"").append(sha256(planBytes))
            .append("\", \"targets\": ").append(targets.size()).append("},\n");
        ready.append("  \"evidenceManifest\": {\"path\": \"")
            .append(json(evidence.getCanonicalPath()))
            .append("\", \"bytes\": ").append(evidenceBytes.length)
            .append(", \"sha256\": \"").append(sha256(evidenceBytes))
            .append("\", \"rows\": ").append(evidenceRows).append("},\n");
        ready.append("  \"program\": {\"name\": \"").append(EXPECTED_PROGRAM_NAME)
            .append("\", \"executableMd5\": \"").append(EXPECTED_PROGRAM_MD5)
            .append("\", \"executableSha256\": \"").append(EXPECTED_PROGRAM_SHA256)
            .append("\", \"imageBase\": \"0x").append(EXPECTED_IMAGE_BASE)
            .append("\", \"language\": \"").append(EXPECTED_LANGUAGE)
            .append("\", \"compilerSpec\": \"").append(EXPECTED_COMPILER_SPEC)
            .append("\", \"memorySha256\": \"").append(EXPECTED_MEMORY_SHA256)
            .append("\", \"functions\": ").append(EXPECTED_FUNCTION_COUNT)
            .append(", \"instructions\": ").append(EXPECTED_INSTRUCTION_COUNT)
            .append("},\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"catalog\": {\"state\": \"")
            .append(post ? "POST" : "PRE").append("\", \"count\": ")
            .append(catalog.size()).append(", \"sha256\": \"")
            .append(sortedDigest(catalog)).append("\", \"usageSha256\": \"")
            .append(sortedDigest(usage)).append("\"},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"rollbackRequested\": ").append(rollbackRequested).append(",\n");
        ready.append("  \"transactionEndReturnedCommitted\": ")
            .append(transactionEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback"))
            .append(",\n");
        ready.append("  \"reopenVerificationRequired\": ").append(mode.equals("apply"))
            .append(",\n");
        ready.append("  \"semanticCandidateCohort\": true,\n");
        ready.append("  \"semanticNamesAuthorized\": false,\n");
        ready.append("  \"authorityBoundary\": \"")
            .append(mode.equals("apply")
                ? "provisional_until_separate_reopen_inventory_and_refutation"
                : mode.equals("readback")
                    ? "loaded_exact_five_function_postimage"
                    : "validated_exact_five_function_preimage_no_mutation")
            .append("\"\n");
        ready.append("}\n");
        return ready.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static void publishPair(
            File output, byte[] outputBytes, File ready, byte[] readyBytes) throws Exception {
        File stagedOutput = null;
        File stagedReady = null;
        boolean outputPublished = false;
        boolean readyPublished = false;
        try {
            stagedOutput = stageAtomic(output, outputBytes);
            stagedReady = stageAtomic(ready, readyBytes);
            publishStaged(stagedOutput, output);
            stagedOutput = null;
            outputPublished = true;
            requireEqual("publication", "output_sha256", sha256(outputBytes),
                sha256(Files.readAllBytes(output.toPath())));
            publishStaged(stagedReady, ready);
            stagedReady = null;
            readyPublished = true;
            requireEqual("publication", "ready_sha256", sha256(readyBytes),
                sha256(Files.readAllBytes(ready.toPath())));
        }
        catch (Exception ex) {
            if (readyPublished) {
                deleteExactPublished(ready, readyBytes, ex);
            }
            if (outputPublished) {
                deleteExactPublished(output, outputBytes, ex);
            }
            throw ex;
        }
        finally {
            discardStaged(stagedOutput);
            discardStaged(stagedReady);
        }
    }

    private void validateOuterTransaction(long expectedId, String phase) throws Exception {
        TransactionInfo info = currentProgram.getCurrentTransactionInfo();
        if (info == null) {
            throw new IllegalStateException(
                phase + " outer GhidraScript transaction is no longer present");
        }
        requireEqual("transaction", phase + "_outer_id", expectedId, info.getID());
        requireEqual("transaction", phase + "_outer_status",
            TransactionInfo.Status.NOT_DONE, info.getStatus());
        requireEqual("transaction", phase + "_terminated", false,
            currentProgram.hasTerminatedTransaction());
    }

    private void publishSuccess(
            String mode, File plan, byte[] planBytes,
            File evidence, byte[] evidenceBytes, int evidenceRows,
            File output, File ready,
            List<Target> targets, byte[] toolBytes, String toolPath,
            boolean commitRequested, boolean rollbackRequested,
            boolean transactionEndReturnedCommitted) throws Exception {
        String state = mode.equals("dry") ? "PRE" : "POST";
        String status = mode.equals("dry")
            ? "validated_preimage" : mode.equals("readback")
                ? "verified_loaded_postimage" : "applied_commit_requested";
        byte[] outputBytes = buildOutput(targets, mode, state, status);
        byte[] readyBytes = buildReady(
            mode, toolBytes, toolPath, plan, planBytes,
            evidence, evidenceBytes, evidenceRows, output, outputBytes, targets,
            commitRequested, rollbackRequested, transactionEndReturnedCommitted);
        publishPair(output, outputBytes, ready, readyBytes);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 7) {
            throw new IllegalArgumentException(
                "usage: <lock-five-plan.tsv> <expected-plan-sha256> " +
                "<evidence.tsv> <expected-evidence-sha256> <out.tsv> " +
                "<out.ready.json> <dry|probe-row4|probe-post-inner|apply|readback>");
        }
        File plan = new File(args[0]).getCanonicalFile();
        if (!plan.isFile()) {
            throw new IllegalArgumentException("plan is not a file: " + plan);
        }
        String callerHash = normalizeSha256(args[1], "caller plan sha256");
        byte[] planBytes = Files.readAllBytes(plan.toPath());
        requireEqual("plan", "caller_sha256", EXPECTED_PLAN_SHA256, callerHash);
        requireEqual("plan", "actual_sha256", EXPECTED_PLAN_SHA256, sha256(planBytes));
        File evidence = new File(args[2]).getCanonicalFile();
        if (!evidence.isFile()) {
            throw new IllegalArgumentException(
                "evidence manifest is not a file: " + evidence);
        }
        String callerEvidenceHash =
            normalizeSha256(args[3], "caller evidence sha256");
        byte[] evidenceBytes = Files.readAllBytes(evidence.toPath());
        requireEqual("evidence", "caller_sha256", EXPECTED_EVIDENCE_SHA256,
            callerEvidenceHash);
        requireEqual("evidence", "actual_sha256", EXPECTED_EVIDENCE_SHA256,
            sha256(evidenceBytes));
        File output = requireNewOutput(args[4], "output TSV");
        File ready = requireNewOutput(args[5], "READY receipt");
        requireEqual("output", "distinct_paths", false, output.equals(ready));
        requireEqual("output", "shared_parent", output.getParentFile(), ready.getParentFile());
        preflightAtomicWrite(output, "output TSV");
        preflightAtomicWrite(ready, "READY receipt");
        String mode = requireMode(args[6]);

        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        String toolPath = getSourceFile().getCanonicalPath();
        File toolFile = new File(toolPath).getCanonicalFile();
        File repositoryRoot = toolFile.getParentFile().getParentFile().getCanonicalFile();
        requireEqual("tool", "source_parent", "tools",
            toolFile.getParentFile().getName());
        List<EvidenceRow> evidenceRows = loadEvidence(evidenceBytes, repositoryRoot);
        println("TARGET_LOCK_TOOL_OK schema=" + SCHEMA + " path=" + toolPath +
            " bytes=" + toolBytes.length + " sha256=" + sha256(toolBytes));
        println("TARGET_LOCK_PLAN_OK path=" + plan + " sha256=" + EXPECTED_PLAN_SHA256);
        println("TARGET_LOCK_EVIDENCE_OK path=" + evidence + " sha256=" +
            EXPECTED_EVIDENCE_SHA256 + " rows=" + evidenceRows.size());

        validateProgram();
        List<Target> targets = loadPlan(planBytes);
        validatePlanGlobals(targets);
        for (Target target : targets) {
            validateProposal(target);
        }

        if (mode.equals("readback")) {
            validateCatalog(targets, true);
            readBackAll(targets);
            validateProgram();
            println("TARGET_LOCK_READBACK_COMPLETE rows=" + targets.size());
            publishSuccess(
                mode, plan, planBytes, evidence, evidenceBytes, evidenceRows.size(),
                output, ready, targets, toolBytes, toolPath,
                false, false, false);
            return;
        }

        preflight(targets);
        if (mode.equals("dry")) {
            println("TARGET_LOCK_DRY_COMPLETE rows=" + targets.size() + " mutations=0");
            publishSuccess(
                mode, plan, planBytes, evidence, evidenceBytes, evidenceRows.size(),
                output, ready, targets, toolBytes, toolPath,
                false, false, false);
            return;
        }

        FunctionTagManager tagManager =
            currentProgram.getFunctionManager().getFunctionTagManager();
        int transaction = -1;
        long outerTransactionId = -1;
        boolean transactionEnded = false;
        boolean commitRequested = false;
        boolean transactionEndReturnedCommitted = false;
        try {
            TransactionInfo outerTransaction = currentProgram.getCurrentTransactionInfo();
            if (outerTransaction == null || currentProgram.hasTerminatedTransaction()) {
                throw new IllegalStateException(
                    "mutation requires one healthy GhidraScript outer transaction");
            }
            outerTransactionId = outerTransaction.getID();
            validateOuterTransaction(outerTransactionId, "pre_mutation");
            transaction = currentProgram.startTransaction(
                "five target-lock semantic corrections");
            try {
                createAllowedTags(targets, tagManager);
                int applied = 0;
                for (Target target : targets) {
                    monitor.checkCancelled();
                    applyTarget(target, tagManager);
                    ++applied;
                    if (mode.equals("probe-row4") && applied == 4) {
                        println(
                            "TARGET_LOCK_FORCED_ROW4_FAILURE rows_applied=4 " +
                            "rollback_requested=true");
                        throw new IllegalStateException(
                            "intentional target-lock row-4 rollback probe");
                    }
                }
                readBackAll(targets);
                validateCatalog(targets, true);
                commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            }
            finally {
                if (transaction >= 0 && !transactionEnded) {
                    transactionEndReturnedCommitted =
                        currentProgram.endTransaction(transaction, commitRequested);
                    transactionEnded = true;
                    println("TARGET_LOCK_TRANSACTION_END commit_requested=" +
                        commitRequested + " returned_committed=" +
                        transactionEndReturnedCommitted);
                }
            }

            requireEqual("transaction", "nested_end_returned_committed", false,
                transactionEndReturnedCommitted);
            validateOuterTransaction(outerTransactionId, "post_nested_end");
            if (mode.equals("probe-post-inner")) {
                println(
                    "TARGET_LOCK_FORCED_POST_INNER_FAILURE rollback_requested=true");
                throw new IllegalStateException(
                    "intentional target-lock post-inner rollback probe");
            }
            if (!mode.equals("apply") || !commitRequested) {
                throw new IllegalStateException("mutation mode reached unexpected success path");
            }

            readBackAll(targets);
            validateCatalog(targets, true);
            validateProgram();
            println("TARGET_LOCK_APPLY_COMPLETE rows=" + targets.size() +
                " reopen_verification_required=true publication=BEGIN");
            publishSuccess(
                mode, plan, planBytes, evidence, evidenceBytes, evidenceRows.size(),
                output, ready, targets, toolBytes, toolPath,
                true, false, transactionEndReturnedCommitted);
        }
        catch (Exception ex) {
            if (transaction >= 0) {
                boolean outerRollbackRequested = false;
                boolean unexpectedFinalCommit = transactionEndReturnedCommitted;
                boolean persistenceTainted = unexpectedFinalCommit;
                if (!transactionEnded) {
                    try {
                        boolean rollbackEnd = currentProgram.endTransaction(transaction, false);
                        transactionEnded = true;
                        transactionEndReturnedCommitted = rollbackEnd;
                        if (rollbackEnd) {
                            unexpectedFinalCommit = true;
                            persistenceTainted = true;
                        }
                        else {
                            outerRollbackRequested = true;
                        }
                    }
                    catch (Exception rollbackEx) {
                        ex.addSuppressed(rollbackEx);
                    }
                }
                if (transactionEnded && !commitRequested &&
                        !transactionEndReturnedCommitted) {
                    outerRollbackRequested = true;
                }
                if (!outerRollbackRequested && !persistenceTainted &&
                        !currentProgram.hasTerminatedTransaction()) {
                    try {
                        validateOuterTransaction(outerTransactionId, "failure_cleanup");
                        int abort = currentProgram.startTransaction(
                            "abort target-lock correction after failure");
                        boolean abortCommitted = currentProgram.endTransaction(abort, false);
                        if (abortCommitted) {
                            unexpectedFinalCommit = true;
                            persistenceTainted = true;
                        }
                        else {
                            outerRollbackRequested = true;
                        }
                    }
                    catch (Exception abortEx) {
                        ex.addSuppressed(abortEx);
                    }
                }
                println("TARGET_LOCK_MUTATION_TAINTED mode=" + mode +
                    " outer_rollback_requested=" + outerRollbackRequested +
                    " unexpected_final_commit=" + unexpectedFinalCommit +
                    " persistence_tainted=" + persistenceTainted +
                    " transaction_terminated=" + currentProgram.hasTerminatedTransaction() +
                    " recovery=RESTORE_VERIFIED_SCRATCH_BASE");
            }
            throw ex;
        }
    }
}
