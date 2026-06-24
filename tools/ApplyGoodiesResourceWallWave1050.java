//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyGoodiesResourceWallWave1050 extends GhidraScript {
    private static final String ADDRESS = "0x0045d7e0";
    private static final String NAME = "CFEPGoodies__Process";
    private static final String SIGNATURE = "void __thiscall CFEPGoodies__Process(void * this, int state)";
    private static final String COMMENT =
        "Wave1050 Goodies resource-wall correction: this is broader than the older cheat-flag-only "
        + "comment. Fresh static read-back shows the body first refreshes g_Cheat_MALLOY and "
        + "g_Cheat_LATETE via IsCheatActive(0/5), then drives the CFEPGoodies process/update loop: "
        + "resource-free and async-load polling through CFEPGoodies__FreeUpGoodyResources and "
        + "CFEPGoodies__LoadingGoodyPoll, image/model easing and mouse pan/scroll state, current grid "
        + "lookup through get_goodie_number, career Goodie state checks with cheat overrides, and the "
        + "FMV Goodie path that stops/starts CFEPCommon video around CFMV__PlayFullscreenWithLoadingGate. "
        + "Static retail Ghidra/source-shape evidence only; runtime Goodies wall/model/video behavior, "
        + "exact CFEPGoodies layout, visual parity, BEA patching, gameplay outcomes, and rebuild parity "
        + "remain separate proof.";
    private static final String[] TAGS = {
        "static-reaudit",
        "goodies-resource-wall-review-wave1050",
        "wave1050-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "frontend-goodies",
        "goodies-process",
        "goodie-resource-wall",
        "goodie-cheat-flags",
        "fmv-goodie-path",
        "source-shape-evidence"
    };

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

    private int missingTagCount(Function fn) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private boolean hasAllTags(Function fn) {
        return missingTagCount(fn) == 0;
    }

    private void verifyReadBack() {
        Function readBack = functionAtEntry(ADDRESS);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!NAME.equals(readBack.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + ADDRESS + ": " + readBack.getName());
        }
        if (!SIGNATURE.equals(readBack.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + ADDRESS + ": " + readBack.getSignature());
        }
        if (!COMMENT.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + ADDRESS);
        }
        if (!hasAllTags(readBack)) {
            throw new IllegalStateException("Read-back tag mismatch at " + ADDRESS);
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyGoodiesResourceWallWave1050 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        try {
            Function fn = functionAtEntry(ADDRESS);
            if (fn == null) {
                println("MISSING: " + ADDRESS);
                stats.missing++;
            } else if (!NAME.equals(fn.getName())) {
                println("BADNAME: " + ADDRESS + " expected=" + NAME + " actual=" + fn.getName());
                stats.bad++;
            } else if (!SIGNATURE.equals(fn.getSignature().toString())) {
                println("BADSIG: " + ADDRESS + " expected=" + SIGNATURE + " actual=" + fn.getSignature());
                stats.bad++;
            } else {
                boolean commentNeedsUpdate = fn.getComment() == null || !COMMENT.equals(fn.getComment());
                int tagsToAdd = missingTagCount(fn);
                if (!commentNeedsUpdate && tagsToAdd == 0) {
                    println("SKIP: " + ADDRESS + " " + NAME);
                    stats.skipped++;
                } else if (dryRun) {
                    println("DRY: " + ADDRESS + " " + NAME
                        + " commentNeedsUpdate=" + commentNeedsUpdate
                        + " tagsToAdd=" + tagsToAdd);
                    stats.skipped++;
                    stats.commentOnlyUpdated++;
                    stats.tagsAdded += tagsToAdd;
                } else {
                    fn.setComment(COMMENT);
                    stats.commentOnlyUpdated++;
                    for (String tag : TAGS) {
                        if (!tagNames(fn).contains(tag)) {
                            fn.addTag(tag);
                            stats.tagsAdded++;
                        }
                    }
                    verifyReadBack();
                    currentProgram.flushEvents();
                    Thread.sleep(50L);
                    println("OK: " + ADDRESS + " " + NAME + " comment/tags");
                    stats.updated++;
                }
            }
        } catch (Exception ex) {
            println("FAIL: " + ADDRESS + " " + ex.getMessage());
            stats.bad++;
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1050 apply encountered missing/bad rows");
        }
    }
}
