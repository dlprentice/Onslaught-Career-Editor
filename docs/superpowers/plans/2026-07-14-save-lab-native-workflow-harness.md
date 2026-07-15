# Save Lab Native Workflow Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fail-closed unattended native WinUI gate that exercises Save
Editor first use and Game Options with deterministic inputs, publishes eight
receipt-bound normal/760 captures plus two workflow receipts, and needs no game
launch or human screenshot review.

**Architecture:** Keep Save Lab as a separate acceptance surface. Extract the
small generic Python lifecycle and C# pixel-validation pieces from the accepted
Home gate, then add Save-specific native workflow, evidence, publication, and
outer-runner validators. One explicit RID-pinned test owns two isolated WinUI
launches and publishes one invocation-bound ignored/local directory.

**Tech Stack:** .NET 10, NUnit, FlaUI UIA3, WinUI 3, System.Drawing,
System.Text.Json, Python 3 standard library, PowerShell process census, npm
command authority.

## Global Constraints

- Build and test only the repository Debug/win-x64 WinUI output; reject
  `ONSLAUGHT_WINUI_TEST_EXE_PATH` for this gate.
- Keep `tests_shared/fixtures/gold_career_save.bin` immutable and require
  SHA-256 `0C17E47DB9D666E9B26EF88D43D0A25E7CBFBF4F88C8005CC748965050E506FB`.
- Create synthetic options as exactly 10,004 zeroed bytes with little-endian
  word `0x4BD1` at offset zero; require SHA-256
  `A922C6BCA412DB45AED3FCCBE926B6383C039CCF3778C4558D299D1D3C466D99`.
- Use UIA Value/Toggle/ExpandCollapse/Scroll/Focus/Invoke patterns only; do not
  synthesize keyboard or pointer input.
- Never invoke the Save Editor reveal action or Game Options browser action.
- Keep all `.bes`, `.bea`, app data, screenshots, TRX, and manifests under
  ignored `local-lab/`; track only source, tests, commands, and bounded docs.
- Never launch BEA, touch the Steam install/original executable, enable
  Host/Join, publish a release/tag, or claim retail/save-format/visual parity.
- Preserve `terminals/` and every unrelated worktree path.

---

### Task 1: Make RID-Pinned Source Tests Resolve The Repository Reliably

**Files:**
- Modify: `OnslaughtCareerEditor.UiTests/TestFixturePaths.cs`
- Modify: `OnslaughtCareerEditor.UiTests/ReceiptBoundVisualCaptureTests.cs`
- Add: `OnslaughtCareerEditor.UiTests/TestFixturePathsTests.cs`

**Interfaces:**
- Consumes: a starting directory below a repository checkout.
- Produces: `TestFixturePaths.ResolveRepoRoot(string startDirectory)` and the
  existing `TestFixturePaths.RepoRoot` property backed by marker discovery.

- [ ] **Step 1: Add the failing marker-discovery tests**

```csharp
[Test]
public void ResolveRepoRoot_FindsMarkersAboveRidSpecificOutput()
{
    string root = Path.Combine(Path.GetTempPath(), $"repo-root-{Guid.NewGuid():N}");
    string ridOutput = Path.Combine(root, "OnslaughtCareerEditor.UiTests", "bin", "Debug", "net10.0-windows", "win-x64");
    Directory.CreateDirectory(ridOutput);
    File.WriteAllText(Path.Combine(root, "package.json"), "{}");
    Directory.CreateDirectory(Path.Combine(root, "OnslaughtCareerEditor.WinUI"));
    Directory.CreateDirectory(Path.Combine(root, "OnslaughtCareerEditor.UiTests"));
    try
    {
        Assert.That(TestFixturePaths.ResolveRepoRoot(ridOutput), Is.EqualTo(Path.GetFullPath(root)));
    }
    finally
    {
        Directory.Delete(root, recursive: true);
    }
}

[Test]
public void ResolveRepoRoot_RejectsTreeWithoutRepositoryMarkers()
{
    string root = Path.Combine(Path.GetTempPath(), $"repo-root-missing-{Guid.NewGuid():N}");
    Directory.CreateDirectory(root);
    try
    {
        Assert.Throws<DirectoryNotFoundException>(() => TestFixturePaths.ResolveRepoRoot(root));
    }
    finally
    {
        Directory.Delete(root, recursive: true);
    }
}
```

