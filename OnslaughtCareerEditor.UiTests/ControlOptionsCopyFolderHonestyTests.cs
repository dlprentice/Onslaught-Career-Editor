using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Control-options validation used to say "copy root". Name the folder.
/// </summary>
public class ControlOptionsCopyFolderHonestyTests
{
    [Test]
    public void AMissingCopyFolderNamesTheFolderNotARoot()
    {
        string sentence = GameProfileControlOptionsService.CopyFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy folder could not be found."));
        Assert.That(sentence, Does.Contain("copy folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void AMissingProfileFolderNamesTheFolderNotARoot()
    {
        string sentence = GameProfileControlOptionsService.ProfileFolderRequired;

        Assert.That(sentence, Is.EqualTo("An app-owned profile folder is required."));
        Assert.That(sentence, Does.Contain("profile folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("root"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void TheControlOptionsServiceDropsTheRootSentences()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileControlOptionsService.cs"));

        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(source, Does.Contain("ProfileFolderRequired"));
        Assert.That(source, Does.Not.Contain("An app-owned safe game copy root is required."));
        Assert.That(source, Does.Not.Contain("Safe game copy root does not exist."));
        Assert.That(source, Does.Not.Contain("app-owned safe game copy root"));
        Assert.That(source, Does.Not.Contain("safe game copy root"));
        Assert.That(source, Does.Contain("app-owned safe game copy folder"));
        Assert.That(source, Does.Contain("Safe-copy control options require a generated profile under the app-owned safe game copy folder."));
    }

    [Test]
    public void ApplyingOptionsOnAMissingCopyDoesNotDumpARoot()
    {
        InvalidOperationException missingProfile = Assert.Throws<InvalidOperationException>(() =>
            GameProfileControlOptionsService.ApplyToSafeCopy(new GameProfileControlOptionsRequest(
                ProfileRoot: "copy",
                AppOwnedProfilesRoot: " ",
                ScreenShapeOverride: 1u)));

        DirectoryNotFoundException missingCopy = Assert.Throws<DirectoryNotFoundException>(() =>
            GameProfileControlOptionsService.ApplyToSafeCopy(new GameProfileControlOptionsRequest(
                ProfileRoot: " ",
                AppOwnedProfilesRoot: Path.GetTempPath(),
                ScreenShapeOverride: 1u)));

        Assert.That(missingProfile.Message, Is.EqualTo(GameProfileControlOptionsService.ProfileFolderRequired));
        Assert.That(missingCopy.Message, Is.EqualTo(GameProfileControlOptionsService.CopyFolderMissing));
        Assert.That(missingCopy.Message, Does.Not.Contain(Path.GetTempPath()));
        Assert.That(missingCopy.Message, Does.Not.Contain(":\\"));
    }
}
