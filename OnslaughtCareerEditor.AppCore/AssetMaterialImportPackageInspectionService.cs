using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageInspectionService
    {
        private static readonly JsonSerializerOptions JsonOptions = new()
        {
            PropertyNameCaseInsensitive = true
        };

        public AssetMaterialImportPackageInspectionResult Inspect(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string rootName = BuildRootName(fullPackageRoot);
            string manifestPath = Path.Combine(fullPackageRoot, AssetMaterialImportPackageMaterializationService.ManifestFileName);

            if (!Directory.Exists(fullPackageRoot))
            {
                return Failure(rootName, "missing-package-root", manifestExists: false);
            }

            if (!File.Exists(manifestPath))
            {
                return Failure(rootName, "missing-manifest", manifestExists: false);
            }

            string manifestJson = File.ReadAllText(manifestPath);
            bool manifestContainsPackageRoot = ContainsPathToken(manifestJson, fullPackageRoot);
            AssetMaterialImportPackageOutputManifest? manifest;
            try
            {
                manifest = JsonSerializer.Deserialize<AssetMaterialImportPackageOutputManifest>(manifestJson, JsonOptions);
            }
            catch (JsonException)
            {
                return Failure(
                    rootName,
                    "invalid-json",
                    manifestExists: true,
                    manifestBytes: new FileInfo(manifestPath).Length,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    issues: [new AssetMaterialImportPackageInspectionIssue("manifest", AssetMaterialImportPackageMaterializationService.ManifestFileName, "invalid-json")]);
            }

            if (manifest is null)
            {
                return Failure(
                    rootName,
                    "empty-manifest",
                    manifestExists: true,
                    manifestBytes: new FileInfo(manifestPath).Length,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    issues: [new AssetMaterialImportPackageInspectionIssue("manifest", AssetMaterialImportPackageMaterializationService.ManifestFileName, "empty-manifest")]);
            }

            IReadOnlyList<AssetMaterialImportPackageModelOperation> modelRows =
                manifest.Models ?? Array.Empty<AssetMaterialImportPackageModelOperation>();
            HashSet<string> manifestPaths = new(StringComparer.OrdinalIgnoreCase);
            List<AssetMaterialImportPackageInspectionIssue> issues = new();
            int existingManifestFiles = 0;
            int missingManifestFiles = 0;
            int unsafeManifestPaths = 0;
            int unsafeModelGraphPaths = 0;

            foreach (AssetMaterialImportPackageMaterializedFile file in manifest.Files)
            {
                string relativePath = NormalizeRelativePath(file.DestinationRelativePath);
                if (!TryResolveInsideRoot(fullPackageRoot, relativePath, out string fullPath))
                {
                    unsafeManifestPaths++;
                    issues.Add(new AssetMaterialImportPackageInspectionIssue(file.Role, relativePath, "unsafe-manifest-path"));
                    continue;
                }

                manifestPaths.Add(relativePath);
                if (File.Exists(fullPath))
                {
                    existingManifestFiles++;
                }
                else
                {
                    missingManifestFiles++;
                    issues.Add(new AssetMaterialImportPackageInspectionIssue(file.Role, relativePath, "missing-payload-file"));
                }
            }

            foreach (AssetMaterialImportPackageModelOperation model in modelRows)
            {
                if (model.ReadyForPackage &&
                    !string.IsNullOrWhiteSpace(model.DestinationRelativePath) &&
                    !TryResolveInsideRoot(fullPackageRoot, NormalizeRelativePath(model.DestinationRelativePath), out _))
                {
                    unsafeModelGraphPaths++;
                    issues.Add(new AssetMaterialImportPackageInspectionIssue("model", model.DestinationRelativePath, "unsafe-model-graph-path"));
                }

                foreach (AssetMaterialImportPackageTextureReference texture in model.TextureReferences ?? [])
                {
                    if (texture.SourceAvailable &&
                        !string.IsNullOrWhiteSpace(texture.DestinationRelativePath) &&
                        !TryResolveInsideRoot(fullPackageRoot, NormalizeRelativePath(texture.DestinationRelativePath), out _))
                    {
                        unsafeModelGraphPaths++;
                        issues.Add(new AssetMaterialImportPackageInspectionIssue("texture", texture.DestinationRelativePath, "unsafe-model-graph-path"));
                    }
                }
            }

            IReadOnlyList<string> payloadFiles = Directory
                .EnumerateFiles(fullPackageRoot, "*", SearchOption.AllDirectories)
                .Select(path => NormalizeRelativePath(Path.GetRelativePath(fullPackageRoot, path)))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageMaterializationService.ManifestFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageWorkOrderService.WorkOrderFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageImporterDryRunService.DryRunFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageRebuildPreviewService.ManifestFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageRebuildSceneService.ManifestFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageRebuildMeshService.ManifestFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !string.Equals(path, AssetMaterialImportPackageRebuildMeshImportService.ManifestFileName, StringComparison.OrdinalIgnoreCase))
                .Where(static path => !path.StartsWith(AssetMaterialImportPackageImporterInputService.ImporterInputRootRelativePath + "/", StringComparison.OrdinalIgnoreCase))
                .Where(static path => !path.StartsWith(AssetMaterialImportPackageRebuildPreviewService.WorkspaceRootRelativePath + "/", StringComparison.OrdinalIgnoreCase))
                .Where(static path => !path.StartsWith(AssetMaterialImportPackageRebuildSceneService.WorkspaceRootRelativePath + "/", StringComparison.OrdinalIgnoreCase))
                .Where(static path => !path.StartsWith(AssetMaterialImportPackageRebuildMeshService.WorkspaceRootRelativePath + "/", StringComparison.OrdinalIgnoreCase))
                .ToList();
            List<string> extraPayloadFiles = payloadFiles
                .Where(path => !manifestPaths.Contains(path))
                .OrderBy(static path => path, StringComparer.OrdinalIgnoreCase)
                .ToList();
            foreach (string extraPayloadFile in extraPayloadFiles.Take(100))
            {
                issues.Add(new AssetMaterialImportPackageInspectionIssue("payload", extraPayloadFile, "extra-payload-file"));
            }

            bool schemaValid = string.Equals(manifest.Schema, AssetMaterialImportPackageMaterializationService.ManifestSchema, StringComparison.Ordinal);
            bool rowCountsValid =
                manifest.TotalPackageFiles == manifest.Files.Count &&
                manifest.PlannedFiles == manifest.Files.Count;
            bool completed =
                schemaValid &&
                rowCountsValid &&
                manifest.Completed &&
                !manifestContainsPackageRoot &&
                unsafeManifestPaths == 0 &&
                unsafeModelGraphPaths == 0 &&
                missingManifestFiles == 0 &&
                extraPayloadFiles.Count == 0;
            string status = completed
                ? "ok"
                : schemaValid
                    ? "issues-found"
                    : "invalid-schema";

            return new AssetMaterialImportPackageInspectionResult(
                PackageRootName: rootName,
                ManifestRelativePath: AssetMaterialImportPackageMaterializationService.ManifestFileName,
                ManifestExists: true,
                ManifestStatus: status,
                ManifestBytes: new FileInfo(manifestPath).Length,
                Schema: manifest.Schema,
                SchemaValid: schemaValid,
                ManifestCompletedFlag: manifest.Completed,
                ManifestContainsPackageRoot: manifestContainsPackageRoot,
                DeclaredTotalPackageFiles: manifest.TotalPackageFiles,
                DeclaredPlannedFiles: manifest.PlannedFiles,
                ManifestFileRows: manifest.Files.Count,
                ManifestModelFileRows: manifest.Files.Count(static file => string.Equals(file.Role, "model", StringComparison.OrdinalIgnoreCase)),
                ManifestTextureFileRows: manifest.Files.Count(static file => string.Equals(file.Role, "texture", StringComparison.OrdinalIgnoreCase)),
                ManifestModelGraphRows: modelRows.Count,
                ManifestReadyModelGraphRows: modelRows.Count(static model => model.ReadyForPackage),
                ManifestTextureReferenceRows: modelRows.Sum(static model => model.TextureReferences?.Count ?? 0),
                ManifestResolvedTextureReferenceRows: modelRows.Sum(static model =>
                    model.TextureReferences?.Count(static texture => texture.SourceAvailable) ?? 0),
                ExistingManifestFiles: existingManifestFiles,
                MissingManifestFiles: missingManifestFiles,
                ExtraPayloadFiles: extraPayloadFiles.Count,
                UnsafeManifestPaths: unsafeManifestPaths,
                UnsafeModelGraphPaths: unsafeModelGraphPaths,
                Completed: completed,
                Issues: issues);
        }

        private static AssetMaterialImportPackageInspectionResult Failure(
            string packageRootName,
            string status,
            bool manifestExists,
            long manifestBytes = 0,
            bool manifestContainsPackageRoot = false,
            IReadOnlyList<AssetMaterialImportPackageInspectionIssue>? issues = null)
        {
            return new AssetMaterialImportPackageInspectionResult(
                PackageRootName: packageRootName,
                ManifestRelativePath: AssetMaterialImportPackageMaterializationService.ManifestFileName,
                ManifestExists: manifestExists,
                ManifestStatus: status,
                ManifestBytes: manifestBytes,
                Schema: string.Empty,
                SchemaValid: false,
                ManifestCompletedFlag: false,
                ManifestContainsPackageRoot: manifestContainsPackageRoot,
                DeclaredTotalPackageFiles: 0,
                DeclaredPlannedFiles: 0,
                ManifestFileRows: 0,
                ManifestModelFileRows: 0,
                ManifestTextureFileRows: 0,
                ManifestModelGraphRows: 0,
                ManifestReadyModelGraphRows: 0,
                ManifestTextureReferenceRows: 0,
                ManifestResolvedTextureReferenceRows: 0,
                ExistingManifestFiles: 0,
                MissingManifestFiles: 0,
                ExtraPayloadFiles: 0,
                UnsafeManifestPaths: 0,
                UnsafeModelGraphPaths: 0,
                Completed: false,
                Issues: issues ?? []);
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private static string NormalizeRelativePath(string path)
        {
            return path.Replace('\\', '/');
        }

        private static bool TryResolveInsideRoot(string fullPackageRoot, string relativePath, out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathRooted(relativePath))
            {
                return false;
            }

            string candidate = Path.GetFullPath(Path.Combine(fullPackageRoot, relativePath.Replace('/', Path.DirectorySeparatorChar)));
            string root = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            if (!candidate.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            fullPath = candidate;
            return true;
        }

        private static bool ContainsPathToken(string text, string fullPackageRoot)
        {
            string normalized = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            return text.Contains(normalized, StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace("\\", "\\\\"), StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace('\\', '/'), StringComparison.OrdinalIgnoreCase);
        }
    }

    public sealed record AssetMaterialImportPackageInspectionResult(
        string PackageRootName,
        string ManifestRelativePath,
        bool ManifestExists,
        string ManifestStatus,
        long ManifestBytes,
        string Schema,
        bool SchemaValid,
        bool ManifestCompletedFlag,
        bool ManifestContainsPackageRoot,
        int DeclaredTotalPackageFiles,
        int DeclaredPlannedFiles,
        int ManifestFileRows,
        int ManifestModelFileRows,
        int ManifestTextureFileRows,
        int ManifestModelGraphRows,
        int ManifestReadyModelGraphRows,
        int ManifestTextureReferenceRows,
        int ManifestResolvedTextureReferenceRows,
        int ExistingManifestFiles,
        int MissingManifestFiles,
        int ExtraPayloadFiles,
        int UnsafeManifestPaths,
        int UnsafeModelGraphPaths,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageInspectionIssue> Issues);

    public sealed record AssetMaterialImportPackageInspectionIssue(
        string Role,
        string DestinationRelativePath,
        string Status);
}
