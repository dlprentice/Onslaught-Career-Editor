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
/// Real-app smoke for the Patch Lab row inspector: the Lab opens the inspector,
/// rows render with evidence text, a visible row can be staged from the inspector
/// (which ticks the same selection checkbox), and hidden companion rows refuse to
/// stage. Launches the built WinUI app; skipped when no build output exists.
/// </summary>
public class WinUiPatchLabInspectorSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Patch Lab inspector behavior through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void PatchLabInspector_ShowsRowsAndStagesThroughTheSelectionModel()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-patch-lab-inspector");
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

            // The Lab starts collapsed; open it and then the inspector.
            ExpandByAutomationId(window, "PatchBenchLabExpander");
            ExpandByAutomationId(window, "PatchLabInspectorExpander");

            string status = WaitForNameContainsValue(window, "PatchLabInspectorStatus", "patch rows", TimeSpan.FromSeconds(10));
            Assert.That(status, Does.Contain("Inspecting"), $"Inspector status should report the loaded catalog: {status}");
            Assert.That(status, Does.Contain("hidden companion row"), "The all-rows status should disclose hidden companion rows.");

            // A visible row renders its evidence boundary. Rows are Borders (no
            // automation peer), so the row is proven through its Stage button's
            // accessible name, which carries the row title.
            AutomationElement stageGoodies = FindByAutomationId(window, "PatchInspectorStage_goodies_gallery_display_unlock");
            Assert.That(TryGetName(stageGoodies), Does.Contain("Goodies").IgnoreCase,
                "The visible row's Stage button should name the row it belongs to.");
            Assert.That(stageGoodies.IsEnabled, Is.True, "A visible row's Stage button should be enabled.");

            // Staging routes through the shared selection model: the player-mods
            // status line above reacts exactly as if the checkbox had been ticked.
            InvokeElement(stageGoodies);
            string modsStatus = WaitForNameContainsValue(window, "PatchBenchPlayerModsSelectionStatus", "Goodies", TimeSpan.FromSeconds(5));
            Assert.That(modsStatus, Does.Contain("Goodies wall preview"), "Staging should tick the same Goodies preview selection.");

            // Toggling again removes it.
            InvokeElement(FindByAutomationId(window, "PatchInspectorStage_goodies_gallery_display_unlock"));
            WaitForNameContainsValue(window, "PatchBenchPlayerModsSelectionStatus", "No player mods on", TimeSpan.FromSeconds(5));

            // A hidden companion row refuses direct staging.
            AutomationElement stageCave = FindByAutomationId(window, "PatchInspectorStage_version_overlay_patched_format_cave_string");
            Assert.That(stageCave.IsEnabled, Is.False, "Hidden companion rows must not be stageable.");

            // Filtering works through the AppCore filter.
            SetTextBox(window, "PatchLabInspectorSearchBox", "widescreen");
            string filtered = WaitForNameContainsValue(window, "PatchLabInspectorStatus", "your filter.", TimeSpan.FromSeconds(10));
            Assert.That(filtered, Does.Contain("1 row matches"), $"Filter should narrow to the widescreen row: {filtered}");

            CaptureScreenshot(window, evidenceDir, "01-patch-lab-inspector.png");

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

    private static string WaitForNameContainsValue(Window window, string automationId, string text, TimeSpan timeout)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        bool matched = Retry.WhileFalse(
            () => (TryGetName(element) ?? string.Empty).Contains(text, StringComparison.OrdinalIgnoreCase),
            timeout).Success;
        Assert.That(matched, Is.True, $"Expected '{automationId}' name containing '{text}'.");
        return TryGetName(element) ?? string.Empty;
    }

    private static void SetTextBox(Window window, string automationId, string text)
    {
        AutomationElement box = FindByAutomationId(window, automationId);
        box.AsTextBox().Enter(text);
    }

    private static void InvokeElement(AutomationElement element)
    {
        element.AsButton().Invoke();
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
            // Evidence capture is best-effort; the behavioral asserts carry the proof.
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
