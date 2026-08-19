using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// A gameplay resolution for an app-owned safe copy, expressed as the
    /// <c>-res W H</c> launch arguments the copied game accepts.
    ///
    /// Why more than one is offerable at all: the shipped 28-region widescreen
    /// correction does not hard-code 16:9. Its own catalog purpose is to
    /// "accept non-4:3 modes, derive the runtime aspect ratio, and correct
    /// gameplay viewport and field-of-view terms", and the region analysis shows
    /// the aspect being computed from the live screen width
    /// (<c>FILD [EBP+0x32E5C]</c> -> <c>FST [0x9D4FF0]</c>,
    /// reverse-engineering/binary-analysis/widescreen-patch-analysis.md).
    /// 1600x900 is the resolution that was played and measured, not a limit the
    /// patch imposes.
    ///
    /// That distinction is the whole contract here: <see cref="IsMeasured"/> is
    /// true for exactly one preset, and callers are expected to say so rather
    /// than present every option as equally proven.
    /// </summary>
    public sealed record DisplayResolutionPreset(int Width, int Height, bool IsMeasured)
    {
        /// <summary>Widths and heights the copied game's launch validator accepts.</summary>
        public const int MinimumWidth = 640;

        public const int MinimumHeight = 480;
        public const int MaximumExtent = 16384;

        public const string ResolutionFormatHelp =
            "Give a resolution as WIDTHxHEIGHT, for example 1920x1080.";

        public const string ResolutionNotASize =
            "That is not a resolution. Use WIDTHxHEIGHT, for example 1920x1080.";

        public static string ResolutionOutOfRange =>
            $"That copy accepts widths from {MinimumWidth} to {MaximumExtent} and heights from {MinimumHeight} to {MaximumExtent}.";

        /// <summary>The resolution a safe copy uses unless the player chooses another.</summary>
        public static DisplayResolutionPreset Measured { get; } = new(1600, 900, IsMeasured: true);

        /// <summary>
        /// Offered choices, measured one first. These are common 16:9 desktop
        /// sizes; a caller may also build one from the player's own screen.
        /// </summary>
        public static IReadOnlyList<DisplayResolutionPreset> Offered { get; } = new[]
        {
            Measured,
            new DisplayResolutionPreset(1280, 720, IsMeasured: false),
            new DisplayResolutionPreset(1920, 1080, IsMeasured: false),
            new DisplayResolutionPreset(2560, 1440, IsMeasured: false),
            new DisplayResolutionPreset(3840, 2160, IsMeasured: false),
        };

        /// <summary>"1920x1080" - also the form the CLI accepts.</summary>
        public string Label => $"{Width}x{Height}";

        /// <summary>
        /// A sentence a player can act on. The measured preset says it was
        /// played; everything else says plainly that it was not, because the
        /// correction being resolution-independent is a reading of the code,
        /// not something anyone has sat down and watched.
        /// </summary>
        public string Describe() => IsMeasured
            ? $"{Label} - the size this was played and measured at."
            : $"{Label} - the widescreen correction works this out from your screen size, but nobody has played at this size yet.";

        public IReadOnlyList<string> ToLaunchArguments() => new[]
        {
            "-res",
            Width.ToString(CultureInfo.InvariantCulture),
            Height.ToString(CultureInfo.InvariantCulture),
        };

        public static bool IsSupported(int width, int height) =>
            width >= MinimumWidth && width <= MaximumExtent &&
            height >= MinimumHeight && height <= MaximumExtent;

        /// <summary>
        /// Reads "1920x1080" (or "1920X1080", or with spaces). Returns false
        /// rather than throwing, so a caller can report a usable message.
        /// </summary>
        public static bool TryParse(string? value, out DisplayResolutionPreset preset, out string? problem)
        {
            preset = Measured;
            problem = null;

            if (string.IsNullOrWhiteSpace(value))
            {
                problem = ResolutionFormatHelp;
                return false;
            }

            string[] parts = value.Trim().Split('x', 'X');
            if (parts.Length != 2 ||
                !int.TryParse(parts[0].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int width) ||
                !int.TryParse(parts[1].Trim(), NumberStyles.Integer, CultureInfo.InvariantCulture, out int height))
            {
                problem = ResolutionNotASize;
                return false;
            }

            if (!IsSupported(width, height))
            {
                problem = ResolutionOutOfRange;
                return false;
            }

            preset = FromSize(width, height);
            return true;
        }

        /// <summary>
        /// Builds a preset for any supported size, marking it measured only if
        /// it is exactly the size that was played.
        /// </summary>
        public static DisplayResolutionPreset FromSize(int width, int height) =>
            width == Measured.Width && height == Measured.Height
                ? Measured
                : new DisplayResolutionPreset(width, height, IsMeasured: false);

        /// <summary>
        /// Replaces any <c>-res W H</c> already present in a launch argument
        /// list, leaving every other argument untouched and in order. The
        /// compatibility profile always contributes the measured size, so
        /// choosing another resolution is a substitution rather than an append -
        /// two -res triples would leave the copied game reading whichever the
        /// parser happened to reach last.
        /// </summary>
        public IReadOnlyList<string> ApplyTo(IReadOnlyList<string> launchArguments)
        {
            ArgumentNullException.ThrowIfNull(launchArguments);

            List<string> result = new(launchArguments.Count + 3);
            bool substituted = false;

            for (int index = 0; index < launchArguments.Count; index++)
            {
                string token = launchArguments[index];
                if (!string.Equals(token, "-res", StringComparison.OrdinalIgnoreCase))
                {
                    result.Add(token);
                    continue;
                }

                // Drop the existing triple, however many operands survive.
                int skip = Math.Min(2, launchArguments.Count - index - 1);
                index += skip;

                if (!substituted)
                {
                    result.AddRange(ToLaunchArguments());
                    substituted = true;
                }
            }

            if (!substituted)
            {
                result.AddRange(ToLaunchArguments());
            }

            return result;
        }
    }
}
