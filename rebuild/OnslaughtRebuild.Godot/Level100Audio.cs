// SPDX-License-Identifier: GPL-3.0-or-later
using System.Runtime.ExceptionServices;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

// Temporary Core/host boundary. The authored native scene owns every player,
// recipe, queue, fade and music policy; this class carries one ordered frame
// batch and the existing shared shutdown observer, with no audio state machine.
public sealed partial class Level100Audio : Node3D
{
    internal AudioPlaybackRetirement PlaybackRetirement { get; set; } = null!;
    private Node3D? _native;

    public override void _Ready()
    {
        Name = "Level100AudioHost";
        ProcessMode = ProcessModeEnum.Always;
        SetProcess(false);
        if (Engine.IsEditorHint()) return;
        _native = GD.Load<PackedScene>("res://Scenes/Audio/Level100Audio.tscn").Instantiate<Node3D>();
        AddChild(_native);
        Invoke("configure", Callable.From<Node>(ObservePlayback));
    }

    private void ObservePlayback(Node player)
    {
        // The same observer is shared with startup media and FirstFlightGame's
        // quit drain. It disposes transient managed playback bindings promptly.
        if (player is AudioStreamPlayer flat) PlaybackRetirement.Observe(flat);
        else if (player is AudioStreamPlayer3D spatial) PlaybackRetirement.Observe(spatial);
        else throw new InvalidOperationException("Audio start did not supply its native player.");
    }

    public Level100MessagePlaybackState CharacterMessagePlayback
    {
        get
        {
            D value = Native.Call("character_message_playback").AsGodotDictionary();
            return new(OptionalInt(value["active_speaker_id"]), OptionalInt(value["active_message_id"]),
                value["position_seconds"].AsDouble(), value["length_seconds"].AsDouble(),
                value["playing"].AsBool(), value["paused"].AsBool());
        }
    }
    public bool TutorialVoicePlaying => Native.Call("tutorial_voice_playing").AsBool();
    public bool TutorialMusicPlaying => Native.Call("tutorial_music_playing").AsBool();
    public bool FrontendMusicPlaying => Native.Call("frontend_music_playing").AsBool();
    public void StartTutorialMusic() => Invoke("start_tutorial_music");
    public void StartFrontendMusic() => Invoke("start_frontend_music");
    public void StopTutorialMusic() => Invoke("stop_music");
    public void StopFrontendMusic() => Invoke("stop_music");
    public void BindAquila(Level100ActorId actorId, Level100ActorRegistrySnapshot actors) =>
        Invoke("bind_aquila", actorId.Value, ActorFacts(actors));
    public void PlayFrontendCue(string cueName) => Invoke("play_frontend_cue", cueName);
    public void SetMasterSoundOption(float optionValue) => Invoke("set_master_sound_option", optionValue);
    public void SetMusicOption(float optionValue) => Invoke("set_music_option", optionValue);
    public void SetGameplayPaused(bool paused) => Invoke("set_gameplay_paused", paused);
    public void StopForLevelExit(bool playFrontendSelect) => Invoke("stop_for_level_exit", playFrontendSelect);
    public void StopLevel100Audio()
    {
        if (GodotObject.IsInstanceValid(_native)) Invoke("stop_level100_audio");
    }

    // FirstFlightGame preserves its three world/HUD interleavings. This is one
    // coarse transfer; no native call is made per actor, sample or Core event.
    public void ConsumeFrame(FrameAdvanceResult frame, Action<int> interleave)
    {
        ArgumentNullException.ThrowIfNull(interleave);
        Exception? hostFailure = null;
        Callable callback = Callable.From<int, D>(phase =>
        {
            try { interleave(phase); return new D { ["ok"] = true }; }
            catch (Exception error)
            {
                hostFailure = error;
                return new D { ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message };
            }
        });
        D result = Native.Call("consume_frame", FrameFacts(frame), callback).AsGodotDictionary();
        if (hostFailure is not null) ExceptionDispatchInfo.Capture(hostFailure).Throw();
        Check(result);
    }

