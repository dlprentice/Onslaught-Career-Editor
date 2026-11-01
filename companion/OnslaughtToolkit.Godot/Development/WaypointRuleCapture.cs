// SPDX-License-Identifier: GPL-3.0-only
using Godot;
using OnslaughtToolkit.Companion.Tests;
using OnslaughtToolkit.Companion.Ui;

namespace OnslaughtToolkit.Companion.Development;

/// <summary>Actual result controls on authored source and worlds; no compile, publication or launch.</summary>
public partial class WaypointRuleCapture : SceneTree
{
    public override void _Initialize() => _ = CaptureAsync();

    private async Task CaptureAsync()
    {
        int code = 1;
        SubViewport? viewport = null;
        WaypointRulePageTests.Fixture? fixture = null;
        try
        {
            string output = OS.GetCmdlineUserArgs().FirstOrDefault(argument => argument.StartsWith("--output-dir=", StringComparison.Ordinal))?["--output-dir=".Length..]
                ?? throw new ArgumentException("An owned --output-dir is required.");
            Directory.CreateDirectory(output);
            Vector2I size = new(1440, 900);
            fixture = await WaypointRulePageTests.CreateAsync(this, Path.Combine(OS.GetUserDataDir(), "waypoint-rule-capture"), size);
            viewport = new SubViewport { Size = size, RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
            Root.AddChild(viewport);
            ColorRect background = new() { Color = Palette.Background, Size = size, MouseFilter = Control.MouseFilterEnum.Ignore };
            viewport.AddChild(background);
            LevelEditorPage page = fixture.Page;
            Root.RemoveChild(page.Root); viewport.AddChild(page.Root);
            if (!page.ShowScript(page.Model!.Session!.Body.Scripts[0].Name)) throw new InvalidDataException("Authored source unavailable.");
            page.EditSource.ButtonPressed = true;
            page.Scripts.Source.Text = WaypointRulePageTests.DraftFor(page.Model.Session.Body);
            page.CheckWaypointRules.EmitSignal(BaseButton.SignalName.Pressed);
            if (page.WaypointRules is not { Calls: 3, Resolved: 1, Unresolved: 1, Unchecked: 1 }) throw new InvalidDataException("Authored result unavailable.");
            await Shot(viewport, output, "wide-waypoint-rules");
            size = new(1024, 768); viewport.Size = size; page.Root.Size = size; background.Size = size;
            page.RunWaypointRuleCheck();
            await Shot(viewport, output, "compact-waypoint-rules");
            GD.Print("WAYPOINT_RULE_CAPTURE: two authored result-panel captures; no compile, publication or launch.");
            code = 0;
        }
        catch (Exception error) { GD.PrintErr("WAYPOINT_RULE_CAPTURE stopped: " + error.GetType().Name); }
        finally
        {
            if (fixture is not null) await WaypointRulePageTests.DisposeAsync(this, fixture);
            if (viewport is not null) { viewport.QueueFree(); await LevelTriggerInspectorPageTests.Frames(this); }
            Quit(code);
        }
    }

    private async Task Shot(SubViewport viewport, string output, string name)
    {
        await LevelTriggerInspectorPageTests.Frames(this, 5);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        using Image image = viewport.GetTexture().GetImage();
        if (image.SavePng(Path.Combine(output, name + ".png")) != Error.Ok) throw new IOException("Authored capture could not be saved.");
    }
}
