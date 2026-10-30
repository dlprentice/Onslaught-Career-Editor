// SPDX-License-Identifier: GPL-3.0-only
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// A compiled script as lines, in the form tools/msl_vectors.py writes for the Toolkit's reference compiler (the instructions by opcode name,
/// the entry points, the symbols with their values, the named handlers, the two trailing words), so that two compilers' results are compared
/// as text and a difference shows where it is. A float is its bits and a string its Latin-1 bytes in hex. The script's trailer is not a line: every
/// script has the same one, and the tests and the gate compare it on its own.
/// </summary>
internal static class ScriptDump
{
    internal static string[] Lines(MissionScript script)
    {
        ScriptCode code = script.Code;
        List<string> lines = [$"name {script.Name}"];
        for (int n = 0; n < code.Instructions.Count; n++)
            lines.Add($"instruction {n} {ScriptTables.Opcodes[code.Instructions[n].Opcode]} {code.Instructions[n].Attribute}");
        for (int n = 0; n < code.EventPcs.Length; n++) lines.Add($"eventPC {n} {code.EventPcs[n]}");
        foreach (ScriptSymbol symbol in code.Symbols) lines.Add($"symbol {symbol.Index} {symbol.Name} {symbol.DataType} {Value(symbol.Value)} {symbol.SymbolType} {symbol.Flag}");
        lines.Add($"nextSymbolIndex {code.NextSymbolIndex}");
        for (int n = 0; n < code.EventFunctions.Count; n++)
            lines.Add($"eventFunction {n} {code.EventFunctions[n].EntryPc} {string.Join(',', code.EventFunctions[n].Parameters)}");
        lines.Add($"tail {code.Tail1} {code.Tail2}");
        return [.. lines];
    }

    private static string Value(ScriptValue? value) => value switch
    {
        null => "-",
        ScriptInt integer => integer.Value.ToString(System.Globalization.CultureInfo.InvariantCulture),
        ScriptFloat number => "f:" + BitConverter.SingleToUInt32Bits(number.Value).ToString("x8", System.Globalization.CultureInfo.InvariantCulture),
        ScriptText text => "s:" + Convert.ToHexString(Encoding.Latin1.GetBytes(text.Value)).ToLowerInvariant(),
        ScriptVector position => "v:" + string.Join(',', new[] { position.Value.X, position.Value.Y, position.Value.Z }.Select(part => BitConverter.SingleToUInt32Bits(part).ToString("x8", System.Globalization.CultureInfo.InvariantCulture))),
        _ => throw new InvalidOperationException("a script symbol holds an int, a float, a string or a position"),
    };
}
