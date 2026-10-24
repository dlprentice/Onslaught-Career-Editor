# Native Windows companion checks

Status: active development check
Last updated: 2026-10-24
Summary: exercises the companion's production file, process and launcher boundaries on native Windows without Godot.

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
its written options container matched the baseline exactly. Unicode publication and discovery passed in the companion
backend; loading that edited Unicode career in Windows CE was not established. This does not validate the Godot UI.

The initial version queries hit the production five-second deadline. Later queries through the same production
implementation succeeded, as did independent native and .NET subprocess controls. The initial refusals are retained
as a transient limit, with no established cause and no timeout workaround. A warm version pass does not establish
reliable first-launch timing on every Windows system. Preserve failed and successful reports together.
