# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Readiness Note

Status: complete copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke`

This readiness note summarizes the copied-profile launch-window smoke proof. The slice explicitly armed `skip-fmv-copied-profile-launch`, launched the copied-profile `BEA.exe` through `tools/start_game_profile.ps1`, observed bounded process/window metadata, and cleaned up the launched process. It did not capture screenshots or frames, drive native input, attach a debugger, start Godot work, use the direct `-level 100` route, or claim runtime MissionScript behavior.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan`.

Public proof files:

- `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md`
- `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json`
- `tools/missionscript_level100_tutorial_copied_profile_runtime_observation_launch_window_smoke_probe.py`

Static authority remains:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Level100 static source-selection anchors preserved for later runtime observation slices: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

Launch-window smoke summary:

- `status=COMPLETE`
- `launchWindowSmokeStatus=copied-profile-window-smoke-complete`
- `profileId=level100-clean-materialized-20260608-214752`
- `targetExecutableClass=copied-profile-BEA.exe`
- `workingDirectoryClass=copied-profile-root`
- `selectedRoute=skip-fmv-copied-profile-launch`
- `directLevel100Route=direct-level100-candidate`
- `directLevel100RouteStatus=candidate-unproven-unarmed`
- `launchHelper=tools/start_game_profile.ps1`
- `launchHelperSchema=game-launch-process.v1`
- `freshPrintOnlyPreviewChecked=true`
- `launchArmed=true`
- `beLaunch=true`
- `launchCommandExecuted=true`
- `processStarted=true`
- `processAliveAfterDelay=true`
- `mainWindowHandleObserved=true`
- `mainWindowTitleClass=BEA`
- `respondingAfterDelay=true`
- `observationDelaySeconds=8`
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
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `screenshotCapture=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `windowSmokeObservationRows=1`
- `missionScriptRuntimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

What this proves:

- The copied-profile executable launched through `tools/start_game_profile.ps1` with copied-profile working-directory class.
- The selected `skip-fmv-copied-profile-launch` route was explicitly armed and executed.
- A bounded process/window smoke observed a live process, nonzero window handle, `BEA` title class, and responding process state.
- The launched copied-profile process was cleaned up.
- Copied and installed executable hash classes stayed stable.
- The installed game root and original executable remained read-only.

What remains unproven:

- Runtime MissionScript execution.
- Direct Level100 route behavior.
- Runtime command effects or event outcomes.
- Runtime UI, message, audio, HUD, object, spawn, or GetThingRef behavior.
- Screenshot or frame capture proof.
- Visual correctness.
- Native input behavior.
- Debugger observation behavior.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

Next selected child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan`.
