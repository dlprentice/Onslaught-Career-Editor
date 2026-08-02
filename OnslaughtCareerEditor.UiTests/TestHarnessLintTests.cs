using System;
using System.IO;
using System.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Lint on the test harness. NOT product coverage, and counted as such would be a lie.
///
/// Every assertion in this file matches text inside another TEST file. That cannot tell you
/// anything about the app - it tells you something about how the app is being driven, which is a
/// different and much smaller claim. These lived scattered through the product suites, where they
/// inflated the number the project quotes about itself; `tools/enumerate_test_assertions.py`
/// classifies every test method in the suite and `--check` fails if harness lint is found outside
/// a class named for what it is.
///
/// They are kept rather than deleted because each one guards a real project rule that has no other
/// expression:
///   - a native harness may not use global synthetic input, because this project once sent stray
///     keystrokes into whatever window had focus at four in the morning;
///   - a save harness works from the tracked fixture, never from a real career on the machine;
///   - long pages are driven through UI Automation patterns rather than focus-dependent typing,
///     which is what makes those runs reproducible on a machine somebody is using;
///   - the media producer proves its captures without invoking playback.
///
/// If one of these ever fails, the fix is in the harness it names, not here.
/// </summary>
public class TestHarnessLintTests
{

    [Test]
    public void Producer_UsesExactUiaOnlyNoPlaybackBoundary()
    {
        string sourcePath = Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.UiTests",
            "WinUiMediaAssetNativeWorkflowTests.cs");
        string source = File.ReadAllText(sourcePath);

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Contain("ONSLAUGHT_MEDIA_ASSET_NATIVE_ACCEPTANCE_RUN_ID"));
            Assert.That(source, Does.Contain("ONSLAUGHT_MEDIA_ASSET_NATIVE_EXPECTED_PAYLOAD_SHA256"));
            Assert.That(source, Does.Contain("ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"));
            Assert.That(source, Does.Contain("HasPlaybackModulesLoaded"));
            Assert.That(source, Does.Contain("SelectionItem.Pattern.Select"));
            Assert.That(source, Does.Contain("MediaAssetNativeEvidenceAcceptance.Publish"));
            Assert.That(source, Does.Contain("ValidateApplicationPayload"));
            foreach (MediaAssetExpectedCapture capture in MediaAssetNativeEvidenceContract.ExpectedCaptures)
            {
                Assert.That(source, Does.Contain(capture.RelativeFileName));
            }

            Assert.That(source, Does.Not.Contain(".Click("));
            Assert.That(source, Does.Not.Contain("Keyboard"));
            Assert.That(source, Does.Not.Contain("Mouse"));
            Assert.That(source, Does.Not.Contain("MediaAudioPlayButton\").AsButton().Invoke"));
            Assert.That(source, Does.Not.Contain("MediaVideoPlayButton\").AsButton().Invoke"));
            Assert.That(source, Does.Not.Contain("MediaRevealVideoButton\").AsButton().Invoke"));
            Assert.That(source, Does.Not.Contain("AssetOpenExportButton\").AsButton().Invoke"));
        });
    }

    [Test]
    public void NativeSaveSmoke_UsesTrackedTempFixtureAndExplicitlySelectsOneSectionBeforeWrite()
    {
        string smoke = ReadRepoFile("OnslaughtCareerEditor.UiTests", "WinUiSaveAnalyzerInteractionSmokeTests.cs");
        string method = ExtractMethod(
            smoke,
            "public void SaveEditor_GuidesAndWritesCopiedGoldSaveThroughUi()",
            "public void ConfigurationEditor_ExposesModernControllerSetupWithoutOpeningBrowser()");
        string completionRealization = ExtractMethod(
            smoke,
            "private static void RealizeGuidedSaveCompletionRegion(",
            "private static bool ContainsRectangle(");

        int input = method.IndexOf("SetTextBox(window, \"SaveEditorInputFile\", inputCopyPath)", StringComparison.Ordinal);
        int startEmpty = method.IndexOf("Assert.That(patchButton.IsEnabled, Is.False", StringComparison.Ordinal);
        int section = method.IndexOf("SetCheckBox(window, \"SaveEditorPatchGoodiesCheckBox\", isChecked: true)", StringComparison.Ordinal);
        int ready = method.IndexOf("Retry.WhileFalse(() => patchButton.IsEnabled", StringComparison.Ordinal);
        int invoke = method.IndexOf("patchButton.AsButton().Invoke()", StringComparison.Ordinal);

        Assert.Multiple(() =>
        {
            Assert.That(method, Does.Contain("tests_shared"));
            Assert.That(method, Does.Contain("fixtures"));
            Assert.That(method, Does.Contain("gold_career_save.bin"));
            Assert.That(method, Does.Contain("Path.GetTempPath()"));
            Assert.That(method, Does.Not.Contain("ONSLAUGHT_WINUI_REAL_SAVE_PATH"));
            Assert.That(method, Does.Not.Contain("SetTextBox(window, \"SaveEditorOutputFile\""));
            Assert.That(input, Is.GreaterThanOrEqualTo(0));
            Assert.That(startEmpty, Is.GreaterThan(input));
            Assert.That(section, Is.GreaterThan(startEmpty));
            Assert.That(ready, Is.GreaterThan(section));
            Assert.That(invoke, Is.GreaterThan(ready));
            Assert.That(method, Does.Contain("AssertComboBoxSelectedText(window, \"SaveEditorPatchPresetComboBox\", \"Start empty — choose sections\")"));
            foreach (string sectionId in new[]
                     {
                         "SaveEditorPatchNodesCheckBox",
                         "SaveEditorPatchLinksCheckBox",
                         "SaveEditorPatchGoodiesCheckBox",
                         "SaveEditorPatchKillsCheckBox",
                     })
            {
                Assert.That(method, Does.Contain($"AssertCheckBoxState(window, \"{sectionId}\", isChecked: false)"));
            }
            Assert.That(method, Does.Contain("advancedExpander.Patterns.ExpandCollapse.Pattern.Expand()"));
            Assert.That(method, Does.Contain("ScrollIntoView(advancedExpander)"));
            Assert.That(method, Does.Contain("FindByAutomationId(window, \"SaveEditorScrollViewer\")"));
            Assert.That(method, Does.Contain("ScrollUntilAutomationIdIsRealized(window, editorScroll, \"SaveEditorMissionOverridesHeading\")"));
            Assert.That(method, Does.Contain("ScrollUntilAutomationIdIsRealized(window, editorScroll, \"SaveEditorSetAllRanksDefaultButton\")"));
            Assert.That(method, Does.Contain("ScrollUntilAutomationIdIsRealized(window, editorScroll, \"SaveEditorCategoryKillOverridesHeading\")"));
            Assert.That(method, Does.Contain("ScrollUntilAccessibleCheckBoxIsRealized(advancedExpander, editorScroll, \"Aircraft\")"));
            Assert.That(method, Does.Not.Contain("ScrollUntilAutomationIdIsRealized(window, editorScroll, \"EditorMissionRanksListView\")"));
            Assert.That(method, Does.Not.Contain("ScrollUntilAutomationIdIsRealized(window, editorScroll, \"EditorCategoryKillsListView\")"));
            Assert.That(method, Does.Contain("advancedExpander.Patterns.ExpandCollapse.Pattern.Collapse()"));
            Assert.That(method, Does.Contain("SaveEditorShowWrittenSaveButton"));
            Assert.That(method, Does.Contain("bool completionReady = Retry.WhileFalse("));
            Assert.That(method, Does.Contain("() => showWritten.IsEnabled"));
            Assert.That(method, Does.Contain("SaveEditorAdvancedOverridesExpander"));
            Assert.That(method, Does.Contain("SaveEditorAdvancedOverridesStatus"));
            Assert.That(method, Does.Contain("inputHashBefore"));
            Assert.That(method, Does.Contain("ReceiptBoundVisualCapture.Capture("));
            Assert.That(method, Does.Contain("SaveEditorOutputLog"));
            Assert.That(method, Does.Contain("SaveEditorShowWrittenSaveButton"));
            Assert.That(method, Does.Not.Contain("window.CaptureToFile("));
            Assert.That(method, Does.Not.Contain("NormalizeWindowForCapture("));
            Assert.That(method, Does.Not.Contain("ScrollIntoView(outputLog)"));
            Assert.That(method, Does.Contain("02-save-editor-patched-760.png"));
            Assert.That(method, Does.Not.Contain("FindByAutomationId(window, \"SaveEditorShowWrittenSaveButton\").AsButton().Invoke()"));
            Assert.That(completionRealization, Does.Contain("saveEditorScrollViewer.AutomationId"));
            Assert.That(completionRealization, Does.Contain("Is.EqualTo(\"SaveEditorScrollViewer\")"));
            Assert.That(completionRealization, Does.Contain("saveEditorScrollViewer.Patterns.Scroll.Pattern.Scroll("));
            Assert.That(completionRealization, Does.Not.Contain("ScrollIntoView("));
            Assert.That(completionRealization, Does.Contain("stableSamples >= 3"));
            Assert.That(completionRealization, Does.Contain("ContainsRectangle(windowBounds, outputBounds)"));
            Assert.That(completionRealization, Does.Contain("ContainsRectangle(windowBounds, revealBounds)"));
        });
    }

    [Test]
    public void NativeSaveLabHarness_UsesDeterministicInputsAndNoExternalOrSyntheticOsInput()
    {
        string path = Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.UiTests",
            "WinUiSaveLabNativeWorkflowTests.cs");
        Assert.That(File.Exists(path), Is.True, "The unattended Save Lab native producer must exist.");
        string source = File.ReadAllText(path);

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Contain("gold_career_save.bin"));
            Assert.That(source, Does.Contain("0C17E47D"));
            Assert.That(source, Does.Contain("A922C6BC"));
            Assert.That(source, Does.Contain("ONSLAUGHT_SAVE_LAB_NATIVE_ACCEPTANCE_RUN_ID"));
            Assert.That(source, Does.Contain("ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_EXE_SHA256"));
            Assert.That(source, Does.Contain("ONSLAUGHT_SAVE_LAB_NATIVE_EXPECTED_DLL_SHA256"));
            Assert.That(source, Does.Contain("ONSLAUGHT_GAME_DIR_CANDIDATES"));
            Assert.That(source, Does.Contain("ONSLAUGHT_STEAM_ROOT_CANDIDATES"));
            Assert.That(source, Does.Contain("save-ready-normal.png"));
            Assert.That(source, Does.Contain("save-complete-760.png"));
            Assert.That(source, Does.Contain("options-guidance-normal.png"));
            Assert.That(source, Does.Contain("options-complete-760.png"));
            Assert.That(source, Does.Not.Contain("ONSLAUGHT_WINUI_REAL_OPTIONS_PATH"));
            Assert.That(source, Does.Not.Contain("ExplorerRevealService.TryReveal"));
            Assert.That(source, Does.Not.Contain("Launcher.LaunchUriAsync"));
            Assert.That(source, Does.Not.Contain("Keyboard."));
            Assert.That(source, Does.Not.Contain("Mouse."));
        });
    }

    [Test]
    public void NativeSaveLabHarness_UsesScrollItemToRealizeZeroBoundMarkersBeforeDirectionalFallback()
    {
        string source = ReadRepoFile(
            "OnslaughtCareerEditor.UiTests",
            "WinUiSaveLabNativeWorkflowTests.cs");
        string realization = ExtractMethod(
            source,
            "private static void RealizeNamedRegion(",
            "private static string DescribeScrollState(");

        Assert.Multiple(() =>
        {
            Assert.That(realization, Does.Contain("current.Any(bounds => bounds.Width <= 0 || bounds.Height <= 0)"));
            Assert.That(realization, Does.Contain("element.Patterns.ScrollItem.IsSupported"));
            Assert.That(realization, Does.Contain("element.Patterns.ScrollItem.Pattern.ScrollIntoView()"));
            Assert.That(
                realization.IndexOf("element.Patterns.ScrollItem.Pattern.ScrollIntoView()", StringComparison.Ordinal),
                Is.LessThan(realization.IndexOf("bool above =", StringComparison.Ordinal)));
        });
    }

    [Test]
    public void NativeSaveLabHarness_UsesExplicitValuePatternWithoutTextBoxInputFallback()
    {
        string source = ReadRepoFile(
            "OnslaughtCareerEditor.UiTests",
            "WinUiSaveLabNativeWorkflowTests.cs");
        string setTextBox = ExtractMethod(
            source,
            "private static void SetTextBox(",
            "private static void SetCheckBox(");

        Assert.Multiple(() =>
        {
            Assert.That(setTextBox, Does.Contain("textBox.Patterns.Value.IsSupported"));
            Assert.That(setTextBox, Does.Contain("textBox.Patterns.Value.Pattern.SetValue(text)"));
            Assert.That(setTextBox, Does.Contain("textBox.Patterns.Value.Pattern.Value.Value"));
            Assert.That(setTextBox, Does.Not.Contain("textBox.Text = text"));
        });
    }

    [Test]
    public void NativeSaveLabHarness_DeclaresAndUsesSelectionPatternForPresetReadback()
    {
        string producer = ReadRepoFile(
            "OnslaughtCareerEditor.UiTests",
            "WinUiSaveLabNativeWorkflowTests.cs");
        string selectionReadback = ExtractMethod(
            producer,
            "private static void AssertComboBoxSelectedText(",
            "private static void InvokeButton(");

        Assert.Multiple(() =>
        {
            Assert.That(SaveLabNativeEvidenceContract.InteractionMode, Does.Contain("/Selection/"));
            Assert.That(selectionReadback, Does.Contain("comboBox.Patterns.Selection.IsSupported"));
            Assert.That(selectionReadback, Does.Contain("comboBox.SelectedItem?.Text"));
        });
    }

    [Test]
    public void NativeSaveLabHarness_UsesShortOwnedRootsForWindowsMutationGuardBudget()
    {
        string source = ReadRepoFile(
            "OnslaughtCareerEditor.UiTests",
            "WinUiSaveLabNativeWorkflowTests.cs");

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Contain("runName = $\"save-lab-x-{runId}\""));
            Assert.That(source, Does.Contain("Path.Combine(stagingDirectory, \"s\")"));
            Assert.That(source, Does.Contain("Path.Combine(stagingDirectory, \"o\")"));
            Assert.That(source, Does.Not.Contain("Path.Combine(stagingDirectory, \"save-session\")"));
            Assert.That(source, Does.Not.Contain("Path.Combine(stagingDirectory, \"options-session\")"));
        });
    }

    [Test]
    public void NativeSaveLabHarness_UsesExposedSafetyHintForInitialOptionsState()
    {
        string source = ReadRepoFile(
            "OnslaughtCareerEditor.UiTests",
            "WinUiSaveLabNativeWorkflowTests.cs");

        Assert.Multiple(() =>
        {
            Assert.That(source, Does.Not.Contain("\"ConfigurationPendingChanges\""));
            Assert.That(source, Does.Contain("Choose at least one settings override"));
            Assert.That(source, Does.Contain("!patchButton.IsEnabled"));
        });
    }

    [Test]
    public void RuntimeSmokes_DriveLongPagesThroughUiAutomationInsteadOfFocusDependentTyping()
    {
        string saveSmoke = ReadRepoFile("OnslaughtCareerEditor.UiTests", "WinUiSaveAnalyzerInteractionSmokeTests.cs");
        string patchSmoke = ReadRepoFile("OnslaughtCareerEditor.UiTests", "WinUiPatchBenchInteractionSmokeTests.cs");

        Assert.That(saveSmoke, Does.Contain("textBox.Text = text"));
        Assert.That(saveSmoke, Does.Contain("ScrollIntoView(outputLog)"));
        Assert.That(saveSmoke, Does.Not.Contain("textBox.Enter(text);"));
        Assert.That(patchSmoke, Does.Contain("ScrollIntoView(createButton)"));
        Assert.That(patchSmoke, Does.Contain("ScrollIntoView(operationLog)"));
        Assert.That(patchSmoke, Does.Contain("ScrollIntoView(restoreButton)"));
    }

    [Test]
    public void NativeSmoke_GatesDiagnosticsAndDistinguishesGlobalUiaExceptions()
    {
        string smoke = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.UiTests",
            "WinUiHomeNavigationSmokeTests.cs"));

        Assert.Multiple(() =>
        {
            Assert.That(smoke, Does.Contain("ONSLAUGHT_WINUI_TEST_FOCUS_DIAGNOSTICS"));
            Assert.That(smoke, Does.Contain("AssertHomeArrivalFocus("));
            Assert.That(smoke, Does.Contain("FocusedAutomationProbe"));
            Assert.That(smoke, Does.Contain("ExceptionType"));
            Assert.That(smoke, Does.Contain("home-arrival-focus.jsonl"));
            Assert.That(smoke, Does.Contain("ONSLAUGHT_WINUI_TEST_FOCUS_RUN_ID"));
            Assert.That(smoke, Does.Contain("FocusVerified"));
            Assert.That(smoke, Does.Contain("FocusedAutomationIdAtSample"));
            Assert.That(smoke, Does.Contain("InputEpochAtSample"));
            Assert.That(smoke, Does.Contain("FinalXamlFocusedAutomationId"));
            Assert.That(smoke, Does.Contain("HomeFocusEvidenceAcceptance.TryReadEndpointStatus"));
            Assert.That(smoke, Does.Contain("ExactWindowScopedMatch"));
        });
    }

    private static string ReadRepoFile(params string[] relativeParts)
    {
        string path = Path.Combine(relativeParts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }

    private static string ExtractMethod(string source, string startMarker, string nextMarker)
    {
        int start = source.IndexOf(startMarker, StringComparison.Ordinal);
        int end = start >= 0 ? source.IndexOf(nextMarker, start + startMarker.Length, StringComparison.Ordinal) : -1;
        Assert.That(start, Is.GreaterThanOrEqualTo(0), $"Missing method marker: {startMarker}");
        Assert.That(end, Is.GreaterThan(start), $"Missing next method marker: {nextMarker}");
        return source[start..end];
    }
}
