// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public static class FirstFlightSmokeScenario
{
    private const int PlayingStartTick = SimulationConstants.Level100PowerActivationTick;
    private const int PlayingDurationTicks = 60;
    public const int DurationTicks = SimulationConstants.Level100TargetZone1InstructionStartTick + 30;

    public static InteractiveInput GetInputForTick(int tick)
    {
        if (tick < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(tick));
        }

        if (tick < PlayingStartTick || tick >= PlayingStartTick + PlayingDurationTicks)
        {
            return InteractiveInput.Idle;
        }

        int playingTick = tick - PlayingStartTick;
        if (playingTick < 30)
        {
            return new InteractiveInput(0, 1, false, false, false);
        }

        if (playingTick < 60)
        {
            return new InteractiveInput(0, 0, false, false, false, LookX: 1);
        }

        return InteractiveInput.Idle;
    }
}
