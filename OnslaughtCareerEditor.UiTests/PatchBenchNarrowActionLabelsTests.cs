using System.Xml.Linq;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

[TestFixture]
public sealed class PatchBenchNarrowActionLabelsTests
{
    [Test]
    public void CompatibilityActions_UseReadableEqualHeightWrappingLabels()
    {
        XDocument document = XDocument.Parse(ReadRepoFile(
            "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"));

        XElement resetButton = FindByAutomationId(document, "PatchBenchWindowedPresetButton");
        XElement clearButton = FindByAutomationId(document, "PatchBenchClearSelectionButton");

        Assert.Multiple(() =>
        {
            AssertButton(resetButton, "Reset to Compatibility Copy", "Select Compatibility Copy profile", "WindowedPresetButton_Click");
            AssertButton(clearButton, "Clear optional mods", "Clear optional mod rows; safe copies still include required compatibility", "ClearSelectionButton_Click");
            Assert.That((string?)resetButton.Attribute("MinHeight"), Is.EqualTo("56"));
            Assert.That((string?)clearButton.Attribute("MinHeight"), Is.EqualTo("56"));
        });
    }

    private static void AssertButton(XElement button, string label, string accessibleName, string handler)
    {
        XElement content = button.Elements().Single(element => element.Name.LocalName == "TextBlock");
        Assert.Multiple(() =>
        {
            Assert.That((string?)button.Attribute("AutomationProperties.Name"), Is.EqualTo(accessibleName));
            Assert.That((string?)button.Attribute("Click"), Is.EqualTo(handler));
            Assert.That((string?)content.Attribute("Text"), Is.EqualTo(label));
            Assert.That((string?)content.Attribute("TextWrapping"), Is.EqualTo("WrapWholeWords"));
            Assert.That((string?)content.Attribute("TextAlignment"), Is.EqualTo("Center"));
            Assert.That((string?)content.Attribute("HorizontalAlignment"), Is.EqualTo("Center"));
        });
    }

    private static XElement FindByAutomationId(XContainer document, string automationId) =>
        document.Descendants().Single(element =>
            string.Equals((string?)element.Attribute("AutomationProperties.AutomationId"), automationId, StringComparison.Ordinal));

    private static string ReadRepoFile(params string[] parts)
    {
        string path = Path.Combine(parts.Prepend(TestFixturePaths.RepoRoot).ToArray());
        Assert.That(File.Exists(path), Is.True, $"Missing expected repo file: {path}");
        return File.ReadAllText(path);
    }
}
