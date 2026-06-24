//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBPackedVec2QuaternionTailWave722 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-packed-vec2-quaternion-tail-wave722",
            "wave722-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-packed-vec2-quaternion-tail"
        }, extras);
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }

            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        String staticEvidence = "Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact dispatch-table slot schema, packed vector/matrix/quaternion storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        return new Spec[] {
            new Spec(
                "0x005aa480",
                "CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_float_pairs", floatPtr),
                    param("input_packed_s16_pairs", shortPtr),
                    param("pair_count", uintType)
                },
                "Wave722 static read-back: packed 16-bit pair conversion dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; loops over four-pair batches through packed floating operations, falls back to CFastVB__ConvertFloat16BufferToFloat32_00575a6b for small/tail counts, writes float pairs, exits through FastExitMediaState, and returns the output pointer as an int-compatible value. " + staticEvidence,
                tags("packed-s16", "float-conversion", "batch", "dispatch-table", "pointer-return", "tranche-head")
            ),
            new Spec(
                "0x005aa73b",
                "CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("input_vec2", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                "Wave722 static read-back: Vec2-by-matrix4 dispatch with translation referenced by CFastVB__InitDispatchOpsFromFeatureFlags and a nearby transform tail; broadcasts input x/y lanes, applies two matrix row pairs plus translation terms, writes four output floats, exits through FastExitMediaState, and returns the output pointer as an int-compatible value. " + staticEvidence,
                tags("vec2", "matrix4x4", "translation", "transform", "dispatch-table", "pointer-return")
            ),
            new Spec(
                "0x005aa790",
                "CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec2", floatPtr),
                    param("input_vec2", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                "Wave722 static read-back: Vec2-by-matrix4 dispatch without translation referenced by CFastVB__InitDispatchOpsFromFeatureFlags and a nearby transform tail; broadcasts input x/y lanes, multiplies by matrix rows without translation terms, writes two output floats, exits through FastExitMediaState, and returns the output pointer as an int-compatible value. " + staticEvidence,
                tags("vec2", "matrix4x4", "no-translation", "transform", "dispatch-table", "pointer-return")
            ),
            new Spec(
                "0x005aa7c9",
                "CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec2", floatPtr),
                    param("input_vec2", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                "Wave722 static read-back: Vec2 transform/project dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags and a nearby transform tail; applies matrix rows plus translation, derives a reciprocal from the projected w lane, scales the output pair, writes two output floats, exits through FastExitMediaState, and returns the output pointer as an int-compatible value. " + staticEvidence,
                tags("vec2", "matrix4x4", "transform", "project", "reciprocal-w", "dispatch-table", "pointer-return")
            ),
            new Spec(
                "0x005ab00b",
                "CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", floatPtr),
                    param("input_quaternion_xyzw", floatPtr)
                },
                "Wave722 static read-back: packed quaternion normalization dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags and nearby quaternion tails; accumulates squared xy and masked zw lanes, applies reciprocal-square-root refinement with a small-length compare mask, writes four output quaternion floats, and exits through FastExitMediaState. " + staticEvidence,
                tags("quaternion", "normalize", "packed", "rsqrt", "dispatch-table", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyCFastVBPackedVec2QuaternionTailWave722 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave722 CFastVB packed Vec2/quaternion tail apply had missing/bad rows");
        }
    }
}
