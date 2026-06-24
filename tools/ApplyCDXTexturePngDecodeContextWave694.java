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

public class ApplyCDXTexturePngDecodeContextWave694 extends GhidraScript {
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
            "cdxtexture-png-decode-context-wave694",
            "wave694-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
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
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x00592dc2",
                "CDXTexture__CreatePngDecodeContext",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("png_version_string", voidPtr),
                    param("callback_context", voidPtr),
                    param("error_callback", voidPtr),
                    param("warning_callback", voidPtr)
                },
                true,
                "Wave694 static read-back: allocates and zeroes the PNG decode context, installs the callback_context/error_callback/warning_callback triplet through CTexture__SetDecodeContextTriplet, validates the observed version string first byte, allocates the 0x2000 zlib input buffer at +0x9c, seeds zlib allocator callbacks, calls inflate init with windowbits 15 and version literal 1.1.4, maps zlib setup failures to decode errors, seeds read-buffer fields at +0x70/+0x74, and returns the decode context. Static metadata only; exact PNG decode-state layout, callback prototypes, zlib allocator ABI, and runtime PNG decode behavior remain unproven.",
                signatureTags("png", "decode-context", "zlib", "callback-triplet", "tranche-head")
            ),
            new Spec(
                "0x00592eb6",
                "CDXTexture__ParsePngHeadersUntilIdat",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr)
                },
                true,
                "Wave694 static read-back: reads and validates the PNG signature, distinguishes non-PNG files from ASCII-converted/corrupted signatures, loops through chunk length/type reads with CRC seed setup, dispatches observed IHDR/PLTE/tRNS/gAMA/sRGB handlers before IDAT, verifies IHDR and palette ordering preconditions, records the first IDAT byte count at +0xfc, and marks the header/IDAT state flags. Static metadata only; exact image-context layout, chunk flag enum, CRC contract, and runtime PNG header behavior remain unproven.",
                signatureTags("png", "signature-check", "chunk-dispatch", "idat-boundary", "crc")
            ),
            new Spec(
                "0x00593024",
                "CDXTexture__PreparePngRowOutputLayout",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("png_image_context", voidPtr)
                },
                true,
                "Wave694 static read-back: ensures PNG image buffers/pass geometry are initialized when flag +0x5c bit 0x40 is clear, then applies postprocess/output layout flags to the image context. Static metadata only; exact image-context fields, layout-flag enum, pass-geometry contract, and runtime texture output behavior remain unproven.",
                signatureTags("png", "row-output-layout", "pass-geometry", "postprocess-layout")
            ),
            new Spec(
                "0x00593043",
                "CDXTexture__DecodePngPassRowsAndPostprocess",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("previous_row_workspace", voidPtr),
                    param("current_row_workspace", voidPtr)
                },
                true,
                "Wave694 static read-back: decodes one PNG row/pass by initializing buffers when needed, handling Adam7/packed-pixel pre-expansion masks, reading IDAT chunks and chunk CRCs, feeding the zlib stream, detecting unexpected stream end/decompression errors, applying the PNG scanline filter and row transforms, expanding packed pixels into optional previous/current row workspaces, queueing row postprocess work, and invoking the optional row callback at +0x16c. Static metadata only; exact row-workspace ownership, Adam7 table semantics, zlib stream layout, callback ABI, and runtime PNG output behavior remain unproven.",
                signatureTags("png", "row-decode", "idat", "zlib", "scanline-filter", "adam7")
            ),
            new Spec(
                "0x005933c6",
                "CDXTexture__DecodePngRowsAcrossPasses",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("row_workspace_pointer_table", intPtr)
                },
                true,
                "Wave694 static read-back: queries the pass count from the interlace flag helper, resets the observed row counter from the image height field, then loops over each pass and row, dispatching row_workspace_pointer_table entries to CDXTexture__DecodePngPassRowsAndPostprocess with a null secondary workspace. Static metadata only; exact workspace-table layout, pass-count enum, row-count field identity, and runtime interlace behavior remain unproven.",
                signatureTags("png", "row-loop", "interlace", "adam7", "workspace-table")
            ),
            new Spec(
                "0x00593411",
                "CDXTexture__ResetPngDecodeContext",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("primary_row_workspace", voidPtr),
                    param("secondary_row_workspace", voidPtr)
                },
                true,
                "Wave694 static read-back: clears optional row workspaces, frees the observed owned decode buffers at +0x9c/+0xdc/+0xd8/+0x174/+0x178/+0x138, conditionally releases palette/transform buffers through flag checks, walks and frees the indexed table at +0x144, finishes the async/zlib decode job rooted at +0x64, preserves the initial header/callback triplet, zeroes the larger decode-context body, and restores the preserved fields. Static metadata only; exact ownership bits, table cardinality formula, preserved-header layout, cleanup ABI, and runtime reset behavior remain unproven.",
                signatureTags("png", "decode-context-reset", "owned-buffer-release", "zlib-cleanup", "tranche-tail")
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

        println("ApplyCDXTexturePngDecodeContextWave694 mode=" + (dryRun ? "dry" : "apply"));
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
