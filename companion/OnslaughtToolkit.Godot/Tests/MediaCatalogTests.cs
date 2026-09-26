// SPDX-License-Identifier: MIT
using OnslaughtToolkit.Companion.Media;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Media inventory contracts on an invocation-owned folder. Fixtures are tiny original
/// byte headers, never retail assets or valid game-save replacements.
/// </summary>
internal static class MediaCatalogTests
{
    private static readonly Dictionary<string, string> Headers = new()
    {
        ["music.OGG"] = "4f67675300020000", ["sound.wav"] = "524946460000000057415645",
        ["voice.mp3"] = "494433040000", ["movie.bik"] = "42494b69",
        ["cutscene.vid"] = "56494400", ["image.png"] = "89504e470d0a1a0a",
        ["photo.jpg"] = "ffd8ffe0", ["empty.bmp"] = "", ["nested/frame.tga"] = "000002",
        ["not-media.bin"] = "00010203",
    };

    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("media catalog");
        string fixture = Path.Combine(outputDirectory, "media-catalog-fixtures");
        if (Path.Exists(fixture))
        {
            check.Fail("Media catalog tests require a fresh invocation-owned output directory.");
            return;
        }
        Directory.CreateDirectory(Path.Combine(fixture, "nested"));
        Directory.CreateDirectory(Path.Combine(fixture, "empty"));
        MediaScan empty = Scan(Path.Combine(fixture, "empty"));
        check.That(empty.Ok && empty.Complete && empty.Items.Count == 0, "Empty folder returns an honest empty list.");
        MediaScan missing = Scan(Path.Combine(fixture, "missing"));
        check.That(!missing.Ok && !missing.Complete && missing.Items.Count == 0, "Missing folder is refused, not reported as empty.");
        foreach ((string name, string hex) in Headers)
            File.WriteAllBytes(Path.Combine(fixture, name), Convert.FromHexString(hex));

        MediaScan full = Scan(fixture);
        check.That(full.Ok && full.Complete && full.Items.Count == 9, "Known media extensions are inventoried; unrelated files are omitted.");
        Dictionary<string, MediaItem> byPath = full.Items.ToDictionary(item => item.RelativePath);
        foreach (MediaItem item in full.Items)
        {
            check.That(item.Support == "Metadata only" && Headers.TryGetValue(item.RelativePath, out string? hex) &&
                item.Size == hex.Length / 2, "Reported sizes and metadata-only support are accurate.");
        }
        check.That(byPath.ContainsKey("nested/frame.tga") && byPath.ContainsKey("music.OGG"),
            "Nested relative paths and uppercase extensions are supported.");
        check.That(byPath.TryGetValue("empty.bmp", out MediaItem? bitmap) && bitmap.Size == 0,
            "A zero-length file is not mistaken for a size read failure.");
        check.That(byPath.TryGetValue("movie.bik", out MediaItem? movie) && movie.Format == "Bink" &&
            byPath.TryGetValue("cutscene.vid", out MediaItem? cutscene) && cutscene.Format == "VID",
            "Container names remain separate from playback claims.");

        MediaScan shallow = Scan(fixture, depth: 0);
        check.That(!shallow.Complete && shallow.DepthSkips >= 1 && shallow.Items.Count == 8,
            "Depth cap marks the list incomplete and skips nested media.");
        MediaScan capped = Scan(fixture, items: 1);
        check.That(!capped.Complete && capped.Items.Count == 1, "Media item cap is enforced and reported.");
        MediaScan entryCapped = Scan(fixture, entries: 1);
        check.That(!entryCapped.Complete && entryCapped.Entries == 1, "Nonmedia and folder traversal is also bounded by an entry limit.");
        MediaCatalog cancelled = new();
        cancelled.Begin(fixture);
        cancelled.Step(1);
        cancelled.Cancel();
        MediaScan cancelledResult = cancelled.Result();
        check.That(cancelledResult.Done && cancelledResult.Cancelled && !cancelledResult.Complete,
            "Cancellation finishes with an explicitly incomplete result.");
        check.That(new MediaCatalog().Begin(fixture, maxDepth: 9) is { Ok: false },
            "Scan limits outside the supported bounds are refused.");
        check.That(new MediaCatalog().Begin("relative/folder") is { Ok: false } && new MediaCatalog().Begin("") is { Ok: false },
            "Relative and empty folder paths are refused.");

        if (OperatingSystem.IsLinux())
        {
            File.CreateSymbolicLink(Path.Combine(fixture, "linked.ogg"), Path.Combine(fixture, "music.OGG"));
            Directory.CreateSymbolicLink(Path.Combine(fixture, "linked-folder"), Path.Combine(fixture, "nested"));
            MediaScan linked = Scan(fixture);
            check.That(linked.SkippedLinks == 2 && linked.Items.Count == 9, "Linked files and folders are skipped without duplicate entries.");
            MediaScan rootLink = Scan(Path.Combine(fixture, "linked-folder"));
            check.That(!rootLink.Ok && rootLink.Items.Count == 0, "Selecting a linked root is refused.");
        }
        foreach ((string name, string hex) in Headers)
        {
            check.That(File.ReadAllBytes(Path.Combine(fixture, name)).AsSpan().SequenceEqual(Convert.FromHexString(hex)),
                "Scanning left owned fixture bytes unchanged: " + name);
        }
    }

    /// <summary>The game-audio catalog's grouping and its header check, on tiny original byte files.</summary>
    internal static void RunGameAudio(string outputDirectory, byte[] career, Checks check)
    {
        check.Suite("game audio");
        FakeInstall install = FakeInstall.Create(Path.Combine(outputDirectory, "game-audio"), career);
        IReadOnlyList<Media.GameAudioItem> items = Media.GameAudio.Catalog(Game.GameFolder.Inspect(install.Game, "test"), null);
        check.That(items.Count == 3 && items.Count(item => item.Kind == Media.AudioKind.Music) == 1 &&
            items.Single(item => item.Kind == Media.AudioKind.Voice).Group == "Level 2.11" &&
            items.Single(item => item.Kind == Media.AudioKind.Cutscene) is { Playable: false },
            "Music, voice lines by level and unplayable cutscenes are listed from the install.");
        check.That(Media.GameAudio.VoiceGroup("tutorial_01", null).Group == "Tutorial" && Media.GameAudio.VoiceGroup("health_low", null).Group ==
            "Status messages" && Media.GameAudio.VoiceGroup("wingman_03", null).Group == "Wingman", "Voice lines group by their kind.");
        string header = Path.Combine(outputDirectory, "game-audio", "header.ogg");
        File.WriteAllBytes(header, Convert.FromHexString("4f676753" + "0002" + new string('0', 16) + new string('0', 24) + "01" + "1e" +
            "01" + Convert.ToHexString("vorbis"u8.ToArray()) + new string('0', 40)));
        check.That(Media.GameAudio.LooksLikeOggVorbis(header) && !Media.GameAudio.LooksLikeOggVorbis(install.Career) &&
            !Media.GameAudio.LooksLikeOggVorbis(Path.Combine(install.Game, "data", "Music", "theme.ogg")),
            "Only a file with an Ogg page carrying a Vorbis identification header reaches the decoder.");
    }

    private static MediaScan Scan(string root, int depth = 8, int items = 5000, int entries = 30000)
    {
        MediaCatalog scanner = new();
        scanner.Begin(root, depth, items, entries);
        for (int batches = 0; !scanner.Done && batches < 10000; batches++)
            scanner.Step(4);
        if (!scanner.Done) scanner.Cancel();
        return scanner.Result();
    }
}
