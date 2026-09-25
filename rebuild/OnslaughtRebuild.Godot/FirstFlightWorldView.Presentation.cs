// SPDX-License-Identifier: GPL-3.0-or-later
using System.Runtime.ExceptionServices;
using Godot;
using OnslaughtRebuild.Core;
using Array = Godot.Collections.Array;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView
{
    internal const string WorldPresentationScriptPath = "res://Scenes/World/world_presentation.gd";
    internal const string WorldPresentationScenePath = "res://Scenes/World/WorldPresentation.tscn";
    private Node _worldPresentation = null!;

    private void CreateWorldPresentation()
    {
        using PackedScene scene = GD.Load<PackedScene>(WorldPresentationScenePath);
        _worldPresentation = scene.Instantiate();
        AddChild(_worldPresentation);
        SetEditableInstance(_worldPresentation, true);
    }

    private void ConfigureWorldPresentation()
    {
        using var bindings = new Dictionary
        {
            ["world"] = this, ["player"] = _playerRoot, ["body"] = _playerBodyPivot,
            ["walker"] = _walkerAsset.Root, ["jet"] = _jetAsset.Root, ["cockpit"] = _cockpitAsset.Root,
            ["camera"] = _camera, ["sky"] = _level100Sky, ["sun"] = _level100Sun.Root,
            ["terrain"] = _level100Terrain.NativeOwner, ["appearance"] = _level100TerrainAppearance.NativeOwner,
            ["entities"] = _entityPresentation, ["water"] = _level100StaticWorld.Water.Root,
            ["scenery"] = _level100StaticWorld.Animation.NativeOwner,
        };
        using var config = new Dictionary
        {
            ["pan_duration_ticks"] = SimulationConstants.Level100OpeningPanTicks,
            ["control_view_handoff_lead_ticks"] = Level100MissionTiming.ReleasedEventFrameTicks,
            ["near_bits"] = (long)BitConverter.SingleToUInt32Bits(RetailNearPlane),
            ["far_bits"] = (long)BitConverter.SingleToUInt32Bits(RetailFarPlane),
            ["walker_height_mm"] = Level100Terrain.WalkerCenterOfGravityMillimeters,
            ["target_count"] = _targetVisualCount, ["projectile_count"] = _projectileVisualCount,
            ["target_surface_count"] = _targetSurfaceCount,
            ["terrain_vertex_count"] = _level100Terrain.VertexCount,
            ["terrain_triangle_count"] = _level100Terrain.TriangleCount,
        };
        using Variant bindingValues = bindings;
        using Variant configValues = config;
        using Variant returned = _worldPresentation.Call("configure", bindingValues, configValues);
        using Dictionary result = WorldPresentationResult(returned);
    }

    // Only immutable facts cross per frame. No transform, clock, camera state,
    // foot arithmetic or actor/projectile lifecycle is owned by this facade.
    private static Dictionary WorldFrameFacts(WorldSnapshot previous, WorldSnapshot current,
        float alpha, float delta, List<ExceptionDispatchInfo> failures)
    {
        bool same = ReferenceEquals(previous, current);
        using Variant before = WorldSnapshotFacts(previous, same, failures);
        using Variant after = WorldSnapshotFacts(current, false, failures);
        return new Dictionary
        {
            ["previous"] = before, ["current"] = after, ["same_snapshot"] = same,
            ["alpha_bits"] = (long)BitConverter.SingleToUInt32Bits(alpha),
            ["delta_bits"] = (long)BitConverter.SingleToUInt32Bits(delta),
        };
    }

    private static Variant WorldSnapshotFacts(WorldSnapshot? snapshot, bool omitRelations,
        List<ExceptionDispatchInfo> failures)
    {
        if (snapshot is null) return default;
        using Variant feet = WorldFeetFacts(snapshot.WalkerFeet);
        using Variant actors = WorldActorIdentities(snapshot.Level100Actors?.Actors);
        using Array? omittedTargets = omitRelations ? new Array() : null;
        using Variant targets = omittedTargets is null ? WorldTargetFacts(snapshot, failures) : Variant.From(omittedTargets);
        using Array? projectileRows = omitRelations ? new Array() : snapshot.Projectiles is null
            ? null : EntityProjectileFacts(snapshot.Projectiles);
        using Variant projectiles = projectileRows is null ? default : Variant.From(projectileRows);
        using var position = new Dictionary { ["x"] = snapshot.PlayerPosition.X, ["z"] = snapshot.PlayerPosition.Z };
        using var result = new Dictionary
        {
            ["tick"] = snapshot.Tick, ["opening_ticks_remaining"] = snapshot.Level100OpeningTicksRemaining,
            ["zoom_permille"] = snapshot.ZoomPermille,
            ["facing_yaw_micro_rad"] = snapshot.FacingYawMicroRad,
            ["facing_pitch_micro_rad"] = snapshot.FacingPitchMicroRad,
            ["body_roll_micro_rad"] = snapshot.BodyRollMicroRad,
            ["player_position"] = position,
            ["player_elevation_millimeters"] = snapshot.PlayerElevationMillimeters,
            ["player_ground_elevation_millimeters"] = snapshot.PlayerGroundElevationMillimeters,
            ["mode"] = (int)snapshot.Mode, ["transition"] = (int)snapshot.Transition,
            ["feet"] = feet, ["actors"] = actors, ["targets"] = targets, ["projectiles"] = projectiles,
        };
        return Variant.From(result);
    }

    private static Variant WorldFeetFacts(IReadOnlyList<WalkerFootContactSnapshot>? feet)
    {
        if (feet is null) return default;
        using var values = new Array();
        foreach (WalkerFootContactSnapshot? foot in feet)
        {
            if (foot is null) { values.Add(default(Variant)); continue; }
            using var value = new Dictionary
            {
                ["id"] = foot.Id, ["x"] = foot.Position.X, ["z"] = foot.Position.Z,
                ["ground_elevation_millimeters"] = foot.GroundElevationMillimeters,
                ["lift_millimeters"] = foot.LiftMillimeters,
            };
            using Variant row = value;
            values.Add(row);
        }
        return Variant.From(values);
    }

    private static Variant WorldActorIdentities(IReadOnlyList<Level100ActorSnapshot>? actors)
    {
        if (actors is null) return default;
        using var values = new Array();
        foreach (Level100ActorSnapshot? actor in actors)
        {
            if (actor is null) { values.Add(default(Variant)); continue; }
            using Variant name = TextUnits(actor.Name);
            using var value = new Dictionary { ["name"] = name, ["actor_id"] = actor.ActorId.Value };
            using Variant row = value;
            values.Add(row);
        }
        return Variant.From(values);
    }

    private static Variant WorldTargetFacts(WorldSnapshot snapshot, List<ExceptionDispatchInfo> failures)
    {
        try
        {
            using Array values = EntityTargetFacts(snapshot.Targets);
            return Variant.From(values);
        }
        catch (Exception error)
        {
            // Targets is still Core's computed projection. Defer its refusal
            // to the native frame's original projection stage, after its clock,
            // player transform and pure foot conversion, before Aquila node
            // writes, then rethrow this exact error.
            // The token is local to one synchronous Render call, never retained
            // by another frame or turned into a successful empty actor list.
            int id = failures.Count;
            failures.Add(ExceptionDispatchInfo.Capture(error));
            using var failure = new Dictionary { ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["error"] = error.Message, ["host_exception_id"] = id };
            return Variant.From(failure);
        }
    }

    private Dictionary WorldPresentationResult(Variant returned, List<ExceptionDispatchInfo>? failures = null)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native world presentation aborted without a completion result.");
        Dictionary result = returned.AsGodotDictionary();
        try
        {
            // These are detached facts, not a second clock or simulation. A
            // later stage failure must not roll back preceding native writes.
            if (result.ContainsKey("particle_seconds_bits"))
            {
                _particlePresentationSeconds = BitConverter.UInt32BitsToSingle(checked((uint)result["particle_seconds_bits"].AsInt64()));
                ShowHud = result["show_hud"].AsBool();
                OpeningPanActive = result["opening_pan"].AsBool();
                StoreEntityCounts(result);
                _level100Terrain.SynchronizePresentationCounts(result["terrain_vertex_count"].AsInt32(),
                    result["terrain_triangle_count"].AsInt32());
            }
            if (result.TryGetValue("host_exception_id", out Variant failure))
            {
                using (failure)
                {
                    int id = checked((int)failure.AsInt64());
                    if (failures is null || id < 0 || id >= failures.Count)
                        throw new InvalidOperationException("Unknown world projection failure token.");
                    failures[id].Throw();
                }
            }
            using Variant ok = result["ok"];
            if (ok.VariantType != Variant.Type.Bool)
                throw new InvalidOperationException("Native world presentation returned no completion flag.");
            if (ok.AsBool()) return result;
            using Variant kind = result["error_type"];
            using Variant message = result["error"];
            string error = message.AsString();
            string? parameter = result.ContainsKey("parameter") ? result["parameter"].AsString() : null;
            throw kind.AsString() switch
            {
                "NullReferenceException" => new NullReferenceException(error),
                "InvalidDataException" => new InvalidDataException(error),
                "ArgumentNullException" => new ArgumentNullException(parameter, error),
                "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(parameter, error),
                "ArgumentException" => new ArgumentException(error, parameter),
                "IndexOutOfRangeException" => new IndexOutOfRangeException(error),
                "OverflowException" => new OverflowException(error),
                "ObjectDisposedException" => new ObjectDisposedException(nameof(MeshInstance3D), error),
                _ => new InvalidOperationException(error),
            };
        }
        catch
        {
            result.Dispose();
            throw;
        }
    }
}
