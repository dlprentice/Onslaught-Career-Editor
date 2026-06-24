//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyPngChunkParserHeadWave715 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String[] acceptedOldNames;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String[] acceptedOldNames, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.acceptedOldNames = acceptedOldNames;
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
            "png-chunk-parser-head-wave715",
            "wave715-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "png-chunk-parser-head"
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

    private boolean acceptedName(Function fn, Spec spec) {
        if (fn.getName().equals(spec.name)) {
            return true;
        }
        for (String oldName : spec.acceptedOldNames) {
            if (fn.getName().equals(oldName)) {
                return true;
            }
        }
        return false;
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
            if (!acceptedName(fn, spec)) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            boolean needsSignature = !signatureMatches(fn, spec);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                else {
                    stats.commentOnlyUpdated++;
                }
                println("DRY: " + spec.address + " actualName=" + fn.getName()
                    + " expected=" + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0059d699",
                "CDXTexture__ParsePngChunk_IHDR",
                new String[] {},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc and ParsePngHeadersUntilIdat xref show decode-state, image-context, and chunk-data-length inputs for the IHDR handler. It rejects duplicate or mis-sized IHDR chunks, reads the 13-byte payload, finalizes CRC, validates width/height, bit depth, color type, compression, filter, and interlace values, records IHDR fields in the decode state, derives channel count, bits-per-pixel, and row byte count, then finalizes the decode format descriptor. Static metadata only; exact decode-state/image-context layouts, chunk flag enum, PNG policy provenance, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "IHDR", "format-descriptor", "ret-0xc", "tranche-head")
            ),
            new Spec(
                "0x0059d879",
                "CDXTexture__ParsePngChunk_PLTE",
                new String[] {},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc and ParsePngHeadersUntilIdat xref show decode-state, image-context, and chunk-data-length inputs for the PLTE handler. It enforces IHDR-before-PLTE, duplicate/after-IDAT policy, reads 3-byte palette entries into a zeroed decode buffer, stores the palette pointer/count on the decode state, forwards scan parameters to the image context, and clamps indexed transparency metadata when palette and tRNS counts disagree. Static metadata only; exact decode-state/image-context layouts, palette ownership, chunk flag enum, warning policy, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "PLTE", "palette", "scan-parameters", "ret-0xc")
            ),
            new Spec(
                "0x0059d992",
                "CDXTexture__ParsePngChunk_IEND",
                new String[] {"CDXTexture__ParsePngChunk_tRNS"},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc, ParsePngHeadersUntilIdat xref, and raw dispatch constant 0x005ee8e4 bytes 49 45 4e 44 identify this row as the IEND handler, replacing the older tRNS symbol. It requires prior IHDR/IDAT state, marks terminal chunk flags, warns on nonzero IEND length, and finalizes the chunk CRC. Static metadata only; exact chunk flag enum, terminal-state policy, source-read bounds, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "IEND", "terminal-chunk", "chunk-tag-constant", "rename-hardened", "ret-0xc")
            ),
            new Spec(
                "0x0059d9d8",
                "CDXTexture__ParsePngChunk_gAMA",
                new String[] {},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc and ParsePngHeadersUntilIdat xref show decode-state, image-context, and chunk-data-length inputs for the gAMA handler. It enforces IHDR/after-IDAT/duplicate policy, reads a 4-byte big-endian gamma integer, finalizes CRC before applying it, checks sRGB/gAMA consistency, stores the normalized gamma float at decode_state +0x130, and forwards the option float to the image context. Static metadata only; exact option-bit layout, gamma policy provenance, floating constants, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "gAMA", "gamma", "decode-option", "ret-0xc")
            ),
            new Spec(
                "0x0059dad9",
                "CDXTexture__ParsePngChunk_sRGB",
                new String[] {},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc and ParsePngHeadersUntilIdat xref show decode-state, image-context, and chunk-data-length inputs for the sRGB handler. It enforces IHDR/after-IDAT/duplicate policy, reads the one-byte rendering intent, finalizes CRC before applying it, rejects intents above 3, checks gAMA/sRGB consistency when a gamma option is already present, and forwards the sRGB option to the image context with the observed default-gamma helper. Static metadata only; exact option-bit layout, rendering-intent policy, gamma constants, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "sRGB", "rendering-intent", "decode-option", "ret-0xc")
            ),
            new Spec(
                "0x0059dbbb",
                "CDXTexture__ParsePngChunk_tRNS",
                new String[] {"CDXTexture__ParsePngChunk_tRNS_Data"},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc, ParsePngHeadersUntilIdat xref, and raw dispatch constant 0x005ee904 bytes 74 52 4e 53 identify this row as the tRNS handler, replacing the older tRNS_Data symbol. It enforces IHDR/after-IDAT/duplicate policy, handles indexed-color transparency by allocating and reading palette alpha bytes, handles truecolor and grayscale transparent samples through big-endian 16-bit fields, stores transparency counts/parameters on the decode state, then forwards the option parameters after CRC validation. Static metadata only; exact transparency field layout, allocation ownership, option-bit layout, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "tRNS", "transparency", "chunk-tag-constant", "rename-hardened", "ret-0xc")
            ),
            new Spec(
                "0x0059dd5c",
                "CDXTexture__HandlePngChunkAfterIdat",
                new String[] {},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr),
                    param("chunk_data_length", uintType)
                },
                "Wave715 static read-back: RET 0xc and ParsePngHeadersUntilIdat fallback xref show a generic PNG chunk handler for chunks not matched by the explicit IHDR/PLTE/IEND/gAMA/sRGB/tRNS dispatch constants. It validates/logs the chunk tag, reports unknown critical chunks, records a post-IDAT unknown-chunk flag when IDAT has started, and drains/finalizes the chunk payload through the CRC finalizer. Static metadata only; exact chunk flag enum, critical/ancillary policy, source-read bounds, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "fallback", "unknown-chunk", "ret-0xc")
            ),
            new Spec(
                "0x0059dda2",
                "CDXTexture__ProcessIdatChunkDataAndQueueDecode",
                new String[] {},
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave715 static read-back: RET 0x4 and both DecodePngPassRowsAndPostprocess call sites show one stack argument, the decode state; the prologue pushes ECX and later pops it as scratch/local storage, not as a stable this pointer. The helper advances row/pass state, clears previous-row storage for interlaced pass changes, reads additional IDAT chunks when needed, feeds the zlib stream, marks decode completion flags, checks for trailing compressed bytes, begins the async decode job, and records IDAT completion state. Static metadata only; exact zlib stream layout, async job contract, Adam7 table semantics, source-read bounds, runtime PNG behavior, image fidelity, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-parser", "IDAT", "zlib", "async-decode-job", "ret-0x4", "tranche-tail")
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
            throw new RuntimeException("Wave715 apply encountered missing/bad rows");
        }
    }
}
