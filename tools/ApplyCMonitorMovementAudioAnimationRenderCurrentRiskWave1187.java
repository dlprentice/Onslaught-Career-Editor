//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyCMonitorMovementAudioAnimationRenderCurrentRiskWave1187 extends GhidraScript {
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
        "wave1187-cmonitor-movement-audio-animation-render-current-risk-review",
        "wave1187-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "monitor",
        "source-identity-deferred",
        "exact-layout-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x00409950",
            "CMonitor__UpdateSoundEventPlaybackForReader",
            "void __fastcall CMonitor__UpdateSoundEventPlaybackForReader(void * monitor)",
            "Wave1187 static read-back: CMonitor sound-event/active-reader helper called from CMonitor__Process at 0x0040963e. The body keeps engine/health/energy/lock/walk samples coherent through CSoundManager play/stop/fade calls, maintains the active reader at monitor+0x5e8 for lock/target audio context, scans the monitor+0x294 event list to trigger walk-sound events, and resets the walk-sound step counter at monitor+0x5d0 when motion gates fail. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact monitor/sound-event/active-reader layouts, exact source-body identity, runtime audio/gameplay behavior, BEA patching, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("sound-event-playback", "active-reader-audio", "process-callee")
        ),
        new Target(
            "0x0044e2c0",
            "CMonitor__CheckSVFAnimationAndAdvanceState",
            "int __fastcall CMonitor__CheckSVFAnimationAndAdvanceState(void * monitor)",
            "Wave1187 static read-back: CMonitor SVF animation gate with DATA vtable ref 0x005e051c. The body resolves the SVF token through CMesh__FindAnimationIndexByName, compares it to the linked object's current animation index from vfunc +0x58, and dispatches monitor vfunc byte offset +0x38 when the current animation matches. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact monitor/object layouts, exact source-body identity, runtime animation/state behavior, BEA patching, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("svf-animation-gate", "animation-state-advance", "vtable-data-ref")
        ),
        new Target(
            "0x0047d3b0",
            "CMonitor__TryQueuePrefireAnimation",
            "int __fastcall CMonitor__TryQueuePrefireAnimation(void * this)",
            "Wave1187 static read-back: CMonitor-style prefire animation helper installed at CGroundVehicle vtable slot 86 via DATA ref 0x005e2ad4. The body calls CUnit__UpdateDeployStateAndChargeEffects, checks profile/state gates at this+0x164/+0x244, resolves the prefire token through CMesh__FindAnimationIndexByName, and dispatches animation vfunc byte offset +0xf0 when the animation index exists. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact owning source method, concrete CMonitor/CGroundVehicle/profile layouts, runtime firing animation behavior, BEA patching, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("prefire-animation", "cgroundvehicle-vtable-slot", "animation-dispatch")
        ),
        new Target(
            "0x005078f0",
            "CMonitor__UpdateTrackedRenderPair",
            "void __thiscall CMonitor__UpdateTrackedRenderPair(void * this, int update_projected_volume)",
            "Wave1187 static read-back: CMonitor tracked-render pair helper called by CMonitor__UpdateMovementTransitionAndEffects at 0x00410c81 and CBattleEngineWalkerPart__Move at 0x004137a6; RET 0x4 preserves one explicit update_projected_volume stack flag after ECX. The body walks two tracked render slots at this+0x18/+0x20, calls owner vfunc byte offset +300 to refresh transform state, copies basis data into linked render objects, and when the flag is nonzero applies optional projected-volume orientation data from owner+0xa0/+0x5c before marking the render object at +0xa0. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact monitor/render/projected-volume layouts, exact source-body identity, runtime render behavior, BEA patching, rebuild parity, and no-noticeable-difference parity remain separate proof.",
            withCommon("tracked-render-pair", "projected-volume", "walkerpart-callee")
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
            throw new IllegalStateException("Wave1187 CMonitor normalization failed: missing=" + missing + " bad=" + bad);
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
