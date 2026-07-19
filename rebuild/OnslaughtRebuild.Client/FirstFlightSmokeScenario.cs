// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public static class FirstFlightSmokeScenario
{
    // Begin after each objective is active, then follow the bounded left/forward
    // routes used by the copied-retail observer. Each forward hold stops at
    // Core's trigger; one later fire tick proves the demonstrated weapon gate.
    private const int TargetZoneInputStartTick =
        SimulationConstants.Level100TargetZone1ActivationTick + 57;
    private const int LeftTicks = 216;
    private const int ForwardTicks = 469;
    private const int FiringRangeInputStartTick = 1_995;
    private const int FiringRangeLeftTicks = 45;
    private const int FiringRangeForwardTicks = 459;
    private const int PulseCannonProofTick = 3_139;
    public const int DurationTicks = 3_228;

    public static InteractiveInput GetInputForTick(int tick)
    {
        if (tick < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(tick));
        }

        if (tick < TargetZoneInputStartTick)
        {
            return InteractiveInput.Idle;
        }

        int routeTick = tick - TargetZoneInputStartTick;
        if (routeTick < LeftTicks)
        {
            return new InteractiveInput(-1, 0, false, false, false);
        }

        if (routeTick < LeftTicks + ForwardTicks)
        {
            return new InteractiveInput(0, 1, false, false, false);
        }

        if (tick >= FiringRangeInputStartTick &&
            tick < FiringRangeInputStartTick + FiringRangeLeftTicks)
        {
            return new InteractiveInput(-1, 0, false, false, false);
        }

        if (tick >= FiringRangeInputStartTick + FiringRangeLeftTicks &&
            tick < FiringRangeInputStartTick + FiringRangeLeftTicks + FiringRangeForwardTicks)
        {
            return new InteractiveInput(0, 1, false, false, false);
        }

        if (tick == PulseCannonProofTick)
        {
            return new InteractiveInput(0, 0, true, false, false);
        }

        return InteractiveInput.Idle;
    }
}
