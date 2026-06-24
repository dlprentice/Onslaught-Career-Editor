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

public class ApplyWaypointWingmanLifecycleCurrentRiskWave1210 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final List<String> tags;
        final List<String> removeTags;

        Spec(String address, String name, String signature, String comment, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = Arrays.asList(tags);
            this.removeTags = Arrays.asList();
        }

        Spec(String address, String name, String signature, String comment, String[] tags, String[] removeTags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = Arrays.asList(tags);
            this.removeTags = Arrays.asList(removeTags);
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int tagsRemoved = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1210-waypoint-wingman-lifecycle-current-risk-review",
        "wave1210-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "object-lifecycle",
        "waypoint-lifecycle",
        "rebuild-grade-static-contract"
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static Spec specRemove(String address, String name, String signature, String comment, String[] extraTags, String... removeTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]), removeTags);
    }

    private static final Spec[] SPECS = {
        spec(
            "0x004bfd60",
            "CWaypoint__scalar_deleting_dtor",
            "void * __thiscall CWaypoint__scalar_deleting_dtor(void * this, byte flags)",
            "Wave1210 static correction: CWaypoint vtable slot 1 scalar-deleting destructor wrapper. DATA vtable ref 0x005dd2f4 points at this wrapper. The body calls CWaypoint__dtor_base at 0x004bfe70, tests flags & 1, optionally frees this through CDXMemoryManager__Free(&DAT_009c3df0, this), returns this, and ends with RET 0x4. Static retail Ghidra metadata/xref/instruction/decompile evidence only; runtime waypoint cleanup behavior, destructor completeness, concrete layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "scalar-deleting-destructor",
            "destructor",
            "waypoint",
            "comment-corrected",
            "memory-manager-free"),
        spec(
            "0x004bfdc0",
            "CWingmanStart__scalar_deleting_dtor",
            "void * __thiscall CWingmanStart__scalar_deleting_dtor(void * this, byte flags)",
            "Wave1210 static correction: CWingmanStart vtable slot 1 scalar-deleting destructor wrapper. DATA vtable ref 0x005dcb5c points at this wrapper. The body calls CWingmanStart__dtor_base at 0x004bffa0, tests flags & 1, optionally frees this through CDXMemoryManager__Free(&DAT_009c3df0, this), returns this, and ends with RET 0x4. Static retail Ghidra metadata/xref/instruction/decompile evidence only; runtime wingman-start cleanup behavior, destructor completeness, concrete layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "scalar-deleting-destructor",
            "destructor",
            "wingman-start",
            "comment-corrected",
            "memory-manager-free"),
        spec(
            "0x004bfe70",
            "CWaypoint__dtor_base",
            "void __fastcall CWaypoint__dtor_base(void * this)",
            "Wave1210 static correction: CWaypoint destructor-base body called by CWaypoint__scalar_deleting_dtor at 0x004bfd60. If the owner/list link at this+0x3c is populated and its monitored/list pointer at +0x04 is non-null, the body removes the link through CSPtrSet__Remove, then delegates to CThing__dtor_base. This corrects stale CThing__ctor_like_004f3640 wording from earlier comments. Static retail Ghidra metadata/xref/instruction/decompile evidence only; runtime waypoint cleanup behavior, exact link layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "destructor-body",
            "destructor",
            "waypoint",
            "comment-corrected",
            "owner-link-cleanup"),
        spec(
            "0x004bffa0",
            "CWingmanStart__dtor_base",
            "void __fastcall CWingmanStart__dtor_base(void * this)",
            "Wave1210 static read-back: CWingmanStart destructor-base body called by CWingmanStart__scalar_deleting_dtor at 0x004bfdc0. If the owner/list link at this+0x7c is populated and its monitored/list pointer at +0x04 is non-null, the body removes the link through CSPtrSet__Remove, then delegates to CComplexThing__dtor_base. Static retail Ghidra metadata/xref/instruction/decompile evidence only; runtime wingman-start cleanup behavior, exact link layout, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "destructor-body",
            "destructor",
            "wingman-start",
            "owner-link-cleanup"),
        specRemove(
            "0x00505960",
            "CWaypoint__Load",
            "void __thiscall CWaypoint__Load(void * this, void * mem_buffer, int load_mode, void * object_table)",
            "Wave1210 static read-back: CWaypointManager__LoadWaypoints calls this loader with the newly allocated waypoint in ECX; RET 0x0c confirms mem_buffer, load_mode, and object_table stack arguments. The body reads a byte name length, allocates/null-terminates the waypoint name at this+0x04 using WaypointManager.cpp line 0x1a provenance, then either links a global waypoint-list entry selected by a 16-bit index for old load modes or reads object_table indices and links flagged objects into this+0x08. Static retail Ghidra metadata/xref/instruction/decompile evidence only; concrete CWaypoint/list/object-table layouts, exact source identity, runtime AI navigation behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            new String[] {"waypoint", "load", "mem-buffer", "object-link"},
            "destructor"),
        spec(
            "0x00505bb0",
            "CWaypointPath__scalar_deleting_dtor",
            "void * __thiscall CWaypointPath__scalar_deleting_dtor(void * this, byte flags)",
            "Wave1210 static read-back: CWaypointPath table 0x005dfc8c slot 0 points at this scalar-deleting destructor wrapper. The body calls CWaypointPath__dtor_base at 0x00505bd0, checks flags & 1, frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when requested, returns this, and ends with RET 0x4. Static retail Ghidra metadata/xref/instruction/decompile evidence only; exact table ownership, concrete CWaypointPath layout, runtime waypoint-path teardown behavior, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            "scalar-deleting-destructor",
            "destructor",
            "waypoint-path",
            "memory-manager-free")
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
            + " tags_removed=" + stats.tagsRemoved
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1210 Waypoint/Wingman lifecycle correction failed: missing="
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
        List<String> presentRemoveTags = new ArrayList<>();
        for (String tag : spec.removeTags) {
            if (existingTags.contains(tag)) {
                presentRemoveTags.add(tag);
            }
        }

        boolean commentNeedsUpdate = !spec.comment.equals(function.getComment());
        boolean tagsNeedUpdate = !missingTags.isEmpty() || !presentRemoveTags.isEmpty();
        if (!commentNeedsUpdate && !tagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        stats.tagsAdded += missingTags.size();
        stats.tagsRemoved += presentRemoveTags.size();
        if (commentNeedsUpdate) {
            stats.commentOnlyUpdated++;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name
                + " comment_update=" + commentNeedsUpdate
                + " missing_tags=" + String.join(",", missingTags)
                + " remove_tags=" + String.join(",", presentRemoveTags));
            return;
        }

        if (commentNeedsUpdate) {
            function.setComment(spec.comment);
        }
        for (String tag : missingTags) {
            function.addTag(tag);
        }
        for (String tag : presentRemoveTags) {
            function.removeTag(tag);
        }
        currentProgram.flushEvents();
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name
            + " comment_update=" + commentNeedsUpdate
            + " tags_added=" + missingTags.size()
            + " tags_removed=" + presentRemoveTags.size());
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
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        if (!spec.signature.equals(function.getSignature().toString())) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address
                + " actual=" + function.getSignature());
        }
        if (!spec.comment.equals(function.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> existingTags = tagNames(function);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
            }
        }
        for (String tag : spec.removeTags) {
            if (existingTags.contains(tag)) {
                throw new IllegalStateException("Read-back stale tag at " + spec.address + ": " + tag);
            }
        }
    }
}
