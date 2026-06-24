// Tag-normalize Wave1058 CUnitAI/GeneralVolume deploy-tracking residual review rows.
// @category BEA

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

public class ApplyCUnitAIDeployTrackingResidualWave1058 extends GhidraScript {
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
        "cunitai-deploy-tracking-residual-review-wave1058",
        "wave1058-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened"
    };

    private static final Spec[] SPECS = {
        spec("0x004247a0", "CGeneralVolume__InitRandomizedVelocityOffsets",
            "void __thiscall CGeneralVolume__InitRandomizedVelocityOffsets(void * this, int randomRange)",
            "generalvolume", "randomized-offsets", "deploy-tracking-context"),
        spec("0x00424a20", "CUnitAI__UpdateDeployAimAndScheduleEvent",
            "void __fastcall CUnitAI__UpdateDeployAimAndScheduleEvent(void * this)",
            "unit-ai", "deploy-tracking", "deploy-animation", "event-scheduler"),
        spec("0x00424be0", "CUnitAI__AdvanceDeployAnimationPhase",
            "void __fastcall CUnitAI__AdvanceDeployAnimationPhase(void * this)",
            "unit-ai", "deploy-tracking", "deploy-animation", "phase-advance"),
        spec("0x00424ca0", "CUnitAI__UpdateDeployTrackingTransformTowardTarget",
            "void __fastcall CUnitAI__UpdateDeployTrackingTransformTowardTarget(void * this)",
            "unit-ai", "deploy-tracking", "target-tracking", "transform-update"),
        spec("0x004250f0", "CUnitAI__DecayDeployTrackingTransformToNeutral",
            "void __fastcall CUnitAI__DecayDeployTrackingTransformToNeutral(void * this)",
            "unit-ai", "deploy-tracking", "neutral-decay", "transform-update"),
        spec("0x004244b0", "CCockpit__ctor",
            "void * __thiscall CCockpit__ctor(void * this, void * battleEngine)",
            "cockpit", "constructor", "battleengine-init-context"),
        spec("0x00424920", "CGeneralVolume__BeginFlyToWalkTransition",
            "void __fastcall CGeneralVolume__BeginFlyToWalkTransition(void * this)",
            "generalvolume", "morph-transition", "flytowalk"),
        spec("0x00424990", "CGeneralVolume__BeginWalkToFlyTransition",
            "void __fastcall CGeneralVolume__BeginWalkToFlyTransition(void * this)",
            "generalvolume", "morph-transition", "walktofly"),
        spec("0x0040a580", "CBattleEngine__Morph",
            "void __fastcall CBattleEngine__Morph(void * battleEngine)",
            "battleengine", "morph-transition", "source-shape-evidence"),
        spec("0x0040eeb0", "CBattleEngine__FinishedPlayingCurrentAnimation",
            "int __thiscall CBattleEngine__FinishedPlayingCurrentAnimation(void * this)",
            "battleengine", "animation-transition", "source-shape-evidence"),
        spec("0x00425760", "Mat34__OrthonormalizeAxes",
            "void __fastcall Mat34__OrthonormalizeAxes(void * mat34)",
            "math", "mat34", "owner-neutral")
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

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
            String actualName = function.getName();
            if (!spec.name.equals(actualName)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + actualName);
                specBad = true;
            }

            String actualSignature = function.getSignature().toString();
            if (!spec.signature.equals(actualSignature)) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + actualSignature);
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
                println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("TAGGED: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
            updated++;
        }

        if (!dryRun) {
            int verificationFailures = 0;
            for (Spec spec : SPECS) {
                Address address = toAddr(spec.address);
                Function function = functionManager.getFunctionAt(address);
                Set<String> tags = function == null ? new HashSet<String>() : tagNames(function);
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
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1058 tag normalization failed: missing=" + missing + " bad=" + bad);
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
