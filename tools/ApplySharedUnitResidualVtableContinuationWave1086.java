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

public class ApplySharedUnitResidualVtableContinuationWave1086 extends GhidraScript {
    private static final String WAVE_TAG = "shared-unit-residual-vtable-continuation-wave1086";

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
            "wave1086-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "function-boundary-recovered",
            "vtable-boundary",
            "shared-unit-vtable"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    private String comment(String bodyEvidence) {
        return "Wave1086 static read-back: recovered shared unit-family residual vtable boundary. "
            + bodyEvidence
            + " Static retail Ghidra vtable/xref/instruction evidence only; exact source virtual name, concrete owner layout, runtime behavior, BEA patching, gameplay outcomes, and rebuild parity remain unproven.";
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

        Spec[] specs = new Spec[] {
            new Spec("0x00405dc0", "SharedUnitVFunc__ReturnFloat005d858c_00405dc0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405dd0" },
                comment("Body returns float constant/data value at 0x005d858c; sampled DATA vtable refs include slot 102 across CAirUnit/CRadar/ground-unit-family tables."),
                tags("float-return")),
            new Spec("0x00401f70", "SharedUnitVFunc__TestFieldCcDeltaBelow015_00401f70", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00401fa0" },
                comment("Body compares global float 0x00672fd0 minus this+0xcc against threshold 0x005d8588 and returns 1/0; sampled DATA vtable refs include slot 97."),
                tags("field-test")),
            new Spec("0x00405dd0", "SharedUnitVFunc__ReturnFloat005d8b9c_00405dd0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00405de0" },
                comment("Body returns float constant/data value at 0x005d8b9c; sampled DATA vtable refs include slot 103."),
                tags("float-return")),
            new Spec("0x0047c8b0", "SharedUnitVFunc__TestFieldCcDeltaBelowGroundThreshold_0047c8b0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0047c8e0" },
                comment("Body compares global float 0x00672fd0 minus this+0xcc against threshold 0x005dbd84 and returns 1/0; sampled CGroundUnit/CSentinel-style DATA refs include slot 97."),
                tags("field-test")),
            new Spec("0x004dfcb0", "SharedUnitVFunc__ReturnInvertedFlag2cMask4_004dfcb0", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x004dfcc0" },
                comment("Body reads this+0x2c, inverts the byte, masks bit 0x4, shifts to a 1/0 return; sampled DATA vtable refs include slots 74/79."),
                tags("flag-test")),
            new Spec("0x0050e860", "SharedUnitVFunc__ReturnFloat005dbe80_0050e860", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050e870" },
                comment("Body returns float constant/data value at 0x005dbe80; sampled DATA vtable refs include slot 45."),
                tags("float-return")),
            new Spec("0x0050eb60", "SharedUnitVFunc__ReturnFloat005d8cc4_0050eb60", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x0050eb70" },
                comment("Body returns float constant/data value at 0x005d8cc4; sampled DATA vtable refs include slots 102/103."),
                tags("float-return")),
            new Spec("0x004037a0", "SharedUnitVFunc__ApplyDamageAndResolveSlot19Vector_004037a0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("hitContext", voidPtr), param("sourceThing", voidPtr), param("arg2", voidPtr), param("arg3", voidPtr) },
                new String[] { "0x00403a50" },
                comment("Body forwards four stack arguments to CUnit__ApplyDamage at 0x004f9a90, checks this+0xf8/flags/this+0x258, calls vtable slot +0x160 with selector 0x19, updates vectors around candidate object fields +0x40/+0x80/+0xac, and returns with RET 0x10."),
                tags("damage-path", "vector-context")),
            new Spec("0x00403a90", "SharedUnitVFunc__ForwardVectorToField208WithScaledAngle_00403a90", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sourceVector", voidPtr), param("phase", floatType), param("limit", floatType), param("targetVector", voidPtr), param("callbackArg", voidPtr) },
                new String[] { "0x00403b60" },
                comment("Body checks this+0x208, quantizes float input through 0x0047ea20, clamps against this+0x164+0x15c, copies a 16-byte vector argument onto the stack, dispatches field208 vtable slot +0x10, and returns with RET 0x14."),
                tags("vector-context")),
            new Spec("0x00403b60", "SharedUnitVFunc__ReturnFlag2cScaledSlot40Float_00403b60", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00403ba0" },
                comment("Body returns 0.0 when flag byte this+0x2c lacks mask 0x4; otherwise calls vtable slot +0x40, caps against 0x005d8614, subtracts from 0x005d8610, scales by 0x005d860c, and returns float."),
                tags("float-return", "flag-test")),
            new Spec("0x00417660", "SharedUnitVFunc__ForwardArgWithFlags40100120_00417660", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x00417680" },
                comment("Body ORs the stack value with mask 0x40100120, forwards it to 0x004fcdc0, and returns with RET 0x4."),
                tags("flag-forwarder")),
            new Spec("0x00417680", "SharedUnitVFunc__ReturnField250_00417680", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00417690" },
                comment("Body returns dword this+0x250; sampled DATA vtable refs include slot 41."),
                tags("field-return")),
            new Spec("0x00417690", "SharedUnitVFunc__SetField250_00417690", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", intType) },
                new String[] { "0x004176a0" },
                comment("Body stores the stack value into this+0x250 and returns with RET 0x4; sampled DATA vtable refs include slot 42."),
                tags("field-setter")),
            new Spec("0x00417df0", "SharedUnitVFunc__HandleType1388Field74Resource_00417df0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("eventRecord", voidPtr) },
                new String[] { "0x00417e30" },
                comment("Body checks word eventRecord+0x4 for 0x1388, releases this+0x74 through 0x005337e0 and a scalar-deleting slot when present, clears this+0x74, otherwise forwards eventRecord to 0x004f9820, and returns with RET 0x4."),
                tags("resource-cleanup")),
            new Spec("0x004284f0", "CUnitAIVFunc__ReturnNegativeAtanField40Field50_004284f0", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00428500" },
                comment("Body loads this+0x40 and this+0x50, computes FPATAN, negates the result, and returns float; sampled CUnitAI-style DATA vtable refs include slot 122."),
                tags("float-return", "orientation")),
            new Spec("0x004287c0", "CUnitAIVFunc__CopyField26cSlot6cOrField7cVector_004287c0", "__thiscall", voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("outVector", voidPtr) },
                new String[] { "0x00428800" },
                comment("Body uses this+0x26c when non-null to dispatch its vtable slot +0x6c with outVector; otherwise copies a 16-byte vector from this+0x7c into outVector, returns outVector, and uses RET 0x4."),
                tags("vector-copy")),
            new Spec("0x00428be0", "CUnitAIVFunc__MaybeSmoothVectorTowardTarget_00428be0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("currentVector", voidPtr), param("targetVector", voidPtr), param("arg2", voidPtr), param("arg3", voidPtr) },
                new String[] { "0x00428c30" },
                comment("Body gates on flag byte this+0x2c mask 0x4, compares three floats from currentVector and targetVector, and calls CUnit__SmoothEulerTowardTargetAndBuildMatrix at 0x004fa4b0 when they differ; returns with RET 0x10."),
                tags("vector-context", "orientation")),
            new Spec("0x00428c30", "CUnitAIVFunc__ReturnFloat005d9434_00428c30", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00428c40" },
                comment("Body returns float constant/data value at 0x005d9434; sampled CUnitAI-style DATA refs include slot 103."),
                tags("float-return")),
            new Spec("0x00428c40", "CUnitAIVFunc__ReturnFloat005d8cb0_00428c40", "__thiscall", floatType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00428c50" },
                comment("Body returns float constant/data value at 0x005d8cb0; sampled CUnitAI-style DATA refs include slot 75."),
                tags("float-return")),
            new Spec("0x00428c50", "CUnitAIVFunc__ReturnField164_198Present_00428c50", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00428c70" },
                comment("Body loads this+0x164, tests nested field +0x198, and returns 1 when non-null or 0 when null; sampled CUnitAI-style DATA refs include slot 74."),
                tags("field-test")),
            new Spec("0x00428c90", "CUnitAIVFunc__CanDeployWhenField264Null_00428c90", "__thiscall", intType,
                new ParameterImpl[] { param("this", voidPtr) },
                new String[] { "0x00428cb0" },
                comment("Body returns 0 when this+0x264 is non-null; when null it tail-jumps to CUnit__CanDeployNow at 0x004fc000. Sampled CUnitAI-style DATA refs include slot 114."),
                tags("tail-call", "field-test")),
            new Spec("0x00428d30", "CUnitAIVFunc__CopyVector1cToOut_00428d30", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("outVector", voidPtr) },
                new String[] { "0x00428d50" },
                comment("Body copies the 16-byte vector at this+0x1c into outVector and returns with RET 0x4; sampled CUnitAI-style DATA refs include slot 120."),
                tags("vector-copy")),
            new Spec("0x0047a730", "CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("arg", voidPtr) },
                new String[] { "0x0047a760" },
                comment("Body forwards arg to 0x00427b80, then calls CComplexThing__SetAnimMode-like helper 0x004f4560 with GillMHead idle string token 0x0062ca48 and two boolean constants; sampled CUnitAI/GillMHead-adjacent DATA refs include slot 39."),
                tags("animation")),
            new Spec("0x0047a9c0", "CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0", "__thiscall", voidType,
                new ParameterImpl[] { param("this", voidPtr), param("mode", intType) },
                new String[] { "0x0047a9e0" },
                comment("Body reads mode, skips mode value 4, otherwise forwards it to CUnit__SetEngagementModeAndMaybeClearTargetReader at 0x004fdcb0, and returns with RET 0x4; sampled CUnitAI/GillMHead-adjacent DATA refs include slot 84."),
                tags("mode-forwarder"))
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
