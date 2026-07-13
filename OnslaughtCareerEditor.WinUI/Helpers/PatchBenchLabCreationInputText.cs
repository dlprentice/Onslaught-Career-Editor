using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class PatchBenchLabCreationInputText
{
    public static string BuildStatus(PatchBenchLabCreationInputState state)
    {
        var categories = new List<string>();
        AddCount(categories, state.OptionalPatchCount, "patch choice", "patch choices");
        AddCount(categories, state.LaunchModifierCount, "launch modifier", "launch modifiers");
        AddCount(categories, state.CopiedOptionsCount, "copied-options change", "copied-options changes");
        if (state.HasCreateTimeMusicExperiment)
        {
            categories.Add("1 create-time music experiment");
        }

        return categories.Count == 0
            ? "Extra settings for next copy: none active."
            : $"Extra settings for next copy: {string.Join("; ", categories)}.";
    }

    public static string BuildConfirmationSection(PatchBenchLabCreationInputState state)
    {
        return $"Settings affecting this copy:{Environment.NewLine}{BuildStatus(state)}";
    }

    private static void AddCount(List<string> categories, int count, string singular, string plural)
    {
        if (count > 0)
        {
            categories.Add($"{count} {(count == 1 ? singular : plural)}");
        }
    }
}
