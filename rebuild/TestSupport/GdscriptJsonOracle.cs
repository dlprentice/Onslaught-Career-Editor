// SPDX-License-Identifier: GPL-3.0-or-later
using System.Globalization;
using System.Numerics;
using System.Text;
using System.Text.Json;

// Exercise the current CommandTape codec's JSON grammar and ordinal duplicate
// rule independently of Godot's deliberately more permissive JSON class.
internal static class GdscriptJsonOracle
{
    internal static object Build()
    {
        var cases = new List<object>();
        void Add(string name, byte[] utf8, bool rejectDuplicates = true, int maxDepth = 64)
        {
            object? value = null;
            bool ok = false;
            try
            {
                using JsonDocument document = JsonDocument.Parse(utf8, new JsonDocumentOptions { MaxDepth = maxDepth });
                if (rejectDuplicates) RequireUnique(document.RootElement);
                value = Normalize(document.RootElement);
                ok = true;
            }
            catch (Exception error) when (error is JsonException or InvalidOperationException or DecoderFallbackException or ArgumentException) { }
            cases.Add(new { name, hex = Convert.ToHexString(utf8).ToLowerInvariant(), rejectDuplicates, maxDepth, ok, value });
        }
        void Text(string name, string text, bool reject = true, int depth = 64) => Add(name, Encoding.UTF8.GetBytes(text), reject, depth);
        foreach (string text in new[] { "null", "true", "false", "0", "-0", "1.0", "1e0", "1E+3", "-1.25e-2",
            "2147483647", "2147483648", "-2147483648", "-2147483649", "9007199254740993",
            "9223372036854775807", "-9223372036854775808", "9223372036854775808", "-9223372036854775809",
            "18446744073709551615", "1e9999", "1e-9999", "-1e-9999", "[]", "{}", "[true,false,null,1]",
            "{\"name\":\"BEA\",\"nested\":[{\"x\":1}]}", "\"áΩ🚀\"", "\"a\\u0000b\"",
            "\"\\b\\f\\n\\r\\t\\/\\\\\\\"\"", "\"\\uD83D\\uDE80\"", "\"\\uD800\"", "\"\\uDC00\"",
            "\"\\uD800x\"", "\"\\uD800\\uD800\"", " \t\r\n[1,2] \t\r\n" }) Text(text, text);
        foreach (string text in new[] { "", " ", "undefined", "NaN", "Infinity", "TRUE", "01", "-01", "+1", ".1", "1.",
            "1e", "1e+", "--1", "[1,]", "{\"x\":1,}", "[1 2]", "{x:1}", "{\"x\" 1}", "true false", "nullx",
            "/*comment*/null", "[//comment\n1]", "\"a\nb\"", "\"a\tb\"", "\"\\x00\"", "\"\\u123\"", "\"\\uXX00\"",
            "\"unterminated", "{\"a\":1,\"a\":2}", "{\"a\":1,\"\\u0061\":2}", "[{\"x\":1,\"x\":2}]" }) Text(text, text);
        Text("duplicates retained on explicit request", "{\"a\":1,\"\\u0061\":2}", false);
        Text("case sensitive names", "{\"a\":1,\"A\":2}");
        Text("embedded NUL duplicate", "{\"a\\u0000\":1,\"a\\u0000\":2}");
        Text("astral duplicate", "{\"🚀\":1,\"\\uD83D\\uDE80\":2}");
        for (int depth = 1; depth <= 65; depth++) Text($"depth {depth}", new string('[', depth) + "0" + new string(']', depth));
        Text("depth one empty", "[]", depth: 1);
        Text("depth one child", "[[]]", depth: 1);
        for (int value = 0; value < 32; value++) Add($"raw control {value}", [34, 97, (byte)value, 98, 34]);
        foreach (byte[] bytes in new byte[][] { [34,0xc0,0xaf,34], [34,0xe0,0x80,0x80,34], [34,0xed,0xa0,0x80,34],
            [34,0xf4,0x90,0x80,0x80,34], [34,0xff,34], [34,0xc2,34], [0xef,0xbb,0xbf,49] }) Add("invalid UTF-8", bytes);
        // Deterministic varied members/arrays and number tokens, with exact
        // decimal integers straddling binary64's 53-bit precision boundary.
        for (int i = 0; i < 256; i++)
            Text($"integer member {i}", $"{{\"index\":{i},\"value\":{9007199254740864L + i},\"rows\":[-0,\"unit {i}\",null]}}");
        foreach (string text in new[] { "0.1", "0.1000000000000000055511151231257827021181583404541015625",
            "2.2250738585072014e-308", "4.9406564584124654e-324", "2.4703282292062327e-324",
            "1.7976931348623157e308", "1.7976931348623159e308",
            "1.00000000000000011102230246251565404236316680908203125",
            "1.00000000000000033306690738754696212708950042724609375",
            "1e999999999999999999999999999999999999", "-1e-999999999999999999999999999999999999",
            "-0e999999999999999999999999999999999999" }) Text("double boundary " + text, text);
        BigInteger halfSubnormal = BigInteger.Pow(5, 1075);
        foreach (BigInteger numerator in new[] { halfSubnormal - 1, halfSubnormal, halfSubnormal + 1,
            halfSubnormal * 3, ((BigInteger.One << 53) - 1) * halfSubnormal })
        {
            Text("subnormal rounding boundary", numerator.ToString(CultureInfo.InvariantCulture) + "e-1075");
            Text("negative subnormal rounding boundary", "-" + numerator.ToString(CultureInfo.InvariantCulture) + "e-1075");
        }
        BigInteger overflowMidpoint = (BigInteger.One << 1024) - (BigInteger.One << 970);
        foreach (BigInteger value in new[] { overflowMidpoint - 1, overflowMidpoint, overflowMidpoint + 1 })
            Text("overflow rounding boundary", value.ToString(CultureInfo.InvariantCulture));
        ulong random = 0x415155494c41;
        for (int i = 0; i < 512; i++)
        {
            random = unchecked(random * 6364136223846793005UL + 1442695040888963407UL);
            double value = BitConverter.Int64BitsToDouble(unchecked((long)random));
            if (double.IsFinite(value)) Text($"roundtrip double {i}", value.ToString("R", CultureInfo.InvariantCulture));
        }
        return cases;
    }

