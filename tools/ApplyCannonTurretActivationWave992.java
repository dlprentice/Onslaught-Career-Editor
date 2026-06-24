//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCannonTurretActivationWave992 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private int missingTagCount(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        return missingTagCount(fn, spec) == 0;
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            ok = false;
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.name);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            stats.bad++;
            return;
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
            stats.bad++;
            return;
        }

        boolean needsComment = !spec.comment.equals(fn.getComment());
        int tagsToAdd = missingTagCount(fn, spec);
        boolean needsUpdate = needsComment || tagsToAdd != 0;
        if (!needsUpdate) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }

        stats.commentOnlyUpdated++;
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsComment=" + needsComment
                + " tagsToAdd=" + tagsToAdd);
            stats.tagsAdded += tagsToAdd;
            stats.skipped++;
            return;
        }

        if (needsComment) {
            fn.setComment(spec.comment);
        }
        for (String tag : spec.tags) {
            if (!tagNames(fn).contains(tag)) {
                fn.addTag(tag);
                stats.tagsAdded++;
            }
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.name);
        }
        stats.updated++;
        currentProgram.flushEvents();
        Thread.sleep(50L);
    }

    private String[] commonTags(String... extra) {
        String[] base = new String[] {
            "static-reaudit",
            "cannon-turret-activation-review-wave992",
            "wave992-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "tag-corrected",
            "cannon"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyCannonTurretActivationWave992 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0041b1a0",
                "CCannon__Init",
                "void __thiscall CCannon__Init(void * this, void * init)",
                "Wave992 Cannon/turret activation review: CCannon init takes this plus an init object, sets init flags, calls CGroundUnit__Init, chooses Active/Inactive animation state from +0x214, allocates CTerrainGuide/CWarspite-or-target-controller/CMCCannon helper objects, stores helpers at +0x208/+0x13c/+0x70, seeds +0x260/+0x264 state, registers with the world occupancy grid, and sets the height-threshold flag at +0x258. Static retail Ghidra evidence only; exact source identity, concrete layout, runtime turret/firing behavior, and rebuild parity remain unproven.",
                commonTags("activation-state", "occupancy-grid", "motion-controller")
            ),
            new Spec(
                "0x0041b370",
                "CCannon__UpdateState",
                "void __fastcall CCannon__UpdateState(void * this)",
                "Wave992 Cannon/turret activation review: CCannon activation update tests enable/target-controller state through +0x214 and +0x13c, requests Activate or Deactivate animations, updates state +0x260 and timestamp +0x264, and calls CGroundUnit__UpdateLinkedEffectsByHeightClearance in both active and inactive paths. Static retail Ghidra evidence only; exact source method name, runtime turret behavior, and rebuild parity remain unproven.",
                commonTags("activation-state", "groundunit-bridge", "linked-effects")
            ),
            new Spec(
                "0x0041b450",
                "CCannon__VFuncSlot_02_RemoveFromWorldAndForward",
                "void __fastcall CCannon__VFuncSlot_02_RemoveFromWorldAndForward(void * this)",
                "Wave992 Cannon/turret activation review: this is not a destructor body. Vtable DATA refs place the slot-2 entry in CCannon, CSentinel, and CWarspiteDome tables; the body removes the unit from the world occupancy-grid wrapper and forwards to CUnit__VFunc02_CleanupWorldLinksAndForward. Static retail Ghidra evidence only; exact owning base class, source virtual name, runtime world/render behavior, and rebuild parity remain unproven.",
                commonTags("vtable-slot", "occupancy-grid", "owner-corrected")
            ),
            new Spec(
                "0x0041b470",
                "CCannon__AdvanceActivationAnimationState",
                "int __fastcall CCannon__AdvanceActivationAnimationState(void * this)",
                "Wave992 Cannon/turret activation review: this no-argument helper does not set an arbitrary state; it reads the current animation, resolves Activate/Deactivate/Active/Inactive animation ids, advances completed activation/deactivation transitions, and writes state +0x260 to Active or Inactive. Static retail Ghidra evidence only; exact source method name, return semantics, runtime animation behavior, and rebuild parity remain unproven.",
                commonTags("activation-state", "animation-state", "owner-corrected")
            ),
            new Spec(
                "0x0041b540",
                "CCannon__GetMidpoint",
                "void __thiscall CCannon__GetMidpoint(void * this, float * outMidpoint)",
                "Wave992 Cannon/turret activation review: resolves a target position through CCannon__SelectTarget, adds this unit position at +0x1c/+0x20/+0x24, and scales the sum by the 0.5 constant to produce an output midpoint. Static retail Ghidra evidence only; exact vector type/layout, runtime targeting behavior, and rebuild parity remain unproven.",
                commonTags("target-selection", "midpoint")
            ),
            new Spec(
                "0x0041b590",
                "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph",
                "int __fastcall CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph(void * this)",
                "Wave992 Cannon/turret activation review: current read-back does not support the old CanFire label. Vtable refs place this slot-50 entry in CCannon, CWarspiteDome, and CGroundVehicle tables; the body calls CGroundUnit__MarkDestroyedAndResetState and then CUnit__ResetDeploymentGraphAndScheduleEvent on success. Static retail Ghidra evidence only; exact owning base class, source virtual name, runtime destruction/deploy behavior, and rebuild parity remain unproven.",
                commonTags("vtable-slot", "destruction-reset", "groundunit-bridge", "owner-corrected")
            ),
            new Spec(
                "0x004fd4d0",
                "CCannon__SelectTarget",
                "void __thiscall CCannon__SelectTarget(void * this, float * outTargetPosition)",
                "Wave992 Cannon/turret activation review: takes this plus outTargetPosition; if linked target +0x178 exists, forwards to CDiveBomber__SelectTarget, otherwise writes this unit center position through CThing__GetCentrePos. Static retail Ghidra evidence only; exact source method name, target semantics, runtime behavior, and rebuild parity remain unproven.",
                commonTags("target-selection", "cthing-centre")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave992 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
