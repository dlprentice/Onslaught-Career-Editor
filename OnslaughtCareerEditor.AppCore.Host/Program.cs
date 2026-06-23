using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Onslaught___Career_Editor;

namespace Onslaught___Career_Editor.Host;

internal static class Program
{
    private const string InspectSaveSchemaVersion = "appcore-save-analysis.v1";
    private const string CompareSavesSchemaVersion = "appcore-save-comparison.v1";
    private const string PatchRequestSchemaVersion = "appcore-save-patch-request.v1";
    private const string PlanSavePatchSchemaVersion = "appcore-save-patch-plan.v1";
    private const string PreviewSavePatchSchemaVersion = "appcore-save-patch-preview.v1";
    private const string AssetCatalogModelPreviewCoverageSchemaVersion = "appcore-asset-catalog-model-preview-coverage.v1";
    private const string AssetCatalogGoodiePreviewCoverageSchemaVersion = "appcore-asset-catalog-goodie-preview-coverage.v1";
    private const string AssetCatalogReadabilitySchemaVersion = "appcore-asset-catalog-readability.v1";
    private const string AssetMaterialImportPlanSchemaVersion = "appcore-asset-material-import-plan.v1";
    private const string AssetMaterialImportManifestSchemaVersion = "appcore-asset-material-import-manifest.v1";
    private const string AssetMaterialImportDryRunPlanSchemaVersion = "appcore-asset-material-import-dry-run-plan.v1";
    private const string AssetMaterialImportPackagePlanSchemaVersion = "appcore-asset-material-import-package-plan.v1";
    private const string AssetMaterialImportPackageMaterializationSchemaVersion = "appcore-asset-material-import-package-materialization.v1";
    private const string AssetMaterialPackageInspectionSchemaVersion = "appcore-asset-material-package-inspection.v1";
    private const string AssetMaterialPackageWorkOrderSchemaVersion = "appcore-asset-material-package-work-order.v1";
    private const string AssetMaterialPackageWorkOrderSidecarValidationSchemaVersion = "appcore-asset-material-package-work-order-sidecar-validation.v1";
    private const string AssetMaterialPackageImporterBatchSchemaVersion = "appcore-asset-material-package-importer-batch.v1";
    private const string AssetMaterialPackageImporterDryRunSchemaVersion = "appcore-asset-material-package-importer-dry-run.v1";
    private const string AssetMaterialPackageImporterDryRunSidecarValidationSchemaVersion = "appcore-asset-material-package-importer-dry-run-sidecar-validation.v1";
    private const string AssetMaterialPackageImporterInputMaterializationSchemaVersion = "appcore-asset-material-package-importer-input-materialization.v1";
    private const string AssetMaterialPackageImporterInputPlanSchemaVersion = "appcore-asset-material-package-importer-input-plan.v1";
    private const string AssetMaterialPackageRebuildPreviewMaterializationSchemaVersion = "appcore-asset-material-package-rebuild-preview-materialization.v1";
    private const string AssetMaterialPackageRebuildSceneMaterializationSchemaVersion = "appcore-asset-material-package-rebuild-scene-materialization.v1";
    private const string AssetMaterialPackageRebuildMeshMaterializationSchemaVersion = "appcore-asset-material-package-rebuild-mesh-materialization.v1";
    private const string AssetMaterialPackageRebuildMeshImportSchemaVersion = "appcore-asset-material-package-rebuild-mesh-import.v1";
    private const string PrivateAssetOutputArmPhrase = "MATERIALIZE ASSET MATERIAL PACKAGE";

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        PropertyNameCaseInsensitive = true,
        WriteIndented = true
    };

    private static readonly string[] KillCategories =
    [
        "Aircraft",
        "Vehicles",
        "Emplacements",
        "Infantry",
        "Mechs"
    ];

    public static int Main(string[] args)
    {
        try
        {
            if (args.Length == 0 || IsHelp(args[0]))
            {
                WriteUsage();
                return args.Length == 0 ? 1 : 0;
            }

            if (string.Equals(args[0], "inspect-save", StringComparison.OrdinalIgnoreCase))
            {
                return InspectSave(args[1..]);
            }

            if (string.Equals(args[0], "compare-saves", StringComparison.OrdinalIgnoreCase))
            {
                return CompareSaves(args[1..]);
            }

            if (string.Equals(args[0], "preview-save-patch", StringComparison.OrdinalIgnoreCase))
            {
                return PreviewSavePatch(args[1..]);
            }

            if (string.Equals(args[0], "plan-save-patch", StringComparison.OrdinalIgnoreCase))
            {
                return PlanSavePatch(args[1..]);
            }

            if (string.Equals(args[0], "inspect-asset-model-preview", StringComparison.OrdinalIgnoreCase))
            {
                return InspectAssetModelPreview(args[1..]);
            }

            if (string.Equals(args[0], "inspect-goodie-preview-coverage", StringComparison.OrdinalIgnoreCase))
            {
                return InspectGoodiePreviewCoverage(args[1..]);
            }

            if (string.Equals(args[0], "inspect-asset-catalog-readability", StringComparison.OrdinalIgnoreCase))
            {
                return InspectAssetCatalogReadability(args[1..]);
            }

            if (string.Equals(args[0], "inspect-asset-material-import-plan", StringComparison.OrdinalIgnoreCase))
            {
                return InspectAssetMaterialImportPlan(args[1..]);
            }

            if (string.Equals(args[0], "export-asset-material-import-manifest", StringComparison.OrdinalIgnoreCase))
            {
                return ExportAssetMaterialImportManifest(args[1..]);
            }

            if (string.Equals(args[0], "plan-asset-material-import-dry-run", StringComparison.OrdinalIgnoreCase))
            {
                return PlanAssetMaterialImportDryRun(args[1..]);
            }

            if (string.Equals(args[0], "plan-asset-material-import-package", StringComparison.OrdinalIgnoreCase))
            {
                return PlanAssetMaterialImportPackage(args[1..]);
            }

            if (string.Equals(args[0], "materialize-asset-material-import-package", StringComparison.OrdinalIgnoreCase))
            {
                return MaterializeAssetMaterialImportPackage(args[1..]);
            }

            if (string.Equals(args[0], "inspect-asset-material-package", StringComparison.OrdinalIgnoreCase))
            {
                return InspectAssetMaterialPackage(args[1..]);
            }

            if (string.Equals(args[0], "build-asset-material-package-work-order", StringComparison.OrdinalIgnoreCase))
            {
                return BuildAssetMaterialPackageWorkOrder(args[1..]);
            }

            if (string.Equals(args[0], "validate-asset-material-package-work-order-sidecar", StringComparison.OrdinalIgnoreCase))
            {
                return ValidateAssetMaterialPackageWorkOrderSidecar(args[1..]);
            }

            if (string.Equals(args[0], "build-asset-material-package-importer-batch", StringComparison.OrdinalIgnoreCase))
            {
                return BuildAssetMaterialPackageImporterBatch(args[1..]);
            }

            if (string.Equals(args[0], "build-asset-material-package-importer-dry-run", StringComparison.OrdinalIgnoreCase))
            {
                return BuildAssetMaterialPackageImporterDryRun(args[1..]);
            }

            if (string.Equals(args[0], "validate-asset-material-package-importer-dry-run-sidecar", StringComparison.OrdinalIgnoreCase))
            {
                return ValidateAssetMaterialPackageImporterDryRunSidecar(args[1..]);
            }

            if (string.Equals(args[0], "materialize-asset-material-package-importer-input", StringComparison.OrdinalIgnoreCase))
            {
                return MaterializeAssetMaterialPackageImporterInput(args[1..]);
            }

            if (string.Equals(args[0], "build-asset-material-package-importer-input-plan", StringComparison.OrdinalIgnoreCase))
            {
                return BuildAssetMaterialPackageImporterInputPlan(args[1..]);
            }

            if (string.Equals(args[0], "materialize-asset-material-package-rebuild-preview", StringComparison.OrdinalIgnoreCase))
            {
                return MaterializeAssetMaterialPackageRebuildPreview(args[1..]);
            }

            if (string.Equals(args[0], "materialize-asset-material-package-rebuild-scene", StringComparison.OrdinalIgnoreCase))
            {
                return MaterializeAssetMaterialPackageRebuildScene(args[1..]);
            }

            if (string.Equals(args[0], "materialize-asset-material-package-rebuild-mesh", StringComparison.OrdinalIgnoreCase))
            {
                return MaterializeAssetMaterialPackageRebuildMesh(args[1..]);
            }

            if (string.Equals(args[0], "materialize-asset-material-package-rebuild-mesh-import", StringComparison.OrdinalIgnoreCase))
            {
                return MaterializeAssetMaterialPackageRebuildMeshImport(args[1..]);
            }

            WriteError("appcore-host-error.v1", $"Unsupported command: {args[0]}");
            return 1;
        }
        catch (Exception ex)
        {
            WriteError("appcore-host-error.v1", ex.Message);
            return 1;
        }
    }

    private static int InspectSave(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "inspect-save requires a .bes/.bea/defaultoptions.bea path.");
            return 1;
        }

        string filePath = args[0];
        bool verbose = args.Any(arg => string.Equals(arg, "--verbose", StringComparison.OrdinalIgnoreCase));
        bool dumpMystery = args.Any(arg => string.Equals(arg, "--dump-mystery", StringComparison.OrdinalIgnoreCase));
        string fullPath = Path.GetFullPath(filePath);
        if (!File.Exists(fullPath))
        {
            WriteError("appcore-host-error.v1", $"Input file does not exist: {fullPath}");
            return 1;
        }

        if (!IsSupportedSavePath(fullPath))
        {
            WriteError("appcore-host-error.v1", "Input must be a .bes career save, .bea options file, or defaultoptions.bea backup.");
            return 1;
        }

        SaveAnalysis analysis = BesFilePatcher.AnalyzeSave(fullPath);
        SaveAnalyzerDocument document = SaveAnalyzerService.BuildAnalysisDocument(analysis, verbose, dumpMystery);
        string sha256 = HashFileSha256(fullPath);
        int displayableUnlocked = analysis.GoodiesNew + analysis.GoodiesOld;
        int displayableTotal = analysis.GoodiesNew
                               + analysis.GoodiesOld
                               + analysis.GoodiesLocked
                               + analysis.GoodiesInstructions
                               + analysis.GoodiesOther;
        object payload = new
        {
            schemaVersion = InspectSaveSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "inspect-save",
            mutation = false,
            input = new
            {
                path = fullPath,
                verbose,
                dumpMystery
            },
            analysis = new
            {
                filePath = analysis.FilePath ?? fullPath,
                fileName = Path.GetFileName(fullPath),
                fileSize = analysis.FileSize,
                sha256,
                isValid = analysis.IsValid,
                errorMessage = analysis.ErrorMessage,
                isOptionsFile = analysis.IsOptionsFile,
                versionWordHex = $"0x{analysis.VersionWord:X4}",
                versionValid = analysis.VersionValid,
                counts = new
                {
                    completedNodes = analysis.CompletedNodes,
                    partialNodes = analysis.PartialNodes,
                    emptyNodes = analysis.EmptyNodes,
                    completedLinks = analysis.CompletedLinks,
                    totalLinks = analysis.TotalLinks,
                    activeTechSlots = analysis.ActiveTechSlots,
                    totalTechSlots = analysis.TotalTechSlots
                },
                goodies = new
                {
                    displayableUnlocked,
                    displayableTotal,
                    newCount = analysis.GoodiesNew,
                    old = analysis.GoodiesOld,
                    locked = analysis.GoodiesLocked,
                    instructions = analysis.GoodiesInstructions,
                    other = analysis.GoodiesOther,
                    reserved = analysis.GoodiesReserved
                },
                kills = Enumerable.Range(0, KillCategories.Length).Select(index => new
                {
                    categoryIndex = index,
                    categoryName = KillCategories[index],
                    kills = IntAt(analysis.KillCounts, index),
                    meta = ByteAt(analysis.KillMeta, index),
                    nextUnlockThreshold = NullableIntAt(analysis.NextUnlockThresholds, index)
                }),
                rankDistribution = analysis.RankDistribution
                    .OrderBy(row => RankSortKey(row.Key))
                    .ThenBy(row => row.Key, StringComparer.Ordinal)
                    .Select(row => new { rank = row.Key, count = row.Value }),
                completedNodeSamples = analysis.CompletedNodeDetails.Take(5).Select(row => new
                {
                    index = row.Index,
                    world = row.World,
                    rank = row.Rank,
                    rankBitsHex = $"0x{row.RankBits:X8}"
                }),
                settings = new
                {
                    newGoodieCountRaw = analysis.NewGoodieCountRaw,
                    careerInProgress = analysis.CareerInProgressOn,
                    godModeEnabled = analysis.GodModeEnabledOn,
                    soundVolume = analysis.SoundVolume,
                    soundVolumeBitsHex = $"0x{analysis.SoundVolumeBits:X8}",
                    musicVolume = analysis.MusicVolume,
                    musicVolumeBitsHex = $"0x{analysis.MusicVolumeBits:X8}",
                    walkerInvertY = new[] { UIntAt(analysis.InvertYAxisRaw, 0) != 0, UIntAt(analysis.InvertYAxisRaw, 1) != 0 },
                    flightInvertY = new[] { UIntAt(analysis.InvertFlightRaw, 0) != 0, UIntAt(analysis.InvertFlightRaw, 1) != 0 },
                    vibration = new[] { UIntAt(analysis.VibrationRaw, 0) != 0, UIntAt(analysis.VibrationRaw, 1) != 0 },
                    controllerConfig = new[] { UIntAt(analysis.ControllerConfigNum, 0), UIntAt(analysis.ControllerConfigNum, 1) }
                },
                options = new
                {
                    entryCount = analysis.OptionsEntryCount > 0 ? (int?)analysis.OptionsEntryCount : null,
                    tailStartHex = analysis.OptionsTailStart > 0 ? $"0x{analysis.OptionsTailStart:X4}" : null,
                    mouseSensitivity = analysis.OptionsEntryCount > 0 ? (float?)analysis.OptionsMouseSensitivity : null,
                    mouseSensitivityBitsHex = analysis.OptionsEntryCount > 0 ? $"0x{analysis.OptionsMouseSensitivityBits:X8}" : null,
                    controlSchemeIndex = analysis.OptionsEntryCount > 0 ? (ushort?)analysis.OptionsControlSchemeIndex : null,
                    languageIndex = analysis.OptionsEntryCount > 0 ? (ushort?)analysis.OptionsLanguageIndex : null,
                    screenShape = analysis.OptionsEntryCount > 0 ? (uint?)analysis.OptionsScreenShape : null,
                    d3dDeviceIndex = analysis.OptionsEntryCount > 0 ? (uint?)analysis.OptionsD3DDeviceIndex : null
                }
            },
            document = new
            {
                title = document.Title,
                modeText = document.ModeText,
                statusText = document.StatusText,
                metrics = document.Metrics,
                reportText = verbose ? document.ReportText : null
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = InspectSaveSchemaVersion,
                note = "Read-only AppCore host payload. No save/options bytes were changed."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int InspectAssetModelPreview(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "inspect-asset-model-preview requires a generated asset catalog path or directory.");
            return 1;
        }

        int sampleLimit = ParseSampleLimit(args, "inspect-asset-model-preview");
        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetModelPreviewCoverage coverage = new AssetModelPreviewCoverageService().Build(snapshot, sampleLimit);
        object payload = new
        {
            schemaVersion = AssetCatalogModelPreviewCoverageSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "inspect-asset-model-preview",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath),
                sampleLimit
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
            },
            coverage = new
            {
                coverage.TotalModelRows,
                coverage.LooseMeshRows,
                coverage.EmbeddedMeshRows,
                coverage.ExistingExportRows,
                coverage.MissingExportRows,
                coverage.MetadataAvailableRows,
                coverage.WireframeAvailableRows,
                coverage.RowsWithTextureCoordinates,
                coverage.RowsWithTextureCoordinateIndices,
                coverage.TotalTextureCoordinates,
                coverage.TotalTextureCoordinateIndices,
                coverage.RowsWithNormals,
                coverage.RowsWithNormalIndices,
                coverage.TotalNormals,
                coverage.TotalNormalIndices,
                coverage.RowsWithNormalMappingModes,
                coverage.RowsWithNormalReferenceModes,
                coverage.NormalMappingModes,
                coverage.NormalReferenceModes,
                coverage.RowsWithVertexColors,
                coverage.RowsWithVertexColorIndices,
                coverage.TotalVertexColors,
                coverage.TotalVertexColorIndices,
                coverage.RowsWithVertexColorMappingModes,
                coverage.RowsWithVertexColorReferenceModes,
                coverage.VertexColorMappingModes,
                coverage.VertexColorReferenceModes,
                coverage.RowsWithTextureCoordinateMappingModes,
                coverage.RowsWithTextureCoordinateReferenceModes,
                coverage.TextureCoordinateMappingModes,
                coverage.TextureCoordinateReferenceModes,
                coverage.RowsWithMaterials,
                coverage.RowsWithTextureBindings,
                coverage.TotalMaterialNodes,
                coverage.TotalTextureBindingNodes,
                coverage.RowsWithMaterialLayers,
                coverage.RowsWithMaterialAssignmentIndices,
                coverage.TotalMaterialLayerNodes,
                coverage.TotalMaterialAssignmentIndices,
                coverage.RowsWithMaterialMappingModes,
                coverage.RowsWithMaterialReferenceModes,
                coverage.MaterialMappingModes,
                coverage.MaterialReferenceModes,
                coverage.RowsWithObjectConnections,
                coverage.RowsWithPropertyConnections,
                coverage.RowsWithTextureToMaterialConnections,
                coverage.RowsWithTextureToMaterialSlotNames,
                coverage.TotalObjectConnections,
                coverage.TotalPropertyConnections,
                coverage.TotalTextureToMaterialConnections,
                coverage.TextureToMaterialSlotNames,
                coverage.RowsWithCatalogMatchedTextureBindingFiles,
                coverage.RowsWithoutCatalogMatchedTextureBindingFiles,
                coverage.RowsWithAllTextureBindingFilesCatalogMatched,
                coverage.RowsWithAnyMissingCatalogTextureBindingFiles,
                coverage.TotalCatalogMatchedTextureBindingFiles,
                coverage.MetadataWithoutWireframeRows,
                coverage.UnreadableExportRows,
                samples = coverage.Samples,
                unmatchedSamples = coverage.UnmatchedSamples
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetCatalogModelPreviewCoverageSchemaVersion,
                note = "Read-only model-preview coverage payload. Full local paths are intentionally omitted."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int InspectGoodiePreviewCoverage(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "inspect-goodie-preview-coverage requires a generated asset catalog path or directory.");
            return 1;
        }

        int sampleLimit = ParseSampleLimit(args, "inspect-goodie-preview-coverage");
        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        GoodiePreviewCoverage coverage = new GoodiePreviewCoverageService().Build(snapshot, sampleLimit);
        object payload = new
        {
            schemaVersion = AssetCatalogGoodiePreviewCoverageSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "inspect-goodie-preview-coverage",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath),
                sampleLimit
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                goodieRows = snapshot.Summary.GoodieCount,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                videoRows = snapshot.Summary.VideoCount
            },
            coverage = new
            {
                coverage.TotalGoodieRows,
                coverage.SourceGridVisibleRows,
                coverage.SourceGridHiddenRows,
                coverage.TextureBearingRows,
                coverage.TextureMatchedRows,
                coverage.TexturePreviewReadyRows,
                coverage.ModelBearingRows,
                coverage.ModelMatchedRows,
                coverage.ModelExportReadyRows,
                coverage.ModelWireframeReadyRows,
                coverage.VideoRows,
                coverage.VideoCatalogLinkedRows,
                coverage.RowsWithoutLocalPreview,
                samples = coverage.Samples
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetCatalogGoodiePreviewCoverageSchemaVersion,
                note = "Read-only Goodies preview coverage payload. Full local paths and private asset payloads are intentionally omitted."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int InspectAssetCatalogReadability(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "inspect-asset-catalog-readability requires a generated asset catalog path or directory.");
            return 1;
        }

        int sampleLimit = ParseSampleLimit(args, "inspect-asset-catalog-readability");
        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetCatalogReadability readability = new AssetCatalogReadabilityService().Build(snapshot, sampleLimit);
        object payload = new
        {
            schemaVersion = AssetCatalogReadabilitySchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "inspect-asset-catalog-readability",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                sampleLimit
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount,
                videoRows = snapshot.Summary.VideoCount,
                languageRows = snapshot.Summary.LanguageRowCount
            },
            readability = new
            {
                readability.TextureRows,
                readability.TextureExportRows,
                readability.TextureReadablePngRows,
                readability.TextureMissingExportRows,
                readability.TextureUnreadableExportRows,
                readability.TotalModelRows,
                readability.ModelExportRows,
                readability.ModelMetadataAvailableRows,
                readability.ModelWireframeAvailableRows,
                readability.ModelMissingExportRows,
                readability.ModelUnreadableExportRows,
                textureSamples = readability.TextureSamples,
                modelSamples = readability.ModelSamples
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetCatalogReadabilitySchemaVersion,
                note = "Read-only asset-catalog readability payload. Full local paths and private asset payloads are intentionally omitted."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int InspectAssetMaterialImportPlan(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "inspect-asset-material-import-plan requires a generated asset catalog path or directory.");
            return 1;
        }

        int sampleLimit = ParseSampleLimit(args, "inspect-asset-material-import-plan");
        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetMaterialImportPlan plan = new AssetMaterialImportPlanService().Build(snapshot, sampleLimit);
        object payload = new
        {
            schemaVersion = AssetMaterialImportPlanSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "inspect-asset-material-import-plan",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath),
                sampleLimit
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
            },
            materialImportPlan = new
            {
                plan.TotalModelRows,
                plan.MetadataAvailableRows,
                plan.RowsWithTextureBindings,
                plan.RowsWithAllTextureBindingsCatalogMatched,
                plan.RowsWithCatalogMissingTextureBindings,
                plan.RowsWithSidecarTexturePreviews,
                plan.RowsWithCatalogMissingSidecarTexturePreviews,
                plan.RowsWithUnresolvedTextureBindings,
                plan.TotalTextureBindingFiles,
                plan.TotalCatalogMatchedTextureBindingFiles,
                plan.TotalCatalogMissingTextureBindingFiles,
                plan.TotalSidecarTextureFiles,
                plan.TotalCatalogMissingSidecarTextureFiles,
                plan.TotalUnresolvedTextureBindingFiles,
                samples = plan.Samples,
                unresolvedSamples = plan.UnresolvedSamples
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialImportPlanSchemaVersion,
                note = "Read-only material-import plan payload. Full local paths and private asset payloads are intentionally omitted."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int ExportAssetMaterialImportManifest(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "export-asset-material-import-manifest requires one generated asset catalog path or directory.");
            return 1;
        }

        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
        object payload = new
        {
            schemaVersion = AssetMaterialImportManifestSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "export-asset-material-import-manifest",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath)
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
            },
            materialImportManifest = manifest,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialImportManifestSchemaVersion,
                note = "Read-only material-import manifest payload. It contains sanitized catalog IDs, labels, and file names only; full local paths and private asset payloads are intentionally omitted."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int PlanAssetMaterialImportDryRun(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "plan-asset-material-import-dry-run requires one generated asset catalog path or directory.");
            return 1;
        }

        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
        AssetMaterialImportDryRunPlan dryRunPlan = new AssetMaterialImportDryRunPlanService().Build(manifest);
        object payload = new
        {
            schemaVersion = AssetMaterialImportDryRunPlanSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "plan-asset-material-import-dry-run",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath)
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
            },
            materialImportDryRunPlan = dryRunPlan,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialImportDryRunPlanSchemaVersion,
                note = "Read-only material-import dry-run plan. It emits deterministic relative operations only; no asset bytes are copied and no full local paths are included."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int PlanAssetMaterialImportPackage(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "plan-asset-material-import-package requires one generated asset catalog path or directory.");
            return 1;
        }

        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(args[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
        AssetMaterialImportPackagePlan packagePlan = new AssetMaterialImportPackagePlanService().Build(manifest);
        object payload = new
        {
            schemaVersion = AssetMaterialImportPackagePlanSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "plan-asset-material-import-package",
            mutation = false,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath)
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
            },
            materialImportPackagePlan = packagePlan,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialImportPackagePlanSchemaVersion,
                note = "Read-only material-import package plan. It emits deterministic package-relative file entries only; no asset bytes are copied and no full local paths are included."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int MaterializeAssetMaterialImportPackage(string[] args)
    {
        if (!TryParseMaterializationArgs(args, out bool explicitPreflight, out string armPhrase, out string[] positional, out string error))
        {
            WriteError("appcore-host-error.v1", error);
            return 1;
        }

        if (positional.Length != 2)
        {
            WriteError(
                "appcore-host-error.v1",
                "materialize-asset-material-import-package requires <catalog.json-or-directory> <output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"].");
            return 1;
        }

        bool executeCopy = !explicitPreflight && !string.IsNullOrWhiteSpace(armPhrase);
        if (executeCopy && !string.Equals(armPhrase, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
        {
            WriteError(
                "appcore-host-error.v1",
                "Refusing to copy private asset bytes: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
            return 1;
        }

        string? catalogFilePath = AssetCatalogService.ResolveCatalogFilePath(positional[0]);
        if (catalogFilePath is null)
        {
            WriteError("appcore-host-error.v1", "Generated asset catalog was not found at the supplied path or directory.");
            return 1;
        }

        AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogFilePath);
        AssetMaterialImportPackageMaterializationService service = new();
        AssetMaterialImportPackageMaterializationResult result = executeCopy
            ? service.Materialize(snapshot, positional[1])
            : service.Preflight(snapshot, positional[1]);
        object payload = new
        {
            schemaVersion = AssetMaterialImportPackageMaterializationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "materialize-asset-material-import-package",
            mode = executeCopy ? "copy" : "preflight",
            mutation = executeCopy,
            input = new
            {
                catalogFileName = Path.GetFileName(catalogFilePath),
                catalogSha256 = HashFileSha256(catalogFilePath),
                outputRootName = BuildOutputRootName(positional[1]),
                explicitPreflight,
                armedPrivateAssetOutput = executeCopy
            },
            catalog = new
            {
                totalCatalogEntries = snapshot.Summary.TotalCatalogEntries,
                textureRows = snapshot.Summary.TextureCount,
                looseMeshRows = snapshot.Summary.LooseMeshCount,
                embeddedMeshRows = snapshot.Summary.EmbeddedMeshCount
            },
            materialImportPackageMaterialization = result,
            artifact = new
            {
                kind = "app-owned-private-output",
                mutation = executeCopy,
                originalGameMutation = false,
                schemaVersion = AssetMaterialImportPackageMaterializationSchemaVersion,
                note = executeCopy
                    ? "Copies ready model and texture exports into the supplied output root using package-relative destinations; no installed game files or original executable bytes are modified, and raw source paths are omitted from this JSON."
                    : "Preflights ready model and texture package output using package-relative destinations only; no asset bytes are copied, no output root is created, and raw source paths are omitted from this JSON."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return result.Completed ? 0 : 1;
    }

    private static int MaterializeAssetMaterialPackageRebuildScene(string[] args)
    {
        if (!TryParseMaterializationArgs(args, out bool explicitPreflight, out string armPrivateAssetOutput, out string[] positional, out string error))
        {
            WriteError("appcore-host-error.v1", error);
            return 1;
        }

        if (positional.Length != 1)
        {
            WriteError("appcore-host-error.v1", "materialize-asset-material-package-rebuild-scene requires <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"].");
            return 1;
        }

        string packageRoot = positional[0];
        bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
        if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
        {
            WriteError("appcore-host-error.v1", "Refusing to write rebuild scene contract outputs: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
            return 1;
        }

        AssetMaterialImportPackageRebuildSceneService service = new();
        AssetMaterialImportPackageRebuildSceneResult result = executeWrite
            ? service.Materialize(packageRoot)
            : service.Preflight(packageRoot);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageRebuildSceneMaterializationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "materialize-asset-material-package-rebuild-scene",
            mode = executeWrite ? "write" : "preflight",
            mutation = executeWrite,
            input = new
            {
                packageRootName = BuildOutputRootName(packageRoot),
                explicitPreflight,
                armedPrivateAssetOutput = executeWrite
            },
            materialPackageRebuildScene = result,
            artifact = new
            {
                kind = executeWrite ? "app-owned-rebuild-scene-contract" : "preflight",
                mutation = executeWrite,
                originalGameMutation = false,
                schemaVersion = AssetMaterialPackageRebuildSceneMaterializationSchemaVersion,
                note = executeWrite
                    ? "Writes deterministic package-relative scene/mesh/material contract JSON from staged importer-input and rebuild-preview files. It does not launch the game, run a renderer, execute Godot, convert full meshes, or claim rebuild parity."
                    : "Preflights package-relative scene/mesh/material contract output from staged importer-input and rebuild-preview files. No files are written and no original game files are touched."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return result.Completed ? 0 : 1;
    }

    private static int MaterializeAssetMaterialPackageRebuildMesh(string[] args)
    {
        if (!TryParseMaterializationArgs(args, out bool explicitPreflight, out string armPrivateAssetOutput, out string[] positional, out string error))
        {
            WriteError("appcore-host-error.v1", error);
            return 1;
        }

        if (positional.Length != 1)
        {
            WriteError("appcore-host-error.v1", "materialize-asset-material-package-rebuild-mesh requires <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"].");
            return 1;
        }

        string packageRoot = positional[0];
        bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
        if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
        {
            WriteError("appcore-host-error.v1", "Refusing to write rebuild mesh outputs: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
            return 1;
        }

        AssetMaterialImportPackageRebuildMeshService service = new();
        AssetMaterialImportPackageRebuildMeshResult result = executeWrite
            ? service.Materialize(packageRoot)
            : service.Preflight(packageRoot);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageRebuildMeshMaterializationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "materialize-asset-material-package-rebuild-mesh",
            mode = executeWrite ? "write" : "preflight",
            mutation = executeWrite,
            input = new
            {
                packageRootName = BuildOutputRootName(packageRoot),
                explicitPreflight,
                armedPrivateAssetOutput = executeWrite
            },
            materialPackageRebuildMesh = result,
            artifact = new
            {
                kind = executeWrite ? "app-owned-rebuild-mesh" : "preflight",
                mutation = executeWrite,
                originalGameMutation = false,
                schemaVersion = AssetMaterialPackageRebuildMeshMaterializationSchemaVersion,
                note = executeWrite
                    ? "Writes deterministic package-relative OBJ/MTL mesh outputs from existing rebuild-scene contracts and staged FBX data. It does not launch the game, run a renderer, execute Godot, animate meshes, or claim rebuild parity."
                    : "Preflights package-relative OBJ/MTL mesh output from existing rebuild-scene contracts and staged FBX data. No files are written and no original game files are touched."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return result.Completed ? 0 : 1;
    }

    private static int MaterializeAssetMaterialPackageRebuildMeshImport(string[] args)
    {
        if (!TryParseMaterializationArgs(args, out bool explicitPreflight, out string armPrivateAssetOutput, out string[] positional, out string error))
        {
            WriteError("appcore-host-error.v1", error);
            return 1;
        }

        if (positional.Length != 1)
        {
            WriteError("appcore-host-error.v1", "materialize-asset-material-package-rebuild-mesh-import requires <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"].");
            return 1;
        }

        string packageRoot = positional[0];
        bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
        if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
        {
            WriteError("appcore-host-error.v1", "Refusing to write rebuild mesh import contract: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
            return 1;
        }

        AssetMaterialImportPackageRebuildMeshImportService service = new();
        AssetMaterialImportPackageRebuildMeshImportResult result = executeWrite
            ? service.Materialize(packageRoot)
            : service.Preflight(packageRoot);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageRebuildMeshImportSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "materialize-asset-material-package-rebuild-mesh-import",
            mode = executeWrite ? "write" : "preflight",
            mutation = executeWrite,
            input = new
            {
                packageRootName = BuildOutputRootName(packageRoot),
                explicitPreflight,
                armedPrivateAssetOutput = executeWrite
            },
            materialPackageRebuildMeshImport = result,
            artifact = new
            {
                kind = executeWrite ? "app-owned-rebuild-mesh-import-contract" : "preflight",
                mutation = executeWrite,
                originalGameMutation = false,
                schemaVersion = AssetMaterialPackageRebuildMeshImportSchemaVersion,
                note = executeWrite
                    ? "Writes a deterministic package-relative import validation manifest after parsing the generated OBJ/MTL rebuild mesh outputs and validating mesh counts, material references, and staged texture paths. It does not launch the game, run a renderer, execute Godot, or claim rebuild parity."
                    : "Preflights generated OBJ/MTL rebuild mesh outputs as importer-consumable package-local data. No files are written and no original game files are touched."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return result.Completed ? 0 : 1;
    }

    private static int InspectAssetMaterialPackage(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "inspect-asset-material-package requires one materialized package output directory.");
            return 1;
        }

        AssetMaterialImportPackageInspectionResult inspection =
            new AssetMaterialImportPackageInspectionService().Inspect(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageInspectionSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "inspect-asset-material-package",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageInspection = inspection,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageInspectionSchemaVersion,
                note = "Read-only material package inspection. Validates the package manifest and package-relative payload files; raw local paths are omitted from this JSON."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return inspection.Completed ? 0 : 1;
    }

    private static int BuildAssetMaterialPackageWorkOrder(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "build-asset-material-package-work-order requires one materialized package output directory.");
            return 1;
        }

        AssetMaterialImportPackageWorkOrderResult workOrder =
            new AssetMaterialImportPackageWorkOrderService().Build(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageWorkOrderSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "build-asset-material-package-work-order",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageWorkOrder = workOrder,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageWorkOrderSchemaVersion,
                note = "Read-only material package work order. Converts a validated package manifest into package-relative importer/rebuild tasks; raw local paths are omitted from this JSON."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return workOrder.Completed ? 0 : 1;
    }

    private static int ValidateAssetMaterialPackageWorkOrderSidecar(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "validate-asset-material-package-work-order-sidecar requires one materialized package output directory.");
            return 1;
        }

        AssetMaterialImportPackageWorkOrderSidecarValidationResult validation =
            new AssetMaterialImportPackageWorkOrderService().ValidateSidecar(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageWorkOrderSidecarValidationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "validate-asset-material-package-work-order-sidecar",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageWorkOrderSidecarValidation = validation,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageWorkOrderSidecarValidationSchemaVersion,
                note = "Read-only material package work-order sidecar validation. Reads the saved sidecar and rejects stale or path-leaking importer/rebuild tasks by comparing them with a fresh package-relative work-order build."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return validation.Completed ? 0 : 1;
    }

    private static int BuildAssetMaterialPackageImporterBatch(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "build-asset-material-package-importer-batch requires one materialized package output directory.");
            return 1;
        }

        AssetMaterialImportPackageImporterBatchResult batch =
            new AssetMaterialImportPackageImporterBatchService().Build(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageImporterBatchSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "build-asset-material-package-importer-batch",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageImporterBatch = batch,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageImporterBatchSchemaVersion,
                note = "Read-only material package importer batch. Consumes only a validated package work-order sidecar and emits flat package-relative model/texture task rows for future importer/rebuild tooling."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return batch.Completed ? 0 : 1;
    }

    private static int BuildAssetMaterialPackageImporterDryRun(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "build-asset-material-package-importer-dry-run requires one materialized package output directory.");
            return 1;
        }

        AssetMaterialImportPackageImporterDryRunResult dryRun =
            new AssetMaterialImportPackageImporterDryRunService().Build(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageImporterDryRunSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "build-asset-material-package-importer-dry-run",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageImporterDryRun = dryRun,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageImporterDryRunSchemaVersion,
                note = "Read-only material package importer dry-run. Consumes a validated importer batch and emits package-relative adapter rows for future importer/rebuild tooling."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return dryRun.Completed ? 0 : 1;
    }

    private static int ValidateAssetMaterialPackageImporterDryRunSidecar(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "validate-asset-material-package-importer-dry-run-sidecar requires one materialized package output directory.");
            return 1;
        }

        AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation =
            new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageImporterDryRunSidecarValidationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "validate-asset-material-package-importer-dry-run-sidecar",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageImporterDryRunSidecarValidation = validation,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageImporterDryRunSidecarValidationSchemaVersion,
                note = "Read-only material package importer dry-run sidecar validation. Reads the saved adapter sidecar and rejects stale or path-leaking importer/rebuild rows by comparing them with a fresh package-relative importer dry-run build."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return validation.Completed ? 0 : 1;
    }

    private static int MaterializeAssetMaterialPackageImporterInput(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "materialize-asset-material-package-importer-input requires one materialized package output directory.");
            return 1;
        }

        string packageRoot = args[0];
        bool explicitPreflight = false;
        string? armPrivateAssetOutput = null;
        for (int index = 1; index < args.Length; index++)
        {
            if (string.Equals(args[index], "--preflight", StringComparison.OrdinalIgnoreCase))
            {
                explicitPreflight = true;
                continue;
            }

            if (string.Equals(args[index], "--arm-private-asset-output", StringComparison.OrdinalIgnoreCase) &&
                index + 1 < args.Length)
            {
                armPrivateAssetOutput = args[++index];
            }
        }

        bool executeCopy = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
        if (executeCopy && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
        {
            WriteError("appcore-host-error.v1", "Refusing to stage private asset bytes: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
            return 1;
        }

        AssetMaterialImportPackageImporterInputService service = new();
        AssetMaterialImportPackageImporterInputMaterializationResult result = executeCopy
            ? service.Materialize(packageRoot)
            : service.Preflight(packageRoot);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageImporterInputMaterializationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "materialize-asset-material-package-importer-input",
            mode = executeCopy ? "copy" : "preflight",
            mutation = executeCopy,
            input = new
            {
                packageRootName = BuildOutputRootName(packageRoot),
                explicitPreflight,
                armedPrivateAssetOutput = executeCopy
            },
            materialPackageImporterInputMaterialization = result,
            artifact = new
            {
                kind = executeCopy ? "app-owned-materialization" : "preflight",
                mutation = executeCopy,
                originalGameMutation = false,
                schemaVersion = AssetMaterialPackageImporterInputMaterializationSchemaVersion,
                note = executeCopy
                    ? "Copies validated package-local model/texture payloads into importer-input using package-relative adapter paths; no installed game files or original executable bytes are modified."
                    : "Preflights importer-input staging from a validated package-local dry-run sidecar; no files are copied and no original game files are touched."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return result.Completed ? 0 : 1;
    }

    private static int BuildAssetMaterialPackageImporterInputPlan(string[] args)
    {
        if (args.Length != 1)
        {
            WriteError("appcore-host-error.v1", "build-asset-material-package-importer-input-plan requires one materialized package output directory with staged importer-input files.");
            return 1;
        }

        AssetMaterialImportPackageImporterInputPlanResult plan =
            new AssetMaterialImportPackageImporterInputPlanService().Build(args[0]);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageImporterInputPlanSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "build-asset-material-package-importer-input-plan",
            mutation = false,
            input = new
            {
                packageRootName = BuildOutputRootName(args[0])
            },
            materialPackageImporterInputPlan = plan,
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = AssetMaterialPackageImporterInputPlanSchemaVersion,
                note = "Builds a read-only importer/rebuild consumer plan from package-local importer-input files. It validates staged FBX/PNG readability and emits model-import and texture-bind jobs without running an importer, renderer, game executable, or Godot."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return plan.Completed ? 0 : 1;
    }

    private static int MaterializeAssetMaterialPackageRebuildPreview(string[] args)
    {
        if (!TryParseMaterializationArgs(args, out bool explicitPreflight, out string armPrivateAssetOutput, out string[] positional, out string error))
        {
            WriteError("appcore-host-error.v1", error);
            return 1;
        }

        if (positional.Length != 1)
        {
            WriteError("appcore-host-error.v1", "materialize-asset-material-package-rebuild-preview requires <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"].");
            return 1;
        }

        string packageRoot = positional[0];
        bool executeWrite = !explicitPreflight && !string.IsNullOrWhiteSpace(armPrivateAssetOutput);
        if (executeWrite && !string.Equals(armPrivateAssetOutput, PrivateAssetOutputArmPhrase, StringComparison.Ordinal))
        {
            WriteError("appcore-host-error.v1", "Refusing to write rebuild preview outputs: --arm-private-asset-output must exactly match MATERIALIZE ASSET MATERIAL PACKAGE.");
            return 1;
        }

        AssetMaterialImportPackageRebuildPreviewService service = new();
        AssetMaterialImportPackageRebuildPreviewResult result = executeWrite
            ? service.Materialize(packageRoot)
            : service.Preflight(packageRoot);
        object payload = new
        {
            schemaVersion = AssetMaterialPackageRebuildPreviewMaterializationSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "materialize-asset-material-package-rebuild-preview",
            mode = executeWrite ? "write" : "preflight",
            mutation = executeWrite,
            input = new
            {
                packageRootName = BuildOutputRootName(packageRoot),
                explicitPreflight,
                armedPrivateAssetOutput = executeWrite
            },
            materialPackageRebuildPreview = result,
            artifact = new
            {
                kind = executeWrite ? "app-owned-rebuild-preview" : "preflight",
                mutation = executeWrite,
                originalGameMutation = false,
                schemaVersion = AssetMaterialPackageRebuildPreviewMaterializationSchemaVersion,
                note = executeWrite
                    ? "Writes deterministic OBJ wireframe preview files and binding sidecars from staged importer-input files under the app-owned package output. It does not launch the game, run a renderer, execute Godot, or claim rebuild parity."
                    : "Preflights deterministic OBJ wireframe preview and binding sidecar output from staged importer-input files. No files are written and no original game files are touched."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return result.Completed ? 0 : 1;
    }

    private static int CompareSaves(string[] args)
    {
        if (args.Length < 2)
        {
            WriteError("appcore-host-error.v1", "compare-saves requires left and right .bes/.bea/defaultoptions.bea paths.");
            return 1;
        }

        string leftPath = Path.GetFullPath(args[0]);
        string rightPath = Path.GetFullPath(args[1]);
        bool verbose = args.Any(arg => string.Equals(arg, "--verbose", StringComparison.OrdinalIgnoreCase));
        EnsureSupportedExistingSave(leftPath, "Left");
        EnsureSupportedExistingSave(rightPath, "Right");

        BesFilePatcher.CompareResult comparison = BesFilePatcher.CompareFiles(leftPath, rightPath);
        string leftSha256 = HashFileSha256(leftPath);
        string rightSha256 = HashFileSha256(rightPath);
        string? reportText = verbose ? BesFilePatcher.FormatCompareReport(comparison, leftPath, rightPath) : null;
        bool identical = comparison.ErrorMessage is null && comparison.SameSize && comparison.DifferingBytes == 0;
        object payload = new
        {
            schemaVersion = CompareSavesSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "compare-saves",
            mutation = false,
            input = new
            {
                leftPath,
                rightPath,
                verbose
            },
            comparison = new
            {
                leftPath,
                rightPath,
                leftFileName = comparison.File1Name,
                rightFileName = comparison.File2Name,
                leftFileSize = comparison.File1Size,
                rightFileSize = comparison.File2Size,
                leftSha256,
                rightSha256,
                sameSize = comparison.SameSize,
                identical,
                differingBytes = comparison.DifferingBytes,
                errorMessage = comparison.ErrorMessage,
                topRegions = comparison.RegionCounts
                    .OrderByDescending(row => row.Value)
                    .ThenBy(row => row.Key, StringComparer.Ordinal)
                    .Take(12)
                    .Select(row => new { region = row.Key, differingBytes = row.Value }),
                diffRanges = comparison.DiffRanges.Take(50).Select(range => new
                {
                    startOffsetHex = $"0x{range.Start:X4}",
                    endOffsetHex = $"0x{Math.Max(range.Start, range.End - 1):X4}",
                    endOffsetExclusiveHex = $"0x{range.End:X4}",
                    byteLength = Math.Max(0, range.End - range.Start)
                })
            },
            document = new
            {
                title = $"Comparison: {Path.GetFileName(leftPath)} vs {Path.GetFileName(rightPath)}",
                statusText = comparison.ErrorMessage is null
                    ? identical
                        ? "Files are identical."
                        : $"{comparison.DifferingBytes} differing bytes."
                    : $"Error: {comparison.ErrorMessage}",
                reportText
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = CompareSavesSchemaVersion,
                note = "Read-only AppCore host comparison payload. No save/options bytes were changed."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static int PreviewSavePatch(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "preview-save-patch requires a .bes/.bea/defaultoptions.bea path.");
            return 1;
        }

        SavePatchPreviewOptions options = ParseSavePatchPreviewOptions(args);
        string fullPath = Path.GetFullPath(options.InputPath);
        EnsureSupportedExistingSave(fullPath, "Input");

        BesFilePatcher patcher = BuildPreviewPatcher(options);
        if (IsOptionsLikePath(fullPath) && HasCareerSectionPatches(patcher) && !options.AllowCareerSectionsOnOptionsFile)
        {
            WriteError(
                "appcore-host-error.v1",
                "Career section patch preview is blocked for .bea/defaultoptions files by default. Use --no-nodes --no-links --no-goodies --no-kills for settings-only previews or pass --allow-career-sections-on-options-file intentionally.");
            return 1;
        }

        string tempDir = Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditor.AppCore.Host", Guid.NewGuid().ToString("N"));
        string extension = Path.GetExtension(fullPath);
        string previewPath = Path.Combine(tempDir, $"{Path.GetFileNameWithoutExtension(fullPath)}.preview{extension}");
        bool tempOutputDeleted = false;

        try
        {
            Directory.CreateDirectory(tempDir);
            SaveAnalysis before = BesFilePatcher.AnalyzeSave(fullPath);
            PatchResult patchResult = patcher.PatchFile(fullPath, previewPath);
            if (!patchResult.Success)
            {
                WriteError("appcore-host-error.v1", patchResult.Message);
                return 1;
            }

            SaveAnalysis after = BesFilePatcher.AnalyzeSave(previewPath);
            BesFilePatcher.CompareResult comparison = BesFilePatcher.CompareFiles(fullPath, previewPath);
            string sourceSha256 = HashFileSha256(fullPath);
            string previewSha256 = HashFileSha256(previewPath);
            try
            {
                Directory.Delete(tempDir, recursive: true);
                tempOutputDeleted = !Directory.Exists(tempDir);
            }
            catch
            {
                tempOutputDeleted = false;
            }

            bool wouldChange = comparison.ErrorMessage is null && comparison.DifferingBytes > 0;
            object payload = new
            {
                schemaVersion = PreviewSavePatchSchemaVersion,
                generatedAt = DateTimeOffset.UtcNow,
                command = "preview-save-patch",
                mutation = false,
                input = new
                {
                    path = fullPath,
                    rank = patcher.Rank,
                    kills = patcher.GlobalKillCount,
                    useNewGoodies = patcher.UseNewGoodiesInstead,
                    patchNodes = patcher.PatchNodes,
                    patchLinks = patcher.PatchLinks,
                    patchGoodies = patcher.PatchGoodies,
                    patchKills = patcher.PatchKills,
                    allowCareerSectionsOnOptionsFile = options.AllowCareerSectionsOnOptionsFile,
                    levelRanks = options.LevelRanks
                        .OrderBy(row => row.Key)
                        .Select(row => new { nodeIndex = row.Key + 1, rank = row.Value }),
                    perCategoryKills = options.PerCategoryKills
                        .OrderBy(row => row.Key)
                        .Select(row => new
                        {
                            categoryIndex = row.Key,
                            categoryName = KillCategoryName(row.Key),
                            kills = row.Value
                        })
                },
                source = new
                {
                    path = fullPath,
                    fileName = Path.GetFileName(fullPath),
                    fileSize = before.FileSize,
                    sha256 = sourceSha256,
                    isValid = before.IsValid,
                    isOptionsFile = before.IsOptionsFile,
                    versionWordHex = $"0x{before.VersionWord:X4}",
                    versionValid = before.VersionValid
                },
                preview = new
                {
                    success = true,
                    message = patchResult.Message,
                    wouldChange,
                    tempOutputDeleted,
                    candidateSha256 = previewSha256,
                    differingBytes = comparison.DifferingBytes,
                    topRegion = comparison.RegionCounts
                        .OrderByDescending(row => row.Value)
                        .ThenBy(row => row.Key, StringComparer.Ordinal)
                        .Select(row => row.Key)
                        .FirstOrDefault()
                },
                beforeAfter = new
                {
                    completedNodes = new { before = before.CompletedNodes, after = after.CompletedNodes },
                    partialNodes = new { before = before.PartialNodes, after = after.PartialNodes },
                    displayableGoodiesUnlocked = new
                    {
                        before = before.GoodiesNew + before.GoodiesOld,
                        after = after.GoodiesNew + after.GoodiesOld
                    },
                    totalKills = new
                    {
                        before = before.KillCounts.Sum(),
                        after = after.KillCounts.Sum()
                    },
                    rankDistribution = new
                    {
                        before = before.RankDistribution
                            .OrderBy(row => RankSortKey(row.Key))
                            .ThenBy(row => row.Key, StringComparer.Ordinal)
                            .Select(row => new { rank = row.Key, count = row.Value }),
                        after = after.RankDistribution
                            .OrderBy(row => RankSortKey(row.Key))
                            .ThenBy(row => row.Key, StringComparer.Ordinal)
                            .Select(row => new { rank = row.Key, count = row.Value })
                    }
                },
                comparison = new
                {
                    sameSize = comparison.SameSize,
                    identical = comparison.ErrorMessage is null && comparison.SameSize && comparison.DifferingBytes == 0,
                    differingBytes = comparison.DifferingBytes,
                    errorMessage = comparison.ErrorMessage,
                    topRegions = comparison.RegionCounts
                        .OrderByDescending(row => row.Value)
                        .ThenBy(row => row.Key, StringComparer.Ordinal)
                        .Take(12)
                        .Select(row => new { region = row.Key, differingBytes = row.Value }),
                    diffRanges = comparison.DiffRanges.Take(50).Select(range => new
                    {
                        startOffsetHex = $"0x{range.Start:X4}",
                        endOffsetHex = $"0x{Math.Max(range.Start, range.End - 1):X4}",
                        endOffsetExclusiveHex = $"0x{range.End:X4}",
                        byteLength = Math.Max(0, range.End - range.Start)
                    })
                },
                artifact = new
                {
                    kind = "read-only",
                    mutation = false,
                    schemaVersion = PreviewSavePatchSchemaVersion,
                    note = "Read-only AppCore host patch preview. The source file was not modified; a temporary patched copy was compared and deleted."
                }
            };

            Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
            return 0;
        }
        finally
        {
            if (!tempOutputDeleted)
            {
                try
                {
                    if (Directory.Exists(tempDir))
                    {
                        Directory.Delete(tempDir, recursive: true);
                    }
                }
                catch
                {
                    // Best-effort cleanup only. The preview payload reports whether the normal cleanup succeeded.
                }
            }
        }
    }

    private static int PlanSavePatch(string[] args)
    {
        if (args.Length == 0)
        {
            WriteError("appcore-host-error.v1", "plan-save-patch requires an appcore-save-patch-request.v1 JSON path.");
            return 1;
        }

        string requestPath = Path.GetFullPath(args[0]);
        if (!File.Exists(requestPath))
        {
            WriteError("appcore-host-error.v1", $"Patch request JSON does not exist: {requestPath}");
            return 1;
        }

        SavePatchPlanRequest request = ReadSavePatchPlanRequest(requestPath);
        SavePatchPreviewOptions options = BuildOptionsFromPlanRequest(request);
        string fullPath = Path.GetFullPath(options.InputPath);
        EnsureSupportedExistingSave(fullPath, "Input");

        BesFilePatcher patcher = BuildPreviewPatcher(options);
        if (IsOptionsLikePath(fullPath) && HasCareerSectionPatches(patcher) && !options.AllowCareerSectionsOnOptionsFile)
        {
            WriteError(
                "appcore-host-error.v1",
                "Career section patch planning is blocked for .bea/defaultoptions files by default. Set patchNodes/patchLinks/patchGoodies/patchKills false for settings-only plans or set allowCareerSectionsOnOptionsFile intentionally.");
            return 1;
        }

        SaveAnalysis before = BesFilePatcher.AnalyzeSave(fullPath);
        string[] sections = PlannedPatchSections(patcher);
        object payload = new
        {
            schemaVersion = PlanSavePatchSchemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            command = "plan-save-patch",
            mutation = false,
            request = new
            {
                schemaVersion = PatchRequestSchemaVersion,
                requestPath,
                requestSha256 = HashFileSha256(requestPath)
            },
            input = new
            {
                path = fullPath,
                rank = patcher.Rank,
                kills = patcher.GlobalKillCount,
                useNewGoodies = patcher.UseNewGoodiesInstead,
                killsOnly = patcher.KillsOnly,
                patchNodes = patcher.PatchNodes,
                patchLinks = patcher.PatchLinks,
                patchGoodies = patcher.PatchGoodies,
                patchKills = patcher.PatchKills,
                allowCareerSectionsOnOptionsFile = options.AllowCareerSectionsOnOptionsFile,
                levelRanks = options.LevelRanks
                    .OrderBy(row => row.Key)
                    .Select(row => new { nodeIndex = row.Key + 1, rank = row.Value }),
                perCategoryKills = options.PerCategoryKills
                    .OrderBy(row => row.Key)
                    .Select(row => new
                    {
                        categoryIndex = row.Key,
                        categoryName = KillCategoryName(row.Key),
                        kills = row.Value
                    })
            },
            source = new
            {
                path = fullPath,
                fileName = Path.GetFileName(fullPath),
                fileSize = before.FileSize,
                sha256 = HashFileSha256(fullPath),
                isValid = before.IsValid,
                isOptionsFile = before.IsOptionsFile,
                versionWordHex = $"0x{before.VersionWord:X4}",
                versionValid = before.VersionValid
            },
            current = new
            {
                completedNodes = before.CompletedNodes,
                partialNodes = before.PartialNodes,
                displayableGoodiesUnlocked = before.GoodiesNew + before.GoodiesOld,
                totalKills = before.KillCounts.Sum(),
                kills = Enumerable.Range(0, KillCategories.Length).Select(index => new
                {
                    categoryIndex = index,
                    categoryName = KillCategories[index],
                    kills = IntAt(before.KillCounts, index),
                    meta = ByteAt(before.KillMeta, index)
                }),
                rankDistribution = before.RankDistribution
                    .OrderBy(row => RankSortKey(row.Key))
                    .ThenBy(row => row.Key, StringComparer.Ordinal)
                    .Select(row => new { rank = row.Key, count = row.Value })
            },
            plan = new
            {
                accepted = true,
                targetKind = before.IsOptionsFile ? "global-options" : "career-save",
                sections,
                sectionCount = sections.Length,
                levelRankCount = options.LevelRanks.Count,
                perCategoryKillCount = options.PerCategoryKills.Count,
                willPatchCareerSections = HasCareerSectionPatches(patcher),
                requiresCopiedApply = true,
                sourceUnchanged = true,
                notes = new[]
                {
                    "Plan-only AppCore host payload. No source bytes were changed.",
                    "Future apply jobs must run against an explicit copied target or backup-backed workflow.",
                    "The request JSON is preserved so Electron can replay the same typed intent during preview/apply parity checks."
                }
            },
            artifact = new
            {
                kind = "read-only",
                mutation = false,
                schemaVersion = PlanSavePatchSchemaVersion,
                note = "Read-only AppCore host patch plan. The source file was not modified and no temporary patched copy was created."
            }
        };

        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
        return 0;
    }

    private static bool IsHelp(string value)
    {
        return string.Equals(value, "-h", StringComparison.OrdinalIgnoreCase)
               || string.Equals(value, "--help", StringComparison.OrdinalIgnoreCase)
               || string.Equals(value, "help", StringComparison.OrdinalIgnoreCase);
    }

    private static void WriteUsage()
    {
        Console.WriteLine("Usage:");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host inspect-save <path> [--verbose] [--dump-mystery]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host compare-saves <left> <right> [--verbose]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host preview-save-patch <path> [--rank S] [--kills 100] [--new] [--kills-only] [--no-nodes] [--no-links] [--no-goodies] [--no-kills]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host plan-save-patch <appcore-save-patch-request.v1.json>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host inspect-asset-model-preview <catalog.json-or-directory> [--sample-limit 12]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host inspect-goodie-preview-coverage <catalog.json-or-directory> [--sample-limit 12]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host inspect-asset-catalog-readability <catalog.json-or-directory> [--sample-limit 12]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host inspect-asset-material-import-plan <catalog.json-or-directory> [--sample-limit 12]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host export-asset-material-import-manifest <catalog.json-or-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host plan-asset-material-import-dry-run <catalog.json-or-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host plan-asset-material-import-package <catalog.json-or-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host materialize-asset-material-import-package <catalog.json-or-directory> <output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host inspect-asset-material-package <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host build-asset-material-package-work-order <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host validate-asset-material-package-work-order-sidecar <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host build-asset-material-package-importer-batch <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host build-asset-material-package-importer-dry-run <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host validate-asset-material-package-importer-dry-run-sidecar <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host materialize-asset-material-package-importer-input <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host build-asset-material-package-importer-input-plan <package-output-directory>");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host materialize-asset-material-package-rebuild-preview <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host materialize-asset-material-package-rebuild-scene <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host materialize-asset-material-package-rebuild-mesh <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"]");
        Console.WriteLine("  OnslaughtCareerEditor.AppCore.Host materialize-asset-material-package-rebuild-mesh-import <package-output-directory> [--preflight] [--arm-private-asset-output \"MATERIALIZE ASSET MATERIAL PACKAGE\"]");
    }

    private static bool TryParseMaterializationArgs(
        string[] args,
        out bool explicitPreflight,
        out string armPhrase,
        out string[] positional,
        out string error)
    {
        explicitPreflight = false;
        armPhrase = string.Empty;
        error = string.Empty;
        List<string> positionalArgs = new();
        for (int index = 0; index < args.Length; index++)
        {
            string arg = args[index];
            if (string.Equals(arg, "--preflight", StringComparison.OrdinalIgnoreCase))
            {
                explicitPreflight = true;
                continue;
            }

            if (string.Equals(arg, "--arm-private-asset-output", StringComparison.OrdinalIgnoreCase))
            {
                if (index + 1 >= args.Length)
                {
                    positional = Array.Empty<string>();
                    error = "--arm-private-asset-output requires an arm phrase value.";
                    return false;
                }

                armPhrase = args[++index];
                continue;
            }

            const string armPrefix = "--arm-private-asset-output=";
            if (arg.StartsWith(armPrefix, StringComparison.OrdinalIgnoreCase))
            {
                armPhrase = arg[armPrefix.Length..];
                continue;
            }

            if (arg.StartsWith("--", StringComparison.Ordinal))
            {
                positional = Array.Empty<string>();
                error = $"Unsupported materialization option: {arg}";
                return false;
            }

            positionalArgs.Add(arg);
        }

        positional = positionalArgs.ToArray();
        return true;
    }

    private static string BuildOutputRootName(string outputRoot)
    {
        string fullPath = Path.GetFullPath(outputRoot)
            .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
        return Path.GetFileName(fullPath);
    }

    private static void WriteError(string schemaVersion, string message)
    {
        var payload = new
        {
            schemaVersion,
            generatedAt = DateTimeOffset.UtcNow,
            mutation = false,
            error = new
            {
                message
            }
        };
        Console.WriteLine(JsonSerializer.Serialize(payload, JsonOptions));
    }

    private static bool IsSupportedSavePath(string filePath)
    {
        string extension = Path.GetExtension(filePath);
        string fileName = Path.GetFileName(filePath);
        return string.Equals(extension, ".bes", StringComparison.OrdinalIgnoreCase)
               || string.Equals(extension, ".bea", StringComparison.OrdinalIgnoreCase)
               || fileName.StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsOptionsLikePath(string filePath)
    {
        string fileName = Path.GetFileName(filePath);
        return string.Equals(Path.GetExtension(filePath), ".bea", StringComparison.OrdinalIgnoreCase)
               || fileName.StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);
    }

    private static void EnsureSupportedExistingSave(string filePath, string label)
    {
        if (!File.Exists(filePath))
        {
            throw new FileNotFoundException($"{label} input file does not exist.", filePath);
        }

        if (!IsSupportedSavePath(filePath))
        {
            throw new InvalidDataException($"{label} input must be a .bes career save, .bea options file, or defaultoptions.bea backup.");
        }
    }

    private static string HashFileSha256(string filePath)
    {
        using FileStream stream = File.OpenRead(filePath);
        return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
    }

    private static BesFilePatcher BuildPreviewPatcher(SavePatchPreviewOptions options)
    {
        var patcher = new BesFilePatcher
        {
            UseNewGoodiesInstead = options.UseNewGoodies,
            GlobalKillCount = options.GlobalKillCount,
            Rank = options.Rank,
            LevelRanks = options.LevelRanks.Count > 0 ? new Dictionary<int, string>(options.LevelRanks) : null,
            PerCategoryKills = options.PerCategoryKills.Count > 0 ? new Dictionary<int, int>(options.PerCategoryKills) : null
        };

        if (options.KillsOnly)
        {
            patcher.KillsOnly = true;
        }
        else
        {
            patcher.PatchNodes = options.PatchNodes;
            patcher.PatchLinks = options.PatchLinks;
            patcher.PatchGoodies = options.PatchGoodies;
            patcher.PatchKills = options.PatchKills;
        }

        return patcher;
    }

    private static SavePatchPlanRequest ReadSavePatchPlanRequest(string requestPath)
    {
        SavePatchPlanRequest? request = JsonSerializer.Deserialize<SavePatchPlanRequest>(File.ReadAllText(requestPath), JsonOptions);
        if (request is null)
        {
            throw new InvalidDataException("Patch request JSON is empty or invalid.");
        }

        if (!string.Equals(request.SchemaVersion, PatchRequestSchemaVersion, StringComparison.Ordinal))
        {
            throw new InvalidDataException($"Patch request schema must be {PatchRequestSchemaVersion}.");
        }

        if (request.Mutation)
        {
            throw new InvalidDataException("Patch planning requests must have mutation=false.");
        }

        if (request.Input is null)
        {
            throw new InvalidDataException("Patch request JSON is missing input.");
        }

        return request;
    }

    private static SavePatchPreviewOptions BuildOptionsFromPlanRequest(SavePatchPlanRequest request)
    {
        SavePatchPlanInput input = request.Input ?? throw new InvalidDataException("Patch request JSON is missing input.");
        if (string.IsNullOrWhiteSpace(input.Path))
        {
            throw new InvalidDataException("Patch request input.path is required.");
        }

        var options = new SavePatchPreviewOptions
        {
            InputPath = input.Path,
            Rank = NormalizeRank(string.IsNullOrWhiteSpace(input.Rank) ? "S" : input.Rank),
            GlobalKillCount = ValidateKillCount(input.Kills ?? 100, "input.kills"),
            UseNewGoodies = input.UseNewGoodies ?? false,
            KillsOnly = input.KillsOnly ?? false,
            PatchNodes = input.PatchNodes ?? true,
            PatchLinks = input.PatchLinks ?? true,
            PatchGoodies = input.PatchGoodies ?? true,
            PatchKills = input.PatchKills ?? true,
            AllowCareerSectionsOnOptionsFile = input.AllowCareerSectionsOnOptionsFile ?? false
        };

        foreach (LevelRankInput row in input.LevelRanks ?? [])
        {
            if (row.NodeIndex < 1 || row.NodeIndex > 43)
            {
                throw new ArgumentException($"Invalid input.levelRanks nodeIndex {row.NodeIndex}; expected 1-43.");
            }

            options.LevelRanks[row.NodeIndex - 1] = NormalizeRank(row.Rank);
        }

        foreach (CategoryKillsInput row in input.PerCategoryKills ?? [])
        {
            if (row.CategoryIndex < 0 || row.CategoryIndex >= KillCategories.Length)
            {
                throw new ArgumentException($"Invalid input.perCategoryKills categoryIndex {row.CategoryIndex}; expected 0-{KillCategories.Length - 1}.");
            }

            options.PerCategoryKills[row.CategoryIndex] = ValidateKillCount(row.Kills, $"input.perCategoryKills[{row.CategoryIndex}].kills");
        }

        if (options.KillsOnly && !options.PatchKills)
        {
            throw new ArgumentException("killsOnly cannot be combined with patchKills=false.");
        }

        return options;
    }

    private static SavePatchPreviewOptions ParseSavePatchPreviewOptions(string[] args)
    {
        var options = new SavePatchPreviewOptions
        {
            InputPath = args[0]
        };

        for (int i = 1; i < args.Length; i++)
        {
            string arg = args[i];
            switch (arg.ToLowerInvariant())
            {
                case "--rank":
                    options.Rank = NormalizeRank(RequireValue(args, ref i, arg));
                    break;
                case "--kills":
                    options.GlobalKillCount = ParseKillCount(RequireValue(args, ref i, arg), arg);
                    break;
                case "--new":
                    options.UseNewGoodies = true;
                    break;
                case "--kills-only":
                    options.KillsOnly = true;
                    break;
                case "--no-nodes":
                    options.PatchNodes = false;
                    break;
                case "--no-links":
                    options.PatchLinks = false;
                    break;
                case "--no-goodies":
                    options.PatchGoodies = false;
                    break;
                case "--no-kills":
                    options.PatchKills = false;
                    break;
                case "--allow-career-sections-on-options-file":
                    options.AllowCareerSectionsOnOptionsFile = true;
                    break;
                case "--level-rank":
                    ParseLevelRank(RequireValue(args, ref i, arg), options.LevelRanks);
                    break;
                case "--aircraft-kills":
                    options.PerCategoryKills[BesFilePatcher.KILL_AIRCRAFT] = ParseKillCount(RequireValue(args, ref i, arg), arg);
                    break;
                case "--vehicle-kills":
                    options.PerCategoryKills[BesFilePatcher.KILL_VEHICLES] = ParseKillCount(RequireValue(args, ref i, arg), arg);
                    break;
                case "--emplacement-kills":
                    options.PerCategoryKills[BesFilePatcher.KILL_EMPLACEMENTS] = ParseKillCount(RequireValue(args, ref i, arg), arg);
                    break;
                case "--infantry-kills":
                    options.PerCategoryKills[BesFilePatcher.KILL_INFANTRY] = ParseKillCount(RequireValue(args, ref i, arg), arg);
                    break;
                case "--mech-kills":
                    options.PerCategoryKills[BesFilePatcher.KILL_MECHS] = ParseKillCount(RequireValue(args, ref i, arg), arg);
                    break;
                default:
                    throw new ArgumentException($"Unsupported preview-save-patch option: {arg}");
            }
        }

        if (options.KillsOnly && !options.PatchKills)
        {
            throw new ArgumentException("--kills-only cannot be combined with --no-kills.");
        }

        return options;
    }

    private static string RequireValue(string[] args, ref int index, string optionName)
    {
        if (index + 1 >= args.Length || args[index + 1].StartsWith("--", StringComparison.Ordinal))
        {
            throw new ArgumentException($"{optionName} requires a value.");
        }

        index++;
        return args[index];
    }

    private static int ParseKillCount(string value, string optionName)
    {
        if (!int.TryParse(value, out int parsed) || parsed < 0 || parsed > 0x00FFFFFF)
        {
            throw new ArgumentException($"{optionName} must be an integer from 0 to 16777215.");
        }

        return ValidateKillCount(parsed, optionName);
    }

    private static int ValidateKillCount(int parsed, string optionName)
    {
        if (parsed < 0 || parsed > 0x00FFFFFF)
        {
            throw new ArgumentException($"{optionName} must be an integer from 0 to 16777215.");
        }

        return parsed;
    }

    private static string NormalizeRank(string value)
    {
        string rank = value.ToUpperInvariant();
        return rank is "S" or "A" or "B" or "C" or "D" or "E" or "NONE"
            ? rank
            : throw new ArgumentException($"Invalid rank '{value}'. Valid values: S, A, B, C, D, E, NONE.");
    }

    private static void ParseLevelRank(string value, Dictionary<int, string> target)
    {
        string[] parts = value.Split(':', 2);
        if (parts.Length != 2 || !int.TryParse(parts[0], out int level) || level < 1 || level > 43)
        {
            throw new ArgumentException($"Invalid --level-rank entry '{value}', expected NODE_INDEX:GRADE with node index 1-43.");
        }

        target[level - 1] = NormalizeRank(parts[1]);
    }

    private static bool HasCareerSectionPatches(BesFilePatcher patcher)
    {
        return patcher.KillsOnly || patcher.PatchNodes || patcher.PatchLinks || patcher.PatchGoodies || patcher.PatchKills;
    }

    private static string KillCategoryName(int index)
    {
        return index >= 0 && index < KillCategories.Length ? KillCategories[index] : $"Category {index}";
    }

    private static string[] PlannedPatchSections(BesFilePatcher patcher)
    {
        if (patcher.KillsOnly)
        {
            return ["kills"];
        }

        List<string> sections = [];
        if (patcher.PatchNodes)
        {
            sections.Add("nodes");
        }

        if (patcher.PatchLinks)
        {
            sections.Add("links");
        }

        if (patcher.PatchGoodies)
        {
            sections.Add("goodies");
        }

        if (patcher.PatchKills)
        {
            sections.Add("kills");
        }

        return sections.ToArray();
    }

    private static int ParseSampleLimit(string[] args, string commandName)
    {
        int sampleLimit = 12;
        for (int i = 1; i < args.Length; i++)
        {
            string arg = args[i];
            if (!string.Equals(arg, "--sample-limit", StringComparison.OrdinalIgnoreCase))
            {
                throw new ArgumentException($"Unsupported {commandName} option: {arg}");
            }

            if (i + 1 >= args.Length || !int.TryParse(args[i + 1], out sampleLimit) || sampleLimit < 0 || sampleLimit > 100)
            {
                throw new ArgumentException("--sample-limit must be an integer from 0 to 100.");
            }

            i++;
        }

        return sampleLimit;
    }

    private static int RankSortKey(string rank)
    {
        return rank switch
        {
            "S" => 0,
            "A" => 1,
            "B" => 2,
            "C" => 3,
            "D" => 4,
            "E" => 5,
            "NONE" => 6,
            _ => 99
        };
    }

    private static int IntAt(int[] values, int index)
    {
        return index >= 0 && index < values.Length ? values[index] : 0;
    }

    private static byte ByteAt(byte[] values, int index)
    {
        return index >= 0 && index < values.Length ? values[index] : (byte)0;
    }

    private static int? NullableIntAt(int?[] values, int index)
    {
        return index >= 0 && index < values.Length ? values[index] : null;
    }

    private static uint UIntAt(uint[] values, int index)
    {
        return index >= 0 && index < values.Length ? values[index] : 0;
    }

    private sealed class SavePatchPreviewOptions
    {
        public string InputPath { get; init; } = "";
        public bool UseNewGoodies { get; set; }
        public int GlobalKillCount { get; set; } = 100;
        public string Rank { get; set; } = "S";
        public bool KillsOnly { get; set; }
        public bool PatchNodes { get; set; } = true;
        public bool PatchLinks { get; set; } = true;
        public bool PatchGoodies { get; set; } = true;
        public bool PatchKills { get; set; } = true;
        public bool AllowCareerSectionsOnOptionsFile { get; set; }
        public Dictionary<int, string> LevelRanks { get; } = new();
        public Dictionary<int, int> PerCategoryKills { get; } = new();
    }

    private sealed class SavePatchPlanRequest
    {
        public string SchemaVersion { get; set; } = "";
        public bool Mutation { get; set; }
        public SavePatchPlanInput? Input { get; set; }
    }

    private sealed class SavePatchPlanInput
    {
        public string Path { get; set; } = "";
        public string? Rank { get; set; }
        public int? Kills { get; set; }
        public bool? UseNewGoodies { get; set; }
        public bool? KillsOnly { get; set; }
        public bool? PatchNodes { get; set; }
        public bool? PatchLinks { get; set; }
        public bool? PatchGoodies { get; set; }
        public bool? PatchKills { get; set; }
        public bool? AllowCareerSectionsOnOptionsFile { get; set; }
        public List<LevelRankInput>? LevelRanks { get; set; }
        public List<CategoryKillsInput>? PerCategoryKills { get; set; }
    }

    private sealed class LevelRankInput
    {
        public int NodeIndex { get; set; }
        public string Rank { get; set; } = "";
    }

    private sealed class CategoryKillsInput
    {
        public int CategoryIndex { get; set; }
        public int Kills { get; set; }
    }
}
