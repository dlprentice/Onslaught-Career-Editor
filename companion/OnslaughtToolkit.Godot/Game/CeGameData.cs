// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;

namespace OnslaughtToolkit.Companion.Game;

/// <summary>
/// CE's read-only original-data admission and automatic folder order. Contract: Onslaught CE commit
/// 72a44140c6db3e093cc07b1bed40a0584fdfecd2, port/updater/ce_launch.c:538-601, 605-630, 714-731.
/// The launcher checks two data hashes; it does not require the original executable or use Steam app manifests.
/// </summary>
public static class CeGameData
{
    private const string MissionScriptSha256 = "a1c9b9383ea7f9255de207a86c0e6c1885465309d50334344fd82696a1cf36c6";
    private const string TextSha256 = "fd318d6c2304eb8ffcfa718357c1715aadad69915f39851b19f442d8263b56ae";

    /// <summary>Whether both hash-pinned original data files match, resolving their components without regard to case.</summary>
    public static bool IsSupported(string root) => IsSupported(root, MissionScriptSha256, TextSha256);

    /// <summary>Data-only installs have no BEA.exe marker; protect the admitted original root explicitly.</summary>
    internal static void RejectWriteFolder(string folder, string? originalRoot, string label)
    {
        if (!string.IsNullOrWhiteSpace(originalRoot))
            CeInstallation.RejectFolderInTree(folder, originalRoot, label, " must be outside CE's original game data folder.");
    }

    // The test seam changes expected hashes per call; production's public admission always uses the CE pins above.
    internal static bool IsSupported(string root, string missionScriptSha256, string textSha256)
    {
        if (Candidate(root) is not string real) return false;
        try
        {
            return Matches(real, ["data", "MissionScripts", "onsldef.msl"], missionScriptSha256) &&
                Matches(real, ["data", "MissionScripts", "text", "text.stf"], textSha256);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or ArgumentException)
        {
            return false;
        }
    }

    /// <summary>
    /// The first supported absolute, canonical folder: BEA_GAME_DIR, ce.ini's gamedir, then each Steam library's
    /// fixed Battle Engine Aquila folder. Unsupported choices fall through; this does not choose or persist a folder.
    /// </summary>
    public static string? Resolve(IEnumerable<string> steamRoots, string? environmentFolder, string? iniFolder,
        Func<string, bool>? supported = null)
    {
        supported ??= IsSupported;
        string? Accepted(string? path) => Candidate(path) is string real && supported(real) ? real : null;
        if (Accepted(environmentFolder) is string environment) return environment;
        if (Accepted(iniFolder) is string ini) return ini;
        foreach (string library in SteamLibraries.Libraries(steamRoots))
            if (Accepted(Path.Combine(library, "steamapps", "common", SteamLibraries.DefaultInstallFolder)) is string steam)
                return steam;
        return null;
    }

    private static string? Candidate(string? path)
    {
        if (string.IsNullOrWhiteSpace(path) || !Path.IsPathFullyQualified(path)) return null;
        return SteamLibraries.Canonical(path) is string real && Directory.Exists(real) ? real : null;
    }

    private static bool Matches(string root, string[] components, string expected)
    {
        string current = root;
        foreach (string component in components)
        {
            if (Directory.EnumerateFileSystemEntries(current).FirstOrDefault(entry =>
                Path.GetFileName(entry).Equals(component, StringComparison.OrdinalIgnoreCase)) is not string next) return false;
            current = next;
        }
        if (!File.Exists(current)) return false;
        using FileStream stream = new(current, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete);
        return Convert.ToHexString(SHA256.HashData(stream)).Equals(expected, StringComparison.OrdinalIgnoreCase);
    }
}
