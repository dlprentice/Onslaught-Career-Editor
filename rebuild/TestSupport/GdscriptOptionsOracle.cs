// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using OnslaughtRebuild.Client;

// Public/synthetic options facts only. Current admitted Client laws are the
// temporary oracle. The controller below is a device-free extraction of the
// existing RetailFrontendFlow.Options.cs handlers, ending at the same frontend
// Back seam; it neither invents a preset nor touches host settings or devices.
internal static class GdscriptOptionsOracle
{
    private static readonly (string Name, string Property)[] SettingFields =
    [
        ("sound_volume", "SoundVolume"), ("music_volume", "MusicVolume"), ("mouse_sensitivity", "MouseSensitivity"),
        ("controller_configuration", "ControllerConfiguration"), ("invert_y_walker_player1", "InvertYWalkerPlayer1"),
        ("invert_y_walker_player2", "InvertYWalkerPlayer2"), ("invert_y_flight_player1", "InvertYFlightPlayer1"),
        ("invert_y_flight_player2", "InvertYFlightPlayer2"), ("overall_detail", "OverallDetail"),
        ("shadow_detail", "ShadowDetail"), ("geometry_detail", "GeometryDetail"), ("trilinear_mipmapping", "TrilinearMipmapping"),
        ("v_sync", "VSync"), ("landscape_resolution", "LandscapeResolution"), ("texture_resolution", "TextureResolution"),
        ("enable32_bit_textures", "Enable32BitTextures"), ("swap_speakers", "SwapSpeakers"), ("hardware_sound", "HardwareSound"),
        ("sound_quality", "SoundQuality"), ("sound_method3_d", "SoundMethod3D"),
    ];

