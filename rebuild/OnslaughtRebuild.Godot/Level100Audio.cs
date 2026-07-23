// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using Godot;

namespace OnslaughtRebuild.GodotClient;

public readonly record struct Level100MessagePlaybackState(
    int? ActiveSpeakerId,
    int? ActiveMessageId,
    double PositionSeconds,
    double LengthSeconds,
    bool Playing,
    bool Paused);

// This is deliberately the Level 100 path adapter, not a reusable audio engine.
// Mission, frontend, flight, actor, destruction, HUD, and pause lanes decide
// their events and state. This node owns only exact stream selection, released
// queue/mix/pause behavior, presentation pitch/volume, and stream lifetime.
public sealed partial class Level100Audio : Node3D
{
    private const double RetailCharacterMessageHandoffSeconds = 6d / 30d;

    private readonly Dictionary<string, AudioStream> _pcmStreams =
        new(StringComparer.Ordinal);
    private readonly Dictionary<string, AudioStreamWav> _loopStreams =
        new(StringComparer.Ordinal);
    private readonly Dictionary<Level100TerminalCue, AudioStream> _terminalStreams = [];
    private readonly Dictionary<string, AudioStream> _frontendStreams =
        new(StringComparer.Ordinal);
    private readonly Dictionary<int, AudioStreamOggVorbis> _voiceStreams = [];
    private readonly Level100CharacterMessageQueue _queuedCharacterMessages = new();
    private readonly List<AudioStreamPlayer3D> _gameplayOneShots = [];
    private readonly List<AudioStreamPlayer> _terminalOneShots = [];
    private readonly List<AudioStreamPlayer> _frontendOneShots = [];
    private readonly Dictionary<AudioStreamPlayer3D, float> _gameplayBaseVolumes = [];
    private readonly Dictionary<AudioStreamPlayer, float> _terminalBaseVolumes = [];
    private readonly Dictionary<AudioStreamPlayer, float> _frontendBaseVolumes = [];

    private AudioStreamPlayer _tutorialVoice = null!;
    private AudioStreamPlayer _tutorialMusic = null!;
    private AudioStreamOggVorbis? _tutorialMusicStream;
    private Node3D? _aquila;
    private AudioStreamPlayer3D? _aquilaFlightLoop;
    private AudioStreamPlayer3D? _aquilaWarningLoop;
    private AquilaWarningAudioState _aquilaWarningState;
    private AudioStreamPlayer3D? _trainerLoop;
    private AudioStreamPlayer3D? _transportLoop;
    private AudioStreamPlayer3D? _repairPadIdleLoop;
    private int? _activeCharacterSpeakerId;
    private int? _activeCharacterMessageId;
    private double _activeCharacterMessageLengthSeconds;
    private double _characterMessageHandoffSecondsRemaining;
    private float _soundOptionMix = 1f;
    private float _musicOptionMix = 1f;
    private float _gameplayMix = 1f;
    private bool _gameplayPaused;

    public bool TutorialVoicePlaying =>
        CharacterMessagePlayback is { Playing: true, Paused: false };

    // HUD owns paging and lip presentation. It can poll this presentation-only
    // state without feeding playback timing back into deterministic mission waits.
    public Level100MessagePlaybackState CharacterMessagePlayback
    {
        get
        {
            bool playing =
                _activeCharacterMessageId.HasValue &&
                GodotObject.IsInstanceValid(_tutorialVoice) &&
                _tutorialVoice.Playing;
            double position = playing
                ? Math.Clamp(
                    _tutorialVoice.GetPlaybackPosition(),
                    0d,
                    _activeCharacterMessageLengthSeconds)
                : 0d;
            return new Level100MessagePlaybackState(
                _activeCharacterSpeakerId,
                _activeCharacterMessageId,
                position,
                _activeCharacterMessageLengthSeconds,
                playing,
                playing && _tutorialVoice.StreamPaused);
        }
    }

    public bool TutorialMusicPlaying =>
        GodotObject.IsInstanceValid(_tutorialMusic) && _tutorialMusic.Playing;

