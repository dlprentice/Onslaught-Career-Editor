using System;
using System.Diagnostics;
using System.Drawing;
using System.Drawing.Imaging;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Input;
using FlaUI.Core.Tools;
using FlaUI.Core.WindowsAPI;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[NonParallelizable]
public class WinUiHomeNavigationSmokeTests
{
    private sealed record HomeCaptureEvidence(
        string RelativeFileName,
        string Sha256,
        int X,
        int Y,
        int Width,
        int Height,
        int ProcessId,
        DateTime ProcessStartTimeUtc,
        string ExecutablePath,
        string ExecutableSha256,
        string ProductAssemblyPath,
        string ProductAssemblySha256,
        long MainWindowHandle,
        long UiaNativeWindowHandle,
        int WindowOwnerProcessId);

    private sealed record FocusedAutomationProbe(string? AutomationId, string? ExceptionType);

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches WinUI on Home and verifies each Home task button reaches its destination page.")]
    [Apartment(ApartmentState.STA)]
    [TestCase("HomeOpenSaveLabButton", "SaveAnalyzerFilePath")]
    [TestCase("HomeOpenMediaButton", "MediaAudioTabButton")]
    [TestCase("HomeOpenLoreButton", "LoreSearchBox")]
    [TestCase("HomeOpenPatchBenchButton", "PatchBenchScrollViewer")]
    [TestCase("HomeOpenAssetLibraryButton", "AssetSearchBox")]
    [TestCase("HomeOpenAboutButton", "AboutPageTitle")]
    [TestCase("HomeReviewSettingsButton", "SettingsPageScrollViewer")]
    public void Home_TaskButton_NavigatesToExpectedDestination(string homeButtonAutomationId, string destinationAutomationId)
    {
        using HomeNavigationSession session = LaunchHomeSession();
        WaitForText(session.Window, "Start Here", TimeSpan.FromSeconds(20));
        AutomationElement homeButton = FindByAutomationId(session.Window, homeButtonAutomationId);
        ScrollIntoView(homeButton);
        bool destinationReady = ActivateAndWait(
            session.Window,
            homeButton,
            () => TryFindByAutomationId(session.Window, destinationAutomationId) is not null);
        Assert.That(destinationReady, Is.True, $"Expected destination marker {destinationAutomationId} after clicking {homeButtonAutomationId}.");

        if (string.Equals(homeButtonAutomationId, "HomeOpenMediaButton", StringComparison.Ordinal))
        {
            Assert.That(
                Retry.WhileFalse(
                    () => string.Equals(TryGetFocusedAutomationId(session.Automation), "MediaAudioTabButton", StringComparison.Ordinal),
                    TimeSpan.FromSeconds(5)).Success,
                Is.True,
                "Home-to-Media navigation should focus the selected Audio tab.");
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches a true no-detection first run and verifies setup hierarchy plus destination focus.")]
    [Apartment(ApartmentState.STA)]
    public void Home_TrueFirstRun_PrioritizesSetupWithoutBlockingManualSaveLab()
    {
        using HomeNavigationSession session = LaunchHomeSession();
        Window window = session.Window;
        WaitForText(window, "Start Here", TimeSpan.FromSeconds(20));

        AutomationElement setupAction = FindByAutomationId(window, "HomeSetupActionButton");
        AutomationElement saveLabAction = FindByAutomationId(window, "HomeOpenSaveLabButton");
        Assert.That(setupAction.Name, Is.EqualTo("Choose game folder"));
        Assert.That(setupAction.IsEnabled, Is.True);
        Assert.That(saveLabAction.IsEnabled, Is.True, "Manual Save Lab browsing remains available before game-folder setup.");
        Assert.That(setupAction.BoundingRectangle.Top, Is.LessThan(saveLabAction.BoundingRectangle.Top), "The setup action should appear before the task grid on a true first run.");
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(TryGetFocusedAutomationId(session.Automation), "HomeSetupActionButton", StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "True first run should place arrival focus on the visible setup action.");
        Assert.That(FindByAutomationId(window, "AppStatusText").Name, Does.Contain("Home: choose a task"));

        string screenshotPath = Path.Combine(session.EvidenceDir, "00-home-true-first-run.png");
        window.Focus();
        Thread.Sleep(750);
        window.CaptureToFile(screenshotPath);
        Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
        Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "First-run screenshot should not be empty.");

        bool settingsReady = ActivateAndWait(
            window,
            setupAction,
            () => TryFindByAutomationId(window, "SettingsBrowseGameDirectoryButton") is not null);
        Assert.That(settingsReady, Is.True, "Setup action should open the game-folder controls in Settings.");
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(TryGetFocusedAutomationId(session.Automation), "SettingsBrowseGameDirectoryButton", StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "Setup navigation should move focus once to the explicit game-folder browse action.");
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches Home with a saved incomplete folder and verifies the review state remains truthful.")]
    [Apartment(ApartmentState.STA)]
    public void Home_InvalidConfiguredFolder_RequiresReviewWithoutBlockingManualSaveLab()
    {
        string invalidGameDirectory = Path.Combine(
            ResolveRepoRoot(),
            "subagents",
            "winui-home-navigation",
            "2026-05-27",
            "fixtures",
            "invalid-game");
        Directory.CreateDirectory(invalidGameDirectory);

        using HomeNavigationSession session = LaunchHomeSession(invalidGameDirectory, "invalid");
        Window window = session.Window;
        WaitForText(window, "Review your game folder", TimeSpan.FromSeconds(20));

        Assert.That(FindByAutomationId(window, "HomeSetupActionButton").Name, Is.EqualTo("Review game folder"));
        Assert.That(FindByAutomationId(window, "HomeOpenSaveLabButton").IsEnabled, Is.True);
        Assert.That(FindByAutomationId(window, "HomeSetupTitle").Name, Is.EqualTo("Setup needs attention"));
        Assert.That(FindByAutomationId(window, "ShellGameDirectoryStatus").Name, Is.EqualTo("Game folder: Needs review"));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches with a temporarily unavailable configured folder and verifies unrelated settings do not erase it.")]
    [Apartment(ApartmentState.STA)]
    public void Settings_MissingConfiguredFolder_PreservesPathWhenMediaPreferencesChange()
    {
        string missingGameDirectory = Path.Combine(
            ResolveRepoRoot(),
            "subagents",
            "winui-home-navigation",
            "2026-05-27",
            "fixtures",
            $"missing-game-{Guid.NewGuid():N}");
        Assert.That(Directory.Exists(missingGameDirectory), Is.False, "The regression fixture must represent an unavailable folder.");

        using HomeNavigationSession session = LaunchHomeSession(missingGameDirectory, "missing-configured-folder");
        Window window = session.Window;
        WaitForText(window, "Review your game folder", TimeSpan.FromSeconds(20));

        AutomationElement reviewAction = FindByAutomationId(window, "HomeSetupActionButton");
        Assert.That(
            ActivateAndWait(
                window,
                reviewAction,
                () => TryFindByAutomationId(window, "SettingsPageScrollViewer") is not null),
            Is.True,
            "Review action should open Settings for the remembered unavailable folder.");

        Assert.That(
            FindByAutomationId(window, "SettingsGameDirectoryStatus").Name,
            Is.EqualTo("Directory does not exist."));
        Assert.That(
            FindByAutomationId(window, "SettingsGameDirectorySummary").Name,
            Is.EqualTo(Path.GetFileName(missingGameDirectory)));

        ToggleByAutomationId(window, "SettingsAllowBackgroundAudioToggle");
        Assert.That(
            Retry.WhileFalse(
                () => ConfigStoresGameDirectoryAndAudioPreference(
                    session.ConfigPath,
                    missingGameDirectory,
                    expectedAllowBackgroundAudio: false),
                TimeSpan.FromSeconds(10)).Success,
            Is.True,
            "Saving an unrelated media preference must preserve the unavailable configured path.");
        Assert.That(FindByAutomationId(window, "ShellGameDirectoryStatus").Name, Is.EqualTo("Game folder: Needs review"));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Captures first-run and ready Home hierarchy at normal and compact widths without navigating.")]
    [Apartment(ApartmentState.STA)]
    public void Home_NewcomerHierarchy_CapturesFirstRunReadyAndCompactWithoutNavigation()
    {
        string evidenceRoot = Path.Combine(
            ResolveRepoRoot(),
            "subagents",
            "winui-home-navigation",
            "2026-05-27");
        string runName = $"home-newcomer-{DateTime.UtcNow:yyyyMMddTHHmmssfffZ}-{Guid.NewGuid():N}";
        string stagingDirectory = Path.Combine(evidenceRoot, $".{runName}.partial");
        string acceptedDirectory = Path.Combine(evidenceRoot, runName);
        Directory.CreateDirectory(stagingDirectory);
        var captures = new List<HomeCaptureEvidence>();
        Rectangle normalBounds = new(16, 16, 1100, 900);
        try
        {
            using (HomeNavigationSession firstRunSession = LaunchHomeSession())
            {
                Window firstRunWindow = firstRunSession.Window;
                WaitForText(firstRunWindow, "Start Here", TimeSpan.FromSeconds(20));

                AutomationElement setupAction = FindByAutomationId(firstRunWindow, "HomeSetupActionButton");
                AutomationElement primaryTasksHeading = FindByAutomationId(firstRunWindow, "HomePrimaryTasksTitle");
                Assert.That(setupAction.IsOffscreen, Is.False, "The first-run setup action must be visibly available.");
                Assert.That(
                    setupAction.BoundingRectangle.Top,
                    Is.LessThan(primaryTasksHeading.BoundingRectangle.Top),
                    "Visible first-run setup guidance must precede the task hierarchy.");
                AssertHomeArrivalFocus(
                    firstRunSession,
                    "HomeSetupActionButton",
                    TimeSpan.FromSeconds(10),
                    "A true first run must focus the visible setup action first.");

                captures.Add(CaptureReceiptBoundHomeWindow(
                    firstRunSession,
                    normalBounds,
                    Path.Combine(stagingDirectory, "first-run-normal.png"),
                    ["HomeSetupActionButton", "HomePrimaryTasksTitle", "HomeOpenPatchBenchButton"]));
            }

            string readyGameDirectory = Path.Combine(evidenceRoot, "fixtures", "full-game");
            Directory.CreateDirectory(Path.Combine(readyGameDirectory, "data"));
            File.WriteAllBytes(Path.Combine(readyGameDirectory, "BEA.exe"), new byte[] { 0 });

            using (HomeNavigationSession readySession = LaunchHomeSession(readyGameDirectory, "ready"))
            {
                Window window = readySession.Window;
                WaitForText(window, "Game directory configured: full-game.", TimeSpan.FromSeconds(20));

                Assert.That(FindByAutomationId(window, "HomeSetupTitle").Name, Is.EqualTo("Setup"));
                AutomationElement patchBenchHeading = FindByAutomationId(window, "HomePatchModsTitle");
                AutomationElement saveLabHeading = FindByAutomationId(window, "HomeSaveOptionsTitle");
                AutomationElement patchBenchAction = FindByAutomationId(window, "HomeOpenPatchBenchButton");
                AutomationElement saveLabAction = FindByAutomationId(window, "HomeOpenSaveLabButton");
                Assert.That(patchBenchAction.IsEnabled, Is.True);
                Assert.That(saveLabAction.IsEnabled, Is.True);
                Rectangle patchBenchBounds = patchBenchHeading.BoundingRectangle;
                Rectangle saveLabBounds = saveLabHeading.BoundingRectangle;
                Assert.That(
                    patchBenchBounds.Top < saveLabBounds.Top ||
                    (Math.Abs(patchBenchBounds.Top - saveLabBounds.Top) <= 2 && patchBenchBounds.Left < saveLabBounds.Left),
                    Is.True,
                    "The safe-copy task should precede Save Lab in the rendered Home reading order.");
                Assert.That(FindByAutomationId(window, "ShellGameDirectoryStatus").Name, Is.EqualTo("Game folder: full-game"));
                AssertHomeArrivalFocus(
                    readySession,
                    "HomeOpenPatchBenchButton",
                    TimeSpan.FromSeconds(10),
                    "A ready Home arrival should focus the first usable task instead of the closed setup prompt.");

                string[] readyMarkers =
                [
                    "HomePrimaryTasksTitle",
                    "HomePatchModsTitle",
                    "HomeOpenPatchBenchButton",
                    "HomeSaveOptionsTitle",
                    "HomeOpenSaveLabButton",
                    "HomeOpenConfigurationEditorButton",
                ];
                captures.Add(CaptureReceiptBoundHomeWindow(
                    readySession,
                    normalBounds,
                    Path.Combine(stagingDirectory, "ready-normal.png"),
                    readyMarkers));

                Rectangle compactBounds = new Rectangle(16, 16, 760, 820);
                captures.Add(CaptureReceiptBoundHomeWindow(
                    readySession,
                    compactBounds,
                    Path.Combine(stagingDirectory, "ready-760.png"),
                    readyMarkers,
                    () =>
                    {
                        ScrollIntoView(FindByAutomationId(window, "HomePrimaryTasksTitle"));
                        WaitForHomeLayout(window, readyMarkers, TimeSpan.FromSeconds(5));
                        AssertHomeElementsInsideWindow(window, compactBounds, readyMarkers);
                        AssertHomeHasNoHorizontalOverflow(window);
                    }));
            }

            PublishHomeAcceptanceRun(stagingDirectory, acceptedDirectory, captures);
        }
        catch
        {
            TryDeleteDirectory(stagingDirectory);
            throw;
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches WinUI on Home and verifies Game Options deep-link navigation.")]
    [Apartment(ApartmentState.STA)]
    public void Home_OpenConfigurationEditorButton_ShowsConfigurationEditorTab()
    {
        using HomeNavigationSession session = LaunchHomeSession();
        Window window = session.Window;

        WaitForText(window, "Start Here", TimeSpan.FromSeconds(20));
        AutomationElement deepLinkButton = FindByAutomationId(window, "HomeOpenConfigurationEditorButton");
        ScrollIntoView(deepLinkButton);

        bool configurationReady = ActivateAndWait(
            window,
            deepLinkButton,
            () => TryFindByAutomationId(window, "ConfigurationInputFile") is not null
                && TryFindByAutomationId(window, "ConfigurationEditorScrollViewer") is not null
                && TryFindByAutomationId(window, "ConfigurationStatusInfo") is not null);
        Assert.That(configurationReady, Is.True, "Expected Game Options inputs after Home deep-link.");

        bool analyzerHidden = Retry.WhileFalse(
            () => TryFindByAutomationId(window, "SaveAnalyzerFilePath") is null,
            TimeSpan.FromSeconds(5)).Success;
        Assert.That(analyzerHidden, Is.True, "Expected Save Analyzer tab content hidden after Game Options deep-link.");

        string screenshotPath = Path.Combine(session.EvidenceDir, "01-home-configuration-editor-deeplink.png");
        window.Focus();
        Thread.Sleep(1_000);
        window.CaptureToFile(screenshotPath);
        Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
        Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Deep-link screenshot should not be empty.");
    }

    private sealed class HomeNavigationSession : IDisposable
    {
        public HomeNavigationSession(Application app, UIA3Automation automation, Window window, string evidenceDir, string configPath, string executablePath, string focusRunId)
        {
            App = app;
            Automation = automation;
            Window = window;
            EvidenceDir = evidenceDir;
            ConfigPath = configPath;
            ExecutablePath = executablePath;
            FocusRunId = focusRunId;
        }

        public Application App { get; }

        public UIA3Automation Automation { get; }

        public Window Window { get; }

        public string EvidenceDir { get; }

        public string ConfigPath { get; }

        public string ExecutablePath { get; }

        public string FocusRunId { get; }

        public void Dispose()
        {
            Automation.Dispose();
            try
            {
                App.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (!App.HasExited)
            {
                App.Kill();
            }
        }
    }

    private static HomeNavigationSession LaunchHomeSession(string? gameDirectory = null, string stateName = "unset")
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-home-navigation", "2026-05-27");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir, gameDirectory, stateName);
        string configPath = Path.Combine(appDataDir, "OnslaughtCareerEditor", "config.json");
        string focusRunId = Guid.NewGuid().ToString("N");
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "home";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_FOCUS_DIAGNOSTICS"] = "1";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_FOCUS_RUN_ID"] = focusRunId;
        startInfo.Environment["ONSLAUGHT_GAME_DIR_CANDIDATES"] = string.Empty;
        startInfo.Environment["ONSLAUGHT_STEAM_ROOT_CANDIDATES"] = Path.Combine(appDataDir, "empty-steam-root");

        Application app = Application.Launch(startInfo);
        var automation = new UIA3Automation();
        Window window = WaitForMainWindow(app, automation);
        return new HomeNavigationSession(app, automation, window, evidenceDir, configPath, exePath, focusRunId);
    }

    private static HomeCaptureEvidence CaptureReceiptBoundHomeWindow(
        HomeNavigationSession session,
        Rectangle targetBounds,
        string outputPath,
        IReadOnlyList<string> markerAutomationIds,
        Action? postResizeRealization = null)
    {
        var operations = new FlaUiReceiptBoundVisualCaptureOperations(session.App, session.Window, session.ExecutablePath);
        ReceiptBoundAppIdentity expectedIdentity = operations.ReadIdentity();
        ReceiptBoundWindowState originalState = operations.ReadWindowState();
        Bitmap? bitmap = null;
        Directory.CreateDirectory(Path.GetDirectoryName(outputPath)!);
        Assert.That(File.Exists(outputPath), Is.False, $"Home acceptance evidence destination must be fresh: {outputPath}");
        string temporaryPath = $"{outputPath}.{Guid.NewGuid():N}.tmp";
        try
        {
            try
            {
                operations.ShowRestored();
                operations.PositionWindow(targetBounds);
                operations.SetForeground();
                operations.WaitForForegroundAndBounds(targetBounds, TimeSpan.FromSeconds(5));
                Assert.That(operations.ReadIdentity(), Is.EqualTo(expectedIdentity), "Toolkit identity changed after Home resize.");

                postResizeRealization?.Invoke();
                WaitForHomeLayout(session.Window, markerAutomationIds, TimeSpan.FromSeconds(5));
                operations.WaitForForegroundAndBounds(targetBounds, TimeSpan.FromSeconds(5));
                IReadOnlyList<GuidedSaveVisualMarker> beforeMarkers = markerAutomationIds.Select(operations.ReadMarker).ToArray();
                AssertHomeMarkersInsideImage(beforeMarkers, targetBounds.Size);

                operations.SetTopmost();
                operations.SetForeground();
                operations.WaitForForegroundAndBounds(targetBounds, TimeSpan.FromSeconds(5));
                Assert.That(operations.ReadIdentity(), Is.EqualTo(expectedIdentity), "Toolkit identity changed immediately before Home capture.");
                bitmap = operations.CaptureBoundWindow(expectedIdentity.MainWindowHandle, targetBounds);
                IReadOnlyList<GuidedSaveVisualMarker> afterMarkers = markerAutomationIds.Select(operations.ReadMarker).ToArray();
                Assert.That(afterMarkers, Is.EqualTo(beforeMarkers), "Home marker bounds changed during receipt-bound capture.");
                Assert.That(operations.ReadIdentity(), Is.EqualTo(expectedIdentity), "Toolkit identity changed immediately after Home capture.");
                AssertHomeToolkitImage(bitmap, beforeMarkers);

                using (FileStream encoded = new(temporaryPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
                {
                    bitmap.Save(encoded, ImageFormat.Png);
                    encoded.Flush(flushToDisk: true);
                }
                using (FileStream stream = File.Open(temporaryPath, FileMode.Open, FileAccess.Read, FileShare.Read))
                using (var reopenedSource = new Bitmap(stream))
                using (var reopened = new Bitmap(reopenedSource))
                {
                    Assert.That(reopened.Size, Is.EqualTo(targetBounds.Size));
                    AssertHomeToolkitImage(reopened, beforeMarkers);
                }
            }
            finally
            {
                bitmap?.Dispose();
                bitmap = null;
                operations.RestoreWindowState(originalState);
            }

            File.Move(temporaryPath, outputPath);
            TestContext.Progress.WriteLine($"Home Toolkit capture: {outputPath}; Bounds={targetBounds}; PID={expectedIdentity.ProcessId}; HWND=0x{expectedIdentity.MainWindowHandle.ToInt64():X}");
            return new HomeCaptureEvidence(
                Path.GetFileName(outputPath),
                Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(outputPath))),
                targetBounds.X,
                targetBounds.Y,
                targetBounds.Width,
                targetBounds.Height,
                expectedIdentity.ProcessId,
                expectedIdentity.ProcessStartTimeUtc,
                expectedIdentity.ExecutablePath,
                expectedIdentity.ExecutableSha256,
                expectedIdentity.ProductAssemblyPath,
                expectedIdentity.ProductAssemblySha256,
                expectedIdentity.MainWindowHandle.ToInt64(),
                expectedIdentity.UiaNativeWindowHandle.ToInt64(),
                expectedIdentity.WindowOwnerProcessId);
        }
        catch
        {
            File.Delete(temporaryPath);
            throw;
        }
        finally
        {
            File.Delete(temporaryPath);
            bitmap?.Dispose();
        }
    }

    private static void PublishHomeAcceptanceRun(
        string stagingDirectory,
        string acceptedDirectory,
        IReadOnlyList<HomeCaptureEvidence> captures)
    {
        Assert.That(captures, Has.Count.EqualTo(3), "Home acceptance requires exactly three validated captures.");
        Assert.That(Directory.Exists(stagingDirectory), Is.True);
        Assert.That(Directory.Exists(acceptedDirectory), Is.False, "The unique Home acceptance destination must be fresh.");
        foreach (HomeCaptureEvidence capture in captures)
        {
            string capturePath = Path.Combine(stagingDirectory, capture.RelativeFileName);
            Assert.That(File.Exists(capturePath), Is.True, $"Missing staged Home capture: {capture.RelativeFileName}");
            Assert.That(
                Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(capturePath))),
                Is.EqualTo(capture.Sha256),
                $"Staged Home capture hash changed: {capture.RelativeFileName}");
        }

        const string manifestFileName = "home-acceptance-manifest.json";
        string temporaryManifestName = $".{manifestFileName}.{Guid.NewGuid():N}.tmp";
        string temporaryManifestPath = Path.Combine(stagingDirectory, temporaryManifestName);
        string acceptedTemporaryManifestPath = Path.Combine(acceptedDirectory, temporaryManifestName);
        string acceptedManifestPath = Path.Combine(acceptedDirectory, manifestFileName);
        try
        {
            var manifest = new
            {
                SchemaVersion = 1,
                Captures = captures,
            };
            using (FileStream stream = new(temporaryManifestPath, FileMode.CreateNew, FileAccess.Write, FileShare.None))
            {
                JsonSerializer.Serialize(stream, manifest, new JsonSerializerOptions { WriteIndented = true });
                stream.Flush(flushToDisk: true);
            }
            using (JsonDocument document = JsonDocument.Parse(File.ReadAllText(temporaryManifestPath)))
            {
                Assert.That(document.RootElement.GetProperty("SchemaVersion").GetInt32(), Is.EqualTo(1));
                Assert.That(document.RootElement.GetProperty("Captures").GetArrayLength(), Is.EqualTo(3));
            }
            Directory.Move(stagingDirectory, acceptedDirectory);
            File.Move(acceptedTemporaryManifestPath, acceptedManifestPath);
        }
        catch
        {
            if (Directory.Exists(acceptedDirectory) && !File.Exists(acceptedManifestPath))
            {
                TryDeleteDirectory(acceptedDirectory);
            }
            throw;
        }
        finally
        {
            File.Delete(temporaryManifestPath);
            File.Delete(acceptedTemporaryManifestPath);
        }
    }

    private static void TryDeleteDirectory(string path)
    {
        if (Directory.Exists(path))
        {
            Directory.Delete(path, recursive: true);
        }
    }

    private static void WaitForHomeLayout(Window window, IReadOnlyList<string> automationIds, TimeSpan timeout)
    {
        Rectangle[]? previous = null;
        int stableSamples = 0;
        DateTime deadline = DateTime.UtcNow + timeout;
        while (DateTime.UtcNow < deadline)
        {
            Rectangle[] current = automationIds
                .Select(id => FindByAutomationId(window, id).BoundingRectangle)
                .ToArray();
            if (current.All(bounds => bounds.Width > 0 && bounds.Height > 0) &&
                previous is not null &&
                current.SequenceEqual(previous))
            {
                stableSamples++;
                if (stableSamples >= 2)
                {
                    return;
                }
            }
            else
            {
                stableSamples = 0;
            }
            previous = current;
            Thread.Sleep(100);
        }

        Assert.Fail("Home layout did not reach stable realized bounds before capture.");
    }

    private static void AssertHomeElementsInsideWindow(Window window, Rectangle windowBounds, IReadOnlyList<string> automationIds)
    {
        foreach (string automationId in automationIds)
        {
            Rectangle bounds = FindByAutomationId(window, automationId).BoundingRectangle;
            Assert.That(
                bounds.Width > 0 && bounds.Height > 0 &&
                bounds.Left >= windowBounds.Left && bounds.Right <= windowBounds.Right &&
                bounds.Top >= windowBounds.Top && bounds.Bottom <= windowBounds.Bottom,
                Is.True,
                $"Home element {automationId} must remain fully visible inside the compact Toolkit HWND. Element={bounds}; HWND={windowBounds}.");
        }
    }

    private static void AssertHomeHasNoHorizontalOverflow(Window window)
    {
        AutomationElement scrollViewer = FindByAutomationId(window, "HomePageScrollViewer");
        Assert.That(scrollViewer.Patterns.Scroll.IsSupported, Is.True, "Home scroll host must expose its scroll contract.");
        Assert.That(
            scrollViewer.Patterns.Scroll.Pattern.HorizontallyScrollable.Value,
            Is.False,
            "Compact Home must not expose horizontal scrolling.");
    }

    private static void AssertHomeMarkersInsideImage(IReadOnlyList<GuidedSaveVisualMarker> markers, Size imageSize)
    {
        foreach (GuidedSaveVisualMarker marker in markers)
        {
            Assert.That(
                marker.Bounds.Width > 0 && marker.Bounds.Height > 0 &&
                marker.Bounds.Left >= 0 && marker.Bounds.Top >= 0 &&
                marker.Bounds.Right <= imageSize.Width && marker.Bounds.Bottom <= imageSize.Height,
                Is.True,
                $"Home marker {marker.Name} must be inside the receipt-bound image. Marker={marker.Bounds}; Image={imageSize}.");
        }
    }

    private static void AssertHomeToolkitImage(Bitmap bitmap, IReadOnlyList<GuidedSaveVisualMarker> markers)
    {
        Assert.That(HasKnownCodexDesktopSignature(bitmap), Is.False, "Home screenshot matches the known Codex Desktop signature.");
        Assert.That(HasRenderedToolkitHeader(bitmap), Is.True, "Home screenshot does not contain the rendered Toolkit blue header signature.");
        foreach (GuidedSaveVisualMarker marker in markers)
        {
            Assert.That(
                HasRenderedActivity(bitmap, marker.Bounds),
                Is.True,
                $"Home marker {marker.Name} is not visibly rendered in the captured Toolkit image.");
        }
    }

    private static bool HasRenderedToolkitHeader(Bitmap bitmap)
    {
        if (bitmap.Width < 4 || bitmap.Height < 117)
        {
            return false;
        }

        int renderedSamples = 0;
        foreach (int x in new[] { bitmap.Width / 4, bitmap.Width / 2, bitmap.Width * 3 / 4 })
        {
            foreach (int y in new[] { 50, 70, 90 })
            {
                Color pixel = bitmap.GetPixel(x, y);
                if (pixel.A > 240 && pixel.B > pixel.R && pixel.R + pixel.G + pixel.B > 100)
                {
                    renderedSamples++;
                }
            }
        }
        return renderedSamples >= 6;
    }

    private static bool HasKnownCodexDesktopSignature(Bitmap bitmap)
    {
        int leftWidth = Math.Min(bitmap.Width / 2, 310);
        int magentaSamples = 0;
        for (int y = 0; y < bitmap.Height; y += 3)
        {
            for (int x = 0; x < leftWidth; x += 3)
            {
                Color pixel = bitmap.GetPixel(x, y);
                if (pixel.R >= 180 && pixel.B >= 130 && pixel.G <= 150 && pixel.R > pixel.G + 30)
                {
                    magentaSamples++;
                }
            }
        }

        int darkChromeSamples = 0;
        int chromeSampleCount = 0;
        for (int x = 0; x < bitmap.Width; x += Math.Max(1, bitmap.Width / 32))
        {
            Color pixel = bitmap.GetPixel(x, Math.Min(24, bitmap.Height - 1));
            chromeSampleCount++;
            if (pixel.R < 55 && pixel.G < 55 && pixel.B < 70 && Math.Abs(pixel.R - pixel.G) < 18)
            {
                darkChromeSamples++;
            }
        }
        return magentaSamples >= 4 && darkChromeSamples >= chromeSampleCount * 3 / 4;
    }

    private static bool HasRenderedActivity(Bitmap bitmap, Rectangle bounds)
    {
        int left = Math.Clamp(bounds.Left, 0, bitmap.Width - 1);
        int top = Math.Clamp(bounds.Top, 0, bitmap.Height - 1);
        int right = Math.Clamp(bounds.Right - 1, left, bitmap.Width - 1);
        int bottom = Math.Clamp(bounds.Bottom - 1, top, bitmap.Height - 1);
        Color first = bitmap.GetPixel(left, top);
        for (int y = top; y <= bottom; y += Math.Max(1, (bottom - top + 1) / 8))
        {
            for (int x = left; x <= right; x += Math.Max(1, (right - left + 1) / 8))
            {
                Color pixel = bitmap.GetPixel(x, y);
                if (Math.Abs(pixel.R - first.R) + Math.Abs(pixel.G - first.G) + Math.Abs(pixel.B - first.B) >= 24)
                {
                    return true;
                }
            }
        }
        return false;
    }

    private static void ToggleByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        window.Focus();
        if (element.Patterns.Toggle.IsSupported)
        {
            element.Patterns.Toggle.Pattern.Toggle();
        }
        else
        {
            element.Click();
        }
    }

    private static bool ConfigStoresGameDirectoryAndAudioPreference(
        string configPath,
        string expectedGameDirectory,
        bool expectedAllowBackgroundAudio)
    {
        try
        {
            using JsonDocument document = JsonDocument.Parse(File.ReadAllText(configPath));
            JsonElement root = document.RootElement;
            return root.TryGetProperty("gameDirectory", out JsonElement gameDirectory) &&
                string.Equals(gameDirectory.GetString(), expectedGameDirectory, StringComparison.Ordinal) &&
                root.TryGetProperty("allowBackgroundAudio", out JsonElement allowBackgroundAudio) &&
                allowBackgroundAudio.GetBoolean() == expectedAllowBackgroundAudio;
        }
        catch (IOException)
        {
            return false;
        }
        catch (JsonException)
        {
            return false;
        }
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static void ScrollIntoView(AutomationElement element)
    {
        try
        {
            if (element.Patterns.ScrollItem.IsSupported)
            {
                element.Patterns.ScrollItem.Pattern.ScrollIntoView();
            }
        }
        catch
        {
            // Best-effort positioning only.
        }
    }

    private static bool ActivateAndWait(Window window, AutomationElement element, Func<bool> isReady)
    {
        window.Focus();
        Thread.Sleep(200);

        try
        {
            if (element.Patterns.Invoke.IsSupported)
            {
                element.Patterns.Invoke.Pattern.Invoke();
                if (WaitUntilReady(isReady))
                {
                    return true;
                }
            }
        }
        catch (MissingMethodException)
        {
            // Some packaged WinUI/FlaUI invoke-provider paths throw here even though the button is clickable.
        }

        try
        {
            element.Focus();
            Keyboard.Press(VirtualKeyShort.RETURN);
            if (WaitUntilReady(isReady))
            {
                return true;
            }
        }
        catch
        {
            // Fall back to pointer activation below.
        }

        try
        {
            if (element.TryGetClickablePoint(out Point clickablePoint))
            {
                Mouse.Click(clickablePoint, MouseButton.Left);
                if (WaitUntilReady(isReady))
                {
                    return true;
                }
            }
        }
        catch
        {
            // Fall back to the element center below.
        }

        Rectangle bounds = element.BoundingRectangle;
        Mouse.Click(new Point(bounds.Left + bounds.Width / 2, bounds.Top + bounds.Height / 2), MouseButton.Left);
        return WaitUntilReady(isReady);
    }

    private static bool WaitUntilReady(Func<bool> isReady)
    {
        return Retry.WhileFalse(isReady, TimeSpan.FromSeconds(15)).Success;
    }

    private static AutomationElement? TryFindByAutomationId(Window window, string automationId)
    {
        try
        {
            return window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
        }
        catch
        {
            return null;
        }
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => TryFindByAutomationId(window, automationId),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
    }

    private static string? TryGetFocusedAutomationId(UIA3Automation automation)
    {
        return ProbeFocusedAutomation(automation).AutomationId;
    }

    private static FocusedAutomationProbe ProbeFocusedAutomation(UIA3Automation automation)
    {
        try
        {
            return new FocusedAutomationProbe(automation.FocusedElement()?.AutomationId, null);
        }
        catch (Exception ex)
        {
            return new FocusedAutomationProbe(null, ex.GetType().Name);
        }
    }

    private static void AssertHomeArrivalFocus(
        HomeNavigationSession session,
        string expectedAutomationId,
        TimeSpan timeout,
        string failureMessage)
    {
        var samples = new Queue<string>();
        bool focused = Retry.WhileFalse(
            () =>
            {
                FocusedAutomationProbe probe = ProbeFocusedAutomation(session.Automation);
                if (samples.Count >= 12)
                {
                    samples.Dequeue();
                }

                samples.Enqueue($"AutomationId={probe.AutomationId ?? "<none>"};ExceptionType={probe.ExceptionType ?? "<none>"}");
                return string.Equals(probe.AutomationId, expectedAutomationId, StringComparison.Ordinal);
            },
            timeout).Success;
        if (focused)
        {
            bool diagnosticConfirmed = Retry.WhileFalse(
                () => HasCurrentHomeFocusDiagnostic(session, expectedAutomationId),
                TimeSpan.FromSeconds(2)).Success;
            if (diagnosticConfirmed)
            {
                return;
            }
        }

        string diagnosticPath = Path.Combine(
            Path.GetDirectoryName(session.ConfigPath)!,
            "home-arrival-focus.jsonl");
        string diagnostics = File.Exists(diagnosticPath)
            ? string.Join(" | ", File.ReadLines(diagnosticPath).TakeLast(12))
            : "<none>";
        Assert.Fail($"{failureMessage} Global UIA samples: {string.Join(" | ", samples)}. App XAML diagnostics: {diagnostics}");
    }

    private static bool HasCurrentHomeFocusDiagnostic(HomeNavigationSession session, string expectedAutomationId)
    {
        string diagnosticPath = Path.Combine(
            Path.GetDirectoryName(session.ConfigPath)!,
            "home-arrival-focus.jsonl");
        if (!File.Exists(diagnosticPath))
        {
            return false;
        }

        string expectedTarget = expectedAutomationId switch
        {
            "HomeSetupActionButton" => "Setup",
            "HomeOpenPatchBenchButton" => "PatchBench",
            "HomeOpenSaveLabButton" => "SaveLab",
            _ => string.Empty,
        };
        foreach (string line in File.ReadLines(diagnosticPath).Reverse().Take(32))
        {
            try
            {
                using JsonDocument document = JsonDocument.Parse(line);
                JsonElement root = document.RootElement;
                if (root.GetProperty("ProcessId").GetInt32() == session.App.ProcessId
                    && string.Equals(root.GetProperty("RunId").GetString(), session.FocusRunId, StringComparison.Ordinal)
                    && string.Equals(root.GetProperty("Target").GetString(), expectedTarget, StringComparison.Ordinal)
                    && root.GetProperty("FocusVerified").ValueKind == JsonValueKind.True
                    && string.Equals(root.GetProperty("FinalXamlFocusedAutomationId").GetString(), expectedAutomationId, StringComparison.Ordinal))
                {
                    return true;
                }
            }
            catch (IOException)
            {
                return false;
            }
            catch (JsonException)
            {
                continue;
            }
        }

        return false;
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

    private static string PrepareIsolatedAppData(string evidenceDir, string? gameDirectory, string stateName)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata", stateName);
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        string gameDirectoryJson = string.IsNullOrWhiteSpace(gameDirectory)
            ? "null"
            : JsonSerializer.Serialize(gameDirectory);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            $$"""
            {
              "gameDirectory": {{gameDirectoryJson}},
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 820,
              "lastTab": 0,
              "lastSaveSubTab": 0,
              "lastMediaSubTab": 0,
              "assetCatalogPath": null,
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
