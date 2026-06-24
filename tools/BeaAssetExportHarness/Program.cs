using System.Buffers.Binary;
using System.Drawing;
using System.IO.Compression;
using System.Numerics;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Runtime.Loader;
using System.Text.Json;

namespace BeaAssetExportHarness;

internal static class Program
{
    private const uint DdpfFourCc = 0x00000004;
    private const uint DdpfRgb = 0x00000040;

    private sealed record ExportOptions(
        string Command,
        string RepoRoot,
        string ResourcesRoot,
        string ExtractorRuntimeDir,
        string ExtractorRoot,
        string EmbeddedRoot,
        string OutDir,
        int? LimitLooseTextures,
        int? LimitLooseMeshes,
        int? LimitEmbeddedBodies,
        int StartLooseTextures,
        int StartLooseMeshes,
        int StartEmbeddedBodies,
        bool SkipExisting,
        int ProgressEvery
    );

    private sealed record DdsHeaderInfo(
        int Width,
        int Height,
        int PitchOrLinearSize,
        uint PixelFlags,
        uint FourCc,
        int RgbBitCount,
        uint RMask,
        uint GMask,
        uint BMask,
        uint AMask
    );

    private sealed class ExtractorRuntime
    {
        private readonly string _runtimeDir;
        private readonly string _extractorRoot;
        private readonly Assembly _ayaAssembly;
        private readonly Assembly _ddsAssembly;
        private readonly MethodInfo _looseMeshExportMethod;
        private readonly Type _looseMeshExtractorType;
        private readonly Type _importerType;
        private readonly Type _exporterType;
        private readonly Type _ddsType;

        public ExtractorRuntime(string extractorRuntimeDir, string extractorRoot)
        {
            _runtimeDir = extractorRuntimeDir;
            _extractorRoot = extractorRoot;
            Directory.SetCurrentDirectory(_extractorRoot);

            AssemblyLoadContext.Default.Resolving += ResolveFromRuntimeDir;

            _ayaAssembly = AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.Combine(_runtimeDir, "AYAResourceExtractor.dll"));
            _ddsAssembly = AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.Combine(_runtimeDir, "DDSTextureUncompress.dll"));

            _looseMeshExtractorType = _ayaAssembly.GetType("AYAResourceExtractor.AyaModelExtractor", throwOnError: true)!;
            _looseMeshExportMethod = _looseMeshExtractorType.GetMethod("ExtractModel", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMethodException("AyaModelExtractor.ExtractModel");
            _importerType = _ayaAssembly.GetType("AYAResourceExtractor.AyaModelImporter", throwOnError: true)!;
            _exporterType = _ayaAssembly.GetType("AYAResourceExtractor.FbxModelExporter", throwOnError: true)!;
            _ddsType = _ddsAssembly.GetType("DDSTextureUncompress", throwOnError: true)!
                ?? throw new TypeLoadException("DDSTextureUncompress");
        }

        private Assembly? ResolveFromRuntimeDir(AssemblyLoadContext context, AssemblyName name)
        {
            var candidate = Path.Combine(_runtimeDir, $"{name.Name}.dll");
            return File.Exists(candidate) ? context.LoadFromAssemblyPath(candidate) : null;
        }

        public void ExportLooseMesh(string resourcesRoot, string inputAyaPath, string outputDir, bool binaryFbx, bool asciiFbx)
        {
            Directory.CreateDirectory(outputDir);
            var instance = Activator.CreateInstance(_looseMeshExtractorType, nonPublic: true)
                ?? throw new InvalidOperationException("Failed to create AyaModelExtractor");
            _looseMeshExportMethod.Invoke(instance, new object[] { resourcesRoot, inputAyaPath, outputDir, binaryFbx, asciiFbx });
        }

