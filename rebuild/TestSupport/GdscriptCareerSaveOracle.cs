// SPDX-License-Identifier: GPL-3.0-or-later
using System.Buffers.Binary;
using System.Security.Cryptography;
using OnslaughtRebuild.Core;

/// <summary>Read-only differential oracle. Each case starts from the real,
/// tracked gold container. Mutations are in-memory parser probes only; no save
/// is manufactured, emitted, or written back to an original.</summary>
internal static class GdscriptCareerSaveOracle
{
    internal static object Build(byte[] gold)
    {
        string originalHash = Hash(gold);
        var cases = new List<object>();
        void Case(string name, int? length = null, params (int Offset, int Width, uint Word)[] patches)
        {
            byte[] bytes = gold.ToArray();
            if (length is int size) Array.Resize(ref bytes, size);
            foreach (var patch in patches)
            {
                if (patch.Width == 1) bytes[patch.Offset] = (byte)patch.Word;
                else if (patch.Width == 2) BinaryPrimitives.WriteUInt16LittleEndian(bytes.AsSpan(patch.Offset), (ushort)patch.Word);
                else BinaryPrimitives.WriteUInt32LittleEndian(bytes.AsSpan(patch.Offset), patch.Word);
            }
            object expected;
            try
            {
                RetailCareerSave save = RetailCareerSaveCodec.Read(bytes);
                expected = new { ok = true, value = Snapshot(save),
                    summary = Summary(save),
                    project = new { suggested_world_number = save.SuggestedWorldNumber,
                        selectable_world_numbers = save.SelectableWorldNumbers },
                    bytes_sha256 = Hash(save.ContainerBytes),
                    selection = new[] { int.MinValue, 0, 100, 110, 200, 800, 999, int.MaxValue }
                        .Select(world => new { world, selectable = save.IsWorldSelectable(world) }).ToArray() };
            }
            catch (RetailCareerSaveFormatException error)
            { expected = new { ok = false, error_type = error.GetType().Name, error = error.Message }; }
            cases.Add(new { name, length, patches = patches.Select(p => new { offset = p.Offset, width = p.Width, word = p.Word }).ToArray(), expected });
        }
        Case("gold");
        foreach (int size in new[] { 0, 1, 2, 9999, 10003, 10005 }) Case("length:" + size, size);
        foreach (uint version in new uint[] { 0, 1, 0xffff, 0x4bd0, 0x4bd2 })
            Case("version:" + version, null, (0, 2, version));
        const int nodeBase = 2 + RetailCareerRecordLayout.NodeArrayOffset;
        const int linkBase = 2 + RetailCareerRecordLayout.LinkArrayOffset;
        for (int index = 0; index < RetailWorldCatalog.NodeCount; index++)
        {
            int offset = nodeBase + index * RetailCareerRecordLayout.NodeStride;
            Case("world:" + index, null, (offset + 0x10, 4, 0x7fffffff));
            Case("lower-link:" + index, null, (offset + 8, 4, 0xffffffff));
            Case("higher-link:" + index, null, (offset + 12, 4, 0xffffffff));
            Case("attempts:" + index, null, (offset + 0x38, 4, 0x80000000));
        }
        for (int index = 0; index < RetailWorldCatalog.NodeCount * 2; index++)
        {
            int offset = linkBase + index * RetailCareerRecordLayout.LinkStride;
            Case("link-state:" + index, null, (offset, 4, index % 2 == 0 ? 3u : 0xffffffff));
            Case("link-destination:" + index, null, (offset + 4, 4, 0x7fffffff));
        }
        // Error precedence: links before nodes; state before destination; world
        // before link indices; lower and higher indices are reported together.
        Case("version-before-link", null, (0, 2, 0), (linkBase, 4, 3));
        Case("link-before-node", null, (linkBase + 8, 4, 3), (nodeBase + 0x10, 4, 999));
        Case("state-before-destination", null, (linkBase, 4, 3), (linkBase + 4, 4, 999));
        Case("world-before-indices", null, (nodeBase + 0x10, 4, 999), (nodeBase + 8, 4, 999));
        Case("both-indices", null, (nodeBase + 8, 4, 999), (nodeBase + 12, 4, 998));
        uint[] words = [0, 0x80000000, 1, 0x80000001, 0x3f000000, 0x3f7fffff,
            0x3f800000, 0x3f800001, 0xbf800000, 0x7f7fffff, 0xff7fffff,
            0x7f800000, 0xff800000, 0x7fc00000, 0xffc00001, 0x7f800001];
        foreach (uint ranking in words)
            foreach (uint complete in new uint[] { 0, 1, 2, 0xffffffff, 0x80000000 })
                Case($"ranking:{ranking}:complete:{complete}", null,
                    (nodeBase + 0x3c, 4, ranking), (nodeBase + 4, 4, complete));
        foreach (uint state in new uint[] { 0, 1, 2 })
            Case("incoming-state:" + state, null, (linkBase, 4, state));
        foreach (uint state in new uint[] { 0, 1, 2, 3, 0xffffffff, 0x80000000, 0x7fffffff })
            Case("goodies-and-career:" + state, null,
                (2 + RetailCareerRecordLayout.GoodieArrayOffset, 4, state),
                (2 + RetailCareerRecordLayout.GoodieArrayOffset + 299 * 4, 4, state),
                (2 + RetailCareerRecordLayout.CareerInProgressOffset, 4, state));
        foreach (int offset in new[] { 2, nodeBase + 43 * 64, linkBase + 86 * 8, 0x249a, 10003 })
            Case("unknown-byte:" + offset, null, (offset, 1, (uint)(gold[offset] ^ 0xff)));
        if (Hash(gold) != originalHash) throw new InvalidOperationException("Oracle mutated the supplied fixture.");
        return new { fixture_sha256 = originalHash, cases };
    }

    private static object Snapshot(RetailCareerSave value) => new
    {
        version_word = value.VersionWord, container_length = value.ContainerLength,
        career_in_progress = value.CareerInProgress,
        campaign_nodes = value.CampaignNodes.Select(node => new { index = node.Index,
            world_number = node.WorldNumber, complete = node.Complete, lower_link = node.LowerLink,
            higher_link = node.HigherLink, num_attempts = node.NumAttempts,
            ranking_bits = BitConverter.SingleToUInt32Bits(node.Ranking), grade = node.Grade }).ToArray(),
        completed_world_count = value.CompletedWorldCount, unlocked_goodie_count = value.UnlockedGoodieCount,
        selectable_world_numbers = value.SelectableWorldNumbers, suggested_world_number = value.SuggestedWorldNumber,
    };
    private static object Summary(RetailCareerSave value) => new { career_in_progress = value.CareerInProgress,
        completed_world_count = value.CompletedWorldCount, unlocked_goodie_count = value.UnlockedGoodieCount,
        suggested_world_number = value.SuggestedWorldNumber };
    private static string Hash(ReadOnlySpan<byte> bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
}
