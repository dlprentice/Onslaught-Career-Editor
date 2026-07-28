// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// What <see cref="Level100ChainAutopilot"/> drives.
///
/// <para>The autopilot decides in <see cref="SimInput"/> and reads
/// <see cref="WorldSnapshot"/>; it has no opinion about who owns the
/// simulation. This seam exists so the same decisions can be delivered either
/// straight into <see cref="Simulation"/> - which is what every measurement
/// before 2026-07-27 did - or through
/// <see cref="OnslaughtRebuild.Client.InteractiveSession"/>, which is the
/// surface the shipping client actually gives a player.</para>
///
/// <para><b>It is not an abstraction over the simulation.</b> There is exactly
/// one <see cref="Simulation"/> underneath either implementation. What differs
/// is the route the input takes to reach it.</para>
/// </summary>
internal interface ILevel100ChainHost
{
    WorldSnapshot Snapshot { get; }

    WorldSnapshot Step(SimInput input);
}

/// <summary>The pre-existing route: straight into Core.</summary>
internal sealed class Level100DirectChainHost : ILevel100ChainHost
{
    private readonly Simulation _simulation;
    private readonly bool _quantizeLookToClientPointerPath;
    private readonly bool _quantizeLookToIntegerMousePixels;

    /// <param name="quantizeLookToClientPointerPath">
    /// Apply only the analogue-look quantisation the client's pointer path
    /// imposes, and change nothing else.
    ///
    /// <para>This is an INSTRUMENT CHECK, not a mode. If a run with this set
    /// produces the same pose trace as the same run through
    /// <see cref="Level100InteractiveChainHost"/>, then that host's inverse of
    /// the pointer laws is exact and the dead zone is the ONLY thing the client
    /// costs. Without it, "the client is lossy" and "this driver mistranslates"
    /// are the same observation.</para>
    /// </param>
    /// <param name="quantizeLookToIntegerMousePixels">
    /// Restrict the analogue look axis to the positions a hand on a mouse can
    /// actually reach. See
    /// <see cref="Level100InteractiveChainHost.PlayerPlausiblePermille"/>.
    ///
    /// <para>This constrains the driver's OUTPUT channel, and only that. With
    /// it set the driver is no longer allowed sub-pixel aim: every stick
    /// position it asks for snaps to one a whole retail mouse pixel can
    /// produce, so a beat it then fails is a beat a player would also have to
    /// fight for <em>with the same hand</em>.</para>
    ///
    /// <para><b>It does not make the run player-plausible.</b> The PERCEPTION
    /// channel is still omniscient: this driver reads exact
    /// <c>Health</c>, full three-dimensional actor poses, and sampled
    /// line-of-sight ray tests against terrain. A player has a compass, a
    /// scanner and a windscreen. <c>GOAL.md</c> demotes the driven <c>Won</c>
    /// run to an acceptance test precisely because "an autopilot that reaches
    /// <c>Won</c> by means no player could reproduce has proved nothing";
    /// integer mouse pixels close one half of that gap and the wording here
    /// used to claim the whole of it.</para>
    /// </param>
    internal Level100DirectChainHost(
        Simulation simulation,
        bool quantizeLookToClientPointerPath = false,
        bool quantizeLookToIntegerMousePixels = false)
    {
        _simulation = simulation;
        _quantizeLookToClientPointerPath = quantizeLookToClientPointerPath;
        _quantizeLookToIntegerMousePixels = quantizeLookToIntegerMousePixels;
    }

    public WorldSnapshot Snapshot => _simulation.Snapshot;

    public WorldSnapshot Step(SimInput input)
    {
        if (_quantizeLookToIntegerMousePixels)
        {
            input = input with
            {
                LookXAnalogPermille =
                    Level100InteractiveChainHost.PlayerPlausiblePermille(
                        input.LookXAnalogPermille),
                LookYAnalogPermille =
                    Level100InteractiveChainHost.PlayerPlausiblePermille(
                        input.LookYAnalogPermille),
            };
        }

        if (_quantizeLookToClientPointerPath)
        {
            input = input with
            {
                LookXAnalogPermille =
                    Level100InteractiveChainHost.DeliverablePermille(
                        input.LookXAnalogPermille),
                LookYAnalogPermille =
                    Level100InteractiveChainHost.DeliverablePermille(
                        input.LookYAnalogPermille),
            };
        }

        return _simulation.Step(input);
    }
}

