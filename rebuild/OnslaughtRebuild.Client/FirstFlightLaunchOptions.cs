// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client;

/// <summary>Launch argument admission, before any media or career files are opened.</summary>
public sealed record FirstFlightLaunchOptions(
    bool Smoke,
    string? ReportPath,
    bool CaptureArgumentsPresent,
    bool SkipStartupMedia,
    bool ForceStartupMedia,
    string? RecordTapePath)
{
    public static FirstFlightLaunchOptions Parse(IEnumerable<string> arguments)
    {
        ArgumentNullException.ThrowIfNull(arguments);
        bool smoke = false, capture = false, skip = false, intro = false;
        string? report = null, tape = null;
        foreach (string argument in arguments)
        {
            if (argument == "--smoke") smoke = true;
            else if (argument == "--skipfmv") skip = true;
            else if (argument == "--intro") intro = true;
            else if (argument.StartsWith("--report=", StringComparison.Ordinal))
                report = argument["--report=".Length..];
            else if (argument.StartsWith("--record-tape=", StringComparison.Ordinal))
                tape = argument["--record-tape=".Length..];
            else if (argument.StartsWith("--capture-dir=", StringComparison.Ordinal) ||
                     argument.StartsWith("--capture-plan=", StringComparison.Ordinal) ||
                     argument.StartsWith("--capture-size=", StringComparison.Ordinal) ||
                     argument.StartsWith("--capture-offsets-ms=", StringComparison.Ordinal))
                capture = true;
            else if (argument.StartsWith("--startup-media=", StringComparison.Ordinal) ||
                     argument.StartsWith("--career-save=", StringComparison.Ordinal))
            {
                // Their existing adapters own path/content validation and file reads.
            }
            else
                throw new ArgumentException($"Unknown First Flight argument '{argument}'.");
        }

        if (smoke && (string.IsNullOrWhiteSpace(report) || !Path.IsPathFullyQualified(report)))
            throw new ArgumentException("Smoke mode requires an absolute --report path.");
        if (tape is not null &&
            (!Path.IsPathFullyQualified(tape) ||
             !string.Equals(Path.GetExtension(tape), ".json", StringComparison.OrdinalIgnoreCase)))
            throw new ArgumentException(
                "--record-tape requires an absolute .json path outside career-save and retail storage.");

        return new(smoke, report, capture, skip, intro, tape);
    }
}
