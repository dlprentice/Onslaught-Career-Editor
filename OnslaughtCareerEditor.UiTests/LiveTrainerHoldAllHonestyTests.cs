using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Cheats live trainer now has one switch that holds life, energy, and shields
/// together. The three existing holds still work; this is the missing one-switch
/// path for a fight, and it has to stay honest about walker/jet overwrite and
/// about being a top-up rather than invulnerability.
/// </summary>
public class LiveTrainerHoldAllHonestyTests
{
    private static string PageXamlPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml");

    private static string PageCodeBehindPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml.cs");

    private static string PageXaml => File.ReadAllText(PageXamlPath);

    private static XElement HoldAllToggle()
    {
        XDocument page = XDocument.Parse(PageXaml);
        XElement? toggle = page.Descendants().SingleOrDefault(candidate =>
            candidate.Attributes().Any(attribute =>
                attribute.Name.LocalName == "AutomationProperties.AutomationId"
                && attribute.Value == "LiveTrainerHoldAllToggle"));
        Assert.That(toggle, Is.Not.Null, "Expected LiveTrainerHoldAllToggle on Cheats.");
        return toggle!;
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
    public void HoldAllThreeShipsDisabledAndStaysOnScreen()
    {
        XElement toggle = HoldAllToggle();
        string? isEnabled = toggle.Attributes()
            .FirstOrDefault(attribute => attribute.Name.LocalName == "IsEnabled")?.Value;

        Assert.That(isEnabled, Is.EqualTo("False"));
        Assert.That(IsBehindADisclosure(toggle), Is.False);
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerHoldAllNote")), Is.False);
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerHoldAllHeadline")), Is.False);
    }

    [Test]
    public void HoldAllThreeIsTheSameTopUpNotInvulnerability()
    {
        Assert.That(LiveTrainerPageText.HoldAllHeadline, Is.EqualTo("Hold life, energy, and shields together."));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Contain("same top-up"));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Contain("not a freeze"));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Contain("still will"));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Contain("Walker mode"));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Contain("energy has to be held"));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Contain("Jet mode"));
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Not.Contain("verified").IgnoreCase);
        Assert.That(LiveTrainerPageText.HoldAllNote, Does.Not.Contain("guaranteed").IgnoreCase);
    }

    [Test]
    public void HoldAllThreeUsesTheAllOrNothingHoldAndTheWriteGate()
    {
        string codeBehind = File.ReadAllText(PageCodeBehindPath);

        Assert.That(codeBehind, Does.Contain("TryHoldAll("));
        Assert.That(codeBehind, Does.Contain("DescribeWhyWritingIsBlocked"));
        Assert.That(
            codeBehind,
            Does.Not.Contain("LiveTrainerHoldAllToggle.IsEnabled = true"),
            "Hold all three must go through the same write gate as the three individual holds.");
        Assert.That(
            PageXaml,
            Does.Contain("AutomationProperties.Name=\"Hold all three\""));
    }
}