        public void ExportEmbeddedBody(string resourcesRoot, string inputBodyPath, string outputDir, bool binaryFbx, bool asciiFbx)
        {
            Directory.CreateDirectory(outputDir);
            var importer = Activator.CreateInstance(_importerType, nonPublic: true)
                ?? throw new InvalidOperationException("Failed to create AyaModelImporter");
            var exporter = Activator.CreateInstance(_exporterType, nonPublic: true)
                ?? throw new InvalidOperationException("Failed to create FbxModelExporter");

            var importMethod = _importerType.GetMethod("Import", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMethodException("AyaModelImporter.Import");
            var modelProperty = _importerType.GetProperty("Model", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMemberException("AyaModelImporter.Model");
            var exportMethod = _exporterType.GetMethod("Export", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMethodException("FbxModelExporter.Export");

            var bodyBytes = File.ReadAllBytes(inputBodyPath);
            importMethod.Invoke(importer, new object[] { bodyBytes });
            var model = modelProperty.GetValue(importer) ?? throw new InvalidOperationException("Importer produced null model");
            var modelName = Path.GetFileNameWithoutExtension(inputBodyPath);
            exportMethod.Invoke(exporter, new object[] { model, outputDir, modelName, resourcesRoot, binaryFbx, asciiFbx });
        }

        public void ExportTextureFile(string inputAyaPath, string outputPngPath)
        {
            Directory.CreateDirectory(Path.GetDirectoryName(outputPngPath)!);
            var ddsBytes = InflateAya(File.ReadAllBytes(inputAyaPath));
            var header = ReadDdsHeader(ddsBytes);
            if (header is null)
            {
                throw new InvalidDataException($"Could not read DDS dimensions from {inputAyaPath}");
            }

            byte[] rgba;
            int width;
            int height;

            if (TryDecodeUncompressedDds(ddsBytes, header, out var decoded))
            {
                rgba = decoded;
                width = header.Width;
                height = header.Height;
            }
            else
            {
                rgba = new byte[checked(header.Width * header.Height * 4)];

                var instance = Activator.CreateInstance(_ddsType, nonPublic: true)
                    ?? throw new InvalidOperationException("Failed to create DDSTextureUncompress");
                var method = _ddsType.GetMethod("Uncompress", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                    ?? throw new MissingMethodException("DDSTextureUncompress.Uncompress");

                object[] args = { ddsBytes, ddsBytes.Length, rgba, 0, 0 };
                var result = method.Invoke(instance, args);
                width = (int)args[3];
                height = (int)args[4];
                if ((result is int code && code != 1) || width <= 0 || height <= 0)
                {
                    throw new InvalidDataException($"DDS decode failed for {inputAyaPath}");
                }
            }

            using var bitmap = new Bitmap(width, height, System.Drawing.Imaging.PixelFormat.Format32bppArgb);
            var rect = new Rectangle(0, 0, width, height);
            var bitmapData = bitmap.LockBits(rect, System.Drawing.Imaging.ImageLockMode.WriteOnly, System.Drawing.Imaging.PixelFormat.Format32bppArgb);
            try
            {
                var rowBytes = checked(width * 4);
                for (var y = 0; y < height; y++)
                {
                    var sourceOffset = y * rowBytes;
                    var dest = IntPtr.Add(bitmapData.Scan0, y * bitmapData.Stride);
                    Marshal.Copy(rgba, sourceOffset, dest, rowBytes);
                }
            }
            finally
            {
                bitmap.UnlockBits(bitmapData);
            }

            bitmap.Save(outputPngPath, System.Drawing.Imaging.ImageFormat.Png);
        }
    }

    private sealed record LaneResult(string Lane, int Attempted, int Succeeded, int Failed, string ManifestPath);

    private sealed record ExportError(
        string Message,
        string Type,
        string? WrapperMessage,
        string? WrapperType
    );

    private static int Main(string[] args)
    {
        try
        {
            var options = ParseArgs(args);
            var runtime = new ExtractorRuntime(options.ExtractorRuntimeDir, options.ExtractorRoot);

            var results = new List<LaneResult>();

            if (options.Command is "export-all" or "export-textures")
            {
                results.Add(ExportLooseTextures(runtime, options));
            }

            if (options.Command is "export-all" or "export-loose-meshes")
            {
                results.Add(ExportLooseMeshes(runtime, options));
            }

            if (options.Command is "export-all" or "export-embedded-meshes")
            {
                results.Add(ExportEmbeddedMeshes(runtime, options));
            }

            var summary = new
            {
                command = options.Command,
                out_dir = options.OutDir,
                results
            };
            var summaryPath = Path.Combine(options.OutDir, "summary.json");
            File.WriteAllText(summaryPath, JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }));
            Console.WriteLine(JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }));
            return 0;
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine(ex);
            return 1;
        }
    }

    private static ExportOptions ParseArgs(string[] args)
    {
        string command = "export-all";
        string repoRoot = Directory.GetCurrentDirectory();
        string resourcesRoot = Path.Combine(repoRoot, "game", "data", "resources");
        string extractorRuntimeDir = Path.Combine(repoRoot, "references", "AYAResourceExtractor", "Code", "AyaResourceExtractor", "bin", "Debug", "net6.0-windows");
        string extractorRoot = Path.Combine(repoRoot, "references", "AYAResourceExtractor");
        string embeddedRoot = Path.Combine(repoRoot, "subagents", "aya_embedded_mesh_wave1_2026-03-13");
        string outDir = Path.Combine(repoRoot, "subagents", $"asset_export_wave1_{DateTime.Today:yyyy-MM-dd}");
        int? limitLooseTextures = null;
        int? limitLooseMeshes = null;
        int? limitEmbeddedBodies = null;
        var startLooseTextures = 1;
        var startLooseMeshes = 1;
        var startEmbeddedBodies = 1;
        var skipExisting = false;
        var progressEvery = 25;

        for (var i = 0; i < args.Length; i++)
        {
            switch (args[i])
            {
                case "export-all":
                case "export-textures":
                case "export-loose-meshes":
                case "export-embedded-meshes":
                    command = args[i];
                    break;
                case "--repo-root":
                    repoRoot = Path.GetFullPath(args[++i]);
                    break;
                case "--resources-root":
                    resourcesRoot = Path.GetFullPath(args[++i]);
                    break;
                case "--extractor-runtime-dir":
                    extractorRuntimeDir = Path.GetFullPath(args[++i]);
                    break;
                case "--extractor-root":
                    extractorRoot = Path.GetFullPath(args[++i]);
                    break;
                case "--embedded-root":
                    embeddedRoot = Path.GetFullPath(args[++i]);
                    break;
                case "--out-dir":
                    outDir = Path.GetFullPath(args[++i]);
                    break;
                case "--limit-loose-textures":
                    limitLooseTextures = int.Parse(args[++i]);
                    break;
                case "--limit-loose-meshes":
                    limitLooseMeshes = int.Parse(args[++i]);
                    break;
                case "--limit-embedded-bodies":
                    limitEmbeddedBodies = int.Parse(args[++i]);
                    break;
                case "--start-loose-textures":
                    startLooseTextures = int.Parse(args[++i]);
                    break;
                case "--start-loose-meshes":
                    startLooseMeshes = int.Parse(args[++i]);
                    break;
                case "--start-embedded-bodies":
                    startEmbeddedBodies = int.Parse(args[++i]);
                    break;
                case "--skip-existing":
                    skipExisting = true;
                    break;
                case "--progress-every":
                    progressEvery = int.Parse(args[++i]);
                    break;
                default:
                    throw new ArgumentException($"Unknown argument: {args[i]}");
            }
        }

        return new ExportOptions(
            command,
            repoRoot,
            resourcesRoot,
            extractorRuntimeDir,
            extractorRoot,
            embeddedRoot,
            outDir,
            limitLooseTextures,
            limitLooseMeshes,
            limitEmbeddedBodies,
            startLooseTextures,
            startLooseMeshes,
            startEmbeddedBodies,
            skipExisting,
            progressEvery);
    }

    private static LaneResult ExportLooseTextures(ExtractorRuntime runtime, ExportOptions options)
    {
        var textureRoots = new[]
        {
            Path.Combine(options.ResourcesRoot, "dxtntextures"),
            Path.Combine(options.ResourcesRoot, "textures")
        };
        var files = textureRoots
            .Where(Directory.Exists)
            .SelectMany(root => Directory.EnumerateFiles(root, "*.aya", SearchOption.TopDirectoryOnly))
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToList();

        if (options.StartLooseTextures > 1)
        {
            files = files.Skip(options.StartLooseTextures - 1).ToList();
        }

        if (options.LimitLooseTextures is int limit)
        {
            files = files.Take(limit).ToList();
        }

        var rows = new List<object>();
        var succeeded = 0;
        var failed = 0;
        var laneRoot = Path.Combine(options.OutDir, "loose_textures");
        Directory.CreateDirectory(laneRoot);
        var progressPath = Path.Combine(laneRoot, "progress.jsonl");

        for (var index = 0; index < files.Count; index++)
        {
            var input = files[index];
            var relativeParent = Path.GetFileName(Path.GetDirectoryName(input)) ?? "textures";
            var outputDir = Path.Combine(laneRoot, relativeParent);
            var outputName = $"{Path.GetFileNameWithoutExtension(input)}.png";
            var outputPath = Path.Combine(outputDir, outputName);

            if (options.SkipExisting && File.Exists(outputPath))
            {
                succeeded++;
                var skippedRow = new { input, output = outputPath, status = "skipped_existing" };
                rows.Add(skippedRow);
                WriteProgress(progressPath, skippedRow);
                MaybePrintProgress("loose_textures", index + 1, files.Count, input, "skipped_existing", options.ProgressEvery);
                continue;
            }

            try
            {
                runtime.ExportTextureFile(input, outputPath);
                succeeded++;
                var okRow = new { input, output = outputPath, status = "ok" };
                rows.Add(okRow);
                WriteProgress(progressPath, okRow);
                MaybePrintProgress("loose_textures", index + 1, files.Count, input, "ok", options.ProgressEvery);
            }
            catch (Exception ex)
            {
                failed++;
                var error = DescribeExportError(ex);
                var errorRow = new { input, output = outputPath, status = "error", error = error.Message, errorType = error.Type, wrappedError = error.WrapperMessage, wrappedErrorType = error.WrapperType };
                rows.Add(errorRow);
                WriteProgress(progressPath, errorRow);
                Console.Error.WriteLine($"[loose_textures] {index + 1}/{files.Count} error {input}: {FormatErrorForConsole(error)}");
            }
        }

        var manifestPath = Path.Combine(laneRoot, "manifest.json");
        File.WriteAllText(manifestPath, JsonSerializer.Serialize(rows, new JsonSerializerOptions { WriteIndented = true }));
        return new LaneResult("loose_textures", files.Count, succeeded, failed, manifestPath);
    }

    private static LaneResult ExportLooseMeshes(ExtractorRuntime runtime, ExportOptions options)
    {
        var meshRoot = Path.Combine(options.ResourcesRoot, "meshes");
        var files = Directory.EnumerateFiles(meshRoot, "*.aya", SearchOption.TopDirectoryOnly)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToList();

        if (options.StartLooseMeshes > 1)
        {
            files = files.Skip(options.StartLooseMeshes - 1).ToList();
        }

        if (options.LimitLooseMeshes is int limit)
        {
            files = files.Take(limit).ToList();
        }

        var rows = new List<object>();
        var succeeded = 0;
        var failed = 0;
        var laneRoot = Path.Combine(options.OutDir, "loose_meshes");
        Directory.CreateDirectory(laneRoot);
        var progressPath = Path.Combine(laneRoot, "progress.jsonl");

        for (var index = 0; index < files.Count; index++)
        {
            var input = files[index];
            var outputPath = Path.Combine(laneRoot, $"{Path.GetFileNameWithoutExtension(input)}_binary.fbx");

            if (options.SkipExisting && File.Exists(outputPath))
            {
                succeeded++;
                var skippedRow = new { input, output = outputPath, status = "skipped_existing" };
                rows.Add(skippedRow);
                WriteProgress(progressPath, skippedRow);
                MaybePrintProgress("loose_meshes", index + 1, files.Count, input, "skipped_existing", options.ProgressEvery);
                continue;
            }

            try
            {
                runtime.ExportLooseMesh(options.ResourcesRoot, input, laneRoot, binaryFbx: true, asciiFbx: false);
                succeeded++;
                var okRow = new { input, output = outputPath, status = "ok" };
                rows.Add(okRow);
                WriteProgress(progressPath, okRow);
                MaybePrintProgress("loose_meshes", index + 1, files.Count, input, "ok", options.ProgressEvery);
            }
            catch (Exception ex)
            {
                failed++;
                var error = DescribeExportError(ex);
                var errorRow = new { input, output = outputPath, status = "error", error = error.Message, errorType = error.Type, wrappedError = error.WrapperMessage, wrappedErrorType = error.WrapperType };
                rows.Add(errorRow);
                WriteProgress(progressPath, errorRow);
                Console.Error.WriteLine($"[loose_meshes] {index + 1}/{files.Count} error {input}: {FormatErrorForConsole(error)}");
            }
        }

        var manifestPath = Path.Combine(laneRoot, "manifest.json");
        File.WriteAllText(manifestPath, JsonSerializer.Serialize(rows, new JsonSerializerOptions { WriteIndented = true }));
        return new LaneResult("loose_meshes", files.Count, succeeded, failed, manifestPath);
    }

    private static LaneResult ExportEmbeddedMeshes(ExtractorRuntime runtime, ExportOptions options)
    {
        var files = Directory.EnumerateFiles(options.EmbeddedRoot, "*_embedded_body*_CMSH.bin", SearchOption.AllDirectories)
            .OrderBy(path => path, StringComparer.OrdinalIgnoreCase)
            .ToList();

        if (options.StartEmbeddedBodies > 1)
        {
            files = files.Skip(options.StartEmbeddedBodies - 1).ToList();
        }

        if (options.LimitEmbeddedBodies is int limit)
        {
            files = files.Take(limit).ToList();
        }

        var rows = new List<object>();
        var succeeded = 0;
        var failed = 0;
        var laneRoot = Path.Combine(options.OutDir, "embedded_meshes");
        Directory.CreateDirectory(laneRoot);
        var progressPath = Path.Combine(laneRoot, "progress.jsonl");

        for (var index = 0; index < files.Count; index++)
        {
            var input = files[index];
            var outputPath = Path.Combine(laneRoot, $"{Path.GetFileNameWithoutExtension(input)}_binary.fbx");

            if (options.SkipExisting && File.Exists(outputPath))
            {
                succeeded++;
                var skippedRow = new { input, output = outputPath, status = "skipped_existing" };
                rows.Add(skippedRow);
                WriteProgress(progressPath, skippedRow);
                MaybePrintProgress("embedded_meshes", index + 1, files.Count, input, "skipped_existing", options.ProgressEvery);
                continue;
            }

            try
            {
                runtime.ExportEmbeddedBody(options.ResourcesRoot, input, laneRoot, binaryFbx: true, asciiFbx: false);
                succeeded++;
                var okRow = new { input, output = outputPath, status = "ok" };
                rows.Add(okRow);
                WriteProgress(progressPath, okRow);
                MaybePrintProgress("embedded_meshes", index + 1, files.Count, input, "ok", options.ProgressEvery);
            }
            catch (Exception ex)
            {
                failed++;
                var error = DescribeExportError(ex);
                var errorRow = new { input, output = outputPath, status = "error", error = error.Message, errorType = error.Type, wrappedError = error.WrapperMessage, wrappedErrorType = error.WrapperType };
                rows.Add(errorRow);
                WriteProgress(progressPath, errorRow);
                Console.Error.WriteLine($"[embedded_meshes] {index + 1}/{files.Count} error {input}: {FormatErrorForConsole(error)}");
            }
        }

        var manifestPath = Path.Combine(laneRoot, "manifest.json");
        File.WriteAllText(manifestPath, JsonSerializer.Serialize(rows, new JsonSerializerOptions { WriteIndented = true }));
        return new LaneResult("embedded_meshes", files.Count, succeeded, failed, manifestPath);
    }

    private static byte[] InflateAya(byte[] compressedAya)
    {
        using var output = new MemoryStream();
        var index = 0;

        while (index < compressedAya.Length)
        {
            if (index + 4 > compressedAya.Length)
            {
                throw new InvalidDataException($"truncated part header at 0x{index:X}");
            }

            var size = BinaryPrimitives.ReadUInt32LittleEndian(compressedAya.AsSpan(index, 4));
            index += 4;
            if (index + size > compressedAya.Length)
            {
                throw new InvalidDataException($"part overruns file at 0x{index:X} size=0x{size:X}");
            }

            using var partStream = new MemoryStream(compressedAya, index, checked((int)size), writable: false);
            using var z = new ZLibStream(partStream, CompressionMode.Decompress);
            z.CopyTo(output);
            index += checked((int)size);
        }

        return output.ToArray();
    }

    private static DdsHeaderInfo? ReadDdsHeader(byte[] ddsBytes)
    {
        if (ddsBytes.Length < 20 || ddsBytes[0] != (byte)'D' || ddsBytes[1] != (byte)'D' || ddsBytes[2] != (byte)'S' || ddsBytes[3] != (byte)' ')
        {
            return null;
        }

        var rawHeight = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(12, 4));
        var rawWidth = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(16, 4));
        var rawPitchOrLinearSize = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(20, 4));
        var pixelFlags = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(80, 4));
        var fourCc = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(84, 4));
        var rgbBitCount = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(88, 4));
        var rMask = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(92, 4));
        var gMask = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(96, 4));
        var bMask = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(100, 4));
        var aMask = BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(104, 4));
        var width = checked((int)(rawWidth & ~3u));
        var height = checked((int)(rawHeight & ~3u));
        return new DdsHeaderInfo(
            width,
            height,
            checked((int)rawPitchOrLinearSize),
            pixelFlags,
            fourCc,
            checked((int)rgbBitCount),
            rMask,
            gMask,
            bMask,
            aMask);
    }

    private static bool TryDecodeUncompressedDds(byte[] ddsBytes, DdsHeaderInfo header, out byte[] rgba)
    {
        rgba = Array.Empty<byte>();
        if ((header.PixelFlags & DdpfRgb) == 0 || (header.PixelFlags & DdpfFourCc) != 0)
        {
            return false;
        }

        var bytesPerPixel = header.RgbBitCount / 8;
        if (bytesPerPixel is not (2 or 4))
        {
            return false;
        }

        var rowBytes = checked(header.Width * bytesPerPixel);
        var filePitch = header.PitchOrLinearSize > 0 ? header.PitchOrLinearSize : rowBytes;
        var dataOffset = 128;
        var requiredBytes = checked(dataOffset + header.Height * filePitch);
        if (ddsBytes.Length < requiredBytes)
        {
            return false;
        }

        rgba = new byte[checked(header.Width * header.Height * 4)];
        for (var y = 0; y < header.Height; y++)
        {
            var rowStart = dataOffset + (y * filePitch);
            for (var x = 0; x < header.Width; x++)
            {
                uint pixelValue = bytesPerPixel switch
                {
                    2 => BinaryPrimitives.ReadUInt16LittleEndian(ddsBytes.AsSpan(rowStart + (x * 2), 2)),
                    4 => BinaryPrimitives.ReadUInt32LittleEndian(ddsBytes.AsSpan(rowStart + (x * 4), 4)),
                    _ => 0
                };

                var outIndex = (y * header.Width + x) * 4;
                rgba[outIndex] = ExpandMaskedComponent(pixelValue, header.BMask);
                rgba[outIndex + 1] = ExpandMaskedComponent(pixelValue, header.GMask);
                rgba[outIndex + 2] = ExpandMaskedComponent(pixelValue, header.RMask);
                rgba[outIndex + 3] = header.AMask == 0 ? (byte)255 : ExpandMaskedComponent(pixelValue, header.AMask);
            }
        }

        return true;
    }

    private static byte ExpandMaskedComponent(uint value, uint mask)
    {
        if (mask == 0)
        {
            return 0;
        }

        var shift = BitOperations.TrailingZeroCount(mask);
        var max = mask >> shift;
        var component = (value & mask) >> shift;
        return (byte)((component * 255u + (max / 2u)) / max);
    }

    private static void WriteProgress(string progressPath, object row)
    {
        File.AppendAllText(progressPath, JsonSerializer.Serialize(row) + Environment.NewLine);
    }

    private static ExportError DescribeExportError(Exception exception)
    {
        if (exception is TargetInvocationException { InnerException: { } inner })
        {
            return new ExportError(
                inner.Message,
                inner.GetType().FullName ?? inner.GetType().Name,
                exception.Message,
                exception.GetType().FullName ?? exception.GetType().Name);
        }

        return new ExportError(
            exception.Message,
            exception.GetType().FullName ?? exception.GetType().Name,
            null,
            null);
    }

    private static string FormatErrorForConsole(ExportError error)
    {
        return error.WrapperType is null
            ? $"{error.Type}: {error.Message}"
            : $"{error.Type}: {error.Message} (wrapped by {error.WrapperType}: {error.WrapperMessage})";
    }

    private static void MaybePrintProgress(string lane, int current, int total, string input, string status, int progressEvery)
    {
        if (current == 1 || current == total || current % Math.Max(progressEvery, 1) == 0)
        {
            Console.WriteLine($"[{lane}] {current}/{total} {status} {Path.GetFileName(input)}");
        }
    }
}
