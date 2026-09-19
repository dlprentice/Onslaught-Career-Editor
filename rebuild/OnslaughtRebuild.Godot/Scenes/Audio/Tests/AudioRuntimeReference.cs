// SPDX-License-Identifier: GPL-3.0-or-later
using System.Reflection;
using Godot;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

// Temporary comparison adapter for the unchanged production C# owner. It
// returns object-free facts; it never writes assets or drives a real device.
public sealed partial class AudioRuntimeReference : RefCounted
{
    private readonly AudioPlaybackRetirement _retirement = new();
    private LegacyLevel100AudioReference? _audio;
    private readonly Dictionary<string, Node3D> _attachments = [];
    private static readonly BindingFlags Private = BindingFlags.NonPublic | BindingFlags.Instance;

    public D CreateReference(Node host, A operations)
    {
        if (Engine.IsEditorHint() || AudioServer.GetDriverName() != "Dummy")
            return new D { ["ok"] = false, ["error"] = "Runtime reference requires the isolated Dummy audio driver." };
        _audio = new LegacyLevel100AudioReference { PlaybackRetirement = _retirement };
        host.AddChild(_audio);
        _audio.SetProcess(false);
        foreach (string name in new[] { "trainer", "transport", "repair" })
        {
            Node3D owner = new() { Name = name };
            _audio.AddChild(owner);
            _attachments.Add(name, owner);
        }
        A snapshots = [];
        GD.Seed(42042);
        try
        {
            snapshots.Add(new D { ["result"] = Success(), ["state"] = Snapshot(), ["next_random"] = GD.Randi() });
            foreach (Variant value in operations)
            {
                D operation = value.AsGodotDictionary();
                D result;
                try { Apply(operation); result = Success(); }
                catch (Exception error)
                {
                    Exception actual = error is TargetInvocationException { InnerException: not null } wrapper
                        ? wrapper.InnerException! : error;
                    result = new D { ["ok"] = false, ["error_type"] = actual.GetType().Name };
                }
                snapshots.Add(new D { ["result"] = result, ["state"] = Snapshot(), ["next_random"] = GD.Randi() });
            }
            A music = [];
            MethodInfo volume = typeof(LegacyLevel100AudioReference).GetMethod("MusicVolumeDb", BindingFlags.NonPublic | BindingFlags.Static)!;
            for (int index = 0; index <= 127; index++)
                music.Add(Word((float)volume.Invoke(null, [index])!));
            A positions = [];
            foreach (int[] xyz in new int[][] { [0, 0, 0], [1, -1, 1], [1000, -2000, 3000],
                [16_777_217, -16_777_217, 16_777_217], [int.MinValue, int.MaxValue, int.MinValue],
                [int.MaxValue, int.MinValue, int.MaxValue] })
            {
                MethodInfo sim = typeof(LegacyLevel100AudioReference).GetMethod("ToGodotWorld", BindingFlags.NonPublic | BindingFlags.Static,
                    null, [typeof(SimVector3)], null)!;
                MethodInfo retail = typeof(LegacyLevel100AudioReference).GetMethod("ToGodotWorld", BindingFlags.NonPublic | BindingFlags.Static,
                    null, [typeof(Level100Vector3)], null)!;
                positions.Add(new D { ["input"] = xyz,
                    ["sim"] = VectorWords((Vector3)sim.Invoke(null, [new SimVector3(xyz[0], xyz[1], xyz[2])])!),
                    ["retail"] = VectorWords((Vector3)retail.Invoke(null, [new Level100Vector3(xyz[0], xyz[1], xyz[2])])!) });
            }
            return new D { ["ok"] = true, ["value"] = new D { ["schema"] = 1,
                ["operations"] = operations, ["snapshots"] = snapshots, ["music_volume_words"] = music, ["positions"] = positions } };
        }
        finally
        {
            _audio.StopLevel100Audio();
            _audio.QueueFree();
            _audio = null;
            _attachments.Clear();
        }
    }

    public int PendingPlaybackCount() => _retirement.PendingCount;
    public void ReleaseObserver() => _retirement.Dispose();

