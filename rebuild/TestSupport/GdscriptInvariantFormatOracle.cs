// SPDX-License-Identifier: GPL-3.0-or-later
using System.Globalization;

// Synthetic filename/number patterns only. The expected strings come from the
// runtime used by the existing startup media reader, never a copied formatter.
internal static class GdscriptInvariantFormatOracle
{
    private const int MaximumTextUnits = 65536;

    internal static object Build()
    {
        var cases = new List<object>();
        var rawCases = new List<object>();
        void Add(string name, string? template, int argument)
        {
            try
            {
                string formatted = string.Format(CultureInfo.InvariantCulture, template!, argument);
                bool unsupported = template!.Length > MaximumTextUnits || formatted.Length > MaximumTextUnits;
                cases.Add(new { name, template, argument, ok = true, unsupported,
                    formattedUtf16Length = formatted.Length, value = unsupported ? null : formatted,
                    error_type = (string?)null });
            }
            catch (FormatException)
            {
                cases.Add(new { name, template, argument, ok = false, unsupported = false,
                    formattedUtf16Length = 0, value = (string?)null, error_type = "FormatException" });
            }
            catch (ArgumentException)
            {
                cases.Add(new { name, template, argument, ok = false, unsupported = false,
                    formattedUtf16Length = 0, value = (string?)null, error_type = "ArgumentException" });
            }
        }
        void AddRaw(string name, string template, int argument)
        {
            int[] templateUnits = template.Select(unit => (int)unit).ToArray();
            try
            {
                string formatted = string.Format(CultureInfo.InvariantCulture, template, argument);
                bool unsupported = template.Length > MaximumTextUnits || formatted.Length > MaximumTextUnits;
                rawCases.Add(new { name, templateUnits, argument, ok = true, unsupported,
                    formattedUtf16Length = formatted.Length,
                    valueUnits = unsupported ? null : formatted.Select(unit => (int)unit).ToArray(),
                    error_type = (string?)null });
            }
            catch (FormatException)
            {
                rawCases.Add(new { name, templateUnits, argument, ok = false, unsupported = false,
                    formattedUtf16Length = 0, valueUnits = (int[]?)null, error_type = "FormatException" });
            }
        }

        int[] values = [int.MinValue, -1234567890, -999999, -99995, -12500, -2500, -1500, -500,
            -99, -25, -15, -1, 0, 1, 2, 9, 10, 15, 25, 49, 50, 99, 499, 500, 999, 1000, 1499,
            1500, 2500, 9999, 99995, 100000, 1234567890, int.MaxValue];
        string[] standard = ["", "D", "d0", "D1", "D5", "D12", "D00005", "X", "x0", "X4", "x12",
            "B", "b0", "B8", "b40", "C", "c0", "C3", "F", "f0", "F4", "N", "n0", "N3",
            "P", "p0", "P3", "E", "e0", "E1", "e2", "E12", "G", "g0", "G1", "g2", "G3",
            "g9", "G12", "R", "r0", "R1", "r3", "G999999999", "R999999999", "Q", "q2", "Z0"];
        foreach (string format in standard)
            foreach (int value in values)
                Add($"standard {format} / {value}", "frame_{0:" + format + "}.png", value);

        string[] custom = ["0", "00", "00000", "#", "##", "##0#", "#000#", "0.00", "#.##",
            ".00", ".##", "0.##", "#.#0", "0..00", "0.0.0", "0#.#0", "00.000##",
            "#,##0", "0,0", "000,000", "#,##0.00", "0,", "0,,", "0,,.000", "0,,.###", "0,.0",
            "#,##0,,", "0,,0", ",0", "0.,", "0, 'K'", "0%", "0.0%", "0%%", "0‰", "0%‰",
            "0.00E+00", "0.0e-00", "0E0", "00.0E+000", "#E+0", ".0E+0", "0E+000000000000",
            "0E+0E+0", "0E0e0", "0E+", "0E-", "0e#", "0e+##", "E+0", "e00", "E#0",
            "0;[0];zero", "0;negative;zero", "0;;zero", "0;", ";0", ";;zero", "0;;", ";", ";;",
            "0;0;0;ignored", "0,;[0,];'ZERO'", "0,,.00;[0,,.00];'ZERO'", "'#'0'%'", "\"unit \"000",
            "0\\;0;[0];'ZERO'", "0'\\'", "0\\", "'unclosed", "\"unclosed", "0'quoted;semi'", "0\\0",
            "0\\#", "literal", "D-1", "D 5", "G1x", "00 Ω", "'🚀'0", "0'🚀'", "0'±'", "0'𐐀'",
            "0 # 0", "0/0", "0:0", "0+0", "#' units'", "'zero'", "'0;neg;zero'", "\\;0"];
        foreach (string format in custom)
            foreach (int value in values)
                Add($"custom {format} / {value}", "{0:" + format + "}", value);

