// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>The frozen, orientation-relative offsets owned by the opening spline.</summary>
public sealed record Level100PanPoints(
    Level100FloatVector3Bits Point0, Level100FloatVector3Bits Point1,
    Level100FloatVector3Bits Point2, Level100FloatVector3Bits Point3);

public sealed record Level100PanCameraSnapshot(
    int StartTimeBits, int LengthBits, Level100PanPoints Points,
    RetailActorPoseSnapshot OldPose, RetailActorPoseSnapshot CurrentPose,
    uint? NextUpdateFrame);

/// <summary>
/// One current camera. A null Pan selects the attached first-person camera.
/// The player's queued control-view event survives an early skip; deleting the
/// pan removes its own update, not that independent player event.
/// </summary>
public sealed record Level100CameraSnapshot(
    uint EventFrameCount, Level100ActorId AttachedThingId,
    int? ControlViewDueTimeBits, Level100PanCameraSnapshot? Pan);

/// <summary>
/// Core owner of the Level100 opening pan and attached first-person selection.
/// Simulation supplies controller, normal-event and end-of-frame boundaries;
/// rendering only samples the resulting snapshot.
/// </summary>
/// <remarks>
/// Pinned Player.cpp:152-213 and Camera.cpp:42-59,344-393. Pristine
/// 74154bfa…7750: GotoPanView 004d2c10, CPan ctor 004198d0, Update 00419b00,
/// player event 004d2fe0, spline 00416d10/00416e30/00416fc0.
/// The spline follows native recursion/stores under PC24, not the former
/// polynomial. Camera-site FPU precision and managed orientation trig remain
/// unmeasured. The player still supplies its existing projected pose, and
/// Simulation starts this pan at its reset epoch, without retail's pre-run.
/// These explicit phase calls do not establish complete shared-world event
/// ordering or manufacture render frames for the separate attachment cache.
/// </remarks>
public sealed class Level100CameraRuntime
{
    private static readonly Level100FloatBasis3Bits Identity = new(
        Bits(1), 0, 0, 0, Bits(1), 0, 0, 0, Bits(1));
    private Level100CameraSnapshot _snapshot;

    public Level100CameraRuntime(Level100ActorId attachedThingId,
        RetailActorPoseSnapshot initialPose, uint eventFrameCount = 0,
        float panLengthSeconds = 6f)
    {
        ArgumentNullException.ThrowIfNull(initialPose);
        if (attachedThingId.Value <= 0 || !float.IsFinite(panLengthSeconds) || panLengthSeconds <= 0)
            throw new ArgumentOutOfRangeException(nameof(panLengthSeconds));
        float now = RetailEventScheduler.TimeAtFrameCount(eventFrameCount);
        var points = new Level100PanPoints(
            Transform(initialPose.BasisFloatBits, 1, 10, -4.3f),
            Transform(initialPose.BasisFloatBits, 0, 5, 1.3f),
            Transform(initialPose.BasisFloatBits, 1, -9, -1.3f),
            Transform(initialPose.BasisFloatBits, 1, -2.5f, null));
        var emptyPose = new RetailActorPoseSnapshot(default, Identity);
        var pan = new Level100PanCameraSnapshot(Bits(now), Bits(panLengthSeconds),
            points, emptyPose, emptyPose, eventFrameCount);
        // CPanCamera calls Update before installation, then shadows its result.
        pan = UpdatePan(pan, eventFrameCount, initialPose);
        pan = pan with { OldPose = pan.CurrentPose };
        float delay = (float)RetailFloat24.Subtract(panLengthSeconds, 0.05f);
        _snapshot = new(eventFrameCount, attachedThingId,
            Bits(RetailFloat24.Add(now, delay)), pan);
    }

    /// <summary>Restore retained state; do not rerun construction or sample an actor.</summary>
    public Level100CameraRuntime(Level100CameraSnapshot snapshot)
    {
        Validate(snapshot);
        _snapshot = snapshot;
    }

    public Level100CameraSnapshot Snapshot => _snapshot;

    public void AdvanceEventClock(uint frameCount)
    {
        if (frameCount != unchecked(_snapshot.EventFrameCount + 1))
            throw new InvalidOperationException("Camera requires every simulation event frame.");
        _snapshot = _snapshot with { EventFrameCount = frameCount };
    }

    /// <summary>Player 4000, after controller dispatch. A missing reader refuses handoff.</summary>
    public void DeliverControlViewEvent(bool attachedReaderExists)
    {
        if (_snapshot.ControlViewDueTimeBits is not int due ||
            Read(due) > RetailEventScheduler.TimeAtFrameCount(_snapshot.EventFrameCount))
            return;
        _snapshot = _snapshot with
        {
            ControlViewDueTimeBits = null,
            Pan = attachedReaderExists ? null : _snapshot.Pan,
        };
    }

