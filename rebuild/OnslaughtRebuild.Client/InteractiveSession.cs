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
    IReadOnlyList<Level100MissionEvent> Level100MissionEvents,
    IReadOnlyList<AquilaFlightEvent> AquilaFlightEvents,
    IReadOnlyList<Level100DestructionEvent> Level100DestructionEvents,
    IReadOnlyList<Level100WeaponFireEvent> Level100WeaponFireEvents)
{
    public double InterpolationAlpha =>
        (double)InterpolationPhase / InterpolationPhaseScale;
}

[Flags]
public enum InteractivePauseReason
{
    None = 0,
    AuthenticMenu = 1,
}

public sealed class InteractiveSession
{
    public const long PhaseUnitsPerStep = TimeSpan.TicksPerSecond;
    public const long MaximumFrameElapsedTicks = TimeSpan.TicksPerSecond / 4;

    // Steam CController::DoMappings maps a centered mouse displacement by
    // g_MouseSensitivity and the scalar 0.004333333, then clamps the analogue
    // axis. Input__UpdateCursorCenterWithWindowScale recenters by 10/17 per
    // 20 Hz update, and Core now RUNS at 20 Hz, so that ratio is used verbatim.
    // It read 702049/1000000 - (10/17)^(2/3) - while Core ran at 30 Hz.
    //
    // The scalar is exactly 13/3000. Verified in the PRISTINE specimen
    // (local-lab/safe-copy-bea-pristine/BEA.exe.original.backup, sha256
    // 74154bfa...) at VA 0x005d97c8 -> file 0x001d97c8, float32
    // 0.004333333112299442. Read it from that file and no other: the installed
    // Steam executable is e7881829... and carries four local patches - see
    // reverse-engineering/binary-analysis/retail-specimen-baseline.md.
    //
    // "Four" was queried in review 2026-07-27 and is CONFIRMED, but only for
    // the STEAM executable - do not carry the number across specimens. Measured
    // by byte diff against its own neighbouring pristine backup: 28 differing
    // bytes in exactly four contiguous runs -
    //     0x06416F..0x064171   3 bytes   version-string pointer
    //     0x129696             1 byte
    //     0x12A644..0x12A647   4 bytes   force_windowed
    //     0x1AA444..0x1AA457  20 bytes   "V%1d.%02d - PATCHED" into padding
    // The maintainer applied these deliberately for his own testing; CLAUDE.md
    // says so and they are not drift.
    //
    // The CAPTURE TARGET is a different specimen and carries only ONE of them:
    // local-lab/safe-copy-bea-pristine/BEA.exe (e1436ef7...) differs from
    // pristine in 4 bytes at 0x12A644 alone, the same force_windowed site. A
    // reviewer diffing the safe-copy pair therefore finds one patch and can
    // conclude "four" is wrong; it is not, it is a statement about the Steam
    // install.
    //
    // SENSITIVITY WAS 1.5 HERE, AND THAT IS NOT A RETAIL VALUE. The old
    // 13/2000 is exactly 1.5 x 13/3000. Retail's slider is
    // g_MouseSensitivity = (index + 1) * 3.0f (setter 0x004cefe0, const 3.0 at
    // 0x005d8cc0, max index 0x14 at PauseMenu__Init 0x004ce27d), so the
    // reachable values are 3, 6, ... 63 and 1.5 is below the FLOOR. The image
    // default, before the slider is ever touched, is the static initialiser at
    // VA 0x006254f4 = float32 7.0 - itself not reachable from the slider.
    //
    // 7.0 x 13/3000 = 91/3000. Aiming was 4.67x too slow at equal hand motion.
    //
    // The slider now exists (RetailOptionsMenu, Controller Options row 0) and
    // this IS (index + 1) * 3 * 13/3000 when it is moved. 91/3000 remains the
    // untouched default, because the default is the image's own static
    // initialiser at VA 0x006254f4 and nothing in this change is allowed to move
    // it: see SetMouseSensitivity.
    private const int PointerOffsetScale = 1_000;
    private const int PointerOffsetRetentionNumerator = 10;
    private const int PointerOffsetRetentionDenominator = 17;
    private const int DefaultPointerAxisNumerator = 91;
    private const int PointerAxisDenominator = 3_000;

    /// <summary>The 13/3000 in <c>CController::DoMappings</c>, as an exact ratio.</summary>
    private const int PointerAxisPerSensitivityNumerator = 13;
    private const int MaximumPointerOffsetMilliPixels = 1_000_000;

