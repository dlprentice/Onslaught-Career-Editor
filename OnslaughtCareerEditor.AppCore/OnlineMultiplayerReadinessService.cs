using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;

namespace Onslaught___Career_Editor
{
    public sealed record OnlineMultiplayerStatusRow(string Label, string Value);

    public sealed record OnlineMultiplayerTryableAction(string Label, string LaunchHint, string Description);

    public sealed record OnlineMultiplayerBlockedAction(string Label, bool Enabled, string Reason);

    public sealed record OnlineMultiplayerProofGateRow(string Label, string Value);

    public sealed record OnlineMultiplayerProofLadderRow(string Label, string Status, string Detail);

    public sealed record OnlineMultiplayerSetupStep(string Label, string Status, string Detail);

    public sealed record OnlineSecondHostLiveAttemptReadiness(
        string SchemaVersion,
        bool ReadyToAttemptHarness,
        bool ReadyForLiveValidationCandidate,
        bool ReadyToRunLiveCommandSource,
        bool ServerCommandInputsComplete,
        bool ClientPreflightProvided,
        int CandidatePrivateBindAddressCount,
        int WslOnHostInterfaceCount,
        bool HostJoinControlsMayBeEnabled,
        bool AcceptedLiveSecondHostCommandSourceProof,
        bool BaseOnlineMultiplayerReady,
        IReadOnlyList<OnlineMultiplayerSetupStep> RequiredInputs,
        IReadOnlyList<string> BlockingReasons,
        IReadOnlyList<string> SafeCommands);

    public sealed record OnlineSecondHostReadinessArtifactSummary(
        string SchemaVersion,
        string Status,
        string SourceKind,
        bool ReadyToAttemptHarness,
        bool ReadyForLiveValidationCandidate,
        bool ReadyToRunLiveCommandSource,
        bool ServerCommandInputsComplete,
        bool ClientPreflightProvided,
        int CandidatePrivateBindAddressCount,
        int WslOnHostInterfaceCount);

    public sealed record OnlineLocalGamepadReadinessArtifactSummary(
        string SchemaVersion,
        string Status,
        string SourceKind,
        bool ReadyForPhysicalGamepadRuntimeAttempt,
        int PresentGamepadCandidateCount,
        int RegistryGamepadCandidateCount,
        int PnpDeviceCount,
        int JoystickRegistryRowCount);

    public sealed record OnlineDualSafeCopyTopologyArtifactSummary(
        string SchemaVersion,
        string Status,
        string Scope,
        string SourceKind,
        int SafeCopyCount,
        IReadOnlyList<string> Roles,
        bool SameWorkstationOnly,
        bool SamePhysicalMachineOnly,
        int SafeCopyRootDescriptorCount,
        int SafeCopyExecutableDescriptorCount,
        int DistinctSafeCopyRootPairCount,
        int BeaLaunchCount,
        int ProcessStartCount,
        int CdbAttachCount,
        int ListenerOpenCount,
        int InvitationCreateCount,
        int HostJoinControlsEnabledCount,
        IReadOnlyList<string> RequiredFutureEvidenceIds,
        string ClaimBoundary);

    public sealed record OnlineCompanionNetplayTarget(
        string UserExperience,
        string HostRole,
        string JoinRole,
        string ViewModel,
        string CompanionRequirement,
        string CurrentBoundary);

    public sealed record OnlineCompanionSessionReadinessSummary(
        string SchemaVersion,
        string SafeCopyManifestStatus,
        string LaunchPlanPreview,
        bool MayEnableHostJoin,
        bool BaseOnlineMultiplayerReady,
        IReadOnlyList<OnlineMultiplayerTryableAction> TryableActions,
        IReadOnlyList<OnlineMultiplayerBlockedAction> BlockedActions,
        IReadOnlyList<string> NextProofIds,
        IReadOnlyList<string> NonClaims);

    public sealed record OnlineMultiplayerReadinessSummary(
        string SchemaVersion,
        bool BaseOnlineMultiplayerReady,
        bool MultiHostLanProof,
        bool PublicMatchmakingProof,
        bool NativeBeaNetcodeProof,
        bool ActiveP3P4OriginalBinaryGameplayProof,
        bool PhysicalGamepadRuntimeProof,
        IReadOnlyList<string> AcceptedOriginalBinaryGameplaySlots,
        IReadOnlyList<string> MetadataOnlySlots,
        IReadOnlyList<OnlineMultiplayerSetupStep> SecondHostSetupSteps,
        OnlineSecondHostLiveAttemptReadiness SecondHostLiveAttemptReadiness,
        IReadOnlyList<OnlineMultiplayerStatusRow> StatusRows,
        IReadOnlyList<OnlineMultiplayerTryableAction> TryableActions,
        IReadOnlyList<OnlineMultiplayerBlockedAction> BlockedActions,
        IReadOnlyList<OnlineMultiplayerProofGateRow> ProofGateRows,
        IReadOnlyList<OnlineMultiplayerProofLadderRow> ProofLadderRows,
        OnlineDualSafeCopyTopologyArtifactSummary? DualSafeCopyTopologyArtifact,
        OnlineCompanionNetplayTarget CompanionNetplayTarget,
        IReadOnlyList<string> NonClaims,
        string NextProofNeeded,
        string FallbackWithoutSecondHost);

    public static class OnlineMultiplayerReadinessService
    {
        private const string SecondHostLiveReadinessSchema = "winui-original-binary-second-host-live-readiness.v1";
        private const string SecondHostLiveRunKitSchema = "winui-original-binary-second-host-live-run-kit.v1";
        private const string LocalGamepadReadinessSchema = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1";
        private const string DualSafeCopyTopologySchema = "winui-original-binary-online-dual-safe-copy-topology.v1";
        private const string DualSafeCopyTopologyScope = "dual-safe-copy-same-workstation-topology-not-online-play";
        private const string DualSafeCopyTopologyStatus = "complete public-safe dual-safe-copy topology contract; no BEA launch or runtime proof";
        private const long MaxSecondHostReadinessArtifactBytes = 64 * 1024;
        private const long MaxLocalGamepadReadinessArtifactBytes = 64 * 1024;
        private const long MaxDualSafeCopyTopologyArtifactBytes = 64 * 1024;
        private const int MaxReadinessCounter = 4096;

        private static readonly string[] s_proofOverclaimKeys =
        {
            "hostJoinControlsMayBeEnabled",
            "baseOnlineMultiplayerReady",
            "acceptedLiveSecondHostCommandSourceProof",
            "acceptedLiveSecondHostRuntimeDeliveryProof",
            "acceptedLiveSecondHostRuntimeCausalityProof",
            "multiHostLanPlayProof",
            "publicMatchmakingProof",
            "nativeBeaNetcodeProof",
            "activeP3P4OriginalBinaryGameplayProof"
        };

        private static readonly string[] s_localGamepadRuntimeOverclaimKeys =
        {
            "physicalGamepadRuntimeProof",
            "gamepadRuntimeProof",
            "directInputPollingProof",
            "virtualControllerRoutingProof",
            "visibleMovementProof",
            "beaRuntimeInputProof",
            "onlineMultiplayerProof"
        };

        private static readonly string[] s_dualSafeCopyTopologyOverclaimKeys =
        {
            "rootPathPublished",
            "absolutePathsSerialized",
            "launchAllowedByThisRung",
            "installedGameMutationAllowed",
            "originalExecutableMutationAllowed",
            "steamInstallWriteAllowed",
            "separateGameViewsProven",
            "distinctEndpointProof",
            "playerReadyOnlineProof",
            "hostJoinControlsMayBeEnabled",
            "baseOnlineMultiplayerReady",
            "acceptedLiveSecondHostCommandSourceProof",
            "acceptedLiveSecondHostRuntimeDeliveryProof",
            "acceptedLiveSecondHostRuntimeCausalityProof",
            "secondHostProof",
            "multiHostLanPlayProof",
            "publicMatchmakingProof",
            "nativeBeaNetcodeProof",
            "activeP3P4OriginalBinaryGameplayProof",
            "moreThanTwoOriginalBinaryRuntimePlayersProof",
            "hostHelperInputSent",
            "gameInputSentByTopologyTool",
            "separateScreenNetplayProof",
            "deterministicSyncProof",
            "rollbackProof",
            "antiCheatProof",
            "coOpVersusRuntimeProof",
            "rebuildParityProof",
            "noNoticeableDifferenceProof",
            "listenerOpened",
            "invitationCreated",
            "inputSent",
            "patchBytesChanged",
            "publicReleaseCreated",
            "privateArtifactContentPublished",
            "copiedExecutablePublished",
            "publicHostOrMatchmakingEndpointPublished",
            "secretsSerialized",
            "newBeaLaunchCount",
            "processStartCount",
            "cdbAttachCount",
            "listenerOpenCount",
            "invitationCreateCount",
            "hostJoinControlsEnabledCount",
            "nPlayerOriginalBinaryRuntimeProof",
            "beaLaunchCount"
        };

        private static readonly Regex s_privateIpv4Pattern = new(@"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b", RegexOptions.CultureInvariant);
        private static readonly Regex s_hex64Pattern = new("^[0-9a-f]{64}$", RegexOptions.CultureInvariant);
        private static readonly Regex s_publicSafeTopologyTokenPattern = new("^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$", RegexOptions.CultureInvariant);

