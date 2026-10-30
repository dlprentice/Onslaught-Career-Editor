// SPDX-License-Identifier: GPL-3.0-only
using System.Text.RegularExpressions;

namespace OnslaughtToolkit.Companion.Missions;

internal enum TokenKind { Id, Int, Float, Str, Op }

/// <summary>One token: its text, the 0-based line it is on (counting <c>\n</c>) and its span in the text it was read from (a name from an <c>#include</c> or <c>#define</c> keeps the span of its use).</summary>
internal sealed record Token(TokenKind Kind, string Text, int Line, int Start, int End);

/// <summary>
/// The mission script language's tokens, as tools/msl_compile.py reads them: blanks (space, tab, CR, FF, VT) and <c>//</c> comments are
/// dropped, a line ends at <c>\n</c> only, a number is digits with an optional point and an optional <c>f</c>, a word is ASCII letters,
/// digits and underscores, a string is closed on its own line, and the operators are <c>== != &lt;= &gt;= &amp;&amp; ||</c> and
/// <c>- + * / &lt; &gt; = ! ( ) { } ; , . :</c>.
/// </summary>
internal static class ScriptLexer
{
    public static List<Token> Lex(string text)
    {
        List<Token> tokens = [];
        int line = 0, at = 0;
        while (at < text.Length)
        {
            char c = text[at];
            if (c is ' ' or '\t' or '\r' or '\f' or '\v')
            {
                while (at < text.Length && text[at] is ' ' or '\t' or '\r' or '\f' or '\v') at++;
                continue;
            }
            if (c == '\n')
            {
                line++;
                at++;
                continue;
            }
            if (c == '/' && at + 1 < text.Length && text[at + 1] == '/')
            {
                while (at < text.Length && text[at] != '\n') at++;
                continue;
            }
            int end;
            TokenKind kind;
            if (IsDigit(c) || (c == '.' && at + 1 < text.Length && IsDigit(text[at + 1])))
            {
                end = at;
                while (end < text.Length && IsDigit(text[end])) end++;
                if (end < text.Length && text[end] == '.')
                {
                    end++;
                    while (end < text.Length && IsDigit(text[end])) end++;
                    if (end < text.Length && text[end] == 'f') end++;
                    kind = TokenKind.Float;
                }
                else
                {
                    kind = TokenKind.Int;
                }
            }
            else if (IsWordStart(c))
            {
                end = at + 1;
                while (end < text.Length && (IsWordStart(text[end]) || IsDigit(text[end]))) end++;
                kind = TokenKind.Id;
            }
            else if (c == '"' && ClosingQuote(text, at) is int close)
            {
                end = close + 1;
                kind = TokenKind.Str;
            }
            else if (OperatorAt(text, at) is int length)
            {
                if (c == '/' && at + 1 < text.Length && text[at + 1] == '*') throw new CompileError("this language has no /* */ comments; use //", line);
                end = at + length;
                kind = TokenKind.Op;
            }
            else
            {
                throw new CompileError(c == '"' ? "a string must end on the line it starts" : $"unexpected character {PythonText.Repr(PythonText.CharacterAt(text, at))}", line);
            }
            tokens.Add(new Token(kind, text[at..end], line, at, end));
            at = end;
        }
        return tokens;
    }

    private static bool IsDigit(char c) => c is >= '0' and <= '9';

    private static bool IsWordStart(char c) => c is (>= 'A' and <= 'Z') or (>= 'a' and <= 'z') or '_';

    /// <summary>The index of the quote that closes the string opened at <paramref name="open"/> on the same line, or null.</summary>
    private static int? ClosingQuote(string text, int open)
    {
        for (int i = open + 1; i < text.Length; i++)
        {
            if (text[i] == '"') return i;
            if (text[i] == '\n') return null;
        }
        return null;
    }

    /// <summary>The length (1 or 2) of the operator at <paramref name="at"/>, or null.</summary>
    private static int? OperatorAt(string text, int at)
    {
        if (at + 1 < text.Length)
        {
            string two = text.Substring(at, 2);
            if (two is "==" or "!=" or "<=" or ">=" or "&&" or "||") return 2;
        }
        return "-+*/<>=!(){};,.:".Contains(text[at]) ? 1 : null;
    }

    private static readonly Regex DefineLine = new($"^{Blank}*#{Blank}*define{Blank}+([A-Za-z_][A-Za-z_0-9]*)(.*)$", RegexOptions.CultureInvariant);
    private static readonly Regex IncludeLine = new($"^{Blank}*#{Blank}*include{Blank}+([^ \\t\\r\\f\\v]+)", RegexOptions.CultureInvariant);
    private static readonly Regex DefineWord = new($"^{Blank}*#{Blank}*define(?![A-Za-z0-9_])", RegexOptions.CultureInvariant);
    private static readonly Regex LineComment = new("//.*", RegexOptions.CultureInvariant);

    private const string Blank = "[ \\t\\r\\f\\v]";

    /// <summary>The name and the tokens of a <c>#define NAME tokens</c> line, or null if the line is not one.</summary>
    public static (string Name, List<Token> Body)? DefineOf(string line)
    {
        Match match = DefineLine.Match(line);
        return match.Success ? (match.Groups[1].Value, Lex(LineComment.Replace(match.Groups[2].Value, ""))) : null;
    }

    /// <summary>The path an <c>#include</c> line names, or null if the line is not one.</summary>
    public static string? IncludeOf(string line)
    {
        Match match = IncludeLine.Match(line);
        return match.Success ? match.Groups[1].Value : null;
    }

    /// <summary>Whether the line starts a <c>#define</c> (whether or not it is a well-formed one).</summary>
    public static bool IsDefine(string line) => DefineWord.IsMatch(line);
}
