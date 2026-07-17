using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiLaunchSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app on the desktop; run only in an interactive Windows session.")]
    [Apartment(ApartmentState.STA)]
    public void MainWindow_LaunchesAndShowsWinUiProductChrome()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string appDataDir = PrepareIsolatedAppData();
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();

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
            Assert.That(window!.Title, Does.Contain("Onslaught Toolkit"));
            Assert.That(app.HasExited, Is.False, "App should still be running after launch.");
            Assert.That(
                window.Patterns.Window.Pattern.WindowVisualState.Value,
                Is.EqualTo(WindowVisualState.Maximized),
                "The WinUI product window should start maximized for the broadest default workspace.");

            AutomationElement? navigation = window.FindFirstDescendant(cf => cf.ByName("Main navigation tabs"));
            Assert.That(navigation, Is.Not.Null, "Expected the WinUI main navigation in the app shell.");

            Assert.That(window.FindFirstDescendant(cf => cf.ByText("Home")), Is.Not.Null);
            Assert.That(window.FindFirstDescendant(cf => cf.ByText("Save Lab")), Is.Not.Null);
            Assert.That(window.FindFirstDescendant(cf => cf.ByText("Asset Library")), Is.Not.Null);
            Assert.That(window.FindFirstDescendant(cf => cf.ByText("Windowed & Mods")), Is.Not.Null);
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

    private static string PrepareIsolatedAppData()
    {
        string appDataDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-launch-smoke", "appdata");
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
              "lastTab": -1,
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

    private static string ResolveRepoRoot()
    {
        return Path.GetFullPath(
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }
}