        private static readonly string[] s_nextProofIds =
        {
            "distinct-private-host-command-source-proof",
            "host-runtime-delivery-from-source-bound-distinct-command-source",
            "host-join-enablement-composite-proof",
        };

        public static OnlineMultiplayerReadinessSummary GetCurrentSummary()
        {
            return GetCurrentSummary(secondHostReadinessArtifact: null, localGamepadReadinessArtifact: null, dualSafeCopyTopologyArtifact: null);
        }

        public static OnlineMultiplayerReadinessSummary GetCurrentSummary(OnlineSecondHostReadinessArtifactSummary? secondHostReadinessArtifact)
        {
            return GetCurrentSummary(secondHostReadinessArtifact, localGamepadReadinessArtifact: null, dualSafeCopyTopologyArtifact: null);
        }

        public static OnlineMultiplayerReadinessSummary GetCurrentSummary(
            OnlineSecondHostReadinessArtifactSummary? secondHostReadinessArtifact,
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact)
        {
            return GetCurrentSummary(secondHostReadinessArtifact, localGamepadReadinessArtifact, dualSafeCopyTopologyArtifact: null);
        }

        public static OnlineMultiplayerReadinessSummary GetCurrentSummary(
            OnlineSecondHostReadinessArtifactSummary? secondHostReadinessArtifact,
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact,
            OnlineDualSafeCopyTopologyArtifactSummary? dualSafeCopyTopologyArtifact)
        {
            IReadOnlyList<OnlineMultiplayerStatusRow> statusRows = BuildStatusRows(localGamepadReadinessArtifact, dualSafeCopyTopologyArtifact);
            IReadOnlyList<OnlineMultiplayerProofGateRow> proofGateRows = BuildProofGateRows(localGamepadReadinessArtifact);
            IReadOnlyList<OnlineMultiplayerProofLadderRow> proofLadderRows = BuildProofLadderRows(localGamepadReadinessArtifact, dualSafeCopyTopologyArtifact);
            IReadOnlyList<string> nonClaims = BuildNonClaims();

            return new OnlineMultiplayerReadinessSummary(
                SchemaVersion: "original-binary-online-readiness-summary.v1",
                BaseOnlineMultiplayerReady: false,
                MultiHostLanProof: false,
                PublicMatchmakingProof: false,
                NativeBeaNetcodeProof: false,
                ActiveP3P4OriginalBinaryGameplayProof: false,
                PhysicalGamepadRuntimeProof: false,
                AcceptedOriginalBinaryGameplaySlots: new[] { "P1", "P2" },
                MetadataOnlySlots: new[] { "P3", "P4" },
                SecondHostSetupSteps: new[]
                {
                    new OnlineMultiplayerSetupStep(
                        "Prepare safe copy",
                        "Required",
                        "Create a safe game copy first. Online-adjacent tests must still run against copied files only."),
                    new OnlineMultiplayerSetupStep(
                        "Use a real endpoint",
                        "No accepted endpoint proof",
                        "A distinct VM or second PC on a private LAN must run the client preflight. Same-workstation processes and WSL-on-host do not count."),
                    new OnlineMultiplayerSetupStep(
                        "Accept a signed P2 command",
                        "Pending",
                        "The live command-source checker must accept one session-scoped P2 command and reject unsupported gameplay routes."),
                    new OnlineMultiplayerSetupStep(
                        "Bind it to copied runtime",
                        "Pending",
                        "The accepted command must drive copied BEA in the same run with exact-PID CDB evidence, mapped P2 sequence, and host-helper receipt."),
                    new OnlineMultiplayerSetupStep(
                        "Keep P3/P4 out of gameplay",
                        "Boundary",
                        "P3/P4 remain session metadata until a separate original-binary runtime proof class exists.")
                },
                SecondHostLiveAttemptReadiness: BuildSecondHostLiveAttemptReadiness(secondHostReadinessArtifact),
                StatusRows: statusRows,
                TryableActions: new[]
                {
                    new OnlineMultiplayerTryableAction(
                        "Local multiplayer probe",
                        "-skipfmv -level 850",
                        "Launches the safe copied game into the current P1/P2 split-screen probe path.")
                },
                BlockedActions: new[]
                {
                    new OnlineMultiplayerBlockedAction("Online hosting unavailable", false, "Requires accepted live distinct command-source proof plus source-bound runtime causality with exact-PID CDB evidence, accepted payload hash binding, mapped P2 sequence, host-helper receipt, and invitation lifecycle hash."),
                    new OnlineMultiplayerBlockedAction("Online joining unavailable", false, "Requires accepted live distinct command-source proof plus source-bound runtime causality with exact-PID CDB evidence, accepted payload hash binding, mapped P2 sequence, host-helper receipt, and invitation lifecycle hash."),
                    new OnlineMultiplayerBlockedAction("Public matchmaking", false, "Requires public server, identity, abuse, and release policy work."),
                    new OnlineMultiplayerBlockedAction("Native BEA netcode", false, "No native BEA networking path is proven.")
                },
                ProofGateRows: proofGateRows,
                ProofLadderRows: proofLadderRows,
                DualSafeCopyTopologyArtifact: dualSafeCopyTopologyArtifact,
                CompanionNetplayTarget: new OnlineCompanionNetplayTarget(
                    "Future design sketch: the host starts a safe copied game session, and the second player joins from a separate safe copy instead of split-screen. Host/Join is unavailable until the proof gates pass.",
                    "Host PC remains authoritative for the original-binary P1/P2 route until a deeper sync model is proven.",
                    "Join client sends signed P2 commands through the companion path; it must not inject input directly into the host game.",
                    "Current proof uses local split-screen as the P1/P2 routing study surface; the player-facing target is separate rendered sessions.",
                    "WinUI or packaged helper is expected to stay running for session identity, command relay, cleanup, and proof/safety checks.",
                    "No Host/Join controls until accepted live distinct endpoint command-source proof and source-bound copied-runtime causality both exist."),
                NonClaims: nonClaims,
                NextProofNeeded: "Real VM or physical second-host live command-source proof, then source-bound runtime causality with direct exact-PID CDB evidence, mapped P2 sequence and host-helper receipt binding before Host/Join can be enabled.",
                FallbackWithoutSecondHost: "WinUI host/join readiness surface plus same-host harness tightening while Host/Join gameplay controls remain disabled.");
        }

        private static IReadOnlyList<OnlineMultiplayerStatusRow> BuildStatusRows(
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact,
            OnlineDualSafeCopyTopologyArtifactSummary? dualSafeCopyTopologyArtifact)
        {
            var rows = new List<OnlineMultiplayerStatusRow>
            {
                new("Netplay readiness", "Not player-ready"),
                new("Current original-binary gameplay slots", "P1/P2 only"),
                new("P3/P4 status", "Session metadata only"),
                new("Current proof class", "Same-host/same-workstation only"),
                new("Host/Join promotion lock", "Online play is not available in this release; readiness artifacts cannot enable Host/Join."),
                new("Next proof dependency", "Real VM/physical second-host live command-source proof, then source-bound runtime causality")
            };

            rows.Add(localGamepadReadinessArtifact is null
                ? new OnlineMultiplayerStatusRow("Physical gamepad readiness", "No local physical controller readiness artifact loaded")
                : new OnlineMultiplayerStatusRow(
                    "Physical gamepad readiness",
                    $"{localGamepadReadinessArtifact.Status}; present candidates={localGamepadReadinessArtifact.PresentGamepadCandidateCount}; " +
                    $"registry candidates={localGamepadReadinessArtifact.RegistryGamepadCandidateCount}; pnp devices={localGamepadReadinessArtifact.PnpDeviceCount}; " +
                    $"joystick registry rows={localGamepadReadinessArtifact.JoystickRegistryRowCount}"));

            rows.Add(dualSafeCopyTopologyArtifact is null
                ? new OnlineMultiplayerStatusRow("Dual safe-copy topology", "No descriptor-only topology contract loaded")
                : new OnlineMultiplayerStatusRow(
                    "Dual safe-copy topology",
                    $"Descriptor-only contract loaded: safeCopyCount={dualSafeCopyTopologyArtifact.SafeCopyCount}; roles={string.Join(",", dualSafeCopyTopologyArtifact.Roles)}; sameWorkstationOnly={FormatBoolLower(dualSafeCopyTopologyArtifact.SameWorkstationOnly)}; samePhysicalMachineOnly={FormatBoolLower(dualSafeCopyTopologyArtifact.SamePhysicalMachineOnly)}; Host/Join remains locked"));

            return rows;
        }

