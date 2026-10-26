# Native Windows companion checks

Status: active development check
Last updated: 2026-10-25
Summary: exercises native file/process/launcher boundaries and records the separate bounded development Godot UI workflow gate.

This console executable compile-links the app's production implementations. It does not carry a second save codec,
file publisher, process detector or platform override. Its Windows checks complement the Godot UI checks; they do not
establish UI, rendering, game-load or gameplay acceptance. A successful cross-compilation is not a Windows test result.

Build with the repository's pinned SDK and runtime from the repository root:

```sh
dotnet publish companion/OnslaughtToolkit.NativeChecks/OnslaughtToolkit.NativeChecks.csproj \
  -c Release -r win-x64 --self-contained true \
  -p:UseSharedCompilation=false -m:8 --output local-data/native-check/win-x64
```

On a shared development machine, apply its resource and heavy-job lock rules around that command. The result includes
its runtime; no .NET installation or Godot is needed on Windows. Copy the entire output directory to the test machine.

Use an admitted **copy of a real game-created career**, with an independently recorded SHA-256. Never synthesize one.
Keep the fixture outside the disposable root. Keep the root outside the actual user profile and CE package; the `files`
phase refuses any existing root. The launcher must be a real `onslaught-ce.exe` from the selected CE package. The harness
does not launch a game or terminate processes. It launches only `onslaught-ce.exe --version` in the `version` phase.

Run in a Windows command prompt, substituting the absolute paths, fixture hash and expected package version:

```bat
OnslaughtToolkit.NativeChecks.exe files --root C:\ce-check\run01 --fixture C:\ce-check\fixtures\baseline.bes --fixture-sha256 HASH --launcher C:\ce-package\onslaught-ce.exe
OnslaughtToolkit.NativeChecks.exe version --root C:\ce-check\run01 --fixture C:\ce-check\fixtures\baseline.bes --fixture-sha256 HASH --launcher C:\ce-package\onslaught-ce.exe --expected-version VERSION
```

The file phase uses an isolated `BEA_USER_DIR` at `ROOT\user`, with backups at `ROOT\backups`. It checks protected read,
selected-counter edit, preservation of every other byte, verified backup/reopen, Unicode publication/discovery,
stale-input refusal in both writers, Windows sharing refusal, restoration from the verified backup, and `ce.ini`
backup/edit/reopen with unknown-line preservation and stale refusal. It restores `baseline.bes` and leaves a separate
edited Unicode career. The copied profile ends with update checks disabled. It does not touch the fixture or package.

For running-process acceptance, separately start the actual CE launcher with `BEA_USER_DIR=ROOT\user` and admitted game
data. Record its actual **bea.exe** PID and leave it running. Then run:

```bat
OnslaughtToolkit.NativeChecks.exe running --root C:\ce-check\run01 --fixture C:\ce-check\fixtures\baseline.bes --fixture-sha256 HASH --launcher C:\ce-package\onslaught-ce.exe --pid PID
```

That phase independently checks the PID's executable path against the selected package, then requires production
`GameProcess` to detect it and both production writers to refuse without changing the careers/settings or creating a
backup. A missing process, a test stub or an unrelated PID is a failure. The operator owns game shutdown.

Each phase prints a JSON report and returns zero only on success. Retain the report, source commit, artifact hash,
fixture provenance/hash, selected launcher hash/version, Windows version and actual CE launch/exit evidence in private
`local-data/`. These reports contain local paths and do not belong in Git. A failing phase stops at its first failure
and preserves its private root for diagnosis; use a new root for another file-phase run.

Native Windows 11 Enterprise Evaluation (build 26300) was exercised on 2026-10-24 with the pinned .NET runtime.
The file/settings workflow and actual CE process refusal passed. A separate CE replay loaded the restored baseline;
its written options container matched the baseline exactly. A second replay loaded the production-written edited
`CE Élan 日本語.bes` from a fresh copied profile, reached level selection and exited normally. CE's written options
container matched the edited career exactly, and the career itself was unchanged. The capture was inspected. These
backend and game-load checks do not validate the Godot UI, hardware audio or complete campaign play.

