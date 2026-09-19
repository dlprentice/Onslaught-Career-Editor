// SPDX-License-Identifier: GPL-3.0-or-later
// Transitional comparison oracle; expected native words stay in their existing tests.
using System.Numerics;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.Core.Tests;
using OnslaughtRebuild.Client;

string output = Path.GetFullPath(args[0]);
Type fp = typeof(Simulation).Assembly.GetType("OnslaughtRebuild.Core.RetailFloat24")!;
string Hex(double v) => Convert.ToHexString(BitConverter.GetBytes(v)).ToLowerInvariant();
uint[] Words(Level100FloatVector3Bits v) => [unchecked((uint)v.X), unchecked((uint)v.Y), unchecked((uint)v.Z)];
uint[] Basis(Level100FloatBasis3Bits v) => [unchecked((uint)v.Row0X), unchecked((uint)v.Row0Y), unchecked((uint)v.Row0Z),
    unchecked((uint)v.Row1X), unchecked((uint)v.Row1Y), unchecked((uint)v.Row1Z),
    unchecked((uint)v.Row2X), unchecked((uint)v.Row2Y), unchecked((uint)v.Row2Z)];
uint random = 0x4f4e534c;
uint Next() { random = unchecked(random * 1664525u + 1013904223u); return random; }
double Number()
{
    ulong mantissa = (((ulong)Next() << 32) | Next()) & 0x000ffffffffffffful;
    ulong exponent = (ulong)(Next() % 2046 + 1) << 52;
    ulong sign = (ulong)((Next() >> 16) & 1) << 63;
    return BitConverter.Int64BitsToDouble(unchecked((long)(sign | exponent | mantissa)));
}
var arithmetic = new List<object>();
void Arithmetic(string operation, params double[] operands)
{
    MethodInfo method = fp.GetMethod(operation, BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic)!;
    try
    {
        double value = (double)method.Invoke(null, operands.Cast<object>().ToArray())!;
        arithmetic.Add(new { operation, operands = operands.Select(Hex), result = Hex(value), error = false });
    }
    catch (TargetInvocationException ex) when (ex.InnerException is ArgumentOutOfRangeException)
    {
        arithmetic.Add(new { operation, operands = operands.Select(Hex), result = "", error = true });
    }
}
foreach (double value in new[] { 0.0, -0.0, 1.0, -1.0, 1.0 + Math.ScaleB(1.0, -24),
    1.0 + 3 * Math.ScaleB(1.0, -24), -1.0 - Math.ScaleB(1.0, -24),
    double.Epsilon, -double.Epsilon, double.MaxValue, -double.MaxValue,
    Math.ScaleB(1.0, -1022), Math.ScaleB(1.0, -150), Math.ScaleB(1.0, 150),
    double.NaN, double.PositiveInfinity, double.NegativeInfinity }) Arithmetic("Round", value);
for (int i = 0; i < 512; i++) Arithmetic("Round", Number());
foreach (string operation in new[] { "Add", "Subtract", "Multiply", "Divide" })
    for (int i = 0; i < 256; i++) Arithmetic(operation, Number(), Number());
for (int i = 0; i < 256; i++) Arithmetic("Sqrt", Math.Abs(Number()));
Arithmetic("Add", 0.0, -0.0);
Arithmetic("Multiply", -0.0, 2.0);
Arithmetic("Divide", 0.0, 0.0);
Arithmetic("Divide", 1.0, 0.0);

