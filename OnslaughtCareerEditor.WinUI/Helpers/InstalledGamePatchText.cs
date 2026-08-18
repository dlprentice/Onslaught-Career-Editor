using System;
using System.IO;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>What the app can currently do to the installed game, and why.</summary>
    public enum InstalledGamePatchReadiness
    {
        /// <summary>No install has been chosen or found yet.</summary>
        NoGameChosen,

        /// <summary>A backup and its recorded hash are both there. Patch and Put back are both live.</summary>
        BackedUp,

        /// <summary>The game is still as it shipped. Backing it up is a copy away.</summary>
        CleanAndUnbackedUp,

        /// <summary>
        /// Something already changed this executable and there is no original beside it, so the app
        /// cannot promise to put anything back and will not pretend otherwise.
        /// </summary>
        ChangedWithNothingToGoBackTo,

        /// <summary>
        /// The file is there but cannot be read right now. That is not the same as "already
        /// changed" - the game being open is enough to lock BEA.exe.
        /// </summary>
        Unreadable,
    }

    /// <summary>
    /// The sentences the Windowed &amp; Mods page shows about patching the installed game.
    ///
    /// This is the one place in the app that offers to change something the user cannot simply
    /// recreate, so the copy carries more weight than usual. Two things have to come across before
    /// anybody presses anything: that this is the real game and not a copy, and that a verified
    /// original is made first and is what Put back uses. Neither may end up behind a disclosure.
    ///
    /// The words are here rather than in the page so they can be tested without a running app, and
    /// so the page cannot drift into promising something the engine does not do. In particular the
    /// engine restores a whole-file snapshot taken before the first patch - it is not a per-patch
    /// undo, and nothing here may imply that it is.
    /// </summary>
    internal static class InstalledGamePatchText
    {
        public const string SectionTitle = "Or change the game you installed";

        public const string Introduction =
            "A safe copy is the sandbox. If you would rather just play your own install patched, this does "
            + "that - and it copies your original executable first, so you can put it back.";

        public const string BackupButtonText = "Back up my game";

        public const string BackupButtonAccessibleName =
            "Back up my game, copying the original executable so it can be put back later";

        public const string PatchButtonText = "Patch my installed game";

        public const string PatchButtonAccessibleName =
            "Patch my installed game, after copying and verifying the original executable";

        public const string RestoreButtonText = "Put my game back";

        public const string RestoreButtonAccessibleName =
            "Put my game back to the original executable that was copied before patching";

        /// <summary>
        /// Said plainly, on screen, with nothing to open. A person deciding whether to press the
        /// button has to know what Put back actually returns them to.
        /// </summary>
        public const string RestoreScopeNote =
            "Put my game back restores the whole executable as it was before the first patch. It undoes every "
            + "patch at once, not the last one, and it does not touch your saves, options or anything else in "
            + "the folder.";

        public const string ConfirmPatchTitle = "Patch the game you installed?";

        public const string ConfirmRestoreTitle = "Put your game back?";

        public const string ConfirmPatchPrimaryButton = "Patch it";

        public const string ConfirmRestorePrimaryButton = "Put it back";

        public const string ConfirmCloseButton = "Cancel";

        /// <summary>The state line, in the terms somebody deciding needs.</summary>
        public static string BuildStatusLine(InstalledGamePatchReadiness readiness, string? exePath)
        {
            return readiness switch
            {
                InstalledGamePatchReadiness.NoGameChosen =>
                    "No installed game chosen yet. Pick your game folder in Settings, or browse to a BEA.exe below.",
                InstalledGamePatchReadiness.BackedUp =>
                    "Your original executable is saved beside the game as BEA.exe.original.backup. "
                        + "Patching from here can be undone.",
                InstalledGamePatchReadiness.CleanAndUnbackedUp =>
                    "Your game is as it shipped. Nothing has been backed up yet - patching will copy the original first.",
                InstalledGamePatchReadiness.ChangedWithNothingToGoBackTo =>
                    "Something has already changed this BEA.exe, and there is no original beside it. The app will not " +
                        "copy a changed file and call it the original, so patching stays off until the game is " +
                        "verified or reinstalled.",
                InstalledGamePatchReadiness.Unreadable =>
                    "The app could not read BEA.exe just now, so it cannot say whether this is as it shipped. " +
                        "Patching stays off until the file can be read.",
                _ => string.Empty,
            } + DescribeWhere(exePath);
        }

        private static string DescribeWhere(string? exePath)
        {
            return string.IsNullOrWhiteSpace(exePath)
                ? string.Empty
                : $" ({Path.GetDirectoryName(exePath)})";
        }

        /// <summary>
        /// What the confirmation dialog says. It names the folder, because the whole risk of this
        /// action is somebody believing it is pointed somewhere else.
        /// </summary>
        public static string BuildPatchConfirmation(string exePath, string patchSummary)
        {
            return $"This changes the game in:\n{Path.GetDirectoryName(exePath)}\n\n"
                + $"Changes: {patchSummary}\n\n"
                + "Your original executable is copied and checked before anything is written. If the copy cannot be "
                + "made, nothing is patched. Put my game back returns it afterwards.";
        }

        public static string BuildRestoreConfirmation(string exePath)
        {
            return $"This puts back the original executable in:\n{Path.GetDirectoryName(exePath)}\n\n"
                + RestoreScopeNote;
        }

        /// <summary>
        /// The outcome line. Success repeats where the original lives, because that is the sentence
        /// somebody will want three weeks later when they have forgotten doing this.
        /// </summary>
        public static string BuildOutcomeNote(bool success, string message)
        {
            return success ? message : $"Nothing was changed. {message}";
        }

        /// <summary>
        /// Whether the app is willing to offer each action. Kept out of the page so the enable
        /// rules can be read and tested in one place instead of inferred from three IsEnabled lines.
        /// </summary>
        public static bool CanBackUp(InstalledGamePatchReadiness readiness) =>
            readiness is InstalledGamePatchReadiness.CleanAndUnbackedUp;

        public static bool CanPatch(InstalledGamePatchReadiness readiness) =>
            readiness is InstalledGamePatchReadiness.BackedUp or InstalledGamePatchReadiness.CleanAndUnbackedUp;

        public static bool CanRestore(InstalledGamePatchReadiness readiness) =>
            readiness is InstalledGamePatchReadiness.BackedUp;

        /// <summary>
        /// Read the state of an installed game without changing anything.
        ///
        /// Deliberately does not call <c>AuthorizeInstalledGameWrite</c>: that would write a backup
        /// as a side effect of drawing a page, which is exactly the kind of quiet mutation this
        /// section exists to avoid.
        /// </summary>
        public static InstalledGamePatchReadiness DescribeReadiness(string? exePath)
        {
            if (string.IsNullOrWhiteSpace(exePath) || !File.Exists(exePath))
                return InstalledGamePatchReadiness.NoGameChosen;

            try
            {
                string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
                string backupHashPath = BinaryPatchEngine.BuildBackupHashPath(exePath);
                if (File.Exists(backupPath))
                {
                    // A backup with no recorded hash is still a route back - the app writes the
                    // missing hash itself when permission is asked for - so this is BackedUp, not
                    // a problem to report.
                    _ = backupHashPath;
                    return InstalledGamePatchReadiness.BackedUp;
                }

                return BinaryPatchEngine.IdentifyRetailExecutable(exePath) switch
                {
                    RetailExecutableIdentity.KnownCleanRetail => InstalledGamePatchReadiness.CleanAndUnbackedUp,
                    RetailExecutableIdentity.Unreadable => InstalledGamePatchReadiness.Unreadable,
                    RetailExecutableIdentity.DifferentFromKnownRetail =>
                        InstalledGamePatchReadiness.ChangedWithNothingToGoBackTo,
                    _ => InstalledGamePatchReadiness.NoGameChosen,
                };
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
            {
                return InstalledGamePatchReadiness.NoGameChosen;
            }
        }
    }
}
