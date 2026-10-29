// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>A game function a script calls, and how many CALL instructions of its code call it.</summary>
public readonly record struct NativeCall(string Name, int Count);

/// <summary>An object that names a script: its row in the object table and the field that names it (see <see cref="ScriptCatalog"/>).</summary>
public readonly record struct ScriptUse(int Row, string Role);

/// <summary>What a compiled script shows without being run: its name, the events it handles, the game functions it calls, and the objects that name it.</summary>
public sealed record ScriptSummary(string Name, IReadOnlyList<string> Events, IReadOnlyList<NativeCall> Calls, int Instructions, IReadOnlyList<ScriptUse> Uses);

/// <summary>An object's reference to a script, and whether the world has a script of that name.</summary>
public readonly record struct ScriptReference(string Role, string Name, bool Resolved);

/// <summary>
/// The compiled scripts of a world body, read for display. Nothing here changes a body. The game runs scripts, not their sources: what
/// follows is read from the compiled code (the 13 fixed events' entry points, the named handlers' event names, the natives each CALL
/// instruction indexes) and from the objects that name a script. An object names a script in up to three places: the script it runs,
/// the script it gives the things it spawns, and (a spawner) the spawn script it gives its unit.
/// </summary>
public static class ScriptCatalog
{
    /// <summary>The object's own script, the spawn script, and a spawner's spawn script.</summary>
    public const string RoleScript = "script", RoleSpawnScript = "spawn script", RoleSpawnerScript = "spawner's spawn script";

    private const int OpCall = 24;

    /// <summary>One summary per compiled script, in the body's order; each names the rows of the objects that name it (exact name).</summary>
    public static IReadOnlyList<ScriptSummary> Of(WorldBody body)
    {
        Dictionary<string, List<ScriptUse>> uses = new(StringComparer.Ordinal);
        for (int row = 0; row < body.Things.Count; row++)
            foreach ((string role, string name) in References(body.Things[row]))
            {
                if (!uses.TryGetValue(name, out List<ScriptUse>? list)) uses[name] = list = [];
                list.Add(new ScriptUse(row, role));
            }
        return [.. body.Scripts.Select(script => new ScriptSummary(script.Name, Events(script.Code), Calls(script.Code), script.Code.Instructions.Count,
            uses.TryGetValue(script.Name, out List<ScriptUse>? mine) ? mine : []))];
    }

    /// <summary>The scripts an object names, each with whether this body has a script of that name.</summary>
    public static IReadOnlyList<ScriptReference> ReferencesOf(WorldBody body, int row)
    {
        if (row < 0 || row >= body.Things.Count) return [];
        HashSet<string> names = [.. body.Scripts.Select(script => script.Name)];
        return [.. References(body.Things[row]).Select(reference => new ScriptReference(reference.Role, reference.Name, names.Contains(reference.Name)))];
    }

    private static IEnumerable<(string Role, string Name)> References(PlacedObject thing)
    {
        if (thing.Init.Script.Length > 0) yield return (RoleScript, thing.Init.Script);
        if (thing.Init.SpawnScript.Length > 0) yield return (RoleSpawnScript, thing.Init.SpawnScript);
        if (thing.Init.Spawner?.SpawnerSpawnScript is { Length: > 0 } spawner) yield return (RoleSpawnerScript, spawner);
    }

    /// <summary>The events a script handles: each fixed event it has an entry point for, then each named handler as <c>event "name"</c>.</summary>
    internal static IReadOnlyList<string> Events(ScriptCode code)
    {
        List<string> events = [];
        for (int index = 0; index < code.EventPcs.Length && index < ScriptTables.EventNames.Length; index++)
            if (code.EventPcs[index] >= 0) events.Add(ScriptTables.EventNames[index]);
        for (int handler = 0; handler < code.EventFunctions.Count; handler++)
        {
            List<int> parameters = code.EventFunctions[handler].Parameters;
            string? name = parameters.Count > 0 && parameters[0] >= 0 && parameters[0] < code.Symbols.Count && code.Symbols[parameters[0]].Value is ScriptText text
                ? text.Value : null;
            events.Add(name is null ? $"event #{handler + 1}" : $"event \"{name}\"");
        }
        return events;
    }

    /// <summary>The game functions a script calls, in the order its code first calls them.</summary>
    internal static IReadOnlyList<NativeCall> Calls(ScriptCode code)
    {
        List<string> order = [];
        Dictionary<string, int> counts = [];
        foreach (ScriptInstruction instruction in code.Instructions)
        {
            if (instruction.Opcode != OpCall) continue;
            int index = instruction.Attribute & 0xFF;
            string name = index < ScriptTables.Natives.Length ? ScriptTables.Natives[index].Name : $"function {index}";
            if (!counts.TryGetValue(name, out int before)) order.Add(name);
            counts[name] = before + 1;
        }
        return [.. order.Select(name => new NativeCall(name, counts[name]))];
    }
}
