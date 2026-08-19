using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Control-options validation used to say "copy root", then a generated
/// profile under the app-owned safe game copy folder. Name the copy, and
/// reuse the stay-inside sentence.
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
        Assert.That(source, Does.Contain("CopyMustStayInside"));
        Assert.That(source, Does.Not.Contain("An app-owned safe game copy root is required."));
        Assert.That(source, Does.Not.Contain("Safe game copy root does not exist."));
        Assert.That(source, Does.Not.Contain("app-owned safe game copy root"));
        Assert.That(source, Does.Not.Contain("safe game copy root"));
        Assert.That(source, Does.Not.Contain(
            "Safe-copy control options require a generated profile under the app-owned safe game copy folder."));
        Assert.That(GameProfileControlOptionsService.CopyMustStayInside,
            Is.EqualTo("That copy must stay inside the app-owned profile folder."));
        Assert.That(GameProfileControlOptionsService.CopyMustStayInside,
            Is.EqualTo(GameProfilePreflightService.CopyMustStayInside));
        Assert.That(GameProfileControlOptionsService.CopyMustStayInside.ToLowerInvariant(),
            Does.Not.Contain("generated"));
        Assert.That(GameProfileControlOptionsService.CopyMustStayInside.ToLowerInvariant(),
            Does.Not.Contain("safe game copy"));
    }

    [Test]
    public void ACopyOutsideTheFolderNamesTheCopyNotAGeneratedProfile()
    {
        string appFolder = Path.Combine(Path.GetTempPath(), $"bea-opt-app-{Guid.NewGuid():N}");
        string copyFolder = Path.Combine(Path.GetTempPath(), $"bea-opt-copy-{Guid.NewGuid():N}");
        Directory.CreateDirectory(appFolder);
        Directory.CreateDirectory(copyFolder);
        try
        {
            InvalidOperationException error = Assert.Throws<InvalidOperationException>(() =>
                GameProfileControlOptionsService.ApplyToSafeCopy(new GameProfileControlOptionsRequest(
                    ProfileRoot: copyFolder,
                    AppOwnedProfilesRoot: appFolder,
                    ScreenShapeOverride: 1u)));

            Assert.That(error.Message, Is.EqualTo(GameProfileControlOptionsService.CopyMustStayInside));
            Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.CopyMustStayInside));
            Assert.That(error.Message, Does.Not.Contain("generated profile"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(error.Message, Does.Not.Contain(appFolder));
            Assert.That(error.Message, Does.Not.Contain(copyFolder));
            Assert.That(error.Message, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(appFolder, recursive: true);
            Directory.Delete(copyFolder, recursive: true);
        }
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

    [Test]
    public void ASharedOptionsFileIsNamedWithoutCallingItAHardlink()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileControlOptionsService.cs"));

        Assert.That(source, Does.Not.Contain("is hardlinked to another file"));
        Assert.That(source, Does.Contain("FileCannotShareData"));
        Assert.That(GameProfileControlOptionsService.FileCannotShareData,
            Is.EqualTo("That file cannot share its data with another file."));
        Assert.That(source, Does.Not.Contain("Could not inspect hardlink count"));
        Assert.That(source, Does.Not.Contain("Win32 error:"));
        Assert.That(source, Does.Contain("FileCouldNotBeInspected"));
    }
}
