// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using Array = Godot.Collections.Array;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>Actual native scene/managed facts boundary. Retained Client laws are
/// test oracles only; the production host owns no competing entity state.</summary>
public sealed partial class EntityBridgeChecks : Node
{
    private int _checks;
    private readonly System.Collections.Generic.Dictionary<int, Node3D> _referenceProjectiles = [];
    private readonly System.Collections.Generic.Dictionary<int, Level100ProjectileTrailHistory> _referenceTrails = [];
    private readonly System.Collections.Generic.Dictionary<Level100ActorId, Level100TargetVisualDescriptor> _referenceTargets = [];

    public override async void _Ready()
    {
        try
        {
            var pointer = Input.MouseMode;
            var session = new InteractiveSession(0x4f4e534c, Level100StaticWorldAsset.LoadActorDefinitions());
            WorldSnapshot basis = session.CurrentSnapshot with
            {
                Level100Actors = session.CurrentSnapshot.Level100Actors with { Actors = [] },
                Projectiles = [],
            };
            string initialHash = StateHasher.ComputeHex(session.CurrentSnapshot);
            CompareProductionTexturePages();
            CompareMuzzleAnimation();
            CompareVulcanImpactAnimation();
            CompareDestructionAnimations();
            ComparePulseImpactAnimation();
            var viewport = new SubViewport { Size = new(320, 240), OwnWorld3D = true,
                RenderTargetUpdateMode = SubViewport.UpdateMode.Disabled };
            AddChild(viewport);
            var world = new Node3D();
            var referenceWorld = new Node3D();
            viewport.AddChild(world);
            viewport.AddChild(referenceWorld);
            var camera = new Camera3D { Position = new(4, 2, 8), Current = false };
            world.AddChild(camera);
            using PackedScene scene = GD.Load<PackedScene>(FirstFlightWorldView.EntityScenePath);
            Node owner = scene.Instantiate();
            world.AddChild(owner);
            using var assets = new Array();
            foreach (Level100TargetVisualBinding binding in Level100TargetPresentation.RenderedBindings)
            {
                using var mesh = new BoxMesh();
                using Variant meshValue = mesh;
                using var entry = new Dictionary { ["definition_name"] = binding.DefinitionName,
                    ["mesh_binding"] = binding.MeshBinding, ["mesh"] = meshValue };
                using Variant entryValue = entry;
                assets.Add(entryValue);
            }
            using var initialTargets = new Array();
            using Variant assetValues = assets;
            using Variant targetValues = initialTargets;
            using Variant configuredValue = owner.Call("configure", world, camera, assetValues, targetValues);
            using Dictionary configured = Result(configuredValue);

            WorldSnapshot previous = basis;
            for (int step = 0; step < 32; step++)
            {
                Level100ActorSnapshot[] actors = Enumerable.Range(0, 6)
                    .Select(index => Actor(index, step)).Reverse().ToArray();
                // An absent actor intentionally retains its previous visual;
                // an inactive actor remains registered and explicitly hidden.
                if (step % 7 == 4) actors = actors.Where(value => value.ActorId.Value != 3).ToArray();
                ProjectileSnapshot[] projectiles = step % 8 == 7 ? [] :
                [
                    new(100 + step / 8, Level100ProjectileKind.MechPulseBoltMedium,
                        new(3000 + step * 170, 7000 - step * 230), new(170, -230), 1500 + step * 19, 19, 120 - step % 8),
                    new(200 + step / 8, step % 2 == 0 ? Level100ProjectileKind.MechBullet : Level100ProjectileKind.MechAirBullet,
                        new(-2000 + step * 77, 3000 + step * 150), new(77, 150), 2100 - step * 8, -8, 20 - step % 8),
                ];
                WorldSnapshot current = basis with { Tick = step + 1,
                    Level100Actors = basis.Level100Actors with { Actors = actors }, Projectiles = projectiles,
                    WalkerFeet = basis.WalkerFeet.Select(foot => foot with { Position = new(foot.Position.X + step * 15,
                        foot.Position.Z - step * 11), LiftMillimeters = foot.LiftMillimeters + step * 4 }).ToArray() };
                // A duplicate previous identity must select its last pose,
                // rather than a sorted/ordinal or first-match substitute.
                if (step == 9 && previous.Level100Actors.Actors.Count > 0)
                {
                    Level100ActorSnapshot duplicate = previous.Level100Actors.Actors[0];
                    duplicate = duplicate with { Pose = duplicate.Pose with { PositionMillimeters = new(
                        duplicate.Pose.PositionMillimeters.X + 19, duplicate.Pose.PositionMillimeters.Y + 23,
                        duplicate.Pose.PositionMillimeters.Z + 29) } };
                    previous = previous with { Level100Actors = previous.Level100Actors with {
                        Actors = previous.Level100Actors.Actors.Concat([duplicate]).ToArray() } };
                }
                if (step == 16)
                {
                    world.Transform = new Transform3D(new Basis(Vector3.Up, 0.3f), new(3, 0, 4));
                    referenceWorld.Transform = world.Transform;
                }
                foreach (float alpha in new[] { 0f, 0.25f, 0.5f, 1f })
                {
                    int callbacks = 0;
                    using Dictionary facts = EntityFrameFacts(previous, current, alpha,
                        resetJump: step == 12, pendingMuzzles: 0);
                    Callable stage = Callable.From<Array, Dictionary>(feet =>
                    {
                        callbacks++;
                        CompareFeet(previous, current, alpha, step == 12, feet);
                        return new Dictionary { ["ok"] = true };
                    });
                    using Variant factValues = facts;
                    using Variant frameResult = owner.Call("render_frame", factValues, stage);
                    using Dictionary result = Result(frameResult);
                    Check(callbacks == 1, "Exactly one Aquila stage callback per native render batch.");
                    CompareTargets(owner, world, previous, current, alpha);
                    CompareProjectiles(owner, world, referenceWorld, camera, previous, current, alpha);
                    Check(result["projectile_count"].AsInt32() == current.Projectiles.Count, "Projectile diagnostics reflect the native owner.");
                    Check(result["target_count"].AsInt32() == _referenceTargets.Values.Count(value => value.Visible), "Visible actor diagnostics reflect retained/inactive actors.");
                }
                previous = current;
            }
            // Reference-equal snapshots deliberately suppress previous joins.
            using (Dictionary same = EntityFrameFacts(previous, previous, 0.5f, false, 0))
            {
                Check(same["same_snapshot"].AsBool() && same["previous_targets"].AsGodotArray().Count == 0 &&
                    same["previous_projectiles"].AsGodotArray().Count == 0 && same["previous_feet"].VariantType == Variant.Type.Nil,
                    "The actual host facts preserve the reference-equal snapshot gate.");
            }
            Check(StateHasher.ComputeHex(session.CurrentSnapshot) == initialHash, "Presentation leaves source Core state unchanged.");
            Check(Input.MouseMode == pointer, "The actual entity boundary never takes pointer ownership.");
            world.Free();
            referenceWorld.Free();
            viewport.QueueFree();
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
            GD.Print($"ENTITY_BRIDGE_CHECKS: {_checks} passed; exact actor matrices, foot words, projectile poses, trail vertices/UVs, identity and retained lifecycle.");
            GetTree().Quit(0);
        }
        catch (Exception error)
        {
            GD.PushError(error.ToString());
            GetTree().Quit(1);
        }
    }

