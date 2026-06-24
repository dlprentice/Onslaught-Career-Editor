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

public class ApplyJpegEntropyFrequencyHeadWave733 extends GhidraScript {
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
            "jpeg-entropy-frequency-head-wave733",
            "wave733-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "jpeg-entropy-frequency-head"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "jpeg-entropy-frequency-head-wave733",
            "wave733-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only",
            "jpeg-entropy-frequency-head"
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
            Thread.sleep(75);
        } catch (Exception ex) {
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
                "0x005b3840",
                "CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("coeff_block", voidPtr),
                    param("ac_frequency_counts", voidPtr)
                },
                true,
                "Wave733 static read-back: accumulates DC/AC JPEG Huffman frequency counts for one coefficient block. RET 0xc caller CDXTexture__EncodeMcuBlocksForScan supplies hidden ECX as previous_dc_value, hidden EAX as the DC frequency table, and stack arguments jpeg_encoder_state, coeff_block, and ac_frequency_counts; the helper computes the DC difference category, validates category bounds through the encoder error callback, walks AC coefficients through zig-zag table DAT_005f37fc, increments ZRL bucket +0x3c0 and EOB bucket 0 when needed, and updates AC run/size buckets. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact coefficient layout, hidden ECX/EAX ABI, Huffman table schema, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-head", "jpeg-huffman-frequency", "hidden-ecx-previous-dc", "hidden-eax-dc-table", "zigzag-table-005f37fc", "ret-0xc")
            ),
            new Spec(
                "0x005b3920",
                "CDXTexture__EncodeMcuBlocksForScan",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("coeff_block_table", voidPtr)
                },
                true,
                "Wave733 static read-back: frequency-count pass over MCU coefficient blocks for the active JPEG scan. RET 0x8 helper refreshes restart-interval counters at entropy state +0x24, zeroes per-component DC predictors at entropy state +0x14 when a restart interval begins, loops scan component order from encoder state +0x11c, calls CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock with component DC/AC frequency tables, and stores each block's first coefficient as the next DC predictor. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact scan layout, coefficient-block table layout, restart policy, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-mcu-frequency-pass", "jpeg-scan-components", "dc-predictor-update", "ret-0x8")
            ),
            new Spec(
                "0x005b39d0",
                "CDXTexture__BuildCanonicalHuffmanCodes",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("out_huffman_descriptor", voidPtr),
                    param("frequency_counts", voidPtr)
                },
                true,
                "Wave733 static read-back: builds a canonical JPEG Huffman descriptor from frequency counts. RET 0xc callers pass jpeg_encoder_state, an output Huffman descriptor, and a frequency-count table; the helper creates code lengths for 0x101 symbols, validates maximum depth through error id 0x27, applies the JPEG 16-bit length limiting adjustment, writes sixteen count bytes plus ordered symbol bytes into out_huffman_descriptor, and clears descriptor +0x114. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact descriptor schema, source algorithm identity, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-canonical-huffman", "huffman-frequency-counts", "jpeg-length-limit", "ret-0xc")
            ),
            new Spec(
                "0x005b3e80",
                "CDXTexture__InitJpegEntropyEncoderState",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr)
                },
                true,
                "Wave733 static read-back: allocates and initializes the JPEG entropy encoder state. RET 0x4 caller CDXTexture__InitializeJpegEncoderPipeline selects this path when scan-script state is not used; the helper allocates a 0x6c-byte controller through encoder allocator callback +4, stores it at encoder state +0x174, installs vtable/table entry 0x005b3d20, and clears four per-component DC/restart/frequency slots. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact entropy-state layout, callback table contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-entropy-state", "encoder-controller", "ret-0x4")
            ),
            new Spec(
                "0x005b3ec0",
                "CDXTexture__WriteEntropyBitsWithByteStuffing",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("bit_value", uintType)
                },
                true,
                "Wave733 static read-back: writes JPEG entropy bits and performs byte stuffing through hidden state. RET 0x4 callers pass bit_value on the stack while hidden EAX supplies bit_count and hidden ESI supplies the entropy writer/controller; the helper validates nonzero bit_count, merges bits into writer +0x18/+0x1c, emits full bytes through the output cursor, refreshes the host output buffer through owner callback +0x18 when full, and inserts a stuffed zero byte after emitted 0xff. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact hidden-register ABI, writer layout, callback contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-entropy-bit-writer", "byte-stuffing", "hidden-eax-esi", "ret-0x4")
            ),
            new Spec(
                "0x005b3fd0",
                "CDXTexture__FlushEntropyBitWriter",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave733 static read-back: flushes pending entropy bits using hidden EAX as the entropy writer/controller. The helper emits the pending zero-run/extra-bit state through CDXTexture__WriteEntropyBitsWithByteStuffing when output mode is active, increments frequency buckets when in frequency-collection mode, drains queued literal bytes from state +0x40, and clears pending counters at +0x38/+0x3c. Comment/tag-only because Ghidra keeps an unknown locked calling convention and hidden EAX ABI here; static retail Ghidra metadata/decompile/instruction/xref evidence only; exact hidden-register ABI, pending-state semantics, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                commentOnlyTags("jpeg-entropy-flush", "hidden-eax-writer", "comment-only", "unknown-locked-calling-convention")
            ),
            new Spec(
                "0x005b4080",
                "CDXTexture__EmitRestartMarkerAndReset",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("restart_marker_code", intType)
                },
                true,
                "Wave733 static read-back: emits a JPEG restart marker and resets entropy/DC predictor state through hidden EAX writer state. RET 0x4 callers pass restart_marker_code while hidden EAX supplies the entropy writer/controller; the helper flushes pending bits, writes a 0xff marker prefix and a marker byte derived from restart_marker_code, refreshes output as needed, clears bit-buffer fields, zeroes per-component DC predictors when scan-script mode is off, or clears pending counters when scan-script mode is active. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact marker-code enum, hidden EAX ABI, restart-interval policy, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-restart-marker", "dc-predictor-reset", "hidden-eax-writer", "ret-0x4")
            ),
            new Spec(
                "0x005b44c0",
                "CDXTexture__WriteEncodedBlockWithRestartControl",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("coeff_block_table", voidPtr)
                },
                true,
                "Wave733 static read-back: writes encoded block DC seed values with restart-interval control for the active JPEG scan. RET 0x8 helper snapshots output cursor fields from encoder state +0x18 into entropy state +0x10/+0x14, emits a restart marker when interval countdown +0x44 reaches zero, loops over scan components from encoder state +0x118 and writes shifted first coefficients through CDXTexture__WriteEntropyBitsWithByteStuffing, restores output cursor fields, advances restart marker index modulo 8, and decrements the interval countdown. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact coefficient-block table layout, shift semantics, restart policy, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("jpeg-encoded-block-restart", "restart-control", "output-cursor-snapshot", "ret-0x8")
            ),
            new Spec(
                "0x005b4ae0",
                "CDXTexture__InitJpegEncoderScanScriptState",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr)
                },
                true,
                "Wave733 static read-back: allocates and initializes the alternate JPEG scan-script encoder state. RET 0x4 caller CDXTexture__InitializeJpegEncoderPipeline selects this path when the scan-script mode flag is set; the helper allocates a 0x6c-byte controller through encoder allocator callback +4, stores it at encoder state +0x174, installs vtable/table entry 0x005b4950, clears four component table slots at +0x34/+0x44, and clears state +0x40. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact scan-script-state layout, callback table contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("tranche-tail", "jpeg-scan-script-state", "encoder-controller", "ret-0x4")
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

        println("ApplyJpegEntropyFrequencyHeadWave733 mode=" + (dryRun ? "dry" : "apply"));
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
            throw new IllegalStateException("Wave733 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
