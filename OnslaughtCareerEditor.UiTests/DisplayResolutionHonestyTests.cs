using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A refused resolution used to echo the typed value and say "copied game".
/// Name the copy. Keep the typed value off the sentence.
/// </summary>
public class DisplayResolutionHonestyTests
{
    [Test]
    public void ARefusedResolutionNamesTheCopyNotTheTypedValue()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "DisplayResolutionPreset.cs"));

        Assert.That(source, Does.Contain("ResolutionNotASize"));
        Assert.That(source, Does.Contain("ResolutionOutOfRange"));
        Assert.That(source, Does.Not.Contain("'{value}' is not a resolution"));
        Assert.That(source, Does.Not.Contain("The copied game accepts widths"));
        Assert.That(DisplayResolutionPreset.ResolutionNotASize,
            Is.EqualTo("That is not a resolution. Use WIDTHxHEIGHT, for example 1920x1080."));
        Assert.That(DisplayResolutionPreset.ResolutionNotASize, Does.Not.Contain("{value}"));
        Assert.That(DisplayResolutionPreset.ResolutionOutOfRange, Does.Contain("copy"));
        Assert.That(DisplayResolutionPreset.ResolutionOutOfRange.ToLowerInvariant(),
            Does.Not.Contain("copied game"));
    }
}