    private void Apply(D op)
    {
        LegacyLevel100AudioReference audio = _audio!;
        switch (op["op"].AsString())
        {
            case "bind": audio.BindAquila(new(I(op, "id")), Actors(op["actors"].AsGodotArray())); break;
            case "pose": audio.UpdateAquilaPose(Actors(op["actors"].AsGodotArray())); break;
            case "transition": audio.PlayAquilaTransition((AquilaTransitionCue)I(op, "value")); break;
            case "effect": audio.PlayOnAquila((Level100EffectCue)I(op, "value")); break;
            case "warning": audio.SetAquilaWarningState((AquilaWarningAudioState)I(op, "value")); break;
            case "terminal": audio.PlayTerminalCue((Level100TerminalCue)I(op, "value")); break;
            case "frontend": audio.PlayFrontendCue(op["value"].AsString()); break;
            case "master": audio.SetMasterSoundOption((float)op["value"].AsDouble()); break;
            case "music_option": audio.SetMusicOption((float)op["value"].AsDouble()); break;
            case "mix": audio.SetGameplayMix((float)op["value"].AsDouble()); break;
            case "pitch": audio.SetAquilaFlightPitch((float)op["value"].AsDouble()); break;
            case "pause": audio.SetGameplayPaused(op["value"].AsBool()); break;
            case "advance": audio._Process(op["value"].AsDouble()); break;
            case "music_frontend": audio.StartFrontendMusic(); break;
            case "music_tutorial": audio.StartTutorialMusic(); break;
            case "music_stop": audio.StopFrontendMusic(); break;
            case "music_finished": Get<AudioStreamPlayer>("_music").Stop(); Invoke("HandleMusicFinished"); break;
            case "queue": audio.QueueCharacterMessage(I(op, "speaker"), I(op, "message")); break;
            case "voice_finished": Get<AudioStreamPlayer>("_tutorialVoice").Stop(); Invoke("BeginCharacterMessageHandoff"); break;
            case "voice_stop": audio.StopCharacterMessages(); break;
            case "flight": audio.ConsumeAquilaFlightEvents(Flight(op["events"].AsGodotArray()), I(op, "tick"), I(op, "mission")); break;
            case "weapons": audio.ConsumeLevel100WeaponFireEvents(Weapons(op["events"].AsGodotArray())); break;
            case "destruction": audio.ConsumeLevel100DestructionEvents(Destruction(op["events"].AsGodotArray())); break;
            case "loop": SetLoop(op["name"].AsString(), op["active"].AsBool()); break;
            case "repair":
                if (op["full"].AsBool()) audio.PlayRepairFull(_attachments["repair"]);
                else audio.PlayRepairCharging(_attachments["repair"]);
                break;
            case "owner_pose": _attachments[op["name"].AsString()].Position = op["value"].AsVector3(); break;
            case "stop_gameplay": audio.StopGameplaySamples(); break;
            case "stop_all": audio.StopAllSamples(); break;
            case "stop_level": audio.StopLevel100Audio(); break;
            case "exit": audio.StopForLevelExit(op["select"].AsBool()); break;
            case "frame":
                D f = op["facts"].AsGodotDictionary();
                audio.UpdateAquilaPose(Actors(f["actors"].AsGodotArray()));
                audio.SetAquilaWarningState((AquilaWarningAudioState)I(f, "warning_state"));
                foreach (Variant value in f["messages"].AsGodotArray())
                { D row = value.AsGodotDictionary(); audio.QueueCharacterMessage(I(row, "speaker_id"), I(row, "message_id")); }
                audio.ConsumeAquilaFlightEvents(Flight(f["flight_events"].AsGodotArray()), I(f, "simulation_tick"), I(f, "mission_tick"));
                audio.ConsumeLevel100WeaponFireEvents(Weapons(f["weapon_events"].AsGodotArray()));
                audio.SetAquilaFlightPitch((float)f["thruster_fraction"].AsDouble());
                audio.ConsumeLevel100DestructionEvents(Destruction(f["destruction_events"].AsGodotArray()));
                audio.SetGameplayMix((float)f["gameplay_mix"].AsDouble());
                audio.SetGameplayPaused(f["gameplay_paused"].AsBool());
                break;
            default: throw new InvalidOperationException("Unknown audio reference operation.");
        }
    }

