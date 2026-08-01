using System;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The quick-start card is the answer to "a new player goes from download to a
/// running game without reading anything". Its whole contract is that at any
/// moment there is exactly one sensible next action, it has a button, and the
/// button says what will happen.
/// </summary>
public class HomeQuickStartStateTests
{
    [Test]
    public void AFreshInstallIsAskedForTheGameFolderFirst()
    {
        HomeQuickStartState state = HomeQuickStartState.Resolve(
            gameFolderSet: false, gameFolderComplete: false, safeCopyExists: false, safeCopyRunning: false);

        Assert.That(state.Stage, Is.EqualTo(HomeQuickStartStage.FindGame));
        Assert.That(state.PrimaryActionLabel, Is.EqualTo("Find my game"));
        Assert.That(state.ShowsSecondaryChooseFolder, Is.True, "A failed auto-detect must leave a way forward.");
    }

    [Test]
    public void AConfiguredGameWithNoCopyOffersTheOneButtonPath()
    {
        HomeQuickStartState state = HomeQuickStartState.Resolve(
            gameFolderSet: true, gameFolderComplete: true, safeCopyExists: false, safeCopyRunning: false);

        Assert.That(state.Stage, Is.EqualTo(HomeQuickStartStage.MakeCopy));
        Assert.That(state.PrimaryActionLabel, Is.EqualTo("Set up and play"));
    }

    [Test]
    public void AnExistingCopyJustPlays()
    {
        HomeQuickStartState state = HomeQuickStartState.Resolve(
            gameFolderSet: true, gameFolderComplete: true, safeCopyExists: true, safeCopyRunning: false);

        Assert.That(state.Stage, Is.EqualTo(HomeQuickStartStage.Play));
        Assert.That(state.PrimaryActionLabel, Is.EqualTo("Play"));
    }

    [Test]
    public void ARunningCopyTakesPriorityOverEveryOtherState()
    {
        HomeQuickStartState state = HomeQuickStartState.Resolve(
            gameFolderSet: false, gameFolderComplete: false, safeCopyExists: false, safeCopyRunning: true);

        Assert.That(state.Stage, Is.EqualTo(HomeQuickStartStage.Running));
    }

    [Test]
    public void AnIncompleteInstallSaysWhatIsMissingRatherThanFailingLater()
    {
        HomeQuickStartState state = HomeQuickStartState.Resolve(
            gameFolderSet: true, gameFolderComplete: false, safeCopyExists: false, safeCopyRunning: false);

        Assert.That(state.Stage, Is.EqualTo(HomeQuickStartStage.FixGame));
        Assert.That(state.Body, Does.Contain("BEA.exe"));
        Assert.That(state.ShowsSecondaryChooseFolder, Is.True);
    }

    [Test]
    public void EveryStateHasSomethingToReadAndSomethingToPress()
    {
        foreach (bool set in new[] { false, true })
        foreach (bool complete in new[] { false, true })
        foreach (bool exists in new[] { false, true })
        foreach (bool running in new[] { false, true })
        {
            HomeQuickStartState state = HomeQuickStartState.Resolve(set, complete, exists, running);
            Assert.That(state.Title, Is.Not.Empty);
            Assert.That(state.Body, Is.Not.Empty);
            Assert.That(state.PrimaryActionLabel, Is.Not.Empty);
        }
    }

    [Test]
    public void TheCardNeverSpeaksInTheProjectsInternalVocabulary()
    {
        // The goal says the app must never read like a technical manual. This
        // card is the first thing a new player sees, so it is held to that
        // hardest.
        string[] banned =
        {
            "receipt", "manifest", "provenance", "byte-verified", "specimen",
            "catalog", "preflight", "profile root", "proof level", "dword",
        };

        foreach (bool set in new[] { false, true })
        foreach (bool complete in new[] { false, true })
        foreach (bool exists in new[] { false, true })
        foreach (bool running in new[] { false, true })
        {
            HomeQuickStartState state = HomeQuickStartState.Resolve(set, complete, exists, running);
            string all = $"{state.Title} {state.Body} {state.PrimaryActionLabel}".ToLowerInvariant();
            foreach (string word in banned)
            {
                Assert.That(all, Does.Not.Contain(word), $"Quick-start copy should not say '{word}'.");
            }
        }
    }

    [Test]
    public void TheSafetyPromiseIsMadeWhereItMatters()
    {
        // Before the app copies gigabytes or starts a game, it should say the
        // installed game is left alone - that is the project's central promise
        // and the moment a new player most needs to hear it.
        HomeQuickStartState makeCopy = HomeQuickStartState.Resolve(true, true, false, false);
        Assert.That(makeCopy.Body.ToLowerInvariant(), Does.Contain("installed game"));

        HomeQuickStartState findGame = HomeQuickStartState.Resolve(false, false, false, false);
        Assert.That(findGame.Body.ToLowerInvariant(), Does.Contain("only ever reads"));
    }
}
