namespace OnslaughtCareerEditor.UiTests;

internal static class SaveLabNativeEvidenceContract
{
    internal const int SchemaVersion = 1;
    internal const int ArtifactLength = 10_004;
    internal const int DisplayableGoodieCount = 233;
    internal const int SyntheticOptionsVersionWord = 0x4BD1;
    internal const string InteractionMode =
        "UIA Value/Toggle/ExpandCollapse/Scroll/ScrollItem/Selection/Focus/Invoke; no keyboard or pointer synthesis";
    internal const string TrackedSaveFixtureSha256 =
        "0C17E47DB9D666E9B26EF88D43D0A25E7CBFBF4F88C8005CC748965050E506FB";
    internal const string SyntheticOptionsSha256 =
        "A922C6BCA412DB45AED3FCCBE926B6383C039CCF3778C4558D299D1D3C466D99";
}

internal sealed record SaveLabAppIdentityEvidence(
    int ProcessId,
    DateTime ProcessStartTimeUtc,
    string ExecutablePath,
    string ExecutableSha256,
    string ProductAssemblyPath,
    string ProductAssemblySha256,
    long MainWindowHandle,
    long UiaNativeWindowHandle,
    int WindowOwnerProcessId);

internal sealed record SaveLabFocusObservation(
    string AutomationId,
    int ProcessId,
    long MainWindowHandle,
    int X,
    int Y,
    int Width,
    int Height,
    bool HasKeyboardFocus);

internal sealed record SaveLabCaptureEvidence(
    string Workflow,
    string Phase,
    string FocusAutomationId,
    string RelativeFileName,
    string Sha256,
    int Width,
    int Height,
    SaveLabAppIdentityEvidence Identity,
    IReadOnlyList<GuidedSaveVisualMarker> Markers,
    SaveLabFocusObservation FocusBeforeCapture,
    SaveLabFocusObservation FocusAfterCapture);

internal sealed record SaveLabWorkflowEvidence(
    string Workflow,
    SaveLabAppIdentityEvidence Identity,
    string InputRelativePath,
    string InputSha256Before,
    string InputSha256After,
    string OutputRelativePath,
    string OutputSha256,
    int OutputLength,
    bool InputPreserved,
    bool OutputValidated,
    string Readback);

internal sealed record SyntheticOptionsEvidence(
    int Length,
    int VersionWord,
    string Sha256);

internal sealed record SaveLabAcceptanceManifest(
    int SchemaVersion,
    string HarnessRunId,
    string InteractionMode,
    string TrackedSaveFixtureSha256,
    SyntheticOptionsEvidence SyntheticOptions,
    IReadOnlyList<SaveLabCaptureEvidence> Captures,
    IReadOnlyList<SaveLabWorkflowEvidence> Workflows);
