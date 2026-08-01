using System.Text.Json;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.Cli.Tests
{
    /// <summary>
    /// These tests redirect the app-owned config root to a temp directory and therefore mutate a
    /// process-wide environment variable. Running them in parallel with each other would let one test's
    /// root leak into another's, so the whole suite is serialized.
    /// </summary>
    [CollectionDefinition(Name, DisableParallelization = true)]
    public sealed class CliCollection
    {
        public const string Name = "CLI invocation";
    }

    /// <summary>
    /// Runs the CLI in-process with its output captured.
    ///
    /// This is why <see cref="Program.Run"/> takes writers rather than reaching for
    /// <see cref="Console"/>: spawning a process per assertion would make pinning verb routing and the
    /// exit-code split slow enough to skip, and the behaviours below are exactly the ones that must not
    /// be allowed to drift.
    /// </summary>
    public sealed record CliRun(int ExitCode, string StdOut, string StdErr)
    {
        /// <summary>Parse stdout as the JSON envelope. Fails loudly when stdout is not pure JSON.</summary>
        public JsonElement Envelope()
        {
            Assert.False(
                string.IsNullOrWhiteSpace(StdOut),
                $"Expected a JSON envelope on stdout but it was empty. stderr was: {StdErr}");

            try
            {
                return JsonDocument.Parse(StdOut).RootElement.Clone();
            }
            catch (JsonException ex)
            {
                throw new Xunit.Sdk.XunitException(
                    $"stdout was not parseable JSON ({ex.Message}). Under --json nothing else may be written to stdout.\n" +
                    $"stdout was:\n{StdOut}");
            }
        }
    }

    public static class Cli
    {
        public static CliRun Run(params string[] args)
        {
            var output = new StringWriter();
            var error = new StringWriter();
            int exitCode = Program.Run(args, output, error);
            return new CliRun(exitCode, output.ToString(), error.ToString());
        }
    }

    /// <summary>
    /// A scratch directory plus a redirected app config root, so safe-copy and patch verbs operate on a
    /// throwaway workspace instead of the developer's real one.
    /// </summary>
    public sealed class CliScratch : IDisposable
    {
        private const string ConfigRootVariable = "ONSLAUGHT_APP_CONFIG_ROOT";

        private readonly string? _previousConfigRoot;

        public CliScratch()
        {
            Root = Path.Combine(Path.GetTempPath(), "onslaught-cli-tests", Guid.NewGuid().ToString("N"));
            Directory.CreateDirectory(Root);

            ConfigRoot = Path.Combine(Root, "config");
            Directory.CreateDirectory(ConfigRoot);

            _previousConfigRoot = Environment.GetEnvironmentVariable(ConfigRootVariable);
            Environment.SetEnvironmentVariable(ConfigRootVariable, ConfigRoot);
        }

        public string Root { get; }

        public string ConfigRoot { get; }

        public string Path_(string relative) => Path.Combine(Root, relative);

        /// <summary>
        /// A file that is deliberately NOT a save. It exists only for refusals that fire before anything
        /// is parsed - argument contradictions, in-place writes, path containment - so no test here ever
        /// depends on hand-built save bytes.
        /// </summary>
        public string NonSaveFixture(string name, string contents = "this is not a Battle Engine Aquila save")
        {
            string path = Path_(name);
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(path)!);
            File.WriteAllText(path, contents);
            return path;
        }

        /// <summary>
        /// A real retail career save copied from the machine's own installation, or null when this
        /// machine has none. Saves are never synthesized: a test that needs valid bytes either gets real
        /// ones or does not run.
        /// </summary>
        public string? TryCopyRealBaselineSave(string name)
        {
            string? gameDir = AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
            if (gameDir is null)
                return null;

            SaveFileInfo? baseline = AppConfig.FindSaveFiles(gameDir)
                .FirstOrDefault(save => save.IsValid &&
                                        save.Path.EndsWith(".bes", StringComparison.OrdinalIgnoreCase));
            if (baseline is null)
                return null;

            string destination = Path_(name);
            Directory.CreateDirectory(System.IO.Path.GetDirectoryName(destination)!);
            File.Copy(baseline.Path, destination, overwrite: true);
            return destination;
        }

        public void Dispose()
        {
            Environment.SetEnvironmentVariable(ConfigRootVariable, _previousConfigRoot);
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
    }
}
