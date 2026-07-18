using System;
using System.Buffers.Binary;
using System.Collections.Generic;

namespace Onslaught___Career_Editor
{
    public enum MissionScriptGoodieState : uint
    {
        Unknown = 0,
        Instructions = 1,
        New = 2,
        Old = 3
    }

    public readonly record struct MissionScriptGoodieStateVector(
        int ScriptIndex,
        int SaveGoodieIndex,
        int TrueViewDwordOffset,
        int TrueViewDwordEndOffset,
        bool IsDisplayable,
        bool IsReservedPreserve);

    /// <summary>
    /// Clean-room MissionScript SetGoodieState/GetGoodieState codec over the retail
    /// true-view CCareer Goodie storage. This is pure buffer math; it performs no
    /// file I/O and proves no runtime MissionScript behavior.
    /// </summary>
    public static class MissionScriptGoodieStateSaveCodec
    {
        public const int ExpectedFileSize = 10004;
        public const ushort VersionWord = 0x4BD1;
        public const int GoodieBaseOffset = 0x1F46;
        public const int GoodieStorageEntryCount = 300;
        public const int DisplayableGoodieCount = 233;
        public const int ReservedPreserveEntryCount = GoodieStorageEntryCount - DisplayableGoodieCount;
        public const int GoodieStorageBytes = GoodieStorageEntryCount * 4;
        public const int GoodieStorageEndExclusive = GoodieBaseOffset + GoodieStorageBytes;
        public const uint MaxKnownStateValue = (uint)MissionScriptGoodieState.Old;

        public static bool IsValidCareerSaveContainer(ReadOnlySpan<byte> buffer)
        {
            return buffer.Length == ExpectedFileSize
                && BinaryPrimitives.ReadUInt16LittleEndian(buffer.Slice(0, 2)) == VersionWord;
        }

        public static MissionScriptGoodieStateVector GetVectorFromScriptIndex(int scriptIndex)
        {
            if (scriptIndex < 1 || scriptIndex > GoodieStorageEntryCount)
            {
                throw new ArgumentOutOfRangeException(nameof(scriptIndex), scriptIndex, "MissionScript Goodie script index must be in range 1..300.");
            }

            return GetVectorFromSaveIndex(scriptIndex - 1);
        }

        public static MissionScriptGoodieStateVector GetVectorFromSaveIndex(int saveGoodieIndex)
        {
            if ((uint)saveGoodieIndex >= GoodieStorageEntryCount)
            {
                throw new ArgumentOutOfRangeException(nameof(saveGoodieIndex), saveGoodieIndex, "Save Goodie index must be in range 0..299.");
            }

            int offset = GoodieBaseOffset + (saveGoodieIndex * 4);
            bool isDisplayable = saveGoodieIndex < DisplayableGoodieCount;
            return new MissionScriptGoodieStateVector(
                saveGoodieIndex + 1,
                saveGoodieIndex,
                offset,
                offset + 3,
                isDisplayable,
                !isDisplayable);
        }

        public static MissionScriptGoodieStateVector GetDisplayableVectorFromScriptIndex(int scriptIndex)
        {
            MissionScriptGoodieStateVector vector = GetVectorFromScriptIndex(scriptIndex);
            if (!vector.IsDisplayable)
            {
                throw new ArgumentOutOfRangeException(nameof(scriptIndex), scriptIndex, "MissionScript Goodie script index must target displayable Goodie range 1..233 for mutation.");
            }

            return vector;
        }

        public static MissionScriptGoodieState GetStateByScriptIndex(ReadOnlySpan<byte> buffer, int scriptIndex)
        {
            MissionScriptGoodieStateVector vector = GetVectorFromScriptIndex(scriptIndex);
            return GetStateAtVector(buffer, vector);
        }

