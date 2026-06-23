using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed record GameProfileRegisteredProcess(
        GameProfileManagedProcess Process,
        string AppOwnedProfilesRoot);

    public sealed class GameProfileManagedProcessRegistry
    {
        public const string LeaseFileName = "onslaught-managed-processes.json";
        public const string LeaseSchemaVersion = "winui-managed-safe-copy-processes.v1";

        private readonly object _gate = new();
        private readonly Dictionary<int, GameProfileRegisteredProcess> _processes = new();
        private readonly string? _leasePath;
        private readonly string? _leaseProfilesRoot;

        public GameProfileManagedProcessRegistry(string? leasePath = null)
        {
            _leasePath = string.IsNullOrWhiteSpace(leasePath)
                ? null
                : Path.GetFullPath(leasePath);
            _leaseProfilesRoot = _leasePath is null
                ? null
                : Path.GetDirectoryName(_leasePath);

            LoadPersistedLeases();
        }

        public IReadOnlyList<GameProfileRegisteredProcess> Snapshot()
        {
            lock (_gate)
            {
                return _processes.Values
                    .OrderBy(row => row.Process.StartedAt)
                    .ToArray();
            }
        }

        public bool TryGetLatest(out GameProfileRegisteredProcess registered)
        {
            lock (_gate)
            {
                registered = _processes.Values
                    .OrderByDescending(row => row.Process.StartedAt)
                    .FirstOrDefault()!;
                return registered is not null;
            }
        }

        public void Register(GameProfileManagedProcess process, string appOwnedProfilesRoot)
        {
            if (string.IsNullOrWhiteSpace(appOwnedProfilesRoot))
                throw new InvalidOperationException("A managed playable copied game folder process requires an app-owned profile root.");

            if (!LeaseRootMatches(appOwnedProfilesRoot))
                throw new InvalidOperationException("A managed playable copied game folder process root must match the registry lease root.");

            if (!TryBuildRegisteredProcess(process, appOwnedProfilesRoot, out GameProfileRegisteredProcess registered))
                throw new InvalidOperationException("A managed playable copied game folder process must point at BEA.exe under the app-owned playable copied game folder root.");

            lock (_gate)
            {
                _processes[registered.Process.ProcessId] = registered;
                PersistLeasesNoThrow();
            }
        }

        public void Forget(GameProfileManagedProcess process)
        {
            lock (_gate)
            {
                _processes.Remove(process.ProcessId);
                PersistLeasesNoThrow();
            }
        }

        public GameProfileStopResult Stop(
            GameProfileManagedProcess process,
            IGameProfileProcessRunner? runner = null,
            TimeSpan? gracefulTimeout = null)
        {
            GameProfileRegisteredProcess registered;
            lock (_gate)
            {
                if (!_processes.TryGetValue(process.ProcessId, out registered!))
                {
                    return new GameProfileStopResult(false, process.ProcessId, "Playable copied game folder process is not registered with this app session.");
                }
            }

            GameProfileStopResult result = GameProfileRuntimeService.StopCopiedProfile(
                registered.Process,
                registered.AppOwnedProfilesRoot,
                runner,
                gracefulTimeout);

            if (result.Success)
            {
                Forget(registered.Process);
            }

            return result;
        }

        public IReadOnlyList<GameProfileStopResult> StopAll(
            IGameProfileProcessRunner? runner = null,
            TimeSpan? gracefulTimeout = null)
        {
            GameProfileRegisteredProcess[] snapshot;
            lock (_gate)
            {
                snapshot = _processes.Values.ToArray();
            }

            var results = new List<GameProfileStopResult>();
            foreach (GameProfileRegisteredProcess registered in snapshot)
            {
                results.Add(Stop(registered.Process, runner, gracefulTimeout));
            }

            return results;
        }

        private void LoadPersistedLeases()
        {
            if (string.IsNullOrWhiteSpace(_leasePath) || !File.Exists(_leasePath))
                return;

            bool shouldRewrite = false;
            try
            {
                using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(_leasePath));
                JsonElement root = doc.RootElement;
                string? schemaVersion = root.TryGetProperty("schemaVersion", out JsonElement schemaEl)
                    ? schemaEl.GetString()
                    : null;
                if (!string.Equals(schemaVersion, LeaseSchemaVersion, StringComparison.Ordinal))
                {
                    shouldRewrite = true;
                    throw new InvalidOperationException("Managed playable copied game folder lease schema is stale.");
                }

                if (!root.TryGetProperty("processes", out JsonElement processesEl) ||
                    processesEl.ValueKind != JsonValueKind.Array)
                {
                    shouldRewrite = true;
                    throw new InvalidOperationException("Managed playable copied game folder lease is missing process rows.");
                }

                lock (_gate)
                {
                    foreach (JsonElement processEl in processesEl.EnumerateArray())
                    {
                        if (!TryParsePersistedLease(processEl, out GameProfileManagedProcess? process, out string appOwnedProfilesRoot) ||
                            process is null ||
                            !LeaseRootMatches(appOwnedProfilesRoot) ||
                            !TryBuildRegisteredProcess(process, appOwnedProfilesRoot, out GameProfileRegisteredProcess registered))
                        {
                            shouldRewrite = true;
                            continue;
                        }

                        _processes[registered.Process.ProcessId] = registered;
                    }

                    if (shouldRewrite)
                        PersistLeasesNoThrow();
                }
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or JsonException or InvalidOperationException)
            {
                lock (_gate)
                {
                    _processes.Clear();
                    PersistLeasesNoThrow();
                }
            }
        }

        private static bool TryParsePersistedLease(
            JsonElement processEl,
            out GameProfileManagedProcess? process,
            out string appOwnedProfilesRoot)
        {
            process = null;
            appOwnedProfilesRoot = string.Empty;

            if (!TryGetInt32(processEl, "processId", out int processId) || processId <= 0 ||
                !TryGetString(processEl, "executablePath", out string executablePath) ||
                !TryGetString(processEl, "workingDirectory", out string workingDirectory) ||
                !TryGetString(processEl, "manifestPath", out string manifestPath) ||
                !TryGetString(processEl, "appOwnedProfilesRoot", out appOwnedProfilesRoot) ||
                !TryGetDateTimeOffset(processEl, "startedAt", out DateTimeOffset startedAt))
            {
                return false;
            }

            string[] arguments = Array.Empty<string>();
            if (processEl.TryGetProperty("arguments", out JsonElement argsEl) &&
                argsEl.ValueKind == JsonValueKind.Array)
            {
                arguments = argsEl.EnumerateArray()
                    .Where(argEl => argEl.ValueKind == JsonValueKind.String)
                    .Select(argEl => argEl.GetString())
                    .Where(arg => !string.IsNullOrWhiteSpace(arg))
                    .Select(arg => arg!)
                    .ToArray();
            }

            process = new GameProfileManagedProcess(
                processId,
                executablePath,
                workingDirectory,
                arguments,
                startedAt,
                manifestPath);
            return true;
        }

        private static bool TryGetString(JsonElement el, string propertyName, out string value)
        {
            value = string.Empty;
            if (!el.TryGetProperty(propertyName, out JsonElement propertyEl) ||
                propertyEl.ValueKind != JsonValueKind.String)
            {
                return false;
            }

            value = propertyEl.GetString() ?? string.Empty;
            return !string.IsNullOrWhiteSpace(value);
        }

        private static bool TryGetInt32(JsonElement el, string propertyName, out int value)
        {
            value = 0;
            return el.TryGetProperty(propertyName, out JsonElement propertyEl) &&
                propertyEl.ValueKind == JsonValueKind.Number &&
                propertyEl.TryGetInt32(out value);
        }

        private static bool TryGetDateTimeOffset(JsonElement el, string propertyName, out DateTimeOffset value)
        {
            value = default;
            return el.TryGetProperty(propertyName, out JsonElement propertyEl) &&
                propertyEl.ValueKind == JsonValueKind.String &&
                DateTimeOffset.TryParse(propertyEl.GetString(), out value);
        }

        private static bool TryBuildRegisteredProcess(
            GameProfileManagedProcess process,
            string appOwnedProfilesRoot,
            out GameProfileRegisteredProcess registered)
        {
            registered = null!;
            try
            {
                if (process.ProcessId <= 0 ||
                    string.IsNullOrWhiteSpace(appOwnedProfilesRoot) ||
                    string.IsNullOrWhiteSpace(process.ExecutablePath) ||
                    string.IsNullOrWhiteSpace(process.WorkingDirectory) ||
                    string.IsNullOrWhiteSpace(process.ManifestPath))
                {
                    return false;
                }

                string appRoot = NormalizeExistingDirectory(appOwnedProfilesRoot);
                string workingDirectory = NormalizeExistingDirectory(process.WorkingDirectory);
                if (!IsStrictlyUnderRoot(workingDirectory, appRoot))
                    return false;

                string executablePath = Path.GetFullPath(process.ExecutablePath);
                string manifestPath = Path.GetFullPath(process.ManifestPath);
                string expectedExePath = Path.GetFullPath(Path.Combine(workingDirectory, "BEA.exe"));
                string expectedManifestPath = Path.GetFullPath(Path.Combine(workingDirectory, "onslaught-profile-manifest.json"));
                if (!string.Equals(executablePath, expectedExePath, StringComparison.OrdinalIgnoreCase) ||
                    !string.Equals(manifestPath, expectedManifestPath, StringComparison.OrdinalIgnoreCase) ||
                    !File.Exists(executablePath) ||
                    !File.Exists(manifestPath))
                {
                    return false;
                }

                RejectExistingReparseAncestors(appRoot, "app-owned playable copied game folder root");
                RejectExistingReparseAncestors(workingDirectory, "managed playable copied game folder");
                RejectReparsePoint(workingDirectory, "managed playable copied game folder");
                RejectReparsePoint(executablePath, "managed playable copied game folder executable");
                RejectReparsePoint(manifestPath, "managed playable copied game folder manifest");

                var normalizedProcess = new GameProfileManagedProcess(
                    process.ProcessId,
                    executablePath,
                    workingDirectory,
                    process.Arguments?.ToArray() ?? Array.Empty<string>(),
                    process.StartedAt,
                    manifestPath);
                registered = new GameProfileRegisteredProcess(normalizedProcess, appRoot);
                return true;
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return false;
            }
        }

        private bool LeaseRootMatches(string appOwnedProfilesRoot)
        {
            if (string.IsNullOrWhiteSpace(_leaseProfilesRoot))
                return true;

            try
            {
                string expectedRoot = NormalizeExistingDirectory(_leaseProfilesRoot);
                string actualRoot = NormalizeExistingDirectory(appOwnedProfilesRoot);
                return string.Equals(expectedRoot, actualRoot, StringComparison.OrdinalIgnoreCase);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                return false;
            }
        }

        private void PersistLeasesNoThrow()
        {
            if (string.IsNullOrWhiteSpace(_leasePath))
                return;

            try
            {
                Directory.CreateDirectory(Path.GetDirectoryName(_leasePath)!);
                var payload = new
                {
                    SchemaVersion = LeaseSchemaVersion,
                    WrittenAt = DateTimeOffset.UtcNow,
                    Processes = _processes.Values
                        .OrderBy(row => row.Process.StartedAt)
                        .Select(row => new
                        {
                            row.Process.ProcessId,
                            row.Process.ExecutablePath,
                            row.Process.WorkingDirectory,
                            Arguments = row.Process.Arguments.ToArray(),
                            row.Process.StartedAt,
                            row.Process.ManifestPath,
                            row.AppOwnedProfilesRoot,
                        })
                        .ToArray(),
                };

                var options = new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                };
                File.WriteAllText(_leasePath, JsonSerializer.Serialize(payload, options));
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or InvalidOperationException)
            {
                // The in-memory registry is still authoritative for this app session.
            }
        }

        private static string NormalizeExistingDirectory(string path)
        {
            if (string.IsNullOrWhiteSpace(path) || !Directory.Exists(path))
                throw new DirectoryNotFoundException("Managed playable copied game folder directory does not exist.");

            return Path.GetFullPath(path)
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        }

        private static bool IsStrictlyUnderRoot(string path, string root)
        {
            string normalizedPath = NormalizeForPrefix(path);
            string normalizedRoot = NormalizeForPrefix(root);
            return !string.Equals(
                    normalizedPath.TrimEnd(Path.DirectorySeparatorChar),
                    normalizedRoot.TrimEnd(Path.DirectorySeparatorChar),
                    StringComparison.OrdinalIgnoreCase) &&
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
                throw new InvalidOperationException($"Managed playable copied game folder registry refuses reparse points in {label}.");
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
}
