// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Parity.Maths;

namespace OnslaughtRebuild.Oracle;

/// <summary>One adapter per oracle function: words in, words out (floats as IEEE bits), matching the retail side's adapter
/// of the same name. To add a function: this file, its VC6 adapter in the data root, a generator in gen.py, functions.json.</summary>
public static class Adapters
{
    public static float F(uint w) => BitConverter.UInt32BitsToSingle(w);

    public static uint U(float f) => BitConverter.SingleToUInt32Bits(f);

    public static IReadOnlyDictionary<string, Func<uint[], uint[]>> Create(OracleContext c) =>
        new Dictionary<string, Func<uint[], uint[]>>
        {
            ["HeightField.Collide"] = i => [U(c.HeightField.Collide(new FVector(F(i[0]), F(i[1]), 0)))],
            ["HeightField.Normal"] = i =>
            {
                FVector n = c.HeightField.Normal(new FVector(F(i[0]), F(i[1]), 0));
                return [U(n.X), U(n.Y), U(n.Z)];
            },
        };
}
