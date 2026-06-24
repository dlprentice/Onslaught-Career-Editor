//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyMonitorOidBallisticWave553 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "monitor-oid-ballistic-wave553",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
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
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }
            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005078f0",
                "CMonitor__UpdateTrackedRenderPair",
                "CMonitor__UpdateTrackedRenderPair",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("update_projected_volume", intType)
                },
                "Wave553 signature/comment hardening: RET 0x4 and callsites from CMonitor__UpdateMovementTransitionAndEffects and CBattleEngineWalkerPart__Move prove one explicit update_projected_volume flag after ECX. The body walks two tracked render slots at this +0x18/+0x20, calls the owner vfunc +300 to refresh transform state, copies basis data into linked render objects, and when the flag is nonzero applies optional projected-volume orientation data from owner +0xa0/+0x5c before marking the render object at +0xa0. Static retail-binary evidence only; exact Monitor source identity, concrete object layouts, runtime render behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("monitor", "render-pair", "projected-volume", "phantom-param-removed")
            ),
            new Spec(
                "0x00507ab0",
                "OID__CanFireAtTarget_BallisticArcA",
                "OID__CanFireAtTarget_BallisticArcA",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_unit", voidPtr()),
                    param("ballistic_context", intType)
                },
                "Wave553 signature/comment hardening: RET 0x8 and the CUnit__CanFireAtTarget_BallisticArcA callsite prove two explicit stack arguments after ECX; the older third explicit parameter was register carryover. The body checks attachment/origin height, fear-grid clearance, target yaw/pitch windows, ballistic-arc statement state, optional trace context, and line hits through CLine/OID__TraceLineAndSelectBestTargetHit before returning a fire-eligibility boolean. Static retail-binary evidence only; exact boolean contract, concrete OID/target/weapon-statement layouts, runtime weapon behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("oid", "projectile-ballistics", "fire-eligibility", "phantom-param-removed")
            ),
            new Spec(
                "0x005088b0",
                "OID__CanFireAtTarget_BallisticArcB",
                "OID__CanFireAtTarget_BallisticArcB",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_unit", voidPtr())
                },
                "Wave553 signature/comment hardening: RET 0x4 and the CUnit__CanFireAtTarget_BallisticArcB callsite prove one explicit target_unit argument after ECX; the older second explicit parameter was register carryover. The body checks attachment/origin height, fear-grid clearance, target-relative pitch and ballistic profile windows, static-shadow fallback behavior, and optional CLine/OID__TraceLineAndSelectBestTargetHit visibility before returning a fire-eligibility boolean. Static retail-binary evidence only; exact boolean contract, concrete OID/target/profile layouts, runtime weapon behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("oid", "projectile-ballistics", "fire-eligibility", "phantom-param-removed")
            ),
            new Spec(
                "0x00509140",
                "OID__UpdateAimTransformAndAttachTargetReader",
                "OID__UpdateAimTransformAndAttachTargetReader",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_reader", voidPtr()),
                    param("target_transform", voidPtr())
                },
                "Wave553 signature/comment hardening: RET 0x8 and CUnit__ForwardAimTransformAndAttachTargetReader callsite instructions prove two explicit stack arguments after ECX; the older third explicit parameter was register carryover. The body uses target_transform to compute/copy target-vector state at this +0x84..+0x90, updates aim orientation through direct or ballistic pitch paths, sets the dirty flag at +0x80, and registers target_reader through CGenericActiveReader__SetReader at this +0x2c. Static retail-binary evidence only; exact argument order at higher-level wrappers, concrete reader/transform/OID layouts, runtime aim behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("oid", "aim-transform", "active-reader", "phantom-param-removed")
            ),
            new Spec(
                "0x005094b0",
                "OID__SolveBallisticPitchToTarget",
                "OID__SolveBallisticPitchToTarget",
                "__thiscall",
                doubleType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_x", floatType),
                    param("target_y", floatType),
                    param("target_z", floatType),
                    param("target_w", floatType)
                },
                "Wave553 signature/comment hardening: RET 0x10 and CUnit/Warspite callsite vector copies prove four explicit stack dwords after ECX; the first three are used as target_x/target_y/target_z and target_w is carried by the 16-byte vector convention but unused in the current decompile. The body solves a pitch angle from target position, owner origin, ballistic speed/gravity profile fields, and active pitch-window fields at owner +0xa0 offsets +0x7c/+0x80, with a direct acos fallback. Static retail-binary evidence only; exact math contract, concrete OID/profile layouts, runtime aiming behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("oid", "projectile-ballistics", "pitch-solver", "vector-target")
            ),
            new Spec(
                "0x005096a0",
                "CUnit__ComputeMinBallisticTravelDistance",
                "CUnit__ComputeMinBallisticTravelDistance",
                "__thiscall",
                doubleType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_x", floatType),
                    param("target_y", floatType),
                    param("target_z", floatType),
                    param("target_w", floatType)
                },
                "Wave553 signature/comment hardening: RET 0x10 and auto-aim/range-classifier/support callsites prove four explicit vector dwords after ECX; the first three carry target_x/target_y/target_z while target_w is part of the copied 16-byte vector convention. Non-ballistic statements return owner +0xa0 field +0x74; ballistic statements derive a minimum reachable travel distance from target height, launch speed, gravity, and active pitch-window fields. Static retail-binary evidence only; exact range semantics, concrete CUnit/OID/profile layouts, runtime targeting behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cunit", "projectile-ballistics", "range-distance", "vector-target")
            ),
            new Spec(
                "0x005099a0",
                "CUnit__ComputeMaxBallisticTravelDistance",
                "CUnit__ComputeMaxBallisticTravelDistance",
                "__thiscall",
                doubleType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_x", floatType),
                    param("target_y", floatType),
                    param("target_z", floatType),
                    param("target_w", floatType)
                },
                "Wave553 signature/comment hardening: RET 0x10 and callers from auto-aim, range classification, support selection, ProjectileBurst, and projectile caller boundaries prove four explicit vector dwords after ECX. Non-ballistic statements return owner +0xa0 field +0x78; ballistic statements derive a maximum reachable travel distance from target height, launch speed, gravity, and active pitch-window fields. Static retail-binary evidence only; exact range semantics, concrete CUnit/OID/profile layouts, runtime targeting/projectile behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cunit", "projectile-ballistics", "range-distance", "vector-target")
            ),
            new Spec(
                "0x00509c80",
                "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
                "CBattleEngine__ComputeProjectileMetricFromTargetProfile",
                "__thiscall",
                doubleType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("target_x", floatType),
                    param("target_y", floatType),
                    param("target_z", floatType),
                    param("target_w", floatType)
                },
                "Wave553 signature/comment hardening: RET 0x10 and CBattleEngine__CalcUnitOverCrossHair callsite vector copies prove four explicit vector dwords after ECX. When an active ballistic profile is available the body forwards the target vector to CUnit__ComputeMaxBallisticTravelDistance; otherwise it selects a target/profile entry from DAT_008553ec by range bucket and returns one of several projectile metric fields or speed/range products. Static retail-binary evidence only; exact profile metric meaning, concrete BattleEngine/target-profile layouts, runtime targeting behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("battleengine", "projectile-ballistics", "target-profile", "vector-target")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply")
            + " updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave553 apply had missing/bad rows");
        }
    }
}
