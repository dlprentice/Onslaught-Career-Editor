//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyUnitCoreTailWave526 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.renameAllowed = renameAllowed;
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
            "unit-core-tail-wave526",
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
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (dryRun) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.wouldRename++;
                stats.skipped++;
                return;
            }
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (!needsUpdate(fn, spec)) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
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
        DataType byteType = ByteDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f84c0",
                "CUnit__VFunc01_ScalarDeletingDtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave526 Unit core-tail signature/comment hardening: RET 0x4 and body shape identify a scalar-deleting destructor-style wrapper. It calls CUnit__dtor_base, frees this through CDXMemoryManager__Free when flags bit 0 is set, and returns this. Static retail evidence only; exact vtable coverage, destructor ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                tags("unit-lifecycle", "scalar-deleting-dtor", "vfunc-slot-01"),
                true
            ),
            new Spec(
                "0x004f86d0",
                "CUnit__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave526 Unit core-tail signature/comment hardening: full instruction read-back shows RET 0x4, and the body consumes init from the stack while setting the Unit profile pointer at this+0x164. The body delegates to CActor__Init, creates weapon/spawner/child/pickup/effect reader state from profile lists, initializes destructible segments, increments observed side/type counters, queues event 0xfa3, and calls CUnit__UpdateFireControlYawAndQueueEvent. Static retail evidence only; exact CUnit/init/profile layouts, source-body identity, runtime spawn behavior, and rebuild parity remain unproven.",
                tags("unit-init", "profile-driven", "event-scheduler"),
                true
            ),
            new Spec(
                "0x004f9430",
                "CUnit__ApplyRandomDestructibleDamageBurst",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail signature/comment hardening: register-this helper calls CDestructableSegmentsController__ApplyRandomDamageBurstAndUpdateThreshold when this+0x178 exists; otherwise it scales health-like field this+0xf8 by an LCG-derived random divisor. Static retail evidence only; exact health semantics, random distribution, runtime damage behavior, and rebuild parity remain unproven.",
                tags("unit-damage", "destructible-segment", "randomized"),
                true
            ),
            new Spec(
                "0x004f9490",
                "CUnit__SpawnConfiguredPickupIfAboveWater",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: register-this helper builds a local CInitThing-style record, resolves position from the unit mesh/object when available, copies side/team field this+0x138, and calls CWorldPhysicsManager__CreatePickup from profile field +0xec when height is above DAT_006fbdfc. Static retail evidence only; exact virtual slot meaning, pickup init layout, runtime pickup behavior, and rebuild parity remain unproven.",
                tags("unit-pickup", "profile-driven", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f95d0",
                "CUnit__VFunc02_CleanupWorldLinksAndForward",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: register-this slot-2 cleanup kills sound samples, clears active readers and linked sets at +0x17c/+0x18c/+0x19c, releases particle/effect links at +0x1ac/+0x1b4/+0x1c4/+0x1d4, removes this from observed global unit sets, frees the destructible-segment controller at +0x178, releases controller +0x208, updates observed side/type counters, and forwards to CComplexThing__Shutdown. Static retail evidence only; exact vtable coverage, ownership of each set, runtime cleanup order, and rebuild parity remain unproven.",
                tags("unit-lifecycle", "vfunc-slot-02", "active-reader", "particle-effect"),
                true
            ),
            new Spec(
                "0x004f9820",
                "CUnit__HandleEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: RET 0x4 proves one explicit event argument after ECX; the prior second parameter was stale register carryover. The body handles event ids 0xfa1, 0xfa3, 0xfa4, and 0xfa5, forwarding default cases to CActor__HandleEvent; the handled paths refresh fire-control scheduling, nearby-unit scan state, deployment graph reset, and countdown field +0x218. Static retail evidence only; exact event structure, state-field names, runtime event behavior, and rebuild parity remain unproven.",
                tags("unit-event", "vfunc-slot-00", "event-scheduler"),
                true
            ),
            new Spec(
                "0x004f99b0",
                "CUnit__PlayRespawnVoiceCueIfAvailable",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: register-this helper checks profile pointer this+0x164 and effect pointer profile+0x34, then plays that effect through CSoundManager__PlayEffect with this as owner. Static retail evidence only; exact cue meaning, profile field name, runtime audio behavior, and rebuild parity remain unproven.",
                tags("unit-audio", "profile-driven", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f99f0",
                "CUnit__GetCurrentHealthOrSubtreeHealth",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: register-this query returns CDestructableSegmentsController__GetCurrentSubtreeHealthIfAnyActive from this+0x178 when present, otherwise returns health-like field this+0xf8. Static retail evidence only; exact health contract, HUD/compass caller semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("unit-health", "destructible-segment", "owner-corrected", "query"),
                true
            ),
            new Spec(
                "0x004f9a40",
                "CUnit__GetRootSubtreeHealthIfAnyActive",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: register-this query returns CDestructableSegmentsController__GetRootSubtreeHealthIfAnyActive from this+0x178 when present, otherwise returns health-like field this+0xf8. Static retail evidence only; exact root-subtree health contract, HUD caller semantics, runtime UI behavior, and rebuild parity remain unproven.",
                tags("unit-health", "destructible-segment", "owner-corrected", "query"),
                true
            ),
            new Spec(
                "0x004f9a60",
                "CUnit__RemoveLinkedObjectFromSpawnerSet",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("linked_object", voidPtr)},
                "Wave526 Unit core-tail owner/signature hardening: RET 0x4 proves one explicit linked_object argument after ECX; the prior second parameter was stale register carryover. When linked_object is non-null, the body removes it from this+0x18c and calls its vfunc +0x4 with delete flag 1. Static retail evidence only; exact linked-object type, ownership semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("unit-spawner-set", "destructible-segment", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004fa800",
                "CUnit__UpdateClosingAndUnshuttingState",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail signature/comment hardening: register-this helper switches on state field this+0x168, compares deadline/timer this+0x16c against DAT_00672fd0, toggles flag-like field this+0x1e8, dispatches vfunc +0x15c or +0x100, and for state 3 copies a 0x30-byte transform block from this+0x9c to this+0x3c. Static retail evidence only; exact state names, transform layout, runtime closing/unshutting behavior, and rebuild parity remain unproven.",
                tags("unit-state", "motion-update", "transform"),
                true
            ),
            new Spec(
                "0x004fa8d0",
                "CUnit__UpdateMotionAttachmentsAndEffects",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave526 Unit core-tail signature/comment hardening: register-this motion/effects update calls CUnit__UpdateClosingAndUnshuttingState and CActor__Move, updates transform history and linked particle/effect attachments, manages spawner/deploy state, clamps yaw/aim fields from profile motion limits, plays or kills support-loop audio, and ends by updating thing position. Static retail evidence only; exact field names, particle ownership, runtime motion/effect behavior, and rebuild parity remain unproven.",
                tags("unit-motion", "particle-effect", "audio-loop", "deploy-animation"),
                true
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
            throw new IllegalStateException("Wave526 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
