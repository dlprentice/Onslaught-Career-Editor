//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyPhysicsWeaponModeRoundTailWave987 extends GhidraScript {
    private static final String ADDRESS = "0x004359c0";
    private static final String EXPECTED_NAME = "CPhysicsWeaponModeValue__dtor_base";
    private static final String EXPECTED_SIGNATURE =
        "void __fastcall CPhysicsWeaponModeValue__dtor_base(void * this)";
    private static final String STALE_TAG = "constructor";
    private static final String[] REQUIRED_TAGS = {
        "destructor",
        "physics-script",
        "physics-script-wave337",
        "supersedes-wave336-ctor-label",
        "physics-weaponmode-round-tail-review-wave987",
        "wave987-readback-verified",
        "tag-corrected"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int tagRemoved = 0;
        int wouldRemoveTag = 0;
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

    private boolean hasAllRequiredTags(Set<String> tags) {
        for (String tag : REQUIRED_TAGS) {
            if (!tags.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private int missingRequiredTagCount(Set<String> tags) {
        int count = 0;
        for (String tag : REQUIRED_TAGS) {
            if (!tags.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private boolean signatureMatches(Function fn) {
        return fn.getSignature().toString().equals(EXPECTED_SIGNATURE);
    }

    private boolean verifyReadBack(Function fn, Stats stats) {
        boolean ok = true;
        Set<String> tags = tagNames(fn);
        if (!EXPECTED_NAME.equals(fn.getName())) {
            println("BADNAME: " + ADDRESS + " expected=" + EXPECTED_NAME + " actual=" + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn)) {
            println("BADSIG: " + ADDRESS + " expected=" + EXPECTED_SIGNATURE + " actual=" + fn.getSignature());
            ok = false;
        }
        if (tags.contains(STALE_TAG)) {
            println("BADTAG: " + ADDRESS + " stale tag still present: " + STALE_TAG);
            ok = false;
        }
        if (!hasAllRequiredTags(tags)) {
            println("BADTAGS: " + ADDRESS + " missing required Wave987/read-back tags");
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyPhysicsWeaponModeRoundTailWave987 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
        } else if (!EXPECTED_NAME.equals(fn.getName())) {
            println("BADNAME: " + ADDRESS + " expected=" + EXPECTED_NAME + " actual=" + fn.getName());
            stats.bad++;
        } else if (!signatureMatches(fn)) {
            println("BADSIG: " + ADDRESS + " expected=" + EXPECTED_SIGNATURE + " actual=" + fn.getSignature());
            stats.bad++;
        } else {
            Set<String> tags = tagNames(fn);
            boolean removeNeeded = tags.contains(STALE_TAG);
            int tagsToAdd = missingRequiredTagCount(tags);
            if (!removeNeeded && tagsToAdd == 0) {
                println((dryRun ? "DRY" : "SKIP") + ": " + ADDRESS + " tags already matched");
                stats.skipped++;
            } else if (dryRun) {
                println("DRY: " + ADDRESS + " removeTag=" + removeNeeded + " tagsToAdd=" + tagsToAdd);
                if (removeNeeded) {
                    stats.wouldRemoveTag++;
                }
                stats.tagsAdded += tagsToAdd;
                stats.skipped++;
            } else {
                if (removeNeeded) {
                    fn.removeTag(STALE_TAG);
                    stats.tagRemoved++;
                }
                for (String tag : REQUIRED_TAGS) {
                    if (!tagNames(fn).contains(tag)) {
                        fn.addTag(tag);
                        stats.tagsAdded++;
                    }
                }
                if (verifyReadBack(fn, stats)) {
                    println("APPLY_OK: " + ADDRESS + " removedStaleConstructor=" + removeNeeded + " tagsAdded=" + stats.tagsAdded);
                }
                stats.updated++;
                currentProgram.flushEvents();
                Thread.sleep(50L);
            }
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " tag_removed=" + stats.tagRemoved
            + " would_remove_tag=" + stats.wouldRemoveTag
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave987 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
