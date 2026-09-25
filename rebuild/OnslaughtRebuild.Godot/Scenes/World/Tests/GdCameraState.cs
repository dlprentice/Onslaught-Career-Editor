// SPDX-License-Identifier: GPL-3.0-or-later
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using Dictionary = Godot.Collections.Dictionary;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Test-only camera observer and pure compatibility bridge. A borrowed observer
/// reads the actual WorldPresentation camera without creating, replacing or
/// disposing that owner's state. The original constructor remains available
/// solely for the raw-word/pure-owner comparison cases.
/// </summary>
internal sealed class GdCameraState : IDisposable
{
    private readonly int _panDurationTicks;
    private readonly int _controlViewHandoffLeadTicks;
    private readonly float _nearPlane;
    private readonly float _farPlane;
    private readonly Node? _borrowedOwner;
    private GodotObject? _state;
    private bool _disposed;

    internal GdCameraState(int panDurationTicks, int controlViewHandoffLeadTicks, float nearPlane, float farPlane)
    {
        _panDurationTicks = panDurationTicks;
        _controlViewHandoffLeadTicks = controlViewHandoffLeadTicks;
        _nearPlane = nearPlane;
        _farPlane = farPlane;
    }

    internal GdCameraState(Node worldPresentation)
    {
        ArgumentNullException.ThrowIfNull(worldPresentation);
        _borrowedOwner = worldPresentation;
    }

    internal bool IsInitialized
    {
        get
        {
            if (IsDisposed) return false;
            if (_borrowedOwner is null) return _state is not null;
            using Variant state = _borrowedOwner.Get("_camera_state");
            return state.VariantType == Variant.Type.Object && GodotObject.IsInstanceValid(state.AsGodotObject());
        }
    }
    internal bool IsDisposed => _disposed || (_borrowedOwner is not null && !GodotObject.IsInstanceValid(_borrowedOwner));

    private GodotObject State
    {
        get
        {
            ObjectDisposedException.ThrowIf(IsDisposed, this);
            if (Engine.IsEditorHint())
                throw new InvalidOperationException("Live world camera state is unavailable during editor inspection.");
            if (_borrowedOwner is not null)
            {
                using Variant state = _borrowedOwner.Get("_camera_state");
                return state.VariantType == Variant.Type.Object && GodotObject.IsInstanceValid(state.AsGodotObject())
                    ? state.AsGodotObject()
                    : throw new InvalidOperationException("The production world camera has not been initialized.");
            }
            if (_state is not null) return _state;
            using Variant created = GD.Load<GDScript>("res://Client/world_camera.gd").New();
            GodotObject native = created.AsGodotObject()
                ?? throw new InvalidOperationException("Native world camera could not be instantiated.");
            try
            {
                RequireResult(native.Call("configure", _panDurationTicks, _controlViewHandoffLeadTicks,
                    Word(_nearPlane), Word(_farPlane)));
                _state = native;
                return native;
            }
            catch
            {
                native.Dispose();
                throw;
            }
        }
    }

    public void Advance(WorldSnapshot previous, WorldSnapshot current)
    {
        // Both null checks precede all current-frame work in the original API.
        ArgumentNullException.ThrowIfNull(previous);
        ArgumentNullException.ThrowIfNull(current);
        using Dictionary previousFacts = Facts(previous);
        using Dictionary currentFacts = Facts(current);
        RequireResult(State.Call("advance", previousFacts, currentFacts));
    }

    public (AttachedPanCameraViewSnapshot Camera, EngineViewpointSnapshot Viewpoint)
        SampleAndBind(float interpolationAlpha)
    {
        Dictionary value = Record(RequireResult(State.Call("sample_and_bind", Word(interpolationAlpha))), "value");
        return (ReadView(Record(value, "camera")), ReadViewpoint(Record(value, "viewpoint")));
    }

