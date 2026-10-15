// SPDX-License-Identifier: MIT
using System.Text.RegularExpressions;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>A folder that Steam's own records name as this game's installation.</summary>
public sealed record GameCandidate(string Root, string Library);

/// <summary>
/// Finds the game through Steam's own records: each Steam root's <c>steamapps/libraryfolders.vdf</c>
/// lists its libraries, and a library's <c>appmanifest_1346400.acf</c> names the install folder.
/// Paths are returned canonical (no symbolic links), because the protected file layer refuses
/// linked path components.
/// </summary>
public static partial class SteamLibraries
{
    public const string AppId = "1346400";
    public const string DefaultInstallFolder = "Battle Engine Aquila";

    /// <summary>Where Steam keeps its root on this machine: native, Flatpak and Snap on Linux; the registry on Windows.</summary>
    public static IReadOnlyList<string> DefaultRoots()
    {
        List<string> roots = [];
        if (OperatingSystem.IsWindows())
        {
            foreach (string? path in new[]
            {
                WindowsRegistry(@"HKEY_CURRENT_USER\Software\Valve\Steam", "SteamPath"),
                WindowsRegistry(@"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Valve\Steam", "InstallPath"),
                WindowsRegistry(@"HKEY_LOCAL_MACHINE\SOFTWARE\Valve\Steam", "InstallPath"),
            })
            {
                if (!string.IsNullOrWhiteSpace(path)) roots.Add(path.Replace('/', '\\'));
            }
            roots.Add(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), "Steam"));
        }
        else
        {
            string home = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile);
            roots.Add(Path.Combine(home, ".local", "share", "Steam"));
            roots.Add(Path.Combine(home, ".steam", "steam"));
            roots.Add(Path.Combine(home, ".steam", "root"));
            roots.Add(Path.Combine(home, ".var", "app", "com.valvesoftware.Steam", ".local", "share", "Steam"));
            roots.Add(Path.Combine(home, "snap", "steam", "common", ".local", "share", "Steam"));
        }
        return roots;
    }

    /// <summary>Every existing game folder named by the given Steam roots, de-duplicated by real path.</summary>
    public static IReadOnlyList<GameCandidate> FindGame(IEnumerable<string> roots)
    {
        List<GameCandidate> found = [];
        HashSet<string> seen = new(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        foreach (string library in Libraries(roots))
        {
            string steamapps = Path.Combine(library, "steamapps");
            string folder = DefaultInstallFolder;
            string manifest = Path.Combine(steamapps, $"appmanifest_{AppId}.acf");
            if (ReadText(manifest) is string text && Value(text, "installdir") is string installDir &&
                installDir.Length > 0 && installDir.IndexOfAny(Path.GetInvalidFileNameChars()) < 0)
                folder = installDir;
            string candidate = Path.Combine(steamapps, "common", folder);
            if (!Directory.Exists(candidate) || Canonical(candidate) is not string real || !seen.Add(real)) continue;
            found.Add(new GameCandidate(real, library));
        }
        return found;
    }

    /// <summary>The Steam roots themselves plus every library their libraryfolders.vdf lists.</summary>
    public static IReadOnlyList<string> Libraries(IEnumerable<string> roots)
    {
        List<string> libraries = [];
        HashSet<string> seen = new(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal);
        foreach (string root in roots)
        {
            if (!Directory.Exists(root) || Canonical(root) is not string real) continue;
            if (seen.Add(real)) libraries.Add(real);
            if (ReadText(Path.Combine(real, "steamapps", "libraryfolders.vdf")) is not string vdf) continue;
            foreach (string path in ParseLibraryFolders(vdf))
            {
                if (Directory.Exists(path) && Canonical(path) is string library && seen.Add(library)) libraries.Add(library);
            }
        }
        return libraries;
    }

    /// <summary>The <c>"path"</c> values of a libraryfolders.vdf document, with KeyValues escapes undone.</summary>
    public static IReadOnlyList<string> ParseLibraryFolders(string vdf) =>
        PathPattern().Matches(vdf).Select(match => Unescape(match.Groups[1].Value)).Where(path => path.Length > 0).ToArray();

    /// <summary>
    /// The path with every symbolic link resolved, or null if it cannot be resolved. The protected
    /// file layer opens each component without following links, so linked roots must be resolved first.
    /// </summary>
    public static string? Canonical(string path) => Canonical(path, 0);

    private static string? Canonical(string path, int depth)
    {
        if (depth > 40) return null;
        try
        {
            string full = Path.GetFullPath(path);
            string? root = Path.GetPathRoot(full);
            if (string.IsNullOrEmpty(root)) return null;
            string current = root;
            foreach (string part in full[root.Length..].Split(Path.DirectorySeparatorChar, StringSplitOptions.RemoveEmptyEntries))
            {
                current = Path.Combine(current, part);
                // LinkTarget reads the link itself (lstat/readlink), whether it points at a file or a folder.
                if (new FileInfo(current).LinkTarget is not string target) continue;
                string resolved = Path.IsPathRooted(target) ? target : Path.Combine(Path.GetDirectoryName(current)!, target);
                if (Canonical(resolved, depth + 1) is not string real) return null;
                current = real;
            }
            return current;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException)
        {
            return null;
        }
    }

    private static string? Value(string document, string key)
    {
        Match match = Regex.Match(document, "\"" + Regex.Escape(key) + "\"\\s+\"((?:[^\"\\\\]|\\\\.)*)\"", RegexOptions.IgnoreCase);
        return match.Success ? Unescape(match.Groups[1].Value) : null;
    }

    private static string Unescape(string value) => value.Replace("\\\\", "\\").Replace("\\\"", "\"");

    private static string? ReadText(string path)
    {
        try
        {
            FileInfo info = new(path);
            // Steam's records are small; anything large is not one of them.
            return info.Exists && info.Length < 1_000_000 ? File.ReadAllText(path) : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    private static string? WindowsRegistry(string key, string name)
    {
        if (!OperatingSystem.IsWindows()) return null;
        try
        {
            return Microsoft.Win32.Registry.GetValue(key, name, null) as string;
        }
        catch (Exception error) when (error is System.Security.SecurityException or IOException or UnauthorizedAccessException)
        {
            return null;
        }
    }

    [GeneratedRegex("\"path\"\\s+\"((?:[^\"\\\\]|\\\\.)*)\"", RegexOptions.IgnoreCase)]
    private static partial Regex PathPattern();
}
