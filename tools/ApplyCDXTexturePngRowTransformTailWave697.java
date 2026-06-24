//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
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

public class ApplyCDXTexturePngRowTransformTailWave697 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
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

    private String[] concat(String[] common, String... extras) {
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] signatureTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "cdxtexture-png-row-transform-tail-wave697",
            "wave697-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
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
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
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
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00593d0b",
                "CDXTexture__PngStrip16BitSamplesTo8Bit",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr)
                },
                "Wave697 static read-back: if the row descriptor bit-depth byte at +0x9 is 16, walks width * channel-count 16-bit samples, copies each high byte into the 8-bit row lane, then updates bit depth, bits-per-pixel, and row byte count for an 8-bit row. Static metadata only; exact row descriptor layout, host-endian policy, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "strip16", "expand-to-8bit", "tranche-head")
            ),
            new Spec(
                "0x00593d51",
                "CDXTexture__PngInsertFillerChannel",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("filler_sample_value", uintType),
                    param("layout_flags", uintType)
                },
                "Wave697 static read-back: inserts a filler sample into grayscale or RGB rows for 8-bit and 16-bit sample widths; the filler_sample_value supplies low/high sample bytes and layout_flags bit 0x80 chooses before-color versus after-color placement. Static metadata only; exact filler enum, channel layout contract, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "filler-channel", "layout-flags")
            ),
            new Spec(
                "0x00593f8a",
                "CDXTexture__PngApplyRowTransformLuts",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("byte_lut_table", intType),
                    param("word_lut_table", voidPtr),
                    param("word_lut_index_shift", intType)
                },
                "Wave697 static read-back: applies byte and 16-bit LUT tables across low-bit, 8-bit, and 16-bit grayscale/RGB/alpha row forms, using word_lut_index_shift for the observed 16-bit table index. Static metadata only; exact LUT allocation contract, significant-bits policy, and runtime gamma behavior remain unproven.",
                signatureTags("png", "row-transform", "gamma", "lut", "significant-bits")
            ),
            new Spec(
                "0x005942da",
                "CDXTexture__ExpandIndexedRowToRgbOrRgba",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("palette_rgb_table", voidPtr),
                    param("palette_alpha_table", voidPtr),
                    param("palette_alpha_count", intType)
                },
                "Wave697 static read-back: for indexed-color rows, expands packed 1/2/4-bit indices when needed and rewrites palette indices into RGB or RGBA bytes using the PLTE table plus optional transparency alpha table and alpha count. Static metadata only; exact palette table layout, tRNS semantics, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "palette", "plte", "transparency")
            ),
            new Spec(
                "0x005944e3",
                "CDXTexture__PngExpandTransparentColorToAlpha",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("transparent_color_record", voidPtr)
                },
                "Wave697 static read-back: expands grayscale/RGB rows to carry alpha by comparing pixels against the transparent_color_record, emitting gray+alpha or RGB+alpha output for 8-bit and 16-bit sample widths and updating row metadata. Static metadata only; exact tRNS record layout, comparison policy, and runtime alpha behavior remain unproven.",
                signatureTags("png", "row-transform", "transparency", "trns", "alpha")
            ),
            new Spec(
                "0x00594836",
                "CDXTexture__PngConvertRgbRowsToPaletteIndices",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("rgb_to_palette_lut", voidPtr),
                    param("index_remap_lut", voidPtr)
                },
                "Wave697 static read-back: converts RGB/RGBA 8-bit rows to indexed rows through an observed RGB-to-palette lookup and remaps already-indexed rows through an index LUT when provided, then updates row metadata to indexed color. Static metadata only; exact RGB key packing, palette index policy, and runtime image fidelity remain unproven.",
                signatureTags("png", "row-transform", "palette", "rgb-to-index")
            ),
            new Spec(
                "0x00594945",
                "CDXTexture__BuildPngGammaAndExpandTables",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave697 static read-back: builds PNG gamma or expand LUT storage from the decode state when output gamma or significant-bit transforms require it, allocating byte or word tables and storing the observed word-lut shift at +0x12c. Static metadata only; exact decode-state layout, allocation lifetime, and color-management policy remain unproven.",
                signatureTags("png", "gamma", "lut", "expand-table", "color-management")
            ),
            new Spec(
                "0x00594c48",
                "CDXTexture__ApplyPngPostDecodeTransforms",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave697 static read-back: prepares PNG post-decode transform support by building gamma/expand tables when needed, applying palette gamma adjustment, and shifting PLTE RGB entries according to significant-bit state. Static metadata only; exact transform flag enum, palette mutation contract, and runtime color output remain unproven.",
                signatureTags("png", "postprocess-layout", "gamma", "palette", "significant-bits")
            ),
            new Spec(
                "0x00594d5c",
                "CDXTexture__ApplyPngRowTransforms",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave697 static read-back: dispatches PNG row transforms from the decode state, including palette expansion, transparency alpha, gamma LUTs, strip-16, RGB-to-palette, significant-bit shifts, packed expansion, RGB/BGR swap, filler insertion, and 16-bit byte swap. Static metadata only; exact transform order, row callback ABI, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "dispatcher", "transform-options", "tranche-tail")
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = true;
        if (args != null && args.length > 0) {
            dryRun = isDryRun(args[0]);
        }

        println("ApplyCDXTexturePngRowTransformTailWave697 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
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
    }
}
