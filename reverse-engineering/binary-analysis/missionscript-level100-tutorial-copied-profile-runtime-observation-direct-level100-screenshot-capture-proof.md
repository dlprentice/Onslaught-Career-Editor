# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof

Status: complete direct Level100 copied-profile screenshot capture proof, not MissionScript/runtime behavior or visual correctness proof
Last updated: 2026-06-09
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md`
Completed slice token: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan`

This slice explicitly arms the direct `-skipfmv -level 100` route in the copied-profile Level100 observation lane and captures one private still frame from the exact launched process/window pair. It launches only the copied-profile executable through `tools/start_game_profile.ps1`, resolves the bounded window state with `tools/list_game_windows.ps1`, captures one frame with `tools/capture_game_window.ps1`, then closes only the launched copied-profile process. It does not publish the raw PNG, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This direct Level100 screenshot capture proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Capture Result

Private lifecycle and screenshot evidence exists under the ignored artifact-root class. Public docs expose only sanitized counts/classes, dimensions, route ids, hashes for executable stability, and stop conditions:

- `status=COMPLETE`
- `directLevel100ScreenshotCaptureStatus=direct-level100-copied-profile-window-still-frame-captured`
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
- `selectedRoute=direct-level100-candidate`
- `launchArguments=-skipfmv -level 100`
- `directLevel100Route=direct-level100-candidate`
- `directLevel100RouteStatus=still-frame-captured-no-missionscript-proof`
- `launchHelper=tools/start_game_profile.ps1`
- `launchHelperSchema=game-launch-process.v1`
- `windowScanHelper=tools/list_game_windows.ps1`
- `windowScanHelperSchema=game-window-scan-helper.v1`
- `captureHelper=tools/capture_game_window.ps1`
- `captureHelperSchema=game-window-capture-helper.v1`
- `windowHelperPowerShellCompatibilityFix=runningOnWindows-local-variable`
- `freshPrintOnlyPreviewChecked=true`
- `launchArmed=true`
- `beLaunch=true`
- `launchCommandExecuted=true`
- `processStarted=true`
- `processPathClass=copied-profile-BEA.exe`
- `beProcessesBefore=0`
- `processAliveAfterDelay=true`
- `respondingAfterDelay=true`
- `observationDelaySeconds=15`
- `windowScanStatus=ready`
- `windowCandidateCount=1`
- `exactProcessWindowCount=1`
- `exactProcessWindowMatch=true`
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
- `captureOutputPathClass=short-private-output-path`
- `pathLengthMitigation=short-private-output-path-used-after-gdi-plus-long-path-save-failure`
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

The raw still-frame PNG path, hash, and byte count are recorded only in private ignored evidence and are not published.

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

- The direct `-skipfmv -level 100` copied-profile launch route can be explicitly armed and executed through `tools/start_game_profile.ps1`.
- The copied-profile process stayed alive and responding after a bounded delay.
- `tools/list_game_windows.ps1` found exactly one visible, non-minimized `BEA` top-level window for the launched process.
- `tools/capture_game_window.ps1` captured one bounded still frame from the exact direct-route process/window pair.
- The raw still-frame PNG remained private under the ignored artifact-root class.
- The launched copied-profile process was cleaned up with `CloseMainWindow`.
- Copied target, copied clean backup, installed target, and installed clean backup hashes stayed stable during capture.
- The installed game root and original executable remained read-only.

This slice does not prove runtime MissionScript execution, Level100 script source selection, runtime command effects, event outcomes, live loose-MSL loading, packed-vs-loose script selection, runtime Level100 mission outcome, runtime objective UI, runtime message/audio output, runtime HUD flashing, runtime object identity, `SpawnThing`, `GetThingRef`, visual correctness, occlusion-free pixel correctness, native input, debugger observation, in-game screenshot command behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.

Follow-up child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan`.
