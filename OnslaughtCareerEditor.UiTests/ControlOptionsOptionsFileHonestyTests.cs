using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A missing defaultoptions.bea used to attach the full options path
/// to FileNotFoundException. Name the file, not a path.
/// </summary>
public class ControlOptionsOptionsFileHonestyTests
{
    [Test]
    public void AMissingOptionsFileDoesNotAttachTheFilePath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfileControlOptionsService.cs"));

        Assert.That(source, Does.Not.Contain(
            "throw new FileNotFoundException(\"Safe game copy is missing defaultoptions.bea.\", optionsPath);"));
        Assert.That(source, Does.Contain("That copy is missing defaultoptions.bea."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(\"That copy is missing defaultoptions.bea.\","));
    }
}
