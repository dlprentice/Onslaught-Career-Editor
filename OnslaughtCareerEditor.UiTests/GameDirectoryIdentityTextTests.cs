using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;
using OnslaughtCareerEditor.WinUI.Helpers;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Settings used to say "valid game directory" as soon as BEA.exe and data were present.
/// That sentence is still true as a layout check, but it hid the case this app cares about:
/// the executable is already not the known Steam retail file, and a copy will carry that.
/// </summary>
public class GameDirectoryIdentityTextTests
{
    [Test]
    public void AKnownRetailFileIsNamedAsTheKnownSteamFile()
    {
        string line = GameDirectoryIdentityText.ForSettings(RetailExecutableIdentity.KnownCleanRetail);

        Assert.That(line, Does.Contain("known Steam retail"));
        Assert.That(line, Does.Contain("Copies start from that original"));
        Assert.That(GameDirectoryIdentityText.IsWarning(RetailExecutableIdentity.KnownCleanRetail), Is.False);
    }

    [Test]
    public void AChangedFileRefusesToBeCalledAnOriginal()
    {
        string line = GameDirectoryIdentityText.ForSettings(RetailExecutableIdentity.DifferentFromKnownRetail);

        Assert.That(line, Does.Contain("not the known Steam retail file"));
        Assert.That(line, Does.Contain("will carry those changes"));
        Assert.That(line.ToLowerInvariant(), Does.Contain("do not treat this file as an original"));
        Assert.That(GameDirectoryIdentityText.IsWarning(RetailExecutableIdentity.DifferentFromKnownRetail), Is.True);
    }

    [Test]
    public void AnUnreadableFileIsNotCalledChanged()
    {
        string line = GameDirectoryIdentityText.ForSettings(RetailExecutableIdentity.Unreadable);

        Assert.That(line, Does.Contain("could not read BEA.exe"));
        Assert.That(line.ToLowerInvariant(), Does.Not.Contain("already"));
        Assert.That(line.ToLowerInvariant(), Does.Not.Contain("changed"));
        Assert.That(GameDirectoryIdentityText.IsWarning(RetailExecutableIdentity.Unreadable), Is.True);
    }

    [Test]
    public void MissingIdentityAddsNothingOnTopOfTheLayoutStatus()
    {
        Assert.That(GameDirectoryIdentityText.ForSettings(RetailExecutableIdentity.Missing), Is.Empty);
        Assert.That(GameDirectoryIdentityText.IsWarning(RetailExecutableIdentity.Missing), Is.False);
    }

    [Test]
    public void HomeKeepsTheUsualGuidanceUntilTheFileIsNotRetail()
    {
        const string usual =
            "Windowed & Mods creates a safe game copy, patches only that copy, and plays only that copy without changing the Steam/game install.";

        Assert.That(
            GameDirectoryIdentityText.ForHomeGuidance(RetailExecutableIdentity.KnownCleanRetail, usual),
            Is.EqualTo(usual));
        Assert.That(
            GameDirectoryIdentityText.ForHomeGuidance(RetailExecutableIdentity.DifferentFromKnownRetail, usual),
            Does.Contain("not the known Steam retail file"));
        Assert.That(
            GameDirectoryIdentityText.ForHomeGuidance(RetailExecutableIdentity.DifferentFromKnownRetail, usual),
            Does.Contain("what is there now"));
        Assert.That(
            GameDirectoryIdentityText.ForHomeGuidance(RetailExecutableIdentity.Unreadable, usual),
            Does.Contain("could not read BEA.exe"));
    }

    [Test]
    public void TheCopyNeverUsesTheProjectsInternalVocabulary()
    {
        string[] banned =
        {
            "receipt", "manifest", "provenance", "byte-verified", "specimen",
            "catalog", "preflight", "profile root", "proof level", "dword", "sha-256", "sha256",
        };

        foreach (RetailExecutableIdentity identity in Enum.GetValues<RetailExecutableIdentity>())
        {
            string all = (
                GameDirectoryIdentityText.ForSettings(identity) + " " +
                GameDirectoryIdentityText.ForHomeGuidance(identity, "default guidance") + " " +
                GameDirectoryIdentityText.AutoDetectFailed + " " +
                GameDirectoryIdentityText.PersistFailed + " " +
                GameDirectoryIdentityText.AppearancePersistFailed + " " +
                GameDirectoryIdentityText.MediaPersistFailed).ToLowerInvariant();
            foreach (string word in banned)
            {
                Assert.That(all, Does.Not.Contain(word), $"Identity copy should not say '{word}'.");
            }
        }
    }

    [Test]
    public void AutoDetectFailureTellsThePlayerWhatToDoWithoutJargon()
    {
        Assert.That(GameDirectoryIdentityText.AutoDetectFailed, Does.Contain("Could not find the game automatically"));
        Assert.That(GameDirectoryIdentityText.AutoDetectFailed, Does.Contain("BEA.exe"));
        Assert.That(GameDirectoryIdentityText.AutoDetectFailed.ToLowerInvariant(), Does.Not.Contain("preflight"));
        Assert.That(GameDirectoryIdentityText.AutoDetectFailed.ToLowerInvariant(), Does.Not.Contain("catalog"));
    }

    [Test]
    public void AFailedSaveNamesTheFolderWasNotKept()
    {
        Assert.That(GameDirectoryIdentityText.PersistFailed, Does.Contain("Could not keep that folder"));
        Assert.That(GameDirectoryIdentityText.PersistFailed, Does.Contain("Nothing was changed"));
        Assert.That(GameDirectoryIdentityText.PersistFailed, Does.Contain("Try choosing it again"));
        Assert.That(GameDirectoryIdentityText.PersistFailed, Does.Not.Contain(":\\"));
        Assert.That(GameDirectoryIdentityText.PersistFailed, Does.Not.Contain("/"));
    }

