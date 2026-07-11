using System.Buffers.Binary;
using System.Drawing;
using System.IO.Compression;
using System.Numerics;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Runtime.Loader;
using System.Text;
using System.Text.Json;
using Microsoft.Win32.SafeHandles;

namespace BeaAssetExportHarness;

internal static class Program
{
    private const uint DdpfFourCc = 0x00000004;
    private const uint DdpfRgb = 0x00000040;
    private const uint GenericRead = 0x80000000;
    private const uint GenericWrite = 0x40000000;
    private const uint DeleteAccess = 0x00010000;
    private const uint FileReadAttributes = 0x00000080;
    private const uint FileFlagOpenReparsePoint = 0x00200000;
    private const uint FileFlagDeleteOnClose = 0x04000000;
    private const uint FileAttributeTemporary = 0x00000100;
    private const int FileDispositionInfoEx = 21;
    private const int FileRenameInfoEx = 22;
    private const uint FileDispositionFlagDelete = 0x00000001;
    private const uint FileDispositionFlagPosixSemantics = 0x00000002;
    private const uint FileRenameFlagReplaceIfExists = 0x00000001;
    private const uint FileRenameFlagPosixSemantics = 0x00000002;
    private static readonly HashSet<string> ReservedDosNames = new(
        [
            "CON", "PRN", "AUX", "NUL",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"
        ],
        StringComparer.OrdinalIgnoreCase);

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

    private sealed record AyaIndexValue(int Index, int Texture);

    private sealed class ExtractorRuntime
    {
        private readonly string _runtimeDir;
        private readonly string _extractorRoot;
        private readonly Assembly _ayaAssembly;
        private readonly Assembly _ddsAssembly;
        private readonly Assembly _fbxAssembly;
        private readonly Type _importerType;
        private readonly Type _ddsType;

        public ExtractorRuntime(string extractorRuntimeDir, string extractorRoot)
        {
            _runtimeDir = extractorRuntimeDir;
            _extractorRoot = extractorRoot;
            Directory.SetCurrentDirectory(_extractorRoot);

            AssemblyLoadContext.Default.Resolving += ResolveFromRuntimeDir;

            _ayaAssembly = AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.Combine(_runtimeDir, "AYAResourceExtractor.dll"));
            _ddsAssembly = AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.Combine(_runtimeDir, "DDSTextureUncompress.dll"));
            _fbxAssembly = AssemblyLoadContext.Default.LoadFromAssemblyPath(Path.Combine(_runtimeDir, "Fbx.dll"));

