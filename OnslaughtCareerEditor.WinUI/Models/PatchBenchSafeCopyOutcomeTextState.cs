namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchSafeCopyOutcomeTextState(
        bool CopiedSavegames,
        PatchBenchSafeCopyControlOptionsTextState? ControlOptions,
        PatchBenchSafeCopyMusicSwapTextState? MusicSwap,
        string SafeCopyFolderName,
        int FilesCopied,
        string PatchDisplayList,
        string LaunchModifierSummary,
        bool Level100TextModApplied,
        bool Level100EarlyFlightModApplied);
}