        public static MissionScriptGoodieState GetStateBySaveIndex(ReadOnlySpan<byte> buffer, int saveGoodieIndex)
        {
            MissionScriptGoodieStateVector vector = GetVectorFromSaveIndex(saveGoodieIndex);
            return GetStateAtVector(buffer, vector);
        }

        public static void SetDisplayableStateByScriptIndex(Span<byte> buffer, int scriptIndex, MissionScriptGoodieState state)
        {
            MissionScriptGoodieStateVector vector = GetDisplayableVectorFromScriptIndex(scriptIndex);
            SetStateAtVector(buffer, vector, state);
        }

        public static void SetDisplayableStateBySaveIndex(Span<byte> buffer, int saveGoodieIndex, MissionScriptGoodieState state)
        {
            if ((uint)saveGoodieIndex >= DisplayableGoodieCount)
            {
                throw new ArgumentOutOfRangeException(nameof(saveGoodieIndex), saveGoodieIndex, "Save Goodie index must target displayable range 0..232 for mutation.");
            }

            MissionScriptGoodieStateVector vector = GetVectorFromSaveIndex(saveGoodieIndex);
            SetStateAtVector(buffer, vector, state);
        }

        public static MissionScriptGoodieStateVector[] SetDisplayableStatesByScriptIndex(
            Span<byte> buffer,
            IReadOnlyDictionary<int, MissionScriptGoodieState> statesByScriptIndex)
        {
            if (statesByScriptIndex is null)
            {
                throw new ArgumentNullException(nameof(statesByScriptIndex));
            }

            ValidateCareerSaveContainer(buffer);
            if (statesByScriptIndex.Count == 0)
            {
                throw new ArgumentException("At least one MissionScript Goodie state override is required.", nameof(statesByScriptIndex));
            }

            MissionScriptGoodieStateVector[] vectors = new MissionScriptGoodieStateVector[statesByScriptIndex.Count];
            int index = 0;
            foreach (var (scriptIndex, state) in statesByScriptIndex)
            {
                MissionScriptGoodieStateVector vector = GetDisplayableVectorFromScriptIndex(scriptIndex);
                ValidateState(state);
                vectors[index++] = vector;
            }

            foreach (var (scriptIndex, state) in statesByScriptIndex)
            {
                MissionScriptGoodieStateVector vector = GetDisplayableVectorFromScriptIndex(scriptIndex);
                BinaryPrimitives.WriteUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4), (uint)state);
            }

            return vectors;
        }

        public static string GetStateLabel(MissionScriptGoodieState state)
        {
            return state switch
            {
                MissionScriptGoodieState.Unknown => "Locked",
                MissionScriptGoodieState.Instructions => "Locked with hint",
                MissionScriptGoodieState.New => "New",
                MissionScriptGoodieState.Old => "Old",
                _ => throw new ArgumentOutOfRangeException(nameof(state), state, "Goodie state must be 0, 1, 2, or 3.")
            };
        }

        private static MissionScriptGoodieState GetStateAtVector(ReadOnlySpan<byte> buffer, MissionScriptGoodieStateVector vector)
        {
            ValidateCareerSaveContainer(buffer);
            uint raw = BinaryPrimitives.ReadUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4));
            if (raw > MaxKnownStateValue)
            {
                throw new ArgumentOutOfRangeException(nameof(buffer), raw, "Goodie state must be 0, 1, 2, or 3.");
            }

            return (MissionScriptGoodieState)raw;
        }

        private static void SetStateAtVector(Span<byte> buffer, MissionScriptGoodieStateVector vector, MissionScriptGoodieState state)
        {
            ValidateCareerSaveContainer(buffer);
            ValidateState(state);
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.Slice(vector.TrueViewDwordOffset, 4), (uint)state);
        }

        private static void ValidateState(MissionScriptGoodieState state)
        {
            if ((uint)state > MaxKnownStateValue)
            {
                throw new ArgumentOutOfRangeException(nameof(state), state, "Goodie state must be 0, 1, 2, or 3.");
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
