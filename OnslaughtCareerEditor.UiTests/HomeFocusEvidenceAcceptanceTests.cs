using System.Text.Json;

namespace OnslaughtCareerEditor.UiTests;

public class HomeFocusEvidenceAcceptanceTests
{
    private const int ProcessId = 4217;
    private const string RunId = "run-4217";

    [Test]
    public void TerminalDiagnostic_AcceptsVerifiedFirstRunFocus()
    {
        string line = Diagnostic(
            target: "Setup",
            outcome: "ContentFocused",
            focusVerified: true,
            sampledAutomationId: "HomeSetupActionButton",
            finalAutomationId: "HomeSetupActionButton");

        bool accepted = HomeFocusEvidenceAcceptance.TryReadTerminalDiagnostic(
            [line],
            ProcessId,
            RunId,
            "first-run",
            "Setup",
            "HomeSetupActionButton",
            out HomeFocusDiagnosticEvidence? evidence);

        Assert.Multiple(() =>
        {
            Assert.That(accepted, Is.True);
            Assert.That(evidence, Is.Not.Null);
            Assert.That(evidence!.Outcome, Is.EqualTo("ContentFocused"));
            Assert.That(evidence.FocusedAutomationIdAtSample, Is.EqualTo("HomeSetupActionButton"));
        });
    }

    [Test]
    public void TerminalDiagnostic_RejectsPreservedFirstRunFocus()
    {
        string line = Diagnostic(
            target: null,
            outcome: "UserFocusPreserved",
            focusVerified: null,
            sampledAutomationId: "HomeNavigationItem",
            finalAutomationId: "HomeSetupActionButton");

        bool accepted = HomeFocusEvidenceAcceptance.TryReadTerminalDiagnostic(
            [line],
            ProcessId,
            RunId,
            "first-run",
            "Setup",
            "HomeSetupActionButton",
            out _);

        Assert.That(accepted, Is.False);
    }

    [Test]
    public void TerminalDiagnostic_AcceptsReadyPreservationWithTransientSampleAndCorrectFinalXamlFocus()
    {
        string line = Diagnostic(
            target: null,
            outcome: "UserFocusPreserved",
            focusVerified: null,
            sampledAutomationId: "HomeNavigationItem",
            finalAutomationId: "HomeOpenPatchBenchButton");

        bool accepted = HomeFocusEvidenceAcceptance.TryReadTerminalDiagnostic(
            [line],
            ProcessId,
            RunId,
            "ready",
            "PatchBench",
            "HomeOpenPatchBenchButton",
            out HomeFocusDiagnosticEvidence? evidence);

        Assert.Multiple(() =>
        {
            Assert.That(accepted, Is.True);
            Assert.That(evidence, Is.Not.Null);
            Assert.That(evidence!.FocusedAutomationIdAtSample, Is.EqualTo("HomeNavigationItem"));
            Assert.That(evidence.FinalXamlFocusedAutomationId, Is.EqualTo("HomeOpenPatchBenchButton"));
        });
    }

    [TestCase("HomeOpenSaveLabButton", 0)]
    [TestCase("HomeOpenPatchBenchButton", 1)]
    public void TerminalDiagnostic_RejectsWrongFinalFocusOrNonzeroInputEpoch(string finalAutomationId, int inputEpoch)
    {
        string line = Diagnostic(
            target: null,
            outcome: "UserFocusPreserved",
            focusVerified: null,
            sampledAutomationId: "HomeNavigationItem",
            finalAutomationId: finalAutomationId,
            inputEpoch: inputEpoch);

        bool accepted = HomeFocusEvidenceAcceptance.TryReadTerminalDiagnostic(
            [line],
            ProcessId,
            RunId,
            "ready",
            "PatchBench",
            "HomeOpenPatchBenchButton",
            out _);

        Assert.That(accepted, Is.False);
    }

