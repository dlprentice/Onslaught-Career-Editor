// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.IO.Compression;
using System.Text;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the Level 100 water colour envelope against retail pixels.
///
/// <para><b>Why this exists.</b> On 2026-07-25 the reconstruction's water was
/// clipping to pure white and had lost retail's B &gt; G &gt; R hue rule. Two
/// uncited passes were responsible, and both had passed code review: an
/// additive second draw of the shoreline that re-applied <c>water-waves</c>
/// (the only water texture with a hue) on top of a primary pass that already
/// consumed it, and a <c>D3DTOP_MULTIPLYADD</c> stage whose operands were
/// mapped as <c>waves + diffuse * current</c> instead of
/// <c>waves * diffuse + current</c>. Reviewing the shader could not catch
/// either. Only pixels could.</para>
///
/// <para><b>The retail envelope.</b> Measured over
/// <c>local-lab/retail-reference-pristine/level100-gameplay/opening-pan-run1</c>
/// at the four matched level offsets t0+2 / 256 / 499 / 749 ms, in three
/// rectangles that are open water for the whole of the opening pan:</para>
/// <code>
///   box              n       median          p99             max         white  B&gt;G&gt;R
///   open-sea-right   37,400  (98,105,125)   (216,208,220)   (240,240,253)   0    88.1%
///   caustic-band     90,000  (91,109,130)   (223,206,217)   (252,246,243)   0    94.5%
///   mid-sea          25,600  (89, 92,109)   (153,155,178)   (181,191,203)   0    86.3%
/// </code>
/// <para>"white" is pixels at or above 250 on all three channels. Retail has
/// none, in any box, at any offset - consistent with the wider evidence pass
/// that found 0 of 180,000 sampled retail water pixels at 250+ on all
/// channels.</para>
///
/// <para><b>Scope.</b> This gate needs a locally produced gameplay capture,
/// which lives on an ignored path:</para>
/// <code>
///   pwsh -File rebuild/tools/Capture-Frontend.ps1 -Plan gameplay `
///       -RetailOffsetManifest local-lab/retail-reference-pristine/level100-gameplay/manifest.json
/// </code>
/// <para>Set <c>ONSLAUGHT_WATER_CAPTURE_DIR</c> to point at a specific one.
/// Otherwise the newest capture under <c>local-lab/godot-captures/</c> that is
/// at least as new as <c>Level100WaterAsset.cs</c> is scored; older captures
/// describe a build that no longer exists and are ignored, not judged.
/// If a directory is named but unusable the gate fails; if no capture exists at
/// all the pixel assertions cannot run, and
/// <see cref="ShorelineCompositionKeepsTheOperandOrderTheEnvelopeDependsOn"/>
/// is the always-on backstop for the two specific regressions above.</para>
/// </summary>
public sealed class Level100WaterEnvelopeTests
{
    private readonly record struct Box(string Name, int X0, int Y0, int X1, int Y1);

    /// <summary>Rectangles that are open water throughout the opening pan.</summary>
    private static readonly Box[] WaterBoxes =
    [
        new("open-sea-right", 430, 150, 600, 205),
        new("caustic-band", 0, 175, 250, 265),
        new("mid-sea", 260, 150, 420, 190),
    ];

    /// <summary>Retail-matched capture offsets, in level milliseconds.</summary>
    private static readonly int[] OffsetsMs = [2, 256, 499, 749];

    /// <summary>
    /// Retail has zero pixels at or above 250 on all three channels in any
    /// water box. No allowance: a single one means a stage saturated.
    /// </summary>
    private const int MaxWhitePixels = 0;

    /// <summary>
    /// Per-channel 99th-percentile ceiling. Retail's worst box reads
    /// (223,206,217); the evidence pass's stated ceiling over its wider sample
    /// was (231,213,228), which is what is used here so a slightly brighter but
    /// still retail-plausible water does not fail.
    /// </summary>
    private static readonly int[] P99Ceiling = [231, 213, 228];

