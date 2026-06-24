# WinDbg/CDB Runbook

> Minimal runtime-validation workflow for BEA.exe
> Date: 2026-03-14

## Purpose

This is the first durable runtime-debugging runbook for the retail Steam build.

It is intentionally narrow:

- pin the specimen first,
- use `CDB` server/client mode,
- log to a file,
- tail the log incrementally,
- probe only the highest-value unresolved runtime questions.

## Current Workstation Reality

As of 2026-03-14 on this workstation:

- `cdb.exe` is still **not** on `PATH` in older shells
- the standard Windows Kits paths checked during this pass were absent:
  - `C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\cdb.exe`
  - `C:\Program Files\Windows Kits\10\Debuggers\x86\cdb.exe`
- Microsoft WinDbg is now installed and exposes the x86 debugger here:
  - `C:\Program Files\WindowsApps\Microsoft.WinDbg_1.2601.12001.0_x64__8wekyb3d8bbwe\x86\cdb.exe`

That means live sessions can run now, but helper scripts should be preferred over bare `cdb.exe` invocations so the path resolution stays stable.

## First Step: Pin The Specimen

Before attaching:

```powershell
py -3 tools\hash_retail_specimens.py
```

Use the current [retail-specimen-baseline.md](retail-specimen-baseline.md) and
[retail-specimen-manifest-2026-03-14.json](/reverse-engineering/binary-analysis/retail-specimen-manifest-2026-03-14.json)
as the authority for which executable and supporting files the session is about.

If the installed live executable does not match the clean repo mirror, say so explicitly in the session notes. Do not silently treat a patched live binary as the clean retail authority.

## Recommended Session Layout

Use a task-scoped scratch folder under `subagents/`, for example:

```text
subagents/2026-03-14-runtime-defaultoptions-wave1/
```

Suggested contents:

- `windbg.log`
- `windbg.cursor`
- `session-notes.md`
- any breakpoint command files or probe outputs

## Helper Scripts

Prefer these helpers instead of typing the WindowsApps path manually:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\get_cdb_path.ps1 -AsLiteral
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\defaultoptions-wave1.cdb.txt
powershell -ExecutionPolicy Bypass -File .\tools\connect_cdb_client.ps1
```

For copied-profile runtime proof, prefer exact-PID attach after `tools/list_game_windows.ps1` identifies the managed BEA window:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -ProcessId <managed-bea-pid> -CommandFile .\tools\runtime-probes\defaultoptions-wave1.cdb.txt
```

The helper defaults to a local attached logger because the current WinDbg/CDB package exits before opening the log when `-server` is combined directly with an attach target. Use `-EnableRemoteServer` only for a separately proven server/client workflow. The helper fails if multiple name-matched BEA processes are running, if the requested PID is not the expected process, or if CDB cannot create the requested log before input begins. Treat a missing debugger log as a setup failure, not runtime behavior evidence.

Use simple alphanumeric or underscore-only server passwords. CDB can exit before opening the log when the TCP server password contains punctuation.

Current canned probe command files:

- `tools/runtime-probes/defaultoptions-wave1.cdb.txt`
- `tools/runtime-probes/maladim-wave1.cdb.txt`

## Server / Client Pattern

Assuming `cdb.exe` is available:

### 1. Start the game normally

Reach the state you want to probe, or leave it at boot if the probe target is startup/load behavior.

### 2. Attach a long-lived server

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\defaultoptions-wave1.cdb.txt
```

### 3. Connect a client

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\connect_cdb_client.ps1
```

### 4. Tail the server log incrementally

```powershell
py -3 tools\windbg_tail.py --log C:\temp\bea-windbg.log
```

Use `--reset` when starting a fresh read window.

## First Probe Targets

These are the highest-value immediate targets from the current repo state:

1. `CCareer__Load` at `0x00421200`
2. `CFEPLoadGame__DoLoad` at `0x00461E20`
3. `IsCheatActive` at `0x00465490`
4. `PauseMenu__Init` at `0x004CDE60`

Why these first:

- `CCareer__Load` and `CFEPLoadGame__DoLoad` close the `defaultoptions.bea` write/apply behavior loop.
- `IsCheatActive` and `PauseMenu__Init` are the shortest path to clarifying `Maladim` runtime gating.

## Minimal Breakpoint Recipes

These are starting points, not final automation. They assume current address naming and current retail baseline.

### `CCareer__Load`

```text
bp 00421200 ".printf \"CCareer__Load this=%p src=%p size=%x flag=%x\\n\", @ecx, poi(@esp+4), poi(@esp+8), poi(@esp+0c); g"
```

Inference:

- `this` in `ECX`
- source pointer at `esp+4`
- size at `esp+8`
- `flag` at `esp+0c`

### `IsCheatActive`

```text
bp 00465490 ".printf \"IsCheatActive this=%p cheat=%x\\n\", @ecx, poi(@esp+4); g"
```

### `PauseMenu__Init`

```text
bp 004CDE60 ".printf \"PauseMenu__Init this=%p\\n\", @ecx; g"
```

### `CFEPLoadGame__DoLoad`

```text
bp 00461E20 ".printf \"CFEPLoadGame__DoLoad this=%p\\n\", @ecx; g"
```

## Suggested First Runtime Questions

### `defaultoptions.bea`

- Does boot call `CCareer__Load(..., flag=0)` exactly as expected?
- During frontend load flows, when does `CFEPLoadGame__DoLoad` cause `defaultoptions.bea` write-back?
- Is the write-back path gated only by `DAT_0082b5b0 == 0`, or are there extra runtime conditions?

### `Maladim`

- Does `IsCheatActive(3)` fire when the save name contains `Maladim`?
- Does `PauseMenu__Init` expose the option but later gameplay paths suppress the effect?
- Is the missing visible effect a menu/display issue, a toggle-state issue, or a deeper gameplay-state gate?

## Recording Rule

Every runtime pass should leave behind:

- the specimen keys used,
- the exact breakpoints/commands used,
- the log path,
- the observed outcome,
- and the unresolved next question.

Persist those under `subagents/` with a dated, task-scoped filename.
