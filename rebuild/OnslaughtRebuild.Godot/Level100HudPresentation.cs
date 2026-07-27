// SPDX-License-Identifier: GPL-3.0-or-later

using System.Collections.ObjectModel;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Exact numbering from the released <c>data\MissionScripts\onsldef.msl</c>
/// lines 66-68, which the developers' own source <c>#include</c>s as a header
/// (<c>Career.cpp:11</c>, <c>game.cpp:46</c>):
/// <code>
/// #define FRIENDLY_ALLIGENCE   0
/// #define ENEMY_ALLIGENCE      1
/// #define NEUTRAL_ALLEGIANCE   2
/// </code>
/// (the released spelling of "allegiance" is inconsistent between the three;
/// that is theirs, not a transcription slip.)
///
/// <para>This enum was previously <c>Neutral = 0, Friendly = 1, Enemy = 2</c> -
/// a PERMUTATION, with every released value occupied by the wrong name and no
/// comment saying so, while the sibling enums in this same file all cite the
/// release. It read as released and was not.</para>
///
/// <para>It was latent rather than broken: the contact list is currently always
/// empty, and every use site names the member rather than its value, so the
/// renumbering changes no behaviour today. It was a TRAP, not a bug. Core
/// already stores allegiance in released numbering - <c>SetAllegiance</c> keeps
/// <c>command.Scalar</c> verbatim at
/// <c>Level100ActorMechanics.cs:207</c> - so the first commit to join those two
/// same-named <c>int</c>s would have painted every enemy friendly-blue at
/// <c>FirstFlightHud.cs:592</c> and picked the friendly classification texture
/// at <c>:1365</c>. The compiler cannot catch a permutation of ints.</para>
/// </summary>
public enum Level100HudAllegiance
{
    Friendly = 0,
    Enemy = 1,
    Neutral = 2,
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

/// <summary>
/// One contact placed on the lower-left scanner: a design-space offset from the
/// scanner centre and the 0-255 alpha the released fade produced.
/// </summary>
public readonly record struct Level100ScannerPlacement(
    float OffsetX,
    float OffsetY,
    int Alpha,
    bool Drawn,
    bool Clamped);

/// <summary>
/// The released tactical-scanner projection, recovered from the SHIPPED BYTES.
/// The HUD has no source in the pinned GPL drop (rebuild/PROVENANCE.md places
/// <c>Hud.h</c>/<c>DXHud.h</c>/<c>PCHud.h</c> in the "recover from shipped
/// bytes" partition), so every constant below is a decoded .rdata float or a
/// decoded instruction immediate, cited by address.
///
/// <para>Owner: <c>CHud__RenderTacticalRadarContacts</c> @ <c>0x00484c50</c>,
/// called once from <c>CHud__RenderOverlayForViewpoint</c>. Its sole call site
/// at <c>0x00487bab</c> is <c>PUSH 0x42c00000</c> (<b>96.0f</b>) before
/// <c>MOV ECX,ESI; CALL</c> - the function is <c>RET 0x4</c>, so that float is
/// its one stack argument. Markers reach the screen through
/// <c>HudOverlay__DrawSpriteQuad</c> @ <c>0x004857e0</c>, a fixed forwarder to
/// <c>CVBufTexture__DrawSpriteEx</c> @ <c>0x00555be0</c> with anchor mode
/// <b>4</b> - the case that subtracts half the texture width AND half its
/// height - so (x, y) is the sprite CENTRE at 1:1 texel scale.</para>
///
/// <para>Decoded constants (read from the .rdata of the verified safe copy,
/// image base 0x00400000, .rdata VA 0x005d8000 / file 0x1d8000):</para>
/// <list type="table">
/// <item><term><c>0x005d8610</c></term><description>40.0f - scale numerator</description></item>
/// <item><term>call-site imm</term><description>96.0f - scale denominator</description></item>
/// <item><term><c>0x005dbe6c</c></term><description>46.0f - contact clamp radius, in PIXELS</description></item>
/// <item><term><c>0x005dbe70</c></term><description>8464.0f = 92^2 - cull radius squared, in PIXELS</description></item>
/// <item><term><c>0x005dbe68</c></term><description>0.021739131f = 1/46 - alpha fade per pixel past the rim</description></item>
/// <item><term><c>0x005d8c70</c></term><description>255.0f - alpha quantiser</description></item>
/// <item><term><c>0x005dbb70</c></term><description>69.0f - scanner centre x</description></item>
/// <item><term><c>0x005dbe74</c></term><description>44.0f - scanner centre y, up from the viewport bottom</description></item>
/// <item><term><c>0x005d857c</c></term><description>20.0f - second centre-y term</description></item>
/// <item><term><c>0x005d8568</c></term><description>1.0f - the -1 x / +1 y trim, and the clamp test</description></item>
/// </list>
///
/// <para>Those three radius constants are mutually consistent, which is the
/// cross-check that they were read correctly: the fade is
/// <c>1 - (r - 46)/46</c>, so it reaches exactly zero at r = 92, and the cull
/// test is exactly <c>r^2 &lt; 92^2</c>. Contacts past the rim are pinned TO the
/// rim and fade out over the next 46 pixels rather than vanishing.</para>
///
/// <para>VALIDATED against retail, not just read: with the released Level 100
/// start pose (288.6875, 243.25) yaw 0.509829998, this law places all eleven
/// authored allegiance-0 base-world objects on retail frame
/// <c>hud-timeline-run1/level100-t025065ms.png</c> to within 0.2 px of the
/// measured blue-blob centroids, and the pixel under each predicted centre is
/// literally <c>(80, 80, 174)</c> - the decoded friendly base tint. See the
/// tint constants below.</para>
/// </summary>
public static class Level100ScannerProjection
{
    /// <summary>_DAT_005d8610 = 40.0f.</summary>
    public const float ScaleNumerator = 40f;

