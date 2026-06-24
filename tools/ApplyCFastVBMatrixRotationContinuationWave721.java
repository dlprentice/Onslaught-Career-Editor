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

public class ApplyCFastVBMatrixRotationContinuationWave721 extends GhidraScript {
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
            "cfastvb-matrix-rotation-continuation-wave721",
            "wave721-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-matrix-rotation-continuation"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-matrix-rotation-continuation-wave721",
            "wave721-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-stack-context",
            "cfastvb-matrix-rotation-continuation"
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
        String staticEvidence = "Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact dispatch-table slot schema, packed vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        return new Spec[] {
            new Spec(
                "0x005a62bf",
                "CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: identity matrix4x4 initializer called by the adjacent optional-transform composition path; writes one/zero lanes across a sixteen-float matrix and exits through FastExitMediaState. " + staticEvidence,
                signatureTags("matrix4x4", "identity", "composition-helper", "tranche-head")
            ),
            new Spec(
                "0x005a647f",
                "CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave721 static read-back: large optional-transform composition core called by the SIMD composition path; stack-locked decompile shows output matrix, optional translation, quaternion/rotation, scale/basis, inverse pivot, and additive offset-style inputs, then writes a composed matrix and returns the output pointer. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("matrix4x4", "optional-inputs", "composition", "stack-locked", "simd-helper")
            ),
            new Spec(
                "0x005a7617",
                "CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave721 static read-back: Euler-angle-to-matrix4 dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; custom stack-frame code scales packed angle inputs by the 0x005ef190 constant, calls the fast trig pair helper three times, and writes a rotation matrix. Signature intentionally left unchanged because the decompile exposes hidden packed stack inputs and the exact packed argument ABI remains unresolved. " + staticEvidence,
                commentOnlyTags("matrix4x4", "rotation", "euler-angles", "fast-trig", "packed-stack-abi", "dispatch-table")
            ),
            new Spec(
                "0x005a7cf0",
                "CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("axis_angle_vec3", floatPtr)
                },
                true,
                "Wave721 static read-back: axis-angle-vector-to-matrix4 dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; copies the input vector, normalizes it through CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f, calls the fast trig pair helper, and expands the axis-angle terms into a sixteen-float rotation matrix. " + staticEvidence,
                signatureTags("matrix4x4", "rotation", "axis-angle", "normalize", "fast-trig", "dispatch-table")
            ),
            new Spec(
                "0x005a7e09",
                "CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms",
                "",
                intType,
                new ParameterImpl[] {},
                false,
                "Wave721 static read-back: optional transform matrix composition dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags; stack-locked decompile builds identity/scale/rotation/translation combinations from nullable transform pointers, applies optional inverse-pivot and additive-offset adjustments, and returns the output pointer. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("matrix4x4", "optional-transforms", "composition", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a8f5d",
                "CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_inverse_matrix4x4", floatPtr),
                    param("out_determinant_or_null", floatPtr),
                    param("input_matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: matrix4x4 inverse dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags and called by the SIMD optional-transform composition path; computes cofactors and determinant, writes the determinant when the optional output pointer is non-null, skips inverse writes for zero determinant, otherwise writes a reciprocal-determinant-scaled inverse matrix. " + staticEvidence,
                signatureTags("matrix4x4", "inverse", "determinant", "cofactor", "dispatch-table", "simd-helper")
            ),
            new Spec(
                "0x005a9637",
                "CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_inverse_matrix4x4", floatPtr),
                    param("out_determinant_or_null", floatPtr),
                    param("input_matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: scalar matrix4x4 inverse variant called by the scalar optional-transform composition path; computes determinant/cofactor terms, writes the optional determinant, returns zero when the determinant is zero, otherwise writes the inverse matrix and returns the output pointer as an int-compatible value. " + staticEvidence,
                signatureTags("matrix4x4", "inverse", "determinant", "cofactor", "scalar-helper", "pointer-return")
            ),
            new Spec(
                "0x005a99f8",
                "CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec3", floatPtr),
                    param("input_vec3", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: Vec3-by-matrix4 helper referenced by CFastVB__InitDispatchOpsFromFeatureFlags and nearby transform tails; multiplies input x/y/z by the matrix rows without adding translation terms, writes three output floats, and returns the output pointer as an int-compatible value. " + staticEvidence,
                signatureTags("vec3", "matrix4x4", "transform", "no-translation", "dispatch-table", "pointer-return")
            ),
            new Spec(
                "0x005a9a5f",
                "CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec3", floatPtr),
                    param("input_vec3", floatPtr)
                },
                true,
                "Wave721 static read-back: packed Vec3 normalization helper referenced by CFastVB__InitDispatchOpsFromFeatureFlags and called by the axis-angle matrix/quaternion builders; computes squared length, applies reciprocal-square-root refinement with a small-length mask, writes normalized x/y/z, and exits through FastExitMediaState. " + staticEvidence,
                signatureTags("vec3", "normalize", "packed", "rsqrt", "dispatch-table", "shared-helper")
            ),
            new Spec(
                "0x005a9ced",
                "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec3", floatPtr),
                    param("input_vec3", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: Vec3 transform/project helper called by the composition/project tails; applies matrix rows plus translation, derives a reciprocal from the projected w lane, scales x/y/z by that reciprocal, writes three output floats, and returns the output pointer as an int-compatible value. " + staticEvidence,
                signatureTags("vec3", "matrix4x4", "transform", "project", "reciprocal-w", "pointer-return")
            ),
            new Spec(
                "0x005a9d78",
                "CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("left_matrix4x4", floatPtr),
                    param("right_matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: packed matrix4x4 multiply helper called by the composition/project tails; reads four packed rows from the left matrix, multiplies them across the right matrix columns, writes sixteen output floats, and returns the output pointer as an int-compatible value. " + staticEvidence,
                signatureTags("matrix4x4", "multiply", "packed", "composition-helper", "pointer-return")
            ),
            new Spec(
                "0x005a9f3f",
                "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec3", floatPtr),
                    param("input_vec3", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                true,
                "Wave721 static read-back: alternate Vec3 transform/project dispatch referenced by CFastVB__InitDispatchOpsFromFeatureFlags and a nearby tail call; mirrors the projected transform shape at 0x005a9ced, including translation terms, reciprocal-w scaling, three output floats, and an int-compatible output-pointer return. " + staticEvidence,
                signatureTags("vec3", "matrix4x4", "transform", "project", "alternate-dispatch", "dispatch-table", "pointer-return", "tranche-tail")
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

        println("ApplyCFastVBMatrixRotationContinuationWave721 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave721 CFastVB matrix rotation continuation apply had missing/bad rows");
        }
    }
}
