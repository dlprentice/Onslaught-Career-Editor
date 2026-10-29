// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.Text;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>
/// Text as the Toolkit's Python reference compiler writes it into its messages: <c>repr</c> of a string (single quotes unless the text holds
/// one and no double quote; backslash, the quote, line ends and tabs escaped; other control and non-printable characters as \x, \u or \U
/// escapes). The C# compiler's messages are held to the reference's word for word, so a quoted token reads the same in both. Python counts
/// characters as code points and C# strings are UTF-16, so everything here goes by code point: a valid surrogate pair is one character, and
/// a surrogate on its own is a character of its own (Python writes it as \udXXX; no printable character is a lone surrogate). The one thing a
/// C# string cannot say is a lone high surrogate followed by a lone low one: that is a pair, as it is for every UTF-16 text.
/// </summary>
internal static class PythonText
{
    public static string Repr(string text)
    {
        char quote = text.Contains('\'') && !text.Contains('"') ? '"' : '\'';
        StringBuilder builder = new();
        builder.Append(quote);
        for (int at = 0; at < text.Length; at++)
        {
            int code = text[at];
            if (char.IsHighSurrogate(text[at]) && at + 1 < text.Length && char.IsLowSurrogate(text[at + 1])) code = char.ConvertToUtf32(text[at], text[++at]);
            AppendCharacter(builder, code, quote);
        }
        builder.Append(quote);
        return builder.ToString();
    }

    /// <summary>The character at index <paramref name="at"/> as a string: both halves of a surrogate pair, or the one unit of anything else (a lone surrogate included).</summary>
    public static string CharacterAt(string text, int at) =>
        char.IsHighSurrogate(text[at]) && at + 1 < text.Length && char.IsLowSurrogate(text[at + 1]) ? text.Substring(at, 2) : text[at].ToString();

    /// <summary>The number of characters, counting a surrogate pair as one (what Python's <c>len</c> says of the same text).</summary>
    public static int CharacterCount(string text) => CharacterCount(text.AsSpan());

    /// <summary>The same count for a slice without copying it.</summary>
    public static int CharacterCount(ReadOnlySpan<char> text)
    {
        int count = text.Length;
        for (int at = 0; at + 1 < text.Length; at++)
        {
            if (!char.IsHighSurrogate(text[at]) || !char.IsLowSurrogate(text[at + 1])) continue;
            count--;
            at++;
        }
        return count;
    }

    private static void AppendCharacter(StringBuilder builder, int code, char quote)
    {
        if (code == quote || code == '\\') builder.Append('\\').Append((char)code);
        else if (code == '\n') builder.Append("\\n");
        else if (code == '\r') builder.Append("\\r");
        else if (code == '\t') builder.Append("\\t");
        else if (code < ' ' || code == 0x7f) builder.Append("\\x").Append(code.ToString("x2", CultureInfo.InvariantCulture));
        else if (code < 0x7f || IsPrintable(code)) builder.Append(char.ConvertFromUtf32(code));
        else if (code <= 0xff) builder.Append("\\x").Append(code.ToString("x2", CultureInfo.InvariantCulture));
        else if (code <= 0xffff) builder.Append("\\u").Append(code.ToString("x4", CultureInfo.InvariantCulture));
        else builder.Append("\\U").Append(code.ToString("x8", CultureInfo.InvariantCulture));
    }

    /// <summary>
    /// Python's <c>str.isprintable</c> for one character: not "Other" (control, format, surrogate, private use, unassigned) or "Separator" in the
    /// Unicode database, except the ASCII space. The two databases may be of different versions, so a character assigned after the older one
    /// was made can differ; the tests compare the whole range on the machine that generates the vectors.
    /// </summary>
    private static bool IsPrintable(int code) =>
        CharUnicodeInfo.GetUnicodeCategory(code) is not (UnicodeCategory.Control or UnicodeCategory.Format or UnicodeCategory.Surrogate or UnicodeCategory.PrivateUse or
            UnicodeCategory.OtherNotAssigned or UnicodeCategory.LineSeparator or UnicodeCategory.ParagraphSeparator or UnicodeCategory.SpaceSeparator);
}
