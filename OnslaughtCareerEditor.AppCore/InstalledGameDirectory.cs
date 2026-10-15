using System;
using System.IO;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// Whether a path looks like a real Battle Engine Aquila installation rather than an
    /// app-owned copy. <see cref="BinaryPatchEngine"/> refuses to inspect such a path from a
    /// list of copies; writing to an installed game goes through
    /// <see cref="BinaryPatchEngine.AuthorizeInstalledGameWrite"/> instead. Moved verbatim from
    /// the retired live trainer's attach policy, which shared it.
    /// </summary>
    public static class InstalledGameDirectory
    {
        public static bool LooksLikeAnInstalledGameDirectory(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
                return false;

            string fullPath;
            try
            {
                fullPath = Path.GetFullPath(path);
            }
            catch (Exception ex) when (ex is ArgumentException or NotSupportedException or PathTooLongException or IOException)
            {
                // A path the app cannot even normalize is not a path it is going to open.
                return true;
            }

            string[] parts = fullPath.Split(
                new[] { Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar },
                StringSplitOptions.RemoveEmptyEntries);

            for (int i = 0; i <= parts.Length - 3; i++)
            {
                if (string.Equals(parts[i], "steamapps", StringComparison.OrdinalIgnoreCase) &&
                    string.Equals(parts[i + 1], "common", StringComparison.OrdinalIgnoreCase) &&
                    string.Equals(parts[i + 2], "Battle Engine Aquila", StringComparison.OrdinalIgnoreCase))
                {
                    return true;
                }
            }

            foreach (Environment.SpecialFolder folder in new[]
                     {
                         Environment.SpecialFolder.ProgramFiles,
                         Environment.SpecialFolder.ProgramFilesX86,
                         Environment.SpecialFolder.Windows,
                     })
            {
                string root = Environment.GetFolderPath(folder);
                if (string.IsNullOrWhiteSpace(root))
                    continue;

                string normalizedRoot = Path.GetFullPath(root)
                    .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) + Path.DirectorySeparatorChar;
                if (fullPath.StartsWith(normalizedRoot, StringComparison.OrdinalIgnoreCase))
                    return true;
            }

            return false;
        }
    }
}
