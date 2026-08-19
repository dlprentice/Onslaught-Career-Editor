using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    public sealed record GameProfileLaunchOptions(
        string ProfileRoot,
        string AppOwnedProfilesRoot,
        IReadOnlyList<string>? LaunchArguments = null);

    public sealed record GameProfileProcessStartRequest(
        string FileName,
        string WorkingDirectory,
        IReadOnlyList<string> Arguments,
        string ArgumentString);

    public sealed record GameProfileProcessStartResult(
        int ProcessId,
        DateTimeOffset? StartedAt = null);

    public sealed record GameProfileManagedProcess(
        int ProcessId,
        string ExecutablePath,
        string WorkingDirectory,
        IReadOnlyList<string> Arguments,
        DateTimeOffset StartedAt,
        string ManifestPath);

    public sealed record GameProfileStopResult(
        bool Success,
        int ProcessId,
        string Message,
        bool LiveBeforeStop = false,
        bool StopRequested = false,
        bool CloseRequested = false,
        bool ForceRequested = false,
        bool ExitObserved = false,
        bool AlreadyGone = false,
        DateTimeOffset? ExitTime = null);

    public interface IGameProfileProcessRunner
    {
        GameProfileProcessStartResult Start(GameProfileProcessStartRequest request);

        GameProfileStopResult Stop(GameProfileManagedProcess process, TimeSpan gracefulTimeout);
    }

    /// <summary>
    /// What a read-only look at one process id found. <see cref="StartedAt"/> and
    /// <see cref="MainModulePath"/> are the two identity facts a managed record is
    /// checked against; either being unreadable means the identity cannot be proven,
    /// which is never treated as "still running".
    /// </summary>
    public sealed record GameProfileProcessLivenessProbeResult(
        bool IsRunning,
        DateTimeOffset? StartedAt,
        string? MainModulePath);

    /// <summary>
    /// Reads process facts without changing anything. Implementations must never close,
    /// kill, or signal the process; this exists so liveness stays unit-testable without a
    /// real process and without any presentation or UI-thread dependency.
    /// </summary>
    public interface IGameProfileProcessLivenessProbe
    {
        GameProfileProcessLivenessProbeResult Probe(GameProfileManagedProcess process);
    }

    public static class GameProfileRuntimeService
    {
        public const string StopFailed = "Could not stop that copied game. Nothing was changed.";
        public const string CopyFolderMissing = "That copy folder could not be found.";
        public const string ProfileFolderRequired = "An app-owned profile folder is required.";

        private static readonly TimeSpan s_defaultStopTimeout = TimeSpan.FromSeconds(3);

        /// <summary>
        /// Read-only answer to "is the copied game from this record still running?". This
        /// never closes, kills, or signals anything.
        ///
        /// A process id on its own is never enough, because Windows recycles process ids.
        /// A record counts as live only when a process with that id exists AND its start
        /// time and main module path still match the record - the same identity check the
        /// stop path must pass before it is allowed to close anything. Anything the probe
        /// cannot read counts as not live, which only ever makes the app forget a copy it
        /// was tracking; it can never point a stop at an unrelated process.
        /// </summary>
        public static bool IsManagedProcessLive(
            GameProfileManagedProcess process,
            IGameProfileProcessLivenessProbe? probe = null)
        {
            ArgumentNullException.ThrowIfNull(process);

            if (process.ProcessId <= 0 || string.IsNullOrWhiteSpace(process.ExecutablePath))
                return false;

            GameProfileProcessLivenessProbeResult probed =
                (probe ?? DefaultGameProfileProcessLivenessProbe.Instance).Probe(process);

            if (!probed.IsRunning || probed.StartedAt is null)
                return false;

            return MatchesManagedProcessIdentity(probed.StartedAt.Value, probed.MainModulePath, process);
        }

        /// <summary>
        /// The one identity comparison shared by the stop path and the liveness query, so
        /// the two can never drift apart. Start time is compared to the exact tick: it is
        /// what makes a recycled process id fail to match.
        /// </summary>
        internal static bool MatchesManagedProcessIdentity(
            DateTimeOffset runningStartedAt,
            string? modulePath,
            GameProfileManagedProcess expected)
        {
            if (runningStartedAt.ToUniversalTime().Ticks != expected.StartedAt.ToUniversalTime().Ticks)
                return false;

            if (string.IsNullOrWhiteSpace(modulePath))
                return false;

            try
            {
                return string.Equals(
                    Path.GetFullPath(modulePath),
                    Path.GetFullPath(expected.ExecutablePath),
                    StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception ex) when (ex is ArgumentException or NotSupportedException or IOException)
            {
                return false;
            }
        }

        public static GameProfileManagedProcess LaunchCopiedProfile(
            GameProfileLaunchOptions options,
            IGameProfileProcessRunner? runner = null)
        {
            string profileRoot = ValidateManagedProfileRoot(options.ProfileRoot, options.AppOwnedProfilesRoot, requireGeneratedManifest: true);
            GameProfileLaunchPlan plan = GameProfilePreflightService.BuildLaunchPlan(
                profileRoot,
                options.LaunchArguments ?? Array.Empty<string>());

            var request = new GameProfileProcessStartRequest(
                FileName: plan.ExecutablePath,
                WorkingDirectory: plan.WorkingDirectory,
                Arguments: plan.Arguments.ToArray(),
                ArgumentString: string.Join(" ", plan.Arguments));

            GameProfileProcessStartResult started = (runner ?? DefaultGameProfileProcessRunner.Instance).Start(request);
            if (started.ProcessId <= 0)
                throw new InvalidOperationException("Playable copied game folder launch did not return a valid process id.");

            return new GameProfileManagedProcess(
                ProcessId: started.ProcessId,
                ExecutablePath: plan.ExecutablePath,
                WorkingDirectory: plan.WorkingDirectory,
                Arguments: plan.Arguments.ToArray(),
                StartedAt: started.StartedAt ?? DateTimeOffset.UtcNow,
                ManifestPath: Path.Combine(profileRoot, "onslaught-profile-manifest.json"));
        }

        public static GameProfileStopResult StopCopiedProfile(
            GameProfileManagedProcess process,
            string appOwnedProfilesRoot,
            IGameProfileProcessRunner? runner = null,
            TimeSpan? gracefulTimeout = null)
        {
            string profileRoot = ValidateManagedProfileRoot(process.WorkingDirectory, appOwnedProfilesRoot, requireGeneratedManifest: false);
            string expectedExePath = Path.Combine(profileRoot, "BEA.exe");
            string expectedManifestPath = Path.Combine(profileRoot, "onslaught-profile-manifest.json");

            if (!string.Equals(Path.GetFullPath(process.ExecutablePath), expectedExePath, StringComparison.OrdinalIgnoreCase) ||
                !string.Equals(Path.GetFullPath(process.ManifestPath), expectedManifestPath, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Stop requires a managed playable copied game folder process record.");
            }

            return (runner ?? DefaultGameProfileProcessRunner.Instance).Stop(
                process,
                gracefulTimeout ?? s_defaultStopTimeout);
        }

        private static string ValidateManagedProfileRoot(string profileRoot, string appOwnedProfilesRoot, bool requireGeneratedManifest)
        {
            if (string.IsNullOrWhiteSpace(appOwnedProfilesRoot))
                throw new InvalidOperationException(ProfileFolderRequired);

            if (string.IsNullOrWhiteSpace(profileRoot))
                throw new DirectoryNotFoundException(CopyFolderMissing);

            string resolvedAppRoot = NormalizeExistingDirectory(appOwnedProfilesRoot);
            RejectExistingReparseAncestors(resolvedAppRoot, "app-owned playable copied game folder root");
            string resolvedProfileRoot = NormalizeExistingDirectory(profileRoot);

            if (!IsSameOrUnderRoot(resolvedProfileRoot, resolvedAppRoot) ||
                string.Equals(resolvedProfileRoot, resolvedAppRoot, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Launch/stop requires a managed playable copied game folder generated under the app-owned playable copied game folder root.");
            }

            if (!Directory.Exists(resolvedProfileRoot))
                throw new DirectoryNotFoundException(CopyFolderMissing);

            RejectExistingReparseAncestors(resolvedProfileRoot, "managed playable copied game folder");
            RejectReparsePoint(resolvedProfileRoot, "managed playable copied game folder");

            string exePath = Path.Combine(resolvedProfileRoot, "BEA.exe");
            string manifestPath = Path.Combine(resolvedProfileRoot, "onslaught-profile-manifest.json");
            if (!File.Exists(exePath))
                throw new InvalidOperationException("Managed playable copied game folder requires BEA.exe.");

            RejectReparsePoint(exePath, "managed playable copied game folder executable");
            if (requireGeneratedManifest)
            {
                if (!File.Exists(manifestPath))
                    throw new InvalidOperationException("Managed playable copied game folder requires its generated manifest.");

                RejectReparsePoint(manifestPath, "managed playable copied game folder manifest");
            }

            return resolvedProfileRoot;
        }

        private static string NormalizeExistingDirectory(string path)
        {
            return Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }

        private static bool IsSameOrUnderRoot(string path, string root)
        {
            string normalizedPath = NormalizeForPrefix(path);
            string normalizedRoot = NormalizeForPrefix(root);
            return string.Equals(normalizedPath.TrimEnd(Path.DirectorySeparatorChar), normalizedRoot.TrimEnd(Path.DirectorySeparatorChar), StringComparison.OrdinalIgnoreCase) ||
                normalizedPath.StartsWith(normalizedRoot, StringComparison.OrdinalIgnoreCase);
        }

        private static string NormalizeForPrefix(string path)
        {
            return Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;
        }

        private static void RejectReparsePoint(string path, string label)
        {
            FileAttributes attributes = File.GetAttributes(path);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"Playable copied game folder runtime refuses reparse points in {label}.");
        }

        private static void RejectExistingReparseAncestors(string path, string label)
        {
            string fullPath = Path.GetFullPath(path);
            string? current = Directory.Exists(fullPath)
                ? fullPath
                : Path.GetDirectoryName(fullPath);

            while (!string.IsNullOrWhiteSpace(current))
            {
                if (Directory.Exists(current))
                    RejectReparsePoint(current, label);

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                    break;

                current = parent;
            }
        }
    }

    internal sealed class DefaultGameProfileProcessRunner : IGameProfileProcessRunner
    {
        public static DefaultGameProfileProcessRunner Instance { get; } = new();

        public GameProfileProcessStartResult Start(GameProfileProcessStartRequest request)
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = request.FileName,
                WorkingDirectory = request.WorkingDirectory,
                UseShellExecute = false,
            };
            foreach (string argument in request.Arguments)
            {
                startInfo.ArgumentList.Add(argument);
            }

            Process? process = Process.Start(startInfo);
            if (process is null)
                throw new InvalidOperationException("Playable copied game folder launch did not start a process.");

            DateTimeOffset? startTime = null;
            try
            {
                startTime = new DateTimeOffset(process.StartTime);
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                startTime = DateTimeOffset.UtcNow;
            }

            return new GameProfileProcessStartResult(process.Id, startTime);
        }

        public GameProfileStopResult Stop(GameProfileManagedProcess process, TimeSpan gracefulTimeout)
        {
            double totalTimeoutMilliseconds = gracefulTimeout.TotalMilliseconds;
            if (!double.IsFinite(totalTimeoutMilliseconds) ||
                totalTimeoutMilliseconds < 0 ||
                totalTimeoutMilliseconds > int.MaxValue)
            {
                return new GameProfileStopResult(false, process.ProcessId, "Could not stop managed playable copied game folder process: stop timeout must be a finite nonnegative millisecond value no greater than Int32.MaxValue.");
            }

            int stopTimeoutMilliseconds = (int)totalTimeoutMilliseconds;
            Process running;
            try
            {
                running = Process.GetProcessById(process.ProcessId);
            }
            catch (ArgumentException)
            {
                return new GameProfileStopResult(true, process.ProcessId, "Managed playable copied game folder process was already gone before an exact stop handle could be acquired.", AlreadyGone: true);
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                return new GameProfileStopResult(false, process.ProcessId, GameProfileRuntimeService.StopFailed);
            }

            using (running)
            {
                try
                {
                    bool exactProcessHandlePinned = false;
                    var exactProcessHandle = running.SafeHandle;
                    try
                    {
                        exactProcessHandle.DangerousAddRef(ref exactProcessHandlePinned);

                        if (!MatchesManagedProcess(running, process))
                        {
                            return new GameProfileStopResult(false, process.ProcessId, "Refused to stop a process that no longer matches the managed playable copied game folder record.");
                        }

                        if (running.HasExited)
                            return new GameProfileStopResult(
                                true,
                                process.ProcessId,
                                "Managed playable copied game folder process exited before the exact stop request.",
                                AlreadyGone: true);

                        bool liveBeforeStop = true;
                        bool closeSent = false;
                        try
                        {
                            closeSent = running.CloseMainWindow();
                        }
                        catch (InvalidOperationException)
                        {
                            closeSent = false;
                        }

                        if (closeSent && running.WaitForExit(stopTimeoutMilliseconds))
                        {
                            if (!TryGetExactExitTime(running, out DateTimeOffset exitTime))
                                return new GameProfileStopResult(false, process.ProcessId, "Managed playable copied game folder process exited but its exact exit time could not be read.", liveBeforeStop, true, true, false, true);

                            return new GameProfileStopResult(true, process.ProcessId, "Managed playable copied game folder process closed normally.", liveBeforeStop, true, true, false, true, false, exitTime);
                        }

                        bool forceRequested = false;
                        if (!running.HasExited)
                        {
                            forceRequested = true;
                            running.Kill(entireProcessTree: false);
                            if (!running.WaitForExit(stopTimeoutMilliseconds))
                            {
                                return new GameProfileStopResult(false, process.ProcessId, "Managed playable copied game folder process did not exit after stop request.", liveBeforeStop, true, closeSent, forceRequested);
                            }
                        }

                        bool stopRequested = closeSent || forceRequested;

                        running.Refresh();
                        if (!running.HasExited)
                        {
                            return new GameProfileStopResult(false, process.ProcessId, "Managed playable copied game folder process is still running after stop request.", liveBeforeStop, stopRequested, closeSent, forceRequested);
                        }

                        if (!TryGetExactExitTime(running, out DateTimeOffset stoppedAt))
                            return new GameProfileStopResult(false, process.ProcessId, "Managed playable copied game folder process stopped but its exact exit time could not be read.", liveBeforeStop, stopRequested, closeSent, forceRequested, true);

                        return new GameProfileStopResult(stopRequested, process.ProcessId, stopRequested ? "Managed playable copied game folder process was stopped." : "Managed playable copied game folder process exited before a stop request was sent.", liveBeforeStop, stopRequested, closeSent, forceRequested, true, !stopRequested, stoppedAt);
                    }
                    finally
                    {
                        if (exactProcessHandlePinned)
                            exactProcessHandle.DangerousRelease();
                    }
                }
                catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or System.ComponentModel.Win32Exception)
                {
                    return new GameProfileStopResult(false, process.ProcessId, GameProfileRuntimeService.StopFailed);
                }
            }
        }

        private static bool MatchesManagedProcess(Process running, GameProfileManagedProcess expected)
        {
            DateTimeOffset runningStartedAt;
            try
            {
                runningStartedAt = new DateTimeOffset(running.StartTime);
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                return false;
            }

            string? modulePath;
            try
            {
                modulePath = running.MainModule?.FileName;
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                return false;
            }

            return MatchesManagedProcessIdentity(runningStartedAt, modulePath, expected);
        }

        private static bool MatchesManagedProcessIdentity(
            DateTimeOffset runningStartedAt,
            string? modulePath,
            GameProfileManagedProcess expected)
        {
            return GameProfileRuntimeService.MatchesManagedProcessIdentity(runningStartedAt, modulePath, expected);
        }

        private static bool TryGetExactExitTime(Process process, out DateTimeOffset exitTime)
        {
            try
            {
                process.Refresh();
                if (!process.HasExited)
                {
                    exitTime = default;
                    return false;
                }

                exitTime = new DateTimeOffset(process.ExitTime).ToUniversalTime();
                return true;
            }
            catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                exitTime = default;
                return false;
            }
        }
    }

    /// <summary>
    /// Looks at a process id and reports only what it can read. It opens the process for
    /// reading and pins the handle while it reads, so the id cannot be recycled underneath
    /// the two identity facts it collects. It never closes, kills, or signals anything.
    /// </summary>
    internal sealed class DefaultGameProfileProcessLivenessProbe : IGameProfileProcessLivenessProbe
    {
        private static readonly GameProfileProcessLivenessProbeResult s_notRunning = new(false, null, null);

        public static DefaultGameProfileProcessLivenessProbe Instance { get; } = new();

        public GameProfileProcessLivenessProbeResult Probe(GameProfileManagedProcess process)
        {
            ArgumentNullException.ThrowIfNull(process);

            Process running;
            try
            {
                running = Process.GetProcessById(process.ProcessId);
            }
            catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or System.ComponentModel.Win32Exception)
            {
                return s_notRunning;
            }

            using (running)
            {
                bool exactProcessHandlePinned = false;
                System.Runtime.InteropServices.SafeHandle? exactProcessHandle = null;
                try
                {
                    exactProcessHandle = running.SafeHandle;
                    exactProcessHandle.DangerousAddRef(ref exactProcessHandlePinned);

                    if (running.HasExited)
                        return s_notRunning;

                    return new GameProfileProcessLivenessProbeResult(
                        true,
                        new DateTimeOffset(running.StartTime),
                        running.MainModule?.FileName);
                }
                catch (Exception ex) when (ex is ArgumentException or InvalidOperationException or ObjectDisposedException or System.ComponentModel.Win32Exception)
                {
                    return s_notRunning;
                }
                finally
                {
                    if (exactProcessHandlePinned)
                        exactProcessHandle!.DangerousRelease();
                }
            }
        }
    }
}
