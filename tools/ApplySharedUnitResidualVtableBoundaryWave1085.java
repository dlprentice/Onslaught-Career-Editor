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

public class ApplySharedUnitResidualVtableBoundaryWave1085 extends GhidraScript {
    private static final String WAVE_TAG = "shared-unit-residual-vtable-boundary-review-wave1085";

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
            "wave1085-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "comment-hardened",
            "signature-hardened",
            "shared-vfunc",
            "unit-family-vtable"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    private String comment(String detail) {
        return "Wave1085 shared unit-family residual vtable-boundary recovery: repeated CAirUnit/CRadar/unit-family vtable slots point at this previously functionless .text body. "
            + detail
            + " Static retail Ghidra listing/xref/vtable evidence only; exact source virtual name, concrete layout semantics, runtime behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.";
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        PointerDataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidType = VoidDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00401550", "SharedUnitVFunc__WriteVector1cMinus8cToOut_00401550", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("outVector", voidPtr) },
                new String[] { "0x00401580" },
                comment("It writes a three-float delta from this+0x1c/0x20/0x24 minus this+0x8c/0x90/0x94 into the caller output vector and returns with RET 0x4."),
                tags("vector-delta", "field1c", "field8c", "ret4")),
            new Spec("0x004fd440", "SharedUnitVFunc__TestField17c19cReadiness_004fd440", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fd5e0" },
                comment("It walks this+0x17c/0x19c style member lists, checks nested entry state/float fields, returns boolean-style EAX, and stops before the adjacent 0x004fd5e0 body."),
                tags("field17c", "field19c", "boolean")),
            new Spec("0x004fc3c0", "SharedUnitVFunc__ResolveField17cVectorContext_004fc3c0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("candidate", voidPtr), param("outA", voidPtr), param("outB", voidPtr), param("arg3", voidPtr), param("arg4", voidPtr) },
                new String[] { "0x004fc6e0" },
                comment("It checks whether a supplied candidate appears in the this+0x17c list, copies fallback/vector contexts through 0x0044a850 and 0x0044a930, and returns with RET 0x14."),
                tags("field17c", "vector-context", "ret14")),
            new Spec("0x004f9a10", "SharedUnitVFunc__ReturnField178Or164C0Float_004f9a10", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004f9a40" },
                comment("It tail-calls 0x004443b0 when this+0x178 exists, otherwise returns float field this+0x164+0xc0 or static zero-like float 0x005d856c."),
                tags("field178", "field164", "float-return")),
            new Spec("0x004f9220", "SharedUnitVFunc__CountNestedThingListAndDispatch_004f9220", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("thing", voidPtr) },
                new String[] { "0x004f9260" },
                comment("It reads the stack argument's field+0x3bc list, increments global counter 0x0083da30 for non-null entries, calls 0x00452b60, and returns with RET 0x4."),
                tags("nested-list", "global-counter", "ret4")),
            new Spec("0x004fe4a0", "SharedUnitVFunc__CopySourceVectors114120AndRefresh_004fe4a0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("source", voidPtr) },
                new String[] { "0x004fe500" },
                comment("It samples a source argument through 0x0044adb0 twice, copies two three-dword vectors into this+0x114 and this+0x120, calls 0x004019b0, and returns with RET 0x4."),
                tags("field114", "field120", "vector-copy", "ret4")),
            new Spec("0x004fdc90", "SharedUnitVFunc__IsField13cNotMode2_004fdc90", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fdcb0" },
                comment("It checks this+0x13c and returns 0 only when field+0x20 equals mode value 2; otherwise it returns 1."),
                tags("field13c", "mode2", "boolean")),
            new Spec("0x004fdd60", "SharedUnitVFunc__PropagateNameToField18c19c_004fdd60", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("name", voidPtr) },
                new String[] { "0x004fde10" },
                comment("It copies the supplied name/string into this+0x18c entries, then walks this+0x19c and dispatches virtual slot +0xfc with the same name before returning with RET 0x4."),
                tags("field18c", "field19c", "name-propagation", "ret4")),
            new Spec("0x00417620", "SharedUnitVFunc__ReturnField164Float154_00417620", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00417630" },
                comment("It returns float field this+0x164+0x154 and stops before the existing 0x00417630 helper."),
                tags("field164", "field154", "float-return")),
            new Spec("0x00417610", "SharedUnitVFunc__ReturnField164E4_00417610", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00417620" },
                comment("It returns dword field this+0x164+0xe4 and stops before the adjacent 0x00417620 float-return body."),
                tags("field164", "fielde4")),
            new Spec("0x00417600", "SharedUnitVFunc__SetField160_00417600", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x00417610" },
                comment("It stores the stack argument into this+0x160 and returns with RET 0x4."),
                tags("field160", "setter", "ret4")),
            new Spec("0x004175e0", "SharedUnitVFunc__ReturnField13cCOrZero_004175e0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00417600" },
                comment("It returns this+0x13c+0x0c when the field13c pointer exists, otherwise returns zero."),
                tags("field13c", "field0c", "nullable-return")),
            new Spec("0x00405e50", "SharedUnitVFunc__ReturnField210_00405e50", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e60" },
                comment("It returns dword field this+0x210 and stops before the existing 0x00405e60 float-return body."),
                tags("field210")),
            new Spec("0x00405e40", "SharedUnitVFunc__ReturnField15c_00405e40", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e50" },
                comment("It returns dword field this+0x15c and stops before the adjacent 0x00405e50 body."),
                tags("field15c")),
            new Spec("0x00405e20", "SharedUnitVFunc__ClearField1f0_00405e20", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e30" },
                comment("It stores zero to this+0x1f0 and returns."),
                tags("field1f0", "setter", "clear")),
            new Spec("0x00405e10", "SharedUnitVFunc__SetField1f0One_00405e10", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e20" },
                comment("It stores one to this+0x1f0 and returns."),
                tags("field1f0", "setter")),
            new Spec("0x00405de0", "SharedUnitVFunc__TestField168Or214OrFlag2c_00405de0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405e10" },
                comment("It returns a boolean-style result from this+0x168, this+0x214, and the this+0x2c flag mask 0x4."),
                tags("field168", "field214", "flag2c", "boolean")),
            new Spec("0x00405e30", "SharedUnitVFunc__SetField15c_00405e30", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x00405e40" },
                comment("It stores the stack argument into this+0x15c and returns with RET 0x4."),
                tags("field15c", "setter", "ret4")),
            new Spec("0x00401900", "SharedUnitVFunc__ForwardArgToThingBridge_00401900", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x00401910" },
                comment("It forwards its stack argument to helper 0x004f3cb0 and returns with RET 0x4."),
                tags("helper-forward", "ret4")),
            new Spec("0x00401910", "SharedUnitVFunc__CopyTransformAndNotify_00401910", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sourceBlock", voidPtr) },
                new String[] { "0x004019b0" },
                comment("It copies a caller block into this+0x8c, calls 0x004f3ce0, optionally dispatches a virtual slot +0x14 through field this+0x38, and returns with RET 0x4."),
                tags("transform-copy", "field8c", "virtual-dispatch", "ret4")),
            new Spec("0x004175c0", "SharedUnitVFunc__ReturnField164FloatF4_004175c0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004175d0" },
                comment("It returns float field this+0x164+0xf4 and stops before the adjacent 0x004175d0 body."),
                tags("field164", "fieldf4", "float-return")),
            new Spec("0x004175d0", "SharedUnitVFunc__ReturnField164FloatF8_004175d0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004175e0" },
                comment("It returns float field this+0x164+0xf8 and stops before the adjacent 0x004175e0 body."),
                tags("field164", "fieldf8", "float-return")),
            new Spec("0x004fce00", "SharedUnitVFunc__ForwardField208Slot10_004fce00", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg0", voidPtr), param("arg1", voidPtr), param("arg2", voidPtr), param("arg3", voidPtr), param("arg4", voidPtr) },
                new String[] { "0x004fce40" },
                comment("It forwards a five-argument stack payload to this+0x208 virtual slot +0x10 when field208 exists and returns with RET 0x14."),
                tags("field208", "virtual-dispatch", "ret14")),
            new Spec("0x004fb270", "SharedUnitVFunc__ReturnField114Float_004fb270", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004fb280" },
                comment("It returns float field this+0x114 and stops before the adjacent 0x004fb280 body."),
                tags("field114", "float-return"))
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
            throw new IllegalStateException("Wave1085 shared unit residual vtable-boundary recovery encountered bad rows");
        }
    }
}