    public static object Build()
    {
        var numeric = new List<object>();
        void N(string operation, object[] input, Func<object?> run) => numeric.Add(new { operation, input, expected = Capture(run) });
        var floats = new List<float> { float.NegativeInfinity, float.PositiveInfinity, float.NaN, -0f, 0f,
            float.MinValue, float.MaxValue, -1000f, -3f, -0.5f, 0.48f, 0.5f, 0.8f, 0.9f, 1f, 7f, 1000f };
        for (int index = -2; index <= 23; index++)
        {
            float value = index * 3f;
            floats.AddRange([MathF.BitDecrement(value), value, MathF.BitIncrement(value)]);
            float volume = (index - 0.48f + 0.5f) / 10f;
            floats.AddRange([MathF.BitDecrement(volume), volume, MathF.BitIncrement(volume)]);
        }
        foreach (float value in floats)
        {
            N("mouse_index", [Word(value)], () => RetailOptionsMenu.MouseSensitivityIndex(value));
            N("volume_index", [Word(value)], () => RetailOptionsMenu.VolumeIndex(value));
            N("pulse_channel", [Word(value)], () => RetailOptionsApplyPulse.Channel(value));
            foreach (bool pending in new[] { false, true })
                N("pulse_color", [pending, Word(value)], () => RetailOptionsApplyPulse.PackedColor(pending, value));
        }
        int[] words = [int.MinValue, int.MinValue + 1, -1023, -21, -3, -1, 0, 1, 2, 3, 10, 20, 21, 31, 320, 641, int.MaxValue];
        foreach (int value in words)
        {
            N("mouse_value", [value], () => Word(RetailOptionsMenu.MouseSensitivityValue(value)));
            N("volume_value", [value], () => Word(RetailOptionsMenu.VolumeValue(value)));
            N("integer_half", [value], () => RetailOptionsMenuItemDest.IntegerHalf(value));
            N("dropdown_width", [value], () => RetailOptionsDropdownDest.Width(value));
            N("panel_width", [value], () => Word(RetailOptionsDropdownPanelDest.Width(value)));
            foreach (float x in new[] { -9.25f, -0f, 0f, 4.999f, 5f, 319f, 320.25f })
            {
                N("item_x", [Word(x), value], () => Word(RetailOptionsMenuItemDest.DestX(x, value)));
                N("item_scale", [Word(x), value], () => Word(RetailOptionsMenuItemDest.Scale(x, value)));
                N("icon_x", [Word(x), value], () => Word(RetailOptionsMenuItemIconDest.DestX(x, value)));
                N("icon_scale", [Word(x), value], () => Word(RetailOptionsMenuItemIconDest.Scale(x, value)));
                N("hit_right", [Word(x), value], () => Word(RetailOptionsDropdownListClick.Right(x, value)));
                N("dropdown_x", [Word(x), value], () => Word(RetailOptionsDropdownDest.DestX(x, value)));
                N("dropdown_scale", [Word(x), value], () => Word(RetailOptionsDropdownDest.Scale(x, value)));
            }
        }
        foreach (float x in new[] { -319f, -0f, 0f, 319f, 33554432f })
        {
            N("value_x", [Word(x)], () => Word(RetailOptionsDropdownValueDest.DestX(x)));
            N("list_x", [Word(x)], () => Word(RetailOptionsDropdownListDest.DestX(x)));
        }
        (int Count, int Pitch)[] dimensions = [(0, 16), (1, 16), (3, 16), (31, 16), (41, 17), (-3, 16),
            (3, -17), (int.MinValue, -1), (int.MaxValue, 16), (int.MaxValue, int.MaxValue)];
        foreach (var size in dimensions)
            foreach (float y in new[] { -5f, -0f, 5f, 195f, 479f, 500f })
            {
                N("panel_y", [Word(y), size.Count, size.Pitch], () => Word(RetailOptionsDropdownPanelDest.DestY(y, size.Count, size.Pitch)));
                N("list_scale", [size.Count, size.Pitch], () => Word(RetailOptionsDropdownListDestY.Scale(size.Count, size.Pitch)));
                foreach (int index in new[] { int.MinValue, -1, 0, 1, 3, int.MaxValue })
                {
                    N("list_y", [Word(y), size.Count, size.Pitch, index], () => Word(RetailOptionsDropdownListDestY.DestY(y, size.Count, size.Pitch, index)));
                    N("hit_bottom", [Word(y), size.Count, size.Pitch, index], () => Word(RetailOptionsDropdownListHover.Bottom(y, size.Count, size.Pitch, index)));
                }
            }
        foreach (float x in new[] { 322.999f, 323f, 422.999f, 423f, float.NaN })
            foreach (float y in new[] { 178.999f, 179f, 194.999f, 195f, float.NaN })
                N("contains", [Word(x), Word(y), Word(323f), Word(179f), 100, 16],
                    () => RetailOptionsDropdownListHover.Contains(x, y, 323f, 179f, 100, 16));
        foreach (int index in new[] { int.MinValue, -1, 0, 1, int.MaxValue })
            foreach (int current in new[] { -1, 0, 1 })
            {
                N("list_color", [index, current], () => RetailOptionsDropdownListColor.PackedColor(index, current));
                N("row_is_pending", [index, current], () => RetailOptionsApplyPulse.DropdownRowIsPending(index, current));
                foreach (bool flag in new[] { false, true })
                {
                    N("hit_index", [current, index, flag], () => RetailOptionsDropdownListClick.CurrentIndexAfterClick(current, index, flag));
                    N("cancel_index", [current, index, flag], () => RetailOptionsDropdownListCancel.CurrentIndexAfterCancel(current, index, flag));
                }
                foreach (byte pending in new byte[] { 0, 1, 127, 128, 255 })
                    N("applies_live", [pending, current, index], () => RetailOptionsDropdownListClick.AppliesLive(pending, current, index));
                N("helper_nonzero", [index, current], () => RetailOptionsDropdownListCancel.HelperNonzero(index, current));
            }
        foreach (bool first in new[] { false, true })
            foreach (bool second in new[] { false, true })
            {
                N("cancel_applies", [first, second], () => RetailOptionsDropdownListCancel.Applies(first, second));
                N("should_pulse", [first], () => RetailOptionsApplyPulse.ShouldPulse(first));
                N("click_sound_applies", [second], () => RetailOptionsDropdownListClickSound.Applies(second));
                N("expand_after_click", [first, second], () => RetailOptionsDropdownListClick.ExpandAfterClick(first, second));
                N("expand_after_cancel", [first, second], () => RetailOptionsDropdownListCancel.ExpandAfterCancel(first, second));
                foreach (uint incoming in new uint[] { 0, 0xffffffff, 0x80808080, 0x01020408 })
                    N("menu_color", [first, second, incoming], () => RetailOptionsMenuItemColor.PackedColor(first, second, incoming));
            }

