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

public class ApplyDecodeRowUtilityHeadWave712 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final boolean updateSignature;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, boolean updateSignature, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.updateSignature = updateSignature;
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
            "decode-row-utility-head-wave712",
            "wave712-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "decode-row-utility-head"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "decode-row-utility-head-wave712",
            "wave712-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only-hidden-abi",
            "decode-row-utility-head"
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
        if (!spec.updateSignature) {
            return true;
        }
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
        if (!spec.updateSignature) {
            return "<comment/tag-only; saved signature intentionally unchanged>";
        }
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
            boolean needsSignature = spec.updateSignature && !signatureMatches(fn, spec);
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
                if (!spec.updateSignature) {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actual=" + fn.getSignature() + " expected=" + expectedSignature(spec));
                return;
            }
            if (spec.updateSignature) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                    SourceType.USER_DEFINED, spec.parameters);
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
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
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(75);
        }
        catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0059c070",
                "CTexture__ProcessRowBatchesLinearStride",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave712 static read-back: RET 0x8 and decompile/xrefs show a row-batch walker that uses a hidden ESI row-batch descriptor plus two visible stack arguments. The helper advances linear row pointers using descriptor row stride, descriptor batch bounds, and descriptor row limit fields, then invokes callback slot [0xc] with a byte offset/size when the visible mode argument is zero, or callback slot [0xd] with the row pointer otherwise. Signature intentionally left unchanged because Ghidra still exposes hidden unaff_ESI context and visible param_ names. Static metadata only; exact row-batch descriptor layout, callback ABI, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("row-batch-hidden-esi", "linear-row-batches", "ret-0x8", "tranche-head")
            ),
            new Spec(
                "0x0059c110",
                "CTexture__ProcessRowBatchesMcuStride128",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave712 static read-back: RET 0x8 and decompile/xrefs show the MCU-stride companion to the linear row-batch walker, again using a hidden ESI row-batch descriptor plus two visible stack arguments. The helper advances row pointers through the descriptor and invokes callback slot [0xc] with byte offset/size multiplied by 0x80 when the visible mode argument is zero, or callback slot [0xd] with the row pointer otherwise. Signature intentionally left unchanged because Ghidra still exposes hidden unaff_ESI context and visible param_ names. Static metadata only; exact row-batch descriptor layout, callback ABI, MCU/component semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("row-batch-hidden-esi", "mcu-row-batches", "ret-0x8")
            ),
            new Spec(
                "0x0059c630",
                "CTexture__AllocJpegQuantTableDescriptor",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                true,
                "Wave712 static read-back: RET 0x4 and callers from CTexture__LoadAndScaleQuantizationTable and CDXTexture__DecodeJpegSegment_QuantizationTables show one decode-state argument. The helper allocates a 0x84 JPEG quantization-table descriptor through the allocator stored at decode_state +4 using bank 0, stores the resulting descriptor at decode_state +0x20, and clears descriptor +0x80. Static metadata only; exact descriptor schema, allocator contract, runtime JPEG behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-quant-table", "descriptor-allocation", "ret-0x4")
            ),
            new Spec(
                "0x0059c650",
                "CTexture__AllocJpegHuffmanTableDescriptor",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                true,
                "Wave712 static read-back: RET 0x4 and callers from CTexture__LoadHuffmanTableDefinition and CDXTexture__DecodeJpegSegment_HuffmanTables show one decode-state argument. The helper allocates a 0x118 JPEG Huffman-table descriptor through the allocator stored at decode_state +4 using bank 0, stores the resulting descriptor at decode_state +0x24, and clears descriptor +0x114. Static metadata only; exact descriptor schema, allocator contract, runtime JPEG behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-huffman-table", "descriptor-allocation", "ret-0x4")
            ),
            new Spec(
                "0x0059c670",
                "CDXTexture__CeilDiv",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("value", intType),
                    param("divisor", intType)
                },
                true,
                "Wave712 static read-back: RET 0x8 and callers from JPEG/decode geometry builders show a two-argument integer ceiling-division helper. The helper returns (value + divisor - 1) / divisor and is used around MCU/layout geometry calculations. Static metadata only; divisor validity, exact geometry ownership, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("ceil-div", "geometry-helper", "ret-0x8")
            ),
            new Spec(
                "0x0059c690",
                "CDXTexture__AlignUpToMultiple",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("value", intType),
                    param("multiple", intType)
                },
                true,
                "Wave712 static read-back: RET 0x8 and callers from color-conversion, entropy-decode, and encoder working-buffer initializers show a two-argument integer align-up helper. The helper computes the next value aligned to the requested multiple by subtracting the remainder from value + multiple - 1. Static metadata only; multiple validity, exact workspace layout, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("align-up", "workspace-helper", "ret-0x8")
            ),
            new Spec(
                "0x0059c6b0",
                "CTexture__CopyRowsFromPointerTable",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("src_row_table", voidPtr),
                    param("src_row_index", intType),
                    param("dst_row_table", voidPtr),
                    param("dst_row_index", intType),
                    param("row_count", intType),
                    param("bytes_per_row", uintType)
                },
                true,
                "Wave712 static read-back: RET 0x18 and row-copy callsites show source row table/index, destination row table/index, row count, and bytes-per-row arguments. The helper walks row pointer tables, copies row_count rows from source to destination, and copies each row as dwords followed by remaining tail bytes. Static metadata only; exact row-table ownership, format/component semantics, runtime texture behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("row-pointer-copy", "copy-helper", "ret-0x18")
            ),
            new Spec(
                "0x0059c700",
                "CFastVB__CopyBlockRows128Bytes",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("src", voidPtr),
                    param("dst", voidPtr),
                    param("block_row_count", intType)
                },
                true,
                "Wave712 static read-back: RET 0xc and the caller at 0x005ac57f show source pointer, destination pointer, and 128-byte block-row count arguments. The helper copies block_row_count << 7 bytes from source to destination using dword moves; the byte-tail loop is structurally present but zero for 128-byte multiples. Static metadata only; exact block ownership, caller context, runtime vertex-buffer/texture behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("copy-128-byte-blocks", "copy-helper", "ret-0xc")
            ),
            new Spec(
                "0x0059c730",
                "CDXTexture__ZeroBufferBytes",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("buffer", voidPtr),
                    param("byte_count", uintType)
                },
                true,
                "Wave712 static read-back: RET 0x8 and calls from row-batch/decode helpers show buffer pointer and byte-count arguments. The helper zeroes byte_count bytes at the buffer using dword stores followed by remaining tail-byte stores. Static metadata only; exact buffer ownership, lifetime, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("zero-buffer", "clear-helper", "ret-0x8")
            ),
            new Spec(
                "0x0059c750",
                "CDXTexture__BeginAsyncDecodeJob",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("decode_job", voidPtr)
                },
                true,
                "Wave712 static read-back: RET 0x4 and callers from CDXTexture__InflateInitStateFromHeader and CDXTexture__ProcessIdatChunkDataAndQueueDecode show one decode-job argument. The helper returns -2 for null job/state inputs, otherwise clears job fields, seeds the pointed decode-state status word to 7 or 0 based on its async flag, calls CDXTexture__ResetDecodeWindowState with the decode-state window at +0x14, and returns 0. Static metadata only; exact job/state layout, async state enum, runtime PNG/decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("async-decode-job", "decode-job-begin", "ret-0x4")
            ),
            new Spec(
                "0x0059c78f",
                "CDXTexture__FinishAsyncDecodeJob",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("decode_job", voidPtr)
                },
                true,
                "Wave712 static read-back: RET 0x4 and callers from CDXTexture__ResetPngDecodeContext and CDXTexture__InflateInitStateFromHeader show one decode-job argument. The helper returns -2 for null job/state/callback inputs, closes async handles from decode-state +0x14 when present, invokes the completion callback stored at decode_job +0x24 with callback context +0x28 and the decode-state pointer, clears decode_job +0x1c, and returns 0. Static metadata only; exact job/state layout, callback ABI, runtime PNG/decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("async-decode-job", "decode-job-finish", "ret-0x4", "tranche-tail")
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

        println("ApplyDecodeRowUtilityHeadWave712 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave712 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
