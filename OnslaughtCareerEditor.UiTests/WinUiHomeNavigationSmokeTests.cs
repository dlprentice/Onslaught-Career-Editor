using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Input;
using FlaUI.Core.Tools;
using FlaUI.Core.WindowsAPI;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[NonParallelizable]
public class WinUiHomeNavigationSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches WinUI on Home and verifies each Home task button reaches its destination page.")]
    [Apartment(ApartmentState.STA)]
    [TestCase("HomeOpenSaveLabButton", "SaveAnalyzerFilePath")]
    [TestCase("HomeOpenMediaButton", "MediaAudioTabButton")]
    [TestCase("HomeOpenLoreButton", "LoreSearchBox")]
    [TestCase("HomeOpenPatchBenchButton", "PatchBenchScrollViewer")]
    [TestCase("HomeOpenAssetLibraryButton", "AssetSearchBox")]
    [TestCase("HomeOpenAboutButton", "AboutPageTitle")]
    [TestCase("HomeReviewSettingsButton", "SettingsPageScrollViewer")]
    public void Home_TaskButton_NavigatesToExpectedDestination(string homeButtonAutomationId, string destinationAutomationId)
    {
        using HomeNavigationSession session = LaunchHomeSession();
        WaitForText(session.Window, "Start Here", TimeSpan.FromSeconds(20));
        AutomationElement homeButton = FindByAutomationId(session.Window, homeButtonAutomationId);
        ScrollIntoView(homeButton);
        bool destinationReady = ActivateAndWait(
            session.Window,
            homeButton,
            () => TryFindByAutomationId(session.Window, destinationAutomationId) is not null);
        Assert.That(destinationReady, Is.True, $"Expected destination marker {destinationAutomationId} after clicking {homeButtonAutomationId}.");

        if (string.Equals(homeButtonAutomationId, "HomeOpenMediaButton", StringComparison.Ordinal))
        {
            Assert.That(
                Retry.WhileFalse(
                    () => string.Equals(TryGetFocusedAutomationId(session.Automation), "MediaAudioTabButton", StringComparison.Ordinal),
                    TimeSpan.FromSeconds(5)).Success,
                Is.True,
                "Home-to-Media navigation should focus the selected Audio tab.");
        }
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches a true no-detection first run and verifies setup hierarchy plus destination focus.")]
    [Apartment(ApartmentState.STA)]
    public void Home_TrueFirstRun_PrioritizesSetupWithoutBlockingManualSaveLab()
    {
        using HomeNavigationSession session = LaunchHomeSession();
        Window window = session.Window;
        WaitForText(window, "Start Here", TimeSpan.FromSeconds(20));

        AutomationElement setupAction = FindByAutomationId(window, "HomeSetupActionButton");
        AutomationElement saveLabAction = FindByAutomationId(window, "HomeOpenSaveLabButton");
        Assert.That(setupAction.Name, Is.EqualTo("Choose game folder"));
        Assert.That(setupAction.IsEnabled, Is.True);
        Assert.That(saveLabAction.IsEnabled, Is.True, "Manual Save Lab browsing remains available before game-folder setup.");
        Assert.That(setupAction.BoundingRectangle.Top, Is.LessThan(saveLabAction.BoundingRectangle.Top), "The setup action should appear before the task grid on a true first run.");
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(TryGetFocusedAutomationId(session.Automation), "HomeSetupActionButton", StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "True first run should place arrival focus on the visible setup action.");
        Assert.That(FindByAutomationId(window, "AppStatusText").Name, Does.Contain("Home: choose a task"));

        string screenshotPath = Path.Combine(session.EvidenceDir, "00-home-true-first-run.png");
        window.Focus();
        Thread.Sleep(750);
        window.CaptureToFile(screenshotPath);
        Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
        Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "First-run screenshot should not be empty.");

        bool settingsReady = ActivateAndWait(
            window,
            setupAction,
            () => TryFindByAutomationId(window, "SettingsBrowseGameDirectoryButton") is not null);
        Assert.That(settingsReady, Is.True, "Setup action should open the game-folder controls in Settings.");
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(TryGetFocusedAutomationId(session.Automation), "SettingsBrowseGameDirectoryButton", StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "Setup navigation should move focus once to the explicit game-folder browse action.");
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches Home with a saved incomplete folder and verifies the review state remains truthful.")]
    [Apartment(ApartmentState.STA)]
    public void Home_InvalidConfiguredFolder_RequiresReviewWithoutBlockingManualSaveLab()
    {
        string invalidGameDirectory = Path.Combine(
            ResolveRepoRoot(),
            "subagents",
            "winui-home-navigation",
            "2026-05-27",
            "fixtures",
            "invalid-game");
        Directory.CreateDirectory(invalidGameDirectory);

        using HomeNavigationSession session = LaunchHomeSession(invalidGameDirectory, "invalid");
        Window window = session.Window;
        WaitForText(window, "Review your game folder", TimeSpan.FromSeconds(20));

        Assert.That(FindByAutomationId(window, "HomeSetupActionButton").Name, Is.EqualTo("Review game folder"));
        Assert.That(FindByAutomationId(window, "HomeOpenSaveLabButton").IsEnabled, Is.True);
        Assert.That(FindByAutomationId(window, "HomeSetupTitle").Name, Is.EqualTo("Setup needs attention"));
        Assert.That(FindByAutomationId(window, "ShellGameDirectoryStatus").Name, Is.EqualTo("Game folder: Needs review"));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches with a temporarily unavailable configured folder and verifies unrelated settings do not erase it.")]
    [Apartment(ApartmentState.STA)]
    public void Settings_MissingConfiguredFolder_PreservesPathWhenMediaPreferencesChange()
    {
        string missingGameDirectory = Path.Combine(
            ResolveRepoRoot(),
            "subagents",
            "winui-home-navigation",
            "2026-05-27",
            "fixtures",
            $"missing-game-{Guid.NewGuid():N}");
        Assert.That(Directory.Exists(missingGameDirectory), Is.False, "The regression fixture must represent an unavailable folder.");

        using HomeNavigationSession session = LaunchHomeSession(missingGameDirectory, "missing-configured-folder");
        Window window = session.Window;
        WaitForText(window, "Review your game folder", TimeSpan.FromSeconds(20));

        AutomationElement reviewAction = FindByAutomationId(window, "HomeSetupActionButton");
        Assert.That(
            ActivateAndWait(
                window,
                reviewAction,
                () => TryFindByAutomationId(window, "SettingsPageScrollViewer") is not null),
            Is.True,
            "Review action should open Settings for the remembered unavailable folder.");

        Assert.That(
            FindByAutomationId(window, "SettingsGameDirectoryStatus").Name,
            Is.EqualTo("Directory does not exist."));
        Assert.That(
            FindByAutomationId(window, "SettingsGameDirectorySummary").Name,
            Is.EqualTo(Path.GetFileName(missingGameDirectory)));

        ToggleByAutomationId(window, "SettingsAllowBackgroundAudioToggle");
        Assert.That(
            Retry.WhileFalse(
                () => ConfigStoresGameDirectoryAndAudioPreference(
                    session.ConfigPath,
                    missingGameDirectory,
                    expectedAllowBackgroundAudio: false),
                TimeSpan.FromSeconds(10)).Success,
            Is.True,
            "Saving an unrelated media preference must preserve the unavailable configured path.");
        Assert.That(FindByAutomationId(window, "ShellGameDirectoryStatus").Name, Is.EqualTo("Game folder: Needs review"));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches Home with a synthetic full-install shape and verifies ready state and arrival focus.")]
    [Apartment(ApartmentState.STA)]
    public void Home_ReadyConfiguredFolder_HidesSetupPromptAndFocusesManualSaveLab()
    {
        string readyGameDirectory = Path.Combine(
            ResolveRepoRoot(),
            "subagents",
            "winui-home-navigation",
            "2026-05-27",
            "fixtures",
            "full-game");
        Directory.CreateDirectory(Path.Combine(readyGameDirectory, "data"));
        File.WriteAllBytes(Path.Combine(readyGameDirectory, "BEA.exe"), new byte[] { 0 });

        using HomeNavigationSession session = LaunchHomeSession(readyGameDirectory, "ready");
        Window window = session.Window;
        WaitForText(window, "Game directory configured: full-game.", TimeSpan.FromSeconds(20));

        Assert.That(FindByAutomationId(window, "HomeSetupTitle").Name, Is.EqualTo("Setup"));
        Assert.That(FindByAutomationId(window, "HomeOpenSaveLabButton").IsEnabled, Is.True);
        Assert.That(FindByAutomationId(window, "ShellGameDirectoryStatus").Name, Is.EqualTo("Game folder: full-game"));
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(TryGetFocusedAutomationId(session.Automation), "HomeOpenSaveLabButton", StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True,
            "A ready Home arrival should focus the first usable task instead of the closed setup prompt.");
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches WinUI on Home and verifies Game Options deep-link navigation.")]
    [Apartment(ApartmentState.STA)]
    public void Home_OpenConfigurationEditorButton_ShowsConfigurationEditorTab()
    {
        using HomeNavigationSession session = LaunchHomeSession();
        Window window = session.Window;

        WaitForText(window, "Start Here", TimeSpan.FromSeconds(20));
        AutomationElement deepLinkButton = FindByAutomationId(window, "HomeOpenConfigurationEditorButton");
        ScrollIntoView(deepLinkButton);

        bool configurationReady = ActivateAndWait(
            window,
            deepLinkButton,
            () => TryFindByAutomationId(window, "ConfigurationInputFile") is not null
                && TryFindByAutomationId(window, "ConfigurationEditorScrollViewer") is not null
                && TryFindByAutomationId(window, "ConfigurationStatusInfo") is not null);
        Assert.That(configurationReady, Is.True, "Expected Game Options inputs after Home deep-link.");

        bool analyzerHidden = Retry.WhileFalse(
            () => TryFindByAutomationId(window, "SaveAnalyzerFilePath") is null,
            TimeSpan.FromSeconds(5)).Success;
        Assert.That(analyzerHidden, Is.True, "Expected Save Analyzer tab content hidden after Game Options deep-link.");

        string screenshotPath = Path.Combine(session.EvidenceDir, "01-home-configuration-editor-deeplink.png");
        window.Focus();
        Thread.Sleep(1_000);
        window.CaptureToFile(screenshotPath);
        Assert.That(File.Exists(screenshotPath), Is.True, $"Expected screenshot: {screenshotPath}");
        Assert.That(new FileInfo(screenshotPath).Length, Is.GreaterThan(10_000), "Deep-link screenshot should not be empty.");
    }

    private sealed class HomeNavigationSession : IDisposable
    {
        public HomeNavigationSession(Application app, UIA3Automation automation, Window window, string evidenceDir, string configPath)
        {
            App = app;
            Automation = automation;
            Window = window;
            EvidenceDir = evidenceDir;
            ConfigPath = configPath;
        }

        public Application App { get; }

        public UIA3Automation Automation { get; }

        public Window Window { get; }

        public string EvidenceDir { get; }

        public string ConfigPath { get; }

        public void Dispose()
        {
            Automation.Dispose();
            try
            {
                App.Close();
            }
            catch
            {
                // Fall through to process termination below.
            }

            if (!App.HasExited)
            {
                App.Kill();
            }
        }
    }

    private static HomeNavigationSession LaunchHomeSession(string? gameDirectory = null, string stateName = "unset")
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-home-navigation", "2026-05-27");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir, gameDirectory, stateName);
        string configPath = Path.Combine(appDataDir, "OnslaughtCareerEditor", "config.json");
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "home";
        startInfo.Environment["ONSLAUGHT_GAME_DIR_CANDIDATES"] = string.Empty;
        startInfo.Environment["ONSLAUGHT_STEAM_ROOT_CANDIDATES"] = Path.Combine(appDataDir, "empty-steam-root");

        Application app = Application.Launch(startInfo);
        var automation = new UIA3Automation();
        Window window = WaitForMainWindow(app, automation);
        return new HomeNavigationSession(app, automation, window, evidenceDir, configPath);
    }

    private static void ToggleByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        window.Focus();
        if (element.Patterns.Toggle.IsSupported)
        {
            element.Patterns.Toggle.Pattern.Toggle();
        }
        else
        {
            element.Click();
        }
    }

    private static bool ConfigStoresGameDirectoryAndAudioPreference(
        string configPath,
        string expectedGameDirectory,
        bool expectedAllowBackgroundAudio)
    {
        try
        {
            using JsonDocument document = JsonDocument.Parse(File.ReadAllText(configPath));
            JsonElement root = document.RootElement;
            return root.TryGetProperty("gameDirectory", out JsonElement gameDirectory) &&
                string.Equals(gameDirectory.GetString(), expectedGameDirectory, StringComparison.Ordinal) &&
                root.TryGetProperty("allowBackgroundAudio", out JsonElement allowBackgroundAudio) &&
                allowBackgroundAudio.GetBoolean() == expectedAllowBackgroundAudio;
        }
        catch (IOException)
        {
            return false;
        }
        catch (JsonException)
        {
            return false;
        }
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static void ScrollIntoView(AutomationElement element)
    {
        try
        {
            if (element.Patterns.ScrollItem.IsSupported)
            {
                element.Patterns.ScrollItem.Pattern.ScrollIntoView();
            }
        }
        catch
        {
            // Best-effort positioning only.
        }
    }

    private static bool ActivateAndWait(Window window, AutomationElement element, Func<bool> isReady)
    {
        window.Focus();
        Thread.Sleep(200);

        try
        {
            if (element.Patterns.Invoke.IsSupported)
            {
                element.Patterns.Invoke.Pattern.Invoke();
                if (WaitUntilReady(isReady))
                {
                    return true;
                }
            }
        }
        catch (MissingMethodException)
        {
            // Some packaged WinUI/FlaUI invoke-provider paths throw here even though the button is clickable.
        }

        try
        {
            element.Focus();
            Keyboard.Press(VirtualKeyShort.RETURN);
            if (WaitUntilReady(isReady))
            {
                return true;
            }
        }
        catch
        {
            // Fall back to pointer activation below.
        }

        try
        {
            if (element.TryGetClickablePoint(out Point clickablePoint))
            {
                Mouse.Click(clickablePoint, MouseButton.Left);
                if (WaitUntilReady(isReady))
                {
                    return true;
                }
            }
        }
        catch
        {
            // Fall back to the element center below.
        }

        Rectangle bounds = element.BoundingRectangle;
        Mouse.Click(new Point(bounds.Left + bounds.Width / 2, bounds.Top + bounds.Height / 2), MouseButton.Left);
        return WaitUntilReady(isReady);
    }

    private static bool WaitUntilReady(Func<bool> isReady)
    {
        return Retry.WhileFalse(isReady, TimeSpan.FromSeconds(15)).Success;
    }

    private static AutomationElement? TryFindByAutomationId(Window window, string automationId)
    {
        try
        {
            return window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
        }
        catch
        {
            return null;
        }
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => TryFindByAutomationId(window, automationId),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
    }

    private static string? TryGetFocusedAutomationId(UIA3Automation automation)
    {
        try
        {
            return automation.FocusedElement()?.AutomationId;
        }
        catch
        {
            return null;
        }
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

    private static string PrepareIsolatedAppData(string evidenceDir, string? gameDirectory, string stateName)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata", stateName);
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        string gameDirectoryJson = string.IsNullOrWhiteSpace(gameDirectory)
            ? "null"
            : JsonSerializer.Serialize(gameDirectory);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            $$"""
            {
              "gameDirectory": {{gameDirectoryJson}},
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 820,
              "lastTab": 0,
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