        var scenarios = new List<object>();
        void Done(Scenario value) => scenarios.Add(value.Output());
        foreach (RetailOptionsPage page in Enum.GetValues<RetailOptionsPage>())
        {
            var s = new Scenario("page-navigation-" + page);
            s.Step("enter", (int)page);
            for (int index = 0; index < s.Menu.Rows.Count + 2; index++) s.Step("move", 1);
            s.Step("move", int.MinValue); s.Step("move", 0); s.Step("hover", -1); s.Step("hover", int.MaxValue);
            foreach (int index in new[] { int.MinValue, -1, 0, s.Menu.Rows.Count - 1, s.Menu.Rows.Count, s.Menu.Rows.Count + 1, int.MaxValue }) s.Step("top", index);
            foreach (float y in new[] { MathF.BitDecrement(s.Menu.FirstRowTop), s.Menu.FirstRowTop,
                MathF.BitIncrement(s.Menu.FirstRowTop), s.Menu.FirstRowTop + s.Menu.PageHeight, float.NaN, float.PositiveInfinity })
                s.Step("at", value: Word(y));
            s.Step("back"); s.Step("reset"); Done(s);
        }
        foreach ((RetailOptionsPage page, int row) in new[] { (RetailOptionsPage.Controller, 0), (RetailOptionsPage.Sound, 0), (RetailOptionsPage.Sound, 1) })
        {
            var s = new Scenario($"slider-ends-{page}-{row}"); s.Step("enter", (int)page); s.Step("hover", row);
            for (int index = 0; index < 24; index++) s.Step("adjust", -1);
            for (int index = 0; index < 24; index++) s.Step("adjust", 1);
            s.Step("sync"); Done(s);
        }
        foreach ((RetailOptionsPage page, int row) in new[] { (RetailOptionsPage.Controller, 1), (RetailOptionsPage.Video, 7),
            (RetailOptionsPage.Sound, 2), (RetailOptionsPage.Sound, 4), (RetailOptionsPage.Video, 2) })
        {
            var s = new Scenario($"commit-hover-cancel-{page}-{row}", RichHost());
            s.Step("enter", (int)page); s.Step("hover", row); s.Step("adjust", 1); s.Step("hover_state", 0);
            s.Step("cancel"); s.Step("confirm"); s.Step("select", 1); s.Step("back");
            s.Step("apply"); s.Step("confirm"); s.Step("hover_state", 0); s.Step("confirm");
            s.Step("back"); s.Step("enter", (int)page); s.Step("hover", row); s.Step("adjust", 1);
            s.Step("confirm"); s.Step("apply"); s.Step("sync"); Done(s);
        }
        foreach (int recommended in new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue })
        {
            var s = new Scenario("recommendation-" + recommended, RichHost() with
                { RecommendedTextureResolution = recommended, RecommendedEnable32BitTextures = recommended });
            s.Step("enter", 2);
            foreach (int row in new[] { 9, 10 })
            {
                foreach (int index in new[] { -2, 0, 1, 2, 99 }) s.Step("label", row, index);
                s.Step("hover", row); s.Step("adjust", 1); s.Step("confirm"); s.Step("apply");
            }
            Done(s);
        }
        foreach (bool nullLists in new[] { false, true })
        {
            string[]? states = nullLists ? null : [];
            var s = new Scenario("malformed-host-lists-" + nullLists, new(states!, states!, states!, states!));
            s.Step("enter", 2); s.Step("hover", 2); s.Step("label", 2, 0); s.Step("hover_state", -1);
            s.Step("select", 0); s.Step("adjust", 1); s.Step("hover_state", -1); s.Step("hover_state", 0);
            s.Step("select", -1); s.Step("select", 0); s.Step("cancel"); s.Step("confirm");
            s.Step("back"); s.Step("enter", 3); s.Step("hover", 5); s.Step("adjust", -1); s.Step("reset"); Done(s);
        }
        var raw = new Scenario("raw-host-labels", new(["A\0B", "\ufeffhead", "\ud800", null!], ["same", "same"], ["None"], ["Device"]));
        raw.Step("enter", 2); raw.Step("hover", 2); raw.Step("confirm");
        for (int index = -1; index <= 4; index++) { raw.Step("label", 2, index); raw.Step("select", index); }
        raw.Step("confirm"); Done(raw);
        foreach (int value in new[] { int.MinValue, -1, 5, int.MaxValue })
        {
            var s = new Scenario("invalid-page-order-" + value); s.Step("enter", 3); s.Step("hover", 4); s.Step("adjust", 1);
            s.Step("enter", value); s.Step("move", 0); s.Step("adjust", 0); s.Step("hover", -1); s.Step("select", -1);
            s.Step("cancel"); s.Step("apply"); s.Step("sync"); s.Step("top", -1); s.Step("back"); s.Step("reset"); Done(s);
        }
        var external = new Scenario("external-setting-sync-and-wrapped-dropdown");
        foreach ((string name, _) in SettingFields)
        {
            PropertyInfo property = SettingProperty(name);
            if (property.PropertyType == typeof(bool)) external.Step("set", setting: name, value: true);
            else if (property.PropertyType == typeof(float)) external.Step("set", setting: name, value: Word(float.NaN));
            else external.Step("set", setting: name, value: int.MaxValue);
        }
        external.Step("sync"); external.Step("enter", 1); external.Step("hover", 1); external.Step("adjust", 1);
        external.Step("select", 0); external.Step("confirm"); external.Step("apply"); external.Step("reset"); Done(external);
        var varied = new Scenario("varied-state-operations", RichHost());
        uint random = 0x4f505453;
        uint Next() => random = unchecked(random * 1664525u + 1013904223u);
        string[] operations = ["enter", "move", "hover", "adjust", "confirm", "back", "hover_state", "select", "cancel", "apply", "sync", "reset"];
        for (int index = 0; index < 128; index++)
        {
            string operation = operations[(int)(Next() % (uint)operations.Length)];
            int value = operation == "enter" ? (int)(Next() % 4) : (int)(Next() % 19) - 3;
            varied.Step(operation, value);
        }
        Done(varied);

