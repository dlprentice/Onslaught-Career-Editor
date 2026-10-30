// SPDX-License-Identifier: GPL-3.0-only
using System.Globalization;
using System.Text.Json;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// Replaces one compiled script of a world body with another of the same name. The name stays because it is how the things that run the script
/// (and the other scripts that post to it) find it: renaming is a different edit, which this editor does not make. One instance is one replacement:
/// it remembers the script it put aside, so it cannot be made twice without being taken back between.
/// </summary>
public sealed class ReplaceScript : IEditCommand
{
    private readonly int _scriptIndex;
    private readonly MissionScript _script;
    private MissionScript? _previous;
    private string _description;

    /// <summary>Captures the supplied script now; later changes to the caller's object cannot change this edit or its redo.</summary>
    public ReplaceScript(int scriptIndex, MissionScript script)
    {
        ArgumentNullException.ThrowIfNull(script);
        _scriptIndex = scriptIndex;
        _script = ScriptCopy.Of(script);
        _description = $"Replace script {scriptIndex}";
    }

    public int ScriptIndex => _scriptIndex;
    /// <summary>A fresh copy of the script this command captured.</summary>
    public MissionScript Script => ScriptCopy.Of(_script);
    public string Description => _description;

    public void Do(WorldBody body)
    {
        if (_previous is not null) throw new InvalidOperationException("This replacement has already been made. Take it back first, or make a new one.");
        if (_scriptIndex < 0 || _scriptIndex >= body.Scripts.Count)
            throw new InvalidOperationException($"There is no script {_scriptIndex}: this world has {body.Scripts.Count}.");
        MissionScript old = body.Scripts[_scriptIndex] ?? throw new InvalidOperationException($"Script {_scriptIndex} is missing and cannot be replaced.");
        if (!string.Equals(old.Name, _script.Name, StringComparison.Ordinal))
            throw new InvalidOperationException($"The script {old.Name} cannot be replaced by one named {_script.Name}: a script keeps its name, which is how the things that run it find it.");
        MissionScript replacement = ScriptCopy.Of(_script);
        _previous = ScriptCopy.Of(old);
        body.Scripts[_scriptIndex] = replacement;
        _description = $"Replace script {old.Name}";
    }

    public void Undo(WorldBody body)
    {
        if (_previous is null) throw new InvalidOperationException("This replacement has not been made, so there is nothing to take back.");
        body.Scripts[_scriptIndex] = _previous;
        _previous = null;
    }
}

/// <summary>Copies every mutable part, including malformed fields, so the edit can be inspected and refused without serializing it first.</summary>
internal static class ScriptCopy
{
    internal static MissionScript Of(MissionScript script)
    {
        ScriptCode? source = script.Code;
        ScriptCode? code = source is null ? null : new ScriptCode
        {
            EventPcs = source.EventPcs?.ToArray()!, NextSymbolIndex = source.NextSymbolIndex, Tail1 = source.Tail1, Tail2 = source.Tail2,
        };
        if (source is not null && code is not null)
        {
            code.Instructions.AddRange(source.Instructions);
            foreach (ScriptSymbol? symbol in source.Symbols)
                code.Symbols.Add(symbol is null ? null! : new ScriptSymbol
                {
                    Name = symbol.Name, DataType = symbol.DataType, Value = symbol.Value, SymbolType = symbol.SymbolType, Index = symbol.Index, Flag = symbol.Flag,
                });
            foreach (EventFunction? function in source.EventFunctions)
            {
                if (function is null) { code.EventFunctions.Add(null!); continue; }
                EventFunction copy = new() { EntryPc = function.EntryPc };
                copy.Parameters.AddRange(function.Parameters);
                code.EventFunctions.Add(copy);
            }
        }
        return new MissionScript { Name = script.Name, Code = code!, Trailer = script.Trailer?.ToArray()! };
    }
}

