// SPDX-License-Identifier: GPL-3.0-or-later
// Synthetic differential inputs for the existing resident-memory framing owner.
using System;
using System.Collections.Generic;
using System.Linq;
using OnslaughtRebuild.Core;

public static class GdscriptChunkReaderOracle
{
    private readonly record struct Step(string Operation, uint Size = 0, uint Count = 0,
        int Number = 0, int DestinationLength = 0, int Index = 0, byte Byte = 0);

    public static object Build()
    {
        if (!BitConverter.IsLittleEndian)
            throw new PlatformNotSupportedException("The retained C# chunk oracle requires its little-endian host contract.");
        var cases = new List<object>();
        byte[] fixture = Join(Chunk("DATA", 6, [0x10, 0x20, 0x30, 0x40, 0x50, 0x60]), Chunk("TAIL", 2, [0x70, 0x80]));
        void Add(string name, byte[] source, params Step[] steps) => cases.Add(Run(name, source, steps));

        // These sequences retain RetailChunkReaderTests' admitted framing laws.
        Add("two_chunks_exact_end", fixture, new Step("open"), new Step("where"), new Step("get_next"),
            new Step("read", 2, 3, DestinationLength: 6), new Step("skip"), new Step("get_next"),
            new Step("read", 2, 1, DestinationLength: 2), new Step("skip"), new Step("get_next"), new Step("get_next"));
        Add("skip_unread_remainder", fixture, new Step("open"), new Step("get_next"),
            new Step("read", 4, 1, DestinationLength: 4), new Step("skip"), new Step("get_next"));
        Add("release_overread_then_wrapped_skip", fixture, new Step("open"), new Step("get_next"),
            new Step("read", 10, 1, DestinationLength: 10), new Step("skip"), new Step("where"), new Step("get_next"));
        Add("partial_size_from_zero", [0x44, 0x41, 0x54, 0x41, 0xaa, 0xbb],
            new Step("open"), new Step("get_next"), new Step("get_next"));
        Add("partial_size_preserves_high_bytes", Join(Chunk("DATA", 0x12345678, []), [0x54, 0x41, 0x49, 0x4c, 0xaa, 0xbb]),
            new Step("open"), new Step("get_next"), new Step("get_next"), new Step("get_next"));
        Add("adopt_without_rewind", fixture, new Step("open"), new Step("get_next"),
            new Step("read", 6, 1, DestinationLength: 6), new Step("new_reader"), new Step("open"), new Step("get_next"));
        Add("close_twice", fixture, new Step("open"), new Step("close"), new Step("close"));
        Add("short_payload_keeps_destination_tail", Chunk("DATA", 8, [1, 2, 3]), new Step("open"), new Step("get_next"),
            new Step("read", 8, 1, DestinationLength: 12), new Step("read", 0, 1), new Step("skip"), new Step("get_next"));
        Add("zero_chunk_id_is_not_a_new_tag", Chunk("\0\0\0\0", 3, [0x41, 0, 0xff]),
            new Step("open"), new Step("get_next"), new Step("read", 3, 1, DestinationLength: 3));
        Add("uint32_product_and_accounting_wrap", fixture, new Step("open"), new Step("get_next"),
            new Step("read", 0x80000000, 1), new Step("read", 0xffffffff, 1), new Step("read", 0xffffffff, 2),
            new Step("read", 65536, 65536), new Step("read", 0xffffffff, 0xffffffff, DestinationLength: 1), new Step("skip"));
        Add("negative_and_zero_buffer_counts", [1, 2, 3], new Step("buffer_skip", Number: -1),
            new Step("buffer_read", Number: -3, DestinationLength: 4), new Step("buffer_read", Number: 0),
            new Step("buffer_skip", Number: 3), new Step("buffer_read", Number: 0), new Step("buffer_skip", Number: 0),
            new Step("buffer_read", Number: 1, DestinationLength: 1));
        Add("destination_too_small", [1, 2, 3], new Step("buffer_read", Number: 2, DestinationLength: 1));
        Add("eof_precedes_destination_failure", [1, 2, 3], new Step("buffer_read", Number: 7, DestinationLength: 1));
        Add("accounting_precedes_destination_failure", fixture, new Step("open"), new Step("get_next"),
            new Step("read", 6, 1, DestinationLength: 1));
        Add("source_alias_is_not_copied", [1, 2, 3], new Step("mutate_source", Index: 0, Byte: 9),
            new Step("buffer_read", Number: 3, DestinationLength: 3));
        Add("overlapping_copy_uses_memmove", [1, 2, 3, 4, 5], new Step("buffer_skip", Number: 1),
            new Step("buffer_read_alias", Number: 3));
        // Current managed implementation keeps its data after Close. This is a
        // regression boundary, not a new claim about retail null-pointer reads.
        Add("managed_read_after_close", fixture, new Step("open"), new Step("close"), new Step("get_next"), new Step("buffer_close"));
        Add("open_null_resets_counters_before_throw", fixture, new Step("open"), new Step("get_next"),
            new Step("read", 2, 1, DestinationLength: 2), new Step("open_null"));
        foreach (string operation in new[] { "where", "get_next", "read", "skip", "close", "open_null" })
            Add("missing_buffer_" + operation, [], new Step(operation));
        // Pin C# unchecked int32 behavior without calling it a retail pointer
        // contract. These sizes never cause a large allocation in this oracle.
        Add("managed_positive_skip_wrap", [1, 2, 3], new Step("buffer_skip", Number: 1),
            new Step("buffer_skip", Number: int.MaxValue), new Step("buffer_read", Number: 1, DestinationLength: 1));
        Add("managed_span_overflow_failure", fixture, new Step("open"), new Step("get_next"),
            new Step("read", int.MaxValue, 1, DestinationLength: 1));

