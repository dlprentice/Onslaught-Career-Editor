//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBQuaternionTailWave720 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean updateSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean updateSignature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
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

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-quaternion-tail-wave720",
            "wave720-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-quaternion-tail"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-quaternion-tail-wave720",
            "wave720-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-stack-context",
            "cfastvb-quaternion-tail"
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
        if (!spec.updateSignature) {
            return true;
        }
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
        if (spec.updateSignature && !signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        if (!spec.updateSignature) {
            return "<comment/tag-only; saved signature intentionally unchanged>";
        }
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
        if (spec.updateSignature && !signatureMatches(readBack, spec)) {
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

            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
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
                if (!spec.updateSignature) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }

            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            if (!spec.updateSignature) {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        String staticEvidence = "Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact dispatch-table slot schema, vector/quaternion storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        return new Spec[] {
            new Spec(
                "0x005a38c0",
                "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave720 static read-back: Vec4-array-by-matrix4 dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile shows output pointer, destination stride, input Vec4 pointer, source stride, matrix4x4 pointer, and element count, then writes transformed Vec4 lanes and returns the original output pointer. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("vec4-array", "matrix4x4", "transform", "stack-locked", "dispatch-table", "tranche-head")
            ),
            new Spec(
                "0x005a3980",
                "CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave720 static read-back: alternate Vec4-array-by-matrix4 dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile shows the same strided output/input/matrix/count shape as 0x005a38c0 and writes four transformed float lanes per element. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("vec4-array", "matrix4x4", "transform", "alternate-dispatch", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a40c0",
                "CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave720 static read-back: strided Vec3-array-by-matrix4 dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile reads three source lanes, applies matrix rows plus translation terms, writes four output lanes, advances source/destination strides, and returns the original output pointer. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("vec3-array", "matrix4x4", "translation", "transform", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a47f2",
                "CFastVB__DispatchOp_ExtractAxisAndOptionalAngle",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("quaternion_xyzw", floatPtr),
                    param("out_axis_vec3_or_null", floatPtr),
                    param("out_angle_or_null", floatPtr)
                },
                true,
                "Wave720 static read-back: quaternion axis/angle extraction dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; copies the first three quaternion lanes to the optional axis output, and when the optional angle output is non-null applies CFastVB__FastAcosApprox_Scalar to the scalar lane and scales the result before storing one float. " + staticEvidence,
                signatureTags("quaternion", "axis-angle", "optional-output", "fast-acos", "dispatch-table")
            ),
            new Spec(
                "0x005a4d2c",
                "CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", floatPtr),
                    param("axis_vec3", floatPtr),
                    param("angle_radians", FloatDataType.dataType)
                },
                true,
                "Wave720 static read-back: axis-angle-vector-to-quaternion dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; normalizes the axis vector through CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f, scales the angle by the 0x005ef190 constant, calls the fast trig pair helper, and writes four quaternion lanes. " + staticEvidence,
                signatureTags("quaternion", "axis-angle", "normalize", "fast-trig", "dispatch-table")
            ),
            new Spec(
                "0x005a4d98",
                "CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", floatPtr),
                    param("from_quaternion_xyzw", floatPtr),
                    param("to_quaternion_xyzw", floatPtr),
                    param("blend_ratio", FloatDataType.dataType)
                },
                true,
                "Wave720 static read-back: quaternion-pair interpolation core referenced by the CFastVB dispatch table and called by the adjacent quaternion blend helpers; computes a quaternion dot product, handles sign/short-path selection, uses reciprocal/trig branches for the angular case, and writes blended quaternion lanes to the output. " + staticEvidence,
                signatureTags("quaternion", "interpolation", "slerp-nlerp-core", "blend", "dispatch-table")
            ),
            new Spec(
                "0x005a4ecf",
                "CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave720 static read-back: quaternion triple-blend dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile sums two weight inputs, interpolates a base quaternion toward two controls through CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98, applies a reciprocal-weighted blend between the intermediates, and returns the output pointer. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("quaternion", "triple-blend", "interpolation", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a4f5c",
                "CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave720 static read-back: quaternion control-pair blend dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile interpolates two quaternion pairs at the same blend ratio, derives a secondary smoothstep-like ratio from t and t*t, then interpolates between the two intermediate quaternions. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("quaternion", "control-pair-blend", "interpolation", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a5052",
                "CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", floatPtr),
                    param("input_quaternion_xyzw", floatPtr)
                },
                true,
                "Wave720 static read-back: quaternion normalization/angle fallback dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; reads four input lanes, conditionally uses CFastVB__FastAcosApprox_Scalar and CFastVB__FastSinApprox_Scalar_005b8da0 when the scalar lane is below threshold, scales vector lanes through reciprocal refinement, masks the scalar lane, and writes the output quaternion. " + staticEvidence,
                signatureTags("quaternion", "normalize", "fast-acos", "fast-sin", "dispatch-table")
            ),
            new Spec(
                "0x005a519e",
                "CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave720 static read-back: large quaternion spline-segment blend dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile aligns quaternion signs by distance tests, normalizes/fallbacks through fast acos/sin paths, writes two quaternion outputs, and preserves an intermediate control quaternion. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("quaternion", "spline-segment", "sign-alignment", "stack-locked", "dispatch-table", "tranche-tail")
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

        println("ApplyCFastVBQuaternionTailWave720 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave720 CFastVB quaternion tail apply had missing/bad rows");
        }
    }
}
