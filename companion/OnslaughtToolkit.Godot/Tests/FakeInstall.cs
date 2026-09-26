// SPDX-License-Identifier: MIT
namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// A game-shaped folder behind a Steam-shaped library, built from tiny original bytes and copies of
/// the one tracked career fixture. Nothing retail is copied: BEA.exe is a text marker.
/// </summary>
internal sealed record FakeInstall(string SteamRoot, string Library, string Game, string Career, string Options)
{
    internal const string ExecutableMarker = "Owned test marker; not an executable.";

    internal static FakeInstall Create(string parent, byte[] career)
    {
        string steam = Path.Combine(parent, "steam");
        string library = Path.Combine(parent, "library");
        string game = Path.Combine(library, "steamapps", "common", "Battle Engine Aquila");
        Directory.CreateDirectory(Path.Combine(steam, "steamapps"));
        Directory.CreateDirectory(Path.Combine(game, "savegames"));
        Directory.CreateDirectory(Path.Combine(game, "data", "language"));
        Directory.CreateDirectory(Path.Combine(game, "data", "Music"));
        File.WriteAllText(Path.Combine(steam, "steamapps", "libraryfolders.vdf"),
            "\"libraryfolders\"\n{\n\t\"0\"\n\t{\n\t\t\"path\"\t\t\"" + steam.Replace("\\", "\\\\") + "\"\n\t}\n" +
            "\t\"1\"\n\t{\n\t\t\"path\"\t\t\"" + library.Replace("\\", "\\\\") + "\"\n\t\t\"apps\"\n\t\t{\n\t\t\t\"1346400\"\t\t\"1\"\n\t\t}\n\t}\n}\n");
        File.WriteAllText(Path.Combine(library, "steamapps", "appmanifest_1346400.acf"),
            "\"AppState\"\n{\n\t\"appid\"\t\t\"1346400\"\n\t\"installdir\"\t\t\"Battle Engine Aquila\"\n}\n");
        File.WriteAllText(Path.Combine(game, "BEA.exe"), ExecutableMarker);
        File.WriteAllBytes(Path.Combine(game, "data", "language", "english.dat"), [0x4E, 0x6F, 0x74, 0x20, 0x61]);
        File.WriteAllBytes(Path.Combine(game, "data", "Music", "theme.ogg"), Convert.FromHexString("4f67675300020000"));
        Directory.CreateDirectory(Path.Combine(game, "data", "sounds", "english", "MessageBox"));
        Directory.CreateDirectory(Path.Combine(game, "data", "video", "cutscenes"));
        File.WriteAllBytes(Path.Combine(game, "data", "sounds", "english", "MessageBox", "211_briefing.ogg"), Convert.FromHexString("4f676753"));
        File.WriteAllBytes(Path.Combine(game, "data", "video", "cutscenes", "01.vid"), Convert.FromHexString("56494400"));
        // Tiny pictures made here, standing in for the manual's art, and a one-line manual page.
        Directory.CreateDirectory(Path.Combine(game, "Manuals", "Images"));
        Directory.CreateDirectory(Path.Combine(game, "Manuals", "English"));
        Godot.Image picture = Godot.Image.CreateEmpty(8, 6, false, Godot.Image.Format.Rgb8);
        picture.Fill(new Godot.Color(0.2f, 0.3f, 0.4f));
        File.WriteAllBytes(Path.Combine(game, "Manuals", "Images", "image003.png"), picture.SavePngToBuffer());
        File.WriteAllBytes(Path.Combine(game, "Manuals", "Images", "gamemap.jpg"), picture.SaveJpgToBuffer());
        File.WriteAllText(Path.Combine(game, "Manuals", "English", "English.htm"), "<html><body>Test manual</body></html>");
        string careerPath = Path.Combine(game, "savegames", "Career One.bes");
        File.WriteAllBytes(careerPath, career);
        string options = Path.Combine(game, "defaultoptions.bea");
        File.WriteAllBytes(options, career);
        return new FakeInstall(steam, library, game, careerPath, options);
    }
}
