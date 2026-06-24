//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyWave1216RenderResourceTextureHudTailCurrentRisk extends GhidraScript {
    private static final class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "retail-binary-evidence",
        "current-risk-review",
        "wave1216-render-resource-texture-hud-tail-current-risk-review",
        "wave1216-readback-verified",
        "texture-node-label-corrected",
        "rebuild-grade-static-contract"
    };

    private static final Spec[] SPECS = {
        new Spec(
            "0x005997e1",
            "CTexture__NodeType12_Ctor_DeleteOnFlag",
            "CTexture__NodeType11_Ctor_WithDescriptorCopy",
            "Wave1216 static read-back/name correction: hidden-ECX constructor for node-type 0x11, not node-type 0x12. The body calls CTexture__NodePayloadBaseCtor with type value 0x11, binds vtable 0x005ef374, copies eight descriptor dwords into +0x10, copies stack scalars into +0x30/+0x34/+0x38, clears +0x3c through +0x58, and returns the node pointer. Signature intentionally remains locked as Ghidra reports unknown calling convention/parameter storage. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact hidden ABI, descriptor schema, runtime texture behavior, and rebuild parity remain unproven.",
            tags("constructor", "hidden-ecx", "locked-storage", "node-type-0x11", "descriptor-copy", "name-corrected")
        ),
        new Spec(
            "0x00599831",
            "CTexture__NodeType12_Dtor_DeleteOnFlag_Body",
            "CTexture__NodeType11_Dtor_DeleteOnFlag_Body",
            "Wave1216 static read-back/name correction: destructor body for the node-type 0x11 vtable at 0x005ef374. The body restores vtable 0x005ef374, releases optional owned interfaces at +0x3c and +0x40 through vslot 0 with delete flag 1, releases up to four +0x44..+0x50 entries through the same path, then releases the base node-payload chain. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact slot ownership, interface types, runtime texture behavior, and rebuild parity remain unproven.",
            tags("destructor-body", "node-type-0x11", "owned-resource-slots", "release-chain", "name-corrected")
        ),
        new Spec(
            "0x00599a3c",
            "CTexture__NodeType12_Dtor_DeleteOnFlag",
            "CTexture__NodeType11_Dtor_DeleteOnFlag",
            "Wave1216 static read-back/name correction: scalar-deleting-style wrapper for the node-type 0x11 vtable at 0x005ef374. The wrapper calls CTexture__NodeType11_Dtor_DeleteOnFlag_Body, frees this through OID__FreeObject_Callback when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact vtable slot, allocator ownership, runtime texture behavior, and rebuild parity remain unproven.",
            tags("scalar-deleting-dtor", "delete-flag", "node-type-0x11", "name-corrected")
        ),
        new Spec(
            "0x0059996f",
            "CTexture__NodeType12_Ctor_ScalarDeletingDtor",
            "CTexture__NodeType12_Ctor_WithStackScalars",
            "Wave1216 static read-back/name correction: hidden-ECX constructor for node-type 0x12, not a scalar-deleting destructor. The body calls CTexture__NodePayloadBaseCtor with type value 0x12, copies five stack-provided scalars into +0x10/+0x14/+0x18/+0x1c/+0x28, binds vtable 0x005ef384, seeds fixed scalar defaults +0x20=0xf0000 and +0x24=0xe40000, and returns the node pointer. Signature intentionally remains locked as Ghidra reports unknown calling convention/parameter storage. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact hidden ABI, scalar semantics, runtime texture behavior, and rebuild parity remain unproven.",
            tags("constructor", "hidden-ecx", "locked-storage", "node-type-0x12", "stack-scalars", "default-scalars", "name-corrected")
        )
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

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : SPECS) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=0"
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1216 texture label correction failed: missing="
                + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function function = functionAtEntry(spec.address);
        if (function == null) {
            println("MISSING: " + spec.address + " " + spec.newName);
            stats.missing++;
            return;
        }

        String currentName = function.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " expected_old=" + spec.oldName
                + " expected_new=" + spec.newName + " actual=" + currentName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean commentNeeded = function.getComment() == null || !function.getComment().equals(spec.comment);
        Set<String> existingTags = tagNames(function);
        List<String> missingTags = new ArrayList<>();
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                missingTags.add(tag);
            }
        }

        if (!renameNeeded && !commentNeeded && missingTags.isEmpty()) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (renameNeeded && dryRun) {
            stats.wouldRename++;
        }
        if (commentNeeded) {
            stats.commentOnlyUpdated++;
        }
        stats.tagsAdded += missingTags.size();

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName
                + " rename=" + renameNeeded
                + " comment=" + commentNeeded
                + " missing_tags=" + String.join(",", missingTags));
            return;
        }

        if (renameNeeded) {
            function.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (commentNeeded) {
            function.setComment(spec.comment);
        }
        for (String tag : missingTags) {
            function.addTag(tag);
        }

        currentProgram.flushEvents();
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.newName
            + " renamed=" + renameNeeded
            + " comment=" + commentNeeded
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
        if (!spec.newName.equals(function.getName())) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address
                + " actual=" + function.getName());
        }
        if (function.getComment() == null || !function.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> existingTags = tagNames(function);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
    }

    private static String[] tags(String... specificTags) {
        String[] all = new String[COMMON_TAGS.length + specificTags.length];
        System.arraycopy(COMMON_TAGS, 0, all, 0, COMMON_TAGS.length);
        System.arraycopy(specificTags, 0, all, COMMON_TAGS.length, specificTags.length);
        return all;
    }
}
