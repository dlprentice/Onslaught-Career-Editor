// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// The media beats retail plays before the interactive frontend appears, named
/// SEMANTICALLY rather than by file path.
///
/// The names are the released sequencer's own: the intro block at
/// <c>0x004efce3</c>-<c>0x004efee9</c> in pristine <c>BEA.exe</c>
/// (sha256 <c>74154bfa…</c>, image base <c>0x400000</c>) loads
/// <c>"splash.tga"</c> and then plays <c>"ltlogo"</c> and <c>"openingfmv"</c>
/// through the format string <c>"data\video\%s.vid"</c>.
/// </summary>
public enum RetailStartupCue
{
    /// <summary><c>data/video/LTLogo.vid</c> — the Lost Toys bear logo.</summary>
    LostToysLogo,

    /// <summary><c>data/video/OpeningFMV.vid</c> — the title card and gameplay montage.</summary>
    OpeningMontage,

    /// <summary><c>data/textures/splash.tga</c> — the static Lost Toys / Atari card.</summary>
    Splash,
}

/// <summary>What the startup sequence is drawing at a sampled instant.</summary>
public enum RetailStartupFrameKind
{
    /// <summary>Nothing is drawn. The client is black.</summary>
    Black,

    /// <summary>A decoded video frame is drawn, letterboxed.</summary>
    Video,

    /// <summary>The static splash card is drawn full-frame at <see cref="RetailStartupFrame.Alpha"/>.</summary>
    Splash,

    /// <summary>The sequence is over; the interactive frontend owns the screen.</summary>
    Finished,
}

/// <summary>
/// Timing and geometry of one decoded clip. Populated from the media index the
/// materialize step writes, never guessed: a clip that has not been decoded is
/// ABSENT rather than assumed, so a missing decode can never silently
/// contribute a duration to the schedule.
/// </summary>
public readonly record struct RetailStartupClip(
    int FrameCount,
    int FramesPerSecondNumerator,
    int FramesPerSecondDenominator,
    int Width,
    int Height)
{
    public double FramesPerSecond =>
        FramesPerSecondNumerator / (double)FramesPerSecondDenominator;

    /// <summary>
    /// Duration in seconds, taken from the clip's own frame count and rate.
    /// For <c>LTLogo.vid</c> this is 229 / 25 = 9.16 s and for
    /// <c>OpeningFMV.vid</c> 2054 / 25 = 82.16 s, which is exactly what
    /// <c>ffprobe</c> reports for the shipped Bink files.
    /// </summary>
    public double DurationSeconds =>
        FrameCount * FramesPerSecondDenominator / (double)FramesPerSecondNumerator;
}

/// <summary>A sample of the startup sequence at one instant.</summary>
public readonly record struct RetailStartupFrame(
    RetailStartupFrameKind Kind,
    RetailStartupCue? Cue,
    int FrameIndex,
    float Alpha);

