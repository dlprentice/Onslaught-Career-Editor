# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Window Smoke Proof

Status: complete direct Level100 copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md`
Completed slice token: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan`

This slice explicitly arms the previously candidate direct `-skipfmv -level 100` route in the copied-profile Level100 observation lane. It launches only the copied-profile executable through `tools/start_game_profile.ps1`, observes a bounded process/window state with `tools/list_game_windows.ps1`, then closes only the launched copied-profile process. It does not capture a still frame, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This direct Level100 launch-window smoke proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Smoke Result

Private lifecycle evidence exists under the ignored artifact-root class. Public docs expose only sanitized counts/classes, hashes, route ids, helper schemas, and stop conditions:

- `status=COMPLETE`
- `directLevel100LaunchWindowSmokeStatus=direct-level100-copied-profile-window-smoke-complete`
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
- `directLevel100RouteStatus=window-smoke-complete-no-missionscript-proof`
- `launchHelper=tools/start_game_profile.ps1`
- `launchHelperSchema=game-launch-process.v1`
- `windowScanHelper=tools/list_game_windows.ps1`
- `windowScanHelperSchema=game-window-scan-helper.v1`
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
- `exactPidWindowCount=1`
- `mainWindowHandleObserved=true`
- `mainWindowTitleClass=BEA`
- `windowVisible=true`
- `windowNotMinimized=true`
- `screenshotCapture=false`
- `captureFrameCount=0`
- `boundedProcessLifetime=true`
- `cleanupMethod=CloseMainWindow`
- `processCleanup=PASS`
- `processAliveAfterCleanup=false`
- `beProcessesAfterCleanup=0`
- `copiedTargetHashStableDuringSmoke=true`
- `copiedBackupHashStableDuringSmoke=true`
- `installedTargetHashStableDuringSmoke=true`
- `installedBackupHashStableDuringSmoke=true`
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `windowSmokeObservationRows=1`
- `missionScriptRuntimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

During this slice the window helper PowerShell compatibility defect was corrected by renaming its local `$isWindows` variable to `$runningOnWindows`; PowerShell variable names are case-insensitive, so the old local name collided with the read-only automatic `$IsWindows` variable in this profile. The same narrow variable rename was applied to `tools/capture_game_window.ps1` so future capture slices use the same compatibility-safe helper pattern.

## Level100 Static Anchors Preserved

The direct launch smoke remains tied to the same Level100 observation surface:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with `0` missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

## Claims

This slice proves only:

- The direct `-skipfmv -level 100` copied-profile launch route was explicitly armed and executed through `tools/start_game_profile.ps1`.
- The copied-profile process stayed alive and responding after a bounded delay.
- `tools/list_game_windows.ps1` found exactly one visible non-minimized `BEA` top-level window for the launched process.
- The launched copied-profile process was cleaned up with `CloseMainWindow`.
- Copied target, copied clean backup, installed target, and installed clean backup hashes stayed stable during the smoke.
- The installed game root and original executable remained read-only.

This slice does not prove:

- Runtime MissionScript execution.
- Level100 script source selection.
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
- Screenshot or frame capture for the direct Level100 route.
- Visual correctness.
- Native input behavior.
- Debugger observation behavior.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan`. That follow-up must separately arm still-frame capture for the direct `-skipfmv -level 100` route if selected, keep the copied-profile process bounded, keep raw screenshots private, and still avoid native input, debugger attachment, runtime MissionScript claims, Godot, rebuild parity, and no-noticeable-difference parity unless those are separately selected in later slices.
