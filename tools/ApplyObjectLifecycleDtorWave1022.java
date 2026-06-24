//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyObjectLifecycleDtorWave1022 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(spec.signature);
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
            ok = false;
        }
        if (!signatureMatches(fn, spec)) {
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

        boolean oldOrNewName = fn.getName().equals(spec.oldName) || fn.getName().equals(spec.name);
        if (!oldOrNewName) {
            println("BADNAME: " + spec.address + " expected_old_or_new=" + spec.oldName + "/" + spec.name + " actual=" + fn.getName());
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        boolean needsComment = !spec.comment.equals(fn.getComment());
        int tagsToAdd = missingTagCount(fn, spec);
        boolean needsUpdate = needsRename || needsComment || tagsToAdd != 0;
        if (!needsUpdate) {
            if (!signatureMatches(fn, spec)) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
                stats.bad++;
                return;
            }
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=" + needsRename
                + " needsComment=" + needsComment
                + " tagsToAdd=" + tagsToAdd);
            if (needsRename) {
                stats.wouldRename++;
            }
            if (needsComment && !needsRename) {
                stats.commentOnlyUpdated++;
            }
            stats.tagsAdded += tagsToAdd;
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsComment) {
            fn.setComment(spec.comment);
            if (!needsRename) {
                stats.commentOnlyUpdated++;
            }
        }
        Set<String> actualTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                fn.addTag(tag);
                stats.tagsAdded++;
            }
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.name);
            stats.updated++;
        }
        currentProgram.flushEvents();
        Thread.sleep(50L);
    }

    private String[] tags(String... extra) {
        String[] base = new String[] {
            "static-reaudit",
            "object-lifecycle-dtor-review-wave1022",
            "wave1022-readback-verified",
            "retail-binary-evidence",
            "owner-prefix-normalized",
            "dtor-chain"
        };
        String[] result = new String[base.length + extra.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extra, 0, result, base.length, extra.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyObjectLifecycleDtorWave1022 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bfd80",
                "CSpawnerThing__scalar_deleting_dtor",
                "CSpawnerThng__scalar_deleting_dtor",
                "void * __thiscall CSpawnerThng__scalar_deleting_dtor(void * this, byte flags)",
                "Wave1022 owner-prefix normalization: scalar-deleting destructor wrapper for the SpawnerThng vtable at 0x005dd16c slot 1. The wrapper calls CSpawnerThng__dtor_base, optionally frees this through CDXMemoryManager__Free when flags&1 is set, returns this, and ends with RET 0x4. Slots 2 and 9 in the same table already point to CSpawnerThng__Shutdown and CSpawnerThng__Init, so the old CSpawnerThing prefix was stale spelling. Static retail Ghidra evidence only; runtime spawner cleanup behavior, concrete layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.",
                tags("scalar-deleting-dtor")
            ),
            new Spec(
                "0x004bfed0",
                "CSpawnerThing__dtor_base",
                "CSpawnerThng__dtor_base",
                "void __fastcall CSpawnerThng__dtor_base(void * this)",
                "Wave1022 owner-prefix normalization: destructor-base body called by CSpawnerThng__scalar_deleting_dtor. If the owner/list link at +0x7c is populated, the body removes that link through CSPtrSet__Remove, then delegates to CComplexThing__dtor_base. Vtable evidence at 0x005dd16c keeps this in the same SpawnerThng family as CSpawnerThng__Shutdown and CSpawnerThng__Init; the older CSpawnerThing prefix was stale spelling. Static retail Ghidra evidence only; runtime spawner cleanup behavior, concrete layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.",
                tags("dtor-base", "spawnerthng")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1022 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
