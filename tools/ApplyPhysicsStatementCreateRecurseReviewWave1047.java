//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyPhysicsStatementCreateRecurseReviewWave1047 extends GhidraScript {
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

            boolean commentNeedsUpdate = !spec.comment.equals(fn.getComment());
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

    private String sigFast(String name) {
        return "void __fastcall " + name + "(void * this)";
    }

    private String[] tags(String sourceWave) {
        return new String[] {
            "static-reaudit",
            "physics-statement-create-recurse-review-wave1047",
            "wave1047-readback-verified",
            "retail-binary-evidence",
            "physics-script",
            sourceWave,
            "statement-tranche",
            "statement-create-recurse",
            "comment-corrected"
        };
    }

    private Spec unitSpec() {
        String name = "CUnitStatement__CreateUnitAndRecurse";
        return new Spec(
            "0x0042ede0",
            name,
            sigFast(name),
            "Wave1047 static re-audit correction: CUnitStatement vtable slot +0x4 body from DATA xref 0x005d987c. It creates/registers UnitAI by statement name through CUnitAI__CreateAndRegisterByName, resolves the matching UnitAI record from DAT_008553fc by name, then passes that resolved UnitAI context through child statement slot +0x4 and CStatementChain__InvokeVFunc04OnNodes. Exact statement/value-list layout, UnitAI record layout, runtime physics behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            tags("physics-script-wave331")
        );
    }

    private Spec nameContextSpec(String address, String name, String sourceWave, String dataXref, String createCall, String recordKind) {
        return new Spec(
            address,
            name,
            sigFast(name),
            "Wave1047 static re-audit correction: " + recordKind + " vtable slot +0x4 body from DATA xref " + dataXref
                + ". It calls " + createCall
                + " with the statement name, then passes the statement name/string context, not a returned registry object, through child statement slot +0x4 and CStatementChain__InvokeVFunc04OnNodes. Exact statement/value-list layout, registry record layout, runtime physics behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            tags(sourceWave)
        );
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyPhysicsStatementCreateRecurseReviewWave1047 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            unitSpec(),
            nameContextSpec("0x0042f5b0", "CWeaponStatement__CreateWeaponAndRecurse", "physics-script-wave331", "0x005d9854", "CWeaponStatement__Create", "CWeaponStatement"),
            nameContextSpec("0x0042fa40", "CWeaponModeStatement__CreateWeaponModeAndRecurse", "physics-script-wave331", "0x005d9868", "CWeaponModeStatement__Create", "CWeaponModeStatement"),
            nameContextSpec("0x0042ff60", "CRoundStatement__CreateRoundAndRecurse", "physics-script-wave331", "0x005d9840", "CRoundStatement__Create", "CRoundStatement"),
            nameContextSpec("0x004304d0", "CSpawnerStatement__CreateSpawnerAndRecurse", "physics-script-wave332", "0x005d982c", "CSpawnerData__CreateAndRegisterByName", "CSpawnerStatement"),
            nameContextSpec("0x004309a0", "CExplosionStatement__CreateExplosionAndRecurse", "physics-script-wave332", "0x005d9818", "CExplosionStatement__Create", "CExplosionStatement"),
            nameContextSpec("0x00430e20", "CComponentStatement__CreateComponentAndRecurse", "physics-script-wave332", "0x005d9804", "CComponentStatement__CreateAndRegisterByName", "CComponentStatement"),
            nameContextSpec("0x00431310", "CFeatureStatement__CreateFeatureAndRecurse", "physics-script-wave333", "0x005d97f0", "CFeatureStatement__CreateAndRegisterByName", "CFeatureStatement"),
            nameContextSpec("0x00431760", "CHazardStatement__CreateHazardAndRecurse", "physics-script-wave333", "0x005d97dc", "CHazardStatement__CreateAndRegisterByName", "CHazardStatement")
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
            throw new IllegalStateException("Wave1047 apply encountered missing/bad rows");
        }
    }
}