- [ ] **Step 2: Run the tests RED and retain the observed RID baseline**

Run:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --configuration Debug --runtime win-x64 --filter "FullyQualifiedName~TestFixturePathsTests"
```

Expected: compile failure because `ResolveRepoRoot` does not exist. The already
observed broader RID baseline remains 32 passed / 7 failed with duplicated
`OnslaughtCareerEditor.UiTests` source paths.

- [ ] **Step 3: Implement marker-based ancestor discovery**

```csharp
internal static string RepoRoot => ResolveRepoRoot(AppContext.BaseDirectory);

internal static string ResolveRepoRoot(string startDirectory)
{
    DirectoryInfo? candidate = new(Path.GetFullPath(startDirectory));
    for (int depth = 0; candidate is not null && depth < 12; depth++, candidate = candidate.Parent)
    {
        if (File.Exists(Path.Combine(candidate.FullName, "package.json")) &&
            Directory.Exists(Path.Combine(candidate.FullName, "OnslaughtCareerEditor.WinUI")) &&
            Directory.Exists(Path.Combine(candidate.FullName, "OnslaughtCareerEditor.UiTests")))
        {
            return candidate.FullName;
        }
    }

    throw new DirectoryNotFoundException($"Could not resolve repository root from: {startDirectory}");
}
```

Replace the private fixed-parent `ResolveRepoRoot` in
`ReceiptBoundVisualCaptureTests` with `TestFixturePaths.RepoRoot`.

- [ ] **Step 4: Run RID-focused tests GREEN**

Run the 39-test filter from the baseline:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --configuration Debug --runtime win-x64 --filter "FullyQualifiedName~SaveEditorFirstSaveJourneyTests|FullyQualifiedName~ReceiptBoundVisualCaptureTests|FullyQualifiedName~TestFixturePathsTests"
```

Expected: all tests pass, with no duplicated project segment in source paths.

- [ ] **Step 5: Commit the bounded fix**

```powershell
git add -- OnslaughtCareerEditor.UiTests/TestFixturePaths.cs OnslaughtCareerEditor.UiTests/TestFixturePathsTests.cs OnslaughtCareerEditor.UiTests/ReceiptBoundVisualCaptureTests.cs
git commit -m "test(winui): resolve repo root from RID output"
```

### Task 2: Extract Shared Native Runner And Toolkit Pixel Primitives

**Files:**
- Add: `tools/winui_native_acceptance_support.py`
- Add: `tools/winui_native_acceptance_support_test.py`
- Modify: `tools/run_winui_home_native_visual_focus.py`
- Modify: `tools/run_winui_home_native_visual_focus_test.py`
- Add: `OnslaughtCareerEditor.UiTests/ToolkitVisualEvidenceAcceptance.cs`
- Add: `OnslaughtCareerEditor.UiTests/NativeWinUiSessionResourceCleanup.cs`
- Modify: `OnslaughtCareerEditor.UiTests/HomeVisualEvidenceAcceptance.cs`
- Modify: `OnslaughtCareerEditor.UiTests/HomeSessionResourceCleanup.cs`
- Modify: `OnslaughtCareerEditor.UiTests/HomeVisualEvidenceAcceptanceTests.cs`
- Add: `OnslaughtCareerEditor.UiTests/NativeWinUiSessionResourceCleanupTests.cs`

**Interfaces:**
- Produces Python `NativeAcceptanceError`, `require`, `sha256`, `normalized`,
  `png_dimensions`, `validate_exact_trx`, `process_census`,
  `describe_processes`, `run_command`, `terminate_owned_process_tree`,
  `validate_invocation_id`, `shutdown_build_servers`, and
  `append_cleanup_error`.
- Produces C# `ToolkitVisualEvidenceAcceptance` with
  `HasMeaningfulFrameCoverage`, `HasRenderedToolkitHeader`, and
  `HasRenderedActivity`, plus `NativeWinUiSessionResourceCleanup.Run`.
