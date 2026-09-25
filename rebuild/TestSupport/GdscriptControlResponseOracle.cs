// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.Core;
using System.Reflection;
using System.Text.RegularExpressions;

internal static class GdscriptControlResponseOracle
{
    internal static object Build()
    {
        var inputs = Enumerable.Range(-1200, 2401).Concat(new[] { int.MinValue, int.MinValue + 1,
            int.MaxValue, -32768, 32767, -70000, 70000 }).ToList();
        var look = inputs.Select(input =>
        {
            object result;
            try { result = new { ok = true, value = LookAxisResponse.Apply(input) }; }
            catch (OverflowException) { result = new { ok = false, error_type = "OverflowException" }; }
            return new { input, result };
        }).ToArray();
        var axes = Enumerable.Range(-1024, 2049).Concat(Enumerable.Range(32760, 17))
            .Concat(new[] { int.MinValue, int.MinValue + 1, int.MaxValue, -70000, 70000,
                -65536, -65535, -32768, -32767, 65534, 65535, 65536 }).ToList();
        var random = new Random(0x41584953);
        for (int i = 0; i < 4096; i++) axes.Add((int)random.NextInt64(int.MinValue, (long)int.MaxValue + 1));
        var normalized = axes.Select(input => new { input,
            left_x = Word(RetailAnalogueControls.NormalizeLeftX(input)),
            left_y = Word(RetailAnalogueControls.NormalizeLeftY(input)),
            right_x = Word(RetailAnalogueControls.NormalizeRightX(input)),
            right_y = Word(RetailAnalogueControls.NormalizeRightY(input)) }).ToArray();
        var words = new List<uint> { 0, 0x80000000, 1, 0x80000001, 0x007fffff, 0x807fffff,
            0x00800000, 0x80800000, 0x3f666665, 0x3f666666, 0x3f666667,
            0xbf666665, 0xbf666666, 0xbf666667, 0x3f800000, 0xbf800000,
            0x7f7fffff, 0xff7fffff, 0x7f800000, 0xff800000,
            0x7fc00000, 0xffc00000, 0x7f800001, 0xff800001 };
        for (int i = 0; i < 1024; i++) words.Add((uint)random.NextInt64(1L << 32));
        var gates = words.Select(bits =>
        {
            float value = BitConverter.UInt32BitsToSingle(bits);
            return new { bits, value = new { plus_fires = RetailAnalogueControls.AnaloguePlusFires(value),
                minus_fires = RetailAnalogueControls.AnalogueMinusFires(value),
                plus_repeat_arms = RetailAnalogueControls.AnaloguePlusRepeatArms(value),
                minus_repeat_arms = RetailAnalogueControls.AnalogueMinusRepeatArms(value) } };
        }).ToArray();
        string NativeName(string name) => Regex.Replace(
            Regex.Replace(name, "([A-Z]+)([A-Z][a-z])", "$1_$2"), "([a-z0-9])([A-Z])", "$1_$2").ToUpperInvariant();
        var simulationConstants = new Dictionary<string, object>();
        foreach (FieldInfo field in typeof(SimulationConstants).GetFields(BindingFlags.Public | BindingFlags.Static))
        {
            object value = field.GetValue(null)!;
            simulationConstants.Add(NativeName(field.Name), value is SimVector2 v ? new { x = v.X, z = v.Z } : value);
        }
        simulationConstants.Add("WALKER_FOOT_STANCE_OFFSETS_MILLIMETERS",
            SimulationConstants.WalkerFootStanceOffsetsMillimeters.Select(v => new { x = v.X, z = v.Z }).ToArray());
        return new { look, normalized, gates, simulation_constants = simulationConstants, constants = new {
            axis_scale = Word(RetailAnalogueControls.AxisScale), right_y_centre = Word(RetailAnalogueControls.RightYCentre),
            right_y_scale = Word(RetailAnalogueControls.RightYScale), digital_threshold = Word(RetailAnalogueControls.ActAsDigitalThreshold),
            initial_repeat_delay = Word(RetailAnalogueControls.InitialRepeatDelay), repeat_delay = Word(RetailAnalogueControls.RepeatDelay),
            absent_pad_axis = Word(RetailAnalogueControls.AbsentPadAxis) } };
    }
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
}
