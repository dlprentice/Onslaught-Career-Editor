//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMCMechBoneRecursiveWave810 extends GhidraScript {
    private static final String ADDRESS = "0x0049bd50";
    private static final String NAME = "CMCMech__UpdateBoneHierarchyRecursive";
    private static final String SIGNATURE = "void CMCMech__UpdateBoneHierarchyRecursive(void)";
    private static final String COMMENT =
        "Wave810 static read-back hardening: comment/tag-only because the retail body uses a 0x54-byte cleaned stack contract with by-value vector/matrix payload that is safer to keep out of Ghidra's normal parameter model until shared FVector/FMatrix stack-aggregate types are recovered. ECX is the CMCMech receiver. CMCMech__Reset callsites 0x00498ac6 and 0x00498bad, plus recursive callsite 0x0049bddf, pass a 0x10-byte vector payload, a 0x30-byte matrix payload copied with MOVSD.REP ECX=0xc, child mesh_part from parent mesh_part+0x94[index], two pose-argument dwords, and blend floats. The body first calls CMCMech__UpdateBone(this, position, matrix, mesh_part, pose_arg_a, pose_arg_b, blend_a, blend_b), then iterates child count at mesh_part+0x90 and recursively descends child table at mesh_part+0x94. Static retail evidence only; exact by-value FVector/FMatrix type contract, concrete CMCMech/CMeshPart layouts, source identity, runtime leg/bone animation behavior, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "cmcmech-bone-recursive-wave810",
        "wave810-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "large-stack-argument-contract",
        "by-value-stack-payload",
        "recursive-bone-update",
        "raw-commentless-tail",
        "tranche-head"
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> actual = tagNames(fn);
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void addTags(Function fn) {
        for (String tag : TAGS) {
            fn.addTag(tag);
        }
    }

    private boolean hasComment(Function fn) {
        String current = fn.getComment();
        return current != null && current.equals(COMMENT);
    }

    private boolean hasExpectedSignature(Function fn) {
        return fn.getSignature().toString().equals(SIGNATURE);
    }

    private boolean readBack(Function fn, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " expected " + NAME + " got " + fn.getName());
            ok = false;
        }
        if (!hasExpectedSignature(fn)) {
            println("BADSIG: " + ADDRESS + " expected " + SIGNATURE + " got " + fn.getSignature());
            ok = false;
        }
        if (!hasComment(fn)) {
            println("BADCOMMENT: " + ADDRESS);
            ok = false;
        }
        if (!hasAllTags(fn)) {
            println("BADTAGS: " + ADDRESS);
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
        String mode = args != null && args.length > 0 ? args[0] : "dry";
        boolean dryRun = isDryRun(mode);
        Stats stats = new Stats();

        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
            printSummary(stats);
            return;
        }

        boolean commentMatches = hasComment(fn);
        boolean tagsMatch = hasAllTags(fn);
        boolean signatureMatches = hasExpectedSignature(fn);
        boolean needsCommentOrTags = !commentMatches || !tagsMatch;
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!fn.getName().equals(NAME)) {
            println("BADNAME: " + ADDRESS + " expected " + NAME + " got " + fn.getName());
            stats.bad++;
        }
        if (!signatureMatches) {
            println("BADSIG: " + ADDRESS + " expected " + SIGNATURE + " got " + fn.getSignature());
            stats.bad++;
        }

        if (stats.bad == 0 && needsCommentOrTags && !dryRun) {
            fn.setComment(COMMENT);
            addTags(fn);
            stats.updated++;
            if (readBack(fn, stats)) {
                println("OK: " + ADDRESS + " " + NAME + " comment/tags saved");
            }
        } else {
            stats.skipped++;
            println((dryRun ? "DRY" : "SKIP") + ": " + ADDRESS + " " + NAME +
                " comment_matches=" + commentMatches + " tags_match=" + tagsMatch +
                " signature_matches=" + signatureMatches);
        }

        printSummary(stats);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave810 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }

    private void printSummary(Stats stats) {
        println("SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
