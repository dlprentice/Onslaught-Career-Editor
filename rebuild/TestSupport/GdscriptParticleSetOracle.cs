// SPDX-License-Identifier: GPL-3.0-or-later
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using OnslaughtRebuild.Client;

// Synthetic parser probes and read-only hashes of the three prepared retail
// files. The corpus stays at its existing path; no input file is copied/written.
internal static class GdscriptParticleSetOracle
{
    private const string Header = "ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd\r\nFile_Version 1.000000\r\nNum_Particle_Descriptors ";
    private static string Record(string type, string name, string fields = "") =>
        "Particle_Descriptor_Type " + type + "\r\nParticle_Descriptor_Name " + name + "\r\n" + fields + ParticleSetFile.RecordSeparator + "\r\n";

    internal static object Build()
    {
        string rich = Header + "2\r\n" + Record("1", "Alpha\0\ud800", "I -2147483648\r\nF -0\r\nM 1.5 modifier name\r\nR NONE\r\nDup\r\nDup later value\r\nEmpty \r\n Unknown value\r\nUnknown\r\n") +
            Record("-7", "Alpha\0\ud800", "I 2147483647\r\nM -0 NONE\r\nRef \r\n");
        var probes = new List<(string Name, string? Text)> { ("null", null), ("empty", ""), ("lf-only", (Header + "0\r\n").Replace("\r\n", "\n")),
            ("empty-set", Header + "0\r\n"), ("missing-final-crlf", Header + "0"), ("negative-declared-count", Header + "-7\r\n"),
            ("declared-count-not-enforced", Header + "2147483647\r\n"), ("duplicate-raw-names", rich),
            ("trailing-blank", rich + "\r\n"), ("empty-record", Header + "1\r\n" + ParticleSetFile.RecordSeparator + "\r\n"),
            ("partial-record", Header + "1\r\nParticle_Descriptor_Type 1\r\n"),
            ("wrong-header", "Bad" + (Header + "0\r\n")), ("wrong-version", Header.Replace("File_Version ", "Version ") + "0\r\n"),
            ("wrong-count", Header.Replace("Num_Particle_Descriptors ", "Count ") + "0\r\n"),
            ("count-format", Header + "x\r\n"), ("count-overflow", Header + "2147483648\r\n"),
            ("count-before-bad-record", Header + "2147483648\r\nWrong\r\n" + ParticleSetFile.RecordSeparator + "\r\n"),
            ("type-format", Header + "1\r\n" + Record("x", "Name")), ("type-overflow", Header + "1\r\n" + Record("2147483648", "Name")),
            ("name-before-type-number", (Header + "1\r\n" + Record("x", "Name")).Replace("Particle_Descriptor_Name", "Name")),
            ("empty-name", Header + "1\r\n" + Record("0", "")),
            ("normalizes-count-and-type", Header + " +0001 \r\n" + Record("\t+0001 ", "Space name ", "Field  leading and trailing \t\r\n")),
            ("preserves-bare-cr-lf", Header + "1\r\n" + Record("1", "N\n\r", "K value\ninside\rvalue\r\n")),
            ("all-latin1-bytes-in-field", Header + "1\r\n" + Record("1", "Bytes", "Raw " + new string(Enumerable.Range(0, 256).Where(x => x != 13 && x != 10).Select(x => (char)x).ToArray()) + "\r\n")),
            ("nonlatin-and-surrogates", Header + "1\r\n" + Record("1", "Ā\ud800\udfff\ud800X\udfff", "Raw Ǽϐ𝄞\r\n")) };
        foreach (string value in new[] { "", " ", "0", "-0", "+01", "2147483647", "2147483648", "-2147483648", "-2147483649", "1.5", ".5", "1.", "1e9999", "1e-9999", "NaN", "Infinity", "-Infinity", "1\0", "1 \0", "1\0 ", "1.000000059604644775390625000000000001", "0 NONE", "1.5 modifier with spaces", " 1.5", "NONE", "none" })
            probes.Add(("getter-" + probes.Count, Header + "1\r\n" + Record("1", "Value", "Key " + value + "\r\n")));
        var cases = probes.Select(probe => BuildCase(probe.Name, probe.Text)).ToArray();