    /// <summary>Stack argument at the sole call site 0x00487bab: PUSH 0x42c00000 = 96.0f.</summary>
    public const float ScaleDenominator = 96f;

    /// <summary>World units to scanner pixels: 40/96.</summary>
    public const float PixelsPerWorldUnit = ScaleNumerator / ScaleDenominator;

    /// <summary>_DAT_005dbe6c = 46.0f, in PIXELS.</summary>
    public const float ClampRadiusPixels = 46f;

    /// <summary>_DAT_005dbe70 = 8464.0f = 92^2, in PIXELS.</summary>
    public const float CullRadiusSquaredPixels = 8_464f;

    /// <summary>_DAT_005dbe68 = 0.021739131f = 1/46.</summary>
    public const float FadePerPixel = 0.021739131f;

    /// <summary>_DAT_005d8c70 = 255.0f.</summary>
    public const float AlphaQuantiser = 255f;

    /// <summary>
    /// _DAT_005dbb70 (69.0f) plus the two viewport-origin globals, which are
    /// zero for the single-player full-window viewport, minus _DAT_005d8568
    /// (1.0f).
    /// </summary>
    public const float CentreX = 69f - 1f;

    /// <summary>
    /// Viewport bottom (480 on the released 640x480 stage) minus _DAT_005dbe74
    /// (44.0f) minus _DAT_005d857c (20.0f) plus _DAT_005d8568 (1.0f). The
    /// 480-44-20 = 416 agrees with the 55-point circle fit of retail's
    /// radar-outline ring at y = 417.25 in the 640x480 frame.
    /// </summary>
    public const float CentreY = 480f - 44f - 20f + 1f;

    // Packed 0x00RRGGBB tint bases, read straight out of the three draw loops.
    // Each is OR-ed with alpha<<24 (0xFF while inside the rim). The "+" value is
    // added when unit flag 0x400 at unit+0x34 is set; Core does not currently
    // model that flag, so the client draws the base tint only.
    //
    // Friendly base 0x5050AF is CONFIRMED at the pixel level: retail's scanner
    // blobs at t025065 are literally (80, 80, 174) = 0x5050AE/AF.

    /// <summary>Allegiance 0 (FRIENDLY_ALLIGENCE), base at 0x00484d9f-ish loop: 0x5050AF.</summary>
    public const int FriendlyTintRgb = 0x5050AF;

    /// <summary>Friendly brightened by flag 0x400: +0x404050 -&gt; 0x9090FF.</summary>
    public const int FriendlyHighlightAdd = 0x404050;

    /// <summary>Allegiance 1 (ENEMY_ALLIGENCE): 0xAF0808.</summary>
    public const int EnemyTintRgb = 0xAF0808;

    /// <summary>Enemy brightened by flag 0x400: +0x504848 -&gt; 0xFF5050.</summary>
    public const int EnemyHighlightAdd = 0x504848;

    /// <summary>Every other allegiance (NEUTRAL_ALLEGIANCE = 2 and up): 0x606060.</summary>
    public const int NeutralTintRgb = 0x606060;

    /// <summary>Neutral brightened by flag 0x400: +0x101010 -&gt; 0x707070.</summary>
    public const int NeutralHighlightAdd = 0x101010;

