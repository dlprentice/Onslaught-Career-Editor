// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using OnslaughtRebuild.Core;

// Synthetic byte-stream and field-width comparisons. This does not simulate
// gameplay or refresh any existing tape/state/trace expectation.
internal static class GdscriptReplayOracle
{
    public static object Build()
    {
        var hashes = new List<object>();
        string Hex(byte[] bytes) => Convert.ToHexString(bytes).ToLowerInvariant();
        byte[] Pattern(int length) => Enumerable.Range(0, length).Select(i => (byte)(i * 197 + i / 17)).ToArray();
        void Hash(string name, byte[] bytes, int chunkSize)
        {
            using IncrementalHash hasher = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
            var chunks = new List<object>();
            for (int offset = 0; offset < bytes.Length; offset += chunkSize)
            {
                byte[] piece = bytes.AsSpan(offset, Math.Min(chunkSize, bytes.Length - offset)).ToArray();
                hasher.AppendData(piece);
                chunks.Add(new { hex = Hex(piece), hash = Hex(hasher.GetCurrentHash()) });
            }
            hashes.Add(new { name, chunks, hash = Hex(SHA256.HashData(bytes)) });
        }
        Hash("empty", [], 64);
        Hash("abc", Encoding.ASCII.GetBytes("abc"), 1);
        Hash("fips-multiblock", Encoding.ASCII.GetBytes("abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"), 7);
        foreach (int length in Enumerable.Range(1, 132).Concat([255, 256, 257, 511, 512, 513, 1023, 1024, 1025]))
        {
            Hash($"length-{length}-whole", Pattern(length), length);
            Hash($"length-{length}-split", Pattern(length), length % 67 + 1);
        }
        Hash("128k-bounded-stream", Pattern(131072), 4093);

        Type type = typeof(Simulation).Assembly.GetType("OnslaughtRebuild.Core.ReplayTraceHasher")!;
        var append = type.GetMethod("Append")!;
        var current = type.GetMethod("GetCurrentHash")!;
        var header = type.GetMethod("CreateTraceHeader", BindingFlags.Static | BindingFlags.NonPublic)!;
        var entry = type.GetMethod("CreateTraceEntry", BindingFlags.Static | BindingFlags.NonPublic)!;
        object hasherObject = Activator.CreateInstance(type)!;
        var rows = new List<object>();
        string initial = (string)current.Invoke(hasherObject, null)!;
        uint random = 0x54524143;
        uint Next() => random = unchecked(random * 1664525u + 1013904223u);
        for (int index = 0; index < 96; index++)
        {
            int slot = index switch { 0 => int.MinValue, 1 => int.MaxValue, _ => unchecked((int)Next()) };
            var input = new SimInput(unchecked((sbyte)Next()), unchecked((sbyte)Next()),
                (SimActions)(ushort)Next(), unchecked((sbyte)Next()), unchecked((sbyte)Next()),
                unchecked((short)Next()), unchecked((short)Next()));
            byte[] state = Pattern(index % 73);
            byte[] canonical = (byte[])entry.Invoke(null, [slot, input, state])!;
            append.Invoke(hasherObject, [slot, input, state]);
            string hash = (string)current.Invoke(hasherObject, null)!;
            if (hash != (string)current.Invoke(hasherObject, null)!) throw new Exception("Reference peek mutated state.");
            rows.Add(new { slot, input = new {
                move_x = input.MoveX, move_z = input.MoveZ, look_x = input.LookX, look_y = input.LookY,
                look_x_analog_permille = input.LookXAnalogPermille, look_y_analog_permille = input.LookYAnalogPermille,
                actions = (ushort)input.Actions }, state = Hex(state), entry = Hex(canonical), hash });
        }
        ((IDisposable)hasherObject).Dispose();
        var strings = new List<object>();
        void StringCase(string text)
        {
            using var stream = new MemoryStream();
            using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true)) writer.Write(text);
            strings.Add(new { units = text.Select(unit => (int)unit).ToArray(), bytes = Hex(stream.ToArray()) });
        }
        foreach (string text in new[] { "", "\0suffix", "prefix\0suffix", "\ufeff\ufeffstart",
            "\ud800", "\udc00", "\ud800\ud800\udc00", "\ud83d\ude80", "é", "Ω" }) StringCase(text);
        foreach (int size in new[] { 126, 127, 128, 129, 16382, 16383, 16384, 16385 }) StringCase(new string('a', size));
        for (int index = 0; index < 128; index++)
        {
            char[] units = new char[index];
            for (int offset = 0; offset < units.Length; offset++) units[offset] = (char)Next();
            StringCase(new string(units));
        }
        return new { hashes, header = Hex((byte[])header.Invoke(null, null)!), initial, rows, strings };
    }
}
