// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>
/// A source's tokens with its <c>#include</c> and <c>#define</c> lines applied. An included file contributes its <c>#define</c> lines only
/// (the game's headers hold nothing else the compiler needs); a name that has been defined is replaced by the tokens of its definition, to
/// a depth of 16 (a definition that names itself stops there). The lines of the source keep their numbers: a directive's line is left
/// empty, and a replaced name keeps the line of its use.
/// </summary>
internal static class ScriptPreprocessor
{
    public static (List<Token> Tokens, string Text) Run(string source, Func<string, string> readInclude, CompileLimits limits)
    {
        Dictionary<string, List<Token>> defines = new(StringComparer.Ordinal);

        void DefineFrom(string text)
        {
            foreach (string raw in text.Split('\n'))
                if (ScriptLexer.DefineOf(raw) is { } define) defines[define.Name] = define.Body;
        }

        List<string> body = [];
        foreach (string raw in source.Split('\n'))
        {
            if (ScriptLexer.IncludeOf(raw) is { } path)
            {
                DefineFrom(readInclude(path));
                body.Add("");  // the line stays, so the lines after it keep their numbers
            }
            else if (ScriptLexer.IsDefine(raw))
            {
                DefineFrom(raw);
                body.Add("");
            }
            else
            {
                body.Add(raw);
            }
        }
        string text = string.Join('\n', body);
        List<Token> output = [];
        long steps = 0;

        void Expand(Token token, Token use, int depth)
        {
            steps++;
            if (steps > limits.MaxExpansionSteps || output.Count >= limits.MaxTokens)
                throw new CompileError($"replacing the #define names makes the script longer than {limits.MaxTokens.ToString("N0", CultureInfo.InvariantCulture)} tokens", use.Line);
            if (token.Kind == TokenKind.Id && depth < 16 && defines.TryGetValue(token.Text, out List<Token>? replacement))
            {
                foreach (Token inner in replacement) Expand(inner, use, depth + 1);
            }
            else
            {
                output.Add(new Token(token.Kind, token.Text, use.Line, use.Start, use.End));
            }
        }

        foreach (Token token in ScriptLexer.Lex(text)) Expand(token, token, 0);
        return (output, text);
    }
}
