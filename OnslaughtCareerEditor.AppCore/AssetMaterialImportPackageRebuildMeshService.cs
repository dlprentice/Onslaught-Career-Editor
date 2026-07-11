using System.Globalization;
using System.Text;
using System.Text.Json;

namespace Onslaught___Career_Editor
{
    public sealed class AssetMaterialImportPackageRebuildMeshService
    {
        public const string WorkspaceRootRelativePath = "rebuild-mesh";
        public const string ManifestFileName = "material-package-rebuild-mesh.v1.json";
        public const string ManifestSchema = "onslaught.asset-material-package-rebuild-mesh.v1";

        private static readonly JsonSerializerOptions JsonOptions = new(JsonSerializerDefaults.Web)
        {
            PropertyNameCaseInsensitive = true,
            WriteIndented = true
        };
        private static readonly UTF8Encoding Utf8NoBom = new(encoderShouldEmitUTF8Identifier: false);

        public AssetMaterialImportPackageRebuildMeshResult Preflight(string packageRoot)
        {
            return Build(packageRoot, executeWrite: false);
        }

        public AssetMaterialImportPackageRebuildMeshResult Materialize(string packageRoot)
        {
            return Build(packageRoot, executeWrite: true);
        }

        private static AssetMaterialImportPackageRebuildMeshResult Build(string packageRoot, bool executeWrite)
        {
            string fullPackageRoot = Path.GetFullPath(packageRoot);
            using GuardedPackageOutputRoot? operationRoot = Directory.Exists(fullPackageRoot)
                ? new GuardedPackageOutputRoot(
                    fullPackageRoot,
                    trustedSourceRoot: null,
                    execute: false,
                    requireExistingRoot: true)
                : null;
            string packageRootName = BuildRootName(fullPackageRoot);
            AssetMaterialImportPackageRebuildSceneResult rebuildScene =
                new AssetMaterialImportPackageRebuildSceneService().Preflight(fullPackageRoot);
            List<AssetMaterialImportPackageRebuildMeshIssue> issues = rebuildScene.Issues
                .Select(static issue => new AssetMaterialImportPackageRebuildMeshIssue(
                    issue.Role,
                    issue.RelativePath,
                    issue.Status))
                .ToList();

            List<AssetMaterialImportPackageRebuildMeshModelRow> meshRows = rebuildScene.Scenes
                .OrderBy(static scene => scene.Ordinal)
                .Select(scene => BuildMeshRow(fullPackageRoot, executeWrite, scene, issues))
                .ToList();

            bool completed = rebuildScene.Completed &&
                             meshRows.All(static row => IsReadyStatus(row.Status)) &&
                             issues.Count == 0;
            (bool manifestWritten, string manifestStatus, long manifestBytes) =
                WriteManifestIfRequested(executeWrite, fullPackageRoot, packageRootName, rebuildScene, meshRows, completed);

            return BuildResult(
                executeWrite,
                packageRootName,
                rebuildScene,
                manifestWritten,
                manifestStatus,
                manifestBytes,
                meshRows,
                issues);
        }

