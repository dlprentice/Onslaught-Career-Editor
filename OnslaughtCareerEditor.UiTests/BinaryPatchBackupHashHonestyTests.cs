using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// A leftover backup hash used to say sidecar / copied-workspace.
/// Name the hash file and the backup.
/// </summary>
public class BinaryPatchBackupHashHonestyTests
{
    [Test]
    public void AHashFileWithoutABackupNamesTheFilesNotASidecar()
    {
        string folder = Path.Combine(Path.GetTempPath(), $"bea-hash-only-{Guid.NewGuid():N}");
        Directory.CreateDirectory(folder);
        string exePath = Path.Combine(folder, "BEA.exe");
        File.WriteAllBytes(exePath, new byte[16]);
        File.WriteAllText(BinaryPatchEngine.BuildBackupHashPath(exePath), "deadbeef");
        try
        {
            var restore = BinaryPatchEngine.RestoreFromBackup(
                new BinaryPatchTargetOptions(exePath, AllowedRoot: folder));

            Assert.That(restore.success, Is.False);
            Assert.That(restore.message, Is.EqualTo(BinaryPatchEngine.BackupHashWithoutBackup));
            Assert.That(restore.message, Is.EqualTo(
                "The backup hash file is here without BEA.exe.original.backup. Remove that leftover hash file. Nothing was changed."));
            Assert.That(restore.message, Does.Contain("backup hash file"));
            Assert.That(restore.message, Does.Contain("BEA.exe.original.backup"));
            Assert.That(restore.message.ToLowerInvariant(), Does.Not.Contain("sidecar"));
            Assert.That(restore.message.ToLowerInvariant(), Does.Not.Contain("copied-workspace"));
            Assert.That(restore.message.ToLowerInvariant(), Does.Not.Contain("path"));
            Assert.That(restore.message, Does.Not.Contain(folder));
            Assert.That(restore.message, Does.Not.Contain(":\\"));
        }
        finally
        {
            Directory.Delete(folder, recursive: true);
        }
    }

    [Test]
    public void ThePatchEngineDropsTheSidecarSentence()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "BinaryPatchEngine.cs"));

        Assert.That(source, Does.Contain("BackupHashWithoutBackup"));
        Assert.That(source, Does.Not.Contain("stale copied-workspace sidecar"));
        Assert.That(source, Does.Not.Contain("Patch backup hash sidecar exists without its backup snapshot"));
        Assert.That(source, Does.Not.Contain("The backup hash sidecar is missing"));
        Assert.That(source, Does.Contain("The backup hash file is missing, and the BEA.exe-only copy was not overwritten."));
    }
}
