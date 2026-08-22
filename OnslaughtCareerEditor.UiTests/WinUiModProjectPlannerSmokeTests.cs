using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Exact real-app acceptance for the metadata-only Mod Project Manifest Planner.
/// The smoke selects a texture and loose mesh from one generated fixture catalog,
/// exports the receipt, then reads the files independently and proves no source
/// asset was copied into the chosen output folder.
/// </summary>
public class WinUiModProjectPlannerSmokeTests
{
    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and verifies the mod project plan receipt through UI Automation.")]
    [Apartment(ApartmentState.STA)]
    public void ModProjectPlanner_SelectsTwoKindsAndExportsMetadataOnlyReceipt()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string scratchRoot = Path.Combine(Path.GetTempPath(), "onslaught-mod-project-planner-smoke", Guid.NewGuid().ToString("N"));
        string catalogDir = Path.Combine(scratchRoot, "generated", "asset_catalog");
        string exportsDir = Path.Combine(scratchRoot, "generated", "exports");
        string outputDir = Path.Combine(scratchRoot, "chosen-output");
        Directory.CreateDirectory(catalogDir);
        Directory.CreateDirectory(exportsDir);
        Directory.CreateDirectory(outputDir);
        string texturePath = Path.Combine(exportsDir, "texture_one.png");
        string meshPath = Path.Combine(exportsDir, "ship_body.msh_binary.fbx");
        File.WriteAllBytes(texturePath, [0x89, 0x50, 0x4E, 0x47, 0x01]);
        File.WriteAllBytes(meshPath, [0x46, 0x42, 0x58, 0x02]);
        string catalogPath = Path.Combine(catalogDir, "catalog.json");
        File.WriteAllText(catalogPath, """
            {
              "schema_version": 2,
              "path_contract": "bundle-root-relative",
              "summary": { "texture_catalog_entries": 1, "loose_mesh_catalog_entries": 1, "embedded_mesh_catalog_entries": 0, "video_catalog_entries": 0, "language_catalog_entries": 0, "goodie_catalog_entries": 0, "total_catalog_entries": 2 },
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
              "loose_meshes": [
                {
                  "catalog_id": "mesh:ship_body.msh",
                  "kind": "loose_mesh",
                  "canonical_ref": "ship_body.msh",
                  "export_fbx_paths": ["exports/ship_body.msh_binary.fbx"],
                  "source_aya_count": 1,
                  "export_fbx_count": 1,
                  "packed_reference_count": 0,
                  "gdie_ref_count": 0,
                  "total_packed_ref_count": 0,
                  "referenced_in_packed": true
                }
              ],
              "embedded_meshes": [],
              "videos": [],
              "language_rows": [],
              "goodies": []
            }
            """);
        string expectedCatalogSha256 = Sha256Hex(catalogPath);
        string outputPath = Path.Combine(outputDir, "aquila-two-kind-plan.json");

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-mod-project-planner");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot(),
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "assets";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_ASSET_CATALOG"] = catalogDir;

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);

            string loadStatus = WaitForNameContainsValue(
                window,
                "AssetCatalogStatus",
                TimeSpan.FromSeconds(30),
                value => value.Contains("Catalog loaded", StringComparison.OrdinalIgnoreCase));
            Assert.That(loadStatus, Does.Contain("Catalog loaded"));

            InvokeByAutomationId(window, "AssetAddCurrentToModProjectButton");
            WaitForNameContainsValue(
                window,
                "AssetModProjectSummary",
                TimeSpan.FromSeconds(30),
                value => value.Contains("1 selected", StringComparison.OrdinalIgnoreCase));

            InvokeByAutomationId(window, "AssetMeshesTabButton");
            WaitForNameContainsValue(
                window,
                "AssetSelectedTitle",
                TimeSpan.FromSeconds(20),
                value => value.Contains("ship_body", StringComparison.OrdinalIgnoreCase));
            InvokeByAutomationId(window, "AssetAddCurrentToModProjectButton");

            string summary = WaitForNameContainsValue(
                window,
                "AssetModProjectSummary",
                TimeSpan.FromSeconds(30),
                value => value.Contains("2 selected", StringComparison.OrdinalIgnoreCase));
            Assert.That(summary, Does.Contain("1 texture"));
            Assert.That(summary, Does.Contain("1 loose mesh"));
            string provenance = RequireName(window, "AssetModProjectProvenance");
            Assert.That(provenance, Does.Contain(expectedCatalogSha256));
            Assert.That(provenance, Does.Contain("bundle-root-relative"));

            SetTextBox(window, "AssetModProjectOutputFileTextBox", outputPath);
            InvokeByAutomationId(window, "AssetExportModProjectPlanButton");
            string exportStatus = WaitForNameContainsValue(
                window,
                "AssetModProjectStatus",
                TimeSpan.FromSeconds(30),
                value => value.Contains("No game assets were copied", StringComparison.OrdinalIgnoreCase) ||
                         value.Contains("could not be written", StringComparison.OrdinalIgnoreCase));
            Assert.That(exportStatus, Does.Contain("No game assets were copied"));

            Assert.That(File.Exists(outputPath), Is.True, "The chosen JSON receipt should exist.");
            string tsvPath = Path.ChangeExtension(outputPath, ".tsv");
            Assert.That(File.Exists(tsvPath), Is.True, "The optional TSV should be beside the JSON receipt.");
            using JsonDocument document = JsonDocument.Parse(File.ReadAllBytes(outputPath));
            JsonElement root = document.RootElement;
            Assert.That(root.GetProperty("manifestVersion").GetString(), Is.EqualTo("mod-project-plan.v1"));
            Assert.That(root.GetProperty("catalogFileName").GetString(), Is.EqualTo("catalog.json"));
            Assert.That(root.GetProperty("catalogSchemaVersion").GetInt32(), Is.EqualTo(2));
            Assert.That(root.GetProperty("catalogPathContract").GetString(), Is.EqualTo("bundle-root-relative"));
            Assert.That(root.GetProperty("catalogSha256").GetString(), Is.EqualTo(expectedCatalogSha256));
            JsonElement[] assets = root.GetProperty("assets").EnumerateArray().ToArray();
            Assert.That(assets, Has.Length.EqualTo(2));
            Assert.That(assets.Select(asset => asset.GetProperty("kind").GetString()),
                Is.EquivalentTo(new[] { "texture", "mesh" }));
            Assert.That(assets.Select(asset => asset.GetProperty("catalogId").GetString()),
                Is.EquivalentTo(new[] { "texture:textures/texture_one.tga", "mesh:ship_body.msh" }));

            string[] outputFiles = Directory.GetFiles(outputDir);
            Assert.That(outputFiles.Select(Path.GetExtension), Is.EquivalentTo(new[] { ".json", ".tsv" }));
            Assert.That(outputFiles, Has.None.Matches<string>(path =>
                string.Equals(Path.GetExtension(path), ".png", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(Path.GetExtension(path), ".fbx", StringComparison.OrdinalIgnoreCase)));
            Assert.That(File.Exists(texturePath), Is.True);
            Assert.That(File.Exists(meshPath), Is.True);
            string json = File.ReadAllText(outputPath);
            Assert.That(json, Does.Not.Contain(scratchRoot));
            Assert.That(json, Does.Contain("not an asset pack"));

            CaptureScreenshot(window, evidenceDir, "01-mod-project-plan-exported.png");
            app.Close();
            app = null;
        }
        finally
        {
            try
            {
                Directory.Delete(scratchRoot, recursive: true);
            }
            catch
            {
            }

            app?.Kill();
        }
    }

    private static string Sha256Hex(string path)
    {
        using FileStream stream = File.OpenRead(path);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox textBox = FindByAutomationId(window, automationId).AsTextBox();
        Assert.That(textBox.Patterns.Value.IsSupported, Is.True);
        textBox.Patterns.Value.Pattern.SetValue(text);
        Assert.That(Retry.WhileFalse(
            () => string.Equals(textBox.Patterns.Value.Pattern.Value.Value, text, StringComparison.Ordinal),
            TimeSpan.FromSeconds(5)).Success, Is.True);
    }

    private static void InvokeByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
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
        return Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));
    }
}
