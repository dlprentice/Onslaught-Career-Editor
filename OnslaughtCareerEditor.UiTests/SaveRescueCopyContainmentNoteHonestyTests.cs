using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab rescue used to say a copy must stay inside an app-owned
/// profile folder. Control-options and preflight throws of the same
/// sentence are swallowed by DescribeCaughtFailure / DescribeDeleteFailure
/// and are not this gap. Name the folder on the rescue note.
/// </summary>
public class SaveRescueCopyContainmentNoteHonestyTests
{
    [Test]
    public void ACopyOutsideTheFolderNoteNamesTheFolderNotAnAppOwnedProfileFolder()
    {
        string appFolder = Path.Combine(Path.GetTempPath(), $"bea-rescue-app-{Guid.NewGuid():N}");
        string copyFolder = Path.Combine(Path.GetTempPath(), $"bea-rescue-copy-{Guid.NewGuid():N}");
        string keep = Path.Combine(Path.GetTempPath(), $"bea-rescue-keep-{Guid.NewGuid():N}");
        Directory.CreateDirectory(appFolder);
        Directory.CreateDirectory(copyFolder);
        try
        {
            SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
                new SafeCopySaveRescueRequest
                {
                    ProfileRoot = copyFolder,
                    DestinationDirectory = keep,
                },
                appFolder);

            string note = SaveRescuePageText.BuildOutcomeNote(result);

            Assert.That(result.Success, Is.False);
            Assert.That(note, Is.EqualTo(SaveRescuePageText.CopyMustStayInside));
            Assert.That(note, Is.EqualTo("That copy must stay inside the profile folder."));
            Assert.That(note, Does.Contain("profile folder"));
            Assert.That(note, Does.Not.Contain("app-owned"));
            Assert.That(note, Does.Not.Contain(appFolder));
            Assert.That(note, Does.Not.Contain(copyFolder));
            Assert.That(note, Does.Not.Contain(keep));
            Assert.That(note, Does.Not.Contain(":\\"));
            Assert.That(Directory.Exists(keep), Is.False);
        }
        finally
        {
            Directory.Delete(appFolder, recursive: true);
            Directory.Delete(copyFolder, recursive: true);
            if (Directory.Exists(keep))
                Directory.Delete(keep, recursive: true);
        }
    }

    [Test]
    public void TheRescueNotePaintsTheStayInsideSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "SaveRescuePageText.cs"));
        string rescue = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "SafeCopySaveRescue.cs"));

        Assert.That(page, Does.Contain("SaveRescuePageText.BuildOutcomeNote"));
        Assert.That(helper, Does.Contain("CopyMustStayInside"));
        Assert.That(helper, Does.Contain("return result.Message;"));
        Assert.That(rescue, Does.Contain("CopyMustStayInside"));
        Assert.That(helper, Does.Not.Contain("That copy must stay inside the app-owned profile folder."));
    }
}
