//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyComponentScalarFlagApplyReviewWave1039 extends GhidraScript {
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

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (!spec.comment.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (missingTagCount(fn, spec) != 0) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
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

            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            int tagsToAdd = missingTagCount(fn, spec);
            if (!commentNeedsUpdate && tagsToAdd == 0) {
                println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + spec.name + " already matched");
                stats.skipped++;
                return;
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name
                    + " commentNeedsUpdate=" + commentNeedsUpdate
                    + " tagsToAdd=" + tagsToAdd);
                stats.skipped++;
                if (commentNeedsUpdate) {
                    stats.commentOnlyUpdated++;
                }
                stats.tagsAdded += tagsToAdd;
                return;
            }

            if (commentNeedsUpdate) {
                fn.setComment(spec.comment);
                stats.commentOnlyUpdated++;
            }
            Set<String> actualTags = tagNames(fn);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    fn.addTag(tag);
                    stats.tagsAdded++;
                }
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name);
            stats.updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            stats.bad++;
        }
    }

    private String[] tags(String kind) {
        return new String[] {
            "static-reaudit",
            "component-scalar-flag-apply-review-wave1039",
            "wave1039-readback-verified",
            "retail-binary-evidence",
            "physics-script",
            "physics-script-wave343",
            "component-value-tranche",
            "component-apply",
            "function-boundary",
            kind,
            "comment-hardened",
            "wave343-normalized"
        };
    }

    private Spec scalar(String address, String name, String offset) {
        return new Spec(
            address,
            name,
            "void __thiscall " + name + "(void * this, char * componentName)",
            "Wave1039 static re-audit: searches DAT_00855400 by componentName and writes the raw "
                + "scalar value at this+0x8 to the matched component record+" + offset + ". Fresh "
                + "metadata/tag/xref/instruction/decompile evidence preserved the Wave343 name and "
                + "signature. Exact field semantics, runtime PhysicsScript application behavior, "
                + "source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain "
                + "separate proof.",
            tags("offset-backed-scalar")
        );
    }

    private Spec flag(String address, String name, String offset) {
        return new Spec(
            address,
            name,
            "void __thiscall " + name + "(void * this, char * componentName)",
            "Wave1039 static re-audit correction: searches DAT_00855400 by componentName, compares "
                + "the scalar at this+0x8 with the zero constant at 0x005d856c, and writes the matched "
                + "component record+" + offset + " as 0 on the zero-comparison path and 1 otherwise. "
                + "This replaces the older positive-only wording; exact flag meaning, runtime "
                + "PhysicsScript application behavior, source-body identity, BEA patching, gameplay "
                + "outcomes, and rebuild parity remain separate proof.",
            tags("offset-backed-flag")
        );
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyComponentScalarFlagApplyReviewWave1039 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            scalar("0x0043ca70", "CComponentScalarD8__ApplyToComponentByName", "0xd8"),
            scalar("0x0043cb40", "CComponentScalarDC__ApplyToComponentByName", "0xdc"),
            scalar("0x0043cbe0", "CComponentScalarC0__ApplyToComponentByName", "0xc0"),
            scalar("0x0043cc80", "CComponentScalar158__ApplyToComponentByName", "0x158"),
            scalar("0x0043cd20", "CComponentScalarB8__ApplyToComponentByName", "0xb8"),
            scalar("0x0043cdc0", "CComponentScalarBC__ApplyToComponentByName", "0xbc"),
            scalar("0x0043d460", "CComponentScalar160__ApplyToComponentByName", "0x160"),
            flag("0x0043ce60", "CComponentFlag124__ApplyToComponentByName", "0x124"),
            flag("0x0043cf20", "CComponentFlag128__ApplyToComponentByName", "0x128"),
            flag("0x0043cfe0", "CComponentFlag12C__ApplyToComponentByName", "0x12c"),
            flag("0x0043d0a0", "CComponentFlag198__ApplyToComponentByName", "0x198"),
            flag("0x0043d160", "CComponentFlag114__ApplyToComponentByName", "0x114"),
            flag("0x0043d220", "CComponentFlag19C__ApplyToComponentByName", "0x19c"),
            flag("0x0043d2e0", "CComponentFlag134__ApplyToComponentByName", "0x134"),
            flag("0x0043d3a0", "CComponentFlag108__ApplyToComponentByName", "0x108")
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1039 apply encountered missing/bad rows");
        }
    }
}