var eulers = new List<object>();
for (int i = 0; i < 512; i++)
{
    int Angle() => BitConverter.SingleToInt32Bits(((int)(Next() % 4000001) - 2000000) / 65536f);
    var value = new Level100FloatVector3Bits(Angle(), Angle(), Angle());
    eulers.Add(new { words = Words(value), expected = Basis(RetailUnitEuler.BuildBasis(value)) });
}
var smooth = new List<object>();
for (int i = 0; i < 256; i++)
{
    int Angle() => BitConverter.SingleToInt32Bits(((int)(Next() % 4000001) - 2000000) / 65536f);
    var current = new Level100FloatVector3Bits(Angle(), Angle(), Angle());
    var desired = new Level100FloatVector3Bits(Angle(), Angle(), Angle());
    var rate = new Level100FloatVector3Bits(BitConverter.SingleToInt32Bits((Next() % 10000) / 10000f),
        BitConverter.SingleToInt32Bits((Next() % 10000) / 10000f), BitConverter.SingleToInt32Bits((Next() % 10000) / 10000f));
    float multiplier = (Next() % 8 + 1) * 0.5f;
    smooth.Add(new { current = Words(current), desired = Words(desired), rate = Words(rate), multiplier,
        expected = Words(RetailUnitEuler.Smooth(current, desired, rate, multiplier)) });
}
var rng = new List<object>();
foreach (int seed in new[] { 123456, 0, 1, -1, int.MinValue, int.MaxValue, -214783647 })
{
    var stream = new Level100ReleasedRandom(seed);
    var values = new List<object>();
    for (int i = 0; i < 1024; i++) { int value = stream.Next(); values.Add(new { value, seed = stream.Seed }); }
    rng.Add(new { seed, values });
}
var big = new List<object>();
int[] Limbs(BigInteger v)
{
    var result = new List<int>();
    do { result.Add((int)(v & 32767)); v >>= 15; } while (v > 0);
    return result.ToArray();
}
for (int i = 0; i < 64; i++)
{
    long nx = (int)(Next() % 2000001) - 1000000, ny = 1000, nz = (int)(Next() % 2000001) - 1000000;
    long vx = (int)(Next() % 2000001) - 1000000, vy = (int)(Next() % 2000001) - 1000000, vz = (int)(Next() % 2000001) - 1000000;
    long a = Math.Abs(nx * vx + ny * vy + nz * vz), normal2 = nx * nx + ny * ny + nz * nz, velocity2 = vx * vx + vy * vy + vz * vz;
    BigInteger numerator = (BigInteger)a * a * 1000000, denominator = (BigInteger)normal2 * velocity2;
    big.Add(new { a = a.ToString(), normal2 = normal2.ToString(), velocity2 = velocity2.ToString(),
        product = Limbs(numerator), result = (int)((numerator + denominator / 2) / denominator) });
}
string label = new string('é', 100) + " Aquila Ω 🚀";
byte[] binary;
using (var stream = new MemoryStream())
{
    using (var writer = new BinaryWriter(stream, Encoding.UTF8, true))
    {
        writer.Write(true); writer.Write(false); writer.Write(int.MinValue); writer.Write(uint.MaxValue);
        writer.Write(long.MinValue); writer.Write(ulong.MaxValue - 4); writer.Write(-0.0f);
        writer.Write(1.25); writer.Write(label);
    }
    binary = stream.ToArray();
}
var nativeBasis = RetailUnitEulerTests.NativeBasisCases().Select(row => new
{
    name = (string)row[0], words = Words((Level100FloatVector3Bits)row[1]),
    expected = Basis((Level100FloatBasis3Bits)row[2]),
}).ToArray();
foreach (var row in nativeBasis)
{
    var input = new Level100FloatVector3Bits(unchecked((int)row.words[0]), unchecked((int)row.words[1]), unchecked((int)row.words[2]));
    if (!Basis(RetailUnitEuler.BuildBasis(input)).SequenceEqual(row.expected)) throw new Exception("Current C# fails native basis fixture.");
}
var nativeSmooth = RetailUnitEulerTests.NativeCases().Select(row => new
{
    name = (string)row[0], current = Words((Level100FloatVector3Bits)row[1]),
    desired = Words((Level100FloatVector3Bits)row[2]), rate = Words((Level100FloatVector3Bits)row[3]),
    multiplier = (float)row[4], expected = Words((Level100FloatVector3Bits)row[5]),
}).ToArray();
var scaledRng = new List<object>();
foreach (int seed in new[] { 123456, 0, 1, -1, int.MinValue, int.MaxValue, 31449323 })
foreach (int scale in new[] { 0, 1, -1, 32768, int.MinValue, int.MaxValue })
{
    var stream = new Level100ReleasedRandom(seed);
    try
    {
        int value = stream.NextSignedUnitScaled(scale);
        scaledRng.Add(new { seed, scale, value, seedAfter = stream.Seed, error = false });
    }
    catch (OverflowException)
    {
        scaledRng.Add(new { seed, scale, value = 0, seedAfter = stream.Seed, error = true });
    }
}
// The arbitrary-precision operations used by contact comparisons and integer rounding.
var wide = new List<object>();
string[] wideInputs = ["0", "1", "2", "32767", "32768", "9223372036854775807",
    "18446744073709551615", "170141183460469231731687303715884105727",
    "999999999999999999999999999999999999999999999999999999999999999"];
