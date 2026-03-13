using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Result from a patching operation
    /// </summary>
    public class PatchResult
    {
        public bool Success { get; }
        public string Message { get; }

        private PatchResult(bool success, string message)
        {
            Success = success;
            Message = message;
        }

        public static PatchResult Ok(string message) => new PatchResult(true, message);
        public static PatchResult Fail(string message) => new PatchResult(false, message);
    }

    /// <summary>
    /// Data about an unmapped/reserved region in the save file.
    /// </summary>
    public class MysteryRegionData
    {
        public string Name { get; set; } = "";
        public string Description { get; set; } = "";
        public int StartOffset { get; set; }
        public int EndOffset { get; set; }
        public int Size => EndOffset - StartOffset;
        public byte[] Data { get; set; } = Array.Empty<byte>();
        public int NonZeroCount { get; set; }
        public bool AllZeros => NonZeroCount == 0;
        public bool AllFF { get; set; }
    }

    /// <summary>
    /// Results from analyzing a .bes save file
    /// </summary>
    public class SaveAnalysis
    {
        public bool IsValid { get; set; }
        public string? ErrorMessage { get; set; }
        public string? FilePath { get; set; }
        public bool IsOptionsFile { get; set; }
        public int FileSize { get; set; }
        public ushort VersionWord { get; set; }
        public uint VersionStamp { get; set; }
        public bool VersionValid { get; set; }
        public uint NewGoodieCountRaw { get; set; }
        public uint GodModeEnabledRaw { get; set; }
        public bool GodModeEnabledOn { get; set; }

        // CCareer settings near end of fixed block
        public uint CareerInProgressRaw { get; set; }
        public bool CareerInProgressOn { get; set; }
        public uint SoundVolumeBits { get; set; }
        public float SoundVolume { get; set; }
        public uint MusicVolumeBits { get; set; }
        public float MusicVolume { get; set; }
        // Steam build per-player toggles (verified in BEA.exe Controls UI):
        // - Walker mode invert Y axis: P1=CCareer+0x24A4, P2=CCareer+0x24A8
        // - Flight/Jet mode invert Y axis: P1=CCareer+0x249C, P2=CCareer+0x24A0
        // - Controller vibration: P1=CCareer+0x24AC, P2=CCareer+0x24B0
        public uint[] InvertYAxisRaw { get; set; } = new uint[2];
        public uint[] InvertFlightRaw { get; set; } = new uint[2];
        public uint[] VibrationRaw { get; set; } = new uint[2];
        public uint[] ControllerConfigNum { get; set; } = new uint[2];

        // Options entries + fixed tail snapshot (OptionsTail) at end of file
        public int OptionsEntryCount { get; set; }
        public int OptionsTailStart { get; set; }
        public uint OptionsMouseSensitivityBits { get; set; }
        public float OptionsMouseSensitivity { get; set; }
        public ushort OptionsControlSchemeIndex { get; set; }
        public ushort OptionsLanguageIndex { get; set; }
        public uint OptionsScreenShape { get; set; }
        public uint OptionsD3DDeviceIndex { get; set; }

        // Node analysis
        public int CompletedNodes { get; set; }
        public int EmptyNodes { get; set; }
        public int PartialNodes { get; set; }
        public Dictionary<string, int> RankDistribution { get; set; } = new();
        public List<(int Index, uint World, string Rank, uint RankBits)> CompletedNodeDetails { get; set; } = new();

        // Link analysis
        public int CompletedLinks { get; set; }
        public int TotalLinks { get; set; }

        // Goodie analysis
        public int GoodiesNew { get; set; }
        public int GoodiesOld { get; set; }
        public int GoodiesLocked { get; set; }
        public int GoodiesInstructions { get; set; }
        public int GoodiesOther { get; set; }
        public int GoodiesReserved { get; set; }

        // Kill counts
        public int[] KillCounts { get; set; } = new int[5];
        public byte[] KillMeta { get; set; } = new byte[5];
        public int?[] NextUnlockThresholds { get; set; } = new int?[5];

        // Tech slots
        public int ActiveTechSlots { get; set; }
        public int TotalTechSlots { get; set; }
        public uint[] TechSlotsRaw { get; set; } = Array.Empty<uint>();

        // Unmapped/reserved regions
        public List<MysteryRegionData> MysteryRegions { get; set; } = new();
    }

    public class BesFilePatcher
    {
        public sealed class BindingSlotOverride
        {
            // If null, preserve existing value from the file.
            public uint? DeviceCode { get; set; }
            public uint? PackedKey { get; set; }
        }

        public sealed class OptionsEntryOverride
        {
            public BindingSlotOverride Slot0 { get; } = new();
            public BindingSlotOverride Slot1 { get; } = new();
        }

        // ---------- layout constants ----------
        // File format confirmed via Ghidra static analysis of BEA.exe (Feb 2026)
        //
        // IMPORTANT: "true dword view"
        // - CCareer bytes are copied from source+2 (CCareer::Load) and saved to dest+2 (CCareer::Save).
        // - That means all CCareer dwords on disk are aligned to offsets where (file_offset % 4 == 2).
        // - If you view the file at 4-byte aligned offsets (file_offset % 4 == 0), values *look* like
        //   "shift-16", but that is just a misaligned view of the same bytes.
        public const int EXPECTED_FILE_SIZE = 10004;  // Exact size of valid .bes file

        private const int CAREER_BASE = 0x0002; // File offset where the CCareer memory dump begins (after version word)
        private const int CCAREER_NEW_GOODIE_COUNT = 0x0000;
        private const int CCAREER_NODE_BASE = 0x0004;
        private const int CCAREER_LINK_BASE = 0x1904;
        private const int CCAREER_GOODIE_BASE = 0x1F44;
        private const int CCAREER_KILLS_BASE = 0x23F4;
        private const int CCAREER_TECH_SLOTS_BASE = 0x2408;
        private const int CCAREER_CAREER_IN_PROGRESS = 0x2488;
        private const int CCAREER_SOUND_VOLUME = 0x248C;
        private const int CCAREER_MUSIC_VOLUME = 0x2490;
        private const int CCAREER_GOD_MODE_ENABLED = 0x2494;
        // Steam build per-save toggles (verified in BEA.exe):
        // - Walker invert Y axis: P1=+0x24A4, P2=+0x24A8
        // - Flight/Jet invert Y axis: P1=+0x249C, P2=+0x24A0
        // - Controller vibration: P1=+0x24AC, P2=+0x24B0
        private const int CCAREER_WALKER_INVERT_Y_P1 = 0x24A4;
        private const int CCAREER_WALKER_INVERT_Y_P2 = 0x24A8;
        private const int CCAREER_FLIGHT_INVERT_Y_P1 = 0x249C;
        private const int CCAREER_FLIGHT_INVERT_Y_P2 = 0x24A0;
        private const int CCAREER_VIBRATION_P1 = 0x24AC;
        private const int CCAREER_VIBRATION_P2 = 0x24B0;
        private const int CCAREER_CONTROLLER_CONFIG_P1 = 0x24B4;
        private const int CCAREER_CONTROLLER_CONFIG_P2 = 0x24B8;

        private const int NODE_SIZE = 64;             // CCareerNode struct
        private const int NODE_COUNT = 100;
        private const int LINK_SIZE = 8;              // CCareerNodeLink struct
        private const int LINK_COUNT = 200;

        private const int NODE_BASE = CAREER_BASE + CCAREER_NODE_BASE;    // CCareerNode[100] × 64 bytes
        private const int LINK_BASE = CAREER_BASE + CCAREER_LINK_BASE;    // CCareerNodeLink[200] × 8 bytes
        private const int GOODIE_BASE = CAREER_BASE + CCAREER_GOODIE_BASE;// CGoodie[300] × 4 bytes
        private const int KILLS_BASE = CAREER_BASE + CCAREER_KILLS_BASE;
        // NOTE (Feb 2026): The legacy 4-byte-aligned view placed "goodie 228" at 0x22D4 and
        // "mCareerInProgress" at 0x2488; both are artifacts of misalignment.
        // In the true dword view, Goodie 228 is at 0x22D6 and mCareerInProgress is at 0x248A.
        // Patch using true view offsets only.

        // Tech slots (mSlots[32]) - 128 bytes immediately after kill counters
        private const int TECH_SLOTS_BASE = CAREER_BASE + CCAREER_TECH_SLOTS_BASE;
        private const int TECH_SLOTS_COUNT = 32;

        // CCareer settings near end of fixed 0x24BC-byte block (true dword view file offsets)
        private const int NEW_GOODIE_COUNT = CAREER_BASE + CCAREER_NEW_GOODIE_COUNT;
        private const int CAREER_IN_PROGRESS = CAREER_BASE + CCAREER_CAREER_IN_PROGRESS;
        private const int SOUND_VOLUME = CAREER_BASE + CCAREER_SOUND_VOLUME;
        private const int MUSIC_VOLUME = CAREER_BASE + CCAREER_MUSIC_VOLUME;

        // God mode toggle state (used by PauseMenu once the runtime cheat is active).
        // Note: Steam build invincibility is gated by save-name cheat; do not rely on any persisted per-player flags.
        private const int GOD_MODE_ENABLED = CAREER_BASE + CCAREER_GOD_MODE_ENABLED;

        private const int INVERT_Y_P1 = CAREER_BASE + CCAREER_WALKER_INVERT_Y_P1;        // Walker invert Y (P1)
        private const int INVERT_Y_P2 = CAREER_BASE + CCAREER_WALKER_INVERT_Y_P2;        // Walker invert Y (P2)
        private const int INVERT_FLIGHT_Y_P1 = CAREER_BASE + CCAREER_FLIGHT_INVERT_Y_P1; // Flight invert Y (P1)
        private const int INVERT_FLIGHT_Y_P2 = CAREER_BASE + CCAREER_FLIGHT_INVERT_Y_P2; // Flight invert Y (P2)
        private const int VIBRATION_P1 = CAREER_BASE + CCAREER_VIBRATION_P1;              // Controller vibration (P1)
        private const int VIBRATION_P2 = CAREER_BASE + CCAREER_VIBRATION_P2;              // Controller vibration (P2)
        private const int CONTROLLER_CONFIG_P1 = CAREER_BASE + CCAREER_CONTROLLER_CONFIG_P1;
        private const int CONTROLLER_CONFIG_P2 = CAREER_BASE + CCAREER_CONTROLLER_CONFIG_P2;
        private const int GOODIE_COUNT = 300;
        // Retail goodies gallery can surface slot 232 (FMV 33) in addition to 0..231.
        private const int GOODIE_DISPLAYABLE_COUNT = 233;

        // Version stamp: BEA.exe validates only the 16-bit version word at file offset 0.
        public const ushort VERSION_WORD = 0x4BD1;
        public const uint VERSION_STAMP_DWORD_VIEW = 0x00004BD1;

        // Unmapped/reserved regions - bytes we intentionally do not interpret/modify yet.
        // Note: the file tail (options entries + 0x56-byte OptionsTail snapshot) is *not* an unmapped region anymore.
        // See: reverse-engineering/save-file/save-format.md (Region 3).
        private static readonly (string Name, int Start, int End, string Description)[] MYSTERY_REGIONS = new[]
        {
            ("CCareerHeader", 0x0002, 0x0006, "CCareer header dword0 (increments when unlocking goodies; see Cutscene_UnlockGoodie_* in BEA.exe)"),
        };

        // Kill unlock thresholds for goodies
        private static readonly int[][] KILL_THRESHOLDS = new[]
        {
            new[] { 25, 50, 75, 100 },      // Aircraft
            new[] { 100, 200, 300, 400 },   // Vehicles
            new[] { 25, 50 },               // Emplacements (75 appears only in combined unlocks)
            new[] { 40, 80, 160 },          // Infantry
            new[] { 20, 40, 80 }            // Mechs
        };

        // Kill category indices
        public const int KILL_AIRCRAFT = 0;
        public const int KILL_VEHICLES = 1;
        public const int KILL_EMPLACEMENTS = 2;
        public const int KILL_INFANTRY = 3;
        public const int KILL_MECHS = 4;

        private const uint LINK_COMPLETE = 1;

        // Goodie states (true dword view)
        private const uint GOODIE_INSTRUCTIONS = 1;
        private const uint GOODIE_NEW = 2;
        private const uint GOODIE_OLD = 3;

        // Node ranking float bits (true dword view, raw IEEE-754 at node+0x3C)
        private static readonly Dictionary<string, uint> RANK_FLOAT_BITS = new()
        {
            { "S", 0x3F800000 },    // 1.0
            { "A", 0x3F4CCCCD },    // 0.8
            { "B", 0x3F19999A },    // 0.6
            { "C", 0x3EB33333 },    // 0.35
            { "D", 0x3E19999A },    // 0.15
            { "E", 0x00000000 },    // 0.0
            { "NONE", 0xBF800000 }, // -1.0 (never completed)
        };

        // Patch configuration
        // NOTE (Steam build): global options are primarily sourced from defaultoptions.bea at boot.
        // CCareer::Load(flag=1) preserves Sound/Music volumes from pre-load state and skips applying
        // options entries + tail snapshot (keybinds/mouse sensitivity/screen shape/etc).
        public bool UseNewGoodiesInstead { get; set; } = false;
        public int GlobalKillCount { get; set; } = 100;
        public string Rank { get; set; } = "S";

        // Per-level rank overrides (node index -> rank string)
        public Dictionary<int, string>? LevelRanks { get; set; } = null;

        // Per-category kill count overrides (category index -> kill count)
        // Use KILL_AIRCRAFT, KILL_VEHICLES, etc. as keys
        public Dictionary<int, int>? PerCategoryKills { get; set; } = null;

        // Optional CCareer settings overrides (true dword view).
        // Null means "preserve existing save value".
        public float? SoundVolumeOverride { get; set; } = null;
        public float? MusicVolumeOverride { get; set; } = null;
        public bool? InvertYAxisP1Override { get; set; } = null;
        public bool? InvertYAxisP2Override { get; set; } = null;
        public bool? InvertFlightP1Override { get; set; } = null;
        public bool? InvertFlightP2Override { get; set; } = null;
        public bool? VibrationP1Override { get; set; } = null;
        public bool? VibrationP2Override { get; set; } = null;
        public uint? ControllerConfigP1Override { get; set; } = null;
        public uint? ControllerConfigP2Override { get; set; } = null;

        // Options entries + tail snapshot (control bindings + global options snapshot).
        // NOTE (Steam build): Loading a career .bes save (CCareer::Load(flag=1)) does NOT apply these
        // to runtime globals. Boot loads defaultoptions.bea (flag=0) which applies them.
        public string? CopyOptionsFromPath { get; set; } = null;
        public bool CopyOptionsEntries { get; set; } = true;
        public bool CopyOptionsTail { get; set; } = true;
        public Dictionary<int, OptionsEntryOverride>? OptionsEntryOverrides { get; set; } = null;

        // Selective patching flags (Dec 2025)
        // By default, all sections are patched. Set to false to skip specific sections.
        public bool PatchNodes { get; set; } = true;
        public bool PatchLinks { get; set; } = true;
        public bool PatchGoodies { get; set; } = true;
        public bool PatchKills { get; set; } = true;

        /// <summary>
        /// Convenience property: when true, only patch kills (equivalent to NoNodes + NoLinks + NoGoodies)
        /// </summary>
        public bool KillsOnly
        {
            get => !PatchNodes && !PatchLinks && !PatchGoodies && PatchKills;
            set
            {
                if (value)
                {
                    PatchNodes = false;
                    PatchLinks = false;
                    PatchGoodies = false;
                    PatchKills = true;
                }
                else
                {
                    PatchNodes = true;
                    PatchLinks = true;
                    PatchGoodies = true;
                    PatchKills = true;
                }
            }
        }

        // Note: RankingScore and EnableAllObjectives were removed - they don't affect gameplay
        // The displayed grade is calculated at runtime from EndLevelData, not from save file

        /// <summary>
        /// Validate that a file is the correct size for a .bes career save.
        /// </summary>
        public static bool IsValidBesFile(string path)
        {
            try
            {
                var info = new FileInfo(path);
                if (!info.Exists || info.Length != EXPECTED_FILE_SIZE)
                    return false;

                using var stream = File.OpenRead(path);
                Span<byte> header = stackalloc byte[4];
                if (stream.Read(header) != 4)
                    return false;
                ushort versionWord = BinaryPrimitives.ReadUInt16LittleEndian(header);
                return versionWord == VERSION_WORD;
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"IsValidBesFile check failed: {ex.Message}");
                return false;
            }
        }

        public PatchResult PatchFile(string inputPath, string outputPath)
        {
            try
            {
                if (string.Equals(Path.GetFullPath(inputPath), Path.GetFullPath(outputPath), StringComparison.OrdinalIgnoreCase))
                {
                    return PatchResult.Fail("Refusing to patch in place. Please choose a different output path.");
                }

                byte[] buf = File.ReadAllBytes(inputPath);

                // Validate file size (strict check)
                if (buf.Length != EXPECTED_FILE_SIZE)
                {
                    return PatchResult.Fail($"Invalid .bes file. Expected {EXPECTED_FILE_SIZE} bytes, got {buf.Length}. " +
                           "This may not be a valid Battle Engine Aquila career save file.");
                }

                ushort versionWord = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(0, 2));
                if (versionWord != VERSION_WORD)
                {
                    uint headerDword = ReadUInt32(buf, 0x0000);
                    return PatchResult.Fail($"Invalid .bes version word. Expected 0x{VERSION_WORD:X4}, got 0x{versionWord:X4} (header dword view 0x{headerDword:X8}).");
                }

                // NOTE (Feb 2026): Don't write to legacy aligned offsets like 0x22D4.
                // In true dword view, mCareerInProgress is at 0x248A (CCareer offset 0x2488).
                // The save works without setting mCareerInProgress.

                // NOTE: God mode patching removed (Dec 2025) - none of the encodings worked
                // See reverse-engineering/game-mechanics/god-mode.md for details on tested values

                // --- nodes (selective patching) ---
                if (PatchNodes)
                {
                    for (int n = 0; n < NODE_COUNT; n++)
                    {
                        int off = NODE_BASE + n * NODE_SIZE;
                        if (off + NODE_SIZE > buf.Length) break;

                        uint world = ReadUInt32(buf, off + 0x10);
                        if (world == 0)
                        {
                            // Unused node slots in retail saves; avoid touching unknown padding.
                            continue;
                        }

                        // Use per-level rank if specified, otherwise default rank
                        string nodeRank = Rank;
                        if (LevelRanks != null && LevelRanks.TryGetValue(n, out var overrideRank))
                        {
                            nodeRank = overrideRank;
                        }
                        PatchNode(buf, off, n, nodeRank);
                    }
                }

                // --- links (minimal change) (selective patching) ---
                // Link layout (true view): [0]=linkState/type, [4]=toNode (0xFFFFFFFF for unused).
                // Avoid clobbering link types (values like 2 appear in real saves).
                if (PatchLinks)
                {
                    for (int l = 0; l < LINK_COUNT; l++)
                    {
                        int off = LINK_BASE + l * LINK_SIZE;
                        uint current = ReadUInt32(buf, off);
                        uint toNode = ReadUInt32(buf, off + 4);
                        if (toNode == 0xFFFFFFFF)
                            continue;
                        if (current == 0)
                            WriteUInt32(buf, off, LINK_COMPLETE);
                    }
                }

                // --- goodies (true view: raw ints 0/1/2/3) (selective patching) ---
                if (PatchGoodies)
                {
                    uint goodieState = UseNewGoodiesInstead ? GOODIE_NEW : GOODIE_OLD;
                    for (int g = 0; g < GOODIE_COUNT; g++)
                    {
                        if (g >= GOODIE_DISPLAYABLE_COUNT)
                            continue;
                        int off = GOODIE_BASE + g * 4;
                        WriteUInt32(buf, off, goodieState);
                    }
                }

                // --- kills (per-category if specified, otherwise all same) (selective patching) ---
                if (PatchKills)
                {
                    SetKillCounts(buf, GlobalKillCount, PerCategoryKills);
                }

                // --- CCareer settings overrides (only if explicitly set) ---
                ApplyCareerSettingsOverrides(buf);

                // --- Options entries + tail snapshot (optional raw copy) ---
                ApplyOptionsCopy(buf);

                // --- Options entry overrides (keybind edits) ---
                ApplyOptionsEntryOverrides(buf);

                File.WriteAllBytes(outputPath, buf);
                return PatchResult.Ok($"Successfully patched: {outputPath}");
            }
            catch (Exception ex)
            {
                return PatchResult.Fail(ex.Message);
            }
        }

        // ---------- helpers ----------
        private static void WriteUInt32(byte[] buf, int offset, uint val) =>
            BinaryPrimitives.WriteUInt32LittleEndian(buf.AsSpan(offset, 4), val);

        private static void WriteFloat32(byte[] buf, int offset, float val)
        {
            uint bits = unchecked((uint)BitConverter.SingleToInt32Bits(val));
            WriteUInt32(buf, offset, bits);
        }

        /// <summary>
        /// Read a UInt32 value from the buffer at the specified offset
        /// </summary>
        private static uint ReadUInt32(byte[] buf, int offset) =>
            BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(offset, 4));

        private static float ReadFloat32(byte[] buf, int offset) =>
            BitConverter.Int32BitsToSingle(unchecked((int)ReadUInt32(buf, offset)));

        private static (int EntryCount, int TailStart, int EntriesSize, int TailSize) ComputeOptionsLayout(int fileSize)
        {
            const int optionsStart = 0x24BE;
            const int tailSize = 0x56;
            const int entrySize = 0x20;
            const int baseSize = optionsStart + tailSize; // 0x2514

            if (fileSize < baseSize)
                throw new InvalidDataException($"File too small for options layout: 0x{fileSize:X} (< 0x{baseSize:X}).");

            int extra = fileSize - baseSize;
            if (extra % entrySize != 0)
                throw new InvalidDataException(
                    $"Invalid options layout: fileSize=0x{fileSize:X} is not 0x{baseSize:X} + 0x{entrySize:X}*N.");

            int n = extra / entrySize;
            int entriesSize = n * entrySize;
            int tailStart = optionsStart + entriesSize;
            return (n, tailStart, entriesSize, tailSize);
        }

        private void ApplyOptionsCopy(byte[] destBuf)
        {
            if (!CopyOptionsEntries && !CopyOptionsTail)
                return;

            if (string.IsNullOrWhiteSpace(CopyOptionsFromPath))
                return;

            byte[] srcBuf = File.ReadAllBytes(CopyOptionsFromPath);
            if (srcBuf.Length != destBuf.Length)
                throw new InvalidDataException(
                    $"Options copy requires matching file sizes. Source={srcBuf.Length:N0} bytes, Dest={destBuf.Length:N0} bytes.");

            var (nDest, tailStartDest, entriesSizeDest, tailSizeDest) = ComputeOptionsLayout(destBuf.Length);
            var (nSrc, tailStartSrc, entriesSizeSrc, tailSizeSrc) = ComputeOptionsLayout(srcBuf.Length);

            if (nSrc != nDest || tailStartSrc != tailStartDest || entriesSizeSrc != entriesSizeDest || tailSizeSrc != tailSizeDest)
                throw new InvalidDataException(
                    $"Options copy requires matching options layout. Source entries={nSrc}, Dest entries={nDest}.");

            const int optionsStart = 0x24BE;
            if (CopyOptionsEntries)
                Array.Copy(srcBuf, optionsStart, destBuf, optionsStart, entriesSizeDest);
            if (CopyOptionsTail)
                Array.Copy(srcBuf, tailStartDest, destBuf, tailStartDest, destBuf.Length - tailStartDest);
        }

        private void ApplyOptionsEntryOverrides(byte[] buf)
        {
            if (OptionsEntryOverrides == null || OptionsEntryOverrides.Count == 0)
                return;

            var (n, tailStart, _entriesSize, _tailSize) = ComputeOptionsLayout(buf.Length);
            const int optionsStart = 0x24BE;
            const int entrySize = 0x20;

            // Build entry_id -> entry offset map for this file.
            var entryOffsets = new Dictionary<int, int>();
            for (int i = 0; i < n; i++)
            {
                int off = optionsStart + entrySize * i;
                int entryId = BinaryPrimitives.ReadInt32LittleEndian(buf.AsSpan(off + 0x04, 4));
                entryOffsets[entryId] = off;
            }

            ushort schemeIndex = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(tailStart + 0x08, 2));

            // Steam build nuance:
            // - schemeIndex == 0: "Custom"
            // - schemeIndex == 1: "Preset"
            // For retail saves observed on this project, slot0/slot1 map directly to P1/P2 in both modes.
            if (schemeIndex != 0 && schemeIndex != 1)
            {
                throw new InvalidDataException(
                    $"Options entry overrides only support ControlSchemeIndex 0 (Custom) or 1 (Preset). Found: {schemeIndex}.");
            }

            void applyToOne(int entryId, OptionsEntryOverride ov)
            {
                if (!entryOffsets.TryGetValue(entryId, out int off))
                    throw new InvalidDataException($"Options entry_id 0x{entryId:X} not found in file.");

                // Ensure entry is active if we override it.
                uint flags = ReadUInt32(buf, off + 0x00);
                flags = (flags & 0xFFFFFF00u) | 1u;
                WriteUInt32(buf, off + 0x00, flags);

                if (ov.Slot0.DeviceCode.HasValue) WriteUInt32(buf, off + 0x0C, ov.Slot0.DeviceCode.Value);
                if (ov.Slot0.PackedKey.HasValue) WriteUInt32(buf, off + 0x10, ov.Slot0.PackedKey.Value);
                if (ov.Slot1.DeviceCode.HasValue) WriteUInt32(buf, off + 0x18, ov.Slot1.DeviceCode.Value);
                if (ov.Slot1.PackedKey.HasValue) WriteUInt32(buf, off + 0x1C, ov.Slot1.PackedKey.Value);
            }

            // Steam build: action_code 0x48 ("Others: Fire weapon") remaps both entry_id 0x12 and 0x13.
            // If we override either, keep them in sync unless the caller explicitly provides both.
            bool has12 = OptionsEntryOverrides.ContainsKey(0x12);
            bool has13 = OptionsEntryOverrides.ContainsKey(0x13);

            foreach (var (entryId, ov) in OptionsEntryOverrides)
            {
                applyToOne(entryId, ov);
                if (entryId == 0x12 && !has13)
                    applyToOne(0x13, ov);
                else if (entryId == 0x13 && !has12)
                    applyToOne(0x12, ov);
            }

            // Force "Custom" scheme when patching bindings so the two slots map consistently to the in-game columns.
            BinaryPrimitives.WriteUInt16LittleEndian(buf.AsSpan(tailStart + 0x08, 2), 0);
        }

        private static readonly Dictionary<string, (uint Vk, uint Scan)> KEY_NAME_MAP = new(StringComparer.OrdinalIgnoreCase)
        {
            // Arrows (extended: scan|0x80)
            { "Up", (0, 0x00C8) },
            { "Down", (0, 0x00D0) },
            { "Left", (0, 0x00CB) },
            { "Right", (0, 0x00CD) },
            // Common non-printables
            { "Tab", (0, 0x000F) },
            { "Space", ((uint)' ', 0x0039) },
            { "CapsLock", (0, 0x003A) },
            { "LShift", (0, 0x002A) },
            { "RShift", (0, 0x0036) },
            { "RControl", (0, 0x009D) },
            // Punctuation (scan codes are DIK/set-1 compatible)
            { "-", ((uint)'-', 0x000C) },
            { "Minus", ((uint)'-', 0x000C) },
            { "=", ((uint)'=', 0x000D) },
            { "Equals", ((uint)'=', 0x000D) },
            { "+", ((uint)'+', 0x000D) }, // plus shares '=' key; vk differs by shift
        };

        private static readonly Dictionary<char, uint> LETTER_SCAN = new()
        {
            ['A']=0x001E, ['B']=0x0030, ['C']=0x002E, ['D']=0x0020, ['E']=0x0012, ['F']=0x0021, ['G']=0x0022,
            ['H']=0x0023, ['I']=0x0017, ['J']=0x0024, ['K']=0x0025, ['L']=0x0026, ['M']=0x0032, ['N']=0x0031,
            ['O']=0x0018, ['P']=0x0019, ['Q']=0x0010, ['R']=0x0013, ['S']=0x001F, ['T']=0x0014, ['U']=0x0016,
            ['V']=0x002F, ['W']=0x0011, ['X']=0x002D, ['Y']=0x0015, ['Z']=0x002C,
        };

        private static readonly Dictionary<char, uint> DIGIT_SCAN = new()
        {
            ['1']=0x0002, ['2']=0x0003, ['3']=0x0004, ['4']=0x0005, ['5']=0x0006, ['6']=0x0007, ['7']=0x0008,
            ['8']=0x0009, ['9']=0x000A, ['0']=0x000B,
        };

        private static readonly Dictionary<char, uint> NUMPAD_DIGIT_SCAN = new()
        {
            ['7']=0x0047, ['8']=0x0048, ['9']=0x0049,
            ['4']=0x004B, ['5']=0x004C, ['6']=0x004D,
            ['1']=0x004F, ['2']=0x0050, ['3']=0x0051,
            ['0']=0x0052,
        };

        public static bool TryParseKeyboardPackedKey(string? input, out uint packedKey, out string? error)
        {
            packedKey = 0;
            error = null;

            if (string.IsNullOrWhiteSpace(input))
            {
                error = "empty";
                return false;
            }

            string t = input.Trim();
            if (t.Equals("-", StringComparison.OrdinalIgnoreCase) ||
                t.Equals("none", StringComparison.OrdinalIgnoreCase))
            {
                packedKey = 0;
                return true;
            }

            // Allow "Key X" prefix (matches in-game UI style).
            if (t.StartsWith("Key ", StringComparison.OrdinalIgnoreCase))
                t = t[4..].Trim();

            // Allow analyzer fallback format for unknown keyboard tokens:
            // "vk=0x0000 scan=0x0052"
            if (t.StartsWith("vk=0x", StringComparison.OrdinalIgnoreCase))
            {
                string[] parts = t.Split(new[] { ' ', '\t' }, StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length == 2 &&
                    parts[0].StartsWith("vk=0x", StringComparison.OrdinalIgnoreCase) &&
                    parts[1].StartsWith("scan=0x", StringComparison.OrdinalIgnoreCase))
                {
                    string vkHex = parts[0]["vk=0x".Length..];
                    string scanHex = parts[1]["scan=0x".Length..];
                    bool vkOk = uint.TryParse(vkHex, System.Globalization.NumberStyles.HexNumber, null, out uint vkRaw);
                    bool scanOk = uint.TryParse(scanHex, System.Globalization.NumberStyles.HexNumber, null, out uint scanRaw);
                    if (vkOk && scanOk)
                    {
                        packedKey = ((vkRaw & 0xFFFFu) << 16) | (scanRaw & 0xFFFFu);
                        return true;
                    }
                }
            }

            // Numpad shorthand (Num7 / Num 7 / Numpad7)
            string tn = t.Replace(" ", string.Empty, StringComparison.Ordinal);
            if (tn.StartsWith("Num", StringComparison.OrdinalIgnoreCase))
            {
                string rest = tn[3..];
                if (rest.StartsWith("Pad", StringComparison.OrdinalIgnoreCase))
                    rest = rest[3..];
                if (rest.Length == 1 && NUMPAD_DIGIT_SCAN.TryGetValue(rest[0], out uint scan))
                {
                    uint vk = rest[0];
                    packedKey = (vk << 16) | scan;
                    return true;
                }
            }

            // Named keys map
            if (KEY_NAME_MAP.TryGetValue(t, out var kv))
            {
                packedKey = (kv.Vk << 16) | kv.Scan;
                return true;
            }

            // Single printable character
            if (t.Length == 1)
            {
                char c = char.ToUpperInvariant(t[0]);
                if (LETTER_SCAN.TryGetValue(c, out uint scanLetter))
                {
                    packedKey = (((uint)c) << 16) | scanLetter;
                    return true;
                }
                if (DIGIT_SCAN.TryGetValue(c, out uint scanDigit))
                {
                    packedKey = (((uint)c) << 16) | scanDigit;
                    return true;
                }
                // Common punctuation (extend as needed)
                if (c == ';') { packedKey = (((uint)c) << 16) | 0x0027; return true; }
                if (c == '\'') { packedKey = (((uint)c) << 16) | 0x0028; return true; }
                if (c == ',') { packedKey = (((uint)c) << 16) | 0x0033; return true; }
                if (c == '.') { packedKey = (((uint)c) << 16) | 0x0034; return true; }
                if (c == '/') { packedKey = (((uint)c) << 16) | 0x0035; return true; }
                if (c == '\\') { packedKey = (((uint)c) << 16) | 0x002B; return true; }
                if (c == '`') { packedKey = (((uint)c) << 16) | 0x0029; return true; }
            }

            error = $"Unrecognized key '{input}'. Examples: A, Num7, Up, Tab, Space, CapsLock, RShift, RControl, '-', '='.";
            return false;
        }

        public static string FormatBinding(uint deviceCode, uint packedKey, int entryId = 0)
        {
            uint vk = (packedKey >> 16) & 0xFFFF;
            uint scan = packedKey & 0xFFFF;

            // Mouse look axes (Steam preset uses these for Look Up/Down/Left/Right)
            // Observed encoding:
            // - device 11: positive direction, device 12: negative direction
            // - scan: 0 => X axis, 1 => Y axis
            // NOTE: scan=0 => packedKey==0, so deviceCode must be checked before treating packedKey==0 as "unbound".
            if (deviceCode == 11 || deviceCode == 12)
            {
                string axis = scan switch
                {
                    0 => "MouseX",
                    1 => "MouseY",
                    _ => "MouseAxis",
                };
                string dir = deviceCode == 11 ? "+" : "-";
                return axis == "MouseAxis" ? $"Mouse({scan})" : $"{axis}{dir}";
            }

            // Mouse wheel (observed in Steam build for Zoom entries)
            if (deviceCode == 16)
            {
                if (scan == 4) return "MouseWheelDown";
                if (scan == 3) return "MouseWheelUp";
                if (scan == 2) return "MouseRight";
                return $"Mouse({scan})";
            }

            // Mouse buttons (observed in Steam build for "Fire weapon" and related actions)
            // - device 17 + packedKey 0 => left mouse button
            // - device 15 + packedKey 0 => left mouse button (paired entry)
            if ((deviceCode == 17 || deviceCode == 15) && vk == 0 && scan == 0)
                return "MouseLeft";

            if (packedKey == 0)
                return "-";

            // Extended arrows are stored as base scan + 0x80 (0xC8/0xCB/0xCD/0xD0)
            if (vk == 0 && scan == 0x00C8) return "Up";
            if (vk == 0 && scan == 0x00D0) return "Down";
            if (vk == 0 && scan == 0x00CB) return "Left";
            if (vk == 0 && scan == 0x00CD) return "Right";
            if (vk == 0 && scan == 0x0039) return "Space";
            if (vk == 0 && scan == 0x002A) return "LShift";
            if (vk == 0 && scan == 0x0036) return "RShift";
            if (vk == 0 && scan == 0x009D) return "RControl";
            if (vk == 0 && scan == 0x003A) return "CapsLock";
            if (vk == 0 && scan == 0x000F) return "Tab";
            if (vk == 0 && scan == 0x0027) return "Key ;";
            if (vk == 0 && scan == 0x000C) return "Key -";
            if (vk == 0 && scan == 0x000D) return "Key =";

            if (vk == 0)
            {
                foreach (var (digit, s) in NUMPAD_DIGIT_SCAN)
                {
                    if (s == scan)
                        return $"Num {digit}";
                }
            }

            // Numpad digits (scan codes in the 0x47..0x53 region)
            if (vk is >= (uint)'0' and <= (uint)'9')
            {
                char d = (char)vk;
                if (NUMPAD_DIGIT_SCAN.TryGetValue(d, out uint expectedScan) && expectedScan == scan)
                    return $"Num {d}";
            }

            // Printable keys: use vk if it looks like ASCII.
            if (vk >= 0x20 && vk <= 0x7E)
            {
                char c = (char)vk;
                // Match in-game UI style: "Key X" for most printable keys.
                if (c == ' ')
                    return "Space";
                if (scan == 0x000D)
                    return "Key =";
                if (scan == 0x000C)
                    return "Key -";
                if (scan == 0x0027)
                    return "Key ;";
                return $"Key {c}";
            }

            // Fallback to scan-name map when vk is 0.
            foreach (var (name, v) in KEY_NAME_MAP)
            {
                if (v.Vk == vk && v.Scan == scan)
                    return name;
            }

            return $"vk=0x{vk:X4} scan=0x{scan:X4}";
        }

        private void ApplyCareerSettingsOverrides(byte[] buf)
        {
            if (SoundVolumeOverride.HasValue)
            {
                float v = SoundVolumeOverride.Value;
                if (float.IsNaN(v) || float.IsInfinity(v))
                    throw new ArgumentException("Sound volume must be a finite float.");
                v = Math.Clamp(v, 0.0f, 1.0f);
                WriteFloat32(buf, SOUND_VOLUME, v);
            }

            if (MusicVolumeOverride.HasValue)
            {
                float v = MusicVolumeOverride.Value;
                if (float.IsNaN(v) || float.IsInfinity(v))
                    throw new ArgumentException("Music volume must be a finite float.");
                v = Math.Clamp(v, 0.0f, 1.0f);
                WriteFloat32(buf, MUSIC_VOLUME, v);
            }

            if (InvertYAxisP1Override.HasValue)
                WriteUInt32(buf, INVERT_Y_P1, InvertYAxisP1Override.Value ? 1u : 0u);
            if (InvertYAxisP2Override.HasValue)
                WriteUInt32(buf, INVERT_Y_P2, InvertYAxisP2Override.Value ? 1u : 0u);

            if (InvertFlightP1Override.HasValue)
                WriteUInt32(buf, INVERT_FLIGHT_Y_P1, InvertFlightP1Override.Value ? 1u : 0u);
            if (InvertFlightP2Override.HasValue)
                WriteUInt32(buf, INVERT_FLIGHT_Y_P2, InvertFlightP2Override.Value ? 1u : 0u);

            if (VibrationP1Override.HasValue)
                WriteUInt32(buf, VIBRATION_P1, VibrationP1Override.Value ? 1u : 0u);
            if (VibrationP2Override.HasValue)
                WriteUInt32(buf, VIBRATION_P2, VibrationP2Override.Value ? 1u : 0u);

            if (ControllerConfigP1Override.HasValue)
                WriteUInt32(buf, CONTROLLER_CONFIG_P1, ControllerConfigP1Override.Value);
            if (ControllerConfigP2Override.HasValue)
                WriteUInt32(buf, CONTROLLER_CONFIG_P2, ControllerConfigP2Override.Value);
        }

        // NOTE: SetGodMode method removed (Dec 2025)
        // God mode patching doesn't work in console port. Tested encodings:
        // - 0x00010000 (TRUE32), 0x01000000, 0x00000001, 0xFFFFFFFF
        // None had any effect. Likely disabled at runtime or stripped from console port.

        /// <summary>
        /// Set global kill counts for all 5 categories (legacy method for backward compatibility)
        /// </summary>
        public void SetGlobalKills(byte[] buf, int kills)
        {
            SetKillCounts(buf, kills, null);
        }

        /// <summary>
        /// Set kill counts with optional per-category overrides.
        /// Kill categories: 0=Aircraft, 1=Vehicles, 2=Emplacements, 3=Infantry, 4=Mechs
        ///
        /// Validation: Game clamps negative values to 0 (confirmed via Ghidra FUN_00421200)
        /// See: reverse-engineering/executable-analysis.md
        /// Code: "if ((int)in_ECX[0x8fd] &lt; 0) in_ECX[0x8fd] = 0"
        /// </summary>
        public void SetKillCounts(byte[] buf, int defaultKills, Dictionary<int, int>? perCategoryKills)
        {
            for (int k = 0; k < 5; k++)
            {
                int kills = defaultKills;
                if (perCategoryKills != null && perCategoryKills.TryGetValue(k, out var overrideKills))
                {
                    kills = overrideKills;
                }
                // True view encoding: stored_value = (meta << 24) | (kills & 0x00FFFFFF)
                if (kills < 0) kills = 0;
                if (kills > 0x00FFFFFF) kills = 0x00FFFFFF;

                int offset = KILLS_BASE + k * 4;
                uint cur = ReadUInt32(buf, offset);
                uint meta = cur & 0xFF000000;
                uint encoded = meta | ((uint)kills & 0x00FFFFFF);
                WriteUInt32(buf, offset, encoded);
            }
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
        /// Patch a node to mark it as completed with the specified rank display.
        ///
        /// True view node layout (BEA.exe):
        /// - +0x04 mComplete (raw int 0/1)
        /// - +0x38 mNumAttempts (raw int)
        /// - +0x3C mRanking (raw float bits)
        ///
        /// mBaseThingsExists (+0x14 to +0x37): Level-specific data - DO NOT MODIFY.
        /// </summary>
        private void PatchNode(byte[] buf, int off, int nodeIndex, string rank)
        {
            var rankKey = (rank ?? "S").ToUpperInvariant();
            if (!RANK_FLOAT_BITS.TryGetValue(rankKey, out uint rankBits))
                rankBits = RANK_FLOAT_BITS["S"];

            // Do NOT modify +0x00 or +0x14..+0x37 (flags + persistence bits).
            WriteUInt32(buf, off + 0x04, 1);       // complete
            WriteUInt32(buf, off + 0x38, 0);       // attempts
            WriteUInt32(buf, off + 0x3C, rankBits); // float bits

            // DO NOT write to mBaseThingsExists (+0x14 to +0x37)
            // This contains level-specific objective/persistence data
            // Corrupting it causes crashes on certain levels (Evo levels, etc.)
        }

        // ---------- Save Analyzer ----------

        /// <summary>
        /// Decode the rank from the raw float bits at node+0x3C (true dword view).
        /// Returns the grade letter or descriptive string.
        /// </summary>
        private static string DecodeRank(uint rankBits)
        {
            foreach (var kvp in RANK_FLOAT_BITS)
            {
                if (rankBits == kvp.Value)
                    return kvp.Key;
            }

            float floatVal = BitConverter.ToSingle(BitConverter.GetBytes(rankBits), 0);

            // Map float ranges to grades
            if (floatVal >= 0.9f) return $"~S ({floatVal:F2})";
            if (floatVal >= 0.7f) return $"~A ({floatVal:F2})";
            if (floatVal >= 0.5f) return $"~B ({floatVal:F2})";
            if (floatVal >= 0.25f) return $"~C ({floatVal:F2})";
            if (floatVal >= 0.1f) return $"~D ({floatVal:F2})";
            if (floatVal > 0) return $"~D ({floatVal:F2})";  // Very low positive still shows D per testing
            if (floatVal == 0) return "E";  // 0.0f = E-rank (verified Dec 10, 2025)
            if (floatVal < 0) return "NONE";  // -1.0f = unlocked, no grade shown (verified Dec 10, 2025)
            return $"? ({floatVal:F2})";
        }

        /// <summary>
        /// Generate a hex dump string for a byte array.
        /// </summary>
        /// <param name="data">The byte array to dump (data starts at index 0)</param>
        /// <param name="displayStartOffset">The offset to display in output (for showing original file positions)</param>
        /// <param name="bytesPerLine">Number of bytes per line (default: 16)</param>
        private static string HexDump(byte[] data, int displayStartOffset, int bytesPerLine = 16)
        {
            var sb = new StringBuilder();
            for (int dataIndex = 0; dataIndex < data.Length; dataIndex += bytesPerLine)
            {
                int chunkSize = Math.Min(bytesPerLine, data.Length - dataIndex);
                var hexParts = new List<string>();
                var asciiParts = new List<char>();

                for (int i = 0; i < chunkSize; i++)
                {
                    byte b = data[dataIndex + i];
                    hexParts.Add($"{b:X2}");
                    asciiParts.Add(b >= 32 && b < 127 ? (char)b : '.');
                }

                string hex = string.Join(" ", hexParts).PadRight(bytesPerLine * 3);
                string ascii = new string(asciiParts.ToArray());
                int displayOffset = displayStartOffset + dataIndex;
                sb.AppendLine($"  {displayOffset:X4}: {hex}  {ascii}");
            }
            return sb.ToString().TrimEnd();
        }

        /// <summary>
        /// Analyze the unmapped/reserved regions of a save file.
        /// </summary>
        private static List<MysteryRegionData> AnalyzeMysteryRegions(byte[] buf)
        {
            var regions = new List<MysteryRegionData>();

            foreach (var (name, start, end, desc) in MYSTERY_REGIONS)
            {
                var regionData = new MysteryRegionData
                {
                    Name = name,
                    Description = desc,
                    StartOffset = start,
                    EndOffset = end,
                    Data = new byte[end - start]
                };

                // Copy region data
                Array.Copy(buf, start, regionData.Data, 0, end - start);

                // Count non-zero bytes and check for all-FF pattern
                regionData.NonZeroCount = 0;
                regionData.AllFF = true;
                foreach (byte b in regionData.Data)
                {
                    if (b != 0) regionData.NonZeroCount++;
                    if (b != 0xFF) regionData.AllFF = false;
                }

                regions.Add(regionData);
            }

            return regions;
        }

        /// <summary>
        /// Get the next unlock threshold for a kill category, or null if all unlocked.
        /// </summary>
        private static int? GetNextUnlockThreshold(int category, int currentKills)
        {
            if (category < 0 || category >= KILL_THRESHOLDS.Length)
                return null;

            foreach (int threshold in KILL_THRESHOLDS[category])
            {
                if (currentKills < threshold)
                    return threshold;
            }
            return null;
        }

        /// <summary>
        /// Analyze a .bes save file and return detailed information about its contents.
        /// </summary>
        public static SaveAnalysis AnalyzeSave(string filePath)
        {
            var analysis = new SaveAnalysis();
            analysis.FilePath = filePath;
            string fileNameOnly = Path.GetFileName(filePath);
            analysis.IsOptionsFile = string.Equals(Path.GetExtension(filePath), ".bea", StringComparison.OrdinalIgnoreCase) ||
                                     // Backups like "defaultoptions.bea.bak" should still be treated as the global options snapshot.
                                     fileNameOnly.StartsWith("defaultoptions.bea", StringComparison.OrdinalIgnoreCase);

            try
            {
                byte[] buf = File.ReadAllBytes(filePath);
                analysis.FileSize = buf.Length;

                // Validate file size
                if (buf.Length != EXPECTED_FILE_SIZE)
                {
                    analysis.IsValid = false;
                    analysis.ErrorMessage = $"Invalid file size: {buf.Length:N0} bytes (expected {EXPECTED_FILE_SIZE:N0})";
                    return analysis;
                }

                analysis.IsValid = true;

                // Header
                analysis.VersionWord = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(0, 2));
                analysis.VersionStamp = ReadUInt32(buf, 0x0000); // "dword view" of header for debugging
                analysis.VersionValid = analysis.VersionWord == VERSION_WORD;

                // CCareer header dword0 (increments when unlocking goodies via cutscenes; often 0)
                analysis.NewGoodieCountRaw = ReadUInt32(buf, NEW_GOODIE_COUNT);

                // God mode toggle state (cheat-gated; not sufficient by itself)
                analysis.GodModeEnabledRaw = ReadUInt32(buf, GOD_MODE_ENABLED);
                analysis.GodModeEnabledOn = analysis.GodModeEnabledRaw != 0;

                // CCareer settings near end of fixed block
                analysis.CareerInProgressRaw = ReadUInt32(buf, CAREER_IN_PROGRESS);
                analysis.CareerInProgressOn = analysis.CareerInProgressRaw != 0;

                analysis.SoundVolumeBits = ReadUInt32(buf, SOUND_VOLUME);
                analysis.SoundVolume = ReadFloat32(buf, SOUND_VOLUME);
                analysis.MusicVolumeBits = ReadUInt32(buf, MUSIC_VOLUME);
                analysis.MusicVolume = ReadFloat32(buf, MUSIC_VOLUME);

                analysis.InvertYAxisRaw[0] = ReadUInt32(buf, INVERT_Y_P1);
                analysis.InvertYAxisRaw[1] = ReadUInt32(buf, INVERT_Y_P2);
                analysis.InvertFlightRaw[0] = ReadUInt32(buf, INVERT_FLIGHT_Y_P1);
                analysis.InvertFlightRaw[1] = ReadUInt32(buf, INVERT_FLIGHT_Y_P2);
                analysis.VibrationRaw[0] = ReadUInt32(buf, VIBRATION_P1);
                analysis.VibrationRaw[1] = ReadUInt32(buf, VIBRATION_P2);
                analysis.ControllerConfigNum[0] = ReadUInt32(buf, CONTROLLER_CONFIG_P1);
                analysis.ControllerConfigNum[1] = ReadUInt32(buf, CONTROLLER_CONFIG_P2);

                // Options entries + tail snapshot (dynamic count; tail size fixed at 0x56).
                // Total size formula from BEA.exe: 0x2514 + 0x20*N.
                const int optionsStart = 0x24BE;
                const int baseSize = 0x2514;
                const int entrySize = 0x20;
                const int tailSize = 0x56;
                if (buf.Length >= baseSize && (buf.Length - baseSize) % entrySize == 0)
                {
                    int n = (buf.Length - baseSize) / entrySize;
                    int tailStart = optionsStart + entrySize * n;
                    if (tailStart == buf.Length - tailSize)
                    {
                        analysis.OptionsEntryCount = n;
                        analysis.OptionsTailStart = tailStart;
                        analysis.OptionsMouseSensitivityBits = ReadUInt32(buf, tailStart + 0x04);
                        analysis.OptionsMouseSensitivity = ReadFloat32(buf, tailStart + 0x04);
                        analysis.OptionsControlSchemeIndex = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(tailStart + 0x08, 2));
                        analysis.OptionsLanguageIndex = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(tailStart + 0x0A, 2));
                        analysis.OptionsScreenShape = ReadUInt32(buf, tailStart + 0x20);
                        analysis.OptionsD3DDeviceIndex = ReadUInt32(buf, tailStart + 0x28);
                    }
                }

                // Node analysis
                int completedNodes = 0;
                int emptyNodes = 0;
                int partialNodes = 0;

                for (int n = 0; n < NODE_COUNT; n++)
                {
                    int off = NODE_BASE + n * NODE_SIZE;
                    uint world = ReadUInt32(buf, off + 0x10);
                    if (world == 0)
                    {
                        // Unused node slots in retail saves.
                        emptyNodes++;
                        continue;
                    }

                    uint complete = ReadUInt32(buf, off + 0x04);
                    uint rankBits = ReadUInt32(buf, off + 0x3C);
                    bool isComplete = complete != 0;

                    if (isComplete)
                    {
                        completedNodes++;
                        string rank = DecodeRank(rankBits);
                        analysis.CompletedNodeDetails.Add((n, world, rank, rankBits));

                        // Count rank distribution
                        string baseRank = rank.Split(' ')[0].Replace("~", "");
                        if (!analysis.RankDistribution.ContainsKey(baseRank))
                            analysis.RankDistribution[baseRank] = 0;
                        analysis.RankDistribution[baseRank]++;
                    }
                    else
                    {
                        // Used node but not completed
                        partialNodes++;
                    }
                }

                analysis.CompletedNodes = completedNodes;
                analysis.EmptyNodes = emptyNodes;
                analysis.PartialNodes = partialNodes;

                // Link analysis
                int usedLinks = 0;
                int completedLinks = 0;
                for (int l = 0; l < LINK_COUNT; l++)
                {
                    int off = LINK_BASE + l * LINK_SIZE;
                    uint state = ReadUInt32(buf, off);
                    uint toNode = ReadUInt32(buf, off + 4);
                    if (toNode == 0xFFFFFFFF)
                        continue;

                    usedLinks++;
                    if (state != 0)
                        completedLinks++;
                }
                analysis.CompletedLinks = completedLinks;
                analysis.TotalLinks = usedLinks;

                // Goodie analysis
                for (int g = 0; g < GOODIE_COUNT; g++)
                {
                    if (g >= GOODIE_DISPLAYABLE_COUNT)
                    {
                        analysis.GoodiesReserved++;
                        continue;
                    }
                    int off = GOODIE_BASE + g * 4;
                    uint val = ReadUInt32(buf, off);
                    if (val == 0)
                        analysis.GoodiesLocked++;
                    else if (val == GOODIE_INSTRUCTIONS)
                        analysis.GoodiesInstructions++;
                    else if (val == GOODIE_NEW)
                        analysis.GoodiesNew++;
                    else if (val == GOODIE_OLD)
                        analysis.GoodiesOld++;
                    else
                        analysis.GoodiesOther++;
                }

                // Kill counts
                for (int k = 0; k < 5; k++)
                {
                    int off = KILLS_BASE + k * 4;
                    uint raw = ReadUInt32(buf, off);
                    int kills = (int)(raw & 0x00FFFFFF);
                    analysis.KillMeta[k] = (byte)(raw >> 24);
                    analysis.KillCounts[k] = kills;
                    analysis.NextUnlockThresholds[k] = GetNextUnlockThreshold(k, kills);
                }

                // Tech slots
                analysis.TotalTechSlots = TECH_SLOTS_COUNT;
                analysis.TechSlotsRaw = new uint[TECH_SLOTS_COUNT];
                int activeSlots = 0;
                for (int slot = 0; slot < TECH_SLOTS_COUNT; slot++)
                {
                    int off = TECH_SLOTS_BASE + slot * 4;
                    uint val = ReadUInt32(buf, off);
                    analysis.TechSlotsRaw[slot] = val;
                    if (val != 0)
                        activeSlots++;
                }
                analysis.ActiveTechSlots = activeSlots;

                // Unmapped/reserved regions
                analysis.MysteryRegions = AnalyzeMysteryRegions(buf);

                return analysis;
            }
            catch (Exception ex)
            {
                analysis.IsValid = false;
                analysis.ErrorMessage = ex.Message;
                return analysis;
            }
        }

        /// <summary>
        /// Results from comparing two .bes save files
        /// </summary>
        public class CompareResult
        {
            public string File1Name { get; set; } = "";
            public string File2Name { get; set; } = "";
            public int File1Size { get; set; }
            public int File2Size { get; set; }
            public bool SameSize => File1Size == File2Size;
            public int DifferingBytes { get; set; }
            public Dictionary<string, int> RegionCounts { get; set; } = new();
            public List<(int Start, int End)> DiffRanges { get; set; } = new();
            public string? ErrorMessage { get; set; }
        }

        /// <summary>
        /// Map an offset to a known region name (CORRECTED Dec 2025).
        /// </summary>
        private static string GetRegionName(int offset)
        {
            // Header (version word + 4 bytes of CCareer header dword)
            if (offset < CAREER_BASE)
                return "VersionWord";
            if (offset < NODE_BASE)
                return "CCareerHeader";

            // Fixed-size CCareer block (0x24BC bytes copied to/from dest+2/source+2)
            if (offset < LINK_BASE)
            {
                int node = (offset - NODE_BASE) / NODE_SIZE;
                int fieldOff = (offset - NODE_BASE) % NODE_SIZE;
                return $"Node[{node}]+0x{fieldOff:X2}";
            }
            if (offset < GOODIE_BASE)
            {
                int link = (offset - LINK_BASE) / LINK_SIZE;
                return $"Link[{link}]";
            }
            if (offset < KILLS_BASE)
            {
                int goodie = (offset - GOODIE_BASE) / 4;
                return $"Goodie[{goodie}]";
            }
            if (offset < TECH_SLOTS_BASE)
            {
                int kill = (offset - KILLS_BASE) / 4;
                string[] cats = { "Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs" };
                return $"Kills[{(kill < 5 ? cats[kill] : kill.ToString())}]";
            }
            if (offset < CAREER_BASE + 0x2488) // Tech slots: CCareer 0x2408..0x2487
            {
                int slot = (offset - TECH_SLOTS_BASE) / 4;
                return $"TechSlot[{slot}]";
            }
            if (offset < CAREER_BASE + 0x2498) // CCareer 0x2488..0x2497 (career in progress + audio + god mode enabled)
                return "ProgressSettings";
            if (offset < CAREER_BASE + 0x24BC) // CCareer 0x2498..0x24BB (control flags/config/pending goodies)
                return "CareerSettings2";

            // Options entries + tail snapshot (dynamic count; tail size fixed at 0x56)
            int tailStart = EXPECTED_FILE_SIZE - 0x56;
            if (offset < tailStart)
                return "OptionsEntries";
            return "OptionsTail";
        }

        /// <summary>
        /// Simplify region name for counting (e.g., "Node[0]+0x00" -> "Nodes")
        /// </summary>
        private static string SimplifyRegionName(string region)
        {
            if (region.StartsWith("Node[")) return "Nodes";
            if (region.StartsWith("Link[")) return "Links";
            if (region.StartsWith("Goodie[")) return "Goodies";
            if (region.StartsWith("Kills[")) return "Kills";
            if (region.StartsWith("TechSlot[")) return "TechSlots";
            if (region.StartsWith("GodMode")) return "GodMode";
            return region;
        }

        /// <summary>
        /// Compare two .bes files and return detailed differences.
        /// </summary>
        public static CompareResult CompareFiles(string file1Path, string file2Path)
        {
            var result = new CompareResult
            {
                File1Name = Path.GetFileName(file1Path),
                File2Name = Path.GetFileName(file2Path)
            };

            try
            {
                byte[] buf1 = File.ReadAllBytes(file1Path);
                byte[] buf2 = File.ReadAllBytes(file2Path);

                result.File1Size = buf1.Length;
                result.File2Size = buf2.Length;

                int minLen = Math.Min(buf1.Length, buf2.Length);

                // Find all differences
                var diffs = new List<int>();
                for (int i = 0; i < minLen; i++)
                {
                    if (buf1[i] != buf2[i])
                        diffs.Add(i);
                }

                result.DifferingBytes = diffs.Count;

                if (diffs.Count == 0)
                    return result;

                // Group consecutive differences into ranges
                int start = diffs[0];
                int end = diffs[0];
                foreach (int offset in diffs.Skip(1))
                {
                    if (offset == end + 1)
                    {
                        end = offset;
                    }
                    else
                    {
                        result.DiffRanges.Add((start, end + 1));
                        start = offset;
                        end = offset;
                    }
                }
                result.DiffRanges.Add((start, end + 1));

                // Count diffs per region
                foreach (int offset in diffs)
                {
                    string region = SimplifyRegionName(GetRegionName(offset));
                    if (!result.RegionCounts.ContainsKey(region))
                        result.RegionCounts[region] = 0;
                    result.RegionCounts[region]++;
                }

                return result;
            }
            catch (Exception ex)
            {
                result.ErrorMessage = ex.Message;
                return result;
            }
        }

        /// <summary>
        /// Format compare results as a readable string report.
        /// </summary>
        public static string FormatCompareReport(CompareResult result, string file1Path, string file2Path)
        {
            var sb = new StringBuilder();

            sb.AppendLine("============================================================");
            sb.AppendLine("  FILE COMPARISON");
            sb.AppendLine("============================================================");
            sb.AppendLine();

            if (result.ErrorMessage != null)
            {
                sb.AppendLine($"  ERROR: {result.ErrorMessage}");
                return sb.ToString();
            }

            sb.AppendLine($"  File 1: {result.File1Name} ({result.File1Size:N0} bytes)");
            sb.AppendLine($"  File 2: {result.File2Name} ({result.File2Size:N0} bytes)");
            sb.AppendLine();

            if (!result.SameSize)
            {
                sb.AppendLine("  WARNING: Files are different sizes!");
            }
            else
            {
                sb.AppendLine($"  Files are same size: {result.File1Size:N0} bytes");
            }

            sb.AppendLine($"  Total differing bytes: {result.DifferingBytes}");
            sb.AppendLine($"  Difference ranges: {result.DiffRanges.Count}");

            if (result.DifferingBytes == 0)
            {
                sb.AppendLine();
                sb.AppendLine("  Files are identical!");
            }
            else
            {
                sb.AppendLine();
                sb.AppendLine("------------------------------------------------------------");
                sb.AppendLine("DIFFERENCES BY REGION:");
                sb.AppendLine("------------------------------------------------------------");

                foreach (var kvp in result.RegionCounts.OrderByDescending(x => x.Value))
                {
                    sb.AppendLine($"  {kvp.Key,-20}: {kvp.Value,5} bytes differ");
                }

                // Show detailed hex for unmapped/reserved regions
                try
                {
                    byte[] buf1 = File.ReadAllBytes(file1Path);
                    byte[] buf2 = File.ReadAllBytes(file2Path);

                    sb.AppendLine();
                    sb.AppendLine("------------------------------------------------------------");
                    sb.AppendLine("UNMAPPED / RESERVED REGION DETAILS:");
                    sb.AppendLine("------------------------------------------------------------");

                    foreach (var (name, start, end, desc) in MYSTERY_REGIONS)
                    {
                        var regionDiffs = new List<int>();
                        for (int i = start; i < end && i < buf1.Length && i < buf2.Length; i++)
                        {
                            if (buf1[i] != buf2[i])
                                regionDiffs.Add(i);
                        }

                        if (regionDiffs.Count > 0)
                        {
                            sb.AppendLine();
                            sb.AppendLine($"  {name} ({desc}): {regionDiffs.Count} bytes differ");
                            sb.AppendLine();

                            // Show side-by-side hex for first 64 bytes of differences
                            int showStart = regionDiffs[0];
                            int showEnd = Math.Min(showStart + 64, end);

                            sb.AppendLine("  Offset    File1                               File2");
                            sb.AppendLine("  ------    -----                               -----");

                            for (int off = showStart; off < showEnd; off += 8)
                            {
                                int chunkEnd = Math.Min(off + 8, showEnd);
                                var hex1Parts = new List<string>();
                                var hex2Parts = new List<string>();
                                bool differs = false;

                                for (int i = off; i < chunkEnd; i++)
                                {
                                    hex1Parts.Add($"{buf1[i]:X2}");
                                    hex2Parts.Add($"{buf2[i]:X2}");
                                    if (buf1[i] != buf2[i]) differs = true;
                                }

                                string hex1 = string.Join(" ", hex1Parts).PadRight(24);
                                string hex2 = string.Join(" ", hex2Parts).PadRight(24);
                                string marker = differs ? " *" : "";

                                sb.AppendLine($"  0x{off:X4}:   {hex1}      {hex2}{marker}");
                            }
                        }
                        else
                        {
                            sb.AppendLine();
                            sb.AppendLine($"  {name}: No differences");
                        }
                    }
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"Hex dump read failed: {ex.Message}");
                }
            }

            sb.AppendLine();
            sb.AppendLine("============================================================");

            return sb.ToString();
        }

        /// <summary>
        /// Format the analysis results as a readable string report.
        /// </summary>
        public static string FormatAnalysisReport(SaveAnalysis analysis, bool verbose = false, bool dumpMystery = false)
        {
            var sb = new StringBuilder();

            sb.AppendLine("============================================================");
            sb.AppendLine("  SAVE FILE ANALYSIS");
            if (!string.IsNullOrWhiteSpace(analysis.FilePath))
            {
                sb.AppendLine($"  File: {Path.GetFileName(analysis.FilePath)}");
            }
            sb.AppendLine("============================================================");
            sb.AppendLine();

            // File validation
            sb.AppendLine("FILE VALIDATION");
            sb.AppendLine("----------------------------------------");
            sb.AppendLine($"  File size: {analysis.FileSize:N0} bytes {(analysis.FileSize == EXPECTED_FILE_SIZE ? "[OK]" : "[BAD]")}");

            if (!analysis.IsValid)
            {
                sb.AppendLine($"  ERROR: {analysis.ErrorMessage}");
                return sb.ToString();
            }

            sb.AppendLine($"  Version word: 0x{analysis.VersionWord:X4} {(analysis.VersionValid ? "[OK]" : "[BAD]")}");
            sb.AppendLine($"  Header dword view @0x0000: 0x{analysis.VersionStamp:X8} (version word + first 2 bytes of CCareer)");
            sb.AppendLine($"  NewGoodieCount: {analysis.NewGoodieCountRaw} (raw=0x{analysis.NewGoodieCountRaw:X8})");
            sb.AppendLine($"  GodModeEnabled: 0x{analysis.GodModeEnabledRaw:X8} ({(analysis.GodModeEnabledOn ? "ON" : "OFF")})");
            sb.AppendLine($"  CareerInProgress: 0x{analysis.CareerInProgressRaw:X8} ({(analysis.CareerInProgressOn ? "YES" : "NO")})");
            sb.AppendLine($"  SoundVolume: {analysis.SoundVolume:F3} (bits=0x{analysis.SoundVolumeBits:X8})");
            sb.AppendLine($"  MusicVolume: {analysis.MusicVolume:F3} (bits=0x{analysis.MusicVolumeBits:X8})");
            if (analysis.IsOptionsFile)
            {
                sb.AppendLine("  NOTE: This is a .bea options file (loaded at boot). These volumes should apply globally after restart.");
            }
            else
            {
                sb.AppendLine("  NOTE (Steam build): When loading a .bes save, the game preserves current Sound/Music volumes (from defaultoptions.bea). These values may not apply on load.");
            }
            string invWalkerP1 = analysis.InvertYAxisRaw[0] != 0 ? "ON" : "OFF";
            string invWalkerP2 = analysis.InvertYAxisRaw[1] != 0 ? "ON" : "OFF";
            string invFlightP1 = analysis.InvertFlightRaw[0] != 0 ? "ON" : "OFF";
            string invFlightP2 = analysis.InvertFlightRaw[1] != 0 ? "ON" : "OFF";
            string vibrationP1 = analysis.VibrationRaw[0] != 0 ? "ON" : "OFF";
            string vibrationP2 = analysis.VibrationRaw[1] != 0 ? "ON" : "OFF";
            sb.AppendLine($"  InvertY (Walker): P1={invWalkerP1} (raw=0x{analysis.InvertYAxisRaw[0]:X8}) P2={invWalkerP2} (raw=0x{analysis.InvertYAxisRaw[1]:X8})");
            sb.AppendLine($"  InvertY (Flight): P1={invFlightP1} (raw=0x{analysis.InvertFlightRaw[0]:X8}) P2={invFlightP2} (raw=0x{analysis.InvertFlightRaw[1]:X8})");
            sb.AppendLine($"  Vibration: P1={vibrationP1} (raw=0x{analysis.VibrationRaw[0]:X8}) P2={vibrationP2} (raw=0x{analysis.VibrationRaw[1]:X8})");
            sb.AppendLine($"  CtrlConfig:  P1={analysis.ControllerConfigNum[0]} P2={analysis.ControllerConfigNum[1]}");
            sb.AppendLine();

            if (analysis.OptionsTailStart != 0)
            {
                sb.AppendLine("OPTIONS (bindings + tail snapshot)");
                sb.AppendLine("----------------------------------------");
                if (analysis.IsOptionsFile)
                {
                    sb.AppendLine("  NOTE: The game loads these entries/tail at boot by loading defaultoptions.bea via CCareer::Load(flag=0).");
                }
                else
                {
                    sb.AppendLine("  NOTE (Steam build): defaultoptions.bea is authoritative at boot for keybinds and most global options.");
                    sb.AppendLine("        CCareer::Load(flag=1) skips applying options entries/tail at runtime; frontend load/save flows may rewrite defaultoptions.bea from loaded/current buffers for the next boot.");
                    sb.AppendLine("        If a .bes keybind/tail patch doesn’t show up in-game, patch defaultoptions.bea and restart.");
                }
                sb.AppendLine($"  Options entries: {analysis.OptionsEntryCount} (tail start 0x{analysis.OptionsTailStart:X4})");
                sb.AppendLine($"  MouseSensitivity: {analysis.OptionsMouseSensitivity:F3} (bits=0x{analysis.OptionsMouseSensitivityBits:X8})");
                sb.AppendLine($"  ControlSchemeIndex: {analysis.OptionsControlSchemeIndex}");
                sb.AppendLine($"  LanguageIndex: {analysis.OptionsLanguageIndex}");
                sb.AppendLine($"  ScreenShape: 0x{analysis.OptionsScreenShape:X8} ({analysis.OptionsScreenShape}) (0=4:3, 1=16:9, 2=1:1)");
                sb.AppendLine($"  D3DDeviceIndex: 0x{analysis.OptionsD3DDeviceIndex:X8} ({analysis.OptionsD3DDeviceIndex})");
                sb.AppendLine();

                // Always show a decoded bindings summary when options entries exist.
                // This is small (~16 lines) and helps users understand what's actually stored in the save/options file.
                if (!string.IsNullOrWhiteSpace(analysis.FilePath))
                {
                    try
                    {
                        byte[] buf = File.ReadAllBytes(analysis.FilePath);
                        const int optionsStart = 0x24BE;
                        const int entrySize = 0x20;
                        int n = analysis.OptionsEntryCount;

                        var entries = new Dictionary<int, (uint S0Dev, uint S0Key, uint S1Dev, uint S1Key)>();
                        for (int i = 0; i < n; i++)
                        {
                            int off = optionsStart + entrySize * i;
                            uint active = ReadUInt32(buf, off + 0x00) & 0xFF;
                            if (active == 0)
                                continue;

                            int entryId = BinaryPrimitives.ReadInt32LittleEndian(buf.AsSpan(off + 0x04, 4));
                            uint s0Dev = ReadUInt32(buf, off + 0x0C);
                            uint s0Key = ReadUInt32(buf, off + 0x10);
                            uint s1Dev = ReadUInt32(buf, off + 0x18);
                            uint s1Key = ReadUInt32(buf, off + 0x1C);
                            entries[entryId] = (s0Dev, s0Key, s1Dev, s1Key);
                        }

                        (int Id, string Name)[] rows =
                        {
                            (0x1F, "Movement: Forward"),
                            (0x20, "Movement: Backward"),
                            (0x1D, "Movement: Left"),
                            (0x1E, "Movement: Right"),
                            (0x1A, "Look: Up"),
                            (0x1C, "Look: Down"),
                            (0x19, "Look: Left"),
                            (0x1B, "Look: Right"),
                            (0x10, "Zoom: In"),
                            (0x11, "Zoom: Out"),
                            (0x12, "Others: Fire weapon (A)"),
                            (0x13, "Others: Fire weapon (B)"),
                            (0x14, "Others: Select weapon"),
                            (0x21, "Others: Transform"),
                            (0x15, "Others: Air brake"),
                            (0x3B, "Others: Special function"),
                        };

                        sb.AppendLine("  Bindings:");
                        string col0 = analysis.OptionsControlSchemeIndex is 0 or 1 ? "P1" : "Slot0";
                        string col1 = analysis.OptionsControlSchemeIndex is 0 or 1 ? "P2" : "Slot1";
                        if (analysis.OptionsControlSchemeIndex == 1)
                        {
                            sb.AppendLine("  NOTE: ControlSchemeIndex=1 preset detected; retail mapping reads slot0/slot1 as P1/P2.");
                        }
                        else if (analysis.OptionsControlSchemeIndex != 0)
                        {
                            sb.AppendLine("  NOTE: ControlSchemeIndex!=0 is a preset/unknown scheme; output shows raw slot0/slot1 (presets may rewrite values).");
                        }
                        foreach (var (id, name) in rows)
                        {
                            if (!entries.TryGetValue(id, out var e))
                                continue;

                            uint aDev = e.S0Dev;
                            uint aKey = e.S0Key;
                            uint bDev = e.S1Dev;
                            uint bKey = e.S1Key;
                            string s0 = FormatBinding(aDev, aKey, id);
                            string s1 = FormatBinding(bDev, bKey, id);
                            sb.AppendLine($"    {name,-26} {col0}={s0,-14} {col1}={s1}");
                        }

                        sb.AppendLine();
                    }
                    catch (Exception ex)
                    {
                        sb.AppendLine($"  (Bindings decode failed: {ex.Message})");
                        sb.AppendLine();
                    }
                }
            }

            // Node analysis
            sb.AppendLine("MISSION NODES (100 slots)");
            sb.AppendLine("----------------------------------------");
            int usedNodes = analysis.CompletedNodes + analysis.PartialNodes;
            sb.AppendLine($"  Used:      {usedNodes} nodes (world != 0)");
            sb.AppendLine($"  Completed: {analysis.CompletedNodes} nodes");
            sb.AppendLine($"  Incomplete:{analysis.PartialNodes} nodes");
            sb.AppendLine($"  Unused:    {analysis.EmptyNodes} nodes (world == 0)");

            if (verbose && analysis.CompletedNodeDetails.Count > 0)
            {
                sb.AppendLine();
                sb.AppendLine("  Completed Nodes:");
                foreach (var (index, world, rank, rankBits) in analysis.CompletedNodeDetails)
                {
                    sb.AppendLine($"    Node {index,2}: world={world,3} rank={rank,-6} (rankBits=0x{rankBits:X8})");
                }
            }
            else if (analysis.RankDistribution.Count > 0)
            {
                sb.Append("  Rank distribution:");
                foreach (var rank in new[] { "S", "A", "B", "C", "D", "E", "NONE", "?" })
                {
                    if (analysis.RankDistribution.TryGetValue(rank, out int count))
                        sb.Append($"  {rank}:{count}");
                }
                sb.AppendLine();
            }
            sb.AppendLine();

            // Link analysis
            sb.AppendLine("LINKS (200 slots)");
            sb.AppendLine("----------------------------------------");
            sb.AppendLine($"  Used:      {analysis.TotalLinks}/{LINK_COUNT}");
            if (analysis.TotalLinks > 0)
                sb.AppendLine($"  Completed: {analysis.CompletedLinks}/{analysis.TotalLinks} (state != 0)");
            else
                sb.AppendLine("  Completed: 0/0");
            sb.AppendLine();

            // Goodie analysis
            int displayableGoodies = GOODIE_DISPLAYABLE_COUNT;
            sb.AppendLine($"GOODIES ({displayableGoodies} displayable, {GOODIE_COUNT - displayableGoodies} reserved)");
            sb.AppendLine("----------------------------------------");
            int unlocked = analysis.GoodiesNew + analysis.GoodiesOld;
            sb.AppendLine($"  Unlocked:  {unlocked}/{displayableGoodies}");
            sb.AppendLine($"    - NEW (gold): {analysis.GoodiesNew}");
            sb.AppendLine($"    - OLD (blue): {analysis.GoodiesOld}");
            if (analysis.GoodiesInstructions > 0)
                sb.AppendLine($"    - Instructions: {analysis.GoodiesInstructions}");
            if (analysis.GoodiesOther > 0)
                sb.AppendLine($"    - Other:      {analysis.GoodiesOther}");
            sb.AppendLine($"  Locked:    {analysis.GoodiesLocked}");
            if (analysis.GoodiesReserved > 0)
                sb.AppendLine($"  Reserved:  {analysis.GoodiesReserved}");
            sb.AppendLine();

            // Kill counts
            sb.AppendLine("KILL COUNTS");
            sb.AppendLine("----------------------------------------");
            string[] categories = { "Aircraft", "Vehicles", "Emplacements", "Infantry", "Mechs" };
            for (int k = 0; k < 5; k++)
            {
                string progress = analysis.NextUnlockThresholds[k].HasValue
                    ? $" (next unlock at {analysis.NextUnlockThresholds[k]})"
                    : " (all unlocked)";

                string metaStr = analysis.KillMeta[k] != 0 ? $" meta=0x{analysis.KillMeta[k]:X2}" : "";
                sb.AppendLine($"  {categories[k],-13}: {analysis.KillCounts[k],6}{metaStr}{progress}");
            }
            sb.AppendLine();

            // Tech slots
            sb.AppendLine("TECH SLOTS (32 slots)");
            sb.AppendLine("------------------------------------------------------------");
            sb.AppendLine($"  Active: {analysis.ActiveTechSlots}/{analysis.TotalTechSlots}");
            if (verbose && analysis.TechSlotsRaw.Length > 0)
            {
                sb.AppendLine();
                sb.AppendLine("  Slot values (bit masks, NOT shift-16):");
                for (int slot = 0; slot < analysis.TechSlotsRaw.Length; slot++)
                {
                    uint val = analysis.TechSlotsRaw[slot];
                    if (val == 0)
                        continue;

                    var setBits = new List<int>();
                    for (int bit = 0; bit < 32; bit++)
                    {
                        if ((val & (1u << bit)) != 0)
                            setBits.Add(bit);
                    }

                    var slotNums = setBits.Select(b => slot * 32 + b).ToList();
                    string bitsStr = string.Join(",", setBits.Take(8));
                    if (setBits.Count > 8)
                        bitsStr += $"...+{setBits.Count - 8} more";
                    string slotsStr = string.Join(",", slotNums.Take(4));
                    if (slotNums.Count > 4)
                        slotsStr += $"...+{slotNums.Count - 4}";

                    sb.AppendLine($"    mSlots[{slot,2}]: 0x{val:X8} bits=[{bitsStr}] -> slots [{slotsStr}]");
                }
            }
            sb.AppendLine();

            // Unmapped/reserved regions (always show summary, hex dump if verbose)
            if (analysis.MysteryRegions.Count > 0)
            {
                int totalMysteryBytes = 0;
                foreach (var region in analysis.MysteryRegions)
                    totalMysteryBytes += region.Size;

                sb.AppendLine($"UNMAPPED / RESERVED REGIONS ({totalMysteryBytes} bytes total)");
                sb.AppendLine("------------------------------------------------------------");

                foreach (var region in analysis.MysteryRegions)
                {
                    sb.AppendLine($"  {region.Name}: 0x{region.StartOffset:X4} - 0x{region.EndOffset:X4} ({region.Size} bytes)");
                    sb.AppendLine($"    {region.Description}");

                    if (region.AllZeros)
                    {
                        sb.AppendLine("    [All zeros]");
                    }
                    else if (region.AllFF)
                    {
                        sb.AppendLine("    [All 0xFF]");
                    }
                    else
                    {
                        double pct = 100.0 * region.NonZeroCount / region.Size;
                        sb.AppendLine($"    Non-zero bytes: {region.NonZeroCount}/{region.Size} ({pct:F1}%)");

                        if (verbose || dumpMystery)
                        {
                            sb.AppendLine();
                            // Pass region.Data directly with display offset for file position labels
                            sb.AppendLine(HexDump(region.Data, region.StartOffset));
                        }
                    }
                    sb.AppendLine();
                }
            }

            sb.AppendLine("============================================================");

            // Build hints for additional options (like Python CLI)
            var hints = new List<string>();
            if (!verbose)
                hints.Add("--verbose for node details");
            if (!dumpMystery && !verbose)
                hints.Add("--dump-mystery for raw unmapped-byte dumps");

            if (hints.Count > 0)
            {
                sb.AppendLine($"  Analysis complete. Use {string.Join(", ", hints)}.");
            }
            else
            {
                sb.AppendLine("  Analysis complete.");
            }
            sb.AppendLine("============================================================");

            return sb.ToString();
        }
    }
}
