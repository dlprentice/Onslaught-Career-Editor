// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// Retail's non-linear look-axis response, ported from
/// references/Onslaught/Player.cpp:334-355.
/// </summary>
/// <remarks>
/// The released law, gated on exactly the four look buttons
/// (BUTTON_MECH_YAW_LEFT/RIGHT, BUTTON_MECH_PITCH_UP/DOWN):
/// <code>
///     t1 = tan(val * 1.2f) * 3.0f          // sign-preserving
///     static t2 = tan(1.2f) * 3.0f
///     val = t1 / t2
/// </code>
/// The 3.0 cancels, so the mapping is tan(1.2*val) / tan(1.2). It is
/// NORMALISED — f(0) = 0 and f(1) = 1 — and therefore COMPRESSIVE, not
/// expansive: the slope at centre is 1.2 / tan(1.2) = 0.4665, so retail gives
/// roughly half our sensitivity to a small correction and reaches full rate
/// only at the stops. The developers' comment beside it is the specification:
/// "should give a curve so 50% before would result in 25% after"; the law
/// returns 0.266 at 0.5.
///
/// Core is integer fixed-point and must stay bit-reproducible, so the curve is
/// a checked-in table rather than a Math.Tan call — .NET does not guarantee
/// transcendentals are identical across runtimes, and the smoke state hash
/// would inherit that. The table samples every 10 permille and interpolates
/// linearly; LookAxisResponseTests asserts every one of the 1001 integer inputs
/// against the double-precision law, worst case 0.55 permille.
///
/// Retail has no digital look producer at all — PCController.cpp:91-95 maps all
/// four look buttons to ANALOGUE_X2/Y2. Core's digital +-1 saturates the
/// combined input, and the curve maps full deflection to full deflection, so a
/// digital tap stays faithful; only partial analog values were diverging.
/// </remarks>
public static class LookAxisResponse
{
    private const int Step = 10;

    // round(1000 * tan(1.2 * i/100) / tan(1.2)) for i in 0..100.
    private static readonly int[] Curve =
    [
        0, 5, 9, 14, 19, 23, 28, 33, 37, 42,
        47, 52, 56, 61, 66, 71, 76, 80, 85, 90,
        95, 100, 105, 110, 115, 120, 125, 131, 136, 141,
        146, 152, 157, 163, 168, 174, 179, 185, 191, 197,
        202, 208, 214, 221, 227, 233, 239, 246, 252, 259,
        266, 273, 280, 287, 294, 302, 309, 317, 325, 333,
        341, 349, 358, 367, 375, 385, 394, 404, 413, 423,
        434, 444, 455, 466, 478, 490, 502, 515, 528, 541,
        555, 570, 585, 600, 616, 633, 650, 668, 687, 707,
        727, 749, 771, 795, 820, 846, 873, 902, 933, 966,
        1000,
    ];

    /// <summary>
    /// Maps a clamped look input in permille to its released response, in
    /// permille. Odd-symmetric, so axis inversion may be applied on either
    /// side of the call.
    /// </summary>
    public static int Apply(int inputPermille)
    {
        int magnitude = Math.Clamp(Math.Abs(inputPermille), 0, 1_000);
        int index = magnitude / Step;
        // The curve rises monotonically, so the interpolation delta is never
        // negative and a half-step bias rounds to nearest. Truncating here
        // costs almost a whole permille on its own and breaches the bound the
        // tests hold this table to.
        int response = index >= Curve.Length - 1
            ? Curve[^1]
            : Curve[index] + ((((Curve[index + 1] - Curve[index]) *
                (magnitude - (index * Step))) + (Step / 2)) / Step);
        return inputPermille < 0 ? -response : response;
    }
}
