// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;
using System.Text.Json;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The index of decoded startup media, read from a cache directory that lives
/// OUTSIDE <c>res://</c>.
///
/// <para><b>Why outside res://.</b></para>
/// These files are decodes of the user's own retail installation. They are
/// already gitignored, but a <c>.gitignore</c> entry does not stop a Godot
/// export from packing an ignored file into the PCK — the export scans the
/// project directory, not the git index. Keeping the cache outside the project
/// tree makes packing them structurally impossible rather than merely
/// discouraged. (The pre-existing <c>Assets/Frontend/Backgrounds/
/// fe-back-128x128x15.rgb</c> DOES sit inside <c>res://</c> and is exposed to
/// exactly that hazard; this lane does not extend the problem.)
///
/// <para><b>Frames are per-file, never one big strip.</b></para>
/// The decode is one lossless PNG per video frame. Measured on this machine:
/// LTLogo 229 frames = 24 MB, OpeningFMV 2054 frames = 244 MB, against 98.9 MB
/// and 887 MB for raw RGB24 strips of the same footage. Because the frames are
/// separately addressable, the player holds exactly ONE frame resident and
/// updates a single texture in place. The existing FEBack loader — which reads
/// a whole strip and builds one <c>Texture2D</c> per frame — must not be
/// applied at this scale.
/// </summary>
public sealed class RetailStartupMediaIndex
{
    public const string Schema = "onslaught-startup-media.v3";
    private static ReadOnlySpan<byte> FrameSetDomain =>
        "onslaught-startup-frame-set.v1\0"u8;

    private readonly Dictionary<RetailStartupCue, RetailStartupClip> _clips = [];
    private readonly Dictionary<RetailStartupCue, string> _frameFormats = [];

    private RetailStartupMediaIndex()
    {
    }

    /// <summary>Directory the index was read from; frame paths are relative to it.</summary>
    public string Root { get; private init; } = string.Empty;

    /// <summary>Decoded video clips, keyed by cue.</summary>
    public IReadOnlyDictionary<RetailStartupCue, RetailStartupClip> Clips => _clips;

    /// <summary>Relative path of the splash still, or null if it was not materialized.</summary>
    public string? SplashRelativePath { get; private init; }

    /// <summary>Why the index is absent or unusable, or null when it loaded.</summary>
    public string? Unavailable { get; private init; }

    public bool HasSplash => SplashRelativePath is not null;

    /// <summary>
    /// Relative path of one frame of a clip. Throws if the cue has no clip, so a
    /// caller cannot silently address media that was never decoded.
    /// </summary>
    public string FrameRelativePath(RetailStartupCue cue, int frameIndex)
    {
        if (!_frameFormats.TryGetValue(cue, out string? format))
        {
            throw new InvalidOperationException(
                $"Startup media has no decoded clip for {cue}.");
        }

        if (!_clips.TryGetValue(cue, out RetailStartupClip clip) ||
            frameIndex < 0 || frameIndex >= clip.FrameCount)
        {
            throw new ArgumentOutOfRangeException(
                nameof(frameIndex),
                frameIndex,
                $"Frame index outside {cue}'s decoded range.");
        }

        // The format is "<dir>/f{0:D5}.png"; the index is 1-based on disk
        // because that is what `ffmpeg -i in.vid out%05d.png` writes, and
        // renumbering it here would put a silent off-by-one between the cache
        // and any frame a human inspects with an image viewer.
        return string.Format(
            System.Globalization.CultureInfo.InvariantCulture, format, frameIndex + 1);
    }

    /// <summary>
    /// Reports that no media is available, with the reason. The sequence still
    /// runs; its beats are simply absent.
    /// </summary>
    public static RetailStartupMediaIndex Missing(string reason) =>
        new() { Unavailable = reason };

