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

            if (!Directory.Exists(fullPackageRoot))
            {
                return Failure(rootName, "missing-package-root", manifestExists: false);
            }

            GuardedPackageOutputRoot? packageSafety = null;
            try
            {
                packageSafety = new GuardedPackageOutputRoot(
                    fullPackageRoot,
                    trustedSourceRoot: null,
                    execute: false);
                string manifestPath = packageSafety.ResolveDestination(
                    AssetMaterialImportPackageMaterializationService.ManifestFileName,
                    createDirectories: false);
                FileStream? manifestStream = packageSafety.HoldExistingFile(manifestPath);
                if (manifestStream is null)
                {
                    return Failure(rootName, "missing-manifest", manifestExists: false);
                }

                const long maxManifestBytes = 64L * 1024 * 1024;
                if (manifestStream.Length > maxManifestBytes)
                {
                    return Failure(
                        rootName,
                        "manifest-too-large",
                        manifestExists: true,
                        manifestBytes: manifestStream.Length,
                        issues: [new AssetMaterialImportPackageInspectionIssue(
                            "manifest",
                            AssetMaterialImportPackageMaterializationService.ManifestFileName,
                            "manifest-too-large")]);
                }

            manifestStream.Position = 0;
            using var manifestReader = new StreamReader(
                manifestStream,
                System.Text.Encoding.UTF8,
                detectEncodingFromByteOrderMarks: true,
                leaveOpen: true);
            string manifestJson = manifestReader.ReadToEnd();
            long manifestBytes = manifestStream.Length;
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
                    manifestBytes: manifestBytes,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    issues: [new AssetMaterialImportPackageInspectionIssue("manifest", AssetMaterialImportPackageMaterializationService.ManifestFileName, "invalid-json")]);
            }

            if (manifest is null)
            {
                return Failure(
                    rootName,
                    "empty-manifest",
                    manifestExists: true,
                    manifestBytes: manifestBytes,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    issues: [new AssetMaterialImportPackageInspectionIssue("manifest", AssetMaterialImportPackageMaterializationService.ManifestFileName, "empty-manifest")]);
            }

            if (manifest.Files is null || manifest.Models is null ||
                manifest.Files.Count > 100_000 || manifest.Models.Count > 100_000 ||
                manifest.Files.Any(static file => file is null) ||
                manifest.Models.Any(static model => model is null) ||
                manifest.Models.Any(static model =>
                    model.TextureReferences is null ||
                    model.TextureReferences.Any(static texture => texture is null)))
            {
                return Failure(
                    rootName,
                    "invalid-structure",
                    manifestExists: true,
                    manifestBytes: manifestBytes,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    issues: [new AssetMaterialImportPackageInspectionIssue("manifest", AssetMaterialImportPackageMaterializationService.ManifestFileName, "invalid-structure")]);
            }

            IReadOnlyList<AssetMaterialImportPackageMaterializedFile> fileRows = manifest.Files;
            IReadOnlyList<AssetMaterialImportPackageModelOperation> modelRows = manifest.Models;
            HashSet<string> manifestPaths = new(StringComparer.OrdinalIgnoreCase);
            HashSet<string> manifestFullPaths = new(FileMutationSafety.PathComparer);
            List<AssetMaterialImportPackageInspectionIssue> issues = new();
            int existingManifestFiles = 0;
            int missingManifestFiles = 0;
            int unsafeManifestPaths = 0;
            int unsafeModelGraphPaths = 0;
            int duplicateManifestPaths = 0;

            foreach (AssetMaterialImportPackageMaterializedFile file in fileRows)
            {
                string relativePath = NormalizeRelativePath(file.DestinationRelativePath);
                if (!TryResolveInsideRoot(fullPackageRoot, relativePath, out string fullPath))
                {
                    unsafeManifestPaths++;
                    issues.Add(new AssetMaterialImportPackageInspectionIssue(file.Role, relativePath, "unsafe-manifest-path"));
                    continue;
                }

                string canonicalRelativePath = NormalizeRelativePath(
                    Path.GetRelativePath(fullPackageRoot, fullPath));
                if (!manifestFullPaths.Add(fullPath))
                {
                    duplicateManifestPaths++;
                    issues.Add(new AssetMaterialImportPackageInspectionIssue(file.Role, relativePath, "duplicate-manifest-path"));
                    continue;
                }
                manifestPaths.Add(canonicalRelativePath);
                if (packageSafety.HoldExistingFile(fullPath) is not null)
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
                .EnumerateFiles(
                    fullPackageRoot,
                    "*",
                    new EnumerationOptions
                    {
                        RecurseSubdirectories = true,
                        AttributesToSkip = FileAttributes.ReparsePoint,
                        IgnoreInaccessible = false,
                        ReturnSpecialDirectories = false,
                    })
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
                manifest.TotalPackageFiles == fileRows.Count &&
                manifest.PlannedFiles == fileRows.Count;
            bool completed =
                schemaValid &&
                rowCountsValid &&
                manifest.Completed &&
                !manifestContainsPackageRoot &&
                unsafeManifestPaths == 0 &&
                unsafeModelGraphPaths == 0 &&
                duplicateManifestPaths == 0 &&
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
                ManifestBytes: manifestBytes,
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
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return Failure(
                    rootName,
                    "unsafe-package-tree",
                    manifestExists: false,
                    issues: [new AssetMaterialImportPackageInspectionIssue(
                        "package",
                        AssetMaterialImportPackageMaterializationService.ManifestFileName,
                        "unsafe-package-tree")]);
            }
            finally
            {
                packageSafety?.Dispose();
            }
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

        private static string NormalizeRelativePath(string? path)
        {
            return (path ?? string.Empty).Replace('\\', '/');
        }

        private static bool TryResolveInsideRoot(string fullPackageRoot, string relativePath, out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathRooted(relativePath))
            {
                return false;
            }

            try
            {
                string normalizedRelative = relativePath
                    .Replace('/', Path.DirectorySeparatorChar)
                    .Replace('\\', Path.DirectorySeparatorChar);
                string[] components = normalizedRelative.Split(
                    Path.DirectorySeparatorChar,
                    StringSplitOptions.None);
                if (components.Length == 0 ||
                    components.Any(static component => string.IsNullOrWhiteSpace(component) || component is "." or ".."))
                {
                    return false;
                }

                string candidate = FileMutationSafety.NormalizeLocalPath(
                    Path.Combine(fullPackageRoot, Path.Combine(components)),
                    "Material package manifest path");
                if (!FileMutationSafety.IsSameOrUnderRoot(candidate, fullPackageRoot) ||
                    string.Equals(candidate, fullPackageRoot, FileMutationSafety.PathComparison))
                {
                    return false;
                }

                fullPath = candidate;
                return true;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException)
            {
                return false;
            }
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
