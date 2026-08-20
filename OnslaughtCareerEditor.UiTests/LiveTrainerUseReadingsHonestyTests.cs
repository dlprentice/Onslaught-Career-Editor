using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Set/Hold boxes default to 100. A player watching life 20 had to type
/// 20 before Set or Hold would keep that number. Use these readings copies
/// the live readout into the boxes and does not write the game.
/// </summary>
public class LiveTrainerUseReadingsHonestyTests
{
    private static string PageXamlPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml");

    private static string PageCodeBehindPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml.cs");

    private static string PageXaml => File.ReadAllText(PageXamlPath);

    private static XElement UseReadingsButton()
    {
        XDocument page = XDocument.Parse(PageXaml);
        XElement? button = page.Descendants().SingleOrDefault(candidate =>
            candidate.Attributes().Any(attribute =>
                attribute.Name.LocalName == "AutomationProperties.AutomationId"
                && attribute.Value == "LiveTrainerUseReadingsButton"));
        Assert.That(button, Is.Not.Null, "Expected LiveTrainerUseReadingsButton on Cheats.");
        return button!;
    }

    private static bool IsBehindADisclosure(XElement element) =>
        element.Ancestors().Any(ancestor => ancestor.Name.LocalName == "Expander");

    private static XElement TrainerElement(string automationId)
    {
        XDocument page = XDocument.Parse(PageXaml);
        XElement? element = page.Descendants().SingleOrDefault(candidate =>
            candidate.Attributes().Any(attribute =>
                attribute.Name.LocalName == "AutomationProperties.AutomationId"
                && attribute.Value == automationId));
        Assert.That(element, Is.Not.Null, $"Expected trainer element {automationId}.");
        return element!;
    }

    [Test]
    public void UseTheseReadingsShipsDisabledAndStaysOnScreen()
    {
        XElement button = UseReadingsButton();
        string? isEnabled = button.Attributes()
            .FirstOrDefault(attribute => attribute.Name.LocalName == "IsEnabled")?.Value;

        Assert.That(isEnabled, Is.EqualTo("False"));
        Assert.That(IsBehindADisclosure(button), Is.False);
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerUseReadingsNote")), Is.False);
    }

    [Test]
    public void UseTheseReadingsCopiesBoxesAndDoesNotWriteTheGame()
    {
        Assert.That(LiveTrainerPageText.UseReadingsButtonText, Is.EqualTo("Use these readings"));
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Contain("does not write them back"));
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Contain("does not change a hold"));
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Not.Contain("verified").IgnoreCase);
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Not.Contain("guaranteed").IgnoreCase);
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Not.Contain(@":\"));
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Not.Contain("CDB"));
        Assert.That(LiveTrainerPageText.UseReadingsNote, Does.Not.Contain("sidecar"));
    }

    [Test]
    public void TryCopyReadingsTakesAllThreeOrNone()
    {
        Assert.That(LiveTrainerPageText.TryCopyReadings(null, out _, out _, out _), Is.False);

        Assert.That(
            LiveTrainerPageText.TryCopyReadings(Vitals(20f, 8f, 8f), out float life, out float energy, out float shields),
            Is.True);
        Assert.That(life, Is.EqualTo(20f));
        Assert.That(energy, Is.EqualTo(8f));
        Assert.That(shields, Is.EqualTo(8f));

        // A non-finite energy must not leave life 20 mixed with a leftover 100.
        Assert.That(
            LiveTrainerPageText.TryCopyReadings(Vitals(20f, float.NaN, 8f), out life, out energy, out shields),
            Is.False);
        Assert.That(life, Is.EqualTo(0f));
        Assert.That(energy, Is.EqualTo(0f));
        Assert.That(shields, Is.EqualTo(0f));
    }

    [Test]
    public void UseTheseReadingsFillsTheBoxesThroughTheWriteGate()
    {
        string codeBehind = File.ReadAllText(PageCodeBehindPath);

        Assert.That(codeBehind, Does.Contain("TryCopyReadings("));
        Assert.That(codeBehind, Does.Contain("LiveTrainerLifeNumberBox.Value = life"));
        Assert.That(codeBehind, Does.Contain("LiveTrainerEnergyNumberBox.Value = energy"));
        Assert.That(codeBehind, Does.Contain("LiveTrainerShieldsNumberBox.Value = shields"));
        Assert.That(codeBehind, Does.Contain("DescribeWhyWritingIsBlocked"));
        Assert.That(
            codeBehind,
            Does.Not.Contain("LiveTrainerUseReadingsButton.IsEnabled = true"),
            "Use these readings must go through the same write gate as Set and Hold.");
        Assert.That(
            ExtractUseReadingsClickHandler(),
            Does.Not.Contain("WriteLiveTrainerVital"),
            "Copying the readout into the boxes must not write the running game.");
        Assert.That(
            ExtractUseReadingsClickHandler(),
            Does.Not.Contain("TryHold"),
            "Copying the readout must not start or change a hold.");
        Assert.That(
            PageXaml,
            Does.Contain("AutomationProperties.Name=\"Use these readings\""));
    }

    private static string ExtractUseReadingsClickHandler()
    {
        string code = File.ReadAllText(PageCodeBehindPath);
        const string startMark = "private void LiveTrainerUseReadingsButton_Click";
        int start = code.IndexOf(startMark, StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0), "Use these readings click handler is missing.");
        int end = code.IndexOf("private void LiveTrainerSetLifeButton_Click", start, StringComparison.Ordinal);
        Assert.That(end, Is.GreaterThan(start), "Use these readings click handler has no end.");
        return code.Substring(start, end - start);
    }

    private static LivePlayerVitals Vitals(float life, float energy, float shields)
    {
        static LiveTrainerFieldReading Field(uint address, float value) =>
            new(address, unchecked((uint)BitConverter.SingleToInt32Bits(value)));

        return new LivePlayerVitals(
            0x0A000000,
            0x0B000000,
            Field(0x0B0000F8, life),
            Field(0x0B0000FC, energy),
            Field(0x0B000100, shields),
            new LiveTrainerFieldReading(0x0B000260, 2));
    }
}