    /// <summary>
    /// Reads <c>startup-media.json</c> from <paramref name="root"/>. A malformed
    /// manifest, incomplete inventory, byte inventory that no longer matches
    /// the materializer receipt, or invalid edge-frame envelope is DROPPED
    /// rather than repaired. The supported Python producer performs the
    /// independent deep PNG validation before publishing this receipt.
    /// </summary>
    public static RetailStartupMediaIndex Load(string root, Func<string, bool> fileExists)
    {
        ArgumentNullException.ThrowIfNull(fileExists);

        if (string.IsNullOrWhiteSpace(root))
        {
            return Missing("No startup media cache directory was configured.");
        }

        string manifest = Path.Combine(root, "startup-media.json");
        if (!fileExists(manifest))
        {
            return Missing(
                $"No startup media index at {manifest}. Run " +
                "`py -3 rebuild/tools/materialize_retail_assets.py --startup-media`.");
        }

        JsonDocument document;
        try
        {
            document = JsonDocument.Parse(File.ReadAllText(manifest));
        }
        catch (Exception exception)
        {
            return Missing($"Startup media index at {manifest} is unreadable: {exception.Message}");
        }

        using (document)
        {
            JsonElement rootElement = document.RootElement;
            if (rootElement.ValueKind != JsonValueKind.Object ||
                !rootElement.TryGetProperty("schema", out JsonElement schema) ||
                schema.ValueKind != JsonValueKind.String ||
                schema.GetString() != Schema)
            {
                return Missing(
                    $"Startup media index at {manifest} is not schema '{Schema}'.");
            }

            var index = new RetailStartupMediaIndex
            {
                Root = root,
                SplashRelativePath = ReadSplash(rootElement, root, fileExists),
            };

            if (rootElement.TryGetProperty("clips", out JsonElement clips) &&
                clips.ValueKind == JsonValueKind.Object)
            {
                foreach (JsonProperty clip in clips.EnumerateObject())
                {
                    if (!Enum.TryParse(clip.Name, out RetailStartupCue cue))
                    {
                        continue;
                    }

                    try
                    {
                        int frameCount = clip.Value.GetProperty("frameCount").GetInt32();
                        int numerator = clip.Value.GetProperty("fpsNumerator").GetInt32();
                        int denominator = clip.Value.GetProperty("fpsDenominator").GetInt32();
                        int width = clip.Value.GetProperty("width").GetInt32();
                        int height = clip.Value.GetProperty("height").GetInt32();
                        string format = clip.Value.GetProperty("framePathFormat").GetString()
                            ?? string.Empty;
                        string framesSha256 = clip.Value.GetProperty("framesSha256").GetString()
                            ?? string.Empty;

                        if (frameCount <= 0 || numerator <= 0 || denominator <= 0 ||
                            width <= 0 || height <= 0 || format.Length == 0 ||
                            framesSha256.Length != 64)
                        {
                            continue;
                        }

                        bool complete = true;
                        var framePaths = new List<string>(frameCount);
                        for (int frame = 1; frame <= frameCount; frame++)
                        {
                            string relative = string.Format(
                                System.Globalization.CultureInfo.InvariantCulture,
                                format,
                                frame);
                            string framePath = Path.Combine(root, relative);
                            if (!fileExists(framePath))
                            {
                                complete = false;
                                break;
                            }
                            framePaths.Add(framePath);
                        }
                        if (complete)
                        {
                            string first = Path.Combine(
                                root,
                                string.Format(
                                    System.Globalization.CultureInfo.InvariantCulture,
                                    format,
                                    1));
                            string last = Path.Combine(
                                root,
                                string.Format(
                                    System.Globalization.CultureInfo.InvariantCulture,
                                    format,
                                    frameCount));
                            complete =
                                HasExpectedPngEnvelope(first, width, height) &&
                                HasExpectedPngEnvelope(last, width, height) &&
                                string.Equals(
                                    ComputeFrameSetSha256(framePaths),
                                    framesSha256,
                                    StringComparison.OrdinalIgnoreCase);
                        }
                        if (!complete)
                        {
                            continue;
                        }

                        index._clips[cue] = new RetailStartupClip(
                            frameCount, numerator, denominator, width, height);
                        index._frameFormats[cue] = format;
                    }
                    catch (InvalidOperationException)
                    {
                        // One malformed clip is absent; it does not invalidate
                        // independently complete clips in the same local cache.
                    }
                    catch (FormatException)
                    {
                    }
                    catch (OverflowException)
                    {
                    }
                    catch (KeyNotFoundException)
                    {
                    }
                    catch (IOException)
                    {
                    }
                    catch (UnauthorizedAccessException)
                    {
                    }
                }
            }

            if (index._clips.Count == 0 && index.SplashRelativePath is null)
            {
                return Missing(
                    $"Startup media index at {manifest} listed no usable clip or still.");
            }

            return index;
        }
    }

