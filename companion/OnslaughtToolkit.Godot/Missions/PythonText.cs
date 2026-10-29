// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.Text;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>
/// Text as the Toolkit's Python reference compiler writes it into its messages: <c>repr</c> of a string (single quotes unless the text holds
/// one and no double quote; backslash, the quote, line ends and tabs escaped; other control and non-printable characters as \x or \u
/// escapes). The C# compiler's messages are held to the reference's word for word, so a quoted token reads the same in both.
/// </summary>
internal static class PythonText
{
    public static string Repr(string text)
    {
        char quote = text.Contains('\'') && !text.Contains('"') ? '"' : '\'';
        StringBuilder builder = new();
        builder.Append(quote);
        foreach (char c in text) AppendChar(builder, c, quote);
        builder.Append(quote);
        return builder.ToString();
    }

    public static string Repr(char c) => Repr(c.ToString());

    private static void AppendChar(StringBuilder builder, char c, char quote)
    {
        if (c == quote || c == '\\') builder.Append('\\').Append(c);
        else if (c == '\n') builder.Append("\\n");
        else if (c == '\r') builder.Append("\\r");
        else if (c == '\t') builder.Append("\\t");
        else if (c < ' ' || c == '\u007f') builder.Append("\\x").Append(((int)c).ToString("x2", CultureInfo.InvariantCulture));
        else if (c < '\u007f' || IsPrintable(c)) builder.Append(c);
        else if (c <= '\u00ff') builder.Append("\\x").Append(((int)c).ToString("x2", CultureInfo.InvariantCulture));
        else builder.Append("\\u").Append(((int)c).ToString("x4", CultureInfo.InvariantCulture));
    }

    /// <summary>Python's <c>str.isprintable</c> for one character: not "Other" or "Separator" in the Unicode database, except the ASCII space.</summary>
    private static bool IsPrintable(char c) => char.IsHighSurrogate(c) || char.IsLowSurrogate(c) ||
        CharUnicodeInfo.GetUnicodeCategory(c) is not (UnicodeCategory.Control or UnicodeCategory.Format or UnicodeCategory.PrivateUse or
            UnicodeCategory.OtherNotAssigned or UnicodeCategory.LineSeparator or UnicodeCategory.ParagraphSeparator or UnicodeCategory.SpaceSeparator);
}
