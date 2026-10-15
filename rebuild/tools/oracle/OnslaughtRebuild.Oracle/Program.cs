// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Text;

namespace OnslaughtRebuild.Oracle;

/// <summary>The C# side of the per-function oracle: reads "function TAB hex words" lines, runs each through its adapter and
/// writes the same shape. usage: Oracle.exe cases out imagesDir gameDir</summary>
public static class Program
{
    public static int Main(string[] args)
    {
        if (args.Length < 4)
        {
            Console.Error.WriteLine("usage: cases out imagesDir gameDir");
            return 2;
        }

        var context = new OracleContext(args[2], args[3]);
        IReadOnlyDictionary<string, Func<uint[], uint[]>> adapters = Adapters.Create(context);
        var output = new StringBuilder();
        foreach (string line in File.ReadLines(args[0]))
        {
            int tab = line.IndexOf('\t');
            if (tab < 0)
            {
                continue;
            }

            string name = line[..tab];
            uint[] input = Parse(line[(tab + 1)..]);
            output.Append(name).Append('\t').Append(adapters.TryGetValue(name, out Func<uint[], uint[]>? adapter) ? Format(adapter(input)) : "ERROR no adapter").Append('\n');
        }

        File.WriteAllText(args[1], output.ToString());
        return 0;
    }

    public static uint[] Parse(string words) =>
        words.Split(' ', StringSplitOptions.RemoveEmptyEntries).Select(w => uint.Parse(w, NumberStyles.HexNumber, CultureInfo.InvariantCulture)).ToArray();

    public static string Format(uint[] words) => string.Join(' ', words.Select(w => w.ToString("x8", CultureInfo.InvariantCulture)));
}
