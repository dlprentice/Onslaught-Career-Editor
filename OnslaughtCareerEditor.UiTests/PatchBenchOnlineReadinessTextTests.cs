using System;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class PatchBenchOnlineReadinessTextTests
{
    private static readonly string[] ReflectedOnlineReadinessSourcePaths =
    [
        "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchOnlineReadinessText.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineReadinessTextState.cs",
        "OnslaughtCareerEditor.WinUI/Models/PatchBenchOnlineCompanionSessionTextState.cs",
    ];

    [Test]
    public void Build_MapsReadinessDtoIntoBoundaryTextState()
    {
        OnlineMultiplayerReadinessSummary summary = BuildMinimalReadinessSummary();
        OnlineSecondHostReadinessArtifactSummary secondHostArtifact = BuildSecondHostArtifactSummary();
        OnlineLocalGamepadReadinessArtifactSummary gamepadArtifact = BuildLocalGamepadArtifactSummary();
        OnlineDualSafeCopyTopologyArtifactSummary topologyArtifact = BuildDualSafeCopyTopologyArtifactSummary();

        object text = InvokeBuild(summary, secondHostArtifact, gamepadArtifact, topologyArtifact);

        Assert.Multiple(() =>
        {
            Assert.That(TextProperty(text, "Headline"), Is.EqualTo("Online play is not available yet"));
            Assert.That(TextProperty(text, "Slots"), Does.Contain("local split-screen"));
            Assert.That(TextProperty(text, "MetadataSlots"), Does.Contain("There is no Host or Join workflow"));
            Assert.That(TextProperty(text, "TargetModel"), Does.Contain("Host/Join unavailable"));
            Assert.That(TextProperty(text, "TargetModel"), Does.Contain("local split-screen companion concept only"));
            Assert.That(TextProperty(text, "ProofClass"), Does.Contain("fixture proof class: no online proof"));
            Assert.That(TextProperty(text, "NextProof"), Does.Contain("real second computer or VM"));
            Assert.That(TextProperty(text, "NextProof"), Does.Contain("drives the copied game"));
            Assert.That(
                TextProperty(text, "GateDetails"),
                Is.EqualTo("Technical gates: real second-host command proof and same-run copied-game runtime proof are both still pending."));
            Assert.That(TextProperty(text, "ProofLadder"), Does.Contain("local split-screen"));
            Assert.That(TextProperty(text, "ProofLadder"), Does.Contain("not online proof"));
            Assert.That(TextProperty(text, "CompanionModelDetails"), Does.Contain("no Host/Join or online proof"));
            Assert.That(TextProperty(text, "SecondHostSetupChecklist"), Does.Contain("distinct endpoint command source"));
            Assert.That(TextProperty(text, "BlockedActions"), Does.Contain("Online hosting unavailable"));
            Assert.That(TextProperty(text, "BlockedActions"), Does.Contain("Online joining unavailable"));
            Assert.That(TextProperty(text, "BlockedReasons"), Does.Contain("distinct endpoint proof"));
            Assert.That(TextProperty(text, "BlockedReasons"), Does.Contain("source-bound copied-runtime causality"));
            Assert.That(TextProperty(text, "LiveAttemptStatus"), Does.Contain("not ready for a live command-source run"));
            Assert.That(TextProperty(text, "LiveAttemptStatus"), Does.Contain("Host/Join controls locked"));
            Assert.That(TextProperty(text, "LiveAttemptBlockers"), Does.Contain("source-bound copied-runtime causality missing"));
            Assert.That(TextProperty(text, "LiveAttemptCommands"), Does.Contain("read-only candidate inspection"));
            Assert.That(TextProperty(text, "PromotionLockStatus"), Does.Contain("Online play is not player-ready"));
            Assert.That(TextProperty(text, "PromotionLockStatus"), Does.Contain("Host/Join remain unavailable"));
            Assert.That(TextProperty(text, "PromotionLockStatus"), Does.Contain("real separate-machine input test"));
            Assert.That(TextProperty(text, "PromotionLockStatus"), Does.Contain("copied-game behavior"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("Loaded in-memory public-safe test summary"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("ready for future live command-source review"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("server inputs complete"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("client preflight provided"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("network candidates checked: 3"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("Online play is not player-ready"));
            Assert.That(TextProperty(text, "SecondHostReadinessArtifactStatus"), Does.Contain("Host/Join remain unavailable"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("Loaded in-memory gamepad readiness test summary"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("status=ready-for-hardware-preflight"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("ready for a physical-controller runtime attempt"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("presentGamepadCandidateCount=1"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("registryGamepadCandidateCount=2"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("pnpDeviceCount=3"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("joystickRegistryRowCount=4"));
            Assert.That(TextProperty(text, "GamepadReadinessArtifactStatus"), Does.Contain("hardware preflight only; no BEA DirectInput/runtime proof, visible movement proof, Host/Join, or online proof."));
            Assert.That(TextProperty(text, "DualSafeCopyTopologyArtifactStatus"), Does.Contain("distinct endpoint proof"));
            Assert.That(TextProperty(text, "DualSafeCopyTopologyArtifactStatus"), Does.Contain("Host/Join remain unavailable"));
            Assert.That(
                TextProperty(text, "DualSafeCopyTopologyBoundary"),
                Is.EqualTo("Not online multiplayer: no BEA launch, listener, invitation, remote input, Host/Join controls, distinct endpoint proof, or player-ready netplay."));
            Assert.That(
                TextProperty(text, "DualSafeCopyTopologyNextProofs"),
                Is.EqualTo("Why Host/Join is locked: topology/status only. Host/Join requires both a real VM or second PC command-source proof and source-bound copied-runtime causality in the same run."));
        });
    }

    [Test]
    public void BuildCompanionSession_MapsSafeCopyAndNonClaimDtoIntoBoundaryTextState()
    {
        var summary = new OnlineCompanionSessionReadinessSummary(
            SchemaVersion: "test-companion-readiness.v1",
            SafeCopyManifestStatus: "safe-copy-launch-plan-ready",
            LaunchPlanPreview: "\"BEA.exe\" -skipfmv -level 850",
            MayEnableHostJoin: false,
            BaseOnlineMultiplayerReady: false,
            TryableActions: new[]
            {
                new OnlineMultiplayerTryableAction(
                    "Local multiplayer probe",
                    "-skipfmv -level 850",
                    "Launches only a copied local split-screen setup."),
            },
            BlockedActions: new[]
            {
                new OnlineMultiplayerBlockedAction("Online hosting unavailable", false, "No distinct endpoint proof."),
            },
            NextProofIds: new[]
            {
                "distinct-private-host-command-source-proof",
                "host-runtime-delivery-from-source-bound-distinct-command-source",
            },
            NonClaims: new[]
            {
                "no listener",
                "no invitation",
                "no remote input",
                "no Host/Join controls",
            });

        object text = InvokeBuildCompanionSession(summary);

        Assert.Multiple(() =>
        {
            Assert.That(TextProperty(text, "PrepActionStatus"), Does.Contain("Ready safe-copy action: Local multiplayer probe"));
            Assert.That(TextProperty(text, "PrepActionStatus"), Does.Contain("-skipfmv -level 850"));
            Assert.That(TextProperty(text, "PrepActionStatus"), Does.Contain("local split-screen only"));
            Assert.That(TextProperty(text, "PrepActionStatus"), Does.Contain("not Host/Join or online proof"));
            Assert.That(TextProperty(text, "SessionStatus"), Does.Contain("Safe copy status: safe copy is ready for local launch tests."));
            Assert.That(TextProperty(text, "SessionStatus"), Does.Contain("Host/Join stay off"));
            Assert.That(TextProperty(text, "LaunchPlan"), Does.Contain("Launch plan:"));
            Assert.That(TextProperty(text, "LaunchPlan"), Does.Contain("-level 850"));
            Assert.That(
                TextProperty(text, "NextProofs"),
                Is.EqualTo("Next online work: real second-host command test, then source-bound runtime proof for the copied game."));
            Assert.That(TextProperty(text, "NonClaims"), Does.Contain("Current limits:"));
            Assert.That(TextProperty(text, "NonClaims"), Does.Contain("no network listener"));
            Assert.That(TextProperty(text, "NonClaims"), Does.Contain("no invitation"));
            Assert.That(TextProperty(text, "NonClaims"), Does.Contain("no remote input"));
            Assert.That(TextProperty(text, "NonClaims"), Does.Contain("no Host/Join controls"));
        });
    }

    private static OnlineMultiplayerReadinessSummary BuildMinimalReadinessSummary()
    {
        return new OnlineMultiplayerReadinessSummary(
            SchemaVersion: "test-online-readiness.v1",
            BaseOnlineMultiplayerReady: false,
            MultiHostLanProof: false,
            PublicMatchmakingProof: false,
            NativeBeaNetcodeProof: false,
            ActiveP3P4OriginalBinaryGameplayProof: false,
            PhysicalGamepadRuntimeProof: false,
            AcceptedOriginalBinaryGameplaySlots: Array.Empty<string>(),
            MetadataOnlySlots: new[] { "local split-screen" },
            SecondHostSetupSteps: new[]
            {
                new OnlineMultiplayerSetupStep(
                    "Prepare distinct endpoint command source",
                    "missing",
                    "Use a real VM or second PC before Host/Join can move."),
            },
            SecondHostLiveAttemptReadiness: new OnlineSecondHostLiveAttemptReadiness(
                SchemaVersion: "test-live-readiness.v1",
                ReadyToAttemptHarness: false,
                ReadyForLiveValidationCandidate: false,
                ReadyToRunLiveCommandSource: false,
                ServerCommandInputsComplete: false,
                ClientPreflightProvided: false,
                CandidatePrivateBindAddressCount: 0,
                WslOnHostInterfaceCount: 0,
                HostJoinControlsMayBeEnabled: false,
                AcceptedLiveSecondHostCommandSourceProof: false,
                BaseOnlineMultiplayerReady: false,
                RequiredInputs: Array.Empty<OnlineMultiplayerSetupStep>(),
                BlockingReasons: new[]
                {
                    "distinct endpoint proof missing",
                    "source-bound copied-runtime causality missing",
                },
                SafeCommands: new[] { "read-only candidate inspection" }),
            StatusRows: new[]
            {
                new OnlineMultiplayerStatusRow("Current proof class", "fixture proof class: no online proof"),
                new OnlineMultiplayerStatusRow("Host/Join promotion lock", "Online play is not player-ready; readiness artifacts cannot enable Host/Join."),
            },
            TryableActions: new[]
            {
                new OnlineMultiplayerTryableAction("Local multiplayer probe", "-level 850", "Local split-screen safe-copy probe."),
            },
            BlockedActions: new[]
            {
                new OnlineMultiplayerBlockedAction("Online hosting unavailable", false, "Requires distinct endpoint proof."),
                new OnlineMultiplayerBlockedAction("Online joining unavailable", false, "Requires source-bound copied-runtime causality."),
            },
            ProofGateRows: new[]
            {
                new OnlineMultiplayerProofGateRow("Live command source", "Not accepted."),
                new OnlineMultiplayerProofGateRow("Runtime causality", "Not accepted."),
            },
            ProofLadderRows: new[]
            {
                new OnlineMultiplayerProofLadderRow("local split-screen", "accepted for study", "not online proof"),
                new OnlineMultiplayerProofLadderRow("Host/Join", "locked", "distinct endpoint proof and source-bound copied-runtime causality required"),
            },
            DualSafeCopyTopologyArtifact: null,
            CompanionNetplayTarget: new OnlineCompanionNetplayTarget(
                "local split-screen companion concept only",
                "host role pending",
                "join role pending",
                "technical status only",
                "requires separate-machine proof",
                "no Host/Join or online proof"),
            NonClaims: new[] { "no Host/Join controls", "no online proof" },
            NextProofNeeded: "distinct endpoint proof plus source-bound copied-runtime causality",
            FallbackWithoutSecondHost: "keep Host/Join unavailable");
    }

    private static OnlineSecondHostReadinessArtifactSummary BuildSecondHostArtifactSummary()
    {
        return new OnlineSecondHostReadinessArtifactSummary(
            SchemaVersion: "test-second-host-artifact.v1",
            Status: "ready-command-source-only",
            SourceKind: "in-memory public-safe test",
            ReadyToAttemptHarness: true,
            ReadyForLiveValidationCandidate: true,
            ReadyToRunLiveCommandSource: true,
            ServerCommandInputsComplete: true,
            ClientPreflightProvided: true,
            CandidatePrivateBindAddressCount: 2,
            WslOnHostInterfaceCount: 1);
    }

    private static OnlineLocalGamepadReadinessArtifactSummary BuildLocalGamepadArtifactSummary()
    {
        return new OnlineLocalGamepadReadinessArtifactSummary(
            SchemaVersion: "test-local-gamepad-readiness.v1",
            Status: "ready-for-hardware-preflight",
            SourceKind: "in-memory gamepad readiness test",
            ReadyForPhysicalGamepadRuntimeAttempt: true,
            PresentGamepadCandidateCount: 1,
            RegistryGamepadCandidateCount: 2,
            PnpDeviceCount: 3,
            JoystickRegistryRowCount: 4);
    }

    private static OnlineDualSafeCopyTopologyArtifactSummary BuildDualSafeCopyTopologyArtifactSummary()
    {
        return new OnlineDualSafeCopyTopologyArtifactSummary(
            SchemaVersion: "test-dual-safe-copy-topology.v1",
            Status: "descriptor-only",
            Scope: "same-workstation only",
            SourceKind: "in-memory public-safe test",
            SafeCopyCount: 2,
            Roles: new[] { "host-descriptor", "join-descriptor" },
            SameWorkstationOnly: true,
            SamePhysicalMachineOnly: true,
            SafeCopyRootDescriptorCount: 2,
            SafeCopyExecutableDescriptorCount: 2,
            DistinctSafeCopyRootPairCount: 1,
            BeaLaunchCount: 0,
            ProcessStartCount: 0,
            CdbAttachCount: 0,
            ListenerOpenCount: 0,
            InvitationCreateCount: 0,
            HostJoinControlsEnabledCount: 0,
            RequiredFutureEvidenceIds: new[]
            {
                "distinct-endpoint-proof",
                "source-bound-copied-runtime-causality",
            },
            ClaimBoundary: "not online proof");
    }

    private static object InvokeBuild(
        OnlineMultiplayerReadinessSummary summary,
        OnlineSecondHostReadinessArtifactSummary? secondHostArtifact,
        OnlineLocalGamepadReadinessArtifactSummary? gamepadArtifact,
        OnlineDualSafeCopyTopologyArtifactSummary? topologyArtifact)
    {
        return ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            "Build",
            summary,
            secondHostArtifact,
            gamepadArtifact,
            topologyArtifact);
    }

    private static object InvokeBuildCompanionSession(OnlineCompanionSessionReadinessSummary summary)
    {
        return ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            GetHelperType(),
            "BuildCompanionSession",
            summary);
    }

    private static Type GetHelperType()
    {
        return ReflectedWinUiTestSupport.GetRequiredType(
            "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchOnlineReadinessText",
            ReflectedOnlineReadinessSourcePaths);
    }

    private static string TextProperty(object instance, string propertyName)
    {
        return ReflectedWinUiTestSupport.GetStringProperty(instance, propertyName);
    }
}
