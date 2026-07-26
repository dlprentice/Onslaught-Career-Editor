// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client;

/// <summary>
/// The render-space state of a single pulse bolt: its world position and the
/// unnormalised direction its trail points along.
/// </summary>
public readonly record struct Level100ProjectileVisualState(
    Level100RenderVector3 Position,
    Level100RenderVector3 Direction);

/// <summary>
/// Presentation-only interpolation of rendered entities between two fixed-rate
/// simulation snapshots.
/// </summary>
/// <remarks>
/// Core owns simulation truth and is untouched by this type; nothing here feeds
/// back into a snapshot. Entities are matched across snapshots by their stable
/// Core identity (Level100ActorId for actors, the projectile id
/// for bolts) and never by list ordinal, so removing an entity mid-list cannot
/// make its neighbour slide into the gap.
/// </remarks>
public static class Level100RenderInterpolation
{
    /// <summary>
    /// Render-space displacement across one snapshot pair above which an entity
    /// is treated as having teleported and is drawn at its current state. This
    /// is the same 100 m^2 gate the player path already applies.
    /// </summary>
    public const float TeleportMeters = 10f;

    private const float OrthonormalTolerance = 1e-3f;

    public static Level100RenderVector3 Lerp(
        Level100RenderVector3 previous,
        Level100RenderVector3 current,
        float alpha) =>
        new(
            previous.X + ((current.X - previous.X) * alpha),
            previous.Y + ((current.Y - previous.Y) * alpha),
            previous.Z + ((current.Z - previous.Z) * alpha));

    public static float DistanceSquared(
        Level100RenderVector3 previous,
        Level100RenderVector3 current)
    {
        float dx = current.X - previous.X;
        float dy = current.Y - previous.Y;
        float dz = current.Z - previous.Z;
        return (dx * dx) + (dy * dy) + (dz * dz);
    }

    /// <summary>
    /// Interpolates a position, snapping to <paramref name="current"/> when the
    /// pair is further apart than one plausible tick of travel.
    /// </summary>
    public static Level100RenderVector3 InterpolatePosition(
        Level100RenderVector3 previous,
        Level100RenderVector3 current,
        float alpha,
        float teleportMeters = TeleportMeters) =>
        DistanceSquared(previous, current) > teleportMeters * teleportMeters
            ? current
            : Lerp(previous, current, alpha);

    /// <summary>
    /// Interpolates a rendered target actor. Returns <paramref name="current"/>
    /// unchanged - i.e. suppresses interpolation - when the actor has no prior
    /// state (spawn), changed identity or mesh binding, was hidden on either
    /// side of the pair (activation or destruction), or teleported.
    /// </summary>
    public static Level100TargetVisualDescriptor Interpolate(
        Level100TargetVisualDescriptor? previous,
        Level100TargetVisualDescriptor current,
        float alpha)
    {
        if (previous is not Level100TargetVisualDescriptor prior ||
            prior.ActorId != current.ActorId ||
            prior.Binding != current.Binding ||
            !prior.Visible ||
            !current.Visible ||
            DistanceSquared(prior.Position, current.Position) >
                TeleportMeters * TeleportMeters)
        {
            return current;
        }

        return current with
        {
            Position = Lerp(prior.Position, current.Position, alpha),
            Basis = InterpolateBasis(prior.Basis, current.Basis, alpha),
        };
    }

    /// <summary>
    /// Interpolates a pulse bolt. A bolt that did not exist in the previous
    /// snapshot was created during the tick that produced
    /// <paramref name="current"/>, so its first rendered frames run from
    /// <paramref name="spawn"/> - the muzzle state derived by subtracting one
    /// tick of velocity - rather than from a stale or teleported prior state.
    /// </summary>
    public static Level100ProjectileVisualState Interpolate(
        Level100ProjectileVisualState? previous,
        Level100ProjectileVisualState spawn,
        Level100ProjectileVisualState current,
        float alpha)
    {
        Level100ProjectileVisualState prior = previous ?? spawn;
        Level100RenderVector3 direction = Lerp(
            prior.Direction,
            current.Direction,
            alpha);
        return new Level100ProjectileVisualState(
            Lerp(prior.Position, current.Position, alpha),
            DistanceSquared(default, direction) > 0f
                ? direction
                : current.Direction);
    }

