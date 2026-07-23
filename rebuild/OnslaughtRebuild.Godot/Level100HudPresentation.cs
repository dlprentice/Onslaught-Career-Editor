// SPDX-License-Identifier: GPL-3.0-or-later

using System.Collections.ObjectModel;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

public enum Level100HudAllegiance
{
    Neutral = 0,
    Friendly = 1,
    Enemy = 2,
}

public enum Level100HudContactSize
{
    Small = 0,
    Medium = 1,
    Large = 2,
    RepairPad = 3,
}

public enum Level100HudWeapon
{
    None = 0,
    PulseCannon = 1,
    VulcanCannon = 2,
}

public enum Level100HudWeaponSelectionSlot
{
    None = 0,
    Side = 1,
    Front = 2,
    Top = 3,
}

public enum Level100HudHelpPrompt
{
    // Exact signed text IDs from the released text.stf/native CText table.
    Fire = 1_197_607,
    ZoomIn = 8_268_984,
    ZoomOut = 17_186_000,
    Transform = 31_505_972,
    RetroThrusters = 2_302_408,
    WeaponSelect = 488_286_858,
}

public enum Level100HudSpeaker
{
    // Exact PlayCharMessage speaker arguments from the released text table.
    Kramer = 919_601,
    Tatiana = 1_508_464,
    Technician = 10_565_784,
}

public enum Level100HudPart
{
    // Exact HighlightHudPart arguments from the released onsldef.msl.
    Health = 0,
    Energy = 1,
    Compass = 2,
    BattleLine = 3,
    Radar = 4,
    CurrentWeapon = 5,
}

public sealed record Level100HudWeaponSnapshot(
    Level100HudWeapon? SelectedWeapon,
    bool PulseCannonEnabled,
    bool VulcanCannonEnabled,
    bool? SelectionPanelVisible,
    Level100HudWeaponSelectionSlot? SelectionSlot,
    int? PulseHeatPermille,
    int? VulcanAmmo,
    int? ChargePermille,
    bool? PulseCannonOverheated)
{
    public static Level100HudWeaponSnapshot Unavailable { get; } = new(
        SelectedWeapon: null,
        PulseCannonEnabled: false,
        VulcanCannonEnabled: false,
        SelectionPanelVisible: null,
        SelectionSlot: null,
        PulseHeatPermille: null,
        VulcanAmmo: null,
        ChargePermille: null,
        PulseCannonOverheated: null);
}

public sealed record Level100HudContactSnapshot(
    int Id,
    SimVector2 Position,
    SimVector2 Velocity,
    Level100HudAllegiance Allegiance,
    Level100HudContactSize Size,
    bool IsObjective,
    bool OnScanner);

public sealed record Level100HudThreatSnapshot(
    int RelativeYawMicroRad,
    int TicksRemaining);

public sealed record Level100HudDamageFlashSnapshot(
    int RelativeYawMicroRad,
    int TicksRemaining);

public sealed record Level100HudTargetSnapshot(
    int ContactId,
    int HullPermille,
    SimVector2 PredictedPosition,
    int LockPermille);

public sealed record Level100HudObjectiveSnapshot(
    Level100ActorId ActorId,
    string ThingName,
    SimVector3 PositionMillimeters);

public sealed record Level100HudMessageDeliverySnapshot(
    int Tick,
    Level100HudSpeaker Speaker,
    int MessageId,
    bool ScriptWaitsForDuration,
    int ExpectedPlaybackTicks);

public sealed record Level100HudBattleLineSnapshot(
    bool HasInfluenceValues,
    IReadOnlyList<short> InfluencePermille)
{
    public static Level100HudBattleLineSnapshot Unavailable { get; } = new(
        HasInfluenceValues: false,
        Array.AsReadOnly(Array.Empty<short>()));
}