    public AttachedPanCameraSnapshot CurrentSnapshot => ReadSnapshot(
        Record(RequireResult(State.Call("current_snapshot")), "value"));

    public EngineViewpointSnapshot SelectedSnapshot => ReadViewpoint(
        Record(RequireResult(State.Call("selected_snapshot")), "value"));

    public string ComputeCameraHash() => String(RequireResult(State.Call("camera_hash")), "hex");
    public string ComputeViewpointHash() => String(RequireResult(State.Call("viewpoint_hash")), "hex");

    private static Dictionary Facts(WorldSnapshot world)
    {
        // One array in the frame batch, never one cross-language call per actor.
        // Names use UTF-16 units so NUL/unpaired-surrogate names cannot become
        // a different Player 1 identity through native String marshaling.
        Variant actors = default;
        if (world.Level100Actors?.Actors is { } sourceActors)
        {
            var rows = new Godot.Collections.Array();
            foreach (Level100ActorSnapshot? actor in sourceActors)
            {
                rows.Add(actor is null ? default(Variant) : Variant.From(new Dictionary
                {
                    ["name"] = actor.Name is null ? default(Variant) : Variant.From(actor.Name.Select(c => (int)c).ToArray()),
                    ["actor_id"] = actor.ActorId.Value,
                }));
            }
            actors = rows;
        }
        return new Dictionary
        {
            ["tick"] = world.Tick,
            ["opening_ticks_remaining"] = world.Level100OpeningTicksRemaining,
            ["zoom_permille"] = world.ZoomPermille,
            ["facing_yaw_micro_rad"] = world.FacingYawMicroRad,
            ["facing_pitch_micro_rad"] = world.FacingPitchMicroRad,
            ["body_roll_micro_rad"] = world.BodyRollMicroRad,
            ["player_position"] = new Dictionary { ["x"] = world.PlayerPosition.X, ["z"] = world.PlayerPosition.Z },
            ["player_elevation_millimeters"] = world.PlayerElevationMillimeters,
            ["actors"] = actors,
        };
    }

    private static AttachedPanCameraSnapshot ReadSnapshot(Dictionary value) => new(
        Int32(value, "pan_duration_ticks"), Int32(value, "control_view_handoff_tick"), Int32(value, "reset_generation"),
        (AttachedPanCameraUpdatePhase)Int32(value, "update_phase"), ReadFrame(Record(value, "previous_frame")),
        ReadFrame(Record(value, "current_frame")), ReadPose(Record(value, "previous_pan_pose")),
        ReadPose(Record(value, "current_pan_pose")), Boolean(value, "pan_update_scheduled"));

    private static AttachedPanCameraFrame ReadFrame(Dictionary value)
    {
        Variant item = Required(value, "attached_thing");
        AttachedCameraThingSnapshot? attached = null;
        if (item.VariantType != Variant.Type.Nil)
        {
            Dictionary thing = Record(value, "attached_thing");
            attached = new(new Level100ActorId(Int32(thing, "thing_id")), ReadPose(Record(thing, "pose")), ReadVector(Record(thing, "pan_right")));
        }
        return new(Int32(value, "event_frame"), Int32(value, "pan_elapsed_ticks"), Int32(value, "zoom_permille"), attached);
    }

    private static AttachedPanCameraViewSnapshot ReadView(Dictionary value) => new(
        NullableInt32(value, "attached_thing_id") is int id ? new Level100ActorId(id) : null,
        ReadPose(Record(value, "pose")), Single(value, "zoom_bits"), Boolean(value, "hud_visible"), Boolean(value, "opening_pan_active"));

    private static ClientCameraPose ReadPose(Dictionary value) => new(
        ReadVector(Record(value, "position")), ReadVector(Record(value, "forward")), ReadVector(Record(value, "up")));

    private static Level100RenderVector3 ReadVector(Dictionary value) => new(
        Single(value, "x_bits"), Single(value, "y_bits"), Single(value, "z_bits"));