/// <summary>
/// The client's route: every decision is delivered through the same
/// <see cref="InteractiveSession"/> methods the Godot client calls from
/// <c>_Process</c> and <c>_Input</c>, and the simulation is advanced by handing
/// the session a frame time rather than by calling <c>Step</c>.
///
/// <para><b>Three of the autopilot's channels do not survive the trip
/// unchanged, and that is the point of running it.</b></para>
///
/// <list type="number">
///   <item><description><b>Held state</b> - <c>MoveX</c>, <c>MoveZ</c>,
///   <c>Fire</c>, <c>LandingJets</c>, digital <c>LookX/LookY</c> - goes through
///   <see cref="InteractiveSession.ObserveInput"/> exactly as
///   <c>FirstFlightGame.SampleInput</c> polls it. Lossless.</description></item>
///   <item><description><b>Discrete edges</b> - <c>ToggleMode</c>,
///   <c>Reset</c> - go through <see cref="InteractiveSession.QueueToggleMode"/>
///   and <see cref="InteractiveSession.QueueReset"/>, which is the key-press
///   path <c>FirstFlightGame._Input</c> uses. Lossless, and deliberately not
///   the <c>ToggleModeHeld</c> level, because a held key produces one edge
///   where the autopilot may want one per tick.</description></item>
///   <item><description><b>The analogue look axis is LOSSY, and the loss is
///   measured rather than assumed.</b> The autopilot commands a stick position
///   in permille. The client has no route for that: <c>SampleInput</c> leaves
///   the look actions unbound on purpose
///   (<c>FirstFlightGame.ConfigureInputMap</c>), so the only way to move the
///   analogue axis is mouse motion through
///   <see cref="InteractiveSession.QueuePointerMotionMilliPixels"/>. That path
///   carries a released recentring retention and a half-pixel dead zone, and
///   the two together mean <b>no stick position between 1 and 14 permille is
///   reachable at all</b>. See <see cref="UnreachableLookCommands"/>.
///   </description></item>
/// </list>
/// </summary>
internal sealed class Level100InteractiveChainHost : ILevel100ChainHost
{
    /// <summary>
    /// Frame time the client pins itself to when it is being driven
    /// deterministically (<c>FirstFlightGame.SmokeFrameElapsedTicks</c>).
    ///
    /// <para>30 Hz does not divide <see cref="TimeSpan.TicksPerSecond"/>, so
    /// this is the client's own rounded-up value, not a new one. It advances
    /// exactly one simulation step per frame and leaves 20 phase units of
    /// residue; <see cref="InteractiveSession.PhaseUnitsPerStep"/> is 10,000,000,
    /// so the first double-step would arrive at frame 500,000. This run is four
    /// orders of magnitude short of that, and <see cref="Step"/> asserts the
    /// one-step property on every frame rather than trusting the arithmetic.
    /// </para>
    /// </summary>
    internal const long FrameElapsedTicks = 333_334;

    // The inverse of InteractiveSession's two published pointer laws. Both
    // constants are transcribed from OnslaughtRebuild.Client/InteractiveSession.cs
    // (PointerAxisNumerator/Denominator and PointerOffsetRetention*), which
    // carries their retail provenance: 91/3000 is the shipped 13/3000 scalar at
    // pristine VA 0x005d97c8 times the image's untouched 7.0 sensitivity, and
    // 702049/1000000 is the 30 Hz time-equivalent of retail's 10/17 recentring.
    private const int PointerAxisNumerator = 91;
    private const int PointerAxisDenominator = 3_000;
    private const int PointerRetentionNumerator = 702_049;
    private const int PointerRetentionDenominator = 1_000_000;
    private const int PointerDeadZoneMilliPixels = 500;

    private readonly InteractiveSession _session;
    private readonly bool _quantizeLookToIntegerMousePixels;

    /// <summary>
    /// What the session's stored pointer offset is after the last step.
    ///
    /// <para>It is not read back from the session, because the session does not
    /// expose it. It is known by construction: the step applies the retention
    /// in place, so whatever this host aimed the retention at is exactly what
    /// the session now holds. If that were wrong the run would diverge
    /// immediately and visibly, which is why no product accessor was added to
    /// make it observable.</para>
    /// </summary>
    private int _storedOffsetX;
    private int _storedOffsetY;

    private int _unreachableLookCommands;
    private int _lookCommands;
    private int _subRetailPixelLookCommands;

