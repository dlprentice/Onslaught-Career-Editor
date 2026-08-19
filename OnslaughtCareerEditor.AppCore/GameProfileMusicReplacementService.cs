using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

namespace OnslaughtCareerEditor.AppCore
{
    public sealed record GameProfileMusicReplacementOptions(
        string SafeGameRoot,
        string AppOwnedProfilesRoot,
        string TargetMusicFileName,
        string ReplacementOggPath);

    public sealed record GameProfileMusicSwapPreset(
        string Id,
        string DisplayName,
        string Description,
        string TargetMusicFileName,
        string ReplacementMusicFileName,
        string ProofStatus,
        string ClaimBoundary);

    public sealed record GameProfileMusicReplacementResult(
        string SchemaVersion,
        DateTimeOffset GeneratedAt,
        bool Mutation,
        string TargetMusicFileName,
        string TargetRelativePath,
        string BackupRelativePath,
        string TargetPath,
        string BackupPath,
        string ManifestPath,
        long OriginalSize,
        string OriginalSha256,
        long ReplacementSize,
        string ReplacementSha256);

    public sealed record GameProfileMusicReplacementRestoreOptions(
        string SafeGameRoot,
        string AppOwnedProfilesRoot);

    public sealed record GameProfileMusicReplacementRestoreResult(
        bool Success,
        string TargetMusicFileName,
        string Message);

    public sealed record GameProfileMusicTrack(
        string FileName,
        string RelativePath,
        long Size);

    public static class GameProfileMusicReplacementService
    {
        public const string SchemaVersion = "winui-safe-copy-music-replacement.v1";
        public const string ManifestFileName = "onslaught-music-replacement-manifest.json";
        public const string UseBea02ForBea01PresetId = "use-bea02-for-bea01";
        public const string UseBea01ForBea02PresetId = "use-bea01-for-bea02";
        public const string UseBea02ForBea04PresetId = "use-bea02-for-bea04";
        public const string MusicFolderMissing = "That copy does not have a Music folder.";
        public const string CopyFolderMissing = "That copy folder could not be found.";
        public const string ProfileFolderMissing = "That app-owned profile folder could not be found.";
        public const string TargetMusicFileMissing = "That target music file could not be found.";
        public const string ReplacementMusicFileMissing = "That replacement music file could not be found.";
        public const string MusicBackupMissing = "That music backup file could not be found.";
        public const string CopyCannotUseLink = "That copy cannot use a shortcut or link.";
        public const string FileCannotShareData = "That file cannot share its data with another file.";
        public const string MusicSwapPresetUnknown = "That music swap is not available.";
        public const string MusicFileTooSmall = "That music file is too small.";
        public const string MusicFileNotOgg = "That music file is not an OGG.";
        public const string MusicDetailsUnsupported = "That copy's music details are out of date.";
        public const string MusicDetailsWrongTarget = "That copy's music details do not match the music file.";
        public const string MusicBackupMismatch = "That copy's music backup no longer matches.";
        public const string MusicRestoreMismatch = "That copy's restored music file no longer matches.";
        public const string MusicRestored = "That music file was restored.";
        private const string BackupSuffix = ".original.backup";

        private static readonly GameProfileMusicSwapPreset[] s_musicSwapPresets =
        {
            new(
                UseBea02ForBea01PresetId,
                "Use BEA_02 for BEA_01",
                "Stages copied BEA_02(Master).ogg over copied BEA_01(Master).ogg.",
                "BEA_01(Master).ogg",
                "BEA_02(Master).ogg",
                "Copied-track staging and restore contract only; runtime playback is not proven.",
                "Mutates only the generated safe copy's data/Music folder and writes a restore manifest; does not alter the installed game, prove cue selection, or prove audible output."),
            new(
                UseBea01ForBea02PresetId,
                "Use BEA_01 for BEA_02",
                "Stages copied BEA_01(Master).ogg over copied BEA_02(Master).ogg.",
                "BEA_02(Master).ogg",
                "BEA_01(Master).ogg",
                "Copied-track staging and restore contract only; runtime playback is not proven.",
                "Mutates only the generated safe copy's data/Music folder and writes a restore manifest; does not alter the installed game, prove cue selection, or prove audible output."),
            new(
                UseBea02ForBea04PresetId,
                "Use BEA_02 for BEA_04",
                "Stages copied BEA_02(Master).ogg over copied BEA_04(Master).ogg for the level-100 music-selection path.",
                "BEA_04(Master).ogg",
                "BEA_02(Master).ogg",
                "Copied-track staging plus focused level-100 selection/decode proof; audible output is not proven.",
                "Mutates only the generated safe copy's data/Music folder and writes a restore manifest; level-100 CDB evidence observed the staged BEA_04 path reaching selection/decode, but this does not alter the installed game, prove audible output, prove all music cues, or prove rebuild parity."),
        };