        var controllers = new List<object>();
        var keys = new Scenario("key-precedence-and-commit", RichHost());
        keys.Step("enter", 1);
        for (int mask = 0; mask < 64; mask++) keys.Control("key", mask);
        controllers.Add(keys.Output());
        foreach (int page in new[] { 1, 2, 3 })
        {
            var s = new Scenario("pointer-page-" + page, RichHost()); s.Step("enter", page);
            float top = s.Menu.FirstRowTop;
            foreach ((float x, float y) in new[] { (0f, top), (400f, top), (639f, top), (323f, top + 20f),
                (323f, top + 35f), (422.999f, top + 35f), (423f, top + 35f), (640f, 0f),
                (45.999f, 430f), (46f, 430f), (0f, 478f), (0f, 477.999f) })
            {
                s.Control("motion", x: x, y: y); s.Control("click", x: x, y: y);
                s.Control("cancel", 0); s.Control("cancel", 1);
            }
            controllers.Add(s.Output());
        }
        var popup = new Scenario("tall-popup-hit-boundaries", RichHost() with { ScreenModes = Enumerable.Range(0, 40).Select(i => "Mode " + i).ToArray() });
        popup.Step("enter", 2); popup.Step("hover", 2); popup.Step("confirm");
        foreach ((float x, float y) in new[] { (322.999f, 0f), (323f, 0f), (423f, 16f), (422.999f, 16f), (323f, 479f), (323f, 480f) })
            popup.Control("motion", x: x, y: y);
        popup.Control("cancel", 1); popup.Step("confirm"); popup.Control("click", x: 0f, y: 0f); controllers.Add(popup.Output());
        var brokenPopup = new Scenario("null-popup-failure", new(null!, [], [], []));
        brokenPopup.Step("enter", 2); brokenPopup.Step("hover", 2); brokenPopup.Step("confirm");
        brokenPopup.Control("motion", x: 323f, y: 0f); brokenPopup.Control("click", x: 0f, y: 0f);
        brokenPopup.Control("cancel", 1); brokenPopup.Control("key", 32); brokenPopup.Control("key", 32); controllers.Add(brokenPopup.Output());

