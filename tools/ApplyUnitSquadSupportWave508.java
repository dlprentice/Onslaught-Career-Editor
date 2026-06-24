//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyUnitSquadSupportWave508 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
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
            "unit-squad-support-wave508",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.newName).append("(");
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e43d0",
                "CUnit__CanProvideSupportNow",
                "CUnit__CanProvideSupportNow",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CUnit support/spawn readiness predicate. The ECX-only body requires this+0x3f4 support data, this+0x3ec clear, DAT_00672fd0 past the this+0x3e0 cooldown, this+0x3d0 profile data, and either this+0x3d8 below profile+0xc or profile+0x24 set. Static retail evidence only; exact support-profile layout, runtime squad/spawner behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "support-readiness", "predicate")
            ),
            new Spec(
                "0x004e4420",
                "CUnit__IsInBlockedSupportState",
                "CUnit__IsInBlockedSupportState",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CUnit support-block predicate. The ECX-only body returns whether this+0x3ec is non-zero; retail callers use it from Unit, UnitAI, and CSquadNormal support/deploy paths. Static retail evidence only; exact field semantics, runtime support/deploy behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "support-readiness", "predicate")
            ),
            new Spec(
                "0x004e4480",
                "CSquadNormal__IsTargetMaskCompatible",
                "CUnit__IsSupportTargetMaskCompatible",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("target", voidPtr)},
                "Wave508 stale-owner correction: support target-mask predicate for a CUnit-style object, not a CSquadNormal object method. The body uses ECX fields this+0x3f4, this+0x3d0, this+0x3d8, and this+0x3f0, then tests target+0x34 against the mask; RET 0x4 proves one explicit target argument. Static retail evidence only; exact target flag meanings, support-profile layout, runtime targeting behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "support-readiness", "target-mask", "stale-owner-corrected")
            ),
            new Spec(
                "0x004e4d70",
                "CSphere__VFunc_02_004e4d70",
                "CSphere__VFunc02_ResolveCollisionAsCylinder",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("collision_arg0", voidPtr),
                    param("collision_arg1", voidPtr),
                    param("collision_arg2", voidPtr),
                    param("collision_flags", intType)
                },
                "Wave508 signature/name hardening: CSphere vfunc-slot-2 collision proxy. The body builds a temporary CCylinder-style descriptor with vtable 0x005d88cc, radius this+0x14, and radius squared, then delegates to CCylinder__ResolveCollisionVFunc02 with four forwarded stack arguments; DATA vtable evidence is at 0x005d95f0. Static retail evidence only; exact collision argument layouts, sphere/cylinder source identity, runtime collision behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("sphere", "collision", "vfunc-slot-2", "collision-proxy")
            ),
            new Spec(
                "0x004e5da0",
                "CSquad__ctor_like_004e5da0",
                "CSquad__Constructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/name hardening: CSquad constructor-like base body. The ECX-only body calls CThing__ctor_like_004f3e10, installs CSquad vtables 0x005def1c and 0x005deea4, clears this+0x80 and this+0x84, and returns this; callers include CSquadNormal__Constructor and CWorldPhysicsManager__CreateSquad. Static retail evidence only; exact CSquad layout, source constructor identity, runtime squad creation behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad", "constructor", "vtable-backed")
            ),
            new Spec(
                "0x004e5e50",
                "VFuncSlot_01_004e5e50",
                "SharedComplexThing__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave508 shared-wrapper correction: scalar-deleting destructor target shared by multiple CComplexThing-derived vtables rather than a CSquad-only body. The wrapper calls CComplexThing__dtor_base_Thunk_004bff30, conditionally frees this through CDXMemoryManager__Free when flags bit 0 is set, returns this, and ends with RET 0x4. Static retail evidence only; exact owner coverage, allocator ownership, runtime destruction ordering, BEA launch, patching, and rebuild parity remain unproven.",
                tags("shared-vfunc", "scalar-deleting-destructor", "complexthing")
            ),
            new Spec(
                "0x004e65b0",
                "CSquad__VFunc_02_004e65b0",
                "CSquad__VFunc02_RemoveFromGlobalLists",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/name hardening: CSquad vfunc-slot-2 removal wrapper. The ECX-only body removes this from global squad lists DAT_008550c0, DAT_008550b0, and DAT_008550a0, then delegates to shared VFuncSlot_02_004f41b0. Static retail evidence only; exact virtual contract, global-list semantics, runtime cleanup behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad", "global-list", "vfunc-slot-2")
            ),
            new Spec(
                "0x004e65e0",
                "VFuncSlot_00_004e65e0",
                "CSquad__HandleEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)},
                "Wave508 signature/name hardening: CSquad event handler. RET 0x4 proves one explicit event argument; non-0xfa2 events delegate to CComplexThing__HandleEvent, while event code 0xfa2 dispatches the CSquad virtual target at vtable +0x108. Static retail evidence only; exact event meaning, virtual contract, runtime scheduler behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad", "event", "vfunc-slot-0")
            ),
            new Spec(
                "0x004e6660",
                "CUnit__ResetDamageCooldownTimer",
                "CUnit__ResetDamageCooldownTimer",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CUnit damage-cooldown timer reset helper. The ECX-only body writes this+0x88 to DAT_00672fd0 plus the constant at 0x005d85d8; the only direct caller in the read-back tranche is CUnit__ApplyDamage. Static retail evidence only; exact cooldown duration semantics, runtime damage behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "damage-cooldown")
            ),
            new Spec(
                "0x004e6680",
                "CSquadNormal__IsFactionCompatible",
                "CSquadNormal__IsFactionCompatible",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("candidate_faction_state", intType)},
                "Wave508 signature/comment hardening: CSquadNormal faction/state compatibility predicate. RET 0x4 proves one explicit candidate_faction_state argument; the body compares that value with this+0x7c and admits only the observed 0/1/6 compatibility cases used by CSquadNormal__SelectBestEngagementTarget. Static retail evidence only; exact faction enum names, target-selection semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "faction-compatibility", "predicate")
            ),
            new Spec(
                "0x004e66e0",
                "CUnit__RenderWithIdentityWorldAndShadowProbe",
                "CUnit__RenderWithIdentityWorldAndShadowProbe",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CUnit-family render helper with static-shadow probe. The ECX-only body copies the world-matrix constants from DAT_0083d148, calls CDXEngine__SetWorldMatrixElements, dispatches this vtable slot +0x40, then samples CStaticShadows__SampleShadowHeightBilinear at this+0x1c. Static retail evidence only; exact owner coverage, render contract, shadow sample side effects, runtime rendering behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("unit", "render", "static-shadows")
            ),
            new Spec(
                "0x004e6870",
                "CSquadNormal__Constructor",
                "CSquadNormal__Constructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal constructor-like body. The ECX-only body calls CSquad__Constructor, initializes the embedded set at this+0xa4, allocates two array-backed records via OID__AllocObject, installs vtables 0x005df0f4 and 0x005df07c, seeds default fields, and returns this. Static retail evidence only; exact CSquadNormal layout, array element type, runtime squad creation behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "constructor", "vtable-backed")
            ),
            new Spec(
                "0x004e6ac0",
                "CSquadNormal__ScalarDestructor",
                "CSquadNormal__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave508 signature/name hardening: CSquadNormal scalar-deleting destructor wrapper. The wrapper calls CSquadNormal__Destructor, conditionally frees this through CDXMemoryManager__Free when flags bit 0 is set, returns this, and ends with RET 0x4. Static retail evidence only; allocator ownership, runtime destruction behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "scalar-deleting-destructor")
            ),
            new Spec(
                "0x004e6ae0",
                "CSquadNormal__Destructor",
                "CSquadNormal__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal destructor body. The ECX-only body frees pointers at this+0xec and this+0xe4, removes active-reader cells at this+0xc8 and this+0xc4 from their owning sets when present, clears the member set at this+0xa4, and delegates to CComplexThing__dtor_base. Static retail evidence only; exact resource ownership, runtime destruction ordering, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "destructor", "member-set")
            ),
            new Spec(
                "0x004e6bb0",
                "CSquadNormal__Init",
                "CSquadNormal__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal init vfunc. RET 0x4 proves one explicit init argument; the body copies init position/state fields, samples static-shadow height, delegates to CSquad__VFunc_09_004e5e70, adds the squad to DAT_008550c0/DAT_008550b0 by state, schedules target refresh, prunes/reschedules members, and dispatches vtable +0x108. Static retail evidence only; exact init layout, state enum names, runtime squad AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "init", "static-shadows", "global-list")
            ),
            new Spec(
                "0x004e6f70",
                "CSquadNormal__RemoveMember",
                "CSquadNormal__RemoveMember",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("member", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal member-removal helper. RET 0x4 proves one explicit member argument; the body verifies member+0x148 points back to this, removes the matching active-reader node from this+0xa4, destructs/frees that reader node, clears the member reader through CSquadNormal__SetReaderAndUnregisterFromFactionSets, and decrements this+0xb4. Static retail evidence only; exact member/list layout, runtime squad membership behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "member-set", "remove-member")
            ),
            new Spec(
                "0x004e6ff0",
                "CSquadNormal__SyncFromLeaderUnit",
                "CSquadNormal__SyncFromLeaderUnit",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("leader_unit", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal leader-unit sync helper. RET 0x4 proves one explicit leader_unit argument; when non-null, the body reads leader vtable slots +0x44 and +0x1bc, calls CUnit__GetGridMapByType, stores grid/profile values at this+0xd0, this+0x104, and this+0x10c, and copies leader flags at +0x34 into this+0xc0. Static retail evidence only; exact leader/squad field layout, runtime formation behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "leader-sync", "formation")
            ),
            new Spec(
                "0x004e7cf0",
                "CSquadNormal__UpdateFormationAdvanceScale",
                "CSquadNormal__UpdateFormationAdvanceScale",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal formation advance-scale updater. The ECX-only body copies this+0x10c into this+0x108, periodically walks member reader nodes at this+0xa4, checks member distance and grid occupancy, scales this+0x108 by the blocked-member fraction, refreshes this+0x11c, and returns a boolean continue/changed result. Static retail evidence only; exact formation constants, grid semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "formation", "member-set", "predicate")
            ),
            new Spec(
                "0x004e7f40",
                "CSquadNormal__IsLeaderNearFormationCentroid",
                "CSquadNormal__IsLeaderNearFormationCentroid",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal formation-centroid predicate. The ECX-only body averages member positions from the this+0xa4 reader set, compares the squad position at this+0x1c/0x20 with that centroid, and returns true when the distance is below this+0x10c scaled by the constant at 0x005d857c. Static retail evidence only; exact formation threshold semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "formation", "member-set", "predicate")
            ),
            new Spec(
                "0x004e8100",
                "CSquadNormal__ScheduleTargetReaderRefresh",
                "CSquadNormal__ScheduleTargetReaderRefresh",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave508 signature/comment hardening: CSquadNormal target-reader refresh scheduler. The ECX-only body conditionally selects a best engagement target through CSquadNormal__SelectBestEngagementTarget, stores it through CGenericActiveReader__SetReader at this+0xc4, then schedules event 4000 through CEventManager__AddEvent_AtTime with a randomized delay from Random__NextLCGAbs. Static retail evidence only; exact event cadence, target-reader semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "target-selection", "event-4000", "active-reader")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave508 had missing/bad targets");
        }
    }
}