        public static IReadOnlyList<GameProfileMusicSwapPreset> GetSafeCopyMusicSwapPresets()
        {
            return s_musicSwapPresets.ToArray();
        }

        public static GameProfileMusicSwapPreset GetSafeCopyMusicSwapPreset(string presetId)
        {
            GameProfileMusicSwapPreset? preset = s_musicSwapPresets.FirstOrDefault(preset =>
                string.Equals(preset.Id, presetId, StringComparison.OrdinalIgnoreCase));
            return preset ?? throw new InvalidOperationException(MusicSwapPresetUnknown);
        }

        public static GameProfileMusicReplacementOptions BuildSafeCopyMusicSwapPresetOptions(
            string safeGameRoot,
            string appOwnedProfilesRoot,
            string presetId)
        {
            string safeRoot = ValidateSafeGameRoot(safeGameRoot, appOwnedProfilesRoot);
            GameProfileMusicSwapPreset preset = GetSafeCopyMusicSwapPreset(presetId);
            string targetFileName = ValidateTargetMusicFileName(preset.TargetMusicFileName);
            string replacementFileName = ValidateTargetMusicFileName(preset.ReplacementMusicFileName);
            string musicDirectory = Path.Combine(safeRoot, "data", "Music");
            if (!Directory.Exists(musicDirectory))
                throw new DirectoryNotFoundException(MusicFolderMissing);

            string targetPath = Path.Combine(musicDirectory, targetFileName);
            string replacementPath = Path.Combine(musicDirectory, replacementFileName);
            if (!File.Exists(targetPath))
                throw new FileNotFoundException(TargetMusicFileMissing);
            if (!File.Exists(replacementPath))
                throw new FileNotFoundException(ReplacementMusicFileMissing);
            if (string.Equals(Path.GetFullPath(targetPath), Path.GetFullPath(replacementPath), StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Safe-copy music swap preset target and replacement must be different copied tracks.");

            RejectExistingReparseAncestors(targetPath, "preset target music path");
            RejectExistingReparseAncestors(replacementPath, "preset replacement music path");
            RejectReparsePoint(targetPath, "preset target music file");
            RejectReparsePoint(replacementPath, "preset replacement music file");
            ValidateOggHeader(targetPath, "Preset target music file");
            ValidateOggHeader(replacementPath, "Preset replacement music file");

            return new GameProfileMusicReplacementOptions(
                safeRoot,
                appOwnedProfilesRoot,
                targetFileName,
                replacementPath);
        }

        public static IReadOnlyList<GameProfileMusicTrack> ListSafeCopyMusicTracks(string safeGameRoot, string appOwnedProfilesRoot)
        {
            string safeRoot = ValidateSafeGameRoot(safeGameRoot, appOwnedProfilesRoot);
            string musicDirectory = Path.Combine(safeRoot, "data", "Music");
            if (!Directory.Exists(musicDirectory))
                throw new DirectoryNotFoundException(MusicFolderMissing);

            RejectExistingReparseAncestors(musicDirectory, "music directory");
            RejectReparsePoint(musicDirectory, "music directory");

            var tracks = new List<GameProfileMusicTrack>();
            foreach (string path in Directory.EnumerateFiles(musicDirectory, "*.ogg", SearchOption.TopDirectoryOnly))
            {
                string fileName = Path.GetFileName(path);
                if (fileName.EndsWith(BackupSuffix, StringComparison.OrdinalIgnoreCase))
                    continue;

                ValidateTargetMusicFileName(fileName);
                RejectReparsePoint(path, "music track file");

                byte[] header = new byte[4];
                using (FileStream stream = File.OpenRead(path))
                {
                    if (stream.Read(header, 0, header.Length) != header.Length)
                        continue;
                }

                if (header[0] != (byte)'O' || header[1] != (byte)'g' || header[2] != (byte)'g' || header[3] != (byte)'S')
                    continue;

                var info = new FileInfo(path);
                tracks.Add(new GameProfileMusicTrack(
                    fileName,
                    ToRelativeSlash(safeRoot, path),
                    info.Length));
            }

            return tracks
                .OrderBy(track => track.FileName, StringComparer.OrdinalIgnoreCase)
                .ToArray();
        }

        public static GameProfileMusicReplacementResult StageReplacement(GameProfileMusicReplacementOptions options)
        {
            string safeRoot = ValidateSafeGameRoot(options.SafeGameRoot, options.AppOwnedProfilesRoot);
            string targetFileName = ValidateTargetMusicFileName(options.TargetMusicFileName);
            string musicDirectory = Path.Combine(safeRoot, "data", "Music");
            if (!Directory.Exists(musicDirectory))
                throw new DirectoryNotFoundException(MusicFolderMissing);

            string targetPath = Path.Combine(musicDirectory, targetFileName);
            if (!File.Exists(targetPath))
                throw new FileNotFoundException(TargetMusicFileMissing);
            RejectExistingReparseAncestors(targetPath, "target music path");
            RejectReparsePoint(targetPath, "target music file");
            RejectMultipleHardLinks(targetPath, "Target music file");

            string replacementPath = ValidateReplacementOgg(options.ReplacementOggPath);
            if (string.Equals(Path.GetFullPath(replacementPath), Path.GetFullPath(targetPath), StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("The replacement OGG must not be the target music file.");

            string manifestPath = Path.Combine(safeRoot, ManifestFileName);
            RejectExistingReparseAncestors(manifestPath, "music replacement manifest path");
            if (File.Exists(manifestPath))
            {
                RejectReparsePoint(manifestPath, "music replacement manifest");
                RejectMultipleHardLinks(manifestPath, "Music replacement manifest");
                throw new InvalidOperationException("An active safe-copy music replacement manifest already exists; restore copied music bytes before staging another replacement.");
            }

            string backupPath = targetPath + BackupSuffix;
            RejectExistingReparseAncestors(backupPath, "music backup path");
            if (File.Exists(backupPath))
            {
                RejectReparsePoint(backupPath, "music backup file");
                RejectMultipleHardLinks(backupPath, "Music backup file");
                EnsureTargetMatchesBackupBeforeReplacement(targetPath, backupPath);
            }
            else
            {
                File.Copy(targetPath, backupPath, overwrite: false);
            }

            byte[] originalBytes = File.ReadAllBytes(backupPath);
            string originalSha = ComputeSha256(originalBytes);
            byte[] replacementBytes = File.ReadAllBytes(replacementPath);
            string replacementSha = ComputeSha256(replacementBytes);

            string tempPath = Path.Combine(musicDirectory, $"{targetFileName}.{Guid.NewGuid():N}.tmp");
            try
            {
                File.WriteAllBytes(tempPath, replacementBytes);
                File.Replace(tempPath, targetPath, null, ignoreMetadataErrors: true);
            }
            finally
            {
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
            }

            var result = new GameProfileMusicReplacementResult(
                SchemaVersion,
                DateTimeOffset.UtcNow,
                Mutation: true,
                targetFileName,
                ToRelativeSlash(safeRoot, targetPath),
                ToRelativeSlash(safeRoot, backupPath),
                targetPath,
                backupPath,
                manifestPath,
                originalBytes.LongLength,
                originalSha,
                replacementBytes.LongLength,
                replacementSha);

            WriteManifest(result, replacementPath);
            return result;
        }

        public static GameProfileMusicReplacementRestoreResult RestoreReplacement(GameProfileMusicReplacementRestoreOptions options)
        {
            string safeRoot = ValidateSafeGameRoot(options.SafeGameRoot, options.AppOwnedProfilesRoot);
            string manifestPath = Path.Combine(safeRoot, ManifestFileName);
            if (!File.Exists(manifestPath))
                throw new FileNotFoundException("That copy is missing onslaught-music-replacement-manifest.json.");
            RejectExistingReparseAncestors(manifestPath, "music replacement manifest path");
            RejectReparsePoint(manifestPath, "music replacement manifest");
            RejectMultipleHardLinks(manifestPath, "Music replacement manifest");

            using JsonDocument doc = JsonDocument.Parse(File.ReadAllText(manifestPath));
            string? schema = doc.RootElement.TryGetProperty("schemaVersion", out JsonElement schemaEl)
                ? schemaEl.GetString()
                : null;
            if (!string.Equals(schema, SchemaVersion, StringComparison.Ordinal))
                throw new InvalidOperationException(MusicDetailsUnsupported);

            string targetFileName = doc.RootElement.GetProperty("targetMusicFileName").GetString() ?? string.Empty;
            string targetRelative = doc.RootElement.GetProperty("targetRelativePath").GetString() ?? string.Empty;
            string backupRelative = doc.RootElement.GetProperty("backupRelativePath").GetString() ?? string.Empty;
            string originalSha256 = doc.RootElement.GetProperty("originalSha256").GetString() ?? string.Empty;

            targetFileName = ValidateTargetMusicFileName(targetFileName);
            string targetPath = Path.Combine(safeRoot, "data", "Music", targetFileName);
            string backupPath = targetPath + BackupSuffix;
            string manifestTargetPath = ResolveManifestRelativePath(safeRoot, targetRelative);
            string manifestBackupPath = ResolveManifestRelativePath(safeRoot, backupRelative);
            if (!string.Equals(Path.GetFullPath(manifestTargetPath), Path.GetFullPath(targetPath), StringComparison.OrdinalIgnoreCase) ||
                !string.Equals(Path.GetFullPath(manifestBackupPath), Path.GetFullPath(backupPath), StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(MusicDetailsWrongTarget);
            }

            if (!File.Exists(backupPath))
                throw new FileNotFoundException(MusicBackupMissing);
            RejectExistingReparseAncestors(targetPath, "target music path");
            RejectExistingReparseAncestors(backupPath, "music backup path");
            RejectReparsePoint(targetPath, "target music file");
            RejectReparsePoint(backupPath, "music backup file");
            RejectMultipleHardLinks(targetPath, "Target music file");
            RejectMultipleHardLinks(backupPath, "Music backup file");
            string backupSha = ComputeSha256(File.ReadAllBytes(backupPath));
            if (!string.Equals(backupSha, originalSha256, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException(MusicBackupMismatch);

            string tempPath = Path.Combine(
                Path.GetDirectoryName(targetPath)!,
                $"{Path.GetFileName(targetPath)}.restore.{Guid.NewGuid():N}.tmp");
            try
            {
                File.Copy(backupPath, tempPath, overwrite: false);
                File.Replace(tempPath, targetPath, null, ignoreMetadataErrors: true);
            }
            finally
            {
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
            }

            RejectReparsePoint(targetPath, "target music file");
            RejectMultipleHardLinks(targetPath, "Target music file");
            string restoredSha = ComputeSha256(File.ReadAllBytes(targetPath));
            if (!string.Equals(restoredSha, originalSha256, StringComparison.OrdinalIgnoreCase))
                throw new IOException(MusicRestoreMismatch);

            RejectReparsePoint(manifestPath, "music replacement manifest");
            RejectMultipleHardLinks(manifestPath, "Music replacement manifest");
            File.Delete(manifestPath);
            return new GameProfileMusicReplacementRestoreResult(
                true,
                targetFileName,
                MusicRestored);
        }

        private static void EnsureTargetMatchesBackupBeforeReplacement(string targetPath, string backupPath)
        {
            string targetSha = ComputeSha256(File.ReadAllBytes(targetPath));
            string backupSha = ComputeSha256(File.ReadAllBytes(backupPath));
            if (!string.Equals(targetSha, backupSha, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Current copied-game music target no longer matches the original backup; restore before staging another replacement.");
        }

        private static string ValidateSafeGameRoot(string safeGameRoot, string appOwnedProfilesRoot)
        {
            if (string.IsNullOrWhiteSpace(safeGameRoot) || !Directory.Exists(safeGameRoot))
                throw new DirectoryNotFoundException(CopyFolderMissing);
            if (string.IsNullOrWhiteSpace(appOwnedProfilesRoot) || !Directory.Exists(appOwnedProfilesRoot))
                throw new DirectoryNotFoundException(ProfileFolderMissing);

            string root = NormalizeExistingDirectory(safeGameRoot);
            string profilesRoot = NormalizeExistingDirectory(appOwnedProfilesRoot);
            if (!IsSameOrUnderRoot(root, profilesRoot) ||
                string.Equals(root, profilesRoot, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException(GameProfilePreflightService.CopyMustStayInside);

            RejectExistingReparseAncestors(root, "playable copied game folder root");
            RejectReparsePoint(root, "playable copied game folder root");
            GameProfilePreflightService.BuildLaunchPlan(
                root,
                Array.Empty<string>(),
                validateMusicReplacementManifest: false);
            return root;
        }

        private static string ValidateTargetMusicFileName(string value)
        {
            string fileName = (value ?? string.Empty).Trim();
            if (fileName.Length == 0 ||
                !string.Equals(Path.GetFileName(fileName), fileName, StringComparison.Ordinal) ||
                fileName.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 ||
                !string.Equals(Path.GetExtension(fileName), ".ogg", StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Target music file name must be a single .ogg file name under data\\Music.");
            }

            return fileName;
        }

        private static string ValidateReplacementOgg(string replacementPath)
        {
            if (string.IsNullOrWhiteSpace(replacementPath))
                throw new InvalidOperationException("A replacement OGG is required.");

            string fullPath = Path.GetFullPath(replacementPath);
            if (!File.Exists(fullPath))
                throw new FileNotFoundException("That replacement OGG file could not be found.");
            if (!string.Equals(Path.GetExtension(fullPath), ".ogg", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Replacement music file must use the .ogg extension.");

            RejectExistingReparseAncestors(fullPath, "replacement OGG path");
            RejectReparsePoint(fullPath, "replacement OGG file");

            ValidateOggHeader(fullPath, "Replacement music file");

            return fullPath;
        }

        private static void ValidateOggHeader(string path, string label)
        {
            byte[] header = new byte[4];
            using (FileStream stream = File.OpenRead(path))
            {
                if (stream.Read(header, 0, header.Length) != header.Length)
                    throw new InvalidOperationException(MusicFileTooSmall);
            }

            if (header[0] != (byte)'O' || header[1] != (byte)'g' || header[2] != (byte)'g' || header[3] != (byte)'S')
                throw new InvalidOperationException(MusicFileNotOgg);
        }

        private static string ResolveManifestRelativePath(string safeRoot, string relativePath)
        {
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathFullyQualified(relativePath))
                throw new InvalidOperationException("Music replacement manifest files must stay inside the copy.");

            string fullPath = Path.GetFullPath(Path.Combine(safeRoot, relativePath.Replace('/', Path.DirectorySeparatorChar)));
            if (!IsSameOrUnderRoot(fullPath, safeRoot))
                throw new InvalidOperationException("Music replacement manifest files must stay inside the copy.");
            return fullPath;
        }

        private static void WriteManifest(GameProfileMusicReplacementResult result, string replacementPath)
        {
            RejectExistingReparseAncestors(result.ManifestPath, "music replacement manifest path");
            RejectReparsePoint(result.ManifestPath, "music replacement manifest");
            RejectMultipleHardLinks(result.ManifestPath, "Music replacement manifest");

            var options = new JsonSerializerOptions
            {
                WriteIndented = true,
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            };

            var manifest = new
            {
                result.SchemaVersion,
                result.GeneratedAt,
                result.Mutation,
                SafeGameRoot = ".",
                result.TargetMusicFileName,
                result.TargetRelativePath,
                result.BackupRelativePath,
                ReplacementSourceFileName = Path.GetFileName(replacementPath),
                result.OriginalSize,
                result.OriginalSha256,
                result.ReplacementSize,
                result.ReplacementSha256,
            };

            string tempPath = Path.Combine(
                Path.GetDirectoryName(result.ManifestPath)!,
                $"{Path.GetFileName(result.ManifestPath)}.{Guid.NewGuid():N}.tmp");
            try
            {
                File.WriteAllText(tempPath, JsonSerializer.Serialize(manifest, options));
                if (File.Exists(result.ManifestPath))
                {
                    File.Replace(tempPath, result.ManifestPath, null, ignoreMetadataErrors: true);
                }
                else
                {
                    File.Move(tempPath, result.ManifestPath);
                }
            }
            finally
            {
                if (File.Exists(tempPath))
                    File.Delete(tempPath);
            }
        }

        private static string ToRelativeSlash(string root, string path)
        {
            return Path.GetRelativePath(root, path).Replace(Path.DirectorySeparatorChar, '/');
        }

        private static string ComputeSha256(byte[] data)
        {
            return Convert.ToHexString(SHA256.HashData(data)).ToLowerInvariant();
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
            if (!File.Exists(path) && !Directory.Exists(path))
                return;

            FileAttributes attributes = File.GetAttributes(path);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException(CopyCannotUseLink);
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

        private static void RejectMultipleHardLinks(string path, string label)
        {
            if (!OperatingSystem.IsWindows() || !File.Exists(path))
                return;

            uint linkCount = GetWindowsHardLinkCount(path);
            if (linkCount > 1)
                throw new InvalidOperationException(FileCannotShareData);
        }

        private static uint GetWindowsHardLinkCount(string path)
        {
            using SafeFileHandle handle = File.OpenHandle(
                path,
                FileMode.Open,
                FileAccess.Read,
                FileShare.ReadWrite | FileShare.Delete);

            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation info))
                throw new IOException(FileMutationSafety.FileCouldNotBeInspected, new System.ComponentModel.Win32Exception(Marshal.GetLastWin32Error()));

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
    }
}
