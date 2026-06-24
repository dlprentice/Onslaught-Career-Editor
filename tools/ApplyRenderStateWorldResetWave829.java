//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyRenderStateWorldResetWave829 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String preSignature;
        final String expectedSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String preSignature, String expectedSignature,
                String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.preSignature = preSignature;
            this.expectedSignature = expectedSignature;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "renderstate-world-reset-wave829",
            "wave829-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "render-state"
        };
        String[] all = new String[common.length + extras.length];
        System.arraycopy(common, 0, all, 0, common.length);
        System.arraycopy(extras, 0, all, common.length, extras.length);
        return all;
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x004eb1e0",
                "D3DStateCache__UseDefaultRenderState",
                "void CGame__ResetRenderStateForWorldRender(void)",
                "void D3DStateCache__UseDefaultRenderState(void)",
                "Wave829 static read-back/name correction: this global default render-state helper aligns with source STATE.UseDefault() callsites in CDXEngine::PreRender, CDXEngine::Render, CDXFrontEnd::RenderStart, loading-screen render, and debug render. The body resets cached-state sentinel tables, conditionally disables the vertex-shader path, forces the baseline D3D render-state sequence through raw SetRenderState helpers, clamps fog/range constants from global depth values, resets projection depth bias and vertex-shader path state, then initializes texture-stage defaults for stages 0-3. This is not CGame-owned. Static retail/source evidence only; exact state-table schema, runtime device behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "source-parity", "default-state", "d3d-state-cache")
            ),
            new Spec(
                "0x00513600",
                "D3DStateCache__ResetSentinelTable",
                "void D3DStateCache__ResetSentinelTable(void)",
                "void D3DStateCache__ResetSentinelTable(void)",
                "Wave829 static read-back: resets the render-state and texture-stage cache sentinels before a forced default-state apply. The body writes INVALID_STATE 0xfedcba98 into the render-state cache at 0x00855540, the texture-stage cache at 0x008557f0, the compact render-state cache at 0x008554d0, and resets current shader/auxiliary sentinel globals 0x00889070/0x00889068 plus zeroes 0x0088906c. Source ltshell.h defines INVALID_STATE as 0xfedcba98. Static retail/source evidence only; exact cache-table ownership and runtime device behavior remain deferred.",
                tags("sentinel-reset", "d3d-state-cache")
            ),
            new Spec(
                "0x00513a50",
                "CEngine__SetRenderStateCached",
                "void __thiscall CEngine__SetRenderStateCached(void * this, int state_id, int value)",
                "void __thiscall CEngine__SetRenderStateCached(void * this, int state_id, int value)",
                "Wave829 static read-back: cached CEngine render-state setter. If the compact cache row at 0x008554d0[state_id] already matches, it returns without a device call; otherwise it updates that cache and dispatches through the device pointer at this+0x32ea0 vtable slot 0x104 with state_id/value. Used by loading screen, battle line, compass, landscape, mesh, particles, render queue, water, surf, frontend video, and other render paths. Static retail evidence only; exact CEngine device-field layout and runtime D3D behavior remain deferred.",
                tags("cached-setter", "engine-render-state")
            ),
            new Spec(
                "0x00513c20",
                "RenderState_SetRaw",
                "void __stdcall RenderState_SetRaw(int render_state, int value)",
                "void __stdcall RenderState_SetRaw(int render_state, int value)",
                "Wave829 static read-back: raw global render-state setter. It always writes 0x00855540[render_state], applies the same 0x16 cull-mode 2<->3 swap when the winding-flip flag is set, then calls the device SetRenderState-like vtable slot 0xe4. This differs from RenderState_Set because it bypasses the cache-equality early return and is used by the default-state reset to force hardware state. Static retail evidence only; exact global device pointer ownership and runtime D3D behavior remain deferred.",
                tags("raw-setter", "device-setrenderstate")
            ),
            new Spec(
                "0x00513d90",
                "RenderState_SetAlphaRefCached",
                "void __stdcall RenderState_SetAlphaRefCached(int alpha_ref)",
                "void __stdcall RenderState_SetAlphaRefCached(int alpha_ref)",
                "Wave829 static read-back: cached alpha-reference render-state helper. When the alpha-ref packing flag at 0x0085541c is set, it mirrors the byte with alpha_ref | alpha_ref<<8; if cached state 0x008555a0 already matches, it skips the device call, otherwise it writes cache state and calls the device SetRenderState-like slot 0xe4 for render state 0x18. Static retail evidence only; exact alpha-test packing reason and runtime device behavior remain deferred.",
                tags("cached-alpha-ref", "alpha-test")
            ),
            new Spec(
                "0x00513dd0",
                "RenderState_SetAlphaRefRaw",
                "void __stdcall RenderState_SetAlphaRefRaw(int alpha_ref)",
                "void __stdcall RenderState_SetAlphaRefRaw(int alpha_ref)",
                "Wave829 static read-back: raw alpha-reference render-state helper. It applies the same optional alpha_ref | alpha_ref<<8 packing as the cached helper, always writes cache state 0x008555a0, and always calls the device SetRenderState-like slot 0xe4 for render state 0x18. The default-state reset uses this to force alpha-reference value 8. Static retail evidence only; exact alpha-test packing reason and runtime device behavior remain deferred.",
                tags("raw-alpha-ref", "alpha-test")
            ),
            new Spec(
                "0x00514030",
                "RenderState_Set_23_8C_Compat",
                "void __stdcall RenderState_Set_23_8C_Compat(char enable)",
                "void __stdcall RenderState_Set_23_8C_Compat(char enable)",
                "Wave829 static read-back: compatibility helper for paired render states 0x23 and 0x8c. Disabled mode clears both cached globals and writes both states to zero. Enabled mode chooses state 0x23 when capability/global bit 0x100 is present, otherwise it clears 0x23 and enables 0x8c. The default-state reset calls this with enable=1, while pending vertex-shader state can disable it before shader-object apply. Static retail evidence only; exact Direct3D enum mapping and runtime capability behavior remain deferred.",
                tags("compat-state", "render-state-23-8c")
            ),
            new Spec(
                "0x00550d50",
                "CDXEngine__ApplyPendingRenderState",
                "void __thiscall CDXEngine__ApplyPendingRenderState(void * this, char force_raw)",
                "void __thiscall CDXEngine__ApplyPendingRenderState(void * this, char force_raw)",
                "Wave829 static read-back: CDXEngine pending render-state flush. It applies dirty alpha/lighting/fog-like state fields through RenderState_Set, handles pending vertex-shader objects or dynamically built render-info shaders, toggles texture-stage defaults around shader apply, pushes dirty transform matrices/lights through the device, applies cached fog/color states 0x8b/0x24/0x25/0x26, and clears dirty flags. Static retail evidence only; exact CDXEngine field layout, shader-object semantics, runtime device behavior, and rebuild parity remain deferred.",
                tags("pending-state-flush", "cdxengine", "vertex-shader", "dirty-flags")
            ),
            new Spec(
                "0x00558fb0",
                "CVBufTexture__SetupRenderStates",
                "void __thiscall CVBufTexture__SetupRenderStates(void * this, char enable_overlay)",
                "void __thiscall CVBufTexture__SetupRenderStates(void * this, char enable_overlay)",
                "Wave829 static read-back: CVBufTexture render-state setup for texture mode at this+0x88. It skips mode 5, pushes a texture transform when scale/offset fields differ from identity, then configures stage 0/1 texture-stage cache state and render-state toggles for modes 0-4, including alpha-ref cached value 8 for mode 4 and optional overlay handling for state 0x1b/state 0xb. Static retail evidence only; exact CVBufTexture field schema, texture-mode enum names, and runtime render behavior remain deferred.",
                tags("cvbuftexture", "texture-stage", "render-mode")
            )
        };
    }

    private boolean hasTags(Function fn, String[] expected) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.expectedName);
        String signature = fn.getSignature().toString();
        String allowedPreSignature = needsRename ? spec.preSignature : spec.expectedSignature;
        if (!signature.equals(allowedPreSignature)) {
            println("BAD: signature mismatch before update at " + spec.address + " got=" + signature
                + " expected=" + allowedPreSignature);
            stats.bad++;
            return;
        }

        boolean needsComment = fn.getComment() == null || !fn.getComment().equals(spec.comment);
        boolean needsTags = !hasTags(fn, spec.tags);

        if (!needsRename && !needsComment && !needsTags) {
            println("SKIP: " + spec.address + " already matches " + spec.expectedName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + spec.expectedName
                + " needsRename=" + needsRename
                + " needsComment=" + needsComment
                + " needsTags=" + needsTags);
            stats.skipped++;
            if (needsRename) {
                stats.wouldRename++;
            }
            if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsComment || needsTags) {
            stats.commentOnlyUpdated++;
        }
        if (needsComment) {
            fn.setComment(spec.comment);
        }
        for (String tagName : spec.tags) {
            fn.addTag(tagName);
        }

        Function readBack = functionAtEntry(spec.address);
        if (readBack == null || !readBack.getName().equals(spec.expectedName)
                || !readBack.getSignature().toString().equals(spec.expectedSignature)
                || readBack.getComment() == null || !readBack.getComment().equals(spec.comment)
                || !hasTags(readBack, spec.tags)) {
            println("BAD: readback mismatch at " + spec.address + " expected " + spec.expectedSignature);
            if (readBack != null) {
                println("BAD: got name=" + readBack.getName() + " signature=" + readBack.getSignature().toString());
            }
            stats.bad++;
            return;
        }

        println("READBACK_OK: " + spec.address + " " + readBack.getName() + " " + readBack.getSignature().toString());
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
            Thread.sleep(100);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (!dryRun && stats.bad == 0 && stats.missing == 0) {
            println("REPORT: Mutation pass complete; headless save follows");
        }
    }
}
