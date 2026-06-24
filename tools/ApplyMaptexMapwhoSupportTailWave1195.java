//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyMaptexMapwhoSupportTailWave1195 extends GhidraScript {
    private static class Target {
        final String address;
        final String name;
        final String signature;
        final String comment;

        Target(String address, String name, String signature, String comment) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1195-cmaptex-cmapwho-support-tail-current-risk-review",
        "wave1195-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score16",
        "maptex-mapwho-support-tail",
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
            "0x00491180",
            "CMapTex__Reset",
            "void __fastcall CMapTex__Reset(void * this)",
            "Wave1195 static current-risk read-back: score16 CMapTex lifecycle/reset support-tail row retained from Wave427 with normalized rebuild-grade tags. Fresh metadata/xref/instruction/decompile evidence keeps the this-only RET shape; body writes -1 to +0x0c, frees owned pointers at +0x00/+0x08 through OID__FreeObject, and clears each slot after the free. Static rebuild contract only; maptex.cpp is absent from the current Stuart source snapshot, and exact CMapTex layout, runtime terrain texture lifecycle behavior, texture pixel/blend parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00491340",
            "CMapTex__DownsampleTexture",
            "void __thiscall CMapTex__DownsampleTexture(void * this, void * dest_buffer, void * src_buffer)",
            "Wave1195 static current-risk read-back: score16 CMapTex downsample support-tail row retained from Wave427 with normalized rebuild-grade tags. Fresh read-back preserves RET 0x8 for dest_buffer/src_buffer; body uses CMapTex width at +0x18 to downsample 2x2 source texels into dest_buffer, with separate signed averaging for the fourth channel. Static rebuild contract only; maptex.cpp is absent from the current Stuart source snapshot, and exact CMapTex/pixel layout, runtime terrain texture behavior, texture pixel/blend parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x004915d0",
            "CMapTex__CopyFromOther",
            "void __thiscall CMapTex__CopyFromOther(void * this, void * source_map_tex)",
            "Wave1195 static current-risk read-back: score16 CMapTex copy/LOD support-tail row retained from Wave427 with normalized rebuild-grade tags. Fresh read-back preserves RET 0x4 for source_map_tex; body refreshes this object when the source set differs, copies set/count/min/max metadata, halves the destination width, allocates a new buffer, and calls CMapTex__DownsampleTexture for each source texture slice. Static rebuild contract only; maptex.cpp is absent from the current Stuart source snapshot, and exact CMapTex layout, runtime terrain texture behavior, texture LOD parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x004916c0",
            "CMapTex__Deserialize",
            "void __thiscall CMapTex__Deserialize(void * this, void * chunk_reader, int texture_index)",
            "Wave1195 static current-risk read-back: score16 CMapTex deserialize support-tail row retained from Wave427 with normalized rebuild-grade tags. Fresh read-back preserves RET 0x8 for chunk_reader and texture_index; body reads the 0x4c-byte CMapTex header from chunk_reader, conditionally allocates count << 0xc primary data and count << 10 secondary data, then reads each payload. Static rebuild contract only; texture_index remains callsite/RET-proven but unused in the current decompile, maptex.cpp is absent from the current Stuart source snapshot, and exact CMapTex/resource layout, runtime terrain texture loading behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00491900",
            "CMapWhoEntry__Init",
            "void __fastcall CMapWhoEntry__Init(void * entry)",
            "Wave1195 static current-risk read-back: score16 CMapWhoEntry init support-tail row retained from Wave428 with normalized rebuild-grade tags. Fresh read-back preserves the register-only initializer; body clears +0x00/+0x04 next/previous links for the CMapWhoEntry-style record. Static rebuild contract only; exact CMapWhoEntry layout, runtime spatial-query behavior, entry lifecycle parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00491d80",
            "CMapWho__SetIteratorFromSectorHead",
            "void * __thiscall CMapWho__SetIteratorFromSectorHead(void * this, void * sector_entry)",
            "Wave1195 static current-risk read-back: score16 CMapWho iterator support-tail row retained from Wave428 with normalized rebuild-grade tags. Fresh read-back preserves RET 0x4 for sector_entry; body writes the sector head at +0x04 into this+0x00 and returns the current entry through EAX. Static rebuild contract only; exact CMapWho/sector layout, runtime spatial-query iteration behavior, collision/render/debug consumer parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00491d90",
            "CMapWho__AdvanceIteratorAndGetCurrent",
            "void * __fastcall CMapWho__AdvanceIteratorAndGetCurrent(void * this)",
            "Wave1195 static current-risk read-back: score16 CMapWho iterator advance support-tail row retained from Wave428 with normalized rebuild-grade tags. Fresh read-back preserves the register-only helper; body advances this+0x00 through the current entry next pointer when present and returns the current entry through EAX. Static rebuild contract only; exact CMapWho/entry layout, runtime spatial-query iteration behavior, collision/render/debug consumer parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00491da0",
            "CMapWho__IsSectorCoordInBounds",
            "int __stdcall CMapWho__IsSectorCoordInBounds(void * sector_coord)",
            "Wave1195 static current-risk read-back: score16 CMapWho sector-coordinate bounds helper retained from Wave428 with normalized rebuild-grade tags. Fresh read-back preserves RET 0x4 for sector_coord; body validates level 0..4 and x/y sector bounds against 64 >> (4 - level), narrowing older generic entry-bounds wording to sector-coordinate validation. Static rebuild contract only; exact packed sector-coordinate/layout semantics, runtime spatial-query bounds behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00491df0",
            "CMapWho__SetupNextRadiusLevel",
            "int __fastcall CMapWho__SetupNextRadiusLevel(void * this)",
            "Wave1195 static current-risk read-back: score16 CMapWho radius-level support-tail row retained from Wave428 with normalized rebuild-grade tags. Fresh read-back preserves the register-only helper; body decrements the active level, uses the query radius at +0x28 plus level cell scale to compute sector bounds at +0x04/+0x08/+0x0c/+0x10, seeds current sector coordinates at +0x2c/+0x2e, and returns 0 when levels are exhausted. Static rebuild contract only; exact CMapWho query layout, runtime radius-query behavior, collision/targeting consumer parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00492860",
            "CMapWho__DebugDrawSector",
            "void __thiscall CMapWho__DebugDrawSector(void * this, int packed_sector_coord, int level)",
            "Wave1195 static current-risk read-back: score16 CMapWho debug-draw support-tail row retained from Wave429 with normalized rebuild-grade tags. Fresh read-back preserves RET 0x8 for packed_sector_coord and level; body unpacks sector x/y, scales by selected level metadata, chooses a debug color by level, prepares a debug volume, and calls CThing__RenderDebugVolumeOverlay. Static rebuild contract only; exact CMapWho/debug volume layout, runtime debug rendering behavior, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00492950",
            "CMapWho__DebugDraw",
            "void __fastcall CMapWho__DebugDraw(void * this)",
            "Wave1195 static current-risk read-back: score16 CMapWho debug-draw traversal support-tail row retained from Wave429 with normalized rebuild-grade tags. Fresh read-back preserves the register-only helper; body resets render state/world matrix, iterates MapWho sectors across levels, calls CMapWhoEntry__GetOwner to filter entries, and calls CMapWho__DebugDrawSector for the first qualifying entry per sector. Static rebuild contract only; exact CMapWho sector/entry layout, runtime debug rendering behavior, visual parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x00492c60",
            "CMapWhoEntry__Invalidate",
            "void __fastcall CMapWhoEntry__Invalidate(void * entry)",
            "Wave1195 static current-risk read-back: score16 CMapWhoEntry invalidation support-tail row retained from Wave429 with normalized rebuild-grade tags. Fresh read-back preserves the register-only helper; body writes -1 to the entry level field at +0x0c. Static rebuild contract only; exact CMapWhoEntry layout, runtime entry tracking/invalidation behavior, collision/spatial-query consumer parity, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
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
            Set<String> requiredTags = new HashSet<>(Arrays.asList(COMMON_TAGS));
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
                    for (String tag : COMMON_TAGS) {
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
            throw new IllegalStateException("Wave1195 CMapTex/CMapWho support-tail normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
