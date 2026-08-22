using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Real-app smoke of the Lore search-to-section journey: typing a word that only
/// occurs deep inside one document lists hits that name the section they fall
/// under, and opening such a hit lands the reader scrolled at that section
/// instead of at the top of the document.
/// </summary>
public class WinUiLoreSearchSectionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Lore search hits open at their section through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void LoreSearchHit_OpensTheReaderAtTheMatchedSection()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-lore-search-section");
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

            // "Localization" appears many documents deep inside Development
            // History - far past its first headings - so a hit for it must carry
            // a real section target rather than falling back to the top.
            SetTextBox(window, "LoreSearchBox", "localization");

            // The hits panel is collapsed until there is something to show; the
            // census smokes use the same expand step before reading their lists.
            ExpandByAutomationId(window, "LoreSearchHitsExpander");

            // Wait for the bound status sentence first: it proves the models are
            // on screen before scanning for the row itself.
            string hitsStatus = string.Empty;
            bool hitsReady = Retry.WhileFalse(
                () =>
                {
                    hitsStatus = TryGetName(FindByAutomationId(window, "LoreSearchHitsStatus")) ?? string.Empty;
                    return hitsStatus.Contains("matches across", StringComparison.OrdinalIgnoreCase);
                },
                TimeSpan.FromSeconds(15)).Success;
            Assert.That(hitsReady, Is.True, $"Expected the hits status to report matches, got: {hitsStatus}");

            const string expectedSectionFragment = "in section 3. Planning Localization";
            AutomationElement? developmentHistoryHit;
            try
            {
                developmentHistoryHit = Retry.WhileNull(
                    () => window.FindAllDescendants()
                        .FirstOrDefault(candidate =>
                            candidate.ControlType == ControlType.Button &&
                            (TryGetName(candidate) ?? string.Empty).Contains("Development History", StringComparison.OrdinalIgnoreCase) &&
                            (TryGetName(candidate) ?? string.Empty).Contains(expectedSectionFragment, StringComparison.Ordinal)),
                    TimeSpan.FromSeconds(15)).Result;
            }
            catch
            {
                // Leave visual evidence of what the pane actually looked like.
                window.Focus();
                Thread.Sleep(500);
                window.CaptureToFile(Path.Combine(evidenceDir, "00-lore-smoke-before-hit-assert.png"));
                throw;
            }
            Assert.That(developmentHistoryHit, Is.Not.Null,
                $"Expected a search hit for Development History named as targeting '{expectedSectionFragment}'.");

            InvokeElement(developmentHistoryHit!);

            bool documentOpened = Retry.WhileFalse(
                () => string.Equals(
                    TryGetName(FindByAutomationId(window, "LoreCurrentDocumentTitle")),
                    "Development History",
                    StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(15)).Success;
            Assert.That(documentOpened, Is.True, "Opening the search hit should show Development History in the reader.");

            // Disk-independent but decisive: the reader must actually be scrolled
            // down at the matched section, not sitting at the top of the page.
            AutomationElement scrollViewer = FindByAutomationId(window, "LoreReaderScrollViewer");
            bool scrolledDown = Retry.WhileFalse(
                () =>
                {
                    try
                    {
                        return scrollViewer.Patterns.Scroll.IsSupported
                            && scrollViewer.Patterns.Scroll.Pattern.VerticalScrollPercent > 5.0;
                    }
                    catch
                    {
                        return false;
                    }
                },
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(scrolledDown, Is.True,
                "Opening a section-targeted search hit should scroll the reader down from the document top.");

            string screenshotPath = Path.Combine(evidenceDir, "01-lore-search-section.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Lore reader screenshot should not be empty.");
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

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        textBox.Focus();
        textBox.Text = text;
        bool valueApplied = Retry.WhileFalse(
            () => string.Equals(textBox.Text, text, StringComparison.Ordinal),
            TimeSpan.FromSeconds(5)).Success;
        Assert.That(valueApplied, Is.True, $"Expected {automationId} to accept the requested text value.");
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

    private static void InvokeElement(AutomationElement element)
    {
        if (element.Patterns.ScrollItem.IsSupported)
        {
            element.Patterns.ScrollItem.Pattern.ScrollIntoView();
        }

        if (element.Patterns.SelectionItem.IsSupported)
        {
            element.Patterns.SelectionItem.Pattern.Select();
        }

        element.Focus();
        Thread.Sleep(250);

        if (element.Patterns.Invoke.IsSupported)
        {
            element.Patterns.Invoke.Pattern.Invoke();
        }
        else
        {
            element.Click();
        }
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
