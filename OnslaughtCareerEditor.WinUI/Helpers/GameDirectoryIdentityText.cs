using System.IO;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences Settings and Home show about whether the chosen BEA.exe is the known
    /// Steam retail file. Kept out of the pages so the wording can be tested without a
    /// running app, and so those pages cannot call a changed executable the original.
    /// </summary>
    internal static class GameDirectoryIdentityText
    {
        public const string KnownRetailSettingsLine =
            "This BEA.exe matches the known Steam retail file. Copies start from that original.";

        public const string ChangedSettingsLine =
            "This BEA.exe is not the known Steam retail file. A copy made from it will carry those changes. " +
            "Do not treat this file as an original.";

        public const string UnreadableSettingsLine =
            "The app could not read BEA.exe just now, so it cannot say whether this is the known Steam retail file.";

        public const string ChangedHomeGuidance =
            "This install's BEA.exe is not the known Steam retail file. A playable copy will start from what is there now. " +
            "Windowed & Mods still leaves the installed game alone unless you ask it to change it.";

        public const string UnreadableHomeGuidance =
            "The app could not read BEA.exe just now, so it cannot say whether this is the known Steam retail file. " +
            "Windowed & Mods still works on a separate copy unless you ask it to change the installed game.";

        public const string AutoDetectFailed =
            "Could not find the game automatically. Choose the folder you installed it into - the one holding BEA.exe.";

        /// <summary>
        /// Settings already painted the chosen folder before persist. If the
        /// write fails, this sentence has to replace that picture so the page
        /// does not look saved.
        /// </summary>
        public const string PersistFailed =
            "Could not keep that folder. Nothing was changed. Try choosing it again.";

        public const string AppearancePersistFailed =
            "Could not keep that look. Nothing was changed. Try choosing it again.";

        public const string MediaPersistFailed =
            "Could not keep those media choices. Nothing was changed. Try them again.";

        public static string ForSettings(RetailExecutableIdentity identity)
        {
            return identity switch
            {
                RetailExecutableIdentity.KnownCleanRetail => KnownRetailSettingsLine,
                RetailExecutableIdentity.DifferentFromKnownRetail => ChangedSettingsLine,
                RetailExecutableIdentity.Unreadable => UnreadableSettingsLine,
                _ => string.Empty,
            };
        }

        public static bool IsWarning(RetailExecutableIdentity identity) =>
            identity is RetailExecutableIdentity.DifferentFromKnownRetail
                or RetailExecutableIdentity.Unreadable;

        public static string ForHomeGuidance(RetailExecutableIdentity identity, string defaultGuidance)
        {
            return identity switch
            {
                RetailExecutableIdentity.DifferentFromKnownRetail => ChangedHomeGuidance,
                RetailExecutableIdentity.Unreadable => UnreadableHomeGuidance,
                _ => defaultGuidance,
            };
        }

        /// <summary>
        /// Settings-file details name the file and its parent folder. The full path stays off the page.
        /// </summary>
        public static string BuildConfigPathSummary(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "No settings file selected";
            }

            string trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string name = Path.GetFileName(trimmed);
            string? parent = Path.GetFileName(Path.GetDirectoryName(trimmed) ?? string.Empty);
            if (string.IsNullOrWhiteSpace(parent))
            {
                return string.IsNullOrWhiteSpace(name) ? "Settings file" : name;
            }

            return $"{name} in {parent}";
        }

        /// <summary>
        /// Folder cards name the last path segment. The full path stays off the page.
        /// </summary>
        public static string BuildFolderSummary(string? path, string fallback)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return fallback;
            }

            string trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string name = Path.GetFileName(trimmed);
            return string.IsNullOrWhiteSpace(name) ? fallback : name;
        }
    }
}