public sealed record Level100HudSnapshot(
    Level100HudWeaponSnapshot Weapon,
    IReadOnlyList<Level100HudContactSnapshot> Contacts,
    IReadOnlyList<Level100HudObjectiveSnapshot> Objectives,
    IReadOnlyList<Level100HudThreatSnapshot> Threats,
    IReadOnlyList<Level100HudDamageFlashSnapshot> DamageFlashes,
    Level100HudTargetSnapshot? Target,
    Level100HudMessageDeliverySnapshot? ActiveMessage,
    IReadOnlyList<Level100HudPart> EmphasizedParts,
    IReadOnlyList<Level100HudMessageDeliverySnapshot> DeliveredMessages,
    IReadOnlyList<Level100HudHelpPrompt> ActiveHelp,
    IReadOnlyList<Level100HudHelpPrompt> DeliveredHelp,
    Level100HudBattleLineSnapshot BattleLine);

public sealed record Level100HudInfluenceNode(
    int Id,
    SimVector2 Position,
    int RadiusMillimeters);

public readonly record struct Level100HudInfluenceLink(int FirstNodeId, int SecondNodeId);

public static class Level100HudInfluenceMap
{
    // Exact version-1 influence nodes and links embedded in Level 100's BSWD.
    // Positions are translated from the released player-one origin in the same
    // millimetre coordinate system used by the rest of deterministic Core.
    private static readonly ReadOnlyCollection<Level100HudInfluenceNode> s_nodes =
        Array.AsReadOnly(new[]
        {
            new Level100HudInfluenceNode(0, new SimVector2(-3_688, 83_750), 10_000),
            new Level100HudInfluenceNode(1, new SimVector2(-30_688, 59_750), 10_000),
            new Level100HudInfluenceNode(2, new SimVector2(-70_688, 51_750), 10_000),
            new Level100HudInfluenceNode(3, new SimVector2(-95_688, -42_250), 10_000),
            new Level100HudInfluenceNode(4, new SimVector2(-99_688, -3_250), 10_000),
            new Level100HudInfluenceNode(5, new SimVector2(-109_688, 30_750), 10_000),
            new Level100HudInfluenceNode(6, new SimVector2(-66_688, 16_750), 10_000),
            new Level100HudInfluenceNode(7, new SimVector2(-77_688, 84_750), 10_000),
            new Level100HudInfluenceNode(8, new SimVector2(-38_688, 94_750), 10_000),
            new Level100HudInfluenceNode(9, new SimVector2(33_313, 69_750), 10_000),
            new Level100HudInfluenceNode(10, new SimVector2(-688, 48_750), 10_000),
            new Level100HudInfluenceNode(11, new SimVector2(33_813, 21_250), 10_000),
            new Level100HudInfluenceNode(12, new SimVector2(-13_188, 12_250), 10_000),
        });

    private static readonly ReadOnlyCollection<Level100HudInfluenceLink> s_links =
        Array.AsReadOnly(new[]
        {
            new Level100HudInfluenceLink(0, 9),
            new Level100HudInfluenceLink(0, 10),
            new Level100HudInfluenceLink(0, 1),
            new Level100HudInfluenceLink(10, 1),
            new Level100HudInfluenceLink(1, 8),
            new Level100HudInfluenceLink(1, 7),
            new Level100HudInfluenceLink(1, 2),
            new Level100HudInfluenceLink(2, 5),
            new Level100HudInfluenceLink(2, 6),
            new Level100HudInfluenceLink(12, 2),
            new Level100HudInfluenceLink(2, 7),
            new Level100HudInfluenceLink(10, 9),
            new Level100HudInfluenceLink(10, 11),
            new Level100HudInfluenceLink(12, 11),
            new Level100HudInfluenceLink(11, 9),
            new Level100HudInfluenceLink(10, 12),
            new Level100HudInfluenceLink(6, 12),
            new Level100HudInfluenceLink(8, 7),
            new Level100HudInfluenceLink(6, 5),
            new Level100HudInfluenceLink(6, 4),
            new Level100HudInfluenceLink(5, 4),
            new Level100HudInfluenceLink(4, 3),
        });

    public static IReadOnlyList<Level100HudInfluenceNode> Nodes => s_nodes;

    public static IReadOnlyList<Level100HudInfluenceLink> Links => s_links;
}

/// <summary>
/// Presentation-only projection of canonical mission events, actor state, and
/// audio playback. It never feeds simulation or mission progression.
/// </summary>
public sealed class Level100HudPresentationState
{
    private readonly List<Level100HudMessageDeliverySnapshot> _deliveredMessages = [];
    private readonly List<Level100HudHelpPrompt> _deliveredHelp = [];

