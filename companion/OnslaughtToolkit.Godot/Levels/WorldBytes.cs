// SPDX-License-Identifier: GPL-3.0-only
using System.Buffers.Binary;
using System.Text;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>How a length-prefixed string stores its length: a signed byte, an unsigned byte or a 32-bit word.</summary>
internal enum LengthKind { SignedByte, UnsignedByte, Int32 }

/// <summary>
/// Little-endian reads over a world body, each refused when it would pass the end. Strings are Latin-1 (one byte, one
/// character), so every byte value survives a round trip.
/// </summary>
internal sealed class ByteReader(byte[] data)
{
    /// <summary>A count above this is framing damage, not data (the Toolkit decoder's limit).</summary>
    private const int CountLimit = 1 << 20;

    private int _position;

    internal int Position => _position;
    internal int Length => data.Length;

    internal ReadOnlySpan<byte> Take(int count)
    {
        if (count < 0 || count > data.Length - _position)
            throw new InvalidDataException($"read of {count} bytes at {_position} passes the end ({data.Length})");
        ReadOnlySpan<byte> slice = data.AsSpan(_position, count);
        _position += count;
        return slice;
    }

    internal byte[] Bytes(int count) => Take(count).ToArray();

    internal int Int32() => BinaryPrimitives.ReadInt32LittleEndian(Take(4));

    internal ushort UInt16() => BinaryPrimitives.ReadUInt16LittleEndian(Take(2));

    internal short Int16() => BinaryPrimitives.ReadInt16LittleEndian(Take(2));

    internal float Single() => BinaryPrimitives.ReadSingleLittleEndian(Take(4));

    /// <summary>A 32-bit count from 0 to the limit.</summary>
    internal int Count()
    {
        int value = Int32();
        if (value is < 0 or > CountLimit) throw new InvalidDataException($"implausible count {value} at {_position}");
        return value;
    }

    /// <summary>A 16-bit unsigned count.</summary>
    internal int CountUInt16() => UInt16();

    /// <summary>A 16-bit signed count, which may not be negative.</summary>
    internal int CountInt16()
    {
        short value = Int16();
        if (value < 0) throw new InvalidDataException($"implausible count {value} at {_position}");
        return value;
    }

    /// <summary>A string up to its NUL, at most 255 characters (CInitThing::Load's loop).</summary>
    internal string CString()
    {
        int window = Math.Min(256, data.Length - _position);
        int nul = window <= 0 ? -1 : data.AsSpan(_position, window).IndexOf((byte)0);
        if (nul < 0) throw new InvalidDataException($"unterminated string at {_position}");
        string text = Encoding.Latin1.GetString(data, _position, nul);
        _position += nul + 1;
        return text;
    }

    internal string LString(LengthKind kind = LengthKind.SignedByte)
    {
        int length = kind switch
        {
            LengthKind.SignedByte => (sbyte)Take(1)[0],
            LengthKind.UnsignedByte => Take(1)[0],
            _ => Int32(),
        };
        if (length < 0) throw new InvalidDataException($"negative string length at {_position}");
        return Encoding.Latin1.GetString(Take(length));
    }
}

/// <summary>Little-endian writes into a world body, refusing what the format's fixed-width fields cannot hold.</summary>
internal sealed class ByteWriter
{
    private readonly MemoryStream _out = new();

    internal byte[] ToArray() => _out.ToArray();

    internal void Raw(ReadOnlySpan<byte> bytes) => _out.Write(bytes);

    internal void Int32(int value)
    {
        Span<byte> b = stackalloc byte[4];
        BinaryPrimitives.WriteInt32LittleEndian(b, value);
        _out.Write(b);
    }

    internal void UInt16(int value)
    {
        if (value is < 0 or > ushort.MaxValue) throw new InvalidDataException($"{value} does not fit an unsigned 16-bit field");
        Span<byte> b = stackalloc byte[2];
        BinaryPrimitives.WriteUInt16LittleEndian(b, (ushort)value);
        _out.Write(b);
    }

    internal void Int16(int value)
    {
        if (value is < short.MinValue or > short.MaxValue) throw new InvalidDataException($"{value} does not fit a signed 16-bit field");
        Span<byte> b = stackalloc byte[2];
        BinaryPrimitives.WriteInt16LittleEndian(b, (short)value);
        _out.Write(b);
    }

    internal void Single(float value)
    {
        Span<byte> b = stackalloc byte[4];
        BinaryPrimitives.WriteSingleLittleEndian(b, value);
        _out.Write(b);
    }

    internal void CString(string text)
    {
        byte[] bytes = Latin1(text);
        if (bytes.Length > 255 || Array.IndexOf(bytes, (byte)0) >= 0)
            throw new InvalidDataException($"string {Describe(text)} cannot be written NUL-terminated");
        _out.Write(bytes);
        _out.WriteByte(0);
    }

    internal void LString(string text, LengthKind kind = LengthKind.SignedByte)
    {
        byte[] bytes = Latin1(text);
        switch (kind)
        {
            case LengthKind.SignedByte when bytes.Length > sbyte.MaxValue:
            case LengthKind.UnsignedByte when bytes.Length > byte.MaxValue:
                throw new InvalidDataException($"string {Describe(text)} is longer than its length field holds");
            case LengthKind.Int32:
                Int32(bytes.Length);
                break;
            default:
                _out.WriteByte((byte)bytes.Length);
                break;
        }
        _out.Write(bytes);
    }

    private static byte[] Latin1(string text)
    {
        foreach (char c in text)
            if (c > 0xFF) throw new InvalidDataException($"string {Describe(text)} holds a character outside Latin-1");
        return Encoding.Latin1.GetBytes(text);
    }

    private static string Describe(string text) => text.Length <= 24 ? $"\"{text}\"" : $"of {text.Length} characters";
}
