// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

// The world presentation's Core inputs. Only immutable facts cross: no
// transform, clock, camera state, foot arithmetic or actor/projectile lifecycle
// is owned here.
public sealed partial class SimulationBridge
{
    private const string HeightFieldResource = "OnslaughtRebuild.Core.Assets.Level100.level100-heightfield.hfld.bin";

    /// <summary>
    /// The retained Level 100 HFLD bytes Core's terrain samples, for the
    /// presentation's terrain, sun and water owners. Transferred once per owner.
    /// </summary>
    public D GetHeightFieldBytes() => Guard(() =>
    {
        using Stream source = typeof(Level100Terrain).Assembly.GetManifestResourceStream(HeightFieldResource)
            ?? throw new InvalidDataException("The retained Level 100 heightfield is missing.");
        byte[] bytes = new byte[source.Length];
        source.ReadExactly(bytes);
        return bytes;
    });

    /// <summary>
    /// Constants the world presentation is configured with, the actor manifest
    /// pin and the managed build identity the private Level 100 import is keyed to.
    /// </summary>
    public D WorldConfigFacts() => Guard(() => new D
    {
        ["pan_duration_ticks"] = SimulationConstants.Level100OpeningPanTicks,
        ["control_view_handoff_lead_ticks"] = Level100MissionTiming.ReleasedEventFrameTicks,
        ["walker_height_mm"] = Level100Terrain.WalkerCenterOfGravityMillimeters,
        ["actor_manifest_sha256"] = Level100ActorDefinitionManifest.ExpectedManifestSha256,
        ["assembly_identity"] = AssemblyIdentity(),
    });

    // Deterministic builds derive each module ID from its content, and Godot
    // may load assemblies from memory, so the ID stands in for the file hash.
    private static string AssemblyIdentity()
    {
        using var hash = System.Security.Cryptography.IncrementalHash.CreateHash(
            System.Security.Cryptography.HashAlgorithmName.SHA256);
        foreach (Type type in new[] { typeof(Simulation), typeof(Level100ActorDefinitionManifest), typeof(SimulationBridge) })
            hash.AppendData(type.Assembly.ManifestModule.ModuleVersionId.ToByteArray());
        return Convert.ToHexString(hash.GetHashAndReset());
    }

    /// <summary>The current snapshot's target projection for the entity presentation.</summary>
    public D TargetFacts() => Guard(() => EntityTargetFacts(CurrentSnapshot.Targets));

    /// <summary>
    /// The previous and current snapshots' world facts with the float32 alpha
    /// and delta words. A failed target projection is carried in place of the
    /// targets as {ok:false, error_type, error, host_exception_id}, so the
    /// native frame refuses it at its original projection stage.
    /// </summary>
    public D WorldFrameFacts(double interpolationAlpha, double frameDelta) => Guard(() =>
    {
        WorldSnapshot previous = PreviousSnapshot;
        WorldSnapshot current = CurrentSnapshot;
        bool same = ReferenceEquals(previous, current);
        int failures = 0;
        Variant before = WorldSnapshotFacts(previous, same, ref failures);
        Variant after = WorldSnapshotFacts(current, false, ref failures);
        return new D
        {
            ["previous"] = before, ["current"] = after, ["same_snapshot"] = same,
            ["alpha_bits"] = (long)BitConverter.SingleToUInt32Bits((float)interpolationAlpha),
            ["delta_bits"] = (long)BitConverter.SingleToUInt32Bits((float)frameDelta),
        };
    });

    private static Variant WorldSnapshotFacts(WorldSnapshot snapshot, bool omitRelations, ref int failures)
    {
        Variant feet = WorldFeetFacts(snapshot.WalkerFeet);
        Variant actors = WorldActorIdentities(snapshot.Level100Actors?.Actors);
        Variant targets = omitRelations ? Variant.From(new A()) : WorldTargetFacts(snapshot, ref failures);
        Variant projectiles = omitRelations ? Variant.From(new A())
            : snapshot.Projectiles is null ? default : Variant.From(EntityProjectileFacts(snapshot.Projectiles));
        return Variant.From(new D
        {
            ["tick"] = snapshot.Tick, ["opening_ticks_remaining"] = snapshot.Level100OpeningTicksRemaining,
            ["zoom_permille"] = snapshot.ZoomPermille,
            ["facing_yaw_micro_rad"] = snapshot.FacingYawMicroRad,
            ["facing_pitch_micro_rad"] = snapshot.FacingPitchMicroRad,
            ["body_roll_micro_rad"] = snapshot.BodyRollMicroRad,
            ["player_position"] = new D { ["x"] = snapshot.PlayerPosition.X, ["z"] = snapshot.PlayerPosition.Z },
            ["player_elevation_millimeters"] = snapshot.PlayerElevationMillimeters,
            ["player_ground_elevation_millimeters"] = snapshot.PlayerGroundElevationMillimeters,
            ["mode"] = (int)snapshot.Mode, ["transition"] = (int)snapshot.Transition,
            ["feet"] = feet, ["actors"] = actors, ["targets"] = targets, ["projectiles"] = projectiles,
        });
    }

