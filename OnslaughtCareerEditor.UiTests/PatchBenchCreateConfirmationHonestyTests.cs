using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Windowed &amp; Mods Create safe copy used to say verified profile
/// in the confirmation body. ConfirmAsync paints that helper. Name
/// the selected profile.
/// </summary>
public class PatchBenchCreateConfirmationHonestyTests
{
    [Test]
    public void CreateConfirmationPaintsTheSelectedProfileNotAVerifiedProfile()
    {
        string painted = InvokeCreateConfirmation();

        Assert.That(
            painted,
            Does.Contain("apply the selected profile and selected mods only inside that copy."));
        Assert.That(painted, Does.Contain("selected profile"));
        Assert.That(painted, Does.Not.Contain("verified profile"));
        Assert.That(painted, Does.Not.Contain("app-owned"));
        Assert.That(painted, Does.Not.Contain(":\\"));
    }

    [Test]
    public void CreateSafeCopyConfirmationPaintsTheHelperBody()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));
        string helper = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Helpers",
            "PatchBenchSafeCopyOutcomeText.cs"));

        Assert.That(page, Does.Contain("\"Create safe copy?\""));
        Assert.That(page, Does.Contain("PatchBenchSafeCopyOutcomeText.BuildCreateConfirmation"));
        Assert.That(
            helper,
            Does.Contain("apply the selected profile and selected mods only inside that copy."));
        Assert.That(
            helper,
            Does.Not.Contain("apply the verified profile and selected mods only inside that copy."));
    }

    private static string InvokeCreateConfirmation()
    {
        return (string)ReflectedWinUiTestSupport.InvokeRequiredStaticMethod(
            ReflectedWinUiTestSupport.GetRequiredType(
                "OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopyOutcomeText",
                "OnslaughtCareerEditor.WinUI/Helpers/PatchBenchSafeCopyOutcomeText.cs"),
            "BuildCreateConfirmation",
            @"C:\Steam\steamapps\common\Battle Engine Aquila",
            @"C:\Users\player\AppData\GameProfiles",
            "Settings affecting this copy:" + Environment.NewLine + "Extra settings for next copy: none active.",
            string.Empty);
    }
}
