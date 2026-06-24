//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyRoundRocketProjectileVfuncResidualWave1196 extends GhidraScript {
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
        "wave1196-round-rocket-projectile-vfunc-residual-current-risk-review",
        "wave1196-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score17",
        "round-rocket-projectile-vfunc-residual",
        "projectile",
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
            "0x004d8ae0",
            "VFuncSlot_39_004d8ae0",
            "void __thiscall VFuncSlot_39_004d8ae0(void * this, void * other_thing, void * collision_report)",
            "Wave1196 static current-risk read-back: score17 shared CRound/CMissile projectile vfunc residual retained from Wave1011 with normalized rebuild-grade tags. Fresh xrefs keep DATA refs from CRound vtable slot 39 at 0x005de8c8 and CMissile-style vtable slot 39 at 0x005e3c40; fresh body evidence keeps the RET 0x8 signature. Static contract: calls CComplexThing__Hit(this, other_thing, collision_report), can call CBattleEngine__Rearm using round-config data, calls CUnit__PlayImpactSoundForMaterials, calls CRound__UpdateEffectTransformByMode_004d9f30, schedules an event through CEventManager__AddEvent_AtTime, and clears this+0x124 on the event path. Static rebuild contract only; exact source virtual name, exact hit/collision semantics, concrete CRound/CMissile/target/collision-report layouts, runtime projectile behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x004d8e40",
            "VFuncSlot_66_004d8e40",
            "void __fastcall VFuncSlot_66_004d8e40(void * this)",
            "Wave1196 static current-risk read-back: score17 shared CRound/CMissile projectile vfunc residual retained from Wave1012 with normalized rebuild-grade tags. Fresh xrefs keep DATA refs from CRound vtable slot 66 at 0x005de934 and CMissile-style vtable slot 66 at 0x005e3cac; fresh body evidence keeps the register-only signature. Static contract: touches CRound/CMissile-style fields this+0xe0/+0xe4/+0xe8/+0xec/+0xf0/+0x120, clears particle/effect links, removes active-reader state, calls Vec3__SetXYZ, CGeneralVolume__OffsetPointByForwardScaled, CUnit__PushTransformHistoryAndSetCurrent, and CRound__UpdateEffectTransformByMode_004d9f30 before the separate slot-0 body. Static rebuild contract only; exact source virtual name, concrete CRound/CMissile/effect/reader layouts, runtime projectile/effect/reader semantics, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x004d9910",
            "VFuncSlot_00_004d9910",
            "void __thiscall VFuncSlot_00_004d9910(void * this, void * event_record)",
            "Wave1196 static current-risk read-back: score17 shared CRound/CMissile projectile vfunc residual retained from Wave1012 with normalized rebuild-grade tags. Fresh xrefs keep DATA refs from CRound vtable base slot 0 at 0x005de82c and CMissile-style vtable base slot 0 at 0x005e3ba4; fresh body evidence keeps the SEH-framed RET 0x4 event-record signature. Static contract: switches on the word at event_record+4 and routes projectile dispatch through CRound__SelectBestTargetReaderAndSyncAimState, CRound__SpawnConfiguredProjectile, CEngine__InitRoundLaunchStateDefaults, CRound__UpdateEffectTransformByMode_004d9f30, CEventManager__AddEvent_AtTime, CActor__HandleEvent, and a CRound-style virtual slot +0xc8 path. Static rebuild contract only; exact source virtual name, event/record schema, concrete CRound/CMissile layouts, runtime projectile dispatch behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x004d8040",
            "CRocket__VFunc_22_CreateBigRocketEngineEffects",
            "void __fastcall CRocket__VFunc_22_CreateBigRocketEngineEffects(void * this)",
            "Wave1196 static current-risk read-back: score17 CRocket projectile vfunc residual retained from Wave492 with normalized rebuild-grade tags. Fresh xrefs keep the CRocket vtable slot 22 DATA ref at 0x005dd4b0; fresh body evidence keeps the register-only signature. Static contract: sets this+0xe4, resolves Big Rocket Engine Effect through CParticleSet__FindByNameAndTrackLinkSlot, then creates four particle effects through CParticleManager__CreateEffect using output handle slots starting at this+0xec and global effect-position/vector payload 0x0083cc48..0x0083cc54. Static rebuild contract only; exact source virtual name, concrete CRocket/particle-handle/effect payload layouts, runtime engine-effect behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
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
            throw new IllegalStateException("Wave1196 Round/Rocket projectile vfunc residual normalization failed: missing=" + missing + " bad=" + bad);
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
