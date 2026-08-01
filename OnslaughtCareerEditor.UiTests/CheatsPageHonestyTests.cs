using System;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Cheats page is allowed to offer cheats it has only read out of the executable, but it is
/// not allowed to describe them as though somebody had watched them work. It is also not allowed
/// to lose the three things a player has to understand before pressing the button: the write goes
/// to a safe copy, it makes a new file rather than editing one, and the free camera is
/// experimental.
///
/// Since the progressive-disclosure pass, most of that evidence is collapsed behind a panel
/// labelled "How we know". Moving it is allowed; losing it is not. So alongside the wording, this
/// suite pins the structure: which lines a player sees without opening anything, which lines are
/// one click away, and the fact that nothing has quietly become unreachable in the process.
///
/// Those are properties of strings and of markup, both of which drift silently. This suite pins
/// them.
/// </summary>
public class CheatsPageHonestyTests
{
    private static string PageXamlPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml");

    private static string PageCodeBehindPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml.cs");

    private static string PageXaml => File.ReadAllText(PageXamlPath);

    /// <summary>One cheat's four places on the page, by automation id.</summary>
    private static (string CheatId, string Effect, string Evidence, string Disclosure, string Tag)[] CheatSurfaces =>
    [
        (CheatCodeCatalog.AllGoodiesId, "CheatsAllGoodiesEffect", "CheatsAllGoodiesEvidence",
            "CheatsAllGoodiesEvidenceExpander", "CheatsAllGoodiesEvidenceTag"),
        (CheatCodeCatalog.AllLevelsId, "CheatsAllLevelsEffect", "CheatsAllLevelsEvidence",
            "CheatsAllLevelsEvidenceExpander", "CheatsAllLevelsEvidenceTag"),
        (CheatCodeCatalog.GodModeId, "CheatsGodModeEffect", "CheatsGodModeEvidence",
            "CheatsGodModeEvidenceExpander", "CheatsGodModeEvidenceTag"),
        (CheatCodeCatalog.FreeCameraId, "CheatsFreeCameraEffect", "CheatsFreeCameraEvidence",
            "CheatsFreeCameraEvidenceExpander", "CheatsFreeCameraEvidenceTag"),
        (CheatCodeCatalog.GoodieGatingBypassId, "CheatsGoodieGatingBypassEffect", "CheatsGoodieGatingBypassEvidence",
            "CheatsGoodieGatingBypassEvidenceExpander", "CheatsGoodieGatingBypassEvidenceTag"),
    ];

    private static XElement ElementWithAutomationId(XDocument page, string automationId)
    {
        XElement? element = page.Descendants().SingleOrDefault(candidate =>
            candidate.Attributes().Any(attribute =>
                attribute.Name.LocalName == "AutomationProperties.AutomationId" &&
                attribute.Value == automationId));

        Assert.That(element, Is.Not.Null, $"Expected exactly one element with automation id {automationId}.");
        return element!;
    }

    /// <summary>True when a player has to open a disclosure before this line exists on screen.</summary>
    private static bool IsBehindADisclosure(XElement element) =>
        element.Ancestors().Any(ancestor => ancestor.Name.LocalName == "Expander");

    [Test]
    public void TheVersionDisplayCheatIsNotOffered_BecauseNothingInTheGameEverCallsIt()
    {
        // Cheat index 2 decodes out of the table but no call site has ever been found for it.
        // Offering it would be offering a switch wired to nothing.
        Assert.That(
            CheatCodeCatalog.All.Select(cheat => cheat.RetailCheatIndex),
            Does.Not.Contain(2));
        Assert.That(
            CheatCodeCatalog.All.Select(cheat => cheat.Code),
            Does.Not.Contain("V3R5IOF"));
        Assert.That(PageXaml, Does.Not.Contain("V3R5IOF"));
    }

