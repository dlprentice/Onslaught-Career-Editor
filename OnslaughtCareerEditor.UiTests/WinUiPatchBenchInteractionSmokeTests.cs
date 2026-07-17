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
using FlaUI.Core.Definitions;
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
        AssertWinUiBuildIsFresh(exePath);

        string evidenceDir = Path.Combine(Path.GetTempPath(), "onslaught-patch-choice-state-20260625");
        if (Directory.Exists(evidenceDir))
        {
            Directory.Delete(evidenceDir, recursive: true);
        }

        Directory.CreateDirectory(evidenceDir);
        string fakeGameDir = Path.Combine(evidenceDir, "fake-game");
        Directory.CreateDirectory(fakeGameDir);
        string fakeExePath = Path.Combine(fakeGameDir, "BEA.exe");
        File.WriteAllBytes(fakeExePath, new byte[] { 0 });
        byte[] fakeExeHashBefore = SHA256.HashData(File.ReadAllBytes(fakeExePath));
        int[] initialBeaProcessIds = Process.GetProcessesByName("BEA").Select(process => process.Id).ToArray();
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
            AssertAutomationNameContains(window, "PatchBenchWindowedPresetButton", "Selected: Enhanced Copy profile");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Enhanced Copy");
            CaptureChoiceStateScreenshot(
                window,
                app.MainWindowHandle,
                evidenceDir,
                "patch-compatibility-actions-narrow.png",
                "PatchBenchWindowedPresetButton",
                760,
                640);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-player-mods-normal.png", "PatchBenchAddVersionMarkerButton", 1000, 720);
            InvokeByAutomationId(window, "PatchBenchAddVersionMarkerButton");
            AssertAutomationNameContains(window, "PatchBenchPlayerModsSelectionStatus", "PATCHED identity marker");
            InvokeByAutomationId(window, "PatchBenchClearVersionMarkerButton");
            AssertAutomationNameContains(window, "PatchBenchPlayerModsSelectionStatus", "Player mods selected: none");
            InvokeByAutomationId(window, "PatchBenchAddGoodiesPreviewButton");
            AssertAutomationNameContains(window, "PatchBenchPlayerModsSelectionStatus", "Goodies wall preview");
            InvokeByAutomationId(window, "PatchBenchClearGoodiesPreviewButton");
            AssertAutomationNameContains(window, "PatchBenchPlayerModsSelectionStatus", "Player mods selected: none");

            foreach (string normalId in new[]
                     {
                         "PatchBenchSafeCopySelectionReadiness",
                         "PatchBenchPrepareCopiedProfileButton",
                         "PatchBenchCopiedProfileReceiptExpander",
                         "PatchBenchLaunchCopiedProfileButton",
                         "PatchBenchStopCopiedProfileButton",
                         "PatchBenchLocalMultiplayerProbeButton",
                     })
            {
                AssertElementAvailable(window, normalId);
            }

            AssertExpandCollapseState(window, "PatchBenchLabExpander", ExpandCollapseState.Collapsed);
            AssertElementUnavailable(window, "PatchBenchStableDefaultsButton");
            AssertElementUnavailable(window, "PatchBenchCreateMusicSwapPresetComboBox");
            AssertElementUnavailable(window, "PatchBenchAdvancedTechnicalExpander");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-lab-collapsed-normal.png", "PatchBenchLabSelectionStatus", 1000, 720);
            ExpandByAutomationId(window, "PatchBenchLabExpander");
            AssertExpandCollapseState(window, "PatchBenchLabExpander", ExpandCollapseState.Expanded);
            foreach (string groupId in new[]
                     {
                         "PatchBenchLabPatchExperimentsExpander",
                         "PatchBenchLabLaunchControlExpander",
                         "PatchBenchLabOnlineResearchExpander",
                         "PatchBenchLabMusicExperimentsExpander",
                         "PatchBenchLabBeaDiagnosticsExpander",
                     })
            {
                AssertExpandCollapseState(window, groupId, ExpandCollapseState.Collapsed);
            }

            ExpandByAutomationId(window, "PatchBenchLabPatchExperimentsExpander");
            AssertLockedRequiredPatch(window, "PatchBenchPatchCheckBox_resolution_gate");
            AssertLockedRequiredPatch(window, "PatchBenchPatchCheckBox_force_windowed");
            ExpandByAutomationId(window, "PatchBenchPatchDetails_resolution_gate");
            AssertExpandCollapseState(window, "PatchBenchPatchDetails_resolution_gate", ExpandCollapseState.Expanded);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-lab-expanded-header.png", "PatchBenchLabExpander", 1000, 720);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-lab-visual-experiments.png", "PatchBenchMenuColorRedButton", 1000, 720);

            InvokeByAutomationId(window, "PatchBenchStableDefaultsButton");
            AssertAutomationNameContains(window, "PatchBenchStableDefaultsButton", "Selected: legacy graphics-default Lab recipe");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Windowed + Graphics Defaults");
            CollapseByAutomationId(window, "PatchBenchLabExpander");
            AssertExpandCollapseState(window, "PatchBenchLabExpander", ExpandCollapseState.Collapsed);
            AssertAutomationNameContains(window, "PatchBenchLabSelectionStatus", "2 patch choices");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-lab-selection-collapsed-narrow.png", "PatchBenchLabSelectionStatus", 760, 640);
            ExpandByAutomationId(window, "PatchBenchLabExpander");
            AssertExpandCollapseState(window, "PatchBenchLabPatchExperimentsExpander", ExpandCollapseState.Expanded);

            ExpandByAutomationId(window, "PatchBenchLabMusicExperimentsExpander");
            SelectComboBoxItem(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");
            InvokeByAutomationId(window, "PatchBenchEnhancedPreviewProfileButton");
            AssertAutomationNameContains(window, "PatchBenchEnhancedPreviewProfileButton", "Selected: retained legacy Enhanced Profile Preview Lab recipe");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Enhanced Profile Preview");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            InvokeByAutomationId(window, "PatchBenchDebugCameraPreviewProfileButton");
            AssertAutomationNameContains(window, "PatchBenchDebugCameraPreviewProfileButton", "Selected: experimental Debug Camera Preview Lab research recipe");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Debug Camera Preview");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-profile-selected-normal.png", "PatchBenchDebugCameraPreviewProfileButton", 1000, 640);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-profile-selected-narrow.png", "PatchBenchDebugCameraPreviewProfileButton", 760, 640);

            InvokeByAutomationId(window, "PatchBenchClearSelectionButton");
            AssertAutomationNameContains(window, "PatchBenchClearSelectionButton", "Selected: no optional mod rows");
            AssertAutomationNameContains(window, "PatchBenchSelectedProfileStatus", "Selected profile: Enhanced Copy");
            AssertAutomationNameContains(window, "PatchBenchSafeCopySelectionReadiness", "Required compatibility base ready. No optional mods selected.");
            AssertElementEnabled(window, "PatchBenchPrepareCopiedProfileButton", expected: true);
            AssertElementEnabled(window, "PatchBenchTopCreateSafeCopyButton", expected: true);

            InvokeByAutomationId(window, "PatchBenchMenuColorRedButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorRedButton", "Selected: red frontend margins");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected frontend margins: red.");

            InvokeByAutomationId(window, "PatchBenchMenuColorGreenButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorGreenButton", "Selected: green frontend margins");
            AssertAutomationNameContains(window, "PatchBenchMenuColorRedButton", "Select red frontend margins");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected frontend margins: green.");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-menu-color-selected-normal.png", "PatchBenchMenuColorRedButton", 1000, 640);
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-choice-menu-color-selected-narrow.png", "PatchBenchMenuColorRedButton", 760, 640);

            InvokeByAutomationId(window, "PatchBenchMenuColorBlackButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorBlackButton", "Selected: black frontend margins");
            AssertAutomationNameContains(window, "PatchBenchMenuColorGreenButton", "Select green frontend margins");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected frontend margins: black.");

            InvokeByAutomationId(window, "PatchBenchMenuColorClearButton");
            AssertAutomationNameContains(window, "PatchBenchMenuColorClearButton", "Selected: no frontend margin color");
            AssertAutomationNameContains(window, "PatchBenchMenuColorSelectionStatus", "Selected frontend margins: none.");

            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-safe-copy-source-actions-narrow.png", "PatchBenchSafeCopyUseGameFolderButton", 760, 640);
            AssertSourceActionLayout(
                window,
                "PatchBenchSafeCopyUseGameFolderButton",
                "Use configured game folder",
                "PatchBenchSafeCopyBrowseSourceButton",
                "Browse BEA.exe source");

            ExpandByAutomationId(window, "PatchBenchLabBeaDiagnosticsExpander");
            ExpandByAutomationId(window, "PatchBenchAdvancedTechnicalExpander");
            CaptureChoiceStateScreenshot(window, app.MainWindowHandle, evidenceDir, "patch-advanced-source-actions-narrow.png", "PatchBenchBrowseSourceButton", 760, 640);
            AssertSourceActionLayout(
                window,
                "PatchBenchBrowseSourceButton",
                "Browse read-only BEA.exe source",
                "PatchBenchUseGameFolderButton",
                "Use configured source game folder");

            ExpandByAutomationId(window, "PatchBenchLabLaunchControlExpander");
            ExpandByAutomationId(window, "PatchBenchAdvancedLaunchOptionsExpander");
            SelectComboBoxItem(window, "PatchBenchAdminLevelPresetComboBox", "Campaign training world 100");
            AssertTextBoxText(window, "PatchBenchLevelLaunchOption", "100");
            SelectComboBoxItem(window, "PatchBenchAdminLevelPresetComboBox", "Choose admin level preset");
            AssertTextBoxText(window, "PatchBenchLevelLaunchOption", string.Empty);
            AssertComboBoxSelectedText(window, "PatchBenchAdminLevelPresetComboBox", "Choose admin level preset");

            SelectComboBoxItem(window, "PatchBenchAdminLevelPresetComboBox", "Campaign training world 100");
            AssertTextBoxText(window, "PatchBenchLevelLaunchOption", "100");
            ClickByAutomationId(window, "PatchBenchQuietCaptureLaunchPresetButton");
            AssertAutomationNameContains(window, "PatchBenchQuietCaptureLaunchPresetButton", "Selected: quiet capture launch preset");
            AssertAutomationNameContains(window, "PatchBenchHighDetailLaunchPresetButton", "Set high detail launch options for safe copy");
            AssertComboBoxSelectedText(window, "PatchBenchAdminLevelPresetComboBox", "Choose admin level preset");
            AssertTextBoxText(window, "PatchBenchLevelLaunchOption", string.Empty);
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");

            ToggleCheckBoxByAutomationId(window, "PatchBenchShowDebugTraceLaunchOption");
            AssertAutomationNameContains(window, "PatchBenchQuietCaptureLaunchPresetButton", "Set quiet capture launch options for safe copy");
            ToggleCheckBoxByAutomationId(window, "PatchBenchShowDebugTraceLaunchOption");
            AssertAutomationNameContains(window, "PatchBenchQuietCaptureLaunchPresetButton", "Selected: quiet capture launch preset");
            SetTextBoxText(window, "PatchBenchLevelLaunchOption", "  ");
            AssertAutomationNameContains(window, "PatchBenchQuietCaptureLaunchPresetButton", "Selected: quiet capture launch preset");

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
            AssertComboBoxSelectedText(window, "PatchBenchAdminLevelPresetComboBox", "Campaign training world 100");
            ClickByAutomationId(window, "PatchBenchLocalMultiplayerProbeButton");
            AssertTextBoxText(window, "PatchBenchLevelLaunchOption", "850");
            AssertComboBoxSelectedText(window, "PatchBenchAdminLevelPresetComboBox", "Local split-screen test world 850");
            AssertComboBoxSelectedText(window, "PatchBenchCreateMusicSwapPresetComboBox", "BEA_02 over BEA_01");
            Assert.That(SHA256.HashData(File.ReadAllBytes(fakeExePath)), Is.EqualTo(fakeExeHashBefore), "UIA selection smoke must not mutate the source BEA.exe fixture.");
            int[] newBeaProcessIds = Process.GetProcessesByName("BEA")
                .Select(process => process.Id)
                .Except(initialBeaProcessIds)
                .ToArray();
            Assert.That(newBeaProcessIds, Is.Empty, "UIA selection smoke must not launch BEA.exe.");
            Assert.That(
                Directory.Exists(Path.Combine(appDataDir, "OnslaughtCareerEditor", "GameProfiles")),
                Is.False,
                "UIA selection smoke must not create a safe game copy.");
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
    [Explicit("Requires a private BEA.exe source path in ONSLAUGHT_WINUI_REAL_BEA_EXE_PATH and writes only copied outputs under .artifacts/.")]
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

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-patch-bench-interaction");
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
            Thread.Sleep(350);
            return;
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

    private static void CollapseByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        Assert.That(element.Patterns.ExpandCollapse.IsSupported, Is.True, $"{automationId} should expose ExpandCollapsePattern.");
        element.Patterns.ExpandCollapse.Pattern.Collapse();
        Thread.Sleep(250);
    }

    private static void AssertExpandCollapseState(Window window, string automationId, ExpandCollapseState expected)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Patterns.ExpandCollapse.IsSupported, Is.True, $"{automationId} should expose ExpandCollapsePattern.");
        Assert.That(element.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value, Is.EqualTo(expected));
    }

    private static void AssertLockedRequiredPatch(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.Multiple(() =>
        {
            Assert.That(element.IsEnabled, Is.False, $"{automationId} should be visibly locked.");
            Assert.That(element.Patterns.Toggle.IsSupported, Is.True, $"{automationId} should expose TogglePattern.");
            Assert.That(element.Patterns.Toggle.Pattern.ToggleState.Value, Is.EqualTo(ToggleState.On));
            Assert.That(element.Properties.HelpText.Value, Does.Contain("Required and automatically included in every safe game copy"));
        });
    }

    private static void AssertElementEnabled(Window window, string automationId, bool expected)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.IsEnabled, Is.EqualTo(expected), $"Unexpected enabled state for {automationId}.");
    }

    private static void AssertElementAvailable(Window window, string automationId)
    {
        Assert.That(FindByAutomationId(window, automationId), Is.Not.Null);
    }

    private static void AssertElementUnavailable(Window window, string automationId)
    {
        Thread.Sleep(150);
        Assert.That(
            window.FindFirstDescendant(cf => cf.ByAutomationId(automationId)),
            Is.Null,
            $"{automationId} should stay outside the UIA tree while Lab is collapsed.");
    }

    private static void SetTextBoxText(Window window, string automationId, string text)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        ScrollIntoView(element);
        element.AsTextBox().Text = text;
    }

    private static void AssertTextBoxText(Window window, string automationId, string expectedText)
    {
        bool matched = Retry.WhileFalse(
            () => string.Equals(
                FindByAutomationId(window, automationId).AsTextBox().Text,
                expectedText,
                StringComparison.Ordinal),
            TimeSpan.FromSeconds(5)).Success;
        Assert.That(matched, Is.True, $"Expected {automationId} text to equal: {expectedText}");
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

    private static void AssertSourceActionLayout(
        Window window,
        string firstAutomationId,
        string firstExpectedName,
        string secondAutomationId,
        string secondExpectedName)
    {
        AutomationElement first = FindByAutomationId(window, firstAutomationId);
        AutomationElement second = FindByAutomationId(window, secondAutomationId);
        Assert.That(first.Name, Is.EqualTo(firstExpectedName));
        Assert.That(second.Name, Is.EqualTo(secondExpectedName));
        Assert.That(first.IsEnabled, Is.True);
        Assert.That(second.IsEnabled, Is.True);

        System.Drawing.Rectangle windowBounds = window.BoundingRectangle;
        foreach (AutomationElement action in new[] { first, second })
        {
            ScrollIntoView(action);
            Assert.That(
                Retry.WhileFalse(() => !action.IsOffscreen, TimeSpan.FromSeconds(5)).Success,
                Is.True,
                $"{action.AutomationId} should be reachable in the compact workflow.");
            System.Drawing.Rectangle bounds = action.BoundingRectangle;
            Assert.That(bounds.Left, Is.GreaterThanOrEqualTo(windowBounds.Left));
            Assert.That(bounds.Right, Is.LessThanOrEqualTo(windowBounds.Right));
            Assert.That(bounds.Height, Is.GreaterThanOrEqualTo(40));
        }
    }

    private static void CaptureChoiceStateScreenshot(Window window, IntPtr windowHandle, string evidenceDir, string fileName, string anchorAutomationId, int width, int height)
    {
        NormalizeWindowForCapture(windowHandle, width, height);
        Assert.That(
            window.BoundingRectangle.Width,
            Is.InRange(width - 40, width + 40),
            "Compact-layout evidence must use the requested window width.");
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

    private static void AssertWinUiBuildIsFresh(string exePath)
    {
        string projectRoot = Path.Combine(ResolveRepoRoot(), "OnslaughtCareerEditor.WinUI");
        string outputAssemblyPath = Path.Combine(
            Path.GetDirectoryName(exePath) ?? string.Empty,
            "OnslaughtCareerEditor.WinUI.dll");
        Assert.That(File.Exists(outputAssemblyPath), Is.True, $"WinUI build assembly not found at: {outputAssemblyPath}");

        string binSegment = Path.DirectorySeparatorChar + "bin" + Path.DirectorySeparatorChar;
        string objSegment = Path.DirectorySeparatorChar + "obj" + Path.DirectorySeparatorChar;
        DateTime latestSourceWriteUtc = Directory.EnumerateFiles(projectRoot, "*", SearchOption.AllDirectories)
            .Where(path =>
                (path.EndsWith(".cs", StringComparison.OrdinalIgnoreCase) ||
                 path.EndsWith(".xaml", StringComparison.OrdinalIgnoreCase)) &&
                !path.Contains(binSegment, StringComparison.OrdinalIgnoreCase) &&
                !path.Contains(objSegment, StringComparison.OrdinalIgnoreCase))
            .Select(path => File.GetLastWriteTimeUtc(path))
            .Max();

        Assert.That(
            File.GetLastWriteTimeUtc(outputAssemblyPath),
            Is.GreaterThanOrEqualTo(latestSourceWriteUtc),
            $"WinUI build output is older than current source. Rebuild the default output before native UIA: {outputAssemblyPath}");
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
