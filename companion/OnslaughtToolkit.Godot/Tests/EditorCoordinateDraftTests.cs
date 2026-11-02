// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Unapplied coordinates through the real page, selection confirmations and edit history on authored worlds only.</summary>
internal static class EditorCoordinateDraftTests
{
    private sealed class ProjectProbe : IEditorProjectFiles
    {
        internal int Reads, Writes;
        public EditorProjectRead Open(string path) { Reads++; return new(false, "Unexpected authored project read."); }
        public EditorProjectWrite WriteNew(string path, byte[] bytes, IReadOnlyList<string?> protectedFolders)
        { Writes++; return new(false, "Unexpected authored project write."); }
    }

    private static void Type(LineEdit field, string text)
    {
        field.Text = text;
        field.EmitSignal(LineEdit.SignalName.TextChanged, text);
    }

    private static void Escape(LineEdit field) => field.EmitSignal(Control.SignalName.GuiInput,
        new InputEventKey { Keycode = Key.Escape, PhysicalKeycode = Key.Escape, Pressed = true });

    private static void Press(BaseButton button) => button.EmitSignal(BaseButton.SignalName.Pressed);
    private static bool Unchanged(EditSession session, byte[] bytes, string? undo, bool redo) =>
        session.ToBytes().AsSpan().SequenceEqual(bytes) && session.UndoDescription == undo && session.CanRedo == redo;

    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("editor coordinate drafts");
        string scratch = Path.Combine(output, "coordinate-drafts");
        string gameRoot = LevelTriggerInspectorPageTests.CreateGame(scratch);
        string[] originalFiles = LevelEditorPageTests.Snapshot(gameRoot);
        SettingsStore settings = new(Path.Combine(scratch, "settings.json"));
        GameLibrary game = new([], settings, ceUserFolder: Path.Combine(scratch, "unused-ce"), ceEnvironment: _ => null);
        typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, GameFolder.Inspect(gameRoot, "Authored coordinate fixture"));
        ProjectProbe files = new();
        Action? discard = null;
        string question = "";
        int external = 0;
        Control popups = new();
        AppServices services = new()
        {
            Workspace = new CareerWorkspace(new SaveFileWorker(new ProtectedSaveFiles())), EditorProjects = files,
            Game = game, Status = new StatusLine(), Backups = new(settings, Path.Combine(scratch, "unused-backups")), GameRunning = () => false,
            OpenUrl = _ => external++, Navigate = _ => external++, OpenCareer = null!, ChooseCareer = null!, OpenCareerFile = () => external++,
            AskToDiscard = (text, _, action) => { question = text; discard = action; }, LevelEditsUnsaved = () => 0,
            Play = new CePlay(game, Path.Combine(scratch, "unused-play")), Popups = popups, CatchUp = () => Task.CompletedTask,
        };
        void Confirm() { Action? action = discard; discard = null; action?.Invoke(); }
        Theme theme = CompanionTheme.Build();
        LevelEditorPage page = new(services);
        page.Root.Theme = theme;
        page.Root.Size = new Vector2(1280, 800);
        tree.Root.AddChild(popups); tree.Root.AddChild(page.Root);
        try
        {
            page.Refresh();
            await LevelTriggerInspectorPageTests.Frames(tree);
            LevelEditorModel model = page.Model!;
            EditSession session = model.Session!;
            check.That(page.SelectIndex(1) && !page.HasChanges, "the authored unit starts selected without an unapplied draft");
            byte[] baseline = session.ToBytes();
            Type(page.X, "-");
            page.X.EmitSignal(Control.SignalName.FocusExited);
            page.Refresh();
            check.That(page.X.Text == "-" && page.CoordinatesHaveDraft && page.HasChanges && page.ChangeCount == 1 &&
                page.SaveProject.Disabled && page.OpenProject.Disabled && page.Save.Disabled && page.Play.Disabled &&
                session.ToBytes().AsSpan().SequenceEqual(baseline), "invalid coordinate text stays unsaved through focus exit and same-session refresh");
            check.That(!page.SelectIndex(0) && discard is not null && question.Contains("coordinates", StringComparison.Ordinal) &&
                page.SelectedRow == 1 && page.Map.Selected == 1 && page.X.Text == "-", "selection asks before replacing unapplied coordinate text and keeps the selected marker");
            discard = null;
            check.That(page.X.Text == "-" && page.SelectedRow == 1 && page.CoordinatesHaveDraft, "cancelling selection keeps the owned coordinate draft");
            page.SelectIndex(0);
            Type(page.X, "newer draft");
            Confirm();
            check.That(page.SelectedRow == 1 && page.X.Text == "newer draft" && page.Problem.Contains("changed while confirmation", StringComparison.Ordinal),
                "dirty-to-dirty coordinate typing invalidates an old selection confirmation");
            page.SelectIndex(0);
            long revision = page.ConfirmationRevision;
            page.X.Text = "programmatic newer draft";
            Confirm();
            check.That(page.ConfirmationRevision == revision && page.SelectedRow == 1 && page.X.Text == "programmatic newer draft" && page.CoordinatesHaveDraft,
                "an unannounced coordinate change also invalidates confirmation by its actual text");
            page.SelectIndex(0); Confirm();
            check.That(page.SelectedRow == 0 && page.Map.Selected == 0 && !page.CoordinatesHaveDraft && !page.HasChanges && page.X.Text == "180",
                "fresh explicit discard selects the requested object and refreshes its coordinates");
            Type(page.X, "unfinished coordinate");
            LevelTriggerInspectorPageTests.Type(page, "7");
            check.That(!page.SelectIndex(1) && question.Contains("radius and coordinates", StringComparison.Ordinal) && page.ChangeCount == 2,
                "one selection confirmation names both kinds of unapplied inspector text");
            discard = null;
            check.That(page.X.Text == "unfinished coordinate" && page.TriggerRadius.RadiusInput.Text == "7", "cancelling keeps both coordinate and radius text");
            page.SelectIndex(1); Confirm();
            check.That(page.SelectedRow == 1 && !page.CoordinatesHaveDraft && !page.TriggerRadius.HasDraft && !page.HasChanges,
                "fresh confirmed selection discards both drafts together");

            model.MoveTo(1, 260, 210);
            session.Undo();
            byte[] before = session.ToBytes();
            string? undo = session.UndoDescription;
            bool redo = session.CanRedo;
            Type(page.X, "unfinished");
            check.That(page.Undo.Disabled && page.Redo.Disabled && page.Reset.Disabled && page.Duplicate.Disabled,
                "coordinate drafts disable history, reset and copy controls until applied or restored");
            DuplicateOutcome? copy = page.DuplicateSelected();
            Press(page.Reset); Press(page.Undo); Press(page.Redo);
            MoveOutcome? sameDrag = page.Dragged(1, 300, 300), otherDrag = page.Dragged(0, 310, 310);
            page.Map._GuiInput(new InputEventKey { Keycode = Key.Right, PhysicalKeycode = Key.Right, Pressed = true });
            check.That(copy is { Ok: false } && sameDrag?.Result == MoveResult.Refused && otherDrag?.Result == MoveResult.Refused &&
                page.SelectedRow == 1 && page.X.Text == "unfinished" && page.CoordinatesHaveDraft && Unchanged(session, before, undo, redo),
                "direct copy, reset, history, drag and map nudge actions preserve draft text, world bytes and redo history");
            bool accepted = page.RequestProjectSave(Path.Combine(scratch, "unapplied" + EditorProjectFiles.Extension));
            await page.OpenProjectAsync(Path.Combine(scratch, "unopened" + EditorProjectFiles.Extension));
            check.That(!accepted && files.Reads == 0 && files.Writes == 0 && page.CoordinatesHaveDraft && page.X.Text == "unfinished" &&
                page.ProjectMessage.Contains("Apply coordinate edits", StringComparison.Ordinal), "coordinate drafts refuse both project operations before any file boundary is called");
            Escape(page.X);
            check.That(!page.CoordinatesHaveDraft && page.X.Text == "240" && !page.Duplicate.Disabled && !page.Redo.Disabled && Unchanged(session, before, undo, redo),
                "Escape explicitly restores stored coordinates and re-enables controls without consuming redo");
            Type(page.X, "262.125"); Type(page.Y, "-0");
            page.X.EmitSignal(LineEdit.SignalName.TextSubmitted, page.X.Text);
            byte[] moved = session.ToBytes();
            check.That(!page.CoordinatesHaveDraft && page.X.Text == "262.125" && page.Y.Text == "-0" &&
                session.Body.Things[1].Init.Position.X == 262.125f && BitConverter.SingleToInt32Bits(session.Body.Things[1].Init.Position.Y) == BitConverter.SingleToInt32Bits(-0f),
                "Enter applies the complete valid draft once and preserves a typed negative zero");
            Press(page.Undo);
            check.That(session.ToBytes().AsSpan().SequenceEqual(before) && !page.CoordinatesHaveDraft, "one page undo restores the complete pre-coordinate world");
            Press(page.Redo);
            check.That(session.ToBytes().AsSpan().SequenceEqual(moved) && !page.CoordinatesHaveDraft, "one page redo restores that coordinate move");

            Type(page.X, "kept over external move");
            model.MoveTo(1, 275, 213);
            before = session.ToBytes(); undo = session.UndoDescription; redo = session.CanRedo;
            MoveOutcome? stale = page.ApplyFields(explicitly: true);
            check.That(page.X.Text == "kept over external move" && page.CoordinatesHaveDraft && stale?.Result == MoveResult.Refused &&
                page.Note.Contains("stored object or position changed", StringComparison.Ordinal) && Unchanged(session, before, undo, redo),
                "a changed stored position preserves the old text and refuses to silently rebase or apply it");
            Escape(page.X);
            check.That(page.X.Text == "275" && page.Y.Text == "213" && !page.CoordinatesHaveDraft, "Escape after an external move loads the current stored coordinates");
            Type(page.X, "285");
            session.Body.Things[1] = session.Body.Things[1].Clone();
            before = session.ToBytes(); undo = session.UndoDescription; redo = session.CanRedo;
            stale = page.ApplyFields(explicitly: true);
            page.Refresh();
            check.That(stale?.Result == MoveResult.Refused && page.X.Text == "285" && page.CoordinatesHaveDraft && Unchanged(session, before, undo, redo),
                "an unannounced record replacement cannot redirect coordinate text to a different object in the same row");
            Escape(page.X);
            copy = page.DuplicateSelected();
            check.That(copy is { Ok: true } && page.SelectedRow == copy.Row, "an ordinary copy remains available after explicitly restoring coordinate text");
            Type(page.X, "keep after removal");
            session.Undo();
            check.That(page.SelectedRow is null && page.X.Text == "keep after removal" && !page.X.Editable && page.CoordinatesHaveDraft && page.HasChanges,
                "a model-side removal of the selected copy retains its unbound coordinate draft for explicit discard");
            check.That(!page.SelectIndex(1) && discard is not null && page.X.Text == "keep after removal", "selecting after record removal still asks before dropping the retained text");
            discard = null; Escape(page.X); page.SelectIndex(1);
            Type(page.X, "old session draft");
            page.SelectIndex(0);
            page.OpenLevel(100); page.SelectIndex(1);
            Type(page.X, "new session draft");
            Confirm();
            check.That(!ReferenceEquals(model.Session, session) && page.SelectedRow == 1 && page.X.Text == "new session draft" && page.CoordinatesHaveDraft,
                "a selection confirmation captured for an earlier session cannot discard the new session's text");
            check.That(originalFiles.SequenceEqual(LevelEditorPageTests.Snapshot(gameRoot)) && external == 0 && files.Reads == 0 && files.Writes == 0,
                "coordinate authoring changes no authored game file and dispatches no project read, project write, launch or external action");
        }
        finally
        {
            page.Root.QueueFree(); popups.QueueFree(); services.Status.Root.QueueFree();
            await LevelTriggerInspectorPageTests.Frames(tree);
            theme.Dispose();
        }
    }
}
