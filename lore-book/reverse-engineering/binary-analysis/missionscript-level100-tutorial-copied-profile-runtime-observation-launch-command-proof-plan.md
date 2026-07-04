# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan

Status: complete launch-command proof, not BEA launch or runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md`

This slice proves launch command construction for the patched copied-profile `BEA.exe` without starting BEA. It reads the ignored private launch-command manifest for the sanitized Level100 copied-profile artifact-root class, verifies the copied executable and clean backup hashes, verifies copied-profile working-directory selection, verifies command-class construction through `tools/start_game_profile.ps1 -PrintOnly`, and records the launch arm gate and stop-before-create-process boundary. It did not run BEA, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This launch-command proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Command Result

Private command evidence exists under the ignored artifact-root class. Public docs expose only sanitized counts/classes, command classes, hash classes, and stop conditions:

- Sanitized profile id: `level100-clean-materialized-20260608-214752`.
- Artifact-root class: `repo-local ignored private evidence root`.
- Target executable class: `copied-profile-BEA.exe`.
- Working directory class: `copied-profile-root`.
- Launch helper: `tools/start_game_profile.ps1`.
- Launch helper mode: `PrintOnly`.
- `commandClassCount=3`.
- `selectedInitialRoute=skip-fmv-copied-profile-launch`.
- `directLevel100Route=direct-level100-candidate`.
- `directLevel100RouteStatus=candidate-unproven-unarmed`.
- Target executable SHA-256: `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`.
- Backup executable SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
- Target executable bytes: `2506752`.
- Backup executable bytes: `2506752`.
- Patch status: `stable-copied-executable-patched`.
- `stablePatchRows=4`.
- `skipAutoToggleArmed=false`.
- `beProcessesBefore=0`.
- `invalidArgumentRejected=true`.

Command classes:

| Command class | Argument vector | Status | Public preview |
| --- | --- | --- | --- |
| `baseline-copied-profile-launch` | `[]` | `ready-unarmed` | `Start-Process -FilePath "<COPIED_PROFILE>\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>"` |
| `skip-fmv-copied-profile-launch` | `["-skipfmv"]` | `ready-unarmed` | `Start-Process -FilePath "<COPIED_PROFILE>\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>" -ArgumentList "-skipfmv"` |
| `direct-level100-candidate` | `["-skipfmv", "-level", "100"]` | `candidate-unproven-unarmed` | `Start-Process -FilePath "<COPIED_PROFILE>\BEA.exe" -WorkingDirectory "<COPIED_PROFILE>" -ArgumentList "-skipfmv -level 100"` |

The initial launch route selected for a later live proof is `skip-fmv-copied-profile-launch`. The direct Level100 route is documented as `direct-level100-candidate` only; a later runtime proof must explicitly choose it before using `-level 100`.

## Guard Outcomes

The launch-command proof records:

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

No local path is public evidence. Public docs may report sanitized profile id, command classes, command arguments, patch/hash classes, stop conditions, and claim boundary only.

## Level100 Static Anchors Preserved

The launch command remains tied to the same Level100 observation surface:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with `0` missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

## Claims

This slice proves only:

- A copied-profile launch command can be constructed for the patched copied executable through `tools/start_game_profile.ps1 -PrintOnly`.
- The command target class is the copied-profile `BEA.exe`, with the copied-profile root as working-directory class.
- The copied executable and clean backup hashes match the expected patched-copy and clean-retail hash classes.
- Three command classes are documented: baseline, skip-FMV, and direct Level100 candidate.
- Unsupported launch arguments are rejected before launch.
- Launch remains unarmed and stops before process creation.
- The installed game root and original executable remained read-only.

This slice does not prove:

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

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan`. That follow-up must explicitly arm a copied-profile BEA launch, use the selected command route, bound process lifetime, stop/cleanup the process, and still avoid screenshot/native-input/debugger/runtime MissionScript claims unless those are separately selected in a later slice.
