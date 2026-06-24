//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyOggVorbisWave568 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getOrCreateFunction(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
            return null;
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
            return null;
        }
        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        stats.created++;
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "ogg-vorbis-wave568",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getOrCreateFunction(spec, dryRun, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                stats.skipped++;
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00523df0",
                "OggVorbisStream__InitDecoder",
                "__thiscall",
                intType,
                "Wave568 signature/comment hardening: initializes one Ogg/Vorbis decode stream on this object. It fills the ogg sync buffer from either the file handle at +0x2008 or the memory cursor at +0x200c/+0x2010, validates the first Ogg page and Vorbis headers, initializes stream/comment/info/dsp/block state, and derives the sample byte quantum from channel count. Static retail evidence only; exact layout names, source identity, runtime streaming behavior, and rebuild parity remain unproven.",
                new String[] {"OggVorbisStream__InitDecoder"},
                tags("ogg-vorbis", "decoder-init", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00524180",
                "OggVorbisStream__ReadPcmSamples",
                "__thiscall",
                intType,
                "Wave568 signature/comment hardening: decodes Ogg/Vorbis packets into signed 16-bit PCM bytes. The body initializes/clears libogg state, calls OggVorbisStream__InitDecoder, converts float PCM through a clamp scale, buffers leftover bytes at this+4/+0x22d8, and returns bytes copied or -1 on decode failure. RET 0x8 confirms only output pointer and requested byte count are stack arguments after this; the older third param_N was a decompiler artifact. Static retail evidence only; exact buffer layout, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"OggVorbisStream__ReadPcmSamples"},
                tags("ogg-vorbis", "pcm-decode", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_pcm_bytes", voidPtr),
                    param("requested_byte_count", uintType)
                }
            ),
            new Spec(
                "0x005245a0",
                "COggFileRead__ctor_base",
                "__thiscall",
                voidPtr,
                "Wave568 name/signature/comment correction: base constructor for the Ogg file/memory reader object. It returns this in EAX, installs the COggFileRead vtable at 0x005e4a44, clears decode/open state fields, sets the initial 0x1000 sample/read quantum, and is called by COggLoader construction and PCPlatform async music stream initialization. Static retail evidence only; exact class layout, ownership, runtime streaming behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__ctor_like_005245a0", "COggFileRead__ctor_base"},
                tags("ogg-file-read", "constructor", "name-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x005245e0",
                "COggFileRead__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave568 name/signature/comment correction: scalar-deleting destructor wrapper for the COggFileRead vtable slot 0. It calls COggFileRead__dtor_body, conditionally frees this when flags bit 0 is set, returns this, and RET 0x4 confirms a single stack flags argument. Static retail evidence only; allocator ownership, source identity, runtime streaming behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__VFunc_00_005245e0", "COggFileRead__scalar_deleting_dtor"},
                tags("ogg-file-read", "destructor", "scalar-deleting-dtor", "name-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x00524600",
                "COggFileRead__dtor_body",
                "__thiscall",
                voidType,
                "Wave568 name/signature/comment correction: destructor/close body for the Ogg file reader. If a file handle is open at +0x2008, it clears ogg_stream, vorbis block/dsp/comment/info, ogg_sync, closes the FILE pointer, clears the handle, clears memory-buffer cursor fields when present, and restores the base CWaveSoundRead vtable. Static retail evidence only; exact member names, runtime streaming behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__ctor_like_00524600", "COggFileRead__dtor_body"},
                tags("ogg-file-read", "destructor", "close-reset", "name-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x005246a0",
                "COggFileRead__OpenFileAndPrimeDecoder",
                "__thiscall",
                intType,
                "Wave568 vtable slot correction: COggFileRead slot 1 closes any prior stream through vtable slot 3, opens the supplied path with the observed read-mode string, stores the FILE pointer at +0x2008, and primes the decoder by calling OggVorbisStream__ReadPcmSamples with null output and zero requested bytes. Returns 0 on success or 0x80004005-style failure. Static retail evidence only; exact HRESULT contract, path lifetime, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_01_005246a0", "COggFileRead__OpenFileAndPrimeDecoder"},
                tags("ogg-file-read", "vtable-slot", "open", "decoder-prime", "name-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("file_path", charPtr)
                }
            ),
            new Spec(
                "0x00524710",
                "COggFileRead__ReadDecodedPcm",
                "__thiscall",
                intType,
                "Wave568 recovered vtable slot 2 boundary: reads decoded PCM bytes from either an open file stream or an in-memory Ogg buffer. It validates input availability, then pushes the first stack argument as the requested byte count and the second stack argument as the output buffer before calling OggVorbisStream__ReadPcmSamples; it writes the returned byte count through out_bytes_read and returns 0 or 0x80004005-style failure. Static retail evidence only; exact COM-style contract, buffer ownership, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__ReadDecodedPcm"},
                tags("ogg-file-read", "vtable-slot", "function-boundary", "pcm-decode", "boundary-recovered", "argument-order-corrected", "signature-corrected", "comment-hardened"),
                true,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("requested_byte_count", uintType),
                    param("out_pcm_bytes", voidPtr),
                    param("out_bytes_read", intPtr)
                }
            ),
            new Spec(
                "0x00524770",
                "COggFileRead__CloseAndReset",
                "__thiscall",
                intType,
                "Wave568 vtable slot correction: COggFileRead slot 3 closes and resets the active Ogg/Vorbis stream. It clears libogg/libvorbis state when a FILE pointer is open, closes and clears +0x2008, clears memory-buffer cursor fields at +0x200c/+0x2010, and returns 0. Static retail evidence only; exact member names, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_03_00524770", "COggFileRead__CloseAndReset"},
                tags("ogg-file-read", "vtable-slot", "close-reset", "name-corrected", "signature-corrected", "comment-hardened"),
                false,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00524800",
                "COggFileRead__IsOpen",
                "__thiscall",
                intType,
                "Wave568 recovered vtable slot 4 boundary: returns a boolean-style open-state value from the FILE pointer at +0x2008. Static retail evidence only; exact interface contract, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__IsOpen"},
                tags("ogg-file-read", "vtable-slot", "function-boundary", "field-reader", "boundary-recovered", "signature-corrected", "comment-hardened"),
                true,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00524810",
                "COggFileRead__GetSampleRate",
                "__thiscall",
                intType,
                "Wave568 recovered vtable slot 5 boundary: returns the Vorbis info rate field at this+0x21d0, immediately after the channel count field. Static retail evidence only; exact layout type, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__GetSampleRate"},
                tags("ogg-file-read", "vtable-slot", "function-boundary", "field-reader", "sample-rate", "boundary-recovered", "signature-corrected", "comment-hardened"),
                true,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00524820",
                "COggFileRead__GetChannelCount",
                "__thiscall",
                intType,
                "Wave568 recovered vtable slot 6 boundary: returns the Vorbis info channel-count field at this+0x21cc. Static retail evidence only; exact layout type, runtime playback behavior, and rebuild parity remain unproven.",
                new String[] {"COggFileRead__GetChannelCount"},
                tags("ogg-file-read", "vtable-slot", "function-boundary", "field-reader", "channel-count", "boundary-recovered", "signature-corrected", "comment-hardened"),
                true,
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave568 Ogg/Vorbis tranche failed");
        }
    }
}