/// <summary>One entry of a script's symbol table that differs from the baseline's, as the player would read it.</summary>
/// <param name="Index">The symbol's place in the script's symbol table.</param>
/// <param name="From">The baseline's symbol: its name and value ("(none)" when the baseline has no symbol there).</param>
/// <param name="To">The working script's symbol, in the same form ("(none)" when it has no symbol there).</param>
public sealed record SymbolChange(int Index, string From, string To);

/// <summary>A stored non-symbol field that differs, with its place and the two values.</summary>
public sealed record ScriptFieldChange(string Field, string From, string To);

/// <summary>One script whose record differs from the baseline's, with what differs said in numbers and values.</summary>
public sealed record ScriptChange(int Index, string Name, int InstructionsFrom, int InstructionsTo, int SymbolsFrom, int SymbolsTo, IReadOnlyList<SymbolChange> Symbols)
{
    /// <summary>True when the instructions differ in more than their number (an instruction's opcode or operand is not the baseline's).</summary>
    public bool CodeDiffers { get; init; }

    /// <summary>Changed instructions, event entries, handlers, trailing words and trailer. Symbol fields are in <see cref="Symbols"/>.</summary>
    public IReadOnlyList<ScriptFieldChange> Fields { get; init; } = [];

    /// <summary>Why the working record cannot be stored, or null when it can.</summary>
    public string? StorageError { get; init; }

    /// <summary>A short player-facing summary. The full before/after details remain in <see cref="Fields"/> and <see cref="Symbols"/>.</summary>
    public string Describe()
    {
        if (StorageError is { } error) return $"cannot be saved: {error}";
        List<string> parts = [];
        if (CodeDiffers) parts.Add(InstructionsFrom == InstructionsTo ? "its code differs" : $"{InstructionsFrom} to {InstructionsTo} instructions");
        if (Symbols.Count > 0) parts.Add(Symbols.Count == 1 ? "1 symbol differs" : $"{Symbols.Count} symbols differ");
        ScriptFieldChange[] other = [.. Fields.Where(field => !field.Field.StartsWith("instruction ", StringComparison.Ordinal))];
        parts.AddRange(other.Take(3).Select(field => $"{field.Field}: {Brief(field.From)} to {Brief(field.To)}"));
        if (other.Length > 3)
        {
            int more = other.Length - 3;
            parts.Add(more == 1 ? "1 more field differs" : $"{more} more fields differ");
        }
        return parts.Count == 0 ? "its record differs" : string.Join(", ", parts);
    }

    private static string Brief(string text) => text.Length <= 80 ? text : text[..77] + "...";
}

