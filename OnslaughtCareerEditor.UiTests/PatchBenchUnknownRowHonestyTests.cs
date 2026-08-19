using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Verify/apply used to interpolate the catalog key into Last operation
/// (<c>Unknown or hidden patch row is not selectable: {unknownKey}</c>).
/// That is an internal id, not something a player should see.
/// </summary>
public class PatchBenchUnknownRowHonestyTests
{
    [Test]
    public void AnUnknownRowNamesTheRefusalWithoutTheCatalogKey()
    {
        string? sentence = BinaryPatchPlanBuilder.ValidateVisibleSelection(new[] { "not_a_patch_row" });

        Assert.That(sentence, Is.Not.Null.And.EqualTo(BinaryPatchPlanBuilder.PatchRowNotSelectable));
        Assert.That(sentence, Does.Contain("not selectable"));
        Assert.That(sentence, Does.Not.Contain("not_a_patch_row"));
        Assert.That(sentence, Does.Not.Contain(":\\"));
        Assert.That(sentence, Does.Not.Contain("/"));
    }
}
