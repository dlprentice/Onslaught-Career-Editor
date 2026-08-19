using System.IO;
using System.Text.RegularExpressions;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Copied-game apply/restore already named the action, then appended ex.Message
/// on the next line. That still put the OS path on Windowed &amp; Mods Last operation.
/// </summary>
public class BinaryPatchCopyHonestyTests
{
    [Test]
    public void CopiedGameApplyAndRestoreDoNotAppendTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(
            Regex.IsMatch(engine, @"\+\s*ex\.Message\)"),
            Is.False,
            "Apply/restore I/O still concatenates ex.Message after the honest sentence.");
        Assert.That(engine, Does.Contain("the BEA.exe-only copy was not modified"));
        Assert.That(engine, Does.Contain("The verified full-file backup remains available"));
        Assert.That(engine, Does.Contain("The verified backup snapshot was left unchanged"));
    }

    [Test]
    public void AnUnusablePatchTargetDoesNotDumpTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(engine, Does.Contain("WorkingCopyPathUnusable"));
        Assert.That(engine, Does.Not.Contain("Patch target path could not be normalized: {ex.Message}"));
        Assert.That(engine, Does.Contain("That patch target could not be used. Nothing was changed."));
    }

    [Test]
    public void CatalogReadFallbackDoesNotDumpTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));
        string profiles = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchPlanBuilder.cs"));

        Assert.That(engine, Does.Not.Contain("Catalog read failed ({ex.Message})"));
        Assert.That(engine, Does.Contain("Catalog could not be read; using built-in fallback patch specs."));
        Assert.That(profiles, Does.Not.Contain("Profile catalog read failed ({ex.Message})"));
        Assert.That(profiles, Does.Contain("Profile catalog could not be read; using built-in safe-copy profile presets."));
    }

    [Test]
    public void FilesystemSafetyDoesNotDumpTheException()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(engine, Does.Not.Contain("return (false, ex.Message);"));
        Assert.That(engine, Does.Contain("WorkingCopyPathUnusable"));
        Assert.That(engine, Does.Contain("That patch target could not be used. Nothing was changed."));
    }

    [Test]
    public void LoadedCatalogStatusDoesNotIncludeAFullPath()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));
        string profiles = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchPlanBuilder.cs"));

        Assert.That(engine, Does.Not.Contain("Loaded patch catalog from {catalogPath}"));
        Assert.That(engine, Does.Contain("Loaded the patch catalog."));
        Assert.That(profiles, Does.Not.Contain("Loaded safe-copy profile catalog from {catalogPath}"));
        Assert.That(profiles, Does.Contain("Loaded the safe-copy profile catalog."));
    }

    [Test]
    public void ApplyAndRestoreNameTheFilesNotThePaths()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(engine, Does.Not.Contain("Target: {exePath}"));
        Assert.That(engine, Does.Not.Contain("Backup: {backupPath}"));
        Assert.That(engine, Does.Not.Contain("Backup source: {backupPath}"));
        Assert.That(engine, Does.Contain("Target: {TargetFileName}"));
        Assert.That(engine, Does.Contain("BEA.exe.original.backup"));
    }

    [Test]
    public void AMissingBackupDoesNotDumpThePath()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs"));

        Assert.That(engine, Does.Not.Contain("Backup file not found: {backupPath}"));
        Assert.That(engine, Does.Contain("BEA.exe.original.backup could not be found. Nothing was changed."));
        Assert.That(page, Does.Not.Contain("Backup file not found for the selected executable."));
        Assert.That(page, Does.Contain("BackupFileMissing"));
    }

    [Test]
    public void ChoosingBeaExeDoesNotCallItAPath()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs"));

        Assert.That(engine, Does.Not.Contain("Select a valid BEA.exe path first."));
        Assert.That(engine, Does.Contain("Select a valid BEA.exe first."));
        Assert.That(page, Does.Not.Contain("loaded source path from shared settings"));
        Assert.That(page, Does.Contain("Windowed & Mods: loaded BEA.exe from Settings"));
    }

    [Test]
    public void WindowedAndModsPathLabelsNameTheFile()
    {
        string xaml = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml"));

        Assert.That(xaml, Does.Not.Contain("Source path details"));
        Assert.That(xaml, Does.Contain("Source file details"));
        Assert.That(xaml, Does.Not.Contain("Path to replacement .ogg"));
        Assert.That(xaml, Does.Contain("Replacement .ogg file"));
        Assert.That(xaml, Does.Not.Contain("Replacement track OGG path"));
        Assert.That(xaml, Does.Contain("Replacement track OGG file"));
        Assert.That(xaml, Does.Not.Contain("Source executable path"));
        Assert.That(xaml, Does.Contain("Source executable file"));
        Assert.That(xaml, Does.Not.Contain("restore path"));
        Assert.That(xaml, Does.Contain("restore steps"));
        Assert.That(xaml, Does.Not.Contain("copy executable path"));
        Assert.That(xaml, Does.Contain("copy executable file"));
    }

    [Test]
    public void WindowedAndModsVerifyHintNamesTheFileNotAPath()
    {
        string page = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.WinUI", "Pages", "BinaryPatchesPage.xaml.cs"));

        Assert.That(page, Does.Not.Contain("after any path or selection change"));
        Assert.That(page, Does.Contain("after any file or selection change"));
    }

    [Test]
    public void AWorkspaceBackupRefusalNamesTheFileNotAPath()
    {
        string engine = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "BinaryPatchEngine.cs"));

        Assert.That(engine, Does.Not.Contain("Patch backup path must stay inside"));
        Assert.That(engine, Does.Not.Contain("Patch backup hash path must stay inside"));
        Assert.That(engine, Does.Contain("BEA.exe.original.backup must stay inside the app-owned Patch Bench workspace."));
        Assert.That(engine, Does.Contain("The backup hash file must stay inside the app-owned Patch Bench workspace."));
    }
}
