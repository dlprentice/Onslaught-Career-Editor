using System.Diagnostics;

namespace OnslaughtCareerEditor.UiTests;

internal sealed record NativeWinUiOwnedProcessIdentity(
    int ProcessId,
    DateTime ProcessStartTimeUtc,
    string ExecutablePath)
{
    internal static NativeWinUiOwnedProcessIdentity Capture(
        int processId,
        string expectedExecutablePath,
        DateTime launchRequestedUtc)
    {
        using Process process = Process.GetProcessById(processId);
        process.Refresh();
        DateTime startTimeUtc = process.StartTime.ToUniversalTime();
        string executablePath = process.MainModule?.FileName
            ?? throw new InvalidOperationException("The launched WinUI process executable path is unavailable.");
        var identity = new NativeWinUiOwnedProcessIdentity(
            processId,
            startTimeUtc,
            Path.GetFullPath(expectedExecutablePath));
        identity.Validate(process.Id, startTimeUtc, executablePath);
        if (startTimeUtc < launchRequestedUtc.AddSeconds(-1))
        {
            throw new InvalidOperationException("The launched WinUI process start time predates this launch request.");
        }
        return identity;
    }

    internal void Validate(int processId, DateTime processStartTimeUtc, string executablePath)
    {
        if (processId != ProcessId)
        {
            throw new InvalidOperationException(
                $"The owned WinUI process ID changed from {ProcessId} to {processId}.");
        }
        if (processStartTimeUtc.ToUniversalTime() != ProcessStartTimeUtc)
        {
            throw new InvalidOperationException("The owned WinUI process start time no longer matches its launch receipt.");
        }
        if (!string.Equals(
                Path.GetFullPath(executablePath),
                ExecutablePath,
                StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException("The owned WinUI executable path no longer matches its launch receipt.");
        }
    }
}