        string source = File.ReadAllText(Path.GetFullPath("../OnslaughtRebuild.Client/ParticleSetFile.cs"));
        string switchBody = source.Split("kind = tokenName switch", 2)[1].Split("_ => RetailParticleTokenParseKind.Unrecognized", 2)[0];
        string[] tokens = Regex.Matches(switchBody, "\"([^\"\\r\\n]+)\"").Select(match => match.Groups[1].Value).Distinct(StringComparer.Ordinal).ToArray();
        var tokenInputs = tokens.Concat(tokens.Select(x => x.ToLowerInvariant())).Concat(new[] { "", "unknown", "Radius\0suffix", "Radius ", "Radius\ud800" }).Cast<string?>().Append(null);
        var kinds = tokenInputs.Select(name => { bool recognized = RetailParticleTokenContract.TryGetParseKind(name!, out var kind);
            return new { name = Units(name), recognized, kind = (int)kind }; }).ToArray();
        var classes = new[] { int.MinValue, -1, 0 }.Concat(Enumerable.Range(1, 15)).Append(int.MaxValue).Select(type => new {
            type, name = Try(() => RetailParticleTokenContract.DescriptorClassName(type)), address = Try(() => RetailParticleTokenContract.DescriptorLoaderAddress(type)) }).ToArray();

        var corpus = new[] {
            ("MainSet.par", "a51fe4419b55e1af132e31c6b3cd8133c937745d8f4ab691eb5a0d81017ded06"),
            ("Frontend.par", "01a4c73d7cfc666b4a367736fabd1d91bf3459ed1c538b6ca77f70c069cf8bc6"),
            ("ModelViewer.par", "32d85d1f0400f46a45078d49c695967cde60ed572053059fd6246227162115a9")
        }.Select(row => {
            string path = Path.GetFullPath(Path.Combine("Assets/Level100/ParticleSets", row.Item1));
            byte[] bytes = File.ReadAllBytes(path);
            if (Hash(bytes) != row.Item2) throw new InvalidDataException("Prepared particle input differs from its existing pin: " + row.Item1);
            var set = ParticleSetFile.Parse(bytes);
            if (!set.ToBytes().SequenceEqual(bytes)) throw new InvalidDataException("Existing particle reader did not round-trip its input.");
            return new { name = row.Item1, path, length = bytes.Length, sha256 = row.Item2, projection = Projection(set) };
        }).ToArray();
        var latin = new List<object>();
        for (int unit = 256; unit <= 65535; unit++)
        {
            byte[] bytes = Encoding.Latin1.GetBytes(new string((char)unit, 1));
            if (bytes.Length != 1 || bytes[0] != 63) latin.Add(new { unit, bytes = bytes.Select(x => (int)x).ToArray() });
        }
        return new { schema = 1, cases, kinds, classes, corpus, latin1_single_overrides = latin };
    }

    private static object BuildCase(string name, string? text)
    {
        object expected;
        try
        {
            var set = ParticleSetFile.Parse(text!);
            var queries = new List<object>();
            for (int index = 0; index < set.Descriptors.Count; index++)
            {
                ParticleDescriptor descriptor = set.Descriptors[index];
                foreach (string? key in descriptor.Fields.Select(f => f.Key).Append("missing").Append("").Cast<string?>().Append(null).Distinct(StringComparer.Ordinal))
                {
                    foreach (string operation in new[] { "raw", "raw_all", "int_value", "int_or_default", "float_bits", "retail_direct_float_bits", "float_with_modifier", "reference" })
                        queries.Add(new { index, key = Units(key), operation, expected = Query(descriptor, operation, key!) });
                }
            }
            expected = new { ok = true, projection = Projection(set), queries,
                lookup_first = set.Descriptors.Select(descriptor => set.Descriptors.ToList().IndexOf(set.Find(descriptor.Name)!)).ToArray() };
        }
        catch (Exception error) { expected = Failure(error); }
        return new { name, units = Units(text), expected };
    }

