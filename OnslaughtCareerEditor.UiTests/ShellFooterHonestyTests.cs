using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The shell footer already named the folder. The tooltip still painted the
/// full install path. Both have to stay on the last segment.
/// </summary>
public class ShellFooterHonestyTests
{
    [Test]
    public void AReadyFolderIsNamedByItsLeafNotThePath()
    {
        string path = @"C:\Games\Steam\steamapps\common\Battle Engine Aquila";
        string label = ShellFooterText.BuildFolderLabel(path);
        string tip = ShellFooterText.DescribeReadyTooltip(path);

        Assert.That(label, Is.EqualTo("Battle Engine Aquila"));
        Assert.That(tip, Does.Contain("Battle Engine Aquila"));
        Assert.That(tip, Does.Not.Contain(path));
        Assert.That(tip, Does.Not.Contain(@":\"));
        Assert.That(tip, Does.Not.Contain("Games"));
        Assert.That(
            ShellFooterText.BuildFolderLabel(@"C:\Games\Battle Engine Aquila\"),
            Is.EqualTo("Battle Engine Aquila"));
    }

    [Test]
    public void AMissingFolderFallsBackWithoutPrintingAPath()
    {
        Assert.That(ShellFooterText.BuildFolderLabel("   "), Is.EqualTo("Not set"));
        Assert.That(ShellFooterText.BuildFolderLabel(null), Is.EqualTo("Not set"));
        Assert.That(ShellFooterText.DescribeReadyTooltip(null), Does.Not.Contain(@":\"));
        Assert.That(ShellFooterText.DescribeReadyTooltip(null), Does.Not.Contain("/"));
    }

    [Test]
    public void TheFooterUsesTheSharedLeafAndDoesNotPaintThePath()
    {
        string code = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "MainWindow.xaml.cs"));

        Assert.That(code, Does.Contain("ShellFooterText.BuildFolderLabel"));
        Assert.That(code, Does.Contain("ShellFooterText.DescribeReadyTooltip"));
        Assert.That(code, Does.Contain("? ShellFooterText.DescribeReadyTooltip(gameDir)"));
        Assert.That(code, Does.Not.Contain("                    ? gameDir"));
        Assert.That(code, Does.Not.Contain("private static string BuildGameDirectoryLabel"));
    }
}
