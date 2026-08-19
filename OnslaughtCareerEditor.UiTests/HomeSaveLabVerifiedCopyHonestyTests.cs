using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Home Save Lab still tells the player they will write a verified copy.
/// That TextBlock paints. Name the written save.
/// </summary>
public class HomeSaveLabVerifiedCopyHonestyTests
{
    private const string PaintedSentence =
        "Open Save Lab to inspect a .bes career save or defaultoptions.bea, then write a separate save or options file.";

    [Test]
    public void HomeSaveLabCardPaintsAWrittenSaveNotAVerifiedCopy()
    {
        string card = ReadSaveLabCard();

        Assert.That(card, Does.Contain("HomeSaveOptionsTitle"));
        Assert.That(card, Does.Contain("HomeOpenSaveLabButton"));
        Assert.That(card, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(card, Does.Contain("save or options file"));
        Assert.That(card, Does.Not.Contain("verified copy"));
        Assert.That(card, Does.Not.Contain("verified profile"));
        Assert.That(card, Does.Not.Contain("app-owned"));
        Assert.That(card, Does.Not.Contain(":\\"));
    }

    [Test]
    public void HomeDoesNotOverwriteTheSaveLabCardSentence()
    {
        string xaml = ReadHomeXaml();
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "HomePage.xaml.cs"));
        string body = ExtractSaveLabBody(ReadSaveLabCard());

        Assert.That(xaml, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(body, Does.Contain($"Text=\"{PaintedSentence}\""));
        Assert.That(body, Does.Not.Contain("x:Name="));
        Assert.That(code, Does.Not.Contain("verified copy"));
        Assert.That(code, Does.Not.Contain(PaintedSentence));
        Assert.That(code, Does.Not.Contain("SaveOptionsCardBorder"));
    }

    private static string ReadHomeXaml()
    {
        return File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "HomePage.xaml"));
    }

    private static string ReadSaveLabCard()
    {
        string xaml = ReadHomeXaml();
        const string startMark = "x:Name=\"SaveOptionsCardBorder\"";
        int start = xaml.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Home Save Lab card is missing.");

        int end = xaml.IndexOf("HomeBrowseLearnTitle", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Home Save Lab card has no end.");
        return xaml[start..end];
    }

    private static string ExtractSaveLabBody(string card)
    {
        const string startMark = "Text=\"Open Save Lab";
        int start = card.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Home Save Lab body is missing.");

        int end = card.IndexOf("/>", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Home Save Lab body is unclosed.");
        return card[start..(end + 2)];
    }
}
