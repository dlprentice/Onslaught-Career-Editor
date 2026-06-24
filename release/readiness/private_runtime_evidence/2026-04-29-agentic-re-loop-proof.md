# Private runtime evidence: bounded agentic RE loop proof

Status: private evidence, sanitized
Date: 2026-04-29 local Prompt 7 session; artifact timestamps below are UTC `2026-04-30`
Runtime: Electron desktop dev mode
Branch: `wip/sandbox`
Source/proof base commit: `6817fbee979ef8f0e0178c84e44ae9cd7a119250`
Evidence-report commit: `e485121b599a095c31950003d3547fd918aac2e0`

## Scope

Prompt 7 proved one bounded agentic reverse-engineering loop:

```text
observe -> decide -> act -> observe -> record -> stop
```

This was a runtime proof, not an open-ended autonomy feature. The final accepted run used the Electron desktop renderer and typed workbench job boundary. Native filesystem copy, executable patching, launch, window capture, scoped input, and process stop work stayed behind Electron main/job-runner cases. The renderer never received raw Node, shell, desktop capture, raw input, or filesystem privileges.

## Local artifact root

- Artifact root: `C:\Users\david\AppData\Roaming\Electron`
- Local ignored proof JSON: `C:\Users\david\source\Onslaught-Career-Editor-private\subagents\2026-04-29-prompt7-agentic-re-loop-proof.json`
- Raw frame PNGs stay under `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-frame-capture\...` and are not committed.
- No raw screenshots, frame PNGs, data URLs, base64 payloads, or private proof JSON are committed.

## Commands run for runtime proof

- `git status --short --branch`
- `git rev-parse HEAD`
- `Get-Process -Name BEA -ErrorAction SilentlyContinue | Select-Object -Property Id,ProcessName,Path`
- `node subagents/2026-04-29-prompt7-agentic-re-loop-proof.cjs`
- `Get-Process -Name BEA -ErrorAction SilentlyContinue | Select-Object -Property Id,ProcessName,Path`

The final pre-run and post-run `Get-Process` checks returned no process rows.

## Source profile and original executable

- Source game root: `C:\Users\david\source\Onslaught-Career-Editor-private\game`
- Source executable: `C:\Users\david\source\Onslaught-Career-Editor-private\game\BEA.exe`
- Source SHA-256 before: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Source verified before: `2026-04-30T00:38:15.258Z`
- Source SHA-256 after: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Source verified after: `2026-04-30T00:38:42.051Z`
- Source stayed known clean Steam retail: yes
- Source stayed unchanged: yes

No repo-local `game\BEA.exe`, installed Steam executable, or real user profile was patched.

## Copied profile

- Job: `game.prepareSafeProfile`
- Run ID: `job-20260430003815267-game-prepareSafeProfile-394e12`
- Target copied profile: `C:\Users\david\AppData\Roaming\Electron\game-profiles\bea-agentic-loop-prompt7-1777509493363`
- Source game root: `C:\Users\david\source\Onslaught-Career-Editor-private\game`
- Entries copied: `9`
- Artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-profile-prepare\job-20260430003815267-game-prepareSafeProfile-394e12\prepare.json`

## Copied executable and patch

- Copied executable: `C:\Users\david\AppData\Roaming\Electron\game-profiles\bea-agentic-loop-prompt7-1777509493363\BEA.exe`
- Copied executable SHA-256 before patch: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Copied executable SHA-256 after patch: `e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`
- Patch job: `patch.applyCatalogPatch`
- Patch run ID: `job-20260430003822524-patch-applyCatalogPatch-23878a`
- Patch ID: `force_windowed`
- Applied rows: `1`
- Already applied rows: `0`
- Changed: yes
- Read-back verified: yes
- Known Steam hash before: yes
- Known Steam hash after: no
- Post-patch catalog counts: original `6`, patched `1`, mismatch `0`, out-of-range `0`
- Backup path: `C:\Users\david\AppData\Roaming\Electron\game-profiles\bea-agentic-loop-prompt7-1777509493363\BEA.exe.original.backup`
- Artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\patch-apply\job-20260430003822524-patch-applyCatalogPatch-23878a\apply.json`

Only catalog patch id `force_windowed` was applied, and only to the copied executable.

## Managed launch

