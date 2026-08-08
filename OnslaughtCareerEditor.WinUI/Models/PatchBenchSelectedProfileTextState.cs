using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchSelectedProfileTextState(
        int SelectedVisibleRowCount,
        SafeCopyProfilePreset? MatchedPreset,
        bool IsModernGraphicsOnly);
}
