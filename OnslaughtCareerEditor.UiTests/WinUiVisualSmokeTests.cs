using System;
using System.Buffers.Binary;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.Json;
using System.Threading;
using FlaUI.Core;
using FlaUI.Core.AutomationElements;
using FlaUI.Core.Tools;
using FlaUI.UIA3;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiVisualSmokeTests
{
    private const int DefaultCaptureWidth = 1000;
    private const int DefaultCaptureHeight = 640;
    private const string PrimaryVisualQaDate = "2026-05-27";
    private const string ScrolledVisualQaDate = "2026-05-27";
    private static readonly IntPtr HwndTop = IntPtr.Zero;
    private const uint SwpShowWindow = 0x0040;
    private const int SwMaximize = 3;

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app on the desktop and captures ignored screenshots under .artifacts/.")]
    [Apartment(ApartmentState.STA)]
    public void MainWindow_CapturesPrimaryProductScreens()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-visual-qa", PrimaryVisualQaDate);
        Directory.CreateDirectory(evidenceDir);
        foreach (string oldScreenshot in Directory.GetFiles(evidenceDir, "*.png"))
        {
            File.Delete(oldScreenshot);
        }

        CaptureConfiguredTab(exePath, evidenceDir, "01-home.png", initialTag: "home", expectedText: "Start Here");
        CaptureConfiguredTab(exePath, evidenceDir, "02-save-lab.png", initialTag: "saves", expectedText: "1. Inspect a file", initialSaveSubTab: 0);
        CaptureConfiguredTab(exePath, evidenceDir, "03-media-audio.png", initialTag: "media", expectedText: "Source folder", settleMilliseconds: 10_000, initialMediaSubTab: 0);
        CaptureConfiguredTab(exePath, evidenceDir, "04-media-video.png", initialTag: "media", expectedText: "Video library", settleMilliseconds: 10_000, initialMediaSubTab: 1);
        string assetCatalogFixture = PrepareAssetCatalogFixture(evidenceDir);
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "05-asset-library-texture.png",
            initialTag: "assets",
            expectedText: "1 textures, 1 loose meshes, 1 embedded meshes, 1 goodies",
            assetCatalogPath: assetCatalogFixture,
            initialAssetSubTab: 0);
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "06-asset-library-model.png",
            initialTag: "assets",
            expectedText: "Model facts",
            assetCatalogPath: assetCatalogFixture,
            initialAssetSubTab: 1);
        string goodieSaveFixture = PrepareGoodieSaveFixture(evidenceDir);
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "07-asset-library-goodies.png",
            initialTag: "assets",
            expectedText: "Goodie 008 - BE:A Unit-00 'Prototype'",
            assetCatalogPath: assetCatalogFixture,
            initialAssetSubTab: 3,
            goodieSavePath: goodieSaveFixture,
            assertWindow: window =>
            {
                string summary = TryGetName(FindByAutomationId(window, "AssetSelectedSummary")) ?? string.Empty;
                Assert.That(summary, Does.Contain("save state: new"));
                string filterStatus = TryGetName(FindByAutomationId(window, "AssetGoodiesFilterStatus")) ?? string.Empty;
                Assert.That(filterStatus, Does.Contain("1 cataloged Goodies"));
            });
        CaptureConfiguredTab(exePath, evidenceDir, "08-lore.png", initialTag: "lore", expectedText: "Library", settleMilliseconds: 4_000);
        CaptureConfiguredTab(exePath, evidenceDir, "09-patch-bench.png", initialTag: "binary", expectedText: "Safe game copy");
        CaptureConfiguredTab(exePath, evidenceDir, "10-settings.png", initialTag: "settings", expectedText: "Game Directory");
        CaptureConfiguredTab(exePath, evidenceDir, "11-about.png", initialTag: "about", expectedText: "About Onslaught Toolkit");

        string[] screenshots = Directory.GetFiles(evidenceDir, "*.png");
        Assert.That(screenshots.Select(Path.GetFileName), Is.EquivalentTo(new[]
        {
                "01-home.png",
                "02-save-lab.png",
                "03-media-audio.png",
                "04-media-video.png",
                "05-asset-library-texture.png",
                "06-asset-library-model.png",
                "07-asset-library-goodies.png",
                "08-lore.png",
                "09-patch-bench.png",
                "10-settings.png",
                "11-about.png",
            }));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app and captures ignored screenshots after scrolling long workflow pages under .artifacts/.")]
    [Apartment(ApartmentState.STA)]
    public void MainWindow_CapturesScrolledWorkflowSections()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-scrolled-visual-qa", ScrolledVisualQaDate);
        Directory.CreateDirectory(evidenceDir);
        foreach (string oldScreenshot in Directory.GetFiles(evidenceDir, "*.png"))
        {
            File.Delete(oldScreenshot);
        }

        string assetCatalogFixture = PrepareAssetCatalogFixture(evidenceDir);
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "01-home-scrolled.png",
            initialTag: "home",
            expectedText: "Open About",
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "HomeOpenAboutButton"));
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "02-save-editor-scrolled.png",
            initialTag: "saves",
            expectedText: "Patch output",
            initialSaveSubTab: 1,
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "SaveEditorOutputLog"));
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "03-configuration-editor-scrolled.png",
            initialTag: "saves",
            expectedText: "Patch output",
            initialSaveSubTab: 2,
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "ConfigurationOutputLog"));
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "04-asset-preview-scrolled.png",
            initialTag: "assets",
            expectedText: "Copy path",
            initialAssetSubTab: 0,
            assetCatalogPath: assetCatalogFixture,
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "AssetCopyExportPathButton"));
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "05-patch-bench-scrolled.png",
            initialTag: "binary",
            expectedText: "Last operation",
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "PatchBenchOperationLog"));
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "06-settings-scrolled.png",
            initialTag: "settings",
            expectedText: "Settings file details",
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "SettingsReloadButton"));
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "07-about-scrolled.png",
            initialTag: "about",
            expectedText: "Version",
            beforeCapture: window => ScrollIntoViewByAutomationId(window, "AboutVersionText"));

        string[] screenshots = Directory.GetFiles(evidenceDir, "*.png");
        Assert.That(screenshots.Select(Path.GetFileName), Is.EquivalentTo(new[]
        {
                "01-home-scrolled.png",
                "02-save-editor-scrolled.png",
                "03-configuration-editor-scrolled.png",
                "04-asset-preview-scrolled.png",
                "05-patch-bench-scrolled.png",
                "06-settings-scrolled.png",
                "07-about-scrolled.png",
            }));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Requires a private generated asset catalog path in ONSLAUGHT_WINUI_REAL_ASSET_CATALOG and captures ignored screenshots under .artifacts/.")]
    [Apartment(ApartmentState.STA)]
    public void AssetLibrary_CapturesRealTexturePreviewWhenCatalogProvided()
    {
        string? assetCatalogPath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_CATALOG");
        if (string.IsNullOrWhiteSpace(assetCatalogPath) || !File.Exists(assetCatalogPath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_ASSET_CATALOG to a generated private catalog.json to run this visual smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-real-asset-visual-qa");
        Directory.CreateDirectory(evidenceDir);
        string searchText = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_TEXTURE_SEARCH") ?? "f_trooperd";
        string expectedText = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_TEXTURE_EXPECTED") ?? "F Trooperd";
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "asset-library-real-texture.png",
            initialTag: "assets",
            expectedText: expectedText,
            settleMilliseconds: 6_000,
            initialAssetSubTab: 0,
            assetCatalogPath: assetCatalogPath,
            assetSearchText: searchText);
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Requires a private generated asset catalog path in ONSLAUGHT_WINUI_REAL_ASSET_CATALOG and captures ignored screenshots under .artifacts/.")]
    [Apartment(ApartmentState.STA)]
    public void AssetLibrary_CapturesRealModelWireframeWhenCatalogProvided()
    {
        string? assetCatalogPath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_CATALOG");
        if (string.IsNullOrWhiteSpace(assetCatalogPath) || !File.Exists(assetCatalogPath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_ASSET_CATALOG to a generated private catalog.json to run this visual smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-real-asset-visual-qa");
        Directory.CreateDirectory(evidenceDir);
        string searchText = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_MODEL_SEARCH") ?? "arachnid";
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "asset-library-real-model.png",
            initialTag: "assets",
            expectedText: "Model facts",
            settleMilliseconds: 6_000,
            initialAssetSubTab: 1,
            assetCatalogPath: assetCatalogPath,
            assetSearchText: searchText,
            assertWindow: window =>
            {
                string wireframeStatus = TryGetName(FindByAutomationId(window, "AssetModelWireframeStatus")) ?? string.Empty;
                Assert.That(wireframeStatus, Does.Contain("Wireframe preview available"));
                string metadata = TryGetName(FindByAutomationId(window, "AssetModelMetadataInline")) ?? string.Empty;
                Assert.That(metadata, Does.Contain("vertices"));
                Assert.That(metadata, Does.Contain("polygon index entries"));
            });
    }

    [Test]
    [Category("WinUIRuntime")]
    [Description("Captures ignored screenshots for representative full-install Goodies model, artwork, and video rows.")]
    [Apartment(ApartmentState.STA)]
    public void AssetLibrary_CapturesRealGoodiesBrowserWhenCatalogProvided()
    {
        string? assetCatalogPath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_CATALOG");
        if (string.IsNullOrWhiteSpace(assetCatalogPath) || !File.Exists(assetCatalogPath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_ASSET_CATALOG to a generated private catalog.json to run this Goodies visual smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-real-asset-visual-qa");
        Directory.CreateDirectory(evidenceDir);

        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "asset-library-real-goodie-model.png",
            initialTag: "assets",
            expectedText: "Goodie model: Goodie 009 - BE:A Unit-01 'Pulsar'",
            settleMilliseconds: 6_000,
            initialAssetSubTab: 3,
            assetCatalogPath: assetCatalogPath,
            assetSearchText: "Pulsar",
            assertWindow: window =>
            {
                string filterStatus = TryGetName(FindByAutomationId(window, "AssetGoodiesFilterStatus")) ?? string.Empty;
                Assert.That(filterStatus, Does.Contain("cataloged Goodies"));
                AssertGoodieModelSelection(window, "Pulsar", "BE:A Unit-01 'Pulsar'");
                string rewardFact = TryGetName(FindByAutomationId(window, "AssetGoodieFactReward")) ?? string.Empty;
                Assert.That(rewardFact, Does.Contain("model link"));
            });

        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "asset-library-real-goodie-artwork.png",
            initialTag: "assets",
            expectedText: "Goodie artwork: Goodie 071 - All Configurations",
            settleMilliseconds: 6_000,
            initialAssetSubTab: 3,
            assetCatalogPath: assetCatalogPath,
            assetSearchText: "All Configurations",
            assertWindow: window =>
            {
                AssertGoodieArtworkSelection(window, "All Configurations", "Goodie 071 - All Configurations");
                string wallFact = TryGetName(FindByAutomationId(window, "AssetGoodieFactWall")) ?? string.Empty;
                Assert.That(wallFact, Does.Contain("does not expose this slot"));
            });

        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "asset-library-real-goodie-video.png",
            initialTag: "assets",
            expectedText: "Goodie entry: Goodie 077 - Development",
            settleMilliseconds: 6_000,
            initialAssetSubTab: 3,
            assetCatalogPath: assetCatalogPath,
            assetSearchText: "Development",
            assertWindow: window =>
            {
                AssertSelectedTitle(window, "Goodie 077 - Development");
                string summary = TryGetName(FindByAutomationId(window, "AssetSelectedSummary")) ?? string.Empty;
                Assert.That(summary, Does.Contain("linked to cutscene UsTheMovie"));
                string rewardFact = TryGetName(FindByAutomationId(window, "AssetGoodieFactReward")) ?? string.Empty;
                Assert.That(rewardFact, Does.Contain("opens Media"));
                Button exportButton = FindByAutomationId(window, "AssetOpenExportButton").AsButton();
                Assert.That(exportButton.IsEnabled, Is.False, "Video Goodies should not expose a fake export action.");

                Button mediaButton = FindByAutomationId(window, "AssetOpenInMediaButton").AsButton();
                Assert.That(mediaButton.IsEnabled, Is.True, "Video Goodies should offer a direct Media handoff.");
                mediaButton.Invoke();
                Thread.Sleep(1_000);

                TextBox videoSearchBox = FindByAutomationId(window, "MediaVideoSearchBox").AsTextBox();
                Assert.That(
                    Retry.WhileFalse(() => videoSearchBox.Text.Contains("UsTheMovie", StringComparison.OrdinalIgnoreCase), TimeSpan.FromSeconds(10)).Success,
                    Is.True,
                    "The Media handoff should search for the linked video sequence.");
                Assert.That(
                    Retry.WhileFalse(() => (TryGetName(FindByAutomationId(window, "MediaVideoSelected")) ?? string.Empty).Contains("Credits Video", StringComparison.OrdinalIgnoreCase), TimeSpan.FromSeconds(10)).Success,
                    Is.True,
                    "The Media handoff should select the matching human-labeled video row.");
                Assert.That(
                    Retry.WhileFalse(() => (TryGetName(FindByAutomationId(window, "MediaVideoSourceSummary")) ?? string.Empty).Contains("UsTheMovie.vid", StringComparison.OrdinalIgnoreCase), TimeSpan.FromSeconds(10)).Success,
                    Is.True,
                    "The Media handoff should preserve the real Bink source filename in the selected video summary.");
                Capture(window, evidenceDir, "asset-library-real-goodie-video-media-handoff.png", "Credits Video");
            });
    }

    [Test]
    [Category("WinUIRuntime")]
    [Explicit("Launches the current WinUI app with a deterministic fixture catalog to prove sidecar-only model texture preview.")]
    [Apartment(ApartmentState.STA)]
    public void AssetLibrary_PreviewsSidecarTextureWhenOnlySidecarExists()
    {
        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-sidecar-texture-smoke");
        Directory.CreateDirectory(evidenceDir);
        string assetCatalogFixture = PrepareSidecarOnlyAssetCatalogFixture(evidenceDir);
        CaptureConfiguredTab(
            exePath,
            evidenceDir,
            "asset-library-sidecar-texture.png",
            initialTag: "assets",
            expectedText: "Sidecar texture preview: orphan_sidecar.png",
            settleMilliseconds: 1_000,
            initialAssetSubTab: 1,
            assetCatalogPath: assetCatalogFixture,
            assetSearchText: "sidecar_only",
            beforeCapture: window => AssertSidecarTexturePreview(
                window,
                searchText: "sidecar_only",
                expectedTitle: "sidecar_only_mesh.msh",
                expectedFileName: "orphan_sidecar.png"));
    }

    [Test]
    [Category("WinUIRuntime")]
    [Apartment(ApartmentState.STA)]
    public void AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided()
    {
        string? assetCatalogPath = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_REAL_ASSET_CATALOG");
        if (string.IsNullOrWhiteSpace(assetCatalogPath) || !File.Exists(assetCatalogPath))
        {
            Assert.Ignore("Set ONSLAUGHT_WINUI_REAL_ASSET_CATALOG to a generated private catalog.json to run this Asset Library breadth smoke.");
        }

        string exePath = ResolveWinUiAppPath();
        if (!File.Exists(exePath))
        {
            Assert.Ignore($"Build output not found at: {exePath}. Run the WinUI build first.");
        }

        string evidenceDir = Path.Combine(ResolveRepoRoot(), ".artifacts", "winui-real-asset-row-breadth");
        Directory.CreateDirectory(evidenceDir);
        string appDataDir = PrepareIsolatedAppData(evidenceDir, "asset-library-row-breadth");
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = "assets";
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_ASSET_CATALOG"] = assetCatalogPath;

        var proof = new
        {
            generatedAt = DateTimeOffset.UtcNow,
            catalog = new { fileName = Path.GetFileName(assetCatalogPath) },
            textureSamples = new[]
            {
                new { search = "cloud", expectedTitle = "Cloud" },
                new { search = "ca_boss_warspite", expectedTitle = "Ca Boss Warspite" },
                new { search = "f_trooperd", expectedTitle = "F Trooperd" },
                new { search = "A8_bluegunlight", expectedTitle = "A8 Bluegunlight Lit" }
            },
            looseMeshSamples = new[]
            {
                new { search = "arachnid", expectedTitle = "arachnid.msh" },
                new { search = "boss-warspite", expectedTitle = "boss-warspite.msh" },
                new { search = "gill-m-head", expectedTitle = "boss_gill-m-head.msh" },
                new { search = "battletank", expectedTitle = "f_battletank.msh" }
            },
            embeddedMeshSamples = new[]
            {
                new { search = "body00", expectedTitle = "body00" }
            },
            goodieSamples = new[]
            {
                new { search = "Pulsar", expectedTitle = "BE:A Unit-01 'Pulsar'", expectedPreview = "model wireframe" },
                new { search = "Sniper", expectedTitle = "BE:A Unit-04S 'Sniper'", expectedPreview = "model wireframe" }
            },
            hiddenGoodieArtworkSamples = new[]
            {
                new { search = "All Configurations", expectedTitle = "Goodie 071 - All Configurations" },
                new { search = "Free Camera Mode", expectedTitle = "Goodie 072 - Free Camera Mode" },
                new { search = "God Mode", expectedTitle = "Goodie 073 - God Mode" }
            }
        };

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            Assert.That(
                Retry.WhileFalse(() => (TryGetName(FindByAutomationId(window, "AssetCatalogSummary")) ?? string.Empty).Contains("828 textures", StringComparison.OrdinalIgnoreCase), TimeSpan.FromSeconds(15)).Success,
                Is.True,
                "Expected the generated full-corpus asset catalog summary.");
            string coverageSummary = TryGetName(FindByAutomationId(window, "AssetCatalogCoverageSummary")) ?? string.Empty;
            Assert.That(coverageSummary, Does.Contain("Real local extraction"));
            Assert.That(coverageSummary, Does.Contain("352/352 model rows have direct catalog texture links"));
            Assert.That(coverageSummary, Does.Contain("352/352 model rows report material slots"));
            Assert.That(coverageSummary, Does.Contain("352/352 material import dry-run model operations ready"));
            Assert.That(coverageSummary, Does.Contain("1268/1268 material import dry-run texture operations resolved"));
            Assert.That(coverageSummary, Does.Contain("194/194 texture Goodies preview-ready"));
            Assert.That(coverageSummary, Does.Contain("45/45 model Goodies wireframe-ready"));
            Assert.That(coverageSummary, Does.Contain("wireframe/export-based"));
            string provenanceSummary = TryGetName(FindByAutomationId(window, "AssetCatalogProvenanceSummary")) ?? string.Empty;
            Assert.That(provenanceSummary, Does.Contain("broad PC-install export from local game files"));
            Assert.That(provenanceSummary, Does.Contain("not source-tree sample data"));
            Assert.That(provenanceSummary, Does.Contain("Private assets stay local"));
            Assert.That(provenanceSummary, Does.Contain("runtime Goodies behavior is separate proof"));

            foreach (var sample in proof.textureSamples)
            {
                AssertTextureSelection(window, sample.search, sample.expectedTitle);
            }

            InvokeButton(window, "AssetMeshesTabButton");
            bool checkedLinkedTextureHandoff = false;
            foreach (var sample in proof.looseMeshSamples)
            {
                AssertModelSelection(window, sample.search, sample.expectedTitle);
                if (!checkedLinkedTextureHandoff)
                {
                    AssertLinkedTextureHandoff(window);
                    InvokeButton(window, "AssetMeshesTabButton");
                    checkedLinkedTextureHandoff = true;
                }
            }

            InvokeButton(window, "AssetEmbeddedMeshesTabButton");
            foreach (var sample in proof.embeddedMeshSamples)
            {
                AssertModelSelection(window, sample.search, sample.expectedTitle);
            }

            InvokeButton(window, "AssetGoodiesTabButton");
            InvokeButton(window, "AssetGoodiesModelsFilterButton");
            string modelFilterStatus = TryGetName(FindByAutomationId(window, "AssetGoodiesFilterStatus")) ?? string.Empty;
            Assert.That(modelFilterStatus, Does.Contain("model Goodies"));
            foreach (var sample in proof.goodieSamples)
            {
                AssertGoodieModelSelection(window, sample.search, sample.expectedTitle);
            }

            InvokeButton(window, "AssetGoodiesHiddenFilterButton");
            string hiddenFilterStatus = TryGetName(FindByAutomationId(window, "AssetGoodiesFilterStatus")) ?? string.Empty;
            Assert.That(hiddenFilterStatus, Does.Contain("not runtime reachability"));
            foreach (var sample in proof.hiddenGoodieArtworkSamples)
            {
                AssertGoodieArtworkSelection(window, sample.search, sample.expectedTitle);
            }

            File.WriteAllText(
                Path.Combine(evidenceDir, "asset-library-row-breadth.json"),
                JsonSerializer.Serialize(proof, new JsonSerializerOptions { WriteIndented = true }));
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

    private static void CaptureConfiguredTab(
        string exePath,
        string evidenceDir,
        string fileName,
        string initialTag,
        string expectedText,
        int settleMilliseconds = 750,
        int? initialSaveSubTab = null,
        int? initialMediaSubTab = null,
        int? initialAssetSubTab = null,
        string? assetCatalogPath = null,
        string? goodieSavePath = null,
        string? assetSearchText = null,
        Action<Window>? beforeCapture = null,
        Action<Window>? assertWindow = null)
    {
        string appDataDir = PrepareIsolatedAppData(evidenceDir, fileName);
        var startInfo = new ProcessStartInfo(exePath)
        {
            WorkingDirectory = Path.GetDirectoryName(exePath) ?? ResolveRepoRoot()
        };
        startInfo.Environment["APPDATA"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_APP_CONFIG_ROOT"] = appDataDir;
        startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_TAG"] = initialTag;
        if (initialSaveSubTab.HasValue)
        {
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_SAVE_TAB"] = initialSaveSubTab.Value.ToString();
        }
        if (initialMediaSubTab.HasValue)
        {
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"] = initialMediaSubTab.Value.ToString();
        }
        if (initialAssetSubTab.HasValue)
        {
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_INITIAL_ASSET_TAB"] = initialAssetSubTab.Value.ToString();
        }
        if (!string.IsNullOrWhiteSpace(assetCatalogPath))
        {
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_ASSET_CATALOG"] = assetCatalogPath;
        }
        if (!string.IsNullOrWhiteSpace(goodieSavePath))
        {
            startInfo.Environment["ONSLAUGHT_WINUI_TEST_GOODIE_SAVE"] = goodieSavePath;
        }

        Application? app = null;
        try
        {
            app = Application.Launch(startInfo);
            using var automation = new UIA3Automation();
            Window window = WaitForMainWindow(app, automation);
            NormalizeWindowForCapture(app.MainWindowHandle);

            if (!string.IsNullOrWhiteSpace(assetSearchText))
            {
                Thread.Sleep(1_500);
                SetTextBox(window, "AssetSearchBox", assetSearchText);
            }

            Thread.Sleep(settleMilliseconds);
            beforeCapture?.Invoke(window);
            Capture(window, evidenceDir, fileName, expectedText);
            bool pageReady = Retry.WhileFalse(
                () => window.FindFirstDescendant(cf => cf.ByText(expectedText)) is not null,
                TimeSpan.FromSeconds(2)).Success;
            Assert.That(pageReady, Is.True, $"Expected visible page text: {expectedText}");
            assertWindow?.Invoke(window);
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

    private static void SetTextBox(Window window, string automationId, string text)
    {
        TextBox? textBox = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByAutomationId(automationId))?.AsTextBox(),
            TimeSpan.FromSeconds(5)).Result;
        Assert.That(textBox, Is.Not.Null, $"Expected text box with automation id: {automationId}");
        textBox!.Text = text;
    }

    private static AutomationElement FindByAutomationId(Window window, string automationId)
    {
        AutomationElement? element = Retry.WhileNull(
            () => TryFindByAutomationId(window, automationId),
            TimeSpan.FromSeconds(10)).Result;
        Assert.That(element, Is.Not.Null, $"Expected automation element: {automationId}");
        return element!;
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

    private static void ScrollIntoViewByAutomationId(Window window, string automationId)
    {
        AutomationElement element = FindByAutomationId(window, automationId);
        try
        {
            if (element.Patterns.ScrollItem.IsSupported)
            {
                element.Patterns.ScrollItem.Pattern.ScrollIntoView();
                Thread.Sleep(350);
                return;
            }
        }
        catch
        {
            // Some static WinUI elements expose names/ids but not ScrollItem; focus is a safe fallback.
        }

        try
        {
            element.Focus();
        }
        catch
        {
            // Capture still records the current viewport; the assertion above proves the target exists.
        }

        Thread.Sleep(350);
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

    private static void InvokeButton(Window window, string automationId)
    {
        Button? button = Retry.WhileNull(
            () => window.FindFirstDescendant(cf => cf.ByAutomationId(automationId))?.AsButton(),
            TimeSpan.FromSeconds(5)).Result;
        Assert.That(button, Is.Not.Null, $"Expected button with automation id: {automationId}");
        button!.Invoke();
        Thread.Sleep(750);
    }

    private static void AssertTextureSelection(Window window, string searchText, string expectedTitle)
    {
        SetTextBox(window, "AssetSearchBox", searchText);
        AssertSelectedTitle(window, expectedTitle);
        string summary = TryGetName(FindByAutomationId(window, "AssetSelectedSummary")) ?? string.Empty;
        Assert.That(summary, Does.Contain("export available"));
        Button openButton = FindByAutomationId(window, "AssetOpenExportButton").AsButton();
        Assert.That(openButton.IsEnabled, Is.True, $"Expected texture export action to be enabled for {expectedTitle}.");
    }

    private static void AssertModelSelection(Window window, string searchText, string expectedTitle)
    {
        SetTextBox(window, "AssetSearchBox", searchText);
        AssertSelectedTitle(window, expectedTitle);
        string wireframeStatus = TryGetName(FindByAutomationId(window, "AssetModelWireframeStatus")) ?? string.Empty;
        Assert.That(wireframeStatus, Does.Contain("Wireframe preview available"));
        string metadata = TryGetName(FindByAutomationId(window, "AssetModelMetadataInline")) ?? string.Empty;
        Assert.That(metadata, Does.Contain("vertices"));
        Assert.That(metadata, Does.Contain("polygon index entries"));
        string textureLinks = TryGetName(FindByAutomationId(window, "AssetModelTextureLinks")) ?? string.Empty;
        Assert.That(textureLinks, Does.Contain("direct catalog texture link"));
        Assert.That(textureLinks, Does.Contain("Sidecar preview files"));
        string packagePlan = TryGetName(FindByAutomationId(window, "AssetModelPackagePlan")) ?? string.Empty;
        Assert.That(packagePlan, Does.Contain("Material package plan: ready"));
        Assert.That(packagePlan, Does.Contain("model destination models/"));
        Assert.That(packagePlan, Does.Contain("texture references resolved"));
        Assert.That(packagePlan, Does.Contain("Texture destinations: textures/catalog/"));
        Button openButton = FindByAutomationId(window, "AssetOpenExportButton").AsButton();
        Assert.That(openButton.IsEnabled, Is.True, $"Expected model export action to be enabled for {expectedTitle}.");
    }

    private static void AssertLinkedTextureHandoff(Window window)
    {
        Button linkedTextureButton = FindByAutomationId(window, "AssetViewLinkedTextureButton").AsButton();
        Assert.That(linkedTextureButton.IsEnabled, Is.True, "Expected a selected model with matched texture links to offer a texture handoff.");
        linkedTextureButton.Invoke();
        Thread.Sleep(750);

        string title = TryGetName(FindByAutomationId(window, "AssetSelectedTitle")) ?? string.Empty;
        Assert.That(title, Does.Not.Contain(".msh"));
        string summary = TryGetName(FindByAutomationId(window, "AssetSelectedSummary")) ?? string.Empty;
        Assert.That(summary, Does.Contain("export available"));
        _ = FindByAutomationId(window, "AssetTexturePreviewImage");
    }

    private static void AssertSidecarTexturePreview(
        Window window,
        string searchText,
        string expectedTitle,
        string expectedFileName)
    {
        SetTextBox(window, "AssetSearchBox", searchText);
        AssertSelectedTitle(window, expectedTitle);
        string textureLinks = TryGetName(FindByAutomationId(window, "AssetModelTextureLinks")) ?? string.Empty;
        Assert.That(textureLinks, Does.Contain("none are direct catalog rows"));
        Assert.That(textureLinks, Does.Contain("Sidecar preview files: 1/1"));

        AutomationElement sidecarButtonElement = FindByAutomationId(window, "AssetViewLinkedTextureButton");
        Button sidecarButton = sidecarButtonElement.AsButton();
        Assert.That(sidecarButton.IsEnabled, Is.True, "Expected a sidecar-only model to offer a sidecar texture preview.");
        Assert.That(TryGetName(sidecarButtonElement) ?? string.Empty, Does.Contain("Preview sidecar texture"));
        sidecarButton.Invoke();
        Thread.Sleep(750);

        _ = FindByAutomationId(window, "AssetTexturePreviewImage");
        string previewTitle = TryGetName(FindByAutomationId(window, "AssetPreviewTitle")) ?? string.Empty;
        Assert.That(previewTitle, Does.Contain("Sidecar texture preview"));
        Assert.That(previewTitle, Does.Contain(expectedFileName));
    }

    private static void AssertGoodieModelSelection(Window window, string searchText, string expectedTitle)
    {
        SetTextBox(window, "AssetSearchBox", searchText);
        AssertSelectedTitle(window, expectedTitle);
        string summary = TryGetName(FindByAutomationId(window, "AssetSelectedSummary")) ?? string.Empty;
        Assert.That(summary, Does.Contain("matched to an extracted model export"));
        string wireframeStatus = TryGetName(FindByAutomationId(window, "AssetModelWireframeStatus")) ?? string.Empty;
        Assert.That(wireframeStatus, Does.Contain("Wireframe preview available"));
        string metadata = TryGetName(FindByAutomationId(window, "AssetModelMetadataInline")) ?? string.Empty;
        Assert.That(metadata, Does.Contain("vertices"));
        Assert.That(metadata, Does.Contain("polygon index entries"));
    }

    private static void AssertGoodieArtworkSelection(Window window, string searchText, string expectedTitle)
    {
        SetTextBox(window, "AssetSearchBox", searchText);
        AssertSelectedTitle(window, expectedTitle);
        string summary = TryGetName(FindByAutomationId(window, "AssetSelectedSummary")) ?? string.Empty;
        Assert.That(summary, Does.Contain("matched to an extracted artwork export"));
        _ = FindByAutomationId(window, "AssetTexturePreviewImage");
        Button openButton = FindByAutomationId(window, "AssetOpenExportButton").AsButton();
        Assert.That(openButton.IsEnabled, Is.True, $"Expected hidden goodie artwork export action to be enabled for {expectedTitle}.");
    }

    private static void AssertSelectedTitle(Window window, string expectedTitle)
    {
        bool selected = Retry.WhileFalse(
            () => (TryGetName(FindByAutomationId(window, "AssetSelectedTitle")) ?? string.Empty).Contains(expectedTitle, StringComparison.OrdinalIgnoreCase),
            TimeSpan.FromSeconds(8)).Success;
        Assert.That(selected, Is.True, $"Expected selected asset title to contain: {expectedTitle}");
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
        NormalizeWindowForCapture(app.MainWindowHandle);
        return window!;
    }

    private static void NormalizeWindowForCapture(IntPtr windowHandle)
    {
        if (windowHandle == IntPtr.Zero)
        {
            return;
        }

        if (ShouldMaximizeForVisualCapture())
        {
            _ = ShowWindow(windowHandle, SwMaximize);
            _ = SetForegroundWindow(windowHandle);
            Thread.Sleep(500);
            return;
        }

        int width = ReadPositiveIntEnvironment("ONSLAUGHT_WINUI_VISUAL_CAPTURE_WIDTH", DefaultCaptureWidth);
        int height = ReadPositiveIntEnvironment("ONSLAUGHT_WINUI_VISUAL_CAPTURE_HEIGHT", DefaultCaptureHeight);
        _ = SetWindowPos(windowHandle, HwndTop, 16, 16, width, height, SwpShowWindow);
        _ = SetForegroundWindow(windowHandle);
        Thread.Sleep(350);
    }

    private static bool ShouldMaximizeForVisualCapture()
    {
        string? value = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_VISUAL_CAPTURE_MAXIMIZE");
        return !string.Equals(value, "0", StringComparison.OrdinalIgnoreCase) &&
               !string.Equals(value, "false", StringComparison.OrdinalIgnoreCase);
    }

    private static int ReadPositiveIntEnvironment(string name, int fallback)
    {
        string? value = Environment.GetEnvironmentVariable(name);
        return int.TryParse(value, out int parsed) && parsed > 0 ? parsed : fallback;
    }

    private static void Capture(Window window, string evidenceDir, string fileName, string label)
    {
        string outputPath = Path.Combine(evidenceDir, fileName);
        const int maxCaptureAttempts = 4;
        bool renderedCaptureSaved = false;
        for (int attempt = 1; attempt <= maxCaptureAttempts; attempt++)
        {
            window.Focus();
            Thread.Sleep(attempt == 1 ? 350 : 750);
            using FlaUI.Core.Capturing.CaptureImage capture = FlaUI.Core.Capturing.Capture.Element(window);
            if (!HasRenderedHeader(capture.Bitmap))
            {
                continue;
            }

            capture.ToFile(outputPath);
            renderedCaptureSaved = true;
            break;
        }

        Assert.That(renderedCaptureSaved, Is.True, $"Screenshot for {label} never produced a fully rendered app header.");
        Assert.That(File.Exists(outputPath), Is.True, $"Expected screenshot for {label}: {outputPath}");
        Assert.That(new FileInfo(outputPath).Length, Is.GreaterThan(10_000), $"Screenshot for {label} should not be empty.");
    }

    private static bool HasRenderedHeader(System.Drawing.Bitmap bitmap)
    {
        if (bitmap.Width < 4 || bitmap.Height < 91)
        {
            return false;
        }

        int renderedSamples = 0;
        foreach (int x in new[] { bitmap.Width / 4, bitmap.Width / 2, bitmap.Width * 3 / 4 })
        {
            foreach (int y in new[] { 50, 70, 90 })
            {
                System.Drawing.Color headerPixel = bitmap.GetPixel(x, y);
                if (headerPixel.A > 240 &&
                    headerPixel.B > headerPixel.R &&
                    headerPixel.R + headerPixel.G + headerPixel.B > 100)
                {
                    renderedSamples++;
                }
            }
        }

        return renderedSamples >= 6;
    }

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint uFlags);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    private static string PrepareIsolatedAppData(string evidenceDir, string fileName)
    {
        string appDataDir = Path.Combine(evidenceDir, "appdata", Path.GetFileNameWithoutExtension(fileName));
        string configDir = Path.Combine(appDataDir, "OnslaughtCareerEditor");
        Directory.CreateDirectory(configDir);
        string? detectedGameDirectory = AppConfig.DetectGameDirectory();
        string gameDirectoryJson = string.IsNullOrWhiteSpace(detectedGameDirectory)
            ? "null"
            : JsonSerializer.Serialize(detectedGameDirectory);
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

    private static string PrepareAssetCatalogFixture(string evidenceDir)
    {
        string root = Path.Combine(evidenceDir, "asset-catalog-fixture");
        string catalogDir = Path.Combine(root, "asset_catalog");
        string exportDir = Path.Combine(root, "exports");
        Directory.CreateDirectory(catalogDir);
        Directory.CreateDirectory(exportDir);
        File.WriteAllBytes(Path.Combine(exportDir, "fixture_texture.png"), new byte[]
        {
            137, 80, 78, 71, 13, 10, 26, 10,
            0, 0, 0, 13, 73, 72, 68, 82,
            0, 0, 0, 1, 0, 0, 0, 1,
            8, 6, 0, 0, 0, 31, 21, 196,
            137, 0, 0, 0, 13, 73, 68, 65,
            84, 120, 156, 99, 248, 207, 192,
            240, 31, 0, 5, 0, 1, 255, 137,
            153, 61, 29, 0, 0, 0, 0, 73,
            69, 78, 68, 174, 66, 96, 130
        });
        byte[] binaryFbx = BuildMinimalBinaryFbx("texture_one.tga");
        File.WriteAllBytes(Path.Combine(exportDir, "fixture_mesh_binary.fbx"), binaryFbx);
        File.WriteAllBytes(Path.Combine(exportDir, "body00_binary.fbx"), binaryFbx);

        string catalogPath = Path.Combine(catalogDir, "catalog.json");
        File.WriteAllText(catalogPath, """
        {
          "schema_version": 2,
          "path_contract": "bundle-root-relative",
          "summary": {
            "texture_catalog_entries": 1,
            "loose_mesh_catalog_entries": 1,
            "embedded_mesh_catalog_entries": 1,
            "video_catalog_entries": 0,
            "language_catalog_entries": 0,
            "goodie_catalog_entries": 1,
            "total_catalog_entries": 4
          },
          "textures": [
            {
              "catalog_id": "texture:fixture/texture_one.tga",
              "kind": "texture",
              "canonical_ref": "fixture/texture_one.tga",
              "source_roots": ["fixture"],
              "export_png_paths": ["exports/fixture_texture.png"],
              "source_aya_count": 1,
              "export_png_count": 1,
              "packed_text_ref_count": 1,
              "gdie_ref_count": 0
            }
          ],
          "loose_meshes": [
            {
              "catalog_id": "mesh:fixture_mesh.msh",
              "kind": "loose_mesh",
              "canonical_ref": "fixture_mesh.msh",
              "export_fbx_paths": ["exports/fixture_mesh_binary.fbx"],
              "source_aya_count": 1,
              "export_fbx_count": 1,
              "packed_reference_count": 1,
              "gdie_ref_count": 0
            }
          ],
          "embedded_meshes": [
            {
              "catalog_id": "embedded_mesh:fixture/body00",
              "kind": "embedded_mesh",
              "source_archive": "fixture",
              "body_name": "body00",
              "export_fbx_path": "exports/body00_binary.fbx"
            }
          ],
          "videos": [],
          "language_rows": [],
          "goodies": [
            {
              "catalog_id": "goodie:008",
              "kind": "goodie",
              "index": 8,
              "display_name": "Goodie 008 - BE:A Unit-00 'Prototype'",
              "content_kind": "Model",
              "source_title": "BE:A Unit-00 'Prototype'",
              "source_archive": "goodie_08_res_PC.aya",
              "gdie_family": "goodie_08_res_PC.aya",
              "texture_refs": ["fixture/texture_one.tga"],
              "mesh_refs": ["fixture_mesh.msh"],
              "primary_texture_ref": "fixture/texture_one.tga",
              "primary_mesh_ref": "fixture_mesh.msh",
              "video_sequence_id": "",
              "video_catalog_id": "",
              "video_relative_path": ""
            }
          ]
        }
        """);
        return catalogPath;
    }

    private static string PrepareSidecarOnlyAssetCatalogFixture(string evidenceDir)
    {
        string root = Path.Combine(evidenceDir, "asset-sidecar-fixture");
        string catalogDir = Path.Combine(root, "asset_catalog");
        string exportDir = Path.Combine(root, "exports");
        string sidecarDir = Path.Combine(exportDir, "MeshTextures");
        Directory.CreateDirectory(catalogDir);
        Directory.CreateDirectory(exportDir);
        Directory.CreateDirectory(sidecarDir);
        File.WriteAllBytes(Path.Combine(sidecarDir, "orphan_sidecar.png"), new byte[]
        {
            137, 80, 78, 71, 13, 10, 26, 10,
            0, 0, 0, 13, 73, 72, 68, 82,
            0, 0, 0, 1, 0, 0, 0, 1,
            8, 6, 0, 0, 0, 31, 21, 196,
            137, 0, 0, 0, 13, 73, 68, 65,
            84, 120, 156, 99, 248, 207, 192,
            240, 31, 0, 5, 0, 1, 255, 137,
            153, 61, 29, 0, 0, 0, 0, 73,
            69, 78, 68, 174, 66, 96, 130
        });
        File.WriteAllBytes(Path.Combine(exportDir, "sidecar_only_mesh_binary.fbx"), BuildMinimalBinaryFbx("orphan_sidecar.tga"));

        string catalogPath = Path.Combine(catalogDir, "catalog.json");
        File.WriteAllText(catalogPath, """
        {
          "schema_version": 2,
          "path_contract": "bundle-root-relative",
          "summary": {
            "texture_catalog_entries": 0,
            "loose_mesh_catalog_entries": 1,
            "embedded_mesh_catalog_entries": 0,
            "video_catalog_entries": 0,
            "language_catalog_entries": 0,
            "goodie_catalog_entries": 0,
            "total_catalog_entries": 1
          },
          "textures": [],
          "loose_meshes": [
            {
              "catalog_id": "mesh:sidecar_only_mesh.msh",
              "kind": "loose_mesh",
              "canonical_ref": "sidecar_only_mesh.msh",
              "export_fbx_paths": ["exports/sidecar_only_mesh_binary.fbx"],
              "source_aya_count": 1,
              "export_fbx_count": 1,
              "packed_reference_count": 1,
              "gdie_ref_count": 0
            }
          ],
          "embedded_meshes": [],
          "videos": [],
          "language_rows": [],
          "goodies": []
        }
        """);
        return catalogPath;
    }

    private static string PrepareGoodieSaveFixture(string evidenceDir)
    {
        string path = Path.Combine(evidenceDir, "asset-goodie-state-fixture.bes");
        byte[] buffer = new byte[BesFilePatcher.EXPECTED_FILE_SIZE];
        BinaryPrimitives.WriteUInt16LittleEndian(buffer.AsSpan(0, 2), BesFilePatcher.VERSION_WORD);
        BinaryPrimitives.WriteUInt32LittleEndian(buffer.AsSpan(0x1F46 + 8 * 4, 4), 2);
        File.WriteAllBytes(path, buffer);
        return path;
    }

    private static byte[] BuildMinimalBinaryFbx(string textureFileName)
    {
        using MemoryStream stream = new();
        using BinaryWriter writer = new(stream, Encoding.ASCII, leaveOpen: true);

        writer.Write(Encoding.ASCII.GetBytes("Kaydara FBX Binary  "));
        writer.Write((byte)0);
        writer.Write((byte)0x1A);
        writer.Write((byte)0);
        writer.Write(7400);
        WriteNode(
            writer,
            "Objects",
            props: [],
            children:
            [
                () => WriteNode(
                    writer,
                    "Geometry",
                    props:
                    [
                        () => WriteLongProperty(writer, 1),
                        () => WriteStringProperty(writer, "Fixture\0\u0001Geometry"),
                        () => WriteStringProperty(writer, "Mesh")
                    ],
                    children:
                    [
                        () => WriteNode(
                            writer,
                            "Vertices",
                            props:
                            [
                                () => WriteDoubleArrayProperty(writer, [0, 0, 0, 1, 0, 0, 0, 1, 0])
                            ],
                            children: []),
                        () => WriteNode(
                            writer,
                            "PolygonVertexIndex",
                            props:
                            [
                                () => WriteIntArrayProperty(writer, [0, 1, -3])
                            ],
                            children: [])
                    ]),
                () => WriteNode(writer, "Model", props: [() => WriteLongProperty(writer, 2), () => WriteStringProperty(writer, "Fixture\0\u0001Model"), () => WriteStringProperty(writer, "Mesh")], children: []),
                () => WriteNode(writer, "Material", props: [() => WriteLongProperty(writer, 3), () => WriteStringProperty(writer, "Material1\0\u0001Material"), () => WriteStringProperty(writer, string.Empty)], children: []),
                () => WriteNode(writer, "Texture", props: [() => WriteLongProperty(writer, 4), () => WriteStringProperty(writer, "base_color_texture\0\u0001Texture"), () => WriteStringProperty(writer, string.Empty), () => WriteStringProperty(writer, textureFileName)], children: [])
            ]);
        WriteSentinel(writer);
        return stream.ToArray();
    }

    private static void WriteNode(BinaryWriter writer, string name, Action[] props, Action[] children)
    {
        long headerPosition = writer.BaseStream.Position;
        writer.Write((uint)0);
        writer.Write((uint)props.Length);
        writer.Write((uint)0);
        writer.Write((byte)name.Length);
        writer.Write(Encoding.ASCII.GetBytes(name));

        long propertyStart = writer.BaseStream.Position;
        foreach (Action prop in props)
        {
            prop();
        }

        long propertyEnd = writer.BaseStream.Position;
        foreach (Action child in children)
        {
            child();
        }

        if (children.Length > 0)
        {
            WriteSentinel(writer);
        }

        long endPosition = writer.BaseStream.Position;
        writer.BaseStream.Position = headerPosition;
        writer.Write((uint)endPosition);
        writer.Write((uint)props.Length);
        writer.Write((uint)(propertyEnd - propertyStart));
        writer.Write((byte)name.Length);
        writer.BaseStream.Position = endPosition;
    }

    private static void WriteLongProperty(BinaryWriter writer, long value)
    {
        writer.Write((byte)'L');
        writer.Write(value);
    }

    private static void WriteStringProperty(BinaryWriter writer, string value)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(value);
        writer.Write((byte)'S');
        writer.Write((uint)bytes.Length);
        writer.Write(bytes);
    }

    private static void WriteDoubleArrayProperty(BinaryWriter writer, double[] values)
    {
        writer.Write((byte)'d');
        writer.Write((uint)values.Length);
        writer.Write((uint)0);
        writer.Write((uint)(values.Length * sizeof(double)));
        foreach (double value in values)
        {
            writer.Write(value);
        }
    }

    private static void WriteIntArrayProperty(BinaryWriter writer, int[] values)
    {
        writer.Write((byte)'i');
        writer.Write((uint)values.Length);
        writer.Write((uint)0);
        writer.Write((uint)(values.Length * sizeof(int)));
        foreach (int value in values)
        {
            writer.Write(value);
        }
    }

    private static void WriteSentinel(BinaryWriter writer)
    {
        writer.Write(new byte[13]);
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
