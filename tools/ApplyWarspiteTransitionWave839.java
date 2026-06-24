//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyWarspiteTransitionWave839 extends GhidraScript {
    private static final String ADDRESS = "0x004fde70";
    private static final String NAME = "CWarspite__TransitionToUndeploying";
    private static final String SIGNATURE = "void __thiscall CWarspite__TransitionToUndeploying(void * this)";
    private static final String COMMENT =
        "Wave839 static read-back/comment hardening: CWarspite transition helper that only acts when state field this+0x244 equals 4. In that path it writes state 5 to this+0x244, asks the owner/unit pointer at this+0x30 through vfunc +0x24 for the undeploying animation resource (string s_undeploying_006239d8, args 1 and 0), calls CMesh__FindAnimationIndexByName, and dispatches this vfunc +0xf0 with the resolved animation index; otherwise it returns without changing state. Xrefs include 0x004ff2ae in CWarspite__Update plus raw controller/AI callsites 0x00416870, 0x0044655f, 0x00446671, 0x0044671a, and 0x00534f99. Static retail Ghidra evidence only; exact Warspite state enum names, concrete owner/unit animation-resource type, runtime AI/animation behavior, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "warspite-transition-wave839",
        "wave839-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "cwarspite",
        "warspite",
        "state-machine",
        "animation-transition",
        "undeploying"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private boolean hasTags(Function fn) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean alreadyApplied(Function fn) {
        String comment = fn.getComment();
        return fn.getName().equals(NAME)
            && fn.getSignature().toString().equals(SIGNATURE)
            && COMMENT.equals(comment)
            && hasTags(fn);
    }

    private void apply(boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS + " " + NAME);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " " + fn.getName() + " expected " + NAME);
            stats.bad++;
            return;
        }
        if (!fn.getSignature().toString().equals(SIGNATURE)) {
            println("BADSIG: " + ADDRESS + " " + fn.getSignature().toString() + " expected " + SIGNATURE);
            stats.bad++;
            return;
        }

        boolean needsComment = !COMMENT.equals(fn.getComment());
        boolean needsTags = !hasTags(fn);
        if (!needsComment && !needsTags) {
            println("SKIP: " + ADDRESS + " " + NAME + " already current");
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + ADDRESS + " " + NAME + " comment=" + needsComment + " tags=" + needsTags);
            stats.skipped++;
            if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (needsComment) {
            fn.setComment(COMMENT);
        }
        for (String tag : TAGS) {
            fn.addTag(tag);
        }

        Function readback = functionAtEntry(ADDRESS);
        if (readback == null || !alreadyApplied(readback)) {
            println("READBACK_BAD: " + ADDRESS);
            stats.bad++;
            return;
        }

        println("READBACK_OK: " + ADDRESS + " " + NAME + " " + readback.getSignature().toString());
        stats.updated++;
        stats.commentOnlyUpdated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        apply(dryRun, stats);

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
