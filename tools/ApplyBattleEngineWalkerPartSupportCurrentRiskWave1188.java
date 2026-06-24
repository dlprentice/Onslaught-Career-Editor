//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyBattleEngineWalkerPartSupportCurrentRiskWave1188 extends GhidraScript {
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
        "wave1188-battleengine-walkerpart-support-current-risk-review",
        "wave1188-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "battleengine",
        "walkerpart",
        "source-identity-deferred",
        "exact-layout-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x00405a40",
            "CBattleEngine__dtor_base",
            "void __fastcall CBattleEngine__dtor_base(void * this)",
            "Wave1188 static read-back: CBattleEngine destructor-base cleanup installs BattleEngine vtables, drains particle-effect links at this+0x620, deletes owned vcall-managed set entries at this+0x284, destroys active-reader projectile/target sets at this+0x294 and this+0x2a4, releases walker/jet part objects at this+0x578/this+0x57c, clears parked primary/secondary reader state at this+0x5ec/this+0x5f4, removes monitored safe-pointer registrations, clears CSPtrSet members, and tail-calls CUnit__dtor_base. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact BattleEngine concrete layout, exact source-body identity, runtime cleanup ordering, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("destructor-cleanup", "active-reader-set-cleanup", "walker-jet-part-ownership")
        ),
        new Target(
            "0x00405f60",
            "CBattleEngine__scalar_deleting_dtor",
            "void * __thiscall CBattleEngine__scalar_deleting_dtor(void * this, byte flags)",
            "Wave1188 static read-back: CBattleEngine scalar-deleting destructor wrapper calls CBattleEngine__dtor_base, checks delete flag bit 0, optionally frees the object through CDXMemoryManager__Free, and returns this; DATA xref 0x005d89c8 anchors the wrapper in the saved metadata. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact source-body identity, allocator/runtime deletion behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("scalar-deleting-destructor", "vtable-data-ref", "allocator-delete-wrapper")
        ),
        new Target(
            "0x004063b0",
            "CBattleEngine__UpdateWeaponEffect",
            "void __fastcall CBattleEngine__UpdateWeaponEffect(void * this)",
            "Wave1188 static read-back: CBattleEngine weapon-effect helper called by CBattleEngine__HandleEvent at 0x0040c1db and 0x0040c27f. The body samples virtual getters at vtable offsets +0x40/+0xc0, allocates a 0x20 CLine-like effect object from BattleEngine.cpp line 0x1f5, writes squared range and timing/scalar fields, and submits the object through the nested manager at this+0x38 vfunc +0x24. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact effect-object layout, exact source-body identity, runtime weapon/effect behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("weapon-effect", "event-handler-callee", "effect-object-allocation")
        ),
        new Target(
            "0x00406460",
            "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
            "void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(void * this)",
            "Wave1188 static read-back: CBattleEngine primary/secondary reader swap helper called from CBattleEngine__Init at 0x00405863, CUnit__ProcessStateSwapAndDeathChecks at 0x00408153, CBattleEngine__Morph at 0x0040a75d, and CGeneralVolume__ResetAndSetActiveReader at 0x0040c724. The body branches on mode/state this+0x260 and latch this+0x5f0, swaps this+0x5ec with this+0x30, parks/restores the active reader through this+0x70/this+0x5f4, resets the multiplayer mech twenty times when gated, and refreshes influence-map tracking from the current reader. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact BattleEngine/reader/influence-map layouts, exact source-body identity, runtime morph/reader behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("reader-state-swap", "morph-callee", "influence-map-refresh")
        ),
        new Target(
            "0x00406fc0",
            "CBattleEngine__AddProjectile",
            "void __thiscall CBattleEngine__AddProjectile(void * this, void * target, float lifetime, int modeFlag)",
            "Wave1188 static read-back: CBattleEngine tracked projectile insertion helper called four times by CBattleEngine__UpdateAutoTargetSetAndFireProjectiles at 0x004068d9, 0x00406a51, 0x00406aae, and 0x00406d06. The body skips targets with byte flag target+0x2c bit 2, scans the tracked projectile active-reader set at this+0x294 to avoid duplicate targets, allocates a 0x14 active-reader entry from BattleEngine.cpp line 0x332, sets reader/expiry/modeFlag fields using DAT_00672fd0 plus lifetime, and appends via CSPtrSet__AddToTail. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact projectile-entry layout, exact source-body identity, runtime weapon/projectile targeting behavior, weapon_fire_breaks_stealth closure, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("tracked-projectile", "weapon-fire-callee", "active-reader-entry")
        ),
        new Target(
            "0x004080f0",
            "CGame__IsWalkerGroundedOrCollision",
            "bool __fastcall CGame__IsWalkerGroundedOrCollision(void * battleEngine)",
            "Wave1188 static read-back: BattleEngine grounded/collision predicate called from CGame__Update at 0x0046eb8d and CPlayer__ReceiveButtonAction at 0x004d31d3. The body requires walker/state value battleEngine+0x260 == 2, then returns true when the BattleEngine vfunc at +0x10c reports contact or HeightDelta__Below015_D4 succeeds. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact mode enum naming, concrete BattleEngine/collision layout, runtime movement/input behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("grounded-collision-predicate", "game-update-callee", "player-input-callee")
        ),
        new Target(
            "0x004145d0",
            "CBattleEngineWalkerPart__GetWeaponPhysicsName",
            "char * __thiscall CBattleEngineWalkerPart__GetWeaponPhysicsName(void * this)",
            "Wave1188 static read-back: CBattleEngineWalkerPart weapon-physics-name adapter called by CBattleEngine__GetWeaponPhysicsName at 0x0040c57f. The body resolves the current weapon through CBattleEngineWalkerPart__GetCurrentWeapon, then returns the first name pointer through the weapon-data pointer at currentWeapon+0xa4 when present. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact CWeaponData concrete layout, exact source-body identity, runtime weapon/resource lookup behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("weapon-physics-name", "walkerpart-weapon-adapter", "source-parity")
        ),
        new Target(
            "0x00414610",
            "CBattleEngineWalkerPart__GetWeaponIconName",
            "char * __thiscall CBattleEngineWalkerPart__GetWeaponIconName(void * this)",
            "Wave1188 static read-back: CBattleEngineWalkerPart weapon-icon-name adapter called by CBattleEngine__GetWeaponIconName at 0x0040c59f. The body resolves the current weapon through CBattleEngineWalkerPart__GetCurrentWeapon, then returns the icon/name-like pointer at weapon-data+0x38 through the weapon-data pointer at currentWeapon+0xa4 when present. Static retail Ghidra metadata/xref/decompile/instruction evidence only; exact CWeaponData concrete layout, exact source-body identity, runtime weapon/resource lookup behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            withCommon("weapon-icon-name", "walkerpart-weapon-adapter", "source-parity")
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
            throw new IllegalStateException("Wave1188 BattleEngine/WalkerPart normalization failed: missing=" + missing + " bad=" + bad);
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
