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

public class ApplyUnitDeploySupportWave524 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
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
            "unit-deploy-support-wave524",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }
        if (!needsUpdate(fn, spec)) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRYUPDATE: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.updateFunction(spec.callingConvention, null, FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
            SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("UPDATED: " + spec.address + " " + spec.name + " :: " + fn.getSignature());
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        DataType voidType = VoidDataType.dataType;
        DataType ptr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x004fb780", "CSquadNormal__GetSupportMinEngageDistance", "__thiscall", floatType, new ParameterImpl[] {
                param("this", ptr),
                param("ballistic_context", ptr),
                param("aim_x", floatType),
                param("aim_y", floatType),
                param("aim_z", floatType)
            }, "Wave524 signature/comment hardening: RET 0x10 proves four explicit stack arguments after ECX. When this+0x140 is active, forwards the context/vector triple to CUnit__ComputeMinBallisticTravelDistance; otherwise uses the active reader profile +0x2c or the global fallback float. Exact profile layout, float semantics, runtime support selection, and rebuild parity remain unproven.",
                tags("squad-support", "range-helper")),
            new Spec("0x004fb7e0", "CSquadNormal__GetSupportMaxEngageDistance", "__thiscall", floatType, new ParameterImpl[] {
                param("this", ptr),
                param("ballistic_context", ptr),
                param("aim_x", floatType),
                param("aim_y", floatType),
                param("aim_z", floatType)
            }, "Wave524 signature/comment hardening: RET 0x10 proves four explicit stack arguments after ECX. When this+0x140 is active, forwards the context/vector triple to CUnit__ComputeMaxBallisticTravelDistance; otherwise uses the active reader profile +0x30 or the global fallback float. Exact profile layout, float semantics, runtime support selection, and rebuild parity remain unproven.",
                tags("squad-support", "range-helper")),
            new Spec("0x004fb840", "CSquadNormal__SelectBestSupportOrEscort", "__thiscall", voidType, new ParameterImpl[] {
                param("this", ptr),
                param("target_unit", ptr)
            }, "Wave524 signature/comment hardening: RET 0x4 proves one explicit target_unit argument after ECX. The body clears the prior support reader, scores linked support units at this+0x18c and active-mask units at this+0x17c against target range, mask, height-window, ballistic-distance, and blocked-support predicates, then stores either this+0x140 or this+0x144. Runtime squad AI behavior, exact lists/profile layouts, exact mode semantics, and rebuild parity remain unproven.",
                tags("squad-support", "selection-helper")),
            new Spec("0x004fbc90", "CWarspite__GetMountedUnitPitchOrZero", "__thiscall", floatType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave524 signature/comment hardening: ECX-only helper returns the active linked unit/profile float at this+0x140 -> +0xa0 -> +0x88, or the global fallback float when no active link exists. The strongest named caller remains CWarspite__Update, but the field meaning and runtime pitch/use semantics remain unproven.",
                tags("warspite-context", "support-profile")),
            new Spec("0x004fbcb0", "CUnit__UpdateDeployStateAndChargeEffects", "__thiscall", intType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave524 signature/comment hardening: ECX-only deploy/support state helper. It gates active support readers at +0x144 and mounted unit profiles at +0x140, updates state/timer fields +0x168/+0x16c/+0x1e8/+0x1ec, plays profile sound/effects, emits charge attachment particles, and starts the deploying animation when profile state permits. Exact state enum names, profile layout, runtime deploy behavior, and rebuild parity remain unproven.",
                tags("unit-deploy", "support-profile")),
            new Spec("0x004fc000", "CUnit__CanDeployNow", "__thiscall", intType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave524 signature/comment hardening: ECX-only deploy readiness predicate. Reader-backed support is allowed unless blocked support candidates are present under profile flag +0x110; mounted-unit support requires +0x1e8 and CUnit__IsEligibleByDistanceBucketOrRange on this+0x140. Exact state/flag semantics, runtime deploy behavior, and rebuild parity remain unproven.",
                tags("unit-deploy", "support-profile")),
            new Spec("0x004fc080", "CUnitAI__TrySpawnOrFinalizeAttachedUnit", "__thiscall", intType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave524 signature/comment hardening: ECX-only activation/spawn helper. Reader-backed support calls vfunc +0x1cc and CSpawnerThng__DoSpawn, then updates state/timer fields from profile +0x38; mounted-unit support can spawn the projectile burst fallback, call vfunc +0x15c, and clear +0x1e8/+0x1ec. Exact CUnitAI state names, spawn semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("unit-ai", "spawn-helper", "support-profile")),
            new Spec("0x004fc170", "CUnitAI__FinalizeSpawnAndAdvanceState", "__thiscall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave524 signature/comment hardening: ECX-only finalize helper reached from CUnitAI firing/postfire flow and vtable data. It optionally plays the active profile sound at +0x14, recursively spawns component effects, clears +0x1e8, and either advances state/timer fields from profile +0x8c or resets +0x168. Exact state enum names, profile layout, runtime behavior, and rebuild parity remain unproven.",
                tags("unit-ai", "spawn-helper", "support-profile")),
            new Spec("0x004fc220", "CUnit__SpawnComponentEffectsRecursive", "__thiscall", voidType, new ParameterImpl[] {
                param("this", ptr)
            }, "Wave524 signature/comment hardening: ECX-only recursive component-effect spawner. The body walks component/effect handles at +0x1c4 when the profile effect at this+0x164+0x1c exists, creates particle effects, copies transform/basis data into spawned renderers, refreshes mesh renderer time, then recurses through child units at +0x19c. Exact component/effect handle layouts, runtime particle behavior, and rebuild parity remain unproven.",
                tags("unit-effects", "recursive-helper")),
            new Spec("0x004fc4e0", "CUnit__UpdateTransform", "__thiscall", voidType, new ParameterImpl[] {
                param("this", ptr),
                param("emitter_slot_tag", intType),
                param("cache_key", intType),
                param("out_position4", ptr),
                param("out_basis3x4", ptr)
            }, "Wave524 signature/comment hardening: RET 0x10 proves four explicit stack arguments after ECX. The body resolves or creates a cached emitter transform entry keyed by emitter_slot_tag/cache_key, maps slot tags through CUnit__FindEmitterIndexBySlotTag, writes a transformed 4-float position to out_position4 and a multiplied 3x4 basis to out_basis3x4, or falls back to tag lookup for excluded waypoint slots. This corrects older docs that over-described general movement/terrain updates; exact cache-entry layout, slot enum names, runtime behavior, and rebuild parity remain unproven.",
                tags("unit-emitter-transform", "signature-corrected")),
            new Spec("0x004fc6e0", "CUnit__FindEmitterIndexBySlotTag", "__thiscall", intType, new ParameterImpl[] {
                param("this", ptr),
                param("emitter_slot_tag", intType),
                param("cache_key", intType),
                param("out_position4", ptr),
                param("out_basis3x4", ptr),
                param("flag_a", intType),
                param("flag_b", intType)
            }, "Wave524 signature/comment hardening: RET 0x18 proves six explicit stack arguments after ECX. The switch maps emitter_slot_tag values 1..0x1d to mesh/attachment names such as SpawnerA-E, WaypointA-E, Component, Engine, Trail, Smoke, Thruster, Doorstop, Activation, and Charge, then forwards the name plus cache/output/flag arguments through the mesh/profile vfunc +0x1c. Exact slot enum names, forwarded argument semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("unit-emitter-transform", "slot-map"))
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave524 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
