// SPDX-License-Identifier: GPL-3.0-or-later
using System.Globalization;
using System.Numerics;

// Existing .NET parsing/formatting semantics, not a new retail numeric law.
internal static class GdscriptInvariantNumberOracle
{
    internal static object Build()
    {
        var text = new HashSet<string?>(StringComparer.Ordinal) { null, "", " ", "0", "-0", "+0", "1", "+1", "-1",
            "2147483647", "2147483648", "-2147483648", "-2147483649", "4294967296", "99999999999999999999999",
            "2147483648junk", "-2147483649junk", "1.0", ".5", "1.", "+.5", "000001.5000", "-.0",
            "1e0", "1E+09", "1e-9999", "-1e-9999", "1e9999", "1e", "1e+", "1e-", ".", "1,000", "1_000",
            "NaN", "nan", "NAN", "+NaN", "-NaN", "Infinity", "infinity", "+Infinity", "-Infinity", "∞",
            "1\0", "1\0\0", "1 \0", "1\0 ", "NaN\0", "\0NaN", "1\ud800", "１", "١", "−1",
            "1.000000059604644775390625", "1.0000000596046447753906250000000000000000001",
            "1.0000000596046447753906249999999999999999999", "-1.0000000596046447753906250000000000000000001",
            "7.00649232162408535461864791644958e-46", "7.00649232162408535461864791644958065640130970938257885878534141944895541342930300743319094181060791015625e-46",
            "3.40282346638528859811704183484516925440e38", "3.40282356779733661637539395458142568448e38" };
        foreach (char unit in Enumerable.Range(0, 128).Concat(new[] { 0x85, 0xa0, 0x1680, 0x2000, 0x200a, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000, 0xfeff, 0xd800, 0xdc00 }).Select(x => (char)x))
            foreach (string atom in new[] { "1", "-2.5", "NaN", "+Infinity" })
            {
                text.Add(unit + atom);
                text.Add(atom + unit);
                text.Add(unit + atom + unit);
            }
        var words = new HashSet<uint> { 0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x00800000,
            0x3f800000, 0xbf800000, 0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
            0x7fc00000, 0xffc00001, 0x7f800001, 0xff800001 };
        for (int power = -46; power <= 39; power++)
        {
            float value = float.Parse("1e" + power, NumberStyles.Float, CultureInfo.InvariantCulture);
            foreach (float nearby in new[] { value, MathF.BitDecrement(value), MathF.BitIncrement(value), -value })
                words.Add(BitConverter.SingleToUInt32Bits(nearby));
        }
        uint random = 0x4e554d42;
        for (int index = 0; index < 2048; index++)
        {
            random = unchecked(random * 1664525u + 1013904223u);
            words.Add(random);
            float value = BitConverter.UInt32BitsToSingle(random);
            text.Add(value.ToString("R", CultureInfo.InvariantCulture));
            text.Add(((double)value).ToString("R", CultureInfo.InvariantCulture));
        }
        // Decimal midpoints and their immediate decimal neighbors detect the
        // double-rounding error from parse-as-double then narrow-to-Single.
        foreach (uint word in new uint[] { 0, 1, 0x007ffffe, 0x007fffff, 0x00800000, 0x3f7fffff, 0x3f800000, 0x3f800001, 0x4b000000, 0x7f7ffffe })
        {
            string midpoint = ExactMidpoint(word);
            text.Add(midpoint);
            text.Add("-" + midpoint);
            var digits = midpoint.Replace(".", "");
            int places = midpoint.Length - midpoint.IndexOf('.') - 1;
            BigInteger number = BigInteger.Parse(digits, CultureInfo.InvariantCulture) * 10;
            foreach (int delta in new[] { -1, 1 })
            {
                string varied = (number + delta).ToString(CultureInfo.InvariantCulture).PadLeft(places + 2, '0');
                text.Add(varied.Insert(varied.Length - places - 1, "."));
            }
        }
        return new
        {
            schema = 1,
            parsing = text.Select(value => new { units = Units(value), integer = ParseInt(value), single = ParseSingle(value) }).ToArray(),
            formatting = words.Select(word => new { bits = word, text = BitConverter.UInt32BitsToSingle(word).ToString(CultureInfo.InvariantCulture) }).ToArray()
        };
    }

    private static object ParseInt(string? value)
    {
        try { return new { ok = true, value = int.Parse(value!, NumberStyles.Integer, CultureInfo.InvariantCulture) }; }
        catch (Exception error) { return Failure(error); }
    }
    private static object ParseSingle(string? value)
    {
        try { return new { ok = true, bits = BitConverter.SingleToUInt32Bits(float.Parse(value!, NumberStyles.Float, CultureInfo.InvariantCulture)) }; }
        catch (Exception error) { return Failure(error); }
    }
    private static object Failure(Exception error) => new { ok = false, error_type = error.GetType().Name,
        parameter = (error as ArgumentException)?.ParamName ?? "" };
    private static int[]? Units(string? value) => value?.Select(unit => (int)unit).ToArray();

    private static string ExactMidpoint(uint word)
    {
        (BigInteger n, int shift) Ratio(uint value)
        {
            int exponent = (int)(value >> 23);
            int mantissa = (int)(value & 0x7fffff) | (exponent == 0 ? 0 : 0x800000);
            return (new BigInteger(mantissa), exponent == 0 ? -149 : exponent - 150);
        }
        var left = Ratio(word); var right = Ratio(word + 1);
        int exponent = Math.Min(left.shift, right.shift) - 1;
        BigInteger number = (left.n << (left.shift - exponent - 1)) + (right.n << (right.shift - exponent - 1));
        if (exponent >= 0) return (number << exponent).ToString(CultureInfo.InvariantCulture) + ".0";
        int places = -exponent;
        string digits = (number * BigInteger.Pow(5, places)).ToString(CultureInfo.InvariantCulture).PadLeft(places + 1, '0');
        return digits.Insert(digits.Length - places, ".");
    }
}
