namespace OnslaughtCareerEditor.WinUI.Models;

internal sealed record SaveEditorFirstSaveJourneyState(
    bool HasValidInput,
    bool HasValidOutput,
    bool HasSelectedChanges,
    bool CanWrite,
    bool HasCompletedCurrentPlan,
    bool CanRevealWrittenCopy);
