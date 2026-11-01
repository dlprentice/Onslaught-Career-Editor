// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Levels;

internal enum WaypointRuleKind { Resolved, MissingPath, EmptyPath, UncheckedExpression, Unavailable }
internal sealed record WaypointRuleFinding(int Line, string Function, string? Target, WaypointRuleKind Kind, string Message);
internal sealed record WaypointRuleReport(IReadOnlyList<WaypointRuleFinding> Findings, int Calls, int UnshownCalls, int SkippedDirectives, bool Available)
{
    internal int Resolved => Findings.Count(item => item.Kind == WaypointRuleKind.Resolved);
    internal int Unresolved => Findings.Count(item => item.Kind is WaypointRuleKind.MissingPath or WaypointRuleKind.EmptyPath);
    internal int Unchecked => Findings.Count(item => item.Kind == WaypointRuleKind.UncheckedExpression);
    internal const string Scope = "Direct literal names in the current source only. Dynamic expressions, includes/macros and runtime behavior are unchecked. Compile and verify the mission separately.";
}

/// <summary>Read-only audit of source-visible waypoint call targets against selected data. It neither compiles nor executes source.</summary>
internal static class WaypointRuleAudit
{
    internal const int MaxFindings = 64, MaxWorldPaths = 4096, MaxPathName = 4096, MaxPathSlots = 65536;

    internal static WaypointRuleReport Check(string source, WorldBody? world, WorldBody? baseWorld = null)
    {
        if (source is null || source.Length > ScriptCompiler.MaxSource)
            return Unavailable("The source is absent or too large for this limited check.");
        if (world is null) return Unavailable("Open a readable world before checking its waypoint rules.");
        try
        {
            CheckWorld(world);
            if (baseWorld is not null) CheckWorld(baseWorld);
            int directives = 0;
            string[] lines = source.Split('\n');
            for (int line = 0; line < lines.Length; line++)
            {
                if (ScriptLexer.IncludeOf(lines[line]) is null && !ScriptLexer.IsDefine(lines[line])) continue;
                lines[line] = ""; directives++;
            }
            List<Token> tokens;
            try { tokens = ScriptLexer.Lex(string.Join('\n', lines)); }
            catch (CompileError error) { return Unavailable("The source could not be tokenized for this limited check. Compile it to inspect syntax errors.", error.Line ?? 0, directives); }
            List<WaypointRuleFinding> findings = [];
            int calls = 0;
            for (int index = 0; index + 1 < tokens.Count; index++)
            {
                Token function = tokens[index];
                if (function.Kind != TokenKind.Id || function.Text is not ("FollowWaypoint" or "FollowWaypointWait") ||
                    tokens[index + 1].Text != "(" || (index > 0 && tokens[index - 1].Text == ".")) continue;
                calls++;
                if (findings.Count == MaxFindings) continue;
                Token? argument = index + 2 < tokens.Count ? tokens[index + 2] : null;
                Token? after = index + 3 < tokens.Count ? tokens[index + 3] : null;
                if (argument?.Kind != TokenKind.Str || after?.Text is not ("," or ")"))
                {
                    findings.Add(new(argument?.Line ?? function.Line, function.Text, null, WaypointRuleKind.UncheckedExpression,
                        "The target is dynamic, indirect or incomplete; it was not checked."));
                    continue;
                }
                string target = argument.Text[1..^1];
                if (target.Length > MaxPathName)
                {
                    findings.Add(new(argument.Line, function.Text, null, WaypointRuleKind.UncheckedExpression, "The literal target is too long for this limited check."));
                    continue;
                }
                NameMatch? match = ScriptNames.Resolve(target, world, [], baseWorld, pathsIgnoreCase: true)
                    .Where(item => item.Kind is NameKind.Path or NameKind.BasePath).Select(item => (NameMatch?)item).FirstOrDefault();
                if (match is null)
                {
                    findings.Add(new(argument.Line, function.Text, target, WaypointRuleKind.MissingPath, "No matching waypoint path in the selected worlds."));
                    continue;
                }
                WorldBody owner = match.Value.Kind == NameKind.BasePath ? baseWorld! : world;
                int points = WaypointCatalog.Rows(owner, owner.WaypointPaths[match.Value.Index]).Count;
                string where = match.Value.Kind == NameKind.BasePath ? "base world" : "level world";
                findings.Add(new(argument.Line, function.Text, target, points == 0 ? WaypointRuleKind.EmptyPath : WaypointRuleKind.Resolved,
                    points == 0 ? $"The matched {where} path has no waypoint rows in the selected data."
                        : $"Matched {where} path with {points} waypoint rows in the selected data."));
            }
            return new(Array.AsReadOnly(findings.ToArray()), calls, Math.Max(0, calls - findings.Count), directives, true);
        }
        catch (Exception error) when (EditSession.IsUnstorable(error))
        {
            return Unavailable("The selected world data is unavailable, malformed or too large for this limited check.");
        }
    }

    private static void CheckWorld(WorldBody world)
    {
        if (world is null || world.Things.Count > WorldBody.MaxThings || world.WaypointPaths.Count > MaxWorldPaths)
            throw new InvalidDataException("World is outside the audit bounds.");
        long names = 0, slots = 0;
        foreach (PlacedObject thing in world.Things)
        {
            if (thing?.Init?.Name is not { } name || name.Length > MaxPathName) throw new InvalidDataException("Invalid object name.");
            names += name.Length;
        }
        foreach (WaypointPath path in world.WaypointPaths)
        {
            if (path?.Name is not { } name || name.Length > MaxPathName || path.Slots.Count > MaxPathSlots)
                throw new InvalidDataException("Invalid path.");
            names += name.Length; slots += path.Slots.Count;
        }
        if (names > ScriptCompiler.MaxSource || slots > ScriptCompiler.MaxSource) throw new InvalidDataException("World is outside the audit bounds.");
    }

    private static WaypointRuleReport Unavailable(string message, int line = 0, int directives = 0) =>
        new(Array.AsReadOnly(new[] { new WaypointRuleFinding(line, "", null, WaypointRuleKind.Unavailable, message) }), 0, 0, directives, false);
}
