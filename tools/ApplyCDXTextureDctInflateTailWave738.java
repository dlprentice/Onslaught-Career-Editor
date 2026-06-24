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

public class ApplyCDXTextureDctInflateTailWave738 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final boolean updateSignature;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, boolean updateSignature, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.updateSignature = updateSignature;
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
            "cdxtexture-dct-inflate-tail-wave738",
            "wave738-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "cdxtexture-dct-inflate-tail"
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
        if (spec.updateSignature && !signatureMatches(fn, spec)) {
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
        if (spec.updateSignature && !signatureMatches(readBack, spec)) {
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

            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
            boolean needsAnyUpdate = needsUpdate(fn, spec);
            String signatureText = spec.updateSignature ? expectedSignature(spec) : fn.getSignature().toString();
            if (!needsAnyUpdate) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + signatureText);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " " + signatureText);
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
            }
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            else {
                stats.commentOnlyUpdated++;
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + signatureText);
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x005bb9b0",
                "CDXTexture__InverseDct8x8_DequantAndStore_Scalar",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("coefficient_block_rows", voidPtr),
                    param("quant_table_rows", voidPtr),
                    param("idct_workspace_rows", voidPtr),
                    param("row_offset_table", intPtr),
                    param("output_base", intType),
                    param("clamp_table", voidPtr)
                },
                "Wave738 static read-back: scalar 8x8 inverse-DCT/dequantize/output-store helper reached through a no-function wrapper at 0x005bbe20. RET 0x18 and the wrapper call at 0x005bbe59 show six stack parameters; the body multiplies coefficient and quant table rows, writes an IDCT workspace, then clamps and stores two packed output dwords per row through row_offset_table/output_base/clamp_table. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact JPEG color pipeline role, source identity, runtime image behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-head", "dct-scalar", "ret-0x18", "no-function-wrapper")
            ),
            new Spec(
                "0x005bbe70",
                "CDXTexture__InverseDct8x8_DequantAndStore_Mmx",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("coefficient_block_rows", voidPtr),
                    param("quant_table_rows", voidPtr),
                    param("idct_workspace_rows", voidPtr),
                    param("row_offset_table", intPtr),
                    param("output_base", intType),
                    param("clamp_table", voidPtr)
                },
                "Wave738 static read-back: MMX-style twin of the 8x8 inverse-DCT/dequantize/output-store helper reached through a no-function wrapper at 0x005bc530. RET 0x18 and the wrapper call at 0x005bc569 show six stack parameters; the body performs packed multiply/add IDCT work, clamps through clamp_table, writes through row_offset_table/output_base, and returns a constant zero that the wrapper does not inspect. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact SIMD equivalence, JPEG color pipeline role, source identity, runtime image behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("dct-mmx", "ret-0x18", "no-function-wrapper")
            ),
            new Spec(
                "0x005bcfa0",
                "CDXTexture__InflateCodesState_Create",
                true,
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("literal_bits", intType),
                    param("distance_bits", intType),
                    param("literal_table", voidPtr),
                    param("distance_table", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave738 static read-back: inflate code-state allocator called by CDXTexture__InflateProcessBlockHeader after fixed and dynamic table setup. RET 0x14 and calls at 0x005b1fbf/0x005b2410 show five stack parameters; the body allocates a 0x1c-byte state through inflate_stream callbacks, stores literal/distance bit widths at offsets 0x10/0x11, stores literal/distance table pointers at offsets 0x14/0x18, and returns the allocated state pointer. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib version/source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-code-state", "ret-0x14", "allocator-callback")
            ),
            new Spec(
                "0x005bcfd3",
                "CDXTexture__InflateCodesState_Process",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_state", voidPtr),
                    param("inflate_stream", voidPtr),
                    param("status_code", intType)
                },
                "Wave738 static read-back: inflate code-state processor called by CDXTexture__InflateProcessBlockHeader. RET 0xc and the call at 0x005b2455 show three stack parameters, and the caller immediately compares EAX against 1, so the stale void return is corrected to an int status return; the body drives literal/length and distance code states, calls CDXTexture__InflateFast_DecodeBlockStream, flushes through CDXTexture__InflateOutputWindowFlush, and writes zlib-style error text for invalid literal/length and distance codes. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib version/source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-code-state", "ret-0xc", "status-return", "invalid-code-errors")
            ),
            new Spec(
                "0x005bd52a",
                "CDXTexture__InvokeReleaseCallback",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("release_payload", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave738 static read-back: two-argument callback wrapper used by CDXTexture__ResetDecodeWindowState and CDXTexture__InflateProcessBlockHeader to release an inflate code-state payload through inflate_stream +0x24 with user data at +0x28. RET 0x8 and calls at 0x005b1de8/0x005b246b show two stack parameters. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact allocator ownership model, source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-callback", "ret-0x8", "release-callback")
            ),
            new Spec(
                "0x005bd8ba",
                "CDXTexture__InflateDynamicTree_BuildBitLengthTree",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("code_length_count", intType),
                    param("bit_length_count_out", voidPtr),
                    param("tree_workspace", voidPtr),
                    param("bit_length_order_table", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave738 static read-back: dynamic inflate bit-length Huffman table builder called at 0x005b225a. RET 0x14 and the call-site pushes show five stack parameters; the body allocates a 0x13-entry work table through inflate_stream callbacks, calls CDXTexture__BuildInflateHuffmanTable, writes oversubscribed/incomplete dynamic bit-length tree errors, frees the work table, and returns a zlib-style status code. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib version/source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-dynamic-tree", "ret-0x14", "huffman-table", "bit-length-tree")
            ),
            new Spec(
                "0x005bd933",
                "CDXTexture__InflateDynamicTree_BuildLitDistTrees",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("literal_length_count", intType),
                    param("distance_count", intType),
                    param("code_lengths", voidPtr),
                    param("literal_bits_out", voidPtr),
                    param("distance_bits_out", voidPtr),
                    param("literal_table_out", voidPtr),
                    param("distance_table_out", voidPtr),
                    param("tree_workspace", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave738 static read-back: dynamic inflate literal/length and distance Huffman tree builder called at 0x005b23f3. RET 0x24 and the call-site pushes show nine stack parameters, correcting the stale five-parameter signature and hidden in_stack_00000024 allocator stream; the body allocates a 0x120-entry work table, builds literal/length and distance tables through CDXTexture__BuildInflateHuffmanTable, writes oversubscribed/incomplete/empty tree errors, frees the work table, and returns a zlib-style status code. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib version/source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-dynamic-tree", "ret-0x24", "huffman-table", "litdist-tree")
            ),
            new Spec(
                "0x005bda2d",
                "CDXTexture__InflateFixedTrees_InitDescriptors",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("literal_bits_out", voidPtr),
                    param("distance_bits_out", voidPtr),
                    param("literal_table_out", voidPtr),
                    param("distance_table_out", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave738 static read-back: fixed inflate descriptor initializer called at 0x005b1fad before CDXTexture__InflateCodesState_Create. RET 0x14 and the call-site pushes show five stack parameters; the body writes fixed literal/distance bit counts and fixed table pointers from DAT_0065ee58/DAT_0065ee5c/DAT_0065ee60/DAT_0065fe60, while the fifth stream argument is an unused ABI slot for the surrounding inflate helper family. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib version/source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-fixed-tree", "ret-0x14", "descriptor-init")
            ),
            new Spec(
                "0x005bda5e",
                "CDXTexture__InflateOutputWindowFlush",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_state", voidPtr),
                    param("inflate_stream", voidPtr),
                    param("status_code", intType)
                },
                "Wave738 static read-back: inflate output-window flush helper called from CDXTexture__InflateProcessBlockHeader and CDXTexture__InflateCodesState_Process. RET 0xc and multiple call-site push sequences show three stack parameters; the body copies pending ring-window bytes to the stream output buffer, invokes the output callback at inflate_state +0x38 when present, updates stream counters, clears -5 to 0 when progress is made, and returns the status code. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact stream structure, runtime decompression behavior, source identity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate-output-window", "ret-0xc", "status-return", "output-callback")
            ),
            new Spec(
                "0x005be360",
                "CDXTexture__InflateFast_DecodeBlockStream",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("literal_bits", intType),
                    param("distance_bits", intType),
                    param("literal_table", voidPtr),
                    param("distance_table", voidPtr),
                    param("inflate_state", voidPtr),
                    param("inflate_stream", voidPtr)
                },
                "Wave738 static read-back: fast inflate literal/length-distance decode helper called by CDXTexture__InflateCodesState_Process at 0x005bd067. RET 0x18 and the call-site pushes show six stack parameters; the body uses mask table DAT_0065ff60, decodes literals/copy lengths/distances, updates stream/window counters, returns 0/1/-3 status values, and writes invalid distance or invalid literal/length code error text on failure. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact zlib version/source identity, runtime decompression behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-tail", "inflate-fast-decode", "ret-0x18", "status-return", "invalid-code-errors")
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

        println("ApplyCDXTextureDctInflateTailWave738 mode=" + (dryRun ? "dry" : "apply"));
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

        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave738 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
