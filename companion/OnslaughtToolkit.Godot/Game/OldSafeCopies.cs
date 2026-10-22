// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// A <c>.bes</c> file left in one of the retired Windows toolkit's copied installs. <see cref="Folder"/> is the
/// folder inside the copy it was found in (<c>savegames</c> for almost all of them, empty at the copy's root).
/// Only a career-sized file (<see cref="CanCopy"/>) can be saved elsewhere; any other is still listed, so a career
/// never disappears without a word.
/// </summary>
public sealed record OldCopyCareer(string Copy, string Folder, string Path, long Length)
{
    public string Name => System.IO.Path.GetFileNameWithoutExtension(Path);

    public bool CanCopy => Length == CareerSave.Size;

    /// <summary>Where it is, as a player would say it: the copy, and the folder inside it unless that is <c>savegames</c>.</summary>
    public string Where => Folder is "savegames" ? Copy : Folder.Length == 0 ? Copy + " (top folder)" : Copy + "/" + Folder;
}

/// <summary>
/// The retired Windows toolkit (WinUI v1.0.11) could copy the game into
/// <c>%APPDATA%\OnslaughtCareerEditor\GameProfiles\&lt;copy&gt;</c> and play the copy ("safe launch"), so careers
/// played that way were saved inside the copy, where the game and the companion never look. This lists them so
/// each can be saved as a protected copy elsewhere. It searches the folders that toolkit's own rescue searched
/// (<c>savegames</c>, <c>saves</c>, <c>Save</c> and the copy's root) and lists every <c>.bes</c> there of any
/// length; <c>defaultoptions.bea</c> ships in every copy and is not a career. It only reads: nothing there is
/// changed, moved or deleted, and linked folders and files are skipped.
/// </summary>
public static class OldSafeCopies
{
    /// <summary>The folders inside a copy that the old toolkit's rescue searched, in its order; empty is the root.</summary>
    public static readonly IReadOnlyList<string> SaveFolders = ["savegames", "saves", "Save", ""];

    /// <summary>The old toolkit's copies folder on Windows; null elsewhere, where that toolkit never ran.</summary>
    public static string? DefaultRoot() =>
        OperatingSystem.IsWindows() && Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData) is { Length: > 0 } appData
            ? System.IO.Path.Combine(appData, "OnslaughtCareerEditor", "GameProfiles")
            : null;

    /// <summary>
    /// Every <c>.bes</c> file in a copy's save folders, by copy, then folder, then name. A folder that cannot be read
    /// is skipped rather than failing the list, and a file reached twice is listed once.
    /// </summary>
    public static IReadOnlyList<OldCopyCareer> Find(string? root)
    {
        if (string.IsNullOrWhiteSpace(root) || !Directory.Exists(root) || IsLink(new DirectoryInfo(root))) return [];
        StringComparer paths = OperatingSystem.IsWindows() || OperatingSystem.IsMacOS() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal;
        List<OldCopyCareer> found = [];
        foreach (DirectoryInfo copy in Read(() => new DirectoryInfo(root).GetDirectories())
            .Where(copy => !IsLink(copy)).OrderBy(copy => copy.Name, StringComparer.OrdinalIgnoreCase))
        {
            HashSet<string> seen = new(paths);
            foreach (string folder in SaveFolders)
            {
                DirectoryInfo saves = folder.Length == 0 ? copy : new(System.IO.Path.Combine(copy.FullName, folder));
                if (!saves.Exists || IsLink(saves)) continue;
                found.AddRange(Read(saves.GetFiles)
                    .Where(file => !IsLink(file) && string.Equals(file.Extension, ".bes", StringComparison.OrdinalIgnoreCase) &&
                        seen.Add(file.FullName))
                    .OrderBy(file => file.Name, StringComparer.OrdinalIgnoreCase)
                    .Select(file => new OldCopyCareer(copy.Name, folder, file.FullName, file.Length)));
            }
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
