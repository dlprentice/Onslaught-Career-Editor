// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>A held authored folder scan exposes edits made after discard confirmation, before folder publication.</summary>
internal static class EditorFolderScanTests
{
    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("editor folder scan race");
        string scratch = Path.Combine(output, "folder-scan-race");
        string first = LevelTriggerInspectorPageTests.CreateGame(Path.Combine(scratch, "first"));
        string second = LevelTriggerInspectorPageTests.CreateGame(Path.Combine(scratch, "second"));
        int external = 0, confirmations = 0;
        CompanionEnvironment environment = new([], Path.Combine(scratch, "settings.json"), GameRunning: () => false,
            OpenUrl: _ => external++, DefaultBackupFolder: Path.Combine(scratch, "unused-backups"), Quit: () => external++,
            OldCopiesFolder: Path.Combine(scratch, "unused-copies"), CeUserFolder: Path.Combine(scratch, "unused-ce"));
        CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
        TaskCompletionSource<bool> started = new(TaskCreationOptions.RunContinuationsAsynchronously);
        using ManualResetEventSlim release = new(false);
        await LevelTriggerInspectorPageTests.Frames(tree, 1);
        tree.Root.AddChild(app);
        try
        {
            for (int i = 0; i < 300 && app.Game.Busy; i++) await LevelTriggerInspectorPageTests.Frames(tree, 1);
            if (!(await app.Game.ChooseAsync(first)).Ok) { check.Fail("the first authored game folder opens"); return; }
            app.DiscardDialog.VisibilityChanged += () => { if (app.DiscardDialog.Visible) confirmations++; };
            app.Navigate("levels");
            LevelEditorPage page = app.LevelEditor;
            page.SelectIndex(0);
            LevelEditorModel model = page.Model!;
            EditSession session = model.Session!;
            LevelTriggerInspectorPageTests.Type(page, "8");
            app.Game.BeforeChooseReadForTest = path =>
            {
                if (path != second) return;
                started.TrySetResult(true);
                if (!release.Wait(TimeSpan.FromSeconds(10))) throw new IOException("Authored folder-scan gate timed out.");
            };
            app.Navigate("home");
            await app.Home.ChooseAsync(second);
            check.That(app.DiscardDialog.Visible && page.TriggerRadius.HasDraft, "changing folders first asks about the existing radius draft");
            app.DiscardDialog.EmitSignal(ConfirmationDialog.SignalName.Confirmed); app.DiscardDialog.Hide();
            await started.Task;
            app.Navigate("levels");
            check.That(!app.RequestClose() && !app.DiscardDialog.Visible, "closing waits for the active folder scan without abandoning its pending operation");
            LevelTriggerInspectorPageTests.Type(page, "9");
            check.That(app.Game.Busy && ReferenceEquals(page.Model, model) && page.Save.Disabled && page.Play.Disabled && page.SaveProject.Disabled,
                       "the retained editor remains available during the held scan while save and play actions are fenced");
            release.Set();
            for (int i = 0; i < 300 && app.Game.Busy; i++) await LevelTriggerInspectorPageTests.Frames(tree, 1);
            await LevelTriggerInspectorPageTests.Frames(tree);
            check.That(app.Game.Folder?.Root == first && app.Game.Settings.Load().GameFolder == first && ReferenceEquals(page.Model, model) &&
                       ReferenceEquals(page.Model?.Session, session) && page.TriggerRadius.HasDraft && page.TriggerRadius.RadiusInput.Text == "9" && confirmations == 1,
                       "typing a newer radius draft during a confirmed folder scan preserves the editor, old folder and remembered folder together");
            started = new(TaskCreationOptions.RunContinuationsAsynchronously); release.Reset();
            app.Navigate("home"); await app.Home.ChooseAsync(second);
            app.DiscardDialog.EmitSignal(ConfirmationDialog.SignalName.Confirmed); app.DiscardDialog.Hide();
            await started.Task; app.Navigate("levels");
            page.X.Text = "181";
            release.Set();
            for (int i = 0; i < 300 && app.Game.Busy; i++) await LevelTriggerInspectorPageTests.Frames(tree, 1);
            await LevelTriggerInspectorPageTests.Frames(tree);
            check.That(app.Game.Folder?.Root == first && app.Game.Settings.Load().GameFolder == first && ReferenceEquals(page.Model, model) &&
                       ReferenceEquals(page.Model?.Session, session) && page.X.Text == "181" && page.TriggerRadius.HasDraft,
                       "unapplied coordinate text also cancels folder publication before editor or remembered-folder replacement");
            page.TriggerRadius.UseStoredRadius.EmitSignal(BaseButton.SignalName.Pressed);
            byte[] beforeEscape = session.ToBytes();
            check.That(page.CoordinatesHaveDraft && page.HasChanges && !page.RequestProjectSave(Path.Combine(scratch, "unapplied-coordinate" + EditorProjectFiles.Extension)) &&
                       page.ProjectMessage.Contains("coordinate edits", StringComparison.OrdinalIgnoreCase),
                       "unapplied coordinate text is explicitly unsaved and refuses project capture without a file write");
            using InputEventKey escape = new() { Pressed = true, Keycode = Key.Escape };
            page.X.EmitSignal(Control.SignalName.GuiInput, escape);
            check.That(!page.CoordinatesHaveDraft && !page.HasChanges && session.ToBytes().AsSpan().SequenceEqual(beforeEscape) && !page.SaveProject.Disabled,
                       "Escape restores current coordinate text without changing the world or history and enables project capture again");
            check.That(external == 0, "the folder-scan witness launches no game, external navigation or quit");
        }
        finally
        {
            release.Set(); app.Game.BeforeChooseReadForTest = null;
            for (int i = 0; i < 300 && app.Game.Busy; i++) await LevelTriggerInspectorPageTests.Frames(tree, 1);
            app.QueueFree(); await LevelTriggerInspectorPageTests.Frames(tree);
        }
    }
}
