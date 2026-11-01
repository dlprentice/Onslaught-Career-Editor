// SPDX-License-Identifier: GPL-3.0-only
using System.Text;
using System.Text.Json.Nodes;
using Godot;
using OnslaughtToolkit.Companion.Careers;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Game;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Real project page actions on authored archives and sources only, including asynchronous failure and confirmation races.</summary>
internal static class EditorProjectPageTests
{
    private sealed class ControlledFiles : IEditorProjectFiles
    {
        internal readonly EditorProjectFiles Real = new();
        internal bool FailRead, FailWrite, UncertainWrite, BlockRead, BlockWrite;
        internal int Reads, Writes;
        internal TaskCompletionSource<bool> Started = new(TaskCreationOptions.RunContinuationsAsynchronously);
        internal ManualResetEventSlim Release = new(false);
        internal void Block(bool write)
        {
            Started = new(TaskCreationOptions.RunContinuationsAsynchronously);
            Release = new(false);
            BlockWrite = write; BlockRead = !write;
        }
        private void Wait()
        {
            Started.TrySetResult(true);
            if (!Release.Wait(TimeSpan.FromSeconds(10))) throw new IOException("Authored test gate timed out.");
        }
        public EditorProjectRead Open(string path)
        {
            Interlocked.Increment(ref Reads);
            if (BlockRead) { BlockRead = false; Wait(); }
            return FailRead ? new(false, "Authored read refusal.") : Real.Open(path);
        }
        public EditorProjectWrite WriteNew(string path, byte[] bytes, IReadOnlyList<string?> protectedFolders)
        {
            Interlocked.Increment(ref Writes);
            if (BlockWrite) { BlockWrite = false; Wait(); }
            return FailWrite || UncertainWrite ? new(false, "Authored write refusal.", MayHaveOutput: UncertainWrite) : Real.WriteNew(path, bytes, protectedFolders);
        }
    }

    private static SignalAwaiter Frame(SceneTree tree) => tree.ToSignal(tree, SceneTree.SignalName.ProcessFrame);
    private static void ConfirmSave(LevelEditorPage page)
    {
        page.ProjectSaveConfirm.EmitSignal(ConfirmationDialog.SignalName.Confirmed);
        page.ProjectSaveConfirm.Hide();
    }