            _importerType = _ayaAssembly.GetType("AYAResourceExtractor.AyaModelImporter", throwOnError: true)!;
            _ddsType = _ddsAssembly.GetType("DDSTextureUncompress", throwOnError: true)!
                ?? throw new TypeLoadException("DDSTextureUncompress");
        }

        private Assembly? ResolveFromRuntimeDir(AssemblyLoadContext context, AssemblyName name)
        {
            var candidate = Path.Combine(_runtimeDir, $"{name.Name}.dll");
            return File.Exists(candidate) ? context.LoadFromAssemblyPath(candidate) : null;
        }

        public GeneratedOutputSeal ExportLooseMesh(
            string outputRoot,
            string resourcesRoot,
            string inputAyaPath,
            string stagingDir,
            string publishedOutputDir,
            bool binaryFbx,
            bool asciiFbx)
        {
            byte[] bodyBytes = InflateAya(ReadLockedFileBytes(inputAyaPath, "loose model source"));
            object model = ImportModel(bodyBytes);
            return ExportModel(
                outputRoot,
                resourcesRoot,
                model,
                Path.GetFileNameWithoutExtension(inputAyaPath),
                stagingDir,
                publishedOutputDir,
                binaryFbx,
                asciiFbx);
        }

        public GeneratedOutputSeal ExportEmbeddedBody(
            string outputRoot,
            string resourcesRoot,
            string inputBodyPath,
            string stagingDir,
            string publishedOutputDir,
            bool binaryFbx,
            bool asciiFbx)
        {
            object model = ImportModel(ReadLockedFileBytes(inputBodyPath, "embedded model source"));
            return ExportModel(
                outputRoot,
                resourcesRoot,
                model,
                Path.GetFileNameWithoutExtension(inputBodyPath),
                stagingDir,
                publishedOutputDir,
                binaryFbx,
                asciiFbx);
        }

        private object ImportModel(byte[] bodyBytes)
        {
            var importer = Activator.CreateInstance(_importerType, nonPublic: true)
                ?? throw new InvalidOperationException("Failed to create AyaModelImporter");
            var importMethod = _importerType.GetMethod("Import", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMethodException("AyaModelImporter.Import");
            var modelProperty = _importerType.GetProperty("Model", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMemberException("AyaModelImporter.Model");
            importMethod.Invoke(importer, new object[] { bodyBytes });
            return modelProperty.GetValue(importer)
                ?? throw new InvalidOperationException("Importer produced null model");
        }

        private object BuildFbxDocument(object model, string publishedOutputDir)
        {
            byte[] templateBytes = ReadLockedFileBytes(
                ResolveFbxTemplatePath(),
                "FBX template");
            object document = ReadFbxDocument(templateBytes);
            object objectsNode = GetFbxNode(document, "Objects");
            object geometryNode = GetFbxNode(objectsNode, "Geometry");

            var vertices = ((System.Collections.IEnumerable)GetRequiredMemberValue(model, "AyaVertices"))
                .Cast<object>()
                .ToArray();
            var outputVertices = new double[checked(vertices.Length * 3)];
            int vertexOffset = 0;
            foreach (object vertex in vertices)
            {
                object position = GetRequiredMemberValue(vertex, "position");
                outputVertices[vertexOffset++] = ReadDoubleMember(position, "x");
                outputVertices[vertexOffset++] = ReadDoubleMember(position, "y");
                outputVertices[vertexOffset++] = -ReadDoubleMember(position, "z");
            }
            SetFbxNodeValue(GetFbxNode(geometryNode, "Vertices"), outputVertices);

            IReadOnlyList<AyaIndexValue> triangleIndices = GenerateTriListIndices(model);
            SetFbxNodeValue(
                GetFbxNode(geometryNode, "PolygonVertexIndex"),
                triangleIndices.Select(static value => value.Index).ToArray());

            var uv = new List<float>(checked(triangleIndices.Count * 2));
            var uvIndices = new List<int>(triangleIndices.Count);
            var normals = new List<double>(checked(triangleIndices.Count * 3));
            var materials = new List<int>();
            foreach (AyaIndexValue encodedIndex in triangleIndices)
            {
                AyaIndexValue index = encodedIndex;
                if (index.Index < 0)
                {
                    index = index with { Index = -(index.Index + 1) };
                    materials.Add(index.Texture);
                }
                if ((uint)index.Index >= (uint)vertices.Length)
                    throw new InvalidDataException("AYA triangle index falls outside the vertex table.");

                object vertex = vertices[index.Index];
                uv.Add((float)ReadDoubleMember(vertex, "U"));
                uv.Add((float)-ReadDoubleMember(vertex, "V"));
                uvIndices.Add(uvIndices.Count);
                object normal = GetRequiredMemberValue(vertex, "normal");
                normals.Add(ReadDoubleMember(normal, "x"));
                normals.Add(ReadDoubleMember(normal, "y"));
                normals.Add(-ReadDoubleMember(normal, "z"));
            }

            SetFbxNodeValue(GetFbxNode(GetFbxNode(geometryNode, "LayerElementNormal"), "Normals"), normals.ToArray());
            object layerUv = GetFbxNode(geometryNode, "LayerElementUV");
            SetFbxNodeValue(GetFbxNode(layerUv, "UV"), uv.ToArray());
            SetFbxNodeValue(GetFbxNode(layerUv, "UVIndex"), uvIndices.ToArray());
            SetFbxNodeValue(
                GetFbxNode(GetFbxNode(geometryNode, "LayerElementMaterial"), "Materials"),
                materials.ToArray());

            const int maxTextures = 24;
            IReadOnlyList<string> textures = GetModelTextures(model);
            System.Collections.IList objectNodes = GetFbxNodes(objectsNode);
            string publishedTextureRoot = Path.Combine(
                    NormalizeLocalPath(publishedOutputDir, "published model output"),
                    "MeshTextures") + Path.DirectorySeparatorChar;
            for (int textureIndex = 0;
                 textureIndex < Math.Min(textures.Count, maxTextures);
                 textureIndex++)
            {
                string replacement = textures[textureIndex]
                    .Replace(".tga", ".png")
                    .Replace("meshtex\\", string.Empty)
                    .Replace(" ", string.Empty);
                int textureNodeIndex = 2 + maxTextures + textureIndex;
                int videoNodeIndex = 2 + maxTextures + maxTextures + textureIndex;
                if (textureNodeIndex >= objectNodes.Count || videoNodeIndex >= objectNodes.Count)
                    throw new InvalidDataException("FBX template does not contain the expected texture/video nodes.");
                object textureNode = objectNodes[textureNodeIndex]
                    ?? throw new InvalidDataException("FBX template contains a missing texture node.");
                object videoNode = objectNodes[videoNodeIndex]
                    ?? throw new InvalidDataException("FBX template contains a missing video node.");
                string mediaName = "Video::" + replacement;
                string texturePath = publishedTextureRoot + replacement;

                SetFbxNodeValue(GetFbxNode(textureNode, "Media"), mediaName);
                SetFbxNodeValue(GetFbxNode(textureNode, "FileName"), texturePath);
                SetFbxNodeValue(GetFbxNode(textureNode, "RelativeFilename"), texturePath);

                System.Collections.IList videoProperties = GetFbxProperties(videoNode);
                if (videoProperties.Count <= 1)
                    throw new InvalidDataException("FBX template video node is missing its media property.");
                videoProperties[1] = mediaName;
                SetFbxNodeValue(GetFbxNode(videoNode, "Filename"), texturePath);
                SetFbxNodeValue(GetFbxNode(videoNode, "RelativeFilename"), texturePath);
                System.Collections.IList propertyValues = GetFbxProperties(
                    GetFbxNode(GetFbxNode(videoNode, "Properties70"), "P"));
                if (propertyValues.Count <= 4)
                    throw new InvalidDataException("FBX template video path property is incomplete.");
                propertyValues[4] = texturePath;
            }

            return document;
        }

        private object ReadFbxDocument(byte[] templateBytes)
        {
            Type readerType = _fbxAssembly.GetType("Fbx.FbxBinaryReader", throwOnError: true)!;
            Type errorLevelType = _fbxAssembly.GetType("Fbx.ErrorLevel", throwOnError: true)!;
            object checkedLevel = Enum.Parse(errorLevelType, "Checked");
            using var stream = new MemoryStream(templateBytes, writable: false);
            object reader = Activator.CreateInstance(readerType, new[] { stream, checkedLevel })
                ?? throw new InvalidOperationException("Failed to create FbxBinaryReader.");
            MethodInfo readMethod = readerType.GetMethod("Read", BindingFlags.Instance | BindingFlags.Public)
                ?? throw new MissingMethodException("FbxBinaryReader.Read");
            return readMethod.Invoke(reader, null)
                ?? throw new InvalidDataException("FBX template reader produced no document.");
        }

        private byte[] SerializeFbxDocument(object document, bool binary)
        {
            string writerName = binary ? "Fbx.FbxBinaryWriter" : "Fbx.FbxAsciiWriter";
            Type writerType = _fbxAssembly.GetType(writerName, throwOnError: true)!;
            using var stream = new MemoryStream();
            object writer = Activator.CreateInstance(writerType, new object[] { stream })
                ?? throw new InvalidOperationException($"Failed to create {writerName}.");
            MethodInfo writeMethod = writerType.GetMethod("Write", BindingFlags.Instance | BindingFlags.Public)
                ?? throw new MissingMethodException($"{writerName}.Write");
            writeMethod.Invoke(writer, new[] { document });
            return stream.ToArray();
        }

        private static IReadOnlyList<AyaIndexValue> GenerateTriListIndices(object model)
        {
            var result = new List<AyaIndexValue>();
            var strips = (System.Collections.IEnumerable)GetRequiredMemberValue(model, "AyaIndices");
            foreach (object stripValue in strips)
            {
                var strip = ((System.Collections.IEnumerable)stripValue)
                    .Cast<object>()
                    .Select(static value => new AyaIndexValue(
                        Convert.ToInt32(GetRequiredMemberValue(value, "index")),
                        Convert.ToInt32(GetRequiredMemberValue(value, "texture"))))
                    .ToArray();
                if (strip.Length is 1 or 2)
                    throw new InvalidDataException("AYA triangle strip has fewer than three indices.");

                int offset = 0;
                while (offset < strip.Length)
                {
                    AyaIndexValue a;
                    AyaIndexValue b;
                    AyaIndexValue c;
                    if (offset == 0)
                    {
                        a = strip[0];
                        b = strip[1];
                        c = strip[2];
                        offset += 3;
                    }
                    else
                    {
                        a = strip[offset - 1];
                        b = strip[offset - 2];
                        c = strip[offset];
                        if (offset % 2 == 1)
                            (b, a) = (a, b);
                        offset++;
                    }

                    if (a.Index == b.Index || a.Index == c.Index || b.Index == c.Index)
                        continue;
                    result.Add(a);
                    result.Add(b);
                    result.Add(c with { Index = -(c.Index + 1) });
                }
            }
            return result;
        }

        private static object GetRequiredMemberValue(object target, string name)
        {
            Type type = target.GetType();
            PropertyInfo? property = type.GetProperty(
                name,
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            if (property is not null)
                return property.GetValue(target)
                    ?? throw new InvalidDataException($"{type.Name}.{name} is null.");
            FieldInfo? field = type.GetField(
                name,
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            return field?.GetValue(target)
                ?? throw new MissingMemberException(type.FullName, name);
        }

        private static double ReadDoubleMember(object target, string name) =>
            Convert.ToDouble(GetRequiredMemberValue(target, name));

        private static object GetFbxNode(object nodeList, string name)
        {
            PropertyInfo indexer = nodeList.GetType().GetProperty(
                "Item",
                BindingFlags.Instance | BindingFlags.Public,
                binder: null,
                returnType: null,
                types: new[] { typeof(string) },
                modifiers: null)
                ?? throw new MissingMemberException(nodeList.GetType().FullName, "Item[string]");
            return indexer.GetValue(nodeList, new object[] { name })
                ?? throw new InvalidDataException($"FBX template is missing node '{name}'.");
        }

        private static void SetFbxNodeValue(object node, object value)
        {
            PropertyInfo property = node.GetType().GetProperty(
                "Value",
                BindingFlags.Instance | BindingFlags.Public)
                ?? throw new MissingMemberException(node.GetType().FullName, "Value");
            property.SetValue(node, value);
        }

        private static System.Collections.IList GetFbxNodes(object nodeList) =>
            GetRequiredMemberValue(nodeList, "Nodes") as System.Collections.IList
                ?? throw new InvalidDataException("FBX node collection is not a list.");

        private static System.Collections.IList GetFbxProperties(object node) =>
            GetRequiredMemberValue(node, "Properties") as System.Collections.IList
                ?? throw new InvalidDataException("FBX property collection is not a list.");

        private GeneratedOutputSeal ExportModel(
            string outputRoot,
            string resourcesRoot,
            object model,
            string modelName,
            string stagingDir,
            string publishedOutputDir,
            bool binaryFbx,
            bool asciiFbx)
        {
            var seal = new GeneratedOutputSeal(outputRoot, stagingDir);
            try
            {
                string textureOutputRoot = Path.Combine(stagingDir, "MeshTextures");
                seal.PinDirectory(textureOutputRoot);
                foreach (string textureName in GetModelTextures(model).Take(24))
                {
                    string? sourcePath = ResolveModelTextureSource(resourcesRoot, textureName);
                    if (sourcePath is null)
                        continue;

                    string outputName = GetModelTextureOutputName(textureName);
                    string outputPath = Path.Combine(textureOutputRoot, outputName);
                    if (!seal.ContainsFile(outputPath))
                        seal.CreatePinnedFile(outputPath, ExportTextureBytes(sourcePath));
                }

                object document = BuildFbxDocument(model, publishedOutputDir);
                if (asciiFbx)
                {
                    seal.CreatePinnedFile(
                        Path.Combine(stagingDir, $"{modelName}_ascii.fbx"),
                        SerializeFbxDocument(document, binary: false));
                }
                if (binaryFbx)
                {
                    seal.CreatePinnedFile(
                        Path.Combine(stagingDir, $"{modelName}_binary.fbx"),
                        SerializeFbxDocument(document, binary: true));
                }
                return seal;
            }
            catch
            {
                seal.Dispose();
                throw;
            }
        }

        private IReadOnlyList<string> GetModelTextures(object model)
        {
            PropertyInfo property = model.GetType().GetProperty(
                "Textures",
                BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?? throw new MissingMemberException("AyaModel.Textures");
            if (property.GetValue(model) is not System.Collections.IEnumerable values)
                throw new InvalidOperationException("AyaModel.Textures is not enumerable.");

            return values.Cast<object?>()
                .Select(static value => value as string
                    ?? throw new InvalidDataException("AyaModel contained a non-text texture name."))
                .ToArray();
        }

        private static string? ResolveModelTextureSource(string resourcesRoot, string textureName)
        {
            string extractorName = textureName;
            int folderIndex = extractorName.IndexOf('\\');
            if (folderIndex >= 0)
                extractorName = extractorName[(folderIndex + 1)..];

            string textureRoot = Path.Combine(resourcesRoot, "dxtntextures");
            string a1Path = Path.Combine(textureRoot, $"meshtex%{extractorName}(0)A1R5G5B5.aya");
            if (File.Exists(a1Path))
                return a1Path;
            string a8Path = Path.Combine(textureRoot, $"meshtex%{extractorName}(0)A8R8G8B8.aya");
            return File.Exists(a8Path) ? a8Path : null;
        }

        private static string GetModelTextureOutputName(string textureName)
        {
            string extractorName = textureName;
            int folderIndex = extractorName.IndexOf('\\');
            if (folderIndex >= 0)
                extractorName = extractorName[(folderIndex + 1)..];
            string outputName = Path.GetFileNameWithoutExtension(extractorName).Replace(" ", string.Empty);
            if (string.IsNullOrWhiteSpace(outputName))
                throw new InvalidDataException("AyaModel contained an invalid texture output name.");
            return outputName + ".png";
        }

        private string ResolveFbxTemplatePath()
        {
            string directPath = Path.Combine(_extractorRoot, "BoxWithTextures.fbx");
            if (File.Exists(directPath))
                return directPath;
            string fallbackPath = Path.GetFullPath(
                Path.Combine(_extractorRoot, @"..\..\..\..\..\BoxWithTextures.fbx"));
            if (File.Exists(fallbackPath))
                return fallbackPath;
            throw new FileNotFoundException("Could not find the FBX template used by AYAResourceExtractor.");
        }

        public GeneratedOutputSeal ExportTextureFile(
            string outputRoot,
            string stagingRoot,
            string inputAyaPath,
            string outputPngPath)
        {
            var seal = new GeneratedOutputSeal(outputRoot, stagingRoot);
            try
            {
                seal.CreatePinnedFile(outputPngPath, ExportTextureBytes(inputAyaPath));
                return seal;
            }
            catch
            {
                seal.Dispose();
                throw;
            }
        }

        private byte[] ExportTextureBytes(string inputAyaPath)
        {
            var ddsBytes = InflateAya(ReadLockedFileBytes(inputAyaPath, "texture source"));
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

            using var output = new MemoryStream();
            bitmap.Save(output, System.Drawing.Imaging.ImageFormat.Png);
            return output.ToArray();
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
            if (args is ["--self-test-output-safety"])
                return RunOutputSafetySelfTest();

            var options = ParseArgs(args);
            ValidateOutputRoot(options);
            using DirectoryLease outputLease = DirectoryLease.Open(options.OutDir, guardTargetMutation: true);
            using DirectoryLease resourcesLease = DirectoryLease.Open(options.ResourcesRoot);
            using DirectoryLease embeddedLease = DirectoryLease.Open(options.EmbeddedRoot);
            using DirectoryLease extractorRootLease = DirectoryLease.Open(options.ExtractorRoot);
            using DirectoryLease extractorRuntimeLease = DirectoryLease.Open(options.ExtractorRuntimeDir);
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
            WriteGeneratedText(
                options.OutDir,
                summaryPath,
                JsonSerializer.Serialize(summary, new JsonSerializerOptions { WriteIndented = true }));
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
        EnsureSafeDirectory(options.OutDir, laneRoot);
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
                ValidateExistingGeneratedOutputForSkip(options.OutDir, outputPath);
                succeeded++;
                var skippedRow = new { input, output = outputPath, status = "skipped_existing" };
                rows.Add(skippedRow);
                WriteProgress(options.OutDir, progressPath, skippedRow);
                MaybePrintProgress("loose_textures", index + 1, files.Count, input, "skipped_existing", options.ProgressEvery);
                continue;
            }

            try
            {
                RunStagedExport(
                    options.OutDir,
                    laneRoot,
                    stagingRoot => runtime.ExportTextureFile(
                        options.OutDir,
                        stagingRoot,
                        input,
                        Path.Combine(stagingRoot, relativeParent, outputName)));
                succeeded++;
                var okRow = new { input, output = outputPath, status = "ok" };
                rows.Add(okRow);
                WriteProgress(options.OutDir, progressPath, okRow);
                MaybePrintProgress("loose_textures", index + 1, files.Count, input, "ok", options.ProgressEvery);
            }
            catch (Exception ex)
            {
                failed++;
                var error = DescribeExportError(ex);
                var errorRow = new { input, output = outputPath, status = "error", error = error.Message, errorType = error.Type, wrappedError = error.WrapperMessage, wrappedErrorType = error.WrapperType };
                rows.Add(errorRow);
                WriteProgress(options.OutDir, progressPath, errorRow);
                Console.Error.WriteLine($"[loose_textures] {index + 1}/{files.Count} error {input}: {FormatErrorForConsole(error)}");
            }
        }

        var manifestPath = Path.Combine(laneRoot, "manifest.json");
        WriteGeneratedText(
            options.OutDir,
            manifestPath,
            JsonSerializer.Serialize(rows, new JsonSerializerOptions { WriteIndented = true }));
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
        EnsureSafeDirectory(options.OutDir, laneRoot);
        var progressPath = Path.Combine(laneRoot, "progress.jsonl");

        for (var index = 0; index < files.Count; index++)
        {
            var input = files[index];
            var outputPath = Path.Combine(laneRoot, $"{Path.GetFileNameWithoutExtension(input)}_binary.fbx");

            if (options.SkipExisting && File.Exists(outputPath))
            {
                ValidateExistingGeneratedOutputForSkip(options.OutDir, outputPath);
                succeeded++;
                var skippedRow = new { input, output = outputPath, status = "skipped_existing" };
                rows.Add(skippedRow);
                WriteProgress(options.OutDir, progressPath, skippedRow);
                MaybePrintProgress("loose_meshes", index + 1, files.Count, input, "skipped_existing", options.ProgressEvery);
                continue;
            }

            try
            {
                RunStagedExport(
                    options.OutDir,
                    laneRoot,
                    stagingRoot => runtime.ExportLooseMesh(
                        options.OutDir,
                        options.ResourcesRoot,
                        input,
                        stagingRoot,
                        laneRoot,
                        binaryFbx: true,
                        asciiFbx: false));
                succeeded++;
                var okRow = new { input, output = outputPath, status = "ok" };
                rows.Add(okRow);
                WriteProgress(options.OutDir, progressPath, okRow);
                MaybePrintProgress("loose_meshes", index + 1, files.Count, input, "ok", options.ProgressEvery);
            }
            catch (Exception ex)
            {
                failed++;
                var error = DescribeExportError(ex);
                var errorRow = new { input, output = outputPath, status = "error", error = error.Message, errorType = error.Type, wrappedError = error.WrapperMessage, wrappedErrorType = error.WrapperType };
                rows.Add(errorRow);
                WriteProgress(options.OutDir, progressPath, errorRow);
                Console.Error.WriteLine($"[loose_meshes] {index + 1}/{files.Count} error {input}: {FormatErrorForConsole(error)}");
            }
        }

        var manifestPath = Path.Combine(laneRoot, "manifest.json");
        WriteGeneratedText(
            options.OutDir,
            manifestPath,
            JsonSerializer.Serialize(rows, new JsonSerializerOptions { WriteIndented = true }));
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
        EnsureSafeDirectory(options.OutDir, laneRoot);
        var progressPath = Path.Combine(laneRoot, "progress.jsonl");

        for (var index = 0; index < files.Count; index++)
        {
            var input = files[index];
            var outputPath = Path.Combine(laneRoot, $"{Path.GetFileNameWithoutExtension(input)}_binary.fbx");

            if (options.SkipExisting && File.Exists(outputPath))
            {
                ValidateExistingGeneratedOutputForSkip(options.OutDir, outputPath);
                succeeded++;
                var skippedRow = new { input, output = outputPath, status = "skipped_existing" };
                rows.Add(skippedRow);
                WriteProgress(options.OutDir, progressPath, skippedRow);
                MaybePrintProgress("embedded_meshes", index + 1, files.Count, input, "skipped_existing", options.ProgressEvery);
                continue;
            }

            try
            {
                RunStagedExport(
                    options.OutDir,
                    laneRoot,
                    stagingRoot => runtime.ExportEmbeddedBody(
                        options.OutDir,
                        options.ResourcesRoot,
                        input,
                        stagingRoot,
                        laneRoot,
                        binaryFbx: true,
                        asciiFbx: false));
                succeeded++;
                var okRow = new { input, output = outputPath, status = "ok" };
                rows.Add(okRow);
                WriteProgress(options.OutDir, progressPath, okRow);
                MaybePrintProgress("embedded_meshes", index + 1, files.Count, input, "ok", options.ProgressEvery);
            }
            catch (Exception ex)
            {
                failed++;
                var error = DescribeExportError(ex);
                var errorRow = new { input, output = outputPath, status = "error", error = error.Message, errorType = error.Type, wrappedError = error.WrapperMessage, wrappedErrorType = error.WrapperType };
                rows.Add(errorRow);
                WriteProgress(options.OutDir, progressPath, errorRow);
                Console.Error.WriteLine($"[embedded_meshes] {index + 1}/{files.Count} error {input}: {FormatErrorForConsole(error)}");
            }
        }

        var manifestPath = Path.Combine(laneRoot, "manifest.json");
        WriteGeneratedText(
            options.OutDir,
            manifestPath,
            JsonSerializer.Serialize(rows, new JsonSerializerOptions { WriteIndented = true }));
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

    private static void ValidateOutputRoot(ExportOptions options)
    {
        string outputRoot = NormalizeLocalPath(options.OutDir, "output root");
        string resourcesRoot = NormalizeLocalPath(options.ResourcesRoot, "resources root");
        string embeddedRoot = NormalizeLocalPath(options.EmbeddedRoot, "embedded source root");
        if (PathsOverlap(outputRoot, resourcesRoot) || PathsOverlap(outputRoot, embeddedRoot))
        {
            throw new InvalidOperationException(
                "Asset export output cannot overlap resource or embedded-body inputs.");
        }

        string? current = outputRoot;
        while (!string.IsNullOrWhiteSpace(current))
        {
            if (File.Exists(Path.Combine(current, "BEA.exe")) &&
                Directory.Exists(Path.Combine(current, "data")))
            {
                throw new InvalidOperationException(
                    "Asset export output cannot be placed inside a Battle Engine Aquila game tree.");
            }

            string? parent = Path.GetDirectoryName(current);
            if (string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                break;
            current = parent;
        }

        EnsureSafeDirectory(outputRoot, outputRoot);
    }

    private static int RunOutputSafetySelfTest()
    {
        string root = Path.Combine(
            Path.GetTempPath(),
            "bea-asset-export-harness-self-test",
            Guid.NewGuid().ToString("N"));
        string resourcesRoot = Path.Combine(root, "resources");
        string embeddedRoot = Path.Combine(root, "embedded");
        string outputRoot = Path.Combine(root, "output");
        string outsidePath = Path.Combine(root, "outside.json");
        try
        {
            Directory.CreateDirectory(resourcesRoot);
            Directory.CreateDirectory(embeddedRoot);
            File.WriteAllText(outsidePath, "outside-canary");
            ExportOptions options = new(
                "self-test",
                root,
                resourcesRoot,
                root,
                root,
                embeddedRoot,
                outputRoot,
                null,
                null,
                null,
                1,
                1,
                1,
                false,
                1);
            ValidateOutputRoot(options);

            string movedOutputRoot = outputRoot + "-moved";
            using (DirectoryLease outputLease = DirectoryLease.Open(outputRoot, guardTargetMutation: true))
            {
                AssertSelfTestThrows<IOException>(() =>
                    Directory.Move(outputRoot, movedOutputRoot));
            }
            if (!Directory.Exists(outputRoot) || Directory.Exists(movedOutputRoot))
                throw new InvalidOperationException("Output-root lease did not preserve the expected directory identity.");

            string guardedPath = Path.Combine(outputRoot, "guarded.json");
            if (!CreateHardLinkW(guardedPath, outsidePath, IntPtr.Zero))
                throw new IOException($"Could not create self-test hardlink. Win32 error: {Marshal.GetLastWin32Error()}");
            AssertSelfTestThrows<InvalidOperationException>(() =>
                WriteGeneratedText(outputRoot, guardedPath, "unsafe replacement"));
            if (File.ReadAllText(outsidePath) != "outside-canary")
                throw new InvalidOperationException("Hardlink canary changed during generated-output self-test.");
            File.Delete(guardedPath);

            WriteGeneratedText(outputRoot, guardedPath, "safe replacement");
            if (File.ReadAllText(guardedPath) != "safe replacement")
                throw new InvalidOperationException("Atomic generated-output self-test did not publish expected content.");

            string racedStagePath = Path.Combine(outputRoot, "prewrite-race.bin");
            string racedAliasPath = Path.Combine(root, "prewrite-race-alias.bin");
            using (DirectoryLease outputGuard = DirectoryLease.Open(
                outputRoot,
                guardTargetMutation: true))
            {
                AssertSelfTestThrows<InvalidOperationException>(() =>
                    PinnedGeneratedFile.Create(
                        racedStagePath,
                        Encoding.UTF8.GetBytes("must-not-escape"),
                        createdPath =>
                        {
                            if (!CreateHardLinkW(racedAliasPath, createdPath, IntPtr.Zero))
                            {
                                throw new IOException(
                                    $"Could not create pre-write race alias. Win32 error: {Marshal.GetLastWin32Error()}");
                            }
                        }));
            }
            if (!File.Exists(racedAliasPath) || new FileInfo(racedAliasPath).Length != 0)
            {
                throw new InvalidOperationException(
                    "Pre-write hardlink race received generated bytes before quarantine rejection.");
            }
            File.Delete(racedAliasPath);

            string laneRoot = Path.Combine(outputRoot, "lane");
            RunStagedExport(
                outputRoot,
                laneRoot,
                stagingRoot =>
                {
                    var seal = new GeneratedOutputSeal(outputRoot, stagingRoot);
                    try
                    {
                        string payloadPath = Path.Combine(stagingRoot, "payload.bin");
                        seal.CreatePinnedFile(payloadPath, Encoding.UTF8.GetBytes("payload"));
                        if (CreateHardLinkW(payloadPath, outsidePath, IntPtr.Zero))
                            throw new InvalidOperationException("A hardlink replaced a pre-pinned staged output name.");

                        AssertSelfTestThrows<IOException>(() =>
                        {
                            using var writer = new FileStream(
                                payloadPath,
                                FileMode.Open,
                                FileAccess.Write,
                                FileShare.Read | FileShare.Write);
                            writer.WriteByte(0);
                        });

                        if (File.ReadAllText(outsidePath) != "outside-canary")
                            throw new InvalidOperationException("Staged-output hardlink canary changed during publication.");
                        return seal;
                    }
                    catch
                    {
                        seal.Dispose();
                        throw;
                    }
                });
            if (File.ReadAllText(Path.Combine(laneRoot, "payload.bin")) != "payload")
                throw new InvalidOperationException("Staged export self-test did not publish expected content.");

            string contestedLaneRoot = Path.Combine(outputRoot, "contested-lane");
            AssertSelfTestThrows<InvalidOperationException>(() =>
                RunStagedExport(
                    outputRoot,
                    contestedLaneRoot,
                    stagingRoot =>
                    {
                        var seal = new GeneratedOutputSeal(outputRoot, stagingRoot);
                        try
                        {
                            seal.CreatePinnedFile(
                                Path.Combine(stagingRoot, "expected.bin"),
                                Encoding.UTF8.GetBytes("expected"));
                            if (!CreateHardLinkW(
                                    Path.Combine(stagingRoot, "contested.bin"),
                                    outsidePath,
                                    IntPtr.Zero))
                            {
                                throw new IOException(
                                    $"Could not create contested-stage hardlink. Win32 error: {Marshal.GetLastWin32Error()}");
                            }
                            return seal;
                        }
                        catch
                        {
                            seal.Dispose();
                            throw;
                        }
                    }));
            string[] contestedResidues = Directory.Exists(contestedLaneRoot)
                ? Directory.GetDirectories(contestedLaneRoot, ".export-stage-*", SearchOption.TopDirectoryOnly)
                : [];
            if (contestedResidues.Length != 1 || File.ReadAllText(outsidePath) != "outside-canary")
            {
                throw new InvalidOperationException(
                    "Contested staging cleanup did not leave the ambiguous entry safely isolated.");
            }

            string gameRoot = Path.Combine(root, "separate-game");
            Directory.CreateDirectory(Path.Combine(gameRoot, "data"));
            File.WriteAllText(Path.Combine(gameRoot, "BEA.exe"), "test marker");
            ExportOptions gameTreeOptions = options with { OutDir = Path.Combine(gameRoot, "generated") };
            AssertSelfTestThrows<InvalidOperationException>(() => ValidateOutputRoot(gameTreeOptions));
            if (Directory.Exists(gameTreeOptions.OutDir))
                throw new InvalidOperationException("Game-tree output was created during rejection self-test.");

            Console.WriteLine("BeaAssetExportHarness output-safety self-test: PASS");
            return 0;
        }
        finally
        {
            if (Directory.Exists(root))
                CleanupDirectoryNoFollow(root);
        }
    }

    private static void AssertSelfTestThrows<TException>(Action action)
        where TException : Exception
    {
        try
        {
            action();
        }
        catch (TException)
        {
            return;
        }

        throw new InvalidOperationException($"Expected {typeof(TException).Name} during output-safety self-test.");
    }

    private static void RunStagedExport(
        string outputRoot,
        string laneRoot,
        Func<string, GeneratedOutputSeal> export)
    {
        EnsureSafeDirectory(outputRoot, laneRoot);
        using DirectoryLease laneLease = DirectoryLease.Open(laneRoot, guardTargetMutation: true);
        string stagingRoot = Path.Combine(laneRoot, $".export-stage-{Guid.NewGuid():N}");
        EnsureSafeDirectory(outputRoot, stagingRoot);
        try
        {
            using (DirectoryLease stagingLease = DirectoryLease.Open(stagingRoot, guardTargetMutation: true))
            using (GeneratedOutputSeal seal = export(stagingRoot))
            {
                seal.LockAndValidateTree(
                    stagingRoot,
                    [
                        stagingLease.GetValidatedMutationSentinelPath(),
                        .. seal.GetValidatedMutationSentinelPaths()
                    ]);
                PublishGeneratedTree(outputRoot, stagingRoot, laneRoot, seal);
            }
        }
        finally
        {
            CleanupStagingTree(outputRoot, stagingRoot);
        }
    }

    private static void PublishGeneratedTree(
        string outputRoot,
        string stagingRoot,
        string destinationRoot,
        GeneratedOutputSeal seal)
    {
        foreach (LockedGeneratedFile file in seal.LockedFiles
            .OrderBy(static file => file.Path, StringComparer.OrdinalIgnoreCase))
        {
            string relativePath = Path.GetRelativePath(stagingRoot, file.Path);
            string destinationPath = Path.Combine(destinationRoot, relativePath);
            EnsureSafeDirectory(outputRoot, Path.GetDirectoryName(destinationPath)!);
            WriteGeneratedFromHandle(outputRoot, destinationPath, file.Handle);
        }
    }

    private static void CollectGeneratedTree(
        string directory,
        List<string> files,
        List<string> directories)
    {
        directories.Add(NormalizeLocalPath(directory, "staged generated directory"));
        foreach (string entry in Directory.EnumerateFileSystemEntries(directory))
        {
            FileAttributes attributes = File.GetAttributes(entry);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"Generated export contains a reparse point: {entry}");
            if ((attributes & FileAttributes.Directory) != 0)
                CollectGeneratedTree(entry, files, directories);
            else
            {
                ValidateRegularSingleLinkFile(entry, "staged generated export");
                files.Add(NormalizeLocalPath(entry, "staged generated output"));
            }
        }
    }

    private static string ReadValidatedGeneratedText(string outputRoot, string path)
    {
        string normalizedPath = RequireUnderOutputRoot(outputRoot, path);
        using SafeFileHandle handle = OpenLockedReadHandle(normalizedPath, "existing generated output");
        ValidateRegularSingleLinkHandle(handle, normalizedPath, "existing generated output");
        return Encoding.UTF8.GetString(ReadAllFromHandle(handle));
    }

    private static void WriteGeneratedText(string outputRoot, string path, string text)
    {
        string normalizedPath = RequireUnderOutputRoot(outputRoot, path);
        WriteGeneratedBytes(
            outputRoot,
            normalizedPath,
            new UTF8Encoding(encoderShouldEmitUTF8Identifier: false).GetBytes(text));
    }

    private static void WriteGeneratedBytes(
        string outputRoot,
        string destinationPath,
        ReadOnlySpan<byte> bytes)
    {
        byte[] content = bytes.ToArray();
        PublishGeneratedContent(
            outputRoot,
            destinationPath,
            content.LongLength,
            handle =>
            {
                if (content.Length > 0)
                    RandomAccess.Write(handle, content, 0);
            });
    }

    private static void WriteGeneratedFromHandle(
        string outputRoot,
        string destinationPath,
        SafeFileHandle sourceHandle)
    {
        long sourceLength = RandomAccess.GetLength(sourceHandle);
        PublishGeneratedContent(
            outputRoot,
            destinationPath,
            sourceLength,
            destinationHandle => CopyHandleContent(sourceHandle, destinationHandle, sourceLength));
    }

    private static void PublishGeneratedContent(
        string outputRoot,
        string destinationPath,
        long expectedLength,
        Action<SafeFileHandle> writeContent)
    {
        string normalizedDestination = RequireUnderOutputRoot(outputRoot, destinationPath);
        string parent = Path.GetDirectoryName(normalizedDestination)
            ?? throw new InvalidOperationException("Generated output has no parent directory.");
        EnsureSafeDirectory(outputRoot, parent);
        using DirectoryLease parentLease = DirectoryLease.Open(parent, guardTargetMutation: true);
        ValidateExistingDestination(normalizedDestination);

        string temporaryPath = Path.Combine(
            parent,
            $".{Path.GetFileName(normalizedDestination)}.tmp-{Guid.NewGuid():N}");
        using SafeFileHandle temporaryHandle = CreateFileW(
            temporaryPath,
            GenericWrite | DeleteAccess | FileReadAttributes,
            FileShare.Read,
            IntPtr.Zero,
            FileMode.CreateNew,
            FileFlagOpenReparsePoint,
            IntPtr.Zero);
        if (temporaryHandle.IsInvalid)
        {
            int error = Marshal.GetLastWin32Error();
            throw new IOException(
                $"Could not create guarded generated-output temporary file. Win32 error: {error}");
        }

        bool committed = false;
        try
        {
            SetFileDeleteDisposition(temporaryHandle, delete: true);
            ValidateQuarantinedFileHandle(
                temporaryHandle,
                temporaryPath,
                "generated-output temporary");
            writeContent(temporaryHandle);
            RandomAccess.FlushToDisk(temporaryHandle);
            if (RandomAccess.GetLength(temporaryHandle) != expectedLength)
                throw new IOException("Generated-output temporary file length changed before publication.");
            ValidateQuarantinedFileHandle(
                temporaryHandle,
                temporaryPath,
                "generated-output temporary");

            ValidateExistingDestination(normalizedDestination);
            SetFileDeleteDisposition(temporaryHandle, delete: false);
            RenameFileHandle(temporaryHandle, normalizedDestination, replaceExisting: true);
            ValidateRegularSingleLinkHandle(
                temporaryHandle,
                normalizedDestination,
                "published generated output");
            if (RandomAccess.GetLength(temporaryHandle) != expectedLength)
                throw new IOException("Published generated-output length differs from the sealed source.");
            committed = true;
        }
        finally
        {
            if (!committed)
                TryMarkFileDeleted(temporaryHandle);
        }
    }

    private static void CopyHandleContent(
        SafeFileHandle sourceHandle,
        SafeFileHandle destinationHandle,
        long sourceLength)
    {
        byte[] buffer = System.Buffers.ArrayPool<byte>.Shared.Rent(128 * 1024);
        try
        {
            long offset = 0;
            while (offset < sourceLength)
            {
                int requested = (int)Math.Min(buffer.Length, sourceLength - offset);
                int read = RandomAccess.Read(sourceHandle, buffer.AsSpan(0, requested), offset);
                if (read <= 0)
                    throw new EndOfStreamException("Sealed generated output ended before its recorded length.");
                RandomAccess.Write(destinationHandle, buffer.AsSpan(0, read), offset);
                offset += read;
            }
        }
        finally
        {
            System.Buffers.ArrayPool<byte>.Shared.Return(buffer);
        }
    }

    private static byte[] ReadLockedFileBytes(string path, string label)
    {
        using SafeFileHandle handle = OpenLockedReadHandle(path, label);
        return ReadAllFromHandle(handle);
    }

    private static byte[] ReadAllFromHandle(SafeFileHandle handle)
    {
        long length = RandomAccess.GetLength(handle);
        if (length > int.MaxValue)
            throw new IOException("File is too large for this asset-export operation.");

        byte[] content = new byte[(int)length];
        long offset = 0;
        while (offset < length)
        {
            int read = RandomAccess.Read(handle, content.AsSpan((int)offset), offset);
            if (read <= 0)
                throw new EndOfStreamException("File ended before its recorded length.");
            offset += read;
        }
        return content;
    }

    private static SafeFileHandle OpenLockedReadHandle(string path, string label)
    {
        string normalizedPath = NormalizeLocalPath(path, label);
        SafeFileHandle handle = CreateFileW(
            normalizedPath,
            GenericRead,
            FileShare.Read,
            IntPtr.Zero,
            FileMode.Open,
            FileFlagOpenReparsePoint,
            IntPtr.Zero);
        if (handle.IsInvalid)
        {
            int error = Marshal.GetLastWin32Error();
            handle.Dispose();
            throw new IOException($"Could not lock {label} for reading. Win32 error: {error}");
        }

        try
        {
            if (!GetFileInformationByHandle(handle, out ByHandleFileInformation information))
                throw new IOException($"Could not inspect {label}: {normalizedPath}");
            if ((((FileAttributes)information.FileAttributes) &
                    (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0)
            {
                throw new InvalidOperationException($"{label} must be a regular file: {normalizedPath}");
            }
            if (!string.Equals(
                    ResolveFinalPath(handle, label),
                    normalizedPath,
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException($"{label} resolved somewhere unexpected: {normalizedPath}");
            }
            return handle;
        }
        catch
        {
            handle.Dispose();
            throw;
        }
    }

    private static void ValidateRegularSingleLinkHandle(
        SafeFileHandle handle,
        string expectedPath,
        string label)
    {
        if (!GetFileInformationByHandle(handle, out ByHandleFileInformation information))
            throw new IOException($"Could not inspect {label}: {expectedPath}");
        if ((((FileAttributes)information.FileAttributes) &
                (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0)
        {
            throw new InvalidOperationException($"{label} must be a regular file: {expectedPath}");
        }
        if (information.NumberOfLinks != 1)
            throw new InvalidOperationException($"{label} cannot be hardlinked: {expectedPath}");
        if (!string.Equals(
                ResolveFinalPath(handle, label),
                NormalizeLocalPath(expectedPath, label),
                StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException($"{label} changed path identity: {expectedPath}");
        }
    }

    private static void ValidateQuarantinedFileHandle(
        SafeFileHandle handle,
        string expectedPath,
        string label)
    {
        if (!GetFileInformationByHandle(handle, out ByHandleFileInformation information))
            throw new IOException($"Could not inspect {label}: {expectedPath}");
        if ((((FileAttributes)information.FileAttributes) &
                (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0)
        {
            throw new InvalidOperationException($"{label} must be a regular file: {expectedPath}");
        }
        if (information.NumberOfLinks != 0)
        {
            throw new InvalidOperationException(
                $"{label} gained an alias before its content was sealed: {expectedPath}");
        }
        if (!string.Equals(
                ResolveFinalPath(handle, label),
                NormalizeLocalPath(expectedPath, label),
                StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException($"{label} changed path identity: {expectedPath}");
        }
    }

    private static void RenameFileHandle(
        SafeFileHandle sourceHandle,
        string destinationPath,
        bool replaceExisting)
    {
        byte[] nameBytes = Encoding.Unicode.GetBytes(destinationPath);
        int rootDirectoryOffset = IntPtr.Size == 8 ? 8 : 4;
        int fileNameLengthOffset = rootDirectoryOffset + IntPtr.Size;
        int fileNameOffset = fileNameLengthOffset + sizeof(uint);
        byte[] buffer = new byte[checked(fileNameOffset + nameBytes.Length + sizeof(char))];
        uint flags = FileRenameFlagPosixSemantics |
            (replaceExisting ? FileRenameFlagReplaceIfExists : 0);
        BitConverter.GetBytes(flags).CopyTo(buffer, 0);
        BitConverter.GetBytes(nameBytes.Length).CopyTo(buffer, fileNameLengthOffset);
        nameBytes.CopyTo(buffer, fileNameOffset);

        IntPtr nativeBuffer = Marshal.AllocHGlobal(buffer.Length);
        try
        {
            Marshal.Copy(buffer, 0, nativeBuffer, buffer.Length);
            if (!SetFileInformationByHandle(
                    sourceHandle,
                    FileRenameInfoEx,
                    nativeBuffer,
                    (uint)buffer.Length))
            {
                int error = Marshal.GetLastWin32Error();
                throw new IOException(
                    $"Could not atomically publish generated output. Win32 error: {error}");
            }
        }
        finally
        {
            Marshal.FreeHGlobal(nativeBuffer);
        }
    }

    private static void SetFileDeleteDisposition(SafeFileHandle handle, bool delete)
    {
        uint flags = delete
            ? FileDispositionFlagDelete | FileDispositionFlagPosixSemantics
            : 0;
        byte[] buffer = BitConverter.GetBytes(flags);
        IntPtr nativeBuffer = Marshal.AllocHGlobal(buffer.Length);
        try
        {
            Marshal.Copy(buffer, 0, nativeBuffer, buffer.Length);
            if (!SetFileInformationByHandle(
                    handle,
                    FileDispositionInfoEx,
                    nativeBuffer,
                    (uint)buffer.Length))
            {
                int error = Marshal.GetLastWin32Error();
                throw new IOException(
                    $"Could not update generated-output quarantine state. Win32 error: {error}");
            }
        }
        finally
        {
            Marshal.FreeHGlobal(nativeBuffer);
        }
    }

    private static void TryMarkFileDeleted(SafeFileHandle handle)
    {
        try
        {
            SetFileDeleteDisposition(handle, delete: true);
        }
        catch
        {
            // Best effort cleanup retains the exact handle boundary on failure.
        }
    }

    private sealed record LockedGeneratedFile(string Path, SafeFileHandle Handle);

    private sealed class PinnedGeneratedFile : IDisposable
    {
        private readonly SafeFileHandle _ownerHandle;
        private readonly ByHandleFileInformation _identity;

        private PinnedGeneratedFile(
            string path,
            SafeFileHandle ownerHandle,
            ByHandleFileInformation identity)
        {
            Path = path;
            _ownerHandle = ownerHandle;
            _identity = identity;
        }

        internal string Path { get; }

        internal static PinnedGeneratedFile Create(
            string path,
            ReadOnlySpan<byte> initialContent,
            Action<string>? afterCreateForTest = null)
        {
            string normalizedPath = NormalizeLocalPath(path, "pre-pinned generated output");
            SafeFileHandle owner = CreateFileW(
                normalizedPath,
                GenericRead | GenericWrite | DeleteAccess | FileReadAttributes,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.CreateNew,
                FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (owner.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                owner.Dispose();
                throw new IOException(
                    $"Could not reserve expected staged output '{normalizedPath}'. Win32 error: {error}");
            }

            try
            {
                afterCreateForTest?.Invoke(normalizedPath);
                SetFileDeleteDisposition(owner, delete: true);
                ValidateQuarantinedFileHandle(
                    owner,
                    normalizedPath,
                    "pre-pinned generated output");
                if (!initialContent.IsEmpty)
                    RandomAccess.Write(owner, initialContent, 0);
                RandomAccess.FlushToDisk(owner);
                ValidateQuarantinedFileHandle(
                    owner,
                    normalizedPath,
                    "pre-pinned generated output");
                SetFileDeleteDisposition(owner, delete: false);

                if (!GetFileInformationByHandle(owner, out ByHandleFileInformation ownerInfo) ||
                    ownerInfo.NumberOfLinks != 1 ||
                    (((FileAttributes)ownerInfo.FileAttributes) & FileAttributes.ReparsePoint) != 0 ||
                    !string.Equals(
                        ResolveFinalPath(owner, "pre-pinned generated output"),
                        normalizedPath,
                        StringComparison.OrdinalIgnoreCase))
                {
                    throw new InvalidOperationException(
                        $"Expected staged output changed identity while it was being pinned: {normalizedPath}");
                }

                var result = new PinnedGeneratedFile(normalizedPath, owner, ownerInfo);
                owner = null!;
                return result;
            }
            finally
            {
                if (owner is not null)
                    TryMarkFileDeleted(owner);
                owner?.Dispose();
            }
        }

        internal LockedGeneratedFile OpenLockedRead()
        {
            if (!GetFileInformationByHandle(_ownerHandle, out ByHandleFileInformation current) ||
                !IsSameFile(_identity, current) ||
                current.NumberOfLinks != 1 ||
                !string.Equals(
                    ResolveFinalPath(_ownerHandle, "staged generated output"),
                    Path,
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"Staged generated output changed identity before publication: {Path}");
            }
            using SafeFileHandle pathHandle = CreateFileW(
                Path,
                GenericRead,
                FileShare.Read | FileShare.Write | FileShare.Delete,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (pathHandle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                throw new IOException(
                    $"Could not verify the staged generated-output path. Win32 error: {error}");
            }
            if (!GetFileInformationByHandle(pathHandle, out ByHandleFileInformation pathIdentity) ||
                !IsSameFile(_identity, pathIdentity) ||
                pathIdentity.NumberOfLinks != 1 ||
                !string.Equals(
                    ResolveFinalPath(pathHandle, "staged generated-output path"),
                    Path,
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"Staged generated-output path no longer names its sealed identity: {Path}");
            }
            if (RandomAccess.GetLength(_ownerHandle) <= 0)
                throw new InvalidDataException($"Staged generated output is empty: {Path}");
            return new LockedGeneratedFile(Path, _ownerHandle);
        }

        public void Dispose()
        {
            TryMarkFileDeleted(_ownerHandle);
            _ownerHandle.Dispose();
        }
    }

    private sealed class GeneratedOutputSeal : IDisposable
    {
        private readonly string _outputRoot;
        private readonly string _stagingRoot;
        private readonly Dictionary<string, PinnedGeneratedFile> _files =
            new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, DirectoryLease?> _directories =
            new(StringComparer.OrdinalIgnoreCase);
        private readonly List<LockedGeneratedFile> _lockedFiles = [];
        private bool _locked;

        internal GeneratedOutputSeal(string outputRoot, string stagingRoot)
        {
            _outputRoot = NormalizeLocalPath(outputRoot, "output root");
            _stagingRoot = RequireUnderOutputRoot(_outputRoot, stagingRoot);
            _directories.Add(_stagingRoot, null);
        }

        internal IReadOnlyList<LockedGeneratedFile> LockedFiles => _lockedFiles;

        internal bool ContainsFile(string path) =>
            _files.ContainsKey(RequireUnderStagingRoot(path));

        internal void PinDirectory(string path)
        {
            string normalizedPath = RequireUnderStagingRoot(path, allowRoot: true);
            if (_directories.ContainsKey(normalizedPath))
                return;

            string parent = Path.GetDirectoryName(normalizedPath)
                ?? throw new InvalidOperationException("Generated-output directory has no parent.");
            PinDirectory(parent);
            EnsureSafeDirectory(_outputRoot, normalizedPath);
            _directories.Add(
                normalizedPath,
                DirectoryLease.Open(normalizedPath, guardTargetMutation: true));
        }

        internal void CreatePinnedFile(string path, ReadOnlySpan<byte> initialContent)
        {
            if (_locked)
                throw new InvalidOperationException("Cannot add outputs after the generated-output seal is locked.");
            string normalizedPath = RequireUnderStagingRoot(path);
            if (_files.ContainsKey(normalizedPath))
                throw new InvalidOperationException($"Duplicate expected generated output: {normalizedPath}");
            string parent = Path.GetDirectoryName(normalizedPath)
                ?? throw new InvalidOperationException("Generated output has no parent directory.");
            PinDirectory(parent);
            _files.Add(normalizedPath, PinnedGeneratedFile.Create(normalizedPath, initialContent));
        }

        internal IReadOnlyList<string> GetValidatedMutationSentinelPaths() =>
            _directories.Values
                .Where(static lease => lease is not null)
                .Select(static lease => lease!.GetValidatedMutationSentinelPath())
                .ToArray();

        internal void LockAndValidateTree(
            string stagingRoot,
            IReadOnlyCollection<string> ignoredSentinelPaths)
        {
            if (_locked)
                throw new InvalidOperationException("Generated-output seal is already locked.");
            if (!string.Equals(
                    _stagingRoot,
                    NormalizeLocalPath(stagingRoot, "staging root"),
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException("Generated-output seal belongs to a different staging root.");
            }

            try
            {
                foreach (PinnedGeneratedFile file in _files.Values)
                    _lockedFiles.Add(file.OpenLockedRead());
                _locked = true;

                var files = new List<string>();
                var directories = new List<string>();
                CollectGeneratedTree(_stagingRoot, files, directories);
                var actualFiles = new HashSet<string>(files, StringComparer.OrdinalIgnoreCase);
                foreach (string sentinelPath in ignoredSentinelPaths)
                {
                    if (!actualFiles.Remove(sentinelPath))
                        throw new InvalidOperationException("Generated-output directory guard disappeared.");
                }
                var actualDirectories = new HashSet<string>(directories, StringComparer.OrdinalIgnoreCase);
                var expectedFiles = new HashSet<string>(_files.Keys, StringComparer.OrdinalIgnoreCase);
                var expectedDirectories = new HashSet<string>(_directories.Keys, StringComparer.OrdinalIgnoreCase);
                if (!actualFiles.SetEquals(expectedFiles))
                {
                    throw new InvalidOperationException(
                        "Staged export contains missing or unexpected generated files.");
                }
                if (!actualDirectories.SetEquals(expectedDirectories))
                {
                    throw new InvalidOperationException(
                        "Staged export contains missing or unexpected generated directories.");
                }
            }
            catch
            {
                _lockedFiles.Clear();
                throw;
            }
        }

        private string RequireUnderStagingRoot(string path, bool allowRoot = false)
        {
            string normalizedPath = NormalizeLocalPath(path, "staged generated output");
            if (!IsSameOrUnder(normalizedPath, _stagingRoot) ||
                (!allowRoot && string.Equals(
                    normalizedPath,
                    _stagingRoot,
                    StringComparison.OrdinalIgnoreCase)))
            {
                throw new InvalidOperationException("Expected generated output escapes its staging root.");
            }
            return normalizedPath;
        }

        public void Dispose()
        {
            _lockedFiles.Clear();
            foreach (PinnedGeneratedFile file in _files.Values)
                file.Dispose();
            _files.Clear();
            foreach (DirectoryLease? lease in _directories.Values.Reverse())
                lease?.Dispose();
            _directories.Clear();
        }
    }

    private static void ValidateExistingDestination(string path)
    {
        try
        {
            FileAttributes attributes = File.GetAttributes(path);
            if ((attributes & (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0)
                throw new InvalidOperationException($"Unsafe generated-output destination: {path}");
            ValidateRegularSingleLinkFile(path, "existing generated output");
        }
        catch (FileNotFoundException)
        {
        }
        catch (DirectoryNotFoundException)
        {
        }
    }

    private static void ValidateExistingGeneratedOutputForSkip(
        string outputRoot,
        string path)
    {
        string normalizedPath = RequireUnderOutputRoot(outputRoot, path);
        using SafeFileHandle handle = OpenLockedReadHandle(
            normalizedPath,
            "existing generated output selected for skip");
        ValidateRegularSingleLinkHandle(
            handle,
            normalizedPath,
            "existing generated output selected for skip");
        if (RandomAccess.GetLength(handle) <= 0)
            throw new InvalidDataException(
                $"Existing generated output selected for skip is empty: {normalizedPath}");
    }

    private static void ValidateRegularSingleLinkFile(string path, string label)
    {
        FileAttributes attributes = File.GetAttributes(path);
        if ((attributes & (FileAttributes.Directory | FileAttributes.ReparsePoint)) != 0)
            throw new InvalidOperationException($"{label} must be a regular file: {path}");

        using SafeFileHandle handle = File.OpenHandle(
            path,
            FileMode.Open,
            FileAccess.Read,
            FileShare.Read | FileShare.Write | FileShare.Delete);
        if (!GetFileInformationByHandle(handle, out ByHandleFileInformation information))
            throw new IOException($"Could not inspect {label}: {path}");
        if (information.NumberOfLinks != 1)
            throw new InvalidOperationException($"{label} cannot be hardlinked: {path}");
    }

    private static void EnsureSafeDirectory(string outputRoot, string directory)
    {
        string normalizedRoot = NormalizeLocalPath(outputRoot, "output root");
        string normalizedDirectory = NormalizeLocalPath(directory, "generated-output directory");
        if (!IsSameOrUnder(normalizedDirectory, normalizedRoot))
            throw new InvalidOperationException("Generated-output directory escapes the output root.");

        string? existing = normalizedDirectory;
        while (!string.IsNullOrWhiteSpace(existing) && !Directory.Exists(existing))
            existing = Path.GetDirectoryName(existing);
        for (string? current = existing; !string.IsNullOrWhiteSpace(current); current = Path.GetDirectoryName(current))
        {
            FileAttributes attributes = File.GetAttributes(current);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"Generated-output directory uses a reparse point: {current}");
            string? parent = Path.GetDirectoryName(current);
            if (string.Equals(parent, current, StringComparison.OrdinalIgnoreCase))
                break;
        }

        Directory.CreateDirectory(normalizedDirectory);
        for (string? current = normalizedDirectory;
             !string.IsNullOrWhiteSpace(current) && IsSameOrUnder(current, normalizedRoot);
             current = Path.GetDirectoryName(current))
        {
            FileAttributes attributes = File.GetAttributes(current);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
                throw new InvalidOperationException($"Generated-output directory uses a reparse point: {current}");
            if (string.Equals(current, normalizedRoot, StringComparison.OrdinalIgnoreCase))
                break;
        }
    }

    private static void CleanupStagingTree(string outputRoot, string stagingRoot)
    {
        string normalizedStage = RequireUnderOutputRoot(outputRoot, stagingRoot);
        if (!Path.GetFileName(normalizedStage).StartsWith(".export-stage-", StringComparison.Ordinal))
            throw new InvalidOperationException("Refusing to clean a non-staging directory.");
        if (!Directory.Exists(normalizedStage))
            return;
        CleanupEmptyStagingDirectories(normalizedStage);
    }

    private static void CleanupEmptyStagingDirectories(string directory)
    {
        FileAttributes rootAttributes = File.GetAttributes(directory);
        if ((rootAttributes & FileAttributes.ReparsePoint) != 0)
            return;

        foreach (string entry in Directory.EnumerateFileSystemEntries(directory))
        {
            FileAttributes attributes = File.GetAttributes(entry);
            if ((attributes & (FileAttributes.Directory | FileAttributes.ReparsePoint)) == FileAttributes.Directory)
                CleanupEmptyStagingDirectories(entry);
        }

        if (Directory.EnumerateFileSystemEntries(directory).Any())
            return;
        try
        {
            Directory.Delete(directory);
        }
        catch (IOException)
        {
            // Leave contested or identity-ambiguous staging paths for explicit inspection.
        }
        catch (UnauthorizedAccessException)
        {
            // A safe residue is preferable to path-based deletion of an untrusted entry.
        }
    }

    private static void CleanupDirectoryNoFollow(string directory)
    {
        foreach (string entry in Directory.EnumerateFileSystemEntries(directory))
        {
            FileAttributes attributes = File.GetAttributes(entry);
            if ((attributes & FileAttributes.ReparsePoint) != 0)
            {
                if ((attributes & FileAttributes.Directory) != 0)
                    Directory.Delete(entry);
                else
                    File.Delete(entry);
            }
            else if ((attributes & FileAttributes.Directory) != 0)
                CleanupDirectoryNoFollow(entry);
            else
                File.Delete(entry);
        }
        Directory.Delete(directory);
    }

    private static string RequireUnderOutputRoot(string outputRoot, string path)
    {
        string normalizedRoot = NormalizeLocalPath(outputRoot, "output root");
        string normalizedPath = NormalizeLocalPath(path, "generated output");
        if (!IsSameOrUnder(normalizedPath, normalizedRoot) ||
            string.Equals(normalizedPath, normalizedRoot, StringComparison.OrdinalIgnoreCase))
        {
            throw new InvalidOperationException("Generated output escapes the output root.");
        }
        return normalizedPath;
    }

    private static string NormalizeLocalPath(string path, string label)
    {
        if (string.IsNullOrWhiteSpace(path))
            throw new ArgumentException($"{label} is required.", nameof(path));
        string fullPath = Path.GetFullPath(path);
        if (fullPath.StartsWith(@"\\", StringComparison.Ordinal) ||
            fullPath.StartsWith(@"\\?\", StringComparison.Ordinal) ||
            fullPath.StartsWith(@"\\.\", StringComparison.Ordinal) ||
            fullPath.IndexOf(':', 2) >= 0)
        {
            throw new InvalidOperationException($"{label} must use a local DOS path without alternate streams.");
        }
        string root = Path.GetPathRoot(fullPath) ?? string.Empty;
        foreach (string component in fullPath[root.Length..].Split(
            [Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar],
            StringSplitOptions.RemoveEmptyEntries))
        {
            if (component.EndsWith(' ') || component.EndsWith('.'))
                throw new InvalidOperationException($"{label} cannot use trailing spaces or periods.");
            string stem = component.Split('.', 2)[0];
            if (ReservedDosNames.Contains(stem))
                throw new InvalidOperationException(
                    $"{label} cannot use the reserved DOS device name '{stem}'.");
        }
        return string.Equals(fullPath, root, StringComparison.OrdinalIgnoreCase)
            ? root
            : fullPath.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
    }

    private static bool PathsOverlap(string left, string right) =>
        IsSameOrUnder(left, right) || IsSameOrUnder(right, left);

    private static bool IsSameOrUnder(string path, string root)
    {
        string normalizedPath = NormalizeLocalPath(path, "path");
        string normalizedRoot = NormalizeLocalPath(root, "root");
        return string.Equals(normalizedPath, normalizedRoot, StringComparison.OrdinalIgnoreCase) ||
            normalizedPath.StartsWith(
                normalizedRoot + Path.DirectorySeparatorChar,
                StringComparison.OrdinalIgnoreCase);
    }

    private static bool IsSameFile(
        ByHandleFileInformation left,
        ByHandleFileInformation right) =>
        left.VolumeSerialNumber == right.VolumeSerialNumber &&
        left.FileIndexHigh == right.FileIndexHigh &&
        left.FileIndexLow == right.FileIndexLow;

    private static string ResolveFinalPath(SafeFileHandle handle, string label)
    {
        var buffer = new StringBuilder(512);
        uint length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
        if (length == 0)
            throw new IOException($"Could not resolve {label}. Win32 error: {Marshal.GetLastWin32Error()}");
        if (length >= buffer.Capacity)
        {
            buffer.EnsureCapacity(checked((int)length + 1));
            length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
            if (length == 0 || length >= buffer.Capacity)
                throw new IOException($"Could not resolve {label}. Win32 error: {Marshal.GetLastWin32Error()}");
        }

        string resolved = buffer.ToString();
        if (resolved.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase))
            throw new InvalidOperationException($"{label} resolved to a network path.");
        if (resolved.StartsWith(@"\\?\", StringComparison.Ordinal))
            resolved = resolved[4..];
        if (resolved.StartsWith(@"\??\", StringComparison.Ordinal))
            resolved = resolved[4..];
        return NormalizeLocalPath(resolved, label);
    }

    private sealed class DirectoryLease : IDisposable
    {
        private const uint FileListDirectory = 0x0001;
        private const uint FileFlagBackupSemantics = 0x02000000;
        private readonly List<SafeFileHandle> _handles;
        private readonly SafeFileHandle? _mutationSentinel;
        private readonly string? _mutationSentinelPath;

        private DirectoryLease(
            List<SafeFileHandle> handles,
            SafeFileHandle? mutationSentinel,
            string? mutationSentinelPath)
        {
            _handles = handles;
            _mutationSentinel = mutationSentinel;
            _mutationSentinelPath = mutationSentinelPath;
        }

        internal static DirectoryLease Open(
            string path,
            bool guardTargetMutation = false)
        {
            string target = NormalizeLocalPath(path, "leased directory");
            if (!Directory.Exists(target))
                throw new DirectoryNotFoundException($"Leased directory does not exist: {target}");

            var ancestors = new Stack<string>();
            for (DirectoryInfo? current = new(target); current is not null; current = current.Parent)
                ancestors.Push(current.FullName);

            var handles = new List<SafeFileHandle>();
            try
            {
                foreach (string ancestor in ancestors)
                {
                    FileAttributes attributes = File.GetAttributes(ancestor);
                    if ((attributes & FileAttributes.ReparsePoint) != 0)
                        throw new InvalidOperationException($"Leased directory uses a reparse point: {ancestor}");

                    SafeFileHandle handle = CreateFileW(
                        ancestor,
                        FileListDirectory,
                        FileShare.Read | FileShare.Write,
                        IntPtr.Zero,
                        FileMode.Open,
                        FileFlagBackupSemantics | FileFlagOpenReparsePoint,
                        IntPtr.Zero);
                    if (handle.IsInvalid)
                    {
                        int error = Marshal.GetLastWin32Error();
                        handle.Dispose();
                        throw new IOException($"Could not lease directory '{ancestor}'. Win32 error: {error}");
                    }

                    string resolved = ResolveFinalPath(handle);
                    string expected = NormalizeLocalPath(ancestor, "leased directory");
                    if (!string.Equals(resolved, expected, StringComparison.OrdinalIgnoreCase))
                    {
                        handle.Dispose();
                        throw new InvalidOperationException(
                            $"Leased directory resolved somewhere unexpected: {ancestor}");
                    }
                    handles.Add(handle);
                }

                string? sentinelPath = null;
                SafeFileHandle? sentinel = guardTargetMutation
                    ? CreateMutationSentinel(target, handles[^1], out sentinelPath)
                    : null;
                return new DirectoryLease(handles, sentinel, sentinelPath);
            }
            catch
            {
                for (int index = handles.Count - 1; index >= 0; index--)
                    handles[index].Dispose();
                throw;
            }
        }

        private static SafeFileHandle CreateMutationSentinel(
            string target,
            SafeFileHandle relaxedTargetHandle,
            out string sentinelPath)
        {
            using SafeFileHandle strictHandle = CreateFileW(
                target,
                FileListDirectory,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.Open,
                FileFlagBackupSemantics | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (strictHandle.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                throw new IOException(
                    $"Could not guard generated-output directory mutation. Win32 error: {error}");
            }
            if (!GetFileInformationByHandle(strictHandle, out ByHandleFileInformation strictInfo) ||
                !GetFileInformationByHandle(relaxedTargetHandle, out ByHandleFileInformation relaxedInfo) ||
                !IsSameFile(strictInfo, relaxedInfo) ||
                (((FileAttributes)strictInfo.FileAttributes) & FileAttributes.ReparsePoint) != 0 ||
                !string.Equals(
                    Program.ResolveFinalPath(strictHandle, "guarded generated-output directory"),
                    target,
                    StringComparison.OrdinalIgnoreCase))
            {
                throw new InvalidOperationException(
                    $"Generated-output directory changed before mutation guard creation: {target}");
            }

            sentinelPath = Path.Combine(
                target,
                $".onslaught-directory-guard-{Guid.NewGuid():N}.tmp");
            SafeFileHandle sentinel = CreateFileW(
                sentinelPath,
                GenericRead | GenericWrite | DeleteAccess | FileReadAttributes,
                FileShare.Read,
                IntPtr.Zero,
                FileMode.CreateNew,
                FileAttributeTemporary | FileFlagDeleteOnClose | FileFlagOpenReparsePoint,
                IntPtr.Zero);
            if (sentinel.IsInvalid)
            {
                int error = Marshal.GetLastWin32Error();
                sentinel.Dispose();
                throw new IOException(
                    $"Could not create generated-output directory mutation guard. Win32 error: {error}");
            }
            try
            {
                ValidateRegularSingleLinkHandle(
                    sentinel,
                    sentinelPath,
                    "generated-output directory mutation guard");
                return sentinel;
            }
            catch
            {
                sentinel.Dispose();
                throw;
            }
        }

        internal string GetValidatedMutationSentinelPath()
        {
            if (_mutationSentinel is null || string.IsNullOrWhiteSpace(_mutationSentinelPath))
                throw new InvalidOperationException("Directory lease has no mutation sentinel.");
            ValidateRegularSingleLinkHandle(
                _mutationSentinel,
                _mutationSentinelPath,
                "generated-output directory mutation guard");
            return _mutationSentinelPath;
        }

        private static string ResolveFinalPath(SafeFileHandle handle)
        {
            var buffer = new StringBuilder(512);
            uint length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
            if (length == 0)
                throw new IOException($"Could not resolve leased directory. Win32 error: {Marshal.GetLastWin32Error()}");
            if (length >= buffer.Capacity)
            {
                buffer.EnsureCapacity(checked((int)length + 1));
                length = GetFinalPathNameByHandleW(handle, buffer, (uint)buffer.Capacity, 0);
                if (length == 0 || length >= buffer.Capacity)
                    throw new IOException($"Could not resolve leased directory. Win32 error: {Marshal.GetLastWin32Error()}");
            }

            string resolved = buffer.ToString();
            if (resolved.StartsWith(@"\\?\UNC\", StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Leased directory resolved to a network path.");
            if (resolved.StartsWith(@"\\?\", StringComparison.Ordinal))
                resolved = resolved[4..];
            return NormalizeLocalPath(resolved, "leased directory");
        }

        public void Dispose()
        {
            for (int index = _handles.Count - 1; index >= 0; index--)
                _handles[index].Dispose();
            _handles.Clear();
            _mutationSentinel?.Dispose();
        }
    }

    private static void WriteProgress(string outputRoot, string progressPath, object row)
    {
        string existing = File.Exists(progressPath)
            ? ReadValidatedGeneratedText(outputRoot, progressPath)
            : string.Empty;
        WriteGeneratedText(
            outputRoot,
            progressPath,
            existing + JsonSerializer.Serialize(row) + Environment.NewLine);
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

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool GetFileInformationByHandle(
        SafeFileHandle hFile,
        out ByHandleFileInformation lpFileInformation);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern SafeFileHandle CreateFileW(
        string lpFileName,
        uint dwDesiredAccess,
        FileShare dwShareMode,
        IntPtr lpSecurityAttributes,
        FileMode dwCreationDisposition,
        uint dwFlagsAndAttributes,
        IntPtr hTemplateFile);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandleW(
        SafeFileHandle hFile,
        StringBuilder lpszFilePath,
        uint cchFilePath,
        uint dwFlags);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CreateHardLinkW(
        string lpFileName,
        string lpExistingFileName,
        IntPtr lpSecurityAttributes);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetFileInformationByHandle(
        SafeFileHandle hFile,
        int fileInformationClass,
        IntPtr lpFileInformation,
        uint dwBufferSize);

    [StructLayout(LayoutKind.Sequential)]
    private struct ByHandleFileInformation
    {
        public uint FileAttributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME CreationTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastAccessTime;
        public System.Runtime.InteropServices.ComTypes.FILETIME LastWriteTime;
        public uint VolumeSerialNumber;
        public uint FileSizeHigh;
        public uint FileSizeLow;
        public uint NumberOfLinks;
        public uint FileIndexHigh;
        public uint FileIndexLow;
    }
}
