using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    /// <summary>What one safe copy is, in the terms somebody deciding whether to keep it needs.</summary>
    /// <param name="SizeBytes">
    /// What it is costing on disk. A copy is most of a game install, so this is the number that
    /// makes somebody go looking for the delete in the first place.
    /// </param>
    /// <param name="CareerSaveCount">
    /// How many careers are inside. This is what makes a delete expensive in a way that deleting
    /// files never is, so it travels with the size rather than being looked up separately.
    /// </param>
    public sealed record SafeCopyOverview(
        string DisplayName,
        string ProfileRoot,
        long SizeBytes,
        DateTime CreatedUtc,
        DateTime LastUsedUtc,
        int CareerSaveCount,
        bool Playable);

    /// <summary>
    /// The safe copies on this machine, as a list somebody can act on.
    ///
    /// The app could make copies and could not show them. Each one is most of a game install
    /// sitting in Roaming AppData, the only route that removed one was a CLI verb, and nothing
    /// anywhere reported how much space they were using. A list is the precondition for the delete
    /// being offered at all - offering to delete something a person cannot see is not an offer.
    /// </summary>
    public static class SafeCopyCatalogService
    {
        /// <summary>Every app-generated copy, largest first, then newest.</summary>
        public static IReadOnlyList<SafeCopyOverview> List()
        {
            string root;
            try
            {
                root = AppConfig.GetGameProfilesDir();
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or UnauthorizedAccessException)
            {
                return Array.Empty<SafeCopyOverview>();
            }

            return List(root);
        }

        /// <inheritdoc cref="List()"/>
        public static IReadOnlyList<SafeCopyOverview> List(string appOwnedProfilesRoot)
        {
            return SafeCopySaveRescueService.InventoryAll(appOwnedProfilesRoot)
                .Select(Describe)
                .OrderByDescending(copy => copy.SizeBytes)
                .ThenByDescending(copy => copy.CreatedUtc)
                .ToArray();
        }

        /// <summary>
        /// The total the copies are costing. Shown once, above the list, because "4 copies" means
        /// nothing and "4 copies, 2.6 GB" is the whole reason somebody opened the page.
        /// </summary>
        public static long TotalSizeBytes(IEnumerable<SafeCopyOverview> copies)
        {
            ArgumentNullException.ThrowIfNull(copies);
            return copies.Sum(copy => copy.SizeBytes);
        }

        /// <summary>
        /// Free space on the volume a new copy would land on, or null when it cannot be read.
        ///
        /// Null is not zero and must not be presented as a refusal: a drive that will not report
        /// its free space is a drive the app knows nothing about, and blocking a copy on that would
        /// be inventing a problem.
        /// </summary>
        public static long? GetFreeSpaceBytesForNewCopy()
        {
            try
            {
                return GetFreeSpaceBytes(AppConfig.GetGameProfilesDir());
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or UnauthorizedAccessException)
            {
                return null;
            }
        }

        /// <inheritdoc cref="GetFreeSpaceBytesForNewCopy()"/>
        public static long? GetFreeSpaceBytes(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
                return null;

            try
            {
                string? rootPath = Path.GetPathRoot(Path.GetFullPath(path));
                if (string.IsNullOrWhiteSpace(rootPath))
                    return null;

                return new DriveInfo(rootPath).AvailableFreeSpace;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or UnauthorizedAccessException
                                        or NotSupportedException)
            {
                return null;
            }
        }

        /// <summary>
        /// Whether there is room for a copy of <paramref name="sourceSizeBytes"/>, with headroom.
        ///
        /// The headroom is not superstition: a copy that exactly fills a volume leaves the game
        /// unable to write a save into it, which turns "you are low on space" into "your career
        /// did not save" much later and somewhere else.
        /// </summary>
        public static bool HasRoomForCopy(long? freeSpaceBytes, long sourceSizeBytes)
        {
            if (freeSpaceBytes is null)
                return true;

            return freeSpaceBytes.Value >= sourceSizeBytes + HeadroomBytes;
        }

        /// <summary>256 MB, which is room for saves and a running game rather than a round number.</summary>
        public const long HeadroomBytes = 256L * 1024 * 1024;

        /// <summary>A size in the units a person uses, not bytes.</summary>
        public static string DescribeSize(long bytes)
        {
            if (bytes <= 0)
                return "0 MB";

            const long gigabyte = 1024L * 1024 * 1024;
            const long megabyte = 1024L * 1024;

            if (bytes >= gigabyte)
                return $"{bytes / (double)gigabyte:0.0} GB";

            if (bytes >= megabyte)
                return $"{bytes / (double)megabyte:0} MB";

            return $"{Math.Max(1, bytes / 1024)} KB";
        }

        /// <summary>Total bytes under a folder. Unreadable subtrees are skipped, not thrown over.</summary>
        public static long MeasureDirectoryBytes(string path)
        {
            if (string.IsNullOrWhiteSpace(path) || !Directory.Exists(path))
                return 0;

            long total = 0;
            var pending = new Stack<string>();
            pending.Push(path);

            while (pending.Count > 0)
            {
                string current = pending.Pop();

                try
                {
                    foreach (string file in Directory.EnumerateFiles(current))
                    {
                        try
                        {
                            total += new FileInfo(file).Length;
                        }
                        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                        {
                            // A file that vanished mid-walk is not worth failing a size estimate.
                        }
                    }

                    foreach (string directory in Directory.EnumerateDirectories(current))
                    {
                        // Do not follow junctions out of the copy; the size would be somebody
                        // else's and the number would be a lie.
                        try
                        {
                            if ((new DirectoryInfo(directory).Attributes & FileAttributes.ReparsePoint) != 0)
                                continue;
                        }
                        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                        {
                            continue;
                        }

                        pending.Push(directory);
                    }
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
                {
                    // Skip what cannot be read rather than reporting zero for the whole copy.
                }
            }

            return total;
        }

        private static SafeCopyOverview Describe(SafeCopySaveInventory inventory)
        {
            DateTime created;
            DateTime lastUsed;
            try
            {
                created = Directory.GetCreationTimeUtc(inventory.ProfileRoot);
                lastUsed = Directory.GetLastWriteTimeUtc(inventory.ProfileRoot);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                created = DateTime.MinValue;
                lastUsed = DateTime.MinValue;
            }

            return new SafeCopyOverview(
                DisplayName: inventory.DisplayName,
                ProfileRoot: inventory.ProfileRoot,
                SizeBytes: MeasureDirectoryBytes(inventory.ProfileRoot),
                CreatedUtc: created,
                LastUsedUtc: lastUsed,
                CareerSaveCount: inventory.Saves.Count,
                Playable: File.Exists(Path.Combine(inventory.ProfileRoot, "BEA.exe")));
        }
    }
}
