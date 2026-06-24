//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyDestructableSegmentsMotionReviewWave942 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;

        Target(String address, String name, String signature, String comment) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
        }
    }

    private static final Target[] TARGETS = new Target[] {
        new Target(
            "0x00494c60",
            "CDestructableSegmentsMotionController__Ctor",
            "void * __thiscall CDestructableSegmentsMotionController__Ctor(void * this, void * segment_controller)",
            "Wave942 comment normalization over Wave430: RET 0x4 proves one segment_controller stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc27c, stores the supplied segment/controller pointer at +0x0c, and caches +0x10+8 at +0x08 when present. Xref read-back shows CMCHiveBoss__Constructor calls this at 0x0049709f with owner_hiveboss+0x178, and vtable 0x005dc27c is a nested destructable-segments motion table after the CMCBuggy slots. Static retail Ghidra evidence only; exact class ownership/layout, runtime rumble/cylinder behavior, BEA patching, and rebuild parity remain unproven."
        ),
        new Target(
            "0x00494ca0",
            "CDestructableSegmentsMotionController__ScalarDeletingDestructor",
            "void * __thiscall CDestructableSegmentsMotionController__ScalarDeletingDestructor(void * this, byte delete_flags)",
            "Wave942 read-back over Wave430: RET 0x4 confirms one delete-flags stack argument. Vtable read-back places this at 0x005dc27c slot 1, adjacent to the 0x00494c60 constructor and shared motion-controller slots, so the older CMCBuggy wheel-specific owner label was too narrow. The wrapper calls CDestructableSegmentsMotionController__Destructor and conditionally frees this when flags bit 0 is set. Static retail evidence only; exact class ownership/layout, runtime destruction coverage, BEA patching, and rebuild parity remain unproven."
        ),
        new Target(
            "0x00494cc0",
            "CDestructableSegmentsMotionController__Destructor",
            "void __fastcall CDestructableSegmentsMotionController__Destructor(void * this)",
            "Wave942 comment normalization over Wave430: the body has no stack cleanup, restores vtable 0x005dc27c, clears +0x08/+0x0c, and calls the base motion-controller destructor. Xref read-back shows calls from CDestructableSegmentsMotionController__ScalarDeletingDestructor and the one-instruction JMP thunk CDestructableSegmentsMotionController__DestructorThunk_00497130. Static retail Ghidra evidence only; exact class ownership/layout, runtime destruction coverage, BEA patching, and rebuild parity remain unproven."
        ),
        new Target(
            "0x00494ce0",
            "CDestructableSegmentsMotionController__ApplyRumbleTransform",
            "void __thiscall CDestructableSegmentsMotionController__ApplyRumbleTransform(void * this, void * state_context, void * segment_state, void * transform)",
            "Wave942 read-back over Wave430: RET 0x10 confirms four stack arguments after this, and vtable read-back places this at 0x005dc27c slot 4. The body samples a target/fallback value via CMCBuggy__GetTargetValueOrFallback, accumulates it into a per-segment state field, clamps/uses trigonometric rotation terms, writes rotated Mat34 rows back into the supplied transform, and clears the pointed source flag. It is called by CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0. Static retail evidence only; exact class ownership/layout, target semantics, runtime rumble behavior, BEA patching, and rebuild parity remain unproven."
        ),
        new Target(
            "0x00497130",
            "CDestructableSegmentsMotionController__DestructorThunk_00497130",
            "void __fastcall CDestructableSegmentsMotionController__DestructorThunk_00497130(void * this)",
            "Wave942 read-back over Wave431: this entry is a one-instruction JMP thunk to the canonical destructor body at 0x00494cc0. The only observed caller is CMCHiveBoss__ScalarDeletingDestructor, and the target body restores vtable 0x005dc27c before clearing +0x08/+0x0c and tailing into the base motion-controller destructor. Static retail evidence only; exact class ownership/layout, runtime destruction coverage, BEA patching, and rebuild parity remain unproven."
        ),
        new Target(
            "0x00497140",
            "CDestructableSegmentsMotionController__CacheNamedCollisionCylinders",
            "void __thiscall CDestructableSegmentsMotionController__CacheNamedCollisionCylinders(void * this, void * mesh_model)",
            "Wave942 comment normalization over Wave431: RET 0x4 proves one mesh_model stack argument after this, not the older two-argument CUnitAI signature. The function walks a mesh/model table with count at +0x15c and pointer table at +0x160, compares part names at +0xdc against N/S/E/W mid/top/bot in/out cylinder tokens, caches matching parts into +0x18..+0x74, and sets +0x14 after caching or on empty input. Xref read-back shows the call at 0x004976f1 inside the recovered CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0 boundary, which then calls CDestructableSegmentsMotionController__ApplyRumbleTransform and tests cached slots. Static retail evidence only; exact layout/source identity, runtime cylinder behavior, BEA patching, and rebuild parity remain unproven."
        )
    };

    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "destructable-segments-motion-review-wave942",
        "wave942-readback-verified",
        "retail-binary-evidence",
        "comment-normalized",
        "comment-hardened",
        "destructable-segments",
        "motion-controller",
        "hiveboss-motion"
    };

    private static class Stats {
        int updated = 0;
        int wouldUpdate = 0;
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

    private Set<String> tagSet(Function fn) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        return existing;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> existing = tagSet(fn);
        for (String tag : TAGS) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Target target) {
        String existing = fn.getComment();
        return existing == null || !existing.equals(target.comment) || !hasAllTags(fn);
    }

    private void verifyReadBack(Target target) throws Exception {
        Function fn = functionAtEntry(target.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + target.address);
        }
        if (!target.name.equals(fn.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + target.address + ": " + fn.getName());
        }
        if (!target.signature.equals(fn.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + target.address + ": " + fn.getSignature());
        }
        if (!target.comment.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + target.address);
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back tag mismatch at " + target.address);
        }
    }

    private void apply(boolean dryRun, Stats stats) throws Exception {
        for (Target target : TARGETS) {
            Function fn = functionAtEntry(target.address);
            if (fn == null) {
                println("MISSING: " + target.address);
                stats.missing++;
                continue;
            }
            if (!target.name.equals(fn.getName())) {
                println("BADNAME: " + target.address + " actual=" + fn.getName() + " expected=" + target.name);
                stats.bad++;
                continue;
            }
            if (!target.signature.equals(fn.getSignature().toString())) {
                println("BADSIGNATURE: " + target.address + " actual=" + fn.getSignature() + " expected=" + target.signature);
                stats.bad++;
                continue;
            }
            if (!needsUpdate(fn, target)) {
                println("SKIP: " + target.address + " already current");
                stats.skipped++;
                continue;
            }
            if (dryRun) {
                println("DRY: " + target.address + " comment/tags would be normalized");
                stats.wouldUpdate++;
                continue;
            }
            fn.setComment(target.comment);
            Set<String> existing = tagSet(fn);
            for (String tag : TAGS) {
                if (!existing.contains(tag)) {
                    fn.addTag(tag);
                }
            }
            verifyReadBack(target);
            println("OK: " + target.address + " comment/tags normalized");
            stats.updated++;
            Thread.sleep(50);
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        apply(dryRun, stats);
        println("SUMMARY updated=" + stats.updated + " would_update=" + stats.wouldUpdate +
            " skipped=" + stats.skipped + " missing=" + stats.missing + " bad=" + stats.bad);
    }
}