/// <summary>
/// The released cold-start media sequence, as a pure deterministic function of
/// elapsed seconds. No Godot types, no filesystem, no clock — it is handed the
/// elapsed time by whichever clock the host injected, so the same schedule
/// serves a fixed capture tick and a wall clock without a second code path.
///
/// <para><b>Order, and where each beat comes from.</b></para>
/// The order is the disassembled sequencer's, not a guess. On the branch the PC
/// build takes (<c>[0x662f28] != 0</c>) it is
/// <c>Play("ltlogo")</c> → <c>Play("openingfmv")</c>, with the splash texture
/// loaded before the chain and released after it.
///
/// <para><b>The nVidia screen, and a claim that had to be withdrawn.</b></para>
/// The gated <c>Play("TWIMTBP_GefFX_640x480_Audio")</c> between them is not
/// reproduced. The first reason offered for that was WRONG, and is recorded
/// here so it is not re-derived: an exact scan of <c>.text</c> for the
/// little-endian dword <c>0x0083d404</c> finds three hits, all reads, which was
/// read as "no writer exists, therefore the screen is dead code". It is not a
/// plain BSS dword. <c>0x004efae0</c> runs
/// <c>push 0; push 0x632b28 ("TWIMTBP"); mov ecx,0x83d3f8; call 0x528aa0</c>,
/// constructing a console variable named <c>TWIMTBP</c> at <c>0x83d3f8</c>, and
/// <c>CVar::Init</c> stores its value with <c>mov [eax+0xc], ecx</c> —
/// and <c>0x83d3f8 + 0xc</c> IS <c>0x83d404</c>. The store is object-relative,
/// so an absolute-address scan cannot see it. The shipped <c>cardid.txt</c>
/// then carries <c>Tweak:TWIMTBP 1</c> under exactly one device:
/// <c>Vendor:10DE nVidia / Device:0330 NVIDIA GeForce FX 5900 Ultra</c>.
///
/// So the screen is reachable BY DESIGN, on one 2003 adapter. It is omitted
/// because no modern adapter matches that tweak entry and it demonstrably did
/// not play on the measured hardware — not because it is unreachable. See
/// <c>local-lab/SPLASH-AND-INTRO-FMV-2026-07-26.md</c>.
///
/// <para><b>The two constants that are NOT derived from a shipped byte.</b></para>
/// <see cref="InterClipBlackSeconds"/> and the splash fade/hold are measured
/// from captures of the released build and are labelled as such at each field.
/// They are observations of what a player sees, not recovered constants, and
/// they are the only numbers here that a better measurement should overwrite.
/// </summary>
public sealed class RetailStartupSchedule
{
    /// <summary>
    /// The black interval between LTLogo ending and OpeningFMV appearing.
    ///
    /// ZERO, AND THAT IS A CORRECTION. Two capture runs on 2026-07-26 showed
    /// last LTLogo content at t=9.2 s and first OpeningFMV content at t=11.4 s
    /// with pure black between, which read as a ~1.9 s authored gap. It is not
    /// one.
    ///
    /// Matching each of the eight 2026-07-25 intro reference frames against the
    /// decoded clips locates the exact source frame for every one of them
    /// (whole-frame mean |delta| 1.22-3.02). The implied clip start times are
    /// LTLogo at t=0.987 s (sd 0.023 over 3 frames) and OpeningFMV at
    /// t=10.200 s (sd 0.089 over 5 frames), while LTLogo's own 9.16 s duration
    /// puts its end at 10.147 s. The gap in THAT run was therefore
    /// <b>+0.053 s</b> — the two clips are contiguous.
    ///
    /// So the black is Bink close/open latency on a cold file cache, not a
    /// beat: it is present in one run and absent in another of the same build.
    /// Reproducing 1.9 s of it would have been fabricating an authored pause
    /// out of one machine's disk behaviour.
    /// </summary>
    public const double InterClipBlackSeconds = 0.00;

    /// <summary>
    /// The splash card's ramp from black to full.
    ///
    /// MEASURED, NOT RECOVERED. Least-squares alpha of the captured frame
    /// against the settled splash frame, over the 72,005 pixels brighter than
    /// 32: 0.165 at t=88.0 s, 0.521 at 88.5, 0.852 at 89.0, 1.000 at 89.5 —
    /// a straight ramp of about 0.67 per second, i.e. ~1.5 s end to end.
    /// </summary>
    public const double SplashFadeInSeconds = 1.50;

    /// <summary>
    /// How long the splash card holds at full before the client goes black.
    ///
    /// MEASURED, NOT RECOVERED. Alpha is exactly 1.000 at t=89.5, 90.0, 90.5,
    /// 91.0, 91.5 and 92.0 s and exactly 0 at 92.5 s, and the 89.6-92.1 s
    /// frames are byte-identical to a frame captured at t=90 s in a SEPARATE
    /// run. There is no fade out; the cut to black is abrupt.
    /// </summary>
    public const double SplashHoldSeconds = 3.00;

    private readonly List<Beat> _beats = [];
    private readonly List<RetailStartupCue> _missing = [];

    private readonly record struct Beat(
        RetailStartupFrameKind Kind,
        RetailStartupCue? Cue,
        double StartSeconds,
        double DurationSeconds,
        bool FadeIn,
        double FramesPerSecond,
        int FrameCount);