    private void SetLoop(string name, bool active)
    {
        switch (name)
        {
            case "trainer": _audio!.SetTrainerFlying(_attachments[name], active); break;
            case "transport": _audio!.SetTransportFlying(_attachments[name], active); break;
            case "repair": _audio!.SetRepairPadIdle(_attachments[name], active); break;
            default: throw new InvalidOperationException();
        }
    }

    private D Snapshot()
    {
        RetailMusicPolicySnapshot music = Get<RetailMusicPolicy>("_musicPolicy").Snapshot();
        var loops = new D();
        foreach ((string name, string field) in new[] { ("flight", "_aquilaFlightLoop"), ("warning", "_aquilaWarningLoop"),
            ("trainer", "_trainerLoop"), ("transport", "_transportLoop"), ("repair", "_repairPadIdleLoop") })
        {
            AudioStreamPlayer3D? player = Field(field) as AudioStreamPlayer3D;
            if (player is not null && GodotObject.IsInstanceValid(player)) loops[name] = Player(player);
        }
        Level100MessagePlaybackState playback = _audio!.CharacterMessagePlayback;
        Node3D? aquila = Field("_aquila") as Node3D;
        return new D
        {
            ["sound_master"] = Word(Get<float>("_soundMasterVolume")), ["gameplay_mix"] = Word(Get<float>("_gameplayMix")),
            ["paused"] = Get<bool>("_gameplayPaused"), ["warning_state"] = (int)Get<AquilaWarningAudioState>("_aquilaWarningState"),
            ["warning_loop_state"] = (int)Get<AquilaWarningAudioState>("_aquilaWarningLoopState"),
            ["mission_start"] = OptionalInt(Field("_hostileEnvironmentMissionStartTick")),
            ["last_contact"] = Get<int>("_lastHostileEnvironmentContactTick"),
            ["actor"] = Field("_aquilaActorId") is Level100ActorId actor ? actor.Value : default(Variant),
            ["actor_position"] = aquila is null ? default(Variant) : VectorWords(aquila.Position),
            ["music_accumulator"] = Get<double>("_musicUpdateAccumulatorSeconds"),
            ["voice_lead"] = Get<double>("_characterMessageVoiceLeadSecondsRemaining"),
            ["handoff"] = Get<double>("_characterMessageHandoffSecondsRemaining"),
            ["queue_count"] = (int)Field("_queuedCharacterMessages")!.GetType().GetProperty("Count")!.GetValue(Field("_queuedCharacterMessages"))!,
            ["speaker"] = playback.ActiveSpeakerId.HasValue ? playback.ActiveSpeakerId.Value : default(Variant),
            ["message"] = playback.ActiveMessageId.HasValue ? playback.ActiveMessageId.Value : default(Variant),
            ["voice_length"] = playback.LengthSeconds,
            ["voice"] = Player(Get<AudioStreamPlayer>("_tutorialVoice")), ["music_player"] = Player(Get<AudioStreamPlayer>("_music")),
            ["music"] = new D { ["configured_volume"] = Word(music.ConfiguredVolume), ["set_volume"] = music.SetVolume,
                ["current_volume"] = music.CurrentVolume, ["target_volume"] = music.TargetVolume,
                ["is_playing"] = music.IsPlaying, ["play_type"] = (int)music.PlayType,
                ["current_track_identity"] = OptionalText(music.CurrentTrackIdentity), ["queued_track_identity"] = OptionalText(music.QueuedTrackIdentity),
                ["selection"] = music.Selection.HasValue ? (int)music.Selection.Value : default(Variant),
                ["selection_track_identity"] = OptionalText(music.SelectionTrackIdentity) },
            ["flight_fade"] = Fade("_aquilaFlightLoop"), ["warning_fade"] = Fade("_aquilaWarningLoop"), ["loops"] = loops,
            ["spatial"] = Players(Get<List<AudioStreamPlayer3D>>("_gameplayOneShots")),
            ["terminal"] = Players(Get<List<AudioStreamPlayer>>("_terminalOneShots")),
            ["frontend"] = Players(Get<List<AudioStreamPlayer>>("_frontendOneShots")),
        };
    }

