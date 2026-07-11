using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

namespace Onslaught___Career_Editor
{
    public sealed record GameProfileControlOptionsRequest(
        string ProfileRoot,
        string AppOwnedProfilesRoot,
        float? MouseSensitivityOverride = null,
        uint? ControllerConfigP1Override = null,
        uint? ControllerConfigP2Override = null,
        bool? InvertWalkerP1Override = null,
        bool? InvertWalkerP2Override = null,
        bool? InvertFlightP1Override = null,
        bool? InvertFlightP2Override = null,
        IReadOnlyList<ConfigurationKeybindRow>? KeybindRows = null);

    public sealed record GameProfileControlOptionsChangeRange(
        int Offset,
        int Length,
        string BeforeHex,
        string AfterHex);

    public sealed record GameProfileControlOptionsBackup(
        string RelativePath,
        long Size,
        string Sha256);

    public sealed record GameProfileControlOptionsResult(
        string OptionsPath,
        float MouseSensitivity,
        uint ControllerConfigP1,
        uint ControllerConfigP2,
        bool InvertWalkerP1,
        bool InvertWalkerP2,
        bool InvertFlightP1,
        bool InvertFlightP2,
        string HashBefore,
        string HashAfter,
        IReadOnlyList<GameProfileControlOptionsChangeRange> ChangedRanges,
        IReadOnlyList<GameProfileControlOptionsBackup> Backups,
        string ManifestPath,
        string ProofStatus,
        string Message);

    public static class GameProfileControlOptionsService
    {
        public const string ManifestFileName = "onslaught-control-options-manifest.json";
        public const string ManifestSchemaVersion = "winui-safe-copy-control-options.v1";
        public const string ProofStatusOptionsByteMaterializedOnly = "options_byte_materialized_only";
        public const float BalancedMouseLookSensitivity = 1.5f;
        public const float SharperMouseLookSensitivity = 2.25f;
        public const float FastMouseLookSensitivity = 3.0f;
        private static readonly float[] s_supportedMouseLookSensitivities =
        {
            BalancedMouseLookSensitivity,
            SharperMouseLookSensitivity,
            FastMouseLookSensitivity,
        };