    /// <summary>
    /// The caller admits BUTTON_SKIP_PANNING only while GAME_STATE_PANNING.
    /// GotoControlView still requires the player's Battle Engine reader.
    /// </summary>
    public void SkipPan(bool attachedReaderExists)
    {
        if (attachedReaderExists && _snapshot.Pan is not null)
            _snapshot = _snapshot with { Pan = null };
    }

    /// <summary>Camera 2000 runs after movement, including every unrendered update.</summary>
    public void EndEventFrame(RetailActorPoseSnapshot? attachedPose)
    {
        if (_snapshot.Pan is not { NextUpdateFrame: uint next } pan ||
            next > _snapshot.EventFrameCount)
            return;
        _snapshot = _snapshot with
        {
            Pan = UpdatePan(pan, _snapshot.EventFrameCount, attachedPose),
        };
    }

    /// <summary>
    /// Current GetPos, without render interpolation. CThingCamera uses the
    /// Battle Engine's live position; CPanCamera uses its retained position.
    /// A missing attached reader returns ZERO only for CThingCamera.
    /// </summary>
    public Level100FloatVector3Bits GetCurrentPosition(RetailActorPoseSnapshot? attachedPose) =>
        _snapshot.Pan?.CurrentPose.PositionFloatBits ?? attachedPose?.PositionFloatBits ?? default;

    /// <summary>
    /// Explicit adapter from the current player projection (X/right, Y/up,
    /// Z/forward, millimetres) to retail XYZ (Z/down). This is not raw player RE.
    /// </summary>
    public static RetailActorPoseSnapshot FromPlayerPose(ThingActorPoseSnapshot pose)
    {
        ArgumentNullException.ThrowIfNull(pose);
        Level100FloatBasis3Bits b = pose.BasisFloatBits;
        return new(new(Bits(pose.PositionMillimeters.X * 0.001f),
                Bits(pose.PositionMillimeters.Z * 0.001f),
                Bits(-pose.PositionMillimeters.Y * 0.001f)),
            new(b.Row0X, b.Row0Z, Negate(b.Row0Y),
                b.Row2X, b.Row2Z, Negate(b.Row2Y),
                Negate(b.Row1X), Negate(b.Row1Z), b.Row1Y));
    }

    private static Level100PanCameraSnapshot UpdatePan(Level100PanCameraSnapshot pan,
        uint frameCount, RetailActorPoseSnapshot? attachedPose)
    {
        pan = pan with { OldPose = pan.CurrentPose, NextUpdateFrame = null };
        double fraction = RetailFloat24.Divide(RetailFloat24.Subtract(
            RetailEventScheduler.TimeAtFrameCount(frameCount), Read(pan.StartTimeBits)), Read(pan.LengthBits));
        // Native compares the retained result after a float store. Equality
        // reaches the half-open spline endpoint; it is not clamped below one.
        if (fraction > 1) return pan;
        Level100FloatVector3Bits offset = EvaluateSpline(pan.Points, (float)fraction);
        if (attachedPose is not null)
        {
            Level100FloatVector3Bits center = attachedPose.PositionFloatBits;
            var position = new Level100FloatVector3Bits(
                Bits(RetailFloat24.Add(Read(center.X), Read(offset.X))),
                Bits(RetailFloat24.Add(Read(center.Y), Read(offset.Y))),
                Bits(RetailFloat24.Add(Read(center.Z), Read(offset.Z))));
            double dx = (float)RetailFloat24.Subtract(Read(center.X), Read(position.X));
            double dy = (float)RetailFloat24.Subtract(Read(center.Y), Read(position.Y));
            double wideZ = RetailFloat24.Subtract(Read(center.Z), Read(position.Z));
            double dz = (float)wideZ;
            double magnitude = RetailFloat24.Sqrt(RetailFloat24.Add(RetailFloat24.Add(
                RetailFloat24.Multiply(dy, dy), RetailFloat24.Multiply(wideZ, wideZ)),
                RetailFloat24.Multiply(dx, dx)));
            Level100FloatBasis3Bits basis = pan.CurrentPose.BasisFloatBits;
            if (magnitude != 0)
            {
                // 419c0e/419c23: stored dz/magnitude -> asin, then -atan2(dx,dy).
                // These angles have no float store before trig. The managed
                // transcendental results remain a bounded approximation.
                double pitch = Math.Asin(RetailFloat24.Divide(dz, (float)magnitude));
                double yaw = -Math.Atan2(dx, dy);
                basis = RetailUnitEuler.CombineTrig((float)Math.Cos(yaw), (float)Math.Sin(yaw),
                    (float)Math.Cos(pitch), Math.Sin(pitch), 1, 0);
            }
            pan = pan with { CurrentPose = new(position, basis) };
        }
        // A missing reader holds the pose but still files a NEW next-frame
        // event. Only replacing the pan or fraction > 1 ends its recurrence.
        return pan with { NextUpdateFrame = unchecked(frameCount + 1) };
    }

