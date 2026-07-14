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
    private const string BuiltInFinalStateHash =
        "9928755b150d4ab172be9b1ee827d462d00887b0c4dcdc4e658c6f1196db0055";
    private const string BuiltInTraceHash =
        "ec6c6628c7d3c1da39bce16160b5f36210899a64f6d1cbfbe18a3b13c7f3dce3";

    private sealed record Options(
        string TapePath,
        bool TapePathExplicit,
        string? ExpectedTraceHash,
        int RepeatCount,
        bool Verify);

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
                error.WriteLine("Replay trace hash did not match the expected golden value.");
                return 2;
            }

            if (finalStateHashVerified == false)
            {
                error.WriteLine("Final state hash did not match the expected golden value.");
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
        bool tapePathExplicit = false;
        string? expectedTraceHash = null;
        int repeatCount = 2;
        bool verify = true;

        for (int index = 0; index < args.Length; index++)
        {
            switch (args[index])
            {
                case "--tape":
                    tapePath = RequireValue(args, ref index, "--tape");
                    tapePathExplicit = true;
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
                case "--no-verify":
                    verify = false;
                    break;
                default:
                    throw new ArgumentException($"Unknown argument: {args[index]}");
            }
        }

        if (!verify && expectedTraceHash is not null)
        {
            throw new ArgumentException("--expect cannot be combined with --no-verify.");
        }

        return new Options(tapePath, tapePathExplicit, expectedTraceHash, repeatCount, verify);
    }

    private static VerificationExpectation ResolveExpectation(Options options, CommandTape tape)
    {
        if (!options.Verify)
        {
            return new VerificationExpectation(null, null, "none");
        }

        if (options.ExpectedTraceHash is not null)
        {
            return new VerificationExpectation(options.ExpectedTraceHash, null, "command-line");
        }

        if (options.TapePathExplicit)
        {
            throw new ArgumentException(
                "Explicit --tape input requires --expect <trace-hash> or --no-verify.");
        }

        if (!string.Equals(
                tape.ExpectedTraceHash,
                BuiltInTraceHash,
                StringComparison.OrdinalIgnoreCase) ||
            !string.Equals(
                tape.ExpectedFinalStateHash,
                BuiltInFinalStateHash,
                StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidDataException(
                "Packaged default tape declarations do not match the independent headless golden values.");
        }

        return new VerificationExpectation(
            BuiltInTraceHash,
            BuiltInFinalStateHash,
            "headless-built-in-golden");
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
        output.WriteLine("  --tape <path>   Explicit command tape; requires --expect or --no-verify");
        output.WriteLine("  --expect <hex>  Expected SHA-256 replay trace hash");
        output.WriteLine("  --repeat <n>    Replay count (default: 2; 100,000 total-step limit)");
        output.WriteLine("  --no-verify     Generate hashes without a trusted expectation");
    }
}