    public static int TintRgb(Level100HudAllegiance allegiance) => allegiance switch
    {
        Level100HudAllegiance.Friendly => FriendlyTintRgb,
        Level100HudAllegiance.Enemy => EnemyTintRgb,
        _ => NeutralTintRgb,
    };

    /// <summary>
    /// Places one contact. <paramref name="deltaX"/> / <paramref name="deltaZ"/>
    /// are the contact minus the player in RETAIL UNITS on Core's horizontal
    /// axes (X, Z), and <paramref name="yawRadians"/> is the player's facing.
    ///
    /// <para>Retail computes <c>sin(-yaw) * 40 / 96</c> and
    /// <c>cos(-yaw) * 40 / 96</c> once, then
    /// <c>rx = dx*cosT - dy*sinT</c>, <c>ry = dx*sinT + dy*cosT</c> - a rotation
    /// by MINUS the player yaw with the world-to-pixel scale folded in. The
    /// returned Y offset is already screen-down, i.e. <c>-ry</c>.</para>
    /// </summary>
    public static Level100ScannerPlacement Place(
        float deltaX,
        float deltaZ,
        float yawRadians)
    {
        float sin = MathF.Sin(-yawRadians) * PixelsPerWorldUnit;
        float cos = MathF.Cos(-yawRadians) * PixelsPerWorldUnit;
        float rx = (deltaX * cos) - (deltaZ * sin);
        float ry = (deltaX * sin) + (deltaZ * cos);

        float radiusSquared = (rx * rx) + (ry * ry);
        if (!(radiusSquared < CullRadiusSquaredPixels))
        {
            return new Level100ScannerPlacement(0f, 0f, 0, Drawn: false, Clamped: false);
        }

        float radius = MathF.Sqrt(radiusSquared);
        int alpha = 255;
        bool clamped = false;
        // Retail's test is `46/r < 1.0f`, which is false at r == 0 (division by
        // zero yields +inf), so a contact standing on the player is unclamped
        // and fully opaque.
        float scale = ClampRadiusPixels / radius;
        if (scale < 1f)
        {
            clamped = true;
            rx *= scale;
            ry *= scale;
            float fade = 1f - ((radius - ClampRadiusPixels) * FadePerPixel);
            alpha = (int)MathF.Round(fade * AlphaQuantiser, MidpointRounding.ToEven);
            alpha = Math.Clamp(alpha, 0, 255);
        }

        return new Level100ScannerPlacement(rx, -ry, alpha, Drawn: true, clamped);
    }

    /// <summary>
    /// The same placement expressed in released design-space pixels, i.e. with
    /// the recovered scanner centre added.
    /// </summary>
    public static Level100ScannerPlacement PlaceInDesignSpace(
        float deltaX,
        float deltaZ,
        float yawRadians)
    {
        Level100ScannerPlacement placement = Place(deltaX, deltaZ, yawRadians);
        return placement.Drawn
            ? placement with
            {
                OffsetX = CentreX + placement.OffsetX,
                OffsetY = CentreY + placement.OffsetY,
            }
            : placement;
    }
}

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
    private readonly IReadOnlyDictionary<string, int> _authoredAllegiance;

    public Level100HudPresentationState()
        : this(null)
    {
    }

    /// <summary>
    /// <paramref name="authoredAllegianceByDefinitionIdentity"/> is the WRES
    /// <c>allegiance</c> int32 the released base-world records carry, keyed by
    /// the same <c>wres:bswd:NNNN</c> identity Core's actor definitions use. It
    /// is presentation input only: retail reads allegiance off the live unit at
    /// <c>unit+0x138</c>, and the scanner's whole colour partition
    /// (<c>0x5050AF</c> / <c>0xAF0808</c> / <c>0x606060</c>) is that one field.
    /// Core's own <c>Level100ActorMechanics</c> allegiance - the released
    /// <c>SetAllegiance</c> script command - takes precedence wherever it
    /// exists, because that is the field retail would have overwritten.
    /// </summary>
    public Level100HudPresentationState(
        IReadOnlyDictionary<string, int>? authoredAllegianceByDefinitionIdentity)
    {
        _authoredAllegiance = authoredAllegianceByDefinitionIdentity ??
            new Dictionary<string, int>(StringComparer.Ordinal);
    }

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

