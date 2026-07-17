using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiRuntimeAccessibilitySmokeTests
{
    private const int SwMaximize = 3;

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and drives shell navigation through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void MainWindow_ShellNavigationIsNamedEnabledAndInvokableThroughUiAutomation()
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
        startInfo.Environment["ONSLAUGHT_GAME_DIR_CANDIDATES"] = string.Empty;
        startInfo.Environment["ONSLAUGHT_STEAM_ROOT_CANDIDATES"] = Path.Combine(appDataDir, "empty-steam-root");

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            AssertNamedEnabledControl(window, "ReviewSetupButton", "Review Setup");
            AssertNamedEnabledControl(window, "HomeNavigationItem", "Home");
            AssertNamedEnabledControl(window, "SavesNavigationItem", "Save Lab");
            AssertNamedEnabledControl(window, "MediaNavigationItem", "Media");
            AssertNamedEnabledControl(window, "AssetLibraryNavigationItem", "Asset Library");
            AssertNamedEnabledControl(window, "LoreNavigationItem", "Lore");
            AssertNamedEnabledControl(window, "BinaryNavigationItem", "Windowed & Mods");
            AssertNamedEnabledControl(window, "SettingsNavigationItem", "Settings");
            AssertNamedEnabledControl(window, "AboutNavigationItem", "About");

            InvokeElement(FindByAutomationId(window, "LoreNavigationItem"));
            InvokeElement(FindByAutomationId(window, "HomeNavigationItem"));
            WaitForText(window, "Start Here", TimeSpan.FromSeconds(10));
            Thread.Sleep(2_000);
            Assert.That(FindByAutomationId(window, "AppStatusText").Name, Does.Contain("Home: choose a task"), "A cached inactive Lore load must not replace Home status.");

            NavigateAndWait(window, "SavesNavigationItem", "Save Lab", "1. Inspect a file", "SavesPageTitle");
            var mediaNavigationTimer = Stopwatch.StartNew();
            NavigateAndWait(window, "MediaNavigationItem", "Media", "Source folder", "MediaPageTitle");
            mediaNavigationTimer.Stop();
            Assert.That(mediaNavigationTimer.Elapsed, Is.LessThan(TimeSpan.FromSeconds(10)), "Audio-first Media navigation should remain responsive.");
            Assert.That(
                HasLoadedNativeModule(app.ProcessId, "libvlc.dll") || HasLoadedNativeModule(app.ProcessId, "libvlccore.dll"),
                Is.False,
                "Audio-first Media navigation must not initialize native VLC before Video is requested.");
            NavigateAndWait(window, "AssetLibraryNavigationItem", "Asset Library", "Load generated catalog", "AssetLibraryPageTitle");
            string assetCatalogStatus = FindByAutomationId(window, "AssetCatalogStatus").Name;
            Assert.That(assetCatalogStatus, Does.Contain("generated catalog is loaded"));
            Assert.That(assetCatalogStatus, Does.Contain("generated export folder"));
            Assert.That(assetCatalogStatus, Does.Contain("asset_catalog/catalog.json"));
            AutomationElement assetFirstRunGuide = FindByAutomationId(window, "AssetCatalogFirstRunGuide");
            Assert.That(assetFirstRunGuide.Name, Does.Contain("First run"));
            Assert.That(assetFirstRunGuide.Name, Does.Contain("Generate a catalog from your own game install"));
            Assert.That(assetFirstRunGuide.Name, Does.Contain("asset_catalog/catalog.json"));
            Assert.That(assetFirstRunGuide.Name, Does.Contain("does not bundle game assets"));
            NavigateAndWait(window, "LoreNavigationItem", "Lore", "Library", "LorePageTitle");
            NavigateAndWait(window, "BinaryNavigationItem", "Windowed & Mods", "Safe game copy", "BinaryPatchesPageTitle");
            NavigateAndWait(window, "SettingsNavigationItem", "Settings", "Game Directory", "SettingsPageTitle");
            NavigateAndWait(window, "AboutNavigationItem", "About", "About Onslaught Toolkit", "AboutPageTitle");

            InvokeElement(FindByAutomationId(window, "ReviewSetupButton"));
            WaitForText(window, "Game Directory", TimeSpan.FromSeconds(5));
            Assert.That(
                Retry.WhileFalse(
                    () => string.Equals(automation.FocusedElement()?.AutomationId, "SettingsBrowseGameDirectoryButton", StringComparison.Ordinal),
                    TimeSpan.FromSeconds(5)).Success,
                Is.True,
                "The shell setup CTA should focus the explicit game-folder browse action.");
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
    [Explicit("Proves a restored Video tab stays responsive and defers native VLC until a current-session request.")]
    [Apartment(ApartmentState.STA)]
    public void MediaPage_RestoredVideoDefersNativeVlcUntilExplicitVideoRequest()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string appDataDir = PrepareIsolatedAppData(lastTab: 1, lastMediaSubTab: 1);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "media";
        startInfo.Environment["ONSLAUGHT_GAME_DIR_CANDIDATES"] = string.Empty;
        startInfo.Environment["ONSLAUGHT_STEAM_ROOT_CANDIDATES"] = Path.Combine(appDataDir, "empty-steam-root");

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            WaitForText(window, "Video library", TimeSpan.FromSeconds(10));
            Assert.That(FindByAutomationId(window, "MediaVideoPlayerStatus").Name, Is.EqualTo("Video player starts on demand"));
            Assert.That(
                HasLoadedNativeModule(app.ProcessId, "libvlc.dll") || HasLoadedNativeModule(app.ProcessId, "libvlccore.dll"),
                Is.False,
                "Restoring the Video tab must not initialize native VLC during page construction.");

            InvokeElement(FindByAutomationId(window, "MediaVideoTabButton"));
            Assert.That(
                Retry.WhileFalse(
                    () => HasLoadedNativeModule(app.ProcessId, "libvlc.dll") || HasLoadedNativeModule(app.ProcessId, "libvlccore.dll"),
                    TimeSpan.FromSeconds(10)).Success,
                Is.True,
                "A current-session Video request should initialize native VLC on demand.");
            Assert.That(
                Retry.WhileFalse(
                    () => string.Equals(FindByAutomationId(window, "MediaVideoPlayerStatus").Name, "Select a video", StringComparison.Ordinal),
                    TimeSpan.FromSeconds(5)).Success,
                Is.True,
                "Successful on-demand initialization should leave Video ready for selection.");
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

    private static void AssertNamedEnabledControl(Window window, string automationId, string expectedName)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Name, Is.EqualTo(expectedName), $"{automationId} should expose a useful accessible name.");
        Assert.That(element.IsEnabled, Is.True, $"{automationId} should be enabled for keyboard/UIA users.");
    }

    private static void NavigateAndWait(
        Window window,
        string automationId,
        string expectedName,
        string expectedPageText,
        string headingAutomationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Name, Is.EqualTo(expectedName), $"{automationId} should expose a useful accessible name.");
        Assert.That(element.IsEnabled, Is.True, $"{automationId} should be enabled before navigation.");
        InvokeElement(element);
        WaitForText(window, expectedPageText, TimeSpan.FromSeconds(10));
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(element.Automation.FocusedElement()?.AutomationId, automationId, StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            $"Navigation-item entry should keep focus on {automationId}.");

        AutomationElement heading = FindByAutomationId(window, headingAutomationId);
        Assert.That(heading.Name, Is.Not.Empty, $"{headingAutomationId} should expose its visible title as its accessible name.");
        Assert.That(heading.FrameworkAutomationElement.HeadingLevel.ValueOrDefault, Is.EqualTo(HeadingLevel.Level1));
        AutomationElement[] visibleLevelOneHeadings = window
            .FindAllDescendants()
            .Where(candidate =>
                TryGetIsOffscreen(candidate) != true &&
                candidate.FrameworkAutomationElement.HeadingLevel.ValueOrDefault == HeadingLevel.Level1)
            .ToArray();
        Assert.That(visibleLevelOneHeadings.Select(candidate => candidate.AutomationId), Is.EqualTo(new[] { headingAutomationId }));
    }

    private static bool? TryGetIsOffscreen(AutomationElement element)
    {
        try
        {
            return element.Properties.IsOffscreen.ValueOrDefault;
        }
        catch
        {
            return null;
        }
    }

    private static void InvokeElement(AutomationElement element)
    {
        if (element.Patterns.Invoke.IsSupported)
        {
            element.Patterns.Invoke.Pattern.Invoke();
            return;
        }

        if (element.Patterns.SelectionItem.IsSupported)
        {
            element.Patterns.SelectionItem.Pattern.Select();
            return;
        }

        element.Click();
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static bool HasLoadedNativeModule(int processId, string moduleName)
    {
        using Process process = Process.GetProcessById(processId);
        return process.Modules
            .Cast<ProcessModule>()
            .Any(module => string.Equals(module.ModuleName, moduleName, StringComparison.OrdinalIgnoreCase));
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
        MaximizeForRuntimeSmoke(app.MainWindowHandle);
        return window!;
    }

    private static void MaximizeForRuntimeSmoke(IntPtr windowHandle)
    {
        if (windowHandle == IntPtr.Zero || !ShouldMaximizeForRuntimeSmoke())
        {
            return;
        }

        _ = ShowWindow(windowHandle, SwMaximize);
        _ = SetForegroundWindow(windowHandle);
        Thread.Sleep(500);
    }

    private static bool ShouldMaximizeForRuntimeSmoke()
    {
        string? value = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_VISUAL_CAPTURE_MAXIMIZE");
        return !string.Equals(value, "0", StringComparison.OrdinalIgnoreCase) &&
               !string.Equals(value, "false", StringComparison.OrdinalIgnoreCase);
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    private static string PrepareIsolatedAppData(int lastTab = -1, int lastMediaSubTab = 0)
    {
        string appDataDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-runtime-accessibility-smoke", "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            $$"""
            {
              "gameDirectory": null,
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 820,
              "lastTab": {{lastTab}},
              "lastSaveSubTab": 0,
              "lastMediaSubTab": {{lastMediaSubTab}},
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
