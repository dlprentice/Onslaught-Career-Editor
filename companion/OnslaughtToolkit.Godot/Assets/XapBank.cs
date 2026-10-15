// SPDX-License-Identifier: MIT
using System.Buffers.Binary;
using System.Text;

namespace OnslaughtToolkit.Companion.Assets;

/// <summary>One sample in a sound bank: its name, its decoded size in bytes and its 4-bit ADPCM data.</summary>
public sealed record XapSample(string Name, int PcmBytes, byte[] Packed)
{
    public double Seconds => PcmBytes / 2.0 / XapBank.SampleRate;
}

/// <summary>
/// The game's sound-effect and HUD-voice banks (<c>data/sounds/sounds_&lt;language&gt;_pc.xap</c>), as
/// reverse-engineering/asset-formats/xap-sample-bank.md describes them: a "PCXP" magic and a count, then per sample a
/// "PSMP" tag, a 64-byte name, the decoded size and IMA ADPCM data (high nibble first, from a zero state), which decodes
/// to 16-bit mono PCM at 44,100 Hz. A bank that does not end where its last sample ends is refused.
/// </summary>
public static class XapBank
{
    public const int SampleRate = 44_100;
    private const int NameBytes = 64;

    private static readonly int[] IndexTable = [-1, -1, -1, -1, 2, 4, 6, 8, -1, -1, -1, -1, 2, 4, 6, 8];

    private static readonly int[] StepTable =
    [
        7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41, 45, 50, 55, 60, 66, 73, 80, 88, 97, 107,
        118, 130, 143, 157, 173, 190, 209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724, 796, 876, 963,
        1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272, 2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358, 5894,
        6484, 7132, 7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500, 20350, 22385, 24623, 27086, 29794,
        32767,
    ];

    public static IReadOnlyList<XapSample> Read(byte[] bank)
    {
        if (bank.Length < 8) throw new InvalidDataException("Not a supported sound bank: it is shorter than its header.");
        int count = BinaryPrimitives.ReadInt32LittleEndian(bank.AsSpan(4));
        if (count < 0) throw new InvalidDataException("Not a supported sound bank: negative sample count.");
        List<XapSample> samples = [];
        long position = 8;
        for (int i = 0; i < count; i++)
        {
            if (position + 4 + NameBytes + 4 > bank.Length) throw new InvalidDataException($"Not a supported sound bank: sample {i} runs past the end.");
            position += 4;
            int nameEnd = Array.IndexOf(bank, (byte)0, (int)position, NameBytes);
            string name = Encoding.Latin1.GetString(bank, (int)position, (nameEnd < 0 ? (int)position + NameBytes : nameEnd) - (int)position);
            position += NameBytes;
            uint size = BinaryPrimitives.ReadUInt32LittleEndian(bank.AsSpan((int)position));
            position += 4;
            long packed = (size + 3L) / 4;
            if (size > int.MaxValue || position + packed > bank.Length)
                throw new InvalidDataException($"Not a supported sound bank: {name} runs past the end.");
            samples.Add(new XapSample(name, (int)size, bank.AsSpan((int)position, (int)packed).ToArray()));
            position += packed;
        }
        if (position != bank.Length) throw new InvalidDataException($"Not a supported sound bank: its samples end at byte {position} of {bank.Length}.");
        return samples;
    }

    /// <summary>The sample's 16-bit mono PCM.</summary>
    public static short[] Decode(XapSample sample)
    {
        int count = sample.PcmBytes / 2;
        short[] pcm = new short[count];
        int predicted = 0, index = 0;
        for (int n = 0; n < count; n++)
        {
            byte b = sample.Packed[n >> 1];
            int code = (n & 1) == 0 ? (b >> 4) & 0xF : b & 0xF;
            int step = StepTable[index];
            int difference = step >> 3;
            if ((code & 4) != 0) difference += step;
            if ((code & 2) != 0) difference += step >> 1;
            if ((code & 1) != 0) difference += step >> 2;
            predicted = Math.Clamp((code & 8) != 0 ? predicted - difference : predicted + difference, -32768, 32767);
            index = Math.Clamp(index + IndexTable[code], 0, 88);
            pcm[n] = (short)predicted;
        }
        return pcm;
    }

    /// <summary>A RIFF/WAVE file of 16-bit mono PCM.</summary>
    public static byte[] Wav(short[] pcm, int rate = SampleRate)
    {
        int dataBytes = pcm.Length * 2;
        byte[] wav = new byte[44 + dataBytes];
        Span<byte> w = wav;
        Encoding.ASCII.GetBytes("RIFF").CopyTo(w);
        BinaryPrimitives.WriteInt32LittleEndian(w[4..], 36 + dataBytes);
        Encoding.ASCII.GetBytes("WAVEfmt ").CopyTo(w[8..]);
        BinaryPrimitives.WriteInt32LittleEndian(w[16..], 16);
        BinaryPrimitives.WriteInt16LittleEndian(w[20..], 1);
        BinaryPrimitives.WriteInt16LittleEndian(w[22..], 1);
        BinaryPrimitives.WriteInt32LittleEndian(w[24..], rate);
        BinaryPrimitives.WriteInt32LittleEndian(w[28..], rate * 2);
        BinaryPrimitives.WriteInt16LittleEndian(w[32..], 2);
        BinaryPrimitives.WriteInt16LittleEndian(w[34..], 16);
        Encoding.ASCII.GetBytes("data").CopyTo(w[36..]);
        BinaryPrimitives.WriteInt32LittleEndian(w[40..], dataBytes);
        for (int i = 0; i < pcm.Length; i++) BinaryPrimitives.WriteInt16LittleEndian(w[(44 + 2 * i)..], pcm[i]);
        return wav;
    }
}
