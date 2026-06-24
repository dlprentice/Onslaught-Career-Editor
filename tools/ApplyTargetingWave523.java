//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyTargetingWave523 extends GhidraScript {
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
            "targeting-wave523",
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004fb280",
                "CUnit__UpdateFireControlYawAndQueueEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("event_context", voidPtr)},
                "Wave523 Unit/Squad targeting signature/comment hardening: RET 0x4 proves one explicit event_context stack argument after ECX. CUnit__Init passes 0 and VFuncSlot_00_004f9820 passes its event record. The body refreshes the unit fire-control pitch/yaw field at this+0xec from weapon/target state, clamps it between observed -pi/+pi constants, then schedules event 0xfa1 through CEventManager__AddEvent_AtTime with a randomized delay and event_context. Static retail evidence only; exact event structure, field names, runtime targeting behavior, source identity, and rebuild parity remain unproven.",
                tags("unit-targeting", "event-scheduler", "ballistic-targeting"),
                true
            ),
            new Spec(
                "0x004fb3d0",
                "CSquadNormal__IsValidLinkedSupportForTarget",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("target_unit", voidPtr)},
                "Wave523 Unit/Squad targeting signature/comment hardening: RET 0x4 proves one explicit target_unit stack argument after ECX; the prior second decompiler parameter was register carryover. The body requires a non-null target with vfunc +0x1b0 success, scans support candidates at this+0x18c through CUnit__IsSupportTargetMaskCompatible, then scans this+0x17c for active mask matches and checks terrain-relative height against profile offsets +0x6c/+0x70. Static retail evidence only; exact squad/support list layouts, target type, runtime AI behavior, source identity, and rebuild parity remain unproven.",
                tags("squadnormal", "unit-targeting", "support-targeting"),
                true
            ),
            new Spec(
                "0x004fb500",
                "CUnit__CanFireAtTarget_BallisticArcA",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("target_unit", voidPtr),
                    param("ballistic_context", intType)
                },
                "Wave523 Unit/Squad targeting signature/comment hardening: RET 0x8 proves two explicit stack arguments after ECX. The body first calls CUnit__ClassifyTargetRangeBand(this,target_unit), samples static-shadow/terrain height for target_unit+0x1c, compares the target's relative height against the active ballistic profile window at this+0x140->+0xa0 offsets +0x6c/+0x70, then forwards target_unit and ballistic_context to OID__CanFireAtTarget_BallisticArcA. If no ballistic owner is present it falls back to whether this+0x144 is non-null. Static retail evidence only; exact boolean contract, context meaning, runtime weapon behavior, source identity, and rebuild parity remain unproven.",
                tags("unit-targeting", "ballistic-targeting", "range-gate"),
                true
            ),
            new Spec(
                "0x004fb5a0",
                "CUnit__CanFireAtTarget_BallisticArcB",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("target_unit", voidPtr)},
                "Wave523 Unit/Squad targeting signature/comment hardening: RET 0x4 proves one explicit target_unit stack argument after ECX. The body gates through CUnit__ClassifyTargetRangeBand(this,target_unit), handles an alternate target vfunc +0x10c height path before the static-shadow sample, compares height against the active ballistic profile window at this+0x140->+0xa0 offsets +0x6c/+0x70, then forwards target_unit to OID__CanFireAtTarget_BallisticArcB. If no ballistic owner is present it falls back to whether this+0x144 is non-null. Static retail evidence only; exact boolean contract, runtime weapon behavior, source identity, and rebuild parity remain unproven.",
                tags("unit-targeting", "ballistic-targeting", "range-gate"),
                true
            ),
            new Spec(
                "0x004fb650",
                "CUnit__ForwardAimTransformAndAttachTargetReader",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("target_transform", voidPtr),
                    param("target_reader", voidPtr)
                },
                "Wave523 Unit/Squad targeting owner/signature hardening: renamed from the Warspite-specific label because the body is a generic CUnit-style forwarder over this+0x140 and xrefs include CGillMHeadAI__UpdateAimTransformAndTargetReader plus CWarspite__Update and other unit-family callsites. RET 0x8 proves two explicit stack arguments after ECX. When this+0x140 is non-null, the body forwards target_transform and target_reader to OID__UpdateAimTransformAndAttachTargetReader. Static retail evidence only; exact source virtual name, concrete target-reader type, runtime aim behavior, and rebuild parity remain unproven.",
                tags("unit-targeting", "aim-transform", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004fb670",
                "CUnit__ClassifyTargetRangeBand",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("target_unit", voidPtr)},
                "Wave523 Unit/Squad targeting signature/comment hardening: RET 0x4 proves one explicit target_unit stack argument after ECX; the prior second parameter was register carryover. The body returns 2 for null/too-close/invalid target cases, returns 1 for beyond-range cases, and returns 0 when the target is inside the usable range. Ballistic-owner units compare planar/3D target distance against CUnit__ComputeMinBallisticTravelDistance and CUnit__ComputeMaxBallisticTravelDistance through this+0x140; fallback units use profile range fields this+0x144->+0x3d0 offsets +0x2c/+0x30. Static retail evidence only; exact enum names, range semantics, runtime weapon behavior, source identity, and rebuild parity remain unproven.",
                tags("unit-targeting", "ballistic-targeting", "range-gate"),
                true
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
