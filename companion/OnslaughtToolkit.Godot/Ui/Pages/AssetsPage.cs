// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's own models, textures and sound effects, read from the player's install: a preview of each, and copies
/// saved as glTF (models), PNG (textures) or WAV (sound effects) into a folder the player chooses. The game is only read; exports never go into the game
/// folder or the backups, and never replace a file.
/// </summary>
internal sealed class AssetsPage : Page
{
    private readonly AppServices _services;
    private readonly Label _empty, _title, _details, _result;
    private readonly SubViewport _viewport;
    private readonly SubViewportContainer _modelView;
    private readonly TextureRect _textureView;
    private readonly Control _texturePanel;
    private readonly Node3D _stage;
    private readonly Camera3D _camera;
    private AssetLibrary? _library;
    private IReadOnlyList<GameAsset> _shown = [];
    private Node? _previewScene;
    private readonly AudioStreamPlayer _player;

    internal AssetsPage(AppServices services) : base("assets", "Art & sound", "models")
    {
        _services = services;
        HBoxContainer layout = Build.Row(16);
        layout.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = layout;

        VBoxContainer left = layout.Add(Build.Column(10));
        left.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        _empty = left.Add(Build.Text("Choose your game folder on Home to see its models and textures.", "Muted"));
        HBoxContainer filters = left.Add(Build.Row(10));
        Kind = filters.Add(new OptionButton { TooltipText = "Show the game's 3D models, its textures or its sound effects" });
        Kind.AddItem("Models", 0);
        Kind.AddItem("Textures", 1);
        Kind.AddItem("Sound effects", 2);
        Kind.ItemSelected += _ => ShowList();
        Search = filters.Add(new LineEdit { PlaceholderText = "Search by name", ClearButtonEnabled = true, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill });
        Search.TextChanged += _ => ShowList();
        List = left.Add(Build.Table("Name", "Group", "Size"));
        List.SetColumnExpandRatio(0, 3);
        List.ItemSelected += () => Select(List.GetSelected());

        (PanelContainer card, VBoxContainer body) = Build.Panel("Card", 8);
        card.CustomMinimumSize = new Vector2(420, 0);
        card.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        card.SizeFlagsVertical = Control.SizeFlags.ShrinkBegin;
        layout.Add(card);
        body.Add(Build.Eyebrow("Preview"));
        _title = body.Add(Build.Text("Nothing selected", "Section"));
        _modelView = body.Add(new SubViewportContainer { Stretch = true, CustomMinimumSize = new Vector2(380, 300), Visible = false });
        _viewport = _modelView.Add(new SubViewport
        {
            OwnWorld3D = true, TransparentBg = false, Msaa3D = Viewport.Msaa.Msaa4X, RenderTargetUpdateMode = SubViewport.UpdateMode.WhenVisible,
        });
        _stage = _viewport.Add(new Node3D());
        _viewport.Add(new WorldEnvironment
        {
            Environment = new Godot.Environment
            {
                BackgroundMode = Godot.Environment.BGMode.Color, BackgroundColor = new Color(0.16f, 0.18f, 0.21f),
                AmbientLightSource = Godot.Environment.AmbientSource.Color, AmbientLightColor = new Color(0.55f, 0.57f, 0.6f),
            },
        });
        DirectionalLight3D sun = _viewport.Add(new DirectionalLight3D { LightEnergy = 1.3f });
        sun.RotationDegrees = new Vector3(-50, 35, 0);
        _camera = _viewport.Add(new Camera3D { Current = true, Fov = 35 });
        // A texture shows over a checkerboard, so transparent parts read as transparent rather than as the card.
        _texturePanel = body.Add(new Control { CustomMinimumSize = new Vector2(380, 300), Visible = false });
        _texturePanel.Add(new TextureRect
        {
            Texture = Checkerboard(), StretchMode = TextureRect.StretchModeEnum.Tile, ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
        }).SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _textureView = _texturePanel.Add(new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize, StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
        });
        _textureView.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        _details = body.Add(Build.Text("", "Muted"));
        HBoxContainer actions = body.Add(Build.Row(10));
        Play = actions.Add(Build.Button("Play", disabled: true));
        Play.Visible = false;
        _player = body.Add(new AudioStreamPlayer { VolumeDb = Mathf.LinearToDb(0.8f) });
        _player.Finished += () => Play.Text = "Play";
        Play.Pressed += () =>
        {
            if (_player.Playing)
            {
                _player.Stop();
                Play.Text = "Play";
            }
            else if (_player.Stream is not null)
            {
                _player.Play();
                Play.Text = "Stop";
            }
        };
        Save = actions.Add(Build.Button("Save a copy…", "Primary", disabled: true));
        Save.TooltipText = "Models are saved as glTF (.glb), which Blender and most 3D tools open; textures as PNG; sound effects as WAV.";
        _result = body.Add(Build.Text("Copies are saved only into a folder you choose, never into your game or backups, and never " +
            "over an existing file.", "Faint"));
        FolderDialog = services.Popups.Add(Build.FilePicker("Choose a folder to save the copy in", FileDialog.FileModeEnum.OpenDir));
        Save.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += folder => SaveCopy(folder);
        services.Game.Changed += Refresh;
    }

    internal override Control Root { get; }
    internal override string Subtitle => _library is null ? "The game's 3D models, textures and sound effects, from your install"
        : $"{Build.Count(_library.Models.Count, "model")} · {Build.Count(_library.Textures.Count, "texture")} · " +
          Build.Count(_library.Sounds.Count, "sound effect");
    internal OptionButton Kind { get; }
    internal LineEdit Search { get; }
    internal Tree List { get; }
    internal Button Save { get; }
    internal Button Play { get; }
    internal short[]? Sound { get; private set; }
    internal FileDialog FolderDialog { get; }
    internal GameAsset? Selected { get; private set; }
    internal CmshMesh? Model { get; private set; }
    internal DdsImage? Texture { get; private set; }
    internal string Result => _result.Text;

    internal override void Refresh()
    {
        if (_services.Game.Busy) return;
        // A listing of two folders is quick, so it is read again each time: the install may have changed.
        GameFolder? folder = _services.Game.Folder;
        _library = folder is null ? null : AssetLibrary.Scan(folder.Root);
        bool any = _library is { } l && l.Models.Count + l.Textures.Count > 0;
        _empty.Text = folder is null ? "Choose your game folder on Home to see its models and textures."
            : "No models or textures were found in your game's data/resources folder.";
        _empty.Visible = !any;
        Kind.Visible = Search.Visible = List.Visible = any;
        ShowList();
        HeaderChanged?.Invoke();
    }

    private void ShowList()
    {
        List.Clear();
        TreeItem root = List.CreateItem();
        if (_library is null) return;
        string search = Search.Text.Trim();
        _shown = (Kind.Selected switch { 1 => _library.Textures, 2 => _library.Sounds, _ => _library.Models })
            .Where(asset => search.Length == 0 || asset.Title.Contains(search, StringComparison.OrdinalIgnoreCase)).ToList();
        for (int i = 0; i < _shown.Count; i++)
            Build.TableRow(List, root, _shown[i].Title, _shown[i].Group, Size(_shown[i].Size)).SetMetadata(0, i);
    }

    /// <summary>Reads the chosen model or texture and shows it. Returns false, with the reason shown, if it cannot be read.</summary>
    internal bool Select(TreeItem? row)
    {
        if (row?.GetMetadata(0).AsInt32() is not int index || index < 0 || index >= _shown.Count) return false;
        return Open(_shown[index]);
    }

    internal bool Open(GameAsset asset)
    {
        Selected = asset;
        Model = null;
        Texture = null;
        Sound = null;
        ClearPreview();
        _title.Text = asset.Title;
        Save.Disabled = true;
        try
        {
            if (asset.Kind == AssetKind.Sound)
            {
                IReadOnlyList<XapSample> samples = XapBank.Read(File.ReadAllBytes(asset.Path));
                if (asset.Index < 0 || asset.Index >= samples.Count) throw new InvalidDataException("the sample is no longer in its bank");
                XapSample sample = samples[asset.Index];
                Sound = XapBank.Decode(sample);
                _details.Text = $"{sample.Seconds:0.00} s · 44,100 Hz mono · {asset.Group} sound bank";
                byte[] pcm = new byte[Sound.Length * 2];
                Buffer.BlockCopy(Sound, 0, pcm, 0, pcm.Length);
                _player.Stream = new AudioStreamWav { Data = pcm, Format = AudioStreamWav.FormatEnum.Format16Bits, MixRate = XapBank.SampleRate, Stereo = false };
                Play.Visible = true;
                Play.Disabled = false;
                Save.Disabled = false;
                Save.Text = "Save as WAV…";
                return true;
            }
            byte[] inflated = AyaContainer.Inflate(File.ReadAllBytes(asset.Path));
            if (asset.Kind == AssetKind.Model)
            {
                IReadOnlyList<CmshMesh> meshes = CmshReader.Read(inflated);
                Model = meshes[0];
                int geometry = Model.Parts.Count(part => part.Positions.Length > 0);
                _details.Text = $"{Build.Count(Model.Parts.Count, "part")}, {geometry} with geometry · " +
                    $"{Build.Count(Model.Textures.Count, "texture")} · {Build.Count(Model.Modes.Count, "animation")}" +
                    (meshes.Count > 1 ? $" · {meshes.Count - 1} more mesh{(meshes.Count > 2 ? "es" : "")} in this file (the first is shown and saved)" : "");
                ShowModel(Model);
            }
            else
            {
                Texture = DdsTexture.Decode(inflated);
                _details.Text = $"{Texture.Width} × {Texture.Height} · {Texture.Format}" +
                    (Texture.MipLevels > 1 ? $" · {Texture.MipLevels} mip levels (the largest is shown and saved)" : "") +
                    (Texture.HasTransparency ? " · has transparency" : "");
                _textureView.Texture = ImageTexture.CreateFromImage(ToImage(Texture));
                _texturePanel.Visible = true;
            }
            Save.Disabled = false;
            Save.Text = asset.Kind == AssetKind.Model ? "Save as glTF…" : "Save as PNG…";
            return true;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException)
        {
            _details.Text = "This file could not be read: " + error.Message;
            _services.Status.Show($"{asset.Title} could not be read; nothing was changed.", StatusKind.Failure);
            return false;
        }
    }

    /// <summary>Saves the selected model or texture into <paramref name="folder"/> as a new file.</summary>
    internal ExportReceipt SaveCopy(string folder)
    {
        if (Selected is null || (Model is null && Texture is null && Sound is null)) return new ExportReceipt(false, "Choose a model, texture or sound first.");
        string stem = string.Concat(Selected.Title.Select(c => char.IsLetterOrDigit(c) || c is '-' or '_' or ' ' ? c : '_')).Trim();
        if (stem.Length == 0) stem = "asset";
        ExportReceipt receipt;
        try
        {
            (byte[] bytes, string extension) = Model is not null ? (GltfExport.Write(Model, LoadTexture, Png), ".glb")
                : Sound is not null ? (XapBank.Wav(Sound), ".wav") : (Png(Texture!), ".png");
            if (Sound is not null) stem += $" ({Selected.Group})";
            receipt = ExportFiles.Write(folder, stem + extension, bytes,
                [_services.Game.Folder?.Root, _services.Backups.Folder]);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException)
        {
            receipt = new ExportReceipt(false, "The copy could not be made: " + error.Message);
        }
        _result.Text = receipt.Ok ? $"Saved {receipt.Path}." : receipt.Message;
        _services.Status.Show(receipt.Ok ? $"Saved a copy of {Selected.Title}." : receipt.Message, receipt.Ok ? StatusKind.Success : StatusKind.Failure);
        return receipt;
    }

    private DdsImage? LoadTexture(string name)
    {
        try
        {
            return _library?.FindTexture(name) is string path ? DdsTexture.Decode(AyaContainer.Inflate(File.ReadAllBytes(path))) : null;
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException)
        {
            return null;
        }
    }

    private void ShowModel(CmshMesh mesh)
    {
        GltfDocument document = new();
        GltfState state = new();
        if (document.AppendFromBuffer(GltfExport.Write(mesh, LoadTexture, Png), "", state) != Error.Ok ||
            document.GenerateScene(state) is not Node3D scene)
            return;
        _previewScene = scene;
        _stage.AddChild(scene);
        Aabb? bounds = null;
        foreach (MeshInstance3D part in scene.FindChildren("*", nameof(MeshInstance3D), true, false).OfType<MeshInstance3D>())
        {
            Aabb box = RelativeTo(part, scene) * part.GetAabb();
            bounds = bounds is Aabb b ? b.Merge(box) : box;
        }
        Aabb frame = bounds ?? new Aabb(-Vector3.One, Vector3.One * 2);
        float size = Mathf.Max(frame.Size.Length(), 0.01f);
        Vector3 centre = frame.GetCenter();
        _camera.Near = size * 0.01f;
        _camera.Far = size * 20f;
        _camera.LookAtFromPosition(centre + new Vector3(0.9f, 0.55f, 1.4f).Normalized() * size * 1.7f, centre, Vector3.Up);
        _modelView.Visible = true;
    }

    /// <summary>A node's transform relative to an ancestor, without needing the tree (the page may not be showing).</summary>
    private static Transform3D RelativeTo(Node3D node, Node3D ancestor)
    {
        Transform3D transform = node.Transform;
        for (Node? parent = node.GetParent(); parent is not null && parent != ancestor; parent = parent.GetParent())
            if (parent is Node3D spatial) transform = spatial.Transform * transform;
        return ancestor.Transform * transform;
    }

    private void ClearPreview()
    {
        _player.Stop();
        _player.Stream = null;
        Play.Text = "Play";
        Play.Visible = false;
        _previewScene?.QueueFree();
        _previewScene = null;
        _modelView.Visible = false;
        _texturePanel.Visible = false;
        _textureView.Texture = null;
    }

    /// <summary>The name of the first texture the open model uses, as the texture list shows it, or null.</summary>
    internal string? ModelTextureTitle() =>
        Model?.Textures.Select(t => _library?.FindTexture(t.Name)).OfType<string>().Select(path => AssetLibrary.TextureTitle(Path.GetFileName(path))).FirstOrDefault();

    private static ImageTexture Checkerboard()
    {
        Image image = Image.CreateEmpty(16, 16, false, Image.Format.Rgba8);
        for (int y = 0; y < 16; y++)
            for (int x = 0; x < 16; x++)
                image.SetPixel(x, y, (x < 8) == (y < 8) ? new Color(0.30f, 0.32f, 0.35f) : new Color(0.22f, 0.24f, 0.27f));
        return ImageTexture.CreateFromImage(image);
    }

    private static Image ToImage(DdsImage image) => Image.CreateFromData(image.Width, image.Height, false, Image.Format.Rgba8, image.Rgba);

    private static byte[] Png(DdsImage image) => ToImage(image).SavePngToBuffer();

    private static string Size(long bytes) => bytes >= 1024 * 1024 ? $"{bytes / 1048576.0:0.0} MB" : $"{Math.Max(1, bytes / 1024)} KB";
}
