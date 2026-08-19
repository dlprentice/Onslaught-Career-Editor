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

    [Test]
    public void ATargetOutsideTheWorkspaceFolderNamesTheFolderNotPatchBench()
    {
        string allowed = Path.Combine(Path.GetTempPath(), $"bea-workspace-allowed-{Guid.NewGuid():N}");
        string outside = Path.Combine(Path.GetTempPath(), $"bea-workspace-outside-{Guid.NewGuid():N}");
        Directory.CreateDirectory(allowed);
        Directory.CreateDirectory(outside);
        string exePath = Path.Combine(outside, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        try
        {
            var restore = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: allowed));

            Assert.That(restore.success, Is.False);
            Assert.That(restore.message, Is.EqualTo(BinaryPatchEngine.PatchTargetMustStayInsideWorkspaceFolder));
            Assert.That(restore.message, Is.EqualTo("Patch target must stay inside the workspace folder."));
            Assert.That(restore.message, Does.Contain("workspace folder"));
            Assert.That(restore.message, Does.Not.Contain("Patch Bench"));
            Assert.That(restore.message.ToLowerInvariant(), Does.Not.Contain("root"));
            Assert.That(restore.message.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(restore.message, Does.Not.Contain(allowed));
            Assert.That(restore.message, Does.Not.Contain(outside));
            Assert.That(restore.message, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(allowed, recursive: true);
            Directory.Delete(outside, recursive: true);
        }
    }

    [Test]
    public void ThePatchEngineDropsThePatchBenchWorkspaceSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));

        Assert.That(source, Does.Contain("PatchTargetMustStayInsideWorkspaceFolder"));
        Assert.That(source, Does.Contain("BackupMustStayInsideWorkspaceFolder"));
        Assert.That(source, Does.Contain("BackupHashMustStayInsideWorkspaceFolder"));
        Assert.That(source, Does.Not.Contain("app-owned Patch Bench workspace."));
        Assert.That(source, Does.Not.Contain("app-owned Patch Bench workspace root"));
        Assert.That(BinaryPatchEngine.BackupMustStayInsideWorkspaceFolder,
            Is.EqualTo("BEA.exe.original.backup must stay inside the workspace folder."));
        Assert.That(BinaryPatchEngine.BackupHashMustStayInsideWorkspaceFolder,
            Is.EqualTo("The backup hash file must stay inside the workspace folder."));
    }

    [Test]
    public void AProtectedInstallNamesTheFolderNotARoot()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));

        Assert.That(source, Does.Contain("ProtectedInstallFolder"));
        Assert.That(source, Does.Not.Contain("protected install root"));
        Assert.That(BinaryPatchEngine.ProtectedInstallFolder, Does.Contain("protected install folder"));
        Assert.That(BinaryPatchEngine.ProtectedInstallFolder.ToLowerInvariant(), Does.Not.Contain("root"));
    }
}
