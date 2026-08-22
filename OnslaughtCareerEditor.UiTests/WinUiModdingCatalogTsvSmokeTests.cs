using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Real-app smoke for the Asset Library catalog TSV export: the button stays
/// hidden until a catalog loads, then writes metadata-only TSV beside catalog.json.
/// </summary>
public class WinUiModdingCatalogTsvSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies catalog TSV export through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void ModdingCatalogTsvExport_WritesBesideALoadedCatalog()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string exportRoot = Path.Combine(Path.GetTempPath(), "onslaught-modding-catalog-tsv-smoke", Guid.NewGuid().ToString("N"));
        string catalogDir = Path.Combine(exportRoot, "asset_catalog");
        string exportsDir = Path.Combine(exportRoot, "exports");
        Directory.CreateDirectory(catalogDir);
        Directory.CreateDirectory(exportsDir);
        File.WriteAllBytes(Path.Combine(exportsDir, "texture_one.png"), new byte[] { 0x89, 0x50, 0x4E, 0x47 });
        File.WriteAllText(Path.Combine(catalogDir, "catalog.json"), """
            {
              "schema_version": 2,
              "path_contract": "bundle-root-relative",
              "summary": { "texture_catalog_entries": 1, "loose_mesh_catalog_entries": 0, "embedded_mesh_catalog_entries": 0, "video_catalog_entries": 0, "language_catalog_entries": 0, "goodie_catalog_entries": 0, "total_catalog_entries": 1 },
              "textures": [
                {
                  "catalog_id": "texture:textures/texture_one.tga",
                  "kind": "texture",
                  "canonical_ref": "textures/texture_one.tga",
                  "source_roots": ["dxtntextures"],
                  "export_png_paths": ["exports/texture_one.png"],
                  "source_aya_count": 1,
                  "export_png_count": 1,
                  "packed_text_ref_count": 0,
                  "gdie_ref_count": 0,
                  "total_packed_ref_count": 0,
                  "referenced_in_packed": true
                }
              ],
              "loose_meshes": [],
              "embedded_meshes": [],
              "videos": [],
              "language_rows": [],
              "goodies": []
            }
            """);

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-modding-catalog-tsv");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "assets";

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            WaitForText(window, "Load generated catalog", TimeSpan.FromSeconds(20));

            AutomationElement? beforeLoad = Retry.WhileNull(
                () => window.FindFirstDescendant(cf => cf.ByAutomationId("AssetExportModdingCatalogTsvButton")),
                TimeSpan.FromSeconds(2)).Result;
            Assert.That(beforeLoad, Is.Null, "Catalog TSV export button must stay hidden until a catalog loads.");

            SetTextBox(window, "AssetCatalogFileTextBox", catalogDir);
            InvokeByAutomationId(window, "AssetLoadCatalogButton");

            string loadStatus = WaitForNameContainsValue(window, "AssetCatalogStatus", TimeSpan.FromSeconds(20), value =>
                value.Contains("Catalog loaded", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("not found", StringComparison.OrdinalIgnoreCase));
            Assert.That(loadStatus, Does.Contain("Catalog loaded"),
                $"Loading the fixture catalog should succeed: {loadStatus}");

            AutomationElement exportButton = FindByAutomationId(window, "AssetExportModdingCatalogTsvButton");
            Assert.That(TryGetName(exportButton), Does.Contain("Export catalog TSV"));

            InvokeElement(exportButton);

            string status = WaitForNameContainsValue(window, "AssetCatalogStatus", TimeSpan.FromSeconds(15), value =>
                value.Contains("catalog TSV written", StringComparison.OrdinalIgnoreCase) ||
                value.Contains("could not be written", StringComparison.OrdinalIgnoreCase));
            Assert.That(status, Does.Contain("written"), $"Catalog TSV export should succeed: {status}");

            string tsvPath = Path.Combine(catalogDir, "modding-catalog.tsv");
            Assert.That(File.Exists(tsvPath), Is.True, "The catalog TSV should exist beside catalog.json.");
            string tsv = File.ReadAllText(tsvPath);
            Assert.That(tsv, Does.Contain("catalog_id"));
            Assert.That(tsv, Does.Contain("texture:textures/texture_one.tga"));
            Assert.That(tsv, Does.Not.Contain("\x89PNG"));

            CaptureScreenshot(window, evidenceDir, "01-modding-catalog-tsv.png");

            app.Close();
            app = null;
        }
        finally
        {
            try
            {
                Directory.Delete(exportRoot, recursive: true);
            }
            catch
            {
            }

            app?.Kill();
        }
    }

    private static void SetTextBox(Window window, string automationId, string text)
    {
        FindByAutomationId(window, automationId).AsTextBox().Enter(text);
    }

    private static void InvokeByAutomationId(Window window, string automationId)
    {
        InvokeElement(FindByAutomationId(window, automationId));
    }

    private static void InvokeElement(AutomationElement element)
    {
        element.AsButton().Invoke();
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

    private static string PrepareIsolatedAppData(string evidenceDir)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata");
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        File.WriteAllText(
            Path.Combine(configDir, "config.json"),
            """
            {
              "gameDirectory": null,
              "recentFiles": [],
              "maxRecentFiles": 10,
              "windowWidth": 1280,
              "windowHeight": 900,
              "lastTab": 6,
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
