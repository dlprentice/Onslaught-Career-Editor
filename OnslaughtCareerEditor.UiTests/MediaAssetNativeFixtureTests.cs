using System.Drawing;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

public class MediaAssetNativeFixtureTests
{
    [Test]
    public void Build_ProducesExactGeneratedMediaAndAssetContracts()
    {
        using var temp = new FixtureTempRoot();

        MediaAssetNativeFixture fixture = MediaAssetNativeFixtureBuilder.Build(
            Path.Combine(temp.Path, "fixture"));

        Assert.Multiple(() =>
        {
            Assert.That(MediaCatalogService.LooksLikeGameDirectory(fixture.MediaGameDirectory), Is.True);
            Assert.That(new FileInfo(Path.Combine(fixture.MediaGameDirectory, "BEA.exe")).Length, Is.Zero);
            Assert.That(fixture.Files, Has.Count.EqualTo(13));
            Assert.That(
                fixture.Files.Select(row => row.RelativePath),
                Is.EqualTo(MediaAssetNativeFixtureContract.ExpectedRelativePaths));
            Assert.That(fixture.Files, Has.All.Property(nameof(MediaAssetNativeFixtureFile.Sha256))
                .Match("^[0-9A-F]{64}$"));
        });

        MediaCatalogSnapshot media = new MediaCatalogService().Load(fixture.MediaGameDirectory);
        Assert.Multiple(() =>
        {
            Assert.That(media.AudioItems, Has.Count.EqualTo(4));
            Assert.That(media.AudioItems.Select(row => row.GroupName),
                Is.EquivalentTo(new[] { "Music", "Mission 110", "Tutorial", "Status Messages" }));
            Assert.That(media.AudioItems.Single(row => row.Name == "TUTORIAL_intro").DurationLabel, Is.Empty);
            Assert.That(media.VideoItems, Has.Count.EqualTo(4));
            Assert.That(media.VideoItems.Single(row => row.Name == "Credits Video").FilePath,
                Does.EndWith("UsTheMovie.vid").IgnoreCase);
            Assert.That(media.VideoItems.Single(row => row.Name == "Mission 101").SectionName,
                Is.EqualTo("Mission Briefings / Episode 1"));
        });

        AssetCatalogSnapshot assets = new AssetCatalogService().Load(fixture.AssetCatalogPath);
        AssetModelSummary model = assets.LooseMeshes.Single().ModelSummary;
        Assert.Multiple(() =>
        {
            Assert.That(assets.Summary, Is.EqualTo(new AssetCatalogSummary(1, 1, 1, 0, 0, 1, 4)));
            Assert.That(assets.Textures.Single().CatalogId, Is.EqualTo("texture:fixture/texture_one.tga"));
            Assert.That(assets.LooseMeshes.Single().CatalogId, Is.EqualTo("mesh:fixture_mesh.msh"));
            Assert.That(assets.EmbeddedMeshes.Single().CatalogId, Is.EqualTo("embedded_mesh:fixture/body00"));
            Assert.That(assets.Goodies.Single().CatalogId, Is.EqualTo("goodie:008"));
            Assert.That(model.MetadataAvailable, Is.True, model.Status);
            Assert.That(model.VertexCount, Is.EqualTo(3));
            Assert.That(model.PolygonIndexCount, Is.EqualTo(3));
            Assert.That(model.GeometryPreview.Available, Is.True);
        });

        using var texture = new Bitmap(assets.Textures.Single().ExportPath);
        Assert.Multiple(() =>
        {
            Assert.That(texture.Size, Is.EqualTo(new Size(8, 8)));
            Assert.That(
                Enumerable.Range(0, texture.Width)
                    .SelectMany(x => Enumerable.Range(0, texture.Height).Select(y => texture.GetPixel(x, y).ToArgb()))
                    .Distinct()
                    .Count(),
                Is.GreaterThanOrEqualTo(4),
                "The synthetic texture must expose enough contrast for pixel-level native preview verification.");
        });
        MediaAssetNativeFixtureBuilder.Validate(fixture);
    }

    [Test]
    public void Build_IsByteDeterministicAcrossFreshRoots()
    {
        using var temp = new FixtureTempRoot();

        MediaAssetNativeFixture first = MediaAssetNativeFixtureBuilder.Build(Path.Combine(temp.Path, "one"));
        MediaAssetNativeFixture second = MediaAssetNativeFixtureBuilder.Build(Path.Combine(temp.Path, "two"));

        Assert.That(
            second.Files.Select(row => (row.RelativePath, row.Length, row.Sha256)),
            Is.EqualTo(first.Files.Select(row => (row.RelativePath, row.Length, row.Sha256))));
    }

    [Test]
    public void Build_RejectsNonFreshRoot()
    {
        using var temp = new FixtureTempRoot();
        string root = Path.Combine(temp.Path, "fixture");
        Directory.CreateDirectory(root);
        File.WriteAllText(Path.Combine(root, "ambient.txt"), "not owned");

        Assert.That(
            () => MediaAssetNativeFixtureBuilder.Build(root),
            Throws.TypeOf<InvalidOperationException>());
    }

    [Test]
    public void Validate_RejectsFixtureMutation()
    {
        using var temp = new FixtureTempRoot();
        MediaAssetNativeFixture fixture = MediaAssetNativeFixtureBuilder.Build(Path.Combine(temp.Path, "fixture"));
        File.AppendAllText(fixture.AssetCatalogPath, " ");

        Assert.That(
            () => MediaAssetNativeFixtureBuilder.Validate(fixture),
            Throws.TypeOf<InvalidOperationException>());
    }

    private sealed class FixtureTempRoot : IDisposable
    {
        internal FixtureTempRoot()
        {
            Path = System.IO.Path.Combine(
                System.IO.Path.GetTempPath(),
                "onslaught-media-asset-fixture-tests",
                Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Path);
        }

        internal string Path { get; }

        public void Dispose()
        {
            if (Directory.Exists(Path))
            {
                Directory.Delete(Path, recursive: true);
            }
        }
    }
}
