// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public readonly record struct Level100RenderVector3(
    float X,
    float Y,
    float Z);

public readonly record struct Level100RenderBasis3(
    Level100RenderVector3 XAxis,
    Level100RenderVector3 YAxis,
    Level100RenderVector3 ZAxis);

public readonly record struct Level100TargetVisualBinding(
    string DefinitionName,
    string MeshBinding);

public readonly record struct Level100TargetVisualDescriptor(
    Level100ActorId ActorId,
    string DefinitionName,
    string MeshBinding,
    bool Visible,
    Level100RenderVector3 Position,
    Level100RenderBasis3 Basis)
{
    public Level100TargetVisualBinding Binding =>
        new(DefinitionName, MeshBinding);
}

/// <summary>
/// Presentation-only conversion from the canonical Core actor pose into the
/// right-handed world transform consumed by the Godot client.
/// </summary>
public static class Level100TargetPresentation
{
    private const float MillimetersToMeters = 0.001f;

    public static Level100TargetVisualBinding TargetTankBinding { get; } =
        new("Target Tank", "m_f_pulsetank_training.msh.aya");

    public static Level100TargetVisualBinding TargetTruckBinding { get; } =
        new("Target Truck", "m_f_truck_training.msh.aya");

    public static Level100TargetVisualBinding WarehouseBinding { get; } =
        new("Warehouse", "m_m_warehouse.msh.aya");

    /// <summary>
    /// The ambient U-17 Highside Transporter, authored into the level world at
    /// RLWD ordinal 21 with script <c>Transporter</c>. Retail constructs it at
    /// level load as <c>CDropship</c> and attaches that script before the player
    /// has control: MEASURED in the 2026-07-28 TTD trace of the pristine
    /// specimen, <c>CWorldPhysicsManager__CreateThingByType</c> creation 28
    /// returning <c>0x0809b550</c>, then <c>CComplexThing__SetScript</c> row T3f
    /// reading <c>this=0809b550 vptr=005e1dd8 script=Transporter</c>
    /// (<c>local-lab/TTD-LEVEL100-FINDINGS-2026-07-28.md</c> §3, §5a).
    /// </summary>
    public static Level100TargetVisualBinding TransporterBinding { get; } =
        new("U-17 Highside Transporter", "m_f_lifter.msh.aya");

    /// <summary>
    /// The Air Trainer. One definition serves two instances: the ambient
    /// <c>Flyby</c> aircraft authored at RLWD ordinal 40, and the dodge-exercise
    /// attacker the Airfield spawns at <c>LevelScript.msl:185</c>. Retail builds
    /// the ambient one as <c>CPlane</c> at level load — creation 29 returning
    /// <c>0x08118f70</c>, script row T41 <c>vptr=005e1930 script=Flyby</c>.
    /// </summary>
    public static Level100TargetVisualBinding AirTrainerBinding { get; } =
        new("Air Trainer", "m_FA_F24_training.msh.aya");

    /// <summary>
    /// The nine airborne Target Drones. MEASURED: this definition carries the
    /// SAME <c>CUnitMesh</c> as <see cref="AirTrainerBinding"/> —
    /// <c>fa_f24_training.msh</c>, <c>default physics.dat</c> records #660 and
    /// #601 — so one conversion serves both and task #101's premise that the
    /// drone "needs a new mesh retention" does not hold. The binding stays
    /// distinct because the canonical binding is a (definition, mesh) pair and
    /// the two definitions diverge everywhere else: allegiance, life, weapons,
    /// and the drone's absent engine loop.
    /// </summary>
    public static Level100TargetVisualBinding TargetDroneBinding { get; } =
        new("Target Drone", "m_FA_F24_training.msh.aya");

    /// <summary>
    /// Every canonical binding a Level 100 world actor can reach the renderer
    /// with. This is the complete set that the Godot world view must hold a mesh
    /// for: an actor whose binding is absent here reaches
    /// <c>FirstFlightWorldView.AddLevel100Target</c> and throws.
    ///
    /// <para>The player is deliberately NOT here. It carries mesh binding
    /// <c>m_f_be1.msh.aya</c> and is non-static, but its presentation owner is
    /// the Aquila walker/jet asset, not the target list.</para>
    /// </summary>
    public static IReadOnlyList<Level100TargetVisualBinding> RenderedBindings { get; } =
        Array.AsReadOnly(new[]
        {
            TargetTankBinding,
            TargetTruckBinding,
            WarehouseBinding,
            TransporterBinding,
            AirTrainerBinding,
            TargetDroneBinding,
        });

    public static Level100TargetVisualDescriptor Project(
        TargetSnapshot target)
    {
        ArgumentNullException.ThrowIfNull(target);
        Level100ActorPoseSnapshot pose = target.Pose;
        Level100FloatBasis3Bits core = pose.BasisFloatBits;

        float c00 = Decode(core.Row0X);
        float c01 = Decode(core.Row0Y);
        float c02 = Decode(core.Row0Z);
        float c10 = Decode(core.Row1X);
        float c11 = Decode(core.Row1Y);
        float c12 = Decode(core.Row1Z);
        float c20 = Decode(core.Row2X);
        float c21 = Decode(core.Row2Y);
        float c22 = Decode(core.Row2Z);

        return new Level100TargetVisualDescriptor(
            target.ActorId,
            target.DefinitionName,
            target.MeshBinding,
            target.IsActive,
            new Level100RenderVector3(
                pose.PositionMillimeters.X * MillimetersToMeters,
                pose.PositionMillimeters.Y * MillimetersToMeters,
                -pose.PositionMillimeters.Z * MillimetersToMeters),
            new Level100RenderBasis3(
                new Level100RenderVector3(c00, c10, -c20),
                new Level100RenderVector3(c01, c11, -c21),
                new Level100RenderVector3(-c02, -c12, c22)));
    }

    private static float Decode(int bits) =>
        BitConverter.Int32BitsToSingle(bits);
}
