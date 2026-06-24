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

public class ApplyHiveBossUnitVtableTailReviewWave1087 extends GhidraScript {
    private static final String WAVE_TAG = "hiveboss-unit-vtable-tail-review-wave1087";

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
            "wave1087-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "function-boundary-recovered",
            "vtable-boundary",
            "hiveboss-vtable"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    private String comment(String bodyEvidence) {
        return "Wave1087 static read-back: recovered CHiveBoss/unit-family vtable tail boundary from vtable 0x005e1668. "
            + bodyEvidence
            + " Static retail Ghidra vtable/xref/instruction/string evidence only; exact source virtual name, concrete CHiveBoss/unit layout, runtime behavior, BEA patching, gameplay outcomes, and rebuild parity remain unproven.";
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
            new Spec("0x00480000", "CHiveBossVFunc__CheckField170AndMaybeReturn64_00480000", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x00480050" },
                comment("Slot 26 DATA xref 0x005e16d0 points at a compact body that checks this+0x170 and this+0x29c, compares nested field +0x14 against global 0x00672fd0, may call 0x00441740 with string 0x0062ccb8 \"!!all flash!!\", returns 0x64 on that path, otherwise forwards the stack argument to 0x004fd5e0; returns with RET 0x4."),
                tags("hiveboss-vfunc", "field-test", "arg-forwarder")),
            new Spec("0x0050eb10", "CHiveBossVFunc__GetClassNameString_0050eb10", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050eb20" },
                comment("Slot 37 DATA xref 0x005e16fc points at a constant-string getter. The body returns 0x0063d844, and string read-back at that address is \"CHiveBoss\"."),
                tags("hiveboss-vfunc", "string-return", "class-name")),
            new Spec("0x0050eb20", "CHiveBossVFunc__ForwardArgWithFlags40100400_0050eb20", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x0050eb40" },
                comment("Slot 68 DATA xref 0x005e1778 points at a flag-forwarding thunk. The body ORs the stack value with mask 0x40100400, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("hiveboss-vfunc", "flag-forwarder")),
            new Spec("0x00480050", "CHiveBossVFunc__ForwardApplyDamageUnlessFlag01000000_00480050", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("hitContext", voidPtr), param("sourceThing", voidPtr), param("arg2", voidPtr), param("arg3", voidPtr) },
                new String[] { "0x00480080" },
                comment("Slot 70 DATA xref 0x005e1780 points at a RET 0x10 body that tests dword field hitContext+0x34 for mask 0x01000000 and, when the mask is clear, forwards four stack arguments to CUnit__ApplyDamage at 0x004f9a90."),
                tags("hiveboss-vfunc", "damage-path", "flag-test")),
            new Spec("0x0050eb40", "CHiveBossVFunc__ReturnFloat005d8580_0050eb40", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050eb50" },
                comment("Slot 75 DATA xref 0x005e1794 points at a two-instruction float-return body that loads float data at 0x005d8580 and returns."),
                tags("hiveboss-vfunc", "float-return")),
            new Spec("0x004802f0", "CHiveBossVFunc__MaybeScheduleEvent1388ForField74_004802f0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00480340" },
                comment("Slot 80 DATA xref 0x005e17a8 points at a body that calls 0x004fd140, returns zero if that test fails, then checks this+0x74 and may call 0x0044b370 through global context 0x00672fc8 with event/type value 0x1388 and -1.0f before returning one."),
                tags("hiveboss-vfunc", "event-path", "field-test")),
            new Spec("0x00480220", "CHiveBossVFunc__AccumulateMotionOffsetsThenTailJmp4fa8d0_00480220", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004802f0" },
                comment("Slot 96 DATA xref 0x005e17e8 points at a body that adds this+0x29c into this+0x114, snapshots fields this+0x250..0x264 into this+0x26c..0x280, accumulates float deltas from this+0x284..0x298 back into this+0x250..0x264, then tail-jumps to 0x004fa8d0."),
                tags("hiveboss-vfunc", "motion-fields", "tail-call")),
            new Spec("0x00480690", "CHiveBossVFunc__ForwardArgToThingHelper4f3ac0_00480690", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x004806a0" },
                comment("Slot 120 DATA xref 0x005e1848 points at a compact thunk after CHiveBoss__SetVar. The body forwards the stack argument to helper 0x004f3ac0 and returns with RET 0x4."),
                tags("hiveboss-vfunc", "arg-forwarder")),
            new Spec("0x00480340", "CHiveBossVFunc__BuildField164ContextAndDispatch_00480340", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004804c0" },
                comment("Slot 125 DATA xref 0x005e185c points at a large stack-context body before CHiveBoss__SetVar. It checks this+0x164, initializes a stack context through 0x0048dcf0, uses this+0x30 slot +0x20 or this+0x1c as position input, calls 0x0050ff10 on field164+0xec, walks global list head 0x008553f8, and dispatches the built context through the returned object's vtable slot +0x24."),
                tags("hiveboss-vfunc", "field164-context", "dispatch")),
            new Spec("0x00480080", "CHiveBossVFunc__ComputeScaledOffsetVectorToOut_00480080", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("outVector", voidPtr) },
                new String[] { "0x00480220" },
                comment("Slot 140 DATA xref 0x005e1898 points at a bounded vector-output body. It compares this+0x1c against a global object at 0x008a9d3c+0x1c, normalizes/scales the offset using this+0x2a0 and helper 0x0047eb80, conditionally updates the candidate vector, then writes four dwords to the caller output buffer and returns with RET 0x4."),
                tags("hiveboss-vfunc", "vector-context", "output-buffer"))
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
