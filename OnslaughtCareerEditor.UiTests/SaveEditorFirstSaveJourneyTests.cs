using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.WinUI.Models;
using Onslaught___Career_Editor;
using System.Xml.Linq;

namespace OnslaughtCareerEditor.UiTests;

public class SaveEditorFirstSaveJourneyTests
{
    private static readonly XNamespace Xaml = "http://schemas.microsoft.com/winfx/2006/xaml";

    [TestCase(false, false, false, false, false, false, "Choose an existing .bes career save")]
    [TestCase(true, false, false, false, false, false, "Keep the suggested separate .bes output")]
    [TestCase(true, true, true, true, true, true, "Written copy ready")]
    [TestCase(true, true, true, true, true, false, "Written copy ready")]
    [TestCase(true, true, false, false, false, false, "Choose at least one change")]
    [TestCase(true, true, true, true, false, false, "Review Pending changes")]
    [TestCase(true, true, true, false, false, false, "Resolve the safety message")]
    public void Status_ProjectsTheNextStepInSafetyPrecedence(
        bool hasValidInput,
        bool hasValidOutput,
        bool hasSelectedChanges,
        bool canWrite,
        bool hasCompletedCurrentPlan,
        bool canRevealWrittenCopy,
        string expected)
    {
        var state = new SaveEditorFirstSaveJourneyState(
            hasValidInput,
            hasValidOutput,
            hasSelectedChanges,
            canWrite,
            hasCompletedCurrentPlan,
            canRevealWrittenCopy);

        Assert.That(SaveEditorFirstSaveJourneyText.BuildStatus(state), Does.Contain(expected));
    }

    [TestCase(0, 0, "No advanced overrides active")]
    [TestCase(1, 0, "1 mission override active")]
    [TestCase(0, 1, "1 category-kill override active")]
    [TestCase(2, 3, "2 mission overrides and 3 category-kill overrides active")]
    public void AdvancedStatus_ReportsVisibleSingularAndPluralCounts(int missions, int categories, string expected)
    {
        Assert.That(SaveEditorFirstSaveJourneyText.BuildAdvancedOverrideStatus(missions, categories), Is.EqualTo(expected));
    }

    [Test]
    public void Fingerprint_IsDictionaryOrderIndependentAndCoversEveryRequestField()
    {
        SavePatchRequest baseline = BuildRequest();
        string fingerprint = SaveEditorPlanFingerprint.Build(baseline);
        SavePatchRequest reordered = BuildRequest(
            levelRanks: new Dictionary<int, string> { [2] = "A", [1] = "S" },
            categoryKills: new Dictionary<int, int> { [8] = 900, [3] = 250 });

        Assert.That(SaveEditorPlanFingerprint.Build(reordered), Is.EqualTo(fingerprint));

        SavePatchRequest[] changed =
        [
            BuildRequest(input: "other.bes"),
            BuildRequest(output: "other-output.bes"),
            BuildRequest(rank: "A"),
            BuildRequest(useNewGoodies: true),
            BuildRequest(globalKills: 101),
            BuildRequest(patchNodes: false),
            BuildRequest(patchLinks: false),
            BuildRequest(patchGoodies: false),
            BuildRequest(patchKills: false),
            BuildRequest(levelRanks: new Dictionary<int, string> { [1] = "S", [2] = "B" }),
            BuildRequest(categoryKills: new Dictionary<int, int> { [3] = 251, [8] = 900 }),
        ];

        Assert.That(changed.Select(SaveEditorPlanFingerprint.Build), Has.All.Not.EqualTo(fingerprint));
    }

    [Test]
    public void IsInsideDirectory_IsCanonicalAndSeparatorAware()
    {
        string root = Path.Combine(Path.GetTempPath(), "onslaught-first-save");

        Assert.Multiple(() =>
        {
            Assert.That(SaveEditorPlanFingerprint.IsInsideDirectory(Path.Combine(root, "career.bes"), root), Is.True);
            Assert.That(SaveEditorPlanFingerprint.IsInsideDirectory(Path.Combine(root, "nested", "career.bes"), root), Is.True);
            Assert.That(SaveEditorPlanFingerprint.IsInsideDirectory(root + "-other" + Path.DirectorySeparatorChar + "career.bes", root), Is.False);
        });
    }

