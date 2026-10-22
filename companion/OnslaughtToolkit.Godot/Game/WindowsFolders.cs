// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// Two Windows folder rules, written as plain functions of the folders they are given so they can be checked on any
/// system. Neither has been run on Windows yet (README, Known limits).
/// </summary>
public static class WindowsFolders
{
    /// <summary>The folder under the local application data folder that holds the companion's backups on Windows.</summary>
    public const string LocalFolderName = "Onslaught Companion";

    /// <summary>
    /// Where the backup folder goes unless the player chooses another. On Windows that is the local application data
    /// folder (<c>%LOCALAPPDATA%\Onslaught Companion</c>), which Windows never syncs: Documents is often a OneDrive
    /// folder whose files can be online-only placeholders, and the companion refuses to back up into a tree with such
    /// reparse points, which would refuse every write. Elsewhere it is Documents. Without either, the app's own data
    /// folder.
    /// </summary>
    public static string DefaultBackupRoot(bool windows, string? documents, string? localAppData, string userData)
    {
        if (windows)
            return !string.IsNullOrWhiteSpace(localAppData) && Directory.Exists(localAppData)
                ? Path.Combine(localAppData, LocalFolderName) : userData;
        return !string.IsNullOrWhiteSpace(documents) && Directory.Exists(documents) ? documents : userData;
    }

    /// <summary>
    /// When the game is installed under a Program Files folder, Windows can redirect what the game saves into its own
    /// folder to <c>%LOCALAPPDATA%\VirtualStore\&lt;the same path without its drive&gt;</c> (file virtualization, for older
    /// programs that may not write there). This names that folder's <c>savegames</c>; null when the game is not under
    /// one of <paramref name="programFolders"/> or there is no local application data folder.
    /// </summary>
    public static string? VirtualStoreSaves(string gameRoot, string? localAppData, IEnumerable<string?> programFolders)
    {
        if (string.IsNullOrWhiteSpace(gameRoot) || string.IsNullOrWhiteSpace(localAppData)) return null;
        string game = gameRoot.TrimEnd('\\', '/');
        foreach (string? folder in programFolders)
        {
            if (string.IsNullOrWhiteSpace(folder)) continue;
            string program = folder.TrimEnd('\\', '/');
            if (!game.StartsWith(program, StringComparison.OrdinalIgnoreCase) || game.Length == program.Length ||
                game[program.Length] is not ('\\' or '/'))
                continue;
            string withoutDrive = game.Length > 1 && game[1] == ':' ? game[2..] : game;
            string[] parts = withoutDrive.Split(['\\', '/'], StringSplitOptions.RemoveEmptyEntries);
            return Path.Combine([localAppData, "VirtualStore", .. parts, "savegames"]);
        }
        return null;
    }

    /// <summary>The <see cref="VirtualStoreSaves"/> folder for this computer: Windows only, null elsewhere.</summary>
    public static string? VirtualStoreSavesHere(string gameRoot) =>
        OperatingSystem.IsWindows()
            ? VirtualStoreSaves(gameRoot, Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                [Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86),
                 Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles)])
            : null;

    /// <summary>The <c>.bes</c> files directly in <paramref name="folder"/>, by name; linked files and an unreadable folder count as none.</summary>
    public static IReadOnlyList<string> Careers(string? folder)
    {
        if (string.IsNullOrWhiteSpace(folder)) return [];
        try
        {
            DirectoryInfo saves = new(folder);
            if (!saves.Exists || (saves.Attributes & FileAttributes.ReparsePoint) != 0) return [];
            return saves.GetFiles()
                .Where(file => (file.Attributes & FileAttributes.ReparsePoint) == 0 &&
                    string.Equals(file.Extension, ".bes", StringComparison.OrdinalIgnoreCase))
                .Select(file => file.Name).Order(StringComparer.OrdinalIgnoreCase).ToArray();
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return [];
        }
    }
}
