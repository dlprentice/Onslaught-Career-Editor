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

public class ApplyJpegScanHuffmanHeadWave725 extends GhidraScript {
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
            "jpeg-scan-huffman-head-wave725",
            "wave725-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "jpeg-scan-huffman"
        }, extras);
    }

    private String[] commentTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "jpeg-scan-huffman-head-wave725",
            "wave725-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "hidden-register-context",
            "jpeg-scan-huffman"
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        return new Spec[] {
            new Spec(
                "0x005aba90",
                "CDXTexture__SelectNextScanTableForProgress",
                true,
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave725 static read-back: selects/reset the next JPEG scan table progress state using the ECX texture/decode context. It updates the scan/controller block at context +0x1b0, chooses the next scan table count from component descriptor fields under +0x150/+0x144/+0x98, and resets scan-progress counters at +0x14/+0x18. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact JPEG/decode context layout, scan table schema, progressive/baseline policy, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("scan-table", "scan-progress", "fastcall-ecx-context", "tranche-head")
            ),
            new Spec(
                "0x005ac180",
                "CDXTexture__ValidateAndIndexQuantTables",
                false,
                "__stdcall",
                intType,
                new ParameterImpl[] {},
                "Wave725 static read-back: validates component quantization table availability and copies per-component table indexes into the decode color/scan controller using hidden EBX texture/decode context. It requires component descriptors under +0xdc, quant/source tables under +0xa4, row/sample fields under +0xe0, allocates the controller table at scan block +0x70 if needed, and returns whether any copied table selector is nonzero. Ghidra still exposes locked hidden EBX storage, so the current int(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, component descriptor schema, quant table descriptor schema, hidden EBX ABI, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("quant-table", "component-descriptor", "hidden-ebx-context", "comment-only")
            ),
            new Spec(
                "0x005ac930",
                "CDXTexture__SelectColorConvertEntryPoint",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave725 static read-back: selects the color-conversion entry point for a texture/decode context. It checks the scan/controller block at context +0x1b0, calls the quant-table validator when context +0x50 is set, installs LAB_005ac2d0 for the indexed quant-table path or LAB_005abff0 as fallback, and clears context +0xa0 before return. RET 0x4 evidence restores the single stack argument as decode_context. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, callback table contract, color conversion policy, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("color-conversion", "callback-selector", "quant-table", "ret-0x4")
            ),
            new Spec(
                "0x005ac980",
                "CDXTexture__InitColorConversionResources",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("decode_context", voidPtr) },
                "Wave725 static read-back: initializes color-conversion resources for a texture/decode context. It allocates a 0x74-byte controller at context +0x1b0, installs setup/select callbacks, either allocates per-component row resources when the hidden EBX mode flag is nonzero or allocates a shared 0x500-byte table block with fixed 0x80-byte slices, and stores callback/data pointers into the controller. RET 0x4 evidence restores the single stack argument as decode_context; hidden EBX remains a mode/context signal that is documented but not promoted into the signature. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, hidden EBX ABI, callback table contract, resource ownership, runtime image decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("color-conversion", "resource-init", "hidden-ebx-mode", "allocator", "ret-0x4")
            ),
            new Spec(
                "0x005acac0",
                "CDXTexture__BuildJpegHuffmanDecodeTable",
                true,
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_context", voidPtr),
                    param("table_class", intType),
                    param("table_index", intType),
                    param("decode_table_slot", voidPtr)
                },
                "Wave725 static read-back: builds a JPEG Huffman decode lookup table from the decode context's DC/AC table descriptors. RET 0x10 evidence restores decode_context, table_class, table_index, and decode_table_slot; the function validates table_index range, selects DC versus AC descriptor bases, allocates a 0x590-byte table when the slot is empty, builds max-code/offset arrays, fills an 8-bit fast lookup table at +0x90 and symbol table at +0x490, and validates AC run-length symbols. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact JPEG context layout, DHT descriptor schema, decode-table layout, error callback ABI, runtime Huffman decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("huffman", "decode-table", "dht", "ret-0x10")
            ),
            new Spec(
                "0x005acd90",
                "CDXTexture__BitstreamReadBitsWithJpegStuffing",
                true,
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("bitstream_state", voidPtr),
                    param("bit_buffer", uintType),
                    param("bit_count", intType),
                    param("min_bits", intType)
                },
                "Wave725 static read-back: refills a JPEG entropy bitstream state while honoring 0xff byte-stuffing and marker detection. RET 0x10 evidence restores bitstream_state, bit_buffer, bit_count, and min_bits; the function pulls bytes through the source callback at context slot +0x18/+0xc, converts 0xff00 to literal 0xff, records nonzero marker bytes at decoder +0x1a4, pads to 25 bits after marker/error state when needed, writes the updated source pointer/count/bit buffer/bit count back to the bitstream state, and returns success/failure. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact entropy state layout, source callback contract, marker/error policy, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("bitstream", "jpeg-stuffing", "marker-detection", "ret-0x10")
            ),
            new Spec(
                "0x005aceb0",
                "CDXTexture__DecodeHuffmanSymbolFromBitstream",
                true,
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("bitstream_state", voidPtr),
                    param("bit_buffer", uintType),
                    param("bit_count", intType),
                    param("huffman_table", voidPtr),
                    param("min_bits", intType)
                },
                "Wave725 static read-back: decodes one JPEG Huffman symbol from the entropy bitstream. RET 0x14 evidence restores bitstream_state, bit_buffer, bit_count, huffman_table, and min_bits; the function refills through CDXTexture__BitstreamReadBitsWithJpegStuffing when needed, grows the code until it is within the table's max-code entries, writes back the updated bit buffer/count, returns the symbol through the table descriptor at +0x8c/+0x48, and reports error id 0x76 when no valid code length is found. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact entropy state layout, Huffman table layout, error callback ABI, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("huffman", "bitstream", "symbol-decode", "ret-0x14")
            ),
            new Spec(
                "0x005acf90",
                "CDXTexture__FinalizeScanBitstreamState",
                false,
                "__stdcall",
                intType,
                new ParameterImpl[] {},
                "Wave725 static read-back: finalizes JPEG scan bitstream state using the hidden ESI texture/decode context. It advances the source byte position by the buffered-bit count, clears the entropy bit count, calls the scan/source flush callback, zeroes per-component restart/history slots for the component count at +0x14c, stores the restart interval/state value from context +0x118, and clears the scan marker field when context +0x1a4 is zero. Ghidra still exposes locked hidden ESI storage, so the current int(void) signature is intentionally retained. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact context layout, entropy state layout, callback ABI, restart/marker policy, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.",
                commentTags("scan-bitstream", "finalize", "hidden-esi-context", "tranche-tail")
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

        println("ApplyJpegScanHuffmanHeadWave725 mode=" + (dryRun ? "dry" : "apply"));
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