- Job: `game.launchProfile`
- Run ID: `job-20260430003823033-game-launchProfile-7e8819`
- Process ID: `22372`
- Executable: `C:\Users\david\AppData\Roaming\Electron\game-profiles\bea-agentic-loop-prompt7-1777509493363\BEA.exe`
- Working directory: `C:\Users\david\AppData\Roaming\Electron\game-profiles\bea-agentic-loop-prompt7-1777509493363`
- Arguments: none
- Artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-launch\job-20260430003823033-game-launchProfile-7e8819\launch.json`

## Observe 1

- Capture-plan job: `game.planWindowCapture`
- Capture-plan run ID: `job-20260430003827344-game-planWindowCapture-c94aea`
- Capture-plan status: ready
- Selected window: `BEA`
- Process ID: `22372`
- Window handle: `0x840D28`

Frame 1:

- Job: `game.captureWindowFrame`
- Run ID: `job-20260430003829274-game-captureWindowFrame-047546`
- Status: captured
- PNG path: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-frame-capture\job-20260430003829274-game-captureWindowFrame-047546\frame.png`
- Dimensions: `655x540`
- Size: `293152` bytes
- MIME: `image/png`
- SHA-256: `311119dd61e1458ff6cc4d32889d7643241150121ab74cdba11255856a7fc2d7`
- Captured at: `2026-04-30T00:38:31.723Z`
- Artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-frame-capture\job-20260430003829274-game-captureWindowFrame-047546\frame.json`

## Decide

Decision schema: `agentic-decision.v1`

Decision policy: `prompt7-one-step-low-risk-probe.v1`

Rules:

- If frame 1 status is captured, dimensions are nonzero, and the managed BEA window has exact ProcessId and HwndHex, choose `tap:F12`.
- Otherwise choose `stop` and do not send input.

Available observations:

- Frame status: captured
- Frame size: `655x540`
- Capture-plan status: ready
- Process ID: `22372`
- Window handle: `0x840D28`

Selected action: `tap:F12`

Reason: frame 1 was captured with nonzero dimensions and exact managed `ProcessId`/`HwndHex`, so `tap:F12` was the lowest-risk one-step probe action.

Rejected alternatives:

- `tap:ENTER`
- `tap:ESCAPE`
- continuous frame stream
- multi-step gameplay input
- debugger/Ghidra mutation

## Act

- Input-plan job: `game.planWindowInput`
- Input-plan run ID: `job-20260430003832021-game-planWindowInput-8a777c`
- Input-send job: `game.sendWindowInput`
- Input-send run ID: `job-20260430003833846-game-sendWindowInput-483f9f`
- Exact target process ID: `22372`
- Exact target window handle: `0x840D28`
- Planned sequence: `tap:F12`
- Step delay: `80` ms
- Plan status: ready
- Send status: sent
- Action count: `1`
- Key events/messages sent: `2`
- Focused: yes
- Plan artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-input-plan\job-20260430003832021-game-planWindowInput-8a777c\plan.json`
- Send artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-input\job-20260430003833846-game-sendWindowInput-483f9f\input.json`
- Send note: focused the selected `BEA.exe` top-level window, then sent bounded keyboard input.

The action was sent only after a plan and only to the managed `game.launchProfile` target with exact `ProcessId` and `HwndHex`.

## Observe 2

- Job: `game.captureWindowFrame`
- Run ID: `job-20260430003836772-game-captureWindowFrame-e9f917`
- Status: captured
- PNG path: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-frame-capture\job-20260430003836772-game-captureWindowFrame-e9f917\frame.png`
- Dimensions: `655x540`
- Size: `236799` bytes
- MIME: `image/png`
- SHA-256: `b5908068133e819f2f53a56a8dd3ce8f485321bcea06db4af0705cc0d49283de`
- Captured at: `2026-04-30T00:38:39.210Z`
- Artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\game-window-frame-capture\job-20260430003836772-game-captureWindowFrame-e9f917\frame.json`

Frame 2 has a later timestamp, a distinct artifact path, a different byte size, and a different hash from frame 1. This still does not claim semantic gameplay reaction; no gameplay-state classifier or human-labeled state assertion was part of this proof.

## Stop and registry confirmation

- Stop job: `runtime.stopManagedProcess`
- Stop run ID: `job-20260430003839488-runtime-stopManagedProcess-abaa19`
- Target launch run ID: `job-20260430003823033-game-launchProfile-7e8819`
- Process ID: `22372`
- Previous status: running
- Current status: exited
- Stop requested: yes
- Stop artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\managed-process-stop\job-20260430003839488-runtime-stopManagedProcess-abaa19\stop.json`
- Registry job: `runtime.listManagedProcesses`
- Registry run ID: `job-20260430003841815-runtime-listManagedProcesses-205f70`
- Managed process records: `6`
- Running records after stop: `0`
- Exited records after stop: `6`
- Latest record: `game PID 22372 (exited)`
- Registry artifact: `C:\Users\david\AppData\Roaming\Electron\artifacts\managed-process-registry\job-20260430003841815-runtime-listManagedProcesses-205f70\processes.json`

