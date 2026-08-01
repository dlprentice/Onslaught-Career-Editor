using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentences the Cheats page shows about the name it is about to write and where it is
    /// about to write it.
    ///
    /// This is separate from the page so the wording can be tested. The page's whole promise is
    /// that you can see the exact file name before anything is written, and that the app does not
    /// claim an effect it has not seen; both of those are properties of these strings, and a
    /// property nobody tests is a property that drifts.
    /// </summary>
    internal static class CheatsPageText
    {
        /// <summary>
        /// The one label every collapsed evidence disclosure on this page carries, trainer section
        /// included. It is a constant because "pick one label and use it everywhere" is only worth
        /// anything if a second label cannot quietly appear next to it.
        /// </summary>
        public const string EvidenceDisclosureLabel = "How we know";

        /// <summary>
        /// What to do when no safe copy has been found. It is the same sentence whether the list
        /// came back empty on load or after the player pressed the refresh button.
        /// </summary>
        public const string NoSafeCopiesFoundNote =
            "Make a safe copy in Windowed & Mods, or press Choose a folder instead.";

        /// <summary>
        /// The short marker shown beside a cheat nobody has watched work, or null for one somebody
        /// has. This is the visible half of the evidence: the full sentence moves behind the
        /// disclosure, but a player must not have to open anything to learn that a switch has
        /// never been seen doing what it says.
        /// </summary>
        public static string? DescribeEvidenceTag(CheatCode? cheat)
        {
            if (cheat is null)
            {
                return null;
            }

            return cheat.Evidence == CheatEvidenceLevel.FoundInGameCodeOnly ? "Untested" : null;
        }

        /// <summary>
        /// The accessible name for one cheat's disclosure. Every one of them shows the same words,
        /// so the label alone would give a screen reader eight identical controls.
        /// </summary>
        public static string BuildEvidenceDisclosureName(CheatCode? cheat)
        {
            return cheat is null
                ? EvidenceDisclosureLabel
                : $"{EvidenceDisclosureLabel} about {cheat.DisplayName}";
        }

        /// <summary>The big line: exactly what the file will be called.</summary>
        public static string BuildNameHeadline(CheatSaveName? composition)
        {
            if (composition is null || !composition.IsUsable)
            {
                return "Pick a cheat to see the file name.";
            }

            return composition.FileName;
        }

        /// <summary>
        /// The sentence under the file name. It says which cheats the name switches on, names any
        /// the player did not tick, and repeats that nothing else changes.
        /// </summary>
        public static string BuildNameExplanation(CheatSaveName? composition)
        {
            if (composition is null)
            {
                return "Tick a cheat above and the file name appears here before anything is written.";
            }

            if (!composition.IsUsable)
            {
                return composition.Problem ?? "That name cannot be used.";
            }

            string[] activeNames = composition.ActiveCheatIds
                .Select(id => CheatCodeCatalog.FindById(id)?.DisplayName)
                .Where(name => !string.IsNullOrWhiteSpace(name))
                .Select(name => name!)
                .ToArray();
            if (activeNames.Length == 0)
            {
                return "This name carries no cheats. It is an ordinary copy of your save.";
            }

            string list = JoinReadable(activeNames);
            string sentence = activeNames.Length == 1
                ? $"This name switches on {list}."
                : $"This name switches on {list} - the game looks for each word separately.";

            string[] unrequested = composition.ActiveCheatIds
                .Where(id => !composition.RequestedCheatIds.Contains(id, StringComparer.OrdinalIgnoreCase))
                .Select(id => CheatCodeCatalog.FindById(id)?.DisplayName)
                .Where(name => !string.IsNullOrWhiteSpace(name))
                .Select(name => name!)
                .ToArray();
            if (unrequested.Length > 0)
            {
                sentence += $" {JoinReadable(unrequested)} came from the name you typed rather than a tick box.";
            }

            return sentence;
        }

        /// <summary>The chosen source save, named but never shown as a full path.</summary>
        public static string BuildSourceSummary(string? sourcePath)
        {
            if (string.IsNullOrWhiteSpace(sourcePath))
            {
                return "Press Choose a save and pick the career save you want to start from.";
            }

            return $"Starting from {Path.GetFileName(sourcePath)}. It is copied, not changed.";
        }

        public static string BuildDestinationSummary(CheatSaveTarget? safeCopy, string? chosenFolder)
        {
            if (safeCopy is not null)
            {
                return $"Going into the safe copy \"{safeCopy.DisplayName}\", in its savegames folder.";
            }

            if (!string.IsNullOrWhiteSpace(chosenFolder))
            {
                return $"Going into the folder \"{Path.GetFileName(Path.TrimEndingDirectorySeparator(chosenFolder))}\". "
                    + "Copy it into a safe copy's savegames folder when you want to play it.";
            }

            return NoSafeCopiesFoundNote;
        }

        /// <summary>
        /// What is still missing before the write button can do anything, or null when nothing is.
        /// </summary>
        public static string? DescribeWhatIsStillNeeded(
            string? sourcePath,
            CheatSaveName? composition,
            string? destinationDirectory)
        {
            if (string.IsNullOrWhiteSpace(sourcePath))
            {
                return "Choose a save to start from.";
            }

            if (composition is null || composition.RequestedCheatIds.Count == 0)
            {
                return "Tick at least one cheat.";
            }

            if (!composition.IsUsable)
            {
                return composition.Problem;
            }

            if (string.IsNullOrWhiteSpace(destinationDirectory))
            {
                return "Choose where the new save should go.";
            }

            return null;
        }

        public static string BuildOverwriteQuestion(string fileName)
        {
            return $"{fileName} is already there. Replacing it cannot be undone. "
                + "Rename yours instead if you want to keep both.";
        }

        private static string JoinReadable(IReadOnlyList<string> values)
        {
            return values.Count switch
            {
                0 => string.Empty,
                1 => values[0],
                2 => $"{values[0]} and {values[1]}",
                _ => string.Join(", ", values.Take(values.Count - 1)) + " and " + values[^1],
            };
        }
    }
}
