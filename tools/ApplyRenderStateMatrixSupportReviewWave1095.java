//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;

public class ApplyRenderStateMatrixSupportReviewWave1095 extends GhidraScript {
    private static final String ADDRESS = "0x00513af0";
    private static final String NAME = "D3DStateCache__SetSlotMode4or5";
    private static final String SIGNATURE = "void __stdcall D3DStateCache__SetSlotMode4or5(int state_slot)";
    private static final String COMMENT =
        "Frontend/game-state toggle helper: updates per-slot state array DAT_008557f4 (mode 4 or 5 based on DAT_008554fc) and notifies DAT_00888a50 via vfunc +0x10c when state changes.";

    private static final String[] TAGS = {
        "static-reaudit",
        "render-state-matrix-support-review-wave1095",
        "wave1095-readback-verified",
        "retail-binary-evidence",
        "tag-normalized",
        "comment-hardened",
        "d3d-state-cache",
        "direct3d-device",
        "render-state",
        "state-cache",
        "mode-toggle",
        "mode-4-or-5",
        "vtable-0x10c"
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
        Address address = toAddr(ADDRESS);
        Function function = functionManager.getFunctionAt(address);

        int updated = 0;
        int skipped = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        if (function == null) {
            println("MISSING: " + ADDRESS + " " + NAME);
            missing++;
        } else if (!verifyIdentity(function)) {
            bad++;
        } else {
            Set<String> existingTags = tagNames(function);
            StringBuilder missingTags = new StringBuilder();
            for (String tag : TAGS) {
                if (!existingTags.contains(tag)) {
                    if (missingTags.length() != 0) {
                        missingTags.append(",");
                    }
                    missingTags.append(tag);
                    tagsAdded++;
                }
            }

            if (missingTags.length() == 0) {
                println("SKIP: " + ADDRESS + " " + NAME + " tags already present");
                skipped++;
            } else if (dryRun) {
                println("WOULD_TAG: " + ADDRESS + " " + NAME + " +" + missingTags);
            } else {
                for (String tag : TAGS) {
                    if (!existingTags.contains(tag)) {
                        function.addTag(tag);
                    }
                }
                println("UPDATED: " + ADDRESS + " " + NAME + " tags=+" + missingTags);
                updated++;
                currentProgram.flushEvents();
                Thread.sleep(50L);
            }
        }

        if (!dryRun && missing == 0 && bad == 0) {
            Function readBack = functionManager.getFunctionAt(address);
            if (readBack == null) {
                println("VERIFY_MISSING: " + ADDRESS);
                bad++;
            } else if (!verifyIdentity(readBack)) {
                bad++;
            } else {
                Set<String> readBackTags = tagNames(readBack);
                for (String tag : TAGS) {
                    if (!readBackTags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + ADDRESS + " " + tag);
                        bad++;
                    }
                }
            }
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
            throw new IllegalStateException("Wave1095 tag normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private boolean verifyIdentity(Function function) {
        boolean ok = true;
        if (!NAME.equals(function.getName())) {
            println("BADNAME: " + ADDRESS + " expected=" + NAME + " actual=" + function.getName());
            ok = false;
        }
        if (!SIGNATURE.equals(function.getSignature().toString())) {
            println("BADSIG: " + ADDRESS + " expected=" + SIGNATURE + " actual=" + function.getSignature());
            ok = false;
        }
        if (!COMMENT.equals(function.getComment())) {
            println("BADCOMMENT: " + ADDRESS);
            ok = false;
        }
        return ok;
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
