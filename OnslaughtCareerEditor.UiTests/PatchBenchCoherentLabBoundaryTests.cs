using System;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchCoherentLabBoundaryTests
{
    private static readonly XNamespace Xaml = "http://schemas.microsoft.com/winfx/2006/xaml";

    [Test]
    public void SpecialistControls_AreDescendantsOfOneCollapsedOuterLab()
    {
        XDocument document = LoadPage();
        XElement lab = FindNamedElement(document, "PatchBenchLabExpander");

        Assert.Multiple(() =>
        {
            Assert.That((string?)lab.Attribute("IsExpanded"), Is.EqualTo("False"));
            foreach (string name in new[]
                     {
                         "PatchBenchStableDefaultsButton",
                         "PatchBenchPatchRows",
                         "PatchBenchAdvancedLaunchOptionsExpander",
                         "PatchBenchOnlineTechnicalDetailsExpander",
                         "PatchBenchCreateMusicSwapPresetComboBox",
                         "PatchBenchStageCopiedTrackSwapButton",
                         "PatchBenchAdvancedTechnicalExpander",
                     })
            {
                Assert.That(FindNamedElement(lab, name), Is.Not.Null, $"{name} must be inside the outer Lab");
            }
        });
    }

    [Test]
    public void NormalSafeCopyJourney_RemainsOutsideOuterLab()
    {
        XDocument document = LoadPage();
        XElement lab = FindNamedElement(document, "PatchBenchLabExpander");

        Assert.Multiple(() =>
        {
            foreach (string name in new[]
                     {
                         "PatchBenchSafeCopySourceStatus",
                         "PatchBenchPrepareCopiedProfileButton",
                         "PatchBenchCopiedProfileReceipt",
                         "PatchBenchLaunchCopiedProfileButton",
                         "PatchBenchStopCopiedProfileButton",
                         "PatchBenchLocalMultiplayerProbeButton",
                         "PatchBenchLabSelectionStatus",
                     })
            {
                XElement element = FindNamedElement(document, name);
                Assert.That(lab.Descendants().Contains(element), Is.False, $"{name} must stay in the normal journey");
            }
        });
    }

    [Test]
    public void Lab_UsesFiveCollapsedPurposeGroupsWithStableAutomationIds()
    {
        XDocument document = LoadPage();
        XElement lab = FindNamedElement(document, "PatchBenchLabExpander");

        Assert.Multiple(() =>
        {
            foreach (string name in new[]
                     {
                         "PatchBenchLabPatchExperimentsExpander",
                         "PatchBenchLabLaunchControlExpander",
                         "PatchBenchLabOnlineResearchExpander",
                         "PatchBenchLabMusicExperimentsExpander",
                         "PatchBenchLabBeaDiagnosticsExpander",
                     })
            {
                XElement group = FindNamedElement(lab, name);
                Assert.That((string?)group.Attribute("AutomationProperties.AutomationId"), Is.EqualTo(name));
                Assert.That((string?)group.Attribute("IsExpanded"), Is.EqualTo("False"));
            }
        });
    }

    [Test]
    public void PageProjection_CountsOnlyNextCopyInputsAndRefreshesLiveStatus()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");

        Assert.Multiple(() =>
        {
            Assert.That(code, Does.Contain("private PatchBenchLabCreationInputState BuildLabCreationInputState()"));
            Assert.That(code, Does.Contain("private int CountSelectedLaunchModifiers()"));
            Assert.That(code, Does.Contain("!_requiredCompatibilityKeys.Contains(key)"));
            Assert.That(code, Does.Contain("PatchBenchLabSelectionStatus.Text = PatchBenchLabCreationInputText.BuildStatus("));
            Assert.That(code, Does.Contain("AutomationProperties.SetName(PatchBenchLabSelectionStatus, PatchBenchLabSelectionStatus.Text);"));
        });

        string builder = ExtractMethod(
            code,
            "private PatchBenchLabCreationInputState BuildLabCreationInputState()",
            "private int CountSelectedLaunchModifiers()");
        Assert.Multiple(() =>
        {
            Assert.That(builder, Does.Contain("PatchBenchPersistControllerConfigOption"));
            Assert.That(builder, Does.Contain("PatchBenchSharpenMouseLookOption"));
            Assert.That(builder, Does.Contain("PatchBenchInvertWalkerYOption"));
            Assert.That(builder, Does.Contain("PatchBenchInvertFlightYOption"));
            Assert.That(builder, Does.Contain("GetSelectedCreateMusicSwapPresetId()"));
            Assert.That(builder, Does.Not.Contain("Online"));
            Assert.That(builder, Does.Not.Contain("StageMusic"));
            Assert.That(builder, Does.Not.Contain("RestoreMusic"));
            Assert.That(builder, Does.Not.Contain("ExePathTextBox"));
        });
    }

    [Test]
    public void BothCreateButtons_UseFreshCreationInputSummaryBeforeConfirmationAndMutation()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string handler = ExtractMethod(
            code,
            "private async void PrepareCopiedProfileButton_Click",
            "private async void LaunchCopiedProfileButton_Click");

        int readinessGuard = handler.IndexOf("if (!readiness.CanCreate)", StringComparison.Ordinal);
        int guardedReturn = handler.IndexOf("return;", readinessGuard, StringComparison.Ordinal);
        int summaryState = handler.IndexOf("PatchBenchLabCreationInputState creationInputState = BuildLabCreationInputState();", StringComparison.Ordinal);
        int confirmationSummary = handler.IndexOf("PatchBenchLabCreationInputText.BuildConfirmationSection(creationInputState)", StringComparison.Ordinal);
        int confirmation = handler.IndexOf("ConfirmAsync(", StringComparison.Ordinal);
        int preflight = handler.IndexOf("GameProfilePreflightService.PrepareWindowedCompatibilityProfile", StringComparison.Ordinal);

        Assert.Multiple(() =>
        {
            Assert.That(Regex.Matches(xaml, "Click=\"PrepareCopiedProfileButton_Click\"").Count, Is.EqualTo(2));
            Assert.That(guardedReturn, Is.GreaterThan(readinessGuard));
            Assert.That(summaryState, Is.GreaterThan(guardedReturn));
            Assert.That(confirmationSummary, Is.GreaterThan(summaryState));
            Assert.That(confirmation, Is.GreaterThan(summaryState));
            Assert.That(preflight, Is.GreaterThan(confirmation));
            Assert.That(handler[..confirmation], Does.Not.Contain("Directory.CreateDirectory"));
            Assert.That(handler[..confirmation], Does.Not.Contain("File.Copy"));
        });
    }

    [Test]
    public void Create_UsesImmutableCopiedOptionsSnapshotAfterConfirmation()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string handler = ExtractMethod(
            code,
            "private async void PrepareCopiedProfileButton_Click",
            "private async void LaunchCopiedProfileButton_Click");

        int confirmation = handler.IndexOf("ConfirmAsync(", StringComparison.Ordinal);
        string beforeConfirmation = handler[..confirmation];
        string afterConfirmation = handler[confirmation..];

        Assert.Multiple(() =>
        {
            Assert.That(beforeConfirmation, Does.Contain("uint? persistedControllerConfig ="));
            Assert.That(beforeConfirmation, Does.Contain("float? mouseLookSensitivity ="));
            Assert.That(beforeConfirmation, Does.Contain("bool invertWalkerY ="));
            Assert.That(beforeConfirmation, Does.Contain("bool invertFlightY ="));
            Assert.That(afterConfirmation, Does.Not.Contain("PatchBenchPersistControllerConfigOption.IsChecked"));
            Assert.That(afterConfirmation, Does.Not.Contain("GetSelectedControllerConfigurationPreset()"));
            Assert.That(afterConfirmation, Does.Not.Contain("GetSelectedMouseLookSensitivityPreset()"));
            Assert.That(afterConfirmation, Does.Not.Contain("PatchBenchInvertWalkerYOption.IsChecked"));
            Assert.That(afterConfirmation, Does.Not.Contain("PatchBenchInvertFlightYOption.IsChecked"));
        });
    }

    [Test]
    public void NarrowTwoColumnActionButtons_WrapCompleteLabelsAt760Pixels()
    {
        XDocument document = LoadPage();

        Assert.Multiple(() =>
        {
            foreach ((string automationId, string label) in new[]
                     {
                         ("PatchBenchWindowedPresetButton", "Reset to Compatibility Copy"),
                         ("PatchBenchClearSelectionButton", "Clear optional mods"),
                         ("PatchBenchAddVersionMarkerButton", "Add PATCHED marker"),
                         ("PatchBenchClearVersionMarkerButton", "Clear PATCHED marker"),
                         ("PatchBenchAddGoodiesPreviewButton", "Add Goodies wall preview"),
                         ("PatchBenchClearGoodiesPreviewButton", "Clear Goodies wall preview"),
                         ("PatchBenchStableDefaultsButton", "Legacy graphics-default recipe"),
                         ("PatchBenchEnhancedPreviewProfileButton", "Enhanced Profile Preview"),
                         ("PatchBenchModernGraphicsPresetButton", "Graphics flag rows only"),
                         ("PatchBenchDebugCameraPreviewProfileButton", "Debug Camera Preview"),
                     })
            {
                XElement button = document.Descendants()
                    .Single(element => string.Equals(
                        (string?)element.Attribute("AutomationProperties.AutomationId"),
                        automationId,
                        StringComparison.Ordinal));
                XElement labelElement = button.Elements().Single();
                Assert.That((string?)button.Attribute("MinHeight"), Is.EqualTo("56"), $"{automationId} needs equal wrapped height");
                Assert.That((string?)labelElement.Attribute("Text"), Is.EqualTo(label));
                Assert.That((string?)labelElement.Attribute("TextWrapping"), Is.EqualTo("WrapWholeWords"));
                Assert.That((string?)labelElement.Attribute("TextAlignment"), Is.EqualTo("Center"));
            }
        });
    }

    [Test]
    public void NativeSmoke_RejectsWinUiOutputOlderThanCurrentSources()
    {
        string smoke = ReadRepoFile(
            "OnslaughtCareerEditor.UiTests",
            "WinUiPatchBenchInteractionSmokeTests.cs");
        string test = ExtractMethod(
            smoke,
            "public void PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia()",
            "private static void CollapseByAutomationId");

        int resolve = test.IndexOf("string exePath = ResolveWinUiAppPath();", StringComparison.Ordinal);
        int freshness = test.IndexOf("AssertWinUiBuildIsFresh(exePath);", StringComparison.Ordinal);
        int launch = test.IndexOf("Application.Launch(startInfo)", StringComparison.Ordinal);

        Assert.Multiple(() =>
        {
            Assert.That(freshness, Is.GreaterThan(resolve));
            Assert.That(launch, Is.GreaterThan(freshness));
            Assert.That(smoke, Does.Contain("OnslaughtCareerEditor.WinUI.dll"));
            Assert.That(smoke, Does.Contain("LastWriteTimeUtc"));
            Assert.That(smoke, Does.Contain("SearchOption.AllDirectories"));
            Assert.That(smoke, Does.Contain("DirectorySeparatorChar + \"bin\" + Path.DirectorySeparatorChar"));
            Assert.That(smoke, Does.Contain("DirectorySeparatorChar + \"obj\" + Path.DirectorySeparatorChar"));
        });
    }

    private static XDocument LoadPage() => XDocument.Parse(ReadRepoFile(
        "OnslaughtCareerEditor.WinUI",
        "Pages",
        "BinaryPatchesPage.xaml"));

    private static XElement FindNamedElement(XContainer container, string name)
    {
        return container.Descendants()
            .Single(element => string.Equals((string?)element.Attribute(Xaml + "Name"), name, StringComparison.Ordinal));
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
}
