namespace OnslaughtCareerEditor.WinUI.Models;

internal sealed record PatchBenchLabCreationInputState(
    int OptionalPatchCount,
    int LaunchModifierCount,
    int CopiedOptionsCount,
    bool HasCreateTimeMusicExperiment,
    bool HasLevel100TextMod,
    bool HasLevel100EarlyFlightMod);
