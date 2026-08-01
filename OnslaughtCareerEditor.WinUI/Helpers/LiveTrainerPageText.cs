using System;
using System.Globalization;
using System.IO;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences the Cheats page shows about the live trainer.
    ///
    /// They live here rather than in the page so they can be tested, and they need testing more
    /// than the rest of the page does. Everything else on Cheats is a file copy whose effects the
    /// game itself provides; this section reaches into a running process using three field
    /// positions that nobody has ever read out of a running game. The honesty of these strings is
    /// the only thing standing between "here are your vitals" and a claim the evidence does not
    /// support, so the wording is pinned by
    /// <c>OnslaughtCareerEditor.UiTests.LiveTrainerPageHonestyTests</c>.
    ///
    /// Nothing here may say verified, confirmed, proven, or guaranteed about the vitals.
    /// </summary>
    internal static class LiveTrainerPageText
    {
        public const string SectionTitle = "Live trainer";

        public const string Introduction =
            "This is the only part of the app that reaches into a running game. It watches a copy this "
            + "app started, shows you the numbers it finds, and only then offers to change them.";

        public const string SafeCopyOnlyNote =
            "It attaches to a copy you launched from Windowed & Mods, in this app, and to nothing else. "
            + "Your installed game is never opened.";

        public const string MissionRunningNote =
            "It needs a mission actually running. At the title screen and in the menus there is nothing "
            + "to read, and the app will say so rather than showing you zeroes.";

        /// <summary>
        /// The standing caveat. This is the sentence the whole feature rests on, so it is written
        /// plainly and it is not softened anywhere else on the page.
        /// </summary>
        public const string EvidenceNote =
            "Nobody has read these three numbers out of a running game yet. Their positions come from "
            + "the game's own damage code lining up with the developers' source, which is good evidence "
            + "about where they should be and no evidence at all about what you will see. If the numbers "
            + "below look like nonsense, they are - and the controls that change them stay switched off.";

        public const string LifeEvidenceNote =
            "Life sits where the game's damage routine reads it, and where the health readout on the HUD "
            + "gets its number. Read from a running game: never.";

        public const string EnergyEvidenceNote =
            "Energy sits next to life in the same routine. It is the least corroborated of the three, and "
            + "one of the notes behind it has already been superseded once. Read from a running game: never.";

        public const string ShieldsEvidenceNote =
            "Shields sit next to energy in the same routine. In walker mode the game copies energy over "
            + "the top of shields on every update, so holding shields on its own will not stick - hold "
            + "energy as well. In jet mode it sets shields to zero every update. Read from a running "
            + "game: never.";

        public const string StateEvidenceNote =
            "This one has been watched in a running game: 2 is walker, 1 is changing to jet, 3 is jet. "
            + "It is shown and never changed - knowing what a number means is not knowing what happens "
            + "if you force it.";

        public const string HoldExplanation =
            "The game rewrites these ten to twenty times a second, so setting a value once barely lasts "
            + "a blink. Hold writes it back about ten times a second instead. It stops on its own when "
            + "the mission ends, when the game closes, and when you leave this page.";

        public const string NothingOfferedNote =
            "Ammunition and game speed are not offered. There is no address for either in anything this "
            + "project has measured, so a control for them would be a switch wired to nothing.";

        /// <summary>Where the app is in the attach cycle, in one line.</summary>
        public static string BuildAttachSummary(bool attached, string? copyName, string? message)
        {
            if (!attached)
            {
                return string.IsNullOrWhiteSpace(message)
                    ? "Not watching anything. Launch a copy from Windowed & Mods, then press Watch."
                    : message;
            }

            return string.IsNullOrWhiteSpace(copyName)
                ? "Watching the copy this app launched."
                : $"Watching \"{copyName}\".";
        }

        /// <summary>The live line under the values: what the last read actually found.</summary>
        public static string BuildReadingSummary(LiveTrainerReadResult? reading)
        {
            if (reading is null)
                return "Nothing read yet.";

            return reading.Status switch
            {
                LiveTrainerReadStatus.Read when reading.WritingCanBeOffered =>
                    "Reading a running mission. The numbers below are what is in the game right now.",
                LiveTrainerReadStatus.Read =>
                    "Reading a running mission, but the numbers do not look like vitals - so nothing here "
                        + "will be changed. This is what a wrong field position looks like.",
                _ => reading.Message,
            };
        }

        /// <summary>
        /// One vital, shown as a decimal first and as the exact bytes second. The raw value is not
        /// decoration: it is how a player can tell a real reading from a bit pattern the app has
        /// misread as a number.
        /// </summary>
        public static string FormatVital(LiveTrainerFieldReading? field)
        {
            if (field is null)
                return "-";

            string number = field.LooksLikeAVital
                ? field.AsSingle.ToString("0.###", CultureInfo.InvariantCulture)
                : "not a number";

            return $"{number}   (bytes {field.RawHex})";
        }

        /// <summary>The state field, named when the number is one of the three that were watched.</summary>
        public static string FormatState(LivePlayerVitals? vitals)
        {
            if (vitals is null)
                return "-";

            string? name = vitals.StateName;
            string raw = vitals.State.AsInt32.ToString(CultureInfo.InvariantCulture);
            return name is null
                ? $"{raw}   (no meaning recorded for this one)"
                : $"{name}   ({raw})";
        }

        /// <summary>
        /// Why the set and hold controls are switched off, or null when they are allowed. Nothing
        /// on the page may enable a write while this returns a reason.
        /// </summary>
        public static string? DescribeWhyWritingIsBlocked(bool attached, LiveTrainerReadResult? reading)
        {
            if (!attached)
                return "Watch a running copy first.";

            if (reading is null)
                return "Nothing has been read yet.";

            if (!reading.HasVitals)
                return reading.Message;

            if (!reading.WritingCanBeOffered)
                return "The numbers read back do not look like vitals, so nothing here will be changed.";

            return null;
        }

        /// <summary>A safe copy's folder name, which is what a player recognises it by.</summary>
        public static string DescribeCopyName(GameProfileManagedProcess? process)
        {
            if (process is null || string.IsNullOrWhiteSpace(process.WorkingDirectory))
                return string.Empty;

            return Path.GetFileName(Path.TrimEndingDirectorySeparator(process.WorkingDirectory));
        }
    }
}
