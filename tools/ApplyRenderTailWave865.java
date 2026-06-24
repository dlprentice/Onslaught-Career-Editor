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

public class ApplyRenderTailWave865 extends GhidraScript {
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
            "render-tail-wave865",
            "wave865-readback-verified",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened",
            "important-connective-infrastructure",
            "render-tail"
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
                "0x0053df40",
                "CDXEngine__RenderTexturedBeamQuad",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("start_x", floatType),
                    param("start_y", floatType),
                    param("start_z", floatType),
                    param("start_w_or_pad", floatType),
                    param("end_x", floatType),
                    param("end_y", floatType),
                    param("end_z", floatType),
                    param("end_w_or_pad", floatType),
                    param("reserved_flags", intType)
                },
                "Wave865 render-tail static read-back: side-effect render helper reached by three no-boundary callsites at 0x004e9fc9, 0x004ea110, and 0x004ea2f0 with ECX loaded to 0x0089c9a0 and RET 0x24. The body copies the global world matrix seed from 0x0089d640, builds a perpendicular beam half-vector from observed start/end coordinate lanes, obtains a CVBufTexture from this+0x4ec, writes four vertices and six indices, renders once, then decrements the resource reference. The two W/pad lanes and reserved flag slot are preserved as bounded stack-shape evidence only. Static retail Ghidra metadata/decompile/xref evidence only; exact source identity, caller function boundaries, visual beam semantics, runtime rendering, BEA patching, and rebuild parity remain unproven.",
                tags("cdxengine", "beam-render", "cvbuftexture", "ret-0x24")
            ),
            new Spec(
                "0x0053f010",
                "CCutscene__SetTrackSlotByFlag",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("track_slot", intType),
                    param("use_primary_track", intType)
                },
                "Wave865 render-tail static read-back: CCutscene/CGame callers in CGame__LoadLevel, CCutscene__Start, CCutscene__Stop, and CCutscene__Update push exactly two stack arguments before calling this RET 0x8 helper on global cutscene owner 0x0089c9a0. The body writes track_slot to this+0x4cc when use_primary_track is nonzero and to this+0x4d0 otherwise. Static retail Ghidra metadata/decompile/xref evidence only; exact cutscene track-slot semantics, source identity, runtime cutscene behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cutscene", "track-slot", "ret-0x8")
            ),
            new Spec(
                "0x00540c30",
                "CDXFrontEnd__SetupRenderMatricesAndProjection",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave865 render-tail static read-back: CDXFrontEnd__VFunc_07_00540fb0 calls this no-stack-argument frontend render setup helper. The body seeds render/world matrices from 0x008a9788 and global frontend constants, writes three render-info/light matrix blocks at 0x009c65c0/0x009c661c/0x009c6678, calls CParticleManager__InterpolatePositions and CParticleManager__UpdateRenderNodesAndResetState, invokes the device vfunc at +0xc4, toggles render state 0xf, and calls CDXEngine__RenderParticleTexturePass. Source DXFrontend::RenderParticles is a useful architecture hint, but this is static retail Ghidra evidence only; exact source identity, frontend particle visual behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cdxfrontend", "render-particles", "render-info", "particle-texture")
            ),
            new Spec(
                "0x00541f50",
                "CDXEngine__GenerateLandscapeCacheTileChunk",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("detail_shift", intType),
                    param("source_cache_info", voidPtr),
                    param("source_pixels", voidPtr),
                    param("tile_x", intType),
                    param("tile_y", intType),
                    param("dest_x", intType),
                    param("dest_y", intType),
                    param("tile_count_x", intType),
                    param("tile_count_y", intType),
                    param("output_stride_pixels", intType)
                },
                "Wave865 render-tail static read-back: CDXEngine__BuildLandscapeTextureCache calls this RET 0x28 helper with detail-shift, source/cache pointers, tile coordinates, tile span, and output-stride stack shape while ECX is the landscape-cache generator owner. The body samples source pixels, walks landscape descriptor rows through this+0x20/0x28 and mask fields this+0x10c4/0x10c8, blends five neighbor height/color lanes, and writes ARGB cache pixels into the destination tile buffer. Static retail Ghidra metadata/decompile/xref evidence only; exact landscape/cache structure layouts, source identity, generated cache correctness, runtime usage, BEA patching, and rebuild parity remain unproven.",
                tags("cdxengine", "landscape-cache", "ret-0x28", "texture-cache")
            ),
            new Spec(
                "0x00542f90",
                "CDXImposter__BuildQuadGeometry",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("center_vec", floatPtr),
                    param("right_vec", floatPtr),
                    param("up_vec", floatPtr),
                    param("vertex_alpha", floatType),
                    param("reserved_14", intType),
                    param("u0", floatType),
                    param("v0", floatType),
                    param("u1", floatType),
                    param("v1", floatType),
                    param("use_secondary_buffer", intType)
                },
                "Wave865 render-tail static read-back: CDXEngine__RenderImposterBillboardSet calls this RET 0x28 helper with center/right/up vector pointers, UV/alpha lanes, and a primary-vs-secondary buffer selector. The body normalizes the right/up cross product, selects CVBufTexture globals 0x008aa8b4 or 0x008aa8cc, writes four billboard vertices with shared normal and UV lanes, and writes six quad indices. Static retail Ghidra metadata/decompile/xref evidence only; exact vertex layout, imposter frame layout, runtime billboard output, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("cdximposter", "billboard-quad", "cvbuftexture", "ret-0x28")
            ),
            new Spec(
                "0x00544fb0",
                "CDXLandscape__ResetWrapper",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reset_x", intType),
                    param("reset_y", intType)
                },
                "Wave865 render-tail static read-back: CEngine__ResetPos forwards two stack values and the engine landscape pointer at engine+0x10 into this RET 0x8 wrapper. The wrapper ignores the two stack values and calls CDXLandscape__Reset(this). Static retail Ghidra metadata/decompile/xref evidence only; exact reset coordinate semantics, CDXLandscape layout, runtime reset behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("cdxlandscape", "reset-wrapper", "ret-0x8")
            ),
            new Spec(
                "0x005473b0",
                "CDXEngine__InvalidateLandscapeTilesAndPatchSlots",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("min_x", intType),
                    param("min_y", intType),
                    param("max_x", intType),
                    param("max_y", intType),
                    param("force_full_rebuild", intType)
                },
                "Wave865 render-tail static read-back: CStaticShadows__UpdateVisibility and CDXEngine__ApplyNavMapConsoleToggle_Thunk call this RET 0x14 helper with a landscape rectangle and a full-rebuild flag. The non-full branch clamps to a 64x64 tile range, marks patch-slot bytes with 0x80, and calls CLandscapeTexture__UpdateTileRange for larger ranges; the full branch rebuilds the landscape vertex buffer, resets three CDXPatchManager slots rooted at 0x009c64d8, and clears 0x1000 cached patch entries. Static retail Ghidra metadata/decompile/xref evidence only; exact tile/patch entry layout, runtime invalidation behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("cdxengine", "landscape", "patch-slots", "ret-0x14")
            ),
            new Spec(
                "0x00547860",
                "CDXEngine__BuildLandscapeTextureCache",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave865 render-tail static read-back: no-argument developer/cache-builder path reached through a no-boundary wrapper at 0x00544706 after loading global engine pointer 0x0089c9b0. The body logs 'Building texture cache...', opens ps2data/LandscapeTextureCache texture/index outputs, loops detail shifts 2 through 4, calls CDXEngine__GenerateLandscapeCacheTileChunk for each tile, palletizes with DXPalletizer__Palletize, writes index/texture data, frees temporary buffers through CDXMemoryManager__Free, and logs completion. Static retail Ghidra metadata/decompile/xref evidence only; exact tool-mode entrypoint, file-format semantics, runtime use, source identity, BEA patching, and rebuild parity remain unproven.",
                tags("cdxengine", "landscape-cache", "developer-tool", "palletizer")
            ),
            new Spec(
                "0x00549310",
                "CDXMemoryManager__LogDebugStats",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave865 render-tail static read-back: CLTShell__RunFrontEndAndGameLoop and CLTShell__RunStressTestLevelLoop call this ECX-only memory debug logger on global CDXMemoryManager 0x009c3df0. The body emits DebugTrace separators, calls CMemoryHeap__LogStats for three heap subobjects at this+0x214, this+0xae0, and this+0x13ac, then formats default/thing heap peak and size lines. Stuart source DXMemoryManager::LogDebugStats gives matching architecture names, but this is static retail Ghidra evidence only; exact heap layout, debug-output completeness, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cdxmemorymanager", "debug-stats", "heap-stats", "shell-loop")
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
            throw new RuntimeException("Wave865 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
