//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMeshLegMotionAnimationWave811 extends GhidraScript {
    private static final String ADDRESS = "0x0049c2d0";
    private static final String NAME = "CMesh__HasLegMotionAnimation";
    private static final String OLD_NAME = "CMeshPart__HasAnimationToken_623074";
    private static final String COMMENT =
        "Wave811 static read-back hardening: cdecl one-argument CMesh predicate that loads the mesh pointer from ESP+4, pushes string token 0x00623074 (LegMotion), calls CMesh__FindAnimationIndexByName, and returns true when the lookup result is not -1. CMeshPart optimization predicates pass part+0x128 before calling this helper, while CMesh__HasSpecialOptimizationConstraints passes its mesh argument directly, so the saved owner is CMesh rather than CMeshPart. Static retail evidence only; exact field +0x128 meaning, concrete CMesh/CMeshPart layouts, runtime mesh optimization behavior, runtime animation behavior, source identity, BEA patching, and rebuild parity remain deferred.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "cmesh-legmotion-animation-wave811",
        "wave811-readback-verified",
        "retail-binary-evidence",
        "renamed",
        "signature-corrected",
        "comment-hardened",
        "raw-commentless-tail",
        "mesh-optimization",
        "legmotion-animation"
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

    private String expectedSignature() {
        return "bool __cdecl " + NAME + "(void * mesh)";
    }

    private boolean hasExpectedSignature(Function fn) {
        return expectedSignature().equals(fn.getSignature().toString());
    }

    private boolean hasExpectedComment(Function fn) {
        return COMMENT.equals(fn.getComment());
    }

    private boolean allowedName(String actual) {
        return NAME.equals(actual) || OLD_NAME.equals(actual);
    }

    private void readBack(Function fn, Stats stats) {
        boolean ok = true;
        if (!NAME.equals(fn.getName())) {
            println("BADNAME: " + ADDRESS + " expected " + NAME + " got " + fn.getName());
            ok = false;
        }
        if (!hasExpectedSignature(fn)) {
            println("BADSIG: " + ADDRESS + " expected " + expectedSignature() + " got " + fn.getSignature());
            ok = false;
        }
        if (!hasExpectedComment(fn)) {
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
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();

        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
            printSummary(stats);
            throw new IllegalStateException("Wave811 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }

        if (!allowedName(fn.getName())) {
            println("BADNAME: " + ADDRESS + " unexpected " + fn.getName());
            stats.bad++;
        }

        boolean needsRename = !NAME.equals(fn.getName());
        boolean signatureMatches = hasExpectedSignature(fn);
        boolean commentMatches = hasExpectedComment(fn);
        boolean tagsMatch = hasAllTags(fn);
        boolean needsSignature = !signatureMatches;
        boolean needsCommentOrTags = !commentMatches || !tagsMatch;

        if (needsRename) {
            stats.wouldRename++;
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (stats.bad == 0 && (needsRename || needsSignature || needsCommentOrTags) && !dryRun) {
            if (needsRename) {
                fn.setName(NAME, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (needsSignature) {
                DataType voidPtr = new PointerDataType(VoidDataType.dataType);
                fn.setCallingConvention("__cdecl");
                fn.setReturnType(BooleanDataType.dataType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    new ParameterImpl("mesh", voidPtr, currentProgram)
                );
            }
            fn.setComment(COMMENT);
            addTags(fn);
            stats.updated++;

            Function readBack = functionAtEntry(ADDRESS);
            if (readBack == null) {
                println("MISSING-READBACK: " + ADDRESS);
                stats.missing++;
            } else {
                readBack(readBack, stats);
                println("OK: " + ADDRESS + " " + readBack.getSignature());
            }
        } else {
            stats.skipped++;
            println((dryRun ? "DRY" : "SKIP") + ": " + ADDRESS + " " + fn.getName() +
                " rename=" + needsRename +
                " signature_matches=" + signatureMatches +
                " comment_matches=" + commentMatches +
                " tags_match=" + tagsMatch);
        }

        printSummary(stats);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave811 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
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
