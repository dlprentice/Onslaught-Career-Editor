// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.Numerics;
using System.Text.RegularExpressions;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// What a typed coordinate comes to: the 32-bit float the world body stores, whether the stored number is not exactly the one typed
/// (so the page can say so), or why the text is not a coordinate.
/// </summary>
/// <param name="Value">The float32 that is stored (meaningful when <paramref name="Problem"/> is null).</param>
/// <param name="Rounded">True when the typed decimal is not exactly representable and <paramref name="Value"/> is the nearest float32.</param>
/// <param name="Problem">A sentence for the player, or null.</param>
public readonly record struct CoordinateParse(float Value, bool Rounded, string? Problem)
{
    public bool Ok => Problem is null;
}

/// <summary>
/// Reads a coordinate typed into a field as the Toolkit's move tool reads it (<c>tools/world_edit_move.py</c>): the decimal is read
/// exactly, converted to the nearest double and then to the nearest float32, refused when it is not finite or outside float32's
/// range, and called rounded when the float32 is not exactly the decimal that was typed. The page stores the float32 and says so.
/// Stricter than the tool in what it accepts as text, never looser: a sign, ASCII digits with a point, and an exponent of up to 18
/// digits; surrounding ASCII spaces are ignored; no digit separators, no other digits, no other whitespace. A negative zero stays a
/// negative zero, never canonicalised.
/// </summary>
public static partial class CoordinateInput
{
    /// <summary>The tool refuses coordinate text longer than this.</summary>
    public const int MaxLength = 128;

    /// <summary>Exponent digits the move tool's decimal reader takes before it refuses the text (a 19-digit exponent is refused).</summary>
    private const int MaxExponentDigits = 18;

    [GeneratedRegex(@"\A([+-]?)([0-9]*)(?:\.([0-9]*))?(?:[eE]([+-]?)([0-9]+))?\z", RegexOptions.CultureInvariant)]
    private static partial Regex NumberText();

    public static CoordinateParse Parse(string text)
    {
        if (text.Length > MaxLength) return Refuse("That is not a coordinate: it is too long.");
        string trimmed = text.Trim(' ');
        Match match = NumberText().Match(trimmed);
        string integer = match.Groups[2].Value, fraction = match.Groups[3].Value;
        if (!match.Success || integer.Length + fraction.Length == 0)
            return Refuse(trimmed.Length == 0 ? "Type a number." : $"\"{trimmed}\" is not a number. Write it like 276.49 or -12.1 or 1e3.");
        bool negative = match.Groups[1].Value == "-";
        BigInteger digits = BigInteger.Parse(integer + fraction, CultureInfo.InvariantCulture);
        long exponent = 0;
        if (match.Groups[5].Success)
        {
            string magnitude = match.Groups[5].Value.TrimStart('0');
            if (magnitude.Length > MaxExponentDigits) return Refuse($"\"{trimmed}\" has an exponent that is far too large to be a coordinate.");
            exponent = magnitude.Length == 0 ? 0 : long.Parse(magnitude, CultureInfo.InvariantCulture) * (match.Groups[4].Value == "-" ? -1 : 1);
        }
        long scale = checked(exponent - fraction.Length);

        if (digits.IsZero) return new CoordinateParse(negative ? -0f : 0f, false, null);
        int digitCount = digits.ToString(CultureInfo.InvariantCulture).Length;
        if (scale + digitCount > 40) return Refuse($"\"{trimmed}\" is too large: a stored coordinate is a 32-bit float, at most about 3.4e38.");
        if (scale + digitCount < -50) return new CoordinateParse(negative ? -0f : 0f, true, null);

        // The nearest double (correctly rounded, as Python's float(Decimal)), then the nearest float32.
        double asDouble = double.Parse((negative ? "-" : "") + digits.ToString(CultureInfo.InvariantCulture) + "E" + scale.ToString(CultureInfo.InvariantCulture), NumberStyles.Float, CultureInfo.InvariantCulture);
        float stored = (float)asDouble;
        if (double.IsInfinity(asDouble) || float.IsInfinity(stored)) return Refuse($"\"{trimmed}\" is too large: a stored coordinate is a 32-bit float, at most about 3.4e38.");
        return new CoordinateParse(stored, !Equal(digits, scale, stored), null);
    }

    /// <summary>The shortest text that reads back as the same float32 ("276.49"); a negative zero is "-0".</summary>
    public static string Format(float value) => value.ToString("R", CultureInfo.InvariantCulture);

    /// <summary>The float32's exact decimal value ("276.489990234375" for 276.49), in plain notation; a negative zero is "-0".</summary>
    public static string Exact(float value)
    {
        if (!float.IsFinite(value)) return value.ToString(CultureInfo.InvariantCulture);
        if (value == 0f) return float.IsNegative(value) ? "-0" : "0";
        (BigInteger mantissa, int binary) = Parts(value);
        // mantissa x 2^binary as digits x 10^-point (2^-n is 5^n / 10^n).
        string digits = binary >= 0 ? (mantissa << binary).ToString(CultureInfo.InvariantCulture)
            : (mantissa * BigInteger.Pow(5, -binary)).ToString(CultureInfo.InvariantCulture);
        int point = binary >= 0 ? 0 : -binary;
        string whole = digits.Length > point ? digits[..^point] : "0";
        string part = point == 0 ? "" : digits.Length > point ? digits[^point..] : new string('0', point - digits.Length) + digits;
        part = part.TrimEnd('0');
        return (float.IsNegative(value) ? "-" : "") + whole + (part.Length == 0 ? "" : "." + part);
    }

    private static CoordinateParse Refuse(string problem) => new(0f, false, problem);

    /// <summary>The magnitude of a finite nonzero float32 as mantissa x 2^binary.</summary>
    private static (BigInteger Mantissa, int Binary) Parts(float value)
    {
        int bits = BitConverter.SingleToInt32Bits(value) & 0x7FFFFFFF;
        int biased = bits >> 23, fraction = bits & 0x7FFFFF;
        return (biased == 0 ? fraction : fraction | 0x800000, (biased == 0 ? 1 : biased) - 127 - 23);
    }

    /// <summary>Whether digits x 10^scale is exactly the magnitude of the float32 (compared as integers, so nothing is rounded); the sign was read with the digits.</summary>
    private static bool Equal(BigInteger digits, long scale, float stored)
    {
        if (stored == 0f) return false;
        (BigInteger mantissa, int binary) = Parts(stored);
        // digits x 10^scale == mantissa x 2^binary, with every power moved to the side that makes it an integer.
        BigInteger left = digits * BigInteger.Pow(10, (int)Math.Max(scale, 0)) * BigInteger.Pow(2, Math.Max(-binary, 0));
        BigInteger right = mantissa * BigInteger.Pow(2, Math.Max(binary, 0)) * BigInteger.Pow(10, (int)Math.Max(-scale, 0));
        return left == right;
    }
}
