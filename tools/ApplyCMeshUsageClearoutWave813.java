//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMeshUsageClearoutWave813 extends GhidraScript {
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "cmesh-usage-clearout-wave813",
        "wave813-readback-verified",
        "retail-binary-evidence",
        "signature-verified",
        "comment-hardened",
        "raw-commentless-tail",
        "mesh-resource-lifetime",
        "mesh-usage-markers"
    };

    private static final Target[] TARGETS = new Target[] {
        new Target(
            "0x004a52b0",
            "CMesh__ClearAllUsageMarkers",
            "Wave813 static read-back hardening: clears the usage/ref marker field at +0x170 for every mesh in global mesh list DAT_00704ad8 by following next-link +0x158, then calls CMesh__ClearOut. CLTShell__ShutdownRuntimeAndReleaseResources calls this at 0x004f01c4 after calling CMesh__ClearOut at 0x004f01bf. Static retail Ghidra evidence only; exact CMesh list layout, runtime shutdown ordering, BEA patching, and rebuild parity remain deferred."
        ),
        new Target(
            "0x004a52d0",
            "CMesh__ClearOut",
            "Wave813 static read-back hardening: releases default embedded mesh resource DAT_00704adc through CMesh__ReleaseEmbeddedResources and CDXMemoryManager__Free, then repeatedly scans global mesh list DAT_00704ad8 for entries with usage/ref marker +0x170 equal to zero, freeing each through CMesh__FreeResourcesAndUnlink and CDXMemoryManager__Free. It emits DebugTrace no-leak or leak-report strings and formats leaked mesh names/refcounts with string 0x0062f938. Called by CLTShell__ShutdownRuntimeAndReleaseResources and by CMesh__ClearAllUsageMarkers. Static retail Ghidra evidence only; exact CMesh list/resource layout, runtime leak behavior, BEA patching, and rebuild parity remain deferred."
        ),
        new Target(
            "0x004a53f0",
            "CMesh__StatusLoadingMeshResources",
            "Wave813 static read-back hardening: formats the loading-status string at 0x0062f9a0 (Loading mesh resources), sends it to global console/status object DAT_00663498 through CConsole__Status, then completes it through CConsole__StatusDone with success byte 1. Called from CFrontEnd__LoadSharedResources at 0x00468809 and CGame__LoadResources at 0x0046cdba. Static retail Ghidra evidence only; exact frontend/game loading UI behavior, BEA patching, and rebuild parity remain deferred."
        ),
        new Target(
            "0x004a5430",
            "CMesh__FreeUnusedAndReportLeaks",
            "Wave813 static read-back hardening: resets global mesh leak/report counter DAT_00704ae0, repeatedly frees global mesh-list entries whose usage/ref marker +0x170 is zero via CMesh__FreeResourcesAndUnlink and CDXMemoryManager__Free, then emits end-of-level mesh leak header/footer strings and formats remaining leaked mesh names/refcounts with string 0x0062f938. Called from CFrontEnd__ReleaseParticleHudWaypointResources at 0x0046928d and from raw callsite 0x0046ca13 that Ghidra does not currently attach to a function. Static retail Ghidra evidence only; exact CMesh list/resource layout, runtime end-of-level leak behavior, BEA patching, and rebuild parity remain deferred."
        )
    };

    private static class Target {
        final String address;
        final String name;
        final String comment;

        Target(String address, String name, String comment) {
            this.address = address;
            this.name = name;
            this.comment = comment;
        }

        String expectedSignature() {
            return "void __cdecl " + name + "(void)";
        }
    }

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

    private boolean hasExpectedSignature(Target target, Function fn) {
        return target.expectedSignature().equals(fn.getSignature().toString());
    }

    private void readBack(Target target, Function fn, Stats stats) {
        boolean ok = true;
        if (!target.name.equals(fn.getName())) {
            println("BADNAME: " + target.address + " expected " + target.name + " got " + fn.getName());
            ok = false;
        }
        if (!hasExpectedSignature(target, fn)) {
            println("BADSIG: " + target.address + " expected " + target.expectedSignature() + " got " + fn.getSignature());
            ok = false;
        }
        if (!target.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + target.address);
            ok = false;
        }
        if (!hasAllTags(fn)) {
            println("BADTAGS: " + target.address);
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

        for (Target target : TARGETS) {
            Function fn = functionAtEntry(target.address);
            if (fn == null) {
                println("MISSING: " + target.address);
                stats.missing++;
                continue;
            }
            if (!target.name.equals(fn.getName())) {
                println("BADNAME: " + target.address + " unexpected " + fn.getName());
                stats.bad++;
                continue;
            }

            boolean signatureMatches = hasExpectedSignature(target, fn);
            boolean commentMatches = target.comment.equals(fn.getComment());
            boolean tagsMatch = hasAllTags(fn);
            boolean needsSignature = !signatureMatches;
            boolean needsCommentOrTags = !commentMatches || !tagsMatch;

            if (needsSignature) {
                stats.signatureUpdated++;
            }
            if (needsCommentOrTags) {
                stats.commentOnlyUpdated++;
            }

            if ((needsSignature || needsCommentOrTags) && !dryRun) {
                if (needsSignature) {
                    fn.setCallingConvention("__cdecl");
                    fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
                    fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED);
                }
                fn.setComment(target.comment);
                addTags(fn);
                stats.updated++;

                Function readBack = functionAtEntry(target.address);
                if (readBack == null) {
                    println("MISSING-READBACK: " + target.address);
                    stats.missing++;
                } else {
                    readBack(target, readBack, stats);
                    println("OK: " + target.address + " " + readBack.getSignature());
                }
            } else {
                stats.skipped++;
                println((dryRun ? "DRY" : "SKIP") + ": " + target.address + " " + fn.getName() +
                    " signature_matches=" + signatureMatches +
                    " comment_matches=" + commentMatches +
                    " tags_match=" + tagsMatch);
            }
        }

        printSummary(stats);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave813 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
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