    public override void _Ready()
    {
        Name = "Level100Audio";
        ProcessMode = ProcessModeEnum.Always;

        _tutorialVoice = new AudioStreamPlayer
        {
            Name = "RetailLevel100TutorialVoice",
            ProcessMode = ProcessModeEnum.Always,
            VolumeDb = MixedSoundVolumeDb(
                Level100AudioCatalog.RetailRadioMessageVolume,
                gameplay: true),
        };
        _tutorialVoice.Finished += BeginCharacterMessageHandoff;
        AddChild(_tutorialVoice);

        _tutorialMusic = new AudioStreamPlayer
        {
            Name = "RetailLevel100TutorialMusic",
            ProcessMode = ProcessModeEnum.Always,
            VolumeDb = MixedMusicVolumeDb(),
        };
        AddChild(_tutorialMusic);
    }

    public override void _Process(double delta)
    {
        if (_gameplayPaused ||
            _characterMessageHandoffSecondsRemaining <= 0d ||
            !double.IsFinite(delta) ||
            delta <= 0d)
        {
            return;
        }

        _characterMessageHandoffSecondsRemaining -= delta;
        if (_characterMessageHandoffSecondsRemaining <= 0d)
        {
            _characterMessageHandoffSecondsRemaining = 0d;
            StartNextCharacterMessage();
        }
    }

    public void StartTutorialMusic()
    {
        if (_tutorialMusic.Playing)
        {
            return;
        }

        Level100MusicRecipe recipe = Level100AudioCatalog.TutorialMusic;
        _tutorialMusicStream ??= LoadOgg(recipe.ResourcePath, looping: true);
        _tutorialMusic.Stream = _tutorialMusicStream;
        _tutorialMusic.VolumeDb = MixedMusicVolumeDb();
        _tutorialMusic.Play();
    }

    public void StopTutorialMusic()
    {
        _tutorialMusic.Stop();
        _tutorialMusic.Stream = null;
    }

    public void BindAquila(Node3D aquila)
    {
        ArgumentNullException.ThrowIfNull(aquila);
        if (_aquila == aquila)
        {
            return;
        }

        StopLoop(ref _aquilaFlightLoop);
        StopLoop(ref _aquilaWarningLoop);
        _aquilaWarningState = AquilaWarningAudioState.Normal;
        _aquila = aquila;
    }

