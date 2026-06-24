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

public class ApplySquadNormalTailWave509 extends GhidraScript {
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
            "squadnormal-tail-wave509",
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e5e70",
                "CSquad__VFunc_09_004e5e70",
                "CSquad__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave509 signature/comment hardening: CSquad base init vfunc at vtable 0x005def1c slot 9. The body uses one explicit init argument, copies init position/state fields into this+0x1c..0x28/0x7c/0x9c, resolves a type/name through DAT_008553fc from init+0x3c0, builds CInitThing locals, spawns initial members through CWorldPhysicsManager__CreateThingByType and squad vfunc +0x10c, then calls CComplexThing__Init and adds this to DAT_008550a0. Static retail evidence only; exact init layout, global-list semantics, spawned-member behavior, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad", "init", "vfunc-slot-9", "spawn")
            ),
            new Spec(
                "0x004e6610",
                "CExplosionInitThing__HasSpawnDelayElapsedAndNotTriggered",
                "SharedState__IsTimer88PendingAndState7CZero",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 stale-owner correction: ECX-only timer/state predicate. The body returns true when DAT_00672fd0 is still below this+0x88 and this+0x7c is zero; the previous CExplosionInitThing owner is not supported by the adjacent CUnit timer helper or the xref read-back. Static retail evidence only; exact owner, field layout, timer meaning, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("shared-state", "stale-owner-corrected", "timer-predicate", "predicate")
            ),
            new Spec(
                "0x004e66d0",
                "CWaypoint__Process_NoOp",
                "SharedVFunc__ForwardProcessNoOp",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("process_arg", voidPtr)},
                "Wave509 stale-owner correction: owner-neutral thiscall process/no-op forwarder. RET 0x4 proves one explicit process_arg while ECX is preserved into the delegated call at 0x00452b60; vtable/data and raw-call read-back do not support the old CWaypoint-specific owner. Static retail evidence only; exact owning class, process contract, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("shared-vfunc", "stale-owner-corrected", "process", "forwarder")
            ),
            new Spec(
                "0x004e7110",
                "CSquadNormal__Process",
                "CSquadNormal__Process",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("process_arg", voidPtr)},
                "Wave509 signature/comment hardening: CSquadNormal process/update body. The function syncs from the leader, evaluates pursuit/target mode, refreshes path/reader state, switches column versus attack formation, samples static-shadow height, forwards process_arg to the shared process/no-op path, runs spawn/split and nearby-squad merge helpers, then averages live member positions into this+0x124..0x12c and returns a process status. Static retail evidence only; exact squad layout, state enum names, path/AI behavior, runtime behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "process", "formation", "member-set")
            ),
            new Spec(
                "0x004e81d0",
                "CSquadNormal__EvaluateLeaderTargetPursuitMode",
                "CSquadNormal__EvaluateLeaderTargetPursuitMode",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 signature/comment hardening: CSquadNormal leader-target pursuit-mode evaluator. The ECX-only body reads the leader/target reader, checks target flags and support/escort candidates, compares support min/max distances, and tests CUnit__CanFireAtTarget_BallisticArcB before returning a small mode value. Static retail evidence only; exact mode enum, target-reader layout, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "target-selection", "pursuit-mode")
            ),
            new Spec(
                "0x004e83b0",
                "CSquadNormal__PruneDeadMembersAndReschedule",
                "CSquadNormal__PruneDeadMembersAndReschedule",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("schedule_event", intType)},
                "Wave509 signature/comment hardening: CSquadNormal member-prune and optional reschedule helper. RET 0x4 proves one explicit schedule_event argument; the body removes null/dead reader nodes from this+0xa4, frees reader storage, decrements this+0xb4, clears formation state at this+0xbc when needed, resolves formation-slot conflicts, and optionally schedules event 0xfa1 using DAT_00672fd0 plus a randomized delay. Static retail evidence only; exact member/list/event layout, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "member-set", "formation", "event-0xfa1")
            ),
            new Spec(
                "0x004e84e0",
                "CSquadNormal__ResolveFormationSlotConflicts",
                "CSquadNormal__ResolveFormationSlotConflicts",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 signature/comment hardening: CSquadNormal formation-slot conflict resolver. The ECX-only body walks reader nodes at this+0xa4, compares transformed slot errors against current unit positions, calls CGenericActiveReader__SwapWithCandidateIfFormationCloser when a candidate may improve total error, and returns true when no swap was needed. Static retail evidence only; exact reader-node layout, formation metric semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "formation", "member-set", "predicate")
            ),
            new Spec(
                "0x004e8730",
                "CSquadNormal__BuildColumnFormation",
                "CSquadNormal__BuildColumnFormation",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 signature/comment hardening: CSquadNormal column-formation builder. The ECX-only body prunes members without rescheduling, derives column offsets from member count and formation spacing, marks this+0xbc as column mode, repeatedly resolves slot conflicts until stable, transforms offsets, and dispatches each member to vfunc +0xf4. Static retail evidence only; exact spacing constants, member command contract, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "formation", "column-formation", "member-set")
            ),
            new Spec(
                "0x004e8930",
                "CSquadNormal__BuildAttackFormation",
                "CSquadNormal__BuildAttackFormation",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 signature/comment hardening: CSquadNormal attack-formation builder. The ECX-only body prunes members, computes attack offsets when this+0xbc is not already attack mode, repeatedly resolves slot conflicts until stable, refreshes per-member target/support readers, and dispatches each member to vfunc +0xf4 with the transformed attack slot. Static retail evidence only; exact attack-slot layout, target/support reader semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "formation", "attack-formation", "member-set")
            ),
            new Spec(
                "0x004e8dd0",
                "CSquadNormal__ShouldSwitchToAttackFormation",
                "CSquadNormal__ShouldSwitchToAttackFormation",
                "__fastcall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 signature/comment hardening: CSquadNormal attack-formation predicate. The ECX-only body queries the leader/target through vtable +0x128 and +0x3c, returning true when the measured target distance is positive and this+0x9c is zero. Static retail evidence only; exact distance semantics, state enum names, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "formation", "predicate", "attack-formation")
            ),
            new Spec(
                "0x004e8ed0",
                "CSquadNormal__CreateIterator",
                "CSquadNormal__CreateIterator",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 undefined-signature correction: CSquadNormal member iterator/set snapshot creator. The ECX-only body allocates a 0x10-byte CSPtrSet, initializes it, walks this+0xa4 through the scratch cursor at this+0xac, adds each member to the new set, and returns that set pointer. Static retail evidence only; exact iterator ownership/lifetime, reader-node layout, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "member-set", "iterator", "undefined-signature-corrected")
            ),
            new Spec(
                "0x004e8f80",
                "CSquadNormal__TryMergeWithNearbySquad",
                "CSquadNormal__TryMergeWithNearbySquad",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("force_merge", intType)},
                "Wave509 signature/comment hardening: CSquadNormal nearby-squad merge helper. RET 0x4 proves one explicit force_merge argument; the body gates on no current target, positive formation range, squad state/profile compatibility, member readiness, distance to another squad in DAT_008550a0, capacity unless forced, then removes members from this and transfers them through the target squad vfunc +0x10c. Static retail evidence only; exact global-list/member layout, force flag semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "merge", "member-set", "global-list")
            ),
            new Spec(
                "0x004e91f0",
                "CSquadNormal__SpawnMembers",
                "CSquadNormal__SpawnMembers",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave509 undefined-signature correction: CSquadNormal spawn/split helper. The ECX-only body splits grounded members out of multi-member squads by allocating a new CSquadNormal, building a CInitThing from the member and squad profile data, initializing the new squad, removing the member from this, and adding it to the new squad; singleton squads instead realign their position to the leader and static-shadow height. Static retail evidence only; exact split threshold, init/profile layout, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "spawn", "member-set", "undefined-signature-corrected")
            ),
            new Spec(
                "0x004e9570",
                "CSquadNormal__SetFactionAndRefreshGlobalLists",
                "CSquadNormal__SetFactionAndRefreshGlobalLists",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("faction_state", intType)},
                "Wave509 signature/comment hardening: CSquadNormal faction/state setter and global-list refresher. The body stores faction_state at this+0x7c, propagates it to live member units through CUnit__SetFactionForHierarchy, removes this from DAT_008550c0/DAT_008550b0, then re-adds it to those faction-specific sets for state values 0, 1, and 6. Static retail evidence only; exact faction enum, global-list semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("squad-normal", "faction", "global-list", "member-set")
            ),
            new Spec(
                "0x004e97e0",
                "CSquadNormal__SwapReadersIfPairCloser",
                "CGenericActiveReader__SwapWithCandidateIfFormationCloser",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("candidate_reader", voidPtr)},
                "Wave509 stale-owner correction: active-reader slot-swap helper used by CSquadNormal formation conflict resolution. RET 0x4 proves one explicit candidate_reader argument; the body compares current and cross-assigned formation errors for two reader nodes and swaps their readers through CGenericActiveReader__SetReader when the candidate pairing is closer. Static retail evidence only; exact reader-node layout, formation metric semantics, runtime AI behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("active-reader", "formation", "stale-owner-corrected", "predicate")
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
            throw new IllegalStateException("Wave509 had missing/bad targets");
        }
    }
}
