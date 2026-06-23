using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.Json;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class AssetCatalogServiceTests
    {
        [Fact]
        public void Load_ParsesGeneratedCatalogAndResolvesLocalExports()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            Assert.Equal(catalog.CatalogFilePath, snapshot.CatalogFilePath);
            Assert.Equal(3_820, snapshot.Summary.TotalCatalogEntries);
            Assert.Equal(828, snapshot.Summary.TextureCount);
            Assert.Equal(213, snapshot.Summary.LooseMeshCount);
            Assert.Equal(139, snapshot.Summary.EmbeddedMeshCount);
            Assert.Equal(3, snapshot.Summary.GoodieCount);

            AssetTextureItem texture = Assert.Single(snapshot.Textures);
            Assert.Equal("Texture One", texture.DisplayName);
            Assert.Equal("textures/texture_one.tga", texture.CanonicalRef);
            Assert.Equal("texture_one.png", texture.ExportFileName);
            Assert.True(texture.ExportExists);
            Assert.Equal(Path.Combine(catalog.RootPath, "exports", "texture_one.png"), texture.ExportPath);
            Assert.Equal("dxtntextures", texture.SourceGroup);
            Assert.Equal(7, texture.PackedReferenceCount);

            AssetLooseMeshItem mesh = Assert.Single(snapshot.LooseMeshes);
            Assert.Equal("ship_body.msh", mesh.DisplayName);
            Assert.Equal("ship_body.msh_binary.fbx", mesh.ExportFileName);
            Assert.True(mesh.ExportExists);
            Assert.Equal(4, mesh.PackedReferenceCount);
            Assert.False(mesh.ModelSummary.MetadataAvailable);
            Assert.Equal("FBX", mesh.ModelSummary.Format);

            Assert.Equal(3, snapshot.Goodies.Count);
            AssetGoodieItem modelGoodie = snapshot.Goodies[0];
            Assert.Equal(8, modelGoodie.Index);
            Assert.Equal("Model", modelGoodie.ContentKind);
            Assert.Equal("BE:A Unit-00 'Prototype'", modelGoodie.SourceTitle);
            Assert.Equal("ship_body.msh", modelGoodie.PrimaryMeshRef);
            Assert.True(modelGoodie.HasModel);
            Assert.True(modelGoodie.HasTexture);
            Assert.Equal("Complete level 100.", modelGoodie.UnlockRequirement);
            Assert.Equal("CCareer__UpdateGoodieStates 0x0041c470", modelGoodie.UnlockEvidenceLabel);
            Assert.True(modelGoodie.IsSourceGridVisible);
            Assert.Equal("FEPGoodies get_goodie_number 0x0045cb80", modelGoodie.WallVisibilityEvidenceLabel);
            Assert.Equal("Unit viewer", modelGoodie.WallGroupLabel);
            Assert.Equal("row 2, slot 1", modelGoodie.WallPositionLabel);

            AssetGoodieItem hiddenGoodie = snapshot.Goodies[1];
            Assert.Equal(71, hiddenGoodie.Index);
            Assert.Equal("Artwork", hiddenGoodie.ContentKind);
            Assert.False(hiddenGoodie.IsSourceGridVisible);
            Assert.Contains("does not expose this slot", hiddenGoodie.WallVisibilitySummary);
            Assert.Equal("Not on known wall", hiddenGoodie.WallGroupLabel);
            Assert.Equal("No wall position", hiddenGoodie.WallPositionLabel);

            AssetGoodieItem videoGoodie = snapshot.Goodies[2];
            Assert.Equal(232, videoGoodie.Index);
            Assert.Equal("Video", videoGoodie.ContentKind);
            Assert.Equal("33", videoGoodie.VideoSequenceId);
            Assert.True(videoGoodie.HasVideo);
            Assert.Equal("Watch cutscene 33 during normal play.", videoGoodie.UnlockRequirement);
            Assert.Equal("CGame cutscene handlers", videoGoodie.UnlockEvidenceLabel);
            Assert.True(videoGoodie.IsSourceGridVisible);
            Assert.Contains("FMV slot 33", videoGoodie.WallVisibilitySummary);
            Assert.Equal("Cutscenes", videoGoodie.WallGroupLabel);
            Assert.Equal("row 3, slot 32", videoGoodie.WallPositionLabel);
        }

        [Theory]
        [InlineData(66, "Earn C or better on 26 campaign missions.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(78, "Earn C or better on level 100.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(121, "Earn B or better on level 100.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(164, "Earn A or better on level 100.", "CCareer__UpdateGoodieStates 0x0041c470")]
        [InlineData(201, "Watch cutscene 1 during normal play.", "CGame cutscene handlers")]
        [InlineData(232, "Watch cutscene 33 during normal play.", "CGame cutscene handlers")]
        public void GoodieUnlockRequirementService_MapsSourceBackedRules(
            int index,
            string expectedSummary,
            string expectedEvidence)
        {
            GoodieUnlockRequirement requirement = GoodieUnlockRequirementService.Describe(index);

            Assert.Equal(expectedSummary, requirement.Summary);
            Assert.Equal(expectedEvidence, requirement.EvidenceLabel);
        }

        [Theory]
        [InlineData(70, true, "known in-game Goodies wall")]
        [InlineData(71, false, "does not expose this slot")]
        [InlineData(73, false, "does not expose this slot")]
        [InlineData(74, true, "developer item")]
        [InlineData(78, true, "concept art")]
        [InlineData(232, true, "FMV slot 33")]
        [InlineData(233, false, "Reserved save slot")]
        public void GoodieWallVisibilityService_MapsSourceGridQuirks(
            int index,
            bool expectedVisible,
            string expectedSummaryFragment)
        {
            GoodieWallVisibility visibility = GoodieWallVisibilityService.Describe(index);

            Assert.Equal(expectedVisible, visibility.IsSourceGridVisible);
            Assert.Contains(expectedSummaryFragment, visibility.Summary);
            Assert.NotEmpty(visibility.EvidenceLabel);
        }

        [Theory]
        [InlineData(0, 0, 0)]
        [InlineData(7, 0, 7)]
        [InlineData(8, 0, 66)]
        [InlineData(12, 0, 70)]
        [InlineData(13, 0, 74)]
        [InlineData(16, 0, 77)]
        [InlineData(0, 1, 8)]
        [InlineData(57, 1, 65)]
        [InlineData(0, 2, 201)]
        [InlineData(31, 2, 232)]
        [InlineData(0, 3, 78)]
        [InlineData(122, 3, 200)]
        public void GoodieWallGridMappingService_ResolvesCompiledVisibleWallCoordinates(
            int x,
            int y,
            int expectedIndex)
        {
            Assert.Equal(expectedIndex, GoodieWallGridMappingService.Resolve(x, y));
        }

        [Fact]
        public void GoodieWallGridMappingService_RaceRowSkipsHiddenGoodiesToDeveloperItems()
        {
            int[] topRowSequence = Enumerable.Range(8, 6)
                .Select(x => GoodieWallGridMappingService.Resolve(x, 0))
                .ToArray();

            Assert.Equal(new[] { 66, 67, 68, 69, 70, 74 }, topRowSequence);
            Assert.DoesNotContain(71, topRowSequence);
            Assert.DoesNotContain(72, topRowSequence);
            Assert.DoesNotContain(73, topRowSequence);
        }

        [Theory]
        [InlineData(17, 0)]
        [InlineData(58, 1)]
        [InlineData(32, 2)]
        [InlineData(123, 3)]
        [InlineData(0, 4)]
        public void GoodieWallGridMappingService_ReturnsMinusOneForUnmappedCoordinates(
            int x,
            int y)
        {
            Assert.Equal(-1, GoodieWallGridMappingService.Resolve(x, y));
        }

        [Theory]
        [InlineData(71)]
        [InlineData(72)]
        [InlineData(73)]
        public void GoodieWallGridMappingService_KeepsShippedHiddenArchivesOutOfVisibleIndexSet(int index)
        {
            Assert.False(GoodieWallGridMappingService.IsSourceGridVisible(index));
        }

        [Theory]
        [InlineData(0, "Character bios", "row 1, slot 1")]
        [InlineData(8, "Unit viewer", "row 2, slot 1")]
        [InlineData(66, "Race levels", "row 1, slot 9")]
        [InlineData(74, "Developer items", "row 1, slot 14")]
        [InlineData(78, "Concept art", "row 4, slot 1")]
        [InlineData(201, "Cutscenes", "row 3, slot 1")]
        [InlineData(232, "Cutscenes", "row 3, slot 32")]
        public void GoodieWallGridMappingService_LocatesVisibleWallSlots(
            int index,
            string expectedGroup,
            string expectedPosition)
        {
            GoodieWallSlot? slot = GoodieWallGridMappingService.Locate(index);

            Assert.NotNull(slot);
            Assert.Equal(index, slot.Index);
            Assert.Equal(expectedGroup, slot.GroupLabel);
            Assert.Equal(expectedPosition, slot.PositionLabel);
        }

        [Fact]
        public void GoodieWallGridMappingService_LocatesEveryVisibleIndexWithCompiledRoundTrip()
        {
            for (int index = 0; index <= 232; index++)
            {
                bool expectedVisible = index is >= 0 and <= 70 or >= 74 and <= 232;
                GoodieWallSlot? slot = GoodieWallGridMappingService.Locate(index);

                if (!expectedVisible)
                {
                    Assert.Null(slot);
                    continue;
                }

                Assert.NotNull(slot);
                Assert.Equal(index, slot.Index);
                Assert.Equal(index, GoodieWallGridMappingService.Resolve(slot.X, slot.Y));
                Assert.False(string.IsNullOrWhiteSpace(slot.GroupLabel));
                Assert.False(string.IsNullOrWhiteSpace(slot.PositionLabel));
            }
        }

        [Fact]
        public void GoodieWallGridMappingService_CompiledVisibleCoordinatesAreUnique()
        {
            HashSet<int> resolved = new();

            for (int y = 0; y <= 3; y++)
            {
                for (int x = 0; x <= 122; x++)
                {
                    int index = GoodieWallGridMappingService.Resolve(x, y);
                    if (index == -1)
                    {
                        continue;
                    }

                    Assert.InRange(index, 0, 232);
                    Assert.True(
                        resolved.Add(index),
                        $"Duplicate Goodies wall mapping for index {index} at x={x}, y={y}.");
                }
            }

            Assert.Equal(230, resolved.Count);
            Assert.DoesNotContain(71, resolved);
            Assert.DoesNotContain(72, resolved);
            Assert.DoesNotContain(73, resolved);
            Assert.Contains(232, resolved);
        }

        [Theory]
        [InlineData(71)]
        [InlineData(73)]
        [InlineData(233)]
        public void GoodieWallGridMappingService_ReturnsNullForHiddenOrReservedSlots(int index)
        {
            Assert.Null(GoodieWallGridMappingService.Locate(index));
        }

        [Fact]
        public void Load_AcceptsCatalogDirectoryOrCatalogFile()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create();

            AssetCatalogSnapshot byFile = new AssetCatalogService().Load(catalog.CatalogFilePath);
            AssetCatalogSnapshot byDirectory = new AssetCatalogService().Load(Path.GetDirectoryName(catalog.CatalogFilePath)!);

            Assert.Equal(byFile.CatalogFilePath, byDirectory.CatalogFilePath);
            Assert.Equal(byFile.Summary.TotalCatalogEntries, byDirectory.Summary.TotalCatalogEntries);
        }

        [Fact]
        public void Load_ReturnsEmptyForMissingCatalog()
        {
            string missing = Path.Combine(Path.GetTempPath(), "oce-missing-assets", Guid.NewGuid().ToString("N"));

            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(missing);

            Assert.Equal(string.Empty, snapshot.CatalogFilePath);
            Assert.Empty(snapshot.Textures);
            Assert.Empty(snapshot.LooseMeshes);
            Assert.Empty(snapshot.EmbeddedMeshes);
            Assert.Empty(snapshot.Goodies);
        }

        [Fact]
        public void ModelPreviewCoverage_SummarizesWireframeAvailability()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            AssetModelPreviewCoverage coverage = new AssetModelPreviewCoverageService().Build(snapshot, sampleLimit: 5);

            Assert.Equal(2, coverage.TotalModelRows);
            Assert.Equal(1, coverage.LooseMeshRows);
            Assert.Equal(1, coverage.EmbeddedMeshRows);
            Assert.Equal(2, coverage.ExistingExportRows);
            Assert.Equal(2, coverage.MetadataAvailableRows);
            Assert.Equal(2, coverage.WireframeAvailableRows);
            Assert.Equal(2, coverage.RowsWithTextureCoordinates);
            Assert.Equal(2, coverage.RowsWithTextureCoordinateIndices);
            Assert.Equal(6, coverage.TotalTextureCoordinates);
            Assert.Equal(6, coverage.TotalTextureCoordinateIndices);
            Assert.Equal(2, coverage.RowsWithNormals);
            Assert.Equal(2, coverage.RowsWithNormalIndices);
            Assert.Equal(6, coverage.TotalNormals);
            Assert.Equal(6, coverage.TotalNormalIndices);
            Assert.Equal(2, coverage.RowsWithNormalMappingModes);
            Assert.Equal(2, coverage.RowsWithNormalReferenceModes);
            Assert.Contains("ByPolygonVertex", coverage.NormalMappingModes);
            Assert.Contains("IndexToDirect", coverage.NormalReferenceModes);
            Assert.Equal(2, coverage.RowsWithVertexColors);
            Assert.Equal(2, coverage.RowsWithVertexColorIndices);
            Assert.Equal(6, coverage.TotalVertexColors);
            Assert.Equal(6, coverage.TotalVertexColorIndices);
            Assert.Equal(2, coverage.RowsWithVertexColorMappingModes);
            Assert.Equal(2, coverage.RowsWithVertexColorReferenceModes);
            Assert.Contains("ByPolygonVertex", coverage.VertexColorMappingModes);
            Assert.Contains("IndexToDirect", coverage.VertexColorReferenceModes);
            Assert.Equal(2, coverage.RowsWithTextureCoordinateMappingModes);
            Assert.Equal(2, coverage.RowsWithTextureCoordinateReferenceModes);
            Assert.Contains("ByPolygonVertex", coverage.TextureCoordinateMappingModes);
            Assert.Contains("IndexToDirect", coverage.TextureCoordinateReferenceModes);
            Assert.Equal(2, coverage.RowsWithMaterialLayers);
            Assert.Equal(2, coverage.RowsWithMaterialAssignmentIndices);
            Assert.Equal(2, coverage.TotalMaterialLayerNodes);
            Assert.Equal(2, coverage.TotalMaterialAssignmentIndices);
            Assert.Equal(2, coverage.RowsWithMaterialMappingModes);
            Assert.Equal(2, coverage.RowsWithMaterialReferenceModes);
            Assert.Contains("AllSame", coverage.MaterialMappingModes);
            Assert.Contains("IndexToDirect", coverage.MaterialReferenceModes);
            Assert.Equal(2, coverage.RowsWithObjectConnections);
            Assert.Equal(2, coverage.RowsWithPropertyConnections);
            Assert.Equal(2, coverage.RowsWithTextureToMaterialConnections);
            Assert.Equal(2, coverage.TotalObjectConnections);
            Assert.Equal(2, coverage.TotalPropertyConnections);
            Assert.Equal(2, coverage.TotalTextureToMaterialConnections);
            Assert.Equal(2, coverage.RowsWithTextureToMaterialSlotNames);
            Assert.Contains("DiffuseColor", coverage.TextureToMaterialSlotNames);
            Assert.Equal(2, coverage.RowsWithMaterials);
            Assert.Equal(2, coverage.RowsWithTextureBindings);
            Assert.Equal(2, coverage.TotalMaterialNodes);
            Assert.Equal(2, coverage.TotalTextureBindingNodes);
            Assert.Equal(2, coverage.RowsWithCatalogMatchedTextureBindingFiles);
            Assert.Equal(0, coverage.RowsWithoutCatalogMatchedTextureBindingFiles);
            Assert.Equal(2, coverage.RowsWithAllTextureBindingFilesCatalogMatched);
            Assert.Equal(0, coverage.RowsWithAnyMissingCatalogTextureBindingFiles);
            Assert.Equal(2, coverage.TotalCatalogMatchedTextureBindingFiles);
            Assert.Equal(0, coverage.UnreadableExportRows);
            Assert.Empty(coverage.UnmatchedSamples);
            Assert.All(coverage.Samples, sample =>
            {
                Assert.DoesNotContain(catalog.RootPath, sample.SourceLabel, StringComparison.OrdinalIgnoreCase);
                Assert.Equal(1, sample.MaterialCount);
                Assert.Equal(1, sample.TextureBindingCount);
                Assert.Contains("texture_one.png", sample.TextureBindingFileNames);
                Assert.Contains("Texture One", sample.CatalogMatchedTextureNames);
                Assert.Empty(sample.CatalogMissingTextureFileNames);
                Assert.Equal(3, sample.TextureCoordinateCount);
                Assert.Equal(3, sample.TextureCoordinateIndexCount);
                Assert.Equal(3, sample.NormalCount);
                Assert.Equal(3, sample.NormalIndexCount);
                Assert.Contains("ByPolygonVertex", sample.NormalMappingModes);
                Assert.Contains("IndexToDirect", sample.NormalReferenceModes);
                Assert.Equal(3, sample.VertexColorCount);
                Assert.Equal(3, sample.VertexColorIndexCount);
                Assert.Contains("ByPolygonVertex", sample.VertexColorMappingModes);
                Assert.Contains("IndexToDirect", sample.VertexColorReferenceModes);
                Assert.Contains("ByPolygonVertex", sample.TextureCoordinateMappingModes);
                Assert.Contains("IndexToDirect", sample.TextureCoordinateReferenceModes);
                Assert.Equal(1, sample.MaterialLayerCount);
                Assert.Equal(1, sample.MaterialAssignmentIndexCount);
                Assert.Contains("AllSame", sample.MaterialMappingModes);
                Assert.Contains("IndexToDirect", sample.MaterialReferenceModes);
                Assert.Equal(1, sample.ObjectConnectionCount);
                Assert.Equal(1, sample.PropertyConnectionCount);
                Assert.Equal(1, sample.TextureToMaterialConnectionCount);
                Assert.Contains("DiffuseColor", sample.TextureToMaterialSlotNames);
                Assert.True(sample.PreviewEdgeCount > 0);
            });
        }

        [Fact]
        public void ModelTextureLinks_ResolvesSelectedModelTextureNames()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            AssetLooseMeshItem mesh = Assert.Single(snapshot.LooseMeshes);

            AssetModelTextureLinks links = new AssetModelTextureLinkService().Build(snapshot.Textures, mesh.ModelSummary);

            Assert.Contains("texture_one.png", links.TextureBindingFileNames);
            Assert.Contains("Texture One", links.CatalogMatchedTextureNames);
            Assert.Single(links.CatalogMatchedTextureNames);
        }

        [Fact]
        public void ModelTextureLinks_IgnoresBlankBindingsAndMatchesPathVariants()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: false,
                SourceFileCount: 1,
                ExportFileCount: 0,
                PackedReferenceCount: 1);
            AssetModelSummary summary = new(
                Format: "Binary FBX",
                FormatVersion: 7400,
                ByteSize: 1,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 1,
                TextureBindingCount: 4,
                MaterialLayerCount: 0,
                MaterialAssignmentIndexCount: 0,
                MaterialMappingModes: Array.Empty<string>(),
                MaterialReferenceModes: Array.Empty<string>(),
                ObjectConnectionCount: 0,
                PropertyConnectionCount: 0,
                TextureToMaterialConnectionCount: 0,
                TextureToMaterialSlotNames: Array.Empty<string>(),
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames:
                [
                    " ",
                    "\t",
                    "default10.png",
                    "base_color_texture.png",
                    @"textures\texture_one.tga.png",
                    "Texture One.dds"
                ],
                VertexCount: 0,
                PolygonIndexCount: 0,
                NormalCount: 0,
                NormalIndexCount: 0,
                NormalMappingModes: Array.Empty<string>(),
                NormalReferenceModes: Array.Empty<string>(),
                VertexColorCount: 0,
                VertexColorIndexCount: 0,
                VertexColorMappingModes: Array.Empty<string>(),
                VertexColorReferenceModes: Array.Empty<string>(),
                TextureCoordinateCount: 0,
                TextureCoordinateIndexCount: 0,
                TextureCoordinateMappingModes: Array.Empty<string>(),
                TextureCoordinateReferenceModes: Array.Empty<string>(),
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: true,
                Status: "metadata available.");

            AssetModelTextureLinks links = new AssetModelTextureLinkService().Build([texture], summary);

            Assert.DoesNotContain(links.TextureBindingFileNames, string.IsNullOrWhiteSpace);
            Assert.DoesNotContain("default10.png", links.TextureBindingFileNames);
            Assert.DoesNotContain("base_color_texture.png", links.TextureBindingFileNames);
            Assert.Contains("texture_one.tga.png", links.TextureBindingFileNames);
            Assert.Contains("Texture One.dds", links.TextureBindingFileNames);
            Assert.Equal(["Texture One"], links.CatalogMatchedTextureNames);
            Assert.Empty(links.CatalogMissingTextureFileNames);
        }

        [Fact]
        public void ModelTextureLinks_ReportsCatalogMissingTextureBindings()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: false,
                SourceFileCount: 1,
                ExportFileCount: 0,
                PackedReferenceCount: 1);
            AssetModelSummary summary = new(
                Format: "Binary FBX",
                FormatVersion: 7400,
                ByteSize: 1,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 1,
                TextureBindingCount: 2,
                MaterialLayerCount: 0,
                MaterialAssignmentIndexCount: 0,
                MaterialMappingModes: Array.Empty<string>(),
                MaterialReferenceModes: Array.Empty<string>(),
                ObjectConnectionCount: 0,
                PropertyConnectionCount: 0,
                TextureToMaterialConnectionCount: 0,
                TextureToMaterialSlotNames: Array.Empty<string>(),
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames:
                [
                    "texture_one.png",
                    "sidecar_only_diffuse.png"
                ],
                VertexCount: 0,
                PolygonIndexCount: 0,
                NormalCount: 0,
                NormalIndexCount: 0,
                NormalMappingModes: Array.Empty<string>(),
                NormalReferenceModes: Array.Empty<string>(),
                VertexColorCount: 0,
                VertexColorIndexCount: 0,
                VertexColorMappingModes: Array.Empty<string>(),
                VertexColorReferenceModes: Array.Empty<string>(),
                TextureCoordinateCount: 0,
                TextureCoordinateIndexCount: 0,
                TextureCoordinateMappingModes: Array.Empty<string>(),
                TextureCoordinateReferenceModes: Array.Empty<string>(),
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: true,
                Status: "metadata available.");

            AssetModelTextureLinks links = new AssetModelTextureLinkService().Build([texture], summary);

            Assert.Equal(["Texture One"], links.CatalogMatchedTextureNames);
            Assert.Equal(["sidecar_only_diffuse.png"], links.CatalogMissingTextureFileNames);
        }

        [Fact]
        public void ModelPreviewCoverage_DistinguishesAllCatalogMatchedRowsFromSidecarNeededRows()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: false,
                SourceFileCount: 1,
                ExportFileCount: 0,
                PackedReferenceCount: 1);
            AssetModelSummary directSummary = CreateModelSummary(["texture_one.png"]);
            AssetModelSummary sidecarSummary = CreateModelSummary(["texture_one.png", "sidecar_only_diffuse.png"]);
            AssetCatalogSnapshot snapshot = new(
                string.Empty,
                AssetCatalogSummary.Empty,
                [texture],
                [
                    new AssetLooseMeshItem(
                        "mesh:direct",
                        "mesh/direct.msh",
                        "Direct model",
                        string.Empty,
                        "direct.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        directSummary),
                    new AssetLooseMeshItem(
                        "mesh:sidecar",
                        "mesh/sidecar.msh",
                        "Sidecar model",
                        string.Empty,
                        "sidecar.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        sidecarSummary)
                ],
                Array.Empty<AssetEmbeddedMeshItem>(),
                Array.Empty<AssetGoodieItem>());

            AssetModelPreviewCoverage coverage = new AssetModelPreviewCoverageService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(2, coverage.RowsWithCatalogMatchedTextureBindingFiles);
            Assert.Equal(2, coverage.RowsWithTextureBindings);
            Assert.Equal(1, coverage.RowsWithAllTextureBindingFilesCatalogMatched);
            Assert.Equal(1, coverage.RowsWithAnyMissingCatalogTextureBindingFiles);
            Assert.Contains(coverage.Samples, row =>
                row.Label == "Sidecar model" &&
                row.CatalogMissingTextureFileNames.SequenceEqual(["sidecar_only_diffuse.png"]));
        }

        [Fact]
        public void MaterialImportPlan_SummarizesCatalogMatchedModelTextureBindings()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            AssetMaterialImportPlan plan = new AssetMaterialImportPlanService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(2, plan.TotalModelRows);
            Assert.Equal(2, plan.MetadataAvailableRows);
            Assert.Equal(2, plan.RowsWithTextureBindings);
            Assert.Equal(2, plan.RowsWithAllTextureBindingsCatalogMatched);
            Assert.Equal(0, plan.RowsWithCatalogMissingTextureBindings);
            Assert.Equal(2, plan.TotalTextureBindingFiles);
            Assert.Equal(2, plan.TotalCatalogMatchedTextureBindingFiles);
            Assert.Equal(0, plan.TotalCatalogMissingTextureBindingFiles);
            Assert.Equal(0, plan.TotalUnresolvedTextureBindingFiles);
            Assert.Empty(plan.UnresolvedSamples);
            Assert.All(plan.Samples, row =>
            {
                Assert.DoesNotContain(catalog.RootPath, row.SourceLabel, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, row.Label, StringComparison.OrdinalIgnoreCase);
                Assert.Equal("All readable FBX texture binding files resolve through catalog texture rows.", row.Status);
            });
        }

        [Fact]
        public void MaterialImportPlan_UsesSidecarsForCatalogMissingTextureBindings()
        {
            string root = Path.Combine(Path.GetTempPath(), $"asset-material-plan-{Guid.NewGuid():N}");
            try
            {
                string looseMeshRoot = Path.Combine(root, "asset_export", "loose_meshes");
                string meshTextureRoot = Path.Combine(looseMeshRoot, "MeshTextures");
                Directory.CreateDirectory(meshTextureRoot);
                File.WriteAllText(Path.Combine(meshTextureRoot, "sidecar_only_diffuse.png"), "png");

                AssetTextureItem texture = new(
                    "texture:textures/texture_one.tga",
                    "textures/texture_one.tga",
                    "Texture One",
                    "dxtntextures",
                    string.Empty,
                    "texture_one.png",
                    ExportExists: false,
                    SourceFileCount: 1,
                    ExportFileCount: 0,
                    PackedReferenceCount: 1);
                AssetModelSummary directSummary = CreateModelSummary(["texture_one.png"]);
                AssetModelSummary sidecarSummary = CreateModelSummary(["texture_one.png", "sidecar_only_diffuse.tga"]);
                AssetCatalogSnapshot snapshot = new(
                    string.Empty,
                    AssetCatalogSummary.Empty,
                    [texture],
                    [
                        new AssetLooseMeshItem(
                            "mesh:direct",
                            "mesh/direct.msh",
                            "Direct model",
                            Path.Combine(looseMeshRoot, "direct.fbx"),
                            "direct.fbx",
                            ExportExists: true,
                            SourceFileCount: 1,
                            ExportFileCount: 1,
                            PackedReferenceCount: 1,
                            directSummary),
                        new AssetLooseMeshItem(
                            "mesh:sidecar",
                            "mesh/sidecar.msh",
                            "Sidecar model",
                            Path.Combine(looseMeshRoot, "sidecar.fbx"),
                            "sidecar.fbx",
                            ExportExists: true,
                            SourceFileCount: 1,
                            ExportFileCount: 1,
                            PackedReferenceCount: 1,
                            sidecarSummary)
                    ],
                    Array.Empty<AssetEmbeddedMeshItem>(),
                    Array.Empty<AssetGoodieItem>());

                AssetMaterialImportPlan plan = new AssetMaterialImportPlanService().Build(snapshot, sampleLimit: 10);

                Assert.Equal(2, plan.TotalModelRows);
                Assert.Equal(3, plan.TotalTextureBindingFiles);
                Assert.Equal(2, plan.TotalCatalogMatchedTextureBindingFiles);
                Assert.Equal(1, plan.TotalCatalogMissingTextureBindingFiles);
                Assert.Equal(1, plan.RowsWithAllTextureBindingsCatalogMatched);
                Assert.Equal(1, plan.RowsWithCatalogMissingTextureBindings);
                Assert.Equal(1, plan.RowsWithSidecarTexturePreviews);
                Assert.Equal(1, plan.RowsWithCatalogMissingSidecarTexturePreviews);
                Assert.Equal(1, plan.TotalCatalogMissingSidecarTextureFiles);
                Assert.Equal(0, plan.TotalUnresolvedTextureBindingFiles);
                AssetMaterialImportPlanRow sidecarRow = Assert.Single(plan.Samples, row => row.Label == "Sidecar model");
                Assert.Equal(["sidecar_only_diffuse.tga"], sidecarRow.CatalogMissingTextureFileNames);
                Assert.Equal(["sidecar_only_diffuse.png"], sidecarRow.CatalogMissingSidecarTextureFileNames);
                Assert.Empty(sidecarRow.UnresolvedTextureBindingFileNames);
                Assert.Contains("sidecar texture previews", sidecarRow.Status, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void MaterialImportManifest_EmitsPerBindingCatalogResolutions()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            Assert.Equal(2, manifest.TotalModelRows);
            Assert.Equal(2, manifest.MetadataAvailableRows);
            Assert.Equal(2, manifest.RowsWithTextureBindings);
            Assert.Equal(2, manifest.RowsReadyForImport);
            Assert.Equal(0, manifest.RowsWithUnresolvedTextureBindings);
            Assert.Equal(2, manifest.TotalTextureBindingRows);
            Assert.Equal(2, manifest.CatalogResolvedTextureBindingRows);
            Assert.Equal(0, manifest.SidecarResolvedTextureBindingRows);
            Assert.Equal(0, manifest.UnresolvedTextureBindingRows);

            AssetMaterialImportManifestModelRow looseMesh = Assert.Single(manifest.Models, row => row.CatalogId == "mesh:ship_body.msh");
            Assert.Equal("ready", looseMesh.ImportReadiness);
            AssetModelTextureBindingResolution binding = Assert.Single(looseMesh.TextureBindings);
            Assert.Equal("texture_one.png", binding.BindingFileName);
            Assert.Equal("catalog", binding.ResolutionKind);
            Assert.Equal("texture:textures/texture_one.tga", binding.CatalogTextureId);
            Assert.Equal("Texture One", binding.CatalogTextureName);
            Assert.Equal("texture_one.png", binding.CatalogTextureExportFileName);
            Assert.True(binding.CatalogTextureExportExists);
            Assert.Empty(binding.SidecarTextureFileName);
            Assert.DoesNotContain(catalog.RootPath, looseMesh.SourceLabel, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(catalog.RootPath, looseMesh.ExportFileName, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(catalog.RootPath, binding.BindingFileName, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(catalog.RootPath, binding.CatalogTextureExportFileName, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void MaterialImportManifest_EmitsPerBindingSidecarResolutions()
        {
            string root = Path.Combine(Path.GetTempPath(), $"asset-material-manifest-{Guid.NewGuid():N}");
            try
            {
                string looseMeshRoot = Path.Combine(root, "asset_export", "loose_meshes");
                string meshTextureRoot = Path.Combine(looseMeshRoot, "MeshTextures");
                Directory.CreateDirectory(meshTextureRoot);
                File.WriteAllText(Path.Combine(meshTextureRoot, "sidecar_only_diffuse.png"), "png");

                AssetTextureItem texture = new(
                    "texture:textures/texture_one.tga",
                    "textures/texture_one.tga",
                    "Texture One",
                    "dxtntextures",
                    string.Empty,
                    "texture_one.png",
                    ExportExists: false,
                    SourceFileCount: 1,
                    ExportFileCount: 0,
                    PackedReferenceCount: 1);
                AssetCatalogSnapshot snapshot = new(
                    string.Empty,
                    AssetCatalogSummary.Empty,
                    [texture],
                    [
                        new AssetLooseMeshItem(
                            "mesh:sidecar",
                            "mesh/sidecar.msh",
                            "Sidecar model",
                            Path.Combine(looseMeshRoot, "sidecar.fbx"),
                            "sidecar.fbx",
                            ExportExists: true,
                            SourceFileCount: 1,
                            ExportFileCount: 1,
                            PackedReferenceCount: 1,
                            CreateModelSummary(["texture_one.png", "sidecar_only_diffuse.tga"]))
                    ],
                    Array.Empty<AssetEmbeddedMeshItem>(),
                    Array.Empty<AssetGoodieItem>());

                AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

                Assert.Equal(1, manifest.TotalModelRows);
                Assert.Equal(1, manifest.RowsReadyForImport);
                Assert.Equal(2, manifest.TotalTextureBindingRows);
                Assert.Equal(1, manifest.CatalogResolvedTextureBindingRows);
                Assert.Equal(1, manifest.SidecarResolvedTextureBindingRows);
                Assert.Equal(0, manifest.UnresolvedTextureBindingRows);
                AssetMaterialImportManifestModelRow model = Assert.Single(manifest.Models);
                Assert.Equal("ready", model.ImportReadiness);
                AssetModelTextureBindingResolution sidecarBinding = Assert.Single(model.TextureBindings, binding => binding.ResolutionKind == "sidecar");
                Assert.Equal("sidecar_only_diffuse.tga", sidecarBinding.BindingFileName);
                Assert.Equal("sidecar_only_diffuse.png", sidecarBinding.SidecarTextureFileName);
                Assert.False(sidecarBinding.SidecarExactFileNameMatch);
                Assert.Empty(sidecarBinding.CatalogTextureId);
                Assert.DoesNotContain(root, model.SourceLabel, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(root, model.ExportFileName, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(root, sidecarBinding.BindingFileName, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(root, sidecarBinding.SidecarTextureFileName, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void MaterialImportDryRunPlan_EmitsRelativeCatalogOperations()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            AssetMaterialImportDryRunPlan plan = new AssetMaterialImportDryRunPlanService().Build(manifest);

            Assert.Equal(2, plan.TotalModelOperations);
            Assert.Equal(2, plan.ReadyModelOperations);
            Assert.Equal(0, plan.BlockedModelOperations);
            Assert.Equal(2, plan.TotalTextureOperations);
            Assert.Equal(2, plan.CatalogTextureOperations);
            Assert.Equal(0, plan.SidecarTextureOperations);
            Assert.Equal(0, plan.UnresolvedTextureOperations);
            Assert.All(plan.ModelOperations, operation =>
            {
                Assert.True(operation.ReadyForImport);
                Assert.Equal("ready", operation.ImportReadiness);
                Assert.StartsWith("models/", operation.DestinationRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, operation.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, operation.ExportFileName, StringComparison.OrdinalIgnoreCase);

                AssetMaterialImportDryRunTextureOperation textureOperation = Assert.Single(operation.TextureOperations);
                Assert.Equal("catalog", textureOperation.ResolutionKind);
                Assert.Equal("texture_one.png", textureOperation.BindingFileName);
                Assert.Equal("texture_one.png", textureOperation.SourceFileName);
                Assert.True(textureOperation.SourceAvailable);
                Assert.StartsWith("textures/catalog/", textureOperation.DestinationRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, textureOperation.SourceToken, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, textureOperation.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);
            });
        }

        [Fact]
        public void MaterialImportDryRunPlan_UsesSidecarFallbackWithoutAbsolutePaths()
        {
            string root = Path.Combine(Path.GetTempPath(), $"asset-material-dry-run-{Guid.NewGuid():N}");
            try
            {
                string looseMeshRoot = Path.Combine(root, "asset_export", "loose_meshes");
                string meshTextureRoot = Path.Combine(looseMeshRoot, "MeshTextures");
                Directory.CreateDirectory(meshTextureRoot);
                File.WriteAllText(Path.Combine(meshTextureRoot, "sidecar_only_diffuse.png"), "png");

                AssetTextureItem texture = new(
                    "texture:textures/texture_one.tga",
                    "textures/texture_one.tga",
                    "Texture One",
                    "dxtntextures",
                    string.Empty,
                    "texture_one.png",
                    ExportExists: false,
                    SourceFileCount: 1,
                    ExportFileCount: 0,
                    PackedReferenceCount: 1);
                AssetCatalogSnapshot snapshot = new(
                    string.Empty,
                    AssetCatalogSummary.Empty,
                    [texture],
                    [
                        new AssetLooseMeshItem(
                            "mesh:sidecar",
                            "mesh/sidecar.msh",
                            "Sidecar model",
                            Path.Combine(looseMeshRoot, "sidecar.fbx"),
                            "sidecar.fbx",
                            ExportExists: true,
                            SourceFileCount: 1,
                            ExportFileCount: 1,
                            PackedReferenceCount: 1,
                            CreateModelSummary(["texture_one.png", "sidecar_only_diffuse.tga"]))
                    ],
                    Array.Empty<AssetEmbeddedMeshItem>(),
                    Array.Empty<AssetGoodieItem>());
                AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

                AssetMaterialImportDryRunPlan plan = new AssetMaterialImportDryRunPlanService().Build(manifest);

                Assert.Equal(1, plan.TotalModelOperations);
                Assert.Equal(1, plan.ReadyModelOperations);
                Assert.Equal(0, plan.BlockedModelOperations);
                Assert.Equal(2, plan.TotalTextureOperations);
                Assert.Equal(1, plan.CatalogTextureOperations);
                Assert.Equal(1, plan.SidecarTextureOperations);
                Assert.Equal(0, plan.UnresolvedTextureOperations);
                AssetMaterialImportDryRunModelOperation modelOperation = Assert.Single(plan.ModelOperations);
                Assert.Equal("models/loose_mesh/mesh_sidecar/sidecar.fbx", modelOperation.DestinationRelativePath);
                Assert.DoesNotContain(root, modelOperation.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);

                AssetMaterialImportDryRunTextureOperation sidecar = Assert.Single(
                    modelOperation.TextureOperations,
                    operation => operation.ResolutionKind == "sidecar");
                Assert.Equal("sidecar_only_diffuse.tga", sidecar.BindingFileName);
                Assert.Equal("sidecar_only_diffuse.png", sidecar.SourceFileName);
                Assert.Equal("sidecar_only_diffuse.png", sidecar.SourceToken);
                Assert.Equal("textures/sidecar/mesh_sidecar/sidecar_only_diffuse.png", sidecar.DestinationRelativePath);
                Assert.True(sidecar.SourceAvailable);
                Assert.DoesNotContain(root, sidecar.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void MaterialImportDryRunPlan_BlocksUnresolvedTextureBindings()
        {
            AssetCatalogSnapshot snapshot = new(
                string.Empty,
                AssetCatalogSummary.Empty,
                Array.Empty<AssetTextureItem>(),
                [
                    new AssetLooseMeshItem(
                        "mesh:missing",
                        "mesh/missing.msh",
                        "Missing texture model",
                        string.Empty,
                        "missing.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        CreateModelSummary(["missing_diffuse.png"]))
                ],
                Array.Empty<AssetEmbeddedMeshItem>(),
                Array.Empty<AssetGoodieItem>());
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            AssetMaterialImportDryRunPlan plan = new AssetMaterialImportDryRunPlanService().Build(manifest);

            Assert.Equal(1, plan.TotalModelOperations);
            Assert.Equal(0, plan.ReadyModelOperations);
            Assert.Equal(1, plan.BlockedModelOperations);
            Assert.Equal(1, plan.TotalTextureOperations);
            Assert.Equal(0, plan.CatalogTextureOperations);
            Assert.Equal(0, plan.SidecarTextureOperations);
            Assert.Equal(1, plan.UnresolvedTextureOperations);
            AssetMaterialImportDryRunModelOperation modelOperation = Assert.Single(plan.ModelOperations);
            Assert.False(modelOperation.ReadyForImport);
            Assert.Equal("unresolved-texture-bindings", modelOperation.ImportReadiness);
            AssetMaterialImportDryRunTextureOperation unresolved = Assert.Single(modelOperation.TextureOperations);
            Assert.Equal("unresolved", unresolved.ResolutionKind);
            Assert.Equal("missing_diffuse.png", unresolved.BindingFileName);
            Assert.Equal("missing_diffuse.png", unresolved.SourceToken);
            Assert.Equal(string.Empty, unresolved.SourceFileName);
            Assert.Equal(string.Empty, unresolved.DestinationRelativePath);
            Assert.False(unresolved.SourceAvailable);
        }

        [Fact]
        public void MaterialImportPackagePlan_EmitsDeduplicatedPackageFiles()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            AssetMaterialImportPackagePlan plan = new AssetMaterialImportPackagePlanService().Build(manifest);

            Assert.Equal(2, plan.TotalModelOperations);
            Assert.Equal(2, plan.ReadyPackageModelOperations);
            Assert.Equal(0, plan.BlockedPackageModelOperations);
            Assert.Equal(2, plan.TotalTextureReferences);
            Assert.Equal(2, plan.ResolvedTextureReferences);
            Assert.Equal(0, plan.UnresolvedTextureReferences);
            Assert.Equal(2, plan.ModelPackageFiles);
            Assert.Equal(1, plan.TexturePackageFiles);
            Assert.Equal(3, plan.TotalPackageFiles);
            Assert.Equal(1, plan.DuplicateTextureReferences);

            AssetMaterialImportPackageFile textureFile = Assert.Single(plan.PackageFiles, file => file.Role == "texture");
            Assert.Equal("textures/catalog/texture_textures_texture_one.tga/texture_one.png", textureFile.DestinationRelativePath);
            Assert.Equal("texture_one.png", textureFile.SourceFileName);
            Assert.Equal("catalog", textureFile.ResolutionKind);
            Assert.Equal(2, textureFile.ReferenceCount);

            Assert.All(plan.ModelOperations, operation =>
            {
                Assert.True(operation.ReadyForPackage);
                Assert.Equal("ready", operation.PackageStatus);
                Assert.StartsWith("models/", operation.DestinationRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, operation.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, operation.ExportFileName, StringComparison.OrdinalIgnoreCase);
            });
        }

        [Fact]
        public void MaterialImportPackageMaterializer_CopiesReadyFilesToOwnedOutputRoot()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationService service = new();

            AssetMaterialImportPackageMaterializationResult preflight = service.Preflight(snapshot, outputRoot);

            Assert.True(preflight.Completed);
            Assert.False(preflight.Executed);
            Assert.Equal(3, preflight.TotalPackageFiles);
            Assert.Equal(3, preflight.PlannedFiles);
            Assert.Equal(3, preflight.WouldCopyFiles);
            Assert.Equal(0, preflight.CopiedFiles);
            Assert.False(preflight.ManifestWritten);
            Assert.Equal("preflight-not-written", preflight.ManifestStatus);
            Assert.False(preflight.WorkOrderSidecarWritten);
            Assert.Equal(AssetMaterialImportPackageWorkOrderService.WorkOrderFileName, preflight.WorkOrderSidecarRelativePath);
            Assert.Equal("preflight-not-written", preflight.WorkOrderSidecarStatus);
            Assert.Equal(0, preflight.WorkOrderSidecarBytes);
            Assert.Equal(2, preflight.ModelFilesReady);
            Assert.Equal(1, preflight.TextureFilesReady);
            Assert.False(Directory.Exists(outputRoot));
            Assert.All(preflight.Files, file => Assert.Equal("would-copy", file.Status));

            AssetMaterialImportPackageMaterializationResult result = service.Materialize(snapshot, outputRoot);

            Assert.True(result.Completed);
            Assert.True(result.Executed);
            Assert.Equal(3, result.TotalPackageFiles);
            Assert.Equal(3, result.PlannedFiles);
            Assert.Equal(3, result.CopiedFiles);
            Assert.Equal(0, result.ExistingFilesSkipped);
            Assert.Equal(0, result.MissingSourceFiles);
            Assert.Equal(0, result.UnsafeDestinationFiles);
            Assert.True(result.ManifestWritten);
            Assert.Equal(AssetMaterialImportPackageMaterializationService.ManifestFileName, result.ManifestRelativePath);
            Assert.Equal("written", result.ManifestStatus);
            Assert.True(result.ManifestBytes > 0);
            Assert.True(result.WorkOrderSidecarWritten);
            Assert.Equal(AssetMaterialImportPackageWorkOrderService.WorkOrderFileName, result.WorkOrderSidecarRelativePath);
            Assert.Equal("written", result.WorkOrderSidecarStatus);
            Assert.True(result.WorkOrderSidecarBytes > 0);
            Assert.True(result.ImporterDryRunSidecarWritten);
            Assert.Equal(AssetMaterialImportPackageImporterDryRunService.DryRunFileName, result.ImporterDryRunSidecarRelativePath);
            Assert.Equal("written", result.ImporterDryRunSidecarStatus);
            Assert.True(result.ImporterDryRunSidecarBytes > 0);
            Assert.Equal(2, result.ModelFilesReady);
            Assert.Equal(1, result.TextureFilesReady);
            Assert.Equal(2, result.ModelFilesCopied);
            Assert.Equal(1, result.TextureFilesCopied);

            Assert.All(result.Files, file =>
            {
                Assert.Equal("copied", file.Status);
                Assert.DoesNotContain(catalog.RootPath, file.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, file.SourceFileName, StringComparison.OrdinalIgnoreCase);
                Assert.True(File.Exists(Path.Combine(outputRoot, file.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar))));
            });
            Assert.Contains(result.Files, file => file.Role == "model" && file.DestinationRelativePath.StartsWith("models/loose_mesh/", StringComparison.Ordinal));
            Assert.Contains(result.Files, file => file.Role == "model" && file.DestinationRelativePath.StartsWith("models/embedded_mesh/", StringComparison.Ordinal));
            Assert.Contains(result.Files, file => file.Role == "texture" && file.DestinationRelativePath.StartsWith("textures/catalog/", StringComparison.Ordinal));
            string manifestPath = Path.Combine(outputRoot, AssetMaterialImportPackageMaterializationService.ManifestFileName);
            Assert.True(File.Exists(manifestPath));
            string manifestJson = File.ReadAllText(manifestPath);
            Assert.DoesNotContain(catalog.RootPath, manifestJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument manifest = JsonDocument.Parse(manifestJson);
            Assert.Equal("onslaught.asset-material-package-manifest.v1", manifest.RootElement.GetProperty("schema").GetString());
            Assert.Equal(3, manifest.RootElement.GetProperty("totalPackageFiles").GetInt32());
            Assert.Equal(3, manifest.RootElement.GetProperty("files").GetArrayLength());
            Assert.Equal(2, manifest.RootElement.GetProperty("models").GetArrayLength());
            Assert.Equal(
                2,
                manifest.RootElement.GetProperty("models")
                    .EnumerateArray()
                    .Sum(model => model.GetProperty("textureReferences").GetArrayLength()));

            string workOrderSidecarPath = Path.Combine(outputRoot, AssetMaterialImportPackageWorkOrderService.WorkOrderFileName);
            Assert.True(File.Exists(workOrderSidecarPath));
            string workOrderSidecarJson = File.ReadAllText(workOrderSidecarPath);
            Assert.DoesNotContain(catalog.RootPath, workOrderSidecarJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument workOrderSidecar = JsonDocument.Parse(workOrderSidecarJson);
            Assert.Equal("onslaught.asset-material-package-work-order.v1", workOrderSidecar.RootElement.GetProperty("schema").GetString());
            JsonElement sidecarWorkOrder = workOrderSidecar.RootElement.GetProperty("materialPackageWorkOrder");
            Assert.True(sidecarWorkOrder.GetProperty("completed").GetBoolean());
            Assert.Equal(2, sidecarWorkOrder.GetProperty("workOrderModelRows").GetInt32());
            Assert.Equal(2, sidecarWorkOrder.GetProperty("readyWorkOrderModelRows").GetInt32());
            Assert.Equal(2, sidecarWorkOrder.GetProperty("readyTextureReferenceRows").GetInt32());

            string importerDryRunPath = Path.Combine(outputRoot, AssetMaterialImportPackageImporterDryRunService.DryRunFileName);
            Assert.True(File.Exists(importerDryRunPath));
            string importerDryRunJson = File.ReadAllText(importerDryRunPath);
            Assert.DoesNotContain(catalog.RootPath, importerDryRunJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, importerDryRunJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument importerDryRunSidecar = JsonDocument.Parse(importerDryRunJson);
            Assert.Equal("onslaught.asset-material-package-importer-dry-run.v1", importerDryRunSidecar.RootElement.GetProperty("schema").GetString());
            JsonElement sidecarDryRun = importerDryRunSidecar.RootElement.GetProperty("materialPackageImporterDryRun");
            Assert.True(sidecarDryRun.GetProperty("completed").GetBoolean());
            Assert.Equal(4, sidecarDryRun.GetProperty("plannedAdapterRows").GetInt32());
            Assert.Equal(4, sidecarDryRun.GetProperty("readyAdapterRows").GetInt32());
            Assert.Equal(4, sidecarDryRun.GetProperty("rows").GetArrayLength());
        }

        [Fact]
        public void MaterialImportPackageMaterializer_DoesNotOverwriteExistingOutputFiles()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationService service = new();

            AssetMaterialImportPackageMaterializationResult first = service.Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializationResult second = service.Materialize(snapshot, outputRoot);

            Assert.True(first.Completed);
            Assert.True(second.Completed);
            Assert.Equal(3, first.CopiedFiles);
            Assert.Equal(0, second.CopiedFiles);
            Assert.Equal(3, second.ExistingFilesSkipped);
            Assert.True(first.ManifestWritten);
            Assert.True(second.ManifestWritten);
            Assert.Equal("written", second.ManifestStatus);
            Assert.True(first.WorkOrderSidecarWritten);
            Assert.True(second.WorkOrderSidecarWritten);
            Assert.Equal("written", second.WorkOrderSidecarStatus);
            Assert.True(first.ImporterDryRunSidecarWritten);
            Assert.True(second.ImporterDryRunSidecarWritten);
            Assert.Equal("written", second.ImporterDryRunSidecarStatus);
            Assert.All(second.Files, file => Assert.Equal("skipped-existing", file.Status));
        }

        [Fact]
        public void MaterialImportPackageInspector_ValidatesManifestAndPayloadFiles()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);

            Assert.True(inspection.Completed);
            Assert.Equal("ok", inspection.ManifestStatus);
            Assert.True(inspection.ManifestExists);
            Assert.True(inspection.SchemaValid);
            Assert.False(inspection.ManifestContainsPackageRoot);
            Assert.Equal(3, inspection.DeclaredTotalPackageFiles);
            Assert.Equal(3, inspection.DeclaredPlannedFiles);
            Assert.Equal(3, inspection.ManifestFileRows);
            Assert.Equal(2, inspection.ManifestModelFileRows);
            Assert.Equal(1, inspection.ManifestTextureFileRows);
            Assert.Equal(2, inspection.ManifestModelGraphRows);
            Assert.Equal(2, inspection.ManifestReadyModelGraphRows);
            Assert.Equal(2, inspection.ManifestTextureReferenceRows);
            Assert.Equal(2, inspection.ManifestResolvedTextureReferenceRows);
            Assert.Equal(3, inspection.ExistingManifestFiles);
            Assert.Equal(0, inspection.MissingManifestFiles);
            Assert.Equal(0, inspection.ExtraPayloadFiles);
            Assert.Equal(0, inspection.UnsafeManifestPaths);
            Assert.Equal(0, inspection.UnsafeModelGraphPaths);
            Assert.Empty(inspection.Issues);
        }

        [Fact]
        public void MaterialImportPackageWorkOrder_BuildsImporterReadyRowsFromManifestGraph()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);

            AssetMaterialImportPackageWorkOrderResult workOrder =
                new AssetMaterialImportPackageWorkOrderService().Build(outputRoot);

            Assert.True(workOrder.Completed);
            Assert.Equal("ok", workOrder.ManifestStatus);
            Assert.True(workOrder.ManifestInspectionCompleted);
            Assert.Equal(2, workOrder.ManifestModelGraphRows);
            Assert.Equal(2, workOrder.ManifestReadyModelGraphRows);
            Assert.Equal(2, workOrder.WorkOrderModelRows);
            Assert.Equal(2, workOrder.ReadyWorkOrderModelRows);
            Assert.Equal(2, workOrder.TextureReferenceRows);
            Assert.Equal(2, workOrder.ResolvedTextureReferenceRows);
            Assert.Equal(2, workOrder.ReadyTextureReferenceRows);
            Assert.Equal(0, workOrder.MissingPackageFiles);
            Assert.Equal(0, workOrder.UnsafePackagePaths);
            Assert.False(workOrder.ManifestContainsPackageRoot);
            Assert.Empty(workOrder.Issues);

            Assert.All(workOrder.Models, model =>
            {
                Assert.True(model.ReadyForImporter);
                Assert.Equal("ready-for-importer", model.ImportReadiness);
                Assert.Equal("ready", model.PackageStatus);
                Assert.Equal("copied", model.ModelFileStatus);
                Assert.Equal("inside-package-root", model.ModelPathStatus);
                Assert.True(model.ModelPackageFileExists);
                Assert.Equal(1, model.TextureReferenceCount);
                Assert.Equal(1, model.ReadyTextureReferenceCount);
                Assert.StartsWith("models/", model.ModelDestinationRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("textures/catalog/", model.FirstTextureDestinationRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, model.ModelDestinationRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, model.ExportFileName, StringComparison.OrdinalIgnoreCase);
                AssetMaterialImportPackageWorkOrderTexture texture = Assert.Single(model.Textures);
                Assert.True(texture.ReadyForImporter);
                Assert.Equal("ready-for-importer", texture.TextureReadiness);
                Assert.Equal("copied", texture.PackageFileStatus);
                Assert.Equal("inside-package-root", texture.PackagePathStatus);
                Assert.True(texture.PackageFileExists);
                Assert.StartsWith("textures/catalog/", texture.DestinationRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, texture.DestinationRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, texture.SourceFileName, StringComparison.OrdinalIgnoreCase);
            });
        }

        [Fact]
        public void MaterialImportPackageWorkOrderSidecarValidation_AcceptsFreshSidecar()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);

            AssetMaterialImportPackageWorkOrderSidecarValidationResult validation =
                new AssetMaterialImportPackageWorkOrderService().ValidateSidecar(outputRoot);

            Assert.True(validation.Completed);
            Assert.Equal("ok", validation.SidecarStatus);
            Assert.True(validation.SidecarExists);
            Assert.True(validation.SidecarBytes > 0);
            Assert.Equal("onslaught.asset-material-package-work-order.v1", validation.Schema);
            Assert.True(validation.SchemaValid);
            Assert.False(validation.SidecarContainsPackageRoot);
            Assert.True(validation.SidecarCompletedFlag);
            Assert.True(validation.FreshWorkOrderCompleted);
            Assert.True(validation.WorkOrderMatchesFreshBuild);
            Assert.Equal(2, validation.SidecarWorkOrderModelRows);
            Assert.Equal(2, validation.FreshWorkOrderModelRows);
            Assert.Equal(2, validation.SidecarReadyWorkOrderModelRows);
            Assert.Equal(2, validation.FreshReadyWorkOrderModelRows);
            Assert.Equal(2, validation.SidecarTextureReferenceRows);
            Assert.Equal(2, validation.FreshTextureReferenceRows);
            Assert.Equal(2, validation.SidecarReadyTextureReferenceRows);
            Assert.Equal(2, validation.FreshReadyTextureReferenceRows);
            Assert.Equal(0, validation.SidecarMissingPackageFiles);
            Assert.Equal(0, validation.FreshMissingPackageFiles);
            Assert.Equal(0, validation.SidecarUnsafePackagePaths);
            Assert.Equal(0, validation.FreshUnsafePackagePaths);
            Assert.Empty(validation.Issues);
        }

        [Fact]
        public void MaterialImportPackageWorkOrderSidecarValidation_FailsWhenPayloadFileChangedAfterSidecarWrite()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageWorkOrderSidecarValidationResult validation =
                new AssetMaterialImportPackageWorkOrderService().ValidateSidecar(outputRoot);

            Assert.False(validation.Completed);
            Assert.Equal("stale-work-order-sidecar", validation.SidecarStatus);
            Assert.True(validation.SidecarExists);
            Assert.True(validation.SchemaValid);
            Assert.False(validation.SidecarContainsPackageRoot);
            Assert.True(validation.SidecarCompletedFlag);
            Assert.False(validation.FreshWorkOrderCompleted);
            Assert.False(validation.WorkOrderMatchesFreshBuild);
            Assert.Equal(2, validation.SidecarWorkOrderModelRows);
            Assert.Equal(2, validation.FreshWorkOrderModelRows);
            Assert.Equal(2, validation.SidecarReadyWorkOrderModelRows);
            Assert.Equal(1, validation.FreshReadyWorkOrderModelRows);
            Assert.Equal(0, validation.SidecarMissingPackageFiles);
            Assert.Equal(1, validation.FreshMissingPackageFiles);
            Assert.Contains(validation.Issues, issue =>
                issue.Role == "sidecar" &&
                issue.RelativePath == AssetMaterialImportPackageWorkOrderService.WorkOrderFileName &&
                issue.Status == "work-order-mismatch");
        }

        [Fact]
        public void MaterialImportPackageImporterBatch_BuildsFlatTasksFromValidatedSidecar()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);

            AssetMaterialImportPackageImporterBatchResult batch =
                new AssetMaterialImportPackageImporterBatchService().Build(outputRoot);

            Assert.True(batch.Completed);
            Assert.True(batch.SidecarValidated);
            Assert.True(batch.WorkOrderCompleted);
            Assert.Equal("ok", batch.SidecarStatus);
            Assert.Equal(2, batch.ModelTaskRows);
            Assert.Equal(2, batch.TextureTaskRows);
            Assert.Equal(4, batch.TotalTaskRows);
            Assert.Equal(4, batch.ReadyTaskRows);
            Assert.Equal(0, batch.BlockedTaskRows);
            Assert.Empty(batch.Issues);
            Assert.Equal([1, 2, 3, 4], batch.Tasks.Select(task => task.Ordinal).ToArray());
            Assert.Equal(2, batch.Tasks.Count(task => task.Role == "model"));
            Assert.Equal(2, batch.Tasks.Count(task => task.Role == "texture"));
            Assert.All(batch.Tasks, task =>
            {
                Assert.True(task.ReadyForImporter);
                Assert.Equal("ready-for-importer", task.TaskStatus);
                Assert.False(Path.IsPathRooted(task.PackageRelativePath));
                Assert.DoesNotContain("..", task.PackageRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, task.PackageRelativePath, StringComparison.OrdinalIgnoreCase);
            });
            Assert.All(batch.Tasks.Where(task => task.Role == "model"), task =>
                Assert.StartsWith("models/", task.PackageRelativePath, StringComparison.Ordinal));
            Assert.All(batch.Tasks.Where(task => task.Role == "texture"), task =>
                Assert.StartsWith("textures/catalog/", task.PackageRelativePath, StringComparison.Ordinal));
        }

        [Fact]
        public void MaterialImportPackageImporterDryRun_BuildsAdapterRowsFromValidatedBatch()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);

            AssetMaterialImportPackageImporterDryRunResult dryRun =
                new AssetMaterialImportPackageImporterDryRunService().Build(outputRoot);

            Assert.True(dryRun.Completed);
            Assert.True(dryRun.SourceBatchValidated);
            Assert.True(dryRun.SourceBatchCompleted);
            Assert.Equal("ok", dryRun.SourceBatchStatus);
            Assert.Equal(2, dryRun.ModelTaskRows);
            Assert.Equal(2, dryRun.TextureTaskRows);
            Assert.Equal(4, dryRun.TotalTaskRows);
            Assert.Equal(4, dryRun.ReadyTaskRows);
            Assert.Equal(0, dryRun.BlockedTaskRows);
            Assert.Equal(4, dryRun.PlannedAdapterRows);
            Assert.Equal(4, dryRun.ReadyAdapterRows);
            Assert.Empty(dryRun.Issues);
            Assert.Equal([1, 2, 3, 4], dryRun.Rows.Select(row => row.Ordinal).ToArray());
            Assert.Equal(2, dryRun.Rows.Count(row => row.Role == "model"));
            Assert.Equal(2, dryRun.Rows.Count(row => row.Role == "texture"));
            Assert.All(dryRun.Rows, row =>
            {
                Assert.True(row.ReadyForAdapter);
                Assert.Equal("ready-for-importer", row.TaskStatus);
                Assert.False(Path.IsPathRooted(row.PackageRelativePath));
                Assert.False(Path.IsPathRooted(row.AdapterRelativePath));
                Assert.StartsWith("importer-input/", row.AdapterRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain("..", row.PackageRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, row.PackageRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, row.AdapterRelativePath, StringComparison.OrdinalIgnoreCase);
            });
            Assert.All(dryRun.Rows.Where(row => row.Role == "model"), row =>
                Assert.Equal("queue-model-import", row.AdapterAction));
            Assert.All(dryRun.Rows.Where(row => row.Role == "texture"), row =>
                Assert.Equal("queue-texture-bind", row.AdapterAction));
        }

        [Fact]
        public void MaterialImportPackageImporterDryRunSidecarValidation_AcceptsFreshSidecar()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);

            AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation =
                new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(outputRoot);

            Assert.True(validation.Completed);
            Assert.Equal("ok", validation.SidecarStatus);
            Assert.True(validation.SidecarExists);
            Assert.True(validation.SchemaValid);
            Assert.Equal(AssetMaterialImportPackageImporterDryRunService.DryRunSchema, validation.Schema);
            Assert.False(validation.SidecarContainsPackageRoot);
            Assert.True(validation.SidecarCompletedFlag);
            Assert.True(validation.FreshDryRunCompleted);
            Assert.True(validation.DryRunMatchesFreshBuild);
            Assert.Equal(4, validation.SidecarPlannedAdapterRows);
            Assert.Equal(4, validation.FreshPlannedAdapterRows);
            Assert.Equal(4, validation.SidecarReadyAdapterRows);
            Assert.Equal(4, validation.FreshReadyAdapterRows);
            Assert.Equal(4, validation.SidecarTotalTaskRows);
            Assert.Equal(4, validation.FreshTotalTaskRows);
            Assert.Equal(4, validation.SidecarReadyTaskRows);
            Assert.Equal(4, validation.FreshReadyTaskRows);
            Assert.Equal(0, validation.SidecarBlockedTaskRows);
            Assert.Equal(0, validation.FreshBlockedTaskRows);
            Assert.Empty(validation.Issues);
        }

        [Fact]
        public void MaterialImportPackageImporterDryRunSidecarValidation_FailsWhenPayloadFileChangedAfterSidecarWrite()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageImporterDryRunSidecarValidationResult validation =
                new AssetMaterialImportPackageImporterDryRunService().ValidateSidecar(outputRoot);

            Assert.False(validation.Completed);
            Assert.Equal("stale-importer-dry-run-sidecar", validation.SidecarStatus);
            Assert.True(validation.SidecarExists);
            Assert.True(validation.SchemaValid);
            Assert.False(validation.SidecarContainsPackageRoot);
            Assert.True(validation.SidecarCompletedFlag);
            Assert.False(validation.FreshDryRunCompleted);
            Assert.False(validation.DryRunMatchesFreshBuild);
            Assert.Equal(4, validation.SidecarPlannedAdapterRows);
            Assert.Equal(0, validation.FreshPlannedAdapterRows);
            Assert.Equal(4, validation.SidecarReadyAdapterRows);
            Assert.Equal(0, validation.FreshReadyAdapterRows);
            Assert.Equal(4, validation.SidecarTotalTaskRows);
            Assert.Equal(0, validation.FreshTotalTaskRows);
            Assert.Equal(0, validation.FreshReadyTaskRows);
            Assert.Contains(validation.Issues, issue =>
                issue.Role == "sidecar" &&
                issue.RelativePath == AssetMaterialImportPackageImporterDryRunService.DryRunFileName &&
                issue.Status == "importer-dry-run-mismatch");
        }

        [Fact]
        public void MaterialImportPackageImporterInputMaterialization_StagesValidatedDryRunRows()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageImporterInputService service = new();

            AssetMaterialImportPackageImporterInputMaterializationResult preflight = service.Preflight(outputRoot);

            Assert.True(preflight.Completed);
            Assert.False(preflight.Executed);
            Assert.True(preflight.SourceDryRunSidecarValidated);
            Assert.True(preflight.SourceDryRunCompleted);
            Assert.Equal("ok", preflight.SourceDryRunSidecarStatus);
            Assert.Equal(4, preflight.PlannedAdapterRows);
            Assert.Equal(4, preflight.ReadyAdapterRows);
            Assert.Equal(4, preflight.InputRowsReady);
            Assert.Equal(2, preflight.ModelInputRows);
            Assert.Equal(2, preflight.TextureInputRows);
            Assert.Equal(3, preflight.UniqueAdapterFiles);
            Assert.Equal(3, preflight.WouldCopyFiles);
            Assert.Equal(1, preflight.WouldUsePlannedCopyRows);
            Assert.False(preflight.ManifestWritten);
            Assert.Equal("preflight-not-written", preflight.ManifestStatus);
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageImporterInputService.ImporterInputRootRelativePath)));
            Assert.All(preflight.Rows, row =>
            {
                Assert.StartsWith("importer-input/", row.AdapterRelativePath, StringComparison.Ordinal);
                Assert.False(Path.IsPathRooted(row.SourcePackageRelativePath));
                Assert.False(Path.IsPathRooted(row.AdapterRelativePath));
                Assert.DoesNotContain("..", row.SourcePackageRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain("..", row.AdapterRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, row.SourcePackageRelativePath, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, row.AdapterRelativePath, StringComparison.OrdinalIgnoreCase);
            });

            AssetMaterialImportPackageImporterInputMaterializationResult result = service.Materialize(outputRoot);

            Assert.True(result.Completed);
            Assert.True(result.Executed);
            Assert.True(result.ManifestWritten);
            Assert.Equal("written", result.ManifestStatus);
            Assert.Equal(4, result.PlannedAdapterRows);
            Assert.Equal(4, result.ReadyAdapterRows);
            Assert.Equal(4, result.InputRowsReady);
            Assert.Equal(3, result.UniqueAdapterFiles);
            Assert.Equal(3, result.CopiedFiles);
            Assert.Equal(1, result.ExistingFilesSkipped);
            Assert.Equal(0, result.ExistingHashMismatches);
            Assert.Equal(0, result.MissingSourceFiles);
            Assert.Equal(0, result.UnsafeSourcePaths);
            Assert.Equal(0, result.UnsafeDestinationPaths);
            Assert.Contains(result.Rows, row => row.Status == "skipped-existing" && row.Role == "texture");
            Assert.All(result.Rows, row =>
            {
                Assert.StartsWith("importer-input/", row.AdapterRelativePath, StringComparison.Ordinal);
                Assert.True(File.Exists(Path.Combine(outputRoot, row.AdapterRelativePath.Replace('/', Path.DirectorySeparatorChar))));
            });

            string manifestPath = Path.Combine(outputRoot, AssetMaterialImportPackageImporterInputService.ImporterInputManifestFileName);
            Assert.True(File.Exists(manifestPath));
            string manifestJson = File.ReadAllText(manifestPath);
            Assert.DoesNotContain(catalog.RootPath, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("sha256", manifestJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument manifest = JsonDocument.Parse(manifestJson);
            Assert.Equal(AssetMaterialImportPackageImporterInputService.ImporterInputManifestSchema, manifest.RootElement.GetProperty("schema").GetString());
            Assert.True(manifest.RootElement.GetProperty("completed").GetBoolean());
            Assert.Equal(4, manifest.RootElement.GetProperty("plannedAdapterRows").GetInt32());
            Assert.Equal(3, manifest.RootElement.GetProperty("uniqueAdapterFiles").GetInt32());
            Assert.Equal(4, manifest.RootElement.GetProperty("rows").GetArrayLength());

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);
            Assert.True(inspection.Completed);
            Assert.Equal(0, inspection.ExtraPayloadFiles);
        }

        [Fact]
        public void MaterialImportPackageImporterInputPlan_BuildsConsumerJobsFromStagedInput()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);

            AssetMaterialImportPackageImporterInputPlanResult plan =
                new AssetMaterialImportPackageImporterInputPlanService().Build(outputRoot);

            Assert.True(plan.Completed);
            Assert.Equal("ready", plan.ManifestStatus);
            Assert.True(plan.InputManifestSchemaValid);
            Assert.True(plan.InputManifestCompletedFlag);
            Assert.False(plan.ManifestContainsPackageRoot);
            Assert.False(plan.ManifestContainsHashToken);
            Assert.True(plan.SourceDryRunSidecarValidated);
            Assert.Equal("ok", plan.SourceDryRunSidecarStatus);
            Assert.Equal(4, plan.PlannedAdapterRows);
            Assert.Equal(4, plan.ReadyAdapterRows);
            Assert.Equal(4, plan.ManifestRows);
            Assert.Equal(2, plan.ModelJobRows);
            Assert.Equal(2, plan.TextureBindingJobRows);
            Assert.Equal(4, plan.TotalJobRows);
            Assert.Equal(4, plan.ReadyJobRows);
            Assert.Equal(0, plan.BlockedJobRows);
            Assert.Equal(3, plan.UniqueInputFiles);
            Assert.Equal(3, plan.ExistingUniqueInputFiles);
            Assert.Equal(0, plan.MissingInputFiles);
            Assert.Equal(0, plan.UnsafeInputPaths);
            Assert.Equal(2, plan.ReadableModelRows);
            Assert.Equal(2, plan.ModelGeometryRows);
            Assert.Equal(2, plan.ModelWireframeRows);
            Assert.Equal(2, plan.ReadableTextureBindingRows);
            Assert.Equal(1, plan.UniqueReadableTextureFiles);
            Assert.Empty(plan.Issues);

            Assert.All(plan.ModelJobs, model =>
            {
                Assert.Equal("import-model", model.Action);
                Assert.True(model.ReadyForImportPlan);
                Assert.Equal("ready-for-import-plan", model.PlanStatus);
                Assert.Equal("queue-model-import", model.AdapterAction);
                Assert.True(model.InputFileExists);
                Assert.Equal("inside-package-root", model.PathStatus);
                Assert.Equal(1, model.TextureBindingRows);
                Assert.Equal(1, model.UniqueTextureInputFiles);
                Assert.True(model.MetadataAvailable);
                Assert.True(model.GeometryCount > 0);
                Assert.True(model.WireframeAvailable);
                Assert.StartsWith("importer-input/models/", model.AdapterRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, model.AdapterRelativePath, StringComparison.OrdinalIgnoreCase);
            });

            Assert.All(plan.TextureBindingJobs, texture =>
            {
                Assert.Equal("bind-texture", texture.Action);
                Assert.True(texture.ReadyForImportPlan);
                Assert.Equal("ready-for-import-plan", texture.PlanStatus);
                Assert.Equal("queue-texture-bind", texture.AdapterAction);
                Assert.True(texture.InputFileExists);
                Assert.Equal("inside-package-root", texture.PathStatus);
                Assert.True(texture.ReadablePng);
                Assert.True(texture.Width > 0);
                Assert.True(texture.Height > 0);
                Assert.StartsWith("importer-input/textures/", texture.AdapterRelativePath, StringComparison.Ordinal);
                Assert.DoesNotContain(catalog.RootPath, texture.AdapterRelativePath, StringComparison.OrdinalIgnoreCase);
            });

            string serializedPlan = JsonSerializer.Serialize(plan);
            Assert.DoesNotContain(catalog.RootPath, serializedPlan, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, serializedPlan, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("sha256", serializedPlan, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void MaterialImportPackageRebuildPreview_WritesDeterministicObjAndBindingSidecars()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            AssetMaterialImportPackageRebuildPreviewService service = new();

            AssetMaterialImportPackageRebuildPreviewResult preflight = service.Preflight(outputRoot);

            Assert.True(preflight.Completed);
            Assert.False(preflight.Executed);
            Assert.True(preflight.SourceInputPlanCompleted);
            Assert.Equal("ready", preflight.SourceInputPlanStatus);
            Assert.Equal(2, preflight.SourceModelJobRows);
            Assert.Equal(2, preflight.SourceTextureBindingJobRows);
            Assert.Equal(2, preflight.ModelPreviewRows);
            Assert.Equal(2, preflight.ReadyPreviewRows);
            Assert.Equal(0, preflight.BlockedPreviewRows);
            Assert.Equal(2, preflight.WouldWritePreviewRows);
            Assert.Equal(0, preflight.WrittenPreviewRows);
            Assert.Equal(2, preflight.ObjFileRows);
            Assert.Equal(2, preflight.BindingSidecarRows);
            Assert.Equal(2, preflight.TextureBindingRows);
            Assert.Equal(6, preflight.PreviewVertexRows);
            Assert.Equal(6, preflight.PreviewEdgeRows);
            Assert.False(preflight.ManifestWritten);
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageRebuildPreviewService.WorkspaceRootRelativePath)));

            AssetMaterialImportPackageRebuildPreviewResult result = service.Materialize(outputRoot);

            Assert.True(result.Completed);
            Assert.True(result.Executed);
            Assert.True(result.ManifestWritten);
            Assert.Equal("written", result.ManifestStatus);
            Assert.Equal(2, result.WrittenPreviewRows);
            Assert.Equal(0, result.ExistingPreviewRows);
            Assert.Equal(0, result.BlockedExistingMismatches);
            Assert.Equal(0, result.MissingInputFiles);
            Assert.Equal(0, result.UnsafeOutputPaths);
            Assert.All(result.Models, model =>
            {
                Assert.True(model.ReadyForRebuildPreview);
                Assert.Equal("written", model.Status);
                Assert.StartsWith("importer-input/models/", model.ModelInputRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-preview/models/", model.ObjRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-preview/models/", model.BindingSidecarRelativePath, StringComparison.Ordinal);
                Assert.True(model.PreviewVertexCount > 0);
                Assert.True(model.PreviewEdgeCount > 0);
                Assert.True(model.TextureBindingRows > 0);
                string objPath = Path.Combine(outputRoot, model.ObjRelativePath.Replace('/', Path.DirectorySeparatorChar));
                string bindingSidecarPath = Path.Combine(outputRoot, model.BindingSidecarRelativePath.Replace('/', Path.DirectorySeparatorChar));
                Assert.True(File.Exists(objPath));
                Assert.True(File.Exists(bindingSidecarPath));
                Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(objPath)));
                Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(bindingSidecarPath)));
                string objText = File.ReadAllText(objPath);
                Assert.Contains("# onslaught asset material package rebuild preview obj v1", objText);
                Assert.Contains("v 0", objText);
                Assert.Contains("l 1 2", objText);
            });

            string manifestPath = Path.Combine(outputRoot, AssetMaterialImportPackageRebuildPreviewService.ManifestFileName);
            Assert.True(File.Exists(manifestPath));
            Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(manifestPath)));
            string manifestJson = File.ReadAllText(manifestPath);
            Assert.DoesNotContain(catalog.RootPath, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("sha256", manifestJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument manifest = JsonDocument.Parse(manifestJson);
            Assert.Equal(AssetMaterialImportPackageRebuildPreviewService.ManifestSchema, manifest.RootElement.GetProperty("schema").GetString());
            Assert.True(manifest.RootElement.GetProperty("completed").GetBoolean());
            Assert.Equal(2, manifest.RootElement.GetProperty("modelPreviewRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("objFileRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("bindingSidecarRows").GetInt32());

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);
            Assert.True(inspection.Completed);
            Assert.Equal(0, inspection.ExtraPayloadFiles);

            AssetMaterialImportPackageRebuildPreviewResult second = service.Materialize(outputRoot);

            Assert.True(second.Completed);
            Assert.Equal(0, second.WrittenPreviewRows);
            Assert.Equal(2, second.ExistingPreviewRows);
            Assert.All(second.Models, model => Assert.Equal("skipped-existing", model.Status));

            static bool StartsWithUtf8Bom(byte[] bytes)
            {
                return bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
            }
        }

        [Fact]
        public void MaterialImportPackageRebuildScene_WritesMeshMaterialSceneContracts()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildPreviewService().Materialize(outputRoot);
            AssetMaterialImportPackageRebuildSceneService service = new();

            AssetMaterialImportPackageRebuildSceneResult preflight = service.Preflight(outputRoot);

            Assert.True(preflight.Completed);
            Assert.False(preflight.Executed);
            Assert.True(preflight.SourceRebuildPreviewCompleted);
            Assert.Equal("preflight-not-written", preflight.ManifestStatus);
            Assert.Equal(2, preflight.SourceModelPreviewRows);
            Assert.Equal(2, preflight.SceneRows);
            Assert.Equal(2, preflight.ReadySceneRows);
            Assert.Equal(2, preflight.WouldWriteSceneRows);
            Assert.Equal(0, preflight.WrittenSceneRows);
            Assert.Equal(0, preflight.BlockedSceneRows);
            Assert.Equal(2, preflight.SourceObjFileRows);
            Assert.Equal(2, preflight.SourceBindingSidecarRows);
            Assert.Equal(2, preflight.TextureBindingRows);
            Assert.Equal(6, preflight.SceneVertexRows);
            Assert.Equal(6, preflight.SceneEdgeRows);
            Assert.True(preflight.FbxVertexRows >= preflight.SceneVertexRows);
            Assert.True(preflight.FbxPolygonIndexRows > 0);
            Assert.True(preflight.FbxNormalRows >= 0);
            Assert.True(preflight.FbxTextureCoordinateRows >= 0);
            Assert.Equal(0, preflight.MissingPreviewFiles);
            Assert.Equal(0, preflight.MissingModelInputFiles);
            Assert.Equal(0, preflight.InvalidPreviewFiles);
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageRebuildSceneService.WorkspaceRootRelativePath)));

            AssetMaterialImportPackageRebuildSceneResult result = service.Materialize(outputRoot);

            Assert.True(result.Completed);
            Assert.True(result.Executed);
            Assert.True(result.ManifestWritten);
            Assert.Equal("written", result.ManifestStatus);
            Assert.Equal(2, result.WrittenSceneRows);
            Assert.Equal(0, result.ExistingSceneRows);
            Assert.Equal(0, result.BlockedExistingMismatches);
            Assert.All(result.Scenes, scene =>
            {
                Assert.True(scene.ReadyForSceneContract);
                Assert.Equal("written", scene.Status);
                Assert.StartsWith("rebuild-preview/models/", scene.ObjRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-preview/models/", scene.BindingSidecarRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-scene/models/", scene.SceneRelativePath, StringComparison.Ordinal);
                Assert.True(scene.VertexCount > 0);
                Assert.True(scene.EdgeCount > 0);
                Assert.True(scene.TextureBindingRows > 0);
                Assert.NotNull(scene.Bounds);
                Assert.NotNull(scene.MeshContract);
                Assert.Equal("Binary FBX", scene.MeshContract!.Format);
                Assert.True(scene.MeshContract.VertexCount >= scene.VertexCount);
                Assert.True(scene.MeshContract.PolygonIndexCount > 0);
                Assert.True(scene.MeshContract.MaterialCount > 0);
                Assert.True(scene.MeshContract.TextureBindingCount > 0);
                Assert.NotEmpty(scene.MeshContract.TextureToMaterialSlotNames);

                string scenePath = Path.Combine(outputRoot, scene.SceneRelativePath.Replace('/', Path.DirectorySeparatorChar));
                Assert.True(File.Exists(scenePath));
                byte[] sceneBytes = File.ReadAllBytes(scenePath);
                Assert.False(StartsWithUtf8Bom(sceneBytes));
                string sceneJson = File.ReadAllText(scenePath);
                Assert.DoesNotContain(catalog.RootPath, sceneJson, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(outputRoot, sceneJson, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain("sha256", sceneJson, StringComparison.OrdinalIgnoreCase);
                using JsonDocument sceneDoc = JsonDocument.Parse(sceneJson);
                Assert.Equal(AssetMaterialImportPackageRebuildSceneService.SceneFileSchema, sceneDoc.RootElement.GetProperty("schema").GetString());
                Assert.Equal(scene.CatalogId, sceneDoc.RootElement.GetProperty("catalogId").GetString());
                Assert.Equal(scene.VertexCount, sceneDoc.RootElement.GetProperty("vertexCount").GetInt32());
                Assert.Equal(scene.EdgeCount, sceneDoc.RootElement.GetProperty("edgeCount").GetInt32());
                Assert.True(sceneDoc.RootElement.GetProperty("meshContract").GetProperty("polygonIndexCount").GetInt32() > 0);
                Assert.True(sceneDoc.RootElement.GetProperty("textures").GetArrayLength() > 0);
            });

            string manifestPath = Path.Combine(outputRoot, AssetMaterialImportPackageRebuildSceneService.ManifestFileName);
            Assert.True(File.Exists(manifestPath));
            Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(manifestPath)));
            string manifestJson = File.ReadAllText(manifestPath);
            Assert.DoesNotContain(catalog.RootPath, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("sha256", manifestJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument manifest = JsonDocument.Parse(manifestJson);
            Assert.Equal(AssetMaterialImportPackageRebuildSceneService.ManifestSchema, manifest.RootElement.GetProperty("schema").GetString());
            Assert.True(manifest.RootElement.GetProperty("completed").GetBoolean());
            Assert.Equal(2, manifest.RootElement.GetProperty("sceneRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("readySceneRows").GetInt32());
            Assert.True(manifest.RootElement.GetProperty("fbxPolygonIndexRows").GetInt32() > 0);
            Assert.True(manifest.RootElement.GetProperty("textureToMaterialConnectionRows").GetInt32() > 0);

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);
            Assert.True(inspection.Completed);
            Assert.Equal(0, inspection.ExtraPayloadFiles);

            AssetMaterialImportPackageRebuildSceneResult second = service.Materialize(outputRoot);

            Assert.True(second.Completed);
            Assert.Equal(0, second.WrittenSceneRows);
            Assert.Equal(2, second.ExistingSceneRows);
            Assert.All(second.Scenes, scene => Assert.Equal("skipped-existing", scene.Status));

            static bool StartsWithUtf8Bom(byte[] bytes)
            {
                return bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
            }
        }

        [Fact]
        public void MaterialImportPackageRebuildMesh_WritesFaceBearingObjMtlOutputsFromSceneContracts()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildPreviewService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildSceneService().Materialize(outputRoot);
            AssetMaterialImportPackageRebuildMeshService service = new();

            AssetMaterialImportPackageRebuildMeshResult preflight = service.Preflight(outputRoot);

            Assert.True(preflight.Completed);
            Assert.False(preflight.Executed);
            Assert.True(preflight.SourceRebuildSceneCompleted);
            Assert.Equal("preflight-not-written", preflight.ManifestStatus);
            Assert.Equal(2, preflight.SourceSceneRows);
            Assert.Equal(2, preflight.SourceExistingSceneRows);
            Assert.Equal(2, preflight.MeshRows);
            Assert.Equal(2, preflight.ReadyMeshRows);
            Assert.Equal(2, preflight.WouldWriteMeshRows);
            Assert.Equal(0, preflight.WrittenMeshRows);
            Assert.Equal(0, preflight.BlockedMeshRows);
            Assert.Equal(2, preflight.ObjFileRows);
            Assert.Equal(2, preflight.MtlFileRows);
            Assert.Equal(2, preflight.CompleteMeshPayloadRows);
            Assert.Equal(0, preflight.PartialMeshPayloadRows);
            Assert.Equal(6, preflight.VertexRows);
            Assert.Equal(2, preflight.FaceRows);
            Assert.Equal(6, preflight.NormalRows);
            Assert.Equal(6, preflight.TextureCoordinateRows);
            Assert.Equal(2, preflight.TextureBindingRows);
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageRebuildMeshService.WorkspaceRootRelativePath)));

            AssetMaterialImportPackageRebuildMeshResult result = service.Materialize(outputRoot);

            Assert.True(result.Completed);
            Assert.True(result.Executed);
            Assert.True(result.ManifestWritten);
            Assert.Equal("written", result.ManifestStatus);
            Assert.Equal(2, result.WrittenMeshRows);
            Assert.Equal(0, result.ExistingMeshRows);
            Assert.Equal(0, result.BlockedExistingMismatches);
            Assert.All(result.Meshes, mesh =>
            {
                Assert.True(mesh.ReadyForMeshExport);
                Assert.Equal("written", mesh.Status);
                Assert.StartsWith("rebuild-scene/models/", mesh.SourceSceneRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-mesh/models/", mesh.ObjRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-mesh/models/", mesh.MtlRelativePath, StringComparison.Ordinal);
                Assert.Equal(3, mesh.VertexCount);
                Assert.Equal(1, mesh.FaceCount);
                Assert.Equal(3, mesh.NormalCount);
                Assert.Equal(3, mesh.TextureCoordinateCount);
                Assert.True(mesh.MaterialCount > 0);
                Assert.True(mesh.MeshPayloadAvailable);
                Assert.True(mesh.MeshPayloadComplete);
                Assert.Equal("complete-mesh-payload", mesh.MeshPayloadStatus);

                string objPath = Path.Combine(outputRoot, mesh.ObjRelativePath.Replace('/', Path.DirectorySeparatorChar));
                string mtlPath = Path.Combine(outputRoot, mesh.MtlRelativePath.Replace('/', Path.DirectorySeparatorChar));
                Assert.True(File.Exists(objPath));
                Assert.True(File.Exists(mtlPath));
                Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(objPath)));
                Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(mtlPath)));
                string obj = File.ReadAllText(objPath);
                string mtl = File.ReadAllText(mtlPath);
                Assert.DoesNotContain(catalog.RootPath, obj, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, mtl, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(outputRoot, obj, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(outputRoot, mtl, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain("sha256", obj, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain("sha256", mtl, StringComparison.OrdinalIgnoreCase);
                Assert.Contains("# onslaught asset material package rebuild mesh obj v1", obj, StringComparison.Ordinal);
                Assert.Contains("mtllib ", obj, StringComparison.Ordinal);
                Assert.Contains("\nv ", obj, StringComparison.Ordinal);
                Assert.Contains("\nvt ", obj, StringComparison.Ordinal);
                Assert.Contains("\nvn ", obj, StringComparison.Ordinal);
                Assert.Contains("\nusemtl ", obj, StringComparison.Ordinal);
                Assert.Contains("\nf ", obj, StringComparison.Ordinal);
                Assert.Contains("# onslaught asset material package rebuild mesh mtl v1", mtl, StringComparison.Ordinal);
                Assert.Contains("\nnewmtl ", mtl, StringComparison.Ordinal);
                Assert.Contains("\nmap_Kd importer-input/textures/", mtl, StringComparison.Ordinal);
            });

            string manifestPath = Path.Combine(outputRoot, AssetMaterialImportPackageRebuildMeshService.ManifestFileName);
            Assert.True(File.Exists(manifestPath));
            Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(manifestPath)));
            string manifestJson = File.ReadAllText(manifestPath);
            Assert.DoesNotContain(catalog.RootPath, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("sha256", manifestJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument manifest = JsonDocument.Parse(manifestJson);
            Assert.Equal(AssetMaterialImportPackageRebuildMeshService.ManifestSchema, manifest.RootElement.GetProperty("schema").GetString());
            Assert.True(manifest.RootElement.GetProperty("completed").GetBoolean());
            Assert.Equal(2, manifest.RootElement.GetProperty("meshRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("readyMeshRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("objFileRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("mtlFileRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("faceRows").GetInt32());

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);
            Assert.True(inspection.Completed);
            Assert.Equal(0, inspection.ExtraPayloadFiles);

            AssetMaterialImportPackageRebuildMeshResult second = service.Materialize(outputRoot);

            Assert.True(second.Completed);
            Assert.Equal(0, second.WrittenMeshRows);
            Assert.Equal(2, second.ExistingMeshRows);
            Assert.All(second.Meshes, mesh => Assert.Equal("skipped-existing", mesh.Status));

            static bool StartsWithUtf8Bom(byte[] bytes)
            {
                return bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
            }
        }

        [Fact]
        public void MaterialImportPackageRebuildMeshImport_ValidatesGeneratedObjMtlAsConsumerReady()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildPreviewService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildSceneService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildMeshService().Materialize(outputRoot);
            AssetMaterialImportPackageRebuildMeshImportService service = new();

            AssetMaterialImportPackageRebuildMeshImportResult preflight = service.Preflight(outputRoot);

            Assert.True(preflight.Completed);
            Assert.False(preflight.Executed);
            Assert.True(preflight.SourceRebuildMeshCompleted);
            Assert.Equal("preflight-not-written", preflight.ManifestStatus);
            Assert.Equal(2, preflight.ImportRows);
            Assert.Equal(2, preflight.ReadyImportRows);
            Assert.Equal(0, preflight.BlockedImportRows);
            Assert.Equal(2, preflight.ObjParsedRows);
            Assert.Equal(2, preflight.MtlParsedRows);
            Assert.Equal(2, preflight.ObjFileRows);
            Assert.Equal(2, preflight.MtlFileRows);
            Assert.Equal(6, preflight.VertexRows);
            Assert.Equal(2, preflight.FaceRows);
            Assert.Equal(6, preflight.NormalRows);
            Assert.Equal(6, preflight.TextureCoordinateRows);
            Assert.True(preflight.MaterialRows > 0);
            Assert.Equal(2, preflight.FaceMaterialUseRows);
            Assert.Equal(2, preflight.TextureReferenceRows);
            Assert.Equal(0, preflight.MissingTextureRows);
            Assert.Equal(0, preflight.CountMismatchRows);
            Assert.Equal(0, preflight.UndefinedMaterialUseRows);
            Assert.Equal(0, preflight.UnsafePathRows);
            Assert.Empty(preflight.Issues);
            Assert.False(File.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageRebuildMeshImportService.ManifestFileName)));

            AssetMaterialImportPackageRebuildMeshImportResult result = service.Materialize(outputRoot);

            Assert.True(result.Completed);
            Assert.True(result.Executed);
            Assert.True(result.ManifestWritten);
            Assert.Equal("written", result.ManifestStatus);
            Assert.All(result.Rows, row =>
            {
                Assert.True(row.ReadyForRebuildConsumer);
                Assert.True(row.ObjParsed);
                Assert.True(row.MtlParsed);
                Assert.Equal("ready-for-rebuild-consumer", row.Status);
                Assert.StartsWith("rebuild-mesh/models/", row.ObjRelativePath, StringComparison.Ordinal);
                Assert.StartsWith("rebuild-mesh/models/", row.MtlRelativePath, StringComparison.Ordinal);
                Assert.Equal(3, row.VertexCount);
                Assert.Equal(1, row.FaceCount);
                Assert.Equal(3, row.NormalCount);
                Assert.Equal(3, row.TextureCoordinateCount);
                Assert.True(row.MaterialCount > 0);
                Assert.Equal(1, row.FaceMaterialUseRows);
                Assert.Equal(1, row.TextureReferenceRows);
                Assert.Equal(0, row.MissingTextureRows);
                Assert.False(row.CountMismatch);
                Assert.Equal(0, row.UndefinedMaterialUseRows);
                Assert.Equal(0, row.UnsafePathRows);
            });

            string manifestPath = Path.Combine(outputRoot, AssetMaterialImportPackageRebuildMeshImportService.ManifestFileName);
            Assert.True(File.Exists(manifestPath));
            Assert.False(StartsWithUtf8Bom(File.ReadAllBytes(manifestPath)));
            string manifestJson = File.ReadAllText(manifestPath);
            Assert.DoesNotContain(catalog.RootPath, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(outputRoot, manifestJson, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("sha256", manifestJson, StringComparison.OrdinalIgnoreCase);
            using JsonDocument manifest = JsonDocument.Parse(manifestJson);
            Assert.Equal(AssetMaterialImportPackageRebuildMeshImportService.ManifestSchema, manifest.RootElement.GetProperty("schema").GetString());
            Assert.True(manifest.RootElement.GetProperty("completed").GetBoolean());
            Assert.Equal(2, manifest.RootElement.GetProperty("importRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("readyImportRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("objParsedRows").GetInt32());
            Assert.Equal(2, manifest.RootElement.GetProperty("mtlParsedRows").GetInt32());
            Assert.Equal(0, manifest.RootElement.GetProperty("countMismatchRows").GetInt32());
            Assert.Equal(0, manifest.RootElement.GetProperty("missingTextureRows").GetInt32());

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);
            Assert.True(inspection.Completed);
            Assert.Equal(0, inspection.ExtraPayloadFiles);

            static bool StartsWithUtf8Bom(byte[] bytes)
            {
                return bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF;
            }
        }

        [Fact]
        public void MaterialImportPackageRebuildMesh_RequiresExistingSceneContracts()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            new AssetMaterialImportPackageRebuildPreviewService().Materialize(outputRoot);

            AssetMaterialImportPackageRebuildMeshResult result =
                new AssetMaterialImportPackageRebuildMeshService().Preflight(outputRoot);

            Assert.False(result.Completed);
            Assert.True(result.SourceRebuildSceneCompleted);
            Assert.Equal(2, result.MeshRows);
            Assert.Equal(0, result.ReadyMeshRows);
            Assert.Equal(2, result.BlockedMeshRows);
            Assert.Equal(2, result.MissingSceneContractRows);
            Assert.Equal(0, result.ObjFileRows);
            Assert.Equal(0, result.MtlFileRows);
            Assert.All(result.Meshes, mesh => Assert.Equal("missing-scene-contract-file", mesh.Status));
            Assert.Contains(result.Issues, issue =>
                issue.Role == "scene" &&
                issue.Status == "missing-scene-contract-file");
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageRebuildMeshService.WorkspaceRootRelativePath)));
        }

        [Fact]
        public void MaterialImportPackageRebuildScene_BlocksCorruptPreviewOutputBeforeSceneContracts()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            AssetMaterialImportPackageRebuildPreviewResult preview =
                new AssetMaterialImportPackageRebuildPreviewService().Materialize(outputRoot);
            string objPath = Path.Combine(
                outputRoot,
                preview.Models[0].ObjRelativePath.Replace('/', Path.DirectorySeparatorChar));
            string[] corruptedLines = File.ReadAllLines(objPath)
                .Select(static line => line.StartsWith("l ", StringComparison.Ordinal) ? "l 1 9999" : line)
                .ToArray();
            File.WriteAllLines(objPath, corruptedLines);

            AssetMaterialImportPackageRebuildSceneResult result =
                new AssetMaterialImportPackageRebuildSceneService().Preflight(outputRoot);

            Assert.False(result.Completed);
            Assert.False(result.SourceRebuildPreviewCompleted);
            Assert.Equal(0, result.SceneRows);
            Assert.Equal(0, result.ReadySceneRows);
            Assert.Equal(0, result.BlockedSceneRows);
            Assert.Contains(result.Issues, issue =>
                issue.Role == "model" &&
                issue.Status == "blocked-existing-mismatch" &&
                issue.RelativePath == preview.Models[0].ObjRelativePath);
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageRebuildSceneService.WorkspaceRootRelativePath)));
        }

        [Fact]
        public void MaterialImportPackageImporterInputPlan_FailsWhenStagedInputFileIsMissing()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageImporterInputMaterializationResult input =
                new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);
            AssetMaterialImportPackageImporterInputRow removed = input.Rows.First(row => row.Role == "model");
            File.Delete(Path.Combine(outputRoot, removed.AdapterRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageImporterInputPlanResult plan =
                new AssetMaterialImportPackageImporterInputPlanService().Build(outputRoot);

            Assert.False(plan.Completed);
            Assert.Equal("issues-found", plan.ManifestStatus);
            Assert.True(plan.SourceDryRunSidecarValidated);
            Assert.Equal(1, plan.MissingInputFiles);
            Assert.Equal(1, plan.BlockedJobRows);
            Assert.Equal(3, plan.ReadyJobRows);
            Assert.Contains(plan.Issues, issue =>
                issue.Role == "model" &&
                issue.RelativePath == removed.AdapterRelativePath &&
                issue.Status == "missing-input-file");
        }

        [Fact]
        public void MaterialImportPackageImporterInputMaterialization_BlocksWhenDryRunSidecarIsStale()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageImporterInputMaterializationResult result =
                new AssetMaterialImportPackageImporterInputService().Materialize(outputRoot);

            Assert.False(result.Completed);
            Assert.True(result.Executed);
            Assert.False(result.SourceDryRunSidecarValidated);
            Assert.False(result.SourceDryRunCompleted);
            Assert.Equal("stale-importer-dry-run-sidecar", result.SourceDryRunSidecarStatus);
            Assert.False(result.ManifestWritten);
            Assert.Equal("stale-importer-dry-run-sidecar", result.ManifestStatus);
            Assert.Equal(0, result.InputRowsReady);
            Assert.Empty(result.Rows);
            Assert.Contains(result.Issues, issue =>
                issue.Role == "sidecar" &&
                issue.RelativePath == AssetMaterialImportPackageImporterDryRunService.DryRunFileName &&
                issue.Status == "importer-dry-run-mismatch");
            Assert.False(Directory.Exists(Path.Combine(outputRoot, AssetMaterialImportPackageImporterInputService.ImporterInputRootRelativePath)));
        }

        [Fact]
        public void MaterialImportPackageImporterBatch_BlocksWhenSidecarValidationFails()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageImporterBatchResult batch =
                new AssetMaterialImportPackageImporterBatchService().Build(outputRoot);

            Assert.False(batch.Completed);
            Assert.False(batch.SidecarValidated);
            Assert.False(batch.WorkOrderCompleted);
            Assert.Equal("stale-work-order-sidecar", batch.SidecarStatus);
            Assert.Equal(0, batch.TotalTaskRows);
            Assert.Empty(batch.Tasks);
            Assert.Contains(batch.Issues, issue =>
                issue.Role == "sidecar" &&
                issue.RelativePath == AssetMaterialImportPackageWorkOrderService.WorkOrderFileName &&
                issue.Status == "work-order-mismatch");
        }

        [Fact]
        public void MaterialImportPackageImporterDryRun_BlocksWhenSidecarValidationFails()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageImporterDryRunResult dryRun =
                new AssetMaterialImportPackageImporterDryRunService().Build(outputRoot);

            Assert.False(dryRun.Completed);
            Assert.False(dryRun.SourceBatchValidated);
            Assert.False(dryRun.SourceBatchCompleted);
            Assert.Equal("stale-work-order-sidecar", dryRun.SourceBatchStatus);
            Assert.Equal(0, dryRun.PlannedAdapterRows);
            Assert.Equal(0, dryRun.ReadyAdapterRows);
            Assert.Empty(dryRun.Rows);
            Assert.Contains(dryRun.Issues, issue =>
                issue.Role == "sidecar" &&
                issue.RelativePath == AssetMaterialImportPackageWorkOrderService.WorkOrderFileName &&
                issue.Status == "work-order-mismatch");
        }

        [Fact]
        public void MaterialImportPackageWorkOrder_BlocksImporterTasksWhenPayloadFileIsMissing()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageWorkOrderResult workOrder =
                new AssetMaterialImportPackageWorkOrderService().Build(outputRoot);

            Assert.False(workOrder.Completed);
            Assert.Equal("issues-found", workOrder.ManifestStatus);
            Assert.False(workOrder.ManifestInspectionCompleted);
            Assert.Equal(2, workOrder.WorkOrderModelRows);
            Assert.Equal(1, workOrder.ReadyWorkOrderModelRows);
            Assert.Equal(2, workOrder.TextureReferenceRows);
            Assert.Equal(2, workOrder.ReadyTextureReferenceRows);
            Assert.Equal(1, workOrder.MissingPackageFiles);
            Assert.Equal(0, workOrder.UnsafePackagePaths);
            Assert.Contains(workOrder.Issues, issue =>
                issue.Status == "missing-payload-file" &&
                issue.DestinationRelativePath == removedFile.DestinationRelativePath);

            AssetMaterialImportPackageWorkOrderModel blocked =
                Assert.Single(workOrder.Models, model => !model.ReadyForImporter);
            Assert.Equal("missing-model-package-file", blocked.ImportReadiness);
            Assert.False(blocked.ModelPackageFileExists);
            Assert.Equal(removedFile.DestinationRelativePath, blocked.ModelDestinationRelativePath);

            AssetMaterialImportPackageWorkOrderModel ready =
                Assert.Single(workOrder.Models, model => model.ReadyForImporter);
            Assert.Equal("ready-for-importer", ready.ImportReadiness);
        }

        [Fact]
        public void MaterialImportPackageInspector_FailsWhenPayloadFileIsMissing()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);
            string outputRoot = Path.Combine(catalog.RootPath, "material-package");
            AssetMaterialImportPackageMaterializationResult materialization =
                new AssetMaterialImportPackageMaterializationService().Materialize(snapshot, outputRoot);
            AssetMaterialImportPackageMaterializedFile removedFile = materialization.Files.First(file => file.Role == "model");
            File.Delete(Path.Combine(outputRoot, removedFile.DestinationRelativePath.Replace('/', Path.DirectorySeparatorChar)));

            AssetMaterialImportPackageInspectionResult inspection =
                new AssetMaterialImportPackageInspectionService().Inspect(outputRoot);

            Assert.False(inspection.Completed);
            Assert.Equal("issues-found", inspection.ManifestStatus);
            Assert.Equal(2, inspection.ExistingManifestFiles);
            Assert.Equal(1, inspection.MissingManifestFiles);
            Assert.Contains(inspection.Issues, issue =>
                issue.Status == "missing-payload-file" &&
                issue.DestinationRelativePath == removedFile.DestinationRelativePath);
        }

        [Fact]
        public void MaterialImportPackagePlan_BlocksUnresolvedTextureBindings()
        {
            AssetCatalogSnapshot snapshot = new(
                string.Empty,
                AssetCatalogSummary.Empty,
                Array.Empty<AssetTextureItem>(),
                [
                    new AssetLooseMeshItem(
                        "mesh:missing",
                        "mesh/missing.msh",
                        "Missing texture model",
                        string.Empty,
                        "missing.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        CreateModelSummary(["missing_diffuse.png"]))
                ],
                Array.Empty<AssetEmbeddedMeshItem>(),
                Array.Empty<AssetGoodieItem>());
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            AssetMaterialImportPackagePlan plan = new AssetMaterialImportPackagePlanService().Build(manifest);

            Assert.Equal(1, plan.TotalModelOperations);
            Assert.Equal(0, plan.ReadyPackageModelOperations);
            Assert.Equal(1, plan.BlockedPackageModelOperations);
            Assert.Equal(1, plan.TotalTextureReferences);
            Assert.Equal(0, plan.ResolvedTextureReferences);
            Assert.Equal(1, plan.UnresolvedTextureReferences);
            Assert.Equal(0, plan.ModelPackageFiles);
            Assert.Equal(0, plan.TexturePackageFiles);
            Assert.Equal(0, plan.TotalPackageFiles);

            AssetMaterialImportPackageModelOperation operation = Assert.Single(plan.ModelOperations);
            Assert.False(operation.ReadyForPackage);
            Assert.Equal("blocked-unresolved-textures", operation.PackageStatus);
            AssetMaterialImportPackageTextureReference texture = Assert.Single(operation.TextureReferences);
            Assert.Equal("unresolved", texture.ResolutionKind);
            Assert.Equal("missing_diffuse.png", texture.BindingFileName);
            Assert.Equal(string.Empty, texture.DestinationRelativePath);
            Assert.False(texture.SourceAvailable);
        }

        [Fact]
        public void MaterialImportPackagePlan_BlocksMissingModelExportsAndMetadata()
        {
            AssetTextureItem texture = new(
                "texture:textures/texture_one.tga",
                "textures/texture_one.tga",
                "Texture One",
                "dxtntextures",
                string.Empty,
                "texture_one.png",
                ExportExists: true,
                SourceFileCount: 1,
                ExportFileCount: 1,
                PackedReferenceCount: 1);
            AssetCatalogSnapshot snapshot = new(
                string.Empty,
                AssetCatalogSummary.Empty,
                [texture],
                [
                    new AssetLooseMeshItem(
                        "mesh:missing-export",
                        "mesh/missing_export.msh",
                        "Missing export model",
                        string.Empty,
                        "missing_export.fbx",
                        ExportExists: false,
                        SourceFileCount: 1,
                        ExportFileCount: 0,
                        PackedReferenceCount: 1,
                        CreateModelSummary(["texture_one.png"])),
                    new AssetLooseMeshItem(
                        "mesh:missing-metadata",
                        "mesh/missing_metadata.msh",
                        "Missing metadata model",
                        "missing_metadata.fbx",
                        "missing_metadata.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        AssetModelSummary.Unavailable(0, "Metadata unavailable."))
                ],
                Array.Empty<AssetEmbeddedMeshItem>(),
                Array.Empty<AssetGoodieItem>());
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            AssetMaterialImportPackagePlan plan = new AssetMaterialImportPackagePlanService().Build(manifest);

            Assert.Equal(2, plan.TotalModelOperations);
            Assert.Equal(0, plan.ReadyPackageModelOperations);
            Assert.Equal(2, plan.BlockedPackageModelOperations);
            Assert.Equal(1, plan.TotalTextureReferences);
            Assert.Equal(1, plan.ResolvedTextureReferences);
            Assert.Equal(0, plan.UnresolvedTextureReferences);
            Assert.Equal(0, plan.TotalPackageFiles);

            Assert.Contains(
                plan.ModelOperations,
                operation => operation.Label == "Missing export model" &&
                             operation.PackageStatus == "blocked-missing-model-export");
            Assert.Contains(
                plan.ModelOperations,
                operation => operation.Label == "Missing metadata model" &&
                             operation.PackageStatus == "blocked-missing-model-metadata");
        }

        [Fact]
        public void MaterialImportPackagePlan_BlocksModelsWithoutTextureBindings()
        {
            AssetCatalogSnapshot snapshot = new(
                string.Empty,
                AssetCatalogSummary.Empty,
                Array.Empty<AssetTextureItem>(),
                [
                    new AssetLooseMeshItem(
                        "mesh:no-textures",
                        "mesh/no_textures.msh",
                        "No texture model",
                        "no_textures.fbx",
                        "no_textures.fbx",
                        ExportExists: true,
                        SourceFileCount: 1,
                        ExportFileCount: 1,
                        PackedReferenceCount: 1,
                        CreateModelSummary([]))
                ],
                Array.Empty<AssetEmbeddedMeshItem>(),
                Array.Empty<AssetGoodieItem>());
            AssetMaterialImportManifest manifest = new AssetMaterialImportManifestService().Build(snapshot);

            AssetMaterialImportPackagePlan plan = new AssetMaterialImportPackagePlanService().Build(manifest);

            Assert.Equal(1, plan.TotalModelOperations);
            Assert.Equal(0, plan.ReadyPackageModelOperations);
            Assert.Equal(1, plan.BlockedPackageModelOperations);
            Assert.Equal(0, plan.TotalTextureReferences);
            Assert.Equal(0, plan.TotalPackageFiles);

            AssetMaterialImportPackageModelOperation operation = Assert.Single(plan.ModelOperations);
            Assert.False(operation.ReadyForPackage);
            Assert.Equal("blocked-no-texture-bindings", operation.PackageStatus);
            Assert.Empty(operation.TextureReferences);
        }

        [Fact]
        public void ModelTextureLinks_ResolvesSidecarTexturesFromExportRoot()
        {
            string root = Path.Combine(Path.GetTempPath(), $"asset-sidecars-{Guid.NewGuid():N}");
            try
            {
                string looseMeshRoot = Path.Combine(root, "asset_export", "loose_meshes");
                string embeddedMeshRoot = Path.Combine(root, "asset_export", "embedded_meshes");
                string meshTextureRoot = Path.Combine(looseMeshRoot, "MeshTextures");
                Directory.CreateDirectory(looseMeshRoot);
                Directory.CreateDirectory(embeddedMeshRoot);
                Directory.CreateDirectory(meshTextureRoot);
                File.WriteAllText(Path.Combine(meshTextureRoot, "texture_one.png"), "png");
                File.WriteAllText(Path.Combine(meshTextureRoot, "texture_two.png"), "png");
                File.WriteAllText(Path.Combine(meshTextureRoot, "notes.txt"), "ignore");

                AssetModelTextureLinkService service = new();
                IReadOnlyList<AssetModelSidecarTexture> looseMatches = service.ResolveSidecarTextures(
                    Path.Combine(looseMeshRoot, "ship_body.msh_binary.fbx"),
                    [@"textures\texture_one.png", "texture_two.tga"]);
                IReadOnlyList<AssetModelSidecarTexture> embeddedMatches = service.ResolveSidecarTextures(
                    Path.Combine(embeddedMeshRoot, "body00_binary.fbx"),
                    ["texture_one.png"]);

                Assert.Equal(2, looseMatches.Count);
                Assert.Contains(looseMatches, match => match.FileName == "texture_one.png" && match.ExactFileNameMatch);
                Assert.Contains(looseMatches, match => match.FileName == "texture_two.png" && !match.ExactFileNameMatch);
                Assert.Single(embeddedMatches);
                Assert.Equal("texture_one.png", embeddedMatches[0].FileName);
            }
            finally
            {
                if (Directory.Exists(root))
                {
                    Directory.Delete(root, recursive: true);
                }
            }
        }

        [Fact]
        public void GoodiePreviewCoverage_SummarizesGoodiePreviewReadiness()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            GoodiePreviewCoverage coverage = new GoodiePreviewCoverageService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(3, coverage.TotalGoodieRows);
            Assert.Equal(2, coverage.SourceGridVisibleRows);
            Assert.Equal(1, coverage.SourceGridHiddenRows);
            Assert.Equal(2, coverage.TextureBearingRows);
            Assert.Equal(2, coverage.TextureMatchedRows);
            Assert.Equal(2, coverage.TexturePreviewReadyRows);
            Assert.Equal(1, coverage.ModelBearingRows);
            Assert.Equal(1, coverage.ModelMatchedRows);
            Assert.Equal(1, coverage.ModelExportReadyRows);
            Assert.Equal(1, coverage.ModelWireframeReadyRows);
            Assert.Equal(1, coverage.VideoRows);
            Assert.Equal(1, coverage.VideoCatalogLinkedRows);
            Assert.Equal(0, coverage.RowsWithoutLocalPreview);
            Assert.Contains(coverage.Samples, row =>
                row.Index == 71 &&
                !row.IsSourceGridVisible &&
                row.TexturePreviewReady &&
                row.Status.Contains("not exposed", StringComparison.OrdinalIgnoreCase));
        }

        [Fact]
        public void ReadabilityCoverage_SummarizesTextureAndModelExportsWithoutLocalPaths()
        {
            using TempAssetCatalog catalog = TempAssetCatalog.Create(withModelPreviewExports: true);
            AssetCatalogSnapshot snapshot = new AssetCatalogService().Load(catalog.CatalogFilePath);

            AssetCatalogReadability readability = new AssetCatalogReadabilityService().Build(snapshot, sampleLimit: 10);

            Assert.Equal(1, readability.TextureRows);
            Assert.Equal(1, readability.TextureExportRows);
            Assert.Equal(1, readability.TextureReadablePngRows);
            Assert.Equal(0, readability.TextureMissingExportRows);
            Assert.Equal(0, readability.TextureUnreadableExportRows);
            AssetTextureReadabilityRow textureSample = Assert.Single(readability.TextureSamples);
            Assert.Equal(1, textureSample.Width);
            Assert.Equal(1, textureSample.Height);
            Assert.True(textureSample.ReadablePng);
            Assert.DoesNotContain(catalog.RootPath, textureSample.SourceLabel, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(catalog.RootPath, textureSample.Label, StringComparison.OrdinalIgnoreCase);

            Assert.Equal(2, readability.TotalModelRows);
            Assert.Equal(2, readability.ModelExportRows);
            Assert.Equal(2, readability.ModelMetadataAvailableRows);
            Assert.Equal(2, readability.ModelWireframeAvailableRows);
            Assert.Equal(0, readability.ModelMissingExportRows);
            Assert.Equal(0, readability.ModelUnreadableExportRows);
            Assert.All(readability.ModelSamples, sample =>
            {
                Assert.True(sample.MetadataAvailable);
                Assert.True(sample.WireframeAvailable);
                Assert.DoesNotContain(catalog.RootPath, sample.SourceLabel, StringComparison.OrdinalIgnoreCase);
                Assert.DoesNotContain(catalog.RootPath, sample.Label, StringComparison.OrdinalIgnoreCase);
            });
        }

        private sealed class TempAssetCatalog : IDisposable
        {
            public string RootPath { get; }
            public string CatalogFilePath { get; }

            private TempAssetCatalog(string rootPath, string catalogFilePath)
            {
                RootPath = rootPath;
                CatalogFilePath = catalogFilePath;
            }

            public static TempAssetCatalog Create(bool withModelPreviewExports = false)
            {
                string root = Path.Combine(Path.GetTempPath(), "oce-asset-catalog-tests", Guid.NewGuid().ToString("N"));
                string catalogDir = Path.Combine(root, "asset_catalog");
                string exportsDir = Path.Combine(root, "exports");
                Directory.CreateDirectory(catalogDir);
                Directory.CreateDirectory(exportsDir);
                File.WriteAllBytes(Path.Combine(exportsDir, "texture_one.png"), BuildMinimalPng());
                if (withModelPreviewExports)
                {
                    byte[] fbx = BuildMinimalBinaryFbx();
                    File.WriteAllBytes(Path.Combine(exportsDir, "ship_body.msh_binary.fbx"), fbx);
                    File.WriteAllBytes(Path.Combine(exportsDir, "body00_binary.fbx"), fbx);
                }
                else
                {
                    File.WriteAllText(Path.Combine(exportsDir, "ship_body.msh_binary.fbx"), "not a real fbx");
                }

                string catalogPath = Path.Combine(catalogDir, "catalog.json");
                File.WriteAllText(catalogPath, """
                {
                  "summary": {
                    "texture_catalog_entries": 828,
                    "loose_mesh_catalog_entries": 213,
                    "embedded_mesh_catalog_entries": 139,
                    "video_catalog_entries": 66,
                    "language_catalog_entries": 2571,
                    "goodie_catalog_entries": 3,
                    "total_catalog_entries": 3820
                  },
                  "textures": [
                    {
                      "catalog_id": "texture:textures/texture_one.tga",
                      "kind": "texture",
                      "canonical_ref": "textures/texture_one.tga",
                      "source_roots": ["dxtntextures"],
                      "export_png_paths": ["exports/texture_one.png"],
                      "source_aya_count": 2,
                      "export_png_count": 1,
                      "packed_text_ref_count": 5,
                      "gdie_ref_count": 2,
                      "total_packed_ref_count": 7,
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
                      "packed_reference_count": 3,
                      "gdie_ref_count": 1,
                      "total_packed_ref_count": 4,
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
                      "catalog_id": "goodie:008",
                      "kind": "goodie",
                      "index": 8,
                      "display_name": "Goodie 008 - BE:A Unit-00 'Prototype'",
                      "content_kind": "Model",
                      "source_title": "BE:A Unit-00 'Prototype'",
                      "source_archive": "goodie_08_res_PC.aya",
                      "gdie_family": "goodie_08_res_PC.aya",
                      "texture_refs": ["textures/texture_one.tga"],
                      "mesh_refs": ["ship_body.msh"],
                      "primary_texture_ref": "textures/texture_one.tga",
                      "primary_mesh_ref": "ship_body.msh",
                      "video_sequence_id": "",
                      "video_catalog_id": "",
                      "video_relative_path": ""
                    },
                    {
                      "catalog_id": "goodie:071",
                      "kind": "goodie",
                      "index": 71,
                      "display_name": "Goodie 071 - All Configurations",
                      "content_kind": "Artwork",
                      "source_title": "All Configurations",
                      "source_archive": "goodie_71_res_PC.aya",
                      "gdie_family": "goodie_71_res_PC.aya",
                      "texture_refs": ["textures/texture_one.tga"],
                      "mesh_refs": [],
                      "primary_texture_ref": "textures/texture_one.tga",
                      "primary_mesh_ref": "",
                      "video_sequence_id": "",
                      "video_catalog_id": "",
                      "video_relative_path": ""
                    },
                    {
                      "catalog_id": "goodie:232",
                      "kind": "goodie",
                      "index": 232,
                      "display_name": "Goodie 232 - Cutscene 33",
                      "content_kind": "Video",
                      "source_archive": "",
                      "gdie_family": "",
                      "texture_refs": [],
                      "mesh_refs": [],
                      "primary_texture_ref": "",
                      "primary_mesh_ref": "",
                      "video_sequence_id": "33",
                      "video_catalog_id": "video:cutscene:33",
                      "video_relative_path": "FMV/33.vid"
                    }
                  ]
                }
                """);

                return new TempAssetCatalog(root, catalogPath);
            }

            public void Dispose()
            {
                try
                {
                    if (Directory.Exists(RootPath))
                    {
                        Directory.Delete(RootPath, recursive: true);
                    }
                }
                catch
                {
                    // Best effort test cleanup only.
                }
            }
        }

        private static byte[] BuildMinimalPng()
        {
            return
            [
                137, 80, 78, 71, 13, 10, 26, 10,
                0, 0, 0, 13, 73, 72, 68, 82,
                0, 0, 0, 1, 0, 0, 0, 1,
                8, 6, 0, 0, 0, 31, 21, 196,
                137, 0, 0, 0, 13, 73, 68, 65,
                84, 120, 156, 99, 248, 207, 192,
                240, 31, 0, 5, 0, 1, 255, 137,
                153, 61, 29, 0, 0, 0, 0, 73,
                69, 78, 68, 174, 66, 96, 130
            ];
        }

        private static AssetModelSummary CreateModelSummary(IReadOnlyList<string> textureBindingFileNames)
        {
            return new AssetModelSummary(
                Format: "Binary FBX",
                FormatVersion: 7400,
                ByteSize: 1,
                GeometryCount: 0,
                ModelCount: 0,
                MaterialCount: 1,
                TextureBindingCount: textureBindingFileNames.Count,
                MaterialLayerCount: 1,
                MaterialAssignmentIndexCount: 1,
                MaterialMappingModes: ["AllSame"],
                MaterialReferenceModes: ["IndexToDirect"],
                ObjectConnectionCount: 1,
                PropertyConnectionCount: textureBindingFileNames.Count == 0 ? 0 : 1,
                TextureToMaterialConnectionCount: textureBindingFileNames.Count == 0 ? 0 : 1,
                TextureToMaterialSlotNames: textureBindingFileNames.Count == 0 ? Array.Empty<string>() : ["DiffuseColor"],
                MaterialNames: Array.Empty<string>(),
                TextureBindingNames: Array.Empty<string>(),
                TextureBindingFileNames: textureBindingFileNames,
                VertexCount: 3,
                PolygonIndexCount: 3,
                NormalCount: 3,
                NormalIndexCount: 3,
                NormalMappingModes: ["ByPolygonVertex"],
                NormalReferenceModes: ["IndexToDirect"],
                VertexColorCount: 3,
                VertexColorIndexCount: 3,
                VertexColorMappingModes: ["ByPolygonVertex"],
                VertexColorReferenceModes: ["IndexToDirect"],
                TextureCoordinateCount: 3,
                TextureCoordinateIndexCount: 3,
                TextureCoordinateMappingModes: ["ByPolygonVertex"],
                TextureCoordinateReferenceModes: ["IndexToDirect"],
                GeometryPreview: AssetModelGeometryPreview.Empty,
                MeshPayload: AssetModelMeshPayload.Empty,
                MetadataAvailable: true,
                Status: "metadata available.");
        }

        private static byte[] BuildMinimalBinaryFbx()
        {
            using MemoryStream stream = new();
            using BinaryWriter writer = new(stream, Encoding.ASCII, leaveOpen: true);

            writer.Write(Encoding.ASCII.GetBytes("Kaydara FBX Binary  "));
            writer.Write((byte)0);
            writer.Write((byte)0x1A);
            writer.Write((byte)0);
            writer.Write(7400);

            WriteNode(
                writer,
                "Objects",
                props: [],
                children:
                [
                    () => WriteNode(
                        writer,
                        "Geometry",
                        props:
                        [
                            () => WriteLongProperty(writer, 1),
                            () => WriteStringProperty(writer, "Triangle\0\u0001Geometry"),
                            () => WriteStringProperty(writer, "Mesh")
                        ],
                        children:
                        [
                            () => WriteNode(
                                writer,
                                "Vertices",
                                props:
                                [
                                    () => WriteDoubleArrayProperty(writer, [0, 0, 0, 1, 0, 0, 0, 1, 0])
                                ],
                                children: []),
                            () => WriteNode(
                                writer,
                                "PolygonVertexIndex",
                                props:
                                [
                                    () => WriteIntArrayProperty(writer, [0, 1, -3])
                                ],
                                children: []),
                            () => WriteNode(
                                writer,
                                "LayerElementNormal",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Normals",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [0, 0, 1, 0, 0, 1, 0, 0, 1])
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "NormalsIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2])
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementUV",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "UV",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [0, 0, 1, 0, 0, 1])
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "UVIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2])
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementColor",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "ByPolygonVertex")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Colors",
                                        props:
                                        [
                                            () => WriteDoubleArrayProperty(writer, [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1])
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ColorIndex",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0, 1, 2])
                                        ],
                                        children: [])
                                ]),
                            () => WriteNode(
                                writer,
                                "LayerElementMaterial",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "MappingInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "AllSame")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "ReferenceInformationType",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "IndexToDirect")
                                        ],
                                        children: []),
                                    () => WriteNode(
                                        writer,
                                        "Materials",
                                        props:
                                        [
                                            () => WriteIntArrayProperty(writer, [0])
                                        ],
                                        children: [])
                                ])
                        ]),
                    () => WriteNode(
                        writer,
                        "Material",
                        props:
                        [
                            () => WriteLongProperty(writer, 2),
                            () => WriteStringProperty(writer, "Material1\0\u0001Material"),
                            () => WriteStringProperty(writer, string.Empty)
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "Texture",
                        props:
                        [
                            () => WriteLongProperty(writer, 3),
                            () => WriteStringProperty(writer, "base_color_texture\0\u0001Texture"),
                            () => WriteStringProperty(writer, string.Empty)
                        ],
                        children:
                        [
                            () => WriteNode(
                                writer,
                                "Properties70",
                                props: [],
                                children:
                                [
                                    () => WriteNode(
                                        writer,
                                        "P",
                                        props:
                                        [
                                            () => WriteStringProperty(writer, "FileName"),
                                            () => WriteStringProperty(writer, "KString"),
                                            () => WriteStringProperty(writer, string.Empty),
                                            () => WriteStringProperty(writer, "A"),
                                            () => WriteStringProperty(writer, @"C:\exports\texture_one.png")
                                        ],
                                        children: [])
                                ])
                        ])
                ]);
            WriteNode(
                writer,
                "Connections",
                props: [],
                children:
                [
                    () => WriteNode(
                        writer,
                        "C",
                        props:
                        [
                            () => WriteStringProperty(writer, "OO"),
                            () => WriteLongProperty(writer, 2),
                            () => WriteLongProperty(writer, 1)
                        ],
                        children: []),
                    () => WriteNode(
                        writer,
                        "C",
                        props:
                        [
                            () => WriteStringProperty(writer, "OP"),
                            () => WriteLongProperty(writer, 3),
                            () => WriteLongProperty(writer, 2),
                            () => WriteStringProperty(writer, "DiffuseColor")
                        ],
                        children: [])
                ]);
            WriteSentinel(writer);

            return stream.ToArray();
        }

        private static void WriteNode(BinaryWriter writer, string name, Action[] props, Action[] children)
        {
            long headerPosition = writer.BaseStream.Position;
            writer.Write((uint)0);
            writer.Write((uint)props.Length);
            writer.Write((uint)0);
            writer.Write((byte)name.Length);
            writer.Write(Encoding.ASCII.GetBytes(name));

            long propertyStart = writer.BaseStream.Position;
            foreach (Action prop in props)
            {
                prop();
            }

            long propertyEnd = writer.BaseStream.Position;
            foreach (Action child in children)
            {
                child();
            }

            if (children.Length > 0)
            {
                WriteSentinel(writer);
            }

            long endPosition = writer.BaseStream.Position;
            writer.BaseStream.Position = headerPosition;
            writer.Write((uint)endPosition);
            writer.Write((uint)props.Length);
            writer.Write((uint)(propertyEnd - propertyStart));
            writer.Write((byte)name.Length);
            writer.BaseStream.Position = endPosition;
        }

        private static void WriteLongProperty(BinaryWriter writer, long value)
        {
            writer.Write((byte)'L');
            writer.Write(value);
        }

        private static void WriteStringProperty(BinaryWriter writer, string value)
        {
            byte[] bytes = Encoding.UTF8.GetBytes(value);
            writer.Write((byte)'S');
            writer.Write((uint)bytes.Length);
            writer.Write(bytes);
        }

        private static void WriteDoubleArrayProperty(BinaryWriter writer, double[] values)
        {
            writer.Write((byte)'d');
            writer.Write((uint)values.Length);
            writer.Write((uint)0);
            writer.Write((uint)(values.Length * sizeof(double)));
            foreach (double value in values)
            {
                writer.Write(value);
            }
        }

        private static void WriteIntArrayProperty(BinaryWriter writer, int[] values)
        {
            writer.Write((byte)'i');
            writer.Write((uint)values.Length);
            writer.Write((uint)0);
            writer.Write((uint)(values.Length * sizeof(int)));
            foreach (int value in values)
            {
                writer.Write(value);
            }
        }

        private static void WriteSentinel(BinaryWriter writer)
        {
            writer.Write(new byte[13]);
        }
    }
}
