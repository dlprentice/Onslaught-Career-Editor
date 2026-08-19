using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using System.Xml.Linq;
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
                "CheatsNavigationItem",
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
                "HomePrimaryTasksTitle",
                "HomeBrowseLearnTitle",
                "HomeMoreToolsTitle",
                "HomeSetupSafetyTitle",
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
            ["OnslaughtCareerEditor.WinUI/Pages/CheatsPage.xaml"] =
            [
                "CheatsPageTitle",
                "CheatsPageSummary",
                "CheatsBoundarySafeCopyNote",
                "CheatsBoundaryNewFileNote",
                "CheatsBoundaryReversibleNote",
                "CheatsChooseSourceSaveButton",
                "CheatsSourceSaveStatus",
                "CheatsAllGoodiesCheckBox",
                "CheatsAllLevelsCheckBox",
                "CheatsGodModeCheckBox",
                "CheatsFreeCameraCheckBox",
                "CheatsGoodieGatingBypassCheckBox",
                "CheatsBaseNameTextBox",
                "CheatsComposedName",
                "CheatsComposedNameExplanation",
                "CheatsDestinationComboBox",
                "CheatsChooseDestinationFolderButton",
                "CheatsRefreshSafeCopiesButton",
                "CheatsDestinationStatus",
                "CheatsWriteCheatSaveButton",
                "CheatsStatusInfo",
                "CheatsFreeCameraExtraNote",
                "CheatsOpenDebugCameraPreviewButton"
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
                "SaveAnalyzerInputFile",
                "SaveAnalyzerCompareFile",
                "SaveAnalyzerAnalyzeButton",
                "SaveEditorInputFile",
                "SaveEditorInputLocation",
                "SaveEditorOutputFile",
                "SaveEditorPatchButton",
                "SaveEditorOutputLog",
                "ConfigurationStatusInfo",
                "ConfigurationDetectedFilesComboBox",
                "ConfigurationInputFile",
                "ConfigurationInputLocation",
                "ConfigurationOutputFile",
                "ConfigurationControllerConfigP1",
                "ConfigurationPatchButton",
                "ConfigurationSafetyHint",
                "ConfigurationOutputLog",
                "ConfigurationCopyOutputButton"
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml"] =
            [
                "PatchBenchSourceExeFile",
                "PatchBenchCreateWorkingCopyButton",
                "PatchBenchWorkingCopyFile",
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
                "PatchBenchShowDebugTraceLaunchOption",
                "PatchBenchLevelLaunchOption",
                "PatchBenchAdminLevelPresetComboBox",
                "PatchBenchLocalMultiplayerProbeButton",
                "PatchBenchCopiedControllerConfigComboBox",
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
                "PatchBenchMusicReplacementFile",
                "PatchBenchStageMusicReplacementButton",
                "PatchBenchRestoreMusicReplacementButton",
                "PatchBenchMusicReplacementStatus",
                "PatchBenchOnlinePrepCard",
                "PatchBenchOnlinePrepTitle",
                "PatchBenchOnlinePrepSummary",
                "PatchBenchOnlinePrepBoundary",
                "PatchBenchOnlinePrepLocalProbeButton",
                "PatchBenchOnlinePrepActionStatus",
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
                "AssetCatalogFileTextBox",
                "AssetCatalogFirstRunGuide",
                "AssetLoadCatalogButton",
                "AssetItemsList",
                "AssetGoodiesTabButton",
                "AssetGoodieSaveStateStatus",
                "AssetGoodieSaveStateFileTextBox",
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
                "SettingsGameDirectoryFolderDetails",
                "SettingsGameDirectoryFolderTextBox",
                "SettingsGameDirectoryIdentity",
                "SettingsAppearancePersistStatus",
                "SettingsMediaPersistStatus",
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
                "AboutGameInstallBoundaryNote",
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
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/CheatsPage.xaml"] =
            [
                "CheatsPageScrollViewer"
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
    public void PrincipalPageOrientationHeadings_ExposeOneSemanticLevelOneHeading()
    {
        Dictionary<string, (string RelativePath, string ExpectedLevel)[]> expectedHeadingsByFile = new()
        {
            ["OnslaughtCareerEditor.WinUI/Pages/HomePage.xaml"] =
            [
                ("HomePageTitle", "Level1"),
                ("HomePrimaryTasksTitle", "Level2"),
                ("HomePatchModsTitle", "Level3"),
                ("HomeSaveOptionsTitle", "Level3"),
                ("HomeBrowseLearnTitle", "Level2"),
                ("HomeMediaTitle", "Level3"),
                ("HomeLoreTitle", "Level3"),
                ("HomeMoreToolsTitle", "Level2"),
                ("HomeAssetCatalogsTitle", "Level3"),
                ("HomeProjectNotesTitle", "Level3"),
                ("HomeSetupSafetyTitle", "Level2"),
                ("HomeSetupTitle", "Level3"),
                ("HomeSafetyPostureTitle", "Level3")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/AboutPage.xaml"] =
            [
                ("AboutPageTitle", "Level1"),
                ("AboutCoreCapabilitiesTitle", "Level2"),
                ("AboutProjectNotesTitle", "Level2"),
                ("AboutRetailBehaviorTitle", "Level2"),
                ("AboutVersionTitle", "Level2")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/SavesPage.xaml"] =
            [
                ("SavesPageTitle", "Level1")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/MediaPage.xaml"] =
            [
                ("MediaPageTitle", "Level1")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/AssetLibraryPage.xaml"] =
            [
                ("AssetLibraryPageTitle", "Level1")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/LorePage.xaml"] =
            [
                ("LorePageTitle", "Level1")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/BinaryPatchesPage.xaml"] =
            [
                ("BinaryPatchesPageTitle", "Level1")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/SettingsPage.xaml"] =
            [
                ("SettingsPageTitle", "Level1")
            ],
            ["OnslaughtCareerEditor.WinUI/Pages/CheatsPage.xaml"] =
            [
                ("CheatsPageTitle", "Level1"),
                ("CheatsBoundaryTitle", "Level2"),
                ("CheatsSourceTitle", "Level2"),
                ("CheatsSelectionTitle", "Level2"),
                ("CheatsNameTitle", "Level2"),
                ("CheatsDestinationTitle", "Level2"),
                ("CheatsFreeCameraExtraTitle", "Level2")
            ]
        };

        List<string> missing = [];
        foreach ((string relativePath, (string AutomationId, string ExpectedLevel)[] expectedHeadings) in expectedHeadingsByFile)
        {
            XDocument document = XDocument.Parse(ReadRepoFile(relativePath.Split('/')));
            int levelOneCount = document
                .Descendants()
                .Count(element => string.Equals(
                    (string?)element.Attribute("AutomationProperties.HeadingLevel"),
                    "Level1",
                    System.StringComparison.Ordinal));
            if (levelOneCount != 1)
            {
                missing.Add($"{relativePath}: expected exactly one Level1 heading, found {levelOneCount}");
            }

            foreach ((string automationId, string expectedLevel) in expectedHeadings)
            {
                XElement element = ExtractControlElementByAutomationId(document, automationId);
                string? actualLevel = (string?)element.Attribute("AutomationProperties.HeadingLevel");
                if (!string.Equals(actualLevel, expectedLevel, System.StringComparison.Ordinal))
                {
                    missing.Add($"{relativePath}: {automationId} expected {expectedLevel}, found {actualLevel ?? "<missing>"}");
                }
            }
        }

        Assert.That(missing, Is.Empty, "Each principal page should expose one Level1 title, with subordinate Home/About headings retaining their semantic levels.");
    }

    [Test]
    public void WinUiPageButtons_ExposeAutomationIds()
    {
        string pagesRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages");
        List<string> missing = [];

        foreach (string filePath in Directory.GetFiles(pagesRoot, "*.xaml", SearchOption.AllDirectories))
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

        foreach (string filePath in Directory.GetFiles(pagesRoot, "*.xaml", SearchOption.AllDirectories))
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
    public void AssetLibrary_GoodieSaveStateStatusIsOnlyPoliteLiveRegion()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml");
        XDocument document = XDocument.Parse(xaml);

        XElement goodieStatus = ExtractControlElementByAutomationId(document, "AssetGoodieSaveStateStatus");
        Assert.That((string?)goodieStatus.Attribute("AutomationProperties.LiveSetting"), Is.EqualTo("Polite"));

        string[] politeLiveRegionIds = document.Descendants()
            .Where(element => (string?)element.Attribute("AutomationProperties.LiveSetting") == "Polite")
            .Select(element => (string?)element.Attribute("AutomationProperties.AutomationId") ?? "<missing AutomationId>")
            .ToArray();
        Assert.That(politeLiveRegionIds, Is.EqualTo(new[] { "AssetGoodieSaveStateStatus" }));

        string[] nonLiveStatusIds =
        [
            "AssetCatalogStatus",
            "AssetModelWireframeStatus",
            "AssetModelMetadataStatus"
        ];

        foreach (string automationId in nonLiveStatusIds)
        {
            XElement element = ExtractControlElementByAutomationId(document, automationId);
            Assert.That(element.Attribute("AutomationProperties.LiveSetting"), Is.Null, $"{automationId} should not be a live region.");
        }

        Assert.That(xaml, Does.Not.Contain("AutomationProperties.LiveSetting=\"Assertive\""));
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
            ["CheatsNavigationItem"] = "C",
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

    [Test]
    public void PatchBenchChoiceButtons_KeepXamlAndRuntimeAccessibleNamesIdentical()
    {
        // Windowed & Mods choice buttons declare an accessible name in XAML and then have it
        // re-applied at runtime by PatchBenchChoiceVisualState.Bind. When the two drift, the
        // XAML value is silently replaced on the first refresh and screen-reader users hear a
        // different name than the static surface (and the audits pinning it) describe.
        XDocument page = XDocument.Parse(ReadRepoFile(
            "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"));
        string codeBehind = ReadRepoFile(
            "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");

        string launchPresetHelper = ReadRepoFile(
            "OnslaughtCareerEditor.WinUI", "Helpers", "PatchBenchLaunchPresetText.cs");

        // Two registration shapes exist: literal names inline, and names produced by the shared
        // PatchBenchLaunchPresetText builders. Both are resolved so neither can drift from XAML.
        MatchCollection literalBindings = Regex.Matches(
            codeBehind,
            @"PatchBenchChoiceVisualState\.Bind\(\s*(?<button>\w+)\s*,\s*""(?<normal>[^""]*)""\s*,\s*""(?<selected>[^""]*)""");
        MatchCollection helperBindings = Regex.Matches(
            codeBehind,
            @"PatchBenchChoiceVisualState\.Bind\(\s*(?<button>\w+)\s*,\s*PatchBenchLaunchPresetText\.(?<builder>\w+)\(");

        Assert.That(literalBindings, Is.Not.Empty, "Expected literal PatchBenchChoiceVisualState.Bind registrations.");
        Assert.That(helperBindings, Is.Not.Empty, "Expected PatchBenchLaunchPresetText-backed PatchBenchChoiceVisualState.Bind registrations.");

        List<(string Button, string RuntimeName)> registrations = literalBindings
            .Select(binding => (binding.Groups["button"].Value, binding.Groups["normal"].Value))
            .ToList();

        foreach (Match binding in helperBindings)
        {
            string builder = binding.Groups["builder"].Value;
            Match builderBody = Regex.Match(
                launchPresetHelper,
                Regex.Escape(builder) + @"\(bool isSelected\)\s*\{\s*return BuildChoiceState\(\s*""(?<normal>[^""]*)""");
            Assert.That(
                builderBody.Success,
                Is.True,
                $"Could not resolve the normal accessible name produced by PatchBenchLaunchPresetText.{builder}.");
            registrations.Add((binding.Groups["button"].Value, builderBody.Groups["normal"].Value));
        }

        Assert.Multiple(() =>
        {
            foreach ((string button, string runtimeName) in registrations)
            {
                XElement element = ExtractControlElementByAutomationId(page, button);

                Assert.That(
                    (string?)element.Attribute("AutomationProperties.Name"),
                    Is.EqualTo(runtimeName),
                    $"{button}: XAML AutomationProperties.Name must match the runtime Bind name.");

                string? visibleLabel = ExtractVisibleLabel(element);
                if (visibleLabel is not null)
                {
                    // WCAG 2.5.3 Label in Name. Case is not significant for speech input.
                    Assert.That(
                        runtimeName,
                        Does.Contain(visibleLabel).IgnoreCase,
                        $"{button}: accessible name '{runtimeName}' must contain visible label '{visibleLabel}'.");
                }
            }
        });
    }

    [Test]
    public void WinUiLabelledButtons_KeepTheirVisibleLabelInsideTheAccessibleName()
    {
        // WCAG 2.5.3 Label in Name (Level A): a speech-input user must be able to activate a
        // control by saying the words they can see on it. Every button that carries both a
        // visible label and an explicit AutomationProperties.Name is covered, not just the
        // PatchBenchChoiceVisualState set.
        string winUiRoot = Path.Combine(TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI");
        List<string> violations = [];

        foreach (string filePath in EnumerateSourceXaml(winUiRoot))
        {
            string relativePath = Path.GetRelativePath(TestFixturePaths.RepoRoot, filePath);
            violations.AddRange(FindLabelInNameViolations(relativePath, File.ReadAllText(filePath)));
        }

        Assert.That(
            violations,
            Is.Empty,
            $"Button accessible names should contain their visible label so speech input can activate them. {violations.Count} violation(s):{System.Environment.NewLine}{string.Join(System.Environment.NewLine, violations)}");
    }

    [Test]
    public void LabelInNameAudit_ReportsAButtonWhoseAccessibleNameOmitsItsVisibleLabel()
    {
        // Vacuity guard: the widened audit above is only worth having if it can fail.
        const string compliantXaml = """
            <Root>
              <Button AutomationProperties.AutomationId="GoodButton"
                      AutomationProperties.Name="Create safe copy of the game"
                      Content="Create safe copy" />
            </Root>
            """;
        const string violatingXaml = """
            <Root>
              <Button AutomationProperties.AutomationId="BadButton"
                      AutomationProperties.Name="Duplicate the installation"
                      Content="Create safe copy" />
            </Root>
            """;
        const string violatingNestedLabelXaml = """
            <Root>
              <Button AutomationProperties.AutomationId="BadNestedButton"
                      AutomationProperties.Name="Duplicate the installation">
                <TextBlock Text="Create safe copy" />
              </Button>
            </Root>
            """;

        Assert.Multiple(() =>
        {
            Assert.That(
                FindLabelInNameViolations("synthetic.xaml", compliantXaml),
                Is.Empty,
                "A name that contains its visible label must not be reported.");
            Assert.That(
                FindLabelInNameViolations("synthetic.xaml", violatingXaml),
                Is.EqualTo(new[]
                {
                    "synthetic.xaml: BadButton: accessible name 'Duplicate the installation' omits visible label 'Create safe copy'."
                }));
            Assert.That(
                FindLabelInNameViolations("synthetic.xaml", violatingNestedLabelXaml),
                Is.EqualTo(new[]
                {
                    "synthetic.xaml: BadNestedButton: accessible name 'Duplicate the installation' omits visible label 'Create safe copy'."
                }));
        });
    }

    private static IEnumerable<string> EnumerateSourceXaml(string root)
    {
        return Directory.GetFiles(root, "*.xaml", SearchOption.AllDirectories)
            .Where(path => !path.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") &&
                           !path.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}"))
            .OrderBy(path => path, System.StringComparer.Ordinal);
    }

    private static List<string> FindLabelInNameViolations(string relativePath, string xaml)
    {
        List<string> violations = [];
        foreach (XElement button in XDocument.Parse(xaml)
                     .Descendants()
                     .Where(element => element.Name.LocalName is "Button" or "AppBarButton" or "HyperlinkButton" or "ToggleButton" or "DropDownButton"))
        {
            string? accessibleName = (string?)button.Attribute("AutomationProperties.Name");
            if (accessibleName is null || accessibleName.Contains('{'))
            {
                continue;
            }

            string? visibleLabel = ExtractVisibleLabel(button);
            if (visibleLabel is null || string.IsNullOrWhiteSpace(visibleLabel))
            {
                continue;
            }

            if (accessibleName.Contains(visibleLabel, System.StringComparison.OrdinalIgnoreCase))
            {
                continue;
            }

            string identifier = (string?)button.Attribute("AutomationProperties.AutomationId")
                ?? button.Attributes().FirstOrDefault(attribute => attribute.Name.LocalName == "Name")?.Value
                ?? visibleLabel;
            violations.Add($"{relativePath}: {identifier}: accessible name '{accessibleName}' omits visible label '{visibleLabel}'.");
        }

        return violations;
    }

    private static string? ExtractVisibleLabel(XElement button)
    {
        string? content = (string?)button.Attribute("Content") ?? (string?)button.Attribute("Label");
        if (content is not null)
        {
            return content.Contains('{') ? null : content;
        }

        string[] texts = button.Descendants()
            .Where(candidate => candidate.Name.LocalName == "TextBlock")
            .Select(candidate => (string?)candidate.Attribute("Text"))
            .Where(text => !string.IsNullOrWhiteSpace(text) && !text!.Contains('{'))
            .Select(text => text!)
            .ToArray();
        return texts.Length == 1 ? texts[0] : null;
    }

    private static XElement ExtractControlElementByAutomationId(XDocument document, string automationId)
    {
        XElement? element = document.Descendants()
            .SingleOrDefault(candidate => (string?)candidate.Attribute("AutomationProperties.AutomationId") == automationId);
        Assert.That(element, Is.Not.Null, $"Missing XAML element with AutomationId {automationId}.");
        return element!;
    }

    private static string ReadRepoFile(params string[] relativeParts)
    {
        string path = Path.Combine(relativeParts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }
}
