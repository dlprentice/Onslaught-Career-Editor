using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Restoring a tracked safe-copy process used to interpolate
/// <c>registered.Process.ExecutablePath</c> into Last operation. That is the
/// copy folder path. Live launch already names BEA.exe via
/// <c>BuildRedactedCommandPreview</c>.
/// </summary>
public class PatchBenchRestoredLaunchHonestyTests
{
    [Test]
    public void ARestoredLaunchPlanNamesBeaExeNotTheCopyFolder()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "Pages",
            "BinaryPatchesPage.xaml.cs"));
        string preflight = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        int start = page.IndexOf("private void RestoreTrackedSafeGameCopyProcess", StringComparison.Ordinal);
        int end = page.IndexOf("private static bool SetEquals", StringComparison.Ordinal);
        Assert.That(start, Is.GreaterThanOrEqualTo(0));
        Assert.That(end, Is.GreaterThan(start));

        string method = page[start..end];
        Assert.That(method, Does.Contain("GameProfilePreflightService.BuildRedactedCommandPreview"));
        Assert.That(method, Does.Not.Contain("{registered.Process.ExecutablePath}"));
        Assert.That(method, Does.Not.Contain("registered.Process.ExecutablePath"));
        Assert.That(preflight, Does.Contain("public static string BuildRedactedCommandPreview"));
        Assert.That(preflight, Does.Contain("BEA.exe"));
        Assert.That(preflight, Does.Not.Contain("Start-Process -FilePath \\\"{"));
    }
}
