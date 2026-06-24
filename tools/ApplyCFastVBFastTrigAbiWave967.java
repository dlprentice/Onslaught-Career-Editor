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

public class ApplyCFastVBFastTrigAbiWave967 extends GhidraScript {
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
            "cfastvb-fast-trig-abi-review-wave967",
            "wave967-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "dispatch-table-target",
            "packed-mmx",
            "fast-trig"
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
        println("ApplyCFastVBFastTrigAbiWave967 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005a4c67",
                "CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67",
                "__stdcall",
                voidType,
                "Wave967 CFastVB fast-trig ABI boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x64 at 0x00598537. The block starts immediately after a RET at 0x005a4c64, multiplies packed qword stack lanes, calls CFastVB__FastTrigPairApprox_Scalar three times at 0x005a4c89/0x005a4c9a/0x005a4ca9, writes two qword quaternion-like output lanes through the first stack argument, runs FEMMS, and returns with RET 0x10. Static retail Ghidra evidence only; exact dispatch slot name, input lane order, vector/quaternion layout, packed MMX register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret10", "slot-64", "quaternion-fast-trig"),
                new ParameterImpl[] {
                    param("out_quaternion_lanes", voidPtr),
                    param("packed_lane_arg2", intType),
                    param("packed_lane_arg3", intType),
                    param("packed_lane_arg4", intType)
                }
            ),
            new Spec(
                "0x005a60ef",
                "CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef",
                "__stdcall",
                voidType,
                "Wave967 CFastVB fast-trig ABI boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x78 at 0x0059855a. The block starts immediately after a RET at 0x005a60ec, loads the angle argument into MM0, calls CFastVB__FastTrigPairApprox_Scalar at 0x005a60f8, writes a 0x40-byte X-axis rotation-matrix-style output block through the first stack argument, runs FEMMS, and returns with RET 0x8. Static retail Ghidra evidence only; exact dispatch slot name, matrix layout, packed angle/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret08", "slot-78", "rotation-matrix-x"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                }
            ),
            new Spec(
                "0x005a6152",
                "CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152",
                "__stdcall",
                voidType,
                "Wave967 CFastVB fast-trig ABI boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x7c at 0x00598561. The block starts immediately after a RET at 0x005a614f, loads the angle argument into MM0, calls CFastVB__FastTrigPairApprox_Scalar at 0x005a615b, writes a 0x40-byte Y-axis rotation-matrix-style output block through the first stack argument, runs FEMMS, and returns with RET 0x8. Static retail Ghidra evidence only; exact dispatch slot name, matrix layout, packed angle/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret08", "slot-7c", "rotation-matrix-y"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                }
            ),
            new Spec(
                "0x005a61b0",
                "CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0",
                "__stdcall",
                voidType,
                "Wave967 CFastVB fast-trig ABI boundary recovery: CFastVB__InitDispatchOpsFromFeatureFlags stores this body into dispatch-table slot +0x80 at 0x00598568. The block starts immediately after a RET at 0x005a61ad, loads the angle argument into MM0, calls CFastVB__FastTrigPairApprox_Scalar at 0x005a61b9, writes a 0x40-byte Z-axis rotation-matrix-style output block through the first stack argument, runs FEMMS, and returns with RET 0x8. Static retail Ghidra evidence only; exact dispatch slot name, matrix layout, packed angle/register ABI, runtime math behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ret08", "slot-80", "rotation-matrix-z"),
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
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
            throw new IllegalStateException("Wave967 CFastVB fast-trig ABI apply encountered missing/bad rows");
        }
    }
}
