# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Readiness Note

Status: complete launch-command proof, not BEA launch or runtime proof
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command`

This slice proves launch command construction for the patched copied-profile `BEA.exe` without starting BEA. It verifies copied-profile path selection, copied executable and backup hashes, command classes, launch arming, and stop-before-create-process boundaries. It did not run BEA, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

This readiness note is the release-facing summary for the MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan`.

Public proof files:

- `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md`
- `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json`
- `tools/missionscript_level100_tutorial_copied_profile_runtime_observation_launch_command_probe.py`

Static authority remains:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Launch-command proof summary:

- `status=COMPLETE`
- `launchCommandStatus=ready-unarmed-command-proof`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `targetExecutableClass=copied-profile-BEA.exe`
- `workingDirectoryClass=copied-profile-root`
- `launchHelper=tools/start_game_profile.ps1`
- `launchHelperMode=PrintOnly`
- `commandClassCount=3`
- `selectedInitialRoute=skip-fmv-copied-profile-launch`
- `directLevel100Route=direct-level100-candidate`
- `directLevel100RouteStatus=candidate-unproven-unarmed`
- `patchStatus=stable-copied-executable-patched`
- `stablePatchRows=4`
- `skipAutoToggleArmed=false`
- `targetHash=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- `backupHash=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `targetBytes=2506752`
- `backupBytes=2506752`
- `beProcessesBefore=0`
- `invalidArgumentRejected=true`
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `beLaunch=false`
- `launchArmed=false`
- `launchCommandExecuted=false`
- `processStarted=false`
- `stopBeforeCreateProcess=true`
- `launchArmGateSpecified=true`
- `screenshotCapture=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `runtimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

Command classes:

| Command class | Argument vector | Status | Public preview |
| --- | --- | --- | --- |
| `baseline-copied-profile-launch` | `[]` | `ready-unarmed` | `Start-Process -FilePath "<COPIED_PROFILE>\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>"` |
| `skip-fmv-copied-profile-launch` | `["-skipfmv"]` | `ready-unarmed` | `Start-Process -FilePath "<COPIED_PROFILE>\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>" -ArgumentList "-skipfmv"` |
| `direct-level100-candidate` | `["-skipfmv", "-level", "100"]` | `candidate-unproven-unarmed` | `Start-Process -FilePath "<COPIED_PROFILE>\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>" -ArgumentList "-skipfmv -level 100"` |

Level100 static source-selection anchors preserved for the later launch-window smoke proof: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

What this proves:

- A copied-profile launch command can be constructed through `tools/start_game_profile.ps1 -PrintOnly`.
- The command target class is the copied-profile `BEA.exe`, with the copied-profile root as working-directory class.
- The copied executable and clean backup hashes match the expected patched-copy and clean-retail hash classes.
- Three command classes are documented: baseline, skip-FMV, and direct Level100 candidate.
- Unsupported launch arguments are rejected before launch.
- Launch remains unarmed and stops before process creation.
- The installed game root and original executable remained read-only.

What remains unproven:

- BEA launch behavior.
- Runtime behavior of any patch row.
- Runtime MissionScript execution.
- Runtime command effects.
- Runtime event outcomes.
- Live loose-MSL loading.
- Packed-vs-loose script selection.
- Runtime Level100 mission outcome.
- Runtime objective UI.
- Runtime message or audio output.
- Runtime HUD flashing.
- Runtime object identity.
- Runtime `SpawnThing` behavior.
- Runtime `GetThingRef` lookup behavior.
- Screenshot/capture proof.
- Native input behavior.
- Debugger observation behavior.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

Next selected child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan`.