    /// <summary>
    /// Builds the schedule from whatever media is actually present.
    /// </summary>
    /// <param name="clips">Decoded video clips, keyed by cue. A cue absent from
    /// this map contributes NO time and is reported in <see cref="MissingCues"/>.</param>
    /// <param name="splashPresent">Whether the splash still was materialized.</param>
    public RetailStartupSchedule(
        IReadOnlyDictionary<RetailStartupCue, RetailStartupClip> clips,
        bool splashPresent)
    {
        ArgumentNullException.ThrowIfNull(clips);

        double cursor = 0d;

        cursor = AppendVideo(RetailStartupCue.LostToysLogo, clips, cursor);

        // The gap only exists BETWEEN two clips. If either side is absent there
        // is nothing to sit between, and holding black anyway would invent a
        // beat retail never shows on that path.
        if (clips.ContainsKey(RetailStartupCue.LostToysLogo) &&
            clips.ContainsKey(RetailStartupCue.OpeningMontage))
        {
            _beats.Add(new Beat(
                RetailStartupFrameKind.Black, null, cursor, InterClipBlackSeconds,
                false, 0d, 0));
            cursor += InterClipBlackSeconds;
        }

        cursor = AppendVideo(RetailStartupCue.OpeningMontage, clips, cursor);

        if (splashPresent)
        {
            _beats.Add(new Beat(
                RetailStartupFrameKind.Splash, RetailStartupCue.Splash, cursor,
                SplashFadeInSeconds, true, 0d, 0));
            cursor += SplashFadeInSeconds;
            _beats.Add(new Beat(
                RetailStartupFrameKind.Splash, RetailStartupCue.Splash, cursor,
                SplashHoldSeconds, false, 0d, 0));
            cursor += SplashHoldSeconds;
        }
        else
        {
            _missing.Add(RetailStartupCue.Splash);
        }

        TotalSeconds = cursor;
    }

    /// <summary>Total length of the sequence, in seconds of injected time.</summary>
    public double TotalSeconds { get; }

    /// <summary>
    /// Cues the media index did not supply. The sequence still runs; the beat is
    /// simply absent. Nothing is drawn in its place and nothing is imitated.
    /// </summary>
    public IReadOnlyList<RetailStartupCue> MissingCues => _missing;

    /// <summary>
    /// True when no beat has any content at all, i.e. the whole sequence would
    /// be a no-op. The host uses this to hand straight over to the frontend
    /// rather than holding a black screen for nothing.
    /// </summary>
    public bool IsEmpty => _beats.Count == 0;

    /// <summary>
    /// What to draw at <paramref name="elapsedSeconds"/>. A negative time is
    /// treated as zero; past the end the result is
    /// <see cref="RetailStartupFrameKind.Finished"/>.
    /// </summary>
    public RetailStartupFrame Sample(double elapsedSeconds)
    {
        double time = Math.Max(0d, elapsedSeconds);
        if (time >= TotalSeconds)
        {
            return new RetailStartupFrame(RetailStartupFrameKind.Finished, null, 0, 0f);
        }

        foreach (Beat beat in _beats)
        {
            if (time >= beat.StartSeconds + beat.DurationSeconds)
            {
                continue;
            }

            double local = time - beat.StartSeconds;
            switch (beat.Kind)
            {
                case RetailStartupFrameKind.Video:
                    // floor(local * fps): frame n covers [n/fps, (n+1)/fps).
                    // At 25 fps under a 60 Hz fixed tick this repeats each video
                    // frame for two or three engine frames in a fixed pattern,
                    // which is deterministic because `local` is.
                    int index = (int)Math.Floor(local * beat.FramesPerSecond);
                    index = Math.Clamp(index, 0, beat.FrameCount - 1);
                    return new RetailStartupFrame(
                        RetailStartupFrameKind.Video, beat.Cue, index, 1f);

                case RetailStartupFrameKind.Splash:
                    float alpha = beat.FadeIn
                        ? (float)Math.Clamp(local / beat.DurationSeconds, 0d, 1d)
                        : 1f;
                    return new RetailStartupFrame(
                        RetailStartupFrameKind.Splash, beat.Cue, 0, alpha);

                default:
                    return new RetailStartupFrame(
                        RetailStartupFrameKind.Black, null, 0, 0f);
            }
        }

        return new RetailStartupFrame(RetailStartupFrameKind.Finished, null, 0, 0f);
    }

    private double AppendVideo(
        RetailStartupCue cue,
        IReadOnlyDictionary<RetailStartupCue, RetailStartupClip> clips,
        double cursor)
    {
        if (!clips.TryGetValue(cue, out RetailStartupClip clip) || clip.FrameCount <= 0)
        {
            _missing.Add(cue);
            return cursor;
        }

        _beats.Add(new Beat(
            RetailStartupFrameKind.Video,
            cue,
            cursor,
            clip.DurationSeconds,
            false,
            clip.FramesPerSecond,
            clip.FrameCount));
        return cursor + clip.DurationSeconds;
    }
}
