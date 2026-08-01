using System;
using System.Collections.Generic;
using System.Text;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Builds a structurally real Battle Engine Aquila language file in memory.
    ///
    /// Built rather than checked in: no retail bytes are tracked, and the parser cases stay
    /// deterministic on a machine that has never seen the game. The layout mirrors the game's own
    /// <c>CText__Init</c> loader, so a test that passes here is testing the same shape the retail
    /// file has - the suite proves that separately against a real installation.
    /// </summary>
    internal static class TestLanguageFile
    {
        public static byte[] Build(params (string Text, string? Audio)[] entries)
        {
            ArgumentNullException.ThrowIfNull(entries);

            var textPool = new List<byte>();
            var audioPool = new List<byte>();
            var textOffsetsInWords = new List<uint>();
            var audioOffsets = new List<uint>();

            foreach ((string text, string? audio) in entries)
            {
                textOffsetsInWords.Add((uint)(textPool.Count / 2));
                textPool.AddRange(Encoding.Unicode.GetBytes(text));
                textPool.AddRange(new byte[] { 0, 0 });

                if (audio is null)
                {
                    audioOffsets.Add(0xFFFFFFFF);
                }
                else
                {
                    audioOffsets.Add((uint)audioPool.Count);
                    audioPool.AddRange(Encoding.ASCII.GetBytes(audio));
                    audioPool.Add(0);
                }
            }

            int count = entries.Length;
            const int entriesOffset = 0x0C;
            int uvar7Offset = entriesOffset + (count * 0x0C);
            int textPoolOffset = uvar7Offset + 4;

            // The loader finds the audio pool at (uVar7 + count*12) + 0x14, so choose uVar7 to put
            // that anchor immediately after the string pool.
            int anchor = textPoolOffset + textPool.Count;
            uint uvar7 = (uint)(anchor - (count * 0x0C));

            var file = new List<byte>();
            file.AddRange(BitConverter.GetBytes(0xFFFFFFBBu));
            file.AddRange(BitConverter.GetBytes(3u));
            file.AddRange(BitConverter.GetBytes((uint)count));

            for (int index = 0; index < count; index++)
            {
                file.AddRange(BitConverter.GetBytes((uint)(0x1000 + index)));
                file.AddRange(BitConverter.GetBytes(textOffsetsInWords[index]));
                file.AddRange(BitConverter.GetBytes(audioOffsets[index]));
            }

            file.AddRange(BitConverter.GetBytes(uvar7));
            file.AddRange(textPool);
            file.AddRange(new byte[0x10]);
            file.AddRange(BitConverter.GetBytes((uint)audioPool.Count));
            file.AddRange(audioPool);

            return file.ToArray();
        }
    }
}
