// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailMeshPartPoseTests
{
    private const int One = 0x3f800000;
    private static readonly Level100FloatBasis3Bits Identity = new(One, 0, 0, 0, One, 0, 0, 0, One);
    private static readonly Level100FloatBasis3Bits Ones = new(One, One, One, One, One, One, One, One, One);

    [Fact]
    public void SingleFrameInterpolationNormalizesNegativeZeroWithoutQuantization()
    {
        var frame = new RetailUnitAttachmentPose(new(int.MinValue, 0x3dbec640, int.MinValue),
            Identity with { Row0Y = int.MinValue, Row2X = int.MinValue });
        Assert.Equal(new RetailUnitAttachmentPose(new(0, 0x3dbec640, 0), Identity),
            RetailMeshPartPose.InterpolateSingleFrame(frame));
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void TranslationSpillsYAndZBeforeAddingOwnerOrParent(bool owner)
    {
        // Synthetic arithmetic discriminator, not a retail capture: preserving
        // 1 + 2^-24 until subtracting 1 differs from storing that tie first.
        int halfUlp = BitConverter.SingleToInt32Bits(MathF.ScaleB(1, -24));
        int minusOne = BitConverter.SingleToInt32Bits(-1);
        var parent = new RetailUnitAttachmentPose(new(minusOne, minusOne, minusOne), Ones);
        var local = new RetailUnitAttachmentPose(new(One, halfUlp, 0), Identity);
        var result = owner ? RetailMeshPartPose.ApplyOwner(parent, local)
            : RetailMeshPartPose.ComposeHierarchy(parent, local);
        Assert.Equal(new Level100FloatVector3Bits(halfUlp, 0, 0), result.PositionFloatBits);
    }

    [Theory]
    [InlineData(false)]
    [InlineData(true)]
    public void HierarchyAndOwnerHaveDistinctMeasuredMatrixOrders(bool negativeMiddle)
    {
        // Synthetic 53-bit cancellation probe: the pair summed first changes
        // whether the surviving unit is lost at 2^54. No orthonormality claim.
        int large = BitConverter.SingleToInt32Bits(MathF.ScaleB(1, 54));
        int negative = BitConverter.SingleToInt32Bits(-MathF.ScaleB(1, 54));
        int middle = negativeMiddle ? negative : One;
        int last = negativeMiddle ? One : negative;
        var local = new RetailUnitAttachmentPose(default, new(
            large, large, large, middle, middle, middle, last, last, last));
        var parent = new RetailUnitAttachmentPose(default, Ones);
        var hierarchy = negativeMiddle
            ? new Level100FloatBasis3Bits(0, 0, 0, 0, One, One, One, One, One)
            : new Level100FloatBasis3Bits(One, 0, 0, 0, 0, 0, 0, 0, 0);
        var owner = negativeMiddle
            ? new Level100FloatBasis3Bits(One, One, 0, One, One, 0, One, One, 0)
            : new Level100FloatBasis3Bits(0, 0, 0, 0, 0, One, 0, 0, One);
        Assert.Equal(hierarchy, RetailMeshPartPose.ComposeHierarchy(parent, local).BasisFloatBits);
        Assert.Equal(owner, RetailMeshPartPose.ApplyOwner(parent, local).BasisFloatBits);
    }

    [Fact]
    public void WarehouseHierarchyUsesRawSingleFrameInputs()
    {
        // Source-bound arithmetic examples, not observed runtime poses.
        // The selected Warehouse asset is pinned by Level100ContactCatalog.
        var parts = Level100ContactCatalog.Instance.GetDefinition("Warehouse").Parts;
        var poses = new RetailUnitAttachmentPose[parts.Count];
        for (int i = 0; i < parts.Count; i++)
        {
            var raw = parts[i].FloatGeometry;
            Assert.All(raw.FrameMap!.Value.ToArray(), frame => Assert.Equal(0, frame));
            var p = Assert.Single(raw.HierarchyPositionWords!).Span;
            var b = Assert.Single(raw.HierarchyOrientationWords!).Span;
            var local = new RetailUnitAttachmentPose(new(I(p[0]), I(p[1]), I(p[2])), new(
                I(b[0]), I(b[1]), I(b[2]), I(b[4]), I(b[5]), I(b[6]), I(b[8]), I(b[9]), I(b[10])));
            var parent = parts[i].Parent < 0 ? new RetailUnitAttachmentPose(default, Identity)
                : poses[parts[i].Parent];
            // All actual Warehouse hierarchy parents are identity-oriented;
            // rotated leaves do not justify an invented rotated-parent sample.
            Assert.Equal(Identity, parent.BasisFloatBits);
            poses[i] = RetailMeshPartPose.ComposeHierarchy(parent,
                RetailMeshPartPose.InterpolateSingleFrame(local));
        }
        Assert.Equal(new Level100FloatVector3Bits(0x3db709c2, 0x40a1b550, 0x3ca129a0), poses[1].PositionFloatBits);
        Assert.Equal(new Level100FloatVector3Bits(0x3fdfe291, 0x40d8b0ae, I(0xc0231284)), poses[8].PositionFloatBits);
        Assert.Equal(new Level100FloatVector3Bits(I(0xbfdc217e), 0x40c5910f, I(0xc071faf6)), poses[19].PositionFloatBits);
        Assert.Equal(new Level100FloatBasis3Bits(I(0xbf6208da), I(0xb325c382), 0x3ef05e95,
            I(0xb2c733a5), One, 0x3325c382, 0x3ef05e95, I(0xb2c733a5), 0x3f6208da), poses[19].BasisFloatBits);
        Assert.NotEqual(0x3dbe76c9, poses[0].PositionFloatBits.X); // nearest-mm round trip
        Assert.Equal(0x3dbec640, poses[0].PositionFloatBits.X);
    }

    [Fact]
    public void NonFiniteInputsAreRejected()
    {
        int invalid = BitConverter.SingleToInt32Bits(float.NaN);
        var pose = new RetailUnitAttachmentPose(new(invalid, 0, 0), Identity);
        var identity = new RetailUnitAttachmentPose(default, Identity);
        Assert.Throws<ArgumentOutOfRangeException>(() => RetailMeshPartPose.InterpolateSingleFrame(pose));
        Assert.Throws<ArgumentOutOfRangeException>(() => RetailMeshPartPose.ComposeHierarchy(identity, pose));
        Assert.Throws<ArgumentOutOfRangeException>(() => RetailMeshPartPose.ApplyOwner(pose, identity));
    }

    private static int I(uint bits) => unchecked((int)bits);
}
