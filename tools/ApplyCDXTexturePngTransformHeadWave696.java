//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCDXTexturePngTransformHeadWave696 extends GhidraScript {
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
            "cdxtexture-png-transform-head-wave696",
            "wave696-readback-verified",
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
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00593812",
                "CDXTexture__ConfigureFillerChannel",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("filler_sample_value", intType),
                    param("place_filler_after_color", intType)
                },
                "Wave696 static read-back: sets the PNG transform option byte at +0x61 bit 0x80, stores the low-byte filler sample value at +0x11e, toggles layout flag +0x5c bit 0x80 from the place_filler_after_color selector, and adjusts observed output channel metadata for palette/color-type and bit-depth combinations. Static metadata only; exact filler-channel enum, channel-order contract, and runtime filler behavior remain unproven.",
                signatureTags("png", "filler-channel", "transform-options", "layout-flags", "tranche-head")
            ),
            new Spec(
                "0x00593861",
                "CDXTexture__Swap16BitSampleByteOrder",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr)
                },
                "Wave696 static read-back: when the row descriptor bit-depth byte at +0x9 is 16, walks width * channel-count 16-bit samples and swaps the two bytes of each sample in place. Static metadata only; exact row descriptor layout, sample count contract, endian policy, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "swap16", "byte-order")
            ),
            new Spec(
                "0x00593890",
                "CDXTexture__SwapRgbBgrChannelOrder",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr)
                },
                "Wave696 static read-back: for RGB/RGBA row descriptors, swaps red and blue lanes in place across 8-bit and 16-bit samples, using 3/4 byte strides for 8-bit rows and 6/8 byte strides for 16-bit rows. Static metadata only; exact color-type enum, channel stride contract, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "rgb-bgr-swap", "channel-order")
            ),
            new Spec(
                "0x00593951",
                "CDXTexture__SetGammaCorrectionParams",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("file_gamma", doubleType),
                    param("display_gamma", doubleType)
                },
                "Wave696 static read-back: compares file_gamma * display_gamma against the observed default tolerance, sets transform option bit 0x20 when correction is needed, and stores the two gamma inputs as floats at +0x130/+0x134. Static metadata only; exact gamma parameter order, constants, color-management policy, and runtime output behavior remain unproven.",
                signatureTags("png", "gamma", "transform-options", "color-management")
            ),
            new Spec(
                "0x00593989",
                "CDXTexture__EnablePaletteExpansion",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave696 static read-back: sets PNG transform option bit 0x10 at decode-state +0x61, enabling the nearby palette expansion/layout path. Static metadata only; exact transform-option enum and runtime palette expansion behavior remain unproven.",
                signatureTags("png", "palette", "transform-options", "plte")
            ),
            new Spec(
                "0x00593994",
                "CDXTexture__ApplyPngPostprocessLayoutFlags",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr)
                },
                "Wave696 static read-back: applies transform option/layout flags to PNG info metadata, including palette expansion, gamma propagation, 16-bit strip-to-8-bit layout, RGB-to-palette fallback, packed-sample expansion, channel-count derivation, bits-per-pixel calculation, and row-stride update. Static metadata only; exact info-state layout, color-type enum, flag enum, and runtime layout behavior remain unproven.",
                signatureTags("png", "postprocess-layout", "palette", "gamma", "row-stride")
            ),
            new Spec(
                "0x00593a81",
                "CDXTexture__PngExpandPackedSamplesTo8Bit",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr)
                },
                "Wave696 static read-back: expands packed 1/2/4-bit samples into one byte per sample from the end of the row, then updates bit depth to 8, bits-per-pixel to channel-count * 8, and row byte count to width * channel-count. Static metadata only; exact row descriptor layout, packed-sample ordering, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "packed-samples", "expand-to-8bit")
            ),
            new Spec(
                "0x00593b92",
                "CDXTexture__PngShiftPackedSamplesBySigBits",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_row_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("significant_bits_table", voidPtr)
                },
                "Wave696 static read-back: derives per-channel right-shift counts from row bit depth and the significant-bits table, clamps non-positive shifts to zero, and applies in-place shifts for 2/4/8/16-bit sample forms across grayscale, RGB, and alpha-bearing rows. Static metadata only; exact significant-bits table layout, return-value meaning, channel enum, and runtime row behavior remain unproven.",
                signatureTags("png", "row-transform", "significant-bits", "packed-samples", "tranche-tail")
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

        println("ApplyCDXTexturePngTransformHeadWave696 mode=" + (dryRun ? "dry" : "apply"));
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
