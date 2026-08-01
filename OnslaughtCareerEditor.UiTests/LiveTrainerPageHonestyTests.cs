using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Xml.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The live trainer is the only part of this app that reaches into a running process, and it does
/// it using three field positions that nobody has ever read out of a running game. That makes its
/// copy load-bearing in a way the rest of the Cheats page's copy is not: everywhere else, the game
/// itself supplies the effect and the worst case is a file that does nothing. Here the worst case
/// is a player believing a number.
///
/// So this suite pins three things. The section must never say the vitals are verified. It must
/// say out loud that nobody has read them from a running game. And no control that writes may be
/// enabled in the shipped markup - the only route to enabling one is a read that came back
/// looking like real numbers.
/// </summary>
public class LiveTrainerPageHonestyTests
{
    private static readonly string[] OverclaimingWords =
    [
        "verified", "confirmed", "proven", "guaranteed", "certain", "reliable", "accurate",
    ];

    private static string PageXamlPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml");

    private static string PageCodeBehindPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml.cs");

    private static string PageXaml => File.ReadAllText(PageXamlPath);

    /// <summary>Every string the trainer section can put on screen, from markup and from code.</summary>
    private static IReadOnlyList<(string Where, string Text)> AllTrainerCopy()
    {
        var copy = new List<(string, string)>();

        foreach (FieldInfo field in typeof(LiveTrainerPageText)
                     .GetFields(BindingFlags.Public | BindingFlags.Static | BindingFlags.FlattenHierarchy)
                     .Where(candidate => candidate.FieldType == typeof(string)))
        {
            if (field.GetValue(null) is string value)
            {
                copy.Add(($"LiveTrainerPageText.{field.Name}", value));
            }
        }

        foreach (XElement element in TrainerSectionElements())
        {
            foreach (XAttribute attribute in element.Attributes())
            {
                if (attribute.Name.LocalName is "Text" or "Content" or "Header" or "Title" or "Message" or "PlaceholderText" &&
                    !attribute.Value.StartsWith("{", StringComparison.Ordinal))
                {
                    copy.Add(($"CheatsPage.xaml/{attribute.Name.LocalName}", attribute.Value));
                }
            }
        }

        return copy;
    }

    private static IEnumerable<XElement> TrainerSectionElements()
    {
        XDocument page = XDocument.Parse(PageXaml);
        XElement section = page.Descendants().Single(candidate => HasAutomationId(candidate, "LiveTrainerSection"));
        return section.DescendantsAndSelf();
    }

    private static bool HasAutomationId(XElement element, string automationId) =>
        element.Attributes().Any(attribute =>
            attribute.Name.LocalName == "AutomationProperties.AutomationId" && attribute.Value == automationId);

    [Test]
    public void NothingInTheTrainerClaimsTheVitalsAreVerified()
    {
        foreach ((string where, string text) in AllTrainerCopy())
        {
            foreach (string word in OverclaimingWords)
            {
                Assert.That(
                    text,
                    Does.Not.Contain(word).IgnoreCase,
                    $"{where} says '{word}'. Nobody has read these fields out of a running game.");
            }
        }
    }

    [Test]
    public void TheTrainerSaysPlainlyThatNobodyHasReadTheseFromARunningGame()
    {
        Assert.That(LiveTrainerPageText.EvidenceNote, Does.Contain("running game"));
        Assert.That(LiveTrainerPageText.EvidenceNote, Does.Contain("Nobody has read"));
        Assert.That(
            LiveTrainerPageText.EvidenceNote,
            Does.Contain("nonsense"),
            "The failure mode has to be described, because seeing it is the whole safety argument.");

        foreach (string perControl in new[]
                 {
                     LiveTrainerPageText.LifeEvidenceNote,
                     LiveTrainerPageText.EnergyEvidenceNote,
                     LiveTrainerPageText.ShieldsEvidenceNote,
                 })
        {
            Assert.That(
                perControl,
                Does.Contain("Read from a running game: never"),
                "Each write control carries its own evidence line, not just the section heading.");
        }
    }

    [Test]
    public void TheTrainerSaysItOnlyAttachesToACopyThisAppLaunched()
    {
        Assert.That(LiveTrainerPageText.SafeCopyOnlyNote, Does.Contain("installed game is never opened"));
        Assert.That(LiveTrainerPageText.SafeCopyOnlyNote, Does.Contain("Windowed & Mods"));
    }

