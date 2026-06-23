using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.Linq;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class MissionScriptGoodieStateSaveCodecTests
    {
        [Theory]
        [InlineData(1, 0, 0x1F46, true, false)]
        [InlineData(51, 50, 0x200E, true, false)]
        [InlineData(53, 52, 0x2016, true, false)]
        [InlineData(68, 67, 0x2052, true, false)]
        [InlineData(71, 70, 0x205E, true, false)]
        [InlineData(233, 232, 0x22E6, true, false)]
        [InlineData(234, 233, 0x22EA, false, true)]
        [InlineData(300, 299, 0x23F2, false, true)]
        public void GetVectorFromScriptIndex_MatchesStaticGoodieOffsetProof(
            int scriptIndex,
            int saveGoodieIndex,
            int trueViewOffset,
            bool isDisplayable,
            bool isReservedPreserve)
        {
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(scriptIndex);

            Assert.Equal(scriptIndex, vector.ScriptIndex);
            Assert.Equal(saveGoodieIndex, vector.SaveGoodieIndex);
            Assert.Equal(trueViewOffset, vector.TrueViewDwordOffset);
            Assert.Equal(trueViewOffset + 3, vector.TrueViewDwordEndOffset);
            Assert.Equal(isDisplayable, vector.IsDisplayable);
            Assert.Equal(isReservedPreserve, vector.IsReservedPreserve);
        }

        [Theory]
        [InlineData(0, "Locked")]
        [InlineData(1, "Instructions")]
        [InlineData(2, "New")]
        [InlineData(3, "Old")]
        public void GetStateLabel_MatchesAppCoreGoodieVocabulary(uint rawState, string label)
        {
            Assert.Equal(label, MissionScriptGoodieStateSaveCodec.GetStateLabel((MissionScriptGoodieState)rawState));
        }

        [Fact]
        public void SetDisplayableStatesByScriptIndex_MatchesCopiedBaselineChangedOffsets()
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();

            MissionScriptGoodieStateVector[] vectors = MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(
                buffer,
                new Dictionary<int, MissionScriptGoodieState>
                {
                    [1] = MissionScriptGoodieState.Instructions,
                    [51] = MissionScriptGoodieState.New,
                    [53] = MissionScriptGoodieState.Old,
                    [68] = MissionScriptGoodieState.Instructions,
                    [71] = MissionScriptGoodieState.New,
                    [233] = MissionScriptGoodieState.Old
                });

            Assert.Equal(new[] { 0x1F46, 0x200E, 0x2016, 0x2052, 0x205E, 0x22E6 }, ChangedOffsets(before, buffer));
            Assert.Equal(new[] { 0x1F46, 0x200E, 0x2016, 0x2052, 0x205E, 0x22E6 }, vectors.Select(vector => vector.TrueViewDwordOffset).ToArray());
            Assert.Equal(MissionScriptGoodieState.Instructions, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 1));
            Assert.Equal(MissionScriptGoodieState.New, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 51));
            Assert.Equal(MissionScriptGoodieState.New, MissionScriptGoodieStateSaveCodec.GetStateBySaveIndex(buffer, 50));
            Assert.Equal(MissionScriptGoodieState.Old, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 53));
            Assert.Equal(MissionScriptGoodieState.Instructions, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 68));
            Assert.Equal(MissionScriptGoodieState.New, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 71));
            Assert.Equal(MissionScriptGoodieState.Old, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 233));
            Assert.True(MissionScriptGoodieStateSaveCodec.IsValidCareerSaveContainer(buffer));
        }

        [Fact]
        public void DisplayableSet_IsIdempotentAndUnknownRoundtrips()
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, 71, MissionScriptGoodieState.New);
            byte[] afterSet = buffer.ToArray();

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, 71, MissionScriptGoodieState.New);
            Assert.Empty(ChangedOffsets(afterSet, buffer));

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, 71, MissionScriptGoodieState.Unknown);
            Assert.Empty(ChangedOffsets(before, buffer));
            Assert.Equal(MissionScriptGoodieState.Unknown, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, 71));
        }

        [Fact]
        public void Codec_RejectsInvalidIndicesStatesAndContainers()
        {
            byte[] valid = CreateCodecBuffer();
            byte[] wrongSize = new byte[MissionScriptGoodieStateSaveCodec.ExpectedFileSize - 1];
            byte[] wrongVersion = CreateCodecBuffer();
            BinaryPrimitives.WriteUInt16LittleEndian(wrongVersion.AsSpan(0, 2), 0x1234);

            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(0));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(301));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetVectorFromSaveIndex(-1));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetVectorFromSaveIndex(300));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(234));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateBySaveIndex(valid, 233, MissionScriptGoodieState.Old));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(valid, 1, (MissionScriptGoodieState)4));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(valid, 1, (MissionScriptGoodieState)uint.MaxValue));
            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetStateLabel((MissionScriptGoodieState)4));
            Assert.Throws<ArgumentException>(() => MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(wrongSize, 1));
            Assert.Throws<ArgumentException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(wrongVersion, 1, MissionScriptGoodieState.Old));
            Assert.Throws<ArgumentNullException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(valid, null!));
            Assert.Throws<ArgumentException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(valid, new Dictionary<int, MissionScriptGoodieState>()));
        }

        [Fact]
        public void SetDisplayableStatesByScriptIndex_InvalidMixedBatchLeavesBufferUnchanged()
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();

            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.SetDisplayableStatesByScriptIndex(
                buffer,
                new Dictionary<int, MissionScriptGoodieState>
                {
                    [1] = MissionScriptGoodieState.Old,
                    [234] = MissionScriptGoodieState.New
                }));

            Assert.Empty(ChangedOffsets(before, buffer));
        }

        [Theory]
        [MemberData(nameof(AllDisplayableScriptIndices))]
        public void SetDisplayableState_ForEveryDisplayableScriptIndex_TouchesOnlyExpectedDwordStartAndRoundtrips(int scriptIndex)
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(scriptIndex);

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, scriptIndex, MissionScriptGoodieState.Old);

            byte[] afterSet = buffer.ToArray();
            Assert.Equal(new[] { vector.TrueViewDwordOffset }, ChangedOffsets(before, afterSet));
            Assert.Equal(MissionScriptGoodieState.Old, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, scriptIndex));

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateBySaveIndex(buffer, vector.SaveGoodieIndex, MissionScriptGoodieState.Old);
            Assert.Empty(ChangedOffsets(afterSet, buffer));

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, scriptIndex, MissionScriptGoodieState.Unknown);
            Assert.Empty(ChangedOffsets(before, buffer));
        }

        [Theory]
        [MemberData(nameof(AllStorageScriptIndices))]
        public void GetVectorFromScriptIndex_ForEveryStorageScriptIndex_MatchesTrueViewOffsetAndRange(int scriptIndex)
        {
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(scriptIndex);
            int saveGoodieIndex = scriptIndex - 1;
            int trueViewOffset = MissionScriptGoodieStateSaveCodec.GoodieBaseOffset + saveGoodieIndex * 4;
            bool displayable = saveGoodieIndex < MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount;

            Assert.Equal(scriptIndex, vector.ScriptIndex);
            Assert.Equal(saveGoodieIndex, vector.SaveGoodieIndex);
            Assert.Equal(trueViewOffset, vector.TrueViewDwordOffset);
            Assert.Equal(trueViewOffset + 3, vector.TrueViewDwordEndOffset);
            Assert.Equal(displayable, vector.IsDisplayable);
            Assert.Equal(!displayable, vector.IsReservedPreserve);
        }

        [Theory]
        [MemberData(nameof(AllReservedScriptIndices))]
        public void SetDisplayableState_ForEveryReservedScriptIndex_IsRejectedAndLeavesBufferUnchanged(int scriptIndex)
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();

            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(scriptIndex);

            Assert.True(vector.IsReservedPreserve);
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, scriptIndex, MissionScriptGoodieState.Old));
            Assert.Empty(ChangedOffsets(before, buffer));
        }

        [Theory]
        [MemberData(nameof(DisplayableBoundaryStateMatrix))]
        public void SetDisplayableState_ForBoundaryStateMatrix_RoundtripsAndRestores(int scriptIndex, MissionScriptGoodieState state)
        {
            byte[] buffer = CreateCodecBuffer();
            byte[] before = buffer.ToArray();
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetDisplayableVectorFromScriptIndex(scriptIndex);

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, scriptIndex, state);

            byte[] afterSet = buffer.ToArray();
            int[] changedAfterSet = ChangedOffsets(before, afterSet);
            if (state == MissionScriptGoodieState.Unknown)
            {
                Assert.Empty(changedAfterSet);
            }
            else
            {
                Assert.Equal(new[] { vector.TrueViewDwordOffset }, changedAfterSet);
            }

            Assert.Equal(state, MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, scriptIndex));

            MissionScriptGoodieStateSaveCodec.SetDisplayableStateByScriptIndex(buffer, scriptIndex, MissionScriptGoodieState.Unknown);
            Assert.Empty(ChangedOffsets(before, buffer));
        }

        [Theory]
        [InlineData(1)]
        [InlineData(234)]
        [InlineData(300)]
        public void GetStateByScriptIndex_RejectsRawStateOutsideKnownRange(int scriptIndex)
        {
            byte[] buffer = CreateCodecBuffer();
            MissionScriptGoodieStateVector vector = MissionScriptGoodieStateSaveCodec.GetVectorFromScriptIndex(scriptIndex);
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.AsSpan(vector.TrueViewDwordOffset, 4), 4);

            Assert.Throws<ArgumentOutOfRangeException>(() => MissionScriptGoodieStateSaveCodec.GetStateByScriptIndex(buffer, scriptIndex));
        }

        public static IEnumerable<object[]> AllStorageScriptIndices()
        {
            for (int scriptIndex = 1; scriptIndex <= MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount; scriptIndex++)
            {
                yield return new object[] { scriptIndex };
            }
        }

        public static IEnumerable<object[]> AllDisplayableScriptIndices()
        {
            for (int scriptIndex = 1; scriptIndex <= MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount; scriptIndex++)
            {
                yield return new object[] { scriptIndex };
            }
        }

        public static IEnumerable<object[]> AllReservedScriptIndices()
        {
            for (int scriptIndex = MissionScriptGoodieStateSaveCodec.DisplayableGoodieCount + 1;
                 scriptIndex <= MissionScriptGoodieStateSaveCodec.GoodieStorageEntryCount;
                 scriptIndex++)
            {
                yield return new object[] { scriptIndex };
            }
        }

        public static IEnumerable<object[]> DisplayableBoundaryStateMatrix()
        {
            foreach (int scriptIndex in new[] { 1, 2, 51, 53, 68, 71, 232, 233 })
            {
                foreach (MissionScriptGoodieState state in Enum.GetValues<MissionScriptGoodieState>())
                {
                    yield return new object[] { scriptIndex, state };
                }
            }
        }

        private static byte[] CreateCodecBuffer()
        {
            byte[] buffer = new byte[MissionScriptGoodieStateSaveCodec.ExpectedFileSize];
            BinaryPrimitives.WriteUInt16LittleEndian(buffer.AsSpan(0, 2), MissionScriptGoodieStateSaveCodec.VersionWord);
            return buffer;
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
