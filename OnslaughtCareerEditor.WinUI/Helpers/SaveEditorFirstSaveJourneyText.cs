using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class SaveEditorFirstSaveJourneyText
{
    public static string BuildStatus(SaveEditorFirstSaveJourneyState state)
    {
        if (!state.HasValidInput)
        {
            return "Choose an existing .bes career save to begin.";
        }

        if (!state.HasValidOutput)
        {
            return "Keep the suggested separate .bes output or choose another non-game destination.";
        }

        if (state.HasCompletedCurrentPlan)
        {
            return state.CanRevealWrittenCopy
                ? "Written copy ready. Show it in File Explorer, then manually copy it into a Safe Game Copy's savegames folder when ready to try it."
                : "Written copy ready at the chosen destination. Manually copy it into a Safe Game Copy's savegames folder when ready to try it.";
        }

        if (!state.HasSelectedChanges)
        {
            return "Choose at least one change. Start empty is selected by default.";
        }

        if (state.CanWrite)
        {
            return "Review Pending changes, then write the separate copy to run final safety checks.";
        }

        return "Resolve the safety message below before writing the copied save.";
    }

    public static string BuildAdvancedOverrideStatus(int missionCount, int categoryCount)
    {
        missionCount = Math.Max(0, missionCount);
        categoryCount = Math.Max(0, categoryCount);
        if (missionCount == 0 && categoryCount == 0)
        {
            return "No advanced overrides active";
        }

        string missionText = missionCount == 1 ? "1 mission override" : $"{missionCount} mission overrides";
        string categoryText = categoryCount == 1 ? "1 category-kill override" : $"{categoryCount} category-kill overrides";
        if (missionCount == 0)
        {
            return $"{categoryText} active";
        }

        if (categoryCount == 0)
        {
            return $"{missionText} active";
        }

        return $"{missionText} and {categoryText} active";
    }
}
