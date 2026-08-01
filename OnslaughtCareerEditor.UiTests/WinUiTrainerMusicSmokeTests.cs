using System;
using System.Diagnostics;
using System.IO;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Turns the trainer music on in the real app and checks it does not take the app with it.
///
/// The synth is covered by deterministic AppCore tests, and the markup by the static suite.
/// Neither touches the part that can actually fail in front of a person: opening an audio device.
/// A machine with no output, or one that will not take 22 kHz mono, is an ordinary thing - the
/// toggle has to come back off and say so rather than throwing out of an event handler, which in
/// WinUI takes the process down.
/// </summary>
[NonParallelizable]
public class WinUiTrainerMusicSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and toggles the trainer music on and off.")]
    [Apartment(ApartmentState.STA)]
    public void TrainerMusic_TogglesOnAndOffWithoutTakingTheAppDown()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-trainer-music");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        if (Directory.Exists(appDataDir))
            Directory.Delete(appDataDir, recursive: true);
        Directory.CreateDirectory(appDataDir);

        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "cheats";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            AutomationElement toggleElement = FindByAutomationId(window, "TrainerMusicToggle");

            // The music is deliberately not gated on being attached to a game: it is a mood, not a
            // capability, and making somebody launch a copy to hear it would be silly.
            Assert.That(toggleElement.IsEnabled, Is.True, "The music toggle should not need a running game.");

            Toggle(toggleElement);
            Thread.Sleep(1_500);

            Assert.That(app.HasExited, Is.False, "Turning the music on must not take the app down.");

            // Either it is playing, or the device refused and the app said so and put the switch
            // back. Both are fine; a crash or a silently-stuck switch is not.
            AutomationElement? statusElement = window.FindFirstDescendant(cf => cf.ByAutomationId("TrainerMusicStatus"));
            bool refused = statusElement is not null && !string.IsNullOrWhiteSpace(TryGetName(statusElement));
            if (refused)
            {
                Assert.That(
                    TryGetName(statusElement),
                    Does.Contain("audio device"),
                    "A refusal has to explain itself.");
            }

            string screenshotPath = Path.Combine(evidenceDir, "01-trainer-music.png");
            ScrollIntoView(toggleElement);
            window.Focus();
            Thread.Sleep(800);
            window.CaptureToFile(screenshotPath);
            Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000));

            Toggle(toggleElement);
            Thread.Sleep(800);
            Assert.That(app.HasExited, Is.False, "Turning it off must not take the app down either.");
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

    /// <summary>A ToggleSwitch exposes the Toggle pattern; fall back to a click if it does not.</summary>
    private static void Toggle(AutomationElement element)
    {
        var pattern = element.Patterns.Toggle.PatternOrDefault;
        if (pattern is not null)
        {
            pattern.Toggle();
            return;
        }

        element.Click();
    }

    private static void ScrollIntoView(AutomationElement element)
    {
        try
        {
            element.Patterns.ScrollItem.PatternOrDefault?.ScrollIntoView();
            Thread.Sleep(400);
        }
        catch
        {
            // Only the screenshot is worse.
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
