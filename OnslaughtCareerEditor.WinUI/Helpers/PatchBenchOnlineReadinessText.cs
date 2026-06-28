using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtCareerEditor.WinUI.Models;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchOnlineReadinessText
    {
        public static PatchBenchOnlineReadinessTextState Build(
            OnlineMultiplayerReadinessSummary summary,
            OnlineSecondHostReadinessArtifactSummary? secondHostReadinessArtifact,
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact,
            OnlineDualSafeCopyTopologyArtifactSummary? dualSafeCopyTopologyArtifact)
        {
            OnlineMultiplayerStatusRow? proofClass = summary.StatusRows.FirstOrDefault(row =>
                string.Equals(row.Label, "Current proof class", StringComparison.Ordinal));

            return new PatchBenchOnlineReadinessTextState(
                Headline: "Online play is not available yet",
                Slots: "You can still use local split-screen in a safe copy.",
                MetadataSlots: "There is no Host or Join workflow in this build; larger-player support remains future design work.",
                TargetModel: FormatCompanionNetplayTarget(summary.CompanionNetplayTarget),
                ProofClass: $"Current test coverage: {proofClass?.Value ?? "not proven"}",
                NextProof: "Next work: prove a real second computer or VM can send a command, then prove that command drives the copied game in the same run.",
                GateDetails: $"Technical gates: {FormatOnlineProofGateSummary(summary)}",
                ProofLadder: $"Proof ladder (technical status only):{Environment.NewLine}{FormatOnlineProofLadder(summary.ProofLadderRows)}",
                CompanionModelDetails: FormatCompanionNetplayDetails(summary.CompanionNetplayTarget),
                SecondHostSetupChecklist: $"Setup steps: {FormatSecondHostSetupChecklist(summary.SecondHostSetupSteps)}",
                BlockedActions: $"Unavailable: {string.Join(", ", summary.BlockedActions.Where(action => !action.Enabled).Select(action => action.Label))}",
                BlockedReasons: $"Why unavailable: {string.Join("; ", summary.BlockedActions.Where(action => !action.Enabled).Select(action => $"{action.Label}: {action.Reason}"))}",
                LiveAttemptStatus: FormatSecondHostLiveAttemptStatus(summary.SecondHostLiveAttemptReadiness),
                LiveAttemptBlockers: FormatSecondHostLiveAttemptBlockers(summary.SecondHostLiveAttemptReadiness),
                LiveAttemptCommands: FormatSecondHostLiveAttemptCommands(summary.SecondHostLiveAttemptReadiness),
                PromotionLockStatus: FormatOnlinePromotionLockStatus(summary),
                SecondHostReadinessArtifactStatus: FormatSecondHostReadinessArtifactStatus(secondHostReadinessArtifact),
                GamepadReadinessArtifactStatus: FormatLocalGamepadReadinessArtifactStatus(localGamepadReadinessArtifact),
                DualSafeCopyTopologyArtifactStatus: FormatDualSafeCopyTopologyArtifactStatus(dualSafeCopyTopologyArtifact),
                DualSafeCopyTopologyBoundary: "Not online multiplayer: no BEA launch, listener, invitation, remote input, Host/Join controls, distinct endpoint proof, or player-ready netplay.",
                DualSafeCopyTopologyNextProofs: "Why Host/Join is locked: topology/status only. Host/Join requires both a real VM or second PC command-source proof and source-bound copied-runtime causality in the same run.");
        }

        public static PatchBenchOnlineCompanionSessionTextState BuildCompanionSession(
            OnlineCompanionSessionReadinessSummary summary)
        {
            return new PatchBenchOnlineCompanionSessionTextState(
                PrepActionStatus: BuildOnlinePrepActionStatus(summary),
                SessionStatus: $"Safe copy status: {FormatCompanionSafeCopyStatus(summary.SafeCopyManifestStatus)} Host/Join stay off.",
                LaunchPlan: $"Launch plan: {summary.LaunchPlanPreview}",
                NextProofs: "Next online work: real second-host command test, then source-bound runtime proof for the copied game.",
                NonClaims: $"Current limits: {FormatCompanionLimits(summary.NonClaims)}");
        }

        public static string FormatSecondHostReadinessArtifactStatus(OnlineSecondHostReadinessArtifactSummary? artifact)
        {
            if (artifact is null)
            {
                return "No second-host readiness summary loaded. Host/Join remain unavailable.";
            }

            string status = artifact.ReadyToRunLiveCommandSource
                ? "ready for future live command-source review"
                : "not ready for a live command-source run";
            return
                $"Loaded {artifact.SourceKind} summary: {status}; " +
                $"server inputs {(artifact.ServerCommandInputsComplete ? "complete" : "incomplete")}; " +
                $"client preflight {(artifact.ClientPreflightProvided ? "provided" : "missing")}; " +
                $"network candidates checked: {artifact.CandidatePrivateBindAddressCount + artifact.WslOnHostInterfaceCount}. " +
                "Online play is not player-ready. Host/Join remain unavailable.";
        }

        public static string FormatLocalGamepadReadinessArtifactStatus(OnlineLocalGamepadReadinessArtifactSummary? artifact)
        {
            if (artifact is null)
            {
                return "No physical controller readiness summary loaded. Hardware readiness only; Host/Join remain unavailable.";
            }

            string readyText = artifact.ReadyForPhysicalGamepadRuntimeAttempt
                ? "ready for a physical-controller runtime attempt"
                : "not ready for a physical-controller runtime attempt";
            return
                $"Loaded {artifact.SourceKind} summary: status={artifact.Status}; {readyText}; " +
                $"presentGamepadCandidateCount={artifact.PresentGamepadCandidateCount}; registryGamepadCandidateCount={artifact.RegistryGamepadCandidateCount}; " +
                $"pnpDeviceCount={artifact.PnpDeviceCount}; joystickRegistryRowCount={artifact.JoystickRegistryRowCount}. " +
                "hardware preflight only; no BEA DirectInput/runtime proof, visible movement proof, Host/Join, or online proof.";
        }

        public static string FormatDualSafeCopyTopologyArtifactStatus(OnlineDualSafeCopyTopologyArtifactSummary? artifact)
        {
            if (artifact is null)
            {
                return "No dual-safe-copy topology summary loaded. Host/Join remain unavailable.";
            }

            return
                $"Loaded dual-safe-copy topology summary: descriptor-only same-workstation topology; safeCopyCount={artifact.SafeCopyCount}; roles={string.Join(",", artifact.Roles)}; " +
                $"sameWorkstationOnly={artifact.SameWorkstationOnly}; samePhysicalMachineOnly={artifact.SamePhysicalMachineOnly}; " +
                $"root/executable descriptor counts={artifact.SafeCopyRootDescriptorCount}/{artifact.SafeCopyExecutableDescriptorCount}; " +
                "no BEA launch, CDB attach, listener, invitation, remote input, Host/Join, distinct endpoint proof, or player-ready netplay. " +
                "Host/Join remain unavailable.";
        }

        private static string BuildOnlinePrepActionStatus(OnlineCompanionSessionReadinessSummary summary)
        {
            if (summary.SafeCopyManifestStatus == "safe-copy-launch-plan-ready" && summary.TryableActions.Count > 0)
            {
                OnlineMultiplayerTryableAction action = summary.TryableActions[0];
                return $"Ready safe-copy action: {action.Label}. Launch uses {action.LaunchHint}; this remains local split-screen only, not Host/Join or online proof.";
            }

            return "Select the local split-screen launch preset, then create and play a safe copy. This is not Host/Join or online proof.";
        }

        private static string FormatOnlineProofGateSummary(OnlineMultiplayerReadinessSummary summary)
        {
            bool commandSourcePending = summary.ProofGateRows.Any(row =>
                row.Label.Contains("command source", StringComparison.OrdinalIgnoreCase) &&
                row.Value.Contains("not accepted", StringComparison.OrdinalIgnoreCase));
            bool runtimeCausalityPending = summary.ProofGateRows.Any(row =>
                row.Label.Contains("runtime causality", StringComparison.OrdinalIgnoreCase) &&
                row.Value.Contains("not accepted", StringComparison.OrdinalIgnoreCase));

            if (commandSourcePending && runtimeCausalityPending)
            {
                return "real second-host command proof and same-run copied-game runtime proof are both still pending.";
            }

            return string.Join("; ", summary.ProofGateRows.Select(row => $"{row.Label}: {row.Value}"));
        }

        private static string FormatCompanionNetplayTarget(OnlineCompanionNetplayTarget target)
        {
            return $"Future design sketch; Host/Join unavailable. {target.UserExperience}";
        }

        private static string FormatCompanionNetplayDetails(OnlineCompanionNetplayTarget target)
        {
            return $"Companion model: {target.HostRole} {target.JoinRole} {target.ViewModel} {target.CompanionRequirement} {target.CurrentBoundary}";
        }

        private static string FormatOnlineProofLadder(IReadOnlyList<OnlineMultiplayerProofLadderRow> rows)
        {
            if (rows.Count == 0)
            {
                return "No proof-ladder rows are loaded; Host/Join remains unavailable.";
            }

            return string.Join(Environment.NewLine, rows.Select(row => $"{row.Label}: {row.Status} - {row.Detail}"));
        }

        private static string FormatSecondHostSetupChecklist(IReadOnlyList<OnlineMultiplayerSetupStep> steps)
        {
            return string.Join("; ", steps.Select(step => $"{step.Label} ({step.Status}) - {step.Detail}"));
        }

        private static string FormatSecondHostLiveAttemptStatus(OnlineSecondHostLiveAttemptReadiness readiness)
        {
            string status = readiness.ReadyToRunLiveCommandSource
                ? "ready to run live command-source candidate; online play is not available in this release and Host/Join remain unavailable"
                : "not ready for a live command-source run";
            string blockers = readiness.BlockingReasons.Count == 0
                ? "no readiness blockers recorded"
                : string.Join("; ", readiness.BlockingReasons);
            return $"Second-host live attempt: {status}. Checklist: server command inputs {(readiness.ServerCommandInputsComplete ? "ready" : "incomplete")}; client preflight {(readiness.ClientPreflightProvided ? "provided" : "missing")}; Host/Join controls {(readiness.HostJoinControlsMayBeEnabled ? "eligible for future review" : "locked")}. Blockers: {blockers}.";
        }

        private static string FormatOnlinePromotionLockStatus(OnlineMultiplayerReadinessSummary summary)
        {
            OnlineMultiplayerStatusRow? lockRow = summary.StatusRows.FirstOrDefault(row =>
                string.Equals(row.Label, "Host/Join promotion lock", StringComparison.Ordinal));
            return $"{lockRow?.Value ?? "Online play is not player-ready; readiness artifacts cannot enable Host/Join."} Host/Join remain unavailable until a real separate-machine input test also proves copied-game behavior.";
        }

        private static string FormatSecondHostLiveAttemptBlockers(OnlineSecondHostLiveAttemptReadiness readiness)
        {
            return $"Blocked by: {string.Join("; ", readiness.BlockingReasons)}";
        }

        private static string FormatSecondHostLiveAttemptCommands(OnlineSecondHostLiveAttemptReadiness readiness)
        {
            return $"Safe checks: {string.Join("; ", readiness.SafeCommands)}";
        }

        private static string FormatCompanionSafeCopyStatus(string status)
        {
            return status switch
            {
                "missing-safe-copy" => "create a safe game copy first.",
                "stale-safe-copy" => "create a fresh safe game copy for the current selections.",
                "launch-plan-blocked" => "fix the safe-copy launch plan before testing.",
                "safe-copy-launch-plan-ready" => "safe copy is ready for local launch tests.",
                _ => status
            };
        }

        private static string FormatCompanionLimits(IReadOnlyList<string> nonClaims)
        {
            var labels = new List<string>();
            if (nonClaims.Contains("no listener", StringComparer.OrdinalIgnoreCase))
            {
                labels.Add("no network listener");
            }

            if (nonClaims.Contains("no invitation", StringComparer.OrdinalIgnoreCase))
            {
                labels.Add("no invitation");
            }

            if (nonClaims.Contains("no remote input", StringComparer.OrdinalIgnoreCase))
            {
                labels.Add("no remote input");
            }

            if (nonClaims.Contains("no Host/Join controls", StringComparer.OrdinalIgnoreCase))
            {
                labels.Add("no Host/Join controls");
            }

            return labels.Count == 0 ? string.Join(", ", nonClaims) : string.Join(", ", labels) + ".";
        }
    }
}