    public void Consume(IReadOnlyList<Level100MissionEvent> events)
    {
        ArgumentNullException.ThrowIfNull(events);
        foreach (Level100MissionEvent missionEvent in events)
        {
            switch (missionEvent)
            {
                case Level100MessageRequested message:
                    _deliveredMessages.Add(new Level100HudMessageDeliverySnapshot(
                        message.Tick,
                        ParseSpeaker(message.SpeakerId),
                        message.MessageId,
                        message.ScriptWaitsForDuration,
                        message.ExpectedPlaybackTicks));
                    break;
                case Level100HelpRequested help:
                {
                    var prompt = (Level100HudHelpPrompt)help.HelpMessageId;
                    if (!Enum.IsDefined(prompt))
                    {
                        throw new InvalidDataException(
                            $"Released Level 100 help ID {help.HelpMessageId} is unsupported.");
                    }
                    _deliveredHelp.Add(prompt);
                    break;
                }
            }
        }
    }

    public Level100HudSnapshot Project(
        WorldSnapshot snapshot,
        Level100MessagePlaybackState playback)
    {
        ArgumentNullException.ThrowIfNull(snapshot);

        Level100ActorSnapshot[] objectiveActors = snapshot.Level100Actors.Actors
            .Where(actor =>
                actor.Active &&
                actor.IsObjective &&
                actor.Lifecycle != Level100ActorLifecycle.Destroyed)
            .ToArray();
        Level100HudObjectiveSnapshot[] objectives = objectiveActors
            .Select(actor => new Level100HudObjectiveSnapshot(
                actor.ActorId,
                actor.Name,
                actor.Pose.PositionMillimeters))
            .ToArray();

        Level100HudMessageDeliverySnapshot? activeDelivery =
            playback.ActiveSpeakerId is int activeSpeakerId &&
            playback.ActiveMessageId is int activeMessageId
                ? _deliveredMessages.LastOrDefault(
                    delivery =>
                        (int)delivery.Speaker == activeSpeakerId &&
                        delivery.MessageId == activeMessageId)
                : null;
        Level100MissionSnapshot mission = snapshot.Level100Mission;
        bool pulseEnabled =
            mission.PulseCannonAvailability == Level100MissionWeaponAvailability.Enabled;
        bool vulcanEnabled =
            mission.TwinVulcanAvailability == Level100MissionWeaponAvailability.Enabled ||
            mission.MechVulcanAvailability == Level100MissionWeaponAvailability.Enabled;
        var weapon = new Level100HudWeaponSnapshot(
            SelectedWeapon: null,
            pulseEnabled,
            vulcanEnabled,
            SelectionPanelVisible: null,
            SelectionSlot: null,
            PulseHeatPermille: null,
            VulcanAmmo: null,
            ChargePermille: null,
            PulseCannonOverheated: null);

        Level100HudPart[] emphasizedParts = Enum.GetValues<Level100HudPart>()
            .Where(part => (snapshot.Level100HudEmphasisMask & (1 << (int)part)) != 0)
            .ToArray();

        return new Level100HudSnapshot(
            weapon,
            Array.AsReadOnly(Array.Empty<Level100HudContactSnapshot>()),
            Array.AsReadOnly(objectives),
            Array.AsReadOnly(Array.Empty<Level100HudThreatSnapshot>()),
            Array.AsReadOnly(Array.Empty<Level100HudDamageFlashSnapshot>()),
            Target: null,
            activeDelivery,
            Array.AsReadOnly(emphasizedParts),
            Array.AsReadOnly(_deliveredMessages.ToArray()),
            Array.AsReadOnly(Array.Empty<Level100HudHelpPrompt>()),
            Array.AsReadOnly(_deliveredHelp.ToArray()),
            Level100HudBattleLineSnapshot.Unavailable);
    }

    private static Level100HudSpeaker ParseSpeaker(int speakerId)
    {
        var speaker = (Level100HudSpeaker)speakerId;
        return Enum.IsDefined(speaker)
            ? speaker
            : throw new InvalidDataException(
                $"Released Level 100 speaker ID {speakerId} is unsupported.");
    }
}