    // The flight owner calls this once for each ordered mechanics event. This
    // adapter does not infer an edge from snapshots or suppress same-frame cues.
    public void PlayAquilaTransition(AquilaTransitionCue cue)
    {
        Node3D aquila = _aquila ??
            throw new InvalidOperationException("The Level 100 Aquila audio owner is not bound.");
        switch (cue)
        {
            case AquilaTransitionCue.Takeoff:
                PlayAttached(
                    aquila,
                    "RetailAquilaTakeoff",
                    Level100AudioCatalog.GetAquilaTransition(cue));
                SetSpecificLoop(
                    ref _aquilaFlightLoop,
                    aquila,
                    "RetailAquilaInFlightLoop",
                    Level100AudioCatalog.GetAquilaTransition(AquilaTransitionCue.InFlight),
                    active: true);
                break;
            case AquilaTransitionCue.InFlight:
                SetSpecificLoop(
                    ref _aquilaFlightLoop,
                    aquila,
                    "RetailAquilaInFlightLoop",
                    Level100AudioCatalog.GetAquilaTransition(cue),
                    active: true);
                break;
            case AquilaTransitionCue.Landing:
                StopLoop(ref _aquilaFlightLoop);
                PlayAttached(
                    aquila,
                    "RetailAquilaLanding",
                    Level100AudioCatalog.GetAquilaTransition(cue));
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(cue));
        }
    }

    public void StopAquilaFlightLoop() => StopLoop(ref _aquilaFlightLoop);

    public void SetAquilaFlightPitch(float thrusterFraction)
    {
        if (!float.IsFinite(thrusterFraction) || thrusterFraction is < 0f or > 1f)
        {
            throw new ArgumentOutOfRangeException(nameof(thrusterFraction));
        }

        if (IsPlaying(_aquilaFlightLoop))
        {
            _aquilaFlightLoop!.PitchScale = 1f + (thrusterFraction * 0.25f);
        }
    }

    public void SetAquilaWarningState(AquilaWarningAudioState state)
    {
        if (_aquilaWarningState == state && IsPlaying(_aquilaWarningLoop))
        {
            return;
        }

        _aquilaWarningState = state;
        StopLoop(ref _aquilaWarningLoop);
        if (state == AquilaWarningAudioState.Normal)
        {
            return;
        }

        Node3D aquila = _aquila ??
            throw new InvalidOperationException("The Level 100 Aquila audio owner is not bound.");
        SetSpecificLoop(
            ref _aquilaWarningLoop,
            aquila,
            state == AquilaWarningAudioState.EnergyLow
                ? "RetailAquilaEnergyLowLoop"
                : "RetailAquilaHullCriticalLoop",
            Level100AudioCatalog.GetAquilaWarning(state),
            active: true);
    }

    public void PlayOnAquila(Level100EffectCue cue)
    {
        if (cue is not (
            Level100EffectCue.AquilaStrafe or
            Level100EffectCue.AquilaHydraulics or
            Level100EffectCue.AquilaIncomingMissile or
            Level100EffectCue.AquilaTargetLocked or
            Level100EffectCue.AquilaTargetAcquired or
            Level100EffectCue.PulseCannonFire or
            Level100EffectCue.VulcanCannonFire or
            Level100EffectCue.MicroMissileFire))
        {
            throw new ArgumentOutOfRangeException(
                nameof(cue),
                cue,
                "This Level 100 event is not owned by the Aquila.");
        }

        Node3D aquila = _aquila ??
            throw new InvalidOperationException("The Level 100 Aquila audio owner is not bound.");
        PlayAttached(aquila, $"Retail{cue}", Level100AudioCatalog.GetEffect(cue));
    }

    public void PlayAt(Level100EffectCue cue, Vector3 worldPosition)
    {
        if (cue is not (
            Level100EffectCue.DroneVulcanFire or
            Level100EffectCue.PulseImpact or
            Level100EffectCue.MissileImpact or
            Level100EffectCue.TargetOrTrainerDestroyed or
            Level100EffectCue.DroneDestroyed or
            Level100EffectCue.FacilityDestroyed or
            Level100EffectCue.AquilaDestroyed or
            Level100EffectCue.TransportDestroyed or
            Level100EffectCue.ComponentDebrisDestroyed or
            Level100EffectCue.LargeDebrisDestroyed or
            Level100EffectCue.HugeGroundDebrisDestroyed))
        {
            throw new ArgumentOutOfRangeException(
                nameof(cue),
                cue,
                "This Level 100 event requires its released owner.");
        }

        PlaySpatial(
            $"Retail{cue}",
            Level100AudioCatalog.GetEffect(cue),
            worldPosition,
            this);
    }

    public void PlayRepairCharging(Node3D repairPad) =>
        PlayAttached(
            repairPad,
            "RetailRepairPadCharging",
            Level100AudioCatalog.GetEffect(Level100EffectCue.RepairCharging));

    public void PlayRepairFull(Node3D repairPad) =>
        PlayAttached(
            repairPad,
            "RetailRepairPadFull",
            Level100AudioCatalog.GetEffect(Level100EffectCue.RepairFull));

    public void SetRepairPadIdle(Node3D repairPad, bool active) =>
        SetSpecificLoop(
            ref _repairPadIdleLoop,
            repairPad,
            "RetailRepairPadIdleLoop",
            Level100AudioCatalog.GetActorLoop(Level100ActorLoopCue.RepairPadIdle),
            active);

    public void SetTrainerFlying(Node3D trainer, bool active) =>
        SetSpecificLoop(
            ref _trainerLoop,
            trainer,
            "RetailAirTrainerFlybyLoop",
            Level100AudioCatalog.GetActorLoop(Level100ActorLoopCue.AirTrainer),
            active);

    // The shipped Target Drone has no engine effect, and neither its nor the
    // Air Trainer's missile launcher has a launch effect. Those states stay
    // silent instead of borrowing another Level 100 cue.

    public void SetTransportFlying(Node3D transport, bool active) =>
        SetSpecificLoop(
            ref _transportLoop,
            transport,
            "RetailTransportFlybyLoop",
            Level100AudioCatalog.GetActorLoop(Level100ActorLoopCue.Transport),
            active);

    public void PlayTerminalCue(Level100TerminalCue cue)
    {
        Level100AudioCueRecipe spec = Level100AudioCatalog.GetTerminal(cue);
        AudioStreamPlayer player = new()
        {
            Name = $"RetailTerminal{cue}",
            ProcessMode = ProcessModeEnum.Always,
            Stream = GetTerminalStream(cue, spec),
            VolumeDb = MixedSoundVolumeDb(spec.LinearVolume, gameplay: true),
            PitchScale = PitchFor(spec),
        };
        player.Finished += () => ReleaseTerminalOneShot(player);
        _terminalOneShots.Add(player);
        _terminalBaseVolumes.Add(player, spec.LinearVolume);
        AddChild(player);
        player.Play();
        player.StreamPaused = _gameplayPaused;
    }

    // The frontend owner emits the exact Move/Select/Back identity. Cues made
    // after PauseAllSamples remain live, matching the released pause menu.
    public void PlayFrontendCue(string cueName)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(cueName);
        Level100AudioCueRecipe spec = Level100AudioCatalog.GetFrontend(cueName);
        AudioStreamPlayer player = new()
        {
            Name = $"RetailFrontend{cueName}",
            ProcessMode = ProcessModeEnum.Always,
            Stream = GetFrontendStream(cueName, spec),
            VolumeDb = MixedSoundVolumeDb(spec.LinearVolume, gameplay: false),
            PitchScale = PitchFor(spec),
        };
        player.Finished += () => ReleaseFrontendOneShot(player);
        _frontendOneShots.Add(player);
        _frontendBaseVolumes.Add(player, spec.LinearVolume);
        AddChild(player);
        player.Play();
    }

    // Ordered Level100MessageRequested events enter by canonical speaker and
    // numeric message ID. Script waits and duration gates remain Core facts.
    public void QueueCharacterMessage(int speakerId, int messageId)
    {
        _queuedCharacterMessages.Enqueue(speakerId, messageId);
        if (!_tutorialVoice.Playing && _characterMessageHandoffSecondsRemaining <= 0d)
        {
            StartNextCharacterMessage();
        }
    }

    public void StopCharacterMessages()
    {
        _queuedCharacterMessages.Clear();
        _activeCharacterSpeakerId = null;
        _activeCharacterMessageId = null;
        _activeCharacterMessageLengthSeconds = 0d;
        _characterMessageHandoffSecondsRemaining = 0d;
        _tutorialVoice.Stop();
        _tutorialVoice.Stream = null;
    }

    public void SetMasterSoundOption(float optionValue)
    {
        _soundOptionMix = Level100AudioCatalog.ToRetailOptionMix(optionValue);
        ApplyMixVolumes();
    }

    public void SetMusicOption(float optionValue)
    {
        _musicOptionMix = Level100AudioCatalog.ToRetailOptionMix(optionValue);
        if (GodotObject.IsInstanceValid(_tutorialMusic))
        {
            _tutorialMusic.VolumeDb = MixedMusicVolumeDb();
        }
    }

    public void SetGameplayMix(float linearMix)
    {
        ValidateLinearMix(linearMix, nameof(linearMix));
        // The result owner supplies the released current fade or duck value.
        // Audio applies it but does not schedule or advance that state.
        _gameplayMix = linearMix;
        ApplyMixVolumes();
    }

    public void SetGameplayPaused(bool paused)
    {
        if (_gameplayPaused == paused)
        {
            return;
        }

        _gameplayPaused = paused;
        _tutorialVoice.StreamPaused = paused && _tutorialVoice.Playing;
        SetPaused(_terminalOneShots, paused);
        SetPaused(_frontendOneShots, paused);
        SetPaused(_gameplayOneShots, paused);
        SetLoopPaused(_aquilaFlightLoop, paused);
        SetLoopPaused(_aquilaWarningLoop, paused);
        SetLoopPaused(_trainerLoop, paused);
        SetLoopPaused(_transportLoop, paused);
        SetLoopPaused(_repairPadIdleLoop, paused);
        // MUSIC is not a CSoundManager sample and keeps playing in retail.
    }

    public void StopGameplaySamples()
    {
        StopCharacterMessages();
        StopAndFree(_terminalOneShots);
        _terminalBaseVolumes.Clear();
        StopAndFree(_gameplayOneShots);
        _gameplayBaseVolumes.Clear();
        StopLoop(ref _aquilaFlightLoop);
        StopLoop(ref _aquilaWarningLoop);
        StopLoop(ref _trainerLoop);
        StopLoop(ref _transportLoop);
        StopLoop(ref _repairPadIdleLoop);
        _aquilaWarningState = AquilaWarningAudioState.Normal;
        _gameplayMix = 1f;
        _gameplayPaused = false;
    }

    // Released KillAllSamples stops every currently owned sample. A pause-menu
    // frontend cue created after this call is consequently a new live sample.
    public void StopAllSamples()
    {
        StopGameplaySamples();
        StopAndFree(_frontendOneShots);
        _frontendBaseVolumes.Clear();
    }

    public void StopLevel100Audio()
    {
        StopAllSamples();
        StopTutorialMusic();
    }

    public void StopForLevelExit(bool playFrontendSelect)
    {
        StopLevel100Audio();
        if (playFrontendSelect)
        {
            PlayFrontendCue("Select");
        }
    }

    public override void _ExitTree() => StopLevel100Audio();

    private void PlayAttached(
        Node3D owner,
        string name,
        Level100AudioCueRecipe spec) =>
        PlaySpatial(name, spec, Vector3.Zero, owner);

    private void PlaySpatial(
        string name,
        Level100AudioCueRecipe spec,
        Vector3 position,
        Node parent)
    {
        if (spec.Looping)
        {
            throw new InvalidOperationException($"Looping cue '{name}' requires a specific owner.");
        }

        var player = new AudioStreamPlayer3D
        {
            Name = name,
            ProcessMode = ProcessModeEnum.Always,
            Stream = GetEventStream(spec),
            Position = position,
            MaxDistance = 80f,
            UnitSize = 8f,
            VolumeDb = MixedSoundVolumeDb(spec.LinearVolume, gameplay: true),
            PitchScale = PitchFor(spec),
        };
        player.Finished += () => ReleaseGameplayOneShot(player);
        _gameplayOneShots.Add(player);
        _gameplayBaseVolumes.Add(player, spec.LinearVolume);
        parent.AddChild(player);
        player.Play();
        player.StreamPaused = _gameplayPaused;
    }

    private void SetSpecificLoop(
        ref AudioStreamPlayer3D? player,
        Node3D owner,
        string name,
        Level100AudioCueRecipe spec,
        bool active)
    {
        ArgumentNullException.ThrowIfNull(owner);
        if (!active)
        {
            StopLoop(ref player);
            return;
        }

        if (IsPlaying(player) && player!.GetParent() == owner)
        {
            return;
        }

        StopLoop(ref player);
        if (!spec.Looping)
        {
            throw new InvalidOperationException($"Non-looping cue '{name}' cannot own actor state.");
        }

        player = new AudioStreamPlayer3D
        {
            Name = name,
            ProcessMode = ProcessModeEnum.Always,
            Stream = GetLoopStream(spec),
            Position = Vector3.Zero,
            MaxDistance = 80f,
            UnitSize = 8f,
            VolumeDb = MixedSoundVolumeDb(spec.LinearVolume, gameplay: true),
            PitchScale = PitchFor(spec),
        };
        _gameplayBaseVolumes.Add(player, spec.LinearVolume);
        owner.AddChild(player);
        player.Play();
        player.StreamPaused = _gameplayPaused;
    }

    private AudioStream GetEventStream(Level100AudioCueRecipe spec)
    {
        if (!_pcmStreams.TryGetValue(spec.ResourcePath, out AudioStream? stream))
        {
            stream = LoadPcmWav(spec.ResourcePath, looping: false);
            _pcmStreams.Add(spec.ResourcePath, stream);
        }
        return stream;
    }

    private AudioStreamWav GetLoopStream(Level100AudioCueRecipe spec)
    {
        if (!_loopStreams.TryGetValue(spec.ResourcePath, out AudioStreamWav? stream))
        {
            stream = LoadPcmWav(spec.ResourcePath, looping: true);
            _loopStreams.Add(spec.ResourcePath, stream);
        }
        return stream;
    }

    private AudioStream GetTerminalStream(
        Level100TerminalCue cue,
        Level100AudioCueRecipe spec)
    {
        if (!_terminalStreams.TryGetValue(cue, out AudioStream? stream))
        {
            stream = LoadPcmWav(spec.ResourcePath, looping: false);
            _terminalStreams.Add(cue, stream);
        }
        return stream;
    }

    private AudioStream GetFrontendStream(
        string cueName,
        Level100AudioCueRecipe spec)
    {
        if (!_frontendStreams.TryGetValue(cueName, out AudioStream? stream))
        {
            stream = LoadPcmWav(spec.ResourcePath, looping: false);
            _frontendStreams.Add(cueName, stream);
        }
        return stream;
    }

    private void BeginCharacterMessageHandoff()
    {
        _activeCharacterMessageId = null;
        _activeCharacterSpeakerId = null;
        _activeCharacterMessageLengthSeconds = 0d;
        _tutorialVoice.Stream = null;
        if (_queuedCharacterMessages.Count > 0)
        {
            _characterMessageHandoffSecondsRemaining =
                RetailCharacterMessageHandoffSeconds;
        }
    }

    private void StartNextCharacterMessage()
    {
        if (!_queuedCharacterMessages.TryDequeue(
            out Level100QueuedCharacterMessage queuedMessage))
        {
            _activeCharacterSpeakerId = null;
            _activeCharacterMessageId = null;
            _activeCharacterMessageLengthSeconds = 0d;
            _tutorialVoice.Stream = null;
            return;
        }

        Level100MessageAudioSpec message = queuedMessage.Audio;
        if (!_voiceStreams.TryGetValue(message.MessageId, out AudioStreamOggVorbis? stream))
        {
            stream = LoadOgg(message.ResourcePath, looping: false);
            _voiceStreams.Add(message.MessageId, stream);
        }

        _activeCharacterSpeakerId = queuedMessage.SpeakerId;
        _activeCharacterMessageId = message.MessageId;
        _activeCharacterMessageLengthSeconds = stream.GetLength();
        _tutorialVoice.Stream = stream;
        _tutorialVoice.VolumeDb = MixedSoundVolumeDb(
            Level100AudioCatalog.RetailRadioMessageVolume,
            gameplay: true);
        _tutorialVoice.Play();
        _tutorialVoice.StreamPaused = _gameplayPaused;
    }

    private void ApplyMixVolumes()
    {
        if (GodotObject.IsInstanceValid(_tutorialVoice))
        {
            _tutorialVoice.VolumeDb = MixedSoundVolumeDb(
                Level100AudioCatalog.RetailRadioMessageVolume,
                gameplay: true);
        }
        ApplyMixVolumes(_gameplayBaseVolumes, gameplay: true);
        ApplyMixVolumes(_terminalBaseVolumes, gameplay: true);
        ApplyMixVolumes(_frontendBaseVolumes, gameplay: false);
    }

    private void ApplyMixVolumes(
        Dictionary<AudioStreamPlayer3D, float> baseVolumes,
        bool gameplay)
    {
        // Finished/stop owners remove entries, so option and fade updates can
        // iterate directly without a temporary key-copy allocation.
        foreach ((AudioStreamPlayer3D player, float baseVolume) in baseVolumes)
        {
            if (GodotObject.IsInstanceValid(player))
            {
                player.VolumeDb = MixedSoundVolumeDb(baseVolume, gameplay);
            }
        }
    }

    private void ApplyMixVolumes(
        Dictionary<AudioStreamPlayer, float> baseVolumes,
        bool gameplay)
    {
        foreach ((AudioStreamPlayer player, float baseVolume) in baseVolumes)
        {
            if (GodotObject.IsInstanceValid(player))
            {
                player.VolumeDb = MixedSoundVolumeDb(baseVolume, gameplay);
            }
        }
    }

    private float MixedSoundVolumeDb(float baseVolume, bool gameplay)
    {
        float linear =
            baseVolume * _soundOptionMix * (gameplay ? _gameplayMix : 1f);
        return linear <= 0f ? -80f : Mathf.LinearToDb(linear);
    }

    private float MixedMusicVolumeDb() =>
        _musicOptionMix <= 0f ? -80f : Mathf.LinearToDb(_musicOptionMix);

    private static void ValidateLinearMix(float value, string parameterName)
    {
        if (!float.IsFinite(value) || value is < 0f or > 1f)
        {
            throw new ArgumentOutOfRangeException(
                parameterName,
                value,
                "Audio mix values must be finite and between zero and one.");
        }
    }

    private static float PitchFor(Level100AudioCueRecipe spec) =>
        spec.PitchVariancePercent == 0
            ? 1f
            : 1f + ((GD.Randi() % (uint)spec.PitchVariancePercent) / 100f);

    private void ReleaseGameplayOneShot(AudioStreamPlayer3D player)
    {
        _gameplayOneShots.Remove(player);
        _gameplayBaseVolumes.Remove(player);
        player.QueueFree();
    }

    private void ReleaseTerminalOneShot(AudioStreamPlayer player)
    {
        _terminalOneShots.Remove(player);
        _terminalBaseVolumes.Remove(player);
        player.QueueFree();
    }

    private void ReleaseFrontendOneShot(AudioStreamPlayer player)
    {
        _frontendOneShots.Remove(player);
        _frontendBaseVolumes.Remove(player);
        player.QueueFree();
    }

    private static void SetPaused(List<AudioStreamPlayer3D> players, bool paused)
    {
        for (int index = players.Count - 1; index >= 0; index--)
        {
            if (GodotObject.IsInstanceValid(players[index]))
            {
                players[index].StreamPaused = paused;
            }
        }
    }

    private static void SetPaused(List<AudioStreamPlayer> players, bool paused)
    {
        for (int index = players.Count - 1; index >= 0; index--)
        {
            if (GodotObject.IsInstanceValid(players[index]))
            {
                players[index].StreamPaused = paused;
            }
        }
    }

    private static void SetLoopPaused(AudioStreamPlayer3D? player, bool paused)
    {
        if (IsPlaying(player))
        {
            player!.StreamPaused = paused;
        }
    }

    private static void StopAndFree(List<AudioStreamPlayer3D> players)
    {
        foreach (AudioStreamPlayer3D player in players)
        {
            if (GodotObject.IsInstanceValid(player))
            {
                player.Stop();
                player.QueueFree();
            }
        }
        players.Clear();
    }

    private static void StopAndFree(List<AudioStreamPlayer> players)
    {
        foreach (AudioStreamPlayer player in players)
        {
            if (GodotObject.IsInstanceValid(player))
            {
                player.Stop();
                player.QueueFree();
            }
        }
        players.Clear();
    }

    private void StopLoop(ref AudioStreamPlayer3D? player)
    {
        if (player is not null)
        {
            _gameplayBaseVolumes.Remove(player);
        }
        if (GodotObject.IsInstanceValid(player))
        {
            player!.Stop();
            player.QueueFree();
        }
        player = null;
    }

    private static bool IsPlaying(AudioStreamPlayer3D? player) =>
        GodotObject.IsInstanceValid(player) && player!.Playing;

    private static AudioStreamOggVorbis LoadOgg(string resourcePath, bool looping)
    {
        byte[] source = Godot.FileAccess.GetFileAsBytes(resourcePath);
        AudioStreamOggVorbis? stream = source.Length == 0
            ? null
            : AudioStreamOggVorbis.LoadFromBuffer(source);
        if (stream is null)
        {
            throw new InvalidDataException(
                $"Released Ogg stream is missing or invalid: {resourcePath}");
        }
        stream.Loop = looping;
        return stream;
    }

    private static AudioStreamWav LoadPcmWav(string resourcePath, bool looping)
    {
        byte[] wave = Godot.FileAccess.GetFileAsBytes(resourcePath);
        if (wave.Length < 44 ||
            !wave.AsSpan(0, 4).SequenceEqual("RIFF"u8) ||
            !wave.AsSpan(8, 4).SequenceEqual("WAVE"u8) ||
            !wave.AsSpan(12, 4).SequenceEqual("fmt "u8) ||
            BinaryPrimitives.ReadUInt32LittleEndian(wave.AsSpan(16, 4)) != 16 ||
            BinaryPrimitives.ReadUInt16LittleEndian(wave.AsSpan(20, 2)) != 1 ||
            BinaryPrimitives.ReadUInt16LittleEndian(wave.AsSpan(22, 2)) != 1 ||
            BinaryPrimitives.ReadUInt32LittleEndian(wave.AsSpan(24, 4)) != 44_100 ||
            BinaryPrimitives.ReadUInt16LittleEndian(wave.AsSpan(34, 2)) != 16 ||
            !wave.AsSpan(36, 4).SequenceEqual("data"u8))
        {
            throw new InvalidDataException(
                $"Curated audio '{resourcePath}' is not 44.1 kHz mono 16-bit PCM WAV.");
        }

        uint dataLength = BinaryPrimitives.ReadUInt32LittleEndian(wave.AsSpan(40, 4));
        if (dataLength != wave.Length - 44)
        {
            throw new InvalidDataException(
                $"Curated audio '{resourcePath}' has invalid WAV framing.");
        }

        return new AudioStreamWav
        {
            Format = AudioStreamWav.FormatEnum.Format16Bits,
            MixRate = 44_100,
            Stereo = false,
            Data = wave.AsSpan(44).ToArray(),
            LoopMode = looping
                ? AudioStreamWav.LoopModeEnum.Forward
                : AudioStreamWav.LoopModeEnum.Disabled,
            LoopBegin = 0,
            LoopEnd = looping ? (wave.Length - 44) / sizeof(short) : 0,
        };
    }
}
