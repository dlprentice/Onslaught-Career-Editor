using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
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
        string Message);

    public interface IGameProfileProcessRunner
    {
        GameProfileProcessStartResult Start(GameProfileProcessStartRequest request);

        GameProfileStopResult Stop(GameProfileManagedProcess process, TimeSpan gracefulTimeout);
    }

    public static class GameProfileRuntimeService
    {
        private static readonly TimeSpan s_defaultStopTimeout = TimeSpan.FromSeconds(3);

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
                throw new InvalidOperationException("An app-owned playable copied game folder root is required.");

            if (string.IsNullOrWhiteSpace(profileRoot))
                throw new DirectoryNotFoundException("Playable copied game folder root does not exist.");

            string resolvedAppRoot = NormalizeExistingDirectory(appOwnedProfilesRoot);
            RejectExistingReparseAncestors(resolvedAppRoot, "app-owned playable copied game folder root");
            string resolvedProfileRoot = NormalizeExistingDirectory(profileRoot);

            if (!IsSameOrUnderRoot(resolvedProfileRoot, resolvedAppRoot) ||
                string.Equals(resolvedProfileRoot, resolvedAppRoot, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Launch/stop requires a managed playable copied game folder generated under the app-owned playable copied game folder root.");
            }

            if (!Directory.Exists(resolvedProfileRoot))
                throw new DirectoryNotFoundException($"Playable copied game folder root does not exist: {resolvedProfileRoot}");

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
    private static readonly TimeSpan s_processStartTolerance = TimeSpan.FromSeconds(2);

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
            try
            {
                using Process running = Process.GetProcessById(process.ProcessId);
                if (!MatchesManagedProcess(running, process))
                {
                    return new GameProfileStopResult(false, process.ProcessId, "Refused to stop a process that no longer matches the managed playable copied game folder record.");
                }

                if (running.HasExited)
                    return new GameProfileStopResult(true, process.ProcessId, "Managed playable copied game folder process had already exited.");

                bool closeSent = false;
                try
                {
                    closeSent = running.CloseMainWindow();
                }
                catch (InvalidOperationException)
                {
                    closeSent = false;
                }

                if (closeSent && running.WaitForExit((int)gracefulTimeout.TotalMilliseconds))
                    return new GameProfileStopResult(true, process.ProcessId, "Managed playable copied game folder process closed normally.");

                if (!running.HasExited)
                {
                    running.Kill(entireProcessTree: true);
                    if (!running.WaitForExit((int)gracefulTimeout.TotalMilliseconds))
                    {
                        return new GameProfileStopResult(false, process.ProcessId, "Managed playable copied game folder process did not exit after stop request.");
                    }
                }

                running.Refresh();
                if (!running.HasExited)
                {
                    return new GameProfileStopResult(false, process.ProcessId, "Managed playable copied game folder process is still running after stop request.");
                }

                return new GameProfileStopResult(true, process.ProcessId, "Managed playable copied game folder process was stopped.");
            }
            catch (ArgumentException)
            {
                return new GameProfileStopResult(true, process.ProcessId, "Managed playable copied game folder process was already gone.");
            }
            catch (InvalidOperationException ex)
            {
                return new GameProfileStopResult(false, process.ProcessId, $"Could not stop managed playable copied game folder process: {ex.Message}");
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
            TimeSpan startDelta = (runningStartedAt.ToUniversalTime() - expected.StartedAt.ToUniversalTime()).Duration();
            if (startDelta > s_processStartTolerance)
                return false;

            if (string.IsNullOrWhiteSpace(modulePath))
                return false;

            return string.Equals(
                Path.GetFullPath(modulePath),
                Path.GetFullPath(expected.ExecutablePath),
                StringComparison.OrdinalIgnoreCase);
        }
    }
}
