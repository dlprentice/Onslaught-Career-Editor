//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyJpegDctComponentUpsamplerHeadWave734 extends GhidraScript {
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
            "jpeg-dct-component-upsampler-head-wave734",
            "wave734-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "jpeg-dct-component-upsampler-head"
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
            Thread.sleep(75);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x005b5b80",
                "CDXTexture__InitJpegDctQuantPipeline",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr)
                },
                "Wave734 static read-back: initializes the JPEG DCT/quant pipeline controller for the active codec state. RET 0x4 caller CDXTexture__InitializeJpegEncoderPipeline reaches this helper; it allocates a 0x30-byte controller through allocator callback +4, stores it at state +0x170, installs controller entry 0x005b4b20, dispatches mode field +0xc4 across cases 0/3/5, 1/4/6, and 2, installs DCT/quant callback entries including 0x005b4ed0, 0x005be000, 0x005bdda0, 0x005b5370, and 0x005bdb70, and raises error id 0x30 for unsupported modes. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact JPEG state layout, DCT/quant controller schema, callback table contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-head", "jpeg-dct-quant-pipeline", "jpeg-mode-dispatch", "encoder-controller", "ret-0x4")
            ),
            new Spec(
                "0x005b60a0",
                "CDXTexture__BuildComponentWorkBufferViews",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr)
                },
                "Wave734 static read-back: builds per-component row/work-buffer view tables beneath the component sample-buffer controller. RET 0x4 caller CDXTexture__InitComponentSampleBuffers invokes this path after detecting the state +0x16c/+8 mode; the helper allocates a component-count by row-count slab, calls allocator callback +8 for each component, copies row pointer ranges, stores view-table pointers through controller state +0x15c/+8, and advances component descriptors in 0x54-byte steps. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact component descriptor schema, allocation callback semantics, sample-buffer layout, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("component-work-buffer-views", "component-sample-buffers", "row-table-views", "ret-0x4")
            ),
            new Spec(
                "0x005b61e0",
                "CDXTexture__InitComponentSampleBuffers",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr),
                    param("sample_buffer_mode", intType)
                },
                "Wave734 static read-back: initializes the component sample-buffer controller and per-component storage. RET 0x8 caller CDXTexture__InitializeJpegEncoderPipeline supplies jpeg_codec_state and sample_buffer_mode; nonzero sample_buffer_mode raises error id 4, the helper allocates a 0x40-byte controller at state +0x15c, chooses direct allocation entry 0x005b5c80 when state +0x16c/+8 is zero, otherwise installs entry 0x005b5e90 and calls CDXTexture__BuildComponentWorkBufferViews. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact sample-buffer controller layout, component descriptor schema, allocation callback semantics, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("component-sample-buffers", "allocator-callbacks", "controller-init", "ret-0x8")
            ),
            new Spec(
                "0x005b6290",
                "CDXTexture__PadRowsWithLastSample",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("row_table", voidPtr),
                    param("row_count", intType),
                    param("valid_width_bytes", intType),
                    param("padded_width_bytes", intType)
                },
                "Wave734 static read-back: pads each sample row from valid_width_bytes to padded_width_bytes by repeating the row's last valid byte. RET 0x10 callers include scalar/SSE horizontal and bilinear upsamplers plus nearby unfenced helpers; the helper walks row_table entries, reads the byte at valid_width_bytes - 1, writes dword repeats for the bulk fill, then writes trailing byte repeats for the remaining 0..3 bytes. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact row-table ownership, sample format, unfenced helper boundaries, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("row-padding", "last-sample-fill", "row-table-helper", "ret-0x10")
            ),
            new Spec(
                "0x005b6500",
                "CDXTexture__UpsampleHorizontal_Average2_Scalar",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("source_row_table", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("output_row_table", voidPtr)
                },
                "Wave734 static read-back: scalar horizontal average-2 upsampler. Dispatch caller CDXTexture__UpsampleDispatchHorizontal loads hidden EAX with jpeg_codec_state, ECX with source_row_table, EDX with component_descriptor, and pushes output_row_table; the helper pads source rows through CDXTexture__PadRowsWithLastSample, then writes averaged adjacent horizontal samples into output rows while toggling the half-pixel rounding term. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact hidden EAX ABI, component descriptor schema, sample format, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("horizontal-upsampler", "scalar-kernel", "hidden-eax-jpeg-state", "average2", "row-table-helper")
            ),
            new Spec(
                "0x005b65a0",
                "CDXTexture__UpsampleHorizontal_Average2_Sse",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("component_descriptor", voidPtr),
                    param("jpeg_codec_state", voidPtr),
                    param("source_row_table", voidPtr),
                    param("output_row_table", voidPtr)
                },
                "Wave734 static read-back: packed/SSE horizontal average-2 upsampler selected by aligned dispatch paths. CDXTexture__UpsampleDispatchHorizontal supplies component_descriptor in ECX, jpeg_codec_state in EDX, source_row_table and output_row_table on the stack; the helper pads source rows, reads vector constants DAT_005f4c00 and DAT_005f4bf0, combines adjacent packed samples, clamps byte results, and writes output rows. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact SIMD source identity, component descriptor schema, sample format, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("horizontal-upsampler", "sse-kernel", "average2", "alignment-gated", "row-table-helper")
            ),
            new Spec(
                "0x005b6650",
                "CDXTexture__UpsampleBilinear2x2_Scalar",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("source_row_table", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("output_row_table", voidPtr)
                },
                "Wave734 static read-back: scalar bilinear 2x2 upsampler. Dispatch caller CDXTexture__UpsampleDispatchBilinear loads hidden EAX with jpeg_codec_state, ECX with source_row_table, EDX with component_descriptor, and pushes output_row_table; the helper pads source rows, reads paired current/next source row bytes, averages a 2x2 neighborhood with alternating rounding bias, and writes output rows. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact hidden EAX ABI, component descriptor schema, sample format, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("bilinear-upsampler", "scalar-kernel", "hidden-eax-jpeg-state", "2x2-average", "row-table-helper")
            ),
            new Spec(
                "0x005b6720",
                "CDXTexture__UpsampleBilinear2x2_Sse",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("component_descriptor", voidPtr),
                    param("jpeg_codec_state", voidPtr),
                    param("source_row_table", voidPtr),
                    param("output_row_table", voidPtr)
                },
                "Wave734 static read-back: packed/SSE bilinear 2x2 upsampler selected by aligned dispatch paths. CDXTexture__UpsampleDispatchBilinear supplies component_descriptor in ECX, jpeg_codec_state in EDX, source_row_table and output_row_table on the stack; the helper pads source rows, reads adjacent current/next row vectors, uses constants DAT_005f4c10 and DAT_005f4c08, averages packed samples, clamps byte results, and writes output rows. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact SIMD source identity, component descriptor schema, sample format, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("bilinear-upsampler", "sse-kernel", "2x2-average", "alignment-gated", "row-table-helper")
            ),
            new Spec(
                "0x005b6c30",
                "CDXTexture__UpsampleDispatchHorizontal",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("source_row_table", voidPtr),
                    param("output_row_table", voidPtr)
                },
                "Wave734 static read-back: dispatches horizontal average-2 upsampling between scalar and packed/SSE kernels. RET 0x10 the helper checks source_row_table alignment, raises error id 2 through the codec error callback when unaligned, checks state +0xc4 for modes 5 or 6 before selecting CDXTexture__UpsampleHorizontal_Average2_Sse, otherwise falls back to CDXTexture__UpsampleHorizontal_Average2_Scalar while preserving hidden EAX jpeg_codec_state for the scalar call. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact mode enum, alignment contract, hidden-register ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("horizontal-upsampler-dispatch", "sse-alignment-gate", "jpeg-mode-5-6", "ret-0x10")
            ),
            new Spec(
                "0x005b6c90",
                "CDXTexture__UpsampleDispatchBilinear",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr),
                    param("component_descriptor", voidPtr),
                    param("source_row_table", voidPtr),
                    param("output_row_table", voidPtr)
                },
                "Wave734 static read-back: dispatches bilinear 2x2 upsampling between scalar and packed/SSE kernels. RET 0x10 the helper checks source_row_table alignment, raises error id 2 through the codec error callback when unaligned, checks state +0xc4 for modes 5 or 6 before selecting CDXTexture__UpsampleBilinear2x2_Sse, otherwise falls back to CDXTexture__UpsampleBilinear2x2_Scalar while preserving hidden EAX jpeg_codec_state for the scalar call. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact mode enum, alignment contract, hidden-register ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("bilinear-upsampler-dispatch", "sse-alignment-gate", "jpeg-mode-5-6", "ret-0x10")
            ),
            new Spec(
                "0x005b6cf0",
                "CDXTexture__InitUpsamplerDispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_codec_state", voidPtr)
                },
                "Wave734 static read-back: allocates and initializes the upsampler dispatch/controller table for JPEG component sampling ratios. RET 0x4 caller CDXTexture__InitializeJpegEncoderPipeline reaches this helper; it allocates a 0x34-byte controller at state +0x16c, installs controller entries 0x005b0ed0 and 0x005b62f0, walks component descriptors in 0x54-byte steps, chooses passthrough, horizontal, bilinear, or generic upsampler entries based on component sampling ratios versus state +0xf0/+0xf4, records slow-path need in controller +8, and raises error ids 0x19, 0x26, or 99 for unsupported cases. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact sampling-ratio schema, generic upsampler helper boundaries, controller layout, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-tail", "upsampler-dispatch-init", "component-sampling-ratio", "dispatch-table", "ret-0x4")
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

        println("ApplyJpegDctComponentUpsamplerHeadWave734 mode=" + (dryRun ? "dry" : "apply"));
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
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave734 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
