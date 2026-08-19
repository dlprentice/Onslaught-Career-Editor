using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// FileMutationSafety used to say "output paths" when a write would land
/// inside a Battle Engine Aquila game folder, and two later refusals still
/// named a path. Name the file or folder.
/// </summary>
public class FileMutationSafetyHonestyTests
{
    [Test]
    public void AGameFolderWriteNamesTheFilesNotThePaths()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain("Output paths inside a Battle Engine Aquila game folder"));
        Assert.That(source, Does.Contain("Output files inside a Battle Engine Aquila game folder are blocked."));
        Assert.That(source, Does.Contain("Choose the app-owned patched-output folder or another non-game folder."));
    }

    [Test]
    public void AFolderOutputNamesTheFileNotAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain("The selected output path is a directory."));
        Assert.That(source, Does.Contain("The selected output file is a folder."));
        Assert.That(source, Does.Not.Contain("Output path must remain inside the verified app-owned profile root."));
        Assert.That(source, Does.Contain("The output file must remain inside the verified app-owned profile folder."));
    }

    [Test]
    public void ADeviceLocationRefusalDoesNotSayPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain("cannot use a Windows device path."));
        Assert.That(source, Does.Not.Contain("cannot use a drive-relative path."));
        Assert.That(source, Does.Not.Contain("cannot use a UNC or network path."));
        Assert.That(source, Does.Not.Contain("\"Protected input path\""));
        Assert.That(source, Does.Contain("cannot use a Windows device location."));
        Assert.That(source, Does.Contain("cannot use a drive-relative location."));
        Assert.That(source, Does.Contain("cannot use a UNC or network location."));
        Assert.That(source, Does.Contain("\"Protected input file\""));
    }

    [Test]
    public void AResolvedNetworkLocationDoesNotSayPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain("resolves to a network path."));
        Assert.That(source, Does.Not.Contain("does not resolve to a local DOS drive path."));
        Assert.That(source, Does.Contain("resolves to a network location."));
        Assert.That(source, Does.Contain("does not resolve to a local drive."));
    }
}