    private void CompareProductionTexturePages()
    {
        using PackedScene scene = GD.Load<PackedScene>(FirstFlightWorldView.EntityScenePath);
        Node owner = scene.Instantiate();
        try
        {
            foreach ((string part, string file, int size, CuratedAyaTextureLoader.Compression compression) in new[]
            {
                ("PulseBolt/PulseBoltSprite", "pulse-bolt-blue-spark", 64, CuratedAyaTextureLoader.Compression.Dxt2),
                ("PulseBolt/PulseBoltHalo", "mech-pulse-medium-halo", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("PulseBolt/PulseBoltEnergyTrail", "mech-pulse-medium-energy-trail", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("PulseBolt/ProjectileTrail", "pulse-bolt-blue-trail", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("VulcanBullet/ProjectileTrail", "vulcan-bullet-trail", 64, CuratedAyaTextureLoader.Compression.Dxt1),
                ("MuzzleFlash/PulseCannonMuzzleFlash", "particle-alparticle5-additive", 128, CuratedAyaTextureLoader.Compression.Dxt1),
            })
            {
                var visual = owner.GetNode<MeshInstance3D>("Definitions/" + part);
                var material = (StandardMaterial3D)visual.MaterialOverride;
                Texture2D actual = material.AlbedoTexture;
                Check(actual is not null && actual.HasMethod("ensure_loaded"), "Each production material owns its native private-page recipe.");
                using Variant loadedValue = actual!.Call("ensure_loaded");
                using Dictionary loaded = Result(loadedValue);
                using Texture2D expected = CuratedAyaTextureLoader.Load(
                    "res://Assets/Level100/Textures/" + file + ".texture.aya", size, size, compression);
                using Image referenceImage = expected.GetImage();
                using Image actualImage = actual.GetImage();
                Check(actualImage.GetWidth() == referenceImage.GetWidth() && actualImage.GetHeight() == referenceImage.GetHeight(),
                    "Native texture dimensions equal the former managed loader: " + file);
                Check(actualImage.GetFormat() == referenceImage.GetFormat() && actualImage.HasMipmaps() == referenceImage.HasMipmaps(),
                    "Native texture format and mipmap admission equal the former loader: " + file);
                Check(actualImage.GetData().AsSpan().SequenceEqual(referenceImage.GetData()),
                    "Native decoded texture bytes equal the former loader: " + file);
                if (part != "MuzzleFlash/PulseCannonMuzzleFlash")
                    // Godot 4.8 dev6 excludes emission fields from Storage on
                    // unshaded materials. Local-to-scene copies drop those
                    // inactive fields; the native scene checks separately
                    // inspect identical page references in the authored state.
                    Check(material.ShadingMode == BaseMaterial3D.ShadingModeEnum.Unshaded &&
                        !material.EmissionEnabled && material.EmissionTexture is null,
                        "Native local-to-scene duplication omits inactive unshaded emission fields.");
            }
        }
        finally { owner.Free(); }
    }

    private void CompareMuzzleAnimation()
    {
        // Advance both production tweens explicitly, without wall-clock sleeps
        // or rendering. This retains the exact former C# schedule as the
        // temporary oracle for the native scene's UV and scale animation.
        var before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
        using PackedScene scene = GD.Load<PackedScene>("res://Scenes/World/PulseMuzzleFlash.tscn");
        var native = scene.Instantiate<Node3D>();
        AddChild(native);
        using Variant startValue = native.Call("start");
        using Dictionary started = Result(startValue);
        Tween[] nativeTweens = GetTree().GetProcessedTweens()
            .Where(value => !before.Contains(value.GetInstanceId())).ToArray();
        Check(nativeTweens.Length == 2, "A muzzle starts exactly one atlas and one scale tween.");
        Check(!native.GetNode<Godot.Timer>("Lifetime").IsStopped() &&
            native.GetNode<Godot.Timer>("Lifetime").WaitTime == 0.5d,
            "The native muzzle retains its explicit half-second lifetime timer.");
        var reference = new Node3D();
        AddChild(reference);
        var material = new StandardMaterial3D { AlbedoColor = new(0.5f, 1f, 1f, 1f),
            Uv1Scale = new(0.25f, 0.25f, 1f), Uv1Offset = new(0.25f, 0f, 0f) };
        var flash = new MeshInstance3D { Mesh = new QuadMesh { Size = new(0.6f, 0.6f) }, MaterialOverride = material };
        reference.AddChild(flash);
        Tween atlas = reference.CreateTween();
        const double interval = 1d / (1.4d * SimulationConstants.TicksPerSecond);
        for (int cell = 2; cell <= 15; cell++)
        {
            int captured = cell;
            atlas.TweenInterval(interval);
            atlas.TweenCallback(Callable.From(() => material.Uv1Offset = new(
                (captured % 4) / 4f, (captured / 4) / 4f, 0f)));
        }
        flash.Scale = Vector3.One;
        Tween scale = flash.CreateTween();
        scale.TweenProperty(flash, new NodePath("scale"), Vector3.One * 5f, 0.5d);
        Tween[] referenceTweens = [atlas, scale];
        bool[] nativeActive = [true, true], referenceActive = [true, true];
        foreach (Tween tween in nativeTweens.Concat(referenceTweens)) tween.Pause();
        var actual = native.GetNode<MeshInstance3D>("PulseCannonMuzzleFlash");
        var actualAnimatedMaterial = (StandardMaterial3D)actual.MaterialOverride;
        // The original callback closes over its initial material. Replacing
        // the mesh override must not retarget either running atlas animation.
        var sentinelOffset = new Vector3(0.125f, 0.375f, 0.625f);
        using var actualSentinel = new StandardMaterial3D { Uv1Offset = sentinelOffset };
        using var referenceSentinel = new StandardMaterial3D { Uv1Offset = sentinelOffset };
        actual.MaterialOverride = actualSentinel;
        flash.MaterialOverride = referenceSentinel;
        foreach (double delta in new[] { 0d, Math.BitDecrement(interval), interval - Math.BitDecrement(interval),
            interval, 0.01d, 0.023d, interval, 0.1d, interval, 0.15d, 0.2d })
        {
            for (int index = 0; index < 2; index++)
            {
                if (nativeActive[index]) nativeActive[index] = nativeTweens[index].CustomStep(delta);
                if (referenceActive[index]) referenceActive[index] = referenceTweens[index].CustomStep(delta);
                Check(nativeActive[index] == referenceActive[index], "Native muzzle tween completion follows the original schedule.");
            }
            Compare(actualAnimatedMaterial.Uv1Offset, material.Uv1Offset, "muzzle captured atlas UV");
            Compare(actualSentinel.Uv1Offset, sentinelOffset, "muzzle replacement material remains unchanged");
            Compare(referenceSentinel.Uv1Offset, sentinelOffset, "retained muzzle replacement material remains unchanged");
            Check(actual.MaterialOverride == actualSentinel && flash.MaterialOverride == referenceSentinel,
                "Atlas callbacks retain their initial material without replacing the current mesh override.");
            Compare(actual.Scale, flash.Scale, "muzzle radius animation");
        }
        Check(actualAnimatedMaterial.Uv1Offset == new Vector3(0.75f, 0.75f, 0f),
            "The production muzzle reaches final atlas cell fifteen.");
        Compare(actual.Scale, Vector3.One * 5f, "muzzle final radius ratio");
        foreach (Tween tween in nativeTweens.Concat(referenceTweens)) tween.Kill();
        native.Free();
        reference.Free();
    }

    private void CompareVulcanImpactAnimation()
    {
        // Retained cb2c5b4a SpawnVulcanImpact/AnimateVulcanImpactSpark and
        // AnimateScale are the reference. CustomStep advances the actual
        // engine tweens synchronously; no wall clock or rendering drives them.
        const string texturePath = "res://Assets/Level100/Textures/vulcan-impact-spark.texture.aya";
        byte[] sourceBefore = System.Security.Cryptography.SHA256.HashData(
            File.ReadAllBytes(ProjectSettings.GlobalizePath(texturePath)));
        using PackedScene scene = GD.Load<PackedScene>(FirstFlightWorldView.VulcanImpactScenePath);
        using GDScript controller = GD.Load<GDScript>("res://Scenes/World/vulcan_impact.gd");
        const ulong seed = 0x564c43414e53504bUL;
        GD.Seed(seed);
        uint[] expectedRandom = Enumerable.Range(0, 16).Select(_ => GD.Randi()).ToArray();
        GD.Seed(seed);
        uint[] actualPrefix = Enumerable.Range(0, 4).Select(_ => GD.Randi()).ToArray();
        Check(actualPrefix.SequenceEqual(expectedRandom.Take(4)), "The Vulcan RNG control sequence starts at its exact seeded prefix.");
        using (Variant admittedValue = controller.Call("admit_artwork"))
        using (Dictionary admitted = Result(admittedValue)) { }

        var native = scene.Instantiate<Node3D>();
        var sibling = scene.Instantiate<Node3D>();
        var reference = new Node3D();
        var ownershipReference = new Node3D();
        var host = new FirstFlightWorldView();
        var allTweens = new List<Tween>();
        try
        {
            var spark = native.GetNode<MeshInstance3D>("VulcanImpactSpark");
            var siblingSpark = sibling.GetNode<MeshInstance3D>("VulcanImpactSpark");
            var authoredMaterial = (StandardMaterial3D)spark.MaterialOverride;
            var lifetime = native.GetNode<Godot.Timer>("Lifetime");
            Compare(spark.Scale, Vector3.One, "Vulcan authored scale");
            Compare(authoredMaterial.Uv1Offset, new(0.75f, 0.5f, 0f), "Vulcan authored cell eleven");
            Check(spark.Mesh is QuadMesh quad && quad.Size == new Vector2(0.6f, 0.6f),
                "The authored Vulcan quad retains twice the .3 radius.");
            Check(authoredMaterial.AlbedoColor == Colors.White &&
                authoredMaterial.ShadingMode == BaseMaterial3D.ShadingModeEnum.Unshaded &&
                authoredMaterial.CullMode == BaseMaterial3D.CullModeEnum.Disabled &&
                authoredMaterial.Transparency == BaseMaterial3D.TransparencyEnum.Alpha &&
                authoredMaterial.BlendMode == BaseMaterial3D.BlendModeEnum.Add &&
                authoredMaterial.BillboardMode == BaseMaterial3D.BillboardModeEnum.Enabled && authoredMaterial.BillboardKeepScale,
                "The native direct spark preserves the original white, additive, unshaded billboard material.");
            Compare(authoredMaterial.Uv1Scale, new(0.25f, 0.25f, 1f), "Vulcan atlas cell size");
            using Texture2D recipe = GD.Load<Texture2D>("res://Scenes/World/VulcanImpactTexture.tres");
            Check(authoredMaterial.AlbedoTexture == recipe && ((StandardMaterial3D)siblingSpark.MaterialOverride).AlbedoTexture == recipe,
                "Native admission and both scene instances share the actual production texture recipe.");
            using (Texture2D expected = CuratedAyaTextureLoader.Load(texturePath, 256, 256, CuratedAyaTextureLoader.Compression.Dxt1))
            using (Image expectedImage = expected.GetImage())
            using (Image actualImage = recipe.GetImage())
            {
                Check(actualImage.GetWidth() == expectedImage.GetWidth() && actualImage.GetHeight() == expectedImage.GetHeight(),
                    "The native Vulcan artwork retains the former 256x256 admission.");
                Check(actualImage.GetFormat() == expectedImage.GetFormat() && actualImage.HasMipmaps() == expectedImage.HasMipmaps(),
                    "The native Vulcan format and mipmap policy equal the former DXT1 loader.");
                Check(actualImage.GetData().AsSpan().SequenceEqual(expectedImage.GetData()),
                    "Every decoded Vulcan artwork byte matches the retained loader.");
            }
            using (Variant refusedValue = native.Call("start"))
            using (Dictionary refused = refusedValue.AsGodotDictionary())
                Check(!refused["ok"].AsBool() && refused["error_type"].AsString() == "InvalidOperationException",
                    "An off-tree Vulcan start refuses explicitly without starting time.");
            Check(lifetime.IsStopped() && lifetime.OneShot && !lifetime.Autostart && lifetime.WaitTime == 0.25d &&
                lifetime.ProcessCallback == Godot.Timer.TimerProcessCallback.Idle && !lifetime.IgnoreTimeScale,
                "The authored lifetime retains the old quarter-second one-shot Timer defaults.");
            var before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            AddChild(native);
            AddChild(sibling);
            Check(lifetime.IsStopped() && !native.IsProcessing() && !native.IsProcessingInput() &&
                GetTree().GetProcessedTweens().All(value => before.Contains(value.GetInstanceId())),
                "Entering the tree leaves the frozen Vulcan preview and its timer/tweens inactive.");
            using (Variant startedValue = native.Call("start"))
            using (Dictionary started = Result(startedValue)) { }
            Tween[] nativeTweens = GetTree().GetProcessedTweens().Where(value => !before.Contains(value.GetInstanceId())).ToArray();
            allTweens.AddRange(nativeTweens);
            Check(nativeTweens.Length == 2, "A direct Vulcan spark starts exactly one atlas and one scale tween.");
            Check(!lifetime.IsStopped() && lifetime.TimeLeft == 0.25d &&
                lifetime.GetSignalConnectionList(Godot.Timer.SignalName.Timeout).Count == 1,
                "Explicit start connects and starts the separate original lifetime timer exactly once.");
            var material = (StandardMaterial3D)spark.MaterialOverride;
            Check(material != authoredMaterial && material.AlbedoTexture == recipe,
                "Starting a Vulcan effect detaches mutable material state while retaining its admitted texture.");
            using (Variant refusedValue = native.Call("start"))
            using (Dictionary refused = refusedValue.AsGodotDictionary())
                Check(!refused["ok"].AsBool() && refused["error_type"].AsString() == "InvalidOperationException",
                    "Repeated Vulcan start refuses instead of adding another animation owner.");
            Check(GetTree().GetProcessedTweens().Count(value => !before.Contains(value.GetInstanceId())) == 2 &&
                lifetime.GetSignalConnectionList(Godot.Timer.SignalName.Timeout).Count == 1,
                "A refused repeated start leaves the original two tweens and timeout connection intact.");
            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            using (Variant startedValue = sibling.Call("start"))
            using (Dictionary started = Result(startedValue)) { }
            Tween[] siblingTweens = GetTree().GetProcessedTweens().Where(value => !before.Contains(value.GetInstanceId())).ToArray();
            allTweens.AddRange(siblingTweens);
            Check(siblingTweens.Length == 2 && siblingSpark.MaterialOverride != material && siblingSpark.MaterialOverride != authoredMaterial,
                "Simultaneous Vulcan instances own independent animated materials and two tweens each.");

            AddChild(reference);
            var referenceLifetime = new Godot.Timer { Name = "Lifetime", OneShot = true, WaitTime = 0.25d };
            referenceLifetime.Timeout += reference.QueueFree;
            reference.AddChild(referenceLifetime);
            referenceLifetime.Start();
            var referenceMaterial = new StandardMaterial3D { Uv1Scale = new(0.25f, 0.25f, 1f) };
            var referenceSpark = new MeshInstance3D { Name = "VulcanImpactSpark",
                Mesh = new QuadMesh { Size = new(0.6f, 0.6f) }, MaterialOverride = referenceMaterial };
            reference.AddChild(referenceSpark);
            Tween atlas = RetainedVulcanAtlas(reference, referenceSpark);
            referenceSpark.Scale = Vector3.One * 1f;
            Tween scale = referenceSpark.CreateTween();
            scale.TweenProperty(referenceSpark, new NodePath("scale"), Vector3.One * (10f / 3f), 0.25d);
            Tween[] referenceTweens = [atlas, scale];
            allTweens.AddRange(referenceTweens);
            foreach (Tween tween in allTweens) tween.Pause();
            bool[] nativeActive = [true, true], referenceActive = [true, true];
            const double interval = 1d / (0.8d * SimulationConstants.TicksPerSecond);
            int sample = 0;
            // Keep every original zero/nextafter boundary. On dev6, reaching
            // the final atlas callback can still return active=true; another
            // positive CustomStep observes completion without changing UV/scale
            // or elapsed time. This is an observation horizon, not a new
            // tween interval or a replacement for the independent .25 Timer.
            foreach (double delta in new[] { 0d, Math.BitDecrement(interval), interval - Math.BitDecrement(interval),
                0d, interval, Math.BitDecrement(interval), interval - Math.BitDecrement(interval),
                Math.BitDecrement(interval), interval - Math.BitDecrement(interval), 0d, 0.03125d, interval })
            {
                for (int index = 0; index < 2; index++)
                {
                    if (nativeActive[index]) nativeActive[index] = nativeTweens[index].CustomStep(delta);
                    if (referenceActive[index]) referenceActive[index] = referenceTweens[index].CustomStep(delta);
                    Check(nativeActive[index] == referenceActive[index], "Native Vulcan tween completion follows the retained C# boundary schedule.");
                }
                Compare(material.Uv1Offset, referenceMaterial.Uv1Offset, "Vulcan atlas UV");
                Compare(spark.Scale, referenceSpark.Scale, "Vulcan radius animation");
                Compare(((StandardMaterial3D)siblingSpark.MaterialOverride).Uv1Offset, new(0.75f, 0.5f, 0f), "Independent Vulcan atlas");
                Compare(siblingSpark.Scale, Vector3.One, "Independent Vulcan scale");
                if (sample++ >= 10)
                    GD.Print(FormattableString.Invariant($"VULCAN_TWEEN_OBSERVATION: sample={sample - 1}, delta={delta:R}, native_active={nativeActive[0]}/{nativeActive[1]}, retained_active={referenceActive[0]}/{referenceActive[1]}, native_elapsed={nativeTweens[0].GetTotalElapsedTime():R}/{nativeTweens[1].GetTotalElapsedTime():R}, retained_elapsed={referenceTweens[0].GetTotalElapsedTime():R}/{referenceTweens[1].GetTotalElapsedTime():R}"));
            }
            Check(nativeActive.All(value => !value) && referenceActive.All(value => !value),
                "Both native and retained Vulcan tweens complete without being driven by the lifetime timer.");
            Compare(material.Uv1Offset, new(0.75f, 0.75f, 0f), "Vulcan final cell fifteen");
            Compare(spark.Scale, Vector3.One * (10f / 3f), "Vulcan final Single radius ratio");
            Compare(authoredMaterial.Uv1Offset, new(0.75f, 0.5f, 0f), "Frozen authored Vulcan material");
            Check(!native.IsQueuedForDeletion() && !reference.IsQueuedForDeletion() &&
                lifetime.TimeLeft == referenceLifetime.TimeLeft && lifetime.TimeLeft == 0.25d,
                "Stepping animation alone does not replace or advance the independent Timer owner.");
            lifetime.EmitSignal(Godot.Timer.SignalName.Timeout);
            referenceLifetime.EmitSignal(Godot.Timer.SignalName.Timeout);
            Check(native.IsQueuedForDeletion() && reference.IsQueuedForDeletion(),
                "The same explicit timeout signal queues each lifetime root for deletion.");

            // Use a fresh retained instance for the ownership schedule. Tween
            // IsValid can remain true until SceneTree cleanup after its bound
            // node is freed; compare that timing instead of assuming it.
            AddChild(ownershipReference);
            var ownershipLifetime = new Godot.Timer { Name = "Lifetime", OneShot = true, WaitTime = 0.25d };
            ownershipLifetime.Timeout += ownershipReference.QueueFree;
            ownershipReference.AddChild(ownershipLifetime);
            ownershipLifetime.Start();
            var ownershipMaterial = new StandardMaterial3D { Uv1Scale = new(0.25f, 0.25f, 1f) };
            var ownershipSpark = new MeshInstance3D { Name = "VulcanImpactSpark",
                Mesh = new QuadMesh { Size = new(0.6f, 0.6f) }, MaterialOverride = ownershipMaterial };
            ownershipReference.AddChild(ownershipSpark);
            Tween ownershipAtlas = RetainedVulcanAtlas(ownershipReference, ownershipSpark);
            ownershipSpark.Scale = Vector3.One * 1f;
            Tween ownershipScale = ownershipSpark.CreateTween();
            ownershipScale.TweenProperty(ownershipSpark, new NodePath("scale"), Vector3.One * (10f / 3f), 0.25d);
            allTweens.Add(ownershipAtlas);
            allTweens.Add(ownershipScale);
            ownershipAtlas.Pause();
            ownershipScale.Pause();
            var siblingMaterial = (StandardMaterial3D)siblingSpark.MaterialOverride;
            Compare(siblingMaterial.Uv1Offset, ownershipMaterial.Uv1Offset, "Fresh Vulcan ownership atlas");

            siblingSpark.Free();
            ownershipSpark.Free();
            Check(!CompareVulcanOwnershipStep(siblingTweens[1], ownershipScale, 0d, "scale after child free"),
                "Both child-bound scale tweens stop after their spark is freed.");
            Check(CompareVulcanOwnershipStep(siblingTweens[0], ownershipAtlas, interval * 1.5d, "atlas after child free"),
                "Both root-bound atlas tweens can still advance after their spark is freed.");
            Compare(siblingMaterial.Uv1Offset, ownershipMaterial.Uv1Offset, "Captured Vulcan atlas after child free");
            Check(siblingMaterial.Uv1Offset != new Vector3(0.75f, 0.5f, 0f),
                "Both retained material targets advance beyond cell eleven after the child is freed.");
            Vector3 capturedOffset = siblingMaterial.Uv1Offset;
            sibling.Free();
            ownershipReference.Free();
            Check(!CompareVulcanOwnershipStep(siblingTweens[0], ownershipAtlas, interval, "atlas after root free"),
                "Both atlas tweens stop when their lifetime root is freed.");
            Check(!CompareVulcanOwnershipStep(siblingTweens[1], ownershipScale, interval, "scale after root free"),
                "Both child-bound scale tweens remain stopped after the root is freed.");
            Compare(siblingMaterial.Uv1Offset, ownershipMaterial.Uv1Offset, "Captured Vulcan atlas after root free");
            Compare(siblingMaterial.Uv1Offset, capturedOffset, "Stopped Vulcan atlas retains its last material offset");
            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            AddChild(host);
            var impact = new Level100DestructionEvent(Level100DestructionEventKind.VulcanImpact,
                Level100DestructionEffectKind.VulcanImpact, 37, 0, 0, new(12345, -6789, 4321));
            host.ConsumeLevel100DestructionEvents([impact], 81);
            var spawned = host.GetNode<Node3D>("VulcanImpact37-81");
            using (Variant script = spawned.GetScript())
                Check(script.As<GodotObject>() == controller && spawned.SceneFilePath == FirstFlightWorldView.VulcanImpactScenePath,
                    "The actual public destruction-event route instantiates the production native Vulcan scene.");
            Check(host.GetChildCount() == 1 && spawned.Name == "VulcanImpact37-81",
                "The host preserves the original actor/tick effect name and one direct effect root.");
            Compare(spawned.Position, new(impact.Position.X * 0.001f,
                -impact.Position.Z * 0.001f, -impact.Position.Y * 0.001f), "Host Vulcan X/-Z/-Y position");
            var spawnedTimer = spawned.GetNode<Godot.Timer>("Lifetime");
            Check(!spawnedTimer.IsStopped() && spawnedTimer.WaitTime == 0.25d && spawnedTimer.OneShot,
                "The actual event route explicitly starts the original quarter-second lifetime.");
            Tween[] hostTweens = GetTree().GetProcessedTweens().Where(value => !before.Contains(value.GetInstanceId())).ToArray();
            allTweens.AddRange(hostTweens);
            Check(hostTweens.Length == 2, "The actual event route adds exactly the native atlas and scale tweens.");
            foreach (Tween tween in hostTweens) tween.Pause();
            host.Free();
            uint[] actualSuffix = Enumerable.Range(0, 12).Select(_ => GD.Randi()).ToArray();
            Check(actualSuffix.SequenceEqual(expectedRandom.Skip(4)),
                "Admission, instantiation, start, animation, lifetime and the actual event route consume no global presentation RNG draws.");
            Check(sourceBefore.AsSpan().SequenceEqual(System.Security.Cryptography.SHA256.HashData(
                File.ReadAllBytes(ProjectSettings.GlobalizePath(texturePath)))), "Vulcan asset admission and animation leave the prepared input bytes unchanged.");
        }
        finally
        {
            foreach (Tween tween in allTweens) if (tween.IsValid()) tween.Kill();
            if (GodotObject.IsInstanceValid(native)) native.Free();
            if (GodotObject.IsInstanceValid(sibling)) sibling.Free();
            if (GodotObject.IsInstanceValid(reference)) reference.Free();
            if (GodotObject.IsInstanceValid(ownershipReference)) ownershipReference.Free();
            if (GodotObject.IsInstanceValid(host)) host.Free();
        }
    }

    private bool CompareVulcanOwnershipStep(Tween native, Tween retained, double delta, string stage, string effect = "Vulcan")
    {
        bool nativeValid = native.IsValid(), retainedValid = retained.IsValid();
        Check(nativeValid == retainedValid, effect + " tween validity matches the retained owner before " + stage + ".");
        bool nativeActive = nativeValid && native.CustomStep(delta);
        bool retainedActive = retainedValid && retained.CustomStep(delta);
        Check(nativeActive == retainedActive, effect + " CustomStep result matches the retained owner at " + stage + ".");
        Check(native.IsValid() == retained.IsValid(), effect + " tween validity matches the retained owner after " + stage + ".");
        Check(BitConverter.DoubleToInt64Bits(native.GetTotalElapsedTime()) == BitConverter.DoubleToInt64Bits(retained.GetTotalElapsedTime()),
            effect + " elapsed-time words match the retained owner at " + stage + ".");
        GD.Print(FormattableString.Invariant($"{effect.ToUpperInvariant()}_OWNERSHIP_OBSERVATION: stage={stage}, delta={delta:R}, native_active={nativeActive}, retained_active={retainedActive}, native_valid={native.IsValid()}, retained_valid={retained.IsValid()}, native_elapsed={native.GetTotalElapsedTime():R}, retained_elapsed={retained.GetTotalElapsedTime():R}"));
        return nativeActive;
    }

    // Exact cb2c5b4a AnimateVulcanImpactSpark body, returning its created tween
    // so the existing headless harness can advance it deterministically.
    private static Tween RetainedVulcanAtlas(Node root, MeshInstance3D spark)
    {
        const int startCell = 11;
        const int endCell = 15;
        const int columns = 4;
        const int rows = 4;
        const double cellsPerTurn = 0.8d;
        double cellIntervalSeconds =
            1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
        var material = (StandardMaterial3D)spark.MaterialOverride;
        material.Uv1Offset = new Vector3(
            (startCell % columns) / (float)columns,
            (startCell / columns) / (float)rows,
            0f);

        Tween tween = root.CreateTween();
        for (int cell = startCell + 1; cell <= endCell; cell++)
        {
            int capturedCell = cell;
            tween.TweenInterval(cellIntervalSeconds);
            tween.TweenCallback(Callable.From(() =>
            {
                material.Uv1Offset = new Vector3(
                    (capturedCell % columns) / (float)columns,
                    (capturedCell / columns) / (float)rows,
                    0f);
            }));
        }
        return tween;
    }

    private void CompareDestructionAnimations()
    {
        // The three old 673b630a spawn bodies and their helpers are retained
        // below without replacing their arithmetic or callback order. These
        // are comparisons with that implementation, not new retail claims
        // about the still-unresolved emitter multiplicity/placement/colour.
        const ulong admissionSeed = 0x4453545241444dUL;
        GD.Seed(admissionSeed);
        uint[] expectedAdmissionRandom = Enumerable.Range(0, 16).Select(_ => GD.Randi()).ToArray();
        GD.Seed(admissionSeed);
        using GDScript controller = GD.Load<GDScript>("res://Scenes/World/destruction_effect.gd");
        var inputs = new[]
        {
            (Id: "animated_blob", File: "pulse-impact-animated-blob", Size: 256, Compression: CuratedAyaTextureLoader.Compression.Dxt2),
            (Id: "flash_medium", File: "effect-flash-medium", Size: 128, Compression: CuratedAyaTextureLoader.Compression.Dxt1),
            (Id: "explosion_animated", File: "target-tank-explosion-animated", Size: 256, Compression: CuratedAyaTextureLoader.Compression.Dxt1),
            (Id: "fireball", File: "target-tank-explosion-fireball", Size: 256, Compression: CuratedAyaTextureLoader.Compression.Dxt2),
        };
        var paths = inputs.Select(row => "res://Assets/Level100/Textures/" + row.File + ".texture.aya").ToArray();
        byte[][] beforeHashes = paths.Select(path => System.Security.Cryptography.SHA256.HashData(
            File.ReadAllBytes(ProjectSettings.GlobalizePath(path)))).ToArray();
        var textures = new Texture2D[inputs.Length];
        var recipes = new Texture2D[inputs.Length];
        try
        {
            for (int index = 0; index < inputs.Length; index++)
            {
                textures[index] = CuratedAyaTextureLoader.Load(paths[index], inputs[index].Size, inputs[index].Size, inputs[index].Compression);
                using Variant returned = controller.Call("admit_artwork", inputs[index].Id);
                using Dictionary admitted = Result(returned);
                recipes[index] = admitted["value"].As<Texture2D>();
                using Image actual = recipes[index].GetImage();
                using Image retained = textures[index].GetImage();
                Check(actual.GetWidth() == retained.GetWidth() && actual.GetHeight() == retained.GetHeight() &&
                    actual.GetFormat() == retained.GetFormat() && actual.HasMipmaps() == retained.HasMipmaps(),
                    "Destruction recipe image shape/format/mips match the retained loader: " + inputs[index].Id);
                Check(actual.GetData().AsSpan().SequenceEqual(retained.GetData()),
                    "Every destruction recipe pixel byte matches the retained loader: " + inputs[index].Id);
            }
            Check(Enumerable.Range(0, 16).Select(_ => GD.Randi()).SequenceEqual(expectedAdmissionRandom),
                "Loading and admitting all destruction artwork consumes no presentation RNG.");
            CompareDestructionFamily("TargetTankDestruction", Level100DestructionEffectKind.TargetDestroyed, 1.5d, 1, 5, textures, recipes);
            CompareDestructionFamily("TargetDroneDestruction", Level100DestructionEffectKind.DroneDestroyed, 1.5d, 1, 3, textures, recipes);
            CompareDestructionFamily("FacilityDestruction", Level100DestructionEffectKind.FacilityDestroyed, 15d, 2, 5, textures, recipes);
            for (int index = 0; index < paths.Length; index++)
                Check(beforeHashes[index].AsSpan().SequenceEqual(System.Security.Cryptography.SHA256.HashData(
                    File.ReadAllBytes(ProjectSettings.GlobalizePath(paths[index])))),
                    "Destruction admission, animation and event routing preserve prepared input bytes: " + inputs[index].Id);
        }
        finally
        {
            foreach (Texture2D? texture in textures) texture?.Dispose();
        }
    }

    private void CompareDestructionFamily(string sceneName, Level100DestructionEffectKind kind,
        double lifetimeSeconds, int randomDraws, int tweenCount, Texture2D[] textures, Texture2D[] recipes)
    {
        string scenePath = "res://Scenes/World/" + sceneName + ".tscn";
        const ulong seed = 0x54414e4b46495245UL;
        GD.Seed(seed);
        uint[] expectedRandom = Enumerable.Range(0, 16).Select(_ => GD.Randi()).ToArray();
        GD.Seed(seed);
        using PackedScene scene = GD.Load<PackedScene>(scenePath);
        var native = scene.Instantiate<Node3D>();
        var sibling = scene.Instantiate<Node3D>();
        var retained = new RetainedDestructionEffects(textures);
        var host = new FirstFlightWorldView();
        var allTweens = new List<Tween>();
        var sentinels = new List<StandardMaterial3D>();
        try
        {
            var lifetime = native.GetNode<Godot.Timer>("Lifetime");
            using (Variant refusedValue = native.Call("start"))
            using (Dictionary refused = refusedValue.AsGodotDictionary())
                Check(!refused["ok"].AsBool() && refused["error_type"].AsString() == "InvalidOperationException",
                    sceneName + " refuses off-tree activation explicitly.");
            var before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            AddChild(native);
            AddChild(sibling);
            AddChild(retained.Root);
            Check(lifetime.IsStopped() && sibling.GetNode<Godot.Timer>("Lifetime").IsStopped() &&
                !native.IsProcessing() && !native.IsProcessingInput() && !native.IsProcessingUnhandledInput() &&
                GetTree().GetProcessedTweens().All(value => before.Contains(value.GetInstanceId())),
                sceneName + " scene entry has no automatic animation, timer or input owner.");
            Check(Enumerable.Range(0, 16).Select(_ => GD.Randi()).SequenceEqual(expectedRandom),
                sceneName + " scene load, instantiation and refused start consume no RNG.");

            GD.Seed(seed);
            using (Variant returned = native.Call("start"))
            using (Dictionary result = Result(returned)) { }
            Tween[] nativeTweens = NewDestructionTweens(before, allTweens, tweenCount, sceneName + " native");
            Check(Enumerable.Range(0, 16 - randomDraws).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(randomDraws)),
                sceneName + " consumes exactly its original ordered RNG draws at start.");

            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            Node3D reference = retained.Spawn(kind, Vector3.Zero, 37);
            Tween[] referenceTweens = NewDestructionTweens(before, allTweens, tweenCount, sceneName + " retained");
            Check(Enumerable.Range(0, 16 - randomDraws).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(randomDraws)),
                sceneName + " retained spawn confirms the same RNG suffix.");

            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            using (Variant returned = sibling.Call("start"))
            using (Dictionary result = Result(returned)) { }
            NewDestructionTweens(before, allTweens, tweenCount, sceneName + " sibling");
            Check(Enumerable.Range(0, 16 - randomDraws).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(randomDraws)),
                sceneName + " independent sibling retains the same draw count.");

            var actualMaterials = DestructionMaterials(native);
            var referenceMaterials = DestructionMaterials(reference);
            var siblingMaterials = DestructionMaterials(sibling);
            Check(native.GetChildren().Select(child => child.Name.ToString()).SequenceEqual(
                reference.GetChildren().Select(child => child.Name.ToString())),
                sceneName + " keeps the original Timer and sprite creation order.");
            CompareDestructionTimer(lifetime, reference.GetNode<Godot.Timer>("Lifetime"), lifetimeSeconds, sceneName);
            CompareDestructionFrame(native, reference, actualMaterials, referenceMaterials, sceneName + " initial");
            foreach (MeshInstance3D mesh in native.GetChildren().OfType<MeshInstance3D>())
            {
                string name = mesh.Name.ToString();
                var referenceMesh = reference.GetNode<MeshInstance3D>(name);
                var actualMaterial = actualMaterials[name];
                var referenceMaterial = referenceMaterials[name];
                Check(mesh.Mesh is QuadMesh && referenceMesh.Mesh is QuadMesh, sceneName + " retains billboard quad geometry: " + name);
                Vector2 actualSize = ((QuadMesh)mesh.Mesh).Size, referenceSize = ((QuadMesh)referenceMesh.Mesh).Size;
                Compare(new Vector3(actualSize.X, actualSize.Y, 0f), new Vector3(referenceSize.X, referenceSize.Y, 0f), name + " quad size");
                Check(actualMaterial != siblingMaterials[name], "Simultaneous destruction instances own independent material targets: " + name);
                Check(actualMaterial.ShadingMode == referenceMaterial.ShadingMode && actualMaterial.CullMode == referenceMaterial.CullMode &&
                    actualMaterial.Transparency == referenceMaterial.Transparency && actualMaterial.BlendMode == referenceMaterial.BlendMode &&
                    actualMaterial.BillboardMode == referenceMaterial.BillboardMode && actualMaterial.BillboardKeepScale == referenceMaterial.BillboardKeepScale,
                    sceneName + " preserves the original material recipe: " + name);
                int textureIndex = name.EndsWith("Flash", StringComparison.Ordinal) ? 1 : name == "ExplosionAnimatedSprite" ? 2 : name.EndsWith("Smoke", StringComparison.Ordinal) ? 0 : 3;
                Check(actualMaterial.AlbedoTexture == recipes[textureIndex] && referenceMaterial.AlbedoTexture == textures[textureIndex] &&
                    siblingMaterials[name].AlbedoTexture == recipes[textureIndex],
                    sceneName + " renders its single admitted shared texture recipe: " + name);
            }

            // Preserve each initial animated target while replacing only the
            // mesh override: all old atlas closures captured their material.
            var sentinelOffset = new Vector3(0.125f, 0.375f, 0.625f);
            foreach ((string name, StandardMaterial3D material) in actualMaterials)
            {
                if (material.Uv1Scale.X != 0.25f) continue;
                var actualSentinel = new StandardMaterial3D { Uv1Offset = sentinelOffset };
                var referenceSentinel = new StandardMaterial3D { Uv1Offset = sentinelOffset };
                sentinels.Add(actualSentinel);
                sentinels.Add(referenceSentinel);
                native.GetNode<MeshInstance3D>(name).MaterialOverride = actualSentinel;
                reference.GetNode<MeshInstance3D>(name).MaterialOverride = referenceSentinel;
            }
            var siblingOffsets = siblingMaterials.ToDictionary(row => row.Key, row => row.Value.Uv1Offset);
            var siblingScales = sibling.GetChildren().OfType<MeshInstance3D>().ToDictionary(mesh => mesh.Name.ToString(), mesh => mesh.Scale);
            var siblingVisibility = sibling.GetChildren().OfType<MeshInstance3D>().ToDictionary(mesh => mesh.Name.ToString(), mesh => mesh.Visible);
            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            using (Variant refusedValue = native.Call("start"))
            using (Dictionary refused = refusedValue.AsGodotDictionary())
                Check(!refused["ok"].AsBool() && refused["error_type"].AsString() == "InvalidOperationException",
                    sceneName + " refuses repeated activation before another timer/tween/RNG mutation.");
            Check(GetTree().GetProcessedTweens().All(tween => before.Contains(tween.GetInstanceId())),
                sceneName + " refused restart adds no tween owner.");
            bool[] actualActive = Enumerable.Repeat(true, tweenCount).ToArray();
            bool[] referenceActive = Enumerable.Repeat(true, tweenCount).ToArray();
            const double explosionInterval = 1d / (0.7d * SimulationConstants.TicksPerSecond);
            const double loopInterval = 1d / (0.5d * SimulationConstants.TicksPerSecond);
            var times = new List<double> { 0d, Math.BitDecrement(loopInterval), loopInterval, Math.BitIncrement(loopInterval),
                Math.BitDecrement(0.25d), 0.25d, 0.25d, Math.BitIncrement(0.25d), 0.3d,
                Math.BitDecrement(0.25d + explosionInterval), 0.25d + explosionInterval, Math.BitIncrement(0.25d + explosionInterval),
                0.5d, Math.BitDecrement(0.75d), 0.75d, Math.BitIncrement(0.75d), 0.8d,
                Math.BitDecrement(1.5d), 1.5d, Math.BitIncrement(1.5d), 1.6d, 1.7d };
            if (kind == Level100DestructionEffectKind.FacilityDestroyed)
                times.AddRange([Math.BitDecrement(3d), 3d, Math.BitIncrement(3d), 3.1d,
                    Math.BitDecrement(15d), 15d, Math.BitIncrement(15d), 15.1d, 15.2d]);
            times.Sort();
            double previousTime = 0d;
            foreach (double time in times)
            {
                double delta = time - previousTime;
                previousTime = time;
                for (int index = 0; index < tweenCount; index++)
                {
                    if (actualActive[index]) actualActive[index] = nativeTweens[index].CustomStep(delta);
                    if (referenceActive[index]) referenceActive[index] = referenceTweens[index].CustomStep(delta);
                    Check(actualActive[index] == referenceActive[index] && nativeTweens[index].IsValid() == referenceTweens[index].IsValid(),
                        sceneName + " actual/retained tween completion and validity agree at sample " + time.ToString("R", System.Globalization.CultureInfo.InvariantCulture));
                    Check(BitConverter.DoubleToInt64Bits(nativeTweens[index].GetTotalElapsedTime()) == BitConverter.DoubleToInt64Bits(referenceTweens[index].GetTotalElapsedTime()),
                        sceneName + " actual/retained elapsed words agree for ordered tween " + index);
                }
                CompareDestructionFrame(native, reference, actualMaterials, referenceMaterials, sceneName);
                foreach (StandardMaterial3D sentinel in sentinels) Compare(sentinel.Uv1Offset, sentinelOffset, sceneName + " replacement override stays unchanged");
                foreach ((string name, StandardMaterial3D material) in siblingMaterials)
                {
                    Compare(material.Uv1Offset, siblingOffsets[name], sceneName + " independent sibling atlas");
                    Compare(sibling.GetNode<MeshInstance3D>(name).Scale, siblingScales[name], sceneName + " independent sibling scale");
                    Check(sibling.GetNode<MeshInstance3D>(name).Visible == siblingVisibility[name], sceneName + " independent sibling visibility");
                }
            }
            Check(actualActive.All(active => !active) && referenceActive.All(active => !active),
                sceneName + " actual and retained tweens both finish within the compared observation schedule.");
            Check(Enumerable.Range(0, 16).Select(_ => GD.Randi()).SequenceEqual(expectedRandom),
                sceneName + " rejected restart and all animation callbacks consume no additional RNG.");
            CompareDestructionTimer(lifetime, reference.GetNode<Godot.Timer>("Lifetime"), lifetimeSeconds, sceneName + " after manual animation");
            Check(!native.IsQueuedForDeletion() && !reference.IsQueuedForDeletion(),
                sceneName + " manual animation does not substitute for its independent lifetime Timer.");
            lifetime.EmitSignal(Godot.Timer.SignalName.Timeout);
            reference.GetNode<Godot.Timer>("Lifetime").EmitSignal(Godot.Timer.SignalName.Timeout);
            Check(native.IsQueuedForDeletion() && reference.IsQueuedForDeletion(), sceneName + " actual/retained timeout signals queue their roots.");

            // The public event route must instantiate this scene, retain the
            // actor-only name and original X/-Z/-Y position, and start it.
            AddChild(host);
            var position = new Level100Vector3(12345, -6789, 4321);
            Vector3 mapped = new(position.X * 0.001f, -position.Z * 0.001f, -position.Y * 0.001f);
            var item = new Level100DestructionEvent(Level100DestructionEventKind.Terminal, kind, 71, 0, 0, position);
            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            host.ConsumeLevel100DestructionEvents([item], 81);
            Node3D spawned = host.GetNode<Node3D>(sceneName + "71");
            NewDestructionTweens(before, allTweens, tweenCount, sceneName + " public event");
            Check(Enumerable.Range(0, 16 - randomDraws).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(randomDraws)),
                sceneName + " public event preserves the exact random draw count.");
            using (Variant script = spawned.GetScript())
                Check(script.As<GodotObject>() is GDScript nativeScript && nativeScript.ResourcePath == "res://Scenes/World/destruction_effect.gd" &&
                    spawned.SceneFilePath == scenePath && host.GetChildCount() == 1,
                    sceneName + " public event constructs exactly its actual native production scene.");
            Compare(spawned.Position, mapped, sceneName + " public event position");
            before = GetTree().GetProcessedTweens().Select(value => value.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            Node3D expectedSpawn = retained.Spawn(kind, mapped, 71);
            NewDestructionTweens(before, allTweens, tweenCount, sceneName + " retained public event");
            CompareDestructionFrame(spawned, expectedSpawn, DestructionMaterials(spawned), DestructionMaterials(expectedSpawn), sceneName + " public event");
            CompareDestructionTimer(spawned.GetNode<Godot.Timer>("Lifetime"), expectedSpawn.GetNode<Godot.Timer>("Lifetime"), lifetimeSeconds, sceneName + " public event");
        }
        finally
        {
            foreach (Tween tween in allTweens) if (tween.IsValid()) tween.Kill();
            if (GodotObject.IsInstanceValid(native)) native.Free();
            if (GodotObject.IsInstanceValid(sibling)) sibling.Free();
            if (GodotObject.IsInstanceValid(retained.Root)) retained.Root.Free();
            if (GodotObject.IsInstanceValid(host)) host.Free();
            foreach (StandardMaterial3D sentinel in sentinels) sentinel.Dispose();
        }
    }

