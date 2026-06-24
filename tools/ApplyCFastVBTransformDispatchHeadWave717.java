//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
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

public class ApplyCFastVBTransformDispatchHeadWave717 extends GhidraScript {
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
            "cfastvb-transform-dispatch-head-wave717",
            "wave717-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cfastvb-transform-dispatch-head"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cfastvb-transform-dispatch-head-wave717",
            "wave717-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-register-context",
            "cfastvb-transform-dispatch-head"
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
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        String staticEvidence = "Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact dispatch-table slot schema, vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        return new Spec[] {
            new Spec(
                "0x0059f360",
                "CFastVB__DispatchOp_TransformVec4_0059f360",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("input_vec4", voidPtr),
                    param("matrix4x4", voidPtr)
                },
                true,
                "Wave717 static read-back: SIMD dispatch-table entry referenced by CFastVB__InitDispatchTableVariant_005980be and _0059822c; transforms input_vec4 through matrix4x4, writes four floats to out_vec4, and returns with RET 0xc. " + staticEvidence,
                signatureTags("simd", "matrix4x4", "vec4", "transform", "dispatch-table", "tranche-head")
            ),
            new Spec(
                "0x0059f3d9",
                "CFastVB__DispatchOp_NormalizeVec4_0059f3d9",
                "__stdcall",
                floatPtr,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("input_vec4", voidPtr)
                },
                true,
                "Wave717 static read-back: SIMD dispatch-table entry referenced by CFastVB__InitDispatchTableVariant_005980be and _0059822c; computes a vec4 length square, uses rsqrtss plus one Newton-style refinement, writes normalized components, and returns with RET 0x8. " + staticEvidence,
                signatureTags("simd", "vec4", "normalize", "reciprocal-sqrt", "dispatch-table")
            ),
            new Spec(
                "0x0059f473",
                "CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("input_vec4", voidPtr)
                },
                true,
                "Wave717 static read-back: SIMD dispatch-table entry referenced by CFastVB__InitDispatchTableVariant_005980be; normalizes input_vec4 with reciprocal approximation, applies component scale constants from 0x0065e500, writes out_vec4, and returns with RET 0x8. " + staticEvidence,
                signatureTags("simd", "vec4", "normalize", "scaled", "dispatch-table")
            ),
            new Spec(
                "0x0059f4f1",
                "CFastVB__DispatchOp_EulerToQuaternion_0059f4f1",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("angle_x_radians", floatType),
                    param("angle_y_radians", floatType),
                    param("angle_z_radians", floatType)
                },
                true,
                "Wave717 static read-back: SIMD dispatch-table entry referenced by CFastVB__InitDispatchTableVariant_005980be; scales three Euler inputs, calls CFastVB__SinCosApproxVec4_Paired, writes four quaternion-style floats, and returns with RET 0x10. " + staticEvidence,
                signatureTags("simd", "quaternion", "euler", "dispatch-table")
            ),
            new Spec(
                "0x0059f5b3",
                "CFastVB__BuildOrthonormalBasisFromCovariance",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("matrix3x3_or_basis", voidPtr)
                },
                true,
                "Wave717 static read-back: SIMD-adjacent helper referenced by CFastVB__InitDispatchTableVariant_005980be; branches on the matrix trace, chooses the maximum diagonal fallback when needed, and writes four quaternion-style output floats from matrix3x3_or_basis. " + staticEvidence,
                signatureTags("simd-adjacent", "quaternion", "matrix3x3", "trace-branch", "dispatch-table")
            ),
            new Spec(
                "0x0059f6dd",
                "CFastVB__BroadcastMatrix4x4ToSIMDLanes",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("simd_lane_matrix_out", voidPtr),
                    param("matrix4x4", voidPtr)
                },
                true,
                "Wave717 static read-back: shared helper called by the batch transform family; broadcasts each source matrix4x4 scalar into four-wide lane blocks at offsets 0x00 through 0xfc, and read-back instruction evidence shows RET 0x4. The apply log preserves the initial Ghidra thiscall normalization mismatch before aligning to the saved explicit receiver spelling. " + staticEvidence,
                signatureTags("simd", "matrix4x4", "lane-broadcast", "batch-transform")
            ),
            new Spec(
                "0x0059f857",
                "CFastVB__DispatchOp_TransformVec4Batch_0059f857",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: batch Vec4 transform dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; groups vector_count by fours, calls CFastVB__BroadcastMatrix4x4ToSIMDLanes, emits SIMD matrix products, and tails through CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200. Signature intentionally left unchanged because the decompile still reports unknown calling convention, locked parameter storage, and hidden EDI context. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec4", "batch-transform", "tail-scalar-dispatch")
            ),
            new Spec(
                "0x0059fa5d",
                "CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: batch Vec4W transform dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; processes four records at a time with a broadcast matrix and tails through dispatch slot 0x00656f30 while the decompile keeps hidden EBX/EDI context. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec4", "batch-transform", "hidden-ebx-context", "tail-dispatch")
            ),
            new Spec(
                "0x0059fbeb",
                "CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: batch projected Vec4 transform dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; broadcasts matrix lanes, computes W terms, uses rcpps plus refinement for reciprocal projection, and tails through dispatch slot 0x00656f54. Signature intentionally left unchanged because Ghidra reports unknown calling convention, locked parameter storage, and hidden EBX/EDI context. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec4", "perspective-transform", "batch-transform", "hidden-ebx-context")
            ),
            new Spec(
                "0x0059fd51",
                "CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: no-offset batch Vec4 transform dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; multiplies vector components by broadcast matrix lane blocks without translation offsets and tails through dispatch slot 0x00656f44. Signature intentionally left unchanged because Ghidra reports unknown calling convention, locked parameter storage, and hidden EBX/EDI context. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec4", "batch-transform", "no-offset", "hidden-ebx-context")
            ),
            new Spec(
                "0x0059fe61",
                "CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: perspective-flavored batch transform dispatch referenced multiple times by CFastVB__InitDispatchTableVariant_005980be; uses broadcast matrix lanes, writes four output records per loop, and tails through CFastVB__DispatchOp_TransformVec2ByMatrix4 for remaining records. Signature intentionally left unchanged because Ghidra reports unknown calling convention, locked parameter storage, and hidden EDI context. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec4", "perspective-transform", "batch-transform", "tail-scalar-dispatch")
            ),
            new Spec(
                "0x005a009f",
                "CFastVB__DispatchOp_TransformVec3WBatch_005a009f",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: batch Vec3W transform dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; broadcasts matrix lanes, writes three-float outputs with W contribution, and tails through CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1. Signature intentionally left unchanged because Ghidra reports unknown calling convention, locked parameter storage, and hidden EDI context. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec3", "batch-transform", "tail-scalar-dispatch")
            ),
            new Spec(
                "0x005a026f",
                "CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: batch projected Vec3W transform dispatch referenced by CFastVB__InitDispatchTableVariant_005980be; broadcasts matrix lanes, computes reciprocal projected components, and tails through CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786. Signature intentionally left unchanged because Ghidra reports unknown calling convention, locked parameter storage, and hidden EDI context. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "vec3", "perspective-transform", "batch-transform", "tail-scalar-dispatch")
            ),
            new Spec(
                "0x005a04a0",
                "CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave717 static read-back: weighted matrix/blend batch dispatch referenced by CFastVB__InitDispatchTableVariant_005980be and _0059822c; iterates weighted matrix indices, performs projected matrix-vector blends, copies stride-separated payload bytes, and optionally accumulates auxiliary vector outputs. Signature intentionally left unchanged because Ghidra reports unknown calling convention and locked parameter storage across a large stack-argument contract. " + staticEvidence,
                commentOnlyTags("simd", "matrix4x4", "weighted-blend", "batch-transform", "auxiliary-vector-output", "tranche-tail")
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
