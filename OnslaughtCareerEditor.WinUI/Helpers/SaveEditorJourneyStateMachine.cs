using OnslaughtCareerEditor.WinUI.Models;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class SaveEditorJourneyStateMachine
{
    public static SaveEditorOutputSelectionState ApplyInputSuggestion(
        SaveEditorOutputSelectionState current,
        string suggestedOutput)
    {
        return string.IsNullOrWhiteSpace(current.OutputPath) || current.OutputWasAutoSuggested
            ? new SaveEditorOutputSelectionState(suggestedOutput, true)
            : current;
    }

    public static SaveEditorOutputSelectionState ApplyManualOutput(
        SaveEditorOutputSelectionState current,
        string explicitOutput)
    {
        return new SaveEditorOutputSelectionState(explicitOutput, false);
    }

    public static SaveEditorPresetTransition ApplyPreset(string requestedPreset, SaveEditorSectionSelection current)
    {
        SaveEditorSectionSelection selection = requestedPreset switch
        {
            "SAFE" => new SaveEditorSectionSelection(false, false, false, false, false),
            "QUICK" => new SaveEditorSectionSelection(false, true, true, true, true),
            _ => current,
        };
        return new SaveEditorPresetTransition(selection, ClassifyPreset(selection));
    }

    public static string ClassifyPreset(SaveEditorSectionSelection selection)
    {
        if (!selection.KillsOnly
            && selection.PatchNodes
            && selection.PatchLinks
            && selection.PatchGoodies
            && selection.PatchKills)
        {
            return "QUICK";
        }

        if (!selection.KillsOnly
            && !selection.PatchNodes
            && !selection.PatchLinks
            && !selection.PatchGoodies
            && !selection.PatchKills)
        {
            return "SAFE";
        }

        return "CUSTOM";
    }

    public static SaveEditorCompletionState RecordSuccessfulWrite(SavePatchRequest request, string outputPath)
    {
        return new SaveEditorCompletionState(NormalizePath(outputPath), SaveEditorPlanFingerprint.Build(request));
    }

    public static SaveEditorCompletionEvaluation EvaluateCompletion(
        SaveEditorCompletionState? completion,
        SavePatchRequest currentRequest,
        bool outputExists,
        string appOwnedRoot)
    {
        if (completion is null || !outputExists)
        {
            return new SaveEditorCompletionEvaluation(false, false);
        }

        bool isCurrent =
            string.Equals(completion.PlanFingerprint, SaveEditorPlanFingerprint.Build(currentRequest), StringComparison.Ordinal)
            && string.Equals(completion.OutputPath, NormalizePath(currentRequest.OutputPath), StringComparison.OrdinalIgnoreCase);
        return new SaveEditorCompletionEvaluation(
            isCurrent,
            isCurrent && SaveEditorPlanFingerprint.IsInsideDirectory(currentRequest.OutputPath, appOwnedRoot));
    }

    public static SaveEditorCompletionState? ApplyRevealAttempt(
        SaveEditorCompletionState? completion,
        bool preconditionsCurrent,
        bool launcherSucceeded)
    {
        _ = launcherSucceeded;
        return preconditionsCurrent ? completion : null;
    }

    private static string NormalizePath(string path)
    {
        try
        {
            return Path.GetFullPath(path.Trim());
        }
        catch
        {
            return path.Trim();
        }
    }
}
