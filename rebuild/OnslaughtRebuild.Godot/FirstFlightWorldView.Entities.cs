// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using Dictionary = Godot.Collections.Dictionary;
using Array = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

public sealed partial class FirstFlightWorldView
{
    internal const string EntityScenePath = "res://Scenes/World/EntityPresentation.tscn";
    private Node _entityPresentation = null!;
    private int _targetVisualCount;
    private int _projectileVisualCount;
    private int _targetSurfaceCount;

    private void CreateEntityPresentation()
    {
        using PackedScene scene = GD.Load<PackedScene>(EntityScenePath);
        _entityPresentation = scene.Instantiate();
        AddChild(_entityPresentation);
        SetEditableInstance(_entityPresentation, true);
    }

    private void ConfigureEntityPresentation(WorldSnapshot snapshot)
    {
        var assets = new Array();
        foreach ((Level100TargetVisualBinding binding, Mesh mesh) in _level100TargetAssets)
            assets.Add(new Dictionary
            {
                ["definition_name"] = TextUnits(binding.DefinitionName),
                ["mesh_binding"] = TextUnits(binding.MeshBinding), ["mesh"] = mesh,
            });
        using Dictionary result = EntityResult(_entityPresentation.Call("configure",
            this, _camera, assets, EntityTargetFacts(snapshot.Targets)));
        StoreEntityCounts(result);
    }

    private void RenderEntities(WorldSnapshot previous, WorldSnapshot current, float alpha,
        bool resetJump, Action<Vector3[]> aquilaStage)
    {
        using Dictionary facts = EntityFrameFacts(previous, current, alpha, resetJump,
            _pendingPulseCannonMuzzleFlashes);
        Exception? hostFailure = null;
        Callable callback = Callable.From<Array, Dictionary>(feet =>
        {
            try
            {
                if (feet.Count != 4) throw new InvalidDataException("Native Aquila contacts are incomplete.");
                aquilaStage(feet.Select(value => EntityVector(value.AsGodotDictionary())).ToArray());
                return new Dictionary { ["ok"] = true };
            }
            catch (Exception error)
            {
                hostFailure = error;
                return new Dictionary { ["ok"] = false, ["error_type"] = error.GetType().Name,
                    ["error"] = error.Message };
            }
        });
        using Variant nativeResult = _entityPresentation.Call("render_frame", facts, callback);
        // Preserve a partial muzzle decrement if a later actor/projectile stage
        // refuses the frame. An aborted GDScript function is never success.
        if (nativeResult.VariantType == Variant.Type.Dictionary)
        {
            using Dictionary partial = nativeResult.AsGodotDictionary();
            if (partial.TryGetValue("pending_muzzles", out Variant count))
                _pendingPulseCannonMuzzleFlashes = checked((int)count.AsInt64());
        }
        if (hostFailure is not null) System.Runtime.ExceptionServices.ExceptionDispatchInfo.Capture(hostFailure).Throw();
        using Dictionary result = EntityResult(nativeResult);
        StoreEntityCounts(result);
    }

    private void StoreEntityCounts(Dictionary result)
    {
        _targetVisualCount = checked((int)result["target_count"].AsInt64());
        _projectileVisualCount = checked((int)result["projectile_count"].AsInt64());
        _targetSurfaceCount = checked((int)result["target_surface_count"].AsInt64());
    }

    internal static Dictionary EntityFrameFacts(WorldSnapshot previous, WorldSnapshot current,
        float alpha, bool resetJump, int pendingMuzzles)
    {
        // Current feet are admitted first, then previous feet only through the
        // original reset/reference/count gates. Int32 offset arithmetic remains
        // explicit here; the native owner performs their float32 interpolation.
        Array currentFeet = EntityVectors(ToFootOffsets(current));
        Variant previousFeet = default;
        bool same = ReferenceEquals(previous, current);
        if (!resetJump && !same && previous.WalkerFeet.Count == current.WalkerFeet.Count)
            previousFeet = EntityVectors(ToFootOffsets(previous));
        return new Dictionary
        {
            ["alpha_bits"] = (long)BitConverter.SingleToUInt32Bits(alpha),
            ["same_snapshot"] = same, ["current_feet"] = currentFeet,
            ["previous_feet"] = previousFeet,
            ["previous_targets"] = same ? new Array() : EntityTargetFacts(previous.Targets),
            ["current_targets"] = EntityTargetFacts(current.Targets),
            ["previous_projectiles"] = same ? new Array() : EntityProjectileFacts(previous.Projectiles),
            ["current_projectiles"] = EntityProjectileFacts(current.Projectiles),
            ["pending_muzzles"] = pendingMuzzles,
        };
    }

