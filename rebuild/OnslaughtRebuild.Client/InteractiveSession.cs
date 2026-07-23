// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client;

public readonly record struct InteractiveSessionMetrics(
    long TotalSteps,
    long ToggleEdgesConsumed,
    long ResetEdgesConsumed,
    long ResetGeneration,
    long FireHeldTicksSampled,
    long FirePulseEdgesConsumed,
    long MovementPulseEdgesConsumed,
    long CappedFrameCount,
    long DroppedElapsedTicks);

public readonly record struct FrameAdvanceResult(
    int StepsAdvanced,
    bool FrameTimeCapped,
    long InterpolationPhase,
    long InterpolationPhaseScale,
    WorldSnapshot PreviousSnapshot,
    WorldSnapshot CurrentSnapshot,
    IReadOnlyList<Level100MissionEvent> Level100MissionEvents)
{
    public double InterpolationAlpha =>
        (double)InterpolationPhase / InterpolationPhaseScale;
}

public sealed class InteractiveSession
{
    public const long PhaseUnitsPerStep = TimeSpan.TicksPerSecond;
    public const long MaximumFrameElapsedTicks = TimeSpan.TicksPerSecond / 4;

    // Steam CController::DoMappings maps a centered mouse displacement with
    // sensitivity 1.5 and scalar 0.004333333, then clamps the analogue axis.
    // Input__UpdateCursorCenterWithWindowScale recenters by 10/17 at 20 Hz;
    // 702049/1000000 is the time-equivalent retention at Core's 30 Hz step.
    private const int PointerOffsetScale = 1_000;
    private const int PointerOffsetRetentionNumerator = 702_049;
    private const int PointerOffsetRetentionDenominator = 1_000_000;
    private const int PointerAxisNumerator = 13;
    private const int PointerAxisDenominator = 2_000;
    private const int MaximumPointerOffsetMilliPixels = 1_000_000;

    private readonly Simulation _simulation;
    private readonly List<Level100MissionEvent> _undeliveredLevel100MissionEvents = [];
    private InteractiveInput _input;
    private bool _toggleLevelWasHeld;
    private bool _resetLevelWasHeld;
    private bool _toggleEdgePending;
    private bool _resetEdgePending;
    private bool _firePulsePending;
    private sbyte _movementPulseX;
    private sbyte _movementPulseZ;
    private sbyte _lookPulseX;
    private sbyte _lookPulseY;
    private int _pointerOffsetXMilliPixels;
    private int _pointerOffsetYMilliPixels;
    private bool _inputSuspendedUntilReleased;
    private long _interpolationPhase;
    private long _totalSteps;
    private long _toggleEdgesConsumed;
    private long _resetEdgesConsumed;
    private long _fireHeldTicksSampled;
    private long _firePulseEdgesConsumed;
    private long _movementPulseEdgesConsumed;
    private long _cappedFrameCount;
    private long _droppedElapsedTicks;

    public InteractiveSession(uint seed, Level100ActorDefinitionSet level100ActorDefinitions)
    {
        _simulation = new Simulation(seed, level100ActorDefinitions);
        PreviousSnapshot = _simulation.Snapshot;
        CurrentSnapshot = PreviousSnapshot;
        _undeliveredLevel100MissionEvents.AddRange(
            CurrentSnapshot.Level100MissionEvents);
    }

    public WorldSnapshot PreviousSnapshot { get; private set; }

    public WorldSnapshot CurrentSnapshot { get; private set; }

    public long InterpolationPhase => _interpolationPhase;

    public bool InputSuspendedUntilReleased => _inputSuspendedUntilReleased;

    public bool HasHeldOrPendingInput =>
        _input != InteractiveInput.Idle ||
        _toggleLevelWasHeld ||
        _resetLevelWasHeld ||
        _toggleEdgePending ||
        _resetEdgePending ||
        _firePulsePending ||
        _movementPulseX != 0 ||
        _movementPulseZ != 0 ||
        _lookPulseX != 0 ||
        _lookPulseY != 0 ||
        _pointerOffsetXMilliPixels != 0 ||
        _pointerOffsetYMilliPixels != 0 ||
        _input.LookX != 0 ||
        _input.LookY != 0;

    public InteractiveSessionMetrics Metrics => new(
        _totalSteps,
        _toggleEdgesConsumed,
        _resetEdgesConsumed,
        _resetEdgesConsumed,
        _fireHeldTicksSampled,
        _firePulseEdgesConsumed,
        _movementPulseEdgesConsumed,
        _cappedFrameCount,
        _droppedElapsedTicks);

