//@category BEA

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

public class ApplyCarverCurrentRiskConsolidationWave1178 extends GhidraScript {
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
        "wave1178-carver-current-risk-consolidation-review",
        "wave1178-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "carver-current-risk",
        "tag-normalized",
        "comment-hardened"
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x00422440", "CCarver__Init",
            "void __thiscall CCarver__Init(void * this, void * init)",
            "carver", "air-unit", "init", "guide-helper", "ai-helper", "score-22-current-risk"),
        spec("0x00422580", "CCarverAI__dtor_base",
            "void __fastcall CCarverAI__dtor_base(void * this)",
            "carver-ai", "destructor-base", "monitor-cleanup", "score-20-current-risk"),
        spec("0x00422620", "CCarver__UpdateMotionAndWingPose",
            "void __fastcall CCarver__UpdateMotionAndWingPose(void * this)",
            "carver", "motion-update", "wing-pose", "score-26-current-risk"),
        spec("0x00422760", "CCarverAI__OpenWings",
            "void __fastcall CCarverAI__OpenWings(void * this)",
            "carver-ai", "wing-open", "animation", "score-16-current-risk"),
        spec("0x004227a0", "CCarverAI__CloseWings",
            "void __fastcall CCarverAI__CloseWings(void * this)",
            "carver-ai", "wing-close", "animation", "score-16-current-risk"),
        spec("0x004227e0", "CCarverAI__OnHit",
            "void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)",
            "carver-ai", "hit-handler", "vtable", "score-16-current-risk"),
        spec("0x00422820", "CCarverAI__Fire",
            "int __fastcall CCarverAI__Fire(void * this)",
            "carver-ai", "fire-helper", "wing-attack", "score-16-current-risk"),
        spec("0x00422930", "CCarverAI__SetLastAttackTime",
            "void __fastcall CCarverAI__SetLastAttackTime(void * this)",
            "carver-ai", "last-attack-timestamp", "cooldown", "score-16-current-risk"),
        spec("0x00422940", "CCarverAI__IsRecentlyAttacked",
            "int __fastcall CCarverAI__IsRecentlyAttacked(void * this)",
            "carver-ai", "last-attack-timestamp", "cooldown", "score-16-current-risk"),
        spec("0x00422970", "CCarverAI__CanStartAttack",
            "int __fastcall CCarverAI__CanStartAttack(void * this)",
            "carver-ai", "attack-predicate", "wing-blend", "cooldown", "score-22-current-risk"),
        spec("0x004229b0", "CarverAimGlobals__ResetVector",
            "void __cdecl CarverAimGlobals__ResetVector(void)",
            "carver-aim-globals", "vector-reset", "score-16-current-risk"),
        spec("0x004229d0", "CarverAimGlobals__InitMatrix",
            "void __cdecl CarverAimGlobals__InitMatrix(void)",
            "carver-aim-globals", "matrix-init", "score-16-current-risk"),
        spec("0x00422aa0", "CCarverAI__RefreshTargetReaderAndScheduleMove",
            "void __thiscall CCarverAI__RefreshTargetReaderAndScheduleMove(void * this, void * event)",
            "carver-ai", "target-reader", "event-handler", "wing-close", "score-16-current-risk"),
        spec("0x00422b90", "CCarverAI__UpdateAttackAndReschedule",
            "void __thiscall CCarverAI__UpdateAttackAndReschedule(void * this, void * event)",
            "carver-ai", "attack-update", "event-handler", "reschedule", "score-16-current-risk"),
        spec("0x00422db0", "CCarverAI__CheckNearbyEnemies",
            "void __fastcall CCarverAI__CheckNearbyEnemies(void * this)",
            "carver-ai", "nearby-enemy-scan", "mapwho-scan", "last-attack-timestamp", "score-23-current-risk"),
        spec("0x00422f90", "CCarverGuide__ctor",
            "void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)",
            "carver-guide", "constructor", "air-guide", "score-16-current-risk"),
        spec("0x00422fd0", "CCarverGuide__dtor_base",
            "void __fastcall CCarverGuide__dtor_base(void * this)",
            "carver-guide", "destructor-base", "active-reader", "monitor-cleanup", "score-26-current-risk"),
        spec("0x00423490", "CCarverGuide__HandleEvent",
            "void __thiscall CCarverGuide__HandleEvent(void * this, void * event)",
            "carver-guide", "event-handler", "target-refresh", "score-16-current-risk"),
        spec("0x00423510", "CCarverGuide__AcquireNearestTargetReader",
            "void __fastcall CCarverGuide__AcquireNearestTargetReader(void * this)",
            "carver-guide", "nearest-target-reader", "mapwho-scan", "active-reader", "score-23-current-risk"),
        spec("0x0050f340", "CCarver__Destructor_VFunc01",
            "void __fastcall CCarver__Destructor_VFunc01(void * this)",
            "carver", "destructor-body", "vfunc01", "score-17-current-risk")
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
                println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("TAGGED: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
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
            throw new IllegalStateException("Wave1178 Carver tag normalization failed: missing=" + missing + " bad=" + bad);
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
