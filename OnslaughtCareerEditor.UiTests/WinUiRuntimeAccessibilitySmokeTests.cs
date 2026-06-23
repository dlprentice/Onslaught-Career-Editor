using System;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
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

            NavigateAndWait(window, "SavesNavigationItem", "Save Lab", "1. Inspect a file");
            NavigateAndWait(window, "MediaNavigationItem", "Media", "Source folder");
            NavigateAndWait(window, "AssetLibraryNavigationItem", "Asset Library", "Load generated catalog");
            NavigateAndWait(window, "LoreNavigationItem", "Lore", "Library");
            NavigateAndWait(window, "BinaryNavigationItem", "Windowed & Mods", "Safe game copy");
            NavigateAndWait(window, "SettingsNavigationItem", "Settings", "Game Directory");
            NavigateAndWait(window, "AboutNavigationItem", "About", "About Onslaught Toolkit");

            InvokeElement(FindByAutomationId(window, "ReviewSetupButton"));
            WaitForText(window, "Game Directory", TimeSpan.FromSeconds(5));
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

    private static void NavigateAndWait(Window window, string automationId, string expectedName, string expectedPageText)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Name, Is.EqualTo(expectedName), $"{automationId} should expose a useful accessible name.");
        Assert.That(element.IsEnabled, Is.True, $"{automationId} should be enabled before navigation.");
        InvokeElement(element);
        WaitForText(window, expectedPageText, TimeSpan.FromSeconds(10));
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

    private static string PrepareIsolatedAppData()
    {
        string appDataDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-runtime-accessibility-smoke", "appdata");
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
