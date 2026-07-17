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
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiSettingsInteractionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Settings auto-detect/source-summary behavior through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void Settings_AutoDetectsReadOnlyInstallWithoutShowingFullPathByDefault()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string? gameDirectory = ResolveReadOnlyGameDirectory();
        if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
        {
            Assert.Ignore("No read-only Battle Engine Aquila install was available for Settings interaction smoke.");
        }

        string expectedFolderName = Path.GetFileName(gameDirectory.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-settings-interaction");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "settings";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Game Directory", TimeSpan.FromSeconds(20));
            Assert.That(TryGetName(FindByAutomationId(window, "SettingsGameDirectorySummary")), Is.EqualTo("Not configured"));
            Assert.That(WindowContainsName(window, gameDirectory), Is.False, "The full install path should not be visible before expanding path details.");

            FindByAutomationId(window, "SettingsAutoDetectGameDirectoryButton").AsButton().Invoke();

            bool detected = Retry.WhileFalse(
                () => string.Equals(
                    TryGetName(FindByAutomationId(window, "SettingsGameDirectorySummary")),
                    expectedFolderName,
                    StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(detected, Is.True, "Expected Auto-Detect to set the configured install summary.");

            string role = TryGetName(FindByAutomationId(window, "SettingsGameDirectoryRole")) ?? string.Empty;
            Assert.That(role, Does.Contain("Read-only source material"));

            string status = TryGetName(FindByAutomationId(window, "SettingsGameDirectoryStatus")) ?? string.Empty;
            Assert.That(status, Does.Contain("Valid game directory detected"));

            string saveCount = TryGetName(FindByAutomationId(window, "SettingsSaveFileCount")) ?? string.Empty;
            Assert.That(saveCount, Is.Not.Empty);
            Assert.That(saveCount, Does.Not.Contain(gameDirectory));
            Assert.That(saveCount, Does.Not.Contain(@":\"));

            Assert.That(WindowContainsName(window, gameDirectory), Is.False, "Primary Settings UI should summarize the install without exposing the full path.");

            ExpandPathDetails(window, "SettingsGameDirectoryPathDetails");
            string fullPath = Retry.WhileNull(
                () => TryGetTextBoxText(FindByAutomationId(window, "SettingsGameDirectoryPathTextBox")),
                TimeSpan.FromSeconds(5)).Result ?? string.Empty;
            Assert.That(Path.GetFullPath(fullPath), Is.EqualTo(Path.GetFullPath(gameDirectory)));

            string screenshotPath = Path.Combine(evidenceDir, "01-settings-auto-detected.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Settings screenshot should not be empty.");
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

    private static string? ResolveReadOnlyGameDirectory()
    {
        string? explicitGameDirectory = Environment.GetEnvironmentVariable("ONSLAUGHT_BEA_GAME_DIR");
        if (!string.IsNullOrWhiteSpace(explicitGameDirectory))
        {
            return Path.GetFullPath(explicitGameDirectory);
        }

        return AppConfig.DetectGameDirectory();
    }

    private static void ExpandPathDetails(Window window, string automationId)
    {
        AutomationElement expander = FindByAutomationId(window, automationId);
        if (expander.Patterns.ExpandCollapse.IsSupported)
        {
            expander.Patterns.ExpandCollapse.Pattern.Expand();
            return;
        }

        if (expander.Patterns.Invoke.IsSupported)
        {
            expander.Patterns.Invoke.Pattern.Invoke();
            return;
        }

        expander.Click();
    }

    private static bool WindowContainsName(Window window, string text)
    {
        return window.FindAllDescendants()
            .Any(candidate => (TryGetName(candidate) ?? string.Empty).Contains(text, StringComparison.OrdinalIgnoreCase));
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
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

    private static string? TryGetTextBoxText(AutomationElement element)
    {
        try
        {
            return element.AsTextBox().Text;
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
              "lastTab": 4,
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