Post-run `Get-Process -Name BEA` returned no process rows. The local proof JSON records `rows: []`.

## All final accepted job IDs

- `game.prepareSafeProfile`: `job-20260430003815267-game-prepareSafeProfile-394e12`
- `patch.applyCatalogPatch`: `job-20260430003822524-patch-applyCatalogPatch-23878a`
- `game.launchProfile`: `job-20260430003823033-game-launchProfile-7e8819`
- `game.planWindowCapture`: `job-20260430003827344-game-planWindowCapture-c94aea`
- `game.captureWindowFrame`: `job-20260430003829274-game-captureWindowFrame-047546`
- `game.planWindowInput`: `job-20260430003832021-game-planWindowInput-8a777c`
- `game.sendWindowInput`: `job-20260430003833846-game-sendWindowInput-483f9f`
- `game.captureWindowFrame`: `job-20260430003836772-game-captureWindowFrame-e9f917`
- `runtime.stopManagedProcess`: `job-20260430003839488-runtime-stopManagedProcess-abaa19`
- `runtime.listManagedProcesses`: `job-20260430003841815-runtime-listManagedProcesses-205f70`

## What is proven

- A copied profile was created outside the repo under the app artifact root.
- The copied `BEA.exe` was patched with `force_windowed`; the repo-local source executable stayed unchanged.
- The copied profile launched as a managed `BEA.exe` process.
- The Electron renderer reached the Game Harness UI surface and used the typed workbench job boundary.
- Observation 1 captured a bounded PNG frame artifact.
- A rule-based decision record selected exactly one bounded next action.
- A bounded input action was planned before send.
- A bounded input action was sent only to the exact managed `ProcessId`/`HwndHex` target.
- Observation 2 captured a second bounded PNG frame artifact.
- The managed process was stopped, the registry reported zero running managed BEA processes, and `Get-Process -Name BEA` returned no rows.

This proves a bounded agentic observe/decide/act/observe/stop loop through typed workbench boundaries.

## What is not proven

- This does not prove open-ended autonomy.
- This does not prove continuous frame streaming.
- This does not prove gameplay semantic reaction if frame hashes are unchanged. In this accepted run the hashes differed, but semantic gameplay reaction is still not claimed because no semantic state classifier or human gameplay assertion was part of the proof.
- This does not prove foreground DirectInput if Windows focus is denied and target-window messages are used. In this accepted run Windows focus succeeded and the helper used focused bounded keyboard input.
- This does not prove packaged portable-bundle runtime behavior.
- This does not prove multi-step gameplay progression, debugger automation, Ghidra/runtime mutation, or continuous agent control.

## Privacy and release posture

This report is sanitized and does not embed raw frame PNGs, screenshots, data URLs, or base64 payloads. The raw local proof JSON and frame PNGs can contain private game asset evidence and remain private/ignored. The `release/readiness/private_runtime_evidence/**` path is excluded from the public curated release manifest.

## Verification commands

- `node subagents/2026-04-29-prompt7-agentic-re-loop-proof.cjs`: PASS on final accepted run; acceptance booleans all true.
- `Get-Process -Name BEA -ErrorAction SilentlyContinue | Select-Object -Property Id,ProcessName,Path`: PASS; no process rows after final stop.
- `npm run typecheck`: PASS.
- `npm run test:renderer-smoke`: PASS; renderer smoke result `{"ok":true,"failures":[]}`. Vite emitted the existing chunk-size warning.
- `npm run test:electron-parity`: PASS; Electron parity passed across 13 save/options fixtures and the `game\BEA.exe` executable fixture.
- `py -3 tools\release_curated_manifest.py --check`: PASS.
- `node -e "<parse developer_agent_state.json, documentation_agent_state.json, and local proof JSON>"`: PASS.
- `git diff --check`: PASS.
