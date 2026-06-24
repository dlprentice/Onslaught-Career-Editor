//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCDXTexturePngOptionAccessorsWave695 extends GhidraScript {
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
            "cdxtexture-png-option-accessors-wave695",
            "wave695-readback-verified",
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
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType doublePtr = new PointerDataType(DoubleDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00593526",
                "CDXTexture__ReleasePngDecodeContextHandles",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_context_slot", voidPtr),
                    param("primary_row_workspace_slot", voidPtr),
                    param("secondary_row_workspace_slot", voidPtr)
                },
                "Wave695 static read-back: releases a PNG decode context slot and its optional primary/secondary row workspace slots by reading each slot, calling CDXTexture__ResetPngDecodeContext for the live context, freeing non-null row workspaces with CDXTexture__FreeDecodeState, freeing the decode context, and clearing every owned slot back to null. Static metadata only; exact slot ownership, cleanup ordering requirements, allocator ABI, and runtime PNG cleanup behavior remain unproven.",
                signatureTags("png", "cleanup", "owned-slot-release", "row-workspace", "tranche-head")
            ),
            new Spec(
                "0x005935a3",
                "CDXTexture__TestDecodeOptionFlagMask",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("flag_mask", uintType)
                },
                "Wave695 static read-back: null-checks the decode and info states, then returns info_state +0x8 masked by flag_mask; this matches the local valid-option bit test used by nearby PNG info accessors. Static metadata only; exact info-state layout, flag enum identity, and runtime option behavior remain unproven.",
                signatureTags("png", "option-flags", "info-state", "bitmask")
            ),
            new Spec(
                "0x005935c0",
                "CDXTexture__GetDecodeRowStride",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr)
                },
                "Wave695 static read-back: null-checks the decode and info states, then returns the row-stride field at info_state +0xc. Static metadata only; exact rowbytes type, row-stride layout, and runtime decoded-row size behavior remain unproven.",
                signatureTags("png", "row-stride", "info-state", "accessor")
            ),
            new Spec(
                "0x005935d9",
                "CDXTexture__GetOutputChannelCount",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr)
                },
                "Wave695 static read-back: null-checks the decode and info states, then returns the one-byte channel count field observed at info_state +0x1d. Static metadata only; exact channel-count field identity, color-type relationship, and runtime decoded-channel behavior remain unproven.",
                signatureTags("png", "channel-count", "info-state", "accessor")
            ),
            new Spec(
                "0x005935f2",
                "CDXTexture__GetOutputGamma",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("out_gamma", doublePtr)
                },
                "Wave695 static read-back: requires decode/info state, valid-option bit 0x1, and a non-null output pointer, then widens the float at info_state +0x28 into the output double and returns success. Static metadata only; exact gamma field source, numeric conversion policy, and runtime color-management behavior remain unproven.",
                signatureTags("png", "gamma", "info-state", "output-pointer", "accessor")
            ),
            new Spec(
                "0x0059361e",
                "CDXTexture__GetRenderingIntent",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("out_rendering_intent", intPtr)
                },
                "Wave695 static read-back: requires decode/info state, valid-option bit 0x800, and a non-null output pointer, writes the byte at info_state +0x2c to the rendering-intent output, and returns 0x800. Static metadata only; exact rendering-intent enum, sRGB contract, and runtime color-management behavior remain unproven.",
                signatureTags("png", "rendering-intent", "srgb", "info-state", "output-pointer")
            ),
            new Spec(
                "0x0059371d",
                "CDXTexture__GetPaletteBufferInfo",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("out_palette_buffer", voidPtr),
                    param("out_palette_count", intPtr)
                },
                "Wave695 static read-back: requires decode/info state, valid-option bit 0x8, and a non-null palette-buffer output, then returns the palette pointer from info_state +0x10 and the 16-bit palette count from +0x14 before returning 0x8. Static metadata only; exact palette pointer type, output nullability contract, palette count bounds, and runtime palette behavior remain unproven.",
                signatureTags("png", "palette", "plte", "info-state", "output-pointer")
            ),
            new Spec(
                "0x00593753",
                "CDXTexture__GetTransparencyInfo",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_info_state", voidPtr),
                    param("out_transparency_table", voidPtr),
                    param("out_transparency_count", intPtr),
                    param("out_transparent_color", voidPtr)
                },
                "Wave695 static read-back: requires decode/info state and valid-option bit 0x10, branches on color type byte +0x19, returns the palette alpha table at +0x30 for indexed color, returns the transparent-color record at +0x34 when requested, writes the 16-bit transparency count from +0x16, and clears the table pointer for non-indexed color. Static metadata only; exact tRNS structure layout, output nullability contract, color-type enum, and runtime transparency behavior remain unproven.",
                signatureTags("png", "transparency", "trns", "info-state", "output-pointer")
            ),
            new Spec(
                "0x005937bc",
                "CDXTexture__EnableByteSwapTransform",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave695 static read-back: sets transform flag bit 0x1 at png_decode_state +0x60, used by the nearby PNG postprocess transform setup path. Static metadata only; exact transform-flag enum and runtime byte/channel swap behavior remain unproven.",
                signatureTags("png", "transform-flags", "byte-swap")
            ),
            new Spec(
                "0x005937c7",
                "CDXTexture__EnableSwap16TransformIfNeeded",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave695 static read-back: checks the observed bit-depth byte at png_decode_state +0x117 and sets transform flag bit 0x10 at +0x60 only when the value is 16. Static metadata only; exact bit-depth field identity, transform-flag enum, and runtime 16-bit sample byte-order behavior remain unproven.",
                signatureTags("png", "transform-flags", "bit-depth", "swap16")
            ),
            new Spec(
                "0x005937db",
                "CDXTexture__EnableExpandTo8Bit",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave695 static read-back: when the observed bit-depth byte at png_decode_state +0x117 is below 8, sets transform flag bit 0x4 at +0x60 and raises the output bit-depth byte at +0x118 to 8. Static metadata only; exact input/output bit-depth fields, packed-sample expansion semantics, and runtime output-row behavior remain unproven.",
                signatureTags("png", "transform-flags", "bit-depth", "expand-to-8bit")
            ),
            new Spec(
                "0x005937f6",
                "CDXTexture__GetPngPassCountFromInterlace",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave695 static read-back: returns one pass when the interlace byte at png_decode_state +0x113 is zero; otherwise sets transform flag bit 0x2 at +0x60 and returns seven passes for the Adam7 path. Static metadata only; exact interlace enum, transform-flag side effect, Adam7 table semantics, and runtime interlace behavior remain unproven.",
                signatureTags("png", "interlace", "adam7", "pass-count", "tranche-tail")
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

        println("ApplyCDXTexturePngOptionAccessorsWave695 mode=" + (dryRun ? "dry" : "apply"));
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