    private Tween[] NewDestructionTweens(HashSet<ulong> before, List<Tween> owned, int expectedCount, string name)
    {
        Tween[] result = GetTree().GetProcessedTweens().Where(tween => !before.Contains(tween.GetInstanceId())).ToArray();
        owned.AddRange(result);
        Check(result.Length == expectedCount, name + " creates the original ordered tween count.");
        foreach (Tween tween in result) tween.Pause();
        return result;
    }

    private static System.Collections.Generic.Dictionary<string, StandardMaterial3D> DestructionMaterials(Node root) =>
        root.GetChildren().OfType<MeshInstance3D>().ToDictionary(mesh => mesh.Name.ToString(), mesh => (StandardMaterial3D)mesh.MaterialOverride);

    private void CompareDestructionTimer(Godot.Timer actual, Godot.Timer retained, double lifetime, string name)
    {
        Check(!actual.IsStopped() && actual.IsStopped() == retained.IsStopped() && actual.OneShot == retained.OneShot &&
            actual.Autostart == retained.Autostart && actual.ProcessCallback == retained.ProcessCallback &&
            actual.IgnoreTimeScale == retained.IgnoreTimeScale && actual.OneShot && !actual.Autostart,
            name + " Timer ownership and defaults match the retained effect.");
        Check(BitConverter.DoubleToInt64Bits(actual.WaitTime) == BitConverter.DoubleToInt64Bits(retained.WaitTime) &&
            BitConverter.DoubleToInt64Bits(actual.TimeLeft) == BitConverter.DoubleToInt64Bits(retained.TimeLeft) &&
            actual.WaitTime == lifetime && actual.TimeLeft == lifetime,
            name + " keeps the exact unadvanced lifetime seconds.");
        Check(actual.GetSignalConnectionList(Godot.Timer.SignalName.Timeout).Count == 1 &&
            retained.GetSignalConnectionList(Godot.Timer.SignalName.Timeout).Count == 1,
            name + " connects precisely one original timeout owner.");
    }

