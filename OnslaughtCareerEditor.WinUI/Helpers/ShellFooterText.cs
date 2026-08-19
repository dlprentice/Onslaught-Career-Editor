using System.IO;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The footer names the game folder by its last segment. Kept out of the
    /// window so a tooltip cannot quietly become the full path again.
    /// </summary>
    internal static class ShellFooterText
    {
        public static string BuildFolderLabel(string? gameDir)
        {
            if (string.IsNullOrWhiteSpace(gameDir))
            {
                return "Not set";
            }

            string trimmed = gameDir.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string folderName = Path.GetFileName(trimmed);
            return string.IsNullOrWhiteSpace(folderName) ? "Configured" : folderName;
        }

        public static string DescribeReadyTooltip(string? gameDir)
        {
            string name = BuildFolderLabel(gameDir);
            return name is "Not set" or "Configured"
                ? "The game folder is ready."
                : $"Using the folder \"{name}\".";
        }

        public const string NeedsFolderTooltip =
            "Open Settings and choose the folder that has BEA.exe and data.";
    }
}
