using System.Collections.ObjectModel;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class SavesPage
    {
        private readonly ObservableCollection<SaveMissionRankRow> _editorMissionRankRows = new();
        private readonly ObservableCollection<SaveCategoryKillRow> _editorCategoryKillRows = new();

        private void InitializeEditorAdvancedSurface()
        {
            EditorMissionRanksListView.ItemsSource = _editorMissionRankRows;
            EditorCategoryKillsListView.ItemsSource = _editorCategoryKillRows;
            LoadEditorAdvancedSnapshot();
        }

        private void LoadEditorAdvancedSnapshot()
        {
            string inputPath = _editorInputValid ? (EditorInputFileTextBox.Text ?? string.Empty).Trim() : string.Empty;

            _editorMissionRankRows.Clear();
            foreach (SaveMissionRankRow row in SaveEditorAdvancedService.LoadMissionRankRows(inputPath))
            {
                _editorMissionRankRows.Add(row);
            }

            _editorCategoryKillRows.Clear();
            foreach (SaveCategoryKillRow row in SaveEditorAdvancedService.LoadCategoryKillRows(inputPath))
            {
                _editorCategoryKillRows.Add(row);
            }

            EditorKillBaselineSummaryTextBlock.Text = SaveEditorAdvancedService.BuildKillSeedSummary(_editorCategoryKillRows);
            if (_editorInputValid)
            {
                EditorGlobalKillNumberBox.Value = SaveEditorAdvancedService.GetSuggestedGlobalKillSeed(_editorCategoryKillRows);
            }

            UpdateEditorActionState();
        }

        private void EditorSetMissionRanksToDefaultButton_Click(object sender, RoutedEventArgs e)
        {
            string defaultRank = (EditorRankComboBox.SelectedItem as ComboBoxItem)?.Tag as string ?? "S";
            foreach (SaveMissionRankRow row in _editorMissionRankRows)
            {
                row.SelectedRank = defaultRank;
            }

            EditorMissionRanksListView.ItemsSource = null;
            EditorMissionRanksListView.ItemsSource = _editorMissionRankRows;
            UpdateEditorActionState();
        }

        private void EditorClearMissionRanksButton_Click(object sender, RoutedEventArgs e)
        {
            foreach (SaveMissionRankRow row in _editorMissionRankRows)
            {
                row.SelectedRank = "Keep";
            }

            EditorMissionRanksListView.ItemsSource = null;
            EditorMissionRanksListView.ItemsSource = _editorMissionRankRows;
            UpdateEditorActionState();
        }

        private void EditorMissionRankOverrideComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            UpdateEditorActionState();
        }

        private void EditorCategoryKillOverrideCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            UpdateEditorActionState();
        }

        private void EditorCategoryKillNumberBox_ValueChanged(NumberBox sender, NumberBoxValueChangedEventArgs args)
        {
            UpdateEditorActionState();
        }

        private bool TryBuildEditorAdvancedOverrides(
            out Dictionary<int, string>? levelRanks,
            out Dictionary<int, int>? perCategoryKills,
            out string? error)
        {
            error = null;
            if (!SaveEditorAdvancedService.TryBuildLevelRanks(_editorMissionRankRows, out levelRanks, out string? levelRankError))
            {
                perCategoryKills = null;
                error = levelRankError;
                return false;
            }

            if (!SaveEditorAdvancedService.TryBuildPerCategoryKills(_editorCategoryKillRows, out perCategoryKills, out string? killError))
            {
                error = killError;
                return false;
            }

            return true;
        }
    }
}