    /// <summary>
    /// Retail's water hue rule. The measured retail fractions are 86.3 / 88.1 /
    /// 94.5 percent, so 85 sits just below the weakest retail box: a
    /// reconstruction that inverts the rule (the additive-waves defect scored
    /// 46-65 percent) fails, and retail itself passes.
    /// </summary>
    private const double MinBlueOverGreenOverRedFraction = 0.85;

    [Fact]
    public void CapturedWaterStaysInsideTheRetailEnvelope()
    {
        string? captureDirectory = ResolveCaptureDirectory();
        if (captureDirectory is null)
        {
            // No local gameplay capture on this machine. Say so out loud rather
            // than reporting a green gate that measured nothing.
            Assert.True(
                string.IsNullOrEmpty(
                    Environment.GetEnvironmentVariable("ONSLAUGHT_WATER_CAPTURE_DIR")),
                "ONSLAUGHT_WATER_CAPTURE_DIR is set but holds no gameplay capture " +
                "with level100-t000002ms.png.");
            return;
        }

        var failures = new List<string>();
        foreach (Box box in WaterBoxes)
        {
            List<(int R, int G, int B)> pixels = [];
            foreach (int offsetMs in OffsetsMs)
            {
                string file = Path.Combine(
                    captureDirectory,
                    string.Format(
                        CultureInfo.InvariantCulture,
                        "level100-t{0:D6}ms.png",
                        offsetMs));
                Assert.True(File.Exists(file), $"Capture is missing {file}.");
                pixels.AddRange(ReadBox(file, box));
            }

            Assert.NotEmpty(pixels);
            int white = pixels.Count(p => p.R >= 250 && p.G >= 250 && p.B >= 250);
            if (white > MaxWhitePixels)
            {
                failures.Add(
                    $"{box.Name}: {white} of {pixels.Count} px are >= 250 on all " +
                    $"channels; retail has 0. A water stage is saturating.");
            }

            int[] p99 =
            [
                Percentile(pixels.Select(p => p.R), 99),
                Percentile(pixels.Select(p => p.G), 99),
                Percentile(pixels.Select(p => p.B), 99),
            ];
            for (int channel = 0; channel < 3; channel++)
            {
                if (p99[channel] > P99Ceiling[channel])
                {
                    failures.Add(
                        $"{box.Name}: p99 channel {channel} is {p99[channel]}, over " +
                        $"the retail ceiling {P99Ceiling[channel]}.");
                }
            }

            double blueRule =
                pixels.Count(p => p.B > p.G && p.G > p.R) / (double)pixels.Count;
            if (blueRule < MinBlueOverGreenOverRedFraction)
            {
                failures.Add(
                    $"{box.Name}: only {blueRule:P1} of px satisfy B > G > R; retail " +
                    $"is 86-95%. A hue-bearing stage is over-contributing.");
            }
        }

        Assert.True(
            failures.Count == 0,
            $"Water capture '{captureDirectory}' left the retail envelope:{Environment.NewLine}" +
            string.Join(Environment.NewLine, failures));
    }

