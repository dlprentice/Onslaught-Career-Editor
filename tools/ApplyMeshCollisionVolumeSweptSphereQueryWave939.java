//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyMeshCollisionVolumeSweptSphereQueryWave939 extends GhidraScript {
    private static final String ADDRESS = "0x004ac140";
    private static final String NAME = "CMeshCollisionVolume__TestSweptSphereAgainstBounds";
    private static final String SIGNATURE =
        "int __stdcall CMeshCollisionVolume__TestSweptSphereAgainstBounds(void * part_context, void * bounds_record, float * sphere_start, float * sweep_delta, float * sphere_radius, void * contact_record)";
    private static final String COMMENT =
        "Wave939 comment normalization over Wave535: RET 0x18 helper called from CMeshCollisionVolume vtable slot 3; lazily initializes the direction table, rejects sphere sweeps outside the bounds_record center/extent fields at +0xfc, uses a 24-entry direction-pointer table as 8 triangle tests when contact_record+0xcc is set, otherwise uses Geometry__DistanceOutsideAabb, and records part_context plus hit/status fields in contact_record. Static retail decompile/xref/instruction evidence only; exact AABB/contact layouts, source identity, runtime collision behavior, and rebuild parity remain unproven.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "meshcollisionvolume-swept-sphere-query-review-wave939",
        "wave939-readback-verified",
        "retail-binary-evidence",
        "comment-normalized",
        "comment-hardened",
        "mesh-collision-volume",
        "swept-sphere",
        "bounds-test"
    };

    private static class Stats {
        int updated = 0;
        int wouldUpdate = 0;
        int skipped = 0;
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

    private Set<String> tagSet(Function fn) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        return existing;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> existing = tagSet(fn);
        for (String tag : TAGS) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn) {
        String existing = fn.getComment();
        return existing == null || !existing.equals(COMMENT) || !hasAllTags(fn);
    }

    private void verifyReadBack() throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!NAME.equals(fn.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + ADDRESS + ": " + fn.getName());
        }
        if (!SIGNATURE.equals(fn.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + ADDRESS + ": " + fn.getSignature());
        }
        if (!COMMENT.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + ADDRESS);
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back tag mismatch at " + ADDRESS);
        }
    }

    private void apply(boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(ADDRESS);
        if (fn == null) {
            println("MISSING: " + ADDRESS);
            stats.missing++;
            return;
        }
        if (!NAME.equals(fn.getName())) {
            println("BADNAME: " + ADDRESS + " actual=" + fn.getName() + " expected=" + NAME);
            stats.bad++;
            return;
        }
        if (!SIGNATURE.equals(fn.getSignature().toString())) {
            println("BADSIGNATURE: " + ADDRESS + " actual=" + fn.getSignature() + " expected=" + SIGNATURE);
            stats.bad++;
            return;
        }

        if (!needsUpdate(fn)) {
            println("SKIP: " + ADDRESS + " already current");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + ADDRESS + " comment/tags would be normalized");
            stats.wouldUpdate++;
            return;
        }

        fn.setComment(COMMENT);
        Set<String> existing = tagSet(fn);
        for (String tag : TAGS) {
            if (!existing.contains(tag)) {
                fn.addTag(tag);
            }
        }
        verifyReadBack();
        println("OK: " + ADDRESS + " comment/tags normalized");
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        apply(dryRun, stats);
        println("SUMMARY updated=" + stats.updated + " would_update=" + stats.wouldUpdate +
            " skipped=" + stats.skipped + " missing=" + stats.missing + " bad=" + stats.bad);
    }
}
