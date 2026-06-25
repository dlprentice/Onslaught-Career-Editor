using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Imaging;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;
using Windows.ApplicationModel.DataTransfer;
using Windows.UI;
using XamlLine = Microsoft.UI.Xaml.Shapes.Line;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class AssetLibraryPage : Page
    {
        private readonly AssetCatalogService _catalogService = new();
        private AssetCatalogSnapshot _snapshot = AssetCatalogSnapshot.Empty;
        private AssetListKind _selectedKind = AssetListKind.Textures;
        private GoodieBrowserFilter _selectedGoodieFilter = GoodieBrowserFilter.All;
        private TexturePreviewBackground _texturePreviewBackground = TexturePreviewBackground.Neutral;
        private ModelPreviewView _modelPreviewView = ModelPreviewView.Iso;
        private AssetModelGeometryPreview _currentModelGeometryPreview = AssetModelGeometryPreview.Empty;
        private string _selectedExportPath = string.Empty;
        private string _selectedMediaHandoffSearch = string.Empty;
        private string _selectedMediaHandoffLabel = string.Empty;
        private AssetTextureItem? _selectedModelLinkedTexture;
        private string _selectedModelSidecarTexturePath = string.Empty;
        private string _selectedModelSidecarTextureFileName = string.Empty;
        private AssetMaterialImportDryRunPlan? _materialDryRunPlan;
        private AssetMaterialImportPackagePlan? _materialPackagePlan;
        private string _materialPackageOutputRoot = string.Empty;
        private SaveAnalysis? _goodieSaveAnalysis;
        private string _goodieSaveStatePath = string.Empty;

        public AssetLibraryPage()
        {
            InitializeComponent();
            _selectedKind = GetInitialAssetKind();
            UpdateTabStyles();
            ApplyTexturePreviewBackground();

            AppConfig config = AppConfig.Load();
            string? testCatalog = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_ASSET_CATALOG");
            bool hasTestCatalog = !string.IsNullOrWhiteSpace(testCatalog);
            string? configuredCatalog = hasTestCatalog
                ? testCatalog
                : config.AssetCatalogPath;
            string? initialCatalog = hasTestCatalog
                ? AssetCatalogService.FindCatalogCandidates(configuredCatalog).FirstOrDefault()
                : BuildInitialCatalogCandidates(config, configuredCatalog).FirstOrDefault();
            string? catalogToLoad = initialCatalog ?? configuredCatalog;

            CatalogPathTextBox.Text = catalogToLoad ?? string.Empty;
            if (!string.IsNullOrWhiteSpace(catalogToLoad))
            {
                LoadCatalog(catalogToLoad, persist: !hasTestCatalog);
            }
            else
            {
                ResetSelection();
                CatalogStatusTextBlock.Text = BuildMissingCatalogStatus(catalogToLoad);
                CatalogSummaryTextBlock.Text = "Load a generated catalog to see textures, meshes, and goodies.";
                CatalogCoverageTextBlock.Text = "Coverage summary appears after a generated catalog loads.";
                CatalogProvenanceTextBlock.Text = "Catalog provenance appears after a generated catalog loads.";
                CatalogFullPathTextBlock.Text = string.Empty;
                AppStatusService.SetStatus("Asset Library: choose a generated catalog");
            }

            string? testGoodieSave = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_GOODIE_SAVE");
            if (!string.IsNullOrWhiteSpace(testGoodieSave))
            {
                LoadGoodieSaveState(testGoodieSave, updateInput: false);
            }
        }

        private static IReadOnlyList<string> BuildInitialCatalogCandidates(AppConfig config, string? configuredCatalog)
        {
            _ = config.GetGameDirOrDetect(persistDetection: true);
            return AssetCatalogService.FindCatalogCandidates(configuredCatalog);
        }

        private async void BrowseCatalogButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance == null)
            {
                AppStatusService.SetStatus("Asset Library: main window is not ready");
                return;
            }

            string? folder = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
            if (string.IsNullOrWhiteSpace(folder))
            {
                return;
            }

            CatalogPathTextBox.Text = folder;
            LoadCatalog(folder, persist: true);
        }

        private void LoadCatalogButton_Click(object sender, RoutedEventArgs e)
        {
            LoadCatalog(CatalogPathTextBox.Text, persist: true);
        }

        private void LoadCatalog(string? path, bool persist)
        {
            _snapshot = _catalogService.Load(path);
            if (string.IsNullOrWhiteSpace(_snapshot.CatalogFilePath))
            {
                _materialDryRunPlan = null;
                _materialPackagePlan = null;
                _materialPackageOutputRoot = string.Empty;
                CatalogInputGrid.Visibility = Visibility.Visible;
                ChangeCatalogButton.Visibility = Visibility.Collapsed;
                CatalogStatusTextBlock.Text = BuildMissingCatalogStatus(path);
                CatalogSummaryTextBlock.Text = "Load a catalog to see textures, meshes, and goodies.";
                CatalogCoverageTextBlock.Text = "Coverage summary appears after a generated catalog loads.";
                CatalogProvenanceTextBlock.Text = "Catalog provenance appears after a generated catalog loads.";
                CatalogFullPathTextBlock.Text = path ?? string.Empty;
                AppStatusService.SetStatus("Asset Library: catalog not found");
                AssetItemsListView.ItemsSource = null;
                ResetSelection();
                return;
            }

            CatalogInputGrid.Visibility = Visibility.Collapsed;
            ChangeCatalogButton.Visibility = Visibility.Visible;
            CatalogPathTextBox.Text = string.Empty;
            CatalogPathTextBox.PlaceholderText = "Paste catalog.json path or browse to a generated export folder";
            RefreshMaterialImportPlans();
            _materialPackageOutputRoot = BuildMaterialPackageOutputRoot(_snapshot.CatalogFilePath);
            UpdateMaterialPackageOutputStatus();
            CatalogStatusTextBlock.Text = $"Catalog loaded: {BuildPathSummary(_snapshot.CatalogFilePath)}";
            CatalogFullPathTextBlock.Text = _snapshot.CatalogFilePath;
            CatalogSummaryTextBlock.Text =
                $"{_snapshot.Summary.TextureCount} textures, {_snapshot.Summary.LooseMeshCount} loose meshes, {_snapshot.Summary.EmbeddedMeshCount} embedded meshes, {_snapshot.Summary.GoodieCount} goodies";
            CatalogCoverageTextBlock.Text = BuildCatalogCoverageSummary();
            CatalogProvenanceTextBlock.Text = BuildCatalogProvenanceSummary();
            AppStatusService.SetStatus("Asset Library: catalog loaded");

            if (persist)
            {
                AppConfig config = AppConfig.Load();
                config.AssetCatalogPath = _snapshot.CatalogFilePath;
                config.Save();
            }

            UpdateAssetList();
        }

        private static string BuildMissingCatalogStatus(string? attemptedPath)
        {
            string? gameDir = AppConfig.Load().GetGameDirOrDetect(persistDetection: true);
            return AssetCatalogLoadStatusText.BuildMissingCatalogStatus(attemptedPath, gameDir);
        }

        private string BuildCatalogCoverageSummary()
        {
            if (string.IsNullOrWhiteSpace(_snapshot.CatalogFilePath))
            {
                return "Coverage summary appears after a generated catalog loads.";
            }

            int exportedTextures = _snapshot.Textures.Count(static texture => texture.ExportExists);
            int exportedLooseMeshes = _snapshot.LooseMeshes.Count(static mesh => mesh.ExportExists);
            int exportedEmbeddedMeshes = _snapshot.EmbeddedMeshes.Count(static mesh => mesh.ExportExists);
            int modelRows = _snapshot.Summary.LooseMeshCount + _snapshot.Summary.EmbeddedMeshCount;
            int exportedModelRows = exportedLooseMeshes + exportedEmbeddedMeshes;
            int wireframeRows =
                _snapshot.LooseMeshes.Count(static mesh => mesh.ModelSummary.GeometryPreview.Available) +
                _snapshot.EmbeddedMeshes.Count(static mesh => mesh.ModelSummary.GeometryPreview.Available);
            AssetModelPreviewCoverage modelCoverage = new AssetModelPreviewCoverageService().Build(_snapshot, sampleLimit: 0);
            AssetMaterialImportPlan materialPlan = new AssetMaterialImportPlanService().Build(_snapshot, sampleLimit: 0);
            AssetMaterialImportDryRunPlan materialDryRunPlan = _materialDryRunPlan ?? BuildMaterialDryRunPlan();
            GoodiePreviewCoverage goodieCoverage = new GoodiePreviewCoverageService().Build(_snapshot, sampleLimit: 0);
            string materialSlotSummary = BuildModelCoverageSlotSummary(modelCoverage.TextureToMaterialSlotNames);
            int resolvedDryRunTextureOperations =
                materialDryRunPlan.CatalogTextureOperations + materialDryRunPlan.SidecarTextureOperations;

            return
                $"Real local extraction: {exportedTextures}/{_snapshot.Summary.TextureCount} texture PNG previews, " +
                $"{exportedModelRows}/{modelRows} FBX model exports, {wireframeRows} wireframe previews, " +
                $"{modelCoverage.RowsWithTextureCoordinates}/{modelCoverage.TotalModelRows} model rows report UV mapping metadata, " +
                $"{modelCoverage.RowsWithMaterialAssignmentIndices}/{modelCoverage.TotalModelRows} model rows report material assignment metadata, " +
                $"{modelCoverage.RowsWithTextureToMaterialConnections}/{modelCoverage.TotalModelRows} model rows report texture-material link metadata, " +
                $"{modelCoverage.RowsWithTextureToMaterialSlotNames}/{modelCoverage.TotalModelRows} model rows report material slots ({materialSlotSummary}), " +
                $"{modelCoverage.RowsWithCatalogMatchedTextureBindingFiles}/{modelCoverage.TotalModelRows} model rows have direct catalog texture links, " +
                $"{modelCoverage.RowsWithAllTextureBindingFilesCatalogMatched}/{modelCoverage.RowsWithTextureBindings} model rows have all texture bindings in the texture catalog, " +
                $"{materialPlan.TotalCatalogMatchedTextureBindingFiles}/{materialPlan.TotalTextureBindingFiles} readable texture binding files resolve through catalog rows, " +
                $"{materialPlan.TotalCatalogMissingSidecarTextureFiles}/{materialPlan.TotalCatalogMissingTextureBindingFiles} catalog-missing texture binding files have sidecar previews, " +
                $"{materialPlan.TotalUnresolvedTextureBindingFiles} unresolved material import binding files, " +
                $"{materialDryRunPlan.ReadyModelOperations}/{materialDryRunPlan.TotalModelOperations} material import dry-run model operations ready, " +
                $"{resolvedDryRunTextureOperations}/{materialDryRunPlan.TotalTextureOperations} material import dry-run texture operations resolved, " +
                $"{materialDryRunPlan.UnresolvedTextureOperations} unresolved dry-run texture operations, " +
                $"{goodieCoverage.TexturePreviewReadyRows}/{goodieCoverage.TextureBearingRows} texture Goodies preview-ready, " +
                $"{goodieCoverage.ModelWireframeReadyRows}/{goodieCoverage.ModelBearingRows} model Goodies wireframe-ready, " +
                $"{goodieCoverage.VideoCatalogLinkedRows}/{goodieCoverage.VideoRows} video Goodies linked. " +
                "Model viewing is wireframe/export-based; textured 3D rendering is future work.";
        }

        private static string BuildModelCoverageSlotSummary(IReadOnlyList<string> slotNames)
        {
            if (slotNames.Count == 0)
            {
                return "no named material slots yet";
            }

            string sample = string.Join(", ", slotNames.Take(4));
            return slotNames.Count <= 4 ? sample : $"{sample}, +{slotNames.Count - 4} more";
        }

        private string BuildCatalogProvenanceSummary()
        {
            if (string.IsNullOrWhiteSpace(_snapshot.CatalogFilePath))
            {
                return "Catalog provenance appears after a generated catalog loads.";
            }

            string scope = LooksLikeBroadPcInstallCatalog()
                ? "broad PC-install export from local game files, not source-tree sample data"
                : "smaller generated catalog";
            return
                $"Catalog provenance: {scope}. Previews use local exported PNG and FBX files; " +
                "model display is metadata and wireframe geometry, not final textured 3D rendering. " +
                "Private assets stay local; in-game Goodies behavior is not shown here.";
        }

        private bool LooksLikeBroadPcInstallCatalog()
        {
            return _snapshot.Summary.TextureCount >= 800 &&
                   _snapshot.Summary.LooseMeshCount >= 200 &&
                   _snapshot.Summary.EmbeddedMeshCount >= 100 &&
                   _snapshot.Summary.GoodieCount >= 200;
        }

        private void ChangeCatalogButton_Click(object sender, RoutedEventArgs e)
        {
            CatalogInputGrid.Visibility = Visibility.Visible;
            ChangeCatalogButton.Visibility = Visibility.Collapsed;
            CatalogPathTextBox.Focus(FocusState.Programmatic);
        }

        private void TexturesTabButton_Click(object sender, RoutedEventArgs e)
        {
            SelectAssetKind(AssetListKind.Textures);
        }

        private void MeshesTabButton_Click(object sender, RoutedEventArgs e)
        {
            SelectAssetKind(AssetListKind.LooseMeshes);
        }

        private void EmbeddedMeshesTabButton_Click(object sender, RoutedEventArgs e)
        {
            SelectAssetKind(AssetListKind.EmbeddedMeshes);
        }

        private void GoodiesTabButton_Click(object sender, RoutedEventArgs e)
        {
            SelectAssetKind(AssetListKind.Goodies);
        }

        private void SelectAssetKind(AssetListKind kind)
        {
            _selectedKind = kind;
            UpdateTabStyles();
            UpdateAssetList();
        }

        private void UpdateTabStyles()
        {
            Style activeStyle = (Style)Application.Current.Resources["SubTabActiveButtonStyle"];
            Style inactiveStyle = (Style)Application.Current.Resources["SubTabInactiveButtonStyle"];
            TexturesTabButton.Style = _selectedKind == AssetListKind.Textures ? activeStyle : inactiveStyle;
            MeshesTabButton.Style = _selectedKind == AssetListKind.LooseMeshes ? activeStyle : inactiveStyle;
            EmbeddedMeshesTabButton.Style = _selectedKind == AssetListKind.EmbeddedMeshes ? activeStyle : inactiveStyle;
            GoodiesTabButton.Style = _selectedKind == AssetListKind.Goodies ? activeStyle : inactiveStyle;
            GoodieFilterPanel.Visibility = _selectedKind == AssetListKind.Goodies ? Visibility.Visible : Visibility.Collapsed;
            GoodieSaveStatePanel.Visibility = _selectedKind == AssetListKind.Goodies ? Visibility.Visible : Visibility.Collapsed;
            UpdateGoodieFilterStyles();
        }

        private void GoodiesAllFilterButton_Click(object sender, RoutedEventArgs e)
        {
            SetGoodieFilter(GoodieBrowserFilter.All);
        }

        private void GoodiesWallFilterButton_Click(object sender, RoutedEventArgs e)
        {
            SetGoodieFilter(GoodieBrowserFilter.Wall);
        }

        private void GoodiesHiddenFilterButton_Click(object sender, RoutedEventArgs e)
        {
            SetGoodieFilter(GoodieBrowserFilter.Hidden);
        }

        private void GoodiesModelsFilterButton_Click(object sender, RoutedEventArgs e)
        {
            SetGoodieFilter(GoodieBrowserFilter.Models);
        }

        private void GoodiesArtworkFilterButton_Click(object sender, RoutedEventArgs e)
        {
            SetGoodieFilter(GoodieBrowserFilter.Artwork);
        }

        private void GoodiesVideosFilterButton_Click(object sender, RoutedEventArgs e)
        {
            SetGoodieFilter(GoodieBrowserFilter.Videos);
        }

        private void SetGoodieFilter(GoodieBrowserFilter filter)
        {
            _selectedGoodieFilter = filter;
            UpdateGoodieFilterStyles();
            UpdateAssetList();
            AppStatusService.SetStatus($"Asset Library: Goodies filter set to {BuildGoodieFilterLabel(filter).ToLowerInvariant()}");
        }

        private void UpdateGoodieFilterStyles()
        {
            Style activeStyle = (Style)Application.Current.Resources["SubTabActiveButtonStyle"];
            Style inactiveStyle = (Style)Application.Current.Resources["SubTabInactiveButtonStyle"];
            GoodiesAllFilterButton.Style = _selectedGoodieFilter == GoodieBrowserFilter.All ? activeStyle : inactiveStyle;
            GoodiesWallFilterButton.Style = _selectedGoodieFilter == GoodieBrowserFilter.Wall ? activeStyle : inactiveStyle;
            GoodiesHiddenFilterButton.Style = _selectedGoodieFilter == GoodieBrowserFilter.Hidden ? activeStyle : inactiveStyle;
            GoodiesModelsFilterButton.Style = _selectedGoodieFilter == GoodieBrowserFilter.Models ? activeStyle : inactiveStyle;
            GoodiesArtworkFilterButton.Style = _selectedGoodieFilter == GoodieBrowserFilter.Artwork ? activeStyle : inactiveStyle;
            GoodiesVideosFilterButton.Style = _selectedGoodieFilter == GoodieBrowserFilter.Videos ? activeStyle : inactiveStyle;
            UpdateGoodieFilterStatus();
        }

        private void AssetSearchBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateAssetList();
        }

        private void UpdateAssetList()
        {
            string search = AssetSearchBox.Text?.Trim() ?? string.Empty;
            object[] items = (_selectedKind switch
            {
                AssetListKind.LooseMeshes => Filter(_snapshot.LooseMeshes, search),
                AssetListKind.EmbeddedMeshes => Filter(_snapshot.EmbeddedMeshes, search),
                AssetListKind.Goodies => Filter(BuildGoodieBrowserItems(), search),
                _ => Filter(_snapshot.Textures, search)
            }).Cast<object>().ToArray();

            AssetItemsListView.ItemsSource = items;
            if (_selectedKind == AssetListKind.Goodies)
            {
                UpdateGoodieFilterStatus();
            }

            if (items.Length > 0)
            {
                AssetItemsListView.SelectedIndex = 0;
            }
            else
            {
                ResetSelection();
            }
        }

        private static IEnumerable Filter<T>(IEnumerable<T> items, string search) where T : class
        {
            if (string.IsNullOrWhiteSpace(search))
            {
                return items;
            }

            return items.Where(item => item.ToString()?.Contains(search, StringComparison.OrdinalIgnoreCase) == true);
        }

        private void AssetItemsListView_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            switch (AssetItemsListView.SelectedItem)
            {
                case AssetTextureItem texture:
                    ShowTexture(texture);
                    break;
                case AssetLooseMeshItem mesh:
                    ShowLooseMesh(mesh);
                    break;
                case AssetEmbeddedMeshItem mesh:
                    ShowEmbeddedMesh(mesh);
                    break;
                case AssetGoodieBrowserItem goodie:
                    ShowGoodie(goodie.CatalogItem, goodie.SaveState);
                    break;
                default:
                    ResetSelection();
                    break;
            }
        }

        private async void BrowseGoodieSaveStateButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance == null)
            {
                AppStatusService.SetStatus("Asset Library: main window is not ready");
                return;
            }

            string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, [".bes"]);
            if (string.IsNullOrWhiteSpace(path))
            {
                return;
            }

            GoodieSaveStatePathTextBox.Text = path;
            LoadGoodieSaveState(path, updateInput: false);
        }

        private void LoadGoodieSaveStateButton_Click(object sender, RoutedEventArgs e)
        {
            LoadGoodieSaveState(GoodieSaveStatePathTextBox.Text, updateInput: false);
        }

        private void ClearGoodieSaveStateButton_Click(object sender, RoutedEventArgs e)
        {
            _goodieSaveAnalysis = null;
            _goodieSaveStatePath = string.Empty;
            GoodieSaveStatePathTextBox.Text = string.Empty;
            GoodieSaveStateStatusTextBlock.Text = "Save state not loaded. Goodies rows are showing catalog identity only.";
            AppStatusService.SetStatus("Asset Library: Goodies save state cleared");
            UpdateAssetList();
        }

        private void LoadGoodieSaveState(string? path, bool updateInput)
        {
            if (string.IsNullOrWhiteSpace(path) || !File.Exists(path))
            {
                _goodieSaveAnalysis = null;
                _goodieSaveStatePath = string.Empty;
                GoodieSaveStateStatusTextBlock.Text = "Save state not loaded. Choose a copied .bes save to show locked, newly unlocked, and viewed Goodies states.";
                AppStatusService.SetStatus("Asset Library: Goodies save state not loaded");
                UpdateAssetList();
                return;
            }

            SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(path);
            if (!analysis.IsValid)
            {
                _goodieSaveAnalysis = null;
                _goodieSaveStatePath = string.Empty;
                GoodieSaveStateStatusTextBlock.Text = $"{BuildPathSummary(path)} is not a valid BEA save buffer.";
                AppStatusService.SetStatus("Asset Library: Goodies save state invalid");
                UpdateAssetList();
                return;
            }

            _goodieSaveAnalysis = analysis;
            _goodieSaveStatePath = path;
            if (updateInput)
            {
                GoodieSaveStatePathTextBox.Text = path;
            }

            int unlocked = analysis.GoodieStates.Count(static state => state.IsDisplayable && state.IsUnlocked);
            int displayable = analysis.GoodieStates.Count(static state => state.IsDisplayable);
            GoodieSaveStateStatusTextBlock.Text = $"Loaded Goodies state from {BuildPathSummary(path)}: {unlocked}/{displayable} displayable slots unlocked or viewed.";
            AppStatusService.SetStatus("Asset Library: Goodies save state loaded");
            UpdateAssetList();
        }

        private void ShowTexture(AssetTextureItem texture)
        {
            SelectedAssetTitleTextBlock.Text = texture.DisplayName;
            SelectedAssetSummaryTextBlock.Text =
                $"{texture.SourceGroup}; {texture.PackedReferenceCount} packed references; export {BuildAvailability(texture.ExportExists)}.";
            SelectedExportPathTextBlock.Text = texture.ExportPath;
            SelectedCatalogIdTextBlock.Text = texture.CatalogId;
            GoodieFactsPanel.Visibility = Visibility.Collapsed;
            PreviewTitleTextBlock.Text = "Texture preview";
            ConfigureExportActions(texture.ExportPath, texture.ExportExists, "Open texture");
            TexturePreviewPanel.Visibility = Visibility.Visible;
            TexturePreviewBackgroundPanel.Visibility = Visibility.Visible;
            TexturePreviewCanvasNoteTextBlock.Visibility = Visibility.Visible;
            ModelMetadataPanel.Visibility = Visibility.Collapsed;
            ModelMetadataInlineTextBlock.Visibility = Visibility.Collapsed;
            ModelWireframePreviewPanel.Visibility = Visibility.Collapsed;
            ModelViewControlsPanel.Visibility = Visibility.Collapsed;
            ModelWireframeStatusTextBlock.Visibility = Visibility.Collapsed;
            ModelWireframeNoteTextBlock.Visibility = Visibility.Collapsed;
            TexturePreviewEmptyTextBlock.Text = texture.ExportExists
                ? "Loading texture preview..."
                : "Texture export is not available at the recorded local path.";
            ModelTextureLinksTextBlock.Text = "Catalog texture links appear when a model export is selected.";
            ModelPackagePlanTextBlock.Text = "Material package plan appears here when a model export is selected.";
            UpdateMaterialPackageOutputStatus();
            ClearSelectedModelLinkedTexture();

            if (!texture.ExportExists)
            {
                TexturePreviewImage.Source = null;
                TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
                return;
            }

            try
            {
                TexturePreviewImage.Source = new BitmapImage(new Uri(texture.ExportPath));
                TexturePreviewEmptyTextBlock.Visibility = Visibility.Collapsed;
            }
            catch (Exception ex) when (ex is ArgumentException or UriFormatException or IOException)
            {
                TexturePreviewImage.Source = null;
                TexturePreviewEmptyTextBlock.Text = "Texture export exists, but the preview could not be opened.";
                TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
            }
        }

        private void ShowLooseMesh(AssetLooseMeshItem mesh)
        {
            SelectedAssetTitleTextBlock.Text = mesh.DisplayName;
            SelectedAssetSummaryTextBlock.Text =
                $"{mesh.PackedReferenceCount} packed references; FBX export {BuildAvailability(mesh.ExportExists)}. Use the in-app wireframe for a quick geometry check, then open the FBX for full material review.";
            SelectedExportPathTextBlock.Text = mesh.ExportPath;
            SelectedCatalogIdTextBlock.Text = mesh.CatalogId;
            GoodieFactsPanel.Visibility = Visibility.Collapsed;
            PreviewTitleTextBlock.Text = $"Model export: {mesh.DisplayName}";
            ConfigureExportActions(mesh.ExportPath, mesh.ExportExists, "Open model");
            TexturePreviewImage.Source = null;
            TexturePreviewPanel.Visibility = Visibility.Collapsed;
            TexturePreviewBackgroundPanel.Visibility = Visibility.Collapsed;
            TexturePreviewCanvasNoteTextBlock.Visibility = Visibility.Collapsed;
            TexturePreviewEmptyTextBlock.Text = mesh.ModelSummary.MetadataAvailable
                ? "Model metadata and wireframe preview are shown below. Open the FBX for full material review."
                : "Model export is ready for a local FBX viewer. Wireframe preview needs model geometry metadata.";
            TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
            RenderModelSummary(mesh.ModelSummary, mesh.ExportPath);
            RenderModelPackagePlan(mesh.CatalogId);
        }

        private void ShowEmbeddedMesh(AssetEmbeddedMeshItem mesh)
        {
            SelectedAssetTitleTextBlock.Text = mesh.DisplayName;
            SelectedAssetSummaryTextBlock.Text =
                $"{mesh.SourceArchive}; FBX export {BuildAvailability(mesh.ExportExists)}. Use the in-app wireframe for a quick geometry check, then open the FBX for full material review.";
            SelectedExportPathTextBlock.Text = mesh.ExportPath;
            SelectedCatalogIdTextBlock.Text = mesh.CatalogId;
            GoodieFactsPanel.Visibility = Visibility.Collapsed;
            PreviewTitleTextBlock.Text = $"Embedded model export: {mesh.DisplayName}";
            ConfigureExportActions(mesh.ExportPath, mesh.ExportExists, "Open model");
            TexturePreviewImage.Source = null;
            TexturePreviewPanel.Visibility = Visibility.Collapsed;
            TexturePreviewBackgroundPanel.Visibility = Visibility.Collapsed;
            TexturePreviewCanvasNoteTextBlock.Visibility = Visibility.Collapsed;
            TexturePreviewEmptyTextBlock.Text = mesh.ModelSummary.MetadataAvailable
                ? "Embedded model metadata and wireframe preview are shown below. Open the FBX for full material review."
                : "Embedded model export is ready for a local FBX viewer. Wireframe preview needs model geometry metadata.";
            TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
            RenderModelSummary(mesh.ModelSummary, mesh.ExportPath);
            RenderModelPackagePlan(mesh.CatalogId);
        }

        private void ShowGoodie(AssetGoodieItem goodie, GoodieStateDetail? saveState)
        {
            AssetLooseMeshItem? matchingMesh = FindLooseMesh(goodie.PrimaryMeshRef);
            AssetTextureItem? matchingTexture = FindTexture(goodie.PrimaryTextureRef);

            if (matchingMesh != null)
            {
                ShowLooseMesh(matchingMesh);
                PreviewTitleTextBlock.Text = $"Goodie model: {goodie.DisplayName}";
            }
            else if (matchingTexture != null)
            {
                ShowTexture(matchingTexture);
                PreviewTitleTextBlock.Text = $"Goodie artwork: {goodie.DisplayName}";
            }
            else
            {
                SelectedExportPathTextBlock.Text = string.Empty;
                ConfigureExportActions(string.Empty, exists: false, label: "Open export");
                TexturePreviewImage.Source = null;
                TexturePreviewPanel.Visibility = Visibility.Visible;
                TexturePreviewBackgroundPanel.Visibility = Visibility.Collapsed;
                TexturePreviewCanvasNoteTextBlock.Visibility = Visibility.Collapsed;
                ModelMetadataPanel.Visibility = Visibility.Collapsed;
                ModelMetadataInlineTextBlock.Visibility = Visibility.Collapsed;
                ModelWireframePreviewPanel.Visibility = Visibility.Collapsed;
                ModelViewControlsPanel.Visibility = Visibility.Collapsed;
                ModelWireframeStatusTextBlock.Visibility = Visibility.Collapsed;
                ModelWireframeNoteTextBlock.Visibility = Visibility.Collapsed;
                ClearSelectedModelLinkedTexture();
                _currentModelGeometryPreview = AssetModelGeometryPreview.Empty;
                PreviewTitleTextBlock.Text = $"Goodie entry: {goodie.DisplayName}";
                TexturePreviewEmptyTextBlock.Text = goodie.HasVideo
                    ? $"Cutscene {goodie.VideoSequenceId} is linked in the media catalog. Use Media playback for Bink preparation and playback."
                    : "This goodie is cataloged, but no matching local preview export is available yet.";
                TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
                if (goodie.HasVideo && !string.IsNullOrWhiteSpace(goodie.VideoSequenceId))
                {
                    ConfigureMediaHandoff(goodie.VideoSequenceId, goodie.DisplayName);
                }
            }

            SelectedAssetTitleTextBlock.Text = goodie.DisplayName;
            SelectedAssetSummaryTextBlock.Text = BuildGoodieSummary(goodie, matchingTexture != null, matchingMesh != null, saveState);
            SelectedCatalogIdTextBlock.Text = goodie.CatalogId;
            RenderGoodieFacts(goodie, saveState);
        }

        private void RenderGoodieFacts(AssetGoodieItem goodie, GoodieStateDetail? saveState)
        {
            GoodieFactsPanel.Visibility = Visibility.Visible;
            GoodieFactStateTextBlock.Text = saveState?.StateLabel ?? "Not loaded";
            GoodieFactWallTextBlock.Text = goodie.IsSourceGridVisible
                ? $"{goodie.WallGroupLabel}; {goodie.WallPositionLabel}"
                : goodie.WallVisibilitySummary;
            GoodieFactUnlockTextBlock.Text = goodie.UnlockRequirement;
            GoodieFactRewardTextBlock.Text = BuildGoodieRewardFact(goodie);
            GoodieFactEvidenceTextBlock.Text = goodie.IsSourceGridVisible
                ? $"{goodie.WallVisibilityEvidenceLabel}; {goodie.UnlockEvidenceLabel}."
                : $"{goodie.WallVisibilityEvidenceLabel}; in-game reachability is not shown here.";
        }

        private static string BuildGoodieRewardFact(AssetGoodieItem goodie)
        {
            string reward = $"{goodie.ContentKind} reward";
            if (goodie.HasModel)
            {
                return $"{reward}; {goodie.MeshRefs.Count} model link(s), {goodie.TextureRefs.Count} texture link(s).";
            }

            if (goodie.HasTexture)
            {
                return $"{reward}; {goodie.TextureRefs.Count} artwork texture link(s).";
            }

            if (goodie.HasVideo)
            {
                return $"{reward}; opens Media for cutscene {goodie.VideoSequenceId}.";
            }

            return $"{reward}; no local preview export is linked yet.";
        }

        private string BuildGoodieSummary(AssetGoodieItem goodie, bool matchedTexture, bool matchedMesh, GoodieStateDetail? saveState)
        {
            string textureSummary = goodie.TextureRefs.Count == 1
                ? "1 texture link"
                : $"{goodie.TextureRefs.Count} texture links";
            string meshSummary = goodie.MeshRefs.Count == 1
                ? "1 model link"
                : $"{goodie.MeshRefs.Count} model links";
            string previewSummary = matchedMesh
                ? "matched to an extracted model export"
                : matchedTexture
                    ? "matched to an extracted artwork export"
                    : goodie.HasVideo
                        ? $"linked to cutscene {goodie.VideoSequenceId}"
                        : "cataloged without a local preview export";

            string stateSummary = saveState == null
                ? "save state not loaded"
                : $"save state: {saveState.StateLabel.ToLowerInvariant()}";
            return $"{stateSummary}; {goodie.ContentKind} reward; {textureSummary}; {meshSummary}; {previewSummary}. Facts below show wall placement and unlock evidence.";
        }

        private IReadOnlyList<AssetGoodieBrowserItem> BuildGoodieBrowserItems()
        {
            Dictionary<int, GoodieStateDetail> states = _goodieSaveAnalysis?.GoodieStates
                .Where(static state => state.IsDisplayable)
                .ToDictionary(static state => state.Index)
                ?? new Dictionary<int, GoodieStateDetail>();

            return _snapshot.Goodies
                .Where(ShouldShowGoodie)
                .Select(goodie =>
                {
                    states.TryGetValue(goodie.Index, out GoodieStateDetail? state);
                    return new AssetGoodieBrowserItem(goodie, state);
                })
                .ToArray();
        }

        private bool ShouldShowGoodie(AssetGoodieItem goodie)
        {
            return _selectedGoodieFilter switch
            {
                GoodieBrowserFilter.Wall => goodie.IsSourceGridVisible,
                GoodieBrowserFilter.Hidden => !goodie.IsSourceGridVisible,
                GoodieBrowserFilter.Models => goodie.HasModel,
                GoodieBrowserFilter.Artwork => goodie.HasTexture && !goodie.HasModel && !goodie.HasVideo,
                GoodieBrowserFilter.Videos => goodie.HasVideo,
                _ => true
            };
        }

        private static string BuildGoodieFilterLabel(GoodieBrowserFilter filter)
        {
            return filter switch
            {
                GoodieBrowserFilter.Wall => "Wall",
                GoodieBrowserFilter.Hidden => "Hidden",
                GoodieBrowserFilter.Models => "Models",
                GoodieBrowserFilter.Artwork => "Artwork",
                GoodieBrowserFilter.Videos => "Videos",
                _ => "All"
            };
        }

        private void UpdateGoodieFilterStatus()
        {
            int filteredCount = _snapshot.Goodies.Count(ShouldShowGoodie);
            string count = filteredCount.ToString("N0", CultureInfo.InvariantCulture);
            GoodiesFilterStatusTextBlock.Text = _selectedGoodieFilter switch
            {
                GoodieBrowserFilter.Wall =>
                    $"Showing {count} Goodies with known wall coordinates from static grid mapping.",
                GoodieBrowserFilter.Hidden =>
                    $"Showing {count} shipped Goodies without a known wall coordinate; this is static catalog evidence, not runtime reachability.",
                GoodieBrowserFilter.Models =>
                    $"Showing {count} model Goodies from static catalog links; textured in-game model viewing is separate runtime work.",
                GoodieBrowserFilter.Artwork =>
                    $"Showing {count} artwork Goodies from static texture links.",
                GoodieBrowserFilter.Videos =>
                    $"Showing {count} video Goodies linked to the media catalog.",
                _ =>
                    $"Showing {count} cataloged Goodies. Filters use catalog links; in-game wall availability is not shown here."
            };
        }

        private AssetTextureItem? FindTexture(string canonicalRef)
        {
            string normalized = NormalizeAssetRef(canonicalRef);
            if (string.IsNullOrWhiteSpace(normalized))
            {
                return null;
            }

            return _snapshot.Textures.FirstOrDefault(texture =>
                NormalizeAssetRef(texture.CanonicalRef) == normalized ||
                NormalizeAssetRef(texture.CanonicalRef).EndsWith(normalized, StringComparison.OrdinalIgnoreCase));
        }

        private AssetLooseMeshItem? FindLooseMesh(string canonicalRef)
        {
            string normalized = NormalizeAssetRef(canonicalRef);
            if (string.IsNullOrWhiteSpace(normalized))
            {
                return null;
            }

            return _snapshot.LooseMeshes.FirstOrDefault(mesh =>
                NormalizeAssetRef(mesh.CanonicalRef) == normalized ||
                NormalizeAssetRef(mesh.CanonicalRef).EndsWith(normalized, StringComparison.OrdinalIgnoreCase));
        }

        private static string NormalizeAssetRef(string? value)
        {
            return string.IsNullOrWhiteSpace(value)
                ? string.Empty
                : value.Replace('\\', '/').Trim().ToLowerInvariant();
        }

        private void ResetSelection()
        {
            SelectedAssetTitleTextBlock.Text = "Choose an asset";
            SelectedAssetSummaryTextBlock.Text = "Pick a texture, mesh, or goodie to review local export status.";
            SelectedExportPathTextBlock.Text = string.Empty;
            SelectedCatalogIdTextBlock.Text = string.Empty;
            PreviewTitleTextBlock.Text = "Texture preview";
            ConfigureExportActions(string.Empty, exists: false, label: "Open export");
            TexturePreviewImage.Source = null;
            TexturePreviewBackgroundPanel.Visibility = Visibility.Collapsed;
            TexturePreviewCanvasNoteTextBlock.Visibility = Visibility.Collapsed;
            TexturePreviewEmptyTextBlock.Text = "Texture preview appears here when the selected export is available.";
            TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
            ModelMetadataPanel.Visibility = Visibility.Collapsed;
            ModelMetadataInlineTextBlock.Visibility = Visibility.Collapsed;
            GoodieFactsPanel.Visibility = Visibility.Collapsed;
            ModelWireframePreviewPanel.Visibility = Visibility.Collapsed;
            ModelViewControlsPanel.Visibility = Visibility.Collapsed;
            ModelWireframeStatusTextBlock.Visibility = Visibility.Collapsed;
            ModelWireframeNoteTextBlock.Visibility = Visibility.Collapsed;
            ModelPackagePlanTextBlock.Text = "Material package plan appears here when a model export is selected.";
            MaterialPackageOutputStatusTextBlock.Text = "Material package output appears here after a catalog loads.";
            PrepareMaterialPackageButton.IsEnabled = false;
            OpenMaterialPackageButton.IsEnabled = false;
            CopyMaterialPackagePathButton.IsEnabled = false;
            ClearSelectedModelLinkedTexture();
            _currentModelGeometryPreview = AssetModelGeometryPreview.Empty;
        }

        private void RenderModelSummary(AssetModelSummary summary, string modelExportPath)
        {
            string formatLabel = summary.FormatVersion is int version
                ? $"{summary.Format} {version}"
                : summary.Format;
            ModelMetadataInlineTextBlock.Text = summary.MetadataAvailable
                ? $"{formatLabel}; {FormatCount(summary.VertexCount)} vertices; {FormatCount(summary.PolygonIndexCount)} polygon index entries; {BuildModelUvMappingText(summary)}."
                : $"{formatLabel}; model metadata unavailable.";
            ModelMetadataInlineTextBlock.Visibility = Visibility.Visible;
            ModelMetadataPanel.Visibility = Visibility.Visible;
            ModelWireframePreviewPanel.Visibility = Visibility.Visible;
            ModelViewControlsPanel.Visibility = Visibility.Visible;
            ModelWireframeStatusTextBlock.Visibility = Visibility.Visible;
            ModelWireframeNoteTextBlock.Visibility = Visibility.Visible;
            ModelMetadataStatusTextBlock.Text = $"{summary.Status} In-app wireframe preview is available when model geometry metadata is present.";
            ModelFormatTextBlock.Text = formatLabel;
            ModelSizeTextBlock.Text = FormatByteSize(summary.ByteSize);
            ModelVertexCountTextBlock.Text = FormatCount(summary.VertexCount);
            ModelPolygonIndexCountTextBlock.Text = FormatCount(summary.PolygonIndexCount);
            ModelGeometryCountTextBlock.Text = FormatCount(summary.GeometryCount);
            ModelMaterialCountTextBlock.Text =
                $"{FormatCount(summary.MaterialCount)} / {FormatCount(summary.TextureBindingCount)}";
            ModelUvCountTextBlock.Text = BuildModelUvMappingText(summary);
            ModelMaterialLayerCountTextBlock.Text = BuildModelMaterialAssignmentText(summary);
            ModelConnectionCountTextBlock.Text = BuildModelConnectionText(summary);
            AssetModelTextureLinkService textureLinkService = new();
            AssetModelTextureLinks textureLinks = textureLinkService.Build(_snapshot.Textures, summary);
            IReadOnlyList<AssetModelSidecarTexture> sidecarTextures =
                textureLinkService.ResolveSidecarTextures(modelExportPath, textureLinks.TextureBindingFileNames);
            ModelTextureLinksTextBlock.Text = BuildModelTextureLinkText(textureLinks, sidecarTextures);
            ConfigureSelectedModelLinkedTexture(textureLinks, sidecarTextures);
            _currentModelGeometryPreview = summary.GeometryPreview;
            UpdateModelPreviewViewButtonStyles();
            RenderWireframe(_currentModelGeometryPreview);
        }

        private void RefreshMaterialImportPlans()
        {
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(_snapshot);
            _materialDryRunPlan = new AssetMaterialImportDryRunPlanService().Build(manifest);
            _materialPackagePlan = new AssetMaterialImportPackagePlanService().Build(manifest);
        }

        private AssetMaterialImportDryRunPlan BuildMaterialDryRunPlan()
        {
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(_snapshot);
            return new AssetMaterialImportDryRunPlanService().Build(manifest);
        }

        private void RenderModelPackagePlan(string catalogId)
        {
            AssetMaterialImportPackagePlan packagePlan = _materialPackagePlan ??
                new AssetMaterialImportPackagePlanService().Build(new AssetMaterialImportManifestService().Build(_snapshot));
            AssetMaterialImportPackageModelOperation? operation = packagePlan.ModelOperations.FirstOrDefault(model =>
                string.Equals(model.CatalogId, catalogId, StringComparison.OrdinalIgnoreCase));
            if (operation == null)
            {
                ModelPackagePlanTextBlock.Text = "Material package plan: no package operation matched this catalog row.";
                return;
            }

            int resolvedTextures = operation.TextureReferences.Count(static texture => texture.SourceAvailable);
            string status = operation.ReadyForPackage ? "ready" : operation.PackageStatus;
            string textureSample = BuildPackageTextureSample(operation.TextureReferences);
            ModelPackagePlanTextBlock.Text =
                $"Material package plan: {status}; model destination {operation.DestinationRelativePath}; " +
                $"{resolvedTextures}/{operation.TextureReferences.Count} texture references resolved. {textureSample}";
        }

        private static string BuildPackageTextureSample(
            IReadOnlyList<AssetMaterialImportPackageTextureReference> textureReferences)
        {
            IReadOnlyList<string> destinations = textureReferences
                .Where(static texture => texture.SourceAvailable && !string.IsNullOrWhiteSpace(texture.DestinationRelativePath))
                .Select(static texture => texture.DestinationRelativePath)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Take(3)
                .ToList();
            if (destinations.Count == 0)
            {
                return "No package texture destinations are ready.";
            }

            return $"Texture destinations: {string.Join(", ", destinations)}.";
        }

        private void UpdateMaterialPackageOutputStatus(
            AssetMaterialImportPackageMaterializationResult? result = null,
            AssetMaterialImportPackageInspectionResult? inspection = null,
            AssetMaterialImportPackageWorkOrderResult? workOrder = null,
            AssetMaterialImportPackageImporterBatchResult? importerBatch = null,
            AssetMaterialImportPackageImporterDryRunResult? importerDryRun = null,
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult? importerDryRunSidecarValidation = null,
            AssetMaterialImportPackageImporterInputMaterializationResult? importerInput = null,
            AssetMaterialImportPackageImporterInputPlanResult? importerInputPlan = null,
            AssetMaterialImportPackageRebuildPreviewResult? rebuildPreview = null,
            AssetMaterialImportPackageRebuildSceneResult? rebuildScene = null,
            AssetMaterialImportPackageRebuildMeshResult? rebuildMesh = null,
            AssetMaterialImportPackageRebuildMeshImportResult? rebuildMeshImport = null)
        {
            AssetMaterialImportPackagePlan? packagePlan = _materialPackagePlan;
            if (packagePlan == null || string.IsNullOrWhiteSpace(_materialPackageOutputRoot))
            {
                MaterialPackageOutputStatusTextBlock.Text = "Material package output appears here after a catalog loads.";
                PrepareMaterialPackageButton.IsEnabled = false;
                OpenMaterialPackageButton.IsEnabled = false;
                CopyMaterialPackagePathButton.IsEnabled = false;
                return;
            }

            bool outputExists = Directory.Exists(_materialPackageOutputRoot);
            if (result == null && outputExists)
            {
                try
                {
                    inspection ??= new AssetMaterialImportPackageInspectionService().Inspect(_materialPackageOutputRoot);
                    workOrder ??= new AssetMaterialImportPackageWorkOrderService().Build(_materialPackageOutputRoot);
                    importerBatch ??= new AssetMaterialImportPackageImporterBatchService().Build(_materialPackageOutputRoot);
                    importerDryRun ??= new AssetMaterialImportPackageImporterDryRunService().Build(_materialPackageOutputRoot);
                    importerDryRunSidecarValidation ??=
                        new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(_materialPackageOutputRoot);
                    importerInput ??= new AssetMaterialImportPackageImporterInputService().Preflight(_materialPackageOutputRoot);
                    string importerInputManifestPath = Path.Combine(
                        _materialPackageOutputRoot,
                        AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName);
                    if (File.Exists(importerInputManifestPath))
                    {
                        importerInputPlan ??= new AssetMaterialImportPackageImporterInputPlanService().Build(_materialPackageOutputRoot);
                        rebuildPreview ??= new AssetMaterialImportPackageRebuildPreviewService().Preflight(_materialPackageOutputRoot);
                        string rebuildPreviewManifestPath = Path.Combine(
                            _materialPackageOutputRoot,
                            AssetMaterialImportPackageRebuildPreviewService.ManifestFileName);
                        if (File.Exists(rebuildPreviewManifestPath))
                        {
                            rebuildScene ??= new AssetMaterialImportPackageRebuildSceneService().Preflight(_materialPackageOutputRoot);
                            string rebuildSceneManifestPath = Path.Combine(
                                _materialPackageOutputRoot,
                                AssetMaterialImportPackageRebuildSceneService.ManifestFileName);
                            if (File.Exists(rebuildSceneManifestPath))
                            {
                                rebuildMesh ??= new AssetMaterialImportPackageRebuildMeshService().Preflight(_materialPackageOutputRoot);
                                string rebuildMeshManifestPath = Path.Combine(
                                    _materialPackageOutputRoot,
                                    AssetMaterialImportPackageRebuildMeshService.ManifestFileName);
                                if (File.Exists(rebuildMeshManifestPath))
                                {
                                    rebuildMeshImport ??= new AssetMaterialImportPackageRebuildMeshImportService().Preflight(_materialPackageOutputRoot);
                                }
                            }
                        }
                    }
                }
                catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
                {
                    inspection = null;
                    workOrder = null;
                    importerBatch = null;
                    importerDryRun = null;
                    importerDryRunSidecarValidation = null;
                    importerInput = null;
                    importerInputPlan = null;
                    rebuildPreview = null;
                    rebuildScene = null;
                    rebuildMesh = null;
                    rebuildMeshImport = null;
                }
            }

            if (result != null)
            {
                MaterialPackageOutputStatusTextBlock.Text =
                    $"Material package output: {result.CopiedFiles:N0} copied, {result.ExistingFilesSkipped:N0} already present, " +
                    $"{result.MissingSourceFiles:N0} missing source files, {result.UnsafeDestinationFiles:N0} unsafe destinations. " +
                    $"{BuildMaterialPackageInspectionSummary(inspection)} " +
                    $"{BuildMaterialPackageWorkOrderSummary(workOrder)} " +
                    $"{BuildMaterialPackageImporterBatchSummary(importerBatch)} " +
                    $"{BuildMaterialPackageImporterDryRunSummary(importerDryRun)} " +
                    $"{BuildMaterialPackageImporterDryRunSidecarValidationSummary(importerDryRunSidecarValidation)} " +
                    $"{BuildMaterialPackageImporterInputSummary(importerInput)} " +
                    $"{BuildMaterialPackageImporterInputPlanSummary(importerInputPlan)} " +
                    $"{BuildMaterialPackageRebuildPreviewSummary(rebuildPreview)} " +
                    $"{BuildMaterialPackageRebuildSceneSummary(rebuildScene)} " +
                    $"{BuildMaterialPackageRebuildMeshSummary(rebuildMesh)} " +
                    $"{BuildMaterialPackageRebuildMeshImportSummary(rebuildMeshImport)} " +
                    $"{BuildMaterialPackageWorkOrderSidecarSummary(result)} " +
                    $"{BuildMaterialPackageImporterDryRunSidecarSummary(result)} " +
                    $"Package root: {_materialPackageOutputRoot}";
            }
            else if (outputExists && workOrder != null)
            {
                MaterialPackageOutputStatusTextBlock.Text =
                    $"Material package output: {packagePlan.TotalPackageFiles:N0} expected files under " +
                    $"{BuildPathSummary(_materialPackageOutputRoot)}. " +
                    $"{BuildMaterialPackageInspectionSummary(inspection)} " +
                    $"{BuildMaterialPackageWorkOrderSummary(workOrder)} " +
                    $"{BuildMaterialPackageImporterBatchSummary(importerBatch)} " +
                    $"{BuildMaterialPackageImporterDryRunSummary(importerDryRun)} " +
                    $"{BuildMaterialPackageImporterDryRunSidecarValidationSummary(importerDryRunSidecarValidation)} " +
                    $"{BuildMaterialPackageImporterInputSummary(importerInput)} " +
                    $"{BuildMaterialPackageImporterInputPlanSummary(importerInputPlan)} " +
                    $"{BuildMaterialPackageRebuildPreviewSummary(rebuildPreview)} " +
                    $"{BuildMaterialPackageRebuildSceneSummary(rebuildScene)} " +
                    $"{BuildMaterialPackageRebuildMeshSummary(rebuildMesh)} " +
                    $"{BuildMaterialPackageRebuildMeshImportSummary(rebuildMeshImport)}";
            }
            else
            {
                MaterialPackageOutputStatusTextBlock.Text =
                    $"Material package output: {packagePlan.TotalPackageFiles:N0} ready files " +
                    $"({packagePlan.ModelPackageFiles:N0} model, {packagePlan.TexturePackageFiles:N0} texture) can be prepared under " +
                    $"{BuildPathSummary(_materialPackageOutputRoot)}. " +
                    (outputExists ? "Package folder already exists." : "Package folder has not been created yet.");
            }

            PrepareMaterialPackageButton.IsEnabled = packagePlan.TotalPackageFiles > 0;
            OpenMaterialPackageButton.IsEnabled = outputExists;
            CopyMaterialPackagePathButton.IsEnabled = true;
        }

        private static string BuildMaterialPackageInspectionSummary(AssetMaterialImportPackageInspectionResult? inspection)
        {
            if (inspection == null)
            {
                return "Manifest graph inspection was not run.";
            }

            string status = inspection.Completed ? "ok" : inspection.ManifestStatus;
            return
                $"Manifest graph inspection: {status}; " +
                $"{inspection.ManifestReadyModelGraphRows:N0}/{inspection.ManifestModelGraphRows:N0} model rows ready, " +
                $"{inspection.ManifestResolvedTextureReferenceRows:N0}/{inspection.ManifestTextureReferenceRows:N0} texture references resolved, " +
                $"{inspection.UnsafeModelGraphPaths:N0} unsafe graph paths.";
        }

        private static string BuildMaterialPackageWorkOrderSummary(AssetMaterialImportPackageWorkOrderResult? workOrder)
        {
            if (workOrder == null)
            {
                return "Importer work order was not built.";
            }

            string status = workOrder.Completed ? "ready" : workOrder.ManifestStatus;
            return
                $"Importer work order: {status}; " +
                $"{workOrder.ReadyWorkOrderModelRows:N0}/{workOrder.WorkOrderModelRows:N0} ready model tasks, " +
                $"{workOrder.ReadyTextureReferenceRows:N0}/{workOrder.TextureReferenceRows:N0} ready texture-reference tasks, " +
                $"{workOrder.MissingPackageFiles:N0} missing package files, " +
                $"{workOrder.UnsafePackagePaths:N0} unsafe package paths.";
        }

        private static string BuildMaterialPackageImporterBatchSummary(AssetMaterialImportPackageImporterBatchResult? importerBatch)
        {
            if (importerBatch == null)
            {
                return "Importer batch was not built.";
            }

            string status = importerBatch.Completed ? "ready" : importerBatch.SidecarStatus;
            return
                $"Importer batch: {status}; " +
                $"{importerBatch.ReadyTaskRows:N0}/{importerBatch.TotalTaskRows:N0} ready flat tasks " +
                $"({importerBatch.ModelTaskRows:N0} model, {importerBatch.TextureTaskRows:N0} texture), " +
                $"{importerBatch.BlockedTaskRows:N0} blocked tasks.";
        }

        private static string BuildMaterialPackageImporterDryRunSummary(AssetMaterialImportPackageImporterDryRunResult? importerDryRun)
        {
            if (importerDryRun == null)
            {
                return "Importer dry-run adapter rows were not built.";
            }

            string status = importerDryRun.Completed ? "ready" : importerDryRun.SourceBatchStatus;
            return
                $"Importer dry run: {status}; " +
                $"{importerDryRun.ReadyAdapterRows:N0}/{importerDryRun.PlannedAdapterRows:N0} adapter rows ready, " +
                $"{importerDryRun.BlockedTaskRows:N0} blocked source tasks.";
        }

        private static string BuildMaterialPackageImporterDryRunSidecarValidationSummary(
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult? validation)
        {
            if (validation == null)
            {
                return "Importer dry-run sidecar validation was not run.";
            }

            string status = validation.Completed ? "ok" : validation.SidecarStatus;
            return
                $"Importer dry-run sidecar validation: {status}; " +
                $"{validation.FreshReadyAdapterRows:N0}/{validation.FreshPlannedAdapterRows:N0} fresh adapter rows, " +
                $"matches fresh build: {(validation.DryRunMatchesFreshBuild ? "yes" : "no")}.";
        }

        private static string BuildMaterialPackageImporterInputSummary(
            AssetMaterialImportPackageImporterInputMaterializationResult? importerInput)
        {
            if (importerInput == null)
            {
                return "Importer input staging was not run.";
            }

            string status = importerInput.Completed ? "ready" : importerInput.ManifestStatus;
            string mode = importerInput.Executed ? "staged" : "preflight";
            return
                $"Importer input {mode}: {status}; " +
                $"{importerInput.InputRowsReady:N0}/{importerInput.PlannedAdapterRows:N0} rows ready, " +
                $"{importerInput.UniqueAdapterFiles:N0} unique files, " +
                $"{importerInput.CopiedFiles:N0} copied, " +
                $"{importerInput.ExistingFilesSkipped:N0} existing, " +
                $"{importerInput.ExistingHashMismatches:N0} hash mismatches.";
        }

        private static string BuildMaterialPackageImporterInputPlanSummary(
            AssetMaterialImportPackageImporterInputPlanResult? importerInputPlan)
        {
            if (importerInputPlan == null)
            {
                return "Importer input plan was not built.";
            }

            string status = importerInputPlan.Completed ? "ready" : importerInputPlan.ManifestStatus;
            return
                $"Importer input plan: {status}; " +
                $"{importerInputPlan.ReadyJobRows:N0}/{importerInputPlan.TotalJobRows:N0} consumer jobs ready " +
                $"({importerInputPlan.ModelJobRows:N0} model imports, {importerInputPlan.TextureBindingJobRows:N0} texture binds), " +
                $"{importerInputPlan.ReadableModelRows:N0} readable FBX rows, " +
                $"{importerInputPlan.ReadableTextureBindingRows:N0} readable PNG binding rows, " +
                $"{importerInputPlan.BlockedJobRows:N0} blocked jobs.";
        }

        private static string BuildMaterialPackageRebuildPreviewSummary(
            AssetMaterialImportPackageRebuildPreviewResult? rebuildPreview)
        {
            if (rebuildPreview == null)
            {
                return "Rebuild preview adapter was not run.";
            }

            string status = rebuildPreview.Completed ? "ready" : rebuildPreview.ManifestStatus;
            string mode = rebuildPreview.Executed ? "materialized" : "preflight";
            return
                $"Rebuild preview {mode}: {status}; " +
                $"{rebuildPreview.ReadyPreviewRows:N0}/{rebuildPreview.ModelPreviewRows:N0} model previews ready, " +
                $"{rebuildPreview.ObjFileRows:N0} OBJ rows, " +
                $"{rebuildPreview.BindingSidecarRows:N0} binding sidecars, " +
                $"{rebuildPreview.TextureBindingRows:N0} texture bindings, " +
                $"{rebuildPreview.BlockedPreviewRows:N0} blocked previews.";
        }

        private static string BuildMaterialPackageRebuildSceneSummary(
            AssetMaterialImportPackageRebuildSceneResult? rebuildScene)
        {
            if (rebuildScene == null)
            {
                return "Rebuild scene contract was not run.";
            }

            string status = rebuildScene.Completed ? "ready" : rebuildScene.ManifestStatus;
            string mode = rebuildScene.Executed ? "materialized" : "preflight";
            return
                $"Rebuild scene contract {mode}: {status}; " +
                $"{rebuildScene.ReadySceneRows:N0}/{rebuildScene.SceneRows:N0} scene rows ready, " +
                $"{rebuildScene.FbxVertexRows:N0} FBX vertices, " +
                $"{rebuildScene.FbxPolygonIndexRows:N0} polygon indices, " +
                $"{rebuildScene.FbxNormalRows:N0} normals, " +
                $"{rebuildScene.FbxTextureCoordinateRows:N0} UV rows, " +
                $"{rebuildScene.TextureBindingRows:N0} texture bindings, " +
                $"{rebuildScene.BlockedSceneRows:N0} blocked scenes.";
        }

        private static string BuildMaterialPackageRebuildMeshSummary(
            AssetMaterialImportPackageRebuildMeshResult? rebuildMesh)
        {
            if (rebuildMesh == null)
            {
                return "Rebuild mesh output was not run.";
            }

            string status = rebuildMesh.Completed ? "ready" : rebuildMesh.ManifestStatus;
            string mode = rebuildMesh.Executed ? "materialized" : "preflight";
            return
                $"Rebuild mesh output {mode}: {status}; " +
                $"{rebuildMesh.ReadyMeshRows:N0}/{rebuildMesh.MeshRows:N0} mesh rows ready, " +
                $"{rebuildMesh.FaceRows:N0} faces, " +
                $"{rebuildMesh.VertexRows:N0} vertices, " +
                $"{rebuildMesh.NormalRows:N0} normals, " +
                $"{rebuildMesh.TextureCoordinateRows:N0} UV rows, " +
                $"{rebuildMesh.MaterialRows:N0} materials, " +
                $"{rebuildMesh.TextureBindingRows:N0} texture bindings, " +
                $"{rebuildMesh.BlockedMeshRows:N0} blocked meshes.";
        }

        private static string BuildMaterialPackageRebuildMeshImportSummary(
            AssetMaterialImportPackageRebuildMeshImportResult? rebuildMeshImport)
        {
            if (rebuildMeshImport == null)
            {
                return "Rebuild mesh import validation was not run.";
            }

            string status = rebuildMeshImport.Completed ? "ready" : rebuildMeshImport.ManifestStatus;
            string mode = rebuildMeshImport.Executed ? "materialized" : "preflight";
            return
                $"Rebuild mesh import validation {mode}: {status}; " +
                $"{rebuildMeshImport.ReadyImportRows:N0}/{rebuildMeshImport.ImportRows:N0} import rows ready, " +
                $"{rebuildMeshImport.ObjParsedRows:N0} OBJ parsed, " +
                $"{rebuildMeshImport.MtlParsedRows:N0} MTL parsed, " +
                $"{rebuildMeshImport.FaceRows:N0} faces, " +
                $"{rebuildMeshImport.MaterialRows:N0} materials, " +
                $"{rebuildMeshImport.TextureReferenceRows:N0} texture references, " +
                $"{rebuildMeshImport.CountMismatchRows:N0} count mismatches, " +
                $"{rebuildMeshImport.MissingTextureRows:N0} missing textures.";
        }

        private static string BuildMaterialPackageWorkOrderSidecarSummary(AssetMaterialImportPackageMaterializationResult result)
        {
            if (!result.WorkOrderSidecarWritten)
            {
                return $"Work-order sidecar: {result.WorkOrderSidecarStatus}.";
            }

            return
                $"Work-order sidecar: {result.WorkOrderSidecarStatus} " +
                $"({result.WorkOrderSidecarRelativePath}, {result.WorkOrderSidecarBytes:N0} bytes).";
        }

        private static string BuildMaterialPackageImporterDryRunSidecarSummary(AssetMaterialImportPackageMaterializationResult result)
        {
            if (!result.ImporterDryRunSidecarWritten)
            {
                return $"Importer dry-run sidecar: {result.ImporterDryRunSidecarStatus}.";
            }

            return
                $"Importer dry-run sidecar: {result.ImporterDryRunSidecarStatus} " +
                $"({result.ImporterDryRunSidecarRelativePath}, {result.ImporterDryRunSidecarBytes:N0} bytes).";
        }

        private async void PrepareMaterialPackageButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_snapshot.CatalogFilePath) ||
                string.IsNullOrWhiteSpace(_materialPackageOutputRoot))
            {
                AppStatusService.SetStatus("Asset Library: load a catalog before preparing a material package");
                return;
            }

            PrepareMaterialPackageButton.IsEnabled = false;
            MaterialPackageOutputStatusTextBlock.Text = $"Preparing material package under {_materialPackageOutputRoot}...";
            AppStatusService.SetStatus("Asset Library: preparing material package");

            try
            {
                AssetCatalogSnapshot snapshot = _snapshot;
                string outputRoot = _materialPackageOutputRoot;
                AssetMaterialImportPackageMaterializationResult result = await Task.Run(() =>
                    new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot));
                AssetMaterialImportPackageInspectionResult inspection = await Task.Run(() =>
                    new AssetMaterialImportPackageInspectionService().Inspect(outputRoot));
                AssetMaterialImportPackageWorkOrderResult workOrder = await Task.Run(() =>
                    new AssetMaterialImportPackageWorkOrderService().Build(outputRoot));
                AssetMaterialImportPackageImporterBatchResult importerBatch = await Task.Run(() =>
                    new AssetMaterialImportPackageImporterBatchService().Build(outputRoot));
                AssetMaterialImportPackageImporterDryRunResult importerDryRun = await Task.Run(() =>
                    new AssetMaterialImportPackageImporterDryRunService().Build(outputRoot));
                AssetMaterialImportPackageImporterDryRunSidecarValidationResult importerDryRunSidecarValidation = await Task.Run(() =>
                    new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(outputRoot));
                AssetMaterialImportPackageImporterInputMaterializationResult importerInput = await Task.Run(() =>
                    new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot));
                AssetMaterialImportPackageImporterInputPlanResult importerInputPlan = await Task.Run(() =>
                    new AssetMaterialImportPackageImporterInputPlanService().Build(outputRoot));
                AssetMaterialImportPackageRebuildPreviewResult rebuildPreview = await Task.Run(() =>
                    new AssetMaterialImportPackageRebuildPreviewService().Materialize(outputRoot));
                AssetMaterialImportPackageRebuildSceneResult rebuildScene = await Task.Run(() =>
                    new AssetMaterialImportPackageRebuildSceneService().Materialize(outputRoot));
                AssetMaterialImportPackageRebuildMeshResult rebuildMesh = await Task.Run(() =>
                    new AssetMaterialImportPackageRebuildMeshService().Materialize(outputRoot));
                AssetMaterialImportPackageRebuildMeshImportResult rebuildMeshImport = await Task.Run(() =>
                    new AssetMaterialImportPackageRebuildMeshImportService().Materialize(outputRoot));

                UpdateMaterialPackageOutputStatus(
                    result,
                    inspection,
                    workOrder,
                    importerBatch,
                    importerDryRun,
                    importerDryRunSidecarValidation,
                    importerInput,
                    importerInputPlan,
                    rebuildPreview,
                    rebuildScene,
                    rebuildMesh,
                    rebuildMeshImport);
                string completion = result.Completed &&
                    inspection.Completed &&
                    workOrder.Completed &&
                    importerBatch.Completed &&
                    importerDryRun.Completed &&
                    importerDryRunSidecarValidation.Completed &&
                    importerInput.Completed &&
                    importerInputPlan.Completed &&
                    rebuildPreview.Completed &&
                    rebuildScene.Completed &&
                    rebuildMesh.Completed &&
                    rebuildMeshImport.Completed
                    ? "complete, inspected, sidecar-validated, importer-batch-ready, importer-dry-run-ready, importer-dry-run-sidecar-validated, importer-input-staged, importer-input-plan-ready, rebuild-preview-ready, rebuild-scene-contract-ready, rebuild-mesh-ready, and rebuild-mesh-import-ready"
                    : result.Completed && inspection.Completed
                        ? "complete and inspected with importer handoff issues"
                    : result.Completed
                        ? "complete with manifest inspection issues"
                        : "completed with blocked files";
                AppStatusService.SetStatus(
                    $"Asset Library: material package {completion}; {importerBatch.ReadyTaskRows:N0}/{importerBatch.TotalTaskRows:N0} ready flat importer tasks; " +
                    $"{importerDryRun.ReadyAdapterRows:N0}/{importerDryRun.PlannedAdapterRows:N0} ready importer dry-run rows; " +
                    $"dry-run sidecar validation {importerDryRunSidecarValidation.SidecarStatus}; " +
                    $"importer input {importerInput.InputRowsReady:N0}/{importerInput.PlannedAdapterRows:N0} rows; " +
                    $"input plan {importerInputPlan.ReadyJobRows:N0}/{importerInputPlan.TotalJobRows:N0} jobs; " +
                    $"rebuild preview {rebuildPreview.ReadyPreviewRows:N0}/{rebuildPreview.ModelPreviewRows:N0} models; " +
                    $"rebuild scene contract {rebuildScene.ReadySceneRows:N0}/{rebuildScene.SceneRows:N0} scenes; " +
                    $"rebuild mesh {rebuildMesh.ReadyMeshRows:N0}/{rebuildMesh.MeshRows:N0} meshes; " +
                    $"rebuild mesh import {rebuildMeshImport.ReadyImportRows:N0}/{rebuildMeshImport.ImportRows:N0} rows");
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
            {
                MaterialPackageOutputStatusTextBlock.Text = "Material package output could not be prepared.";
                AppStatusService.SetStatus("Asset Library: material package preparation failed");
            }
            finally
            {
                PrepareMaterialPackageButton.IsEnabled = (_materialPackagePlan?.TotalPackageFiles ?? 0) > 0;
                OpenMaterialPackageButton.IsEnabled = Directory.Exists(_materialPackageOutputRoot);
                CopyMaterialPackagePathButton.IsEnabled = !string.IsNullOrWhiteSpace(_materialPackageOutputRoot);
            }
        }

        private void OpenMaterialPackageButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_materialPackageOutputRoot) ||
                !Directory.Exists(_materialPackageOutputRoot))
            {
                AppStatusService.SetStatus("Asset Library: material package folder does not exist yet");
                return;
            }

            try
            {
                Process.Start(new ProcessStartInfo(_materialPackageOutputRoot)
                {
                    UseShellExecute = true
                });
                AppStatusService.SetStatus("Asset Library: opened material package folder");
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException or System.ComponentModel.Win32Exception)
            {
                AppStatusService.SetStatus("Asset Library: material package folder could not be opened");
            }
        }

        private void CopyMaterialPackagePathButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_materialPackageOutputRoot))
            {
                AppStatusService.SetStatus("Asset Library: material package path is not available");
                return;
            }

            DataPackage data = new();
            data.SetText(_materialPackageOutputRoot);
            Clipboard.SetContent(data);
            AppStatusService.SetStatus("Asset Library: material package path copied");
        }

        private static string BuildModelUvMappingText(AssetModelSummary summary)
        {
            if (summary.TextureCoordinateCount == 0 && summary.TextureCoordinateIndexCount == 0)
            {
                return "UV mapping: no coordinate data recorded";
            }

            return
                $"UV mapping: {FormatCount(summary.TextureCoordinateCount)} coordinates / " +
                $"{FormatCount(summary.TextureCoordinateIndexCount)} index entries";
        }

        private static string BuildModelMaterialAssignmentText(AssetModelSummary summary)
        {
            if (summary.MaterialLayerCount == 0 && summary.MaterialAssignmentIndexCount == 0)
            {
                return "Material assignment: no layer data recorded";
            }

            return
                $"Material assignment: {FormatCount(summary.MaterialLayerCount)} layers / " +
                $"{FormatCount(summary.MaterialAssignmentIndexCount)} index entries";
        }

        private static string BuildModelConnectionText(AssetModelSummary summary)
        {
            string slotSummary = BuildTextureToMaterialSlotSummary(summary.TextureToMaterialSlotNames);
            if (summary.ObjectConnectionCount == 0 &&
                summary.PropertyConnectionCount == 0 &&
                summary.TextureToMaterialConnectionCount == 0)
            {
                return "Texture-material links: no connection data recorded";
            }

            return
                $"Texture-material links: {FormatCount(summary.TextureToMaterialConnectionCount)} texture-to-material / " +
                $"{FormatCount(summary.PropertyConnectionCount)} property / " +
                $"{FormatCount(summary.ObjectConnectionCount)} object. {slotSummary}";
        }

        private static string BuildTextureToMaterialSlotSummary(IReadOnlyList<string> slotNames)
        {
            if (slotNames.Count == 0)
            {
                return "No material slot names were readable.";
            }

            return $"Material slots: {string.Join(", ", slotNames.Take(6))}";
        }

        private static string BuildModelTextureLinkText(
            AssetModelTextureLinks links,
            IReadOnlyList<AssetModelSidecarTexture> sidecarTextures)
        {
            int bindingCount = links.TextureBindingFileNames.Count;
            if (bindingCount == 0)
            {
                return "Texture links: no FBX texture bindings were readable.";
            }

            int matchCount = links.CatalogMatchedTextureNames.Count;
            string sidecarSummary = BuildSidecarTextureSummary(sidecarTextures.Count, bindingCount);
            if (matchCount == 0)
            {
                return $"Texture links: {FormatCount(bindingCount)} FBX texture bindings; none are direct catalog rows. {sidecarSummary}";
            }

            string sample = string.Join(", ", links.CatalogMatchedTextureNames.Take(6));
            if (links.CatalogMatchedTextureNames.Count > 6)
            {
                sample += $", plus {FormatCount(links.CatalogMatchedTextureNames.Count - 6)} more";
            }

            string label = matchCount == 1 ? "direct catalog texture link" : "direct catalog texture links";
            return $"Texture links: {matchCount}/{bindingCount} {label}: {sample}. {sidecarSummary}";
        }

        private static string BuildSidecarTextureSummary(int sidecarCount, int bindingCount)
        {
            return sidecarCount == 0
                ? "No sidecar preview file was found beside the export."
                : $"Sidecar preview files: {sidecarCount}/{bindingCount}.";
        }

        private void ConfigureSelectedModelLinkedTexture(
            AssetModelTextureLinks links,
            IReadOnlyList<AssetModelSidecarTexture> sidecarTextures)
        {
            string textureName = links.CatalogMatchedTextureNames.FirstOrDefault() ?? string.Empty;
            _selectedModelLinkedTexture = string.IsNullOrWhiteSpace(textureName)
                ? null
                : _snapshot.Textures.FirstOrDefault(texture =>
                    string.Equals(texture.DisplayName, textureName, StringComparison.OrdinalIgnoreCase));

            AssetModelSidecarTexture? sidecarTexture = sidecarTextures.FirstOrDefault();
            _selectedModelSidecarTexturePath = _selectedModelLinkedTexture == null ? sidecarTexture?.ExportPath ?? string.Empty : string.Empty;
            _selectedModelSidecarTextureFileName = _selectedModelLinkedTexture == null ? sidecarTexture?.FileName ?? string.Empty : string.Empty;

            bool hasPreviewTarget = _selectedModelLinkedTexture != null || !string.IsNullOrWhiteSpace(_selectedModelSidecarTexturePath);
            ViewLinkedTextureButton.Content = _selectedModelLinkedTexture == null ? "Preview sidecar texture" : "View linked texture";
            ViewLinkedTextureButton.IsEnabled = hasPreviewTarget;
            ViewLinkedTextureButton.Visibility = !hasPreviewTarget
                ? Visibility.Collapsed
                : Visibility.Visible;
        }

        private void ClearSelectedModelLinkedTexture()
        {
            _selectedModelLinkedTexture = null;
            _selectedModelSidecarTexturePath = string.Empty;
            _selectedModelSidecarTextureFileName = string.Empty;
            ViewLinkedTextureButton.Content = "View linked texture";
            ViewLinkedTextureButton.IsEnabled = false;
            ViewLinkedTextureButton.Visibility = Visibility.Collapsed;
        }

        private void ViewLinkedTextureButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedModelLinkedTexture == null && string.IsNullOrWhiteSpace(_selectedModelSidecarTexturePath))
            {
                AppStatusService.SetStatus("Asset Library: no linked texture is available for this model");
                return;
            }

            if (_selectedModelLinkedTexture == null)
            {
                PreviewSidecarTexture();
                return;
            }

            AssetTextureItem texture = _selectedModelLinkedTexture;
            _selectedKind = AssetListKind.Textures;
            UpdateTabStyles();
            AssetSearchBox.Text = texture.DisplayName;
            UpdateAssetList();
            AssetItemsListView.SelectedItem = texture;
            AssetItemsListView.ScrollIntoView(texture);
            ShowTexture(texture);
            AppStatusService.SetStatus($"Asset Library: showing linked texture {texture.DisplayName}");
        }

        private void PreviewSidecarTexture()
        {
            if (string.IsNullOrWhiteSpace(_selectedModelSidecarTexturePath) || !File.Exists(_selectedModelSidecarTexturePath))
            {
                AppStatusService.SetStatus("Asset Library: sidecar texture preview file is unavailable");
                return;
            }

            TexturePreviewPanel.Visibility = Visibility.Visible;
            TexturePreviewBackgroundPanel.Visibility = Visibility.Visible;
            TexturePreviewCanvasNoteTextBlock.Visibility = Visibility.Visible;
            TexturePreviewEmptyTextBlock.Text = "Loading sidecar texture preview...";
            TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;

            try
            {
                TexturePreviewImage.Source = new BitmapImage(new Uri(_selectedModelSidecarTexturePath));
                TexturePreviewEmptyTextBlock.Visibility = Visibility.Collapsed;
                PreviewTitleTextBlock.Text = $"Sidecar texture preview: {_selectedModelSidecarTextureFileName}";
                AppStatusService.SetStatus($"Asset Library: previewing sidecar texture {_selectedModelSidecarTextureFileName}");
            }
            catch (Exception ex) when (ex is ArgumentException or UriFormatException or IOException)
            {
                TexturePreviewImage.Source = null;
                TexturePreviewEmptyTextBlock.Text = "Sidecar texture exists, but the preview could not be opened.";
                TexturePreviewEmptyTextBlock.Visibility = Visibility.Visible;
            }
        }

        private void OpenInMediaButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_selectedMediaHandoffSearch))
            {
                AppStatusService.SetStatus("Asset Library: no linked media item is available for this Goodie");
                return;
            }

            MediaHandoffService.RequestVideo(_selectedMediaHandoffSearch, _selectedMediaHandoffLabel);
            App.MainWindowInstance?.NavigateToTag("media");
            AppStatusService.SetStatus($"Media: opening {_selectedMediaHandoffLabel}");
        }

        private void ModelViewFrontButton_Click(object sender, RoutedEventArgs e)
        {
            SetModelPreviewView(ModelPreviewView.Front);
        }

        private void ModelViewSideButton_Click(object sender, RoutedEventArgs e)
        {
            SetModelPreviewView(ModelPreviewView.Side);
        }

        private void ModelViewTopButton_Click(object sender, RoutedEventArgs e)
        {
            SetModelPreviewView(ModelPreviewView.Top);
        }

        private void ModelViewIsoButton_Click(object sender, RoutedEventArgs e)
        {
            SetModelPreviewView(ModelPreviewView.Iso);
        }

        private void SetModelPreviewView(ModelPreviewView view)
        {
            _modelPreviewView = view;
            UpdateModelPreviewViewButtonStyles();
            RenderWireframe(_currentModelGeometryPreview);
            AppStatusService.SetStatus($"Asset Library: model view set to {view.ToString().ToLowerInvariant()}");
        }

        private void UpdateModelPreviewViewButtonStyles()
        {
            Style activeStyle = (Style)Application.Current.Resources["SubTabActiveButtonStyle"];
            Style inactiveStyle = (Style)Application.Current.Resources["SubTabInactiveButtonStyle"];
            ModelViewFrontButton.Style = _modelPreviewView == ModelPreviewView.Front ? activeStyle : inactiveStyle;
            ModelViewSideButton.Style = _modelPreviewView == ModelPreviewView.Side ? activeStyle : inactiveStyle;
            ModelViewTopButton.Style = _modelPreviewView == ModelPreviewView.Top ? activeStyle : inactiveStyle;
            ModelViewIsoButton.Style = _modelPreviewView == ModelPreviewView.Iso ? activeStyle : inactiveStyle;
        }

        private void TexturePreviewNeutralButton_Click(object sender, RoutedEventArgs e)
        {
            SetTexturePreviewBackground(TexturePreviewBackground.Neutral);
        }

        private void TexturePreviewLightButton_Click(object sender, RoutedEventArgs e)
        {
            SetTexturePreviewBackground(TexturePreviewBackground.Light);
        }

        private void TexturePreviewDarkButton_Click(object sender, RoutedEventArgs e)
        {
            SetTexturePreviewBackground(TexturePreviewBackground.Dark);
        }

        private void SetTexturePreviewBackground(TexturePreviewBackground background)
        {
            _texturePreviewBackground = background;
            ApplyTexturePreviewBackground();
            AppStatusService.SetStatus($"Asset Library: texture preview background set to {background.ToString().ToLowerInvariant()}");
        }

        private void ApplyTexturePreviewBackground()
        {
            (Color Panel, Color Text) colors = _texturePreviewBackground switch
            {
                TexturePreviewBackground.Light => (Color.FromArgb(255, 244, 241, 232), Color.FromArgb(255, 30, 41, 59)),
                TexturePreviewBackground.Dark => (Color.FromArgb(255, 15, 23, 42), Color.FromArgb(255, 226, 232, 240)),
                _ => (Color.FromArgb(255, 116, 125, 139), Color.FromArgb(255, 15, 23, 42))
            };

            TexturePreviewPanel.Background = new SolidColorBrush(colors.Panel);
            TexturePreviewEmptyTextBlock.Foreground = new SolidColorBrush(colors.Text);
            UpdateTexturePreviewBackgroundButtonStyles();
        }

        private void UpdateTexturePreviewBackgroundButtonStyles()
        {
            Style activeStyle = (Style)Application.Current.Resources["SubTabActiveButtonStyle"];
            Style inactiveStyle = (Style)Application.Current.Resources["SubTabInactiveButtonStyle"];
            TexturePreviewNeutralButton.Style = _texturePreviewBackground == TexturePreviewBackground.Neutral ? activeStyle : inactiveStyle;
            TexturePreviewLightButton.Style = _texturePreviewBackground == TexturePreviewBackground.Light ? activeStyle : inactiveStyle;
            TexturePreviewDarkButton.Style = _texturePreviewBackground == TexturePreviewBackground.Dark ? activeStyle : inactiveStyle;
        }

        private void RenderWireframe(AssetModelGeometryPreview preview)
        {
            ModelWireframeCanvas.Children.Clear();
            if (!preview.Available)
            {
                ModelWireframeEmptyTextBlock.Text = "Wireframe preview is unavailable for this FBX export.";
                ModelWireframeStatusTextBlock.Text = "Wireframe preview unavailable for this model export.";
                ModelWireframeEmptyTextBlock.Visibility = Visibility.Visible;
                return;
            }

            const double width = 360;
            const double height = 190;
            const double padding = 16;
            IReadOnlyList<AssetModelPreviewVertex> vertices = preview.Vertices;
            (double X, double Y)[] projectedVertices = vertices.Select(ProjectModelVertex).ToArray();
            double minX = projectedVertices.Min(static vertex => vertex.X);
            double maxX = projectedVertices.Max(static vertex => vertex.X);
            double minY = projectedVertices.Min(static vertex => vertex.Y);
            double maxY = projectedVertices.Max(static vertex => vertex.Y);
            double rangeX = Math.Max(maxX - minX, 0.0001);
            double rangeY = Math.Max(maxY - minY, 0.0001);
            double scale = Math.Min((width - padding * 2) / rangeX, (height - padding * 2) / rangeY);
            double xOffset = (width - rangeX * scale) / 2;
            double yOffset = (height - rangeY * scale) / 2;
            Brush stroke = new SolidColorBrush(Color.FromArgb(255, 230, 177, 92));

            foreach (AssetModelPreviewEdge edge in preview.Edges)
            {
                if (edge.StartIndex < 0 ||
                    edge.EndIndex < 0 ||
                    edge.StartIndex >= vertices.Count ||
                    edge.EndIndex >= vertices.Count)
                {
                    continue;
                }

                (double X, double Y) start = Project(projectedVertices[edge.StartIndex]);
                (double X, double Y) end = Project(projectedVertices[edge.EndIndex]);
                ModelWireframeCanvas.Children.Add(new XamlLine
                {
                    X1 = start.X,
                    Y1 = start.Y,
                    X2 = end.X,
                    Y2 = end.Y,
                    Stroke = stroke,
                    StrokeThickness = 1.5
                });
            }

            ModelWireframeEmptyTextBlock.Visibility = ModelWireframeCanvas.Children.Count == 0
                ? Visibility.Visible
                : Visibility.Collapsed;
            ModelWireframeStatusTextBlock.Text = ModelWireframeCanvas.Children.Count == 0
                ? "Wireframe preview unavailable for this model export."
                : "Wireframe preview available for this model export.";

            (double X, double Y) Project((double X, double Y) vertex)
            {
                double x = xOffset + (vertex.X - minX) * scale;
                double y = height - (yOffset + (vertex.Y - minY) * scale);
                return (x, y);
            }
        }

        private (double X, double Y) ProjectModelVertex(AssetModelPreviewVertex vertex)
        {
            return _modelPreviewView switch
            {
                ModelPreviewView.Front => (vertex.X, vertex.Y),
                ModelPreviewView.Side => (vertex.Z, vertex.Y),
                ModelPreviewView.Top => (vertex.X, vertex.Z),
                _ => (vertex.X - vertex.Z * 0.55, vertex.Y + (vertex.X + vertex.Z) * 0.22)
            };
        }

        private void OpenExportButton_Click(object sender, RoutedEventArgs e)
        {
            if (!CanOpenSelectedExport())
            {
                AppStatusService.SetStatus("Asset Library: selected export is not available");
                return;
            }

            try
            {
                Process.Start(new ProcessStartInfo(_selectedExportPath)
                {
                    UseShellExecute = true
                });
                AppStatusService.SetStatus("Asset Library: opened selected export");
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException or System.ComponentModel.Win32Exception)
            {
                AppStatusService.SetStatus("Asset Library: export could not be opened");
            }
        }

        private void CopyExportPathButton_Click(object sender, RoutedEventArgs e)
        {
            if (string.IsNullOrWhiteSpace(_selectedExportPath))
            {
                AppStatusService.SetStatus("Asset Library: no export path selected");
                return;
            }

            DataPackage data = new();
            data.SetText(_selectedExportPath);
            Clipboard.SetContent(data);
            AppStatusService.SetStatus("Asset Library: export path copied");
        }

        private void ConfigureExportActions(string exportPath, bool exists, string label)
        {
            _selectedExportPath = exportPath;
            OpenExportButton.Content = label;
            OpenExportButton.IsEnabled = exists && IsAllowedExportPath(exportPath);
            CopyExportPathButton.IsEnabled = !string.IsNullOrWhiteSpace(exportPath);
            ClearMediaHandoff();
        }

        private void ConfigureMediaHandoff(string searchText, string label)
        {
            _selectedMediaHandoffSearch = searchText;
            _selectedMediaHandoffLabel = label;
            OpenInMediaButton.IsEnabled = true;
            OpenInMediaButton.Visibility = Visibility.Visible;
        }

        private void ClearMediaHandoff()
        {
            _selectedMediaHandoffSearch = string.Empty;
            _selectedMediaHandoffLabel = string.Empty;
            OpenInMediaButton.IsEnabled = false;
            OpenInMediaButton.Visibility = Visibility.Collapsed;
        }

        private bool CanOpenSelectedExport()
        {
            return File.Exists(_selectedExportPath) && IsAllowedExportPath(_selectedExportPath);
        }

        private static bool IsAllowedExportPath(string path)
        {
            string extension = Path.GetExtension(path).ToLowerInvariant();
            return extension is ".png" or ".fbx";
        }

        private static string BuildAvailability(bool exists)
        {
            return exists ? "available" : "missing";
        }

        private static string FormatCount(int count)
        {
            return count > 0 ? count.ToString("N0", CultureInfo.InvariantCulture) : "Unknown";
        }

        private static string FormatByteSize(long byteSize)
        {
            return byteSize > 0 ? $"{byteSize:N0} bytes" : "Unknown";
        }

        private static string BuildPathSummary(string? path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "No local path selected";
            }

            string trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string name = Path.GetFileName(trimmed);
            string? parent = Path.GetFileName(Path.GetDirectoryName(trimmed) ?? string.Empty);
            if (string.IsNullOrWhiteSpace(parent))
            {
                return string.IsNullOrWhiteSpace(name) ? "Configured local path" : name;
            }

            return $"{name} in {parent}";
        }

        private static string BuildMaterialPackageOutputRoot(string? catalogFilePath)
        {
            string? overrideRoot = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_ASSET_PACKAGE_ROOT");
            string baseRoot = string.IsNullOrWhiteSpace(overrideRoot)
                ? Path.Combine(
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                    "OnslaughtCareerEditor",
                    "asset-material-packages")
                : Path.GetFullPath(overrideRoot);
            return Path.Combine(baseRoot, BuildMaterialPackageOutputToken(catalogFilePath));
        }

        private static string BuildMaterialPackageOutputToken(string? catalogFilePath)
        {
            if (string.IsNullOrWhiteSpace(catalogFilePath))
            {
                return "catalog";
            }

            string fullPath = Path.GetFullPath(catalogFilePath);
            string? catalogDirectory = Path.GetDirectoryName(fullPath);
            string? catalogRoot = string.Equals(Path.GetFileName(catalogDirectory), "asset_catalog", StringComparison.OrdinalIgnoreCase)
                ? Path.GetDirectoryName(catalogDirectory)
                : catalogDirectory;
            string label = SanitizePathToken(Path.GetFileName(catalogRoot) ?? "catalog");
            if (string.IsNullOrWhiteSpace(label))
            {
                label = "catalog";
            }

            byte[] hashBytes = SHA256.HashData(Encoding.UTF8.GetBytes(fullPath.ToUpperInvariant()));
            string hash = Convert.ToHexString(hashBytes).Substring(0, 12).ToLowerInvariant();
            return $"{label}-{hash}";
        }

        private static string SanitizePathToken(string value)
        {
            char[] chars = value.Select(static ch =>
                char.IsLetterOrDigit(ch) || ch is '-' or '_' or '.' ? ch : '_').ToArray();
            string result = new string(chars).Trim('_');
            while (result.Contains("__", StringComparison.Ordinal))
            {
                result = result.Replace("__", "_", StringComparison.Ordinal);
            }

            return result.Length <= 64 ? result : result[..64].Trim('_');
        }

        private static AssetListKind GetInitialAssetKind()
        {
            string? value = Environment.GetEnvironmentVariable("ONSLAUGHT_WINUI_TEST_INITIAL_ASSET_TAB");
            return value switch
            {
                "1" => AssetListKind.LooseMeshes,
                "2" => AssetListKind.EmbeddedMeshes,
                "3" => AssetListKind.Goodies,
                _ => AssetListKind.Textures
            };
        }

        private enum AssetListKind
        {
            Textures,
            LooseMeshes,
            EmbeddedMeshes,
            Goodies
        }

        private enum GoodieBrowserFilter
        {
            All,
            Wall,
            Hidden,
            Models,
            Artwork,
            Videos
        }

        private enum TexturePreviewBackground
        {
            Neutral,
            Light,
            Dark
        }

        private enum ModelPreviewView
        {
            Front,
            Side,
            Top,
            Iso
        }

        private sealed record AssetGoodieBrowserItem(AssetGoodieItem CatalogItem, GoodieStateDetail? SaveState)
        {
            public string DisplayName => CatalogItem.DisplayName;

            public string ExportFileName
            {
                get
                {
                    string state = SaveState?.StateLabel ?? "State not loaded";
                    string wall = CatalogItem.IsSourceGridVisible
                        ? $"{CatalogItem.WallGroupLabel}; {CatalogItem.WallPositionLabel}"
                        : "Not on known Goodies wall";
                    return $"{state}; {wall}; unlock: {CatalogItem.UnlockRequirement}; {CatalogItem.ContentKind}; {CatalogItem.ExportFileName}";
                }
            }

            public override string ToString()
            {
                return $"{DisplayName} {ExportFileName} {CatalogItem.SourceTitle}";
            }
        }
    }
}
