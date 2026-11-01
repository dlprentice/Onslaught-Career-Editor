// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Text;
using Godot;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;
using NumericVector3 = System.Numerics.Vector3;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>The actual page, discard dialogs and edit history on authored worlds; no game, save, compiler or mod publication is run.</summary>
internal static class LevelTriggerInspectorPageTests
{
    internal static async Task Frames(SceneTree tree, int count = 2)
    {
        for (int i = 0; i < count; i++) await tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
    }

    internal static string CreateGame(string output)
    {
        string game = LevelEditorTests.GameWithLevels(output);
        File.WriteAllText(Path.Combine(game, "BEA.exe"), "Authored editor fixture; not an executable.");
        WorldBody body = new() { Version = 43, BaseLevel = -1, MapNumber = 2 };
        body.Things.Add(new PlacedObject
        {
            ObjectId = 36,
            Init = new ObjectInit { Name = "Harbour trigger", Position = new NumericVector3(180, 180, -20), Active = 1,
                SphereTrigger = new SphereTriggerInit { Radius = 3 } },
        });
        body.Things.Add(new PlacedObject
        {
            ObjectId = ObjectKinds.Unit, Definition = "authored-unit",
            Init = new ObjectInit { Name = "Authored unit", Position = new NumericVector3(240, 210, -25), Active = 1 },
        });
        byte[] numbers;
        using (MemoryStream data = new())
        {
            using (BinaryWriter writer = new(data, Encoding.ASCII, leaveOpen: true)) { writer.Write(-1); writer.Write(100); }
            numbers = data.ToArray();
        }
        byte[] packed = Chunk("WRES", Chunk("WRLD", [.. Chunk("WDAT", numbers), .. Chunk("RLWD", body.Write())]));
        using MemoryStream compressed = new();
        using (ZLibStream zlib = new(compressed, CompressionLevel.Optimal, leaveOpen: true)) zlib.Write(packed);
        byte[] member = compressed.ToArray();
        using MemoryStream archive = new();
        using (BinaryWriter writer = new(archive, Encoding.ASCII, leaveOpen: true)) { writer.Write(member.Length); writer.Write(member); }
        File.WriteAllBytes(Path.Combine(game, "data", "resources", "100_res_PC.aya"), AuthoredTerrainFixture.WithAuthoredTerrain(archive.ToArray()));
        return game;
    }

    private static byte[] Chunk(string tag, byte[] bytes)
    {
        using MemoryStream data = new();
        using (BinaryWriter writer = new(data, Encoding.ASCII, leaveOpen: true))
        { writer.Write(Encoding.ASCII.GetBytes(tag)); writer.Write(bytes.Length); writer.Write(bytes); }
        return data.ToArray();
    }

    internal static void Type(LevelEditorPage page, string text)
    {
        page.TriggerRadius.RadiusInput.Text = text;
        page.TriggerRadius.RadiusInput.EmitSignal(LineEdit.SignalName.TextChanged, text);
    }

    private static void Confirm(CompanionApp app)
    {
        app.DiscardDialog.EmitSignal(ConfirmationDialog.SignalName.Confirmed);
        app.DiscardDialog.Hide();
    }

    private static void Cancel(CompanionApp app)
    {
        app.DiscardDialog.EmitSignal(ConfirmationDialog.SignalName.Canceled);
        app.DiscardDialog.Hide();
    }

