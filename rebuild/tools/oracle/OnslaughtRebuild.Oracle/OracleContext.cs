// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Parity.Data;
using OnslaughtRebuild.Parity.World;

namespace OnslaughtRebuild.Oracle;

/// <summary>What the adapters share: the image folder, the installation, and the real objects they read.</summary>
public sealed class OracleContext(string imagesDirectory, string gameDirectory)
{
    private HeightField? _heightField;

    public string ImagesDirectory { get; } = imagesDirectory;

    public string GameDirectory { get; } = gameDirectory;

    public HeightField HeightField => _heightField ??= LoadHeightField();

    public byte[] Image(string name) => File.ReadAllBytes(Path.Combine(ImagesDirectory, name + ".bin"));

    private HeightField LoadHeightField()
    {
        string path = new[] { "data/resources", "data/Resources" }.Select(d => Path.Combine(GameDirectory, d, "100_res_PC.aya")).First(File.Exists);
        var c = new ChunkReader(MemBuffer.FromFile("100_res_PC.aya", File.ReadAllBytes(path)));
        uint tag;
        while ((tag = c.GetNext()) != ChunkReader.MakeId("ERES"))
        {
            if (tag == 0)
            {
                throw new InvalidDataException("no ERES chunk");
            }

            c.Skip();
        }

        HeightField h = EngineResources.Read(c).HeightField;
        if (!Image("hf").AsSpan(0, HeightField.RecordSize).SequenceEqual(h.Record))
        {
            throw new InvalidDataException("the height field image and the C# height field differ");
        }

        return h;
    }
}
