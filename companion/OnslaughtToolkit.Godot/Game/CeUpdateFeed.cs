// SPDX-License-Identifier: GPL-3.0-only
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using Org.BouncyCastle.Math.EC.Rfc8032;

namespace OnslaughtToolkit.Companion.Game;

public enum CeUpdateAvailability { Unknown, Current, Newer, Older }

/// <summary>A read-only result. A failed signature or unsupported feed never supplies a release version.</summary>
public sealed record CeUpdateState(bool Verified, string? LatestVersion, CeUpdateAvailability Availability, string Message);

/// <summary>
/// Reads only the public CE release feed and its detached signature, on explicit request. It never fetches packages,
/// writes configuration, or performs updates. Contract: Onslaught CE commit 72a44140c6db3e093cc07b1bed40a0584fdfecd2,
/// port/updater/ce_launch.c (PUBLIC_KEY_HEX, check_for_update) and port/tools/sign_release.py.
/// The signature authenticates exact feed bytes; it cannot establish when those bytes were published.
/// </summary>
public static class CeUpdateFeed
{
    public const string FeedUrl = "https://github.com/dlprentice/onslaught-ce/releases/latest/download/latest.json";
    public const string SignatureUrl = FeedUrl + ".sig";
    public const string PublicKeyHex = "b6cf39b727c92cd8a1682c31f315a5d38427dce912e406ccbd4802f0f7634510";
    internal const int MaximumFeedBytes = 16 * 1024;
    private const int MaximumSignatureBytes = 130;
    private const string ReleasePath = "/dlprentice/onslaught-ce/releases/";
    private const string PackagePrefix = "https://github.com/dlprentice/onslaught-ce/releases/download/";
    private static readonly byte[] PublicKey = Convert.FromHexString(PublicKeyHex);
    private static readonly HttpClient Client = new(new HttpClientHandler
    {
        AllowAutoRedirect = false, UseCookies = false, UseDefaultCredentials = false,
        AutomaticDecompression = DecompressionMethods.None,
    }) { Timeout = Timeout.InfiniteTimeSpan };

    /// <summary>
    /// Contacts GitHub's public latest.json and latest.json.sig (and GitHub's HTTPS release-asset redirects).
    /// No account, credentials, local paths, installed version or usage information is sent.
    /// </summary>
    public static Task<CeUpdateState> CheckAsync(string? installedVersion, CancellationToken cancellationToken = default) =>
        CheckAsync(Client, PublicKey, installedVersion, cancellationToken);

    internal static async Task<CeUpdateState> CheckAsync(HttpClient client, byte[] publicKey, string? installedVersion,
        CancellationToken cancellationToken = default)
    {
        using CancellationTokenSource timeout = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
        timeout.CancelAfter(TimeSpan.FromSeconds(20));
        try
        {
            byte[] json = await DownloadAsync(client, new Uri(FeedUrl), MaximumFeedBytes, timeout.Token).ConfigureAwait(false);
            byte[] signature = await DownloadAsync(client, new Uri(SignatureUrl), MaximumSignatureBytes, timeout.Token).ConfigureAwait(false);
            return Validate(json, signature, publicKey, installedVersion);
        }
        catch (OperationCanceledException)
        {
            return Failure(cancellationToken.IsCancellationRequested ? "The release check was cancelled." : "The release check timed out. Try again later.");
        }
        catch (Exception error) when (error is HttpRequestException or IOException or InvalidDataException)
        {
            return Failure("The public release information could not be read safely. Try again later; CE has not been changed.");
        }
    }

    /// <summary>Verifies the exact bytes against CE's pinned release key before parsing any fields.</summary>
    public static CeUpdateState Validate(byte[] json, byte[] signatureText, string? installedVersion) =>
        Validate(json, signatureText, PublicKey, installedVersion);

    internal static CeUpdateState Validate(byte[] json, byte[] signatureText, byte[] publicKey, string? installedVersion)
    {
        if (json.Length is 0 or > MaximumFeedBytes || !TrySignature(signatureText, out byte[] signature) ||
            publicKey.Length != 32 || !Ed25519.Verify(signature, publicKey, json))
            return Failure("The release signature could not be verified. No update information is trusted; CE has not been changed.");

        try
        {
            using JsonDocument document = JsonDocument.Parse(json, new JsonDocumentOptions { MaxDepth = 4 });
            JsonElement root = document.RootElement;
            if (!RequiredFields(root, ["name", "version", "linux-i686", "windows-i686"], allowAdditional: true) ||
                Text(root, "name") != "Onslaught CE" || Text(root, "version") is not string version ||
                !TryVersion(version, out _) || !Package(root.GetProperty("linux-i686")) || !Package(root.GetProperty("windows-i686")))
                return Failure("The signed release information has a format this companion does not support. CE has not been changed.");

            CeUpdateAvailability availability = Compare(version, installedVersion);
            string message = availability switch
            {
                CeUpdateAvailability.Newer => $"CE {version} is available. Start CE to let its launcher offer the update.",
                CeUpdateAvailability.Current => $"Your CE version matches the signed release, {version}.",
                CeUpdateAvailability.Older => $"The signed release is {version}; your installed version is newer.",
                _ => $"Signed release: CE {version}. Your installed version could not be compared.",
            };
            return new CeUpdateState(true, version, availability, message);
        }
        catch (JsonException)
        {
            return Failure("The signed release information could not be understood. CE has not been changed.");
        }
    }

