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
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Drives the real app and checks that a career sitting inside a safe copy can actually be found
/// and brought out.
///
/// The static suite pins the markup and the shape of the code; neither of those notices if the
/// pickers come up empty in front of a person. This one seeds an isolated app-data root with a
/// safe copy holding one career, launches the shipped executable against it, and reads what the
/// Save Lab shows.
/// </summary>
[NonParallelizable]
public class WinUiSaveRescueInteractionSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies the Save Lab finds careers inside a seeded safe copy.")]
    [Apartment(ApartmentState.STA)]
    public void SaveLab_FindsTheCareersInsideASafeCopyAndOffersToKeepThem()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-save-rescue-interaction");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        SeedSafeCopy(appDataDir, "seeded-copy", "Maladim.bes");

        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "saves";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            FindByAutomationId(window, "SaveEditorTabButton").AsButton().Invoke();
            Thread.Sleep(750);

            Assert.That(
                TryGetName(FindByAutomationId(window, "SaveRescueHeading")),
                Is.EqualTo("Bring a career out of a copy"));

            // Read the selection rather than enumerating Items: asking UIA for a ComboBox's items
            // expands the popup, which then sits over the card in the capture below.
            ComboBox copies = FindByAutomationId(window, "SaveRescueCopyComboBox").AsComboBox();
            ComboBox careers = FindByAutomationId(window, "SaveRescueSaveComboBox").AsComboBox();
            Assert.That(
                TryGetName(copies.SelectedItem),
                Does.Contain("seeded-copy"),
                "The copy picker must find the copy on disk and select it.");
            Assert.That(
                TryGetName(careers.SelectedItem),
                Does.Contain("Maladim"),
                "The career picker must find the save inside the copy's savegames folder.");

            string summary = TryGetName(FindByAutomationId(window, "SaveRescueSelection")) ?? string.Empty;
            Assert.That(summary, Does.Contain("Maladim"));
            Assert.That(
                summary,
                Does.Contain("does not take it away"),
                "A person has to be able to tell, before pressing it, that the copy stays playable.");

            Assert.That(
                FindByAutomationId(window, "SaveRescueButton").AsButton().IsEnabled,
                Is.True,
                "With a copy and a career selected there is something to do, so the button must be live.");

            // The card sits below the fold on a normal window, so a capture that has not scrolled
            // to it is a screenshot of everything except the thing under test.
            // The heading, not the card Border - a Border carries no automation peer, so it never
            // appears in the tree even though its AutomationId is in the markup.
            ScrollIntoView(FindByAutomationId(window, "SaveRescueButton"));

            string screenshotPath = Path.Combine(evidenceDir, "01-save-rescue-card.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000));
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to the kill below.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    /// <summary>
    /// A safe copy carrying the generated manifest and one career. The location comes from
    /// <see cref="AppConfig"/> with the same override the child process gets, so this cannot drift
    /// into seeding a folder the app never looks at.
    /// </summary>
    private static void SeedSafeCopy(string appDataRoot, string copyName, string saveFileName)
    {
        string? previous = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
        try
        {
            Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", appDataRoot);
            string copy = Path.Combine(AppConfig.GetGameProfilesDir(), copyName);
            Directory.CreateDirectory(Path.Combine(copy, "savegames"));
            File.WriteAllText(
                Path.Combine(copy, GameProfilePreflightService.ProfileManifestFileName),
                "{\"schemaVersion\":\"" + GameProfilePreflightService.SchemaVersion + "\"}");
            File.WriteAllText(Path.Combine(copy, "savegames", saveFileName), "career-save-fixture");
        }
        finally
        {
            Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", previous);
        }
    }

    private static string PrepareIsolatedAppData(string evidenceDir)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        if (Directory.Exists(appDataDir))
        {
            Directory.Delete(appDataDir, recursive: true);
        }

        Directory.CreateDirectory(appDataDir);
        return appDataDir;
    }

    private static void ScrollIntoView(AutomationElement element)
    {
        try
        {
            element.Patterns.ScrollItem.PatternOrDefault?.ScrollIntoView();
            Thread.Sleep(500);
        }
        catch
        {
            // A host that will not scroll still leaves every assertion above intact; only the
            // screenshot is worse.
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
            TimeSpan.FromSeconds(20),
            TimeSpan.FromMilliseconds(250)).Result;

        Assert.That(element, Is.Not.Null, $"Expected an element with AutomationId '{automationId}'.");
        return element!;
    }

    private static Window WaitForMainWindow(Application app, UIA3Automation automation)
    {
        Window? window = Retry.WhileNull(
            () => app.GetMainWindow(automation, TimeSpan.FromSeconds(5)),
            TimeSpan.FromSeconds(60),
            TimeSpan.FromMilliseconds(500)).Result;

        Assert.That(window, Is.Not.Null, "The WinUI main window did not appear.");
        return window!;
    }

    private static string ResolveWinUiAppPath()
    {
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
        DirectoryInfo? directory = new(TestContext.CurrentContext.TestDirectory);
        while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "package.json")))
        {
            directory = directory.Parent;
        }

        Assert.That(directory, Is.Not.Null, "Could not find the repository root.");
        return directory!.FullName;
    }
}