        public static GameProfileControlOptionsResult ApplyToSafeCopy(GameProfileControlOptionsRequest request)
        {
            bool hasKeybindOverrides = request.KeybindRows is { Count: > 0 } &&
                request.KeybindRows.Any(row =>
                    !string.IsNullOrWhiteSpace(row.Player1Token) ||
                    !string.IsNullOrWhiteSpace(row.Player2Token));

            if (!request.MouseSensitivityOverride.HasValue &&
                !request.ControllerConfigP1Override.HasValue &&
                !request.ControllerConfigP2Override.HasValue &&
                !request.InvertWalkerP1Override.HasValue &&
                !request.InvertWalkerP2Override.HasValue &&
                !request.InvertFlightP1Override.HasValue &&
                !request.InvertFlightP2Override.HasValue &&
                !hasKeybindOverrides)
            {
                throw new InvalidOperationException("Choose at least one safe-copy control option before applying.");
            }

            ValidateControllerConfig(request.ControllerConfigP1Override, "Player 1");
            ValidateControllerConfig(request.ControllerConfigP2Override, "Player 2");
            ValidateMouseSensitivityPreset(request.MouseSensitivityOverride);

            string profileRoot = ValidateProfileRoot(request.ProfileRoot, request.AppOwnedProfilesRoot);
            string manifestPath = ValidateControlOptionsManifestTarget(profileRoot);
            _ = GameProfilePreflightService.BuildLaunchPlan(profileRoot, Array.Empty<string>());
            using FileMutationSafety.AppOwnedProfileMutationAuthorization outputAuthorization =
                FileMutationSafety.AuthorizeAppOwnedProfileRoot(profileRoot, request.AppOwnedProfilesRoot);

            string optionsPath = Path.Combine(profileRoot, "defaultoptions.bea");
            if (!File.Exists(optionsPath))
                throw new FileNotFoundException("Safe game copy is missing defaultoptions.bea.", optionsPath);

            RejectReparsePoint(optionsPath, "safe-copy defaultoptions.bea");
            RejectMultipleHardLinks(optionsPath, "Safe-copy defaultoptions.bea");
            byte[] beforeBytes = File.ReadAllBytes(optionsPath);
            string hashBefore = ComputeSha256(beforeBytes);
            string[] backupsBefore = Directory.GetFiles(profileRoot, "defaultoptions.bea.*.bak");
            string tempOptionsPath = BuildUniqueSiblingPath(profileRoot, "defaultoptions", ".bea");

            try
            {
                PatchResult result = ConfigurationEditorService.PatchConfiguration(new ConfigurationPatchRequest
                {
                    InputPath = optionsPath,
                    OutputPath = tempOptionsPath,
                    MouseSensitivityOverride = request.MouseSensitivityOverride,
                    ControllerConfigP1Override = request.ControllerConfigP1Override,
                    ControllerConfigP2Override = request.ControllerConfigP2Override,
                    InvertWalkerP1Override = request.InvertWalkerP1Override,
                    InvertWalkerP2Override = request.InvertWalkerP2Override,
                    InvertFlightP1Override = request.InvertFlightP1Override,
                    InvertFlightP2Override = request.InvertFlightP2Override,
                    KeybindRows = request.KeybindRows ?? Array.Empty<ConfigurationKeybindRow>(),
                    OutputAuthorization = outputAuthorization
                });
                if (!result.Success)
                    throw new InvalidOperationException(result.Message);

                byte[] patchedBytes = File.ReadAllBytes(tempOptionsPath);
                if (patchedBytes.Length != beforeBytes.Length)
                    throw new InvalidOperationException("Safe-copy defaultoptions.bea size changed during control-options patching.");

                string backupPath = BuildUniqueSiblingPath(profileRoot, "defaultoptions.bea", ".bak");
                File.Copy(optionsPath, backupPath);
                File.Move(tempOptionsPath, optionsPath, overwrite: true);
            }
            finally
            {
                if (File.Exists(tempOptionsPath))
                {
                    File.Delete(tempOptionsPath);
                }
            }

            byte[] afterBytes = File.ReadAllBytes(optionsPath);
            string hashAfter = ComputeSha256(afterBytes);
            IReadOnlyList<GameProfileControlOptionsChangeRange> changedRanges = BuildChangedRanges(beforeBytes, afterBytes);
            string[] backupsAfter = Directory.GetFiles(profileRoot, "defaultoptions.bea.*.bak");
            IReadOnlyList<GameProfileControlOptionsBackup> backups = backupsAfter
                .Except(backupsBefore, StringComparer.OrdinalIgnoreCase)
                .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
                .Select(path => new GameProfileControlOptionsBackup(
                    RelativePath: Path.GetRelativePath(profileRoot, path),
                    Size: new FileInfo(path).Length,
                    Sha256: ComputeSha256(File.ReadAllBytes(path))))
                .ToArray();

            ConfigurationSnapshot snapshot = ConfigurationEditorService.LoadConfigurationSnapshot(optionsPath);
            WriteControlOptionsManifest(
                manifestPath,
                profileRoot,
                optionsPath,
                request,
                snapshot,
                hashBefore,
                hashAfter,
                afterBytes.LongLength,
                changedRanges,
                backups);
            return new GameProfileControlOptionsResult(
                OptionsPath: optionsPath,
                MouseSensitivity: snapshot.MouseSensitivity,
                ControllerConfigP1: snapshot.ControllerConfigP1,
                ControllerConfigP2: snapshot.ControllerConfigP2,
                InvertWalkerP1: snapshot.InvertWalkerP1,
                InvertWalkerP2: snapshot.InvertWalkerP2,
                InvertFlightP1: snapshot.InvertFlightP1,
                InvertFlightP2: snapshot.InvertFlightP2,
                HashBefore: hashBefore,
                HashAfter: hashAfter,
                ChangedRanges: changedRanges,
                Backups: backups,
                ManifestPath: manifestPath,
                ProofStatus: ProofStatusOptionsByteMaterializedOnly,
                Message: "Safe-copy defaultoptions.bea control options were patched with a local backup. This does not prove runtime input feel until the copied game is launched and checked.");
        }

        private static string BuildUniqueSiblingPath(string directory, string prefix, string extension)
        {
            for (int attempt = 0; attempt < 10; attempt++)
            {
                string path = Path.Combine(directory, $"{prefix}.{DateTime.UtcNow:yyyyMMddHHmmssfff}.{Guid.NewGuid():N}{extension}");
                if (!File.Exists(path))
                    return path;
            }

            throw new IOException($"Could not allocate a unique {prefix}{extension} path in {directory}.");
        }

