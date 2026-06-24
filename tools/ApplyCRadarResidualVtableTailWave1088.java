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

public class ApplyCRadarResidualVtableTailWave1088 extends GhidraScript {
    private static final String WAVE_TAG = "cradar-residual-vtable-tail-wave1088";

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
            "wave1088-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "function-boundary-recovered",
            "vtable-boundary",
            "cradar-vtable"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    private String comment(String bodyEvidence) {
        return "Wave1088 static read-back: recovered CRadar residual vtable boundary from vtable 0x005dd710. "
            + bodyEvidence
            + " Static retail Ghidra vtable/xref/instruction/string evidence only; exact source virtual name, concrete CRadar/unit layout, runtime behavior, BEA patching, gameplay outcomes, and rebuild parity remain unproven.";
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
            new Spec("0x004bfb00", "CRadarVFunc__GetClassNameString_004bfb00", "__thiscall", charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004bfb10" },
                comment("Slot 37 DATA xref 0x005dd7a4 points at a compact constant-string getter. The body returns 0x00630c44, and string read-back at that address is \"CRadar\"."),
                tags("string-return", "class-name")),
            new Spec("0x0052ddb0", "SharedUnitVFunc__ReturnInt10_0052ddb0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0052ddc0" },
                comment("Slot 38 DATA xref 0x005dd7a8 plus additional DATA refs 0x005ddbbc and 0x005e4ca8 point at a two-instruction integer-return body that returns 0x0a."),
                tags("int-return", "shared-unit-vtable")),
            new Spec("0x004d6360", "CRadarVFunc__FlagArg70AndSeedMotion280_004d6360", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x004d63c0" },
                comment("Slot 39 DATA xref 0x005dd7ac points at a RET 0x4 body. It sets bit 0x20 in arg+0x70, calls 0x004f86d0 with the argument, copies 12 dwords from 0x0083c9d8 into this+0x250, derives a pseudo-random float through 0x0055dbfe/0x188b, and stores it at this+0x280."),
                tags("field-seed", "motion-fields", "arg-flag")),
            new Spec("0x004bfb20", "CRadarVFunc__ReturnFloat005d8bb8_004bfb20", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004bfb30" },
                comment("Slot 46 DATA xref 0x005dd7c8 points at a two-instruction float-return body that loads float data at 0x005d8bb8 and returns."),
                tags("float-return")),
            new Spec("0x004bfb10", "CRadarVFunc__ForwardArgWithLowFlag20_004bfb10", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x004bfb20" },
                comment("Slot 68 DATA xref 0x005dd820 points at a flag-forwarding thunk. The body ORs the low byte of the stack value with 0x20, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("flag-forwarder")),
            new Spec("0x004d63c0", "CRadarVFunc__UpdateMotionVector250FromAngle280_004d63c0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004d64b0" },
                comment("Slot 96 DATA xref 0x005dd890 points at a body that calls 0x004fa8d0, advances wrapped angle/state this+0x280, computes sine/cosine values, and writes a 3x4 vector/matrix-like block through this+0x250..0x278 before returning."),
                tags("motion-fields", "vector-context")),
            new Spec("0x004f6560", "CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("outTransform", voidPtr) },
                new String[] { "0x004f68e0" },
                comment("Slot 149 DATA xref 0x005dd964 points at a bounded output-buffer body. When this+0x34 is zero, it initializes/wraps frame index this+0x38 and copies 12 dwords from 0x008406b8 + index*0x30 to the caller output buffer. When this+0x40 is non-null, it computes vector/transform data through helpers 0x00401ec0, 0x00401f10, 0x00401ee0, 0x00406d50, and 0x00411a60, then copies a 12-dword transform to the output buffer. The next existing function is 0x004f68e0 CTree__VFunc_28_CreateFallingTreeAfterDelay."),
                tags("output-buffer", "transform-copy", "long-body"))
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
