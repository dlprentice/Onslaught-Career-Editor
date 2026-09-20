// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.IO.Compression;
using System.Security.Cryptography;
using Godot;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;
using SA = System.Array;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Exact pre-port Aquila fixtures using original terrain/material owners.
/// Private meshes and textures are read in place; generated comparison scenes
/// and object-free receipts require fresh explicitly owned output paths.</summary>
public sealed partial class AquilaSceneChecks : Node
{
    private const BindingFlags Hidden = BindingFlags.NonPublic | BindingFlags.Static;
    private const BindingFlags Fields = BindingFlags.NonPublic | BindingFlags.Instance;
    private static readonly Type Legacy = typeof(LegacyRetailAquilaReference);
    private int _checks;

    public override void _Ready()
    {
        LegacyLevel100HeightFieldReference? terrain = null;
        var ownedRoots = new List<Node3D>();
        var ownedTextures = new List<Texture2D>();
        try
        {
            string[] args = OS.GetCmdlineUserArgs();
            Check(args.Length == 2 && !Engine.IsEditorHint() && DisplayServer.GetName() == "headless", "Headless runtime and two fresh owned outputs required.");
            string fixturePath = Owned(args[0]), reportPath = Owned(args[1]);
            Check(fixturePath != reportPath, "Distinct output paths.");
            terrain = LegacyLevel100HeightFieldReference.Load();
            var pointer = Input.MouseMode;
            Texture2D Texture(string path, int size) { Texture2D value = CuratedAyaTextureLoader.Load(path, size, size); ownedTextures.Add(value); return value; }
            Texture2D cockpit = Texture("res://Assets/Aquila/Textures/cockpit.texture.aya", 512);
            Texture2D a = Texture("res://Assets/Aquila/Textures/be-tex-a.texture.aya", 512);
            Texture2D b = Texture("res://Assets/Aquila/Textures/be-tex-b.texture.aya", 1024);
            Texture2D chrome = Texture("res://Assets/Level100/StaticWorld/Textures/meshtex-chrome3.texture.aya", 128);
            Texture2D gun = Texture("res://Assets/Aquila/Textures/bluegun-light.texture.aya", 64);
            using var gunMaterial = new StandardMaterial3D { AlbedoTexture = gun, ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
                CullMode = BaseMaterial3D.CullModeEnum.Disabled, Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
                BlendMode = BaseMaterial3D.BlendModeEnum.Add, EmissionEnabled = true, Emission = new Color(.12f, .45f, 1f),
                EmissionTexture = gun, EmissionEnergyMultiplier = 1.6f };
            D hashes = new();
            foreach (string path in new[] { "res://Assets/Aquila/Source/m_f_be1.msh.aya", "res://Assets/Aquila/Source/m_f_be2.msh.aya", "res://Assets/Aquila/Source/m_cockpit2.msh.aya",
                "res://Assets/Aquila/Textures/cockpit.texture.aya", "res://Assets/Aquila/Textures/be-tex-a.texture.aya", "res://Assets/Aquila/Textures/be-tex-b.texture.aya",
                "res://Assets/Aquila/Textures/bluegun-light.texture.aya", "res://Assets/Level100/StaticWorld/Textures/meshtex-chrome3.texture.aya" }) hashes[path] = Hex(Godot.FileAccess.GetFileAsBytes(path));
            // Private-inflater diagnostics are retained as evidence, but the
            // production contract is LoadExact's prior length+SHA admission.
            // These independently generated inputs never copy retail payloads.
            A inflationDiagnostics = InflationFixtures();
            foreach (Variant item in inflationDiagnostics)
            {
                D diagnostic = item.AsGodotDictionary();
                string path = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, "synthetic-" + diagnostic["name"].AsString() + ".aya"));
                File.WriteAllBytes(path, diagnostic["input"].AsByteArray());
                diagnostic["source_path"] = path;
                hashes[path] = Hex(File.ReadAllBytes(path));
            }
            A profiles = [];
            foreach (string name in new[] { "walker", "jet", "cockpit" })
            {
                string sourcePath = "res://Assets/Aquila/Source/" + (name == "walker" ? "m_f_be1" : name == "jet" ? "m_f_be2" : "m_cockpit2") + ".msh.aya";
                IReadOnlyDictionary<int, Texture2D> textures = name switch {
                    "walker" => new Dictionary<int, Texture2D> { [0] = cockpit, [1] = b, [3] = a },
                    "jet" => new Dictionary<int, Texture2D> { [0] = cockpit, [1] = chrome, [2] = b, [3] = chrome, [4] = a },
                    _ => new Dictionary<int, Texture2D> { [0] = gun, [1] = cockpit, [2] = chrome } };
                IReadOnlyDictionary<string, Material>? overrides = name == "cockpit" ? new Dictionary<string, Material> { ["layers-00000000-ffffffff-ffffffff-ffffffff-ffffffff-ffffffff"] = gunMaterial } : null;
                LegacyRetailAquilaReference asset = name switch {
                    "walker" => LegacyRetailAquilaReference.Load(sourcePath, textures, terrain),
                    "jet" => LegacyRetailAquilaReference.LoadJet(sourcePath, textures, terrain),
                    _ => LegacyRetailAquilaReference.LoadCockpit(sourcePath, textures, overrides!, terrain) };
                ownedRoots.Add(asset.Root); AddChild(asset.Root);
                object parts = Legacy.GetField("_parts", Fields)!.GetValue(asset)!;
                object profile = Legacy.GetField("_profile", Fields)!.GetValue(asset)!;
                byte[] source = Godot.FileAccess.GetFileAsBytes(sourcePath);
                byte[] data = (byte[])Invoke("InflateAya", source);
                D row = new() { ["name"] = name, ["source_path"] = sourcePath, ["decoded_sha256"] = Hex(data),
                    ["definition"] = Definition(asset, parts), ["initial"] = SceneFacts(asset.Root), ["frames"] = new A(), ["contacts"] = new A(), ["mutations"] = new A() };
                A textureMetadata = [];
                foreach (object texture in (SA)Get(Invoke("ParseExactAsset", data, profile), "Textures"))
                    textureMetadata.Add(new D { ["opacity"] = (float)Get(texture,"Opacity"), ["offset"] = (Vector2)Get(texture,"Offset"), ["scale"] = (Vector2)Get(texture,"Scale") });
                ((D)row["definition"])["textures"] = textureMetadata;
                A sourceAdmission = [];
                void RejectSource(string path, string caseName)
                {
                    D admission = new() { ["name"] = caseName, ["source_path"] = path };
                    try
                    {
                        LegacyRetailAquilaReference unexpected = name switch {
                            "walker" => LegacyRetailAquilaReference.Load(path, textures, terrain),
                            "jet" => LegacyRetailAquilaReference.LoadJet(path, textures, terrain),
                            _ => LegacyRetailAquilaReference.LoadCockpit(path, textures, overrides!, terrain) };
                        unexpected.Root.Free();
                        admission["result"] = new D { ["ok"] = true };
                    }
                    catch(Exception error) { admission["result"] = Failure(error); }
                    sourceAdmission.Add(admission);
                }
                foreach(Variant item in inflationDiagnostics)
                {
                    D diagnostic = item.AsGodotDictionary();
                    RejectSource(diagnostic["source_path"].AsString(), diagnostic["name"].AsString());
                }
                string zeroPath = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, name + "-same-size-zero.aya"));
                File.WriteAllBytes(zeroPath, new byte[source.Length]);
                hashes[zeroPath] = Hex(File.ReadAllBytes(zeroPath));
                RejectSource(zeroPath, "same-size-wrong-hash");
                row["source_admission"] = sourceAdmission;
                // Raw decoded frames are independently evaluated even for the
                // walker whose live SetVirtualFrame method refuses that owner.
                var frameWords = new SortedSet<uint> { 0, 0x80000000, 1, 0xbf800000, 0x3f000000, 0x3f800000, 0x3fc00000,
                    0x41c40000, 0x41c80000, 0x41cc0000, 0x42480000, 0x42c80000, 0x7f7fffff, 0x7f800000, 0xff800000, 0x7fc00000 };
                var random = new Random(219731);
                for (int index = 0; index < 32; index++) frameWords.Add(BitConverter.SingleToUInt32Bits((float)(random.NextDouble() * 105.0 - 2.0)));
                foreach (uint word in frameWords)
                {
                    float frame = BitConverter.UInt32BitsToSingle(word);
                    D f = new() { ["word"] = (long)word };
                    try { f["transforms"] = TransformWords((SA)Invoke("BuildGlobalTransforms", parts, frame)); f["result"] = new D { ["ok"] = true }; }
                    catch (Exception error) { f["result"] = Failure(error); }
                    ((A)row["frames"]).Add(f);
                }
                // The public methods' mutation/failure order and external root
                // transform preservation are captured after each operation.
                var operations = new A();
                asset.Root.Transform = new Transform3D(Basis.FromEuler(new Vector3(.17f,-.43f,.29f)), new Vector3(.5f,1.25f,-.75f));
                operations.Add(new D { ["kind"] = "root", ["value"] = asset.Root.Transform, ["result"] = new D { ["ok"] = true }, ["state"] = Transforms(asset.Root) });
                foreach (float frame in new[] { 0f, 1.5f, 25f, 48.5f, float.PositiveInfinity, float.NegativeInfinity })
                {
                    D step = new() { ["kind"] = "frame", ["word"] = Word(frame) };
                    try { asset.SetVirtualFrame(frame); step["result"] = new D { ["ok"] = true }; }
                    catch (Exception error) { step["result"] = Failure(error); }
                    step["state"] = Transforms(asset.Root); operations.Add(step);
                }
                var contacts = new Vector3[] { new(.75f, -.8f, -.7f), new(.75f, -.8f, .7f), new(-.75f, -.8f, .7f), new(-.75f, -.8f, -.7f) };
                List<Vector3[]?> contactCases = [null, [], [Vector3.Zero], contacts, contacts.Select(v => v + new Vector3(.03f, .17f, -.09f)).ToArray(), [Vector3.Zero, Vector3.Zero, Vector3.Zero, Vector3.Zero]];
                for (int sample = 0; sample < 24; sample++) contactCases.Add(contacts.Select(v => v + new Vector3((float)(random.NextDouble()-.5), (float)(random.NextDouble()-.5), (float)(random.NextDouble()-.5))).ToArray());
                foreach (float word in new[] { float.NaN, float.PositiveInfinity, float.NegativeInfinity, float.MaxValue, float.Epsilon })
                    contactCases.Add([new Vector3(word, 0, 0), contacts[1], contacts[2], contacts[3]]);
                foreach (Vector3[]? values in contactCases)
                {
                    D step = new() { ["kind"] = "contacts", ["value"] = values is null ? default(Variant) : Variant.From(values) };
                    try { asset.SetGroundContactPose(values!); step["result"] = new D { ["ok"] = true }; }
                    catch (Exception error) { step["result"] = Failure(error); }
                    step["state"] = Transforms(asset.Root); operations.Add(step);
                }
                row["operations"] = operations;
                // Fresh state is saved; contact-only mutation on non-walkers is
                // intentional reference behavior, not the public saved pose.
                asset.Root.Basis = Basis.Identity;
                if (name == "walker") Legacy.GetMethod("SetStandingPose", Fields)!.Invoke(asset, null);
                else { asset.SetVirtualFrame(25f); asset.Root.Position = name == "jet" ? new Vector3(0,.6706632f,0) : Vector3.Zero; }
                OwnChildren(asset.Root, asset.Root);
                string scenePath = Owned(Path.Combine(Path.GetDirectoryName(fixturePath)!, name + "-legacy.tscn"));
                using (var packed = new PackedScene()) { Check(packed.Pack(asset.Root) == Error.Ok, "Pack legacy hierarchy."); Check(ResourceSaver.Save(packed, scenePath) == Error.Ok, "Save private legacy hierarchy."); }
                row["scene_path"] = scenePath; hashes[scenePath] = Hex(File.ReadAllBytes(scenePath));
                AddMutations((A)row["mutations"], data, profile);
                profiles.Add(row);
            }
            A signatures = [];
            foreach (int[]? indices in new int[]?[] { null, [], [0,1,2,3,4], [0,-1,-1,-1,-1,-1], [int.MinValue,int.MaxValue,-1,0,1,17] })
            {
                D row = new() { ["input"] = indices is null ? default(Variant) : Variant.From(indices) };
                try { row["result"] = new D { ["ok"] = true, ["value"] = (string)Invoke("MaterialSignature", indices!) }; }
                catch (Exception error) { row["result"] = Failure(error); }
                signatures.Add(row);
            }
            D fixture = new() { ["schema"] = 1, ["completed"] = new A { "aquila_reference" }, ["profiles"] = profiles,
                ["signatures"] = signatures, ["private_inflater_diagnostics"] = inflationDiagnostics, ["facts"] = new D { ["ambient_color_rgb24"] = terrain.AmbientColorRgb24, ["sun_color_rgb24"] = terrain.SunColorRgb24,
                    ["anti_sun_color_rgb24"] = terrain.AntiSunColorRgb24, ["sunlight_direction"] = terrain.SunlightDirection, ["fog_color"] = terrain.FogColor, ["fog_density"] = terrain.FogDensity }, ["hashes"] = hashes };
            foreach (Variant path in hashes.Keys) Check(Hex(Godot.FileAccess.GetFileAsBytes(path.AsString())) == hashes[path].AsString(), "Input remains unchanged.");
            Check(Input.MouseMode == pointer, "Pointer is unchanged.");
            using (var file = Godot.FileAccess.Open(fixturePath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Fixture output unavailable.")) file.StoreVar(fixture, false);
            using (var file = Godot.FileAccess.Open(reportPath, Godot.FileAccess.ModeFlags.Write) ?? throw new IOException("Report output unavailable.")) file.StoreString(Json.Stringify(new D { ["schema"] = 1, ["failure_count"] = 0, ["completed"] = new A { "aquila_reference" }, ["counts"] = new D { ["checks"] = _checks, ["profiles"] = profiles.Count } }));
            foreach (Node3D node in ownedRoots) node.Free(); ownedRoots.Clear();
            terrain.Mesh.Dispose(); terrain = null;
            foreach (Texture2D texture in ownedTextures) texture.Dispose(); ownedTextures.Clear();
            GD.Print($"AQUILA_REFERENCE: {_checks} checks, three exact profiles; {fixturePath}");
            GetTree().Quit(0);
        }
        catch (Exception error) { foreach (Node3D node in ownedRoots) node.Free(); terrain?.Mesh.Dispose(); foreach (Texture2D texture in ownedTextures) texture.Dispose(); GD.PushError(error.ToString()); GetTree().Quit(1); }
    }

    private static object Invoke(string name, params object?[] arguments)
    {
        try { return Legacy.GetMethod(name, Hidden)!.Invoke(null, arguments)!; }
        catch (TargetInvocationException error) when (error.InnerException is not null) { throw error.InnerException; }
    }
    private static object Get(object value, string property) => value.GetType().GetProperty(property)!.GetValue(value)!;
    private static D Definition(LegacyRetailAquilaReference asset, object input)
    {
        A parts = []; var geometries = new Dictionary<object, int>(ReferenceEqualityComparer.Instance);
        foreach (object part in (SA)input)
        {
            object? geometry = Get(part, "Geometry"); int owner = -1;
            if (geometry is not null && !geometries.TryGetValue(geometry, out owner)) { owner = (int)Get(part,"Index"); geometries.Add(geometry,owner); }
            var orientations = ((SA)Get(part,"Orientations")).Cast<object>().SelectMany(value => MatrixWords(Get(value,"Rotation"))).ToArray();
            D row = new() { ["index"] = (int)Get(part,"Index"), ["name"] = (string)Get(part,"Name"), ["virtual_count"] = (int)Get(part,"VirtualFrameCount"), ["horizontal_count"] = (int)Get(part,"HorizontalFrameCount"),
                ["parent"] = Get(part,"Parent") is int parent ? Variant.From(parent) : default, ["reference"] = Get(part,"Reference") is int reference ? Variant.From(reference) : default,
                ["children"] = (int[])Get(part,"Children"), ["frame_map"] = (byte[])Get(part,"FrameMap"), ["base_transform"] = Words(Get(part,"BaseGlobalTransform")),
                ["orientations"] = orientations, ["positions"] = (Vector3[])Get(part,"Positions"), ["geometry_owner"] = owner, ["geometry"] = geometry is null ? default(Variant) : Variant.From(GeometryFacts(geometry)) };
            parts.Add(row);
        }
        return new D { ["parts"] = parts, ["part_count"] = asset.PartCount, ["surface_count"] = asset.SurfaceCount, ["animated_count"] = asset.AnimatedPartCount,
            ["standing_clearance"] = Word(asset.StandingClearance), ["leg_lengths"] = new A(((float[][])Legacy.GetField("_legFrameLengths",Fields)!.GetValue(asset)!).Select(v => Variant.From(v))) };
    }
    private static D GeometryFacts(object geometry)
    {
        A groups = []; foreach (object group in (SA)Get(geometry,"Groups")) groups.Add(new D { ["triangles"] = (int[])Get(group,"Triangles"), ["texture_indices"] = (int[])Get(group,"TextureIndices") });
        return new D { ["vertices"] = Hex(GD.VarToBytes((Vector3[])Get(geometry,"Vertices"))), ["normals"] = Hex(GD.VarToBytes((Vector3[])Get(geometry,"Normals"))),
            ["uvs"] = Hex(GD.VarToBytes((Vector2[])Get(geometry,"TextureCoordinates"))), ["colors"] = Hex(GD.VarToBytes((Color[])Get(geometry,"Colors"))), ["groups"] = groups };
    }
    private static float[] MatrixWords(object value) => Enumerable.Range(0,9).Select(index => (float)Get(value,$"M{index / 3}{index % 3}")).ToArray();
    private static float[] Words(object value) => [.. MatrixWords(Get(value,"Rotation")), ((Vector3)Get(value,"Position")).X, ((Vector3)Get(value,"Position")).Y, ((Vector3)Get(value,"Position")).Z];
    private static float[] TransformWords(SA values) => values.Cast<object>().SelectMany(Words).ToArray();
    private static D Transforms(Node3D root)
    {
        D result = new() { ["."] = GD.VarToBytes(root.Transform) };
        void Visit(Node node) { foreach (Node child in node.GetChildren()) { if (child is Node3D transform) result[root.GetPathTo(child).ToString()] = GD.VarToBytes(transform.Transform); Visit(child); } }
        Visit(root); return result;
    }
    private static D SceneFacts(Node3D root)
    {
        D meshes = new(); var aliases = new Dictionary<Mesh,int>(ReferenceEqualityComparer.Instance); var materials = new Dictionary<Material,int>(ReferenceEqualityComparer.Instance);
        void Visit(Node node) { foreach (Node child in node.GetChildren()) { if (child is MeshInstance3D mesh) {
            if (!aliases.TryGetValue(mesh.Mesh,out int alias)) { alias=aliases.Count; aliases.Add(mesh.Mesh,alias); }
            A surfaces=[]; for(int i=0;i<mesh.Mesh.GetSurfaceCount();i++) { Material material=mesh.Mesh.SurfaceGetMaterial(i); if(!materials.TryGetValue(material,out int matAlias)){matAlias=materials.Count;materials.Add(material,matAlias);} surfaces.Add(new D { ["name"]=((ArrayMesh)mesh.Mesh).SurfaceGetName(i), ["primitive"]=(int)((ArrayMesh)mesh.Mesh).SurfaceGetPrimitiveType(i), ["format"]=mesh.Mesh.Call("surface_get_format",i).AsInt64(), ["arrays"]=Hex(GD.VarToBytes(mesh.Mesh.SurfaceGetArrays(i))), ["material_alias"]=matAlias, ["material"]=MaterialFacts(material) }); }
            meshes[root.GetPathTo(mesh).ToString()]=new D { ["alias"]=alias, ["shadow"]=(int)mesh.CastShadow, ["surfaces"]=surfaces }; } Visit(child); } }
        Visit(root); return new D { ["root_name"]=root.Name.ToString(), ["transforms"]=Transforms(root), ["meshes"]=meshes };
    }
    private static D MaterialFacts(Material material)
    {
        D result=new() { ["class"]=material.GetClass() };
        if(material is ShaderMaterial shader) {
            D values=new(); foreach(string name in new[]{"has_dot3","has_reflection","has_overlay","base_blend_texture_alpha","alpha_reference","stage_zero_gain","dot3_offset","dot3_scale","reflection_factor_alpha","overlay_offset","overlay_scale","overlay_opacity","ambient_color","sun_color","anti_sun_color","sunlight_direction","fog_color","fog_density","maximum_horizontal_distance_squared"}) values[name]=GD.VarToBytes(shader.GetShaderParameter(name));
            D textures=new();foreach(string name in new[]{"base_texture","dot3_texture","reflection_texture","overlay_texture"}){using Variant v=shader.GetShaderParameter(name);Texture2D? texture=v.AsGodotObject() as Texture2D;if(texture is not null){using Image image=texture.GetImage();textures[name]=Hex(image.GetData());}}
            result["values"]=values;result["textures"]=textures;
        } else if(material is StandardMaterial3D standard) {
            result["shading"]=(int)standard.ShadingMode; result["cull"]=(int)standard.CullMode;result["transparency"]=(int)standard.Transparency;result["blend"]=(int)standard.BlendMode;
            result["emission_enabled"]=standard.EmissionEnabled;result["emission"]=GD.VarToBytes(standard.Emission);result["energy"]=Word(standard.EmissionEnergyMultiplier);
            using Image a=standard.AlbedoTexture.GetImage();using Image e=standard.EmissionTexture.GetImage();result["albedo"]=Hex(a.GetData());result["emission_texture"]=Hex(e.GetData());result["same_texture"]=ReferenceEquals(standard.AlbedoTexture,standard.EmissionTexture);
        } return result;
    }
    private static void AddMutations(A result, byte[] data, object profile)
    {
        void Case(string name,int offset,int value,int width=4,int truncate=-1) {
            byte[] copy=truncate>=0 ? data.AsSpan(0,truncate).ToArray() : data.ToArray();
            if(offset>=0) { if(width==1) copy[offset]=(byte)value;else BitConverter.GetBytes(value).CopyTo(copy,offset); }
            D row=new() { ["name"]=name,["offset"]=offset,["value"]=value,["width"]=width,["truncate"]=truncate };
            try { object parsed=Invoke("ParseExactAsset",copy,profile);object parts=Get(parsed,"Parts");Invoke("ResolveAndValidateHierarchy",parts,Get(profile,"BasePoseValidationFrame"),Get(profile,"InitialFrame"),Get(profile,"DisplayName"));
                if((bool)Get(profile,"IsWalker")){Invoke("BuildLegFrameLengths",parts);Invoke("BuildStandingClearance",parts);}row["result"]=new D { ["ok"]=true }; }
            catch(Exception error){row["result"]=Failure(error);} result.Add(row);
        }
        foreach(int length in new[]{0,1,7,379,data.Length-1})Case("truncate-"+length,-1,0,truncate:length);
        Case("wrong-CMSH-tag",0,0);Case("negative-CMSH-length",4,-1);Case("overflow-CMSH-length",4,int.MaxValue);Case("wrong-texture-count",12,0);Case("wrong-part-count",8+0x15c,0);
        int cursor=0;while(cursor+8<=data.Length){string tag=System.Text.Encoding.ASCII.GetString(data,cursor,4);int length=BitConverter.ToInt32(data,cursor+4);if(tag=="MESP"){
            int cmsp=cursor+16;Case("invalid-part-number",cmsp+0x88,-1);Case("negative-child-count",cmsp+0x90,-1);Case("zero-virtual-count",cmsp+0xb8,0);Case("nan-base-matrix",cmsp+0x30,unchecked((int)0x7fc00000));
            int nested=cmsp+316,end=cursor+8+length;Case("unknown-part-tag",nested,0x5a5a5a5a);Case("nul-part-tag",nested,0);Case("ascii-replacement-part-tag",nested,-1);
            while(nested+8<=end){string inner=System.Text.Encoding.ASCII.GetString(data,nested,4);int size=BitConverter.ToInt32(data,nested+4);if(inner=="VHFM"){Case("bad-frame-map",nested+8,255,1);Case("bad-frame-map-length",nested+4,size+1);}if(inner=="HORI")Case("nan-orientation",nested+8,unchecked((int)0x7fc00000));if(inner=="HPOS")Case("nan-position",nested+8,unchecked((int)0x7fc00000));nested+=8+size;}break;}cursor+=8+length;}
    }
    private static A InflationFixtures()
    {
        A rows = [];
        void Add(string name, byte[] source) {
            D row = new() { ["name"] = name, ["input"] = source };
            try { byte[] value = (byte[])Invoke("InflateAya", source); row["result"] = new D { ["ok"] = true, ["length"] = value.Length, ["sha256"] = Hex(value) }; }
            catch (Exception error) { row["result"] = Failure(error); }
            rows.Add(row);
        }
        static byte[] Compress(byte[] bytes) { using var stream = new MemoryStream(); using(var zip = new ZLibStream(stream, CompressionLevel.SmallestSize, leaveOpen:true)) zip.Write(bytes); return stream.ToArray(); }
        static byte[] Frame(byte[] bytes) => [.. BitConverter.GetBytes(bytes.Length), .. bytes];
        Add("no-records", []); Add("short-header", [1,2,3]); Add("zero-record", [0,0,0,0]); Add("negative-record", [255,255,255,255]); Add("record-too-long", [8,0,0,0,0]);
        byte[] small = Compress([0,1,2,3,255,4,5,6,128,7]);
        Add("empty-zlib", Frame(Compress([]))); Add("valid-zlib", Frame(small));
        Add("two-records", [.. Frame(small), .. Frame(small)]);
        for(int length=1;length<small.Length;length++) Add("truncated-zlib-"+length, Frame(small.AsSpan(0,length).ToArray()));
        foreach(int tail in new[]{1,16,8192-small.Length,8193-small.Length,8192,8193}) Add("trailing-"+tail,Frame([.. small,.. new byte[tail]]));
        Add("concatenated-zlib",Frame([.. small,.. small]));
        byte[] checksum = small.ToArray(); checksum[^1] ^= 1; Add("bad-checksum",Frame(checksum));
        Add("bad-header",Frame([1,2,3,4,5])); Add("limit-exact",Frame(Compress(new byte[2*1024*1024]))); Add("limit-exceeded",Frame(Compress(new byte[2*1024*1024+1])));
        return rows;
    }
    private static void OwnChildren(Node parent,Node root){foreach(Node child in parent.GetChildren()){child.Owner=root;OwnChildren(child,root);}}
    private static D Failure(Exception error)
    {
        D result = new() { ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message.Replace("\0", "\\u0000", StringComparison.Ordinal) };
        if(error.Message.IndexOf('\0') >= 0) result["error_units"] = error.Message.Select(value=>(int)value).ToArray();
        return result;
    }
    private static long Word(float value)=>BitConverter.SingleToUInt32Bits(value);
    private static string Hex(byte[] bytes)=>Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
    private string Owned(string path){string full=Path.GetFullPath(path),owner=Path.GetFullPath(Path.Combine(ProjectSettings.GlobalizePath("res://"),"..","..","local-data"))+Path.DirectorySeparatorChar;Check(full.StartsWith(owner,StringComparison.Ordinal)&&Directory.Exists(Path.GetDirectoryName(full))&&!File.Exists(full),"Fresh worktree-local output required.");return full;}
    private void Check(bool condition,string message){_checks++;if(!condition)throw new InvalidOperationException(message);}
}
