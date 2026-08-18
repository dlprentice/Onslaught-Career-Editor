using System;
using System.IO;

namespace OnslaughtCareerEditor.AppCore
{
    public enum CareerSaveLocationKind
    {
        Missing,
        InstalledGame,
        SafeCopy,
        ChosenFolder,
    }

    /// <summary>
    /// Where a career save is sitting. Layout only: it never writes, and it never treats a
    /// playable copy this app made as the installed game even though that copy also has
    /// BEA.exe and a data folder. A directory can be classified the same way as a file
    /// inside it, so a destination folder uses this instead of a second walk.
    /// </summary>
    public static class CareerSaveLocation
    {
        public static CareerSaveLocationKind Classify(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
                return CareerSaveLocationKind.Missing;

            bool isFile = File.Exists(path);
            bool isDirectory = !isFile && Directory.Exists(path);
            if (!isFile && !isDirectory)
                return CareerSaveLocationKind.Missing;

            string fullPath = Path.GetFullPath(path);
            string? current = isFile ? Path.GetDirectoryName(fullPath) : fullPath;
            bool sawInstalledLayout = false;

            while (!string.IsNullOrWhiteSpace(current))
            {
                if (File.Exists(Path.Combine(current, GameProfilePreflightService.ProfileManifestFileName)))
                    return CareerSaveLocationKind.SafeCopy;

                if (File.Exists(Path.Combine(current, "BEA.exe")) &&
                    Directory.Exists(Path.Combine(current, "data")))
                {
                    sawInstalledLayout = true;
                }

                string? parent = Path.GetDirectoryName(current);
                if (string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                    break;
                current = parent;
            }

            return sawInstalledLayout
                ? CareerSaveLocationKind.InstalledGame
                : CareerSaveLocationKind.ChosenFolder;
        }
    }
}
