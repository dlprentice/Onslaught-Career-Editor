using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace Onslaught___Career_Editor.Cli
{
    /// <summary>
    /// The exit code scheme, in one place so every verb answers the same question the same way.
    ///
    /// The distinction that matters is the third one. Before this existed, <c>--analyze</c> returned 1
    /// both when the tool could not run and when it ran perfectly and the file turned out to be invalid.
    /// An agent driving the CLI could not tell "I called this wrong" from "the answer is no", which are
    /// the two cases it most needs to separate: the first is worth retrying differently, the second is
    /// the result.
    /// </summary>
    public static class CliExit
    {
        /// <summary>The operation ran and the answer is yes.</summary>
        public const int Success = 0;

        /// <summary>
        /// The operation could not be attempted: an unknown verb, a malformed or contradictory flag, a
        /// file that is not there, or a safety refusal. Nothing was measured, so nothing is being said
        /// about the data.
        /// </summary>
        public const int UsageOrToolError = 1;

        /// <summary>
        /// The operation ran to completion and the data says no: an invalid save, a patch target whose
        /// bytes are in an unexpected state, a game directory that could not be detected. Re-running
        /// with different flags will not change this answer.
        /// </summary>
        public const int DataVerdict = 2;
    }

    /// <summary>
    /// The stable machine-readable envelope. Every <c>--json</c> invocation of every verb emits exactly
    /// this shape on stdout and nothing else, including on failure - a caller can parse first and branch
    /// second, instead of having to know in advance whether the run succeeded.
    /// </summary>
    public sealed class CliEnvelope
    {
        [JsonPropertyName("ok")]
        public bool Ok { get; init; }

        /// <summary>Dotted verb path, e.g. <c>saves.analyze</c>. Stable across releases.</summary>
        [JsonPropertyName("command")]
        public string Command { get; init; } = string.Empty;

        [JsonPropertyName("exitCode")]
        public int ExitCode { get; init; }

        [JsonPropertyName("warnings")]
        public IReadOnlyList<string> Warnings { get; init; } = Array.Empty<string>();

        [JsonPropertyName("data")]
        public object? Data { get; init; }

        [JsonPropertyName("error")]
        public CliEnvelopeError? Error { get; init; }
    }

    public sealed class CliEnvelopeError
    {
        /// <summary><c>usage</c> for exit 1, <c>data</c> for exit 2. Mirrors the exit code so a caller
        /// reading only the JSON never has to also inspect the process result.</summary>
        [JsonPropertyName("kind")]
        public string Kind { get; init; } = string.Empty;

        [JsonPropertyName("message")]
        public string Message { get; init; } = string.Empty;

        [JsonPropertyName("details")]
        public IReadOnlyList<string> Details { get; init; } = Array.Empty<string>();
    }

    /// <summary>
    /// Where a single invocation writes, and whether it is speaking JSON.
    ///
    /// Output goes through this rather than <see cref="Console"/> so the whole CLI can be driven
    /// in-process by tests. That is not a testing nicety: verb routing, envelope shape, and the exit-code
    /// split are exactly the behaviours worth pinning, and pinning them by spawning a process is slow
    /// enough that it does not get done.
    /// </summary>
    public sealed class CliContext
    {
        private static readonly JsonSerializerOptions s_json = new()
        {
            WriteIndented = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping,
        };

        private readonly List<string> _warnings = new();

        public CliContext(TextWriter output, TextWriter error, bool json)
        {
            Out = output ?? throw new ArgumentNullException(nameof(output));
            Error = error ?? throw new ArgumentNullException(nameof(error));
            Json = json;
        }

        public TextWriter Out { get; }

        public TextWriter Error { get; }

        public bool Json { get; }

        public IReadOnlyList<string> Warnings => _warnings;

        /// <summary>
        /// A human-readable line. Suppressed entirely under <c>--json</c> so stdout stays a single
        /// parseable document - a JSON consumer that also had to skip banner text would not be a
        /// machine-readable interface.
        /// </summary>
        public void Line(string text = "")
        {
            if (!Json)
                Out.WriteLine(text);
        }

        /// <summary>
        /// A non-fatal caveat. In text mode it goes to stderr immediately; in JSON mode it is collected
        /// into the envelope, because a warning printed outside the document would be invisible to the
        /// caller that most needs it.
        /// </summary>
        public void Warn(string message)
        {
            _warnings.Add(message);
            if (!Json)
                Error.WriteLine($"Warning: {message}");
        }

        public int Ok(string command, object? data = null, string? humanSummary = null)
        {
            if (Json)
            {
                WriteEnvelope(new CliEnvelope
                {
                    Ok = true,
                    Command = command,
                    ExitCode = CliExit.Success,
                    Warnings = _warnings.ToArray(),
                    Data = data,
                });
            }
            else if (!string.IsNullOrWhiteSpace(humanSummary))
            {
                Out.WriteLine(humanSummary);
            }

            return CliExit.Success;
        }

        /// <summary>The caller got the invocation wrong, or a guard refused. Exit 1.</summary>
        public int Usage(string command, string message, params string[] details)
        {
            return Failure(command, CliExit.UsageOrToolError, "usage", message, details);
        }

        /// <summary>The operation ran and the answer is no. Exit 2.</summary>
        public int Verdict(string command, string message, object? data = null, params string[] details)
        {
            return Failure(command, CliExit.DataVerdict, "data", message, details, data);
        }

        private int Failure(
            string command,
            int exitCode,
            string kind,
            string message,
            IReadOnlyList<string>? details,
            object? data = null)
        {
            if (Json)
            {
                WriteEnvelope(new CliEnvelope
                {
                    Ok = false,
                    Command = command,
                    ExitCode = exitCode,
                    Warnings = _warnings.ToArray(),
                    Data = data,
                    Error = new CliEnvelopeError
                    {
                        Kind = kind,
                        Message = message,
                        Details = details?.ToArray() ?? Array.Empty<string>(),
                    },
                });
            }
            else
            {
                Error.WriteLine($"Error: {message}");
                foreach (string detail in details ?? Array.Empty<string>())
                    Error.WriteLine($"  {detail}");
            }

            return exitCode;
        }

        private void WriteEnvelope(CliEnvelope envelope)
        {
            Out.WriteLine(JsonSerializer.Serialize(envelope, s_json));
        }
    }
}
