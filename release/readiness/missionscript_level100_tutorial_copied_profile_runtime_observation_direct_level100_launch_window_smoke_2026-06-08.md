# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Window Smoke Readiness Note

Status: complete direct Level100 copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke`

This readiness note records one bounded copied-profile launch-window smoke for the direct `-skipfmv -level 100` route. It uses `tools/start_game_profile.ps1` and `tools/list_game_windows.ps1` against the copied-profile target only. It does not capture a still frame, send native input, attach a debugger, start Godot, or claim MissionScript runtime behavior.

Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md`.
Machine-checkable result: `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json`.
Completed slice token: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan`.
Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan`.

Evidence anchors:

- `status=COMPLETE`
- `directLevel100LaunchWindowSmokeStatus=direct-level100-copied-profile-window-smoke-complete`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `targetExecutableClass=copied-profile-BEA.exe`
- `workingDirectoryClass=copied-profile-root`
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
- `beProcessesBefore=0`
- `beProcessesAfterCleanup=0`
- `targetHashBefore=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- `targetHashAfter=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- `backupHashBefore=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `backupHashAfter=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `targetBytes=2506752`
- `backupBytes=2506752`
- `stablePatchRows=4`
- `skipAutoToggleArmed=false`
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

Static authority remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, expanded static surface `1560/1560 = 100.00%`, active current-risk focused accounting `1179/1179 = 100.00%`, remaining active focused work `0`, and latest verified Ghidra backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Level100 static source-selection anchors remain `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

This proves direct copied-profile launch/window smoke and cleanup only. It does not prove runtime MissionScript execution, Level100 script source selection, runtime command effects, runtime event outcomes, live loose-MSL loading, packed-vs-loose script selection, runtime Level100 mission outcome, runtime objective UI, runtime message or audio output, runtime HUD flashing, runtime object identity, runtime `SpawnThing` behavior, runtime `GetThingRef` behavior, screenshot/frame capture for the direct Level100 route, visual correctness, native input behavior, debugger observation behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.

Follow-up child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan`.
