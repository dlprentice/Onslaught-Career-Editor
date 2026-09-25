// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Client.Tests;

public sealed class PlatformInputEdgeStateTests
{
    [Fact]
    public void HeldKeyReadTracksPressAndRelease()
    {
        var state = new PlatformInputEdgeState();

        state.ObserveKey(0x51, pressed: true, echo: false);
        Assert.Equal(1, state.GetHeldKey(0x51));

        state.ObserveKey(0x51, pressed: false, echo: false);
        Assert.Equal(0, state.GetHeldKey(0x51));
    }

    [Fact]
    public void ConsumeKeyOnceReturnsTheLatchedByteAndClearsOnlyThatKey()
    {
        var state = new PlatformInputEdgeState();
        state.ObserveKey(0x51, pressed: true, echo: false);
        state.ObserveKey(0x52, pressed: true, echo: false);

        Assert.Equal(1, state.ConsumeKeyOnce(0x51));
        Assert.Equal(0, state.ConsumeKeyOnce(0x51));
        Assert.Equal(1, state.ConsumeKeyOnce(0x52));
        Assert.Equal(1, state.GetHeldKey(0x51));
    }

    [Fact]
    public void JoyButtonRisingEdgeComparesPreviousAndCurrentFrameBytes()
    {
        var state = new PlatformInputEdgeState();

        state.ObserveJoyButton(joypad: 2, button: 7, value: 0x80);

        Assert.Equal(0, state.GetPreviousJoyButton(2, 7));
        Assert.Equal(0x80, state.GetCurrentJoyButton(2, 7));
        Assert.True(state.IsJoyButtonRising(2, 7));

        state.AdvanceFrame();

        Assert.Equal(0x80, state.GetPreviousJoyButton(2, 7));
        Assert.False(state.IsJoyButtonRising(2, 7));
        Assert.Equal(1, state.FrameIndex);
    }

    [Fact]
    public void JoyButtonHeldReadsTheCurrentByteAcrossFrames()
    {
        var state = new PlatformInputEdgeState();
        state.ObserveJoyButton(joypad: 0, button: 3, value: 0x80);

        state.AdvanceFrame();

        Assert.True(state.IsJoyButtonHeld(0, 3));
        Assert.Equal(0x80, state.GetCurrentJoyButton(0, 3));
    }

    [Fact]
    public void JoyButtonFallingEdgeRequiresAPreviouslyHeldByte()
    {
        var state = new PlatformInputEdgeState();
        state.ObserveJoyButton(joypad: 1, button: 4, value: 0x80);
        state.AdvanceFrame();

        state.ObserveJoyButton(joypad: 1, button: 4, value: 0);

        Assert.True(state.IsJoyButtonFalling(1, 4));
        Assert.False(state.IsJoyButtonHeld(1, 4));

        state.AdvanceFrame();
        Assert.False(state.IsJoyButtonFalling(1, 4));
    }

    [Fact]
    public void ResetClearsEveryByteAtAnExplicitGenerationBoundary()
    {
        var state = new PlatformInputEdgeState();
        state.ObserveKey(0x51, pressed: true, echo: false);
        state.ObserveJoyButton(joypad: 0, button: 1, value: 0x80);
        state.AdvanceFrame();
        state.ObserveJoyButton(joypad: 0, button: 1, value: 0);

        state.Reset();

        Assert.Equal(0, state.GetHeldKey(0x51));
        Assert.Equal(0, state.ConsumeKeyOnce(0x51));
        Assert.Equal(0, state.GetPreviousJoyButton(0, 1));
        Assert.Equal(0, state.GetCurrentJoyButton(0, 1));
        Assert.Equal(1, state.FrameIndex);
        Assert.Equal(1, state.ResetGeneration);
    }

    [Fact]
    public void KeyEchoDoesNotCreateAHeldOrConsumeOnceByte()
    {
        var state = new PlatformInputEdgeState();

        state.ObserveKey(0x51, pressed: true, echo: true);

        Assert.Equal(0, state.GetHeldKey(0x51));
        Assert.Equal(0, state.ConsumeKeyOnce(0x51));
    }

    [Fact]
    public void DistinctNonEchoPressEventsCanEachLatchOnce()
    {
        var state = new PlatformInputEdgeState();
        state.ObserveKey(0x51, pressed: true, echo: false);
        Assert.Equal(1, state.ConsumeKeyOnce(0x51));

        state.ObserveKey(0x51, pressed: true, echo: false);

        Assert.Equal(1, state.ConsumeKeyOnce(0x51));
    }