        var bindings = new List<object>();
        for (int flags = 0; flags < 16; flags++)
        {
            var menu = new RetailOptionsMenu();
            menu.Settings.InvertYWalkerPlayer1 = (flags & 1) != 0; menu.Settings.InvertYWalkerPlayer2 = (flags & 2) != 0;
            menu.Settings.InvertYFlightPlayer1 = (flags & 4) != 0; menu.Settings.InvertYFlightPlayer2 = (flags & 8) != 0;
            bindings.Add(new { flags, expected = RetailControlBindings.Rows.Select(row =>
            {
                string left = row.Slot0, right = row.Slot1;
                if (row.Kind == RetailControlBindingRowKind.InvertWalker)
                { left = RetailControlBindings.InvertYLabel(menu.Settings.InvertYWalkerPlayer1); right = RetailControlBindings.InvertYLabel(menu.Settings.InvertYWalkerPlayer2); }
                else if (row.Kind == RetailControlBindingRowKind.InvertFlight)
                { left = RetailControlBindings.InvertYLabel(menu.Settings.InvertYFlightPlayer1); right = RetailControlBindings.InvertYLabel(menu.Settings.InvertYFlightPlayer2); }
                return new { action_code = row.ActionCode, kind = (int)row.Kind, label = row.Label, slot0 = left, slot1 = right };
            }).ToArray() });
        }
        return new { numeric, scenarios, controllers, bindings, constants = new {
            row_height = Word(RetailOptionsMenu.RowHeight), bindings_row_height = Word(RetailOptionsMenu.BindingsRowHeight),
            joystick_row_height = Word(RetailOptionsMenu.JoystickRowHeight), range_origin_y = Word(RetailOptionsMenu.RangeOriginY),
            range_top_inset = Word(RetailOptionsMenu.RangeTopInset), mouse_sensitivity_step = Word(RetailOptionsMenu.MouseSensitivityStep),
            mouse_sensitivity_max_value = RetailOptionsMenu.MouseSensitivityMaxValue,
            default_mouse_sensitivity = Word(RetailOptionsMenu.DefaultMouseSensitivity), volume_max_value = RetailOptionsMenu.VolumeMaxValue,
            value_row_seed_bias = Word(RetailOptionsMenu.ValueRowSeedBias) } };
    }

    private static RetailOptionsHostCapabilities RichHost() => new(["640 x 480", "1280 x 720", "1920 x 1080"],
        ["Synthetic adapter A", "Synthetic adapter B"], ["None", "2", "4"], ["Synthetic device A", "Synthetic device B"]);
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static float Float(object? value) => BitConverter.UInt32BitsToSingle(Convert.ToUInt32(value));
    private static int[]? Units(string? value) => value?.Select(c => (int)c).ToArray();
    private static object? Texts(IReadOnlyList<string>? values) => values?.Select(Units).ToArray();
    private static object? Host(RetailOptionsHostCapabilities? host) => host is null ? null : new {
        screen_modes = Texts(host.ScreenModes), video_adapters = Texts(host.VideoAdapters), anti_aliasing_levels = Texts(host.AntiAliasingLevels),
        sound_devices = Texts(host.SoundDevices), recommended_texture_resolution = host.RecommendedTextureResolution,
        recommended_enable32_bit_textures = host.RecommendedEnable32BitTextures };
    private static PropertyInfo SettingProperty(string name) => typeof(RetailOptionsSettings).GetProperty(SettingFields.Single(field => field.Name == name).Property)!;
    private static object Capture(Func<object?> operation)
    {
        try { return new { ok = true, value = operation() }; }
        catch (Exception error)
        {
            if (error is TargetInvocationException wrapper && wrapper.InnerException is not null) error = wrapper.InnerException;
            return new { ok = false, error_type = error.GetType().Name, parameter = (error as ArgumentException)?.ParamName ?? "" };
        }
    }
    private static object Row(RetailOptionsRow row) => new { kind = (int)row.Kind, label = row.Label, states = Texts(row.States),
        timing = (int)row.Timing, height = Word(row.Height), target_page = (int)row.TargetPage, action = (int)row.Action,
        max_value = row.MaxValue, current_index = row.CurrentIndex, committed_index = row.CommittedIndex,
        recommended_index = row.RecommendedIndex, recommended_states = Texts(row.RecommendedStates), is_selectable = row.IsSelectable,
        current_state = Capture(() => Units(row.CurrentState)) };
    private static object Snapshot(RetailOptionsMenu menu)
    {
        var settings = new Dictionary<string, object?>();
        foreach ((string name, string property) in SettingFields)
        {
            object? value = typeof(RetailOptionsSettings).GetProperty(property)!.GetValue(menu.Settings);
            settings[name] = value is float single ? Word(single) : value;
        }
        var pages = new List<object>();
        foreach (string field in new[] { "_root", "_controller", "_video", "_sound" })
        {
            var rows = (IReadOnlyList<RetailOptionsRow>)typeof(RetailOptionsMenu).GetField(field, BindingFlags.Instance | BindingFlags.NonPublic)!.GetValue(menu)!;
            pages.Add(rows.Select(row => new { current_index = row.CurrentIndex, committed_index = row.CommittedIndex }).ToArray());
        }
        return new { page = (int)menu.Page, selected_index = menu.SelectedIndex, is_expanded = menu.IsExpanded, settings, pages,
            rows = Capture(() => menu.Rows.Select(Row).ToArray()), selected_row = Capture(() => Row(menu.SelectedRow)),
            has_pending_changes = Capture(() => menu.HasPendingChanges), page_height = Capture(() => Word(menu.PageHeight)),
            first_row_top = Capture(() => Word(menu.FirstRowTop)) };
    }

    private sealed class Scenario
    {
        public RetailOptionsMenu Menu { get; }
        private readonly string name;
        private readonly RetailOptionsHostCapabilities? host;
        private readonly object initial;
        private readonly List<object> steps = [];
        private readonly Controller controller;
        public Scenario(string name, RetailOptionsHostCapabilities? host = null)
        { this.name = name; this.host = host; Menu = new(host); initial = Snapshot(Menu); controller = new(Menu); }
        public void Step(string operation, int a = 0, int b = 0, string setting = "", object? value = null)
        {
            object expected = Capture(() =>
            {
                switch (operation)
                {
                    case "enter": Menu.Enter((RetailOptionsPage)a); return null;
                    case "reset": Menu.Reset(); return null;
                    case "move": return Menu.MoveSelection(a);
                    case "hover": return Menu.Hover(a);
                    case "hover_state": return Menu.HoverState(a);
                    case "cancel": return Menu.CancelExpanded();
                    case "adjust": return Menu.Adjust(a);
                    case "confirm": return (int)Menu.Confirm();
                    case "back": return (int)Menu.Back();
                    case "apply": Menu.ApplyPage(); return null;
                    case "sync": Menu.SyncFromSettings(); return null;
                    case "select": return Menu.SelectState(a);
                    case "top": return Word(Menu.RowTop(a));
                    case "at": return Menu.RowAt(Float(value));
                    case "label": return Units(Menu.Rows[a].StateLabel(b));
                    case "set":
                        PropertyInfo property = SettingProperty(setting);
                        property.SetValue(Menu.Settings, property.PropertyType == typeof(float) ? Float(value) : value);
                        return null;
                    default: throw new InvalidOperationException("Unknown options fixture operation.");
                }
            });
            steps.Add(new { operation, a, b, setting, value, expected, snapshot = Snapshot(Menu) });
        }
        public void Control(string operation, int mask = 0, float x = 0f, float y = 0f, float width = 100f)
        {
            controller.Effects.Clear();
            object expected = Capture(() => operation switch {
                "key" => controller.Key(mask), "motion" => controller.Motion(x, y, width),
                "click" => controller.Click(x, y, width), "cancel" => controller.Cancel(mask != 0),
                _ => throw new InvalidOperationException("Unknown options controller operation.") });
            steps.Add(new { operation = "controller_" + operation, mask, x = Word(x), y = Word(y), width = Word(width),
                expected, effects = controller.Effects.ToArray(), snapshot = Snapshot(Menu) });
        }
        public object Output() => new { name, host = Host(host), initial, steps };
    }

    private sealed class Controller(RetailOptionsMenu menu)
    {
        public List<object> Effects { get; } = [];
        private void Audio(int cue) => Effects.Add(new { kind = "audio", cue });
        private void Effect(string kind) => Effects.Add(new { kind });
        private bool Notify(bool changed)
        { if (changed) { Audio(0); Effect("apply_settings"); Effect("redraw"); } return true; }
        private bool Confirm()
        {
            RetailOptionsSignal signal = menu.Confirm();
            if (signal == RetailOptionsSignal.None) return true;
            if (signal == RetailOptionsSignal.Closed) return Back();
            Audio(1); Effect("apply_settings"); Effect("redraw"); return true;
        }
        private bool Back()
        {
            RetailOptionsSignal signal = menu.Back();
            if (signal is RetailOptionsSignal.PageChanged or RetailOptionsSignal.ValueChanged) { Audio(2); Effect("redraw"); }
            else Effect("frontend_back");
            return true;
        }
        public bool Key(int mask)
        {
            if ((mask & 1) != 0) return Notify(menu.MoveSelection(-1));
            if ((mask & 2) != 0) return Notify(menu.MoveSelection(1));
            if ((mask & 4) != 0) return Notify(menu.Adjust(-1));
            if ((mask & 8) != 0) return Notify(menu.Adjust(1));
            if ((mask & 16) != 0) return Confirm();
            if ((mask & 32) != 0) return Back();
            return false;
        }
        private int Hit(float x, float y, float width)
        {
            RetailOptionsRow row = menu.SelectedRow;
            float top = menu.RowTop(menu.SelectedIndex);
            int labelCx = (int)width;
            for (int index = 0; index < row.States.Count; index++)
                if (RetailOptionsDropdownListHover.Contains(x, y, RetailOptionsDropdownListDest.DestX(319f),
                    RetailOptionsDropdownListDestY.DestY(top, row.States.Count, 16, index), labelCx, 16)) return index;
            return -1;
        }
        public bool Motion(float x, float y, float width)
        {
            if (menu.IsExpanded)
            {
                int index = Hit(x, y, width);
                if (index < 0 || !menu.HoverState(index)) return false;
                Audio(0); return true;
            }
            int row = menu.RowAt(y);
            if (row < 0 || !menu.Hover(row)) return false;
            Audio(0); return true;
        }
        public bool Click(float x, float y, float width)
        {
            if (x >= 0f && x < 46f && y >= 430f && y < 478f) return Back();
            if (menu.IsExpanded)
            {
                int hit = Hit(x, y, width);
                if (hit >= 0) menu.SelectState(hit);
                return Confirm();
            }
            int index = menu.RowAt(y);
            if (index < 0) return false;
            RetailOptionsRow row = menu.Rows[index];
            if (!row.IsSelectable) return false;
            if (menu.Hover(index)) Audio(0);
            if (row.Kind == RetailOptionsRowKind.ValueBar)
            {
                float left = 320f - ((width + 6f + 103f) * 0.5f);
                float leftArrow = left + width + 6f;
                float bar = leftArrow + 13f;
                if (x < bar) return Notify(menu.Adjust(-1));
                if (x >= bar + 81f) return Notify(menu.Adjust(1));
                return true;
            }
            return Confirm();
        }
        public bool Cancel(bool down)
        {
            if (!RetailOptionsDropdownListCancel.Applies(false, down) || !menu.CancelExpanded()) return false;
            Audio(2); Effect("redraw"); return true;
        }
    }
}