    public void ObserveInput(InteractiveInput input)
    {
        input.Validate();

        if (_inputSuspendedUntilReleased)
        {
            if (input != InteractiveInput.Idle)
            {
                return;
            }

            _inputSuspendedUntilReleased = false;
        }

        if (input.ToggleModeHeld && !_toggleLevelWasHeld)
        {
            _toggleEdgePending = true;
        }

        if (input.ResetHeld && !_resetLevelWasHeld)
        {
            _resetEdgePending = true;
        }

        _toggleLevelWasHeld = input.ToggleModeHeld;
        _resetLevelWasHeld = input.ResetHeld;
        _input = input;
    }

    public void QueueToggleMode()
    {
        if (_inputSuspendedUntilReleased)
        {
            return;
        }

        _toggleEdgePending = true;
    }

    public void QueueReset()
    {
        if (_inputSuspendedUntilReleased)
        {
            return;
        }

        _resetEdgePending = true;
    }

    public void QueueFirePulse()
    {
        if (_inputSuspendedUntilReleased)
        {
            return;
        }

        _firePulsePending = true;
    }

    public void QueueMovementPulse(sbyte moveX, sbyte moveZ)
    {
        new SimInput(moveX, moveZ).Validate();
        if (moveX == 0 && moveZ == 0)
        {
            throw new ArgumentException("A movement pulse must contain a nonzero axis.");
        }

        if (_inputSuspendedUntilReleased)
        {
            return;
        }

        if (moveX != 0)
        {
            _movementPulseX = moveX;
        }

        if (moveZ != 0)
        {
            _movementPulseZ = moveZ;
        }
    }

    public void QueueLookPulse(sbyte lookX, sbyte lookY)
    {
        new SimInput(0, 0, LookX: lookX, LookY: lookY).Validate();
        if (lookX == 0 && lookY == 0)
        {
            throw new ArgumentException("A look pulse must contain a nonzero axis.");
        }

        if (_inputSuspendedUntilReleased)
        {
            return;
        }

        if (lookX != 0)
        {
            _lookPulseX = lookX;
        }

        if (lookY != 0)
        {
            _lookPulseY = lookY;
        }
    }

    public void QueuePointerMotionMilliPixels(int deltaX, int deltaY)
    {
        if (deltaX == 0 && deltaY == 0)
        {
            throw new ArgumentException("Pointer motion must contain a nonzero axis.");
        }

        if (_inputSuspendedUntilReleased)
        {
            return;
        }

        _pointerOffsetXMilliPixels = AddPointerOffset(_pointerOffsetXMilliPixels, deltaX);
        _pointerOffsetYMilliPixels = AddPointerOffset(_pointerOffsetYMilliPixels, deltaY);
    }

    public void ReleaseAllInput()
    {
        ClearInputState();
        _inputSuspendedUntilReleased = false;
    }

    public void SuspendInputUntilReleased()
    {
        ClearInputState();
        _inputSuspendedUntilReleased = true;
    }

    private void ClearInputState()
    {
        _input = InteractiveInput.Idle;
        _toggleLevelWasHeld = false;
        _resetLevelWasHeld = false;
        _toggleEdgePending = false;
        _resetEdgePending = false;
        _firePulsePending = false;
        _movementPulseX = 0;
        _movementPulseZ = 0;
        _lookPulseX = 0;
        _lookPulseY = 0;
        _pointerOffsetXMilliPixels = 0;
        _pointerOffsetYMilliPixels = 0;
    }

    public FrameAdvanceResult AdvanceFrame(TimeSpan elapsed)
    {
        return AdvanceFrameTicks(elapsed.Ticks);
    }

    public FrameAdvanceResult AdvanceFrameTicks(long elapsedTicks)
    {
        return AdvanceFrameTicks(elapsedTicks, null);
    }

    public FrameAdvanceResult AdvanceFrameTicks(
        long elapsedTicks,
        IReadOnlyList<Level100SimulationFact>? level100Facts)
    {
        if (elapsedTicks < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(elapsedTicks), "Elapsed time cannot be negative.");
        }

        long boundedElapsedTicks = Math.Min(elapsedTicks, MaximumFrameElapsedTicks);
        long prospectivePhase = checked(
            _interpolationPhase +
            (boundedElapsedTicks * SimulationConstants.TicksPerSecond));
        if (level100Facts is { Count: > 0 } && prospectivePhase < PhaseUnitsPerStep)
        {
            throw new ArgumentException(
                "Level 100 facts must be supplied on a frame that advances a simulation step.",
                nameof(level100Facts));
        }

        bool frameTimeCapped = elapsedTicks > MaximumFrameElapsedTicks;
        if (frameTimeCapped)
        {
            _cappedFrameCount++;
            _droppedElapsedTicks += elapsedTicks - MaximumFrameElapsedTicks;
            elapsedTicks = MaximumFrameElapsedTicks;
        }

