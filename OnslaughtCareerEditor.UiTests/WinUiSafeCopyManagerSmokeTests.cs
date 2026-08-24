using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
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
    private const string ExtractedSafeCopyExperiment = "extracted-portable-winui-synthetic-safe-copy-v1";

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

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches one extracted portable app process and completes a generated synthetic safe-copy workflow.")]
    [Apartment(ApartmentState.STA)]
    public void ExtractedPortableApp_CreatesSyntheticSafeCopyAndProvesNegativeControls()
    {
        string exePath = ResolveWinUiAppPath();
        Assert.That(File.Exists(exePath), Is.True, $"Extracted WinUI executable not found: {exePath}");

        string approvedRoot = ResolveSafeCopyProbeRoot();
        Assert.That(Directory.Exists(approvedRoot), Is.False, "The extracted safe-copy probe root must be fresh.");
        Directory.CreateDirectory(approvedRoot);

        int timeoutSeconds = ResolveSafeCopyProbeTimeoutSeconds();
        string appDataDir = Path.Combine(approvedRoot, "appdata");
        string outputRoot = Path.Combine(appDataDir, "OnslaughtCareerEditor", "GameProfiles");
        string aliasSourceRoot = Path.Combine(outputRoot, "unsafe-alias-source");
        string restoredAliasSourceRoot = Path.Combine(outputRoot, "unsafe-alias-source-restored");
        string sourceRoot = Path.Combine(approvedRoot, "source-fixture");
        string aliasExe = PrepareSyntheticGameRoot(aliasSourceRoot);
        _ = PrepareSyntheticGameRoot(sourceRoot);
        string sourceTreeBefore = ComputeTreeSha256(sourceRoot);
        WriteAppConfig(appDataDir, aliasSourceRoot);

        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "binary";
        startInfo.Environment["ONSLAUGHT_GAME_DIR_CANDIDATES"] = string.Empty;
        startInfo.Environment["ONSLAUGHT_STEAM_ROOT_CANDIDATES"] = Path.Combine(approvedRoot, "empty-steam-root");
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_EXE_PATH"] = Path.GetFullPath(exePath);
        startInfo.Environment["ONSLAUGHT_WINUI_SAFE_COPY_PROBE_ROOT"] = approvedRoot;
        startInfo.Environment["ONSLAUGHT_WINUI_SAFE_COPY_PROBE_TIMEOUT_SECONDS"] = timeoutSeconds.ToString();
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_SYNTHETIC_SAFE_COPY_ROOT"] = sourceRoot;

        Application? app = null;
        int processId = 0;
        string targetRoot = string.Empty;
        string targetTreeSha256 = string.Empty;
        string appReportedSummary = string.Empty;
        try
        {
            Assert.That(CountProcessesAtPath(exePath), Is.Zero, "The extracted executable must start with no owned process.");
            app = Application.Launch(startInfo);
            processId = app.ProcessId;
            Assert.That(
                Retry.WhileFalse(() => CountProcessesAtPath(exePath) == 1, TimeSpan.FromSeconds(10)).Success,
                Is.True,
                "Exactly one extracted WinUI process must own this experiment.");
            WritePreregistration(approvedRoot, exePath, processId, timeoutSeconds);

            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            InvokeElement(FindByAutomationId(window, "PatchBenchTopUseGameFolderButton"));
            AssertElementEnabled(window, "PatchBenchTopCreateSafeCopyButton");

            // Stale/missing-input negative control: preserve the generated bytes by
            // renaming the executable after Create was enabled. The live handler
            // must re-check the source and decline before opening a dialog.
            File.Move(aliasExe, aliasExe + ".missing");
            InvokeElement(FindByAutomationId(window, "PatchBenchTopCreateSafeCopyButton"));
            WaitForNameContaining(
                window,
                "PatchBenchSafeCopySelectionReadiness",
                "Choose a read-only BEA.exe source",
                TimeSpan.FromSeconds(10));
            Assert.That(Directory.EnumerateFiles(outputRoot, GameProfilePreflightService.ProfileManifestFileName, SearchOption.AllDirectories), Is.Empty);

            _ = PrepareSyntheticGameRoot(restoredAliasSourceRoot);
            WriteAppConfig(appDataDir, restoredAliasSourceRoot);
            InvokeElement(FindByAutomationId(window, "PatchBenchTopUseGameFolderButton"));
            AssertElementEnabled(window, "PatchBenchTopCreateSafeCopyButton");

            // Source/output-alias negative control: the source sits under the
            // app-owned output root. AppCore must reject it before any copy.
            InvokeElement(FindByAutomationId(window, "PatchBenchTopCreateSafeCopyButton"));
            ConfirmContinue(window);
            WaitForTextBoxContaining(
                window,
                "PatchBenchOperationLog",
                "Could not prepare a safe game copy. Nothing was changed.",
                TimeSpan.FromSeconds(30));
            Assert.That(Directory.EnumerateFiles(outputRoot, GameProfilePreflightService.ProfileManifestFileName, SearchOption.AllDirectories), Is.Empty);

            WriteAppConfig(appDataDir, sourceRoot);
            InvokeElement(FindByAutomationId(window, "PatchBenchTopUseGameFolderButton"));
            AssertElementEnabled(window, "PatchBenchTopCreateSafeCopyButton");

            InvokeElement(FindByAutomationId(window, "PatchBenchTopCreateSafeCopyButton"));
            ConfirmContinue(window);
            WaitForTextBoxContaining(
                window,
                "PatchBenchOperationLog",
                "Safe game copy preparation complete.",
                TimeSpan.FromSeconds(120));

            string[] generatedTargets = Directory
                .EnumerateFiles(outputRoot, GameProfilePreflightService.ProfileManifestFileName, SearchOption.AllDirectories)
                .Select(Path.GetDirectoryName)
                .Where(path => !string.IsNullOrWhiteSpace(path))
                .Cast<string>()
                .ToArray();
            Assert.That(generatedTargets, Has.Length.EqualTo(1));
            targetRoot = Path.GetFullPath(generatedTargets[0]);
            Assert.That(IsSameOrUnder(targetRoot, approvedRoot), Is.True);
            Assert.That(IsSameOrUnder(targetRoot, outputRoot), Is.True);
            Assert.That(ComputeTreeSha256(sourceRoot), Is.EqualTo(sourceTreeBefore), "The synthetic source must stay byte-identical.");
            targetTreeSha256 = ComputeTreeSha256(targetRoot);
            appReportedSummary = FindByAutomationId(window, "PatchBenchOperationLog").AsTextBox().Text;
            Assert.That(appReportedSummary, Does.Contain("Only files inside the safe copy were changed"));
        }
        finally
        {
            try
            {
                app?.Close();
            }
            catch
            {
                // Fall through to the exact owned-process kill below.
            }

            if (app is not null && !app.HasExited)
                app.Kill();

            Assert.That(
                Retry.WhileFalse(() => CountProcessesAtPath(exePath) == 0, TimeSpan.FromSeconds(10)).Success,
                Is.True,
                "The one preregistered extracted WinUI process must be gone.");
        }

        string sourceTreeAfter = ComputeTreeSha256(sourceRoot);
        Assert.That(sourceTreeAfter, Is.EqualTo(sourceTreeBefore));
        WriteResultReceipt(
            approvedRoot,
            sourceRoot,
            outputRoot,
            targetRoot,
            sourceTreeBefore,
            sourceTreeAfter,
            targetTreeSha256,
            processId,
            appReportedSummary);
    }

    private static string ResolveSafeCopyProbeRoot()
    {
        string? requested = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_SAFE_COPY_PROBE_ROOT");
        Assert.That(requested, Is.Not.Null.And.Not.Empty, "The extracted safe-copy probe root must be explicit.");
        string root = Path.GetFullPath(requested!);
        string artifactsRoot = Path.GetFullPath(Path.Combine(ResolveRepoRoot(), ".artifacts"));
        Assert.That(IsSameOrUnder(root, artifactsRoot), Is.True, "The live workflow must stay under ignored .artifacts scratch.");
        return root;
    }

    private static int ResolveSafeCopyProbeTimeoutSeconds()
    {
        string? value = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_SAFE_COPY_PROBE_TIMEOUT_SECONDS");
        Assert.That(int.TryParse(value, out int seconds) && seconds is >= 60 and <= 600, Is.True);
        return seconds;
    }

    private static string PrepareSyntheticGameRoot(string root)
    {
        Directory.CreateDirectory(Path.Combine(root, "data", "Resources"));
        string exePath = Path.Combine(root, "BEA.exe");
        SeedSyntheticExecutable(exePath);
        File.WriteAllBytes(Path.Combine(root, "defaultoptions.bea"), new byte[10_004]);
        File.WriteAllText(Path.Combine(root, "data", "Resources", "base_res_PC.aya"), "generated-public-safe-resource\n");
        File.WriteAllBytes(Path.Combine(root, "binkw32.dll"), new byte[] { 1 });
        File.WriteAllBytes(Path.Combine(root, "ogg.dll"), new byte[] { 2 });
        File.WriteAllBytes(Path.Combine(root, "vorbis.dll"), new byte[] { 3 });
        File.WriteAllBytes(Path.Combine(root, "zlib.dll"), new byte[] { 4 });
        return exePath;
    }

    private static void SeedSyntheticExecutable(string path)
    {
        int maxEnd = BinaryPatchEngine.PatchSpecs
            .SelectMany(BinaryPatchEngine.GetPatchRegions)
            .Select(region => region.FileOffset + region.Original.Length)
            .Max();
        byte[] data = Enumerable.Repeat((byte)0x90, maxEnd + 0x100).ToArray();
        foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
        {
            foreach (BinaryPatchRegion region in BinaryPatchEngine.GetPatchRegions(spec))
                region.Original.CopyTo(data, region.FileOffset);
        }

        File.WriteAllBytes(path, data);
    }

    private static void WriteAppConfig(string appDataRoot, string gameRoot)
    {
        string configRoot = Path.Combine(appDataRoot, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configRoot);
        File.WriteAllText(
            Path.Combine(configRoot, "config.json"),
            JsonSerializer.Serialize(
                new
                {
                    gameDirectory = Path.GetFullPath(gameRoot),
                    recentFiles = Array.Empty<string>(),
                    maxRecentFiles = 10,
                    windowWidth = 1280,
                    windowHeight = 820,
                    lastTab = 3,
                    lastSaveSubTab = 0,
                    lastMediaSubTab = 0,
                    assetCatalogPath = (string?)null,
                    allowBackgroundAudio = true,
                    allowBackgroundVideo = false,
                    preventAudioVideoOverlap = true,
                },
                new JsonSerializerOptions { WriteIndented = true }));
    }

    private static void WritePreregistration(string approvedRoot, string exePath, int processId, int timeoutSeconds)
    {
        File.WriteAllText(
            Path.Combine(approvedRoot, "safe-copy-preregistration.json"),
            JsonSerializer.Serialize(
                new
                {
                    schema = "winui-extracted-safe-copy-preregistration.v1",
                    experiment = ExtractedSafeCopyExperiment,
                    executablePath = Path.GetFullPath(exePath),
                    executableSha256 = ComputeFileSha256(exePath),
                    processIds = new[] { processId },
                    timeoutSeconds,
                },
                new JsonSerializerOptions { WriteIndented = true }));
    }

    private static void WriteResultReceipt(
        string approvedRoot,
        string sourceRoot,
        string outputRoot,
        string targetRoot,
        string sourceTreeBefore,
        string sourceTreeAfter,
        string targetTreeSha256,
        int processId,
        string appReportedSummary)
    {
        File.WriteAllText(
            Path.Combine(approvedRoot, "safe-copy-result.json"),
            JsonSerializer.Serialize(
                new
                {
                    schema = "winui-extracted-safe-copy-result.v1",
                    status = "pass",
                    experiment = ExtractedSafeCopyExperiment,
                    approvedRoot = Path.GetFullPath(approvedRoot),
                    sourceRoot = Path.GetFullPath(sourceRoot),
                    outputRoot = Path.GetFullPath(outputRoot),
                    targetRoot = Path.GetFullPath(targetRoot),
                    sourceTreeSha256Before = sourceTreeBefore,
                    sourceTreeSha256After = sourceTreeAfter,
                    targetTreeSha256,
                    processIds = new[] { processId },
                    processExitClean = true,
                    negativeControls = new
                    {
                        missingInput = "pass",
                        sourceOutputAlias = "pass",
                    },
                    appReportedSummary,
                },
                new JsonSerializerOptions { WriteIndented = true }));
    }

    private static string ComputeTreeSha256(string root)
    {
        using var digest = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        foreach (string path in Directory
                     .EnumerateFiles(root, "*", SearchOption.AllDirectories)
                     .OrderBy(path => Path.GetRelativePath(root, path).Replace('\\', '/'), StringComparer.Ordinal))
        {
            string relative = Path.GetRelativePath(root, path).Replace('\\', '/');
            digest.AppendData(Encoding.UTF8.GetBytes(relative + "\n"));
            digest.AppendData(Encoding.ASCII.GetBytes(ComputeFileSha256(path) + "\n"));
        }

        return Convert.ToHexString(digest.GetHashAndReset()).ToLowerInvariant();
    }

    private static string ComputeFileSha256(string path)
    {
        using FileStream stream = File.OpenRead(path);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    private static bool IsSameOrUnder(string path, string root)
    {
        string fullPath = Path.GetFullPath(path).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        string fullRoot = Path.GetFullPath(root).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        return string.Equals(fullPath, fullRoot, StringComparison.OrdinalIgnoreCase) ||
               fullPath.StartsWith(fullRoot + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase);
    }

    private static int CountProcessesAtPath(string executablePath)
    {
        string expected = Path.GetFullPath(executablePath);
        int count = 0;
        foreach (Process process in Process.GetProcessesByName(Path.GetFileNameWithoutExtension(executablePath)))
        {
            using (process)
            {
                try
                {
                    if (string.Equals(process.MainModule?.FileName, expected, StringComparison.OrdinalIgnoreCase))
                        count++;
                }
                catch (Exception ex) when (ex is InvalidOperationException or System.ComponentModel.Win32Exception)
                {
                    // A process that exited between enumeration and inspection is not live.
                }
            }
        }

        return count;
    }

    private static void AssertElementEnabled(Window window, string automationId)
    {
        Assert.That(
            Retry.WhileFalse(
                () => FindByAutomationId(window, automationId).IsEnabled,
                TimeSpan.FromSeconds(10),
                TimeSpan.FromMilliseconds(200)).Success,
            Is.True,
            $"Expected enabled element '{automationId}'.");
    }

    private static void WaitForNameContaining(Window window, string automationId, string expected, TimeSpan timeout)
    {
        string actual = string.Empty;
        Assert.That(
            Retry.WhileFalse(
                () =>
                {
                    actual = TryGetName(FindByAutomationId(window, automationId)) ?? string.Empty;
                    return actual.Contains(expected, StringComparison.Ordinal);
                },
                timeout,
                TimeSpan.FromMilliseconds(250)).Success,
            Is.True,
            $"Expected '{automationId}' to contain '{expected}'. Actual: {actual}");
    }

    private static void WaitForTextBoxContaining(Window window, string automationId, string expected, TimeSpan timeout)
    {
        string actual = string.Empty;
        Assert.That(
            Retry.WhileFalse(
                () =>
                {
                    actual = FindByAutomationId(window, automationId).AsTextBox().Text;
                    return actual.Contains(expected, StringComparison.Ordinal);
                },
                timeout,
                TimeSpan.FromMilliseconds(250)).Success,
            Is.True,
            $"Expected '{automationId}' text to contain '{expected}'. Actual: {actual}");
    }

    private static void ConfirmContinue(Window window)
    {
        AutomationElement? button = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByName("Continue")),
            TimeSpan.FromSeconds(10),
            TimeSpan.FromMilliseconds(200)).Result;
        Assert.That(button, Is.Not.Null, "Expected the safe-copy confirmation Continue button.");
        InvokeElement(button!);
    }

    private static void InvokeElement(AutomationElement element)
    {
        if (element.Patterns.Invoke.IsSupported)
        {
            element.Patterns.Invoke.Pattern.Invoke();
            return;
        }

        if (element.Patterns.SelectionItem.IsSupported)
        {
            element.Patterns.SelectionItem.Pattern.Select();
            return;
        }

        element.Click();
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
        string? explicitExePath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_EXE_PATH");
        if (!string.IsNullOrWhiteSpace(explicitExePath))
            return explicitExePath;

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
