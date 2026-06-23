using System.Globalization;
using System.Text;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageRebuildMeshImportService
    {
        public const string ManifestFileName = "material-package-rebuild-mesh-import.v1.json";
        public const string ManifestSchema = "onslaught.asset-material-package-rebuild-mesh-import.v1";

        private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
        {
            PropertyNameCaseInsensitive = true,
            WriteIndented = true
        };
        private static readonly UTF8Encoding Utf8NoBom = new(encoderShouldEmitUTF8Identifier: false);

        public AssetMaterialImportPackageRebuildMeshImportResult Preflight(string packageRoot)
        {
            return Build(packageRoot, executeWrite: false);
        }

        public AssetMaterialImportPackageRebuildMeshImportResult Materialize(string packageRoot)
        {
            return Build(packageRoot, executeWrite: true);
        }

        private static AssetMaterialImportPackageRebuildMeshImportResult Build(string packageRoot, bool executeWrite)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            string packageRootName = BuildRootName(fullPackageRoot);
            string sourceManifestRelativePath = AssetMaterialImportPackageRebuildMeshService.ManifestFileName;
            string sourceManifestPath = Path.Combine(fullPackageRoot, sourceManifestRelativePath);
            List<AssetMaterialImportPackageRebuildMeshImportIssue> issues = [];

            if (!File.Exists(sourceManifestPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("manifest", sourceManifestRelativePath, "missing-rebuild-mesh-manifest"));
                return BuildResult(
                    executeWrite,
                    packageRootName,
                    sourceManifestRelativePath,
                    "missing-rebuild-mesh-manifest",
                    sourceCompleted: false,
                    manifestWritten: false,
                    manifestStatus: executeWrite ? "not-written" : "preflight-not-written",
                    manifestBytes: 0,
                    rows: [],
                    issues);
            }

            if (!TryReadSourceManifest(sourceManifestPath, out AssetMaterialImportPackageRebuildMeshManifest? sourceManifest) ||
                sourceManifest == null)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("manifest", sourceManifestRelativePath, "invalid-rebuild-mesh-manifest"));
                return BuildResult(
                    executeWrite,
                    packageRootName,
                    sourceManifestRelativePath,
                    "invalid-rebuild-mesh-manifest",
                    sourceCompleted: false,
                    manifestWritten: false,
                    manifestStatus: executeWrite ? "not-written" : "preflight-not-written",
                    manifestBytes: 0,
                    rows: [],
                    issues);
            }

            List<AssetMaterialImportPackageRebuildMeshImportRow> rows = sourceManifest.Meshes
                .OrderBy(static row => row.Ordinal)
                .Select(row => BuildImportRow(fullPackageRoot, row, issues))
                .ToList();
            bool completed = sourceManifest.Completed &&
                             rows.All(static row => row.ReadyForRebuildConsumer) &&
                             issues.Count == 0;
            (bool manifestWritten, string manifestStatus, long manifestBytes) =
                WriteManifestIfRequested(executeWrite, fullPackageRoot, packageRootName, sourceManifestRelativePath, sourceManifest, rows, completed);

            return BuildResult(
                executeWrite,
                packageRootName,
                sourceManifestRelativePath,
                sourceManifest.Completed ? "ready" : "source-incomplete",
                sourceManifest.Completed,
                manifestWritten,
                manifestStatus,
                manifestBytes,
                rows,
                issues);
        }

        private static AssetMaterialImportPackageRebuildMeshImportResult BuildResult(
            bool executeWrite,
            string packageRootName,
            string sourceManifestRelativePath,
            string sourceManifestStatus,
            bool sourceCompleted,
            bool manifestWritten,
            string manifestStatus,
            long manifestBytes,
            IReadOnlyList<AssetMaterialImportPackageRebuildMeshImportRow> rows,
            IReadOnlyList<AssetMaterialImportPackageRebuildMeshImportIssue> issues)
        {
            int readyRows = rows.Count(static row => row.ReadyForRebuildConsumer);
            return new AssetMaterialImportPackageRebuildMeshImportResult(
                Executed: executeWrite,
                PackageRootName: packageRootName,
                SourceRebuildMeshManifestRelativePath: sourceManifestRelativePath,
                SourceRebuildMeshStatus: sourceManifestStatus,
                SourceRebuildMeshCompleted: sourceCompleted,
                ManifestRelativePath: ManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                ImportRows: rows.Count,
                ReadyImportRows: readyRows,
                BlockedImportRows: rows.Count - readyRows,
                ObjParsedRows: rows.Count(static row => row.ObjParsed),
                MtlParsedRows: rows.Count(static row => row.MtlParsed),
                ObjFileRows: rows.Count(static row => !string.IsNullOrWhiteSpace(row.ObjRelativePath)),
                MtlFileRows: rows.Count(static row => !string.IsNullOrWhiteSpace(row.MtlRelativePath)),
                VertexRows: rows.Sum(static row => row.VertexCount),
                FaceRows: rows.Sum(static row => row.FaceCount),
                NormalRows: rows.Sum(static row => row.NormalCount),
                TextureCoordinateRows: rows.Sum(static row => row.TextureCoordinateCount),
                MaterialRows: rows.Sum(static row => row.MaterialCount),
                FaceMaterialUseRows: rows.Sum(static row => row.FaceMaterialUseRows),
                TexturedMaterialRows: rows.Sum(static row => row.TexturedMaterialRows),
                TextureReferenceRows: rows.Sum(static row => row.TextureReferenceRows),
                MissingTextureRows: rows.Sum(static row => row.MissingTextureRows),
                CountMismatchRows: rows.Count(static row => row.CountMismatch),
                UndefinedMaterialUseRows: rows.Sum(static row => row.UndefinedMaterialUseRows),
                UnsafePathRows: rows.Sum(static row => row.UnsafePathRows),
                Completed: sourceCompleted && readyRows == rows.Count && issues.Count == 0,
                Rows: rows,
                Issues: issues);
        }

        private static AssetMaterialImportPackageRebuildMeshImportRow BuildImportRow(
            string fullPackageRoot,
            AssetMaterialImportPackageRebuildMeshModelRow mesh,
            List<AssetMaterialImportPackageRebuildMeshImportIssue> issues)
        {
            if (!mesh.ReadyForMeshExport)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("mesh", mesh.ObjRelativePath, "source-mesh-not-ready"));
                return BlockedRow(mesh, "source-mesh-not-ready");
            }

            if (!TryResolveInsidePackage(fullPackageRoot, mesh.ObjRelativePath, out string fullObjPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("mesh", mesh.ObjRelativePath, "unsafe-obj-path"));
                return BlockedRow(mesh, "unsafe-obj-path", unsafePathRows: 1);
            }

            if (!TryResolveInsidePackage(fullPackageRoot, mesh.MtlRelativePath, out string fullMtlPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("mesh", mesh.MtlRelativePath, "unsafe-mtl-path"));
                return BlockedRow(mesh, "unsafe-mtl-path", unsafePathRows: 1);
            }

            if (!File.Exists(fullObjPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("mesh", mesh.ObjRelativePath, "missing-obj-file"));
                return BlockedRow(mesh, "missing-obj-file");
            }

            if (!File.Exists(fullMtlPath))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("mesh", mesh.MtlRelativePath, "missing-mtl-file"));
                return BlockedRow(mesh, "missing-mtl-file");
            }

            ObjParseResult obj = ParseObj(fullObjPath, Path.GetFileName(mesh.MtlRelativePath));
            MtlParseResult mtl = ParseMtl(fullPackageRoot, fullMtlPath);
            List<string> rowIssues = [];
            rowIssues.AddRange(obj.Issues);
            rowIssues.AddRange(mtl.Issues);

            bool countMismatch =
                obj.VertexCount != mesh.VertexCount ||
                obj.FaceCount != mesh.FaceCount ||
                obj.NormalCount != mesh.NormalCount ||
                obj.TextureCoordinateCount != mesh.TextureCoordinateCount ||
                mtl.MaterialCount != mesh.MaterialCount;
            if (countMismatch)
            {
                rowIssues.Add("count-mismatch");
            }

            int undefinedMaterialUseRows = obj.MaterialNamesUsed.Count(name => !mtl.MaterialNames.Contains(name));
            if (undefinedMaterialUseRows > 0)
            {
                rowIssues.Add("undefined-material-use");
            }

            string status = rowIssues.Count == 0 ? "ready-for-rebuild-consumer" : rowIssues[0];
            foreach (string statusIssue in rowIssues.Distinct(StringComparer.Ordinal))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshImportIssue("mesh", mesh.ObjRelativePath, statusIssue));
            }

            int unsafePathRows = obj.UnsafePathRows + mtl.UnsafePathRows;
            return new AssetMaterialImportPackageRebuildMeshImportRow(
                Ordinal: mesh.Ordinal,
                CatalogId: mesh.CatalogId,
                Label: mesh.Label,
                ObjRelativePath: NormalizeRelativePath(mesh.ObjRelativePath),
                MtlRelativePath: NormalizeRelativePath(mesh.MtlRelativePath),
                ObjParsed: obj.Parsed,
                MtlParsed: mtl.Parsed,
                VertexCount: obj.VertexCount,
                FaceCount: obj.FaceCount,
                NormalCount: obj.NormalCount,
                TextureCoordinateCount: obj.TextureCoordinateCount,
                MaterialCount: mtl.MaterialCount,
                FaceMaterialUseRows: obj.FaceMaterialUseRows,
                TexturedMaterialRows: mtl.TexturedMaterialRows,
                TextureReferenceRows: mtl.TextureReferenceRows,
                MissingTextureRows: mtl.MissingTextureRows,
                CountMismatch: countMismatch,
                UndefinedMaterialUseRows: undefinedMaterialUseRows,
                UnsafePathRows: unsafePathRows,
                Status: status,
                ReadyForRebuildConsumer: rowIssues.Count == 0);
        }

        private static AssetMaterialImportPackageRebuildMeshImportRow BlockedRow(
            AssetMaterialImportPackageRebuildMeshModelRow mesh,
            string status,
            int unsafePathRows = 0)
        {
            return new AssetMaterialImportPackageRebuildMeshImportRow(
                Ordinal: mesh.Ordinal,
                CatalogId: mesh.CatalogId,
                Label: mesh.Label,
                ObjRelativePath: NormalizeRelativePath(mesh.ObjRelativePath),
                MtlRelativePath: NormalizeRelativePath(mesh.MtlRelativePath),
                ObjParsed: false,
                MtlParsed: false,
                VertexCount: 0,
                FaceCount: 0,
                NormalCount: 0,
                TextureCoordinateCount: 0,
                MaterialCount: 0,
                FaceMaterialUseRows: 0,
                TexturedMaterialRows: 0,
                TextureReferenceRows: 0,
                MissingTextureRows: 0,
                CountMismatch: false,
                UndefinedMaterialUseRows: 0,
                UnsafePathRows: unsafePathRows,
                Status: status,
                ReadyForRebuildConsumer: false);
        }

        private static ObjParseResult ParseObj(string fullObjPath, string expectedMtlFileName)
        {
            int vertexCount = 0;
            int textureCoordinateCount = 0;
            int normalCount = 0;
            int faceCount = 0;
            int faceMaterialUseRows = 0;
            int unsafePathRows = 0;
            string activeMaterial = string.Empty;
            bool sawExpectedMtl = false;
            HashSet<string> materialNamesUsed = new(StringComparer.Ordinal);
            List<string> issues = [];

            foreach (string rawLine in File.ReadLines(fullObjPath))
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith('#'))
                {
                    continue;
                }

                string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length == 0)
                {
                    continue;
                }

                switch (parts[0])
                {
                    case "mtllib":
                        if (parts.Length != 2 ||
                            Path.IsPathRooted(parts[1]) ||
                            !string.Equals(parts[1], expectedMtlFileName, StringComparison.Ordinal))
                        {
                            unsafePathRows++;
                            issues.Add("mtllib-mismatch");
                        }
                        else
                        {
                            sawExpectedMtl = true;
                        }

                        break;
                    case "o":
                        break;
                    case "v":
                        if (!TryParseFloatVector(parts, 3))
                        {
                            issues.Add("invalid-vertex-row");
                        }

                        vertexCount++;
                        break;
                    case "vt":
                        if (!TryParseFloatVector(parts, 2))
                        {
                            issues.Add("invalid-texture-coordinate-row");
                        }

                        textureCoordinateCount++;
                        break;
                    case "vn":
                        if (!TryParseFloatVector(parts, 3))
                        {
                            issues.Add("invalid-normal-row");
                        }

                        normalCount++;
                        break;
                    case "usemtl":
                        if (parts.Length < 2)
                        {
                            issues.Add("empty-material-use");
                        }
                        else
                        {
                            activeMaterial = parts[1];
                        }

                        break;
                    case "f":
                        if (parts.Length < 4)
                        {
                            issues.Add("invalid-face-row");
                            break;
                        }

                        if (string.IsNullOrWhiteSpace(activeMaterial))
                        {
                            issues.Add("face-without-material");
                        }
                        else
                        {
                            faceMaterialUseRows++;
                            materialNamesUsed.Add(activeMaterial);
                        }

                        for (int index = 1; index < parts.Length; index++)
                        {
                            if (!TryParseFaceToken(parts[index], vertexCount, textureCoordinateCount, normalCount))
                            {
                                issues.Add("invalid-face-index");
                                break;
                            }
                        }

                        faceCount++;
                        break;
                    default:
                        issues.Add("unsupported-obj-row");
                        break;
                }
            }

            if (!sawExpectedMtl)
            {
                issues.Add("missing-mtllib");
            }

            return new ObjParseResult(
                Parsed: issues.Count == 0,
                VertexCount: vertexCount,
                FaceCount: faceCount,
                NormalCount: normalCount,
                TextureCoordinateCount: textureCoordinateCount,
                FaceMaterialUseRows: faceMaterialUseRows,
                UnsafePathRows: unsafePathRows,
                MaterialNamesUsed: materialNamesUsed,
                Issues: issues);
        }

        private static MtlParseResult ParseMtl(string fullPackageRoot, string fullMtlPath)
        {
            HashSet<string> materialNames = new(StringComparer.Ordinal);
            int texturedMaterialRows = 0;
            int textureReferenceRows = 0;
            int missingTextureRows = 0;
            int unsafePathRows = 0;
            bool insideMaterial = false;
            List<string> issues = [];

            foreach (string rawLine in File.ReadLines(fullMtlPath))
            {
                string line = rawLine.Trim();
                if (line.Length == 0 || line.StartsWith('#'))
                {
                    continue;
                }

                if (line.StartsWith("newmtl ", StringComparison.Ordinal))
                {
                    string name = line["newmtl ".Length..].Trim();
                    if (string.IsNullOrWhiteSpace(name))
                    {
                        issues.Add("empty-material-name");
                    }
                    else
                    {
                        materialNames.Add(name);
                        insideMaterial = true;
                    }

                    continue;
                }

                if (line.StartsWith("Kd ", StringComparison.Ordinal))
                {
                    string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                    if (parts.Length != 4 || !TryParseFloatValues(parts, 1, 3))
                    {
                        issues.Add("invalid-diffuse-color");
                    }

                    continue;
                }

                if (line.StartsWith("map_Kd ", StringComparison.Ordinal))
                {
                    string texturePath = NormalizeRelativePath(line["map_Kd ".Length..].Trim());
                    textureReferenceRows++;
                    if (!insideMaterial)
                    {
                        issues.Add("texture-without-material");
                    }

                    if (!texturePath.StartsWith("importer-input/textures/", StringComparison.OrdinalIgnoreCase) ||
                        !TryResolveInsidePackage(fullPackageRoot, texturePath, out string fullTexturePath))
                    {
                        unsafePathRows++;
                        issues.Add("unsafe-texture-path");
                        continue;
                    }

                    if (!File.Exists(fullTexturePath))
                    {
                        missingTextureRows++;
                        issues.Add("missing-texture-file");
                    }

                    texturedMaterialRows++;
                    continue;
                }

                issues.Add("unsupported-mtl-row");
            }

            return new MtlParseResult(
                Parsed: issues.Count == 0,
                MaterialCount: materialNames.Count,
                TexturedMaterialRows: texturedMaterialRows,
                TextureReferenceRows: textureReferenceRows,
                MissingTextureRows: missingTextureRows,
                UnsafePathRows: unsafePathRows,
                MaterialNames: materialNames,
                Issues: issues);
        }

        private static bool TryParseFaceToken(string token, int vertexCount, int textureCoordinateCount, int normalCount)
        {
            string[] parts = token.Split('/');
            if (parts.Length is < 1 or > 3)
            {
                return false;
            }

            if (!TryParsePositiveIndex(parts[0], vertexCount, required: true))
            {
                return false;
            }

            if (parts.Length >= 2 && !TryParsePositiveIndex(parts[1], textureCoordinateCount, required: false))
            {
                return false;
            }

            if (parts.Length == 3 && !TryParsePositiveIndex(parts[2], normalCount, required: false))
            {
                return false;
            }

            return true;
        }

        private static bool TryParsePositiveIndex(string value, int maxValue, bool required)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return !required;
            }

            return int.TryParse(value, NumberStyles.Integer, CultureInfo.InvariantCulture, out int index) &&
                   index > 0 &&
                   index <= maxValue;
        }

        private static bool TryParseFloatVector(string[] parts, int valueCount)
        {
            return parts.Length == valueCount + 1 && TryParseFloatValues(parts, 1, valueCount);
        }

        private static bool TryParseFloatValues(string[] parts, int startIndex, int valueCount)
        {
            for (int index = startIndex; index < startIndex + valueCount; index++)
            {
                if (!double.TryParse(parts[index], NumberStyles.Float, CultureInfo.InvariantCulture, out _))
                {
                    return false;
                }
            }

            return true;
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeWrite,
            string fullPackageRoot,
            string packageRootName,
            string sourceManifestRelativePath,
            AssetMaterialImportPackageRebuildMeshManifest sourceManifest,
            IReadOnlyList<AssetMaterialImportPackageRebuildMeshImportRow> rows,
            bool completed)
        {
            if (!executeWrite)
            {
                return (false, "preflight-not-written", 0);
            }

            string manifestPath = Path.Combine(fullPackageRoot, ManifestFileName);
            AssetMaterialImportPackageRebuildMeshImportManifest manifest = new(
                Schema: ManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                PackageRootName: packageRootName,
                SourceRebuildMeshManifestRelativePath: sourceManifestRelativePath,
                SourceMeshRows: sourceManifest.MeshRows,
                ImportRows: rows.Count,
                ReadyImportRows: rows.Count(static row => row.ReadyForRebuildConsumer),
                ObjParsedRows: rows.Count(static row => row.ObjParsed),
                MtlParsedRows: rows.Count(static row => row.MtlParsed),
                VertexRows: rows.Sum(static row => row.VertexCount),
                FaceRows: rows.Sum(static row => row.FaceCount),
                NormalRows: rows.Sum(static row => row.NormalCount),
                TextureCoordinateRows: rows.Sum(static row => row.TextureCoordinateCount),
                MaterialRows: rows.Sum(static row => row.MaterialCount),
                FaceMaterialUseRows: rows.Sum(static row => row.FaceMaterialUseRows),
                TexturedMaterialRows: rows.Sum(static row => row.TexturedMaterialRows),
                TextureReferenceRows: rows.Sum(static row => row.TextureReferenceRows),
                MissingTextureRows: rows.Sum(static row => row.MissingTextureRows),
                CountMismatchRows: rows.Count(static row => row.CountMismatch),
                UndefinedMaterialUseRows: rows.Sum(static row => row.UndefinedMaterialUseRows),
                UnsafePathRows: rows.Sum(static row => row.UnsafePathRows),
                Completed: completed,
                Rows: rows.OrderBy(static row => row.Ordinal).ToList());
            File.WriteAllText(manifestPath, JsonSerializer.Serialize(manifest, JsonOptions), Utf8NoBom);
            return (true, "written", new FileInfo(manifestPath).Length);
        }

        private static bool TryReadSourceManifest(
            string sourceManifestPath,
            out AssetMaterialImportPackageRebuildMeshManifest? sourceManifest)
        {
            sourceManifest = null;
            try
            {
                sourceManifest = JsonSerializer.Deserialize<AssetMaterialImportPackageRebuildMeshManifest>(
                    File.ReadAllText(sourceManifestPath),
                    JsonOptions);
            }
            catch (JsonException)
            {
                return false;
            }

            return sourceManifest != null &&
                   string.Equals(sourceManifest.Schema, AssetMaterialImportPackageRebuildMeshService.ManifestSchema, StringComparison.Ordinal);
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

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }

        private sealed record ObjParseResult(
            bool Parsed,
            int VertexCount,
            int FaceCount,
            int NormalCount,
            int TextureCoordinateCount,
            int FaceMaterialUseRows,
            int UnsafePathRows,
            IReadOnlySet<string> MaterialNamesUsed,
            IReadOnlyList<string> Issues);

        private sealed record MtlParseResult(
            bool Parsed,
            int MaterialCount,
            int TexturedMaterialRows,
            int TextureReferenceRows,
            int MissingTextureRows,
            int UnsafePathRows,
            IReadOnlySet<string> MaterialNames,
            IReadOnlyList<string> Issues);
    }

    public sealed record AssetMaterialImportPackageRebuildMeshImportResult(
        bool Executed,
        string PackageRootName,
        string SourceRebuildMeshManifestRelativePath,
        string SourceRebuildMeshStatus,
        bool SourceRebuildMeshCompleted,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        int ImportRows,
        int ReadyImportRows,
        int BlockedImportRows,
        int ObjParsedRows,
        int MtlParsedRows,
        int ObjFileRows,
        int MtlFileRows,
        int VertexRows,
        int FaceRows,
        int NormalRows,
        int TextureCoordinateRows,
        int MaterialRows,
        int FaceMaterialUseRows,
        int TexturedMaterialRows,
        int TextureReferenceRows,
        int MissingTextureRows,
        int CountMismatchRows,
        int UndefinedMaterialUseRows,
        int UnsafePathRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildMeshImportRow> Rows,
        IReadOnlyList<AssetMaterialImportPackageRebuildMeshImportIssue> Issues);

    public sealed record AssetMaterialImportPackageRebuildMeshImportRow(
        int Ordinal,
        string CatalogId,
        string Label,
        string ObjRelativePath,
        string MtlRelativePath,
        bool ObjParsed,
        bool MtlParsed,
        int VertexCount,
        int FaceCount,
        int NormalCount,
        int TextureCoordinateCount,
        int MaterialCount,
        int FaceMaterialUseRows,
        int TexturedMaterialRows,
        int TextureReferenceRows,
        int MissingTextureRows,
        bool CountMismatch,
        int UndefinedMaterialUseRows,
        int UnsafePathRows,
        string Status,
        bool ReadyForRebuildConsumer);

    public sealed record AssetMaterialImportPackageRebuildMeshImportIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageRebuildMeshImportManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        string PackageRootName,
        string SourceRebuildMeshManifestRelativePath,
        int SourceMeshRows,
        int ImportRows,
        int ReadyImportRows,
        int ObjParsedRows,
        int MtlParsedRows,
        int VertexRows,
        int FaceRows,
        int NormalRows,
        int TextureCoordinateRows,
        int MaterialRows,
        int FaceMaterialUseRows,
        int TexturedMaterialRows,
        int TextureReferenceRows,
        int MissingTextureRows,
        int CountMismatchRows,
        int UndefinedMaterialUseRows,
        int UnsafePathRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildMeshImportRow> Rows);
}
