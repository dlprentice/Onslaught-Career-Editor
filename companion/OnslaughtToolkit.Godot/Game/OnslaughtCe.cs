// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// What the companion knows about Onslaught CE, the native port, read as a documented contract from the port's own
/// source (bea-decomp <c>port/platform/linux/paths.cpp</c>, <c>port/platform/windows/files.cpp</c> and
/// <c>port/tools/package.py</c>): where CE keeps its own careers and settings, and which programs a CE package holds.
/// The process rule was seen finding a running Onslaught CE 0.1 on Linux on 2026-10-22 (its <c>bea</c> started from the
/// package folder, before and after its file was replaced while it ran; the check's output is kept in the ignored
/// <c>local-data/companion/evidence/ce-running-check-2026-10-22.log</c>); it has not been tried on Windows. The
/// companion does not read or write CE's folder yet; it only refuses to
/// save copies there and counts CE as the game while it runs, because CE reads the original install's careers too.
/// </summary>
public static class OnslaughtCe
{
    /// <summary>The program a Linux package starts the game through (its <c>onslaught-ce</c> script runs it).</summary>
    public const string LinuxLauncher = "onslaught-ce-launch";

    /// <summary>The Windows package's launcher.</summary>
    public const string WindowsLauncher = "onslaught-ce.exe";

    /// <summary>The game program beside the launcher: <c>bea</c> on Linux, <c>bea.exe</c> on Windows.</summary>
    public const string LinuxGame = "bea", WindowsGame = "bea.exe";

    /// <summary>
    /// Said beside the promise not to write while CE runs, where that check has not been tried against a running CE
    /// (Windows); empty on Linux, where it has.
    /// </summary>
    public static string UntestedCheckNote => OperatingSystem.IsWindows()
        ? " Spotting Onslaught CE has not been tested on Windows yet, so close CE yourself before saving into the game." : "";

    /// <summary>The CE user folders for this process's environment.</summary>
    public static IReadOnlyList<string> UserFolders() =>
        UserFolders(Environment.GetEnvironmentVariable, OperatingSystem.IsWindows(),
            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile));

    /// <summary>
    /// Every folder Onslaught CE may use as its own careers-and-settings folder. CE takes <c>BEA_USER_DIR</c> when it is
    /// set, else <c>$XDG_DATA_HOME/onslaught-ce</c>, else <c>~/.local/share/onslaught-ce</c> on Linux, and
    /// <c>%APPDATA%\Onslaught CE</c> on Windows. CE may run with a different environment from the companion, so every
    /// candidate is listed, not only the one CE would pick here. A <c>BEA_USER_DIR</c> that is not a full path, or is a
    /// drive root or the home folder itself (or above it), is ignored rather than refusing everything under it.
    /// </summary>
    public static IReadOnlyList<string> UserFolders(Func<string, string?> environment, bool windows, string home)
    {
        List<string> folders = [];
        if (environment("BEA_USER_DIR") is { Length: > 0 } custom && Path.IsPathFullyQualified(custom) && !IsRootOrHome(custom, home))
            folders.Add(Path.TrimEndingDirectorySeparator(Path.GetFullPath(custom)));
        if (windows)
        {
            if (environment("APPDATA") is { Length: > 0 } appData && Path.IsPathFullyQualified(appData))
                folders.Add(Path.Combine(appData, "Onslaught CE"));
        }
        else
        {
            if (environment("XDG_DATA_HOME") is { Length: > 0 } data && Path.IsPathFullyQualified(data))
                folders.Add(Path.Combine(data, "onslaught-ce"));
            if (home.Length > 0) folders.Add(Path.Combine(home, ".local", "share", "onslaught-ce"));
        }
        return folders.Distinct(OperatingSystem.IsWindows() ? StringComparer.OrdinalIgnoreCase : StringComparer.Ordinal).ToArray();
    }

    /// <summary>
    /// Whether a running program is Onslaught CE. It is when the program is CE's launcher, or is named <c>bea</c>
    /// (<c>bea.exe</c>) and its folder also holds that launcher, as a CE package lays them out. A program called
    /// <c>bea</c> anywhere else is not counted. <paramref name="program"/> is the program's full path
    /// (<c>/proc/PID/exe</c>, or argv[0] when that is a full path); <paramref name="comm"/> is the kernel's 15-character
    /// process name, which shortens the launcher's to <c>onslaught-ce-la</c> (<c>onslaught-ce</c> is the package's start script
    /// for the moment before it hands over to the launcher).
    /// </summary>
    public static bool IsCeProgram(string comm, string? program, Func<string, bool> fileExists)
    {
        string name = comm.Trim();
        if (name is LinuxLauncher or "onslaught-ce-la" or "onslaught-ce") return true;
        if (string.IsNullOrEmpty(program)) return false;
        string file = FileName(program);
        if (file == LinuxLauncher || file.Equals(WindowsLauncher, StringComparison.OrdinalIgnoreCase)) return true;
        if (file != LinuxGame && !file.Equals(WindowsGame, StringComparison.OrdinalIgnoreCase)) return false;
        int slash = program.LastIndexOfAny(['/', '\\']);
        if (slash <= 0) return false;
        string folder = program[..slash];
        return fileExists(Path.Combine(folder, LinuxLauncher)) || fileExists(Path.Combine(folder, WindowsLauncher));
    }

    private static bool IsRootOrHome(string path, string home)
    {
        string full = Path.TrimEndingDirectorySeparator(Path.GetFullPath(path));
        if (string.Equals(full, Path.TrimEndingDirectorySeparator(Path.GetPathRoot(full) ?? ""), StringComparison.OrdinalIgnoreCase)) return true;
        if (home.Length == 0) return false;
        string homeFull = Path.TrimEndingDirectorySeparator(Path.GetFullPath(home));
        StringComparison comparison = OperatingSystem.IsWindows() ? StringComparison.OrdinalIgnoreCase : StringComparison.Ordinal;
        return string.Equals(full, homeFull, comparison) || homeFull.StartsWith(full + Path.DirectorySeparatorChar, comparison);
    }

    private static string FileName(string path) => path[(path.LastIndexOfAny(['/', '\\']) + 1)..];
}
