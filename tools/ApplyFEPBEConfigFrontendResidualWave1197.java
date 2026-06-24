//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyFEPBEConfigFrontendResidualWave1197 extends GhidraScript {
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
        "wave1197-fepbeconfig-frontend-residual-current-risk-review",
        "wave1197-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score15-16",
        "fepbeconfig-frontend-residual",
        "frontend",
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
            "0x0044fa90",
            "CFEPBEConfig__Init",
            "void __thiscall CFEPBEConfig__Init(void * this)",
            "Wave1197 static current-risk read-back: score16 FEPBEConfig frontend residual retained from Wave367/Wave999 with normalized rebuild-grade tags. Fresh xref keeps the CFEPBEConfig vtable/init DATA ref at 0x005dba3c; fresh body evidence keeps the corrected SEH-prologue boundary at 0x0044fa90, not the old mid-prologue 0x0044fa93 note. Static contract: initializes CFEPBEConfig page/config state, optional preview mesh/animation state, reads data\\WorldHeaders.dat through CDXMemBuffer, traces beconf::init() 0-5 debug stages, calls the load vfunc for each header, and ends before CFEPBEConfig__Cleanup. Static rebuild contract only; exact source-body identity, concrete FEPBEConfig/config-entry/memory-buffer layouts, runtime frontend/config loading behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x0044eb30",
            "CFEPMultiplayerStart__SetConfigDescriptionByIndex",
            "void __cdecl CFEPMultiplayerStart__SetConfigDescriptionByIndex(int config_index)",
            "Wave1197 static current-risk read-back: score15 FEPBEConfig/frontend residual retained from Wave367/Wave999 with normalized rebuild-grade tags. Fresh xref keeps the call from CFEPMultiplayerStart__Render at 0x0051efa8; fresh body evidence keeps the cdecl config_index signature. Static contract: walks the selected BattleEngine config list keyed by DAT_0089d94c, selects config_index, matches the config name against the global config/profile list at DAT_006602a0, maps matched type ids 1..5 to frontend text ids, and falls back through Text__AsciiToWideScratch(\"Unknown Configuration\"). Static rebuild contract only; exact source-body identity, concrete config/list/profile/string-table layouts, runtime frontend text behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x0044f530",
            "CFEPBEConfig__PlayWeaponSound",
            "void __cdecl CFEPBEConfig__PlayWeaponSound(void * config, int weapon_index)",
            "Wave1197 static current-risk read-back: score15 FEPBEConfig frontend residual retained from Wave367/Wave999 with normalized rebuild-grade tags. Fresh xref keeps the call from CFEPBEConfig__Render at 0x00451044; fresh body evidence keeps the cdecl config/weapon_index signature. Static contract: resolves the selected config entry through DAT_0089da34/DAT_0089d94c, matches the config record against DAT_006602a0, selects the primary weapon-name path using record fields +0x40/+0x48 and the shared weapon-name table at DAT_008553e8, returns CText__GetStringById using weapon-record field +0x0f, and falls back through Text__AsciiToWideScratch(\"Unknown Weapon\"). Static rebuild contract only; exact source-body identity, concrete FEPBEConfig/config/weapon/list/text/audio layouts, runtime frontend audio/text behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
        ),
        new Target(
            "0x0044f830",
            "CFEPBEConfig__PlayWeaponSoundAlt",
            "void __cdecl CFEPBEConfig__PlayWeaponSoundAlt(void * config, int weapon_index)",
            "Wave1197 static current-risk read-back: score15 FEPBEConfig frontend residual retained from Wave367/Wave999 with normalized rebuild-grade tags. Fresh xref keeps the call from CFEPBEConfig__Render at 0x0045117f; fresh body evidence keeps the cdecl config/weapon_index signature. Static contract: resolves the same selected config/list path as the primary helper, then uses the alternate weapon-name list at matched record fields +0x50/+0x58 with the shared weapon-name table at DAT_008553e8, returns CText__GetStringById using weapon-record field +0x0f, and falls back through Text__AsciiToWideScratch(\"Unknown Weapon\"). Static rebuild contract only; exact source-body identity, concrete FEPBEConfig/config/alternate-weapon/list/text/audio layouts, runtime frontend audio/text behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof."
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
            throw new IllegalStateException("Wave1197 FEPBEConfig frontend residual normalization failed: missing=" + missing + " bad=" + bad);
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
