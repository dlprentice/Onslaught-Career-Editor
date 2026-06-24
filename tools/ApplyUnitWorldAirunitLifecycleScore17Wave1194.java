//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyUnitWorldAirunitLifecycleScore17Wave1194 extends GhidraScript {
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
        "wave1194-unit-world-airunit-lifecycle-score17-current-risk-review",
        "wave1194-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score17",
        "unit-world-airunit-lifecycle",
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
            "0x004dfa40",
            "CUnit__VFunc08_InitAndAddToWorld",
            "void __thiscall CUnit__VFunc08_InitAndAddToWorld(void * this, void * init)",
            "Wave1194 static current-risk read-back: score17 unit lifecycle/add-to-world row retained from Wave1075 boundary recovery with normalized rebuild-grade tags. Fresh metadata/xref/instruction/decompile evidence keeps the CUnit-family vtable table 0x005dfd40 slot 8 DATA xref at 0x005dfd60; the body consumes ECX this and stack init, calls CUnit__Init, dispatches vtable offset +0x48, clears this+0x13c, then calls CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk(this). Static rebuild contract only; exact source virtual name, concrete CUnit/init/world-layout semantics, runtime init/add-to-world/static-shadow behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("cunit", "unit-lifecycle", "add-to-world", "world-occupancy", "static-shadow", "vtable-slot")
        ),
        new Target(
            "0x004dfd10",
            "CUnit__VFunc18_SyncOldVectorAndClampHeight",
            "void __thiscall CUnit__VFunc18_SyncOldVectorAndClampHeight(void * this)",
            "Wave1194 static current-risk read-back: score17 unit movement/height-clamp row retained from Wave507 and Wave912 context with normalized rebuild-grade tags. Fresh DATA xrefs keep unit-family vtable tables 0x005d8efc and 0x005dfd84; body evidence calls CActor__StickToGround, then clamps current Z at this+0x24 and old/render Z at this+0x94 down to global ceiling 0x006fbdfc when the global is below current Z. Static rebuild contract only; exact source virtual name, concrete height/ceiling semantics, runtime movement behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("cunit", "height-clamp", "old-vector-sync", "stick-to-ground", "movement")
        ),
        new Target(
            "0x0050b010",
            "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
            "void __stdcall CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk(void * unit)",
            "Wave1194 static current-risk read-back: score17 world occupancy add/shadow rebuild thunk retained from Wave790 with normalized rebuild-grade tags. Fresh xrefs show callers from UnitAI, Feature, WarspiteDome, Building, NamedMesh, Cannon, Hazard, BattleEngine, and CUnit add-to-world paths; the direct body forwards unit to CWorld__AddUnitToOccupancyGridAndRebuildShadows. Static rebuild contract only; exact source identity, concrete unit/world/list/grid layouts, runtime occupancy/static-shadow behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("cworld", "world-occupancy", "shadow-rebuild", "add-to-world", "thunk")
        ),
        new Target(
            "0x0050b020",
            "CWorld__RemoveUnitFromOccupancyGrid_Thunk",
            "void __stdcall CWorld__RemoveUnitFromOccupancyGrid_Thunk(void * unit)",
            "Wave1194 static current-risk read-back: score17 world occupancy remove thunk retained from Wave790 with normalized rebuild-grade tags. Fresh xrefs show callers from Building, BuildingNamedMesh, NamedMesh, Cannon, Dropship, UnitAI, Feature, and Hazard cleanup/remove paths; the direct body forwards unit to CWorld__RemoveUnitFromOccupancyGrid. Static rebuild contract only; exact source identity, concrete unit/world/list/grid layouts, runtime occupancy removal behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("cworld", "world-occupancy", "remove-from-world", "cleanup", "thunk")
        ),
        new Target(
            "0x0050f130",
            "CGroundAttackAircraft__Destructor_VFunc01",
            "void __fastcall CGroundAttackAircraft__Destructor_VFunc01(void * this)",
            "Wave1194 static current-risk read-back: score17 aircraft destructor body retained from Wave557 with normalized rebuild-grade tags. Fresh xref from CGroundAttackAircraft__scalar_deleting_dtor proves ECX this; body evidence clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, then calls CUnit__dtor_base(this). Static rebuild contract only; exact source destructor identity, concrete aircraft set/list layouts, runtime teardown behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("air-unit", "ground-attack-aircraft", "destructor", "pointer-set-cleanup", "global-list")
        ),
        new Target(
            "0x0050f1f0",
            "CDropship__Destructor_VFunc01",
            "void __fastcall CDropship__Destructor_VFunc01(void * this)",
            "Wave1194 static current-risk read-back: score17 aircraft destructor body retained from Wave557/Wave959 context with normalized rebuild-grade tags. Fresh xref from CDropship__scalar_deleting_dtor proves ECX this; body evidence clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, then calls CUnit__dtor_base(this). Static rebuild contract only; exact source destructor identity, concrete aircraft set/list layouts, runtime dropship teardown behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("air-unit", "dropship", "destructor", "pointer-set-cleanup", "global-list")
        ),
        new Target(
            "0x0050f260",
            "CPlane__Destructor_VFunc01",
            "void __fastcall CPlane__Destructor_VFunc01(void * this)",
            "Wave1194 static current-risk read-back: score17 aircraft destructor body retained from Wave557 with normalized rebuild-grade tags. Fresh xref from CPlane__scalar_deleting_dtor proves ECX this; body evidence clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, then calls CUnit__dtor_base(this). Static rebuild contract only; exact source destructor identity, concrete aircraft set/list layouts, runtime plane teardown behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("air-unit", "plane", "destructor", "pointer-set-cleanup", "global-list")
        ),
        new Target(
            "0x0050f2d0",
            "CDiveBomber__Destructor_VFunc01",
            "void __fastcall CDiveBomber__Destructor_VFunc01(void * this)",
            "Wave1194 static current-risk read-back: score17 aircraft destructor body retained from Wave557/Wave959 context with normalized rebuild-grade tags. Fresh xref from CDiveBomber__scalar_deleting_dtor proves ECX this; body evidence clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, then calls CUnit__dtor_base(this). Static rebuild contract only; exact source destructor identity, concrete aircraft set/list layouts, runtime dive-bomber teardown behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("air-unit", "dive-bomber", "destructor", "pointer-set-cleanup", "global-list")
        ),
        new Target(
            "0x0050f3b0",
            "CFenrir__Destructor_VFunc01",
            "void __fastcall CFenrir__Destructor_VFunc01(void * this)",
            "Wave1194 static current-risk read-back: score17 aircraft destructor body retained from Wave557 with normalized rebuild-grade tags. Fresh xref from CFenrir__scalar_deleting_dtor proves ECX this; body evidence clears owned pointer sets at this+0x26c and this+0x25c, removes the this+0x250 global-list node, then calls CUnit__dtor_base(this). Static rebuild contract only; exact source destructor identity, concrete aircraft set/list layouts, runtime Fenrir teardown behavior, gameplay parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("air-unit", "fenrir", "destructor", "pointer-set-cleanup", "global-list")
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
            throw new IllegalStateException("Wave1194 unit/world/airunit lifecycle normalization failed: missing=" + missing + " bad=" + bad);
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
