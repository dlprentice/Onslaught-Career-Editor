using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Nodes;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class OnlineMultiplayerReadinessServiceTests
    {
        [Fact]
        public void GetCurrentSummary_PreservesOnlineNonClaimsAndSlotBoundary()
        {
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary();

            Assert.Equal("original-binary-online-readiness-summary.v1", summary.SchemaVersion);
            Assert.False(summary.BaseOnlineMultiplayerReady);
            Assert.False(summary.MultiHostLanProof);
            Assert.False(summary.PublicMatchmakingProof);
            Assert.False(summary.NativeBeaNetcodeProof);
            Assert.False(summary.ActiveP3P4OriginalBinaryGameplayProof);
            Assert.False(summary.PhysicalGamepadRuntimeProof);
            Assert.Equal(new[] { "P1", "P2" }, summary.AcceptedOriginalBinaryGameplaySlots);
            Assert.Equal(new[] { "P3", "P4" }, summary.MetadataOnlySlots);
            Assert.Contains(summary.StatusRows, row => row.Label == "Netplay readiness" && row.Value == "Not player-ready");
            Assert.Contains(summary.StatusRows, row => row.Label == "Current original-binary gameplay slots" && row.Value == "P1/P2 only");
            Assert.Contains(summary.StatusRows, row => row.Label == "P3/P4 status" && row.Value == "Session metadata only");
            Assert.Contains(summary.SecondHostSetupSteps, step => step.Label == "Use a real endpoint" && step.Status == "No accepted endpoint proof");
            Assert.Contains(summary.SecondHostSetupSteps, step => step.Label == "Use a real endpoint" && step.Detail.Contains("Same-workstation processes and WSL-on-host do not count"));
            Assert.Contains(summary.SecondHostSetupSteps, step => step.Label == "Accept a signed P2 command" && step.Status == "Pending");
            Assert.Contains(summary.SecondHostSetupSteps, step => step.Label == "Bind it to copied runtime" && step.Detail.Contains("exact-PID CDB evidence"));
            Assert.Contains(summary.SecondHostSetupSteps, step => step.Label == "Keep P3/P4 out of gameplay" && step.Status == "Boundary");
            Assert.Contains("separate safe copy", summary.CompanionNetplayTarget.UserExperience, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("instead of split-screen", summary.CompanionNetplayTarget.UserExperience, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("WinUI or packaged helper", summary.CompanionNetplayTarget.CompanionRequirement, System.StringComparison.Ordinal);
            Assert.Contains("No Host/Join controls", summary.CompanionNetplayTarget.CurrentBoundary, System.StringComparison.Ordinal);
            Assert.Equal(6, summary.ProofLadderRows.Count);
            Assert.Equal("P1/P2 local split-screen study surface", summary.ProofLadderRows[0].Label);
            Assert.Equal("accepted-local-only", summary.ProofLadderRows[0].Status);
            Assert.Contains("not online play", summary.ProofLadderRows[0].Detail, System.StringComparison.OrdinalIgnoreCase);
            Assert.Equal("Same-workstation command relay chain", summary.ProofLadderRows[1].Label);
            Assert.Equal("accepted-local-only", summary.ProofLadderRows[1].Status);
            Assert.Contains("not second-host LAN proof", summary.ProofLadderRows[1].Detail, System.StringComparison.OrdinalIgnoreCase);
            Assert.Equal("Physical gamepad input route", summary.ProofLadderRows[2].Label);
            Assert.Equal("blocked", summary.ProofLadderRows[2].Status);
            Assert.Contains("No local physical controller readiness artifact", summary.ProofLadderRows[2].Detail, System.StringComparison.Ordinal);
            Assert.Equal("Distinct endpoint command source", summary.ProofLadderRows[3].Label);
            Assert.Equal("missing", summary.ProofLadderRows[3].Status);
            Assert.Equal("Source-bound copied-runtime causality", summary.ProofLadderRows[4].Label);
            Assert.Equal("missing", summary.ProofLadderRows[4].Status);
            Assert.Equal("Host/Join player workflow", summary.ProofLadderRows[5].Label);
            Assert.Equal("locked", summary.ProofLadderRows[5].Status);
        }

        [Fact]
        public void GetCurrentSummary_ExposesOnlySafeTryableAction()
        {
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary();

            Assert.Single(summary.TryableActions);
            Assert.Equal("Local multiplayer probe", summary.TryableActions[0].Label);
            Assert.Equal("-skipfmv -level 850", summary.TryableActions[0].LaunchHint);
            Assert.DoesNotContain(summary.TryableActions, action => action.Label.Contains("Host"));
            Assert.DoesNotContain(summary.TryableActions, action => action.Label.Contains("Join"));
            Assert.Contains(summary.BlockedActions, action => action.Label == "Online hosting unavailable");
            Assert.Contains(summary.BlockedActions, action => action.Label == "Online joining unavailable");
            Assert.All(summary.BlockedActions, action => Assert.False(action.Enabled));
        }

        [Fact]
        public void GetCurrentSummary_NamesNextProofWithoutPromotingOnline()
        {
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary();

            Assert.Contains("real VM or physical second-host live command-source proof", summary.NextProofNeeded, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("source-bound runtime causality", summary.NextProofNeeded, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("mapped P2 sequence and host-helper receipt binding", summary.NextProofNeeded, System.StringComparison.OrdinalIgnoreCase);
            Assert.Contains("WinUI host/join readiness surface", summary.FallbackWithoutSecondHost);
            Assert.Contains(summary.NonClaims, claim => claim.Contains("No player-ready online multiplayer", System.StringComparison.Ordinal));
            Assert.Contains(summary.NonClaims, claim => claim.Contains("No native BEA netcode", System.StringComparison.Ordinal));
            Assert.Contains(summary.NonClaims, claim => claim.Contains("No active P3/P4 original-binary gameplay", System.StringComparison.Ordinal));
            Assert.Contains(summary.NonClaims, claim => claim.Contains("No proof-ladder row enables Host/Join", System.StringComparison.Ordinal));
        }

        [Fact]
        public void TryParseDualSafeCopyTopologyArtifactJson_AcceptsDescriptorOnlyContractWithoutEnablingHostJoin()
        {
            string json = BuildDualSafeCopyTopologyFixture().ToJsonString();

            bool loaded = OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                json,
                out OnlineDualSafeCopyTopologyArtifactSummary? topology,
                out string? error);

            Assert.True(loaded, error);
            Assert.NotNull(topology);
            Assert.Equal("winui-original-binary-online-dual-safe-copy-topology.v1", topology!.SchemaVersion);
            Assert.Equal("dual-safe-copy-same-workstation-topology-not-online-play", topology.Scope);
            Assert.Equal(2, topology.SafeCopyCount);
            Assert.Equal(new[] { "host", "joiner" }, topology.Roles);
            Assert.True(topology.SameWorkstationOnly);
            Assert.True(topology.SamePhysicalMachineOnly);
            Assert.Equal(2, topology.SafeCopyRootDescriptorCount);
            Assert.Equal(2, topology.SafeCopyExecutableDescriptorCount);
            Assert.Equal(1, topology.DistinctSafeCopyRootPairCount);
            Assert.Equal(0, topology.BeaLaunchCount);
            Assert.Equal(0, topology.CdbAttachCount);
            Assert.Equal(0, topology.HostJoinControlsEnabledCount);
            Assert.Contains("distinct-endpoint-command-source-proof", topology.RequiredFutureEvidenceIds);
            Assert.Contains("source-bound-copied-runtime-causality-proof", topology.RequiredFutureEvidenceIds);
            Assert.Contains("no BEA launch", topology.ClaimBoundary, System.StringComparison.OrdinalIgnoreCase);

            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(
                secondHostReadinessArtifact: null,
                localGamepadReadinessArtifact: null,
                dualSafeCopyTopologyArtifact: topology);
            Assert.False(summary.BaseOnlineMultiplayerReady);
            Assert.False(summary.SecondHostLiveAttemptReadiness.HostJoinControlsMayBeEnabled);
            Assert.Equal(topology, summary.DualSafeCopyTopologyArtifact);
            Assert.Contains(summary.StatusRows, row => row.Label == "Dual safe-copy topology" && row.Value.Contains("descriptor-only", System.StringComparison.OrdinalIgnoreCase));
            Assert.Equal(7, summary.ProofLadderRows.Count);
            Assert.Contains(summary.ProofLadderRows, row =>
                row.Label == "Dual safe-copy topology contract" &&
                row.Status == "accepted-contract-only" &&
                row.Detail.Contains("not online play", System.StringComparison.OrdinalIgnoreCase));
            Assert.Contains(summary.NonClaims, claim => claim.Contains("No dual-safe-copy topology contract enables Host/Join", System.StringComparison.Ordinal));
        }

        [Fact]
        public void TryParseDualSafeCopyTopologyArtifactJson_RejectsHostJoinOrRuntimeOverclaims()
        {
            JsonObject hostJoinPayload = BuildDualSafeCopyTopologyFixture();
            hostJoinPayload["proofBoundary"]!["hostJoinControlsMayBeEnabled"] = true;
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                hostJoinPayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? hostJoinTopology,
                out string? hostJoinError));
            Assert.Null(hostJoinTopology);
            Assert.Contains("hostJoinControlsMayBeEnabled", hostJoinError);

            JsonObject launchPayload = BuildDualSafeCopyTopologyFixture();
            launchPayload["topologyCounters"]!["newBeaLaunchCount"] = 1;
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                launchPayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? launchTopology,
                out string? launchError));
            Assert.Null(launchTopology);
            Assert.Contains("newBeaLaunchCount", launchError);
        }

        [Fact]
        public void TryParseDualSafeCopyTopologyArtifactJson_RejectsPrivatePathsAndInvalidRoles()
        {
            JsonObject pathPayload = BuildDualSafeCopyTopologyFixture();
            pathPayload["safeCopies"]![0]!["safeCopyRootLabel"] = string.Join("\\", new[] { "C:", "Users", "david", "safe-copy" });
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                pathPayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? pathTopology,
                out string? pathError));
            Assert.Null(pathTopology);
            Assert.Contains("private or sensitive string", pathError);

            JsonObject rolePayload = BuildDualSafeCopyTopologyFixture();
            rolePayload["safeCopies"]![1]!["role"] = "host";
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                rolePayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? roleTopology,
                out string? roleError));
            Assert.Null(roleTopology);
            Assert.Contains("roles", roleError, System.StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void TryParseDualSafeCopyTopologyArtifactJson_RejectsUnknownFieldsAndWeakFutureEvidence()
        {
            JsonObject unknownPayload = BuildDualSafeCopyTopologyFixture();
            unknownPayload["proofBoundary"]!["hostJoinEnabled"] = true;
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                unknownPayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? unknownTopology,
                out string? unknownError));
            Assert.Null(unknownTopology);
            Assert.Contains("unexpected field", unknownError, System.StringComparison.OrdinalIgnoreCase);

            JsonObject weakFuturePayload = BuildDualSafeCopyTopologyFixture();
            weakFuturePayload["requiredFutureEvidence"]![0]!["mustProve"] = new JsonArray("foo");
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                weakFuturePayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? weakFutureTopology,
                out string? weakFutureError));
            Assert.Null(weakFutureTopology);
            Assert.Contains("future evidence", weakFutureError, System.StringComparison.OrdinalIgnoreCase);

            JsonObject extraFuturePayload = BuildDualSafeCopyTopologyFixture();
            extraFuturePayload["requiredFutureEvidence"]!.AsArray().Add(BuildFutureEvidence("maybe-online-later", "hostJoinEnabled"));
            Assert.False(OnlineMultiplayerReadinessService.TryParseDualSafeCopyTopologyArtifactJson(
                extraFuturePayload.ToJsonString(),
                out OnlineDualSafeCopyTopologyArtifactSummary? extraFutureTopology,
                out string? extraFutureError));
            Assert.Null(extraFutureTopology);
            Assert.Contains("future evidence", extraFutureError, System.StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void GetCurrentSummary_ExposesSecondHostLiveAttemptChecklistWithoutEnablingNetplay()
        {
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary();

            OnlineSecondHostLiveAttemptReadiness readiness = summary.SecondHostLiveAttemptReadiness;
            Assert.Equal("winui-original-binary-second-host-live-attempt-readiness.v1", readiness.SchemaVersion);
            Assert.False(readiness.ReadyToAttemptHarness);
            Assert.False(readiness.ReadyForLiveValidationCandidate);
            Assert.False(readiness.ReadyToRunLiveCommandSource);
            Assert.False(readiness.ServerCommandInputsComplete);
            Assert.False(readiness.ClientPreflightProvided);
            Assert.False(readiness.HostJoinControlsMayBeEnabled);
            Assert.False(readiness.AcceptedLiveSecondHostCommandSourceProof);
            Assert.False(readiness.BaseOnlineMultiplayerReady);
            Assert.Contains(readiness.BlockingReasons, reason => reason.Contains("client identity/source-safety preflight", System.StringComparison.OrdinalIgnoreCase));
            Assert.Contains(readiness.BlockingReasons, reason => reason.Contains("server command inputs", System.StringComparison.OrdinalIgnoreCase));
            Assert.Contains(readiness.RequiredInputs, step => step.Label == "Client preflight" && step.Status == "Missing");
            Assert.Contains(readiness.RequiredInputs, step => step.Label == "Server command inputs" && step.Status == "Incomplete");
            Assert.Equal(new[] { "npm run test:safe-copy", "npm run test:product" }, readiness.SafeCommands);
            Assert.DoesNotContain(readiness.SafeCommands, command => command.Contains("Host/Join", System.StringComparison.OrdinalIgnoreCase));
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_AcceptsReadinessPreflightWithoutEnablingHostJoin()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-readiness.v1",
                status = "host-preflight-ready-for-external-client",
                proofBooleans = FalseProofBooleans(),
                hostInterfacePreflight = new
                {
                    candidatePrivateBindAddressCount = 2,
                    wslOnHostInterfaceCount = 1
                },
                requestedRunInputs = new
                {
                    serverCommandInputsComplete = true
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.True(loaded, error);
            Assert.NotNull(artifact);
            Assert.Equal("host live-readiness preflight", artifact!.SourceKind);
            Assert.False(artifact.ReadyToRunLiveCommandSource);
            Assert.True(artifact.ServerCommandInputsComplete);
            Assert.False(artifact.ClientPreflightProvided);
            Assert.Equal(2, artifact.CandidatePrivateBindAddressCount);

            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(artifact);
            Assert.False(summary.SecondHostLiveAttemptReadiness.HostJoinControlsMayBeEnabled);
            Assert.False(summary.SecondHostLiveAttemptReadiness.BaseOnlineMultiplayerReady);
            Assert.False(summary.SecondHostLiveAttemptReadiness.AcceptedLiveSecondHostCommandSourceProof);
            Assert.True(summary.SecondHostLiveAttemptReadiness.ServerCommandInputsComplete);
            Assert.False(summary.SecondHostLiveAttemptReadiness.ClientPreflightProvided);
        }

        [Fact]
        public void TryParseLocalGamepadReadinessArtifactJson_AcceptsBlockedPreflightWithoutPromotingRuntimeProof()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1",
                status = "blocked_no_present_gamepad",
                physicalGamepadRuntimeProofReady = false,
                presentGamepadCandidateCount = 0,
                registryGamepadCandidateCount = 0,
                pnpDeviceCount = 12,
                joystickRegistryRowCount = 2,
                presentGamepadCandidates = System.Array.Empty<object>(),
                registryGamepadCandidates = System.Array.Empty<object>(),
                claimBoundary = "hardware detection is a precondition, not BEA polling proof",
                nextRuntimeProofRequires = new[]
                {
                    "exact managed BEA PID and CDB attachment",
                    "zero keyboard SendInput/keybd_event/PostMessage positive-stimulus counters"
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseLocalGamepadReadinessArtifactJson(
                json,
                out OnlineLocalGamepadReadinessArtifactSummary? artifact,
                out string? error);

            Assert.True(loaded, error);
            Assert.NotNull(artifact);
            Assert.Equal("local physical gamepad readiness preflight", artifact!.SourceKind);
            Assert.Equal("blocked_no_present_gamepad", artifact.Status);
            Assert.False(artifact.ReadyForPhysicalGamepadRuntimeAttempt);
            Assert.Equal(0, artifact.PresentGamepadCandidateCount);
            Assert.Equal(2, artifact.JoystickRegistryRowCount);

            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(null, artifact);
            Assert.False(summary.PhysicalGamepadRuntimeProof);
            Assert.Contains(summary.StatusRows, row => row.Label == "Physical gamepad readiness" && row.Value.Contains("blocked_no_present_gamepad"));
            Assert.Contains(summary.ProofGateRows, row => row.Label == "Physical gamepad routing" && row.Value.Contains("Not accepted"));
            Assert.Contains(summary.ProofLadderRows, row =>
                row.Label == "Physical gamepad input route" &&
                row.Status == "hardware-preflight-only" &&
                row.Detail.Contains("Local hardware preflight has no present controller candidate", System.StringComparison.Ordinal));
            Assert.Contains(summary.NonClaims, claim => claim.Contains("No physical gamepad runtime proof", System.StringComparison.Ordinal));
        }

        [Fact]
        public void TryParseLocalGamepadReadinessArtifactJson_AcceptsPresentHardwareWithoutPromotingRuntimeProof()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1",
                status = "ready_for_physical_gamepad_runtime_attempt",
                physicalGamepadRuntimeProofReady = true,
                presentGamepadCandidateCount = 1,
                registryGamepadCandidateCount = 1,
                pnpDeviceCount = 8,
                joystickRegistryRowCount = 1,
                presentGamepadCandidates = new[]
                {
                    new
                    {
                        candidate = true,
                        friendlyName = "HID-compliant game controller",
                        instanceId = "HID\\VID_045E&PID_02FF",
                        reason = "gamepad-like present PnP device"
                    }
                },
                registryGamepadCandidates = new[]
                {
                    new
                    {
                        candidate = true,
                        oemName = "Xbox Controller",
                        key = "VID_045E&PID_02FF"
                    }
                },
                claimBoundary = "This is a workstation readiness preflight only.",
                nextRuntimeProofRequires = new[] { "CDB rows at 0x00513370 PlatformInput__PollPadState" }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseLocalGamepadReadinessArtifactJson(
                json,
                out OnlineLocalGamepadReadinessArtifactSummary? artifact,
                out string? error);

            Assert.True(loaded, error);
            Assert.NotNull(artifact);
            Assert.True(artifact!.ReadyForPhysicalGamepadRuntimeAttempt);
            Assert.Equal(1, artifact.PresentGamepadCandidateCount);

            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(null, artifact);
            Assert.False(summary.PhysicalGamepadRuntimeProof);
            Assert.Contains(summary.StatusRows, row => row.Label == "Physical gamepad readiness" && row.Value.Contains("ready_for_physical_gamepad_runtime_attempt"));
            Assert.Contains(summary.ProofGateRows, row => row.Label == "Physical gamepad routing" && row.Value.Contains("hardware preflight only"));
            Assert.Contains(summary.ProofLadderRows, row =>
                row.Label == "Physical gamepad input route" &&
                row.Status == "hardware-preflight-only" &&
                row.Detail.Contains("Local hardware preflight found a controller candidate", System.StringComparison.Ordinal) &&
                row.Detail.Contains("no-keyboard negative control", System.StringComparison.Ordinal));
            Assert.All(summary.BlockedActions, action => Assert.False(action.Enabled));
        }

        [Fact]
        public void GetCurrentSummary_KeepsHostJoinPromotionLockedWhenCandidateArtifactsAreLoaded()
        {
            string secondHostJson = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-run-kit.v1",
                status = "ready-to-run-live-command-source",
                readyToAttemptHarness = true,
                readyForLiveValidationCandidate = true,
                readyToRunLiveCommandSource = true,
                proofBooleans = FalseProofBooleans(),
                hostReadiness = new
                {
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0,
                    serverCommandInputsComplete = true
                },
                clientPreflight = new
                {
                    provided = true
                }
            });
            string gamepadJson = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1",
                status = "ready_for_physical_gamepad_runtime_attempt",
                physicalGamepadRuntimeProofReady = true,
                presentGamepadCandidateCount = 1,
                registryGamepadCandidateCount = 1,
                pnpDeviceCount = 4,
                joystickRegistryRowCount = 1,
                presentGamepadCandidates = new[]
                {
                    new
                    {
                        candidate = true,
                        friendlyName = "HID-compliant game controller",
                        instanceId = "HID\\VID_045E&PID_02FF",
                        reason = "gamepad-like present PnP device"
                    }
                },
                registryGamepadCandidates = new[]
                {
                    new
                    {
                        candidate = true,
                        oemName = "Xbox Controller",
                        key = "VID_045E&PID_02FF"
                    }
                },
                claimBoundary = "hardware detection is not player-ready online proof",
                nextRuntimeProofRequires = new[] { "source-bound copied-runtime causality proof" }
            });

            bool secondHostLoaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                secondHostJson,
                out OnlineSecondHostReadinessArtifactSummary? secondHostArtifact,
                out string? secondHostError);
            bool gamepadLoaded = OnlineMultiplayerReadinessService.TryParseLocalGamepadReadinessArtifactJson(
                gamepadJson,
                out OnlineLocalGamepadReadinessArtifactSummary? gamepadArtifact,
                out string? gamepadError);

            Assert.True(secondHostLoaded, secondHostError);
            Assert.True(gamepadLoaded, gamepadError);
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(secondHostArtifact, gamepadArtifact);

            Assert.True(summary.SecondHostLiveAttemptReadiness.ReadyToRunLiveCommandSource);
            Assert.True(summary.SecondHostLiveAttemptReadiness.ClientPreflightProvided);
            Assert.True(summary.SecondHostLiveAttemptReadiness.ServerCommandInputsComplete);
            Assert.False(summary.BaseOnlineMultiplayerReady);
            Assert.False(summary.SecondHostLiveAttemptReadiness.HostJoinControlsMayBeEnabled);
            Assert.False(summary.SecondHostLiveAttemptReadiness.AcceptedLiveSecondHostCommandSourceProof);
            Assert.False(summary.PhysicalGamepadRuntimeProof);
            Assert.DoesNotContain(summary.TryableActions, action => action.Label.Contains("Host", System.StringComparison.OrdinalIgnoreCase));
            Assert.DoesNotContain(summary.TryableActions, action => action.Label.Contains("Join", System.StringComparison.OrdinalIgnoreCase));
            Assert.All(summary.BlockedActions, action => Assert.False(action.Enabled));
            Assert.Contains(summary.StatusRows, row =>
                row.Label == "Host/Join promotion lock" &&
                row.Value.Contains("online play is not available in this release", System.StringComparison.OrdinalIgnoreCase));
            Assert.Contains(summary.ProofGateRows, row =>
                row.Label == "Host/Join promotion" &&
                row.Value.Contains("source-bound copied-runtime causality", System.StringComparison.OrdinalIgnoreCase));
            Assert.Contains(summary.NonClaims, claim =>
                claim.Contains("No Host/Join promotion from readiness artifacts", System.StringComparison.Ordinal));
            Assert.Contains(summary.ProofLadderRows, row =>
                row.Label == "Host/Join player workflow" &&
                row.Status == "locked" &&
                row.Detail.Contains("remain unavailable", System.StringComparison.OrdinalIgnoreCase));
        }

        [Fact]
        public void TryParseLocalGamepadReadinessArtifactJson_RejectsRuntimeAndOnlineOverclaims()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-safe-copy-local-multiplayer-gamepad-readiness.v1",
                status = "ready_for_physical_gamepad_runtime_attempt",
                physicalGamepadRuntimeProofReady = true,
                presentGamepadCandidateCount = 1,
                registryGamepadCandidateCount = 0,
                pnpDeviceCount = 2,
                joystickRegistryRowCount = 0,
                hidden = new
                {
                    physicalGamepadRuntimeProof = true,
                    hostJoinControlsMayBeEnabled = "yes"
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseLocalGamepadReadinessArtifactJson(
                json,
                out OnlineLocalGamepadReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("physicalGamepadRuntimeProof", error);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_AcceptsRunKitSummaryWithoutPublishingNetplay()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-run-kit.v1",
                status = "ready-to-run-live-command-source",
                readyToAttemptHarness = true,
                readyForLiveValidationCandidate = true,
                readyToRunLiveCommandSource = true,
                proofBooleans = FalseProofBooleans(),
                hostReadiness = new
                {
                    serverCommandInputsComplete = true,
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                clientPreflight = new
                {
                    provided = true
                },
                privateRunInputs = new
                {
                    rawPrivatePathsSerializedInPublicDocs = false
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.True(loaded, error);
            Assert.NotNull(artifact);
            Assert.Equal("second-host live run kit", artifact!.SourceKind);
            Assert.True(artifact.ReadyToAttemptHarness);
            Assert.True(artifact.ReadyForLiveValidationCandidate);
            Assert.True(artifact.ReadyToRunLiveCommandSource);
            Assert.True(artifact.ClientPreflightProvided);

            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(artifact);
            Assert.True(summary.SecondHostLiveAttemptReadiness.ReadyToRunLiveCommandSource);
            Assert.False(summary.SecondHostLiveAttemptReadiness.HostJoinControlsMayBeEnabled);
            Assert.False(summary.SecondHostLiveAttemptReadiness.BaseOnlineMultiplayerReady);
            Assert.Contains(summary.SecondHostLiveAttemptReadiness.BlockingReasons, reason => reason.Contains("No source-bound copied-runtime causality proof", System.StringComparison.Ordinal));
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsProofOverclaims()
        {
            var proof = FalseProofBooleans();
            proof["hostJoinControlsMayBeEnabled"] = true;
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-run-kit.v1",
                status = "ready-to-run-live-command-source",
                proofBooleans = proof,
                hostReadiness = new
                {
                    serverCommandInputsComplete = true,
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                clientPreflight = new
                {
                    provided = true
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("hostJoinControlsMayBeEnabled", error);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsTruthyStringAndNumericOverclaims()
        {
            var proof = new Dictionary<string, object>
            {
                ["acceptedLiveSecondHostCommandSourceProof"] = false,
                ["acceptedLiveSecondHostRuntimeDeliveryProof"] = false,
                ["acceptedLiveSecondHostRuntimeCausalityProof"] = false,
                ["baseOnlineMultiplayerReady"] = false,
                ["hostJoinControlsMayBeEnabled"] = "true",
                ["multiHostLanPlayProof"] = false,
                ["publicMatchmakingProof"] = false,
                ["nativeBeaNetcodeProof"] = false,
                ["activeP3P4OriginalBinaryGameplayProof"] = 0,
            };
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-run-kit.v1",
                status = "ready-to-attempt-harness-only-not-live-ready",
                proofBooleans = proof,
                hidden = new
                {
                    nativeBeaNetcodeProof = 1
                },
                hostReadiness = new
                {
                    serverCommandInputsComplete = true,
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                clientPreflight = new
                {
                    provided = true
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("hostJoinControlsMayBeEnabled", error);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsPrivatePathsIpAddressesAndTokensInNestedStrings()
        {
            string privateIp = string.Join(".", new[] { "192", "168", "1", "50" });
            string privatePath = string.Join("\\", new[] { "C:", "Users", "david", "source", "Onslaught-Career-Editor-" + "private", "game" });
            string tokenLikeValue = "ghp_" + "abcdefghijklmnopqrstuvwxyz123456";
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-run-kit.v1",
                status = "ready-to-attempt-harness-only-not-live-ready",
                proofBooleans = FalseProofBooleans(),
                hostReadiness = new
                {
                    serverCommandInputsComplete = true,
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                clientPreflight = new
                {
                    provided = true
                },
                diagnostics = new
                {
                    rejected = new[]
                    {
                        privatePath,
                        privateIp,
                        tokenLikeValue
                    }
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("private", error, System.StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsUnexpectedDisplayStatus()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-readiness.v1",
                status = "host-join-enabled",
                proofBooleans = FalseProofBooleans(),
                hostInterfacePreflight = new
                {
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                requestedRunInputs = new
                {
                    serverCommandInputsComplete = true
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("status", error, System.StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsMissingRequiredFalseProofBooleans()
        {
            var proof = FalseProofBooleans();
            proof.Remove("nativeBeaNetcodeProof");
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-readiness.v1",
                status = "host-preflight-ready-for-external-client",
                proofBooleans = proof,
                hostInterfacePreflight = new
                {
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                requestedRunInputs = new
                {
                    serverCommandInputsComplete = true
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("nativeBeaNetcodeProof", error);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsOutOfRangeReadinessCounts()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-readiness.v1",
                status = "host-preflight-ready-for-external-client",
                proofBooleans = FalseProofBooleans(),
                hostInterfacePreflight = new
                {
                    candidatePrivateBindAddressCount = -1,
                    wslOnHostInterfaceCount = 100_000
                },
                requestedRunInputs = new
                {
                    serverCommandInputsComplete = true
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("candidatePrivateBindAddressCount", error);
        }

        [Fact]
        public void TryParseSecondHostReadinessArtifactJson_RejectsReadyToRunWithoutHostAndClientPrerequisites()
        {
            string json = JsonSerializer.Serialize(new
            {
                schemaVersion = "winui-original-binary-second-host-live-run-kit.v1",
                status = "ready-to-run-live-command-source",
                readyToAttemptHarness = true,
                readyForLiveValidationCandidate = true,
                readyToRunLiveCommandSource = true,
                proofBooleans = FalseProofBooleans(),
                hostReadiness = new
                {
                    serverCommandInputsComplete = false,
                    candidatePrivateBindAddressCount = 1,
                    wslOnHostInterfaceCount = 0
                },
                clientPreflight = new
                {
                    provided = false
                }
            });

            bool loaded = OnlineMultiplayerReadinessService.TryParseSecondHostReadinessArtifactJson(
                json,
                out OnlineSecondHostReadinessArtifactSummary? artifact,
                out string? error);

            Assert.False(loaded);
            Assert.Null(artifact);
            Assert.Contains("ready-to-run", error, System.StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void TryLoadSecondHostReadinessArtifact_RejectsOversizedJsonBeforeParsing()
        {
            string path = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName() + ".json");
            try
            {
                File.WriteAllText(path, new string(' ', 70_000));

                bool loaded = OnlineMultiplayerReadinessService.TryLoadSecondHostReadinessArtifact(
                    path,
                    out OnlineSecondHostReadinessArtifactSummary? artifact,
                    out string? error);

                Assert.False(loaded);
                Assert.Null(artifact);
                Assert.Contains("too large", error, System.StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (File.Exists(path))
                {
                    File.Delete(path);
                }
            }
        }

        [Fact]
        public void GetCurrentSummary_ExposesCurrentProofGateHardening()
        {
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary();

            Assert.Contains(summary.ProofGateRows, row => row.Label == "Live command source" && row.Value.Contains("not accepted", System.StringComparison.OrdinalIgnoreCase));
            Assert.Contains(summary.ProofGateRows, row => row.Value.Contains("4096", System.StringComparison.Ordinal));
            Assert.Contains(summary.ProofGateRows, row => row.Value.Contains("operator-supplied runtime-host-kind", System.StringComparison.Ordinal));
            Assert.Contains(summary.ProofGateRows, row => row.Value.Contains("mapped P2 sequence", System.StringComparison.Ordinal));
            Assert.Contains(summary.ProofGateRows, row => row.Value.Contains("host-helper receipt", System.StringComparison.Ordinal));
            Assert.Contains(summary.BlockedActions, action => action.Label == "Online hosting unavailable" && action.Reason.Contains("mapped P2", System.StringComparison.Ordinal));
            Assert.Contains(summary.BlockedActions, action => action.Label == "Online joining unavailable" && action.Reason.Contains("invitation lifecycle hash", System.StringComparison.Ordinal));
        }

        [Fact]
        public void GetCompanionSessionReadiness_ReportsMissingSafeCopyWithoutEnablingHostJoin()
        {
            OnlineCompanionSessionReadinessSummary summary = OnlineMultiplayerReadinessService.GetCompanionSessionReadiness(
                copiedProfileRoot: null,
                contentMatchesCurrentSelection: false,
                launchPlan: null,
                launchPlanError: null);

            Assert.Equal("winui-original-binary-companion-session-readiness.v1", summary.SchemaVersion);
            Assert.Equal("missing-safe-copy", summary.SafeCopyManifestStatus);
            Assert.False(summary.MayEnableHostJoin);
            Assert.False(summary.BaseOnlineMultiplayerReady);
            Assert.Empty(summary.TryableActions);
            Assert.Contains(summary.BlockedActions, action => action.Label == "Online hosting unavailable" && !action.Enabled);
            Assert.Contains("no listener", summary.NonClaims);
            Assert.Contains("no invitation", summary.NonClaims);
            Assert.Contains("no remote input", summary.NonClaims);
        }

        [Fact]
        public void GetCompanionSessionReadiness_ReportsReadySafeCopyAsLocalProbeOnly()
        {
            var launchPlan = new GameProfileLaunchPlan(
                ExecutablePath: "C:\\SafeCopy\\BEA.exe",
                WorkingDirectory: "C:\\SafeCopy",
                Arguments: new[] { "-skipfmv", "-level", "850" },
                CommandPreview: "\"C:\\SafeCopy\\BEA.exe\" -skipfmv -level 850");

            OnlineCompanionSessionReadinessSummary summary = OnlineMultiplayerReadinessService.GetCompanionSessionReadiness(
                copiedProfileRoot: "C:\\SafeCopy",
                contentMatchesCurrentSelection: true,
                launchPlan: launchPlan,
                launchPlanError: null);

            Assert.Equal("safe-copy-launch-plan-ready", summary.SafeCopyManifestStatus);
            Assert.Contains("-level 850", summary.LaunchPlanPreview);
            Assert.Single(summary.TryableActions);
            Assert.Equal("Local multiplayer probe", summary.TryableActions[0].Label);
            Assert.False(summary.MayEnableHostJoin);
            Assert.Contains("distinct-private-host-command-source-proof", summary.NextProofIds);
            Assert.Contains("host-runtime-delivery-from-source-bound-distinct-command-source", summary.NextProofIds);
            Assert.Contains("host-join-enablement-composite-proof", summary.NextProofIds);
        }

        [Fact]
        public void GetCompanionSessionReadiness_ReportsStaleOrBlockedSafeCopy()
        {
            OnlineCompanionSessionReadinessSummary stale = OnlineMultiplayerReadinessService.GetCompanionSessionReadiness(
                copiedProfileRoot: "C:\\SafeCopy",
                contentMatchesCurrentSelection: false,
                launchPlan: null,
                launchPlanError: "stale");
            Assert.Equal("stale-safe-copy", stale.SafeCopyManifestStatus);
            Assert.False(stale.MayEnableHostJoin);

            OnlineCompanionSessionReadinessSummary blocked = OnlineMultiplayerReadinessService.GetCompanionSessionReadiness(
                copiedProfileRoot: "C:\\SafeCopy",
                contentMatchesCurrentSelection: true,
                launchPlan: null,
                launchPlanError: "Launch plan is not ready.");
            Assert.Equal("launch-plan-blocked", blocked.SafeCopyManifestStatus);
            Assert.Contains("Launch plan is not ready.", blocked.LaunchPlanPreview);
            Assert.Empty(blocked.TryableActions);
        }

        private static System.Collections.Generic.Dictionary<string, bool> FalseProofBooleans()
        {
            return new System.Collections.Generic.Dictionary<string, bool>
            {
                ["acceptedLiveSecondHostCommandSourceProof"] = false,
                ["acceptedLiveSecondHostRuntimeDeliveryProof"] = false,
                ["acceptedLiveSecondHostRuntimeCausalityProof"] = false,
                ["baseOnlineMultiplayerReady"] = false,
                ["hostJoinControlsMayBeEnabled"] = false,
                ["multiHostLanPlayProof"] = false,
                ["publicMatchmakingProof"] = false,
                ["nativeBeaNetcodeProof"] = false,
                ["activeP3P4OriginalBinaryGameplayProof"] = false,
            };
        }

        private static JsonObject BuildDualSafeCopyTopologyFixture()
        {
            return new JsonObject
            {
                ["schemaVersion"] = "winui-original-binary-online-dual-safe-copy-topology.v1",
                ["status"] = "complete public-safe dual-safe-copy topology contract; no BEA launch or runtime proof",
                ["date"] = "2026-06-22",
                ["scope"] = "dual-safe-copy-same-workstation-topology-not-online-play",
                ["topology"] = new JsonObject
                {
                    ["topologyKind"] = "same-workstation-two-app-owned-safe-copies",
                    ["topologyProofClass"] = "topology-contract-not-runtime-proof",
                    ["safeCopyCount"] = 2,
                    ["sameWorkstationOnly"] = true,
                    ["samePhysicalMachineOnly"] = true,
                    ["separateGameViewsProven"] = false,
                    ["distinctEndpointProof"] = false,
                    ["playerReadyOnlineProof"] = false,
                },
                ["safeCopies"] = new JsonArray
                {
                    BuildSafeCopyDescriptor(
                        "host",
                        "host-safe-copy-root",
                        "1111111111111111111111111111111111111111111111111111111111111111",
                        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                        "host-copied-bea-exe",
                        "future-host-copied-runtime"),
                    BuildSafeCopyDescriptor(
                        "joiner",
                        "joiner-safe-copy-root",
                        "2222222222222222222222222222222222222222222222222222222222222222",
                        "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
                        "joiner-copied-bea-exe",
                        "future-joiner-command-source-safe-copy"),
                },
                ["topologyCounters"] = new JsonObject
                {
                    ["safeCopyRootDescriptorCount"] = 2,
                    ["safeCopyExecutableDescriptorCount"] = 2,
                    ["distinctSafeCopyRootPairCount"] = 1,
                    ["sessionRoleDescriptorCount"] = 2,
                    ["newBeaLaunchCount"] = 0,
                    ["processStartCount"] = 0,
                    ["cdbAttachCount"] = 0,
                    ["listenerOpenCount"] = 0,
                    ["invitationCreateCount"] = 0,
                    ["hostJoinControlsEnabledCount"] = 0,
                    ["nPlayerOriginalBinaryRuntimeProof"] = 0,
                },
                ["proofBoundary"] = new JsonObject
                {
                    ["hostJoinControlsMayBeEnabled"] = false,
                    ["baseOnlineMultiplayerReady"] = false,
                    ["acceptedLiveSecondHostCommandSourceProof"] = false,
                    ["acceptedLiveSecondHostRuntimeDeliveryProof"] = false,
                    ["acceptedLiveSecondHostRuntimeCausalityProof"] = false,
                    ["secondHostProof"] = false,
                    ["multiHostLanPlayProof"] = false,
                    ["publicMatchmakingProof"] = false,
                    ["nativeBeaNetcodeProof"] = false,
                    ["activeP3P4OriginalBinaryGameplayProof"] = false,
                    ["moreThanTwoOriginalBinaryRuntimePlayersProof"] = false,
                    ["hostHelperInputSent"] = false,
                    ["gameInputSentByTopologyTool"] = false,
                    ["nPlayerOriginalBinaryRuntimeProof"] = 0,
                    ["maxOriginalBinaryActiveSlotsProven"] = 2,
                    ["acceptedOriginalBinaryGameplaySlots"] = new JsonArray("P1", "P2"),
                    ["metadataOnlySlots"] = new JsonArray("P3", "P4"),
                },
                ["sideEffects"] = new JsonObject
                {
                    ["beaLaunchCount"] = 0,
                    ["processStartCount"] = 0,
                    ["cdbAttachCount"] = 0,
                    ["listenerOpened"] = false,
                    ["invitationCreated"] = false,
                    ["inputSent"] = false,
                    ["patchBytesChanged"] = false,
                    ["publicReleaseCreated"] = false,
                },
                ["requiredFutureEvidence"] = new JsonArray
                {
                    BuildFutureEvidence("distinct-endpoint-command-source-proof", "distinctEndpointIdentity", "privateNonLoopbackCommandSource", "sessionScopedAuthentication", "acceptedP2Command", "noInstalledGameMutation"),
                    BuildFutureEvidence("source-bound-copied-runtime-causality-proof", "acceptedCommandPayloadHashBoundToRuntimeInput", "invitationLifecycleHashBoundToRuntimeInput", "exactPidCdbEvidence", "copiedRuntimeArtifact", "hostHelperDeliveryReceipt"),
                    BuildFutureEvidence("host-join-enablement-composite-proof", "distinct-endpoint-command-source-proof", "source-bound-copied-runtime-causality-proof", "fixtureAndPosthocArtifactsRejected"),
                    BuildFutureEvidence("player-ready-host-join-release-proof", "userFacingHostJoinFlow", "releaseTestedCleanupAndRecovery", "noPublicPrivateProofLeakage"),
                },
                ["nonClaims"] = new JsonObject
                {
                    ["separateScreenNetplayProof"] = false,
                    ["multiHostLanPlayProof"] = false,
                    ["publicMatchmakingProof"] = false,
                    ["nativeBeaNetcodeProof"] = false,
                    ["deterministicSyncProof"] = false,
                    ["rollbackProof"] = false,
                    ["antiCheatProof"] = false,
                    ["coOpVersusRuntimeProof"] = false,
                    ["activeP3P4OriginalBinaryGameplayProof"] = false,
                    ["rebuildParityProof"] = false,
                    ["noNoticeableDifferenceProof"] = false,
                },
                ["releaseBoundary"] = new JsonObject
                {
                    ["privateProofReleaseExcludedByPolicy"] = true,
                    ["privateArtifactContentPublished"] = false,
                    ["copiedExecutablePublished"] = false,
                    ["publicHostOrMatchmakingEndpointPublished"] = false,
                    ["installedGameMutationAllowed"] = false,
                    ["secretsSerialized"] = false,
                },
            };
        }

        private static JsonObject BuildSafeCopyDescriptor(
            string role,
            string rootLabel,
            string rootFingerprint,
            string contentManifestSha256,
            string copiedExecutableLabel,
            string runtimeRole)
        {
            return new JsonObject
            {
                ["role"] = role,
                ["safeCopyRootLabel"] = rootLabel,
                ["rootPathPublished"] = false,
                ["absolutePathsSerialized"] = false,
                ["safeCopyRootPathFingerprint"] = rootFingerprint,
                ["safeCopyContentManifestSha256"] = contentManifestSha256,
                ["copiedExecutableLabel"] = copiedExecutableLabel,
                ["executableRelativePath"] = "BEA.exe",
                ["executableSha256"] = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
                ["sourceRootLabel"] = "selected-game-root-read-only",
                ["appOwnedRootRequired"] = true,
                ["separateRootRequired"] = true,
                ["launchAllowedByThisRung"] = false,
                ["installedGameMutationAllowed"] = false,
                ["originalExecutableMutationAllowed"] = false,
                ["steamInstallWriteAllowed"] = false,
                ["runtimeRole"] = runtimeRole,
            };
        }

        private static JsonObject BuildFutureEvidence(string id, params string[] mustProve)
        {
            JsonArray rows = [];
            foreach (string row in mustProve)
            {
                rows.Add(row);
            }

            return new JsonObject
            {
                ["id"] = id,
                ["mustProve"] = rows,
            };
        }
    }
}
