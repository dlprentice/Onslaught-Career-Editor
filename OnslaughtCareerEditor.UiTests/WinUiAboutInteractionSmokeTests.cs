using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiAboutInteractionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies About/product-lane copy through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void About_StatesWinUiProductLaneAndKeepsArchivedLanesOutOfPrimaryCopy()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-about-interaction");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "about";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            Assert.That(TryGetName(FindByAutomationId(window, "AboutPageTitle")), Is.EqualTo("About Onslaught Toolkit"));
            Assert.That(TryGetName(FindByAutomationId(window, "AboutProductSummary")), Does.Contain("Primary Windows app"));
            Assert.That(TryGetName(FindByAutomationId(window, "AboutProductSummary")), Does.Contain("playable copied-game patching"));
            Assert.That(TryGetName(FindByAutomationId(window, "AboutProductLaneNote")), Does.Contain("primary user-facing Windows product lane"));
            Assert.That(TryGetName(FindByAutomationId(window, "AboutProductLaneNote")), Does.Contain("historical app references remain separate"));
            Assert.That(TryGetName(FindByAutomationId(window, "AboutVersionText")), Does.StartWith("Version:"));

            Assert.That(WindowContainsName(window, "Electron"), Is.False, "About should not present Electron as a primary product lane.");
            Assert.That(WindowContainsName(window, "Python"), Is.False, "About should not present the old Python app as a primary product lane.");
            Assert.That(WindowContainsName(window, "WPF"), Is.False, "About should not present WPF as a primary product lane.");

            string screenshotPath = Path.Combine(evidenceDir, "01-about-product-summary.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "About screenshot should not be empty.");
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

    private static bool WindowContainsName(Window window, string text)
    {
        return window.FindAllDescendants()
            .Any(candidate => (TryGetName(candidate) ?? string.Empty).Contains(text, StringComparison.OrdinalIgnoreCase));
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
              "lastTab": 5,
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
