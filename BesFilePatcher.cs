using System;
using System.Buffers.Binary;
using System.IO;

namespace Onslaught___Career_Editor
{
    public class BesFilePatcher
    {
        // ---------- layout constants ----------
        private const int NODE_SIZE = 64;
        private const int NODE_COUNT = 100;
        private const int LINK_SIZE = 8;
        private const int LINK_COUNT = 200;

        private const int NODE_BASE = 0x0004;
        private const int LINK_BASE = 0x1904;
        private const int GOODIE_BASE = 0x1F44;
        private const int KILLS_BASE = 0x23A4;
        private const int PROGRESS = 0x22D4;
        private const int GOD_MODE = 0x240C;   // mIsGod[0] – int<<16 (Note: only works in Free-Play mode)
        private const int TECH_SLOTS_BASE = 0x244C; // 32 × 4 B tech slot bit-fields

        private const int SHIFT = 16;
        private const uint TRUE32 = 1u << SHIFT;    // 0x0001_0000
        private const uint OLD32 = 3u << SHIFT;     // goodie = OLD (blue color)
        private const uint NEW32 = 2u << SHIFT;     // goodie = NEW (gold color)
        private const uint OBJ_ALL = 7u << SHIFT;   // primary + both secondary objectives
        private const uint SENTINEL = 0xBF80_0000;  // float -1.0 (required at offset 0x00)
        private const float B_SCORE = 600_000f;     // placeholder score
        private const float S_SCORE = 900_000f;     // grade S score

        // Patch configuration
        public bool EnableGodMode { get; set; } = false;
        public bool UseNewGoodiesInstead { get; set; } = false;
        public int GlobalKillCount { get; set; } = 100;
        public float RankingScore { get; set; } = 900_000f; // Default to S-rank
        public bool EnableAllObjectives { get; set; } = false;

        public string PatchFile(string inputPath, string outputPath)
        {
            try
            {
                byte[] buf = File.ReadAllBytes(inputPath);

                // Mark career started
                buf[PROGRESS] = 1;

                // Apply god mode if enabled
                SetGodMode(buf, EnableGodMode);

                // --- nodes ---
                for (int n = 0; n < NODE_COUNT; n++)
                {
                    int off = NODE_BASE + n * NODE_SIZE;
                    if (off + NODE_SIZE > buf.Length) break;

                    PatchNode(buf, off, RankingScore, EnableAllObjectives);
                }

                // --- links ---
                for (int l = 0; l < LINK_COUNT; l++)
                    WriteUInt32(buf, LINK_BASE + l * LINK_SIZE, TRUE32);

                // --- goodies ---
                for (int g = 0; g < 300; g++)
                    WriteUInt32(buf, GOODIE_BASE + g * 4, UseNewGoodiesInstead ? NEW32 : OLD32);

                // --- global kills ---
                SetGlobalKills(buf, GlobalKillCount);

                File.WriteAllBytes(outputPath, buf);
                return $"Successfully patched: {outputPath}";
            }
            catch (Exception ex)
            {
                return $"Error: {ex.Message}";
            }
        }

        // ---------- helpers ----------
        private static void WriteUInt32(byte[] buf, int offset, uint val) =>
            BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(offset, 4), val);

        private static void WriteFloat(byte[] buf, int offset, float val) =>
            BitConverter.GetBytes(val).CopyTo(buf, offset);

        /// <summary>
        /// Read a UInt32 value from the buffer at the specified offset
        /// </summary>
        private static uint ReadUInt32(byte[] buf, int offset) =>
            BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(offset, 4));

        /// <summary>
        /// Enable or disable god mode
        /// </summary>
        public void SetGodMode(byte[] buf, bool on)
        {
            WriteUInt32(buf, GOD_MODE, on ? TRUE32 : 0);
        }

        /// <summary>
        /// Set global kill counts for all 5 categories
        /// </summary>
        public void SetGlobalKills(byte[] buf, int kills)
        {
            uint encoded = (uint)(kills << SHIFT);
            for (int k = 0; k < 5; k++)
                WriteUInt32(buf, KILLS_BASE + k * 4, encoded);
        }

        /// <summary>
        /// Enable/disable a specific bit in a tech slot
        /// </summary>
        public void SetSlotBit(byte[] buf, int slotIndex, int bitIndex, bool on)
        {
            if (slotIndex < 0 || slotIndex >= 32) return; // Safety check
            if (bitIndex < 0 || bitIndex >= 32) return; // Safety check

            int off = TECH_SLOTS_BASE + slotIndex * 4;
            uint cur = ReadUInt32(buf, off);
            uint mask = 1u << bitIndex;
            uint next = on ? cur | mask : cur & ~mask;
            WriteUInt32(buf, off, next);
        }

        /// <summary>
        /// Patch a node with custom score and objective settings
        /// </summary>
        private void PatchNode(byte[] buf, int off, float score, bool objectives)
        {
            // 1) Set sentinel value -1.0f (REQUIRED for PC grade calculation)
            WriteUInt32(buf, off + 0x00, SENTINEL);        // float -1.0 (0xBF80_0000)

            // 2) Mark level as completed (makes links walkable)
            WriteUInt32(buf, off + 0x04, TRUE32);          // 0x0001_0000

            // 3) Set objective mask when enabled
            // On PC, this is what determines the letter grade when sentinel is -1.0f
            if (objectives)
                WriteUInt32(buf, off + 0x18, OBJ_ALL);     // 0x0007_0000 (all objectives complete)
            
            // 4) Zero attempts to keep stats clean
            WriteUInt32(buf, off + 0x38, 0);               // 0x0000_0000
            
            // 5) Set ranking score - note that on PC version with proper sentinel and objective
            // mask, this value is ignored for letter grade calculation and can be 0.0
            WriteFloat(buf, off + 0x3C, 1.0f);            // Appropriate values: 1.0f (S), 0.75f (A), 0.5f (B), 0.25f (C)
        }
    }
}
