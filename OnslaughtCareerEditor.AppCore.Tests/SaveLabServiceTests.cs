using System.Runtime.InteropServices;
using System.Security.Cryptography;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests;

public sealed class SaveLabServiceTests
{
    [Fact]
    public void Open_AnalyzesRealFixtureWithoutChangingItOrExposingMutableSnapshot()
    {
        using Fixture fixture = new();
        SaveLabOpenResult opened = SaveLabService.Open(fixture.Input);
        Assert.True(opened.Success, opened.Message);
        SaveLabSession session = Assert.IsType<SaveLabSession>(opened.Session);
        Assert.Equal(BesFilePatcher.EXPECTED_FILE_SIZE, session.FileSize);
        Assert.Equal(Convert.ToHexString(SHA256.HashData(fixture.Original)), session.InputSha256);
        Assert.True(session.Analysis.IsValid);
        Assert.True(session.Analysis.KillCounts.Distinct().Count() > 1);
        int expected = session.Analysis.KillCounts[0];
        session.Analysis.KillCounts[0] = 0;
        Assert.Equal(expected, session.Analysis.KillCounts[0]);
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
    }

    [Theory]
    [InlineData(0)]
    [InlineData(1)]
    [InlineData(2)]
    [InlineData(3)]
    [InlineData(4)]
    public void WriteCopy_ReopensRealSaveAndPreservesEveryUnselectedByte(int category)
    {
        using Fixture fixture = new();
        SaveLabSession session = fixture.Open();
        const int target = 123456;
        Assert.NotEqual(target, session.Analysis.KillCounts[category]);
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(session, fixture.Output, category, target);
        Assert.True(result.Success, result.Message);
        Assert.True(result.OriginalVerified);
        Assert.True(result.UntargetedBytesVerified);
        Assert.InRange(result.ChangedBytes, 1, 3);
        Assert.Equal(target, result.Analysis!.KillCounts[category]);
        byte[] output = File.ReadAllBytes(fixture.Output);
        Assert.Equal(BesFilePatcher.EXPECTED_FILE_SIZE, output.Length);
        Assert.Equal(Convert.ToHexString(SHA256.HashData(output)), result.OutputSha256);
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
        // An independent literal fixture-layout assertion covers unknown bytes as well as known fields.
        int firstCountByte = 0x23F6 + category * 4;
        for (int offset = 0; offset < output.Length; offset++)
            if (offset < firstCountByte || offset >= firstCountByte + 3)
                Assert.Equal(fixture.Original[offset], output[offset]);
        Assert.Equal(target, BesFilePatcher.AnalyzeSave(fixture.Output).KillCounts[category]);
        Assert.DoesNotContain(Directory.EnumerateFiles(fixture.OutputDirectory), path => path != fixture.Output);
    }

    [Theory]
    [InlineData(-1, 2)]
    [InlineData(5, 2)]
    [InlineData(0, -1)]
    [InlineData(0, 0x01000000)]
    public void WriteCopy_RejectsUnstatedOrOutOfRangeChanges(int category, int count)
    {
        using Fixture fixture = new();
        Assert.False(SaveLabService.WriteKillCountCopy(fixture.Open(), fixture.Output, category, count).Success);
        Assert.False(File.Exists(fixture.Output));
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
    }

