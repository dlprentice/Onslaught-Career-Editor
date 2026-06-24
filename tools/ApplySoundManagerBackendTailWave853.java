//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplySoundManagerBackendTailWave853 extends GhidraScript {
    private static class Spec {
        final String address;
        final String currentName;
        final String expectedName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String currentName, String expectedName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.currentName = currentName;
            this.expectedName = expectedName;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "soundmanager-backend-tail-wave853",
            "wave853-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "source-reference-soundmanager",
            "pc-sound-backend"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType a, DataType b) {
        if (a == null || b == null) {
            return a == b;
        }
        return a.getName().equals(b.getName()) || a.getDisplayName().equals(b.getDisplayName()) || a.isEquivalent(b);
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        Parameter[] actualParams = fn.getParameters();
        if (actualParams.length != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < actualParams.length; i++) {
            Parameter actual = actualParams[i];
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " actual=" + fn.getSignature() + " convention=" + fn.getCallingConventionName());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        String actualName = fn.getName();
        if (!actualName.equals(spec.currentName) && !actualName.equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected current=" + spec.currentName
                + " or final=" + spec.expectedName + " actual=" + actualName);
            stats.bad++;
            return;
        }

        boolean needsRename = !actualName.equals(spec.expectedName);
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);

        if (needsRename) {
            stats.wouldRename++;
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsRename && !needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsSignature) {
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
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.expectedName + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType ucharType = UnsignedCharDataType.dataType;
        DataType charType = CharDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005168d0",
                "CPCSoundManager__dtor",
                "CPCSample__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave853 static read-back/name correction: this is the CPCSample destructor body, not a CPCSoundManager destructor. It installs the CPCSample vtable, calls CSoundManager__KillAllInstancesOfSample on global SOUND/DAT_00896988 for this sample, frees sample data at this+0x78 through CDXMemoryManager__Free, releases the DirectSound buffer at this+0x80 through vtable slot 8, then chains to CSample__DestructorBody. Source pcsoundmanager.cpp CPCSample::~CPCSample matches the sample cleanup shape. Static retail/source-reference evidence only; exact CPCSample layout, runtime DirectSound release behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "cpcsample", "sample-lifetime", "directsound-buffer")
            ),
            new Spec(
                "0x00516960",
                "CPCSoundManager__scalar_deleting_dtor",
                "CPCSample__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("free_flag", ucharType) },
                "Wave853 static read-back/name correction: CPCSample scalar deleting destructor wrapper. It calls CPCSample__dtor, conditionally frees this when free_flag bit 0 is set, and returns this; DATA xref 0x005e4988 is the CPCSample vtable slot 0 pointer. Static retail/source-reference evidence only; exact allocator contract, runtime sample lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "cpcsample", "scalar-deleting-dtor", "vtable-slot")
            ),
            new Spec(
                "0x00516980",
                "CPCSoundManager__GetDeviceCount",
                "CPCSoundManager__GetDeviceCount",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave853 static read-back/signature/comment hardening: tiny PC sound-device enumeration helper returning DAT_00896ca0. Callsite xrefs are PC sound-options/frontend code paths near 0x004cf1f0 and 0x004cf220. Static retail evidence only; exact frontend option schema, runtime device enumeration behavior, BEA patching, and rebuild parity remain deferred.",
                tags("device-enumeration", "frontend-options")
            ),
            new Spec(
                "0x00516990",
                "CPCSoundManager__GetDeviceInfoPtr",
                "CPCSoundManager__GetDeviceInfoPtr",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] { param("index", intType) },
                "Wave853 static read-back/comment hardening: PC sound-device info accessor returning DAT_008964ec + index*0x78. Frontend/options caller xref 0x004cf20e pairs it with CPCSoundManager__GetDeviceCount. Static retail evidence only; exact device-info record schema, runtime device enumeration behavior, BEA patching, and rebuild parity remain deferred.",
                tags("device-enumeration", "frontend-options", "record-stride-0x78")
            ),
            new Spec(
                "0x005171e0",
                "CSoundManager__ReleaseAllVoiceBuffers",
                "CPCSoundManager__DeviceShutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::DeviceShutdown helper, not a generic CSoundManager routine. It logs Shutting down sound device, walks 64 channel slots releasing DS3D buffers at this+0x1c4 and DirectSound buffers at this+0xc4, releases the DirectSound object at this+0xc0, and deletes the wave-reader/helper at this+0x2c8. Xrefs are CSoundManager__Shutdown and CSoundManager__ReinitializeAfterDeviceLoss. Static retail/source-reference evidence only; exact COM interface types, runtime shutdown behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "device-shutdown", "directsound-release", "voice-buffer")
            ),
            new Spec(
                "0x00517260",
                "CSoundManager__StopAllActiveVoices",
                "CPCSoundManager__DeviceReset",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::DeviceReset helper. It walks 64 DirectSound buffer slots at this+0xc4 and calls vtable slot 0x48 (Stop) on each non-null buffer without releasing the buffers. Xref is CSoundManager__ReloadLanguageSampleBank. Static retail/source-reference evidence only; runtime device-reset behavior, exact DirectSound interface identity, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "device-reset", "directsound-stop", "voice-buffer")
            ),
            new Spec(
                "0x00517290",
                "CSoundManager__CreateSample_StubFail",
                "CPCSoundManager__LoadSampleFromBuffer_StubFail",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] { param("mem_buffer", voidPtr), param("music", intType) },
                "Wave853 static read-back/name/signature correction: retail stub for CPCSoundManager::LoadSampleFromBuffer-like path. The body is XOR EAX,EAX; RET 0x8, proving two stack arguments and a null sample return. The only xref is CSoundManager__CreateSample when a data stream is supplied; source pcsoundmanager.h has LoadSampleFromBuffer(CMEMBUFFER*, BOOL) as an unimplemented PC stub returning NULL. Static retail/source-reference evidence only; runtime data-stream sample loading, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "signature-corrected", "stub", "sample-loading")
            ),
            new Spec(
                "0x00517790",
                "CSoundManager__PlaySoundOnChannel",
                "CPCSoundManager__PlaySound",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sound_event", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::PlaySound backend. It computes start/end sample offsets using the selected sample rate, duplicates the sample's DirectSound buffer into the event channel, queries the DS3D buffer interface, seeds volume/pan/3D params through CSoundManager__UpdateSoundPosition and CPCSoundManager__UpdateSound, seeks the channel, starts playback with loop flag from event+0x18, and marks event+0x08 playing. Xrefs are CSoundManager__StartSoundEvent and CSoundManager__SortEventList. Static retail/source-reference evidence only; exact CSoundEvent/CPCSample fields, runtime playback behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "playback", "directsound-buffer", "channel")
            ),
            new Spec(
                "0x00517960",
                "CSoundManager__UpdateChannelLooping",
                "CPCSoundManager__UnPauseSound",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sound_event", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::UnPauseSound helper. It reloads the event channel buffer from this+0xc4 and calls DirectSound Play slot 0x30 with the event looping flag at +0x18. Xref is CSoundManager__UnPauseAllSamples. Static retail/source-reference evidence only; runtime pause/unpause behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "unpause", "directsound-play", "channel")
            ),
            new Spec(
                "0x00517990",
                "CSoundManager__StopChannel",
                "CPCSoundManager__PauseSound",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sound_event", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::PauseSound helper. It checks the event channel buffer at this+0xc4 + channel*4 and calls DirectSound Stop slot 0x48 when present. Xref is CSoundManager__PauseAllSamples. Static retail/source-reference evidence only; runtime pause behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "pause", "directsound-stop", "channel")
            ),
            new Spec(
                "0x005179b0",
                "CSoundManager__StopAndReleaseChannel",
                "CPCSoundManager__StopSound",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sound_event", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::StopSound helper. It stops the event channel buffer, releases/nulls the DirectSound buffer slot at this+0xc4 + channel*4, then releases/nulls the DS3D buffer slot at this+0x1c4 + channel*4. Xrefs include CSample__DestructorBody, CSoundManager__StopSoundEvent, Kill/Pause/Sort/UpdateStatus paths. Static retail/source-reference evidence only; exact block_until_stopped handling, runtime channel lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "stop-sound", "directsound-release", "channel")
            ),
            new Spec(
                "0x00517a20",
                "CSoundManager__UpdateListener3D",
                "CPCSoundManager__UpdateGlobals",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::UpdateGlobals/listener update stub. When initialized, it builds a DS3DLISTENER-sized 0x40-byte local parameter block with neutral orientation/distance/doppler constants and calls the listener at this+0x2c4 vtable slot 0x28 with deferred flag 1. Xref is CSoundManager__UpdateStatus. Static retail/source-reference evidence only; exact listener parameter fields, runtime 3D audio behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "listener", "directsound3d", "update-globals")
            ),
            new Spec(
                "0x00517ad0",
                "CSoundManager__GetOutputEnabledFlag",
                "CSoundManager__GetOutputEnabledFlag",
                "__cdecl",
                ucharType,
                new ParameterImpl[] {},
                "Wave853 static read-back/signature/comment hardening: tiny audio gate helper returning DAT_00896c58. The saved xref is CSoundManager__PlayEffect, where the return controls whether the effect can proceed to playback. Static retail evidence only; exact global meaning, runtime sound-enable behavior, BEA patching, and rebuild parity remain deferred.",
                tags("audio-gate", "global-flag", "play-effect")
            ),
            new Spec(
                "0x00517ae0",
                "CSoundManager__UpdateChannelParams",
                "CPCSoundManager__UpdateSound",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("sound_event", voidPtr), param("first_time", intType) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::UpdateSound backend. It updates the DS3D buffer at this+0x1c4 with event position/velocity when present, applies distance rolloff to current attenuated volume, writes DirectSound volume slot 0x3c, updates frequency when continuous-rate support DAT_008964d0 is enabled, and stops the event when status no longer has looping/playing flags during non-first-time updates. Xrefs include volume recompute, CSoundManager__UpdateStatus, and CPCSoundManager__PlaySound. Static retail/source-reference evidence only; exact event field schema, runtime mixing/3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "update-sound", "directsound3d", "channel-params")
            ),
            new Spec(
                "0x00517c40",
                "CSoundManager__CommitListener",
                "CPCSoundManager__UpdatesDone",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::UpdatesDone helper. If initialized and listener at this+0x2c4 is non-null, it calls listener vtable slot 0x44 to commit deferred DirectSound3D settings. Xref is CSoundManager__UpdateStatus. Static retail/source-reference evidence only; runtime listener commit behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "listener", "commit-deferred", "directsound3d")
            ),
            new Spec(
                "0x00517c60",
                "CSoundManager__GetSampleDurationSeconds",
                "CPCSoundManager__GetSampleLength",
                "__stdcall",
                doubleType,
                new ParameterImpl[] { param("sample", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::GetSampleLength helper. It selects 44100/22050/11025 Hz from g_SoundSampleRateIndex, reads CPCSample byte length at sample+0x7c, and returns length divided by sample_rate*2. Xrefs include CSoundManager__UpdateStatus end-point checks and CCutscene__PrepareAnimations. Static retail/source-reference evidence only; exact sample format assumptions, runtime timing behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "sample-length", "timing", "sample-rate")
            ),
            new Spec(
                "0x00517cb0",
                "CSoundManager__FindFreeChannel",
                "CPCSoundManager__FindFreeChannel",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave853 static read-back/name correction: source-backed CPCSoundManager::FindFreeChannel helper. It scans up to this+0x2cc active voice count, rejects any channel already used by active events on DAT_00896994, and returns the first channel whose DirectSound buffer slot at this+0xc4 is null or -1 if none are free. Xrefs are CSoundManager__StartSoundEvent and CSoundManager__SortEventList. Static retail/source-reference evidence only; exact active-event list schema, runtime channel allocation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "channel-allocation", "voice-count")
            ),
            new Spec(
                "0x00517d00",
                "CSoundManager__LoadCompressedSampleBank",
                "CSoundManager__LoadCompressedSampleBank",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("stream_mode", charType) },
                "Wave853 static read-back/comment hardening: PC compressed sample-bank loader reached from CSoundManager__ReloadLanguageSampleBank and CSoundManager__ReinitializeAfterDeviceLoss. It skips during resource build, respects DAT_0066307c compressed-sound enable, opens the cached XAP path at this+0x88 through CDXMemBuffer__InitFromFile, logs XAP load/cache diagnostics, reads sample count/name records, calls CSoundManager__CreateSample with stream_mode, updates loading fraction, closes/destroys the mem-buffer, and preserves the SEH cleanup path. Static retail/source-reference evidence only; exact XAP schema, runtime sample-bank loading behavior, BEA patching, and rebuild parity remain deferred.",
                tags("compressed-sample-bank", "xap", "language-bank", "mem-buffer")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
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
            throw new RuntimeException("Wave853 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
        if (!dryRun) {
            currentProgram.flushEvents();
        }
    }
}
