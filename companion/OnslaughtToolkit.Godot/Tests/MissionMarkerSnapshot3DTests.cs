using System;
using System.Collections.Generic;
using System.Numerics;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

internal static class MissionMarkerSnapshot3DTests
{
    internal static void Run(Checks check)
    {
        var markers = new List<MissionMarkerSnapshot3D.Marker>
        {
            new(10, new Vector3(0, 0, 9)),
            new(20, new Vector3(0, 0, 4)),
            new(30, new Vector3(3, 0, 3)),
        };
        var snapshot = MissionMarkerSnapshot3D.Capture(markers, 3);
        check.That(snapshot.Count == 3, "3D marker snapshot includes its input rows");
        check.That(snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out var closest), "3D marker ray finds a hit");
        check.That(snapshot.TryResolve(closest, out var selected) && selected.Index == 20, "3D marker ray selects the nearest surface");
        check.That(Math.Abs(closest.Distance - 3) < 0.00001, "3D marker hit reports distance to the surface");
        check.That(snapshot.TryPick(Vector3.Zero, Vector3.UnitZ * 10, 1, 20, out var scaled) && Math.Abs(scaled.Distance - closest.Distance) < 0.00001, "3D marker ray direction is normalized");
        check.That(!snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 2, out _), "3D marker range excludes distant hits");
        check.That(!snapshot.TryPick(Vector3.Zero, -Vector3.UnitZ, 1, 20, out _), "3D marker ray excludes points behind it");
        check.That(snapshot.TryPick(new Vector3(0, 0, 4), Vector3.UnitX, 1, 0, out var inside) && inside.Distance == 0, "3D marker origin inside a sphere hits immediately");
        check.That(!snapshot.TryPick(Vector3.Zero, Vector3.Zero, 1, 20, out _), "3D marker rejects zero direction");
        check.That(!snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, 0, 20, out _), "3D marker rejects zero radius");
        check.That(!snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, 1, -1, out _), "3D marker rejects negative distance");
        check.That(!snapshot.TryPick(new Vector3(float.NaN, 0, 0), Vector3.UnitZ, 1, 20, out _), "3D marker rejects nonfinite origin");
        check.That(!snapshot.TryPick(Vector3.Zero, new Vector3(float.PositiveInfinity, 0, 0), 1, 20, out _), "3D marker rejects nonfinite direction");
        check.That(!snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, float.NaN, 20, out _), "3D marker rejects nonfinite radius");
        check.That(!snapshot.TryPick(Vector3.Zero, Vector3.UnitZ, 1, float.PositiveInfinity, out _), "3D marker rejects nonfinite distance");
        markers[1] = new MissionMarkerSnapshot3D.Marker(40, new Vector3(0, 0, 2));
        check.That(snapshot.TryResolve(closest, out selected) && selected.Index == 20, "3D marker snapshot copies caller rows");
        var next = MissionMarkerSnapshot3D.Capture(markers, 3);
        check.That(!next.TryResolve(closest, out _), "3D marker rejects a hit from a different snapshot");
        check.That(!snapshot.TryResolve(default, out _), "3D marker rejects an empty hit");
        check.That(next.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out var nextHit) && next.TryResolve(nextHit, out var nextMarker) && nextMarker.Index == 40, "3D marker new snapshot uses current rows");
        var tied = MissionMarkerSnapshot3D.Capture(new[]
        {
            new MissionMarkerSnapshot3D.Marker(5, new Vector3(0, 0, 4)),
            new MissionMarkerSnapshot3D.Marker(6, new Vector3(0, 0, 4)),
        }, 2);
        check.That(tied.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out var tie) && tied.TryResolve(tie, out var first) && first.Index == 5, "3D marker ties use the earlier row");
        var offAxis = MissionMarkerSnapshot3D.Capture(new[]
        {
            new MissionMarkerSnapshot3D.Marker(11, new Vector3(0.9f, 0, 3.5f)),
            new MissionMarkerSnapshot3D.Marker(12, new Vector3(0, 0, 4)),
        }, 2);
        check.That(offAxis.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out var front) && offAxis.TryResolve(front, out var frontRow) && frontRow.Index == 12, "3D marker selects the first surface rather than the closest centre");
        var invalid = MissionMarkerSnapshot3D.Capture(new[]
        {
            new MissionMarkerSnapshot3D.Marker(7, new Vector3(float.NaN, 0, 1)),
            new MissionMarkerSnapshot3D.Marker(8, new Vector3(0, 0, 4)),
        }, 2);
        check.That(invalid.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out var valid) && invalid.TryResolve(valid, out var validRow) && validRow.Index == 8, "3D marker ignores nonfinite positions");
        var huge = MissionMarkerSnapshot3D.Capture(new[]
        {
            new MissionMarkerSnapshot3D.Marker(9, new Vector3(0, 0, 1e30f)),
        }, 1);
        check.That(huge.TryPick(Vector3.Zero, new Vector3(0, 0, 1e30f), 1e24f, 2e30f, out _), "3D marker handles large finite coordinates");
        var empty = MissionMarkerSnapshot3D.Capture(Array.Empty<MissionMarkerSnapshot3D.Marker>(), 0);
        check.That(!empty.TryPick(Vector3.Zero, Vector3.UnitZ, 1, 20, out _), "3D marker empty snapshot has no hit");
        bool overLimit = false, negativeLimit = false, nullInput = false;
        try { MissionMarkerSnapshot3D.Capture(markers, 2); } catch (InvalidOperationException) { overLimit = true; }
        try { MissionMarkerSnapshot3D.Capture(markers, -1); } catch (ArgumentOutOfRangeException) { negativeLimit = true; }
        try { MissionMarkerSnapshot3D.Capture((IReadOnlyList<MissionMarkerSnapshot3D.Marker>)null!, 1); } catch (ArgumentNullException) { nullInput = true; }
        check.That(overLimit && negativeLimit && nullInput, "3D marker snapshot enforces input limits");
    }

    internal static void CheckEditorSnapshot(Checks check, LevelEditorModel editor)
    {
        var rows = editor.Rows();
        var snapshot = MissionMarkerSnapshot3D.Capture(editor, rows.Count);
        check.That(snapshot.Count == rows.Count, "3D snapshot reads the editor model");
        bool same = true;
        for (int i = 0; i < rows.Count; i++)
        {
            var marker = snapshot.MarkerAt(i);
            same &= marker.Index == rows[i].Index && marker.Position.Equals(rows[i].Position);
        }
        check.That(same, "3D snapshot preserves editor row indices and positions");
        check.That(rows.Count > 0, "3D snapshot fixture contains an editable row");
        if (rows.Count > 0)
        {
            var first = snapshot.MarkerAt(0);
            check.That(snapshot.TryPick(first.Position, Vector3.UnitX, 0.1f, 1, out var hit)
                && snapshot.TryResolve(hit, out var picked) && picked.Index == first.Index,
                "3D editor rows can be picked and resolved on their owning snapshot");
        }
    }
}