        string[] composites = ["", "static.png", "f{0:D5}.png", "logo/f{0:D5}.png", "{0}", "{00}", "{0000}",
            "{0:}", "{{0}}", "{{{0:D5}}}", "{{{{{0:D2}}}}}", "a}}b{{c", "{0}/{0:D5}/{0:X8}",
            "[{0,12:D5}]", "[{0,-12:D5}]", "[{0,0}]", "[{0,-0}]", "[{0, 12 :D5}]", "[{0 , -12 :D5}]",
            "{0   }", "{0 :D5}", "{0: D5}", "[{0,8:'🚀'0}]", "[{0,-8:'🚀'0}]", "{0:0'}}'}",
            "{", "}", "{0", "{0:0", "{0}}", "{{{", "}{", "{1}", "{01:D5}", "{-0}", "{+0}",
            "{ 0}", "{0,}", "{0,-}", "{0,+5}", "{0, - 5}", "{0,1.0}", "{0,,1}", "{0;D5}",
            "{0\t}", "{0,\t5}", "{0,5\t}", "{0,5,}", "{0:D{5}", "{0:'{'}", "{0:{{0}}}",
            "{0:'}'}", "{0000000000000000000000000000000000000000001}", "{10000000}",
            "{0,10000000}", "{0:D1000000000}", "{0:D1000000000x}", "{0:D0000000000000000000005}"];
        foreach (string format in composites)
            foreach (int value in new[] { int.MinValue, -25, 0, 1, 25, int.MaxValue })
                Add($"composite {format} / {value}", format, value);
        Add("null template", null, 1);
        Add("output at bound", "{0:D65536}", 1);
        Add("output above bound", "{0:D65537}", 1);
        Add("alignment above bound", "{0,65537}", 1);
        Add("precision plus punctuation above bound", "{0:F65536}", 1);
        Add("template above bound", new string('x', MaximumTextUnits + 1), 1);
        Add("UTF16 alignment includes supplementary pair", "[{0,8:'🚀🚀'0}]", 1);
        string[] rawTemplates = ["prefix\0f{0:D5}.png\0suffix", "\0", "x\0y", "{{\0}}", "{0:D5\0ignored}",
            "{0:\0E7}", "{0:0'hello\0ignored'}", "before{0:'a\0b'000}after", "before{0:0\\\0ignored}after",
            "{0:0;neg;zero\0ignored}", "{0:0;\0neg;zero}", "{0:0;;\0zero}", "{0:0,\0ignored}",
            "{0:D5\0ignored{brace}}", "{\00}", "{0\0}", "{0,\05}", "{0,5\0}", "{0:Q\0}",
            "\uD800{0}x\uDC00", "{0:'\uD800'000}", "{0:'\uDC00\uD800'0}", "{0:'\uD83D\uDE80'0}",
            "[{0,8:'\uD800'0}]", "[{0,-8:'\uDC00'0}]", "{0:'\U000F0000\uD800'0}",
            "{0:'\uD800\U000F0000\U000F0001\uDC00'0}", "{0:\\\uD8000}", "{0:'\uD800'0;'\uDC00'0;'\uD801'}"];
        for (int index = 0; index < rawTemplates.Length; index++)
            foreach (int value in new[] { int.MinValue, -25, 0, 1, 25, int.MaxValue })
                AddRaw($"raw template {index} / {value}", rawTemplates[index], value);
        foreach (string specifier in new[] { "B", "C", "D", "E", "F", "G", "N", "P", "R", "X", "e2", "D0005" })
            foreach (int value in new[] { -25, 0, 1, int.MaxValue })
                AddRaw($"NUL standard {specifier} / {value}", "{0:" + specifier + "\0ignored}", value);
        AddRaw("raw NUL text at bound", new string('\0', MaximumTextUnits), 1);
        AddRaw("raw NUL text above bound", new string('\0', MaximumTextUnits + 1), 1);
        AddRaw("surrogate numeric carrier near bound", "{0:'" + new string('\uD800', MaximumTextUnits - 6) + "'}", 1);
        AddRaw("surrogate numeric carrier at maximum negative output", "{0:'" + new string('\uD800', MaximumTextUnits - 6) + "'}", -1);
        return new { cases, rawCases };
    }
}
