// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Assets;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>
/// Reads every installed mesh with the companion's reader and prints the counts tools/cmsh_grammar_walk.py prints, and
/// the same composition check, so the two independent readers can be compared. It then exports every mesh to glTF and
/// reads each export back with Godot's own glTF importer (counting the animations and skins it finds), and decodes every texture and encodes it as PNG. A few
/// exports are kept in the test output folder for inspection. The game folder comes from BEA_GAME and
/// is only read: <c>BEA_GAME=GAME python tools/companion_godot.py test --script Development/AssetCheck.cs</c>.
/// </summary>
public partial class AssetCheck : SceneTree
{
    private bool _ran;

    // The checks run on the first frame, with the engine fully started.
    public override bool _Process(double delta)
    {
        if (_ran) return false;
        _ran = true;
        Run();
        return false;
    }

    private void Run()
    {
        int exit = 1;
        try
        {
            string game = System.Environment.GetEnvironmentVariable("BEA_GAME") ?? "";
            string folder = Path.Combine(game, "data", "resources", "meshes");
            if (!Directory.Exists(folder))
            {
                GD.PrintErr("Set BEA_GAME to the game folder.");
                exit = 2;
                return;
            }
            string output = OS.GetCmdlineUserArgs().FirstOrDefault(a => a.StartsWith("--output-dir=", StringComparison.Ordinal))?["--output-dir=".Length..] ?? "";
            AssetLibrary library = AssetLibrary.Scan(game);
            Dictionary<string, DdsImage?> decoded = new(StringComparer.OrdinalIgnoreCase);
            DdsImage? Texture(string name)
            {
                if (decoded.TryGetValue(name, out DdsImage? cached)) return cached;
                string? path = library.FindTexture(name);
                return decoded[name] = path is null ? null : DdsTexture.Decode(AyaContainer.Inflate(File.ReadAllBytes(path)));
            }
            int exported = 0, imported = 0, unresolved = 0, animations = 0, skins = 0;
            CmshCounts counts = new();
            int files = 0, failures = 0, positions = 0, orientations = 0, mismatched = 0;
            double worstPosition = 0, worstOrientation = 0;
            string only = System.Environment.GetEnvironmentVariable("ASSET_ONLY") ?? "";
            foreach (string file in Directory.GetFiles(folder, "*.aya").Order(StringComparer.Ordinal)
                .Where(f => only.Length == 0 || Path.GetFileName(f).Contains(only, StringComparison.OrdinalIgnoreCase)))
            {
                files++;
                try
                {
                    IReadOnlyList<CmshMesh> meshes = CmshReader.Read(AyaContainer.Inflate(File.ReadAllBytes(file)), counts);
                    byte[] glb = GltfExport.Write(meshes[0], name =>
                    {
                        DdsImage? image = Texture(name);
                        if (image is null) unresolved++;
                        return image;
                    }, Png);
                    exported++;
                    GltfDocument document = new();
                    GltfState state = new();
                    if (document.AppendFromBuffer(glb, "", state) == Error.Ok && document.GenerateScene(state) is Node3D scene)
                    {
                        imported++;
                        animations += state.GetAnimations().Count;
                        skins += state.GetSkins().Count;
                        scene.Free();
                    }
                    else GD.PrintErr($"FAIL {Path.GetFileName(file)}: Godot could not import the export");
                    bool keepAll = System.Environment.GetEnvironmentVariable("ASSET_KEEP") == "all";
                    if (output.Length > 0 && (keepAll || Path.GetFileName(file) is "m_arachnid.msh.aya" or "m_ftrooper.msh.aya" or "m_be_trans.msh.aya"))
                        File.WriteAllBytes(Path.Combine(output, Path.GetFileName(file)[..^8] + ".glb"), glb);
                    foreach (CmshMesh mesh in meshes)
                        for (int p = 0; p < mesh.Parts.Count; p++)
                        {
                            CmshPart part = mesh.Parts[p];
                            for (int frame = 0; frame < part.CachedFrameCount; frame++)
                            {
                                PartTransform composed = mesh.ModelSpace(p, frame);
                                if (part.CachedPositions is { } cached && frame < cached.Length)
                                {
                                    float scale = 1 + MathF.Max(MathF.Abs(composed.Position.X), MathF.Max(MathF.Abs(composed.Position.Y), MathF.Abs(composed.Position.Z)));
                                    double error = MaxAbs(cached[frame] - composed.Position) / scale;
                                    worstPosition = Math.Max(worstPosition, error);
                                    if (error <= 1e-5) positions++; else mismatched++;
                                }
                                if (part.CachedOrientations is { } cachedOrientations && frame < cachedOrientations.Length)
                                {
                                    MeshBasis s = cachedOrientations[frame], o = composed.Orientation;
                                    double error = Math.Max(MaxAbs(s.Row0 - o.Row0), Math.Max(MaxAbs(s.Row1 - o.Row1), MaxAbs(s.Row2 - o.Row2)));
                                    worstOrientation = Math.Max(worstOrientation, error);
                                    if (error <= 1e-5) orientations++; else mismatched++;
                                }
                            }
                        }
                }
                catch (InvalidDataException error)
                {
                    failures++;
                    GD.PrintErr($"FAIL {Path.GetFileName(file)}: {error.Message}");
                }
            }
            GD.Print($"ASSET_CHECK: {files - failures} of {files} streams read; meshes {counts.Meshes}, parts {counts.Parts}, " +
                $"pieces {counts.Pieces}, textures {counts.Textures}, animation modes {counts.AnimModes}, collision grids {counts.CollisionGrids}");
            GD.Print($"ASSET_COMPOSE: {positions} cached positions and {orientations} cached orientations equal the composed keys; " +
                $"{mismatched} differ; worst relative position error {worstPosition:0.00e+00}, worst orientation element error {worstOrientation:0.00e+00}");
            int textures = 0, textureFailures = 0;
            foreach (GameAsset texture in library.Textures)
            {
                try
                {
                    byte[] png = Png(DdsTexture.Decode(AyaContainer.Inflate(File.ReadAllBytes(texture.Path))));
                    if (png.Length > 8) textures++; else textureFailures++;
                }
                catch (InvalidDataException error)
                {
                    textureFailures++;
                    GD.PrintErr($"FAIL {Path.GetFileName(texture.Path)}: {error.Message}");
                }
            }
            foreach (string bank in Directory.GetFiles(Path.Combine(game, "data", "sounds"), "*.xap").Order(StringComparer.Ordinal))
            {
                using System.Security.Cryptography.IncrementalHash whole = System.Security.Cryptography.IncrementalHash.CreateHash(System.Security.Cryptography.HashAlgorithmName.SHA256);
                IReadOnlyList<XapSample> samples = XapBank.Read(File.ReadAllBytes(bank));
                foreach (XapSample sample in samples)
                {
                    short[] pcm = XapBank.Decode(sample);
                    byte[] bytes = new byte[pcm.Length * 2];
                    Buffer.BlockCopy(pcm, 0, bytes, 0, bytes.Length);
                    whole.AppendData(bytes);
                }
                GD.Print($"PCM_BANK {Path.GetFileName(bank)} {Convert.ToHexString(whole.GetHashAndReset()).ToLowerInvariant()} ({samples.Count} samples)");
            }
            // Every Goodie archive through the companion's reader, hashed as tools/goodie_resource_walk.py hashes it.
            int goodies = 0, goodieFailures = 0;
            using (System.Security.Cryptography.IncrementalHash content = System.Security.Cryptography.IncrementalHash.CreateHash(System.Security.Cryptography.HashAlgorithmName.SHA256))
            {
                for (int number = 0; number < 1000; number++)
                {
                    if (!File.Exists(Path.Combine(game, "data", "resources", GoodieResources.ArchiveName(number)))) continue;
                    goodies++;
                    try
                    {
                        GoodieContent goodie = GoodieResources.Read(game, number);
                        IEnumerable<string> shown = goodie.Kind switch
                        {
                            GoodieKind.Video => ["video/" + goodie.Video],
                            GoodieKind.Level => [$"level {goodie.Level}"],
                            _ => goodie.Files,
                        };
                        content.AppendData(System.Text.Encoding.UTF8.GetBytes($"{number} {(int)goodie.Kind} {string.Join(" | ", shown)}\n"));
                        if (goodie.Missing.Count > 0)
                        {
                            goodieFailures++;
                            GD.PrintErr($"FAIL Goodie {number}: missing {string.Join(", ", goodie.Missing)}");
                        }
                    }
                    catch (Exception error) when (error is IOException or InvalidDataException)
                    {
                        goodieFailures++;
                        GD.PrintErr($"FAIL Goodie {number}: {error.Message}");
                    }
                }
                GD.Print($"GOODIE_CONTENT {Convert.ToHexString(content.GetHashAndReset()).ToLowerInvariant()} ({goodies} archives, {goodieFailures} failures)");
            }
            GD.Print($"ASSET_ANIMATION: Godot's importer read {animations} animations and {skins} skins from the exports");
            GD.Print($"ASSET_EXPORT: {exported} models exported to glTF, {imported} read back by Godot's importer, {unresolved} texture " +
                $"lookups unresolved; {textures} of {library.Textures.Count} textures decoded and encoded as PNG");
            exit = failures == 0 && mismatched == 0 && imported == exported && textureFailures == 0 && unresolved == 0 && goodieFailures == 0 ? 0 : 1;
        }
        finally
        {
            Quit(exit);
        }
    }

    private static byte[] Png(DdsImage image) =>
        Image.CreateFromData(image.Width, image.Height, false, Image.Format.Rgba8, image.Rgba).SavePngToBuffer();

    private static double MaxAbs(System.Numerics.Vector3 v) => Math.Max(Math.Abs(v.X), Math.Max(Math.Abs(v.Y), Math.Abs(v.Z)));
}
