// SPDX-License-Identifier: GPL-3.0-or-later
using System.Buffers.Binary;
using System.IO.Compression;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.Json;
using System.Text.Json.Serialization;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Exact import-decoder comparison. The retained C# implementation is
/// the independent oracle; all malformed files are synthetic, fresh and user-local.</summary>
public sealed partial class AyaTextureChecks : Node
{
    private const string NativePath = "res://Scenes/Shared/retail_aya_texture.gd";
    private const string TruncatedPixels = "Curated texture has truncated DDS pixel data.";
    private const string ShortReadOrigin = "file_access_memory.cpp";
    private const string ManifestPath = "res://Assets/Level100/StaticWorld/level100-static-world.json";
    private const int SourceLimit = 2 * 1024 * 1024;
    private const int DecodedLimit = 8 * 1024 * 1024;
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower, WriteIndented = true };
    private readonly List<string> _failures = [];
    private readonly List<string> _completed = [];
    private readonly List<CaseReceipt> _cases = [];
    private readonly Dictionary<string, string> _inputHashes = new(StringComparer.Ordinal);
    private readonly Dictionary<string, string> _inputHashesAfter = new(StringComparer.Ordinal);
    private int _checks;
    private long _comparedBytes;
    private string? _outputDirectory;
    private string _godotVersion = "unavailable";
    private string _godotHash = "unavailable";
    private DiagnosticLogger? _logger;

    private sealed record Spec(string Name, string Path, int Width, int Height, int Compression,
        int? TargetFormat = null, int? MipCount = null, bool MustSucceed = false,
        string[]? DiagnosticOrigins = null, string? ExpectedNativeRefusal = null, string[]? LegacyDiagnosticOrigins = null);
    private sealed record ImageFacts(int Width, int Height, int Format, bool HasMipmaps, int MipmapCount,
        int ByteCount, string Sha256, [property: JsonIgnore] byte[] Bytes);
    private sealed record Outcome(bool Ok, string? ErrorType = null, string? Error = null, ImageFacts? Image = null);
    private sealed record CaseReceipt(Spec Spec, Outcome Legacy, Outcome Native, Outcome Facade,
        bool ContractPassed, bool IntentionalAdmissionDifference);
    private sealed record Diagnostic(string Case, string Phase, string Function, string File, int Line,
        string Code, string Rationale, int ErrorType, bool Expected);

    public override async void _Ready()
    {
        try
        {
            Require(!Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "AYA checks require a headless runtime.");
            using (D version = Engine.GetVersionInfo())
            using (Variant versionName = version["string"])
            using (Variant versionHash = version["hash"])
            {
                _godotVersion = versionName.AsString();
                _godotHash = versionHash.AsString();
            }
            _outputDirectory = CreateOwnedDirectory();
            _logger = new DiagnosticLogger();
            OS.AddLogger(_logger);
            Input.MouseModeEnum pointer = Input.MouseMode;
            List<Spec> imports = ImportSpecs();
            List<Spec> extras = ExtraSpecs();
            foreach (string path in imports.Concat(extras).Select(spec => spec.Path).Prepend(ManifestPath).Distinct(StringComparer.Ordinal))
                _inputHashes.Add(path, HashInput(path));
            Require(string.Equals(_inputHashes[ManifestPath], Level100ActorDefinitionManifest.ExpectedManifestSha256,
                StringComparison.OrdinalIgnoreCase), "The actual static manifest must retain its pinned identity.");

            using (GDScript script = GD.Load<GDScript>(NativePath))
            using (Variant created = script.New())
            using (RefCounted native = created.As<RefCounted>())
            {
                foreach (Spec spec in imports) Compare(spec, native);
                _completed.Add("47_import_uses");
                foreach (Spec spec in extras) Compare(spec, native);
                _completed.Add("cursor_and_fonts");
                foreach (Spec spec in SyntheticSpecs()) Compare(spec, native);
                _completed.Add("synthetic_admission");
            }

            var released = new List<(ulong Texture, ulong Image)>();
            foreach (Spec spec in extras)
                released.Add(ProbeFacadeLifetime(spec));
            // Godot may retain script call-stack temporaries until the next
            // process frame. Observe bounded release; do not force managed GC.
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            foreach ((ulong texture, ulong image) in released)
            {
                Check(!GodotObject.IsInstanceIdValid(texture), "Disposed facade texture remains in ObjectDB: " + texture);
                Check(!GodotObject.IsInstanceIdValid(image), "Disposed facade image remains in ObjectDB: " + image);
            }
            _completed.Add("facade_lifetime");
            Check(Input.MouseMode == pointer, "Texture admission changed pointer ownership.");
        }
        catch (Exception error)
        {
            _failures.Add("Harness aborted: " + error);
        }
        finally
        {
            // Preserve these checks even when an individual comparison or
            // fixture construction unexpectedly aborts the remaining sections.
            foreach ((string path, string before) in _inputHashes)
            {
                try
                {
                    string after = HashInput(path);
                    _inputHashesAfter.Add(path, after);
                    Check(after == before, "Private source changed: " + path);
                }
                catch (Exception error) { _failures.Add("Cannot recheck input '" + path + "': " + error.Message); }
            }
            if (_inputHashes.Count > 0) _completed.Add("private_inputs_unchanged");
            Diagnostic[] diagnostics = [];
            if (_logger is not null)
            {
                OS.RemoveLogger(_logger);
                diagnostics = _logger.Snapshot();
                _logger.Dispose();
                _logger = null;
            }
            foreach (Diagnostic diagnostic in diagnostics.Where(item => !item.Expected))
                _failures.Add($"Unexpected engine diagnostic in {diagnostic.Case}/{diagnostic.Phase}: {diagnostic.File}:{diagnostic.Line} {diagnostic.Code} {diagnostic.Rationale}");
            string[] required = ["47_import_uses", "cursor_and_fonts", "synthetic_admission", "facade_lifetime", "private_inputs_unchanged"];
            Check(required.All(_completed.Contains), "One or more required AYA sections did not complete.");
            var report = new
            {
                schema = 1, failureCount = _failures.Count, checks = _checks, caseCount = _cases.Count,
                runtime = RuntimeInformation.FrameworkDescription, godot = _godotVersion, godotHash = _godotHash,
                comparedBytes = _comparedBytes, completed = _completed, inputHashes = _inputHashes, inputHashesAfter = _inputHashesAfter,
                exactMatchCount = _cases.Count(item => item.ContractPassed && !item.IntentionalAdmissionDifference),
                intentionalAdmissionDifferenceCount = _cases.Count(item => item.IntentionalAdmissionDifference),
                intentionalAdmissionDifferences = _cases.Where(item => item.IntentionalAdmissionDifference).Select(item => item.Spec.Name).ToArray(),
                cases = _cases, diagnostics, failures = _failures,
            };
            try
            {
                if (_outputDirectory is not null)
                    File.WriteAllText(Path.Combine(_outputDirectory, "report.json"), JsonSerializer.Serialize(report, JsonOptions));
            }
            catch (Exception error) { _failures.Add("Cannot write report: " + error.Message); }
            GD.Print("AYA_TEXTURE_CHECKS " + JsonSerializer.Serialize(new
            {
                failure_count = _failures.Count, checks = _checks, case_count = _cases.Count,
                runtime = RuntimeInformation.FrameworkDescription, godot = _godotVersion, godot_hash = _godotHash,
                compared_bytes = _comparedBytes, expected_diagnostics = diagnostics.Count(item => item.Expected),
                unexpected_diagnostics = diagnostics.Count(item => !item.Expected), completed = _completed,
                intentional_admission_difference_count = _cases.Count(item => item.IntentionalAdmissionDifference),
                report = _outputDirectory is null ? null : Path.Combine(_outputDirectory, "report.json"),
            }));
            foreach (string failure in _failures) GD.Print("AYA_FAILURE " + failure);
            GetTree().Quit(_failures.Count == 0 ? 0 : 1);
        }
    }

    private List<Spec> ImportSpecs()
    {
        using JsonDocument manifest = JsonDocument.Parse(File.ReadAllBytes(ProjectSettings.GlobalizePath(ManifestPath)));
        JsonElement textures = Property(manifest.RootElement, "textures");
        Require(textures.ValueKind == JsonValueKind.Object, "Static texture table is not an object.");
        var result = new List<Spec>();
        foreach (JsonProperty row in textures.EnumerateObject())
        {
            JsonElement entry = row.Value;
            string compression = Property(entry, "compression").GetString()!;
            Require(Enum.TryParse(compression, false, out LegacyCuratedAyaTextureReference.Compression parsed),
                "Unknown actual manifest compression: " + compression);
            result.Add(new Spec("static/" + row.Name, Property(entry, "resourcePath").GetString()!,
                Property(entry, "width").GetInt32(), Property(entry, "height").GetInt32(), (int)parsed, MustSucceed: true));
        }
        Require(result.Count == 34, "The production manifest must contribute exactly 34 ordered texture uses.");
        foreach (string face in new[] { "cent", "up", "right", "down", "left" })
            result.Add(new Spec("sky/" + face, $"res://Assets/Level100/Sky/cube25-{face}.texture.aya", 512, 512, 0, MustSucceed: true));
        result.Add(new Spec("shared/chrome3", "res://Assets/Level100/StaticWorld/Textures/meshtex-chrome3.texture.aya", 128, 128, 1, MustSucceed: true));
        result.Add(new Spec("shared/overlay", "res://Assets/Level100/Textures/material-overlay-a8trust5.texture.aya", 128, 128, 1, MustSucceed: true));
        foreach (string name in new[] { "target-tank", "target-truck", "target-warehouse-m001", "target-warehouse-m002", "transporter-lifter01", "transporter-lifter02" })
            result.Add(new Spec("actor/" + name, $"res://Assets/Level100/Textures/{name}.texture.aya", 512, 512, 1, MustSucceed: true));
        Require(result.Count == 47, "All 47 actual import uses, including repeated shared inputs, must be compared.");
        return result;
    }

    private static List<Spec> ExtraSpecs() =>
    [
        new("cursor/rgba8-eight-levels", "res://Assets/Frontend/mouse-cursor.texture.aya", 128, 128, 1, (int)Image.Format.Rgba8, 8, true),
        new("font/font-13ps", "res://Assets/Hud/font-13ps.texture.aya", 256, 256, 2, MustSucceed: true),
        new("font/font-22", "res://Assets/Hud/font-22.texture.aya", 512, 512, 2, MustSucceed: true),
        new("pause/dxt2-circle", "res://Assets/PauseMenu/circle-01.texture.aya", 256, 256, 1, MustSucceed: true),
    ];

    private void Compare(Spec spec, RefCounted native)
    {
        Outcome legacy = Phase(spec, "legacy", () => Managed(spec, legacy: true));
        Outcome actual = Phase(spec, "native", () => Native(spec, native));
        Outcome facade = Phase(spec, "facade", () => Managed(spec, legacy: false));
        int failuresBefore = _failures.Count;
        if (spec.MustSucceed) Check(legacy.Ok, spec.Name + ": admitted control failed in independent C# oracle: " + legacy.Error);
        if (spec.ExpectedNativeRefusal is string strictMessage)
        {
            // The shared strict decoder intentionally refuses malformed zlib
            // that the legacy .NET reader sometimes accepted via read-ahead.
            // This is an explicit stronger-admission assertion, never a skip.
            Check(legacy.Ok || legacy.ErrorType == nameof(InvalidDataException), spec.Name + ": unexpected oracle failure type.");
            CheckStrictRefusal(spec.Name + "/native", actual, strictMessage);
            CheckStrictRefusal(spec.Name + "/facade", facade, strictMessage);
            // A pixel truncation refusal is only as strict as the loader: the
            // unchanged oracle must actually have read past the payload.
            if (strictMessage == TruncatedPixels)
                Check(_logger!.Logged(spec.Name, "legacy", ShortReadOrigin), spec.Name + ": truncation refused without a loader short read.");
        }
        else
        {
            CompareOutcome(spec.Name + "/native", legacy, actual);
            CompareOutcome(spec.Name + "/facade", legacy, facade);
        }
        bool passed = failuresBefore == _failures.Count;
        bool difference = spec.ExpectedNativeRefusal is not null && passed &&
            (legacy.Ok != actual.Ok || legacy.ErrorType != actual.ErrorType || legacy.Error != actual.Error);
        _cases.Add(new CaseReceipt(spec, WithoutBytes(legacy), WithoutBytes(actual), WithoutBytes(facade), passed, difference));
    }

    private Outcome Phase(Spec spec, string phase, Func<Outcome> action)
    {
        string[] origins = phase == "legacy"
            ? [.. spec.DiagnosticOrigins ?? [], .. spec.LegacyDiagnosticOrigins ?? []]
            : spec.DiagnosticOrigins ?? [];
        GD.Print("AYA_CASE_BEGIN " + JsonSerializer.Serialize(new { name = spec.Name, phase, expected_diagnostic_origins = origins }));
        _logger!.Begin(spec.Name, phase, origins);
        Outcome outcome;
        try { outcome = action(); }
        catch (Exception error) { outcome = new Outcome(false, error.GetType().Name, error.Message); }
        finally { _logger.End(); }
        GD.Print("AYA_CASE_END " + JsonSerializer.Serialize(new { name = spec.Name, phase, ok = outcome.Ok, error_type = outcome.ErrorType }));
        return outcome;
    }

    private static Outcome Managed(Spec spec, bool legacy)
    {
        Image.Format? target = spec.TargetFormat is int format ? (Image.Format)format : null;
        using Texture2D texture = legacy
            ? LegacyCuratedAyaTextureReference.Load(spec.Path, spec.Width, spec.Height,
                (LegacyCuratedAyaTextureReference.Compression)spec.Compression, target, spec.MipCount)
            : CuratedAyaTextureLoader.Load(spec.Path, spec.Width, spec.Height,
                (CuratedAyaTextureLoader.Compression)spec.Compression, target, spec.MipCount);
        return new Outcome(true, Image: Capture(texture));
    }

    private static Outcome Native(Spec spec, RefCounted loader)
    {
        using Variant target = spec.TargetFormat is int format ? Variant.From(format) : default;
        using Variant mips = spec.MipCount is int count ? Variant.From(count) : default;
        using Variant returned = loader.Call("load_texture_checked", spec.Path, spec.Width, spec.Height, spec.Compression, target, mips);
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native checked texture call did not return its result dictionary.");
        using D result = returned.AsGodotDictionary();
        using Variant ok = result["ok"];
        if (ok.VariantType != Variant.Type.Bool)
            throw new InvalidOperationException("Native checked texture call returned a non-Boolean ok field.");
        if (!ok.AsBool())
        {
            using Variant errorType = result["error_type"];
            using Variant error = result["error"];
            if (errorType.VariantType != Variant.Type.String || error.VariantType != Variant.Type.String)
                throw new InvalidOperationException("Native checked texture failure lacks explicit type/message.");
            return new Outcome(false, errorType.AsString(), error.AsString());
        }
        using Variant value = result["value"];
        using ImageTexture texture = value.As<ImageTexture>();
        return new Outcome(true, Image: Capture(texture));
    }

    private static ImageFacts Capture(Texture2D texture)
    {
        using Image image = texture.GetImage();
        byte[] bytes = image.GetData();
        return new ImageFacts(image.GetWidth(), image.GetHeight(), (int)image.GetFormat(), image.HasMipmaps(),
            image.GetMipmapCount(), bytes.Length, Hex(bytes), bytes);
    }

    private void CompareOutcome(string name, Outcome expected, Outcome actual)
    {
        Check(expected.Ok == actual.Ok, $"{name}: success differs; legacy={expected.Ok} native={actual.Ok}; {actual.Error}");
        if (!expected.Ok || !actual.Ok)
        {
            if (!expected.Ok && !actual.Ok)
            {
                Check(expected.ErrorType == actual.ErrorType, $"{name}: error type legacy='{expected.ErrorType}', actual='{actual.ErrorType}'.");
                Check(expected.Error == actual.Error, $"{name}: error message legacy='{expected.Error}', actual='{actual.Error}'.");
            }
            return;
        }
        ImageFacts left = expected.Image!, right = actual.Image!;
        Check(left.Width == right.Width && left.Height == right.Height, name + ": image dimensions differ.");
        Check(left.Format == right.Format, $"{name}: image format legacy={left.Format}, actual={right.Format}.");
        Check(left.HasMipmaps == right.HasMipmaps && left.MipmapCount == right.MipmapCount,
            $"{name}: mip chain legacy={left.HasMipmaps}/{left.MipmapCount}, actual={right.HasMipmaps}/{right.MipmapCount}.");
        _comparedBytes += left.Bytes.Length;
        Check(left.Bytes.AsSpan().SequenceEqual(right.Bytes),
            $"{name}: full image bytes differ; legacy={left.ByteCount}/{left.Sha256}, actual={right.ByteCount}/{right.Sha256}.");
    }

    private static Outcome WithoutBytes(Outcome value) => value.Image is null ? value : value with { Image = value.Image with { Bytes = [] } };

    private void CheckStrictRefusal(string name, Outcome actual, string message)
    {
        Check(!actual.Ok, name + ": malformed zlib must be refused by the shared strict decoder.");
        Check(actual.ErrorType == nameof(InvalidDataException), name + ": strict refusal changed exception type: " + actual.ErrorType);
        Check(actual.Error == message, $"{name}: strict diagnostic expected='{message}', actual='{actual.Error}'.");
    }

    private (ulong Texture, ulong Image) ProbeFacadeLifetime(Spec spec)
    {
        using Texture2D texture = CuratedAyaTextureLoader.Load(spec.Path, spec.Width, spec.Height,
            (CuratedAyaTextureLoader.Compression)spec.Compression,
            spec.TargetFormat is int format ? (Image.Format)format : null, spec.MipCount);
        using Image image = texture.GetImage();
        Check(!image.IsEmpty() && image.GetWidth() == spec.Width && image.GetHeight() == spec.Height,
            "Facade result survives its loader/result disposal: " + spec.Name);
        return (texture.GetInstanceId(), image.GetInstanceId());
    }

    private IEnumerable<Spec> SyntheticSpecs()
    {
        byte[] rgba = Dds(2, 4, 4, 1), dxt1 = Dds(0, 4, 4, 1), dxt2 = Dds(1, 4, 4, 1);
        byte[] compressed = Compress(rgba), valid = Frame(compressed);
        string[] zlib = ["stream_peer_gzip.cpp"];
        string[] ddsDiagnostic = ["texture_loader_dds.cpp", "image.cpp"];
        string[] formatDiagnostic = ["image.cpp"];
        const string truncated = "Curated texture has a truncated zlib stream.";
        const string trailing = "Curated texture AYA record contains trailing compressed data.";
        const string corruptStream = "Curated texture contains an invalid zlib stream.";
        yield return Fixture("rgba-control", valid, mustSucceed: true);
        yield return Fixture("dxt1-control", Frame(Compress(dxt1)), compression: 0, mustSucceed: true);
        yield return Fixture("dxt2-control", Frame(Compress(dxt2)), compression: 1, mustSucceed: true);
        yield return Fixture("rgba-three-mips", Frame(Compress(Dds(2, 4, 4, 3))), mips: 3, mustSucceed: true);
        yield return Fixture("rgba-header-zero-mips", Frame(Compress(Mutate(rgba, 28, 0))), mips: 0, mustSucceed: true);
        yield return Fixture("aya-two-records", Join(Frame(Compress(rgba[..73])), Frame(Compress(rgba[73..]))), mustSucceed: true);
        // The pinned .NET ZLibStream writes nothing for an empty payload, so
        // spell out a complete empty zlib member (fixed block, Adler-32 of 1).
        yield return Fixture("aya-empty-second-record", Join(valid, Frame([0x78, 0x9c, 0x03, 0x00, 0x00, 0x00, 0x00, 0x01])), mustSucceed: true);
        yield return Fixture("aya-zero-length-second-record", Join(valid, [0, 0, 0, 0]));
        yield return Fixture("empty-source", []);
        yield return Fixture("short-record-header", [1, 2, 3]);
        yield return Fixture("zero-record-length", [0, 0, 0, 0]);
        yield return Fixture("oversized-record-length", [255, 255, 255, 255]);
        yield return Fixture("record-past-input", [8, 0, 0, 0, 1]);
        yield return Fixture("trailing-partial-record", Join(valid, [1]));
        yield return Fixture("empty-dds", Frame(Compress([])));
        yield return Fixture("invalid-zlib", Frame([0xff, 0, 0, 0]), origins: zlib, refusal: corruptStream);
        byte[] corrupt = (byte[])compressed.Clone(); corrupt[^1] ^= 1;
        yield return Fixture("bad-adler32", Frame(corrupt), origins: zlib, refusal: corruptStream);
        for (int missing = 1; missing <= 8; missing++)
            yield return Fixture("zlib-missing-suffix-" + missing, Frame(compressed[..^missing]), origins: [.. zlib, .. ddsDiagnostic], refusal: truncated,
                legacyOrigins: [ShortReadOrigin]);
        yield return Fixture("small-trailing-bytes", Frame(Join(compressed, [7, 8])), origins: zlib, refusal: trailing);
        yield return Fixture("concatenated-members", Frame(Join(compressed, Compress([11, 22, 33]))), origins: zlib, refusal: trailing);
        foreach (int length in new[] { 8191, 8192, 8193 })
            yield return Fixture("short-member-record-" + length, Frame(Pad(compressed, length)), origins: zlib, refusal: trailing);
        byte[] exactBlock = Exact8192ByteMember();
        yield return Fixture("exact8192-member-no-tail", Frame(exactBlock));
        yield return Fixture("exact8192-member-one-tail-byte", Frame(Join(exactBlock, [0])), origins: zlib, refusal: trailing);
        byte[] largeDds = Dds(2, 64, 64, 1), largeCompressed = Compress(largeDds);
        Require(largeCompressed.Length > 8192, "Deterministic noisy DDS must exercise more than one managed input buffer.");
        int boundary = (largeCompressed.Length + 8191) / 8192 * 8192;
        foreach (int length in new[] { boundary - 1, boundary, boundary + 1 })
            yield return Fixture("large-member-record-" + length, Frame(Pad(largeCompressed, length)), width: 64, height: 64, origins: zlib, refusal: trailing);
        yield return Fixture("source-at-limit", Frame(Pad(compressed, SourceLimit - 4)), origins: zlib);
        yield return Fixture("source-over-limit", new byte[SourceLimit + 1]);
        // No allocation exceeds the accepted 8 MiB output limit. The extra
        // byte is streamed into zlib and must be refused before DDS decoding.
        yield return Fixture("decoded-at-limit", Frame(CompressWithPadding(rgba, DecodedLimit)), origins: ddsDiagnostic);
        yield return Fixture("decoded-over-limit", Frame(CompressWithPadding(rgba, DecodedLimit + 1)), origins: zlib);
        byte[] overLimitBadChecksum = CompressWithPadding(rgba, DecodedLimit + 1);
        overLimitBadChecksum[^1] ^= 1;
        yield return Fixture("decoded-over-limit-bad-checksum", Frame(overLimitBadChecksum), origins: zlib, refusal: corruptStream);
        yield return Fixture("second-record-crosses-decoded-limit",
            Join(Frame(CompressWithPadding(rgba, DecodedLimit - 1)), Frame(Compress([0, 0]))), origins: zlib);
        yield return Fixture("dds-short-header", Frame(Compress(rgba[..127])));
        yield return Fixture("dds-header-size", Frame(Compress(Mutate(rgba, 4, 123))), origins: ddsDiagnostic);
        yield return Fixture("dds-pixel-format-size", Frame(Compress(Mutate(rgba, 76, 31))), origins: ddsDiagnostic);
        byte[] badMagic = (byte[])rgba.Clone(); badMagic[0] = 0;
        yield return Fixture("dds-bad-magic", Frame(Compress(badMagic)));
        foreach (int offset in new[] { 80, 84, 88, 92, 96, 100, 104 })
            yield return Fixture("rgba-mask-word-" + offset, Frame(Compress(Mutate(rgba, offset, BinaryPrimitives.ReadUInt32LittleEndian(rgba.AsSpan(offset, 4)) ^ 1))));
        yield return Fixture("wrong-fourcc", Frame(Compress(dxt1)), compression: 1);
        foreach (int compression in new[] { -1, 3, int.MaxValue })
            yield return Fixture("compression-" + compression, valid, compression: compression);
        foreach (int? mip in new int?[] { null, 0, 1, 2, -1, -2, int.MinValue })
            yield return Fixture("mip-option-" + (mip?.ToString() ?? "null"), valid, mips: mip);
        foreach (int? target in new int?[] { null, (int)Image.Format.Rgba8, (int)Image.Format.Rgb8, -1, int.MinValue, int.MaxValue })
            yield return Fixture("target-option-" + (target?.ToString() ?? "null"), valid, target: target, origins: formatDiagnostic);
        yield return Fixture("dxt2-rgba-conversion", Frame(Compress(dxt2)), compression: 1, target: (int)Image.Format.Rgba8, mustSucceed: true);
        yield return Fixture("width-mismatch", valid, width: 5);
        yield return Fixture("width-zero", valid, width: 0);
        yield return Fixture("height-negative", valid, height: -1);
        // The loader reads a short surface from uninitialized memory. The native
        // decoder refuses it before decoding; the oracle must show the short read.
        string[] shortRead = [.. ddsDiagnostic, ShortReadOrigin];
        byte[] shortPixels = Frame(Compress(dxt1[..129]));
        yield return Fixture("short-pixels", shortPixels, compression: 0, refusal: TruncatedPixels, legacyOrigins: shortRead);
        yield return Fixture("short-pixels-before-dimension", shortPixels, compression: 0, width: 5, refusal: TruncatedPixels, legacyOrigins: shortRead);
        yield return Fixture("format-before-short-pixels", shortPixels, compression: 1);
        yield return Fixture("mips-before-short-pixels", shortPixels, compression: 0, mips: 2);
        yield return Fixture("decode-before-dimension", Frame(Compress(Dds(2, 5, 4, 1))), origins: ddsDiagnostic);
        yield return Fixture("decode-truncated-header-width", Frame(Compress(Mutate(rgba, 16, 5))), refusal: TruncatedPixels, legacyOrigins: shortRead);
        byte[] odd = Dds(0, 5, 4, 1), mips = Dds(2, 4, 4, 3);
        yield return Fixture("dxt1-odd-width-complete", Frame(Compress(odd)), width: 5, compression: 0, mustSucceed: true, origins: ddsDiagnostic);
        yield return Fixture("dxt1-odd-width-short", Frame(Compress(odd[..^1])), width: 5, compression: 0, refusal: TruncatedPixels, legacyOrigins: shortRead);
        yield return Fixture("rgba-three-mips-short", Frame(Compress(mips[..^1])), mips: 3, refusal: TruncatedPixels, legacyOrigins: shortRead);
        byte[] cube = Mutate(rgba, 112, 0x200), volume = Mutate(Mutate(rgba, 112, 0x200000), 24, 2);
        yield return Fixture("rgba-cubemap-six-faces", Frame(Compress(Join(cube, Surfaces(rgba, 5)))), mustSucceed: true);
        yield return Fixture("rgba-cubemap-one-face", Frame(Compress(cube)), refusal: TruncatedPixels, legacyOrigins: shortRead);
        yield return Fixture("rgba-volume-two-slices", Frame(Compress(Join(volume, Surfaces(rgba, 1)))), mustSucceed: true);
        yield return Fixture("rgba-volume-one-slice", Frame(Compress(volume)), refusal: TruncatedPixels, legacyOrigins: shortRead);
        yield return Fixture("format-before-mips-and-dimension", Frame(Compress(Mutate(rgba, 92, 0))), width: 0, mips: 2);
        yield return Fixture("mips-before-dimension", valid, width: 0, mips: 2);
        yield return Fixture("dimension-before-negative-format", valid, width: 0, target: -1);
        yield return Fixture("magic-before-negative-options", Frame(Compress(badMagic)), width: 0, target: -1, mips: -1);
        string absent = Path.Combine(_outputDirectory!, "never-created.texture.aya");
        yield return new Spec("synthetic/missing-file", absent, 4, 4, 2, DiagnosticOrigins: ["file_access.cpp"]);
    }

    private Spec Fixture(string name, byte[] bytes, int width = 4, int height = 4, int compression = 2,
        int? target = null, int? mips = null, bool mustSucceed = false, string[]? origins = null, string? refusal = null,
        string[]? legacyOrigins = null)
    {
        string path = Path.Combine(_outputDirectory!, name + ".texture.aya");
        using (var output = new FileStream(path, FileMode.CreateNew, System.IO.FileAccess.Write, FileShare.None)) output.Write(bytes);
        return new Spec("synthetic/" + name, path, width, height, compression, target, mips, mustSucceed, origins, refusal, legacyOrigins);
    }

    private static byte[] Dds(int compression, int width, int height, int mipCount)
    {
        int payload = 0;
        for (int level = 0, w = width, h = height; level < mipCount; level++, w = Math.Max(1, w / 2), h = Math.Max(1, h / 2))
            payload += compression == 2 ? w * h * 4 : Math.Max(1, (w + 3) / 4) * Math.Max(1, (h + 3) / 4) * (compression == 0 ? 8 : 16);
        byte[] bytes = new byte[128 + payload];
        "DDS "u8.CopyTo(bytes);
        void Put(int offset, uint value) => BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(offset, 4), value);
        Put(4, 124); Put(8, (uint)(0x1007 | (compression == 2 ? 8 : 0x80000) | (mipCount > 1 ? 0x20000 : 0)));
        Put(12, (uint)height); Put(16, (uint)width); Put(20, (uint)(compression == 2 ? width * 4 : payload));
        Put(28, (uint)mipCount); Put(76, 32); Put(80, compression == 2 ? 0x41u : 4u);
        Put(108, (uint)(0x1000 | (mipCount > 1 ? 0x400008 : 0)));
        if (compression == 2)
        {
            Put(88, 32); Put(92, 0x00ff0000); Put(96, 0x0000ff00); Put(100, 0x000000ff); Put(104, 0xff000000);
        }
        else (compression == 0 ? "DXT1"u8 : "DXT2"u8).CopyTo(bytes.AsSpan(84));
        uint state = 0x41594131;
        for (int index = 128; index < bytes.Length; index++)
        {
            state ^= state << 13; state ^= state >> 17; state ^= state << 5;
            bytes[index] = (byte)state;
        }
        return bytes;
    }

    private static byte[] Compress(byte[] payload)
    {
        using var output = new MemoryStream();
        using (var zlib = new ZLibStream(output, CompressionLevel.SmallestSize, leaveOpen: true)) zlib.Write(payload);
        return output.ToArray();
    }

    private static byte[] CompressWithPadding(byte[] prefix, int length)
    {
        using var output = new MemoryStream();
        using (var zlib = new ZLibStream(output, CompressionLevel.SmallestSize, leaveOpen: true))
        {
            zlib.Write(prefix);
            byte[] chunk = new byte[16 * 1024];
            for (int remaining = length - prefix.Length; remaining > 0; remaining -= Math.Min(remaining, chunk.Length))
                zlib.Write(chunk, 0, Math.Min(remaining, chunk.Length));
        }
        return output.ToArray();
    }

    private static byte[] Exact8192ByteMember()
    {
        // Bounded generation uses the actual pinned .NET compressor rather
        // than mistaking record padding for the compressed member's length.
        byte[] noise = new byte[8192];
        uint state = 0x41594132;
        for (int index = 0; index < noise.Length; index++)
        {
            state ^= state << 13; state ^= state >> 17; state ^= state << 5;
            noise[index] = (byte)state;
        }
        for (int length = 8160; length <= noise.Length; length++)
        {
            byte[] member = Compress(noise[..length]);
            if (member.Length == 8192) return member;
        }
        throw new InvalidOperationException("Bounded compressor search could not produce an exact 8192-byte member.");
    }

    private static byte[] Frame(byte[] compressed)
    {
        byte[] result = new byte[compressed.Length + 4];
        BinaryPrimitives.WriteUInt32LittleEndian(result, (uint)compressed.Length);
        compressed.CopyTo(result, 4); return result;
    }
    private static byte[] Surfaces(byte[] dds, int count) { byte[] surface = dds[128..], value = new byte[surface.Length * count]; for (int index = 0; index < count; index++) surface.CopyTo(value, index * surface.Length); return value; }
    private static byte[] Join(byte[] first, byte[] second) { byte[] value = new byte[first.Length + second.Length]; first.CopyTo(value, 0); second.CopyTo(value, first.Length); return value; }
    private static byte[] Pad(byte[] source, int length) { if (length < source.Length) throw new ArgumentOutOfRangeException(nameof(length)); byte[] result = new byte[length]; source.CopyTo(result, 0); return result; }
    private static byte[] Mutate(byte[] source, int offset, uint value) { byte[] result = (byte[])source.Clone(); BinaryPrimitives.WriteUInt32LittleEndian(result.AsSpan(offset, 4), value); return result; }
    private static JsonElement Property(JsonElement value, string name) => value.EnumerateObject().Single(item => string.Equals(item.Name, name, StringComparison.OrdinalIgnoreCase)).Value;
    private static string Hex(byte[] source) => Convert.ToHexString(SHA256.HashData(source)).ToLowerInvariant();
    private static string HashInput(string path) => Hex(File.ReadAllBytes(ProjectSettings.GlobalizePath(path)));

    private string CreateOwnedDirectory()
    {
        string root = Path.GetFullPath(ProjectSettings.GlobalizePath("user://"));
        string[] choices = OS.GetCmdlineUserArgs().Where(argument => argument.StartsWith("--aya-check-dir=", StringComparison.Ordinal)).ToArray();
        Require(choices.Length <= 1, "Supply at most one --aya-check-dir.");
        string path = choices.Length == 0 ? Path.Combine(root, "aya-texture-checks-" + Guid.NewGuid().ToString("N")) : choices[0]["--aya-check-dir=".Length..];
        Require(Path.IsPathFullyQualified(path), "Explicit AYA output directory must be absolute.");
        path = Path.GetFullPath(path);
        Require(path.StartsWith(root.TrimEnd(Path.DirectorySeparatorChar) + Path.DirectorySeparatorChar, StringComparison.Ordinal)
            && !Directory.Exists(path) && !File.Exists(path), "AYA output must be a fresh descendant of this invocation's user:// directory.");
        for (DirectoryInfo? parent = new DirectoryInfo(path).Parent; parent is not null && parent.FullName.StartsWith(root, StringComparison.Ordinal); parent = parent.Parent)
            Require(!parent.Exists || parent.LinkTarget is null, "AYA output may not traverse an existing symbolic link.");
        Directory.CreateDirectory(path);
        return path;
    }

    private void Check(bool condition, string message) { _checks++; if (!condition) _failures.Add(message); }
    private static void Require(bool condition, string message) { if (!condition) throw new InvalidOperationException(message); }

    private sealed partial class DiagnosticLogger : Logger
    {
        private readonly object _gate = new();
        private readonly List<Diagnostic> _entries = [];
        private string _case = "outside-case";
        private string _phase = "outside-phase";
        private string[] _origins = [];
        internal void Begin(string name, string phase, string[] origins) { lock (_gate) { _case = name; _phase = phase; _origins = origins; } }
        internal void End() { lock (_gate) { _case = "outside-case"; _phase = "outside-phase"; _origins = []; } }
        internal Diagnostic[] Snapshot() { lock (_gate) return [.. _entries]; }
        internal bool Logged(string name, string phase, string file)
        {
            lock (_gate) return _entries.Any(item => item.Case == name && item.Phase == phase && item.File.Replace('\\', '/').EndsWith('/' + file, StringComparison.Ordinal));
        }
        public override void _LogError(string function, string file, int line, string code, string rationale,
            bool editorNotify, int errorType, Godot.Collections.Array<ScriptBacktrace> scriptBacktraces)
        {
            lock (_gate)
            {
                string origin = file.Replace('\\', '/');
                bool expected = (errorType == (int)ErrorType.Error || errorType == (int)ErrorType.Warning) &&
                    _origins.Any(allowed => origin.EndsWith('/' + allowed, StringComparison.Ordinal) || origin == allowed);
                _entries.Add(new Diagnostic(_case, _phase, function, file, line, code, rationale, errorType, expected));
            }
        }
    }
}
