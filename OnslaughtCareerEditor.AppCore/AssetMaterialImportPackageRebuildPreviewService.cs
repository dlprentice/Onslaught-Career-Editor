using System.Globalization;
using System.Text;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageRebuildPreviewService
    {
        public const string WorkspaceRootRelativePath = "rebuild-preview";
        public const string ManifestFileName = "material-package-rebuild-preview.v1.json";
        public const string ManifestSchema = "onslaught.asset-material-package-rebuild-preview.v1";

        private static readonly JsonSerializerOptions WriteJsonOptions = new(JsonSerializerDefaults.Web)
        {
            WriteIndented = true
        };
        private static readonly UTF8Encoding Utf8NoBom = new(encoderShouldEmitUTF8Identifier: false);

        public AssetMaterialImportPackageRebuildPreviewResult Preflight(string packageRoot)
        {
            return Build(packageRoot, executeWrite: false);
        }

        public AssetMaterialImportPackageRebuildPreviewResult Materialize(string packageRoot)
        {
            return Build(packageRoot, executeWrite: true);
        }

        private static AssetMaterialImportPackageRebuildPreviewResult Build(string packageRoot, bool executeWrite)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageImporterInputPlanResult inputPlan =
                new AssetMaterialImportPackageImporterInputPlanService().Build(fullPackageRoot);
            List<AssetMaterialImportPackageRebuildPreviewIssue> issues = inputPlan.Issues
                .Select(static issue => new AssetMaterialImportPackageRebuildPreviewIssue(
                    issue.Role,
                    issue.RelativePath,
                    issue.Status))
                .ToList();

            if (!inputPlan.Completed)
            {
                if (issues.Count == 0)
                {
                    issues.Add(new AssetMaterialImportPackageRebuildPreviewIssue(
                        "input-plan",
                        inputPlan.ManifestRelativePath,
                        inputPlan.ManifestStatus));
                }

                return BuildResult(
                    executeWrite,
                    packageRootName,
                    inputPlan,
                    manifestWritten: false,
                    manifestStatus: inputPlan.ManifestStatus,
                    manifestBytes: 0,
                    modelRows: [],
                    issues);
            }

            IReadOnlyDictionary<string, IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob>> texturesByCatalogId =
                inputPlan.TextureBindingJobs
                    .GroupBy(static texture => texture.CatalogId, StringComparer.OrdinalIgnoreCase)
                    .ToDictionary(static group => group.Key, static group => (IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob>)group.ToList(), StringComparer.OrdinalIgnoreCase);

            List<AssetMaterialImportPackageRebuildPreviewModelRow> modelRows = inputPlan.ModelJobs
                .OrderBy(static job => job.Ordinal)
                .Select(job => BuildModelRow(fullPackageRoot, executeWrite, job, texturesByCatalogId, issues))
                .ToList();

            bool ready = modelRows.All(static row => IsReadyStatus(row.Status)) && issues.Count == 0;
            (bool manifestWritten, string manifestStatus, long manifestBytes) =
                WriteManifestIfRequested(executeWrite, fullPackageRoot, packageRootName, inputPlan, modelRows, ready);

            return BuildResult(
                executeWrite,
                packageRootName,
                inputPlan,
                manifestWritten,
                manifestStatus,
                manifestBytes,
                modelRows,
                issues);
        }

        private static AssetMaterialImportPackageRebuildPreviewResult BuildResult(
            bool executeWrite,
            string packageRootName,
            AssetMaterialImportPackageImporterInputPlanResult inputPlan,
            bool manifestWritten,
            string manifestStatus,
            long manifestBytes,
            IReadOnlyList<AssetMaterialImportPackageRebuildPreviewModelRow> modelRows,
            IReadOnlyList<AssetMaterialImportPackageRebuildPreviewIssue> issues)
        {
            int readyRows = modelRows.Count(static row => IsReadyStatus(row.Status));
            int blockedRows = modelRows.Count - readyRows;
            return new AssetMaterialImportPackageRebuildPreviewResult(
                Executed: executeWrite,
                PackageRootName: packageRootName,
                SourceInputPlanRelativePath: inputPlan.ManifestRelativePath,
                SourceInputPlanStatus: inputPlan.ManifestStatus,
                SourceInputPlanCompleted: inputPlan.Completed,
                WorkspaceRootRelativePath: WorkspaceRootRelativePath,
                ManifestRelativePath: ManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                SourceModelJobRows: inputPlan.ModelJobRows,
                SourceTextureBindingJobRows: inputPlan.TextureBindingJobRows,
                ModelPreviewRows: modelRows.Count,
                ReadyPreviewRows: readyRows,
                BlockedPreviewRows: blockedRows,
                WouldWritePreviewRows: modelRows.Count(static row => row.Status == "would-write"),
                WrittenPreviewRows: modelRows.Count(static row => row.Status == "written"),
                ExistingPreviewRows: modelRows.Count(static row => row.Status is "would-skip-existing" or "skipped-existing"),
                BlockedExistingMismatches: modelRows.Count(static row => row.Status == "blocked-existing-mismatch"),
                MissingInputFiles: modelRows.Count(static row => row.Status == "missing-input-file"),
                UnsafeOutputPaths: modelRows.Count(static row => row.Status == "unsafe-output-path"),
                ObjFileRows: modelRows.Count(static row => !string.IsNullOrWhiteSpace(row.ObjRelativePath)),
                BindingSidecarRows: modelRows.Count(static row => !string.IsNullOrWhiteSpace(row.BindingSidecarRelativePath)),
                TextureBindingRows: modelRows.Sum(static row => row.TextureBindingRows),
                PreviewVertexRows: modelRows.Sum(static row => row.PreviewVertexCount),
                PreviewEdgeRows: modelRows.Sum(static row => row.PreviewEdgeCount),
                Completed: inputPlan.Completed && readyRows == modelRows.Count && issues.Count == 0,
                Models: modelRows,
                Issues: issues);
        }

        private static AssetMaterialImportPackageRebuildPreviewModelRow BuildModelRow(
            string fullPackageRoot,
            bool executeWrite,
            AssetMaterialImportPackageImporterInputPlanModelJob model,
            IReadOnlyDictionary<string, IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob>> texturesByCatalogId,
            List<AssetMaterialImportPackageRebuildPreviewIssue> issues)
        {
            string modelInputRelativePath = NormalizeRelativePath(model.AdapterRelativePath);
            if (!model.ReadyForImportPlan)
            {
                issues.Add(new AssetMaterialImportPackageRebuildPreviewIssue("model", modelInputRelativePath, model.PlanStatus));
                return BuildBlockedModelRow(model, modelInputRelativePath, model.PlanStatus);
            }

            if (!TryResolveInsidePackage(fullPackageRoot, modelInputRelativePath, out string fullModelInputPath) ||
                !File.Exists(fullModelInputPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildPreviewIssue("model", modelInputRelativePath, "missing-input-file"));
                return BuildBlockedModelRow(model, modelInputRelativePath, "missing-input-file");
            }

            AssetModelSummary summary = FbxModelSummaryReader.Read(fullModelInputPath);
            if (!summary.GeometryPreview.Available)
            {
                issues.Add(new AssetMaterialImportPackageRebuildPreviewIssue("model", modelInputRelativePath, "missing-wireframe-preview"));
                return BuildBlockedModelRow(model, modelInputRelativePath, "missing-wireframe-preview");
            }

            string outputToken = BuildOutputToken(model.Ordinal, model.CatalogId);
            string objRelativePath = $"{WorkspaceRootRelativePath}/models/{outputToken}.wire.obj";
            string bindingRelativePath = $"{WorkspaceRootRelativePath}/models/{outputToken}.bindings.json";
            if (!TryResolveInsidePackage(fullPackageRoot, objRelativePath, out string fullObjPath) ||
                !TryResolveInsidePackage(fullPackageRoot, bindingRelativePath, out string fullBindingPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildPreviewIssue("model", objRelativePath, "unsafe-output-path"));
                return BuildBlockedModelRow(model, modelInputRelativePath, "unsafe-output-path", objRelativePath, bindingRelativePath);
            }

            IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob> textureJobs =
                texturesByCatalogId.TryGetValue(model.CatalogId, out IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob>? jobs)
                    ? jobs
                    : [];
            string objContent = BuildObjContent(model, summary.GeometryPreview);
            string bindingContent = BuildBindingSidecarContent(model, textureJobs, objRelativePath);
            bool objExists = File.Exists(fullObjPath);
            bool bindingExists = File.Exists(fullBindingPath);
            bool objMatches = objExists && string.Equals(File.ReadAllText(fullObjPath), objContent, StringComparison.Ordinal);
            bool bindingMatches = bindingExists && string.Equals(File.ReadAllText(fullBindingPath), bindingContent, StringComparison.Ordinal);
            if ((objExists && !objMatches) || (bindingExists && !bindingMatches))
            {
                issues.Add(new AssetMaterialImportPackageRebuildPreviewIssue("model", objRelativePath, "blocked-existing-mismatch"));
                return BuildModelRowResult(
                    model,
                    modelInputRelativePath,
                    objRelativePath,
                    bindingRelativePath,
                    "blocked-existing-mismatch",
                    summary.GeometryPreview.Vertices.Count,
                    summary.GeometryPreview.Edges.Count,
                    textureJobs.Count);
            }

            string status;
            if (!executeWrite)
            {
                status = objExists && bindingExists ? "would-skip-existing" : "would-write";
            }
            else
            {
                Directory.CreateDirectory(Path.GetDirectoryName(fullObjPath)!);
                if (!objExists)
                {
                    File.WriteAllText(fullObjPath, objContent, Utf8NoBom);
                }

                if (!bindingExists)
                {
                    File.WriteAllText(fullBindingPath, bindingContent, Utf8NoBom);
                }

                status = objExists && bindingExists ? "skipped-existing" : "written";
            }

            return BuildModelRowResult(
                model,
                modelInputRelativePath,
                objRelativePath,
                bindingRelativePath,
                status,
                summary.GeometryPreview.Vertices.Count,
                summary.GeometryPreview.Edges.Count,
                textureJobs.Count);
        }

        private static AssetMaterialImportPackageRebuildPreviewModelRow BuildBlockedModelRow(
            AssetMaterialImportPackageImporterInputPlanModelJob model,
            string modelInputRelativePath,
            string status,
            string objRelativePath = "",
            string bindingRelativePath = "")
        {
            return BuildModelRowResult(
                model,
                modelInputRelativePath,
                objRelativePath,
                bindingRelativePath,
                status,
                previewVertexCount: 0,
                previewEdgeCount: 0,
                textureBindingRows: model.TextureBindingRows);
        }

        private static AssetMaterialImportPackageRebuildPreviewModelRow BuildModelRowResult(
            AssetMaterialImportPackageImporterInputPlanModelJob model,
            string modelInputRelativePath,
            string objRelativePath,
            string bindingRelativePath,
            string status,
            int previewVertexCount,
            int previewEdgeCount,
            int textureBindingRows)
        {
            return new AssetMaterialImportPackageRebuildPreviewModelRow(
                Ordinal: model.Ordinal,
                CatalogId: model.CatalogId,
                Label: model.Label,
                ModelInputRelativePath: modelInputRelativePath,
                ObjRelativePath: objRelativePath,
                BindingSidecarRelativePath: bindingRelativePath,
                TextureBindingRows: textureBindingRows,
                PreviewVertexCount: previewVertexCount,
                PreviewEdgeCount: previewEdgeCount,
                Status: status,
                ReadyForRebuildPreview: IsReadyStatus(status));
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeWrite,
            string fullPackageRoot,
            string packageRootName,
            AssetMaterialImportPackageImporterInputPlanResult inputPlan,
            IReadOnlyList<AssetMaterialImportPackageRebuildPreviewModelRow> modelRows,
            bool completed)
        {
            if (!executeWrite)
            {
                return (false, "preflight-not-written", 0);
            }

            string manifestPath = Path.Combine(fullPackageRoot, ManifestFileName);
            AssetMaterialImportPackageRebuildPreviewManifest manifest = new(
                Schema: ManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                PackageRootName: packageRootName,
                SourceInputPlanRelativePath: inputPlan.ManifestRelativePath,
                WorkspaceRootRelativePath: WorkspaceRootRelativePath,
                SourceModelJobRows: inputPlan.ModelJobRows,
                SourceTextureBindingJobRows: inputPlan.TextureBindingJobRows,
                ModelPreviewRows: modelRows.Count,
                ReadyPreviewRows: modelRows.Count(static row => row.ReadyForRebuildPreview),
                ObjFileRows: modelRows.Count(static row => !string.IsNullOrWhiteSpace(row.ObjRelativePath)),
                BindingSidecarRows: modelRows.Count(static row => !string.IsNullOrWhiteSpace(row.BindingSidecarRelativePath)),
                Completed: completed,
                Models: modelRows.OrderBy(static row => row.Ordinal).ToList());
            File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, WriteJsonOptions), Utf8NoBom);
            return (true, "written", new FileInfo(manifestPath).Length);
        }

        private static string BuildObjContent(
            AssetMaterialImportPackageImporterInputPlanModelJob model,
            AssetModelGeometryPreview preview)
        {
            StringBuilder builder = new();
            builder.AppendLine("# onslaught asset material package rebuild preview obj v1");
            builder.AppendLine($"# catalogId: {model.CatalogId}");
            builder.AppendLine($"# source: {NormalizeRelativePath(model.AdapterRelativePath)}");
            builder.AppendLine($"o {BuildObjectName(model.CatalogId)}");
            foreach (AssetModelPreviewVertex vertex in preview.Vertices)
            {
                builder.Append("v ");
                builder.Append(vertex.X.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(vertex.Y.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(vertex.Z.ToString("R", CultureInfo.InvariantCulture));
                builder.AppendLine();
            }

            foreach (AssetModelPreviewEdge edge in preview.Edges)
            {
                builder.Append("l ");
                builder.Append((edge.StartIndex + 1).ToString(CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append((edge.EndIndex + 1).ToString(CultureInfo.InvariantCulture));
                builder.AppendLine();
            }

            return builder.ToString();
        }

        private static string BuildBindingSidecarContent(
            AssetMaterialImportPackageImporterInputPlanModelJob model,
            IReadOnlyList<AssetMaterialImportPackageImporterInputPlanTextureBindingJob> textureJobs,
            string objRelativePath)
        {
            AssetMaterialImportPackageRebuildPreviewBindingSidecar sidecar = new(
                Schema: "onslaught.asset-material-package-rebuild-preview-bindings.v1",
                CatalogId: model.CatalogId,
                Label: model.Label,
                ModelInputRelativePath: NormalizeRelativePath(model.AdapterRelativePath),
                ObjRelativePath: objRelativePath,
                TextureBindingRows: textureJobs.Count,
                Textures: textureJobs
                    .OrderBy(static texture => texture.Ordinal)
                    .Select(static texture => new AssetMaterialImportPackageRebuildPreviewTextureBinding(
                        Ordinal: texture.Ordinal,
                        BindingFileName: texture.BindingFileName,
                        TextureInputRelativePath: NormalizeRelativePath(texture.AdapterRelativePath),
                        Width: texture.Width,
                        Height: texture.Height,
                        ReadyForBinding: texture.ReadyForImportPlan))
                    .ToList());
            return JsonSerializer.Serialize(sidecar, WriteJsonOptions);
        }

        private static string BuildOutputToken(int ordinal, string catalogId)
        {
            return $"{ordinal:0000}-{SanitizeToken(catalogId)}";
        }

        private static string BuildObjectName(string catalogId)
        {
            return SanitizeToken(catalogId).Replace('-', '_');
        }

        private static string SanitizeToken(string value)
        {
            StringBuilder builder = new();
            foreach (char c in value)
            {
                if (char.IsAsciiLetterOrDigit(c))
                {
                    builder.Append(char.ToLowerInvariant(c));
                }
                else if (c is '-' or '_' or '.')
                {
                    builder.Append(c);
                }
                else
                {
                    builder.Append('_');
                }
            }

            string token = builder.ToString().Trim('_', '.', '-');
            return string.IsNullOrWhiteSpace(token) ? "asset" : token;
        }

        private static bool TryResolveInsidePackage(string fullPackageRoot, string relativePath, out string fullPath)
        {
            fullPath = string.Empty;
            if (string.IsNullOrWhiteSpace(relativePath) || Path.IsPathRooted(relativePath))
            {
                return false;
            }

            string candidate = Path.GetFullPath(Path.Combine(
                fullPackageRoot,
                relativePath.Replace('/', Path.DirectorySeparatorChar).Replace('\\', Path.DirectorySeparatorChar)));
            string root = fullPackageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar) +
                Path.DirectorySeparatorChar;
            if (!candidate.StartsWith(root, StringComparison.OrdinalIgnoreCase))
            {
                return false;
            }

            fullPath = candidate;
            return true;
        }

        private static bool IsReadyStatus(string status)
        {
            return status is "would-write" or "would-skip-existing" or "written" or "skipped-existing";
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }
    }

    public sealed record AssetMaterialImportPackageRebuildPreviewResult(
        bool Executed,
        string PackageRootName,
        string SourceInputPlanRelativePath,
        string SourceInputPlanStatus,
        bool SourceInputPlanCompleted,
        string WorkspaceRootRelativePath,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        int SourceModelJobRows,
        int SourceTextureBindingJobRows,
        int ModelPreviewRows,
        int ReadyPreviewRows,
        int BlockedPreviewRows,
        int WouldWritePreviewRows,
        int WrittenPreviewRows,
        int ExistingPreviewRows,
        int BlockedExistingMismatches,
        int MissingInputFiles,
        int UnsafeOutputPaths,
        int ObjFileRows,
        int BindingSidecarRows,
        int TextureBindingRows,
        int PreviewVertexRows,
        int PreviewEdgeRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildPreviewModelRow> Models,
        IReadOnlyList<AssetMaterialImportPackageRebuildPreviewIssue> Issues);

    public sealed record AssetMaterialImportPackageRebuildPreviewModelRow(
        int Ordinal,
        string CatalogId,
        string Label,
        string ModelInputRelativePath,
        string ObjRelativePath,
        string BindingSidecarRelativePath,
        int TextureBindingRows,
        int PreviewVertexCount,
        int PreviewEdgeCount,
        string Status,
        bool ReadyForRebuildPreview);

    public sealed record AssetMaterialImportPackageRebuildPreviewIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageRebuildPreviewManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        string PackageRootName,
        string SourceInputPlanRelativePath,
        string WorkspaceRootRelativePath,
        int SourceModelJobRows,
        int SourceTextureBindingJobRows,
        int ModelPreviewRows,
        int ReadyPreviewRows,
        int ObjFileRows,
        int BindingSidecarRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildPreviewModelRow> Models);

    public sealed record AssetMaterialImportPackageRebuildPreviewBindingSidecar(
        string Schema,
        string CatalogId,
        string Label,
        string ModelInputRelativePath,
        string ObjRelativePath,
        int TextureBindingRows,
        IReadOnlyList<AssetMaterialImportPackageRebuildPreviewTextureBinding> Textures);

    public sealed record AssetMaterialImportPackageRebuildPreviewTextureBinding(
        int Ordinal,
        string BindingFileName,
        string TextureInputRelativePath,
        int? Width,
        int? Height,
        bool ReadyForBinding);
}
