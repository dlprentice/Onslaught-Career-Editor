// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Files;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;
namespace OnslaughtToolkit.Companion.Development;

/// <summary>Actual companion project controls and notices on authored data only; no career, mod staging or launch.</summary>
public partial class EditorProjectCapture : SceneTree
{
    public override void _Initialize() => _ = CaptureAsync();
    private async Task CaptureAsync()
    {
        int code = 1;
        SubViewport? viewport = null;
        try
        {
            string output = OS.GetCmdlineUserArgs().FirstOrDefault(argument => argument.StartsWith("--output-dir=", StringComparison.Ordinal))?["--output-dir=".Length..]
                ?? throw new ArgumentException("An owned output folder is required.");
            Directory.CreateDirectory(output);
            string scratch = Path.Combine(OS.GetUserDataDir(), "authored-project-capture");
            string game = LevelEditorTests.GameWithLevels(scratch);
            File.WriteAllText(Path.Combine(game, "BEA.exe"), "Authored capture fixture; not an executable.");
            string archive = Path.Combine(game, "data", "resources", "100_res_PC.aya");
            File.WriteAllBytes(archive, AuthoredTerrainFixture.WithAuthoredTerrain(File.ReadAllBytes(archive)));
            AuthoredTerrainFixture.AddDraftSources(game);
            int external = 0;
            CompanionEnvironment environment = new([], Path.Combine(scratch, "settings.json"), GameRunning: () => false,
                OpenUrl: _ => external++, DefaultBackupFolder: Path.Combine(scratch, "unused-backups"), Quit: () => { },
                OldCopiesFolder: Path.Combine(scratch, "unused-copies"), CeUserFolder: Path.Combine(scratch, "unused-ce"));
            viewport = new SubViewport { Size = new Vector2I(1440, 900), RenderTargetUpdateMode = SubViewport.UpdateMode.Always, GuiEmbedSubwindows = true };
            await LevelTriggerInspectorPageTests.Frames(this, 1);
            Root.AddChild(viewport);
            CompanionApp app = new(new ProtectedSaveFiles(), managesWindow: false, environment);
            viewport.AddChild(app);
            for (int i = 0; i < 300 && app.Game.Busy; i++) await LevelTriggerInspectorPageTests.Frames(this, 1);
            if (!(await app.Game.ChooseAsync(game)).Ok) throw new InvalidDataException("The authored capture fixture did not open.");
            app.Navigate("levels");
            LevelEditorPage page = app.LevelEditor;
            page.SelectIndex(0); page.TerrainViewSwitch.ButtonPressed = true;
            page.Model!.Move(0, "12", "24", "3");
            await Shot(viewport, output, "wide-unchanged-preview-warning");
            string name = page.Model.Session!.Body.Scripts[0].Name;
            page.ShowScript(name); page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = "// Authored source draft preserved by an editor project.\n";
            page.ScriptsToggle.ButtonPressed = false;
            page.TerrainEdit.ButtonPressed = true;
            page.Model.ChangeTerrainPreview(256, 256, true);
            string chosen = Path.Combine(scratch, "authored-snapshot" + EditorProjectFiles.Extension);
            if (!page.RequestProjectSave(chosen)) throw new InvalidDataException("The authored project notice was refused.");
            await Shot(viewport, output, "wide-project-contents-notice");
            page.ProjectSaveConfirm.Hide();
            viewport.Size = new Vector2I(1024, 768);
            await Shot(viewport, output, "compact-project-controls-warning");
            page.ShowScript(name);
            await Shot(viewport, output, "compact-project-source-draft");
            if (external != 0 || !page.Save.Disabled || !page.Play.Disabled || page.SaveProject.Disabled)
                throw new InvalidDataException("The authored capture did not retain the project and terrain policies.");
            GD.Print("EDITOR_PROJECT_CAPTURE: 4 authored fixed-size full-app captures; no external action.");
            code = 0;
        }
        catch (Exception error) { GD.PrintErr("EDITOR_PROJECT_CAPTURE stopped: " + error.GetType().Name); }
        finally
        {
            if (viewport is not null) { viewport.QueueFree(); await LevelTriggerInspectorPageTests.Frames(this); }
            Quit(code);
        }
    }
    private async Task Shot(SubViewport viewport, string output, string name)
    {
        await LevelTriggerInspectorPageTests.Frames(this, 4);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image image = viewport.GetTexture().GetImage();
        if (image.SavePng(Path.Combine(output, name + ".png")) != Error.Ok) throw new IOException("The authored UI image could not be saved.");
    }
}
