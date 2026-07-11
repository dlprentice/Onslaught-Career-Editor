using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    public sealed class AssetModelTextureLinkService
    {
        internal static IReadOnlyDictionary<string, IReadOnlyList<AssetModelSidecarTexture>>
            CaptureSnapshotSidecars(
                AssetCatalogLoadSession session,
                IEnumerable<string> modelExportPaths)
        {
            var result = new Dictionary<string, IReadOnlyList<AssetModelSidecarTexture>>(
                FileMutationSafety.PathComparer);
            string trustedRoot = FileMutationSafety.NormalizeLocalPath(
                session.TrustedExportRoot,
                "Trusted asset export root");

            foreach (string modelExportPath in modelExportPaths
                .Where(static path => !string.IsNullOrWhiteSpace(path))
                .Select(path => FileMutationSafety.NormalizeLocalPath(path, "Catalog model export"))
                .Distinct(FileMutationSafety.PathComparer))
            {
                using AssetCatalogSourceRead modelSource = session.OpenSource(
                    modelExportPath,
                    "Catalog model export used for sidecar discovery");
                if (!modelSource.Exists)
                {
                    result[modelExportPath] = [];
                    continue;
                }

                result[modelExportPath] = CaptureModelSidecars(
                    session,
                    trustedRoot,
                    modelSource.PhysicalPath);
            }

            return result;
        }

        public AssetModelTextureLinks Build(IReadOnlyList<AssetTextureItem> textures, AssetModelSummary summary)
        {
            IReadOnlyDictionary<string, AssetTextureItem> catalogTextures = BuildCatalogTextureMap(textures);
            IReadOnlyList<string> textureBindingFileNames = summary.TextureBindingFileNames
                .Where(static value => !string.IsNullOrWhiteSpace(value))
                .Select(static value => ExtractFileName(value.Trim()))
                .Where(static value => !string.IsNullOrWhiteSpace(value))
                .Where(static value => !IsTemplateTextureBinding(value))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                .ToList();
            List<string> catalogMatchedTextureNames = new();
            List<string> catalogMissingTextureFileNames = new();
            foreach (string fileName in textureBindingFileNames)
            {
                if (TryResolveCatalogTexture(fileName, catalogTextures, out AssetTextureItem? catalogTexture))
                {
                    catalogMatchedTextureNames.Add(catalogTexture.DisplayName);
                }
                else
                {
                    catalogMissingTextureFileNames.Add(fileName);
                }
            }

            return new AssetModelTextureLinks(
                textureBindingFileNames,
                catalogMatchedTextureNames
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                    .ToList(),
                catalogMissingTextureFileNames
                    .Distinct(StringComparer.OrdinalIgnoreCase)
                    .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                    .ToList());
        }

        public IReadOnlyList<AssetModelTextureBindingResolution> BuildBindingResolutions(
            AssetCatalogSnapshot snapshot,
            string modelExportPath,
            AssetModelSummary summary)
        {
            IReadOnlyDictionary<string, AssetTextureItem> catalogTextures = BuildCatalogTextureMap(snapshot.Textures);
            SidecarTextureIndex sidecarIndex = BuildSidecarTextureIndex(snapshot, modelExportPath);
            IReadOnlyList<string> textureBindingFileNames = summary.TextureBindingFileNames
                .Where(static value => !string.IsNullOrWhiteSpace(value))
                .Select(static value => ExtractFileName(value.Trim()))
                .Where(static value => !string.IsNullOrWhiteSpace(value))
                .Where(static value => !IsTemplateTextureBinding(value))
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(static value => value, StringComparer.OrdinalIgnoreCase)
                .ToList();
            List<AssetModelTextureBindingResolution> resolutions = new();

            foreach (string binding in textureBindingFileNames)
            {
                if (TryResolveCatalogTexture(binding, catalogTextures, out AssetTextureItem? catalogTexture))
                {
                    resolutions.Add(new AssetModelTextureBindingResolution(
                        BindingFileName: binding,
                        ResolutionKind: "catalog",
                        CatalogTextureId: catalogTexture.CatalogId,
                        CatalogTextureName: catalogTexture.DisplayName,
                        CatalogTextureExportFileName: catalogTexture.ExportFileName,
                        CatalogTextureExportExists: catalogTexture.ExportExists,
                        SidecarTextureFileName: string.Empty,
                        SidecarExactFileNameMatch: false,
                        Status: "Catalog texture row resolves this FBX texture binding."));
                    continue;
                }

                if (TryResolveSidecarTexture(binding, sidecarIndex, out AssetModelSidecarTexture? sidecarTexture))
                {
                    resolutions.Add(new AssetModelTextureBindingResolution(
                        BindingFileName: binding,
                        ResolutionKind: "sidecar",
                        CatalogTextureId: string.Empty,
                        CatalogTextureName: string.Empty,
                        CatalogTextureExportFileName: string.Empty,
                        CatalogTextureExportExists: false,
                        SidecarTextureFileName: sidecarTexture.FileName,
                        SidecarExactFileNameMatch: sidecarTexture.ExactFileNameMatch,
                        Status: "Local mesh-texture sidecar resolves this catalog-missing FBX texture binding."));
                    continue;
                }

                resolutions.Add(new AssetModelTextureBindingResolution(
                    BindingFileName: binding,
                    ResolutionKind: "unresolved",
                    CatalogTextureId: string.Empty,
                    CatalogTextureName: string.Empty,
                    CatalogTextureExportFileName: string.Empty,
                    CatalogTextureExportExists: false,
                    SidecarTextureFileName: string.Empty,
                    SidecarExactFileNameMatch: false,
                    Status: "No catalog texture row or local mesh-texture sidecar resolves this FBX texture binding."));
            }

            return resolutions;
        }

        public IReadOnlyList<AssetModelSidecarTexture> ResolveSidecarTextures(
            AssetCatalogSnapshot snapshot,
            string modelExportPath,
            IReadOnlyList<string> textureBindingFileNames)
        {
            if (string.IsNullOrWhiteSpace(modelExportPath) || textureBindingFileNames.Count == 0)
            {
                return Array.Empty<AssetModelSidecarTexture>();
            }

            IReadOnlyList<AssetModelSidecarTexture> sidecarFiles = ReadSidecarFiles(snapshot, modelExportPath);
            if (sidecarFiles.Count == 0)
            {
                return Array.Empty<AssetModelSidecarTexture>();
            }

            SidecarTextureIndex index = BuildSidecarTextureIndexFromFiles(sidecarFiles);
            Dictionary<string, AssetModelSidecarTexture> matches = new(StringComparer.OrdinalIgnoreCase);

            foreach (string binding in textureBindingFileNames)
            {
                if (TryResolveSidecarTexture(binding, index, out AssetModelSidecarTexture? sidecarTexture))
                {
                    string key = string.IsNullOrWhiteSpace(sidecarTexture.ExportPath)
                        ? sidecarTexture.FileName
                        : sidecarTexture.ExportPath;
                    matches.TryAdd(key, sidecarTexture);
                }
            }

            return matches.Values
                .OrderBy(static value => value.FileName, StringComparer.OrdinalIgnoreCase)
                .ToList();
        }

        private static IReadOnlyDictionary<string, AssetTextureItem> BuildCatalogTextureMap(IReadOnlyList<AssetTextureItem> textures)
        {
            Dictionary<string, AssetTextureItem> texturesByKey = new(StringComparer.OrdinalIgnoreCase);
            foreach (AssetTextureItem texture in textures)
            {
                AddCatalogTexture(texturesByKey, texture.CanonicalRef, texture);
                AddCatalogTexture(texturesByKey, texture.ExportFileName, texture);
            }

            return texturesByKey;
        }

        private static void AddCatalogTexture(Dictionary<string, AssetTextureItem> texturesByKey, string value, AssetTextureItem texture)
        {
            AddCatalogTextureKey(texturesByKey, NormalizeTextureKey(value), texture);
            AddCatalogTextureKey(texturesByKey, NormalizeCompactTextureKey(value), texture);
        }

        private static void AddCatalogTextureKey(
            Dictionary<string, AssetTextureItem> texturesByKey,
            string key,
            AssetTextureItem texture)
        {
            if (!string.IsNullOrWhiteSpace(key) && !texturesByKey.ContainsKey(key))
            {
                texturesByKey[key] = texture;
            }
        }

        private static bool TryResolveCatalogTexture(
            string textureBindingFileName,
            IReadOnlyDictionary<string, AssetTextureItem> catalogTextures,
            out AssetTextureItem texture)
        {
            string key = NormalizeTextureKey(textureBindingFileName);
            if (!string.IsNullOrWhiteSpace(key) && catalogTextures.TryGetValue(key, out texture!))
            {
                return true;
            }

            string compactKey = NormalizeCompactTextureKey(textureBindingFileName);
            if (!string.IsNullOrWhiteSpace(compactKey) && catalogTextures.TryGetValue(compactKey, out texture!))
            {
                return true;
            }

            texture = default!;
            return false;
        }

        private static SidecarTextureIndex BuildSidecarTextureIndex(
            AssetCatalogSnapshot snapshot,
            string modelExportPath)
        {
            if (string.IsNullOrWhiteSpace(modelExportPath))
            {
                return SidecarTextureIndex.Empty;
            }

            IReadOnlyList<AssetModelSidecarTexture> sidecarFiles = ReadSidecarFiles(snapshot, modelExportPath);
            return sidecarFiles.Count == 0 ? SidecarTextureIndex.Empty : BuildSidecarTextureIndexFromFiles(sidecarFiles);
        }

        private static SidecarTextureIndex BuildSidecarTextureIndexFromFiles(
            IReadOnlyList<AssetModelSidecarTexture> sidecarFiles)
        {
            Dictionary<string, AssetModelSidecarTexture> byFileName = sidecarFiles
                .GroupBy(static file => file.FileName, StringComparer.OrdinalIgnoreCase)
                .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase);
            Dictionary<string, AssetModelSidecarTexture> byStem = sidecarFiles
                .GroupBy(static file => NormalizeTextureKey(file.FileName), StringComparer.OrdinalIgnoreCase)
                .Where(static group => !string.IsNullOrWhiteSpace(group.Key))
                .ToDictionary(static group => group.Key, static group => group.First(), StringComparer.OrdinalIgnoreCase);
            return new SidecarTextureIndex(byFileName, byStem);
        }

        private static bool TryResolveSidecarTexture(
            string textureBindingFileName,
            SidecarTextureIndex index,
            out AssetModelSidecarTexture texture)
        {
            string fileName = ExtractFileName(textureBindingFileName);
            if (string.IsNullOrWhiteSpace(fileName))
            {
                texture = default!;
                return false;
            }

            if (index.ByFileName.TryGetValue(fileName, out AssetModelSidecarTexture? exactFile))
            {
                texture = exactFile with { ExactFileNameMatch = true };
                return true;
            }

            string key = NormalizeTextureKey(fileName);
            if (!string.IsNullOrWhiteSpace(key) && index.ByStem.TryGetValue(key, out AssetModelSidecarTexture? stemFile))
            {
                texture = stemFile with { ExactFileNameMatch = false };
                return true;
            }

            texture = default!;
            return false;
        }

        private static bool IsTemplateTextureBinding(string value)
        {
            string key = NormalizeTextureKey(value);
            if (key.Equals("base_color_texture", StringComparison.OrdinalIgnoreCase))
            {
                return true;
            }

            const string prefix = "default";
            if (!key.StartsWith(prefix, StringComparison.OrdinalIgnoreCase) || key.Length == prefix.Length)
            {
                return false;
            }

            for (int index = prefix.Length; index < key.Length; index++)
            {
                if (!char.IsDigit(key[index]))
                {
                    return false;
                }
            }

            return true;
        }

        private static string NormalizeCompactTextureKey(string value)
        {
            string key = NormalizeTextureKey(value);
            if (string.IsNullOrWhiteSpace(key))
            {
                return string.Empty;
            }

            Span<char> buffer = key.Length <= 256 ? stackalloc char[key.Length] : new char[key.Length];
            int length = 0;
            foreach (char ch in key)
            {
                if (char.IsLetterOrDigit(ch))
                {
                    buffer[length++] = ch;
                }
            }

            return length == 0 ? string.Empty : new string(buffer[..length]);
        }

        private static string NormalizeTextureKey(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return string.Empty;
            }

            string fileName = Path.GetFileName(value.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar));
            if (string.IsNullOrWhiteSpace(fileName))
            {
                return string.Empty;
            }

            string withoutExtension = Path.GetFileNameWithoutExtension(fileName);
            int tgaIndex = withoutExtension.IndexOf(".tga", StringComparison.OrdinalIgnoreCase);
            if (tgaIndex >= 0)
            {
                withoutExtension = withoutExtension[..tgaIndex];
            }

            int ddsIndex = withoutExtension.IndexOf(".dds", StringComparison.OrdinalIgnoreCase);
            if (ddsIndex >= 0)
            {
                withoutExtension = withoutExtension[..ddsIndex];
            }

            int variantIndex = withoutExtension.IndexOf('(');
            if (variantIndex >= 0)
            {
                withoutExtension = withoutExtension[..variantIndex];
            }

            return withoutExtension.Trim().ToLowerInvariant();
        }

        private static IReadOnlyList<AssetModelSidecarTexture> ReadSidecarFiles(
            AssetCatalogSnapshot snapshot,
            string modelExportPath)
        {
            try
            {
                string normalizedModelPath = FileMutationSafety.NormalizeLocalPath(
                    modelExportPath,
                    "Catalog model export");
                return snapshot.SealedSidecarTexturesByModelPath.TryGetValue(
                    normalizedModelPath,
                    out IReadOnlyList<AssetModelSidecarTexture>? sidecars)
                        ? sidecars
                        : Array.Empty<AssetModelSidecarTexture>();
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or InvalidOperationException or NotSupportedException or UnauthorizedAccessException)
            {
                return Array.Empty<AssetModelSidecarTexture>();
            }
        }

        private static IReadOnlyList<AssetModelSidecarTexture> CaptureModelSidecars(
            AssetCatalogLoadSession session,
            string trustedRoot,
            string modelPhysicalPath)
        {
            string? directory = Path.GetDirectoryName(modelPhysicalPath);
            while (!string.IsNullOrWhiteSpace(directory) &&
                FileMutationSafety.IsSameOrUnderRoot(directory, trustedRoot))
            {
                foreach (string candidate in new[]
                {
                    Path.Combine(directory, "MeshTextures"),
                    Path.Combine(directory, "loose_meshes", "MeshTextures"),
                })
                {
                    if (!Directory.Exists(candidate))
                        continue;

                    using FileMutationSafety.DirectoryLockSet directoryLocks =
                        FileMutationSafety.LockDirectoryTree(candidate, "Model sidecar texture directory");
                    if (!FileMutationSafety.IsSameOrUnderRoot(directoryLocks.PhysicalPath, trustedRoot))
                    {
                        throw new InvalidOperationException(
                            "Model sidecar texture directory resolves outside the trusted generated export root.");
                    }

                    var sidecars = new List<AssetModelSidecarTexture>();
                    foreach (string filePath in Directory
                        .EnumerateFiles(directoryLocks.PhysicalPath)
                        .Where(static path => IsTextureSidecar(Path.GetFileName(path)))
                        .OrderBy(static path => Path.GetFileName(path), StringComparer.OrdinalIgnoreCase))
                    {
                        using AssetCatalogSourceRead sidecar = session.OpenSource(
                            filePath,
                            "Model sidecar texture");
                        if (sidecar.Exists)
                        {
                            sidecars.Add(new AssetModelSidecarTexture(
                                Path.GetFileName(sidecar.Path),
                                sidecar.Path,
                                ExactFileNameMatch: false));
                        }
                    }

                    return sidecars;
                }

                if (string.Equals(directory, trustedRoot, FileMutationSafety.PathComparison))
                    break;

                string? parent = Path.GetDirectoryName(directory);
                if (string.Equals(parent, directory, FileMutationSafety.PathComparison))
                    break;
                directory = parent;
            }

            return Array.Empty<AssetModelSidecarTexture>();
        }

        private static bool IsTextureSidecar(string fileName)
        {
            string extension = Path.GetExtension(fileName);
            return extension.Equals(".png", StringComparison.OrdinalIgnoreCase)
                || extension.Equals(".tga", StringComparison.OrdinalIgnoreCase);
        }

        private static string ExtractFileName(string value)
        {
            return Path.GetFileName(value.Replace('\\', Path.DirectorySeparatorChar).Replace('/', Path.DirectorySeparatorChar));
        }

        private sealed record SidecarTextureIndex(
            IReadOnlyDictionary<string, AssetModelSidecarTexture> ByFileName,
            IReadOnlyDictionary<string, AssetModelSidecarTexture> ByStem)
        {
            public static SidecarTextureIndex Empty { get; } = new(
                new Dictionary<string, AssetModelSidecarTexture>(StringComparer.OrdinalIgnoreCase),
                new Dictionary<string, AssetModelSidecarTexture>(StringComparer.OrdinalIgnoreCase));
        }
    }

    public sealed record AssetModelTextureLinks(
        IReadOnlyList<string> TextureBindingFileNames,
        IReadOnlyList<string> CatalogMatchedTextureNames,
        IReadOnlyList<string> CatalogMissingTextureFileNames);

    public sealed record AssetModelSidecarTexture(
        string FileName,
        string ExportPath,
        bool ExactFileNameMatch);

    public sealed record AssetModelTextureBindingResolution(
        string BindingFileName,
        string ResolutionKind,
        string CatalogTextureId,
        string CatalogTextureName,
        string CatalogTextureExportFileName,
        bool CatalogTextureExportExists,
        string SidecarTextureFileName,
        bool SidecarExactFileNameMatch,
        string Status);
}
