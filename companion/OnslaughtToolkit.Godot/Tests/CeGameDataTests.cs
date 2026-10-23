// SPDX-License-Identifier: GPL-3.0-only
using System.Security.Cryptography;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>CE data admission and launcher precedence using owned tiny files and fake candidate validation.</summary>
internal static class CeGameDataTests
{
    internal static void Run(string scratch, Checks check)
    {
        check.Suite("CE original-data resolution");
        string root = Path.Combine(scratch, "ce-game-data");
        string dataOnly = Path.Combine(root, "data-only");
        string scripts = Path.Combine(dataOnly, "DaTa", "mISSIONSCRIPTS");
        string text = Path.Combine(scripts, "TeXt");
        Directory.CreateDirectory(text);
        byte[] missionBytes = "owned mission-script fixture\n"u8.ToArray();
        byte[] textBytes = "owned game-text fixture\n"u8.ToArray();
        string missionPath = Path.Combine(scripts, "ONSLDEF.MSL"), textPath = Path.Combine(text, "TEXT.STF");
        File.WriteAllBytes(missionPath, missionBytes);
        File.WriteAllBytes(textPath, textBytes);
        string missionHash = Convert.ToHexString(SHA256.HashData(missionBytes));
        string textHash = Convert.ToHexString(SHA256.HashData(textBytes));
        bool FixtureSupported(string folder) => CeGameData.IsSupported(folder, missionHash, textHash);

        check.That(FixtureSupported(dataOnly) && !File.Exists(Path.Combine(dataOnly, "BEA.exe")),
            "CE accepts both matching data files with mixed-case components and without BEA.exe.");
        check.That(!CeGameData.IsSupported(dataOnly),
            "The public validator retains CE's production hash pins and rejects the tiny owned fixtures.");
        check.That(!CeGameData.IsSupported(dataOnly, new string('0', 64), textHash) &&
            !CeGameData.IsSupported(dataOnly, missionHash, new string('0', 64)),
            "Each of the two data hashes is required independently.");
        string missing = Path.Combine(root, "missing-text");
        Directory.CreateDirectory(Path.Combine(missing, "data", "MissionScripts"));
        File.WriteAllBytes(Path.Combine(missing, "data", "MissionScripts", "onsldef.msl"), missionBytes);
        check.That(!FixtureSupported(missing) && !FixtureSupported(Path.Combine(root, "absent")),
            "A missing second data file or absent folder cannot be admitted.");
        string markerOnly = Path.Combine(root, "selected-original-markers");
        Directory.CreateDirectory(Path.Combine(markerOnly, "data"));
        File.WriteAllText(Path.Combine(markerOnly, "BEA.exe"), "owned executable marker");
        check.That(GameFolder.LooksLikeGame(markerOnly) && !FixtureSupported(markerOnly),
            "The original companion's BEA.exe and data markers do not establish CE data support.");
        check.That(File.ReadAllBytes(missionPath).AsSpan().SequenceEqual(missionBytes) &&
            File.ReadAllBytes(textPath).AsSpan().SequenceEqual(textBytes), "Data admission leaves the inspected fixture bytes unchanged.");

        string steamRoot = Path.Combine(root, "steam"), library = Path.Combine(root, "library"), laterRoot = Path.Combine(root, "later-steam");
        string firstSteam = SteamGame(steamRoot), listedSteam = SteamGame(library), laterSteam = SteamGame(laterRoot);
        foreach (string folder in new[] { firstSteam, listedSteam, laterSteam }) Directory.CreateDirectory(folder);
        File.WriteAllText(Path.Combine(steamRoot, "steamapps", "libraryfolders.vdf"),
            "\"libraryfolders\" { \"1\" { \"path\" \"" + library.Replace("\\", "\\\\", StringComparison.Ordinal) + "\" } }");
        const string manifestFolder = "Different manifest folder";
        string manifestGame = Path.Combine(steamRoot, "steamapps", "common", manifestFolder);
        Directory.CreateDirectory(manifestGame);
        File.WriteAllText(Path.Combine(steamRoot, "steamapps", "appmanifest_1346400.acf"),
            "\"AppState\" { \"installdir\" \"" + manifestFolder + "\" }");
        string environment = Path.Combine(root, "environment"), ini = Path.Combine(root, "ini"), stale = Path.Combine(root, "stale");
        foreach (string folder in new[] { environment, ini, stale }) Directory.CreateDirectory(folder);
        List<string> inspected = [];
        HashSet<string> accepted = new(StringComparer.Ordinal) { environment, ini, firstSteam, listedSteam, laterSteam, manifestGame };
        bool Supported(string folder) { inspected.Add(folder); return accepted.Contains(folder); }

        check.That(CeGameData.Resolve([steamRoot, laterRoot], environment, ini, Supported) == environment &&
            inspected.SequenceEqual([environment]), "A supported environment folder wins before INI or Steam candidates are inspected.");
        inspected.Clear();
        check.That(CeGameData.Resolve([steamRoot, laterRoot], stale, ini, Supported) == ini && inspected.SequenceEqual([stale, ini]),
            "A stale environment choice falls through to a supported ce.ini folder.");
        inspected.Clear();
        check.That(CeGameData.Resolve([steamRoot, laterRoot], stale, markerOnly, Supported) == firstSteam &&
            inspected.SequenceEqual([stale, markerOnly, firstSteam]),
            "Unsupported environment and selected-original markers fall through to the Steam root's fixed game folder.");
        accepted.Remove(firstSteam); inspected.Clear();
        check.That(CeGameData.Resolve([steamRoot, laterRoot], null, null, Supported) == listedSteam &&
            inspected.SequenceEqual([firstSteam, listedSteam]),
            "A listed library follows its Steam root and precedes the next root; the appmanifest override is ignored.");
        accepted.Remove(listedSteam); inspected.Clear();
        check.That(CeGameData.Resolve([steamRoot, laterRoot], "relative-folder", "", Supported) == laterSteam &&
            inspected.SequenceEqual([firstSteam, listedSteam, laterSteam]),
            "Relative and empty explicit choices are skipped while Steam root ordering is retained.");
        accepted.Remove(laterSteam); inspected.Clear();
        check.That(CeGameData.Resolve([steamRoot, laterRoot], null, null, Supported) is null && !inspected.Contains(manifestGame),
            "A supported manifest-only folder is never substituted for CE's fixed Steam candidate.");
        check.That(CeGameData.Resolve([], markerOnly, dataOnly, FixtureSupported) == dataOnly,
            "Data-only validation participates in fallback after unsupported original-game markers.");
        if (OperatingSystem.IsLinux())
        {
            string link = Path.Combine(root, "data-link");
            Directory.CreateSymbolicLink(link, dataOnly);
            check.That(CeGameData.Resolve([], link, null, FixtureSupported) == dataOnly,
                "An explicit linked data folder resolves to its absolute canonical path before admission.");
        }
    }

    private static string SteamGame(string root) => Path.Combine(root, "steamapps", "common", SteamLibraries.DefaultInstallFolder);
}
