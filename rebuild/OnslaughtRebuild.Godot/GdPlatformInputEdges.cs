// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using A = Godot.Collections.Array;
using D = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary managed host boundary for Client/platform_input_edges.gd. The
/// native RefCounted is the sole byte/counter owner; this adapter only marshals
/// event/frame operations and detached snapshots. InteractiveSession borrows
/// this object, so the creating host must dispose it after its last session use.
/// Retail repeat policy and joystick polling cadence remain unresolved, as in
/// PlatformInputEdgeState; this bridge adds no input sampling or timing owner.
/// </summary>
public sealed class GdPlatformInputEdges : IPlatformInputEdges, IDisposable
{
    private GodotObject? _state;
    private bool _disposed;

    public GdPlatformInputEdges()
    {
        using GDScript script = GD.Load<GDScript>("res://Client/platform_input_edges.gd")
            ?? throw new InvalidOperationException("The native platform-input owner is unavailable.");
        using Variant created = script.New();
        if (created.VariantType != Variant.Type.Object || created.AsGodotObject() is not RefCounted owner)
            throw new InvalidOperationException("The native platform-input owner must be a RefCounted.");
        _state = owner;
        try
        {
            foreach (string method in new[] { "get_frame_index", "get_reset_generation", "observe_key",
                "get_held_key", "consume_key_once", "observe_joy_button", "get_previous_joy_button",
                "get_current_joy_button", "is_joy_button_rising", "is_joy_button_held", "is_joy_button_falling",
                "advance_frame", "reset", "capture" })
                if (!owner.HasMethod(method)) throw new InvalidOperationException("Missing native input method: " + method);
        }
        catch
        {
            Dispose();
            throw;
        }
    }

    public long FrameIndex => Counter("get_frame_index");
    public long ResetGeneration => Counter("get_reset_generation");

    public void ObserveKey(int keyCode, bool pressed, bool echo)
    {
        using D result = Result("observe_key", keyCode, pressed, echo);
    }

    public byte GetHeldKey(int keyCode) => ByteResult("get_held_key", keyCode);
    public byte ConsumeKeyOnce(int keyCode) => ByteResult("consume_key_once", keyCode);

    public void ObserveJoyButton(int joypad, int button, byte value)
    {
        // Explicit integer transport retains 0x80/0xff as unsigned byte values.
        using D result = Result("observe_joy_button", joypad, button, (int)value);
    }

    public byte GetPreviousJoyButton(int joypad, int button) => ByteResult("get_previous_joy_button", joypad, button);
    public byte GetCurrentJoyButton(int joypad, int button) => ByteResult("get_current_joy_button", joypad, button);
    public bool IsJoyButtonRising(int joypad, int button) => BoolResult("is_joy_button_rising", joypad, button);
    public bool IsJoyButtonHeld(int joypad, int button) => BoolResult("is_joy_button_held", joypad, button);
    public bool IsJoyButtonFalling(int joypad, int button) => BoolResult("is_joy_button_falling", joypad, button);
    public void AdvanceFrame() => VoidCall("advance_frame");
    public void Reset() => VoidCall("reset");

    public PlatformInputEdgeSnapshot Capture()
    {
        using Variant value = Call("capture");
        using D snapshot = Dictionary(value, "capture");
        return new PlatformInputEdgeSnapshot(
            Integer(Field(snapshot, "frame_index"), "frame_index"),
            Integer(Field(snapshot, "reset_generation"), "reset_generation"),
            Keys(Field(snapshot, "held_keys"), "held_keys"),
            Keys(Field(snapshot, "consume_once_keys"), "consume_once_keys"),
            JoyButtons(Field(snapshot, "previous_joy_buttons"), "previous_joy_buttons"),
            JoyButtons(Field(snapshot, "current_joy_buttons"), "current_joy_buttons"));
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;
        GodotObject? owner = _state;
        _state = null;
        owner?.Dispose();
    }

