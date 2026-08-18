using System;
using System.IO;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences the Save Lab shows about bringing a career back out of a safe copy.
    ///
    /// They live here rather than in the page so they can be tested without a running app, the same
    /// way <see cref="CheatsPageText"/> holds the Cheats page's wording.
    ///
    /// The reason this section exists at all is worth keeping next to the words. The app could put
    /// a save into a copy and had no way to get one back, while the only deletion it offered was a
    /// recursive delete of the whole copy folder - so a career played inside a copy was one
    /// cleanup away from gone, with no warning. Everything else in a copy is a duplicate of the
    /// installed game. The careers are not.
    /// </summary>
    internal static class SaveRescuePageText
    {
        public const string SectionTitle = "Bring a career out of a copy";

        public const string Introduction =
            "Careers you play inside a safe copy are kept inside that copy. This puts one in a folder of "
            + "your own, so it is still there when the copy is not.";

        public const string CopyLabel = "Safe copy";

        public const string SaveLabel = "Career";

        public const string RescueButtonText = "Keep it somewhere else";

        /// <summary>
        /// The accessible name for the rescue button. It has to contain the visible label word for
        /// word - the accessibility audit enforces that - so it reads as the label plus what
        /// happens next.
        /// </summary>
        public const string RescueButtonAccessibleName =
            "Keep it somewhere else, by choosing a folder to copy the career into";

        public const string RefreshButtonText = "Look again for copies";

        public const string NoCopiesNote =
            "No safe copies on this machine. Make one in Windowed & Mods, play a career in it, and it will "
            + "show up here.";

        public const string NothingChosenNote = "Pick a copy and a career.";

        /// <summary>
        /// Said once, plainly, where somebody deciding whether to bother will read it. The copy is
        /// left playable, so this is never a one-way move.
        /// </summary>
        public const string CopyNotMoveNote =
            "The career stays in the copy as well - this copies it out, it does not take it away.";

        public static string BuildNoSavesNote(string copyDisplayName)
        {
            return string.IsNullOrWhiteSpace(copyDisplayName)
                ? "That copy has no careers in it yet."
                : $"{copyDisplayName} has no careers in it yet.";
        }

        /// <summary>One line naming what is about to be copied and out of where.</summary>
        public static string BuildSelectionSummary(SafeCopySaveInventory? copy, SafeCopySaveFile? save)
        {
            if (copy is null)
                return NoCopiesNote;

            if (!copy.HasSaves)
                return BuildNoSavesNote(copy.DisplayName);

            if (save is null)
                return NothingChosenNote;

            return $"{Path.GetFileNameWithoutExtension(save.FileName)}, from {copy.DisplayName}. {CopyNotMoveNote}";
        }

        /// <summary>
        /// What happened, in the voice the rest of the page uses: what landed, and where it is.
        /// The folder is named, never shown as a full path.
        /// </summary>
        public static string BuildOutcomeNote(SafeCopySaveRescueResult result)
        {
            ArgumentNullException.ThrowIfNull(result);

            if (!result.Success)
            {
                if (CareerSaveLocation.Classify(result.DestinationDirectory) == CareerSaveLocationKind.InstalledGame)
                    return CareerSaveLocation.InstalledDestinationRefused;

                return result.Message;
            }

            string leaf = FolderLeaf(result.DestinationDirectory);
            return string.IsNullOrWhiteSpace(leaf)
                ? $"{result.Message} They are in the folder you chose."
                : $"{result.Message} They are in the folder \"{leaf}\".";
        }

        /// <summary>
        /// Null when the write may proceed. The same installed-game sentence Cheats uses,
        /// so a folder picker cannot become a second classifier.
        /// </summary>
        public static string? DescribeDestinationRefusal(string? folder)
        {
            return CareerSaveLocation.Classify(folder) == CareerSaveLocationKind.InstalledGame
                ? CareerSaveLocation.InstalledDestinationRefused
                : null;
        }

        private static string FolderLeaf(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
                return string.Empty;

            try
            {
                return Path.GetFileName(Path.TrimEndingDirectorySeparator(path.Trim()));
            }
            catch (ArgumentException)
            {
                return string.Empty;
            }
        }

        /// <summary>How a career reads in the picker: its name, and when it was last played.</summary>
        public static string DescribeSave(SafeCopySaveFile save)
        {
            ArgumentNullException.ThrowIfNull(save);
            return $"{Path.GetFileNameWithoutExtension(save.FileName)}  -  {save.LastWriteUtc.ToLocalTime():d MMM yyyy}";
        }
    }
}