        private static IReadOnlyList<OnlineMultiplayerProofGateRow> BuildProofGateRows(
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact)
        {
            string physicalGamepadGate = localGamepadReadinessArtifact switch
            {
                null => "Not accepted. Load a local physical controller readiness artifact before any physical-controller runtime attempt.",
                { ReadyForPhysicalGamepadRuntimeAttempt: true } => "Not accepted. ready_for_physical_gamepad_runtime_attempt is hardware preflight only; no BEA DirectInput/runtime proof, virtual-controller routing proof, visible movement proof, Host/Join, or online proof.",
                _ => $"Not accepted. {localGamepadReadinessArtifact.Status}; hardware preflight only; no BEA DirectInput/runtime proof."
            };

            return new[]
            {
                new OnlineMultiplayerProofGateRow("Host/Join promotion", "Locked. Readiness artifacts, run-kit artifacts, and local controller readiness can never promote Host/Join without accepted distinct-endpoint command-source proof plus source-bound copied-runtime causality proof."),
                new OnlineMultiplayerProofGateRow("Live command source", "Not accepted. A real VM or physical second-host private-LAN run must pass the live command-source checker before Host/Join can move."),
                new OnlineMultiplayerProofGateRow("Current hardening", "Command-source JSONL is capped at 4096 bytes; live physical proof rejects operator-supplied runtime-host-kind for host and client identity evidence."),
                new OnlineMultiplayerProofGateRow("Runtime causality", "Not accepted. The accepted payload hash and invitation lifecycle hash must bind through scheduler, bridge, runtime input-window, exact-PID CDB, mapped P2 sequence, and host-helper receipt in one same-run chain."),
                new OnlineMultiplayerProofGateRow("Physical gamepad routing", physicalGamepadGate),
                new OnlineMultiplayerProofGateRow("Fallback without second host", "Keep WinUI host/join readiness visible and same-host harnesses strict while gameplay Host/Join controls remain disabled.")
            };
        }

        private static IReadOnlyList<OnlineMultiplayerProofLadderRow> BuildProofLadderRows(
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact,
            OnlineDualSafeCopyTopologyArtifactSummary? dualSafeCopyTopologyArtifact)
        {
            string gamepadStatus = localGamepadReadinessArtifact is null
                ? "blocked"
                : "hardware-preflight-only";
            string gamepadDetail = DescribePhysicalGamepadLadderDetail(localGamepadReadinessArtifact);

            var rows = new List<OnlineMultiplayerProofLadderRow>
            {
                new OnlineMultiplayerProofLadderRow(
                    "P1/P2 local split-screen study surface",
                    "accepted-local-only",
                    "Same-host copied-runtime evidence supports P1/P2 local split-screen study, not online play."),
                new OnlineMultiplayerProofLadderRow(
                    "Same-workstation command relay chain",
                    "accepted-local-only",
                    "Loopback/process-separated/WSL and host-authority executor proofs are provenance rungs only; they are not second-host LAN proof."),
            };

            if (dualSafeCopyTopologyArtifact is not null)
            {
                rows.Add(new OnlineMultiplayerProofLadderRow(
                    "Dual safe-copy topology contract",
                    "accepted-contract-only",
                    $"Two app-owned safe-copy descriptors are mapped for the same workstation only: safeCopyCount={dualSafeCopyTopologyArtifact.SafeCopyCount}; roles={string.Join(",", dualSafeCopyTopologyArtifact.Roles)}; not online play; no BEA launch, listener, invitation, input, Host/Join, distinct endpoint, or runtime causality proof."));
            }

            rows.AddRange(new[]
            {
                new OnlineMultiplayerProofLadderRow(
                    "Physical gamepad input route",
                    gamepadStatus,
                    gamepadDetail),
                new OnlineMultiplayerProofLadderRow(
                    "Distinct endpoint command source",
                    "missing",
                    "A real VM or second PC must produce an accepted signed P2 command-source bundle."),
                new OnlineMultiplayerProofLadderRow(
                    "Source-bound copied-runtime causality",
                    "missing",
                    "Future proof must show a real accepted command driving copied BEA in the same run, with payload and invitation hashes carried through scheduler, bridge, runtime input, exact-PID CDB, mapped P2 sequence, and host-helper receipt."),
                new OnlineMultiplayerProofLadderRow(
                    "Host/Join player workflow",
                    "locked",
                    "Host/Join controls remain unavailable until distinct command-source and source-bound runtime causality proofs both pass.")
            });

            return rows;
        }

        private static string DescribePhysicalGamepadLadderDetail(
            OnlineLocalGamepadReadinessArtifactSummary? localGamepadReadinessArtifact)
        {
            if (localGamepadReadinessArtifact is null)
            {
                return "No local physical controller readiness artifact is loaded.";
            }

            string preflightSummary = localGamepadReadinessArtifact.ReadyForPhysicalGamepadRuntimeAttempt
                ? "Local hardware preflight found a controller candidate"
                : "Local hardware preflight has no present controller candidate";
            return $"{preflightSummary}; DirectInput/runtime routing still needs exact-PID BEA observation and a no-keyboard negative control.";
        }

        private static IReadOnlyList<string> BuildNonClaims()
        {
            return new[]
            {
                "No player-ready online multiplayer.",
                "No second-host LAN gameplay.",
                "No public matchmaking.",
                "No native BEA netcode.",
                "No deterministic sync, rollback, or anti-cheat.",
                "No active P3/P4 original-binary gameplay.",
                "No physical gamepad runtime proof.",
                "No Host/Join promotion from readiness artifacts.",
                "No proof-ladder row enables Host/Join or accepts online multiplayer proof.",
                "No dual-safe-copy topology contract enables Host/Join or accepts online multiplayer proof."
            };
        }

        public static bool TryLoadSecondHostReadinessArtifact(
            string? path,
            out OnlineSecondHostReadinessArtifactSummary? summary,
            out string? error)
        {
            summary = null;
            error = null;
            if (string.IsNullOrWhiteSpace(path))
            {
                error = "Choose a second-host readiness or run-kit JSON artifact.";
                return false;
            }

            if (!File.Exists(path))
            {
                error = "Second-host readiness artifact was not found.";
                return false;
            }

            try
            {
                FileInfo info = new(path);
                if (info.Length > MaxSecondHostReadinessArtifactBytes)
                {
                    error = "Second-host readiness artifact is too large.";
                    return false;
                }

                return TryParseSecondHostReadinessArtifactJson(File.ReadAllText(path), out summary, out error);
            }
            catch (IOException)
            {
                error = "Second-host readiness artifact could not be read.";
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                error = "Second-host readiness artifact could not be accessed.";
                return false;
            }
        }

        public static bool TryParseSecondHostReadinessArtifactJson(
            string json,
            out OnlineSecondHostReadinessArtifactSummary? summary,
            out string? error)
        {
            summary = null;
            error = null;
            if (json.Length > MaxSecondHostReadinessArtifactBytes)
            {
                error = "Second-host readiness artifact is too large.";
                return false;
            }

            try
            {
                using JsonDocument document = JsonDocument.Parse(json);
                JsonElement root = document.RootElement;
                if (root.ValueKind != JsonValueKind.Object)
                {
                    error = "Second-host readiness artifact must be a JSON object.";
                    return false;
                }

                string schema = GetString(root, "schemaVersion");
                if (!string.Equals(schema, SecondHostLiveReadinessSchema, StringComparison.Ordinal) &&
                    !string.Equals(schema, SecondHostLiveRunKitSchema, StringComparison.Ordinal))
                {
                    error = "Unsupported second-host readiness artifact schema.";
                    return false;
                }

                if (ContainsProofOverclaim(root, out string overclaim))
                {
                    error = $"Second-host readiness artifact is not a readiness artifact: {overclaim}.";
                    return false;
                }

                if (!HasAllowedStatus(schema, GetString(root, "status")))
                {
                    error = "Second-host readiness artifact has an unsupported status.";
                    return false;
                }

                if (ContainsSensitiveString(root, "$", out string sensitivePath))
                {
                    error = $"Second-host readiness artifact contains private or sensitive string data at {sensitivePath}.";
                    return false;
                }

                summary = string.Equals(schema, SecondHostLiveRunKitSchema, StringComparison.Ordinal)
                    ? ParseLiveRunKitArtifact(root)
                    : ParseLiveReadinessArtifact(root);
                return true;
            }
            catch (JsonException)
            {
                error = "Second-host readiness artifact is not valid JSON.";
                return false;
            }
            catch (InvalidOperationException ex)
            {
                error = ex.Message;
                return false;
            }
        }

        public static bool TryLoadLocalGamepadReadinessArtifact(
            string? path,
            out OnlineLocalGamepadReadinessArtifactSummary? summary,
            out string? error)
        {
            summary = null;
            error = null;
            if (string.IsNullOrWhiteSpace(path))
            {
                error = "Choose a local physical controller readiness JSON artifact.";
                return false;
            }

            if (!File.Exists(path))
            {
                error = "Local physical controller readiness artifact was not found.";
                return false;
            }

            try
            {
                FileInfo info = new(path);
                if (info.Length > MaxLocalGamepadReadinessArtifactBytes)
                {
                    error = "Local physical controller readiness artifact is too large.";
                    return false;
                }

                return TryParseLocalGamepadReadinessArtifactJson(File.ReadAllText(path), out summary, out error);
            }
            catch (IOException)
            {
                error = "Local physical controller readiness artifact could not be read.";
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                error = "Local physical controller readiness artifact could not be accessed.";
                return false;
            }
        }

