using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods keep-careers used to pass the rescue stay-inside
/// refusal through DescribeRemovalOutcome and paint "app-owned profile
/// folder" on the safe-copy manager note. Name the folder. The delete
/// button's first Inventory catch is CheckFailure and is not this gap.
/// </summary>
public class SafeCopyManagerCopyContainmentNoteHonestyTests
{
    [Test]
    public void ACopyOutsideTheFolderNoteNamesTheFolderNotAnAppOwnedProfileFolder()
    {
        string appFolder = Path.Combine(Path.GetTempPath(), $"bea-manager-app-{Guid.NewGuid():N}");
        string copyFolder = Path.Combine(Path.GetTempPath(), $"bea-manager-copy-{Guid.NewGuid():N}");
        string keep = Path.Combine(Path.GetTempPath(), $"bea-manager-keep-{Guid.NewGuid():N}");
        Directory.CreateDirectory(appFolder);
        Directory.CreateDirectory(copyFolder);
        try
        {
            SafeCopyRemovalResult removal = SafeCopySaveRescueService.RescueThenDelete(
                copyFolder,
                appFolder,
                keep);

            string note = SafeCopyManagerText.DescribeRemovalOutcome(removal, "trainer-proof", "700 MB");

            Assert.That(removal.Success, Is.False);
            Assert.That(removal.Message, Is.EqualTo(SafeCopySaveRescueService.CopyMustStayInside));
            Assert.That(note, Is.EqualTo(SafeCopyManagerText.CopyMustStayInside));
            Assert.That(note, Is.EqualTo("That copy must stay inside the profile folder."));
            Assert.That(note, Does.Contain("profile folder"));
            Assert.That(note, Does.Not.Contain("app-owned"));
            Assert.That(note, Does.Not.Contain(appFolder));
            Assert.That(note, Does.Not.Contain(copyFolder));
            Assert.That(note, Does.Not.Contain(keep));
            Assert.That(note, Does.Not.Contain(":\\"));
            Assert.That(Directory.Exists(copyFolder), Is.True);
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
    public void TheManagerNotePaintsTheStayInsideSentence()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "SafeCopyManagerText.cs"));
        string rescue = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "SafeCopySaveRescue.cs"));

        Assert.That(page, Does.Contain("SafeCopyManagerText.DescribeRemovalOutcome"));
        Assert.That(page, Does.Contain("ShowSafeCopyManagerNote"));
        Assert.That(helper, Does.Contain("CopyMustStayInside"));
        Assert.That(helper, Does.Contain("return removal.Message;"));
        Assert.That(rescue, Does.Contain("CopyMustStayInside"));
        Assert.That(helper, Does.Not.Contain("That copy must stay inside the app-owned profile folder."));
    }
}
