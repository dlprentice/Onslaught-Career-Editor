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
            CanvasLayer presentation = view.Presentation;
            var stage = presentation.GetNode<Control>("Surface/DesignStage");
            var parts = presentation.FindChildren("*", nameof(Control), true, false).OfType<Control>()
                .Where(part => part.HasMethod("retail_to_local_transform")).ToArray();
            Check(parts.Length == 22, "Twenty-two production instruments exist before entering the tree.");
            Check(stage.GetChildren().Select(node => node.Name.ToString()).SequenceEqual(["Base", "Glow", "Text"]),
                "The three blend layers retain their explicit order.");
            Check(stage.GetChildren().Cast<Control>().All(group => !group.UseParentMaterial && group.Material is ShaderMaterial),
                "Each layer owns its explicit blend material.");
            Check(parts.All(part => part.UseParentMaterial), "Instruments inherit their layer's material.");
            Check(parts.Select(part => part.Get("part").AsInt32()).Distinct().Count() == 22, "Each drawing law has one scene owner.");
            Check(presentation.FindChildren("*", nameof(TextureRect), true, false).Count == 6,
                "Static backing and the three crosshair quads are native texture controls.");
            Check(view.IsReadyForSmoke, "The same production assets and all three drawing owners are ready.");
            foreach (int identity in Level100AudioCatalog.CharacterMessages.Select(item => item.MessageId)
                .Concat([int.MinValue, -1, 0, 1, int.MaxValue]).Distinct())
            {
                foreach (double elapsed in new[] { 0d, 0.05d, 0.1d, 0.15d, 0.2d, 0.3d, 0.35d,
                    0.9999999999d, 1d, 1.05d, 13.16d, 100000.05d })
                {
                    Check(presentation.Call("portrait_pose", identity, elapsed).AsInt32() == ExpectedPhase(identity, elapsed, true),
                        "Native portrait hash matches original uint behavior for catalog/signed-edge IDs and timer boundaries.");
                    Check(presentation.Call("noise_phase", identity, elapsed).AsInt32() == ExpectedPhase(identity, elapsed, false),
                        "Native noise hash matches original uint behavior for catalog/signed-edge IDs and timer boundaries.");
                }
            }
            Check(!presentation.GetNode<Control>("Surface").Visible, "No editor illustration leaks into the runtime factory.");

            var viewport = new SubViewport { Size = new Vector2I(640, 480), Disable3D = true,
                RenderTargetUpdateMode = SubViewport.UpdateMode.Always };
            AddChild(viewport);
            viewport.AddChild(view);
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            Near(stage.Scale.X, 1f, "640x480 is the identity letterbox.");
            Check(stage.Position == Vector2.Zero, "The identity stage has no offset.");
            var scanner = presentation.GetNode<TextureRect>("Surface/DesignStage/Base/ScannerBackdrop");
            Check(scanner.Position == new Vector2(17, 368) && scanner.Size == new Vector2(128, 128),
                "Native scanner rectangle retains the measured retail baseline.");
            Texture2D scannerTexture = scanner.Texture ?? throw new InvalidOperationException("Scanner has no texture recipe.");
            Check(scannerTexture.GetScript().As<Script>().ResourcePath ==
                "res://Scenes/Shared/retail_texture_page.gd" && scannerTexture.GetSize() == new Vector2(128, 128),
                "Native texture uses a reusable recipe for the actual private page.");
            Check(scannerTexture.GetImage().GetWidth() == 128, "The production private texture decodes.");
            var right = presentation.GetNode<TextureRect>("Surface/DesignStage/Base/RightWeaponBacking");
            Check(right.FlipH && right.Position == new Vector2(499, 339), "Right backing retains the measured mirror.");
            var crosshair = presentation.GetNode<Control>("Surface/DesignStage/Base/Crosshair");
            Check(crosshair.GetChildren().Select(node => node.Name.ToString()).SequenceEqual(["Primary", "Secondary", "Dot"]),
                "Crosshair native quads preserve the measured 64/128/64 issue order.");
            Near(crosshair.GetNode<TextureRect>("Primary").SelfModulate.A, 0.6863f, "Primary crosshair alpha.");
            Near(crosshair.GetNode<TextureRect>("Secondary").SelfModulate.A, 0.3412f, "Secondary crosshair alpha.");
            Near(crosshair.GetNode<TextureRect>("Dot").SelfModulate.A, 0.3412f, "Dot alpha.");

            var compass = presentation.GetNode<Control>("Surface/DesignStage/Base/Compass");
            Vector2 measuredCenter = new(320, 240);
            NearVector(compass.GetTransform() * (compass.Call("retail_to_local_transform").AsTransform2D() * measuredCenter),
                measuredCenter, "Measured coordinates map onto the native rectangle.");
            compass.Position += new Vector2(37, -12);
            NearVector(compass.GetTransform() * (compass.Call("retail_to_local_transform").AsTransform2D() * measuredCenter),
                measuredCenter + new Vector2(37, -12), "Native Position edits move the actual draw coordinates.");
            compass.Size *= 1.5f;
            NearVector(compass.Call("retail_to_local_transform").AsTransform2D() * measuredCenter, new Vector2(192, 192),
                "Native Size edits resize the actual draw coordinates.");
            compass.Rotation = 0.25f;
            Vector2 mapped = compass.GetTransform() * (compass.Call("retail_to_local_transform").AsTransform2D() * measuredCenter);
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
            Check(presentation.GetNode<Control>("Surface").Visible, "A real snapshot opens the runtime HUD.");
            Check(view.Level100Energy == session.CurrentSnapshot.Energy &&
                view.Level100Health == session.CurrentSnapshot.Hull, "Snapshot values reach the existing gauge laws.");
            Check(view.Level100DeliveredMessageCount == 0, "Presentation initialization fabricates no message events.");
            Check(Input.MouseMode == pointerBefore, "HUD initialization and updates do not take pointer ownership.");
            await Capture(viewport, "hud-native.png");

            // Exercise the new production model boundary against the retained
            // C# oracle, including message visibility, gap socket and phases.
            var reference = new Level100HudPresentationState(Level100StaticWorldAsset.LoadAuthoredAllegiance());
            int messageId = Level100AudioCatalog.CharacterMessages[0].MessageId;
            Level100MissionEvent[] events = [new Level100MessageRequested(0,
                (int)Level100HudSpeaker.Tatiana, messageId, false, 60),
                new Level100HelpRequested(0, (int)Level100HudHelpPrompt.Fire)];
            reference.Consume(events);
            view.ConsumeMissionEvents(events);
            foreach (int tick in new[] { 0, 1, 2, 3, 4, 7, 10, 20, 40, 56, 57, 59, 60, 61, 63, 64 })
            {
                WorldSnapshot sample = session.CurrentSnapshot with { Tick = tick,
                    Level100Mission = session.CurrentSnapshot.Level100Mission with { Tick = tick } };
                var playback = new Level100MessagePlaybackState(null, null, 900d, 1d, false, false);
                Level100HudSnapshot expected = reference.Project(sample, playback);
                view.UpdateFromSnapshot(sample, playback);
                var actual = presentation.Call("snapshot").AsGodotDictionary();
                var actualHud = actual["hud"].AsGodotDictionary();
                Check(actualHud["contacts"].AsGodotArray().Count == expected.Contacts.Count &&
                    view.Level100ObjectiveMarkerCount == expected.Objectives.Count,
                    "Native production model projects the same actor facts as the retained reference.");
                Check(view.Level100DeliveredMessageIds.SequenceEqual(expected.DeliveredMessages.Select(item => item.MessageId)) &&
                    view.Level100DeliveredHelpCount == expected.DeliveredHelp.Count,
                    "Production delivery histories preserve original event order.");
                var entry = Level100MessageSchedule.ActiveAt(expected.DeliveredMessages, tick);
                Check(view.Level100MessagePlaybackAvailable == entry.HasValue,
                    "Native reveal follows Core mission ticks, not the supplied mixer position.");
                int expectedNoise = entry.HasValue ? ExpectedPhase(messageId, entry.Value.ElapsedSecondsAt(tick), false) : 0;
                Check(actual["noise_phase"].AsInt32() == expectedNoise, "Noise phase preserves the original unsigned hash.");
                if (entry.HasValue)
                    Check(actual["portrait_pose"].AsInt32() == ExpectedPhase(messageId, entry.Value.ElapsedSecondsAt(tick), true),
                        "Portrait phase preserves the original float boundary and unsigned hash.");
                else
                    Check(actual["portrait_pose"].VariantType == Variant.Type.Nil,
                        "The promote gap invents no portrait pose.");
                Check(view.Level100LowerRightSocket == Level100HudLowerRightSocketLaw.Select(
                    Level100MessageSchedule.MessageBoxHoldsActiveMessage(expected.DeliveredMessages, tick), expected.BattleLine.InfluenceMap),
                    "Native production socket retains message and influence ordering.");
            }
            view.UpdateFromSnapshot(session.CurrentSnapshot,
                new Level100MessagePlaybackState(null, null, 0d, 0d, false, false));
            Check(view.Level100DeliveredMessageCount == 0, "A backwards mission restart clears the native delivery history.");
            const int unknownMessageId = 2_000_000_001;
            view.ConsumeMissionEvents([new Level100MessageRequested(100, (int)Level100HudSpeaker.Tatiana,
                unknownMessageId, false, 60)]);
            bool refused = false;
            try
            {
                view.UpdateFromSnapshot(session.CurrentSnapshot with { Tick = 100,
                    Level100Mission = session.CurrentSnapshot.Level100Mission with { Tick = 100 } },
                    new Level100MessagePlaybackState(null, null, 0d, 0d, false, false));
            }
            catch (InvalidDataException) { refused = true; }
            Check(refused && view.Level100DeliveredMessageIds.SequenceEqual([unknownMessageId]),
                "A missing catalog row retains the already projected delivery-ID mutation before failure.");
            Check(view.Level100DeliveredMessageCount == 0,
                "The same catalog failure retains the previous visible text snapshot.");
            view.UpdateFromSnapshot(session.CurrentSnapshot,
                new Level100MessagePlaybackState(null, null, 0d, 0d, false, false));

            var packed = new PackedScene();
            Check(packed.Pack(presentation) == Error.Ok, "Production scene can be packed after asset binding.");
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

    private static int ExpectedPhase(int messageId, double elapsed, bool portrait)
    {
        int frame = Math.Max(0, (int)Math.Floor(elapsed / 0.05d));
        uint value = portrait
            ? unchecked(((uint)messageId * 0x9E3779B9u) ^ ((uint)frame * 0x85EBCA6Bu))
            : unchecked(((uint)messageId * 0xC2B2AE35u) ^ ((uint)frame * 0x27D4EB2Fu));
        value ^= value >> (portrait ? 16 : 15);
        if (!portrait) return (int)(value % 16);
        uint weighted = value % 100;
        return weighted < 8 ? 0 : weighted < 20 ? 1 : weighted < 60 ? 2 : 3;
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
