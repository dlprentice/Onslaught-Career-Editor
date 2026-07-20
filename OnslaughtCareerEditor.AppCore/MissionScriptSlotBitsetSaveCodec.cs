using System;
using System.Buffers.Binary;

namespace Onslaught___Career_Editor
{
    public readonly record struct MissionScriptSlotBitsetVector(
        int Slot,
        int DwordIndex,
        int BitIndex,
        uint BitMask,
        int TrueViewDwordOffset,
        int LittleEndianByteOffset,
        byte LittleEndianByteMask)
    {
        public int TrueViewDwordEndOffset => TrueViewDwordOffset + 3;
    }

    public readonly record struct MissionScriptSlotBitsetMask(
        int DwordIndex,
        uint Mask,
        int TrueViewDwordOffset,
        int TrueViewDwordEndOffset);

    /// <summary>
    /// MissionScript SetSlot/GetSlot/SetSlotSave bitset codec over the documented retail
    /// true-view CCareer slot storage. This is pure buffer math; it performs no file I/O
    /// and proves no runtime MissionScript behavior.
    /// </summary>
    public static class MissionScriptSlotBitsetSaveCodec
    {
        public const int ExpectedFileSize = 10004;
        public const ushort VersionWord = 0x4BD1;
        public const int CareerSlotsBaseOffset = 0x240A;
        public const int UsedSlotDwords = 8;
        public const int SlotStorageDwords = 32;
        public const int SlotStorageBytes = SlotStorageDwords * 4;
        public const int CareerSlotsEndExclusive = CareerSlotsBaseOffset + SlotStorageBytes;
        public const int SlotCount = UsedSlotDwords * 32;

        public static bool IsValidCareerSaveContainer(ReadOnlySpan<byte> buffer)
        {
            return buffer.Length == ExpectedFileSize
                && BinaryPrimitives.ReadUInt16LittleEndian(buffer.Slice(0, 2)) == VersionWord;
        }

        public static MissionScriptSlotBitsetVector GetVector(int slot)
        {
            ValidateSlot(slot);

            int dwordIndex = slot >> 5;
            int bitIndex = slot & 31;
            uint bitMask = 1u << bitIndex;
            int dwordOffset = CareerSlotsBaseOffset + (dwordIndex * 4);
            int byteOffset = dwordOffset + (bitIndex >> 3);
            byte byteMask = (byte)(1 << (bitIndex & 7));

            return new MissionScriptSlotBitsetVector(
                slot,
                dwordIndex,
                bitIndex,
                bitMask,
                dwordOffset,
                byteOffset,
                byteMask);
        }

        public static MissionScriptSlotBitsetMask BuildSingleDwordMask(ReadOnlySpan<int> slots)
        {
            if (slots.Length == 0)
            {
                throw new ArgumentException("At least one MissionScript slot is required.", nameof(slots));
            }

            MissionScriptSlotBitsetVector first = GetVector(slots[0]);
            uint mask = first.BitMask;
            for (int index = 1; index < slots.Length; index++)
            {
                MissionScriptSlotBitsetVector vector = GetVector(slots[index]);
                if (vector.DwordIndex != first.DwordIndex)
                {
                    throw new ArgumentException("All slots must map to the same saved dword for this mask helper.", nameof(slots));
                }

                mask |= vector.BitMask;
            }

            return new MissionScriptSlotBitsetMask(
                first.DwordIndex,
                mask,
                first.TrueViewDwordOffset,
                first.TrueViewDwordEndOffset);
        }

        public static bool GetSlot(ReadOnlySpan<byte> buffer, int slot)
        {
            ValidateCareerSaveContainer(buffer);
            MissionScriptSlotBitsetVector vector = GetVector(slot);
            uint dword = BinaryPrimitives.ReadUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4));
            return (dword & vector.BitMask) != 0;
        }

        public static void SetSlot(Span<byte> buffer, int slot, bool enabled)
        {
            ValidateCareerSaveContainer(buffer);
            MissionScriptSlotBitsetVector vector = GetVector(slot);
            uint dword = BinaryPrimitives.ReadUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4));
            uint next = enabled ? dword | vector.BitMask : dword & ~vector.BitMask;
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4), next);
        }

        public static MissionScriptSlotBitsetMask SetSlotsInSingleDword(Span<byte> buffer, ReadOnlySpan<int> slots, bool enabled)
        {
            ValidateCareerSaveContainer(buffer);
            MissionScriptSlotBitsetMask mask = BuildSingleDwordMask(slots);
            uint dword = BinaryPrimitives.ReadUInt32LittleEndian(buffer.Slice(mask.TrueViewDwordOffset, 4));
            uint next = enabled ? dword | mask.Mask : dword & ~mask.Mask;
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.Slice(mask.TrueViewDwordOffset, 4), next);
            return mask;
        }

        private static void ValidateSlot(int slot)
        {
            if ((uint)slot >= SlotCount)
            {
                throw new ArgumentOutOfRangeException(nameof(slot), slot, "MissionScript slot must be in range 0..255.");
            }
        }

        private static void ValidateCareerSaveContainer(ReadOnlySpan<byte> buffer)
        {
            if (buffer.Length != ExpectedFileSize)
            {
                throw new ArgumentException($"Expected a {ExpectedFileSize}-byte Battle Engine Aquila career save buffer.", nameof(buffer));
            }

            ushort versionWord = BinaryPrimitives.ReadUInt16LittleEndian(buffer.Slice(0, 2));
            if (versionWord != VersionWord)
            {
                throw new ArgumentException($"Expected BEA save version word 0x{VersionWord:X4}, got 0x{versionWord:X4}.", nameof(buffer));
            }
        }
    }
}
