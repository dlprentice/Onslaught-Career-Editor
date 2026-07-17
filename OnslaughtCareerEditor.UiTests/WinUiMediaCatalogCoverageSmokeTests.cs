using System;
using System.IO;
using System.Linq;
using System.Text.Json;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiMediaCatalogCoverageSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Reads the local Battle Engine Aquila install and records public-safe media catalog coverage counts.")]
    public void MediaCatalog_CoversRetailAudioAndVideoFamiliesFromReadOnlyInstall()
    {
        string? gameDirectory = ResolveReadOnlyGameDirectory();
        if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
        {
            Assert.Ignore("No read-only Battle Engine Aquila install was available for media catalog coverage smoke.");
        }

        MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);

        Assert.That(snapshot.AudioItems.Count, Is.GreaterThanOrEqualTo(100), "Expected broad audio coverage from the retail install.");
        Assert.That(snapshot.VideoItems.Count, Is.GreaterThanOrEqualTo(30), "Expected broad video coverage from the retail install.");

        Assert.That(snapshot.AudioItems.Count(item => item.GroupName == "Music"), Is.GreaterThanOrEqualTo(5));
        Assert.That(snapshot.AudioItems.Any(item => item.GroupName == "Tutorial"), Is.True);
        Assert.That(snapshot.AudioItems.Any(item => item.GroupName == "Status Messages"), Is.True);
        Assert.That(snapshot.AudioItems.Any(item => item.GroupName.StartsWith("Mission ", StringComparison.OrdinalIgnoreCase)), Is.True);

        Assert.That(snapshot.VideoItems.Count(item => item.SectionName == "Main Videos"), Is.GreaterThanOrEqualTo(3));
        Assert.That(snapshot.VideoItems.Count(item => item.SectionName == "Cutscenes"), Is.GreaterThanOrEqualTo(20));
        Assert.That(snapshot.VideoItems.Any(item => item.SectionName.StartsWith("Mission Briefings / Episode ", StringComparison.OrdinalIgnoreCase)), Is.True);

        foreach (MediaAudioItem item in snapshot.AudioItems.Take(25))
        {
            Assert.That(File.Exists(item.FilePath), Is.True, $"Audio row should point at an existing file: {item.Name}");
        }

        foreach (MediaVideoItem item in snapshot.VideoItems.Take(25))
        {
            Assert.That(File.Exists(item.FilePath), Is.True, $"Video row should point at an existing file: {item.Name}");
            Assert.That(item.SizeText, Is.Not.Empty, $"Video row should expose a human file size: {item.Name}");
        }

        Assert.That(
            snapshot.AudioItems.Where(item => item.GroupName == "Music").Take(5).All(item => !string.IsNullOrWhiteSpace(item.DurationLabel)),
            Is.True,
            "Music rows should expose parsed OGG duration labels.");

        WriteCoverageSummary(snapshot);
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Reads every cataloged local media file and records public-safe decode/header coverage counts.")]
    public void MediaCatalog_VerifiesRetailAudioDurationsAndVideoHeadersFromReadOnlyInstall()
    {
        string? gameDirectory = ResolveReadOnlyGameDirectory();
        if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
        {
            Assert.Ignore("No read-only Battle Engine Aquila install was available for media decodability smoke.");
        }

        MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);
        Assert.That(snapshot.AudioItems.Count, Is.GreaterThanOrEqualTo(100), "Expected broad audio coverage from the retail install.");
        Assert.That(snapshot.VideoItems.Count, Is.GreaterThanOrEqualTo(30), "Expected broad video coverage from the retail install.");

        MediaAudioItem[] missingDurations = snapshot.AudioItems
            .Where(static item => string.IsNullOrWhiteSpace(item.DurationLabel) || !File.Exists(item.FilePath))
            .ToArray();
        MediaVideoItem[] badVideoHeaders = snapshot.VideoItems
            .Where(static item => !HasBinkHeader(item.FilePath))
            .ToArray();

        Assert.That(
            missingDurations,
            Is.Empty,
            "Every cataloged audio row should resolve to an existing OGG file with a parsed duration label.");
        Assert.That(
            badVideoHeaders,
            Is.Empty,
            "Every cataloged video row should resolve to an existing Bink file with a readable header.");

        WriteDecodabilitySummary(snapshot);
    }

    private static void WriteCoverageSummary(MediaCatalogSnapshot snapshot)
    {
        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-media-catalog-coverage");
        Directory.CreateDirectory(evidenceDir);

        object summary = new
        {
            schema = "winui-media-catalog-coverage.v1",
            date = "2026-05-06",
            audioCount = snapshot.AudioItems.Count,
            audioGroups = snapshot.AudioItems
                .GroupBy(static item => item.GroupName)
                .OrderByDescending(static group => group.Count())
                .ThenBy(static group => group.Key, StringComparer.OrdinalIgnoreCase)
                .Select(static group => new
                {
                    group = group.Key,
                    count = group.Count(),
                    sampleFiles = group.Take(3).Select(static item => Path.GetFileName(item.FilePath)).ToArray()
                })
                .ToArray(),
            videoCount = snapshot.VideoItems.Count,
            videoSections = snapshot.VideoItems
                .GroupBy(static item => item.SectionName)
                .OrderBy(static group => group.Key, StringComparer.OrdinalIgnoreCase)
                .Select(static group => new
                {
                    section = group.Key,
                    count = group.Count(),
                    sampleFiles = group.Take(3).Select(static item => Path.GetFileName(item.FilePath)).ToArray()
                })
                .ToArray(),
            privacy = "This ignored local proof records counts and filenames only; it does not include absolute paths or media payloads."
        };

        string outputPath = Path.Combine(evidenceDir, "media-catalog-coverage.json");
        File.WriteAllText(outputPath, JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }));
    }

    private static void WriteDecodabilitySummary(MediaCatalogSnapshot snapshot)
    {
        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-media-catalog-decodability");
        Directory.CreateDirectory(evidenceDir);

        object summary = new
        {
            schema = "winui-media-catalog-decodability.v1",
            date = "2026-05-06",
            audioCount = snapshot.AudioItems.Count,
            audioWithDurationLabels = snapshot.AudioItems.Count(static item => !string.IsNullOrWhiteSpace(item.DurationLabel)),
            videoCount = snapshot.VideoItems.Count,
            videosWithBinkHeaders = snapshot.VideoItems.Count(static item => HasBinkHeader(item.FilePath)),
            audioGroups = snapshot.AudioItems
                .GroupBy(static item => item.GroupName)
                .OrderByDescending(static group => group.Count())
                .ThenBy(static group => group.Key, StringComparer.OrdinalIgnoreCase)
                .Select(static group => new { group = group.Key, count = group.Count() })
                .ToArray(),
            videoSections = snapshot.VideoItems
                .GroupBy(static item => item.SectionName)
                .OrderBy(static group => group.Key, StringComparer.OrdinalIgnoreCase)
                .Select(static group => new { section = group.Key, count = group.Count() })
                .ToArray(),
            privacy = "This ignored local proof records counts, groups, and sections only; it does not include absolute paths, media headers, raw frames, or media payloads."
        };

        string outputPath = Path.Combine(evidenceDir, "media-catalog-decodability.json");
        File.WriteAllText(outputPath, JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }));
    }

    private static bool HasBinkHeader(string filePath)
    {
        if (!File.Exists(filePath))
        {
            return false;
        }

        using FileStream stream = File.OpenRead(filePath);
        if (stream.Length < 4)
        {
            return false;
        }

        Span<byte> header = stackalloc byte[4];
        int read = stream.Read(header);
        return read == 4 &&
            header[0] == (byte)'B' &&
            header[1] == (byte)'I' &&
            header[2] == (byte)'K';
    }

    private static string? ResolveReadOnlyGameDirectory()
    {
        string? explicitGameDirectory = Environment.GetEnvironmentVariable("ONSLAUGHT_BEA_GAME_DIR");
        if (!string.IsNullOrWhiteSpace(explicitGameDirectory))
        {
            return Path.GetFullPath(explicitGameDirectory);
        }

        return AppConfig.DetectGameDirectory();
    }

    private static string ResolveRepoRoot()
    {
        return Path.GetFullPath(
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }
}
