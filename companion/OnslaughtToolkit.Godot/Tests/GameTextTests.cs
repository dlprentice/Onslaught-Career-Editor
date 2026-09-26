// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.Text;
using OnslaughtToolkit.Companion.Game;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The game-text layer on a synthetic language table built in the documented v3 layout from
/// original strings (never retail text), decoded through the linked AppCore reader.
/// </summary>
internal static class GameTextTests
{
    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("game text");
        IReadOnlyDictionary<string, uint> names = GameText.ParseNames(
            "#define\tGOODIE_TEXT_1_TITLE\t\t971379130\r\n#define GOODIE_TEXT_3_TITLE 42\r\n// comment\r\n#define BROKEN x\r\n");
        check.That(names.Count == 2 && names["GOODIE_TEXT_1_TITLE"] == 971379130 && names["GOODIE_TEXT_3_TITLE"] == 42,
            "text.stf #define lines map names to ids; anything else is ignored.");

        string game = Path.Combine(outputDirectory, "game-text", "game");
        GameText? text = LoadSample(game);
        check.That(text is { Language: "english", LevelCount: 2 }, "A language table decodes and its level names are recognised by shape.");
        check.That(text?.LevelName(100) == "1.00 - Test Flight" && text.LevelName(211) == "2.11 - Example Crossing" &&
            text.LevelName(999) is null, "Level numbers map to the game's dotted codes; the plain row wins over (Evo).");
        check.That(text?.GoodieTitle(0) == "First Title" && text.GoodieTitle(2) == "Third Title" && text.GoodieTitle(1) is null,
            "Goodie titles come through text.stf's GOODIE_TEXT_n_TITLE names, one-based.");
        check.That(text?.VoiceLine("v211_01") == "Hello from the briefing.", "Voice lines are found by their audio name.");

        File.WriteAllBytes(Path.Combine(game, "data", "language", "english.dat"), [0xBB, 0xFF, 0xFF, 0xFF, 3, 0, 0, 0, 200, 0, 0, 0]);
        check.That(GameText.Load(game) is null, "A truncated table is no text, not an error.");
        check.That(GameText.Load(Path.Combine(outputDirectory, "game-text", "absent")) is null, "A folder without text is no text.");
    }

    /// <summary>A game folder holding only a synthetic language table and text.stf, loaded as the game's text.</summary>
    internal static GameText? LoadSample(string game)
    {
        Directory.CreateDirectory(Path.Combine(game, "data", "language"));
        Directory.CreateDirectory(Path.Combine(game, "data", "MissionScripts", "text"));
        File.WriteAllBytes(Path.Combine(game, "data", "language", "english.dat"), LanguageTable(
        [
            (10, "1.00 - Test Flight", null), (11, "2.11 - Example Crossing", null),
            (12, "2.11 - Example Crossing (Evo)", null), (971379130, "First Title", null), (42, "Third Title", null),
            (13, "Hello from the briefing.", "V211_01"),
        ]));
        File.WriteAllText(Path.Combine(game, "data", "MissionScripts", "text", "text.stf"),
            "#define GOODIE_TEXT_1_TITLE 971379130\r\n#define GOODIE_TEXT_3_TITLE 42\r\n");
        return GameText.Load(game);
    }

    /// <summary>The v3 table: header, entries, uVar7, UTF-16 pool, then the audio pool the loader finds through uVar7.</summary>
    private static byte[] LanguageTable(IReadOnlyList<(uint Id, string Text, string? Audio)> entries)
    {
        MemoryStream textPool = new(), audioPool = new();
        List<(uint Id, uint TextWords, uint AudioBytes)> rows = [];
        foreach ((uint id, string value, string? audio) in entries)
        {
            uint words = (uint)(textPool.Length / 2);
            textPool.Write(Encoding.Unicode.GetBytes(value + "\0"));
            uint audioOffset = 0xFFFFFFFF;
            if (audio is not null)
            {
                audioOffset = (uint)audioPool.Length;
                audioPool.Write(Encoding.ASCII.GetBytes(audio + "\0"));
            }
            rows.Add((id, words, audioOffset));
        }
        int count = rows.Count;
        long textEnd = 16 + 12L * count + textPool.Length;
        MemoryStream table = new();
        byte[] word = new byte[4];
        void Put(uint value)
        {
            BinaryPrimitives.WriteUInt32LittleEndian(word, value);
            table.Write(word);
        }
        Put(0xFFFFFFBB);
        Put(3);
        Put((uint)count);
        foreach ((uint id, uint words, uint audio) in rows)
        {
            Put(id);
            Put(words);
            Put(audio);
        }
        Put((uint)(textEnd - 0x10 - 12L * count)); // uVar7: the audio anchor is uVar7 + 12 * count.
        table.Write(textPool.ToArray());
        Put((uint)audioPool.Length);
        table.Write(audioPool.ToArray());
        return table.ToArray();
    }
}
