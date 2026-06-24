# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof

Status: complete copied-profile screenshot capture proof, not MissionScript/runtime behavior or visual correctness proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md`

This slice performs the first bounded still-frame capture in the Level100 copied-profile observation lane. It uses the previously patched copied-profile executable, explicitly arms the selected `skip-fmv-copied-profile-launch` route, launches through `tools/start_game_profile.ps1`, resolves exactly one visible `BEA` top-level window with `tools/list_game_windows.ps1`, captures one still frame with `tools/capture_game_window.ps1`, then closes only the launched copied-profile process. It does not publish the raw PNG, drive native input, attach a debugger, use the direct `-level 100` route, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This screenshot capture proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Capture Result

Private lifecycle evidence exists under the ignored artifact-root class. Public docs expose only sanitized counts/classes, dimensions, route ids, hashes for executable stability, and stop conditions:

- `status=COMPLETE`
- `screenshotCaptureStatus=copied-profile-window-still-frame-captured`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `targetExecutableClass=copied-profile-BEA.exe`
- `workingDirectoryClass=copied-profile-root`
- `targetHashBefore=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- `targetHashAfter=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- `backupHashBefore=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `backupHashAfter=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `targetBytes=2506752`
- `backupBytes=2506752`
- `patchStatus=stable-copied-executable-patched`
- `stablePatchRows=4`
- `skipAutoToggleArmed=false`
- `selectedRoute=skip-fmv-copied-profile-launch`
- `directLevel100Route=direct-level100-candidate`
- `directLevel100RouteStatus=candidate-unproven-unarmed`
- `launchHelper=tools/start_game_profile.ps1`
- `launchHelperSchema=game-launch-process.v1`
- `windowScanHelper=tools/list_game_windows.ps1`
- `windowScanHelperSchema=game-window-scan-helper.v1`
- `captureHelper=tools/capture_game_window.ps1`
- `captureHelperSchema=game-window-capture-helper.v1`
- `freshPrintOnlyPreviewChecked=true`
- `launchArmed=true`
- `beLaunch=true`
- `launchCommandExecuted=true`
- `processStarted=true`
- `processPathClass=copied-profile-BEA.exe`
- `beProcessesBefore=0`
- `processAliveAfterDelay=true`
- `observationDelaySeconds=10`
- `windowCandidateCount=1`
- `exactPidHwndWindowMatch=true`
- `mainWindowHandleObserved=true`
- `mainWindowTitleClass=BEA`
- `windowVisible=true`
- `windowNotMinimized=true`
- `captureFrameCount=1`
- `captureStatus=captured`
- `captureWidth=656`
- `captureHeight=539`
- `captureArtifactClass=private-still-frame-png`
- `captureArtifactBytesRecordedPrivately=true`
- `captureArtifactHashRecordedPrivately=true`
- `captureArtifactPublished=false`
- `respondingAfterDelay=true`
- `boundedProcessLifetime=true`
- `cleanupMethod=CloseMainWindow`
- `processCleanup=PASS`
- `processAliveAfterCleanup=false`
- `beProcessesAfterCleanup=0`
- `copiedTargetHashStableDuringCapture=true`
- `copiedBackupHashStableDuringCapture=true`
- `installedTargetHashStableDuringCapture=true`
- `installedBackupHashStableDuringCapture=true`
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `windowSmokeObservationRows=1`
- `screenshotCaptureEvidenceRows=1`
- `missionScriptRuntimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

The direct Level100 command route remains `direct-level100-candidate` and `candidate-unproven-unarmed`. This capture proof intentionally uses only the selected `skip-fmv-copied-profile-launch` route.

## Level100 Static Anchors Preserved

The capture proof remains tied to the same Level100 observation surface:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with `0` missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

## Claims

This slice proves only:

- The copied-profile `BEA.exe` can be launched through `tools/start_game_profile.ps1` from the copied-profile working-directory class.
- The selected `skip-fmv-copied-profile-launch` route was explicitly armed and executed.
- `tools/list_game_windows.ps1` found exactly one visible `BEA` top-level window for the launched process.
- `tools/capture_game_window.ps1` captured one bounded still frame from the exact process/window pair.
- The raw still-frame PNG remained private under the ignored artifact-root class.
- The launched copied-profile process was cleaned up with `CloseMainWindow`.
- Copied target, copied clean backup, installed target, and installed clean backup hashes stayed stable during the capture.
- The installed game root and original executable remained read-only.

This slice does not prove:

- Runtime MissionScript execution.
- Direct Level100 route behavior.
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
- Visual correctness.
- Occlusion-free pixel correctness.
- Native input behavior.
- Debugger observation behavior.
- In-game screenshot command behavior.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan`. That follow-up must separately arm the direct `-skipfmv -level 100` route if selected, keep the copied-profile process bounded, and still avoid native input, debugger attachment, runtime MissionScript claims, Godot, rebuild parity, and no-noticeable-difference parity unless those are separately selected in later slices.
