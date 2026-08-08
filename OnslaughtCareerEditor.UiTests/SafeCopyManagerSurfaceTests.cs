using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The list that had to exist before deleting a copy could be offered at all.
///
/// The app could make copies and never showed them: no list, no size, no total, and the only route
/// that removed one was a CLI verb. Offering to delete something somebody cannot see is not an
/// offer, so the list came first and the delete hangs off it.
///
/// The delete wording is what this suite mostly guards. A copy is disposable; the careers played
/// inside it are the one thing in that folder the game cannot make again, so when careers are
/// present the dialog must not reduce to a single yes/no - keeping them has to be an answer, and
/// the default one.
/// </summary>
[TestFixture]
public class SafeCopyManagerSurfaceTests
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

    private static SafeCopyOverview Overview(
        string name = "my-copy",
        long sizeBytes = 700L * 1024 * 1024,
        int careers = 0,
        bool playable = true)
    {
        return new SafeCopyOverview(
            name,
            $@"X:\GameProfiles\{name}",
            sizeBytes,
            new DateTime(2026, 8, 1, 12, 0, 0, DateTimeKind.Utc),
            new DateTime(2026, 8, 1, 12, 0, 0, DateTimeKind.Utc),
            careers,
            playable);
    }

    [Test]
    public void TheCardShipsInTheMarkupWithStableAccessibleIds()
    {
        string xaml = PageXaml();

        foreach (string id in new[]
                 {
                     "SafeCopyManagerCard",
                     "SafeCopyManagerTitle",
                     "SafeCopyManagerIntro",
                     "SafeCopyManagerTotal",
                     "SafeCopyManagerList",
                     "SafeCopyManagerRefreshButton",
                     "SafeCopyManagerNote",
                 })
        {
            Assert.That(xaml, Does.Contain($"AutomationProperties.AutomationId=\"{id}\""), $"{id} must stay in the markup.");
        }
    }

    [Test]
    public void TheVisibleWordsMatchTheTextHelperExactly()
    {
        string xaml = PageXaml();

        Assert.That(xaml, Does.Contain($"Text=\"{SafeCopyManagerText.SectionTitle}\""));
        Assert.That(xaml, Does.Contain($"Text=\"{SafeCopyManagerText.Introduction}\""));
        Assert.That(xaml, Does.Contain($"Content=\"{SafeCopyManagerText.RefreshButtonText}\""));
    }

    [Test]
    public void EachRowIsAddressableAndItsButtonsSayWhichCopyTheyActOn()
    {
        var item = new SafeCopyManagerItem(Overview("trainer-proof"));

        Assert.Multiple(() =>
        {
            Assert.That(item.SafeCopyRowAutomationId, Is.EqualTo("SafeCopyRow_trainer_proof"));
            Assert.That(item.DeleteAutomationId, Is.EqualTo("SafeCopyRowDelete_trainer_proof"));
            Assert.That(item.DeleteAccessibleName, Is.EqualTo("Delete trainer-proof"));
            Assert.That(item.LaunchAccessibleName, Does.Contain("trainer-proof"));
            Assert.That(item.OpenFolderAccessibleName, Does.Contain("trainer-proof"));
        });
    }

    [Test]
    public void ARowLeadsWithTheNumberSomebodyCameLookingFor()
    {
        var item = new SafeCopyManagerItem(Overview(sizeBytes: 2L * 1024 * 1024 * 1024, careers: 3));

        Assert.That(item.SizeText, Is.EqualTo("2.0 GB"));
        Assert.That(item.DetailText, Does.Contain("3 careers inside"));
    }

    [Test]
    public void ACopyWithNoExecutableSaysWhyItCannotBeLaunched()
    {
        var item = new SafeCopyManagerItem(Overview(playable: false));

        Assert.That(item.CanLaunch, Is.False);
        Assert.That(item.DetailText, Does.Contain("cannot be launched"));
    }

    [Test]
    public void TheTotalLineAnswersHowManyAndHowMuch()
    {
        string total = SafeCopyManagerText.BuildTotalLine(new[]
        {
            Overview("a", 1024L * 1024 * 1024, careers: 1),
            Overview("b", 1024L * 1024 * 1024),
        });

        Assert.That(total, Does.Contain("2 safe copies"));
        Assert.That(total, Does.Contain("2.0 GB"));
        Assert.That(total, Does.Contain("1 career"));
    }

    [Test]
    public void WithNoCopiesTheLineSaysWhereTheyComeFrom()
    {
        Assert.That(
            SafeCopyManagerText.BuildTotalLine(Array.Empty<SafeCopyOverview>()),
            Is.EqualTo(SafeCopyManagerText.EmptyNote));
        Assert.That(SafeCopyManagerText.EmptyNote, Does.Contain("Create one above"));
    }

    // ------------------------------------------------------------------ the delete

    /// <summary>
    /// Careers present must not reduce to a yes/no. "This may delete save data" is a sentence
    /// people click past; "this deletes Maladim" is not, and keeping it has to be an option rather
    /// than a thing you knew to do beforehand.
    /// </summary>
    [Test]
    public void DeletingACopyWithCareersInItNamesThemAndOffersToKeepThem()
    {
        var save = new SafeCopySaveFile("Maladim.bes", @"X:\c\savegames\Maladim.bes", "savegames", 10004, DateTime.UtcNow);
        var inventory = new SafeCopySaveInventory(@"X:\c", "my-copy", new[] { save });

        string body = SafeCopyManagerText.BuildDeleteWithCareersBody(inventory, "700 MB");

        Assert.Multiple(() =>
        {
            Assert.That(body, Does.Contain("Maladim"));
            Assert.That(body, Does.Contain(SafeCopyManagerText.KeepCareersButtonText));
            Assert.That(body, Does.Contain("cannot be undone"));
            Assert.That(
                body,
                Does.Contain("only deletes the copy once every one of them is safely there"),
                "The ordering guarantee is the reason keeping them is safe; it has to be stated.");
        });
    }

    [Test]
    public void DeletingAnEmptyCopySaysTheFilesCanBeMadeAgain()
    {
        string body = SafeCopyManagerText.BuildDeleteBody("my-copy", "700 MB");

        Assert.That(body, Does.Contain("700 MB"));
        Assert.That(body, Does.Contain("no careers inside"));
        Assert.That(body, Does.Contain("copied again from your install"));
    }

    [Test]
    public void TheDeleteDialogWithCareersIsNotAYesNoQuestion()
    {
        string code = PageCode();

        Assert.Multiple(() =>
        {
            Assert.That(
                code,
                Does.Contain("SecondaryButtonText = SafeCopyManagerText.DeleteEverythingButtonText"),
                "Losing the careers must be a distinct answer, not the only one.");
            Assert.That(
                code,
                Does.Contain("PrimaryButtonText = SafeCopyManagerText.KeepCareersButtonText"),
                "Keeping them must be the first answer.");
            Assert.That(
                code,
                Does.Contain("DefaultButton = ContentDialogButton.Primary"),
                "And the default one.");
            Assert.That(
                code,
                Does.Contain("SafeCopySaveRescueService.RescueThenDelete"),
                "Keeping them must use the routine where the delete is unreachable until the rescue succeeded.");
        });
    }

    [Test]
    public void ChoosingToKeepCareersAndThenNotChoosingAFolderLeavesTheCopyAlone()
    {
        Assert.That(
            PageCode(),
            Does.Contain("Left the copy alone - no folder was chosen for the careers."),
            "Backing out of the folder picker must not fall through to a delete.");
    }

    // ------------------------------------------------------------------ free space

    [Test]
    public void ACopyThatWillNotFitIsSaidSoBeforeItIsStarted()
    {
        string? problem = SafeCopyManagerText.DescribeSpaceProblem(
            freeSpaceBytes: 100L * 1024 * 1024,
            sourceSizeBytes: 700L * 1024 * 1024);

        Assert.That(problem, Is.Not.Null);
        Assert.That(problem, Does.Contain("700 MB"));
        Assert.That(problem, Does.Contain("100 MB"));
        Assert.That(problem, Does.Contain("delete a copy you are finished with"));
    }

    [Test]
    public void RoomForTheCopyMeansNothingIsSaid()
    {
        Assert.That(
            SafeCopyManagerText.DescribeSpaceProblem(
                freeSpaceBytes: 40L * 1024 * 1024 * 1024,
                sourceSizeBytes: 700L * 1024 * 1024),
            Is.Null);
    }

    /// <summary>
    /// A volume that will not report its free space is a volume the app knows nothing about.
    /// Refusing on that basis would be inventing a problem.
    /// </summary>
    [Test]
    public void UnknownFreeSpaceIsNotTreatedAsNoSpace()
    {
        Assert.That(
            SafeCopyManagerText.DescribeSpaceProblem(freeSpaceBytes: null, sourceSizeBytes: 700L * 1024 * 1024),
            Is.Null);
    }

    /// <summary>
    /// The space warning rides inside the existing confirmation rather than becoming a second
    /// dialog, so the create path keeps its pinned ordering: revalidate, return, confirm, only then
    /// mutate.
    /// </summary>
    [Test]
    public void TheSpaceWarningDoesNotAddASecondGateToTheCreatePath()
    {
        string code = PageCode();
        int spaceCheck = code.IndexOf("DescribeSpaceProblem", StringComparison.Ordinal);
        int confirm = code.IndexOf("\"Create safe copy?\"", StringComparison.Ordinal);

        Assert.That(spaceCheck, Is.GreaterThanOrEqualTo(0));
        Assert.That(confirm, Is.GreaterThan(spaceCheck), "The space read happens before the one confirmation.");
        Assert.That(code, Does.Contain("{spaceSection}"), "And it is shown inside that confirmation.");
    }
}
