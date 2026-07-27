// SPDX-License-Identifier: GPL-3.0-or-later

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
    public const string Schema = "onslaught-startup-media.v1";

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
    /// Reads <c>startup-media.json</c> from <paramref name="root"/>. Any
    /// malformed or partially-decoded entry is DROPPED with a reason rather
    /// than repaired, so a broken cache produces an absent beat instead of a
    /// plausible-looking wrong one.
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
            if (!rootElement.TryGetProperty("schema", out JsonElement schema) ||
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

            if (rootElement.TryGetProperty("clips", out JsonElement clips))
            {
                foreach (JsonProperty clip in clips.EnumerateObject())
                {
                    if (!Enum.TryParse(clip.Name, out RetailStartupCue cue))
                    {
                        continue;
                    }

                    int frameCount = clip.Value.GetProperty("frameCount").GetInt32();
                    int numerator = clip.Value.GetProperty("fpsNumerator").GetInt32();
                    int denominator = clip.Value.GetProperty("fpsDenominator").GetInt32();
                    int width = clip.Value.GetProperty("width").GetInt32();
                    int height = clip.Value.GetProperty("height").GetInt32();
                    string format = clip.Value.GetProperty("framePathFormat").GetString()
                        ?? string.Empty;

                    if (frameCount <= 0 || numerator <= 0 || denominator <= 0 ||
                        width <= 0 || height <= 0 || format.Length == 0)
                    {
                        continue;
                    }

                    // Spot-check the ends rather than trusting the count. A
                    // truncated decode is the failure this catches, and it is
                    // exactly the class that produced the half-rate FEBack strip.
                    string first = string.Format(
                        System.Globalization.CultureInfo.InvariantCulture, format, 1);
                    string last = string.Format(
                        System.Globalization.CultureInfo.InvariantCulture, format, frameCount);
                    if (!fileExists(Path.Combine(root, first)) ||
                        !fileExists(Path.Combine(root, last)))
                    {
                        continue;
                    }

                    index._clips[cue] = new RetailStartupClip(
                        frameCount, numerator, denominator, width, height);
                    index._frameFormats[cue] = format;
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
        if (!rootElement.TryGetProperty("stills", out JsonElement stills) ||
            !stills.TryGetProperty(nameof(RetailStartupCue.Splash), out JsonElement splash) ||
            !splash.TryGetProperty("path", out JsonElement path))
        {
            return null;
        }

        string? relative = path.GetString();
        if (string.IsNullOrWhiteSpace(relative) ||
            !fileExists(Path.Combine(root, relative)))
        {
            return null;
        }

        return relative;
    }
}
