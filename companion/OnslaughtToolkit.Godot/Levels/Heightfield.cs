// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Security.Cryptography;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// A level's terrain: a 64 x 64 grid of tiles of 9 x 9 signed 16-bit height samples (one sample per world unit; a tile's ninth row and
/// column repeat its neighbour's first) and a height scale, read from the level archive's ERES chunk, and the game's lookup of the
/// height under a position.
///
/// Provenance: the lookup is written here from the decompilation's description of two functions, cited by function and not copied
/// (onslaught-decomp): <c>CHeightField::Collide</c> (0x0047eb80) and the bilinear read it calls (0x0047eb00). What it takes from them
/// is arithmetic, not source: each coordinate gets a bias and a large constant added in 32-bit floats and its bits are read as 8.8
/// fixed point; a position outside 0 to 512 on either axis answers 0; the four samples around the position are interpolated with
/// 8-bit fractions (arithmetic shifts, so a step down rounds down) and the result is multiplied by the height scale. The bias is the
/// named value <see cref="Bias"/> (the game's constant 0x3afffeb0), not a copied line. It is checked against the Toolkit's own Python
/// version (<c>tools/heightfield_lookup.py</c>, written the same way) on generated vectors and, locally, on every retail terrain.
/// Heights are in world units with Z down: the ground under the player's start in level 100 is about -10. A position that is not
/// finite answers 0 (the game's own answer for one is whatever its bit tricks make of it).
/// </summary>
public sealed class Heightfield
{
    public const int Tiles = 64, TileSamples = 9, SampleCount = Tiles * Tiles * TileSamples * TileSamples;

    /// <summary>The square, in world units from 0, that the lookup answers for.</summary>
    public const float Size = 512f;

    /// <summary>The bias that turns the float's round-to-nearest into a round-down: the game's constant 0x3afffeb0.</summary>
    internal const float Bias = 0.49999f / 256f;

    /// <summary>1.5 x 2^15: added to a coordinate it leaves the float's low 8 mantissa bits holding the position's fixed-point fraction.</summary>
    private const float Base = 49152f;

    private const int HeightfieldRecordSize = 0x13DC, ScaleAt = 0x102C, WaterAt = 0x1034, MixerSlots = 0x1000, MixerSlotSize = 0x14, MixerMapSize = 0x40000;

    private readonly short[] _samples;

    private Heightfield(short[] samples, float scale, float water)
    {
        _samples = samples;
        Scale = scale;
        Water = water;
    }

    /// <summary>World units per sample unit.</summary>
    public float Scale { get; }

    /// <summary>The water's height in world units (Z down: ground whose height is greater than this is under water).</summary>
    public float Water { get; }

    /// <summary>The samples, tile by tile: <c>((tileX * 64 + tileY) * 9 + row) * 9 + column</c>.</summary>
    public ReadOnlySpan<short> Samples => _samples;