Repeated standalone version queries, including the final check, hit the production five-second deadline. Queries
through the same production implementation inside a small diagnostic succeeded, as did independent native and .NET
subprocess controls; one intervening standalone query also passed. The version phase is therefore not reliably
passing in this environment. An external observer captured a recurring failure without modifying the launcher:
one thread waited in Windows loader initialization while another thread remained in `NtOpenFile` at both
samples. A further ABI-checked, read-only observation identified that open as the package's `SDL3.dll`.
This narrows the observed stall to startup outside the launcher's version-output path; why Windows delayed that
file open remains unresolved. It does not establish a bug in SDL code or identify a filesystem filter.
The observer resumed each briefly suspended thread, and the production
five-second deadline cleaned up its owned child. No timeout workaround was applied. Preserve failed and successful
reports together; the passing controls do not cancel the observed refusals.

The later selected CE `0.1.6-dev` launcher, source `9ed8c56e81d3`, returned its actual version through
production discovery in the October 25 rendered development workflow. This is a passing observation for
that package and invocation, not a general resolution of the earlier loader wait. The source/package pins,
native process evidence, byte assertions and inspected screenshots are recorded in
[the dated acceptance entry](../../VALIDATION.md#companion-native-windows-development-ui--october-25).

## Godot UI workflow gate

`Development/CeLiveCheck.cs` also accepts an explicit `workflow` phase in a **development** Godot build.
Normal release exports exclude this entry. Use a copied CE package and profile below a new disposable owner,
outside the real Windows profile; keep the admitted real baseline byte-identical. Prepare an existing empty
backup folder, `user/savegames/Companion Pilot.bes` copied from that baseline, and `user/ce.ini` containing
`update_check=0`, `record_sessions=0` and `future_kept=acceptance`. The original game folder is read-only input.
Place the `.companion-owned` marker below the owner and supply this private JSON through
`ONSLAUGHT_CE_LIVE_CHECK`:

```json
{
  "owner": "C:/companion-ui/run01",
  "phase": "workflow",
  "launcher": "C:/companion-ui/run01/ce/onslaught-ce.exe",
  "user": "C:/companion-ui/run01/user",
  "baseline": "C:/companion-ui/run01/baseline.bes",
  "backups": "C:/companion-ui/run01/backups",
  "game": "C:/read-only-game-data",
  "expectedVersion": "SELECTED_VERSION",
  "launcherSha256": "SELECTED_LAUNCHER_SHA256",
  "baselineSha256": "ADMITTED_REAL_BASELINE_SHA256",
  "capture": true
}
```

The acceptance package uses a one-node `CeWorkflowEntry` wrapper to call the same workflow. Invoke that
explicit development package under an external 90-second owned-process deadline, a private
HOME/USERPROFILE/APPDATA/LOCALAPPDATA/TEMP, and cleared inherited `BEA_*` overrides. Source/editor runs can
instead use `--script res://Development/CeLiveCheck.cs`; export templates do not expose that editor argument. The operator owns native Windows execution; no VM is started by this entry. Use rendering for
`capture: true`; a headless invocation refuses that request. Retain the full package inventory and source
commit with the configuration and receipt. Never reuse a successful owner for another workflow.

Before UI initialization, the workflow checks the exact launcher, baseline and initial career hashes and
refuses linked input ancestors. Production discovery must read the expected launcher version. The workflow
then edits one kill counter through the actual career page, verifies the backup and every unselected byte,
creates a named Unicode CE career, checks stale-input refusal, changes and reopens both supported launcher
settings while preserving unknown lines, checks stale-settings refusal, and restores/reopens the baseline
through the Backups page while verifying the displaced career's recovery copy. Only the existing Linux
permission-failure arm runs on Linux; this gate does not claim a Windows ACL-failure test.

With capture enabled, it retains Home, saved Settings and restored Backups screenshots. A zero exit and
`passed: true` workflow receipt establish those automated control/byte checks only. Inspect the screenshots
first-hand before claiming visual acceptance. The gate never starts CE gameplay, checks the public feed,
tests physical input or establishes hardware audio. The selected native Windows development workflow passed
under `DEBUG_PROCESS` and a private job, with first-hand inspection of all three screenshots. Ordinary release
invocation, physical input, file dialogs, Windows ACL failures and hardware GPU rendering remain unvalidated.

The offline/headless fixture control is:

```sh
ONSLAUGHT_GODOT_HEADLESS=godot-headless python tools/companion_godot.py test \
  --script Development/CeLiveCheckTests.cs --timeout 120
```

It uses the tracked real-save fixture and an owned `--version`-only shell script, with no real game or Windows
claim. It exercises hash/version admission refusals, the complete fixture UI workflow, and refusal of a
rendering claim from headless execution.
