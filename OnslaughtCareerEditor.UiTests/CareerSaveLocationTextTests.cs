using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab used to show a path and nothing about where that career lives. The sentence
/// has to name the installed game, a playable copy, or a folder the player chose, and it
/// must never dump a full path or call a copy the original.
/// </summary>
public class CareerSaveLocationTextTests
{
    [Test]
    public void AnInstalledSaveSaysTheAppWillNotWriteBackThere()
    {
        string line = CareerSaveLocationText.Describe(CareerSaveLocationKind.InstalledGame, "career.bes");

        Assert.That(line, Does.Contain("installed game"));
        Assert.That(line.ToLowerInvariant(), Does.Contain("will not write back"));
        Assert.That(line, Does.Contain("career.bes"));
    }

    [Test]
    public void ASafeCopySaveIsNotCalledTheInstalledGame()
    {
        string line = CareerSaveLocationText.Describe(CareerSaveLocationKind.SafeCopy, "career.bes");

        Assert.That(line, Does.Contain("playable copy"));
        Assert.That(line.ToLowerInvariant(), Does.Not.Contain("installed game"));
        Assert.That(line.ToLowerInvariant(), Does.Contain("do not overwrite"));
    }

    [Test]
    public void AChosenFolderIsNamedAsThePlayersFolder()
    {
        string line = CareerSaveLocationText.Describe(CareerSaveLocationKind.ChosenFolder, "career.bes");

        Assert.That(line, Does.Contain("folder you chose"));
        Assert.That(line.ToLowerInvariant(), Does.Contain("new file"));
    }

    [Test]
    public void MissingAddsNothing()
    {
        Assert.That(CareerSaveLocationText.Describe(CareerSaveLocationKind.Missing, null), Is.Empty);
    }

    [Test]
    public void TheCopyNeverDumpsAFullPathOrInternalVocabulary()
    {
        string[] banned =
        {
            "receipt", "manifest", "provenance", "byte-verified", "specimen",
            "catalog", "preflight", "profile root", "proof level", "dword",
            @":\", "/",
        };

        foreach (CareerSaveLocationKind kind in Enum.GetValues<CareerSaveLocationKind>())
        {
            string all = CareerSaveLocationText.Describe(kind, "career.bes").ToLowerInvariant();
            foreach (string word in banned)
            {
                Assert.That(all, Does.Not.Contain(word.ToLowerInvariant()), $"Location copy should not say '{word}'.");
            }
        }
    }

    [Test]
    public void SaveLabActuallyShowsTheLocationLine()
    {
        string root = FindRepoRoot();
        string xaml = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml"));
        string code = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "SavesPage.xaml.cs"));

        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"SaveEditorInputLocation\""));
        Assert.That(code, Does.Contain("CareerSaveLocation.Classify"));
        Assert.That(code, Does.Contain("CareerSaveLocationText.Describe"));
    }

    private static string FindRepoRoot()
    {
        DirectoryInfo? directory = new(TestContext.CurrentContext.TestDirectory);
        while (directory is not null && !File.Exists(Path.Combine(directory.FullName, "package.json")))
            directory = directory.Parent;
        Assert.That(directory, Is.Not.Null, "Could not find the repository root.");
        return directory!.FullName;
    }
}
