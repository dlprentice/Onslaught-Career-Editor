// SPDX-License-Identifier: GPL-3.0-only
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using Org.BouncyCastle.Math.EC.Rfc8032;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Release authentication, conservative schema admission and bounded read-only HTTP. No live network.</summary>
internal static class CeUpdateFeedTests
{
    // RFC 8032 section 7.1 TEST 1: published test-only key and empty-message signature, never a release credential.
    private static readonly byte[] TestKey = Convert.FromHexString("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a");
    private static readonly byte[] TestSeed = Convert.FromHexString("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60");
    private static readonly byte[] EmptySignature = Convert.FromHexString(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555f" +
        "b8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b");

    internal static async Task RunAsync(Checks check)
    {
        check.Suite("CE signed updates");
        check.That(Ed25519.Verify(EmptySignature, TestKey, Array.Empty<byte>()), "Ed25519 verifies the independent RFC 8032 empty-message vector.");
        byte[] badVector = EmptySignature.ToArray();
        badVector[0] ^= 1;
        check.That(!Ed25519.Verify(badVector, TestKey, Array.Empty<byte>()), "A changed RFC signature is rejected.");

        byte[] data = Encoding.UTF8.GetBytes(Feed());
        byte[] signature = Sign(data);
        CeUpdateState valid = CeUpdateFeed.Validate(data, signature, TestKey, "0.1.1");
        check.That(valid is { Verified: true, LatestVersion: "0.1.2", Availability: CeUpdateAvailability.Newer },
            "An authenticated v2 release newer than installed is reported, without applying it.");
        check.That(CeUpdateFeed.FeedUrl.EndsWith("/releases/latest/download/ce-update-v2.json", StringComparison.Ordinal) &&
            !CeUpdateFeed.FeedUrl.Contains("latest.json", StringComparison.Ordinal),
            "The verifier reads CE's v2 feed name, never the retired latest.json.");
        check.That(CeUpdateFeed.Validate(data, signature, "0.1.1") is { Verified: false, LatestVersion: null },
            "The public entry always uses the pinned CE key, never a fixture or environment key.");
        check.That(CeUpdateFeed.Validate(data, SignBare(data), TestKey, "0.1.1") is { Verified: false, LatestVersion: null },
            "A signature over the bare feed bytes (the old latest.json scheme) does not verify: the v2 domain prefix is required.");
        byte[] oldFeed = Encoding.UTF8.GetBytes(OldFeed());
        check.That(CeUpdateFeed.Validate(oldFeed, SignBare(oldFeed), TestKey, "0.1.1") is { Verified: false, LatestVersion: null } &&
            CeUpdateFeed.Validate(oldFeed, Sign(oldFeed), TestKey, "0.1.1") is { Verified: false, LatestVersion: null },
            "An old latest.json feed is refused, whichever way it is signed.");
        foreach ((string? installed, CeUpdateAvailability expected) in new (string?, CeUpdateAvailability)[]
        {
            ("0.1.2", CeUpdateAvailability.Current), ("0.1.2.0", CeUpdateAvailability.Current),
            ("0.2", CeUpdateAvailability.Older), ("0.1.10", CeUpdateAvailability.Older), ("0.1.1.9", CeUpdateAvailability.Newer),
            ("dev", CeUpdateAvailability.Unknown), ("0.1.2-preview", CeUpdateAvailability.Unknown),
            (null, CeUpdateAvailability.Unknown), ("+0.1.1", CeUpdateAvailability.Unknown),
        })
            check.That(CeUpdateFeed.Validate(data, signature, TestKey, installed).Availability == expected,
                $"Version comparison is numeric and honest for {installed ?? "an unread installed version"}.");

        byte[] changed = data.ToArray();
        changed[5] ^= 1;
        check.That(CeUpdateFeed.Validate(changed, signature, TestKey, "0.1") is { Verified: false, LatestVersion: null },
            "A changed feed byte invalidates the signature before any field is used.");
        check.That(!CeUpdateFeed.Validate(Encoding.UTF8.GetBytes(Feed() + "\n"), signature, TestKey, "0.1").Verified,
            "Even added JSON whitespace requires its own exact-byte signature.");
        foreach (byte[] malformedSignature in new[]
        {
            signature[..127], signature.Concat(new byte[] { 0 }).ToArray(), Encoding.ASCII.GetBytes(new string('z', 128)),
            Encoding.ASCII.GetBytes(new string('0', 128)), signature.Concat(Encoding.ASCII.GetBytes("\n")).ToArray(),
        })
            check.That(!CeUpdateFeed.Validate(data, malformedSignature, TestKey, "0.1").Verified,
                "Malformed, extra-text and incorrect signatures are refused.");
        check.That(CeUpdateFeed.Validate(data, signature[..128], TestKey, "0.1").Verified &&
            CeUpdateFeed.Validate(data, signature[..128].Concat("\r\n"u8.ToArray()).ToArray(), TestKey, "0.1").Verified,
            "The detached hex signature accepts no newline, LF and CRLF.");

        string good = Feed();
        string extended = good.Insert(1, "\"future\":true,\"release-notes\":\"Optional release details\",");
        extended = extended.Replace("\"packages\":{", "\"packages\":{\"linux-arm64\":{\"artifact\":\"future-package\",\"features\":[\"example\"]},", StringComparison.Ordinal);
        byte[] extendedData = Encoding.UTF8.GetBytes(extended);
        check.That(CeUpdateFeed.Validate(extendedData, Sign(extendedData), TestKey, "0.1.1") is
            { Verified: true, LatestVersion: "0.1.2", Availability: CeUpdateAvailability.Newer },
            "Authenticated optional fields, including a future platform, preserve the known release result.");
        check.That(CeUpdateFeed.Validate(extendedData, signature, TestKey, "0.1.1") is { Verified: false, LatestVersion: null },
            "Optional fields are accepted only when the signature authenticates their exact bytes.");
        string extendedPackages = good.Replace("\"sha256\":", "\"future\":{\"format\":\"archive\"},\"sha256\":", StringComparison.Ordinal);
        byte[] extendedPackageData = Encoding.UTF8.GetBytes(extendedPackages);
        check.That(CeUpdateFeed.Validate(extendedPackageData, Sign(extendedPackageData), TestKey, "0.1.1") is
            { Verified: true, LatestVersion: "0.1.2", Availability: CeUpdateAvailability.Newer },
            "Authenticated optional object fields inside both platform objects preserve the release result.");
        check.That(CeUpdateFeed.Validate("{"u8.ToArray(), signature, TestKey, "0.1.1").Message.Contains("signature", StringComparison.Ordinal),
            "Unauthenticated malformed JSON fails signature verification before parsing.");
        foreach (string required in new[] { "format", "version", "packages", "linux-i686", "windows-i686", "url", "sha256", "size" })
        {
            byte[] missing = Encoding.UTF8.GetBytes(extended.Replace($"\"{required}\":", $"\"future-{required}\":", StringComparison.Ordinal));
            check.That(CeUpdateFeed.Validate(missing, Sign(missing), TestKey, "0.1.1") is { Verified: false, LatestVersion: null },
                $"Optional signed fields cannot replace the required {required} field.");
        }
        foreach (string duplicate in new[]
        {
            good.Insert(1, "\"future\":true,\"future\":false,"),
            good.Insert(1, "\"future\":true,\"fut\\u0075re\":false,"),
            good.Replace("\"version\":", "\"version\":\"9.0\",\"version\":", StringComparison.Ordinal),
            good.Replace("\"size\":123", "\"size\":123,\"size\":456", StringComparison.Ordinal),
            good.Replace("\"size\":123", "\"size\":123,\"s\\u0069ze\":456", StringComparison.Ordinal),
            good.Replace("\"sha256\":", "\"sha256\":\"" + new string('a', 64) + "\",\"sha256\":", StringComparison.Ordinal),
        })
        {
            byte[] bytes = Encoding.UTF8.GetBytes(duplicate);
            check.That(CeUpdateFeed.Validate(bytes, Sign(bytes), TestKey, "0.1.1") is { Verified: false, LatestVersion: null },
                "Signed duplicate required or optional names are rejected at both schema levels, including escaped spellings.");
        }
        foreach (string malformed in new[]
        {
            good.Replace("\"onslaught-ce-update-v2\"", "\"onslaught-ce-update-v3\"", StringComparison.Ordinal),
            good.Replace("\"version\":\"0.1.2\"", "\"version\":12", StringComparison.Ordinal),
            good.Replace("\"0.1.2\"", "\"0.1.beta\"", StringComparison.Ordinal),
            good.Replace("\"0.1.2\"", "\"0..2\"", StringComparison.Ordinal),
            good.Replace("\"0.1.2\"", "\"2147483648.0\"", StringComparison.Ordinal),
            good.Replace("\"0.1.2\"", "\"0.1.3\"", StringComparison.Ordinal),
            good.Replace("https://github.com/dlprentice/onslaught-ce/releases/download/", "https://example.com/", StringComparison.Ordinal),
            good.Replace("releases/download/v0.1.2", "releases/download/../../elsewhere", StringComparison.Ordinal),
            good.Replace("linux-i686.tar.gz", "linux-i686.tar.gz?x=1", StringComparison.Ordinal),
            good.Replace("onslaught-ce-0.1.2-windows-i686.zip", "onslaught-ce-0.1.2-linux-i686.tar.gz", StringComparison.Ordinal),
            good.Replace(new string('a', 64), new string('g', 64), StringComparison.Ordinal),
            good.Replace(new string('a', 64), new string('A', 64), StringComparison.Ordinal),
            good.Replace("\"size\":123", "\"size\":0", StringComparison.Ordinal),
            good.Replace("\"size\":123", "\"size\":-1", StringComparison.Ordinal),
            good.Replace("\"size\":123", "\"size\":\"123\"", StringComparison.Ordinal),
            good.Replace("\"size\":123", "\"size\":536870913", StringComparison.Ordinal),
            good.Replace("\"windows-i686\"", "\"unexpected-platform\"", StringComparison.Ordinal),
            "[]", "null", "{", good + "{}",
        })
        {
            byte[] bytes = Encoding.UTF8.GetBytes(malformed);
            check.That(CeUpdateFeed.Validate(bytes, Sign(bytes), TestKey, "0.1") is { Verified: false, LatestVersion: null },
                "Even signed duplicate, malformed, wrong-type, unknown-format or off-repository metadata is rejected.");
        }
        byte[] oversized = Encoding.UTF8.GetBytes(good + new string(' ', CeUpdateFeed.MaximumFeedBytes));
        check.That(!CeUpdateFeed.Validate(oversized, Sign(oversized), TestKey, "0.1").Verified, "Oversized signed JSON is refused.");
        VersionChecks(check);
        await HttpChecks(data, signature, check);
    }

