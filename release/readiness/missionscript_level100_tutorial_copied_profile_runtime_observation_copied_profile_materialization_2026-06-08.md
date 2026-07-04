# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Readiness Note

Status: complete clean copied-profile materialization, not patch or runtime proof
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization`

This slice materialized the selected Level100 copied-profile runtime observation profile under an app-owned ignored artifact-root class. It used the verified clean backup executable as the copied `BEA.exe` source and read-only installed game resource/default-options material for the rest of the profile.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan`.

Evidence anchors:

- `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof`
- Public proof: `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md`
- Machine-readable result: `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json`
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`
- Sanitized profile id: `level100-clean-materialized-20260608-214752`
- `status=COMPLETE`
- `materializationStatus=clean-copied-profile-created`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `sourceExecutableClass=canonical-clean-retail-backup-specimen`
- `sourceResourceClass=read-only-installed-game-resource-material`
- Preparation helper: `tools/prepare_game_profile.ps1`
- Executable override used: `true`
- `copiedProfileCreated=true`
- `copiedExecutableCreated=true`
- `copiedSpecimenHashChecked=true`
- Expected clean SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Copied executable SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `copiedExecutableSha256Class=matches-canonical-clean-retail`
- `copiedExecutableBytes=2506752`
- `payloadFileCount=5479`
- `payloadTotalBytes=696783748`
- `dataFileCount=5464`
- `savegameFileCount=9`
- `privateEvidenceFileCount=3`
- `localPrivateArtifactFileCount=5482`
- `localPrivateArtifactTotalBytes=696793402`
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `beLaunch=false`
- `launchArmed=false`
- `executablePatch=false`
- `screenshotCapture=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `runtimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

Preserved static anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

Deferred stable patch ids: `resolution_gate`, `force_windowed`, `version_overlay_use_patched_format_pointer`, and `version_overlay_patched_format_cave_string`. Experimental patch id not armed: `skip_auto_toggle`.

What this proves:

- A copied profile exists in an app-owned ignored artifact-root class.
- The copied `BEA.exe` exists and matches the canonical clean Steam retail/Ghidra specimen hash.
- The copied profile was created with `tools/prepare_game_profile.ps1` using a clean executable override.
- The installed game root and original executable remained read-only.

What remains unproven:

- BEA launch behavior.
- BEA patching behavior.
- Runtime MissionScript execution.
- Runtime command effects and event outcomes.
- Live loose-MSL loading or packed-vs-loose script selection.
- Runtime Level100 outcome, objective UI, message/audio output, HUD flashing, object identity, `SpawnThing`, or `GetThingRef` behavior.
- Screenshot/capture proof, native input behavior, debugger observation behavior, Godot parity, rebuild parity, and no-noticeable-difference parity.

Next selected child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan`.
