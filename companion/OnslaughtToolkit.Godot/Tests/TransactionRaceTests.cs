// SPDX-License-Identifier: MIT
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Linux publication-race and failure cases driven through the linked safety source's
/// internal publication hook. The hook has no production caller, option or environment
/// route, and this suite is compiled only into development builds.
/// </summary>
internal static class TransactionRaceTests
{
    internal static void Run(byte[] original, string outputDirectory, Checks check)
    {
        check.Suite("publication races");
        if (!OperatingSystem.IsLinux())
        {
            check.Fail("The publication-race cases require Linux; they did not run.");
            return;
        }
        string root = Path.Combine(outputDirectory, "publication-races");
        Directory.CreateDirectory(root);

        Race("destination appears after staging", fixture =>
        {
            byte[] competitor = original.ToArray();
            competitor[^1] ^= 1;
            ExpectRefusal(() => fixture.Publish(() => File.WriteAllBytes(fixture.Output, competitor)));
            Require(File.ReadAllBytes(fixture.Output).AsSpan().SequenceEqual(competitor), "Destination was replaced.");
            Require(Directory.GetFiles(fixture.OutputDirectory).Length == 1, "Named staging file leaked.");
        });
        Race("source changes during staging", fixture =>
        {
            byte[] changed = original.ToArray();
            changed[^1] ^= 1;
            ExpectRefusal(() => fixture.Publish(() => File.WriteAllBytes(fixture.Input, changed)));
            Require(File.ReadAllBytes(fixture.Input).AsSpan().SequenceEqual(changed), "Changed source was overwritten.");
            Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Output escaped failed staging.");
        });
        Race("same-byte source replaced during staging", fixture =>
        {
            ExpectRefusal(() => fixture.Publish(() =>
            {
                File.Move(fixture.Input, Path.Combine(fixture.Root, "displaced.bes"));
                File.WriteAllBytes(fixture.Input, original);
            }));
            Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Changed source identity was accepted.");
        });
        Race("output folder replaced during staging", fixture =>
        {
            string displaced = Path.Combine(fixture.Root, "displaced");
            ExpectRefusal(() => fixture.Publish(() =>
            {
                Directory.Move(fixture.OutputDirectory, displaced);
                Directory.CreateDirectory(fixture.OutputDirectory);
            }));
            Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Wrote into replacement directory.");
            Require(Directory.GetFileSystemEntries(displaced).Length == 0, "Unpublished staging file leaked.");
        });
        Race("atomic publication refuses a last-moment entry", fixture =>
        {
            using LinuxSaveDirectory directory = LinuxSaveDirectory.Open(fixture.OutputDirectory);
            using FileStream staged = directory.CreateUnnamed();
            staged.Write(original);
            staged.Flush(flushToDisk: true);
            directory.RequireVacant("copy.bes");
            byte[] competitor = original.ToArray();
            competitor[^1] ^= 1;
            File.WriteAllBytes(fixture.Output, competitor);
            ExpectRefusal(() => directory.Publish(staged.SafeFileHandle, "copy.bes"));
            Require(File.ReadAllBytes(fixture.Output).AsSpan().SequenceEqual(competitor), "Atomic publication clobbered a file.");
        });
        Race("failed staging leaves no named file to delete", fixture =>
        {
            ExpectRefusal(() => fixture.Publish(() => throw new IOException("Injected staging failure.")));
            Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Failed staging left a named file.");
        });

        void Race(string name, Action<Fixture> action)
        {
            try
            {
                action(new Fixture(Path.Combine(root, name.Replace(' ', '-')), original));
                check.That(true, name);
            }
            catch (Exception error)
            {
                check.Fail($"{name}: {error.Message}");
            }
        }
    }

    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void ExpectRefusal(Action action)
    {
        try { action(); }
        catch (IOException) { return; }
        throw new InvalidOperationException("Expected protected publication to refuse.");
    }

    private sealed class Fixture
    {
        private readonly byte[] _original;

        internal Fixture(string root, byte[] original)
        {
            if (Path.Exists(root)) throw new IOException("Race-test output must be new.");
            Root = root;
            Directory.CreateDirectory(root);
            Input = Path.Combine(root, "original.bes");
            _original = original;
            File.WriteAllBytes(Input, original);
            OutputDirectory = Path.Combine(root, "output");
            Directory.CreateDirectory(OutputDirectory);
            Output = Path.Combine(OutputDirectory, "copy.bes");
        }

        internal string Root { get; }
        internal string Input { get; }
        internal string OutputDirectory { get; }
        internal string Output { get; }

        internal void Publish(Action beforePublish)
        {
            using SaveLabSource source = SaveLabSource.Open(Input);
            source.Verify(_original, source.Identity);
            SaveLabFileTransaction.PublishNew(Output, source, _original, _original, source.Identity, beforePublish);
        }
    }
}
