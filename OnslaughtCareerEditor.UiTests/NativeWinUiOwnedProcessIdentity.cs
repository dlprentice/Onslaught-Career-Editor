using System.Diagnostics;

namespace OnslaughtCareerEditor.UiTests;

internal sealed record NativeWinUiExecutablePathObservation(
    bool ProcessExited,
    string? ExecutablePath);

internal sealed record NativeWinUiOwnedProcessIdentity(
    int ProcessId,
    DateTime ProcessStartTimeUtc,
    string ExecutablePath)
{
    private const int ExecutablePathReadinessAttempts = 101;
    private static readonly TimeSpan ExecutablePathReadinessInterval = TimeSpan.FromMilliseconds(50);

    internal static NativeWinUiOwnedProcessIdentity Capture(
        int processId,
        string expectedExecutablePath,
        DateTime launchRequestedUtc)
    {
        using Process process = Process.GetProcessById(processId);
        string executablePath = WaitForExecutablePath(
            () =>
            {
                process.Refresh();
                if (process.HasExited)
                {
                    return new NativeWinUiExecutablePathObservation(ProcessExited: true, ExecutablePath: null);
                }

                return new NativeWinUiExecutablePathObservation(
                    ProcessExited: false,
                    process.MainModule?.FileName);
            },
            ExecutablePathReadinessAttempts,
            () => Thread.Sleep(ExecutablePathReadinessInterval));
        process.Refresh();
        DateTime startTimeUtc = process.StartTime.ToUniversalTime();
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

    internal static string WaitForExecutablePath(
        Func<NativeWinUiExecutablePathObservation> observe,
        int maxAttempts,
        Action waitBetweenAttempts)
    {
        ArgumentNullException.ThrowIfNull(observe);
        ArgumentNullException.ThrowIfNull(waitBetweenAttempts);
        ArgumentOutOfRangeException.ThrowIfNegativeOrZero(maxAttempts);

        for (int attempt = 1; attempt <= maxAttempts; attempt++)
        {
            NativeWinUiExecutablePathObservation observation = observe();
            if (observation.ProcessExited)
            {
                throw new InvalidOperationException(
                    "The launched WinUI process exited before its executable path became available.");
            }
            if (!string.IsNullOrWhiteSpace(observation.ExecutablePath))
            {
                return observation.ExecutablePath;
            }
            if (attempt < maxAttempts)
            {
                waitBetweenAttempts();
            }
        }

        throw new InvalidOperationException(
            $"The launched WinUI process executable path remained unavailable after {maxAttempts} bounded readiness attempts.");
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
