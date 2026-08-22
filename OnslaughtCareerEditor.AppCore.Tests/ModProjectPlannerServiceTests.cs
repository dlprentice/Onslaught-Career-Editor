using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The mod project manifest planner: a bounded selection of catalog rows becomes
    /// a versioned, metadata-only project plan with verified provenance. Fail-closed
    /// on ambiguous identity, game-tree outputs, changed provenance, and drifted
    /// local exports. It never copies retail bytes.
    /// </summary>
    public sealed class ModProjectPlannerServiceTests : IDisposable
    {
        private readonly string _tempRoot;

        public ModProjectPlannerServiceTests()
        {
            _tempRoot = Path.Combine(Path.GetTempPath(), "oce-mod-planner-tests", Guid.NewGuid().ToString("N"));
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
        /// asset_catalog/catalog.json beside an exports folder. One texture with a
        /// local export, one loose mesh with a local export, one texture whose
        /// export is missing, and one embedded mesh with a local export.
        /// </summary>
        private string CreateExportRoot()
        {
            string catalogDir = Path.Combine(_tempRoot, "asset_catalog");
            string exportsDir = Path.Combine(_tempRoot, "exports");
            Directory.CreateDirectory(catalogDir);
            Directory.CreateDirectory(exportsDir);

            File.WriteAllBytes(Path.Combine(exportsDir, "texture_one.png"), new byte[] { 0x89, 0x50, 0x4E, 0x47, 0x01 });
            File.WriteAllBytes(Path.Combine(exportsDir, "ship_body.msh_binary.fbx"), new byte[] { 0x46, 0x42, 0x58, 0x02 });
            File.WriteAllBytes(Path.Combine(exportsDir, "body00_binary.fbx"), new byte[] { 0x46, 0x42, 0x58, 0x03 });

            string catalogPath = Path.Combine(catalogDir, "catalog.json");
            File.WriteAllText(catalogPath, """
                {
                  "schema_version": 2,
                  "path_contract": "bundle-root-relative",
                  "summary": {
                    "texture_catalog_entries": 2,
                    "loose_mesh_catalog_entries": 1,
                    "embedded_mesh_catalog_entries": 1,
                    "video_catalog_entries": 0,
                    "language_catalog_entries": 0,
                    "goodie_catalog_entries": 1,
                    "total_catalog_entries": 5
                  },
                  "textures": [
                    {
                      "catalog_id": "texture:textures/texture_one.tga",
                      "kind": "texture",
                      "canonical_ref": "textures/texture_one.tga",
                      "source_roots": ["dxtntextures"],
                      "export_png_paths": ["exports/texture_one.png"],
                      "export_sha256": "871923f8e5535ef938edc1ea710d5cf9e18637ce5d39feccef23030823993e4e",
                      "source_aya_count": 1,
                      "export_png_count": 1,
                      "packed_text_ref_count": 0,
                      "gdie_ref_count": 0,
                      "total_packed_ref_count": 0,
                      "referenced_in_packed": true
                    },
                    {
                      "catalog_id": "texture:textures/texture_missing.tga",
                      "kind": "texture",
                      "canonical_ref": "textures/texture_missing.tga",
                      "source_roots": ["dxtntextures"],
                      "export_png_paths": ["exports/texture_missing.png"],
                      "source_aya_count": 1,
                      "export_png_count": 0,
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
                  "embedded_meshes": [
                    {
                      "catalog_id": "embedded_mesh:100_res_PC/body00",
                      "kind": "embedded_mesh",
                      "source_archive": "100_res_PC",
                      "body_name": "body00",
                      "export_fbx_path": "exports/body00_binary.fbx"
                    }
                  ],
                  "videos": [],
                  "language_rows": [],
                  "goodies": [
                    {
                      "catalog_id": "goodie:7",
                      "index": 7,
                      "display_name": "Aquila concept art",
                      "content_kind": "artwork",
                      "source_title": "Aquila",
                      "source_archive": "goodies_pc",
                      "gdie_family": "artwork",
                      "primary_texture_ref": "textures/texture_one.tga",
                      "primary_mesh_ref": "",
                      "video_sequence_id": "",
                      "video_catalog_id": "",
                      "video_relative_path": "",
                      "texture_refs": ["textures/texture_one.tga"],
                      "mesh_refs": []
                    }
                  ]
                }
                """);

            return catalogDir;
        }

        private static string Sha256Hex(string filePath)
        {
            using FileStream stream = File.OpenRead(filePath);
            return Convert.ToHexString(SHA256.HashData(stream)).ToLowerInvariant();
        }

        [Fact]
        public void BuildPlan_PlansSelectedRowsAcrossKindsWithProvenanceAndHashes()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);

            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [
                    new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga"),
                    new ModProjectSelectionEntry("mesh", "mesh:ship_body.msh"),
                    new ModProjectSelectionEntry("embedded-mesh", "embedded_mesh:100_res_PC/body00"),
                ]);

            Assert.Equal("mod-project-plan.v1", plan.ManifestVersion);
            Assert.Equal("catalog.json", plan.CatalogFileName);
            Assert.Equal(2, plan.CatalogSchemaVersion);
            Assert.Equal("bundle-root-relative", plan.CatalogPathContract);
            Assert.Equal(Sha256Hex(Path.Combine(catalogDir, "catalog.json")), plan.CatalogSha256);
            Assert.Equal(3, plan.SelectedCount);
            Assert.Equal(3, plan.Assets.Count);
            Assert.Contains(plan.KindCounts, count => count.Kind == "texture" && count.Count == 1);
            Assert.Contains(plan.KindCounts, count => count.Kind == "mesh" && count.Count == 1);
            Assert.Contains(plan.KindCounts, count => count.Kind == "embedded-mesh" && count.Count == 1);

            ModProjectPlannedAsset texture = plan.Assets.Single(asset => asset.Kind == "texture");
            Assert.Equal("texture:textures/texture_one.tga", texture.CatalogId);
            Assert.True(texture.ExportPresent);
            Assert.Equal(Sha256Hex(Path.Combine(_tempRoot, "exports", "texture_one.png")), texture.ExportSha256);
            Assert.Equal(new FileInfo(Path.Combine(_tempRoot, "exports", "texture_one.png")).Length, texture.ExportLengthBytes);
            Assert.Equal(texture.ExportSha256, texture.ExpectedExportSha256);

            ModProjectPlannedAsset mesh = plan.Assets.Single(asset => asset.Kind == "mesh");
            Assert.True(mesh.ExportPresent);
            Assert.Null(mesh.SourceArchive);

            ModProjectPlannedAsset embedded = plan.Assets.Single(asset => asset.Kind == "embedded-mesh");
            Assert.Equal("100_res_PC#body00", embedded.CanonicalRef);
            Assert.Equal("100_res_PC", embedded.SourceArchive);

            // The plan carries the content boundary in its own words: a receipt,
            // not an asset pack, installer, or compatibility guarantee.
            Assert.Contains("not an asset pack", plan.ContentBoundary, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("0x89PNG", plan.ContentBoundary, StringComparison.Ordinal);
        }

        [Fact]
        public void BuildPlan_CountsUnresolvedRowsWithoutDroppingThem()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);

            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [
                    new ModProjectSelectionEntry("texture", "texture:textures/texture_missing.tga"),
                ]);

            Assert.Equal(1, plan.SelectedCount);
            Assert.Equal(1, plan.UnresolvedMetadataCount);
            ModProjectPlannedAsset row = plan.Assets.Single();
            Assert.False(row.ExportPresent);
            Assert.Null(row.ExportSha256);
        }

        [Fact]
        public void BuildPlan_IncludesGoodieWhenCatalogProvidesStableIdentity()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);

            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [new ModProjectSelectionEntry("goodie", "goodie:7")]);

            ModProjectPlannedAsset row = Assert.Single(plan.Assets);
            Assert.Equal("goodie", row.Kind);
            Assert.Equal("goodie:7", row.CatalogId);
            Assert.Equal("Aquila concept art", row.DisplayName);
            Assert.Equal("goodies_pc", row.SourceArchive);
            Assert.False(row.ExportPresent);
            Assert.True(row.IsUnresolved);
        }

        [Fact]
        public void BuildPlan_RejectsSelectionAboveBoundBeforeResolvingRows()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModProjectSelectionEntry[] selection = Enumerable.Range(0, 101)
                .Select(index => new ModProjectSelectionEntry("texture", $"texture:invented-{index}"))
                .ToArray();

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectPlannerService.BuildPlan(snapshot, selection));

            Assert.Contains("at most 100", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void BuildPlan_IsDeterministicUnderSelectionOrder()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            var forward = new[]
            {
                new ModProjectSelectionEntry("texture", "texture:textures/texture_missing.tga"),
                new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga"),
            };
            var backward = forward.Reverse().ToArray();

            ModProjectPlan first = ModProjectPlannerService.BuildPlan(snapshot, forward);
            ModProjectPlan second = ModProjectPlannerService.BuildPlan(snapshot, backward);

            Assert.Equal(
                first.Assets.Select(asset => asset.CatalogId).ToArray(),
                second.Assets.Select(asset => asset.CatalogId).ToArray());
        }

        [Fact]
        public void Export_WritesDeterministicJsonAndOptionalTsvWithoutCopyingAssets()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [
                    new ModProjectSelectionEntry("mesh", "mesh:ship_body.msh"),
                    new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga"),
                ]);
            string outputDir = Path.Combine(_tempRoot, "project-receipt");
            Directory.CreateDirectory(outputDir);
            string outputPath = Path.Combine(outputDir, "aquila-hud-plan.json");
            string secondOutputPath = Path.Combine(outputDir, "aquila-hud-plan-copy.json");

            ModProjectPlanExportResult first = ModProjectPlannerService.Export(
                snapshot,
                plan,
                outputPath,
                includeTsv: true);
            byte[] firstJson = File.ReadAllBytes(outputPath);
            byte[] firstTsv = File.ReadAllBytes(Path.ChangeExtension(outputPath, ".tsv"));
            ModProjectPlanExportResult second = ModProjectPlannerService.Export(
                snapshot,
                plan,
                secondOutputPath,
                includeTsv: true);

            Assert.True(first.Success, first.Message);
            Assert.True(second.Success, second.Message);
            Assert.Equal(outputPath, first.ManifestPath);
            Assert.Equal(Path.ChangeExtension(outputPath, ".tsv"), first.TsvPath);
            Assert.Equal(firstJson, File.ReadAllBytes(secondOutputPath));
            Assert.Equal(firstTsv, File.ReadAllBytes(Path.ChangeExtension(secondOutputPath, ".tsv")));
            Assert.Equal(2, first.AssetCount);
            Assert.Equal(4, Directory.GetFiles(outputDir).Length);

            using JsonDocument document = JsonDocument.Parse(firstJson);
            JsonElement root = document.RootElement;
            Assert.Equal("mod-project-plan.v1", root.GetProperty("manifestVersion").GetString());
            Assert.Equal(plan.CatalogSha256, root.GetProperty("catalogSha256").GetString());
            Assert.Equal(2, root.GetProperty("assets").GetArrayLength());
            Assert.DoesNotContain(_tempRoot, System.Text.Encoding.UTF8.GetString(firstJson), StringComparison.OrdinalIgnoreCase);
            Assert.Contains("catalog_id", System.Text.Encoding.UTF8.GetString(firstTsv), StringComparison.Ordinal);
        }

        [Fact]
        public void BuildPlan_RejectsCatalogChangedAfterItWasLoaded()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            File.AppendAllText(Path.Combine(catalogDir, "catalog.json"), " ");

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectPlannerService.BuildPlan(
                    snapshot,
                    [new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga")]));

            Assert.Contains("catalog", error.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Contains("changed", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void BuildPlan_RejectsLocalExportChangedAfterCatalogLoad()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            File.WriteAllBytes(
                Path.Combine(_tempRoot, "exports", "texture_one.png"),
                new byte[] { 0x89, 0x50, 0x4E, 0x47, 0x7F });

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectPlannerService.BuildPlan(
                    snapshot,
                    [new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga")]));

            Assert.Contains("export", error.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Contains("changed", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void BuildPlan_RejectsDuplicateSelectionIdentity()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectPlannerService.BuildPlan(
                    snapshot,
                    [
                        new ModProjectSelectionEntry("mesh", "mesh:ship_body.msh"),
                        new ModProjectSelectionEntry("loose-mesh", "MESH:SHIP_BODY.MSH"),
                    ]));

            Assert.Contains("more than once", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void BuildPlan_RejectsLocalHashThatDoesNotMatchCatalogExpectedHash()
        {
            string catalogDir = CreateExportRoot();
            string catalogPath = Path.Combine(catalogDir, "catalog.json");
            string catalog = File.ReadAllText(catalogPath);
            File.WriteAllText(
                catalogPath,
                catalog.Replace(
                    "871923f8e5535ef938edc1ea710d5cf9e18637ce5d39feccef23030823993e4e",
                    new string('0', 64),
                    StringComparison.Ordinal));
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);

            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                ModProjectPlannerService.BuildPlan(
                    snapshot,
                    [new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga")]));

            Assert.Contains("no longer matches", error.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Export_RejectsOutputInsideInstalledGameWithoutWriting()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [new ModProjectSelectionEntry("texture", "texture:textures/texture_one.tga")]);
            string gameDir = Path.Combine(_tempRoot, "installed-game");
            Directory.CreateDirectory(Path.Combine(gameDir, "data"));
            File.WriteAllBytes(Path.Combine(gameDir, "BEA.exe"), [0x4D, 0x5A]);
            string outputPath = Path.Combine(gameDir, "project-plan.json");

            ModProjectPlanExportResult result = ModProjectPlannerService.Export(
                snapshot,
                plan,
                outputPath,
                includeTsv: true);

            Assert.False(result.Success);
            Assert.Contains("game", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.False(File.Exists(outputPath));
            Assert.False(File.Exists(Path.ChangeExtension(outputPath, ".tsv")));
        }

        [Fact]
        public void Export_RejectsExportDriftAfterPreviewWithoutWriting()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [new ModProjectSelectionEntry("mesh", "mesh:ship_body.msh")]);
            File.WriteAllBytes(
                Path.Combine(_tempRoot, "exports", "ship_body.msh_binary.fbx"),
                [0x46, 0x42, 0x58, 0x7F]);
            string outputPath = Path.Combine(_tempRoot, "drifted-plan.json");

            ModProjectPlanExportResult result = ModProjectPlannerService.Export(
                snapshot,
                plan,
                outputPath,
                includeTsv: false);

            Assert.False(result.Success);
            Assert.False(File.Exists(outputPath));
        }

        [Fact]
        public void Export_LeavesTsvAbsentWhenItWasNotRequested()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [new ModProjectSelectionEntry("goodie", "goodie:7")]);
            string outputPath = Path.Combine(_tempRoot, "json-only-plan.json");

            ModProjectPlanExportResult result = ModProjectPlannerService.Export(
                snapshot,
                plan,
                outputPath,
                includeTsv: false);

            Assert.True(result.Success, result.Message);
            Assert.True(File.Exists(outputPath));
            Assert.Null(result.TsvPath);
            Assert.False(File.Exists(Path.ChangeExtension(outputPath, ".tsv")));
        }

        [Fact]
        public void Export_RefusesToReplaceAnExistingReceipt()
        {
            string catalogDir = CreateExportRoot();
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalogDir);
            ModProjectPlan plan = ModProjectPlannerService.BuildPlan(
                snapshot,
                [new ModProjectSelectionEntry("goodie", "goodie:7")]);
            string outputPath = Path.Combine(_tempRoot, "existing-plan.json");
            byte[] original = [0x6B, 0x65, 0x65, 0x70];
            File.WriteAllBytes(outputPath, original);

            ModProjectPlanExportResult result = ModProjectPlannerService.Export(
                snapshot,
                plan,
                outputPath,
                includeTsv: true);

            Assert.False(result.Success);
            Assert.Contains("already exists", result.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Equal(original, File.ReadAllBytes(outputPath));
            Assert.False(File.Exists(Path.ChangeExtension(outputPath, ".tsv")));
        }
    }
}
