// SPDX-License-Identifier: MIT
using Godot;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// Headless entry for every companion contract:
/// <c>--script res://Tests/CompanionTestRunner.cs -- --fixture=OWNED_COPY --output-dir=FRESH_DIR</c>.
/// The launcher supplies an invocation-owned copy of the one tracked career fixture.
/// </summary>
public partial class CompanionTestRunner : SceneTree
{
    public override void _Initialize() => _ = RunAsync();

    private async Task RunAsync()
    {
        int exitCode = 1;
        try
        {
            string fixture = "", output = "";
            foreach (string argument in OS.GetCmdlineUserArgs())
            {
                if (argument.StartsWith("--fixture=", StringComparison.Ordinal)) fixture = argument["--fixture=".Length..];
                if (argument.StartsWith("--output-dir=", StringComparison.Ordinal)) output = argument["--output-dir=".Length..];
            }
            if (fixture.Length == 0 || output.Length == 0 || !Directory.Exists(output))
            {
                GD.PrintErr("Owned --fixture and an existing --output-dir are required.");
                exitCode = 2;
                return;
            }
            byte[] original = File.ReadAllBytes(fixture);
            Checks check = new();
            check.Suite("runner");
            check.That(original.Length == 10004, "runner supplied an owned real career baseline");
            if (original.Length == 10004)
            {
                CareerSaveTests.Run(original, check);
                MediaCatalogTests.Run(output, check);
                ProtectedFilesTests.Run(original, output, check);
                TransactionRaceTests.Run(original, output, check);
                await GameFolderTests.RunAsync(original, output, check);
                GameTextTests.Run(output, check);
                InstallTests.Run(original, output, check);
                await CompanionUiTests.RunAsync(this, fixture, output, original, check);
                check.That(File.ReadAllBytes(fixture).AsSpan().SequenceEqual(original), "the owned fixture copy is restored");
            }
            foreach (string failure in check.Failures) GD.PrintErr("FAIL: " + failure);
            GD.Print($"COMPANION_TESTS: {check.Failures.Count} failures in {check.Count} checks; career codec, media catalog, " +
                "protected files, publication races, game folder and the code-built interface executed.");
            exitCode = check.Failures.Count == 0 ? 0 : 1;
        }
        catch (Exception error)
        {
            GD.PrintErr("COMPANION_TESTS stopped unexpectedly: " + error);
            exitCode = 1;
        }
        finally
        {
            Quit(exitCode);
        }
    }
}
