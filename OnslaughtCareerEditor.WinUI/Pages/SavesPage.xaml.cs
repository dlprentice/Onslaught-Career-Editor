using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;
using Windows.ApplicationModel.DataTransfer;
using Windows.System;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class SavesPage : Page
    {
        private const int SaveAnalyzerTabIndex = 0;
        private const int SaveEditorTabIndex = 1;
        private const int ConfigurationEditorTabIndex = 2;
        private static readonly Uri ZigguratControllerGuideUri = new("https://steamcommunity.com/app/1346400/discussions/0/2942494909163878759/");

        private IReadOnlyList<SaveAnalyzerFileItem> _detectedFiles = Array.Empty<SaveAnalyzerFileItem>();
        private IReadOnlyList<SaveAnalyzerFileItem> _editorDetectedFiles = Array.Empty<SaveAnalyzerFileItem>();
        private SaveAnalyzerDocument? _currentDocument;
        private bool _editorInputValid;
        private bool _editorOutputWasAutoSuggested;
        private bool _suppressEditorOutputProvenance;
        private bool _suppressEditorPresetSync;
        private bool _editorKillsOnlyRestoreCaptured;
        private bool _editorRestoreNodes = true;
        private bool _editorRestoreLinks = true;
        private bool _editorRestoreGoodies = true;
        private bool _editorRestoreKills = true;
        private Models.SaveEditorCompletionState? _lastWrittenCompletion;
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
            SelectSavesTab(GetInitialSaveTabIndex(), persistSelection: false);
        }

        private void SaveAnalyzerTabButton_Click(object sender, RoutedEventArgs e) => SelectSavesTab(SaveAnalyzerTabIndex);

        private void SaveEditorTabButton_Click(object sender, RoutedEventArgs e) => SelectSavesTab(SaveEditorTabIndex);

        private void ConfigurationEditorTabButton_Click(object sender, RoutedEventArgs e) => SelectSavesTab(ConfigurationEditorTabIndex);

        private async void OpenZigguratControllerGuideButton_Click(object sender, RoutedEventArgs e)
        {
            await Launcher.LaunchUriAsync(ZigguratControllerGuideUri);
        }

        public void NavigateToSubTab(int tabIndex) => SelectSavesTab(tabIndex);

        private void SetAnalyzerInfoBar(string title, string message, InfoBarSeverity severity)
        {
            AnalyzerInfoBar.Title = title;
            AnalyzerInfoBar.Message = message;
            AnalyzerInfoBar.Severity = severity;
            AnalyzerInfoBar.Visibility = Visibility.Visible;
        }

        private void AnalyzeTaskButton_Click(object sender, RoutedEventArgs e)
        {
            SelectSavesTab(SaveAnalyzerTabIndex);
            FilePathTextBox.Focus(FocusState.Programmatic);
        }

        private void EditSaveTaskButton_Click(object sender, RoutedEventArgs e)
        {
            SelectSavesTab(SaveEditorTabIndex);
            EditorInputFileTextBox.Focus(FocusState.Programmatic);
        }

        private void ConfigureOptionsTaskButton_Click(object sender, RoutedEventArgs e)
        {
            SelectSavesTab(ConfigurationEditorTabIndex);
            ConfigurationInputFileTextBox.Focus(FocusState.Programmatic);
        }

        private static int GetInitialSaveTabIndex()
        {
            string? testInitialTab = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB");
            if (int.TryParse(testInitialTab, out int requestedTab)
                && requestedTab is >= SaveAnalyzerTabIndex and <= ConfigurationEditorTabIndex)
            {
                return requestedTab;
            }

            return Math.Clamp(AppConfig.Load().LastSaveSubTab, SaveAnalyzerTabIndex, ConfigurationEditorTabIndex);
        }

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
                ConfigurationEditorTabIndex => "Game Options: global options ready",
                _ => "Save Lab: analyzer ready"
            });
        }

        private void LoadDetectedFiles()
        {
            string selectedPath = (DetectedFilesComboBox.SelectedItem as SaveAnalyzerFileItem)?.Path
                ?? (FilePathTextBox.Text ?? string.Empty).Trim();
            string? gameDir = AppConfig.Load().GetGameDirOrDetect(persistDetection: true);
            _detectedFiles = SaveAnalyzerService.GetDetectedFiles(gameDir);
            DetectedFilesComboBox.ItemsSource = _detectedFiles;
            DetectedFilesComboBox.PlaceholderText = _detectedFiles.Count == 0
                ? "No detected files yet"
                : "Choose a detected file";
            RestoreAnalyzerDetectedFileSelection(selectedPath);
            DetectedFilesStatusTextBlock.Text = _detectedFiles.Count == 0
                ? "No save or options files were detected. Set the game directory in Settings or browse manually."
                : $"{_detectedFiles.Count} detected file(s) available.";
        }

        private void InitializeEditorSurface()
        {
            EditorRankComboBox.SelectedIndex = 0;
            EditorPatchPresetComboBox.SelectedIndex = 0;
            EditorFocusedGoodieIdNumberBox.Value = 2;
            EditorFocusedGoodieStateComboBox.SelectedIndex = 2;
            EditorGlobalKillNumberBox.Value = 100;
            EditorGoodiesAsNewToggle.IsOn = false;
            ApplyEditorPreset("SAFE");
            EditorOutputTextBox.Text = "Select a career save to begin. Use this page for the normal .bes patch workflow.";
            UpdateEditorActionState();
        }

        private void LoadEditorDetectedFiles()
        {
            string selectedPath = (EditorDetectedFilesComboBox.SelectedItem as SaveAnalyzerFileItem)?.Path
                ?? (EditorInputFileTextBox.Text ?? string.Empty).Trim();
            string? gameDir = AppConfig.Load().GetGameDirOrDetect(persistDetection: true);
            _editorDetectedFiles = SaveEditorService.GetDetectedCareerSaves(gameDir);
            EditorDetectedFilesComboBox.ItemsSource = _editorDetectedFiles;
            EditorDetectedFilesComboBox.PlaceholderText = _editorDetectedFiles.Count == 0
                ? "No detected career saves yet"
                : "Choose a career save";
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
                AppStatusService.SetStatus($"Save Lab: selected {Path.GetFileName(path)}");
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
                AppStatusService.SetStatus($"Save Lab: selected compare file {Path.GetFileName(path)}");
            }
        }

        private void RefreshDetectedFilesButton_Click(object sender, RoutedEventArgs e)
        {
            LoadDetectedFiles();
            AppStatusService.SetStatus($"Save Lab: refreshed detected file list ({_detectedFiles.Count})");
        }

        private void DetectedFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (DetectedFilesComboBox.SelectedItem is SaveAnalyzerFileItem selected)
            {
                FilePathTextBox.Text = selected.Path;
                AppStatusService.SetStatus($"Save Lab: selected {selected.Name}");
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
                SetAnalyzerInfoBar(
                    "Comparison needs two files",
                    "Choose a valid source file and a valid compare file before running comparison mode.",
                    InfoBarSeverity.Warning);
                AppStatusService.SetStatus("Save Lab: comparison needs both files");
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
            AppStatusService.SetStatus("Save Lab: analyzer cleared");
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
            AppStatusService.SetStatus("Save Lab: copied analyzer report");
        }

        private void AnalyzeCurrentFile()
        {
            string filePath = (FilePathTextBox.Text ?? string.Empty).Trim();
            if (!File.Exists(filePath))
            {
                SetAnalyzerInfoBar(
                    "Analyzer needs a valid file",
                    "Choose a valid .bes or .bea path before running analysis.",
                    InfoBarSeverity.Warning);
                AppStatusService.SetStatus("Save Lab: no valid file selected");
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
            AnalyzerEmptyStateBorder.Visibility = Visibility.Collapsed;
            AnalyzerHeaderGrid.Visibility = Visibility.Visible;
            AnalyzerHeaderGrid.MaxHeight = double.PositiveInfinity;
            AnalyzerHeaderGrid.Opacity = 1;
            AnalyzerMetricsGrid.Visibility = Visibility.Visible;
            AnalyzerMetricsGrid.MaxHeight = double.PositiveInfinity;
            AnalyzerMetricsGrid.Opacity = 1;
            AnalyzerTitleTextBlock.Text = document.Title;
            AnalyzerModeTextBlock.Text = document.ModeText;
            SummaryTitleTextBlock.Text = document.SummaryTitle;
            ReportTextBox.Text = document.ReportText;

            PopulateMetricCards(document.Metrics);
            PopulateSummaryTree(document.SummaryNodes);

            SetAnalyzerInfoBar(
                document.IsComparisonMode ? "Comparison complete" : "Analysis complete",
                document.StatusText,
                document.ReportText.Contains("ERROR:", StringComparison.OrdinalIgnoreCase)
                    ? InfoBarSeverity.Warning
                    : InfoBarSeverity.Success);

            AppStatusService.SetStatus(document.StatusText);
            UpdateActionState();
        }

        private void RenderError(string title, string message)
        {
            _currentDocument = null;
            AnalyzerEmptyStateBorder.Visibility = Visibility.Collapsed;
            AnalyzerHeaderGrid.Visibility = Visibility.Collapsed;
            AnalyzerHeaderGrid.MaxHeight = 0;
            AnalyzerHeaderGrid.Opacity = 0;
            AnalyzerMetricsGrid.Visibility = Visibility.Collapsed;
            AnalyzerMetricsGrid.MaxHeight = 0;
            AnalyzerMetricsGrid.Opacity = 0;
            SetAnalyzerInfoBar(title, message, InfoBarSeverity.Error);
            ReportTextBox.Text = message;
            SummaryTreeView.RootNodes.Clear();
            SummaryTreeView.RootNodes.Add(new TreeViewNode { Content = message, IsExpanded = true });
            AppStatusService.SetStatus($"Save Lab: {message}");
            UpdateActionState();
        }

        private void ResetAnalyzerSurface()
        {
            _currentDocument = null;
            AnalyzerEmptyStateBorder.Visibility = Visibility.Visible;
            AnalyzerHeaderGrid.Visibility = Visibility.Collapsed;
            AnalyzerHeaderGrid.MaxHeight = 0;
            AnalyzerHeaderGrid.Opacity = 0;
            AnalyzerMetricsGrid.Visibility = Visibility.Collapsed;
            AnalyzerMetricsGrid.MaxHeight = 0;
            AnalyzerMetricsGrid.Opacity = 0;
            SetAnalyzerInfoBar(
                "Analyzer ready",
                "Choose a detected or manual file path to inspect save structure, options state, and comparison data.",
                InfoBarSeverity.Informational);
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
                SetEditorSuggestedOutputPath(selected.Path);
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
                SetEditorSuggestedOutputPath(path);
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
            Models.SaveEditorOutputSelectionState outputState = SaveEditorJourneyStateMachine.ApplyManualOutput(
                new Models.SaveEditorOutputSelectionState(EditorOutputFileTextBox.Text ?? string.Empty, _editorOutputWasAutoSuggested),
                Path.Combine(folder, fileName));
            ApplyEditorOutputSelectionState(outputState);
            UpdateEditorActionState();
        }

        private void EditorPathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (ReferenceEquals(sender, EditorOutputFileTextBox) && !_suppressEditorOutputProvenance)
            {
                Models.SaveEditorOutputSelectionState outputState = SaveEditorJourneyStateMachine.ApplyManualOutput(
                    new Models.SaveEditorOutputSelectionState(EditorOutputFileTextBox.Text ?? string.Empty, _editorOutputWasAutoSuggested),
                    EditorOutputFileTextBox.Text ?? string.Empty);
                _editorOutputWasAutoSuggested = outputState.OutputWasAutoSuggested;
            }

            if (ReferenceEquals(sender, EditorInputFileTextBox)
                && (string.IsNullOrWhiteSpace(EditorOutputFileTextBox.Text) || _editorOutputWasAutoSuggested))
            {
                string inputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim();
                SetEditorSuggestedOutputPath(inputPath);
            }

            ValidateEditorInputPath();
            if (ReferenceEquals(sender, EditorInputFileTextBox))
            {
                LoadEditorAdvancedSnapshot();
            }
        }

        private void SetEditorSuggestedOutputPath(string inputPath)
        {
            if (!string.IsNullOrWhiteSpace(EditorOutputFileTextBox.Text) && !_editorOutputWasAutoSuggested)
            {
                return;
            }

            string suggestedPath = string.IsNullOrWhiteSpace(inputPath) || SaveEditorService.IsOptionsLikeFilePath(inputPath)
                ? string.Empty
                : SaveEditorService.BuildDefaultSaveOutputPath(inputPath);
            Models.SaveEditorOutputSelectionState outputState = SaveEditorJourneyStateMachine.ApplyInputSuggestion(
                new Models.SaveEditorOutputSelectionState(EditorOutputFileTextBox.Text ?? string.Empty, _editorOutputWasAutoSuggested),
                suggestedPath);
            ApplyEditorOutputSelectionState(outputState);
        }

        private void ApplyEditorOutputSelectionState(Models.SaveEditorOutputSelectionState outputState)
        {
            _suppressEditorOutputProvenance = true;
            try
            {
                EditorOutputFileTextBox.Text = outputState.OutputPath;
            }
            finally
            {
                _suppressEditorOutputProvenance = false;
            }

            _editorOutputWasAutoSuggested = outputState.OutputWasAutoSuggested;
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

        private void EditorFocusedGoodieIdNumberBox_ValueChanged(NumberBox sender, NumberBoxValueChangedEventArgs args)
        {
            UpdateEditorActionState();
        }

        private void EditorFocusedGoodieStateComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateEditorActionState();
        }

        private async void EditorPatchFocusedGoodieButton_Click(object sender, RoutedEventArgs e)
        {
            FocusedGoodieStatePatchRequest? request = BuildFocusedGoodieStateRequest(out string? validationError);
            if (request is null)
            {
                EditorOutputTextBox.Text = validationError ?? "Choose a valid focused Goodie ID and state.";
                EditorInfoBar.Title = "Focused Goodie patch blocked";
                EditorInfoBar.Message = EditorOutputTextBox.Text;
                EditorInfoBar.Severity = InfoBarSeverity.Warning;
                EditorInfoBar.Visibility = Visibility.Visible;
                AppStatusService.SetStatus("Save Editor: invalid focused Goodie edit");
                UpdateEditorActionState();
                return;
            }

            string outputPath = request.OutputPath.Trim();
            if (File.Exists(outputPath) &&
                !await ConfirmAsync(
                    "Overwrite output file?",
                    $"The output file already exists:\n{outputPath}\n\nOverwrite it?"))
            {
                AppStatusService.SetStatus("Save Editor: focused Goodie overwrite canceled");
                return;
            }

            EditorPatchFocusedGoodieButton.IsEnabled = false;
            EditorOutputTextBox.Text = "Writing one focused Goodie state...";
            AppStatusService.SetStatus("Save Editor: writing focused Goodie state...");

            PatchResult result = SaveEditorService.PatchFocusedGoodieState(request);
            ClearLastWrittenSave();
            string stateLabel = MissionScriptGoodieStateSaveCodec.GetStateLabel(request.State);
            string displayMessage = result.Success
                ? $"Goodie ID {request.GoodieId:000} was written as {stateLabel} to {BuildFileNameSummary(request.OutputPath, "the selected output file")}.\nThe source save was not modified. If this destination is a Safe Game Copy, the output is staged only in that verified copy's savegames folder."
                : ReplacePathWithLabel(
                    ReplacePathWithLabel(result.Message, request.InputPath, "selected input save"),
                    request.OutputPath,
                    "selected output file");

            EditorOutputTextBox.Text = displayMessage;
            EditorCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(result.Message);
            EditorInfoBar.Title = result.Success ? "Focused Goodie copy written" : "Focused Goodie patch blocked";
            EditorInfoBar.Message = displayMessage;
            EditorInfoBar.Severity = result.Success ? InfoBarSeverity.Success : InfoBarSeverity.Warning;
            EditorInfoBar.Visibility = Visibility.Visible;
            AppStatusService.SetStatus(result.Success ? "Save Editor: focused Goodie copy written" : "Save Editor: focused Goodie patch failed");
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
                EditorInfoBar.Visibility = Visibility.Visible;
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
            if (result.Success && File.Exists(outputPath))
            {
                _lastWrittenCompletion = SaveEditorJourneyStateMachine.RecordSuccessfulWrite(request, outputPath);
            }
            else
            {
                ClearLastWrittenSave();
            }

            string displayMessage = FormatEditorPatchResultForUi(result, request);
            EditorOutputTextBox.Text = displayMessage;
            EditorCopyOutputButton.IsEnabled = !string.IsNullOrWhiteSpace(result.Message);
            EditorInfoBar.Title = result.Success ? "Save patch complete" : "Save patch blocked";
            EditorInfoBar.Message = displayMessage;
            EditorInfoBar.Severity = result.Success ? InfoBarSeverity.Success : InfoBarSeverity.Warning;
            EditorInfoBar.Visibility = Visibility.Visible;
            AppStatusService.SetStatus(result.Success ? "Save Editor: patch complete" : "Save Editor: patch failed");
            UpdateEditorActionState();
        }

        private void SaveEditorShowWrittenSaveButton_Click(object sender, RoutedEventArgs e)
        {
            SavePatchRequest request = BuildEditorRequest(out string? advancedError);
            string outputPath;
            try
            {
                outputPath = Path.GetFullPath(request.OutputPath.Trim());
            }
            catch
            {
                FailWrittenSaveReveal(
                    "The written-copy details changed. Write the separate copy again before showing it.",
                    clearCompletion: true);
                return;
            }

            Models.SaveEditorCompletionEvaluation completion = SaveEditorJourneyStateMachine.EvaluateCompletion(
                _lastWrittenCompletion,
                request,
                File.Exists(outputPath),
                AppConfig.GetPatchedOutputDir());
            if (!string.IsNullOrWhiteSpace(advancedError) || !completion.IsCurrent || !completion.CanReveal)
            {
                _lastWrittenCompletion = SaveEditorJourneyStateMachine.ApplyRevealAttempt(
                    _lastWrittenCompletion,
                    preconditionsCurrent: false,
                    launcherSucceeded: false);
                FailWrittenSaveReveal(
                    "The written-copy details changed or the app-owned output is missing. Write the separate copy again before showing it.",
                    clearCompletion: true);
                return;
            }

            bool launcherSucceeded = ExplorerRevealService.TryReveal(outputPath);
            _lastWrittenCompletion = SaveEditorJourneyStateMachine.ApplyRevealAttempt(
                _lastWrittenCompletion,
                preconditionsCurrent: true,
                launcherSucceeded: launcherSucceeded);
            if (launcherSucceeded)
            {
                AppStatusService.SetStatus("Save Editor: showing written copy in File Explorer");
            }
            else
            {
                FailWrittenSaveReveal(
                    "File Explorer could not be opened. The successful written save remains unchanged in the app-owned output folder; try Show again.",
                    clearCompletion: false);
            }
        }

        private void FailWrittenSaveReveal(string message, bool clearCompletion)
        {
            if (clearCompletion)
            {
                ClearLastWrittenSave();
            }

            EditorInfoBar.Title = "Written copy could not be shown";
            EditorInfoBar.Message = message;
            EditorInfoBar.Severity = InfoBarSeverity.Warning;
            EditorInfoBar.Visibility = Visibility.Visible;
            AppStatusService.SetStatus("Save Editor: written-copy reveal blocked");
            UpdateEditorActionState();
        }

        private void ClearLastWrittenSave()
        {
            _lastWrittenCompletion = null;
        }

        private static string FormatEditorPatchResultForUi(PatchResult result, SavePatchRequest request)
        {
            if (result.Success)
            {
                string outputName = BuildFileNameSummary(request.OutputPath, "chosen output file");
                return $"Successfully patched copied save to selected output file.\nOutput file: {outputName}\nThe source save was not modified. Close the copied game first and back up any save you replace. The Toolkit does not install this file; to try it, manually copy it into a Safe Game Copy's savegames folder.";
            }

            return RedactEditorPatchPaths(result.Message, request);
        }

        private static string RedactEditorPatchPaths(string message, SavePatchRequest request)
        {
            string redacted = message;
            redacted = ReplacePathWithLabel(redacted, request.InputPath, "selected input save");
            redacted = ReplacePathWithLabel(redacted, request.OutputPath, "selected output file");
            return redacted;
        }

        private static string ReplacePathWithLabel(string message, string? path, string label)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return message;
            }

            string trimmedPath = path.Trim();
            message = message.Replace(trimmedPath, label, StringComparison.OrdinalIgnoreCase);
            try
            {
                string fullPath = Path.GetFullPath(trimmedPath);
                message = message.Replace(fullPath, label, StringComparison.OrdinalIgnoreCase);
            }
            catch
            {
                // The raw value may be an invalid path; the direct replacement above is still useful.
            }

            return message;
        }

        private static string BuildFileNameSummary(string? path, string fallback)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return fallback;
            }

            try
            {
                string fileName = Path.GetFileName(path.Trim());
                return string.IsNullOrWhiteSpace(fileName) ? fallback : fileName;
            }
            catch
            {
                return fallback;
            }
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

        private FocusedGoodieStatePatchRequest? BuildFocusedGoodieStateRequest(out string? error)
        {
            error = null;
            double rawId = EditorFocusedGoodieIdNumberBox.Value;
            if (double.IsNaN(rawId) || double.IsInfinity(rawId) || rawId != Math.Truncate(rawId))
            {
                error = "Goodie ID must be a whole number from 0 to 232.";
                return null;
            }

            int goodieId = (int)rawId;
            if ((uint)goodieId >= MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount)
            {
                error = "Goodie ID must be from 0 to 232.";
                return null;
            }

            string? stateTag = (EditorFocusedGoodieStateComboBox.SelectedItem as ComboBoxItem)?.Tag as string;
            if (!uint.TryParse(stateTag, out uint rawState) || rawState > MissionScriptGoodieStateSaveCodec.MaxKnownStateValue)
            {
                error = "Choose Locked, Locked with hint, New, or Old for the focused Goodie state.";
                return null;
            }

            return new FocusedGoodieStatePatchRequest
            {
                InputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim(),
                OutputPath = (EditorOutputFileTextBox.Text ?? string.Empty).Trim(),
                GoodieId = goodieId,
                State = (MissionScriptGoodieState)rawState
            };
        }

        private void ApplyEditorPreset(string preset)
        {
            _suppressEditorPresetSync = true;
            try
            {
                Models.SaveEditorSectionSelection current = BuildEditorSectionSelection();
                Models.SaveEditorPresetTransition transition = SaveEditorJourneyStateMachine.ApplyPreset(preset, current);
                EditorKillsOnlyCheckBox.IsChecked = transition.Selection.KillsOnly;
                EditorPatchNodesCheckBox.IsChecked = transition.Selection.PatchNodes;
                EditorPatchLinksCheckBox.IsChecked = transition.Selection.PatchLinks;
                EditorPatchGoodiesCheckBox.IsChecked = transition.Selection.PatchGoodies;
                EditorPatchKillsCheckBox.IsChecked = transition.Selection.PatchKills;
                EditorPatchNodesCheckBox.IsEnabled = !transition.Selection.KillsOnly;
                EditorPatchLinksCheckBox.IsEnabled = !transition.Selection.KillsOnly;
                EditorPatchGoodiesCheckBox.IsEnabled = !transition.Selection.KillsOnly;
                EditorPatchKillsCheckBox.IsEnabled = !transition.Selection.KillsOnly;
                SetEditorPresetSelection(transition.VisiblePreset);
            }
            finally
            {
                _suppressEditorPresetSync = false;
            }
        }

        private void UpdateEditorPresetSelection()
        {
            SetEditorPresetSelection(SaveEditorJourneyStateMachine.ClassifyPreset(BuildEditorSectionSelection()));
        }

        private Models.SaveEditorSectionSelection BuildEditorSectionSelection()
        {
            return new Models.SaveEditorSectionSelection(
                EditorKillsOnlyCheckBox.IsChecked == true,
                EditorPatchNodesCheckBox.IsChecked == true,
                EditorPatchLinksCheckBox.IsChecked == true,
                EditorPatchGoodiesCheckBox.IsChecked == true,
                EditorPatchKillsCheckBox.IsChecked == true);
        }

        private void SetEditorPresetSelection(string target)
        {
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
            FocusedGoodieStatePatchRequest? focusedGoodieRequest = BuildFocusedGoodieStateRequest(out string? focusedGoodieError);
            bool hasSections = SaveEditorService.HasAnySelectedSection(request);
            bool outputIsSaveLike = SaveEditorService.IsCareerSaveFilePath(request.OutputPath);
            bool samePath = AreSamePaths(request.InputPath, request.OutputPath);
            bool hasInput = !string.IsNullOrWhiteSpace(request.InputPath);
            bool hasOutput = !string.IsNullOrWhiteSpace(request.OutputPath);
            int missionOverrideCount = SaveEditorAdvancedService.CountMissionRankOverrides(_editorMissionRankRows);
            int categoryKillOverrideCount = SaveEditorAdvancedService.CountCategoryKillOverrides(_editorCategoryKillRows);
            bool overrideDependenciesSatisfied =
                (missionOverrideCount == 0 || request.PatchNodes)
                && (categoryKillOverrideCount == 0 || request.PatchKills);

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
                EditorSafetyHintTextBlock.Text = "Mission rank overrides require Patch missions because the retail patcher applies per-mission ranks through the node pass.";
            }
            else if (categoryKillOverrideCount > 0 && request.PatchKills != true)
            {
                EditorSafetyHintTextBlock.Text = "Category kill overrides require Patch kill counts because the retail patcher applies per-category values through the kill pass.";
            }
            else if (samePath)
            {
                EditorSafetyHintTextBlock.Text = "Output file must be different from input file. In-place save patching remains blocked.";
            }
            else if (!outputIsSaveLike)
            {
                EditorSafetyHintTextBlock.Text = "Output path must end in .bes and stay outside every game folder.";
            }
            else
            {
                EditorSafetyHintTextBlock.Text = "Save patching is ready. Mission rank and category-kill overrides are supported here; startup settings and keybind overrides still belong in Game Options.";
            }

            bool canWrite =
                _editorInputValid &&
                hasInput &&
                hasOutput &&
                hasSections &&
                string.IsNullOrWhiteSpace(advancedError) &&
                overrideDependenciesSatisfied &&
                !samePath &&
                outputIsSaveLike;
            EditorPatchButton.IsEnabled = canWrite;

            bool canWriteFocusedGoodie =
                focusedGoodieRequest is not null &&
                string.IsNullOrWhiteSpace(focusedGoodieError) &&
                _editorInputValid &&
                hasInput &&
                hasOutput &&
                !samePath &&
                outputIsSaveLike;
            EditorPatchFocusedGoodieButton.IsEnabled = canWriteFocusedGoodie;
            EditorFocusedGoodieStatusTextBlock.Text = focusedGoodieError ?? (canWriteFocusedGoodie
                ? $"Ready to write only Goodie ID {focusedGoodieRequest!.GoodieId:000} as {MissionScriptGoodieStateSaveCodec.GetStateLabel(focusedGoodieRequest.State)}."
                : "Choose a valid .bes input and a different .bes output to enable this one-field write.");

            Models.SaveEditorCompletionEvaluation completion = SaveEditorJourneyStateMachine.EvaluateCompletion(
                _lastWrittenCompletion,
                request,
                File.Exists(_lastWrittenCompletion?.OutputPath),
                AppConfig.GetPatchedOutputDir());
            if (!completion.IsCurrent && _lastWrittenCompletion is not null)
            {
                ClearLastWrittenSave();
            }

            bool hasCompletedCurrentPlan = completion.IsCurrent;
            bool canRevealWrittenCopy = completion.CanReveal;
            SaveEditorShowWrittenSaveButton.IsEnabled = canRevealWrittenCopy;

            var journeyState = new Models.SaveEditorFirstSaveJourneyState(
                HasValidInput: _editorInputValid,
                HasValidOutput: hasOutput && outputIsSaveLike,
                HasSelectedChanges: hasSections,
                CanWrite: canWrite,
                HasCompletedCurrentPlan: hasCompletedCurrentPlan,
                CanRevealWrittenCopy: canRevealWrittenCopy);
            string journeyStatus = SaveEditorFirstSaveJourneyText.BuildStatus(journeyState);
            if (!string.Equals(SaveEditorFirstSaveStatus.Text, journeyStatus, StringComparison.Ordinal))
            {
                SaveEditorFirstSaveStatus.Text = journeyStatus;
            }

            string advancedStatus = SaveEditorFirstSaveJourneyText.BuildAdvancedOverrideStatus(
                missionOverrideCount,
                categoryKillOverrideCount);
            SaveEditorAdvancedOverridesStatus.Text = advancedStatus;
            AutomationProperties.SetName(
                SaveEditorAdvancedOverridesExpander,
                $"Advanced: per-mission ranks and category kills. {advancedStatus}");
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
