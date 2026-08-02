using System;
using System.Collections.Generic;
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
    ///
    /// Since the progressive-disclosure pass these strings come in two kinds, and the page puts
    /// them in two different places. A headline is one plain sentence that stays on screen; a note
    /// is the fine print behind a panel labelled "How we know". Nothing moved out of the app in
    /// that pass and nothing was softened - splitting a constant in two is allowed, dropping half
    /// of it is not, and the honesty suite fails on either half going missing.
    /// </summary>
    internal static class LiveTrainerPageText
    {
        public const string SectionTitle = "Live trainer";

        /// <summary>
        /// The same label the rest of the Cheats page puts on a collapsed evidence disclosure. It
        /// is an alias rather than a second constant so the two cannot drift apart.
        /// </summary>
        public const string EvidenceDisclosureLabel = CheatsPageText.EvidenceDisclosureLabel;

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
        /// The standing caveat, in one sentence, and the only part of it that stays on screen with
        /// nothing to open. The rest of the caveat is <see cref="EvidenceNote"/>. Splitting it is
        /// the whole point: a player should meet this sentence without reading a paragraph, and the
        /// paragraph must still be one click away.
        /// </summary>
        public const string EvidenceHeadline =
            "These three have been read out of a running mission, and changing life worked.";

        /// <summary>
        /// The rest of the standing caveat: where the positions came from, and what it looks like
        /// when they are wrong. It sits behind the disclosure, never instead of
        /// <see cref="EvidenceHeadline"/>.
        /// </summary>
        public const string EvidenceNote =
            "Their positions came out of the game's own damage routine, which loads all three together "
            + "and treats life as a decimal number. On 1 August 2026 that was checked against a real "
            + "mission: life read 20, energy and shields both read 8, setting life to 100 took, and the "
            + "health ring on the HUD filled to match. If the numbers below ever look like nonsense, "
            + "they are - and the controls that change them stay switched off.";

        public const string LifeEvidenceNote =
            "Life sits where the game's damage routine reads it, and where the health readout on the HUD "
            + "gets its number. Read from a running mission, and changed there: 20 became 100 and the HUD "
            + "ring filled.";

        public const string EnergyEvidenceNote =
            "Energy sits next to life in the same routine, and read 8 in a running mission. Of the three "
            + "it has the thinnest paper trail behind it - one of the notes was superseded once - so it "
            + "is the one to watch if a value ever looks wrong.";

        /// <summary>
        /// Not provenance: this changes what a player should do with the controls, so it stays on
        /// screen while <see cref="ShieldsEvidenceNote"/> moves behind the disclosure. Telling
        /// somebody a switch is futile without telling them the fix is a shrug, and a shrug they
        /// have to open a panel to find is worse.
        /// </summary>
        public const string ShieldsHoldWarning =
            "In walker mode the game copies energy over the top of shields on every update, so holding "
            + "shields on its own will not stick - hold energy as well. In jet mode it sets shields to "
            + "zero every update.";

        public const string ShieldsEvidenceNote =
            "Shields sit next to energy in the same routine. In a running mission they read 8 - exactly "
            + "what energy read at the same moment, which is the copying described above happening in "
            + "front of us.";

        public const string StateEvidenceNote =
            "2 is walker, 1 is changing to jet, 3 is jet - watched in a running game, and seen again on "
            + "foot in the tutorial, where it read 2. An old note in the project claims the opposite "
            + "mapping; the game disagrees with the note. It is shown and never changed - knowing what a "
            + "number means is not knowing what happens if you force it.";

        /// <summary>
        /// What Hold is, and the part that decides whether somebody trusts it in a fight.
        ///
        /// It is a re-heal, not a freeze. The loop writes at 10 Hz against a simulation that
        /// updates at 20, so damage still lands and is undone a fraction of a second later - and a
        /// single hit big enough to kill outright arrives between two writes and is not undone at
        /// all. Leaving that unsaid would let a player believe a switch labelled Hold makes them
        /// safe, which is exactly the class of claim the rest of this page refuses to make. The
        /// page already makes the same call for shields, in a slot that does not collapse.
        /// </summary>
        public const string HoldExplanation =
            "The game rewrites these ten to twenty times a second, so setting a value once barely lasts "
            + "a blink. Hold writes it back about ten times a second instead. It stops on its own when "
            + "the mission ends, when the game closes, and when you leave this page. It tops the value "
            + "back up rather than freezing it, so you still take damage between writes, and one hit "
            + "big enough to kill you outright will still kill you.";

        // ------------------------------------------------------------------ hotkeys

        public const string HotkeysHeadline =
            "Keys you can press while the game has focus.";

        /// <summary>
        /// What claiming a key actually costs, said plainly.
        ///
        /// This is not provenance and does not go behind the disclosure. A combination registered
        /// with Windows is taken from the whole machine: while the trainer is watching, those four
        /// presses reach nothing else. A player is entitled to know that before it happens, and to
        /// know that it ends when they stop watching.
        /// </summary>
        public const string HotkeysNote =
            "While the app is watching a running copy, these four combinations belong to it and "
            + "will not reach anything else on your PC. They are given back the moment you stop "
            + "watching, leave this page, or close the app. Nothing is typed or clicked for you - "
            + "the app only asks Windows to send these presses here instead of elsewhere.";

        public const string HotkeysUnavailable =
            "Hotkeys are not available right now, so use the switches above.";

        /// <summary>
        /// The keys, in one line each. Built from the same table the listener registers, so the
        /// page cannot advertise a combination the app does not actually claim.
        /// </summary>
        public static string DescribeHotkeys()
        {
            var lines = new System.Text.StringBuilder();
            foreach (TrainerHotkey binding in TrainerHotkeys.Bindings)
            {
                if (lines.Length > 0)
                    lines.Append(Environment.NewLine);

                lines.Append(binding.Display).Append("   -   ").Append(binding.Description);
            }

            return lines.ToString();
        }

        /// <summary>
        /// Whether the keys are live, and which are not. A combination another program already
        /// owns is not this app's failure, but silence about it would be: the player is in a
        /// fight, pressing a key, believing something happened.
        /// </summary>
        public static string DescribeHotkeyState(IReadOnlyList<string>? unavailable)
        {
            if (unavailable is null || unavailable.Count == 0)
                return "The keys below are live.";

            if (unavailable.Count == TrainerHotkeys.Bindings.Count)
            {
                return "None of these keys could be claimed - something else on this PC already "
                    + "has them. Use the switches above.";
            }

            return $"Live, except {string.Join(", ", unavailable)} - something else on this PC "
                + "already has those. The switches above still work.";
        }

        // ------------------------------------------------------------------ god mode

        /// <summary>
        /// The headline for the field that decides whether damage sticks. It is deliberately not
        /// called god mode here: the app has a god mode that works, on this same page, and it is a
        /// different thing.
        /// </summary>
        public const string VulnerableHeadline =
            "Damage switch: found in the game's code, not yet tested here.";

        public const string VulnerableNote =
            "The game keeps one number that decides whether a hit counts. It was found on 1 August "
            + "2026 by reading the game's own damage routine, where setting it to zero makes the "
            + "routine put your life, shields and energy back exactly as they were a moment "
            + "earlier - which is why it stops new damage but never repairs a hull you have "
            + "already lost. It is shown here and not changed, because nothing has written to it "
            + "in a running game yet. The three numbers above only got their controls after "
            + "somebody watched a value change on the HUD, and this has not had that.";

        /// <summary>
        /// The thing to do instead, and it is not a consolation prize - it is the better route.
        /// The save-name God mode was confirmed in a real mission on 2026-03-29 and is already on
        /// this page; the trainer section simply never mentioned it.
        /// </summary>
        public const string VulnerableUseTheCheatInstead =
            "There is a working god mode on this page already: tick God mode above and write the "
            + "save. The game turns it on itself when your save name contains the word, and it was "
            + "checked in a real mission - damage stopped counting, and the pause menu showed "
            + "God ON.";

        /// <summary>How the field reads, without interpreting a number that makes no sense.</summary>
        public static string DescribeVulnerable(LivePlayerVitals? vitals)
        {
            if (vitals?.Vulnerable is null)
                return "-";

            bool? invulnerable = vitals.IsInvulnerable;
            if (invulnerable is null)
            {
                return $"{vitals.Vulnerable.AsInt32} - not a 0 or a 1, so this is not the switch "
                    + $"(bytes {vitals.Vulnerable.RawHex})";
            }

            return invulnerable.Value
                ? $"0 - damage would not stick (bytes {vitals.Vulnerable.RawHex})"
                : $"1 - damage counts (bytes {vitals.Vulnerable.RawHex})";
        }

        public const string NothingOfferedHeadline =
            "Ammunition and game speed are not offered.";

        public const string NothingOfferedNote =
            "There is no address for either in anything this project has measured, so a control for "
            + "them would be a switch wired to nothing.";

        /// <summary>
        /// What to do when there is nothing to watch. One sentence, and it names the button rather
        /// than describing the state the player can already see.
        /// </summary>
        public const string NothingRunningNote =
            "Launch a copy from Windowed & Mods, start a mission, then press Watch the running copy.";

        /// <summary>Where the app is in the attach cycle, in one line.</summary>
        public static string BuildAttachSummary(bool attached, string? copyName, string? message)
        {
            if (!attached)
            {
                return string.IsNullOrWhiteSpace(message) ? NothingRunningNote : message;
            }

            return string.IsNullOrWhiteSpace(copyName)
                ? "Watching the copy this app launched."
                : $"Watching \"{copyName}\".";
        }

        /// <summary>
        /// The live line under the values: what the last read actually found. Empty before the
        /// first read, because the line above it already says what to do next and a second line
        /// saying "nothing yet" only describes what the player can see.
        /// </summary>
        public static string BuildReadingSummary(LiveTrainerReadResult? reading)
        {
            if (reading is null)
                return string.Empty;

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
