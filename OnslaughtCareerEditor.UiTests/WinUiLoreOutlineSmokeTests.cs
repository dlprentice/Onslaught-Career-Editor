using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Real-app smoke for the Lore outline: opening a document fills On this page
/// with headings (or an honest empty sentence) and This page links to finishes
/// loading.
/// </summary>
public class WinUiLoreOutlineSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Lore outline behavior through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void LoreOutline_ListsHeadingsOnTheOpenDocument()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-lore-outline");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "lore";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Library", TimeSpan.FromSeconds(20));

            ExpandByAutomationId(window, "LoreOutlineExpander");
            string outline = WaitForNameContainsValue(window, "LoreOutlineStatus", TimeSpan.FromSeconds(15), value =>
                value.Contains("heading", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("no headings", StringComparison.OrdinalIgnoreCase));
            Assert.That(outline, Does.Not.Contain("Loading outline..."));

            ExpandByAutomationId(window, "LoreOutgoingExpander");
            string outgoing = WaitForNameContainsValue(window, "LoreOutgoingStatus", TimeSpan.FromSeconds(10), value =>
                value.Contains("link", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("unavailable", StringComparison.OrdinalIgnoreCase));
            Assert.That(outgoing, Does.Not.Contain("Loading outgoing links..."));

            CaptureScreenshot(window, evidenceDir, "01-lore-outline.png");

            app.Close();
            app = null;
        }
        finally
        {
            app?.Kill();
        }
    }

    private static void ExpandByAutomationId(Window window, string automationId)
    {
        AutomationElement expander = FindByAutomationId(window, automationId);
        var pattern = expander.Patterns.ExpandCollapse.PatternOrDefault;
        if (pattern is not null && pattern.ExpandCollapseState == FlaUI.Core.Definitions.ExpandCollapseState.Collapsed)
        {
            pattern.Expand();
        }
    }

    private static string WaitForNameContainsValue(
        Window window,
        string automationId,
        TimeSpan timeout,
        Func<string, bool> predicate)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        bool matched = Retry.WhileFalse(
            () => predicate(TryGetName(element) ?? string.Empty),
            timeout).Success;
        Assert.That(matched, Is.True, $"Expected '{automationId}' to satisfy the condition.");
        return TryGetName(element) ?? string.Empty;
    }

    private static void CaptureScreenshot(Window window, string evidenceDir, string fileName)
    {
        try
        {
            string path = Path.Combine(evidenceDir, fileName);
            window.CaptureToFile(path);
            TestContext.AddTestAttachment(path);
        }
        catch
        {
        }
    }

    private static string? TryGetName(AutomationElement? element)
    {
        try
        {
            return element?.Name;
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

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindAllDescendants()
                .Any(candidate => (TryGetName(candidate) ?? string.Empty).Contains(text, StringComparison.OrdinalIgnoreCase)),
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible UIA name containing: {text}");
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
              "windowHeight": 900,
              "lastTab": 2,
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
