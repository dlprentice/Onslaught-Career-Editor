//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyInflatePngHelperHeadWave713 extends GhidraScript {
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
            "inflate-png-helper-head-wave713",
            "wave713-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "inflate-png-helper-head"
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
        DataType boolType = BooleanDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidType = VoidDataType.dataType;

        return new Spec[] {
            new Spec(
                "0x0059c7cc",
                "CDXTexture__InflateInitStateFromHeader",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_stream", voidPtr),
                    param("window_bits", intType),
                    param("version_text", voidPtr),
                    param("stream_struct_size", intType)
                },
                "Wave713 static read-back: RET 0x10 and wrapper/xrefs show zlib-style inflate stream, window-bits, version text, and 0x38 stream struct-size inputs. It rejects non-'1' version/size, installs default alloc/free callbacks, allocates a 0x18 internal state, accepts absolute window bits 8..15, builds fixed Huffman tables, and begins/cleans the decode job. Static metadata only; exact z_stream/state layout, callback ABI, zlib source identity, runtime inflate behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate", "zlib", "state-init", "window-bits", "ret-0x10", "tranche-head")
            ),
            new Spec(
                "0x0059c8ab",
                "CDXTexture__InflateInit_WindowBits15",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_stream", voidPtr),
                    param("version_text", voidPtr),
                    param("stream_struct_size", intType)
                },
                "Wave713 static read-back: RET 0xc wrapper pushes the stream, version text, 0x38-sized caller struct argument, and fixed window bits 15 into CDXTexture__InflateInitStateFromHeader, preserving the callee status return in EAX. Static metadata only; wrapper source identity, caller error handling, runtime inflate behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate", "zlib", "window-bits-15", "wrapper", "ret-0xc")
            ),
            new Spec(
                "0x0059c8c1",
                "CDXTexture__InflateStream_ProcessZlibState",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("inflate_stream", voidPtr),
                    param("flush_mode", intType)
                },
                "Wave713 static read-back: RET 0x8 and PNG IDAT/pass-row xrefs show a two-argument inflate stream/flush-mode state machine. It validates stream/state/input pointers, handles zlib CMF/FLG, dictionary/data-check states, block processing, ResetDecodeWindowState on stream-end, and returns zlib-style status values. Static metadata only; downstream block-header helper return ABI still leaves extraout_EAX in decompile; exact state enum/layout, runtime inflate behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("inflate", "zlib", "state-machine", "png-idat", "extraout-eax-gap", "ret-0x8")
            ),
            new Spec(
                "0x0059cc24",
                "CDXTexture__AllocZeroedDecodeState",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("state_class", intType)
                },
                "Wave713 static read-back: RET 0x4 selects decode-state class 1 as 0x19c bytes and class 2 as 0x40 bytes, mallocs that span, zeroes it dword-wise, and returns the allocated state pointer or null. Static metadata only; state-class enum/layout, allocator failure policy, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("decode-state", "allocation", "zero-init", "state-class", "ret-0x4")
            ),
            new Spec(
                "0x0059cc68",
                "CDXTexture__FreeDecodeState",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("decode_state", voidPtr)
                },
                "Wave713 static read-back: RET 0x4 frees a non-null decode-state pointer through CRT__FreeBase; xrefs include CreatePngDecodeContext and ReleasePngDecodeContextHandles cleanup paths. Static metadata only; ownership contract, state layout, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("decode-state", "allocation", "cleanup", "free", "ret-0x4")
            ),
            new Spec(
                "0x0059cc7c",
                "CDXTexture__AllocOrThrow",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("byte_count", uintType)
                },
                "Wave713 static read-back: RET 0x8 returns null for a null decode state or zero byte_count, otherwise mallocs byte_count bytes and throws a decode error through CDXTexture__ThrowDecodeError on allocation failure. Static metadata only; allocator context layout, exception policy, runtime allocation behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "allocation", "decode-error", "malloc", "ret-0x8")
            ),
            new Spec(
                "0x0059ccf3",
                "CDXTexture__MemsetByte",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("unused_context", voidPtr),
                    param("destination_buffer", voidPtr),
                    param("fill_byte", intType),
                    param("byte_count", uintType)
                },
                "Wave713 static read-back: RET 0x10 fills destination_buffer with fill_byte for byte_count bytes using dword and tail-byte loops, returns destination_buffer, and leaves the first context argument unused in this implementation. Static metadata only; adapter/callback contract, runtime buffer bounds, BEA patching, and rebuild parity remain unproven.",
                signatureTags("memset", "png", "buffer-fill", "unused-context", "ret-0x10")
            ),
            new Spec(
                "0x0059cd26",
                "CDXTexture__ReadU32BigEndian",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("source_buffer", voidPtr)
                },
                "Wave713 static read-back: RET 0x4 reads four bytes from source_buffer as a big-endian uint32; xrefs cover PNG headers, CRC, IHDR, gAMA, IDAT, and pass-row processing. Static metadata only; caller bounds, source lifetime, runtime PNG behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "big-endian", "chunk-read", "u32-read", "ret-0x4")
            ),
            new Spec(
                "0x0059cd4b",
                "CDXTexture__ReadChunkBytesAndUpdateCrc",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("destination_buffer", voidPtr),
                    param("byte_count", uintType)
                },
                "Wave713 static read-back: RET 0xc reads byte_count bytes from the PNG source into destination_buffer, then updates the running chunk CRC with the same span. Static metadata only; source-read callback ABI, CRC flag policy, chunk bounds, runtime PNG behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-read", "crc", "source-read", "ret-0xc")
            ),
            new Spec(
                "0x0059cd62",
                "CDXTexture__IsPngChunkCrcInvalid",
                "__stdcall",
                boolType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr)
                },
                "Wave713 static read-back: RET 0x4 reads the stored CRC dword from the source, conditionally compares it against the running CRC at decode_state +0x100 based on flags at +0x10c/+0x5c/+0x5d, and returns true when the chunk CRC is invalid. Static metadata only; CRC flag enum/layout, warning/error policy, runtime PNG behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "crc", "chunk-validation", "bool-return", "ret-0x4")
            ),
            new Spec(
                "0x0059cdbe",
                "CDXTexture__ValidateChunkTagAsciiOrLog",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("png_decode_state", voidPtr),
                    param("chunk_type_bytes", voidPtr)
                },
                "Wave713 static read-back: RET 0x8 validates four chunk-tag bytes against the observed ASCII ranges and logs \"invalid chunk type\" through CDXTexture__LogChunkTagDiagnostic on failure. Static metadata only; exact PNG chunk policy, warning severity, runtime PNG behavior, BEA patching, and rebuild parity remain unproven.",
                signatureTags("png", "chunk-tag", "diagnostic", "ascii-validation", "ret-0x8", "tranche-tail")
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
            throw new RuntimeException("Wave713 apply encountered missing/bad rows");
        }
    }
}
