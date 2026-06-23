using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageWorkOrderService
    {
        public const string WorkOrderFileName = "material-package-work-order.v1.json";
        public const string WorkOrderSchema = "onslaught.asset-material-package-work-order.v1";

        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNameCaseInsensitive = true
        };

        private static readonly JsonSerializerOptions WriteJsonOptions = new(JsonSerializerDefaults.Web)
        {
            WriteIndented = true
        };

        public AssetMaterialImportPackageWorkOrderResult Build(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(fullPackageRoot);

            if (!inspection.ManifestExists || !inspection.SchemaValid)
            {
                return Failure(inspection, inspection.ManifestStatus);
            }

            string manifestPath = Path.Combine(fullPackageRoot, AssetMaterialImportPackageMaterializationService.ManifestFileName);
            AssetMaterialImportPackageOutputManifest? manifest;
            try
            {
                manifest = JsonSerializer.Deserialize<AssetMaterialImportPackageOutputManifest>(
                    File.ReadAllText(manifestPath),
                    JsonOptions);
            }
            catch (JsonException)
            {
                return Failure(inspection, "invalid-json");
            }

            if (manifest is null)
            {
                return Failure(inspection, "empty-manifest");
            }

            Dictionary<string, AssetMaterialImportPackageMaterializedFile> filesByDestination = manifest.Files
                .GroupBy(static file => NormalizeRelativePath(file.DestinationRelativePath), StringComparer.OrdinalIgnoreCase)
                .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase);
            IReadOnlyList<AssetMaterialImportPackageWorkOrderModel> models = manifest.Models
                .OrderBy(static model => NormalizeRelativePath(model.DestinationRelativePath), StringComparer.OrdinalIgnoreCase)
                .ThenBy(static model => model.CatalogId, StringComparer.OrdinalIgnoreCase)
                .Select(model => BuildModel(fullPackageRoot, model, filesByDestination))
                .ToList();

            int textureReferenceRows = models.Sum(static model => model.TextureReferenceCount);
            int resolvedTextureReferenceRows = models.Sum(static model => model.ResolvedTextureReferenceCount);
            int readyTextureReferenceRows = models.Sum(static model => model.ReadyTextureReferenceCount);
            int missingPackageFiles = models.Count(static model => !model.ModelPackageFileExists) +
                models.Sum(static model => model.Textures.Count(static texture => texture.SourceAvailable && !texture.PackageFileExists));
            int unsafePackagePaths = models.Count(static model => model.ModelPathStatus == "unsafe-package-path") +
                models.Sum(static model => model.Textures.Count(static texture => texture.PackagePathStatus == "unsafe-package-path"));
            bool completed =
                inspection.Completed &&
                manifest.Completed &&
                models.All(static model => model.ReadyForImporter);

            return new AssetMaterialImportPackageWorkOrderResult(
                PackageRootName: inspection.PackageRootName,
                ManifestRelativePath: inspection.ManifestRelativePath,
                ManifestStatus: inspection.ManifestStatus,
                ManifestInspectionCompleted: inspection.Completed,
                ManifestModelGraphRows: inspection.ManifestModelGraphRows,
                ManifestReadyModelGraphRows: inspection.ManifestReadyModelGraphRows,
                WorkOrderModelRows: models.Count,
                ReadyWorkOrderModelRows: models.Count(static model => model.ReadyForImporter),
                TextureReferenceRows: textureReferenceRows,
                ResolvedTextureReferenceRows: resolvedTextureReferenceRows,
                ReadyTextureReferenceRows: readyTextureReferenceRows,
                MissingPackageFiles: missingPackageFiles,
                UnsafePackagePaths: unsafePackagePaths,
                ManifestContainsPackageRoot: inspection.ManifestContainsPackageRoot,
                Completed: completed,
                Models: models,
                Issues: inspection.Issues);
        }

        public AssetMaterialImportPackageWorkOrderSidecarWriteResult WriteSidecar(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            AssetMaterialImportPackageWorkOrderResult workOrder = Build(fullPackageRoot);
            if (!Directory.Exists(fullPackageRoot))
            {
                return new AssetMaterialImportPackageWorkOrderSidecarWriteResult(
                    SidecarRelativePath: WorkOrderFileName,
                    SidecarWritten: false,
                    SidecarStatus: "missing-package-root",
                    SidecarBytes: 0,
                    WorkOrder: workOrder);
            }

            AssetMaterialImportPackageWorkOrderSidecar sidecar = new(
                Schema: WorkOrderSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                MaterialPackageWorkOrder: workOrder);
            string sidecarPath = Path.Combine(fullPackageRoot, WorkOrderFileName);
            File.WriteAllText(sidecarPath, JsonSerializer.Serialize(sidecar, WriteJsonOptions));

            return new AssetMaterialImportPackageWorkOrderSidecarWriteResult(
                SidecarRelativePath: WorkOrderFileName,
                SidecarWritten: true,
                SidecarStatus: "written",
                SidecarBytes: new FileInfo(sidecarPath).Length,
                WorkOrder: workOrder);
        }

        public AssetMaterialImportPackageWorkOrderSidecarValidationResult ValidateSidecar(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageWorkOrderResult freshWorkOrder = Build(fullPackageRoot);
            string sidecarPath = Path.Combine(fullPackageRoot, WorkOrderFileName);

            if (!Directory.Exists(fullPackageRoot))
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "missing-package-root",
                    sidecarExists: false,
                    freshWorkOrder,
                    [new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "missing-package-root")]);
            }

            if (!File.Exists(sidecarPath))
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "missing-sidecar",
                    sidecarExists: false,
                    freshWorkOrder,
                    [new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "missing-sidecar")]);
            }

            string sidecarJson = File.ReadAllText(sidecarPath);
            bool sidecarContainsPackageRoot = ContainsPathToken(sidecarJson, fullPackageRoot);
            AssetMaterialImportPackageWorkOrderSidecar? sidecar;
            try
            {
                sidecar = JsonSerializer.Deserialize<AssetMaterialImportPackageWorkOrderSidecar>(sidecarJson, JsonOptions);
            }
            catch (JsonException)
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "invalid-json",
                    sidecarExists: true,
                    freshWorkOrder,
                    [new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "invalid-json")],
                    sidecarBytes: new FileInfo(sidecarPath).Length,
                    sidecarContainsPackageRoot: sidecarContainsPackageRoot);
            }

            if (sidecar is null || sidecar.MaterialPackageWorkOrder is null)
            {
                return BuildSidecarValidationFailure(
                    packageRootName,
                    "empty-sidecar",
                    sidecarExists: true,
                    freshWorkOrder,
                    [new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "empty-sidecar")],
                    sidecarBytes: new FileInfo(sidecarPath).Length,
                    sidecarContainsPackageRoot: sidecarContainsPackageRoot);
            }

            AssetMaterialImportPackageWorkOrderResult sidecarWorkOrder = sidecar.MaterialPackageWorkOrder;
            bool schemaValid = string.Equals(sidecar.Schema, WorkOrderSchema, StringComparison.Ordinal);
            bool workOrderMatchesFreshBuild = WorkOrderPayloadsMatch(sidecarWorkOrder, freshWorkOrder);
            List<AssetMaterialImportPackageWorkOrderSidecarValidationIssue> issues = new();
            if (!schemaValid)
            {
                issues.Add(new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "invalid-schema"));
            }

            if (sidecarContainsPackageRoot)
            {
                issues.Add(new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "package-root-leak"));
            }

            if (!workOrderMatchesFreshBuild)
            {
                issues.Add(new AssetMaterialImportPackageWorkOrderSidecarValidationIssue("sidecar", WorkOrderFileName, "work-order-mismatch"));
            }

            bool completed =
                schemaValid &&
                !sidecarContainsPackageRoot &&
                sidecarWorkOrder.Completed &&
                freshWorkOrder.Completed &&
                workOrderMatchesFreshBuild;
            string status = completed
                ? "ok"
                : schemaValid && workOrderMatchesFreshBuild
                    ? "issues-found"
                    : schemaValid
                        ? "stale-work-order-sidecar"
                        : "invalid-schema";

            return new AssetMaterialImportPackageWorkOrderSidecarValidationResult(
                PackageRootName: packageRootName,
                SidecarRelativePath: WorkOrderFileName,
                SidecarExists: true,
                SidecarStatus: status,
                SidecarBytes: new FileInfo(sidecarPath).Length,
                Schema: sidecar.Schema,
                SchemaValid: schemaValid,
                SidecarContainsPackageRoot: sidecarContainsPackageRoot,
                SidecarCompletedFlag: sidecarWorkOrder.Completed,
                FreshWorkOrderCompleted: freshWorkOrder.Completed,
                WorkOrderMatchesFreshBuild: workOrderMatchesFreshBuild,
                SidecarWorkOrderModelRows: sidecarWorkOrder.WorkOrderModelRows,
                FreshWorkOrderModelRows: freshWorkOrder.WorkOrderModelRows,
                SidecarReadyWorkOrderModelRows: sidecarWorkOrder.ReadyWorkOrderModelRows,
                FreshReadyWorkOrderModelRows: freshWorkOrder.ReadyWorkOrderModelRows,
                SidecarTextureReferenceRows: sidecarWorkOrder.TextureReferenceRows,
                FreshTextureReferenceRows: freshWorkOrder.TextureReferenceRows,
                SidecarReadyTextureReferenceRows: sidecarWorkOrder.ReadyTextureReferenceRows,
                FreshReadyTextureReferenceRows: freshWorkOrder.ReadyTextureReferenceRows,
                SidecarMissingPackageFiles: sidecarWorkOrder.MissingPackageFiles,
                FreshMissingPackageFiles: freshWorkOrder.MissingPackageFiles,
                SidecarUnsafePackagePaths: sidecarWorkOrder.UnsafePackagePaths,
                FreshUnsafePackagePaths: freshWorkOrder.UnsafePackagePaths,
                Completed: completed,
                Issues: issues);
        }

        private static AssetMaterialImportPackageWorkOrderResult Failure(
            AssetMaterialImportPackageInspectionResult inspection,
            string status)
        {
            return new AssetMaterialImportPackageWorkOrderResult(
                PackageRootName: inspection.PackageRootName,
                ManifestRelativePath: inspection.ManifestRelativePath,
                ManifestStatus: status,
                ManifestInspectionCompleted: inspection.Completed,
                ManifestModelGraphRows: inspection.ManifestModelGraphRows,
                ManifestReadyModelGraphRows: inspection.ManifestReadyModelGraphRows,
                WorkOrderModelRows: 0,
                ReadyWorkOrderModelRows: 0,
                TextureReferenceRows: 0,
                ResolvedTextureReferenceRows: 0,
                ReadyTextureReferenceRows: 0,
                MissingPackageFiles: inspection.MissingManifestFiles,
                UnsafePackagePaths: inspection.UnsafeManifestPaths + inspection.UnsafeModelGraphPaths,
                ManifestContainsPackageRoot: inspection.ManifestContainsPackageRoot,
                Completed: false,
                Models: [],
                Issues: inspection.Issues);
        }

        private static AssetMaterialImportPackageWorkOrderModel BuildModel(
            string fullPackageRoot,
            AssetMaterialImportPackageModelOperation model,
            IReadOnlyDictionary<string, AssetMaterialImportPackageMaterializedFile> filesByDestination)
        {
            string modelDestination = NormalizeRelativePath(model.DestinationRelativePath);
            string modelPathStatus = ResolvePackagePathStatus(fullPackageRoot, modelDestination, out string fullModelPath);
            bool modelPackageFileExists = modelPathStatus == "inside-package-root" && File.Exists(fullModelPath);
            string modelFileStatus = LookupFileStatus(filesByDestination, modelDestination);
            IReadOnlyList<AssetMaterialImportPackageWorkOrderTexture> textures = model.TextureReferences
                .OrderBy(static texture => NormalizeRelativePath(texture.DestinationRelativePath), StringComparer.OrdinalIgnoreCase)
                .ThenBy(static texture => texture.BindingFileName, StringComparer.OrdinalIgnoreCase)
                .Select(texture => BuildTexture(fullPackageRoot, texture, filesByDestination))
                .ToList();
            int resolvedTextureReferenceCount = textures.Count(static texture => texture.SourceAvailable);
            int readyTextureReferenceCount = textures.Count(static texture => texture.ReadyForImporter);
            string importReadiness = BuildImportReadiness(model, modelPackageFileExists, textures.Count, readyTextureReferenceCount);

            return new AssetMaterialImportPackageWorkOrderModel(
                Kind: model.Kind,
                CatalogId: model.CatalogId,
                Label: model.Label,
                ExportFileName: Path.GetFileName(model.ExportFileName),
                ModelDestinationRelativePath: modelDestination,
                ReadyForPackage: model.ReadyForPackage,
                PackageStatus: model.PackageStatus,
                ModelFileStatus: modelFileStatus,
                ModelPathStatus: modelPathStatus,
                ModelPackageFileExists: modelPackageFileExists,
                TextureReferenceCount: textures.Count,
                ResolvedTextureReferenceCount: resolvedTextureReferenceCount,
                ReadyTextureReferenceCount: readyTextureReferenceCount,
                FirstTextureDestinationRelativePath: textures.FirstOrDefault(static texture => texture.ReadyForImporter)?.DestinationRelativePath ?? string.Empty,
                ImportReadiness: importReadiness,
                ReadyForImporter: importReadiness == "ready-for-importer",
                Textures: textures);
        }

        private static AssetMaterialImportPackageWorkOrderTexture BuildTexture(
            string fullPackageRoot,
            AssetMaterialImportPackageTextureReference texture,
            IReadOnlyDictionary<string, AssetMaterialImportPackageMaterializedFile> filesByDestination)
        {
            string destination = NormalizeRelativePath(texture.DestinationRelativePath);
            string pathStatus = ResolvePackagePathStatus(fullPackageRoot, destination, out string fullTexturePath);
            bool packageFileExists = texture.SourceAvailable && pathStatus == "inside-package-root" && File.Exists(fullTexturePath);
            string fileStatus = string.IsNullOrWhiteSpace(destination)
                ? "not-in-manifest"
                : LookupFileStatus(filesByDestination, destination);
            string readiness = BuildTextureReadiness(texture, packageFileExists, pathStatus);

            return new AssetMaterialImportPackageWorkOrderTexture(
                BindingFileName: Path.GetFileName(texture.BindingFileName),
                ResolutionKind: texture.ResolutionKind,
                SourceToken: texture.SourceToken,
                SourceFileName: Path.GetFileName(texture.SourceFileName),
                DestinationRelativePath: destination,
                SourceAvailable: texture.SourceAvailable,
                PackageFileStatus: fileStatus,
                PackagePathStatus: pathStatus,
                PackageFileExists: packageFileExists,
                TextureReadiness: readiness,
                ReadyForImporter: readiness == "ready-for-importer");
        }

        private static string BuildImportReadiness(
            AssetMaterialImportPackageModelOperation model,
            bool modelPackageFileExists,
            int textureReferenceCount,
            int readyTextureReferenceCount)
        {
            if (!model.ReadyForPackage)
            {
                return model.PackageStatus;
            }

            if (!modelPackageFileExists)
            {
                return "missing-model-package-file";
            }

            if (textureReferenceCount == 0)
            {
                return "blocked-no-texture-bindings";
            }

            if (readyTextureReferenceCount != textureReferenceCount)
            {
                return "missing-texture-package-file";
            }

            return "ready-for-importer";
        }

        private static string BuildTextureReadiness(
            AssetMaterialImportPackageTextureReference texture,
            bool packageFileExists,
            string packagePathStatus)
        {
            if (!texture.SourceAvailable)
            {
                return string.IsNullOrWhiteSpace(texture.Status) ? "unresolved" : texture.Status;
            }

            if (packagePathStatus == "unsafe-package-path")
            {
                return "unsafe-package-path";
            }

            if (!packageFileExists)
            {
                return "missing-texture-package-file";
            }

            return "ready-for-importer";
        }

        private static string LookupFileStatus(
            IReadOnlyDictionary<string, AssetMaterialImportPackageMaterializedFile> filesByDestination,
            string destinationRelativePath)
        {
            return filesByDestination.TryGetValue(destinationRelativePath, out AssetMaterialImportPackageMaterializedFile? file)
                ? file.Status
                : "not-in-manifest";
        }

        private static string ResolvePackagePathStatus(
            string fullPackageRoot,
            string relativePath,
            out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath))
            {
                return "missing-package-path";
            }

            if (Path.IsPathRooted(relativePath))
            {
                return "unsafe-package-path";
            }

            string candidate = Path.GetFullPath(Path.Combine(fullPackageRoot, relativePath.Replace('/', Path.DirectorySeparatorChar)));
            string root = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            if (!candidate.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            {
                return "unsafe-package-path";
            }

            fullPath = candidate;
            return "inside-package-root";
        }

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }

        private static AssetMaterialImportPackageWorkOrderSidecarValidationResult BuildSidecarValidationFailure(
            string packageRootName,
            string status,
            bool sidecarExists,
            AssetMaterialImportPackageWorkOrderResult freshWorkOrder,
            IReadOnlyList<AssetMaterialImportPackageWorkOrderSidecarValidationIssue> issues,
            long sidecarBytes = 0,
            bool sidecarContainsPackageRoot = false)
        {
            return new AssetMaterialImportPackageWorkOrderSidecarValidationResult(
                PackageRootName: packageRootName,
                SidecarRelativePath: WorkOrderFileName,
                SidecarExists: sidecarExists,
                SidecarStatus: status,
                SidecarBytes: sidecarBytes,
                Schema: string.Empty,
                SchemaValid: false,
                SidecarContainsPackageRoot: sidecarContainsPackageRoot,
                SidecarCompletedFlag: false,
                FreshWorkOrderCompleted: freshWorkOrder.Completed,
                WorkOrderMatchesFreshBuild: false,
                SidecarWorkOrderModelRows: 0,
                FreshWorkOrderModelRows: freshWorkOrder.WorkOrderModelRows,
                SidecarReadyWorkOrderModelRows: 0,
                FreshReadyWorkOrderModelRows: freshWorkOrder.ReadyWorkOrderModelRows,
                SidecarTextureReferenceRows: 0,
                FreshTextureReferenceRows: freshWorkOrder.TextureReferenceRows,
                SidecarReadyTextureReferenceRows: 0,
                FreshReadyTextureReferenceRows: freshWorkOrder.ReadyTextureReferenceRows,
                SidecarMissingPackageFiles: 0,
                FreshMissingPackageFiles: freshWorkOrder.MissingPackageFiles,
                SidecarUnsafePackagePaths: 0,
                FreshUnsafePackagePaths: freshWorkOrder.UnsafePackagePaths,
                Completed: false,
                Issues: issues);
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private static bool WorkOrderPayloadsMatch(
            AssetMaterialImportPackageWorkOrderResult sidecarWorkOrder,
            AssetMaterialImportPackageWorkOrderResult freshWorkOrder)
        {
            return string.Equals(
                JsonSerializer.Serialize(sidecarWorkOrder, WriteJsonOptions),
                JsonSerializer.Serialize(freshWorkOrder, WriteJsonOptions),
                StringComparison.Ordinal);
        }

        private static bool ContainsPathToken(string text, string fullPackageRoot)
        {
            string normalized = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            return text.Contains(normalized, StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace("\\", "\\\\"), StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace('\\', '/'), StringComparison.OrdinalIgnoreCase);
        }
    }

    public sealed record AssetMaterialImportPackageWorkOrderResult(
        string PackageRootName,
        string ManifestRelativePath,
        string ManifestStatus,
        bool ManifestInspectionCompleted,
        int ManifestModelGraphRows,
        int ManifestReadyModelGraphRows,
        int WorkOrderModelRows,
        int ReadyWorkOrderModelRows,
        int TextureReferenceRows,
        int ResolvedTextureReferenceRows,
        int ReadyTextureReferenceRows,
        int MissingPackageFiles,
        int UnsafePackagePaths,
        bool ManifestContainsPackageRoot,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageWorkOrderModel> Models,
        IReadOnlyList<AssetMaterialImportPackageInspectionIssue> Issues);

    public sealed record AssetMaterialImportPackageWorkOrderSidecar(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        AssetMaterialImportPackageWorkOrderResult MaterialPackageWorkOrder);

    public sealed record AssetMaterialImportPackageWorkOrderSidecarWriteResult(
        string SidecarRelativePath,
        bool SidecarWritten,
        string SidecarStatus,
        long SidecarBytes,
        AssetMaterialImportPackageWorkOrderResult WorkOrder);

    public sealed record AssetMaterialImportPackageWorkOrderSidecarValidationResult(
        string PackageRootName,
        string SidecarRelativePath,
        bool SidecarExists,
        string SidecarStatus,
        long SidecarBytes,
        string Schema,
        bool SchemaValid,
        bool SidecarContainsPackageRoot,
        bool SidecarCompletedFlag,
        bool FreshWorkOrderCompleted,
        bool WorkOrderMatchesFreshBuild,
        int SidecarWorkOrderModelRows,
        int FreshWorkOrderModelRows,
        int SidecarReadyWorkOrderModelRows,
        int FreshReadyWorkOrderModelRows,
        int SidecarTextureReferenceRows,
        int FreshTextureReferenceRows,
        int SidecarReadyTextureReferenceRows,
        int FreshReadyTextureReferenceRows,
        int SidecarMissingPackageFiles,
        int FreshMissingPackageFiles,
        int SidecarUnsafePackagePaths,
        int FreshUnsafePackagePaths,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageWorkOrderSidecarValidationIssue> Issues);

    public sealed record AssetMaterialImportPackageWorkOrderSidecarValidationIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageWorkOrderModel(
        string Kind,
        string CatalogId,
        string Label,
        string ExportFileName,
        string ModelDestinationRelativePath,
        bool ReadyForPackage,
        string PackageStatus,
        string ModelFileStatus,
        string ModelPathStatus,
        bool ModelPackageFileExists,
        int TextureReferenceCount,
        int ResolvedTextureReferenceCount,
        int ReadyTextureReferenceCount,
        string FirstTextureDestinationRelativePath,
        string ImportReadiness,
        bool ReadyForImporter,
        IReadOnlyList<AssetMaterialImportPackageWorkOrderTexture> Textures);

    public sealed record AssetMaterialImportPackageWorkOrderTexture(
        string BindingFileName,
        string ResolutionKind,
        string SourceToken,
        string SourceFileName,
        string DestinationRelativePath,
        bool SourceAvailable,
        string PackageFileStatus,
        string PackagePathStatus,
        bool PackageFileExists,
        string TextureReadiness,
        bool ReadyForImporter);
}
