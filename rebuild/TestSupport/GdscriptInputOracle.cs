// SPDX-License-Identifier: GPL-3.0-or-later
using System.Globalization;
using System.Reflection;
using OnslaughtRebuild.Client;

// Synthetic host facts. No device, window, session, simulation or retail input
// recording is required; current Client is the temporary migration oracle.
internal static class GdscriptInputOracle
{
    private readonly record struct Step(string Operation, int KeyCode = 0, int Joypad = 0,
        int Button = 0, byte Value = 0, bool Pressed = false, bool Echo = false);

    internal static object Build()
    {
        var inputs = new List<object>();
        void Input(string name, InteractiveInput input)
        {
            object expected;
            try { input.Validate(); expected = new { ok = true }; }
            catch (ArgumentException error)
            { expected = new { ok = false, error_type = error.GetType().Name, parameter = error.ParamName }; }
            inputs.Add(new { name, input = Record(input), expected });
        }
        Input("idle", InteractiveInput.Idle);
        for (int flags = 0; flags < 16; flags++)
            foreach (sbyte x in new sbyte[] { -1, 0, 1 })
                foreach (sbyte z in new sbyte[] { -1, 0, 1 })
                    Input($"levels-{flags}-{x}-{z}", new(x, z, (flags & 1) != 0, (flags & 2) != 0,
                        (flags & 4) != 0, z, x, (flags & 8) != 0));
        foreach (sbyte invalid in new sbyte[] { sbyte.MinValue, -127, -2, 2, 126, sbyte.MaxValue })
        {
            Input("move-x-" + invalid, new(invalid, 0, false, false, false));
            Input("move-z-" + invalid, new(0, invalid, true, false, false));
            Input("look-x-" + invalid, new(0, 0, false, true, false, invalid));
            Input("look-y-" + invalid, new(0, 0, false, false, true, 0, invalid));
            Input("first-invalid-axis-" + invalid, new(invalid, invalid, true, true, true, invalid, invalid, true));
            Input("second-invalid-axis-" + invalid, new(0, invalid, true, true, true, invalid, invalid, true));
            Input("third-invalid-axis-" + invalid, new(0, 0, true, true, true, invalid, invalid, true));
        }

