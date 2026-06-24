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

public class ApplyCDXTexturePngDecodeWorkspaceTailWave699 extends GhidraScript {
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
            "cdxtexture-png-decode-workspace-tail-wave699",
            "wave699-readback-verified",
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
                "0x0059512b",
                "CDXTexture__AllocZeroedDecodeBuffer",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("allocator_context", voidPtr),
                    param("element_count", uintType),
                    param("element_size", uintType)
                },
                "Wave699 static read-back: multiplies element_count by element_size, allocates through CDXTexture__AllocOrThrow, zeroes the allocated span with dword and byte loops, and returns the allocated buffer pointer. Current xrefs include PNG PLTE parsing and a CreatePngDecodeContext callback slot. Static metadata only; exact allocator ABI, overflow policy, buffer ownership, and runtime PNG behavior remain unproven.",
                signatureTags("png", "allocation", "decode-workspace", "allocator", "tranche-head")
            ),
            new Spec(
                "0x0059517e",
                "CDXTexture__FreeDecodeBufferIfPresent",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr),
                    param("decode_buffer", voidPtr)
                },
                "Wave699 static read-back: frees decode_buffer through CRT__FreeBase only when both decode_state and decode_buffer are non-null; current xrefs include ResetPngDecodeContext and a CreatePngDecodeContext callback slot. Static metadata only; exact owner object, nullability contract, allocation pair, and runtime cleanup behavior remain unproven.",
                signatureTags("png", "allocation", "decode-workspace", "cleanup")
            ),
            new Spec(
                "0x00595183",
                "CDXTexture__InitDecodeSeedDefault",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave699 static read-back: initializes png_decode_state +0x100 with CDXTexture__Crc32_Update(0, null, 0), matching the observed CRC seed reset used before header/pass/IDAT processing. Static metadata only; exact decode-state layout, CRC policy, and runtime chunk-validation behavior remain unproven.",
                signatureTags("png", "crc", "decode-state", "seed")
            ),
            new Spec(
                "0x0059519a",
                "CDXTexture__UpdateChunkCrc",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("source_buffer", voidPtr),
                    param("byte_count", uintType)
                },
                "Wave699 static read-back: checks observed decode-state flags at +0x10c and +0x5c, then updates png_decode_state +0x100 with CDXTexture__Crc32_Update over source_buffer and byte_count unless the flag state suppresses CRC accumulation. Static metadata only; exact flag enum, chunk-read contract, CRC acceptance policy, and runtime PNG behavior remain unproven.",
                signatureTags("png", "crc", "chunk-read", "decode-state")
            ),
            new Spec(
                "0x005951d9",
                "CDXTexture__ZeroDecodeWorkspace16Dwords",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("workspace", voidPtr)
                },
                "Wave699 static read-back: preserves the two-argument ABI while zeroing 16 dwords at workspace; current xrefs show two ResetPngDecodeContext workspace clears. Static metadata only; exact workspace owner, field layout, and runtime reset behavior remain unproven.",
                signatureTags("png", "decode-workspace", "zero-init")
            ),
            new Spec(
                "0x005951e9",
                "CDXTexture__AllocZeroedInflateState",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("state_required_flag", intType)
                },
                "Wave699 static read-back: returns null when state_required_flag is zero; otherwise allocates decode-state class 2 through CDXTexture__AllocZeroedDecodeState and zeroes the first 16 dwords. Current xref is DecodePngFromMemory. Static metadata only; exact zlib/inflate-state layout, allocation class identity, and runtime PNG behavior remain unproven.",
                signatureTags("png", "zlib", "inflate-state", "allocation")
            ),
            new Spec(
                "0x00595220",
                "CTexture__ResetDecodeContextWithDefaults",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("expected_libjpeg_version", intType),
                    param("expected_struct_size", intType)
                },
                "Wave699 static read-back: checks observed IJG-style constants 0x3e and 0x180 through the context error callback, zeroes 0x60 dwords while preserving slots +0x0 and +0xc, initializes the allocator/vtable helper, and sets default state fields including +0x14 = 100. Static metadata only; exact JPEG context layout, error-manager ABI, libjpeg source identity, and rebuild parity remain unproven.",
                signatureTags("jpeg", "libjpeg", "compress-context", "context-reset")
            ),
            new Spec(
                "0x005952e0",
                "CTexture__SetDecodeTableEpoch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("jpeg_compress_context", voidPtr),
                    param("sent_table_flag", intType)
                },
                "Wave699 static read-back: writes sent_table_flag into four quant-table slots at +0x80 and paired DC/AC Huffman table slots at +0x114, matching an IJG jpeg_suppress_tables-style table-state sweep. Current xref is ResetDecodePipelineForNextChunk. Static metadata only; exact table ownership, field layout, flag semantics, and rebuild parity remain unproven.",
                signatureTags("jpeg", "libjpeg", "table-state", "suppress-tables", "tranche-tail")
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

        println("ApplyCDXTexturePngDecodeWorkspaceTailWave699 mode=" + (dryRun ? "dry" : "apply"));
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
