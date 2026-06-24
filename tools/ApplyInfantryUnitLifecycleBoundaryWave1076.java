//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
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

public class ApplyInfantryUnitLifecycleBoundaryWave1076 extends GhidraScript {
    private static final String WAVE_TAG = "infantryunit-lifecycle-boundary-wave1076";

    private static class Spec {
        final String address;
        final String endRet;
        final String nextAddress;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String endRet, String nextAddress, String name, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.endRet = endRet;
            this.nextAddress = nextAddress;
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
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec);
    }

    private void applySignature(Function fn, Spec spec) throws Exception {
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
            SourceType.USER_DEFINED, spec.parameters);
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address
                + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
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
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address
                + ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
        AddressSetView body = fn.getBody();
        if (!body.contains(addr(spec.endRet))) {
            throw new IllegalStateException("Read-back body for " + spec.address
                + " does not include expected RET at " + spec.endRet);
        }
        if (body.contains(addr(spec.nextAddress))) {
            throw new IllegalStateException("Read-back body for " + spec.address
                + " unexpectedly absorbed next address " + spec.nextAddress);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreate(spec, dryRun, stats);
            if (fn == null) {
                stats.signatureUpdated++;
                stats.commentOnlyUpdated++;
                stats.updated++;
                return;
            }

            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
            boolean commentOrTagsNeedUpdate = fn.getComment() == null
                || !fn.getComment().equals(spec.comment)
                || !hasAllTags(fn, spec);

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (signatureNeedsUpdate) {
                    stats.signatureUpdated++;
                }
                else if (commentOrTagsNeedUpdate || renameNeeded) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (signatureNeedsUpdate) {
                applySignature(fn, spec);
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
            stats.updated++;
            println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            Thread.sleep(75L);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            WAVE_TAG,
            "wave1076-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "cinfantryunit",
            "vtable-slot",
            "signature-hardened",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String comment(String slot, String slotAddr, String endRet, String next, String body) {
        return "Wave1076 boundary recovery: CInfantryUnit primary vtable 0x005e2730 slot " + slot +
            " (slot address " + slotAddr + ") DATA-xrefs to this previously missing function. " +
            "Fresh pre-state listed the entry as INSTRUCTION_NO_FUNCTION with missing metadata and " +
            "missing decompile; the recovered body ends at " + endRet + " and does not absorb " +
            "the next adjacent entry/function at " + next + ". " + body + " Static retail " +
            "Ghidra metadata/xref/instruction/vtable evidence only; exact source virtual name, " +
            "concrete CInfantryUnit/CUnitAI/layout semantics, runtime infantry behavior, BEA " +
            "patching, gameplay outcomes, and rebuild parity remain separate proof.";
    }

    private Spec[] specs() throws Exception {
        DataType voidPtr = voidPtr();
        DataType intType = IntegerDataType.dataType;
        return new Spec[] {
            new Spec(
                "0x00488f10",
                "0x00488f5c",
                "0x00488f60",
                "CInfantryUnit__VFunc38_HandleHitOrDispatchHit",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("otherThing", voidPtr),
                    param("collisionReport", voidPtr)
                },
                comment("38", "0x005e27c8", "0x00488f5c RET 0x8", "0x00488f60",
                    "Body checks otherThing+0x34 flag 0x20000, this+0x2c flag 0x4, and global time delta against this+0xcc; it either dispatches through this vtable offset +0xa0 with immediate 0x41200000/-1/1 arguments or forwards to CThing__CreateHitRefEvaluateImpulseAndDispatchHit(otherThing, collisionReport)."),
                tags("vfunc38", "hit-dispatch", "collision-report")
            ),
            new Spec(
                "0x00488f80",
                "0x0048902f",
                "0x00489040",
                "CInfantryUnit__VFunc34_CreateCollisionSphereWithAttachmentRadius",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("collisionOwner", voidPtr)
                },
                comment("34", "0x005e27b8", "0x0048902f RET 0x4", "0x00489040",
                    "Body queries the subobject at this+0x8 through vtable offset +0x54, optionally allocates a 0x20-byte helper from CDXMemoryManager__Alloc using Infantry.cpp debug string 0x0062d4a8 line 0x7a/allocation value 0x5c, stores vtable 0x005d88cc, writes collisionOwner+0x0c, then calls CGroundUnit__CreateCollisionSphere(this, collisionOwner) on both success and fallback paths."),
                tags("vfunc34", "collision-sphere", "infantry-debug-string")
            ),
            new Spec(
                "0x00489090",
                "0x004892af",
                "0x004892c0",
                "CInfantryUnit__VFunc59_SelectAnimationMode",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("requestedMode", intType),
                    param("resetFrame", intType),
                    param("forceLooped", intType)
                },
                comment("59", "0x005e281c", "0x004892af RET 0xc", "0x004892c0",
                    "Body returns 0 when this+0x110 is null, otherwise derives an animation mode from requestedMode, movement/vector length, state flags, and CMesh__FindAnimationIndexByName lookups for Infantry.cpp animation-name tokens, then calls CComplexThing__SetAnimMode(this, selectedMode, resetFrame, forceLooped)."),
                tags("vfunc59", "animation-mode", "mesh-animation")
            ),
            new Spec(
                "0x004892c0",
                "0x0048964d",
                "0x00489650",
                "CInfantryUnit__VFunc65_UpdateMotionAnimationState",
                "__fastcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                comment("65", "0x005e2834", "0x0048964d RET", "0x00489650",
                    "Body calls CGroundUnit__UpdateLinkedEffectsByHeightClearance, samples movement/orientation vectors, decrements this+0x268 from this+0x260, samples CStaticShadows__SampleShadowHeightBilinear, dispatches this vtable offsets +0x70/+0xc0/+0xf0/+0x10c, and calls CComplexThing__AddShutdownEvent on one branch."),
                tags("vfunc65", "motion-update", "animation-state", "static-shadow")
            ),
            new Spec(
                "0x00489650",
                "0x00489b36",
                "0x00489b40",
                "CInfantryUnit__VFunc39_HandleCollisionDamageReaction",
                "__thiscall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("collisionContext", voidPtr),
                    param("otherThing", voidPtr),
                    param("impactContext", voidPtr),
                    param("damageContext", voidPtr)
                },
                comment("39", "0x005e27cc", "0x00489b36 RET 0x10", "0x00489b40",
                    "Body checks this+0x2c and otherThing+0x34 flags, samples CRound__GetPresetScalarByConfigName and Random__NextLCGAbs, computes distance/impact vectors, can call CUnit__ApplyDamage, and uses animation/effect dispatch helpers before returning through the shared tail at 0x00489b31."),
                tags("vfunc39", "collision-damage", "impact-reaction", "unit-damage")
            ),
            new Spec(
                "0x00489b40",
                "0x00489dde",
                "0x00489de0",
                "CInfantryUnit__VFunc49_HandleDeathPickupAndEffects",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                comment("49", "0x005e27f4", "0x00489dde RET", "0x00489de0",
                    "Body calls CGroundUnit__MarkDestroyedAndResetState, sets the collision-seeking round mask to -1, creates a pickup via CWorldPhysicsManager__CreatePickup, builds a stack CInitThing-like payload, checks height/linked state, creates a particle effect through CParticleManager__CreateEffect, clears linked flags through CGroundUnit__ClearLinkedThingFlagsAndResetCounter, and returns 1 on the normal completed path."),
                tags("vfunc49", "death-pickup", "particle-effect", "destroyed-state")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyInfantryUnitLifecycleBoundaryWave1076 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println(summary(stats));
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1076 InfantryUnit lifecycle boundary apply encountered missing/bad rows");
        }
    }

    private String summary(Stats stats) {
        return "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad;
    }
}
