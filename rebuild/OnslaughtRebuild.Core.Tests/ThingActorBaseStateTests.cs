// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class ThingActorBaseStateTests
{
    [Fact]
    public void Visibility_UsesTheReleasedInvisibleFlagAndIsIdempotent()
    {
        ThingActorBaseState state = CreateState();

        Assert.False(state.Snapshot.IsInvisible);
        Assert.Equal(ThingActorFlags.None, state.Snapshot.Flags);

        state.MakeInvisible();
        state.MakeInvisible();

        Assert.True(state.Snapshot.IsInvisible);
        Assert.Equal(ThingActorFlags.Invisible, state.Snapshot.Flags);

        state.MakeVisible();
        state.MakeVisible();

        Assert.False(state.Snapshot.IsInvisible);
        Assert.Equal(ThingActorFlags.None, state.Snapshot.Flags);
    }

    [Fact]
    public void DyingAndShutdown_FollowTheReleasedOneShotFlagOrdering()
    {
        ThingActorBaseState dying = CreateState();

        Assert.True(dying.StartDieProcess());
        Assert.False(dying.StartDieProcess());
        Assert.True(dying.Snapshot.IsDying);
        Assert.True(dying.Snapshot.IsShuttingDown);
        Assert.Equal(
            ThingActorFlags.Dying | ThingActorFlags.DeclaredShutdown,
            dying.Snapshot.Flags);

        ThingActorBaseState shutdownOnly = CreateState();
        Assert.True(shutdownOnly.DeclareShutdown());
        Assert.False(shutdownOnly.DeclareShutdown());
        Assert.False(shutdownOnly.Snapshot.IsDying);
        Assert.True(shutdownOnly.Snapshot.IsShuttingDown);
    }

    [Fact]
    public void PoseTransition_CapturesOldPoseAndResetCollapsesInterpolation()
    {
        ThingActorBaseState state = CreateState();
        var next = new ThingActorPoseSnapshot(
            new SimVector3(15, 18, 41),
            IdentityBasis());

        state.AdvancePose(next);

        Assert.Equal(new SimVector3(10, 20, 30), state.Snapshot.OldPose.PositionMillimeters);
        Assert.Equal(next, state.Snapshot.CurrentPose);
        Assert.Equal(new SimVector3(5, -2, 11), state.Snapshot.LocalLastFrameMovement);

        var teleported = new ThingActorPoseSnapshot(
            new SimVector3(-1, -2, -3),
            IdentityBasis());
        state.ResetPose(teleported);

        Assert.Equal(teleported, state.Snapshot.OldPose);
        Assert.Equal(teleported, state.Snapshot.CurrentPose);
        Assert.Equal(SimVector3.Zero, state.Snapshot.LocalLastFrameMovement);
    }

    [Fact]
    public void Velocity_UpdateAddAndStopPreserveUnrelatedPoseAndAngularState()
    {
        ThingActorBaseState state = CreateState();
        ThingActorPoseSnapshot pose = state.Snapshot.CurrentPose;

        state.SetVelocity(new SimVector3(10, 20, 30));
        state.AddVelocity(new SimVector3(-2, 4, 8));

        Assert.Equal(new SimVector3(8, 24, 38), state.Snapshot.Velocity);

        state.Stop();

        Assert.Equal(SimVector3.Zero, state.Snapshot.Velocity);
        Assert.Equal(new SimVector3(4, 5, 6), state.Snapshot.AngularVelocity);
        Assert.Equal(pose, state.Snapshot.CurrentPose);
        Assert.Equal(pose, state.Snapshot.OldPose);
    }

    [Fact]
    public void ThingTypeMask_ComposesActorLineageAndReplacesTheSpecificMask()
    {
        ThingActorBaseState state = CreateState();

        Assert.Equal(0x80000043u, state.Snapshot.ThingTypeMask);
        Assert.True(state.Snapshot.IsA(ThingActorTypeMasks.Thing));
        Assert.True(state.Snapshot.IsA(ThingActorTypeMasks.ComplexThing));
        Assert.True(state.Snapshot.IsA(ThingActorTypeMasks.Actor));
        Assert.True(state.Snapshot.IsA(0x40));
        Assert.False(state.Snapshot.IsA(0x08));

        state.SetThingType(0x80);

        Assert.Equal(0x80000083u, state.Snapshot.ThingTypeMask);
        Assert.False(state.Snapshot.IsA(0x40));
        Assert.True(state.Snapshot.IsA(0x80));
    }

    [Fact]
    public void ContactTimestamps_StartAtReleasedSentinelAndUpdateIndependently()
    {
        ThingActorBaseState state = CreateState();
        int sentinel = BitConverter.SingleToInt32Bits(-100.0f);
        Assert.Equal(sentinel, state.Snapshot.LastTimeOnGroundFloatBits);
        Assert.Equal(sentinel, state.Snapshot.LastTimeInWaterFloatBits);
        Assert.Equal(sentinel, state.Snapshot.LastTimeOnObjectFloatBits);

        int ground = BitConverter.SingleToInt32Bits(1.25f);
        int water = BitConverter.SingleToInt32Bits(2.5f);
        int onObject = BitConverter.SingleToInt32Bits(3.75f);
        state.DeclareOnGround(ground);
        state.DeclareInWater(water);
        state.DeclareOnObject(onObject);

        Assert.Equal(ground, state.Snapshot.LastTimeOnGroundFloatBits);
        Assert.Equal(water, state.Snapshot.LastTimeInWaterFloatBits);
        Assert.Equal(onObject, state.Snapshot.LastTimeOnObjectFloatBits);

        int nan = BitConverter.SingleToInt32Bits(float.NaN);
        Assert.Throws<ArgumentOutOfRangeException>(() => state.DeclareOnGround(nan));
        Assert.Equal(ground, state.Snapshot.LastTimeOnGroundFloatBits);
    }

    [Fact]
    public void SnapshotRestore_RoundTripsAndRejectsImpossibleSourceState()
    {
        ThingActorBaseState state = CreateState();
        state.MakeInvisible();
        Assert.True(state.StartDieProcess());
        state.AdvancePose(new ThingActorPoseSnapshot(
            new SimVector3(40, 50, 60),
            IdentityBasis()));
        state.SetVelocity(new SimVector3(7, 8, 9));
        state.DeclareOnGround(BitConverter.SingleToInt32Bits(4.5f));
        ThingActorBaseStateSnapshot snapshot = state.Snapshot;

        var restored = new ThingActorBaseState(snapshot);

        Assert.Equal(snapshot, restored.Snapshot);

        ThingActorBaseStateSnapshot dyingWithoutShutdown = snapshot with
        {
            Flags = ThingActorFlags.Dying,
        };
        Assert.Throws<ArgumentException>(() =>
            new ThingActorBaseState(dyingWithoutShutdown));

        ThingActorBaseStateSnapshot missingActorLineage = snapshot with
        {
            ThingTypeMask = 0x40,
        };
        Assert.Throws<ArgumentException>(() =>
            new ThingActorBaseState(missingActorLineage));
    }

    [Fact]
    public void NonFinitePose_IsRejectedBeforeAnyStateMutation()
    {
        ThingActorBaseState state = CreateState();
        ThingActorBaseStateSnapshot before = state.Snapshot;
        var invalid = new ThingActorPoseSnapshot(
            new SimVector3(1, 2, 3),
            IdentityBasis() with
            {
                Row0X = BitConverter.SingleToInt32Bits(float.NaN),
            });

        Assert.Throws<ArgumentException>(() => state.AdvancePose(invalid));
        Assert.Equal(before, state.Snapshot);
        Assert.Throws<ArgumentException>(() => state.ResetPose(invalid));
        Assert.Equal(before, state.Snapshot);
        Assert.Throws<ArgumentException>(() => new ThingActorBaseState(
            invalid,
            SimVector3.Zero,
            SimVector3.Zero,
            specificTypeMask: 0));
    }

    private static ThingActorBaseState CreateState() => new(
        new ThingActorPoseSnapshot(
            new SimVector3(10, 20, 30),
            IdentityBasis()),
        new SimVector3(1, 2, 3),
        new SimVector3(4, 5, 6),
        specificTypeMask: 0x40);

    private static Level100FloatBasis3Bits IdentityBasis() => new(
        BitConverter.SingleToInt32Bits(1f), 0, 0,
        0, BitConverter.SingleToInt32Bits(1f), 0,
        0, 0, BitConverter.SingleToInt32Bits(1f));
}