        public static bool TryParseLocalGamepadReadinessArtifactJson(
            string json,
            out OnlineLocalGamepadReadinessArtifactSummary? summary,
            out string? error)
        {
            summary = null;
            error = null;
            if (json.Length > MaxLocalGamepadReadinessArtifactBytes)
            {
                error = "Local physical controller readiness artifact is too large.";
                return false;
            }

            try
            {
                using JsonDocument document = JsonDocument.Parse(json);
                JsonElement root = document.RootElement;
                if (root.ValueKind != JsonValueKind.Object)
                {
                    error = "Local physical controller readiness artifact must be a JSON object.";
                    return false;
                }

                if (!string.Equals(GetString(root, "schemaVersion"), LocalGamepadReadinessSchema, StringComparison.Ordinal))
                {
                    error = "Unsupported local physical controller readiness artifact schema.";
                    return false;
                }

                string status = GetString(root, "status");
                if (!string.Equals(status, "blocked_no_present_gamepad", StringComparison.Ordinal) &&
                    !string.Equals(status, "ready_for_physical_gamepad_runtime_attempt", StringComparison.Ordinal))
                {
                    error = "Local physical controller readiness artifact has an unsupported status.";
                    return false;
                }

                if (ContainsLocalGamepadOverclaim(root, out string overclaim))
                {
                    error = $"Local physical controller readiness artifact is not runtime proof: {overclaim}.";
                    return false;
                }

                if (ContainsSensitiveString(root, "$", out string sensitivePath))
                {
                    error = $"Local physical controller readiness artifact contains private or sensitive string data at {sensitivePath}.";
                    return false;
                }

                JsonElement presentCandidates = RequireArray(root, "presentGamepadCandidates", "Local physical controller readiness artifact");
                JsonElement registryCandidates = RequireArray(root, "registryGamepadCandidates", "Local physical controller readiness artifact");
                _ = RequireArray(root, "nextRuntimeProofRequires", "Local physical controller readiness artifact");
                if (string.IsNullOrWhiteSpace(GetString(root, "claimBoundary")))
                {
                    error = "Local physical controller readiness artifact is missing claimBoundary.";
                    return false;
                }

                int presentGamepadCandidateCount = GetBoundedCount(root, "presentGamepadCandidateCount", "Local physical controller readiness artifact");
                int registryGamepadCandidateCount = GetBoundedCount(root, "registryGamepadCandidateCount", "Local physical controller readiness artifact");
                int pnpDeviceCount = GetBoundedCount(root, "pnpDeviceCount", "Local physical controller readiness artifact");
                int joystickRegistryRowCount = GetBoundedCount(root, "joystickRegistryRowCount", "Local physical controller readiness artifact");
                bool readyForRuntimeAttempt = GetBool(root, "physicalGamepadRuntimeProofReady");

                if (presentCandidates.GetArrayLength() != presentGamepadCandidateCount ||
                    registryCandidates.GetArrayLength() != registryGamepadCandidateCount)
                {
                    error = "Local physical controller readiness artifact candidate counts do not match candidate arrays.";
                    return false;
                }

                if (string.Equals(status, "blocked_no_present_gamepad", StringComparison.Ordinal) && readyForRuntimeAttempt)
                {
                    error = "Local physical controller readiness artifact cannot be blocked and ready for runtime attempt.";
                    return false;
                }

                if (string.Equals(status, "ready_for_physical_gamepad_runtime_attempt", StringComparison.Ordinal) &&
                    (!readyForRuntimeAttempt || presentGamepadCandidateCount <= 0))
                {
                    error = "Local physical controller readiness artifact cannot be ready without present hardware candidates.";
                    return false;
                }

                summary = new OnlineLocalGamepadReadinessArtifactSummary(
                    SchemaVersion: LocalGamepadReadinessSchema,
                    Status: status,
                    SourceKind: "local physical gamepad readiness preflight",
                    ReadyForPhysicalGamepadRuntimeAttempt: readyForRuntimeAttempt,
                    PresentGamepadCandidateCount: presentGamepadCandidateCount,
                    RegistryGamepadCandidateCount: registryGamepadCandidateCount,
                    PnpDeviceCount: pnpDeviceCount,
                    JoystickRegistryRowCount: joystickRegistryRowCount);
                return true;
            }
            catch (JsonException)
            {
                error = "Local physical controller readiness artifact is not valid JSON.";
                return false;
            }
            catch (InvalidOperationException ex)
            {
                error = ex.Message;
                return false;
            }
        }

        public static bool TryLoadDualSafeCopyTopologyArtifact(
            string? path,
            out OnlineDualSafeCopyTopologyArtifactSummary? summary,
            out string? error)
        {
            summary = null;
            error = null;
            if (string.IsNullOrWhiteSpace(path))
            {
                error = "Choose a dual-safe-copy topology JSON artifact.";
                return false;
            }

            if (!File.Exists(path))
            {
                error = "Dual-safe-copy topology artifact was not found.";
                return false;
            }

            try
            {
                FileInfo info = new(path);
                if (info.Length > MaxDualSafeCopyTopologyArtifactBytes)
                {
                    error = "Dual-safe-copy topology artifact is too large.";
                    return false;
                }

                return TryParseDualSafeCopyTopologyArtifactJson(File.ReadAllText(path), out summary, out error);
            }
            catch (IOException)
            {
                error = "Dual-safe-copy topology artifact could not be read.";
                return false;
            }
            catch (UnauthorizedAccessException)
            {
                error = "Dual-safe-copy topology artifact could not be accessed.";
                return false;
            }
        }