    [Fact]
    public void WriteCopy_RefusesNoChangeSameInputAndExistingOutput()
    {
        using Fixture fixture = new();
        SaveLabSession session = fixture.Open();
        Assert.False(SaveLabService.WriteKillCountCopy(session, fixture.Output, 0, session.Analysis.KillCounts[0]).Success);
        Assert.False(SaveLabService.WriteKillCountCopy(session, fixture.Input, 0, 123456).Success);
        File.Copy(fixture.Input, fixture.Output);
        Assert.False(SaveLabService.WriteKillCountCopy(session, fixture.Output, 0, 123456).Success);
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Output));
    }

    [Fact]
    public void Open_RejectsBadExtensionLengthAndVersionFromFixtureCopies()
    {
        using Fixture fixture = new();
        string renamed = Path.Combine(fixture.Root, "options.bea");
        File.Copy(fixture.Input, renamed);
        Assert.False(SaveLabService.Open(renamed).Success);
        byte[] wrong = fixture.Original.ToArray();
        wrong[0] ^= 1;
        File.WriteAllBytes(fixture.Input, wrong);
        Assert.False(SaveLabService.Open(fixture.Input).Success);
        File.WriteAllBytes(fixture.Input, fixture.Original[..^1]);
        Assert.False(SaveLabService.Open(fixture.Input).Success);
    }

    [Fact]
    public void WriteCopy_RefusesSourceContentChangeAfterOpen()
    {
        using Fixture fixture = new();
        SaveLabSession session = fixture.Open();
        byte[] changed = fixture.Original.ToArray();
        changed[^1] ^= 1;
        File.WriteAllBytes(fixture.Input, changed);
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(session, fixture.Output, 0, 123456);
        Assert.False(result.Success);
        Assert.Contains("changed", result.Message);
        Assert.False(File.Exists(fixture.Output));
        Assert.Equal(changed, File.ReadAllBytes(fixture.Input));
    }

    [Fact]
    public void WriteCopy_RefusesSourceIdentityReplacementEvenWithIdenticalBytes()
    {
        using Fixture fixture = new();
        SaveLabSession session = fixture.Open();
        File.Move(fixture.Input, Path.Combine(fixture.Root, "old.bes"));
        File.WriteAllBytes(fixture.Input, fixture.Original);
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(session, fixture.Output, 0, 123456);
        Assert.False(result.Success);
        Assert.Contains("changed", result.Message);
        Assert.False(File.Exists(fixture.Output));
    }

    [Fact]
    public void Linux_RejectsSourceHardlinkAndDanglingOutputSymlink()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        SaveLabSession session = fixture.Open();
        string alias = Path.Combine(fixture.Root, "alias.bes");
        Assert.Equal(0, Link(fixture.Input, alias));
        Assert.False(SaveLabService.Open(alias).Success);
        Assert.False(SaveLabService.WriteKillCountCopy(session, fixture.Output, 0, 123456).Success);
        Assert.Equal(fixture.Original, File.ReadAllBytes(alias));
        File.Delete(alias);
        File.CreateSymbolicLink(fixture.Output, Path.Combine(fixture.Root, "absent.bes"));
        Assert.False(SaveLabService.WriteKillCountCopy(session, fixture.Output, 0, 123456).Success);
        Assert.NotNull(new FileInfo(fixture.Output).LinkTarget);
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
    }

    [Fact]
    public void Linux_RejectsLinkedSourceAndOutputFolder()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        string sourceLink = Path.Combine(fixture.Root, "source-link.bes");
        File.CreateSymbolicLink(sourceLink, fixture.Input);
        Assert.False(SaveLabService.Open(sourceLink).Success);
        string folderLink = Path.Combine(fixture.Root, "folder-link");
        Directory.CreateSymbolicLink(folderLink, fixture.OutputDirectory);
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(fixture.Open(),
            Path.Combine(folderLink, "copy.bes"), 0, 123456);
        Assert.False(result.Success);
        Assert.Empty(Directory.EnumerateFileSystemEntries(fixture.OutputDirectory));
    }

    [Fact]
    public void Linux_PublicationRaceDoesNotReplaceDestinationThatAppearsAfterStaging()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(fixture.Open(), fixture.Output, 0, 123456,
            () => File.WriteAllBytes(fixture.Output, fixture.Original));
        Assert.False(result.Success);
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Output));
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
        Assert.Single(Directory.EnumerateFileSystemEntries(fixture.OutputDirectory));
    }

    [Fact]
    public void Linux_NativePublicationDoesNotReplaceAnEntryCreatedAfterItsLastVacancyCheck()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        using LinuxSaveDirectory directory = LinuxSaveDirectory.Open(fixture.OutputDirectory);
        using FileStream staged = directory.CreateUnnamed();
        staged.Write(fixture.Original);
        staged.Flush(flushToDisk: true);
        Assert.Empty(Directory.EnumerateFileSystemEntries(fixture.OutputDirectory));
        directory.RequireVacant("copy.bes");
        byte[] competing = fixture.Original.ToArray();
        competing[^1] ^= 1;
        File.WriteAllBytes(fixture.Output, competing);
        Assert.Throws<IOException>(() => directory.Publish(staged.SafeFileHandle, "copy.bes"));
        Assert.Equal(competing, File.ReadAllBytes(fixture.Output));
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
    }

    [Fact]
    public void Linux_PublicationRefusesDirectoryReplacement()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        string displaced = Path.Combine(fixture.Root, "displaced");
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(fixture.Open(), fixture.Output, 0, 123456, () =>
        {
            Directory.Move(fixture.OutputDirectory, displaced);
            Directory.CreateDirectory(fixture.OutputDirectory);
        });
        Assert.False(result.Success);
        Assert.Empty(Directory.EnumerateFileSystemEntries(fixture.OutputDirectory));
        Assert.Empty(Directory.EnumerateFileSystemEntries(displaced));
        Assert.Equal(fixture.Original, File.ReadAllBytes(fixture.Input));
    }

    [Fact]
    public void Linux_PublicationRefusesSourceChangeDuringStaging()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        byte[] changed = fixture.Original.ToArray();
        changed[^1] ^= 1;
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(fixture.Open(), fixture.Output, 0, 123456,
            () => File.WriteAllBytes(fixture.Input, changed));
        Assert.False(result.Success);
        Assert.False(File.Exists(fixture.Output));
        Assert.Equal(changed, File.ReadAllBytes(fixture.Input));
        Assert.Empty(Directory.EnumerateFileSystemEntries(fixture.OutputDirectory));
    }

    [Fact]
    public void Linux_FinalSourceChangeReportsTheAlreadyCreatedOutputAsUnverified()
    {
        if (!OperatingSystem.IsLinux()) return;
        using Fixture fixture = new();
        byte[] changed = fixture.Original.ToArray();
        changed[^1] ^= 1;
        SaveLabWriteResult result = SaveLabService.WriteKillCountCopy(fixture.Open(), fixture.Output, 0, 123456,
            beforePublish: null, afterPublish: () => File.WriteAllBytes(fixture.Input, changed));
        Assert.False(result.Success);
        Assert.False(result.OriginalVerified);
        Assert.Equal(fixture.Output, result.OutputPath);
        Assert.Contains("new copy exists", result.Message);
        Assert.True(File.Exists(fixture.Output));
        Assert.Equal(changed, File.ReadAllBytes(fixture.Input));
        Assert.Equal(123456, BesFilePatcher.AnalyzeSave(fixture.Output).KillCounts[0]);
    }

    [DllImport("libc", EntryPoint = "link", SetLastError = true)]
    private static extern int Link(string existing, string alias);

    private sealed class Fixture : IDisposable
    {
        internal Fixture()
        {
            DirectoryInfo? repo = new(AppContext.BaseDirectory);
            while (repo is not null && !File.Exists(Path.Combine(repo.FullName, "package.json")))
                repo = repo.Parent;
            Assert.NotNull(repo);
            string gold = Path.Combine(repo.FullName, "tests_shared", "fixtures", "gold_career_save.bin");
            Assert.True(File.Exists(gold), "The tracked real-save fixture is required for this workflow's acceptance tests.");
            Original = File.ReadAllBytes(gold);
            Root = Path.Combine(Path.GetTempPath(), "onslaught-save-lab-" + Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Root);
            Input = Path.Combine(Root, "original.bes");
            File.WriteAllBytes(Input, Original);
            OutputDirectory = Path.Combine(Root, "output");
            Directory.CreateDirectory(OutputDirectory);
            Output = Path.Combine(OutputDirectory, "copy.bes");
        }

        internal string Root { get; }
        internal string Input { get; }
        internal string Output { get; }
        internal string OutputDirectory { get; }
        internal byte[] Original { get; }
        internal SaveLabSession Open()
        {
            SaveLabOpenResult result = SaveLabService.Open(Input);
            Assert.True(result.Success, result.Message);
            return Assert.IsType<SaveLabSession>(result.Session);
        }
        public void Dispose() => Directory.Delete(Root, recursive: true);
    }
}
