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
        Assert.That(source, Does.Not.Contain("The selected output folder does not exist."));
        Assert.That(source, Does.Contain("That folder could not be found. Choose a folder again."));
        Assert.That(source, Does.Not.Contain("expected local path."));
        Assert.That(source, Does.Contain("expected local folder."));
        Assert.That(source, Does.Not.Contain("\"Input path\""));
        Assert.That(source, Does.Not.Contain("\"Output path\""));
        Assert.That(source, Does.Contain("\"Input file\""));
        Assert.That(source, Does.Contain("\"Output file\""));
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
        Assert.That(source, Does.Not.Contain("{label} is required."));
        Assert.That(source, Does.Not.Contain("{label} cannot use a Windows device location."));
        Assert.That(source, Does.Contain("FileOrFolderRequired"));
        Assert.That(source, Does.Contain("FileCannotUseDeviceLocation"));
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
        Assert.That(source, Does.Not.Contain("{label} resolves to a network location."));
        Assert.That(source, Does.Not.Contain("reserved DOS device name"));
        Assert.That(source, Does.Contain("FileCannotUseReservedDevice"));
    }

    [Test]
    public void AMissingProtectedInputDoesNotAttachTheFilePath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "FileMutationSafety.cs"));

        Assert.That(source, Does.Not.Contain(
            "throw new FileNotFoundException(\"Protected input file was not found.\", path);"));
        Assert.That(source, Does.Contain("That protected input file could not be found."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(\"That protected input file could not be found.\","));
        Assert.That(source, Does.Not.Contain("{label} does not exist."));
        Assert.That(source, Does.Contain("That folder could not be found."));
        Assert.That(source, Does.Not.Contain("cannot be a symbolic link, junction, or other reparse point."));
        Assert.That(source, Does.Not.Contain("cannot contain a symbolic link, junction, or other reparse point."));
        Assert.That(source, Does.Not.Contain("Committed output is a symbolic link, junction, or other reparse point."));
        Assert.That(source, Does.Contain("FileCannotUseLink"));
        Assert.That(source, Does.Contain("FolderCannotUseLink"));
        Assert.That(source, Does.Contain("FileCannotShareData"));
        Assert.That(source, Does.Contain("That file cannot use a shortcut or link."));
        Assert.That(source, Does.Contain("That folder cannot use a shortcut or link."));
        Assert.That(source, Does.Contain("That file cannot share its data with another file."));
        Assert.That(source, Does.Not.Contain("is hardlinked to another file"));
    }
}
