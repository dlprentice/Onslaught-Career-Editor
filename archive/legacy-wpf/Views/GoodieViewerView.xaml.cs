using Microsoft.Win32;
using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Goodie Viewer tab - inspect per-slot goodie state for .bes/.bea files.
    /// </summary>
    public partial class GoodieViewerView : UserControl
    {
        private const int ExpectedFileSize = BesFilePatcher.EXPECTED_FILE_SIZE;
        private const int GoodieBaseOffset = 0x1F46;
        private const int GoodieCount = 300;
        private const int GoodieDisplayableCount = 233;

        private const uint GoodieUnknown = 0;
        private const uint GoodieInstructions = 1;
        private const uint GoodieNew = 2;
        private const uint GoodieOld = 3;

        private readonly List<string> _saveFiles = new();
        private readonly List<GoodieSlotRow> _allRows = new();
        private string? _currentFilePath;

        private sealed class GoodieSlotRow
        {
            public int Index { get; init; }
            public string FileOffset { get; init; } = "";
            public string State { get; init; } = "";
            public string RawValue { get; init; } = "";
            public string Scope { get; init; } = "";
            public string Notes { get; init; } = "";
        }

        public GoodieViewerView()
        {
            InitializeComponent();
            StateFilterComboBox.SelectedIndex = 0;
            LoadSaveFiles();
        }

        private void LoadSaveFiles()
        {
            _saveFiles.Clear();
            SaveFilesComboBox.Items.Clear();

            var saveInfos = AppConfig.FindSaveFiles();
            if (saveInfos.Count == 0)
            {
                SaveFilesComboBox.Items.Add("(No .bes/.bea files found)");
                SaveFilesComboBox.SelectedIndex = 0;
                return;
            }

            foreach (var save in saveInfos)
            {
                _saveFiles.Add(save.Path);
                string validity = save.IsValid ? "" : " [invalid size]";
                string displayName = $"{Path.GetFileName(save.Path)} ({save.Modified:MMM dd, HH:mm}){validity}";
                SaveFilesComboBox.Items.Add(displayName);
            }

            SaveFilesComboBox.SelectedIndex = 0;
        }

        private void SaveFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            int index = SaveFilesComboBox.SelectedIndex;
            if (index >= 0 && index < _saveFiles.Count)
            {
                _currentFilePath = _saveFiles[index];
                FilePathTextBox.Text = _currentFilePath;
                LoadGoodiesFromFile(_currentFilePath);
            }
        }

        private void RefreshSaveFiles_Click(object sender, RoutedEventArgs e)
        {
            LoadSaveFiles();
            MainWindow.SetStatus($"Goodie Viewer: Found {_saveFiles.Count} file(s)");
        }

        private void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Filter = "BEA Save/Options Files (*.bes;*.bea)|*.bes;*.bea|All Files (*.*)|*.*",
                Title = "Select Save/Options File"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                _currentFilePath = openFileDialog.FileName;
                FilePathTextBox.Text = _currentFilePath;
                LoadGoodiesFromFile(_currentFilePath);
            }
        }

        private void ReloadButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_currentFilePath))
            {
                MessageBox.Show("Select a source .bes/.bea file first.", "Goodie Viewer", MessageBoxButton.OK, MessageBoxImage.Information);
                return;
            }

            LoadGoodiesFromFile(_currentFilePath);
        }

        private void StateFilterComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            ApplyFilters();
        }

        private void ShowReservedCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            ApplyFilters();
        }

        private void LoadGoodiesFromFile(string filePath)
        {
            try
            {
                var fileInfo = new FileInfo(filePath);
                if (!fileInfo.Exists)
                {
                    throw new FileNotFoundException("File not found.", filePath);
                }

                if (fileInfo.Length != ExpectedFileSize)
                {
                    throw new InvalidDataException(
                        $"Invalid file size: {fileInfo.Length:N0} bytes (expected {ExpectedFileSize:N0}).");
                }

                byte[] buf = File.ReadAllBytes(filePath);
                _allRows.Clear();

                for (int i = 0; i < GoodieCount; i++)
                {
                    int offset = GoodieBaseOffset + (i * 4);
                    uint raw = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(offset, 4));
                    string state = ClassifyState(i, raw);
                    string scope = i < GoodieDisplayableCount ? "Displayable" : "Reserved";

                    string notes = state switch
                    {
                        "NEW" => "Gold badge unlock",
                        "OLD" => "Blue badge unlock",
                        "LOCKED" => "Not unlocked",
                        "INSTRUCTIONS" => "Instructions shown state",
                        "RESERVED" when raw == 0 => "Reserved slot (zero)",
                        "RESERVED" => "Reserved slot (non-zero)",
                        _ => "Unexpected raw value",
                    };

                    _allRows.Add(new GoodieSlotRow
                    {
                        Index = i,
                        FileOffset = $"0x{offset:X4}",
                        State = state,
                        RawValue = $"0x{raw:X8}",
                        Scope = scope,
                        Notes = notes,
                    });
                }

                ApplyFilters();
                UpdateSummary(Path.GetFileName(filePath));
                MainWindow.SetStatus($"Goodie Viewer: Loaded {Path.GetFileName(filePath)}");
            }
            catch (Exception ex)
            {
                _allRows.Clear();
                GoodiesDataGrid.ItemsSource = null;
                SummaryTextBlock.Text = $"Failed to load goodies: {ex.Message}";
                MainWindow.SetStatus($"Goodie Viewer: Error - {ex.Message}");
            }
        }

        private static string ClassifyState(int index, uint raw)
        {
            if (index >= GoodieDisplayableCount)
                return "RESERVED";

            if (raw == GoodieNew)
                return "NEW";
            if (raw == GoodieOld)
                return "OLD";
            if (raw == GoodieUnknown)
                return "LOCKED";
            if (raw == GoodieInstructions)
                return "INSTRUCTIONS";
            return "OTHER";
        }

        private void ApplyFilters()
        {
            if (_allRows.Count == 0)
            {
                GoodiesDataGrid.ItemsSource = null;
                return;
            }

            string stateFilter = (StateFilterComboBox.SelectedItem as ComboBoxItem)?.Content?.ToString() ?? "All";
            bool showReserved = ShowReservedCheckBox.IsChecked == true;

            var filtered = _allRows.Where(row =>
                    (showReserved || row.Scope != "Reserved") &&
                    (string.Equals(stateFilter, "All", StringComparison.OrdinalIgnoreCase) ||
                     string.Equals(row.State, stateFilter, StringComparison.OrdinalIgnoreCase)))
                .ToList();

            GoodiesDataGrid.ItemsSource = filtered;
        }

        private void UpdateSummary(string fileName)
        {
            var displayable = _allRows.Where(r => r.Scope == "Displayable").ToList();
            int newCount = displayable.Count(r => r.State == "NEW");
            int oldCount = displayable.Count(r => r.State == "OLD");
            int lockedCount = displayable.Count(r => r.State == "LOCKED");
            int instructionsCount = displayable.Count(r => r.State == "INSTRUCTIONS");
            int otherCount = displayable.Count(r => r.State == "OTHER");
            int unlocked = newCount + oldCount;

            SummaryTextBlock.Text =
                $"Loaded {fileName}. " +
                $"Unlocked: {unlocked}/{GoodieDisplayableCount} (NEW {newCount}, OLD {oldCount}); " +
                $"Locked: {lockedCount}; Instructions: {instructionsCount}; Other: {otherCount}; " +
                $"Reserved slots: {GoodieCount - GoodieDisplayableCount}.";
        }
    }
}
