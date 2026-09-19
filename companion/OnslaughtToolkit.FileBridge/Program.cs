using System.Security.Cryptography;
using System.Text.Json;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.FileBridge;

internal static class Program
{
    private const int MaximumRequestBytes = 64 * 1024;
    private const int MaximumPathCharacters = 4096;
    private const int SaveLength = BesFilePatcher.EXPECTED_FILE_SIZE;
    private static readonly string[] OpenFields = ["protocol", "op", "input"];
    private static readonly string[] PublishFields = ["protocol", "op", "input", "identity", "sha256", "output", "bytes"];

    private static int Main()
    {
        string? publishedOutput = null;
        try
        {
            using JsonDocument document = JsonDocument.Parse(ReadRequest(), new JsonDocumentOptions { MaxDepth = 4 });
            JsonElement request = document.RootElement;
            if (request.ValueKind != JsonValueKind.Object ||
                !request.TryGetProperty("protocol", out JsonElement protocol) ||
                protocol.ValueKind != JsonValueKind.Number ||
                !protocol.TryGetInt32(out int version) || version != 1)
                throw new InvalidRequestException("Expected file bridge protocol 1.");

            string operation = RequiredString(request, "op", 16);
            if (operation is not ("open" or "publish"))
                throw new InvalidRequestException("The file bridge only supports open and publish.");
            RejectUnexpectedOrDuplicateFields(request, operation == "open" ? OpenFields : PublishFields);
            string input = CareerPath(request, "input");

            if (operation == "open")
            {
                using SaveLabSource source = SaveLabSource.Open(input);
                byte[] bytes = source.ReadBytes();
                source.Verify(bytes, source.Identity);
                Respond(new
                {
                    protocol = 1, ok = true, message = "Source read with protected file identity.",
                    input, identity = source.Identity, sha256 = Hash(bytes),
                    size = bytes.Length, bytes = Convert.ToBase64String(bytes)
                });
                return 0;
            }

            string identity = RequiredString(request, "identity", 128);
            byte[] expectedSourceHash = ParseSha256(request);
            string output = CareerPath(request, "output");
            if (FileMutationSafety.AreLexicallySamePath(input, output))
                throw new InvalidRequestException("Choose a new output file different from the original.");
            byte[] prepared = ParsePreparedBytes(request);

            using (SaveLabSource source = SaveLabSource.Open(input))
            {
                byte[] baseline = source.ReadBytes();
                if (!CryptographicOperations.FixedTimeEquals(SHA256.HashData(baseline), expectedSourceHash))
                    throw new IOException("The original save changed after it was opened. Open it again before editing.");
                source.Verify(baseline, identity);
                byte[] reopened = SaveLabFileTransaction.PublishNew(
                    output, source, prepared, baseline, identity, beforePublish: null);
                publishedOutput = output;
                source.Verify(baseline, identity);
                if (!reopened.AsSpan().SequenceEqual(prepared))
                    throw new IOException("The new copy did not match the prepared bytes.");
                Respond(new
                {
                    protocol = 1, ok = true, message = "Separate copy reopened and verified; source identity and bytes verified.",
                    input, identity, output, sha256 = Hash(reopened), size = reopened.Length,
                    bytes = Convert.ToBase64String(reopened), original_verified = true, verified = true
                });
            }
            return 0;
        }
        catch (SaveLabPublicationException error)
        {
            Respond(new { protocol = 1, ok = false, message = error.Message, may_have_output = true, output = error.OutputPath });
            return 1;
        }
        catch (Exception error) when (error is InvalidRequestException or JsonException or FormatException)
        {
            Respond(new { protocol = 1, ok = false, message = "Invalid request: " + error.Message, may_have_output = false });
            return 2;
        }
        catch (Exception error)
        {
            string message = DescribeFailure(error);
            if (publishedOutput is not null)
                Respond(new { protocol = 1, ok = false, message = "A new copy may exist, but final verification failed. " + message,
                    may_have_output = true, output = publishedOutput });
            else
                Respond(new { protocol = 1, ok = false, message, may_have_output = false });
            return 1;
        }
    }

    private static byte[] ReadRequest()
    {
        using Stream input = Console.OpenStandardInput();
        using MemoryStream line = new();
        while (true)
        {
            int value = input.ReadByte();
            if (value is -1 or '\n') break;
            if (line.Length >= MaximumRequestBytes)
                throw new InvalidRequestException("The request exceeds the 64 KiB limit.");
            line.WriteByte((byte)value);
        }
        if (line.Length == 0) throw new InvalidRequestException("A JSON request is required.");
        return line.ToArray();
    }

    private static string CareerPath(JsonElement request, string field)
    {
        string path = RequiredString(request, field, MaximumPathCharacters);
        if (path.IndexOf('\0') >= 0 || !Path.IsPathFullyQualified(path) ||
            !string.Equals(Path.GetExtension(path), ".bes", StringComparison.OrdinalIgnoreCase))
            throw new InvalidRequestException($"{field} must be an absolute .bes career-save path.");
        if (!string.Equals(path, path.Trim(), StringComparison.Ordinal))
            throw new InvalidRequestException($"{field} must not have leading or trailing whitespace.");
        return FileMutationSafety.NormalizeLocalPath(path, field);
    }

    private static string RequiredString(JsonElement request, string field, int maximumLength)
    {
        if (!request.TryGetProperty(field, out JsonElement value) || value.ValueKind != JsonValueKind.String)
            throw new InvalidRequestException($"{field} must be a string.");
        string? result = value.GetString();
        if (string.IsNullOrEmpty(result) || result.Length > maximumLength)
            throw new InvalidRequestException($"{field} is empty or exceeds its limit.");
        return result;
    }

    private static byte[] ParseSha256(JsonElement request)
    {
        string hash = RequiredString(request, "sha256", 64);
        if (hash.Length != 64) throw new InvalidRequestException("sha256 must contain 64 hexadecimal characters.");
        return Convert.FromHexString(hash);
    }

    private static byte[] ParsePreparedBytes(JsonElement request)
    {
        string encoded = RequiredString(request, "bytes", ((SaveLength + 2) / 3) * 4);
        byte[] bytes = Convert.FromBase64String(encoded);
        if (bytes.Length != SaveLength)
            throw new InvalidRequestException($"Prepared bytes must contain exactly {SaveLength} bytes.");
        return bytes;
    }

    private static void RejectUnexpectedOrDuplicateFields(JsonElement request, string[] allowed)
    {
        HashSet<string> seen = new(StringComparer.Ordinal);
        foreach (JsonProperty property in request.EnumerateObject())
            if (!allowed.Contains(property.Name, StringComparer.Ordinal) || !seen.Add(property.Name))
                throw new InvalidRequestException("The request contains an unsupported or duplicate field.");
    }

    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes));

    private static string DescribeFailure(Exception error) => error switch
    {
        FileNotFoundException => "The selected source save could not be found. Open it again.",
        DirectoryNotFoundException => "Choose an existing folder for the save copy.",
        UnauthorizedAccessException => "The selected file or folder could not be accessed.",
        EntryPointNotFoundException or DllNotFoundException => "This system lacks the file protections required for a verified copy.",
        IOException or ArgumentException or InvalidOperationException or NotSupportedException
            or System.Security.SecurityException or System.ComponentModel.Win32Exception => error.Message,
        _ => "The file bridge could not complete this operation safely."
    };

    private static void Respond(object response) => Console.Out.WriteLine(JsonSerializer.Serialize(response));
    private sealed class InvalidRequestException(string message) : Exception(message);
}
