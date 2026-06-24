//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyGillMGroundUnitAIMotionEffectsCurrentRiskWave1199 extends GhidraScript {
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
        "wave1199-gillm-groundunit-ai-motion-effects-current-risk-review",
        "wave1199-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "score16-19",
        "gillm-groundunit-ai-motion-effects",
        "source-identity-deferred",
        "exact-layout-deferred",
        "runtime-behavior-deferred",
        "rebuild-grade-static-contract",
        "no-noticeable-difference-boundary",
        "comment-hardened",
        "signature-hardened",
        "tag-normalized"
    };

    private static final Target[] TARGETS = {
        new Target(
            "0x0049fdb0",
            "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
            "void __fastcall SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0(void * this)",
            "Wave1199 static current-risk read-back: score19 shared ground-unit/GillM-adjacent vtable slot 71 mesh break-effect dispatcher retained from Wave437 with normalized rebuild-grade tags. Fresh DATA refs at 0x005e3190, 0x005e10fc, 0x005e0c4c, and 0x005e07a0 cover sampled ground-unit vtables; body searches the Generic Mesh node, iterates child mesh parts with flag +0x8c == 1, creates break effects, anchors them through CMCMech__BuildInterpolatedPoseAndAnchor, and randomizes effect velocity. Static rebuild contract only; exact concrete owner coverage, mesh-effect runtime behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"shared-ground-unit", "mesh-effects", "vtable-slot-71", "score19"}
        ),
        new Target(
            "0x0047a900",
            "CGillMHeadAI__AdvanceOpenAttackCloseState",
            "int __fastcall CGillMHeadAI__AdvanceOpenAttackCloseState(void * this)",
            "Wave1199 static current-risk read-back: score18 GillMHeadAI open/attack/close animation-state helper retained from Wave1001 with normalized rebuild-grade tags. Fresh DATA ref 0x005e42e4 in the GillMHeadAI pointer table keeps the this-only fastcall contract; body compares current animation against open, attack, close, and idle tokens, checks CUnit__HasAnyLinkedUnitBeforeTargetTimeout before close transition, and requests shared animation playback through SharedUnitAnimation__PlayAnimationByNameIfPresent. Static rebuild contract only; exact source method name, concrete AI layout, runtime animation behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillmheadai", "animation-state", "gillmhead-ai", "score18"}
        ),
        new Target(
            "0x0047a730",
            "CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730",
            "void __thiscall CGillMHeadAIVFunc__ForwardArgAndSetIdleAnimation_0047a730(void * this, void * arg)",
            "Wave1199 static current-risk read-back: score17 GillMHeadAI-adjacent vtable forwarder retained from Wave1086 with normalized rebuild-grade tags. Fresh DATA ref 0x005e421c keeps the thiscall/arg RET 0x4 contract; body forwards arg to 0x00427b80, then calls CComplexThing__SetAnimMode-like helper 0x004f4560 with GillMHead idle string token 0x0062ca48 and two boolean constants. Static rebuild contract only; exact source virtual name, concrete owner layout, runtime animation behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillmhead-ai-vfunc", "idle-animation", "shared-unit-vtable", "score17"}
        ),
        new Target(
            "0x0047a9c0",
            "CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0",
            "void __thiscall CGillMHeadAIVFunc__ForwardNonMode4ToEngagementSetter_0047a9c0(void * this, int mode)",
            "Wave1199 static current-risk read-back: score17 GillMHeadAI-adjacent mode forwarder retained from Wave1086 with normalized rebuild-grade tags. Fresh DATA ref 0x005e42d0 keeps the thiscall/mode RET 0x4 contract; body skips mode value 4 and otherwise forwards the mode to CUnit__SetEngagementModeAndMaybeClearTargetReader at 0x004fdcb0. Static rebuild contract only; exact source virtual name, concrete owner layout, runtime engagement behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillmhead-ai-vfunc", "mode-forwarder", "shared-unit-vtable", "score17"}
        ),
        new Target(
            "0x00479b60",
            "CGillM__InitGillMAIComponent",
            "void __thiscall CGillM__InitGillMAIComponent(void * this, void * init_data)",
            "Wave1199 static current-risk read-back: score16 CGillM AI component initializer retained from Wave389 with normalized rebuild-grade tags. Fresh DATA ref 0x005e0d08 keeps the CGillM vtable slot 118 contract; body allocates a 0x60-byte object with GillM.cpp line 0x38 evidence, initializes it through CWarspite__Init, installs CGillMAI RTTI vtable 0x005dbcb4, and stores the component at this+0x13c. Static rebuild contract only; exact source method name, concrete AI layout, runtime behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillm", "cgillmai", "component-init", "warspite-base", "score16"}
        ),
        new Target(
            "0x00479bf0",
            "CGillMAI__ScalarDeletingDestructor",
            "void * __thiscall CGillMAI__ScalarDeletingDestructor(void * this, byte flags)",
            "Wave1199 static current-risk read-back: score16 CGillMAI scalar deleting destructor retained from Wave389 with normalized rebuild-grade tags. Fresh DATA ref 0x005dbcb8 keeps the CGillMAI RTTI vtable slot 1 wrapper contract; body calls CGillMAI__Destructor, frees this when flags bit 0 is set, and returns this. Static rebuild contract only; exact source destructor identity, concrete AI layout, runtime destruction behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillmai", "destructor", "scalar-deleting-dtor", "score16"}
        ),
        new Target(
            "0x00479cb0",
            "CGillM__InitTerrainGuideComponent",
            "void __fastcall CGillM__InitTerrainGuideComponent(void * this)",
            "Wave1199 static current-risk read-back: score16 CGillM terrain-guide component initializer retained from Wave389/Wave544 with normalized rebuild-grade tags. Fresh DATA ref 0x005e0d0c keeps the CGillM vtable slot 119 contract; body allocates a 0x20-byte object with GillM.cpp line 0x3e evidence, initializes it through CTerrainGuide__ctor, and stores the result at this+0x208. Static rebuild contract only; exact source method name, concrete terrain-guide layout, runtime guidance behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillm", "terrain-guide", "component-init", "score16"}
        ),
        new Target(
            "0x00479d10",
            "CGillM__UpdateGroundedVerticalDrift",
            "void __fastcall CGillM__UpdateGroundedVerticalDrift(void * this)",
            "Wave1199 static current-risk read-back: score16 CGillM grounded vertical-drift helper retained from Wave389 with normalized rebuild-grade tags. Fresh DATA ref 0x005e0c38 keeps the CGillM vtable slot 66 contract; body uses +0x274 grounded state, +0x244 mode/state, static-shadow height sampling, vertical drift fields +0x84/+0xcc, and repeated shared helper dispatch at 0x0049fc10. Static rebuild contract only; exact source method name, concrete CGillM layout, runtime movement behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillm", "grounded-state", "vertical-drift", "score16"}
        ),
        new Target(
            "0x00479db0",
            "CGillM__TriggerRandomArmHitAnimationIfReady",
            "void __fastcall CGillM__TriggerRandomArmHitAnimationIfReady(void * this)",
            "Wave1199 static current-risk read-back: score16 CGillM random arm-hit animation helper retained from Wave389 with normalized rebuild-grade tags. Fresh call ref 0x0047a392 and decompile evidence keep the this-only fastcall contract; body gates on cooldown field +0x26c, walks the child/component list at +0x19c, selects Gill_M_Left_Arm or Gill_M_Right_Arm from the random result, calls the matching hit-animation helper, and resets the cooldown timer. Static rebuild contract only; exact source method name, arm-list layout, runtime animation behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillm", "arm-hit-animation", "random-animation", "score16"}
        ),
        new Target(
            "0x0047a160",
            "CGillM__StartState1WithStoredMotionVector",
            "void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)",
            "Wave1199 static current-risk read-back: score16 CGillM stored-motion-vector state transition retained from Wave409 with normalized rebuild-grade tags. Fresh DATA ref 0x005e0cc0 keeps the CGillM vtable slot 100 contract; body skips when state field +0x244 is already 1 or 2, copies the stored four-dword motion vector at +0x278 into a virtual dispatch at vtable +0xf4 with a zero flag, then sets +0x244 to 1. Static rebuild contract only; exact source virtual name, concrete CGillM layout, runtime movement behavior, BEA patching, rebuild parity, and clean-room/no-noticeable-difference parity remain separate proof.",
            new String[] {"cgillm", "motion-vector", "state-transition", "score16"}
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
            requiredTags.addAll(Arrays.asList(target.tags));
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
                    Set<String> expectedTags = new HashSet<>(Arrays.asList(COMMON_TAGS));
                    expectedTags.addAll(Arrays.asList(target.tags));
                    for (String tag : expectedTags) {
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
            throw new IllegalStateException("Wave1199 GillM/GroundUnit normalization failed: missing=" + missing + " bad=" + bad);
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
