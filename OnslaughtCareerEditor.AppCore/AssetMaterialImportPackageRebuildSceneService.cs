using System.Globalization;
using System.Text;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageRebuildSceneService
    {
        public const string WorkspaceRootRelativePath = "rebuild-scene";
        public const string ManifestFileName = "material-package-rebuild-scene.v1.json";
        public const string ManifestSchema = "onslaught.asset-material-package-rebuild-scene.v1";
        public const string SceneFileSchema = "onslaught.asset-material-package-rebuild-scene-file.v1";

        private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
        {
            PropertyNameCaseInsensitive = true,
            WriteIndented = true
        };
        private static readonly UTF8Encoding Utf8NoBom = new(encoderShouldEmitUTF8Identifier: false);

        public AssetMaterialImportPackageRebuildSceneResult Preflight(string packageRoot)
        {
            return Build(packageRoot, executeWrite: false);
        }

        public AssetMaterialImportPackageRebuildSceneResult Materialize(string packageRoot)
        {
            return Build(packageRoot, executeWrite: true);
        }

        private static AssetMaterialImportPackageRebuildSceneResult Build(string packageRoot, bool executeWrite)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageRebuildPreviewResult rebuildPreview =
                new AssetMaterialImportPackageRebuildPreviewService().Preflight(fullPackageRoot);
            List<AssetMaterialImportPackageRebuildSceneIssue> issues = rebuildPreview.Issues
                .Select(static issue => new AssetMaterialImportPackageRebuildSceneIssue(
                    issue.Role,
                    issue.RelativePath,
                    issue.Status))
                .ToList();

            if (!rebuildPreview.Completed)
            {
                return BuildResult(
                    executeWrite,
                    packageRootName,
                    rebuildPreview,
                    manifestWritten: false,
                    manifestStatus: rebuildPreview.ManifestStatus,
                    manifestBytes: 0,
                    sceneRows: [],
                    issues);
            }

            List<AssetMaterialImportPackageRebuildSceneModelRow> sceneRows = rebuildPreview.Models
                .OrderBy(static model => model.Ordinal)
                .Select(model => BuildSceneRow(fullPackageRoot, executeWrite, model, issues))
                .ToList();
            bool completed = sceneRows.All(static row => IsReadyStatus(row.Status)) && issues.Count == 0;
            (bool manifestWritten, string manifestStatus, long manifestBytes) =
                WriteManifestIfRequested(executeWrite, fullPackageRoot, packageRootName, rebuildPreview, sceneRows, completed);

            return BuildResult(
                executeWrite,
                packageRootName,
                rebuildPreview,
                manifestWritten,
                manifestStatus,
                manifestBytes,
                sceneRows,
                issues);
        }

        private static AssetMaterialImportPackageRebuildSceneResult BuildResult(
            bool executeWrite,
            string packageRootName,
            AssetMaterialImportPackageRebuildPreviewResult rebuildPreview,
            bool manifestWritten,
            string manifestStatus,
            long manifestBytes,
            IReadOnlyList<AssetMaterialImportPackageRebuildSceneModelRow> sceneRows,
            IReadOnlyList<AssetMaterialImportPackageRebuildSceneIssue> issues)
        {
            int readyRows = sceneRows.Count(static row => IsReadyStatus(row.Status));
            return new AssetMaterialImportPackageRebuildSceneResult(
                Executed: executeWrite,
                PackageRootName: packageRootName,
                SourceRebuildPreviewManifestRelativePath: rebuildPreview.ManifestRelativePath,
                SourceRebuildPreviewStatus: rebuildPreview.ManifestStatus,
                SourceRebuildPreviewCompleted: rebuildPreview.Completed,
                WorkspaceRootRelativePath: WorkspaceRootRelativePath,
                ManifestRelativePath: ManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                SourceModelPreviewRows: rebuildPreview.ModelPreviewRows,
                SourceObjFileRows: rebuildPreview.ObjFileRows,
                SourceBindingSidecarRows: rebuildPreview.BindingSidecarRows,
                SceneRows: sceneRows.Count,
                ReadySceneRows: readyRows,
                BlockedSceneRows: sceneRows.Count - readyRows,
                WouldWriteSceneRows: sceneRows.Count(static row => row.Status == "would-write"),
                WrittenSceneRows: sceneRows.Count(static row => row.Status == "written"),
                ExistingSceneRows: sceneRows.Count(static row => row.Status is "would-skip-existing" or "skipped-existing"),
                BlockedExistingMismatches: sceneRows.Count(static row => row.Status == "blocked-existing-mismatch"),
                MissingPreviewFiles: sceneRows.Count(static row => row.Status == "missing-preview-file"),
                MissingModelInputFiles: sceneRows.Count(static row => row.Status == "missing-model-input-file"),
                InvalidPreviewFiles: sceneRows.Count(static row => row.Status == "invalid-preview-file"),
                UnsafeOutputPaths: sceneRows.Count(static row => row.Status == "unsafe-output-path"),
                TextureBindingRows: sceneRows.Sum(static row => row.TextureBindingRows),
                SceneVertexRows: sceneRows.Sum(static row => row.VertexCount),
                SceneEdgeRows: sceneRows.Sum(static row => row.EdgeCount),
                FbxVertexRows: sceneRows.Sum(static row => row.MeshContract?.VertexCount ?? 0),
                FbxPolygonIndexRows: sceneRows.Sum(static row => row.MeshContract?.PolygonIndexCount ?? 0),
                FbxNormalRows: sceneRows.Sum(static row => row.MeshContract?.NormalCount ?? 0),
                FbxTextureCoordinateRows: sceneRows.Sum(static row => row.MeshContract?.TextureCoordinateCount ?? 0),
                MaterialRows: sceneRows.Sum(static row => row.MeshContract?.MaterialCount ?? 0),
                TextureToMaterialConnectionRows: sceneRows.Sum(static row => row.MeshContract?.TextureToMaterialConnectionCount ?? 0),
                SceneBoundsRows: sceneRows.Count(static row => row.Bounds != null),
                Completed: rebuildPreview.Completed && readyRows == sceneRows.Count && issues.Count == 0,
                Scenes: sceneRows,
                Issues: issues);
        }

        private static AssetMaterialImportPackageRebuildSceneModelRow BuildSceneRow(
            string fullPackageRoot,
            bool executeWrite,
            AssetMaterialImportPackageRebuildPreviewModelRow preview,
            List<AssetMaterialImportPackageRebuildSceneIssue> issues)
        {
            if (!preview.ReadyForRebuildPreview)
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("preview", preview.ObjRelativePath, preview.Status));
                return BuildBlockedSceneRow(preview, preview.Status);
            }

            if (!TryResolveInsidePackage(fullPackageRoot, preview.ObjRelativePath, out string fullObjPath) ||
                !TryResolveInsidePackage(fullPackageRoot, preview.BindingSidecarRelativePath, out string fullBindingPath) ||
                !File.Exists(fullObjPath) ||
                !File.Exists(fullBindingPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("preview", preview.ObjRelativePath, "missing-preview-file"));
                return BuildBlockedSceneRow(preview, "missing-preview-file");
            }

            if (!TryResolveInsidePackage(fullPackageRoot, preview.ModelInputRelativePath, out string fullModelInputPath) ||
                !File.Exists(fullModelInputPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("model", preview.ModelInputRelativePath, "missing-model-input-file"));
                return BuildBlockedSceneRow(preview, "missing-model-input-file");
            }

            if (!TryReadPreviewFiles(fullObjPath, fullBindingPath, out ParsedObjPreview parsedObj, out AssetMaterialImportPackageRebuildPreviewBindingSidecar? bindingSidecar))
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("preview", preview.ObjRelativePath, "invalid-preview-file"));
                return BuildBlockedSceneRow(preview, "invalid-preview-file");
            }

            AssetModelSummary modelSummary = FbxModelSummaryReader.Read(fullModelInputPath);
            if (!modelSummary.MetadataAvailable)
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("model", preview.ModelInputRelativePath, "invalid-model-metadata"));
                return BuildBlockedSceneRow(preview, "invalid-model-metadata");
            }

            string outputToken = BuildOutputToken(preview.Ordinal, preview.CatalogId);
            string sceneRelativePath = $"{WorkspaceRootRelativePath}/models/{outputToken}.scene.json";
            if (!TryResolveInsidePackage(fullPackageRoot, sceneRelativePath, out string fullScenePath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("scene", sceneRelativePath, "unsafe-output-path"));
                return BuildBlockedSceneRow(preview, "unsafe-output-path", sceneRelativePath);
            }

            AssetMaterialImportPackageRebuildSceneBounds bounds = new(
                MinX: parsedObj.MinX,
                MinY: parsedObj.MinY,
                MinZ: parsedObj.MinZ,
                MaxX: parsedObj.MaxX,
                MaxY: parsedObj.MaxY,
                MaxZ: parsedObj.MaxZ);
            IReadOnlyList<AssetMaterialImportPackageRebuildSceneTextureBinding> textures = (bindingSidecar?.Textures ?? [])
                .OrderBy(static texture => texture.Ordinal)
                .Select(static texture => new AssetMaterialImportPackageRebuildSceneTextureBinding(
                    texture.Ordinal,
                    texture.BindingFileName,
                    NormalizeRelativePath(texture.TextureInputRelativePath),
                    texture.Width,
                    texture.Height,
                    texture.ReadyForBinding))
                .ToList();
            AssetMaterialImportPackageRebuildSceneFile sceneFile = new(
                Schema: SceneFileSchema,
                CatalogId: preview.CatalogId,
                Label: preview.Label,
                SourceObjRelativePath: NormalizeRelativePath(preview.ObjRelativePath),
                SourceBindingSidecarRelativePath: NormalizeRelativePath(preview.BindingSidecarRelativePath),
                ModelInputRelativePath: NormalizeRelativePath(preview.ModelInputRelativePath),
                VertexCount: parsedObj.VertexCount,
                EdgeCount: parsedObj.EdgeCount,
                Bounds: bounds,
                MeshContract: BuildMeshContract(modelSummary),
                TextureBindingRows: textures.Count,
                Textures: textures);
            string sceneContent = JsonSerializer.Serialize(sceneFile, JsonOptions);
            bool sceneExists = File.Exists(fullScenePath);
            bool sceneMatches = sceneExists && string.Equals(File.ReadAllText(fullScenePath), sceneContent, StringComparison.Ordinal);
            if (sceneExists && !sceneMatches)
            {
                issues.Add(new AssetMaterialImportPackageRebuildSceneIssue("scene", sceneRelativePath, "blocked-existing-mismatch"));
                return BuildSceneRowResult(preview, sceneRelativePath, "blocked-existing-mismatch", parsedObj, textures.Count, bounds, BuildMeshContract(modelSummary));
            }

            string status;
            if (!executeWrite)
            {
                status = sceneExists ? "would-skip-existing" : "would-write";
            }
            else
            {
                Directory.CreateDirectory(Path.GetDirectoryName(fullScenePath)!);
                if (!sceneExists)
                {
                    File.WriteAllText(fullScenePath, sceneContent, Utf8NoBom);
                }

                status = sceneExists ? "skipped-existing" : "written";
            }

            return BuildSceneRowResult(preview, sceneRelativePath, status, parsedObj, textures.Count, bounds, BuildMeshContract(modelSummary));
        }

        private static AssetMaterialImportPackageRebuildSceneModelRow BuildBlockedSceneRow(
            AssetMaterialImportPackageRebuildPreviewModelRow preview,
            string status,
            string sceneRelativePath = "")
        {
            return new AssetMaterialImportPackageRebuildSceneModelRow(
                Ordinal: preview.Ordinal,
                CatalogId: preview.CatalogId,
                Label: preview.Label,
                ObjRelativePath: NormalizeRelativePath(preview.ObjRelativePath),
                BindingSidecarRelativePath: NormalizeRelativePath(preview.BindingSidecarRelativePath),
                SceneRelativePath: sceneRelativePath,
                TextureBindingRows: 0,
                VertexCount: 0,
                EdgeCount: 0,
                Bounds: null,
                MeshContract: null,
                Status: status,
                ReadyForSceneContract: false);
        }

        private static AssetMaterialImportPackageRebuildSceneModelRow BuildSceneRowResult(
            AssetMaterialImportPackageRebuildPreviewModelRow preview,
            string sceneRelativePath,
            string status,
            ParsedObjPreview parsedObj,
            int textureBindingRows,
            AssetMaterialImportPackageRebuildSceneBounds bounds,
            AssetMaterialImportPackageRebuildSceneMeshContract meshContract)
        {
            return new AssetMaterialImportPackageRebuildSceneModelRow(
                Ordinal: preview.Ordinal,
                CatalogId: preview.CatalogId,
                Label: preview.Label,
                ObjRelativePath: NormalizeRelativePath(preview.ObjRelativePath),
                BindingSidecarRelativePath: NormalizeRelativePath(preview.BindingSidecarRelativePath),
                SceneRelativePath: sceneRelativePath,
                TextureBindingRows: textureBindingRows,
                VertexCount: parsedObj.VertexCount,
                EdgeCount: parsedObj.EdgeCount,
                Bounds: bounds,
                MeshContract: meshContract,
                Status: status,
                ReadyForSceneContract: IsReadyStatus(status));
        }

        private static AssetMaterialImportPackageRebuildSceneMeshContract BuildMeshContract(AssetModelSummary summary)
        {
            return new AssetMaterialImportPackageRebuildSceneMeshContract(
                Format: summary.Format,
                FormatVersion: summary.FormatVersion,
                GeometryCount: summary.GeometryCount,
                ModelCount: summary.ModelCount,
                VertexCount: summary.VertexCount,
                PolygonIndexCount: summary.PolygonIndexCount,
                PreviewVertexCount: summary.GeometryPreview.Vertices.Count,
                PreviewEdgeCount: summary.GeometryPreview.Edges.Count,
                NormalCount: summary.NormalCount,
                NormalIndexCount: summary.NormalIndexCount,
                NormalMappingModes: summary.NormalMappingModes,
                NormalReferenceModes: summary.NormalReferenceModes,
                TextureCoordinateCount: summary.TextureCoordinateCount,
                TextureCoordinateIndexCount: summary.TextureCoordinateIndexCount,
                TextureCoordinateMappingModes: summary.TextureCoordinateMappingModes,
                TextureCoordinateReferenceModes: summary.TextureCoordinateReferenceModes,
                VertexColorCount: summary.VertexColorCount,
                VertexColorIndexCount: summary.VertexColorIndexCount,
                VertexColorMappingModes: summary.VertexColorMappingModes,
                VertexColorReferenceModes: summary.VertexColorReferenceModes,
                MaterialCount: summary.MaterialCount,
                TextureBindingCount: summary.TextureBindingCount,
                MaterialLayerCount: summary.MaterialLayerCount,
                MaterialAssignmentIndexCount: summary.MaterialAssignmentIndexCount,
                MaterialMappingModes: summary.MaterialMappingModes,
                MaterialReferenceModes: summary.MaterialReferenceModes,
                ObjectConnectionCount: summary.ObjectConnectionCount,
                PropertyConnectionCount: summary.PropertyConnectionCount,
                TextureToMaterialConnectionCount: summary.TextureToMaterialConnectionCount,
                TextureToMaterialSlotNames: summary.TextureToMaterialSlotNames,
                MaterialNames: summary.MaterialNames,
                TextureBindingNames: summary.TextureBindingNames,
                TextureBindingFileNames: summary.TextureBindingFileNames);
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeWrite,
            string fullPackageRoot,
            string packageRootName,
            AssetMaterialImportPackageRebuildPreviewResult rebuildPreview,
            IReadOnlyList<AssetMaterialImportPackageRebuildSceneModelRow> sceneRows,
            bool completed)
        {
            if (!executeWrite)
            {
                return (false, "preflight-not-written", 0);
            }

            string manifestPath = Path.Combine(fullPackageRoot, ManifestFileName);
            AssetMaterialImportPackageRebuildSceneManifest manifest = new(
                Schema: ManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                PackageRootName: packageRootName,
                SourceRebuildPreviewManifestRelativePath: rebuildPreview.ManifestRelativePath,
                WorkspaceRootRelativePath: WorkspaceRootRelativePath,
                SourceModelPreviewRows: rebuildPreview.ModelPreviewRows,
                SourceObjFileRows: rebuildPreview.ObjFileRows,
                SourceBindingSidecarRows: rebuildPreview.BindingSidecarRows,
                SceneRows: sceneRows.Count,
                ReadySceneRows: sceneRows.Count(static row => row.ReadyForSceneContract),
                TextureBindingRows: sceneRows.Sum(static row => row.TextureBindingRows),
                SceneVertexRows: sceneRows.Sum(static row => row.VertexCount),
                SceneEdgeRows: sceneRows.Sum(static row => row.EdgeCount),
                FbxVertexRows: sceneRows.Sum(static row => row.MeshContract?.VertexCount ?? 0),
                FbxPolygonIndexRows: sceneRows.Sum(static row => row.MeshContract?.PolygonIndexCount ?? 0),
                FbxNormalRows: sceneRows.Sum(static row => row.MeshContract?.NormalCount ?? 0),
                FbxTextureCoordinateRows: sceneRows.Sum(static row => row.MeshContract?.TextureCoordinateCount ?? 0),
                MaterialRows: sceneRows.Sum(static row => row.MeshContract?.MaterialCount ?? 0),
                TextureToMaterialConnectionRows: sceneRows.Sum(static row => row.MeshContract?.TextureToMaterialConnectionCount ?? 0),
                Completed: completed,
                Scenes: sceneRows.OrderBy(static row => row.Ordinal).ToList());
            File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, JsonOptions), Utf8NoBom);
            return (true, "written", new FileInfo(manifestPath).Length);
        }

        private static bool TryReadPreviewFiles(
            string fullObjPath,
            string fullBindingPath,
            out ParsedObjPreview parsedObj,
            out AssetMaterialImportPackageRebuildPreviewBindingSidecar? bindingSidecar)
        {
            parsedObj = default;
            bindingSidecar = null;
            if (!TryParseObj(File.ReadAllLines(fullObjPath), out parsedObj))
            {
                return false;
            }

            try
            {
                bindingSidecar = JsonSerializer.Deserialize<AssetMaterialImportPackageRebuildPreviewBindingSidecar>(
                    File.ReadAllText(fullBindingPath),
                    JsonOptions);
            }
            catch (JsonException)
            {
                return false;
            }

            return bindingSidecar != null &&
                   string.Equals(bindingSidecar.Schema, "onslaught.asset-material-package-rebuild-preview-bindings.v1", StringComparison.Ordinal);
        }

        private static bool TryParseObj(IReadOnlyList<string> lines, out ParsedObjPreview parsedObj)
        {
            int vertexCount = 0;
            int edgeCount = 0;
            double minX = 0;
            double minY = 0;
            double minZ = 0;
            double maxX = 0;
            double maxY = 0;
            double maxZ = 0;
            foreach (string rawLine in lines)
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith('#'))
                {
                    continue;
                }

                if (line.StartsWith("v ", StringComparison.Ordinal))
                {
                    string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                    if (parts.Length != 4 ||
                        !double.TryParse(parts[1], NumberStyles.Float, CultureInfo.InvariantCulture, out double x) ||
                        !double.TryParse(parts[2], NumberStyles.Float, CultureInfo.InvariantCulture, out double y) ||
                        !double.TryParse(parts[3], NumberStyles.Float, CultureInfo.InvariantCulture, out double z))
                    {
                        parsedObj = default;
                        return false;
                    }

                    if (vertexCount == 0)
                    {
                        minX = maxX = x;
                        minY = maxY = y;
                        minZ = maxZ = z;
                    }
                    else
                    {
                        minX = Math.Min(minX, x);
                        minY = Math.Min(minY, y);
                        minZ = Math.Min(minZ, z);
                        maxX = Math.Max(maxX, x);
                        maxY = Math.Max(maxY, y);
                        maxZ = Math.Max(maxZ, z);
                    }

                    vertexCount++;
                    continue;
                }

                if (line.StartsWith("l ", StringComparison.Ordinal))
                {
                    string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length != 3 ||
                    !int.TryParse(parts[1], NumberStyles.Integer, CultureInfo.InvariantCulture, out int start) ||
                    !int.TryParse(parts[2], NumberStyles.Integer, CultureInfo.InvariantCulture, out int end) ||
                    start < 1 ||
                    end < 1 ||
                    start > vertexCount ||
                    end > vertexCount)
                {
                    parsedObj = default;
                    return false;
                    }

                    edgeCount++;
                }
            }

            if (vertexCount == 0 || edgeCount == 0)
            {
                parsedObj = default;
                return false;
            }

            parsedObj = new ParsedObjPreview(vertexCount, edgeCount, minX, minY, minZ, maxX, maxY, maxZ);
            return true;
        }

        private static string BuildOutputToken(int ordinal, string catalogId)
        {
            return $"{ordinal:0000}-{SanitizeToken(catalogId)}";
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

        private static string NormalizeRelativePath(string value)
        {
            return value.Replace('\\', '/');
        }

        private static bool IsReadyStatus(string status)
        {
            return status is "would-write" or "would-skip-existing" or "written" or "skipped-existing";
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private readonly record struct ParsedObjPreview(
            int VertexCount,
            int EdgeCount,
            double MinX,
            double MinY,
            double MinZ,
            double MaxX,
            double MaxY,
            double MaxZ);
    }

    public sealed record AssetMaterialImportPackageRebuildSceneResult(
        bool Executed,
        string PackageRootName,
        string SourceRebuildPreviewManifestRelativePath,
        string SourceRebuildPreviewStatus,
        bool SourceRebuildPreviewCompleted,
        string WorkspaceRootRelativePath,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        int SourceModelPreviewRows,
        int SourceObjFileRows,
        int SourceBindingSidecarRows,
        int SceneRows,
        int ReadySceneRows,
        int BlockedSceneRows,
        int WouldWriteSceneRows,
        int WrittenSceneRows,
        int ExistingSceneRows,
        int BlockedExistingMismatches,
        int MissingPreviewFiles,
        int MissingModelInputFiles,
        int InvalidPreviewFiles,
        int UnsafeOutputPaths,
        int TextureBindingRows,
        int SceneVertexRows,
        int SceneEdgeRows,
        int FbxVertexRows,
        int FbxPolygonIndexRows,
        int FbxNormalRows,
        int FbxTextureCoordinateRows,
        int MaterialRows,
        int TextureToMaterialConnectionRows,
        int SceneBoundsRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildSceneModelRow> Scenes,
        IReadOnlyList<AssetMaterialImportPackageRebuildSceneIssue> Issues);

    public sealed record AssetMaterialImportPackageRebuildSceneModelRow(
        int Ordinal,
        string CatalogId,
        string Label,
        string ObjRelativePath,
        string BindingSidecarRelativePath,
        string SceneRelativePath,
        int TextureBindingRows,
        int VertexCount,
        int EdgeCount,
        AssetMaterialImportPackageRebuildSceneBounds? Bounds,
        AssetMaterialImportPackageRebuildSceneMeshContract? MeshContract,
        string Status,
        bool ReadyForSceneContract);

    public sealed record AssetMaterialImportPackageRebuildSceneIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageRebuildSceneBounds(
        double MinX,
        double MinY,
        double MinZ,
        double MaxX,
        double MaxY,
        double MaxZ);

    public sealed record AssetMaterialImportPackageRebuildSceneTextureBinding(
        int Ordinal,
        string BindingFileName,
        string TextureInputRelativePath,
        int? Width,
        int? Height,
        bool ReadyForBinding);

    public sealed record AssetMaterialImportPackageRebuildSceneFile(
        string Schema,
        string CatalogId,
        string Label,
        string SourceObjRelativePath,
        string SourceBindingSidecarRelativePath,
        string ModelInputRelativePath,
        int VertexCount,
        int EdgeCount,
        AssetMaterialImportPackageRebuildSceneBounds Bounds,
        AssetMaterialImportPackageRebuildSceneMeshContract MeshContract,
        int TextureBindingRows,
        IReadOnlyList<AssetMaterialImportPackageRebuildSceneTextureBinding> Textures);

    public sealed record AssetMaterialImportPackageRebuildSceneMeshContract(
        string Format,
        int? FormatVersion,
        int GeometryCount,
        int ModelCount,
        int VertexCount,
        int PolygonIndexCount,
        int PreviewVertexCount,
        int PreviewEdgeCount,
        int NormalCount,
        int NormalIndexCount,
        IReadOnlyList<string> NormalMappingModes,
        IReadOnlyList<string> NormalReferenceModes,
        int TextureCoordinateCount,
        int TextureCoordinateIndexCount,
        IReadOnlyList<string> TextureCoordinateMappingModes,
        IReadOnlyList<string> TextureCoordinateReferenceModes,
        int VertexColorCount,
        int VertexColorIndexCount,
        IReadOnlyList<string> VertexColorMappingModes,
        IReadOnlyList<string> VertexColorReferenceModes,
        int MaterialCount,
        int TextureBindingCount,
        int MaterialLayerCount,
        int MaterialAssignmentIndexCount,
        IReadOnlyList<string> MaterialMappingModes,
        IReadOnlyList<string> MaterialReferenceModes,
        int ObjectConnectionCount,
        int PropertyConnectionCount,
        int TextureToMaterialConnectionCount,
        IReadOnlyList<string> TextureToMaterialSlotNames,
        IReadOnlyList<string> MaterialNames,
        IReadOnlyList<string> TextureBindingNames,
        IReadOnlyList<string> TextureBindingFileNames);

    public sealed record AssetMaterialImportPackageRebuildSceneManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        string PackageRootName,
        string SourceRebuildPreviewManifestRelativePath,
        string WorkspaceRootRelativePath,
        int SourceModelPreviewRows,
        int SourceObjFileRows,
        int SourceBindingSidecarRows,
        int SceneRows,
        int ReadySceneRows,
        int TextureBindingRows,
        int SceneVertexRows,
        int SceneEdgeRows,
        int FbxVertexRows,
        int FbxPolygonIndexRows,
        int FbxNormalRows,
        int FbxTextureCoordinateRows,
        int MaterialRows,
        int TextureToMaterialConnectionRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildSceneModelRow> Scenes);
}
