using System.Buffers.Binary;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class BesFilePatcherLinkCensusTests
    {
        private const int LinkTableFileOffset = 0x1906;
        private const int LinkSlotSize = 8;
        private const int LinkSlotCount = 200;
        private const uint UnusedToNode = 0xFFFFFFFF;

        [Fact]
        public void TryReadDisplayableLinkCensus_CountsUsedSlotsAndIgnoresUnused()
        {
            byte[] buffer = CreateUnusedLinkBuffer();
            WriteLink(buffer, 0, state: 0, toNode: 1);
            WriteLink(buffer, 1, state: 1, toNode: 2);
            WriteLink(buffer, 2, state: 2, toNode: 3);
            WriteLink(buffer, 3, state: 99, toNode: 4);
            WriteLink(buffer, 4, state: 1, toNode: UnusedToNode);

            Assert.True(BesFilePatcher.TryReadDisplayableLinkCensus(buffer, out DisplayableLinkCensus census));
            Assert.Equal(4, census.Total);
            Assert.Equal(1, census.StillLocked);
            Assert.Equal(1, census.Complete);
            Assert.Equal(1, census.Broken);
            Assert.Equal(1, census.Unrecognized);
        }

        [Fact]
        public void TryReadDisplayableLinkCensus_TreatsNodeZeroAsUsed()
        {
            byte[] buffer = CreateUnusedLinkBuffer();
            WriteLink(buffer, 0, state: 0, toNode: 0);

            Assert.True(BesFilePatcher.TryReadDisplayableLinkCensus(buffer, out DisplayableLinkCensus census));
            Assert.Equal(1, census.Total);
            Assert.Equal(1, census.StillLocked);
        }

        [Fact]
        public void TryReadDisplayableLinkCensus_RefusesAnInvalidContainer()
        {
            Assert.False(BesFilePatcher.TryReadDisplayableLinkCensus(new byte[8], out DisplayableLinkCensus census));
            Assert.Equal(0, census.Total);
        }

        private static byte[] CreateUnusedLinkBuffer()
        {
            byte[] buffer = new byte[BesFilePatcher.EXPECTED_FILE_SIZE];
            BinaryPrimitives.WriteUInt16LittleEndian(buffer.AsSpan(0, 2), BesFilePatcher.VERSION_WORD);
            for (int index = 0; index < LinkSlotCount; index++)
            {
                WriteLink(buffer, index, state: 0, toNode: UnusedToNode);
            }

            return buffer;
        }

        private static void WriteLink(byte[] buffer, int index, uint state, uint toNode)
        {
            int offset = LinkTableFileOffset + (index * LinkSlotSize);
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.AsSpan(offset, 4), state);
            BinaryPrimitives.WriteUInt32LittleEndian(buffer.AsSpan(offset + 4, 4), toNode);
        }
    }
}
