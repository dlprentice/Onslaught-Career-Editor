//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyUnitFamilyResidualVtableFinalReviewWave1089 extends GhidraScript {
    private static final String WAVE_TAG = "unit-family-residual-vtable-final-review-wave1089";

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

    private String[] tags(String... extra) {
        String[] base = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1089-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "function-boundary-recovered",
            "vtable-boundary",
            "unit-family-vtable"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    private String comment(String bodyEvidence) {
        return "Wave1089 static read-back: recovered unit-family residual vtable boundary from the final 10-vtable sample. "
            + bodyEvidence
            + " Static retail Ghidra vtable/xref/instruction/string evidence only; exact source virtual name, concrete owner layout, runtime behavior, BEA patching, gameplay outcomes, and rebuild parity remain unproven.";
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec("0x00489ed0", "CInfantryUnitVFunc__ReturnFlag24Float005d856cOr005d8568_00489ed0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00489ef0" },
                comment("CInfantryUnit vtable 0x005e26b4 slot 23 DATA xref 0x005e2710 points at a compact flag-gated float-return body. It tests byte this+0x24 mask 0x4 and returns float data at 0x005d856c when set, otherwise 0x005d8568."),
                tags("infantryunit-vfunc", "float-return", "flag-test")),
            new Spec("0x004bfc50", "SharedUnitVFunc__ReturnFloat005d85cc_004bfc50", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004bfc60" },
                comment("CPod vtable 0x005dff14 slot 45 DATA xref 0x005dffc8 plus repeated unit-family DATA refs point at a two-instruction body that returns float data at 0x005d85cc."),
                tags("shared-unit-vfunc", "float-return")),
            new Spec("0x004d35d0", "CPodVFunc__FlagArg70AndSeedMotion250_004d35d0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x004d3630" },
                comment("CPod vtable 0x005dff14 slot 39 DATA xref 0x005dffb0 points at a RET 0x4 body. It sets mask 0x02000010 in arg+0x70, seeds this+0x250/0x254, calls 0x004f86d0, then copies a 16-byte block from arg+4 into this+0x258."),
                tags("cpod-vfunc", "arg-flag", "motion-fields")),
            new Spec("0x004d3650", "CPodVFunc__InitializeVector7cWhenField250Clear_004d3650", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004d36c0" },
                comment("CPod vtable 0x005dff14 slot 98 DATA xref 0x005e009c points at a body that calls timestamp helper 0x00402000, checks this+0x250, dispatches vtable slot +0x148 when clear, sets this+0x250 to one, and zeroes the vector-like block at this+0x7c."),
                tags("cpod-vfunc", "vector-context", "field-init")),
            new Spec("0x004d3890", "CPodVFunc__ForwardArgWithFlag00200000_004d3890", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x004d38b0" },
                comment("CPod vtable 0x005dff14 slot 68 DATA xref 0x005e0024 points at a flag-forwarding thunk. The body ORs the stack value with mask 0x00200000, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("cpod-vfunc", "flag-forwarder")),
            new Spec("0x004d38b0", "CPodVFunc__ReturnFloat005d8580_004d38b0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004d38c0" },
                comment("CPod vtable 0x005dff14 slot 75 DATA xref 0x005e0040 points at a two-instruction body that returns float data at 0x005d8580."),
                tags("cpod-vfunc", "float-return")),
            new Spec("0x004dbc20", "SharedUnitVFunc__ReturnInt5_004dbc20", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004dbc30" },
                comment("CInfantryUnit vtable 0x005e26b4 slot 19 DATA xref 0x005e2700 plus additional unit-family DATA refs point at a two-instruction integer-return body that returns 5."),
                tags("shared-unit-vfunc", "int-return")),
            new Spec("0x004dedc0", "CSentinelVFunc__BuildDispatchArgsFromField220_004dedc0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x004dee00" },
                comment("CSentinel vtable 0x005e0868 slot 143 DATA xref 0x005e0aa4 points at a RET 0x4 body. It builds call arguments from this+0x220, this+0x30, this+8, and the caller stack argument, then calls helper 0x004b4de0."),
                tags("csentinel-vfunc", "arg-forwarder", "dispatch")),
            new Spec("0x004deec0", "CSentinelVFunc__BuildField164ContextAndDispatch_004deec0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004df0b0" },
                comment("CSentinel vtable 0x005e0868 slot 125 DATA xref 0x005e0a5c points at a large stack-context body. It gates on this+0x164, initializes a stack context through 0x0048dcf0, uses this+0x30 slot +0x20 or this+0x1c as position input, calls 0x0050ff10 on field164+0xec, walks global list head 0x008553f8, and dispatches the built context through the returned object's vtable slot +0x24."),
                tags("csentinel-vfunc", "field164-context", "dispatch")),
            new Spec("0x004dfc60", "CSimpleBuildingVFunc__ResetVectorAndDispatchSlot70_004dfc60", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004dfcb0" },
                comment("CSimpleBuilding vtable 0x005dfcc4 slot 98 DATA xref 0x005dfe4c points at a body that calls timestamp helper 0x00402000, optionally runs cleanup helpers when this+0x2c mask 0x4 is set, zeroes a stack vector, and dispatches vtable slot +0x70 with that vector."),
                tags("csimplebuilding-vfunc", "vector-context", "dispatch")),
            new Spec("0x004dfcc0", "CSimpleBuildingVFunc__ReturnFlag2cFloat005d8bbcOrZero_004dfcc0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004dfce0" },
                comment("CSimpleBuilding vtable 0x005dfcc4 slot 75 DATA xref 0x005dfdf0 points at a flag-gated float-return body. It tests this+0x2c mask 0x4 and returns float data at 0x005d8bbc when set, otherwise 0x005d856c."),
                tags("csimplebuilding-vfunc", "float-return", "flag-test")),
            new Spec("0x004eee80", "CSubmarineVFunc__UpdateMotionVectorsAndNormalize_004eee80", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004ef058" },
                comment("CSubmarine vtable 0x005e1418 slot 96 DATA xref 0x005e1598 points at a long motion/vector body. It dispatches vtable slots +0x130 and +0x120, accumulates/scales this+0x14c..0x154 into this+0x7c..0x84, normalizes the vector, calls 0x004fa8d0, and performs flag/field164 follow-up paths."),
                tags("csubmarine-vfunc", "motion-fields", "vector-context")),
            new Spec("0x004ef070", "CSubmarineVFunc__IsField250NonNull_004ef070", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004ef080" },
                comment("CSubmarine vtable 0x005e1418 slot 135 DATA xref 0x005e1634 points at a compact bool-return body that returns whether this+0x250 is non-null."),
                tags("csubmarine-vfunc", "field-test")),
            new Spec("0x004ef080", "CSubmarineVFunc__ResetField14cCopyField114To120_004ef080", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004ef0f0" },
                comment("CSubmarine vtable 0x005e1418 slot 94 DATA xref 0x005e1590 points at a body that zeroes the 16-byte block at this+0x14c, copies vector-like fields this+0x114..0x11c into this+0x120..0x128, then optionally dispatches field208 slot +0x20."),
                tags("csubmarine-vfunc", "vector-context", "field-copy")),
            new Spec("0x004f84b0", "CGroundUnitVFunc__ReturnFloat005d8604_004f84b0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f84c0" },
                comment("CGroundUnit vtable 0x005e325c slot 45 DATA xref 0x005e3310 plus another unit-family DATA ref point at a two-instruction body that returns float data at 0x005d8604."),
                tags("cgroundunit-vfunc", "float-return")),
            new Spec("0x0050e870", "CAirUnitVFunc__ForwardArgWithFlags40000400_0050e870", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050e890" },
                comment("CAirUnit vtable 0x005e3700 slot 68 DATA xref 0x005e3810 plus repeated unit-family DATA refs point at a flag-forwarding thunk. The body ORs the stack value with mask 0x40000400, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("cairunit-vfunc", "flag-forwarder")),
            new Spec("0x0050e890", "CAirUnitVFunc__ReturnFloat005d85ec_0050e890", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050e8a0" },
                comment("CAirUnit vtable 0x005e3700 slot 23 DATA xref 0x005e375c plus repeated unit-family DATA refs point at a two-instruction body that returns float data at 0x005d85ec."),
                tags("cairunit-vfunc", "float-return")),
            new Spec("0x0050e940", "CGroundUnitVFunc__ReturnFloat005d85bc_0050e940", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050e950" },
                comment("CGroundUnit vtable 0x005e325c slot 54 DATA xref 0x005e3334 plus repeated unit-family DATA refs point at a two-instruction body that returns float data at 0x005d85bc."),
                tags("cgroundunit-vfunc", "float-return")),
            new Spec("0x0050e9d0", "CInfantryUnitVFunc__GetClassNameString_0050e9d0", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050e9e0" },
                comment("CInfantryUnit vtable 0x005e26b4 slot 37 DATA xref 0x005e2748 points at a constant-string getter. The body returns 0x0063d804, and string read-back at that address is \"CInfantryUnit\"."),
                tags("cinfantryunit-vfunc", "string-return", "class-name")),
            new Spec("0x0050e9e0", "CInfantryUnitVFunc__ForwardArgWithFlags40004200_0050e9e0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050ea00" },
                comment("CInfantryUnit vtable 0x005e26b4 slot 68 DATA xref 0x005e27c4 points at a flag-forwarding thunk. The body ORs the stack value with mask 0x40004200, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("cinfantryunit-vfunc", "flag-forwarder")),
            new Spec("0x0050ea00", "CInfantryUnitVFunc__ReturnField260Float_0050ea00", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050ea10" },
                comment("CInfantryUnit vtable 0x005e26b4 slot 54 DATA xref 0x005e278c points at a two-instruction body that returns float field this+0x260."),
                tags("cinfantryunit-vfunc", "float-return", "field-return")),
            new Spec("0x0050eb50", "CSubmarineVFunc__GetClassNameString_0050eb50", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050eb60" },
                comment("CSubmarine vtable 0x005e1418 slot 37 DATA xref 0x005e14ac points at a constant-string getter. The body returns 0x0063d850, and string read-back at that address is \"CSubmarine\"."),
                tags("csubmarine-vfunc", "string-return", "class-name")),
            new Spec("0x0050eb70", "CSubmarineVFunc__ForwardArgWithFlags50108000_0050eb70", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050eb90" },
                comment("CSubmarine vtable 0x005e1418 slot 68 DATA xref 0x005e1528 points at a flag-forwarding thunk. The body ORs the stack value with mask 0x50108000, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("csubmarine-vfunc", "flag-forwarder")),
            new Spec("0x0050eb90", "CSubmarineVFunc__ReturnField164B4Float_0050eb90", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050eba0" },
                comment("CSubmarine vtable 0x005e1418 slot 45 DATA xref 0x005e14cc points at a compact field-return body that loads this+0x164 and returns float field +0xb4."),
                tags("csubmarine-vfunc", "float-return", "field-return")),
            new Spec("0x0050ec60", "CSentinelVFunc__GetClassNameString_0050ec60", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050ec70" },
                comment("CSentinel vtable 0x005e0868 slot 37 DATA xref 0x005e08fc points at a constant-string getter. The body returns 0x0063d888, and string read-back at that address is \"CSentinel\"."),
                tags("csentinel-vfunc", "string-return", "class-name")),
            new Spec("0x0050ec70", "CSentinelVFunc__ForwardArgWithFlags40140220_0050ec70", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050ec90" },
                comment("CSentinel vtable 0x005e0868 slot 68 DATA xref 0x005e0978 points at a flag-forwarding thunk. The body ORs the stack value with mask 0x40140220, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("csentinel-vfunc", "flag-forwarder")),
            new Spec("0x0050ecf0", "CPodVFunc__GetClassNameString_0050ecf0", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050ed00" },
                comment("CPod vtable 0x005dff14 slot 37 DATA xref 0x005dffa8 points at a constant-string getter. The body returns 0x0063d8b8, and string read-back at that address is \"CPod\"."),
                tags("cpod-vfunc", "string-return", "class-name")),
            new Spec("0x0050ed00", "CSimpleBuildingVFunc__GetClassNameString_0050ed00", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050ed10" },
                comment("CSimpleBuilding vtable 0x005dfcc4 slot 37 DATA xref 0x005dfd58 points at a constant-string getter. The body returns 0x0063d8c0, and string read-back at that address is \"CSimpleBuilding\"."),
                tags("csimplebuilding-vfunc", "string-return", "class-name")),
            new Spec("0x0050ed30", "CGroundUnitVFunc__GetClassNameString_0050ed30", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050ed40" },
                comment("CGroundUnit vtable 0x005e325c slot 37 DATA xref 0x005e32f0 points at a constant-string getter. The body returns 0x0063d8d0, and string read-back at that address is \"CGroundUnit\"."),
                tags("cgroundunit-vfunc", "string-return", "class-name")),
            new Spec("0x0050ed40", "CGroundUnitVFunc__ForwardArgWithFlags40000200_0050ed40", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050ed60" },
                comment("CGroundUnit vtable 0x005e325c slot 68 DATA xref 0x005e336c points at a flag-forwarding thunk. The body ORs the stack value with mask 0x40000200, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("cgroundunit-vfunc", "flag-forwarder")),
            new Spec("0x0050f120", "CAirUnitVFunc__GetClassNameString_0050f120", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050f130" },
                comment("CAirUnit vtable 0x005e3700 slot 37 DATA xref 0x005e3794 points at a constant-string getter. The body returns 0x0063d8e8, and string read-back at that address is \"CAirUnit\"."),
                tags("cairunit-vfunc", "string-return", "class-name")),
            new Spec("0x0050fca0", "CGillMHeadVFunc__IsField1f4NonNull_0050fca0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050fcb0" },
                comment("CGillMHead vtable 0x005e4180 slot 135 DATA xref 0x005e439c plus repeated unit-family DATA refs point at a compact bool-return body that returns whether this+0x1f4 is non-null."),
                tags("cgillmhead-vfunc", "field-test")),
            new Spec("0x0050fcd0", "CGillMHeadVFunc__ReturnField26cSlot3cOrFallbackFloat_0050fcd0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050fcf0" },
                comment("CGillMHead vtable 0x005e4180 slot 45 DATA xref 0x005e4234 plus repeated unit-family DATA refs point at a compact float-return/tail-call body. When this+0x26c is non-null it tail-jumps through that object's vtable slot +0x3c; otherwise it returns float data at 0x005dbe80."),
                tags("cgillmhead-vfunc", "float-return", "tail-call")),
            new Spec("0x0050fd00", "CGillMHeadVFunc__GetClassNameString_0050fd00", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050fd10" },
                comment("CGillMHead vtable 0x005e4180 slot 37 DATA xref 0x005e4214 points at a constant-string getter. The body returns 0x0063d9d8, and string read-back at that address is \"CGillMHead\"."),
                tags("cgillmhead-vfunc", "string-return", "class-name")),
            new Spec("0x0050fd10", "CGillMHeadVFunc__ForwardArgWithFlags40082000_0050fd10", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050fd30" },
                comment("CGillMHead vtable 0x005e4180 slot 68 DATA xref 0x005e4290 points at a flag-forwarding thunk. The body ORs the stack value with mask 0x40082000, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("cgillmhead-vfunc", "flag-forwarder"))
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception e) {
                stats.bad++;
                println("BAD: " + spec.address + " " + spec.name + " " + e.getMessage());
                throw e;
            }
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " bad=" + stats.bad);
    }
}