        _interpolationPhase = checked(
            _interpolationPhase + (elapsedTicks * SimulationConstants.TicksPerSecond));

        int stepsAdvanced = 0;
        var level100MissionEvents = new List<Level100MissionEvent>();
        level100MissionEvents.AddRange(_undeliveredLevel100MissionEvents);
        while (_interpolationPhase >= PhaseUnitsPerStep)
        {
            bool firstStep = stepsAdvanced == 0;
            bool firePulse = firstStep && _firePulsePending;
            sbyte moveX = _input.MoveX;
            sbyte moveZ = _input.MoveZ;
            sbyte lookX = _input.LookX;
            sbyte lookY = _input.LookY;
            _pointerOffsetXMilliPixels = RetainPointerOffset(_pointerOffsetXMilliPixels);
            _pointerOffsetYMilliPixels = RetainPointerOffset(_pointerOffsetYMilliPixels);
            short pointerLookX = ToPointerAxisPermille(_pointerOffsetXMilliPixels);
            short pointerLookY = ToPointerAxisPermille(_pointerOffsetYMilliPixels);
            if (firstStep)
            {
                if (moveX == 0)
                {
                    moveX = _movementPulseX;
                }

                if (moveZ == 0)
                {
                    moveZ = _movementPulseZ;
                }

                if (lookX == 0)
                {
                    lookX = _lookPulseX;
                }

                if (lookY == 0)
                {
                    lookY = _lookPulseY;
                }
            }

            SimActions actions = _input.FireHeld || firePulse ? SimActions.Fire : SimActions.None;
            if (firstStep)
            {
                if (_toggleEdgePending)
                {
                    actions |= SimActions.ToggleMode;
                    _toggleEdgesConsumed++;
                }

                if (_resetEdgePending)
                {
                    actions |= SimActions.Reset;
                    _resetEdgesConsumed++;
                }

                if (_firePulsePending)
                {
                    _firePulseEdgesConsumed++;
                }

                if (_movementPulseX != 0 || _movementPulseZ != 0)
                {
                    _movementPulseEdgesConsumed++;
                }

                _toggleEdgePending = false;
                _resetEdgePending = false;
                _firePulsePending = false;
                _movementPulseX = 0;
                _movementPulseZ = 0;
                _lookPulseX = 0;
                _lookPulseY = 0;
            }

            if (_input.FireHeld)
            {
                _fireHeldTicksSampled++;
            }

            PreviousSnapshot = CurrentSnapshot;
            // Held digital look is level-sampled. Pointer motion enters as a
            // magnitude-preserving analogue axis and recenters across steps.
            CurrentSnapshot = _simulation.Step(
                new SimInput(
                    moveX,
                    moveZ,
                    actions,
                    lookX,
                    lookY,
                    pointerLookX,
                    pointerLookY),
                firstStep ? level100Facts : null);
            level100MissionEvents.AddRange(CurrentSnapshot.Level100MissionEvents);
            _interpolationPhase -= PhaseUnitsPerStep;
            _totalSteps++;
            stepsAdvanced++;
        }

        FrameAdvanceResult result = new(
            stepsAdvanced,
            frameTimeCapped,
            _interpolationPhase,
            PhaseUnitsPerStep,
            PreviousSnapshot,
            CurrentSnapshot,
            Array.AsReadOnly(level100MissionEvents.ToArray()));
        _undeliveredLevel100MissionEvents.Clear();
        return result;
    }

    private static int AddPointerOffset(int current, int delta)
    {
        long combined = (long)current + delta;
        return (int)Math.Clamp(
            combined,
            -MaximumPointerOffsetMilliPixels,
            MaximumPointerOffsetMilliPixels);
    }

    private static int RetainPointerOffset(int value)
    {
        long scaled = (long)value * PointerOffsetRetentionNumerator;
        int retained = (int)(scaled >= 0
            ? (scaled + (PointerOffsetRetentionDenominator / 2)) /
                PointerOffsetRetentionDenominator
            : (scaled - (PointerOffsetRetentionDenominator / 2)) /
                PointerOffsetRetentionDenominator);
        return Math.Abs(retained) < PointerOffsetScale / 2 ? 0 : retained;
    }

    private static short ToPointerAxisPermille(int offsetMilliPixels)
    {
        long scaled = (long)offsetMilliPixels * PointerAxisNumerator;
        long rounded = scaled >= 0
            ? (scaled + (PointerAxisDenominator / 2)) / PointerAxisDenominator
            : (scaled - (PointerAxisDenominator / 2)) / PointerAxisDenominator;
        return (short)Math.Clamp(rounded, -1_000, 1_000);
    }
}
