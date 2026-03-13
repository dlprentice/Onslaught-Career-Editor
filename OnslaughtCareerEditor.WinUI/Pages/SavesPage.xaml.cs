using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;
using Windows.ApplicationModel.DataTransfer;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class SavesPage : Page
    {
        private const int SaveAnalyzerTabIndex = 0;
        private const int SaveEditorTabIndex = 1;
        private const int ConfigurationEditorTabIndex = 2;

        private IReadOnlyList<SaveAnalyzerFileItem> _detectedFiles = Array.Empty<SaveAnalyzerFileItem>();
        private IReadOnlyList<SaveAnalyzerFileItem> _editorDetectedFiles = Array.Empty<SaveAnalyzerFileItem>();
        private SaveAnalyzerDocument? _currentDocument;
        private bool _editorInputValid;
        private bool _suppressEditorPresetSync;
        private bool _editorKillsOnlyRestoreCaptured;
        private bool _editorRestoreNodes = true;
        private bool _editorRestoreLinks = true;
        private bool _editorRestoreGoodies = true;
        private bool _editorRestoreKills = true;
        private int _selectedSavesTabIndex = SaveAnalyzerTabIndex;

        public SavesPage()
        {
            InitializeComponent();
            ResetAnalyzerSurface();
            LoadDetectedFiles();
            InitializeEditorSurface();
            InitializeEditorAdvancedSurface();
            LoadEditorDetectedFiles();
            InitializeConfigurationSurface();
            LoadConfigurationDetectedFiles();
            int lastSubTab = Math.Clamp(AppConfig.Load().LastSaveSubTab, SaveAnalyzerTabIndex, ConfigurationEditorTabIndex);
            SelectSavesTab(lastSubTab, persistSelection: false);
        }

        private void SaveAnalyzerTabButton_Click(object sender, RoutedEventArgs e) => SelectSavesTab(SaveAnalyzerTabIndex);

        private void SaveEditorTabButton_Click(object sender, RoutedEventArgs e) => SelectSavesTab(SaveEditorTabIndex);

        private void ConfigurationEditorTabButton_Click(object sender, RoutedEventArgs e) => SelectSavesTab(ConfigurationEditorTabIndex);

        private void SelectSavesTab(int tabIndex, bool persistSelection = true)
        {
            _selectedSavesTabIndex = Math.Clamp(tabIndex, SaveAnalyzerTabIndex, ConfigurationEditorTabIndex);

            SaveAnalyzerTabContentGrid.Visibility = _selectedSavesTabIndex == SaveAnalyzerTabIndex ? Visibility.Visible : Visibility.Collapsed;
            SaveEditorTabContentGrid.Visibility = _selectedSavesTabIndex == SaveEditorTabIndex ? Visibility.Visible : Visibility.Collapsed;
            ConfigurationEditorTabContentGrid.Visibility = _selectedSavesTabIndex == ConfigurationEditorTabIndex ? Visibility.Visible : Visibility.Collapsed;

            SaveAnalyzerTabButton.Style = (Style)Resources[_selectedSavesTabIndex == SaveAnalyzerTabIndex ? "SavesActiveTabButtonStyle" : "SavesInactiveTabButtonStyle"];
            SaveEditorTabButton.Style = (Style)Resources[_selectedSavesTabIndex == SaveEditorTabIndex ? "SavesActiveTabButtonStyle" : "SavesInactiveTabButtonStyle"];
            ConfigurationEditorTabButton.Style = (Style)Resources[_selectedSavesTabIndex == ConfigurationEditorTabIndex ? "SavesActiveTabButtonStyle" : "SavesInactiveTabButtonStyle"];

            if (persistSelection)
            {
                AppConfig config = AppConfig.Load();
                config.LastSaveSubTab = _selectedSavesTabIndex;
                config.Save();
            }

            AppStatusService.SetStatus(_selectedSavesTabIndex switch
            {
                SaveEditorTabIndex => "Save Editor: patch workflow ready",
                ConfigurationEditorTabIndex => "Configuration Editor: global options ready",
                _ => "Saves: analyzer ready"
            });
        }

        private void LoadDetectedFiles()
        {
            string selectedPath = (DetectedFilesComboBox.SelectedItem as SaveAnalyzerFileItem)?.Path
                ?? (FilePathTextBox.Text ?? string.Empty).Trim();
            string? gameDir = AppConfig.Load().GetGameDir();
            _detectedFiles = SaveAnalyzerService.GetDetectedFiles(gameDir);
            DetectedFilesComboBox.ItemsSource = _detectedFiles;
            RestoreAnalyzerDetectedFileSelection(selectedPath);
            DetectedFilesStatusTextBlock.Text = _detectedFiles.Count == 0
                ? "No save or options files were detected. Set the game directory in Settings or browse manually."
                : $"{_detectedFiles.Count} detected file(s) available.";
        }

        private void InitializeEditorSurface()
        {
            EditorRankComboBox.SelectedIndex = 0;
            EditorPatchPresetComboBox.SelectedIndex = 0;
            EditorGlobalKillNumberBox.Value = 100;
            EditorGoodiesAsNewToggle.IsOn = false;
            ApplyEditorPreset("QUICK");
            EditorOutputTextBox.Text = "Select a career save to begin. Use this page for the normal `.bes` patch workflow.";
            UpdateEditorActionState();
        }

        private void LoadEditorDetectedFiles()
        {
            string selectedPath = (EditorDetectedFilesComboBox.SelectedItem as SaveAnalyzerFileItem)?.Path
                ?? (EditorInputFileTextBox.Text ?? string.Empty).Trim();
            string? gameDir = AppConfig.Load().GetGameDir();
            _editorDetectedFiles = SaveEditorService.GetDetectedCareerSaves(gameDir);
            EditorDetectedFilesComboBox.ItemsSource = _editorDetectedFiles;
            RestoreEditorDetectedFileSelection(selectedPath);
            EditorDetectedFilesStatusTextBlock.Text = _editorDetectedFiles.Count == 0
                ? "No .bes career saves were detected. Set the game directory in Settings or browse manually."
                : $"{_editorDetectedFiles.Count} detected career save(s) available.";
        }

        private void RestoreAnalyzerDetectedFileSelection(string? selectedPath)
        {
            if (string.IsNullOrWhiteSpace(selectedPath))
            {
                return;
            }

            SaveAnalyzerFileItem? match = _detectedFiles.FirstOrDefault(item =>
                string.Equals(item.Path, selectedPath, StringComparison.OrdinalIgnoreCase));
            if (match is not null)
            {
                DetectedFilesComboBox.SelectedItem = match;
            }
        }

        private void RestoreEditorDetectedFileSelection(string? selectedPath)
        {
            if (string.IsNullOrWhiteSpace(selectedPath))
            {
                return;
            }

            SaveAnalyzerFileItem? match = _editorDetectedFiles.FirstOrDefault(item =>
                string.Equals(item.Path, selectedPath, StringComparison.OrdinalIgnoreCase));
            if (match is not null)
            {
                EditorDetectedFilesComboBox.SelectedItem = match;
            }
        }

        private void UpdateActionState()
        {
            string filePath = (FilePathTextBox.Text ?? string.Empty).Trim();
            string comparePath = (CompareFilePathTextBox.Text ?? string.Empty).Trim();
            bool hasFile = File.Exists(filePath);
            bool hasCompare = File.Exists(comparePath);

            AnalyzeButton.IsEnabled = hasFile;
            CompareButton.IsEnabled = hasFile && hasCompare;
            CopyReportButton.IsEnabled = !string.IsNullOrWhiteSpace(ReportTextBox.Text);
        }

        private async void BrowseFileButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bes", ".bea", "*" });
            if (!string.IsNullOrWhiteSpace(path))
            {
                FilePathTextBox.Text = path;
                AppStatusService.SetStatus($"Saves: selected {Path.GetFileName(path)}");
                AnalyzeCurrentFile();
            }
        }

        private async void BrowseCompareFileButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bes", ".bea", "*" });
            if (!string.IsNullOrWhiteSpace(path))
            {
                CompareFilePathTextBox.Text = path;
                AppStatusService.SetStatus($"Saves: selected compare file {Path.GetFileName(path)}");
            }
        }

        private void RefreshDetectedFilesButton_Click(object sender, RoutedEventArgs e)
        {
            LoadDetectedFiles();
            AppStatusService.SetStatus($"Saves: refreshed detected file list ({_detectedFiles.Count})");
        }

        private void DetectedFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (DetectedFilesComboBox.SelectedItem is SaveAnalyzerFileItem selected)
            {
                FilePathTextBox.Text = selected.Path;
                AppStatusService.SetStatus($"Saves: selected {selected.Name}");
                AnalyzeCurrentFile();
            }
        }

        private void FilePathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateActionState();
        }

        private void CompareFilePathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateActionState();
        }

        private void AnalyzeButton_Click(object sender, RoutedEventArgs e)
        {
            AnalyzeCurrentFile();
        }

        private void CompareButton_Click(object sender, RoutedEventArgs e)
        {
            string leftPath = (FilePathTextBox.Text ?? string.Empty).Trim();
            string rightPath = (CompareFilePathTextBox.Text ?? string.Empty).Trim();
            if (!File.Exists(leftPath) || !File.Exists(rightPath))
            {
                AnalyzerInfoBar.Title = "Comparison needs two files";
                AnalyzerInfoBar.Message = "Choose a valid source file and a valid compare file before running comparison mode.";
                AnalyzerInfoBar.Severity = InfoBarSeverity.Warning;
                AppStatusService.SetStatus("Saves: comparison needs both files");
                UpdateActionState();
                return;
            }

            try
            {
                RenderDocument(SaveAnalyzerService.CompareFiles(leftPath, rightPath));
            }
            catch (Exception ex)
            {
                RenderError("Comparison failed", $"Error comparing files: {ex.Message}");
            }
        }

        private void DisplayOption_Toggled(object sender, RoutedEventArgs e)
        {
            if (_currentDocument is { IsComparisonMode: false } && File.Exists((FilePathTextBox.Text ?? string.Empty).Trim()))
            {
                AnalyzeCurrentFile();
            }
        }

        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            DetectedFilesComboBox.SelectedItem = null;
            FilePathTextBox.Text = string.Empty;
            CompareFilePathTextBox.Text = string.Empty;
            ResetAnalyzerSurface();
            AppStatusService.SetStatus("Saves: analyzer cleared");
        }

        private void CopyReportButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(ReportTextBox.Text))
            {
                return;
            }

            DataPackage package = new();
            package.SetText(ReportTextBox.Text);
            Clipboard.SetContent(package);
            AppStatusService.SetStatus("Saves: copied analyzer report");
        }

        private void AnalyzeCurrentFile()
        {
            string filePath = (FilePathTextBox.Text ?? string.Empty).Trim();
            if (!File.Exists(filePath))
            {
                AnalyzerInfoBar.Title = "Analyzer needs a valid file";
                AnalyzerInfoBar.Message = "Choose a valid `.bes` or `.bea` path before running analysis.";
                AnalyzerInfoBar.Severity = InfoBarSeverity.Warning;
                AppStatusService.SetStatus("Saves: no valid file selected");
                UpdateActionState();
                return;
            }

            try
            {
                RenderDocument(SaveAnalyzerService.AnalyzeFile(
                    filePath,
                    verbose: VerboseToggle.IsOn,
                    dumpMystery: DumpMysteryToggle.IsOn));
            }
            catch (Exception ex)
            {
                RenderError("Analysis failed", $"Error analyzing file: {ex.Message}");
            }
        }

        private void RenderDocument(SaveAnalyzerDocument document)
        {
            _currentDocument = document;
            AnalyzerTitleTextBlock.Text = document.Title;
            AnalyzerModeTextBlock.Text = document.ModeText;
            SummaryTitleTextBlock.Text = document.SummaryTitle;
            ReportTextBox.Text = document.ReportText;

            PopulateMetricCards(document.Metrics);
            PopulateSummaryTree(document.SummaryNodes);

            AnalyzerInfoBar.Title = document.IsComparisonMode ? "Comparison complete" : "Analysis complete";
            AnalyzerInfoBar.Message = document.StatusText;
            AnalyzerInfoBar.Severity = document.ReportText.Contains("ERROR:", StringComparison.OrdinalIgnoreCase)
                ? InfoBarSeverity.Warning
                : InfoBarSeverity.Success;

            AppStatusService.SetStatus(document.StatusText);
            UpdateActionState();
        }

        private void RenderError(string title, string message)
        {
            _currentDocument = null;
            AnalyzerInfoBar.Title = title;
            AnalyzerInfoBar.Message = message;
            AnalyzerInfoBar.Severity = InfoBarSeverity.Error;
            ReportTextBox.Text = message;
            SummaryTreeView.RootNodes.Clear();
            SummaryTreeView.RootNodes.Add(new TreeViewNode { Content = message, IsExpanded = true });
            AppStatusService.SetStatus($"Saves: {message}");
            UpdateActionState();
        }

        private void ResetAnalyzerSurface()
        {
            _currentDocument = null;
            AnalyzerInfoBar.Title = "Analyzer ready";
            AnalyzerInfoBar.Message = "Choose a detected or manual file path to inspect save structure, options state, and comparison data.";
            AnalyzerInfoBar.Severity = InfoBarSeverity.Informational;
            AnalyzerTitleTextBlock.Text = "Save Analyzer";
            AnalyzerModeTextBlock.Text = "Single-file analysis: choose a .bes or .bea file to inspect.";
            SummaryTitleTextBlock.Text = "Analysis Summary";
            ReportTextBox.Text = string.Empty;
            SummaryTreeView.RootNodes.Clear();
            SummaryTreeView.RootNodes.Add(new TreeViewNode
            {
                Content = "No analysis yet. Select a detected file or browse for a .bes / .bea file to inspect.",
                IsExpanded = true
            });

            PopulateMetricCards(Array.Empty<SaveAnalyzerMetric>());
            UpdateActionState();
        }

        private void PopulateMetricCards(IReadOnlyList<SaveAnalyzerMetric> metrics)
        {
            SetMetricCard(Metric1LabelTextBlock, Metric1ValueTextBlock, Metric1DetailTextBlock, metrics.ElementAtOrDefault(0));
            SetMetricCard(Metric2LabelTextBlock, Metric2ValueTextBlock, Metric2DetailTextBlock, metrics.ElementAtOrDefault(1));
            SetMetricCard(Metric3LabelTextBlock, Metric3ValueTextBlock, Metric3DetailTextBlock, metrics.ElementAtOrDefault(2));
            SetMetricCard(Metric4LabelTextBlock, Metric4ValueTextBlock, Metric4DetailTextBlock, metrics.ElementAtOrDefault(3));
            SetMetricCard(Metric5LabelTextBlock, Metric5ValueTextBlock, Metric5DetailTextBlock, metrics.ElementAtOrDefault(4));
        }

        private static void SetMetricCard(TextBlock labelBlock, TextBlock valueBlock, TextBlock detailBlock, SaveAnalyzerMetric? metric)
        {
            labelBlock.Text = metric?.Label ?? "--";
            valueBlock.Text = metric?.Value ?? "--";
            detailBlock.Text = metric?.Detail ?? string.Empty;
        }

        private void PopulateSummaryTree(IReadOnlyList<SaveAnalyzerTreeNode> nodes)
        {
            SummaryTreeView.RootNodes.Clear();
            foreach (SaveAnalyzerTreeNode node in nodes)
            {
                SummaryTreeView.RootNodes.Add(BuildNode(node));
            }
        }

        private void RefreshEditorDetectedFilesButton_Click(object sender, RoutedEventArgs e)
        {
            LoadEditorDetectedFiles();
            AppStatusService.SetStatus($"Save Editor: refreshed detected save list ({_editorDetectedFiles.Count})");
        }

        private void EditorDetectedFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (EditorDetectedFilesComboBox.SelectedItem is SaveAnalyzerFileItem selected)
            {
                EditorInputFileTextBox.Text = selected.Path;
                EditorOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(selected.Path);
                ValidateEditorInputPath();
                LoadEditorAdvancedSnapshot();
                AppStatusService.SetStatus($"Save Editor: selected {selected.Name}");
            }
        }

        private async void BrowseEditorInputButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".bes", "*" });
            if (!string.IsNullOrWhiteSpace(path))
            {
                EditorInputFileTextBox.Text = path;
                if (string.IsNullOrWhiteSpace(EditorOutputFileTextBox.Text))
                {
                    EditorOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(path);
                }
                ValidateEditorInputPath();
                LoadEditorAdvancedSnapshot();
            }
        }

        private async void BrowseEditorOutputButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? folder = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
            if (string.IsNullOrWhiteSpace(folder))
            {
                return;
            }

            string inputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim();
            string fileName = File.Exists(inputPath)
                ? Path.GetFileName(SaveEditorService.BuildDefaultSaveOutputPath(inputPath))
                : "career_patched.bes";
            EditorOutputFileTextBox.Text = Path.Combine(folder, fileName);
            UpdateEditorActionState();
        }

        private void EditorPathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (ReferenceEquals(sender, EditorInputFileTextBox) && string.IsNullOrWhiteSpace(EditorOutputFileTextBox.Text))
            {
                string inputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim();
                if (inputPath.Length > 0 && !SaveEditorService.IsOptionsLikeFilePath(inputPath))
                {
                    EditorOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(inputPath);
                }
            }

            ValidateEditorInputPath();
            if (ReferenceEquals(sender, EditorInputFileTextBox))
            {
                LoadEditorAdvancedSnapshot();
            }
        }

        private void EditorPatchPresetComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_suppressEditorPresetSync)
            {
                return;
            }

            string preset = (EditorPatchPresetComboBox.SelectedItem as ComboBoxItem)?.Tag as string ?? "QUICK";
            ApplyEditorPreset(preset);
            UpdateEditorActionState();
        }

        private void EditorPatchSectionCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (!_suppressEditorPresetSync)
            {
                UpdateEditorPresetSelection();
            }

            UpdateEditorActionState();
        }

        private void EditorKillsOnlyCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            bool killsOnly = EditorKillsOnlyCheckBox.IsChecked == true;

            if (killsOnly)
            {
                _editorRestoreNodes = EditorPatchNodesCheckBox.IsChecked == true;
                _editorRestoreLinks = EditorPatchLinksCheckBox.IsChecked == true;
                _editorRestoreGoodies = EditorPatchGoodiesCheckBox.IsChecked == true;
                _editorRestoreKills = EditorPatchKillsCheckBox.IsChecked == true;
                _editorKillsOnlyRestoreCaptured = true;

                EditorPatchNodesCheckBox.IsChecked = false;
                EditorPatchLinksCheckBox.IsChecked = false;
                EditorPatchGoodiesCheckBox.IsChecked = false;
                EditorPatchKillsCheckBox.IsChecked = true;
            }
            else if (_editorKillsOnlyRestoreCaptured)
            {
                EditorPatchNodesCheckBox.IsChecked = _editorRestoreNodes;
                EditorPatchLinksCheckBox.IsChecked = _editorRestoreLinks;
                EditorPatchGoodiesCheckBox.IsChecked = _editorRestoreGoodies;
                EditorPatchKillsCheckBox.IsChecked = _editorRestoreKills;
            }

            EditorPatchNodesCheckBox.IsEnabled = !killsOnly;
            EditorPatchLinksCheckBox.IsEnabled = !killsOnly;
            EditorPatchGoodiesCheckBox.IsEnabled = !killsOnly;
            EditorPatchKillsCheckBox.IsEnabled = !killsOnly;

            UpdateEditorPresetSelection();
            UpdateEditorActionState();
        }

        private void EditorQuickSettingSelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateEditorActionState();
        }

        private void EditorQuickSettingToggled(object sender, RoutedEventArgs e)
        {
            UpdateEditorActionState();
        }

        private void EditorGlobalKillNumberBox_ValueChanged(NumberBox sender, NumberBoxValueChangedEventArgs args)
        {
            UpdateEditorActionState();
        }

        private async void EditorPatchButton_Click(object sender, RoutedEventArgs e)
        {
            SavePatchRequest request = BuildEditorRequest(out string? advancedError);
            if (!string.IsNullOrWhiteSpace(advancedError))
            {
                EditorOutputTextBox.Text = advancedError;
                EditorInfoBar.Title = "Save patch blocked";
                EditorInfoBar.Message = advancedError;
                EditorInfoBar.Severity = InfoBarSeverity.Warning;
                AppStatusService.SetStatus("Save Editor: invalid advanced override");
                UpdateEditorActionState();
                return;
            }

            string outputPath = request.OutputPath.Trim();

            if (File.Exists(outputPath) &&
                !await ConfirmAsync(
                    "Overwrite output file?",
                    $"The output file already exists:\n{outputPath}\n\nOverwrite it?"))
            {
                AppStatusService.SetStatus("Save Editor: overwrite canceled");
                return;
            }

            EditorPatchButton.IsEnabled = false;
            EditorOutputTextBox.Text = "Patching save...";
            AppStatusService.SetStatus("Save Editor: patching save...");

            PatchResult result = SaveEditorService.PatchSave(request);
            EditorOutputTextBox.Text = result.Message;
            EditorCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(result.Message);
            EditorInfoBar.Title = result.Success ? "Save patch complete" : "Save patch blocked";
            EditorInfoBar.Message = result.Message;
            EditorInfoBar.Severity = result.Success ? InfoBarSeverity.Success : InfoBarSeverity.Warning;
            AppStatusService.SetStatus(result.Success ? "Save Editor: patch complete" : "Save Editor: patch failed");
            UpdateEditorActionState();
        }

        private void EditorCopyOutputButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(EditorOutputTextBox.Text))
            {
                return;
            }

            DataPackage package = new();
            package.SetText(EditorOutputTextBox.Text);
            Clipboard.SetContent(package);
            AppStatusService.SetStatus("Save Editor: copied output");
        }

        private void ValidateEditorInputPath()
        {
            string inputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim();
            if (inputPath.Length == 0)
            {
                _editorInputValid = false;
                UpdateEditorActionState();
                return;
            }

            _editorInputValid = File.Exists(inputPath)
                && !SaveEditorService.IsOptionsLikeFilePath(inputPath)
                && BesFilePatcher.IsValidBesFile(inputPath);

            UpdateEditorActionState();
        }

        private SavePatchRequest BuildEditorRequest(out string? advancedError)
        {
            TryBuildEditorAdvancedOverrides(out Dictionary<int, string>? levelRanks, out Dictionary<int, int>? perCategoryKills, out advancedError);
            return new SavePatchRequest
            {
                InputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim(),
                OutputPath = (EditorOutputFileTextBox.Text ?? string.Empty).Trim(),
                Rank = (EditorRankComboBox.SelectedItem as ComboBoxItem)?.Tag as string ?? "S",
                UseNewGoodiesInstead = EditorGoodiesAsNewToggle.IsOn,
                GlobalKillCount = ClampNumberBoxToInt(EditorGlobalKillNumberBox, fallback: 100),
                PatchNodes = EditorPatchNodesCheckBox.IsChecked == true,
                PatchLinks = EditorPatchLinksCheckBox.IsChecked == true,
                PatchGoodies = EditorPatchGoodiesCheckBox.IsChecked == true,
                PatchKills = EditorPatchKillsCheckBox.IsChecked == true,
                LevelRanks = levelRanks,
                PerCategoryKills = perCategoryKills
            };
        }

        private void ApplyEditorPreset(string preset)
        {
            _suppressEditorPresetSync = true;
            try
            {
                switch (preset)
                {
                    case "SAFE":
                        EditorKillsOnlyCheckBox.IsChecked = false;
                        EditorPatchNodesCheckBox.IsChecked = false;
                        EditorPatchLinksCheckBox.IsChecked = false;
                        EditorPatchGoodiesCheckBox.IsChecked = false;
                        EditorPatchKillsCheckBox.IsChecked = false;
                        break;
                    case "QUICK":
                    default:
                        EditorKillsOnlyCheckBox.IsChecked = false;
                        EditorPatchNodesCheckBox.IsChecked = true;
                        EditorPatchLinksCheckBox.IsChecked = true;
                        EditorPatchGoodiesCheckBox.IsChecked = true;
                        EditorPatchKillsCheckBox.IsChecked = true;
                        break;
                }

                EditorPatchNodesCheckBox.IsEnabled = true;
                EditorPatchLinksCheckBox.IsEnabled = true;
                EditorPatchGoodiesCheckBox.IsEnabled = true;
                EditorPatchKillsCheckBox.IsEnabled = true;
            }
            finally
            {
                _suppressEditorPresetSync = false;
            }
        }

        private void UpdateEditorPresetSelection()
        {
            bool quick =
                EditorKillsOnlyCheckBox.IsChecked != true &&
                EditorPatchNodesCheckBox.IsChecked == true &&
                EditorPatchLinksCheckBox.IsChecked == true &&
                EditorPatchGoodiesCheckBox.IsChecked == true &&
                EditorPatchKillsCheckBox.IsChecked == true;

            bool safe =
                EditorKillsOnlyCheckBox.IsChecked != true &&
                EditorPatchNodesCheckBox.IsChecked != true &&
                EditorPatchLinksCheckBox.IsChecked != true &&
                EditorPatchGoodiesCheckBox.IsChecked != true &&
                EditorPatchKillsCheckBox.IsChecked != true;

            string target = quick ? "QUICK" : safe ? "SAFE" : "CUSTOM";
            _suppressEditorPresetSync = true;
            try
            {
                foreach (ComboBoxItem item in EditorPatchPresetComboBox.Items.OfType<ComboBoxItem>())
                {
                    if (string.Equals(item.Tag as string, target, StringComparison.Ordinal))
                    {
                        EditorPatchPresetComboBox.SelectedItem = item;
                        break;
                    }
                }
            }
            finally
            {
                _suppressEditorPresetSync = false;
            }
        }

        private void UpdateEditorActionState()
        {
            SavePatchRequest request = BuildEditorRequest(out string? advancedError);
            bool hasSections = SaveEditorService.HasAnySelectedSection(request);
            bool outputIsSaveLike = !SaveEditorService.IsOptionsLikeFilePath(request.OutputPath);
            bool samePath = AreSamePaths(request.InputPath, request.OutputPath);
            bool hasInput = !string.IsNullOrWhiteSpace(request.InputPath);
            bool hasOutput = !string.IsNullOrWhiteSpace(request.OutputPath);
            int missionOverrideCount = SaveEditorAdvancedService.CountMissionRankOverrides(_editorMissionRankRows);
            int categoryKillOverrideCount = SaveEditorAdvancedService.CountCategoryKillOverrides(_editorCategoryKillRows);

            EditorPendingChangesTextBlock.Text = SaveEditorService.BuildPendingChangesSummary(request);

            if (!_editorInputValid && hasInput)
            {
                EditorSafetyHintTextBlock.Text = "Input must be a valid .bes career save before patching is enabled.";
            }
            else if (!string.IsNullOrWhiteSpace(advancedError))
            {
                EditorSafetyHintTextBlock.Text = advancedError;
            }
            else if (!hasSections)
            {
                EditorSafetyHintTextBlock.Text = "Choose at least one save section to patch.";
            }
            else if (missionOverrideCount > 0 && request.PatchNodes != true)
            {
                EditorSafetyHintTextBlock.Text = "Mission rank overrides require `Patch missions` because the retail patcher applies per-mission ranks through the node pass.";
            }
            else if (categoryKillOverrideCount > 0 && request.PatchKills != true)
            {
                EditorSafetyHintTextBlock.Text = "Category kill overrides require `Patch kill counts` because the retail patcher applies per-category values through the kill pass.";
            }
            else if (samePath)
            {
                EditorSafetyHintTextBlock.Text = "Output file must be different from input file. In-place save patching remains blocked.";
            }
            else if (!outputIsSaveLike)
            {
                EditorSafetyHintTextBlock.Text = "Output path must remain a .bes career save path.";
            }
            else
            {
                EditorSafetyHintTextBlock.Text = "Save patching is ready. Mission rank and category-kill overrides are supported here; startup settings and keybind overrides still belong in Configuration Editor.";
            }

            EditorPatchButton.IsEnabled =
                _editorInputValid &&
                hasInput &&
                hasOutput &&
                hasSections &&
                string.IsNullOrWhiteSpace(advancedError) &&
                !samePath &&
                outputIsSaveLike;
            EditorCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(EditorOutputTextBox.Text);
        }

        private static int ClampNumberBoxToInt(NumberBox numberBox, int fallback)
        {
            if (double.IsNaN(numberBox.Value) || double.IsInfinity(numberBox.Value))
            {
                return fallback;
            }

            double clamped = Math.Max(0, Math.Min(16777215, numberBox.Value));
            return (int)Math.Round(clamped, MidpointRounding.AwayFromZero);
        }

        private static bool AreSamePaths(string? left, string? right)
        {
            if (string.IsNullOrWhiteSpace(left) || string.IsNullOrWhiteSpace(right))
            {
                return false;
            }

            try
            {
                return string.Equals(
                    Path.GetFullPath(left.Trim()),
                    Path.GetFullPath(right.Trim()),
                    StringComparison.OrdinalIgnoreCase);
            }
            catch
            {
                return false;
            }
        }

        private async System.Threading.Tasks.Task<bool> ConfirmAsync(string title, string body)
        {
            ContentDialog dialog = new()
            {
                Title = title,
                Content = new TextBlock
                {
                    Text = body,
                    TextWrapping = TextWrapping.WrapWholeWords
                },
                PrimaryButtonText = "Continue",
                CloseButtonText = "Cancel",
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = XamlRoot
            };

            return await dialog.ShowAsync() == ContentDialogResult.Primary;
        }

        private static TreeViewNode BuildNode(SaveAnalyzerTreeNode source)
        {
            TreeViewNode node = new()
            {
                Content = source.Label,
                IsExpanded = true
            };

            foreach (SaveAnalyzerTreeNode child in source.Children)
            {
                node.Children.Add(BuildNode(child));
            }

            return node;
        }
    }
}
