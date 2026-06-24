using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Save Analyzer tab - analyzes BEA save / options files without modification.
    ///
    /// Supports:
    /// - Career saves: *.bes
    /// - Global options: defaultoptions.bea (Steam build)
    /// Provides TreeView summary and detailed text output.
    /// </summary>
    public partial class SaveAnalyzerView : UserControl
    {
        private SaveAnalysis? _currentAnalysis;
        private string? _currentFilePath;
        private List<string> _saveFiles = new();

        public SaveAnalyzerView()
        {
            InitializeComponent();
            LoadSaveFiles();
        }

        private void LoadSaveFiles()
        {
            _saveFiles.Clear();
            SaveFilesComboBox.Items.Clear();

            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();

            if (string.IsNullOrEmpty(gameDir))
            {
                SaveFilesComboBox.Items.Add("(Set game directory in Settings)");
                SaveFilesComboBox.SelectedIndex = 0;
                return;
            }

            var saveInfos = AppConfig.FindSaveFiles(gameDir);

            if (saveInfos.Count == 0)
            {
                SaveFilesComboBox.Items.Add("(No files found)");
            }
            else
            {
                foreach (var save in saveInfos)
                {
                    _saveFiles.Add(save.Path);
                    string validity = save.IsValid ? "" : " [invalid file]";
                    string displayName = $"{Path.GetFileName(save.Path)} ({save.Modified:MMM dd, HH:mm}){validity}";
                    SaveFilesComboBox.Items.Add(displayName);
                }
            }

            SaveFilesComboBox.SelectedIndex = 0;
        }

        private void SaveFilesComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            int index = SaveFilesComboBox.SelectedIndex;
            if (index >= 0 && index < _saveFiles.Count)
            {
                string selectedFile = _saveFiles[index];
                FilePathTextBox.Text = selectedFile;
                _currentFilePath = selectedFile;
                AnalyzeButton.IsEnabled = true;
                RefreshButton.IsEnabled = true;
                UpdateCompareButtonState();
                MainWindow.SetStatus($"Save Analyzer: Selected {Path.GetFileName(selectedFile)}");

                // Auto-analyze on selection
                PerformAnalysis();
            }
        }

        private void RefreshSaveFiles_Click(object sender, RoutedEventArgs e)
        {
            LoadSaveFiles();
            MainWindow.SetStatus($"Save Analyzer: Found {_saveFiles.Count} file(s)");
        }

        private void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Filter = "BEA Save/Options Files (*.bes;*.bea)|*.bes;*.bea|All Files (*.*)|*.*",
                Title = "Select Save/Options File to Analyze"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                _ = TryLoadFile(openFileDialog.FileName, out _);
            }
        }

        private void AnalyzeButton_Click(object sender, RoutedEventArgs e)
        {
            PerformAnalysis();
        }

        private void RefreshButton_Click(object sender, RoutedEventArgs e)
        {
            PerformAnalysis();
        }

        private void ClearButton_Click(object sender, RoutedEventArgs e)
        {
            _currentAnalysis = null;
            OutputTextBlock.Text = string.Empty;
            SummaryTree.Items.Clear();
            TitleBlock.Text = "Save/Options Analyzer";
            SummaryGroupBox.Header = "Analysis Summary";
            ModeTextBlock.Text = "Single-file analysis: choose a .bes or .bea file to inspect.";
            CopyButton.IsEnabled = false;
            MainWindow.SetStatus("Save Analyzer: Cleared output");
        }

        private void PerformAnalysis()
        {
            if (string.IsNullOrEmpty(_currentFilePath))
            {
                MainWindow.SetStatus("Save Analyzer: No file selected");
                return;
            }

            try
            {
                MainWindow.SetStatus("Save Analyzer: Analyzing...");
                _currentAnalysis = BesFilePatcher.AnalyzeSave(_currentFilePath);

                // Update TreeView summary
                BuildTreeViewSummary();

                // Update detailed text output
                bool verbose = VerboseCheckBox.IsChecked == true;
                bool dumpMystery = DumpMysteryCheckBox.IsChecked == true;
                string report = BesFilePatcher.FormatAnalysisReport(_currentAnalysis, verbose, dumpMystery);
                OutputTextBlock.Text = report;

                CopyButton.IsEnabled = true;
                TitleBlock.Text = $"Analysis: {Path.GetFileName(_currentFilePath)}";
                SummaryGroupBox.Header = "Analysis Summary";
                ModeTextBlock.Text = _currentAnalysis.IsOptionsFile
                    ? "Single-file analysis: defaultoptions.bea / .bea global settings view."
                    : "Single-file analysis: .bes career save view.";
                MainWindow.SetStatus(_currentAnalysis.IsValid
                    ? $"Save Analyzer: {_currentAnalysis.CompletedNodes} missions, {_currentAnalysis.CompletedLinks} links"
                    : $"Save Analyzer: Invalid file - {_currentAnalysis.ErrorMessage}");
            }
            catch (Exception ex)
            {
                MainWindow.SetStatus($"Save Analyzer: Error - {ex.Message}");
                OutputTextBlock.Text = $"Error analyzing file: {ex.Message}";
            }
        }

        private void BuildTreeViewSummary()
        {
            SummaryTree.Items.Clear();

            if (_currentAnalysis == null || !_currentAnalysis.IsValid)
            {
                var errorItem = new TreeViewItem
                {
                    Header = _currentAnalysis?.ErrorMessage ?? "No analysis available"
                };
                SummaryTree.Items.Add(errorItem);
                return;
            }

            // File Info
            var fileItem = new TreeViewItem { Header = "File Info" };
            fileItem.Items.Add(new TreeViewItem { Header = $"Size: {_currentAnalysis.FileSize:N0} bytes" });
            fileItem.Items.Add(new TreeViewItem
            {
                Header = $"Version word: 0x{_currentAnalysis.VersionWord:X4} " +
                         (_currentAnalysis.VersionValid ? "(valid)" : "(INVALID)")
            });
            fileItem.Items.Add(new TreeViewItem
            {
                Header = $"Header dword view @0x0000: 0x{_currentAnalysis.VersionStamp:X8}"
            });
            fileItem.Items.Add(new TreeViewItem
            {
                Header = $"NewGoodieCount: {_currentAnalysis.NewGoodieCountRaw} (0x{_currentAnalysis.NewGoodieCountRaw:X8})"
            });
            SummaryTree.Items.Add(fileItem);

            // Options / Settings (Steam build)
            var optionsItem = new TreeViewItem
            {
                Header = _currentAnalysis.IsOptionsFile
                    ? "Boot-Time Global Options (.bea)"
                    : "Stored Options Snapshot (.bes)"
            };
            string fileKind = _currentAnalysis.IsOptionsFile ? "defaultoptions.bea (boot/global)" : ".bes (career save)";
            optionsItem.Items.Add(new TreeViewItem { Header = $"File kind: {fileKind}" });
            optionsItem.Items.Add(new TreeViewItem
            {
                Header = _currentAnalysis.IsOptionsFile
                    ? ".bea is the boot-time source for keybinds and most global settings."
                    : ".bes stores a snapshot; retail load/save flows may sync it into defaultoptions.bea for next boot."
            });
            optionsItem.Items.Add(new TreeViewItem
            {
                Header = $"Volumes: Sound={_currentAnalysis.SoundVolume:0.###} Music={_currentAnalysis.MusicVolume:0.###}"
            });

            string invWalkerP1 = _currentAnalysis.InvertYAxisRaw[0] != 0 ? "ON" : "OFF";
            string invWalkerP2 = _currentAnalysis.InvertYAxisRaw[1] != 0 ? "ON" : "OFF";
            string invFlightP1 = _currentAnalysis.InvertFlightRaw[0] != 0 ? "ON" : "OFF";
            string invFlightP2 = _currentAnalysis.InvertFlightRaw[1] != 0 ? "ON" : "OFF";
            string vibrationP1 = _currentAnalysis.VibrationRaw[0] != 0 ? "ON" : "OFF";
            string vibrationP2 = _currentAnalysis.VibrationRaw[1] != 0 ? "ON" : "OFF";
            optionsItem.Items.Add(new TreeViewItem { Header = $"InvertY Walker: P1={invWalkerP1}, P2={invWalkerP2}" });
            optionsItem.Items.Add(new TreeViewItem { Header = $"InvertY Flight: P1={invFlightP1}, P2={invFlightP2}" });
            optionsItem.Items.Add(new TreeViewItem { Header = $"Vibration: P1={vibrationP1}, P2={vibrationP2}" });

            if (_currentAnalysis.OptionsEntryCount > 0)
            {
                optionsItem.Items.Add(new TreeViewItem { Header = $"Options entries: {_currentAnalysis.OptionsEntryCount} (tail @ 0x{_currentAnalysis.OptionsTailStart:X4})" });
                optionsItem.Items.Add(new TreeViewItem { Header = $"ControlSchemeIndex: {_currentAnalysis.OptionsControlSchemeIndex}" });
                optionsItem.Items.Add(new TreeViewItem { Header = $"MouseSensitivity: {_currentAnalysis.OptionsMouseSensitivity:0.###}" });
                optionsItem.Items.Add(new TreeViewItem { Header = $"ScreenShape: {_currentAnalysis.OptionsScreenShape} (0=4:3,1=16:9,2=1:1)" });
            }
            SummaryTree.Items.Add(optionsItem);

            // Missions
            int usedNodes = _currentAnalysis.CompletedNodes + _currentAnalysis.PartialNodes;
            var missionsItem = new TreeViewItem
            {
                Header = $"Missions ({_currentAnalysis.CompletedNodes}/{usedNodes} completed)"
            };
            if (_currentAnalysis.RankDistribution.Count > 0)
            {
                foreach (var rank in new[] { "S", "A", "B", "C", "D", "E", "NONE" })
                {
                    if (_currentAnalysis.RankDistribution.TryGetValue(rank, out int count))
                    {
                        missionsItem.Items.Add(new TreeViewItem { Header = $"{rank}-rank: {count}" });
                    }
                }
            }
            if (_currentAnalysis.PartialNodes > 0)
            {
                missionsItem.Items.Add(new TreeViewItem { Header = $"Partial: {_currentAnalysis.PartialNodes}" });
            }
            SummaryTree.Items.Add(missionsItem);

            // Links
            var linksItem = new TreeViewItem
            {
                Header = $"Links ({_currentAnalysis.CompletedLinks}/{_currentAnalysis.TotalLinks})"
            };
            SummaryTree.Items.Add(linksItem);

            // Goodies
            int totalUnlocked = _currentAnalysis.GoodiesNew + _currentAnalysis.GoodiesOld;
            int totalDisplayable = _currentAnalysis.GoodiesNew
                                   + _currentAnalysis.GoodiesOld
                                   + _currentAnalysis.GoodiesLocked
                                   + _currentAnalysis.GoodiesInstructions
                                   + _currentAnalysis.GoodiesOther;
            var goodiesItem = new TreeViewItem
            {
                Header = $"Goodies ({totalUnlocked}/{totalDisplayable} unlocked)"
            };
            if (_currentAnalysis.GoodiesNew > 0)
                goodiesItem.Items.Add(new TreeViewItem { Header = $"NEW (gold): {_currentAnalysis.GoodiesNew}" });
            if (_currentAnalysis.GoodiesOld > 0)
                goodiesItem.Items.Add(new TreeViewItem { Header = $"OLD (blue): {_currentAnalysis.GoodiesOld}" });
            if (_currentAnalysis.GoodiesLocked > 0)
                goodiesItem.Items.Add(new TreeViewItem { Header = $"Locked: {_currentAnalysis.GoodiesLocked}" });
            if (_currentAnalysis.GoodiesOther > 0)
                goodiesItem.Items.Add(new TreeViewItem { Header = $"Other: {_currentAnalysis.GoodiesOther}" });
            SummaryTree.Items.Add(goodiesItem);

            // Kill Counts
            string[] categories = { "Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs" };
            int totalKills = _currentAnalysis.KillCounts.Sum();
            var killsItem = new TreeViewItem
            {
                Header = $"Kill Counts ({totalKills:N0} total)"
            };
            for (int i = 0; i < 5; i++)
            {
                string threshold = _currentAnalysis.NextUnlockThresholds[i].HasValue
                    ? $" (next: {_currentAnalysis.NextUnlockThresholds[i]})"
                    : " (max)";
                killsItem.Items.Add(new TreeViewItem
                {
                    Header = $"{categories[i]}: {_currentAnalysis.KillCounts[i]:N0}{threshold}"
                });
            }
            SummaryTree.Items.Add(killsItem);

            // God Mode
            var godModeItem = new TreeViewItem { Header = "God Mode" };
            godModeItem.Items.Add(new TreeViewItem
            {
                Header = $"Enabled (toggle): {(_currentAnalysis.GodModeEnabledOn ? "ON" : "OFF")} (0x{_currentAnalysis.GodModeEnabledRaw:X8})"
            });
            SummaryTree.Items.Add(godModeItem);

            // Tech Slots
            var techItem = new TreeViewItem
            {
                Header = $"Tech Slots ({_currentAnalysis.ActiveTechSlots}/{_currentAnalysis.TotalTechSlots} active)"
            };
            SummaryTree.Items.Add(techItem);

            // Unmapped/Reserved regions
            if (_currentAnalysis.MysteryRegions.Count > 0)
            {
                int totalMysteryBytes = _currentAnalysis.MysteryRegions.Sum(r => r.Size);
                var mysteryItem = new TreeViewItem
                {
                    Header = $"Unmapped/Reserved Regions ({totalMysteryBytes} bytes)"
                };
                foreach (var region in _currentAnalysis.MysteryRegions)
                {
                    string status = region.AllZeros ? "[zeros]" :
                                   region.AllFF ? "[0xFF]" :
                                   $"{region.NonZeroCount} non-zero";
                    mysteryItem.Items.Add(new TreeViewItem
                    {
                        Header = $"{region.Name}: {status}"
                    });
                }
                SummaryTree.Items.Add(mysteryItem);
            }
        }

        private void VerboseCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (_currentAnalysis != null)
            {
                UpdateTextOutput();
            }
        }

        private void DumpMysteryCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (_currentAnalysis != null)
            {
                UpdateTextOutput();
            }
        }

        private void UpdateTextOutput()
        {
            if (_currentAnalysis == null) return;

            bool verbose = VerboseCheckBox.IsChecked == true;
            bool dumpMystery = DumpMysteryCheckBox.IsChecked == true;
            string report = BesFilePatcher.FormatAnalysisReport(_currentAnalysis, verbose, dumpMystery);
            OutputTextBlock.Text = report;
        }

        private void BrowseCompareButton_Click(object sender, RoutedEventArgs e)
        {
            var openFileDialog = new OpenFileDialog
            {
                Filter = "BEA Save/Options Files (*.bes;*.bea)|*.bes;*.bea|All Files (*.*)|*.*",
                Title = "Select File to Compare"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                CompareFileTextBox.Text = openFileDialog.FileName;
                UpdateCompareButtonState();
            }
        }

        private void UpdateCompareButtonState()
        {
            CompareButton.IsEnabled = !string.IsNullOrEmpty(_currentFilePath) &&
                                      !string.IsNullOrEmpty(CompareFileTextBox.Text);
        }

        private void BuildCompareTreeViewSummary(string leftPath, string rightPath, BesFilePatcher.CompareResult result)
        {
            SummaryTree.Items.Clear();
            SummaryGroupBox.Header = "Comparison Summary";

            var compareItem = new TreeViewItem { Header = "Comparison" };
            compareItem.Items.Add(new TreeViewItem { Header = $"Left file: {Path.GetFileName(leftPath)}" });
            compareItem.Items.Add(new TreeViewItem { Header = $"Right file: {Path.GetFileName(rightPath)}" });
            compareItem.Items.Add(new TreeViewItem
            {
                Header = $"Size match: {(result.SameSize ? "Yes" : "No")} ({result.File1Size:N0} vs {result.File2Size:N0} bytes)"
            });
            compareItem.Items.Add(new TreeViewItem { Header = $"Differing bytes: {result.DifferingBytes:N0}" });
            compareItem.Items.Add(new TreeViewItem { Header = $"Difference ranges: {result.DiffRanges.Count}" });
            compareItem.Items.Add(new TreeViewItem
            {
                Header = $".bea / options involved: {(leftPath.EndsWith(".bea", StringComparison.OrdinalIgnoreCase) || rightPath.EndsWith(".bea", StringComparison.OrdinalIgnoreCase) ? "Yes" : "No")}"
            });

            if (result.RegionCounts.Count > 0)
            {
                var regions = new TreeViewItem { Header = "Regions with differences" };
                foreach (var row in result.RegionCounts.OrderByDescending(x => x.Value))
                {
                    regions.Items.Add(new TreeViewItem { Header = $"{row.Key}: {row.Value:N0}" });
                }
                compareItem.Items.Add(regions);
            }

            SummaryTree.Items.Add(compareItem);
            compareItem.IsExpanded = true;
        }

        private void CompareButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrEmpty(_currentFilePath) || string.IsNullOrEmpty(CompareFileTextBox.Text))
            {
                MainWindow.SetStatus("Save Analyzer: Please select both files to compare");
                return;
            }

            PerformCompare(_currentFilePath, CompareFileTextBox.Text);
        }

        private void PerformCompare(string leftPath, string rightPath)
        {
            try
            {
                MainWindow.SetStatus("Save Analyzer: Comparing files...");
                var result = BesFilePatcher.CompareFiles(leftPath, rightPath);
                string report = BesFilePatcher.FormatCompareReport(result, leftPath, rightPath);
                BuildCompareTreeViewSummary(leftPath, rightPath, result);
                OutputTextBlock.Text = report;

                TitleBlock.Text = "File Comparison";
                ModeTextBlock.Text = "Comparison mode: summary counts and differing regions for the selected pair.";
                CopyButton.IsEnabled = true;
                MainWindow.SetStatus(result.DifferingBytes == 0
                    ? "Save Analyzer: Files are identical"
                    : $"Save Analyzer: Found {result.DifferingBytes} differing bytes in {result.DiffRanges.Count} regions");
            }
            catch (Exception ex)
            {
                MainWindow.SetStatus($"Save Analyzer: Error - {ex.Message}");
                OutputTextBlock.Text = $"Error comparing files: {ex.Message}";
            }
        }

        public bool TryLoadFile(string filePath, out string error)
        {
            error = string.Empty;
            if (string.IsNullOrWhiteSpace(filePath))
            {
                error = "No file path provided.";
                return false;
            }

            if (!File.Exists(filePath))
            {
                error = $"File not found: {filePath}";
                MainWindow.SetStatus($"Save Analyzer: {error}");
                return false;
            }

            FilePathTextBox.Text = filePath;
            _currentFilePath = filePath;
            AnalyzeButton.IsEnabled = true;
            RefreshButton.IsEnabled = true;
            UpdateCompareButtonState();
            MainWindow.SetStatus($"Save Analyzer: Selected {Path.GetFileName(filePath)}");
            PerformAnalysis();
            return true;
        }

        public bool TryCompareFiles(string leftPath, string rightPath, out string error)
        {
            error = string.Empty;
            if (!TryLoadFile(leftPath, out error))
                return false;

            if (string.IsNullOrWhiteSpace(rightPath) || !File.Exists(rightPath))
            {
                error = $"Compare file not found: {rightPath}";
                MainWindow.SetStatus($"Save Analyzer: {error}");
                return false;
            }

            CompareFileTextBox.Text = rightPath;
            UpdateCompareButtonState();
            PerformCompare(leftPath, rightPath);
            return true;
        }

        private void CopyButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                Clipboard.SetText(OutputTextBlock.Text);
                MainWindow.SetStatus("Save Analyzer: Copied to clipboard");
            }
            catch (Exception ex)
            {
                MainWindow.SetStatus($"Save Analyzer: Copy failed - {ex.Message}");
            }
        }
    }
}
