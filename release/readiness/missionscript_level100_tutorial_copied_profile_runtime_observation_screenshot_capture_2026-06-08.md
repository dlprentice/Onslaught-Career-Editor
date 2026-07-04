# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Readiness Note

Status: complete copied-profile screenshot capture proof, not MissionScript/runtime behavior or visual correctness proof
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture`

This readiness note records one bounded still-frame capture from the copied-profile BEA process. It uses `tools/start_game_profile.ps1`, `tools/list_game_windows.ps1`, and `tools/capture_game_window.ps1` against the copied-profile target only. Raw screenshot/frame artifacts remain private and ignored.

Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md`.
Machine-checkable result: `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json`.
Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan`.

Evidence anchors:

- `status=COMPLETE`
- `screenshotCaptureStatus=copied-profile-window-still-frame-captured`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `targetExecutableClass=copied-profile-BEA.exe`
- `workingDirectoryClass=copied-profile-root`
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

Static authority remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, expanded static surface `1560/1560 = 100.00%`, active current-risk focused accounting `1179/1179 = 100.00%`, remaining active focused work `0`, and latest verified Ghidra backup `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Level100 static source-selection anchors remain `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

This proves copied-profile launch/window identification/still-frame capture and cleanup only. It does not prove runtime MissionScript execution, direct Level100 route behavior, runtime command effects, runtime event outcomes, live loose-MSL loading, packed-vs-loose script selection, runtime Level100 mission outcome, runtime objective UI, runtime message or audio output, runtime HUD flashing, runtime object identity, runtime `SpawnThing` behavior, runtime `GetThingRef` behavior, visual correctness, occlusion-free pixel correctness, native input behavior, debugger observation behavior, in-game screenshot command behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.

Follow-up child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan`.
