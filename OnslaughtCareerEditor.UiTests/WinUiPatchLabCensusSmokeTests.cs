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
/// Real-app smoke for Patch Lab census candidates: the expander opens, the status
/// names the TSV or the honest miss, and a filter either lists a row or says
/// what to try next. Census rows never expose a Stage control.
/// </summary>
public class WinUiPatchLabCensusSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Patch Lab census behavior through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void PatchLabCensus_ShowsCandidatesOrHonestMiss()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-patch-lab-census");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "binary";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Safe game copy", TimeSpan.FromSeconds(20));

            ExpandByAutomationId(window, "PatchBenchLabExpander");
            ExpandByAutomationId(window, "PatchLabCensusExpander");

            string status = WaitForNameContainsValue(window, "PatchLabCensusStatus", TimeSpan.FromSeconds(10), value =>
                value.Contains("census", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("not present", StringComparison.OrdinalIgnoreCase));
            Assert.That(status, Does.Not.Contain("Looking for the census TSV"));

            if (status.Contains("cannot be staged", StringComparison.OrdinalIgnoreCase))
            {
                SetTextBox(window, "PatchLabCensusSearchBox", "CLOCK_TICK");
                string filtered = WaitForNameContainsValue(window, "PatchLabCensusStatus", TimeSpan.FromSeconds(10), value =>
                    value.Contains("filter", StringComparison.OrdinalIgnoreCase) ||
                    value.Contains("CLOCK", StringComparison.OrdinalIgnoreCase) ||
                    value.Contains("candidate", StringComparison.OrdinalIgnoreCase));
                Assert.That(filtered.Length, Is.GreaterThan(0));
            }
            else
            {
                Assert.That(status, Does.Contain("not present").IgnoreCase);
            }

            AutomationElement? stage = window.FindFirstDescendant(cf => cf.ByAutomationId("PatchCensusStage"));
            Assert.That(stage, Is.Null, "Census candidates must not expose a Stage control.");

            CaptureScreenshot(window, evidenceDir, "01-patch-lab-census.png");

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

    private static void SetTextBox(Window window, string automationId, string text)
    {
        FindByAutomationId(window, automationId).AsTextBox().Enter(text);
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
              "lastTab": 3,
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