        Level100MissionSnapshot mission = snapshot.Level100Mission;
        // The active message is resolved from Core's OWN tick, not from the
        // audio mixer. `playback` is retained on the signature because the
        // audio adapter is still the sole playback owner and callers pass it,
        // but it is deliberately NOT consulted here: see the header of
        // Level100MessageSchedule for the 21-25 % cross-run self-noise this
        // caused and the measurement that identified it.
        _ = playback;
        Level100HudMessageDeliverySnapshot? activeDelivery =
            Level100MessageSchedule
                .ActiveAt(_deliveredMessages, mission.Tick)
                ?.Delivery;
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
            Array.AsReadOnly(ProjectContacts(snapshot)),
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

    /// <summary>
    /// Live scanner contacts, from the canonical actor registry. Retail walks
    /// its global unit list at <c>DAT_008550d0</c> inside
    /// <c>CHud__RenderTacticalRadarContacts</c> (<c>0x00484c50</c>), partitions
    /// it by the allegiance field at <c>unit+0x138</c>, and draws each surviving
    /// entry through the projection in <see cref="Level100ScannerProjection"/>.
    ///
    /// <para>What this reproduces: the membership test that an actor is active
    /// and not destroyed, the released allegiance partition, and the exact
    /// projection/clamp/fade. What it does NOT reproduce, because Core does not
    /// model the fields: retail's four extra gates - the <c>+0x1a4</c> vfunc
    /// predicate, <c>CThing</c> flag <c>0x4</c> at <c>+0x2c</c>, unit flag
    /// <c>0x8</c> at <c>+0x34</c>, and the neutral bucket's additional
    /// <c>+0x68</c> vfunc / <c>0x10</c> flag / non-null <c>+0x30</c> tests. The
    /// player's own Battle Engine and the trigger volumes are excluded here
    /// because neither is a member of that unit list.</para>
    /// </summary>
    private Level100HudContactSnapshot[] ProjectContacts(WorldSnapshot snapshot)
    {
        Dictionary<int, int> commandedAllegiance = snapshot.Level100ActorMechanics.Actors
            .GroupBy(actor => actor.ActorId.Value)
            .ToDictionary(group => group.Key, group => group.Last().Allegiance);

        float yaw = snapshot.FacingYawMicroRad / 1_000_000f;
        var contacts = new List<Level100HudContactSnapshot>();
        foreach (Level100ActorSnapshot actor in snapshot.Level100Actors.Actors)
        {
            if (!actor.Active ||
                actor.Lifecycle == Level100ActorLifecycle.Destroyed ||
                actor.Trigger.HasValue ||
                StringComparer.Ordinal.Equals(actor.Name, "Player 1"))
            {
                continue;
            }

            SimVector3 position = actor.Pose.PositionMillimeters;
            float deltaX = (position.X - snapshot.PlayerPosition.X) / 1_000f;
            float deltaZ = (position.Z - snapshot.PlayerPosition.Z) / 1_000f;
            Level100ScannerPlacement placement =
                Level100ScannerProjection.Place(deltaX, deltaZ, yaw);

            int allegiance =
                commandedAllegiance.TryGetValue(actor.ActorId.Value, out int commanded)
                    ? commanded
                    : _authoredAllegiance.TryGetValue(actor.DefinitionIdentity, out int authored)
                        ? authored
                        : (int)Level100HudAllegiance.Neutral;

            contacts.Add(new Level100HudContactSnapshot(
                actor.ActorId.Value,
                new SimVector2(position.X, position.Z),
                new SimVector2(
                    actor.Pose.LinearVelocityMillimetersPerTick.X,
                    actor.Pose.LinearVelocityMillimetersPerTick.Z),
                Enum.IsDefined((Level100HudAllegiance)allegiance)
                    ? (Level100HudAllegiance)allegiance
                    : Level100HudAllegiance.Neutral,
                // Medium is retail's DEFAULT blob, not a guess.
                // CHud__LoadTextures (0x00481650) binds
                // hud\ScannerBlobSmall/Medium/Large/RepairPad to CHud slots
                // +0x1a0/+0x1a4/+0x1a8/+0x1ac in that order, and
                // CHud__SelectMarkerTextureIndexByUnitFlags (0x00485830)
                // returns +0x1a4 - Medium - for the unremarkable unit: the one
                // with none of flags 0x8000000, 0x4000, 0x4008100 or 0x40 set
                // at unit+0x34. Small and Large need flags Core does not model,
                // so every contact takes the default. Corroborated on the retail
                // frame: every scanner blob on t025065 has ScannerBlobMedium's
                // 5x5 ink footprint, not Small's 4x4 or Large's 8x8.
                Level100HudContactSize.Medium,
                actor.IsObjective,
                placement.Drawn));
        }

        return [.. contacts];
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
