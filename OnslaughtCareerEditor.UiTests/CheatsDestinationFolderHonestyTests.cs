using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Writing a cheat-named save into a folder that is gone used to say
/// only that the folder does not exist. Name the next step.
/// </summary>
public class CheatsDestinationFolderHonestyTests
{
    [Test]
    public void AMissingDestinationFolderNamesTheNextStep()
    {
        using TempDirectory workspace = new();
        string source = workspace.CopyIn(TestFixturePaths.RequireGoldSavePath(), "MyCareer.bes");
        string missing = Path.Combine(workspace.Path, "gone");

        CheatSaveWriteOutcome outcome = CheatSaveWriterService.Write(new CheatSaveWriteRequest
        {
            InputPath = source,
            OutputDirectory = missing,
            Name = "MALLOY",
        });

        Assert.That(outcome.Success, Is.False);
        Assert.That(outcome.Message, Is.EqualTo(CheatSaveWriterService.DestinationFolderMissing));
        Assert.That(outcome.Message, Does.Contain("Choose"));
        Assert.That(outcome.Message, Does.Not.Contain("does not exist"));
        Assert.That(outcome.Message, Does.Not.Contain(missing));
        Assert.That(outcome.Message.ToLowerInvariant(), Does.Not.Contain("path"));
        Assert.That(File.Exists(Path.Combine(missing, "MALLOY.bes")), Is.False);
    }

    private sealed class TempDirectory : IDisposable
    {
        public TempDirectory()
        {
            Path = System.IO.Path.Combine(
                System.IO.Path.GetTempPath(),
                $"onslaught-cheats-dest-{Guid.NewGuid():N}");
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
            }
        }
    }
}
