// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Byte-for-byte comparison of the open original with another career. Neither file changes.</summary>
internal sealed class ComparePage
{
    private readonly CareerWorkspace _workspace;
    private readonly StatusLine _status;

    internal ComparePage(CareerWorkspace workspace, StatusLine status, Node popups)
    {
        (_workspace, _status) = (workspace, status);
        Root = Build.Column(12);
        Root.Name = "Compare copies";
        Root.Add(Build.Text("Compare another supported career with your opened original. Every differing byte is " +
            "included, even when its meaning is unknown. Neither file is modified."));
        CompareButton = Root.Add(Build.Button("Choose comparison career…", disabled: true));
        Summary = Root.Add(Build.Detail("Open an original, then choose the copy you want to compare.", 110));
        Tree = Root.Add(Build.Table("File offset", "Original byte", "Comparison byte"));
        Tree.SetColumnCustomMinimumWidth(0, 150);
        Dialog = popups.Add(Build.FilePicker("Compare another career", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career saves"));
        CompareButton.Pressed += () => Dialog.PopupCenteredRatio(0.75f);
        Dialog.FileSelected += path => _status.Track(CompareAsync(path));
    }

    internal VBoxContainer Root { get; }
    internal Button CompareButton { get; }
    internal RichTextLabel Summary { get; }
    internal Tree Tree { get; }
    internal FileDialog Dialog { get; }

    internal void Reset()
    {
        Tree.Clear();
        Summary.Text = "Choose another career to compare with this original.";
    }

    internal void UpdateActions() => CompareButton.Disabled = _workspace.Session is null || _workspace.Busy;

    internal async Task<Outcome<CareerComparison>> CompareAsync(string path)
    {
        if (_workspace.Busy || _workspace.Session is not SaveSession original)
            return Outcome<CareerComparison>.Refusal("Open an original first.");
        _status.Show("Opening the comparison career…");
        Outcome<CareerComparison> result = await _workspace.CompareAsync(path);
        if (result.Value is not CareerComparison comparison)
        {
            _status.Show(result.Message, failed: true);
            return result;
        }
        ByteComparison bytes = comparison.Bytes;
        Summary.Text = $"{comparison.Other.Path}\nSHA-256  {comparison.Other.Sha256}\n" +
            (bytes.Equal ? "Byte-for-byte identical." : $"{bytes.ChangedBytes:N0} differing bytes.") +
            $"\nCompared with the original snapshot: {original.Sha256}";
        Tree.Clear();
        TreeItem root = Tree.CreateItem();
        foreach (ByteChange change in bytes.Changes)
            Build.TableRow(Tree, root, $"0x{change.Offset:X4}", Hex(change.Before), Hex(change.After));
        _status.Show(result.Message);
        return result;
    }

    private static string Hex(int value) => value == ByteComparison.MissingByte ? "absent" : $"{value:X2}";
}
