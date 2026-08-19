using System.IO;
using NUnit.Framework;

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
        Assert.That(source, Does.Contain("requires an app-owned profile folder."));
    }
}
