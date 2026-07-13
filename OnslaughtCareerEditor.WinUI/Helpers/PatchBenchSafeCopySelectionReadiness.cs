using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class PatchBenchSafeCopySelectionReadiness
{
    public static PatchBenchSafeCopySelectionReadinessState Build(
        bool hasSourceExecutable,
        bool isBusy,
        string? validationError,
        int optionalPatchCount)
    {
        if (!string.IsNullOrWhiteSpace(validationError))
        {
            return new(false, $"Review optional mods: {validationError}");
        }

        if (isBusy)
        {
            return new(false, "Safe game copy work is already in progress.");
        }

        if (!hasSourceExecutable)
        {
            return new(false, "Selection is valid. Choose a read-only BEA.exe source to create a safe game copy.");
        }

        return optionalPatchCount == 0
            ? new(true, "Required compatibility base ready. No optional mods selected.")
            : new(
                true,
                $"Required compatibility base ready with {optionalPatchCount} optional {(optionalPatchCount == 1 ? "mod" : "mods")} selected.");
    }
}
