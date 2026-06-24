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

public class ApplyInfantryAIVtableBoundaryWave1082 extends GhidraScript {
    private static final String WAVE_TAG = "infantryai-vtable-boundary-review-wave1082";

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String[] excludedBodyAddresses;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String[] excludedBodyAddresses, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.excludedBodyAddresses = excludedBodyAddresses;
            this.comment = comment;
            this.tags = tags;
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
        if (getInstructionAt(address) == null) {
            throw new IllegalStateException("No instruction at " + spec.address);
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
        for (String excluded : spec.excludedBodyAddresses) {
            if (fn.getBody().contains(addr(excluded))) {
                throw new IllegalStateException("Read-back body for " + spec.address
                    + " unexpectedly absorbed " + excluded);
            }
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1082-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "vtable-slot",
            "ai-vtable"
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
        println("ApplyInfantryAIVtableBoundaryWave1082 mode=" + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004ff330",
                "SharedUnitAI__HandleEventAndMaybeFire_004ff330",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("event_code", intType) },
                new String[] { "0x004ff4f0" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 0 and many CUnitAI-derived vtables point at this previously functionless RET 0x4 body. The body gates owner state, dispatches through owner/unit vtable slots, uses the one stack argument as an event/control code, and stops before adjacent 0x004ff4f0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete CUnitAI/CInfantryAI layout, runtime AI/fire behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "event-gate", "ret4")
            ),
            new Spec(
                "0x004ff4f0",
                "SharedUnitAI__UpdateTargetAndAnimationState_004ff4f0",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004ff710" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 4 and many CUnitAI-derived vtables point at this previously functionless body. The body updates linked target/reader state, tests owner support fields, issues animation/state calls, and stops before adjacent 0x004ff710. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete AI layout, runtime target/animation behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "target-state", "animation-state")
            ),
            new Spec(
                "0x004fea30",
                "SharedUnitAI__CheckField24TargetState_004fea30",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004feac0" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 5 and many CUnitAI-derived vtables point at this previously functionless boolean body. The body reads this+0x24 and this+0x20, formats/logs fallback strings when the field is missing, returns a boolean result, and stops before adjacent 0x004feac0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "target-state", "boolean")
            ),
            new Spec(
                "0x004febe0",
                "SharedUnitAI__CheckField20TargetMode1_004febe0",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fec60" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 6 and many CUnitAI-derived vtables point at this previously functionless boolean body. The body reads this+0x20, accepts only mode 1, formats/logs fallback strings otherwise, returns a boolean result, and ends before later adjacent code. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete mode semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "target-mode", "boolean")
            ),
            new Spec(
                "0x004ffb60",
                "SharedUnitAI__TryStartField28TimedEvent_004ffb60",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004ffbb0" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 7 and many CUnitAI-derived vtables point at this previously functionless boolean body. The body checks this+0x28 and a target flag, stores mode 2, writes a DAT_00672fd0-based timestamp to this+0x44, schedules event id 0xbba, returns 1 on activation, and returns 0 otherwise. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field/event semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "event-schedule", "boolean")
            ),
            new Spec(
                "0x004feac0",
                "SharedUnitAI__CheckField24RangeAgainstCandidate_004feac0",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("candidate", voidPtr) },
                new String[] { "0x004febe0" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 8 and several CUnitAI-derived vtables point at this previously functionless RET 0x4 body. The body checks the this+0x24 target/reader field, computes distance-like deltas against owner/vector fields, and returns a boolean-style result for the stack candidate. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete vector/candidate semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "range-check", "ret4")
            ),
            new Spec(
                "0x0048a030",
                "CInfantryAI__UpdateSupportSelection_0048a030",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0048a3c0" },
                "Wave1082 CInfantryAI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 9 is the observed DATA xref to this previously functionless body. The body gates owner/unit state, reads several AI target/reader fields, calls collision/reader helpers, and stops before CInfantryGuide__ctor at 0x0048a3c0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete CInfantryAI layout, runtime infantry AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("cinfantryai", "support-selection", "target-reader")
            ),
            new Spec(
                "0x004ffbb0",
                "SharedUnitAI__UpdateField28TargetReaderGate_004ffbb0",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("candidate", voidPtr) },
                new String[] { "0x004ffdd0" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 10 and many CUnitAI-derived vtables point at this previously functionless RET 0x4 body. The body checks this+0x28 and owner/unit virtual gates, may call through target virtual slots, and stops before existing CSquadNormal__SetReaderAndRefreshSupportSelection at 0x004ffdd0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete reader/candidate semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "target-reader", "ret4")
            ),
            new Spec(
                "0x004ff710",
                "SharedUnitAI__CheckField0cCloseTargetGate_004ff710",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004ffbb0" },
                "Wave1082 AI vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 11 and several CUnitAI-derived vtables point at this previously functionless boolean body. The body tests this+0x0c target/reader state, uses virtual distance/threshold gates, may refresh attached target context, and stops before adjacent 0x004ffbb0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete close-target semantics, runtime AI behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-unitai", "cinfantryai", "close-target", "boolean")
            ),
            new Spec(
                "0x00402d20",
                "SharedVFunc__ReturnThis_00402d20",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00402d30" },
                "Wave1082 shared vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 17 and several broader DATA refs point at this previously functionless two-instruction body. The body returns ECX/this and stops before existing CAirUnit destructor code at 0x00402d30. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete object semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "cinfantryai", "return-this")
            ),
            new Spec(
                "0x004f45c0",
                "SharedVFunc__ForwardField64FloatOrZero_004f45c0",
                "__thiscall",
                floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f45e0" },
                "Wave1082 shared vtable-boundary recovery: CInfantryAI vtable 0x005dbf14 slot 55 and many CThing/AI-family DATA refs point at this previously functionless float-return body. The body loads this+0x64, returns global zero/default float when null, or tail-jumps to 0x004048c0 when non-null; it stops before existing CComplexThing__SetVar at 0x004f45e0. Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete field semantics, runtime behavior, BEA patching, and rebuild parity remain separate proof.",
                tags("shared-vfunc", "cinfantryai", "float-forwarder")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " "
                    + ex.getClass().getSimpleName() + ": " + ex.getMessage());
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
            + " bad=" + stats.bad
        );
        if (stats.bad != 0) {
            throw new IllegalStateException("Wave1082 InfantryAI vtable-boundary recovery encountered bad rows");
        }
    }
}
