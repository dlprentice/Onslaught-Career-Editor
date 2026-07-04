# Private runtime evidence: Game Harness proof

Status: private evidence, sanitized
Date: 2026-04-29
Runtime: Electron desktop dev mode
Branch: `wip/sandbox`
Source/proof base commit: `e2e90e56ca688790dc4ce87f71580d1ee53ffff2`
Evidence-report commit: `e9940ebabd9fb03bd3f623d0eba94fbb53012206`

## Scope

Prompt 6 proved the real Game Harness copied-profile loop against a disposable app-owned profile. It did not start Prompt 7 and did not implement an open-ended agentic loop.

The final accepted run used Electron desktop IPC/job boundaries, not the browser fixture lane and not the CLI-only lane. The renderer/preload requested typed jobs; native filesystem, patching, launch, capture, input, and process stop work stayed behind the Electron main/job-runner boundary.

## Local artifact root

- Artifact root: `[maintainer-local-appdata]`
- Local ignored proof JSON: `[maintainer-private-checkout]\subagents\2026-04-29-prompt6-game-harness-proof.json`
- Local ignored UI screenshot: `[maintainer-private-checkout]\subagents\2026-04-29-prompt6-game-harness-ui.png` (`130046` bytes)
- Raw frame PNGs stay under `[maintainer-local-appdata]\artifacts\game-window-frame-capture\...` and are not committed.

## Commands run

