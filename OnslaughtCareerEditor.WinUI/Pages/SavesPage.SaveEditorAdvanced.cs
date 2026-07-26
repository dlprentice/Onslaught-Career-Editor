using System.Collections.ObjectModel;
using System.Linq;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class SavesPage
    {
        private readonly ObservableCollection<SaveMissionRankRow> _editorMissionRankRows = new();
        private readonly ObservableCollection<SaveCategoryKillRow> _editorCategoryKillRows = new();
        private bool _editorGlobalKillWasAutoSeeded = true;
        private bool _suppressEditorGlobalKillProvenance;

        private void InitializeEditorAdvancedSurface()
        {
            EditorMissionRanksListView.ItemsSource = _editorMissionRankRows;
            EditorCategoryKillsListView.ItemsSource = _editorCategoryKillRows;
            LoadEditorAdvancedSnapshot();
        }

        private void LoadEditorAdvancedSnapshot()
        {
            string inputPath = _editorInputValid ? (EditorInputFileTextBox.Text ?? string.Empty).Trim() : string.Empty;

            // Snapshot the user's own choices before the rows are rebuilt from the file. Rebuilding used to
            // discard every configured override silently, including on a single keystroke in the input path.
            SaveMissionRankRow[] previousMissionRanks = _editorMissionRankRows.ToArray();
            SaveCategoryKillRow[] previousCategoryKills = _editorCategoryKillRows.ToArray();

            SaveMissionRankRow[] reloadedMissionRanks =
                SaveEditorAdvancedService.LoadMissionRankRows(inputPath).ToArray();
            SaveCategoryKillRow[] reloadedCategoryKills =
                SaveEditorAdvancedService.LoadCategoryKillRows(inputPath).ToArray();

            int carriedMissionRanks = SaveEditorAdvancedOverrideCarryOver.ApplyMissionRankOverrides(
                previousMissionRanks,
                reloadedMissionRanks);
            int carriedCategoryKills = SaveEditorAdvancedOverrideCarryOver.ApplyCategoryKillOverrides(
                previousCategoryKills,
                reloadedCategoryKills);

            _editorMissionRankRows.Clear();
            foreach (SaveMissionRankRow row in reloadedMissionRanks)
            {
                _editorMissionRankRows.Add(row);
            }

            _editorCategoryKillRows.Clear();
            foreach (SaveCategoryKillRow row in reloadedCategoryKills)
            {
                _editorCategoryKillRows.Add(row);
            }

            string killSeedSummary = SaveEditorAdvancedService.BuildKillSeedSummary(
                _editorInputValid ? _editorCategoryKillRows : Array.Empty<SaveCategoryKillRow>());
            string? carryOverNotice = SaveEditorAdvancedOverrideCarryOver.DescribeCarryOver(
                carriedMissionRanks,
                carriedCategoryKills);
            EditorKillBaselineSummaryTextBlock.Text = carryOverNotice is null
                ? killSeedSummary
                : $"{carryOverNotice} {killSeedSummary}";

            if (SaveEditorAdvancedOverrideCarryOver.ShouldReseedGlobalKillValue(
                    _editorInputValid,
                    _editorGlobalKillWasAutoSeeded))
            {
                _suppressEditorGlobalKillProvenance = true;
                try
                {
                    EditorGlobalKillNumberBox.Value =
                        SaveEditorAdvancedService.GetSuggestedGlobalKillSeed(_editorCategoryKillRows);
                }
                finally
                {
                    _suppressEditorGlobalKillProvenance = false;
                }
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
