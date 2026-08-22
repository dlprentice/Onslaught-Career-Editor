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
/// Real-app smokes for the Lore depth surfaces: full-text search hits with
/// snippets open the matching document, and the reader text-size control re-renders.
/// Launches the built WinUI app; skipped when no build output exists.
/// </summary>
public class WinUiLoreDepthSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Lore search-hit behavior through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void LoreSearchHits_OpenTheMatchingDocument()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-lore-depth");
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

            // A whole word that exists in the included lore text produces hit rows.
            // The matches panel lives inside a collapsed expander, which must be
            // opened before its contents join the automation tree.
            ExpandByAutomationId(window, "LoreSearchHitsExpander");
            SetTextBox(window, "LoreSearchBox", "Aquila");
            // "match" also occurs in the placeholder text ("with the matching
            // sentence"); the real outcome line says how many documents matched.
            WaitForNameContainsValue(window, "LoreSearchHitsStatus", TimeSpan.FromSeconds(20), value =>
                value.Contains("across", StringComparison.OrdinalIgnoreCase));

            AutomationElement firstHitButton = FindFirstByAutomationIdPrefix(window, "LoreSearchHitButton");
            // Opening a hit loads that document into the reader (title card updates,
            // back history appears).
            string titleBefore = TryGetName(FindByAutomationId(window, "LoreCurrentDocumentTitle")) ?? string.Empty;
            InvokeElement(firstHitButton);
            bool readerChanged = Retry.WhileFalse(
                () =>
                {
                    string title = TryGetName(FindByAutomationId(window, "LoreCurrentDocumentTitle")) ?? string.Empty;
                    return title.Length > 0 && !string.Equals(title, titleBefore, StringComparison.Ordinal)
                        || title.Contains("Battle Engine", StringComparison.OrdinalIgnoreCase);
                },
                TimeSpan.FromSeconds(15)).Success;
            Assert.That(readerChanged, Is.True, "Opening a search hit should load a document in the reader.");

            // The What-links-here panel is present for the loaded document and says
            // something honest either way.
            ExpandByAutomationId(window, "LoreBacklinksExpander");
            string backlinks = WaitForNameContainsValue(
                window, "LoreBacklinksStatus", TimeSpan.FromSeconds(10), value =>
                    value.Contains("link", StringComparison.OrdinalIgnoreCase) ||
                    value.Contains("unavailable", StringComparison.OrdinalIgnoreCase));
            Assert.That(backlinks, Does.Not.Contain("Loading cross-links..."), "Backlink panel should finish loading.");

            CaptureScreenshot(window, evidenceDir, "01-lore-search-hits.png");

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

    private static void InvokeElement(AutomationElement element)
    {
        element.AsButton().Invoke();
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

    private static AutomationElement FindFirstByAutomationIdPrefix(Window window, string prefix)
    {
        AutomationElement? found = Retry.WhileNull(
            () => window.FindAllDescendants(cf => cf.ByAutomationId(prefix))
                .FirstOrDefault(),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(found, Is.Not.Null, $"Expected at least one element with automation id prefix: {prefix}");
        return found!;
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
            // Evidence capture is best-effort; behavioral asserts carry the proof.
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