    internal static Array EntityTargetFacts(IReadOnlyList<TargetSnapshot> targets)
    {
        var result = new Array();
        foreach (TargetSnapshot? item in targets)
        {
            if (item is null) { result.Add(default(Variant)); continue; }
            Variant pose = default;
            if (item.Pose is { } value)
            {
                Level100FloatBasis3Bits basis = value.BasisFloatBits;
                pose = new Dictionary
                {
                    ["position_millimeters"] = new Dictionary { ["x"] = value.PositionMillimeters.X,
                        ["y"] = value.PositionMillimeters.Y, ["z"] = value.PositionMillimeters.Z },
                    ["basis_float_bits"] = new Dictionary { ["row0_x"] = basis.Row0X, ["row0_y"] = basis.Row0Y,
                        ["row0_z"] = basis.Row0Z, ["row1_x"] = basis.Row1X, ["row1_y"] = basis.Row1Y,
                        ["row1_z"] = basis.Row1Z, ["row2_x"] = basis.Row2X, ["row2_y"] = basis.Row2Y, ["row2_z"] = basis.Row2Z },
                };
            }
            result.Add(new Dictionary { ["actor_id"] = item.ActorId.Value,
                ["definition_name"] = TextUnits(item.DefinitionName), ["mesh_binding"] = TextUnits(item.MeshBinding),
                ["is_active"] = item.IsActive, ["pose"] = pose });
        }
        return result;
    }

    private static Array EntityProjectileFacts(IReadOnlyList<ProjectileSnapshot> projectiles)
    {
        var result = new Array();
        foreach (ProjectileSnapshot item in projectiles)
            result.Add(new Dictionary { ["id"] = item.Id, ["kind"] = (int)item.Kind,
                ["x"] = item.Position.X, ["z"] = item.Position.Z, ["elevation"] = item.ElevationMillimeters,
                ["velocity_x"] = item.Velocity.X, ["velocity_z"] = item.Velocity.Z,
                ["vertical_velocity"] = item.VerticalVelocityMillimetersPerTick, ["remaining_ticks"] = item.RemainingTicks });
        return result;
    }

    private static Variant TextUnits(string? value) => value is null
        ? default : Variant.From(value.Select(character => (int)character).ToArray());

    private static Array EntityVectors(IEnumerable<Vector3> values)
    {
        var result = new Array();
        foreach (Vector3 value in values)
            result.Add(new Dictionary { ["x_bits"] = (long)BitConverter.SingleToUInt32Bits(value.X),
                ["y_bits"] = (long)BitConverter.SingleToUInt32Bits(value.Y), ["z_bits"] = (long)BitConverter.SingleToUInt32Bits(value.Z) });
        return result;
    }

    private static Vector3 EntityVector(Dictionary value) => new(
        BitConverter.UInt32BitsToSingle(checked((uint)value["x_bits"].AsInt64())),
        BitConverter.UInt32BitsToSingle(checked((uint)value["y_bits"].AsInt64())),
        BitConverter.UInt32BitsToSingle(checked((uint)value["z_bits"].AsInt64())));

    private static Dictionary EntityResult(Variant result)
    {
        if (result.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native entity presentation aborted without a completion result.");
        Dictionary record = result.AsGodotDictionary();
        if (!record.TryGetValue("ok", out Variant ok) || ok.VariantType != Variant.Type.Bool)
            throw new InvalidOperationException("Native entity presentation returned no completion flag.");
        if (ok.AsBool()) return record;
        string kind = record.TryGetValue("error_type", out Variant name) ? name.AsString() : "InvalidOperationException";
        string error = record.TryGetValue("error", out Variant message) ? message.AsString() : "Native entity presentation failed.";
        throw kind switch
        {
            "InvalidDataException" => new InvalidDataException(error),
            "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(null, error),
            "ArgumentNullException" => new ArgumentNullException(null, error),
            "ArgumentException" => new ArgumentException(error),
            _ => new InvalidOperationException(error),
        };
    }
}
