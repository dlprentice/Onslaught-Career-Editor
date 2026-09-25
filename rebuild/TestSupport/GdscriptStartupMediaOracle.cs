// SPDX-License-Identifier: GPL-3.0-or-later
using System.Buffers.Binary;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.TestSupport;

/// <summary>
/// Differential media-index fixtures. Only synthetic files are created, in a
/// fresh child of the explicitly supplied task-owned output directory. No
/// canonical cache, installed asset, save, or corpus is located or accessed.
/// Core sequences follow RetailStartupSequenceTests and RetailLevel100CutsceneTests.
/// </summary>
public static class GdscriptStartupMediaOracle
{
    public static object Create(string outputRoot)
    {
        if (!Path.IsPathFullyQualified(outputRoot))
            throw new ArgumentException("A fully qualified owned fixture output root is required.", nameof(outputRoot));
        string owned = Path.Combine(outputRoot, "startup-media-fixtures-" + Guid.NewGuid().ToString("n"));
        Directory.CreateDirectory(owned);
        var rows = new List<object>();
        void Add(string name, Action<Fixture>? change = null, string format = "frames/f{0:D5}.png")
        {
            var fixture = new Fixture(Path.Combine(owned, name), format);
            change?.Invoke(fixture);
            fixture.WriteManifest();
            rows.Add(fixture.Observe(name));
        }

        Add("valid_frames_splash_audio");
        Add("last_frame_missing", f => File.Delete(f.Paths[2]));
        Add("middle_frame_missing", f => File.Delete(f.Paths[1]));
        Add("middle_frame_changed", f => File.WriteAllText(f.Paths[1], "changed synthetic frame"));
        Add("middle_not_png_but_receipted", f => { File.WriteAllText(f.Paths[1], "receipted middle bytes"); f.Receipt(); });
        Add("foreign_schema", f => f.Schema = "something-else");
        Add("legacy_schema", f => f.Schema = "onslaught-startup-media.v2");
        Add("missing_manifest", f => f.OmitManifest = true);
        Add("manifest_is_directory", f => f.ManifestDirectory = true);
        Add("empty_manifest", f => f.Raw = "");
        Add("array_root", f => f.Raw = "[]");
        Add("null_root", f => f.Raw = "null");
        Add("clips_wrong_shape", f => f.Raw = "{\"schema\":\"" + RetailStartupMediaIndex.Schema + "\",\"clips\":[]}");
        Add("trailing_comma", f => f.Raw = "{\"schema\":\"" + RetailStartupMediaIndex.Schema + "\",}");
        Add("comment_in_json", f => f.Raw = "{/*comment*/\"schema\":\"" + RetailStartupMediaIndex.Schema + "\"}");
        Add("duplicate_schema_last_wins", f => f.Raw = "{\"schema\":\"foreign\"," + f.Json()[1..]);
        Add("malformed_clip_keeps_other", f => f.ExtraClips.Add(("OpeningMontage", new { frameCount = "bad" })));
        Add("later_malformed_same_cue_keeps_prior", f => f.ExtraClips.Add(("LostToysLogo", new { frameCount = "bad" })));
        Add("later_video_retains_prior_audio", f =>
        {
            var replacement = new Dictionary<string, object?>(f.Clip);
            replacement["audio"] = new { track = "bad" };
            replacement["fpsNumerator"] = 30;
            f.ExtraClips.Add(("0", replacement));
        });
        foreach (string field in new[] { "frameCount", "fpsNumerator", "fpsDenominator", "width", "height" })
            Add("nonpositive_" + field, f => { f.Clip[field] = 0; f.Stills.Clear(); });
        Add("fractional_integer_token", f => f.Raw = f.Json().Replace("\"frameCount\":3", "\"frameCount\":3.0", StringComparison.Ordinal));
        Add("exponent_integer_token", f => f.Raw = f.Json().Replace("\"frameCount\":3", "\"frameCount\":3e0", StringComparison.Ordinal));
        Add("overflow_integer_token", f => f.Clip["frameCount"] = 2147483648L);
        Add("null_frame_format", f => f.Clip["framePathFormat"] = null);
        Add("malformed_composite", f => f.Clip["framePathFormat"] = "frames/f{1:D5}.png");
        Add("hash_wrong_length", f => f.Clip["framesSha256"] = new string('A', 63));
        Add("hash_not_hex", f => f.Clip["framesSha256"] = new string('z', 64));
        Add("hash_lowercase", f => f.Clip["framesSha256"] = ((string)f.Clip["framesSha256"]!).ToLowerInvariant());
        Add("nul_schema", f => f.Schema += "\0suffix");
        Add("nul_frame_hash_64_units", f => f.Clip["framesSha256"] = "\0" + ((string)f.Clip["framesSha256"]!)[1..]);
        Add("nul_audio_hash_64_units", f => f.Audio["outputSha256"] = "\0" + ((string)f.Audio["outputSha256"]!)[1..]);
        Add("nul_splash_hash_64_units", f => f.Stills["Splash"] = new
        {
            path = "splash.png", outputSha256 = "\0" + Hash(Path.Combine(f.Root, "splash.png"))[1..],
        });

