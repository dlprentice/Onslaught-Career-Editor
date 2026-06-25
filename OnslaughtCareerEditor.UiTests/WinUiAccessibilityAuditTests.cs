using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiAccessibilityAuditTests
{
    [Test]
    public void PrimaryShellAndLongWorkflowControls_ExposeStableAutomationIds()
    {
        Dictionary<string, string[]> expectedIdsByFile = new()
        {
            ["OnslaughtCareerEditor.WinUI/MainWindow.xaml"] =
            [
                "ReviewSetupButton",
                "HomeNavigationItem",
                "SavesNavigationItem",
                "MediaNavigationItem",
                "AssetLibraryNavigationItem",
                "LoreNavigationItem",
                "BinaryNavigationItem",
                "SettingsNavigationItem",
                "AboutNavigationItem"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/HomePage.xaml"] =
            [
                "HomePageTitle",
                "HomePagePurpose",
                "HomeOpenSaveLabButton",
                "HomeOpenConfigurationEditorButton",
                "HomeReviewSettingsButton",
                "HomeSetupStatus",
                "HomeOpenMediaButton",
                "HomeOpenLoreButton",
                "HomeOpenPatchBenchButton",
                "HomeOpenAssetLibraryButton",
                "HomeOpenAboutButton"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/SavesPage.xaml"] =
            [
                "AnalyzeTaskButton",
                "EditSaveTaskButton",
                "ConfigureOptionsTaskButton",
                "SaveAnalyzerTabButton",
                "SaveEditorTabButton",
                "ConfigurationEditorTabButton",
                "SaveAnalyzerStatusInfo",
                "SaveAnalyzerFilePath",
                "SaveAnalyzerAnalyzeButton",
                "SaveEditorInputFile",
                "SaveEditorOutputFile",
                "SaveEditorPatchButton",
                "SaveEditorOutputLog",
                "ConfigurationStatusInfo",
                "ConfigurationDetectedFilesComboBox",
                "ConfigurationInputFile",
                "ConfigurationOutputFile",
                "ConfigurationControllerConfigP1",
                "ConfigurationPatchButton",
                "ConfigurationSafetyHint",
                "ConfigurationOutputLog",
                "ConfigurationCopyOutputButton"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml"] =
            [
                "PatchBenchSourceExePath",
                "PatchBenchCreateWorkingCopyButton",
                "PatchBenchWorkingCopyPath",
                "PatchBenchVerifyButton",
                "PatchBenchApplyButton",
                "PatchBenchRestoreButton",
                "PatchBenchSelectedProfileStatus",
                "PatchBenchMenuColorSelectionStatus",
                "PatchBenchSelectedProfileDetailsExpander",
                "PatchBenchSelectedProfileDetails",
                "PatchBenchDebugCameraPreviewProfileButton",
                "PatchBenchPrepareCopiedProfileButton",
                "PatchBenchCopiedProfileSummary",
                "PatchBenchCopiedProfileReceiptExpander",
                "PatchBenchCopiedProfileReceipt",
                "PatchBenchIncludeSavegamesOption",
                "PatchBenchCreateMusicSwapPresetComboBox",
                "PatchBenchSkipFmvLaunchOption",
                "PatchBenchNoMusicLaunchOption",
                "PatchBenchNoSoundLaunchOption",
                "PatchBenchHighDetailLaunchOption",
                "PatchBenchNoStaticShadowsLaunchOption",
                "PatchBenchNoRumbleLaunchOption",
                "PatchBenchShowDebugTraceLaunchOption",
                "PatchBenchLevelLaunchOption",
                "PatchBenchAdminLevelPresetComboBox",
                "PatchBenchLocalMultiplayerProbeButton",
                "PatchBenchConfigurationLaunchPresetComboBox",
                "PatchBenchPersistControllerConfigOption",
                "PatchBenchSharpenMouseLookOption",
                "PatchBenchMouseSensitivityPresetComboBox",
                "PatchBenchInvertWalkerYOption",
                "PatchBenchInvertFlightYOption",
                "PatchBenchControlBaselinePresetButton",
                "PatchBenchControlSharpenedPresetButton",
                "PatchBenchControlConfig2PresetButton",
                "PatchBenchControlConfig3PresetButton",
                "PatchBenchControlConfig4PresetButton",
                "PatchBenchTextureRamLimitLaunchOption",
                "PatchBenchLaunchCopiedProfileButton",
                "PatchBenchStopCopiedProfileButton",
                "PatchBenchCopiedProfileLaunchStatus",
                "PatchBenchCopiedProfileLaunchPlanExpander",
                "PatchBenchCopiedProfileLaunchPlan",
                "PatchBenchAdvancedLaunchOptionsExpander",
                "PatchBenchMusicSwapBea02ForBea01PresetButton",
                "PatchBenchMusicSwapBea01ForBea02PresetButton",
                "PatchBenchMusicTargetTrackComboBox",
                "PatchBenchMusicReplacementTrackComboBox",
                "PatchBenchStageCopiedTrackSwapButton",
                "PatchBenchMusicTargetFileName",
                "PatchBenchMusicReplacementPath",
                "PatchBenchStageMusicReplacementButton",
                "PatchBenchRestoreMusicReplacementButton",
                "PatchBenchMusicReplacementStatus",
                "PatchBenchOnlineReadinessStatusPanel",
                "PatchBenchOnlinePrepCard",
                "PatchBenchOnlinePrepTitle",
                "PatchBenchOnlinePrepSummary",
                "PatchBenchOnlinePrepBoundary",
                "PatchBenchOnlinePrepLocalProbeButton",
                "PatchBenchOnlinePrepActionStatus",
                "PatchBenchOnlineReadinessTitle",
                "PatchBenchOnlineReadinessHeadline",
                "PatchBenchOnlineReadinessSlots",
                "PatchBenchOnlineReadinessMetadataSlots",
                "PatchBenchOnlineReadinessProofClass",
            "PatchBenchOnlineReadinessNextProof",
            "PatchBenchOnlineReadinessBlockedActions",
            "PatchBenchOnlineMaintainerArtifactToolsToggle",
            "PatchBenchMaintainerArtifactToolsStatus",
            "PatchBenchMaintainerArtifactLoaderPanel",
            "PatchBenchDualSafeCopyTopologyArtifactStatus",
            "PatchBenchDualSafeCopyTopologyBoundary",
            "PatchBenchDualSafeCopyTopologyNextProofs",
                "PatchBenchLoadDualSafeCopyTopologyArtifactButton",
                "PatchBenchClearDualSafeCopyTopologyArtifactButton",
                "PatchBenchOnlineLiveAttemptStatus",
                "PatchBenchOnlineLiveAttemptBlockers",
                "PatchBenchOnlineLiveAttemptCommands",
                "PatchBenchOnlinePromotionLockStatus",
                "PatchBenchOnlineReadinessArtifactStatus",
                "PatchBenchLoadOnlineReadinessArtifactButton",
                "PatchBenchClearOnlineReadinessArtifactButton",
                "PatchBenchGamepadReadinessArtifactStatus",
                "PatchBenchLoadGamepadReadinessArtifactButton",
                "PatchBenchClearGamepadReadinessArtifactButton",
                "PatchBenchOperationLog"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/MediaPage.xaml"] =
            [
                "MediaAudioTabButton",
                "MediaVideoTabButton",
                "MediaAudioSearchBox",
                "MediaAudioTreeView",
                "MediaAudioPlayButton",
                "MediaAudioPauseButton",
                "MediaAudioStopButton",
                "MediaVideoSearchBox",
                "MediaVideoTreeView",
                "MediaVideoPlayButton",
                "MediaVideoPauseButton",
                "MediaVideoStopButton"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml"] =
            [
                "AssetCatalogPathTextBox",
                "AssetCatalogFirstRunGuide",
                "AssetLoadCatalogButton",
                "AssetItemsList",
                "AssetGoodiesTabButton",
                "AssetGoodieSaveStateStatus",
                "AssetGoodieSaveStatePathTextBox",
                "AssetLoadGoodieSaveStateButton",
                "AssetTexturePreviewImage",
                "AssetModelWireframePanel",
                "AssetOpenExportButton",
                "AssetCopyExportPathButton"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/LorePage.xaml"] =
            [
                "LoreSearchBox",
                "LoreSourceBoundaryStatus",
                "LoreDocumentTree",
                "LoreCurrentDocumentTitle",
                "LoreReaderPanel"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/SettingsPage.xaml"] =
            [
                "SettingsGameDirectorySummary",
                "SettingsAutoDetectGameDirectoryButton",
                "SettingsGameDirectoryPathDetails",
                "SettingsGameDirectoryPathTextBox",
                "SettingsAllowBackgroundAudioToggle",
                "SettingsAllowBackgroundVideoToggle",
                "SettingsPreventOverlapToggle",
                "SettingsReloadButton"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/AboutPage.xaml"] =
            [
                "AboutPageTitle",
                "AboutProductSummary",
                "AboutCoreCapabilitiesTitle",
                "AboutProjectNotesTitle",
                "AboutProductLaneNote",
                "AboutRetailBehaviorTitle",
                "AboutVersionText"
            ]
        };

        List<string> missing = [];
        foreach ((string relativePath, string[] expectedIds) in expectedIdsByFile)
        {
            string source = ReadRepoFile(relativePath.Split('/'));
            foreach (string expectedId in expectedIds)
            {
                if (!source.Contains($"AutomationProperties.AutomationId=\"{expectedId}\""))
                {
                    missing.Add($"{relativePath}: {expectedId}");
                }
            }
        }

        Assert.That(missing, Is.Empty, "Primary and long-workflow WinUI controls should expose stable automation ids.");
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
    public void LongWinUiScrollSurfaces_ExposeAutomationIdsAndNames()
    {
        Dictionary<string, string[]> expectedScrollSurfacesByFile = new()
        {
            ["OnslaughtCareerEditor.WinUI/Pages/HomePage.xaml"] =
            [
                "HomePageScrollViewer"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/SavesPage.xaml"] =
            [
                "SaveAnalyzerResultsScrollViewer",
                "SaveEditorScrollViewer",
                "ConfigurationEditorScrollViewer"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml"] =
            [
                "AssetPreviewScrollViewer"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml"] =
            [
                "PatchBenchScrollViewer"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/SettingsPage.xaml"] =
            [
                "SettingsPageScrollViewer"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/AboutPage.xaml"] =
            [
                "AboutPageScrollViewer"
            ]
        };

        List<string> missing = [];
        foreach ((string relativePath, string[] expectedIds) in expectedScrollSurfacesByFile)
        {
            string source = ReadRepoFile(relativePath.Split('/'));
            foreach (string expectedId in expectedIds)
            {
                string pattern = $"<ScrollViewer[\\s\\S]*?AutomationProperties\\.AutomationId=\\\"{Regex.Escape(expectedId)}\\\"[\\s\\S]*?AutomationProperties\\.Name=\\\"[^\\\"]+\\\"";
                if (!Regex.IsMatch(source, pattern))
                {
                    missing.Add($"{relativePath}: {expectedId}");
                }
            }
        }

        Assert.That(missing, Is.Empty, "Long WinUI page scroll surfaces should be explicitly targetable and named for scrolled-section automation and visual proof.");
    }

    [Test]
    public void WinUiPageButtons_ExposeAutomationIds()
    {
        string pagesRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages");
        List<string> missing = [];

        foreach (string filePath in Directory.GetFiles(pagesRoot, "*.xaml"))
        {
            string source = File.ReadAllText(filePath);
            foreach (Match match in Regex.Matches(source, "<Button\\b[\\s\\S]*?(?:/>|>)"))
            {
                string block = match.Value;
                if (block.Contains("AutomationProperties.AutomationId="))
                {
                    continue;
                }

                int line = source[..match.Index].Count(c => c == '\n') + 1;
                string label = Regex.Match(block, "Content=\"([^\"]+)\"") is { Success: true } contentMatch
                    ? contentMatch.Groups[1].Value
                    : block.Split(['\r', '\n'], System.StringSplitOptions.RemoveEmptyEntries)[0].Trim();

                missing.Add($"{Path.GetFileName(filePath)}:{line}: {label}");
            }
        }

        Assert.That(missing, Is.Empty, "All WinUI page buttons should expose stable automation ids for UI Automation and offscreen scroll-driven tests.");
    }

    [Test]
    public void NamedWinUiPageInputs_ExposeAutomationIds()
    {
        string pagesRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages");
        Regex interactiveControl = new("<(?:\\w+:)?(?:TextBox|ComboBox|ToggleSwitch|CheckBox|TreeView|ListView|ListBox|Slider|RadioButton|NumberBox)\\b[\\s\\S]*?(?:/>|>)");
        List<string> missing = [];

        foreach (string filePath in Directory.GetFiles(pagesRoot, "*.xaml"))
        {
            string source = File.ReadAllText(filePath);
            foreach (Match match in interactiveControl.Matches(source))
            {
                string block = match.Value;
                Match nameMatch = Regex.Match(block, "x:Name=\"([^\"]+)\"");
                if (!nameMatch.Success || block.Contains("AutomationProperties.AutomationId="))
                {
                    continue;
                }

                int line = source[..match.Index].Count(c => c == '\n') + 1;
                missing.Add($"{Path.GetFileName(filePath)}:{line}: {nameMatch.Groups[1].Value}");
            }
        }

        Assert.That(missing, Is.Empty, "Named WinUI page inputs should expose stable automation ids for UI Automation and accessibility review.");
    }

    [Test]
    public void WinUiInteractiveControls_ExposeAccessibleNameSource()
    {
        string winUiRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI");
        Regex interactiveControl = new("<(?:\\w+:)?(?:Button|TextBox|ComboBox|ToggleSwitch|CheckBox|TreeView|ListView|ListBox|Slider|RadioButton|NumberBox|NavigationViewItem)(?=\\s|/|>)[\\s\\S]*?(?:/>|>)");
        List<string> missing = [];

        foreach (string filePath in Directory.GetFiles(winUiRoot, "*.xaml", SearchOption.AllDirectories)
                     .Where(path => !path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") &&
                                    !path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")))
        {
            string source = File.ReadAllText(filePath);
            foreach (Match match in interactiveControl.Matches(source))
            {
                string block = match.Value;
                bool hasNameSource =
                    block.Contains("AutomationProperties.Name=") ||
                    Regex.IsMatch(block, "\\bContent=\\\"[^\\\"]+\\\"") ||
                    Regex.IsMatch(block, "\\bHeader=\\\"[^\\\"]+\\\"") ||
                    Regex.IsMatch(block, "\\bPlaceholderText=\\\"[^\\\"]+\\\"");

                if (hasNameSource)
                {
                    continue;
                }

                int line = source[..match.Index].Count(c => c == '\n') + 1;
                string control = block.Split(['\r', '\n'], System.StringSplitOptions.RemoveEmptyEntries)[0].Trim();
                string relativePath = Path.GetRelativePath(TestFixturePaths.RepoRoot, filePath);
                missing.Add($"{relativePath}:{line}: {control}");
            }
        }

        Assert.That(missing, Is.Empty, "Interactive WinUI controls should expose a human accessible name through content, header, placeholder, or AutomationProperties.Name.");
    }

    [Test]
    public void GameOptionsKeybindOverrides_UsePlayerSpecificAccessibleNames()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml");
        string model = ReadRepoFile("OnslaughtCareerEditor.AppCore", "ConfigurationEditorService.cs");

        Assert.That(model, Does.Contain("Player1AccessibleName => BuildOverrideAccessibleName(\"Player 1\")"));
        Assert.That(model, Does.Contain("Player2AccessibleName => BuildOverrideAccessibleName(\"Player 2\")"));
        Assert.That(xaml, Does.Contain("AutomationProperties.Name=\"{Binding Player1AccessibleName}\""));
        Assert.That(xaml, Does.Contain("AutomationProperties.Name=\"{Binding Player2AccessibleName}\""));
        Assert.That(xaml, Does.Not.Contain("AutomationProperties.Name=\"{Binding ActionLabel}\""));
    }

    [Test]
    public void WinUiLargeSummariesLogsReceiptsAndHints_DoNotUseLiveRegions()
    {
        string winUiRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI");
        Regex candidateBlock = new("<(?:\\w+:)?(?:TextBox|TextBlock)\\b[\\s\\S]*?(?:/>|>)");
        Regex controlKind = new("^<(?:(?:\\w+):)?(?<kind>TextBox|TextBlock)\\b");
        Regex broadLiveName = new("(?i)(Summary|Receipt|Log|Hint)");
        List<string> noisyLogs = [];

        foreach (string filePath in Directory.GetFiles(winUiRoot, "*.xaml", SearchOption.AllDirectories)
                     .Where(path => !path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") &&
                                    !path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")))
        {
            string source = File.ReadAllText(filePath);
            foreach (Match match in candidateBlock.Matches(source))
            {
                string block = match.Value;
                if (!block.Contains("AutomationProperties.LiveSetting="))
                {
                    continue;
                }

                string kind = controlKind.Match(block).Groups["kind"].Value;
                string identifierText = string.Join(
                    " ",
                    ExtractAttribute(block, "x:Name"),
                    ExtractAttribute(block, "AutomationProperties.AutomationId"),
                    ExtractAttribute(block, "AutomationProperties.Name"));
                bool isNoisyLiveRegion = kind == "TextBox" || broadLiveName.IsMatch(identifierText);
                if (!isNoisyLiveRegion)
                {
                    continue;
                }

                int line = source[..match.Index].Count(c => c == '\n') + 1;
                string relativePath = Path.GetRelativePath(TestFixturePaths.RepoRoot, filePath);
                noisyLogs.Add($"{relativePath}:{line}");
            }
        }

        Assert.That(noisyLogs, Is.Empty, "Large summaries, receipts, logs, and hints should not be live regions; use concise status/progress TextBlocks for polite announcements.");

        static string ExtractAttribute(string block, string attributeName)
        {
            Match match = Regex.Match(block, Regex.Escape(attributeName) + "=\"([^\"]*)\"");
            return match.Success ? match.Groups[1].Value : string.Empty;
        }
    }

    [Test]
    public void WinUiXamlAutomationIds_AreUnique()
    {
        string winUiRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI");
        Dictionary<string, List<string>> locationsById = [];
        Regex idPattern = new("AutomationProperties\\.AutomationId=\"([^\"]+)\"");

        foreach (string filePath in Directory.GetFiles(winUiRoot, "*.xaml", SearchOption.AllDirectories)
                     .Where(path => !path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") &&
                                    !path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}")))
        {
            string source = File.ReadAllText(filePath);
            foreach (Match match in idPattern.Matches(source))
            {
                string id = match.Groups[1].Value;
                int line = source[..match.Index].Count(c => c == '\n') + 1;
                string relativePath = Path.GetRelativePath(TestFixturePaths.RepoRoot, filePath);

                if (!locationsById.TryGetValue(id, out List<string>? locations))
                {
                    locations = [];
                    locationsById[id] = locations;
                }

                locations.Add($"{relativePath}:{line}");
            }
        }

        string[] duplicates = locationsById
            .Where(pair => pair.Value.Count > 1)
            .Select(pair => $"{pair.Key}: {string.Join(", ", pair.Value)}")
            .ToArray();

        Assert.That(duplicates, Is.Empty, "WinUI automation ids should remain unique across source XAML.");
    }

    [Test]
    public void PrimaryShellActions_ExposeUniqueKeyboardAccessKeys()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml");
        Dictionary<string, string> expectedAccessKeys = new()
        {
            ["ReviewSetupButton"] = "R",
            ["HomeNavigationItem"] = "H",
            ["SavesNavigationItem"] = "S",
            ["MediaNavigationItem"] = "M",
            ["AssetLibraryNavigationItem"] = "A",
            ["LoreNavigationItem"] = "L",
            ["BinaryNavigationItem"] = "W",
            ["SettingsNavigationItem"] = "T",
            ["AboutNavigationItem"] = "B"
        };

        foreach ((string controlName, string accessKey) in expectedAccessKeys)
        {
            Assert.That(xaml, Does.Contain($"x:Name=\"{controlName}\""), $"Expected shell control {controlName}.");
            Assert.That(xaml, Does.Contain($"AccessKey=\"{accessKey}\""), $"Expected {controlName} to expose access key {accessKey}.");
        }

        Assert.That(expectedAccessKeys.Values, Is.Unique, "Shell access keys should stay unique.");
    }

    private static string ReadRepoFile(params string[] relativeParts)
    {
        string path = Path.Combine(relativeParts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }
}
