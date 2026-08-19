using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>One career save sitting inside a safe copy.</summary>
    /// <param name="FileName">The file name with its extension, which is what a player recognises.</param>
    /// <param name="FullPath">Where it actually is.</param>
    /// <param name="RelativeDirectory">
    /// The folder it was found in, relative to the copy root - <c>savegames</c> for almost all of
    /// them, and an empty string for one sitting at the copy root.
    /// </param>
    public sealed record SafeCopySaveFile(
        string FileName,
        string FullPath,
        string RelativeDirectory,
        long Length,
        DateTime LastWriteUtc);

    /// <summary>Every career save one safe copy is holding.</summary>
    public sealed record SafeCopySaveInventory(
        string ProfileRoot,
        string DisplayName,
        IReadOnlyList<SafeCopySaveFile> Saves)
    {
        public bool HasSaves => Saves.Count > 0;

        public long TotalBytes => Saves.Sum(save => save.Length);
    }

    /// <summary>
    /// What should happen to the career saves inside a safe copy when the copy is deleted.
    ///
    /// The default is the refusal. Deleting a copy is how somebody tidies up several gigabytes of
    /// Roaming AppData, and the career they played inside it is the one thing in that folder they
    /// cannot get back from the game files.
    /// </summary>
    public enum SafeCopySaveDisposition
    {
        /// <summary>
        /// Refuse the delete while any career save is still inside. The caller is expected to
        /// rescue them - see <see cref="SafeCopySaveRescueService.RescueThenDelete"/> - or to come
        /// back with <see cref="DiscardSaves"/> once a person has actually been asked.
        /// </summary>
        RefuseWhileSavesArePresent = 0,

        /// <summary>
        /// Delete the copy and the saves with it. Only for a caller that has already rescued them,
        /// or that has put the question to a person and been told to go ahead.
        /// </summary>
        DiscardSaves = 1,
    }

    /// <summary>Which saves to bring out of a copy, and where they should land.</summary>
    public sealed class SafeCopySaveRescueRequest
    {
        /// <summary>The safe copy to take saves out of.</summary>
        public string ProfileRoot { get; init; } = string.Empty;

        /// <summary>An ordinary folder outside the copy. It is created if it does not exist.</summary>
        public string DestinationDirectory { get; init; } = string.Empty;

        /// <summary>
        /// The file names to bring out, or null for every save in the copy. Names are matched
        /// against <see cref="SafeCopySaveFile.FileName"/>; anything unmatched is an error rather
        /// than a silent skip, because a caller that asked for a named save and got a cheerful
        /// "rescued 0 files" would go on to delete the copy.
        /// </summary>
        public IReadOnlyList<string>? FileNames { get; init; }

        /// <summary>Only true once a person has agreed to replace files already in the destination.</summary>
        public bool AllowOverwrite { get; init; }
    }

    /// <param name="NeedsOverwriteConfirmation">
    /// True when the only thing in the way is a file of that name already sitting in the
    /// destination. The caller asks, then retries with
    /// <see cref="SafeCopySaveRescueRequest.AllowOverwrite"/>.
    /// </param>
    public sealed record SafeCopySaveRescueFileOutcome(
        string FileName,
        bool Rescued,
        string? OutputPath,
        string Message,
        bool NeedsOverwriteConfirmation = false);

    public sealed record SafeCopySaveRescueResult(
        bool Success,
        string Message,
        string DestinationDirectory,
        IReadOnlyList<SafeCopySaveRescueFileOutcome> Files)
    {
        public int RescuedCount => Files.Count(file => file.Rescued);

        public bool NeedsOverwriteConfirmation => Files.Any(file => file.NeedsOverwriteConfirmation);

        /// <summary>The saves that could not be brought out, which is what a caller must not ignore.</summary>
        public IReadOnlyList<SafeCopySaveRescueFileOutcome> Failures =>
            Files.Where(file => !file.Rescued).ToArray();
    }

    /// <summary>What a rescue-then-delete actually did.</summary>
    public sealed record SafeCopyRemovalResult(
        bool Success,
        string Message,
        SafeCopySaveRescueResult? Rescue,
        string? DeletedProfileRoot);

    /// <summary>
    /// Getting career saves back out of a safe copy, and getting them out before the copy is
    /// deleted.
    ///
    /// The Save Lab could already push a save into a copy and there was no way back: the only
    /// deletion this codebase exposed was a recursive delete of the whole copy folder, and the
    /// careers a player had built inside it went with it, silently. That is the one thing in the
    /// safe-copy design that could lose something the game cannot regenerate, so the rescue is a
    /// first-class operation here rather than a flag on the delete.
    ///
    /// Every copy out goes through the same guarded transaction the Save Lab and the Cheats page
    /// use. It stages the write, verifies length and SHA-256 on both sides of the swap, refuses to
    /// write in place, refuses symlinks and hardlinked aliases, and refuses any destination inside
    /// an installed Battle Engine Aquila folder. Nothing here modifies the save it read, and
    /// nothing here deletes anything on its own - <see cref="RescueThenDelete"/> is the only
    /// routine that removes a copy, and it will not do so until every requested save is verified
    /// on the other side.
    /// </summary>
    public static class SafeCopySaveRescueService
    {
        /// <summary>
        /// Career saves are <c>.bes</c>. <c>defaultoptions.bea</c> is deliberately not treated as a
        /// save: it ships with the game, so it is in the root of every single copy, and warning
        /// about it before every delete would train people to click through the warning that
        /// matters.
        /// </summary>
        public const string CareerSaveExtension = ".bes";

        public const string CouldNotKeep = "Could not keep that career. Nothing was changed.";

        public const string CopyFolderMissing = "That copy folder could not be found.";

        public const string ProfileFolderRequired = "A profile folder is required.";

        public const string CopyRequired = "A copy is required.";

        public const string CopyMustStayInside =
            "That copy must stay inside the app-owned profile folder.";

        /// <summary>
        /// Where the game keeps saves inside a copy. <c>savegames</c> is the Steam build's folder
        /// and is where everything this app writes goes; the rest are swept because a save that
        /// ends up in one of them is still the player's, and the cost of looking is one directory
        /// listing.
        /// </summary>
        private static readonly string[] SaveDirectories = { "savegames", "saves", "Save", "" };

        /// <summary>Every career save inside one app-generated safe copy, newest first.</summary>
        public static SafeCopySaveInventory Inventory(string profileRoot)
        {
            return Inventory(profileRoot, AppConfig.GetGameProfilesDir());
        }

        /// <inheritdoc cref="Inventory(string)"/>
        public static SafeCopySaveInventory Inventory(string profileRoot, string appOwnedProfilesRoot)
        {
            string resolved = ValidateGeneratedProfile(profileRoot, appOwnedProfilesRoot);
            var found = new List<SafeCopySaveFile>();
            var seen = new HashSet<string>(FileMutationSafety.PathComparer);

            foreach (string relative in SaveDirectories)
            {
                string directory = relative.Length == 0 ? resolved : Path.Combine(resolved, relative);
                if (!Directory.Exists(directory))
                    continue;

                string[] files;
                try
                {
                    files = Directory.GetFiles(directory, "*" + CareerSaveExtension);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                    // A folder that cannot be listed is reported as holding nothing rather than
                    // failing the whole inventory - but the delete gate treats an unreadable copy
                    // as unsafe by refusing on the manifest and containment checks above, so this
                    // cannot turn into a silent "no saves here, go ahead".
                    continue;
                }

                foreach (string file in files)
                {
                    if (!seen.Add(Path.GetFullPath(file)))
                        continue;

                    FileInfo info;
                    try
                    {
                        info = new FileInfo(file);
                    }
                    catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                    {
                        continue;
                    }

                    found.Add(new SafeCopySaveFile(
                        FileName: Path.GetFileName(file),
                        FullPath: file,
                        RelativeDirectory: relative,
                        Length: info.Length,
                        LastWriteUtc: info.LastWriteTimeUtc));
                }
            }

            return new SafeCopySaveInventory(
                ProfileRoot: resolved,
                DisplayName: Path.GetFileName(Path.TrimEndingDirectorySeparator(resolved)),
                Saves: found
                    .OrderByDescending(save => save.LastWriteUtc)
                    .ThenBy(save => save.FileName, StringComparer.OrdinalIgnoreCase)
                    .ToArray());
        }

        /// <summary>
        /// Every app-generated safe copy on disk with whatever saves it is holding, newest copy
        /// first. Copies this app cannot vouch for are left out rather than listed as empty.
        /// </summary>
        public static IReadOnlyList<SafeCopySaveInventory> InventoryAll()
        {
            string root;
            try
            {
                root = AppConfig.GetGameProfilesDir();
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or UnauthorizedAccessException)
            {
                return Array.Empty<SafeCopySaveInventory>();
            }

            return InventoryAll(root);
        }

        /// <inheritdoc cref="InventoryAll()"/>
        public static IReadOnlyList<SafeCopySaveInventory> InventoryAll(string appOwnedProfilesRoot)
        {
            if (string.IsNullOrWhiteSpace(appOwnedProfilesRoot) || !Directory.Exists(appOwnedProfilesRoot))
                return Array.Empty<SafeCopySaveInventory>();

            string[] candidates;
            try
            {
                candidates = Directory.GetDirectories(appOwnedProfilesRoot);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                return Array.Empty<SafeCopySaveInventory>();
            }

            var rows = new List<(DateTime Written, SafeCopySaveInventory Inventory)>();
            foreach (string candidate in candidates)
            {
                SafeCopySaveInventory inventory;
                try
                {
                    inventory = Inventory(candidate, appOwnedProfilesRoot);
                }
                catch (Exception ex) when (ex is InvalidOperationException or IOException
                                            or UnauthorizedAccessException or ArgumentException
                                            or DirectoryNotFoundException)
                {
                    continue;
                }

                DateTime written;
                try
                {
                    written = Directory.GetLastWriteTimeUtc(inventory.ProfileRoot);
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                    written = DateTime.MinValue;
                }

                rows.Add((written, inventory));
            }

            return rows
                .OrderByDescending(row => row.Written)
                .ThenBy(row => row.Inventory.DisplayName, StringComparer.OrdinalIgnoreCase)
                .Select(row => row.Inventory)
                .ToArray();
        }

        /// <summary>
        /// One sentence naming what a delete would take with it, or null when the copy is holding
        /// nothing. This is the sentence a person has to see before the delete, so it counts the
        /// saves and names them rather than saying "some data may be lost".
        /// </summary>
        public static string? DescribeSavesAtRisk(SafeCopySaveInventory inventory)
        {
            ArgumentNullException.ThrowIfNull(inventory);
            if (!inventory.HasSaves)
                return null;

            string[] names = inventory.Saves
                .Select(save => Path.GetFileNameWithoutExtension(save.FileName))
                .ToArray();

            string listed = names.Length <= 3
                ? string.Join(", ", names)
                : $"{string.Join(", ", names.Take(3))} and {names.Length - 3} more";

            string count = names.Length == 1 ? "1 career save" : $"{names.Length} career saves";
            return $"{inventory.DisplayName} is holding {count}: {listed}. Deleting the copy deletes them too.";
        }

        /// <summary>Bring career saves out of a copy into an ordinary folder.</summary>
        public static SafeCopySaveRescueResult Rescue(SafeCopySaveRescueRequest request)
        {
            ArgumentNullException.ThrowIfNull(request);
            return Rescue(request, AppConfig.GetGameProfilesDir());
        }

        /// <inheritdoc cref="Rescue(SafeCopySaveRescueRequest)"/>
        public static SafeCopySaveRescueResult Rescue(
            SafeCopySaveRescueRequest request,
            string appOwnedProfilesRoot)
        {
            ArgumentNullException.ThrowIfNull(request);

            if (string.IsNullOrWhiteSpace(request.DestinationDirectory))
            {
                return new SafeCopySaveRescueResult(
                    false,
                    "Choose a folder to keep the saves in.",
                    string.Empty,
                    Array.Empty<SafeCopySaveRescueFileOutcome>());
            }

            string destination;
            SafeCopySaveInventory inventory;
            IReadOnlyList<SafeCopySaveFile> wanted;
            try
            {
                inventory = Inventory(request.ProfileRoot, appOwnedProfilesRoot);
                destination = FileMutationSafety.NormalizeLocalPath(
                    request.DestinationDirectory.Trim(),
                    "Destination folder");

                if (FileMutationSafety.IsSameOrUnderRoot(destination, inventory.ProfileRoot))
                {
                    return new SafeCopySaveRescueResult(
                        false,
                        "Keep the saves somewhere outside the copy - a folder inside it goes when the copy goes.",
                        destination,
                        Array.Empty<SafeCopySaveRescueFileOutcome>());
                }

                if (LooksLikeInstalledGameDestination(destination))
                {
                    return new SafeCopySaveRescueResult(
                        false,
                        CareerSaveLocation.InstalledDestinationRefused,
                        destination,
                        Array.Empty<SafeCopySaveRescueFileOutcome>());
                }

                wanted = SelectRequested(inventory, request.FileNames);
                if (wanted.Count == 0)
                {
                    return new SafeCopySaveRescueResult(
                        false,
                        $"{inventory.DisplayName} has no career saves in it.",
                        destination,
                        Array.Empty<SafeCopySaveRescueFileOutcome>());
                }

                Directory.CreateDirectory(destination);
                FileMutationSafety.RejectExistingReparseAncestors(destination, "Destination folder");
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException
                                        or NotSupportedException or UnauthorizedAccessException
                                        or DirectoryNotFoundException)
            {
                return new SafeCopySaveRescueResult(
                    false,
                    DescribeCaughtFailure(ex),
                    request.DestinationDirectory,
                    Array.Empty<SafeCopySaveRescueFileOutcome>());
            }

            var outcomes = new List<SafeCopySaveRescueFileOutcome>();
            foreach (SafeCopySaveFile save in wanted)
            {
                outcomes.Add(RescueOne(save, destination, request.AllowOverwrite));
            }

            int rescued = outcomes.Count(outcome => outcome.Rescued);
            bool success = rescued == outcomes.Count;
            string message = success
                ? (rescued == 1
                    ? $"Kept 1 save from {inventory.DisplayName}."
                    : $"Kept {rescued} saves from {inventory.DisplayName}.")
                : (rescued == 0
                    ? $"Could not bring anything out of {inventory.DisplayName}. Nothing was deleted."
                    : $"Kept {rescued} of {outcomes.Count} saves from {inventory.DisplayName}. Nothing was deleted.");

            return new SafeCopySaveRescueResult(success, message, destination, outcomes);
        }

        /// <summary>
        /// Take the saves out first, prove every one of them landed, and only then delete the copy.
        ///
        /// This is the routine behind every offer to delete a copy that has careers in it, and the
        /// ordering is the whole point: the delete is unreachable until the rescue has succeeded,
        /// so there is no arrangement of failures that ends with the saves gone and no copy of
        /// them. A copy holding nothing skips straight to the delete.
        /// </summary>
        public static SafeCopyRemovalResult RescueThenDelete(
            string profileRoot,
            string appOwnedProfilesRoot,
            string destinationDirectory,
            bool allowOverwrite = false)
        {
            SafeCopySaveInventory inventory;
            try
            {
                inventory = Inventory(profileRoot, appOwnedProfilesRoot);
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException
                                        or UnauthorizedAccessException or ArgumentException
                                        or DirectoryNotFoundException)
            {
                return new SafeCopyRemovalResult(false, DescribeCaughtFailure(ex), null, null);
            }

            SafeCopySaveRescueResult? rescue = null;
            if (inventory.HasSaves)
            {
                rescue = Rescue(
                    new SafeCopySaveRescueRequest
                    {
                        ProfileRoot = inventory.ProfileRoot,
                        DestinationDirectory = destinationDirectory,
                        AllowOverwrite = allowOverwrite,
                    },
                    appOwnedProfilesRoot);

                if (!rescue.Success)
                {
                    return new SafeCopyRemovalResult(
                        false,
                        rescue.Message + " The copy is still here.",
                        rescue,
                        null);
                }
            }

            string deleted;
            try
            {
                deleted = GameProfilePreflightService.DeleteGeneratedProfile(
                    inventory.ProfileRoot,
                    appOwnedProfilesRoot,
                    SafeCopySaveDisposition.DiscardSaves);
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException
                                        or UnauthorizedAccessException or DirectoryNotFoundException)
            {
                return new SafeCopyRemovalResult(
                    false,
                    rescue is null
                        ? DescribeCaughtFailure(ex)
                        : $"{rescue.Message} The copy could not be deleted. Nothing more was changed.",
                    rescue,
                    null);
            }

            string message = rescue is null
                ? $"Deleted {inventory.DisplayName}. It had no career saves in it."
                : $"{rescue.Message} Then deleted {inventory.DisplayName}.";

            return new SafeCopyRemovalResult(true, message, rescue, deleted);
        }

        private static SafeCopySaveRescueFileOutcome RescueOne(
            SafeCopySaveFile save,
            string destination,
            bool allowOverwrite)
        {
            string outputPath = Path.Combine(destination, save.FileName);
            try
            {
                outputPath = FileMutationSafety.NormalizeLocalPath(outputPath, "Destination file");

                if (File.Exists(outputPath) && !allowOverwrite)
                {
                    return new SafeCopySaveRescueFileOutcome(
                        save.FileName,
                        false,
                        outputPath,
                        $"There is already a save called {save.FileName} in that folder.",
                        NeedsOverwriteConfirmation: true);
                }

                using GuardedFileMutation mutation = FileMutationSafety.Begin(outputPath, save.FullPath);
                mutation.CommitFromProtectedInput(save.FullPath);
                return new SafeCopySaveRescueFileOutcome(save.FileName, true, outputPath, "Kept.");
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException
                                        or NotSupportedException or UnauthorizedAccessException)
            {
                return new SafeCopySaveRescueFileOutcome(save.FileName, false, outputPath, DescribeCaughtFailure(ex));
            }
        }

        /// <summary>
        /// A folder picker usually returns an existing directory. Rescue also accepts a path it
        /// would create, so walk up to the first ancestor that exists and classify that. Layout
        /// only: this must not create the folder just to ask the question.
        /// </summary>
        private static bool LooksLikeInstalledGameDestination(string destination)
        {
            return CareerSaveLocation.ClassifyExisting(destination) == CareerSaveLocationKind.InstalledGame;
        }

        private static string DescribeCaughtFailure(Exception ex)
        {
            string message = ex.Message ?? string.Empty;
            if (string.IsNullOrWhiteSpace(message) || MessageLeaksPath(message))
                return CouldNotKeep;

            return message;
        }

        private static bool MessageLeaksPath(string message)
        {
            return message.Contains(":\\", StringComparison.Ordinal)
                || message.Contains(":/", StringComparison.Ordinal);
        }

        /// <summary>
        /// The requested subset, or everything when no names were given. An unmatched name returns
        /// an empty list so the caller reports a failure instead of quietly rescuing nothing.
        /// </summary>
        private static IReadOnlyList<SafeCopySaveFile> SelectRequested(
            SafeCopySaveInventory inventory,
            IReadOnlyList<string>? fileNames)
        {
            if (fileNames is null || fileNames.Count == 0)
                return inventory.Saves;

            var selected = new List<SafeCopySaveFile>();
            foreach (string name in fileNames)
            {
                SafeCopySaveFile? match = inventory.Saves.FirstOrDefault(save =>
                    string.Equals(save.FileName, name, StringComparison.OrdinalIgnoreCase) ||
                    string.Equals(
                        Path.GetFileNameWithoutExtension(save.FileName),
                        name,
                        StringComparison.OrdinalIgnoreCase));

                if (match is null)
                    throw new InvalidOperationException($"{inventory.DisplayName} has no save called {name}.");

                if (!selected.Contains(match))
                    selected.Add(match);
            }

            return selected;
        }

        /// <summary>
        /// The same containment and identity checks the delete makes, so an inventory can never
        /// describe a folder the delete would refuse - or, worse, describe a different folder than
        /// the one that gets deleted.
        /// </summary>
        internal static string ValidateGeneratedProfile(string profileRoot, string appOwnedProfilesRoot)
        {
            if (string.IsNullOrWhiteSpace(appOwnedProfilesRoot))
                throw new InvalidOperationException(ProfileFolderRequired);

            if (string.IsNullOrWhiteSpace(profileRoot))
                throw new InvalidOperationException(CopyRequired);

            if (!Directory.Exists(profileRoot))
                throw new DirectoryNotFoundException(CopyFolderMissing);

            string normalizedRoot = FileMutationSafety.NormalizeLocalPath(
                appOwnedProfilesRoot,
                "app-owned playable copied game folder root");
            string normalizedProfile = FileMutationSafety.NormalizeLocalPath(
                profileRoot,
                "playable copied game folder");

            FileMutationSafety.RejectExistingReparseAncestors(normalizedProfile, "playable copied game folder");
            FileMutationSafety.RejectReparsePoint(normalizedProfile, "playable copied game folder");

            if (!FileMutationSafety.IsSameOrUnderRoot(normalizedProfile, normalizedRoot) ||
                string.Equals(normalizedProfile, normalizedRoot, FileMutationSafety.PathComparison))
            {
                throw new InvalidOperationException(CopyMustStayInside);
            }

            string manifestPath = Path.Combine(
                normalizedProfile,
                GameProfilePreflightService.ProfileManifestFileName);
            if (!File.Exists(manifestPath))
            {
                throw new InvalidOperationException(GameProfilePreflightService.CopyManifestMissing);
            }

            return normalizedProfile;
        }
    }
}