    private void CompareDestructionFrame(Node3D actual, Node3D retained,
        IReadOnlyDictionary<string, StandardMaterial3D> actualMaterials,
        IReadOnlyDictionary<string, StandardMaterial3D> retainedMaterials, string name)
    {
        foreach ((string path, StandardMaterial3D material) in actualMaterials)
        {
            var actualMesh = actual.GetNode<MeshInstance3D>(path);
            var retainedMesh = retained.GetNode<MeshInstance3D>(path);
            StandardMaterial3D referenceMaterial = retainedMaterials[path];
            Compare(actualMesh.Scale, retainedMesh.Scale, name + " " + path + " scale");
            Check(actualMesh.Visible == retainedMesh.Visible, name + " " + path + " visibility follows the retained callback order.");
            Compare(material.Uv1Scale, referenceMaterial.Uv1Scale, name + " " + path + " UV scale");
            Compare(material.Uv1Offset, referenceMaterial.Uv1Offset, name + " " + path + " captured UV offset");
            Color ink = material.AlbedoColor, expectedInk = referenceMaterial.AlbedoColor;
            Compare(new Vector3(ink.R, ink.G, ink.B), new Vector3(expectedInk.R, expectedInk.G, expectedInk.B), name + " " + path + " RGB");
            Check(BitConverter.SingleToUInt32Bits(ink.A) == BitConverter.SingleToUInt32Bits(expectedInk.A), name + " " + path + " alpha word");
        }
    }

