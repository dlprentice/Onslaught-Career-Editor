// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Media;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>
/// The game's own soundtrack and voice lines, played from the player's install with Godot's built-in
/// Ogg Vorbis decoder, with transcripts from the game's text. Files are only read; nothing is bundled.
/// </summary>
internal sealed class MusicPage : Page
{
    private readonly GameLibrary _game;
    private readonly StatusLine _status;
    private readonly Label _empty, _title, _detail, _time;
    private readonly RichTextLabel _transcript;
    private readonly HSlider _position, _volume;
    private readonly AudioStreamPlayer _player;
    private IReadOnlyList<GameAudioItem> _items = [];
    private GameAudioItem? _loaded;
    private bool _seeking;

    internal MusicPage(GameLibrary game, StatusLine status) : base("music", "Music & voices")
    {
        (_game, _status) = (game, status);
        HBoxContainer layout = Build.Row(16);
        layout.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = layout;

        VBoxContainer left = layout.Add(Build.Column(10));
        left.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        left.SizeFlagsStretchRatio = 1.5f;
        _empty = left.Add(Build.Text("Choose your game folder on Home to list its music and voice lines.", "Muted"));
        Search = left.Add(new LineEdit { PlaceholderText = "Search titles and transcripts", ClearButtonEnabled = true });
        Search.TextChanged += _ => ShowList();
        List = left.Add(Build.Table("Title", "Transcript"));
        List.SetColumnExpandRatio(1, 2);
        List.ItemActivated += () => Play(List.GetSelected());
        List.ItemSelected += () => Select(List.GetSelected());

        (PanelContainer nowPlaying, VBoxContainer body) = Build.Panel("Card", 8);
        nowPlaying.CustomMinimumSize = new Vector2(360, 0);
        nowPlaying.SizeFlagsHorizontal = Control.SizeFlags.ExpandFill;
        nowPlaying.SizeFlagsVertical = Control.SizeFlags.ShrinkBegin;
        layout.Add(nowPlaying);
        body.Add(Build.Eyebrow("Now playing"));
        _title = body.Add(Build.Text("Nothing selected", "Section"));
        _detail = body.Add(Build.Text("", "Muted"));
        _transcript = body.Add(Build.Detail(""));
        HBoxContainer transport = body.Add(Build.Row(10));
        PlayPause = transport.Add(Build.Button("Play", "Primary", disabled: true));
        Stop = transport.Add(Build.Button("Stop", disabled: true));
        _time = transport.Add(Build.Text("0:00 / 0:00", "Mono", wrap: false));
        _position = body.Add(new HSlider { MinValue = 0, MaxValue = 1, Step = 0.01, Editable = false });
        HBoxContainer volumeRow = body.Add(Build.Row(10));
        volumeRow.Add(Build.Text("Volume", "Muted", wrap: false, width: 70));
        _volume = volumeRow.Add(new HSlider { MinValue = 0, MaxValue = 100, Step = 1, Value = 80, SizeFlagsHorizontal = Control.SizeFlags.ExpandFill });
        body.Add(Build.Text("Cutscenes are Bink video, which this app cannot decode; they are listed for reference only.", "Faint"));

        _player = layout.Add(new AudioStreamPlayer { VolumeDb = Mathf.LinearToDb(0.8f) });
        _player.Finished += () => PlayPause.Text = "Play";
        PlayPause.Pressed += TogglePlay;
        Stop.Pressed += () =>
        {
            _player.Stop();
            PlayPause.Text = "Play";
        };
        _volume.ValueChanged += value => _player.VolumeDb = Mathf.LinearToDb((float)(value / 100));
        _position.DragStarted += () => _seeking = true;
        _position.DragEnded += _ =>
        {
            _seeking = false;
            if (_player.Stream is not null) _player.Seek((float)_position.Value);
        };
        _game.Changed += Refresh;
    }

    internal override Control Root { get; }
    internal override string Subtitle => _items.Count == 0 ? "The game's soundtrack and voice lines, from your install"
        : $"{Build.Count(_items.Count(item => item.Kind == AudioKind.Music), "track")} · " +
          Build.Count(_items.Count(item => item.Kind == AudioKind.Voice), "voice line");
    internal LineEdit Search { get; }
    internal Tree List { get; }
    internal Button PlayPause { get; }
    internal Button Stop { get; }
    internal AudioStreamPlayer Player => _player;
    internal IReadOnlyList<GameAudioItem> Items => _items;
    internal GameAudioItem? Loaded => _loaded;

