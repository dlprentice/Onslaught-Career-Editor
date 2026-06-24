//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyPhysicsValueListLifetimeCurrentRiskWave1183 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final List<String> tags;

        Spec(String address, String name, String signature, String comment, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = Arrays.asList(tags);
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

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1183-physics-value-list-lifetime-current-risk-review",
        "wave1183-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "physics-script",
        "value-lifetime",
        "comment-corrected",
        "memory-manager-free",
        "shared-vtable-slot",
        "destructor"
    };

    private static Spec spec(
            String address,
            String name,
            String signature,
            String baseName,
            String baseAddress,
            String ownerTag,
            String ownerDescription) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.add(ownerTag);

        String comment = "Wave1183 static correction: shared scalar-deleting destructor wrapper used by "
            + ownerDescription
            + " vtables. It calls "
            + baseName
            + " at "
            + baseAddress
            + ", tests the scalar-delete flag, and when bit 0 is set frees this through "
            + "CDXMemoryManager__Free(&DAT_009c3df0, this) via call 0x00549220, not OID__FreeObject. "
            + "It returns this and ends with RET 0x4. Specific leaf owner, concrete layouts, runtime lifetime behavior, "
            + "exact source-body identity, BEA patching, gameplay outcomes, clean-room replacement parity, and rebuild parity remain separate proof.";

        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec(
            "0x00438400",
            "CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor",
            "void * __thiscall CPhysicsRoundValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
            "CPhysicsRoundValue__dtor_base",
            "0x004380c0",
            "round-value",
            "many leaf round-value"),
        spec(
            "0x0043a840",
            "CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor",
            "void * __thiscall CPhysicsSpawnerValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
            "CPhysicsSpawnerValue__dtor_base",
            "0x0043a040",
            "spawner-value",
            "many leaf spawner-value"),
        spec(
            "0x0043b970",
            "CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor",
            "void * __thiscall CPhysicsExplosionValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
            "CPhysicsExplosionValue__dtor_base",
            "0x0043af80",
            "explosion-value",
            "leaf explosion-value"),
        spec(
            "0x0043bff0",
            "CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor",
            "void * __thiscall CPhysicsFeatureValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
            "CPhysicsFeatureValue__dtor_base",
            "0x0043be00",
            "feature-value",
            "leaf feature-value"),
        spec(
            "0x0043c230",
            "CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor",
            "void * __thiscall CPhysicsHazardValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
            "CPhysicsHazardValue__dtor_base",
            "0x0043c310",
            "hazard-value",
            "leaf hazard-value"),
        spec(
            "0x0043d5a0",
            "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor",
            "void * __thiscall CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor(void * this, int flags)",
            "CPhysicsComponentValue__dtor_base",
            "0x0043dcc0",
            "component-value",
            "type-10 component-value leaf")
    };

    @Override
    protected void run() throws Exception {
        boolean dryRun = true;
        String[] args = getScriptArgs();
        if (args.length > 0) {
            String mode = args[0].trim().toLowerCase();
            if ("apply".equals(mode)) {
                dryRun = false;
            } else if (!"dry".equals(mode)) {
                throw new IllegalArgumentException("Expected mode dry|apply, got: " + args[0]);
            }
        }

        Stats stats = new Stats();
        for (Spec spec : SPECS) {
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
            throw new IllegalStateException("Wave1183 PhysicsScript value-list lifetime correction failed: missing="
                + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function function = functionAtEntry(spec.address);
        if (function == null) {
            println("MISSING: " + spec.address + " " + spec.name);
            stats.missing++;
            return;
        }

        if (!spec.name.equals(function.getName())) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
            stats.bad++;
            return;
        }
        if (!spec.signature.equals(function.getSignature().toString())) {
            println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + function.getSignature());
            stats.bad++;
            return;
        }

        Set<String> existingTags = tagNames(function);
        List<String> missingTags = new ArrayList<>();
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                missingTags.add(tag);
            }
        }

        boolean commentNeedsUpdate = !spec.comment.equals(function.getComment());
        boolean tagsNeedUpdate = !missingTags.isEmpty();
        if (!commentNeedsUpdate && !tagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        stats.tagsAdded += missingTags.size();
        if (commentNeedsUpdate) {
            stats.commentOnlyUpdated++;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name
                + " comment_update=" + commentNeedsUpdate
                + " missing_tags=" + String.join(",", missingTags));
            return;
        }

        if (commentNeedsUpdate) {
            function.setComment(spec.comment);
        }
        for (String tag : missingTags) {
            function.addTag(tag);
        }
        currentProgram.flushEvents();
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name
            + " comment_update=" + commentNeedsUpdate
            + " tags_added=" + missingTags.size());
        stats.updated++;
        Thread.sleep(50L);
    }

    private Function functionAtEntry(String addressText) {
        Address entry = toAddr(addressText);
        Function function = getFunctionAt(entry);
        if (function != null) {
            return function;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function function = functionAtEntry(spec.address);
        if (function == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!spec.name.equals(function.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + function.getName());
        }
        if (!spec.signature.equals(function.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + function.getSignature());
        }
        if (!spec.comment.equals(function.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> actualTags = tagNames(function);
        for (String tag : spec.tags) {
            if (!actualTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }
}