    [Test]
    public void CheatsNobodyHasWatchedWork_DoNotSayTheyAreConfirmed()
    {
        string[] confidentWords = ["confirmed", "seen working", "proven", "guaranteed", "verified"];

        foreach (CheatCode cheat in CheatCodeCatalog.All.Where(
                     cheat => cheat.Evidence == CheatEvidenceLevel.FoundInGameCodeOnly))
        {
            foreach (string word in confidentWords)
            {
                Assert.That(
                    cheat.WhatWeKnow,
                    Does.Not.Contain(word).IgnoreCase,
                    $"{cheat.Id} has only been read out of the executable, so its copy must not say '{word}'.");
            }

            Assert.That(
                cheat.WhatWeKnow,
                Does.Contain("not watched it").IgnoreCase,
                $"{cheat.Id} should say plainly that nobody has watched it work.");
        }
    }

    [Test]
    public void TheTwoCheatsWithRuntimeEvidence_AreTheOnesTheEvidenceStoreActuallyBacks()
    {
        // MALLOY and TURKEY are recorded as working in the Steam release without any patch, and
        // Maladim's God toggle was watched changing real combat damage. Nothing else has been.
        string[] seenWorking = CheatCodeCatalog.All
            .Where(cheat => cheat.Evidence == CheatEvidenceLevel.SeenWorkingInGame)
            .Select(cheat => cheat.Code)
            .ToArray();

        Assert.That(seenWorking, Is.EquivalentTo(new[] { "MALLOY", "TURKEY", "Maladim" }));
    }

    [Test]
    public void GodModeCopyKeepsItsHonestNegative_AlreadyLostHullIsNotRepaired()
    {
        CheatCode godMode = CheatCodeCatalog.FindById(CheatCodeCatalog.GodModeId)!;

        Assert.That(godMode.WhatWeKnow, Does.Contain("not repaired").IgnoreCase);
        Assert.That(
            godMode.WhatWeKnow,
            Does.Contain("never tested").IgnoreCase,
            "The measured boundary stops at combat damage; hazards were never tested and the copy must say so.");
    }

    [Test]
    public void TheTickBoxLabelsMatchTheCatalogNames()
    {
        // The labels live in XAML so they carry stable automation ids; the descriptions come from
        // the catalog at runtime. If the two drift, the page names a cheat one thing and describes
        // another.
        XDocument page = XDocument.Parse(PageXaml);

        (string AutomationId, string CheatId)[] pairs =
        [
            ("CheatsAllGoodiesCheckBox", CheatCodeCatalog.AllGoodiesId),
            ("CheatsAllLevelsCheckBox", CheatCodeCatalog.AllLevelsId),
            ("CheatsGodModeCheckBox", CheatCodeCatalog.GodModeId),
            ("CheatsFreeCameraCheckBox", CheatCodeCatalog.FreeCameraId),
            ("CheatsGoodieGatingBypassCheckBox", CheatCodeCatalog.GoodieGatingBypassId),
        ];

        foreach ((string automationId, string cheatId) in pairs)
        {
            XElement? element = page.Descendants().SingleOrDefault(candidate =>
                (string?)candidate.Attribute("{http://schemas.microsoft.com/winfx/2006/xaml/presentation}AutomationProperties.AutomationId") == automationId ||
                candidate.Attributes().Any(attribute =>
                    attribute.Name.LocalName == "AutomationProperties.AutomationId" &&
                    attribute.Value == automationId));

            Assert.That(element, Is.Not.Null, $"Expected a control with automation id {automationId}.");
            string? content = element!.Attributes()
                .FirstOrDefault(attribute => attribute.Name.LocalName == "Content")?.Value;
            Assert.That(
                content,
                Is.EqualTo(CheatCodeCatalog.FindById(cheatId)!.DisplayName),
                $"{automationId} label must match the catalog name for {cheatId}.");
        }
    }