    [Test]
    public void TheTrainerSaysAMissionHasToBeActuallyRunning()
    {
        Assert.That(LiveTrainerPageText.MissionRunningNote, Does.Contain("mission actually running"));
        Assert.That(
            LiveTrainerPageText.MissionRunningNote,
            Does.Contain("zero").IgnoreCase,
            "The frontend reads as zeroes, and the page promises to say so rather than show them.");
    }

    [Test]
    public void AmmunitionAndGameSpeedAreNotOffered_BecauseNeitherHasAnAddress()
    {
        Assert.That(LiveTrainerPageText.NothingOfferedNote, Does.Contain("Ammunition"));
        Assert.That(LiveTrainerPageText.NothingOfferedNote, Does.Contain("game speed"));
        Assert.That(LiveTrainerPageText.NothingOfferedNote, Does.Contain("no address"));

        string xaml = PageXaml;
        foreach (string absent in new[] { "AmmoNumberBox", "SetAmmoButton", "TimescaleNumberBox", "SetSpeedButton" })
        {
            Assert.That(xaml, Does.Not.Contain(absent), $"There is no address evidence behind {absent}.");
        }

        Assert.That(Enum.GetValues<LiveTrainerVital>(), Is.EquivalentTo(new[]
        {
            LiveTrainerVital.Life, LiveTrainerVital.Energy, LiveTrainerVital.Shields,
        }));
    }

    [Test]
    public void EveryControlThatCouldWriteShipsDisabled()
    {
        string[] writeControls =
        [
            "LiveTrainerLifeNumberBox", "LiveTrainerSetLifeButton", "LiveTrainerHoldLifeToggle",
            "LiveTrainerEnergyNumberBox", "LiveTrainerSetEnergyButton", "LiveTrainerHoldEnergyToggle",
            "LiveTrainerShieldsNumberBox", "LiveTrainerSetShieldsButton", "LiveTrainerHoldShieldsToggle",
        ];

        List<XElement> section = TrainerSectionElements().ToList();
        foreach (string automationId in writeControls)
        {
            XElement? control = section.SingleOrDefault(candidate => HasAutomationId(candidate, automationId));
            Assert.That(control, Is.Not.Null, $"Expected a control with automation id {automationId}.");

            string? isEnabled = control!.Attributes()
                .FirstOrDefault(attribute => attribute.Name.LocalName == "IsEnabled")?.Value;
            Assert.That(
                isEnabled,
                Is.EqualTo("False"),
                $"{automationId} must ship disabled; only a believable read may switch it on.");
        }
    }

    [Test]
    public void ThePageEnablesWriteControlsOnlyThroughTheOneGate()
    {
        string codeBehind = File.ReadAllText(PageCodeBehindPath);

        Assert.That(
            codeBehind,
            Does.Contain("DescribeWhyWritingIsBlocked"),
            "The page must ask the one gate whether writing is allowed.");

        foreach (string control in new[]
                 {
                     "LiveTrainerSetLifeButton", "LiveTrainerSetEnergyButton", "LiveTrainerSetShieldsButton",
                     "LiveTrainerHoldLifeToggle", "LiveTrainerHoldEnergyToggle", "LiveTrainerHoldShieldsToggle",
                 })
        {
            Assert.That(
                codeBehind,
                Does.Not.Contain($"{control}.IsEnabled = true"),
                $"{control} must not be switched on directly; it goes through the gate.");
        }
    }

    [Test]
    public void WritingStaysBlockedUntilAReadComesBackLookingLikeNumbers()
    {
        Assert.That(LiveTrainerPageText.DescribeWhyWritingIsBlocked(false, null), Is.Not.Null);
        Assert.That(LiveTrainerPageText.DescribeWhyWritingIsBlocked(true, null), Is.Not.Null);

        var noMission = new LiveTrainerReadResult(
            LiveTrainerReadStatus.NoMissionRunning, null, "No mission is running.");
        Assert.That(LiveTrainerPageText.DescribeWhyWritingIsBlocked(true, noMission), Is.Not.Null);

        var nonsense = new LiveTrainerReadResult(LiveTrainerReadStatus.Read, Vitals(0f, 0f, 0f), "read");
        Assert.That(
            LiveTrainerPageText.DescribeWhyWritingIsBlocked(true, nonsense),
            Is.Not.Null,
            "A read that came back as zeroes is what a wrong field position looks like.");

        var believable = new LiveTrainerReadResult(LiveTrainerReadStatus.Read, Vitals(100f, 50f, 25f), "read");
        Assert.That(LiveTrainerPageText.DescribeWhyWritingIsBlocked(true, believable), Is.Null);
    }

