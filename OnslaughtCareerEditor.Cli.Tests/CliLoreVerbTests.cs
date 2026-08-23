using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// Three small authored lore documents in a scratch directory, addressed by
    /// <c>--root</c>. The corpus deliberately avoids the repository's real lore
    /// corpus, any content pack, any game install, and the live campaign-section
    /// marker - so these tests measure the verb's own behaviour and nothing else.
    /// </summary>
    public sealed class LoreCorpus : IDisposable
    {
        public const string HitWord = "skyship";

        public const string FirstDocRelative = "lore/alpha.md";
        public const string SecondDocRelative = "lore/beta.md";
        public const string ThirdDocRelative = "lore/gamma.md";

        private static readonly string RootBase =
            Path.Combine(Path.GetTempPath(), "onslaught-cli-lore");

        private readonly List<string> _externalDirectories = new();

        public LoreCorpus()
        {
            Root = Path.Combine(RootBase, Guid.NewGuid().ToString("N"));
            WriteDoc(
                FirstDocRelative,
                "# Alpha Document",
                "",
                $"The {HitWord} patrols the northern channel.",
                "",
                "## Second Heading",
                "",
                $"A second mention of the {HitWord} appears here.");
            WriteDoc(
                SecondDocRelative,
                "# Beta Document",
                "",
                $"Only one {HitWord} lives in this file.");
            WriteDoc(
                ThirdDocRelative,
                "# Gamma Document",
                "",
                "Nothing relevant is written in this document at all.");
        }

        public string Root { get; }

        public void Dispose()
        {
            DeleteScratchDirectory(Root);
            foreach (string directory in _externalDirectories)
                DeleteScratchDirectory(directory);
        }

        private void WriteDoc(params string[] lines)
        {
            string path = Path.Combine(Root, lines[0].Replace('/', Path.DirectorySeparatorChar));
            Directory.CreateDirectory(Path.GetDirectoryName(path)!);
            File.WriteAllLines(path, lines[1..]);
        }

        /// <summary>
        /// A minimal but fully valid one-document content pack: real index + content files with a
        /// matching SHA-256 and byte length, exactly the format <c>LoreBrowserService</c> loads.
        /// </summary>
        public string WritePack()
        {
            const string id = "packed-doc-1";
            const string relativePath = "book/packed-doc.md";
            string content = "# Packed Document\n\nThe packed body text.\n";
            byte[] contentBytes = Encoding.UTF8.GetBytes(content);
            string sha256 = Convert.ToHexString(SHA256.HashData(contentBytes)).ToLowerInvariant();

            string packDirectory = Path.Combine(Root, "lore-pack");
            Directory.CreateDirectory(packDirectory);
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.index.json"),
                JsonSerializer.Serialize(new
                {
                    schema = "onslaught-lore-pack.v1",
                    documentCount = 1,
                    documents = new[] { new { id, relativePath, sha256, byteLength = contentBytes.Length } },
                }));
            File.WriteAllText(
                Path.Combine(packDirectory, "onslaught-lore.v1.jsonl"),
                JsonSerializer.Serialize(new { id, relativePath, title = "Packed Document", sha256, byteLength = contentBytes.Length, content }) + "\n");
            return "lore-pack://" + id;
        }

        /// <summary>An authored file outside the corpus root. It must never be readable via lore.</summary>
        public string WriteExternalFile()
        {
            string directory = Path.Combine(Path.GetTempPath(), "onslaught-cli-lore-external", Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(directory);
            _externalDirectories.Add(directory);
            string path = Path.Combine(directory, "external-not-in-lore.md");
            File.WriteAllText(path, ExternalFileMarker);
            return path;
        }

        public const string ExternalFileMarker = "REVIEW_ONLY_SECRET_MARKER_9f32b7";

        private static void DeleteScratchDirectory(string directory)
        {
            try
            {
                if (Directory.Exists(directory))
                    Directory.Delete(directory, recursive: true);
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                // A leftover temp directory is not worth failing a test over.
            }
        }
    }

    /// <summary>
    /// Lore parity through the CLI: the same read/search/show capability the GUI
    /// reader has had all along, reached quietly through the standard verb tree.
    /// Every behaviour below was pinned before implementation existed - the RED
    /// run of this file is the proof that the CLI could not do this.
    /// </summary>
    [Collection(CliCollection.Name)]
    public class CliLoreVerbTests
    {
        [Fact]
        public void SearchFindsHitsInDeterministicIndexOrder()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "search", LoreCorpus.HitWord, "--root", corpus.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement data = run.Envelope().GetProperty("data");
            Assert.Equal(LoreCorpus.HitWord, data.GetProperty("query").GetString());
            Assert.Equal(3, data.GetProperty("documentsSearched").GetInt32());
            Assert.Equal(3, data.GetProperty("hitCount").GetInt32());

            JsonElement.ArrayEnumerator hits = data.GetProperty("hits").EnumerateArray();

            hits.MoveNext();
            Assert.Equal(LoreCorpus.FirstDocRelative, hits.Current.GetProperty("document").GetString());
            Assert.Equal("Alpha Document", hits.Current.GetProperty("documentTitle").GetString());
            Assert.Equal("alpha-document", hits.Current.GetProperty("sectionAnchor").GetString());
            Assert.Equal("Alpha Document", hits.Current.GetProperty("sectionHeading").GetString());
            Assert.Equal(2, hits.Current.GetProperty("occurrenceCount").GetInt32());
            Assert.Contains(LoreCorpus.HitWord, hits.Current.GetProperty("snippet").GetProperty("matched").GetString());

            hits.MoveNext();
            Assert.Equal(LoreCorpus.FirstDocRelative, hits.Current.GetProperty("document").GetString());
            Assert.Equal("second-heading", hits.Current.GetProperty("sectionAnchor").GetString());

            hits.MoveNext();
            Assert.Equal(LoreCorpus.SecondDocRelative, hits.Current.GetProperty("document").GetString());
            Assert.Equal("Beta Document", hits.Current.GetProperty("documentTitle").GetString());
            Assert.False(hits.MoveNext());
        }

        [Fact]
        public void SearchIsByteIdenticalAcrossRunsInBothModes()
        {
            using var corpus = new LoreCorpus();
            string[] textArgs = { "lore", "search", LoreCorpus.HitWord, "--root", corpus.Root };
            string[] jsonArgs = { "lore", "search", LoreCorpus.HitWord, "--root", corpus.Root, "--json" };

            CliRun textFirst = Cli.Run(textArgs);
            CliRun textSecond = Cli.Run(textArgs);
            Assert.Equal(0, textFirst.ExitCode);
            Assert.Equal(textFirst.StdOut, textSecond.StdOut);
            Assert.Equal(textFirst.StdErr, textSecond.StdErr);

            CliRun jsonFirst = Cli.Run(jsonArgs);
            CliRun jsonSecond = Cli.Run(jsonArgs);
            Assert.Equal(0, jsonFirst.ExitCode);
            Assert.Equal(jsonFirst.StdOut, jsonSecond.StdOut);
            Assert.Empty(jsonFirst.StdErr);
        }

        [Fact]
        public void SearchWithNoHitsIsASuccessfulEmptyAnswer()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "search", "word-nowhere-in-the-corpus", "--root", corpus.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            JsonElement envelope = run.Envelope();
            Assert.True(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("lore.search", envelope.GetProperty("command").GetString());
            Assert.Equal(0, envelope.GetProperty("data").GetProperty("hitCount").GetInt32());
        }

        [Fact]
        public void SearchWithoutAQueryIsAUsageErrorKeptOffStdout()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "search", "--root", corpus.Root);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("query", run.StdErr, StringComparison.OrdinalIgnoreCase);
            Assert.DoesNotContain("Error:", run.StdOut);
        }

        [Fact]
        public void SearchUsageErrorUnderJsonEmitsTheEnvelopeOnStdoutAlone()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "search", "--json");

            Assert.Equal(1, run.ExitCode);
            Assert.Empty(run.StdErr);
            JsonElement envelope = run.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("usage", envelope.GetProperty("error").GetProperty("kind").GetString());
        }

        [Fact]
        public void SearchFromALocationWithoutLoreContentIsAUsageError()
        {
            string bare = Path.Combine(Path.GetTempPath(), "onslaught-cli-lore", Guid.NewGuid().ToString("N"), "empty");
            Directory.CreateDirectory(bare);
            try
            {
                CliRun run = Cli.Run("lore", "search", LoreCorpus.HitWord, "--root", bare);

                Assert.Equal(1, run.ExitCode);
                Assert.Contains("lore", run.StdErr, StringComparison.OrdinalIgnoreCase);
            }
            finally
            {
                Directory.Delete(Path.GetDirectoryName(bare)!, recursive: true);
            }
        }

        [Fact]
        public void ShowPrintsTitleOutlineAndPlainText()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "show", LoreCorpus.FirstDocRelative, "--root", corpus.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Empty(run.StdErr);

            JsonElement data = run.Envelope().GetProperty("data");
            Assert.Equal("Alpha Document", data.GetProperty("title").GetString());
            Assert.True(data.GetProperty("isMarkdown").GetBoolean());
            Assert.True(data.GetProperty("blockCount").GetInt32() >= 4);

            JsonElement.ArrayEnumerator outline = data.GetProperty("outline").EnumerateArray();
            outline.MoveNext();
            Assert.Equal(1, outline.Current.GetProperty("level").GetInt32());
            Assert.Equal("Alpha Document", outline.Current.GetProperty("text").GetString());
            outline.MoveNext();
            Assert.Equal(2, outline.Current.GetProperty("level").GetInt32());
            Assert.Equal("second-heading", outline.Current.GetProperty("id").GetString());

            string text = data.GetProperty("text").GetString() ?? "";
            Assert.Contains("patrols the northern channel", text);
            Assert.Contains("appears here", text);
            Assert.DoesNotContain("#", text);
        }

        [Fact]
        public void ShowOfAnUnknownDocumentIsADataVerdict()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "show", "lore/nope.md", "--root", corpus.Root, "--json");

            Assert.Equal(2, run.ExitCode);
            JsonElement envelope = run.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("lore.show", envelope.GetProperty("command").GetString());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());
        }

        [Fact]
        public void ShowWithoutADocumentIsAUsageError()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "show", "--root", corpus.Root);

            Assert.Equal(1, run.ExitCode);
            Assert.Contains("document", run.StdErr, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void ShowAcceptsADotRelativeIndexedPath()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "show", "./lore/beta.md", "--root", corpus.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Equal("Beta Document", run.Envelope().GetProperty("data").GetProperty("title").GetString());
        }

        [Fact]
        public void ShowOfAnExistingFileOutsideTheRootViaCwdRelativeSpellingIsRejectedWithoutReadingIt()
        {
            using var corpus = new LoreCorpus();
            string externalPath = corpus.WriteExternalFile();

            // A spelling relative to the process working directory: it names a real file, but
            // membership in the selected library is decided by the index, not by File.Exists.
            string cwdRelative = Path.GetRelativePath(Directory.GetCurrentDirectory(), externalPath);

            CliRun run = Cli.Run("lore", "show", cwdRelative, "--root", corpus.Root, "--json");

            Assert.Equal(2, run.ExitCode);
            Assert.Empty(run.StdErr);
            JsonElement envelope = run.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());
            Assert.DoesNotContain(LoreCorpus.ExternalFileMarker, run.StdOut);
        }

        [Fact]
        public void ShowOfAnExistingFileOutsideTheRootByAbsolutePathIsRejectedWithoutReadingIt()
        {
            using var corpus = new LoreCorpus();
            string externalPath = corpus.WriteExternalFile();

            CliRun absolute = Cli.Run("lore", "show", externalPath, "--root", corpus.Root, "--json");

            Assert.Equal(2, absolute.ExitCode);
            Assert.Empty(absolute.StdErr);
            JsonElement envelope = absolute.Envelope();
            Assert.False(envelope.GetProperty("ok").GetBoolean());
            Assert.Equal("data", envelope.GetProperty("error").GetProperty("kind").GetString());
            Assert.DoesNotContain(LoreCorpus.ExternalFileMarker, absolute.StdOut);

            // The same verdict in text mode: nothing on stdout, no content on stderr.
            CliRun textMode = Cli.Run("lore", "show", externalPath, "--root", corpus.Root);

            Assert.Equal(2, textMode.ExitCode);
            Assert.Empty(textMode.StdOut);
            Assert.DoesNotContain(LoreCorpus.ExternalFileMarker, textMode.StdErr);
        }

        [Fact]
        public void ShowOfAnExistingFileInsideButNotIndexedByTheRootIsRejectedWithoutReadingIt()
        {
            using var corpus = new LoreCorpus();

            // Inside --root yet outside the index: still not a library document. The reviewer's
            // literal reproduction spelled it relative to the root.
            string smuggled = Path.Combine(corpus.Root, "smuggled.md");
            File.WriteAllText(smuggled, LoreCorpus.ExternalFileMarker);

            CliRun fromRoot = Cli.Run("lore", "show", "smuggled.md", "--root", corpus.Root, "--json");

            Assert.Equal(2, fromRoot.ExitCode);
            Assert.DoesNotContain(LoreCorpus.ExternalFileMarker, fromRoot.StdOut);

            CliRun absolute = Cli.Run("lore", "show", smuggled, "--root", corpus.Root, "--json");

            Assert.Equal(2, absolute.ExitCode);
            Assert.DoesNotContain(LoreCorpus.ExternalFileMarker, absolute.StdOut);
        }

        [Fact]
        public void ShowStillAcceptsAnIndexedDocumentByItsAbsoluteKey()
        {
            using var corpus = new LoreCorpus();
            string absoluteKey = Path.Combine(corpus.Root, "lore", "beta.md");

            CliRun run = Cli.Run("lore", "show", absoluteKey, "--root", corpus.Root, "--json");

            Assert.Equal(0, run.ExitCode);
            Assert.Equal("Beta Document", run.Envelope().GetProperty("data").GetProperty("title").GetString());
        }

        [Fact]
        public void ShowAcceptsBothAPackUriAndItsIndexedRelativeKey()
        {
            using var corpus = new LoreCorpus();
            string packedKey = corpus.WritePack();

            CliRun uri = Cli.Run("lore", "show", packedKey, "--root", corpus.Root, "--json");

            Assert.Equal(0, uri.ExitCode);
            JsonElement uriData = uri.Envelope().GetProperty("data");
            Assert.Equal("Packed Document", uriData.GetProperty("title").GetString());
            Assert.Contains("packed body text", uriData.GetProperty("text").GetString());

            CliRun relative = Cli.Run("lore", "show", "book/packed-doc.md", "--root", corpus.Root, "--json");

            Assert.Equal(0, relative.ExitCode);
            Assert.Equal("Packed Document", relative.Envelope().GetProperty("data").GetProperty("title").GetString());
        }

        [Fact]
        public void SearchReadsTheIndexedPack()
        {
            using var corpus = new LoreCorpus();
            corpus.WritePack();

            CliRun search = Cli.Run("lore", "search", "packed", "--root", corpus.Root, "--json");

            Assert.Equal(0, search.ExitCode);
            Assert.True(search.Envelope().GetProperty("data").GetProperty("hitCount").GetInt32() > 0);
        }

        [Fact]
        public void ShowRejectsARealFileOutsideThePackWithoutReadingIt()
        {
            using var corpus = new LoreCorpus();
            corpus.WritePack();
            string externalPath = corpus.WriteExternalFile();

            CliRun rejected = Cli.Run("lore", "show", externalPath, "--root", corpus.Root, "--json");

            Assert.Equal(2, rejected.ExitCode);
            Assert.Empty(rejected.StdErr);
            Assert.DoesNotContain(LoreCorpus.ExternalFileMarker, rejected.StdOut);
        }

        [Fact]
        public void ShowTextModePrintsTitleOutlineThenBodyLines()
        {
            using var corpus = new LoreCorpus();

            CliRun run = Cli.Run("lore", "show", LoreCorpus.FirstDocRelative, "--root", corpus.Root);

            Assert.Equal(0, run.ExitCode);
            string[] lines = run.StdOut.Split('\n').Select(line => line.TrimEnd('\r')).ToArray();
            int titleIndex = Array.IndexOf(lines, "Alpha Document");
            Assert.True(titleIndex >= 0, "text mode must start with the document title");
            Assert.Equal("==============", lines[titleIndex + 1]);

            // Outline between title and body: heading text plus its anchor.
            string printed = string.Join("\n", lines);
            Assert.Contains("Alpha Document  (#alpha-document)", printed);
            Assert.Contains("Second Heading  (#second-heading)", printed);

            // Body: one output line per source line, not one collapsed paragraph.
            Assert.Contains("The skyship patrols the northern channel.", lines);
            Assert.Contains("A second mention of the skyship appears here.", lines);
        }
    }
}
