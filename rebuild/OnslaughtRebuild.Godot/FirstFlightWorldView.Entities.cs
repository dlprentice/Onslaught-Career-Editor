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
        using var assets = new Array();
        foreach ((Level100TargetVisualBinding binding, Mesh mesh) in _level100TargetAssets)
        {
            using Variant definitionName = TextUnits(binding.DefinitionName);
            using Variant meshBinding = TextUnits(binding.MeshBinding);
            using Variant meshValue = mesh;
            using var entry = new Dictionary
            {
                ["definition_name"] = definitionName,
                ["mesh_binding"] = meshBinding, ["mesh"] = meshValue,
            };
            using Variant entryValue = entry;
            assets.Add(entryValue);
        }
        // The native owner retains its own mesh references. Release both the
        // collection wrappers and independent Variant carriers for this batch.
        using Array targets = EntityTargetFacts(snapshot.Targets);
        using Variant assetValues = assets;
        using Variant targetValues = targets;
        using Variant configured = _entityPresentation.Call("configure",
            this, _camera, assetValues, targetValues);
        using Dictionary result = EntityResult(configured);
        StoreEntityCounts(result);
    }

    private void StoreEntityCounts(Dictionary result)
    {
        using Variant targets = result["target_count"];
        using Variant projectiles = result["projectile_count"];
        using Variant surfaces = result["target_surface_count"];
        _targetVisualCount = checked((int)targets.AsInt64());
        _projectileVisualCount = checked((int)projectiles.AsInt64());
        _targetSurfaceCount = checked((int)surfaces.AsInt64());
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

    internal static Array EntityProjectileFacts(IReadOnlyList<ProjectileSnapshot> projectiles)
    {
        var result = new Array();
        foreach (ProjectileSnapshot? item in projectiles)
        {
            if (item is null) { result.Add(default(Variant)); continue; }
            result.Add(new Dictionary { ["id"] = item.Id, ["kind"] = (int)item.Kind,
                ["x"] = item.Position.X, ["z"] = item.Position.Z, ["elevation"] = item.ElevationMillimeters,
                ["velocity_x"] = item.Velocity.X, ["velocity_z"] = item.Velocity.Z,
                ["vertical_velocity"] = item.VerticalVelocityMillimetersPerTick, ["remaining_ticks"] = item.RemainingTicks });
        }
        return result;
    }

    private static Variant TextUnits(string? value) => value is null
        ? default : Variant.From(value.Select(character => (int)character).ToArray());

    private static Dictionary EntityResult(Variant result)
    {
        if (result.VariantType != Variant.Type.Dictionary)
            throw new InvalidOperationException("Native entity presentation aborted without a completion result.");
        Dictionary record = result.AsGodotDictionary();
        try
        {
            bool hasFlag = record.TryGetValue("ok", out Variant ok);
            using (ok)
            {
                if (!hasFlag || ok.VariantType != Variant.Type.Bool)
                    throw new InvalidOperationException("Native entity presentation returned no completion flag.");
                if (ok.AsBool()) return record;
            }
            string kind = "InvalidOperationException";
            string error = "Native entity presentation failed.";
            if (record.TryGetValue("error_type", out Variant name))
                using (name) kind = name.AsString();
            if (record.TryGetValue("error", out Variant message))
                using (message) error = message.AsString();
            throw kind switch
            {
                "InvalidDataException" => new InvalidDataException(error),
                "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(null, error),
                "ArgumentNullException" => new ArgumentNullException(null, error),
                "ArgumentException" => new ArgumentException(error),
                _ => new InvalidOperationException(error),
            };
        }
        catch
        {
            record.Dispose();
            throw;
        }
    }
}
