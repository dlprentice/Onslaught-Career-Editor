// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client;

/// <summary>
/// The existing platform-input byte and frame contract, independent of its
/// implementation language. InteractiveSession borrows this owner; its host
/// retains responsibility for any native resource lifetime.
/// </summary>
public interface IPlatformInputEdges
{
    long FrameIndex { get; }

    long ResetGeneration { get; }

    void ObserveKey(int keyCode, bool pressed, bool echo);

    byte GetHeldKey(int keyCode);

    byte ConsumeKeyOnce(int keyCode);

    void ObserveJoyButton(int joypad, int button, byte value);

    byte GetPreviousJoyButton(int joypad, int button);

    byte GetCurrentJoyButton(int joypad, int button);

    bool IsJoyButtonRising(int joypad, int button);

    bool IsJoyButtonHeld(int joypad, int button);

    bool IsJoyButtonFalling(int joypad, int button);

    void AdvanceFrame();

    void Reset();

    PlatformInputEdgeSnapshot Capture();
}
