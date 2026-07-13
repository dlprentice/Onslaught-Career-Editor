//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Apply only independently confirmed Ghidra metadata corrections from a
 * SHA-256-bound TSV plan.  The script deliberately performs a complete,
 * read-only preflight before opening the first mutation transaction.
 */
public class GhidraApplyReviewedCorrections extends GhidraScript {
    private static final String CONFIRMED = "confirmed-apply";
    private static final String RENDERING_ONLY = "name-and-parameter-rendering-only";
    private static final String STRUCTURED_PROTOTYPE = "structured-prototype-change";
    private static final String WORLD_LOAD_ADDRESS = "0x0050b9c0";
    private static final String EXPECTED_APPLY_PLAN_SHA256 =
        "a2a5f4210f060d1ce1ecc8f7d11ef041954b7c6951860b3026a32dd857bf2148";
    private static final String EXPECTED_PROGRAM_NAME = "BEA.exe";
    private static final String EXPECTED_PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final int EXPECTED_TARGET_COUNT = 91;
    private static final String[] HEADER = {
        "address", "classification", "fields", "expected_name", "expected_signature",
        "expected_comment", "expected_prototype_key", "corrected_name", "corrected_signature",
        "corrected_comment", "signature_change_class", "expected_corrected_prototype_key"
    };
    private static final Set<String> ALLOWED_FIELDS =
        new HashSet<>(Arrays.asList("name", "signature", "comment"));

    private static class Target {
        final String address;
        final Set<String> fields;
        final String expectedName;
        final String expectedSignature;
        final String expectedComment;
        final String expectedPrototypeKey;
        final String correctedName;
        final String correctedSignature;
        final String correctedComment;
        final String signatureChangeClass;
        final String expectedCorrectedPrototypeKey;

        Target(String[] columns) {
            address = normalizeAddress(columns[0]);
            if (!CONFIRMED.equals(columns[1])) {
                throw new IllegalArgumentException(
                    "plan contains non-confirmed classification at " + address + ": " + columns[1]);
            }
            fields = parseFields(address, columns[2]);
            expectedName = columns[3];
            expectedSignature = columns[4];
            expectedComment = columns[5];
            expectedPrototypeKey = columns[6];
            correctedName = columns[7];
            correctedSignature = columns[8];
            correctedComment = columns[9];
            signatureChangeClass = columns[10];
            expectedCorrectedPrototypeKey = columns[11];
        }
    }