    internal override void Refresh()
    {
        if (_game.Busy) return;
        _items = _game.Folder is GameFolder folder ? GameAudio.Catalog(folder, _game.Text) : [];
        _empty.Visible = _items.Count == 0;
        Search.Visible = List.Visible = _items.Count > 0;
        ShowList();
    }

    /// <summary>Loads an item into the player; refuses unplayable or damaged files without touching the engine's decoder.</summary>
    internal bool Load(GameAudioItem item)
    {
        _player.Stop();
        _player.StreamPaused = false;
        PlayPause.Text = "Play";
        _loaded = item;
        _title.Text = item.Title;
        _detail.Text = item.Group;
        _transcript.Text = item.Transcript ?? (item.Kind == AudioKind.Voice ? "No transcript in the game's text for this line." : "");
        if (!item.Playable || !GameAudio.LooksLikeOggVorbis(item.Path))
        {
            _player.Stream = null;
            PlayPause.Disabled = Stop.Disabled = true;
            _position.Editable = false;
            _status.Show(item.Playable ? $"{Path.GetFileName(item.Path)} is not a playable Ogg Vorbis file." :
                "Cutscenes are Bink video; they cannot be played here.", item.Playable ? StatusKind.Failure : StatusKind.Info);
            return false;
        }
        AudioStreamOggVorbis? stream = AudioStreamOggVorbis.LoadFromFile(item.Path);
        _player.Stream = stream;
        bool ok = stream is not null;
        PlayPause.Disabled = Stop.Disabled = !ok;
        _position.Editable = ok;
        _position.MaxValue = ok ? Math.Max(0.01, stream!.GetLength()) : 1;
        _position.Value = 0;
        UpdateTime();
        return ok;
    }

    internal void Play(TreeItem? row)
    {
        if (row?.GetMetadata(0).AsInt32() is int index && index >= 0 && index < _items.Count && Load(_items[index]))
        {
            _player.Play();
            PlayPause.Text = "Pause";
        }
    }

    /// <summary>Advances the position display; the shell calls this every frame while the page is visible.</summary>
    internal void Tick()
    {
        if (_player.Stream is null || _seeking) return;
        if (_player.Playing) _position.SetValueNoSignal(_player.GetPlaybackPosition());
        UpdateTime();
    }

    private void Select(TreeItem? row)
    {
        if (row?.GetMetadata(0).AsInt32() is int index && index >= 0 && index < _items.Count) Load(_items[index]);
    }

    private void TogglePlay()
    {
        if (_player.Stream is null) return;
        if (_player.Playing)
        {
            _player.StreamPaused = !_player.StreamPaused;
            PlayPause.Text = _player.StreamPaused ? "Play" : "Pause";
        }
        else
        {
            _player.StreamPaused = false;
            _player.Play((float)_position.Value);
            PlayPause.Text = "Pause";
        }
    }

    private void UpdateTime()
    {
        double length = _player.Stream?.GetLength() ?? 0;
        _time.Text = $"{Clock(_position.Value)} / {Clock(length)}";
    }

    private static string Clock(double seconds) => $"{(int)seconds / 60}:{(int)seconds % 60:00}";

    private void ShowList()
    {
        List.Clear();
        TreeItem root = List.CreateItem();
        string query = Search.Text.Trim();
        Dictionary<string, TreeItem> groups = [];
        for (int index = 0; index < _items.Count; index++)
        {
            GameAudioItem item = _items[index];
            if (query.Length > 0 && !item.Title.Contains(query, StringComparison.OrdinalIgnoreCase) &&
                !(item.Transcript?.Contains(query, StringComparison.OrdinalIgnoreCase) ?? false) &&
                !item.Group.Contains(query, StringComparison.OrdinalIgnoreCase))
                continue;
            if (!groups.TryGetValue(item.Group, out TreeItem? group))
            {
                group = Build.TableRow(List, root, item.Group, "");
                group.SetMetadata(0, -1);
                group.SetSelectable(0, false);
                group.SetSelectable(1, false);
                group.SetCustomColor(0, Palette.Accent);
                group.Collapsed = item.Kind == AudioKind.Voice && query.Length == 0;
                groups[item.Group] = group;
            }
            TreeItem row = Build.TableRow(List, group, item.Title, item.Transcript ?? "");
            row.SetMetadata(0, index);
            if (!item.Playable) row.SetCustomColor(0, Palette.Faint);
        }
    }
}
