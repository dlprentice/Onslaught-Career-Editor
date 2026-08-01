using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// The result of turning a set of chosen cheats into one save file name.
    /// </summary>
    /// <param name="Name">The name without the extension - this is what the game reads.</param>
    /// <param name="FileName">The name with <c>.bes</c> on the end - this is what lands on disk.</param>
    /// <param name="RequestedCheatIds">The cheats the user asked for, in catalog order.</param>
    /// <param name="AppendedCheatIds">
    /// The cheats whose code this composition actually had to add. A cheat is skipped when its
    /// code is already somewhere in the name the user typed, because the game matches on any
    /// substring and adding it twice would change nothing.
    /// </param>
    /// <param name="ActiveCheatIds">
    /// Every cheat the finished name switches on, including any the user did not tick but whose
    /// code happens to sit inside the text they typed.
    /// </param>
    /// <param name="Problem">Null when the name is usable; otherwise why it is not.</param>
    public sealed record CheatSaveName(
        string Name,
        string FileName,
        IReadOnlyList<string> RequestedCheatIds,
        IReadOnlyList<string> AppendedCheatIds,
        IReadOnlyList<string> ActiveCheatIds,
        string? Problem)
    {
        public bool IsUsable => Problem is null;
    }

    /// <summary>
    /// Builds the save file name that carries a chosen set of cheats, and reads a name back to
    /// say which cheats it switches on.
    ///
    /// Everything here is pure: no filesystem, no clock, no configuration. The whole point of the
    /// Cheats page is that the only thing it changes is a file *name*, so the rule that decides
    /// that name has to be something a test can pin down exactly.
    ///
    /// The matching rule is the game's own: <c>strstr(saveName, code)</c>, which is an ordinal,
    /// case-sensitive substring test. That is why several codes fit in one name, and why a code
    /// already present is not worth appending again.
    ///
    /// One detail matters enough to model rather than assume. Windows file names are UTF-16, and
    /// the game does not compare UTF-16: <c>FromWCHAR</c> (0x004f7d30) "copies the low byte from
    /// each 16-bit input slot", and <c>IsCheatActive</c> is listed among its callers at
    /// 0x004654f8 (reverse-engineering/binary-analysis/functions/string-helpers.md). So the bytes
    /// the game actually compares are the low byte of each character in the file name. That is
    /// exactly what <see cref="ToGameComparisonBytes"/> reproduces, and it is why the goodie
    /// gating code - whose third character is the single byte 0xEA - matches at all. Encode that
    /// name as UTF-8 anywhere in the chain and 0xEA becomes 0xC3 0xAA, and the cheat silently
    /// does nothing.
    /// </summary>
    public static class CheatSaveNameComposer
    {
        /// <summary>
        /// The longest name this app will build. This is the app's own limit, chosen to keep names
        /// readable - it is not a limit read out of the game.
        /// </summary>
        public const int MaximumNameLength = 64;

        public const string SaveExtension = ".bes";

        /// <summary>
        /// The game truncates each UTF-16 character to its low byte, so U+00FF is the highest
        /// character that reaches it unchanged.
        /// </summary>
        public const char MaximumCharacterTheGameCanRead = '\u00FF';

        private static readonly string[] s_reservedDosNames =
        {
            "CON", "PRN", "AUX", "NUL", "CLOCK$", "CONIN$", "CONOUT$",
            "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
        };

        /// <summary>
        /// Compose the file name for a set of cheats, optionally keeping a name the player typed.
        /// </summary>
        public static CheatSaveName Compose(string? baseName, IEnumerable<string>? selectedCheatIds)
        {
            IReadOnlyList<CheatCode> requested = CheatCodeCatalog.Resolve(selectedCheatIds);
            string[] requestedIds = requested.Select(cheat => cheat.Id).ToArray();
            string trimmedBase = (baseName ?? string.Empty).Trim();

            string? baseProblem = DescribeBaseNameProblem(trimmedBase);
            if (baseProblem is not null)
            {
                return Failed(trimmedBase, requestedIds, baseProblem);
            }

            var appended = new List<string>();
            string name = trimmedBase;
            foreach (CheatCode cheat in requested)
            {
                // Already in the name the player typed, so the game already sees it.
                if (ContainsCode(name, cheat.Code))
                {
                    continue;
                }

                name += cheat.Code;
                appended.Add(cheat.Id);
            }

            if (name.Length == 0)
            {
                return Failed(
                    name,
                    requestedIds,
                    "Choose at least one cheat, or type a name of your own.");
            }

            string? nameProblem = DescribeComposedNameProblem(name);
            if (nameProblem is not null)
            {
                return Failed(name, requestedIds, nameProblem);
            }

            // Belt and braces: check the finished name against the bytes the game will really
            // compare, not against the C# string. A string comparison would happily pass for a
            // name whose bytes on disk cannot match.
            CheatCode[] missing = requested
                .Where(cheat => !GameBytesContainCode(name, cheat.Code))
                .ToArray();
            if (missing.Length > 0)
            {
                return Failed(
                    name,
                    requestedIds,
                    $"That name cannot carry {string.Join(", ", missing.Select(cheat => cheat.DisplayName))} "
                        + "because of the characters it contains. Try a simpler name.");
            }

            return new CheatSaveName(
                Name: name,
                FileName: name + SaveExtension,
                RequestedCheatIds: requestedIds,
                AppendedCheatIds: appended,
                ActiveCheatIds: ActiveCheatIdsIn(name),
                Problem: null);
        }

        /// <summary>
        /// Which offered cheats a given save name switches on. This is the read-back half of
        /// <see cref="Compose"/> and follows the same ordinal, case-sensitive substring rule the
        /// game uses.
        /// </summary>
        public static IReadOnlyList<CheatCode> ActiveCheatsIn(string? saveName)
        {
            string name = saveName ?? string.Empty;
            return CheatCodeCatalog.All
                .Where(cheat => ContainsCode(name, cheat.Code))
                .ToArray();
        }

        public static IReadOnlyList<string> ActiveCheatIdsIn(string? saveName)
        {
            return ActiveCheatsIn(saveName).Select(cheat => cheat.Id).ToArray();
        }

        /// <summary>Does this name switch on that particular cheat?</summary>
        public static bool NameActivates(string? saveName, string? cheatId)
        {
            CheatCode? cheat = CheatCodeCatalog.FindById(cheatId);
            return cheat is not null && ContainsCode(saveName ?? string.Empty, cheat.Code);
        }

        /// <summary>
        /// Why a name the player typed cannot be used, or null when it can. Empty is allowed:
        /// the codes alone make a perfectly good name.
        /// </summary>
        public static string? DescribeBaseNameProblem(string? baseName)
        {
            string name = (baseName ?? string.Empty).Trim();
            if (name.Length == 0)
            {
                return null;
            }

            char[] invalid = Path.GetInvalidFileNameChars();
            char[] offenders = name.Where(character => invalid.Contains(character)).Distinct().ToArray();
            if (offenders.Length > 0)
            {
                return $"A file name cannot contain {DescribeCharacters(offenders)}. Try a different name.";
            }

            if (name.Length > MaximumNameLength)
            {
                return $"Keep the name to {MaximumNameLength} characters or fewer.";
            }

            // The game only ever sees the low byte of each character, so anything above U+00FF
            // reaches it as a different character entirely. Rather than let the player type a
            // name the game will read as something else, say so.
            if (name.Any(character => character > MaximumCharacterTheGameCanRead))
            {
                return "The game can only read plain Western characters in a save name. "
                    + "Try one without accented or non-Latin letters beyond the basic set.";
            }

            return null;
        }

        /// <summary>
        /// The bytes the game compares, reproduced exactly: the low byte of each UTF-16 unit in
        /// the file name, which is what <c>FromWCHAR</c> hands to <c>strstr</c>.
        /// </summary>
        public static byte[] ToGameComparisonBytes(string? name)
        {
            string text = name ?? string.Empty;
            byte[] bytes = new byte[text.Length];
            for (int index = 0; index < text.Length; index++)
            {
                bytes[index] = unchecked((byte)text[index]);
            }

            return bytes;
        }

        /// <summary>
        /// Does the name, as the game will read it byte for byte, contain this code?
        /// </summary>
        public static bool GameBytesContainCode(string? name, string? code)
        {
            byte[] haystack = ToGameComparisonBytes(name);
            byte[] needle = ToGameComparisonBytes(code);
            if (needle.Length == 0 || needle.Length > haystack.Length)
            {
                return false;
            }

            for (int start = 0; start <= haystack.Length - needle.Length; start++)
            {
                bool matched = true;
                for (int offset = 0; offset < needle.Length; offset++)
                {
                    if (haystack[start + offset] != needle[offset])
                    {
                        matched = false;
                        break;
                    }
                }

                if (matched)
                {
                    return true;
                }
            }

            return false;
        }

        /// <summary>
        /// Why the finished name would not be a legal Windows file name, or null when it is.
        /// </summary>
        public static string? DescribeComposedNameProblem(string? composedName)
        {
            string name = composedName ?? string.Empty;
            if (name.Length == 0)
            {
                return "Choose at least one cheat, or type a name of your own.";
            }

            char[] invalid = Path.GetInvalidFileNameChars();
            char[] offenders = name.Where(character => invalid.Contains(character)).Distinct().ToArray();
            if (offenders.Length > 0)
            {
                return $"A file name cannot contain {DescribeCharacters(offenders)}. Try a different name.";
            }

            if (name.Length > MaximumNameLength)
            {
                return $"That name comes to {name.Length} characters. Keep it to {MaximumNameLength} or fewer - "
                    + "shorten the part you typed, or pick fewer cheats.";
            }

            if (name[^1] == '.' || name[^1] == ' ')
            {
                return "A file name cannot end with a space or a dot.";
            }

            string stem = name.Split('.', 2)[0].TrimEnd(' ', '.');
            if (s_reservedDosNames.Any(reserved => string.Equals(reserved, stem, StringComparison.OrdinalIgnoreCase)))
            {
                return $"Windows reserves the name '{stem}'. Try a different name.";
            }

            return null;
        }

        private static CheatSaveName Failed(string name, IReadOnlyList<string> requestedIds, string problem)
        {
            return new CheatSaveName(
                Name: name,
                FileName: name.Length == 0 ? string.Empty : name + SaveExtension,
                RequestedCheatIds: requestedIds,
                AppendedCheatIds: Array.Empty<string>(),
                ActiveCheatIds: Array.Empty<string>(),
                Problem: problem);
        }

        // Every containment question in this class funnels through the byte model, because that
        // is the only comparison the game actually performs. A C# string comparison agrees with
        // it for ordinary names and disagrees exactly where it matters - accented codes, and any
        // character above U+00FF that the game would truncate into something else.
        private static bool ContainsCode(string name, string code) =>
            GameBytesContainCode(name, code);

        private static string DescribeCharacters(IReadOnlyList<char> characters)
        {
            string[] rendered = characters
                .Select(character => char.IsControl(character) ? "control characters" : $"'{character}'")
                .Distinct(StringComparer.Ordinal)
                .ToArray();
            return rendered.Length == 1
                ? rendered[0]
                : string.Join(", ", rendered[..^1]) + " or " + rendered[^1];
        }
    }
}
