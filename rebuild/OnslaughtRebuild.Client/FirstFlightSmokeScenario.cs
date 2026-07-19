// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public static class FirstFlightSmokeScenario
{
    private const int PlayingStartTick = SimulationConstants.Level100OpeningPanTicks;
    private const int PlayingDurationTicks = 120;
    public const int DurationTicks = (SimulationConstants.Level100OpeningPanTicks * 2) + 61;

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
            return new InteractiveInput(0, 1, true, false, false);
        }

        if (playingTick == 30)
        {
            return new InteractiveInput(0, 0, false, true, false);
        }

        if (playingTick < 45)
        {
            return InteractiveInput.Idle;
        }

        if (playingTick < 60)
        {
            return new InteractiveInput(1, 0, false, false, false);
        }

        if (playingTick == 60)
        {
            return new InteractiveInput(0, 0, true, false, true);
        }

        if (playingTick < 91)
        {
            return new InteractiveInput(0, 1, true, false, false);
        }

        return InteractiveInput.Idle;
    }
}
