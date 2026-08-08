using OnslaughtCareerEditor.WinUI.Models;
using OnslaughtCareerEditor.AppCore;

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

    /// <summary>
    /// Advanced overrides are only consumed by their owning section pass, so a plan that carries
    /// mission-rank overrides without node patching (or category-kill overrides without kill
    /// patching) would drop part of the user's stated intent. AppCore rejects such a plan; the
    /// Save Editor keeps Write disabled so the user is told before they attempt the write.
    /// </summary>
    public static bool AreOverrideDependenciesSatisfied(
        SavePatchRequest request,
        int missionRankOverrideCount,
        int categoryKillOverrideCount)
    {
        return (missionRankOverrideCount == 0 || request.PatchNodes)
            && (categoryKillOverrideCount == 0 || request.PatchKills);
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
