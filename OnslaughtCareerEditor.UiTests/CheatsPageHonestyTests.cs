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
/// Those are properties of strings, which drift silently. This suite pins them.
/// </summary>
public class CheatsPageHonestyTests
{
    private static string PageXamlPath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "CheatsPage.xaml");

    private static string PageXaml => File.ReadAllText(PageXamlPath);

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
