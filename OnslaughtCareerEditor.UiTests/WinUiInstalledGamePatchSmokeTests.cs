using System;
using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Drives the real app and checks that the installed-game section reports the state of the game it
/// is pointed at, and offers only what that state allows.
///
/// The static suite pins the words and the shape of the code. It cannot tell whether the buttons
/// come up dead in front of a person, and the failure that matters here - offering to patch
/// something that cannot be put back - is exactly an enablement question.
///
/// The app is pointed at a throwaway folder shaped like an install. No real installation is
/// involved: the clean specimen is copied out, never written to.
/// </summary>
[NonParallelizable]
public class WinUiInstalledGamePatchSmokeTests
{
    private const string KnownCleanSha256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app against a throwaway install and reads the installed-game section.")]
    [Apartment(ApartmentState.STA)]
    public void InstalledGameSection_OffersOnlyWhatTheGamesStateAllows()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-installed-game-patch");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);

        string fakeInstall = Path.Combine(evidenceDir, "fake-install");
        if (Directory.Exists(fakeInstall))
            Directory.Delete(fakeInstall, recursive: true);
        Directory.CreateDirectory(Path.Combine(fakeInstall, "data"));

        string? specimen = FindCleanSpecimen();
        if (specimen is null)
            Assert.Ignore("This machine has no clean retail specimen to build a throwaway install from.");

        // A game that has been changed with no original beside it: the state where the app must
        // refuse to offer a patch, because it could not put anything back.
        byte[] modified = File.ReadAllBytes(specimen!);
        modified[0x400] ^= 0xFF;
        File.WriteAllBytes(Path.Combine(fakeInstall, "BEA.exe"), modified);

        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_GAME_DIR_CANDIDATES"] = fakeInstall;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "binary";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            Assert.That(
                TryGetName(FindByAutomationId(window, "PatchBenchInstalledGameTitle")),
                Is.EqualTo("Or change the game you installed"));

            string status = TryGetName(FindByAutomationId(window, "PatchBenchInstalledGameStatus")) ?? string.Empty;
            Assert.That(
                status,
                Does.Contain("will not copy a changed file and call it the original"),
                $"The section must report the unrescuable state. It said: {status}");

            Assert.That(
                FindByAutomationId(window, "PatchBenchInstalledGamePatchButton").AsButton().IsEnabled,
                Is.False,
                "Patching must not be offered when there is nothing to go back to.");
            Assert.That(
                FindByAutomationId(window, "PatchBenchInstalledGameRestoreButton").AsButton().IsEnabled,
                Is.False,
                "Put my game back must not be offered when there is no original.");

            // And the scope of Restore is on screen rather than behind a disclosure.
            Assert.That(
                TryGetName(FindByAutomationId(window, "PatchBenchInstalledGameRestoreScope")),
                Does.Contain("every patch at once, not the last one"));

            ScrollIntoView(FindByAutomationId(window, "PatchBenchInstalledGamePatchButton"));
            string screenshotPath = Path.Combine(evidenceDir, "01-installed-game-section.png");
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(screenshotPath);
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000));

            // Nothing about drawing that page may have written to the throwaway install.
            Assert.That(
                File.Exists(Path.Combine(fakeInstall, "BEA.exe.original.backup")),
                Is.False,
                "Reading the state must never take a backup as a side effect.");
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

    private static string? FindCleanSpecimen()
    {
        string repoRoot = ResolveRepoRoot();
        foreach (string candidate in new[]
                 {
                     Path.Combine(repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe.original.backup"),
                     Path.Combine(repoRoot, "local-lab", "safe-copy-bea-pristine", "BEA.exe"),
                 })
        {
            try
            {
                if (!File.Exists(candidate) || new FileInfo(candidate).Length != 2_506_752)
                    continue;

                using FileStream stream = File.OpenRead(candidate);
                if (string.Equals(
                        Convert.ToHexString(SHA256.HashData(stream)),
                        KnownCleanSha256,
                        StringComparison.OrdinalIgnoreCase))
                {
                    return candidate;
                }
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // Try the next candidate.
            }
        }

        return null;
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
