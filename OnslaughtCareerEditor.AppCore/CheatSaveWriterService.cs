using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// A folder the Cheats page is willing to write a renamed save copy into.
    /// </summary>
    /// <param name="DisplayName">The safe copy's folder name, shown to the player.</param>
    /// <param name="ProfileRoot">The safe copy's root folder.</param>
    /// <param name="SavegamesDirectory">The <c>savegames</c> folder inside it.</param>
    public sealed record CheatSaveTarget(
        string DisplayName,
        string ProfileRoot,
        string SavegamesDirectory);

    public sealed class CheatSaveWriteRequest
    {
        /// <summary>An existing real <c>.bes</c> career save. Its bytes are copied unchanged.</summary>
        public string InputPath { get; init; } = string.Empty;

        /// <summary>Where the copy goes.</summary>
        public string OutputDirectory { get; init; } = string.Empty;

        /// <summary>The new name, without the extension.</summary>
        public string Name { get; init; } = string.Empty;

        /// <summary>Only true after the player has confirmed replacing a file that already exists.</summary>
        public bool AllowOverwrite { get; init; }
    }

    /// <param name="NeedsOverwriteConfirmation">
    /// True when the only thing standing in the way is that a file of that name is already there.
    /// The page asks, then retries with <see cref="CheatSaveWriteRequest.AllowOverwrite"/>.
    /// </param>
    public sealed record CheatSaveWriteOutcome(
        bool Success,
        string Message,
        string? OutputPath,
        bool NeedsOverwriteConfirmation = false);

    /// <summary>
    /// Writes the cheat-named save copy.
    ///
    /// The only thing this changes is the file *name*. The bytes are copied verbatim from a real
    /// save the player already has, through the same guarded transaction the Save Lab uses, which
    /// stages the write, verifies length and hash before and after the swap, refuses to write in
    /// place, refuses symlinks and hardlinked aliases, and refuses any destination inside an
    /// installed Battle Engine Aquila folder.
    ///
    /// Nothing here synthesizes a save, and nothing here modifies the save it read.
    /// </summary>
    public static class CheatSaveWriterService
    {
        public const string WriteFailed = "Could not write that save. Nothing was changed.";
        public const string DestinationFolderMissing =
            "That folder could not be found. Choose a folder again.";

        private const string ProfileManifestFileName = "onslaught-profile-manifest.json";
        private const string SavegamesFolderName = "savegames";

        /// <summary>
        /// The app-owned safe copies that can take a save right now, newest folder first.
        /// Returns an empty list when there are none - the page then asks for a folder instead.
        /// </summary>
        public static IReadOnlyList<CheatSaveTarget> FindSafeCopyTargets()
        {
            string profilesRoot;
            try
            {
                profilesRoot = AppConfig.GetGameProfilesDir();
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or UnauthorizedAccessException)
            {
                return Array.Empty<CheatSaveTarget>();
            }

            if (!Directory.Exists(profilesRoot))
            {
                return Array.Empty<CheatSaveTarget>();
            }

            var targets = new List<(DateTime Written, CheatSaveTarget Target)>();
            IEnumerable<string> candidates;
            try
            {
                candidates = Directory.EnumerateDirectories(profilesRoot).ToArray();
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return Array.Empty<CheatSaveTarget>();
            }

            foreach (string candidate in candidates)
            {
                if (!File.Exists(Path.Combine(candidate, ProfileManifestFileName)))
                {
                    continue;
                }

                string resolvedRoot;
                try
                {
                    resolvedRoot = GameProfilePreflightService.ValidateSaveStagingProfileRoot(candidate);
                }
                catch (Exception ex) when (ex is IOException or InvalidOperationException
                                            or UnauthorizedAccessException or ArgumentException
                                            or System.Text.Json.JsonException)
                {
                    // Not a safe copy this app is prepared to vouch for. Leave it out rather
                    // than offering the player a destination that will fail at write time.
                    continue;
                }

                DateTime written;
                try
                {
                    written = Directory.GetLastWriteTimeUtc(resolvedRoot);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                    written = DateTime.MinValue;
                }

                targets.Add((written, new CheatSaveTarget(
                    DisplayName: Path.GetFileName(Path.TrimEndingDirectorySeparator(resolvedRoot)),
                    ProfileRoot: resolvedRoot,
                    SavegamesDirectory: Path.Combine(resolvedRoot, SavegamesFolderName))));
            }

            return targets
                .OrderByDescending(entry => entry.Written)
                .ThenBy(entry => entry.Target.DisplayName, StringComparer.OrdinalIgnoreCase)
                .Select(entry => entry.Target)
                .ToArray();
        }

        /// <summary>Where a write with this name would land. Pure string work.</summary>
        public static string BuildOutputPath(string outputDirectory, string name)
        {
            return Path.Combine(
                outputDirectory ?? string.Empty,
                (name ?? string.Empty) + CheatSaveNameComposer.SaveExtension);
        }

        public static CheatSaveWriteOutcome Write(CheatSaveWriteRequest request)
        {
            ArgumentNullException.ThrowIfNull(request);

            string? nameProblem = CheatSaveNameComposer.DescribeComposedNameProblem(request.Name);
            if (nameProblem is not null)
            {
                return new CheatSaveWriteOutcome(false, nameProblem, null);
            }

            string? inputProblem = SaveEditorService.DescribeCareerSaveInputRejection(request.InputPath);
            if (inputProblem is not null)
            {
                return new CheatSaveWriteOutcome(false, inputProblem, null);
            }

            if (string.IsNullOrWhiteSpace(request.OutputDirectory))
            {
                return new CheatSaveWriteOutcome(false, "Choose where the new save should go.", null);
            }

            try
            {
                string inputPath = FileMutationSafety.NormalizeLocalPath(request.InputPath.Trim(), "Input path");
                string outputDirectory = FileMutationSafety.NormalizeLocalPath(
                    request.OutputDirectory.Trim(),
                    "Output folder");
                if (!Directory.Exists(outputDirectory))
                {
                    return new CheatSaveWriteOutcome(false, DestinationFolderMissing, null);
                }

                string outputPath = FileMutationSafety.NormalizeLocalPath(
                    BuildOutputPath(outputDirectory, request.Name),
                    "Output path");

                if (FileMutationSafety.AreLexicallySamePath(inputPath, outputPath))
                {
                    return new CheatSaveWriteOutcome(
                        false,
                        "That would write over the save you picked. Choose a different name or folder.",
                        outputPath);
                }

                if (File.Exists(outputPath) && !request.AllowOverwrite)
                {
                    return new CheatSaveWriteOutcome(
                        false,
                        $"There is already a save called {Path.GetFileName(outputPath)} in that folder.",
                        outputPath,
                        NeedsOverwriteConfirmation: true);
                }

                string profilesRoot = FileMutationSafety.NormalizeLocalPath(
                    AppConfig.GetGameProfilesDir(),
                    "App-owned profiles root");
                if (!FileMutationSafety.IsSameOrUnderRoot(outputPath, profilesRoot))
                {
                    // Ordinary folder. The guarded transaction still refuses anything inside an
                    // installed game folder.
                    using GuardedFileMutation plainMutation = FileMutationSafety.Begin(outputPath, inputPath);
                    plainMutation.CommitFromProtectedInput(inputPath);
                    return Succeeded(outputPath, insideSafeCopy: false);
                }

                string relative = Path.GetRelativePath(profilesRoot, outputPath);
                string[] segments = relative.Split(
                    new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                    StringSplitOptions.RemoveEmptyEntries);
                if (segments.Length != 3 ||
                    !string.Equals(segments[1], SavegamesFolderName, StringComparison.OrdinalIgnoreCase))
                {
                    return new CheatSaveWriteOutcome(
                        false,
                        "Inside a safe copy, the new save has to go in that copy's savegames folder.",
                        outputPath);
                }

                string profileRoot = Path.Combine(profilesRoot, segments[0]);
                _ = GameProfilePreflightService.ValidateSaveStagingProfileRoot(profileRoot);
                using FileMutationSafety.AppOwnedProfileMutationAuthorization authorization =
                    FileMutationSafety.AuthorizeAppOwnedProfileRoot(profileRoot, profilesRoot);

                string savegamesDirectory = Path.Combine(profileRoot, SavegamesFolderName);
                Directory.CreateDirectory(savegamesDirectory);
                FileMutationSafety.RejectExistingReparseAncestors(
                    savegamesDirectory,
                    "Safe-copy savegames folder");

                using GuardedFileMutation mutation = FileMutationSafety.BeginInAppOwnedProfile(
                    outputPath,
                    authorization,
                    inputPath);
                mutation.CommitFromProtectedInput(inputPath);
                return Succeeded(outputPath, insideSafeCopy: true);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException
                                        or NotSupportedException or UnauthorizedAccessException
                                        or System.Text.Json.JsonException)
            {
                return new CheatSaveWriteOutcome(false, WriteFailed, null);
            }
        }

        private static CheatSaveWriteOutcome Succeeded(string outputPath, bool insideSafeCopy)
        {
            string fileName = Path.GetFileName(outputPath);
            string where = insideSafeCopy
                ? "It is in your safe copy's savegames folder, ready to load."
                : "Copy it into a safe copy's savegames folder when you want to use it.";
            return new CheatSaveWriteOutcome(
                true,
                $"Wrote {fileName}. {where} The save you started from was not touched.",
                outputPath);
        }
    }
}
