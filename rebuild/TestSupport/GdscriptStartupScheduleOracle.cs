// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.TestSupport;

/// <summary>
/// Differential fixtures from the retained C# startup owner. The shipped clip
/// records are the fixtures in RetailStartupSequenceTests, RetailAttractLoopTests
/// and RetailLevel100CutsceneTests; no private media is read or serialized.
/// </summary>
public static class GdscriptStartupScheduleOracle
{
    public static object Create()
    {
        var logo = new RetailStartupClip(229, 25, 1, 480, 300);
        var montage = new RetailStartupClip(2054, 25, 1, 480, 300);
        var intro = new RetailStartupClip(3095, 25, 1, 480, 300);
        var fractional = new RetailStartupClip(1001, 30000, 1001, 480, 300);
        var wrappedProduct = new RetailStartupClip(1_000_000_000, 7, 5, 480, 300);
        var emptyLogo = logo with { FrameCount = 0 };
        var negativeMontage = montage with { FrameCount = -1 };
        var full = new Dictionary<RetailStartupCue, RetailStartupClip>
        {
            [RetailStartupCue.LostToysLogo] = logo,
            [RetailStartupCue.OpeningMontage] = montage,
            [RetailStartupCue.Level100IntroCutscene] = intro,
        };
        var emptyRecords = new Dictionary<RetailStartupCue, RetailStartupClip>
        {
            [RetailStartupCue.LostToysLogo] = emptyLogo,
            [RetailStartupCue.OpeningMontage] = negativeMontage,
        };
        var schedules = new List<object>();

        void AddSchedule(string name, string mode,
            IReadOnlyDictionary<RetailStartupCue, RetailStartupClip> clips,
            bool splash = false, RetailStartupCue cue = RetailStartupCue.Level100IntroCutscene,
            bool fixedTicks = false)
        {
            RetailStartupSchedule schedule = mode switch
            {
                "cold" => new RetailStartupSchedule(clips, splash),
                "single" => RetailStartupSchedule.ForSingleClip(cue, clips),
                "attract" => RetailStartupSchedule.ForAttractRestart(clips),
                _ => throw new InvalidOperationException(mode),
            };
            var times = new List<double>
            {
                double.NegativeInfinity, -1d, -double.Epsilon, -0d, 0d, double.Epsilon,
                0.039d, 0.04d, 1d, 9d, 9.5d, 88d, 92d, 200d,
                double.PositiveInfinity, double.NaN,
            };
            void Boundary(double value)
            {
                if (double.IsFinite(value)) times.Add(Math.BitDecrement(value));
                times.Add(value);
                if (double.IsFinite(value)) times.Add(Math.BitIncrement(value));
            }
            Boundary(1d / 25d);
            Boundary(schedule.TotalSeconds);
            Boundary(logo.DurationSeconds);
            double splashStart = logo.DurationSeconds +
                RetailStartupSchedule.InterClipBlackSeconds + montage.DurationSeconds;
            Boundary(splashStart);
            Boundary(splashStart + RetailStartupSchedule.SplashFadeInSeconds);
            times.Add(splashStart + 0.75d);
            times.Add(splashStart + 4d);
            foreach (RetailStartupClip clip in clips.Values)
            {
                Boundary(clip.DurationSeconds);
                Boundary(1d / clip.FramesPerSecond);
            }
            if (fixedTicks)
            {
                // Reuse the existing 6,000 injected 60 Hz samples, now also
                // compare each output word to the independent GDScript owner.
                for (int tick = 0; tick < 6_000; tick++) times.Add(tick / 60d);
            }
            schedules.Add(new
            {
                name, mode, cue = (int)cue, splash_present = splash,
                clips = clips.Select(pair => Clip(pair.Key, pair.Value)).ToArray(),
                total_seconds = DoubleWord(schedule.TotalSeconds),
                missing_cues = schedule.MissingCues.Select(value => (int)value).ToArray(),
                is_empty = schedule.IsEmpty,
                samples = times.Select(elapsed => new
                {
                    elapsed = DoubleWord(elapsed), frame = Frame(schedule.Sample(elapsed)),
                }).ToArray(),
            });
        }

