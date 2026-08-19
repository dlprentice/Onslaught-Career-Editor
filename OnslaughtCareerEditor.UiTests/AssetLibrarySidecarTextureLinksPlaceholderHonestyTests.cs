using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Asset Library used to say sidecar in the empty texture-link
/// placeholder. ModelTextureLinksTextBlock paints that sentence.
/// Name the texture.
/// </summary>
public class AssetLibrarySidecarTextureLinksPlaceholderHonestyTests
{
    private const string PaintedSentence =
        "Texture links appear here when an FBX export references extracted textures.";

    [Test]
    public void TheEmptyTextureLinksPlaceholderPaintsTheTextureNotASidecar()
    {
        string placeholder = ReadTextureLinksPlaceholder();

        Assert.That(placeholder, Does.Contain("x:Name=\"ModelTextureLinksTextBlock\""));
        Assert.That(placeholder, Does.Contain("AssetModelTextureLinks"));
        Assert.That(placeholder, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(placeholder.ToLowerInvariant(), Does.Contain("texture"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("sidecar"));
        Assert.That(placeholder.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(placeholder, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheEmptyTextureLinksPlaceholderIsTheXamlDefault()
    {
        string xaml = ReadAssetLibraryXaml();
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml.cs"));
        string placeholder = ReadTextureLinksPlaceholder();

        Assert.That(xaml, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(placeholder, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(xaml, Does.Not.Contain("Catalog and sidecar texture links appear here"));
        Assert.That(code, Does.Not.Contain(PaintedSentence));
        Assert.That(code, Does.Not.Contain("Catalog and sidecar texture links appear here"));
    }

    private static string ReadAssetLibraryXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "AssetLibraryPage.xaml"));
    }

    private static string ReadTextureLinksPlaceholder()
    {
        string xaml = ReadAssetLibraryXaml();
        const string startMark = "x:Name=\"ModelTextureLinksTextBlock\"";
        int start = xaml.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "ModelTextureLinksTextBlock is missing.");

        int end = xaml.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "ModelTextureLinksTextBlock is unclosed.");
        return xaml[start..(end + 2)];
    }
}