- `git status --short --branch`
- `git rev-parse HEAD`
- `Get-Process -Name BEA -ErrorAction SilentlyContinue | Select-Object -Property Id,ProcessName,Path`
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -Sequence tap:F12 -PrintOnly`
- `node subagents/2026-04-29-prompt6-game-harness-proof.cjs`

Earlier Prompt 6 proof attempts exposed two scoped-input helper issues before the final accepted run: one-item PowerShell collection unwrapping and Windows foreground-focus denial. Each failed attempt still stopped the managed BEA process and ended with zero running BEA processes. The final accepted run used the fixed helper behavior.

## Source profile and original executable

- Source game root: `[maintainer-private-checkout]\game`
- Source executable: `[maintainer-private-checkout]\game\BEA.exe`
- Source SHA-256 before: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Source SHA-256 after: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Source remained known clean Steam retail: yes
- Source remained unchanged: yes

No repo-local `game\BEA.exe`, installed Steam executable, or real user profile was patched.

## Copied profile

- Job: `game.prepareSafeProfile`
- Run ID: `job-20260429192034435-game-prepareSafeProfile-d9ef94`
- Target copied profile: `[maintainer-local-appdata]\game-profiles\bea-safe-profile-prompt6-1777490434419`
- Source game root: `[maintainer-private-checkout]\game`
- Entries copied: `9`
- Artifact: `[maintainer-local-appdata]\artifacts\game-profile-prepare\job-20260429192034435-game-prepareSafeProfile-d9ef94\prepare.json`

## Copied executable and patch

- Copied executable: `[maintainer-local-appdata]\game-profiles\bea-safe-profile-prompt6-1777490434419\BEA.exe`
- Copied executable SHA-256 before patch: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Copied executable SHA-256 after patch: `e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`
- Patch job: `patch.applyCatalogPatch`
- Patch run ID: `job-20260429192042619-patch-applyCatalogPatch-dec561`
- Patch ID: `force_windowed`
- Applied rows: `1`
- Already applied rows: `0`
- Changed: yes
- Read-back verified: yes
- Known Steam hash before: yes
- Known Steam hash after: no
- Backup path: `[maintainer-local-appdata]\game-profiles\bea-safe-profile-prompt6-1777490434419\BEA.exe.original.backup`
- Artifact: `[maintainer-local-appdata]\artifacts\patch-apply\job-20260429192042619-patch-applyCatalogPatch-dec561\apply.json`

Only catalog patch id `force_windowed` was applied, and only to the copied executable.

## Managed launch

- Job: `game.launchProfile`
- Run ID: `job-20260429192043099-game-launchProfile-d214b0`
- Process ID: `46044`
- Executable: `[maintainer-local-appdata]\game-profiles\bea-safe-profile-prompt6-1777490434419\BEA.exe`
- Working directory: `[maintainer-local-appdata]\game-profiles\bea-safe-profile-prompt6-1777490434419`
- Arguments: none
- Artifact: `[maintainer-local-appdata]\artifacts\game-launch\job-20260429192043099-game-launchProfile-d214b0\launch.json`

## Capture plan

- Job: `game.planWindowCapture`
- Run ID: `job-20260429192047401-game-planWindowCapture-632a02`
- Status: ready
- Candidates: `1`
- Selected window: `BEA`
- Window handle: `0x6A0CEC`
- Capture source hint: `window:46044:0x6A0CEC`
- Artifact: `[maintainer-local-appdata]\artifacts\game-window-capture-plan\job-20260429192047401-game-planWindowCapture-632a02\plan.json`

## Frame capture 1

- Job: `game.captureWindowFrame`
- Run ID: `job-20260429192049382-game-captureWindowFrame-e7e261`
- Status: captured
- PNG path: `[maintainer-local-appdata]\artifacts\game-window-frame-capture\job-20260429192049382-game-captureWindowFrame-e7e261\frame.png`
- Dimensions: `655x540`
- Size: `5552` bytes
- MIME: `image/png`
- SHA-256: `1dc763c866935b0b0f3902a851c4c452ca07bdca87cf8284289b8b7850de924e`
- Captured at: `2026-04-29T19:20:52.248Z`
- Artifact: `[maintainer-local-appdata]\artifacts\game-window-frame-capture\job-20260429192049382-game-captureWindowFrame-e7e261\frame.json`

## Bounded input

- Plan job: `game.planWindowInput`
- Plan run ID: `job-20260429192052375-game-planWindowInput-a92a7b`
- Send job: `game.sendWindowInput`
- Send run ID: `job-20260429192054198-game-sendWindowInput-9db0ab`
- Planned sequence: `tap:F12`
- Step delay: `80` ms
- Plan status: ready
- Send status: sent
- Window handle: `0x6A0CEC`
- Actions: `1`
- Key events/messages sent: `2`
- Focused: no
- Plan artifact: `[maintainer-local-appdata]\artifacts\game-window-input-plan\job-20260429192052375-game-planWindowInput-a92a7b\plan.json`
- Send artifact: `[maintainer-local-appdata]\artifacts\game-window-input\job-20260429192054198-game-sendWindowInput-9db0ab\input.json`
- Send note: Windows denied foreground focus handoff, so the helper sent bounded key messages directly to the selected managed `BEA.exe` top-level window handle instead of using unscoped global key events.

This proves a bounded target-window input send through the typed job boundary. It does not prove the game consumed the input through foreground DirectInput, and the captured frames were visually unchanged.

## Frame capture 2

- Job: `game.captureWindowFrame`
- Run ID: `job-20260429192057663-game-captureWindowFrame-45422b`
- Status: captured
- PNG path: `[maintainer-local-appdata]\artifacts\game-window-frame-capture\job-20260429192057663-game-captureWindowFrame-45422b\frame.png`
- Dimensions: `655x540`
- Size: `5552` bytes
- MIME: `image/png`
- SHA-256: `1dc763c866935b0b0f3902a851c4c452ca07bdca87cf8284289b8b7850de924e`
- Captured at: `2026-04-29T19:21:00.464Z`
- Artifact: `[maintainer-local-appdata]\artifacts\game-window-frame-capture\job-20260429192057663-game-captureWindowFrame-45422b\frame.json`

The second frame has a later timestamp and distinct artifact path from the first frame. The PNG hash is the same as the first frame, so this proof is observe-input-observe at the harness/artifact level, not visual gameplay-state-change proof.

## Stop and registry confirmation

- Stop job: `runtime.stopManagedProcess`
- Stop run ID: `job-20260429192100587-runtime-stopManagedProcess-3eaac7`
- Target launch run ID: `job-20260429192043099-game-launchProfile-d214b0`
- Process ID: `46044`
- Previous status: running
- Current status: exited
- Stop requested: yes
- Stop artifact: `[maintainer-local-appdata]\artifacts\managed-process-stop\job-20260429192100587-runtime-stopManagedProcess-3eaac7\stop.json`
- Registry job: `runtime.listManagedProcesses`
- Registry run ID: `job-20260429192102748-runtime-listManagedProcesses-835710`
- Managed process records: `4`
- Running records after stop: `0`
- Exited records after stop: `4`
- Latest record: `game PID 46044 (exited)`
- Registry artifact: `[maintainer-local-appdata]\artifacts\managed-process-registry\job-20260429192102748-runtime-listManagedProcesses-835710\processes.json`

Post-run `Get-Process -Name BEA` returned no process rows.

## All final accepted job IDs

- `game.prepareSafeProfile`: `job-20260429192034435-game-prepareSafeProfile-d9ef94`
- `patch.applyCatalogPatch`: `job-20260429192042619-patch-applyCatalogPatch-dec561`
- `game.launchProfile`: `job-20260429192043099-game-launchProfile-d214b0`
- `game.planWindowCapture`: `job-20260429192047401-game-planWindowCapture-632a02`
- `game.captureWindowFrame`: `job-20260429192049382-game-captureWindowFrame-e7e261`
- `game.planWindowInput`: `job-20260429192052375-game-planWindowInput-a92a7b`
- `game.sendWindowInput`: `job-20260429192054198-game-sendWindowInput-9db0ab`
- `game.captureWindowFrame`: `job-20260429192057663-game-captureWindowFrame-45422b`
- `runtime.stopManagedProcess`: `job-20260429192100587-runtime-stopManagedProcess-3eaac7`
- `runtime.listManagedProcesses`: `job-20260429192102748-runtime-listManagedProcesses-835710`

## What is proven

- A copied profile was created outside the repo under the app artifact root.
- The copied `BEA.exe` was patched with `force_windowed`; the repo-local source executable stayed unchanged.
- The copied profile launched as a managed `BEA.exe` process.
- Window capture planning found one visible managed BEA window.
- A first bounded PNG frame artifact was captured.
- A bounded input action was planned before send.
- A bounded input action was sent to the selected managed BEA window handle through the typed job boundary.
- A second bounded PNG frame artifact was captured after the send.
- The managed process was stopped, and the managed registry reported zero running BEA processes.

## What is not proven

- Packaged portable-bundle Game Harness runtime behavior is not separately proven.
- Continuous frame streaming is not implemented or proven.
- Foreground-focused `keybd_event` delivery was not proven; Windows denied foreground handoff, so the final send used target-window key messages.
- Gameplay reaction to the input was not proven; the two captured frame PNGs have the same hash.
- No Prompt 7 agentic loop, autonomous observe-act policy, debugger automation, or Ghidra/runtime mutation was started.

## Privacy and release posture

This report is sanitized and does not embed raw frame PNGs, screenshots, data URLs, or base64 payloads. The raw local proof JSON, UI screenshot, and frame PNGs can contain private game asset evidence and remain private/ignored. The `release/readiness/private_runtime_evidence/**` path is excluded from the public curated release manifest.

## Prompt 6.1 safety addendum

Prompt 6 proof remains valid. After review, the direct `tools/send_game_window_input.ps1` helper was hardened for defense in depth: any non-PrintOnly send now requires both `ProcessId > 0` and a non-empty `HwndHex`. If either exact target identifier is missing, the helper returns a safe `game-window-input.v1` payload with `status=target-required`, `plannedOnly=true`, `mutation=false`, and the parsed `actions` preserved as an array, then exits `0` without enumerating/sending input.

The typed job-runner managed-target path remains the intended runtime input boundary. This addendum only prevents a direct helper invocation from sending to "the only visible BEA window" without an exact process/window target.

## Verification commands

- `node subagents/2026-04-29-prompt6-game-harness-proof.cjs`: PASS on final accepted run; acceptance booleans all true.
- `Get-Process -Name BEA -ErrorAction SilentlyContinue | Select-Object -Property Id,ProcessName,Path`: PASS; no process rows after final stop.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -Sequence tap:F12 -PrintOnly`: PASS; returned `game-window-input.v1`, `status=no-window`, `actionCount=1`, and preserved `actions` as an array.
- `npm run typecheck`: PASS.
- `npm run test:renderer-smoke`: PASS; renderer smoke result `{"ok":true,"failures":[]}`. Vite emitted the existing chunk-size warning.
- `npm run test:electron-parity`: PASS; Electron parity passed across 13 save/options fixtures and the `game\BEA.exe` executable fixture.
- `npm run test:bundle-policy`: PASS.
- `py -3 tools\release_curated_manifest.py --check`: PASS.
- `node -e "<parse developer_agent_state.json, documentation_agent_state.json, subagents/2026-04-29-prompt6-game-harness-proof.json>"`: PASS.
- `git diff --check`: PASS; only Git's normal LF-to-CRLF warning for `tools/send_game_window_input.ps1` was printed, with exit code 0.

## Prompt 6.1 verification commands

- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -Sequence tap:F12 -PrintOnly`: PASS; returned `game-window-input.v1`, `plannedOnly=true`, `actionCount=1`, and `actions` as an array.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -Sequence tap:F12`: PASS; returned `status=target-required`, `plannedOnly=true`, `mutation=false`, `actionCount=1`, and `actions` as an array. No input was sent.
- `powershell.exe -NoProfile -ExecutionPolicy Bypass -File tools/send_game_window_input.ps1 -Sequence tap:INVALIDKEY`: PASS; invalid key still exits nonzero with the existing safe error path.
- Focused Node helper validation: PASS; parsed PrintOnly, target-required, and invalid-key cases and verified one-item `actions` arrays.
- `npm run typecheck`: PASS.
- `npm run test:renderer-smoke`: PASS; renderer smoke result `{"ok":true,"failures":[]}`. Vite emitted the existing chunk-size warning.
- `npm run test:electron-parity`: PASS; Electron parity passed across 13 save/options fixtures and the `game\BEA.exe` executable fixture.
- `py -3 tools\release_curated_manifest.py --check`: PASS.
- `node -e "<parse developer_agent_state.json, documentation_agent_state.json>"`: PASS.
- `git diff --check`: PASS; only Git's normal LF-to-CRLF warnings were printed, with exit code 0.
