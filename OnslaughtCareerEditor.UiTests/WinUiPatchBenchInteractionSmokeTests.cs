using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
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
}
