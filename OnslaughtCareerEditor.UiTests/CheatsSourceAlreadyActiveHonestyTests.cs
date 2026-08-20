using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Cheats used to name the source save without saying which offered cheats
/// that name already switches on. Those live in the file name, not the bytes,
/// so a new name drops them unless they are ticked.
/// </summary>
public class CheatsSourceAlreadyActiveHonestyTests
{
    [Test]
    public void SourceCheatsPaintsThisSaveNotAPath()
    {
        string god = CheatsPageText.DescribeSourceCheats(Path.Combine("C:", "saves", "Maladim.bes"));
        string none = CheatsPageText.DescribeSourceCheats("career.bes");
        string both = CheatsPageText.DescribeSourceCheats("MALLOYTURKEY.bes");

        Assert.That(
            god,
            Is.EqualTo("This save already switches on God mode. Tick that cheat if you want the new name to keep it."));
        Assert.That(none, Is.EqualTo(CheatsPageText.SourceCheatsNone));
        Assert.That(
            both,
            Is.EqualTo("This save already switches on All goodies and All levels. Tick those cheats if you want the new name to keep them."));
        Assert.That(CheatsPageText.DescribeSourceCheats(null), Is.Empty);
        AssertHonesty(god);
        AssertHonesty(none);
        AssertHonesty(both);
        AssertHonesty(CheatsPageText.SourceCheatsNone);
        Assert.That(god, Does.Not.Contain("C:"));
        Assert.That(god, Does.Not.Contain("Maladim.bes"));
    }

    [Test]
    public void CheatsBindsTheCurrentCheatLineAndReadsTheSourceName()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "CheatsPage.xaml"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "CheatsPage.xaml.cs"));

        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"CheatsSourceAlreadyActive\""));
        Assert.That(page, Does.Contain("SourceCheatsTextBlock.Text = CheatsPageText.DescribeSourceCheats(_sourceSavePath)"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "CheatsPageText.cs"));
        Assert.That(helper, Does.Contain("CheatSaveNameComposer.ActiveCheatsIn"));
        Assert.That(xaml, Does.Not.Contain("CDB"));
        Assert.That(xaml, Does.Not.Contain("sidecar"));
    }

    [Test]
    public void TheSourceLocationSentenceWasNotRemapped()
    {
        string summary = CheatsPageText.BuildSourceSummary(Path.Combine("C:", "saves", "Maladim.bes"));

        Assert.That(summary, Does.StartWith("Starting from Maladim.bes"));
        Assert.That(summary, Does.Contain("not changed"));
        Assert.That(summary, Does.Not.Contain("already switches"));
        Assert.That(summary, Does.Not.Contain("C:\\saves"));
    }

    private static void AssertHonesty(string painted)
    {
        Assert.That(painted, Does.Not.Contain(@":\"));
        Assert.That(painted, Does.Not.Contain("verified"));
        Assert.That(painted, Does.Not.Contain("app-owned"));
        Assert.That(painted, Does.Not.Contain("exception"));
        Assert.That(painted, Does.Not.Contain("sidecar"));
        Assert.That(painted, Does.Not.Contain("CDB"));
    }
}