        foreach (string cue in new[] { "0", "+1", " 2 ", "-1", "99", "2147483647", "-2147483648",
            "LostToysLogo, OpeningMontage", "LostToysLogo, Splash", "losttoyslogo", "Unknown", "2147483648", "1,2", "\u2003Level100IntroCutscene\u2003" })
        {
            int number = rows.Count;
            Add("cue_" + number, f => f.Cue = cue);
        }
        foreach (string cue in new[] { "\0LostToysLogo", "LostToysLogo\0", "0\0", "0\0\0", "+1 \0",
            "0\0 ", "\u20030\0", "0\u2003", "LostToysLogo,\0OpeningMontage", "2147483648\0" })
        {
            int number = rows.Count;
            Add("raw_cue_" + number, f => f.Cue = cue);
        }
        Add("unicode_basename_bmp", format: "frames/é-f{0:D5}.png");
        Add("unicode_basename_astral", format: "frames/🚀-f{0:D5}.png");
        Add("literal_backslash_name", format: "frames/literal\\f{0:D5}.png");
        Add("literal_backslash_with_normalized_decoy", f => f.NormalizedDecoys(false), format: "frames/literal\\f{0:D5}.png");
        Add("literal_backslash_missing_with_normalized_decoy", f => f.NormalizedDecoys(true), format: "frames/literal\\f{0:D5}.png");
        Add("constant_frame_name", format: "frames/same.png");
        Add("composite_alignment_braces", format: "frames/{{frame}}-{0,4:D2}.png");
        Add("absolute_frame_path", f => f.SetFormat(Path.Combine(f.Root, "absolute/f{0:D5}.png")));
        Add("parent_relative_frame_path", f => f.SetFormat("../owned-parent-frames/f{0:D5}.png"));
        Add("nul_decimal_spec_terminator", format: "frames/f{0:D5\0ignored}.png");
        Add("nul_exponent_spec_terminator", format: "frames/f{0:E\0ignored}.png");
        // Existing prefix files remain intact. A reader that truncates NUL can
        // accidentally admit them; the expected outcomes and complete callback
        // paths below make that regression observable without an invalid write.
        foreach (string mode in new[] { "real", "nul_true", "nul_io", "nul_argument" })
        {
            Add("nul_root_" + mode, f => { f.LoadRoot = f.Root + "\0suffix"; f.ExistsMode = mode; });
            Add("nul_frame_path_" + mode, f => { f.Clip["framePathFormat"] = "frames/f{0:D5}.png\0suffix"; f.ExistsMode = mode; });
            Add("nul_audio_path_" + mode, f => { f.Audio["path"] = "voice.wav\0suffix"; f.ExistsMode = mode; });
            Add("nul_splash_path_" + mode, f =>
            {
                f.Stills["Splash"] = new { path = "splash.png\0suffix", outputSha256 = Hash(Path.Combine(f.Root, "splash.png")) };
                f.ExistsMode = mode;
            });
        }