    private D Fade(string prefix) => new()
    {
        ["sub"] = Word(Get<float>(prefix + "SubVolume")), ["target"] = Word(Get<float>(prefix + "TargetSubVolume")),
        ["step"] = Word(Get<float>(prefix + "FadeStep")), ["accumulator"] = Get<double>(prefix + "FadeAccumulatorSeconds"),
    };
    private static A Players<T>(IEnumerable<T> players) where T : Node
    { A values = []; foreach (T player in players) values.Add(Player(player)); return values; }
    private static D Player(Node node)
    {
        if (node is AudioStreamPlayer p) return new D { ["volume"] = Word(p.VolumeDb), ["pitch"] = Word(p.PitchScale),
            ["paused"] = p.StreamPaused, ["stream"] = p.Stream is not null };
        AudioStreamPlayer3D s = (AudioStreamPlayer3D)node;
        return new D { ["volume"] = Word(s.VolumeDb), ["pitch"] = Word(s.PitchScale), ["paused"] = s.StreamPaused,
            ["stream"] = s.Stream is not null, ["position"] = VectorWords(s.Position), ["global_position"] = VectorWords(s.GlobalPosition) };
    }
    private object? Field(string name) => typeof(LegacyLevel100AudioReference).GetField(name, Private)!.GetValue(_audio);
    private T Get<T>(string name) => (T)Field(name)!;
    private void Invoke(string name) => typeof(LegacyLevel100AudioReference).GetMethod(name, Private)!.Invoke(_audio, null);
    private static int I(D value, string name) => value[name].AsInt32();
    private static D Success() => new() { ["ok"] = true };
    private static Variant OptionalInt(object? value) => value is int number ? number : default(Variant);
    private static Variant OptionalText(string? value) => value is null ? default(Variant) : (Variant)value;
    private static long Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static long[] VectorWords(Vector3 value) => [Word(value.X), Word(value.Y), Word(value.Z)];
    private static SimVector3 Position(D row) => new(I(row, "x"), I(row, "y"), I(row, "z"));
    private static Level100ActorRegistrySnapshot Actors(A rows) => new("audio-fixture", 0, 0,
        rows.Select(value =>
        {
            D row = value.AsGodotDictionary();
            return new Level100ActorSnapshot(new(I(row, "actor_id")), "audio-fixture", "Audio fixture", null, null, null,
                0, null, null, false, true, false, default, 1, new(Position(row["position_mm"].AsGodotDictionary()),
                    default, default, default), default, 0, null, false, null, false);
        }).ToArray(), [], []);
    private static AquilaFlightEvent[] Flight(A rows) => rows.Select(value =>
    { D r = value.AsGodotDictionary(); return new AquilaFlightEvent(I(r, "tick"), (AquilaFlightEvents)I(r, "kind"), (VehicleMode)I(r, "mode"), default); }).ToArray();
    private static Level100WeaponFireEvent[] Weapons(A rows) => rows.Select(value =>
    { D r = value.AsGodotDictionary(); return new Level100WeaponFireEvent(0, (Level100PlayerWeapon)I(r, "weapon"), r.ContainsKey("round_count") ? I(r, "round_count") : 1); }).ToArray();
    private static Level100DestructionEvent[] Destruction(A rows) => rows.Select(value =>
    { D r = value.AsGodotDictionary(); SimVector3 p = Position(r["position"].AsGodotDictionary());
        return new Level100DestructionEvent(default, (Level100DestructionEffectKind)I(r, "effect_kind"), 0, 0, 0, new(p.X, p.Y, p.Z)); }).ToArray();
}
