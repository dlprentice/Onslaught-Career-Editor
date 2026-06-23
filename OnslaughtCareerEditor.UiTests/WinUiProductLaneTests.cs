using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

public class WinUiProductLaneTests
{
    [Test]
    public void AboutPage_DescribesWinUiAsPrimaryProductLane()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "AboutPage.xaml");

        Assert.That(xaml, Does.Contain("primary user-facing Windows product lane"));
        Assert.That(xaml, Does.Contain("Maintainer infrastructure and historical app references remain separate"));
        Assert.That(xaml, Does.Not.Contain("legacy reference"));
        Assert.That(xaml, Does.Not.Contain("active product direction is the Electron workbench"));
    }

    [Test]
    public void HomePage_RoutesPrimaryWinUiTasks()
    {
        string shellXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml");
        string shellCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs");
        string homeXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "HomePage.xaml");

        Assert.That(shellXaml, Does.Contain("HomeNavigationItem"));
        Assert.That(shellCode, Does.Contain("typeof(HomePage)"));
        Assert.That(shellCode, Does.Contain("\"home\" => -1"));
        Assert.That(homeXaml, Does.Contain("Start Here"));
        Assert.That(homeXaml, Does.Contain("Open Save Lab"));
        Assert.That(homeXaml, Does.Contain("Open Media"));
        Assert.That(homeXaml, Does.Contain("Open Asset Library"));
        Assert.That(homeXaml, Does.Contain("Open Lore"));
        Assert.That(homeXaml, Does.Contain("Open Windowed &amp; Mods"));
        Assert.That(homeXaml, Does.Contain("configured game install is treated as source material"));
    }

    [Test]
    public void MainWindow_StartsMaximizedForBroadWorkspace()
    {
        string appCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "App.xaml.cs");
        string shellCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs");

        Assert.That(appCode, Does.Contain("MainWindowInstance.Activate();"));
        Assert.That(appCode, Does.Contain("MainWindowInstance.MaximizeForUserWorkspace();"));
        Assert.That(shellCode, Does.Contain("public void MaximizeForUserWorkspace()"));
        Assert.That(shellCode, Does.Contain("OverlappedPresenter presenter"));
        Assert.That(shellCode, Does.Contain("presenter.Maximize();"));
    }

    [Test]
    public void RuntimeAccessibilitySmoke_MaximizesWindowByDefault()
    {
        string smokeCode = ReadRepoFile("OnslaughtCareerEditor.UiTests", "WinUiRuntimeAccessibilitySmokeTests.cs");

        Assert.That(smokeCode, Does.Contain("MaximizeForRuntimeSmoke(app.MainWindowHandle);"));
        Assert.That(smokeCode, Does.Contain("ONSLAUGHT_WINUI_VISUAL_CAPTURE_MAXIMIZE"));
        Assert.That(smokeCode, Does.Contain("ShowWindow(windowHandle, SwMaximize)"));
        Assert.That(smokeCode, Does.Contain("SetForegroundWindow(windowHandle)"));
    }

    [Test]
    public void AppUnhandledExceptionHandler_LogsWithoutBlanketSwallowingCrashes()
    {
        string appCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "App.xaml.cs");

        Assert.That(appCode, Does.Contain("OnslaughtCareerEditor.WinUI-startup-error.log"));
        Assert.That(appCode, Does.Contain("Unexpected app error."));
        Assert.That(appCode, Does.Not.Contain("Unexpected app error handled"));
        Assert.That(appCode, Does.Not.Contain("e.Handled = true"));
    }

    [Test]
    public void AssetLibrary_IsNativeWinUiCatalogBrowser()
    {
        string shellXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml");
        string shellCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs");
        string assetXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml");
        string assetCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "AssetLibraryPage.xaml.cs");

        Assert.That(shellXaml, Does.Contain("AssetLibraryNavigationItem"));
        Assert.That(shellXaml, Does.Contain("Asset Library"));
        Assert.That(shellCode, Does.Contain("typeof(AssetLibraryPage)"));
        Assert.That(assetXaml, Does.Contain("Asset Library"));
        Assert.That(assetXaml, Does.Contain("Load generated catalog"));
        Assert.That(assetXaml, Does.Contain("AssetCatalogProvenanceSummary"));
        Assert.That(assetXaml, Does.Contain("Texture preview"));
        Assert.That(assetXaml, Does.Contain("AssetPreviewTitle"));
        Assert.That(assetXaml, Does.Contain("AssetGoodiesTabButton"));
        Assert.That(assetXaml, Does.Contain("Goodies"));
        Assert.That(assetXaml, Does.Contain("Save state for Goodies"));
        Assert.That(assetXaml, Does.Contain("AssetGoodieSaveStatePathTextBox"));
        Assert.That(assetXaml, Does.Contain("AssetLoadGoodieSaveStateButton"));
        Assert.That(assetXaml, Does.Contain("Goodie facts"));
        Assert.That(assetXaml, Does.Contain("AssetGoodieFactsPanel"));
        Assert.That(assetXaml, Does.Contain("AssetGoodieFactWall"));
        Assert.That(assetXaml, Does.Contain("AssetGoodieFactUnlock"));
        Assert.That(assetXaml, Does.Contain("Preview background"));
        Assert.That(assetXaml, Does.Contain("TexturePreviewNeutralButton"));
        Assert.That(assetXaml, Does.Contain("Texture shown on a neutral canvas"));
        Assert.That(assetXaml, Does.Contain("Model facts"));
        Assert.That(assetXaml, Does.Contain("AssetModelMetadataPanel"));
        Assert.That(assetXaml, Does.Contain("AssetModelMetadataInline"));
        Assert.That(assetXaml, Does.Contain("AssetModelWireframePanel"));
        Assert.That(assetXaml, Does.Contain("Wireframe is a lightweight geometry check"));
        Assert.That(assetXaml, Does.Contain("Model view"));
        Assert.That(assetXaml, Does.Contain("AssetModelViewFrontButton"));
        Assert.That(assetXaml, Does.Contain("AssetModelViewSideButton"));
        Assert.That(assetXaml, Does.Contain("AssetModelViewTopButton"));
        Assert.That(assetXaml, Does.Contain("AssetModelViewIsoButton"));
        Assert.That(assetXaml, Does.Contain("Polygon index entries"));
        Assert.That(assetXaml, Does.Contain("UV mapping"));
        Assert.That(assetXaml, Does.Contain("AssetModelUvCount"));
        Assert.That(assetXaml, Does.Contain("Material assignment"));
        Assert.That(assetXaml, Does.Contain("AssetModelMaterialLayerCount"));
        Assert.That(assetXaml, Does.Contain("Texture-material links"));
        Assert.That(assetXaml, Does.Contain("AssetModelConnectionCount"));
        Assert.That(assetXaml, Does.Contain("AssetMaterialPackageOutputStatus"));
        Assert.That(assetXaml, Does.Contain("AssetPrepareMaterialPackageButton"));
        Assert.That(assetXaml, Does.Contain("AssetOpenMaterialPackageButton"));
        Assert.That(assetXaml, Does.Contain("AssetCopyMaterialPackagePathButton"));
        Assert.That(assetXaml, Does.Contain("AssetOpenExportButton"));
        Assert.That(assetXaml, Does.Contain("AssetCopyExportPathButton"));
        Assert.That(assetXaml, Does.Contain("Path details"));
        Assert.That(assetCode, Does.Contain("AssetCatalogService"));
        Assert.That(assetCode, Does.Contain("BuildCatalogProvenanceSummary"));
        Assert.That(assetCode, Does.Contain("LooksLikeBroadPcInstallCatalog"));
        Assert.That(assetCode, Does.Contain("broad PC-install export from local game files"));
        Assert.That(assetCode, Does.Contain("not source-tree sample data"));
        Assert.That(assetCode, Does.Contain("runtime Goodies behavior is separate proof"));
        Assert.That(assetCode, Does.Contain("direct catalog texture links"));
        Assert.That(assetCode, Does.Contain("catalog-missing texture binding files have sidecar previews"));
        Assert.That(assetCode, Does.Contain("unresolved material import binding files"));
        Assert.That(assetCode, Does.Contain("Sidecar preview files"));
        Assert.That(assetCode, Does.Contain("AssetMaterialImportPackageRebuildPreviewService"));
        Assert.That(assetCode, Does.Contain("Rebuild preview"));
        Assert.That(assetCode, Does.Contain("rebuild-preview-ready"));
        Assert.That(assetCode, Does.Contain("TextureCoordinateCount"));
        Assert.That(assetCode, Does.Contain("UV mapping"));
        Assert.That(assetCode, Does.Contain("MaterialAssignmentIndexCount"));
        Assert.That(assetCode, Does.Contain("Material assignment"));
        Assert.That(assetCode, Does.Contain("TextureToMaterialConnectionCount"));
        Assert.That(assetCode, Does.Contain("TextureToMaterialSlotNames"));
        Assert.That(assetCode, Does.Contain("RowsWithTextureToMaterialSlotNames"));
        Assert.That(assetCode, Does.Contain("material slots"));
        Assert.That(assetCode, Does.Contain("Texture-material links"));
        Assert.That(assetCode, Does.Contain("PreviewSidecarTexture"));
        Assert.That(assetCode, Does.Contain("BesFilePatcher.AnalyzeSave"));
        Assert.That(assetCode, Does.Contain("GoodieStateDetail"));
        Assert.That(assetCode, Does.Contain("ONSLAUGHT_WINUI_TEST_GOODIE_SAVE"));
        Assert.That(assetCode, Does.Contain("WallGroupLabel"));
        Assert.That(assetCode, Does.Contain("WallPositionLabel"));
        Assert.That(assetCode, Does.Contain("RenderModelSummary"));
        Assert.That(assetCode, Does.Contain("RenderGoodieFacts"));
        Assert.That(assetCode, Does.Contain("BuildGoodieRewardFact"));
        Assert.That(assetCode, Does.Contain("ShowGoodie"));
        Assert.That(assetCode, Does.Contain("FindTexture"));
        Assert.That(assetCode, Does.Contain("FindLooseMesh"));
        Assert.That(assetCode, Does.Contain("RenderWireframe"));
        Assert.That(assetCode, Does.Contain("ModelPreviewView"));
        Assert.That(assetCode, Does.Contain("ProjectModelVertex"));
        Assert.That(assetCode, Does.Contain("TexturePreviewBackground"));
        Assert.That(assetCode, Does.Contain("ApplyTexturePreviewBackground"));
        Assert.That(assetCode, Does.Contain("in-app wireframe"));
        Assert.That(assetCode, Does.Contain("full material review"));
        Assert.That(assetCode, Does.Not.Contain("native 3D preview is planned"));
        Assert.That(assetCode, Does.Not.Contain("Native in-app 3D rendering is not enabled yet"));
        Assert.That(assetCode, Does.Contain("ONSLAUGHT_WINUI_TEST_INITIAL_ASSET_TAB"));
        Assert.That(assetCode, Does.Contain("AssetCatalogPath"));
        Assert.That(assetCode, Does.Contain("AssetMaterialImportPackageMaterializationService"));
        Assert.That(assetCode, Does.Contain("AssetMaterialImportPackageWorkOrderService"));
        Assert.That(assetCode, Does.Contain("AssetMaterialImportPackageImporterBatchService"));
        Assert.That(assetCode, Does.Contain("AssetMaterialImportPackageImporterDryRunService"));
        Assert.That(assetCode, Does.Contain("AssetMaterialImportPackageImporterInputService"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageWorkOrderSummary"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageWorkOrderSidecarSummary"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageImporterBatchSummary"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageImporterDryRunSummary"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageImporterDryRunSidecarValidationSummary"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageImporterInputSummary"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageImporterDryRunSidecarSummary"));
        Assert.That(assetCode, Does.Contain("Importer work order"));
        Assert.That(assetCode, Does.Contain("Work-order sidecar"));
        Assert.That(assetCode, Does.Contain("Importer batch"));
        Assert.That(assetCode, Does.Contain("Importer dry run"));
        Assert.That(assetCode, Does.Contain("Importer dry-run sidecar validation"));
        Assert.That(assetCode, Does.Contain("Importer input"));
        Assert.That(assetCode, Does.Contain("Importer input plan"));
        Assert.That(assetCode, Does.Contain("Importer dry-run sidecar"));
        Assert.That(assetCode, Does.Contain("ready flat tasks"));
        Assert.That(assetCode, Does.Contain("ready flat importer tasks"));
        Assert.That(assetCode, Does.Contain("ready importer dry-run rows"));
        Assert.That(assetCode, Does.Contain("dry-run sidecar validation"));
        Assert.That(assetCode, Does.Contain("importer-input-staged"));
        Assert.That(assetCode, Does.Contain("importer-input-plan-ready"));
        Assert.That(assetCode, Does.Contain("consumer jobs ready"));
        Assert.That(assetCode, Does.Contain("adapter rows ready"));
        Assert.That(assetCode, Does.Contain("ready model tasks"));
        Assert.That(assetCode, Does.Contain("ready texture-reference tasks"));
        Assert.That(assetCode, Does.Contain("BuildMaterialPackageOutputRoot"));
        Assert.That(assetCode, Does.Contain("SpecialFolder.LocalApplicationData"));
        Assert.That(assetCode, Does.Contain("ONSLAUGHT_WINUI_ASSET_PACKAGE_ROOT"));
        Assert.That(assetCode, Does.Contain("BuildPathSummary"));
        Assert.That(assetCode, Does.Contain("IsAllowedExportPath"));
        Assert.That(assetCode, Does.Contain("extension is \".png\" or \".fbx\""));
        Assert.That(assetCode, Does.Contain("UseShellExecute = true"));
        Assert.That(assetCode, Does.Contain("Clipboard.SetContent"));
        Assert.That(assetCode, Does.Not.Contain("SourcePathTextBlock.Text ="));
    }

    [Test]
    public void WinUiPublish_CopiesThirdPartyNoticesIntoPublishOutput()
    {
        string project = ReadRepoFile("OnslaughtCareerEditor.WinUI", "OnslaughtCareerEditor.WinUI.csproj");

        Assert.That(project, Does.Contain("CopyWinUINoticesToPublishDirectory"));
        Assert.That(project, Does.Contain("THIRD_PARTY_NOTICES.winui-draft.md"));
        Assert.That(project, Does.Contain("THIRD_PARTY_NOTICES.md"));
        Assert.That(project, Does.Contain("$(PublishDir)"));
    }

    [Test]
    public void WinUiBuild_CopiesPatchCatalogIntoAppOutput()
    {
        string project = ReadRepoFile("OnslaughtCareerEditor.WinUI", "OnslaughtCareerEditor.WinUI.csproj");

        Assert.That(project, Does.Contain("..\\patches\\catalog\\patches.v2.json"));
        Assert.That(project, Does.Contain("Link=\"patches\\catalog\\patches.v2.json\""));
        Assert.That(project, Does.Contain("CopyToOutputDirectory=\"PreserveNewest\""));
    }

    [Test]
    public void AppCoreHost_ModelPreviewCoverageIncludesMaterialSlotCoverage()
    {
        string hostCode = ReadRepoFile("OnslaughtCareerEditor.AppCore.Host", "Program.cs");

        Assert.That(hostCode, Does.Contain("RowsWithTextureToMaterialSlotNames"));
        Assert.That(hostCode, Does.Contain("TextureToMaterialSlotNames"));
        Assert.That(hostCode, Does.Contain("RowsWithNormalMappingModes"));
        Assert.That(hostCode, Does.Contain("RowsWithNormalReferenceModes"));
        Assert.That(hostCode, Does.Contain("NormalMappingModes"));
        Assert.That(hostCode, Does.Contain("NormalReferenceModes"));
        Assert.That(hostCode, Does.Contain("RowsWithVertexColorMappingModes"));
        Assert.That(hostCode, Does.Contain("RowsWithVertexColorReferenceModes"));
        Assert.That(hostCode, Does.Contain("VertexColorMappingModes"));
        Assert.That(hostCode, Does.Contain("VertexColorReferenceModes"));
        Assert.That(hostCode, Does.Contain("RowsWithTextureCoordinateMappingModes"));
        Assert.That(hostCode, Does.Contain("RowsWithTextureCoordinateReferenceModes"));
        Assert.That(hostCode, Does.Contain("TextureCoordinateMappingModes"));
        Assert.That(hostCode, Does.Contain("TextureCoordinateReferenceModes"));
        Assert.That(hostCode, Does.Contain("RowsWithMaterialMappingModes"));
        Assert.That(hostCode, Does.Contain("RowsWithMaterialReferenceModes"));
        Assert.That(hostCode, Does.Contain("MaterialMappingModes"));
        Assert.That(hostCode, Does.Contain("MaterialReferenceModes"));
    }

    [Test]
    public void WinUiInstallerSigning_PreflightTracksPackageProofLayers()
    {
        string project = ReadRepoFile("OnslaughtCareerEditor.WinUI", "OnslaughtCareerEditor.WinUI.csproj");
        string packageJson = ReadRepoFile("package.json");
        string preflight = ReadRepoFile("tools", "winui_installer_preflight.py");

        Assert.That(project, Does.Contain("<EnableMsixTooling>false</EnableMsixTooling>"));
        Assert.That(project, Does.Contain("<AppxPackage>false</AppxPackage>"));
        Assert.That(project, Does.Contain("<WindowsPackageType>None</WindowsPackageType>"));
        Assert.That(project, Does.Contain("<WindowsAppSDKSelfContained>true</WindowsAppSDKSelfContained>"));
        Assert.That(project, Does.Not.Contain("PackageCertificateThumbprint"));
        Assert.That(project, Does.Not.Contain("PackageCertificateKeyFile"));
        Assert.That(project, Does.Not.Contain("PackageCertificatePassword"));
        Assert.That(packageJson, Does.Contain("test:winui-installer-preflight"));
        Assert.That(packageJson, Does.Contain("test:winui-msix-candidate-probe"));
        if (packageJson.Contains("\"name\": \"onslaught-toolkit-public-source\"", StringComparison.Ordinal))
        {
            Assert.That(packageJson, Does.Not.Contain("test:winui-msix-signing-probe"));
            Assert.That(packageJson, Does.Not.Contain("test:winui-msix-install-probe"));
            Assert.That(packageJson, Does.Not.Contain("test:winui-msix-trusted-install-probe"));
            Assert.That(packageJson, Does.Not.Contain("--allow-current-user-cert-trust"));
        }
        else
        {
            Assert.That(packageJson, Does.Contain("test:winui-msix-signing-probe"));
            Assert.That(packageJson, Does.Contain("test:winui-msix-install-probe"));
            Assert.That(packageJson, Does.Contain("test:winui-msix-trusted-install-probe"));
        }
        Assert.That(preflight, Does.Contain("guarded-not-ready"));
        Assert.That(preflight, Does.Contain("unsigned_msix_candidate_probe"));
        Assert.That(preflight, Does.Contain("local_msix_signing_probe"));
        Assert.That(preflight, Does.Contain("untrusted_install_probe"));
        Assert.That(preflight, Does.Contain("trusted_install_probe"));
        Assert.That(preflight, Does.Contain("winui_msix_current_candidate_probe_2026-05-08.md"));
        Assert.That(preflight, Does.Contain("winui_msix_current_signing_probe_2026-05-08.md"));
        Assert.That(preflight, Does.Contain("winui_msix_current_untrusted_install_probe_2026-05-08.md"));
        Assert.That(preflight, Does.Contain("winui_msix_trusted_install_guarded_blocker_2026-05-22.md"));
        Assert.That(preflight, Does.Contain("install is blocked without certificate trust"));
        Assert.That(preflight, Does.Contain("Package.appxmanifest"));
        Assert.That(preflight, Does.Contain("not configured as an MSIX package"));
        Assert.That(preflight, Does.Not.Contain("signed installer/MSIX release is not proven"));
    }

    [Test]
    public void PatchBench_VisibleCopyPromisesCopiedExecutableWorkflow()
    {
        string shellXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml");
        string homeXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "HomePage.xaml");
        string pageXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string itemModel = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Models", "BinaryPatchItemModel.cs");
        string settingsXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml");

        Assert.That(shellXaml, Does.Contain("Windowed &amp; Mods"));
        Assert.That(homeXaml, Does.Contain("Windowed &amp; Mods creates a safe game copy"));
        Assert.That(pageXaml, Does.Contain("A safe game copy is a separate folder"));
        Assert.That(pageXaml, Does.Not.Contain("Patch Bench patches"));
        Assert.That(pageXaml, Does.Contain("Windowed &amp; Mods"));
        Assert.That(pageXaml, Does.Contain("What Gets Touched"));
        Assert.That(pageXaml, Does.Contain("Steam/game install: read-only source"));
        Assert.That(pageXaml, Does.Contain("Safe game copy: app-owned folder"));
        Assert.That(pageXaml, Does.Contain("Advanced BEA.exe-only copy: used for technical inspection and byte-level patching only"));
        Assert.That(pageXaml, Does.Contain("read-only source"));
        Assert.That(pageXaml, Does.Contain("Steam/game install is unchanged"));
        Assert.That(pageXaml, Does.Contain("Main workflow"));
        Assert.That(pageXaml, Does.Contain("1. Find your installed game. 2. Pick mods for a safe copy. 3. Create the safe copy. 4. Play the safe copy."));
        Assert.That(pageXaml, Does.Contain("PatchBenchTopUseGameFolderButton"));
        Assert.That(pageXaml, Does.Contain("Use configured folder"));
        Assert.That(pageXaml, Does.Contain("PatchBenchTopCreateSafeCopyButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchTopPlaySafeCopyButton"));
        Assert.That(pageXaml, Does.Contain("These shortcuts use the same guarded safe-copy workflow below"));
        Assert.That(code, Does.Contain("PatchBenchTopCreateSafeCopyButton.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled"));
        Assert.That(code, Does.Contain("PatchBenchTopPlaySafeCopyButton.IsEnabled = PatchBenchLaunchCopiedProfileButton.IsEnabled"));
        Assert.That(code, Does.Contain("No configured game folder with BEA.exe was found"));
        Assert.That(code, Does.Contain("if (_isLaunchingCopiedProfile)"));
        Assert.That(code, Does.Contain("Safe copy launch is already starting"));
        Assert.That(pageXaml, Does.Contain("Safe copy profiles"));
        Assert.That(pageXaml, Does.Contain("Profiles are presets for normal play and testing"));
        Assert.That(pageXaml, Does.Contain("Compatibility Copy"));
        Assert.That(pageXaml, Does.Contain("Windowed + Graphics Defaults"));
        Assert.That(pageXaml, Does.Contain("Enhanced Profile Preview"));
        Assert.That(pageXaml, Does.Contain("Enhanced Profile Preview combines the windowed setup, graphics defaults, PATCHED title marker, red menu background, Goodies preview, and copied control defaults."));
        Assert.That(pageXaml, Does.Contain("Debug Camera Preview selects only the bounded free-camera toggle plus one Q-forward remap path."));
        Assert.That(pageXaml, Does.Contain("PatchBenchDebugCameraProofMatrixStatus"));
        Assert.That(pageXaml, Does.Contain("Debug Camera Preview only selects Q-forward. Seven other Q remap rows are manual/custom-only and mutually exclusive; their accepted CDB movement/orientation proofs are tracked for future work."));
        Assert.That(pageXaml, Does.Contain("Experimental camera controls may be unstable."));
        Assert.That(pageXaml, Does.Contain("It does not prove full camera controls or gameplay safety."));
        Assert.That(pageXaml, Does.Contain("Fullscreen fallback, netcode, and in-game toggle menus are not part of any preset yet."));
        Assert.That(pageXaml, Does.Contain("Create safe copy records the exact selected rows and control options into the safe-copy manifest"));
        Assert.That(pageXaml, Does.Contain("PatchBenchSelectedProfileStatus"));
        Assert.That(pageXaml, Does.Contain("Selected profile: Compatibility Copy. This is the safest default."));
        Assert.That(pageXaml, Does.Contain("PatchBenchEnhancedPreviewProfileButton"));
        Assert.That(pageXaml, Does.Contain("Click=\"EnhancedPreviewPresetButton_Click\""));
        Assert.That(pageXaml, Does.Contain("PatchBenchDebugCameraPreviewProfileButton"));
        Assert.That(pageXaml, Does.Contain("Click=\"DebugCameraPreviewPresetButton_Click\""));
        Assert.That(pageXaml, Does.Contain("Clear optional mods"));
        Assert.That(pageXaml, Does.Contain("Graphics flag rows only"));
        Assert.That(pageXaml, Does.Contain("PatchBenchWindowedPresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchModernGraphicsPresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchStableDefaultsButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearSelectionButton"));
        Assert.That(pageXaml, Does.Contain("Menu background color"));
        Assert.That(pageXaml, Does.Contain("Choose one frontend clear-screen color for the safe copy"));
        Assert.That(pageXaml, Does.Contain("it does not replace textures, fonts, or HUD colors"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMenuColorRedButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMenuColorGreenButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMenuColorBlackButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMenuColorClearButton"));
        Assert.That(pageXaml, Does.Contain("Red background"));
        Assert.That(pageXaml, Does.Contain("Green background"));
        Assert.That(pageXaml, Does.Contain("Black background"));
        Assert.That(pageXaml, Does.Contain("Clear menu color"));
        Assert.That(pageXaml, Does.Contain("Title marker and Goodies preview"));
        Assert.That(pageXaml, Does.Contain("PATCHED marker shows the word PATCHED on the title screen"));
        Assert.That(pageXaml, Does.Contain("Goodies preview shows Goodies as unlocked in the gallery view of the safe copy"));
        Assert.That(pageXaml, Does.Contain("PatchBenchAddVersionMarkerButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearVersionMarkerButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchAddGoodiesPreviewButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearGoodiesPreviewButton"));
        Assert.That(pageXaml, Does.Contain("Add PATCHED marker"));
        Assert.That(pageXaml, Does.Contain("Clear PATCHED marker"));
        Assert.That(pageXaml, Does.Contain("Add Goodies preview"));
        Assert.That(pageXaml, Does.Contain("Clear Goodies preview"));
        Assert.That(pageXaml, Does.Contain("Select Compatibility Copy profile"));
        Assert.That(pageXaml, Does.Contain("Select Windowed and Graphics Defaults profile"));
        Assert.That(pageXaml, Does.Contain("Clear optional mod rows; safe copies still include required compatibility"));
        Assert.That(code, Does.Contain("Compatibility Copy profile selected"));
        Assert.That(code, Does.Contain("Windowed + Graphics Defaults profile selected"));
        Assert.That(code, Does.Contain("Debug Camera Preview profile selected"));
        Assert.That(code, Does.Contain("BinaryPatchPlanBuilder.DebugCameraPreviewProfileId"));
        Assert.That(code, Does.Contain("optional mod rows cleared"));
        Assert.That(code, Does.Contain("MenuColorRedButton_Click"));
        Assert.That(code, Does.Contain("MenuColorGreenButton_Click"));
        Assert.That(code, Does.Contain("MenuColorBlackButton_Click"));
        Assert.That(code, Does.Contain("MenuColorClearButton_Click"));
        Assert.That(code, Does.Contain("SelectFrontendColorPatch(\"frontend_clear_screen_dark_red\""));
        Assert.That(code, Does.Contain("SelectFrontendColorPatch(\"frontend_clear_screen_dark_green\""));
        Assert.That(code, Does.Contain("SelectFrontendColorPatch(\"frontend_clear_screen_black\""));
        Assert.That(code, Does.Contain("SelectFrontendColorPatch(null, \"frontend clear-screen color selection cleared\")"));
        Assert.That(code, Does.Contain("if (IsFrontendColorPatchKey(item.Spec.Key))"));
        Assert.That(code, Does.Contain("item.IsSelected = selectedKey is not null"));
        Assert.That(code, Does.Contain("red menu background selected"));
        Assert.That(code, Does.Contain("green menu background selected"));
        Assert.That(code, Does.Contain("black menu background selected"));
        Assert.That(code, Does.Contain("AddVersionMarkerButton_Click"));
        Assert.That(code, Does.Contain("ClearVersionMarkerButton_Click"));
        Assert.That(code, Does.Contain("AddGoodiesPreviewButton_Click"));
        Assert.That(code, Does.Contain("ClearGoodiesPreviewButton_Click"));
        Assert.That(code, Does.Contain("SetVisiblePatchRowSelected("));
        Assert.That(code, Does.Contain("\"version_overlay_use_patched_format_pointer\""));
        Assert.That(code, Does.Contain("\"goodies_gallery_display_unlock\""));
        Assert.That(code, Does.Contain("PATCHED title marker row selected"));
        Assert.That(code, Does.Contain("PATCHED title marker row cleared"));
        Assert.That(code, Does.Contain("Goodies display preview row selected"));
        Assert.That(code, Does.Contain("Goodies display preview row cleared"));
        Assert.That(code, Does.Contain("Patch row is not available: {key}"));
        Assert.That(pageXaml, Does.Contain("Available changes include windowed startup, wider display-mode support, graphics defaults, menu color presets, music swaps, Goodies preview, title marker, launch options, control-option presets, and experimental camera/control rows."));
        Assert.That(pageXaml, Does.Contain("Open Details and limits on any row"));
        Assert.That(pageXaml, Does.Contain("Details and limits"));
        Assert.That(pageXaml, Does.Contain("What should change"));
        Assert.That(pageXaml, Does.Contain("What was checked"));
        Assert.That(pageXaml, Does.Contain("Not proven yet"));
        Assert.That(pageXaml, Does.Contain("Proof note"));
        Assert.That(pageXaml, Does.Contain("ExpectedVisibleResult"));
        Assert.That(pageXaml, Does.Contain("VerifiedProof"));
        Assert.That(pageXaml, Does.Contain("StillUnproven"));
        Assert.That(pageXaml, Does.Contain("ProofReference"));
        Assert.That(pageXaml, Does.Contain("PatchBenchSafeCopySourceStatus"));
        Assert.That(code, Does.Contain("Frontend Color Mods"));
        Assert.That(code, Does.Contain("Goodies Gallery Mods"));
        Assert.That(code, Does.Contain("Debug Camera Mods"));
        Assert.That(code, Does.Contain("Controls & Pause"));
        Assert.That(code, Does.Contain("visible patch rows without a rendered group"));
        Assert.That(code, Does.Contain("Version overlay support payload (auto-selected)"));
        Assert.That(code, Does.Contain("these affect frontend clear-screen backgrounds, not textures, fonts, or HUD colors"));
        Assert.That(code, Does.Contain("These may be unstable; open Details on a row for exactly what has been tested."));
        Assert.That(code, Does.Contain("Open Details on a row for tested behavior, remaining limits, and proof notes."));
        Assert.That(code, Does.Contain("s_frontendColorPatchKeys"));
        Assert.That(code, Does.Contain("IsFrontendColorPatchKey"));
        Assert.That(code, Does.Contain("_lastCopiedProfileContentSignature"));
        Assert.That(code, Does.Contain("BuildCurrentSafeCopyContentSignature"));
        Assert.That(code, Does.Contain("Selections changed after this safe copy was created"));
        Assert.That(code, Does.Contain("Prepared safe copy does not match the current optional patch/savegame/control choices"));
        Assert.That(code, Does.Contain("Prepared safe game copy is stale"));
        Assert.That(code, Does.Contain("No safe game copy prepared in this session."));
        Assert.That(itemModel, Does.Contain("frontend_clear_screen_dark_red"));
        Assert.That(itemModel, Does.Contain("Red menu background"));
        Assert.That(itemModel, Does.Contain("frontend_clear_screen_dark_green"));
        Assert.That(itemModel, Does.Contain("Green menu background"));
        Assert.That(itemModel, Does.Contain("frontend_clear_screen_black"));
        Assert.That(itemModel, Does.Contain("Black menu background"));
        Assert.That(itemModel, Does.Contain("Visible proof: one safe-copy title-screen capture and one navigated Goodies-menu run show red-family margins"));
        Assert.That(itemModel, Does.Contain("Visible proof: one safe-copy title-screen capture and one navigated Goodies-menu run show green-family margins"));
        Assert.That(itemModel, Does.Contain("Visible proof: one safe-copy title-screen capture and one navigated Goodies-menu run show black-family margins"));
        Assert.That(itemModel, Does.Contain("goodies_gallery_display_unlock"));
        Assert.That(itemModel, Does.Contain("Goodies wall display-state override"));
        Assert.That(itemModel, Does.Contain("Changes Goodies-wall display state for bounded checked entries in the safe copy without editing your saves or awarding them"));
        Assert.That(itemModel, Does.Contain("Visible proof: two Goodies-wall comparisons changed display state, and one Tatiana page was captured"));
        Assert.That(itemModel, Does.Contain("Model/FMV playback and every-entry browsing remain unproven"));
        Assert.That(itemModel, Does.Contain("Two baseline-vs-patched Goodies-wall comparisons changed display state; one selected Tatiana page was captured."));
        Assert.That(itemModel, Does.Contain("Model/FMV playback, every-entry browsing, save persistence, and permanent unlocks."));
        Assert.That(itemModel, Does.Contain("Readiness: winui_goodies_gallery_display_unlock_2026-06-17.md"));
        Assert.That(itemModel, Does.Contain("free_camera_aurore_gate_bypass"));
        Assert.That(itemModel, Does.Contain("Experimental free-camera gate byte change"));
        Assert.That(itemModel, Does.Contain("Full camera behavior remains unproven"));
        Assert.That(itemModel, Does.Contain("pause_o_scan_initializer_experiment"));
        Assert.That(itemModel, Does.Contain("Experimental O-key pause test"));
        Assert.That(itemModel, Does.Contain("bounded free-camera run recorded O-query, BUTTON_PAUSE dispatch, and pause/unpause evidence"));
        Assert.That(itemModel, Does.Contain("level-100 proof separately observed ordered O-query, BUTTON_PAUSE dispatch, CGame__Pause, pause-menu init, and Enter resume"));
        Assert.That(itemModel, Does.Contain("Readiness: winui_pause_o_scan_initializer_runtime_2026-06-18.md"));
        Assert.That(itemModel, Does.Contain("\"pause_o_scan_initializer_experiment\" => \"Controls & Pause\""));
        Assert.That(itemModel, Does.Contain("\"pause_o_scan_initializer_experiment\" => \"EXPERIMENTAL PAUSE TEST\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_yaw_left_q_hook\" => \"Debug Camera Mods\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_yaw_right_q_hook\" => \"Debug Camera Mods\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_pitch_up_q_hook\" => \"Debug Camera Mods\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_pitch_down_q_hook\" => \"Debug Camera Mods\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_yaw_left_q_hook\" => \"EXPERIMENTAL CAMERA TEST\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_yaw_right_q_hook\" => \"EXPERIMENTAL CAMERA TEST\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_pitch_up_q_hook\" => \"EXPERIMENTAL CAMERA TEST\""));
        Assert.That(itemModel, Does.Contain("\"free_camera_keyboard_pitch_down_q_hook\" => \"EXPERIMENTAL CAMERA TEST\""));
        Assert.That(itemModel, Does.Contain("Readiness: winui_frontend_clear_screen_color_patch_2026-06-16.md"));
        Assert.That(itemModel, Does.Contain("public string UserFacingStatus"));
        Assert.That(pageXaml, Does.Contain("Text=\"{Binding UserFacingStatus}\""));
        Assert.That(itemModel, Does.Not.Contain("Checked: {ProofStatus}"));
        Assert.That(itemModel, Does.Contain("Open Details and limits for technical evidence and remaining limits"));
        Assert.That(itemModel, Does.Contain("SAFE COPY REQUIRED"));
        Assert.That(itemModel, Does.Contain("VISIBLE MARKER"));
        Assert.That(itemModel, Does.Contain("MENU COLOR CHECK"));
        Assert.That(itemModel, Does.Contain("GOODIES DISPLAY CHECK"));
        Assert.That(itemModel, Does.Contain("LAUNCH SMOKE"));
        Assert.That(itemModel, Does.Contain("EXPERIMENTAL PAUSE TEST"));
        Assert.That(itemModel, Does.Not.Contain("Status: {TrackLabel}."));
        Assert.That(pageXaml, Does.Contain("AutomationProperties.HelpText=\"{Binding AccessibilityHelpText}\""));
        int summaryStart = itemModel.IndexOf("Summary = spec.Key switch", StringComparison.Ordinal);
        int proofStatusStart = itemModel.IndexOf("ProofStatus = spec.Key switch", StringComparison.Ordinal);
        int userFacingStatusStart = itemModel.IndexOf("UserFacingStatus = spec.Key switch", StringComparison.Ordinal);
        int expectedVisibleStart = itemModel.IndexOf("ExpectedVisibleResult = spec.Key switch", StringComparison.Ordinal);
        int trackLabelStart = itemModel.IndexOf("public string TrackLabel", StringComparison.Ordinal);
        int trackLabelSwitchStart = itemModel.IndexOf("{", trackLabelStart, StringComparison.Ordinal);
        int trackBrushStart = itemModel.IndexOf("public Brush TrackBrush", StringComparison.Ordinal);
        Assert.That(summaryStart, Is.GreaterThanOrEqualTo(0));
        Assert.That(proofStatusStart, Is.GreaterThan(summaryStart));
        Assert.That(userFacingStatusStart, Is.GreaterThan(proofStatusStart));
        Assert.That(expectedVisibleStart, Is.GreaterThan(userFacingStatusStart));
        Assert.That(trackLabelStart, Is.GreaterThan(expectedVisibleStart));
        Assert.That(trackLabelSwitchStart, Is.GreaterThan(trackLabelStart));
        Assert.That(trackBrushStart, Is.GreaterThan(trackLabelStart));
        string collapsedSummaries = itemModel[summaryStart..proofStatusStart];
        string collapsedStatuses = itemModel[userFacingStatusStart..expectedVisibleStart];
        string collapsedTrackLabels = itemModel[trackLabelSwitchStart..trackBrushStart];
        string accessibilityHelp = Regex.Match(itemModel, "public string AccessibilityHelpText =>\\s*\\$\"(?<value>[^\"]+)\";").Groups["value"].Value;
        foreach (string collapsedText in new[] { collapsedSummaries, collapsedStatuses, collapsedTrackLabels, accessibilityHelp })
        {
            Assert.That(collapsedText, Does.Not.Contain("CDB"));
            Assert.That(collapsedText, Does.Not.Contain("Readiness:"));
            Assert.That(collapsedText, Does.Not.Contain("0x"));
            Assert.That(collapsedText, Does.Not.Contain("PROOF"));
            Assert.That(collapsedText, Does.Not.Contain("ProofStatus"));
            Assert.That(collapsedText, Does.Not.Contain("TrackLabel"));
        }
        Assert.That(
            pageXaml.IndexOf("Safe game copy", StringComparison.Ordinal),
            Is.LessThan(pageXaml.IndexOf("Advanced: patch one BEA.exe copy", StringComparison.Ordinal)),
            "The tryable copied-game flow should appear before the advanced BEA.exe-only copy workflow.");
        Assert.That(pageXaml, Does.Contain("Create BEA.exe-only copy"));
        Assert.That(pageXaml, Does.Contain("Apply to BEA.exe-only copy"));
        Assert.That(pageXaml, Does.Contain("PatchBenchSourceExePath"));
        Assert.That(pageXaml, Does.Contain("AutomationProperties.Name=\"Source executable path\""));
        Assert.That(pageXaml, Does.Contain("PatchBenchCreateWorkingCopyButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchWorkingCopyPath"));
        Assert.That(pageXaml, Does.Contain("AutomationProperties.Name=\"BEA.exe-only copy executable path\""));
        Assert.That(pageXaml, Does.Contain("PatchBenchVerifyButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchApplyButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchRestoreButton"));
        Assert.That(pageXaml, Does.Contain("Safe game copy"));
        Assert.That(pageXaml, Does.Contain("Create a launchable app-owned game copy"));
        Assert.That(pageXaml, Does.Contain("You do not need the advanced BEA.exe-only copy first"));
        Assert.That(pageXaml, Does.Contain("This always adds the required windowed compatibility patches; selected mods are added too"));
        Assert.That(pageXaml, Does.Contain("Savegames are optional"));
        Assert.That(pageXaml, Does.Contain("PatchBenchIncludeSavegamesOption"));
        Assert.That(pageXaml, Does.Contain("Copy savegames into the safe copy"));
        Assert.That(pageXaml, Does.Contain("Leave this off for clean patch tests"));
        Assert.That(pageXaml, Does.Contain("The source savegames folder is still read-only"));
        Assert.That(pageXaml, Does.Contain("Create safe copy"));
        Assert.That(pageXaml, Does.Contain("Play safe copy"));
        Assert.That(pageXaml, Does.Contain("Stop safe copy"));
        Assert.That(pageXaml, Does.Contain("Play starts the safe copy."));
        Assert.That(pageXaml, Does.Contain("Stop closes only the safe-copy process started here"));
        Assert.That(pageXaml, Does.Contain("Save progress first"));
        Assert.That(pageXaml, Does.Not.Contain("Copied profile preflight"));
        Assert.That(pageXaml, Does.Not.Contain("Prepare copied profile"));
        Assert.That(pageXaml, Does.Contain("PatchBenchPrepareCopiedProfileButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchCopiedProfileSummary"));
        Assert.That(pageXaml, Does.Contain("PatchBenchIncludeSavegamesOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchLaunchCopiedProfileButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchStopCopiedProfileButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchCopiedProfileLaunchStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchCopiedProfileLaunchPlanExpander"));
        Assert.That(pageXaml, Does.Contain("PatchBenchCopiedProfileLaunchPlan"));
        Assert.That(pageXaml, Does.Contain("PatchBenchAdvancedLaunchOptionsExpander"));
        Assert.That(pageXaml, Does.Contain("Advanced launch and control options"));
        Assert.That(pageXaml, Does.Contain("IsExpanded=\"False\""));
        Assert.That(
            pageXaml.IndexOf("PatchBenchLaunchCopiedProfileButton", StringComparison.Ordinal),
            Is.LessThan(pageXaml.IndexOf("PatchBenchAdvancedLaunchOptionsExpander", StringComparison.Ordinal)),
            "Play/Stop/status should stay before advanced launch and control diagnostics.");
        Assert.That(
            pageXaml.IndexOf("PatchBenchCopiedProfileLaunchPlanExpander", StringComparison.Ordinal),
            Is.LessThan(pageXaml.IndexOf("PatchBenchAdvancedLaunchOptionsExpander", StringComparison.Ordinal)),
            "The launch plan should stay near Play before advanced controls.");
        Assert.That(pageXaml, Does.Contain("UserFacingStatus"));
        Assert.That(pageXaml, Does.Not.Contain("Text=\"{Binding ProofStatus}\""));
        Assert.That(pageXaml, Does.Contain("Advanced launch options"));
        Assert.That(pageXaml, Does.Contain("These options are passed only to the safe copy. They do not edit either executable."));
        Assert.That(pageXaml, Does.Contain("Launch presets"));
        Assert.That(pageXaml, Does.Contain("PatchBenchQuietCaptureLaunchPresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchHighDetailLaunchPresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearLaunchOptionsButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchControlBaselinePresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchControlSharpenedPresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchControlConfig2PresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchControlConfig3PresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchControlConfig4PresetButton"));
        Assert.That(pageXaml, Does.Contain("Quiet capture"));
        Assert.That(pageXaml, Does.Contain("High detail test"));
        Assert.That(pageXaml, Does.Contain("Clear launch options"));
        Assert.That(pageXaml, Does.Contain("Control diagnostics"));
        Assert.That(pageXaml, Does.Contain("Baseline config 1"));
        Assert.That(pageXaml, Does.Contain("Sensitivity test config 1"));
        Assert.That(pageXaml, Does.Contain("Swapped config 2"));
        Assert.That(pageXaml, Does.Contain("Alt morph/jets config 3"));
        Assert.That(pageXaml, Does.Contain("Swapped alt config 4"));
        Assert.That(pageXaml, Does.Contain("A/B test presets for safe-copy control diagnostics"));
        Assert.That(pageXaml, Does.Contain("They do not add deadzone, look-curve, camera, movement, or online patches."));
        Assert.That(pageXaml, Does.Contain("Presets only fill the options below; Play still uses the guarded safe-copy launch plan."));
        Assert.That(pageXaml, Does.Contain("PatchBenchSkipFmvLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchNoMusicLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchNoSoundLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchHighDetailLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchNoStaticShadowsLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchNoRumbleLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchShowDebugTraceLaunchOption"));
        Assert.That(pageXaml, Does.Not.Contain("PatchBenchDevModeLaunchOption"));
        Assert.That(pageXaml, Does.Not.Contain("PatchBenchKillHudLaunchOption"));
        Assert.That(pageXaml, Does.Not.Contain("PatchBenchModelViewerLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchLevelLaunchOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchAdminLevelPresetComboBox"));
        Assert.That(pageXaml, Does.Contain("Campaign training world 100"));
        Assert.That(pageXaml, Does.Contain("Local split-screen test world 850"));
        Assert.That(pageXaml, Does.Contain("Presets only fill the validated -level argument"));
        Assert.That(pageXaml, Does.Contain("PatchBenchLocalMultiplayerProbeButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineReadinessStatusPanel"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlinePrepCard"));
        Assert.That(pageXaml, Does.Contain("Online multiplayer is not ready"));
        Assert.That(pageXaml, Does.Contain("Local split-screen is available in a safe copy."));
        Assert.That(pageXaml, Does.Contain("Online play is not available in this release."));
        Assert.That(pageXaml, Does.Contain("Local split-screen in a safe copy is the only multiplayer workflow here."));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlinePrepLocalProbeButton"));
        Assert.That(pageXaml, Does.Contain("Use local split-screen launch preset"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlinePrepActionStatus"));
        Assert.That(pageXaml, Does.Contain("Select the local split-screen launch preset, then create and play a safe copy. This is not Host/Join."));
        Assert.That(pageXaml, Does.Contain("Online status"));
        Assert.That(pageXaml, Does.Contain("Online play is not available yet"));
        Assert.That(pageXaml, Does.Contain("You can still use local split-screen in a safe copy."));
        Assert.That(pageXaml, Does.Contain("There is no Host or Join workflow in this build."));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineTargetModel"));
        Assert.That(pageXaml, Does.Contain("Future design sketch; Host/Join unavailable"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineTechnicalDetailsToggle"));
        Assert.That(pageXaml, Does.Contain("Technical status details"));
        Assert.That(pageXaml, Does.Contain("OnContent=\"Section shown\""));
        Assert.That(pageXaml, Does.Contain("Toggled=\"OnlineTechnicalDetailsToggle_Toggled\""));
        Assert.That(pageXaml, Does.Contain("This section is for technical review only. It does not launch online play"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineTechnicalDetailsExpander"));
        Assert.That(pageXaml, Does.Contain("Visibility=\"Collapsed\""));
        Assert.That(code, Does.Contain("RenderOnlineTechnicalDetailsVisibility"));
        Assert.That(code, Does.Contain("PatchBenchOnlineTechnicalDetailsToggle.IsOn"));
        Assert.That(code, Does.Contain("PatchBenchOnlineTechnicalDetailsExpander.Visibility = visible ? Visibility.Visible : Visibility.Collapsed"));
        Assert.That(code, Does.Contain("You can still use local split-screen in a safe copy."));
        Assert.That(code, Does.Contain("larger-player support remains future design work."));
        Assert.That(code, Does.Contain("summary.CompanionNetplayTarget"));
        Assert.That(code, Does.Contain("FormatCompanionNetplayTarget"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineReadinessGateDetails"));
        Assert.That(pageXaml, Does.Contain("Proof ladder"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineProofLadder"));
        Assert.That(pageXaml, Does.Contain("local split-screen accepted for study"));
        Assert.That(pageXaml, Does.Contain("Host/Join locked until second-host command source and copied-runtime causality proofs both pass"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineMaintainerArtifactToolsToggle"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMaintainerArtifactToolsStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMaintainerArtifactLoaderPanel"));
        Assert.That(pageXaml, Does.Contain("Technical summary loaders are hidden. Normal safe-copy play does not need summary files."));
        Assert.That(pageXaml, Does.Contain("Two-safe-copy topology summary"));
        Assert.That(pageXaml, Does.Contain("PatchBenchDualSafeCopyTopologyArtifactStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchDualSafeCopyTopologyBoundary"));
        Assert.That(pageXaml, Does.Contain("PatchBenchDualSafeCopyTopologyNextProofs"));
        Assert.That(pageXaml, Does.Contain("PatchBenchLoadDualSafeCopyTopologyArtifactButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearDualSafeCopyTopologyArtifactButton"));
        Assert.That(pageXaml, Does.Contain("Load topology summary"));
        Assert.That(pageXaml, Does.Contain("No dual-safe-copy topology summary loaded"));
        Assert.That(pageXaml, Does.Contain("Not online multiplayer: no BEA launch, listener, invitation, remote input, Host/Join controls, distinct endpoint proof, or player-ready netplay."));
        Assert.That(code, Does.Contain("_dualSafeCopyTopologyArtifactSummary"));
        Assert.That(code, Does.Contain("TryLoadDualSafeCopyTopologyArtifact"));
        Assert.That(code, Does.Contain("FormatDualSafeCopyTopologyArtifactStatus"));
        Assert.That(code, Does.Contain("Loaded dual-safe-copy topology summary"));
        Assert.That(code, Does.Contain("RenderMaintainerArtifactToolsVisibility"));
        Assert.That(code, Does.Contain("Technical summary loaders are visible. Loading a summary still cannot enable Host/Join or prove online play."));
        Assert.That(code, Does.Contain("Host/Join remain unavailable"));
        Assert.That(pageXaml, Does.Contain("Second-host setup checklist"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineSecondHostSetupChecklist"));
        Assert.That(code, Does.Contain("summary.SecondHostSetupSteps"));
        Assert.That(code, Does.Contain("FormatSecondHostSetupChecklist"));
        Assert.That(code, Does.Contain("summary.ProofLadderRows"));
        Assert.That(code, Does.Contain("FormatOnlineProofLadder"));
        Assert.That(code, Does.Contain("OnlineMultiplayerProofLadderRow"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineReadinessBlockedReasons"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineCompanionSessionStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineCompanionLaunchPlan"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineCompanionNextProofs"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineCompanionNonClaims"));
        Assert.That(pageXaml, Does.Contain("Second-host live attempt"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineLiveAttemptStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineLiveAttemptBlockers"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineLiveAttemptCommands"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlinePromotionLockStatus"));
        Assert.That(pageXaml, Does.Contain("Online play is not player-ready."));
        Assert.That(pageXaml, Does.Contain("Second-host readiness summary"));
        Assert.That(pageXaml, Does.Contain("PatchBenchOnlineReadinessArtifactStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchLoadOnlineReadinessArtifactButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearOnlineReadinessArtifactButton"));
        Assert.That(pageXaml, Does.Contain("Load readiness summary"));
        Assert.That(pageXaml, Does.Contain("Physical controller readiness summary"));
        Assert.That(pageXaml, Does.Contain("PatchBenchGamepadReadinessArtifactStatus"));
        Assert.That(pageXaml, Does.Contain("PatchBenchLoadGamepadReadinessArtifactButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchClearGamepadReadinessArtifactButton"));
        Assert.That(pageXaml, Does.Contain("Load controller summary"));
        Assert.That(pageXaml, Does.Contain("client readiness check"));
        Assert.That(pageXaml, Does.Contain("Unavailable in this release: online play, public matchmaking, and native online code."));
        Assert.That(pageXaml, Does.Not.Contain("Host online session"));
        Assert.That(pageXaml, Does.Not.Contain("Join online session"));
        Assert.That(code, Does.Contain("summary.ProofGateRows"));
        Assert.That(code, Does.Contain("summary.SecondHostLiveAttemptReadiness"));
        Assert.That(code, Does.Contain("FormatSecondHostLiveAttemptStatus"));
        Assert.That(code, Does.Contain("Checklist: server command inputs"));
        Assert.That(code, Does.Contain("client preflight"));
        Assert.That(code, Does.Contain("Host/Join controls"));
        Assert.That(code, Does.Contain("network candidates checked"));
        Assert.That(code, Does.Contain("FormatSecondHostLiveAttemptBlockers"));
        Assert.That(code, Does.Contain("FormatSecondHostLiveAttemptCommands"));
        Assert.That(code, Does.Contain("PatchBenchOnlinePromotionLockStatus.Text"));
        Assert.That(code, Does.Contain("FormatOnlinePromotionLockStatus"));
        Assert.That(code, Does.Contain("GetCompanionSessionReadiness"));
        Assert.That(code, Does.Contain("RenderOnlineCompanionSessionReadiness"));
        Assert.That(code, Does.Contain("PatchBenchOnlineReadinessGateDetails.Text"));
        Assert.That(code, Does.Contain("PatchBenchOnlineReadinessBlockedReasons.Text"));
        Assert.That(code, Does.Contain("PatchBenchOnlineLiveAttemptStatus.Text"));
        Assert.That(code, Does.Contain("PatchBenchOnlineLiveAttemptBlockers.Text"));
        Assert.That(code, Does.Contain("PatchBenchOnlineLiveAttemptCommands.Text"));
        Assert.That(code, Does.Contain("TryLoadSecondHostReadinessArtifact"));
        Assert.That(code, Does.Contain("FormatSecondHostReadinessArtifactStatus"));
        Assert.That(code, Does.Contain("PatchBenchOnlineReadinessArtifactStatus.Text"));
        Assert.That(code, Does.Contain("TryLoadLocalGamepadReadinessArtifact"));
        Assert.That(code, Does.Contain("FormatLocalGamepadReadinessArtifactStatus"));
        Assert.That(code, Does.Contain("PatchBenchGamepadReadinessArtifactStatus.Text"));
        Assert.That(code, Does.Contain("hardware preflight only; no BEA DirectInput/runtime proof"));
        Assert.That(code, Does.Contain("Host/Join remain unavailable."));
        Assert.That(code, Does.Contain("No listener, invitation, remote input, or Host/Join control is enabled."));
        Assert.That(code, Does.Contain("PatchBenchOnlineCompanionSessionStatus.Text"));
        Assert.That(code, Does.Contain("PatchBenchOnlineCompanionLaunchPlan.Text"));
        Assert.That(code, Does.Contain("FormatOnlineProofGateSummary"));
        Assert.That(code, Does.Contain("FormatCompanionSafeCopyStatus"));
        Assert.That(code, Does.Contain("Next work: prove a real second computer or VM can send a command"));
        Assert.That(code, Does.Contain("Safe copy status: {FormatCompanionSafeCopyStatus(summary.SafeCopyManifestStatus)} Host/Join stay off."));
        Assert.That(code, Does.Contain("Next online work: real second-host command test, then source-bound runtime proof for the copied game."));
        Assert.That(code, Does.Contain("no network listener"));
        Assert.That(code, Does.Not.Contain("Next proof IDs:"));
        Assert.That(code, Does.Not.Contain("Companion session: {summary.SafeCopyManifestStatus}"));
        Assert.That(pageXaml, Does.Not.Contain("PatchBenchHostOnlineSessionButton"));
        Assert.That(pageXaml, Does.Not.Contain("PatchBenchJoinOnlineSessionButton"));
        Assert.That(pageXaml, Does.Not.Contain("PatchBenchPublicMatchmakingButton"));
        string[] blockedOnlineButtonBlocks = Regex.Matches(pageXaml, "<Button\\b[\\s\\S]*?(?:/>|>)")
            .Select(match => match.Value)
            .Where(block => Regex.IsMatch(block, "Host online|Join online|Online session|Matchmaking", RegexOptions.IgnoreCase))
            .ToArray();
        string[] blockedOnlineClickHandlers = Regex.Matches(code, "\\b\\w*(?:Host|Join|Matchmaking)\\w*Button_Click\\b")
            .Select(match => match.Value)
            .ToArray();
        Assert.That(blockedOnlineButtonBlocks, Is.Empty, "Windowed & Mods must not grow Host/Join/Matchmaking buttons before readiness flags and proof contract allow them.");
        Assert.That(blockedOnlineClickHandlers, Is.Empty, "Windowed & Mods must not grow Host/Join/Matchmaking click handlers before readiness flags and proof contract allow them.");
        Assert.That(pageXaml, Does.Contain("PatchBenchConfigurationLaunchPresetComboBox"));
        Assert.That(pageXaml, Does.Contain("PatchBenchPersistControllerConfigOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchSharpenMouseLookOption"));
        Assert.That(pageXaml, Does.Contain("PatchBenchTextureRamLimitLaunchOption"));
        Assert.That(pageXaml, Does.Contain("Skip intro movies"));
        Assert.That(pageXaml, Does.Contain("Mute music (-nomusic; disables replacement-audio testing)"));
        Assert.That(pageXaml, Does.Contain("Request high detail"));
        Assert.That(pageXaml, Does.Contain("Disable static shadows (-nostaticshadows)"));
        Assert.That(pageXaml, Does.Contain("Disable controller vibration (-norumble)"));
        Assert.That(pageXaml, Does.Contain("Developer diagnostics"));
        Assert.That(pageXaml, Does.Contain("Show debug trace (-showdebugtrace)"));
        Assert.That(pageXaml, Does.Contain("It does not enable dev mode, build resources, record demos, add online features, or prove gameplay behavior."));
        Assert.That(pageXaml, Does.Not.Contain("Enable developer mode (-devmode)"));
        Assert.That(pageXaml, Does.Not.Contain("Hide HUD (-killhud)"));
        Assert.That(pageXaml, Does.Not.Contain("Open model viewer (-modelviewer)"));
        Assert.That(pageXaml, Does.Contain("Local split-screen test"));
        Assert.That(pageXaml, Does.Contain("Sets -level 850 for the safe copy"));
        Assert.That(pageXaml, Does.Contain("it is not online multiplayer"));
        Assert.That(pageXaml, Does.Contain("Controller configuration preset"));
        Assert.That(pageXaml, Does.Contain("Config 1: Default"));
        Assert.That(pageXaml, Does.Contain("Config 2: Swapped sticks"));
        Assert.That(pageXaml, Does.Contain("Config 3: Alternate morph/jets"));
        Assert.That(pageXaml, Does.Contain("Config 4: Swapped sticks + alternate morph/jets"));
        Assert.That(pageXaml, Does.Contain("Persist selected config in safe copy options"));
        Assert.That(pageXaml, Does.Contain("Persisting writes the selected config to the safe copy's defaultoptions.bea for both players"));
        Assert.That(pageXaml, Does.Contain("It does not change the installed game and does not prove runtime feel"));
        Assert.That(pageXaml, Does.Contain("Use copied mouse-look sensitivity preset"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMouseSensitivityPresetComboBox"));
        Assert.That(pageXaml, Does.Contain("Fast: 3.00"));
        Assert.That(pageXaml, Does.Contain("The sensitivity preset patches only the safe copy's defaultoptions.bea"));
        Assert.That(pageXaml, Does.Contain("PatchBenchCreateMusicSwapPresetComboBox"));
        Assert.That(pageXaml, Does.Contain("Music swap staged during safe-copy creation"));
        Assert.That(pageXaml, Does.Contain("No music swap"));
        Assert.That(pageXaml, Does.Contain("Optional: swap one shipped copied music track while creating the safe copy"));
        Assert.That(pageXaml, Does.Contain("in-game audio playback is still experimental"));
        Assert.That(pageXaml, Does.Contain("Swap music in safe copy"));
        Assert.That(pageXaml, Does.Contain("No music swap staged"));
        Assert.That(pageXaml, Does.Contain("Invert walker look Y in safe copy options"));
        Assert.That(pageXaml, Does.Contain("Invert flight look Y in safe copy options"));
        Assert.That(pageXaml, Does.Contain("They are not executable patches and do not prove improved runtime feel"));
        Assert.That(pageXaml, Does.Contain("does not prove runtime feel"));
        Assert.That(pageXaml, Does.Not.Contain("Improved controls"));
        Assert.That(pageXaml, Does.Not.Contain("better controls"));
        Assert.That(pageXaml, Does.Not.Contain("adds online"));
        Assert.That(pageXaml, Does.Contain("Optional texture RAM limit"));
        Assert.That(pageXaml, Does.Contain("Leave blank, or enter MB from 8 to 512"));
        Assert.That(pageXaml, Does.Contain("This does not confirm it reached the menu, stayed windowed, rendered correctly, or played replacement music."));
        Assert.That(pageXaml, Does.Not.Contain("windowed rendering parity"));
        Assert.That(pageXaml, Does.Not.Contain("preflight"));
        Assert.That(pageXaml, Does.Not.Contain("Copied profile"));
        Assert.That(pageXaml, Does.Contain("Swap one copied music track with another, or stage an external replacement OGG inside the safe copy"));
        Assert.That(pageXaml, Does.Contain("The original install is unchanged."));
        Assert.That(pageXaml, Does.Contain("Safe-copy music replacement status"));
        Assert.That(pageXaml, Does.Contain("Quick copied-track swap"));
        Assert.That(pageXaml, Does.Contain("Named presets use shipped copied tracks only"));
        Assert.That(pageXaml, Does.Contain("write a restore manifest in the safe copy"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicAudibleProofContractStatus"));
        Assert.That(pageXaml, Does.Contain("A music swap modifies safe-copy files only"));
        Assert.That(pageXaml, Does.Contain("Audible proof still requires a bounded audio-output capture"));
        Assert.That(pageXaml, Does.Contain("Staging and CDB decode are not audible playback proof."));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicSwapBea02ForBea01PresetButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicSwapBea01ForBea02PresetButton"));
        Assert.That(pageXaml, Does.Contain("BEA_02 over BEA_01"));
        Assert.That(pageXaml, Does.Contain("BEA_01 over BEA_02"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicTargetTrackComboBox"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicReplacementTrackComboBox"));
        Assert.That(pageXaml, Does.Contain("PatchBenchStageCopiedTrackSwapButton"));
        Assert.That(pageXaml, Does.Contain("Swap safe-copy tracks"));
        Assert.That(pageXaml, Does.Contain("Advanced replacement target"));
        Assert.That(pageXaml, Does.Contain("Target track in safe copy"));
        Assert.That(pageXaml, Does.Contain("Replacement track (.ogg)"));
        Assert.That(pageXaml, Does.Contain("Target must be an existing file in the safe copy's data\\Music folder"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicTargetFileName"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicReplacementPath"));
        Assert.That(pageXaml, Does.Contain("PatchBenchStageMusicReplacementButton"));
        Assert.That(pageXaml, Does.Contain("PatchBenchRestoreMusicReplacementButton"));
        Assert.That(pageXaml, Does.Contain("Stage track in safe copy"));
        Assert.That(pageXaml, Does.Contain("Restore safe-copy track backup"));
        Assert.That(pageXaml, Does.Contain("PatchBenchMusicReplacementStatus"));
        Assert.That(pageXaml, Does.Contain("Staging only; in-game playback is still experimental and unproven."));
        Assert.That(pageXaml, Does.Contain("PatchBenchOperationLog"));
        Assert.That(pageXaml, Does.Contain("Advanced: patch one BEA.exe copy"));
        Assert.That(pageXaml, Does.Contain("Advanced copy source"));
        Assert.That(pageXaml, Does.Contain("Browse read-only BEA.exe source"));
        Assert.That(pageXaml, Does.Contain("Use configured source game folder"));
        Assert.That(pageXaml, Does.Contain("Create BEA.exe-only copy"));
        Assert.That(pageXaml, Does.Contain("Advanced copy actions"));
        Assert.That(pageXaml, Does.Contain("Verify BEA.exe-only copy"));
        Assert.That(pageXaml, Does.Contain("Apply to BEA.exe-only copy"));
        Assert.That(pageXaml, Does.Contain("Source path details"));
        Assert.That(pageXaml, Does.Contain("BEA.exe-only copy details"));
        Assert.That(settingsXaml, Does.Contain("Windowed &amp; Mods prepares an app-owned safe game copy"));
        Assert.That(settingsXaml, Does.Contain("Advanced BEA.exe-only patching is separate"));
        Assert.That(pageXaml, Does.Not.Contain("against the installed retail executable"));
    }

    [Test]
    public void PatchBench_RendersEveryVisiblePatchFunctionalArea()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string itemModel = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Models", "BinaryPatchItemModel.cs");
        string catalogJson = ReadRepoFile("patches", "catalog", "patches.v2.json");
        int functionalAreaStart = itemModel.IndexOf("public string FunctionalArea", StringComparison.Ordinal);
        int trackLabelStart = itemModel.IndexOf("public string TrackLabel", StringComparison.Ordinal);
        string functionalAreaSwitch = itemModel[functionalAreaStart..trackLabelStart];

        MatchCollection explicitFunctionalAreaMappings = Regex.Matches(functionalAreaSwitch, "\"(?<key>[^\"]+)\" => \"(?<area>[^\"]+)\"");
        HashSet<string> functionalAreas = explicitFunctionalAreaMappings
            .Select(match => match.Groups["area"].Value)
            .ToHashSet(StringComparer.OrdinalIgnoreCase);
        HashSet<string> mappedPatchKeys = explicitFunctionalAreaMappings
            .Select(match => match.Groups["key"].Value)
            .ToHashSet(StringComparer.OrdinalIgnoreCase);
        HashSet<string> renderedGroups = Regex.Matches(code, "AddGroup\\(\\s*\"(?<area>[^\"]+)\"")
            .Select(match => match.Groups["area"].Value)
            .ToHashSet(StringComparer.OrdinalIgnoreCase);
        using JsonDocument catalog = JsonDocument.Parse(catalogJson);
        HashSet<string> visiblePatchKeys = catalog.RootElement.GetProperty("patches").EnumerateArray()
            .Where(patch => patch.TryGetProperty("selectability", out JsonElement selectability)
                && selectability.GetString()?.EndsWith("_visible", StringComparison.OrdinalIgnoreCase) == true)
            .Select(patch => patch.GetProperty("id").GetString()!)
            .ToHashSet(StringComparer.OrdinalIgnoreCase);

        Assert.That(functionalAreas, Is.Not.Empty);
        Assert.That(renderedGroups, Is.SupersetOf(functionalAreas));
        Assert.That(mappedPatchKeys, Is.SupersetOf(visiblePatchKeys));
    }

    [Test]
    public void PatchBench_CodeRequiresAppOwnedWorkingCopyBeforeApply()
    {
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");
        string itemModel = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Models", "BinaryPatchItemModel.cs");

        Assert.That(code, Does.Contain("GetPatchWorkspaceRoot()"));
        Assert.That(code, Does.Contain("GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(sourcePath)"));
        Assert.That(code, Does.Contain("GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination"));
        Assert.That(code, Does.Contain("File.Copy(validatedSourcePath, copyPath"));
        Assert.That(code, Does.Contain("IsBattleEngineExecutableSourcePath(sourcePath)"));
        Assert.That(code, Does.Contain("ResolveGameExecutablePath(gameDir)"));
        Assert.That(code, Does.Contain("Guid.NewGuid()"));
        Assert.That(code, Does.Contain("if (!IsUsableWorkingCopy(exePath))"));
        Assert.That(code, Does.Contain("BuildSourceExecutableSummary"));
        Assert.That(code, Does.Contain("BuildWorkingCopySummary"));
        Assert.That(code, Does.Contain("FormatPatchLogForUi"));
        Assert.That(code, Does.Contain("app-owned BEA.exe-only copy"));
        Assert.That(code, Does.Contain("BEA.exe-only backup snapshot"));
        Assert.That(code, Does.Contain("BuildPatchTargetOptions(exePath)"));
        Assert.That(code, Does.Contain("AllowedRoot: GetPatchWorkspaceRoot()"));
        Assert.That(code, Does.Contain("AllowByteLayoutOnlyTarget: false"));
        Assert.That(code, Does.Contain("BinaryPatchEngine.VerifyPatchTargetFile(BuildPatchTargetOptions(exePath), selected)"));
        Assert.That(code, Does.Not.Contain("byte[] data = File.ReadAllBytes(exePath);"));
        Assert.That(code, Does.Contain("IsBattleEngineExecutableSourcePath"));
        Assert.That(code, Does.Contain("BEA.exe.original.backup"));
        Assert.That(code, Does.Contain("WindowedPresetButton_Click"));
        Assert.That(code, Does.Contain("ModernGraphicsPresetButton_Click"));
        Assert.That(code, Does.Contain("EnhancedPreviewPresetButton_Click"));
        Assert.That(code, Does.Contain("QuietCaptureLaunchPresetButton_Click"));
        Assert.That(code, Does.Contain("ControlBaselinePresetButton_Click"));
        Assert.That(code, Does.Contain("ControlSharpenedPresetButton_Click"));
        Assert.That(code, Does.Contain("ControlConfig2PresetButton_Click"));
        Assert.That(code, Does.Contain("ControlConfig3PresetButton_Click"));
        Assert.That(code, Does.Contain("ControlConfig4PresetButton_Click"));
        Assert.That(code, Does.Contain("BuildPersistedControlDiagnosticPreset"));
        Assert.That(code, Does.Contain("HighDetailLaunchPresetButton_Click"));
        Assert.That(code, Does.Contain("ClearLaunchOptionsButton_Click"));
        Assert.That(code, Does.Contain("private sealed record LaunchPresetSelection"));
        Assert.That(code, Does.Contain("ApplyLaunchPreset("));
        Assert.That(code, Does.Contain("HighDetailTextureRamLimitMb = \"256\""));
        Assert.That(code, Does.Contain("quiet capture launch preset selected"));
        Assert.That(code, Does.Contain("control diagnostics baseline config 1 selected"));
        Assert.That(code, Does.Contain("control diagnostics sensitivity test config 1 selected"));
        Assert.That(code, Does.Contain("control diagnostics swapped config 2 selected"));
        Assert.That(code, Does.Contain("control diagnostics alternate config 3 selected"));
        Assert.That(code, Does.Contain("control diagnostics swapped alternate config 4 selected"));
        Assert.That(code, Does.Contain("high detail launch preset selected"));
        Assert.That(code, Does.Contain("launch options cleared"));
        Assert.That(code, Does.Contain("TextureRamLimitMb: HighDetailTextureRamLimitMb"));
        Assert.That(code, Does.Contain("PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex = Math.Clamp(preset.ControllerConfigurationIndex, 0, 4)"));
        Assert.That(code, Does.Contain("PatchBenchShowDebugTraceLaunchOption.IsChecked = false"));
        Assert.That(code, Does.Contain("PatchBenchAdminLevelPresetComboBox.SelectedIndex = NoAdminLevelPresetIndex"));
        Assert.That(code, Does.Contain("s_adminLevelPresets"));
        Assert.That(code, Does.Contain("AdminLevelPresetComboBox_SelectionChanged"));
        Assert.That(code, Does.Contain("args.Add(\"-showdebugtrace\")"));
        Assert.That(code, Does.Not.Contain("PatchBenchDevModeLaunchOption"));
        Assert.That(code, Does.Not.Contain("PatchBenchKillHudLaunchOption"));
        Assert.That(code, Does.Not.Contain("PatchBenchModelViewerLaunchOption"));
        Assert.That(code, Does.Not.Contain("args.Add(\"-devmode\")"));
        Assert.That(code, Does.Not.Contain("args.Add(\"-killhud\")"));
        Assert.That(code, Does.Not.Contain("args.Add(\"-modelviewer\")"));
        Assert.That(code, Does.Contain("AppStatusService.SetStatus($\"Windowed & Mods: {preset.StatusMessage}\")"));
        Assert.That(code, Does.Contain("BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId)"));
        Assert.That(code, Does.Contain("BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.RecommendedProfileId)"));
        Assert.That(code, Does.Contain("BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.EnhancedPreviewProfileId)"));
        Assert.That(code, Does.Contain("SelectOnlyKeys(preset.PatchKeys)"));
        Assert.That(code, Does.Contain("PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex = preset.DefaultControllerConfiguration ?? 0"));
        Assert.That(code, Does.Contain("PatchBenchPersistControllerConfigOption.IsChecked = preset.DefaultPersistControllerConfigInOptions"));
        Assert.That(code, Does.Contain("PatchBenchSharpenMouseLookOption.IsChecked = preset.DefaultSharpenMouseLook"));
        Assert.That(code, Does.Contain("PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = DefaultMouseSensitivityPresetIndex"));
        Assert.That(code, Does.Contain("PatchBenchCreateMusicSwapPresetComboBox.SelectedIndex = NoCreateMusicSwapPresetIndex"));
        Assert.That(code, Does.Contain("PatchBenchInvertWalkerYOption.IsChecked = false"));
        Assert.That(code, Does.Contain("PatchBenchInvertFlightYOption.IsChecked = false"));
        Assert.That(code, Does.Contain("ProfilePresetId: MatchSelectableSafeCopyProfileId(selectedPatchKeys)"));
        Assert.That(code, Does.Contain("MusicSwapPresetId: createMusicSwapPresetId"));
        Assert.That(code, Does.Contain("GameProfileMusicReplacementResult? createMusicSwapResult = result.MusicSwapResult"));
        Assert.That(code, Does.Contain("BuildSafeCopyMusicSwapSummary(createMusicSwapResult)"));
        Assert.That(code, Does.Contain("createMusicSwapPreset="));
        Assert.That(code, Does.Contain("GetSelectedCreateMusicSwapPresetId"));
        Assert.That(code, Does.Contain("MatchSelectableSafeCopyProfileId"));
        Assert.That(code, Does.Contain("Enhanced Profile Preview selected. It adds visible safe-copy mods and copied control defaults"));
        Assert.That(code, Does.Contain("pre-fills copied-options controls for config 1 and mouse sensitivity 2.25"));
        Assert.That(code, Does.Contain("\"extra_graphics_default_on\", \"ignore_cardid_tweak_overrides\""));
        Assert.That(code, Does.Contain("UI & Diagnostics"));
        Assert.That(itemModel, Does.Contain("Shows a small PATCHED marker"));
        Assert.That(code, Does.Contain("BinaryPatchEngine.ApplyPatchesToFile(BuildPatchTargetOptions(exePath), selected)"));
        Assert.That(code, Does.Contain("GameProfilePreflightService.PrepareWindowedCompatibilityProfile"));
        Assert.That(code, Does.Contain("GameProfileRuntimeService.LaunchCopiedProfile"));
        Assert.That(code, Does.Contain("App.SafeGameCopyProcesses.Stop(process)"));
        Assert.That(code, Does.Contain("GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy"));
        Assert.That(code, Does.Contain("ListSafeCopyMusicTracks"));
        Assert.That(code, Does.Contain("GetSafeCopyMusicSwapPreset"));
        Assert.That(code, Does.Contain("BuildSafeCopyMusicSwapPresetOptions"));
        Assert.That(code, Does.Contain("UseBea02ForBea01PresetId"));
        Assert.That(code, Does.Contain("UseBea01ForBea02PresetId"));
        Assert.That(code, Does.Contain("GameProfileMusicReplacementService.StageReplacement"));
        Assert.That(code, Does.Contain("GameProfileMusicReplacementService.RestoreReplacement"));
        Assert.That(code, Does.Contain("GameProfilePreflightService.BuildLaunchPlan"));
        Assert.That(code, Does.Contain("GetCopiedProfileWorkspaceRoot()"));
        Assert.That(code, Does.Contain("PatchBenchPrepareCopiedProfileButton"));
        Assert.That(code, Does.Contain("PatchBenchIncludeSavegamesOption"));
        Assert.That(code, Does.Contain("BuildSelectedLaunchArguments"));
        Assert.That(code, Does.Contain("BuildLaunchModifierSummary"));
        Assert.That(code, Does.Contain("RefreshCopiedProfileLaunchPlanPreview"));
        Assert.That(code, Does.Contain("PatchBenchSkipFmvLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchNoMusicLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchNoSoundLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchHighDetailLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchNoStaticShadowsLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchNoRumbleLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchLevelLaunchOption"));
        Assert.That(code, Does.Contain("PatchBenchAdminLevelPresetComboBox"));
        Assert.That(code, Does.Contain("admin level preset final campaign world 800 selected"));
        Assert.That(code, Does.Contain("LocalMultiplayerProbeLevelId = \"850\""));
        Assert.That(code, Does.Contain("LocalMultiplayerProbeButton_Click"));
        Assert.That(code, Does.Contain("PatchBenchConfigurationLaunchPresetComboBox"));
        Assert.That(code, Does.Contain("PatchBenchPersistControllerConfigOption"));
        Assert.That(code, Does.Contain("PatchBenchSharpenMouseLookOption"));
        Assert.That(code, Does.Contain("GetSelectedMouseLookSensitivityPreset"));
        Assert.That(code, Does.Contain("PatchBenchInvertWalkerYOption"));
        Assert.That(code, Does.Contain("InvertWalkerP1Override"));
        Assert.That(code, Does.Contain("invertWalkerY="));
        Assert.That(code, Does.Contain("GameProfileControlOptionsService.ApplyToSafeCopy"));
        Assert.That(code, Does.Contain("mouseLookSensitivity="));
        Assert.That(code, Does.Contain("GetSelectedControllerConfigurationPreset"));
        Assert.That(code, Does.Contain("ControllerConfigP1Override: persistedControllerConfig"));
        Assert.That(code, Does.Contain("ControllerConfigP2Override: persistedControllerConfig"));
        Assert.That(code, Does.Contain("persistedControllerConfig="));
        Assert.That(code, Does.Contain("PatchBenchTextureRamLimitLaunchOption"));
        Assert.That(code, Does.Contain("\"-skipfmv\""));
        Assert.That(code, Does.Contain("\"-nomusic\""));
        Assert.That(code, Does.Contain("\"-nosound\""));
        Assert.That(code, Does.Contain("\"-hidetail\""));
        Assert.That(code, Does.Contain("\"-nostaticshadows\""));
        Assert.That(code, Does.Contain("\"-norumble\""));
        Assert.That(code, Does.Contain("\"-level\""));
        Assert.That(code, Does.Contain("\"-configuration\""));
        Assert.That(code, Does.Contain("\"-textureramlimit\""));
        Assert.That(code, Does.Contain("PatchBenchLaunchCopiedProfileButton"));
        Assert.That(code, Does.Contain("PatchBenchStopCopiedProfileButton"));
        Assert.That(code, Does.Contain("PatchBenchStageCopiedTrackSwapButton"));
        Assert.That(code, Does.Contain("PatchBenchMusicSwapBea02ForBea01PresetButton"));
        Assert.That(code, Does.Contain("PatchBenchMusicSwapBea01ForBea02PresetButton"));
        Assert.That(code, Does.Contain("PatchBenchStageMusicReplacementButton"));
        Assert.That(code, Does.Contain("PatchBenchRestoreMusicReplacementButton"));
        Assert.That(code, Does.Contain("bool canRestoreMusicReplacement"));
        Assert.That(code, Does.Contain("HasMusicReplacementManifest(_lastCopiedProfileRoot)"));
        Assert.That(code, Does.Contain("PatchBenchRestoreMusicReplacementButton.IsEnabled = canRestoreMusicReplacement"));
        Assert.That(code, Does.Contain("App.SafeGameCopyProcesses.Register"));
        Assert.That(code, Does.Contain("App.SafeGameCopyProcesses.Stop"));
        Assert.That(code, Does.Contain("RestoreTrackedSafeGameCopyProcess"));
        Assert.That(ReadRepoFile("OnslaughtCareerEditor.WinUI", "App.xaml.cs"), Does.Contain("GameProfileManagedProcessRegistry"));
        Assert.That(ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs"), Does.Contain("App.SafeGameCopyProcesses.StopAll();"));
        Assert.That(code, Does.Contain("_isPreparingCopiedProfile"));
        Assert.That(code, Does.Contain("_isLaunchingCopiedProfile"));
        Assert.That(code, Does.Contain("_isStoppingCopiedProfile"));
        Assert.That(code, Does.Contain("_isStagingMusicReplacement"));
        Assert.That(code, Does.Contain("_isRestoringMusicReplacement"));
        Assert.That(code, Does.Contain("_managedCopiedProfileProcess"));
        Assert.That(code, Does.Contain("_lastCopiedProfileRoot"));
        Assert.That(code, Does.Contain("_lastMusicReplacementResult"));
        Assert.That(code, Does.Contain("RefreshMusicTrackChoices"));
        Assert.That(code, Does.Contain("ClearMusicTrackChoices"));
        Assert.That(code, Does.Contain("StageCopiedTrackSwapButton_Click"));
        Assert.That(code, Does.Contain("StageMusicSwapPresetAsync"));
        Assert.That(code, Does.Contain("hasSourceExe && !_isPreparingCopiedProfile && !_isLaunchingCopiedProfile && !_isStoppingCopiedProfile && _managedCopiedProfileProcess is null"));
        Assert.That(code, Does.Contain("AllowByteLayoutOnlyTarget: false"));
        Assert.That(code, Does.Not.Contain("AllowByteLayoutOnlyTarget: true"));
        Assert.That(code, Does.Contain("await Task.Run"));
        Assert.That(code, Does.Contain("IncludeSavegames: includeSavegames"));
        Assert.That(code, Does.Contain("BuildSafeCopySavegamesSummary"));
        Assert.That(code, Does.Contain("string[] selectedPatchKeys = GetVisibleSelectedKeys().ToArray();"));
        Assert.That(code, Does.Contain("PatchKeys: selectedPatchKeys"));
        Assert.That(code, Does.Contain("defaultProfileKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId)"));
        Assert.That(code, Does.Contain("PatchBenchSelectedProfileStatus.Text = BuildSelectedProfileStatus(visibleSelectedKeys)"));
        Assert.That(code, Does.Contain("Only the copied BEA.exe was patched"));
        Assert.That(code, Does.Contain("Selected mods are applied when you create the safe game copy. The advanced buttons below patch a separate BEA.exe-only copy and do not create a launchable game folder."));
        Assert.That(code, Does.Contain("No optional mod rows selected. Safe-copy creation still applies the required windowed compatibility pair."));
        Assert.That(code, Does.Contain("This does not confirm it reached the menu, stayed windowed, rendered correctly, or played replacement music."));
        Assert.That(code, Does.Contain("This proves process start only."));
        Assert.That(code, Does.Contain("Any manual input after launch is not counted as automated proof."));
        Assert.That(code, Does.Contain("Stop can close or force-close the copied game after a timeout."));
        Assert.That(code, Does.Not.Contain("windowed rendering parity"));
        Assert.That(code, Does.Not.Contain("Private save folders are not copied by this preflight."));
        Assert.That(code, Does.Contain("Staging only; in-game playback is still experimental and unproven."));
        Assert.That(code, Does.Contain("The original BEA.exe stays unchanged"));
        Assert.That(code, Does.Not.Contain("PatchBenchCopiedProfileLaunchPlan.Text.Trim"));
        Assert.That(code, Does.Not.Contain("PatchBenchCopiedProfileLaunchPlan.Text.Split"));
        Assert.That(code, Does.Not.Contain("Process.Start"));
        Assert.That(code, Does.Not.Contain("ExePathTextBox.Text = candidate"));
    }

    [Test]
    public void PatchBench_SafeCopyReceiptCardUsesAppCoreReceiptModel()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");

        Assert.That(xaml, Does.Contain("PatchBenchCopiedProfileReceiptExpander"));
        Assert.That(xaml, Does.Contain("Safe copy receipt"));
        Assert.That(xaml, Does.Contain("PatchBenchCopiedProfileReceipt"));

        Assert.That(code, Does.Contain("GameProfilePreflightService.BuildPrepareReceipt"));
        Assert.That(code, Does.Contain("RenderSafeCopyReceipt"));
        Assert.That(code, Does.Contain("BuildSafeCopyReceiptText"));
        Assert.That(code, Does.Contain("PatchBenchCopiedProfileReceipt.Text"));
        Assert.That(code, Does.Contain("Included changes"));
        Assert.That(code, Does.Contain("Still not included"));
        Assert.That(code, Does.Contain("No Host/Join or online multiplayer"));
        Assert.That(code, Does.Contain("Play will run BEA.exe from safe copy folder"));
        Assert.That(code, Does.Not.Contain("Play will run BEA.exe from safe copy: {result.TargetGameRoot}"));
        Assert.That(code, Does.Not.Contain("PatchBenchHostOnlineSessionButton"));
        Assert.That(code, Does.Not.Contain("PatchBenchJoinOnlineSessionButton"));
    }

    [Test]
    public void PatchBench_MusicSwapSurfaceExposesLevel100DecodeBackedPreset()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs");

        Assert.That(xaml, Does.Contain("PatchBenchMusicSwapBea02ForBea04PresetButton"));
        Assert.That(xaml, Does.Contain("BEA_02 over BEA_04"));
        Assert.That(xaml, Does.Contain("Audible proof still requires a bounded audio-output capture"));
        Assert.That(code, Does.Contain("UseBea02ForBea04PresetId"));
        Assert.That(code, Does.Contain("PatchBenchMusicSwapBea02ForBea04PresetButton.IsEnabled"));
        Assert.That(code, Does.Contain("MusicSwapBea02ForBea04PresetButton_Click"));
        Assert.That(code, Does.Contain("3 => GameProfileMusicReplacementService.UseBea02ForBea04PresetId"));
        Assert.That(code, Does.Not.Contain("This does not prove the game plays"));
    }

    [Test]
    public void WinUiPrimaryVisibleCopy_DoesNotRenderMarkdownBackticks()
    {
        string[] primaryTextSources =
        {
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml"),
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "AboutPage.xaml"),
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"),
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs"),
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"),
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"),
            ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml")
        };

        foreach (string source in primaryTextSources)
        {
            Assert.That(source, Does.Not.Contain("`"));
        }
    }

    [Test]
    public void SaveLab_VisibleCopyUsesProductLaneName()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");
        string configurationCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs");

        Assert.That(xaml, Does.Contain("Save Lab"));
        Assert.That(xaml, Does.Contain("1. Inspect a file"));
        Assert.That(xaml, Does.Contain("2. Edit a copied save"));
        Assert.That(xaml, Does.Contain("3. Edit game options"));
        Assert.That(xaml, Does.Contain("Edit startup settings, audio levels, and controller bindings from defaultoptions.bea"));
        Assert.That(xaml, Does.Contain("Start here when you want to understand a save or options snapshot"));
        Assert.That(xaml, Does.Contain("AnalyzerEmptyStateBorder"));
        Assert.That(xaml, Does.Contain("AnalyzerHeaderGrid"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerFilePath"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerAnalyzeButton"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerSummaryTitle"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerSummaryTree"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerDocumentTitle"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerFileKindMetric"));
        Assert.That(xaml, Does.Contain("SaveAnalyzerReport"));
        Assert.That(xaml, Does.Contain("SaveEditorInputFile"));
        Assert.That(xaml, Does.Contain("SaveEditorOutputFile"));
        Assert.That(xaml, Does.Contain("SaveEditorPatchButton"));
        Assert.That(xaml, Does.Contain("SaveEditorPendingChanges"));
        Assert.That(xaml, Does.Contain("SaveEditorSafetyHint"));
        Assert.That(xaml, Does.Contain("SaveEditorOutputLog"));
        Assert.That(xaml, Does.Contain("SaveEditorResultInfo"));
        Assert.That(xaml, Does.Contain("Choose a file to see save facts"));
        Assert.That(xaml, Does.Contain("Analysis report appears here after you choose a save or options file."));
        Assert.That(code, Does.Contain("Save Lab: analyzer ready"));
        Assert.That(code, Does.Contain("FormatEditorPatchResultForUi"));
        Assert.That(code, Does.Contain("Successfully patched copied save to selected output file."));
        Assert.That(code, Does.Contain("RedactEditorPatchPaths"));
        Assert.That(code, Does.Contain("AnalyzeTaskButton_Click"));
        Assert.That(code, Does.Contain("EditSaveTaskButton_Click"));
        Assert.That(code, Does.Contain("ConfigureOptionsTaskButton_Click"));
        Assert.That(code, Does.Contain("AnalyzerHeaderGrid.Visibility = Visibility.Collapsed"));
        Assert.That(code, Does.Contain("AnalyzerMetricsGrid.Visibility = Visibility.Collapsed"));
        Assert.That(code, Does.Contain("Choose a detected file"));
        Assert.That(code, Does.Contain("Choose a career save"));
        Assert.That(configurationCode, Does.Contain("Choose an options file"));
        Assert.That(configurationCode, Does.Contain("ConfigurationInputFileTextBox.Text = path;"));
        Assert.That(configurationCode, Does.Contain("ConfigurationOutputFileTextBox.Text = SaveEditorService.BuildDefaultSaveOutputPath(path);"));
        Assert.That(configurationCode, Does.Contain("Game options patch failed."));
        Assert.That(configurationCode, Does.Contain("catch (Exception ex) when (IsUserFacingConfigurationPatchException(ex))"));
        Assert.That(configurationCode, Does.Contain("private static bool IsUserFacingConfigurationPatchException"));
        Assert.That(configurationCode, Does.Not.Contain("Configuration patch failed"));
        Assert.That(code, Does.Not.Contain("Saves:"));
    }

    [Test]
    public void Settings_FramesGameInstallAsReadOnlySourceMaterial()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml.cs");

        Assert.That(xaml, Does.Contain("Configured install"));
        Assert.That(xaml, Does.Contain("Path details"));
        Assert.That(xaml, Does.Contain("Settings file details"));
        Assert.That(xaml, Does.Contain("read-only source material"));
        Assert.That(code, Does.Contain("RenderGameDirectory"));
        Assert.That(code, Does.Contain("BuildFolderSummary"));
        Assert.That(code, Does.Contain("Read-only source material"));
        Assert.That(code, Does.Contain("Configured install"));
    }

    [Test]
    public void MediaPage_HidesSourcePathsInDefaultPlaybackSummaries()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "MediaPage.xaml.cs");

        Assert.That(xaml, Does.Contain("Source folder"));
        Assert.That(xaml, Does.Contain("Path details"));
        Assert.That(xaml, Does.Contain("read-only source material"));
        Assert.That(code, Does.Contain("SetMediaDirectoryDisplay"));
        Assert.That(code, Does.Contain("GetInitialMediaTabIndex"));
        Assert.That(code, Does.Contain("ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB"));
        Assert.That(code, Does.Contain("BuildFolderSummary"));
        Assert.That(code, Does.Contain("BuildAudioSelectionSummary"));
        Assert.That(code, Does.Contain("BuildVideoSelectionSummary"));
        Assert.That(code, Does.Not.Contain("AudioPathTextBlock.Text = item?.FilePath"));
        Assert.That(code, Does.Not.Contain("VideoPathTextBlock.Text = item?.FilePath"));
    }

    [Test]
    public void SaveLab_InfoBars_ExposeStatusAutomationIdsAndVisibilityHelpers()
    {
        string savesXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml");
        string savesCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");
        string configurationCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.Configuration.cs");

        Assert.That(savesXaml, Does.Contain("SaveAnalyzerStatusInfo"));
        Assert.That(savesXaml, Does.Contain("ConfigurationStatusInfo"));
        Assert.That(savesCode, Does.Contain("SetAnalyzerInfoBar"));
        Assert.That(configurationCode, Does.Contain("ConfigurationInfoBar.Visibility = Visibility.Visible"));
    }

    [Test]
    public void Home_DeepLinksToConfigurationEditorTab()
    {
        string homeXaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "HomePage.xaml");
        string homeCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "HomePage.xaml.cs");
        string shellCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs");
        string savesCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs");

        Assert.That(homeXaml, Does.Contain("HomeOpenConfigurationEditorButton"));
        Assert.That(homeCode, Does.Contain("NavigateToTag(\"saves\", saveSubTab: 2)"));
        Assert.That(shellCode, Does.Contain("NavigateToTag(string tag, int? saveSubTab = null)"));
        Assert.That(shellCode, Does.Contain("savesPage.NavigateToSubTab(tabIndex)"));
        Assert.That(savesCode, Does.Contain("public void NavigateToSubTab(int tabIndex)"));
        Assert.That(savesCode, Does.Contain("ConfigurationEditorTabIndex = 2"));
    }

    [Test]
    public void ShellFooter_UsesFriendlyGameDirectoryLabelAndSafeSetupAction()
    {
        string xaml = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml");
        string code = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs");

        Assert.That(xaml, Does.Contain("Review Setup"));
        Assert.That(xaml, Does.Not.Contain("Launch Game"));
        Assert.That(code, Does.Contain("BuildGameDirectoryLabel"));
        Assert.That(code, Does.Contain("ToolTipService.SetToolTip("));
        Assert.That(code, Does.Contain("NavigateToTag(\"settings\")"));
        Assert.That(code, Does.Contain("read-only game install"));
        Assert.That(code, Does.Not.Contain("Process.Start"));
        Assert.That(code, Does.Not.Contain("ResolveGameExecutablePath"));
    }

    [Test]
    public void ShellWindowSize_UsesPersistedNativeAppWindowBounds()
    {
        string config = ReadRepoFile("OnslaughtCareerEditor.AppCore", "AppConfig.cs");
        string shellCode = ReadRepoFile("OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs");

        Assert.That(config, Does.Contain("public int WindowWidth { get; set; } = 1100;"));
        Assert.That(config, Does.Contain("public int WindowHeight { get; set; } = 720;"));
        Assert.That(shellCode, Does.Contain("AppWindow.GetFromWindowId"));
        Assert.That(shellCode, Does.Contain("ApplySavedWindowSize"));
        Assert.That(shellCode, Does.Contain("MainWindow_Closed"));
        Assert.That(shellCode, Does.Contain("config.WindowWidth = Math.Clamp"));
        Assert.That(shellCode, Does.Contain("config.WindowHeight = Math.Clamp"));
        Assert.That(shellCode, Does.Contain("MinWindowWidth"));
        Assert.That(shellCode, Does.Contain("MaxWindowHeight"));
    }

    private static string ReadRepoFile(params string[] relativeParts)
    {
        string path = Path.Combine(relativeParts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }
}
