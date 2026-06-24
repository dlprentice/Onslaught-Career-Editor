//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyTextureCoreTailWave876 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "texture-core-tail-wave876",
            "wave876-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "important-texture-render-infrastructure",
            "high-importance-low-local-evidence-density",
            "texture-core",
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
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

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
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
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
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
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + expectedSignature(spec));
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        VoidDataType voidType = VoidDataType.dataType;
        IntegerDataType intType = IntegerDataType.dataType;
        PointerDataType voidPtr = new PointerDataType(voidType);
        PointerDataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00556cc0",
                "CTexture__ctor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: CTexture constructor at the post-Wave875 raw commentless head. The body calls CTextureBase__Init with ECX=this+0x08, installs CDXSurf__vtable, clears texture/resource pointer ranges, initializes scale fields +0x94/+0x98 to 1.0, sets frame/resource counters at +0x138 and +0x150 to 1, calls CShaderBase__Init on global engine/shader state DAT_00855bb0, and initializes tail flags at +0x155/+0x156. Xrefs include CTexture__FindTexture, CDXBattleLine construction/load, CDXCompass init, CDXFont GDI creation, and CDXTexture__Deserialize. Static retail Ghidra decompile/xref/instruction evidence only; exact CTexture layout, source-body identity, runtime texture lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "constructor", "xrefs-7")
            ),
            new Spec(
                "0x00556f50",
                "CTexture__Release",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: texture release/cleanup connector. The body clears cached render-state slots 0-3 through CEngine__SetRenderStateCached(DAT_00855bb0, state_id, 0), then when this is non-null dispatches through the object's first vtable slot with delete/release flag 1. Xrefs include CLTShell runtime/resource initialization, frontend/game loop shutdown, CTexture__FindTexture miss cleanup, CTexture__ClearOut, CTexture__FreeLevelResources, and CFEPGoodies resource cleanup. Static retail evidence only; exact destructor ownership, refcount/lifetime policy, runtime resource behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture", "release", "resource-lifetime", "xrefs-7")
            ),
            new Spec(
                "0x00557060",
                "CTextureSequence__EnsureLoaded",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: texture-sequence load/ensure helper referenced from data slot 0x005e59a8 and a no-function callsite at 0x0053a040. When global device/resource state DAT_00888c8c is non-zero and this+0x14c marks the texture as file-backed/resource-backed, the body refreshes this+0x144 from CEngine__TextureFormatField32FD4ToIndex, creates the texture at this+0xb8 when missing using dimensions at this+0xac/+0xb0, level/count field this+0x148, flags at this+0x150, and the observed internal-format-to-D3D mapping, then emits debug trace context through CEngine__GetConstant32. Static retail evidence only; exact CTextureSequence class boundary, field layout, runtime texture allocation behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture-sequence", "ensure-loaded", "resource-lifetime", "d3d-format-map")
            ),
            new Spec(
                "0x005572c0",
                "CTextureSequence__ReleaseIfLoaded",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: texture-sequence release helper referenced from data slots 0x005e4f70 and 0x005e59ac. When this+0x14c is set and this+0xb8 is non-null, the body calls the pointed object's vtable slot +0x08, clears this+0xb8, then runs the observed no-op/status helper with DAT_009c3df0 and this. It returns zero. Static retail evidence only; exact CTextureSequence ownership, COM/resource-release contract, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("ctexture-sequence", "release-if-loaded", "resource-lifetime")
            ),
            new Spec(
                "0x00557a00",
                "CDXTexture__FormatToString",
                "__cdecl",
                charPtr,
                new ParameterImpl[] { param("format", intType) },
                "Wave876 static read-back: internal texture-format index/string mapper called by CDXTexture__LoadTextureFromFile. The switch maps observed indices 0-10 to the UNKNOWN/A1R5G5B5/A4R4G4B4/X8R8G8B8/A8R8G8B8/R5G6B5/compressed-format/Q8W8V8U8 string table entries and returns a default string for out-of-range values. Static retail string/decompile evidence only; exact enum names, complete Direct3D format semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "format-to-string", "d3d-format-map")
            ),
            new Spec(
                "0x00557a90",
                "CDXTexture__LoadTextureFromFile_Core",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: central texture load core referenced by data slot 0x005e59a4 and a no-function callsite at 0x0053a011. The body exits when DAT_00888c8c is zero, handles empty-name textures by creating a D3D texture through the Wave849 CEngine texture-create wrappers, handles procedural names beginning with '*' by parsing format/level/dimension tokens, builds lower-cased data\\Textures paths for ordinary names, detects animated frame sequences from a backslash/underscore path pattern, loads per-frame resources through CDXTexture__LoadTextureFromFile when DAT_00662dd4 permits, otherwise decodes mapped texture files through CDXTexture__DecodeMappedFileToTexture, updates width/height fields at this+0xac/+0xb0 and format field this+0x144, and emits warning/status traces. The decompile still exposes an unaff_EBX-dependent format reconciliation path, so the exact ABI/layout is bounded rather than fully proven. Static retail evidence only; exact CDXTexture layout, source-body identity, runtime file/decode behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "texture-load-core", "animated-texture", "resource-decode")
            ),
            new Spec(
                "0x00558690",
                "CDXTexture__GetAnimatedFrame",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: animated texture frame selector with 53 xrefs across loading screen, CDXBattleLine, CDXCompass, CDXFont, CDXBitmapFont, CDXImposter, CDXEngine, CDXLandscape, mesh rendering, particles, render queue, trees, water rendering, CDXSurf, DX front-end video, and atmospherics. If frame count this+0x138 is 1 it returns this+0xb8; otherwise it computes a time-scaled frame index from CDXMeshVB__GetGlobalZeroDouble() * DAT_005d8ba8, applies modulo frame count, and returns the corresponding pointer at this+0xb8+frame*4. Static retail evidence only; exact timing units, texture frame-array layout, runtime animation behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "animated-frame", "xrefs-53")
            ),
            new Spec(
                "0x00558870",
                "CDXTexture__DumpAllTexturesToTga",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave876 static read-back: console/debug texture dump helper called by con_dumptextures. The body creates the TextureDump directory, walks the global texture list from DAT_0083d9b0 via the +0xa0 next pointer, and dumps entries whose name is empty or begins with '*' to TextureDump\\%d.tga through CDXTexture__DumpTextureToRGBA. Static retail evidence only; exact dump filename counter source, TGA correctness, runtime tooling behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtexture", "dump-textures", "debug-console")
            ),
            new Spec(
                "0x005588f0",
                "CVBufTexture__RenderModePass",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave876 static read-back: CVBufTexture render-mode/state bridge called by CVBufTexture__Render, CMeshRenderer__RenderMeshWithLayerPasses, and Wave875 CVBufTexture__DrawSpriteEx. The body applies a texture transform when scale/offset fields at this+0x94/+0x98/+0x8c/+0x90 are non-identity, then switches on mode field this+0x88 to configure D3DStateCache and RenderState state for observed modes 0-5, including secondary-blend setup, fixed texture transforms, alpha-ref/blend-state updates, and mesh-render pass state. Static retail evidence only; exact CVBufTexture layout, render-mode enum names, runtime visual output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cvbuftexture", "render-mode-pass", "render-state", "wave875-context", "xrefs-6")
            ),
            new Spec(
                "0x00558ef0",
                "CVBufTexture__SetupSecondaryBlend",
                "__cdecl",
                intType,
                new ParameterImpl[] { param("alpha", intType) },
                "Wave876 static read-back: secondary texture-stage blend helper called three times from CVBufTexture__RenderModePass. When alpha is not 0xff it checks CDXTexture__IsResourceHandleValid(DAT_009cc118) and DAT_009cc124, can return false when the secondary resource is valid but disabled, otherwise configures D3DStateCache stage 1 states, writes render-state color 0x3c as alpha<<24 | 0x00ffffff, clears stage-1 state 0x0b, and returns a boolean-like success value. Static retail evidence only; exact secondary texture ownership, render-state enum names, runtime blend behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cvbuftexture", "secondary-blend", "render-state")
            ),
            new Spec(
                "0x0055a0f0",
                "CEngine__TextureFormatIndexToD3D",
                "__cdecl",
                intType,
                new ParameterImpl[] { param("format_index", intType) },
                "Wave876 static read-back: internal texture-format index to Direct3D-format mapper called by CUMTexture__RecreateTextureResource. Observed indices 1-10 map to D3D-format/FourCC constants 0x19, 0x1a, 0x16, 0x15, 0x17, 0x31545844, 0x32545844, 0x34545844, 0x3c, and 0x3f; default returns 0. Static retail evidence only; exact enum names, complete D3D format semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cengine", "texture-format-map", "d3d-format-map")
            ),
            new Spec(
                "0x0055a170",
                "CEngine__TextureFormatD3DToIndex",
                "__cdecl",
                intType,
                new ParameterImpl[] { param("d3d_format", intType) },
                "Wave876 static read-back: inverse Direct3D-format/FourCC to internal texture-format index mapper called by CEngine__TextureFormatField32FD4ToIndex. The body recognizes 0x19, 0x1a, 0x16, 0x15, 0x17, 0x31545844, 0x32545844, 0x34545844, 0x3c, and 0x3f and returns indices 1-10; default returns 0. Static retail evidence only; exact enum names, complete D3D format semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cengine", "texture-format-map", "d3d-format-map")
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
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad == 0 && stats.missing == 0) {
                println("REPORT: Save succeeded");
            } else {
                println("REPORT: Save blocked by bad/missing rows");
            }
        } else {
            println("REPORT: Save succeeded");
        }
    }
}
