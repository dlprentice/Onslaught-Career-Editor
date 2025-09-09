using Microsoft.Win32;
using System;
using System.IO;
using System.Windows;
using System.Windows.Controls;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        private readonly BesFilePatcher _patcher;
        
        public MainWindow()
        {
            InitializeComponent();
            _patcher = new BesFilePatcher();
            StatusTextBlock.Text = "Welcome to Onslaught Career Editor! This tool unlocks everything in your career file.";
            
            // Set up rank combo box to update score automatically
            RankComboBox.SelectionChanged += RankComboBox_SelectionChanged;
            
            // Initialize default recommended score
            UpdateScoreBasedOnRank();
        }

        private void RankComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateScoreBasedOnRank();
        }

        private void UpdateScoreBasedOnRank()
        {
            // Update the score text box based on the selected rank
            // PC grade calculation uses specific float values, not the large "score" values
            switch (RankComboBox.SelectedIndex)
            {
                case 0: // S rank
                    ScoreTextBox.Text = "1.0";
                    break;
                case 1: // A rank
                    ScoreTextBox.Text = "0.75";
                    break;
                case 2: // B rank
                    ScoreTextBox.Text = "0.5";
                    break;
                case 3: // C rank
                    ScoreTextBox.Text = "0.25";
                    break;
                case 4: // D rank
                    ScoreTextBox.Text = "0.1";
                    break;
                default:
                    ScoreTextBox.Text = "1.0"; // Default to S rank
                    break;
            }
        }

        private void BrowseInputButton_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog
            {
                Filter = "BES Files (*.bes)|*.bes|All Files (*.*)|*.*",
                Title = "Select Input BES File"
            };

            if (openFileDialog.ShowDialog() == true)
            {
                InputFileTextBox.Text = openFileDialog.FileName;
                
                // Auto-generate output file name
                string? directory = Path.GetDirectoryName(openFileDialog.FileName);
                string fileName = Path.GetFileNameWithoutExtension(openFileDialog.FileName);
                string extension = Path.GetExtension(openFileDialog.FileName);
                
                // Handle potential null directory
                directory = directory ?? string.Empty;
                OutputFileTextBox.Text = Path.Combine(directory, $"{fileName}_patched{extension}");
                
                UpdatePatchButtonState();
            }
        }

        private void BrowseOutputButton_Click(object sender, RoutedEventArgs e)
        {
            SaveFileDialog saveFileDialog = new SaveFileDialog
            {
                Filter = "BES Files (*.bes)|*.bes|All Files (*.*)|*.*",
                Title = "Select Output BES File"
            };
            
            // Only set filename if we have a valid one
            if (!string.IsNullOrEmpty(OutputFileTextBox.Text))
            {
                saveFileDialog.FileName = OutputFileTextBox.Text;
            }

            if (saveFileDialog.ShowDialog() == true)
            {
                OutputFileTextBox.Text = saveFileDialog.FileName;
                UpdatePatchButtonState();
            }
        }

        private void PatchButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                PatchButton.IsEnabled = false;
                StatusTextBlock.Text = "Patching file...";
                
                // Configure patcher with UI settings
                ConfigurePatcher();
                
                // Perform the patching
                string result = _patcher.PatchFile(InputFileTextBox.Text, OutputFileTextBox.Text);
                StatusTextBlock.Text = result;
            }
            catch (Exception ex)
            {
                StatusTextBlock.Text = $"Error: {ex.Message}";
            }
            finally
            {
                PatchButton.IsEnabled = true;
            }
        }

        private void ConfigurePatcher()
        {
            // Set God Mode flag
            _patcher.EnableGodMode = GodModeCheckBox.IsChecked == true;
            
            // Set Objectives flag
            _patcher.EnableAllObjectives = ObjectivesCheckBox.IsChecked == true;
            
            // Set NEW/OLD goodie state
            _patcher.UseNewGoodiesInstead = NewGoodiesCheckBox.IsChecked == true;
            
            // Set score for rankings
            if (float.TryParse(ScoreTextBox.Text, out float score))
            {
                _patcher.RankingScore = score;
            }
            
            // Set kill count
            if (int.TryParse(KillCountTextBox.Text, out int killCount))
            {
                _patcher.GlobalKillCount = killCount;
            }
        }

        private void UpdatePatchButtonState()
        {
            PatchButton.IsEnabled = !string.IsNullOrWhiteSpace(InputFileTextBox.Text) && 
                                   !string.IsNullOrWhiteSpace(OutputFileTextBox.Text);
            
            if (PatchButton.IsEnabled)
            {
                StatusTextBlock.Text = "Ready to patch!";
            }
        }
    }
}