        private static void WriteControlOptionsManifest(
            string manifestPath,
            string profileRoot,
            string optionsPath,
            GameProfileControlOptionsRequest request,
            ConfigurationSnapshot snapshot,
            string hashBefore,
            string hashAfter,
            long optionsSize,
            IReadOnlyList<GameProfileControlOptionsChangeRange> changedRanges,
            IReadOnlyList<GameProfileControlOptionsBackup> backups)
        {
            ValidateControlOptionsManifestTarget(profileRoot);
            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            };
            var manifest = new
            {
                SchemaVersion = ManifestSchemaVersion,
                GeneratedAt = DateTimeOffset.UtcNow,
                Mutation = true,
                TargetPath = Path.GetRelativePath(profileRoot, optionsPath),
                ProofStatus = ProofStatusOptionsByteMaterializedOnly,
                Requested = new
                {
                    MouseSensitivity = request.MouseSensitivityOverride,
                    ControllerConfigP1 = request.ControllerConfigP1Override,
                    ControllerConfigP2 = request.ControllerConfigP2Override,
                    InvertWalkerP1 = request.InvertWalkerP1Override,
                    InvertWalkerP2 = request.InvertWalkerP2Override,
                    InvertFlightP1 = request.InvertFlightP1Override,
                    InvertFlightP2 = request.InvertFlightP2Override,
                    KeybindRows = (request.KeybindRows ?? Array.Empty<ConfigurationKeybindRow>())
                        .Where(row => !string.IsNullOrWhiteSpace(row.Player1Token) || !string.IsNullOrWhiteSpace(row.Player2Token))
                        .Select(row => new
                        {
                            row.GroupLabel,
                            row.ActionLabel,
                            row.EntryId,
                            Player1Token = string.IsNullOrWhiteSpace(row.Player1Token) ? null : row.Player1Token.Trim(),
                            Player2Token = string.IsNullOrWhiteSpace(row.Player2Token) ? null : row.Player2Token.Trim(),
                        })
                        .ToArray(),
                },
                Observed = new
                {
                    snapshot.MouseSensitivity,
                    snapshot.ControllerConfigP1,
                    snapshot.ControllerConfigP2,
                    snapshot.InvertWalkerP1,
                    snapshot.InvertWalkerP2,
                    snapshot.InvertFlightP1,
                    snapshot.InvertFlightP2,
                },
                OptionsSize = optionsSize,
                HashBefore = hashBefore,
                HashAfter = hashAfter,
                ChangedRanges = changedRanges.Select(range => new
                {
                    range.Offset,
                    OffsetHex = $"0x{range.Offset:x}",
                    range.Length,
                    range.BeforeHex,
                    range.AfterHex,
                }).ToArray(),
                Backups = backups,
                ClaimBoundary = "This manifest proves copied defaultoptions.bea byte materialization only; it does not prove improved runtime input feel.",
            };

            string tempPath = Path.Combine(
                Path.GetDirectoryName(manifestPath)!,
                $"{Path.GetFileName(manifestPath)}.{Guid.NewGuid():N}.tmp");
            try
            {
                File.WriteAllText(tempPath, JsonSerializer.Serialize(manifest, options));
                if (File.Exists(manifestPath))
                {
                    File.Replace(tempPath, manifestPath, null, ignoreMetadataErrors: true);
                }
                else
                {
                    File.Move(tempPath, manifestPath);
                }
            }
            finally
            {
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
            }
        }

        private static string ValidateControlOptionsManifestTarget(string profileRoot)
        {
            string manifestPath = Path.Combine(profileRoot, ManifestFileName);
            RejectExistingReparseAncestors(manifestPath, "safe-copy control-options manifest path");
            RejectReparsePoint(manifestPath, "safe-copy control-options manifest");
            RejectMultipleHardLinks(manifestPath, "Safe-copy control-options manifest");
            return manifestPath;
        }

