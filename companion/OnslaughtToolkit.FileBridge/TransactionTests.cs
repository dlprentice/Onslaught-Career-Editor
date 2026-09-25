using System.Text.Json;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.FileBridge;

// A separate test executable links the same safety files. No fault-injection
// option, environment variable or test command exists in the production bridge.
internal static class TransactionTests
{
    private static int Main(string[] arguments)
    {
        if (arguments.Length != 2 || !OperatingSystem.IsLinux()) return 2;
        byte[] original = File.ReadAllBytes(arguments[0]);
        string root = Path.GetFullPath(arguments[1]);
        if (original.Length != BesFilePatcher.EXPECTED_FILE_SIZE || !Directory.Exists(root)) return 2;
        List<string> passed = [];
        try
        {
            Check("destination_appears_after_staging", fixture =>
            {
                byte[] competitor = original.ToArray();
                competitor[^1] ^= 1;
                ExpectRefusal(() => fixture.Publish(() => File.WriteAllBytes(fixture.Output, competitor)));
                Require(File.ReadAllBytes(fixture.Output).AsSpan().SequenceEqual(competitor), "Destination was replaced.");
                Require(Directory.GetFiles(fixture.OutputDirectory).Length == 1, "Named staging file leaked.");
            });
            Check("source_changes_during_staging", fixture =>
            {
                byte[] changed = original.ToArray();
                changed[^1] ^= 1;
                ExpectRefusal(() => fixture.Publish(() => File.WriteAllBytes(fixture.Input, changed)));
                Require(File.ReadAllBytes(fixture.Input).AsSpan().SequenceEqual(changed), "Changed source was overwritten.");
                Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Output escaped failed staging.");
            });
            Check("same_bytes_source_replaced_during_staging", fixture =>
            {
                ExpectRefusal(() => fixture.Publish(() =>
                {
                    File.Move(fixture.Input, Path.Combine(fixture.Root, "displaced.bes"));
                    File.WriteAllBytes(fixture.Input, original);
                }));
                Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Changed source identity was accepted.");
            });
            Check("output_directory_replaced_during_staging", fixture =>
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
            Check("atomic_publication_refuses_last_moment_entry", fixture =>
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
            Check("failed_staging_has_no_named_file_to_delete", fixture =>
            {
                ExpectRefusal(() => fixture.Publish(() => throw new IOException("Injected staging failure.")));
                Require(Directory.GetFileSystemEntries(fixture.OutputDirectory).Length == 0, "Failed staging left a named file.");
            });
            Console.WriteLine(JsonSerializer.Serialize(new { ok = true, passed }));
            return 0;
        }
        catch (Exception error)
        {
            Console.WriteLine(JsonSerializer.Serialize(new { ok = false, passed, message = error.Message }));
            return 1;
        }

        void Check(string name, Action<Fixture> action)
        {
            Fixture fixture = new(Path.Combine(root, name), original);
            action(fixture);
            passed.Add(name);
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
            Root = root;
            if (Directory.Exists(root)) throw new IOException("Race-test output must be new.");
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
