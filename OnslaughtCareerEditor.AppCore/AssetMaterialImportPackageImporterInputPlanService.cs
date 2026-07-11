using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageImporterInputPlanService
    {
        public const string ImporterInputPlanSchema = "onslaught.asset-material-package-importer-input-plan.v1";

        private static readonly JsonSerializerOptions ReadJsonOptions = new()
        {
            PropertyNameCaseInsensitive = true
        };

        public AssetMaterialImportPackageImporterInputPlanResult Build(string packageRoot)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult dryRunValidation =
                new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(fullPackageRoot);
            List<AssetMaterialImportPackageImporterInputPlanIssue> issues = dryRunValidation.Issues
                .Select(static issue => new AssetMaterialImportPackageImporterInputPlanIssue(
                    issue.Role,
                    issue.RelativePath,
                    issue.Status))
                .ToList();

            if (!Directory.Exists(fullPackageRoot))
            {
                return Failure(
                    packageRootName,
                    "missing-package-root",
                    manifestExists: false,
                    dryRunValidation,
                    [new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "missing-package-root")]);
            }

            string manifestJson;
            long manifestBytes;
            try
            {
                using GuardedPackageArtifactRead manifestRead = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName,
                    "Material package importer-input manifest");
                if (!manifestRead.Exists)
                {
                    return Failure(
                        packageRootName,
                        "missing-manifest",
                        manifestExists: false,
                        dryRunValidation,
                        [new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "missing-manifest")]);
                }

                manifestJson = manifestRead.ReadAllText(System.Text.Encoding.UTF8);
                manifestBytes = manifestRead.Length;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return Failure(
                    packageRootName,
                    "unsafe-manifest-path",
                    manifestExists: false,
                    dryRunValidation,
                    [new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "unsafe-manifest-path")]);
            }

            bool manifestContainsPackageRoot = ContainsPathToken(manifestJson, fullPackageRoot);
            bool manifestContainsHashToken = manifestJson.Contains("sha256", StringComparison.OrdinalIgnoreCase);
            AssetMaterialImportPackageImporterInputManifest? manifest;
            try
            {
                manifest = JsonSerializer.Deserialize<AssetMaterialImportPackageImporterInputManifest>(
                    manifestJson,
                    ReadJsonOptions);
            }
            catch (JsonException)
            {
                return Failure(
                    packageRootName,
                    "invalid-json",
                    manifestExists: true,
                    dryRunValidation,
                    [new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "invalid-json")],
                    manifestBytes: manifestBytes,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    manifestContainsHashToken: manifestContainsHashToken);
            }

            if (manifest is null)
            {
                return Failure(
                    packageRootName,
                    "empty-manifest",
                    manifestExists: true,
                    dryRunValidation,
                    [new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "empty-manifest")],
                    manifestBytes: manifestBytes,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    manifestContainsHashToken: manifestContainsHashToken);
            }

            if (manifest.Rows is null ||
                manifest.Rows.Count > 100_000 ||
                manifest.Rows.Any(static row => row is null))
            {
                return Failure(
                    packageRootName,
                    "invalid-structure",
                    manifestExists: true,
                    dryRunValidation,
                    [new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "invalid-structure")],
                    manifestBytes: manifestBytes,
                    manifestContainsPackageRoot: manifestContainsPackageRoot,
                    manifestContainsHashToken: manifestContainsHashToken);
            }

            bool schemaValid = string.Equals(
                manifest.Schema,
                AssetMaterialImportPackageImporterInputService.ImporterInputManifestSchema,
                StringComparison.Ordinal);
            if (!schemaValid)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "invalid-schema"));
            }

            if (manifestContainsPackageRoot)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "package-root-leak"));
            }

            if (manifestContainsHashToken)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "hash-token-leak"));
            }

            if (manifest.Rows.Count != manifest.PlannedAdapterRows)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "planned-row-count-mismatch"));
            }

            if (!manifest.Completed)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("manifest", AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName, "manifest-not-complete"));
            }

            Dictionary<string, IReadOnlyList<AssetMaterialImportPackageImporterInputRow>> textureRowsByCatalogId = manifest.Rows
                .Where(static row => string.Equals(row.Role, "texture", StringComparison.OrdinalIgnoreCase))
                .GroupBy(static row => row.CatalogId, StringComparer.OrdinalIgnoreCase)
                .ToDictionary(static group => group.Key, static group => (IReadOnlyList<AssetMaterialImportPackageImporterInputRow>)group.ToList(), StringComparer.OrdinalIgnoreCase);
            IReadOnlyList<AssetMaterialImportPackageImporterInputPlanModelJob> modelJobs = manifest.Rows
                .Where(static row => string.Equals(row.Role, "model", StringComparison.OrdinalIgnoreCase))
                .OrderBy(static row => row.Ordinal)
                .Select(row => BuildModelJob(fullPackageRoot, row, textureRowsByCatalogId, issues))
                .ToList();
            IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob> textureJobs = manifest.Rows
                .Where(static row => string.Equals(row.Role, "texture", StringComparison.OrdinalIgnoreCase))
                .OrderBy(static row => row.Ordinal)
                .Select(row => BuildTextureJob(fullPackageRoot, row, issues))
                .ToList();

            int totalJobRows = modelJobs.Count + textureJobs.Count;
            int readyJobRows = modelJobs.Count(static job => job.ReadyForImportPlan) +
                textureJobs.Count(static job => job.ReadyForImportPlan);
            int blockedJobRows = totalJobRows - readyJobRows;
            int missingInputFiles = modelJobs.Count(static job => !job.InputFileExists) +
                textureJobs.Count(static job => !job.InputFileExists);
            int unsafeInputPaths = modelJobs.Count(static job => job.PathStatus == "unsafe-input-path") +
                textureJobs.Count(static job => job.PathStatus == "unsafe-input-path");
            int readableModelRows = modelJobs.Count(static job => job.MetadataAvailable);
            int modelGeometryRows = modelJobs.Count(static job => job.GeometryCount > 0);
            int modelWireframeRows = modelJobs.Count(static job => job.WireframeAvailable);
            int readableTextureBindingRows = textureJobs.Count(static job => job.ReadablePng);
            int uniqueReadableTextureFiles = textureJobs
                .Where(static job => job.ReadablePng)
                .Select(static job => job.AdapterRelativePath)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Count();
            int existingUniqueInputFiles = manifest.Rows
                .Select(static row => row.AdapterRelativePath)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Count(path => SafePackageFileExists(fullPackageRoot, path));
            int uniqueInputFiles = manifest.Rows
                .Select(static row => row.AdapterRelativePath)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .Count();
            bool completed =
                schemaValid &&
                manifest.Completed &&
                dryRunValidation.Completed &&
                !manifestContainsPackageRoot &&
                !manifestContainsHashToken &&
                manifest.Rows.Count == manifest.PlannedAdapterRows &&
                blockedJobRows == 0 &&
                missingInputFiles == 0 &&
                unsafeInputPaths == 0 &&
                issues.Count == 0;
            string status = completed
                ? "ready"
                : schemaValid
                    ? "issues-found"
                    : "invalid-schema";

            return new AssetMaterialImportPackageImporterInputPlanResult(
                PackageRootName: packageRootName,
                Schema: ImporterInputPlanSchema,
                ManifestRelativePath: AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName,
                ManifestExists: true,
                ManifestStatus: status,
                ManifestBytes: manifestBytes,
                InputManifestSchema: manifest.Schema,
                InputManifestSchemaValid: schemaValid,
                InputManifestCompletedFlag: manifest.Completed,
                ManifestContainsPackageRoot: manifestContainsPackageRoot,
                ManifestContainsHashToken: manifestContainsHashToken,
                SourceDryRunSidecarRelativePath: dryRunValidation.SidecarRelativePath,
                SourceDryRunSidecarStatus: dryRunValidation.SidecarStatus,
                SourceDryRunSidecarValidated: dryRunValidation.Completed,
                PlannedAdapterRows: manifest.PlannedAdapterRows,
                ReadyAdapterRows: manifest.ReadyAdapterRows,
                ManifestRows: manifest.Rows.Count,
                ModelJobRows: modelJobs.Count,
                TextureBindingJobRows: textureJobs.Count,
                TotalJobRows: totalJobRows,
                ReadyJobRows: readyJobRows,
                BlockedJobRows: blockedJobRows,
                UniqueInputFiles: uniqueInputFiles,
                ExistingUniqueInputFiles: existingUniqueInputFiles,
                MissingInputFiles: missingInputFiles,
                UnsafeInputPaths: unsafeInputPaths,
                ReadableModelRows: readableModelRows,
                ModelGeometryRows: modelGeometryRows,
                ModelWireframeRows: modelWireframeRows,
                ReadableTextureBindingRows: readableTextureBindingRows,
                UniqueReadableTextureFiles: uniqueReadableTextureFiles,
                Completed: completed,
                ModelJobs: modelJobs,
                TextureBindingJobs: textureJobs,
                Issues: issues);
        }

        private static AssetMaterialImportPackageImporterInputPlanModelJob BuildModelJob(
            string fullPackageRoot,
            AssetMaterialImportPackageImporterInputRow row,
            IReadOnlyDictionary<string, IReadOnlyList<AssetMaterialImportPackageImporterInputRow>> textureRowsByCatalogId,
            List<AssetMaterialImportPackageImporterInputPlanIssue> issues)
        {
            string adapterRelativePath = NormalizeRelativePath(row.AdapterRelativePath);
            string sourceRelativePath = NormalizeRelativePath(row.SourcePackageRelativePath);
            string pathStatus = ResolveInputPathStatus(fullPackageRoot, adapterRelativePath, out _);
            bool inputFileExists = false;
            AssetModelSummary summary = AssetModelSummary.Unavailable(0, "Importer input model file is missing.");
            if (pathStatus == "inside-package-root")
            {
                try
                {
                    using GuardedPackageArtifactRead input = GuardedPackageArtifactReader.Open(
                        fullPackageRoot,
                        adapterRelativePath,
                        "Importer input model");
                    inputFileExists = input.Exists;
                    if (inputFileExists)
                        summary = FbxModelSummaryReader.Read(input.Stream);
                }
                catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
                {
                    pathStatus = "unsafe-input-path";
                }
            }
            bool rowReady = IsReadyManifestRow(row.Status);
            int textureBindingRows = textureRowsByCatalogId.TryGetValue(row.CatalogId, out IReadOnlyList<AssetMaterialImportPackageImporterInputRow>? textureRows)
                ? textureRows.Count
                : 0;
            int uniqueTextureInputFiles = textureRowsByCatalogId.TryGetValue(row.CatalogId, out IReadOnlyList<AssetMaterialImportPackageImporterInputRow>? rows)
                ? rows.Select(static texture => texture.AdapterRelativePath).Distinct(StringComparer.OrdinalIgnoreCase).Count()
                : 0;
            string planStatus = BuildModelPlanStatus(rowReady, pathStatus, inputFileExists, summary, textureBindingRows);
            bool readyForImportPlan = planStatus == "ready-for-import-plan";
            if (!readyForImportPlan)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("model", adapterRelativePath, planStatus));
            }

            return new AssetMaterialImportPackageImporterInputPlanModelJob(
                Ordinal: row.Ordinal,
                Action: "import-model",
                CatalogId: row.CatalogId,
                Label: row.Label,
                SourcePackageRelativePath: sourceRelativePath,
                AdapterRelativePath: adapterRelativePath,
                AdapterAction: row.AdapterAction,
                InputFileExists: inputFileExists,
                PathStatus: pathStatus,
                ManifestRowStatus: row.Status,
                TextureBindingRows: textureBindingRows,
                UniqueTextureInputFiles: uniqueTextureInputFiles,
                MetadataAvailable: summary.MetadataAvailable,
                Format: summary.Format,
                FormatVersion: summary.FormatVersion,
                ByteSize: summary.ByteSize,
                GeometryCount: summary.GeometryCount,
                ModelCount: summary.ModelCount,
                MaterialCount: summary.MaterialCount,
                TextureBindingCount: summary.TextureBindingCount,
                VertexCount: summary.VertexCount,
                PolygonIndexCount: summary.PolygonIndexCount,
                WireframeAvailable: summary.GeometryPreview.Available,
                PreviewVertexCount: summary.GeometryPreview.Vertices.Count,
                PreviewEdgeCount: summary.GeometryPreview.Edges.Count,
                ReadyForImportPlan: readyForImportPlan,
                PlanStatus: planStatus);
        }

        private static AssetMaterialImportPackageImporterInputPlanTextureBindingJob BuildTextureJob(
            string fullPackageRoot,
            AssetMaterialImportPackageImporterInputRow row,
            List<AssetMaterialImportPackageImporterInputPlanIssue> issues)
        {
            string adapterRelativePath = NormalizeRelativePath(row.AdapterRelativePath);
            string sourceRelativePath = NormalizeRelativePath(row.SourcePackageRelativePath);
            string pathStatus = ResolveInputPathStatus(fullPackageRoot, adapterRelativePath, out _);
            bool inputFileExists = false;
            PngHeaderInfo header = new(false, null, null, 0, "Importer input texture file is missing.");
            if (pathStatus == "inside-package-root")
            {
                try
                {
                    using GuardedPackageArtifactRead input = GuardedPackageArtifactReader.Open(
                        fullPackageRoot,
                        adapterRelativePath,
                        "Importer input texture");
                    inputFileExists = input.Exists;
                    if (inputFileExists)
                        header = PngHeaderReader.Read(input.Stream);
                }
                catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
                {
                    pathStatus = "unsafe-input-path";
                }
            }
            bool rowReady = IsReadyManifestRow(row.Status);
            string planStatus = BuildTexturePlanStatus(rowReady, pathStatus, inputFileExists, header);
            bool readyForImportPlan = planStatus == "ready-for-import-plan";
            if (!readyForImportPlan)
            {
                issues.Add(new AssetMaterialImportPackageImporterInputPlanIssue("texture", adapterRelativePath, planStatus));
            }

            return new AssetMaterialImportPackageImporterInputPlanTextureBindingJob(
                Ordinal: row.Ordinal,
                Action: "bind-texture",
                CatalogId: row.CatalogId,
                Label: row.Label,
                BindingFileName: row.BindingFileName,
                SourcePackageRelativePath: sourceRelativePath,
                AdapterRelativePath: adapterRelativePath,
                AdapterAction: row.AdapterAction,
                InputFileExists: inputFileExists,
                PathStatus: pathStatus,
                ManifestRowStatus: row.Status,
                ReadablePng: header.Readable,
                Width: header.Width,
                Height: header.Height,
                ByteSize: header.ByteSize,
                ReadyForImportPlan: readyForImportPlan,
                PlanStatus: planStatus);
        }

        private static AssetMaterialImportPackageImporterInputPlanResult Failure(
            string packageRootName,
            string status,
            bool manifestExists,
            AssetMaterialImportPackageImporterDryRunSidecarValidationResult dryRunValidation,
            IReadOnlyList<AssetMaterialImportPackageImporterInputPlanIssue> issues,
            long manifestBytes = 0,
            bool manifestContainsPackageRoot = false,
            bool manifestContainsHashToken = false)
        {
            return new AssetMaterialImportPackageImporterInputPlanResult(
                PackageRootName: packageRootName,
                Schema: ImporterInputPlanSchema,
                ManifestRelativePath: AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName,
                ManifestExists: manifestExists,
                ManifestStatus: status,
                ManifestBytes: manifestBytes,
                InputManifestSchema: string.Empty,
                InputManifestSchemaValid: false,
                InputManifestCompletedFlag: false,
                ManifestContainsPackageRoot: manifestContainsPackageRoot,
                ManifestContainsHashToken: manifestContainsHashToken,
                SourceDryRunSidecarRelativePath: dryRunValidation.SidecarRelativePath,
                SourceDryRunSidecarStatus: dryRunValidation.SidecarStatus,
                SourceDryRunSidecarValidated: dryRunValidation.Completed,
                PlannedAdapterRows: 0,
                ReadyAdapterRows: 0,
                ManifestRows: 0,
                ModelJobRows: 0,
                TextureBindingJobRows: 0,
                TotalJobRows: 0,
                ReadyJobRows: 0,
                BlockedJobRows: 0,
                UniqueInputFiles: 0,
                ExistingUniqueInputFiles: 0,
                MissingInputFiles: 0,
                UnsafeInputPaths: 0,
                ReadableModelRows: 0,
                ModelGeometryRows: 0,
                ModelWireframeRows: 0,
                ReadableTextureBindingRows: 0,
                UniqueReadableTextureFiles: 0,
                Completed: false,
                ModelJobs: [],
                TextureBindingJobs: [],
                Issues: issues);
        }

        private static string BuildModelPlanStatus(
            bool rowReady,
            string pathStatus,
            bool inputFileExists,
            AssetModelSummary summary,
            int textureBindingRows)
        {
            if (!rowReady)
            {
                return "manifest-row-not-ready";
            }

            if (pathStatus != "inside-package-root")
            {
                return pathStatus;
            }

            if (!inputFileExists)
            {
                return "missing-input-file";
            }

            if (!summary.MetadataAvailable)
            {
                return "unreadable-model-file";
            }

            if (summary.GeometryCount <= 0)
            {
                return "model-without-geometry";
            }

            if (textureBindingRows <= 0)
            {
                return "model-without-texture-bindings";
            }

            return "ready-for-import-plan";
        }

        private static string BuildTexturePlanStatus(
            bool rowReady,
            string pathStatus,
            bool inputFileExists,
            PngHeaderInfo header)
        {
            if (!rowReady)
            {
                return "manifest-row-not-ready";
            }

            if (pathStatus != "inside-package-root")
            {
                return pathStatus;
            }

            if (!inputFileExists)
            {
                return "missing-input-file";
            }

            return header.Readable ? "ready-for-import-plan" : "unreadable-texture-file";
        }

        private static bool SafePackageFileExists(string fullPackageRoot, string relativePath)
        {
            try
            {
                using GuardedPackageArtifactRead read = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    relativePath,
                    "Importer input file");
                return read.Exists;
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return false;
            }
        }

        private static string ResolveInputPathStatus(
            string fullPackageRoot,
            string adapterRelativePath,
            out string fullPath)
        {
            fullPath = string.Empty;
            if (!adapterRelativePath.StartsWith(AssetMaterialImportPackageImporterInputService.ImporterInputRootRelativePath + "/", StringComparison.OrdinalIgnoreCase))
            {
                return "unsafe-input-path";
            }

            return TryResolveInsidePackage(fullPackageRoot, adapterRelativePath, out fullPath)
                ? "inside-package-root"
                : "unsafe-input-path";
        }

        private static bool TryResolveInsidePackage(string fullPackageRoot, string relativePath, out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathRooted(relativePath))
                return false;

            try
            {
                string normalized = relativePath
                    .Replace('/', Path.DirectorySeparatorChar)
                    .Replace('\\', Path.DirectorySeparatorChar);
                string[] components = normalized.Split(Path.DirectorySeparatorChar, StringSplitOptions.None);
                if (components.Length == 0 ||
                    components.Any(static component => string.IsNullOrWhiteSpace(component) || component is "." or ".."))
                {
                    return false;
                }

                string candidate = FileMutationSafety.NormalizeLocalPath(
                    Path.Combine(fullPackageRoot, Path.Combine(components)),
                    "Importer input path");
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

        private static bool IsReadyManifestRow(string status)
        {
            return status is "copied" or "skipped-existing" or "would-skip-existing";
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private static string NormalizeRelativePath(string? value)
        {
            return (value ?? string.Empty).Replace('\\', '/');
        }

        private static bool ContainsPathToken(string text, string fullPackageRoot)
        {
            string normalized = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            return text.Contains(normalized, StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace("\\", "\\\\"), StringComparison.OrdinalIgnoreCase) ||
                   text.Contains(normalized.Replace('\\', '/'), StringComparison.OrdinalIgnoreCase);
        }
    }

    public sealed record AssetMaterialImportPackageImporterInputPlanResult(
        string PackageRootName,
        string Schema,
        string ManifestRelativePath,
        bool ManifestExists,
        string ManifestStatus,
        long ManifestBytes,
        string InputManifestSchema,
        bool InputManifestSchemaValid,
        bool InputManifestCompletedFlag,
        bool ManifestContainsPackageRoot,
        bool ManifestContainsHashToken,
        string SourceDryRunSidecarRelativePath,
        string SourceDryRunSidecarStatus,
        bool SourceDryRunSidecarValidated,
        int PlannedAdapterRows,
        int ReadyAdapterRows,
        int ManifestRows,
        int ModelJobRows,
        int TextureBindingJobRows,
        int TotalJobRows,
        int ReadyJobRows,
        int BlockedJobRows,
        int UniqueInputFiles,
        int ExistingUniqueInputFiles,
        int MissingInputFiles,
        int UnsafeInputPaths,
        int ReadableModelRows,
        int ModelGeometryRows,
        int ModelWireframeRows,
        int ReadableTextureBindingRows,
        int UniqueReadableTextureFiles,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageImporterInputPlanModelJob> ModelJobs,
        IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob> TextureBindingJobs,
        IReadOnlyList<AssetMaterialImportPackageImporterInputPlanIssue> Issues);

    public sealed record AssetMaterialImportPackageImporterInputPlanModelJob(
        int Ordinal,
        string Action,
        string CatalogId,
        string Label,
        string SourcePackageRelativePath,
        string AdapterRelativePath,
        string AdapterAction,
        bool InputFileExists,
        string PathStatus,
        string ManifestRowStatus,
        int TextureBindingRows,
        int UniqueTextureInputFiles,
        bool MetadataAvailable,
        string Format,
        int? FormatVersion,
        long ByteSize,
        int GeometryCount,
        int ModelCount,
        int MaterialCount,
        int TextureBindingCount,
        int VertexCount,
        int PolygonIndexCount,
        bool WireframeAvailable,
        int PreviewVertexCount,
        int PreviewEdgeCount,
        bool ReadyForImportPlan,
        string PlanStatus);

    public sealed record AssetMaterialImportPackageImporterInputPlanTextureBindingJob(
        int Ordinal,
        string Action,
        string CatalogId,
        string Label,
        string BindingFileName,
        string SourcePackageRelativePath,
        string AdapterRelativePath,
        string AdapterAction,
        bool InputFileExists,
        string PathStatus,
        string ManifestRowStatus,
        bool ReadablePng,
        int? Width,
        int? Height,
        long ByteSize,
        bool ReadyForImportPlan,
        string PlanStatus);

    public sealed record AssetMaterialImportPackageImporterInputPlanIssue(
        string Role,
        string RelativePath,
        string Status);
}
