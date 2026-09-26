// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>Byte-for-byte comparison of the open original with another career. Neither file changes.</summary>
internal sealed class ComparePage : Page
{
    private readonly CareerWorkspace _workspace;
    private readonly StatusLine _status;

    internal ComparePage(CareerWorkspace workspace, StatusLine status, Node popups) : base("compare", "Compare")
    {
        (_workspace, _status) = (workspace, status);
        VBoxContainer column = Build.Column(14);
        column.SizeFlagsVertical = Control.SizeFlags.ExpandFill;
        Root = column;
        column.Add(Build.Notice("Opens another career read-only and lists every byte that differs from your open original, " +
            "including bytes whose meaning is unknown. Neither file is changed.").Panel);
        HBoxContainer actions = column.Add(Build.Row(12));
        CompareButton = actions.Add(Build.Button("Choose a career to compare…", "Primary", disabled: true));
        (PanelContainer summaryPanel, VBoxContainer summaryBody) = Build.Panel("Inset", 4);
        Summary = summaryBody.Add(Build.Detail("Open an original first, then choose the career to compare with it.", bbcode: true));
        column.Add(summaryPanel);
        Tree = column.Add(Build.Table("Offset", "Region", "Original", "Other"));
        Tree.SetColumnCustomMinimumWidth(0, 110);
        Tree.SetColumnCustomMinimumWidth(1, 220);
        Dialog = popups.Add(Build.FilePicker("Compare another career", FileDialog.FileModeEnum.OpenFile, "*.bes ; Career saves"));
        CompareButton.Pressed += () => Dialog.PopupCenteredRatio(0.75f);
        Dialog.FileSelected += path => _status.Track(CompareAsync(path));
    }

    internal override Control Root { get; }
    internal override string Subtitle => "Every differing byte between two careers, read-only";
    internal Button CompareButton { get; }
    internal RichTextLabel Summary { get; }
    internal Tree Tree { get; }
    internal FileDialog Dialog { get; }

    internal void Reset()
    {
        Tree.Clear();
        Summary.Text = "Choose another career to compare with this original.";
    }

    internal override void Refresh() => CompareButton.Disabled = _workspace.Session is null || _workspace.Busy;

    internal async Task<Outcome<CareerComparison>> CompareAsync(string path)
    {
        if (_workspace.Busy || _workspace.Session is not SaveSession original)
            return Outcome<CareerComparison>.Refusal("Open an original first.");
        _status.Show("Opening the comparison career…");
        Outcome<CareerComparison> result = await _workspace.CompareAsync(path);
        if (result.Value is not CareerComparison comparison)
        {
            _status.Show(result.Message, StatusKind.Failure);
            return result;
        }
        ByteComparison bytes = comparison.Bytes;
        string verdict = bytes.Equal ? "[color=#" + Palette.Good.ToHtml(false) + "]Byte-for-byte identical.[/color]"
            : $"[color=#{Palette.Data.ToHtml(false)}]{bytes.ChangedBytes:N0} differing bytes[/color] in " +
              string.Join(", ", bytes.Regions.Select(region => $"{region.Key} ({region.Value})")) + ".";
        Summary.Text = $"[b]{comparison.Other.Path.Replace("[", "[lb]")}[/b]\n{verdict}\n" +
            $"[code]other    {comparison.Other.Sha256}\noriginal {original.Sha256}[/code]";
        Tree.Clear();
        TreeItem root = Tree.CreateItem();
        foreach (ByteChange change in bytes.Changes)
            Build.TableRow(Tree, root, $"0x{change.Offset:X4}", CareerSave.RegionOf(change.Offset), Hex(change.Before), Hex(change.After));
        _status.Show(result.Message, StatusKind.Success);
        return result;
    }

    private static string Hex(int value) => value == ByteComparison.MissingByte ? "absent" : $"{value:X2}";
}
