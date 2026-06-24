//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.util.HashSet;
import java.util.Set;

public class ApplyWaterRenderTailWave877 extends GhidraScript {
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
        int renamed = 0;
        int wouldRename = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "water-render-tail-wave877",
            "wave877-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-verified",
            "important-water-render-infrastructure",
            "high-importance-low-local-evidence-density",
            "water-render",
            "render-resource",
            "raw-commentless-head"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        String actualSignature = readBack.getSignature().toString();
        if (!actualSignature.equals(spec.signature)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature);
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> readBackTags = tagNames(readBack);
        for (String tag : spec.tags) {
            if (!readBackTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }
            String actualSignature = fn.getSignature().toString();
            if (!actualSignature.equals(spec.signature)) {
                throw new IllegalStateException("Unexpected signature: " + actualSignature);
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + spec.signature);
                return;
            }

            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + spec.signature);
                return;
            }

            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + spec.signature);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0055b0e0",
                "CWaterRenderSystem__ctor",
                "void * __fastcall CWaterRenderSystem__ctor(void * this)",
                "Wave877 static read-back: CWaterRenderSystem constructor at the post-Wave876 raw commentless head. The body installs the CWaterRenderSystem scalar-deleting-destructor vtable, clears texture/resource slots this+0x08/+0x0c/+0x10/+0x14/+0x18 and dirty/cache field this+0x3ab8, then calls CShaderBase__Init on global engine/shader state DAT_00855bb0. Xref is CEngine__Init at 0x00449b7f. Static retail Ghidra decompile/xref/instruction evidence only; exact water-render class layout, source-body identity, runtime water behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constructor", "cengine-init-xref")
            ),
            new Spec(
                "0x0055b140",
                "CWaterRenderSystem__scalar_deleting_dtor",
                "void * __thiscall CWaterRenderSystem__scalar_deleting_dtor(void * this, int free_flag)",
                "Wave877 static read-back: scalar deleting destructor entry referenced by vtable DATA row 0x005e5a70. The body calls CWaterRenderSystem__dtor(this), then frees this through CDXMemoryManager__Free(DAT_009c3df0, this) when free_flag bit 0 is set, and returns this. Static retail evidence only; exact allocator ownership, source-body identity, runtime lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("destructor", "scalar-deleting-dtor", "vtable-data-xref")
            ),
            new Spec(
                "0x0055b160",
                "CWaterRenderSystem__dtor",
                "void __fastcall CWaterRenderSystem__dtor(void * this)",
                "Wave877 static read-back: water-render destructor/lifetime connector. The body releases global resource DAT_009cc21c through vtable slot +0x08 when present, clears that global, unlinks this from shader/render-object lists through CShaderBase__UnlinkFromRenderObjectLists, decrements texture name refs for slots this+0x08/+0x0c/+0x10/+0x14, decrements the CVBuf/resource slot at this+0x18 through CDXEngine__DecrementResourceRefCount, then runs DeviceObject__dtor_body. Static retail evidence only; exact slot ownership/refcount policy, runtime resource behavior, BEA patching, and rebuild parity remain unproven.",
                tags("destructor", "resource-lifetime", "texture-refcount")
            ),
            new Spec(
                "0x0055b230",
                "CWaterRenderSystem__LoadTextures",
                "void __fastcall CWaterRenderSystem__LoadTextures(void * this)",
                "Wave877 static read-back: water texture/resource loader. Direct string dumps verify mixers\\reflection%.2d.tga at 0x00652a54, mixers\\caustic%.2d.tga at 0x00652a3c, sunblob.tga at 0x00652a30, and sunreflect.tga at 0x00652a20. The body loads reflection and caustic textures into this+0x08/+0x0c, creates the CVBufTexture/resource at this+0x18 from the reflection texture, temporarily sets DAT_00889010 while loading sunblob and sunreflect into this+0x10/+0x14, applies VB/IB formats 0x142 and 0x65, clears this+0x3ab4, and dispatches vtable slot +0x04. Static retail evidence only; exact water texture sequencing, CVBufTexture ownership, runtime visual output, BEA patching, and rebuild parity remain unproven.",
                tags("load-textures", "water-texture-strings", "cvbuftexture")
            ),
            new Spec(
                "0x0055b330",
                "CWaterRenderSystem__ReloadTextures",
                "void __fastcall CWaterRenderSystem__ReloadTextures(void * this, void * reload_target)",
                "Wave877 static read-back: water texture reload entry called by CEngine__SetWater at 0x0044a2c8 and by CWaterRenderSystem__LoadTextures. The body decrements and clears texture slots this+0x08/+0x0c/+0x10/+0x14, clears dirty/cache field this+0x3ab8, then calls CWaterRenderSystem__LoadTextures(this). The reload_target/EDX value is not directly consumed in the decompile. Static retail evidence only; exact SetWater argument semantics, runtime water resource selection, BEA patching, and rebuild parity remain unproven.",
                tags("reload-textures", "setwater-xref", "resource-lifetime")
            ),
            new Spec(
                "0x0055b440",
                "CWaterRenderSystem__BuildGridVBuf",
                "void __stdcall CWaterRenderSystem__BuildGridVBuf(int world_matrix, int texture_a, float p3, float p4, float p5)",
                "Wave877 static read-back: water grid vertex/index-buffer builder called by shadow and main water passes. The body logs the verified string Creating water VBuf\\x0a at 0x00652f50 when rebuilding, resets CVBufTexture slot this+0x18, requests 0x271 vertices, calls CWaterRenderSystem__BuildGridIndexBuffer for a 0x18 by 0x18 grid, adds 0xd80 indices, writes a 25x25 vertex grid with radial alpha clamp/color handling, caches the texture/color key in this+0x3ab8, sets the CVBufTexture persistent, updates world matrix elements, and reapplies shader constants when DAT_009cc1a0 and DAT_009cc218 are active. Static retail evidence only; exact hidden ABI, water grid layout, shader constant schema, runtime rendering, BEA patching, and rebuild parity remain unproven.",
                tags("build-grid-vbuf", "water-grid", "cvbuftexture", "shader-constants")
            ),
            new Spec(
                "0x0055b660",
                "CWaterRenderSystem__RenderShadowPass",
                "void __thiscall CWaterRenderSystem__RenderShadowPass(void * this)",
                "Wave877 static read-back: water shadow-map pass called by CDXLandscape__RenderShadowMap at 0x00546795. The body calls CWaterRenderSystem__BuildGridVBuf with DAT_006fbdfc and this+0x3ab8, applies shader constants from DAT_0089c9b0+0x18, checks a device/vtable call at +0x1ac using DAT_0089c9b0+0x1c, and renders CVBufTexture slot this+0x18 through CVBufTexture__RenderIndexedNoValidate on success. Static retail evidence only; exact shadow-map contract, runtime D3D state, visual output, BEA patching, and rebuild parity remain unproven.",
                tags("shadow-pass", "landscape-shadow-xref", "cvbuftexture")
            ),
            new Spec(
                "0x0055b6c0",
                "CWaterRenderSystem__RenderMainPass",
                "void __fastcall CWaterRenderSystem__RenderMainPass(void * this)",
                "Wave877 static read-back: large main water render pass called twice by CDXEngine__Render. The body gates multiplayer/global water/shader state, validates render records DAT_009cc1c0 and DAT_009cc1a8 through CWaterRenderSystem__ValidateVBufferAndMarkReady / ResetAndMarkSourceFlag / CheckVBufValidAndHandleFailure, animates caustic/reflection/sun texture slots this+0x0c/+0x08/+0x14/+0x10 via CDXTexture__GetAnimatedFrame and CEngine__SetRenderStateCached, uses vertex shader handles 0x242 and 0x142 plus DAT_009cc218, invokes CDXSurf__Render, builds water grids through CWaterRenderSystem__BuildGridVBuf, and renders CVBufTexture slot this+0x18 through CVBufTexture__RenderIndexed / RenderIndexedNoValidate across multiple passes. Static retail evidence only; exact pass ordering, water/shader state schema, runtime visual behavior, BEA patching, and rebuild parity remain unproven.",
                tags("main-pass", "cdxengine-render-xrefs", "animated-textures", "shader-state", "cvbuftexture")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (!dryRun) {
            println("REPORT: Save requested by headless post-script");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave877 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
