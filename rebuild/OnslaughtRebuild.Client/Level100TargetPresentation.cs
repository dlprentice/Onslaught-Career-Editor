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