    /// <summary>
    /// Interpolates an orientation. Proper rotations take the shortest-arc
    /// quaternion path, matching the shortest-arc convention the player yaw and
    /// roll already use; anything that is not orthonormal falls back to a
    /// component-wise lerp so a scaled or degenerate basis cannot blow up.
    /// </summary>
    public static Level100RenderBasis3 InterpolateBasis(
        Level100RenderBasis3 previous,
        Level100RenderBasis3 current,
        float alpha)
    {
        if (!IsProperRotation(previous) || !IsProperRotation(current))
        {
            return new Level100RenderBasis3(
                Lerp(previous.XAxis, current.XAxis, alpha),
                Lerp(previous.YAxis, current.YAxis, alpha),
                Lerp(previous.ZAxis, current.ZAxis, alpha));
        }

        (float px, float py, float pz, float pw) = ToQuaternion(previous);
        (float cx, float cy, float cz, float cw) = ToQuaternion(current);
        if ((px * cx) + (py * cy) + (pz * cz) + (pw * cw) < 0f)
        {
            cx = -cx;
            cy = -cy;
            cz = -cz;
            cw = -cw;
        }

        float x = px + ((cx - px) * alpha);
        float y = py + ((cy - py) * alpha);
        float z = pz + ((cz - pz) * alpha);
        float w = pw + ((cw - pw) * alpha);
        float length = MathF.Sqrt((x * x) + (y * y) + (z * z) + (w * w));
        if (length <= 0f || !float.IsFinite(length))
        {
            return current;
        }

        return FromQuaternion(x / length, y / length, z / length, w / length);
    }

    private static bool IsProperRotation(Level100RenderBasis3 basis)
    {
        if (!IsUnit(basis.XAxis) || !IsUnit(basis.YAxis) || !IsUnit(basis.ZAxis))
        {
            return false;
        }

        if (MathF.Abs(Dot(basis.XAxis, basis.YAxis)) > OrthonormalTolerance ||
            MathF.Abs(Dot(basis.XAxis, basis.ZAxis)) > OrthonormalTolerance ||
            MathF.Abs(Dot(basis.YAxis, basis.ZAxis)) > OrthonormalTolerance)
        {
            return false;
        }

        return Determinant(basis) > 0f;
    }

    private static bool IsUnit(Level100RenderVector3 axis) =>
        MathF.Abs(Dot(axis, axis) - 1f) <= 2f * OrthonormalTolerance;

    private static float Dot(
        Level100RenderVector3 left,
        Level100RenderVector3 right) =>
        (left.X * right.X) + (left.Y * right.Y) + (left.Z * right.Z);

    private static float Determinant(Level100RenderBasis3 basis) =>
        (basis.XAxis.X *
            ((basis.YAxis.Y * basis.ZAxis.Z) - (basis.ZAxis.Y * basis.YAxis.Z))) -
        (basis.YAxis.X *
            ((basis.XAxis.Y * basis.ZAxis.Z) - (basis.ZAxis.Y * basis.XAxis.Z))) +
        (basis.ZAxis.X *
            ((basis.XAxis.Y * basis.YAxis.Z) - (basis.YAxis.Y * basis.XAxis.Z)));

    // The three axes are the matrix columns, so m[row][column] reads
    // m00 = XAxis.X, m10 = XAxis.Y, m20 = XAxis.Z, m01 = YAxis.X, and so on.
    private static (float X, float Y, float Z, float W) ToQuaternion(
        Level100RenderBasis3 basis)
    {
        float m00 = basis.XAxis.X;
        float m10 = basis.XAxis.Y;
        float m20 = basis.XAxis.Z;
        float m01 = basis.YAxis.X;
        float m11 = basis.YAxis.Y;
        float m21 = basis.YAxis.Z;
        float m02 = basis.ZAxis.X;
        float m12 = basis.ZAxis.Y;
        float m22 = basis.ZAxis.Z;

        float trace = m00 + m11 + m22;
        if (trace > 0f)
        {
            float s = MathF.Sqrt(trace + 1f) * 2f;
            return ((m21 - m12) / s, (m02 - m20) / s, (m10 - m01) / s, 0.25f * s);
        }

        if (m00 > m11 && m00 > m22)
        {
            float s = MathF.Sqrt(1f + m00 - m11 - m22) * 2f;
            return (0.25f * s, (m01 + m10) / s, (m02 + m20) / s, (m21 - m12) / s);
        }

        if (m11 > m22)
        {
            float s = MathF.Sqrt(1f + m11 - m00 - m22) * 2f;
            return ((m01 + m10) / s, 0.25f * s, (m12 + m21) / s, (m02 - m20) / s);
        }

        float t = MathF.Sqrt(1f + m22 - m00 - m11) * 2f;
        return ((m02 + m20) / t, (m12 + m21) / t, 0.25f * t, (m10 - m01) / t);
    }

    private static Level100RenderBasis3 FromQuaternion(
        float x,
        float y,
        float z,
        float w) =>
        new(
            new Level100RenderVector3(
                1f - (2f * ((y * y) + (z * z))),
                2f * ((x * y) + (w * z)),
                2f * ((x * z) - (w * y))),
            new Level100RenderVector3(
                2f * ((x * y) - (w * z)),
                1f - (2f * ((x * x) + (z * z))),
                2f * ((y * z) + (w * x))),
            new Level100RenderVector3(
                2f * ((x * z) + (w * y)),
                2f * ((y * z) - (w * x)),
                1f - (2f * ((x * x) + (y * y)))));
}
