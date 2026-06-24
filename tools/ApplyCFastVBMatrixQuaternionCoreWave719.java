//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCFastVBMatrixQuaternionCoreWave719 extends GhidraScript {
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
            "cfastvb-matrix-quaternion-core-wave719",
            "wave719-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-matrix-quaternion-core"
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
                } else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " " + expectedSignature(spec));
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
            } else {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType ushortPtr = new PointerDataType(UnsignedShortDataType.dataType);
        String boundary = " Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact dispatch-table slot schema, vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        return new Spec[] {
            new Spec(
                "0x005a298f",
                "CFastVB__ConvertHalfToFloatArray_SIMD",
                "__stdcall",
                IntegerDataType.dataType,
                new ParameterImpl[] {
                    param("out_float32", floatPtr),
                    param("in_float16", ushortPtr),
                    param("element_count", UnsignedIntegerDataType.dataType)
                },
                "Wave719 static read-back: SIMD half-float conversion dispatch referenced by CFastVB__InitDispatchTableVariant_0059822c; processes eight half-float inputs per loop through CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD, tails scalar ushort inputs into float output slots, and returns the original output pointer as an int-compatible value." + boundary,
                tags("half-float", "float32", "simd", "conversion", "dispatch-table", "tranche-head")
            ),
            new Spec(
                "0x005a2a61",
                "CFastVB__DispatchOp_TransformVec2ByMatrix4",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("input_vec4", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                "Wave719 static read-back: scalar transform dispatch referenced by both CFastVB dispatch-table variants and called by perspective batch tails; reads input x/y plus existing z/w lanes, handles aligned and unaligned matrix loads, and writes four transformed output floats." + boundary,
                tags("vec2", "vec4-output", "matrix4x4", "transform", "tail-scalar-dispatch", "dispatch-table")
            ),
            new Spec(
                "0x005a2b2d",
                "CFastVB__InvertMatrix4x4_WithDeterminant",
                "__stdcall",
                new PointerDataType(FloatDataType.dataType),
                new ParameterImpl[] {
                    param("out_inverse_matrix4x4", floatPtr),
                    param("out_determinant_or_null", floatPtr),
                    param("input_matrix4x4", floatPtr)
                },
                "Wave719 static read-back: matrix4x4 inverse helper referenced by both CFastVB dispatch-table variants; computes cofactors and determinant, writes the determinant when the optional output pointer is non-null, returns null when determinant is zero, otherwise writes a reciprocal-determinant-scaled inverse matrix." + boundary,
                tags("matrix4x4", "inverse", "determinant", "cofactor", "dispatch-table")
            ),
            new Spec(
                "0x005a2e29",
                "CFastVB__ComputeAdjugateVec4_PackedB",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("row_a_vec4", floatPtr),
                    param("row_b_vec4", floatPtr),
                    param("row_c_vec4", floatPtr)
                },
                "Wave719 static read-back: packed adjugate/cofactor Vec4 helper referenced by CFastVB__InitDispatchTableVariant_0059822c; reads three Vec4 rows, combines 3x3 minor products, applies sign masks from the 0x0065e7a0 constant block, and writes four float-bit output lanes." + boundary,
                tags("adjugate", "cofactor", "vec4", "matrix", "dispatch-table")
            ),
            new Spec(
                "0x005a2ee9",
                "CFastVB__DispatchOp_Determinant4x4_005a2ee9",
                "__stdcall",
                DoubleDataType.dataType,
                new ParameterImpl[] {
                    param("matrix4x4", floatPtr)
                },
                "Wave719 static read-back: determinant dispatch referenced by both CFastVB dispatch-table variants; handles aligned and unaligned matrix loads and expands a 4x4 determinant from row/column minors. Return type remains Ghidra's current double because the decompiler materializes the scalar float expression through the x87-style return model." + boundary,
                tags("matrix4x4", "determinant", "dispatch-table", "x87-return-model")
            ),
            new Spec(
                "0x005a2ff4",
                "CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_plane_vec4", floatPtr),
                    param("point_a_vec3", floatPtr),
                    param("point_b_vec3", floatPtr),
                    param("point_c_vec3", floatPtr)
                },
                "Wave719 static read-back: alternate plane-from-triangle dispatch referenced by CFastVB__InitDispatchTableVariant_0059822c; forms edge deltas, computes the cross-product normal, normalizes with rsqrtss refinement, writes xyz normal, and stores a sign-masked distance term." + boundary,
                tags("plane", "triangle", "cross-product", "normalize", "dispatch-table")
            ),
            new Spec(
                "0x005a30f4",
                "CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("quaternion_xyzw", floatPtr)
                },
                "Wave719 static read-back: alternate quaternion-to-matrix4 dispatch referenced by CFastVB__InitDispatchTableVariant_0059822c; masks/normalizes quaternion lanes with rsqrtss refinement and expands the normalized quaternion into sixteen matrix floats using the 0x0065e7e0..0x0065e85c constant block." + boundary,
                tags("quaternion", "matrix4x4", "normalize", "dispatch-table")
            ),
            new Spec(
                "0x005a3200",
                "CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_vec4", floatPtr),
                    param("input_vec4", floatPtr),
                    param("matrix4x4", floatPtr)
                },
                "Wave719 static read-back: scalar Vec4-by-matrix dispatch referenced by both CFastVB dispatch-table variants and called by Vec4 batch tails; handles aligned and unaligned matrix loads, combines input lanes with matrix columns/translation, and writes four output floats." + boundary,
                tags("vec4", "matrix4x4", "transform", "tail-scalar-dispatch", "dispatch-table")
            ),
            new Spec(
                "0x005a32d4",
                "CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("left_matrix4x4", floatPtr),
                    param("right_matrix4x4", floatPtr)
                },
                "Wave719 static read-back: matrix4x4 multiply dispatch referenced by both CFastVB dispatch-table variants; reads left and right 4x4 matrices and writes sixteen output floats as row/column dot products." + boundary,
                tags("matrix4x4", "multiply", "dispatch-table")
            ),
            new Spec(
                "0x005a3508",
                "CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_matrix4x4", floatPtr),
                    param("basis_quaternion_xyzw", floatPtr),
                    param("rotation_quaternion_xyzw", floatPtr)
                },
                "Wave719 static read-back: quaternion-pair-to-matrix dispatch referenced by CFastVB__InitDispatchTableVariant_0059822c; normalizes the rotation quaternion with lazy constants, combines it with a basis quaternion-like input, and writes an aligned or unaligned 4x4 matrix output." + boundary,
                tags("quaternion", "matrix4x4", "basis-transform", "normalize", "dispatch-table")
            ),
            new Spec(
                "0x005a36cf",
                "CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", floatPtr),
                    param("angle_x_radians", FloatDataType.dataType),
                    param("angle_y_radians", FloatDataType.dataType),
                    param("angle_z_radians", FloatDataType.dataType)
                },
                "Wave719 static read-back: Euler-angle-to-quaternion dispatch referenced by CFastVB__InitDispatchTableVariant_0059822c; scales three angle inputs, calls CFastVB__SinCosVec4Approx, combines sine/cosine products, and writes four quaternion floats." + boundary,
                tags("quaternion", "euler-angles", "sincos", "dispatch-table")
            ),
            new Spec(
                "0x005a3791",
                "CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", floatPtr),
                    param("matrix3x3", floatPtr)
                },
                "Wave719 static read-back: matrix3x3-to-quaternion dispatch referenced by CFastVB__InitDispatchTableVariant_0059822c; uses trace-positive and largest-diagonal fallback branches, square-root scaling, and axis-index table 0x005f4340 to write four quaternion floats." + boundary,
                tags("quaternion", "matrix3x3", "trace", "dispatch-table", "tranche-tail")
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

        println("ApplyCFastVBMatrixQuaternionCoreWave719 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave719 CFastVB matrix/quaternion core apply had missing/bad rows");
        }
    }
}
