// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.GodotClient;

// Temporary differential oracle. Raw UTF-16 transport preserves every C# char;
// JsonSerializer's replacement of malformed strings cannot hide differences.
internal static class GdscriptMessagePanelOracle
{
    public static object Build()
    {
        int[]? Units(string? text) => text?.Select(c => (int)c).ToArray();
        object Result(Func<object?> action)
        {
            try { return new { ok = true, value = action() }; }
            catch (Exception error) { return new { ok = false, error_type = error.GetType().Name,
                parameter = (error as ArgumentException)?.ParamName ?? string.Empty }; }
        }
        object[] Lines(IReadOnlyList<Level100MessageLine> lines) => lines.Select(line =>
            (object)new { text = Units(line.Text), source_length = line.SourceLength }).ToArray();
        var wrapped = new List<object>();
        void WrapCase(string name, string text, bool exhaustive = false)
        {
            IReadOnlyList<Level100MessageLine> lines = Level100MessagePanel.Wrap(text);
            int length = Level100MessagePanel.SourceLength(lines);
            var cursors = new SortedSet<int> { int.MinValue, -1, 0, 1, 24, 25, 26,
                Math.Max(0, length - 1), length, length + 1, int.MaxValue };
            int consumed = 0;
            foreach (Level100MessageLine line in lines)
            {
                consumed += line.SourceLength;
                cursors.Add(consumed - 1); cursors.Add(consumed); cursors.Add(consumed + 1);
            }
            if (exhaustive) foreach (int cursor in Enumerable.Range(0, text.Length + 3)) cursors.Add(cursor);
            wrapped.Add(new { name, text = Units(text), lines = Lines(lines), source_length = length,
                windows = cursors.Select(cursor => new { cursor, result = Result(() =>
                    Level100MessagePanel.Window(lines, cursor).Select(Units).ToArray()) }).ToArray() });
        }
        string[] explicitTexts = ["", " ", "\t  \t", "a", "  a", "a  b", "  a b",
            "a\rb\r\nc\n\nd\n", "\r\n", "\n\n", "\na\n", "a    ",
            "  a bbbbbbbbbbbbbbbbbbbbbbbbbbb c  d   ",
            "A short synthetic sentence becomes several scrolling lines in this panel.",
            "Words  can contain  two spaces before they wrap at twenty five columns.",
            "\0suffix", "prefix\0suffix", "\ud800", "\udc00", "\ud800\ud800\udc00",
            new string('a', 24) + "\ud83d\ude80suffix", new string('a', 25) + " tail",
            new string('a', 51), "  " + new string('b', 51) + "   "];
        for (int index = 0; index < explicitTexts.Length; index++) WrapCase($"explicit-{index}", explicitTexts[index], true);
        foreach (int unit in new[] { 8, 9, 10, 11, 12, 13, 14, 31, 32, 33, 0x84, 0x85, 0x86, 0xa0,
            0x1680, 0x180e, 0x2000, 0x2001, 0x2002, 0x2003, 0x2004, 0x2005, 0x2006, 0x2007,
            0x2008, 0x2009, 0x200a, 0x200b, 0x2028, 0x2029, 0x202f, 0x205f, 0x2060, 0x3000, 0xfeff })
            WrapCase($"separator-{unit:x4}", new string((char)unit, 2) + "first " + new string('a', 19) +
                (char)unit + "second" + (char)unit, true);
        uint random = 0x4d534750;
        uint Next() => random = unchecked(random * 1664525u + 1013904223u);
        char[] alphabet = ['a', 'b', 'c', ' ', ' ', '\t', '\n', '\r', '\0', '\ud800', '\udc00', '\u00a0', '\u2003', 'é'];
        for (int index = 0; index < 256; index++)
        {
            char[] chars = new char[Next() % 321];
            for (int pos = 0; pos < chars.Length; pos++) chars[pos] = alphabet[Next() % alphabet.Length];
            WrapCase($"generated-{index}", new string(chars));
        }
        var reveal = new List<object>();
        void Reveal(double seconds) => reveal.Add(new {
            bits = Convert.ToHexString(BitConverter.GetBytes(seconds)).ToLowerInvariant(),
            expected = Level100MessagePanel.RevealedCharacters(seconds) });
        foreach (double value in new[] { double.NaN, double.PositiveInfinity, double.NegativeInfinity,
            -0.0, 0.0, double.Epsilon, -double.Epsilon, double.MaxValue, -double.MaxValue,
            int.MaxValue / 40.0, Math.BitDecrement(int.MaxValue / 40.0), Math.BitIncrement(int.MaxValue / 40.0) }) Reveal(value);
        for (int index = 0; index < 256; index++)
        {
            double boundary = index / 40.0;
            Reveal(Math.BitDecrement(boundary)); Reveal(boundary); Reveal(Math.BitIncrement(boundary));
            Reveal(BitConverter.Int64BitsToDouble(unchecked((long)(((ulong)Next() << 32) | Next()))));
        }
        var supplied = new List<object>();
        void Supplied(string name, Level100MessageLine[]? lines)
        {
            supplied.Add(new { name, lines = lines is null ? null : Lines(lines),
                length = Result(() => Level100MessagePanel.SourceLength(lines!)),
                windows = new[] { int.MinValue, -1, 0, 1, 24, 25, 26, int.MaxValue }.Select(cursor => new {
                    cursor, result = Result(() => Level100MessagePanel.Window(lines!, cursor).Select(Units).ToArray()) }).ToArray() });
        }
        Supplied("null-list", null); Supplied("empty-list", []);
        Supplied("null-last-text", [new("a", 1), new(null!, 2)]);
        Supplied("null-skipped-text", [new(null!, 0), new("b", 1)]);
        Supplied("negative-source-length", [new("first", -30), new("second", 1), new("last", 0)]);
        Supplied("overflow-source-length", [new("first", int.MaxValue), new("second", int.MaxValue), new("last", 4)]);
        Supplied("overflow-reveal-subtraction", [new("a", int.MinValue), new("b", 3)]);
        return new {
            constants = new { wrap_columns = Level100MessagePanel.WrapColumns, visible_lines = Level100MessagePanel.VisibleLines,
                line_height_pixels = Level100MessagePanel.LineHeightPixels, text_pen_left = Level100MessagePanel.TextPenLeft,
                first_line_pen_top = Level100MessagePanel.FirstLinePenTop, characters_per_second = Level100MessagePanel.CharactersPerSecond,
                panel_body_left = Level100MessagePanel.PanelBodyLeft, panel_body_top = Level100MessagePanel.PanelBodyTop,
                panel_body_right = Level100MessagePanel.PanelBodyRight, panel_body_bottom = Level100MessagePanel.PanelBodyBottom },
            wrapped, reveal, supplied, null_wrap = Result(() => Level100MessagePanel.Wrap(null!)) };
    }
}
