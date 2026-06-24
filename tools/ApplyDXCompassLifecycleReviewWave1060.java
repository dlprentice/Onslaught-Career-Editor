// Normalize Wave1060 CDXCompass lifecycle/render-support review rows.
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

public class ApplyDXCompassLifecycleReviewWave1060 extends GhidraScript {
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
        "dxcompass-lifecycle-review-wave1060",
        "wave1060-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened",
        "signature-corrected",
        "dxcompass",
        "hud-render"
    };

    private static final Spec[] SPECS = {
        spec("0x00406040", "CDXCompass__GetTrackedPositionX",
            "double __fastcall CDXCompass__GetTrackedPositionX(void * context)",
            null,
            "tracked-position", "fpu-return", "context-0x4b0"),
        spec("0x0040c630", "CDXCompass__GetTrackedPositionY",
            "double __fastcall CDXCompass__GetTrackedPositionY(void * context)",
            null,
            "tracked-position", "fpu-return", "context-0x4b0"),
        spec("0x004270e0", "CDXCompass__InitMarkerArrays",
            "void __fastcall CDXCompass__InitMarkerArrays(void * this)",
            null,
            "marker-array", "init", "chud-owned"),
        spec("0x00427110", "CDXCompass__LoadTextures",
            "void __fastcall CDXCompass__LoadTextures(void * this)",
            null,
            "texture-load", "threat-flash", "damage-flash", "objective-marker"),
        spec("0x00427190", "CDXCompass__DestroyTextures",
            "void __fastcall CDXCompass__DestroyTextures(void * this)",
            null,
            "texture-release", "resource-lifetime", "chud-shutdown"),
        spec("0x00427200", "CDXCompass__Reset",
            "void __fastcall CDXCompass__Reset(void * this)",
            null,
            "reset", "state-flag", "chud-owned"),
        spec("0x00427210", "CDXCompass__Render",
            "void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)",
            "Signature/comment correction: main compass render path called from CDXCompass__RenderWorldSpaceOverlay with the compass object in ECX and a battle-engine/render context stack argument. The body draws threat, damage, bar-line, and objective compass sprites, calls tracked X/Y getters, toggles render state, and flushes CFastVB. Exact context layout, runtime HUD behavior, stack-local provenance, and rebuild parity remain unproven.",
            "compass-render", "battle-engine-context", "sprite-render"),
        spec("0x0053be40", "CDXCompass__Init",
            "void __fastcall CDXCompass__Init(void * this)",
            null,
            "resource-init", "ring-texture", "byte-sprite", "cvbuffer"),
        spec("0x0053c1d0", "CDXCompass__BuildRingGeometry",
            "void __cdecl CDXCompass__BuildRingGeometry(void * vertices, int textureWidth, int textureHeight, int segmentCount, int thicknessPercent, float uvScale)",
            null,
            "ring-geometry", "plain-helper", "vertex-strip")
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
            boolean needsComment = spec.comment != null && !spec.comment.equals(function.getComment());

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
                Set<String> tags = function == null ? new HashSet<String>() : tagNames(function);
                for (String tag : spec.tags) {
                    if (!tags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        verificationFailures++;
                    }
                }
                if (function != null && spec.comment != null && !spec.comment.equals(function.getComment())) {
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
            throw new IllegalStateException("Wave1060 tag normalization failed: missing=" + missing + " bad=" + bad);
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
