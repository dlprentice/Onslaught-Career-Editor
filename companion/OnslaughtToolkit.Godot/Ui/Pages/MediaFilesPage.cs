// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Media;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Lists audio, video and image files in a chosen folder by name and size. Nothing is played or changed.</summary>
internal sealed class MediaFilesPage : Page
{
    private readonly StatusLine _status;
    private readonly Dictionary<string, MediaItem> _items = [];
    private MediaCatalog? _catalog;
    private TreeItem? _treeRoot;
    private string _folder = "";

    internal MediaFilesPage(StatusLine status, Node popups) : base("media", "Media files")
    {
        _status = status;
        VBoxContainer column = Build.Column(14);
        column.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = column;
        column.Add(Build.Notice("Lists the audio, video and image files in any folder you choose, by name, format and size. " +
            "Formats come from file extensions; nothing is opened, decoded or changed.").Panel);
        HBoxContainer actions = column.Add(Build.Row(12));
        ChooseFolder = actions.Add(Build.Button("Choose a folder…", "Primary"));
        Rescan = actions.Add(Build.Button("Rescan", disabled: true));
        CancelScan = actions.Add(Build.Button("Cancel scan", disabled: true));
        FolderPath = column.Add(new LineEdit
        {
            Editable = false, PlaceholderText = "No folder selected", ThemeTypeVariation = "MonoField",
            TooltipText = "The folder you chose. Files stay where they are.",
        });
        ScanSummary = column.Add(Build.Text("Linked files and folders are skipped. A scan covers 8 folder levels, 5,000 media " +
            "files and 30,000 entries; a cancelled or limited scan says it is partial.", "Muted"));
        Files = column.Add(Build.Table("File", "Kind", "Format", "Bytes", "Folder"));
        Files.CustomMinimumSize = new Vector2(0, 240);
        int[] widths = [200, 120, 100, 90, 220];
        for (int index = 0; index < widths.Length; index++) Files.SetColumnCustomMinimumWidth(index, widths[index]);
        Files.SetColumnExpand(3, false);
        (PanelContainer detailPanel, VBoxContainer detailBody) = Build.Panel("Inset", 4);
        FileDetails = detailBody.Add(Build.Detail("Select a file to see its details."));
        column.Add(detailPanel);
        FolderDialog = popups.Add(Build.FilePicker("Choose a local media folder", FileDialog.FileModeEnum.OpenDir));

        ChooseFolder.Pressed += () => FolderDialog.PopupCenteredRatio(0.75f);
        FolderDialog.DirSelected += path => _status.Track(BrowseAsync(path));
        Rescan.Pressed += () => _status.Track(BrowseAsync(_folder));
        CancelScan.Pressed += Cancel;
        Files.ItemSelected += ShowSelection;
    }

    internal override Control Root { get; }
    internal override string Subtitle => "An inventory of any folder's audio, video and images";
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
        FileDetails.Text = "Select a file to see its details.";
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
        _status.Show(final.Message, final.Ok ? StatusKind.Info : StatusKind.Failure);
        return final;
    }

    internal void Cancel()
    {
        _catalog?.Cancel();
        CancelScan.Disabled = true;
    }

    private void Append(MediaItem item)
    {
        string folder = System.IO.Path.GetDirectoryName(item.RelativePath)?.Replace('\\', '/') ?? "";
        TreeItem row = Build.TableRow(Files, _treeRoot, item.Name, item.Kind, item.Format,
            item.Size >= 0 ? item.Size.ToString("N0") : "Unknown", folder.Length == 0 ? "." : folder);
        row.SetMetadata(0, item.RelativePath);
        _items[item.RelativePath] = item;
    }

    private void ShowSelection()
    {
        if (Files.GetSelected() is not TreeItem selected) return;
        if (!_items.TryGetValue(selected.GetMetadata(0).AsString(), out MediaItem? item)) return;
        string size = item.Size >= 0 ? $"{item.Size:N0} bytes" : "size unavailable";
        FileDetails.Text = $"{item.RelativePath}\n{item.Kind} · {item.Format} · {size}\n" +
            "The extension names a possible format; the contents were not opened or validated.";
    }

    private void UpdateActions()
    {
        ChooseFolder.Disabled = Busy;
        Rescan.Disabled = Busy || _folder.Length == 0;
        CancelScan.Disabled = !Busy;
    }
}