    private static void RequireUnique(JsonElement value)
    {
        if (value.ValueKind == JsonValueKind.Object)
        {
            var names = new HashSet<string>(StringComparer.Ordinal);
            foreach (JsonProperty member in value.EnumerateObject())
            {
                if (!names.Add(member.Name)) throw new InvalidOperationException("Duplicate member");
                RequireUnique(member.Value);
            }
        }
        else if (value.ValueKind == JsonValueKind.Array)
            foreach (JsonElement item in value.EnumerateArray()) RequireUnique(item);
    }

    private static object Normalize(JsonElement value)
    {
        switch (value.ValueKind)
        {
            case JsonValueKind.Object:
                return new { kind = "object", members = value.EnumerateObject().Select(member =>
                    new { name = StringValue(member.Name), value = Normalize(member.Value) }).ToArray() };
            case JsonValueKind.Array:
                return new { kind = "array", items = value.EnumerateArray().Select(Normalize).ToArray() };
            case JsonValueKind.String:
                return StringValue(value.GetString()!);
            case JsonValueKind.Number:
                return new { kind = "number", text = value.GetRawText(), int64 = value.TryGetInt64(out long integer)
                    ? integer.ToString(CultureInfo.InvariantCulture) : null,
                    int32 = value.TryGetInt32(out int small) ? small.ToString(CultureInfo.InvariantCulture) : null,
                    doubleHex = Convert.ToHexString(BitConverter.GetBytes(value.GetDouble())).ToLowerInvariant() };
            case JsonValueKind.True: return new { kind = "boolean", value = true };
            case JsonValueKind.False: return new { kind = "boolean", value = false };
            default: return new { kind = "null" };
        }
    }

    private static object StringValue(string value) => new { kind = "string", units = value.Select(c => (int)c).ToArray(),
        utf8 = Convert.ToHexString(Encoding.UTF8.GetBytes(value)).ToLowerInvariant() };
}
