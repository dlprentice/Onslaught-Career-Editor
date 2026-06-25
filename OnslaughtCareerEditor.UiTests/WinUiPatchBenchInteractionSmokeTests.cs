using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiPatchBenchInteractionSmokeTests
{
    private const int SwRestore = 9;
    private const uint SwpShowWindow = 0x0040;
    private static readonly IntPtr HwndTop = IntPtr.Zero;

    [Test]
    [Category("WinUIRuntime")]
    [Apartment(ApartmentState.STA)]
    public void PatchBench_ProfileAndMenuColorChoices_UpdateSelectedStateThroughUia()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(Path.GetTempPath(), "onslaught-patch-choice-state-20260625");
        if (Directory.Exists(evidenceDir))
        {
            Directory.Delete(evidenceDir, recursive: true);
        }

        Directory.CreateDirectory(evidenceDir);
        string fakeGameDir = Path.Combine(evidenceDir, "fake-game");
        Directory.CreateDirectory(fakeGameDir);
        File.WriteAllBytes(Path.Combine(fakeGameDir, "BEA.exe"), new byte[] { 0 });
        string appDataDir = PrepareIsolatedAppData(evidenceDir, fakeGameDir);
        Application? app = null;
        try
        {
            var startInfo = new ProcessStartInfo(exePath)
            {
                WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
            };
            startInfo.Environment["APPDATA"] = appDataDir;
            startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "binary";

            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Safe game copy", TimeSpan.FromSeconds(20));
            AssertAutomationNameContains(window, "PatchBenchWindowedPresetButton", "Selected: Compatibility Copy profile");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Compatibility Copy");

            InvokeByAutomationId(window, "PatchBenchStableDefaultsButton");
            AssertAutomationNameContains(window, "PatchBenchStableDefaultsButton", "Selected: Windowed and Graphics Defaults profile");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Windowed + Graphics Defaults");

            SelectComboBoxItem(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");
            InvokeByAutomationId(window, "PatchBenchEnhancedPreviewProfileButton");
            AssertAutomationNameContains(window, "PatchBenchEnhancedPreviewProfileButton", "Selected: Enhanced Profile Preview profile");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Enhanced Profile Preview");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            InvokeByAutomationId(window, "PatchBenchDebugCameraPreviewProfileButton");
            AssertAutomationNameContains(window, "PatchBenchDebugCameraPreviewProfileButton", "Selected: Debug Camera Preview profile");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Debug Camera Preview");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-profile-selected-normal.png", "PatchBenchDebugCameraPreviewProfileButton", 1000, 640);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-profile-selected-narrow.png", "PatchBenchDebugCameraPreviewProfileButton", 760, 640);

            InvokeByAutomationId(window, "PatchBenchClearSelectionButton");
            AssertAutomationNameContains(window, "PatchBenchClearSelectionButton", "Selected: no optional mod rows");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "compatibility-only safe copy");

            InvokeByAutomationId(window, "PatchBenchMenuColorRedButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorRedButton", "Selected: red menu background color");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected menu background: red.");

            InvokeByAutomationId(window, "PatchBenchMenuColorGreenButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorGreenButton", "Selected: green menu background color");
            AssertAutomationNameContains(window, "PatchBenchMenuColorRedButton", "Select red menu background color");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected menu background: green.");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-menu-color-selected-normal.png", "PatchBenchMenuColorRedButton", 1000, 640);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-menu-color-selected-narrow.png", "PatchBenchMenuColorRedButton", 760, 640);

            InvokeByAutomationId(window, "PatchBenchMenuColorClearButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorClearButton", "Selected: no menu background color");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected menu background: none.");

            ExpandByAutomationId(window, "PatchBenchAdvancedLaunchOptionsExpander");
            ClickByAutomationId(window, "PatchBenchQuietCaptureLaunchPresetButton");
            AssertAutomationNameContains(window, "PatchBenchQuietCaptureLaunchPresetButton", "Selected: quiet capture launch preset");
            AssertAutomationNameContains(window, "PatchBenchHighDetailLaunchPresetButton", "Set high detail launch options for safe copy");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            ClickByAutomationId(window, "PatchBenchHighDetailLaunchPresetButton");
            AssertAutomationNameContains(window, "PatchBenchHighDetailLaunchPresetButton", "Selected: high detail launch preset");
            AssertAutomationNameContains(window, "PatchBenchQuietCaptureLaunchPresetButton", "Set quiet capture launch options for safe copy");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            ClickByAutomationId(window, "PatchBenchControlBaselinePresetButton");
            AssertAutomationNameContains(window, "PatchBenchControlBaselinePresetButton", "Selected: control diagnostics baseline config 1");
            AssertAutomationNameContains(window, "PatchBenchHighDetailLaunchPresetButton", "Set high detail launch options for safe copy");

            ClickByAutomationId(window, "PatchBenchControlConfig4PresetButton");
            AssertAutomationNameContains(window, "PatchBenchControlConfig4PresetButton", "Selected: control diagnostics swapped alternate config 4");
            AssertAutomationNameContains(window, "PatchBenchControlBaselinePresetButton", "Set control diagnostics baseline config 1");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-launch-preset-selected-normal.png", "PatchBenchControlConfig4PresetButton", 1000, 720);

            ToggleCheckBoxByAutomationId(window, "PatchBenchNoSoundLaunchOption");
            AssertAutomationNameContains(window, "PatchBenchControlConfig4PresetButton", "Set control diagnostics swapped alternate config 4");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            ClickByAutomationId(window, "PatchBenchControlConfig4PresetButton");
            AssertAutomationNameContains(window, "PatchBenchControlConfig4PresetButton", "Selected: control diagnostics swapped alternate config 4");
            SelectComboBoxItem(window, "PatchBenchConfigurationLaunchPresetComboBox", "Config 3: Alternate morph/jets");
            AssertAutomationNameContains(window, "PatchBenchControlConfig4PresetButton", "Set control diagnostics swapped alternate config 4");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            ClickByAutomationId(window, "PatchBenchControlConfig4PresetButton");
            AssertAutomationNameContains(window, "PatchBenchControlConfig4PresetButton", "Selected: control diagnostics swapped alternate config 4");
            SetTextBoxText(window, "PatchBenchLevelLaunchOption", "100");
            AssertAutomationNameContains(window, "PatchBenchControlConfig4PresetButton", "Set control diagnostics swapped alternate config 4");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");
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

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Requires a private BEA.exe source path in ONSLAUGHT_WINUI_REAL_BEA_EXE_PATH and writes only copied outputs under subagents/.")]
    [Apartment(ApartmentState.STA)]
    public void PatchBench_VerifiesAppliesAndRestoresCopiedExecutableWhenProvided()
    {
        string? sourceExePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_BEA_EXE_PATH");
        if (string.IsNullOrWhiteSpace(sourceExePath) || !File.Exists(sourceExePath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_BEA_EXE_PATH to a private BEA.exe source path to run this copied-executable smoke.");
        }

        if (!string.Equals(Path.GetFileName(sourceExePath), "BEA.exe", StringComparison.OrdinalIgnoreCase))
        {
            Assert.Ignore("ONSLAUGHT_WINUI_REAL_BEA_EXE_PATH must point at BEA.exe.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), "subagents", "winui-patch-bench-interaction", "2026-05-06");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir, Path.GetDirectoryName(Path.GetFullPath(sourceExePath))!);
        string patchWorkspace = Path.Combine(appDataDir, "OnslaughtCareerEditor", "PatchBench");
        if (Directory.Exists(patchWorkspace))
        {
            Directory.Delete(patchWorkspace, recursive: true);
        }

        byte[] sourceHashBefore = SHA256.HashData(File.ReadAllBytes(sourceExePath));
        Application? app = null;
        try
        {
            var startInfo = new ProcessStartInfo(exePath)
            {
                WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
            };
            startInfo.Environment["APPDATA"] = appDataDir;
            startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "binary";

            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Safe game copy", TimeSpan.FromSeconds(20));
            AutomationElement createButton = FindByAutomationId(window, "PatchBenchCreateWorkingCopyButton");
            Assert.That(createButton.IsEnabled, Is.True, "Create BEA.exe-only copy should be enabled when the isolated config points at BEA.exe.");
            ScrollIntoView(createButton);
            createButton.AsButton().Invoke();

            string workingCopyPath = WaitForSingleWorkingCopy(patchWorkspace);
            Assert.That(File.Exists(workingCopyPath), Is.True);
            Assert.That(SHA256.HashData(File.ReadAllBytes(sourceExePath)), Is.EqualTo(sourceHashBefore), "Source BEA.exe must not be changed when creating the BEA.exe-only copy.");
            Assert.That(File.ReadAllBytes(workingCopyPath), Is.EqualTo(File.ReadAllBytes(sourceExePath)), "BEA.exe-only copy should initially match the source executable.");

            AutomationElement verifyButton = FindByAutomationId(window, "PatchBenchVerifyButton");
            bool verifyReady = Retry.WhileFalse(() => verifyButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
            Assert.That(verifyReady, Is.True, "Verify copy should become enabled for the app-owned BEA.exe-only copy.");
            ScrollIntoView(verifyButton);
            verifyButton.AsButton().Invoke();
            AutomationElement operationLog = FindByAutomationId(window, "PatchBenchOperationLog");
            bool verificationReady = Retry.WhileFalse(
                () => (TryGetTextBoxText(operationLog) ?? string.Empty).Contains("ready to apply", StringComparison.OrdinalIgnoreCase)
                    || (TryGetTextBoxText(operationLog) ?? string.Empty).Contains("already applied", StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(verificationReady, Is.True, "Verification output should report a known state.");

            AutomationElement applyButton = FindByAutomationId(window, "PatchBenchApplyButton");
            bool applyReady = Retry.WhileFalse(() => applyButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
            Assert.That(applyReady, Is.True, "Apply to copy should become enabled only after verification.");
            ScrollIntoView(applyButton);
            applyButton.AsButton().Invoke();
            ContinueDialog(window);
            bool applyComplete = Retry.WhileFalse(
                () => (TryGetTextBoxText(operationLog) ?? string.Empty).Contains("Patch apply complete", StringComparison.OrdinalIgnoreCase),
                TimeSpan.FromSeconds(15)).Success;
            Assert.That(applyComplete, Is.True, "Apply output should report patch completion.");
            string applyLog = TryGetTextBoxText(operationLog) ?? string.Empty;
            Assert.That(applyLog, Does.Not.Contain(sourceExePath), "Primary Patch Bench output should not expose the private source path.");
            Assert.That(applyLog, Does.Not.Contain(workingCopyPath), "Primary Patch Bench output should summarize the app-owned BEA.exe-only copy path.");
            Assert.That(applyLog, Does.Contain("app-owned BEA.exe-only copy"));
            Assert.That(applyLog, Does.Contain("BEA.exe-only backup snapshot"));
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(workingCopyPath)), Is.True, "Patch apply should create a backup for the BEA.exe-only copy.");
            Assert.That(SHA256.HashData(File.ReadAllBytes(sourceExePath)), Is.EqualTo(sourceHashBefore), "Source BEA.exe must not be changed by apply.");

            string appliedScreenshot = Path.Combine(evidenceDir, "01-patch-bench-applied.png");
            ScrollIntoView(operationLog);
            window.Focus();
            Thread.Sleep(1_000);
            window.CaptureToFile(appliedScreenshot);
            Assert.That(new FileInfo(appliedScreenshot).Length, Is.GreaterThan(10_000), "Applied Patch Bench screenshot should not be empty.");

            AutomationElement restoreButton = FindByAutomationId(window, "PatchBenchRestoreButton");
            bool restoreReady = Retry.WhileFalse(() => restoreButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
            Assert.That(restoreReady, Is.True, "Restore copy backup should be enabled after apply creates a backup.");
            ScrollIntoView(restoreButton);
            restoreButton.AsButton().Invoke();
            ContinueDialog(window);
            bool restoreComplete = Retry.WhileFalse(
                () => (TryGetTextBoxText(operationLog) ?? string.Empty).Contains("Restore complete.", StringComparison.OrdinalIgnoreCase)
                    && SHA256.HashData(File.ReadAllBytes(workingCopyPath)).SequenceEqual(sourceHashBefore),
                TimeSpan.FromSeconds(15)).Success;
            Assert.That(restoreComplete, Is.True, "Restore output should report a restore result.");
            Assert.That(SHA256.HashData(File.ReadAllBytes(workingCopyPath)), Is.EqualTo(sourceHashBefore), "BEA.exe-only copy should match source again after restore.");
            Assert.That(SHA256.HashData(File.ReadAllBytes(sourceExePath)), Is.EqualTo(sourceHashBefore), "Source BEA.exe must not be changed by restore.");
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

    private static void ContinueDialog(Window window)
    {
        AutomationElement? continueButton = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByText("Continue")),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(continueButton, Is.Not.Null, "Expected confirmation dialog Continue button.");
        continueButton!.AsButton().Invoke();
    }

    private static void InvokeByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        element.AsButton().Invoke();
    }

    private static void ClickByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        window.Focus();
        ScrollIntoView(element);
        try
        {
            element.Focus();
        }
        catch
        {
            // Best-effort focus before a visible click.
        }

        if (element.Patterns.Invoke.IsSupported)
        {
            element.Patterns.Invoke.Pattern.Invoke();
            Thread.Sleep(150);
        }

        element.Click();
        Thread.Sleep(350);
    }

    private static void ToggleCheckBoxByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        window.Focus();
        ScrollIntoView(element);
        if (element.Patterns.Toggle.IsSupported)
        {
            element.Patterns.Toggle.Pattern.Toggle();
        }
        else
        {
            element.Click();
        }

        Thread.Sleep(250);
    }

    private static void ExpandByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        if (element.Patterns.ExpandCollapse.IsSupported)
        {
            element.Patterns.ExpandCollapse.Pattern.Expand();
        }
        else if (element.Patterns.Invoke.IsSupported)
        {
            element.Patterns.Invoke.Pattern.Invoke();
        }
        else
        {
            element.Click();
        }

        Thread.Sleep(250);
    }

    private static void SetTextBoxText(Window window, string automationId, string text)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        element.AsTextBox().Text = text;
    }

    private static void SelectComboBoxItem(Window window, string automationId, string itemText)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        Assert.That(element.IsEnabled, Is.True, $"{automationId} should be enabled before selecting {itemText}.");
        ComboBox comboBox = element.AsComboBox();
        comboBox.Select(itemText);
    }

    private static void AssertComboBoxSelectedText(Window window, string automationId, string expectedText)
    {
        bool matched = Retry.WhileFalse(
            () =>
            {
                try
                {
                    ComboBox comboBox = FindByAutomationId(window, automationId).AsComboBox();
                    return string.Equals(comboBox.SelectedItem?.Text, expectedText, StringComparison.OrdinalIgnoreCase);
                }
                catch
                {
                    return false;
                }
            },
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(matched, Is.True, $"{automationId} should keep selected item: {expectedText}");
    }

    private static void AssertAutomationNameContains(Window window, string automationId, string expectedText)
    {
        string? actualName = null;
        bool matched = Retry.WhileFalse(
            () =>
            {
                actualName = TryGetName(FindByAutomationId(window, automationId));
                return (actualName ?? string.Empty).Contains(expectedText, StringComparison.OrdinalIgnoreCase);
            },
            TimeSpan.FromSeconds(10)).Success;
        Assert.That(matched, Is.True, $"Expected {automationId} automation name to contain: {expectedText}. Actual: {actualName ?? "<null>"}");
    }

    private static void CaptureChoiceStateScreenshot(Window window, IntPtr windowHandle, string evidenceDir, string fileName, string anchorAutomationId, int width, int height)
    {
        NormalizeWindowForCapture(windowHandle, width, height);
        ScrollIntoView(FindByAutomationId(window, anchorAutomationId));
        string outputPath = Path.Combine(evidenceDir, fileName);
        window.Focus();
        Thread.Sleep(350);
        window.CaptureToFile(outputPath);
        Assert.That(File.Exists(outputPath), Is.True, $"Expected selected-state screenshot: {outputPath}");
        Assert.That(new FileInfo(outputPath).Length, Is.GreaterThan(10_000), $"Selected-state screenshot should not be empty: {outputPath}");
        TestContext.Out.WriteLine($"Patch Bench selected-state screenshot: {outputPath}");
    }

    private static void NormalizeWindowForCapture(IntPtr windowHandle, int width, int height)
    {
        if (windowHandle == IntPtr.Zero)
        {
            return;
        }

        _ = ShowWindow(windowHandle, SwRestore);
        _ = SetWindowPos(windowHandle, HwndTop, 16, 16, width, height, SwpShowWindow);
        _ = SetForegroundWindow(windowHandle);
        Thread.Sleep(350);
    }

    private static string WaitForSingleWorkingCopy(string patchWorkspace)
    {
        string? workingCopy = Retry.WhileNull(
            () => Directory.Exists(patchWorkspace)
                ? Directory.GetFiles(patchWorkspace, "BEA.exe", SearchOption.AllDirectories)
                    .Concat(Directory.GetFiles(patchWorkspace, "bea.exe", SearchOption.AllDirectories))
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .SingleOrDefault()
                : null,
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(workingCopy, Is.Not.Null, "Expected exactly one app-owned BEA.exe-only copy.");
        return workingCopy!;
    }

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindFirstDescendant(cf => cf.ByText(text)) is not null,
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible text: {text}");
    }

    private static string? TryGetTextBoxText(AutomationElement element)
    {
        try
        {
            return element.AsTextBox().Text;
        }
        catch
        {
            return null;
        }
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
            // Best-effort visual positioning only; InvokePattern still drives the control.
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

    private static string PrepareIsolatedAppData(string evidenceDir, string gameDirectory)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            JsonSerializer.Serialize(
                new
                {
                    gameDirectory,
                    recentFiles = Array.Empty<string>(),
                    maxRecentFiles = 10,
                    windowWidth = 1280,
                    windowHeight = 820,
                    lastTab = -1,
                    lastSaveSubTab = 0,
                    lastMediaSubTab = 0,
                    assetCatalogPath = (string?)null,
                    allowBackgroundAudio = true,
                    allowBackgroundVideo = false,
                    preventAudioVideoOverlap = true
                },
                new JsonSerializerOptions { WriteIndented = true }));
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

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetForegroundWindow(IntPtr hWnd);
}
