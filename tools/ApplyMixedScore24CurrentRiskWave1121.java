// Refresh Wave1121 stale shared-vfunc comment.
// @category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyMixedScore24CurrentRiskWave1121 extends GhidraScript {
    private static final String ADDRESS = "0x005019c0";
    private static final String NAME = "VFuncSlot_09_005019c0";
    private static final String SIGNATURE = "int __cdecl VFuncSlot_09_005019c0(void)";
    private static final String COMMENT = "Wave1121 current-risk comment refresh: shared default/false virtual stub first hardened by Wave841. The body is XOR EAX,EAX; RET, so it returns 0 without reading ECX or stack arguments. Pre-readback xrefs show four direct frontend-development callsites (0x00458662, 0x00458a46, 0x00458d32, 0x00458d4f) where callers test EAX as a boolean/result gate, plus twenty-six DATA pointer slots. RTTI candidate resolution maps those DATA slots to overlapping owner vtables including CControllerDefinition, destroyable segment/component and motion-controller families, CVertexShaderMenu, CVertexShader, CVBuffer, CDXEngine/CDXFMV/CDXFrontEnd/CDXFrontEndVideo, CDXTexture, and CDXTrees. CVertexShader vtable 0x005dfbc4 uses this stub at slots 1 and 4; the former slot-2 no-function-at-pointer boundary at 0x00501a10 was later recovered by Wave961 as CVertexShader__VFunc_02_00501a10. Static retail Ghidra evidence only; exact source virtual method names, caller-specific semantics, concrete class layouts, runtime behavior, BEA patching, and rebuild parity remain deferred.";
    private static final List<String> TAGS = Arrays.asList(
        "static-reaudit",
        "wave1121-mixed-score24-current-risk-review",
        "wave1121-readback-verified",
        "retail-binary-evidence",
        "comment-hardened",
        "comment-refresh",
        "shared-vfunc",
        "default-false",
        "cvertexshader",
        "frontend-development"
    );

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

        println("ApplyMixedScore24CurrentRiskWave1121 mode=" + (dryRun ? "dry" : "apply"));

        FunctionManager functionManager = currentProgram.getFunctionManager();
        Address address = toAddr(ADDRESS);
        Function function = functionManager.getFunctionAt(address);
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
            int missingTags = 0;
            for (String tag : TAGS) {
                if (!existingTags.contains(tag)) {
                    missingTags++;
                }
            }

            boolean commentNeedsUpdate = function.getComment() == null || !function.getComment().equals(COMMENT);
            if (!commentNeedsUpdate && missingTags == 0) {
                println("SKIP: " + ADDRESS + " " + NAME);
                skipped++;
            } else if (dryRun) {
                println("DRY: " + ADDRESS + " " + NAME + " comment_refresh=" + commentNeedsUpdate + " tags_to_add=" + missingTags);
                skipped++;
                commentOnlyUpdated++;
                tagsAdded += missingTags;
            } else {
                function.setComment(COMMENT);
                for (String tag : TAGS) {
                    if (!existingTags.contains(tag)) {
                        function.addTag(tag);
                    }
                }
                currentProgram.flushEvents();
                tagsAdded += missingTags;
                commentOnlyUpdated++;
                updated++;
                verifyReadBack(functionManager);
                println("OK: " + ADDRESS + " " + NAME + " comment refreshed; tags_added=" + missingTags);
                Thread.sleep(50L);
            }
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=" + renamed
            + " would_rename=" + wouldRename
            + " signature_updated=" + signatureUpdated
            + " comment_only_updated=" + commentOnlyUpdated
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1121 comment refresh failed: missing=" + missing + " bad=" + bad);
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
        String actualSignature = function.getSignature().toString();
        if (!SIGNATURE.equals(actualSignature)) {
            println("BADSIG: " + ADDRESS + " expected=" + SIGNATURE + " actual=" + actualSignature);
            ok = false;
        }
        return ok;
    }

    private void verifyReadBack(FunctionManager functionManager) {
        Function function = functionManager.getFunctionAt(toAddr(ADDRESS));
        if (function == null) {
            throw new IllegalStateException("VERIFY_MISSING: " + ADDRESS);
        }
        if (!verifyIdentity(function)) {
            throw new IllegalStateException("VERIFY_IDENTITY_FAILED: " + ADDRESS);
        }
        if (function.getComment() == null || !function.getComment().equals(COMMENT)) {
            throw new IllegalStateException("VERIFY_COMMENT_FAILED: " + ADDRESS);
        }
        Set<String> tags = tagNames(function);
        for (String tag : TAGS) {
            if (!tags.contains(tag)) {
                throw new IllegalStateException("VERIFY_MISSING_TAG: " + ADDRESS + " " + tag);
            }
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
