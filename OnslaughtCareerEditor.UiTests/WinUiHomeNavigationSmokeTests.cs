using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[NonParallelizable]
public class WinUiHomeNavigationSmokeTests
{
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
        homeButton.AsButton().Invoke();

        bool destinationReady = Retry.WhileFalse(
            () => TryFindByAutomationId(session.Window, destinationAutomationId) is not null,
            TimeSpan.FromSeconds(15)).Success;
        Assert.That(destinationReady, Is.True, $"Expected destination marker {destinationAutomationId} after clicking {homeButtonAutomationId}.");
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
        deepLinkButton.AsButton().Invoke();

        bool configurationReady = Retry.WhileFalse(
            () => TryFindByAutomationId(window, "ConfigurationInputFile") is not null
                && TryFindByAutomationId(window, "ConfigurationEditorScrollViewer") is not null
                && TryFindByAutomationId(window, "ConfigurationStatusInfo") is not null,
            TimeSpan.FromSeconds(15)).Success;
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
        public HomeNavigationSession(Application app, UIA3Automation automation, Window window, string evidenceDir)
        {
            App = app;
            Automation = automation;
            Window = window;
            EvidenceDir = evidenceDir;
        }

        public Application App { get; }

        public UIA3Automation Automation { get; }

        public Window Window { get; }

        public string EvidenceDir { get; }

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

    private static HomeNavigationSession LaunchHomeSession()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-home-navigation", "2026-05-27");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "home";

        Application app = Application.Launch(startInfo);
        var automation = new UIA3Automation();
        Window window = WaitForMainWindow(app, automation);
        return new HomeNavigationSession(app, automation, window, evidenceDir);
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

    private static string PrepareIsolatedAppData(string evidenceDir)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            """
            {
              "gameDirectory": null,
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