    internal static Level100FloatVector3Bits EvaluateSpline(Level100PanPoints points, float fraction)
    {
        // Pristine 416fc0: n=3,k=3; t stores (n-k+2)*val. Knots are integers.
        float t = (float)RetailFloat24.Multiply(2, fraction);
        ReadOnlySpan<int> knots = [0, 0, 0, 1, 2, 2, 2];
        ReadOnlySpan<Level100FloatVector3Bits> ordered =
            [points.Point0, points.Point1, points.Point2, points.Point3];
        float x = 0, y = 0, z = 0;
        for (int index = 0; index < ordered.Length; index++)
        {
            double weight = Weight(index, 3, t, knots);
            Level100FloatVector3Bits p = ordered[index];
            x = (float)RetailFloat24.Add(RetailFloat24.Multiply(weight, Read(p.X)), x);
            y = (float)RetailFloat24.Add(RetailFloat24.Multiply(weight, Read(p.Y)), y);
            z = (float)RetailFloat24.Add(RetailFloat24.Multiply(weight, Read(p.Z)), z);
        }
        return new(Bits(x), Bits(y), Bits(z));
    }

    private static double Weight(int i, int order, float t, ReadOnlySpan<int> knots)
    {
        if (order == 1) return knots[i] <= t && t < knots[i + 1] ? 1 : 0;
        int leftDenominator = knots[i + order - 1] - knots[i];
        int rightDenominator = knots[i + order] - knots[i + 1];
        double left = 0;
        if (leftDenominator != 0)
        {
            double child = Weight(i, order - 1, t, knots);
            left = RetailFloat24.Multiply(child, RetailFloat24.Divide(
                RetailFloat24.Subtract(t, knots[i]), leftDenominator));
            if (rightDenominator == 0) return left;
            left = (float)left; // 416f86, before the right recursive call.
        }
        if (rightDenominator == 0) return 0;
        double rightChild = Weight(i + 1, order - 1, t, knots);
        double right = RetailFloat24.Multiply(rightChild, RetailFloat24.Divide(
            RetailFloat24.Subtract(knots[i + order], t), rightDenominator));
        return leftDenominator == 0 ? right : RetailFloat24.Add(right, left);
    }

    private static Level100FloatVector3Bits Transform(Level100FloatBasis3Bits m,
        int column, float scale, float? zScale)
    {
        // 4d2d1c/4d2d92/4d2e48/4d2eba specialize away zero-coordinate
        // products. Keep the final point stores and the reversed point-1 X sum.
        static int Row(int value, int z, float scale, float? zScale, bool reverse)
        {
            double first = RetailFloat24.Multiply(Read(value), scale);
            if (zScale is not float otherScale) return Bits(first);
            double last = RetailFloat24.Multiply(Read(z), otherScale);
            return Bits(reverse ? RetailFloat24.Add(last, first) : RetailFloat24.Add(first, last));
        }
        return new(Row(column == 0 ? m.Row0X : m.Row0Y, m.Row0Z, scale, zScale, column == 0),
            Row(column == 0 ? m.Row1X : m.Row1Y, m.Row1Z, scale, zScale, false),
            Row(column == 0 ? m.Row2X : m.Row2Y, m.Row2Z, scale, zScale, false));
    }

    internal static void Validate(Level100CameraSnapshot snapshot)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        if (snapshot.AttachedThingId.Value <= 0)
            throw new ArgumentException("Camera attachment identity is invalid.", nameof(snapshot));
        if (snapshot.ControlViewDueTimeBits is int due && !float.IsFinite(Read(due)))
            throw new ArgumentException("Camera handoff time must be finite.", nameof(snapshot));
        if (snapshot.Pan is not { } pan) return;
        if (!float.IsFinite(Read(pan.StartTimeBits)) || !float.IsFinite(Read(pan.LengthBits)) ||
            Read(pan.LengthBits) <= 0 || pan.Points is null || pan.OldPose is null || pan.CurrentPose is null)
            throw new ArgumentException("Incomplete pan state.", nameof(snapshot));
        ValidateVector(pan.Points.Point0); ValidateVector(pan.Points.Point1);
        ValidateVector(pan.Points.Point2); ValidateVector(pan.Points.Point3);
        foreach (RetailActorPoseSnapshot pose in new[] { pan.OldPose, pan.CurrentPose })
        {
            ValidateVector(pose.PositionFloatBits);
            Level100FloatBasis3Bits b = pose.BasisFloatBits;
            ValidateVector(new(b.Row0X, b.Row0Y, b.Row0Z));
            ValidateVector(new(b.Row1X, b.Row1Y, b.Row1Z));
            ValidateVector(new(b.Row2X, b.Row2Y, b.Row2Z));
        }
    }

    private static void ValidateVector(Level100FloatVector3Bits p)
    {
        if (!float.IsFinite(Read(p.X)) || !float.IsFinite(Read(p.Y)) || !float.IsFinite(Read(p.Z)))
            throw new ArgumentException("Camera vectors must be finite.");
    }

    private static int Negate(int word) => word ^ int.MinValue;
    private static float Read(int word) => BitConverter.Int32BitsToSingle(word);
    private static int Bits(double value) => BitConverter.SingleToInt32Bits((float)value);
}
