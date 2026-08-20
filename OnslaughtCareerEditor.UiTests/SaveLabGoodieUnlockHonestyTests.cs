using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Save Lab tells a player what a Goodie is, and lets them set its state,
/// but never told them what earning it in the real game would have required -
/// even though <see cref="GoodieUnlockRequirementService"/> has had every rule
/// mapped and tested in AppCore the whole time. This is that surface.
///
/// These tests pin the player-facing sentence and, more importantly, pin that
/// the RE evidence label never reaches it.
/// </summary>
public sealed class SaveLabGoodieUnlockHonestyTests
{
    [Test]
    public void AMappedGoodieNamesWhatTheGameAsksFor()
    {
        Assert.That(
            SaveLabPageText.DescribeFocusedGoodieUnlock(0),
            Is.EqualTo("How the game unlocks Goodie 000: Complete level 100."));
    }

    [Test]
    public void AGradeGoodieNamesTheGradeAndTheLevel()
    {
        Assert.That(
            SaveLabPageText.DescribeFocusedGoodieUnlock(1),
            Does.Contain("Earn C or better on level 110."));
    }

    [Test]
    public void AReservedSlotSaysItIsPreservedNotEarned()
    {
        string painted = SaveLabPageText.DescribeFocusedGoodieUnlock(250);

        Assert.Multiple(() =>
        {
            Assert.That(painted, Does.Contain("reserved save slot"));
            Assert.That(painted, Does.Contain("preserved, not earned"));
            Assert.That(painted, Does.Not.Contain("How the game unlocks"));
        });
    }

    [Test]
    public void AnUnmappedGoodieSaysSoInsteadOfGuessing()
    {
        string painted = SaveLabPageText.DescribeFocusedGoodieUnlock(9999);

        Assert.Multiple(() =>
        {
            Assert.That(painted, Does.Contain("has not mapped"));
            Assert.That(painted, Does.Not.Contain("Unlock rule not mapped yet."));
        });
    }

    [Test]
    public void ThePaintNeverCarriesTheResearchEvidenceLabel()
    {
        // GoodieUnlockRequirement carries an EvidenceLabel like
        // "CCareer__UpdateGoodieStates 0x0041c470" / "RE follow-up required".
        // That is a research pointer. It must never reach a player.
        foreach (int goodieId in new[] { 0, 1, 8, 79, 121, 164, 205, 250, 9999 })
        {
            string painted = SaveLabPageText.DescribeFocusedGoodieUnlock(goodieId);

            Assert.That(painted, Does.Not.Contain("CCareer"), $"Goodie {goodieId}");
            Assert.That(painted, Does.Not.Contain("0x00"), $"Goodie {goodieId}");
            Assert.That(painted, Does.Not.Contain("RE follow-up"), $"Goodie {goodieId}");
            Assert.That(painted, Does.Not.Contain("mGoodies"), $"Goodie {goodieId}");
            Assert.That(painted, Does.Not.Contain("SetGoodieState"), $"Goodie {goodieId}");
        }
    }
}
