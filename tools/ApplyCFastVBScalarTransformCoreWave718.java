//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.UnsignedShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCFastVBScalarTransformCoreWave718 extends GhidraScript {
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
            "cfastvb-scalar-transform-core-wave718",
            "wave718-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-scalar-transform-core"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-scalar-transform-core-wave718",
            "wave718-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-stack-context",
            "cfastvb-scalar-transform-core"
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
        DataType voidType = VoidDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType ushortPtr = new PointerDataType(UnsignedShortDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        String staticEvidence = "Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact dispatch-table slot schema, vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        return new Spec[] {
            new Spec(
                "0x005a0b22",
                "CFastVB__ConvertHalfToFloatArray_SSE",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_float32", floatPtr),
                    param("in_float16", ushortPtr),
                    param("element_count", uintType)
                },
                true,
                "Wave718 static read-back: half-float conversion dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; processes eight half-float elements through CFastVB__ConvertHalfToFloat8_SIMDKernel when possible, tails scalar ushort inputs into float output slots, and returns the original output pointer in Ghidra's saved integer return type. " + staticEvidence,
                signatureTags("half-float", "float32", "sse", "conversion", "dispatch-table", "tranche-head")
            ),
            new Spec(
                "0x005a0df6",
                "CFastVB__ComputeAdjugateVec4_PackedA",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("row_a_vec4", floatPtr),
                    param("row_b_vec4", floatPtr),
                    param("row_c_vec4", floatPtr)
                },
                true,
                "Wave718 static read-back: packed four-float adjugate/cofactor helper referenced by CFastVB__InitDispatchTableVariant_005980be; reads three vec4 rows, combines 3x3 minor products with sign-mask constants at 0x0065e600..0x0065e60c, writes four output lanes, and returns with RET 0x10. " + staticEvidence,
                signatureTags("adjugate", "cofactor", "vec4", "matrix", "dispatch-table")
            ),
            new Spec(
                "0x005a0eb6",
                "CFastVB__NormalizeVec4_ReciprocalSqrt",
                "__stdcall",
                floatPtr,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("input_vec4", floatPtr)
                },
                true,
                "Wave718 static read-back: vec4 normalization helper referenced by both CFastVB dispatch-table variants; computes a four-component length square, uses rsqrtss plus refinement constants at 0x0065e610 and 0x0065e620, writes out_vec4, returns the output pointer, and returns with RET 0x8. " + staticEvidence,
                signatureTags("vec4", "normalize", "reciprocal-sqrt", "sse", "dispatch-table")
            ),
            new Spec(
                "0x005a0f50",
                "CFastVB__EvaluateCubicBasisVec3",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: cubic basis Vec3 evaluator referenced by both CFastVB dispatch-table variants; stack-locked decompile shows four input vectors plus a scalar t, basis constants at 0x0065e5c0..0x0065e5fc, and writes three float lanes to the output. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("cubic-basis", "vec3", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a1002",
                "CFastVB__EvaluateCubicBasisVec2",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: cubic basis Vec2 evaluator referenced by both CFastVB dispatch-table variants; stack-locked decompile shows four input vectors plus scalar t, basis constants at 0x0065e5c0..0x0065e5fc, and writes two float lanes to the output. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("cubic-basis", "vec2", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a1087",
                "CFastVB__EvaluateCubicBasisVec4",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: cubic basis Vec4 evaluator referenced by both CFastVB dispatch-table variants; stack-locked decompile shows four input float vectors plus scalar t, basis constants at 0x0065e5c0..0x0065e5fc, and writes four output lanes. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("cubic-basis", "vec4", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a112c",
                "CFastVB__DispatchOp_CubicBlendVec3_005a112c",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: cubic blend Vec3 dispatch referenced by both CFastVB dispatch-table variants; stack-locked decompile shows four input vectors plus scalar t, blend constants at 0x0065e580..0x0065e5b0, and writes three output lanes. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("cubic-blend", "vec3", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a11df",
                "CFastVB__DispatchOp_CubicBlendVec4_005a11df",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: cubic blend Vec4 dispatch referenced by both CFastVB dispatch-table variants; stack-locked decompile shows four input vectors plus scalar t, blend constants at 0x0065e580..0x0065e5b0, and writes four output lanes. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("cubic-blend", "vec4", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a1279",
                "CFastVB__EvaluateCubicBasisDerivativeVec2",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: cubic derivative/basis Vec2 evaluator referenced by both CFastVB dispatch-table variants; stack-locked decompile uses the 0x0065e580..0x0065e5b0 coefficient family and writes two output lanes from four input vectors. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("cubic-derivative", "vec2", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a13f7",
                "CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave718 static read-back: reciprocal-weighted Vec3 interpolation dispatch referenced by both CFastVB dispatch-table variants; stack-locked decompile combines two input vectors with reciprocal/projective intermediate lanes before writing the output vector. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("interpolate", "vec3", "reciprocal", "stack-locked", "dispatch-table")
            ),
            new Spec(
                "0x005a14a5",
                "CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_plane_vec4", floatPtr),
                    param("point_a_vec3", floatPtr),
                    param("point_b_vec3", floatPtr),
                    param("point_c_vec3", floatPtr)
                },
                true,
                "Wave718 static read-back: plane-from-triangle dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; subtracts point pairs, builds a cross-product normal, normalizes it with rsqrtss refinement, writes xyz normal and a sign-masked distance term, and returns with RET 0x10. " + staticEvidence,
                signatureTags("plane", "triangle", "cross-product", "normalize", "dispatch-table")
            ),
            new Spec(
                "0x005a15a5",
                "CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("quaternion_xyzw", floatPtr)
                },
                true,
                "Wave718 static read-back: quaternion-to-matrix4 dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; normalizes quaternion lanes with sign masks and rsqrtss refinement, expands products into sixteen matrix floats, and returns with RET 0x8. " + staticEvidence,
                signatureTags("quaternion", "matrix4x4", "normalize", "dispatch-table")
            ),
            new Spec(
                "0x005a16b1",
                "CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec3", floatPtr),
                    param("input_vec3", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                true,
                "Wave718 static read-back: scalar Vec3-by-matrix4 transform dispatch referenced by both CFastVB dispatch-table variants and by two batch tails; handles aligned and unaligned matrix reads, adds translation row terms, writes three output floats, and returns with RET 0xc. " + staticEvidence,
                signatureTags("vec3", "matrix4x4", "transform", "tail-scalar-dispatch", "dispatch-table")
            ),
            new Spec(
                "0x005a1786",
                "CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_projected_vec3", floatPtr),
                    param("input_vec3", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                true,
                "Wave718 static read-back: scalar projected Vec3-by-matrix4 transform dispatch referenced by both CFastVB dispatch-table variants and by two batch tails; computes xyz and w terms, refines reciprocal projection with rcpps, writes projected output floats, and returns with RET 0xc. " + staticEvidence,
                signatureTags("vec3", "matrix4x4", "projective-transform", "reciprocal", "dispatch-table")
            ),
            new Spec(
                "0x005a1889",
                "CFastVB__DispatchOp_NormalizeVec3_005a1889",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec3", floatPtr),
                    param("input_vec3", floatPtr)
                },
                true,
                "Wave718 static read-back: scalar Vec3 normalization dispatch referenced by both CFastVB dispatch-table variants; guards tiny length-square values, otherwise uses rsqrtss plus one refinement and writes three output floats, returning with RET 0x8. " + staticEvidence,
                signatureTags("vec3", "normalize", "reciprocal-sqrt", "dispatch-table")
            ),
            new Spec(
                "0x005a1979",
                "CFastVB__DispatchOp_NormalizeVec4_005a1979",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("input_vec4", floatPtr)
                },
                true,
                "Wave718 static read-back: scalar Vec4 normalization dispatch referenced by both CFastVB dispatch-table variants; normalizes xyz with a tiny-length guard, scales the fourth lane with the same factor, writes four output floats, and returns with RET 0x8. " + staticEvidence,
                signatureTags("vec4", "normalize", "reciprocal-sqrt", "dispatch-table")
            ),
            new Spec(
                "0x005a1a8e",
                "CFastVB__BuildMatrix4x4FromQuaternion",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("basis_matrix4x4", floatPtr),
                    param("quaternion_xyzw", floatPtr)
                },
                true,
                "Wave718 static read-back: matrix4x4 build/update helper referenced by CFastVB__InitDispatchTableVariant_005980be; normalizes quaternion input with lazy constants, combines it with the basis matrix rows, handles aligned and unaligned output writes, and returns with RET 0xc. " + staticEvidence,
                signatureTags("matrix4x4", "quaternion", "basis-transform", "normalize", "dispatch-table", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun && (stats.bad != 0 || stats.missing != 0)) {
            throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
