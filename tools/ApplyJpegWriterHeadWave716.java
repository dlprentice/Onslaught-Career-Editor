//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyJpegWriterHeadWave716 extends GhidraScript {
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
            "jpeg-writer-head-wave716",
            "wave716-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "jpeg-writer-head"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "jpeg-writer-head-wave716",
            "wave716-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "jpeg-writer-head"
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
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);

            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            if (!spec.updateSignature) {
                stats.commentOnlyUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType charType = CharDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0059dfb2",
                "CDXTexture__Crc32_Update",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("crc_seed", uintType),
                    param("source_bytes", voidPtr),
                    param("byte_count", uintType)
                },
                true,
                "Wave716 static read-back: updates a CRC-32 value through table DAT_005f3ec0, complements the incoming seed and final value, returns zero for a null source buffer, processes an unrolled 8-byte body loop, then handles remaining tail bytes. Static metadata only; exact caller ownership of source_bytes, checksum role across every texture container, runtime JPEG/PNG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("crc32", "texture-checksum", "table-driven", "tranche-head")
            ),
            new Spec(
                "0x0059e0b0",
                "CDXTexture__WriteJpegMarkerByte",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("marker_byte", intType) },
                true,
                "Wave716 static read-back: writes the 0xff marker prefix and marker_byte into the ESI-held JPEG writer output buffer, flushing through the writer callback when the buffer fills and reporting error id 0x18 if the flush path fails. Static metadata only; the writer context is still register-held in ESI, exact output-manager ABI, callback result contract, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "marker-writer", "output-buffer", "hidden-esi-context")
            ),
            new Spec(
                "0x0059e110",
                "CDXTexture__WriteJpegQuantTable",
                "__stdcall",
                charType,
                new ParameterImpl[] { param("quant_table_index", intType) },
                true,
                "Wave716 static read-back: validates the ESI-held encoder state's quant-table descriptor for quant_table_index, emits DQT marker 0xffdb, computes 8-bit versus 16-bit precision from the 64 table entries, writes the length and precision/id byte, outputs values in zigzag order through DAT_005f37f8, marks the table descriptor as written, and reports error id 0x34 when the table is missing. Static metadata only; bool-like char return semantics, quant-table descriptor layout, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "quant-table", "DQT", "zigzag", "hidden-esi-context")
            ),
            new Spec(
                "0x0059e310",
                "CDXTexture__WriteJpegHuffmanTable",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave716 static read-back: writes a JPEG DHT segment from the encoder-state descriptor selected by visible table index plus hidden EAX table-class context, sums the 16 Huffman code-count bytes to compute segment length, emits the table class/id byte, writes code counts and symbol bytes, and marks the descriptor as written. Signature intentionally left unchanged because the decompile depends on register-carried EAX context and an unused visible slot; exact Huffman descriptor layout, table-class enum, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("jpeg", "huffman-table", "DHT", "hidden-eax-context")
            ),
            new Spec(
                "0x0059e4a0",
                "CDXTexture__WriteJpegRestartIntervalMarker",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave716 static read-back: emits the JPEG DRI marker 0xffdd, fixed length 4, and the restart interval word from the ESI-held writer/encoder context. Signature intentionally left unchanged because Ghidra records the helper with register-held context and no stable stack parameters; exact restart-interval state layout, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("jpeg", "restart-interval", "DRI", "hidden-esi-context")
            ),
            new Spec(
                "0x0059e580",
                "CDXTexture__WriteJpegFrameHeader",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: writes the frame-header segment selected by hidden EAX marker context, validates image width and height against 0xffff, emits precision, height, width, component count, and component id/sampling/quant-table selectors from the encoder component table, and reports error id 0x29 for oversized dimensions. Static metadata only; hidden EAX marker selection, component descriptor layout, SOF variant semantics, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "frame-header", "SOF", "hidden-eax-marker")
            ),
            new Spec(
                "0x0059e770",
                "CDXTexture__WriteJpegScanHeader",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave716 static read-back: emits the JPEG SOS marker 0xffda, segment length derived from scan component count, component selector and entropy-table ids from the ESI-held scan descriptors, then writes spectral-selection and successive-approximation bytes from the encoder context. Signature intentionally left unchanged because the writer context is register-held in ESI; exact scan descriptor layout, progressive-scan flags, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("jpeg", "scan-header", "SOS", "hidden-esi-context")
            ),
            new Spec(
                "0x0059e970",
                "CDXTexture__WriteJpegApp0JfifSegment",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave716 static read-back: writes the JPEG APP0/JFIF marker 0xffe0, length 0x10, ASCII JFIF identifier bytes, version/density fields, and zero thumbnail dimensions from the ESI-held encoder context. Signature intentionally left unchanged because the helper uses register-held writer state; exact density field provenance, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("jpeg", "APP0", "JFIF", "hidden-esi-context")
            ),
            new Spec(
                "0x0059ebf0",
                "CDXTexture__WriteJpegApp14AdobeMarker",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave716 static read-back: writes the JPEG APP14/Adobe marker 0xffee, length 0x0e, Adobe identifier bytes, version/flag fields, and a transform byte derived from the encoder color-transform state, mapping observed values 3 to 1 and 5 to 2. Signature intentionally left unchanged because the helper uses register-held writer state; exact color-transform enum, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("jpeg", "APP14", "Adobe-marker", "hidden-esi-context")
            ),
            new Spec(
                "0x0059ee20",
                "CDXTexture__WriteJpegSegmentMarkerAndLength",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("marker_byte", intType),
                    param("payload_byte_count", uintType)
                },
                true,
                "Wave716 static read-back: validates payload_byte_count against the maximum segment payload 0xfffd, reports writer callback/error flow when the segment is too large, emits the marker through CDXTexture__WriteJpegMarkerByte, then writes the big-endian segment length as payload_byte_count plus two. Static metadata only; exact writer error callback ABI, segment ownership, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "segment-length", "marker-writer", "big-endian")
            ),
            new Spec(
                "0x0059eed0",
                "CDXTexture__WriteJpegStartOfImageAndMetadata",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: writes the SOI bytes 0xffd8, conditionally emits APP0/JFIF metadata when the encoder flag at +0xd0 is set, and conditionally emits APP14/Adobe metadata when the flag at +0xdc is set. Static metadata only; exact metadata flag layout, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "SOI", "metadata", "APP0", "APP14")
            ),
            new Spec(
                "0x0059ef60",
                "CDXTexture__WriteJpegQuantTablesAndFrame",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: walks component quant-table selectors, calls CDXTexture__WriteJpegQuantTable, preserves its bool-like char precision result in the decompile, reports baseline precision error id 0x4b when 16-bit quantization conflicts with the encoder mode, then writes the frame header. Static metadata only; exact baseline/progressive mode flags, quant precision policy, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "quant-table", "frame-header", "DQT", "SOF")
            ),
            new Spec(
                "0x0059f050",
                "CDXTexture__WriteJpegHuffmanAndScanHeaders",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: walks scan components, emits needed DC/AC Huffman tables through CDXTexture__WriteJpegHuffmanTable, refreshes the restart interval marker when the active interval changes, then writes the scan header. Static metadata only; the decompile still carries hidden EBX table-class context into the Huffman helper, exact scan-script state layout, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "huffman-table", "scan-header", "DHT", "SOS", "hidden-ebx-context")
            ),
            new Spec(
                "0x0059f110",
                "CDXTexture__WriteJpegEndOfImage",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: writes the JPEG EOI bytes 0xffd9 through the encoder output buffer path. Static metadata only; exact writer state layout, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "EOI", "tranche-end-marker")
            ),
            new Spec(
                "0x0059f260",
                "CDXTexture__InitJpegWriterStageCallbacks",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: allocates a 0x20-byte writer-stage callback table, stores it on the encoder state at +0x164, and installs the observed sequence for SOI/metadata, quant tables plus frame, Huffman plus scan headers, EOI, and segment-marker support callbacks. Static metadata only; exact callback table ownership, stage enum, allocator ABI, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "stage-callbacks", "writer-pipeline", "callback-table")
            ),
            new Spec(
                "0x0059f2b0",
                "CDXTexture__InitializeJpegEncoderPipeline",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_encoder_state", voidPtr) },
                true,
                "Wave716 static read-back: initializes the JPEG encoder pipeline, preparing scan controller, color conversion, sample buffers, DCT/quant stages, entropy encoding or scan-script state, working buffers, component buffers, and writer-stage callbacks before invoking pipeline callbacks. Static metadata only; exact stage ordering under every option combination, callback ABI, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg", "encoder-pipeline", "pipeline-init", "tranche-tail")
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
        println("MODE: " + (dryRun ? "dry" : "apply"));

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

        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave716 apply encountered missing/bad rows");
        }
    }
}
