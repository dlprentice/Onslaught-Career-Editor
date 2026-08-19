using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Looking up a missing safe-copy profile used to interpolate the catalog id
/// (<c>Unknown safe-copy profile preset: {profileId}</c>). Name the refusal.
/// </summary>
public class PatchBenchUnknownProfileHonestyTests
{
    [Test]
    public void AnUnknownProfileNamesTheRefusalWithoutTheCatalogId()
    {
        InvalidOperationException error = Assert.Throws<InvalidOperationException>(
            () => BinaryPatchPlanBuilder.GetSafeCopyProfilePreset("not_a_profile"));

        Assert.That(error.Message, Is.EqualTo(BinaryPatchPlanBuilder.ProfilePresetUnknown));
        Assert.That(error.Message, Is.EqualTo("That copy profile is not available."));
        Assert.That(error.Message, Does.Not.Contain("not_a_profile"));
        Assert.That(error.Message, Does.Not.Contain("preset"));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(error.Message, Does.Not.Contain(":\\"));
        Assert.That(error.Message, Does.Not.Contain("/"));
    }

    [Test]
    public void ThePlanBuilderDropsTheProfileIdInterpolation()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchPlanBuilder.cs"));

        Assert.That(source, Does.Contain("ProfilePresetUnknown"));
        Assert.That(source, Does.Contain("ProfilePresetNotReady"));
        Assert.That(source, Does.Not.Contain("Unknown safe-copy profile preset:"));
        Assert.That(source, Does.Not.Contain("{profileId}"));
        Assert.That(source, Does.Not.Contain("cannot produce patch keys"));
        Assert.That(source, Does.Not.Contain("{preset.DisplayName}"));
        Assert.That(BinaryPatchPlanBuilder.ProfilePresetNotReady,
            Is.EqualTo("That copy profile cannot be used yet."));
        Assert.That(BinaryPatchPlanBuilder.ProfilePresetNotReady.ToLowerInvariant(),
            Does.Not.Contain("key"));
        Assert.That(BinaryPatchPlanBuilder.ProfilePresetNotReady.ToLowerInvariant(),
            Does.Not.Contain("path"));
    }
}