    private static object Query(ParticleDescriptor descriptor, string operation, string key)
    {
        try
        {
            return operation switch
            {
                "raw" => new { ok = true, value = Units(descriptor.Raw(key)) },
                "raw_all" => new { ok = true, value = descriptor.RawAll(key).Select(Units).ToArray() },
                "int_value" => new { ok = true, value = descriptor.Int(key) },
                "int_or_default" => new { ok = true, value = descriptor.IntOrDefault(key, -17) },
                "float_bits" => new { ok = true, bits = BitConverter.SingleToUInt32Bits(descriptor.Float(key)) },
                "retail_direct_float_bits" => new { ok = true, bits = BitConverter.SingleToUInt32Bits(descriptor.RetailDirectFloat(key)) },
                "float_with_modifier" => Modifier(descriptor.FloatWithModifier(key)),
                "reference" => new { ok = true, value = Units(descriptor.Reference(key)) },
                _ => throw new InvalidOperationException(operation)
            };
        }
        catch (Exception error) { return Failure(error); }
    }
    private static object Modifier((float Value, string? Modifier) value) => new { ok = true,
        value = new { bits = BitConverter.SingleToUInt32Bits(value.Value), modifier = Units(value.Modifier) } };

    private static object Projection(ParticleSetFile set)
    {
        using var bytes = new MemoryStream();
        using var writer = new BinaryWriter(bytes, Encoding.UTF8, leaveOpen: true);
        void Text(string? value)
        {
            writer.Write(value?.Length ?? -1);
            if (value is not null) foreach (char unit in value) writer.Write((ushort)unit);
        }
        void Scalar(Func<object> read)
        {
            object value;
            try { value = read(); }
            catch (Exception error)
            {
                writer.Write(false); Text(error.GetType().Name); Text((error as ArgumentException)?.ParamName ?? "");
                return;
            }
            writer.Write(true);
            switch (value)
            {
                case int number: writer.Write(number); break;
                case float single: writer.Write(BitConverter.SingleToUInt32Bits(single)); break;
                case ValueTuple<float, string?> pair: writer.Write(BitConverter.SingleToUInt32Bits(pair.Item1)); Text(pair.Item2); break;
                case string name: Text(name); break;
                case null: Text(null); break;
                default: throw new InvalidOperationException(value.GetType().Name);
            }
        }
        Text(set.Header); Text(set.VersionLine); writer.Write(set.DeclaredCount); writer.Write(set.Descriptors.Count);
        foreach (ParticleDescriptor descriptor in set.Descriptors)
        {
            writer.Write(descriptor.TypeId); Text(descriptor.Name); writer.Write(descriptor.Fields.Count);
            foreach (ParticleField field in descriptor.Fields) { Text(field.Key); Text(field.Value); }
            foreach (string key in descriptor.Fields.Select(field => field.Key).Distinct(StringComparer.Ordinal))
            {
                Text(key);
                RetailParticleTokenContract.TryGetParseKind(key, out var kind); writer.Write((int)kind);
                switch (kind)
                {
                    case RetailParticleTokenParseKind.DirectInt: Scalar(() => descriptor.Int(key)); break;
                    case RetailParticleTokenParseKind.DirectFloat: Scalar(() => descriptor.RetailDirectFloat(key)); break;
                    case RetailParticleTokenParseKind.FloatWithOptionalReference: Scalar(() => descriptor.FloatWithModifier(key)); break;
                    case RetailParticleTokenParseKind.ReferenceName: Scalar(() => descriptor.Reference(key)!); break;
                }
            }
        }
        writer.Flush();
        byte[] encoded = set.ToBytes();
        return new { declared_count = set.DeclaredCount, count = set.Descriptors.Count, facts_sha256 = Hash(bytes.ToArray()),
            bytes_sha256 = Hash(encoded), bytes_length = encoded.Length };
    }
    private static object Try(Func<object> action)
    {
        try { return new { ok = true, value = action() }; }
        catch (Exception error) { return Failure(error); }
    }
    private static object Failure(Exception error) => new { ok = false, error_type = error.GetType().Name,
        parameter = (error as ArgumentException)?.ParamName ?? "" };
    private static int[]? Units(string? text) => text?.Select(unit => (int)unit).ToArray();
    private static string Hash(byte[] bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();
}
