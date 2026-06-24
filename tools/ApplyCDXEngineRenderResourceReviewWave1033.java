//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXEngineRenderResourceReviewWave1033 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String signature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int commentOnlyUpdated = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private int missingTagCount(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        int count = 0;
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                count++;
            }
        }
        return count;
    }

    private void verifyReadBack(Spec spec) {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!fn.getSignature().toString().equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (!spec.comment.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (missingTagCount(fn, spec) != 0) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + fn.getName());
                stats.bad++;
                return;
            }
            if (!fn.getSignature().toString().equals(spec.signature)) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + fn.getSignature());
                stats.bad++;
                return;
            }

            boolean commentNeedsUpdate = fn.getComment() == null || !fn.getComment().equals(spec.comment);
            int tagsToAdd = missingTagCount(fn, spec);
            if (!commentNeedsUpdate && tagsToAdd == 0) {
                println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + spec.name + " already matched");
                stats.skipped++;
                return;
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name
                    + " commentNeedsUpdate=" + commentNeedsUpdate
                    + " tagsToAdd=" + tagsToAdd);
                stats.skipped++;
                stats.commentOnlyUpdated++;
                stats.tagsAdded += tagsToAdd;
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                    stats.tagsAdded++;
                }
            }
            stats.commentOnlyUpdated++;
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name);
            stats.updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        } catch (Exception ex) {
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            stats.bad++;
        }
    }

    private String[] commonTags(String... extra) {
        String[] common = new String[] {
            "static-reaudit",
            "cdxengine-render-resource-review-wave1033",
            "wave1033-readback-verified",
            "retail-binary-evidence",
            "comment-corrected",
            "wave806-normalized",
            "texture-refcount",
            "cdxengine"
        };
        String[] result = new String[common.length + extra.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extra, 0, result, common.length, extra.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyCDXEngineRenderResourceReviewWave1033 mode=" + (dryRun ? "dry" : "apply"));

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0053d3a0",
                "CDXEngine__ReleaseDefaultTextureAndMeshRefs",
                "void __fastcall CDXEngine__ReleaseDefaultTextureAndMeshRefs(void * this)",
                "Wave1033 stale-comment correction: Wave806 renamed the release helper called here to CTexture__DecrementRefCountFromNameField, superseding the older HUD-specific helper wording. CLTShell shutdown passes the global CDXEngine object at 0x89c9a0 in ECX; this helper releases the default texture handle at this+0x4e4 through CTexture__DecrementRefCountFromNameField(texture+8), decrements the default mesh usage counter at this+0x28 + 0x170, and clears both slots. Static retail Ghidra evidence only; exact CDXEngine/CTexture layout, runtime shutdown/lifetime behavior, BEA patching, and rebuild parity remain separate proof.",
                commonTags("dxengine-resource-tail-wave592", "default-texture", "default-mesh", "resource-release")
            ),
            new Spec(
                "0x00544060",
                "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer",
                "void __fastcall CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer(void * kempy_cube_resources)",
                "Wave1033 stale-comment correction: Wave806 renamed the release helper called here to CTexture__DecrementRefCountFromNameField, superseding the older HUD-specific helper wording. CEngine__Shutdown calls this ECX-only cleanup helper for the engine+0x498 Kempy cube resource block; the body walks five texture pointers, decrements each texture refcount through CTexture__DecrementRefCountFromNameField(texture+8), clears each slot, then releases global CVBuffer pointer 0x008aa908 through its vtable delete path and clears the global. Static retail Ghidra evidence only; exact texture/CVBuffer ownership, runtime shutdown/lifetime behavior, source-body identity, BEA patching, and rebuild parity remain separate proof.",
                commonTags("cdxengine-kempy-cube-wave600", "kempy-cube", "texture-slots", "cvbuffer", "resource-release")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " tags_added=" + stats.tagsAdded
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1033 apply encountered missing/bad rows");
        }
    }
}
