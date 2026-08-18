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
    }
}
