// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary Core boundary. The standard-engine scene owns the HUD catalog,
/// model, event history, schedule, presentation and all authored drawing parts.
/// This bridge sends detached facts once per snapshot and verified text once.
/// </summary>
public sealed partial class FirstFlightHud : Node
{
    public const string ScenePath = "res://Scenes/Hud/FirstFlightHud.tscn";
    private D _info = new();
    private int[] _deliveredIds = [];
    public CanvasLayer Presentation { get; private set; } = null!;
    public bool Visible { get => Presentation.Visible; set => Presentation.Visible = value; }
    public bool IsReadyForSmoke => Presentation.Get("ready_for_snapshot").AsBool();
    public int Level100ObjectiveMarkerCount => Number("objective_count");
    public int Level100DeliveredMessageCount => Number("delivered_message_count");
    public IReadOnlyList<int> Level100DeliveredMessageIds => _deliveredIds;
    public int Level100DeliveredHelpCount => Number("delivered_help_count");
    public int Level100Energy => Number("energy");
    public int Level100Shield => Number("shield");
    public int Level100Health => Number("health");
    public bool Level100BattleLineInfluenceAvailable => Flag("battle_line_available");
    public Level100HudLowerRightSocket Level100LowerRightSocket => (Level100HudLowerRightSocket)Number("socket");
    public bool Level100MessagePlaybackAvailable => Flag("playback_available");
    public bool Level100MessagePlaying => Flag("playing");
    public double Level100MessagePlaybackPositionSeconds => Seconds("playback_position");
    public double Level100MessagePlaybackLengthSeconds => Seconds("playback_length");

    public static D LoadVerifiedCatalog()
    {
        using GodotObject provider = GD.Load<GDScript>("res://Client/hud_catalog.gd").New().AsGodotObject();
        D result = provider.Call("load_verified_text_batch").AsGodotDictionary();
        Require(result);
        return result["value"].AsGodotDictionary();
    }

    public static FirstFlightHud Create(D verifiedCatalog)
    {
        ArgumentNullException.ThrowIfNull(verifiedCatalog);
        var bridge = new FirstFlightHud { Name = "FirstFlightHudBridge" };
        bridge.Presentation = GD.Load<PackedScene>(ScenePath).Instantiate<CanvasLayer>();
        bridge.AddChild(bridge.Presentation);
        bridge.Initialize(verifiedCatalog);
        return bridge;
    }

    public void Initialize(D verifiedCatalog)
    {
        ArgumentNullException.ThrowIfNull(verifiedCatalog);
        var allegiance = new D();
        foreach ((string definition, int value) in Level100StaticWorldAsset.LoadAuthoredAllegiance())
            allegiance[definition] = value;
        var constants = new D { ["maximum_energy"] = SimulationConstants.MaximumEnergy,
            ["maximum_hull"] = SimulationConstants.MaximumHull, ["ticks_per_second"] = SimulationConstants.TicksPerSecond,
            ["damage_flash_lifetime_ticks"] = SimulationConstants.Level100DamageFlashLifetimeTicks,
            ["message_box_allowed_tick"] = Level100MissionTiming.MessageBoxAllowedTick };
        Require(Presentation.Call("configure_model", allegiance, verifiedCatalog, constants).AsGodotDictionary());
        Require(Presentation.Call("initialize").AsGodotDictionary());
    }

    public void ConsumeMissionEvents(IReadOnlyList<Level100MissionEvent> events)
    {
        ArgumentNullException.ThrowIfNull(events);
        var batch = new A();
        foreach (Level100MissionEvent item in events)
        {
            batch.Add(item switch
            {
                Level100MessageRequested message => new D { ["kind"] = "message", ["tick"] = message.Tick,
                    ["speaker_id"] = message.SpeakerId, ["message_id"] = message.MessageId,
                    ["script_waits_for_duration"] = message.ScriptWaitsForDuration,
                    ["expected_playback_ticks"] = message.ExpectedPlaybackTicks },
                Level100HelpRequested help => new D { ["kind"] = "help", ["tick"] = help.Tick,
                    ["help_message_id"] = help.HelpMessageId },
                _ => new D { ["kind"] = "other" },
            });
        }
        Require(Presentation.Call("consume_events", batch).AsGodotDictionary());
    }

    public void MarkInputActivity() { /* The released HUD has no controls legend. */ }