    internal static async Task RunAsync(SceneTree tree, string output, Checks check)
    {
        check.Suite("editor project page");
        string scratch = Path.Combine(output, "project-page"), projects = Path.Combine(scratch, "projects");
        Directory.CreateDirectory(projects);
        string gameRoot = LevelEditorTests.GameWithLevels(scratch);
        File.WriteAllText(Path.Combine(gameRoot, "BEA.exe"), "Authored editor fixture; not an executable.");
        string archive = Path.Combine(gameRoot, "data", "resources", "100_res_PC.aya");
        File.WriteAllBytes(archive, AuthoredTerrainFixture.WithAuthoredTerrain(File.ReadAllBytes(archive)));
        AuthoredTerrainFixture.AddDraftSources(gameRoot);
        string[] originalFiles = LevelEditorPageTests.Snapshot(gameRoot);
        SettingsStore settings = new(Path.Combine(scratch, "settings.json"));
        GameLibrary game = new([], settings, ceUserFolder: Path.Combine(scratch, "unused-ce"), ceEnvironment: _ => null);
        typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, GameFolder.Inspect(gameRoot, "Authored project fixture"));
        ControlledFiles files = new();
        Action? discard = null;
        int external = 0;
        Control popups = new();
        AppServices services = new()
        {
            Workspace = new CareerWorkspace(new SaveFileWorker(new ProtectedSaveFiles())), EditorProjects = files,
            Game = game, Status = new StatusLine(), Backups = new(settings, Path.Combine(scratch, "unused-backups")), GameRunning = () => false,
            OpenUrl = _ => external++, Navigate = _ => external++, OpenCareer = null!, ChooseCareer = null!, OpenCareerFile = () => external++,
            AskToDiscard = (_, _, action) => discard = action, LevelEditsUnsaved = () => 0,
            Play = new CePlay(game, Path.Combine(scratch, "unused-play")), Popups = popups, CatchUp = () => Task.CompletedTask,
        };
        void ConfirmOpen() { Action? action = discard; discard = null; action?.Invoke(); }
        Theme theme = CompanionTheme.Build();
        LevelEditorPage page = new(services);
        page.Root.Theme = theme;
        page.Root.Size = new Vector2(1280, 800);
        await Frame(tree);
        tree.Root.AddChild(popups); tree.Root.AddChild(page.Root);
        try
        {
            page.Refresh();
            await Frame(tree);
            LevelEditorModel model = page.Model!;
            if (model.Session is not { } session || session.Body.Scripts.Count == 0) { check.Fail("the authored project level has a script"); return; }
            string name = session.Body.Scripts[0].Name;
            string PathFor(string file) => Path.Combine(projects, file + EditorProjectFiles.Extension);
            page.TerrainViewSwitch.ButtonPressed = true;
            check.That(page.WorldNote.Contains("even before editing", StringComparison.Ordinal) && page.WorldNote.Contains("unverified ground clearance", StringComparison.Ordinal),
                       "ordinary unchanged 3D terrain persistently warns that preview placement does not verify ground clearance");
            check.That(model.Move(0, "12", "24", "3").Result == MoveResult.Moved && !model.TerrainHasChanges && !page.Save.Disabled &&
                       page.WorldNote.Contains("unverified ground clearance", StringComparison.Ordinal),
                       "a valid object move leaves the unchanged-preview accuracy warning visible while ordinary object export remains available");
            page.Save.EmitSignal(BaseButton.SignalName.Pressed);
            page.SaveDialog.Destination.Text = projects; page.SaveDialog.Id.Text = "stale-mod-session";
            page.OpenLevel(100);
            page.SaveDialog.EmitSignal(ConfirmationDialog.SignalName.Confirmed); page.SaveDialog.Hide();
            check.That(!Directory.Exists(Path.Combine(projects, "stale-mod-session")) && services.Status.Failed,
                       "a mod SaveDialog confirmation from a replaced session refuses before creating a mod folder");
            model.Move(0, "12", "24", "3");
            page.ShowScript(name); page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = "// draft before mod confirmation\n";
            page.Save.EmitSignal(BaseButton.SignalName.Pressed);
            page.SaveDialog.Destination.Text = projects; page.SaveDialog.Id.Text = "stale-mod-draft";
            page.Scripts.Source.Text = "// dirty draft after mod confirmation\n";
            page.SaveDialog.EmitSignal(ConfirmationDialog.SignalName.Confirmed); page.SaveDialog.Hide();
            check.That(!Directory.Exists(Path.Combine(projects, "stale-mod-draft")) && page.Scripts.SourceText == "// dirty draft after mod confirmation\n" && services.Status.Failed,
                       "dirty-to-dirty source typing invalidates the real mod SaveDialog confirmation without losing the draft");
            page.Scripts.Source.Text = "// saved authored draft\n";
            check.That(model.BeginTerrainPreview(out _) &&
                       model.ChangeTerrainPreview(256, 256, true).Result == MoveResult.Moved, "the authored project has a world move, source draft and sampled terrain edit");
            byte[] savedWorld = model.Session!.ToBytes();
            string first = PathFor("first");
            check.That(page.RequestProjectSave(first) && page.ProjectSaveConfirm.DialogText.Contains("Source text from your installation", StringComparison.Ordinal) &&
                       page.ProjectSaveConfirm.DialogText.Contains("not a format CE loads", StringComparison.Ordinal), "the chosen path receives an explicit contents and editor-only format notice");
            ConfirmSave(page); await page.ProjectOperation;
            byte[] project = File.ReadAllBytes(first);
            check.That(!services.Status.Failed && !page.HasChanges && model.TerrainHasChanges && page.Save.Disabled && page.Play.Disabled &&
                       originalFiles.SequenceEqual(LevelEditorPageTests.Snapshot(gameRoot)), "a verified new project preserves every edit, clears project dirtiness and leaves source inputs and terrain export fences intact");
            check.That(page.RequestProjectSave(first), "the same chosen project path can be checked again");
            ConfirmSave(page); await page.ProjectOperation;
            check.That(services.Status.Failed && File.ReadAllBytes(first).AsSpan().SequenceEqual(project) && model.Session.ToBytes().AsSpan().SequenceEqual(savedWorld),
                       "an existing project refuses overwrite while preserving the current world and original project bytes");
            page.Scripts.Source.Text = "// draft before save confirmation\n";
            string staleSave = PathFor("stale-save");
            page.RequestProjectSave(staleSave);
            page.Scripts.Source.Text = "// newer dirty draft\n";
            ConfirmSave(page); await page.ProjectOperation;
            check.That(!File.Exists(staleSave) && page.Scripts.SourceText == "// newer dirty draft\n" && page.HasChanges,
                       "dirty-to-dirty typing invalidates save confirmation before any file is created");
            string replaced = PathFor("replaced-session");
            page.RequestProjectSave(replaced);
            page.OpenLevel(100);
            ConfirmSave(page); await page.ProjectOperation;
            check.That(!File.Exists(replaced) && !ReferenceEquals(session, model.Session), "a replaced session invalidates pending save confirmation");

            page.ShowScript(name); page.EditSource.ButtonPressed = true;
            string sourcePath = page.Scripts.CurrentSource!.Source!.Path;
            File.WriteAllText(sourcePath, "// externally changed authored source\n");
            page.OpenLevel(100); page.ShowScript(name); page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = "// current unsaved source\n";
            await page.OpenProjectAsync(first);
            EditSession beforeOpen = model.Session!;
            page.Scripts.Source.Text = "// source typed after open confirmation\n";
            ConfirmOpen(); await page.ProjectOperation;
            check.That(ReferenceEquals(model.Session, beforeOpen) && page.Scripts.SourceText == "// source typed after open confirmation\n" &&
                       File.ReadAllBytes(first).AsSpan().SequenceEqual(project), "dirty-to-dirty typing invalidates open confirmation and leaves the chosen project untouched");
            await page.OpenProjectAsync(first);
            model.Move(0, "16", "25", "4");
            byte[] afterMove = model.Session!.ToBytes();
            ConfirmOpen(); await page.ProjectOperation;
            check.That(ReferenceEquals(model.Session, beforeOpen) && model.Session.ToBytes().AsSpan().SequenceEqual(afterMove),
                       "an intervening world edit invalidates open confirmation without losing that edit");
            await page.OpenProjectAsync(first);
            page.OpenLevel(100);
            EditSession replacement = model.Session!;
            ConfirmOpen(); await page.ProjectOperation;
            check.That(ReferenceEquals(model.Session, replacement), "replacing the session invalidates a pending open even for the same base level");
            await page.OpenProjectAsync(first);
            page.ShowScript(name);
            check.That(!ReferenceEquals(model.Session, replacement) && model.Session!.ToBytes().AsSpan().SequenceEqual(savedWorld) && model.TerrainHasChanges &&
                       model.Session is { CanUndo: false, CanRedo: false } && page.Scripts.SourceText == "// saved authored draft\n" &&
                       page.Scripts.CurrentSourceFromProject && page.Scripts.Editing && !page.EditSource.Disabled && !page.CompileScriptButton.Disabled && !page.HasChanges,
                       "a portable project restores world bytes, sampled terrain and source draft despite a changed installed source, with a fresh undo history");
            JsonObject claimed = JsonNode.Parse(project)!.AsObject();
            claimed["scripts"]![0]!["used_text"] = "// retained unverified source claim\n";
            claimed["scripts"]![0]!["used_record_sha256"] = EditorProject.Hash(WorldBodyWriter.ScriptBytes(model.Session!.Body.Scripts[0]));
            string claimedPath = PathFor("unverified-source");
            files.Real.WriteNew(claimedPath, Encoding.UTF8.GetBytes(claimed.ToJsonString()), []);
            await page.OpenProjectAsync(claimedPath);
            check.That(page.SourceInUse(name) is null && page.Scripts.CaptureProjectScripts(model.Session!).First().UsedText == "// retained unverified source claim\n" &&
                       page.Scripts.SourceText == "// saved authored draft\n", "a project keeps a separate unverified compiled-source claim without labeling it in use or losing the current draft");
            string[] afterExternalChange = LevelEditorPageTests.Snapshot(gameRoot);
            EditSession restored = model.Session!;
            files.FailRead = true;
            await page.OpenProjectAsync(first);
            files.FailRead = false;
            check.That(services.Status.Failed && ReferenceEquals(model.Session, restored) && page.Scripts.SourceText == "// saved authored draft\n",
                       "a failed project read keeps the restored world and source draft");
            JsonObject old = JsonNode.Parse(project)!.AsObject(); old["version"] = 1;
            foreach (JsonNode? entry in old["scripts"]!.AsArray()) entry!.AsObject().Remove("source");
            byte[] oldBytes = Encoding.UTF8.GetBytes(old.ToJsonString());
            string oldPath = PathFor("old-version");
            files.Real.WriteNew(oldPath, oldBytes, []);
            await page.OpenProjectAsync(oldPath);
            check.That(ReferenceEquals(model.Session, restored) && page.ProjectMessage.Contains("Version 1", StringComparison.Ordinal) &&
                       File.ReadAllBytes(oldPath).AsSpan().SequenceEqual(oldBytes), "opening a version 1 project explicitly refuses missing source text without changing either editor or file");
            page.Scripts.Source.Text = "// draft retained after write failure\n";
            files.FailWrite = true;
            page.RequestProjectSave(PathFor("failed-write")); ConfirmSave(page); await page.ProjectOperation;
            files.FailWrite = false;
            check.That(services.Status.Failed && page.HasChanges && ReferenceEquals(model.Session, restored) && page.Scripts.SourceText == "// draft retained after write failure\n",
                       "a failed project write leaves the complete current edit dirty and unchanged");
            files.UncertainWrite = true;
            page.RequestProjectSave(PathFor("uncertain-write")); ConfirmSave(page); await page.ProjectOperation;
            files.UncertainWrite = false;
            check.That(services.Status.Failed && page.HasChanges && page.Scripts.SourceText == "// draft retained after write failure\n",
                       "an uncertain publication never marks the current project saved");
            discard = null;
            files.Block(write: false);
            Task reading = page.OpenProjectAsync(first);
            await files.Started.Task;
            page.Scripts.Source.Text = "// source typed during read\n";
            files.Release.Set(); await reading;
            check.That(discard is null && ReferenceEquals(model.Session, restored) && page.Scripts.SourceText == "// source typed during read\n",
                       "typing while a read is in flight refuses the obsolete import before confirmation");
            files.Block(write: true);
            string whileWriting = PathFor("typing-during-write"), confirmedText = page.Scripts.SourceText;
            page.RequestProjectSave(whileWriting); ConfirmSave(page);
            await files.Started.Task;
            page.Scripts.Source.Text = "// newer text during write\n";
            files.Release.Set(); await page.ProjectOperation;
            LevelWorlds worlds = model.Worlds!;
            EditorProjectBase basis = new(100, false, worlds.BaseLevel, model.Session!.IsBaseWorld, model.Session.Baseline,
                worlds.RealBody!, worlds.BaseBody, worlds.Terrain);
            RestoredEditorProject earlier = EditorProject.Restore(File.ReadAllBytes(whileWriting), basis);
            check.That(earlier.Scripts.Single(script => script.Name == name).DraftText == confirmedText && page.Scripts.SourceText == "// newer text during write\n" &&
                       page.HasChanges && page.ProjectMessage.Contains("Newer edits remain unsaved", StringComparison.Ordinal),
                       "a completed write verifies the confirmed snapshot while preserving and retaining dirtiness for text typed later");
            string changedFile = PathFor("changed-file");
            files.Real.WriteNew(changedFile, project, []);
            await page.OpenProjectAsync(changedFile);
            File.WriteAllBytes(changedFile, [.. project, (byte)' ']);
            ConfirmOpen(); await page.ProjectOperation;
            check.That(ReferenceEquals(model.Session, restored) && page.Scripts.SourceText == "// newer text during write\n" && services.Status.Failed,
                       "a changed project file between read and confirmation refuses without replacing the current edit");
            check.That(afterExternalChange.SequenceEqual(LevelEditorPageTests.Snapshot(gameRoot)) && File.ReadAllBytes(first).AsSpan().SequenceEqual(project) && external == 0,
                       "project workflows never alter authored source inputs or the original project, and never launch or navigate externally");
            page.OpenLevel(100);
            EditSession unstorableSession = model.Session!;
            MissionScript unstorable = unstorableSession.ShippedScript(0);
            unstorable.Trailer = new byte[9];
            unstorableSession.Apply(new ReplaceScript(0, unstorable));
            discard = null;
            page.PickLevel(200);
            check.That(discard is not null && model.Level == 100 && ReferenceEquals(model.Session, unstorableSession) && page.HasChanges,
                       "the level picker asks before dropping an unstorable script edit");
            unstorableSession.Body.Scripts[0].Trailer[0] = 1;
            ConfirmOpen();
            check.That(model.Level == 100 && ReferenceEquals(model.Session, unstorableSession) && unstorableSession.Body.Scripts[0].Trailer[0] == 1,
                       "a raw change to an unstorable edit invalidates pending discard even without a model notification");
            page.PickLevel(200); ConfirmOpen();
            check.That(model.Level == 200 && !ReferenceEquals(model.Session, unstorableSession), "an exact confirmed unsupported edit can be explicitly discarded");
            string radiusGame = LevelTriggerInspectorPageTests.CreateGame(Path.Combine(scratch, "radius-guard"));
            typeof(GameLibrary).GetProperty(nameof(GameLibrary.Folder))!.SetValue(game, GameFolder.Inspect(radiusGame, "Authored radius fixture"));
            page.Refresh(); page.ShowObject(0);
            LevelTriggerInspectorPageTests.Type(page, "7");
            int reads = files.Reads, writes = files.Writes;
            bool acceptedRadius = page.RequestProjectSave(PathFor("unapplied-radius"));
            await page.OpenProjectAsync(first);
            await page.PlayAsync();
            check.That(page.Save.Disabled && page.Play.Disabled && !acceptedRadius && files.Reads == reads && files.Writes == writes && page.TriggerRadius.HasDraft &&
                       page.ProjectMessage.Contains("unapplied trigger-radius draft", StringComparison.Ordinal),
                       "unapplied radius drafts explicitly refuse project save and open before any file operation");
        }
        finally
        {
            page.Root.QueueFree(); popups.QueueFree(); services.Status.Root.QueueFree();
            await Frame(tree);
            theme.Dispose();
        }
    }
}
