using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Launch/stop used to interpolate the missing copy folder. Name the folder.
/// </summary>
public class PatchBenchCopyFolderHonestyTests
{
    [Test]
    public void AMissingCopyFolderNamesTheFolderNotAPath()
    {
        string sentence = GameProfileRuntimeService.CopyFolderMissing;

        Assert.That(sentence, Is.EqualTo("That copy folder could not be found."));
        Assert.That(sentence, Does.Contain("copy folder"));
        Assert.That(sentence.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }

    [Test]
    public void TheRuntimeServiceDropsTheProfileRootInterpolation()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileRuntimeService.cs"));

        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder root does not exist:"));
        Assert.That(source, Does.Not.Contain("{resolvedProfileRoot}"));
        Assert.That(source, Does.Not.Contain("launch did not return a valid process id."));
        Assert.That(source, Does.Not.Contain("launch did not start a process."));
        Assert.That(source, Does.Not.Contain("refuses reparse points in {label}."));
        Assert.That(source, Does.Contain("CopyDidNotStart"));
        Assert.That(source, Does.Contain("CopyCannotUseLink"));
        Assert.That(GameProfileRuntimeService.CopyDidNotStart, Is.EqualTo("That copy did not start."));
        Assert.That(GameProfileRuntimeService.CopyCannotUseLink,
            Is.EqualTo("That copy cannot use a shortcut or link."));
        Assert.That(GameProfileRuntimeService.CopyDidNotStart.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(source, Does.Contain("CopiedBeaMissing"));
        Assert.That(source, Does.Contain("CopyManifestMissing"));
        Assert.That(source, Does.Not.Contain("Managed playable copied game folder requires BEA.exe."));
        Assert.That(source, Does.Not.Contain("Managed playable copied game folder requires its generated manifest."));
        Assert.That(GameProfilePreflightService.CopiedBeaMissing,
            Is.EqualTo("That copy is missing BEA.exe."));
        Assert.That(GameProfilePreflightService.CopyManifestMissing,
            Is.EqualTo("That copy is missing onslaught-profile-manifest.json."));
    }
}
