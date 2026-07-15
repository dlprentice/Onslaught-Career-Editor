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
    WorldSnapshot CurrentSnapshot)
{
    public double InterpolationAlpha =>
        (double)InterpolationPhase / InterpolationPhaseScale;
}

public sealed class InteractiveSession
{
    public const long PhaseUnitsPerStep = TimeSpan.TicksPerSecond;
    public const long MaximumFrameElapsedTicks = TimeSpan.TicksPerSecond / 4;

    private readonly Simulation _simulation;
    private InteractiveInput _input;
    private bool _toggleLevelWasHeld;
    private bool _resetLevelWasHeld;
    private bool _toggleEdgePending;
    private bool _resetEdgePending;
    private bool _firePulsePending;
    private sbyte _movementPulseX;
    private sbyte _movementPulseZ;
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

    public InteractiveSession(uint seed)
    {
        _simulation = new Simulation(seed);
        PreviousSnapshot = _simulation.Snapshot;
        CurrentSnapshot = PreviousSnapshot;
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
        _movementPulseZ != 0;

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
    }

    public FrameAdvanceResult AdvanceFrame(TimeSpan elapsed)
    {
        return AdvanceFrameTicks(elapsed.Ticks);
    }

    public FrameAdvanceResult AdvanceFrameTicks(long elapsedTicks)
    {
        if (elapsedTicks < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(elapsedTicks), "Elapsed time cannot be negative.");
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
        while (_interpolationPhase >= PhaseUnitsPerStep)
        {
            bool firstStep = stepsAdvanced == 0;
            bool firePulse = firstStep && _firePulsePending;
            sbyte moveX = _input.MoveX;
            sbyte moveZ = _input.MoveZ;
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
            }

            if (_input.FireHeld)
            {
                _fireHeldTicksSampled++;
            }

            PreviousSnapshot = CurrentSnapshot;
            // Look is level-sampled every Core step while observed (same as Move).
            CurrentSnapshot = _simulation.Step(
                new SimInput(moveX, moveZ, actions, _input.LookX));
            _interpolationPhase -= PhaseUnitsPerStep;
            _totalSteps++;
            stepsAdvanced++;
        }

        return new FrameAdvanceResult(
            stepsAdvanced,
            frameTimeCapped,
            _interpolationPhase,
            PhaseUnitsPerStep,
            PreviousSnapshot,
            CurrentSnapshot);
    }
}