    private static EngineViewpointSnapshot ReadViewpoint(Dictionary value)
    {
        Dictionary slot = Record(value, "selected_slot_state");
        Variant identity = Required(slot, "camera_identity");
        string? cameraIdentity = null;
        if (identity.VariantType != Variant.Type.Nil)
        {
            if (identity.VariantType != Variant.Type.PackedInt32Array)
                throw InvalidResult("Camera identity did not retain its UTF-16 carrier.");
            cameraIdentity = new string(identity.AsInt32Array().Select(unit => checked((char)unit)).ToArray());
        }
        return new(Int32(value, "selected_slot"), new EngineViewpointSlotState(cameraIdentity,
            NullableInt32(slot, "player_thing_identity"), ReadViewport(slot, "viewport")),
            ReadViewport(value, "current_viewport"), Single(value, "near_plane_bits"), Single(value, "far_plane_bits"));
    }

    private static EngineViewportValue? ReadViewport(Dictionary owner, string name)
    {
        if (Required(owner, name).VariantType == Variant.Type.Nil) return null;
        Dictionary value = Record(owner, name);
        return new(Int32(value, "width"), Int32(value, "height"), Int32(value, "x"), Int32(value, "y"),
            Single(value, "min_depth_bits"), Single(value, "max_depth_bits"));
    }

    private static Dictionary RequireResult(Variant returned)
    {
        if (returned.VariantType != Variant.Type.Dictionary)
            throw InvalidResult("The native camera operation did not complete with an explicit result.");
        Dictionary result = returned.AsGodotDictionary();
        if (Boolean(result, "ok")) return result;
        string kind = String(result, "error_type");
        string message = String(result, "error");
        string? parameter = result.ContainsKey("parameter") ? String(result, "parameter") : null;
        throw kind switch
        {
            "ArgumentNullException" => new ArgumentNullException(parameter, message),
            "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(parameter, message),
            "ArgumentException" => new ArgumentException(message, parameter),
            "OverflowException" => new OverflowException(message),
            _ => new InvalidOperationException(message),
        };
    }

    private static Variant Required(Dictionary value, string key) => value.TryGetValue(key, out Variant field)
        ? field : throw InvalidResult("Missing camera result field " + key + ".");
    private static Dictionary Record(Dictionary value, string key)
    {
        Variant field = Required(value, key);
        return field.VariantType == Variant.Type.Dictionary ? field.AsGodotDictionary()
            : throw InvalidResult("Camera result field " + key + " is not a record.");
    }
    private static bool Boolean(Dictionary value, string key)
    {
        Variant field = Required(value, key);
        return field.VariantType == Variant.Type.Bool ? field.AsBool()
            : throw InvalidResult("Camera result field " + key + " is not Boolean.");
    }
    private static string String(Dictionary value, string key)
    {
        Variant field = Required(value, key);
        return field.VariantType == Variant.Type.String ? field.AsString()
            : throw InvalidResult("Camera result field " + key + " is not a String.");
    }
    private static int Int32(Dictionary value, string key)
    {
        Variant field = Required(value, key);
        return field.VariantType == Variant.Type.Int ? checked((int)field.AsInt64())
            : throw InvalidResult("Camera result field " + key + " is not an exact integer.");
    }
    private static int? NullableInt32(Dictionary value, string key) =>
        Required(value, key).VariantType == Variant.Type.Nil ? null : Int32(value, key);
    private static float Single(Dictionary value, string key)
    {
        Variant field = Required(value, key);
        if (field.VariantType != Variant.Type.Int)
            throw InvalidResult("Camera result field " + key + " is not a raw float word.");
        return BitConverter.UInt32BitsToSingle(checked((uint)field.AsInt64()));
    }
    private static long Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static InvalidOperationException InvalidResult(string message) => new(message);

    public void Dispose()
    {
        if (_disposed) return;
        _state?.Dispose();
        _state = null;
        _disposed = true;
    }
}