    [Fact]
    public void InteractiveSessionConsumesAKeyOnceThroughItsExistingQueue()
    {
        var session = new InteractiveSession(
            0x4F4E534Cu,
            Level100TestActorDefinitions.Create());
        Assert.IsType<PlatformInputEdgeState>(session.PlatformInput);
        const int toggleKey = 0x51;
        session.PlatformInput.ObserveKey(toggleKey, pressed: true, echo: false);

        if (session.PlatformInput.ConsumeKeyOnce(toggleKey) != 0)
        {
            session.QueueToggleMode();
        }
        session.AdvanceFrameTicks(500_000);

        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
        Assert.Equal(1, session.PlatformInput.FrameIndex);

        session.ReleaseAllInput();
        Assert.Equal(1, session.PlatformInput.ResetGeneration);
        Assert.Equal(0, session.PlatformInput.GetHeldKey(toggleKey));
    }

    [Fact]
    public void InteractiveSessionBorrowsTheSuppliedOwnerAcrossFramePauseAndFocusBoundaries()
    {
        var owner = new RecordingPlatformInputEdges();
        const int toggleKey = 0x51;
        owner.ObserveKey(toggleKey, pressed: true, echo: false);
        owner.ObserveJoyButton(joypad: 0, button: 7, value: 0x80);
        var session = new InteractiveSession(
            0x4F4E534Cu,
            Level100TestActorDefinitions.Create(),
            platformInput: owner);

        Assert.Same(owner, session.PlatformInput);
        Assert.Empty(owner.Lifecycle);
        Assert.Equal(1, session.PlatformInput.GetHeldKey(toggleKey));
        Assert.True(session.PlatformInput.IsJoyButtonRising(0, 7));
        if (session.PlatformInput.ConsumeKeyOnce(toggleKey) != 0)
        {
            session.QueueToggleMode();
        }
        FrameAdvanceResult first = session.AdvanceFrameTicks(500_000);
        Assert.Equal(1, first.StepsAdvanced);
        Assert.Equal(1, session.Metrics.ToggleEdgesConsumed);
        Assert.Equal(1, owner.FrameIndex);
        Assert.Equal(0x80, owner.GetPreviousJoyButton(0, 7));

        session.SetAuthenticMenuPaused(true);
        Assert.Equal(1, owner.ResetGeneration);
        Assert.Equal(0, owner.GetHeldKey(toggleKey));
        Assert.Equal(0, owner.GetPreviousJoyButton(0, 7));
        session.SetAuthenticMenuPaused(true);
        Assert.Equal(1, owner.ResetGeneration);
        FrameAdvanceResult paused = session.AdvanceFrameTicks(500_000);
        Assert.Equal(0, paused.StepsAdvanced);
        Assert.Equal(first.CurrentSnapshot.Tick, paused.CurrentSnapshot.Tick);
        Assert.Equal(2, owner.FrameIndex);

        session.SetAuthenticMenuPaused(false);
        Assert.Equal(2, owner.ResetGeneration);
        owner.ObserveKey(toggleKey, pressed: true, echo: false);
        session.SuspendInputUntilReleased(); // Existing focus-loss route.
        Assert.Equal(3, owner.ResetGeneration);
        Assert.Equal(0, owner.GetHeldKey(toggleKey));
        Assert.Equal(0, owner.ConsumeKeyOnce(toggleKey));
        Assert.True(session.InputSuspendedUntilReleased);
        session.ReleaseAllInput();
        Assert.Equal(4, owner.ResetGeneration);
        Assert.False(session.InputSuspendedUntilReleased);
        Assert.Equal(0, session.AdvanceFrameTicks(0).StepsAdvanced);
        Assert.Equal(3, owner.FrameIndex);
        Assert.Same(owner, session.PlatformInput);
        Assert.Equal(
            new[] { "advance", "reset", "advance", "reset", "reset", "reset", "advance" },
            owner.Lifecycle);
        PlatformInputEdgeSnapshot captured = session.PlatformInput.Capture();
        Assert.Equal(owner.FrameIndex, captured.FrameIndex);
        Assert.Equal(owner.ResetGeneration, captured.ResetGeneration);
        Assert.Empty(captured.HeldKeys);
        Assert.Empty(captured.CurrentJoyButtons);
    }

