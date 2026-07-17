// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text;
using System.Text.Json;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Headless;

public static class HeadlessApplication
{
    private const long MaximumTapeBytes = 8 * 1024 * 1024;
    private const long MaximumReplaySteps = 100_000;
    private const string BuiltInTapeFileName = "first-flight.v1.json";

    private sealed record Options(
        string TapePath,
        string? ExpectedTraceHash,
        int RepeatCount);

    private sealed record VerificationExpectation(
        string? TraceHash,
        string? FinalStateHash,
        string Source);

    public static int Run(string[] args, TextWriter output, TextWriter error)
    {
        ArgumentNullException.ThrowIfNull(args);
        ArgumentNullException.ThrowIfNull(output);
        ArgumentNullException.ThrowIfNull(error);

        try
        {
            if (args.Contains("--help", StringComparer.Ordinal))
            {
                PrintHelp(output);
                return 0;
            }

            Options options = ParseOptions(args);
            CommandTape tape = CommandTapeCodec.Deserialize(ReadTape(options.TapePath));
            ValidateWorkBudget(tape, options.RepeatCount);
            VerificationExpectation expectation = ResolveExpectation(options, tape);

            ReplayResult first = ReplayRunner.Run(tape);
            for (int run = 1; run < options.RepeatCount; run++)
            {
                ReplayResult repeated = ReplayRunner.Run(tape);
                if (!string.Equals(first.TraceHash, repeated.TraceHash, StringComparison.Ordinal) ||
                    !string.Equals(first.FinalStateHash, repeated.FinalStateHash, StringComparison.Ordinal))
                {
                    error.WriteLine("Determinism failure: repeated replay produced different hashes.");
                    return 3;
                }
            }

            bool traceHashChecked = expectation.TraceHash is not null;
            bool? traceHashVerified = traceHashChecked
                ? string.Equals(first.TraceHash, expectation.TraceHash, StringComparison.OrdinalIgnoreCase)
                : null;
            bool finalStateHashChecked = expectation.FinalStateHash is not null;
            bool? finalStateHashVerified = finalStateHashChecked
                ? string.Equals(
                    first.FinalStateHash,
                    expectation.FinalStateHash,
                    StringComparison.OrdinalIgnoreCase)
                : null;
            var summary = new
            {
                schemaVersion = "onslaught-rebuild-headless-result.v1",
                tape = tape.Name,
                ticks = first.FinalState.Tick,
                repeats = options.RepeatCount,
                traceHash = first.TraceHash,
                finalStateHash = first.FinalStateHash,
                expectedTraceHash = expectation.TraceHash,
                expectedFinalStateHash = expectation.FinalStateHash,
                verificationSource = expectation.Source,
                traceHashChecked,
                traceHashVerified,
                finalStateHashChecked,
                finalStateHashVerified,
                mode = first.FinalState.Mode.ToString(),
                energy = first.FinalState.Energy,
                shield = first.FinalState.Shield,
                hull = first.FinalState.Hull,
                targetsDestroyed = first.FinalState.TargetsDestroyed,
                activeProjectiles = first.FinalState.Projectiles.Count,
            };
            output.WriteLine(JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }));

            if (traceHashVerified == false)
            {
                error.WriteLine("Replay trace hash did not match the expected value.");
                return 2;
            }

            if (finalStateHashVerified == false)
            {
                error.WriteLine("Final state hash did not match the expected value.");
                return 2;
            }

            return 0;
        }
        catch (Exception exception) when (
            exception is ArgumentException or IOException or JsonException or InvalidDataException or UnauthorizedAccessException)
        {
            error.WriteLine(exception.Message);
            return 1;
        }
    }

    private static Options ParseOptions(string[] args)
    {
        string tapePath = ResolveDefaultTapePath();
        string? expectedTraceHash = null;
        int repeatCount = 2;

        for (int index = 0; index < args.Length; index++)
        {
            switch (args[index])
            {
                case "--tape":
                    tapePath = RequireValue(args, ref index, "--tape");
                    break;
                case "--expect":
                    expectedTraceHash = RequireValue(args, ref index, "--expect");
                    ValidateHashArgument(expectedTraceHash);
                    break;
                case "--repeat":
                    string repeatText = RequireValue(args, ref index, "--repeat");
                    if (!int.TryParse(repeatText, out repeatCount) || repeatCount is < 1 or > 1_000)
                    {
                        throw new ArgumentException("--repeat must be an integer from 1 through 1000.");
                    }
                    break;
                default:
                    throw new ArgumentException($"Unknown argument: {args[index]}");
            }
        }

        return new Options(tapePath, expectedTraceHash, repeatCount);
    }

    private static VerificationExpectation ResolveExpectation(Options options, CommandTape tape)
    {
        if (options.ExpectedTraceHash is not null)
        {
            return new VerificationExpectation(options.ExpectedTraceHash, null, "command-line");
        }

        if (tape.ExpectedTraceHash is not null || tape.ExpectedFinalStateHash is not null)
        {
            return new VerificationExpectation(
                tape.ExpectedTraceHash,
                tape.ExpectedFinalStateHash,
                "command-tape");
        }

        return new VerificationExpectation(null, null, "none");
    }

    private static void ValidateWorkBudget(CommandTape tape, int repeatCount)
    {
        long requestedSteps = checked((long)tape.DurationTicks * repeatCount);
        if (requestedSteps > MaximumReplaySteps)
        {
            throw new ArgumentException(
                $"Replay request exceeds the {MaximumReplaySteps.ToString("N0", CultureInfo.InvariantCulture)} total-step limit.");
        }
    }

    private static void ValidateHashArgument(string hash)
    {
        if (hash.Length != 64 || hash.Any(character => !Uri.IsHexDigit(character)))
        {
            throw new ArgumentException(
                "--expect must be a 64-character SHA-256 replay trace hash.");
        }
    }

    private static string ReadTape(string path)
    {
        using var stream = new FileStream(
            path,
            FileMode.Open,
            FileAccess.Read,
            FileShare.Read,
            bufferSize: 4_096,
            FileOptions.SequentialScan);
        if (stream.Length > MaximumTapeBytes)
        {
            throw new InvalidDataException("Command tape exceeds the 8 MiB input limit.");
        }

        using var reader = new StreamReader(
            stream,
            Encoding.UTF8,
            detectEncodingFromByteOrderMarks: true,
            bufferSize: 4_096,
            leaveOpen: false);
        return reader.ReadToEnd();
    }

    private static string RequireValue(string[] args, ref int index, string option)
    {
        index++;
        if (index >= args.Length || string.IsNullOrWhiteSpace(args[index]))
        {
            throw new ArgumentException($"{option} requires a value.");
        }

        return args[index];
    }

    private static string ResolveDefaultTapePath()
    {
        return Path.Combine(AppContext.BaseDirectory, "scenarios", BuiltInTapeFileName);
    }

    private static void PrintHelp(TextWriter output)
    {
        output.WriteLine("OnslaughtRebuild.Headless");
        output.WriteLine("  --tape <path>   Command tape (default: packaged first-flight scenario)");
        output.WriteLine("  --expect <hex>  Optional expected SHA-256 replay trace hash");
        output.WriteLine("  --repeat <n>    Replay count (default: 2; 100,000 total-step limit)");
    }
}