    [Test]
    public void ThePageStatesItsThreeBoundariesWithoutMakingTheReaderLookForThem()
    {
        string xaml = PageXaml;

        Assert.That(xaml, Does.Contain("safe copy, not your installed game"));
        Assert.That(xaml, Does.Contain("copies one, byte for byte, under a new name"));
        Assert.That(
            xaml,
            Does.Contain("experimental"),
            "The free-camera movement route changes the copied game and must be labelled experimental.");

        // "Without making the reader look for them" now has a structural meaning too: these three
        // are the boundaries of the whole feature, so none of them may end up behind a disclosure.
        XDocument page = XDocument.Parse(xaml);
        foreach (string automationId in new[]
                 {
                     "CheatsBoundarySafeCopyNote",
                     "CheatsBoundaryNewFileNote",
                     "CheatsBoundaryReversibleNote",
                     "CheatsFreeCameraExtraNote",
                 })
        {
            Assert.That(
                IsBehindADisclosure(ElementWithAutomationId(page, automationId)),
                Is.False,
                $"{automationId} is a boundary of the feature, not provenance; it must stay on screen.");
        }
    }

    [Test]
    public void EveryCheatShowsWhatItDoes_AndKeepsItsEvidenceOneClickAway()
    {
        // The progressive-disclosure contract, stated as markup. The effect sentence is what a
        // player came for and is always on screen; the evidence sentence is still on the page, in
        // full, behind the one disclosure. Neither may swap places with the other.
        XDocument page = XDocument.Parse(PageXaml);

        foreach ((string cheatId, string effect, string evidence, string disclosure, _) in CheatSurfaces)
        {
            Assert.That(
                IsBehindADisclosure(ElementWithAutomationId(page, effect)),
                Is.False,
                $"{cheatId}: what the cheat does must not need opening.");

            XElement evidenceLine = ElementWithAutomationId(page, evidence);
            Assert.That(
                IsBehindADisclosure(evidenceLine),
                Is.True,
                $"{cheatId}: the evidence sentence belongs behind the disclosure, not under the tick box.");
            Assert.That(
                evidenceLine.Ancestors().Any(ancestor =>
                    ancestor.Name.LocalName == "Expander" &&
                    (string?)ancestor.Attribute("AutomationProperties.AutomationId") == disclosure),
                Is.True,
                $"{cheatId}: the evidence sentence should sit inside {disclosure}.");
        }

        Assert.That(
            File.ReadAllText(PageCodeBehindPath),
            Does.Contain("evidence.Text = cheat.WhatWeKnow"),
            "The collapsed line must still be the catalog's own evidence sentence, not page copy.");
    }

    [Test]
    public void ACheatNobodyHasWatchedWorkKeepsAShortMarkerOnScreen()
    {
        // Hiding the whole evidence sentence is fine. Hiding the fact that a switch has never been
        // seen doing what it says is not: that one changes whether a player should trust the tick
        // box at all, so a short tag stays visible and the sentence explains it underneath.
        XDocument page = XDocument.Parse(PageXaml);

        foreach ((string cheatId, _, _, _, string tag) in CheatSurfaces)
        {
            CheatCode cheat = CheatCodeCatalog.FindById(cheatId)!;
            string? marker = CheatsPageText.DescribeEvidenceTag(cheat);

            if (cheat.Evidence == CheatEvidenceLevel.FoundInGameCodeOnly)
            {
                Assert.That(
                    marker,
                    Is.EqualTo("Untested"),
                    $"{cheatId} has only been read out of the executable and must carry a visible marker.");
            }
            else
            {
                Assert.That(marker, Is.Null, $"{cheatId} has been watched working, so it carries no marker.");
            }

            Assert.That(
                IsBehindADisclosure(ElementWithAutomationId(page, tag)),
                Is.False,
                $"{cheatId}: the marker is only worth having if it is visible.");
        }

        Assert.That(
            CheatsPageText.DescribeEvidenceTag(CheatCodeCatalog.FindById(CheatCodeCatalog.FreeCameraId))!.Length,
            Is.LessThanOrEqualTo(12),
            "The marker is a tag, not a sentence. The sentence lives behind the disclosure.");
    }