        private static AssetMaterialImportPackageRebuildMeshResult BuildResult(
            bool executeWrite,
            string packageRootName,
            AssetMaterialImportPackageRebuildSceneResult rebuildScene,
            bool manifestWritten,
            string manifestStatus,
            long manifestBytes,
            IReadOnlyList<AssetMaterialImportPackageRebuildMeshModelRow> meshRows,
            IReadOnlyList<AssetMaterialImportPackageRebuildMeshIssue> issues)
        {
            int readyRows = meshRows.Count(static row => IsReadyStatus(row.Status));
            return new AssetMaterialImportPackageRebuildMeshResult(
                Executed: executeWrite,
                PackageRootName: packageRootName,
                SourceRebuildSceneManifestRelativePath: rebuildScene.ManifestRelativePath,
                SourceRebuildSceneStatus: rebuildScene.ManifestStatus,
                SourceRebuildSceneCompleted: rebuildScene.Completed,
                WorkspaceRootRelativePath: WorkspaceRootRelativePath,
                ManifestRelativePath: ManifestFileName,
                ManifestWritten: manifestWritten,
                ManifestStatus: manifestStatus,
                ManifestBytes: manifestBytes,
                SourceSceneRows: rebuildScene.SceneRows,
                SourceExistingSceneRows: rebuildScene.ExistingSceneRows,
                MeshRows: meshRows.Count,
                ReadyMeshRows: readyRows,
                BlockedMeshRows: meshRows.Count - readyRows,
                WouldWriteMeshRows: meshRows.Count(static row => row.Status == "would-write"),
                WrittenMeshRows: meshRows.Count(static row => row.Status == "written"),
                ExistingMeshRows: meshRows.Count(static row => row.Status is "would-skip-existing" or "skipped-existing"),
                CompleteMeshPayloadRows: meshRows.Count(static row => row.MeshPayloadComplete),
                PartialMeshPayloadRows: meshRows.Count(static row => row.MeshPayloadAvailable && !row.MeshPayloadComplete),
                MissingSceneContractRows: meshRows.Count(static row => row.Status == "missing-scene-contract-file"),
                MissingModelInputRows: meshRows.Count(static row => row.Status == "missing-model-input-file"),
                MissingMeshPayloadRows: meshRows.Count(static row => row.Status == "missing-mesh-payload"),
                BlockedExistingMismatches: meshRows.Count(static row => row.Status == "blocked-existing-mismatch"),
                UnsafeOutputPaths: meshRows.Count(static row => row.Status == "unsafe-output-path"),
                ObjFileRows: meshRows.Count(static row => !string.IsNullOrWhiteSpace(row.ObjRelativePath)),
                MtlFileRows: meshRows.Count(static row => !string.IsNullOrWhiteSpace(row.MtlRelativePath)),
                VertexRows: meshRows.Sum(static row => row.VertexCount),
                FaceRows: meshRows.Sum(static row => row.FaceCount),
                NormalRows: meshRows.Sum(static row => row.NormalCount),
                TextureCoordinateRows: meshRows.Sum(static row => row.TextureCoordinateCount),
                MaterialRows: meshRows.Sum(static row => row.MaterialCount),
                TextureBindingRows: meshRows.Sum(static row => row.TextureBindingRows),
                Completed: rebuildScene.Completed && readyRows == meshRows.Count && issues.Count == 0,
                Meshes: meshRows,
                Issues: issues);
        }

        private static AssetMaterialImportPackageRebuildMeshModelRow BuildMeshRow(
            string fullPackageRoot,
            bool executeWrite,
            AssetMaterialImportPackageRebuildSceneModelRow scene,
            List<AssetMaterialImportPackageRebuildMeshIssue> issues)
        {
            if (!scene.ReadyForSceneContract)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("scene", scene.SceneRelativePath, scene.Status));
                return BuildBlockedMeshRow(scene, scene.Status);
            }

