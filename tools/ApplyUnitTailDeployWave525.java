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

public class ApplyUnitTailDeployWave525 extends GhidraScript {
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
            "unit-tail-deploy-wave525",
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }
        if (!needsUpdate(fn, spec)) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRYUPDATE: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.updateFunction(spec.callingConvention, null, FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
            SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("UPDATED: " + spec.address + " " + spec.name + " :: " + fn.getSignature());
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        DataType voidType = VoidDataType.dataType;
        DataType ptr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x004fcdc0", "CUnit__SetCollisionAndDamageFlags", "__thiscall", voidType, new ParameterImpl[] {
                param("this", ptr),
                param("base_flags", intType)
            }, "Wave525 signature/comment hardening: RET 0x4 proves one explicit base_flags argument after ECX. If this+0x164 and its +0x104 link are present, the body writes base_flags | 0x80200013 to this+0x34; otherwise it writes base_flags | 0x80000013. Exact flag-bit meanings, concrete layout, runtime collision/damage behavior, and rebuild parity remain unproven.",
                tags("unit-flags", "damage-collision")),
            new Spec("0x004fcf00", "CUnit__ResetKinematicsAndNotifyController", "__fastcall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this helper zeroes the four-word blocks at +0x14c and +0x7c, copies +0x114 to +0x120, and calls the attached controller/node vfunc +0x20 when this+0x208 exists. Exact kinematic field names, controller type, runtime notification semantics, and rebuild parity remain unproven.",
                tags("unit-kinematics", "controller-forwarder")),
            new Spec("0x004fcfa0", "CUnit__ClearSpawnerSet", "__fastcall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this helper clears the active reader at +0x144, drains the linked set at +0x18c, removes each value from the set, and invokes each value vfunc +0x8. Exact set ownership, value type, runtime cleanup ordering, and rebuild parity remain unproven.",
                tags("unit-spawner-set", "active-reader")),
            new Spec("0x004fcfe0", "CUnit__ReleaseChildUnits", "__fastcall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this helper drains child reader nodes at +0x19c. For each referenced child it dispatches child vfunc +0x8 or +0xc8 depending on this+0x2c destroyed flag bit 2, removes the node from the set, destructs the active reader, and frees the node. Exact child ownership, vfunc identities, runtime lifecycle behavior, and rebuild parity remain unproven.",
                tags("unit-child-units", "active-reader", "lifecycle")),
            new Spec("0x004fd040", "CUnit__ResetDeploymentGraphAndScheduleEvent", "__fastcall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this cleanup/reset helper releases child readers at +0x19c, clears +0x144, drains +0x18c, reinitializes the deployment-related object state through CExplosionInitThing__ctor_like_004fd230, calls script event id 3/reset on +0x74, and schedules event 2000 at current time plus DAT_00672fd0. Exact event meaning, script ownership, layout, runtime deployment behavior, and rebuild parity remain unproven.",
                tags("unit-deploy", "event-scheduler", "active-reader")),
            new Spec("0x004fd140", "CUnit__MarkDestroyedAndCleanupLinks", "__fastcall", intType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this helper returns 0 when this+0x2c destroyed flag bit 2 is already set; otherwise it kills sounds for this, marks that flag, adjusts global type/side counters through this+0x164 and +0x138, triggers destructible-segment cascade at +0x178, calls script event id 5 on +0x74, clears +0x144, drains +0x18c, and returns 1. Exact counter semantics, script meaning, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("unit-destruction", "active-reader", "counter-update")),
            new Spec("0x004fd380", "CUnit__GetGridMapByType", "__fastcall", ptr, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this query reads this+0x164 and switches on profile/type field +0xfc; values 1, 2, and 3/4 return the global grid/map pointers DAT_00855290, DAT_00855294, and DAT_00855298 respectively, otherwise null. Exact map ownership, enum names, runtime collision/grid behavior, and rebuild parity remain unproven.",
                tags("unit-grid-map", "query")),
            new Spec("0x004fd5b0", "CUnit__IsActiveAndNotInState12", "__stdcall", boolType, new ParameterImpl[] {
                param("unit", ptr)
            }, "Wave525 signature/comment hardening: RET 0x4 proves one explicit unit pointer. The predicate returns true only when unit is non-null, destroyed flag bit 2 at +0x2c is clear, and state field +0x244 is neither 1 nor 2. Exact state enum names, runtime activity semantics, and rebuild parity remain unproven.",
                tags("unit-state", "predicate")),
            new Spec("0x004fd7a0", "CUnit__HasAnyReadySpawner", "__fastcall", boolType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this predicate walks linked entries at +0x18c and returns true when any entry satisfies CUnit__IsInBlockedSupportState; it returns false when the list is empty or no entry matches. The saved name predates this stricter read-back, so exact ready/blocked semantics, list ownership, runtime deploy behavior, and rebuild parity remain unproven.",
                tags("unit-spawner-set", "predicate")),
            new Spec("0x004fd7e0", "CUnitAI__AreSpawnedChildrenReady", "__fastcall", boolType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this predicate walks linked entries at +0x18c and returns true only if the list is empty or every entry is CSpawnerThng__IsSpawnComplete and does not satisfy CUnit__IsInBlockedSupportState; any incomplete or blocked entry returns false. Exact child/spawner ownership, state names, runtime spawn behavior, and rebuild parity remain unproven.",
                tags("unit-ai", "spawn-helper", "predicate")),
            new Spec("0x004fde10", "CUnitAI__IsDeployAnimationState", "__fastcall", boolType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this predicate returns true when state field +0x244 is 3, 4, or 5 and false otherwise. Exact deploy animation state enum names, runtime animation behavior, and rebuild parity remain unproven.",
                tags("unit-ai", "deploy-animation", "predicate")),
            new Spec("0x004fde30", "CUnit__BeginDeployAnimationIfIdle", "__fastcall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this helper only acts when state field +0x244 is 0; it sets that field to 3, resolves the deploying animation through the mesh/profile vfunc +0x24, finds the animation index, and dispatches vfunc +0xf0. Exact state enum names, mesh/profile layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("unit-deploy", "deploy-animation")),
            new Spec("0x004fdeb0", "CUnitAI__HandleDeployAndFireAnimationCompletion", "__fastcall", intType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave525 signature/comment hardening: register-this animation completion helper compares the current animation index against deploying, undeploying, prefire, firing, and postfire tokens. It transitions deploying to deployed state 4, undeploying to normal state 0, prefire to prefirehold, firing/postfire to deployed or normal depending on +0x244, and otherwise falls back to CComplexThing__FinishedPlayingCurrentAnimation. It returns 1 for the no-current-animation path or fallback completion result and 0 when it handled a transition. Exact state enum names, runtime animation behavior, and rebuild parity remain unproven.",
                tags("unit-ai", "deploy-animation", "fire-animation"))
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave525 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
