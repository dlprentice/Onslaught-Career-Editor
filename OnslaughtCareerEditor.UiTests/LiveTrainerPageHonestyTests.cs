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
                // The ban survives the 2026-08-01 live read on purpose. These fields have now been
                // seen in a running mission, but a verdict word still invites the reader to stop
                // thinking; naming what was observed ("read 20", "20 became 100") carries the same
                // confidence and stays checkable.
                Assert.That(
                    text,
                    Does.Not.Contain(word).IgnoreCase,
                    $"{where} says '{word}'. State what was observed rather than pronouncing a verdict.");
            }
        }
    }

    [Test]
    public void TheTrainerSaysPlainlyWhereTheseNumbersStand()
    {
        // Superseded 2026-08-01. This used to require the headline to say "Nobody has read" these
        // from a running game. On that date they WERE read from one: life 20, energy and shields 8,
        // life set to 100, HUD ring filled to match
        // (local-lab/LIVE-TRAINER-RUNTIME-CONFIRMATION-2026-08-01.md). Keeping the old sentence
        // would now be an understatement rather than a caution, and understating evidence is its
        // own dishonesty.
        //
        // What must survive: the headline still states the standing of these numbers in one plain
        // on-screen sentence, and still names the running mission rather than leaving it vague.
        Assert.That(LiveTrainerPageText.EvidenceHeadline, Does.Contain("running mission"));
        Assert.That(
            LiveTrainerPageText.EvidenceHeadline.ToLowerInvariant(),
            Does.Not.Contain("nobody has read"),
            "That claim is no longer true; the vitals were read from a live mission on 2026-08-01.");
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
        // Superseded 2026-08-01. This used to require the phrase "no evidence at all", which was
        // true when the offsets rested only on source correspondence. They were since read straight
        // out of CBattleEngine::Damage in the pristine specimen - three consecutive loads off the
        // this-pointer, with life fetched by an x87 fld, so the positions and the float type are
        // settled (local-lab/VITALS-LAYOUT-STATIC-CONFIRMATION-2026-08-01.md). Keeping the old
        // wording would now understate what is known, which is its own kind of dishonesty.
        //
        // Superseded again the same day: the runtime route WAS walked. Player slot 0 resolved to
        // a battle engine at +0x1c, the three fields read 20 / 8 / 8, life was set to 100 and the
        // HUD ring filled to match (local-lab/LIVE-TRAINER-RUNTIME-CONFIRMATION-2026-08-01.md).
        // The distinction the earlier version protected has collapsed in the good direction.
        //
        // What must survive: the note is grounded in a specific observation with real numbers
        // rather than an assurance, and it still describes the failure mode.
        Assert.That(
            LiveTrainerPageText.EvidenceNote.ToLowerInvariant(),
            Does.Contain("mission"),
            "The note must name the running mission the numbers came from.");
        Assert.That(
            LiveTrainerPageText.EvidenceNote,
            Does.Match(@"\d"),
            "The note must carry the observed values, so the claim stays checkable.");
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
            // Superseded 2026-08-01. This used to require the exact phrase
            // "Read from a running game: never" on each field. All three were read from a live
            // mission that day, so the phrase became false. What the test is really for is that
            // each control carries its OWN standing rather than inheriting the section heading -
            // so it now requires each line to say what that field did in a running mission.
            Assert.That(
                perControl.ToLowerInvariant(),
                Does.Contain("running mission"),
                "Each write control carries its own evidence line, not just the section heading.");
            Assert.That(
                perControl,
                Does.Match(@"\d"),
                "Each line names the value that was actually observed, not a bare assurance.");
        }

        foreach (string automationId in new[]
                 {
                     "LiveTrainerLifeEvidence",
                     "LiveTrainerEnergyEvidence",
                     "LiveTrainerShieldsEvidence",
                     "LiveTrainerStateEvidence",
                     "LiveTrainerVulnerableEvidence",
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

    /// <summary>
    /// Hold is a re-heal, not a freeze, and the difference is the one a player finds out about by
    /// dying.
    ///
    /// The loop writes at 10 Hz against a 20 Hz simulation, so damage lands and is undone a moment
    /// later - and a single hit large enough to kill arrives between two writes and is not undone
    /// at all. A switch labelled Hold that quietly means "mostly" is exactly the kind of claim the
    /// rest of this page refuses to make, so it has to say so, on screen.
    /// </summary>
    [Test]
    public void HoldSaysItIsATopUpRatherThanInvulnerability()
    {
        Assert.Multiple(() =>
        {
            Assert.That(LiveTrainerPageText.HoldExplanation, Does.Contain("rather than freezing it"));
            Assert.That(LiveTrainerPageText.HoldExplanation, Does.Contain("still take damage between writes"));
            Assert.That(LiveTrainerPageText.HoldExplanation, Does.Contain("will still kill you"));
            Assert.That(
                IsBehindADisclosure(TrainerElement("LiveTrainerHoldExplanation")),
                Is.False,
                "A caveat a player has to open is a caveat they will miss.");
        });
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

    /// <summary>
    /// The damage switch is the one field on this page whose position is known from bytes and
    /// whose behaviour has never been watched. That gap is the whole test: it may be shown, it may
    /// not be written, and the page must send a player to the god mode that does work rather than
    /// leaving them with a number and a shrug.
    /// </summary>
    [Test]
    public void TheDamageSwitchIsShownAndNotOffered()
    {
        string xaml = PageXaml;

        Assert.That(
            xaml,
            Does.Contain("LiveTrainerVulnerableValue"),
            "The field is read and displayed - that is the half that is earned.");

        foreach (string absent in new[]
                 {
                     "VulnerableNumberBox", "SetVulnerableButton", "HoldVulnerableToggle",
                     "SetGodModeButton", "LiveTrainerGodModeToggle",
                 })
        {
            Assert.That(
                xaml,
                Does.Not.Contain(absent),
                $"{absent} would write a field nothing has ever written in a running game.");
        }

        Assert.That(
            Enum.GetNames<LiveTrainerVital>(),
            Does.Not.Contain("Vulnerable"),
            "A writable vital is how the write path is reached; the damage switch is not one.");
    }

    [Test]
    public void TheDamageSwitchSaysWhatIsMissingAndWhereToGoInstead()
    {
        Assert.That(
            LiveTrainerPageText.VulnerableHeadline,
            Does.Contain("not yet tested"),
            "The gap is the headline, not the fine print.");
        Assert.That(
            LiveTrainerPageText.VulnerableNote,
            Does.Contain("nothing has written to it"),
            "Name precisely what has not happened, so a later session knows what would close it.");

        // The point of the pointer. There IS a working god mode on this page - the save-name
        // cheat, live-confirmed 2026-03-29 - and the trainer section shipped without mentioning it.
        // A player who wants god mode should leave this section with the thing that works, not
        // with a number they cannot use.
        Assert.That(LiveTrainerPageText.VulnerableUseTheCheatInstead, Does.Contain("God mode"));
        Assert.That(
            LiveTrainerPageText.VulnerableUseTheCheatInstead,
            Does.Contain("real mission"),
            "Say what was observed of the cheat, on the same terms the vitals are held to.");
        Assert.That(
            IsBehindADisclosure(TrainerElement("LiveTrainerVulnerableUseCheat")),
            Is.False,
            "This is what to do instead. A player who has to open a panel to find it will not.");
        Assert.That(IsBehindADisclosure(TrainerElement("LiveTrainerVulnerableHeadline")), Is.False);
    }

    [Test]
    public void ADamageSwitchThatIsNeitherZeroNorOneIsNotCalledASwitch()
    {
        Assert.That(
            LiveTrainerPageText.DescribeVulnerable(Vitals(1f, 1f, 1f, vulnerable: 0)),
            Does.Contain("would not stick"));
        Assert.That(
            LiveTrainerPageText.DescribeVulnerable(Vitals(1f, 1f, 1f, vulnerable: 1)),
            Does.Contain("damage counts"));

        // The same plausibility gate the vitals get. If the pointer is wrong this field is
        // whatever happens to sit at +0x15C, and the page must say so rather than reading a
        // meaning into it.
        Assert.That(
            LiveTrainerPageText.DescribeVulnerable(Vitals(1f, 1f, 1f, vulnerable: 74)),
            Does.Contain("not the switch"));
        Assert.That(LiveTrainerPageText.DescribeVulnerable(null), Is.EqualTo("-"));
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

    private static LivePlayerVitals Vitals(
        float life,
        float energy,
        float shields,
        int state = 2,
        int? vulnerable = null)
    {
        static LiveTrainerFieldReading Field(uint address, float value) =>
            new(address, unchecked((uint)BitConverter.SingleToInt32Bits(value)));

        return new LivePlayerVitals(
            0x0A000000,
            0x0B000000,
            Field(0x0B0000F8, life),
            Field(0x0B0000FC, energy),
            Field(0x0B000100, shields),
            new LiveTrainerFieldReading(0x0B000260, unchecked((uint)state)),
            vulnerable is null
                ? null
                : new LiveTrainerFieldReading(0x0B00015C, unchecked((uint)vulnerable.Value)));
    }
}