    /// <param name="quantizeLookToIntegerMousePixels">
    /// Restrict the driver to stick positions a hand on a mouse can reach
    /// (<see cref="PlayerPlausiblePermille"/>) BEFORE the pointer path is asked
    /// for them.
    ///
    /// <para><b>With it set, this host is lossless.</b> The dead zone measured
    /// by <see cref="UnreachableLookCommands"/> only ever eats magnitudes below
    /// 15 permille, and the smallest position an integer pixel can produce is
    /// 30. So the loss this class exists to expose is a loss of commands
    /// <i>no player could issue in the first place</i>, and a driver that does
    /// not issue them travels through <c>InteractiveSession</c> unchanged.
    /// </para>
    /// </param>
    internal Level100InteractiveChainHost(
        InteractiveSession session,
        bool quantizeLookToIntegerMousePixels = false)
    {
        _session = session;
        _quantizeLookToIntegerMousePixels = quantizeLookToIntegerMousePixels;
    }

    public WorldSnapshot Snapshot => _session.CurrentSnapshot;

    /// <summary>
    /// How many analogue look commands this run asked for and could not get,
    /// because the requested stick position falls inside the client's pointer
    /// dead zone. Each one is delivered as zero.
    /// </summary>
    internal int UnreachableLookCommands => _unreachableLookCommands;

    /// <summary>How many nonzero analogue look commands were issued at all.</summary>
    internal int LookCommands => _lookCommands;

    /// <summary>
    /// How many analogue look commands are finer than <b>one mouse pixel</b>.
    ///
    /// <para>Retail's <c>CController::DoMappings</c> (0x0042DB40) maps an
    /// INTEGER pixel displacement by <c>sensitivity * 13/3000</c>, and the
    /// image's untouched sensitivity is 7.0, so the smallest look input a hand
    /// on a mouse can produce is <c>91/3000</c> of full deflection - about
    /// <b>30 permille</b>. This client is finer than retail there, because it
    /// takes Godot's fractional <c>ScreenRelative</c> as milli-pixels; the count
    /// is kept anyway, because a command below this threshold is one no player
    /// could issue on the released build either.</para>
    /// </summary>
    internal int SubRetailPixelLookCommands => _subRetailPixelLookCommands;

    /// <summary>The permille a one-pixel mouse move produces at the image's
    /// untouched sensitivity.</summary>
    internal const int RetailSinglePixelPermille = 30;

    /// <summary>
    /// The nearest stick position to <paramref name="requested"/> that a hand
    /// on a mouse can actually produce on the released build.
    ///
    /// <para>Retail's <c>CController::DoMappings</c> (0x0042DB40) maps an
    /// INTEGER pixel displacement by <c>sensitivity * 13/3000</c>. At the
    /// image's untouched sensitivity of 7.0 one pixel is <c>91/3000</c> of full
    /// deflection, so the reachable axis is the lattice
    /// <c>{0, ±30, ±61, ±91, ±121, …}</c> permille and NOTHING lies between
    /// zero and thirty. This snaps a requested position to the nearest whole
    /// number of pixels and returns what that many pixels deliver.</para>
    ///
    /// <para><b>Why it exists.</b> Measured over the joined cold-start run,
    /// 2,904 of this driver's 4,937 analogue look commands (58.8 %) are finer
    /// than one mouse pixel and 2,184 (44.2 %) fall inside the client's own
    /// pointer dead zone and arrive as zero. A run that needs those commands is
    /// evidence about the MECHANISM of the level, not about whether a person
    /// can play it. Driving through this function is the honest playability
    /// question.</para>
    /// </summary>
    internal static short PlayerPlausiblePermille(short requested)
    {
        int pixels = (int)Math.Round(
            requested * (double)PointerAxisDenominator /
                (PointerAxisNumerator * 1_000.0),
            MidpointRounding.AwayFromZero);
        long scaled = (long)pixels * PointerAxisNumerator * 1_000;
        long permille = scaled >= 0
            ? (scaled + (PointerAxisDenominator / 2)) / PointerAxisDenominator
            : (scaled - (PointerAxisDenominator / 2)) / PointerAxisDenominator;
        return (short)Math.Clamp(permille, -1_000, 1_000);
    }

    /// <summary>
    /// What the client's pointer path actually delivers when a driver asks for
    /// <paramref name="requested"/> permille of stick. Exposed so the loss can
    /// be stated as a property of the surface rather than inferred from one
    /// run's counters.
    /// </summary>
    internal static short DeliverablePermille(short requested)
    {
        int ignored = 0;
        int offset = PointerOffsetFor(requested, ref ignored, ref ignored);
        return (short)ToPermille(Retain(offset));
    }