    private static D FrameFacts(FrameAdvanceResult frame)
    {
        WorldSnapshot snapshot = frame.CurrentSnapshot;
        Level100MissionSnapshot mission = snapshot.Level100Mission;
        A messages = [];
        foreach (Level100MissionEvent value in frame.Level100MissionEvents)
            if (value is Level100MessageRequested message)
                messages.Add(new D { ["speaker_id"] = message.SpeakerId, ["message_id"] = message.MessageId });
        A flight = [];
        foreach (AquilaFlightEvent value in frame.AquilaFlightEvents)
            flight.Add(new D { ["kind"] = (int)value.Kind, ["tick"] = value.Tick, ["mode"] = (int)value.Mode });
        A weapons = [];
        foreach (Level100WeaponFireEvent value in frame.Level100WeaponFireEvents)
            weapons.Add(new D { ["weapon"] = (int)value.Weapon });
        A destruction = [];
        foreach (Level100DestructionEvent value in frame.Level100DestructionEvents)
            destruction.Add(new D { ["effect_kind"] = (int)value.EffectKind,
                ["position"] = PositionFacts(value.Position.X, value.Position.Y, value.Position.Z) });
        return new D { ["actors"] = ActorFacts(snapshot.Level100Actors),
            // BattleEngine.cpp:1763-1815: strict absolute hull warning before energy.
            ["warning_state"] = snapshot.Hull < 7_000 ? 2 : snapshot.Energy < 2_000 ? 1 : 0,
            ["messages"] = messages, ["flight_events"] = flight, ["weapon_events"] = weapons,
            ["simulation_tick"] = snapshot.Tick, ["mission_tick"] = mission.Tick,
            ["thruster_fraction"] = snapshot.JetThrusterPermille / 1_000f,
            ["destruction_events"] = destruction,
            ["gameplay_mix"] = Level100MissionTiming.GameplayMix(mission.Outcome, mission.FailureReason, mission.TerminalTicksRemaining),
            ["gameplay_paused"] = Level100MissionTiming.GameplayPaused(mission.Outcome, mission.FailureReason, mission.TerminalTicksRemaining) };
    }

    private static A ActorFacts(Level100ActorRegistrySnapshot actors)
    {
        ArgumentNullException.ThrowIfNull(actors);
        A values = [];
        foreach (Level100ActorSnapshot actor in actors.Actors)
        {
            SimVector3 position = actor.Pose.PositionMillimeters;
            values.Add(new D { ["actor_id"] = actor.ActorId.Value, ["position_mm"] = PositionFacts(position.X, position.Y, position.Z) });
        }
        return values;
    }
    private static D PositionFacts(int x, int y, int z) => new() { ["x"] = x, ["y"] = y, ["z"] = z };
    private static int? OptionalInt(Variant value) => value.VariantType == Variant.Type.Nil ? null : value.AsInt32();
    private Node3D Native => _native ?? throw new InvalidOperationException("Native audio scene is not ready.");
    private void Invoke(StringName method, params Variant[] args) => Check(Native.Call(method, args).AsGodotDictionary());
    private static void Check(D result)
    {
        if (result.TryGetValue("ok", out Variant ok) && ok.AsBool()) return;
        string message = result.TryGetValue("error", out Variant text) ? text.AsString() : "Native audio returned no explicit result.";
        string kind = result.TryGetValue("error_type", out Variant type) ? type.AsString() : "InvalidOperationException";
        throw kind switch
        {
            "ArgumentException" => new ArgumentException(message),
            "ArgumentNullException" => new ArgumentNullException(null, message),
            "ArgumentOutOfRangeException" => new ArgumentOutOfRangeException(null, message),
            "InvalidDataException" => new InvalidDataException(message),
            "OverflowException" => new OverflowException(message),
            _ => new InvalidOperationException(message),
        };
    }
}
