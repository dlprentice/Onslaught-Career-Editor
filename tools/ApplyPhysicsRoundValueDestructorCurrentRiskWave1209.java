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

public class ApplyPhysicsRoundValueDestructorCurrentRiskWave1209 extends GhidraScript {
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
        "wave1209-physics-roundvalue-destructor-current-risk-review",
        "wave1209-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "physics-script",
        "round-value-tail",
        "nested-round-value",
        "destructor",
        "rebuild-grade-static-contract"
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec(
            "0x004395b0",
            "CRoundSeek__scalar_deleting_dtor",
            "void * __thiscall CRoundSeek__scalar_deleting_dtor(void * this, int flags)",
            "Wave1209 static correction: CRoundSeek scalar-deleting destructor wrapper in the PhysicsScript round-value tail. It calls CRoundSeek__dtor_base at 0x004395d0, tests the scalar-delete flag, and when bit 0 is set frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) via call 0x00549220, not OID__FreeObject. DATA vtable ref 0x005da534 points at this wrapper. Static retail Ghidra metadata/xref/instruction/decompile evidence only; exact source destructor identity, concrete round-value/layout identity, runtime lifetime behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "scalar-deleting-destructor",
            "memory-manager-free",
            "comment-corrected",
            "round-seek"),
        spec(
            "0x004395d0",
            "CRoundSeek__dtor_base",
            "void __fastcall CRoundSeek__dtor_base(void * this)",
            "Wave1209 static read-back: CRoundSeek destructor body called by CRoundSeek__scalar_deleting_dtor at 0x004395b0. The body installs the CRoundSeek vtable 0x005da534, destroys the owned child value at this+0x8 through the child vtable slot 0 with flag 1 when non-null, then restores the CPhysicsRoundValue base vtable 0x005da584 and unwinds the SEH frame. Static retail Ghidra metadata/xref/instruction/decompile evidence only; exact source destructor identity, concrete round-value/layout identity, runtime lifetime behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "destructor-body",
            "owned-child-lifetime",
            "round-seek"),
        spec(
            "0x00439ad0",
            "CRoundTreeCollision__scalar_deleting_dtor",
            "void * __thiscall CRoundTreeCollision__scalar_deleting_dtor(void * this, int flags)",
            "Wave1209 static correction: CRoundTreeCollision scalar-deleting destructor wrapper in the PhysicsScript round-value tail. It calls CRoundTreeCollision__dtor_base at 0x00439af0, tests the scalar-delete flag, and when bit 0 is set frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) via call 0x00549220, not OID__FreeObject. DATA vtable ref 0x005da2dc points at this wrapper. Static retail Ghidra metadata/xref/instruction/decompile evidence only; exact source destructor identity, concrete round-value/layout identity, runtime lifetime behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "scalar-deleting-destructor",
            "memory-manager-free",
            "comment-corrected",
            "round-tree-collision"),
        spec(
            "0x00439af0",
            "CRoundTreeCollision__dtor_base",
            "void __fastcall CRoundTreeCollision__dtor_base(void * this)",
            "Wave1209 static read-back: CRoundTreeCollision destructor body called by CRoundTreeCollision__scalar_deleting_dtor at 0x00439ad0. The body installs the CRoundTreeCollision vtable 0x005da2dc, destroys the owned child value at this+0x8 through the child vtable slot 0 with flag 1 when non-null, then restores the CPhysicsRoundValue base vtable 0x005da584 and unwinds the SEH frame. Static retail Ghidra metadata/xref/instruction/decompile evidence only; exact source destructor identity, concrete round-value/layout identity, runtime lifetime behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "destructor-body",
            "owned-child-lifetime",
            "round-tree-collision")
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
            throw new IllegalStateException("Wave1209 PhysicsScript round-value destructor correction failed: missing="
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