    [Test]
    public void EveryDisclosureOnThePageCarriesTheSameLabel()
    {
        // One label, used everywhere, is the only reason a player learns what the collapsed panels
        // are for. A second wording would turn them back into a scavenger hunt.
        XElement[] disclosures = XDocument.Parse(PageXaml)
            .Descendants()
            .Where(element => element.Name.LocalName == "Expander")
            .ToArray();

        Assert.That(disclosures, Is.Not.Empty, "The page should collapse its evidence behind disclosures.");

        foreach (XElement disclosure in disclosures)
        {
            Assert.That(
                (string?)disclosure.Attribute("Header"),
                Is.EqualTo(CheatsPageText.EvidenceDisclosureLabel),
                "Every disclosure on this page shows the same label.");
        }
    }

    [Test]
    public void TheDisclosuresAreToldApartByTheirAccessibleNames()
    {
        // Nine controls that all read "How we know" would be nine identical controls to a screen
        // reader. The cheat disclosures take their name from the catalog so it cannot drift from
        // the tick box beside it.
        string[] catalogNames = CheatCodeCatalog.All
            .Select(CheatsPageText.BuildEvidenceDisclosureName)
            .ToArray();
        string[] markupNames = XDocument.Parse(PageXaml)
            .Descendants()
            .Where(element => element.Name.LocalName == "Expander")
            .Select(element => (string?)element.Attribute("AutomationProperties.Name"))
            .Where(name => name is not null)
            .Select(name => name!)
            .ToArray();

        string[] all = [.. catalogNames, .. markupNames];
        Assert.That(all, Is.Unique, "Each disclosure needs its own accessible name.");
        foreach (string name in all)
        {
            Assert.That(
                name,
                Does.StartWith(CheatsPageText.EvidenceDisclosureLabel),
                "The accessible name must contain the visible label so speech input can reach it.");
        }

        Assert.That(
            File.ReadAllText(PageCodeBehindPath),
            Does.Contain("CheatsPageText.BuildEvidenceDisclosureName"),
            "The cheat disclosures take their accessible name from the catalog, not from hand-typed markup.");
    }

    [Test]
    public void EachEmptyStateSaysWhatToDoNext_RatherThanDescribingTheEmptiness()
    {
        string noSaveChosen = CheatsPageText.BuildSourceSummary(null);
        string noDestination = CheatsPageText.BuildDestinationSummary(null, null);

        foreach (string sentence in new[] { noSaveChosen, noDestination })
        {
            Assert.That(
                sentence.Count(character => character == '.'),
                Is.EqualTo(1),
                $"An empty state is one sentence: '{sentence}'");
            Assert.That(
                sentence,
                Does.Not.Contain("yet").IgnoreCase,
                $"'{sentence}' reports a state the player can already see. Say what to do instead.");
        }

        Assert.That(noSaveChosen, Does.Contain("Choose a save"), "Name the button the player has to press.");
        Assert.That(noDestination, Does.Contain("Windowed & Mods"));
        Assert.That(noDestination, Does.Contain("Choose a folder"));
        Assert.That(
            noDestination,
            Is.EqualTo(CheatsPageText.NoSafeCopiesFoundNote),
            "The missing-safe-copy answer is one sentence wherever it is shown.");
        Assert.That(
            PageXaml,
            Does.Contain(noSaveChosen),
            "The markup's starting text must be the same sentence the code produces, or the page opens on a stale one.");
    }

