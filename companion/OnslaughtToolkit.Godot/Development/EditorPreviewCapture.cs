// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Fixed-size captures of the actual editor using authored fixtures only; no game, career, mod publication or external action.</summary>
public partial class EditorPreviewCapture : SceneTree
{
    public override void _Initialize() => _ = CaptureAsync();

    private async Task CaptureAsync()
    {
        int code = 1;
        SubViewport? viewport = null;
        try
        {
            string output = OS.GetCmdlineUserArgs().FirstOrDefault(argument => argument.StartsWith("--output-dir=", StringComparison.Ordinal))?["--output-dir=".Length..]
                ?? throw new ArgumentException("An owned --output-dir is required.");
            Directory.CreateDirectory(output);
            string scratch = Path.Combine(OS.GetUserDataDir(), "authored-editor-capture");
            string game = LevelTriggerInspectorPageTests.CreateGame(scratch);
            int external = 0;
            CompanionEnvironment environment = new([], Path.Combine(scratch, "settings.json"), GameRunning: () => false,
                OpenUrl: _ => external++, DefaultBackupFolder: Path.Combine(scratch, "unused-backups"), Quit: () => { },
                OldCopiesFolder: Path.Combine(scratch, "unused-copies"), CeUserFolder: Path.Combine(scratch, "unused-ce"));
            viewport = new SubViewport { Size = new Vector2I(1440, 900), RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
            await LevelTriggerInspectorPageTests.Frames(this, 1);
            Root.AddChild(viewport);
            CompanionApp app = new(null, managesWindow: false, environment);
            viewport.AddChild(app);
            for (int i = 0; i < 300 && app.Game.Busy; i++) await LevelTriggerInspectorPageTests.Frames(this, 1);
            if (!(await app.Game.ChooseAsync(game)).Ok) throw new InvalidDataException("The authored capture fixture did not open.");
            app.Navigate("levels");
            LevelEditorPage page = app.LevelEditor;
            page.SelectIndex(0);
            page.TerrainViewSwitch.ButtonPressed = true;
            LevelTriggerInspectorPageTests.Type(page, "8");
            await Shot(viewport, output, "wide-radius-draft");
            page.TriggerRadius.Apply.EmitSignal(BaseButton.SignalName.Pressed);
            await Shot(viewport, output, "wide-radius-applied");
            page.TerrainEdit.ButtonPressed = true;
            if (page.Model!.ChangeTerrainPreview(256, 256, true).Result != Levels.MoveResult.Moved)
                throw new InvalidDataException("The authored terrain preview edit was refused.");
            await Shot(viewport, output, "wide-preview-only-terrain");
            viewport.Size = new Vector2I(1024, 768);
            page.TriggerRadius.RadiusInput.GrabFocus();
            await Shot(viewport, output, "compact-preview-only-terrain");
            if (external != 0 || !page.Save.Disabled || !page.Play.Disabled || !page.TriggerRadius.Visible)
                throw new InvalidDataException("The capture did not retain the expected inspector and terrain guards.");
            GD.Print("EDITOR_PREVIEW_CAPTURE: 4 fixed-size authored UI captures; terrain Save/Play guards active; no external action.");
            code = 0;
        }
        catch (Exception error) { GD.PrintErr("EDITOR_PREVIEW_CAPTURE stopped: " + error); }
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
        Error result = image.SavePng(Path.Combine(output, name + ".png"));
        if (result != Error.Ok) throw new IOException("The authored UI capture could not be saved: " + result);
    }
}