        foreach ((string name, Func<byte[], byte[]> mutate) in new (string, Func<byte[], byte[]>)[]
        {
            ("bad_signature", bytes => { bytes[0] = 0; return bytes; }),
            ("truncated", bytes => bytes[..7]),
            ("header_only", bytes => bytes[..33]),
            ("wrong_dimensions", bytes => { BinaryPrimitives.WriteUInt32BigEndian(bytes.AsSpan(16), 481); return bytes; }),
            ("trailing_bytes", bytes => [.. bytes, 0]),
            ("no_payload", _ => Png(480, 300, payload: [])),
            ("duplicate_header", _ => Png(480, 300, duplicateHeader: true)),
            ("oversized_chunk", bytes => { BinaryPrimitives.WriteUInt32BigEndian(bytes.AsSpan(33), uint.MaxValue); return bytes; }),
            ("unknown_chunk_accepted", _ => Png(480, 300, paddingChunks: 1)),
            ("chunk_limit_accepted", _ => Png(480, 300, paddingChunks: 4093)),
            ("chunk_limit_rejected", _ => Png(480, 300, paddingChunks: 4094)),
        })
            Add("png_" + name, f => { File.WriteAllBytes(f.Paths[0], mutate(File.ReadAllBytes(f.Paths[0]))); f.Receipt(); });

