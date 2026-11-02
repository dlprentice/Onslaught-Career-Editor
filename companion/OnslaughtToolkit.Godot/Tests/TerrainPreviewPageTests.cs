// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Exercises terrain preview through the real page using only authored game-shaped data.</summary>
internal static class TerrainPreviewPageTests
{
    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);

    private static Camera3D? Camera(Node root)
    {
        if (root is Camera3D camera) return camera;
        foreach (Node child in root.GetChildren())
            if (Camera(child) is Camera3D found) return found;
        return null;
    }

    private static void Click(SceneTree tree, LevelTerrainViewport view, Vector2 local, bool lower = false, bool? lowerAtRelease = null)
    {
        Vector2 at = view.GetGlobalRect().Position + local;
        tree.Root.PushInput(new InputEventMouseMotion { Position = at, GlobalPosition = at }, true);
        tree.Root.PushInput(new InputEventMouseButton { ButtonIndex = MouseButton.Left, Pressed = true, Position = at, GlobalPosition = at, ButtonMask = MouseButtonMask.Left, ShiftPressed = lower }, true);
        tree.Root.PushInput(new InputEventMouseButton { ButtonIndex = MouseButton.Left, Pressed = false, Position = at, GlobalPosition = at, ShiftPressed = lowerAtRelease ?? lower }, true);
    }

    internal static async Task RunAsync(SceneTree tree, string outputDirectory, Checks check)
    {
        check.Suite("terrain preview page");
        string scratch = Path.Combine(outputDirectory, "terrain-preview-page");
        string gameRoot = LevelEditorTests.GameWithLevels(scratch);
        string archive = Path.Combine(gameRoot, "data", "resources", "100_res_PC.aya");
        File.WriteAllBytes(archive, AuthoredTerrainFixture.WithAuthoredTerrain(File.ReadAllBytes(archive)));
        AuthoredTerrainFixture.AddDraftSources(gameRoot);
        string[] files = LevelEditorPageTests.Snapshot(gameRoot);
        SettingsStore settings = new(Path.Combine(scratch, "settings.json"));
        GameLibrary game = new([], settings, ceUserFolder: "", ceEnvironment: _ => null);
        typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, GameFolder.Inspect(gameRoot, "Authored terrain fixture"));
        Action? pendingDiscard = null;
        int externalActions = 0;
        void Confirm() { Action? confirm = pendingDiscard; pendingDiscard = null; confirm?.Invoke(); }
        Control popups = new();
        AppServices services = new()
        {
            Workspace = null!, Game = game, Status = new StatusLine(), Backups = null!, GameRunning = () => false,
            OpenUrl = _ => externalActions++, Navigate = _ => externalActions++, OpenCareer = null!, ChooseCareer = null!,
            OpenCareerFile = () => externalActions++, AskToDiscard = (_, _, confirm) => pendingDiscard = confirm,
            LevelEditsUnsaved = () => 0, Play = new CePlay(game, Path.Combine(scratch, "unused-play")),
            Popups = popups, CatchUp = () => Task.CompletedTask,
        };
        Theme theme = CompanionTheme.Build();
        LevelEditorPage page = new(services);
        page.Root.Theme = theme;
        page.Root.Size = new Vector2(1280, 800);
        await Frame(tree);
        tree.Root.AddChild(popups);
        tree.Root.AddChild(page.Root);
        page.Refresh();
        await Frame(tree);
        check.That(page.OpenLevel(100), "the authored base level opens for terrain preview");
        LevelEditorModel model = page.Model!;
        EditSession? session = model.Session;
        Heightfield? baseTerrain = model.Terrain;
        check.That(session is not null && baseTerrain is not null, "the authored base includes a world and terrain");
        if (session is null || baseTerrain is null) return;
        byte[] worldBefore = session.ToBytes();
        string baseHash = baseTerrain.SamplesSha256();
        Vector2I oldSize = tree.Root.Size;
        try
        {
            tree.Root.Size = new Vector2I(1280, 800);
            page.TerrainViewSwitch.ButtonPressed = false;
            check.That(page.TerrainEdit.Disabled, "terrain editing is disabled while the 2D map is shown");
            page.TerrainViewSwitch.ButtonPressed = true;
            for (int i = 0; i < 3; i++) await Frame(tree);
            check.That(!page.TerrainEdit.Disabled, "the 3D view enables terrain preview mode");
            page.TerrainEdit.ButtonPressed = true;
            for (int i = 0; i < 3; i++) await Frame(tree);
            LevelTerrainViewport view = page.TerrainPreview;
            TerrainSurface? original = model.TerrainPreviewSurface;
            Camera3D? camera = Camera(view);
            check.That(original is not null && camera is not null && view.IsVisibleInTree() && !model.TerrainHasChanges &&
                       page.WorldNote.Contains("unsaved 3D preview", StringComparison.Ordinal) && page.WorldNote.Contains("2D map shows base terrain", StringComparison.Ordinal),
                       "enabling the mode shows its preview and the unchanged 2D-baseline warning");
            if (original is null || camera is null || !view.IsVisibleInTree()) return;

            Vector2? target = null;
            var vertices = original.Vertices.ToArray();
            var indices = original.Indices.ToArray();
            for (int i = 0; i + 2 < indices.Length; i += 3)
            {
                var point = (vertices[indices[i]] + vertices[indices[i + 1]] + vertices[indices[i + 2]]) / 3;
                Vector2 screen = camera.UnprojectPosition(new Vector3(point.X, point.Y, point.Z));
                if (screen.X <= 20 || screen.Y <= 70 || screen.X >= view.Size.X - 20 || screen.Y >= view.Size.Y - 20) continue;
                target = screen;
                break;
            }
            check.That(target is not null, "an authored terrain point is visible for the click");
            if (target is not Vector2 at) return;
            Vector3 cameraBefore = camera.GlobalPosition;
            Click(tree, view, at);
            TerrainSurface? raised = model.TerrainPreviewSurface;
            check.That(raised is not null && !ReferenceEquals(raised, original) && model.TerrainHasChanges && page.HasChanges && page.ChangeCount == 1 &&
                       page.Summary.Contains("3D terrain preview", StringComparison.Ordinal) &&
                       session.ToBytes().SequenceEqual(worldBefore) && baseTerrain.SamplesSha256() == baseHash,
                       "a 3D click creates one unsaved terrain change without changing the world or base heightfield");
            check.That(!page.Warnings.Contains("Nothing has changed", StringComparison.Ordinal),
                       "a terrain-only change is not contradicted by the world body's no-change message");
            if (raised is null) return;
            check.That(raised.Vertices.ToArray().Zip(vertices).Count(pair => pair.First != pair.Second) == 1,
                       "the click changes exactly one sampled preview vertex");
            Click(tree, view, at);
            check.That(ReferenceEquals(model.TerrainPreviewSurface, raised) && page.ChangeCount == 1,
                       "a second click before redraw cannot use the stale surface");
            for (int i = 0; i < 2; i++) await Frame(tree);
            check.That(camera.GlobalPosition.DistanceTo(cameraBefore) < 0.001f, "a terrain rebuild preserves the camera position");
            var raisedVertices = raised.Vertices.ToArray();
            Click(tree, view, at, lower: true, lowerAtRelease: false);
            TerrainSurface? lowered = model.TerrainPreviewSurface;
            check.That(lowered is not null && !ReferenceEquals(lowered, raised) &&
                       lowered.Vertices.ToArray().Zip(raisedVertices).Count(pair => pair.First.Y == pair.Second.Y - TerrainDraft.Step) == 1,
                       "releasing Shift before the mouse still lowers one preview point");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            raised = model.TerrainPreviewSurface;
            check.That(raised is not null && raised.Vertices.ToArray().SequenceEqual(raisedVertices) && model.TerrainHasChanges,
                       "undo takes back the Shift-click without losing the earlier raise");
            if (raised is null) return;
            for (int i = 0; i < 2; i++) await Frame(tree);
            Click(tree, view, at, lower: false, lowerAtRelease: true);
            TerrainSurface? raisedAgain = model.TerrainPreviewSurface;
            check.That(raisedAgain is not null && !ReferenceEquals(raisedAgain, raised) &&
                       raisedAgain.Vertices.ToArray().Zip(raisedVertices).Count(pair => pair.First.Y == pair.Second.Y + TerrainDraft.Step) == 1,
                       "pressing Shift only after the mouse still raises one preview point");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            raised = model.TerrainPreviewSurface;
            check.That(raised is not null && raised.Vertices.ToArray().SequenceEqual(raisedVertices), "undo restores the preview after that raise");
            if (raised is null) return;
            for (int i = 0; i < 2; i++) await Frame(tree);
            check.That(page.Save.Disabled && page.Play.Disabled && !page.SaveNow().Ok &&
                       !model.SaveAsMod(gameRoot, new ModInfo("preview", "Preview"), []).Ok &&
                       !model.StageForPlay(gameRoot, new ModInfo("preview", "Preview"), []).Ok,
                       "page and model refuse save and play staging for changed terrain even without a selected-world override");
            page.Save.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(!page.SaveDialog.Visible, "a direct save signal cannot open the save dialog for changed terrain");
            page.Play.Disabled = false;
            await page.PlayAsync();
            page.Play.Disabled = true;
            check.That(page.PlayNote.Length == 0, "direct play refuses before attempting to launch");

            page.PickLevel(200);
            check.That(pendingDiscard is not null, "leaving the level asks before discarding terrain edits");
            pendingDiscard = null;
            check.That(model.TerrainHasChanges && ReferenceEquals(model.TerrainPreviewSurface, raised), "cancel keeps the terrain preview");
            check.That(model.Move(0, "55", "66", "-0").Result == MoveResult.Moved, "an object move can follow the terrain click");
            byte[] movedWorld = session.ToBytes();
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(session.ToBytes().SequenceEqual(worldBefore) && model.TerrainHasChanges, "undo first restores the object and keeps terrain");
            page.Undo.EmitSignal(BaseButton.SignalName.Pressed);
            check.That(!model.TerrainHasChanges && !page.HasChanges && model.TerrainPreviewSurface!.Vertices.ToArray().SequenceEqual(vertices),
                       "the next undo restores the terrain preview and clears its dirty state");
            page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
            page.Redo.EmitSignal(BaseButton.SignalName.Pressed);
            raised = model.TerrainPreviewSurface;
            check.That(raised is not null && raised.Vertices.ToArray().SequenceEqual(raisedVertices) && model.TerrainHasChanges &&
                session.ToBytes().SequenceEqual(movedWorld), "redo restores the terrain vertices and object in order");
            if (raised is null) return;

            page.TerrainViewSwitch.ButtonPressed = false;
            check.That(page.TerrainEdit.Disabled && !page.TerrainEdit.ButtonPressed && page.WorldNote.Contains("2D map shows base terrain", StringComparison.Ordinal) && page.Save.Disabled && page.Play.Disabled,
                       "the 2D view identifies its base relief and keeps changed terrain unsavable");
            page.TerrainViewSwitch.ButtonPressed = true;
            page.TerrainEdit.ButtonPressed = true;
            for (int i = 0; i < 2; i++) await Frame(tree);

            page.PickLevel(200);
            check.That(pendingDiscard is not null, "changing levels asks before losing terrain edits");
            pendingDiscard = null;
            check.That(ReferenceEquals(model.Session, session) && ReferenceEquals(model.TerrainPreviewSurface, raised), "cancel keeps both edits");
            page.PickLevel(200);
            check.That(model.ChangeTerrainPreview(0, 0, false).Result == MoveResult.Moved, "a newer terrain edit can arrive while the level question is open");
            TerrainSurface? newerAfterQuestion = model.TerrainPreviewSurface;
            Confirm();
            check.That(ReferenceEquals(model.Session, session) && ReferenceEquals(model.TerrainPreviewSurface, newerAfterQuestion) &&
                       page.Problem.Contains("changed", StringComparison.Ordinal), "a stale level confirmation preserves the newer terrain edit");
            page.PickLevel(200);
            var position = session.Body.Things[0].Init.Position;
            session.Body.Things[0].Init.Position = new System.Numerics.Vector3(position.X + 1, position.Y, position.Z); // Deliberately bypass the command notifier.
            byte[] changedWithoutNotice = session.ToBytes();
            Confirm();
            check.That(ReferenceEquals(model.Session, session) && session.ToBytes().SequenceEqual(changedWithoutNotice) &&
                       page.Problem.Contains("changed", StringComparison.Ordinal), "the level confirmation also catches an unnotified world change");
            page.PickLevel(200);
            Confirm();
            check.That(!ReferenceEquals(model.Session, session) && !model.TerrainHasChanges && !page.TerrainEdit.ButtonPressed,
                       "confirming a new level resets its terrain preview mode and draft");
            check.That(baseTerrain.SamplesSha256() == baseHash && LevelEditorPageTests.Snapshot(gameRoot).SequenceEqual(files),
                       "the authored files and original base terrain remain unchanged");

            check.That(page.OpenLevel(100), "the authored level opens for script-draft confirmation checks");
            string? scriptName = model.Scripts.FirstOrDefault()?.Summary.Name;
            bool scriptReady = scriptName is not null && page.ShowScript(scriptName) && !page.EditSource.Disabled;
            check.That(scriptReady, "the authored level has an editable source for a draft");
            if (!scriptReady) return;
            page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = "// first authored draft\n";
            page.Scripts.Source.EmitSignal(TextEdit.SignalName.TextChanged);
            await Frame(tree);
            int draftCount = page.ChangeCount;
            check.That(page.Scripts.Source.Editable && draftCount == 1 && page.Scripts.HasDraft(scriptName!), "the first authored source change is an unsaved draft");
            EditSession? scriptSession = model.Session;
            page.PickLevel(200);
            check.That(pendingDiscard is not null, "a script draft triggers the level discard question");
            long revisionBeforeNewerDraft = page.ConfirmationRevision;
            page.Scripts.Source.Text = "// newer authored draft\n";
            page.Scripts.Source.EmitSignal(TextEdit.SignalName.TextChanged);
            await Frame(tree);
            check.That(page.ConfirmationRevision > revisionBeforeNewerDraft && page.ChangeCount == draftCount && page.Scripts.HasDraft(scriptName!),
                       "the level confirmation sees a source text-change event with the same draft count");
            Confirm();
            check.That(ReferenceEquals(model.Session, scriptSession) && page.Scripts.Source.Text == "// newer authored draft\n" &&
                       page.Problem.Contains("changed", StringComparison.Ordinal), "a same-count newer draft survives stale level confirmation");
            check.That(externalActions == 0, "the authored editor checks open no external action");
        }
        finally
        {
            tree.Root.Size = oldSize;
            page.Root.QueueFree(); services.Status.Root.QueueFree(); popups.QueueFree();
            await Frame(tree);
        }
    }
}
