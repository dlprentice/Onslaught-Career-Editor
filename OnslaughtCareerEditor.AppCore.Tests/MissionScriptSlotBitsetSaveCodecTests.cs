using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.Linq;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class MissionScriptSlotBitsetSaveCodecTests
    {
        [Theory]
        [InlineData(0, 0, 0, 0x00000001u, 0x240A, 0x240A, 0x01)]
        [InlineData(31, 0, 31, 0x80000000u, 0x240A, 0x240D, 0x80)]
        [InlineData(32, 1, 0, 0x00000001u, 0x240E, 0x240E, 0x01)]
        [InlineData(61, 1, 29, 0x20000000u, 0x240E, 0x2411, 0x20)]
        [InlineData(62, 1, 30, 0x40000000u, 0x240E, 0x2411, 0x40)]
        public void GetVector_MatchesStaticMissionScriptSlotProof(
            int slot,
            int dwordIndex,
            int bitIndex,
            uint bitMask,
            int dwordOffset,
            int byteOffset,
            byte byteMask)
        {
            MissionScriptSlotBitsetVector vector = MissionScriptSlotBitsetSaveCodec.GetVector(slot);

            Assert.Equal(dwordIndex, vector.DwordIndex);
            Assert.Equal(bitIndex, vector.BitIndex);
            Assert.Equal(bitMask, vector.BitMask);
            Assert.Equal(dwordOffset, vector.TrueViewDwordOffset);
            Assert.Equal(dwordOffset + 3, vector.TrueViewDwordEndOffset);
            Assert.Equal(byteOffset, vector.LittleEndianByteOffset);
            Assert.Equal(byteMask, vector.LittleEndianByteMask);
        }

        [Fact]
        public void BuildSingleDwordMask_ForSlots61And62_MatchesCopiedFileProof()
        {
            MissionScriptSlotBitsetMask mask = MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(stackalloc int[] { 61, 62 });

            Assert.Equal(1, mask.DwordIndex);
            Assert.Equal(0x60000000u, mask.Mask);
            Assert.Equal(0x240E, mask.TrueViewDwordOffset);
            Assert.Equal(0x2411, mask.TrueViewDwordEndOffset);
        }

        [Fact]
        public void SetSlotsInSingleDword_ForSlots61And62_TouchesOnlyExpectedByteInCleanVector()
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();

            MissionScriptSlotBitsetMask mask = MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(buffer, stackalloc int[] { 61, 62 }, enabled: true);

            uint beforeDword = ReadDword(before, mask.TrueViewDwordOffset);
            uint afterDword = ReadDword(buffer, mask.TrueViewDwordOffset);
            int[] changed = ChangedOffsets(before, buffer);

            Assert.Equal(0u, beforeDword & mask.Mask);
            Assert.Equal(0x60000000u, beforeDword ^ afterDword);
            Assert.Equal(new[] { 0x2411 }, changed);
            Assert.True(MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, 61));
            Assert.True(MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, 62));
            Assert.True(MissionScriptSlotBitsetSaveCodec.IsValidCareerSaveContainer(buffer));
        }

        [Fact]
        public void SetSlotsInSingleDword_IsIdempotentAndClearRoundtrips()
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();

            MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(buffer, stackalloc int[] { 61, 62 }, enabled: true);
            byte[] afterSet = buffer.ToArray();

            MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(buffer, stackalloc int[] { 61, 62 }, enabled: true);
            Assert.Empty(ChangedOffsets(afterSet, buffer));

            MissionScriptSlotBitsetSaveCodec.SetSlotsInSingleDword(buffer, stackalloc int[] { 61, 62 }, enabled: false);
            Assert.Empty(ChangedOffsets(before, buffer));
        }

        [Fact]
        public void Codec_RejectsInvalidSlotsAndContainers()
        {
            byte[] valid = CreateCodecBuffer();
            byte[] wrongSize = new byte[MissionScriptSlotBitsetSaveCodec.ExpectedFileSize - 1];
            byte[] wrongVersion = CreateCodecBuffer();
            BinaryPrimitives.WriteUInt16LittleEndian(wrongVersion.AsSpan(0, 2), 0x1234);

            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptSlotBitsetSaveCodec.GetVector(-1));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptSlotBitsetSaveCodec.GetVector(256));
            Assert.Throws<ArgumentException>(() => MissionScriptSlotBitsetSaveCodec.GetSlot(wrongSize, 0));
            Assert.Throws<ArgumentException>(() => MissionScriptSlotBitsetSaveCodec.SetSlot(wrongVersion, 0, enabled: true));
            Assert.Throws<ArgumentException>(() => MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(stackalloc int[] { 31, 32 }));
            Assert.False(MissionScriptSlotBitsetSaveCodec.GetSlot(valid, 61));
        }

        [Theory]
        [MemberData(nameof(BoundarySlotPairsInEachUsedDword))]
        public void BuildSingleDwordMask_ForUsedDwordBoundaryPairs_MatchesExpectedMaskAndRange(
            int firstSlot,
            int lastSlot,
            int expectedDwordIndex,
            uint expectedMask,
            int expectedOffset)
        {
            MissionScriptSlotBitsetMask mask = MissionScriptSlotBitsetSaveCodec.BuildSingleDwordMask(stackalloc int[] { firstSlot, lastSlot });

            Assert.Equal(expectedDwordIndex, mask.DwordIndex);
            Assert.Equal(expectedMask, mask.Mask);
            Assert.Equal(expectedOffset, mask.TrueViewDwordOffset);
            Assert.Equal(expectedOffset + 3, mask.TrueViewDwordEndOffset);
        }

        [Theory]
        [MemberData(nameof(AllValidSlots))]
        public void SetSlot_ForEveryValidSavedSlot_TouchesOnlyExpectedByteAndRoundtrips(int slot)
        {
            AssertSingleSlotRoundTrip(slot);
        }

        public static IEnumerable<object[]> BoundarySlotPairsInEachUsedDword()
        {
            for (int dwordIndex = 0; dwordIndex < MissionScriptSlotBitsetSaveCodec.UsedSlotDwords; dwordIndex++)
            {
                int firstSlot = dwordIndex * 32;
                int lastSlot = firstSlot + 31;
                int offset = MissionScriptSlotBitsetSaveCodec.CareerSlotsBaseOffset + (dwordIndex * 4);
                yield return new object[] { firstSlot, lastSlot, dwordIndex, 0x80000001u, offset };
            }
        }

        public static IEnumerable<object[]> AllValidSlots()
        {
            for (int slot = 0; slot < MissionScriptSlotBitsetSaveCodec.SlotCount; slot++)
            {
                yield return new object[] { slot };
            }
        }

        private static byte[] CreateCodecBuffer()
        {
            byte[] buffer = new byte[MissionScriptSlotBitsetSaveCodec.ExpectedFileSize];
            BinaryPrimitives.WriteUInt16LittleEndian(buffer.AsSpan(0, 2), MissionScriptSlotBitsetSaveCodec.VersionWord);
            return buffer;
        }

        private static void AssertSingleSlotRoundTrip(int slot)
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();
            MissionScriptSlotBitsetVector vector = MissionScriptSlotBitsetSaveCodec.GetVector(slot);

            MissionScriptSlotBitsetSaveCodec.SetSlot(buffer, slot, enabled: true);

            byte[] afterSet = buffer.ToArray();
            int[] changedAfterSet = ChangedOffsets(before, afterSet);
            Assert.Equal(new[] { vector.LittleEndianByteOffset }, changedAfterSet);
            Assert.Equal((byte)(before[vector.LittleEndianByteOffset] ^ vector.LittleEndianByteMask), afterSet[vector.LittleEndianByteOffset]);
            Assert.True(MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, slot));
            Assert.True(MissionScriptSlotBitsetSaveCodec.IsValidCareerSaveContainer(buffer));

            MissionScriptSlotBitsetSaveCodec.SetSlot(buffer, slot, enabled: true);
            Assert.Empty(ChangedOffsets(afterSet, buffer));

            MissionScriptSlotBitsetSaveCodec.SetSlot(buffer, slot, enabled: false);
            Assert.Empty(ChangedOffsets(before, buffer));
            Assert.False(MissionScriptSlotBitsetSaveCodec.GetSlot(buffer, slot));
        }

        private static uint ReadDword(byte[] buffer, int offset)
        {
            return BinaryPrimitives.ReadUInt32LittleEndian(buffer.AsSpan(offset, 4));
        }

        private static int[] ChangedOffsets(byte[] before, byte[] after)
        {
            return before
                .Select((value, index) => value == after[index] ? -1 : index)
                .Where(index => index >= 0)
                .ToArray();
        }
    }
}
