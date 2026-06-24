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

public class ApplyJpegEncoderBufferEntropyHeadWave732 extends GhidraScript {
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

    private String[] tags(String... extras) {
        return concat(new String[] {
            "static-reaudit",
            "jpeg-encoder-buffer-entropy-head-wave732",
            "wave732-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "jpeg-encoder-buffer-entropy-head"
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
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true,
                SourceType.USER_DEFINED, spec.parameters);
            if (needsSignature) {
                stats.signatureUpdated++;
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

        return new Spec[] {
            new Spec(
                "0x005b2860",
                "CDXTexture__InitJpegEncoderComponentBuffers",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("component_buffer_mode", intType)
                },
                "Wave732 static read-back: initializes JPEG encoder component-buffer controller at state +0x158. RET 0x8 caller CDXTexture__InitializeJpegEncoderPipeline pushes jpeg_encoder_state and a zero mode flag; the helper allocates a 0x40-byte controller, stores vtable entry 0x005b2810, and when state +0xb0 is zero and the mode flag is zero, allocates per-component buffers through allocator callback +0x8 using component dimensions shifted by 3. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact JPEG encoder-state/component layout, component-buffer mode semantics, allocator contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tranche-head", "jpeg-component-buffers", "encoder-buffer-controller", "ret-0x8")
            ),
            new Spec(
                "0x005b3080",
                "CDXTexture__InitJpegEncoderWorkingBuffers",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("component_work_buffer_mode", intType)
                },
                "Wave732 static read-back: initializes JPEG encoder working-buffer controller at state +0x160. RET 0x8 caller computes a mode flag from state +0xa8 and +0xb8 before pushing jpeg_encoder_state; flag zero allocates one 0x500-byte table slab and installs ten 0x80-byte-spaced table pointers, while nonzero mode loops per component and allocates aligned working buffers through allocator callback +0x14. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact JPEG encoder-state/controller layout, mode flag meaning, allocator contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-working-buffers", "encoder-table-slab", "component-work-buffers", "ret-0x8")
            ),
            new Spec(
                "0x005b3170",
                "CDXTexture__BuildJpegHuffmanEncodeTable",
                "__stdcall",
                VoidDataType.dataType,
                new ParameterImpl[] {
                    param("jpeg_encoder_state", voidPtr),
                    param("table_class", intType),
                    param("table_index", intType),
                    param("out_encode_table", voidPtr)
                },
                "Wave732 static read-back: builds a JPEG Huffman encode lookup table from saved descriptor arrays. RET 0x10 callers pass jpeg_encoder_state, table class selector, table index, and an output table pointer; the helper validates table_index 0..3, selects state +0x68 or +0x58 source tables by class selector, allocates a 0x500-byte encode table when needed, builds canonical code lengths into stack scratch, validates symbol/count bounds, zeroes the 0x100-byte length area at table +0x400, and writes per-symbol code/length entries. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact table class enum, descriptor layout, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-huffman-encode-table", "canonical-huffman-codes", "ret-0x10")
            ),
            new Spec(
                "0x005b3370",
                "CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("bit_value", uintType)
                },
                "Wave732 static read-back: writes pending JPEG entropy bits with byte stuffing through hidden writer state. RET 0x4 callers pass bit_value on the stack while hidden EAX supplies bit_count and hidden ESI supplies the bit-writer state; the helper merges bits into writer +0x8/+0xc, writes bytes to the output cursor, refreshes the output buffer through owner callback +0x18, inserts 0x00 after emitted 0xff bytes, and returns 1/0 for success/failure. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact writer layout, hidden-register ABI, callback contract, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-entropy-bit-writer", "byte-stuffing", "hidden-eax-esi", "ret-0x4")
            ),
            new Spec(
                "0x005b3440",
                "CFastVB__JpegEntropy_EncodeBlockZigZagHuffman",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("coeff_block", voidPtr),
                    param("previous_dc_value", intType),
                    param("dc_huffman_table", voidPtr),
                    param("ac_huffman_table", voidPtr)
                },
                "Wave732 static read-back: encodes one 8x8 block with JPEG zig-zag/Huffman entropy output. RET 0x10 callers pass coefficient block, previous DC value, DC Huffman table, and AC Huffman table while hidden EAX supplies the bit-writer state; the helper encodes the DC difference category and magnitude bits, walks AC coefficients through zig-zag table DAT_005f37fc, emits ZRL from AC table +0x3c0 and EOB from the AC table head, validates DC/AC category bounds through the encoder error callback, and returns 1/0. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact coefficient block layout, zig-zag table identity, hidden writer ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-block-zigzag-huffman", "zigzag-table-005f37fc", "hidden-eax-writer", "ret-0x10")
            ),
            new Spec(
                "0x005b35b0",
                "CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("restart_marker_code", intType)
                },
                "Wave732 static read-back: writes an entropy restart/marker byte path and resets DC predictors through hidden writer state. RET 0x4 callers pass a marker code on the stack while hidden EAX supplies the bit-writer state; the helper flushes pending bits with value 0x7f, writes marker prefix 0xff, clears bit-buffer fields, emits a marker byte derived from the stack code, refreshes output as needed, and zeroes per-component DC predictors based on owner state +0xfc. Static retail Ghidra metadata/decompile/instruction/xref evidence only; exact marker-code enum, writer/owner layout, restart interval policy, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.",
                tags("jpeg-restart-marker", "dc-predictor-reset", "hidden-eax-writer", "ret-0x4", "tranche-tail")
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

        println("ApplyJpegEncoderBufferEntropyHeadWave732 mode=" + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave732 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
