//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyPhysicsStatementCreateSizeReviewWave1040 extends GhidraScript {
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
        if (spec.comment != null && !spec.comment.equals(fn.getComment())) {
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

            boolean commentNeedsUpdate = spec.comment != null && !spec.comment.equals(fn.getComment());
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

    private String sigFastInt(String name) {
        return "int __fastcall " + name + "(void * this)";
    }

    private String sigDtor(String name) {
        return "void * __thiscall " + name + "(void * this, int flags)";
    }

    private String[] tags(String kind) {
        return new String[] {
            "static-reaudit",
            "physics-statement-create-size-review-wave1040",
            "wave1040-readback-verified",
            "retail-binary-evidence",
            "physics-script",
            "physics-script-wave331",
            "statement-tranche",
            "statement-create-size",
            kind
        };
    }

    private String[] dtorTags(String sourceWave) {
        return new String[] {
            "static-reaudit",
            "physics-statement-create-size-review-wave1040",
            "wave1040-readback-verified",
            "retail-binary-evidence",
            "physics-script",
            sourceWave,
            "statement-tranche",
            "value-list",
            "destructor",
            "comment-corrected",
            "memory-manager-free"
        };
    }

    private Spec reviewed(String address, String name, String signature, String kind) {
        return new Spec(address, name, signature, null, tags(kind));
    }

    private Spec dtor(String address, String name, String vtable, String sourceWave) {
        return new Spec(
            address,
            name,
            sigDtor(name),
            "Wave1040 static re-audit correction: scalar-deleting destructor wrapper for "
                + name.replace("__scalar_deleting_dtor", "")
                + " nodes. It restores vtable " + vtable + ", destroys child at +0x4 and "
                + "next-node at +0x8 through vtable slot 0 when present, tests the scalar-delete "
                + "flag, and frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) via "
                + "call 0x00549220, not OID__FreeObject. Exact class layout, runtime lifetime "
                + "behavior, exact source-body identity, BEA patching, gameplay outcomes, and "
                + "rebuild parity remain separate proof.",
            dtorTags(sourceWave)
        );
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyPhysicsStatementCreateSizeReviewWave1040 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            reviewed("0x0042ede0", "CUnitStatement__CreateUnitAndRecurse", sigFast("CUnitStatement__CreateUnitAndRecurse"), "statement-update"),
            reviewed("0x0042f230", "CUnitStatement__GetSerializedSize", sigFastInt("CUnitStatement__GetSerializedSize"), "serialized-size"),
            reviewed("0x0042f280", "CPhysicsUnitValueList__GetSerializedSize", sigFastInt("CPhysicsUnitValueList__GetSerializedSize"), "serialized-size"),
            dtor("0x0042f4b0", "CPhysicsUnitValueList__scalar_deleting_dtor", "0x005d988c", "physics-script-wave331"),
            reviewed("0x0042f5b0", "CWeaponStatement__CreateWeaponAndRecurse", sigFast("CWeaponStatement__CreateWeaponAndRecurse"), "statement-update"),
            reviewed("0x0042f700", "CWeaponStatement__GetSerializedSize", sigFastInt("CWeaponStatement__GetSerializedSize"), "serialized-size"),
            reviewed("0x0042f750", "CPhysicsWeaponValueList__GetSerializedSize", sigFastInt("CPhysicsWeaponValueList__GetSerializedSize"), "serialized-size"),
            dtor("0x0042f980", "CPhysicsWeaponValueList__scalar_deleting_dtor", "0x005d98a8", "physics-script-wave331"),
            reviewed("0x0042fa40", "CWeaponModeStatement__CreateWeaponModeAndRecurse", sigFast("CWeaponModeStatement__CreateWeaponModeAndRecurse"), "statement-update"),
            reviewed("0x0042fc20", "CWeaponModeStatement__GetSerializedSize", sigFastInt("CWeaponModeStatement__GetSerializedSize"), "serialized-size"),
            reviewed("0x0042fc70", "CPhysicsWeaponModeValueList__GetSerializedSize", sigFastInt("CPhysicsWeaponModeValueList__GetSerializedSize"), "serialized-size"),
            dtor("0x0042fea0", "CPhysicsWeaponModeValueList__scalar_deleting_dtor", "0x005d98b0", "physics-script-wave331"),
            reviewed("0x0042ff60", "CRoundStatement__CreateRoundAndRecurse", sigFast("CRoundStatement__CreateRoundAndRecurse"), "statement-update"),
            reviewed("0x00430190", "CRoundStatement__GetSerializedSize", sigFastInt("CRoundStatement__GetSerializedSize"), "serialized-size"),
            reviewed("0x004301e0", "CPhysicsRoundValueList__GetSerializedSize", sigFastInt("CPhysicsRoundValueList__GetSerializedSize"), "serialized-size"),
            dtor("0x00430410", "CPhysicsRoundValueList__scalar_deleting_dtor", "0x005d98b8", "physics-script-wave332")
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
            throw new IllegalStateException("Wave1040 apply encountered missing/bad rows");
        }
    }
}