    [Test]
    public void OutputSuggestion_FollowsInputUntilUserChoosesAnExplicitDestination()
    {
        var state = new SaveEditorOutputSelectionState(string.Empty, OutputWasAutoSuggested: false);
        state = SaveEditorJourneyStateMachine.ApplyInputSuggestion(state, @"C:\app\A_patched.bes");
        Assert.That(state, Is.EqualTo(new SaveEditorOutputSelectionState(@"C:\app\A_patched.bes", true)));

        state = SaveEditorJourneyStateMachine.ApplyInputSuggestion(state, @"C:\app\B_patched.bes");
        Assert.That(state, Is.EqualTo(new SaveEditorOutputSelectionState(@"C:\app\B_patched.bes", true)));

        state = SaveEditorJourneyStateMachine.ApplyManualOutput(state, @"D:\chosen\career.bes");
        state = SaveEditorJourneyStateMachine.ApplyInputSuggestion(state, @"C:\app\C_patched.bes");
        Assert.That(state, Is.EqualTo(new SaveEditorOutputSelectionState(@"D:\chosen\career.bes", false)));
    }

    [Test]
    public void CustomPreset_RecomputesVisiblePresetWithoutMutatingEffectiveSections()
    {
        var safe = new SaveEditorSectionSelection(false, false, false, false, false);
        var quick = new SaveEditorSectionSelection(false, true, true, true, true);
        var custom = new SaveEditorSectionSelection(false, true, false, true, false);

        Assert.Multiple(() =>
        {
            Assert.That(SaveEditorJourneyStateMachine.ApplyPreset("CUSTOM", safe), Is.EqualTo(new SaveEditorPresetTransition(safe, "SAFE")));
            Assert.That(SaveEditorJourneyStateMachine.ApplyPreset("CUSTOM", quick), Is.EqualTo(new SaveEditorPresetTransition(quick, "QUICK")));
            Assert.That(SaveEditorJourneyStateMachine.ApplyPreset("CUSTOM", custom), Is.EqualTo(new SaveEditorPresetTransition(custom, "CUSTOM")));
            Assert.That(SaveEditorJourneyStateMachine.ApplyPreset("SAFE", quick).Selection, Is.EqualTo(safe));
            Assert.That(SaveEditorJourneyStateMachine.ApplyPreset("QUICK", safe).Selection, Is.EqualTo(quick));
        });
    }

