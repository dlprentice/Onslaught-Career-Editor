using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Drives the real app and checks that safe copies on disk actually appear in the manager.
///
/// This is the failure the static suite cannot see. The list is the precondition for the delete
/// being offered at all, and a list that silently comes up empty is indistinguishable, from the
/// outside, from having no copies - which is exactly the state that made people give up and leave
/// several gigabytes in Roaming AppData.
/// </summary>
[NonParallelizable]
public class WinUiSafeCopyManagerSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app against seeded safe copies and reads the manager list.")]
    [Apartment(ApartmentState.STA)]
    public void SafeCopyManager_ShowsTheCopiesOnDiskWithTheirSizeAndCareers()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-safe-copy-manager");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);

        SeedCopy(appDataDir, "kept-career", payloadBytes: 3 * 1024 * 1024, careers: 1);
        SeedCopy(appDataDir, "empty-copy", payloadBytes: 1 * 1024 * 1024, careers: 0);

        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
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

            Assert.That(
                TryGetName(FindByAutomationId(window, "SafeCopyManagerTitle")),
                Is.EqualTo("Your safe copies"));

            string total = TryGetName(FindByAutomationId(window, "SafeCopyManagerTotal")) ?? string.Empty;
            Assert.That(total, Does.Contain("2 safe copies"), $"The total line said: {total}");
            Assert.That(total, Does.Contain("1 career"), "The careers at risk travel with the size.");

            // Addressed through the row's buttons rather than its Border: a Border carries no
            // automation peer, so its AutomationId never reaches the tree even though it is in the
            // markup. The delete on each row must also name its own copy - a screen reader user
            // hearing three identical "Delete" buttons cannot tell them apart.
            Assert.That(
                TryGetName(FindByAutomationId(window, "SafeCopyRowDelete_kept_career")),
                Is.EqualTo("Delete kept-career"));
            Assert.That(
                TryGetName(FindByAutomationId(window, "SafeCopyRowDelete_empty_copy")),
                Is.EqualTo("Delete empty-copy"));

            ScrollIntoView(FindByAutomationId(window, "SafeCopyRowDelete_kept_career"));
            string screenshotPath = Path.Combine(evidenceDir, "01-safe-copy-manager.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000));

            // Listing must never be a mutation: the seeded careers are still there.
            Assert.That(
                File.Exists(Path.Combine(appDataDir, "OnslaughtCareerEditor", "GameProfiles", "kept-career", "savegames", "Career1.bes")),
                Is.True);
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
                app.Kill();
        }
    }

    private static void SeedCopy(string appDataRoot, string name, int payloadBytes, int careers)
    {
        string? previous = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
        try
        {
            Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", appDataRoot);
            string copy = Path.Combine(AppConfig.GetGameProfilesDir(), name);
            Directory.CreateDirectory(Path.Combine(copy, "savegames"));
            File.WriteAllText(
                Path.Combine(copy, GameProfilePreflightService.ProfileManifestFileName),
                "{\"schemaVersion\":\"" + GameProfilePreflightService.SchemaVersion + "\"}");
            File.WriteAllBytes(Path.Combine(copy, "payload.bin"), new byte[payloadBytes]);

            for (int index = 1; index <= careers; index++)
                File.WriteAllText(Path.Combine(copy, "savegames", $"Career{index}.bes"), "career-save-fixture");
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
            Directory.Delete(appDataDir, recursive: true);

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
            // Only the screenshot is worse; every assertion above still holds.
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
            directory = directory.Parent;

        Assert.That(directory, Is.Not.Null, "Could not find the repository root.");
        return directory!.FullName;
    }
}
