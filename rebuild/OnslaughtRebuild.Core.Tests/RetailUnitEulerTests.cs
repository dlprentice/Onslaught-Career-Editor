// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailUnitEulerTests
{
    // Outputs are from the unchanged pristine 847-byte function, executed in
    // an isolated ELF32 probe with an explicit PC24/RN control word. Only its
    // virtual multiplier is supplied; no game frame, resource or RNG is used.
    // Specimen/body pins and private probe path are in CComplexThing.cpp.md.
    [Theory]
    [MemberData(nameof(NativeCases))]
    public void SmoothMatchesIsolatedRetailRoutine(string scenario,
        Level100FloatVector3Bits current, Level100FloatVector3Bits desired,
        Level100FloatVector3Bits rate, float multiplier, Level100FloatVector3Bits expected)
    {
        Level100FloatVector3Bits actual = RetailUnitEuler.Smooth(current, desired, rate, multiplier);
        Assert.True(expected == actual, $"{scenario}: expected {expected}, actual {actual}");
    }

    public static IEnumerable<object[]> NativeCases()
    {
        Level100FloatVector3Bits zero = Uniform(0);
        Level100FloatVector3Bits one = Uniform(0x3f800000);
        yield return ["zero", zero, zero, one, 1f, zero];
        yield return ["equal-negative-zero", Uniform(0x80000000), zero, one, 1f, Uniform(0x80000000)];
        yield return ["equal-outside-pi", Floats(7, -7, 7), Floats(7, -7, 7), one, 1f, Floats(7, -7, 7)];
        yield return ["wrapped-versus-pitch", Floats(3.125f, 3.125f, 3.125f), Floats(-3.125f, -3.125f, -3.125f),
            one, 1f, Words(0x4048365f, 0x40200000, 0x4048365f)];
        yield return ["reverse-wrapped-versus-pitch", Floats(-3.125f, -3.125f, -3.125f), Floats(3.125f, 3.125f, 3.125f),
            one, 1f, Words(0xc048365f, 0xc0200000, 0xc048365f)];
        yield return ["pi-direction", zero, Uniform(0x40490fdb), one, 1f, Uniform(0x3ea0d97c)];
        yield return ["pi-next-direction", zero, Uniform(0x40490fdc), one, 1f, Words(0xbea0d97d, 0x3ea0d97d, 0xbea0d97d)];
        yield return ["negative-pi-direction", zero, Uniform(0xc0490fdb), one, 1f, Uniform(0xbea0d97c)];
        yield return ["negative-pi-next-direction", zero, Uniform(0xc0490fdc), one, 1f, Words(0x3ea0d97d, 0xbea0d97d, 0x3ea0d97d)];
        yield return ["equal-cap", zero, one, Uniform(0x3dcccccd), 1f, Uniform(0x3dcccccd)];
        yield return ["lower-cap", zero, one, Uniform(0x3dcccccc), 1f, Uniform(0x3dcccccc)];
        yield return ["plane-noncanonical-roll", zero, Words(0, 0, 0x40e2a975), one, 1f, Words(0, 0, 0xbf35545e)];
        yield return ["single-wrap-only", Floats(15, 15, 15), Floats(16, 16, 16), one, 1f,
            Words(0x410d11ac, 0x4171999a, 0x410d11ac)];
        yield return ["four-tick-multiplier", Floats(.3f, -.2f, .1f), Floats(.6f, -.9f, .8f),
            Floats(.01f, .3f, .2f), 4f, Words(0x3eae147b, 0xbef5c290, 0x3ec28f5c)];
        yield return ["coefficient-not-division", zero, Floats(.1f, .1f, .1f), one, 1f, Uniform(0x3c23d70b)];
        yield return ["retained-subnormal-step", Uniform(1), Uniform(6), one, 1f, Uniform(2)];
        yield return ["half-pi-boundary", Uniform(0xbfc90fdb), Floats(5, 5, 5), one, 1f,
            Words(0xc00e9585, 0xbf69e957, 0xc00e9585)];
        yield return ["past-half-pi", Uniform(0xbfc90fdc), Floats(5, 5, 5), one, 1f,
            Words(0xbfccbe4e, 0xbf69e959, 0xbfccbe4e)];
        Level100FloatVector3Bits mixed = Words(0x3f333333, 0x3f8ccccd, 0xbecccccd);
        yield return ["equal-mixed", mixed, mixed, one, 1f, mixed];
    }

    private static Level100FloatVector3Bits Uniform(uint value) => Words(value, value, value);
    private static Level100FloatVector3Bits Words(uint x, uint y, uint z) =>
        new(unchecked((int)x), unchecked((int)y), unchecked((int)z));
    private static Level100FloatVector3Bits Floats(float x, float y, float z) =>
        new(BitConverter.SingleToInt32Bits(x), BitConverter.SingleToInt32Bits(y), BitConverter.SingleToInt32Bits(z));
}
