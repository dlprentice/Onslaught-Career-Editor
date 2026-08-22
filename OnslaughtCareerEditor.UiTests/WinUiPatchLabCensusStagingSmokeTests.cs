using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Real-app smoke of the Patch Lab census STAGING journey: with a fabricated
/// app-owned BEA.exe-only safe copy, selecting a MEASURED census row shows the
/// player-terms summary, Stage writes the row's bytes into that copy only (backup
/// snapshot first, sidecar manifest after), and Undo reverses them byte for byte.
/// The installed-game-shaped folder beside it is never touched.
/// </summary>
public class WinUiPatchLabCensusStagingSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and stages a census experiment into a fabricated safe copy through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void PatchLabCensus_StagesIntoSafeCopy_UndoReverses()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-patch-lab-census-staging");
        Directory.CreateDirectory(evidenceDir);

        // Hermetic run state: earlier attempts leave timestamped working copies,
        // manifests, and backups inside this shared evidence folder, and a stale
        // staged copy would defeat the disk-truth checks below. Everything here is
        // test-fabricated, so removing it cannot touch user data.
        foreach (string staleDir in new[] { Path.Combine(evidenceDir, "appdata"), Path.Combine(evidenceDir, "decoy-steam-shape") })
        {
            TryDeleteDirectory(staleDir);
        }

        // A fabricated read-only "source game" folder outside the app-owned
        // workspace; the isolated config points at it, and the page copies it into
        // the workspace through its own Use-game-folder + Create copy flow.
        string fakeGameDir = Path.Combine(evidenceDir, "fake-game");
        Directory.CreateDirectory(fakeGameDir);
        string sourceExe = Path.Combine(fakeGameDir, "BEA.exe");
        WriteSyntheticSafeCopy(sourceExe);
        byte[] originalBytes = File.ReadAllBytes(sourceExe);
        string originalHash = Convert.ToHexString(SHA256.HashData(originalBytes)).ToLowerInvariant();

        string appDataDir = PrepareIsolatedAppData(evidenceDir, fakeGameDir);
        string patchWorkspace = Path.Combine(appDataDir, "OnslaughtCareerEditor", "PatchBench");

        // A decoy that looks like an installed game. Census staging must never write here.
        string decoyGameDir = Path.Combine(evidenceDir, "decoy-steam-shape");
        Directory.CreateDirectory(Path.Combine(decoyGameDir, "data"));
        string decoyExe = Path.Combine(decoyGameDir, "BEA.exe");
        File.WriteAllBytes(decoyExe, new byte[] { 0 });

        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
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

            WaitForText(window, "Safe game copy", TimeSpan.FromSeconds(20));

            // Point the page at the fabricated source through its own UI: the config
            // already names the game folder, so Use configured source game folder
            // loads that BEA.exe, and Create BEA.exe-only copy copies it into the
            // app-owned workspace and selects it.
            SelectWorkingCopyThroughUi(window, fakeGameDir);
            string safeCopyExe = WaitForWorkingCopySelected(window, patchWorkspace);

            ExpandByAutomationId(window, "PatchBenchLabExpander");
            ExpandByAutomationId(window, "PatchLabCensusExpander");

            string status = WaitForNameContainsValue(window, "PatchLabCensusStatus", TimeSpan.FromSeconds(10), value =>
                value.Contains("census", StringComparison.OrdinalIgnoreCase));
            Assert.That(status, Does.Contain("research experiments").IgnoreCase);

            // The staging summary names the safe-copy precondition before anything is selected.
            string summary = WaitForNameContainsValue(window, "PatchLabCensusStagingSummary", TimeSpan.FromSeconds(10), value =>
                value.Contains("safe copy", StringComparison.OrdinalIgnoreCase));

            // Select the first MEASURED row through its real checkbox, then wait for
            // the plan summary to name what staging would change.
            string checkId = FindFirstMeasuredCensusCheckBoxId(status);
            SetCheckBox(window, checkId, true);

            summary = WaitForSummaryChange(window, summary, TimeSpan.FromSeconds(15));
            Assert.That(
                summary,
                Does.Contain("checked against the safe copy"),
                $"expected the staged plan summary, got: {summary}");
            Assert.That(summary, Does.Contain("In player terms"));

            InvokeByAutomationId(window, "PatchLabCensusStageButton");
            AcceptContentDialog(window, "Stage into safe copy");

            string stagedStatus = WaitForNameContainsValue(window, "PatchLabCensusStagingStatus", TimeSpan.FromSeconds(15), value =>
                value.Contains("applied to the safe copy", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("did not run", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("failed", StringComparison.OrdinalIgnoreCase));
            Assert.That(stagedStatus, Does.Contain("applied to the safe copy"));

            // Disk truth: the row's patched bytes landed, the backup exists and still
            // holds the pre-experiment bytes, and the manifest records the batch.
            byte[] stagedBytes = File.ReadAllBytes(safeCopyExe);
            Assert.That(Convert.ToHexString(SHA256.HashData(stagedBytes)).ToLowerInvariant(),
                Is.Not.EqualTo(originalHash), "the safe copy must change after staging");
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(safeCopyExe)), Is.True, "backup snapshot must exist");
            byte[] backupBytes = File.ReadAllBytes(BinaryPatchEngine.BuildBackupPath(safeCopyExe));
            Assert.That(Convert.ToHexString(SHA256.HashData(backupBytes)).ToLowerInvariant(),
                Is.EqualTo(originalHash), "the backup must hold the pre-experiment bytes");
            PatchCensusStagingManifest manifest = PatchCensusStagingService.ReadManifest(safeCopyExe);
            Assert.That(manifest.Present, Is.True, "the undo manifest must exist after staging");
            Assert.That(manifest.Entries.Count, Is.GreaterThanOrEqualTo(1));

            // The receipt list names each staged experiment per row, matching the
            // sidecar manifest on disk - not just a count sentence.
            string expectedReceipt = $"{manifest.Entries[0].Va}: {manifest.Entries[0].Effect}";
            AutomationElement stagedList = FindByAutomationId(window, "PatchLabCensusStagedList");
            bool receiptShown = Retry.WhileFalse(
                () => DescendantNames(stagedList).Any(name =>
                    string.Equals(name, expectedReceipt, StringComparison.Ordinal)),
                TimeSpan.FromSeconds(10)).Success;
            Assert.That(receiptShown, Is.True,
                $"expected the staged receipt '{expectedReceipt}' listed in PatchLabCensusStagedList.");

            // Undo through the app, then disk truth again: byte-identical reversal.
            InvokeByAutomationId(window, "PatchLabCensusUndoButton");
            AcceptContentDialog(window, "Undo experiments");

            string undoneStatus = WaitForNameContainsValue(window, "PatchLabCensusStagingStatus", TimeSpan.FromSeconds(15), value =>
                value.Contains("reversed", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("refused", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("failed", StringComparison.OrdinalIgnoreCase));
            Assert.That(undoneStatus, Does.Contain("reversed"));

            byte[] undoneBytes = File.ReadAllBytes(safeCopyExe);
            Assert.That(Convert.ToHexString(SHA256.HashData(undoneBytes)).ToLowerInvariant(),
                Is.EqualTo(originalHash), "undo must restore the exact pre-staging bytes");

            CaptureScreenshot(window, evidenceDir, "01-patch-lab-census-staging.png");

            app.Close();
            app = null;
        }
        finally
        {
            app?.Kill();
            // The decoy must never have grown a backup or manifest: census staging
            // never writes an installed-game-shaped folder.
            Assert.That(File.Exists(BinaryPatchEngine.BuildBackupPath(decoyExe)), Is.False, "decoy install must stay untouched");
            Assert.That(File.Exists(PatchCensusStagingService.BuildManifestPath(decoyExe)), Is.False, "decoy install must stay untouched");
        }
    }

    private static string FindFirstMeasuredCensusCheckBoxId(string censusStatus)
    {
        // The smoke drives a real checkbox by automation id. Row order follows the
        // TSV, and the sample/real TSVs both lead with MEASURED low-risk rows, so
        // the first row of the filtered list is the first measured one and its
        // checkbox id follows PatchCensusRowModel's PatchCensusCheck_{index:D3}
        // contract. The status text is parsed rather than trusted: if it stops
        // naming MEASURED rows, this fails loudly instead of staging a
        // STATIC_ONLY or SPECULATIVE experiment by accident.
        const string marker = "MEASURED ";
        int measuredIndex = censusStatus.IndexOf(marker, StringComparison.OrdinalIgnoreCase);
        Assert.That(
            measuredIndex,
            Is.GreaterThanOrEqualTo(0),
            $"Census status must name MEASURED rows for this smoke to pick one, got: {censusStatus}");
        int countStart = measuredIndex + marker.Length;
        int digitsEnd = countStart;
        while (digitsEnd < censusStatus.Length && char.IsAsciiDigit(censusStatus[digitsEnd]))
        {
            digitsEnd++;
        }

        Assert.That(
            digitsEnd,
            Is.GreaterThan(countStart),
            $"Census status must give the MEASURED count, got: {censusStatus}");
        int measuredCount = int.Parse(
            censusStatus[countStart..digitsEnd],
            System.Globalization.CultureInfo.InvariantCulture);
        Assert.That(
            measuredCount,
            Is.GreaterThanOrEqualTo(1),
            "The census must contain at least one MEASURED row for this smoke to stage.");

        return "PatchCensusCheck_000";
    }

    /// <summary>
    /// Waits until a BEA.exe-only copy exists inside the app-owned patch workspace
    /// and returns its path. The working-copy path box lives in the collapsed
    /// diagnostics expander, so disk truth is polled instead of UI text. Each create
    /// lands in a fresh timestamped folder, so the copy this run just made is always
    /// the newest one; picking any older copy would read a previous attempt's state.
    /// </summary>
    private static string WaitForWorkingCopySelected(Window window, string patchWorkspace)
    {
        DateTime start = DateTime.UtcNow;
        string? workingCopy = Retry.WhileNull(
            () => Directory.Exists(patchWorkspace)
                ? Directory.GetFiles(patchWorkspace, "BEA.exe", SearchOption.AllDirectories)
                    .OrderByDescending(path => File.GetCreationTimeUtc(path))
                    .FirstOrDefault()
                : null,
            TimeSpan.FromSeconds(20)).Result;
        Assert.That(workingCopy, Is.Not.Null, "Expected the created BEA.exe-only copy inside the app-owned workspace.");
        Assert.That(
            File.GetCreationTimeUtc(workingCopy!),
            Is.GreaterThanOrEqualTo(start.AddSeconds(-5)),
            $"Expected the working copy to be created by this run (got: {workingCopy}).");
        return workingCopy!;
    }

    private static string? TryGetValue(AutomationElement element)
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

    /// <summary>
    /// Collects the UIA names of an element's descendants (bounded, for list
    /// receipt assertions). Returns names in tree order; duplicates preserved.
    /// </summary>
    private static System.Collections.Generic.IReadOnlyList<string> DescendantNames(AutomationElement element)
    {
        try
        {
            return element.FindAllDescendants()
                .Select(candidate => TryGetName(candidate) ?? string.Empty)
                .Where(name => name.Length > 0)
                .ToArray();
        }
        catch
        {
            return Array.Empty<string>();
        }
    }

    /// <summary>
    /// Points the page at the fabricated safe copy through its own UI: the isolated
    /// config names the game folder, so the top-level "Use configured game folder"
    /// loads that BEA.exe as the read-only source; then the smoke opens the
    /// BEA.exe-only diagnostics and clicks Create BEA.exe-only copy, which copies
    /// the executable into the app-owned workspace.
    /// </summary>
    private static void SelectWorkingCopyThroughUi(Window window, string fakeGameDir)
    {
        InvokeByAutomationId(window, "PatchBenchSafeCopyUseGameFolderButton");

        ExpandByAutomationId(window, "PatchBenchLabExpander");
        ExpandByAutomationId(window, "PatchBenchLabBeaDiagnosticsExpander");
        ExpandByAutomationId(window, "PatchBenchAdvancedTechnicalExpander");

        AutomationElement createButton = FindByAutomationId(window, "PatchBenchCreateWorkingCopyButton");
        bool ready = Retry.WhileFalse(() => createButton.IsEnabled, TimeSpan.FromSeconds(10)).Success;
        Assert.That(ready, Is.True, "Create BEA.exe-only copy should enable once the configured source loads.");
        createButton.AsButton().Invoke();
        _ = fakeGameDir; // expressed through config.json; kept for clarity in callers
    }

    /// <summary>
    /// Builds a synthetic BEA.exe whose bytes match the first census row's
    /// expectations: every catalog region carries its original bytes, and the two
    /// census sites the smoke touches (0x6F4A8 lost-countdown, 0x6F33D won-countdown)
    /// carry the TSV's recorded original bytes. Everything else is 0x90 filler.
    /// </summary>
    private static void WriteSyntheticSafeCopy(string exePath)
    {
        int maxEnd = 0;
        foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
        {
            foreach (BinaryPatchRegion region in BinaryPatchEngine.GetPatchRegions(spec))
            {
                maxEnd = Math.Max(maxEnd, region.FileOffset + region.Original.Length);
            }
        }

        byte[] data = new byte[Math.Max(maxEnd, 0x1E5000) + 0x1000];
        Array.Fill(data, (byte)0x90);

        // Census sites exercised by this smoke: exact original bytes from the TSV.
        WriteHex(data, 0x0006F4A8, "c7434800000040");
        WriteHex(data, 0x0006F33D, "0000a040");

        foreach (BinaryPatchSpec spec in BinaryPatchEngine.PatchSpecs)
        {
            foreach (BinaryPatchRegion region in BinaryPatchEngine.GetPatchRegions(spec))
            {
                region.Original.CopyTo(data, region.FileOffset);
            }
        }

        File.WriteAllBytes(exePath, data);
    }

    private static void WriteHex(byte[] data, int offset, string hex)
    {
        for (int i = 0; i < hex.Length / 2; i++)
        {
            data[offset + i] = Convert.ToByte(hex.Substring(i * 2, 2), 16);
        }
    }

    private static void TryDeleteDirectory(string path)
    {
        try
        {
            if (Directory.Exists(path))
            {
                Directory.Delete(path, recursive: true);
            }
        }
        catch (IOException)
        {
            // A previous run's app process can still hold a lock; the freshness
            // assertion in WaitForWorkingCopySelected catches any survivor.
        }
        catch (UnauthorizedAccessException)
        {
        }
    }

    private static void SetCheckBox(Window window, string automationId, bool isChecked)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        window.Focus();
        ScrollIntoView(element);
        if (element.Patterns.Toggle.IsSupported)
        {
            var toggle = element.Patterns.Toggle.Pattern;
            bool current = toggle.ToggleState == FlaUI.Core.Definitions.ToggleState.On;
            if (current != isChecked)
            {
                toggle.Toggle();
            }
        }
        else
        {
            element.Click();
        }

        Thread.Sleep(250);
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
            // Best-effort visual positioning only; TogglePattern still drives the control.
        }
    }

    private static void AcceptContentDialog(Window window, string primaryButtonText)
    {
        AutomationElement? button = Retry.WhileNull(
            () =>
            {
                // The dialog is a child of the window's XamlRoot, not of the page;
                // ByText finds the primary button by its visible label.
                return window.FindFirstDescendant(cf => cf.ByText(primaryButtonText));
            },
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(button, Is.Not.Null, $"Expected the '{primaryButtonText}' dialog button.");
        button!.AsButton().Invoke();
    }

    private static void ExpandByAutomationId(Window window, string automationId)
    {
        AutomationElement expander = FindByAutomationId(window, automationId);
        var pattern = expander.Patterns.ExpandCollapse.PatternOrDefault;
        if (pattern is not null && pattern.ExpandCollapseState == FlaUI.Core.Definitions.ExpandCollapseState.Collapsed)
        {
            pattern.Expand();
        }
    }

    private static void InvokeByAutomationId(Window window, string automationId)
    {
        FindByAutomationId(window, automationId).AsButton().Invoke();
    }

    private static string WaitForNameContainsValue(
        Window window,
        string automationId,
        TimeSpan timeout,
        Func<string, bool> predicate)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        bool matched = Retry.WhileFalse(
            () => predicate(TryGetName(element) ?? string.Empty),
            timeout).Success;
        Assert.That(matched, Is.True, $"Expected '{automationId}' to satisfy the condition.");
        return TryGetName(element) ?? string.Empty;
    }

    /// <summary>
    /// Waits until the named element's text differs from previousText and returns
    /// the new value. Used when a status line legitimately keeps its old sentence,
    /// which a content predicate alone cannot distinguish from a stalled update.
    /// </summary>
    private static string WaitForSummaryChange(Window window, string previousText, TimeSpan timeout)
    {
        AutomationElement element = FindByAutomationId(window, "PatchLabCensusStagingSummary");
        bool matched = Retry.WhileFalse(
            () =>
            {
                string current = TryGetName(element) ?? string.Empty;
                return current.Length > 0 && !string.Equals(current, previousText, StringComparison.Ordinal);
            },
            timeout).Success;
        Assert.That(matched, Is.True, "Expected the staging summary to change after selecting a census row.");
        return TryGetName(element) ?? string.Empty;
    }

    private static void CaptureScreenshot(Window window, string evidenceDir, string fileName)
    {
        try
        {
            string path = Path.Combine(evidenceDir, fileName);
            window.CaptureToFile(path);
            TestContext.AddTestAttachment(path);
        }
        catch
        {
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
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
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

    private static void WaitForText(Window window, string text, TimeSpan timeout)
    {
        bool visible = Retry.WhileFalse(
            () => window.FindAllDescendants()
                .Any(candidate => (TryGetName(candidate) ?? string.Empty).Contains(text, StringComparison.OrdinalIgnoreCase)),
            timeout).Success;
        Assert.That(visible, Is.True, $"Expected visible UIA name containing: {text}");
    }

    private static string PrepareIsolatedAppData(string evidenceDir, string gameDirectory)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            System.Text.Json.JsonSerializer.Serialize(
                new
                {
                    gameDirectory,
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
                    preventAudioVideoOverlap = true
                },
                new System.Text.Json.JsonSerializerOptions { WriteIndented = true }));
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
