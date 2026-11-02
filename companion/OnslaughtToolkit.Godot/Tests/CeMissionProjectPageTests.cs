// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Missions;
using OnslaughtToolkit.Companion.Ui;
using Position = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>The production project page with authored objects/source only. It discovers no installation or profile.</summary>
internal static class CeMissionProjectPageTests
{
    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("authored mission project page");
        await Frames(tree, 1);
        SubViewport viewport = new() { Size = new Vector2I(1280, 900), GuiEmbedSubwindows = true };
        tree.Root.AddChild(viewport);
        Control popups = new();
        viewport.AddChild(popups);
        StatusLine status = new();
        Action? discard = null;
        Theme theme = CompanionTheme.Build();
        CeMissionProjectPage page = new(status, popups, (_, _, then) => discard = then);
        page.Root.Theme = theme;
        viewport.AddChild(page.Root);
        page.Root.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        viewport.AddChild(status.Root);
        status.Root.Visible = false;
        try
        {
            await Frames(tree, 3);
            check.That(page.Editor.Current.Placements.Count == 0 && !page.HasUnsavedChanges,
                "a standalone project starts without a game, career, catalogue or retail world");
            Text(page.ObjectName, "Beacon"); Text(page.Definition, "authored.beacon"); Press(page.AddObject);
            string beacon = page.Editor.Current.Placements.Single().Id;
            Text(page.ObjectName, "Escort"); Text(page.Definition, "authored.escort"); Press(page.AddObject);
            string escort = page.Editor.Current.Placements.Single(item => item.Name == "Escort").Id;
            SelectObject(page, beacon);
            Text(page.Z, "-7.25"); Press(page.Apply);
            Text(page.SourceName, "Arrival"); Press(page.AddSource);
            string arrival = page.Editor.Current.Scripts.Single().Id;
            const string authored = "// Authored mission source\n// Arrival Ω\tkeeps its text.\n";
            Source(page, authored); Text(page.ProjectName, "Escort exercise"); Press(page.Apply);
            Press(page.Bind); page.EntrySource.ButtonPressed = true;
            check.That(page.Editor.Current.Placements.Count == 2 && page.Editor.Current.Placement(beacon).Definition == "authored.beacon" &&
                page.Editor.Current.Placement(beacon).ScriptId == arrival && page.Editor.Current.EntryScriptId == arrival &&
                page.Editor.Current.Script(arrival).Text == authored && page.Editor.Current.Name == "Escort exercise",
                "page controls create stable objects, preserve mission source, attach it and choose the entry source");

            Text(page.SourceName, "Departure"); Press(page.AddSource);
            string departure = page.Editor.Current.Scripts.Single(item => item.Name == "Departure").Id;
            SelectSource(page, arrival);
            Text(page.X, "invalid"); Source(page, "// pending arrival\n");
            long beforeInvalid = page.Editor.Revision;
            SelectObject(page, escort); SelectObject(page, beacon);
            SelectSource(page, departure); SelectSource(page, arrival);
            check.That(page.X.Text == "invalid" && page.Source.Text == "// pending arrival\n" && page.Undo.Disabled && page.AddObject.Disabled,
                "coordinate and source drafts follow stable selections and block history-changing controls");
            check.That(!page.ApplyDrafts() && page.Editor.Revision == beforeInvalid && page.Editor.Current.Script(arrival).Text == authored,
                "one invalid field keeps every draft and changes no part of the document");
            Text(page.X, "36"); Press(page.Apply);
            check.That(page.Editor.Revision == beforeInvalid + 1 && page.Editor.Current.Placement(beacon).Position.X == 36 &&
                page.Editor.Current.Script(arrival).Text == "// pending arrival\n" && page.Undo.Disabled == false,
                "valid inspector and source drafts apply as one undoable change");
            Press(page.Undo);
            check.That(page.Editor.Current.Script(arrival).Text == authored && page.Editor.Current.Placement(beacon).Position.X == 32,
                "one page Undo restores the source and placement together");
            Press(page.Redo);
            await Frames(tree, 3);

            LevelTerrainViewport view = page.View;
            Camera3D camera = view.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
            int row = Index(page, beacon);
            bool projected = view.TryGetMarkerPoint(row, out Vector2 start);
            Vector2 target = camera.UnprojectPosition(new Vector3(82, 0, -91));
            check.That(projected && new Rect2(Vector2.Zero, view.Size).HasPoint(start) && new Rect2(Vector2.Zero, view.Size).HasPoint(target),
                "the authored mark and destination lie inside the real 3D page viewport");
            Position before = page.Editor.Current.Placement(beacon).Position;
            long revision = page.Editor.Revision;
            Vector3 cameraBefore = camera.GlobalPosition;
            Pointer(view, start, start, false); Button(view, start, true); Pointer(view, start, target, true);
            check.That(page.Editor.Revision == revision && page.Editor.Current.Placement(beacon).Position == before && camera.GlobalPosition == cameraBefore,
                "3D drag preview changes neither the document, undo history nor camera");
            Button(view, target, false);
            Position moved = page.Editor.Current.Placement(beacon).Position;
            check.That(page.Editor.Revision == revision + 1 && Math.Abs(moved.X - 82) < 0.03f && Math.Abs(moved.Y - 91) < 0.03f &&
                BitConverter.SingleToInt32Bits(moved.Z) == BitConverter.SingleToInt32Bits(before.Z),
                "pointer release makes one XY placement edit and preserves the object's authored Z");
            Press(page.Undo);
            check.That(page.Editor.Current.Placement(beacon).Position == before, "one Undo restores the complete 3D drop");
            Press(page.Redo);
            await Frames(tree);
            view.TryGetMarkerPoint(row, out start);
            Button(view, start, true); Pointer(view, start, target + new Vector2(20, 0), true);
            viewport.PushInput(new InputEventKey { Keycode = Key.Escape, Pressed = true }, true);
            Button(view, target + new Vector2(20, 0), false);
            check.That(page.Editor.Current.Placement(beacon).Position == moved, "Escape cancels an authored-object drag without an edit");

            string root = Path.Combine(output, "ce-project-page");
            Directory.CreateDirectory(root);
            string path = Path.Combine(root, "escort.ceproject");
            byte[] expected = CeMissionProjectJson.Write(page.Editor.Current);
            check.That(await page.SaveFileAsync(path) && !page.HasUnsavedChanges && File.ReadAllBytes(path).AsSpan().SequenceEqual(expected),
                "Save as publishes and verifies the placements and source together");
            Text(page.ProjectName, "Unsaved name");
            check.That(!await page.OpenFileAsync(path) && page.ProjectName.Text == "Unsaved name",
                "opening another document requires confirmation before dropping pending fields");
            Press(page.NewProject);
            check.That(discard is not null && page.ProjectName.Text == "Unsaved name", "New waits for the page's discard confirmation");
            discard?.Invoke();
            check.That(page.Editor.Current.Placements.Count == 0 && !page.HasUnsavedChanges, "confirmed New starts a clean authored project");
            check.That(await page.OpenFileAsync(path) && CeMissionProjectJson.Write(page.Editor.Current).AsSpan().SequenceEqual(expected) && !page.Editor.CanUndo,
                "Open restores stable IDs, 3D placements, links and source with a fresh undo history");
            string invalidPath = Path.Combine(root, "invalid.ceproject");
            File.WriteAllText(invalidPath, "invalid project");
            CeMissionProject current = page.Editor.Current;
            check.That(!await page.OpenFileAsync(invalidPath) && ReferenceEquals(page.Editor.Current, current),
                "a malformed project keeps the current document intact");

            await Frames(tree);
            row = Index(page, beacon);
            view.TryGetMarkerPoint(row, out start);
            Button(view, start, true); Pointer(view, start, target, true);
            CeMissionProject replacement = CeMissionProject.Empty("replacement", "Replacement");
            page.OpenDocument(replacement);
            Button(view, target, false);
            check.That(ReferenceEquals(page.Editor.Current, replacement) && !page.Editor.CanUndo,
                "opening a document invalidates an in-flight drag before the next frame");
            CeMissionProject untouched = CeMissionProjectTests.Authored();
            page.OpenDocument(untouched);
            string uneditedPath = Path.Combine(root, "unedited-source.ceproject");
            check.That(await page.SaveFileAsync(uneditedPath) && File.ReadAllBytes(uneditedPath).AsSpan().SequenceEqual(CeMissionProjectJson.Write(untouched)),
                "displaying and saving untouched source preserves its stored CRLF, tabs and Unicode exactly");
            page.OpenDocument(new("extended", "Extended coordinates",
                [new("far", "Far marker", "authored.marker", new(800, -200, -800)), new("near", "Near marker", "authored.marker", Position.Zero)], []));
            await Frames(tree, 3);
            check.That(view.TryGetMarkerPoint(0, out _) && view.TryGetMarkerPoint(1, out _),
                "Frame all includes authored Z as well as both horizontal axes");
            target = camera.UnprojectPosition(new Vector3(820, 0, 180));
            Vector2 drop = view.GlobalPosition + target;
            viewport.PushInput(new InputEventMouseButton { Position = drop, GlobalPosition = drop, ButtonIndex = MouseButton.Right, Pressed = true }, true);
            viewport.PushInput(new InputEventMouseButton { Position = drop, GlobalPosition = drop, ButtonIndex = MouseButton.Right, Pressed = false }, true);
            Position extended = page.Editor.Current.Placement("far").Position;
            check.That(Math.Abs(extended.X - 820) < 0.03f && Math.Abs(extended.Y + 180) < 0.03f && extended.Z == -800,
                "authored 3D placement supports negative coordinates and coordinates beyond the retail heightfield");
            view.UseAuthoredSurface = false;
            revision = page.Editor.Revision;
            viewport.PushInput(new InputEventMouseButton { Position = drop, GlobalPosition = drop, ButtonIndex = MouseButton.Right, Pressed = true }, true);
            await Frames(tree);
            check.That(!view.TryGetMarkerPoint(0, out _) && page.Editor.Revision == revision,
                "a preview surface without terrain stays inactive unless the host explicitly opts into authored placement");
        }
        finally { viewport.QueueFree(); await Frames(tree); }
        await DelayedIo(tree, output, check);
    }

    private static async Task DelayedIo(SceneTree tree, string output, Checks check)
    {
        SubViewport viewport = new() { Size = new Vector2I(1000, 800), GuiEmbedSubwindows = true };
        tree.Root.AddChild(viewport);
        Control popups = new(); viewport.AddChild(popups);
        StatusLine status = new(); viewport.AddChild(status.Root); status.Root.Visible = false;
        DelayedFiles files = new();
        CeMissionProjectPage page = new(status, popups, (_, _, _) => { }, files: files);
        viewport.AddChild(page.Root); page.Root.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.FullRect);
        try
        {
            await Frames(tree);
            page.OpenDocument(CeMissionProjectTests.Authored());
            Task<bool> opening = page.OpenFileAsync(Path.Combine(output, "delayed.ceproject"));
            check.That(page.Busy && page.OpenProject.Disabled && page.SaveProject.Disabled && !page.ProjectName.Editable,
                "an active project read disables competing file actions and field edits");
            Text(page.ProjectName, "Newer pending name");
            files.Read.SetResult(new(true, "authored delayed read", CeMissionProjectJson.Write(CeMissionProject.Empty("late", "Late"))));
            check.That(!await opening && page.ProjectName.Text == "Newer pending name" && page.HasUnsavedChanges,
                "a delayed read cannot discard a newer pending field");
            page.ApplyDrafts();
            Task<bool> saving = page.SaveFileAsync(Path.Combine(output, "delayed-save.ceproject"));
            check.That(page.Busy && page.AddObject.Disabled && !page.Source.Editable, "an active project write prevents competing page changes");
            string source = page.Editor.Current.Scripts[0].Id;
            page.Editor.TrySetSource(source, "// Newer document source\n", page.Editor.Revision, out _);
            files.Write.SetResult(new(true, "authored delayed write", "snapshot.ceproject"));
            check.That(await saving && page.HasUnsavedChanges && page.Editor.Current.Script(source).Text == "// Newer document source\n" &&
                page.Notice.Contains("newer changes", StringComparison.Ordinal), "a late write saves its snapshot without marking a newer document saved");
        }
        finally { viewport.QueueFree(); await Frames(tree); }
    }

    private sealed class DelayedFiles : ICeMissionProjectFiles
    {
        internal TaskCompletionSource<CeProjectRead> Read { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
        internal TaskCompletionSource<CeProjectWrite> Write { get; } = new(TaskCreationOptions.RunContinuationsAsynchronously);
        public CeProjectRead Open(string path) => Read.Task.GetAwaiter().GetResult();
        public CeProjectWrite WriteNew(string path, byte[] bytes, IReadOnlyList<string?> protectedFolders) => Write.Task.GetAwaiter().GetResult();
    }

    internal static void Text(LineEdit field, string text) { field.Text = text; field.EmitSignal(LineEdit.SignalName.TextChanged, text); }
    internal static void Source(CeMissionProjectPage page, string text) { page.Source.Text = text; page.Source.EmitSignal(TextEdit.SignalName.TextChanged); }
    internal static void Press(Button button) { if (!button.Disabled) button.EmitSignal(BaseButton.SignalName.Pressed); }
    private static int Index(CeMissionProjectPage page, string id) => page.Editor.Current.Placements.ToList().FindIndex(item => item.Id == id);
    private static void SelectObject(CeMissionProjectPage page, string id) => page.Objects.EmitSignal(ItemList.SignalName.ItemSelected, Index(page, id));
    private static void SelectSource(CeMissionProjectPage page, string id) => page.Sources.EmitSignal(OptionButton.SignalName.ItemSelected,
        page.Editor.Current.Scripts.ToList().FindIndex(item => item.Id == id));
    internal static async Task Frames(SceneTree tree, int count = 2)
    { for (int index = 0; index < count; index++) await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame); }
    internal static void Button(LevelTerrainViewport view, Vector2 local, bool pressed)
    {
        Vector2 point = view.GlobalPosition + local;
        view.GetViewport().PushInput(new InputEventMouseButton { Position = point, GlobalPosition = point,
            ButtonIndex = MouseButton.Left, Pressed = pressed, ButtonMask = pressed ? MouseButtonMask.Left : 0 }, true);
    }
    internal static void Pointer(LevelTerrainViewport view, Vector2 from, Vector2 to, bool held)
    {
        Vector2 point = view.GlobalPosition + to;
        view.GetViewport().PushInput(new InputEventMouseMotion { Position = point, GlobalPosition = point, Relative = to - from,
            ButtonMask = held ? MouseButtonMask.Left : 0 }, true);
    }
}