        AddSchedule("cold_full", "cold", full, splash: true, fixedTicks: true);
        AddSchedule("cold_no_splash", "cold", full);
        AddSchedule("cold_logo_only", "cold", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.LostToysLogo] = logo });
        AddSchedule("cold_montage_only", "cold", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.OpeningMontage] = montage });
        AddSchedule("cold_splash_only", "cold", new Dictionary<RetailStartupCue, RetailStartupClip>(), splash: true);
        AddSchedule("cold_none", "cold", new Dictionary<RetailStartupCue, RetailStartupClip>());
        AddSchedule("cold_cutscene_ignored", "cold", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.Level100IntroCutscene] = intro });
        AddSchedule("cold_empty_records", "cold", emptyRecords);
        AddSchedule("cold_empty_logo", "cold", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.LostToysLogo] = emptyLogo, [RetailStartupCue.OpeningMontage] = montage }, splash: true);
        AddSchedule("attract_full", "attract", full);
        AddSchedule("attract_logo_only", "attract", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.LostToysLogo] = logo });
        AddSchedule("attract_none", "attract", new Dictionary<RetailStartupCue, RetailStartupClip>());
        AddSchedule("attract_empty_records", "attract", emptyRecords);
        AddSchedule("single_intro", "single", full);
        AddSchedule("single_missing", "single", new Dictionary<RetailStartupCue, RetailStartupClip>());
        AddSchedule("single_unknown_present", "single", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [(RetailStartupCue)99] = logo }, cue: (RetailStartupCue)99);
        AddSchedule("single_unknown_missing", "single", full, cue: (RetailStartupCue)(-17));
        AddSchedule("single_fractional_rate", "single", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.Level100IntroCutscene] = fractional });
        AddSchedule("single_wrapped_duration_product", "single", new Dictionary<RetailStartupCue, RetailStartupClip>
            { [RetailStartupCue.Level100IntroCutscene] = wrappedProduct });

        // The schedule itself does not validate rates or geometry; the media
        // index owns that admission. Keep these existing double edge behaviors.
        (string Name, RetailStartupClip Clip)[] unusualClips =
        [
            ("zero_numerator", logo with { FramesPerSecondNumerator = 0 }),
            ("zero_denominator", logo with { FramesPerSecondDenominator = 0 }),
            ("both_rate_fields_zero", logo with { FramesPerSecondNumerator = 0, FramesPerSecondDenominator = 0 }),
            ("negative_numerator", logo with { FramesPerSecondNumerator = -25 }),
            ("negative_denominator", logo with { FramesPerSecondDenominator = -1 }),
            ("negative_zero_duration", logo with { FramesPerSecondNumerator = -25, FramesPerSecondDenominator = 0 }),
            ("maximum_frame_count", logo with { FrameCount = int.MaxValue, FramesPerSecondNumerator = 1 }),
            ("negative_wrapped_duration", logo with { FrameCount = int.MaxValue, FramesPerSecondDenominator = 2 }),
            ("ignored_geometry", logo with { Width = int.MinValue, Height = 0 }),
        ];
        foreach ((string name, RetailStartupClip clip) in unusualClips)
            AddSchedule("single_" + name, "single", new Dictionary<RetailStartupCue, RetailStartupClip>
                { [RetailStartupCue.Level100IntroCutscene] = clip });

        var arguments = new List<object>();
        void ArgumentCase(string name, IReadOnlyList<string>? values)
        {
            try
            {
                arguments.Add(new { name, arguments = values,
                    ok = true, value = RetailStartupSchedule.IsSuppressedByArguments(values!), error_type = "" });
            }
            catch (Exception error) when (error is ArgumentNullException or NullReferenceException)
            {
                arguments.Add(new { name, arguments = values, ok = false, value = false,
                    error_type = error.GetType().Name });
            }
        }
        ArgumentCase("empty", []);
        ArgumentCase("intro_only", ["--intro"]);
        foreach (string flag in new[] { "--skipfmv", "--smoke", "--capture-dir=x", "--capture-plan=x",
            "--capture-size=640x480", "--capture-offsets-ms=0,40", "--capture-dir=", "--capture-plan=" })
        {
            ArgumentCase(flag, [flag]);
            ArgumentCase("intro_before:" + flag, ["--intro", flag]);
            ArgumentCase("intro_after:" + flag, [flag, "--intro"]);
        }
        ArgumentCase("case_and_prefix_do_not_match", ["--INTRO", "--Skipfmv", "-skipfmv",
            "--capture-dir", "--capture-plan", "--capture-sizes=x", " --smoke", "x--capture-dir=x", ""]);
        ArgumentCase("duplicates", ["--skipfmv", "--skipfmv", "--intro", "--intro"]);
        ArgumentCase("null_list", null);
        ArgumentCase("null_element", [null!]);
        ArgumentCase("null_after_intro", ["--intro", null!]);

        var constructionErrors = new List<object>();
        foreach (string mode in new[] { "cold", "single", "attract" })
        {
            try
            {
                _ = mode switch
                {
                    "cold" => new RetailStartupSchedule(null!, false),
                    "single" => RetailStartupSchedule.ForSingleClip(RetailStartupCue.LostToysLogo, null!),
                    _ => RetailStartupSchedule.ForAttractRestart(null!),
                };
                throw new InvalidOperationException("Null clips unexpectedly admitted.");
            }
            catch (ArgumentNullException error)
            {
                constructionErrors.Add(new { mode, error_type = error.GetType().Name });
            }
        }

        return new
        {
            schedules, arguments, construction_errors = constructionErrors,
            clip_timings = new[] { logo, montage, intro, fractional, wrappedProduct, emptyLogo, negativeMontage }
                .Concat(unusualClips.Select(value => value.Clip)).Select(clip => new
                {
                    clip = Clip(RetailStartupCue.LostToysLogo, clip),
                    frames_per_second = DoubleWord(clip.FramesPerSecond), duration_seconds = DoubleWord(clip.DurationSeconds),
                }).ToArray(),
            constants = new
            {
                inter_clip_black_seconds = DoubleWord(RetailStartupSchedule.InterClipBlackSeconds),
                splash_fade_in_seconds = DoubleWord(RetailStartupSchedule.SplashFadeInSeconds),
                splash_hold_seconds = DoubleWord(RetailStartupSchedule.SplashHoldSeconds),
                cue_ids = Enum.GetValues<RetailStartupCue>().Select(value => (int)value).ToArray(),
                frame_kind_ids = Enum.GetValues<RetailStartupFrameKind>().Select(value => (int)value).ToArray(),
            },
        };
    }

    private static object Clip(RetailStartupCue cue, RetailStartupClip clip) => new
    {
        cue = (int)cue, frame_count = clip.FrameCount,
        fps_numerator = clip.FramesPerSecondNumerator, fps_denominator = clip.FramesPerSecondDenominator,
        width = clip.Width, height = clip.Height,
    };

    private static object Frame(RetailStartupFrame frame) => new
    {
        kind = (int)frame.Kind, cue = frame.Cue is RetailStartupCue cue ? (int?)cue : null,
        frame_index = frame.FrameIndex, alpha = SingleWord(frame.Alpha), beat_seconds = DoubleWord(frame.BeatSeconds),
    };

    // Every finite word and signed infinity is compared bit-for-bit. C# does
    // not specify a NaN payload/sign for these presentation calculations.
    private static string DoubleWord(double value) => double.IsNaN(value)
        ? "nan" : Convert.ToHexString(BitConverter.GetBytes(value)).ToLowerInvariant();

    private static string SingleWord(float value) => float.IsNaN(value)
        ? "nan" : Convert.ToHexString(BitConverter.GetBytes(value)).ToLowerInvariant();
}
