// SPDX-License-Identifier: GPL-3.0-only
using System.Collections;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
namespace OnslaughtToolkit.Companion.Levels;

/// <summary>Read-only identity for an unsupported edit; never manufactures a writable world or publishes raw state.</summary>
internal static class EditorDiscardState
{
    internal static string Hash(WorldBody body)
    {
        using IncrementalHash hash = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        using HashSink sink = new(hash);
        using BinaryWriter writer = new(sink, Encoding.UTF8, leaveOpen: true);
        HashSet<object> ancestors = new(ReferenceEqualityComparer.Instance);
        int nodes = 0;
        void Text(string value) { writer.Write(value.Length); foreach (char unit in value) writer.Write((ushort)unit); }
        void Value(object? value, int depth)
        {
            if (++nodes > (1 << 20) || depth > 64) throw new InvalidDataException("This unsupported edit is too complex to confirm safely.");
            if (value is null) { writer.Write((byte)0); return; }
            Type type = value.GetType();
            writer.Write((byte)1); Text(type.FullName ?? type.Name);
            switch (value)
            {
                case string text: Text(text); return;
                case byte[] bytes: writer.Write(bytes.Length); writer.Write(bytes); return;
                case bool item: writer.Write(item); return;
                case byte item: writer.Write(item); return;
                case sbyte item: writer.Write(item); return;
                case short item: writer.Write(item); return;
                case ushort item: writer.Write(item); return;
                case int item: writer.Write(item); return;
                case uint item: writer.Write(item); return;
                case long item: writer.Write(item); return;
                case ulong item: writer.Write(item); return;
                case float item: writer.Write(BitConverter.SingleToInt32Bits(item)); return;
                case double item: writer.Write(BitConverter.DoubleToInt64Bits(item)); return;
                case char item: writer.Write((ushort)item); return;
                case Enum item: Text(item.ToString("D")); return;
            }
            bool reference = !type.IsValueType;
            if (reference && !ancestors.Add(value)) throw new InvalidDataException("This unsupported edit contains a cycle.");
            try
            {
                if (value is IEnumerable sequence)
                {
                    foreach (object? item in sequence) Value(item, depth + 1);
                    writer.Write((byte)255); return;
                }
                if (type.Namespace != typeof(WorldBody).Namespace && type != typeof(System.Numerics.Vector3))
                    throw new InvalidDataException("This unsupported edit contains an unknown value type.");
                var properties = type.GetProperties(BindingFlags.Instance | BindingFlags.Public)
                    .Where(property => property.CanRead && property.GetIndexParameters().Length == 0).OrderBy(property => property.Name, StringComparer.Ordinal).ToArray();
                var fields = type.GetFields(BindingFlags.Instance | BindingFlags.Public).OrderBy(field => field.Name, StringComparer.Ordinal).ToArray();
                writer.Write(properties.Length); writer.Write(fields.Length);
                foreach (PropertyInfo property in properties) { Text(property.Name); Value(property.GetValue(value), depth + 1); }
                foreach (FieldInfo field in fields) { Text(field.Name); Value(field.GetValue(value), depth + 1); }
            }
            catch (TargetInvocationException error) { throw new InvalidDataException("This unsupported edit cannot be inspected safely.", error); }
            finally { if (reference) ancestors.Remove(value); }
        }
        Value(body, 0); writer.Flush();
        return Convert.ToHexStringLower(hash.GetHashAndReset());
    }
    private sealed class HashSink(IncrementalHash hash) : Stream
    {
        public override bool CanRead => false;
        public override bool CanSeek => false;
        public override bool CanWrite => true;
        public override long Length => throw new NotSupportedException();
        public override long Position { get => throw new NotSupportedException(); set => throw new NotSupportedException(); }
        public override void Flush() { }
        public override void Write(byte[] buffer, int offset, int count) => hash.AppendData(buffer, offset, count);
        public override void Write(ReadOnlySpan<byte> buffer) => hash.AppendData(buffer);
        public override void WriteByte(byte value) { Span<byte> one = stackalloc byte[1]; one[0] = value; hash.AppendData(one); }
        public override int Read(byte[] buffer, int offset, int count) => throw new NotSupportedException();
        public override long Seek(long offset, SeekOrigin origin) => throw new NotSupportedException();
        public override void SetLength(long value) => throw new NotSupportedException();
    }
}
