// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public readonly record struct InteractiveInput(
    sbyte MoveX,
    sbyte MoveZ,
    bool FireHeld,
    bool ToggleModeHeld,
    bool ResetHeld)
{
    public static InteractiveInput Idle => new(0, 0, false, false, false);

    public void Validate()
    {
        new SimInput(MoveX, MoveZ).Validate();
    }
}
