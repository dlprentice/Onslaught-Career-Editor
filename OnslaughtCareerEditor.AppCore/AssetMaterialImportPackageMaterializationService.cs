using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageMaterializationService
    {
        public const string ManifestFileName = "material-package-manifest.v1.json";
        public const string ManifestSchema = "onslaught.asset-material-package-manifest.v1";

        public AssetMaterialImportPackageMaterializationResult Preflight(
            AssetCatalogSnapshot snapshot,
            string outputRoot)
        {
            return Build(snapshot, outputRoot, executeCopy: false);
        }

        public AssetMaterialImportPackageMaterializationResult Materialize(
            AssetCatalogSnapshot snapshot,
            string outputRoot)
        {
            return Build(snapshot, outputRoot, executeCopy: true);
        }

        private static AssetMaterialImportPackageMaterializationResult Build(
            AssetCatalogSnapshot snapshot,
            string outputRoot,
            bool executeCopy)
        {
            if (string.IsNullOrWhiteSpace(outputRoot))
            {
                throw new ArgumentException("Output root is required.", nameof(outputRoot));
            }

            string fullOutputRoot = Path.GetFullPath(outputRoot);

            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);
            AssetMaterialImportPackagePlan packagePlan = new AssetMaterialImportPackagePlanService().Build(manifest);
            SourceIndex sourceIndex = SourceIndex.Build(snapshot);
            List<AssetMaterialImportPackageMaterializedFile> files = new();
            HashSet<string> packageDestinations = new(StringComparer.OrdinalIgnoreCase);

            foreach (AssetMaterialImportPackageModelOperation operation in packagePlan.ModelOperations)
            {
                if (!operation.ReadyForPackage)
                {
                    continue;
                }

                MaterializeModel(operation, sourceIndex, fullOutputRoot, executeCopy, packageDestinations, files);
                MaterializeTextures(operation, sourceIndex, fullOutputRoot, executeCopy, packageDestinations, files);
            }

            bool completed = files.Count(static file =>
                file.Status is "missing-source" or "blocked-unsafe-destination") == 0 &&
                packagePlan.BlockedPackageModelOperations == 0 &&
                packagePlan.UnresolvedTextureReferences == 0;
            (bool manifestWritten, string manifestStatus, long manifestBytes) = WriteManifestIfRequested(
                executeCopy,
                fullOutputRoot,
                packagePlan,
                files,
                completed);
            (bool workOrderSidecarWritten, string workOrderSidecarStatus, long workOrderSidecarBytes) =
                WriteWorkOrderSidecarIfRequested(executeCopy, fullOutputRoot, manifestWritten);
            (bool importerDryRunSidecarWritten, string importerDryRunSidecarStatus, long importerDryRunSidecarBytes) =
                WriteImporterDryRunSidecarIfRequested(executeCopy, fullOutputRoot, workOrderSidecarWritten);

            return new AssetMaterialImportPackageMaterializationResult(
                Executed: executeCopy,
                TotalPackageFiles: packagePlan.TotalPackageFiles,
                PlannedFiles: files.Count,
                WouldCopyFiles: files.Count(static file => file.Status == "would-copy"),
                CopiedFiles: files.Count(static file => file.Status == "copied"),
                ExistingFilesSkipped: files.Count(static file => file.Status == "skipped-existing"),
                ExistingFilesDetected: files.Count(static file => file.Status is "skipped-existing" or "would-skip-existing"),
                MissingSourceFiles: files.Count(static file => file.Status == "missing-source"),
                UnsafeDestinationFiles: files.Count(static file => file.Status == "blocked-unsafe-destination"),
                ModelFilesReady: files.Count(static file => file.Role == "model" && file.Status is "would-copy" or "copied" or "would-skip-existing" or "skipped-existing"),
                TextureFilesReady: files.Count(static file => file.Role == "texture" && file.Status is "would-copy" or "copied" or "would-skip-existing" or "skipped-existing"),
                ModelFilesCopied: files.Count(static file => file.Role == "model" && file.Status == "copied"),
                TextureFilesCopied: files.Count(static file => file.Role == "texture" && file.Status == "copied"),
                BlockedPackageModelOperations: packagePlan.BlockedPackageModelOperations,
                UnresolvedTextureReferences: packagePlan.UnresolvedTextureReferences,
                ManifestRelativePath: ManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                WorkOrderSidecarRelativePath: AssetMaterialImportPackageWorkOrderService.WorkOrderFileName,
                WorkOrderSidecarWritten: workOrderSidecarWritten,
                WorkOrderSidecarStatus: workOrderSidecarStatus,
                WorkOrderSidecarBytes: workOrderSidecarBytes,
                ImporterDryRunSidecarRelativePath: AssetMaterialImportPackageImporterDryRunService.DryRunFileName,
                ImporterDryRunSidecarWritten: importerDryRunSidecarWritten,
                ImporterDryRunSidecarStatus: importerDryRunSidecarStatus,
                ImporterDryRunSidecarBytes: importerDryRunSidecarBytes,
                Completed: completed,
                Files: files
                    .OrderBy(static file => file.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ToList());
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeCopy,
            string fullOutputRoot,
            AssetMaterialImportPackagePlan packagePlan,
            IReadOnlyList<AssetMaterialImportPackageMaterializedFile> files,
            bool completed)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            Directory.CreateDirectory(fullOutputRoot);
            string manifestPath = Path.Combine(fullOutputRoot, ManifestFileName);
            AssetMaterialImportPackageOutputManifest manifest = new(
                Schema: ManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                TotalPackageFiles: packagePlan.TotalPackageFiles,
                PlannedFiles: files.Count,
                ModelPackageFiles: packagePlan.ModelPackageFiles,
                TexturePackageFiles: packagePlan.TexturePackageFiles,
                BlockedPackageModelOperations: packagePlan.BlockedPackageModelOperations,
                UnresolvedTextureReferences: packagePlan.UnresolvedTextureReferences,
                Completed: completed,
                Models: packagePlan.ModelOperations
                    .OrderBy(static model => model.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ThenBy(static model => model.CatalogId, StringComparer.OrdinalIgnoreCase)
                    .ToList(),
                Files: files
                    .OrderBy(static file => file.DestinationRelativePath, StringComparer.OrdinalIgnoreCase)
                    .ToList());
            JsonSerializerOptions options = new(JsonSerializerDefaults.Web)
            {
                WriteIndented = true
            };
            File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, options));
            return (true, "written", new FileInfo(manifestPath).Length);
        }

        private static (bool Written, string Status, long Bytes) WriteWorkOrderSidecarIfRequested(
            bool executeCopy,
            string fullOutputRoot,
            bool manifestWritten)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            if (!manifestWritten)
            {
                return (false, "manifest-not-written", 0);
            }

            AssetMaterialImportPackageWorkOrderSidecarWriteResult result =
                new AssetMaterialImportPackageWorkOrderService().WriteSidecar(fullOutputRoot);
            return (result.SidecarWritten, result.SidecarStatus, result.SidecarBytes);
        }

        private static (bool Written, string Status, long Bytes) WriteImporterDryRunSidecarIfRequested(
            bool executeCopy,
            string fullOutputRoot,
            bool workOrderSidecarWritten)
        {
            if (!executeCopy)
            {
                return (false, "preflight-not-written", 0);
            }

            if (!workOrderSidecarWritten)
            {
                return (false, "work-order-sidecar-not-written", 0);
            }

            AssetMaterialImportPackageImporterDryRunSidecarWriteResult result =
                new AssetMaterialImportPackageImporterDryRunService().WriteSidecar(fullOutputRoot);
            return (result.SidecarWritten, result.SidecarStatus, result.SidecarBytes);
        }

        private static void MaterializeModel(
            AssetMaterialImportPackageModelOperation operation,
            SourceIndex sourceIndex,
            string fullOutputRoot,
            bool executeCopy,
            HashSet<string> packageDestinations,
            List<AssetMaterialImportPackageMaterializedFile> files)
        {
            if (!packageDestinations.Add(operation.DestinationRelativePath))
            {
                return;
            }

            string sourcePath = sourceIndex.FindModelSource(operation);
            files.Add(PlanOrCopyPackageFile(
                role: "model",
                sourcePath,
                operation.DestinationRelativePath,
                operation.ExportFileName,
                operation.CatalogId,
                resolutionKind: "model-export",
                fullOutputRoot,
                executeCopy));
        }

        private static void MaterializeTextures(
            AssetMaterialImportPackageModelOperation operation,
            SourceIndex sourceIndex,
            string fullOutputRoot,
            bool executeCopy,
            HashSet<string> packageDestinations,
            List<AssetMaterialImportPackageMaterializedFile> files)
        {
            foreach (AssetMaterialImportPackageTextureReference texture in operation.TextureReferences)
            {
                if (!texture.SourceAvailable ||
                    string.IsNullOrWhiteSpace(texture.DestinationRelativePath) ||
                    !packageDestinations.Add(texture.DestinationRelativePath))
                {
                    continue;
                }

                string sourcePath = sourceIndex.FindTextureSource(operation, texture);
                files.Add(PlanOrCopyPackageFile(
                    role: "texture",
                    sourcePath,
                    texture.DestinationRelativePath,
                    texture.SourceFileName,
                    texture.SourceToken,
                    texture.ResolutionKind,
                    fullOutputRoot,
                    executeCopy));
            }
        }

        private static AssetMaterialImportPackageMaterializedFile PlanOrCopyPackageFile(
            string role,
            string sourcePath,
            string destinationRelativePath,
            string sourceFileName,
            string sourceToken,
            string resolutionKind,
            string fullOutputRoot,
            bool executeCopy)
        {
            if (!IsSafeRelativePath(destinationRelativePath, fullOutputRoot, out string fullDestinationPath))
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    "blocked-unsafe-destination",
                    0);
            }

            if (string.IsNullOrWhiteSpace(sourcePath) || !File.Exists(sourcePath))
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    "missing-source",
                    0);
            }

            if (File.Exists(fullDestinationPath))
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    executeCopy ? "skipped-existing" : "would-skip-existing",
                    new FileInfo(fullDestinationPath).Length);
            }

            if (!executeCopy)
            {
                return BuildFile(
                    role,
                    destinationRelativePath,
                    sourceFileName,
                    sourceToken,
                    resolutionKind,
                    "would-copy",
                    0);
            }

            Directory.CreateDirectory(Path.GetDirectoryName(fullDestinationPath)!);
            File.Copy(sourcePath, fullDestinationPath, overwrite: false);
            return BuildFile(
                role,
                destinationRelativePath,
                sourceFileName,
                sourceToken,
                resolutionKind,
                "copied",
                new FileInfo(fullDestinationPath).Length);
        }

        private static AssetMaterialImportPackageMaterializedFile BuildFile(
            string role,
            string destinationRelativePath,
            string sourceFileName,
            string sourceToken,
            string resolutionKind,
            string status,
            long outputBytes)
        {
            return new AssetMaterialImportPackageMaterializedFile(
                Role: role,
                DestinationRelativePath: NormalizeRelativePath(destinationRelativePath),
                SourceFileName: Path.GetFileName(sourceFileName),
                SourceToken: sourceToken,
                ResolutionKind: resolutionKind,
                Status: status,
                OutputBytes: outputBytes);
        }

        private static bool IsSafeRelativePath(
            string destinationRelativePath,
            string fullOutputRoot,
            out string fullDestinationPath)
        {
            fullDestinationPath = string.Empty;
            if (string.IsNullOrWhiteSpace(destinationRelativePath) ||
                Path.IsPathRooted(destinationRelativePath))
            {
                return false;
            }

            string normalized = destinationRelativePath
                .Replace('/', Path.DirectorySeparatorChar)
                .Replace('\\', Path.DirectorySeparatorChar);
            string candidate = Path.GetFullPath(Path.Combine(fullOutputRoot, normalized));
            string root = fullOutputRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) +
                Path.DirectorySeparatorChar;
            if (!candidate.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            fullDestinationPath = candidate;
            return true;
        }

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }

        private sealed class SourceIndex
        {
            private readonly IReadOnlyDictionary<string, AssetLooseMeshItem> _looseMeshesByCatalogId;
            private readonly IReadOnlyDictionary<string, AssetEmbeddedMeshItem> _embeddedMeshesByCatalogId;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesByCatalogId;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesByFileName;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesBySanitizedCatalogId;
            private readonly IReadOnlyDictionary<string, AssetTextureItem> _texturesBySanitizedFileName;
            private readonly AssetModelTextureLinkService _textureLinkService = new();

            private SourceIndex(
                IReadOnlyDictionary<string, AssetLooseMeshItem> looseMeshesByCatalogId,
                IReadOnlyDictionary<string, AssetEmbeddedMeshItem> embeddedMeshesByCatalogId,
                IReadOnlyDictionary<string, AssetTextureItem> texturesByCatalogId,
                IReadOnlyDictionary<string, AssetTextureItem> texturesByFileName,
                IReadOnlyDictionary<string, AssetTextureItem> texturesBySanitizedCatalogId,
                IReadOnlyDictionary<string, AssetTextureItem> texturesBySanitizedFileName)
            {
                _looseMeshesByCatalogId = looseMeshesByCatalogId;
                _embeddedMeshesByCatalogId = embeddedMeshesByCatalogId;
                _texturesByCatalogId = texturesByCatalogId;
                _texturesByFileName = texturesByFileName;
                _texturesBySanitizedCatalogId = texturesBySanitizedCatalogId;
                _texturesBySanitizedFileName = texturesBySanitizedFileName;
            }

            public static SourceIndex Build(AssetCatalogSnapshot snapshot)
            {
                return new SourceIndex(
                    snapshot.LooseMeshes
                        .Where(static mesh => !string.IsNullOrWhiteSpace(mesh.CatalogId))
                        .GroupBy(static mesh => mesh.CatalogId, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.EmbeddedMeshes
                        .Where(static mesh => !string.IsNullOrWhiteSpace(mesh.CatalogId))
                        .GroupBy(static mesh => mesh.CatalogId, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Where(static texture => !string.IsNullOrWhiteSpace(texture.CatalogId))
                        .GroupBy(static texture => texture.CatalogId, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Where(static texture => !string.IsNullOrWhiteSpace(texture.ExportFileName))
                        .GroupBy(static texture => texture.ExportFileName, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Select(static texture => new { Key = SanitizeToken(texture.CatalogId), Texture = texture })
                        .Where(static row => !string.IsNullOrWhiteSpace(row.Key))
                        .GroupBy(static row => row.Key, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First().Texture, StringComparer.OrdinalIgnoreCase),
                    snapshot.Textures
                        .Select(static texture => new { Key = SanitizeToken(texture.ExportFileName), Texture = texture })
                        .Where(static row => !string.IsNullOrWhiteSpace(row.Key))
                        .GroupBy(static row => row.Key, StringComparer.OrdinalIgnoreCase)
                        .ToDictionary(static group => group.Key, static group => group.First().Texture, StringComparer.OrdinalIgnoreCase));
            }

            public string FindModelSource(AssetMaterialImportPackageModelOperation operation)
            {
                if (operation.Kind.Equals("loose mesh", StringComparison.OrdinalIgnoreCase) &&
                    _looseMeshesByCatalogId.TryGetValue(operation.CatalogId, out AssetLooseMeshItem? looseMesh))
                {
                    return looseMesh.ExportPath;
                }

                if (operation.Kind.Equals("embedded mesh", StringComparison.OrdinalIgnoreCase) &&
                    _embeddedMeshesByCatalogId.TryGetValue(operation.CatalogId, out AssetEmbeddedMeshItem? embeddedMesh))
                {
                    return embeddedMesh.ExportPath;
                }

                return string.Empty;
            }

            public string FindTextureSource(
                AssetMaterialImportPackageModelOperation operation,
                AssetMaterialImportPackageTextureReference texture)
            {
                if (texture.ResolutionKind.Equals("catalog", StringComparison.OrdinalIgnoreCase))
                {
                    if (_texturesByCatalogId.TryGetValue(texture.SourceToken, out AssetTextureItem? byCatalogId))
                    {
                        return byCatalogId.ExportPath;
                    }

                    if (_texturesBySanitizedCatalogId.TryGetValue(texture.SourceToken, out AssetTextureItem? bySanitizedCatalogId))
                    {
                        return bySanitizedCatalogId.ExportPath;
                    }

                    if (_texturesByFileName.TryGetValue(texture.SourceFileName, out AssetTextureItem? byFileName))
                    {
                        return byFileName.ExportPath;
                    }

                    if (_texturesBySanitizedFileName.TryGetValue(texture.SourceFileName, out AssetTextureItem? bySanitizedFileName))
                    {
                        return bySanitizedFileName.ExportPath;
                    }

                    return string.Empty;
                }

                if (!texture.ResolutionKind.Equals("sidecar", StringComparison.OrdinalIgnoreCase))
                {
                    return string.Empty;
                }

                string modelSource = FindModelSource(operation);
                IReadOnlyList<AssetModelSidecarTexture> sidecars =
                    _textureLinkService.ResolveSidecarTextures(modelSource, [texture.BindingFileName]);
                return sidecars.FirstOrDefault(sidecar =>
                        sidecar.FileName.Equals(texture.SourceFileName, StringComparison.OrdinalIgnoreCase) ||
                        SanitizeToken(sidecar.FileName).Equals(texture.SourceFileName, StringComparison.OrdinalIgnoreCase))
                    ?.ExportPath ?? string.Empty;
            }

            private static string SanitizeToken(string value)
            {
                if (string.IsNullOrWhiteSpace(value))
                {
                    return string.Empty;
                }

                char[] chars = value.Trim().Select(static ch =>
                    char.IsLetterOrDigit(ch) || ch is '.' or '-' or '_' ? ch : '_').ToArray();
                string result = new string(chars).Trim('_');
                while (result.Contains("__", StringComparison.Ordinal))
                {
                    result = result.Replace("__", "_", StringComparison.Ordinal);
                }

                return result;
            }
        }
    }

    public sealed record AssetMaterialImportPackageMaterializationResult(
        bool Executed,
        int TotalPackageFiles,
        int PlannedFiles,
        int WouldCopyFiles,
        int CopiedFiles,
        int ExistingFilesSkipped,
        int ExistingFilesDetected,
        int MissingSourceFiles,
        int UnsafeDestinationFiles,
        int ModelFilesReady,
        int TextureFilesReady,
        int ModelFilesCopied,
        int TextureFilesCopied,
        int BlockedPackageModelOperations,
        int UnresolvedTextureReferences,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        string WorkOrderSidecarRelativePath,
        bool WorkOrderSidecarWritten,
        string WorkOrderSidecarStatus,
        long WorkOrderSidecarBytes,
        string ImporterDryRunSidecarRelativePath,
        bool ImporterDryRunSidecarWritten,
        string ImporterDryRunSidecarStatus,
        long ImporterDryRunSidecarBytes,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageMaterializedFile> Files);

    public sealed record AssetMaterialImportPackageMaterializedFile(
        string Role,
        string DestinationRelativePath,
        string SourceFileName,
        string SourceToken,
        string ResolutionKind,
        string Status,
        long OutputBytes);

    public sealed record AssetMaterialImportPackageOutputManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        int TotalPackageFiles,
        int PlannedFiles,
        int ModelPackageFiles,
        int TexturePackageFiles,
        int BlockedPackageModelOperations,
        int UnresolvedTextureReferences,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageModelOperation> Models,
        IReadOnlyList<AssetMaterialImportPackageMaterializedFile> Files);
}
