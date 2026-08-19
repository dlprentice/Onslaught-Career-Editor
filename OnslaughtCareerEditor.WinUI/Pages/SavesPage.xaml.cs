using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.AppCore;
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

        // Which write action last produced a file, and where. Used to warn that the other write action
        // would replace that file rather than compose with it.
        private SaveEditorService.SaveEditorWriteKind? _lastEditorWriteKind;
        private string? _lastEditorWriteOutputPath;
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
            RefreshSaveRescueCopies();
            AppConfigChangedService.ConfigChanged += HandleConfigChanged;
        }

        /// <summary>
        /// Pages are cached, so a Save Lab built before the game folder changed
        /// kept listing files discovered under the old one until the user
        /// happened to press Refresh. The detected lists are read-only
        /// discovery, so re-running them is safe; nothing the user has typed or
        /// selected is touched.
        /// </summary>
        private void HandleConfigChanged(AppConfig config)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                LoadDetectedFiles();
                LoadEditorDetectedFiles();
                LoadConfigurationDetectedFiles();
            });
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
                ? SaveAnalyzerService.NoDetectedFilesNextStep
                : "Choose a detected file";
            RestoreAnalyzerDetectedFileSelection(selectedPath);
            DetectedFilesStatusTextBlock.Text = _detectedFiles.Count == 0
                ? "No save or options files were detected. Set the game folder in Settings or browse manually."
                : $"{_detectedFiles.Count} detected file(s) available.";
        }

        private void InitializeEditorSurface()
        {
            EditorRankComboBox.SelectedIndex = 0;
            EditorPatchPresetComboBox.SelectedIndex = 0;
            EditorFocusedGoodieIdNumberBox.Value = 2;
            EditorFocusedGoodieStateComboBox.SelectedIndex = 2;
            _suppressEditorGlobalKillProvenance = true;
            try
            {
                EditorGlobalKillNumberBox.Value = 100;
            }
            finally
            {
                _suppressEditorGlobalKillProvenance = false;
            }

            _editorGlobalKillWasAutoSeeded = true;

            // Starts cleared with no save loaded; LoadEditorAdvancedSnapshot turns it on for a save with
            // mixed per-category counts, and stops deciding as soon as the user touches it.
            _suppressEditorKeepKillsProvenance = true;
            try
            {
                EditorKeepUnoverriddenKillsCheckBox.IsChecked = false;
            }
            finally
            {
                _suppressEditorKeepKillsProvenance = false;
            }

            _editorKeepKillsWasAutoSet = true;
            EditorGlobalKillNumberBox.IsEnabled = true;
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
                ? SaveAnalyzerService.NoDetectedFilesNextStep
                : "Choose a career save";
            RestoreEditorDetectedFileSelection(selectedPath);
            EditorDetectedFilesStatusTextBlock.Text = _editorDetectedFiles.Count == 0
                ? "No .bes career saves were detected. Set the game folder in Settings or browse manually."
                : $"{_editorDetectedFiles.Count} detected career save(s) available.";
        }

        private void RestoreAnalyzerDetectedFileSelection(string? selectedPath)
        {
            SaveAnalyzerFileItem? match = string.IsNullOrWhiteSpace(selectedPath)
                ? null
                : _detectedFiles.FirstOrDefault(item =>
                    string.Equals(item.Path, selectedPath, StringComparison.OrdinalIgnoreCase));

            // Nothing chosen yet: pick the save the player touched last. The page
            // used to report "9 detected career save(s) available" beside an
            // empty picker, which is a list of work rather than a starting point.
            match ??= MostRecentlyWritten(_detectedFiles);

            if (match is not null)
            {
                DetectedFilesComboBox.SelectedItem = match;
            }
        }

        /// <summary>
        /// The most recently written file, which is almost always the one the
        /// player means. Unreadable timestamps sort last rather than throwing.
        /// </summary>
        private static SaveAnalyzerFileItem? MostRecentlyWritten(IReadOnlyList<SaveAnalyzerFileItem> items)
        {
            SaveAnalyzerFileItem? best = null;
            DateTime bestWritten = DateTime.MinValue;

            foreach (SaveAnalyzerFileItem item in items)
            {
                DateTime written;
                try
                {
                    written = File.GetLastWriteTimeUtc(item.Path);
                }
                catch (Exception)
                {
                    continue;
                }

                if (best is null || written > bestWritten)
                {
                    best = item;
                    bestWritten = written;
                }
            }

            return best;
        }

        private void RestoreEditorDetectedFileSelection(string? selectedPath)
        {
            SaveAnalyzerFileItem? match = string.IsNullOrWhiteSpace(selectedPath)
                ? null
                : _editorDetectedFiles.FirstOrDefault(item =>
                    string.Equals(item.Path, selectedPath, StringComparison.OrdinalIgnoreCase));

            match ??= MostRecentlyWritten(_editorDetectedFiles);

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
            catch (Exception)
            {
                RenderError("Comparison failed", SaveLabPageText.ComparisonFailed);
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
                    SaveLabPageText.AnalysisNeedsAFile,
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
            catch (Exception)
            {
                RenderError("Analysis failed", SaveLabPageText.AnalysisFailed);
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
                SaveAnalyzerService.BuildInfoTitle(document),
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
                "Choose a detected file or browse for a .bes or .bea file to inspect save structure, options, and comparison data.",
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
            // Once the user has typed their own write value, reloading the input save must not silently
            // replace it with a value re-seeded from the file.
            if (!_suppressEditorGlobalKillProvenance)
            {
                _editorGlobalKillWasAutoSeeded = false;
            }

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

            // The two write buttons share one output path and both re-read the input save, so they
            // replace each other rather than composing. Say so before the earlier edit disappears.
            string? focusedCompositionLoss = SaveEditorService.DescribeWriteCompositionLoss(
                _lastEditorWriteKind,
                _lastEditorWriteOutputPath,
                SaveEditorService.SaveEditorWriteKind.FocusedGoodieState,
                outputPath);
            if (focusedCompositionLoss is not null &&
                !await ConfirmAsync("This will discard your previous edit", focusedCompositionLoss))
            {
                AppStatusService.SetStatus("Save Editor: focused Goodie write canceled");
                return;
            }

            if (File.Exists(outputPath) &&
                !await ConfirmAsync(
                    "Overwrite output file?",
                    SaveLabPageText.BuildOverwriteQuestion(outputPath)))
            {
                EditorOutputTextBox.Text = SaveLabPageText.OverwriteCanceled;
                EditorCopyOutputButton.IsEnabled = true;
                AppStatusService.SetStatus("Save Editor: focused Goodie overwrite canceled");
                return;
            }

            EditorPatchFocusedGoodieButton.IsEnabled = false;
            EditorOutputTextBox.Text = "Writing one focused Goodie state...";
            AppStatusService.SetStatus("Save Editor: writing focused Goodie state...");

            PatchResult result = SaveEditorService.PatchFocusedGoodieState(request);
            ClearLastWrittenSave();
            if (result.Success)
            {
                _lastEditorWriteKind = SaveEditorService.SaveEditorWriteKind.FocusedGoodieState;
                _lastEditorWriteOutputPath = outputPath;
            }
            string stateLabel = MissionScriptGoodieStateSaveCodec.GetStateLabel(request.State);
            string displayMessage = result.Success
                ? $"Goodie ID {request.GoodieId:000} was written as {stateLabel} to {BuildFileNameSummary(request.OutputPath, "the selected output file")}.\nThe source save was not modified. If this destination is a Safe Game Copy, the output is staged only in that verified copy's savegames folder."
                : SaveLabPageText.DescribeEditorPatchFailure(
                    ReplacePathWithLabel(
                        ReplacePathWithLabel(result.Message, request.InputPath, "selected input save"),
                        request.OutputPath,
                        "selected output file"));

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

            string? patchCompositionLoss = SaveEditorService.DescribeWriteCompositionLoss(
                _lastEditorWriteKind,
                _lastEditorWriteOutputPath,
                SaveEditorService.SaveEditorWriteKind.FullPatch,
                outputPath);
            if (patchCompositionLoss is not null &&
                !await ConfirmAsync("This will discard your previous edit", patchCompositionLoss))
            {
                AppStatusService.SetStatus("Save Editor: patch canceled");
                return;
            }

            if (File.Exists(outputPath) &&
                !await ConfirmAsync(
                    "Overwrite output file?",
                    SaveLabPageText.BuildOverwriteQuestion(outputPath)))
            {
                EditorOutputTextBox.Text = SaveLabPageText.OverwriteCanceled;
                EditorCopyOutputButton.IsEnabled = true;
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
                _lastEditorWriteKind = SaveEditorService.SaveEditorWriteKind.FullPatch;
                _lastEditorWriteOutputPath = outputPath;
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

        /// <summary>
        /// Closes the journey. The editor writes a separate file and then used
        /// to tell the player to copy it into a safe copy's savegames folder by
        /// hand - the app knew where that folder was the whole time.
        ///
        /// Reuses the cheat page's writer, which is the same guarded
        /// transaction: it stages, verifies length and hash on both sides,
        /// refuses in-place writes, symlinks and hardlinked aliases, and refuses
        /// any destination inside an installed game.
        /// </summary>
        private async void SaveEditorInstallToSafeCopyButton_Click(object sender, RoutedEventArgs e)
        {
            string? writtenPath = _lastWrittenCompletion?.OutputPath;
            if (string.IsNullOrWhiteSpace(writtenPath) || !File.Exists(writtenPath))
            {
                ShowInstallNote("Write the copy first, then this can put it in place.");
                return;
            }

            IReadOnlyList<CheatSaveTarget> targets = CheatSaveWriterService.FindSafeCopyTargets();
            if (targets.Count == 0)
            {
                ShowInstallNote("There is no safe copy yet. Make one in Windowed & Mods, then come back.");
                return;
            }

            CheatSaveTarget target = targets[0];
            string name = Path.GetFileNameWithoutExtension(writtenPath);

            CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
            {
                InputPath = writtenPath,
                OutputDirectory = target.SavegamesDirectory,
                Name = name,
            });

            if (outcome.NeedsOverwriteConfirmation)
            {
                var dialog = new ContentDialog
                {
                    XamlRoot = XamlRoot,
                    Title = "Replace the save that is already there?",
                    Content = SaveLabPageText.BuildOverwriteQuestion($"{name}.bes")
                        + $" It is in {target.DisplayName}.",
                    PrimaryButtonText = "Replace it",
                    CloseButtonText = "Keep it",
                    DefaultButton = ContentDialogButton.Close,
                };

                if (await dialog.ShowAsync() != ContentDialogResult.Primary)
                {
                    ShowInstallNote("Left the existing save alone.");
                    return;
                }

                outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
                {
                    InputPath = writtenPath,
                    OutputDirectory = target.SavegamesDirectory,
                    Name = name,
                    AllowOverwrite = true,
                });
            }

            ShowInstallNote(outcome.Success
                ? $"Done. {name}.bes is in {target.DisplayName} - close the copied game before loading it."
                : SaveLabPageText.SafeCopyInstallFailed);
            AppStatusService.SetStatus(outcome.Success
                ? "Save Lab: put the save into your safe copy"
                : "Save Lab: could not install the save");
        }

        private void ShowInstallNote(string note)
        {
            SaveEditorInstallNoteTextBlock.Text = note;
            SaveEditorInstallNoteTextBlock.Visibility = Visibility.Visible;
        }

        // ------------------------------------------------ bring a career back out

        private IReadOnlyList<SafeCopySaveInventory> _saveRescueCopies = Array.Empty<SafeCopySaveInventory>();
        private bool _refreshingSaveRescue;

        /// <summary>
        /// The other half of "Put it in my safe copy". A career played inside a copy lives only in
        /// that copy, and deleting the copy takes it - so there has to be a way out that does not
        /// involve knowing where Roaming AppData is.
        /// </summary>
        private void RefreshSaveRescueCopies()
        {
            _refreshingSaveRescue = true;
            try
            {
                string? previous = (SaveRescueCopyComboBox.SelectedItem as ComboBoxItem)?.Tag as string;
                _saveRescueCopies = SafeCopySaveRescueService.InventoryAll();
                SaveRescueCopyComboBox.Items.Clear();

                foreach (SafeCopySaveInventory copy in _saveRescueCopies)
                {
                    SaveRescueCopyComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = copy.DisplayName,
                        Tag = copy.ProfileRoot,
                    });
                }

                SaveRescueCopyComboBox.IsEnabled = SaveRescueCopyComboBox.Items.Count > 0;
                if (SaveRescueCopyComboBox.Items.Count > 0)
                {
                    int restored = -1;
                    for (int index = 0; index < SaveRescueCopyComboBox.Items.Count && previous is not null; index++)
                    {
                        if (SaveRescueCopyComboBox.Items[index] is ComboBoxItem { Tag: string tag } &&
                            string.Equals(tag, previous, StringComparison.OrdinalIgnoreCase))
                        {
                            restored = index;
                            break;
                        }
                    }

                    SaveRescueCopyComboBox.SelectedIndex = restored >= 0 ? restored : 0;
                }
            }
            finally
            {
                _refreshingSaveRescue = false;
            }

            RefreshSaveRescueSaves();
        }

        private void RefreshSaveRescueSaves()
        {
            SafeCopySaveInventory? copy = GetSelectedSaveRescueCopy();

            _refreshingSaveRescue = true;
            try
            {
                SaveRescueSaveComboBox.Items.Clear();
                foreach (SafeCopySaveFile save in copy?.Saves ?? Array.Empty<SafeCopySaveFile>())
                {
                    SaveRescueSaveComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = SaveRescuePageText.DescribeSave(save),
                        Tag = save.FileName,
                    });
                }

                SaveRescueSaveComboBox.IsEnabled = SaveRescueSaveComboBox.Items.Count > 0;
                if (SaveRescueSaveComboBox.Items.Count > 0)
                    SaveRescueSaveComboBox.SelectedIndex = 0;
            }
            finally
            {
                _refreshingSaveRescue = false;
            }

            UpdateSaveRescueState();
        }

        private void UpdateSaveRescueState()
        {
            SafeCopySaveInventory? copy = GetSelectedSaveRescueCopy();
            SafeCopySaveFile? save = GetSelectedSaveRescueSave();
            SaveRescueSelectionTextBlock.Text = SaveRescuePageText.BuildSelectionSummary(copy, save);
            SaveRescueButton.IsEnabled = copy is not null && save is not null;
        }

        private SafeCopySaveInventory? GetSelectedSaveRescueCopy()
        {
            if ((SaveRescueCopyComboBox.SelectedItem as ComboBoxItem)?.Tag is not string root)
                return null;

            return _saveRescueCopies.FirstOrDefault(copy =>
                string.Equals(copy.ProfileRoot, root, StringComparison.OrdinalIgnoreCase));
        }

        private SafeCopySaveFile? GetSelectedSaveRescueSave()
        {
            if ((SaveRescueSaveComboBox.SelectedItem as ComboBoxItem)?.Tag is not string fileName)
                return null;

            return GetSelectedSaveRescueCopy()?.Saves.FirstOrDefault(save =>
                string.Equals(save.FileName, fileName, StringComparison.OrdinalIgnoreCase));
        }

        private void SaveRescueCopyComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_refreshingSaveRescue)
                return;

            RefreshSaveRescueSaves();
        }

        private void SaveRescueSaveComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_refreshingSaveRescue)
                return;

            UpdateSaveRescueState();
        }

        private void SaveRescueRefreshButton_Click(object sender, RoutedEventArgs e)
        {
            RefreshSaveRescueCopies();
            ShowSaveRescueNote(_saveRescueCopies.Count == 0
                ? SaveRescuePageText.NoCopiesNote
                : SaveRescuePageText.BuildSelectionSummary(GetSelectedSaveRescueCopy(), GetSelectedSaveRescueSave()));
        }

        private async void SaveRescueButton_Click(object sender, RoutedEventArgs e)
        {
            SafeCopySaveInventory? copy = GetSelectedSaveRescueCopy();
            SafeCopySaveFile? save = GetSelectedSaveRescueSave();
            if (copy is null || save is null || App.MainWindowInstance is null)
                return;

            string? folder = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
            if (string.IsNullOrWhiteSpace(folder))
                return;

            string? refused = SaveRescuePageText.DescribeDestinationRefusal(folder);
            if (refused is not null)
            {
                ShowSaveRescueNote(refused);
                AppStatusService.SetStatus("Save Lab: could not bring that career out");
                return;
            }

            SafeCopySaveRescueResult result = RunSaveRescue(copy, save, folder!, allowOverwrite: false);

            if (result.NeedsOverwriteConfirmation)
            {
                var dialog = new ContentDialog
                {
                    XamlRoot = XamlRoot,
                    Title = "Replace the career that is already there?",
                    Content = SaveLabPageText.BuildOverwriteQuestion(save.FileName),
                    PrimaryButtonText = "Replace it",
                    CloseButtonText = "Keep it",
                    DefaultButton = ContentDialogButton.Close,
                };

                if (await dialog.ShowAsync() != ContentDialogResult.Primary)
                {
                    ShowSaveRescueNote("Left the file that was already there alone.");
                    return;
                }

                result = RunSaveRescue(copy, save, folder!, allowOverwrite: true);
            }

            ShowSaveRescueNote(SaveRescuePageText.BuildOutcomeNote(result));
            AppStatusService.SetStatus(result.Success
                ? "Save Lab: brought a career out of a safe copy"
                : "Save Lab: could not bring that career out");
        }

        private static SafeCopySaveRescueResult RunSaveRescue(
            SafeCopySaveInventory copy,
            SafeCopySaveFile save,
            string destination,
            bool allowOverwrite)
        {
            return SafeCopySaveRescueService.Rescue(new SafeCopySaveRescueRequest
            {
                ProfileRoot = copy.ProfileRoot,
                DestinationDirectory = destination,
                FileNames = new[] { save.FileName },
                AllowOverwrite = allowOverwrite,
            });
        }

        private void ShowSaveRescueNote(string note)
        {
            SaveRescueNoteTextBlock.Text = note;
            SaveRescueNoteTextBlock.Visibility = Visibility.Visible;
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
                return $"Done - your changes are in a new save.\nFile: {outputName}\nThe save you started from was not touched. Close the copied game, then choose Put it in my safe copy to play it.";
            }

            return SaveLabPageText.DescribeEditorPatchFailure(
                RedactEditorPatchPaths(result.Message, request));
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
                ClearEditorInputLocation();
                UpdateEditorActionState();
                return;
            }

            _editorInputValid = File.Exists(inputPath)
                && !SaveEditorService.IsOptionsLikeFilePath(inputPath)
                && BesFilePatcher.IsValidBesFile(inputPath);
            RenderEditorInputLocation(inputPath);
            UpdateEditorActionState();
        }

        private void RenderEditorInputLocation(string inputPath)
        {
            CareerSaveLocationKind kind = CareerSaveLocation.Classify(inputPath);
            string line = CareerSaveLocationText.Describe(kind, inputPath);
            EditorInputLocationTextBlock.Text = line;
            EditorInputLocationTextBlock.Visibility = string.IsNullOrWhiteSpace(line)
                ? Visibility.Collapsed
                : Visibility.Visible;
        }

        private void ClearEditorInputLocation()
        {
            EditorInputLocationTextBlock.Text = string.Empty;
            EditorInputLocationTextBlock.Visibility = Visibility.Collapsed;
        }

        private SavePatchRequest BuildEditorRequest(out string? advancedError)
        {
            TryBuildEditorAdvancedOverrides(out Dictionary<int, string>? levelRanks, out Dictionary<int, int>? perCategoryKills, out advancedError);
            bool patchNodes = EditorPatchNodesCheckBox.IsChecked == true;
            bool patchGoodies = EditorPatchGoodiesCheckBox.IsChecked == true;
            bool patchKills = EditorPatchKillsCheckBox.IsChecked == true;
            return new SavePatchRequest
            {
                InputPath = (EditorInputFileTextBox.Text ?? string.Empty).Trim(),
                OutputPath = (EditorOutputFileTextBox.Text ?? string.Empty).Trim(),
                // A payload is supplied only when the section that consumes it is enabled. Sending a
                // value for a disabled section is exactly what SavePatchIntentContract now refuses,
                // and it would be the UI, not the user, that had configured it.
                Rank = patchNodes ? GetEditorRankBaseline() : null,
                UseNewGoodiesInstead = patchGoodies ? EditorGoodiesAsNewToggle.IsOn : null,
                GlobalKillCount = patchKills && EditorKeepUnoverriddenKillsCheckBox.IsChecked != true
                    ? ClampNumberBoxToInt(EditorGlobalKillNumberBox, fallback: 100)
                    : null,
                PatchNodes = patchNodes,
                PatchLinks = EditorPatchLinksCheckBox.IsChecked == true,
                PatchGoodies = patchGoodies,
                PatchKills = patchKills,
                LevelRanks = levelRanks,
                PerCategoryKills = perCategoryKills
            };
        }

        /// <summary>
        /// The mission rank baseline, or null when the user chose "Keep every grade this save already
        /// has". Null is not a grade: it means the node pass writes only the missions carrying an
        /// explicit per-mission override, leaving every other mission's 64 bytes alone.
        /// </summary>
        private string? GetEditorRankBaseline()
        {
            string? tag = (EditorRankComboBox.SelectedItem as ComboBoxItem)?.Tag as string;
            if (string.Equals(tag, EditorKeepRankBaselineTag, StringComparison.OrdinalIgnoreCase))
            {
                return null;
            }

            return tag ?? "S";
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
            bool overrideDependenciesSatisfied = SaveEditorJourneyStateMachine.AreOverrideDependenciesSatisfied(
                request,
                missionOverrideCount,
                categoryKillOverrideCount);

            EditorPendingChangesTextBlock.Text = SaveEditorService.BuildPendingChangesSummary(request);

            if (!_editorInputValid && hasInput)
            {
                // Say which check failed, not just that one did.
                EditorSafetyHintTextBlock.Text = SaveEditorService.DescribeCareerSaveInputRejection(request.InputPath)
                    ?? "Input must be a valid .bes career save before patching is enabled.";
            }
            else if (!string.IsNullOrWhiteSpace(advancedError))
            {
                EditorSafetyHintTextBlock.Text = advancedError;
            }
            else if (!hasSections)
            {
                EditorSafetyHintTextBlock.Text = "Choose at least one save section to patch.";
            }
            else if (SavePatchIntentContract.DescribeEmptySectionPass(request.ToIntentSnapshot()) is { } emptyPass)
            {
                // Say this before the user clicks, not after. It is reachable from the honest defaults:
                // a mixed-count save switches "Keep the kill counts this save already has" on, so
                // checking Patch kill counts without checking a category leaves nothing to write.
                EditorSafetyHintTextBlock.Text = emptyPass;
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
            else if (SaveLabPageText.DescribeOutputRefusal(request.OutputPath) is { } refusedOutput)
            {
                EditorSafetyHintTextBlock.Text = refusedOutput;
            }
            else if (!outputIsSaveLike)
            {
                // This used to read "...stay outside every game folder", which claimed more than
                // FileMutationSafety.RejectOutputInGameTree delivers: that guard rejects a destination
                // only when an ancestor directory holds BOTH BEA.exe and data/, so it matches the
                // installed game tree and nothing else. Neither Documents\Battle Engine Aquila nor
                // %LocalAppData%\Battle Engine Aquila matches, and the app itself offers files from
                // both. Whether those roots should be protected is an open owner decision; until it is
                // taken, the sentence must not imply they already are.
                EditorSafetyHintTextBlock.Text =
                    "The output file must end in .bes and must not land inside the installed game folder " +
                    "(the one holding BEA.exe and data). That is the only location blocked: your " +
                    "Documents and AppData save folders are not, so an output file there can replace a " +
                    "real career and no backup is taken.";
            }
            else
            {
                EditorSafetyHintTextBlock.Text = "Save patching is ready. Mission rank and category-kill overrides are supported here; startup settings and keybind overrides still belong in Game Options.";
            }

            bool outputRefused = SaveLabPageText.DescribeOutputRefusal(request.OutputPath) is not null;
            bool canWrite =
                _editorInputValid &&
                hasInput &&
                hasOutput &&
                hasSections &&
                string.IsNullOrWhiteSpace(advancedError) &&
                overrideDependenciesSatisfied &&
                !samePath &&
                outputIsSaveLike &&
                !outputRefused;
            EditorPatchButton.IsEnabled = canWrite;

            bool canWriteFocusedGoodie =
                focusedGoodieRequest is not null &&
                string.IsNullOrWhiteSpace(focusedGoodieError) &&
                _editorInputValid &&
                hasInput &&
                hasOutput &&
                !samePath &&
                outputIsSaveLike &&
                !outputRefused;
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
            SaveEditorInstallToSafeCopyButton.IsEnabled = canRevealWrittenCopy;

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