foreach (string left in wideInputs)
foreach (string right in wideInputs)
{
    BigInteger a = BigInteger.Parse(left), b = BigInteger.Parse(right);
    wide.Add(new { left, right, a = Limbs(a), b = Limbs(b), sum = Limbs(a + b), product = Limbs(a * b),
        compare = a.CompareTo(b), difference = a >= b ? Limbs(a - b) : [],
        quotient = b > 0 ? Limbs(a / b) : [], remainder = b > 0 ? Limbs(a % b) : [] });
}
var pause = new List<object>();
var menu = new Level100PauseMenu();
object PauseState() => new
{
    is_open = menu.IsOpen, page = (int)menu.Page, selected_index = menu.SelectedIndex,
    underlying_root_selection = menu.UnderlyingRootSelection,
    entries = menu.Entries.Select(entry => new { id = (int)entry.Id, label = entry.Label, enabled = entry.IsEnabled }).ToArray(),
    root_entries = menu.RootEntries.Select(entry => new { id = (int)entry.Id, label = entry.Label, enabled = entry.IsEnabled }).ToArray(),
};
void PauseOperation(string operation, int argument = 0)
{
    object? returned = null;
    switch (operation)
    {
        case "open": menu.Open(); break;
        case "reset": menu.Reset(); break;
        case "move_selection": returned = menu.MoveSelection(argument); break;
        case "hover": returned = menu.Hover(argument); break;
        case "activate_selected": returned = (int)menu.ActivateSelected(); break;
        case "cancel": returned = (int)menu.Cancel(); break;
        default: throw new InvalidOperationException(operation);
    }
    pause.Add(new { operation, argument, returned, state = PauseState() });
}
// Explicit confirmation outcomes, safe No/default, disabled rows, cancel and reopen.
PauseOperation("reset"); PauseOperation("cancel"); PauseOperation("activate_selected");
PauseOperation("open"); PauseOperation("hover", 1); PauseOperation("hover", -1);
PauseOperation("move_selection", 0); PauseOperation("move_selection", 1);
PauseOperation("activate_selected"); PauseOperation("open"); PauseOperation("activate_selected");
PauseOperation("activate_selected"); PauseOperation("move_selection", 1); PauseOperation("activate_selected");
PauseOperation("open"); PauseOperation("move_selection", -1); PauseOperation("activate_selected");
PauseOperation("cancel"); PauseOperation("activate_selected"); PauseOperation("hover", 1);
PauseOperation("activate_selected"); PauseOperation("open"); PauseOperation("activate_selected");
string[] pauseOperations = ["open", "reset", "move_selection", "hover", "activate_selected", "cancel"];
for (int index = 0; index < 1024; index++)
    PauseOperation(pauseOperations[(Next() >> 16) % 6], (int)((Next() >> 16) % 13) - 2);
File.WriteAllText(output, JsonSerializer.Serialize(new { schema = 1, arithmetic, eulers, smooth, rng, scaledRng, big, wide, pause, json = GdscriptJsonOracle.Build(),
    startup = OnslaughtRebuild.TestSupport.GdscriptStartupScheduleOracle.Create(), chunkReader = GdscriptChunkReaderOracle.Build(),
    scheduler = GdscriptEventSchedulerOracle.BuildFixtures(),
    nativeBasis, nativeSmooth, binary = new { label, hex = Convert.ToHexString(binary).ToLowerInvariant(), sha256 = Convert.ToHexString(SHA256.HashData(binary)).ToLowerInvariant() } }, new JsonSerializerOptions { MaxDepth = 512 }));
Console.WriteLine($"Oracle: {arithmetic.Count} numerical cases, {eulers.Count} generated bases, {nativeBasis.Length} native bases, {nativeSmooth.Length} native smooth fixtures, {smooth.Count} generated smooth cases, {rng.Count * 1024} RNG steps, {scaledRng.Count} scaled RNG cases, {big.Count} contact ratios, {wide.Count} wide integer pairs.");