        private static IReadOnlyList<GameProfileControlOptionsChangeRange> BuildChangedRanges(byte[] beforeBytes, byte[] afterBytes)
        {
            if (beforeBytes.Length != afterBytes.Length)
                throw new InvalidOperationException("Safe-copy defaultoptions.bea size changed during control-options patching.");

            var ranges = new List<GameProfileControlOptionsChangeRange>();
            int index = 0;
            while (index < beforeBytes.Length)
            {
                if (beforeBytes[index] == afterBytes[index])
                {
                    index++;
                    continue;
                }

                int start = index;
                while (index < beforeBytes.Length && beforeBytes[index] != afterBytes[index])
                {
                    index++;
                }

                int length = index - start;
                ranges.Add(new GameProfileControlOptionsChangeRange(
                    Offset: start,
                    Length: length,
                    BeforeHex: Convert.ToHexString(beforeBytes.AsSpan(start, length)).ToLowerInvariant(),
                    AfterHex: Convert.ToHexString(afterBytes.AsSpan(start, length)).ToLowerInvariant()));
            }

            return ranges;
        }

        private static string ComputeSha256(byte[] bytes)
        {
            return Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
        }

        private static string ValidateProfileRoot(string profileRoot, string appOwnedProfilesRoot)
        {
            if (string.IsNullOrWhiteSpace(appOwnedProfilesRoot))
                throw new InvalidOperationException("An app-owned safe game copy root is required.");

            if (string.IsNullOrWhiteSpace(profileRoot))
                throw new DirectoryNotFoundException("Safe game copy root does not exist.");

            string resolvedAppRoot = NormalizeExistingDirectory(appOwnedProfilesRoot);
            string resolvedProfileRoot = NormalizeExistingDirectory(profileRoot);
            RejectExistingReparseAncestors(resolvedAppRoot, "app-owned safe game copy root");
            RejectExistingReparseAncestors(resolvedProfileRoot, "safe game copy root");
            RejectReparsePoint(resolvedProfileRoot, "safe game copy root");

            if (!IsSameOrUnderRoot(resolvedProfileRoot, resolvedAppRoot) ||
                string.Equals(resolvedProfileRoot, resolvedAppRoot, StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Safe-copy control options require a generated profile under the app-owned safe game copy root.");
            }

            return resolvedProfileRoot;
        }

        private static void ValidateControllerConfig(uint? value, string label)
        {
            if (!value.HasValue)
                return;

            if (value.Value < 1 || value.Value > 4)
                throw new InvalidOperationException($"{label} controller configuration must be 1, 2, 3, or 4.");
        }

        private static void ValidateMouseSensitivityPreset(float? value)
        {
            if (!value.HasValue)
                return;

            if (!s_supportedMouseLookSensitivities.Any(preset => Math.Abs(value.Value - preset) <= 0.0001f))
                throw new InvalidOperationException("Safe-copy mouse sensitivity preset must be one of 1.5, 2.25, or 3.0.");
        }

        private static string NormalizeExistingDirectory(string path)
        {
            if (!Directory.Exists(path))
                throw new DirectoryNotFoundException($"Directory does not exist: {path}");

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
            if (!File.Exists(path) && !Directory.Exists(path))
                return;

            FileAttributes attributes = File.GetAttributes(path);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"Safe-copy control options refuse reparse points in {label}.");
        }

        private static void RejectMultipleHardLinks(string path, string label)
        {
            if (!OperatingSystem.IsWindows() || !File.Exists(path))
                return;

            uint linkCount = GetWindowsHardLinkCount(path);
            if (linkCount > 1)
                throw new InvalidOperationException($"{label} is hardlinked to another file; refusing to mutate a shared file identity.");
        }

        private static uint GetWindowsHardLinkCount(string path)
        {
            using SafeFileHandle handle = File.OpenHandle(
                path,
                FileMode.Open,
                FileAccess.Read,
                FileShare.ReadWrite | FileShare.Delete);

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException($"Could not inspect hardlink count for safe-copy control options target. Win32 error: {Marshal.GetLastWin32Error()}");

            return info.NumberOfLinks;
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool GetFileInformationByHandle(
            SafeFileHandle hFile,
            out ByHandleFileInformation lpFileInformation);

        [StructLayout(LayoutKind.Sequential)]
        private struct ByHandleFileInformation
        {
            public uint FileAttributes;
            public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
            public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
            public uint VolumeSerialNumber;
            public uint FileSizeHigh;
            public uint FileSizeLow;
            public uint NumberOfLinks;
            public uint FileIndexHigh;
            public uint FileIndexLow;
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