    private static async Task CheckOrbit(SceneTree tree, LevelEditorPage page, Checks check, string when, bool crossHelp = false)
    {
        var view = page.TerrainPreview;
        Camera3D camera = view.FindChildren("*", nameof(Camera3D), true, false).OfType<Camera3D>().Single();
        Vector3 before = camera.GlobalPosition;
        Vector2 start = view.GlobalPosition + new Vector2(30, crossHelp ? 60 : 90), end = start + new Vector2(30, 20);
        Viewport host = view.GetViewport();
        host.PushInput(new InputEventMouseMotion { Position = start, GlobalPosition = start }, true);
        host.PushInput(new InputEventMouseButton { Position = start, GlobalPosition = start, ButtonIndex = MouseButton.Left, Pressed = true, ButtonMask = MouseButtonMask.Left }, true);
        host.PushInput(new InputEventMouseMotion { Position = end, GlobalPosition = end, Relative = end - start, ButtonMask = MouseButtonMask.Left }, true);
        host.PushInput(new InputEventMouseButton { Position = end, GlobalPosition = end, ButtonIndex = MouseButton.Left }, true);
        await Frames(tree);
        check.That(camera.GlobalPosition.DistanceTo(before) > 0.001f, "the real editor background drag orbits " + when);
    }

    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("trigger inspector through editor page");
        string scratch = Path.Combine(output, "trigger-page");
        string game = CreateGame(Path.Combine(scratch, "first"));
        string other = CreateGame(Path.Combine(scratch, "second"));
        string[] before = LevelEditorPageTests.Snapshot(game);
        int quit = 0, external = 0;
        CompanionEnvironment environment = new([], Path.Combine(scratch, "settings.json"), GameRunning: () => false,
            OpenUrl: _ => external++, DefaultBackupFolder: Path.Combine(scratch, "unused-backups"), Quit: () => quit++,
            OldCopiesFolder: Path.Combine(scratch, "unused-copies"), CeUserFolder: Path.Combine(scratch, "unused-ce"));
        CompanionApp app = new(null, managesWindow: false, environment);
        await Frames(tree, 1);
        tree.Root.AddChild(app);
        try
        {
            for (int i = 0; i < 300 && app.Game.Busy; i++) await Frames(tree, 1);
            check.That((await app.Game.ChooseAsync(game)).Ok, "the app selects only the authored game-shaped fixture");
            app.Navigate("levels");
            await Frames(tree);
            LevelEditorPage page = app.LevelEditor;
            LevelEditorModel model = page.Model!;
            EditSession session = model.Session!;
            byte[] baseline = session.ToBytes();
            check.That(!page.TriggerRadius.Visible && !page.HasChanges && page.SelectIndex(0) && page.TriggerRadius.Visible &&
                page.TriggerRadius.RadiusInput.Text == "3", "selecting the existing trigger binds its stored radius");
            page.TerrainViewSwitch.ButtonPressed = true;
            await Frames(tree, 3);
            check.That(page.TerrainPreview.IsVisibleInTree() && page.Map.Selected == 0 && page.Map.Rows.Count == 2,
                "the 3D viewport and inspector share the selected authored world");
            await CheckOrbit(tree, page, check, "before a discard dialog");
            await CheckOrbit(tree, page, check, "across the help overlay", crossHelp: true);

            long revision = page.ConfirmationRevision;
            Type(page, "7");
            page.Refresh();
            check.That(page.TriggerRadius.HasDraft && page.TriggerRadius.RadiusInput.Text == "7" && page.ChangeCount == 1 && page.HasChanges &&
                page.ConfirmationRevision > revision && page.DraftNote.Contains("radius", StringComparison.Ordinal) && session.ToBytes().SequenceEqual(baseline),
                "a typed radius stays unapplied across a same-session refresh and counts as an unsaved draft");
            check.That(!page.SelectIndex(1) && app.DiscardDialog.Visible && page.SelectedRow == 0 && page.Map.Selected == 0,
                "changing the selection asks before discarding its radius text");
            Cancel(app);
            check.That(page.TriggerRadius.RadiusInput.Text == "7" && page.SelectedRow == 0, "cancelling selection keeps the owned radius draft");
            await CheckOrbit(tree, page, check, "after cancelling a discard dialog");
            page.SelectIndex(1);
            Type(page, "8");
            Confirm(app);
            check.That(page.SelectedRow == 0 && page.TriggerRadius.RadiusInput.Text == "8" && page.ChangeCount == 1 &&
                app.Status.Label.Text.Contains("changed while confirmation", StringComparison.Ordinal), "a dirty-to-dirty edit invalidates selection confirmation");
            page.SelectIndex(1);
            Confirm(app);
            check.That(page.SelectedRow == 1 && !page.TriggerRadius.Visible && !page.TriggerRadius.HasDraft && !page.HasChanges,
                "a fresh selection confirmation clears the draft and hides the non-trigger inspector");
            page.SelectIndex(0);
            Type(page, "8");
            page.TriggerRadius.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            byte[] resized = session.ToBytes();
            check.That(session.Body.Things[0].Init.SphereTrigger!.Radius == 8 && !page.TriggerRadius.HasDraft && page.ChangeCount == 1 &&
                page.Note.StartsWith("Radius set", StringComparison.Ordinal) && page.Summary.Contains("trigger resized", StringComparison.Ordinal) && !page.Undo.Disabled,
                "Apply reaches the real edit history, page result note and change summary");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(session.ToBytes().SequenceEqual(baseline) && page.TriggerRadius.RadiusInput.Text == "3" && !page.HasChanges, "page undo restores the world and clean inspector");
            Type(page, "3.0");
            page.TriggerRadius.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(session.CanRedo && !session.CanUndo && !page.HasChanges && page.Note.Contains("already", StringComparison.Ordinal), "a numeric no-op preserves redo and creates no unsaved change");
            page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(session.ToBytes().SequenceEqual(resized) && page.TriggerRadius.RadiusInput.Text == "8", "page redo restores the radius bytes and field");
            Type(page, "12");
            session.ResizeTrigger(0, 9);
            page.TriggerRadius.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(page.TriggerRadius.HasDraft && page.TriggerRadius.RadiusInput.Text == "12" && session.Body.Things[0].Init.SphereTrigger!.Radius == 9 &&
                page.Note.Contains("stored radius changed", StringComparison.Ordinal), "a different radius edit makes the draft stale rather than rebasing it");
            page.TriggerRadius.UseStoredRadius.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(!page.TriggerRadius.HasDraft && page.TriggerRadius.RadiusInput.Text == "9", "Use stored radius explicitly reloads the selected trigger");

            page.OpenLevel(100);
            page.SelectIndex(0);
            model = page.Model!;
            session = model.Session!;
            page.TerrainEdit.ButtonPressed = true;
            check.That(model.ChangeTerrainPreview(0, 0, true).Result == MoveResult.Moved, "the same editor can make a sampled terrain preview edit");
            Type(page, "6");
            page.TriggerRadius.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(page.ChangeCount == 2 && model.TerrainHasChanges && page.Save.Disabled && page.Play.Disabled && !page.SaveNow().Ok &&
                !model.SaveAsMod(game, new ModInfo("preview", "Preview"), []).Ok && !model.StageForPlay(game, new ModInfo("preview", "Preview"), []).Ok,
                "radius editing cannot bypass preview-only terrain save and play guards");
            page.Play.Disabled = false;
            await page.PlayAsync();
            check.That(page.PlayNote.Length == 0, "even a directly invoked play action refuses changed terrain before launching");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(model.TerrainHasChanges && session.Body.Things[0].Init.SphereTrigger!.Radius == 3, "undo restores the radius while keeping earlier terrain preview edits");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(!model.TerrainHasChanges && !page.HasChanges, "the next undo restores the terrain preview too");

            Type(page, "10");
            page.PickLevel(200);
            revision = page.ConfirmationRevision;
            Type(page, "11");
            Confirm(app);
            check.That(ReferenceEquals(model.Session, session) && page.TriggerRadius.RadiusInput.Text == "11" && page.ConfirmationRevision > revision,
                "a same-count newer radius draft survives a stale level discard confirmation");
            check.That(!app.RequestClose() && app.DiscardDialog.Visible, "closing asks about the unapplied radius draft");
            Type(page, "12");
            Confirm(app);
            check.That(quit == 0 && page.TriggerRadius.RadiusInput.Text == "12", "a dirty-to-dirty draft edit also invalidates close confirmation");
            app.RequestClose();
            Cancel(app);
            check.That(quit == 0 && page.TriggerRadius.HasDraft, "ordinary close cancellation keeps the draft");
            app.RequestClose();
            typeof(LevelEditorModel).GetProperty(nameof(LevelEditorModel.Session))!.SetValue(model, new EditSession(baseline));
            Confirm(app);
            check.That(quit == 0, "a replaced session invalidates a pending close even without a change event");

            page.OpenLevel(100);
            page.SelectIndex(0);
            Type(page, "5");
            await app.Home.ChooseAsync(other);
            Type(page, "6");
            Confirm(app);
            check.That(app.Game.Folder?.Root == game && page.TriggerRadius.RadiusInput.Text == "6", "a newer radius draft invalidates folder-switch confirmation");
            await app.Home.ChooseAsync(other);
            await app.Game.ChooseAsync(other); // Authored replacement arriving independently while the dialog is open.
            Confirm(app);
            check.That(!ReferenceEquals(page.Model, model) && app.Status.Label.Text.Contains("changed while confirmation", StringComparison.Ordinal),
                "a replaced page model invalidates the pending folder confirmation");
            page.Refresh();
            page.SelectIndex(0);
            Type(page, "7");
            await app.Home.ChooseAsync(game);
            Cancel(app);
            check.That(app.Game.Folder?.Root == other && page.TriggerRadius.HasDraft, "folder-switch cancellation keeps the current model and draft");
            await app.Home.ChooseAsync(game);
            Confirm(app);
            for (int i = 0; i < 300 && (app.Game.Busy || app.Game.Folder?.Root != game); i++) await Frames(tree, 1);
            check.That(app.Game.Folder?.Root == game && !page.TriggerRadius.HasDraft && !page.TriggerRadius.Visible, "a fresh accepted folder switch clears the old inspector binding");
            page.SelectIndex(0);
            Type(page, "8");
            app.RequestClose();
            Confirm(app);
            check.That(quit == 1 && external == 0 && LevelEditorPageTests.Snapshot(game).SequenceEqual(before),
                "fresh close confirmation works, no external action ran, and all authored game files stayed unchanged");
        }
        finally { app.QueueFree(); await Frames(tree); }
    }
}
