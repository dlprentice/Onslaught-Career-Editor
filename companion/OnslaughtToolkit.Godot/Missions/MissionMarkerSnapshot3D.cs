using System;
using System.Collections.Generic;
using System.Numerics;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Immutable, snapshot-local level markers for a 3D editor viewport. Positions
/// and picking rays must use the same coordinate space. A caller must recapture
/// Discard the prior snapshot and pending hits after every model change,
/// including undo, redo, reload, and switching documents.
/// after changing the editor and resolve a hit against its current snapshot.
/// Indices are editor-row indices, not persistent game or catalogue identities.
/// </summary>
public sealed class MissionMarkerSnapshot3D
{
    public readonly struct Marker
    {
        public Marker(int index, Vector3 position) { Index = index; Position = position; }
        public int Index { get; }
        public Vector3 Position { get; }
    }

    public readonly struct Hit
    {
        internal Hit(MissionMarkerSnapshot3D owner, int slot, double distance)
        { Owner = owner; Slot = slot; Distance = distance; }
        internal MissionMarkerSnapshot3D Owner { get; }
        internal int Slot { get; }
        public double Distance { get; }
    }

    private readonly Marker[] markers;
    private MissionMarkerSnapshot3D(Marker[] markers) { this.markers = markers; }
    public int Count => markers.Length;
    public Marker MarkerAt(int slot) => markers[slot];

    public static MissionMarkerSnapshot3D Capture(LevelEditorModel editor, int limit)
    {
        if (editor == null) throw new ArgumentNullException(nameof(editor));
        var rows = editor.Rows();
        CheckLimit(rows.Count, limit);
        var result = new Marker[rows.Count];
        for (int i = 0; i < result.Length; i++)
            result[i] = new Marker(rows[i].Index, rows[i].Position);
        return new MissionMarkerSnapshot3D(result);
    }

    public static MissionMarkerSnapshot3D Capture(IReadOnlyList<Marker> source, int limit)
    {
        if (source == null) throw new ArgumentNullException(nameof(source));
        CheckLimit(source.Count, limit);
        var result = new Marker[source.Count];
        for (int i = 0; i < result.Length; i++) result[i] = source[i];
        return new MissionMarkerSnapshot3D(result);
    }

    private static void CheckLimit(int count, int limit)
    {
        if (limit < 0) throw new ArgumentOutOfRangeException(nameof(limit));
        if (count > limit) throw new InvalidOperationException("The marker snapshot exceeds its caller's limit.");
    }

    /// <summary>
    /// Select the first sphere intersected by a ray; equal distances retain the
    /// earlier row. Radius and maximum distance are supplied by the viewport.
    /// Non-finite marker positions are ignored. Malformed rays return false.
    /// </summary>
    public bool TryPick(Vector3 origin, Vector3 direction, float radius, float maxDistance, out Hit hit)
    {
        hit = default;
        if (!Finite(origin) || !Finite(direction) || !Finite(radius) || !Finite(maxDistance)
            || radius <= 0 || maxDistance < 0) return false;
        double dx = direction.X, dy = direction.Y, dz = direction.Z;
        double length = Math.Sqrt(dx * dx + dy * dy + dz * dz);
        if (length == 0) return false;
        dx /= length; dy /= length; dz /= length;
        double radius2 = (double)radius * radius;
        double best = double.PositiveInfinity;
        int bestSlot = -1;
        for (int i = 0; i < markers.Length; i++)
        {
            var p = markers[i].Position;
            if (!Finite(p)) continue;
            double x = (double)p.X - origin.X, y = (double)p.Y - origin.Y, z = (double)p.Z - origin.Z;
            double along = x * dx + y * dy + z * dz;
            double cx = y * dz - z * dy, cy = z * dx - x * dz, cz = x * dy - y * dx;
            double perpendicular2 = cx * cx + cy * cy + cz * cz;
            if (perpendicular2 > radius2) continue;
            double extent = Math.Sqrt(Math.Max(0, radius2 - perpendicular2));
            if (along + extent < 0) continue;
            double entry = Math.Max(0, along - extent);
            if (entry <= maxDistance && entry < best) { best = entry; bestSlot = i; }
        }
        if (bestSlot < 0) return false;
        hit = new Hit(this, bestSlot, best);
        return true;
    }

    public bool TryResolve(Hit hit, out Marker marker)
    {
        if (!ReferenceEquals(hit.Owner, this) || hit.Slot < 0 || hit.Slot >= markers.Length)
        { marker = default; return false; }
        marker = markers[hit.Slot];
        return true;
    }

    private static bool Finite(float x) => !float.IsNaN(x) && !float.IsInfinity(x);
    private static bool Finite(Vector3 v) => Finite(v.X) && Finite(v.Y) && Finite(v.Z);
}
