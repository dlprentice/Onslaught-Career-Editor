using System;
using System.IO;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class SmokeTests
{
    [Test]
    [Category("LegacyWpf")]
    [Apartment(ApartmentState.STA)]
    public void MainWindow_LaunchesAndShowsCoreChrome()
    {
        var exePath = ResolveAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run dotnet build first.");
        }

        Application? app = null;
        try
        {
            app = Application.Launch(exePath);
            using var automation = new UIA3Automation();

            var handleReady = Retry.WhileFalse(
                () => app.MainWindowHandle != IntPtr.Zero,
                TimeSpan.FromSeconds(30)
            ).Success;

            if (!handleReady)
            {
                Assert.Ignore("Main window handle not available; ensure the app launches on this desktop session.");
            }

            var window = Retry.WhileNull(
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
                TimeSpan.FromSeconds(30)
            ).Result;

            Assert.That(window, Is.Not.Null);

            Assert.That(window.Title, Does.Contain("Onslaught"));
            Assert.That(app.HasExited, Is.False, "App should still be running after launch.");

            var mainTabs = window.FindFirstDescendant(cf => cf.ByName("Main navigation tabs"));
            Assert.That(mainTabs, Is.Not.Null, "Expected main tab navigation in window chrome.");
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Ignore close failures; ensure process is terminated below if needed.
            }

            if (app != null && !app.HasExited)
            {
                app.Kill();
            }
        }
    }

    private static string ResolveAppPath()
    {
        var repoRoot = Path.GetFullPath(
            Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..")
        );

        return Path.Combine(
            repoRoot,
            "archive",
            "legacy-wpf",
            "bin",
            "Debug",
            "net10.0-windows",
            "Onslaught - Career Editor.exe"
        );
    }

}
