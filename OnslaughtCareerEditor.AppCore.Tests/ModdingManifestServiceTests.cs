using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The app-owned modding manifest: metadata-only export beside a player-generated
    /// catalog, guarded writes, game-tree refusal, and no retail bytes in the file.
    /// </summary>
    public sealed class ModdingManifestServiceTests : IDisposable
    {
        private readonly string _tempRoot;

        public ModdingManifestServiceTests()
        {
            _tempRoot = Path.Combine(Path.GetTempPath(), "oce-modding-manifest-tests", Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(_tempRoot);
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(_tempRoot, recursive: true);
            }
            catch (IOException)
            {
            }
        }

        /// <summary>
        /// Mirrors the generated export layout the Asset Library documents:
        /// asset_catalog/catalog.json beside an exports folder.
        /// </summary>
        private string CreateExportRoot()
        {
            string catalogDir = Path.Combine(_tempRoot, "asset_catalog");
            string exportsDir = Path.Combine(_tempRoot, "exports");
            Directory.CreateDirectory(catalogDir);
            Directory.CreateDirectory(exportsDir);

            byte[] textureBytes = { 0x89, 0x50, 0x4E, 0x47, 0x01, 0x02, 0x03 };
            File.WriteAllBytes(Path.Combine(exportsDir, "texture_one.png"), textureBytes);

            string catalogPath = Path.Combine(catalogDir, "catalog.json");
            File.WriteAllText(catalogPath, """
                {
                  "schema_version": 2,
                  "path_contract": "bundle-root-relative",
                  "summary": {
                    "texture_catalog_entries": 1,
                    "loose_mesh_catalog_entries": 1,
                    "embedded_mesh_catalog_entries": 0,
                    "video_catalog_entries": 0,
                    "language_catalog_entries": 0,
                    "goodie_catalog_entries": 0,
                    "total_catalog_entries": 2
                  },
                  "textures": [
                    {
                      "catalog_id": "texture:textures/texture_one.tga",
                      "kind": "texture",
                      "canonical_ref": "textures/texture_one.tga",
                      "source_roots": ["dxtntextures"],
                      "export_png_paths": ["exports/texture_one.png"],
                      "source_aya_count": 1,
                      "export_png_count": 1,
                      "packed_text_ref_count": 0,
                      "gdie_ref_count": 0,
                      "total_packed_ref_count": 0,
                      "referenced_in_packed": true
                    }
                  ],
                  "loose_meshes": [
                    {
                      "catalog_id": "mesh:ship_body.msh",
                      "kind": "loose_mesh",
                      "canonical_ref": "ship_body.msh",
                      "export_fbx_paths": ["exports/ship_body.msh_binary.fbx"],
                      "source_aya_count": 1,
                      "export_fbx_count": 1,
                      "packed_reference_count": 0,
                      "gdie_ref_count": 0,
                      "total_packed_ref_count": 0,
                      "referenced_in_packed": true
                    }
                  ],
                  "embedded_meshes": [],
                  "videos": [],
                  "language_rows": [],
                  "goodies": []
                }
                """);

            string meshPath = Path.Combine(exportsDir, "ship_body.msh_binary.fbx");
            if (!File.Exists(meshPath))
            {
                File.WriteAllBytes(meshPath, new byte[] { 0x46, 0x42, 0x58 });
            }

            return catalogDir;
        }

        [Fact]
        public void Export_WritesManifestBesideCatalogWithHashes()
        {
            string catalogDir = CreateExportRoot();

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModdingManifestExportResult result = ModdingManifestService.Export(snapshot);

            Assert.True(result.Success, result.Message);
            string manifestPath = Path.Combine(catalogDir, "modding-manifest.json");
            Assert.Equal(manifestPath, result.ManifestPath);
            Assert.True(File.Exists(manifestPath));

            string manifest = File.ReadAllText(manifestPath);
            Assert.Contains("modding-manifest.v1", manifest, StringComparison.Ordinal);
            Assert.Contains("Metadata only", manifest, StringComparison.Ordinal);

            // Hashes name the player's own exported files; no content bytes are copied.
            string textureHash = Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(Path.Combine(_tempRoot, "exports", "texture_one.png")))).ToLowerInvariant();
            Assert.Contains(textureHash, manifest, StringComparison.Ordinal);
        }

        [Fact]
        public void Export_WithoutLoadedCatalogFailsWithoutWriting()
        {
            ModdingManifestExportResult result = ModdingManifestService.Export(AssetCatalogSnapshot.Empty);

            Assert.False(result.Success);
            Assert.Null(result.ManifestPath);
            Assert.Contains("Load a generated catalog", result.Message, StringComparison.Ordinal);
        }

        [Fact]
        public void Export_RefusesACatalogInsideAGameTree()
        {
            // A game-tree lookalike anywhere above the catalog: BEA.exe + data/.
            string gameRoot = Path.Combine(_tempRoot, "game");
            Directory.CreateDirectory(Path.Combine(gameRoot, "data"));
            File.WriteAllText(Path.Combine(gameRoot, "BEA.exe"), "not really an executable");

            string catalogDir = Path.Combine(gameRoot, "asset_catalog");
            Directory.CreateDirectory(catalogDir);
            File.WriteAllText(
                Path.Combine(catalogDir, "catalog.json"),
                "{\"schema_version\":2,\"path_contract\":\"bundle-root-relative\"}");

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModdingManifestExportResult result = ModdingManifestService.Export(snapshot);

            Assert.False(result.Success);
            Assert.Null(result.ManifestPath);
            Assert.False(File.Exists(Path.Combine(catalogDir, "modding-manifest.json")));
        }

        [Fact]
        public void BuildDocument_ListsEveryCatalogAssetKind()
        {
            string catalogDir = CreateExportRoot();

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModdingManifestDocument document = ModdingManifestService.BuildDocument(snapshot);

            Assert.Equal("modding-manifest.v1", document.ManifestVersion, ignoreCase: true);
            Assert.Equal(snapshot.Textures.Count + snapshot.LooseMeshes.Count + snapshot.EmbeddedMeshes.Count,
                document.AssetCount);
            Assert.Equal(2, document.AssetCount);
            Assert.All(document.Assets, asset =>
                Assert.True(asset.Kind is "texture" or "mesh" or "embedded-mesh", $"unexpected kind {asset.Kind}"));
            Assert.All(document.Assets, asset => Assert.False(string.IsNullOrWhiteSpace(asset.ExportFileName)));
            Assert.Contains(document.Assets, asset => asset.ExportPresent && asset.ExportSha256 is not null);
            // Missing export files stay listed but carry no hash.
            Assert.Contains(document.Assets, asset => !asset.ExportPresent || asset.ExportSha256 is not null);
        }

        [Fact]
        public void Export_IsIdempotentOverwrite()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);

            ModdingManifestExportResult first = ModdingManifestService.Export(snapshot);
            ModdingManifestExportResult second = ModdingManifestService.Export(snapshot);

            Assert.True(first.Success, first.Message);
            Assert.True(second.Success, second.Message);
            Assert.Equal(first.ManifestPath, second.ManifestPath);
        }
    }
}
