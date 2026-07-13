namespace OnslaughtCareerEditor.WinUI.Models;

internal sealed record SaveEditorOutputSelectionState(string OutputPath, bool OutputWasAutoSuggested);

internal sealed record SaveEditorSectionSelection(
    bool KillsOnly,
    bool PatchNodes,
    bool PatchLinks,
    bool PatchGoodies,
    bool PatchKills);

internal sealed record SaveEditorPresetTransition(SaveEditorSectionSelection Selection, string VisiblePreset);

internal sealed record SaveEditorCompletionState(string OutputPath, string PlanFingerprint);

internal sealed record SaveEditorCompletionEvaluation(bool IsCurrent, bool CanReveal);
