using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Editor used to call the written save an app-owned output.
/// Name the written save and the output folder.
/// </summary>
public class SaveEditorOutputFolderHonestyTests
{
    [Test]
    public void RevealCopyNamesTheWrittenSaveNotAnAppOwnedOutput()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("app-owned output is missing"));
        Assert.That(page, Does.Not.Contain("app-owned output folder"));
        Assert.That(
            page,
            Does.Contain("The written-copy details changed or the written save is missing. Write the separate copy again before showing it."));
        Assert.That(
            page,
            Does.Contain("File Explorer could not be opened. The successful written save remains unchanged in the output folder; try Show again."));
    }
}
