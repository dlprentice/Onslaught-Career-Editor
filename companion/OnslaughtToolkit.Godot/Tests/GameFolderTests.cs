// SPDX-License-Identifier: MIT
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Game-folder detection through Steam's records, read-only inspection and remembered settings.</summary>
internal static class GameFolderTests
{
    internal static async Task RunAsync(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("game folder");
        string vdf = "\"libraryfolders\"\n{\n\t\"0\"\n\t{\n\t\t\"path\"\t\t\"/home/player/.local/share/Steam\"\n\t\t\"label\"\t\t\"\"\n\t}\n" +
            "\t\"1\"\n\t{\n\t\t\"path\"\t\t\"D:\\\\Steam \\\"Games\\\"\"\n\t}\n}\n";
        IReadOnlyList<string> parsed = SteamLibraries.ParseLibraryFolders(vdf);
        check.That(parsed.SequenceEqual(["/home/player/.local/share/Steam", "D:\\Steam \"Games\""]),
            "Library paths are read from libraryfolders.vdf with escapes undone.");

        string root = Path.Combine(outputDirectory, "game-folder");
        FakeInstall install = FakeInstall.Create(root, original);
        File.WriteAllBytes(Path.Combine(install.Game, "savegames", "short.bes"), original[..^1]);
        byte[] wrong = original.ToArray();
        wrong[0] ^= 1;
        File.WriteAllBytes(Path.Combine(install.Game, "savegames", "wrong.bes"), wrong);

        IReadOnlyList<GameCandidate> found = SteamLibraries.FindGame([install.SteamRoot]);
        check.That(found.Count == 1 && found[0].Root == install.Game, "The game is found through a second library that Steam lists.");
        check.That(GameFolder.LooksLikeGame(install.Game) && !GameFolder.LooksLikeGame(root) && !GameFolder.LooksLikeGame(null),
            "A game folder needs BEA.exe and data.");

        GameFolder folder = GameFolder.Inspect(install.Game, "test");
        check.That(folder.Executable.State == ExecutableState.Different && folder.Executable.Size == FakeInstall.ExecutableMarker.Length,
            "A BEA.exe that is not the Steam release is reported as different, never as an original.");
        check.That(folder.Careers.Count == 3 && folder.Careers.Count(career => career.Supported) == 1 &&
            folder.Careers.Single(career => career.Supported).Path == install.Career,
            "Careers are listed with the unsupported ones marked, not hidden.");
        check.That(folder.Careers.Single(career => career.Name == "short.bes").Problem?.Contains("10,003") == true &&
            folder.Careers.Single(career => career.Name == "wrong.bes").Problem is not null,
            "Wrong-length and wrong-version careers say why they cannot be opened.");
        check.That(folder.Options is { Supported: true } && folder.Languages.SequenceEqual(["english"]) && folder.MusicTracks == 1,
            "The options file, language files and music are found.");
        check.That(File.ReadAllBytes(install.Career).AsSpan().SequenceEqual(original) && File.ReadAllText(Path.Combine(install.Game, "BEA.exe")) ==
            FakeInstall.ExecutableMarker, "Inspection changes nothing.");

        check.That(ExecutableIdentity.Classify(ExecutableIdentity.RetailSize, ExecutableIdentity.RetailSha256.ToUpperInvariant()).State ==
            ExecutableState.Retail, "The Steam release's size and SHA-256 classify as retail.");
        check.That(ExecutableIdentity.Classify(ExecutableIdentity.RetailSize, new string('0', 64)).State == ExecutableState.Different &&
            ExecutableIdentity.Classify(ExecutableIdentity.RetailSize + 1, ExecutableIdentity.RetailSha256).State == ExecutableState.Different,
            "Any other size or hash is different.");
        check.That(ExecutableIdentity.Measure(Path.Combine(root, "absent.exe")).State == ExecutableState.Missing, "A missing executable is missing.");

        if (OperatingSystem.IsLinux())
        {
            string linkedRoot = Path.Combine(root, "steam-link");
            Directory.CreateSymbolicLink(linkedRoot, "steam");
            IReadOnlyList<GameCandidate> viaLink = SteamLibraries.FindGame([linkedRoot, install.SteamRoot]);
            check.That(viaLink.Count == 1 && viaLink[0].Root == install.Game && SteamLibraries.Canonical(linkedRoot) == install.SteamRoot,
                "A linked Steam root resolves to its real path and is not found twice.");
            File.CreateSymbolicLink(Path.Combine(install.Game, "savegames", "linked.bes"), install.Career);
            check.That(GameFolder.Inspect(install.Game, "test").Careers.Single(career => career.Name == "linked.bes").Problem?.StartsWith("Linked") == true,
                "A linked career is listed as linked, not opened through the link.");
        }

        SettingsStore store = new(Path.Combine(root, "settings", "settings.json"));
        check.That(store.Load().GameFolder is null, "Missing settings are defaults.");
        check.That(store.Save(new CompanionSettings { GameFolder = "/a", BackupFolder = "/b" }) &&
            store.Load() is { GameFolder: "/a", BackupFolder: "/b" }, "Settings round-trip.");
        File.WriteAllText(store.FilePath, "{ not json");
        check.That(store.Load().GameFolder is null, "Unreadable settings fall back to defaults.");

        GameLibrary library = new([install.SteamRoot], new SettingsStore(Path.Combine(root, "settings", "library.json")));
        GameFolder? detected = await library.DetectAsync();
        check.That(detected?.Root == install.Game && detected.Source.Contains("Steam") && !library.Busy, "Detection finds the game through Steam.");
        var refused = await library.ChooseAsync(root);
        check.That(!refused.Ok && library.Folder?.Root == install.Game, "A folder without the game is refused and the current folder kept.");
        var chosen = await library.ChooseAsync(install.Game);
        check.That(chosen.Ok && library.Settings.Load().GameFolder == install.Game, "A chosen game folder is remembered.");
        GameLibrary later = new([], library.Settings);
        check.That((await later.DetectAsync())?.Source == "Chosen by you", "A remembered folder is used without Steam.");
    }
}
