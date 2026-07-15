using System.Buffers.Binary;
using System.Drawing;
using System.Security.Cryptography;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

[NonParallelizable]
public class WinUiSaveLabNativeWorkflowTests
{
    private const string RunIdEnvironment = "ONSLAUGHT_SAVE_LAB_NATIVE_ACCEPTANCE_RUN_ID";
    private const string ExpectedExecutableHashEnvironment = "ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_EXE_SHA256";
    private const string ExpectedProductHashEnvironment = "ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_DLL_SHA256";
    private const string GameDirectoryCandidatesEnvironment = "ONSLAUGHT_GAME_DIR_CANDIDATES";
    private const string SteamRootCandidatesEnvironment = "ONSLAUGHT_STEAM_ROOT_CANDIDATES";
    private const string TrackedFixtureHashPrefix = "0C17E47D";
    private const string SyntheticOptionsHashPrefix = "A922C6BC";

    private static readonly Rectangle NormalBounds = new(16, 16, 1100, 900);
    private static readonly Rectangle CompactBounds = new(16, 16, 760, 820);

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Runs deterministic first-use Save Editor and Game Options workflows and publishes receipt-bound ignored/local evidence.")]
    [Apartment(ApartmentState.STA)]
    public void SaveLab_FirstUseAndOptions_PublishDeterministicNativeEvidence()
    {
        string? runId = Environment.GetEnvironmentVariable(RunIdEnvironment);
        Assert.That(Guid.TryParseExact(runId, "N", out _), Is.True, "Save Lab native acceptance requires the runner's invocation token.");
        Assert.That(runId, Is.EqualTo(runId!.ToLowerInvariant()), "Save Lab invocation token must be lowercase.");

        string expectedExecutableHash = RequireUpperSha256(ExpectedExecutableHashEnvironment);
        string expectedProductHash = RequireUpperSha256(ExpectedProductHashEnvironment);
        string repoRoot = TestFixturePaths.RepoRoot;
        string executablePath = Path.Combine(
            repoRoot,
            "OnslaughtCareerEditor.WinUI",
            "bin",
            "Debug",
            "net10.0-windows10.0.19041.0",
            "win-x64",
            "OnslaughtCareerEditor.WinUI.exe");
        string evidenceRoot = Path.Combine(repoRoot, "local-lab", "winui-save-lab-native-workflow");
        string runName = $"save-lab-{DateTime.UtcNow:yyyyMMddTHHmmssfffZ}-{runId}";
        string stagingDirectory = Path.Combine(evidenceRoot, $".{runName}.partial");
        string acceptedDirectory = Path.Combine(evidenceRoot, runName);
        Directory.CreateDirectory(stagingDirectory);

        try
        {
            (string saveInput, string optionsInput) = PrepareDeterministicInputs(repoRoot, stagingDirectory);
            var captures = new List<SaveLabCaptureEvidence>();
            var workflows = new List<SaveLabWorkflowEvidence>();

            RunSaveEditorWorkflow(
                executablePath,
                stagingDirectory,
                saveInput,
                expectedExecutableHash,
                expectedProductHash,
                captures,
                workflows);
            RunGameOptionsWorkflow(
                executablePath,
                stagingDirectory,
                optionsInput,
                expectedExecutableHash,
                expectedProductHash,
                captures,
                workflows);

            var manifest = new SaveLabAcceptanceManifest(
                SaveLabNativeEvidenceContract.SchemaVersion,
                runId!,
                SaveLabNativeEvidenceContract.InteractionMode,
                SaveLabNativeEvidenceContract.TrackedSaveFixtureSha256,
                new SyntheticOptionsEvidence(
                    SaveLabNativeEvidenceContract.ArtifactLength,
                    SaveLabNativeEvidenceContract.SyntheticOptionsVersionWord,
                    SaveLabNativeEvidenceContract.SyntheticOptionsSha256),
                captures,
                workflows);
            SaveLabNativeEvidenceAcceptance.Publish(stagingDirectory, acceptedDirectory, manifest);
        }
        catch
        {
            TryDeleteDirectory(stagingDirectory);
            throw;
        }
    }

