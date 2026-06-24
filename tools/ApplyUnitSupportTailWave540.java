//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyUnitSupportTailWave540 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                String[] allowedExistingNames) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unit-support-tail-wave540",
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!allowedName(spec, fn.getName())) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        boolean update = needsUpdate(fn, spec);
        if (dryRun) {
            if (needsRename) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.wouldRename++;
            } else {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
            }
            stats.skipped++;
            return;
        }
        if (!update) {
            println("SKIP: " + spec.address + " already current");
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
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
        println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004fd230",
                "CUnit__SpawnProfileDropPickup",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave540 Unit support-tail owner/signature correction: register-only helper reached from Unit, AirUnit, Plane, hit, reset, and event paths before death/reset dispatch. When this+0x164 profile exists, it creates a pickup through CWorldPhysicsManager__CreatePickup using profile +0xe8, builds a local CInitThing-style record, copies side/team field this+0x138 and world position this+0x1c..0x28, derives a small init flag from vfunc +0x10c or HeightDelta__Below025_D0, and initializes the pickup via vfunc +0x24. Static retail evidence only; exact pickup table/layout, source identity, runtime drop behavior, and rebuild parity remain unproven.",
                tags("unit-pickup", "profile-driven", "owner-corrected", "renamed"),
                new String[] {"CExplosionInitThing__ctor_like_004fd230"}
            ),
            new Spec(
                "0x004fd3d0",
                "CUnit__IsCandidateSideCompatibleForTargeting",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("candidate_side", intType)},
                "Wave540 Unit support-tail owner/signature correction: RET 0x4 proves one explicit candidate_side stack argument after ECX; the prior third parameter was stale register carryover. Targeting, firing, collision, monitor, and round-selection callers pass candidate side/team values read from target/context +0x138 while ECX is the querying unit-like object. The body compares candidate_side against this+0x138 and allows candidate_side 2 only when profile field this+0x164->0x128 is set. Static retail evidence only; exact side/team enum names, profile field semantics, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("unit-targeting", "side-team-filter", "owner-corrected", "renamed"),
                new String[] {"CBattleEngine__IsWeaponModeCompatibleWithMountState"}
            ),
            new Spec(
                "0x004fd500",
                "CUnit__ApplyRenderPositionDeltaToVector",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("inout_position", voidPtr)},
                "Wave540 Unit/HUD support-tail owner/signature correction: RET 0x4 proves one explicit inout_position stack argument after ECX; the prior third parameter was stale register carryover. HUD target-marker and world-target sprite callers pass a mutable vector. The body first calls vfunc +0x168 on that vector, then adds the delta between CActor__GetRenderPos(this+8) and vfunc +0x78 output to the vector. Static retail evidence only; exact actor/unit subobject layout, vector type, HUD marker behavior, and rebuild parity remain unproven.",
                tags("unit-render-position", "hud-target-marker", "owner-corrected", "renamed"),
                new String[] {"CExplosionInitThing__ApplyModelSpaceOffsetDelta"}
            ),
            new Spec(
                "0x004fd570",
                "CSquadNormal__HasAnyLinkedUnitWithField94",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave540 CSquadNormal support-tail signature/comment hardening: register-only list scan used by CSquadNormal prune/build-formation callers. The body walks the linked list at this+0x17c and returns true when any linked unit/object has nonzero field +0x94. Static retail evidence only; exact linked-list type, +0x94 field semantics, squad formation behavior, and rebuild parity remain unproven.",
                tags("squad-normal", "linked-unit-list", "query"),
                new String[] {}
            ),
            new Spec(
                "0x004fd5e0",
                "CUnit__VFunc26_GetRecentSegmentDamageMeter",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("segment_index", intType)},
                "Wave540 Unit support-tail vfunc-slot correction: RET 0x4 proves one explicit segment_index stack argument after ECX; the prior third parameter was stale register carryover. Vtable export shows this body in slot 26 across many CUnit-family vtables. The body returns this+0x210 when no destructible-segment controller exists at +0x170; otherwise it queries recent segment damage time/amount, calls an adjusted this-8 vfunc +0x1ac with the damage amount, sets +0x214 to 10, and returns a clamped 0..100 decaying meter. Static retail evidence only; exact adjusted-subobject owner, meter semantics, runtime damage UI/logic, and rebuild parity remain unproven.",
                tags("unit-vfunc-slot-26", "destructible-segment", "damage-meter", "renamed"),
                new String[] {"VFuncSlot_26_004fd5e0"}
            ),
            new Spec(
                "0x004fd6a0",
                "CUnit__VFunc22_ActivateLinkedTargetsAndChildren",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave540 Unit support-tail vfunc-slot correction: register-only slot-22 helper used by UnitAI activation-state callers and many CUnit-family vtables. If state field this+0x214 is clear, the body sets it to 1, dispatches linked target/reader at this+0x148 through vfunc +0x58, then walks child/linked readers at this+0x19c and dispatches each through vfunc +0x58. Source CThing exposes Activate/Deactivate virtual slots, but this comment is bounded to retail slot/caller evidence. Exact derived-class coverage, linked-reader layout, runtime activation behavior, and rebuild parity remain unproven.",
                tags("unit-vfunc-slot-22", "activation", "linked-reader", "renamed"),
                new String[] {"VFuncSlot_22_004fd6a0"}
            ),
            new Spec(
                "0x004fd700",
                "CUnit__VFunc23_DeactivateLinkedTargetsAndChildren",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave540 Unit support-tail vfunc-slot correction: register-only slot-23 helper used by UnitAI activation-state callers and many CUnit-family vtables. If state field this+0x214 is set, the body clears it to 0, dispatches linked target/reader at this+0x148 through vfunc +0x5c, then walks child/linked readers at this+0x19c and dispatches each through vfunc +0x5c. Source CThing exposes Activate/Deactivate virtual slots, but this comment is bounded to retail slot/caller evidence. Exact derived-class coverage, linked-reader layout, runtime deactivation behavior, and rebuild parity remain unproven.",
                tags("unit-vfunc-slot-23", "deactivation", "linked-reader", "renamed"),
                new String[] {"VFuncSlot_23_004fd700"}
            ),
            new Spec(
                "0x004fd760",
                "CUnit__HasAnyLinkedUnitBeforeTargetTimeout",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave540 Unit support-tail owner/signature correction: register-only list scan over this+0x17c used by GillMHeadAI and transition/state helpers. The body returns true when any linked unit/object passes CUnit__IsTargetTimeoutBeforeProfileLimit. The previous CVBufTexture owner prefix is stale for this Unit-family field/caller pattern. Static retail evidence only; exact linked-list ownership, timeout/profile semantics, transition behavior, and rebuild parity remain unproven.",
                tags("unit-targeting", "linked-unit-list", "timeout-filter", "owner-corrected", "renamed"),
                new String[] {"CVBufTexture__HasAnyTrackedUnitBeforeTimeout"}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave540 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
