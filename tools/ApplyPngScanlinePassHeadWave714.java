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

public class ApplyPngScanlinePassHeadWave714 extends GhidraScript {
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
            "png-scanline-pass-head-wave714",
            "wave714-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "png-scanline-pass-head"
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
                else {
                    stats.commentOnlyUpdated++;
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
            else {
                stats.commentOnlyUpdated++;
            }
            println("UPDATED: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    private Spec[] specs() throws Exception {
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0059ce20",
                "CDXTexture__ExpandPackedPixelsToScanline",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("output_scanline", voidPtr),
                    param("pass_pixel_mask", uintType)
                },
                "Wave714 static read-back: RET 0xc and DecodePngPassRowsAndPostprocess xrefs show decode-state, output-scanline, and pass-pixel-mask inputs. The helper copies a full packed row when the mask is 0xff, otherwise expands 1/2/4-bit and byte-aligned packed pixels from the current row buffer at decode_state +0xdc into the provided workspace according to the pass mask. Static metadata only; exact PNG decode-state layout, row-workspace ownership, Adam7 mask semantics, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "scanline", "packed-pixels", "pass-mask", "ret-0xc", "tranche-head")
            ),
            new Spec(
                "0x0059d036",
                "CDXTexture__ExpandAdam7PassRowInPlace",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("row_layout_descriptor", voidPtr),
                    param("row_buffer", voidPtr),
                    param("adam7_pass_index", intType)
                },
                "Wave714 static read-back: RET 0xc, null guards, and the DecodePngPassRowsAndPostprocess call site show an in-place Adam7 pass-row expander over a row-layout descriptor and row buffer. It uses the observed pass-width table at DAT_005f39d8, expands 1/2/4-bit and byte-aligned row data backward in the buffer, then updates descriptor width and byte-count fields. Static metadata only; exact row-layout descriptor schema, Adam7 table semantics, row-buffer capacity/ownership, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "adam7", "row-expansion", "packed-pixels", "ret-0xc")
            ),
            new Spec(
                "0x0059d301",
                "CDXTexture__ApplyPngScanlineFilter",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("row_layout_descriptor", voidPtr),
                    param("current_scanline", voidPtr),
                    param("previous_scanline", voidPtr),
                    param("filter_type", intType)
                },
                "Wave714 static read-back: RET 0x14 and the row decoder call site show PNG scanline filter application over current and previous row spans, using row-layout byte count and pixel-byte stride. Observed filter types 1..4 match Sub, Up, Average, and Paeth-style byte predictors; an unknown filter emits a decode warning and clears the first current byte. Static metadata only; exact row-layout descriptor schema, warning policy, predictor provenance, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "scanline-filter", "paeth", "filter-type", "ret-0x14")
            ),
            new Spec(
                "0x0059d47a",
                "CDXTexture__InitPngImageBuffersAndPassGeometry",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave714 static read-back: RET 0x4 and row-preparation xrefs show PNG row-buffer/pass-geometry initialization on the decode state. The helper resets the pending decode byte count, applies post-decode transforms, computes normal or Adam7 pass dimensions and output bit widths, allocates current and previous row buffers through CDXTexture__AllocOrThrow, clears the previous-row buffer, and marks decode buffers initialized. Static metadata only; exact decode-state layout, transform flags, allocation ownership, Adam7 geometry semantics, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "decode-buffer", "pass-geometry", "allocation", "ret-0x4")
            ),
            new Spec(
                "0x0059d614",
                "CDXTexture__FinalizePngChunkAndVerifyCrc",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("remaining_chunk_bytes", uintType)
                },
                "Wave714 static read-back: RET 0x8 and chunk parser/row decoder xrefs show a chunk finalizer that drains any remaining chunk payload through CDXTexture__ReadChunkBytesAndUpdateCrc, checks the stored CRC through CDXTexture__IsPngChunkCrcInvalid, and logs or warns with \"CRC error\" based on observed chunk/flag policy before returning a nonzero status for invalid CRC. Static metadata only; exact chunk/flag enum, source-read bounds, warning/error policy, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "crc", "chunk-finalize", "chunk-read", "ret-0x8", "tranche-tail")
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
            throw new RuntimeException("Wave714 apply encountered missing/bad rows");
        }
    }
}
