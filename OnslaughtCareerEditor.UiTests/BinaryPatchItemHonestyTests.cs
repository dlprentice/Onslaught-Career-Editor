using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// An unknown patch row used to say "The selected bytes". Name the
/// bytes, not the selection.
/// </summary>
public class BinaryPatchItemHonestyTests
{
    [Test]
    public void AnUnknownRowNamesTheBytesNotTheSelection()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Models",
            "BinaryPatchItemModel.cs"));

        Assert.That(source, Does.Not.Contain("The selected bytes change only the copied executable."));
        Assert.That(source, Does.Contain("Those bytes change only the copied executable."));
    }
}
