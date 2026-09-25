// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Headless checks of the actual production scene and its native transforms.</summary>
public sealed partial class HudSceneChecks : Node
{
    private int _checks;
    private string? _captureDirectory;

    public override async void _Ready()
    {
        try
        {
            string? captureOption = OS.GetCmdlineUserArgs().FirstOrDefault(
                value => value.StartsWith("--hud-scene-capture-dir=", StringComparison.Ordinal));
            if (captureOption is not null)
            {
                _captureDirectory = captureOption["--hud-scene-capture-dir=".Length..];
                if (!Path.IsPathFullyQualified(_captureDirectory) || !Directory.Exists(_captureDirectory))
                    throw new InvalidOperationException("Capture directory must be an existing absolute task-owned path.");
            }
            Input.MouseModeEnum pointerBefore = Input.MouseMode;
            var view = FirstFlightHud.Create(Level100HudAssetCatalog.Load());
            var stage = view.GetNode<Control>("Surface/DesignStage");
            var parts = view.FindChildren("*", nameof(Control), true, false).OfType<RetailHudPart>().ToArray();
            Check(parts.Length == 22, "Twenty-two production instruments exist before entering the tree.");
            Check(stage.GetChildren().Select(node => node.Name.ToString()).SequenceEqual(["Base", "Glow", "Text"]),
                "The three blend layers retain their explicit order.");
            Check(stage.GetChildren().Cast<Control>().All(group => !group.UseParentMaterial && group.Material is ShaderMaterial),
                "Each layer owns its explicit blend material.");
            Check(parts.All(part => part.UseParentMaterial), "Instruments inherit their layer's material.");
            Check(parts.Select(part => part.Part).Distinct().Count() == 22, "Each drawing law has one scene owner.");
            Check(view.FindChildren("*", nameof(TextureRect), true, false).Count == 6,
                "Static backing and the three crosshair quads are native texture controls.");
            Check(view.IsReadyForSmoke, "The same production assets and all three drawing owners are ready.");
            Check(!view.GetNode<Control>("Surface").Visible, "No editor illustration leaks into the runtime factory.");

            var viewport = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true,
                RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
            AddChild(viewport);
            viewport.AddChild(view);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Near(stage.Scale.X, 1f, "640x480 is the identity letterbox.");
            Check(stage.Position == Vector2.Zero, "The identity stage has no offset.");
            var scanner = view.GetNode<TextureRect>("Surface/DesignStage/Base/ScannerBackdrop");
            Check(scanner.Position == new Vector2(17, 368) && scanner.Size == new Vector2(128, 128),
                "Native scanner rectangle retains the measured retail baseline.");
            Check(scanner.Texture is HudTexturePage && scanner.Texture.GetSize() == new Vector2(128, 128),
                "Native texture uses a reusable recipe for the actual private page.");
            Check(scanner.Texture.GetImage().GetWidth() == 128, "The production private texture decodes.");
            var right = view.GetNode<TextureRect>("Surface/DesignStage/Base/RightWeaponBacking");
            Check(right.FlipH && right.Position == new Vector2(499, 339), "Right backing retains the measured mirror.");
            var crosshair = view.GetNode<Control>("Surface/DesignStage/Base/Crosshair");
            Check(crosshair.GetChildren().Select(node => node.Name.ToString()).SequenceEqual(["Primary", "Secondary", "Dot"]),
                "Crosshair native quads preserve the measured 64/128/64 issue order.");
            Near(crosshair.GetNode<TextureRect>("Primary").SelfModulate.A, 0.6863f, "Primary crosshair alpha.");
            Near(crosshair.GetNode<TextureRect>("Secondary").SelfModulate.A, 0.3412f, "Secondary crosshair alpha.");
            Near(crosshair.GetNode<TextureRect>("Dot").SelfModulate.A, 0.3412f, "Dot alpha.");

            var compass = view.GetNode<RetailHudPart>("Surface/DesignStage/Base/Compass");
            Vector2 measuredCenter = new(320, 240);
            NearVector(compass.GetTransform() * (compass.RetailToLocalTransform() * measuredCenter),
                measuredCenter, "Measured coordinates map onto the native rectangle.");
            compass.Position += new Vector2(37, -12);
            NearVector(compass.GetTransform() * (compass.RetailToLocalTransform() * measuredCenter),
                measuredCenter + new Vector2(37, -12), "Native Position edits move the actual draw coordinates.");
            compass.Size *= 1.5f;
            NearVector(compass.RetailToLocalTransform() * measuredCenter, new Vector2(192, 192),
                "Native Size edits resize the actual draw coordinates.");
            compass.Rotation = 0.25f;
            Vector2 mapped = compass.GetTransform() * (compass.RetailToLocalTransform() * measuredCenter);
            NearVector(mapped, compass.Position + new Vector2(192, 192).Rotated(0.25f),
                "Native rotation composes with the measured coordinate mapping.");
            compass.Position = new Vector2(192, 112);
            compass.Size = new Vector2(256, 256);
            compass.Rotation = 0;

            // The test drives the ordinary snapshot API; the view never creates
            // a session and the editor illustration never enters this branch.
            var session = new InteractiveSession(0x4F4E534Cu, Level100StaticWorldAsset.LoadActorDefinitions());
            view.UpdateFromSnapshot(session.CurrentSnapshot,
                new Level100MessagePlaybackState(null, null, 0d, 0d, false, false));
            Check(view.GetNode<Control>("Surface").Visible, "A real snapshot opens the runtime HUD.");
            Check(view.Level100Energy == session.CurrentSnapshot.Energy &&
                view.Level100Health == session.CurrentSnapshot.Hull, "Snapshot values reach the existing gauge laws.");
            Check(view.Level100DeliveredMessageCount == 0, "Presentation initialization fabricates no message events.");
            Check(Input.MouseMode == pointerBefore, "HUD initialization and updates do not take pointer ownership.");
            await Capture(viewport, "hud-native.png");

            var packed = new PackedScene();
            Check(packed.Pack(view) == Error.Ok, "Production scene can be packed after asset binding.");
            var visited = new HashSet<ulong>();
            SceneState state = packed.GetState();
            for (int node = 0; node < state.GetNodeCount(); node++)
                for (int property = 0; property < state.GetNodePropertyCount(node); property++)
                    CheckStoredValue(state.GetNodePropertyValue(node, property), visited);

            viewport.Size = new Vector2I(1280, 720);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Near(stage.Scale.X, 1.5f, "Widescreen retains the measured whole-stage scaling.");
            NearVector(stage.Position, new Vector2(160, 0), "Widescreen remains centered.");
            Check(Input.MouseMode == pointerBefore, "Layout changes leave pointer ownership alone.");
            await Capture(viewport, "hud-widescreen.png");
            GD.Print($"HUD_SCENE_CHECKS: {_checks} passed; authored content, production assets, transforms, blend order, snapshot handoff and serialization boundary.");
            viewport.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private async Task Capture(SubViewport viewport, string filename)
    {
        if (_captureDirectory is null)
            return;
        string destination = Path.Combine(_captureDirectory, filename);
        if (File.Exists(destination))
            throw new InvalidOperationException("Refusing to overwrite an existing scene capture.");
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        Check(viewport.GetTexture().GetImage().SavePng(destination) == Error.Ok,
            $"Saved task-owned capture {filename}.");
    }

    private void CheckStoredValue(Variant value, HashSet<ulong> visited)
    {
        if (value.VariantType != Variant.Type.Object || value.AsGodotObject() is not Resource resource ||
            !visited.Add(resource.GetInstanceId()))
            return;
        Check(resource is not Image && resource is not ImageTexture,
            "Saving public scene/resource definitions cannot embed decoded private pixels.");
        foreach (Godot.Collections.Dictionary property in resource.GetPropertyList())
        {
            if ((property["usage"].As<PropertyUsageFlags>() & PropertyUsageFlags.Storage) != 0)
                CheckStoredValue(resource.Get(property["name"].AsStringName()), visited);
        }
    }

    private void Check(bool condition, string description)
    {
        if (!condition) throw new InvalidOperationException(description);
        _checks++;
    }
    private void Near(float actual, float expected, string description) =>
        Check(Math.Abs(actual - expected) < 0.0001f, $"{description} Expected {expected}, got {actual}.");
    private void NearVector(Vector2 actual, Vector2 expected, string description) =>
        Check(actual.DistanceTo(expected) < 0.0001f, $"{description} Expected {expected}, got {actual}.");
}
