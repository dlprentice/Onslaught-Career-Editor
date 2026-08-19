using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The one place in the app that offers to change something a person cannot simply recreate.
///
/// Two things have to reach somebody before they press anything: that this is their real game and
/// not a copy, and that the original is copied and checked first. Neither may end up behind a
/// disclosure, and neither may be softened into a reassurance that outruns what the engine does -
/// in particular the restore is a whole-file snapshot from before the first patch, not a per-patch
/// undo, and nothing here may imply otherwise.
///
/// This suite also holds the line the rest of the app used to state absolutely. "Your installed
/// game is never changed" was true and is not any more; the honest replacement is not silence, it
/// is saying that copies are the default and the opt-in backs you up first.
/// </summary>
[TestFixture]
public class InstalledGamePatchSurfaceTests
{
    private static string RepoRoot()
    {
        DirectoryInfo? directory = new(TestContext.CurrentContext.TestDirectory);
        while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "package.json")))
            directory = directory.Parent;

        Assert.That(directory, Is.Not.Null, "Could not find the repository root.");
        return directory!.FullName;
    }

    private static string PageXaml() =>
        File.ReadAllText(Path.Combine(RepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"));

    private static string PageCode() =>
        File.ReadAllText(Path.Combine(RepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs"));

    [Test]
    public void TheCardShipsInTheMarkupWithStableAccessibleIds()
    {
        string xaml = PageXaml();

        foreach (string id in new[]
                 {
                     "PatchBenchInstalledGameCard",
                     "PatchBenchInstalledGameTitle",
                     "PatchBenchInstalledGameIntro",
                     "PatchBenchInstalledGameStatus",
                     "PatchBenchInstalledGameBackupButton",
                     "PatchBenchInstalledGamePatchButton",
                     "PatchBenchInstalledGameRestoreButton",
                     "PatchBenchInstalledGameRestoreScope",
                     "PatchBenchInstalledGameNote",
                 })
        {
            Assert.That(xaml, Does.Contain($"AutomationProperties.AutomationId=\"{id}\""), $"{id} must stay in the markup.");
        }
    }

    [Test]
    public void TheVisibleWordsMatchTheTextHelperExactly()
    {
        string xaml = PageXaml();

        Assert.Multiple(() =>
        {
            Assert.That(xaml, Does.Contain($"Text=\"{InstalledGamePatchText.SectionTitle}\""));
            Assert.That(xaml, Does.Contain($"Text=\"{InstalledGamePatchText.Introduction}\""));
            Assert.That(xaml, Does.Contain($"Text=\"{InstalledGamePatchText.RestoreScopeNote}\""));
            Assert.That(xaml, Does.Contain($"Content=\"{InstalledGamePatchText.BackupButtonText}\""));
            Assert.That(xaml, Does.Contain($"Content=\"{InstalledGamePatchText.PatchButtonText}\""));
            Assert.That(xaml, Does.Contain($"Content=\"{InstalledGamePatchText.RestoreButtonText}\""));
        });
    }

    /// <summary>WCAG 2.5.3, and the audit enforces it for every labelled button on the page.</summary>
    [Test]
    public void EveryAccessibleNameContainsItsVisibleLabel()
    {
        Assert.Multiple(() =>
        {
            Assert.That(InstalledGamePatchText.BackupButtonAccessibleName, Does.Contain(InstalledGamePatchText.BackupButtonText));
            Assert.That(InstalledGamePatchText.PatchButtonAccessibleName, Does.Contain(InstalledGamePatchText.PatchButtonText));
            Assert.That(InstalledGamePatchText.RestoreButtonAccessibleName, Does.Contain(InstalledGamePatchText.RestoreButtonText));
        });
    }

    /// <summary>
    /// The two facts that must not be behind a disclosure: it is the real game, and the original is
    /// copied first. A person who reads only what is on screen has to meet both.
    /// </summary>
    [Test]
    public void TheOnScreenWordsSayItIsTheRealGameAndThatTheOriginalIsCopiedFirst()
    {
        string onScreen = InstalledGamePatchText.SectionTitle + " " + InstalledGamePatchText.Introduction;

        Assert.That(onScreen, Does.Contain("installed"));
        Assert.That(onScreen, Does.Contain("original"));
        Assert.That(onScreen, Does.Contain("put it back"));
        Assert.That(
            PageXaml(),
            Does.Not.Contain($"Header=\"{InstalledGamePatchText.SectionTitle}\""),
            "The section must not be an Expander header - it may not start collapsed.");
    }

    /// <summary>
    /// The restore is a whole-file snapshot taken before the first patch. Saying "undo" without
    /// saying "all of them" would be a promise the engine does not keep.
    /// </summary>
    [Test]
    public void TheRestoreScopeIsStatedRatherThanImplied()
    {
        Assert.That(InstalledGamePatchText.RestoreScopeNote, Does.Contain("before the first patch"));
        Assert.That(InstalledGamePatchText.RestoreScopeNote, Does.Contain("every patch at once, not the last one"));
        Assert.That(InstalledGamePatchText.RestoreScopeNote, Does.Contain("does not touch your saves"));
    }

    [Test]
    public void TheConfirmationNamesTheFolderItIsAboutToChange()
    {
        string confirmation = InstalledGamePatchText.BuildPatchConfirmation(
            @"C:\Games\Battle Engine Aquila\BEA.exe",
            "Windowed, Widescreen");

        Assert.That(confirmation, Does.Contain("Battle Engine Aquila"));
        Assert.That(confirmation, Does.Contain("Windowed, Widescreen"));
        Assert.That(confirmation, Does.Not.Contain(@"C:\Games"));
        Assert.That(confirmation, Does.Not.Contain(@":\"));
        Assert.That(
            confirmation,
            Does.Contain("If the copy cannot be made, nothing is patched"),
            "The one thing somebody needs to believe is that a failed backup means a failed patch.");
    }

    [Test]
    public void TheRestoreConfirmationNamesTheFolderNotThePath()
    {
        string confirmation = InstalledGamePatchText.BuildRestoreConfirmation(
            @"C:\Games\Battle Engine Aquila\BEA.exe");

        Assert.That(confirmation, Does.Contain("Battle Engine Aquila"));
        Assert.That(confirmation, Does.Contain(InstalledGamePatchText.RestoreScopeNote));
        Assert.That(confirmation, Does.Not.Contain(@"C:\Games"));
        Assert.That(confirmation, Does.Not.Contain(@":\"));
    }

    [Test]
    public void TheStatusLineNamesTheFolderNotThePath()
    {
        string path = Path.Combine("C:" + Path.DirectorySeparatorChar + "Steam", "steamapps", "common", "Battle Engine Aquila", "BEA.exe");
        string status = InstalledGamePatchText.BuildStatusLine(InstalledGamePatchReadiness.CleanAndUnbackedUp, path);

        Assert.That(status, Does.Contain("Battle Engine Aquila"));
        Assert.That(status, Does.Not.Contain(path));
        Assert.That(status, Does.Not.Contain("steamapps"));
        Assert.That(status, Does.Not.Contain(":\\"));
    }

    [Test]
    public void AnUnbackedInstallDoesNotSayYet()
    {
        string status = InstalledGamePatchText.BuildStatusLine(
            InstalledGamePatchReadiness.CleanAndUnbackedUp,
            null);

        Assert.That(status, Does.Contain("Nothing has been backed up."));
        Assert.That(status, Does.Contain("copy the original first"));
        Assert.That(status, Does.Not.Contain("yet"));
    }

    [Test]
    public void AFailedBackupNamesTheActionWithoutTheException()
    {
        Assert.That(BinaryPatchEngine.InstalledBackupFailed, Does.Contain("backup could not be made"));
        Assert.That(BinaryPatchEngine.InstalledBackupFailed, Does.Contain("untouched"));
        Assert.That(BinaryPatchEngine.InstalledBackupFailed, Does.Not.Contain(":\\"));
        Assert.That(BinaryPatchEngine.InstalledBackupFailed.ToLowerInvariant(), Does.Not.Contain("exception"));
        Assert.That(BinaryPatchEngine.InstalledPathUnreadable, Does.Contain("could not be read"));
        Assert.That(BinaryPatchEngine.InstalledPathUnreadable, Does.Contain("Nothing was changed"));
        Assert.That(BinaryPatchEngine.InstalledPathUnreadable, Does.Not.Contain(":\\"));

        string engine = File.ReadAllText(Path.Combine(RepoRoot(), "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));
        Assert.That(engine, Does.Contain("InstalledBackupFailed"));
        Assert.That(engine, Does.Contain("InstalledPathUnreadable"));
        Assert.That(engine, Does.Not.Contain("your game is untouched: {ex.Message}"));
        Assert.That(engine, Does.Not.Contain("That path could not be read: {ex.Message}"));
    }

    [Test]
    public void TheRestoreConfirmationCarriesTheSameScopeSentence()
    {
        Assert.That(
            InstalledGamePatchText.BuildRestoreConfirmation(@"C:\Games\Battle Engine Aquila\BEA.exe"),
            Does.Contain(InstalledGamePatchText.RestoreScopeNote));
    }

    // ------------------------------------------------------------------ what is offered

    [Test]
    public void NothingIsOfferedUntilThereIsAGame()
    {
        Assert.Multiple(() =>
        {
            Assert.That(InstalledGamePatchText.CanBackUp(InstalledGamePatchReadiness.NoGameChosen), Is.False);
            Assert.That(InstalledGamePatchText.CanPatch(InstalledGamePatchReadiness.NoGameChosen), Is.False);
            Assert.That(InstalledGamePatchText.CanRestore(InstalledGamePatchReadiness.NoGameChosen), Is.False);
        });
    }

    [Test]
    public void AMissingInstallNamesTheNextStepNotTheEmptiness()
    {
        string status = InstalledGamePatchText.BuildStatusLine(InstalledGamePatchReadiness.NoGameChosen, null);

        Assert.That(status, Does.Contain("Settings"));
        Assert.That(status, Does.Contain("BEA.exe"));
        Assert.That(status, Does.Not.Contain("yet").IgnoreCase);
        Assert.That(status, Does.Not.Contain("No installed game chosen"));
        Assert.That(status, Does.Not.Contain(":\\"));
        Assert.That(status, Does.Not.Contain("/"));
    }

    /// <summary>
    /// A changed executable with no original beside it is the state the app cannot rescue. Offering
    /// to patch it would be offering something that cannot be undone.
    /// </summary>
    [Test]
    public void APatchIsNotOfferedWhenThereIsNothingToGoBackTo()
    {
        const InstalledGamePatchReadiness stuck = InstalledGamePatchReadiness.ChangedWithNothingToGoBackTo;

        Assert.Multiple(() =>
        {
            Assert.That(InstalledGamePatchText.CanPatch(stuck), Is.False);
            Assert.That(InstalledGamePatchText.CanBackUp(stuck), Is.False);
            Assert.That(InstalledGamePatchText.CanRestore(stuck), Is.False);
            Assert.That(
                InstalledGamePatchText.BuildStatusLine(stuck, null),
                Does.Contain("will not copy a changed file and call it the original"));
        });
    }

    [Test]
    public void PuttingItBackIsOnlyOfferedOnceThereIsSomethingToPutBack()
    {
        Assert.That(InstalledGamePatchText.CanRestore(InstalledGamePatchReadiness.CleanAndUnbackedUp), Is.False);
        Assert.That(InstalledGamePatchText.CanRestore(InstalledGamePatchReadiness.BackedUp), Is.True);
    }

    [Test]
    public void ACleanGameCanBeBackedUpOrPatchedStraightAway()
    {
        const InstalledGamePatchReadiness clean = InstalledGamePatchReadiness.CleanAndUnbackedUp;

        Assert.That(InstalledGamePatchText.CanBackUp(clean), Is.True);
        Assert.That(InstalledGamePatchText.CanPatch(clean), Is.True);
        Assert.That(
            InstalledGamePatchText.BuildStatusLine(clean, null),
            Does.Contain("copy the original first"));
    }

    [Test]
    public void ReadinessReadsAMissingFileAsNoGameRatherThanAsAProblem()
    {
        Assert.That(
            InstalledGamePatchText.DescribeReadiness(Path.Combine(Path.GetTempPath(), $"nope-{Guid.NewGuid():N}.exe")),
            Is.EqualTo(InstalledGamePatchReadiness.NoGameChosen));
    }

    [Test]
    public void ALockedExecutableIsNotCalledAlreadyChanged()
    {
        string path = Path.Combine(Path.GetTempPath(), $"bea-locked-{Guid.NewGuid():N}.exe");
        File.WriteAllBytes(path, new byte[2_506_752]);
        try
        {
            using var exclusive = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.None);

            InstalledGamePatchReadiness readiness = InstalledGamePatchText.DescribeReadiness(path);

            Assert.That(readiness, Is.EqualTo(InstalledGamePatchReadiness.Unreadable));
            Assert.That(InstalledGamePatchText.CanPatch(readiness), Is.False);
            Assert.That(InstalledGamePatchText.CanBackUp(readiness), Is.False);
            string status = InstalledGamePatchText.BuildStatusLine(readiness, null);
            Assert.That(status.ToLowerInvariant(), Does.Contain("could not read"));
            Assert.That(status.ToLowerInvariant(), Does.Not.Contain("already changed"));
            Assert.That(status.ToLowerInvariant(), Does.Not.Contain("will not copy a changed file"));
        }
        finally
        {
            if (File.Exists(path))
                File.Delete(path);
        }
    }

    // ------------------------------------------------------------------ the handlers

    [Test]
    public void TheHandlersGoThroughTheAuthorizationRatherThanWritingDirectly()
    {
        string code = PageCode();

        Assert.Multiple(() =>
        {
            Assert.That(
                code,
                Does.Contain("BinaryPatchEngine.AuthorizeInstalledGameWrite"),
                "The backup is obtained through the authorization, which is what makes it non-optional.");
            Assert.That(
                code,
                Does.Contain("InstalledGamePatchText.ConfirmPatchTitle"),
                "Patching the real game must be confirmed.");
            Assert.That(
                code,
                Does.Contain("InstalledGamePatchText.ConfirmRestoreTitle"),
                "So must putting it back.");
            Assert.That(
                code,
                Does.Not.Contain("File.WriteAllBytes"),
                "Nothing on this page writes an executable itself; the engine does, atomically and verified.");
        });
    }

    /// <summary>
    /// Drawing a page must not change anything on disk. <c>DescribeReadiness</c> exists precisely so
    /// the status line can be computed without asking for permission, because asking for permission
    /// writes a backup.
    /// </summary>
    [Test]
    public void DrawingThePageDoesNotTakeABackupAsASideEffect()
    {
        string code = PageCode();
        int updateStart = code.IndexOf("private void UpdateInstalledGameState()", StringComparison.Ordinal);
        Assert.That(updateStart, Is.GreaterThanOrEqualTo(0));

        int updateEnd = code.IndexOf("private void ShowInstalledGameNote", updateStart, StringComparison.Ordinal);
        Assert.That(updateEnd, Is.GreaterThan(updateStart));

        Assert.That(
            code[updateStart..updateEnd],
            Does.Not.Contain("AuthorizeInstalledGameWrite"),
            "The state refresh runs on every control update; a backup must never be one of its effects.");
    }

    // ------------------------------------------------------------------ the old absolute

    /// <summary>
    /// The app used to promise, in several places, that the installed game is never changed. That
    /// became false. Removing the promise and saying nothing would be worse than the overclaim, so
    /// the pages that made it now say what is actually true: copies by default, opt-in with a
    /// backup.
    /// </summary>
    [Test]
    public void ThePagesThatPromisedTheGameWasNeverTouchedNowSayWhatIsTrue()
    {
        string root = RepoRoot();
        string home = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "HomePage.xaml"));
        string about = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "AboutPage.xaml"));
        string patchBench = PageXaml();

        Assert.Multiple(() =>
        {
            Assert.That(home, Does.Not.Contain("Your installed game is only ever read - every change lands in a separate copy."));
            Assert.That(home, Does.Contain("you can choose to patch it instead, and the app backs it up first"));
            Assert.That(about, Does.Not.Contain("without ever touching your installed copy"));
            Assert.That(about, Does.Contain("backing up your original first"));
            Assert.That(patchBench, Does.Not.Contain("Your Steam install is never changed."));
            Assert.That(patchBench, Does.Contain("copies your original executable first"));
        });
    }

    [Test]
    public void InstalledPatchAndRestoreUseTheNamedFailureSentence()
    {
        string code = PageCode();
        Assert.That(code, Does.Contain("PatchBenchSafeCopyOutcomeText.DescribeInstalledWriteFailure"));
        Assert.That(code, Does.Not.Contain("applied ? $\"{authorizationMessage} Your game is patched.\" : applyMessage"));
        Assert.That(code, Does.Not.Contain("success ? \"Your game is back the way it was.\" : message"));
    }

    [Test]
    public void ANamedFailureIsNotSaidTwice()
    {
        string note = InstalledGamePatchText.BuildOutcomeNote(false, BinaryPatchEngine.InstalledPathUnreadable);

        Assert.That(note, Is.EqualTo(BinaryPatchEngine.InstalledPathUnreadable));
        Assert.That(note, Does.Contain("Nothing was changed"));
        Assert.That(
            note.Split("Nothing was changed", StringSplitOptions.None).Length - 1,
            Is.EqualTo(1));
    }
}
