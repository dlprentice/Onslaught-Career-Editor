//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyRoundConfigBridgeWave991 extends GhidraScript {
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyRoundConfigBridgeWave991 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00426150",
                "CCollisionSeekingRound__Init",
                "void __thiscall CCollisionSeekingRound__Init(void * this, void * roundConfig)",
                "Wave991 round configuration bridge normalization: initializes owner/config flags, creates or adopts the primary CLine-style seeker, writes its owner-relative offset after sampling the owning thing center, and conditionally creates a secondary CMeshCollisionVolume-style seeker from collisionseekingthing.cpp line 0x39. Callers CCollisionSeekingRound__InitWithSound and CCollisionSeekingRound__CreateEffect plus the vtable DATA ref at 0x005d9614 anchor this as static retail Ghidra evidence only; runtime projectile behavior, exact source identity, concrete layouts, local variable names, and rebuild parity remain unproven.",
                new String[] {
                    "static-reaudit",
                    "round-config-bridge-review-wave991",
                    "wave991-readback-verified",
                    "retail-binary-evidence",
                    "comment-hardened",
                    "tag-corrected",
                    "xref-verified",
                    "projectile",
                    "collision-seeking",
                    "round-config"
                }
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
            throw new IllegalStateException("Wave991 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