- Preserves Home's public-to-tests names through thin compatibility wrappers.

- [ ] **Step 1: Write Python support tests RED**

Cover exact one-test TRX acceptance/rejection, PNG signature/dimensions,
invocation IDs, timeout termination of only the injected root PID, and cleanup
error accumulation. Import the missing module directly so the first run fails
for the intended reason.

```python
def test_validate_exact_trx_rejects_skipped_test(self) -> None:
    trx = self.write_trx(total=1, executed=0, passed=0, not_executed=1, outcome="NotExecuted")
    with self.assertRaisesRegex(support.NativeAcceptanceError, "exactly one executed passing test"):
        support.validate_exact_trx(trx, "ExpectedMethod", "native fixture")

def test_validate_invocation_id_rejects_non_lower_hex(self) -> None:
    with self.assertRaisesRegex(support.NativeAcceptanceError, "invocation ID"):
        support.validate_invocation_id("ABC")
```

Run:

```powershell
py -3 tools\winui_native_acceptance_support_test.py
```

Expected: import/module failure.

- [ ] **Step 2: Implement the generic Python support and migrate Home through wrappers**

Use explicit `repo_root` arguments for process and command operations. Keep the
Home module's existing callable names so its unit tests can continue patching
`home.process_census`, `home.run_command`, and related functions.

```python
class NativeAcceptanceError(RuntimeError):
    pass

def validate_exact_trx(path: Path, expected_method_name: str, label: str) -> dict[str, int]:
    require(path.is_file(), f"{label} TRX is missing: {path}")
    root = ET.parse(path).getroot()
    local_name = lambda element: element.tag.rsplit("}", 1)[-1]
    counters = next((element for element in root.iter() if local_name(element) == "Counters"), None)
    results = [element for element in root.iter() if local_name(element) == "UnitTestResult"]
    require(counters is not None, f"{label} TRX has no result counters")
    names = ("total", "executed", "passed", "failed", "error", "timeout",
             "aborted", "inconclusive", "notExecuted")
    summary = {name: int(counters.attrib.get(name, "0")) for name in names}
    rejected = ("failed", "error", "timeout", "aborted", "inconclusive", "notExecuted")
    require(
        summary["total"] == summary["executed"] == summary["passed"] == 1
        and all(summary[name] == 0 for name in rejected)
        and len(results) == 1
        and results[0].attrib.get("testName") == expected_method_name
        and results[0].attrib.get("outcome") == "Passed",
        f"{label} TRX must contain exactly one executed passing test: {summary}",
    )
    return summary

def run_command(command: list[str], *, repo_root: Path, timeout: int,
                env_overrides: dict[str, str] | None = None) -> None:
    env = os.environ.copy()
    env["MSBUILDDISABLENODEREUSE"] = "1"
    env.update(env_overrides or {})
    process = subprocess.Popen(command, cwd=repo_root, env=env)
    try:
        return_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_owned_process_tree(process.pid, repo_root=repo_root)
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        raise
    require(return_code == 0, f"command exited {return_code}: {' '.join(command)}")
```

Home's surface wrapper remains:

```python
HarnessError = native_support.NativeAcceptanceError
require = native_support.require
sha256 = native_support.sha256
normalized = native_support.normalized
png_dimensions = native_support.png_dimensions

def validate_trx(path: Path) -> dict[str, int]:
    return native_support.validate_exact_trx(path, TEST_METHOD_NAME, "native Home")
```

- [ ] **Step 3: Write C# generic-helper tests RED, then extract without changing Home behavior**

Add direct assertions against `ToolkitVisualEvidenceAcceptance` using the same
opaque structured, near-black, and transparent bitmaps already used by Home.
Add cleanup order/fault tests:

```csharp
[Test]
public void Run_StillCleansAppWhenAutomationDisposeThrows()
{
    bool cleaned = false;
    Assert.Throws<InvalidOperationException>(() =>
        NativeWinUiSessionResourceCleanup.Run(
            () => throw new InvalidOperationException("dispose"),
            () => cleaned = true));
    Assert.That(cleaned, Is.True);
}
```

