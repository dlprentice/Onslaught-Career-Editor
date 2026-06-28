namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchOnlineReadinessTextState(
        string Headline,
        string Slots,
        string MetadataSlots,
        string TargetModel,
        string ProofClass,
        string NextProof,
        string GateDetails,
        string ProofLadder,
        string CompanionModelDetails,
        string SecondHostSetupChecklist,
        string BlockedActions,
        string BlockedReasons,
        string LiveAttemptStatus,
        string LiveAttemptBlockers,
        string LiveAttemptCommands,
        string PromotionLockStatus,
        string SecondHostReadinessArtifactStatus,
        string GamepadReadinessArtifactStatus,
        string DualSafeCopyTopologyArtifactStatus,
        string DualSafeCopyTopologyBoundary,
        string DualSafeCopyTopologyNextProofs);
}
