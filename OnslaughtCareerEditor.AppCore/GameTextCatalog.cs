using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>One string the game itself would show, and the voice line that goes with it.</summary>
    /// <param name="AudioName">
    /// The voice file this line is spoken in, or null for text with no recording. The game keeps
    /// them together, which is how a subtitle finds its audio.
    /// </param>
    public sealed record GameTextEntry(uint TextId, string Text, string? AudioName);

    /// <summary>
    /// The game's own text, decoded from the language file in the user's installation.
    /// </summary>
    /// <param name="LanguageName">
    /// The file's own name - <c>english</c>, <c>french</c>, and so on. The game ships six, and
    /// whichever one the player has is the one this reads, so the app ends up speaking the same
    /// language their game does without being told to.
    /// </param>
    public sealed record GameTextCatalog(
        string SourcePath,
        string LanguageName,
        IReadOnlyList<GameTextEntry> Entries)
    {
        public int Count => Entries.Count;
    }

    /// <summary>One mission, as the game's own Select Level screen names it.</summary>
    /// <param name="Code">The dotted code, <c>2.11</c>.</param>
    /// <param name="Title">Just the name, <c>Assault On Apollo</c>.</param>
    /// <param name="Display">Both, as the game writes it: <c>2.11 - Assault On Apollo</c>.</param>
    /// <param name="IsEvolvedVariant">
    /// True for the <c>(Evo)</c> rows. The game ships a harder second version of most missions and
    /// names it that way; they are separate entries and are not merged here.
    /// </param>
    public sealed record GameLevelName(
        string Code,
        string Title,
        string Display,
        bool IsEvolvedVariant);

    /// <summary>
    /// Reads the game's own string table out of <c>data/language/&lt;language&gt;.dat</c>.
    ///
    /// The app had been inventing labels it could not know - the Media page grouped voice lines
    /// under "Mission 211" because that is what the filename says, while the game itself calls that
    /// mission "2.11 - Assault On Apollo". The real names were never missing; they were sitting in
    /// a file this project had already worked out how to read, in `tools/language_dat_decode.py`.
    /// This is that decoder in C#, so the app can do it at run time against the player's own
    /// installation rather than shipping a table that would be wrong for five of the six languages.
    ///
    /// Everything here is defensive on purpose. This parses a retail file the app does not own and
    /// cannot repair, on a path that runs while a page is being drawn, so a malformed or truncated
    /// file has to end as "no catalog" and never as an exception reaching the UI.
    ///
    /// Format (v2/v3), from the game's own `CText__Init` at <c>0x004f21f0</c>:
    /// <code>
    ///   u32 magic      = 0xFFFFFFBB
    ///   u32 ver_flags  = 2 or 3, high bit is a wide flag
    ///   u32 count
    ///   entry[count]   { u32 textId; u32 textOffsetInUtf16Units; u32 audioOffsetBytes }
    ///   u32 uVar7      language-specific offset the loader uses to find the audio pool
    ///   UTF-16LE string pool, NUL terminated
    ///   audio name pool, ASCII, NUL terminated
    /// </code>
    /// </summary>
    public static class GameTextCatalogService
    {
        private const uint MagicV3 = 0xFFFFFFBB;
        private const int EntrySize = 0x0C;
        private const uint NoAudio = 0xFFFFFFFF;

        /// <summary>
        /// Preference order when an installation ships several. English first because the project's
        /// own evidence is in English; after that whatever is actually present, so a French install
        /// with no english.dat still gets French rather than nothing.
        /// </summary>
        private static readonly string[] PreferredLanguages =
        {
            "english", "american", "french", "german", "italian", "spanish",
        };

        /// <summary>The game's text for an installation, or null when it cannot be read.</summary>
        public static GameTextCatalog? TryLoadFromGameDirectory(string? gameDirectory)
        {
            if (string.IsNullOrWhiteSpace(gameDirectory))
                return null;

            try
            {
                string languageDirectory = Path.Combine(gameDirectory, "data", "language");
                if (!Directory.Exists(languageDirectory))
                    return null;

                string[] candidates = Directory.GetFiles(languageDirectory, "*.dat");
                if (candidates.Length == 0)
                    return null;

                foreach (string preferred in PreferredLanguages)
                {
                    string? match = candidates.FirstOrDefault(path =>
                        string.Equals(
                            Path.GetFileNameWithoutExtension(path),
                            preferred,
                            StringComparison.OrdinalIgnoreCase));

                    if (match is not null && TryLoad(match, out GameTextCatalog? catalog))
                        return catalog;
                }

                foreach (string candidate in candidates.OrderBy(path => path, StringComparer.OrdinalIgnoreCase))
                {
                    if (TryLoad(candidate, out GameTextCatalog? catalog))
                        return catalog;
                }

                return null;
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
            {
                return null;
            }
        }

        /// <summary>Decode one language file, or report that it could not be decoded.</summary>
        public static bool TryLoad(string datPath, out GameTextCatalog? catalog)
        {
            catalog = null;
            if (string.IsNullOrWhiteSpace(datPath) || !File.Exists(datPath))
                return false;

            try
            {
                byte[] data = File.ReadAllBytes(datPath);
                catalog = Decode(data, datPath);
                return catalog is not null;
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException
                                        or ArgumentException or OutOfMemoryException)
            {
                return false;
            }
        }

        /// <summary>
        /// The parse itself, on bytes already in hand. Returns null rather than throwing for every
        /// malformed shape, because "this is not a language file" is an ordinary outcome here - the
        /// app points at whatever folder a person chose.
        /// </summary>
        internal static GameTextCatalog? Decode(byte[] data, string sourcePath)
        {
            ArgumentNullException.ThrowIfNull(data);

            if (data.Length < 0x0C)
                return null;

            if (ReadUInt32(data, 0x00) != MagicV3)
                return null;

            uint versionFlags = ReadUInt32(data, 0x04);
            uint version = versionFlags & 0x7FFFFFFF;
            if (version is not (2 or 3))
                return null;

            uint count = ReadUInt32(data, 0x08);

            // A count is a byte pattern until it has been checked. Reject anything that would need
            // more file than exists before allocating for it.
            const int entriesOffset = 0x0C;
            long needed = (long)entriesOffset + ((long)count * EntrySize) + 4;
            if (count == 0 || needed > data.Length)
                return null;

            long uvar7Offset = entriesOffset + ((long)count * EntrySize);
            uint uvar7 = ReadUInt32(data, (int)uvar7Offset);
            int textPoolOffset = (int)uvar7Offset + 4;

            // Mirrors the loader: the audio pool is found through uVar7, not by walking the strings.
            long audioAnchor = (long)uvar7 + ((long)count * EntrySize);
            if (audioAnchor < 0 || audioAnchor + 0x14 > data.Length)
                return null;

            uint audioPoolSize = ReadUInt32(data, (int)(audioAnchor + 0x10));
            long audioPoolOffset = audioAnchor + 0x14;
            if (audioPoolOffset + audioPoolSize > data.Length)
                return null;

            var entries = new List<GameTextEntry>((int)count);
            for (uint index = 0; index < count; index++)
            {
                int entryOffset = entriesOffset + (int)(index * EntrySize);
                uint textId = ReadUInt32(data, entryOffset);
                uint textOffsetWords = ReadUInt32(data, entryOffset + 0x04);
                uint audioOffsetBytes = ReadUInt32(data, entryOffset + 0x08);

                long textOffset = textPoolOffset + ((long)textOffsetWords * 2);
                if (textOffset < 0 || textOffset >= data.Length)
                    continue;

                string text = ReadUtf16NulTerminated(data, (int)textOffset);

                string? audioName = null;
                if (audioOffsetBytes != NoAudio)
                {
                    long audioOffset = audioPoolOffset + audioOffsetBytes;
                    if (audioOffset >= 0 && audioOffset < data.Length)
                        audioName = ReadAsciiNulTerminated(data, (int)audioOffset);
                }

                entries.Add(new GameTextEntry(textId, text, audioName));
            }

            if (entries.Count == 0)
                return null;

            return new GameTextCatalog(
                SourcePath: sourcePath,
                LanguageName: Path.GetFileNameWithoutExtension(sourcePath),
                Entries: entries);
        }

        /// <summary>
        /// The mission names, as the game's own Select Level screen writes them.
        ///
        /// They are recognised by shape - <c>N.NN - Title</c> - rather than by id, because the ids
        /// are content hashes with no ordering to them and nothing in this project has mapped the
        /// level-code table. The shape is unambiguous in practice: 43 rows match in the retail
        /// English file and no other string in it does.
        /// </summary>
        public static IReadOnlyList<GameLevelName> GetLevelNames(GameTextCatalog? catalog)
        {
            if (catalog is null)
                return Array.Empty<GameLevelName>();

            var names = new List<GameLevelName>();
            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            foreach (GameTextEntry entry in catalog.Entries)
            {
                if (!TryParseLevelName(entry.Text, out GameLevelName? name) || name is null)
                    continue;

                if (seen.Add(name.Display))
                    names.Add(name);
            }

            return names
                .OrderBy(name => name.Code, StringComparer.Ordinal)
                .ThenBy(name => name.IsEvolvedVariant)
                .ToArray();
        }

        /// <summary>
        /// <c>"2.11 - Assault On Apollo"</c> into its parts, or false for anything else.
        /// </summary>
        internal static bool TryParseLevelName(string? text, out GameLevelName? name)
        {
            name = null;
            if (string.IsNullOrWhiteSpace(text))
                return false;

            string trimmed = text.Trim();
            int separator = trimmed.IndexOf(" - ", StringComparison.Ordinal);
            if (separator <= 0)
                return false;

            string code = trimmed[..separator];
            string title = trimmed[(separator + 3)..].Trim();
            if (title.Length == 0)
                return false;

            // N.NN exactly: one or more digits, a dot, two digits.
            int dot = code.IndexOf('.');
            if (dot <= 0 || code.Length - dot - 1 != 2)
                return false;

            for (int index = 0; index < code.Length; index++)
            {
                if (index == dot)
                    continue;

                if (!char.IsAsciiDigit(code[index]))
                    return false;
            }

            name = new GameLevelName(
                Code: code,
                Title: title,
                Display: $"{code} - {title}",
                IsEvolvedVariant: title.EndsWith("(Evo)", StringComparison.OrdinalIgnoreCase));

            return true;
        }

        /// <summary>
        /// The dotted code for a mission number taken from a filename: <c>211</c> is <c>2.11</c>.
        ///
        /// The game's own files number missions as three digits and its screens write them with the
        /// dot; both come from the same episode-and-mission pair. Returns null for anything that is
        /// not three digits, rather than guessing at a shape nobody has seen.
        /// </summary>
        public static string? TryGetLevelCodeForMissionNumber(int missionNumber)
        {
            if (missionNumber is < 100 or > 999)
                return null;

            return $"{missionNumber / 100}.{missionNumber % 100:00}";
        }

        private static uint ReadUInt32(byte[] data, int offset) =>
            BinaryPrimitives.ReadUInt32LittleEndian(data.AsSpan(offset, 4));

        private static string ReadUtf16NulTerminated(byte[] data, int offset)
        {
            int end = offset;
            while (end + 1 < data.Length)
            {
                if (data[end] == 0 && data[end + 1] == 0)
                    break;

                end += 2;
            }

            int byteLength = end - offset;
            return byteLength <= 0 ? string.Empty : Encoding.Unicode.GetString(data, offset, byteLength);
        }

        private static string ReadAsciiNulTerminated(byte[] data, int offset)
        {
            int end = offset;
            while (end < data.Length && data[end] != 0)
                end++;

            int length = end - offset;
            return length <= 0 ? string.Empty : Encoding.ASCII.GetString(data, offset, length);
        }
    }
}