    public void UpdateFromSnapshot(WorldSnapshot snapshot, Level100MessagePlaybackState playback)
    {
        ArgumentNullException.ThrowIfNull(snapshot);
        // Playback remains intentionally ignored: Core mission ticks own reveal,
        // pose and noise, so fixed-fps captures do not follow the audio mixer.
        _ = playback;
        var frame = new D { ["tick"] = snapshot.Tick, ["energy"] = snapshot.Energy,
            ["shield"] = snapshot.Shield, ["hull"] = snapshot.Hull,
            ["facing_yaw_micro_rad"] = snapshot.FacingYawMicroRad,
            ["player_position"] = Position(snapshot.PlayerPosition), ["mission_tick"] = snapshot.Level100Mission.Tick };
        D result = Presentation.Call("update_from_facts", Facts(snapshot), frame).AsGodotDictionary();
        if (result.TryGetValue("delivered_message_ids", out Variant deliveredOnFailure))
            _deliveredIds = deliveredOnFailure.AsInt32Array();
        Require(result);
        _info = result["value"].AsGodotDictionary();
        _deliveredIds = _info["delivered_message_ids"].AsInt32Array();
    }

    private static D Facts(WorldSnapshot value) => new()
    {
        ["tick"] = value.Tick, ["player_position"] = Position(value.PlayerPosition),
        ["facing_yaw_micro_rad"] = value.FacingYawMicroRad, ["mode"] = (int)value.Mode,
        ["walker_selected_weapon"] = (int)value.Level100WalkerSelectedWeapon,
        ["jet_selected_weapon"] = (int)value.Level100JetSelectedWeapon, ["hud_emphasis_mask"] = value.Level100HudEmphasisMask,
        ["mission"] = new D { ["tick"] = value.Level100Mission.Tick,
            ["pulse_cannon_availability"] = (int)value.Level100Mission.PulseCannonAvailability,
            ["twin_vulcan_availability"] = (int)value.Level100Mission.TwinVulcanAvailability,
            ["mech_vulcan_availability"] = (int)value.Level100Mission.MechVulcanAvailability,
            ["outcome"] = (int)value.Level100Mission.Outcome, ["failure_reason"] = (int)value.Level100Mission.FailureReason,
            ["terminal_ticks_remaining"] = value.Level100Mission.TerminalTicksRemaining },
        ["actors"] = Pack(value.Level100Actors.Actors, actor => new D { ["actor_id"] = actor.ActorId.Value,
            ["name"] = actor.Name, ["definition_identity"] = actor.DefinitionIdentity,
            ["active"] = actor.Active, ["is_objective"] = actor.IsObjective, ["lifecycle"] = (int)actor.Lifecycle,
            ["has_trigger"] = actor.Trigger.HasValue, ["position"] = Position(actor.Pose.PositionMillimeters),
            ["velocity"] = Position(actor.Pose.LinearVelocityMillimetersPerTick) }),
        ["commanded_allegiances"] = Pack(value.Level100ActorMechanics.Actors, actor => new D {
            ["actor_id"] = actor.ActorId.Value, ["allegiance"] = actor.Allegiance, ["has_override"] = actor.HasAllegianceOverride }),
        ["damage_flashes"] = Pack(value.Level100DamageFlashes, flash => new D {
            ["relative_yaw_micro_rad"] = flash.RelativeYawMicroRad, ["start_tick"] = flash.StartTick }),
    };

    private static D Position(SimVector2 value) => new() { ["x"] = value.X, ["z"] = value.Z };
    private static D Position(SimVector3 value) => new() { ["x"] = value.X, ["y"] = value.Y, ["z"] = value.Z };
    private static A Pack<T>(IEnumerable<T> items, Func<T, D> convert)
    {
        var result = new A();
        foreach (T item in items) result.Add(convert(item));
        return result;
    }
    private int Number(string key) => _info.TryGetValue(key, out Variant value) ? value.AsInt32() : 0;
    private bool Flag(string key) => _info.TryGetValue(key, out Variant value) && value.AsBool();
    private double Seconds(string key) => _info.TryGetValue(key, out Variant value) ? value.AsDouble() : 0d;
    private static void Require(D result)
    {
        if (!result["ok"].AsBool())
            throw new InvalidDataException(result["error"].AsString());
    }
}
