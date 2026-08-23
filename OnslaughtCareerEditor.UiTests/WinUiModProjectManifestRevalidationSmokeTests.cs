using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Definitions;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Exact real-app acceptance for Manifest Revalidation / Drift Review. The smoke
/// opens a real planner receipt, shows unchanged/catalog-drifted/missing states,
/// exports a metadata-only receipt, and independently proves no source bytes moved.
/// </summary>
public class WinUiModProjectManifestRevalidationSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies manifest revalidation through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void ManifestRevalidation_ReviewsUnchangedChangedAndMissingRowsAndExportsMetadataOnlyReceipt()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        AssertNoSubjectProcesses();
        string scratchRoot = Path.Combine(
            Path.GetTempPath(),
            "onslaught-manifest-revalidation-smoke",
            Guid.NewGuid().ToString("N"));
        string catalogDirectory = Path.Combine(scratchRoot, "generated", "asset_catalog");
        string exportsDirectory = Path.Combine(scratchRoot, "generated", "exports");
        string manifestDirectory = Path.Combine(scratchRoot, "planner-manifest");
        string outputDirectory = Path.Combine(scratchRoot, "chosen-output");
        Directory.CreateDirectory(catalogDirectory);
        Directory.CreateDirectory(exportsDirectory);
        Directory.CreateDirectory(manifestDirectory);
        Directory.CreateDirectory(outputDirectory);

        string texturePath = Path.Combine(exportsDirectory, "texture_one.png");
        string meshPath = Path.Combine(exportsDirectory, "ship_body.msh_binary.fbx");
        string embeddedPath = Path.Combine(exportsDirectory, "body00_binary.fbx");
        File.WriteAllBytes(texturePath, [0x89, 0x50, 0x4E, 0x47, 0x01]);
        File.WriteAllBytes(meshPath, [0x46, 0x42, 0x58, 0x02]);
        File.WriteAllBytes(embeddedPath, [0x46, 0x42, 0x58, 0x03]);
        string catalogPath = Path.Combine(catalogDirectory, "catalog.json");
        File.WriteAllText(catalogPath, BuildOriginalCatalogJson());
        AssetCatalogSnapshot original = new AssetCatalogService().Load(catalogDirectory);
        ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
            original,
            [
                new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga"),
                new ModProjectSelectionEntry("mesh", "mesh:ship_body.msh"),
                new ModProjectSelectionEntry("embedded-mesh", "embedded_mesh:100_res_PC/body00"),
            ]);
        string originalCatalogSha256 = plan.CatalogSha256;
        string manifestPath = Path.Combine(manifestDirectory, "existing-plan.json");
        ModProjectPlanExportResult manifestExport = ModProjectPlannerService.Export(
            original,
            plan,
            manifestPath,
            includeTsv: false);
        Assert.That(manifestExport.Success, Is.True, manifestExport.Message);

        File.WriteAllText(catalogPath, BuildCurrentCatalogJson());
        string currentCatalogSha256 = Sha256Hex(catalogPath);
        string manifestSha256 = Sha256Hex(manifestPath);
        string outputPath = Path.Combine(outputDirectory, "revalidation-review.json");
        FileState[] sourceStates =
        [
            CaptureFileState(catalogPath),
            CaptureFileState(manifestPath),
            CaptureFileState(texturePath),
            CaptureFileState(meshPath),
            CaptureFileState(embeddedPath),
        ];

        string evidenceDirectory = Path.Combine(
            ResolveRepoRoot(),
            ".artifacts",
            "winui-manifest-revalidation");
        Directory.CreateDirectory(evidenceDirectory);
        string pidPath = Path.Combine(evidenceDirectory, "app-pid.txt");
        string pidReadyPath = Path.Combine(evidenceDirectory, "pid-ready.txt");
        string continuePath = Path.Combine(evidenceDirectory, "continue.txt");
        File.Delete(pidPath);
        File.Delete(pidReadyPath);
        File.Delete(continuePath);
        string appDataDirectory = PrepareIsolatedAppData(evidenceDirectory);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDirectory;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDirectory;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "assets";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_ASSET_CATALOG"] = catalogDirectory;

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            File.WriteAllText(pidPath, app.ProcessId.ToString(System.Globalization.CultureInfo.InvariantCulture));
            TestContext.Progress.WriteLine($"Manifest revalidation WinUI PID={app.ProcessId}; exact test={TestContext.CurrentContext.Test.FullName}");
            AssertSerializedSubjectProcess(app.ProcessId);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            string loadStatus = WaitForNameContainsValue(
                window,
                "AssetCatalogStatus",
                TimeSpan.FromSeconds(30),
                value => value.Contains("Catalog loaded", StringComparison.OrdinalIgnoreCase));
            Assert.That(loadStatus, Does.Contain("Catalog loaded"));
            File.WriteAllText(pidReadyPath, app.ProcessId.ToString(System.Globalization.CultureInfo.InvariantCulture));
            if (string.Equals(
                    Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_PID_GATE"),
                    "1",
                    StringComparison.Ordinal))
            {
                Assert.That(
                    Retry.WhileFalse(() => File.Exists(continuePath), TimeSpan.FromSeconds(120)).Success,
                    Is.True,
                    $"Live PID gate was not released through {continuePath}.");
            }

            ExpandByAutomationId(window, "AssetManifestReviewExpander");
            SetTextBox(window, "AssetManifestReviewInputFileTextBox", manifestPath);
            InvokeByAutomationId(window, "AssetReviewManifestButton");
            string summary = WaitForNameContainsValue(
                window,
                "AssetManifestReviewSummary",
                TimeSpan.FromSeconds(30),
                value => value.Contains("1 unchanged", StringComparison.OrdinalIgnoreCase) &&
                         value.Contains("1 catalog-drifted", StringComparison.OrdinalIgnoreCase) &&
                         value.Contains("1 missing", StringComparison.OrdinalIgnoreCase));
            Assert.That(summary, Does.Contain("0 ambiguous/duplicate"));
            Assert.That(summary, Does.Contain("0 local-export missing"));
            Assert.That(summary, Does.Contain("0 local-hash mismatch"));
            string provenance = RequireName(window, "AssetManifestReviewProvenance");
            Assert.That(provenance, Does.Contain(manifestSha256));
            Assert.That(provenance, Does.Contain(originalCatalogSha256));
            Assert.That(provenance, Does.Contain(currentCatalogSha256));
            Assert.That(provenance, Does.Contain("Catalog provenance is changed"));

            SetTextBox(window, "AssetManifestReviewOutputFileTextBox", outputPath);
            WaitForEnabled(window, "AssetExportManifestReviewReceiptButton", TimeSpan.FromSeconds(10));
            InvokeByAutomationId(window, "AssetExportManifestReviewReceiptButton");
            string exportStatus = WaitForNameContainsValue(
                window,
                "AssetManifestReviewStatus",
                TimeSpan.FromSeconds(30),
                value => value.Contains("No game assets were copied or modified", StringComparison.OrdinalIgnoreCase) ||
                         value.Contains("could not be written", StringComparison.OrdinalIgnoreCase));
            Assert.That(exportStatus, Does.Contain("No game assets were copied or modified"));

            Assert.That(File.Exists(outputPath), Is.True, "The chosen JSON review receipt should exist.");
            string tsvPath = Path.ChangeExtension(outputPath, ".tsv");
            Assert.That(File.Exists(tsvPath), Is.True, "The optional TSV should be beside the JSON receipt.");
            using JsonDocument receipt = JsonDocument.Parse(File.ReadAllBytes(outputPath));
            JsonElement root = receipt.RootElement;
            Assert.That(root.GetProperty("receiptVersion").GetString(), Is.EqualTo("mod-project-revalidation-receipt.v1"));
            Assert.That(root.GetProperty("originalManifest").GetProperty("manifestSha256").GetString(), Is.EqualTo(manifestSha256));
            Assert.That(root.GetProperty("catalogProvenanceChanged").GetBoolean(), Is.True);
            Assert.That(root.GetProperty("unchangedCount").GetInt32(), Is.EqualTo(1));
            Assert.That(root.GetProperty("catalogDriftedCount").GetInt32(), Is.EqualTo(1));
            Assert.That(root.GetProperty("missingCount").GetInt32(), Is.EqualTo(1));
            string[] statuses = root.GetProperty("entries")
                .EnumerateArray()
                .Select(entry => entry.GetProperty("status").GetString() ?? string.Empty)
                .ToArray();
            Assert.That(statuses, Is.EquivalentTo(new[] { "unchanged", "catalog-drifted", "missing" }));
            Assert.That(File.ReadAllText(tsvPath), Does.Contain("catalog_id\tdisplay_name\tkind\tstatus"));

            Assert.That(
                Directory.GetFiles(outputDirectory).Select(Path.GetExtension),
                Is.EquivalentTo(new[] { ".json", ".tsv" }));
            foreach (FileState state in sourceStates)
            {
                AssertFileUnchanged(state);
            }

            string json = File.ReadAllText(outputPath);
            Assert.That(json, Does.Not.Contain(scratchRoot));
            Assert.That(json, Does.Contain("Metadata-only manifest revalidation review"));
            CaptureScreenshot(window, evidenceDirectory, "01-manifest-revalidation-receipt.png");
            app.Close();
            app = null;
            Assert.That(
                Retry.WhileFalse(
                    () => Process.GetProcessesByName("OnslaughtCareerEditor.WinUI").Length == 0,
                    TimeSpan.FromSeconds(20)).Success,
                Is.True,
                "The exact WinUI subject should terminate before the smoke completes.");
        }
        finally
        {
            app?.Kill();
            File.Delete(continuePath);
            try
            {
                Directory.Delete(scratchRoot, recursive: true);
            }
            catch
            {
            }
        }

        AssertNoSubjectProcesses();
    }

    private static void WaitForEnabled(Window window, string automationId, TimeSpan timeout)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(
            Retry.WhileFalse(() => element.IsEnabled, timeout).Success,
            Is.True,
            $"{automationId} did not become enabled.");
    }

    private static void AssertNoSubjectProcesses()
    {
        Assert.That(Process.GetProcessesByName("BEA"), Is.Empty, "No BEA.exe process may share this GUI lease.");
        Assert.That(
            Process.GetProcesses().Where(process =>
                process.ProcessName.Contains("Godot", StringComparison.OrdinalIgnoreCase)),
            Is.Empty,
            "No Godot process may share this GUI lease.");
        Assert.That(
            Process.GetProcessesByName("OnslaughtCareerEditor.WinUI"),
            Is.Empty,
            "No second WinUI subject may share this GUI lease.");
    }

    private static void AssertSerializedSubjectProcess(int expectedPid)
    {
        int[] pids = Process.GetProcessesByName("OnslaughtCareerEditor.WinUI")
            .Select(process => process.Id)
            .ToArray();
        Assert.That(pids, Is.EqualTo(new[] { expectedPid }));
        Assert.That(Process.GetProcessesByName("BEA"), Is.Empty);
        Assert.That(
            Process.GetProcesses().Where(process =>
                process.ProcessName.Contains("Godot", StringComparison.OrdinalIgnoreCase)),
            Is.Empty);
    }

    private static FileState CaptureFileState(string path) =>
        new(path, File.ReadAllBytes(path), File.GetLastWriteTimeUtc(path));

    private static void AssertFileUnchanged(FileState state)
    {
        Assert.That(File.Exists(state.Path), Is.True, $"Source file disappeared: {state.Path}");
        Assert.That(File.ReadAllBytes(state.Path), Is.EqualTo(state.Bytes), $"Source bytes changed: {state.Path}");
        Assert.That(File.GetLastWriteTimeUtc(state.Path), Is.EqualTo(state.LastWriteUtc), $"Source timestamp changed: {state.Path}");
    }

    private static string Sha256Hex(string path)
    {
        using FileStream stream = File.OpenRead(path);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    private static void ExpandByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.Patterns.ExpandCollapse.IsSupported, Is.True);
        if (element.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value == ExpandCollapseState.Collapsed)
        {
            element.Patterns.ExpandCollapse.Pattern.Expand();
        }

        Assert.That(
            Retry.WhileFalse(
                () => element.Patterns.ExpandCollapse.Pattern.ExpandCollapseState.Value == ExpandCollapseState.Expanded,
                TimeSpan.FromSeconds(5)).Success,
            Is.True);
    }

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        Assert.That(textBox.Patterns.Value.IsSupported, Is.True);
        textBox.Patterns.Value.Pattern.SetValue(text);
        Assert.That(
            Retry.WhileFalse(
                () => string.Equals(textBox.Patterns.Value.Pattern.Value.Value, text, StringComparison.Ordinal),
                TimeSpan.FromSeconds(5)).Success,
            Is.True);
    }

    private static void InvokeByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        Assert.That(element.IsEnabled, Is.True, $"{automationId} should be enabled.");
        Assert.That(element.Patterns.Invoke.IsSupported, Is.True, $"{automationId} should support Invoke.");
        element.Patterns.Invoke.Pattern.Invoke();
    }

    private static string WaitForNameContainsValue(
        Window window,
        string automationId,
        TimeSpan timeout,
        Func<string, bool> predicate)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        string value = string.Empty;
        bool matched = Retry.WhileFalse(() =>
        {
            value = TryGetName(element) ?? string.Empty;
            return predicate(value);
        }, timeout).Success;
        Assert.That(matched, Is.True, $"Expected {automationId} to reach the requested state; actual: {value}");
        return value;
    }

    private static string RequireName(Window window, string automationId)
    {
        string? name = TryGetName(FindByAutomationId(window, automationId));
        Assert.That(name, Is.Not.Null.And.Not.Empty);
        return name!;
    }

    private static void CaptureScreenshot(Window window, string evidenceDirectory, string fileName)
    {
        try
        {
            string path = Path.Combine(evidenceDirectory, fileName);
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
            () =>
            {
                try
                {
                    return window.FindFirstDescendant(cf => cf.ByAutomationId(automationId));
                }
                catch
                {
                    return null;
                }
            },
            TimeSpan.FromSeconds(15)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
    }

    private static Window WaitForMainWindow(Application app, UIA3Automation automation)
    {
        bool handleReady = Retry.WhileFalse(
            () => app.MainWindowHandle != IntPtr.Zero,
            TimeSpan.FromSeconds(30)).Success;
        Assert.That(handleReady, Is.True, "The real WinUI app did not expose a main window handle.");
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

    private static string PrepareIsolatedAppData(string evidenceDirectory)
    {
        string appDataDirectory = Path.Combine(evidenceDirectory, "appdata");
        string configDirectory = Path.Combine(appDataDirectory, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDirectory);
        File.WriteAllText(
            Path.Combine(configDirectory, "config.json"),
            """
            {
              "gameDirectory": null,
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1440,
              "windowHeight": 1000,
              "lastTab": 6,
              "lastSaveSubTab": 0,
              "lastMediaSubTab": 0,
              "assetCatalogPath": null,
              "allowBackgroundAudio": true,
              "allowBackgroundVideo": false,
              "preventAudioVideoOverlap": true
            }
            """);
        return appDataDirectory;
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

    private static string ResolveRepoRoot() =>
        Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));

    private static string BuildOriginalCatalogJson() => """
        {
          "schema_version": 2,
          "path_contract": "bundle-root-relative",
          "summary": { "texture_catalog_entries": 1, "loose_mesh_catalog_entries": 1, "embedded_mesh_catalog_entries": 1, "video_catalog_entries": 0, "language_catalog_entries": 0, "goodie_catalog_entries": 0, "total_catalog_entries": 3 },
          "textures": [
            { "catalog_id": "texture:textures/texture_one.tga", "kind": "texture", "canonical_ref": "textures/texture_one.tga", "source_roots": ["dxtntextures"], "export_png_paths": ["exports/texture_one.png"], "export_sha256": "871923f8e5535ef938edc1ea710d5cf9e18637ce5d39feccef23030823993e4e", "source_aya_count": 1, "export_png_count": 1, "packed_text_ref_count": 0, "gdie_ref_count": 0, "total_packed_ref_count": 0, "referenced_in_packed": true }
          ],
          "loose_meshes": [
            { "catalog_id": "mesh:ship_body.msh", "kind": "loose_mesh", "canonical_ref": "ship_body.msh", "export_fbx_paths": ["exports/ship_body.msh_binary.fbx"], "source_aya_count": 1, "export_fbx_count": 1, "packed_reference_count": 0, "gdie_ref_count": 0, "total_packed_ref_count": 0, "referenced_in_packed": true }
          ],
          "embedded_meshes": [
            { "catalog_id": "embedded_mesh:100_res_PC/body00", "kind": "embedded_mesh", "source_archive": "100_res_PC", "body_name": "body00", "export_fbx_path": "exports/body00_binary.fbx" }
          ],
          "videos": [],
          "language_rows": [],
          "goodies": []
        }
        """;

    private static string BuildCurrentCatalogJson() => """
        {
          "schema_version": 2,
          "path_contract": "bundle-root-relative",
          "summary": { "texture_catalog_entries": 1, "loose_mesh_catalog_entries": 1, "embedded_mesh_catalog_entries": 0, "video_catalog_entries": 0, "language_catalog_entries": 0, "goodie_catalog_entries": 0, "total_catalog_entries": 2 },
          "textures": [
            { "catalog_id": "texture:textures/texture_one.tga", "kind": "texture", "canonical_ref": "textures/texture_one.tga", "source_roots": ["dxtntextures"], "export_png_paths": ["exports/texture_one.png"], "export_sha256": "871923f8e5535ef938edc1ea710d5cf9e18637ce5d39feccef23030823993e4e", "source_aya_count": 1, "export_png_count": 1, "packed_text_ref_count": 0, "gdie_ref_count": 0, "total_packed_ref_count": 0, "referenced_in_packed": true }
          ],
          "loose_meshes": [
            { "catalog_id": "mesh:ship_body.msh", "kind": "loose_mesh", "canonical_ref": "ship_body_v2.msh", "export_fbx_paths": ["exports/ship_body.msh_binary.fbx"], "source_aya_count": 1, "export_fbx_count": 1, "packed_reference_count": 0, "gdie_ref_count": 0, "total_packed_ref_count": 0, "referenced_in_packed": true }
          ],
          "embedded_meshes": [],
          "videos": [],
          "language_rows": [],
          "goodies": []
        }
        """;

    private sealed record FileState(string Path, byte[] Bytes, DateTime LastWriteUtc);
}
