//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyWave1217LifecycleCleanupTailCurrentRisk extends GhidraScript {
    private static final class Spec {
        final String address;
        final String name;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final class Stats {
        int updated = 0;
        int skipped = 0;
        int commentUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "retail-binary-evidence",
        "current-risk-review",
        "wave1217-lifecycle-cleanup-tail-current-risk-review",
        "wave1217-readback-verified",
        "lifecycle-cleanup-tail",
        "rebuild-grade-static-contract"
    };

    private static final Spec[] SPECS = {
        new Spec(
            "0x00421b80",
            "CCarrierAI__scalar_deleting_dtor",
            "Wave1217 static current-risk read-back: CCarrierAI scalar-deleting destructor wrapper at vtable DATA xref 0x005d93d8. The body calls CCarrierAI__dtor_base, tests delete flag bit 0, optionally frees this through CDXMemoryManager__Free, and returns this with RET 0x4. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact CarrierAI layout, exact source virtual identity, runtime AI cleanup behavior, allocator ownership beyond the observed free path, BEA patching, and rebuild parity remain separate proof.",
            tags("carrier-ai", "scalar-deleting-dtor", "delete-flag", "vtable-slot")
        ),
        new Spec(
            "0x004bfce0",
            "CTree__scalar_deleting_dtor",
            "Wave1217 static current-risk read-back: CTree vtable slot-1 scalar-deleting destructor wrapper at DATA xref 0x005dd9dc. The wrapper calls CTree__dtor_base at 0x004f63c0, tests delete flag bit 0, optionally frees this through CDXMemoryManager__Free, and returns this with RET 0x4. This corrects stale comment wording that referred to 0x004f63c0 as another scalar-deleting destructor. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact tree layout, runtime tree cleanup behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("ctree", "scalar-deleting-dtor", "delete-flag", "vtable-slot", "stale-comment-corrected")
        ),
        new Spec(
            "0x004bfd00",
            "CActorBase__shared_scalar_deleting_dtor_004bfd00",
            "Wave1217 static current-risk read-back: shared actor-base-style scalar-deleting destructor wrapper with vtable DATA xrefs 0x005dd5f4, 0x005ded4c, and 0x005e45e4. The body calls CActor__dtor_base_Thunk, tests delete flag bit 0, optionally frees this through CDXMemoryManager__Free, and returns this with RET 0x4. The owner name remains intentionally shared/bounded. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact owning classes, concrete layouts, runtime lifetime behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("shared-wrapper", "actor-base", "scalar-deleting-dtor", "delete-flag", "owner-bounded")
        ),
        new Spec(
            "0x004db8d0",
            "CRTBuilding__ScalarDeletingDestructor",
            "Wave1217 static current-risk read-back: CRTBuilding scalar-deleting destructor wrapper at vtable DATA xref 0x005de9c0. The body calls CRTBuilding__Destructor, tests delete flag bit 0, optionally frees this through CDXMemoryManager__Free, and returns this with RET 0x4. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact CRTBuilding layout, runtime render-building cleanup behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("rtbuilding", "scalar-deleting-dtor", "delete-flag", "render-lifecycle", "vtable-slot")
        ),
        new Spec(
            "0x004df520",
            "CActor__dtor_base_Thunk",
            "Wave1217 static current-risk read-back: CActor destructor-base thunk called by CActorBase__shared_scalar_deleting_dtor_004bfd00 at 0x004bfd03. The thunk jumps to CActor__dtor_base, which resets actor vtables and delegates to CComplexThing__dtor_base. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact shared-vtable ownership, concrete actor layout, runtime lifetime behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("actor", "destructor-thunk", "shared-wrapper-callee", "lifecycle")
        ),
        new Spec(
            "0x004f3a70",
            "CCSPersistentThing__dtor_base",
            "Wave1217 static current-risk read-back: CCSPersistentThing destructor-base helper called by CCSPersistentThing__scalar_deleting_dtor at 0x004f3a53. The body shuts down monitor state at this+0x24, then chains into CCollisionSeekingRound__Destructor for the base collision-seeking fields. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact persistent-collision layout, exact source-body identity, runtime collision cleanup behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("persistent-collision", "destructor-body", "monitor-shutdown", "collision-seeking")
        ),
        new Spec(
            "0x004f63c0",
            "CTree__dtor_base",
            "Wave1217 static current-risk read-back: CTree destructor body called by CTree__scalar_deleting_dtor at 0x004bfce3. The body restores CTree/CThing-adjacent vtables, frees the falling-tree data pointer at this+0x48 through CDXMemoryManager__Free when present, clears that pointer, and delegates to CThing__dtor_base. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact tree layout, runtime falling-tree cleanup behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("ctree", "destructor-body", "falling-tree", "base-chain")
        ),
        new Spec(
            "0x005044f0",
            "CWarspite__ScalarDeletingDestructor",
            "Wave1217 static current-risk read-back: CWarspite scalar-deleting destructor wrapper at vtable DATA xref 0x005dfbe0. The body calls CWarspite__Destructor, tests delete_flags bit 0, optionally frees this through CDXMemoryManager__Free, and returns this with RET 0x4. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact Warspite AI/controller layout, runtime AI cleanup behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("warspite-ai", "scalar-deleting-dtor", "delete-flag", "vtable-slot")
        ),
        new Spec(
            "0x004ba490",
            "CMine__VFunc02_CleanupLinkedParticleAndForward",
            "Wave1217 static current-risk read-back: CMine cleanup/forwarding vfunc at DATA xref 0x005e1b8c. The body clears the linked particle/effect owner-link cell through ParticleEffectLink__SetHandleStateAndClear, removes/frees the particle-manager global-list node when present, then forwards to CUnit__VFunc02_CleanupWorldLinksAndForward. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact mine/effect-link layouts, exact virtual slot identity, runtime cleanup behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("mine", "cleanup-forwarder", "particle-effect-link", "vfunc-slot")
        ),
        new Spec(
            "0x004ba9d0",
            "CMine__TryDestroyedResetAndDispatchVFunc1D4",
            "Wave1217 static current-risk read-back: CMine destruction/reset vfunc at DATA xref 0x005e1c4c. The body calls CGroundUnit__MarkDestroyedAndResetState, returns 0 if that gate fails, otherwise dispatches receiver vfunc +0x1d4 and returns 1. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact mine lifecycle layout, exact virtual slot identity, runtime destruction behavior, BEA patching, and rebuild parity remain separate proof.",
            tags("mine", "destroyed-reset", "vfunc-dispatch", "groundunit")
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
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + stats.commentUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1217 lifecycle cleanup tail failed: missing="
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
        if (!function.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
            stats.bad++;
            return;
        }

        boolean commentNeeded = function.getComment() == null || !function.getComment().equals(spec.comment);
        Set<String> existingTags = tagNames(function);
        List<String> missingTags = new ArrayList<>();
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                missingTags.add(tag);
            }
        }

        if (!commentNeeded && missingTags.isEmpty()) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        if (commentNeeded) {
            stats.commentUpdated++;
        }
        stats.tagsAdded += missingTags.size();

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name
                + " comment=" + commentNeeded
                + " missing_tags=" + String.join(",", missingTags));
            return;
        }

        if (commentNeeded) {
            function.setComment(spec.comment);
        }
        for (String tag : missingTags) {
            function.addTag(tag);
        }
        currentProgram.flushEvents();
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name
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
        if (!spec.name.equals(function.getName())) {
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
