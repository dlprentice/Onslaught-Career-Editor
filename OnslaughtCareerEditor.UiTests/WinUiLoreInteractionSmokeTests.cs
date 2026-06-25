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

public class WinUiLoreInteractionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies Lore search/select/read behavior through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void LoreReader_SearchesSelectsAndShowsCurrentDocumentThroughUiAutomation()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-lore-reader-interaction", "2026-05-06");
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
            Assert.That(FindByAutomationId(window, "LoreDocumentTree").IsEnabled, Is.True, "Lore document tree should be enabled.");
            Assert.That(FindByAutomationId(window, "LoreSearchBox").IsEnabled, Is.True, "Lore search box should be enabled.");
            Assert.That(FindByAutomationId(window, "LoreReaderPanel").Name, Is.EqualTo("Lore document reader"));

            SetTextBox(window, "LoreSearchBox", "Battle Engine Tech");
            WaitForNameContains(window, "Filtered results for", TimeSpan.FromSeconds(10));

            AutomationElement techDocument = WaitForTreeItem(
                FindByAutomationId(window, "LoreDocumentTree"),
                "Battle Engine Tech",
                TimeSpan.FromSeconds(15));
            InvokeElement(techDocument);

            bool documentSelected = Retry.WhileFalse(
                () => string.Equals(
                    TryGetName(FindByAutomationId(window, "LoreCurrentDocumentTitle")),
                    "Battle Engine Tech",
                    StringComparison.Ordinal),
                TimeSpan.FromSeconds(15)).Success;
            Assert.That(documentSelected, Is.True, "Expected selecting the filtered tree row to update the visible Lore reader title.");

            string summary = TryGetName(FindByAutomationId(window, "LoreCurrentDocumentSummary")) ?? string.Empty;
            Assert.That(summary, Does.Contain("curated lore library"));
            Assert.That(summary, Does.Not.Contain(@":\"));
            Assert.That(summary, Does.Not.Contain(ResolveRepoRoot()));

            Assert.That(FindByAutomationId(window, "LoreBackButton").IsEnabled, Is.True, "Selecting a document from the library should create back history.");
            Assert.That(FindByAutomationId(window, "LoreOpenExternalButton").IsEnabled, Is.True, "A selected document should expose an external-open action.");

            string screenshotPath = Path.Combine(evidenceDir, "01-lore-reader-selected.png");
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

    private static AutomationElement WaitForTreeItem(AutomationElement treeRoot, string name, TimeSpan timeout)
    {
        AutomationElement? element = Retry.WhileNull(
            () => treeRoot.FindAllDescendants()
                .FirstOrDefault(candidate =>
                    candidate.ControlType == ControlType.TreeItem &&
                    string.Equals(TryGetName(candidate), name, StringComparison.OrdinalIgnoreCase)),
            timeout).Result;
        Assert.That(element, Is.Not.Null, $"Expected visible Lore tree item: {name}");
        return element!;
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

        element.Click();
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static void WaitForNameContains(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindAllDescendants()
                .Any(candidate => (TryGetName(candidate) ?? string.Empty).Contains(text, StringComparison.OrdinalIgnoreCase)),
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible UIA name containing: {text}");
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
