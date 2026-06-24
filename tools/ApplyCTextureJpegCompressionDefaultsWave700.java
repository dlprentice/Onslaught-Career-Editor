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

public class ApplyCTextureJpegCompressionDefaultsWave700 extends GhidraScript {
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
            "ctexture-jpeg-compression-defaults-wave700",
            "wave700-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        }, extras);
    }

    private String[] commentOnlyTags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "ctexture-jpeg-compression-defaults-wave700",
            "wave700-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "comment-only"
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
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00595350",
                "CTexture__ProcessDecodeStateMachineStep",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_compress_context", voidPtr) },
                true,
                "Wave700 static read-back: advances the observed IJG-style compression pass controller after input consumption, accepts states 0x65/0x66/0x67, emits diagnostics 0x43/0x14/0x18, loops over the component count at +0xf8, calls the progress callback when present, and finishes through coefficient/master/output controller slots before CDXTexture__PumpDecodeAllocatorAndSetStage. Static metadata only; exact JPEG context layout, controller vtable ABI, pass-state enum, and runtime encoder behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "pass-controller", "component-loop", "tranche-head")
            ),
            new Spec(
                "0x00595430",
                "CTexture__ResetDecodePipelineForNextChunk",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("reset_sent_table_flags", intType)
                },
                true,
                "Wave700 static read-back: requires state 100, optionally clears sent-table flags through CTexture__SetDecodeTableEpoch(..., 0), invokes error/destination/controller setup slots, reinitializes the JPEG encoder pipeline, resets input offset +0xe8, and moves state to 0x65 or 0x66 based on the observed +0xb0 flag. Static metadata only; exact restart policy, callback ABI, state enum, and runtime encoder behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "pipeline-reset", "sent-table-state", "encoder-state")
            ),
            new Spec(
                "0x005954a0",
                "CTexture__ReadDecodeInputBytes",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("destination_buffer", voidPtr),
                    param("requested_byte_count", uintType)
                },
                true,
                "Wave700 static read-back: requires state 0x65, reports diagnostic 0x7b when input is exhausted, updates the observed progress callback slots with +0xe8/+0x20 progress, clamps requested_byte_count to remaining input, dispatches the source-manager callback at +0x158 +4 with destination_buffer, and advances +0xe8 by the returned count. Static metadata only; exact source-manager ABI, destination-buffer ownership, progress callback layout, and runtime input behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "source-manager", "input-read", "progress-callback")
            ),
            new Spec(
                "0x00595550",
                "CTexture__LoadAndScaleQuantizationTable",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("table_index", intType),
                    param("source_quant_table", voidPtr),
                    param("quality_scale_percent", intType),
                    param("force_baseline_range", intType)
                },
                true,
                "Wave700 static read-back: requires state 100, validates table_index 0..3, allocates the quant-table descriptor when absent, scales 64 source_quant_table entries as (value * quality_scale_percent + 50) / 100, clamps to 1..0x7fff and optionally <=0xff for force_baseline_range, then clears the descriptor sent-table flag at +0x80. Static metadata only; exact quant-table descriptor layout, quality policy, baseline policy, and runtime JPEG output behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "quantization-table", "quality-scale", "baseline-clamp")
            ),
            new Spec(
                "0x00595820",
                "CTexture__LoadHuffmanTableDefinition",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("huff_values_table", voidPtr)
                },
                true,
                "Wave700 static read-back: allocates the destination Huffman-table descriptor when the register-held slot is null, copies the register-held bits/count header, sums sixteen code-length counts, errors with diagnostic 0x08 unless the symbol budget is 1..0x100, copies that many huff_values_table bytes, and clears sent_table at descriptor +0x114. Static metadata only; source bits table and destination descriptor slot are register-held in the current decompile, so exact Huffman helper ABI, descriptor layout, and runtime entropy-table behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "huffman-table", "symbol-budget", "register-context")
            ),
            new Spec(
                "0x005958e0",
                "CTexture__LoadDefaultHuffmanTables",
                "",
                voidType,
                new ParameterImpl[] {},
                false,
                "Wave700 static read-back: dispatches four built-in JPEG Huffman table definitions through CTexture__LoadHuffmanTableDefinition using the observed DAT_005eef80, DAT_005eeec8, DAT_005eeea8, and DAT_005eedf0 tables. Signature intentionally left unchanged because Ghidra reports an unknown calling convention with locked storage and exposes the JPEG context through hidden ESI. Static metadata only; exact hidden-register ABI, default table identity, and runtime entropy-table behavior remain unproven.",
                commentOnlyTags("jpeg", "libjpeg", "huffman-table", "default-tables", "locked-storage")
            ),
            new Spec(
                "0x00595930",
                "CTexture__DeflateConfig_SetPreset",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("scan_script_preset", intType)
                },
                true,
                "Wave700 static read-back: despite the existing Deflate name, the decompile writes JPEG scan-script/component selector rows under state 100, resets the observed scan flags at +0xd0/+0xdc/+0xe0/+0xe4, configures preset cases 0..5 including RGB/CMYK/YCCK selector constants, and reports diagnostics 0x14/0x1a/0x0a for invalid state/count/preset values. Static metadata only; exact scan-script row layout, color-space enum, naming provenance, and runtime JPEG output behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "scan-script", "color-space-selectors", "legacy-deflate-name")
            ),
            new Spec(
                "0x00595c10",
                "CTexture__ConfigureDeflatePresetByCompressionMode",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_compress_context", voidPtr) },
                true,
                "Wave700 static read-back: despite the existing Deflate name, maps the observed compression/color-mode field at +0x28 to JPEG scan-script presets 0/3/4 or inline case 1/5 setup, writes the same scan flags and component rows used by CTexture__DeflateConfig_SetPreset, and reports diagnostic 0x09 for unsupported mode values. Static metadata only; exact mode enum, scan-script row layout, naming provenance, and runtime JPEG output behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "scan-script", "compression-mode", "legacy-deflate-name")
            ),
            new Spec(
                "0x00595da0",
                "CTexture__InitializeJpegCompressionDefaults",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("jpeg_compress_context", voidPtr) },
                true,
                "Wave700 static read-back: requires state 100, allocates the 0x348-byte scan/component workspace when absent, sets data precision 8, loads default quant tables from 0x5eecd8/0x5eebd8 at quality scale 0x32 with baseline clamp, installs the default Huffman tables, initializes 16 component default rows and marker flags, then configures the scan-script preset from the observed mode field. Static metadata only; exact workspace layout, default table provenance, component defaults, and runtime JPEG encoder behavior remain unproven.",
                signatureTags("jpeg", "libjpeg", "compression-defaults", "quantization-table", "huffman-table", "scan-script", "tranche-tail")
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

        println("ApplyCTextureJpegCompressionDefaultsWave700 mode=" + (dryRun ? "dry" : "apply"));
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
