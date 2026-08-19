using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences the safe-copy manager shows.
    ///
    /// The list exists because the app could make multi-gigabyte copies and never show them: no
    /// list, no size, no total, and the only route that removed one was a CLI verb. So the words
    /// here lead with the number that made somebody come looking.
    ///
    /// The delete wording carries the weight. A copy is disposable; the careers played inside it
    /// are not, and they are the one thing in that folder the game cannot make again. The dialog
    /// therefore never asks a single yes/no question when careers are present - it offers keeping
    /// them as the first and default answer.
    /// </summary>
    internal static class SafeCopyManagerText
    {
        public const string SectionTitle = "Your safe copies";

        public const string Introduction =
            "Each copy is most of a game install. They stay on disk until you remove them, so this is where "
            + "you can see what they cost and clear out the ones you are done with.";

        public const string RefreshButtonText = "Look again";

        public const string EmptyNote =
            "Create one above and it will show up here.";

        public const string CurrentPatchesNoExecutable =
            "This copy has no BEA.exe, so its patches cannot be read.";

        public const string CurrentPatchesUnreadable =
            "This copy's current patch state could not be read.";

        public const string CurrentPatchesInstalledGame =
            "That is your installed game. This list only reads a copy.";

        public const string CurrentPatchesAllOriginal =
            "This copy still has original bytes for every listed catalog patch.";

        public const string CurrentPatchesAllPatched =
            "This copy already has every listed catalog patch.";

        /// <summary>
        /// What this copy's BEA.exe currently has for the listed catalog patches.
        /// Names the patches, never the folder.
        /// </summary>
        public static string DescribeCurrentPatches(
            BinaryPatchCopyInspectRefusal refusal,
            IReadOnlyList<(string DisplayName, BinaryPatchState State)> rows)
        {
            return refusal switch
            {
                BinaryPatchCopyInspectRefusal.NoExecutable => CurrentPatchesNoExecutable,
                BinaryPatchCopyInspectRefusal.Unreadable => CurrentPatchesUnreadable,
                BinaryPatchCopyInspectRefusal.InstalledGame => CurrentPatchesInstalledGame,
                _ => DescribeCurrentPatchRows(rows),
            };
        }

        private static string DescribeCurrentPatchRows(
            IReadOnlyList<(string DisplayName, BinaryPatchState State)> rows)
        {
            ArgumentNullException.ThrowIfNull(rows);
            if (rows.Count == 0)
                return CurrentPatchesAllOriginal;

            string[] unexpected = rows
                .Where(row => row.State is BinaryPatchState.Mismatch or BinaryPatchState.OutOfRange)
                .Select(row => row.DisplayName)
                .Where(name => !string.IsNullOrWhiteSpace(name))
                .ToArray();
            if (unexpected.Length > 0)
            {
                return unexpected.Length == 1
                    ? $"This copy's bytes for {unexpected[0]} do not match original or patched."
                    : $"This copy's bytes for {JoinNames(unexpected)} do not match original or patched.";
            }

            string[] patched = rows
                .Where(row => row.State == BinaryPatchState.Patched)
                .Select(row => row.DisplayName)
                .Where(name => !string.IsNullOrWhiteSpace(name))
                .ToArray();
            if (patched.Length == 0)
                return CurrentPatchesAllOriginal;
            if (patched.Length == rows.Count)
                return CurrentPatchesAllPatched;
            if (patched.Length > 5)
                return $"This copy already has {patched.Length} listed catalog patches.";

            return $"This copy already has {JoinNames(patched)}.";
        }

        private static string JoinNames(IReadOnlyList<string> names)
        {
            if (names.Count == 1)
                return names[0];
            if (names.Count == 2)
                return $"{names[0]} and {names[1]}";

            return string.Join(", ", names.Take(names.Count - 1)) + ", and " + names[^1];
        }

        public const string DeleteDialogTitle = "Delete this copy?";

        public const string KeepCareersButtonText = "Keep my careers";

        public const string DeleteEverythingButtonText = "Delete it all";

        public const string CancelButtonText = "Cancel";

        /// <summary>The line above the list: how many, and how much.</summary>
        public static string BuildTotalLine(IReadOnlyList<SafeCopyOverview> copies)
        {
            ArgumentNullException.ThrowIfNull(copies);
            if (copies.Count == 0)
                return EmptyNote;

            string count = copies.Count == 1 ? "1 safe copy" : $"{copies.Count} safe copies";
            string size = SafeCopyCatalogService.DescribeSize(SafeCopyCatalogService.TotalSizeBytes(copies));
            int careers = copies.Sum(copy => copy.CareerSaveCount);

            return careers == 0
                ? $"{count}, using {size}."
                : $"{count}, using {size}, holding {(careers == 1 ? "1 career" : $"{careers} careers")} between them.";
        }

        /// <summary>
        /// What the delete dialog says when the copy is holding careers. It names them, because
        /// "this may delete save data" is a sentence people click past and "this deletes Maladim"
        /// is not.
        /// </summary>
        public static string BuildDeleteWithCareersBody(SafeCopySaveInventory inventory, string sizeText)
        {
            ArgumentNullException.ThrowIfNull(inventory);

            string? atRisk = SafeCopySaveRescueService.DescribeSavesAtRisk(inventory);
            return $"{atRisk}\n\n"
                + $"Keep my careers copies them somewhere you choose first, and only deletes the copy once every one "
                + $"of them is safely there. Delete it all removes the {sizeText} folder and the careers with it, and "
                + "that cannot be undone.";
        }

        /// <summary>What it says when there is nothing inside worth keeping.</summary>
        public static string BuildDeleteBody(string displayName, string sizeText)
        {
            return $"This removes {displayName} and the {sizeText} it is using. There are no careers inside it, and "
                + "the game files can all be copied again from your install.";
        }

        public static string BuildDeletedNote(string displayName, string sizeText)
        {
            return $"Deleted {displayName} and freed {sizeText}.";
        }

        public static string DescribeLaunchFailure(string displayName)
        {
            return $"Could not launch {displayName}. Nothing was changed.";
        }

        public const string CheckFailure =
            "That copy could not be checked. Nothing was changed.";

        public const string CopyMustStayInside =
            "That copy must stay inside the profile folder.";

        public static string DescribeDeleteFailure(string displayName)
        {
            return $"Could not delete {displayName}. Nothing was changed.";
        }

        /// <summary>
        /// What RescueThenDelete did. Named here so the page never paints a
        /// <c>SafeCopyRemovalResult.Message</c> that still carries a dump.
        /// </summary>
        public static string DescribeRemovalOutcome(SafeCopyRemovalResult removal, string displayName, string sizeText)
        {
            if (removal.Success)
            {
                if (!LooksLikeAPathOrDump(removal.Message) && !string.IsNullOrWhiteSpace(removal.Message))
                    return $"{removal.Message} Freed {sizeText}.";

                return BuildDeletedNote(displayName, sizeText);
            }

            if (LooksLikeAPathOrDump(removal.Message) || string.IsNullOrWhiteSpace(removal.Message))
                return DescribeDeleteFailure(displayName);

            if (string.Equals(removal.Message, SafeCopySaveRescueService.CopyMustStayInside, StringComparison.Ordinal))
                return CopyMustStayInside;

            return removal.Message;
        }

        private static bool LooksLikeAPathOrDump(string? message)
        {
            if (string.IsNullOrWhiteSpace(message))
                return false;

            return message.Contains(":\\", StringComparison.Ordinal)
                || message.Contains(":/", StringComparison.Ordinal)
                || message.Contains("Win32", StringComparison.OrdinalIgnoreCase)
                || message.Contains("exception", StringComparison.OrdinalIgnoreCase);
        }

        /// <summary>
        /// The warning before creating a copy on a volume that cannot fit it.
        ///
        /// Null when there is room, or when free space could not be read - a drive that will not
        /// report is a drive the app knows nothing about, and refusing on that basis would be
        /// inventing a problem.
        /// </summary>
        public static string? DescribeSpaceProblem(long? freeSpaceBytes, long sourceSizeBytes)
        {
            if (SafeCopyCatalogService.HasRoomForCopy(freeSpaceBytes, sourceSizeBytes))
                return null;

            return $"This copy needs about {SafeCopyCatalogService.DescribeSize(sourceSizeBytes)} and there is "
                + $"{SafeCopyCatalogService.DescribeSize(freeSpaceBytes!.Value)} free. Clear some space, or delete a "
                + "copy you are finished with below.";
        }
    }
}