    private static Variant WorldFeetFacts(IReadOnlyList<WalkerFootContactSnapshot>? feet)
    {
        if (feet is null) return default;
        var values = new A();
        foreach (WalkerFootContactSnapshot? foot in feet)
        {
            if (foot is null) { values.Add(default(Variant)); continue; }
            values.Add(new D
            {
                ["id"] = foot.Id, ["x"] = foot.Position.X, ["z"] = foot.Position.Z,
                ["ground_elevation_millimeters"] = foot.GroundElevationMillimeters,
                ["lift_millimeters"] = foot.LiftMillimeters,
            });
        }
        return Variant.From(values);
    }

    private static Variant WorldActorIdentities(IReadOnlyList<Level100ActorSnapshot>? actors)
    {
        if (actors is null) return default;
        var values = new A();
        foreach (Level100ActorSnapshot? actor in actors)
        {
            if (actor is null) { values.Add(default(Variant)); continue; }
            values.Add(new D { ["name"] = TextUnits(actor.Name), ["actor_id"] = actor.ActorId.Value });
        }
        return Variant.From(values);
    }

    private static Variant WorldTargetFacts(WorldSnapshot snapshot, ref int failures)
    {
        try
        {
            return Variant.From(EntityTargetFacts(snapshot.Targets));
        }
        catch (Exception error)
        {
            // Targets is Core's computed projection; its refusal is deferred to
            // the native frame's projection stage, after the clock, player
            // transform and pure foot conversion, before any Aquila node write.
            return Variant.From(new D { ["ok"] = false, ["error_type"] = error.GetType().Name,
                ["error"] = error.Message, ["host_exception_id"] = failures++ });
        }
    }

    private static A EntityTargetFacts(IReadOnlyList<TargetSnapshot> targets)
    {
        var result = new A();
        foreach (TargetSnapshot? item in targets)
        {
            if (item is null) { result.Add(default(Variant)); continue; }
            Variant pose = default;
            if (item.Pose is { } value)
            {
                Level100FloatBasis3Bits basis = value.BasisFloatBits;
                pose = new D
                {
                    ["position_millimeters"] = new D { ["x"] = value.PositionMillimeters.X,
                        ["y"] = value.PositionMillimeters.Y, ["z"] = value.PositionMillimeters.Z },
                    ["basis_float_bits"] = new D { ["row0_x"] = basis.Row0X, ["row0_y"] = basis.Row0Y,
                        ["row0_z"] = basis.Row0Z, ["row1_x"] = basis.Row1X, ["row1_y"] = basis.Row1Y,
                        ["row1_z"] = basis.Row1Z, ["row2_x"] = basis.Row2X, ["row2_y"] = basis.Row2Y, ["row2_z"] = basis.Row2Z },
                };
            }
            result.Add(new D { ["actor_id"] = item.ActorId.Value,
                ["definition_name"] = TextUnits(item.DefinitionName), ["mesh_binding"] = TextUnits(item.MeshBinding),
                ["is_active"] = item.IsActive, ["pose"] = pose });
        }
        return result;
    }

    private static A EntityProjectileFacts(IReadOnlyList<ProjectileSnapshot> projectiles)
    {
        var result = new A();
        foreach (ProjectileSnapshot? item in projectiles)
        {
            if (item is null) { result.Add(default(Variant)); continue; }
            result.Add(new D { ["id"] = item.Id, ["kind"] = (int)item.Kind,
                ["x"] = item.Position.X, ["z"] = item.Position.Z, ["elevation"] = item.ElevationMillimeters,
                ["velocity_x"] = item.Velocity.X, ["velocity_z"] = item.Velocity.Z,
                ["vertical_velocity"] = item.VerticalVelocityMillimetersPerTick, ["remaining_ticks"] = item.RemainingTicks });
        }
        return result;
    }

    private static Variant TextUnits(string? value) => value is null
        ? default : Variant.From(value.Select(character => (int)character).ToArray());
}