    private static String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            out.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return out.toString();
    }

    private static String sha256(File file) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        return hex(digest.digest(Files.readAllBytes(file.toPath())));
    }

    private static String normalizeAddress(String text) {
        String value = text == null ? "" : text.trim().toLowerCase(Locale.ROOT);
        if (!value.matches("0x[0-9a-f]{8}")) {
            throw new IllegalArgumentException("non-canonical plan address: " + text);
        }
        return value;
    }

    private static Set<String> parseFields(String address, String value) {
        LinkedHashSet<String> result = new LinkedHashSet<>();
        if (value == null || value.isEmpty()) {
            throw new IllegalArgumentException("empty fields at " + address);
        }
        for (String field : value.split(",", -1)) {
            if (!ALLOWED_FIELDS.contains(field)) {
                throw new IllegalArgumentException("unknown field at " + address + ": " + field);
            }
            if (!result.add(field)) {
                throw new IllegalArgumentException("duplicate field at " + address + ": " + field);
            }
        }
        return result;
    }

    private static String unescape(String value) {
        StringBuilder result = new StringBuilder(value.length());
        for (int i = 0; i < value.length(); i++) {
            char ch = value.charAt(i);
            if (ch != '\\') {
                result.append(ch);
                continue;
            }
            if (++i >= value.length()) {
                throw new IllegalArgumentException("trailing backslash in plan field");
            }
            char escaped = value.charAt(i);
            if (escaped == '\\') {
                result.append('\\');
            } else if (escaped == 't') {
                result.append('\t');
            } else if (escaped == 'r') {
                result.append('\r');
            } else if (escaped == 'n') {
                result.append('\n');
            } else {
                throw new IllegalArgumentException("unknown plan escape: \\" + escaped);
            }
        }
        return result.toString();
    }

    private static List<Target> loadTargets(File plan) throws Exception {
        List<String> lines = Files.readAllLines(plan.toPath(), StandardCharsets.UTF_8);
        if (lines.isEmpty() || !lines.get(0).equals(String.join("\t", HEADER))) {
            throw new IllegalArgumentException("reviewed-correction plan header mismatch");
        }
        List<Target> result = new ArrayList<>();
        Set<String> addresses = new HashSet<>();
        for (int lineNumber = 2; lineNumber <= lines.size(); lineNumber++) {
            String line = lines.get(lineNumber - 1);
            if (line.isEmpty()) {
                throw new IllegalArgumentException("blank plan row at line " + lineNumber);
            }
            String[] raw = line.split("\t", -1);
            if (raw.length != HEADER.length) {
                throw new IllegalArgumentException(
                    "plan column count mismatch at line " + lineNumber + ": " + raw.length);
            }
            String[] columns = new String[raw.length];
            for (int i = 0; i < raw.length; i++) {
                columns[i] = unescape(raw[i]);
            }
            Target target = new Target(columns);
            if (!addresses.add(target.address)) {
                throw new IllegalArgumentException("duplicate address in plan: " + target.address);
            }
            result.add(target);
        }
        if (result.isEmpty()) {
            throw new IllegalArgumentException("reviewed-correction plan has no rows");
        }
        return result;
    }

    private Address resolveAddress(String text) {
        Address result = toAddr(text);
        if (result == null) {
            throw new IllegalArgumentException("unresolvable address: " + text);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address address = resolveAddress(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private static String safeComment(Function fn) {
        return fn.getComment() == null ? "" : fn.getComment();
    }

    private static String prototypeKey(Function fn) {
        StringBuilder result = new StringBuilder();
        result.append("cc=").append(fn.getCallingConventionName());
        result.append("|custom=").append(fn.hasCustomVariableStorage());
        result.append("|varargs=").append(fn.hasVarArgs());
        result.append("|noreturn=").append(fn.hasNoReturn());
        result.append("|return=").append(fn.getReturn().getDataType().getPathName());
        result.append('@').append(fn.getReturn().getVariableStorage().toString());
        result.append("|params=");
        Parameter[] parameters = fn.getParameters();
        for (int i = 0; i < parameters.length; i++) {
            if (i > 0) {
                result.append(';');
            }
            Parameter parameter = parameters[i];
            result.append(parameter.getOrdinal()).append(':');
            result.append(parameter.getDataType().getPathName());
            result.append('@').append(parameter.getVariableStorage().toString());
        }
        result.append("|purge=").append(fn.getStackPurgeSize());
        return result.toString();
    }

    private static void requireEqual(String address, String field, String expected, String actual) {
        if (!expected.equals(actual)) {
            throw new IllegalStateException(
                "metadata mismatch at " + address + " field " + field
                + " expected=" + expected + " actual=" + actual);
        }
    }

    private void validateTargetShape(Target target) {
        boolean changesSignature = target.fields.contains("signature");
        if (!changesSignature && !target.signatureChangeClass.isEmpty()) {
            throw new IllegalArgumentException(
                "signature class without signature field at " + target.address);
        }
        if (changesSignature) {
            if (RENDERING_ONLY.equals(target.signatureChangeClass)) {
                requireEqual(target.address, "rendering prototype key",
                    target.expectedPrototypeKey, target.expectedCorrectedPrototypeKey);
            } else if (STRUCTURED_PROTOTYPE.equals(target.signatureChangeClass)) {
                if (!WORLD_LOAD_ADDRESS.equals(target.address)) {
                    throw new IllegalArgumentException(
                        "structured prototype is outside leased 0x0050b9c0 address: " + target.address);
                }
                if (target.expectedCorrectedPrototypeKey.isEmpty()
                        || target.expectedCorrectedPrototypeKey.equals(target.expectedPrototypeKey)) {
                    throw new IllegalArgumentException(
                        "structured prototype lacks distinct corrected key at " + target.address);
                }
            } else {
                throw new IllegalArgumentException(
                    "unsupported signature change class at " + target.address + ": "
                    + target.signatureChangeClass);
            }
        }
        if (!target.fields.contains("name")) {
            requireEqual(target.address, "unlisted corrected name", target.expectedName, target.correctedName);
        }
        if (!target.fields.contains("signature")) {
            String expectedRenderedSignature = target.expectedSignature;
            if (target.fields.contains("name")) {
                int nameOffset = expectedRenderedSignature.indexOf(target.expectedName);
                if (nameOffset < 0) {
                    throw new IllegalArgumentException(
                        "expected name is absent from rendered signature at " + target.address);
                }
                expectedRenderedSignature = expectedRenderedSignature.substring(0, nameOffset)
                    + target.correctedName
                    + expectedRenderedSignature.substring(nameOffset + target.expectedName.length());
            }
            requireEqual(target.address, "unlisted corrected signature rendering",
                expectedRenderedSignature, target.correctedSignature);
            requireEqual(target.address, "unlisted corrected prototype",
                target.expectedPrototypeKey, target.expectedCorrectedPrototypeKey);
        }
        if (!target.fields.contains("comment")) {
            requireEqual(target.address, "unlisted corrected comment",
                target.expectedComment, target.correctedComment);
        }
    }

    private void preflightAll(List<Target> targets) throws Exception {
        for (Target target : targets) {
            monitor.checkCancelled();
            validateTargetShape(target);
            Function fn = functionAtEntry(target.address);
            if (fn == null) {
                throw new IllegalStateException("function missing at " + target.address);
            }
            requireEqual(target.address, "name", target.expectedName, fn.getName());
            requireEqual(target.address, "signature", target.expectedSignature, fn.getSignature().toString());
            requireEqual(target.address, "comment", target.expectedComment, safeComment(fn));
            requireEqual(target.address, "prototype_key", target.expectedPrototypeKey, prototypeKey(fn));
        }
        println("PREFLIGHT_OK rows=" + targets.size());
    }

    private void readBackField(Target target, Function fn, String field) {
        if ("name".equals(field)) {
            requireEqual(target.address, field, target.correctedName, fn.getName());
        } else if ("signature".equals(field)) {
            requireEqual(target.address, field, target.correctedSignature, fn.getSignature().toString());
            requireEqual(target.address, "prototype_key", target.expectedCorrectedPrototypeKey, prototypeKey(fn));
        } else if ("comment".equals(field)) {
            requireEqual(target.address, field, target.correctedComment, safeComment(fn));
        } else {
            throw new IllegalArgumentException("unexpected readback field: " + field);
        }
        println("READBACK_FIELD_OK address=" + target.address + " field=" + field);
    }

    private void readBackRow(Target target) {
        Function fn = functionAtEntry(target.address);
        if (fn == null) {
            throw new IllegalStateException("readback function missing at " + target.address);
        }
        requireEqual(target.address, "name", target.correctedName, fn.getName());
        requireEqual(target.address, "signature", target.correctedSignature, fn.getSignature().toString());
        requireEqual(target.address, "comment", target.correctedComment, safeComment(fn));
        requireEqual(target.address, "prototype_key",
            target.expectedCorrectedPrototypeKey, prototypeKey(fn));
        println("READBACK_ROW_OK address=" + target.address);
    }

    private void applyRenderingSignature(Target target, Function fn) throws Exception {
        if (target.correctedSignature.equals(fn.getSignature().toString())) {
            return;
        }
        Parameter[] parameters = fn.getParameters();
        if (parameters.length == 0) {
            throw new IllegalStateException("rendering-only signature has no parameter at " + target.address);
        }
        parameters[0].setName("this", SourceType.USER_DEFINED);
        requireEqual(target.address, "rendered signature after parameter rename",
            target.correctedSignature, fn.getSignature().toString());
        requireEqual(target.address, "prototype after rendering-only signature",
            target.expectedPrototypeKey, prototypeKey(fn));
    }

    private void applyWorldLoadPrototype(Target target, Function fn) throws Exception {
        if (!WORLD_LOAD_ADDRESS.equals(target.address)) {
            throw new IllegalStateException("prototype mutation attempted outside 0x0050b9c0");
        }
        PointerDataType voidPointer = new PointerDataType(VoidDataType.dataType);
        fn.setCallingConvention("__thiscall");
        fn.setReturnType(BooleanDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            new ParameterImpl("this", voidPointer, currentProgram),
            new ParameterImpl("mem_buffer", voidPointer, currentProgram),
            new ParameterImpl("is_base_world", IntegerDataType.dataType, currentProgram),
            new ParameterImpl("initialize_world_state", IntegerDataType.dataType, currentProgram)
        );
    }

    private void applyTarget(Target target) throws Exception {
        int transactionId = currentProgram.startTransaction(
            "reviewed correction " + target.address);
        boolean commit = false;
        try {
            Function fn = functionAtEntry(target.address);
            if (fn == null) {
                throw new IllegalStateException("function disappeared at " + target.address);
            }
            if (target.fields.contains("name")) {
                fn.setName(target.correctedName, SourceType.USER_DEFINED);
                readBackField(target, fn, "name");
            }
            if (target.fields.contains("signature")) {
                if (RENDERING_ONLY.equals(target.signatureChangeClass)) {
                    applyRenderingSignature(target, fn);
                } else if (STRUCTURED_PROTOTYPE.equals(target.signatureChangeClass)) {
                    applyWorldLoadPrototype(target, fn);
                } else {
                    throw new IllegalStateException(
                        "signature class changed after preflight at " + target.address);
                }
                readBackField(target, fn, "signature");
            }
            if (target.fields.contains("comment")) {
                fn.setComment(target.correctedComment);
                readBackField(target, fn, "comment");
            }
            readBackRow(target);
            commit = true;
        } catch (Exception ex) {
            println("APPLY_ABORT address=" + target.address + " reason=" + ex.getMessage());
            throw ex;
        } finally {
            currentProgram.endTransaction(transactionId, commit);
        }
        readBackRow(target);
    }

    private static boolean isDryRun(String mode) {
        if ("dry".equalsIgnoreCase(mode) || "dry-run".equalsIgnoreCase(mode)) {
            return true;
        }
        if ("apply".equalsIgnoreCase(mode)) {
            return false;
        }
        throw new IllegalArgumentException("mode must be dry or apply");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 3) {
            throw new IllegalArgumentException(
                "usage: <apply-plan.tsv> <expected-sha256> <dry|apply>");
        }
        File plan = new File(args[0]);
        if (!plan.isFile()) {
            throw new IllegalArgumentException("apply plan is not a file: " + plan);
        }
        String expectedSha256 = args[1].trim().toLowerCase(Locale.ROOT);
        if (!expectedSha256.matches("[0-9a-f]{64}")) {
            throw new IllegalArgumentException("expectedSha256 must be 64 lowercase hex characters");
        }
        requireEqual(
            "reviewed apply plan", "caller sha256", EXPECTED_APPLY_PLAN_SHA256, expectedSha256);
        String actualSha256 = sha256(plan);
        requireEqual("reviewed apply plan", "sha256", EXPECTED_APPLY_PLAN_SHA256, actualSha256);
        println("PLAN_HASH_OK sha256=" + actualSha256);

        if (currentProgram == null) {
            throw new IllegalStateException("no current Ghidra program");
        }
        requireEqual("program", "name", EXPECTED_PROGRAM_NAME, currentProgram.getName());
        requireEqual(
            "program", "imported executable md5", EXPECTED_PROGRAM_MD5,
            currentProgram.getExecutableMD5());
        println(
            "PROGRAM_ID_OK name=" + currentProgram.getName() +
            " imported_md5=" + currentProgram.getExecutableMD5());

        List<Target> targets = loadTargets(plan);
        if (targets.size() != EXPECTED_TARGET_COUNT) {
            throw new IllegalArgumentException(
                "reviewed-correction target count mismatch: expected=" +
                EXPECTED_TARGET_COUNT + " actual=" + targets.size());
        }
        preflightAll(targets);
        boolean dryRun = isDryRun(args[2]);
        if (dryRun) {
            println("DRY_RUN_OK rows=" + targets.size() + " mutations=0");
            return;
        }

        int applied = 0;
        for (Target target : targets) {
            monitor.checkCancelled();
            applyTarget(target);
            applied++;
        }
        println("APPLY_COMPLETE rows=" + applied);
    }
}