        public static bool TryParseDualSafeCopyTopologyArtifactJson(
            string json,
            out OnlineDualSafeCopyTopologyArtifactSummary? summary,
            out string? error)
        {
            summary = null;
            error = null;
            if (json.Length > MaxDualSafeCopyTopologyArtifactBytes)
            {
                error = "Dual-safe-copy topology artifact is too large.";
                return false;
            }

            try
            {
                using JsonDocument document = JsonDocument.Parse(json);
                JsonElement root = document.RootElement;
                if (root.ValueKind != JsonValueKind.Object)
                {
                    error = "Dual-safe-copy topology artifact must be a JSON object.";
                    return false;
                }

                ValidateObjectProperties(
                    root,
                    "Dual-safe-copy topology artifact root",
                    "schemaVersion",
                    "status",
                    "date",
                    "scope",
                    "topology",
                    "safeCopies",
                    "topologyCounters",
                    "proofBoundary",
                    "sideEffects",
                    "requiredFutureEvidence",
                    "nonClaims",
                    "releaseBoundary");

                if (!string.Equals(GetString(root, "schemaVersion"), DualSafeCopyTopologySchema, StringComparison.Ordinal))
                {
                    error = "Unsupported dual-safe-copy topology artifact schema.";
                    return false;
                }

                if (!string.Equals(GetString(root, "scope"), DualSafeCopyTopologyScope, StringComparison.Ordinal) ||
                    !string.Equals(GetString(root, "status"), DualSafeCopyTopologyStatus, StringComparison.Ordinal))
                {
                    error = "Dual-safe-copy topology artifact has an unsupported scope or status.";
                    return false;
                }

                if (!string.Equals(GetString(root, "date"), "2026-06-22", StringComparison.Ordinal))
                {
                    error = "Dual-safe-copy topology artifact has an unsupported date.";
                    return false;
                }

                if (ContainsSensitiveString(root, "$", out string sensitivePath))
                {
                    error = $"Dual-safe-copy topology artifact contains private or sensitive string data at {sensitivePath}.";
                    return false;
                }

                if (ContainsTruthyNamedValue(root, "$", s_dualSafeCopyTopologyOverclaimKeys, out string overclaim))
                {
                    error = $"Dual-safe-copy topology artifact is descriptor-only, not runtime proof: {overclaim}.";
                    return false;
                }

                JsonElement topology = RequireObject(root, "topology", "Dual-safe-copy topology artifact");
                ValidateObjectProperties(
                    topology,
                    "Dual-safe-copy topology artifact topology",
                    "topologyKind",
                    "topologyProofClass",
                    "safeCopyCount",
                    "sameWorkstationOnly",
                    "samePhysicalMachineOnly",
                    "separateGameViewsProven",
                    "distinctEndpointProof",
                    "playerReadyOnlineProof");
                RequireStringEquals(topology, "topologyKind", "same-workstation-two-app-owned-safe-copies", "Dual-safe-copy topology artifact");
                RequireStringEquals(topology, "topologyProofClass", "topology-contract-not-runtime-proof", "Dual-safe-copy topology artifact");
                RequireIntEquals(topology, "safeCopyCount", 2, "Dual-safe-copy topology artifact");
                RequireBoolEquals(topology, "sameWorkstationOnly", true, "Dual-safe-copy topology artifact");
                RequireBoolEquals(topology, "samePhysicalMachineOnly", true, "Dual-safe-copy topology artifact");
                RequireBoolEquals(topology, "separateGameViewsProven", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(topology, "distinctEndpointProof", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(topology, "playerReadyOnlineProof", false, "Dual-safe-copy topology artifact");

                IReadOnlyList<string> roles = ValidateDualSafeCopyRows(root);

                JsonElement counters = RequireObject(root, "topologyCounters", "Dual-safe-copy topology artifact");
                ValidateObjectProperties(
                    counters,
                    "Dual-safe-copy topology artifact topologyCounters",
                    "safeCopyRootDescriptorCount",
                    "safeCopyExecutableDescriptorCount",
                    "distinctSafeCopyRootPairCount",
                    "sessionRoleDescriptorCount",
                    "newBeaLaunchCount",
                    "processStartCount",
                    "cdbAttachCount",
                    "listenerOpenCount",
                    "invitationCreateCount",
                    "hostJoinControlsEnabledCount",
                    "nPlayerOriginalBinaryRuntimeProof");
                int safeCopyRootDescriptorCount = RequireIntEquals(counters, "safeCopyRootDescriptorCount", 2, "Dual-safe-copy topology artifact");
                int safeCopyExecutableDescriptorCount = RequireIntEquals(counters, "safeCopyExecutableDescriptorCount", 2, "Dual-safe-copy topology artifact");
                int distinctSafeCopyRootPairCount = RequireIntEquals(counters, "distinctSafeCopyRootPairCount", 1, "Dual-safe-copy topology artifact");
                _ = RequireIntEquals(counters, "sessionRoleDescriptorCount", 2, "Dual-safe-copy topology artifact");
                int newBeaLaunchCount = RequireIntEquals(counters, "newBeaLaunchCount", 0, "Dual-safe-copy topology artifact");
                int processStartCount = RequireIntEquals(counters, "processStartCount", 0, "Dual-safe-copy topology artifact");
                int cdbAttachCount = RequireIntEquals(counters, "cdbAttachCount", 0, "Dual-safe-copy topology artifact");
                int listenerOpenCount = RequireIntEquals(counters, "listenerOpenCount", 0, "Dual-safe-copy topology artifact");
                int invitationCreateCount = RequireIntEquals(counters, "invitationCreateCount", 0, "Dual-safe-copy topology artifact");
                int hostJoinControlsEnabledCount = RequireIntEquals(counters, "hostJoinControlsEnabledCount", 0, "Dual-safe-copy topology artifact");
                _ = RequireIntEquals(counters, "nPlayerOriginalBinaryRuntimeProof", 0, "Dual-safe-copy topology artifact");

                ValidateDualSafeCopyProofBoundary(root);
                ValidateDualSafeCopySideEffects(root);
                IReadOnlyList<string> futureEvidenceIds = ValidateDualSafeCopyFutureEvidence(root);
                ValidateFalseObject(root, "nonClaims", "Dual-safe-copy topology artifact");
                ValidateDualSafeCopyReleaseBoundary(root);

                summary = new OnlineDualSafeCopyTopologyArtifactSummary(
                    SchemaVersion: DualSafeCopyTopologySchema,
                    Status: DualSafeCopyTopologyStatus,
                    Scope: DualSafeCopyTopologyScope,
                    SourceKind: "dual-safe-copy same-workstation topology contract",
                    SafeCopyCount: 2,
                    Roles: roles,
                    SameWorkstationOnly: true,
                    SamePhysicalMachineOnly: true,
                    SafeCopyRootDescriptorCount: safeCopyRootDescriptorCount,
                    SafeCopyExecutableDescriptorCount: safeCopyExecutableDescriptorCount,
                    DistinctSafeCopyRootPairCount: distinctSafeCopyRootPairCount,
                    BeaLaunchCount: newBeaLaunchCount,
                    ProcessStartCount: processStartCount,
                    CdbAttachCount: cdbAttachCount,
                    ListenerOpenCount: listenerOpenCount,
                    InvitationCreateCount: invitationCreateCount,
                    HostJoinControlsEnabledCount: hostJoinControlsEnabledCount,
                    RequiredFutureEvidenceIds: futureEvidenceIds,
                    ClaimBoundary: "Descriptor-only same-workstation topology contract: no BEA launch, no process start, no CDB attach, no listener, no invitation, no input, no Host/Join, no distinct endpoint proof, no source-bound runtime causality, and no player-ready netplay.");
                return true;
            }
            catch (JsonException)
            {
                error = "Dual-safe-copy topology artifact is not valid JSON.";
                return false;
            }
            catch (InvalidOperationException ex)
            {
                error = ex.Message;
                return false;
            }
        }

        private static OnlineSecondHostLiveAttemptReadiness BuildSecondHostLiveAttemptReadiness(
            OnlineSecondHostReadinessArtifactSummary? artifact)
        {
            bool hasArtifact = artifact is not null;
            bool readyToAttempt = artifact?.ReadyToAttemptHarness ?? false;
            bool readyForLiveValidation = artifact?.ReadyForLiveValidationCandidate ?? false;
            bool readyToRun = artifact?.ReadyToRunLiveCommandSource ?? false;
            bool serverInputsComplete = artifact?.ServerCommandInputsComplete ?? false;
            bool clientPreflightProvided = artifact?.ClientPreflightProvided ?? false;
            int candidatePrivateBindAddressCount = artifact?.CandidatePrivateBindAddressCount ?? 1;
            int wslOnHostInterfaceCount = artifact?.WslOnHostInterfaceCount ?? 1;

            var requiredInputs = new[]
            {
                new OnlineMultiplayerSetupStep(
                    "Readiness artifact",
                    hasArtifact ? "Loaded" : "Not loaded",
                    hasArtifact
                        ? $"Loaded {artifact!.SourceKind} artifact with status {artifact.Status}; private paths are not displayed."
                        : "No redacted second-host readiness/run-kit artifact has been loaded into this app session."),
                new OnlineMultiplayerSetupStep(
                    "Host bind candidate",
                    candidatePrivateBindAddressCount > 0 ? "Recorded" : "Missing",
                    "A private non-WSL bind candidate is required, but that alone is not a live command-source proof."),
                new OnlineMultiplayerSetupStep(
                    "Client preflight",
                    clientPreflightProvided ? "Provided" : "Missing",
                    "Run the second-host client identity/source-safety preflight on a real VM or second PC before any live attempt."),
                new OnlineMultiplayerSetupStep(
                    "Server command inputs",
                    serverInputsComplete ? "Complete" : "Incomplete",
                    "The live server needs explicit bind host, copied/source roots, invitation path, and accepted private proof inputs."),
                new OnlineMultiplayerSetupStep(
                    "Live validation candidate",
                    readyForLiveValidation ? "Ready" : "Blocked",
                    "Do not run or promote Host/Join until the live run kit reports ready and the private candidate gates accept the resulting artifacts.")
            };

            var blockingReasons = new List<string>();
            if (!hasArtifact)
            {
                blockingReasons.Add("No redacted second-host readiness/run-kit artifact is loaded.");
            }

            if (!clientPreflightProvided)
            {
                blockingReasons.Add("Missing client identity/source-safety preflight from a real VM or second PC.");
            }

            if (!serverInputsComplete)
            {
                blockingReasons.Add("Server command inputs are incomplete for a live command-source run.");
            }

            if (!readyToRun)
            {
                blockingReasons.Add("No accepted live second-host command-source proof exists.");
            }

            blockingReasons.Add("No source-bound copied-runtime causality proof exists.");

            return new OnlineSecondHostLiveAttemptReadiness(
                SchemaVersion: "winui-original-binary-second-host-live-attempt-readiness.v1",
                ReadyToAttemptHarness: readyToAttempt,
                ReadyForLiveValidationCandidate: readyForLiveValidation,
                ReadyToRunLiveCommandSource: readyToRun,
                ServerCommandInputsComplete: serverInputsComplete,
                ClientPreflightProvided: clientPreflightProvided,
                CandidatePrivateBindAddressCount: candidatePrivateBindAddressCount,
                WslOnHostInterfaceCount: wslOnHostInterfaceCount,
                HostJoinControlsMayBeEnabled: false,
                AcceptedLiveSecondHostCommandSourceProof: false,
                BaseOnlineMultiplayerReady: false,
                RequiredInputs: requiredInputs,
                BlockingReasons: blockingReasons,
                SafeCommands: new[]
                {
                    "npm run test:winui-original-binary-second-host-live-readiness",
                    "npm run test:winui-original-binary-second-host-live-run-kit",
                    "npm run test:winui-original-binary-second-host-command-source",
                    "npm run test:winui-original-binary-host-join-enablement"
                });
        }

        private static OnlineSecondHostReadinessArtifactSummary ParseLiveReadinessArtifact(JsonElement root)
        {
            JsonElement host = RequireObject(root, "hostInterfacePreflight");
            JsonElement requested = RequireObject(root, "requestedRunInputs");
            _ = RequireObject(root, "proofBooleans");
            int candidatePrivateBindAddressCount = GetBoundedCount(host, "candidatePrivateBindAddressCount");
            int wslOnHostInterfaceCount = GetBoundedCount(host, "wslOnHostInterfaceCount");
            return new OnlineSecondHostReadinessArtifactSummary(
                SchemaVersion: SecondHostLiveReadinessSchema,
                Status: GetString(root, "status"),
                SourceKind: "host live-readiness preflight",
                ReadyToAttemptHarness: false,
                ReadyForLiveValidationCandidate: false,
                ReadyToRunLiveCommandSource: false,
                ServerCommandInputsComplete: GetBool(requested, "serverCommandInputsComplete"),
                ClientPreflightProvided: false,
                CandidatePrivateBindAddressCount: candidatePrivateBindAddressCount,
                WslOnHostInterfaceCount: wslOnHostInterfaceCount);
        }

        private static OnlineSecondHostReadinessArtifactSummary ParseLiveRunKitArtifact(JsonElement root)
        {
            JsonElement host = RequireObject(root, "hostReadiness");
            JsonElement client = RequireObject(root, "clientPreflight");
            JsonElement privateInputs = root.TryGetProperty("privateRunInputs", out JsonElement inputs) && inputs.ValueKind == JsonValueKind.Object
                ? inputs
                : default;
            if (privateInputs.ValueKind == JsonValueKind.Object &&
                GetBool(privateInputs, "rawPrivatePathsSerializedInPublicDocs"))
            {
                throw new InvalidOperationException("Run-kit artifact reports raw private paths serialized in public docs.");
            }

            bool readyToAttemptHarness = GetBool(root, "readyToAttemptHarness");
            bool readyForLiveValidationCandidate = GetBool(root, "readyForLiveValidationCandidate");
            bool readyToRunLiveCommandSource = GetBool(root, "readyToRunLiveCommandSource");
            bool serverCommandInputsComplete = GetBool(host, "serverCommandInputsComplete");
            bool clientPreflightProvided = GetBool(client, "provided");
            if (readyToRunLiveCommandSource &&
                (!readyToAttemptHarness || !readyForLiveValidationCandidate || !serverCommandInputsComplete || !clientPreflightProvided))
            {
                throw new InvalidOperationException("Second-host run-kit artifact cannot be ready-to-run without host and client prerequisites.");
            }

            int candidatePrivateBindAddressCount = GetBoundedCount(host, "candidatePrivateBindAddressCount");
            int wslOnHostInterfaceCount = GetBoundedCount(host, "wslOnHostInterfaceCount");
            return new OnlineSecondHostReadinessArtifactSummary(
                SchemaVersion: SecondHostLiveRunKitSchema,
                Status: GetString(root, "status"),
                SourceKind: "second-host live run kit",
                ReadyToAttemptHarness: readyToAttemptHarness,
                ReadyForLiveValidationCandidate: readyForLiveValidationCandidate,
                ReadyToRunLiveCommandSource: readyToRunLiveCommandSource,
                ServerCommandInputsComplete: serverCommandInputsComplete,
                ClientPreflightProvided: clientPreflightProvided,
                CandidatePrivateBindAddressCount: candidatePrivateBindAddressCount,
                WslOnHostInterfaceCount: wslOnHostInterfaceCount);
        }

        private static IReadOnlyList<string> ValidateDualSafeCopyRows(JsonElement root)
        {
            JsonElement rows = RequireArray(root, "safeCopies", "Dual-safe-copy topology artifact");
            if (rows.GetArrayLength() != 2)
            {
                throw new InvalidOperationException("Dual-safe-copy topology artifact must contain exactly two safe-copy descriptor rows.");
            }

            string[] expectedRoles = { "host", "joiner" };
            var roles = new List<string>();
            var rootLabels = new HashSet<string>(StringComparer.Ordinal);
            var executableLabels = new HashSet<string>(StringComparer.Ordinal);
            int index = 0;
            foreach (JsonElement row in rows.EnumerateArray())
            {
                if (row.ValueKind != JsonValueKind.Object)
                {
                    throw new InvalidOperationException("Dual-safe-copy topology artifact safe-copy descriptor row must be an object.");
                }

                ValidateObjectProperties(
                    row,
                    "Dual-safe-copy topology artifact safeCopies[]",
                    "role",
                    "safeCopyRootLabel",
                    "rootPathPublished",
                    "absolutePathsSerialized",
                    "safeCopyRootPathFingerprint",
                    "safeCopyContentManifestSha256",
                    "copiedExecutableLabel",
                    "executableRelativePath",
                    "executableSha256",
                    "sourceRootLabel",
                    "appOwnedRootRequired",
                    "separateRootRequired",
                    "launchAllowedByThisRung",
                    "installedGameMutationAllowed",
                    "originalExecutableMutationAllowed",
                    "steamInstallWriteAllowed",
                    "runtimeRole");

                string role = RequirePublicSafeString(row, "role", "Dual-safe-copy topology artifact");
                if (!string.Equals(role, expectedRoles[index], StringComparison.Ordinal))
                {
                    throw new InvalidOperationException("Dual-safe-copy topology artifact safe-copy roles must be host then joiner.");
                }

                roles.Add(role);
                string rootLabel = RequirePublicSafeString(row, "safeCopyRootLabel", "Dual-safe-copy topology artifact");
                string executableLabel = RequirePublicSafeString(row, "copiedExecutableLabel", "Dual-safe-copy topology artifact");
                _ = RequirePublicSafeString(row, "sourceRootLabel", "Dual-safe-copy topology artifact");
                string rootFingerprint = RequirePublicSafeString(row, "safeCopyRootPathFingerprint", "Dual-safe-copy topology artifact");
                string manifestSha = RequirePublicSafeString(row, "safeCopyContentManifestSha256", "Dual-safe-copy topology artifact");
                string executableSha = RequirePublicSafeString(row, "executableSha256", "Dual-safe-copy topology artifact");
                _ = RequirePublicSafeString(row, "runtimeRole", "Dual-safe-copy topology artifact");

                if (!s_hex64Pattern.IsMatch(rootFingerprint))
                {
                    throw new InvalidOperationException($"Dual-safe-copy topology artifact has invalid hex64 fingerprint for {role} safeCopyRootPathFingerprint.");
                }

                if (!s_hex64Pattern.IsMatch(manifestSha))
                {
                    throw new InvalidOperationException($"Dual-safe-copy topology artifact has invalid hex64 hash for {role} safeCopyContentManifestSha256.");
                }

                if (!s_hex64Pattern.IsMatch(executableSha))
                {
                    throw new InvalidOperationException($"Dual-safe-copy topology artifact has invalid hex64 hash for {role} executableSha256.");
                }

                RequireStringEquals(row, "executableRelativePath", "BEA.exe", "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "appOwnedRootRequired", true, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "separateRootRequired", true, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "rootPathPublished", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "absolutePathsSerialized", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "launchAllowedByThisRung", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "installedGameMutationAllowed", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "originalExecutableMutationAllowed", false, "Dual-safe-copy topology artifact");
                RequireBoolEquals(row, "steamInstallWriteAllowed", false, "Dual-safe-copy topology artifact");

                if (!rootLabels.Add(rootLabel) || !executableLabels.Add(executableLabel))
                {
                    throw new InvalidOperationException("Dual-safe-copy topology artifact safe-copy descriptor labels must be distinct.");
                }

                index++;
            }

            if (!roles.SequenceEqual(expectedRoles, StringComparer.Ordinal))
            {
                throw new InvalidOperationException("Dual-safe-copy topology artifact safe-copy roles must be host then joiner.");
            }

            return roles;
        }

        private static void ValidateDualSafeCopyProofBoundary(JsonElement root)
        {
            JsonElement proof = RequireObject(root, "proofBoundary", "Dual-safe-copy topology artifact");
            ValidateObjectProperties(
                proof,
                "Dual-safe-copy topology artifact proofBoundary",
                "hostJoinControlsMayBeEnabled",
                "baseOnlineMultiplayerReady",
                "acceptedLiveSecondHostCommandSourceProof",
                "acceptedLiveSecondHostRuntimeDeliveryProof",
                "acceptedLiveSecondHostRuntimeCausalityProof",
                "secondHostProof",
                "multiHostLanPlayProof",
                "publicMatchmakingProof",
                "nativeBeaNetcodeProof",
                "activeP3P4OriginalBinaryGameplayProof",
                "moreThanTwoOriginalBinaryRuntimePlayersProof",
                "hostHelperInputSent",
                "gameInputSentByTopologyTool",
                "nPlayerOriginalBinaryRuntimeProof",
                "maxOriginalBinaryActiveSlotsProven",
                "acceptedOriginalBinaryGameplaySlots",
                "metadataOnlySlots");
            foreach (string key in new[]
            {
                "hostJoinControlsMayBeEnabled",
                "baseOnlineMultiplayerReady",
                "acceptedLiveSecondHostCommandSourceProof",
                "acceptedLiveSecondHostRuntimeDeliveryProof",
                "acceptedLiveSecondHostRuntimeCausalityProof",
                "secondHostProof",
                "multiHostLanPlayProof",
                "publicMatchmakingProof",
                "nativeBeaNetcodeProof",
                "activeP3P4OriginalBinaryGameplayProof",
                "moreThanTwoOriginalBinaryRuntimePlayersProof",
                "hostHelperInputSent",
                "gameInputSentByTopologyTool"
            })
            {
                RequireBoolEquals(proof, key, false, "Dual-safe-copy topology artifact");
            }

            RequireIntEquals(proof, "nPlayerOriginalBinaryRuntimeProof", 0, "Dual-safe-copy topology artifact");
            RequireIntEquals(proof, "maxOriginalBinaryActiveSlotsProven", 2, "Dual-safe-copy topology artifact");
            RequireStringArrayEquals(proof, "acceptedOriginalBinaryGameplaySlots", new[] { "P1", "P2" }, "Dual-safe-copy topology artifact");
            RequireStringArrayEquals(proof, "metadataOnlySlots", new[] { "P3", "P4" }, "Dual-safe-copy topology artifact");
        }

        private static void ValidateDualSafeCopySideEffects(JsonElement root)
        {
            JsonElement effects = RequireObject(root, "sideEffects", "Dual-safe-copy topology artifact");
            ValidateObjectProperties(
                effects,
                "Dual-safe-copy topology artifact sideEffects",
                "beaLaunchCount",
                "processStartCount",
                "cdbAttachCount",
                "listenerOpened",
                "invitationCreated",
                "inputSent",
                "patchBytesChanged",
                "publicReleaseCreated");
            RequireIntEquals(effects, "beaLaunchCount", 0, "Dual-safe-copy topology artifact");
            RequireIntEquals(effects, "processStartCount", 0, "Dual-safe-copy topology artifact");
            RequireIntEquals(effects, "cdbAttachCount", 0, "Dual-safe-copy topology artifact");
            foreach (string key in new[]
            {
                "listenerOpened",
                "invitationCreated",
                "inputSent",
                "patchBytesChanged",
                "publicReleaseCreated"
            })
            {
                RequireBoolEquals(effects, key, false, "Dual-safe-copy topology artifact");
            }
        }

        private static IReadOnlyList<string> ValidateDualSafeCopyFutureEvidence(JsonElement root)
        {
            JsonElement required = RequireArray(root, "requiredFutureEvidence", "Dual-safe-copy topology artifact");
            var expected = new (string Id, string[] MustProve)[]
            {
                ("distinct-endpoint-command-source-proof", new[]
                {
                    "distinctEndpointIdentity",
                    "privateNonLoopbackCommandSource",
                    "sessionScopedAuthentication",
                    "acceptedP2Command",
                    "noInstalledGameMutation"
                }),
                ("source-bound-copied-runtime-causality-proof", new[]
                {
                    "acceptedCommandPayloadHashBoundToRuntimeInput",
                    "invitationLifecycleHashBoundToRuntimeInput",
                    "exactPidCdbEvidence",
                    "copiedRuntimeArtifact",
                    "hostHelperDeliveryReceipt"
                }),
                ("host-join-enablement-composite-proof", new[]
                {
                    "distinct-endpoint-command-source-proof",
                    "source-bound-copied-runtime-causality-proof",
                    "fixtureAndPosthocArtifactsRejected"
                }),
                ("player-ready-host-join-release-proof", new[]
                {
                    "userFacingHostJoinFlow",
                    "releaseTestedCleanupAndRecovery",
                    "noPublicPrivateProofLeakage"
                })
            };

            if (required.GetArrayLength() != expected.Length)
            {
                throw new InvalidOperationException("Dual-safe-copy topology artifact future evidence list must match the exact known gate set.");
            }

            var ids = new List<string>();
            int index = 0;
            foreach (JsonElement row in required.EnumerateArray())
            {
                if (row.ValueKind != JsonValueKind.Object)
                {
                    throw new InvalidOperationException("Dual-safe-copy topology artifact future evidence row must be an object.");
                }

                ValidateObjectProperties(row, "Dual-safe-copy topology artifact requiredFutureEvidence[]", "id", "mustProve");
                string id = RequirePublicSafeString(row, "id", "Dual-safe-copy topology artifact");
                if (!string.Equals(id, expected[index].Id, StringComparison.Ordinal))
                {
                    throw new InvalidOperationException($"Dual-safe-copy topology artifact future evidence row {index} has unexpected id.");
                }

                JsonElement mustProve = RequireArray(row, "mustProve", "Dual-safe-copy topology artifact");
                if (mustProve.GetArrayLength() != expected[index].MustProve.Length)
                {
                    throw new InvalidOperationException($"Dual-safe-copy topology artifact future evidence row has unexpected mustProve count: {id}.");
                }

                int tokenIndex = 0;
                foreach (JsonElement token in mustProve.EnumerateArray())
                {
                    if (token.ValueKind != JsonValueKind.String ||
                        string.IsNullOrWhiteSpace(token.GetString()) ||
                        token.GetString() != token.GetString()!.Trim() ||
                        !s_publicSafeTopologyTokenPattern.IsMatch(token.GetString()!))
                    {
                        throw new InvalidOperationException($"Dual-safe-copy topology artifact has invalid future evidence token for {id}.");
                    }

                    if (!string.Equals(token.GetString(), expected[index].MustProve[tokenIndex], StringComparison.Ordinal))
                    {
                        throw new InvalidOperationException($"Dual-safe-copy topology artifact future evidence row has unexpected token for {id}.");
                    }

                    tokenIndex++;
                }

                ids.Add(id);
                index++;
            }

            return ids;
        }

        private static void ValidateFalseObject(JsonElement root, string propertyName, string artifactLabel)
        {
            JsonElement child = RequireObject(root, propertyName, artifactLabel);
            ValidateObjectProperties(
                child,
                $"{artifactLabel} {propertyName}",
                "separateScreenNetplayProof",
                "multiHostLanPlayProof",
                "publicMatchmakingProof",
                "nativeBeaNetcodeProof",
                "deterministicSyncProof",
                "rollbackProof",
                "antiCheatProof",
                "coOpVersusRuntimeProof",
                "activeP3P4OriginalBinaryGameplayProof",
                "rebuildParityProof",
                "noNoticeableDifferenceProof");
            foreach (JsonProperty property in child.EnumerateObject())
            {
                if (property.Value.ValueKind != JsonValueKind.False)
                {
                    throw new InvalidOperationException($"{artifactLabel} {propertyName}.{property.Name} must remain false.");
                }
            }
        }

        private static void ValidateDualSafeCopyReleaseBoundary(JsonElement root)
        {
            JsonElement release = RequireObject(root, "releaseBoundary", "Dual-safe-copy topology artifact");
            ValidateObjectProperties(
                release,
                "Dual-safe-copy topology artifact releaseBoundary",
                "privateProofReleaseExcludedByPolicy",
                "privateArtifactContentPublished",
                "copiedExecutablePublished",
                "publicHostOrMatchmakingEndpointPublished",
                "installedGameMutationAllowed",
                "secretsSerialized");
            RequireBoolEquals(release, "privateProofReleaseExcludedByPolicy", true, "Dual-safe-copy topology artifact");
            foreach (string key in new[]
            {
                "privateArtifactContentPublished",
                "copiedExecutablePublished",
                "publicHostOrMatchmakingEndpointPublished",
                "installedGameMutationAllowed",
                "secretsSerialized"
            })
            {
                RequireBoolEquals(release, key, false, "Dual-safe-copy topology artifact");
            }
        }

        private static bool ContainsProofOverclaim(JsonElement root, out string overclaim)
        {
            overclaim = string.Empty;
            if (!root.TryGetProperty("proofBooleans", out JsonElement proof) ||
                proof.ValueKind != JsonValueKind.Object)
            {
                overclaim = "missing proofBooleans";
                return true;
            }

            foreach (string key in s_proofOverclaimKeys)
            {
                if (!proof.TryGetProperty(key, out JsonElement value))
                {
                    overclaim = key;
                    return true;
                }

                if (value.ValueKind != JsonValueKind.False)
                {
                    overclaim = key;
                    return true;
                }
            }

            return ContainsTruthyProofOverclaim(root, "$", out overclaim);
        }

        private static bool ContainsLocalGamepadOverclaim(JsonElement root, out string overclaim)
        {
            if (ContainsTruthyNamedValue(root, "$", s_localGamepadRuntimeOverclaimKeys, out overclaim))
            {
                return true;
            }

            return ContainsTruthyNamedValue(root, "$", s_proofOverclaimKeys, out overclaim);
        }

        private static bool ContainsTruthyProofOverclaim(JsonElement element, string path, out string overclaim)
        {
            return ContainsTruthyNamedValue(element, path, s_proofOverclaimKeys, out overclaim);
        }

        private static bool ContainsTruthyNamedValue(
            JsonElement element,
            string path,
            IReadOnlyCollection<string> keyNames,
            out string overclaim)
        {
            overclaim = string.Empty;
            if (element.ValueKind == JsonValueKind.Object)
            {
                foreach (JsonProperty property in element.EnumerateObject())
                {
                    string propertyPath = $"{path}.{property.Name}";
                    if (keyNames.Contains(property.Name, StringComparer.Ordinal) &&
                        IsTruthyProofValue(property.Value))
                    {
                        overclaim = propertyPath;
                        return true;
                    }

                    if (ContainsTruthyNamedValue(property.Value, propertyPath, keyNames, out overclaim))
                    {
                        return true;
                    }
                }
            }
            else if (element.ValueKind == JsonValueKind.Array)
            {
                int index = 0;
                foreach (JsonElement child in element.EnumerateArray())
                {
                    if (ContainsTruthyNamedValue(child, $"{path}[{index}]", keyNames, out overclaim))
                    {
                        return true;
                    }

                    index++;
                }
            }

            return false;
        }

        private static bool IsTruthyProofValue(JsonElement value)
        {
            return value.ValueKind switch
            {
                JsonValueKind.True => true,
                JsonValueKind.Number => value.TryGetInt64(out long number) && number != 0,
                JsonValueKind.String => IsTruthyString(value.GetString()),
                _ => false,
            };
        }

        private static bool IsTruthyString(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return false;
            }

            string normalized = value.Trim();
            return string.Equals(normalized, "true", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(normalized, "yes", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(normalized, "enabled", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(normalized, "accepted", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(normalized, "ready", StringComparison.OrdinalIgnoreCase) ||
                   string.Equals(normalized, "1", StringComparison.Ordinal);
        }

        private static bool HasAllowedStatus(string schema, string status)
        {
            if (string.Equals(schema, SecondHostLiveReadinessSchema, StringComparison.Ordinal))
            {
                return string.Equals(status, "host-preflight-ready-for-external-client", StringComparison.Ordinal) ||
                       string.Equals(status, "host-preflight-needs-private-bind-address", StringComparison.Ordinal);
            }

            if (string.Equals(schema, SecondHostLiveRunKitSchema, StringComparison.Ordinal))
            {
                return string.Equals(status, "ready-to-run-live-command-source", StringComparison.Ordinal) ||
                       string.Equals(status, "ready-to-attempt-harness-only-not-live-ready", StringComparison.Ordinal);
            }

            return false;
        }

        private static bool ContainsSensitiveString(JsonElement element, string path, out string sensitivePath)
        {
            sensitivePath = string.Empty;
            if (element.ValueKind == JsonValueKind.String)
            {
                if (IsSensitiveString(element.GetString()))
                {
                    sensitivePath = path;
                    return true;
                }
            }
            else if (element.ValueKind == JsonValueKind.Object)
            {
                foreach (JsonProperty property in element.EnumerateObject())
                {
                    if (ContainsSensitiveString(property.Value, $"{path}.{property.Name}", out sensitivePath))
                    {
                        return true;
                    }
                }
            }
            else if (element.ValueKind == JsonValueKind.Array)
            {
                int index = 0;
                foreach (JsonElement child in element.EnumerateArray())
                {
                    if (ContainsSensitiveString(child, $"{path}[{index}]", out sensitivePath))
                    {
                        return true;
                    }

                    index++;
                }
            }

            return false;
        }

        private static bool IsSensitiveString(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return false;
            }

            string text = value.Trim();
            if (Regex.IsMatch(text, @"\b[A-Za-z]:\\", RegexOptions.CultureInvariant) ||
                text.StartsWith(@"\\", StringComparison.Ordinal) ||
                text.Contains(@"\Users\", StringComparison.OrdinalIgnoreCase) ||
                text.Contains("/Users/", StringComparison.OrdinalIgnoreCase) ||
                text.Contains("Program Files", StringComparison.OrdinalIgnoreCase) ||
                text.Contains("steamapps", StringComparison.OrdinalIgnoreCase) ||
                text.Contains("Onslaught-Career-Editor-" + "private", StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }

            if (s_privateIpv4Pattern.IsMatch(text))
            {
                return true;
            }

            return text.Contains("ghp_", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("github_pat_", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("-----BEGIN", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("PRIVATE KEY", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("Bearer ", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("api_key=", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("apikey=", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("token=", StringComparison.OrdinalIgnoreCase) ||
                   text.Contains("password=", StringComparison.OrdinalIgnoreCase);
        }

        private static JsonElement RequireObject(JsonElement parent, string propertyName)
        {
            return RequireObject(parent, propertyName, "Second-host readiness artifact");
        }

        private static JsonElement RequireObject(JsonElement parent, string propertyName, string artifactLabel)
        {
            if (parent.TryGetProperty(propertyName, out JsonElement child) &&
                child.ValueKind == JsonValueKind.Object)
            {
                return child;
            }

            throw new InvalidOperationException($"{artifactLabel} is missing object: {propertyName}.");
        }

        private static JsonElement RequireArray(JsonElement parent, string propertyName, string artifactLabel)
        {
            if (parent.TryGetProperty(propertyName, out JsonElement child) &&
                child.ValueKind == JsonValueKind.Array)
            {
                return child;
            }

            throw new InvalidOperationException($"{artifactLabel} is missing array: {propertyName}.");
        }

        private static string GetString(JsonElement element, string propertyName)
        {
            return element.TryGetProperty(propertyName, out JsonElement value) && value.ValueKind == JsonValueKind.String
                ? value.GetString() ?? string.Empty
                : string.Empty;
        }

        private static string RequirePublicSafeString(JsonElement element, string propertyName, string artifactLabel)
        {
            string value = GetString(element, propertyName);
            if (string.IsNullOrWhiteSpace(value) ||
                value != value.Trim() ||
                !s_publicSafeTopologyTokenPattern.IsMatch(value))
            {
                throw new InvalidOperationException($"{artifactLabel} has invalid string field: {propertyName}.");
            }

            return value;
        }

        private static void ValidateObjectProperties(JsonElement element, string artifactLabel, params string[] allowedProperties)
        {
            if (element.ValueKind != JsonValueKind.Object)
            {
                throw new InvalidOperationException($"{artifactLabel} must be a JSON object.");
            }

            var allowed = new HashSet<string>(allowedProperties, StringComparer.Ordinal);
            foreach (JsonProperty property in element.EnumerateObject())
            {
                if (!allowed.Contains(property.Name))
                {
                    throw new InvalidOperationException($"{artifactLabel} contains unexpected field: {property.Name}.");
                }
            }
        }

        private static string RequireStringEquals(JsonElement element, string propertyName, string expected, string artifactLabel)
        {
            string value = RequirePublicSafeString(element, propertyName, artifactLabel);
            if (!string.Equals(value, expected, StringComparison.Ordinal))
            {
                throw new InvalidOperationException($"{artifactLabel} has unexpected value for {propertyName}.");
            }

            return value;
        }

        private static bool RequireBoolEquals(JsonElement element, string propertyName, bool expected, string artifactLabel)
        {
            if (!element.ValueKind.Equals(JsonValueKind.Object) ||
                !element.TryGetProperty(propertyName, out JsonElement value) ||
                value.ValueKind != (expected ? JsonValueKind.True : JsonValueKind.False))
            {
                throw new InvalidOperationException($"{artifactLabel} has unexpected boolean value for {propertyName}.");
            }

            return expected;
        }

        private static int RequireIntEquals(JsonElement element, string propertyName, int expected, string artifactLabel)
        {
            if (!element.ValueKind.Equals(JsonValueKind.Object) ||
                !element.TryGetProperty(propertyName, out JsonElement value) ||
                value.ValueKind != JsonValueKind.Number ||
                !value.TryGetInt32(out int result) ||
                result != expected)
            {
                throw new InvalidOperationException($"{artifactLabel} has unexpected count for {propertyName}.");
            }

            return result;
        }

        private static void RequireStringArrayEquals(JsonElement element, string propertyName, IReadOnlyList<string> expected, string artifactLabel)
        {
            if (!element.ValueKind.Equals(JsonValueKind.Object) ||
                !element.TryGetProperty(propertyName, out JsonElement value) ||
                value.ValueKind != JsonValueKind.Array ||
                value.GetArrayLength() != expected.Count)
            {
                throw new InvalidOperationException($"{artifactLabel} has unexpected string array for {propertyName}.");
            }

            int index = 0;
            foreach (JsonElement item in value.EnumerateArray())
            {
                if (item.ValueKind != JsonValueKind.String ||
                    !string.Equals(item.GetString(), expected[index], StringComparison.Ordinal))
                {
                    throw new InvalidOperationException($"{artifactLabel} has unexpected string array item for {propertyName}.");
                }

                index++;
            }
        }

        private static bool GetBool(JsonElement element, string propertyName)
        {
            if (!element.ValueKind.Equals(JsonValueKind.Object) ||
                !element.TryGetProperty(propertyName, out JsonElement value))
            {
                return false;
            }

            return value.ValueKind == JsonValueKind.True;
        }

        private static string FormatBoolLower(bool value)
        {
            return value ? "true" : "false";
        }

        private static int GetBoundedCount(JsonElement element, string propertyName)
        {
            return GetBoundedCount(element, propertyName, "Second-host readiness artifact");
        }

        private static int GetBoundedCount(JsonElement element, string propertyName, string artifactLabel)
        {
            if (!element.ValueKind.Equals(JsonValueKind.Object) ||
                !element.TryGetProperty(propertyName, out JsonElement value) ||
                value.ValueKind != JsonValueKind.Number ||
                !value.TryGetInt32(out int result) ||
                result < 0 ||
                result > MaxReadinessCounter)
            {
                throw new InvalidOperationException($"{artifactLabel} has an invalid count: {propertyName}.");
            }

            return result;
        }

        public static OnlineCompanionSessionReadinessSummary GetCompanionSessionReadiness(
            string? copiedProfileRoot,
            bool contentMatchesCurrentSelection,
            GameProfileLaunchPlan? launchPlan,
            string? launchPlanError)
        {
            OnlineMultiplayerReadinessSummary online = GetCurrentSummary();
            bool hasCopiedProfile = !string.IsNullOrWhiteSpace(copiedProfileRoot);
            string status;
            string preview;
            IReadOnlyList<OnlineMultiplayerTryableAction> tryableActions;

            if (!hasCopiedProfile)
            {
                status = "missing-safe-copy";
                preview = "Prepare a safe game copy before companion-session readiness can inspect a launch plan.";
                tryableActions = [];
            }
            else if (!contentMatchesCurrentSelection)
            {
                status = "stale-safe-copy";
                preview = "Prepared safe copy is stale. Create a new safe copy before using online-adjacent readiness.";
                tryableActions = [];
            }
            else if (launchPlan is null)
            {
                status = "launch-plan-blocked";
                preview = string.IsNullOrWhiteSpace(launchPlanError) ? "Launch plan is not ready." : launchPlanError;
                tryableActions = [];
            }
            else
            {
                status = "safe-copy-launch-plan-ready";
                preview = launchPlan.CommandPreview;
                tryableActions = online.TryableActions;
            }

            return new OnlineCompanionSessionReadinessSummary(
                SchemaVersion: "winui-original-binary-companion-session-readiness.v1",
                SafeCopyManifestStatus: status,
                LaunchPlanPreview: preview,
                MayEnableHostJoin: false,
                BaseOnlineMultiplayerReady: false,
                TryableActions: tryableActions,
                BlockedActions: online.BlockedActions,
                NextProofIds: s_nextProofIds,
                NonClaims: new[]
                {
                    "no listener",
                    "no invitation",
                    "no helper lifecycle",
                    "no remote input",
                    "no second-host runtime delivery",
                    "no BEA netcode proof",
                    "no Host/Join controls",
                    "no player-ready netplay",
                });
        }
    }
}
