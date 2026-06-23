using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiMediaInteractionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the WinUI app, reads the local game install, and briefly starts inline audio/video playback.")]
    [Apartment(ApartmentState.STA)]
    public void MediaPage_SelectsRealInstallAudioAndVideoThroughUi()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string? gameDirectory = ResolveReadOnlyGameDirectory();
        if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
        {
            Assert.Ignore("No read-only Battle Engine Aquila install was available for media interaction smoke.");
        }

        MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);
        MediaAudioItem? audioItem = snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Music" && File.Exists(item.FilePath));
        MediaVideoItem? videoItem = snapshot.VideoItems.FirstOrDefault(item => item.Name == "NVIDIA Logo" && File.Exists(item.FilePath))
                                    ?? snapshot.VideoItems.FirstOrDefault(item => item.Name == "Lost Toys Logo" && File.Exists(item.FilePath))
                                    ?? snapshot.VideoItems.FirstOrDefault(item => File.Exists(item.FilePath));
        if (audioItem is null || videoItem is null)
        {
            Assert.Ignore("Configured game install did not expose both audio and video catalog rows.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-media-interaction", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir, gameDirectory);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "media";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"] = "0";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Audio library", TimeSpan.FromSeconds(20));
            PlayAudioRow(window, audioItem, gameDirectory);
            window.CaptureToFile(Path.Combine(evidenceDir, "01-audio-playing.png"));

            FindByAutomationId(window, "MediaAudioStopButton").AsButton().Invoke();
            Retry.WhileTrue(
                () => FindByAutomationId(window, "MediaAudioStopButton").IsEnabled,
                TimeSpan.FromSeconds(5));

            FindByAutomationId(window, "MediaVideoTabButton").AsButton().Invoke();
            WaitForText(window, "Video library", TimeSpan.FromSeconds(10));
            PlayVideoRow(window, videoItem, gameDirectory);
            window.CaptureToFile(Path.Combine(evidenceDir, "02-video-playing.png"));

            FindByAutomationId(window, "MediaVideoStopButton").AsButton().Invoke();
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the WinUI app against the local install and samples multiple real media families without claiming all-row playback.")]
    [Apartment(ApartmentState.STA)]
    public void MediaPage_PlaysRepresentativeAudioAndVideoRowsThroughUi()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string? gameDirectory = ResolveReadOnlyGameDirectory();
        if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
        {
            Assert.Ignore("No read-only Battle Engine Aquila install was available for media interaction smoke.");
        }

        MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);
        MediaAudioItem?[] candidateAudioRows =
        {
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Music" && File.Exists(item.FilePath)),
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Tutorial" && File.Exists(item.FilePath)),
        };
        MediaAudioItem[] audioRows = candidateAudioRows.Where(item => item is not null)
            .Cast<MediaAudioItem>()
            .DistinctBy(item => item.FilePath, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        MediaVideoItem?[] candidateVideoRows =
        {
            snapshot.VideoItems.FirstOrDefault(item => item.Name == "Lost Toys Logo" && File.Exists(item.FilePath))
                ?? snapshot.VideoItems.FirstOrDefault(item => item.Name == "NVIDIA Logo" && File.Exists(item.FilePath)),
            snapshot.VideoItems.FirstOrDefault(item => item.SectionName == "Cutscenes" && File.Exists(item.FilePath)),
        };
        MediaVideoItem[] videoRows = candidateVideoRows.Where(item => item is not null)
            .Cast<MediaVideoItem>()
            .DistinctBy(item => item.FilePath, StringComparer.OrdinalIgnoreCase)
            .ToArray();

        if (audioRows.Length < 2 || videoRows.Length < 2)
        {
            Assert.Ignore("Configured game install did not expose two representative audio rows and two representative video rows.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-media-representative-playback", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        File.WriteAllText(
            Path.Combine(evidenceDir, "representative-playback-summary.json"),
            JsonSerializer.Serialize(
                new
                {
                    schema = "winui-media-representative-playback.v1",
                    privacy = "Rows, groups, sections, size labels, and duration labels only; no private absolute paths or media payloads.",
                    audio = audioRows.Select(item => new { item.Name, item.GroupName, item.DurationLabel }),
                    video = videoRows.Select(item => new { item.Name, item.SectionName, item.SizeText })
                },
                new JsonSerializerOptions { WriteIndented = true }));
        string appDataDir = PrepareIsolatedAppData(evidenceDir, gameDirectory);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "media";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"] = "0";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Audio library", TimeSpan.FromSeconds(20));
            foreach (MediaAudioItem audioRow in audioRows)
            {
                PlayAudioRow(window, audioRow, gameDirectory);
                FindByAutomationId(window, "MediaAudioStopButton").AsButton().Invoke();
                Retry.WhileTrue(
                    () => FindByAutomationId(window, "MediaAudioStopButton").IsEnabled,
                    TimeSpan.FromSeconds(5));
            }

            FindByAutomationId(window, "MediaVideoTabButton").AsButton().Invoke();
            WaitForText(window, "Video library", TimeSpan.FromSeconds(10));
            foreach (MediaVideoItem videoRow in videoRows)
            {
                PlayVideoRow(window, videoRow, gameDirectory);
                FindByAutomationId(window, "MediaVideoStopButton").AsButton().Invoke();
                Retry.WhileTrue(
                    () => FindByAutomationId(window, "MediaVideoStopButton").IsEnabled,
                    TimeSpan.FromSeconds(5));
            }

            window.CaptureToFile(Path.Combine(evidenceDir, "representative-playback-complete.png"));
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the WinUI app against the local install and samples broader real media families without claiming all-row playback.")]
    [Apartment(ApartmentState.STA)]
    public void MediaPage_PlaysBroaderFamilySampleRowsThroughUi()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string? gameDirectory = ResolveReadOnlyGameDirectory();
        if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
        {
            Assert.Ignore("No read-only Battle Engine Aquila install was available for broader media playback smoke.");
        }

        MediaCatalogSnapshot snapshot = new MediaCatalogService().Load(gameDirectory);
        MediaAudioItem[] audioRows = SelectBroaderAudioRows(snapshot);
        MediaVideoItem[] videoRows = SelectBroaderVideoRows(snapshot);

        if (audioRows.Length < 4 || videoRows.Length < 3)
        {
            Assert.Ignore("Configured game install did not expose the broader media family sample.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-media-broader-family-playback", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        File.WriteAllText(
            Path.Combine(evidenceDir, "broader-family-playback-summary.json"),
            JsonSerializer.Serialize(
                new
                {
                    schema = "winui-media-broader-family-playback.v1",
                    privacy = "Rows, groups, sections, size labels, and duration labels only; no private absolute paths or media payloads.",
                    audio = audioRows.Select(item => new { item.Name, item.GroupName, item.DurationLabel }),
                    video = videoRows.Select(item => new { item.Name, item.SectionName, item.SizeText })
                },
                new JsonSerializerOptions { WriteIndented = true }));

        string appDataDir = PrepareIsolatedAppData(evidenceDir, gameDirectory);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "media";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"] = "0";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Audio library", TimeSpan.FromSeconds(20));
            foreach (MediaAudioItem audioRow in audioRows)
            {
                PlayAudioRow(window, audioRow, gameDirectory);
                FindByAutomationId(window, "MediaAudioStopButton").AsButton().Invoke();
                Retry.WhileTrue(
                    () => FindByAutomationId(window, "MediaAudioStopButton").IsEnabled,
                    TimeSpan.FromSeconds(5));
            }

            FindByAutomationId(window, "MediaVideoTabButton").AsButton().Invoke();
            WaitForText(window, "Video library", TimeSpan.FromSeconds(10));
            foreach (MediaVideoItem videoRow in videoRows)
            {
                PlayVideoRow(window, videoRow, gameDirectory);
                FindByAutomationId(window, "MediaVideoStopButton").AsButton().Invoke();
                Retry.WhileTrue(
                    () => FindByAutomationId(window, "MediaVideoStopButton").IsEnabled,
                    TimeSpan.FromSeconds(5));
            }

            window.CaptureToFile(Path.Combine(evidenceDir, "broader-family-playback-complete.png"));
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    private static MediaAudioItem[] SelectBroaderAudioRows(MediaCatalogSnapshot snapshot)
    {
        MediaAudioItem?[] candidates =
        {
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Music" && File.Exists(item.FilePath)),
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Tutorial" && File.Exists(item.FilePath)),
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Status Messages" && File.Exists(item.FilePath)),
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName.StartsWith("Mission ", StringComparison.OrdinalIgnoreCase) && File.Exists(item.FilePath)),
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Racing" && File.Exists(item.FilePath)),
            snapshot.AudioItems.FirstOrDefault(item => item.GroupName == "Other" && File.Exists(item.FilePath)),
        };

        return candidates.Where(item => item is not null)
            .Cast<MediaAudioItem>()
            .DistinctBy(item => item.FilePath, StringComparer.OrdinalIgnoreCase)
            .Take(5)
            .ToArray();
    }

    private static MediaVideoItem[] SelectBroaderVideoRows(MediaCatalogSnapshot snapshot)
    {
        MediaVideoItem?[] candidates =
        {
            snapshot.VideoItems.FirstOrDefault(item => item.SectionName == "Main Videos" && item.Name == "Lost Toys Logo" && File.Exists(item.FilePath))
                ?? snapshot.VideoItems.FirstOrDefault(item => item.SectionName == "Main Videos" && File.Exists(item.FilePath)),
            snapshot.VideoItems.FirstOrDefault(item => item.SectionName == "Cutscenes" && File.Exists(item.FilePath)),
            snapshot.VideoItems.FirstOrDefault(item => item.SectionName.StartsWith("Mission Briefings / Episode ", StringComparison.OrdinalIgnoreCase) && File.Exists(item.FilePath)),
        };

        return candidates.Where(item => item is not null)
            .Cast<MediaVideoItem>()
            .DistinctBy(item => item.FilePath, StringComparer.OrdinalIgnoreCase)
            .ToArray();
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

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        textBox.Text = string.Empty;
        textBox.Enter(text);
    }

    private static void PlayAudioRow(Window window, MediaAudioItem audioItem, string gameDirectory)
    {
        SetTextBox(window, "MediaAudioSearchBox", audioItem.Name);
        AutomationElement audioLeaf = WaitForNamePrefix(window, audioItem.Name, TimeSpan.FromSeconds(15));
        audioLeaf.Click();

        AssertTextByAutomationId(window, "MediaAudioNowPlaying", audioItem.Name);
        AssertSummaryIsPublicSafe(window, "MediaAudioSourceSummary", gameDirectory, Path.GetFileName(audioItem.FilePath));

        FindByAutomationId(window, "MediaAudioPlayButton").AsButton().Invoke();
        bool audioStarted = Retry.WhileFalse(
            () => FindByAutomationId(window, "MediaAudioStopButton").IsEnabled,
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(audioStarted, Is.True, "Expected inline audio playback controls to become active.");
    }

    private static void PlayVideoRow(Window window, MediaVideoItem videoItem, string gameDirectory)
    {
        SetTextBox(window, "MediaVideoSearchBox", videoItem.Name);
        AutomationElement videoLeaf = WaitForNamePrefix(window, videoItem.Name, TimeSpan.FromSeconds(15));
        videoLeaf.Click();

        AssertTextByAutomationId(window, "MediaVideoSelected", videoItem.Name);
        AssertSummaryIsPublicSafe(window, "MediaVideoSourceSummary", gameDirectory, Path.GetFileName(videoItem.FilePath));
        Assert.That(FindByAutomationId(window, "MediaVideoPlayButton").IsEnabled, Is.True, "Expected selected video to expose a Play action.");
        FindByAutomationId(window, "MediaVideoPlayButton").AsButton().Invoke();
        bool videoStarted = Retry.WhileFalse(
            () => FindByAutomationId(window, "MediaVideoStopButton").IsEnabled,
            TimeSpan.FromSeconds(15)).Success;
        Assert.That(videoStarted, Is.True, "Expected inline video playback controls to become active.");
        bool videoTimeAdvanced = Retry.WhileFalse(
            () => (TryGetName(FindByAutomationId(window, "MediaVideoCurrentTime")) ?? "0:00") != "0:00",
            TimeSpan.FromSeconds(8)).Success;
        Assert.That(videoTimeAdvanced, Is.True, "Expected inline video playback time to advance.");
    }

    private static AutomationElement WaitForNamePrefix(Window window, string prefix, TimeSpan timeout)
    {
        AutomationElement? element = Retry.WhileNull(
            () => window.FindAllDescendants()
                .FirstOrDefault(candidate => TryGetName(candidate)?.StartsWith(prefix, StringComparison.OrdinalIgnoreCase) == true),
            timeout).Result;
        Assert.That(element, Is.Not.Null, $"Expected a visible media row starting with: {prefix}");
        return element!;
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static void AssertTextByAutomationId(Window window, string automationId, string expectedText)
    {
        string actual = TryGetName(FindByAutomationId(window, automationId)) ?? string.Empty;
        Assert.That(actual, Is.EqualTo(expectedText));
    }

    private static void AssertSummaryIsPublicSafe(Window window, string automationId, string gameDirectory, string expectedFileName)
    {
        string summary = TryGetName(FindByAutomationId(window, automationId)) ?? string.Empty;
        Assert.That(summary, Does.Contain(expectedFileName));
        Assert.That(summary, Does.Not.Contain(gameDirectory));
        Assert.That(summary, Does.Not.Contain(@":\"));
    }

    private static string? TryGetName(AutomationElement element)
    {
        try
        {
            return element.Name;
        }
        catch
        {
            return null;
        }
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByAutomationId(automationId)),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
    }

    private static Window WaitForMainWindow(Application app, UIA3Automation automation)
    {
        bool handleReady = Retry.WhileFalse(
            () => app.MainWindowHandle != IntPtr.Zero,
            TimeSpan.FromSeconds(30)).Success;

        if (!handleReady)
        {
            Assert.Ignore("Main window handle not available; ensure the app can launch in this desktop session.");
        }

        Window? window = Retry.WhileNull(
            () =>
            {
                try
                {
                    return automation.FromHandle(app.MainWindowHandle).AsWindow();
                }
                catch
                {
                    return null;
                }
            },
            TimeSpan.FromSeconds(30)).Result;

        Assert.That(window, Is.Not.Null);
        return window!;
    }

    private static string PrepareIsolatedAppData(string evidenceDir, string gameDirectory)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            $$"""
            {
              "gameDirectory": {{JsonSerializer.Serialize(gameDirectory)}},
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 820,
              "lastTab": 1,
              "lastSaveSubTab": 0,
              "lastMediaSubTab": 0,
              "allowBackgroundAudio": true,
              "allowBackgroundVideo": false,
              "preventAudioVideoOverlap": true
            }
            """);
        return appDataDir;
    }

    private static string ResolveWinUiAppPath()
    {
        string? explicitExePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_EXE_PATH");
        if (!string.IsNullOrWhiteSpace(explicitExePath))
        {
            return explicitExePath;
        }

        return Path.Combine(
            ResolveRepoRoot(),
            "OnslaughtCareerEditor.WinUI",
            "bin",
            "Debug",
            "net10.0-windows10.0.19041.0",
            "win-x64",
            "OnslaughtCareerEditor.WinUI.exe");
    }

    private static string ResolveRepoRoot()
    {
        return Path.GetFullPath(
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }
}
