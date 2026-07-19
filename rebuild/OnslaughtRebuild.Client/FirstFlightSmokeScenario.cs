// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public static class FirstFlightSmokeScenario
{
    // Begin after Target Zone 1 is active, then follow the same left/forward
    // route used by the copied-retail observer. The shorter forward hold stops
    // at Core's trigger rather than continuing past the objective.
    private const int TargetZoneInputStartTick =
        SimulationConstants.Level100TargetZone1ActivationTick + 57;
    private const int LeftTicks = 216;
    private const int ForwardTicks = 469;
    public const int DurationTicks = 1_995;

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

        return InteractiveInput.Idle;
    }
}
