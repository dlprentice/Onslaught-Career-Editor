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

public class ApplyCDXEngineFrameRenderSpineReviewWave1094 extends GhidraScript {
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
        "cdxengine-frame-render-spine-review-wave1094",
        "wave1094-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "tag-normalized",
        "frame-render-spine"
    };

    private static Spec spec(String address, String name, String signature, String comment, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, comment, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x0053e220", "CDXEngine__PreRender",
            "int __fastcall CDXEngine__PreRender(void * this, void * viewport)",
            "Wave1094 static read-back: CDXEngine frame pre-render helper. CGame__Render calls this at 0x0046e5c3 before the per-viewpoint CDXEngine__Render calls; the body clears/initializes per-frame engine state, applies viewport state, and prepares counters/state consumed by Render/PostRender. Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime frame timing/device behavior, exact CDXEngine/CViewport layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            "cdxengine", "pre-render", "cgame-render-callee", "viewport"),
        spec("0x0053e2e0", "CDXEngine__Render",
            "int __thiscall CDXEngine__Render(void * this, uint viewpoint)",
            "Wave1094 static read-back: CDXEngine per-view world render spine. CGame__Render calls this for the active viewpoints at 0x0046e68b, 0x0046e747, 0x0046e785, 0x0046e7d8, and 0x0046e883. The body selects viewpoint/camera state, updates wrapped object distance, prepares imposter sample-ring data, updates overlay slots, sets up lights, drives Kempy cube, render queue, water, particles, atmospherics, optional effect, and render-state cleanup paths. Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime render output, exact CDXEngine/queue/resource layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            "cdxengine", "render", "per-view-render", "cgame-render-callee", "render-queue", "water-render", "particle-render", "kempy-cube", "imposter"),
        spec("0x0053ecc0", "CDXEngine__PostRender",
            "int __thiscall CDXEngine__PostRender(void * this, void * viewport)",
            "Wave1094 static read-back: CDXEngine post-view overlay/UI render spine. CGame__Render calls this at 0x0046e892 after the per-view render passes; the body reaches HUD/viewpoint overlays, CHud__RenderBattleline at 0x0053ed79, shared HUD/message/pause/menu/debug/console presentation, render-state cleanup, and frame-end housekeeping. Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime overlay/UI output, exact CDXEngine/CHud/frontend layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            "cdxengine", "post-render", "hud-overlay", "battleline", "cgame-render-callee", "ui-overlay"),
        spec("0x0046e460", "CGame__Render",
            "void __thiscall CGame__Render(void * this, int num_renders)",
            "Wave1094 static read-back: CGame render coordinator for the CDXEngine frame spine. CGame__MainLoop calls this at 0x0046f151; the body updates render-frame timing/fraction, configures split-screen/fullscreen viewports, calls CDXEngine__PreRender, loops CEngine__SetViewpoint and CDXEngine__Render across active viewpoints, then calls CDXEngine__PostRender and reconnect-interface draw paths. Static retail Ghidra metadata/tag/xref/instruction/decompile evidence only; runtime frame cadence, exact CGame/viewport/player layout, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.",
            "cgame", "render-coordinator", "cdxengine-render-caller", "viewport", "split-screen")
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
                if (!spec.comment.equals(function.getComment())) {
                    println("VERIFY_COMMENT_FAIL: " + spec.address);
                    verificationFailures++;
                }
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + commentUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1094 tag/comment normalization failed: missing=" + missing + " bad=" + bad);
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
