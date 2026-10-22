// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>A career left in one of the retired Windows toolkit's copied installs.</summary>
public sealed record OldCopyCareer(string Copy, string Path)
{
    public string Name => System.IO.Path.GetFileNameWithoutExtension(Path);
}

/// <summary>
/// The retired Windows toolkit (WinUI v1.0.11) could copy the game into
/// <c>%APPDATA%\OnslaughtCareerEditor\GameProfiles\&lt;copy&gt;</c> and play the copy ("safe launch"), so careers
/// played that way were saved in the copy's <c>savegames</c> folder, where the game and the companion never look.
/// This lists them so each can be saved as a protected copy elsewhere. It only reads: nothing there is changed,
/// moved or deleted, and linked folders and files are skipped.
/// </summary>
public static class OldSafeCopies
{
    /// <summary>The old toolkit's copies folder on Windows; null elsewhere, where that toolkit never ran.</summary>
    public static string? DefaultRoot() =>
        OperatingSystem.IsWindows() && Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData) is { Length: > 0 } appData
            ? System.IO.Path.Combine(appData, "OnslaughtCareerEditor", "GameProfiles")
            : null;

    /// <summary>
    /// Every career-sized <c>.bes</c> file in a copy's <c>savegames</c> folder, by copy then name. A folder that
    /// cannot be read is skipped rather than failing the list.
    /// </summary>
    public static IReadOnlyList<OldCopyCareer> Find(string? root)
    {
        if (string.IsNullOrWhiteSpace(root) || !Directory.Exists(root) || IsLink(new DirectoryInfo(root))) return [];
        List<OldCopyCareer> found = [];
        foreach (DirectoryInfo copy in Read(() => new DirectoryInfo(root).GetDirectories())
            .Where(copy => !IsLink(copy)).OrderBy(copy => copy.Name, StringComparer.OrdinalIgnoreCase))
        {
            DirectoryInfo saves = new(System.IO.Path.Combine(copy.FullName, "savegames"));
            if (!saves.Exists || IsLink(saves)) continue;
            found.AddRange(Read(saves.GetFiles)
                .Where(file => !IsLink(file) && string.Equals(file.Extension, ".bes", StringComparison.OrdinalIgnoreCase) &&
                    file.Length == CareerSave.Size)
                .OrderBy(file => file.Name, StringComparer.OrdinalIgnoreCase)
                .Select(file => new OldCopyCareer(copy.Name, file.FullName)));
        }
        return found;
    }

    private static bool IsLink(FileSystemInfo entry) => (entry.Attributes & FileAttributes.ReparsePoint) != 0;

    private static T[] Read<T>(Func<T[]> list)
    {
        try
        {
            return list();
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return [];
        }
    }
}