Implement generic classes, then make Home wrappers delegate exactly:

```csharp
internal static bool HasMeaningfulFrameCoverage(Bitmap bitmap) =>
    ToolkitVisualEvidenceAcceptance.HasMeaningfulFrameCoverage(bitmap);

internal static void Run(Action disposeAutomation, Action cleanupApp) =>
    NativeWinUiSessionResourceCleanup.Run(disposeAutomation, cleanupApp);
```

- [ ] **Step 4: Run shared and Home regressions GREEN**

```powershell
py -3 tools\winui_native_acceptance_support_test.py
py -3 tools\run_winui_home_native_visual_focus_test.py
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --no-build --no-restore --configuration Debug --runtime win-x64 --filter "FullyQualifiedName~HomeVisualEvidenceAcceptanceTests|FullyQualifiedName~HomeSessionResourceCleanupTests|FullyQualifiedName~NativeWinUiSessionResourceCleanupTests"
```

Expected: all focused tests pass.

- [ ] **Step 5: Commit shared infrastructure**

```powershell
git add -- tools/winui_native_acceptance_support.py tools/winui_native_acceptance_support_test.py tools/run_winui_home_native_visual_focus.py tools/run_winui_home_native_visual_focus_test.py OnslaughtCareerEditor.UiTests/ToolkitVisualEvidenceAcceptance.cs OnslaughtCareerEditor.UiTests/NativeWinUiSessionResourceCleanup.cs OnslaughtCareerEditor.UiTests/HomeVisualEvidenceAcceptance.cs OnslaughtCareerEditor.UiTests/HomeSessionResourceCleanup.cs OnslaughtCareerEditor.UiTests/HomeVisualEvidenceAcceptanceTests.cs OnslaughtCareerEditor.UiTests/NativeWinUiSessionResourceCleanupTests.cs
git commit -m "refactor(winui): share native acceptance primitives"
```

### Task 3: Define Save Lab Evidence, Artifact, And Publication Contracts

**Files:**
- Add: `OnslaughtCareerEditor.UiTests/SaveLabNativeEvidence.cs`
- Add: `OnslaughtCareerEditor.UiTests/SaveLabNativeEvidenceAcceptance.cs`
- Add: `OnslaughtCareerEditor.UiTests/SaveLabNativeEvidenceAcceptanceTests.cs`

**Interfaces:**
- Produces records `SaveLabAppIdentityEvidence`, `SaveLabFocusObservation`,
  `SaveLabCaptureEvidence`, `SaveLabWorkflowEvidence`,
  `SyntheticOptionsEvidence`, and `SaveLabAcceptanceManifest`.
- Produces `SaveLabNativeEvidenceAcceptance.Publish(stagingDirectory,
  acceptedDirectory, manifest)` and `Validate(stagingDirectory, manifest)`.
- The test file owns `SaveLabNativeEvidenceTestFactory.CreateValid(string
  stagingDirectory)`, which writes the exact eight PNGs and four 10,004-byte
  input/output artifacts before returning a fully mapped valid manifest.

- [ ] **Step 1: Write incomplete/path-escape/hash-mismatch/publication tests RED**

Build a valid in-memory manifest fixture with eight small PNGs and four 10,004
byte workflow artifacts, then mutate one property per test.

```csharp
[Test]
public void Validate_RejectsArtifactPathOutsideStaging()
{
    SaveLabAcceptanceManifest valid = SaveLabNativeEvidenceTestFactory.CreateValid(_staging);
    SaveLabAcceptanceManifest manifest = valid with
    {
        Workflows = valid.Workflows
            .Select((row, index) => index == 0 ? row with { OutputRelativePath = @"..\escape.bes" } : row)
            .ToArray(),
    };
    Assert.That(
        () => SaveLabNativeEvidenceAcceptance.Validate(_staging, manifest),
        Throws.TypeOf<AssertionException>().With.Message.Contains("confined"));
}

[Test]
public void Publish_RenamesOneCompleteSiblingAndLeavesNoPartial()
{
    SaveLabNativeEvidenceAcceptance.Publish(
        _staging,
        _accepted,
        SaveLabNativeEvidenceTestFactory.CreateValid(_staging));
    Assert.That(Directory.Exists(_staging), Is.False);
    Assert.That(File.Exists(Path.Combine(_accepted, "save-lab-acceptance-manifest.json")), Is.True);
}
```

