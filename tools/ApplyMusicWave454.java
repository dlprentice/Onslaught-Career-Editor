//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMusicWave454 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "music-wave454",
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
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
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

            Function readBack = functionAtEntry(spec.address);
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
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
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
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004bb380",
                "CMusic__Init",
                "CMusic__Init",
                "__fastcall",
                voidType,
                "Wave454 signature/comment hardening: CMusic device initialise and retail volume seed path. The body clears mPlaying and playlist head, sets play type linear, calls the platform device initialise vfunc, seeds current/target volume to 0x7f, derives set volume from CAREER_mMusicVolume, clears the queued-song field, and marks the object initialised. Static retail evidence only; source CMusic::Initialise also shows console registration context, but runtime audio playback, exact PC platform behavior, and rebuild parity remain unproven.",
                tags("music", "initialization", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004bb400",
                "CMusic__Shutdown",
                "CMusic__Shutdown",
                "__fastcall",
                voidType,
                "Wave454 signature/comment hardening: CMusic shutdown path. Stops active playback when the playing flag is set, calls the platform device shutdown vfunc, walks playlist entries through their +0x104 next links, frees them, and clears the playlist head. Static retail evidence only; runtime audio playback, concrete CMusic/CSong layout, and rebuild parity remain unproven.",
                tags("music", "shutdown", "playlist", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004bb450",
                "CMusic__Play",
                "CMusic__Play",
                "__thiscall",
                voidType,
                "Wave454 signature/comment correction: CMusic play path with one stack filename argument; ret 0x4 fixes the prior hidden-argument decompile that used unaff_retaddr. The body stops current playback if needed, copies set volume into current/target volume, calls the platform set-volume vfunc, calls the platform DevicePlay vfunc with filename, and sets mPlaying. Static retail evidence only; runtime audio playback and rebuild parity remain unproven.",
                tags("music", "playback", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("filename", charPtr)
                }
            ),
            new Spec(
                "0x004bb490",
                "CMusic__Stop",
                "CMusic__Stop",
                "__fastcall",
                voidType,
                "Wave454 signature/comment hardening: CMusic stop path. If +0x08 mPlaying is set, calls the platform stop vfunc at vtable +0x0c and clears the playing flag; otherwise returns without touching device state. Static retail evidence only; runtime audio playback and rebuild parity remain unproven.",
                tags("music", "stop", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004bb4b0",
                "CMusic__UpdateVolumeFade",
                "CMusic__FadeVolumes",
                "__fastcall",
                voidType,
                "Wave454 source-parity name/signature/comment correction: CMusic::FadeVolumes-style helper. When initialised, snaps current volume to target when within 10, steps current volume by 5 toward target, starts the queued song through CMusic__PlayFromList when fade reaches zero, clears the queued-song field, and restores target volume to set volume when reached. Static retail evidence only; runtime audio playback and rebuild parity remain unproven.",
                tags("music", "fade", "source-parity", "name-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004bb530",
                "CMusic__Update",
                "CMusic__UpdateStatus",
                "__fastcall",
                voidType,
                "Wave454 source-parity name/signature/comment correction: CMusic::UpdateStatus-style per-frame status path. Calls the platform update vfunc, runs CMusic__FadeVolumes while playing, clamps volume to 0..127, updates device volume, handles track-finished modes 0 single/stop, 1 linear playlist, 2 random playlist, and 3 selection replay, with the retail dev/all-cheats override forcing data/music/BEA 08(Master).wma. Static retail evidence only; runtime audio playback and rebuild parity remain unproven.",
                tags("music", "update", "source-parity", "name-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004bb6b0",
                "CMusic__AddToPlaylist",
                "CMusic__AddToPlayList",
                "__thiscall",
                voidType,
                "Wave454 source-parity name/signature/comment correction: CMusic::AddToPlayList-style sorted playlist insertion. Rejects duplicate track_path strings, allocates a 0x10c-byte CSong-like entry from the music pool, inserts it alphabetically through +0x104 next links, copies the filename into the entry, and prints the Added %s to playlist message. Static retail evidence only; concrete CSong layout, runtime directory enumeration, and rebuild parity remain unproven.",
                tags("music", "playlist", "source-parity", "name-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("track_path", charPtr)
                }
            ),
            new Spec(
                "0x004bb7c0",
                "CMusic__LoadPlaylistFromDir",
                "CMusic__LoadPlaylistFromDir",
                "__thiscall",
                voidType,
                "Wave454 signature/comment correction: one-stack-argument directory_path wrapper that calls the platform DeviceAddDirectoryExts-style vfunc at +0x18 with directory_path plus the retail extension token at 0x00630a04, then ret 0x4. Name remains behavior-bounded because the retail body is a platform-specific extension wrapper rather than the full PC source AddDirectoryToPlaylist body. Static retail evidence only; runtime directory enumeration and rebuild parity remain unproven.",
                tags("music", "playlist", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("directory_path", charPtr)
                }
            ),
            new Spec(
                "0x004bb7e0",
                "CMusic__PlayTrack",
                "CMusic__PlayFromList",
                "__thiscall",
                voidType,
                "Wave454 source-parity name/signature/comment correction: CMusic::PlayFromList-style helper. With fade enabled while already playing, queues song_entry at +0x30 and fades target volume to zero; otherwise NULL song_entry selects a random playlist entry, updates current song at +0x10, sets random play type when needed, applies the retail dev/all-cheats BEA 08(Master).wma override, and either crossfades or starts playback directly. Ret 0x8 confirms song_entry and fade stack arguments. Static retail evidence only; runtime audio playback and rebuild parity remain unproven.",
                tags("music", "playlist", "source-parity", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("song_entry", voidPtr),
                    param("fade", intType)
                }
            ),
            new Spec(
                "0x004bb8c0",
                "CMusic__PlayTrackByType",
                "CMusic__PlaySelection",
                "__thiscall",
                voidType,
                "Wave454 source-parity name/signature/comment correction: CMusic::PlaySelection-style helper. Maps music_selection 0 frontend, 1 credits, 2 tutorial, and 3/4 gameplay/stealth to retail track indices, emits the Playing Track trace, resolves a playlist entry by index with head fallback, stores selection mode and +0x3c music_selection, and either queues a fade or starts/crossfades with the retail dev/all-cheats override. Ret 0x8 confirms music_selection and fade stack arguments. Static retail evidence only; runtime audio playback and rebuild parity remain unproven.",
                tags("music", "selection", "source-parity", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("music_selection", intType),
                    param("fade", intType)
                }
            ),
            new Spec(
                "0x004bba10",
                "CMusic__SetMasterVolume",
                "CMusic__SetVolume",
                "__thiscall",
                voidType,
                "Wave454 source-parity name/signature/comment correction: CMusic::SetVolume-style setter. Retail converts the input float volume linearly into the 0..127 set-volume field at +0x2c, logs the input/master music volume message, and persists CAREER_mMusicVolume. Static retail evidence only; source PC tangent-volume path differs from this retail body, runtime audio loudness behavior and rebuild parity remain unproven.",
                tags("music", "volume", "source-parity", "name-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("volume", floatType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave454 apply had missing/bad entries");
        }
    }
}