    private static async Task<byte[]> DownloadAsync(HttpClient client, Uri uri, int limit, CancellationToken token)
    {
        for (int redirects = 0; redirects <= 5; redirects++)
        {
            if (!AllowedRequest(uri)) throw new InvalidDataException("Unexpected release host.");
            using HttpRequestMessage request = new(HttpMethod.Get, uri);
            using HttpResponseMessage response = await client.SendAsync(request, HttpCompletionOption.ResponseHeadersRead, token).ConfigureAwait(false);
            if (response.StatusCode is HttpStatusCode.MovedPermanently or HttpStatusCode.Redirect or HttpStatusCode.SeeOther or
                HttpStatusCode.TemporaryRedirect or HttpStatusCode.PermanentRedirect)
            {
                if (redirects == 5 || response.Headers.Location is not Uri location)
                    throw new InvalidDataException("Too many redirects or missing location.");
                uri = location.IsAbsoluteUri ? location : new Uri(uri, location);
                continue;
            }
            response.EnsureSuccessStatusCode();
            if (response.Content.Headers.ContentLength is long length && (length < 0 || length > limit))
                throw new InvalidDataException("Release data is too large.");
            await using Stream source = await response.Content.ReadAsStreamAsync(token).ConfigureAwait(false);
            using MemoryStream output = new();
            byte[] buffer = new byte[4096];
            for (;;)
            {
                // Read one extra byte to reject oversized chunked responses too, without buffering their body.
                int read = await source.ReadAsync(buffer.AsMemory(0, Math.Min(buffer.Length, limit - (int)output.Length + 1)), token)
                    .ConfigureAwait(false);
                if (read == 0) break;
                if (output.Length + read > limit) throw new InvalidDataException("Release data is too large.");
                output.Write(buffer, 0, read);
            }
            return output.ToArray();
        }
        throw new InvalidDataException("Too many redirects.");
    }

    internal static bool AllowedRequest(Uri uri) => uri.IsAbsoluteUri && uri.Scheme == Uri.UriSchemeHttps &&
        uri.IsDefaultPort && uri.UserInfo.Length == 0 && uri.Fragment.Length == 0 &&
        ((uri.Host == "github.com" && uri.AbsolutePath.StartsWith(ReleasePath, StringComparison.Ordinal)) ||
            uri.Host is "release-assets.githubusercontent.com" or "objects.githubusercontent.com");

    private static bool TrySignature(byte[] text, out byte[] signature)
    {
        signature = [];
        // The producer writes 128 ASCII hex digits and LF; accept CRLF and a missing final newline as well.
        if (text.Length is < 128 or > MaximumSignatureBytes ||
            (text.Length == 129 && text[128] != '\n') ||
            (text.Length == 130 && (text[128] != '\r' || text[129] != '\n'))) return false;
        for (int i = 0; i < 128; i++)
            if (!((text[i] >= '0' && text[i] <= '9') || (text[i] >= 'a' && text[i] <= 'f') || (text[i] >= 'A' && text[i] <= 'F')))
                return false;
        signature = Convert.FromHexString(Encoding.ASCII.GetString(text, 0, 128));
        return true;
    }

    private static bool RequiredFields(JsonElement value, string[] wanted, bool allowAdditional = false)
    {
        if (value.ValueKind != JsonValueKind.Object) return false;
        HashSet<string> seen = new(StringComparer.Ordinal);
        foreach (JsonProperty field in value.EnumerateObject())
            if (!seen.Add(field.Name)) return false;
        // Signed top-level additions are optional, but cannot replace required fields or repeat any name.
        return wanted.All(seen.Contains) && (allowAdditional || seen.Count == wanted.Length);
    }

    private static string? Text(JsonElement value, string key) =>
        value.TryGetProperty(key, out JsonElement field) && field.ValueKind == JsonValueKind.String ? field.GetString() : null;

    private static bool Package(JsonElement value) => RequiredFields(value, ["url", "sha256"]) &&
        Text(value, "url") is string url && url.StartsWith(PackagePrefix, StringComparison.Ordinal) &&
        Uri.TryCreate(url, UriKind.Absolute, out Uri? parsed) && AllowedRequest(parsed) &&
        parsed.AbsolutePath.StartsWith(ReleasePath + "download/", StringComparison.Ordinal) && parsed.Query.Length == 0 &&
        Text(value, "sha256") is { Length: 64 } hash && hash.All(Uri.IsHexDigit);

    private static bool TryVersion(string? version, out int[] parts)
    {
        parts = [];
        if (string.IsNullOrEmpty(version) || version.Length > 63) return false;
        string[] text = version.Split('.');
        parts = new int[text.Length];
        for (int i = 0; i < text.Length; i++)
            if (text[i].Length == 0 || !text[i].All(char.IsAsciiDigit) ||
                !int.TryParse(text[i], System.Globalization.NumberStyles.None, System.Globalization.CultureInfo.InvariantCulture, out parts[i]))
                return false;
        return true;
    }

    private static CeUpdateAvailability Compare(string latest, string? installed)
    {
        if (!TryVersion(latest, out int[] a) || !TryVersion(installed, out int[] b)) return CeUpdateAvailability.Unknown;
        for (int i = 0; i < Math.Max(a.Length, b.Length); i++)
        {
            int x = i < a.Length ? a[i] : 0, y = i < b.Length ? b[i] : 0;
            if (x != y) return x > y ? CeUpdateAvailability.Newer : CeUpdateAvailability.Older;
        }
        return CeUpdateAvailability.Current;
    }

    private static CeUpdateState Failure(string message) => new(false, null, CeUpdateAvailability.Unknown, message);
}