        // Strings/float words are opaque payload: NUL, high byte, negative zero,
        // subnormal, infinity and a NaN payload survive without native decoding.
        byte[] words = [0x41, 0, 0x42, 0xff, 0, 0, 0, 0x80, 1, 0, 0, 0,
            0, 0, 0x80, 0x7f, 0x34, 0x12, 0xc0, 0x7f];
        Add("opaque_string_and_float_bytes", Chunk("BITS", (uint)words.Length, words), new Step("open"), new Step("get_next"),
            new Step("read", 1, (uint)words.Length, DestinationLength: words.Length + 4), new Step("skip"));
        // Every prefix boundary of the existing small two-chunk fixture.
        for (int length = 0; length <= fixture.Length; length++)
            Add("fixture_prefix_" + length, fixture[..length], new Step("open"), new Step("get_next"),
                new Step("read", 6, 1, DestinationLength: 8), new Step("skip"), new Step("get_next"),
                new Step("read", 2, 1, DestinationLength: 4), new Step("get_next"));
        return new { cases };
    }

    private static object Run(string name, byte[] input, Step[] steps)
    {
        byte[] source = input.ToArray();
        var buffer = new RetailMemBuffer(source);
        var reader = new RetailChunkReader();
        bool attached = false;
        var rows = new List<object>();
        foreach (Step step in steps)
        {
            byte[] destination = step.Operation == "buffer_read_alias" ? source :
                Enumerable.Repeat((byte)0xcc, step.DestinationLength).ToArray();
            string beforeDestination = Hex(destination);
            int beforePosition = buffer.WhereAmI;
            int skipSize = unchecked((int)(reader.Size - reader.ReadSinceChunk));
            object? returned = null;
            string error = "";
            bool complete = true;
            try
            {
                switch (step.Operation)
                {
                    case "open":
                        returned = ReferenceEquals(buffer, reader.OpenExistingBuffer(buffer));
                        attached = true;
                        break;
                    case "open_null": reader.OpenExistingBuffer(null!); break;
                    case "new_reader": reader = new RetailChunkReader(); attached = false; break;
                    case "where": returned = reader.WhereAmI; break;
                    case "get_next":
                        returned = reader.GetNext();
                        complete = beforePosition >= 0 && source.Length - beforePosition >= 8;
                        break;
                    case "read": returned = reader.Read(destination, step.Size, step.Count); complete = (bool)returned; break;
                    case "skip": returned = reader.Skip(); complete = (int)returned == skipSize; break;
                    case "close": returned = reader.Close(); break;
                    case "buffer_read":
                    case "buffer_read_alias":
                        returned = buffer.Read(destination, step.Number);
                        complete = (int)returned == step.Number;
                        break;
                    case "buffer_skip": returned = buffer.Skip(step.Number); complete = (int)returned == step.Number; break;
                    case "buffer_close": returned = buffer.Close(); break;
                    case "mutate_source": source[step.Index] = step.Byte; break;
                    default: throw new NotSupportedException("Unknown oracle operation " + step.Operation);
                }
            }
            catch (Exception exception) when (exception is ArgumentException or InvalidOperationException)
            {
                error = exception.GetType().Name;
                complete = false;
            }
            rows.Add(new
            {
                operation = step.Operation, size = step.Size, count = step.Count, number = step.Number,
                index = step.Index, octet = step.Byte, destination = beforeDestination,
                returned, complete, error, destination_after = Hex(destination),
                state = new
                {
                    size = reader.Size, read_since_chunk = reader.ReadSinceChunk,
                    position = buffer.WhereAmI, remaining = buffer.Remaining, eof = buffer.EndOfFile,
                    reader_position = attached ? (int?)reader.WhereAmI : null, source = Hex(source),
                },
            });
            // The GDScript wrapper treats host/API exceptions as terminal. Each
            // differential scenario stops at that exception; sticky-error checks
            // exercise the explicit wrapper policy separately in the engine.
            if (error.Length != 0)
                break;
        }
        return new { name, hex = Hex(input), rows };
    }

    private static byte[] Chunk(string id, uint size, byte[] payload)
    {
        if (id.Length != 4 || id.Any(character => character > 255))
            throw new ArgumentException("Fixture IDs require exactly four raw bytes.");
        return Join(id.Select(character => (byte)character).ToArray(), BitConverter.GetBytes(size), payload);
    }

    private static byte[] Join(params byte[][] values) => values.SelectMany(value => value).ToArray();
    private static string Hex(byte[] value) => Convert.ToHexString(value).ToLowerInvariant();
}
