// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public static class Level100MissionTiming
{
    // Consumed evidence only: supported 100_res_PC.aya SHA-256
    // ed6350c0e214d00ab1bf6a7bd137fba3e77d0afe19a6dc4c0607f56ac037496a;
    // exact LevelScript object SHA-256
    // 73eb349b9c4b5c5d7294b2183cd4d4aebe024c5d3c8cda9be685bd1463ed6fb1;
    // readable LevelScript.msl SHA-256
    // d51f8864564b5bde872092ec822df5af49daac16563f500719135f1a8c6c04a4.
    // Steam Ghidra establishes the object loader,
    // opcode dispatch (0x0052d3d0), saved-state restore (0x00533840), Pause
    // (0x00537c70), message-wait path (0x005375f0), and terminal functions
    // (0x0046f2f0/0x0046f430). Voice ticks are shipped Ogg granules plus the
    // evidenced 18-tick wait post-roll. No retail executable is a play dependency.

    public const int AuthoredTriggerRadiusMillimeters = 5_000;
    public const int HealthPollCadenceTicks = SimulationConstants.TicksPerSecond;
    public const int SuccessCountdownTicks = 5 * SimulationConstants.TicksPerSecond;
    public const int FailureCountdownTicks = 5 * SimulationConstants.TicksPerSecond;
    public const int FailureMenuDelayTicks = SimulationConstants.TicksPerSecond / 2;

    public static SimVector2 TriggerPosition(Level100MissionTrigger trigger) => trigger switch
    {
        Level100MissionTrigger.TargetZone1 => SimulationConstants.Level100TargetZone1Position,
        Level100MissionTrigger.FiringRange => SimulationConstants.Level100FiringRangePosition,
        Level100MissionTrigger.TargetZone2 => new(-56_688, -62_250),
        Level100MissionTrigger.TargetZone3 => new(-57_938, 2_625),
        Level100MissionTrigger.TargetZone4 => new(0, -31),
        _ => throw new ArgumentOutOfRangeException(nameof(trigger)),
    };

    public static bool RequiresNotInJetMode(Level100MissionTrigger trigger) => trigger is
        Level100MissionTrigger.TargetZone2 or
        Level100MissionTrigger.TargetZone3 or
        Level100MissionTrigger.TargetZone4;

    public static Level100MissionJetModeState JetModeState(
        VehicleMode mode,
        VehicleTransition transition)
    {
        // The released side scripts test InJetMode()==FALSE, not Walker mode.
        // Core changes mode to Jet only when WalkerToJet completes, so all
        // transitional/non-jet states remain eligible, matching that predicate.
        _ = transition;
        return mode == VehicleMode.Jet
            ? Level100MissionJetModeState.InJetMode
            : Level100MissionJetModeState.NotInJetMode;
    }

    internal static int PauseTicks(float seconds)
    {
        if (!float.IsFinite(seconds) || seconds < 0)
        {
            throw new InvalidOperationException("The released LevelScript requested an invalid pause.");
        }

        return checked((int)MathF.Round(
            seconds * SimulationConstants.TicksPerSecond,
            MidpointRounding.AwayFromZero));
    }

    internal static int MessagePlaybackTicks(int messageId) => messageId switch
    {
        292562 => 169,       // HUD_01
        293386 => 210,       // HUD_02
        294210 => 265,       // HUD_03
        295034 => 264,       // HUD_04
        295858 => 260,       // HUD_05
        296682 => 183,       // HUD_06
        297506 => 235,       // HUD_07
        -1575499396 => 163,  // TUTORIAL_MESSAGE_LOG
        -257967449 => 65,    // TUTORIAL_TECHNICIAN_01
        82987417 => 215,     // TUTORIAL_13_MOD
        4422830 => 160,      // TUTORIAL_01
        175347826 => 138,    // TUTORIAL_SCANNER
        4458134 => 180,      // TUTORIAL_02
        4493438 => 97,       // TUTORIAL_03
        1339691000 => 221,   // TUTORIAL_PULSE_CANNON
        669198996 => 112,    // TUTORIAL_OPEN_FIRE
        -1715818922 => 243,  // TUTORIAL_PULSE_CANNON_2
        -1616775312 => 239,  // TUTORIAL_VULCAN_CANNON
        -1860407443 => 121,  // TUTORIAL_OPEN_FIRE_2
        864965454 => 182,    // TUTORIAL_VULCAN_CANNON_2
        4564046 => 281,      // TUTORIAL_05
        22775962 => 190,     // TUTORIAL_ZOOM
        667656903 => 201,    // TUTORIAL_DODGE_MOD
        150647733 => 165,    // TUTORIAL_DODGE_2
        151778876 => 244,    // TUTORIAL_DODGE_3
        623538785 => 136,    // TUTORIAL_DODGE_BAD
        1326027769 => 129,   // TUTORIAL_DODGE_GOOD
        4528742 => 262,      // TUTORIAL_04
        165861931 => 228,    // TUTORIAL_LANDING
        4599350 => 226,      // TUTORIAL_06
        1062059777 => 130,   // TUTORIAL_THROTTLE_MOD
        4475837 => 133,      // TUTORIAL_12
        4705262 => 213,      // TUTORIAL_09
        4634654 => 168,      // TUTORIAL_07
        80260569 => 197,     // TUTORIAL_STRAFE
        4669958 => 227,      // TUTORIAL_08
        4440532 => 225,      // TUTORIAL_11
        162342028 => 168,    // TUTORIAL_ABORTED
        150940633 => 109,    // TUTORIAL_BROKE_1
        152071864 => 122,    // TUTORIAL_BROKE_2
        153203095 => 127,    // TUTORIAL_BROKE_3
        -1455850811 => 114,  // TUTORIAL_HELP_PLAYER
        4405227 => 199,      // TUTORIAL_10
        _ => throw new InvalidOperationException(
            $"Released Level 100 message id {messageId} has no evidenced wait duration."),
    };
}
