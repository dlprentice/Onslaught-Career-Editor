//@category BEA

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class ApplyInputAudioSupportCurrentRiskWave1179 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String signature;
        final List<String> tags;

        Spec(String address, String name, String signature, String... tags) {
            this.address = address;
            this.name = name;
            this.signature = signature;
            this.tags = Arrays.asList(tags);
        }
    }

    private static final String[] COMMON_TAGS = {
        "static-reaudit",
        "wave1179-input-audio-support-current-risk-review",
        "wave1179-readback-verified",
        "retail-binary-evidence",
        "current-risk-review",
        "input-audio-support",
        "tag-normalized",
        "comment-hardened"
    };

    private static Spec spec(String address, String name, String signature, String... extraTags) {
        List<String> tags = new ArrayList<>();
        tags.addAll(Arrays.asList(COMMON_TAGS));
        tags.addAll(Arrays.asList(extraTags));
        return new Spec(address, name, signature, tags.toArray(new String[0]));
    }

    private static final Spec[] SPECS = {
        spec("0x0042da00", "Input__UpdateCursorCenterWithWindowScale",
            "void __cdecl Input__UpdateCursorCenterWithWindowScale(bool recenterNow)",
            "input", "cursor-center", "window-scale", "game-loop", "score-20-current-risk"),
        spec("0x00523db0", "Input__ResetMouseTransientState",
            "void __cdecl Input__ResetMouseTransientState(void)",
            "input", "mouse-state", "mouse-transient-reset", "platform-input", "score-20-current-risk"),
        spec("0x004cdd70", "GameControllers__RelinquishControlForTarget",
            "void __fastcall GameControllers__RelinquishControlForTarget(void * controlled_target)",
            "controller", "control-target", "relinquish-control", "message-log", "score-20-current-risk"),
        spec("0x004cddf0", "Audio__ReinitializeSoundAndRestoreMusic",
            "void __cdecl Audio__ReinitializeSoundAndRestoreMusic(int frontend_music_after_reset)",
            "audio", "device-loss", "music-restore", "options-tail", "score-20-current-risk"),
        spec("0x005054e0", "CWaveSoundRead__ScalarDeletingDestructor",
            "void * __thiscall CWaveSoundRead__ScalarDeletingDestructor(void * this, byte delete_flags)",
            "audio", "wave-sound-read", "scalar-deleting-destructor", "destructor", "score-16-current-risk"),
        spec("0x00517290", "CPCSoundManager__LoadSampleFromBuffer_StubFail",
            "void * __stdcall CPCSoundManager__LoadSampleFromBuffer_StubFail(void * mem_buffer, int music)",
            "audio", "pc-sound-backend", "sample-loading-stub", "stub-fail", "score-19-current-risk")
    };

    @Override
    protected void run() throws Exception {
        boolean dryRun = true;
        String[] args = getScriptArgs();
        if (args.length > 0) {
            String mode = args[0].trim().toLowerCase();
            if ("apply".equals(mode)) {
                dryRun = false;
            } else if (!"dry".equals(mode)) {
                throw new IllegalArgumentException("Expected mode dry|apply, got: " + args[0]);
            }
        }

        FunctionManager functionManager = currentProgram.getFunctionManager();
        int updated = 0;
        int skipped = 0;
        int tagsAdded = 0;
        int missing = 0;
        int bad = 0;

        for (Spec spec : SPECS) {
            Address address = toAddr(spec.address);
            Function function = functionManager.getFunctionAt(address);
            if (function == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                missing++;
                continue;
            }

            boolean specBad = false;
            if (!spec.name.equals(function.getName())) {
                println("BADNAME: " + spec.address + " expected=" + spec.name + " actual=" + function.getName());
                specBad = true;
            }
            if (!spec.signature.equals(function.getSignature().toString())) {
                println("BADSIG: " + spec.address + " expected=" + spec.signature + " actual=" + function.getSignature());
                specBad = true;
            }
            if (specBad) {
                bad++;
                continue;
            }

            Set<String> existingTags = tagNames(function);
            List<String> missingTags = new ArrayList<>();
            for (String tag : spec.tags) {
                if (!existingTags.contains(tag)) {
                    missingTags.add(tag);
                }
            }

            if (missingTags.isEmpty()) {
                println("SKIP: " + spec.address + " " + spec.name + " tags already present");
                skipped++;
                continue;
            }

            tagsAdded += missingTags.size();
            if (dryRun) {
                println("WOULD_TAG: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
                continue;
            }

            for (String tag : missingTags) {
                function.addTag(tag);
            }
            println("TAGGED: " + spec.address + " " + spec.name + " +" + String.join(",", missingTags));
            updated++;
            currentProgram.flushEvents();
            Thread.sleep(50L);
        }

        if (!dryRun) {
            int verificationFailures = 0;
            for (Spec spec : SPECS) {
                Address address = toAddr(spec.address);
                Function function = functionManager.getFunctionAt(address);
                if (function == null) {
                    println("VERIFY_MISSING: " + spec.address);
                    verificationFailures++;
                    continue;
                }
                Set<String> tags = tagNames(function);
                for (String tag : spec.tags) {
                    if (!tags.contains(tag)) {
                        println("VERIFY_MISSING_TAG: " + spec.address + " " + tag);
                        verificationFailures++;
                    }
                }
            }
            bad += verificationFailures;
        }

        println("SUMMARY: updated=" + updated
            + " skipped=" + skipped
            + " renamed=0"
            + " would_rename=0"
            + " signature_updated=0"
            + " comment_only_updated=0"
            + " tags_added=" + tagsAdded
            + " missing=" + missing
            + " bad=" + bad);

        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("Wave1179 input/audio support tag normalization failed: missing=" + missing + " bad=" + bad);
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }

    private Set<String> tagNames(Function function) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : function.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }
}
