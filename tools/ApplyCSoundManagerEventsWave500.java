//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCSoundManagerEventsWave500 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] tags) {
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "csoundmanager-wave500",
            "retail-binary-evidence",
            "audio",
            "sound-manager",
            "sound-event",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean updateNeeded = needsUpdate(fn, spec);
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + spec.name);
                return;
            }
            if (dryRun) {
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!signatureMatches(readBack, spec)) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            if (!hasAllTags(readBack, spec.tags)) {
                throw new IllegalStateException("Read-back missing one or more tags at " + spec.address);
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getSignature());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004e0f70",
                "CSoundManager__StopSoundEvent",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("sound_event", voidPtr),
                    param("block_until_stopped", intType)
                },
                "Wave500 signature/comment/tag hardening: the retail binary takes a CSoundEvent pointer and block-until-stopped flag on the stack (RET 0x8), not a hidden CSoundManager this parameter. It invokes the owner SampleFinishedPlaying callback when mInformOwnerWhenComplete and the owner reader are set, calls CSoundManager__StopAndReleaseChannel(&DAT_00896988, sound_event, block_until_stopped) for assigned channels, clears mPlaying, and clears the active reader. Static retail-binary/source evidence only; runtime audio behavior, exact CSoundEvent layout typing, and rebuild parity remain unproven.",
                tags("event-stop", "active-reader")
            ),
            new Spec(
                "0x004e0fb0",
                "CSoundManager__AllocateSoundEvent",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("insert_at_top", intType)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::GetSoundEvent(BOOL insertattop). The helper pops an event from the pool at this+0x34, links it into mFirstSoundEvent at this+0x0c either at the top or after currently channel-assigned events, increments the event count at this+0x08, and returns the event pointer or NULL after the out-of-sound-events DebugTrace. Static retail-binary/source evidence only; exact CSoundManager/CSoundEvent layout typing, runtime allocation behavior, and rebuild parity remain unproven.",
                tags("event-pool", "source-parity")
            ),
            new Spec(
                "0x004e1040",
                "CSoundManager__SortEventList",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::SortEventList. The retail body bubble-sorts active events by current attenuated volume at +0x68, computes a three-quarter channel budget from the available-channel global DAT_00896c54, releases lower-priority assigned channels through CSoundManager__StopAndReleaseChannel, then assigns free channels and calls CSoundManager__PlaySoundOnChannel for unpaused high-priority events. Static retail-binary/source evidence only; runtime mixing behavior, exact list layout typing, and rebuild parity remain unproven.",
                tags("event-sort", "channel-budget", "source-parity")
            ),
            new Spec(
                "0x004e1130",
                "CSoundManager__KillSamplesForThing",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner", voidPtr)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::KillSamplesForThing(IAudibleThing *thing). It iterates mFirstSoundEvent, filters currently-playing events whose active-reader owner equals owner, then performs the same owner-complete callback, channel release with block_until_stopped=0, mPlaying clear, and active-reader clear used by StopSoundEvent. Static retail-binary/source evidence only; runtime audio behavior, exact owner/event typing, and rebuild parity remain unproven.",
                tags("event-stop", "owner-filter", "source-parity")
            ),
            new Spec(
                "0x004e1190",
                "CSoundManager__KillSample",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner", voidPtr),
                    param("sample", voidPtr)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::KillSample(IAudibleThing *thing, const CSample *sample). It iterates active events, filters by owner active-reader plus sample pointer plus mPlaying, then performs the same callback/channel-release/reader-clear stop path with block_until_stopped=0. Static retail-binary/source evidence only; runtime audio behavior, exact sample/event typing, and rebuild parity remain unproven.",
                tags("event-stop", "owner-filter", "sample-filter", "source-parity")
            ),
            new Spec(
                "0x004e12b0",
                "CSoundManager__KillAllSamples",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::KillAllSamples. It walks the active sound-event list, invokes owner-complete callbacks when requested, releases assigned channels with block_until_stopped=0, clears mPlaying, and clears each event's active reader. Static retail-binary/source evidence only; runtime audio behavior, exact event layout typing, and rebuild parity remain unproven.",
                tags("event-stop", "bulk-stop", "source-parity")
            ),
            new Spec(
                "0x004e1300",
                "CSoundManager__PauseAllSamples",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::PauseAllSamples, while the retail body is documented by the binary. It walks active events, calls CSoundManager__StopChannel(&DAT_00896988, sound_event) for channel-assigned entries, and sets each event paused flag at +0x84. Static retail-binary/source evidence only; runtime pause behavior, exact event layout typing, and rebuild parity remain unproven.",
                tags("pause", "channel-state", "source-parity")
            ),
            new Spec(
                "0x004e1330",
                "CSoundManager__UnPauseAllSamples",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::UnPauseAllSamples, while the retail body is documented by the binary. It walks active events, calls CSoundManager__UpdateChannelLooping(&DAT_00896988, sound_event) for channel-assigned entries, and clears each event paused flag at +0x84. Static retail-binary/source evidence only; runtime unpause behavior, exact event layout typing, and rebuild parity remain unproven.",
                tags("pause", "channel-state", "source-parity")
            ),
            new Spec(
                "0x004e1360",
                "CSoundManager__UpdateSoundPosition",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("sound_event", voidPtr),
                    param("first_time", intType)
                },
                "Wave500 signature/comment/tag hardening: the retail binary takes sound_event and first_time on the stack, with no hidden CSoundManager this parameter, and source-aligns to CSoundManager::UpdateSoundPosition(CSoundEvent *se, BOOL firsttime). It reads game camera 0/1, updates event position/velocity for tracking modes, chooses the nearest multiplayer camera frame, transforms positions into camera-local coordinates, handles left/right sample pan offsets, applies g_InvertXAxisFlag, and recalculates pan for followed owners. Static retail-binary/source evidence only; runtime 3D audio behavior, exact matrix/event layout typing, and rebuild parity remain unproven.",
                tags("positioning", "tracking", "camera", "source-parity")
            ),
            new Spec(
                "0x004e18d0",
                "CSoundManager__SetPitch",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("sound_event", voidPtr),
                    param("desired_pitch_factor", floatType),
                    param("fade_time_seconds", floatType)
                },
                "Wave500 signature/comment/tag hardening: this source-aligns to CSoundManager::SetPitch(CSoundEvent *e, float desiredpitchfactor, float fadetime). When the manager is initialized and sound_event is non-null, the retail body stores desired_pitch_factor at event+0x3c and stores round(fade_time_seconds * 20.0) at event+0x40 for the pitch fade ticks. Static retail-binary/source evidence only; runtime pitch behavior, exact event layout typing, and rebuild parity remain unproven.",
                tags("pitch", "source-parity")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
