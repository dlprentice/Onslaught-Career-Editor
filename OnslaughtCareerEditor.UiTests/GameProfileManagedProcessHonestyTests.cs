using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// GameProfileManagedProcessRegistry used to say "profile root" when a
/// managed copy had no app-owned folder. Name the folder.
/// </summary>
public class GameProfileManagedProcessHonestyTests
{
    [Test]
    public void AManagedProcessRequiresTheProfileFolderNotTheRoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "GameProfileManagedProcessRegistry.cs"));

        Assert.That(source, Does.Not.Contain("requires an app-owned profile root."));
        Assert.That(source, Does.Not.Contain("A managed playable copied game folder process requires"));
        Assert.That(source, Does.Contain("ManagedCopyNeedsProfileFolder"));
        Assert.That(GameProfileManagedProcessRegistry.ManagedCopyNeedsProfileFolder,
            Is.EqualTo("A managed copy needs an app-owned profile folder."));
        Assert.That(GameProfileManagedProcessRegistry.ManagedCopyNeedsProfileFolder.ToLowerInvariant(),
            Does.Not.Contain("playable"));
    }

    [Test]
    public void AMissingManagedFolderNamesTheFolderNotADirectory()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "GameProfileManagedProcessRegistry.cs"));

        Assert.That(source, Does.Not.Contain("Managed playable copied game folder directory does not exist."));
        Assert.That(source, Does.Not.Contain("Managed playable copied game folder does not exist."));
        Assert.That(source, Does.Contain("CopyFolderMissing"));
        Assert.That(GameProfileManagedProcessRegistry.CopyFolderMissing,
            Is.EqualTo("That copy folder could not be found."));
        Assert.That(GameProfileManagedProcessRegistry.CopyFolderMissing.ToLowerInvariant(),
            Does.Not.Contain("path"));
    }

    [Test]
    public void AManagedProcessBeaExeNamesTheFolderNotARoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "GameProfileManagedProcessRegistry.cs"));

        Assert.That(source, Does.Not.Contain(
            "must point at BEA.exe under the app-owned playable copied game folder root."));
        Assert.That(source, Does.Not.Contain(
            "must point at BEA.exe under the app-owned playable copied game folder."));
        Assert.That(source, Does.Contain("CopyBeaMustStayInside"));
        Assert.That(GameProfileManagedProcessRegistry.CopyBeaMustStayInside,
            Is.EqualTo("That copy's BEA.exe must stay in the copy."));
        Assert.That(GameProfileManagedProcessRegistry.CopyBeaMustStayInside.ToLowerInvariant(),
            Does.Not.Contain("playable"));
    }

    [Test]
    public void ALeaseFolderMismatchNamesTheFolderNotARoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "GameProfileManagedProcessRegistry.cs"));

        Assert.That(source, Does.Contain("LeaseFolderMismatch"));
        Assert.That(source, Does.Not.Contain(
            "A managed playable copied game folder process root must match the registry lease root."));
        Assert.That(GameProfileManagedProcessRegistry.LeaseFolderMismatch,
            Is.EqualTo("A managed copy must stay in this registry's profile folder."));
        Assert.That(GameProfileManagedProcessRegistry.LeaseFolderMismatch.ToLowerInvariant(),
            Does.Not.Contain("root"));
        Assert.That(GameProfileManagedProcessRegistry.LeaseFolderMismatch.ToLowerInvariant(),
            Does.Not.Contain("path"));
    }

    [Test]
    public void AnUnregisteredCopyNamesTheCopyNotAPlayableProcess()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "GameProfileManagedProcessRegistry.cs"));

        Assert.That(source, Does.Contain("CopyProcessNotRegistered"));
        Assert.That(source, Does.Not.Contain(
            "Playable copied game folder process is not registered with this app session."));
        Assert.That(GameProfileManagedProcessRegistry.CopyProcessNotRegistered,
            Is.EqualTo("That copy is not registered with this session."));
        Assert.That(GameProfileManagedProcessRegistry.CopyProcessNotRegistered.ToLowerInvariant(),
            Does.Not.Contain("playable"));
    }
}