    /// <summary>The terrain of an ERES payload, read in the order <c>CEngine::Deserialize</c> reads it, which must consume it exactly.</summary>
    /// <exception cref="InvalidDataException">The payload is not a terrain chunk.</exception>
    public static Heightfield Read(ReadOnlySpan<byte> eres)
    {
        Cursor cursor = new(eres);
        string tag = cursor.Header();
        if (tag != "ENGN") throw new InvalidDataException($"ERES starts with \"{tag}\", not ENGN");
        int count = cursor.Int32();
        if (count != 7) throw new InvalidDataException($"{count} mixer mips (there are 7)");
        for (int mip = 0; mip < count; mip++)
        {
            cursor.Header();
            cursor.Header();
            ReadOnlySpan<byte> map = cursor.Take(0x4C);
            uint dataPointer = BinaryPrimitives.ReadUInt32LittleEndian(map), extraPointer = BinaryPrimitives.ReadUInt32LittleEndian(map[8..]);
            int textureBytes = BinaryPrimitives.ReadInt32LittleEndian(map[16..]), textures = BinaryPrimitives.ReadInt32LittleEndian(map[20..]);
            if (dataPointer != 0)
            {
                cursor.Header();
                cursor.Take((long)textures * textureBytes);
            }
            if (extraPointer != 0)
            {
                cursor.Header();
                cursor.Take((long)textures * 1024);
            }
        }
        cursor.Header();
        cursor.Int32();  // the map number
        cursor.Header();
        cursor.Header();
        ReadOnlySpan<byte> record = cursor.Take(HeightfieldRecordSize);
        float scale = BitConverter.Int32BitsToSingle(BinaryPrimitives.ReadInt32LittleEndian(record[ScaleAt..]));
        float water = BitConverter.Int32BitsToSingle(BinaryPrimitives.ReadInt32LittleEndian(record[WaterAt..]));
        cursor.Header();
        ReadOnlySpan<byte> raw = cursor.Take(SampleCount * 2L);
        short[] samples = new short[SampleCount];
        for (int i = 0; i < samples.Length; i++) samples[i] = BinaryPrimitives.ReadInt16LittleEndian(raw[(i * 2)..]);
        cursor.Header();
        for (int slot = 0; slot < MixerSlots; slot++)
        {
            cursor.Header();
            cursor.Header();
            ReadOnlySpan<byte> entry = cursor.Take(MixerSlotSize);
            int n = BinaryPrimitives.ReadInt32LittleEndian(entry);
            uint pointer = BinaryPrimitives.ReadUInt32LittleEndian(entry[4..]);
            if (pointer != 0)
            {
                cursor.Header();
                cursor.Take((long)n * 81);
            }
        }
        cursor.Header();
        cursor.Take(MixerMapSize);
        if (cursor.Position != eres.Length) throw new InvalidDataException($"ERES has {eres.Length - cursor.Position} unread bytes");
        return new Heightfield(samples, scale, water);
    }

    /// <summary>The lowercase hex SHA-256 of the samples as the file stores them.</summary>
    public string SamplesSha256()
    {
        byte[] bytes = new byte[SampleCount * 2];
        for (int i = 0; i < _samples.Length; i++) BinaryPrimitives.WriteInt16LittleEndian(bytes.AsSpan(i * 2), _samples[i]);
        return Convert.ToHexStringLower(SHA256.HashData(bytes));
    }

    /// <summary>The height under (x, y) in world units (Z down); 0 outside the 0 to 512 square or for a position that is not finite.</summary>
    public float HeightAt(float x, float y)
    {
        if (!float.IsFinite(x) || !float.IsFinite(y)) return 0f;
        // Each step is a 32-bit float operation of its own, as in the game; the locals keep the compiler from merging them.
        float shiftedX = x - Bias;
        float shiftedY = y - Bias;
        float biasedX = shiftedX + Base;
        float biasedY = shiftedY + Base;
        int px = BitConverter.SingleToInt32Bits(biasedX), py = BitConverter.SingleToInt32Bits(biasedY);
        if (((px | py) & 0x3E0000) != 0) return 0f;
        int fx = px & 255, fy = py & 255;
        int at = ((((px >> 11) & 63) * 64 + ((py >> 11) & 63)) * 9 + ((py >> 8) & 7)) * 9 + ((px >> 8) & 7);
        int top = _samples[at] + (((_samples[at + 1] - _samples[at]) * fx) >> 8);
        int bottom = _samples[at + 9] + (((_samples[at + 10] - _samples[at + 9]) * fx) >> 8);
        int value = top + (((bottom - top) * fy) >> 8);
        float scaled = (float)value * Scale;
        return scaled;
    }

    /// <summary>A read position over the payload that refuses to pass its end.</summary>
    private ref struct Cursor(ReadOnlySpan<byte> data)
    {
        private readonly ReadOnlySpan<byte> _data = data;

        public int Position { get; private set; }

        public ReadOnlySpan<byte> Take(long count)
        {
            if (count < 0 || count > _data.Length - Position) throw new InvalidDataException($"a read of {count} bytes at {Position} passes the end ({_data.Length})");
            ReadOnlySpan<byte> bytes = _data.Slice(Position, (int)count);
            Position += (int)count;
            return bytes;
        }

        public int Int32() => BinaryPrimitives.ReadInt32LittleEndian(Take(4));

        /// <summary>A chunk header (a tag and a size, read in place: the payload follows and nothing is skipped).</summary>
        public string Header()
        {
            ReadOnlySpan<byte> header = Take(8);
            return System.Text.Encoding.Latin1.GetString(header[..4]);
        }
    }
}
