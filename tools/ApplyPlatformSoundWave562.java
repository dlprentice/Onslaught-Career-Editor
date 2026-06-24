//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
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

public class ApplyPlatformSoundWave562 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "platform-sound-wave562",
            "retail-binary-evidence",
            "source-parity",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
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
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType boolType = BooleanDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType shortPtr = new PointerDataType(ShortDataType.dataType);
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = voidPtr();

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005154e0",
                "PCPlatform__Init",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave562 signature/comment hardening: source-aligns to CPCPlatform::Init with retail shader/timer setup. The body allocates a 0x38-byte CFrameTimer, starts it at 1.0f, queries the performance-counter frequency into this+0x08, initializes a 1.0f field at this+0x10, toggles the retail vertex-shader support global from command/capability flags, and calls InitShaderCapabilityFlagsAndCVar. Static retail/source evidence only; exact CPCPlatform/CFrameTimer layout, runtime device behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-platform", "init", "frame-timer", "shader-init")
            ),
            new Spec(
                "0x005155e0",
                "PCPlatform__LoadFonts",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave562 signature/comment hardening: source-aligns to CPCPlatform::InitFonts. The retail body lazily allocates CDXBitmapFont-like objects for the main, debug, small, and title font slots at this+0x18/0x1c/0x20/0x24, loads font22_512.tga, Terminal, Font13PS.tga, and TitleFont.tga, enables the main-font swap flag, then clears this+0x28 and this+0x2c. Static retail/source evidence only; exact font class layout, resource load behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-platform", "fonts", "font-load")
            ),
            new Spec(
                "0x005157b0",
                "CPCPlatform__UnloadFonts",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave562 signature/comment hardening: source-aligns to CPCPlatform::Shutdown font cleanup. The retail body releases font/resource slots at this+0x18 through this+0x2c with the CDXBitmapFont cleanup helper plus CDXMemoryManager__Free, clears each slot, then frees the platform data pointer at this+0x00 when present. Static retail/source evidence only; exact CPCPlatform field layout, runtime shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-platform", "fonts", "shutdown")
            ),
            new Spec(
                "0x005169b0",
                "CPCSoundManager__Init",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave562 signature/comment hardening: retail PC DirectSound backend initializer. The body creates the CWaveSoundRead helper, clears the sound-buffer table, enumerates DirectSound devices, clamps g_SoundDeviceIndex, creates the selected DirectSound8 device, sets DSSCL_PRIORITY cooperative level, queries caps/continuous-rate support, selects 3D sound and voice counts, creates the primary buffer, applies the quality-dependent PCM format, and queries the IDirectSound3DListener. Static retail/source-adjacent evidence only; exact CPCSoundManager/DirectSound layout, runtime device behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-sound", "directsound", "init", "device-enumeration")
            ),
            new Spec(
                "0x005172a0",
                "CPCSoundManager__CreateSampleFromFile",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("sample_source", voidPtr),
                    param("channel_type", intType),
                    param("reusable_sample", voidPtr)
                },
                "Wave562 signature/comment hardening: CSoundManager__CreateSample calls this with a backend sample source, channel_type, and optional reusable CSample pointer; RET 0x0c proves three stack arguments. The body reads a compressed byte count, allocates or refreshes a 0x84-byte CPCSample-like object, reads ADPCM bytes, creates and locks a DirectSound buffer, decodes ADPCM directly or through a temporary high-quality buffer, converts quality-dependent output, unlocks the buffer, and frees temporary storage. Static retail-binary evidence only; exact sample-source/CPCSample layout, runtime audio decode/playback behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-sound", "sample-create", "adpcm", "directsound-buffer")
            ),
            new Spec(
                "0x00517440",
                "CPCSoundManager__CreateSoundBuffer",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("out_ds_buffer", voidPtr),
                    param("source_byte_count", uintType)
                },
                "Wave562 signature/comment hardening: CPCSoundManager sample loaders call this helper with a DirectSound-buffer output slot and source byte count. The body builds a quality-dependent PCM WAVEFORMAT/DSBUFFERDESC, selects the 3D algorithm GUID from DAT_00896a44, scales buffer bytes for medium/low quality, creates a secondary DirectSound buffer through DAT_00896a48, locks the full buffer for writing, and returns the locked write pointer or NULL on failure. Static retail-binary evidence only; exact DirectSound interface typing, buffer flag semantics, runtime playback behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-sound", "directsound-buffer", "format-conversion")
            ),
            new Spec(
                "0x00517600",
                "CPCSoundManager__ConvertAudioFormat",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("destination", voidPtr),
                    param("source_pcm16", shortPtr),
                    param("source_byte_count", uintType)
                },
                "Wave562 signature/comment hardening: quality-dependent PCM conversion helper used after ADPCM decode and by direct sample-from-data creation. Quality 0 copies bytes through unchanged, quality 1 averages stereo 16-bit pairs into downsampled 16-bit mono output, and lower quality averages four samples into unsigned 8-bit output. Static retail-binary evidence only; exact mixer expectations, runtime audio quality behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-sound", "format-conversion", "sample-rate")
            ),
            new Spec(
                "0x005176d0",
                "CPCSoundManager__CreateSampleFromData",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("pcm_data", voidPtr),
                    param("byte_count", uintType),
                    param("unused_arg", intType),
                    param("reusable_sample", voidPtr)
                },
                "Wave562 signature/comment hardening: CGame__PumpBinkVoiceSampleQueue calls this four-stack-argument helper and RET 0x10 proves the callee cleanup. The body allocates or refreshes a 0x84-byte CPCSample-like object, records byte_count at sample+0x7c, creates and locks a DirectSound buffer, converts the supplied PCM data into the quality-dependent target format, then unlocks the buffer. The third stack argument is preserved as unused in the retail body. Static retail-binary evidence only; exact Bink voice/sample layout, runtime voice playback behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-sound", "sample-create", "bink-voice", "format-conversion")
            ),
            new Spec(
                "0x00517fa0",
                "CPCSoundManager__DecodeADPCM",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("source_adpcm", charPtr),
                    param("destination_pcm16", shortPtr),
                    param("sample_count", uintType),
                    param("decoder_state", shortPtr)
                },
                "Wave562 signature/comment hardening: IMA ADPCM decode helper used by CPCSoundManager__CreateSampleFromFile. The body uses the 16-entry index table at 0x0063e85c and 89-entry step table at 0x0063e89c, consumes alternating nibbles, clamps output to signed 16-bit PCM, writes samples to destination_pcm16, and updates the predictor/step-index decoder_state for streaming continuity. Static retail-binary evidence only; runtime audio decode coverage, BEA launch, patching, and rebuild parity remain unproven.",
                tags("pc-sound", "adpcm", "decode")
            )
        };

        Stats stats = new Stats();
        println("ApplyPlatformSoundWave562 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave562 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
