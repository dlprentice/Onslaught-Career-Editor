// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Replaces one compiled script of a world body with another of the same name. The name stays because it is how the things that run the script
/// (and the other scripts that post to it) find it: renaming is a different edit, which this editor does not make. One instance is one replacement:
/// it remembers the script it put aside, so it cannot be made twice without being taken back between.
/// </summary>
public sealed class ReplaceScript(int scriptIndex, MissionScript script) : IEditCommand
{
    private MissionScript? _previous;
    private string _description = $"Replace script {scriptIndex}";

    public int ScriptIndex => scriptIndex;
    public MissionScript Script => script;
    public string Description => _description;

    public void Do(WorldBody body)
    {
        if (_previous is not null) throw new InvalidOperationException("This replacement has already been made. Take it back first, or make a new one.");
        if (scriptIndex < 0 || scriptIndex >= body.Scripts.Count)
            throw new InvalidOperationException($"There is no script {scriptIndex}: this world has {body.Scripts.Count}.");
        MissionScript old = body.Scripts[scriptIndex];
        if (!string.Equals(old.Name, script.Name, StringComparison.Ordinal))
            throw new InvalidOperationException($"The script {old.Name} cannot be replaced by one named {script.Name}: a script keeps its name, which is how the things that run it find it.");
        _previous = old;
        body.Scripts[scriptIndex] = script;
        _description = $"Replace script {old.Name}";
    }

    public void Undo(WorldBody body)
    {
        if (_previous is null) throw new InvalidOperationException("This replacement has not been made, so there is nothing to take back.");
        body.Scripts[scriptIndex] = _previous;
        _previous = null;
    }
}

/// <summary>One entry of a script's symbol table that differs from the baseline's, as the player would read it.</summary>
/// <param name="Index">The symbol's place in the script's symbol table.</param>
/// <param name="From">The baseline's symbol: its name and value ("(none)" when the baseline has no symbol there).</param>
/// <param name="To">The working script's symbol, in the same form ("(none)" when it has no symbol there).</param>
public sealed record SymbolChange(int Index, string From, string To);

/// <summary>One script whose record differs from the baseline's, with what differs said in numbers and values.</summary>
public sealed record ScriptChange(int Index, string Name, int InstructionsFrom, int InstructionsTo, int SymbolsFrom, int SymbolsTo, IReadOnlyList<SymbolChange> Symbols)
{
    /// <summary>True when the instructions differ in more than their number (an instruction's opcode or operand is not the baseline's).</summary>
    public bool CodeDiffers { get; init; }

    /// <summary>What differs, in a few words for the player: "1 symbol differs", "27 to 29 instructions", "its code differs, 2 symbols differ".</summary>
    public string Describe()
    {
        List<string> parts = [];
        if (CodeDiffers) parts.Add(InstructionsFrom == InstructionsTo ? "its code differs" : $"{InstructionsFrom} to {InstructionsTo} instructions");
        if (Symbols.Count > 0) parts.Add(Symbols.Count == 1 ? "1 symbol differs" : $"{Symbols.Count} symbols differ");
        return parts.Count == 0 ? "its record differs" : string.Join(", ", parts);
    }
}

/// <summary>
/// The script machine of the game is entered once and is not built to be entered twice: a script that kills a unit which runs a script of its own, from inside a
/// handler that is running, starts the dying unit's handler at once, which overwrites the running script's code and place and crashes the level
/// (<c>CVM::CallEvent</c> sets them before <c>CVM::Run</c> refuses to run again; <c>IScript::Arrived</c> and <c>IScript::Hit</c> guard against it, the other entry points do
/// not). No shipped script does it, an edited one can. These are the natives that kill: an edit that adds calls to them is warned about.
/// </summary>
internal static class ScriptHazards
{
    internal static readonly string[] Killers = ["Damage", "Die"];

    private const int OpCall = 24;

    /// <summary>The warnings for a script an edit made: for each killing native it calls more often than the shipped script does, one sentence.</summary>
    internal static IReadOnlyList<string> Warnings(MissionScript shipped, MissionScript edited) =>
    [
        .. Killers.Where(native => Calls(edited, native) > Calls(shipped, native)).Select(native =>
            $"This script calls {native} more often than the shipped one does. In the game as it is, a script that kills a unit which runs a script of its own, from inside a handler that is running, can crash the level: the unit's script starts at once and the game's script machine cannot be entered twice."),
    ];

    /// <summary>How many times a script's code calls the native of this name.</summary>
    internal static int Calls(MissionScript script, string native)
    {
        int index = Array.FindIndex(ScriptTables.Natives, entry => entry.Name == native);
        return index < 0 ? 0 : script.Code.Instructions.Count(instruction => instruction.Opcode == OpCall && (instruction.Attribute & 0xFF) == index);
    }
}

internal static class ScriptDiff
{
    /// <summary>What differs between a script as the baseline has it and as it is now, or null when the two are the same record (bit for bit).</summary>
    internal static ScriptChange? Between(int index, MissionScript from, MissionScript to)
    {
        if (WorldBodyWriter.ScriptBytes(from).AsSpan().SequenceEqual(WorldBodyWriter.ScriptBytes(to))) return null;
        List<SymbolChange> symbols = [];
        for (int i = 0; i < Math.Max(from.Code.Symbols.Count, to.Code.Symbols.Count); i++)
        {
            string before = Show(i < from.Code.Symbols.Count ? from.Code.Symbols[i] : null), after = Show(i < to.Code.Symbols.Count ? to.Code.Symbols[i] : null);
            if (before != after) symbols.Add(new SymbolChange(i, before, after));
        }
        return new ScriptChange(index, to.Name, from.Code.Instructions.Count, to.Code.Instructions.Count, from.Code.Symbols.Count, to.Code.Symbols.Count, symbols)
        {
            CodeDiffers = !from.Code.Instructions.SequenceEqual(to.Code.Instructions),
        };
    }

    /// <summary>A symbol as one line: its name, then its type and value (a float by its bits as well, so that a change of one bit shows).</summary>
    private static string Show(ScriptSymbol? symbol) => symbol is null ? "(none)" : $"{symbol.Name} {Value(symbol)}";

    private static string Value(ScriptSymbol symbol) => symbol.Value switch
    {
        null => $"[type {symbol.DataType}]",
        ScriptInt integer => integer.Value.ToString(CultureInfo.InvariantCulture),
        ScriptFloat number => $"{number.Value.ToString("R", CultureInfo.InvariantCulture)} (0x{BitConverter.SingleToUInt32Bits(number.Value):x8})",
        ScriptText text => $"\"{text.Value}\"",
        ScriptVector position => $"({position.Value.X.ToString("R", CultureInfo.InvariantCulture)}, {position.Value.Y.ToString("R", CultureInfo.InvariantCulture)}, {position.Value.Z.ToString("R", CultureInfo.InvariantCulture)})",
        _ => "[?]",
    };
}