    [Test]
    public void CompletionEvaluation_InvalidatesEveryRequestFieldAndGatesRevealByAppOwnedRoot()
    {
        string root = Path.Combine(Path.GetTempPath(), "onslaught-first-save-root");
        string appOwnedOutput = Path.Combine(root, "career_patched.bes");
        SavePatchRequest baseline = BuildRequest(input: Path.Combine(Path.GetTempPath(), "career.bes"), output: appOwnedOutput);
        var completion = SaveEditorJourneyStateMachine.RecordSuccessfulWrite(baseline, appOwnedOutput);

        SaveEditorCompletionEvaluation current = SaveEditorJourneyStateMachine.EvaluateCompletion(
            completion,
            baseline,
            outputExists: true,
            appOwnedRoot: root);
        Assert.That(current, Is.EqualTo(new SaveEditorCompletionEvaluation(true, true)));

        SavePatchRequest[] changed =
        [
            BuildRequest(input: Path.Combine(Path.GetTempPath(), "other.bes"), output: appOwnedOutput),
            BuildRequest(input: baseline.InputPath, output: Path.Combine(root, "other.bes")),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, rank: "A"),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, useNewGoodies: true),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, globalKills: 101),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, patchNodes: false),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, patchLinks: false),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, patchGoodies: false),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, patchKills: false),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, levelRanks: new Dictionary<int, string> { [1] = "B" }),
            BuildRequest(input: baseline.InputPath, output: appOwnedOutput, categoryKills: new Dictionary<int, int> { [3] = 251 }),
        ];

        Assert.That(
            changed.Select(request => SaveEditorJourneyStateMachine.EvaluateCompletion(completion, request, true, root).IsCurrent),
            Has.All.False);
        Assert.That(SaveEditorJourneyStateMachine.EvaluateCompletion(completion, baseline, false, root).IsCurrent, Is.False);

        string externalOutput = Path.Combine(Path.GetTempPath(), "external", "career.bes");
        SavePatchRequest externalRequest = BuildRequest(input: baseline.InputPath, output: externalOutput);
        SaveEditorCompletionState externalCompletion = SaveEditorJourneyStateMachine.RecordSuccessfulWrite(externalRequest, externalOutput);
        Assert.That(
            SaveEditorJourneyStateMachine.EvaluateCompletion(externalCompletion, externalRequest, true, root),
            Is.EqualTo(new SaveEditorCompletionEvaluation(true, false)));
    }

    [Test]
    public void ExplorerReveal_BuildsOneNonShellSelectArgumentForTheExactFullPath()
    {
        string path = Path.Combine(Path.GetTempPath(), "folder with spaces", "career.bes");

        System.Diagnostics.ProcessStartInfo startInfo = ExplorerRevealService.BuildStartInfo(path);

        Assert.Multiple(() =>
        {
            Assert.That(startInfo.FileName, Is.EqualTo("explorer.exe"));
            Assert.That(startInfo.UseShellExecute, Is.True);
            Assert.That(startInfo.ArgumentList, Is.EqualTo(new[] { $"/select,{Path.GetFullPath(path)}" }));
            Assert.That(startInfo.Arguments, Is.Empty);
        });
    }

    [Test]
    public void ExplorerReveal_ExecutesInjectedLauncherSuccessAndFailureWithoutStartingExplorer()
    {
        string path = Path.Combine(Path.GetTempPath(), "launcher seam", "career.bes");
        System.Diagnostics.ProcessStartInfo? captured = null;

        bool success = ExplorerRevealService.TryReveal(path, startInfo => captured = startInfo);
        bool failure = ExplorerRevealService.TryReveal(path, _ => throw new InvalidOperationException("synthetic launch failure"));

        Assert.Multiple(() =>
        {
            Assert.That(success, Is.True);
            Assert.That(failure, Is.False);
            Assert.That(captured, Is.Not.Null);
            Assert.That(captured!.FileName, Is.EqualTo("explorer.exe"));
            Assert.That(captured.UseShellExecute, Is.True);
            Assert.That(captured.ArgumentList, Is.EqualTo(new[] { $"/select,{Path.GetFullPath(path)}" }));
        });
    }

    [Test]
    public void RevealAttempt_PreservesCompletionOnLauncherFailureButClearsStalePreconditions()
    {
        SavePatchRequest request = BuildRequest();
        SaveEditorCompletionState completion = SaveEditorJourneyStateMachine.RecordSuccessfulWrite(request, request.OutputPath);

        Assert.Multiple(() =>
        {
            Assert.That(
                SaveEditorJourneyStateMachine.ApplyRevealAttempt(completion, preconditionsCurrent: true, launcherSucceeded: false),
                Is.SameAs(completion));
            Assert.That(
                SaveEditorJourneyStateMachine.ApplyRevealAttempt(completion, preconditionsCurrent: true, launcherSucceeded: true),
                Is.SameAs(completion));
            Assert.That(
                SaveEditorJourneyStateMachine.ApplyRevealAttempt(completion, preconditionsCurrent: false, launcherSucceeded: false),
                Is.Null);
        });
    }

    [Test]
    public void Xaml_StartsEmptyAndExposesTheGuidedJourneyWithStableAccessibleIds()
    {
        XDocument page = LoadSavesPage();
        XElement preset = FindNamedElement(page, "EditorPatchPresetComboBox");
        string[] labels = preset.Elements().Select(element => (string?)element.Attribute("Content") ?? string.Empty).ToArray();
        string[] tags = preset.Elements().Select(element => (string?)element.Attribute("Tag") ?? string.Empty).ToArray();
        XElement status = FindNamedElement(page, "SaveEditorFirstSaveStatus");
        XElement showWritten = FindNamedElement(page, "SaveEditorShowWrittenSaveButton");

        Assert.Multiple(() =>
        {
            Assert.That(labels, Is.EqualTo(new[] { "Start empty — choose sections", "Quick Unlock — all sections", "Custom selection" }));
            Assert.That(tags, Is.EqualTo(new[] { "SAFE", "QUICK", "CUSTOM" }));
            Assert.That(FindNamedElement(page, "SaveEditorFirstSaveGuide"), Is.Not.Null);
            Assert.That(page.ToString(), Does.Contain("Mission rank applies with Patch missions; NEW/OLD applies with Patch goodies; the kill value applies with Patch kill counts."));
            Assert.That((string?)status.Attribute("AutomationProperties.LiveSetting"), Is.EqualTo("Polite"));
            Assert.That((string?)showWritten.Attribute("Content"), Is.EqualTo("Show written save in File Explorer"));
            Assert.That((string?)showWritten.Attribute("AutomationProperties.Name"), Is.EqualTo("Show written save in File Explorer"));
            Assert.That((string?)showWritten.Attribute("IsEnabled"), Is.EqualTo("False"));
        });
    }

    [Test]
    public void Xaml_AdvancedOverridesStartCollapsedWithoutLosingExistingControls()
    {
        XDocument page = LoadSavesPage();
        XElement advanced = FindNamedElement(page, "SaveEditorAdvancedOverridesExpander");

        Assert.Multiple(() =>
        {
            Assert.That((string?)advanced.Attribute("IsExpanded"), Is.EqualTo("False"));
            Assert.That(FindNamedElement(page, "SaveEditorAdvancedOverridesStatus"), Is.Not.Null);
            foreach (string child in new[]
                     {
                         "SaveEditorSetAllRanksDefaultButton",
                         "SaveEditorClearMissionRanksButton",
                         "EditorMissionRanksListView",
                         "EditorCategoryKillsListView",
                     })
            {
                XElement element = FindNamedElement(page, child);
                Assert.That(advanced.Descendants().Contains(element), Is.True, $"{child} must remain inside the advanced expander");
            }
            Assert.That(
                (string?)FindNamedElement(page, "EditorMissionRanksListView").Attribute("AutomationProperties.AutomationId"),
                Is.EqualTo("EditorMissionRanksListView"));
            Assert.That(
                (string?)FindNamedElement(page, "EditorCategoryKillsListView").Attribute("AutomationProperties.AutomationId"),
                Is.EqualTo("EditorCategoryKillsListView"));
            Assert.That(
                (string?)FindNamedElement(page, "SaveEditorMissionOverridesHeading").Attribute("AutomationProperties.HeadingLevel"),
                Is.EqualTo("Level3"));
            Assert.That(
                (string?)FindNamedElement(page, "SaveEditorCategoryKillOverridesHeading").Attribute("AutomationProperties.HeadingLevel"),
                Is.EqualTo("Level3"));
            XElement categoryWrite = advanced.Descendants().Single(element =>
                element.Name.LocalName == "CheckBox"
                && string.Equals((string?)element.Attribute("Content"), "Write", StringComparison.Ordinal));
            Assert.That((string?)categoryWrite.Attribute("AutomationProperties.Name"), Is.EqualTo("{Binding CategoryName}"));
        });
    }

    [Test]
    public void CodeBehind_DefaultsSafeAndTracksSuggestedOutputWithoutOverwritingUserChoice()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");
        string presetMethod = ExtractMethod(code, "private void ApplyEditorPreset(string preset)", "private void UpdateEditorPresetSelection()");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("ApplyEditorPreset(\"SAFE\")"));
            Assert.That(code, Does.Contain("private bool _editorOutputWasAutoSuggested"));
            Assert.That(code, Does.Contain("private bool _suppressEditorOutputProvenance"));
            Assert.That(code, Does.Contain("private void SetEditorSuggestedOutputPath(string inputPath)"));
            Assert.That(code, Does.Contain("string.IsNullOrWhiteSpace(EditorOutputFileTextBox.Text) || _editorOutputWasAutoSuggested"));
            Assert.That(code, Does.Contain("SaveEditorJourneyStateMachine.ApplyInputSuggestion("));
            Assert.That(code, Does.Contain("SaveEditorJourneyStateMachine.ApplyManualOutput("));
            Assert.That(code, Does.Contain("SaveEditorJourneyStateMachine.ApplyPreset(preset, current)"));
            Assert.That(presetMethod, Does.Contain("SetEditorPresetSelection(transition.VisiblePreset)"));
        });
    }

    [Test]
    public void CodeBehind_BindsCompletionToSuccessfulCurrentPlanAndFailClosedExplorerReveal()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");
        string writeHandler = ExtractMethod(code, "private async void EditorPatchButton_Click", "private static string FormatEditorPatchResultForUi");
        string revealHandler = ExtractMethod(code, "private void SaveEditorShowWrittenSaveButton_Click", "private static string FormatEditorPatchResultForUi");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("private Models.SaveEditorCompletionState? _lastWrittenCompletion"));
            Assert.That(writeHandler, Does.Contain("result.Success && File.Exists(outputPath)"));
            Assert.That(writeHandler, Does.Contain("SaveEditorJourneyStateMachine.RecordSuccessfulWrite(request, outputPath)"));
            Assert.That(code, Does.Contain("SaveEditorJourneyStateMachine.EvaluateCompletion("));
            Assert.That(revealHandler, Does.Contain("File.Exists(outputPath)"));
            Assert.That(revealHandler, Does.Contain("ExplorerRevealService.TryReveal(outputPath)"));
            Assert.That(revealHandler, Does.Contain("clearCompletion: true"));
            Assert.That(revealHandler, Does.Contain("clearCompletion: false"));
            Assert.That(code, Does.Contain("Close the copied game"));
            Assert.That(code, Does.Contain("back up any save you replace"));
            Assert.That(code, Does.Contain("does not install"));
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
    public void CodeBehind_UpdatesLiveAndAdvancedAccessibilityWithoutResettingCollapsedValues()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");
        string advanced = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.SaveEditorAdvanced.cs");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("SaveEditorFirstSaveJourneyText.BuildStatus("));
            Assert.That(code, Does.Contain("if (!string.Equals(SaveEditorFirstSaveStatus.Text, journeyStatus"));
            Assert.That(code, Does.Contain("SaveEditorFirstSaveJourneyText.BuildAdvancedOverrideStatus("));
            Assert.That(code, Does.Contain("AutomationProperties.SetName("));
            Assert.That(code, Does.Contain("SaveEditorAdvancedOverridesExpander,"));
            Assert.That(advanced, Does.Not.Contain("SaveEditorAdvancedOverridesExpander.IsExpanded"));
        });
    }

    private static SavePatchRequest BuildRequest(
        string input = "career.bes",
        string output = "career_patched.bes",
        string rank = "S",
        bool useNewGoodies = false,
        int globalKills = 100,
        bool patchNodes = true,
        bool patchLinks = true,
        bool patchGoodies = true,
        bool patchKills = true,
        Dictionary<int, string>? levelRanks = null,
        Dictionary<int, int>? categoryKills = null)
    {
        return new SavePatchRequest
        {
            InputPath = input,
            OutputPath = output,
            Rank = rank,
            UseNewGoodiesInstead = useNewGoodies,
            GlobalKillCount = globalKills,
            PatchNodes = patchNodes,
            PatchLinks = patchLinks,
            PatchGoodies = patchGoodies,
            PatchKills = patchKills,
            LevelRanks = levelRanks ?? new Dictionary<int, string> { [1] = "S", [2] = "A" },
            PerCategoryKills = categoryKills ?? new Dictionary<int, int> { [3] = 250, [8] = 900 },
        };
    }

    private static XDocument LoadSavesPage()
    {
        return XDocument.Load(Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"));
    }

    private static string ReadRepoFile(params string[] parts)
    {
        return File.ReadAllText(Path.Combine(new[] { TestFixturePaths.RepoRoot }.Concat(parts).ToArray()));
    }

    private static string ExtractMethod(string source, string startMarker, string nextMarker)
    {
        int start = source.IndexOf(startMarker, StringComparison.Ordinal);
        int end = start >= 0 ? source.IndexOf(nextMarker, start + startMarker.Length, StringComparison.Ordinal) : -1;
        Assert.That(start, Is.GreaterThanOrEqualTo(0), $"Missing method marker: {startMarker}");
        Assert.That(end, Is.GreaterThan(start), $"Missing next method marker: {nextMarker}");
        return source[start..end];
    }

    private static XElement FindNamedElement(XContainer container, string name)
    {
        return container.Descendants().Single(element =>
            string.Equals((string?)element.Attribute(Xaml + "Name"), name, StringComparison.Ordinal)
            || string.Equals((string?)element.Attribute("AutomationProperties.AutomationId"), name, StringComparison.Ordinal));
    }

}
