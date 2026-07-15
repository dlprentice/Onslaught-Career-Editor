using System.Text.Json;

namespace OnslaughtCareerEditor.UiTests;

internal sealed record HomeFocusDiagnosticEvidence(
    string Stage,
    int Sample,
    string? Target,
    string Outcome,
    bool? FocusVerified,
    string? FocusedAutomationIdAtSample,
    string FinalXamlFocusedAutomationId,
    int InputEpochAtSample);

internal sealed record HomeFocusEndpointObservation(
    int ProcessId,
    string RunId,
    int NavigationGeneration,
    long Sequence,
    int InputEpoch,
    string ActiveTag,
    string FocusedAutomationId);

internal static class HomeFocusEvidenceAcceptance
{
    internal const string EndpointPrefix = "ONSLAUGHT_HOME_FOCUS_ENDPOINT:";

    internal static bool TryReadTerminalDiagnostic(
        IEnumerable<string> lines,
        int expectedProcessId,
        string expectedRunId,
        string state,
        string expectedTarget,
        string expectedAutomationId,
        out HomeFocusDiagnosticEvidence? evidence)
    {
        evidence = null;
        JsonElement? terminal = null;
        try
        {
            foreach (string line in lines.Where(candidate => !string.IsNullOrWhiteSpace(candidate)))
            {
                using JsonDocument document = JsonDocument.Parse(line);
                JsonElement root = document.RootElement;
                if (root.ValueKind != JsonValueKind.Object)
                {
                    return false;
                }

                if (TryGetInt32(root, "ProcessId", out int processId)
                    && processId == expectedProcessId
                    && string.Equals(GetOptionalString(root, "RunId"), expectedRunId, StringComparison.Ordinal))
                {
                    terminal = root.Clone();
                }
            }
        }
        catch (JsonException)
        {
            return false;
        }

        if (terminal is not JsonElement terminalRoot
            || !TryGetInt32(terminalRoot, "InputEpochAtSample", out int inputEpochAtSample)
            || inputEpochAtSample != 0
            || !TryGetInt32(terminalRoot, "Sample", out int sample))
        {
            return false;
        }

        string? target = GetOptionalString(terminalRoot, "Target");
        string? outcome = GetOptionalString(terminalRoot, "Outcome");
        string? sampledAutomationId = GetOptionalString(terminalRoot, "FocusedAutomationIdAtSample");
        string? finalAutomationId = GetOptionalString(terminalRoot, "FinalXamlFocusedAutomationId");
        bool? focusVerified = GetOptionalBoolean(terminalRoot, "FocusVerified");
        bool activelyFocused = string.Equals(target, expectedTarget, StringComparison.Ordinal)
            && string.Equals(outcome, "ContentFocused", StringComparison.Ordinal)
            && focusVerified is true
            && string.Equals(sampledAutomationId, expectedAutomationId, StringComparison.Ordinal);
        bool preservedReadyState = string.Equals(outcome, "UserFocusPreserved", StringComparison.Ordinal);
        bool stateAllowsEvidence = string.Equals(state, "first-run", StringComparison.Ordinal)
            ? activelyFocused
            : string.Equals(state, "ready", StringComparison.Ordinal) && (activelyFocused || preservedReadyState);
        if (!stateAllowsEvidence || !string.Equals(finalAutomationId, expectedAutomationId, StringComparison.Ordinal))
        {
            return false;
        }

        evidence = new HomeFocusDiagnosticEvidence(
            GetOptionalString(terminalRoot, "Stage") ?? string.Empty,
            sample,
            target,
            outcome!,
            focusVerified,
            sampledAutomationId,
            finalAutomationId!,
            inputEpochAtSample);
        return true;
    }

    internal static bool TryReadEndpointStatus(
        string? status,
        int expectedProcessId,
        string expectedRunId,
        string expectedAutomationId,
        out HomeFocusEndpointObservation? observation)
    {
        observation = null;
        if (string.IsNullOrWhiteSpace(status) || !status.StartsWith(EndpointPrefix, StringComparison.Ordinal))
        {
            return false;
        }

        try
        {
            using JsonDocument document = JsonDocument.Parse(status[EndpointPrefix.Length..]);
            JsonElement root = document.RootElement;
            if (!TryGetInt32(root, "ProcessId", out int processId)
                || processId != expectedProcessId
                || !string.Equals(GetOptionalString(root, "RunId"), expectedRunId, StringComparison.Ordinal)
                || !TryGetInt32(root, "NavigationGeneration", out int navigationGeneration)
                || !TryGetInt64(root, "Sequence", out long sequence)
                || sequence <= 0
                || !TryGetInt32(root, "InputEpoch", out int inputEpoch)
                || inputEpoch != 0
                || !string.Equals(GetOptionalString(root, "ActiveTag"), "home", StringComparison.OrdinalIgnoreCase)
                || !string.Equals(GetOptionalString(root, "FocusedAutomationId"), expectedAutomationId, StringComparison.Ordinal))
            {
                return false;
            }

            observation = new HomeFocusEndpointObservation(
                processId,
                expectedRunId,
                navigationGeneration,
                sequence,
                inputEpoch,
                "home",
                expectedAutomationId);
            return true;
        }
        catch (JsonException)
        {
            return false;
        }
    }

    private static string? GetOptionalString(JsonElement root, string propertyName) =>
        root.TryGetProperty(propertyName, out JsonElement value) && value.ValueKind == JsonValueKind.String
            ? value.GetString()
            : null;

    private static bool? GetOptionalBoolean(JsonElement root, string propertyName)
    {
        if (!root.TryGetProperty(propertyName, out JsonElement value))
        {
            return null;
        }

        return value.ValueKind switch
        {
            JsonValueKind.True => true,
            JsonValueKind.False => false,
            _ => null,
        };
    }

    private static bool TryGetInt32(JsonElement root, string propertyName, out int value)
    {
        value = 0;
        return root.TryGetProperty(propertyName, out JsonElement element) && element.TryGetInt32(out value);
    }

    private static bool TryGetInt64(JsonElement root, string propertyName, out long value)
    {
        value = 0;
        return root.TryGetProperty(propertyName, out JsonElement element) && element.TryGetInt64(out value);
    }
}
