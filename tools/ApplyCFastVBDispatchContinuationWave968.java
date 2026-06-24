//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCFastVBDispatchContinuationWave968 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(Address address) {
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function existing = functionAtEntry(address);
        if (existing != null) {
            return existing;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = getOrCreate(spec, dryRun, stats);
        if (fn == null) {
            return;
        }

        boolean renameNeeded = !fn.getName().equals(spec.name);
        boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
        boolean commentOrTagsNeedUpdate = fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec);

        if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else if (commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (signatureNeedsUpdate) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        }
        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
            stats.commentOnlyUpdated++;
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50L);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cfastvb-dispatch-continuation-wave968",
            "wave968-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "dispatch-table-target",
            "packed-mmx"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyCFastVBDispatchContinuationWave968 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005a6209",
                "CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209",
                "__stdcall",
                voidType,
                "Wave968 CFastVB dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x84 at 0x00598572. The block starts immediately after 0x005a6206 RET 0x8, writes three stack scalar values into diagonal-like 0x40-byte matrix output lanes with zero-fill and the constant at 0x005ef1c0, runs FEMMS, and returns with RET 0x10 at 0x005a624d. Static retail Ghidra evidence only; exact dispatch slot name, matrix layout, scalar meaning, hidden MMX/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret10", "slot-84", "scale-matrix"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("scale_x", floatType),
                    param("scale_y", floatType),
                    param("scale_z", floatType)
                }
            ),
            new Spec(
                "0x005ab06f",
                "CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f",
                "__stdcall",
                voidType,
                "Wave968 CFastVB dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x88 at 0x0059857c. The block starts immediately after 0x005ab06c RET 0x8 in the normalized-quaternion helper, unpacks the input four-float/qword pair from the second stack argument, multiplies it across the matrix-like qword lanes at the third stack argument, writes two output qwords through the first stack argument, runs FEMMS, and returns with RET 0xc at 0x005ab0ea. Static retail Ghidra evidence only; exact dispatch slot name, vector/matrix layout, packed lane order, hidden MMX/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret0c", "slot-88", "vec4-matrix-transform"),
                new ParameterImpl[] {
                    param("out_vec4_lanes", voidPtr),
                    param("in_vec4_lanes", voidPtr),
                    param("matrix4x4", voidPtr)
                }
            ),
            new Spec(
                "0x005a6250",
                "CFastVB__DispatchOp_TransposeMatrix4x4_005a6250",
                "__stdcall",
                voidType,
                "Wave968 CFastVB dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x94 at 0x0059859a. The block starts immediately after 0x005a624d RET 0x10, loads eight qword lanes from the source matrix-like block, uses PUNPCKLDQ/PUNPCKHDQ lane shuffles to transpose/repack the 0x40-byte block into the output pointer, runs FEMMS, and returns with RET 0x8 at 0x005a62bc. Static retail Ghidra evidence only; exact dispatch slot name, matrix layout, hidden MMX/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret08", "slot-94", "matrix-transpose"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("in_matrix4x4", voidPtr)
                }
            ),
            new Spec(
                "0x005a62f8",
                "CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8",
                "__stdcall",
                voidType,
                "Wave968 CFastVB dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this default body into dispatch-table slot +0x98 at 0x005985a4. The block starts immediately after 0x005a62f7 RET in the identity-matrix helper, expands the packed quaternion-like qword input through PFADD/PFMUL/PFSUBR operations against the 1.0 constant at 0x005ef100, writes a 0x40-byte rotation-matrix-style output block, runs FEMMS, and returns with RET 0x8 at 0x005a63c7. Static retail Ghidra evidence only; exact dispatch slot name, quaternion/matrix layout, packed lane order, scalar-vs-SIMD policy, hidden MMX/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret08", "slot-98", "quaternion-to-matrix", "default-dispatch"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("in_quaternion_lanes", voidPtr)
                }
            ),
            new Spec(
                "0x005a63ca",
                "CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca",
                "__stdcall",
                voidType,
                "Wave968 CFastVB dispatch continuation boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this feature-override body into dispatch-table slot +0x98 at 0x00598692 when feature bits 0x100 and 0x200 are both present. The block starts immediately after 0x005a63c7 RET 0x8, uses PSWAPD/PFPNACC/PFACC/PFMUL/PFSUBR lane operations on the packed quaternion-like input and the 1.0 constant at 0x005ef100, writes a 0x40-byte rotation-matrix-style output block, runs FEMMS, and returns with RET 0x8 at 0x005a647c before CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f. Static retail Ghidra evidence only; exact dispatch slot name, quaternion/matrix layout, packed lane order, feature-bit names, hidden MMX/register ABI, runtime CPU dispatch/math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret08", "slot-98", "quaternion-to-matrix", "feature-override"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("in_quaternion_lanes", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                stats.bad++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave968 CFastVB dispatch continuation apply encountered missing/bad rows");
        }
    }
}
