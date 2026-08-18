using System;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Cheats page's write is meant to change exactly one thing about a save: its name. That is
/// what makes the feature safe to offer and trivial to undo, and it is the claim the page copy
/// makes to the player, so it is asserted here against a real career save rather than trusted.
///
/// Also pinned: the source is never modified, an existing file is never replaced without being
/// asked for, and a destination inside an installed game folder is refused.
/// </summary>
public class CheatSaveWriterServiceTests
{
    private static string GoldSavePath => TestFixturePaths.RequireGoldSavePath();

    [Test]
    public void TheWrittenSaveIsByteForByteTheSaveYouStartedFrom()
    {
        using TempDirectory workspace = new();
        string source = workspace.CopyIn(GoldSavePath, "MyCareer.bes");
        byte[] before = File.ReadAllBytes(source);

        CheatSaveName composed = CheatSaveNameComposer.Compose(
            null,
            [CheatCodeCatalog.AllGoodiesId, CheatCodeCatalog.AllLevelsId, CheatCodeCatalog.GodModeId]);
        CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = source,
            OutputDirectory = workspace.Path,
            Name = composed.Name,
        });

        Assert.That(outcome.Success, Is.True, outcome.Message);
        Assert.That(Path.GetFileName(outcome.OutputPath!), Is.EqualTo("MALLOYTURKEYMaladim.bes"));

        byte[] written = File.ReadAllBytes(outcome.OutputPath!);
        Assert.That(
            Convert.ToHexString(SHA256.HashData(written)),
            Is.EqualTo(Convert.ToHexString(SHA256.HashData(before))),
            "The only thing this feature changes is the file name.");
        Assert.That(
            File.ReadAllBytes(source),
            Is.EqualTo(before),
            "The save the player picked must come out of this untouched.");
    }

    [Test]
    public void AnExistingFileIsNotReplacedUntilThePlayerHasBeenAsked()
    {
        using TempDirectory workspace = new();
        string source = workspace.CopyIn(GoldSavePath, "MyCareer.bes");
        string occupied = Path.Combine(workspace.Path, "MALLOY.bes");
        File.WriteAllText(occupied, "something the player already had");

        CheatSaveWriteRequest request = new()
        {
            InputPath = source,
            OutputDirectory = workspace.Path,
            Name = "MALLOY",
        };

        CheatSaveWriteOutcome refused = CheatSaveWriterService.Write(request);

        Assert.That(refused.Success, Is.False);
        Assert.That(refused.NeedsOverwriteConfirmation, Is.True);
        Assert.That(File.ReadAllText(occupied), Is.EqualTo("something the player already had"));

        CheatSaveWriteOutcome confirmed = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = request.InputPath,
            OutputDirectory = request.OutputDirectory,
            Name = request.Name,
            AllowOverwrite = true,
        });

        Assert.That(confirmed.Success, Is.True, confirmed.Message);
        Assert.That(new FileInfo(occupied).Length, Is.EqualTo(new FileInfo(source).Length));
    }

    [Test]
    public void WritingIntoAnInstalledGameFolderIsRefused()
    {
        using TempDirectory workspace = new();
        string source = workspace.CopyIn(GoldSavePath, "MyCareer.bes");

        // A folder is treated as an installed game when it holds BEA.exe beside a data directory.
        string gameRoot = Path.Combine(workspace.Path, "Battle Engine Aquila");
        Directory.CreateDirectory(Path.Combine(gameRoot, "data"));
        File.WriteAllText(Path.Combine(gameRoot, "BEA.exe"), "not really an executable");
        string savegames = Path.Combine(gameRoot, "savegames");
        Directory.CreateDirectory(savegames);

        CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = source,
            OutputDirectory = savegames,
            Name = "MALLOY",
        });

        Assert.That(outcome.Success, Is.False);
        Assert.That(File.Exists(Path.Combine(savegames, "MALLOY.bes")), Is.False);
    }

    [Test]
    public void WritingOverTheSaveYouPickedIsRefused()
    {
        using TempDirectory workspace = new();
        string source = workspace.CopyIn(GoldSavePath, "MALLOY.bes");

        CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = source,
            OutputDirectory = workspace.Path,
            Name = "MALLOY",
            AllowOverwrite = true,
        });

        Assert.That(outcome.Success, Is.False);
        Assert.That(outcome.Message, Does.Contain("save you picked"));
    }

    [Test]
    public void AFileThatIsNotACareerSaveIsRefusedWithTheReason()
    {
        using TempDirectory workspace = new();
        string notASave = Path.Combine(workspace.Path, "notes.bes");
        File.WriteAllText(notASave, "hello");

        CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = notASave,
            OutputDirectory = workspace.Path,
            Name = "MALLOY",
        });

        Assert.That(outcome.Success, Is.False);
        Assert.That(outcome.Message, Is.Not.Null.And.Not.Empty);
        Assert.That(File.Exists(Path.Combine(workspace.Path, "MALLOY.bes")), Is.False);
    }

    [Test]
    public void AnUnusableNameNeverReachesTheDisk()
    {
        using TempDirectory workspace = new();
        string source = workspace.CopyIn(GoldSavePath, "MyCareer.bes");

        CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = source,
            OutputDirectory = workspace.Path,
            Name = "bad:name",
        });

        Assert.That(outcome.Success, Is.False);
        Assert.That(Directory.GetFiles(workspace.Path).Select(Path.GetFileName), Is.EqualTo(new[] { "MyCareer.bes" }));
    }

    [Test]
    public void AFailedWriteDoesNotDumpTheExceptionOrAPath()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot, "OnslaughtCareerEditor.AppCore", "CheatSaveWriterService.cs"));

        Assert.That(source, Does.Contain("WriteFailed"));
        Assert.That(source, Does.Not.Contain("ex.Message"));
        Assert.That(CheatSaveWriterService.WriteFailed, Does.Contain("Nothing was changed"));
        Assert.That(CheatSaveWriterService.WriteFailed, Does.Not.Contain(":\\"));
        Assert.That(CheatSaveWriterService.WriteFailed.ToLowerInvariant(), Does.Not.Contain("exception"));
    }

    [Test]
    public void SafeCopyDiscoveryIsTotal_AndNeverThrowsWhenThereAreNone()
    {
        Assert.DoesNotThrow(() => _ = CheatSaveWriterService.FindSafeCopyTargets());
    }

    private sealed class TempDirectory : IDisposable
    {
        public TempDirectory()
        {
            Path = System.IO.Path.Combine(
                System.IO.Path.GetTempPath(),
                $"onslaught-cheats-{Guid.NewGuid():N}");
            Directory.CreateDirectory(Path);
        }

        public string Path { get; }

        public string CopyIn(string sourcePath, string fileName)
        {
            string destination = System.IO.Path.Combine(Path, fileName);
            File.Copy(sourcePath, destination);
            return destination;
        }

        public void Dispose()
        {
            try
            {
                Directory.Delete(Path, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // A leftover temp folder is not worth failing a test over.
            }
        }
    }
}