        var scenarios = new List<object>();
        void Scenario(string name, IEnumerable<Step> steps, long frame = 0, long generation = 0)
        {
            var state = new PlatformInputEdgeState();
            // Boundary fixture only; production gains no restore/seeding API.
            typeof(PlatformInputEdgeState).GetField("<FrameIndex>k__BackingField", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(state, frame);
            typeof(PlatformInputEdgeState).GetField("<ResetGeneration>k__BackingField", BindingFlags.Instance | BindingFlags.NonPublic)!.SetValue(state, generation);
            var rows = new List<object>();
            foreach (Step step in steps)
            {
                object result;
                switch (step.Operation)
                {
                    case "observe_key": state.ObserveKey(step.KeyCode, step.Pressed, step.Echo); result = new { ok = true }; break;
                    case "held_key": result = new { ok = true, value = state.GetHeldKey(step.KeyCode) }; break;
                    case "consume_key": result = new { ok = true, value = state.ConsumeKeyOnce(step.KeyCode) }; break;
                    case "observe_joy": state.ObserveJoyButton(step.Joypad, step.Button, step.Value); result = new { ok = true }; break;
                    case "previous_joy": result = new { ok = true, value = state.GetPreviousJoyButton(step.Joypad, step.Button) }; break;
                    case "current_joy": result = new { ok = true, value = state.GetCurrentJoyButton(step.Joypad, step.Button) }; break;
                    case "rising": result = new { ok = true, value = state.IsJoyButtonRising(step.Joypad, step.Button) }; break;
                    case "held_joy": result = new { ok = true, value = state.IsJoyButtonHeld(step.Joypad, step.Button) }; break;
                    case "falling": result = new { ok = true, value = state.IsJoyButtonFalling(step.Joypad, step.Button) }; break;
                    case "advance": state.AdvanceFrame(); result = new { ok = true }; break;
                    case "reset": state.Reset(); result = new { ok = true }; break;
                    case "capture": result = new { ok = true }; break;
                    default: throw new InvalidOperationException("Unknown input fixture step.");
                }
                rows.Add(new { operation = step.Operation, key_code = step.KeyCode, joypad = step.Joypad, button = step.Button,
                    value = step.Value, pressed = step.Pressed, echo = step.Echo, expected = result, snapshot = Capture(state.Capture()) });
            }
            scenarios.Add(new { name, initial_frame = Long(frame), initial_generation = Long(generation), steps = rows });
        }
        Scenario("key-held-consume-repeat-release", [new("capture"), new("held_key", 0x51),
            new("observe_key", 0x51, Pressed: true, Echo: true), new("consume_key", 0x51),
            new("observe_key", 0x51, Pressed: true), new("observe_key", 0x52, Pressed: true),
            new("observe_key", 0x51, Pressed: false, Echo: true), new("held_key", 0x51),
            new("consume_key", 0x51), new("consume_key", 0x51), new("held_key", 0x51),
            new("observe_key", 0x51, Pressed: true), new("consume_key", 0x51),
            new("observe_key", 0x51, Pressed: true), new("observe_key", 0x51, Pressed: false),
            new("held_key", 0x51), new("advance"), new("consume_key", 0x51), new("consume_key", 0x52),
            new("reset"), new("advance"), new("reset"), new("capture")]);
        var joys = new List<Step> { new("capture") };
        foreach (byte value in new byte[] { 0, 1, 2, 0x7f, 0x80, 0xfe, 0xff })
        {
            joys.AddRange([new("observe_joy", Joypad: 2, Button: 7, Value: value),
                new("previous_joy", Joypad: 2, Button: 7), new("current_joy", Joypad: 2, Button: 7),
                new("rising", Joypad: 2, Button: 7), new("held_joy", Joypad: 2, Button: 7), new("falling", Joypad: 2, Button: 7),
                new("advance"), new("observe_joy", Joypad: 2, Button: 7), new("falling", Joypad: 2, Button: 7),
                new("advance"), new("falling", Joypad: 2, Button: 7)]);
        }
        joys.AddRange([new("observe_key", -1, Pressed: true), new("observe_joy", Joypad: -1, Button: -2, Value: 255),
            new("advance"), new("observe_joy", Joypad: -1, Button: -2), new("reset"), new("falling", Joypad: -1, Button: -2)]);
        Scenario("joy-full-byte-and-frame-edges", joys);
        var ordered = new List<Step>();
        foreach (int id in new[] { int.MaxValue, 9, -1, 0, int.MinValue, 2 })
        {
            ordered.Add(new("observe_key", id, Pressed: true));
            ordered.Add(new("observe_joy", Joypad: id, Button: int.MaxValue, Value: 128));
            ordered.Add(new("observe_joy", Joypad: id, Button: int.MinValue, Value: 255));
        }
        Scenario("capture-canonical-order", ordered.Concat([new Step("advance"), new Step("capture")]));
        Scenario("capture-reverse-order", ordered.AsEnumerable().Reverse().Concat([new Step("advance"), new Step("capture")]));
        Scenario("counter-wrap-does-not-reset-frame", [new("capture"), new("observe_key", 1, Pressed: true),
            new("observe_joy", Joypad: 1, Button: 2, Value: 1), new("advance"), new("reset"),
            new("advance"), new("reset"), new("capture")], long.MaxValue, long.MaxValue);
        uint random = 0x494e5054;
        uint Next() => random = unchecked(random * 1664525u + 1013904223u);
        string[] operations = ["observe_key", "held_key", "consume_key", "observe_joy", "previous_joy", "current_joy",
            "rising", "held_joy", "falling", "advance", "reset"];
        var varied = new List<Step>();
        for (int index = 0; index < 384; index++)
            varied.Add(new(operations[(int)(Next() % (uint)operations.Length)], (int)(Next() % 7) - 3,
                (int)(Next() % 5) - 2, (int)(Next() % 7) - 3, unchecked((byte)Next()), (Next() & 4) != 0, (Next() & 8) != 0));
        Scenario("varied-observation-order", varied);
        return new { inputs, scenarios, idle = Record(InteractiveInput.Idle),
            bindings = RetailControlBindings.Rows.Select(row => new { action_code = row.ActionCode, kind = (int)row.Kind,
                label = row.Label, slot0 = row.Slot0, slot1 = row.Slot1 }),
            invert_labels = new[] { false, true }.Select(inverted => new { inverted, value = RetailControlBindings.InvertYLabel(inverted) }),
            constants = new { row_count = RetailControlBindings.RowCount, row_pitch = Word(RetailControlBindings.RowPitch),
                top_pad = Word(RetailControlBindings.TopPad), left_column_x = Word(RetailControlBindings.LeftColumnX),
                right_column_right = Word(RetailControlBindings.RightColumnRight), player1_header = RetailControlBindings.Player1Header,
                player2_header = RetailControlBindings.Player2Header } };
    }

    private static object Record(InteractiveInput input) => new { move_x = input.MoveX, move_z = input.MoveZ, fire_held = input.FireHeld,
        toggle_mode_held = input.ToggleModeHeld, reset_held = input.ResetHeld, look_x = input.LookX, look_y = input.LookY, landing_jets_held = input.LandingJetsHeld };
    private static object Long(long value) => new Dictionary<string, string> { ["$i64"] = value.ToString(CultureInfo.InvariantCulture) };
    private static uint Word(float value) => unchecked((uint)BitConverter.SingleToInt32Bits(value));
    private static object Capture(PlatformInputEdgeSnapshot state) => new { frame_index = Long(state.FrameIndex), reset_generation = Long(state.ResetGeneration),
        held_keys = state.HeldKeys.Select(k => new { key_code = k.KeyCode, value = k.Value }),
        consume_once_keys = state.ConsumeOnceKeys.Select(k => new { key_code = k.KeyCode, value = k.Value }),
        previous_joy_buttons = state.PreviousJoyButtons.Select(b => new { joypad = b.Joypad, button = b.Button, value = b.Value }),
        current_joy_buttons = state.CurrentJoyButtons.Select(b => new { joypad = b.Joypad, button = b.Button, value = b.Value }) };
}