    private static void RunSaveEditorWorkflow(
        string executablePath,
        string stagingDirectory,
        string inputCopyPath,
        string expectedExecutableHash,
        string expectedProductHash,
        ICollection<SaveLabCaptureEvidence> captures,
        ICollection<SaveLabWorkflowEvidence> workflows)
    {
        string sessionRoot = Path.Combine(stagingDirectory, "save-session");
        string appDataDirectory = Path.Combine(sessionRoot, "appdata");
        string emptySteamRoot = Path.Combine(sessionRoot, "empty-steam-root");
        Directory.CreateDirectory(emptySteamRoot);
        string outputPath = Path.Combine(
            appDataDirectory,
            "OnslaughtCareerEditor",
            "patched-output",
            "first-save-input_patched.bes");
        IReadOnlyDictionary<string, string> environment = BuildNoDetectionEnvironment(emptySteamRoot);
        string inputHashBefore = Hash(inputCopyPath);

        using var session = SaveLabNativeSession.Launch(
            executablePath,
            appDataDirectory,
            "1",
            expectedExecutableHash,
            expectedProductHash,
            environment);
        Window window = session.Window;
        FindByAutomationId(window, "SaveEditorInputFile");
        SetTextBox(window, "SaveEditorInputFile", inputCopyPath);

        AutomationElement patchButton = FindByAutomationId(window, "SaveEditorPatchButton");
        bool suggested = Retry.WhileFalse(
            () => string.Equals(TryGetTextBoxText(window, "SaveEditorOutputFile"), outputPath, StringComparison.OrdinalIgnoreCase),
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(suggested, Is.True, "Save Editor did not retain its app-owned separate output suggestion.");
        AssertComboBoxSelectedText(window, "SaveEditorPatchPresetComboBox", "Start empty — choose sections");
        AssertCheckBoxState(window, "SaveEditorPatchNodesCheckBox", false);
        AssertCheckBoxState(window, "SaveEditorPatchLinksCheckBox", false);
        AssertCheckBoxState(window, "SaveEditorPatchGoodiesCheckBox", false);
        AssertCheckBoxState(window, "SaveEditorPatchKillsCheckBox", false);
        Assert.Multiple(() =>
        {
            Assert.That(patchButton.IsEnabled, Is.False, "Start-empty Save Editor must not write without a selected section.");
            Assert.That(TryGetName(window, "SaveEditorFirstSaveStatus"), Does.Contain("Choose at least one change"));
            Assert.That(TryGetName(window, "SaveEditorAdvancedOverridesStatus"), Is.EqualTo("No advanced overrides active"));
        });
        AssertAdvancedRegionReachableAndCollapsed(window);

        string[] readyMarkers =
        [
            "SaveEditorInputFile",
            "SaveEditorOutputFile",
            "SaveEditorPatchPresetComboBox",
        ];
        captures.Add(Capture(
            session, "save-editor", "ready", "SaveEditorInputFile", NormalBounds,
            stagingDirectory, "save-ready-normal.png", "SaveEditorScrollViewer", readyMarkers));
        captures.Add(Capture(
            session, "save-editor", "ready", "SaveEditorInputFile", CompactBounds,
            stagingDirectory, "save-ready-760.png", "SaveEditorScrollViewer", readyMarkers));

        SetCheckBox(window, "SaveEditorPatchGoodiesCheckBox", isChecked: true);
        bool ready = Retry.WhileFalse(() => patchButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
        Assert.Multiple(() =>
        {
            Assert.That(ready, Is.True, "Selecting Goodies should make the copied-save write eligible.");
            Assert.That(TryGetName(window, "SaveEditorPendingChanges"), Does.Contain("goodies"));
            Assert.That(TryGetName(window, "SaveEditorSafetyHint"), Does.Contain("Save patching is ready"));
        });
        InvokeButton(patchButton, "SaveEditorPatchButton");

        bool outputReady = Retry.WhileFalse(
            () => File.Exists(outputPath) &&
                  (TryGetTextBoxText(window, "SaveEditorOutputLog") ?? string.Empty)
                      .Contains("Successfully patched", StringComparison.OrdinalIgnoreCase),
            TimeSpan.FromSeconds(15)).Success;
        Assert.That(outputReady, Is.True, "Save Editor did not write and report its deterministic copied output.");
        string outputLog = TryGetTextBoxText(window, "SaveEditorOutputLog") ?? string.Empty;
        string inputHashAfter = Hash(inputCopyPath);
        string outputHash = Hash(outputPath);
        SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(outputPath);
        Assert.Multiple(() =>
        {
            Assert.That(inputHashAfter, Is.EqualTo(inputHashBefore), "Save Editor mutated its deterministic input copy.");
            Assert.That(outputHash, Is.Not.EqualTo(inputHashBefore), "Save Editor output must differ from its input.");
            Assert.That(new FileInfo(outputPath).Length, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
            Assert.That(analysis.IsValid, Is.True, analysis.ErrorMessage);
            Assert.That(analysis.GoodieStates.Where(row => row.IsDisplayable).Select(row => row.RawState), Has.All.EqualTo(3u));
            Assert.That(outputLog, Does.Contain("selected output file"));
            Assert.That(outputLog, Does.Not.Contain(inputCopyPath));
            Assert.That(outputLog, Does.Not.Contain(outputPath));
        });
        AutomationElement showWritten = FindByAutomationId(window, "SaveEditorShowWrittenSaveButton");
        bool completed = Retry.WhileFalse(
            () => showWritten.IsEnabled &&
                  (TryGetName(window, "SaveEditorFirstSaveStatus") ?? string.Empty)
                      .Contains("Written copy ready", StringComparison.Ordinal),
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(completed, Is.True, "Save Editor completion must expose—but not invoke—the app-owned reveal action.");

        string[] completeMarkers = ["SaveEditorOutputLog", "SaveEditorShowWrittenSaveButton"];
        captures.Add(Capture(
            session, "save-editor", "complete", "SaveEditorShowWrittenSaveButton", NormalBounds,
            stagingDirectory, "save-complete-normal.png", "SaveEditorScrollViewer", completeMarkers));
        captures.Add(Capture(
            session, "save-editor", "complete", "SaveEditorShowWrittenSaveButton", CompactBounds,
            stagingDirectory, "save-complete-760.png", "SaveEditorScrollViewer", completeMarkers));

        workflows.Add(new SaveLabWorkflowEvidence(
            "save-editor",
            SaveLabNativeVisualCapture.ToEvidence(session.Identity),
            Relative(stagingDirectory, inputCopyPath),
            inputHashBefore,
            inputHashAfter,
            Relative(stagingDirectory, outputPath),
            outputHash,
            checked((int)new FileInfo(outputPath).Length),
            InputPreserved: true,
            OutputValidated: analysis.IsValid,
            Readback: "goodies-old-output-valid"));
    }

    private static void RunGameOptionsWorkflow(
        string executablePath,
        string stagingDirectory,
        string inputCopyPath,
        string expectedExecutableHash,
        string expectedProductHash,
        ICollection<SaveLabCaptureEvidence> captures,
        ICollection<SaveLabWorkflowEvidence> workflows)
    {
        string sessionRoot = Path.Combine(stagingDirectory, "options-session");
        string appDataDirectory = Path.Combine(sessionRoot, "appdata");
        string emptySteamRoot = Path.Combine(sessionRoot, "empty-steam-root");
        Directory.CreateDirectory(emptySteamRoot);
        string outputPath = Path.Combine(
            appDataDirectory,
            "OnslaughtCareerEditor",
            "patched-output",
            "synthetic-options_patched.bea");
        IReadOnlyDictionary<string, string> environment = BuildNoDetectionEnvironment(emptySteamRoot);
        string inputHashBefore = Hash(inputCopyPath);

        using var session = SaveLabNativeSession.Launch(
            executablePath,
            appDataDirectory,
            "2",
            expectedExecutableHash,
            expectedProductHash,
            environment);
        Window window = session.Window;
        AutomationElement guideButton = FindByAutomationId(window, "OpenZigguratControllerGuideButton");
        Assert.Multiple(() =>
        {
            Assert.That(TryGetName(window, "ModernControllerSetupHeading"), Does.Contain("Modern controller setup"));
            Assert.That(TryGetName(window, "ModernControllerSetupBoundary"), Does.Contain("does not configure Steam Input"));
            Assert.That(guideButton.IsEnabled, Is.True);
        });

        string[] guidanceMarkers =
        [
            "ModernControllerSetupHeading",
            "ModernControllerSetupBoundary",
            "OpenZigguratControllerGuideButton",
        ];
        captures.Add(Capture(
            session, "game-options", "guidance", "OpenZigguratControllerGuideButton", NormalBounds,
            stagingDirectory, "options-guidance-normal.png", "ConfigurationEditorScrollViewer", guidanceMarkers));
        captures.Add(Capture(
            session, "game-options", "guidance", "OpenZigguratControllerGuideButton", CompactBounds,
            stagingDirectory, "options-guidance-760.png", "ConfigurationEditorScrollViewer", guidanceMarkers));

        SetTextBox(window, "ConfigurationInputFile", inputCopyPath);
        AutomationElement patchButton = FindByAutomationId(window, "ConfigurationPatchButton");
        bool inputLoaded = Retry.WhileFalse(
            () => string.Equals(TryGetTextBoxText(window, "ConfigurationOutputFile"), outputPath, StringComparison.OrdinalIgnoreCase) &&
                  (TryGetName(window, "ConfigurationPendingChanges") ?? string.Empty)
                      .Contains("No pending configuration changes", StringComparison.Ordinal) &&
                  !patchButton.IsEnabled,
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(inputLoaded, Is.True, "Game Options did not load its deterministic input with an app-owned separate output and no pending changes.");

        SetTextBox(window, "ConfigurationControllerConfigP1", "1");
        bool ready = Retry.WhileFalse(
            () => patchButton.IsEnabled &&
                  (TryGetName(window, "ConfigurationSafetyHint") ?? string.Empty)
                      .Contains("Game options patching is ready", StringComparison.Ordinal),
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(ready, Is.True, "The one-field Game Options override did not become eligible.");
        InvokeButton(patchButton, "ConfigurationPatchButton");

        bool outputReady = Retry.WhileFalse(
            () => File.Exists(outputPath) &&
                  (TryGetTextBoxText(window, "ConfigurationOutputLog") ?? string.Empty)
                      .Contains("Successfully patched", StringComparison.OrdinalIgnoreCase),
            TimeSpan.FromSeconds(15)).Success;
        Assert.That(outputReady, Is.True, "Game Options did not write and report its deterministic copied output.");
        string outputLog = TryGetTextBoxText(window, "ConfigurationOutputLog") ?? string.Empty;
        string inputHashAfter = Hash(inputCopyPath);
        string outputHash = Hash(outputPath);
        ConfigurationSnapshot snapshot = ConfigurationEditorService.LoadConfigurationSnapshot(outputPath);
        Assert.Multiple(() =>
        {
            Assert.That(inputHashAfter, Is.EqualTo(inputHashBefore), "Game Options mutated its deterministic input copy.");
            Assert.That(outputHash, Is.Not.EqualTo(inputHashBefore), "Game Options output must differ from its input.");
            Assert.That(new FileInfo(outputPath).Length, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
            Assert.That(snapshot.ControllerConfigP1, Is.EqualTo(1u));
            Assert.That(outputLog, Does.Contain("selected output file"));
            Assert.That(outputLog, Does.Not.Contain(inputCopyPath));
            Assert.That(outputLog, Does.Not.Contain(outputPath));
        });

        string[] completeMarkers =
        [
            "ConfigurationSafetyHint",
            "ConfigurationPatchButton",
            "ConfigurationOutputLog",
        ];
        captures.Add(Capture(
            session, "game-options", "complete", "ConfigurationPatchButton", NormalBounds,
            stagingDirectory, "options-complete-normal.png", "ConfigurationEditorScrollViewer", completeMarkers));
        captures.Add(Capture(
            session, "game-options", "complete", "ConfigurationPatchButton", CompactBounds,
            stagingDirectory, "options-complete-760.png", "ConfigurationEditorScrollViewer", completeMarkers));

        workflows.Add(new SaveLabWorkflowEvidence(
            "game-options",
            SaveLabNativeVisualCapture.ToEvidence(session.Identity),
            Relative(stagingDirectory, inputCopyPath),
            inputHashBefore,
            inputHashAfter,
            Relative(stagingDirectory, outputPath),
            outputHash,
            checked((int)new FileInfo(outputPath).Length),
            InputPreserved: true,
            OutputValidated: true,
            Readback: "controller-config-p1=1"));
    }

    private static SaveLabCaptureEvidence Capture(
        SaveLabNativeSession session,
        string workflow,
        string phase,
        string focusAutomationId,
        Rectangle bounds,
        string stagingDirectory,
        string fileName,
        string scrollHostAutomationId,
        IReadOnlyList<string> markers)
    {
        return SaveLabNativeVisualCapture.Capture(
            session,
            workflow,
            phase,
            focusAutomationId,
            bounds,
            Path.Combine(stagingDirectory, fileName),
            markers,
            () => RealizeNamedRegion(session.Window, scrollHostAutomationId, markers));
    }

    private static IReadOnlyDictionary<string, string> BuildNoDetectionEnvironment(string emptySteamRoot) =>
        new Dictionary<string, string>(StringComparer.Ordinal)
        {
            [GameDirectoryCandidatesEnvironment] = string.Empty,
            [SteamRootCandidatesEnvironment] = Path.GetFullPath(emptySteamRoot),
        };

    private static (string SaveInput, string OptionsInput) PrepareDeterministicInputs(
        string repoRoot,
        string stagingDirectory)
    {
        string fixture = Path.Combine(repoRoot, "tests_shared", "fixtures", "gold_career_save.bin");
        Assert.That(File.Exists(fixture), Is.True, "Tracked gold_career_save.bin is required.");
        string fixtureHash = Hash(fixture);
        Assert.Multiple(() =>
        {
            Assert.That(fixtureHash, Does.StartWith(TrackedFixtureHashPrefix));
            Assert.That(fixtureHash, Is.EqualTo(SaveLabNativeEvidenceContract.TrackedSaveFixtureSha256));
            Assert.That(new FileInfo(fixture).Length, Is.EqualTo(SaveLabNativeEvidenceContract.ArtifactLength));
        });

        string fixtureDirectory = Path.Combine(stagingDirectory, "fixtures");
        Directory.CreateDirectory(fixtureDirectory);
        string saveInput = Path.Combine(fixtureDirectory, "first-save-input.bes");
        File.Copy(fixture, saveInput, overwrite: false);

        byte[] syntheticOptions = new byte[SaveLabNativeEvidenceContract.ArtifactLength];
        BinaryPrimitives.WriteUInt16LittleEndian(
            syntheticOptions.AsSpan(0, sizeof(ushort)),
            SaveLabNativeEvidenceContract.SyntheticOptionsVersionWord);
        string optionsInput = Path.Combine(fixtureDirectory, "synthetic-options.bea");
        File.WriteAllBytes(optionsInput, syntheticOptions);
        string syntheticHash = Hash(optionsInput);
        Assert.Multiple(() =>
        {
            Assert.That(syntheticHash, Does.StartWith(SyntheticOptionsHashPrefix));
            Assert.That(syntheticHash, Is.EqualTo(SaveLabNativeEvidenceContract.SyntheticOptionsSha256));
            Assert.That(BesFilePatcher.AnalyzeSave(optionsInput).IsValid, Is.True);
        });
        return (saveInput, optionsInput);
    }

    private static void AssertAdvancedRegionReachableAndCollapsed(Window window)
    {
        AutomationElement expander = FindByAutomationId(window, "SaveEditorAdvancedOverridesExpander");
        Assert.That(expander.Patterns.ExpandCollapse.IsSupported, Is.True);
        Assert.That(expander.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value.ToString(), Is.EqualTo("Collapsed"));
        expander.Patterns.ExpandCollapse.Pattern.Expand();
        Assert.That(
            Retry.WhileFalse(
                () => expander.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value.ToString() == "Expanded" &&
                      TryFindByAutomationId(window, "SaveEditorMissionOverridesHeading") is not null,
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "Save Editor advanced region was not reachable through ExpandCollapsePattern.");
        expander.Patterns.ExpandCollapse.Pattern.Collapse();
        Assert.That(
            Retry.WhileFalse(
                () => expander.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value.ToString() == "Collapsed",
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "Save Editor advanced region did not return to collapsed first-use state.");
    }

    private static void RealizeNamedRegion(
        Window window,
        string scrollHostAutomationId,
        IReadOnlyList<string> markerAutomationIds)
    {
        AutomationElement scrollHost = FindByAutomationId(window, scrollHostAutomationId);
        Assert.That(scrollHost.Patterns.Scroll.IsSupported, Is.True, $"{scrollHostAutomationId} must expose ScrollPattern.");
        Assert.That(
            scrollHost.Patterns.Scroll.Pattern.HorizontallyScrollable.Value,
            Is.False,
            $"{scrollHostAutomationId} must not expose horizontal scrolling at the accepted widths.");

        IReadOnlyList<Rectangle>? previous = null;
        int stableSamples = 0;
        bool realized = Retry.WhileFalse(
            () =>
            {
                Rectangle windowBounds = window.BoundingRectangle;
                AutomationElement[] elements = markerAutomationIds
                    .Select(id => TryFindByAutomationId(window, id))
                    .Where(element => element is not null)
                    .Cast<AutomationElement>()
                    .ToArray();
                if (elements.Length != markerAutomationIds.Count)
                {
                    Scroll(scrollHost, ScrollAmount.LargeIncrement);
                    stableSamples = 0;
                    previous = null;
                    return false;
                }

                Rectangle[] current = elements.Select(element => element.BoundingRectangle).ToArray();
                bool allInside = current.All(bounds => Contains(windowBounds, bounds));
                if (!allInside)
                {
                    bool above = current.Any(bounds => bounds.Top < windowBounds.Top);
                    Scroll(scrollHost, above ? ScrollAmount.LargeDecrement : ScrollAmount.LargeIncrement);
                    stableSamples = 0;
                    previous = null;
                    return false;
                }

                if (previous is not null && current.SequenceEqual(previous))
                {
                    stableSamples++;
                }
                else
                {
                    stableSamples = 0;
                }
                previous = current;
                return stableSamples >= 2;
            },
            TimeSpan.FromSeconds(10),
            TimeSpan.FromMilliseconds(100)).Success;
        Assert.That(
            realized,
            Is.True,
            $"Markers for {scrollHostAutomationId} were not simultaneously visible and stable in the exact Toolkit HWND.");
    }

    private static void Scroll(AutomationElement scrollHost, ScrollAmount amount)
    {
        try
        {
            scrollHost.Patterns.Scroll.Pattern.Scroll(ScrollAmount.NoAmount, amount);
        }
        catch
        {
            // Bounded realization owns the final exact failure.
        }
    }

    private static bool Contains(Rectangle container, Rectangle child) =>
        child.Width > 0 && child.Height > 0 &&
        child.Left >= container.Left && child.Top >= container.Top &&
        child.Right <= container.Right && child.Bottom <= container.Bottom;

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        textBox.Focus();
        textBox.Text = text;
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(textBox.Text, text, StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            $"Expected {automationId} to accept the requested ValuePattern text.");
    }

    private static void SetCheckBox(Window window, string automationId, bool isChecked)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Patterns.Toggle.IsSupported, Is.True, $"{automationId} must expose TogglePattern.");
        bool IsOn() => element.Patterns.Toggle.Pattern.ToggleState.Value == ToggleState.On;
        if (IsOn() != isChecked)
        {
            element.Patterns.Toggle.Pattern.Toggle();
        }
        Assert.That(Retry.WhileFalse(() => IsOn() == isChecked, TimeSpan.FromSeconds(5)).Success, Is.True);
    }

    private static void AssertCheckBoxState(Window window, string automationId, bool isChecked)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Patterns.Toggle.IsSupported, Is.True);
        ToggleState expected = isChecked ? ToggleState.On : ToggleState.Off;
        Assert.That(element.Patterns.Toggle.Pattern.ToggleState.Value, Is.EqualTo(expected));
    }

    private static void AssertComboBoxSelectedText(Window window, string automationId, string expected)
    {
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(
                    FindByAutomationId(window, automationId).AsComboBox().SelectedItem?.Text,
                    expected,
                    StringComparison.Ordinal),
                TimeSpan.FromSeconds(10)).Success,
            Is.True,
            $"Expected {automationId} selected item: {expected}");
    }

    private static void InvokeButton(AutomationElement button, string automationId)
    {
        Assert.That(button.Patterns.Invoke.IsSupported, Is.True, $"{automationId} must expose InvokePattern.");
        button.Patterns.Invoke.Pattern.Invoke();
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => TryFindByAutomationId(window, automationId),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected Save Lab automation element: {automationId}");
        return element!;
    }

    private static AutomationElement? TryFindByAutomationId(Window window, string automationId)
    {
        try
        {
            return window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
        }
        catch
        {
            return null;
        }
    }

    private static string? TryGetName(Window window, string automationId)
    {
        try
        {
            return FindByAutomationId(window, automationId).Name;
        }
        catch
        {
            return null;
        }
    }

    private static string? TryGetTextBoxText(Window window, string automationId)
    {
        try
        {
            return FindByAutomationId(window, automationId).AsTextBox().Text;
        }
        catch
        {
            return null;
        }
    }

    private static string RequireUpperSha256(string environmentVariable)
    {
        string? value = Environment.GetEnvironmentVariable(environmentVariable);
        Assert.That(
            value,
            Does.Match("^[0-9A-F]{64}$"),
            $"Save Lab native acceptance requires an uppercase SHA-256 in {environmentVariable}.");
        return value!;
    }

    private static string Hash(string path) =>
        Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));

    private static string Relative(string root, string path) =>
        Path.GetRelativePath(root, path).Replace(Path.DirectorySeparatorChar, '/');

    private static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch
        {
            // The outer runner owns bounded rollback and final process/file census.
        }
    }
}