    private Variant Call(string method, params Variant[] arguments)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);
        if (_state is null || !GodotObject.IsInstanceValid(_state))
            throw new InvalidOperationException("The native platform-input owner was released outside its host lifetime.");
        return _state.Call(method, arguments);
    }

    private D Result(string method, params Variant[] arguments)
    {
        using Variant value = Call(method, arguments);
        D result = Dictionary(value, method);
        try
        {
            if (!Boolean(Field(result, "ok"), method + ".ok"))
            {
                string type = Text(Field(result, "error_type"), method + ".error_type");
                string message = Text(Field(result, "error"), method + ".error");
                if (type == nameof(ArgumentException)) throw new ArgumentException(message);
                throw new InvalidOperationException($"Native platform input {method} failed ({type}): {message}");
            }
            return result;
        }
        catch
        {
            result.Dispose();
            throw;
        }
    }

    private long Counter(string method)
    {
        using Variant value = Call(method);
        // Godot's integer Variant is signed Int64. Never pass through Int32 or
        // floating point, including values beyond 2^53 and wrapped counters.
        return Integer(value, method);
    }

    private void VoidCall(string method)
    {
        using Variant value = Call(method);
        if (value.VariantType != Variant.Type.Nil) throw Invalid(method, "void result");
    }

    private byte ByteResult(string method, params Variant[] arguments)
    {
        using D result = Result(method, arguments);
        return Byte(Field(result, "value"), method);
    }

    private bool BoolResult(string method, params Variant[] arguments)
    {
        using D result = Result(method, arguments);
        return Boolean(Field(result, "value"), method);
    }

    private static IReadOnlyList<PlatformInputKeyByte> Keys(Variant value, string name)
    {
        using A rows = Rows(value, name);
        var detached = new PlatformInputKeyByte[rows.Count];
        for (int index = 0; index < detached.Length; index++)
        {
            using D row = Dictionary(rows[index], name);
            int key = Int32(Field(row, "key_code"), name + ".key_code");
            byte state = Byte(Field(row, "value"), name + ".value");
            if (state == 0 || (index > 0 && detached[index - 1].KeyCode >= key))
                throw Invalid(name, "nonzero sparse bytes in strict signed key order");
            detached[index] = new(key, state);
        }
        return Array.AsReadOnly(detached);
    }

    private static IReadOnlyList<PlatformInputJoyButtonByte> JoyButtons(Variant value, string name)
    {
        using A rows = Rows(value, name);
        var detached = new PlatformInputJoyButtonByte[rows.Count];
        for (int index = 0; index < detached.Length; index++)
        {
            using D row = Dictionary(rows[index], name);
            int joypad = Int32(Field(row, "joypad"), name + ".joypad");
            int button = Int32(Field(row, "button"), name + ".button");
            byte state = Byte(Field(row, "value"), name + ".value");
            if (state == 0 || (index > 0 && (detached[index - 1].Joypad > joypad ||
                (detached[index - 1].Joypad == joypad && detached[index - 1].Button >= button))))
                throw Invalid(name, "nonzero sparse bytes in strict signed joypad/button order");
            detached[index] = new(joypad, button, state);
        }
        return Array.AsReadOnly(detached);
    }

    private static Variant Field(D dictionary, string field) => dictionary.TryGetValue(field, out Variant value)
        ? value : throw new InvalidDataException("Native platform input omitted " + field + ".");
    private static D Dictionary(Variant value, string name) => value.VariantType == Variant.Type.Dictionary
        ? value.AsGodotDictionary() : throw Invalid(name, "Dictionary");
    private static A Rows(Variant value, string name) => value.VariantType == Variant.Type.Array
        ? value.AsGodotArray() : throw Invalid(name, "Array");
    private static long Integer(Variant value, string name) => value.VariantType == Variant.Type.Int
        ? value.AsInt64() : throw Invalid(name, "Int64");
    private static bool Boolean(Variant value, string name) => value.VariantType == Variant.Type.Bool
        ? value.AsBool() : throw Invalid(name, "Boolean");
    private static string Text(Variant value, string name) => value.VariantType == Variant.Type.String
        ? value.AsString() : throw Invalid(name, "String");
    private static int Int32(Variant value, string name)
    {
        long integer = Integer(value, name);
        return integer is >= int.MinValue and <= int.MaxValue ? (int)integer : throw Invalid(name, "Int32 range");
    }
    private static byte Byte(Variant value, string name)
    {
        long integer = Integer(value, name);
        return integer is >= byte.MinValue and <= byte.MaxValue ? (byte)integer : throw Invalid(name, "byte range");
    }
    private static InvalidDataException Invalid(string name, string expected) =>
        new($"Native platform input {name} did not return {expected}.");
}