Run the new class filter; expect compile failure because records/acceptance do
not exist.

- [ ] **Step 2: Implement exact records and validation**

Use these fixed top-level values:

```csharp
internal sealed record SaveLabAcceptanceManifest(
    int SchemaVersion,
    string HarnessRunId,
    string InteractionMode,
    string TrackedSaveFixtureSha256,
    SyntheticOptionsEvidence SyntheticOptions,
    IReadOnlyList<SaveLabCaptureEvidence> Captures,
    IReadOnlyList<SaveLabWorkflowEvidence> Workflows);
```

Validation requires schema 1; lowercase 32-hex run ID; exact interaction mode;
the exact fixture and synthetic hashes; exact eight-file workflow/phase/size
map; two workflows named `save-editor` and `game-options`; full identity
bijection; matching before/after input hashes; distinct output hashes; path
confinement; exact artifact lengths; PNG dimensions/hashes; nonempty markers;
and owner-bound before/after focus on the phase target.

Write the manifest to a unique temporary sibling inside staging with
`FileMode.CreateNew`, flush to disk, reopen/parse/validate, move to the canonical
name, and then `Directory.Move(stagingDirectory, acceptedDirectory)`. On any
exception delete only the temporary manifest and leave the caller-owned partial
directory for bounded rollback.

- [ ] **Step 3: Run evidence tests GREEN**

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --no-restore --configuration Debug --runtime win-x64 --filter "FullyQualifiedName~SaveLabNativeEvidenceAcceptanceTests"
```

Expected: all acceptance and adversarial mutations pass.

- [ ] **Step 4: Commit the evidence contract**

```powershell
git add -- OnslaughtCareerEditor.UiTests/SaveLabNativeEvidence.cs OnslaughtCareerEditor.UiTests/SaveLabNativeEvidenceAcceptance.cs OnslaughtCareerEditor.UiTests/SaveLabNativeEvidenceAcceptanceTests.cs
git commit -m "test(winui): define Save Lab native evidence"
```

### Task 4: Implement The One-Test Two-Workflow Native Producer

**Files:**
- Add: `OnslaughtCareerEditor.UiTests/SaveLabNativeVisualCapture.cs`
- Add: `OnslaughtCareerEditor.UiTests/SaveLabNativeSession.cs`
- Add: `OnslaughtCareerEditor.UiTests/WinUiSaveLabNativeWorkflowTests.cs`
- Modify: `OnslaughtCareerEditor.UiTests/SaveEditorFirstSaveJourneyTests.cs`

**Interfaces:**
- Produces explicit method
  `WinUiSaveLabNativeWorkflowTests.SaveLab_FirstUseAndOptions_PublishDeterministicNativeEvidence`.
- Produces `SaveLabNativeSession` with `Application App`,
  `UIA3Automation Automation`, `Window Window`, `string ExecutablePath`, and
  `ReceiptBoundAppIdentity Identity`; disposal always runs app cleanup even
  when automation disposal throws.
- Produces `SaveLabNativeVisualCapture.Capture(SaveLabNativeSession session,
  string workflow, string phase, string focusAutomationId, Rectangle bounds,
  string outputPath, IReadOnlyList<string> markerAutomationIds,
  Action postResizeRealization) -> SaveLabCaptureEvidence`.

- [ ] **Step 1: Add static producer-contract tests RED**

Extend `SaveEditorFirstSaveJourneyTests` to require the new producer source to:

```csharp
Assert.That(source, Does.Contain("gold_career_save.bin"));
Assert.That(source, Does.Contain("0C17E47D"));
Assert.That(source, Does.Contain("A922C6BC"));
Assert.That(source, Does.Contain("ONSLAUGHT_SAVE_LAB_NATIVE_ACCEPTANCE_RUN_ID"));
Assert.That(source, Does.Contain("ONSLAUGHT_GAME_DIR_CANDIDATES"));
Assert.That(source, Does.Contain("ONSLAUGHT_STEAM_ROOT_CANDIDATES"));
Assert.That(source, Does.Not.Contain("ONSLAUGHT_WINUI_REAL_OPTIONS_PATH"));
Assert.That(source, Does.Not.Contain("ExplorerRevealService.TryReveal"));
Assert.That(source, Does.Not.Contain("Launcher.LaunchUriAsync"));
Assert.That(source, Does.Not.Contain("Keyboard."));
Assert.That(source, Does.Not.Contain("Mouse."));
```

Run the focused class and expect failure because the producer file is absent.

- [ ] **Step 2: Implement receipt-bound visual capture returning evidence**

`Capture` accepts the session app/automation/window, expected identity,
workflow, phase, focus target, bounds, output path, marker IDs, and a bounded
post-resize realization callback. It must:

1. revalidate full identity;
2. restore/position/foreground the exact HWND;
3. realize and stabilize every named marker;
4. focus the exact scoped element and confirm global/scoped ID, PID, bounds,
   keyboard focus, and launch HWND ownership;
5. sample marker bounds, set topmost, capture only the bound HWND, resample
   identity/focus/markers, and apply generic Toolkit pixel checks;
6. flush/reopen/validate a fresh temporary PNG, move without overwrite, and
   return its hash/evidence; and
7. restore full window placement in `finally` and delete temporary output on
   failure.

- [ ] **Step 3: Implement isolated sessions and deterministic inputs**

The test creates:

```text
local-lab/winui-save-lab-native-workflow/
  .save-lab-<UTC>-<runid>.partial/
    fixtures/first-save-input.bes
    fixtures/synthetic-options.bea
    save-session/appdata/OnslaughtCareerEditor/patched-output/first-save-input_patched.bes
    options-session/appdata/OnslaughtCareerEditor/patched-output/synthetic-options_patched.bea
    <eight PNGs>
