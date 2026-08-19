using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A patch target with no workspace used to require an app-owned workspace
/// root. Name the folder, not a root.
/// </summary>
public class BinaryPatchWorkspaceFolderHonestyTests
{
    [Test]
    public void ABlankWorkspaceFolderNamesTheFolderNotARoot()
    {
        string folder = Path.Combine(Path.GetTempPath(), $"bea-workspace-{Guid.NewGuid():N}");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var (success, message) = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: " "));

            Assert.That(success, Is.False);
            Assert.That(message, Is.EqualTo(BinaryPatchEngine.WorkspaceFolderRequired));
            Assert.That(message, Is.EqualTo("An app-owned workspace folder is required."));
            Assert.That(message, Does.Contain("workspace folder"));
            Assert.That(message.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(message.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(message, Does.Not.Contain(folder));
            Assert.That(message, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(folder, recursive: true);
        }
    }

    [Test]
    public void ThePatchEngineDropsTheWorkspaceRootSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));

        Assert.That(source, Does.Contain("WorkspaceFolderRequired"));
        Assert.That(source, Does.Not.Contain("Patch target requires an app-owned workspace root."));
    }
}