            if (scene.Status is "would-write" or "written")
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("scene", scene.SceneRelativePath, "missing-scene-contract-file"));
                return BuildBlockedMeshRow(scene, "missing-scene-contract-file");
            }

            if (!TryResolveInsidePackage(fullPackageRoot, scene.SceneRelativePath, out _))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("scene", scene.SceneRelativePath, "missing-scene-contract-file"));
                return BuildBlockedMeshRow(scene, "missing-scene-contract-file");
            }

            AssetMaterialImportPackageRebuildSceneFile? sceneFile;
            try
            {
                using GuardedPackageArtifactRead sceneInput = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    scene.SceneRelativePath,
                    "Rebuild-mesh scene contract");
                if (!sceneInput.Exists)
                {
                    issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("scene", scene.SceneRelativePath, "missing-scene-contract-file"));
                    return BuildBlockedMeshRow(scene, "missing-scene-contract-file");
                }
                if (!TryReadSceneFile(sceneInput, out sceneFile) || sceneFile == null)
                {
                    issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("scene", scene.SceneRelativePath, "invalid-scene-contract-file"));
                    return BuildBlockedMeshRow(scene, "invalid-scene-contract-file");
                }
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("scene", scene.SceneRelativePath, "invalid-scene-contract-file"));
                return BuildBlockedMeshRow(scene, "invalid-scene-contract-file");
            }

            if (!TryResolveInsidePackage(fullPackageRoot, sceneFile.ModelInputRelativePath, out _))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("model", sceneFile.ModelInputRelativePath, "missing-model-input-file"));
                return BuildBlockedMeshRow(scene, "missing-model-input-file");
            }

            AssetModelSummary modelSummary;
            try
            {
                using GuardedPackageArtifactRead modelInput = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    sceneFile.ModelInputRelativePath,
                    "Rebuild-mesh model input");
                if (!modelInput.Exists)
                {
                    issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("model", sceneFile.ModelInputRelativePath, "missing-model-input-file"));
                    return BuildBlockedMeshRow(scene, "missing-model-input-file");
                }
                modelSummary = FbxModelSummaryReader.Read(modelInput.Stream);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("model", sceneFile.ModelInputRelativePath, "missing-mesh-payload"));
                return BuildBlockedMeshRow(scene, "missing-mesh-payload");
            }
            AssetModelMeshPayload payload = modelSummary.MeshPayload;
            if (!modelSummary.MetadataAvailable || !payload.Available || !payload.BaseGeometryComplete)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("model", sceneFile.ModelInputRelativePath, "missing-mesh-payload"));
                return BuildBlockedMeshRow(scene, "missing-mesh-payload");
            }

            string outputToken = BuildOutputToken(scene.Ordinal, scene.CatalogId);
            string objRelativePath = $"{WorkspaceRootRelativePath}/models/{outputToken}.mesh.obj";
            string mtlRelativePath = $"{WorkspaceRootRelativePath}/models/{outputToken}.mesh.mtl";
            if (!TryResolveInsidePackage(fullPackageRoot, objRelativePath, out _) ||
                !TryResolveInsidePackage(fullPackageRoot, mtlRelativePath, out _))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("mesh", objRelativePath, "unsafe-output-path"));
                return BuildBlockedMeshRow(scene, "unsafe-output-path", objRelativePath, mtlRelativePath);
            }

            IReadOnlyList<string> materialNames = BuildMaterialNames(modelSummary);
            string objContent = BuildObjContent(scene, mtlRelativePath, payload, materialNames);
            string mtlContent = BuildMtlContent(scene, materialNames, sceneFile.Textures);
            bool objExists;
            bool mtlExists;
            bool objMatches;
            bool mtlMatches;
            try
            {
                using GuardedPackageArtifactRead objRead = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    objRelativePath,
                    "Rebuild-mesh OBJ output");
                using GuardedPackageArtifactRead mtlRead = GuardedPackageArtifactReader.Open(
                    fullPackageRoot,
                    mtlRelativePath,
                    "Rebuild-mesh MTL output");
                objExists = objRead.Exists;
                mtlExists = mtlRead.Exists;
                objMatches = objExists && string.Equals(objRead.ReadAllText(Utf8NoBom), objContent, StringComparison.Ordinal);
                mtlMatches = mtlExists && string.Equals(mtlRead.ReadAllText(Utf8NoBom), mtlContent, StringComparison.Ordinal);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("mesh", objRelativePath, "unsafe-output-path"));
                return BuildBlockedMeshRow(scene, "unsafe-output-path", objRelativePath, mtlRelativePath);
            }
            if ((objExists && !objMatches) || (mtlExists && !mtlMatches))
            {
                issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("mesh", objRelativePath, "blocked-existing-mismatch"));
                return BuildMeshRowResult(scene, objRelativePath, mtlRelativePath, "blocked-existing-mismatch", payload, materialNames.Count, sceneFile.Textures.Count);
            }

            string status;
            if (!executeWrite)
            {
                status = objExists && mtlExists ? "would-skip-existing" : "would-write";
            }
            else
            {
                try
                {
                    GuardedArtifactWriteResult objWrite = GuardedPackageArtifactWriter.WriteText(
                        fullPackageRoot,
                        objRelativePath,
                        objContent,
                        Utf8NoBom);
                    GuardedArtifactWriteResult mtlWrite = GuardedPackageArtifactWriter.WriteText(
                        fullPackageRoot,
                        mtlRelativePath,
                        mtlContent,
                        Utf8NoBom);
                    status = objWrite.Existing && mtlWrite.Existing ? "skipped-existing" : "written";
                }
                catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
                {
                    issues.Add(new AssetMaterialImportPackageRebuildMeshIssue("mesh", objRelativePath, "unsafe-output-path"));
                    return BuildBlockedMeshRow(scene, "unsafe-output-path", objRelativePath, mtlRelativePath);
                }
            }

            return BuildMeshRowResult(scene, objRelativePath, mtlRelativePath, status, payload, materialNames.Count, sceneFile.Textures.Count);
        }

        private static AssetMaterialImportPackageRebuildMeshModelRow BuildBlockedMeshRow(
            AssetMaterialImportPackageRebuildSceneModelRow scene,
            string status,
            string objRelativePath = "",
            string mtlRelativePath = "")
        {
            return new AssetMaterialImportPackageRebuildMeshModelRow(
                Ordinal: scene.Ordinal,
                CatalogId: scene.CatalogId,
                Label: scene.Label,
                SourceSceneRelativePath: NormalizeRelativePath(scene.SceneRelativePath),
                ObjRelativePath: NormalizeRelativePath(objRelativePath),
                MtlRelativePath: NormalizeRelativePath(mtlRelativePath),
                VertexCount: 0,
                FaceCount: 0,
                NormalCount: 0,
                TextureCoordinateCount: 0,
                MaterialCount: 0,
                TextureBindingRows: 0,
                MeshPayloadAvailable: false,
                MeshPayloadComplete: false,
                MeshPayloadStatus: status,
                Status: status,
                ReadyForMeshExport: false);
        }

        private static AssetMaterialImportPackageRebuildMeshModelRow BuildMeshRowResult(
            AssetMaterialImportPackageRebuildSceneModelRow scene,
            string objRelativePath,
            string mtlRelativePath,
            string status,
            AssetModelMeshPayload payload,
            int materialCount,
            int textureBindingRows)
        {
            return new AssetMaterialImportPackageRebuildMeshModelRow(
                Ordinal: scene.Ordinal,
                CatalogId: scene.CatalogId,
                Label: scene.Label,
                SourceSceneRelativePath: NormalizeRelativePath(scene.SceneRelativePath),
                ObjRelativePath: NormalizeRelativePath(objRelativePath),
                MtlRelativePath: NormalizeRelativePath(mtlRelativePath),
                VertexCount: payload.Vertices.Count,
                FaceCount: payload.Faces.Count,
                NormalCount: payload.Normals.Count,
                TextureCoordinateCount: payload.TextureCoordinates.Count,
                MaterialCount: materialCount,
                TextureBindingRows: textureBindingRows,
                MeshPayloadAvailable: payload.Available,
                MeshPayloadComplete: payload.Complete,
                MeshPayloadStatus: payload.Status,
                Status: status,
                ReadyForMeshExport: IsReadyStatus(status));
        }

        private static string BuildObjContent(
            AssetMaterialImportPackageRebuildSceneModelRow scene,
            string mtlRelativePath,
            AssetModelMeshPayload payload,
            IReadOnlyList<string> materialNames)
        {
            StringBuilder builder = new();
            builder.AppendLine("# onslaught asset material package rebuild mesh obj v1");
            builder.AppendLine($"# catalogId: {scene.CatalogId}");
            builder.AppendLine($"# sourceScene: {NormalizeRelativePath(scene.SceneRelativePath)}");
            builder.AppendLine($"mtllib {Path.GetFileName(mtlRelativePath)}");
            builder.AppendLine($"o {BuildObjectName(scene.CatalogId)}");
            foreach (AssetModelPreviewVertex vertex in payload.Vertices)
            {
                builder.Append("v ");
                builder.Append(vertex.X.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(vertex.Y.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(vertex.Z.ToString("R", CultureInfo.InvariantCulture));
                builder.AppendLine();
            }

            foreach (AssetModelTextureCoordinate textureCoordinate in payload.TextureCoordinates)
            {
                builder.Append("vt ");
                builder.Append(textureCoordinate.U.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(textureCoordinate.V.ToString("R", CultureInfo.InvariantCulture));
                builder.AppendLine();
            }

            foreach (AssetModelPreviewVertex normal in payload.Normals)
            {
                builder.Append("vn ");
                builder.Append(normal.X.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(normal.Y.ToString("R", CultureInfo.InvariantCulture));
                builder.Append(' ');
                builder.Append(normal.Z.ToString("R", CultureInfo.InvariantCulture));
                builder.AppendLine();
            }

            string activeMaterial = string.Empty;
            foreach (AssetModelMeshFace face in payload.Faces)
            {
                string materialName = ResolveMaterialName(materialNames, face.MaterialIndex);
                if (!string.Equals(activeMaterial, materialName, StringComparison.Ordinal))
                {
                    builder.AppendLine($"usemtl {materialName}");
                    activeMaterial = materialName;
                }

                builder.Append('f');
                for (int index = 0; index < face.VertexIndices.Count; index++)
                {
                    int vertexIndex = face.VertexIndices[index] + 1;
                    int? uvIndex = TryResolvePolygonVertexIndex(face.PolygonVertexIndices, index, payload.TextureCoordinateIndices, payload.TextureCoordinates.Count);
                    int? normalIndex = TryResolvePolygonVertexIndex(face.PolygonVertexIndices, index, payload.NormalIndices, payload.Normals.Count);
                    builder.Append(' ');
                    AppendObjFaceToken(builder, vertexIndex, uvIndex, normalIndex);
                }

                builder.AppendLine();
            }

            return builder.ToString();
        }

        private static string BuildMtlContent(
            AssetMaterialImportPackageRebuildSceneModelRow scene,
            IReadOnlyList<string> materialNames,
            IReadOnlyList<AssetMaterialImportPackageRebuildSceneTextureBinding> textures)
        {
            StringBuilder builder = new();
            builder.AppendLine("# onslaught asset material package rebuild mesh mtl v1");
            builder.AppendLine($"# catalogId: {scene.CatalogId}");
            for (int index = 0; index < materialNames.Count; index++)
            {
                builder.AppendLine($"newmtl {materialNames[index]}");
                builder.AppendLine("Kd 1 1 1");
                AssetMaterialImportPackageRebuildSceneTextureBinding? texture = ResolveMaterialTexture(textures, index);
                if (texture != null && texture.ReadyForBinding)
                {
                    builder.AppendLine($"map_Kd {NormalizeRelativePath(texture.TextureInputRelativePath)}");
                }

                builder.AppendLine();
            }

            return builder.ToString();
        }

        private static void AppendObjFaceToken(StringBuilder builder, int vertexIndex, int? uvIndex, int? normalIndex)
        {
            builder.Append(vertexIndex.ToString(CultureInfo.InvariantCulture));
            if (uvIndex.HasValue && normalIndex.HasValue)
            {
                builder.Append('/');
                builder.Append((uvIndex.Value + 1).ToString(CultureInfo.InvariantCulture));
                builder.Append('/');
                builder.Append((normalIndex.Value + 1).ToString(CultureInfo.InvariantCulture));
                return;
            }

            if (uvIndex.HasValue)
            {
                builder.Append('/');
                builder.Append((uvIndex.Value + 1).ToString(CultureInfo.InvariantCulture));
                return;
            }

            if (normalIndex.HasValue)
            {
                builder.Append("//");
                builder.Append((normalIndex.Value + 1).ToString(CultureInfo.InvariantCulture));
            }
        }

        private static int? TryResolvePolygonVertexIndex(
            IReadOnlyList<int> polygonVertexOrdinals,
            int faceVertexIndex,
            IReadOnlyList<int> indices,
            int valueCount)
        {
            if (faceVertexIndex >= polygonVertexOrdinals.Count)
            {
                return null;
            }

            int ordinal = polygonVertexOrdinals[faceVertexIndex];
            if (ordinal < 0 || ordinal >= indices.Count)
            {
                return null;
            }

            int valueIndex = indices[ordinal];
            return valueIndex >= 0 && valueIndex < valueCount ? valueIndex : null;
        }

        private static IReadOnlyList<string> BuildMaterialNames(AssetModelSummary modelSummary)
        {
            List<string> names = modelSummary.MaterialNames
                .Select(SanitizeMaterialName)
                .Where(static name => !string.IsNullOrWhiteSpace(name))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .ToList();
            int targetCount = Math.Max(1, Math.Max(modelSummary.MaterialCount, names.Count));
            for (int index = names.Count; index < targetCount; index++)
            {
                names.Add($"material_{index}");
            }

            return names;
        }

        private static string ResolveMaterialName(IReadOnlyList<string> materialNames, int? materialIndex)
        {
            int index = materialIndex.GetValueOrDefault();
            if (index < 0 || index >= materialNames.Count)
            {
                index = 0;
            }

            return materialNames.Count == 0 ? "material_0" : materialNames[index];
        }

        private static AssetMaterialImportPackageRebuildSceneTextureBinding? ResolveMaterialTexture(
            IReadOnlyList<AssetMaterialImportPackageRebuildSceneTextureBinding> textures,
            int materialIndex)
        {
            if (materialIndex >= 0 && materialIndex < textures.Count)
            {
                return textures[materialIndex];
            }

            return null;
        }

        private static (bool Written, string Status, long Bytes) WriteManifestIfRequested(
            bool executeWrite,
            string fullPackageRoot,
            string packageRootName,
            AssetMaterialImportPackageRebuildSceneResult rebuildScene,
            IReadOnlyList<AssetMaterialImportPackageRebuildMeshModelRow> meshRows,
            bool completed)
        {
            if (!executeWrite)
            {
                return (false, "preflight-not-written", 0);
            }

            if (!completed)
                return (false, "source-not-ready-not-written", 0);

            AssetMaterialImportPackageRebuildMeshManifest manifest = new(
                Schema: ManifestSchema,
                GeneratedAtUtc: DateTimeOffset.UtcNow,
                PackageRootName: packageRootName,
                SourceRebuildSceneManifestRelativePath: rebuildScene.ManifestRelativePath,
                WorkspaceRootRelativePath: WorkspaceRootRelativePath,
                SourceSceneRows: rebuildScene.SceneRows,
                MeshRows: meshRows.Count,
                ReadyMeshRows: meshRows.Count(static row => row.ReadyForMeshExport),
                CompleteMeshPayloadRows: meshRows.Count(static row => row.MeshPayloadComplete),
                PartialMeshPayloadRows: meshRows.Count(static row => row.MeshPayloadAvailable && !row.MeshPayloadComplete),
                ObjFileRows: meshRows.Count(static row => !string.IsNullOrWhiteSpace(row.ObjRelativePath)),
                MtlFileRows: meshRows.Count(static row => !string.IsNullOrWhiteSpace(row.MtlRelativePath)),
                VertexRows: meshRows.Sum(static row => row.VertexCount),
                FaceRows: meshRows.Sum(static row => row.FaceCount),
                NormalRows: meshRows.Sum(static row => row.NormalCount),
                TextureCoordinateRows: meshRows.Sum(static row => row.TextureCoordinateCount),
                MaterialRows: meshRows.Sum(static row => row.MaterialCount),
                TextureBindingRows: meshRows.Sum(static row => row.TextureBindingRows),
                Completed: completed,
                Meshes: meshRows.OrderBy(static row => row.Ordinal).ToList());
            try
            {
                GuardedArtifactWriteResult write = GuardedPackageArtifactWriter.ReplaceText(
                    fullPackageRoot,
                    ManifestFileName,
                    JsonSerializer.Serialize(manifest, JsonOptions),
                    Utf8NoBom);
                return (true, "written", write.Bytes);
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return (false, "unsafe-manifest-path", 0);
            }
        }

        private static bool TryReadSceneFile(
            GuardedPackageArtifactRead sceneInput,
            out AssetMaterialImportPackageRebuildSceneFile? sceneFile)
        {
            sceneFile = null;
            try
            {
                sceneFile = JsonSerializer.Deserialize<AssetMaterialImportPackageRebuildSceneFile>(
                    sceneInput.ReadAllText(Utf8NoBom),
                    JsonOptions);
            }
            catch (JsonException)
            {
                return false;
            }

            return sceneFile != null &&
                   string.Equals(sceneFile.Schema, AssetMaterialImportPackageRebuildSceneService.SceneFileSchema, StringComparison.Ordinal);
        }

        private static string BuildOutputToken(int ordinal, string catalogId)
        {
            return $"{ordinal:0000}-{SanitizeToken(catalogId)}";
        }

        private static string BuildObjectName(string catalogId)
        {
            return SanitizeToken(catalogId).Replace('-', '_');
        }

        private static string SanitizeMaterialName(string value)
        {
            string name = SanitizeToken(value).Replace('-', '_').Replace('.', '_');
            return string.IsNullOrWhiteSpace(name) ? "material_0" : name;
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

        private static bool TryResolveInsidePackage(string fullPackageRoot, string? relativePath, out string fullPath) =>
            GuardedPackageArtifactReader.TryResolveRelativePath(fullPackageRoot, relativePath, out fullPath);

        private static string NormalizeRelativePath(string? value)
        {
            return (value ?? string.Empty).Replace('\\', '/');
        }

        private static bool IsReadyStatus(string status)
        {
            return status is "would-write" or "would-skip-existing" or "written" or "skipped-existing";
        }

        private static string BuildRootName(string packageRoot)
        {
            return Path.GetFileName(packageRoot.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
        }
    }

    public sealed record AssetMaterialImportPackageRebuildMeshResult(
        bool Executed,
        string PackageRootName,
        string SourceRebuildSceneManifestRelativePath,
        string SourceRebuildSceneStatus,
        bool SourceRebuildSceneCompleted,
        string WorkspaceRootRelativePath,
        string ManifestRelativePath,
        bool ManifestWritten,
        string ManifestStatus,
        long ManifestBytes,
        int SourceSceneRows,
        int SourceExistingSceneRows,
        int MeshRows,
        int ReadyMeshRows,
        int BlockedMeshRows,
        int WouldWriteMeshRows,
        int WrittenMeshRows,
        int ExistingMeshRows,
        int CompleteMeshPayloadRows,
        int PartialMeshPayloadRows,
        int MissingSceneContractRows,
        int MissingModelInputRows,
        int MissingMeshPayloadRows,
        int BlockedExistingMismatches,
        int UnsafeOutputPaths,
        int ObjFileRows,
        int MtlFileRows,
        int VertexRows,
        int FaceRows,
        int NormalRows,
        int TextureCoordinateRows,
        int MaterialRows,
        int TextureBindingRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildMeshModelRow> Meshes,
        IReadOnlyList<AssetMaterialImportPackageRebuildMeshIssue> Issues);

    public sealed record AssetMaterialImportPackageRebuildMeshModelRow(
        int Ordinal,
        string CatalogId,
        string Label,
        string SourceSceneRelativePath,
        string ObjRelativePath,
        string MtlRelativePath,
        int VertexCount,
        int FaceCount,
        int NormalCount,
        int TextureCoordinateCount,
        int MaterialCount,
        int TextureBindingRows,
        bool MeshPayloadAvailable,
        bool MeshPayloadComplete,
        string MeshPayloadStatus,
        string Status,
        bool ReadyForMeshExport);

    public sealed record AssetMaterialImportPackageRebuildMeshIssue(
        string Role,
        string RelativePath,
        string Status);

    public sealed record AssetMaterialImportPackageRebuildMeshManifest(
        string Schema,
        DateTimeOffset GeneratedAtUtc,
        string PackageRootName,
        string SourceRebuildSceneManifestRelativePath,
        string WorkspaceRootRelativePath,
        int SourceSceneRows,
        int MeshRows,
        int ReadyMeshRows,
        int CompleteMeshPayloadRows,
        int PartialMeshPayloadRows,
        int ObjFileRows,
        int MtlFileRows,
        int VertexRows,
        int FaceRows,
        int NormalRows,
        int TextureCoordinateRows,
        int MaterialRows,
        int TextureBindingRows,
        bool Completed,
        IReadOnlyList<AssetMaterialImportPackageRebuildMeshModelRow> Meshes);
}
