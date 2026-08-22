using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Lore depth surfaces: full-text matches with snippets, "what links here"
/// cross-links, and the reader text-size control. Every new panel must say what to
/// do next instead of going blank, and no path may dump a file path into the pane.
/// </summary>
public class LoreDepthHonestyTests
{
    private static string ReadWinUiFile(string relative)
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            relative));
    }

    [Test]
    public void SearchMatchesPanelSaysWhatToDoNextWhenEmpty()
    {
        string page = ReadWinUiFile(Path.Combine("Pages", "LorePage.xaml.cs"));

        Assert.That(page, Does.Contain("No document contains that word in its text. Try another word, or clear the search."));
        Assert.That(page, Does.Contain("Type a word to find every document containing it"));
    }

    [Test]
    public void BacklinksPanelNamesBothEmptyStates()
    {
        string page = ReadWinUiFile(Path.Combine("Pages", "LorePage.xaml.cs"));

        Assert.That(page, Does.Contain("No included document links to this one yet."));
        Assert.That(page, Does.Contain("Cross-links are unavailable for this library."));
    }

    [Test]
    public void CrossLinkIndexReusesTheBrowserServiceNotASecondPathResolver()
    {
        string service = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "LoreSearchService.cs"));

        // Link resolution goes through the app's own rules.
        Assert.That(service, Does.Contain("_service.ResolveInternalTarget("));
        Assert.That(service, Does.Contain("LoadDocumentContent(filePath)"));
    }

    [Test]
    public void TextSizeControlIsPresentAndClamped()
    {
        string xaml = ReadWinUiFile(Path.Combine("Pages", "LorePage.xaml"));
        string page = ReadWinUiFile(Path.Combine("Pages", "LorePage.xaml.cs"));

        Assert.That(xaml, Does.Contain("LoreTextSmallerButton"));
        Assert.That(xaml, Does.Contain("LoreTextLargerButton"));
        Assert.That(page, Does.Contain("Math.Clamp(_readerTextScale + (grow ? 0.1 : -0.1), 0.7, 1.8)"));
    }

    [Test]
    public void OutlineAndOutgoingPanelsNameEmptyStates()
    {
        string xaml = ReadWinUiFile(Path.Combine("Pages", "LorePage.xaml"));
        string page = ReadWinUiFile(Path.Combine("Pages", "LorePage.xaml.cs"));

        Assert.That(xaml, Does.Contain("LoreOutlineExpander"));
        Assert.That(xaml, Does.Contain("LoreOutgoingExpander"));
        Assert.That(page, Does.Contain("This document has no headings yet."));
        Assert.That(page, Does.Contain("This page does not link to another included document yet."));
        Assert.That(page, Does.Contain("Outgoing links are unavailable for this library."));
    }

    [Test]
    public void ReaderRendersAtTheChosenScale()
    {
        string renderer = ReadWinUiFile(Path.Combine("Helpers", "LoreDocumentRenderer.cs"));

        Assert.That(renderer, Does.Contain("double textScale"));
        Assert.That(renderer, Does.Contain("Math.Clamp(textScale, 0.7, 1.8)"));
    }
}
