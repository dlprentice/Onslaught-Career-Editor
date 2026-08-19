using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Rescue used to interpolate the missing copy folder. Name the folder.
/// </summary>
public class SaveRescueCopyFolderHonestyTests
{
    [Test]
    public void AMissingCopyFolderNamesTheFolderNotAPath()
    {
        string sentence = SafeCopySaveRescueService.CopyFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy folder could not be found."));
        Assert.That(sentence, Does.Contain("copy folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void TheRescueServiceDropsTheProfileRootInterpolation()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "SafeCopySaveRescue.cs"));

        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder does not exist:"));
        Assert.That(source, Does.Not.Contain("Not an app-generated playable copied game folder:"));
        Assert.That(source, Does.Contain("CopyManifestMissing"));
        Assert.That(source, Does.Contain("CopyRequired"));
        Assert.That(source, Does.Not.Contain("A playable copied game folder is required."));
        Assert.That(SafeCopySaveRescueService.CopyRequired,
            Is.EqualTo("A copy is required."));
        Assert.That(source, Does.Not.Contain("{profileRoot}"));
        Assert.That(source, Does.Not.Contain("\"Destination path\""));
        Assert.That(source, Does.Contain("\"Destination file\""));
    }
}