    private void ComparePulseImpactAnimation()
    {
        const string scenePath = "res://Scenes/World/PulseImpact.tscn";
        const string scriptPath = "res://Scenes/World/pulse_impact.gd";
        const ulong seed = 0x50554c5345424c42UL;
        const float globalSeconds = 2048.3125f;
        GD.Seed(seed);
        uint[] expectedRandom = Enumerable.Range(0, 16).Select(_ => GD.Randi()).ToArray();
        GD.Seed(seed);
        var paths = new[]
        {
            "res://Assets/Level100/Textures/pulse-impact-animated-blob.texture.aya",
            "res://Assets/Level100/Textures/pulse-impact-shockwave.texture.aya",
            "res://Assets/Level100/Textures/effect-flash-medium.texture.aya",
        };
        byte[][] beforeHashes = paths.Select(path => System.Security.Cryptography.SHA256.HashData(
            File.ReadAllBytes(ProjectSettings.GlobalizePath(path)))).ToArray();
        using Texture2D blobTexture = CuratedAyaTextureLoader.Load(paths[0], 256, 256);
        using Texture2D shockwaveTexture = CuratedAyaTextureLoader.Load(paths[1], 128, 128, CuratedAyaTextureLoader.Compression.Dxt1);
        using Texture2D flashTexture = CuratedAyaTextureLoader.Load(paths[2], 128, 128, CuratedAyaTextureLoader.Compression.Dxt1);
        using GDScript controller = GD.Load<GDScript>(scriptPath);
        using GDScript sharedArtwork = GD.Load<GDScript>("res://Scenes/World/destruction_effect.gd");
        foreach (string id in new[] { "animated_blob", "flash_medium" })
        {
            using Variant returned = sharedArtwork.Call("admit_artwork", id);
            using Dictionary admitted = Result(returned);
        }
        using (Variant returned = controller.Call("admit_artwork"))
        using (Dictionary admitted = Result(returned)) { }
        using PackedScene scene = GD.Load<PackedScene>(scenePath);
        var native = scene.Instantiate<Node3D>();
        var sibling = scene.Instantiate<Node3D>();
        var retained = new RetainedPulseImpact(blobTexture, shockwaveTexture, flashTexture);
        var host = new FirstFlightWorldView();
        var allTweens = new List<Tween>();
        var sentinels = new List<StandardMaterial3D>();
        try
        {
            var lifetime = native.GetNode<Godot.Timer>("Lifetime");
            using (Variant returned = native.Call("start", globalSeconds))
            using (Dictionary refused = returned.AsGodotDictionary())
                Check(!refused["ok"].AsBool() && refused["error_type"].AsString() == "InvalidOperationException",
                    "PulseImpact explicitly refuses off-tree activation.");
            var before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            AddChild(native);
            AddChild(sibling);
            AddChild(retained.Root);
            Check(lifetime.IsStopped() && sibling.GetNode<Godot.Timer>("Lifetime").IsStopped() &&
                !native.IsProcessing() && !native.IsProcessingInput() && !native.IsProcessingUnhandledInput() &&
                GetTree().GetProcessedTweens().All(tween => before.Contains(tween.GetInstanceId())),
                "PulseImpact scene entry starts no timer, tween or input owner.");
            Check(Enumerable.Range(0, 16).Select(_ => GD.Randi()).SequenceEqual(expectedRandom),
                "PulseImpact artwork admission, scene loading/instantiation and refused start consume no RNG.");
            GD.Seed(seed);
            using (Variant returned = native.Call("start", globalSeconds))
            using (Dictionary started = Result(returned)) { }
            Tween[] nativeTweens = NewDestructionTweens(before, allTweens, 4, "PulseImpact native");
            Check(Enumerable.Range(0, 15).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(1)),
                "PulseImpact starts with exactly one original blob random draw.");
            before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            Node3D reference = retained.Spawn(Vector3.Zero, 37, 81, globalSeconds);
            Tween[] referenceTweens = NewDestructionTweens(before, allTweens, 4, "PulseImpact retained");
            Check(Enumerable.Range(0, 15).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(1)),
                "Retained PulseImpact confirms the same one-draw suffix.");
            before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            using (Variant returned = sibling.Call("start", globalSeconds))
            using (Dictionary started = Result(returned)) { }
            Tween[] siblingTweens = NewDestructionTweens(before, allTweens, 4, "PulseImpact sibling");
            var actualMaterials = DestructionMaterials(native);
            var referenceMaterials = DestructionMaterials(reference);
            var siblingMaterials = DestructionMaterials(sibling);
            Check(native.GetChildren().Select(child => child.Name.ToString()).SequenceEqual(reference.GetChildren().Select(child => child.Name.ToString())),
                "PulseImpact preserves Timer, blob, flash and sphere creation order.");
            CompareDestructionTimer(lifetime, reference.GetNode<Godot.Timer>("Lifetime"), 1.05d, "PulseImpact");
            CompareDestructionFrame(native, reference, actualMaterials, referenceMaterials, "PulseImpact before first callback");
            Compare(actualMaterials["BlueAnimatedBlob"].Uv1Offset, Vector3.Zero,
                "PulseImpact blob random cell remains unapplied until its first tween callback");
            Texture2D[] textures = [blobTexture, flashTexture, shockwaveTexture];
            string[] parts = ["BlueAnimatedBlob", "FlashMedium", "PulseBlastSphere"];
            string[] recipePaths = ["res://Scenes/World/EffectAnimatedBlobTexture.tres", "res://Scenes/World/EffectFlashMediumTexture.tres", "res://Scenes/World/PulseShockwaveTexture.tres"];
            for (int index = 0; index < parts.Length; index++)
            {
                string part = parts[index];
                var mesh = native.GetNode<MeshInstance3D>(part);
                var referenceMesh = reference.GetNode<MeshInstance3D>(part);
                StandardMaterial3D material = actualMaterials[part], expected = referenceMaterials[part];
                using Texture2D recipe = GD.Load<Texture2D>(recipePaths[index]);
                Check(material.AlbedoTexture == recipe && siblingMaterials[part].AlbedoTexture == recipe && material != siblingMaterials[part],
                    "PulseImpact independent materials share their admitted production recipe: " + part);
                using Image actualImage = recipe.GetImage();
                using Image expectedImage = textures[index].GetImage();
                Check(actualImage.GetWidth() == expectedImage.GetWidth() && actualImage.GetHeight() == expectedImage.GetHeight() &&
                    actualImage.GetFormat() == expectedImage.GetFormat() && actualImage.HasMipmaps() == expectedImage.HasMipmaps(),
                    "PulseImpact texture dimensions/format/mipmaps equal the retained loader: " + part);
                Check(actualImage.GetData().AsSpan().SequenceEqual(expectedImage.GetData()),
                    "Every PulseImpact production texture byte equals the retained loader: " + part);
                Check(material.ShadingMode == expected.ShadingMode && material.CullMode == expected.CullMode &&
                    material.Transparency == expected.Transparency && material.BlendMode == expected.BlendMode &&
                    material.BillboardMode == expected.BillboardMode && material.BillboardKeepScale == expected.BillboardKeepScale,
                    "PulseImpact material render properties retain the original recipe: " + part);
                if (index < 2)
                {
                    Check(mesh.Mesh is QuadMesh && referenceMesh.Mesh is QuadMesh, "PulseImpact blob/flash retain quad meshes.");
                    Vector2 size = ((QuadMesh)mesh.Mesh).Size, expectedSize = ((QuadMesh)referenceMesh.Mesh).Size;
                    Compare(new Vector3(size.X, size.Y, 0f), new Vector3(expectedSize.X, expectedSize.Y, 0f), "PulseImpact authored billboard half-extent law");
                }
                else
                {
                    Check(mesh.Mesh is SphereMesh && referenceMesh.Mesh is SphereMesh, "PulseImpact blast retains its production sphere mesh.");
                    var sphere = (SphereMesh)mesh.Mesh;
                    var expectedSphere = (SphereMesh)referenceMesh.Mesh;
                    Compare(new Vector3(sphere.Radius, sphere.Height, 0f), new Vector3(expectedSphere.Radius, expectedSphere.Height, 0f), "PulseImpact sphere radius/height");
                    Check(sphere.RadialSegments == expectedSphere.RadialSegments && sphere.Rings == expectedSphere.Rings &&
                        sphere.IsHemisphere == expectedSphere.IsHemisphere && sphere.FlipFaces == expectedSphere.FlipFaces,
                        "PulseImpact sphere preserves the original tessellation and winding defaults.");
                }
            }

            // Both old callbacks close over their initial material; an authored
            // replacement must not retarget atlas or shockwave UV/colour writes.
            var sentinelOffset = new Vector3(0.125f, 0.375f, 0.625f);
            var sentinelColor = new Color(0.125f, 0.25f, 0.5f, 0.75f);
            foreach (string part in new[] { "BlueAnimatedBlob", "PulseBlastSphere" })
            {
                var actualSentinel = new StandardMaterial3D { Uv1Offset = sentinelOffset, AlbedoColor = sentinelColor };
                var referenceSentinel = new StandardMaterial3D { Uv1Offset = sentinelOffset, AlbedoColor = sentinelColor };
                sentinels.Add(actualSentinel);
                sentinels.Add(referenceSentinel);
                native.GetNode<MeshInstance3D>(part).MaterialOverride = actualSentinel;
                reference.GetNode<MeshInstance3D>(part).MaterialOverride = referenceSentinel;
            }
            var siblingOffsets = siblingMaterials.ToDictionary(row => row.Key, row => row.Value.Uv1Offset);
            var siblingScales = sibling.GetChildren().OfType<MeshInstance3D>().ToDictionary(mesh => mesh.Name.ToString(), mesh => mesh.Scale);
            before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            using (Variant returned = native.Call("start", globalSeconds))
            using (Dictionary refused = returned.AsGodotDictionary())
                Check(!refused["ok"].AsBool() && refused["error_type"].AsString() == "InvalidOperationException",
                    "PulseImpact repeated start refuses before another mutation.");
            Check(GetTree().GetProcessedTweens().All(tween => before.Contains(tween.GetInstanceId())), "PulseImpact refused restart adds no tween.");
            bool[] nativeActive = [true, true, true, true], referenceActive = [true, true, true, true];
            const double interval = 1d / 14;
            var times = new[] { 0d, double.Epsilon, Math.BitDecrement(interval), interval, Math.BitIncrement(interval),
                0.25d, Math.BitDecrement(0.3d), 0.3d, Math.BitIncrement(0.3d),
                Math.BitDecrement(0.5d), 0.5d, Math.BitIncrement(0.5d), 0.75d,
                Math.BitDecrement(1d), 1d, Math.BitIncrement(1d), 1.05d, 1.125d, 1.25d };
            double previousTime = 0d;
            foreach (double time in times)
            {
                double delta = time - previousTime;
                previousTime = time;
                for (int index = 0; index < 4; index++)
                {
                    if (nativeActive[index]) nativeActive[index] = nativeTweens[index].CustomStep(delta);
                    if (referenceActive[index]) referenceActive[index] = referenceTweens[index].CustomStep(delta);
                    Check(nativeActive[index] == referenceActive[index] && nativeTweens[index].IsValid() == referenceTweens[index].IsValid(),
                        "PulseImpact ordered tween completion/validity matches the retained sequence.");
                    Check(BitConverter.DoubleToInt64Bits(nativeTweens[index].GetTotalElapsedTime()) == BitConverter.DoubleToInt64Bits(referenceTweens[index].GetTotalElapsedTime()),
                        "PulseImpact ordered tween elapsed words match the retained sequence.");
                }
                CompareDestructionFrame(native, reference, actualMaterials, referenceMaterials,
                    "PulseImpact sample " + time.ToString("R", System.Globalization.CultureInfo.InvariantCulture));
                foreach (StandardMaterial3D sentinel in sentinels)
                {
                    Compare(sentinel.Uv1Offset, sentinelOffset, "PulseImpact replacement UV remains untouched");
                    ComparePulseColor(sentinel.AlbedoColor, sentinelColor, "PulseImpact replacement colour remains untouched");
                }
                foreach (string part in parts)
                {
                    Compare(siblingMaterials[part].Uv1Offset, siblingOffsets[part], "Independent PulseImpact UV");
                    Compare(sibling.GetNode<MeshInstance3D>(part).Scale, siblingScales[part], "Independent PulseImpact scale");
                }
            }
            Check(nativeActive.All(active => !active) && referenceActive.All(active => !active), "Both PulseImpact owners complete within the paired observation schedule.");
            Compare(native.GetNode<MeshInstance3D>("BlueAnimatedBlob").Scale, Vector3.One * 1.07f, "PulseImpact exact legacy blob final ratio");
            Compare(native.GetNode<MeshInstance3D>("FlashMedium").Scale, Vector3.Zero, "PulseImpact final flash scale");
            Check(Enumerable.Range(0, 16).Select(_ => GD.Randi()).SequenceEqual(expectedRandom), "PulseImpact rejection and animation consume no further RNG.");
            CompareDestructionTimer(lifetime, reference.GetNode<Godot.Timer>("Lifetime"), 1.05d, "PulseImpact after manual animation");
            Check(!native.IsQueuedForDeletion() && !reference.IsQueuedForDeletion(), "PulseImpact tween stepping never substitutes for its lifetime timer.");
            lifetime.EmitSignal(Godot.Timer.SignalName.Timeout);
            reference.GetNode<Godot.Timer>("Lifetime").EmitSignal(Godot.Timer.SignalName.Timeout);
            Check(native.IsQueuedForDeletion() && reference.IsQueuedForDeletion(), "PulseImpact timeout signals queue the same lifetime roots.");

            before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            Node3D ownershipReference = retained.Spawn(Vector3.Zero, 42, 81, globalSeconds);
            Tween[] ownershipTweens = NewDestructionTweens(before, allTweens, 4, "PulseImpact ownership reference");
            var ownershipMaterials = DestructionMaterials(ownershipReference);
            sibling.GetNode<MeshInstance3D>("BlueAnimatedBlob").Free();
            ownershipReference.GetNode<MeshInstance3D>("BlueAnimatedBlob").Free();
            sibling.GetNode<MeshInstance3D>("FlashMedium").Free();
            ownershipReference.GetNode<MeshInstance3D>("FlashMedium").Free();
            for (int index = 1; index <= 2; index++)
                Check(!CompareVulcanOwnershipStep(siblingTweens[index], ownershipTweens[index], 0d, "child free " + index, "PulseImpact"),
                    "PulseImpact child-bound scales stop with the same retained ownership semantics.");
            Check(CompareVulcanOwnershipStep(siblingTweens[0], ownershipTweens[0], interval * 1.5d, "atlas after child free", "PulseImpact"),
                "PulseImpact root atlas survives freeing its blob child.");
            Compare(siblingMaterials["BlueAnimatedBlob"].Uv1Offset, ownershipMaterials["BlueAnimatedBlob"].Uv1Offset,
                "PulseImpact root atlas retains its captured material after child removal");
            Check(CompareVulcanOwnershipStep(siblingTweens[3], ownershipTweens[3], 0.125d, "blast with live root", "PulseImpact"),
                "PulseImpact shockwave remains bound to the root alongside its atlas.");
            Compare(sibling.GetNode<MeshInstance3D>("PulseBlastSphere").Scale, ownershipReference.GetNode<MeshInstance3D>("PulseBlastSphere").Scale,
                "PulseImpact retained root-bound shockwave scale");
            Compare(siblingMaterials["PulseBlastSphere"].Uv1Offset, ownershipMaterials["PulseBlastSphere"].Uv1Offset, "PulseImpact retained root-bound shockwave UV");
            ComparePulseColor(siblingMaterials["PulseBlastSphere"].AlbedoColor, ownershipMaterials["PulseBlastSphere"].AlbedoColor, "PulseImpact retained root-bound shockwave colour");
            sibling.Free();
            ownershipReference.Free();
            foreach (int index in new[] { 0, 3 })
                Check(!CompareVulcanOwnershipStep(siblingTweens[index], ownershipTweens[index], interval, "root free " + index, "PulseImpact"),
                    "PulseImpact atlas and shockwave stop after their lifetime root is freed.");

