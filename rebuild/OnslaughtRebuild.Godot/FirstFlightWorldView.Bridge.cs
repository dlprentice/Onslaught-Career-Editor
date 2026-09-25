// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

// Entry points for the GDScript host while world assembly is still C#. Each
// returns {ok, show_hud, opening_pan_active} or the failure, never throwing
// across the language boundary.
public sealed partial class FirstFlightWorldView
{
    public D InitializeFromBridge(SimulationBridge bridge) => Guarded(() => Initialize(bridge.CurrentSnapshot));

    public D RenderFromBridge(SimulationBridge bridge, double interpolationAlpha, double frameDelta) =>
        Guarded(() => Render(bridge.PreviousSnapshot, bridge.CurrentSnapshot, (float)interpolationAlpha, (float)frameDelta));

    public D ConsumeWeaponFireFacts(A weapons) => Guarded(() =>
    {
        using Variant batch = weapons;
        using Variant returned = _worldPresentation.Call("queue_weapon_events", batch);
        using D result = WorldPresentationResult(returned);
    });

    public D ConsumeDestructionFacts(A events, int tick) => Guarded(() =>
    {
        foreach (Variant value in events)
        {
            D item = value.AsGodotDictionary();
            int x = item["x"].AsInt32(), y = item["y"].AsInt32(), z = item["z"].AsInt32(), actorId = item["actor_id"].AsInt32();
            Vector3 position = new(x * UnitsToMeters, -z * UnitsToMeters, -y * UnitsToMeters);
            var kind = (Level100DestructionEffectKind)item["effect_kind"].AsInt32();
            switch (kind)
            {
                case Level100DestructionEffectKind.None:
                    break;
                case Level100DestructionEffectKind.PulseImpact:
                    SpawnPulseImpact(position, actorId, tick);
                    break;
                case Level100DestructionEffectKind.VulcanImpact:
                    SpawnVulcanImpact(position, actorId, tick);
                    break;
                case Level100DestructionEffectKind.TargetDestroyed:
                    SpawnTargetTankDestruction(position, actorId);
                    break;
                case Level100DestructionEffectKind.DroneDestroyed:
                    SpawnTargetDroneDestruction(position, actorId);
                    break;
                case Level100DestructionEffectKind.FacilityDestroyed:
                    SpawnFacilityDestruction(position, actorId);
                    break;
                default:
                    throw new InvalidDataException($"Core exposed unknown Level 100 destruction effect {kind}.");
            }
        }
    });

    /// <summary>The world half of the smoke report.</summary>
    public D PresentationFacts() => new()
    {
        ["show_hud"] = ShowHud,
        ["opening_pan_active"] = OpeningPanActive,
        ["player_visual_present"] = PlayerVisualPresent,
        ["retail_aquila_meshes_present"] = RetailAquilaMeshesPresent,
        ["retail_aquila_surface_count"] = RetailAquilaSurfaceCount,
        ["retail_aquila_part_count"] = RetailAquilaPartCount,
        ["retail_aquila_animated_part_count"] = RetailAquilaAnimatedPartCount,
        ["retail_aquila_standing_clearance"] = RetailAquilaStandingClearance,
        ["retail_cockpit_surface_count"] = RetailCockpitSurfaceCount,
        ["level100_player_start_relative_height"] = Level100PlayerStartRelativeHeight,
        ["retail_level100_static_object_count"] = RetailLevel100StaticObjectCount,
        ["retail_level100_static_object_surface_count"] = RetailLevel100StaticObjectSurfaceCount,
        ["retail_level100_pine_count"] = RetailLevel100PineCount,
        ["retail_level100_water_present"] = RetailLevel100WaterPresent,
        ["retail_level100_water_grid_vertex_count"] = RetailLevel100WaterGridVertexCount,
        ["retail_level100_water_grid_triangle_count"] = RetailLevel100WaterGridTriangleCount,
        ["retail_level100_shoreline_triangle_count"] = RetailLevel100ShorelineTriangleCount,
        ["retail_level100_target_surface_count"] = RetailLevel100TargetSurfaceCount,
        ["retail_level100_terrain_vertex_count"] = RetailLevel100TerrainVertexCount,
        ["retail_level100_terrain_triangle_count"] = RetailLevel100TerrainTriangleCount,
        ["retail_level100_sky_surface_count"] = RetailLevel100SkySurfaceCount,
        ["target_visual_count"] = TargetVisualCount,
    };

    private D Guarded(Action action)
    {
        try
        {
            action();
            return new D { ["ok"] = true, ["show_hud"] = ShowHud, ["opening_pan_active"] = OpeningPanActive };
        }
        catch (Exception error)
        {
            return new D { ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message };
        }
    }
}
