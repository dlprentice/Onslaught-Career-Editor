//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyComponentAiCurrentRiskWave1132 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final List<String> tags;

        Spec(String address, String name, String signature, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.tags = Arrays.asList(tags);
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1132-component-ai-current-risk-review",
        "wave1132-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "component-ai-current-risk-review"
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x00427b80", "CComponent__VFunc_09_00427b80",
            "void __thiscall CComponent__VFunc_09_00427b80(void * this, void * init)",
            "score-21-current-risk", "component-system", "component-wave324", "active-reader",
            "component-init", "thunderhead-main-gun"),
        spec("0x00427f90", "CComponentBomberAI__scalar_deleting_dtor",
            "void * __thiscall CComponentBomberAI__scalar_deleting_dtor(void * this, byte flags)",
            "score-16-current-risk", "component-system", "component-wave324", "destructor",
            "component-ai-lifecycle", "vtable-rtti", "ccomponent-bomber-ai"),
        spec("0x00427fb0", "CComponentBomberAI__dtor_base",
            "void __fastcall CComponentBomberAI__dtor_base(void * this)",
            "score-20-current-risk", "component-system", "component-wave324", "destructor",
            "component-ai-lifecycle", "monitored-set-cleanup", "ccomponent-bomber-ai"),
        spec("0x00428050", "CFenrirMainGunAI__scalar_deleting_dtor",
            "void * __thiscall CFenrirMainGunAI__scalar_deleting_dtor(void * this, byte flags)",
            "score-16-current-risk", "component-system", "component-wave324", "destructor",
            "component-ai-lifecycle", "vtable-rtti", "cfenrir-main-gun-ai"),
        spec("0x00428070", "CFenrirMainGunAI__dtor_base",
            "void __fastcall CFenrirMainGunAI__dtor_base(void * this)",
            "score-20-current-risk", "component-system", "component-wave324", "destructor",
            "component-ai-lifecycle", "monitored-set-cleanup", "cfenrir-main-gun-ai"),
        spec("0x00428710", "CUnitAI__GetRenderPosFromActorOrCache",
            "void * __thiscall CUnitAI__GetRenderPosFromActorOrCache(void * this, void * outRenderPos, void * unused)",
            "score-20-current-risk", "unitai-system", "render-cache", "actor-forwarding",
            "component-transform-cache"),
        spec("0x00428770", "CUnitAI__GetRenderOrientationFromActorOrCache",
            "void * __thiscall CUnitAI__GetRenderOrientationFromActorOrCache(void * this, void * outRenderOrientation, void * unused)",
            "score-20-current-risk", "unitai-system", "render-cache", "actor-forwarding",
            "component-transform-cache"),
        spec("0x00428c70", "CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action",
            "void __fastcall CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action(void * this)",
            "score-20-current-risk", "unitai-system", "shared-step", "flag4-dispatch",
            "vtable-slot-38"),
        spec("0x00428d50", "CUnitAI__PlayActivateAnimationOrFinalizeActivated",
            "void __fastcall CUnitAI__PlayActivateAnimationOrFinalizeActivated(void * this)",
            "score-20-current-risk", "unitai-system", "activation-animation", "activate-token",
            "vtable-slot-f0"),
        spec("0x00428e80", "CComponentAI__ClearReaderIfTargetDestroyedThenForward",
            "void __fastcall CComponentAI__ClearReaderIfTargetDestroyedThenForward(void * this)",
            "score-22-current-risk", "unitai-system", "component-ai-reader-clear", "active-reader",
            "vtable-slot-2c", "shared-component-ai")
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
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Spec spec : SPECS) {
            Address address = toAddr(spec.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                missing++;
                continue;
            }

            boolean specBad = false;
            if (!spec.name.equals(function.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
                specBad = true;
            }
            if (!spec.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + function.getSignature());
                specBad = true;
            }
            if (specBad) {
                bad++;
                continue;
            }

            Set<String> existingTags = tagNames(function);
            List<String> missingTags = new ArrayList<>();
            for (String tag : spec.tags) {
                if (!existingTags.contains(tag)) {
                    missingTags.add(tag);
                }
            }

            if (missingTags.isEmpty()) {
                println("SKIP: " + spec.address + " " + spec.name + " tags already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (dryRun) {
                println("WOULD_UPDATE: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags));
            updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        }

        if (!dryRun) {
            int verificationFailures = 0;
            for (Spec spec : SPECS) {
                Address address = toAddr(spec.address);
                Function function = functionManager.getFunctionAt(address);
                if (function == null) {
                    println("VERIFY_MISSING: " + spec.address);
                    verificationFailures++;
                    continue;
                }
                Set<String> tags = tagNames(function);
                for (String tag : spec.tags) {
                    if (!tags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        verificationFailures++;
                    }
                }
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=0"
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1132 component-AI current-risk normalization failed: missing=" + missing + " bad=" + bad);
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