    public WorldSnapshot Step(SimInput input)
    {
        _session.ObserveInput(new InteractiveInput(
            input.MoveX,
            input.MoveZ,
            input.HasAction(SimActions.Fire),
            ToggleModeHeld: false,
            ResetHeld: false,
            input.LookX,
            input.LookY,
            input.HasAction(SimActions.LandingJets)));

        if (input.HasAction(SimActions.ToggleMode))
        {
            _session.QueueToggleMode();
        }

        if (input.HasAction(SimActions.Reset))
        {
            _session.QueueReset();
        }

        // The counters read what the DRIVER ASKED FOR, always, so the
        // sub-pixel census below is a statement about the driver rather than
        // about this host's configuration.
        CountLookCommand(input.LookXAnalogPermille);
        CountLookCommand(input.LookYAnalogPermille);
        short requestedX = _quantizeLookToIntegerMousePixels
            ? PlayerPlausiblePermille(input.LookXAnalogPermille)
            : input.LookXAnalogPermille;
        short requestedY = _quantizeLookToIntegerMousePixels
            ? PlayerPlausiblePermille(input.LookYAnalogPermille)
            : input.LookYAnalogPermille;
        int targetX = PointerOffsetFor(requestedX, ref _lookCommands, ref _unreachableLookCommands);
        int targetY = PointerOffsetFor(requestedY, ref _lookCommands, ref _unreachableLookCommands);
        int deltaX = targetX - _storedOffsetX;
        int deltaY = targetY - _storedOffsetY;
        if (deltaX != 0 || deltaY != 0)
        {
            _session.QueuePointerMotionMilliPixels(deltaX, deltaY);
        }

        FrameAdvanceResult result = _session.AdvanceFrameTicks(FrameElapsedTicks);
        if (result.StepsAdvanced != 1)
        {
            throw new InvalidOperationException(
                $"The client advanced {result.StepsAdvanced} simulation steps on one frame; " +
                "this driver is one frame per tick and every measurement here assumes it.");
        }

        _storedOffsetX = Retain(targetX);
        _storedOffsetY = Retain(targetY);
        return result.CurrentSnapshot;
    }

    private void CountLookCommand(short permille)
    {
        if (permille != 0 && Math.Abs((int)permille) < RetailSinglePixelPermille)
        {
            _subRetailPixelLookCommands++;
        }
    }

    /// <summary>
    /// The pointer offset that has to be standing before the step so that the
    /// step's retention leaves an offset the client converts to
    /// <paramref name="permille"/>.
    ///
    /// <para>Returns 0 and counts an unreachable command when no such offset
    /// exists. That happens for every requested magnitude from 1 to 14: the
    /// retention zeroes anything below half a pixel, and half a pixel is
    /// already 15 permille.</para>
    /// </summary>
    private static int PointerOffsetFor(
        short permille,
        ref int commands,
        ref int unreachable)
    {
        if (permille == 0)
        {
            return 0;
        }

        commands++;
        int magnitude = Math.Abs((int)permille);
        int retained = (int)Math.Round(
            magnitude * (double)PointerAxisDenominator / PointerAxisNumerator,
            MidpointRounding.AwayFromZero);
        retained = Math.Max(retained, PointerDeadZoneMilliPixels);
        if (ToPermille(retained) != magnitude)
        {
            unreachable++;
            return 0;
        }

        // The smallest pre-retention offset the retention maps onto `retained`.
        int offset = (int)Math.Round(
            retained * (double)PointerRetentionDenominator / PointerRetentionNumerator,
            MidpointRounding.AwayFromZero);
        while (Retain(offset) > retained)
        {
            offset--;
        }

        while (Retain(offset) < retained)
        {
            offset++;
        }

        return permille < 0 ? -offset : offset;
    }

    private static int Retain(int value)
    {
        long scaled = (long)value * PointerRetentionNumerator;
        int retained = (int)(scaled >= 0
            ? (scaled + (PointerRetentionDenominator / 2)) / PointerRetentionDenominator
            : (scaled - (PointerRetentionDenominator / 2)) / PointerRetentionDenominator);
        return Math.Abs(retained) < PointerDeadZoneMilliPixels ? 0 : retained;
    }

    private static int ToPermille(int offsetMilliPixels)
    {
        long scaled = (long)offsetMilliPixels * PointerAxisNumerator;
        long rounded = scaled >= 0
            ? (scaled + (PointerAxisDenominator / 2)) / PointerAxisDenominator
            : (scaled - (PointerAxisDenominator / 2)) / PointerAxisDenominator;
        return (int)Math.Clamp(rounded, -1_000, 1_000);
    }
}