    [Test]
    public void EveryNumberIsShownWithTheBytesItCameFrom()
    {
        // The raw bytes are not decoration. They are how a player tells a real reading from a bit
        // pattern the app has misread as a number.
        string formatted = LiveTrainerPageText.FormatVital(new LiveTrainerFieldReading(0x0B0000F8, 0x42C80000));

        Assert.That(formatted, Does.Contain("100"));
        Assert.That(formatted, Does.Contain("bytes 0x42C80000"));
    }

    [Test]
    public void AReadingThatIsNotANumberIsSaidToNotBeANumber()
    {
        // 100 stored as a whole number reads as a subnormal float. The page must not print
        // "0.000000000000000000000000000000000000000000140" and let a player believe it.
        string formatted = LiveTrainerPageText.FormatVital(new LiveTrainerFieldReading(0x0B0000F8, 100));

        Assert.That(formatted, Does.Contain("not a number"));
        Assert.That(formatted, Does.Contain("bytes 0x00000064"));
    }

    [Test]
    public void TheShieldsNoteWarnsThatTheGameOverwritesShieldsFromEnergy()
    {
        Assert.That(LiveTrainerPageText.ShieldsEvidenceNote, Does.Contain("walker mode"));
        Assert.That(LiveTrainerPageText.ShieldsEvidenceNote, Does.Contain("will not stick"));
        Assert.That(
            LiveTrainerPageText.ShieldsEvidenceNote,
            Does.Contain("hold energy as well").IgnoreCase,
            "Telling a player the control is futile without telling them the fix is not honesty, it is a shrug.");
    }

    [Test]
    public void ThePlayerModeIsShownAndNeverOffered()
    {
        Assert.That(LiveTrainerPageText.StateEvidenceNote, Does.Contain("watched in a running game"));
        Assert.That(LiveTrainerPageText.StateEvidenceNote, Does.Contain("never changed"));
        Assert.That(PageXaml, Does.Not.Contain("SetStateButton"));
        Assert.That(PageXaml, Does.Not.Contain("SetModeButton"));
    }

    [Test]
    public void AModeNumberNobodyHasSeenIsNotGivenAName()
    {
        Assert.That(LiveTrainerPageText.FormatState(Vitals(1f, 1f, 1f, state: 2)), Does.Contain("walker"));
        Assert.That(
            LiveTrainerPageText.FormatState(Vitals(1f, 1f, 1f, state: 9)),
            Does.Contain("no meaning recorded"));
    }

    [Test]
    public void TheHoldControlSaysWhyItRepeatsAndWhenItStops()
    {
        Assert.That(LiveTrainerPageText.HoldExplanation, Does.Contain("ten times a second"));
        Assert.That(LiveTrainerPageText.HoldExplanation, Does.Contain("stops on its own"));
        Assert.That(LiveTrainerPageText.HoldExplanation, Does.Contain("leave this page"));
    }

    [Test]
    public void TheTrainerDoesNotBorrowTheEvidenceRegistersVocabulary()
    {
        string[] banned = ["receipt", "manifest", "proof boundary", "byte-verified", "claim boundary", "corpus"];

        foreach ((string where, string text) in AllTrainerCopy())
        {
            foreach (string word in banned)
            {
                Assert.That(text, Does.Not.Contain(word).IgnoreCase, $"{where} should not use '{word}'.");
            }
        }
    }

    private static LivePlayerVitals Vitals(float life, float energy, float shields, int state = 2)
    {
        static LiveTrainerFieldReading Field(uint address, float value) =>
            new(address, unchecked((uint)BitConverter.SingleToInt32Bits(value)));

        return new LivePlayerVitals(
            0x0A000000,
            0x0B000000,
            Field(0x0B0000F8, life),
            Field(0x0B0000FC, energy),
            Field(0x0B000100, shields),
            new LiveTrainerFieldReading(0x0B000260, unchecked((uint)state)));
    }
}
