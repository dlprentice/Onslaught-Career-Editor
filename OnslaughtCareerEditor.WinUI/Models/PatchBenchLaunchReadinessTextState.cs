namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchLaunchReadinessTextState(
        bool ContentMatchesCurrent,
        bool HasLaunchPlan,
        string? CommandPreview,
        string? LaunchError);
}
