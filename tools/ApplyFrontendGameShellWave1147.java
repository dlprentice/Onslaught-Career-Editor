//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyFrontendGameShellWave1147 extends GhidraScript {
    private static final String ADDRESS = "0x00456830";
    private static final String NAME = "GlobalListNode__ClearField4AndPushGlobalList";
    private static final String SIGNATURE =
        "void * __thiscall GlobalListNode__ClearField4AndPushGlobalList(void * this)";
    private static final String COMMENT =
        "Wave1147 static read-back correction: shared constructor-style callback referenced by " +
        "CFEPDebriefing initialization, OID creation, and equipment construction paths. The body " +
        "clears field +0x4, calls the Wave822-corrected global effect/owner-link head helper " +
        "ParticleEffectLink__PushGlobalList at 0x004cb040, and returns this. This supersedes the " +
        "older CWorldPhysicsManager-only callee wording, which is too narrow for the current saved " +
        "callee identity. Static callback evidence only; concrete object layout, runtime allocation " +
        "behavior, runtime frontend/game behavior, BEA patching, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "wave1147-frontend-game-shell-score20-current-risk-review",
        "wave1147-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "global-list",
        "particle-effect-link-callee"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;
        int commentOnlyUpdated = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> names = tagNames(fn);
        for (String tag : TAGS) {
            if (!names.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean signatureMatches(Function fn) {
        return SIGNATURE.equals(fn.getSignature().toString());
    }

    private boolean needsUpdate(Function fn) {
        return !COMMENT.equals(fn.getComment()) || !hasAllTags(fn);
    }

    private void verifyReadBack() {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!NAME.equals(fn.getName())) {
            throw new IllegalStateException("Read-back name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn)) {
            throw new IllegalStateException("Read-back signature mismatch: " + fn.getSignature());
        }
        if (!COMMENT.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch");
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back tag mismatch");
        }
    }

    private void apply(boolean dryRun, Stats stats) {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            stats.missing++;
            println("MISSING: " + ADDRESS);
            return;
        }
        if (!NAME.equals(fn.getName())) {
            stats.bad++;
            println("BADNAME: " + ADDRESS + " actual=" + fn.getName() + " expected=" + NAME);
            return;
        }
        if (!signatureMatches(fn)) {
            stats.bad++;
            println("BADSIG: " + ADDRESS + " actual=" + fn.getSignature() + " expected=" + SIGNATURE);
            return;
        }
        if (!needsUpdate(fn)) {
            stats.skipped++;
            println("SKIP: " + ADDRESS + " " + NAME);
            return;
        }
        if (dryRun) {
            stats.skipped++;
            stats.commentOnlyUpdated++;
            println("DRY: " + ADDRESS + " " + NAME);
            return;
        }
        fn.setComment(COMMENT);
        for (String tag : TAGS) {
            fn.addTag(tag);
        }
        verifyReadBack();
        stats.updated++;
        stats.commentOnlyUpdated++;
        println("OK: " + ADDRESS + " " + NAME);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);
        println("ApplyFrontendGameShellWave1147 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        apply(dryRun, stats);
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1147 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
