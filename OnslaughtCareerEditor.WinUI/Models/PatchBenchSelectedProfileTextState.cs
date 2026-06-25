using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchSelectedProfileTextState(
        int SelectedVisibleRowCount,
        SafeCopyProfilePreset? MatchedPreset,
        bool IsModernGraphicsOnly);
}