    private static void VersionChecks(Checks check)
    {
        foreach (string version in new[] { "1", "0.2", "0.1.8", "0.1.8.1" })
        {
            byte[] bytes = Encoding.UTF8.GetBytes(Feed(version));
            check.That(CeUpdateFeed.Validate(bytes, Sign(bytes), TestKey, "0.1.7") is { Verified: true } displayed &&
                displayed.LatestVersion == version && displayed.Availability == CeUpdateAvailability.Newer,
                $"A signed numeric version of one to four parts ({version}) is accepted.");
        }
        foreach (string version in new[] { "0.1.8.1.2", "0.2.0-rc1", "0.2.0+build.7", "", "0.2.0-" })
        {
            byte[] bytes = Encoding.UTF8.GetBytes(Feed(version));
            check.That(CeUpdateFeed.Validate(bytes, Sign(bytes), TestKey, "0.1.7") is { Verified: false, LatestVersion: null },
                $"A signed version that is not one to four numeric parts ('{version}') is refused, as the launcher refuses it.");
        }
    }

    private static async Task HttpChecks(byte[] data, byte[] signature, Checks check)
    {
        List<string> requested = [];
        using HttpClient client = new(new Handler(request =>
        {
            requested.Add(request.RequestUri!.AbsoluteUri);
            check.That(request.Method == HttpMethod.Get && !request.Headers.Contains("Authorization") && request.Content is null,
                "Release requests are unauthenticated GETs with no body.");
            return Ok(request.RequestUri.AbsoluteUri == CeUpdateFeed.FeedUrl ? data : signature);
        }));
        CeUpdateState found = await CeUpdateFeed.CheckAsync(client, TestKey, "0.1.1");
        check.That(found.Verified && requested.SequenceEqual([CeUpdateFeed.FeedUrl, CeUpdateFeed.SignatureUrl]),
            "A check reads exactly the public metadata and signature, never a game package or installed-version URL.");

        using HttpClient missing = new(new Handler(_ => new HttpResponseMessage(HttpStatusCode.NotFound)));
        check.That(await CeUpdateFeed.CheckAsync(missing, TestKey, "0.1") is { Verified: false, LatestVersion: null },
            "An absent release is unavailable, not current.");
        using HttpClient failing = new(new Handler(_ => throw new HttpRequestException("offline")));
        check.That(!(await CeUpdateFeed.CheckAsync(failing, TestKey, "0.1")).Verified, "A network failure is an honest unavailable result.");
        using CancellationTokenSource cancelled = new();
        cancelled.Cancel();
        check.That(!(await CeUpdateFeed.CheckAsync(client, TestKey, "0.1", cancelled.Token)).Verified, "Cancellation never yields a current version.");

        int followed = 0;
        using HttpClient redirected = new(new Handler(request =>
        {
            followed++;
            if (request.RequestUri!.Host == "github.com")
                return Redirect("https://release-assets.githubusercontent.com/public/" + (request.RequestUri.AbsoluteUri.EndsWith(".sig", StringComparison.Ordinal) ? "signature" : "feed"));
            return Ok(request.RequestUri.AbsolutePath.EndsWith("signature", StringComparison.Ordinal) ? signature : data);
        }));
        check.That((await CeUpdateFeed.CheckAsync(redirected, TestKey, "0.1")).Verified && followed == 4,
            "The public GitHub-to-release-asset redirect is supported and the bytes still require authentication.");
        foreach (string badRedirect in new[] { "http://github.com/dlprentice/onslaught-ce/releases/x", "https://example.com/file",
            "https://github.com/other/repo/releases/x", "https://user@github.com/dlprentice/onslaught-ce/releases/x",
            "https://github.com:8443/dlprentice/onslaught-ce/releases/x" })
        {
            int count = 0;
            using HttpClient external = new(new Handler(_ => { count++; return Redirect(badRedirect); }));
            check.That(!(await CeUpdateFeed.CheckAsync(external, TestKey, "0.1")).Verified && count == 1,
                "An off-policy redirect is rejected before contacting its destination.");
        }
        int loops = 0;
        using HttpClient looping = new(new Handler(_ => { loops++; return Redirect(CeUpdateFeed.FeedUrl); }));
        check.That(!(await CeUpdateFeed.CheckAsync(looping, TestKey, "0.1")).Verified && loops == 6,
            "Redirect loops have a fixed bound.");
        using HttpClient huge = new(new Handler(_ => Ok(new byte[CeUpdateFeed.MaximumFeedBytes + 1])));
        check.That(!(await CeUpdateFeed.CheckAsync(huge, TestKey, "0.1")).Verified, "HTTP metadata over the limit is refused.");
        using HttpClient chunked = new(new Handler(_ => new HttpResponseMessage(HttpStatusCode.OK)
        {
            Content = new StreamContent(new NonSeekable(new byte[CeUpdateFeed.MaximumFeedBytes + 1])),
        }));
        check.That(!(await CeUpdateFeed.CheckAsync(chunked, TestKey, "0.1")).Verified, "Unknown-length HTTP bodies are bounded too.");
    }