```

Each launch sets `APPDATA`, `ONSLAUGHT_APP_CONFIG_ROOT`, initial Save tab,
`ONSLAUGHT_GAME_DIR_CANDIDATES=""`, and an isolated empty Steam root. It reads
only the repo-built executable, compares runner hashes before launch, and
verifies live identity after launch. Disposal uses
`NativeWinUiSessionResourceCleanup.Run`.

- [ ] **Step 4: Implement Save Editor RED/GREEN workflow assertions and four captures**

Require empty preset/sections, disabled write, app-owned suggested output,
collapsed/reachable advanced region, one explicit Goodies selection, successful
separate write, unchanged input hash, valid/different output, redacted UI log,
current completion, and enabled reveal without invoking it. Use these phases:

```csharp
("save-editor", "ready", "SaveEditorInputFile",
 ["SaveEditorInputFile", "SaveEditorOutputFile", "SaveEditorPatchPresetComboBox"])
```

and

```csharp
("save-editor", "complete", "SaveEditorShowWrittenSaveButton",
 ["SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton"])
```

Capture each at 1100x900 and 760x820 through `SaveEditorScrollViewer`.

- [ ] **Step 5: Implement Game Options RED/GREEN workflow assertions and four captures**

First capture guidance with focus on
`OpenZigguratControllerGuideButton` and markers
`ModernControllerSetupHeading`, `ModernControllerSetupBoundary`, and the guide
button. Then load the deterministic `.bea`; require the app-owned distinct
suggested output and no pending change; set `ConfigurationControllerConfigP1`
to `1`; require ready safety text; invoke only `ConfigurationPatchButton`; and
verify input preservation, valid/different output, P1 readback `1`, and a
redacted success log. Completion focuses the patch button and marks
`ConfigurationSafetyHint`, `ConfigurationPatchButton`, and
`ConfigurationOutputLog`. Capture both phases at both sizes through
`ConfigurationEditorScrollViewer`.

- [ ] **Step 6: Publish one complete manifest and run non-native producer guards GREEN**

Build two workflow receipts, eight capture receipts, and the fixed synthetic
recipe; call `SaveLabNativeEvidenceAcceptance.Publish`. Delete the partial root
on any test exception. Do not delete an accepted directory in the child.

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --configuration Debug --runtime win-x64 --filter "FullyQualifiedName~SaveEditorFirstSaveJourneyTests|FullyQualifiedName~SaveLabNativeEvidenceAcceptanceTests"
```