    private readonly Simulation _simulation;
    private readonly List<Level100MissionEvent> _undeliveredLevel100MissionEvents = [];
    private readonly List<AquilaFlightEvent> _undeliveredAquilaFlightEvents = [];
    private readonly List<Level100DestructionEvent>
        _undeliveredLevel100DestructionEvents = [];
    private readonly List<Level100WeaponFireEvent>
        _undeliveredLevel100WeaponFireEvents = [];
    private InteractiveInput _input;
    private bool _toggleLevelWasHeld;
    private bool _resetLevelWasHeld;
    private bool _toggleEdgePending;
    private bool _resetEdgePending;
    private bool _firePulsePending;
    private bool _skipPanningEdgePending;
    private sbyte _movementPulseX;
    private sbyte _movementPulseZ;
    private sbyte _lookPulseX;
    private sbyte _lookPulseY;
    private int _pointerOffsetXMilliPixels;
    private int _pointerOffsetYMilliPixels;
    private int _pointerAxisNumerator = DefaultPointerAxisNumerator;
    private InteractivePauseReason _pauseReasons;
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
        _undeliveredAquilaFlightEvents.AddRange(
            CurrentSnapshot.AquilaFlightEventLog);
        _undeliveredLevel100DestructionEvents.AddRange(
            CurrentSnapshot.Level100DestructionEvents);
        _undeliveredLevel100WeaponFireEvents.AddRange(
            CurrentSnapshot.Level100WeaponFireEvents);
    }

    public WorldSnapshot PreviousSnapshot { get; private set; }

    public WorldSnapshot CurrentSnapshot { get; private set; }

    public long InterpolationPhase => _interpolationPhase;

    public InteractivePauseReason PauseReasons => _pauseReasons;

    public bool IsPaused => _pauseReasons != InteractivePauseReason.None;

    public bool IsAuthenticMenuPaused =>
        (_pauseReasons & InteractivePauseReason.AuthenticMenu) != 0;

    public bool InputSuspendedUntilReleased => _inputSuspendedUntilReleased;

    public bool HasHeldOrPendingInput =>
        _input != InteractiveInput.Idle ||
        _toggleLevelWasHeld ||
        _resetLevelWasHeld ||
        _toggleEdgePending ||
        _resetEdgePending ||
        _firePulsePending ||
        _skipPanningEdgePending ||
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

        if (IsPaused)
        {
            return;
        }

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
        if (IsPaused || _inputSuspendedUntilReleased)
        {
            return;
        }

        _toggleEdgePending = true;
    }

    public void QueueReset()
    {
        if (IsPaused || _inputSuspendedUntilReleased)
        {
            return;
        }

        _resetEdgePending = true;
    }

    /// <summary>
    /// One <c>BUTTON_SKIP_PANNING</c> (<c>0x3a</c>) edge.
    /// </summary>
    /// <remarks>
    /// Every shipped row for this action is KEY_ONCE (push type 8), so it is
    /// an edge and never a held level. Core ignores it outside the opening
    /// pan, exactly as <c>references/Onslaught/Player.cpp:311</c> requires, so
    /// a client may bind it to a key that means something else during play.
    /// </remarks>
    public void QueueSkipPanning()
    {
        if (IsPaused || _inputSuspendedUntilReleased)
        {
            return;
        }

        _skipPanningEdgePending = true;
    }

    public void QueueFirePulse()
    {
        if (IsPaused || _inputSuspendedUntilReleased)
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

        if (IsPaused || _inputSuspendedUntilReleased)
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

        if (IsPaused || _inputSuspendedUntilReleased)
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

        if (IsPaused || _inputSuspendedUntilReleased)
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

    public void SetAuthenticMenuPaused(bool paused)
    {
        SetPauseReason(InteractivePauseReason.AuthenticMenu, paused);
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
        _skipPanningEdgePending = false;
        _movementPulseX = 0;
        _movementPulseZ = 0;
        _lookPulseX = 0;
        _lookPulseY = 0;
        _pointerOffsetXMilliPixels = 0;
        _pointerOffsetYMilliPixels = 0;
    }

    private void SetPauseReason(InteractivePauseReason reason, bool paused)
    {
        InteractivePauseReason updated = paused
            ? _pauseReasons | reason
            : _pauseReasons & ~reason;
        if (updated == _pauseReasons)
        {
            return;
        }

        _pauseReasons = updated;
        SuspendInputUntilReleased();
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

        if (IsPaused)
        {
            return new FrameAdvanceResult(
                0,
                false,
                _interpolationPhase,
                PhaseUnitsPerStep,
                PreviousSnapshot,
                CurrentSnapshot,
                Array.Empty<Level100MissionEvent>(),
                Array.Empty<AquilaFlightEvent>(),
                Array.Empty<Level100DestructionEvent>(),
                Array.Empty<Level100WeaponFireEvent>());
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
        var aquilaFlightEvents = new List<AquilaFlightEvent>();
        aquilaFlightEvents.AddRange(_undeliveredAquilaFlightEvents);
        var level100DestructionEvents = new List<Level100DestructionEvent>();
        level100DestructionEvents.AddRange(
            _undeliveredLevel100DestructionEvents);
        var level100WeaponFireEvents = new List<Level100WeaponFireEvent>();
        level100WeaponFireEvents.AddRange(
            _undeliveredLevel100WeaponFireEvents);
        while (_interpolationPhase >= PhaseUnitsPerStep)
        {
            bool firstStep = stepsAdvanced == 0;
            bool firePulse = firstStep && _firePulsePending;
            sbyte moveX = _input.MoveX;
            sbyte moveZ = _input.MoveZ;
            sbyte lookX = _input.LookX;
            sbyte lookY = _input.LookY;
            // RETAIL'S ORDER, AND IT IS NOT THE ONE THIS USED TO HAVE.
            // CController::DoMappings (0x0042DB40) READS the cursor offset and
            // only raises the recentre flag (DAT_0066E94D = 1) on its way out;
            // Input__UpdateCursorCenterWithWindowScale (0x0042DA00) does the
            // easing afterwards. Easing BEFORE the read - which is what this
            // did until 2026-07-30 - takes 29.8 % off a fresh motion before the
            // simulation ever sees it, and that is what made a half-pixel floor
            // look necessary. Quantise, read, then ease.
            int cursorX = WholePixelsOf(_pointerOffsetXMilliPixels);
            int cursorY = WholePixelsOf(_pointerOffsetYMilliPixels);
            short pointerLookX = ToPointerAxisPermille(cursorX);
            short pointerLookY = ToPointerAxisPermille(cursorY);
            _pointerOffsetXMilliPixels = RecenterPointerOffset(cursorX) +
                (_pointerOffsetXMilliPixels - cursorX);
            _pointerOffsetYMilliPixels = RecenterPointerOffset(cursorY) +
                (_pointerOffsetYMilliPixels - cursorY);
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
            if (_input.LandingJetsHeld)
            {
                actions |= SimActions.LandingJets;
            }
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

                if (_skipPanningEdgePending)
                {
                    actions |= SimActions.SkipPanning;
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
                _skipPanningEdgePending = false;
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
            // Held digital look is level-sampled. Pointer motion enters as the
            // whole-pixel analogue axis retail reads out of the cursor, and
            // recenters across steps.
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
            aquilaFlightEvents.AddRange(CurrentSnapshot.AquilaFlightEventLog);
            level100DestructionEvents.AddRange(
                CurrentSnapshot.Level100DestructionEvents);
            level100WeaponFireEvents.AddRange(
                CurrentSnapshot.Level100WeaponFireEvents);
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
            Array.AsReadOnly(level100MissionEvents.ToArray()),
            Array.AsReadOnly(aquilaFlightEvents.ToArray()),
            Array.AsReadOnly(level100DestructionEvents.ToArray()),
            Array.AsReadOnly(level100WeaponFireEvents.ToArray()));
        _undeliveredLevel100MissionEvents.Clear();
        _undeliveredAquilaFlightEvents.Clear();
        _undeliveredLevel100DestructionEvents.Clear();
        _undeliveredLevel100WeaponFireEvents.Clear();
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

    /// <summary>
    /// The whole-pixel CURSOR inside the accumulated offset - the only part of
    /// it retail's look axis is read from. This is what replaced the half-pixel
    /// dead zone.
    ///
    /// <para><b>Retail has no look dead zone.</b> The shipped mouse case in
    /// <c>CController::DoMappings</c> (0x0042DB40) is, in full:
    /// <c>v = g_MouseSensitivity * (cursor - windowCentre) * 0.004333333</c>,
    /// then <c>if (v &lt; -1) v = -1; else if (v &gt; 1) v = 1;</c>, then a SIGN
    /// GATE - <c>ANALOGUE_PLUS</c> zeroes <c>v &lt; 0</c> and
    /// <c>ANALOGUE_MINUS</c> zeroes <c>v &gt; 0</c>. The three constants are
    /// read from the pristine specimen
    /// (<c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, sha256
    /// <c>74154bfa…</c>): VA 0x005D8BE0 = -1.0, VA 0x005D8568 = +1.0, and the
    /// gate's threshold VA 0x005D856C = <b>0.0</b>. There is no other
    /// comparison on that path.</para>
    ///
    /// <para>The GPL drop's <c>ANALOGUE_X_DEAD</c>/<c>ANALOGUE_Y_DEAD</c> of
    /// 0.36 (<c>Controller.h:11-12</c>, applied at
    /// <c>Controller.cpp:227-233</c>) is a JOYSTICK rule - it guards
    /// <c>GetJoyAnalogue*</c>, and its own comment says "the Xbox controllers
    /// appear to need really huge dead zones". It is not in the shipped PC
    /// image at all: the float32 0.36 (<c>EC 51 B8 3E</c>) occurs <b>zero</b>
    /// times in that 2,506,752-byte specimen.</para>
    ///
    /// <para>So retail's floor is not a threshold, it is a QUANTUM. The
    /// displacement comes from the cached cursor position
    /// <c>DAT_0089BDA8</c>/<c>DAT_0089BDA4</c>, which are <b>ints</b> fed from
    /// <c>WM_MOUSEMOVE</c>'s <c>LOWORD/HIWORD(lParam)</c>
    /// (<c>ltshell.cpp:1058-1067</c>). One pixel is the smallest displacement
    /// the released build can see.</para>
    ///
    /// <para>This client takes Godot's fractional <c>ScreenRelative</c> as
    /// milli-pixels, so the fraction has to live somewhere. It stays in the
    /// accumulator and is carried, never read: that is where retail keeps it
    /// too, in the OS - Windows accumulates mouse counts and moves the cursor
    /// by whole pixels, so a slow drag still eventually turns the walker. What
    /// must NOT happen is the fraction reaching the axis, which is what made
    /// this client able to aim finer than the released build.</para>
    /// </summary>
    private static int WholePixelsOf(int value) =>
        value / PointerOffsetScale * PointerOffsetScale;

    /// <summary>
    /// Retail's recentring ease, from
    /// <c>Input__UpdateCursorCenterWithWindowScale</c> (0x0042DA00), on the
    /// whole-pixel cursor <see cref="WholePixelsOf"/> returns.
    ///
    /// <para>Retail eases the cached cursor toward the window centre by
    /// VA 0x005D97C4 = 0.5882353186607361 = <b>10/17</b> per 20 Hz update, and
    /// Core now runs at that rate, so the shipped ratio is used verbatim; it
    /// read 702049/1000000, i.e. <c>0.5882353^(20/30)</c>, at 30 Hz. The
    /// ease is integer, so it stalls - and 0x0042DA00 carries its own anti-stall
    /// for exactly that: <c>if ((centre != cursor) &amp;&amp; (step == 0))
    /// step = ±1</c>, forcing one whole pixel toward the centre whenever the
    /// eased step rounds to nothing.</para>
    ///
    /// <para><b>That rule is the proof the state is integer.</b> A float offset
    /// never needs it. Without it a one-pixel offset rounds back to itself
    /// (round(1 × 10/17) = 1) and the axis never returns to rest; with it,
    /// one pixel decays to zero on the next update, which is what the old
    /// half-pixel floor was standing in for.</para>
    /// </summary>
    private static int RecenterPointerOffset(int wholePixelValue)
    {
        int pixels = wholePixelValue / PointerOffsetScale;
        if (pixels == 0)
        {
            return 0;
        }

        long scaled = (long)pixels * PointerOffsetRetentionNumerator;
        int eased = (int)(scaled >= 0
            ? (scaled + (PointerOffsetRetentionDenominator / 2)) /
                PointerOffsetRetentionDenominator
            : (scaled - (PointerOffsetRetentionDenominator / 2)) /
                PointerOffsetRetentionDenominator);
        if (eased == pixels)
        {
            eased = pixels - Math.Sign(pixels);
        }

        return eased * PointerOffsetScale;
    }

    /// <summary>
    /// The mouse-sensitivity slider's only consumer.
    ///
    /// Retail's reachable values are <c>(index + 1) * 3</c> for index 0..20, so
    /// the range floors at 3.0 and the axis scale is
    /// <c>sensitivity * 13/3000</c>. Passing the image default 7.0 reproduces
    /// 91/3000 exactly, which is what keeps this from silently changing the
    /// untouched default.
    /// </summary>
    public void SetMouseSensitivity(float sensitivity)
    {
        if (!float.IsFinite(sensitivity) || sensitivity <= 0f)
        {
            throw new ArgumentOutOfRangeException(nameof(sensitivity));
        }

        _pointerAxisNumerator = (int)Math.Round(
            sensitivity * PointerAxisPerSensitivityNumerator,
            MidpointRounding.AwayFromZero);
    }

    private short ToPointerAxisPermille(int offsetMilliPixels)
    {
        long scaled = (long)offsetMilliPixels * _pointerAxisNumerator;
        long rounded = scaled >= 0
            ? (scaled + (PointerAxisDenominator / 2)) / PointerAxisDenominator
            : (scaled - (PointerAxisDenominator / 2)) / PointerAxisDenominator;
        return (short)Math.Clamp(rounded, -1_000, 1_000);
    }
}
