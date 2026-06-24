//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyFEPWingmenPageReviewWave1051 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] addTags;
        final String[] removeTags;

        Spec(String address, String name, String signature, String comment, String[] addTags, String[] removeTags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.addTags = addTags;
            this.removeTags = removeTags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int commentUpdated = 0;
        int tagsAdded = 0;
        int tagsRemoved = 0;
        int wouldRemoveTags = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "fepwingmen-page-review-wave1051",
        "wave1051-readback-verified",
        "retail-binary-evidence",
        "frontend-wingmen",
        "page-consolidation"
    };

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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address address = toAddr(addressText);
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private String[] tags(String... extraTags) {
        String[] result = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, result, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, result, COMMON_TAGS.length, extraTags.length);
        return result;
    }

    private int missingTagCount(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private int presentRemoveTagCount(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : tags) {
            if (actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private void verifyReadBack(Spec spec) {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!spec.name.equals(readBack.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!spec.signature.equals(readBack.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (spec.comment != null && !spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actual = tagNames(readBack);
        for (String tag : spec.addTags) {
            if (!actual.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
        for (String tag : spec.removeTags) {
            if (actual.contains(tag)) {
                throw new IllegalStateException("Read-back still has stale tag at " + spec.address + ": " + tag);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (!spec.name.equals(fn.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }
            if (!spec.signature.equals(fn.getSignature().toString())) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
                stats.bad++;
                return;
            }

            boolean commentNeedsUpdate = spec.comment != null && !spec.comment.equals(fn.getComment());
            int tagsToAdd = missingTagCount(fn, spec.addTags);
            int tagsToRemove = presentRemoveTagCount(fn, spec.removeTags);
            if (!commentNeedsUpdate && tagsToAdd == 0 && tagsToRemove == 0) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name
                    + " commentNeedsUpdate=" + commentNeedsUpdate
                    + " tagsToAdd=" + tagsToAdd
                    + " tagsToRemove=" + tagsToRemove);
                stats.skipped++;
                if (commentNeedsUpdate) {
                    stats.commentUpdated++;
                }
                stats.tagsAdded += tagsToAdd;
                stats.wouldRemoveTags += tagsToRemove;
                return;
            }

            if (commentNeedsUpdate) {
                fn.setComment(spec.comment);
                stats.commentUpdated++;
            }
            for (String tag : spec.addTags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                    stats.tagsAdded++;
                }
            }
            for (String tag : spec.removeTags) {
                if (tagNames(fn).contains(tag)) {
                    fn.removeTag(tag);
                    stats.tagsRemoved++;
                }
            }
            verifyReadBack(spec);
            currentProgram.flushEvents();
            Thread.sleep(50L);
            println("OK: " + spec.address + " " + spec.name + " comment/tags");
            stats.updated++;
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + ex.getMessage());
            stats.bad++;
        }
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x00521650",
                "CFEPWingmen__GetWingmenCount",
                "char CFEPWingmen__GetWingmenCount(void)",
                null,
                tags("wingman-count"),
                new String[] {}
            ),
            new Spec(
                "0x005216c0",
                "CFEPWingmen__Init",
                "int __fastcall CFEPWingmen__Init(void * this)",
                null,
                tags("init", "vtable-boundary-closed"),
                new String[] {}
            ),
            new Spec(
                "0x00521a60",
                "CFEPWingmen__Destroy",
                "void __fastcall CFEPWingmen__Destroy(void * this)",
                null,
                tags("frontend-thing-cleanup"),
                new String[] {}
            ),
            new Spec(
                "0x00521ae0",
                "CFEPWingmen__Load",
                "void __thiscall CFEPWingmen__Load(void * this, void * stream)",
                null,
                tags("cdxmembuffer", "record-loader"),
                new String[] {}
            ),
            new Spec(
                "0x00521c80",
                "CFEPWingmen__Update",
                "void __thiscall CFEPWingmen__Update(void * this, int state)",
                "Wave1051 FEPWingmen page correction: vtable 0x005dba10 slot 2 per-frame update increments this+0x14 by _DAT_005d8574, calls CFEPWingmen__UpdateSpinnerTransformAndPulse for each live frontend thing at this+0x08/+0x0c/+0x10, decrements/clamps fade fields this+0x1c and this+0x20 by _DAT_005d85c0, and in dev-mode/state-zero flow dispatches vtable slot +0x0c. Wave1045 recovered that slot target as 0x00521d20 CFEPWingmen__ButtonPressed, so the older missing-boundary-deferred wording/tag is closed. FEPWingmen.cpp source is absent from references/Onslaught; runtime Wingmen UI behavior, exact layout, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
                tags("per-frame-update", "devmode", "vtable-boundary-closed"),
                new String[] {"missing-boundary-deferred"}
            ),
            new Spec(
                "0x00521d20",
                "CFEPWingmen__ButtonPressed",
                "void __thiscall CFEPWingmen__ButtonPressed(void * this, int button, float val)",
                null,
                tags("button", "vtable-boundary-closed"),
                new String[] {}
            ),
            new Spec(
                "0x00522160",
                "CFEPWingmen__RenderPreCommon",
                "void __stdcall CFEPWingmen__RenderPreCommon(float transition, int dest)",
                null,
                tags("render-pre-common", "vtable-boundary-closed"),
                new String[] {}
            ),
            new Spec(
                "0x00522190",
                "CFEPWingmen__Render",
                "void __thiscall CFEPWingmen__Render(void * this, float transition, int dest)",
                null,
                tags("render", "vtable-boundary-closed"),
                new String[] {}
            ),
            new Spec(
                "0x005230c0",
                "CFEPWingmen__TransitionNotification",
                "void __thiscall CFEPWingmen__TransitionNotification(void * this, int from_page)",
                null,
                tags("transition-notification"),
                new String[] {}
            ),
            new Spec(
                "0x005230e0",
                "CFEPWingmen__FindCurrentLevelRecord",
                "void * __thiscall CFEPWingmen__FindCurrentLevelRecord(void * this)",
                "Wave1051 FEPWingmen page normalization: this remains the Wave566 owner-corrected current-level-record helper, but the older deferred-callsite framing is superseded by Wave1045. Recovered CFEPWingmen__ButtonPressed and CFEPWingmen__Render callsites now load ECX with &DAT_0089da44, call this helper, then read returned record fields at +0x04/+0x08/+0x0c. The body seeds cursor this+0x30 from list head this+0x28, follows node+0x04 links, and returns the first record whose id dword matches DAT_0089d94c or null. This aligns with CFEPWingmen__Load appending 0x24-byte records to this+0x28. Static retail Ghidra evidence only; exact record field names, runtime Wingmen menu behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
                tags("current-level-record", "vtable-boundary-closed"),
                new String[] {}
            ),
            new Spec(
                "0x0046baf0",
                "CFEPWingmen__UpdateSpinnerTransformAndPulse",
                "void __thiscall CFEPWingmen__UpdateSpinnerTransformAndPulse(void * this)",
                null,
                tags("shared-frontend-spinner", "transform"),
                new String[] {}
            ),
        };
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyFEPWingmenPageReviewWave1051 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " comment_updated=" + stats.commentUpdated
            + " tags_added=" + stats.tagsAdded
            + " tags_removed=" + stats.tagsRemoved
            + " would_remove_tags=" + stats.wouldRemoveTags
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1051 apply encountered missing/bad rows");
        }
    }
}