    [Test]
    public void TerminalDiagnostic_RejectsStaleRunAndDoesNotFallBackPastBadTerminalRecord()
    {
        string stale = Diagnostic(
            target: "PatchBench",
            outcome: "ContentFocused",
            focusVerified: true,
            sampledAutomationId: "HomeOpenPatchBenchButton",
            finalAutomationId: "HomeOpenPatchBenchButton",
            processId: ProcessId + 1,
            runId: "stale");
        string valid = Diagnostic(
            target: "PatchBench",
            outcome: "ContentFocused",
            focusVerified: true,
            sampledAutomationId: "HomeOpenPatchBenchButton",
            finalAutomationId: "HomeOpenPatchBenchButton");
        string badTerminal = Diagnostic(
            target: "PatchBench",
            outcome: "ContentTimedOut",
            focusVerified: false,
            sampledAutomationId: "HomeNavigationItem",
            finalAutomationId: "HomeNavigationItem");

        bool accepted = HomeFocusEvidenceAcceptance.TryReadTerminalDiagnostic(
            [stale, valid, badTerminal],
            ProcessId,
            RunId,
            "ready",
            "PatchBench",
            "HomeOpenPatchBenchButton",
            out _);

        Assert.That(accepted, Is.False);
    }

    [Test]
    public void TerminalDiagnostic_RejectsMalformedCurrentRunStream()
    {
        bool accepted = HomeFocusEvidenceAcceptance.TryReadTerminalDiagnostic(
            [Diagnostic("PatchBench", "ContentFocused", true, "HomeOpenPatchBenchButton", "HomeOpenPatchBenchButton"), "{not-json"],
            ProcessId,
            RunId,
            "ready",
            "PatchBench",
            "HomeOpenPatchBenchButton",
            out _);

        Assert.That(accepted, Is.False);
    }

    [Test]
    public void EndpointStatus_AcceptsOnlyExactRunProcessHomeFocusAndZeroEpoch()
    {
        string status = HomeFocusEvidenceAcceptance.EndpointPrefix + JsonSerializer.Serialize(new
        {
            ProcessId,
            RunId,
            NavigationGeneration = 1,
            Sequence = 4,
            InputEpoch = 0,
            ActiveTag = "home",
            FocusedAutomationId = "HomeOpenPatchBenchButton",
        });

        bool accepted = HomeFocusEvidenceAcceptance.TryReadEndpointStatus(
            status,
            ProcessId,
            RunId,
            "HomeOpenPatchBenchButton",
            out HomeFocusEndpointObservation? observation);

        Assert.Multiple(() =>
        {
            Assert.That(accepted, Is.True);
            Assert.That(observation, Is.Not.Null);
            Assert.That(observation!.InputEpoch, Is.Zero);
            Assert.That(observation.Sequence, Is.EqualTo(4));
        });
    }

    [TestCase(4218, "run-4217", 0, "home", "HomeOpenPatchBenchButton")]
    [TestCase(4217, "other-run", 0, "home", "HomeOpenPatchBenchButton")]
    [TestCase(4217, "run-4217", 1, "home", "HomeOpenPatchBenchButton")]
    [TestCase(4217, "run-4217", 0, "saves", "HomeOpenPatchBenchButton")]
    [TestCase(4217, "run-4217", 0, "home", "HomeOpenSaveLabButton")]
    public void EndpointStatus_RejectsIdentityEpochPageOrFocusMismatch(
        int processId,
        string runId,
        int inputEpoch,
        string activeTag,
        string focusedAutomationId)
    {
        string status = HomeFocusEvidenceAcceptance.EndpointPrefix + JsonSerializer.Serialize(new
        {
            ProcessId = processId,
            RunId = runId,
            NavigationGeneration = 1,
            Sequence = 4,
            InputEpoch = inputEpoch,
            ActiveTag = activeTag,
            FocusedAutomationId = focusedAutomationId,
        });

        bool accepted = HomeFocusEvidenceAcceptance.TryReadEndpointStatus(
            status,
            ProcessId,
            RunId,
            "HomeOpenPatchBenchButton",
            out _);

        Assert.That(accepted, Is.False);
    }

    private static string Diagnostic(
        string? target,
        string outcome,
        bool? focusVerified,
        string? sampledAutomationId,
        string finalAutomationId,
        int inputEpoch = 0,
        int processId = ProcessId,
        string runId = RunId) => JsonSerializer.Serialize(new
        {
            ProcessId = processId,
            RunId = runId,
            NavigationGeneration = 1,
            Stage = "terminal",
            Sample = 3,
            Target = target,
            SetupApplicability = "NotApplicable",
            Readiness = "Ready",
            TryFocusSucceeded = focusVerified,
            FocusVerified = focusVerified,
            Outcome = outcome,
            FocusedAutomationIdAtSample = sampledAutomationId,
            InputEpochAtSample = inputEpoch,
            FinalXamlFocusedAutomationId = finalAutomationId,
        });
}