    private static string? ReadSplash(
        JsonElement rootElement, string root, Func<string, bool> fileExists)
    {
        if (rootElement.ValueKind != JsonValueKind.Object ||
            !rootElement.TryGetProperty("stills", out JsonElement stills) ||
            stills.ValueKind != JsonValueKind.Object ||
            !stills.TryGetProperty(nameof(RetailStartupCue.Splash), out JsonElement splash) ||
            splash.ValueKind != JsonValueKind.Object ||
            !splash.TryGetProperty("path", out JsonElement path) ||
            path.ValueKind != JsonValueKind.String ||
            !splash.TryGetProperty("outputSha256", out JsonElement outputSha256) ||
            outputSha256.ValueKind != JsonValueKind.String)
        {
            return null;
        }

        string? relative = path.GetString();
        string? expectedSha256 = outputSha256.GetString();
        string splashPath = Path.Combine(root, relative ?? string.Empty);
        if (string.IsNullOrWhiteSpace(relative) ||
            expectedSha256?.Length != 64 ||
            !fileExists(splashPath) ||
            !HasExpectedPngEnvelope(splashPath, 512, 512) ||
            !HasSha256(splashPath, expectedSha256))
        {
            return null;
        }

        return relative;
    }

    private static bool HasSha256(string path, string expectedSha256)
    {
        try
        {
            using FileStream stream = File.OpenRead(path);
            return string.Equals(
                Convert.ToHexString(SHA256.HashData(stream)),
                expectedSha256,
                StringComparison.OrdinalIgnoreCase);
        }
        catch (IOException)
        {
            return false;
        }
        catch (UnauthorizedAccessException)
        {
            return false;
        }
    }

    private static bool HasExpectedPngEnvelope(
        string path,
        int expectedWidth,
        int expectedHeight)
    {
        try
        {
            using FileStream stream = File.OpenRead(path);
            Span<byte> signatureBytes = stackalloc byte[8];
            stream.ReadExactly(signatureBytes);
            ReadOnlySpan<byte> signature =
                [0x89, (byte)'P', (byte)'N', (byte)'G', 0x0D, 0x0A, 0x1A, 0x0A];
            if (!signatureBytes.SequenceEqual(signature))
            {
                return false;
            }

            bool firstChunk = true;
            bool sawHeader = false;
            bool sawImagePayload = false;
            Span<byte> chunkHeader = stackalloc byte[8];
            Span<byte> headerPayload = stackalloc byte[13];
            Span<byte> crc = stackalloc byte[4];
            for (int chunk = 0; chunk < 4096; chunk++)
            {
                stream.ReadExactly(chunkHeader);
                uint length =
                    System.Buffers.Binary.BinaryPrimitives.ReadUInt32BigEndian(chunkHeader[..4]);
                ReadOnlySpan<byte> kind = chunkHeader[4..8];
                if (stream.Position + length + 4L > stream.Length)
                {
                    return false;
                }

                if (kind.SequenceEqual("IHDR"u8))
                {
                    if (!firstChunk || length != 13)
                    {
                        return false;
                    }
                    stream.ReadExactly(headerPayload);
                    if (System.Buffers.Binary.BinaryPrimitives.ReadUInt32BigEndian(
                            headerPayload[..4]) !=
                            (uint)expectedWidth ||
                        System.Buffers.Binary.BinaryPrimitives.ReadUInt32BigEndian(
                            headerPayload[4..8]) !=
                            (uint)expectedHeight)
                    {
                        return false;
                    }
                    sawHeader = true;
                }
                else
                {
                    stream.Seek(length, SeekOrigin.Current);
                }

                stream.ReadExactly(crc);
                if (kind.SequenceEqual("IDAT"u8) && length > 0)
                {
                    sawImagePayload = true;
                }
                if (kind.SequenceEqual("IEND"u8))
                {
                    return length == 0 &&
                        sawHeader &&
                        sawImagePayload &&
                        stream.Position == stream.Length;
                }
                firstChunk = false;
            }
            return false;
        }
        catch (IOException)
        {
            return false;
        }
        catch (UnauthorizedAccessException)
        {
            return false;
        }
    }

    private static string ComputeFrameSetSha256(IReadOnlyList<string> paths)
    {
        using IncrementalHash digest =
            IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        digest.AppendData(FrameSetDomain);
        byte[] separator = [0];
        byte[] buffer = new byte[1024 * 1024];
        foreach (string path in paths)
        {
            digest.AppendData(Encoding.ASCII.GetBytes(Path.GetFileName(path)));
            digest.AppendData(separator);
            long length = new FileInfo(path).Length;
            digest.AppendData(Encoding.ASCII.GetBytes(
                length.ToString(System.Globalization.CultureInfo.InvariantCulture)));
            digest.AppendData(separator);
            using FileStream stream = File.OpenRead(path);
            int read;
            while ((read = stream.Read(buffer, 0, buffer.Length)) > 0)
            {
                digest.AppendData(buffer, 0, read);
            }
        }
        return Convert.ToHexString(digest.GetHashAndReset());
    }
}
