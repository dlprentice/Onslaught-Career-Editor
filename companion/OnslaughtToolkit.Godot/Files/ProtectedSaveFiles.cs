// SPDX-License-Identifier: MIT
using System.Security.Cryptography;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion.Files;

/// <summary>A protected snapshot of one career file: exact bytes plus physical file identity.</summary>
public sealed record ProtectedRead(bool Ok, string Message, string Input = "", string Identity = "",
    string Sha256 = "", int Size = 0, byte[]? Bytes = null);

/// <summary>
/// The result of publishing a separate copy. Once publication may have begun, a failure sets
/// <see cref="MayHaveOutput"/> and names <see cref="Output"/> for inspection; it is never deleted.
/// </summary>
public sealed record PublicationReceipt(bool Ok, string Message, string? Output = null, bool MayHaveOutput = false,
    string Input = "", string Identity = "", string Sha256 = "", int Size = 0, byte[]? Bytes = null,
    bool OriginalVerified = false, bool Verified = false)
{
    public static PublicationReceipt Uncertain(string? output, string message) => new(false, message, output, MayHaveOutput: true);
}

/// <summary>Protected career file access. Implementations never interpret career fields.</summary>
public interface IProtectedSaveFiles
{
    ProtectedRead OpenCareer(string input);

    PublicationReceipt PublishCopy(string input, string identity, string sha256, string output, byte[] prepared);
}

/// <summary>
/// The companion's narrow OS file-safety boundary. It links the existing MIT
/// SaveLabFileTransaction and FileMutationSafety source unchanged: no-follow opens, physical
/// identity checks, unnamed staging, no-clobber publication and verified reopen. Each call owns
/// and releases its handles before returning. A running transaction must not be abandoned or
/// reported as failed merely because a caller stopped waiting.
/// </summary>
public sealed class ProtectedSaveFiles : IProtectedSaveFiles
{
    private const int MaximumPathCharacters = 4096;
    private const int SaveLength = BesFilePatcher.EXPECTED_FILE_SIZE;

    public ProtectedRead OpenCareer(string input)
    {
        try
        {
            string path = CareerPath(input, "input");
            using SaveLabSource source = SaveLabSource.Open(path);
            byte[] bytes = source.ReadBytes();
            source.Verify(bytes, source.Identity);
            return new ProtectedRead(true, "Source read with protected file identity.", path, source.Identity,
                Hash(bytes), bytes.Length, bytes);
        }
        catch (Exception error)
        {
            return new ProtectedRead(false, DescribeFailure(error));
        }
    }

    public PublicationReceipt PublishCopy(string input, string identity, string sha256, string output, byte[] prepared)
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

            // Own the payload for the whole transaction; the caller's array is never changed.
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

            return new PublicationReceipt(true, "Separate copy reopened and verified; source identity and bytes verified.",
                destination, false, path, expectedIdentity, Hash(reopened), reopened.Length, reopened,
                OriginalVerified: true, Verified: true);
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
        if (path.Contains('\0') || !Path.IsPathFullyQualified(path) ||
            !string.Equals(Path.GetExtension(path), ".bes", StringComparison.OrdinalIgnoreCase))
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

    private static PublicationReceipt Failure(Exception error, string? output)
    {
        string message = DescribeFailure(error);
        return output is null
            ? new PublicationReceipt(false, message)
            : PublicationReceipt.Uncertain(output, error is SaveLabPublicationException
                ? message : "A new copy may exist, but final verification failed. " + message);
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
        _ => "The protected save operation could not complete safely.",
    };
}
