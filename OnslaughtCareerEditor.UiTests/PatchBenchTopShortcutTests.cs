using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The three shortcuts at the top of Patch Bench.
///
/// They exist because the page is long and the three things most people came to do sit far down
/// it. The page says so in as many words: "These shortcuts use the same guarded safe-copy
/// workflow below." That sentence is a promise, and until now nothing checked it - all three
/// buttons could have been repointed at a different handler, or at nothing, and every test in the
/// repository would still have passed.
///
/// This was found while looking for dead code to delete. Two of the three were named by no test
/// at all, which is easy to read as "unused" - they are not. They are working controls a person
/// can click, wired to the same handlers as the main workflow. The thing that was missing was
/// never the buttons; it was this.
///
/// Asserting on markup is the weaker kind of test and is used deliberately here: a shortcut
/// sharing a handler with the control it shortcuts to has no expression in behaviour that a
/// headless test could reach, and the failure it guards against is silent.
/// </summary>
[TestFixture]
public class PatchBenchTopShortcutTests
{
    private static string PagePath => Path.Combine(
        TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml");

    private static XDocument Page => XDocument.Load(PagePath);

    /// <summary>Each shortcut, and the handler the main workflow below uses for the same job.</summary>
    private static readonly (string AutomationId, string Handler)[] Shortcuts =
    [
        ("PatchBenchTopUseGameFolderButton", "UseGameDirButton_Click"),
        ("PatchBenchTopCreateSafeCopyButton", "PrepareCopiedProfileButton_Click"),
        ("PatchBenchTopPlaySafeCopyButton", "LaunchCopiedProfileButton_Click"),
    ];

    [Test]
    public void EveryTopShortcutRunsTheSameHandlerAsTheWorkflowBelow()
    {
        XDocument page = Page;

        foreach ((string automationId, string handler) in Shortcuts)
        {
            XElement? button = FindByAutomationId(page, automationId);
            Assert.That(button, Is.Not.Null, $"{automationId} is gone from the page.");
            Assert.That(
                (string?)button!.Attribute("Click"),
                Is.EqualTo(handler),
                $"{automationId} promises the workflow below and must call its handler.");

            int usesOfHandler = page.Descendants()
                .Count(element => (string?)element.Attribute("Click") == handler);
            Assert.That(
                usesOfHandler,
                Is.GreaterThan(1),
                $"{handler} is only reachable from the shortcut, so it shortcuts to nothing.");
        }
    }

    [Test]
    public void TheShortcutRowStillSaysWhereTheShortcutsGo()
    {
        // If the sentence goes, three buttons that look like a second way to do the job become
        // three buttons that look like a different job.
        Assert.That(
            File.ReadAllText(PagePath),
            Does.Contain("These shortcuts use the same guarded safe-copy workflow below"),
            "The row explains itself, or it is three unexplained buttons above the real thing.");
    }

    [Test]
    public void EveryTopShortcutIsNamedForAScreenReader()
    {
        XDocument page = Page;

        foreach ((string automationId, _) in Shortcuts)
        {
            XElement button = FindByAutomationId(page, automationId)!;
            string? name = button.Attributes()
                .FirstOrDefault(attribute => attribute.Name.LocalName == "AutomationProperties.Name")
                ?.Value;

            Assert.That(
                name,
                Is.Not.Null.And.Not.Empty,
                $"{automationId} needs an AutomationProperties.Name: three buttons whose labels "
                    + "are all verbs are ambiguous read aloud.");
        }
    }

    /// <summary>
    /// The attached property arrives as one dotted attribute name -
    /// <c>AutomationProperties.AutomationId</c> - not as a namespaced <c>AutomationId</c>. Looking
    /// for the short name finds nothing and reads as "the button is gone", which is a confusing
    /// way for a test to be wrong about markup that is right there.
    /// </summary>
    private static XElement? FindByAutomationId(XDocument page, string automationId)
    {
        return page.Descendants().FirstOrDefault(element =>
            element.Attributes().Any(attribute =>
                attribute.Name.LocalName == "AutomationProperties.AutomationId" &&
                attribute.Value == automationId));
    }
}
