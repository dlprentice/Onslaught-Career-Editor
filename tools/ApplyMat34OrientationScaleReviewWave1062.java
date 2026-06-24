// Normalize Wave1062 Mat34 orientation/scale review rows.
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

public class ApplyMat34OrientationScaleReviewWave1062 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final List<String> tags;

        Spec(String address, String name, String signature, String comment, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = Arrays.asList(tags);
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "mat34-orientation-scale-review-wave1062",
        "wave1062-readback-verified",
        "retail-binary-evidence",
        "comment-normalized",
        "tag-normalized",
        "mat34",
        "matrix-basis"
    };

    private static final Spec[] SPECS = {
        spec("0x0040d1f0", "Mat34__SetFromEulerAngles",
            "void __thiscall Mat34__SetFromEulerAngles(void * this, float angle0, float angle1, float angle2)",
            "Wave1062 comment/tag normalization: Mat34-style basis builder evaluates cos/sin for three stack float angles, writes basis floats through offsets +0x0..+0x28, and returns with RET 0x0c. Fresh xrefs include CBattleEngine__GetLaunchPosition, OID__CanFireAtTarget_BallisticArcA, CMCComponent__VFunc_04_UpdateTurretBarrelTransform, CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0, and CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0. Static retail evidence only; exact source identity, angle order/convention, concrete Mat34 layout, runtime transform behavior, local names, BEA patching, and rebuild parity remain separate proof.",
            "euler", "basis-builder", "angle-floats"),
        spec("0x0040d2c0", "Mat34__TransformVec3ByBasisToOut",
            "void __thiscall Mat34__TransformVec3ByBasisToOut(void * this, void * outVec, void * vec)",
            "Wave1062 comment/tag normalization: basis-transform helper multiplies a Vec3-style input by three Mat34 basis rows at offsets +0x0/+0x10/+0x20, writes outVec lanes, and returns with RET 0x8. Fresh xrefs include CBattleEngine__GetLaunchPosition, CMCMech__BuildInterpolatedPoseAndAnchor, CVBufTexture__RenderDynamicUnitPass, CMCBuggy__UpdateWheel, CParticle/CPDSimpleSprite/CDXEngine render paths, CSquadNormal formation helpers, and CMeshCollisionVolume__VFunc_04_004ad830. Static retail evidence only; translation semantics, exact Mat34/Vec3 layouts, exact source identity, runtime transform/render/formation behavior, local names, BEA patching, and rebuild parity remain separate proof.",
            "vec3-transform", "basis-transform", "translation-unproven")
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
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
        int commentUpdated = 0;
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
            boolean needsComment = !spec.comment.equals(function.getComment());

            if (missingTags.isEmpty() && !needsComment) {
                println("SKIP: " + spec.address + " " + spec.name + " tags/comment already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (needsComment) {
                commentUpdated++;
            }
            if (dryRun) {
                if (!missingTags.isEmpty()) {
                    println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                }
                if (needsComment) {
                    println("WOULD_COMMENT: " + spec.address + " " + spec.name);
                }
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            if (needsComment) {
                function.setComment(spec.comment);
            }
            println("UPDATED: " + spec.address + " " + spec.name + " tags=+" + String.join(",", missingTags) + " comment=" + needsComment);
            updated++;
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
                if (!spec.comment.equals(function.getComment())) {
                    println("VERIFY_COMMENT_FAIL: " + spec.address);
                    verificationFailures++;
                }
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " tags_added=" + tagsAdded
            + " comment_updated=" + commentUpdated
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1062 Mat34 normalization failed: missing=" + missing + " bad=" + bad);
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