- [ ] **Step 7: Commit the native producer**

```powershell
git add -- OnslaughtCareerEditor.UiTests/SaveLabNativeVisualCapture.cs OnslaughtCareerEditor.UiTests/SaveLabNativeSession.cs OnslaughtCareerEditor.UiTests/WinUiSaveLabNativeWorkflowTests.cs OnslaughtCareerEditor.UiTests/SaveEditorFirstSaveJourneyTests.cs
git commit -m "test(winui): produce Save Lab native evidence"
```

### Task 5: Add The Fail-Closed Outer Runner And Command Authority

**Files:**
- Add: `tools/run_winui_save_lab_native_workflow.py`
- Add: `tools/run_winui_save_lab_native_workflow_test.py`
- Modify: `package.json`
- Modify: `CONTRIBUTING.md`
- Modify: `VALIDATION.md`

**Interfaces:**
- Produces `npm run test:winui-save-lab-native-workflow`.
- Produces Python `validate_manifest`, `validate_trx`, owned-evidence discovery
  and rollback, and `run_acceptance`.

- [ ] **Step 1: Write runner tests RED**

Construct a valid temporary schema-1 tree and test exact acceptance plus these
failures independently: wrong invocation ID, missing/eighth extra capture,
PNG dimension/hash mismatch, path traversal, fixture/synthetic hash mismatch,
workflow identity mismatch, input-preservation mismatch, skipped TRX, stale
partial directory, and cleanup that targets another invocation.

```python
def test_validate_manifest_rejects_path_escape(self) -> None:
    manifest = self.valid_manifest()
    manifest["Workflows"][0]["OutputRelativePath"] = "../escape.bes"
    path = self.write_manifest(manifest)
    with self.assertRaisesRegex(runner.NativeAcceptanceError, "confined"):
        runner.validate_manifest(path, repo_root=self.repo, expected_harness_run_id=self.RUN_ID)
```

Run and expect import failure before adding the runner.

- [ ] **Step 2: Implement exact surface validator and owned cleanup**

Use the shared Python lifecycle helpers. Keep Save-specific constants:

```python
EVIDENCE_ROOT = REPO_ROOT / "local-lab" / "winui-save-lab-native-workflow"
RUNNER_ROOT = REPO_ROOT / "local-lab" / "winui-save-lab-native-workflow-runner"
TEST_METHOD_NAME = "SaveLab_FirstUseAndOptions_PublishDeterministicNativeEvidence"
TEST_FQN = f"OnslaughtCareerEditor.UiTests.WinUiSaveLabNativeWorkflowTests.{TEST_METHOD_NAME}"
```

Validate exact schema/capture/workflow maps, full repo-build identities, safe
relative artifact paths, hashes/lengths, input preservation, readbacks, marker
sets, focus ownership, and PNG dimensions. Owned discovery accepts only
`save-lab-*-<runid>` and `.save-lab-*-<runid>.partial` direct children.

- [ ] **Step 3: Implement runner lifecycle and fault-safe finalization**

Run pre-census/no-partials, build, hash, one filtered test, exact TRX, exactly
one owned manifest, no partials, independent manifest reconciliation, post
census, build-server shutdown, final census, and runner-root deletion. Accumulate
all cleanup failures. On any error remove only this invocation's accepted or
partial evidence, then fail nonzero.

Pass only:

```python
{
    "ONSLAUGHT_SAVE_LAB_NATIVE_ACCEPTANCE_RUN_ID": invocation_id,
    "ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_EXE_SHA256": expected_executable_hash,
    "ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_DLL_SHA256": expected_product_hash,
}
```

- [ ] **Step 4: Run runner unit tests GREEN and wire package/docs**