    /// <summary>
    /// Always-on backstop for the two specific compositions that produced the
    /// 2026-07-25 overbright water. This asserts on source text, which is not
    /// evidence that the product is correct - only
    /// <see cref="CapturedWaterStaysInsideTheRetailEnvelope"/> is. It exists so
    /// the exact defects that were measured cannot silently return on a machine
    /// with no capture.
    /// </summary>
    [Fact]
    public void ShorelineCompositionKeepsTheOperandOrderTheEnvelopeDependsOn()
    {
        string path = Path.Combine(
            AppContext.BaseDirectory,
            "godot-water-source",
            "Level100WaterAsset.cs");
        Assert.True(File.Exists(path), $"Water source was not copied to the test output: {path}");
        // Comment lines are dropped: the file documents the removed passes by
        // name, and a note about a defect must not read as the defect.
        string source = string.Join(
            '\n',
            File.ReadLines(path).Where(line => !line.TrimStart().StartsWith("//", StringComparison.Ordinal)));

        // D3DTOP_MULTIPLYADD is result = Arg1 * Arg2 + Arg0, i.e.
        // waves * diffuse + current. Adding the wave term outside the modulate
        // applies the only hue-bearing water texture at full strength
        // regardless of the shoreline vertex-colour ramp.
        Assert.Contains("(wave.rgb * COLOR.rgb) + base_water", source, StringComparison.Ordinal);
        Assert.DoesNotContain("wave.rgb + (COLOR.rgb * base_water)", source, StringComparison.Ordinal);

        // No additive water pass. No decoded D3DRS_SRCBLEND / DESTBLEND /
        // ALPHABLENDENABLE write exists anywhere in reverse-engineering/ for
        // the water, and an additive draw of the shoreline mesh doubled the
        // wave contribution.
        Assert.DoesNotContain("blend_add", source, StringComparison.Ordinal);

        // No opaque tint-constant slab on the water. #E8E8FF and the 0xc0
        // alpha test have no RE citation, and the pass wrote B = 255 where
        // retail's hard water maximum is 253 with zero all-channel whites.
        Assert.DoesNotContain("sun_reflection_color", source, StringComparison.Ordinal);
    }

    private static string? ResolveCaptureDirectory()
    {
        string? configured = Environment.GetEnvironmentVariable("ONSLAUGHT_WATER_CAPTURE_DIR");
        if (!string.IsNullOrWhiteSpace(configured))
        {
            return HasGameplayFrames(configured) ? configured : null;
        }

        string? repoRoot = FindRepositoryRoot();
        if (repoRoot is null)
        {
            return null;
        }
        string captureRoot = Path.Combine(repoRoot, "local-lab", "godot-captures");
        if (!Directory.Exists(captureRoot))
        {
            return null;
        }

        // A capture taken before the current water source is not evidence about
        // the current build, so it is ignored rather than judged. Without this,
        // any stale capture left in local-lab would fail an unrelated test run,
        // and a capture that predates a change would "prove" nothing either way.
        string waterSource = Path.Combine(
            repoRoot, "rebuild", "OnslaughtRebuild.Godot", "Level100WaterAsset.cs");
        DateTime floor = File.Exists(waterSource)
            ? File.GetLastWriteTimeUtc(waterSource)
            : DateTime.MinValue;

        return Directory.EnumerateDirectories(captureRoot)
            .Where(HasGameplayFrames)
            .Where(directory => File.GetLastWriteTimeUtc(
                Path.Combine(directory, "level100-t000002ms.png")) >= floor)
            .OrderByDescending(Directory.GetLastWriteTimeUtc)
            .FirstOrDefault();
    }

    private static bool HasGameplayFrames(string directory) =>
        File.Exists(Path.Combine(directory, "level100-t000002ms.png"));

    private static string? FindRepositoryRoot()
    {
        var directory = new DirectoryInfo(AppContext.BaseDirectory);
        while (directory is not null)
        {
            if (Directory.Exists(Path.Combine(directory.FullName, "rebuild")) &&
                File.Exists(Path.Combine(directory.FullName, "AGENTS.md")))
            {
                return directory.FullName;
            }
            directory = directory.Parent;
        }
        return null;
    }

    private static int Percentile(IEnumerable<int> values, int percentile)
    {
        int[] sorted = [.. values.Order()];
        int index = (int)Math.Round(
            (percentile / 100.0) * (sorted.Length - 1),
            MidpointRounding.AwayFromZero);
        return sorted[Math.Clamp(index, 0, sorted.Length - 1)];
    }

