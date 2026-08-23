using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// A synthetic Battle Engine Aquila installation tree in a scratch directory, addressed by
    /// <c>--game-dir</c>. Modelled on the AppCore suite's <c>TempGameDirectory</c> plus its
    /// structurally-real language-file builder, rebuilt locally because test projects do not
    /// reference each other. No retail bytes, no machine installation, no real ogg decoding -
    /// every media file is empty, which is exactly why durations and sizes come back empty and
    /// the output stays deterministic.
    /// </summary>
    public sealed class MediaGameTree : IDisposable
    {
        private static readonly string RootBase =
            Path.Combine(Path.GetTempPath(), "onslaught-cli-media");

        public MediaGameTree()
        {
            Root = Path.Combine(RootBase, Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Root);
            File.WriteAllText(Path.Combine(Root, "BEA.exe"), string.Empty);
            Directory.CreateDirectory(Path.Combine(Root, "data"));
        }

        public string Root { get; }

        public string WriteFile(string relativePath)
        {
            string fullPath = Path.Combine(Root, relativePath);
            string? directory = Path.GetDirectoryName(fullPath);
            if (!string.IsNullOrWhiteSpace(directory))
                Directory.CreateDirectory(directory);

            File.WriteAllText(fullPath, string.Empty);
            return fullPath;
        }

        /// <summary>
        /// Writes <c>data/language/english.dat</c> in the v3 layout the game's own loader uses,
        /// mirroring the AppCore fixture builder byte for byte.
        /// </summary>
        public void WriteLanguageFile(params (string Text, string? Audio)[] entries)
        {
            string path = Path.Combine(Root, "data", "language", "english.dat");
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllBytes(path, BuildLanguageFile(entries));
        }

        /// <summary>Every path, byte length, and write time under the tree, for read-only proofs.</summary>
        public Dictionary<string, (long Length, long LastWriteTicks)> Snapshot()
        {
            var snapshot = new Dictionary<string, (long, long)>(StringComparer.OrdinalIgnoreCase);
            foreach (string file in Directory.GetFiles(Root, "*", SearchOption.AllDirectories))
            {
                FileInfo info = new(file);
                snapshot[file[Root.Length..].Replace('\\', '/')] = (info.Length, info.LastWriteTimeUtc.Ticks);
            }

            return snapshot;
        }

        public void Dispose()
        {
            try
            {
                if (Directory.Exists(Root))
                    Directory.Delete(Root, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // A leftover temp directory is not worth failing a test over.
            }
        }

        /// <summary>
        /// The same structurally-real language file the AppCore suite builds: magic 0xFFFFFFBB,
        /// version 3, counted entries, the uVar7 audio anchor immediately after the string pool,
        /// UTF-16 text pool, ASCII audio-name pool.
        /// </summary>
        private static byte[] BuildLanguageFile(params (string Text, string? Audio)[] entries)
        {
            var textPool = new List<byte>();
            var audioPool = new List<byte>();
            var textOffsetsInWords = new List<uint>();
            var audioOffsets = new List<uint>();

            foreach ((string text, string? audio) in entries)
            {
                textOffsetsInWords.Add((uint)(textPool.Count / 2));
                textPool.AddRange(Encoding.Unicode.GetBytes(text));
                textPool.AddRange(new byte[] { 0, 0 });

                if (audio is null)
                {
                    audioOffsets.Add(0xFFFFFFFF);
                }
                else
                {
                    audioOffsets.Add((uint)audioPool.Count);
                    audioPool.AddRange(Encoding.ASCII.GetBytes(audio));
                    audioPool.Add(0);
                }
            }

            int count = entries.Length;
            const int entriesOffset = 0x0C;
            int uvar7Offset = entriesOffset + (count * 0x0C);
            int textPoolOffset = uvar7Offset + 4;

            int anchor = textPoolOffset + textPool.Count;
            uint uvar7 = (uint)(anchor - (count * 0x0C));

            var file = new List<byte>();
            file.AddRange(BitConverter.GetBytes(0xFFFFFFBBu));
            file.AddRange(BitConverter.GetBytes(3u));
            file.AddRange(BitConverter.GetBytes((uint)count));

            for (int index = 0; index < count; index++)
            {
                file.AddRange(BitConverter.GetBytes((uint)(0x1000 + index)));
                file.AddRange(BitConverter.GetBytes(textOffsetsInWords[index]));
                file.AddRange(BitConverter.GetBytes(audioOffsets[index]));
            }

            file.AddRange(BitConverter.GetBytes(uvar7));
            file.AddRange(textPool);
            file.AddRange(new byte[0x10]);
            file.AddRange(BitConverter.GetBytes((uint)audioPool.Count));
            file.AddRange(audioPool);

            return file.ToArray();
        }
    }

    /// <summary>
    /// Pins detection to nothing so the no-installation path is deterministic even on a machine
    /// that has a real game installed. Restores both variables on dispose; the CLI collection is
    /// serialized, so nothing else reads them mid-test.
    /// </summary>
    internal sealed class DetectionPin : IDisposable
    {
        private const string CandidatesVariable = "ONSLAUGHT_GAME_DIR_CANDIDATES";
        private const string SteamRootsVariable = "ONSLAUGHT_STEAM_ROOT_CANDIDATES";

        private readonly string? _previousCandidates;
        private readonly string? _previousSteamRoots;

        public DetectionPin(string nowhere)
        {
            _previousCandidates = Environment.GetEnvironmentVariable(CandidatesVariable);
            _previousSteamRoots = Environment.GetEnvironmentVariable(SteamRootsVariable);
            Environment.SetEnvironmentVariable(CandidatesVariable, nowhere);
            Environment.SetEnvironmentVariable(SteamRootsVariable, nowhere);
        }

        public void Dispose()
        {
            Environment.SetEnvironmentVariable(CandidatesVariable, _previousCandidates);
            Environment.SetEnvironmentVariable(SteamRootsVariable, _previousSteamRoots);
        }
    }

    /// <summary>
    /// Media parity through the CLI: the same catalog, mission names, and voice-line transcripts
    /// the GUI Media page shows, reached quietly through the standard verb tree. Every behaviour
    /// below was pinned before implementation existed - the RED run of this file is the proof
    /// that the CLI could not do this.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class CliMediaVerbTests
    {
        private const string Transcript = "Hawk, Billy! What are you two doing?";

        /// <summary>The fixture every happy-path test shares: three audio, five video, one language file.</summary>
        private static MediaGameTree NewPopulatedTree()
        {
            var tree = new MediaGameTree();
            tree.WriteFile(@"data\Music\battle_theme (Master).ogg");
            tree.WriteFile(@"data\sounds\english\MessageBox\110_arrival.ogg");
            tree.WriteFile(@"data\sounds\english\MessageBox\512_TATIANA_NEW_1.ogg");
            tree.WriteFile(@"data\video\OpeningFMV.vid");
            tree.WriteFile(@"data\video\02.vid");
            tree.WriteFile(@"data\video\cutscenes\03.vid");
            tree.WriteFile(@"data\video\briefings\PC_101_exact.vid");
            tree.WriteFile(@"data\video\briefings\PC_110_exact.vid");
            tree.WriteLanguageFile(
                ("1.10 - Blackout", null),
                (Transcript, "512_TATIANA_NEW_1"),
                ("A line with no recording", null));
            return tree;
        }

        [Fact]
        public void ListJsonReportsBothSectionsWithNamesGroupsTranscriptsAndRelativeLabelsOnly()
        {
            using var tree = NewPopulatedTree();

            CliRun run = Cli.Run("media", "list", "--game-dir", tree.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement envelope = run.Envelope();
            Assert.True(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("media.list", envelope.GetProperty("command").GetString());

            JsonElement data = envelope.GetProperty("data");
            Assert.Equal(3, data.GetProperty("audioCount").GetInt32());
            Assert.Equal(5, data.GetProperty("videoCount").GetInt32());

            var audio = ByName(data.GetProperty("audio"));

            JsonElement music = audio["battle theme"];
            Assert.Equal("Music", music.GetProperty("groupName").GetString());
            Assert.Equal(0, music.GetProperty("groupSortOrder").GetInt32());
            Assert.Equal(string.Empty, music.GetProperty("durationLabel").GetString());
            Assert.Equal("data/Music/battle_theme (Master).ogg", music.GetProperty("file").GetString());
            Assert.False(music.TryGetProperty("transcript", out _));

            // The game's own name for mission 110 replaces "Mission 110" - the join is the point.
            JsonElement arrival = audio["110_arrival"];
            Assert.Equal("1.10 - Blackout", arrival.GetProperty("groupName").GetString());
            Assert.Equal(110, arrival.GetProperty("groupSortOrder").GetInt32());

            // The words travel with the recording, joined by the audio name in the text table.
            JsonElement spoken = audio["512_TATIANA_NEW_1"];
            Assert.Equal(Transcript, spoken.GetProperty("transcript").GetString());
            Assert.Equal("Mission 512", spoken.GetProperty("groupName").GetString());

            var video = ByName(data.GetProperty("video"));
            JsonElement opening = video["Opening Cinematic"];
            Assert.Equal("Main Videos", opening.GetProperty("sectionName").GetString());
            Assert.Equal("data/video/OpeningFMV.vid", opening.GetProperty("file").GetString());

            JsonElement cutscene = video["Cutscene 03"];
            Assert.Equal("Cutscenes", cutscene.GetProperty("sectionName").GetString());
            Assert.Equal("data/video/cutscenes/03.vid", cutscene.GetProperty("file").GetString());

            // Briefing 110 resolves through the game's own name for 1.10 - the same join; a
            // briefing whose mission the language file does not name keeps its number instead.
            JsonElement briefing = video["1.10 - Blackout"];
            Assert.Equal("Mission Briefings / Episode 1", briefing.GetProperty("sectionName").GetString());
            JsonElement numberedBriefing = video["Mission 101"];
            Assert.Equal("Mission Briefings / Episode 1", numberedBriefing.GetProperty("sectionName").GetString());

            // Disclosure rule: no absolute path anywhere in the document.
            Assert.DoesNotContain(tree.Root, run.StdOut, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(":\\", run.StdOut, StringComparison.Ordinal);
        }

        [Fact]
        public void ListTextModePrintsABannerGroupedSectionsAndNeverAPath()
        {
            using var tree = NewPopulatedTree();

            CliRun run = Cli.Run("media", "list", "--game-dir", tree.Root);

            Assert.Equal(0, run.ExitCode);
            Assert.Empty(run.StdErr);

            string[] lines = run.StdOut.Split('\n').Select(line => line.TrimEnd('\r')).ToArray();
            Assert.Contains("Onslaught Career Editor - Media Catalog", lines);

            string printed = string.Join("\n", lines);
            Assert.Contains("Audio (3)", printed);
            Assert.Contains("Video (5)", printed);
            Assert.Contains("battle theme", printed);
            Assert.Contains("1.10 - Blackout", printed);
            Assert.Contains(Transcript, printed);
            Assert.Contains("Cutscene 03", printed);

            // Default output names media, never where it lives.
            Assert.DoesNotContain(tree.Root, run.StdOut, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain(":\\", run.StdOut, StringComparison.Ordinal);
            Assert.DoesNotContain(".ogg", run.StdOut, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void TheAudioFilterLimitsOutputToTheAudioSection()
        {
            using var tree = NewPopulatedTree();

            CliRun run = Cli.Run("media", "list", "audio", "--game-dir", tree.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement data = run.Envelope().GetProperty("data");
            Assert.Equal(3, data.GetProperty("audioCount").GetInt32());
            Assert.True(data.GetProperty("audio").GetArrayLength() > 0);
            Assert.False(data.TryGetProperty("video", out _));
            Assert.False(data.TryGetProperty("videoCount", out _));
        }

        [Fact]
        public void TheVideoFilterLimitsOutputToTheVideoSection()
        {
            using var tree = NewPopulatedTree();

            CliRun run = Cli.Run("media", "list", "video", "--game-dir", tree.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement data = run.Envelope().GetProperty("data");
            Assert.Equal(5, data.GetProperty("videoCount").GetInt32());
            Assert.True(data.GetProperty("video").GetArrayLength() > 0);
            Assert.False(data.TryGetProperty("audio", out _));
            Assert.False(data.TryGetProperty("audioCount", out _));
        }

        [Fact]
        public void AnUnknownFilterWordIsAUsageErrorKeptOffStdout()
        {
            using var tree = NewPopulatedTree();

            CliRun run = Cli.Run("media", "list", "both", "--game-dir", tree.Root, "--json");

            Assert.Equal(1, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement envelope = run.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("usage", envelope.GetProperty("error").GetProperty("kind").GetString());
        }

        [Fact]
        public void WithoutAGameDirJsonEmitsAUsageEnvelopeWithGuidance()
        {
            using var scratch = new CliScratch();
            using var pin = new DetectionPin(scratch.Path_("nowhere"));

            CliRun run = Cli.Run("media", "list", "--json");

            Assert.Equal(1, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement envelope = run.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("media.list", envelope.GetProperty("command").GetString());
            Assert.Equal("usage", envelope.GetProperty("error").GetProperty("kind").GetString());

            string help = envelope.GetProperty("error").GetProperty("message").GetString() ?? "";
            foreach (JsonElement detail in envelope.GetProperty("error").GetProperty("details").EnumerateArray())
                help += "\n" + detail.GetString();
            Assert.Contains("set-game-dir", help, StringComparison.OrdinalIgnoreCase);
            Assert.Contains("--game-dir", help, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void WithoutAGameDirTextModePointsAtConfigurationOnStderr()
        {
            using var scratch = new CliScratch();
            using var pin = new DetectionPin(scratch.Path_("nowhere"));

            CliRun run = Cli.Run("media", "list");

            Assert.Equal(1, run.ExitCode);
            Assert.Empty(run.StdOut);
            Assert.Contains("set-game-dir", run.StdErr, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void ANonGameDirectoryIsADataVerdictInBothModes()
        {
            using var scratch = new CliScratch();
            string notGame = scratch.Path_("not-a-game");
            Directory.CreateDirectory(notGame);
            File.WriteAllText(Path.Combine(notGame, "readme.txt"), "just a folder");

            CliRun json = Cli.Run("media", "list", "--game-dir", notGame, "--json");

            Assert.Equal(2, json.ExitCode);
            Assert.Empty(json.StdErr);
            JsonElement envelope = json.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("media.list", envelope.GetProperty("command").GetString());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());

            CliRun text = Cli.Run("media", "list", "--game-dir", notGame);

            Assert.Equal(2, text.ExitCode);
            Assert.Empty(text.StdOut);
            Assert.Contains("Error:", text.StdErr);
        }

        [Fact]
        public void ARunNeverWritesAnythingInsideTheGameTree()
        {
            using var tree = NewPopulatedTree();
            Dictionary<string, (long Length, long LastWriteTicks)> before = tree.Snapshot();

            CliRun text = Cli.Run("media", "list", "--game-dir", tree.Root);
            CliRun json = Cli.Run("media", "list", "--game-dir", tree.Root, "--json");

            Assert.Equal(0, text.ExitCode);
            Assert.Equal(0, json.ExitCode);
            Assert.Equal(before, tree.Snapshot());
        }

        [Fact]
        public void TwoIdenticalRunsProduceByteIdenticalOutput()
        {
            using var tree = NewPopulatedTree();

            CliRun first = Cli.Run("media", "list", "--game-dir", tree.Root, "--json");
            CliRun second = Cli.Run("media", "list", "--game-dir", tree.Root, "--json");

            Assert.Equal(0, first.ExitCode);
            Assert.Equal(first.StdOut, second.StdOut);
            Assert.Equal(first.StdErr, second.StdErr);
        }

        /// <summary>
        /// The binding no-write contract: a media list that answers from default resolution must
        /// leave the app config root exactly as it found it. <see cref="AppConfig.Load"/> creates
        /// the config directory as a side effect of reading; the verb resolves through
        /// <see cref="AppConfig.LoadReadOnly"/> instead, so even a fresh nonexistent root stays
        /// nonexistent when the command ends in the usage verdict.
        /// </summary>
        [Fact]
        public void MissingGameDirDefaultResolutionLeavesAFreshConfigRootNonexistent()
        {
            string? previousRoot = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
            try
            {
                string root = Path.Combine(
                    Path.GetTempPath(), "onslaught-cli-media-configroot", Guid.NewGuid().ToString("N"));
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", root);

                using (var scratch = new CliScratch())
                using (new DetectionPin(scratch.Path_("nowhere")))
                {
                    CliRun run = Cli.Run("media", "list", "--json");

                    Assert.Equal(1, run.ExitCode);
                    Assert.Empty(run.StdErr);

                    JsonElement envelope = run.Envelope();
                    Assert.False(envelope.GetProperty("ok").GetBoolean());
                    Assert.Equal("usage", envelope.GetProperty("error").GetProperty("kind").GetString());
                }

                Assert.False(Directory.Exists(root));
                Assert.False(Directory.Exists(Path.Combine(root, "OnslaughtCareerEditor")));
            }
            finally
            {
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", previousRoot);
            }
        }

        /// <summary>
        /// Control for the regression above: an explicit --game-dir never touches configuration at
        /// all. A second fresh config root stays nonexistent while the same command succeeds.
        /// </summary>
        [Fact]
        public void ExplicitGameDirControlLeavesASecondFreshConfigRootNonexistent()
        {
            string? previousRoot = Environment.GetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT");
            try
            {
                string root = Path.Combine(
                    Path.GetTempPath(), "onslaught-cli-media-control-root", Guid.NewGuid().ToString("N"));
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", root);

                using var tree = NewPopulatedTree();
                Dictionary<string, (long Length, long LastWriteTicks)> before = tree.Snapshot();

                CliRun run = Cli.Run("media", "list", "--game-dir", tree.Root, "--json");

                Assert.Equal(0, run.ExitCode);
                Assert.Empty(run.StdErr);
                Assert.True(run.Envelope().GetProperty("ok").GetBoolean());

                Assert.False(Directory.Exists(root));
                Assert.Equal(before, tree.Snapshot());
            }
            finally
            {
                Environment.SetEnvironmentVariable("ONSLAUGHT_APP_CONFIG_ROOT", previousRoot);
            }
        }

        private static Dictionary<string, JsonElement> ByName(JsonElement array)
        {
            var byName = new Dictionary<string, JsonElement>(StringComparer.Ordinal);
            foreach (JsonElement item in array.EnumerateArray())
            {
                string name = item.GetProperty("name").GetString()
                    ?? throw new InvalidOperationException("media item without a name");
                byName.Add(name, item);
            }

            return byName;
        }
    }
}