    [Test]
    public void ThePageDoesNotBorrowTheEvidenceRegistersVocabulary()
    {
        // This tone is being removed from the app: a player should not have to learn the project's
        // internal evidence language to use a cheat menu.
        string[] banned = ["receipt", "manifest", "proof boundary", "byte-verified", "claim boundary"];
        string xaml = PageXaml;

        foreach (string word in banned)
        {
            Assert.That(xaml, Does.Not.Contain(word).IgnoreCase, $"Cheats page copy should not use '{word}'.");
        }

        foreach (CheatCode cheat in CheatCodeCatalog.All)
        {
            foreach (string word in banned)
            {
                Assert.That(cheat.WhatItDoes, Does.Not.Contain(word).IgnoreCase);
                Assert.That(cheat.WhatWeKnow, Does.Not.Contain(word).IgnoreCase);
            }
        }
    }

    [Test]
    public void FreeCameraIsOfferedAsTheSaveNameCheatFirst_AndThePatchRouteIsTheLabelledExtra()
    {
        // The save-name route passes the game's own gate with nothing modified, which is strictly
        // better than the executable patch that only exists to skip that same gate.
        string xaml = PageXaml;

        Assert.That(xaml, Does.Contain("CheatsFreeCameraCheckBox"));
        Assert.That(xaml, Does.Contain("Debug Camera Preview"));
        Assert.That(
            xaml,
            Does.Contain("not a full flying camera"),
            "The bounded profile covers the toggle and one movement direction, not a camera mode.");
        Assert.That(
            xaml,
            Does.Not.Contain("free_camera_"),
            "The page should not make a player read patch row ids.");
    }

    [Test]
    public void TheNameExplanationNamesEveryCheatTheFileNameWillSwitchOn()
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            null,
            [CheatCodeCatalog.AllGoodiesId, CheatCodeCatalog.AllLevelsId]);

        string explanation = CheatsPageText.BuildNameExplanation(composed);

        Assert.That(explanation, Does.Contain("All goodies"));
        Assert.That(explanation, Does.Contain("All levels"));
    }

    [Test]
    public void TheNameExplanationOwnsUpToACheatTheTypedNameSmuggledIn()
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            "TURKEYdinner",
            [CheatCodeCatalog.AllGoodiesId]);

        string explanation = CheatsPageText.BuildNameExplanation(composed);

        Assert.That(explanation, Does.Contain("All levels"));
        Assert.That(explanation, Does.Contain("name you typed"));
    }

    [Test]
    public void ARejectedNameShowsItsReasonRatherThanAFileName()
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose("bad:name", [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(CheatsPageText.BuildNameHeadline(composed), Does.Not.Contain(".bes"));
        Assert.That(CheatsPageText.BuildNameExplanation(composed), Is.EqualTo(composed.Problem));
    }

    [Test]
    public void TheWriteButtonStaysBlockedUntilEveryPieceIsThere()
    {
        CheatSaveName ready = CheatSaveNameComposer.Compose(null, [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(CheatsPageText.DescribeWhatIsStillNeeded(null, ready, "C:\\out"), Is.Not.Null);
        Assert.That(CheatsPageText.DescribeWhatIsStillNeeded("C:\\a.bes", null, "C:\\out"), Is.Not.Null);
        Assert.That(CheatsPageText.DescribeWhatIsStillNeeded("C:\\a.bes", ready, null), Is.Not.Null);
        Assert.That(CheatsPageText.DescribeWhatIsStillNeeded("C:\\a.bes", ready, "C:\\out"), Is.Null);
    }

    [Test]
    public void TheSourceSummaryPromisesTheOriginalIsOnlyRead()
    {
        string summary = CheatsPageText.BuildSourceSummary(Path.Combine("C:", "saves", "MyCareer.bes"));

        Assert.That(summary, Does.Contain("MyCareer.bes"));
        Assert.That(summary, Does.Contain("not changed"));
        Assert.That(summary, Does.Not.Contain("C:\\saves"), "A full path should not be shown back to the player.");
    }

    [Test]
    public void TheOverwriteQuestionSaysItCannotBeUndone()
    {
        string question = CheatsPageText.BuildOverwriteQuestion("MALLOY.bes");

        Assert.That(question, Does.Contain("MALLOY.bes"));
        Assert.That(question, Does.Contain("cannot be undone"));
    }
}
