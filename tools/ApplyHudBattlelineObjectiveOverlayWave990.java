//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyHudBattlelineObjectiveOverlayWave990 extends GhidraScript {
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
        println("ApplyHudBattlelineObjectiveOverlayWave990 mode=" + (dryRun ? "dry" : "apply"));

        String[] sharedTags = new String[] {
            "static-reaudit",
            "hud-battleline-objective-overlay-review-wave990",
            "wave990-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "xref-verified"
        };

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0040dda0",
                "CUnitAI__RefreshGridCooldownFromOccupiedCells",
                "void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)",
                "Wave990 HUD objective-panel normalization: this CUnitAI cooldown helper is called by CHud__RenderObjectiveStatusPanel at 0x004862af, gates on DAT_00672fd0 minus a threshold, checks the object vfunc at +0x10c, samples two CFearGrid__GetOccupancyAtWorldVector globals (DAT_008a9d7c and DAT_008a9d80) at the current world vector, and refreshes this+0x2e8 when either occupancy grid is active. Static retail Ghidra evidence only; owner, exact source identity, concrete layout, runtime HUD/objective behavior, and rebuild parity remain unproven.",
                concat(sharedTags, new String[] {
                    "hud-objective-panel",
                    "fear-grid",
                    "cooldown-refresh"
                })
            ),
            new Spec(
                "0x00414cb0",
                "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices",
                "void __thiscall CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices(void * this)",
                "Wave990 HUD battleline normalization: CDXBattleLine overlay helper called by CHud__RenderBattleline at 0x00488071. The body resets vertex count +0x60, walks battle-line list DAT_00855140 and influence/deferred list DAT_008550a0, filters the latter through SharedState__IsTimer88PendingAndState7CZero at 0x00414d1c, and appends yellow/red overlay vertices through CDXBattleLine__AppendOverlayVertex. Static retail Ghidra evidence only; exact list ownership, source identity, runtime rendering behavior, and rebuild parity remain unproven.",
                concat(sharedTags, new String[] {
                    "hud-battleline",
                    "battleline",
                    "influence-overlay",
                    "dynamic-overlay-vertices"
                })
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
            throw new IllegalStateException("Wave990 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }

    private static String[] concat(String[] first, String[] second) {
        String[] result = new String[first.length + second.length];
        System.arraycopy(first, 0, result, 0, first.length);
        System.arraycopy(second, 0, result, first.length, second.length);
        return result;
    }
}
