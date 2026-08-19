using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The kill-seed summary used to say only that no save is loaded.
/// Name the next step, the same way an unread advanced read already does.
/// </summary>
public class KillSeedSummaryHonestyTests
{
    [Test]
    public void AnEmptyKillSummaryNamesTheNextStep()
    {
        string empty = SaveEditorAdvancedService.BuildKillSeedSummary(Array.Empty<SaveCategoryKillRow>());

        Assert.That(empty, Does.StartWith("Choose a career save first."));
        Assert.That(empty, Does.Contain("not a cumulative score"));
        Assert.That(empty, Does.Not.Contain("No save is loaded"));
        Assert.That(empty.ToLowerInvariant(), Does.Not.Contain("path"));
    }
}
