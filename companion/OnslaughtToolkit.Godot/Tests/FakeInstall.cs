// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// A game-shaped folder behind a Steam-shaped library, built from tiny original bytes and copies of
/// the one tracked career fixture. Nothing retail is copied: BEA.exe is a text marker.
/// </summary>
internal sealed record FakeInstall(string SteamRoot, string Library, string Game, string Career, string Options)
{
    internal const string ExecutableMarker = "Owned test marker; not an executable.";

    /// <summary>
    /// A half-second 440 Hz tone as Ogg Vorbis (22,050 Hz mono, 3,944 bytes, SHA-256 c4fdc0eb…36d8), our own bytes,
    /// standing in for a playable voice line. Regenerate it bit-exactly with FFmpeg 9.0.1 and libvorbis:
    /// <c>ffmpeg -f lavfi -i "sine=frequency=440:sample_rate=22050:duration=0.5"
    /// -af "volume=0.25,afade=t=in:d=0.02,afade=t=out:st=0.45:d=0.05" -ac 1 -c:a libvorbis -q:a 0
    /// -fflags +bitexact -flags:a +bitexact -map_metadata -1 tone.ogg</c>, then base64-encode it.
    /// </summary>
    internal static readonly byte[] ToneOgg = Convert.FromBase64String(
        "T2dnUwACAAAAAAAAAAAAAAAAAAAAANoLuMsBHgF2b3JiaXMAAAAAASJWAAAAAAAAwF0AAAAAAACqAU9nZ1MAAAAAAAAAAAAAAAAAAAEAAABxjw5u" +
        "DjD///////////////+aA3ZvcmJpcwYAAABmZm1wZWcBAAAAFgAAAGVuY29kZXI9TGF2YyBsaWJ2b3JiaXMBBXZvcmJpcyJCQ1YBAAgAAIAgChnG" +
        "gNCQVQAAEAAAQohGxlCnlASXgoUQR8RQh5DzUGrpIHhKYcmY9BRrEEII33vPvffeeyA0ZBUAAAQAQBgFDmLgMQlCCKEYxQlRnCkIQghhOQmWch46" +
        "CUL3IIQQLufecu699x4IDVkFAAACADAIIYQQQgghhBBCCimlFFKKKaaYYsoxxxxzzDHIIIMMOuikk04yqaSTjjLJqKPUWkotxRRTbLnFWGutNefc" +
        "a1DKGGOMMcYYY4wxxhhjjDHGCEJDVgEAIAAAhEEGGWQQQgghhRRSiimmHHPMMceA0JBVAAAgAIAAAAAAR5EUyZEcyZEkSbIkS9Ikz/Isz/IsTxM1" +
        "UVNFVXVV27V925d923d12bd92XZ1WZdlWXdtW5d1V9d1Xdd1Xdd1Xdd1Xdd1Xdd1IDRkFQAgAQCgIzmOIzmOIzmSIymSAoSGrAIAZAAABADgKI7i" +
        "OJIjOZZjSZakSZrlWZ7laZ4maqIHhIasAgAAAQAEAAAAAACgKIriKI4jSZalaZrnqZ4oiqaqqqJpqqqqmqZpmqZpmqZpmqZpmqZpmqZpmqZpmqZp" +
        "mqZpmqZpmqZpmkBoyCoAQAIAQMdxHMdRHMdxHMmRJAkIDVkFAMgAAAgAwFAUR5Ecy7EkzdIsz/I00TM9V5RN3dRVGwgNWQUAAAIACAAAAAAAwPEc" +
        "z/EcT/Ikz/Icz/EkT9I0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdOA0JBVAAACAAAgiEKGMSA0ZBUAAAQAgBCikTHU" +
        "KSXBpWAhxBEx1CHkPJRaOgieUlgyJj3FGoQQwvfec++99x4IDVkFAAABABBGgYMYeEyCEEIoRnFCFGcKghBCWE6CpZyHToLQPQghhMu5t5x7770H" +
        "QkNWAQCAAAAMQgghhBBCCCGEkEJKKYWUYooppphyzDHHHHMMMsgggw466aSTTCrppKNMMuootZZSSzHFFFtuMdZaa8059xqUMsYYY4wxxhhjjDHG" +
        "GGOMMYLQkFUAAAgAAGGQQQYZhBBCSCGFlGKKKcccc8wxIDRkFQAACAAgAAAAwFEkRXIkR3IkSZIsyZI0ybM8y7M8y9NETdRUUVVd1XZt3/Zl3/Zd" +
        "XfZtX7ZdXdZlWdZd29Zl3dV1Xdd1Xdd1Xdd1Xdd1Xdd1HQgNWQUASAAA6EiO40iO40iO5EiKpAChIasAABkAAAEAOIqjOI7kSI7lWJIlaZJmeZZn" +
        "eZqniZroAaEhqwAAQAAAAQAAAAAAKIqiOIrjSJJlaZrmeaoniqKpqqpomqqqqqZpmqZpmqZpmqZpmqZpmqZpmqZpmqZpmqZpmqZpmqZpmiYQGrIK" +
        "AJAAANBxHMdxFMdxHEdyJEkCQkNWAQAyAAACADAUxVEkx3IsSbM0y7M8TfRMzxVlUzd11QZCQ1YBAIAAAAIAAAAAAHA8x3M8x5M8ybM8x3M8yZM0" +
        "TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0TdM0IDRkJQAABACAIMe0gyQJhKCC5BnEHMSkGYWgguQ6BiXF5CGnoGLkOcmY" +
        "QeSC0kWmIggNWREARAEAAMYgxhBzyDknpZMUOeekdFIaCKGljlJnqbRaYswoldpSrQ2EjlJILaNUYi2tdtRKrSW2AgAAAhwAAAIshEJDVgQAUQAA" +
        "hDFIKaQUYow5yBxEjDHoGGSGMQYhc05BxxyFVCoHHXVQUsMYc45BqKCDVDpHlYNQUkedAACAAAcAgAALodCQFQFAnACAQZI0zdI0z7M0z/M8UVRV" +
        "TxRV1RI90/RMU1U901RVUzVlV1RNWbY80TQ901RVzzRVVTRV2TVN1XU9VbVl01V1WXRV3XZt2bddWRZuT1VlW1RdWzdVV9ZVWbZ9V7ZtXxJFVRVV" +
        "1XU9VXVd1XV123RdXfdUVXZN15Vl03Vt2XVlW1dlWfg1VZVl03Vt2XRd2XZlV7dVWdZt0XV9XZVl4Tdl2fdlW9d9WbeVYXRd21dlWfdNWRZ+2ZaF" +
        "3dV1X5hEUVU9VZVdUVVd13RdW1dd17Y11ZRd03Vt2VRdWVZlWfddV9Z1TVVl2ZRl2zZdV5ZVWfZ1V5Z1W3RdXTdlWfhVV9Z1V7eNY7ZtXxhdV/dN" +
        "WdZ9VZZ1X9Z1YZh129c1VdV9U3Z94XRlXdh93xhmXReOz3V9X5Vt4Vhl2fh14ReWW9eF33NdX1dt2RhW2TaG3feNYfZ941h12xhmWze6uk4YfmE4" +
        "bt84qrYtdHVbWF7dNurGT7iN36ipqq+brmv8piz7uqzbwnD7vnJ8ruv7qiwbvyrbwm/runLsvk/5XNcXVlkWhtWWhWHWdWHZhWGp2royvLpvHK+t" +
        "K8PtC43fV4aqbRvLq9vCMPu28NvCbxy7sTMGAAAMOAAABJhQBgoNWREAxAkAWCTJ8yzLEkXLskRRNEVVFUVRVS1NM01N80xT0zzTNE1TdUXTVF1L" +
        "00xT8zTT1DzNNE3VdFXTNGVTNE3XNVXTdkVVlWXVlWVZdV1dFk3TlUXVdGXTVF1ZdV1XVl1XliVNM03N80xT8zzTNFXTlU1TdV3L81RT80TT9URR" +
        "VVVTVV1TVWVX8zxT9URPNT1RVFXTNWXVVFVZNlXTlk1TlWXTVW3ZVWVXll3Ztk1VlWVTNV3ZdF3Xdl3Xdl3ZFXZJ00xT8zzT1DxPNU1TdV1TVV3Z" +
        "8jzV9ERRVTVPNFVVVV3XNFVXtjzPVD1RVFVN1FTTdF1ZVlVTVkXVtGVVVXXZNFVZdmXZtl3VdWVTVV3ZVF1ZNlVTdl1XtrmyKqueacqyqaq2bKqq" +
        "7Mq2beuu6+q2qJqya5qqbKuqqruya+u+LMu2LKqq65quKsumqsq2LMu6Lsu2sKuua9um6sq6K8t0WbVd3/Ztuuq6tq/Krq+7smzrru3qsm7bvu+Z" +
        "piybqinbpqrKsiy7tm3Lsi+Mpunapqvasqm6su26rq7LsmzbomnKsqm6rm2qpizLsmz7sizbturKuuzasu27rizbsm0Lu+wKs6+6sq27sm0Lq6va" +
        "tuzbPltXdVUAAMCAAwBAgAlloNCQlQBAFAAAYAxjjEFolHLOOQiNUs45ByFzDkIIqWTOQQihpMw5CKWklDkHoZSUQgilpNRaCKGUlForAACgwAEA" +
        "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");

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
        // The voice line plays; the music file is a deliberately broken stub that the refusal checks use.
        File.WriteAllBytes(Path.Combine(game, "data", "sounds", "english", "MessageBox", "211_briefing.ogg"), ToneOgg);
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
