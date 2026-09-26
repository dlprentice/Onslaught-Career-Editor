// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Media;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Lists audio, video and image files in a chosen folder by name and size. Nothing is played or changed.</summary>
internal sealed class MediaPage
{
    private readonly StatusLine _status;
    private readonly Dictionary<string, MediaItem> _items = [];
    private MediaCatalog? _catalog;
    private TreeItem? _treeRoot;
    private string _folder = "";

    internal MediaPage(StatusLine status, Node popups)
    {
        _status = status;
        Root = Build.Column(12);
        Root.Name = "Media";
        Root.Add(Build.Text("Browse local media", CompanionTheme.PageHeadingSize));
        Root.Add(Build.Text("Choose your game or media folder to inspect its audio, video and image filenames, sizes and " +
            "locations. This browser lists metadata only; it does not play, decode, import or change the files."));
        HBoxContainer actions = Root.Add(Build.Row(12));
        ChooseFolder = actions.Add(Build.Button("Choose media folder…"));
        Rescan = actions.Add(Build.Button("Rescan", disabled: true));
        CancelScan = actions.Add(Build.Button("Cancel scan", disabled: true));
        FolderPath = Root.Add(new LineEdit
        {
            Editable = false, PlaceholderText = "No folder selected",
            TooltipText = "The folder you explicitly selected. Files remain in place.",
        });
        ScanSummary = Root.Add(Build.Text("Choose a folder to begin. Linked files and folders are skipped."));
        Files = Root.Add(Build.Table("Filename", "Kind", "Format", "Bytes", "Relative path"));
        Files.CustomMinimumSize = new Vector2(0, 240);
        int[] widths = [190, 120, 95, 90, 220];
        for (int column = 0; column < widths.Length; column++) Files.SetColumnCustomMinimumWidth(column, widths[column]);
        Files.SetColumnExpand(3, false);
        FileDetails = Root.Add(Build.Detail("Select a file to inspect its relative path and reported format. Formats are " +
            "identified by filename extension; their contents have not been validated.", 108));
        Root.Add(Build.Text("Each scan covers up to 8 folder levels, 5,000 media files and 30,000 entries. A cancelled or " +
            "limited scan is labelled as a partial list.", CompanionTheme.NoteSize));
        FolderDialog = popups.Add(Build.FilePicker("Choose a local media folder", FileDialog.FileModeEnum.OpenDir));

        ChooseFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += path => _status.Track(BrowseAsync(path));
        Rescan.Pressed += () => _status.Track(BrowseAsync(_folder));
        CancelScan.Pressed += Cancel;
        Files.ItemSelected += ShowSelection;
    }

    internal VBoxContainer Root { get; }
    internal Button ChooseFolder { get; }
    internal Button Rescan { get; }
    internal Button CancelScan { get; }
    internal LineEdit FolderPath { get; }
    internal Label ScanSummary { get; }
    internal Tree Files { get; }
    internal RichTextLabel FileDetails { get; }
    internal FileDialog FolderDialog { get; }
    internal bool Busy { get; private set; }

    internal async Task<MediaScan> BrowseAsync(string path)
    {
        if (Busy) return new MediaCatalog().Result() with { Message = "A media scan is already running." };
        Busy = true;
        MediaCatalog catalog = _catalog = new MediaCatalog();
        Files.Clear();
        _items.Clear();
        _treeRoot = Files.CreateItem();
        FileDetails.Text = "Select a file to inspect its metadata. Files are identified by extension; contents are not decoded or validated.";
        MediaScan progress = catalog.Begin(path);
        _folder = progress.Root;
        FolderPath.Text = _folder;
        UpdateActions();
        ScanSummary.Text = progress.Message;
        while (!catalog.Done)
        {
            progress = catalog.Step(64);
            foreach (MediaItem item in progress.Items) Append(item);
            ScanSummary.Text = progress.Message;
            await Root.ToSignal(Root.GetTree(), SceneTree.SignalName.ProcessFrame);
            if (!Root.IsInsideTree())
            {
                catalog.Cancel();
                return catalog.Result();
            }
        }
        MediaScan final = catalog.Result();
        ScanSummary.Text = final.Message;
        if (final.IssueCount > 0) FileDetails.Text = "Some entries could not be listed:\n" + string.Join("\n", final.Issues);
        Busy = false;
        UpdateActions();
        return final;
    }

    internal void Cancel()
    {
        _catalog?.Cancel();
        CancelScan.Disabled = true;
    }

    private void Append(MediaItem item)
    {
        TreeItem row = Build.TableRow(Files, _treeRoot, item.Name, item.Kind, item.Format,
            item.Size >= 0 ? item.Size.ToString("N0") : "Unknown", item.RelativePath);
        row.SetMetadata(0, item.RelativePath);
        _items[item.RelativePath] = item;
        row.SetTooltipText(2, "Filename extension only; contents have not been validated.");
    }

    private void ShowSelection()
    {
        if (Files.GetSelected() is not TreeItem selected) return;
        if (!_items.TryGetValue(selected.GetMetadata(0).AsString(), out MediaItem? item)) return;
        string size = item.Size >= 0 ? $"{item.Size:N0} bytes" : "Size unavailable";
        FileDetails.Text = $"{item.Name}\n{item.Kind}  •  {item.Format}  •  {size}\n{item.RelativePath}\n" +
            "Metadata only. The extension names a possible format; no playback or content validation is implied.";
    }

    private void UpdateActions()
    {
        ChooseFolder.Disabled = Busy;
        Rescan.Disabled = Busy || _folder.Length == 0;
        CancelScan.Disabled = !Busy;
    }
}