internal static class ScriptDiff
{
    /// <summary>What differs between a script as the baseline has it and as it is now, or null when the two are the same record (bit for bit).</summary>
    internal static ScriptChange? Between(int index, MissionScript from, MissionScript to)
    {
        byte[] beforeBytes = WorldBodyWriter.ScriptBytes(from);
        byte[] afterBytes;
        try { afterBytes = WorldBodyWriter.ScriptBytes(to); }
        catch (InvalidDataException error)
        {
            return new ScriptChange(index, to.Name, from.Code.Instructions.Count, to.Code?.Instructions.Count ?? 0,
                from.Code.Symbols.Count, to.Code?.Symbols.Count ?? 0, []) { StorageError = error.Message };
        }
        if (beforeBytes.AsSpan().SequenceEqual(afterBytes)) return null;
        List<SymbolChange> symbols = [];
        for (int i = 0; i < Math.Max(from.Code.Symbols.Count, to.Code.Symbols.Count); i++)
        {
            string before = Show(i < from.Code.Symbols.Count ? from.Code.Symbols[i] : null), after = Show(i < to.Code.Symbols.Count ? to.Code.Symbols[i] : null);
            if (before != after) symbols.Add(new SymbolChange(i, before, after));
        }
        List<ScriptFieldChange> fields = [];
        for (int i = 0; i < Math.Max(from.Code.Instructions.Count, to.Code.Instructions.Count); i++)
        {
            ScriptInstruction? before = i < from.Code.Instructions.Count ? from.Code.Instructions[i] : null;
            ScriptInstruction? after = i < to.Code.Instructions.Count ? to.Code.Instructions[i] : null;
            if (before != after) fields.Add(new ScriptFieldChange($"instruction {i}", Instruction(before), Instruction(after)));
        }
        for (int i = 0; i < ScriptCode.EventCount; i++)
            Add(fields, $"event {i} entry", from.Code.EventPcs[i], to.Code.EventPcs[i]);
        Add(fields, "next symbol index", from.Code.NextSymbolIndex, to.Code.NextSymbolIndex);
        for (int i = 0; i < Math.Max(from.Code.EventFunctions.Count, to.Code.EventFunctions.Count); i++)
        {
            EventFunction? before = i < from.Code.EventFunctions.Count ? from.Code.EventFunctions[i] : null;
            EventFunction? after = i < to.Code.EventFunctions.Count ? to.Code.EventFunctions[i] : null;
            string first = Handler(before), second = Handler(after);
            if (first != second) fields.Add(new ScriptFieldChange($"handler {i}", first, second));
        }
        Add(fields, "first trailing word", from.Code.Tail1, to.Code.Tail1);
        Add(fields, "second trailing word", from.Code.Tail2, to.Code.Tail2);
        if (!from.Trailer.AsSpan().SequenceEqual(to.Trailer))
            fields.Add(new ScriptFieldChange("trailer", Convert.ToHexString(from.Trailer), Convert.ToHexString(to.Trailer)));
        return new ScriptChange(index, to.Name, from.Code.Instructions.Count, to.Code.Instructions.Count, from.Code.Symbols.Count, to.Code.Symbols.Count, symbols)
        {
            CodeDiffers = !from.Code.Instructions.SequenceEqual(to.Code.Instructions),
            Fields = fields,
        };
    }

    private static void Add(List<ScriptFieldChange> fields, string name, int before, int after)
    {
        if (before != after) fields.Add(new ScriptFieldChange(name, before.ToString(CultureInfo.InvariantCulture), after.ToString(CultureInfo.InvariantCulture)));
    }

    private static string Instruction(ScriptInstruction? instruction) => instruction is { } value
        ? $"opcode {value.Opcode.ToString(CultureInfo.InvariantCulture)}, operand {value.Attribute.ToString(CultureInfo.InvariantCulture)}" : "(none)";

    private static string Handler(EventFunction? function) => function is null ? "(none)" :
        $"entry {function.EntryPc.ToString(CultureInfo.InvariantCulture)}, parameters [{string.Join(", ", function.Parameters.Select(value => value.ToString(CultureInfo.InvariantCulture)))}]";

    /// <summary>A symbol includes every stored field; floating-point values include their bits so signed zero and NaNs remain distinct.</summary>
    private static string Show(ScriptSymbol? symbol) => symbol is null ? "(none)" :
        $"{JsonSerializer.Serialize(symbol.Name)} [data type {symbol.DataType}, symbol type {symbol.SymbolType}, index {symbol.Index}, flag {symbol.Flag}] {Value(symbol)}";

    private static string Value(ScriptSymbol symbol) => symbol.Value switch
    {
        _ when symbol.DataType == 0 => "(no value)",
        null => "(missing)",
        ScriptInt integer => integer.Value.ToString(CultureInfo.InvariantCulture),
        ScriptFloat number => Float(number.Value),
        ScriptText text => JsonSerializer.Serialize(text.Value),
        ScriptVector position => $"({Float(position.Value.X)}, {Float(position.Value.Y)}, {Float(position.Value.Z)})",
        _ => "[?]",
    };

    private static string Float(float value) => $"{value.ToString("R", CultureInfo.InvariantCulture)} (0x{BitConverter.SingleToUInt32Bits(value):x8})";
}
