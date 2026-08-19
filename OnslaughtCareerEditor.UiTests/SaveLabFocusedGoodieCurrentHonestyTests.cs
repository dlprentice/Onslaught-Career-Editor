using System;
using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Save Lab focused Goodie used to let you pick a new state without saying
/// what the opened save already has. The current-state line paints that dword.
/// </summary>
public class SaveLabFocusedGoodieCurrentHonestyTests
{
    [Test]
    public void FocusedGoodieCurrentPaintsThisSaveNotAPath()
    {
        string painted = SaveLabPageText.DescribeFocusedGoodieCurrent(2, MissionScriptGoodieState.New);

        Assert.That(painted, Is.EqualTo("This save has Goodie 002 as New."));
        Assert.That(painted, Does.Not.Contain(":\\"));
        Assert.That(painted, Does.Not.Contain("verified"));
        Assert.That(painted, Does.Not.Contain("app-owned"));
        Assert.That(SaveLabPageText.FocusedGoodieCurrentUnreadable, Does.Not.Contain(":\\"));
        Assert.That(SaveLabPageText.FocusedGoodieCurrentUnreadable, Does.Not.Contain("exception"));
    }

    [Test]
    public void SaveLabBindsTheCurrentGoodieLineAndReadsTheDword()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "SavesPage.xaml.cs"));

        Assert.That(xaml, Does.Contain("AutomationProperties.AutomationId=\"SaveEditorFocusedGoodieCurrent\""));
        Assert.That(page, Does.Contain("BuildFocusedGoodieCurrentText"));
        Assert.That(page, Does.Contain("SaveLabPageText.DescribeFocusedGoodieCurrent"));
        Assert.That(page, Does.Contain("TryGetDisplayableStateBySaveIndex"));
        Assert.That(page, Does.Contain("EditorFocusedGoodieCurrentTextBlock.Text = BuildFocusedGoodieCurrentText"));
        Assert.That(xaml, Does.Contain("that copy's savegames folder"));
    }
}