    [Fact]
    public void CaptureOrdersEquivalentStateIndependentlyOfEventInsertionOrder()
    {
        var first = new PlatformInputEdgeState();
        first.ObserveKey(9, pressed: true, echo: false);
        first.ObserveKey(2, pressed: true, echo: false);
        first.ObserveJoyButton(joypad: 3, button: 8, value: 0x80);
        first.ObserveJoyButton(joypad: 0, button: 4, value: 0x80);

        var second = new PlatformInputEdgeState();
        second.ObserveJoyButton(joypad: 0, button: 4, value: 0x80);
        second.ObserveJoyButton(joypad: 3, button: 8, value: 0x80);
        second.ObserveKey(2, pressed: true, echo: false);
        second.ObserveKey(9, pressed: true, echo: false);

        PlatformInputEdgeSnapshot firstSnapshot = first.Capture();
        PlatformInputEdgeSnapshot secondSnapshot = second.Capture();

        Assert.Equal(firstSnapshot.HeldKeys, secondSnapshot.HeldKeys);
        Assert.Equal(firstSnapshot.ConsumeOnceKeys, secondSnapshot.ConsumeOnceKeys);
        Assert.Equal(firstSnapshot.CurrentJoyButtons, secondSnapshot.CurrentJoyButtons);
    }

    [Fact]
    public void GodotEventsFeedTheStateBeforeExistingSessionQueuesConsumeThem()
    {
        string source = File.ReadAllText(Path.Combine(
            AppContext.BaseDirectory,
            "godot-pause-source",
            "FirstFlightGame.cs"));
        int inputStart = source.IndexOf(
            "public override void _Input(InputEvent inputEvent)",
            StringComparison.Ordinal);
        int inputEnd = source.IndexOf(
            "private bool HandleAuthenticPauseInput",
            inputStart,
            StringComparison.Ordinal);
        string input = source[inputStart..inputEnd];

        AssertOccursInOrder(
            input,
            "ObservePlatformInputEvent(inputEvent);",
            "_session.PlatformInput.ConsumeKeyOnce",
            "_session.QueueMovementPulse",
            "_session.QueueToggleMode");
        Assert.Contains("_session.PlatformInput.IsJoyButtonRising", input, StringComparison.Ordinal);
        Assert.Contains("_session.PlatformInput.ObserveKey", source, StringComparison.Ordinal);
        Assert.Contains("_session.PlatformInput.ObserveJoyButton", source, StringComparison.Ordinal);
    }

    private static void AssertOccursInOrder(string text, params string[] values)
    {
        int cursor = 0;
        foreach (string value in values)
        {
            int index = text.IndexOf(value, cursor, StringComparison.Ordinal);
            Assert.True(index >= cursor, $"Expected '{value}' at or after offset {cursor}.");
            cursor = index + value.Length;
        }
    }

    private sealed class RecordingPlatformInputEdges : IPlatformInputEdges
    {
        private readonly PlatformInputEdgeState _state = new();

        public List<string> Lifecycle { get; } = [];

        public long FrameIndex => _state.FrameIndex;

        public long ResetGeneration => _state.ResetGeneration;

        public void ObserveKey(int keyCode, bool pressed, bool echo) =>
            _state.ObserveKey(keyCode, pressed, echo);

        public byte GetHeldKey(int keyCode) => _state.GetHeldKey(keyCode);

        public byte ConsumeKeyOnce(int keyCode) => _state.ConsumeKeyOnce(keyCode);

        public void ObserveJoyButton(int joypad, int button, byte value) =>
            _state.ObserveJoyButton(joypad, button, value);

        public byte GetPreviousJoyButton(int joypad, int button) =>
            _state.GetPreviousJoyButton(joypad, button);

        public byte GetCurrentJoyButton(int joypad, int button) =>
            _state.GetCurrentJoyButton(joypad, button);

        public bool IsJoyButtonRising(int joypad, int button) =>
            _state.IsJoyButtonRising(joypad, button);

        public bool IsJoyButtonHeld(int joypad, int button) =>
            _state.IsJoyButtonHeld(joypad, button);

        public bool IsJoyButtonFalling(int joypad, int button) =>
            _state.IsJoyButtonFalling(joypad, button);

        public void AdvanceFrame()
        {
            Lifecycle.Add("advance");
            _state.AdvanceFrame();
        }

        public void Reset()
        {
            Lifecycle.Add("reset");
            _state.Reset();
        }

        public PlatformInputEdgeSnapshot Capture() => _state.Capture();
    }
}
