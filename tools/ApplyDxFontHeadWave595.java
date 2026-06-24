//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyDxFontHeadWave595 extends GhidraScript {
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
            "dxfont-head-wave595",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
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
            println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType wideTextPtr = new PointerDataType(ShortDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0053f730",
                "CDXBitmapFont__ctor_base",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave595 name/signature/comment hardening: PCPlatform__LoadFonts and PCPlatform__DeserializeFontsAndAssets call this after allocating CDXBitmapFont-sized objects. ECX carries this; the body zeroes fields at this+0x168/+0x16c/+0x170/+0x174/+0x178, installs vtable 0x005e504c, calls CDXBitmapFont__BuildGlyphRemapTables, and returns this. Static retail evidence only; exact CDXBitmapFont layout, source identity, runtime font loading behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBitmapFont__ctor_like_0053f730", "CDXBitmapFont__ctor_base"},
                tags("cdxbitmapfont", "constructor", "font-loading")
            ),
            new Spec(
                "0x0053f770",
                "CDXBitmapFont__ReleaseFontResources",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave595 name/signature/comment hardening: CPCPlatform__UnloadFonts and PCPlatform__DeserializeFontsAndAssets call this resource-release helper for CDXBitmapFont slots. ECX carries this; the body reinstalls vtable 0x005e504c, releases/clears this+0x170 through the embedded +8 counter path, releases/clears cached resources at this+0x174 and this+0x178, and returns without freeing the object. Static retail evidence only; exact lifecycle ownership, resource classes, runtime font unload behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBitmapFont__ctor_like_0053f770", "CDXBitmapFont__ReleaseFontResources"},
                tags("cdxbitmapfont", "resource-release", "font-unload", "owner-corrected")
            ),
            new Spec(
                "0x0053f7d0",
                "CDXBitmapFont__InitNamedFontSlot",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("font_face", charPtr),
                    param("font_size", intType),
                    param("font_style_flags", intType)
                },
                "Wave595 signature/comment hardening: PCPlatform__LoadFonts uses this for the Terminal/debug font slot. RET 0xc proves three stack parameters after this; the body copies the scratch-buffer font face into this+4, stores font_size at this+0x54 and font_style_flags at this+0x58, clears this+0x170, and marks this+0x15c as the GDI/font-face path. Static retail evidence only; exact CDXBitmapFont layout, GDI style semantics, runtime font creation behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXBitmapFont__InitNamedFontSlot"},
                tags("cdxbitmapfont", "named-font-slot", "gdi-font", "ret-0xc", "phantom-param-removed")
            ),
            new Spec(
                "0x0053f830",
                "CDXBitmapFont__InitTextureFontSlot",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("texture_name", charPtr),
                    param("glyph_cell_width", intType)
                },
                "Wave595 name/signature/comment hardening: PCPlatform__LoadFonts uses this for texture-backed main/small/title font slots. RET 0x8 proves two stack parameters after this; the body copies texture_name into this+0x5c, clears the GDI flag at this+0x15c, stores glyph_cell_width at this+0x54, clears this+0x170, and returns. Static retail evidence only; exact CDXBitmapFont layout, texture atlas semantics, runtime font loading behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"PCPlatform__LoadFonts_InitFontSlot", "CDXBitmapFont__InitTextureFontSlot"},
                tags("cdxbitmapfont", "texture-font-slot", "font-loading", "ret-0x8", "phantom-param-removed", "owner-corrected")
            ),
            new Spec(
                "0x0053f880",
                "CDXFont__CreateFromTexture",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave595 signature/comment hardening: CDXFont__DrawTextScaled and CDXFont__GetTextExtent lazily call this when this+0x170 is empty and this+0x15c selects the texture-backed path. ECX carries this; the body temporarily forces the global texture-load flag, loads the texture named at this+0x5c, caches it at this+0x170, records atlas dimensions at this+0x160/+0x164, locks the animated frame, and builds glyph UV/width metrics from alpha coverage. Static retail evidence only; exact CDXFont layout, glyph metric semantics, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFont__CreateFromTexture"},
                tags("cdxfont", "texture-font", "glyph-metrics", "lazy-create")
            ),
            new Spec(
                "0x0053fb00",
                "CDXFont__CreateGDIFont",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave595 signature/comment hardening: CDXFont__DrawTextScaled and CDXFont__GetTextExtent lazily call this when this+0x170 is empty and this+0x15c selects the GDI/font-face path. ECX carries this; the SEH-wrapped body chooses a texture size from this+0x54, creates a CTexture at this+0x170, builds a DIB-backed Windows font from the face/style fields, rasterizes printable characters into the texture, writes glyph metrics, and labels the texture SystemFont. Static retail evidence only; exact CDXFont layout, GDI style semantics, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFont__CreateGDIFont"},
                tags("cdxfont", "gdi-font", "glyph-metrics", "lazy-create", "seh-wrapped")
            ),
            new Spec(
                "0x00540010",
                "CDXFont__DrawTextScaled",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("depth_z", floatType),
                    param("x_scale", floatType),
                    param("y_scale", floatType),
                    param("packed_argb", uintType),
                    param("text", wideTextPtr),
                    param("flags", uintType),
                    param("per_char_argb", floatPtr)
                },
                "Wave595 signature/comment hardening: high-fan-in CDXFont renderer used by HUD/interface/debug text paths and by CDXFont__DrawText. RET 0x24 proves nine stack parameters after this; the body skips empty UTF-16 text, lazily creates texture/GDI font resources, optionally scales normalized coordinates by window size, locks CFastVB quads for non-newline glyphs, applies packed or per-character color, renders the cached texture, restores render state, and returns 0. Static retail evidence only; exact flag bits, vertex format semantics, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFont__DrawTextScaled"},
                tags("cdxfont", "text-render", "wide-text", "ret-0x24", "render-state")
            ),
            new Spec(
                "0x00540640",
                "CDXFont__DrawText",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("packed_argb", uintType),
                    param("text", wideTextPtr),
                    param("flags", uintType),
                    param("per_char_argb", floatPtr),
                    param("depth_z", floatType)
                },
                "Wave595 signature/comment hardening: convenience CDXFont wrapper called by loading screen, debug, interface, menu, heap, and overlay render paths. RET 0x1c proves seven stack parameters after this; the body forwards x/y/depth, default x/y scale of 1.0, packed/per-character color, UTF-16 text, and flags into CDXFont__DrawTextScaled. Static retail evidence only; exact argument naming, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFont__DrawText"},
                tags("cdxfont", "text-render", "wide-text", "ret-0x1c", "wrapper")
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
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave595 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
