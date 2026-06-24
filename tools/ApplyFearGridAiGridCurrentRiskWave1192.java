//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyFearGridAiGridCurrentRiskWave1192 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Target(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1192-feargrid-ai-grid-current-risk-review",
        "wave1192-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "fear-grid",
        "ai-grid",
        "source-identity-deferred",
        "exact-layout-deferred",
        "runtime-behavior-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x0040dda0",
            "CUnitAI__RefreshGridCooldownFromOccupiedCells",
            "void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)",
            "Wave1192 static current-risk read-back: CUnitAI cooldown refresh bridge retained from the Wave990 HUD objective-panel normalization. Fresh xrefs show CHud__RenderObjectiveStatusPanel calls this at 0x004862af; decompile/instruction evidence gates on DAT_00672fd0 minus the cooldown threshold, calls the object vfunc at +0x10c, samples CFearGrid__GetOccupancyAtWorldVector for both global grids DAT_008a9d7c and DAT_008a9d80 using this+0x1c/+0x20/+0x24 position fields, and refreshes this+0x2e8 when either occupancy grid is active. Static rebuild contract only; exact CUnitAI/object/vector layouts, exact source-body identity, runtime HUD/objective/AI behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("cunitai", "cooldown-refresh", "hud-objective-panel", "occupancy-query")
        ),
        new Target(
            "0x0044c3d0",
            "CFearGrid__ctor_base",
            "void * __thiscall CFearGrid__ctor_base(void * this, int grid_id)",
            "Wave1192 static current-risk read-back: CFearGrid constructor-style body retained from the Wave366 correction. Fresh xrefs show CGame__InitRestartLoop constructs two grid instances through calls at 0x0046c634 and 0x0046c671; body evidence installs vtable 0x005db2a4, stores grid_id at this+0x8008, calls CFearGrid__RebuildOccupancyAndScheduleTick, returns this, and ends with RET 0x4. Static rebuild contract only; exact allocation owner, concrete CFearGrid layout, source identity, runtime AI/fear-grid behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("constructor", "grid-id", "cgame-init")
        ),
        new Target(
            "0x0044c440",
            "CFearGrid__RebuildOccupancyAndScheduleTick",
            "void __thiscall CFearGrid__RebuildOccupancyAndScheduleTick(void * this)",
            "Wave1192 static current-risk read-back: CFearGrid rebuild/refresh body retained from the Wave993 normalization. Fresh xrefs show constructor/init scheduling callers and the tracked-object weight helper call at 0x0044c4af. Decompile evidence clears the occupancy plane at this+0x08, initializes the clearance plane at this+0x4008, filters tracked objects by this+0x8008 against object fields, calls FearGridTrackedObject__LookupFearWeightByArchetype for occupancy marks, clears nearby clearance cells for blocking actors, and schedules event 1000 through EVENT_MANAGER before returning. Static rebuild contract only; exact object-list ownership, concrete CFearGrid/tracked-object layouts, runtime AI/fear/pathing behavior, pickup behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("grid-refresh", "occupancy-plane", "clearance-plane", "event-1000", "tracked-object-weight")
        ),
        new Target(
            "0x0044c720",
            "CFearGrid__GetOccupancyAtWorldVector",
            "int __thiscall CFearGrid__GetOccupancyAtWorldVector(void * this, float vector_x, float vector_y, float vector_z, float vector_w)",
            "Wave1192 static current-risk read-back: CFearGrid occupancy sampler retained from the Wave366 correction. Fresh xrefs show CUnitAI__RefreshGridCooldownFromOccupiedCells calls this for DAT_008a9d7c and DAT_008a9d80, while CSquadNormal__Process also samples grid occupancy. Body evidence treats the stack payload as a 16-byte world vector, rounds vector_x/vector_y into 8-unit 64x64 grid coordinates, reads the occupancy plane at this+0x08, returns zero when outside the grid, and ends with RET 0x10. Static rebuild contract only; exact vector-by-value type, concrete CFearGrid layout, source identity, runtime AI/formation/pathing behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("occupancy", "world-vector", "ret-0x10", "squadnormal")
        ),
        new Target(
            "0x0044c780",
            "CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta",
            "int __thiscall CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta(void * this, float vector_x, float vector_y, float vector_z, float vector_w)",
            "Wave1192 static current-risk read-back: CFearGrid clearance sampler retained from the Wave366 correction. Fresh xrefs show OID__CanFireAtTarget_BallisticArcA and OID__CanFireAtTarget_BallisticArcB call this at 0x00507b5b and 0x00508953. Body evidence samples terrain height through CStaticShadows__SampleShadowHeightBilinear, gates vector_z against the static threshold at 0x005db2b0, reads the clearance plane at this+0x4008 when the sample is in range, otherwise returns the fallback clear value, and ends with RET 0x10. Static rebuild contract only; exact vector/terrain/clearance layout, source identity, runtime firing/line-of-sight/pathing behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("clearance", "terrain-height", "ballistic-arc", "ret-0x10")
        ),
        new Target(
            "0x0044c810",
            "CFearGrid__FindNearestFreeCellSpiral",
            "void __thiscall CFearGrid__FindNearestFreeCellSpiral(void * this, void * inout_world_vector)",
            "Wave1192 static current-risk read-back: CFearGrid free-cell spiral search retained from the Wave366 correction. Fresh xrefs show CSquadNormal__Process calls this at 0x004e752d and 0x004e7580 after occupancy sampling. Body evidence converts the first two floats of inout_world_vector into 8-unit 64x64 grid coordinates, spirals through the occupancy plane at this+0x08 for a zero cell, snaps the vector fields back using the scale constant at 0x005d8c44 when a later-radius free cell is found, and ends with RET 0x4. Static rebuild contract only; exact vector layout, source identity, runtime formation/pathing behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("free-cell-search", "spiral-search", "squadnormal", "ret-0x4")
        ),
        new Target(
            "0x004daff0",
            "FearGridTrackedObject__LookupFearWeightByArchetype",
            "double __thiscall FearGridTrackedObject__LookupFearWeightByArchetype(void * this)",
            "Wave1192 static current-risk context read-back: tracked-object fear-weight lookup retained from the Wave826 name correction and used as context for CFearGrid__RebuildOccupancyAndScheduleTick. Fresh xrefs show the rebuild body calls this at 0x0044c4af with the tracked object being marked, not the CFearGrid receiver. Decompile evidence reads the tracked-object name pointer at this+0x118, scans DAT_008553f8 entries, compares against entry+0x30, returns the matched float at entry+0x34, and otherwise returns the default scalar at _DAT_005d856c; the caller scales this result and marks the occupancy plane at grid+0x08. Static rebuild context only; exact tracked-object/list entry layout, concrete weight semantics, runtime AI/fear behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("tracked-object", "archetype-weight", "context-row", "preset-list")
        )
    };

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String mode = args != null && args.length > 0 ? args[0].trim().toLowerCase() : "dry";
        boolean dryRun = true;
        if ("apply".equals(mode)) {
            dryRun = false;
        } else if (!"dry".equals(mode)) {
            throw new IllegalArgumentException("Expected mode dry|apply, got: " + mode);
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : TARGETS) {
            Address address = toAddr(target.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + target.address + " " + target.name);
                missing++;
                continue;
            }

            boolean targetBad = false;
            if (!target.name.equals(function.getName())) {
                println("BADNAME: " + target.address + " expected=" + target.name + " actual=" + function.getName());
                targetBad = true;
            }
            if (!target.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + target.address + " expected=" + target.signature + " actual=" + function.getSignature());
                targetBad = true;
            }
            if (targetBad) {
                bad++;
                continue;
            }

            Set<String> actualTags = tagNames(function);
            Set<String> requiredTags = new HashSet<>(Arrays.asList(target.tags));
            requiredTags.removeAll(actualTags);
            boolean commentNeedsUpdate = function.getComment() == null || !target.comment.equals(function.getComment());
            boolean tagsNeedUpdate = !requiredTags.isEmpty();

            if (!commentNeedsUpdate && !tagsNeedUpdate) {
                println("SKIP: " + target.address + " " + target.name + " comment/tags already current");
                skipped++;
            } else if (dryRun) {
                println("WOULD_UPDATE: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags=+" + String.join(",", requiredTags));
                if (commentNeedsUpdate) {
                    commentOnlyUpdated++;
                }
                tagsAdded += requiredTags.size();
            } else {
                if (commentNeedsUpdate) {
                    function.setComment(target.comment);
                    commentOnlyUpdated++;
                }
                for (String tag : requiredTags) {
                    function.addTag(tag);
                }
                tagsAdded += requiredTags.size();
                updated++;
                currentProgram.flushEvents();
                Thread.sleep(50L);

                Function readBack = functionManager.getFunctionAt(address);
                if (readBack == null) {
                    println("VERIFY_MISSING: " + target.address);
                    bad++;
                } else {
                    if (!target.comment.equals(readBack.getComment())) {
                        println("VERIFY_BAD_COMMENT: " + target.address);
                        bad++;
                    }
                    Set<String> readBackTags = tagNames(readBack);
                    for (String tag : target.tags) {
                        if (!readBackTags.contains(tag)) {
                            println("VERIFY_MISSING_TAG: " + target.address + " " + tag);
                            bad++;
                        }
                    }
                }
                println("UPDATED: " + target.address + " " + target.name + " comment=" + commentNeedsUpdate + " tags_added=" + requiredTags.size());
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + commentOnlyUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1192 FearGrid/AI-grid normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private static String[] withCommon(String... extraTags) {
        String[] tags = new String[COMMON_TAGS.length + extraTags.length];
        System.arraycopy(COMMON_TAGS, 0, tags, 0, COMMON_TAGS.length);
        System.arraycopy(extraTags, 0, tags, COMMON_TAGS.length, extraTags.length);
        return tags;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
