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

public class ApplyUnitWarspiteCommandWave528 extends GhidraScript {
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
            "unit-warspite-command-wave528",
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

        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004fe030",
                "CUnit__TriggerEffect",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("trigger_context", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x4 proves one explicit trigger_context argument after ECX. The body gates through CBattleEngine__IsWeaponModeCompatibleWithMountState using trigger_context+0x138, checks this+0x164 -> +0x120 and cooldown field +0x240, selects Tara/Billy/default text IDs, allocates CMessage, and queues it through the global message box when present. Static retail evidence only; exact trigger semantics, message text mapping, runtime UI behavior, concrete Unit/profile layouts, and rebuild parity remain unproven.",
                tags("unit-trigger", "message-queue", "pilot-text"),
                false
            ),
            new Spec(
                "0x004fe390",
                "CEngine__EnableThingByNameFlag",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("thing_name", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x4 proves one explicit thing_name argument after ECX; the prior second parameter was stale register carryover. The IScript helper at 0x00535010 passes a script-provided name, and the body walks this+0x18c, compares against each entry profile/name pointer at +0x3d0 -> +0x8, then sets entry field +0x3f4 to 1. Static retail evidence only; exact CEngine/member-list layout, flag meaning, script command semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("engine-list", "script-command", "thing-name-flag"),
                false
            ),
            new Spec(
                "0x004fe3f0",
                "CEngine__DisableThingByNameFlag",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("thing_name", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x4 proves one explicit thing_name argument after ECX; the prior second parameter was stale register carryover. The IScript helper at 0x00535040 passes a script-provided name, and the body walks this+0x18c, clears matched entry field +0x3f4, clears active reader +0x144 when it points at the matched entry, and refreshes support selection through this+0x13c when present. Static retail evidence only; exact CEngine/member-list layout, flag meaning, script command semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("active-reader", "engine-list", "script-command", "thing-name-flag"),
                false
            ),
            new Spec(
                "0x004fe480",
                "CEngine__DispatchBoundCallbackIfPresent",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: ECX-only helper checks this+0x208 and dispatches callback/controller vfunc +0x24 when present, otherwise returns 0. The current CEngine owner label is retained from surrounding tail context, but the concrete callback type remains unresolved. Static retail evidence only; exact owner identity, callback contract, runtime behavior, and rebuild parity remain unproven.",
                tags("callback-dispatch", "vtable-forwarder"),
                false
            ),
            new Spec(
                "0x004fe500",
                "CSquadNormal__SetReaderAndUnregisterFromFactionSets",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("reader", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x4 proves one explicit reader argument after ECX; the prior second parameter was stale register carryover. The body sets active reader field this+0x148, then removes this from global faction sets DAT_008550c0 and DAT_008550b0 when reader is non-null. Static retail evidence only; exact CSquadNormal reader layout, faction-set semantics, runtime support behavior, and rebuild parity remain unproven.",
                tags("active-reader", "faction-set", "squad-support"),
                false
            ),
            new Spec(
                "0x004fe540",
                "CUnitAI__AccumulateForwardedCommandScore",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("score_delta", intType)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x4 proves one explicit score_delta argument after ECX; the prior float-looking second parameter was stale register carryover. The caller CUnitAI__ForwardCommandToAttachedNodeThenDispatch provides the score-like value, and the body schedules event 0xfa5 when the accumulator is empty, adds ROUND(score_delta * global scale) to this+0x218 with a 100 cap, then writes timer/cooldown field +0x21c to 10. Static retail evidence only; exact score units, event semantics, runtime command behavior, and rebuild parity remain unproven.",
                tags("command-forwarding", "event-scheduled", "unitai-score"),
                false
            ),
            new Spec(
                "0x004fe710",
                "CWarspite__Init",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("owner_unit", voidPtr), param("init_context", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x8 proves owner_unit and init_context stack arguments after ECX, and the helper returns this. Callers allocate 0x60/0x64-byte Warspite-style controller objects, pass the owning unit plus init context, then install concrete vtables. The body initializes active readers at +0x24/+0x28 from init_context fields +0xa4/+0x3b4, schedules fighting/waypoint/target events 0x7d3/0xbb9/0xbba, and randomizes oscillation fields when profile +0x19c exists. Static retail evidence only; exact Warspite layout, state enum names, runtime AI behavior, and rebuild parity remain unproven.",
                tags("warspite-ai", "init", "event-scheduled", "active-reader"),
                false
            ),
            new Spec(
                "0x004fef40",
                "CWarspite__Update",
                "__fastcall",
                floatType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: ECX-only vtable update returns a float-like delay/angle value through the x87 path. The body advances base state, checks owner unit vfunc +0x150, handles target/reader state, updates aim through CUnit__ForwardAimTransformAndAttachTargetReader, refreshes support selection through CSquadNormal__SelectBestSupportOrEscort, may call CWarspite__TransitionToUndeploying, and returns randomized timing/oscillation values from profile flags. Static retail evidence only; exact return contract, Warspite state layout, runtime AI behavior, and rebuild parity remain unproven.",
                tags("warspite-ai", "update", "support-selection", "x87-return"),
                false
            ),
            new Spec(
                "0x004ffdd0",
                "CSquadNormal__SetReaderAndRefreshSupportSelection",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("reader", voidPtr), param("selection_context", voidPtr)},
                "Wave528 Unit/Warspite command-tail signature/comment hardening: RET 0x8 proves two explicit stack arguments after ECX; the prior third argument was stale register carryover. The body sets active reader field this+0xc, refreshes support selection for owner pointer this+0x8 and reader, then stores selection_context into this+0x10. Xrefs include CUnit__PropagateTargetUnitToHierarchy, CEngine__DisableThingByNameFlag, ComponentTargeting, and CSquadNormal formation paths. Static retail evidence only; exact CSquadNormal layout, selection_context meaning, runtime support behavior, and rebuild parity remain unproven.",
                tags("active-reader", "squad-support", "support-selection"),
                false
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
            throw new IllegalStateException("Wave528 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
