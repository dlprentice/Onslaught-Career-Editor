# WinDbg/CDB copied-target runbook

Use this workflow only for a copied `BEA.exe` launched from an app-owned profile. Never attach these helpers to the installed game directory.

## Prepare a bounded session

1. Confirm the retail specimen against [retail-specimen-baseline.md](retail-specimen-baseline.md) and [retail-specimen-manifest-2026-03-14.json](retail-specimen-manifest-2026-03-14.json):

   ```powershell
   py -3 tools\hash_retail_specimens.py
   ```

2. Create one ignored, task-scoped command directory under `.artifacts/`:

   ```powershell
   New-Item -ItemType Directory -Force .artifacts\cdb\session | Out-Null
   ```

3. Put only the commands needed for this observation in `.artifacts\cdb\session\observer.cdb.txt`. Command files are deliberately not tracked; the evidence record should state the exact commands used.

4. Identify the copied-profile process with `tools/list_game_windows.ps1`, then attach by exact PID and identity:

   ```powershell
   $profilesRoot = (Resolve-Path .artifacts\profiles).Path
   $profile = (Resolve-Path .artifacts\profiles\<profile-name>).Path
   $commandRoot = (Resolve-Path .artifacts\cdb\session).Path

   powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 `
     -ProcessId <managed-bea-pid> `
     -AppOwnedProfilesRoot $profilesRoot `
     -ExpectedExecutablePath (Join-Path $profile BEA.exe) `
     -ExpectedWorkingDirectory $profile `
     -CommandFile (Join-Path $commandRoot observer.cdb.txt) `
     -AllowedCommandRoot $commandRoot `
     -LogPath (Join-Path $commandRoot windbg.log)
   ```

`start_cdb_server.ps1` refuses process-name attachment by default, verifies the copied executable and working directory, and requires an explicit allowed root for debugger commands. Keep remote-server mode off unless that separate surface is the subject of a deliberate security review.

## Useful breakpoint recipes

These addresses and calling-shape inferences apply only to the pinned retail specimen.

### Career load

```text
bp 00421200 ".printf \"CCareer__Load this=%p src=%p size=%x flag=%x\\n\", @ecx, poi(@esp+4), poi(@esp+8), poi(@esp+0c); g"
```

Observed static shape: `this` in `ECX`; source, size, and flag at `esp+4`, `esp+8`, and `esp+0c`.

### Frontend load

```text
bp 00461E20 ".printf \"CFEPLoadGame__DoLoad this=%p\\n\", @ecx; g"
```

### Cheat lookup

```text
bp 00465490 ".printf \"IsCheatActive this=%p cheat=%x\\n\", @ecx, poi(@esp+4); g"
```

### Pause-menu initialization

```text
bp 004CDE60 ".printf \"PauseMenu__Init this=%p\\n\", @ecx; g"
```

## Evidence boundary

Runtime observations establish only what the pinned copied specimen did under the recorded inputs. Keep the specimen hashes, command text, log, outcome, and remaining question together under the task-scoped `.artifacts/` directory. Do not promote binaries, payloads, debugger logs, or generated command files into Git.
