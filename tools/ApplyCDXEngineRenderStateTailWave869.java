//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXEngineRenderStateTailWave869 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String convention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String convention, DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.convention = convention;
            this.returnType = returnType;
            this.parameters = parameters;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cdxengine-render-state-tail-wave869",
            "wave869-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-reviewed",
            "important-connective-infrastructure",
            "cdxengine",
            "renderer-state",
            "lighting-state",
            "d3d-state-cache"
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.convention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
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

    private boolean alreadyApplied(Function fn, Spec spec) {
        return fn.getName().equals(spec.name)
            && signatureMatches(fn, spec)
            && spec.comment.equals(fn.getComment())
            && hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.convention).append(" ").append(spec.name).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                stats.bad++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }

            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsComment = !spec.comment.equals(fn.getComment());
            boolean needsTags = !hasAllTags(fn, spec.tags);

            if (!needsSignature && !needsComment && !needsTags) {
                println("SKIP_OK: " + spec.address + " " + spec.name + " already current");
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY_UPDATE: " + spec.address + " " + spec.name
                    + " -> " + expectedSignature(spec)
                    + " needsSignature=" + needsSignature
                    + " needsComment=" + needsComment
                    + " needsTags=" + needsTags);
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else if (needsComment || needsTags) {
                    stats.commentOnlyUpdated++;
                }
                return;
            }

            if (needsSignature) {
                fn.setCallingConvention(spec.convention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            if (needsComment) {
                fn.setComment(spec.comment);
            }
            for (String tag : spec.tags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                }
            }

            Function readback = functionAtEntry(spec.address);
            if (readback == null || !alreadyApplied(readback, spec)) {
                println("READBACK_BAD: " + spec.address);
                if (readback != null) {
                    println("READBACK_GOT: " + readback.getName() + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
                }
                stats.bad++;
                return;
            }
            println("READBACK_OK: " + spec.address + " " + spec.name + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00551200",
                "CDXEngine__ApplyCachedLight",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("light_index", intType), param("enabled", intType)},
                "Wave869 CDXEngine render-state tail static read-back: applies one 0x5c-byte cached light record selected by light_index into a stack D3D light-style record, chooses a light type from the record header, copies color/vector/attenuation fields, derives attenuation from constants at 0x005d8568 and 0x005d8578, conditionally copies the direction/vector fields when enabled == 1, then calls the D3D device vtable slot at 0xcc with the light index. Xrefs include CDXLandscape__Render and CDXEngine__ApplyPendingRenderState. This is high-importance, low local-evidence-density renderer lighting infrastructure. Static retail Ghidra evidence only; exact light-record layout, exact Direct3D light semantic fields, runtime lighting behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cached-light", "landscape-render", "pending-render-state")
            ),
            new Spec(
                "0x005512f0",
                "CDXEngine__SetFieldE18",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("value", intType)},
                "Wave869 CDXEngine render-state tail static read-back: writes the incoming value directly to CDXEngine field this+0xe18 and returns. The only pre-state xrefs are from CMeshRenderer__RenderMeshCore at 0x0054b22c and 0x0054b27f, so the row is preserved with the existing conservative field-based name instead of forcing a stronger semantic label. This is high-importance, low local-evidence-density renderer state infrastructure. Static retail Ghidra evidence only; exact field purpose, mesh-render side effect, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("field-e18", "mesh-renderer", "conservative-name")
            ),
            new Spec(
                "0x00551300",
                "CDXEngine__PushTransformState",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("slot", intType), param("mode", intType), param("matrix", floatPtr)},
                "Wave869 CDXEngine render-state tail static read-back: snapshots 16-value world/view/projection matrix blocks from this+0x354, this+0x394, and this+0x3d4 into stack locals, calls the shared matrix/texture dispatch thunk, then adjusts a float at slot+4 using matrix[1] and global constants 0x005d85ec and 0x00888a40. Xrefs come from CHud__RenderTargetMarkers3D and CHud__RenderWorldTargetSprites, tying this helper to world-space HUD marker transform handoff. Existing signature is reviewed and left unchanged, but the slot/mode naming remains conservative. Static retail Ghidra evidence only; exact parameter semantics, matrix convention, runtime HUD rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("transform-state", "hud-world-marker", "matrix-snapshot")
            ),
            new Spec(
                "0x005513d0",
                "CDXEngine__SetVertexFormatDeferred",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("format", intType)},
                "Wave869 CDXEngine render-state tail static read-back: marks deferred vertex-format dirty byte this+0xe2d and stores the requested format at this+0x2f0. The observed xref is CDXEngine__Render at 0x0053e5e6 after render setup calls, so this remains a deferred render-state setter rather than a runtime behavior proof. Static retail Ghidra evidence only; exact vertex declaration/FVF interpretation, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("vertex-format", "deferred-render-state", "cdxengine-render")
            ),
            new Spec(
                "0x005513f0",
                "CDXEngine__SetShaderMode",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("mode", intType)},
                "Wave869 CDXEngine render-state tail static read-back: stores mode at this+0xe58. When mode is zero, it restores the cached vertex-shader handle from this+0xe14 through CEngine__SetVertexShaderHandleRaw(&DAT_00855bb0, ...), then calls RenderState_Set_23_8C_Compat(1). Pre-state xrefs at 0x005559af and 0x00555a15 sit outside a named function boundary, so this keeps a bounded shader-mode claim. Static retail Ghidra evidence only; exact shader-mode enum, surrounding unnamed caller identity, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shader-mode", "vertex-shader", "unnamed-caller-xref")
            ),
            new Spec(
                "0x00551420",
                "D3DStateCache__SetMipFilterByGlobalToggle",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("stage", intType)},
                "Wave869 CDXEngine render-state tail static read-back: chooses sampler state 7 value 1 when global g_DisallowMipMapping is nonzero, otherwise sets value 2, both through D3DStateCache__SetState114Cached(stage, 7, value). Xrefs include D3DStateCache__UseDefaultRenderState, CDXEngine__Render, terrain/landscape texture paths, and water/render helper rows. This is high-importance D3D sampler policy infrastructure. Static retail Ghidra evidence only; exact Direct3D enum naming, runtime texture filtering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mip-filter", "global-toggle", "sampler-state")
            ),
            new Spec(
                "0x00551460",
                "D3DStateCache__SetMipFilterLinear",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("stage", intType)},
                "Wave869 CDXEngine render-state tail static read-back: unconditionally calls D3DStateCache__SetState114Cached(stage, 7, 2). Xrefs include D3DStateCache__UseDefaultRenderState, CDXEngine__Render, CHud__RenderOverlay, HUD target marker paths, and landscape render-state setup. This is high-importance D3D sampler policy infrastructure. Static retail Ghidra evidence only; exact Direct3D enum naming, runtime texture filtering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mip-filter", "linear-filter", "sampler-state")
            ),
            new Spec(
                "0x00551480",
                "D3DStateCache__SetMipFilterPoint",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("stage", intType)},
                "Wave869 CDXEngine render-state tail static read-back: unconditionally calls D3DStateCache__SetState114Cached(stage, 7, 0). Xrefs include CDXEngine__PostRender, HudRenderState__ApplyOverlaySpriteState, CLevelBriefingLog__Render, CDXEngine sprite/text setup, and HUD texture paths. This is high-importance D3D sampler policy infrastructure for point/nearest-style filtering. Static retail Ghidra evidence only; exact Direct3D enum naming, runtime texture filtering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("mip-filter", "point-filter", "sampler-state", "hud-render")
            ),
            new Spec(
                "0x005514a0",
                "CDXEngine__SetProjectionDepthBiasIndex",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("bias_index", intType)},
                "Wave869 CDXEngine render-state tail static read-back: if bias_index differs from this+0xe24, stores it, copies the projection matrix at this+0x3d4 into a stack matrix, subtracts global 0x009c742c * bias_index from the depth/translation slot, calls the D3D device vtable slot at 0xb0 with transform index 3, and clears projection dirty byte this+0xe2a. Xrefs include D3DStateCache__UseDefaultRenderState, CWaterRenderSystem__RenderMainPass, water render transitions, and render-state setup. Static retail Ghidra evidence only; exact depth-bias convention, projection slot identity, runtime water/render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("projection-depth-bias", "water-render", "device-transform")
            ),
            new Spec(
                "0x00551510",
                "CDXEngine__GetProjectionWithDepthBias",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_matrix", floatPtr)},
                "Wave869 CDXEngine render-state tail static read-back: copies the current projection matrix from this+0x3d4 into out_matrix, then subtracts this+0xe24 * global 0x009c742c from out_matrix[0xe]. Xrefs are CVertexShader__ApplyRenderStateShaderConstants and CVertexShader__ApplyCustomRenderStateShaderConstants, tying the helper to shader constant setup. Static retail Ghidra evidence only; exact matrix convention, shader constant register mapping, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                tags("projection-depth-bias", "vertex-shader-constants", "matrix-copy")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave869 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
