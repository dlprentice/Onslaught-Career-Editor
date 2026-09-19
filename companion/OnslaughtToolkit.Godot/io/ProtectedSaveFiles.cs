// SPDX-License-Identifier: MIT
using System.Security.Cryptography;
using Godot;
using OnslaughtCareerEditor.AppCore;
using Reply = Godot.Collections.Dictionary;

namespace OnslaughtToolkit.Companion;

/// <summary>
/// The companion's narrow OS file-safety boundary. GDScript owns format analysis,
/// edit planning and all presentation; this class never interprets career fields.
/// Each synchronous call owns and releases its handles before returning. Calls
/// may run on a Godot worker Thread, with the adapter retained until it finishes.
/// A running protected transaction must not be force-aborted or treated as an
/// unsuccessful write solely because a UI wait deadline has passed.
/// </summary>
[GlobalClass]
public partial class ProtectedSaveFiles : RefCounted
{
    private const int MaximumPathCharacters = 4096;
    private const int SaveLength = BesFilePatcher.EXPECTED_FILE_SIZE;

    public Reply OpenCareer(string input)
    {
        try
        {
            string path = CareerPath(input, "input");
            using SaveLabSource source = SaveLabSource.Open(path);
            byte[] bytes = source.ReadBytes();
            source.Verify(bytes, source.Identity);
            return new Reply
            {
                ["ok"] = true,
                ["message"] = "Source read with protected file identity.",
                ["input"] = path,
                ["identity"] = source.Identity,
                ["sha256"] = Hash(bytes),
                ["size"] = bytes.Length,
                ["bytes"] = bytes
            };
        }
        catch (Exception error)
        {
            return Failure(error);
        }
    }

    public Reply PublishCopy(string input, string identity, string sha256, string output, byte[] prepared)
    {
        string? publishedOutput = null;
        try
        {
            string path = CareerPath(input, "input");
            string destination = CareerPath(output, "output");
            string expectedIdentity = RequiredText(identity, "identity", 128);
            byte[] expectedSourceHash = ParseSha256(sha256);
            if (FileMutationSafety.AreLexicallySamePath(path, destination))
                throw new ArgumentException("Choose a new output file different from the original.");
            if (prepared is null || prepared.Length != SaveLength)
                throw new ArgumentException($"Prepared bytes must contain exactly {SaveLength} bytes.");

            // Own the payload for the full transaction, even if a C# caller gave
            // us a mutable array. The adapter never changes the supplied bytes.
            byte[] expected = prepared.ToArray();
            using SaveLabSource source = SaveLabSource.Open(path);
            byte[] baseline = source.ReadBytes();
            if (!CryptographicOperations.FixedTimeEquals(SHA256.HashData(baseline), expectedSourceHash))
                throw new IOException("The original save changed after it was opened. Open it again before editing.");
            source.Verify(baseline, expectedIdentity);
            byte[] reopened = SaveLabFileTransaction.PublishNew(
                destination, source, expected, baseline, expectedIdentity, beforePublish: null);
            publishedOutput = destination;
            source.Verify(baseline, expectedIdentity);
            if (!reopened.AsSpan().SequenceEqual(expected))
                throw new IOException("The new copy did not match the prepared bytes.");

            return new Reply
            {
                ["ok"] = true,
                ["message"] = "Separate copy reopened and verified; source identity and bytes verified.",
                ["input"] = path,
                ["identity"] = expectedIdentity,
                ["output"] = destination,
                ["sha256"] = Hash(reopened),
                ["size"] = reopened.Length,
                ["bytes"] = reopened,
                ["original_verified"] = true,
                ["verified"] = true
            };
        }
        catch (SaveLabPublicationException error)
        {
            return Failure(error, error.OutputPath);
        }
        catch (Exception error)
        {
            return Failure(error, publishedOutput);
        }
    }

    private static string CareerPath(string? value, string field)
    {
        string path = RequiredText(value, field, MaximumPathCharacters);
        if (path.IndexOf('\0') >= 0 || !Path.IsPathFullyQualified(path) ||
            !string.Equals(System.IO.Path.GetExtension(path), ".bes", StringComparison.OrdinalIgnoreCase))
            throw new ArgumentException($"{field} must be an absolute .bes career-save path.");
        if (!string.Equals(path, path.Trim(), StringComparison.Ordinal))
            throw new ArgumentException($"{field} must not have leading or trailing whitespace.");
        return FileMutationSafety.NormalizeLocalPath(path, field);
    }

    private static string RequiredText(string? value, string field, int maximumLength)
    {
        if (string.IsNullOrEmpty(value) || value.Length > maximumLength)
            throw new ArgumentException($"{field} is empty or exceeds its limit.");
        return value;
    }

    private static byte[] ParseSha256(string? value)
    {
        string hash = RequiredText(value, "sha256", 64);
        if (hash.Length != 64)
            throw new ArgumentException("sha256 must contain 64 hexadecimal characters.");
        return Convert.FromHexString(hash);
    }

    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes));

    private static Reply Failure(Exception error, string? output = null)
    {
        string message = DescribeFailure(error);
        Reply reply = new()
        {
            ["ok"] = false,
            ["message"] = output is null || error is SaveLabPublicationException
                ? message : "A new copy may exist, but final verification failed. " + message,
            ["may_have_output"] = output is not null
        };
        if (output is not null) reply["output"] = output;
        return reply;
    }

    private static string DescribeFailure(Exception error) => error switch
    {
        FileNotFoundException => "The selected source save could not be found. Open it again.",
        DirectoryNotFoundException => "Choose an existing folder for the save copy.",
        UnauthorizedAccessException => "The selected file or folder could not be accessed.",
        EntryPointNotFoundException or DllNotFoundException => "This system lacks the file protections required for a verified copy.",
        FormatException => "sha256 must contain 64 hexadecimal characters.",
        IOException or ArgumentException or InvalidOperationException or NotSupportedException
            or System.Security.SecurityException or System.ComponentModel.Win32Exception => error.Message,
        _ => "The protected save operation could not complete safely."
    };
}