    private static byte[] Sign(byte[] data) => SignBare([.. CeUpdateFeed.SignatureDomain, .. data]);

    private static byte[] SignBare(byte[] data)
    {
        byte[] signature = new byte[64];
        Ed25519.Sign(TestSeed, 0, data, 0, data.Length, signature, 0);
        return Encoding.ASCII.GetBytes(Convert.ToHexString(signature).ToLowerInvariant() + "\n");
    }

    private static string Feed(string version = "0.1.2") => "{\"format\":\"onslaught-ce-update-v2\",\"version\":" +
        JsonSerializer.Serialize(version) + ",\"packages\":{" +
        "\"linux-i686\":{\"url\":\"https://github.com/dlprentice/onslaught-ce/releases/download/v" + version + "/onslaught-ce-" + version +
        "-linux-i686.tar.gz\",\"sha256\":\"" + new string('a', 64) + "\",\"size\":123}," +
        "\"windows-i686\":{\"url\":\"https://github.com/dlprentice/onslaught-ce/releases/download/v" + version + "/onslaught-ce-" + version +
        "-windows-i686.zip\",\"sha256\":\"" + new string('b', 64) + "\",\"size\":456}}}";

    /// <summary>The retired 0.1.0–0.1.6 latest.json shape.</summary>
    private static string OldFeed() => "{\"name\":\"Onslaught CE\",\"version\":\"0.1.2\"," +
        "\"linux-i686\":{\"url\":\"https://github.com/dlprentice/onslaught-ce/releases/download/v0.1.2/linux.tar.gz\",\"sha256\":\"" + new string('a', 64) + "\"}," +
        "\"windows-i686\":{\"url\":\"https://github.com/dlprentice/onslaught-ce/releases/download/v0.1.2/windows.zip\",\"sha256\":\"" + new string('b', 64) + "\"}}";

    private static HttpResponseMessage Ok(byte[] bytes) => new(HttpStatusCode.OK) { Content = new ByteArrayContent(bytes) };

    private static HttpResponseMessage Redirect(string url)
    {
        HttpResponseMessage response = new(HttpStatusCode.Redirect);
        response.Headers.Location = new Uri(url);
        return response;
    }

    private sealed class Handler(Func<HttpRequestMessage, HttpResponseMessage> reply) : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken cancellationToken)
        {
            cancellationToken.ThrowIfCancellationRequested();
            return Task.FromResult(reply(request));
        }
    }

    private sealed class NonSeekable(byte[] bytes) : MemoryStream(bytes)
    {
        public override bool CanSeek => false;
    }
}
