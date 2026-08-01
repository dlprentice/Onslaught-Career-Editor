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
///
/// Since the progressive-disclosure pass the second of those has a shape as well as a wording: one
/// short sentence stays on screen, the paragraph behind it collapses into a panel labelled
/// "How we know", and the per-field provenance goes with it. Two things are exempt because they
/// change what a player should do rather than saying where a number came from - the shields hold
/// warning, and the hold explanation - and this suite fails if either is hidden.
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

    private static XElement TrainerElement(string automationId)
    {
        XElement? element = TrainerSectionElements()
            .SingleOrDefault(candidate => HasAutomationId(candidate, automationId));
        Assert.That(element, Is.Not.Null, $"Expected exactly one trainer element with automation id {automationId}.");
        return element!;
    }

    /// <summary>True when a player has to open a disclosure before this line exists on screen.</summary>
    private static bool IsBehindADisclosure(XElement element) =>
        element.Ancestors().Any(ancestor => ancestor.Name.LocalName == "Expander");

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
        // This is the one sentence that may not be behind anything. A player who never opens a
        // disclosure still has to meet it, so it is short, plain, and on screen.
        Assert.That(LiveTrainerPageText.EvidenceHeadline, Does.Contain("running game"));
        Assert.That(LiveTrainerPageText.EvidenceHeadline, Does.Contain("Nobody has read"));
        Assert.That(
            LiveTrainerPageText.EvidenceHeadline.Count(character => character == '.'),
            Is.EqualTo(1),
            "The visible caveat is one sentence. The rest of it belongs behind the disclosure.");
        Assert.That(
            IsBehindADisclosure(TrainerElement("LiveTrainerEvidenceHeadline")),
            Is.False,
            "A player must meet this sentence without opening anything.");
    }

    [Test]
    public void TheRestOfTheCaveatIsStillOnThePage_OneClickAway()
    {
        // Moving it is allowed. Losing it is not: where the positions came from, and what a wrong
        // one looks like, are the whole safety argument.
        Assert.That(
            LiveTrainerPageText.EvidenceNote,
            Does.Contain("no evidence at all"),
            "The section must still say the positions are evidence about where, not about what you will see.");
        Assert.That(
            LiveTrainerPageText.EvidenceNote,
            Does.Contain("nonsense"),
            "The failure mode has to be described, because seeing it is the whole safety argument.");
        Assert.That(
            IsBehindADisclosure(TrainerElement("LiveTrainerEvidence")),
            Is.True,
            "The paragraph is fine print, so it collapses.");
    }

    [Test]
    public void EveryFieldStillCarriesItsOwnEvidenceLine_BehindItsOwnDisclosure()
    {
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

        foreach (string automationId in new[]
                 {
                     "LiveTrainerLifeEvidence",
                     "LiveTrainerEnergyEvidence",
                     "LiveTrainerShieldsEvidence",
                     "LiveTrainerStateEvidence",
                 })
        {
            Assert.That(
                IsBehindADisclosure(TrainerElement(automationId)),
                Is.True,
                $"{automationId} is provenance and belongs behind the disclosure.");
        }
    }

    [Test]
    public void TheDisclosuresInTheTrainerCarryTheSameLabelAsTheRestOfThePage()
    {
        XElement[] disclosures = TrainerSectionElements()
            .Where(element => element.Name.LocalName == "Expander")
            .ToArray();

        Assert.That(disclosures, Is.Not.Empty, "The trainer collapses its provenance like the rest of the page.");
        foreach (XElement disclosure in disclosures)
        {
            Assert.That(
                (string?)disclosure.Attribute("Header"),
                Is.EqualTo(LiveTrainerPageText.EvidenceDisclosureLabel));
            Assert.That(
                (string?)disclosure.Attribute("AutomationProperties.Name"),
                Does.StartWith(LiveTrainerPageText.EvidenceDisclosureLabel),
                "Identical labels need distinct accessible names, and the name must contain the label.");
        }

        Assert.That(
            disclosures.Select(disclosure => (string?)disclosure.Attribute("AutomationProperties.Name")),
            Is.Unique);
    }

    [Test]
    public void TheTrainerSaysItOnlyAttachesToACopyThisAppLaunched()
    {
        Assert.That(LiveTrainerPageText.SafeCopyOnlyNote, Does.Contain("installed game is never opened"));
        Assert.That(LiveTrainerPageText.SafeCopyOnlyNote, Does.Contain("Windowed & Mods"));
        Assert.That(
            IsBehindADisclosure(TrainerElement("LiveTrainerSafeCopyNote")),
            Is.False,
            "What this feature will and will not touch is a boundary, not fine print.");
    }

    [Test]
    public void TheTrainerSaysAMissionHasToBeActuallyRunning()
    {
        Assert.That(LiveTrainerPageText.MissionRunningNote, Does.Contain("mission actually running"));
        Assert.That(
            LiveTrainerPageText.MissionRunningNote,
            Does.Contain("zero").IgnoreCase,
            "The frontend reads as zeroes, and the page promises to say so rather than show them.");
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerMissionNote")), Is.False);
    }

    [Test]
    public void WithNothingRunning_TheTrainerSaysWhatToDoNextInOneSentence()
    {
        string nothingRunning = LiveTrainerPageText.BuildAttachSummary(false, null, null);

        Assert.That(nothingRunning, Is.EqualTo(LiveTrainerPageText.NothingRunningNote));
        Assert.That(
            nothingRunning.Count(character => character == '.'),
            Is.EqualTo(1),
            $"An empty state is one sentence: '{nothingRunning}'");
        Assert.That(nothingRunning, Does.Contain("Windowed & Mods"));
        Assert.That(
            nothingRunning,
            Does.Contain("Watch the running copy"),
            "Name the button, so the sentence works for somebody driving by voice as well.");
        Assert.That(
            PageXaml,
            Does.Contain("start a mission, then press Watch the running copy"),
            "The status bar's opening message must be the same instruction, not a stale one.");

        Assert.That(
            LiveTrainerPageText.BuildReadingSummary(null),
            Is.Empty,
            "Before the first read there is nothing to report; a line saying so only describes the emptiness.");
    }

    [Test]
    public void AmmunitionAndGameSpeedAreNotOffered_BecauseNeitherHasAnAddress()
    {
        Assert.That(LiveTrainerPageText.NothingOfferedHeadline, Does.Contain("Ammunition"));
        Assert.That(LiveTrainerPageText.NothingOfferedHeadline, Does.Contain("game speed"));
        Assert.That(
            LiveTrainerPageText.NothingOfferedNote,
            Does.Contain("no address"),
            "The reason stays on the page, behind the disclosure; only the absence is stated up front.");
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerNothingOffered")), Is.True);
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerNothingOfferedHeadline")), Is.False);

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
    public void TheShieldsWarningStaysOnScreen_BecauseItChangesWhatThePlayerShouldDo()
    {
        Assert.That(LiveTrainerPageText.ShieldsHoldWarning, Does.Contain("walker mode"));
        Assert.That(LiveTrainerPageText.ShieldsHoldWarning, Does.Contain("will not stick"));
        Assert.That(
            LiveTrainerPageText.ShieldsHoldWarning,
            Does.Contain("hold energy as well").IgnoreCase,
            "Telling a player the control is futile without telling them the fix is not honesty, it is a shrug.");
        Assert.That(
            LiveTrainerPageText.ShieldsHoldWarning,
            Does.Contain("jet mode"),
            "The jet-mode behaviour is the other half of why the switch will not hold.");

        Assert.That(
            IsBehindADisclosure(TrainerElement("LiveTrainerShieldsHoldWarning")),
            Is.False,
            "This is an instruction, not provenance. A warning a player has to open is a warning they will miss.");
    }

    [Test]
    public void TheHoldControlsExplanationStaysOnScreen_BecauseItIsHowTheControlWorks()
    {
        Assert.That(
            IsBehindADisclosure(TrainerElement("LiveTrainerHoldExplanation")),
            Is.False,
            "Why Hold repeats and when it stops is how the control behaves, not where a number came from.");
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