    [Test]
    public void AFailedAppearanceOrMediaSaveNamesTheChoiceWasNotKept()
    {
        Assert.That(GameDirectoryIdentityText.AppearancePersistFailed, Does.Contain("Could not keep that look"));
        Assert.That(GameDirectoryIdentityText.AppearancePersistFailed, Does.Contain("Nothing was changed"));
        Assert.That(GameDirectoryIdentityText.MediaPersistFailed, Does.Contain("Could not keep those media choices"));
        Assert.That(GameDirectoryIdentityText.MediaPersistFailed, Does.Contain("Nothing was changed"));
        Assert.That(GameDirectoryIdentityText.AppearancePersistFailed, Does.Not.Contain(":\\"));
        Assert.That(GameDirectoryIdentityText.MediaPersistFailed, Does.Not.Contain(":\\"));
    }

    [Test]
    public void SettingsAndHomeActuallyShowTheIdentityLine()
    {
        string root = FindRepoRoot();
        string settingsXaml = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml"));
        string settingsCode = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml.cs"));
        string homeCode = File.ReadAllText(Path.Combine(root, "OnslaughtCareerEditor.WinUI", "Pages", "HomePage.xaml.cs"));

        Assert.That(settingsXaml, Does.Contain("AutomationProperties.AutomationId=\"SettingsGameDirectoryIdentity\""));
        Assert.That(settingsCode, Does.Contain("IdentifyRetailExecutable"));
        Assert.That(settingsCode, Does.Contain("GameDirectoryIdentityText.ForSettings"));
        Assert.That(homeCode, Does.Contain("GameDirectoryIdentityText.ForHomeGuidance"));
        Assert.That(settingsCode, Does.Contain("GameDirectoryIdentityText.AutoDetectFailed"));
        Assert.That(settingsCode, Does.Contain("GameDirectoryIdentityText.PersistFailed"));
        Assert.That(settingsCode, Does.Contain("RestoreKeptGameDirectory"));
        Assert.That(settingsCode, Does.Contain("GameDirectoryIdentityText.AppearancePersistFailed"));
        Assert.That(settingsCode, Does.Contain("RestoreKeptAppearance"));
        Assert.That(settingsCode, Does.Contain("GameDirectoryIdentityText.MediaPersistFailed"));
        Assert.That(settingsCode, Does.Contain("RestoreKeptMediaPreferences"));
        Assert.That(homeCode, Does.Contain("GameDirectoryIdentityText.AutoDetectFailed"));
        Assert.That(homeCode, Does.Contain("GameDirectoryIdentityText.PersistFailed"));
        Assert.That(homeCode, Does.Not.Contain("That folder could not be saved"));
    }

    [Test]
    public void SettingsPutsTheKeptFolderBackBeforeItSaysPersistFailed()
    {
        string settings = File.ReadAllText(Path.Combine(
            FindRepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml.cs"));

        int fail = settings.IndexOf("if (!config.SetGameDir(path))", StringComparison.Ordinal);
        int restore = settings.IndexOf("RestoreKeptGameDirectory();", StringComparison.Ordinal);
        int sentence = settings.IndexOf("GameDirectoryIdentityText.PersistFailed", StringComparison.Ordinal);
        int notify = settings.IndexOf("AppConfigChangedService.NotifyChanged", StringComparison.Ordinal);

        Assert.That(fail, Is.GreaterThanOrEqualTo(0));
        Assert.That(restore, Is.GreaterThan(fail));
        Assert.That(sentence, Is.GreaterThan(restore));
        Assert.That(notify, Is.GreaterThan(sentence));
        Assert.That(settings.IndexOf("return;", fail, notify - fail, StringComparison.Ordinal), Is.GreaterThan(sentence));
    }

    [Test]
    public void SettingsPutsTheKeptLookAndMediaBackBeforeItSaysPersistFailed()
    {
        string settings = File.ReadAllText(Path.Combine(
            FindRepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml.cs"));
        string xaml = File.ReadAllText(Path.Combine(
            FindRepoRoot(), "OnslaughtCareerEditor.WinUI", "Pages", "SettingsPage.xaml"));

        int appearanceFail = settings.IndexOf("RestoreKeptAppearance();", StringComparison.Ordinal);
        int mediaFail = settings.IndexOf("RestoreKeptMediaPreferences();", StringComparison.Ordinal);
        int appearanceNotify = settings.IndexOf(
            "AppearancePersistStatusTextBlock.Visibility = Visibility.Collapsed;",
            appearanceFail,
            StringComparison.Ordinal);
        int mediaNotify = settings.IndexOf(
            "MediaPersistStatusTextBlock.Visibility = Visibility.Collapsed;",
            mediaFail,
            StringComparison.Ordinal);

        Assert.That(appearanceFail, Is.GreaterThanOrEqualTo(0));
        Assert.That(mediaFail, Is.GreaterThan(appearanceFail));
        Assert.That(appearanceNotify, Is.GreaterThan(appearanceFail));
        Assert.That(mediaNotify, Is.GreaterThan(mediaFail));
        Assert.That(xaml, Does.Contain("SettingsAppearancePersistStatus"));
        Assert.That(xaml, Does.Contain("SettingsMediaPersistStatus"));
        Assert.That(settings, Does.Contain("GameDirectoryIdentityText.AppearancePersistFailed"));
        Assert.That(settings, Does.Contain("GameDirectoryIdentityText.MediaPersistFailed"));
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