    private static List<(int R, int G, int B)> ReadBox(string pngPath, Box box)
    {
        (int width, int height, byte[] rgba) = DecodePng(File.ReadAllBytes(pngPath));
        Assert.True(
            box.X1 <= width && box.Y1 <= height,
            $"{pngPath} is {width}x{height}, too small for box {box.Name}.");
        var pixels = new List<(int R, int G, int B)>((box.X1 - box.X0) * (box.Y1 - box.Y0));
        for (int y = box.Y0; y < box.Y1; y++)
        {
            int row = y * width * 4;
            for (int x = box.X0; x < box.X1; x++)
            {
                int offset = row + (x * 4);
                pixels.Add((rgba[offset], rgba[offset + 1], rgba[offset + 2]));
            }
        }
        return pixels;
    }

    /// <summary>
    /// Minimal decoder for the exact PNG subset Godot's <c>Image.save_png</c>
    /// emits for a viewport readback: 8-bit, colour type 6 (RGBA), no
    /// interlacing. Anything else throws rather than being silently
    /// mis-measured. Kept local so the gate needs no image package.
    /// </summary>
    private static (int Width, int Height, byte[] Rgba) DecodePng(byte[] png)
    {
        ReadOnlySpan<byte> signature = [0x89, (byte)'P', (byte)'N', (byte)'G', 0x0D, 0x0A, 0x1A, 0x0A];
        Assert.True(png.Length > 8 && png.AsSpan(0, 8).SequenceEqual(signature), "Not a PNG.");

        int width = 0;
        int height = 0;
        using var idat = new MemoryStream();
        int position = 8;
        while (position + 8 <= png.Length)
        {
            int length = ReadBigEndianInt32(png, position);
            string type = Encoding.ASCII.GetString(png, position + 4, 4);
            int dataStart = position + 8;
            if (type == "IHDR")
            {
                width = ReadBigEndianInt32(png, dataStart);
                height = ReadBigEndianInt32(png, dataStart + 4);
                Assert.Equal(8, png[dataStart + 8]);
                Assert.Equal(6, png[dataStart + 9]);
                Assert.Equal(0, png[dataStart + 12]);
            }
            else if (type == "IDAT")
            {
                idat.Write(png, dataStart, length);
            }
            else if (type == "IEND")
            {
                break;
            }
            position = dataStart + length + 4;
        }

        Assert.True(width > 0 && height > 0, "PNG had no IHDR.");
        idat.Position = 0;
        using var inflate = new ZLibStream(idat, CompressionMode.Decompress);
        int stride = width * 4;
        var raw = new byte[(stride + 1) * height];
        int read = 0;
        while (read < raw.Length)
        {
            int got = inflate.Read(raw, read, raw.Length - read);
            if (got == 0)
            {
                break;
            }
            read += got;
        }
        Assert.Equal(raw.Length, read);

        var rgba = new byte[stride * height];
        for (int y = 0; y < height; y++)
        {
            int filter = raw[y * (stride + 1)];
            int source = (y * (stride + 1)) + 1;
            int target = y * stride;
            for (int x = 0; x < stride; x++)
            {
                int left = x >= 4 ? rgba[target + x - 4] : 0;
                int up = y > 0 ? rgba[target - stride + x] : 0;
                int upLeft = (x >= 4 && y > 0) ? rgba[target - stride + x - 4] : 0;
                int value = raw[source + x];
                rgba[target + x] = filter switch
                {
                    0 => (byte)value,
                    1 => (byte)(value + left),
                    2 => (byte)(value + up),
                    3 => (byte)(value + ((left + up) / 2)),
                    4 => (byte)(value + Paeth(left, up, upLeft)),
                    _ => throw new InvalidDataException($"Unsupported PNG filter {filter}."),
                };
            }
        }
        return (width, height, rgba);
    }

    private static int Paeth(int a, int b, int c)
    {
        int p = a + b - c;
        int pa = Math.Abs(p - a);
        int pb = Math.Abs(p - b);
        int pc = Math.Abs(p - c);
        if (pa <= pb && pa <= pc)
        {
            return a;
        }
        return pb <= pc ? b : c;
    }

    private static int ReadBigEndianInt32(byte[] data, int offset) =>
        (data[offset] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | data[offset + 3];
}