        Add("splash_tampered", f => File.AppendAllText(Path.Combine(f.Root, "splash.png"), "changed"));
        Add("splash_no_receipt", f => f.Stills["Splash"] = new { path = "splash.png" });
        Add("splash_wrong_dimensions", f =>
        {
            string path = Path.Combine(f.Root, "splash.png");
            File.WriteAllBytes(path, Png(480, 300));
            f.Stills["Splash"] = new { path = "splash.png", outputSha256 = Hash(path) };
        });
        Add("audio_tampered", f => File.AppendAllText(f.AudioPath, "changed"));
        Add("audio_bad_declaration", f => f.Audio["sampleFrameCount"] = long.MaxValue);
        Add("audio_fractional_count", f => f.Raw = f.Json().Replace("\"sampleFrameCount\":64", "\"sampleFrameCount\":64.0", StringComparison.Ordinal));
        Add("audio_bad_metadata_type", f => f.Audio["track"] = "bad");
        Add("audio_missing_file", f => File.Delete(f.AudioPath));
        foreach ((string name, int offset, uint value, bool halfWord) in new[]
        {
            ("riff_length", 4, 1u, false), ("format_length", 16, 18u, false),
            ("format_tag", 20, 3u, true), ("channels_zero", 22, 0u, true),
            ("rate_zero", 24, 0u, false), ("byte_rate", 28, 1u, false),
            ("block_align", 32, 3u, true), ("bits", 34, 12u, true), ("data_length", 40, 1u, false),
        })
            Add("wav_" + name, f =>
            {
                byte[] bytes = File.ReadAllBytes(f.AudioPath);
                if (halfWord) BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(offset), (ushort)value);
                else BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(offset), value);
                File.WriteAllBytes(f.AudioPath, bytes);
                f.Audio["outputSha256"] = Hash(f.AudioPath);
            });
        Add("wav_uint32_byte_rate_wrap", f =>
        {
            File.WriteAllBytes(f.AudioPath, Wav(1_000_000_000, 4, 64));
            f.Audio["sampleRate"] = 1_000_000_000;
            f.Audio["channels"] = 4;
            f.Audio["outputSha256"] = Hash(f.AudioPath);
        });
        foreach ((string name, Encoding encoding) in new (string, Encoding)[]
        {
            ("utf8_bom", new UTF8Encoding(true)), ("utf16_le", new UnicodeEncoding(false, true)),
            ("utf16_be", new UnicodeEncoding(true, true)), ("utf32_le", new UTF32Encoding(false, true)),
            ("utf32_be", new UTF32Encoding(true, true)),
        })
            Add(name, f => f.Encoding = encoding);
        Add("invalid_utf8_replacement", f => f.InvalidUtf8 = true, format: "frames/�-f{0:D5}.png");
        Add("escaped_surrogate_schema", f => f.Raw = f.Json().Replace(RetailStartupMediaIndex.Schema, "\\ud800", StringComparison.Ordinal));
        Add("escaped_surrogate_clip_name", f => f.Raw = f.Json().Replace("LostToysLogo", "\\ud800", StringComparison.Ordinal));
        Add("escaped_surrogate_clip_value", f => f.Raw = f.Json().Replace("frames/f{0:D5}.png", "\\ud800", StringComparison.Ordinal));
        Add("escaped_surrogate_splash_path", f => f.Raw = f.Json().Replace("\"path\":\"splash.png\"", "\"path\":\"\\ud800\"", StringComparison.Ordinal));

        foreach (string mode in new[] { "none", "manifest_io", "frame_io", "frame_argument", "audio_io" })
            Add("exists_" + mode, f => f.ExistsMode = mode);
        Add("root_relative", f => f.LoadRoot = Path.GetRelativePath(Environment.CurrentDirectory, f.Root));
        Add("root_null", f => f.LoadRoot = null);
        Add("root_whitespace", f => f.LoadRoot = "\u2003 \t");
        Add("null_callback", f => f.ExistsMode = "null");

        var files = Directory.EnumerateFiles(owned, "*", SearchOption.AllDirectories)
            .OrderBy(path => path, StringComparer.Ordinal).Select(path => new { path, sha256 = Hash(path) }).ToArray();
        return new { schema = 1, root = owned, cases = rows, files };
    }

    private sealed class Fixture
    {
        public string Root { get; }
        public string? LoadRoot { get; set; }
        public string Schema { get; set; } = RetailStartupMediaIndex.Schema;
        public string Cue { get; set; } = "LostToysLogo";
        public Dictionary<string, object?> Clip { get; } = [];
        public Dictionary<string, object?> Audio { get; } = [];
        public Dictionary<string, object?> Stills { get; } = [];
        public List<(string Name, object? Value)> ExtraClips { get; } = [];
        public string[] Paths { get; private set; } = [];
        public string AudioPath => Path.Combine(Root, "voice.wav");
        public string? Raw { get; set; }
        public Encoding Encoding { get; set; } = new UTF8Encoding(false);
        public bool InvalidUtf8 { get; set; }
        public bool OmitManifest { get; set; }
        public bool ManifestDirectory { get; set; }
        public string ExistsMode { get; set; } = "real";

        public Fixture(string root, string format)
        {
            Root = root;
            LoadRoot = root;
            Directory.CreateDirectory(root);
            Clip["frameCount"] = 3; Clip["fpsNumerator"] = 25; Clip["fpsDenominator"] = 1;
            Clip["width"] = 480; Clip["height"] = 300;
            SetFormat(format);
            File.WriteAllBytes(AudioPath, Wav(44_100, 2, 64));
            Audio["track"] = 0; Audio["sampleRate"] = 44_100; Audio["channels"] = 2;
            Audio["bitsPerSample"] = 16; Audio["sampleFrameCount"] = 64L;
            Audio["path"] = "voice.wav"; Audio["outputSha256"] = Hash(AudioPath);
            Clip["audio"] = Audio;
            string splash = Path.Combine(root, "splash.png");
            File.WriteAllBytes(splash, Png(512, 512));
            Stills["Splash"] = new { path = "splash.png", outputSha256 = Hash(splash) };
        }

        public void SetFormat(string format)
        {
            Clip["framePathFormat"] = format;
            Paths = Enumerable.Range(1, 3).Select(frame => Path.Combine(Root,
                string.Format(System.Globalization.CultureInfo.InvariantCulture, format, frame))).ToArray();
            foreach (string path in Paths)
            {
                Directory.CreateDirectory(Path.GetDirectoryName(path)!);
                File.WriteAllBytes(path, Png(480, 300));
            }
            Receipt();
        }

        public void Receipt() => Clip["framesSha256"] = FrameHash(Paths);

        public void NormalizedDecoys(bool removeOriginal)
        {
            if (OperatingSystem.IsWindows()) return; // Backslash is a separator there.
            foreach (string original in Paths)
            {
                string alias = original.Replace('\\', '/');
                Directory.CreateDirectory(Path.GetDirectoryName(alias)!);
                // The missing-original case is deliberately byte-identical: a
                // normalizing reader would falsely admit its wrong target.
                File.WriteAllBytes(alias, removeOriginal ? File.ReadAllBytes(original) : Png(480, 300, payload: [9]));
                if (removeOriginal) File.Delete(original);
            }
        }

        public string Json()
        {
            var clips = new List<(string Name, object? Value)> { (Cue, Clip) };
            clips.AddRange(ExtraClips);
            return "{\"schema\":" + JsonSerializer.Serialize(Schema) + ",\"clips\":{" +
                string.Join(",", clips.Select(pair => JsonSerializer.Serialize(pair.Name) + ":" + JsonSerializer.Serialize(pair.Value))) +
                "},\"stills\":" + JsonSerializer.Serialize(Stills) + "}";
        }

        public void WriteManifest()
        {
            string manifest = Path.Combine(Root, "startup-media.json");
            if (OmitManifest) return;
            if (ManifestDirectory) { Directory.CreateDirectory(manifest); return; }
            string json = Raw ?? Json();
            if (InvalidUtf8)
            {
                json = json.Replace("\\uFFFD", "�", StringComparison.OrdinalIgnoreCase);
                byte[] bytes = System.Text.Encoding.UTF8.GetBytes(json);
                var replaced = new List<byte>();
                for (int index = 0; index < bytes.Length; index++)
                {
                    if (index + 2 < bytes.Length && bytes[index] == 239 && bytes[index + 1] == 191 && bytes[index + 2] == 189)
                    { replaced.Add(255); index += 2; }
                    else replaced.Add(bytes[index]);
                }
                File.WriteAllBytes(manifest, replaced.ToArray());
            }
            else File.WriteAllBytes(manifest, [.. Encoding.GetPreamble(), .. Encoding.GetBytes(json)]);
        }

        public object Observe(string name)
        {
            var visits = new List<string>();
            bool Exists(string path)
            {
                visits.Add(path);
                if (ExistsMode == "none") return false;
                if (path.Contains('\0'))
                {
                    if (ExistsMode == "nul_true") return true;
                    if (ExistsMode == "nul_io") throw new IOException("fixture IO");
                    if (ExistsMode == "nul_argument") throw new ArgumentException("fixture argument");
                }
                if (ExistsMode == "manifest_io" && path.EndsWith("startup-media.json", StringComparison.Ordinal)) throw new IOException("fixture IO");
                if (path.Contains("frames/", StringComparison.Ordinal) || path.Contains("frames\\", StringComparison.Ordinal))
                {
                    if (ExistsMode == "frame_io") throw new IOException("fixture IO");
                    if (ExistsMode == "frame_argument") throw new ArgumentException("fixture argument");
                }
                if (ExistsMode == "audio_io" && path.EndsWith("voice.wav", StringComparison.Ordinal)) throw new IOException("fixture IO");
                return File.Exists(path);
            }
            object expected;
            var frames = new List<object>();
            var audio = new List<object>();
            try
            {
                var index = RetailStartupMediaIndex.Load(LoadRoot!, ExistsMode == "null" ? null! : Exists);
                expected = new { ok = true, value = State(index) };
                foreach (RetailStartupCue cue in index.Clips.Keys.Append((RetailStartupCue)99).Distinct())
                {
                    int count = index.Clips.TryGetValue(cue, out RetailStartupClip clip) ? clip.FrameCount : 1;
                    foreach (int frame in new[] { -1, 0, count - 1, count }.Distinct())
                        frames.Add(new { cue = (int)cue, frame, result = Attempt(() => index.FrameRelativePath(cue, frame)) });
                }
                foreach (RetailStartupCue cue in index.Clips.Keys.Append((RetailStartupCue)99).Distinct())
                    audio.Add(new { cue = (int)cue, result = Attempt(() => index.AudioRelativePath(cue)) });
            }
            catch (Exception error) { expected = new { ok = false, error_type = error.GetType().Name }; }
            // JSON input itself stays lossless in a native Godot runner: every
            // potentially raw .NET string crosses the oracle as UTF-16 units.
            return new { name, root_units = LoadRoot is null ? null : Units(LoadRoot), exists_mode = ExistsMode,
                expected, visits = visits.Select(Units).ToArray(), frames, audio };
        }
    }

    private static object State(RetailStartupMediaIndex index) => new
    {
        root_units = Units(index.Root), has_splash = index.HasSplash,
        splash_relative_units = index.SplashRelativePath is null ? null : Units(index.SplashRelativePath),
        unavailable = Unavailable(index.Unavailable), unavailable_identity_units = UnavailableIdentity(index.Unavailable),
        clips = index.Clips.Select(pair => new { cue = (int)pair.Key, frame_count = pair.Value.FrameCount,
            fps_numerator = pair.Value.FramesPerSecondNumerator, fps_denominator = pair.Value.FramesPerSecondDenominator,
            width = pair.Value.Width, height = pair.Value.Height }).ToArray(),
        audio = index.ClipAudio.Select(pair => new { cue = (int)pair.Key, track = pair.Value.Track,
            sample_rate = pair.Value.SampleRate, channels = pair.Value.Channels, bits_per_sample = pair.Value.BitsPerSample,
            sample_frame_count = pair.Value.SampleFrameCount }).ToArray(),
    };

    private static string? Unavailable(string? text) => text is null ? null :
        text.StartsWith("No startup media cache", StringComparison.Ordinal) ? "no_root" :
        text.StartsWith("No startup media index", StringComparison.Ordinal) ? "missing" :
        text.Contains(" is unreadable:", StringComparison.Ordinal) ? "unreadable" :
        text.Contains(" is not schema ", StringComparison.Ordinal) ? "schema" :
        text.Contains(" listed no usable ", StringComparison.Ordinal) ? "empty" : "unknown";

    private static int[]? UnavailableIdentity(string? text)
    {
        if (text is null) return null;
        const string marker = " is unreadable:";
        int at = text.IndexOf(marker, StringComparison.Ordinal);
        // The exception's human message is platform/runtime-specific. Preserve
        // every unit before it, including NUL in the manifest path.
        return Units(at < 0 ? text : text[..(at + marker.Length)]);
    }

    private static int[] Units(string text) => text.Select(unit => (int)unit).ToArray();

    private static object Attempt(Func<string> action)
    {
        try { return new { ok = true, value_units = Units(action()) }; }
        catch (Exception error) { return new { ok = false, error_type = error.GetType().Name }; }
    }

    private static string Hash(string path) => Convert.ToHexString(SHA256.HashData(File.ReadAllBytes(path)));
    private static string FrameHash(IEnumerable<string> paths)
    {
        using var digest = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        digest.AppendData("onslaught-startup-frame-set.v1\0"u8);
        foreach (string path in paths)
        {
            digest.AppendData(Encoding.ASCII.GetBytes(Path.GetFileName(path)));
            digest.AppendData([0]);
            digest.AppendData(Encoding.ASCII.GetBytes(new FileInfo(path).Length.ToString(System.Globalization.CultureInfo.InvariantCulture)));
            digest.AppendData([0]);
            digest.AppendData(File.ReadAllBytes(path));
        }
        return Convert.ToHexString(digest.GetHashAndReset());
    }

    private static byte[] Png(int width, int height, byte[]? payload = null, bool duplicateHeader = false, int paddingChunks = 0)
    {
        using var stream = new MemoryStream();
        stream.Write([137, 80, 78, 71, 13, 10, 26, 10]);
        byte[] header = new byte[13];
        BinaryPrimitives.WriteUInt32BigEndian(header, (uint)width);
        BinaryPrimitives.WriteUInt32BigEndian(header.AsSpan(4), (uint)height);
        header[8] = 8; header[9] = 2;
        void Chunk(string kind, byte[] data)
        {
            Span<byte> length = stackalloc byte[4];
            BinaryPrimitives.WriteUInt32BigEndian(length, (uint)data.Length);
            stream.Write(length); stream.Write(Encoding.ASCII.GetBytes(kind)); stream.Write(data); stream.Write(new byte[4]);
        }
        Chunk("IHDR", header);
        if (duplicateHeader) Chunk("IHDR", header);
        for (int index = 0; index < paddingChunks; index++) Chunk("tEST", []);
        Chunk("IDAT", payload ?? [1]); Chunk("IEND", []);
        return stream.ToArray();
    }

    private static byte[] Wav(int rate, int channels, int frames)
    {
        int align = channels * 2;
        var bytes = new byte[44 + frames * align];
        "RIFF"u8.CopyTo(bytes); "WAVEfmt "u8.CopyTo(bytes.AsSpan(8)); "data"u8.CopyTo(bytes.AsSpan(36));
        BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(4), (uint)(bytes.Length - 8));
        BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(16), 16);
        BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(20), 1);
        BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(22), (ushort)channels);
        BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(24), (uint)rate);
        BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(28), unchecked((uint)(rate * align)));
        BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(32), (ushort)align);
        BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(34), 16);
        BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(40), (uint)(bytes.Length - 44));
        for (int index = 44; index < bytes.Length; index++) bytes[index] = (byte)(index * 7);
        return bytes;
    }
}
