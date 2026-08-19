using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab rescue used to require an app-owned profile folder when the
/// profiles folder was blank. Name the folder. Prepare/music/managed-copy
/// leftovers stay swallowed by DescribeCaughtFailure and are not this gap.
/// </summary>
public class SaveRescueProfileFolderNoteHonestyTests
{
    [Test]
    public void ABlankProfileFolderNoteNamesTheFolderNotAnAppOwnedProfileFolder()
    {
        string keep = Path.Combine(Path.GetTempPath(), $"bea-rescue-keep-{Guid.NewGuid():N}");

        SafeCopySaveRescueResult result = SafeCopySaveRescueService.Rescue(
            new SafeCopySaveRescueRequest
            {
                ProfileRoot = "copy",
                DestinationDirectory = keep,
            },
            " ");

        string note = SaveRescuePageText.BuildOutcomeNote(result);

        Assert.That(result.Success, Is.False);
        Assert.That(note, Is.EqualTo(SafeCopySaveRescueService.ProfileFolderRequired));
        Assert.That(note, Is.EqualTo("A profile folder is required."));
        Assert.That(note, Does.Contain("profile folder"));
        Assert.That(note, Does.Not.Contain("app-owned"));
        Assert.That(note, Does.Not.Contain(keep));
        Assert.That(note, Does.Not.Contain(":\\"));
        Assert.That(Directory.Exists(keep), Is.False);
    }

    [Test]
    public void TheRescueNotePaintsTheProfileFolderSentence()
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
        Assert.That(helper, Does.Contain("return result.Message;"));
        Assert.That(rescue, Does.Contain("ProfileFolderRequired"));
        Assert.That(rescue, Does.Not.Contain("An app-owned profile folder is required."));
    }
}