            ComparePulseBlastArithmetic(controller);

            AddChild(host);
            typeof(FirstFlightWorldView).GetField("_particlePresentationSeconds", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic)!
                .SetValue(host, globalSeconds);
            var position = new Level100Vector3(12345, -6789, 4321);
            var mapped = new Vector3(position.X * 0.001f, -position.Z * 0.001f, -position.Y * 0.001f);
            var impact = new Level100DestructionEvent(Level100DestructionEventKind.PulseImpact, Level100DestructionEffectKind.PulseImpact, 71, 0, 0, position);
            before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            host.ConsumeLevel100DestructionEvents([impact], 81);
            Node3D spawned = host.GetNode<Node3D>("PulseImpact71-81");
            NewDestructionTweens(before, allTweens, 4, "PulseImpact public event");
            Check(Enumerable.Range(0, 15).Select(_ => GD.Randi()).SequenceEqual(expectedRandom.Skip(1)), "PulseImpact public event retains the original single RNG draw.");
            using (Variant script = spawned.GetScript())
                Check(script.As<GodotObject>() == controller && spawned.SceneFilePath == scenePath && host.GetChildCount() == 1,
                    "The PulseImpact public event instantiates the actual native scene with the original actor/tick name.");
            Compare(spawned.Position, mapped, "PulseImpact public event X/-Z/-Y position");
            before = GetTree().GetProcessedTweens().Select(tween => tween.GetInstanceId()).ToHashSet();
            GD.Seed(seed);
            Node3D expectedSpawn = retained.Spawn(mapped, 71, 81, globalSeconds);
            NewDestructionTweens(before, allTweens, 4, "PulseImpact retained event");
            CompareDestructionFrame(spawned, expectedSpawn, DestructionMaterials(spawned), DestructionMaterials(expectedSpawn), "PulseImpact public event initial clock");
            CompareDestructionTimer(spawned.GetNode<Godot.Timer>("Lifetime"), expectedSpawn.GetNode<Godot.Timer>("Lifetime"), 1.05d, "PulseImpact public event");
            for (int index = 0; index < paths.Length; index++)
                Check(beforeHashes[index].AsSpan().SequenceEqual(System.Security.Cryptography.SHA256.HashData(
                    File.ReadAllBytes(ProjectSettings.GlobalizePath(paths[index])))), "PulseImpact checks preserve every prepared source byte.");
        }
        finally
        {
            foreach (Tween tween in allTweens) if (tween.IsValid()) tween.Kill();
            if (GodotObject.IsInstanceValid(native)) native.Free();
            if (GodotObject.IsInstanceValid(sibling)) sibling.Free();
            if (GodotObject.IsInstanceValid(retained.Root)) retained.Root.Free();
            if (GodotObject.IsInstanceValid(host)) host.Free();
            foreach (StandardMaterial3D sentinel in sentinels) sentinel.Dispose();
        }
    }

    private void ComparePulseColor(Color actual, Color retained, string name)
    {
        Compare(new Vector3(actual.R, actual.G, actual.B), new Vector3(retained.R, retained.G, retained.B), name);
        Check(BitConverter.SingleToUInt32Bits(actual.A) == BitConverter.SingleToUInt32Bits(retained.A), name + " alpha word");
    }

    private void ComparePulseBlastArithmetic(GDScript controller)
    {
        // Dense normalized-age samples detect MathF.Sin versus double-sin
        // rounding differences without turning every clock into another full
        // matrix. Boundary neighbours exercise the actual Single carrier.
        var ages = new HashSet<uint>();
        for (int index = 0; index <= 4096; index++) ages.Add(BitConverter.SingleToUInt32Bits(index / 4096f));
        foreach (float boundary in new[] { 0f, 0.125f, 0.25f, 0.5f, 0.75f, 1f })
        {
            if (boundary > 0f) ages.Add(BitConverter.SingleToUInt32Bits(MathF.BitDecrement(boundary)));
            if (boundary < 1f) ages.Add(BitConverter.SingleToUInt32Bits(MathF.BitIncrement(boundary)));
        }
        ages.Add(0x80000000u);
        int cases = 0;
        foreach (uint ageBits in ages.Order()) CheckOne(0.3125f, BitConverter.UInt32BitsToSingle(ageBits));
        foreach (float clock in new[] { 0f, BitConverter.UInt32BitsToSingle(0x80000000u), float.Epsilon, -float.Epsilon,
            MathF.BitDecrement(0.5f), 0.5f, MathF.BitIncrement(0.5f), -0.5f, 0.125f, -0.125f,
            1f, -1f, 2048.3125f, -2048.3125f, 65536.5f, 16777216f,
            float.MaxValue, -float.MaxValue, float.PositiveInfinity, float.NegativeInfinity,
            BitConverter.UInt32BitsToSingle(0x7fc00000u), BitConverter.UInt32BitsToSingle(0xffc00000u) })
            foreach (float age in new[] { 0f, BitConverter.UInt32BitsToSingle(0x80000000u), float.Epsilon,
                0.25f, MathF.BitDecrement(0.5f), 0.5f, MathF.BitIncrement(0.5f), 0.75f, 1f }) CheckOne(clock, age);
        GD.Print($"PULSE_BLAST_WORDS: {cases} exact initial-scroll/scale/UV/RGBA cases; nonfinite clock cases use pure values only.");

        void CheckOne(float clock, float age)
        {
            float expectedInitial = Mathf.PosMod(-2f * clock, 1f);
            using Variant initialValue = controller.Call("initial_scroll", clock);
            float actualInitial = initialValue.AsSingle();
            string name = $"Pulse blast clock={BitConverter.SingleToUInt32Bits(clock):x8} age={BitConverter.SingleToUInt32Bits(age):x8}";
            Check(BitConverter.SingleToUInt32Bits(actualInitial) == BitConverter.SingleToUInt32Bits(expectedInitial), name + " initial V word");
            using Variant values = controller.Call("blast_values", actualInitial, age);
            using Dictionary actual = values.AsGodotDictionary();
            // Exact operations retained from b8c1a220 AnimatePulseBlast's
            // captured Action<float>, independently of the native helper.
            float radius = (0.6f * MathF.Sin(age)) + 0.4f;
            Vector3 scale = Vector3.One * (radius / 0.5f);
            Vector3 uv = new(0f, expectedInitial - age, 0f);
            Color colour = Colors.White.Lerp(Colors.Black, age);
            Compare(actual["scale"].AsVector3(), scale, name + " scale");
            Compare(actual["uv_offset"].AsVector3(), uv, name + " UV");
            ComparePulseColor(actual["color"].AsColor(), colour, name + " colour");
            cases++;
        }
    }

    // Test-only b8c1a220 FirstFlightWorldView PulseImpact source. The spawn
    // and helper bodies below are unchanged, including first atlas callback,
    // Float32 MathF.Sin/PosMod/Color.Lerp operations and tween insertion order.
    // Root/AddChild supplies only the former containing world node.
    private sealed class RetainedPulseImpact
    {
        public Node3D Root { get; } = new();
        private readonly Texture2D _pulseImpactAnimatedTexture;
        private readonly Texture2D _pulseImpactShockwaveTexture;
        private readonly Texture2D _effectFlashMediumTexture;
        private float _particlePresentationSeconds;

        public RetainedPulseImpact(Texture2D blob, Texture2D shockwave, Texture2D flash)
        {
            _pulseImpactAnimatedTexture = blob;
            _pulseImpactShockwaveTexture = shockwave;
            _effectFlashMediumTexture = flash;
        }

        public Node3D Spawn(Vector3 position, int actorId, int tick, float globalSeconds)
        {
            _particlePresentationSeconds = globalSeconds;
            SpawnPulseImpact(position, actorId, tick);
            return Root.GetChild<Node3D>(Root.GetChildCount() - 1);
        }

        private void AddChild(Node child) => Root.AddChild(child);

        private void SpawnPulseImpact(Vector3 position, int targetId, int tick)
        {
            Node3D root = CreateTimedEffect($"PulseImpact{targetId}-{tick}", position, 1.05d);
            // `Blue Anim Blob Large Sprite`: Radius 0.7, Final_Radius 0.75,
            // Life 20 turns = 1.0 s, End_Frame 14 (15 cells), Random_Start_Frame 1,
            // Texture_Size 2 (a 4x4 grid) - every one of which the animation below
            // already reproduces.
            MeshInstance3D animatedBlob = CreateEffectSprite(
                "BlueAnimatedBlob",
                _pulseImpactAnimatedTexture,
                0.7f,
                columns: 4,
                rows: 4);
            root.AddChild(animatedBlob);
            AnimatePulseImpactBlob(root, animatedBlob);
            AnimateScale(animatedBlob, 1f, 1.07f, 1d);

            // `Flash Medium`: Radius 1.5, Life 6 turns = 0.3 s, Texture_Size 4 (a
            // single cell), sun2.tga.
            MeshInstance3D flash = CreateEffectSprite(
                "FlashMedium",
                _effectFlashMediumTexture,
                1.5f);
            root.AddChild(flash);
            AnimateScale(flash, 1f, 0f, 0.3d);

            MeshInstance3D blastSphere = CreatePulseBlastSphere(
                _pulseImpactShockwaveTexture);
            root.AddChild(blastSphere);
            AnimatePulseBlast(
                root,
                blastSphere,
                _particlePresentationSeconds,
                0.5d);
        }

        private Node3D CreateTimedEffect(string name, Vector3 position, double lifetimeSeconds)
        {
            var root = new Node3D
            {
                Name = name,
                Position = position,
            };
            AddChild(root);
            var lifetime = new Godot.Timer
            {
                Name = "Lifetime",
                OneShot = true,
                WaitTime = lifetimeSeconds,
            };
            lifetime.Timeout += root.QueueFree;
            root.AddChild(lifetime);
            lifetime.Start();
            return root;
        }

        /// <summary>
        /// Builds one billboard for a sprite descriptor.
        /// </summary>
        /// <param name="authoredRadius">
        /// The descriptor's <c>Radius</c>, exactly as its <c>MainSet.par</c> record
        /// spells it. It is a HALF extent; the quad side is derived by the one
        /// owner of that law,
        /// <see cref="ParticleEffectResolver.BillboardQuadSide(float)"/>. Pass the
        /// authored number, never a pre-doubled one - a bare literal cannot be
        /// traced back to the record it came from, which is exactly how this
        /// convention came to look inconsistent (task #151).
        /// </param>
        private static MeshInstance3D CreateEffectSprite(
            string name,
            Texture2D texture,
            float authoredRadius,
            int columns = 1,
            int rows = 1)
        {
            StandardMaterial3D material = CreateEffectMaterial(texture, billboard: true);
            material.Uv1Scale = new Vector3(1f / columns, 1f / rows, 1f);
            float side = ParticleEffectResolver.BillboardQuadSide(authoredRadius);
            return new MeshInstance3D
            {
                Name = name,
                Mesh = new QuadMesh { Size = new Vector2(side, side) },
                MaterialOverride = material,
            };
        }

        private static MeshInstance3D CreatePulseBlastSphere(Texture2D texture)
        {
            StandardMaterial3D material = CreateEffectMaterial(texture, billboard: false);
            material.Uv1Scale = new Vector3(2f, 2f, 1f);
            return new MeshInstance3D
            {
                Name = "PulseBlastSphere",
                Mesh = new SphereMesh
                {
                    Radius = 0.5f,
                    Height = 1f,
                    RadialSegments = 10,
                    Rings = 10,
                },
                MaterialOverride = material,
            };
        }

        private static void AnimatePulseBlast(
            Node root,
            MeshInstance3D sphere,
            float globalSeconds,
            double durationSeconds)
        {
            var material = (StandardMaterial3D)sphere.MaterialOverride;
            float initialV = Mathf.PosMod(-2f * globalSeconds, 1f);
            Action<float> update = normalizedAge =>
            {
                // MainSet's Shockwave Medium Growth is
                // radius = 0.6*sin(normalized age)+0.4. The mesh has radius 0.5.
                float radius = (0.6f * MathF.Sin(normalizedAge)) + 0.4f;
                sphere.Scale = Vector3.One * (radius / 0.5f);
                material.Uv1Offset = new Vector3(0f, initialV - normalizedAge, 0f);
                material.AlbedoColor = Colors.White.Lerp(Colors.Black, normalizedAge);
            };
            update(0f);
            root.CreateTween().TweenMethod(
                Callable.From<float>(update),
                0f,
                1f,
                durationSeconds);
        }

        private static void AnimatePulseImpactBlob(Node root, MeshInstance3D sprite)
        {
            var material = (StandardMaterial3D)sprite.MaterialOverride;
            int startFrame = (int)(GD.Randi() % 15u);
            Tween tween = root.CreateTween();
            const int frameAdvances = 14;
            const double frameIntervalSeconds = 1d / frameAdvances;
            for (int step = 0; step <= frameAdvances; step++)
            {
                int capturedFrame = (startFrame + step) % 15;
                tween.TweenCallback(Callable.From(() =>
                {
                    material.Uv1Offset = new Vector3(
                        (capturedFrame % 4) / 4f,
                        (capturedFrame / 4) / 4f,
                        0f);
                }));
                if (step < frameAdvances)
                {
                    tween.TweenInterval(frameIntervalSeconds);
                }
            }
        }

        private static void AnimateScale(Node3D node, float start, float end, double durationSeconds)
        {
            node.Scale = Vector3.One * start;
            node.CreateTween().TweenProperty(
                node,
                new NodePath("scale"),
                Vector3.One * end,
                durationSeconds);
        }

        private static StandardMaterial3D CreateEffectMaterial(
            Texture2D texture,
            bool billboard)
        {
            return new StandardMaterial3D
            {
                AlbedoTexture = texture,
                ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
                CullMode = BaseMaterial3D.CullModeEnum.Disabled,
                Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
                BlendMode = BaseMaterial3D.BlendModeEnum.Add,
                BillboardMode = billboard
                    ? BaseMaterial3D.BillboardModeEnum.Enabled
                    : BaseMaterial3D.BillboardModeEnum.Disabled,
                BillboardKeepScale = billboard,
            };
        }

    }

    // Test-only 673b630a FirstFlightWorldView source. The following spawn,
    // material and animation bodies retain their executable text, float stores,
    // callback captures and provenance. Root/AddChild only supplies their former
    // containing world; the native scene is never used to construct this oracle.
    private sealed class RetainedDestructionEffects
    {
        public Node3D Root { get; } = new();
        private readonly Texture2D _pulseImpactAnimatedTexture;
        private readonly Texture2D _effectFlashMediumTexture;
        private readonly Texture2D _targetTankExplosionAnimatedTexture;
        private readonly Texture2D _targetTankExplosionFireballTexture;

        public RetainedDestructionEffects(Texture2D[] textures)
        {
            _pulseImpactAnimatedTexture = textures[0];
            _effectFlashMediumTexture = textures[1];
            _targetTankExplosionAnimatedTexture = textures[2];
            _targetTankExplosionFireballTexture = textures[3];
        }

        public Node3D Spawn(Level100DestructionEffectKind kind, Vector3 position, int actorId)
        {
            switch (kind)
            {
                case Level100DestructionEffectKind.TargetDestroyed:
                    SpawnTargetTankDestruction(position, actorId);
                    break;
                case Level100DestructionEffectKind.DroneDestroyed:
                    SpawnTargetDroneDestruction(position, actorId);
                    break;
                case Level100DestructionEffectKind.FacilityDestroyed:
                    SpawnFacilityDestruction(position, actorId);
                    break;
                default: throw new ArgumentOutOfRangeException(nameof(kind));
            }
            return Root.GetChild<Node3D>(Root.GetChildCount() - 1);
        }

        private void AddChild(Node child) => Root.AddChild(child);

        private void SpawnTargetTankDestruction(Vector3 position, int targetId)
        {
            Node3D root = CreateTimedEffect($"TargetTankDestruction{targetId}", position, 1.5d);
            // `Tank Explosion Medium` dispatches the shared `Flash` sprite at Time
            // 0: sun2.tga, Radius 5, Final_Radius 0 and Life 5 turns (0.25 s).
            MeshInstance3D flash = CreateEffectSprite(
                "TargetTankFlash",
                _effectFlashMediumTexture,
                5f);
            root.AddChild(flash);
            AnimateScale(flash, 1f, 0f, 0.25d);

            // `Explosion Anim Sprite Medium`: Radius 1.5, Final_Radius 1.3,
            // Life 10 turns = 0.5 s, End_Frame 7 (8 cells), Texture_Size 2,
            // PlayOnce at 0.7 cells/turn. Tank Explosion Medium schedules it at
            // Time 5, so this direct layer remains hidden for the first 0.25 s.
            MeshInstance3D animatedExplosion = CreateEffectSprite(
                "ExplosionAnimatedSprite",
                _targetTankExplosionAnimatedTexture,
                1.5f,
                columns: 4,
                rows: 4);
            root.AddChild(animatedExplosion);
            AnimateTargetTankDelayedExplosion(root, animatedExplosion);

            // `Fire Sprite Damped 2`: Radius 1.0, Final_Radius 0.5,
            // Life 30 turns = 1.5 s, Texture_Size 2, fireball.tga. It loops only
            // cells 0..11 at 0.5 cells/turn from one authored random start; cells
            // 12..15 are deliberately blank and are not part of this sprite.
            MeshInstance3D fireball = CreateEffectSprite(
                "ExplosionFireball",
                _targetTankExplosionFireballTexture,
                1.0f,
                columns: 4,
                rows: 4);
            root.AddChild(fireball);
            AnimateTargetTankFireball(root, fireball);
            AnimateScale(fireball, 1f, 0.5f, 1.5d);
        }

        private void SpawnTargetDroneDestruction(Vector3 position, int droneId)
        {
            Node3D root = CreateTimedEffect(
                $"TargetDroneDestruction{droneId}",
                position,
                1.5d);
            // `Drone Explosion Effect` dispatches `Flash` directly at Time 0.
            // That retained sprite is sun2.tga, Radius 5, Final_Radius 0 and Life
            // 5 released 20 Hz turns. Its debris/emitter multiplicity, placement,
            // velocity and colour evolution remain open rather than being guessed.
            MeshInstance3D flash = CreateEffectSprite(
                "DroneFlash",
                _effectFlashMediumTexture,
                5f);
            root.AddChild(flash);
            AnimateScale(flash, 1f, 0f, 0.25d);

            // `Drone Explosion Emitter` is the other Time-0 branch retained by
            // `Drone Explosion Effect`. One explicitly representative
            // `Fire Sprite Damped 2` preserves its bright tail: additive
            // fireball.tga, Radius 1.0 -> 0.5, Life 30 turns = 1.5 s, and
            // random-start looping cells 0..11 at 0.5 cells/turn. The emitter's
            // decreasing multiplicity, shape, placement and velocity remain open.
            MeshInstance3D fireball = CreateEffectSprite(
                "DroneFireball",
                _targetTankExplosionFireballTexture,
                1f,
                columns: 4,
                rows: 4);
            root.AddChild(fireball);
            AnimateLoopingFireball(root, fireball, lifeTurns: 30);
            AnimateScale(fireball, 1f, 0.5f, 1.5d);
        }

        private void SpawnFacilityDestruction(Vector3 position, int facilityId)
        {
            Node3D root = CreateTimedEffect(
                $"FacilityDestruction{facilityId}",
                position,
                15d);
            // `Flash Building`: direct Time-0 entry in Muspell Building Explosion
            // Effect. Radius 3, Final_Radius 0, Life 6 released 20 Hz turns = 0.30 s,
            // Texture_Size 4 (one cell), sun2.tga.
            MeshInstance3D flash = CreateEffectSprite(
                "FacilityFlash",
                _effectFlashMediumTexture,
                3f);
            root.AddChild(flash);
            AnimateScale(flash, 1f, 0f, 0.3d);

            // `Fire Sprite Damped Long`: one explicitly representative billboard
            // from the authored Time-0 Muspell Building Explosion Emitter. Radius
            // 0.5 -> 2.0, Life 60 turns = 3.0 s, random-start looping cells 0..11
            // at 0.5 cells/turn. The emitter's unresolved decreasing multiplicity,
            // placement and velocity laws remain open rather than being invented.
            MeshInstance3D fireball = CreateEffectSprite(
                "FacilityFireball",
                _targetTankExplosionFireballTexture,
                0.5f,
                columns: 4,
                rows: 4);
            root.AddChild(fireball);
            AnimateFacilityFireball(root, fireball);
            AnimateScale(fireball, 1f, 4f, 3d);

            // `Smoke Sprite Anim Large Building`: the single Time-0 smoke emitted
            // by Building Smoke Emitter. It is an alpha-blended 4x4 alparticle4
            // billboard, radius 3 -> 2, random-start looping cells 0..14 at 0.5
            // cells/turn for 300 turns = 15 seconds. Shape placement, velocity
            // randomness and Fade_Col/Life_Pct colour behavior remain open.
            MeshInstance3D smoke = CreateEffectSprite(
                "FacilitySmoke",
                _pulseImpactAnimatedTexture,
                3f,
                columns: 4,
                rows: 4);
            ((StandardMaterial3D)smoke.MaterialOverride).BlendMode =
                BaseMaterial3D.BlendModeEnum.Mix;
            root.AddChild(smoke);
            AnimateFacilitySmoke(root, smoke);
            AnimateScale(smoke, 1f, 2f / 3f, 15d);
        }

        private Node3D CreateTimedEffect(string name, Vector3 position, double lifetimeSeconds)
        {
            var root = new Node3D
            {
                Name = name,
                Position = position,
            };
            AddChild(root);
            var lifetime = new Godot.Timer
            {
                Name = "Lifetime",
                OneShot = true,
                WaitTime = lifetimeSeconds,
            };
            lifetime.Timeout += root.QueueFree;
            root.AddChild(lifetime);
            lifetime.Start();
            return root;
        }

        /// <summary>
        /// Builds one billboard for a sprite descriptor.
        /// </summary>
        /// <param name="authoredRadius">
        /// The descriptor's <c>Radius</c>, exactly as its <c>MainSet.par</c> record
        /// spells it. It is a HALF extent; the quad side is derived by the one
        /// owner of that law,
        /// <see cref="ParticleEffectResolver.BillboardQuadSide(float)"/>. Pass the
        /// authored number, never a pre-doubled one - a bare literal cannot be
        /// traced back to the record it came from, which is exactly how this
        /// convention came to look inconsistent (task #151).
        /// </param>
        private static MeshInstance3D CreateEffectSprite(
            string name,
            Texture2D texture,
            float authoredRadius,
            int columns = 1,
            int rows = 1)
        {
            StandardMaterial3D material = CreateEffectMaterial(texture, billboard: true);
            material.Uv1Scale = new Vector3(1f / columns, 1f / rows, 1f);
            float side = ParticleEffectResolver.BillboardQuadSide(authoredRadius);
            return new MeshInstance3D
            {
                Name = name,
                Mesh = new QuadMesh { Size = new Vector2(side, side) },
                MaterialOverride = material,
            };
        }

        private static void AnimateTargetTankDelayedExplosion(
            Node root,
            MeshInstance3D sprite)
        {
            const int startCell = 0;
            const int endCell = 7;
            const int columns = 4;
            const int rows = 4;
            const double cellsPerTurn = 0.7d;
            const double lifeSeconds = 0.5d;
            double startDelaySeconds = 5d / SimulationConstants.TicksPerSecond;
            double cellIntervalSeconds =
                1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
            var material = (StandardMaterial3D)sprite.MaterialOverride;
            material.Uv1Offset = new Vector3(
                (startCell % columns) / (float)columns,
                (startCell / columns) / (float)rows,
                0f);
            sprite.Visible = false;
            sprite.Scale = Vector3.One;

            Tween atlasTween = root.CreateTween();
            atlasTween.TweenInterval(startDelaySeconds);
            atlasTween.TweenCallback(Callable.From(() =>
            {
                sprite.Visible = true;
            }));
            for (int cell = startCell + 1; cell <= endCell; cell++)
            {
                int capturedCell = cell;
                atlasTween.TweenInterval(cellIntervalSeconds);
                atlasTween.TweenCallback(Callable.From(() =>
                {
                    material.Uv1Offset = new Vector3(
                        (capturedCell % columns) / (float)columns,
                        (capturedCell / columns) / (float)rows,
                        0f);
                }));
            }

            Tween scaleTween = root.CreateTween();
            scaleTween.TweenInterval(startDelaySeconds);
            scaleTween.TweenProperty(
                sprite,
                new NodePath("scale"),
                Vector3.One * (1.3f / 1.5f),
                lifeSeconds);
            scaleTween.TweenCallback(Callable.From(() =>
            {
                sprite.Visible = false;
            }));
        }

        private static void AnimateTargetTankFireball(
            Node root,
            MeshInstance3D sprite) =>
            AnimateLoopingFireball(root, sprite, lifeTurns: 30);

        private static void AnimateFacilityFireball(
            Node root,
            MeshInstance3D sprite) =>
            AnimateLoopingFireball(root, sprite, lifeTurns: 60);

        private static void AnimateLoopingFireball(
            Node root,
            MeshInstance3D sprite,
            int lifeTurns)
        {
            const int startCell = 0;
            const int endCell = 11;
            const int columns = 4;
            const int rows = 4;
            const double cellsPerTurn = 0.5d;
            int cellCount = endCell - startCell + 1;
            int initialCell = startCell + (int)(GD.Randi() % (uint)cellCount);
            double cellIntervalSeconds =
                1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
            int frameAdvances = (int)(lifeTurns * cellsPerTurn);
            var material = (StandardMaterial3D)sprite.MaterialOverride;
            material.Uv1Offset = new Vector3(
                (initialCell % columns) / (float)columns,
                (initialCell / columns) / (float)rows,
                0f);

            Tween tween = root.CreateTween();
            for (int step = 1; step <= frameAdvances; step++)
            {
                int capturedCell = startCell + ((initialCell - startCell + step) % cellCount);
                tween.TweenInterval(cellIntervalSeconds);
                tween.TweenCallback(Callable.From(() =>
                {
                    material.Uv1Offset = new Vector3(
                        (capturedCell % columns) / (float)columns,
                        (capturedCell / columns) / (float)rows,
                        0f);
                }));
            }
            tween.TweenCallback(Callable.From(() => sprite.Visible = false));
        }

        private static void AnimateFacilitySmoke(Node root, MeshInstance3D sprite)
        {
            const int startCell = 0;
            const int endCell = 14;
            const int columns = 4;
            const int rows = 4;
            const int lifeTurns = 300;
            const double cellsPerTurn = 0.5d;
            int cellCount = endCell - startCell + 1;
            int initialCell = startCell + (int)(GD.Randi() % (uint)cellCount);
            double cellIntervalSeconds =
                1d / (cellsPerTurn * SimulationConstants.TicksPerSecond);
            int frameAdvances = (int)(lifeTurns * cellsPerTurn);
            var material = (StandardMaterial3D)sprite.MaterialOverride;
            material.Uv1Offset = new Vector3(
                (initialCell % columns) / (float)columns,
                (initialCell / columns) / (float)rows,
                0f);

            Tween tween = root.CreateTween();
            for (int step = 1; step <= frameAdvances; step++)
            {
                int capturedCell = startCell + ((initialCell - startCell + step) % cellCount);
                tween.TweenInterval(cellIntervalSeconds);
                tween.TweenCallback(Callable.From(() =>
                {
                    material.Uv1Offset = new Vector3(
                        (capturedCell % columns) / (float)columns,
                        (capturedCell / columns) / (float)rows,
                        0f);
                }));
            }
        }

        private static void AnimateScale(Node3D node, float start, float end, double durationSeconds)
        {
            node.Scale = Vector3.One * start;
            node.CreateTween().TweenProperty(
                node,
                new NodePath("scale"),
                Vector3.One * end,
                durationSeconds);
        }

        private static StandardMaterial3D CreateEffectMaterial(
            Texture2D texture,
            bool billboard)
        {
            return new StandardMaterial3D
            {
                AlbedoTexture = texture,
                ShadingMode = BaseMaterial3D.ShadingModeEnum.Unshaded,
                CullMode = BaseMaterial3D.CullModeEnum.Disabled,
                Transparency = BaseMaterial3D.TransparencyEnum.Alpha,
                BlendMode = BaseMaterial3D.BlendModeEnum.Add,
                BillboardMode = billboard
                    ? BaseMaterial3D.BillboardModeEnum.Enabled
                    : BaseMaterial3D.BillboardModeEnum.Disabled,
                BillboardKeepScale = billboard,
            };
        }

    }

    private void CompareTargets(Node owner, Node3D world, WorldSnapshot previous, WorldSnapshot current, float alpha)
    {
        var prior = new System.Collections.Generic.Dictionary<Level100ActorId, Level100TargetVisualDescriptor>();
        foreach (TargetSnapshot item in previous.Targets) prior[item.ActorId] = Level100TargetPresentation.Project(item);
        foreach (TargetSnapshot item in current.Targets)
        {
            Level100TargetVisualDescriptor descriptor = Level100TargetPresentation.Project(item);
            Level100TargetVisualDescriptor expected = Level100RenderInterpolation.Interpolate(
                prior.TryGetValue(item.ActorId, out var found) ? found : null, descriptor, alpha);
            _referenceTargets[item.ActorId] = expected;
        }
        foreach ((Level100ActorId id, Level100TargetVisualDescriptor expected) in _referenceTargets)
        {
            var actual = world.GetNode<Node3D>($"RetailLevel100TargetActor{id.Value}");
            Compare(actual.Transform, new(new Basis(Vector(expected.Basis.XAxis), Vector(expected.Basis.YAxis), Vector(expected.Basis.ZAxis)), Vector(expected.Position)), $"actor {id.Value}");
            Check(actual.Visible == expected.Visible, "Actor visibility follows the current explicit flag.");
            Check(actual.GetMeta("actor_id").AsInt32() == id.Value, "Actor identity remains authored metadata.");
        }
    }

    private void CompareProjectiles(Node owner, Node3D world, Node3D referenceWorld, Camera3D camera,
        WorldSnapshot previous, WorldSnapshot current, float alpha)
    {
        var prior = new System.Collections.Generic.Dictionary<int, ProjectileSnapshot>();
        foreach (ProjectileSnapshot item in previous.Projectiles) prior[item.Id] = item;
        var active = new HashSet<int>();
        foreach (ProjectileSnapshot item in current.Projectiles)
        {
            active.Add(item.Id);
            if (!_referenceProjectiles.TryGetValue(item.Id, out Node3D? reference))
            {
                reference = new Node3D();
                referenceWorld.AddChild(reference);
                _referenceProjectiles.Add(item.Id, reference);
                _referenceTrails.Add(item.Id, new(Level100ProjectileTrailHistory.AuthoredPointCount(item.Kind), Level100ProjectileTrailHistory.AuthoredLifetimeTicks(item.Kind)));
            }
            Level100ProjectileVisualState expected = Level100RenderInterpolation.Interpolate(
                prior.TryGetValue(item.Id, out ProjectileSnapshot? previousItem) ? State(previousItem, Position(previousItem)) : null,
                State(item, Spawn(item)), State(item, Position(item)), alpha);
            reference.Position = Vector(expected.Position);
            Vector3 direction = Vector(expected.Direction);
            if (!direction.IsZeroApprox()) reference.LookAt(reference.Position + direction.Normalized(), Vector3.Up);
            string prefix = item.Id < 200 ? "RetailPulseBolt" : "RetailVulcanBullet";
            Node3D actual = world.GetNode<Node3D>(prefix + item.Id);
            Compare(actual.Transform, reference.Transform, "projectile " + item.Id);
            Level100ProjectileTrailHistory trail = _referenceTrails[item.Id];
            trail.Advance(Position(item), new(item.Velocity.X * 0.001f, item.VerticalVelocityMillimetersPerTick * 0.001f, -item.Velocity.Z * 0.001f), item.RemainingTicks);
            IReadOnlyList<Level100RenderVector3> points = trail.WithRenderedHead(expected.Position);
            MeshInstance3D mesh = actual.GetNode<MeshInstance3D>("ProjectileTrail");
            Check(mesh.Visible == (points.Count >= 2), "Trail visibility retains the one-point gate.");
            if (points.Count >= 2)
                CompareTrail(mesh, points, referenceWorld, camera.GlobalPosition, reference.GlobalTransform.AffineInverse(), item.Kind == Level100ProjectileKind.MechPulseBoltMedium ? 0.08f : 0.02f);
        }
        foreach (int id in _referenceProjectiles.Keys.Where(id => !active.Contains(id)).ToArray())
        {
            _referenceProjectiles[id].Free();
            _referenceProjectiles.Remove(id);
            _referenceTrails.Remove(id);
        }
        using Variant snapshotValue = owner.Call("diagnostic_snapshot");
        using Dictionary snapshot = snapshotValue.AsGodotDictionary();
        using Variant trailValues = snapshot["trails"];
        using Dictionary trails = trailValues.AsGodotDictionary();
        Check(trails.Count == _referenceTrails.Count, "Native trail histories retire alongside projectiles.");
        foreach ((int id, Level100ProjectileTrailHistory expected) in _referenceTrails)
        {
            using Variant trailValue = trails[id];
            using Dictionary trail = trailValue.AsGodotDictionary();
            using Variant pointValues = trail["points"];
            using Array points = pointValues.AsGodotArray();
            Check(points.Count == expected.Points.Count, "Native trail capacity matches its authored kind.");
            for (int index = 0; index < points.Count; index++)
            {
                using Variant pointValue = points[index];
                using Dictionary point = pointValue.AsGodotDictionary();
                Compare(RawVector(point), Vector(expected.Points[index]), "history point");
            }
        }
    }

    private void CompareTrail(MeshInstance3D actual, IReadOnlyList<Level100RenderVector3> points,
        Node3D world, Vector3 camera, Transform3D worldToProjectile, float width)
    {
        using Array arrays = actual.Mesh.SurfaceGetArrays(0);
        using Variant vertexValues = arrays[(int)Mesh.ArrayType.Vertex];
        using Variant uvValues = arrays[(int)Mesh.ArrayType.TexUV];
        Vector3[] vertices = vertexValues.AsVector3Array();
        Vector2[] uv = uvValues.AsVector2Array();
        Check(vertices.Length == points.Count * 2 && uv.Length == vertices.Length, "Trail emits one ordered strip pair per retained point.");
        float halfWidth = width * 0.5f;
        for (int index = 0; index < points.Count; index++)
        {
            Vector3 point = world.ToGlobal(Vector(points[index]));
            Vector3 neighbour = world.ToGlobal(Vector(points[index + 1 < points.Count ? index + 1 : index - 1]));
            Vector3 direction = index + 1 < points.Count ? neighbour - point : point - neighbour;
            if (direction.IsZeroApprox()) direction = Vector3.Forward;
            Vector3 side = direction.Cross(camera - point);
            if (side.IsZeroApprox()) side = direction.Cross(Vector3.Up);
            if (side.IsZeroApprox()) side = Vector3.Right;
            side = side.Normalized() * halfWidth;
            Compare(vertices[index * 2], worldToProjectile * (point - side), "trail left vertex");
            Compare(vertices[index * 2 + 1], worldToProjectile * (point + side), "trail right vertex");
            float u = index / (float)(points.Count - 1);
            Check(uv[index * 2] == new Vector2(u, 0) && uv[index * 2 + 1] == new Vector2(u, 1), "Trail UV order and float32 fraction match.");
        }
    }

    private void CompareFeet(WorldSnapshot previous, WorldSnapshot current, float alpha, bool reset, Array actual)
    {
        Vector3[] expected = FootOffsets(current);
        if (!reset)
        {
            Vector3[] prior = FootOffsets(previous);
            for (int index = 0; index < 4; index++) expected[index] = Vector(Level100RenderInterpolation.InterpolatePosition(Render(prior[index]), Render(expected[index]), alpha, 3f));
        }
        Check(actual.Count == 4, "The Aquila stage receives exactly four contacts.");
        for (int index = 0; index < 4; index++)
        {
            using Variant pointValue = actual[index];
            using Dictionary point = pointValue.AsGodotDictionary();
            Compare(RawVector(point), expected[index], "foot interpolation");
        }
    }

    // Retained pre-controller host fixture from FirstFlightWorldView.Entities
    // at 1bb29345. Production now submits raw snapshot facts to its native
    // world owner; this conversion remains only as an independent leaf oracle.
    private static Dictionary EntityFrameFacts(WorldSnapshot previous, WorldSnapshot current,
        float alpha, bool resetJump, int pendingMuzzles)
    {
        Array currentFeet = EntityVectors(FootOffsets(current));
        Variant previousFeet = default;
        bool same = ReferenceEquals(previous, current);
        if (!resetJump && !same && previous.WalkerFeet.Count == current.WalkerFeet.Count)
            previousFeet = EntityVectors(FootOffsets(previous));
        return new Dictionary
        {
            ["alpha_bits"] = (long)BitConverter.SingleToUInt32Bits(alpha),
            ["same_snapshot"] = same, ["current_feet"] = currentFeet,
            ["previous_feet"] = previousFeet,
            ["previous_targets"] = same ? new Array() : FirstFlightWorldView.EntityTargetFacts(previous.Targets),
            ["current_targets"] = FirstFlightWorldView.EntityTargetFacts(current.Targets),
            ["previous_projectiles"] = same ? new Array() : FirstFlightWorldView.EntityProjectileFacts(previous.Projectiles),
            ["current_projectiles"] = FirstFlightWorldView.EntityProjectileFacts(current.Projectiles),
            ["pending_muzzles"] = pendingMuzzles,
        };
    }

    private static Array EntityVectors(IEnumerable<Vector3> values)
    {
        var result = new Array();
        foreach (Vector3 value in values)
            result.Add(new Dictionary { ["x_bits"] = (long)BitConverter.SingleToUInt32Bits(value.X),
                ["y_bits"] = (long)BitConverter.SingleToUInt32Bits(value.Y), ["z_bits"] = (long)BitConverter.SingleToUInt32Bits(value.Z) });
        return result;
    }

    private static Vector3[] FootOffsets(WorldSnapshot snapshot)
    {
        if (snapshot.WalkerFeet.Count != 4)
            throw new InvalidDataException("Core did not expose four Aquila foot contacts.");
        var result = new Vector3[4];
        foreach (WalkerFootContactSnapshot foot in snapshot.WalkerFeet)
        {
            if (foot.Id < 0 || foot.Id >= result.Length)
                throw new InvalidDataException($"Core exposed unknown Aquila foot {foot.Id}.");
            result[foot.Id] = new((foot.Position.X - snapshot.PlayerPosition.X) * 0.001f,
                (foot.GroundElevationMillimeters + foot.LiftMillimeters - snapshot.PlayerGroundElevationMillimeters) * 0.001f,
                -(foot.Position.Z - snapshot.PlayerPosition.Z) * 0.001f);
        }
        return result;
    }
    private static Level100ActorSnapshot Actor(int index, int step)
    {
        Level100TargetVisualBinding binding = Level100TargetPresentation.RenderedBindings[index];
        float yaw = (step * 0.03f) + index * 0.13f;
        int s = BitConverter.SingleToInt32Bits(MathF.Sin(yaw)), c = BitConverter.SingleToInt32Bits(MathF.Cos(yaw));
        return new(new(index + 1), "synthetic-entity-" + index, "Entity " + index,
            binding.DefinitionName, null, binding.MeshBinding, 0, null, null, false,
            (step + index) % 9 != 0, false, Level100ActorLifecycle.Alive, 3000,
            new(new(index * 5000 + step * (step == 10 ? 2000 : 30), 1700 + index * 101, -3000 + step * 45),
                new(c, 0, s, 0, 0x3f800000, 0, s ^ int.MinValue, 0, c), default, default),
            Level100MissionTargetGroup.None, 0, null, false, null, false);
    }
    private static Level100RenderVector3 Position(ProjectileSnapshot item) => new(item.Position.X * 0.001f, item.ElevationMillimeters * 0.001f, -item.Position.Z * 0.001f);
    private static Level100RenderVector3 Spawn(ProjectileSnapshot item) => new((item.Position.X - item.Velocity.X) * 0.001f,
        (item.ElevationMillimeters - item.VerticalVelocityMillimetersPerTick) * 0.001f, -(item.Position.Z - item.Velocity.Z) * 0.001f);
    private static Level100ProjectileVisualState State(ProjectileSnapshot item, Level100RenderVector3 position) => new(position, new(item.Velocity.X, item.VerticalVelocityMillimetersPerTick, -item.Velocity.Z));
    private static Vector3 Vector(Level100RenderVector3 value) => new(value.X, value.Y, value.Z);
    private static Level100RenderVector3 Render(Vector3 value) => new(value.X, value.Y, value.Z);
    private static Vector3 RawVector(Dictionary value) => new(BitConverter.UInt32BitsToSingle((uint)value["x_bits"].AsInt64()),
        BitConverter.UInt32BitsToSingle((uint)value["y_bits"].AsInt64()), BitConverter.UInt32BitsToSingle((uint)value["z_bits"].AsInt64()));
    private static Dictionary Result(Variant value)
    {
        if (value.VariantType != Variant.Type.Dictionary) throw new InvalidOperationException("Native scene aborted without a completion record.");
        Dictionary result = value.AsGodotDictionary();
        bool hasFlag = result.TryGetValue("ok", out Variant ok);
        using (ok)
            if (!hasFlag || ok.VariantType != Variant.Type.Bool || !ok.AsBool())
            {
                string error = "Native scene refused: " + result;
                result.Dispose();
                throw new InvalidOperationException(error);
            }
        return result;
    }
    private void Compare(Transform3D actual, Transform3D expected, string name)
    { Compare(actual.Origin, expected.Origin, name + " origin"); Compare(actual.Basis.X, expected.Basis.X, name + " X"); Compare(actual.Basis.Y, expected.Basis.Y, name + " Y"); Compare(actual.Basis.Z, expected.Basis.Z, name + " Z"); }
    private void Compare(Vector3 actual, Vector3 expected, string name)
    {
        for (int axis = 0; axis < 3; axis++)
            Check(BitConverter.SingleToUInt32Bits(actual[axis]) == BitConverter.SingleToUInt32Bits(expected[axis]),
                $"{name}[{axis}]: actual {BitConverter.SingleToUInt32Bits(actual[axis]):x8}, expected {BitConverter.SingleToUInt32Bits(expected[axis]):x8}.");
    }
    private void Check(bool condition, string message)
    { _checks++; if (!condition) throw new InvalidOperationException(message); }
}