```powershell
py -3 tools\run_winui_save_lab_native_workflow_test.py
py -3 -m py_compile tools\winui_native_acceptance_support.py tools\run_winui_home_native_visual_focus.py tools\run_winui_save_lab_native_workflow.py
```

Add:

```json
"test:winui-save-lab-native-workflow": "py -3 tools\\run_winui_save_lab_native_workflow_test.py && py -3 tools\\run_winui_save_lab_native_workflow.py"
```

Document the ignored evidence root, deterministic inputs, exact 1/1 and eight
capture/two workflow contract, boundaries, and the change-class routing.

- [ ] **Step 5: Commit runner and command authority**

```powershell
git add -- tools/run_winui_save_lab_native_workflow.py tools/run_winui_save_lab_native_workflow_test.py package.json CONTRIBUTING.md VALIDATION.md
git commit -m "test(winui): orchestrate Save Lab native acceptance"
```

### Task 6: Run Native Acceptance, Fix Only Proven Product Defects, And Close The Slice

**Files:**
- Conditionally modify only if the native gate proves a defect:
  `OnslaughtCareerEditor.WinUI/Pages/SavesPage.xaml`
- Conditionally add the matching static regression to:
  `OnslaughtCareerEditor.UiTests/SaveEditorFirstSaveJourneyTests.cs`
- Modify after acceptance: `CURRENT_CAPABILITIES.md`
- Modify after acceptance: `lore-book/CURRENT_CAPABILITIES.md`
- Modify after acceptance: `goal.md`
- Modify after acceptance: `goal.campaign.md`
- Modify after acceptance: `developer_agent_state.json`
- Modify after acceptance: `documentation_agent_state.json`

**Interfaces:**
- Produces one accepted ignored/local Save Lab manifest and a resume-ready next
  campaign slice.

- [ ] **Step 1: Run the exact named native gate**

```powershell
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:winui-save-lab-native-workflow
```

Expected: Debug/win-x64 build succeeds; exact native TRX 1/1; eight captures;
two workflow receipts; schema 1; one invocation; final process census zero.

- [ ] **Step 2: If native evidence proves compact clipping/overflow, reproduce RED before the smallest XAML fix**

Add one static test naming the exact grid/visual-state contract observed to
fail, run it RED, then add only the required adaptive state or width rule. Rerun
the static test and the Save native gate. Do not make speculative layout
changes when the native gate is already green.

- [ ] **Step 3: Re-run the accepted Home native gate after shared extraction or SavesPage changes**

```powershell
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:winui-home-native-visual-focus
```

Expected: exact Home 1/1, four captures, two focus receipts, schema 3, zero
process census.

- [ ] **Step 4: Run proportional full verification**

```powershell
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:winui-primary-lane
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:validation-inventory
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:docsync
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:doc-commands
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:md-links:public-core
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:generated-output-safety
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:hard-payload-safety
& 'C:\Users\david\AppData\Roaming\npm\npm.cmd' run test:repo-hygiene
git diff --check
```

Finish with a zero census for Toolkit, testhost, vstest, BEA, CDB, and WinDbg.

- [ ] **Step 5: Complete the substantive review envelope**

Obtain one normal and one adversarial Codex review plus one normal and one
adversarial sanitized Cursor/Grok consult. Give external consults source diffs,
tests, schema summaries, and nonclaims only—no screenshots, local paths,
runtime artifacts, credentials, or proprietary bytes. Resolve all
Critical/Important findings and rerun affected gates.

- [ ] **Step 6: Reconcile state, commit, and push green**

Record exact native scope/nonclaims, keep the shield live blocker, choose the
next actionable campaign slice from `goal.campaign.md`, parse changed JSON,
verify capability mirrors byte-identically, and commit. Push `main` without
force and verify `HEAD == origin/main`, divergence 0/0. No release or tag.

## Plan Self-Review

- Spec coverage: RID discovery, shared support, deterministic inputs, both UIA
  workflows, all eight visual states, schema/publication, outer lifecycle,
  native remediation, reviews, and baton reconciliation each map to a task.
- Placeholder scan: no placeholder or deferred implementation language remains.
- Type consistency: the evidence record, session, capture, publisher, and
  runner names are identical across their producer and consumer tasks.
