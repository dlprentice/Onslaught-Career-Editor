// SPDX-License-Identifier: GPL-3.0-or-later

using System.Buffers.Binary;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

/// <summary>
/// Parser for the exact compiled script objects consumed by Level 100. This
/// deliberately accepts only the 25 hash-pinned Steam payloads.
/// </summary>
internal sealed class Level100MissionProgram
{
    internal const string ExpectedSha256 =
        "73eb349b9c4b5c5d7294b2183cd4d4aebe024c5d3c8cda9be685bd1463ed6fb1";

    private const int BuiltInEventCount = 13;
    private const string ResourcePrefix =
        "OnslaughtRebuild.Core.Assets.Level100.Scripts.level100-";

    private static readonly IReadOnlyDictionary<string, ProgramIdentity> s_programs =
        new Dictionary<string, ProgramIdentity>(StringComparer.Ordinal)
        {
            ["AirborneDrone1"] = new(920, "7209f0752e4715d1b3dbd9d102cda997f65b3d4ff38a37a5c382d4bb5f364f28"),
            ["AirborneDrone2"] = new(952, "6491cb323adb7758176c0afce12ec8d84e025323bdc4014f1f452c881102ed17"),
            ["AirTrainer"] = new(625, "9549f63b5bd964dfafb1cd002685144311db2e53b01d79b8a1be47d68f0da9d7"),
            ["BattleEngine"] = new(990, "b68d9e176051f6fec4fb84d344c51998047cf635a40dd56cc87c30ec1156ab26"),
            ["Facilities"] = new(564, "3f19d9cb84a06a898aea98cf2236301f4b81739c874a018093ca8f1e3a9b6ed2"),
            ["FiringRange"] = new(913, "8b05629d4a350005322333c1442e068f3f50707e65ab810c665c82f34bd7a7c9"),
            ["Flyby"] = new(394, "20039756aba7f0b79a5f9bccc3c45f6b17a0e6ec27e05b406f4c40c3254e1444"),
            ["Hangar"] = new(3419, "f5d42f5c58e9874d97965971b7e2a7cdede12a039eaf3ab699965da61568d073"),
            ["LevelScript"] = new(20586, ExpectedSha256),
            ["Setup"] = new(2402, "986e2b60afa62df15c9ad52fc04538a8eab8473a4eab46fc1844e67d7a85d1e0"),
            ["StaticTarget"] = new(1011, "6670ab8cf964b037fb29f4feff19790a1e15c9fc45504e71fc259eadda9e8a54"),
            ["StaticTarget2"] = new(1016, "28281145def2cdd0576b4ab9c6cb9e47f36c37f59397b3a941f46b15f334b8c3"),
            ["TankFactory"] = new(3790, "44577134d213c3e8362fcedfe8344cbc3ac1346623f89408a16d32d685703892"),
            ["TargetTank1"] = new(1278, "50839be04b6d72e29ecf6b1519c43baa9f826cda3d3c1bd0ebe56eedc292d305"),
            ["TargetTank2"] = new(739, "331a5ecdf7122014d3eb70827f30b348ba2d8c80a58971c4764d040b4da7dc09"),
            ["TargetTruck1"] = new(1299, "cca2f36f70d0751e62cf5a66e4fc23a12a2f77d98f9eb8579f28d8625e72ebbb"),
            ["TargetTruck2"] = new(1299, "7c00c14b9de87873f21848cd28696a331cf0b5902548988030ef3192c438a2b6"),
            ["TargetTruck3"] = new(1299, "8b864edfa626bbb9f45e06c6cc73b71d6b68c3ae41469fc4cd61a453d0386c52"),
            ["TargetZone1"] = new(969, "50269961be899b4f50025300ff1af8bb220437b36f9e8bce1cd2806e7617d56c"),
            ["TargetZone2"] = new(1092, "8a4b727dcf0f9e249c7c1ab0155326004356f0ad5dd84f226148db794a884af3"),
            ["TargetZone3"] = new(1118, "222c44814482a69ff716b785d01a0bc7b508f19fc60774f2067db5d8bd1ca90d"),
            ["TargetZone4"] = new(1092, "026a70263ede8daaed00d324dbe13160bcb4882a10e10f7bfe384f62896b2e8f"),
            ["Transporter"] = new(408, "15cf230e674d80bb92fecefc4f16c708d3c969c02aa1384c4142de47dbf35a5f"),
            ["Turret"] = new(835, "462614eaa5222bd3be759d4b8d0217d695c3afbbf36e334fbdc256a906797c71"),
            ["Weather"] = new(540, "369ca18aba315a853404779b931d45bed0d692d5bad38536a41c4d4706650ce4"),
        };

    private static readonly (string Name, int InstructionPointer)[] s_levelScriptEvents =
    [
        ("Reached Target Zone 1", 152),
        ("Reached Firing Range", 172),
        ("Static Target Destroyed", 248),
        ("Static Target 2 Destroyed", 313),
        ("Moving Target Destroyed", 363),
        ("Reached Target Zone 2", 545),
        ("Airborne Target 1 Destroyed", 564),
        ("Reached Target Zone 3", 594),
        ("Airborne Target 2 Destroyed", 688),
        ("Reached Target Zone 4", 722),
        ("Broke Tutorial", 744),
        ("Hit Friendly Building", 760),
        ("Friendly Building Destroyed", 788),
        ("Flash things", 804),
        ("Help Player", 818),
        ("Abort Airborne Drones", 829),
        ("Evade Failed", 875),
    ];

    private Level100MissionProgram(
        string name,
        string sha256,
        Level100Instruction[] instructions,
        int[] builtInEventInstructionPointers,
        Level100Symbol[] symbols,
        IReadOnlyDictionary<string, int> namedEventInstructionPointers,
        bool runInitializer)
    {
        Name = name;
        Sha256 = sha256;
        Instructions = instructions;
        BuiltInEventInstructionPointers = builtInEventInstructionPointers;
        Symbols = symbols;
        NamedEventInstructionPointers = namedEventInstructionPointers;
        RunInitializer = runInitializer;
    }

    internal string Name { get; }

    internal string Sha256 { get; }

    internal IReadOnlyList<Level100Instruction> Instructions { get; }

    internal IReadOnlyList<int> BuiltInEventInstructionPointers { get; }

    internal IReadOnlyList<Level100Symbol> Symbols { get; }

    internal IReadOnlyDictionary<string, int> NamedEventInstructionPointers { get; }

    internal bool RunInitializer { get; }

    internal static IReadOnlyCollection<string> ProgramNames => s_programs.Keys.ToArray();

    internal static Level100MissionProgram LoadEmbedded() => LoadEmbedded("LevelScript");

    internal static Level100MissionProgram LoadEmbedded(string name)
    {
        if (!s_programs.TryGetValue(name, out ProgramIdentity expected))
        {
            throw new ArgumentOutOfRangeException(nameof(name), $"Unknown Level 100 script '{name}'.");
        }

        string resourceName = ResourcePrefix + name + ".mso.bin";
        using Stream stream = Assembly.GetExecutingAssembly()
            .GetManifestResourceStream(resourceName)
            ?? throw new InvalidOperationException(
                $"The materialized Level 100 {name} object is missing. " +
                "Run rebuild/tools/materialize_retail_assets.py against the supported Steam install.");
        using var memory = new MemoryStream(expected.Length);
        stream.CopyTo(memory);
        return Parse(memory.ToArray(), name, expected);
    }

    private static Level100MissionProgram Parse(
        byte[] payload,
        string expectedName,
        ProgramIdentity expected)
    {
        string actualHash = Convert.ToHexString(SHA256.HashData(payload)).ToLowerInvariant();
        if (payload.Length != expected.Length ||
            !StringComparer.Ordinal.Equals(actualHash, expected.Sha256))
        {
            throw new InvalidDataException(
                $"The materialized Level 100 {expectedName} object is not the supported Steam payload.");
        }

        var reader = new Level100ObjectReader(payload);
        string objectName = reader.ReadString();
        if (!StringComparer.Ordinal.Equals(objectName, expectedName))
        {
            throw new InvalidDataException("The released script object name is invalid.");
        }

        int instructionCount = reader.ReadInt32();
        if (instructionCount is < 0 or > 20_000)
        {
            throw new InvalidDataException("The released script instruction count is invalid.");
        }

        var instructions = new Level100Instruction[instructionCount];
        for (int index = 0; index < instructions.Length; index++)
        {
            int opcode = reader.ReadInt32();
            int attribute = reader.ReadInt32();
            if ((uint)opcode > 0x1a)
            {
                throw new InvalidDataException($"Invalid opcode {opcode} at instruction {index}.");
            }

            instructions[index] = new Level100Instruction(opcode, attribute);
        }

        for (int index = 0; index < instructions.Length; index++)
        {
            Level100Instruction instruction = instructions[index];
            if (instruction.Opcode != 24)
            {
                continue;
            }

            int returnCount = (instruction.Attribute >> 16) & 0xff;
            if (returnCount is < 0 or > 1 ||
                (returnCount == 0 &&
                    (index + 1 >= instructions.Length || instructions[index + 1].Opcode != 14)))
            {
                throw new InvalidDataException(
                    $"Released {expectedName} native result ownership changed at instruction {index}.");
            }
        }

        var builtInEvents = new int[BuiltInEventCount];
        for (int index = 0; index < builtInEvents.Length; index++)
        {
            builtInEvents[index] = reader.ReadInt32();
            ValidateInstructionPointer(builtInEvents[index], instructionCount, "built-in event");
        }

        int symbolCount = reader.ReadInt32();
        if (symbolCount is < 0 or > 4_096)
        {
            throw new InvalidDataException("The released script symbol count is invalid.");
        }

        var symbols = new Level100Symbol[symbolCount];
        for (int index = 0; index < symbols.Length; index++)
        {
            string name = reader.ReadString();
            Level100ScriptValue value = reader.ReadValue();
            int owner = reader.ReadInt32();
            int ordinal = reader.ReadInt32();
            bool serialized = reader.ReadInt32() != 0;
            if (ordinal != index || !serialized)
            {
                throw new InvalidDataException($"Invalid symbol metadata at ordinal {index}.");
            }

            symbols[index] = new Level100Symbol(name, value, owner, ordinal);
        }

        if (reader.ReadInt32() != symbolCount)
        {
            throw new InvalidDataException("The released script symbol-table trailer is invalid.");
        }

        int namedEventCount = reader.ReadInt32();
        if (namedEventCount is < 0 or > 256)
        {
            throw new InvalidDataException("The released script named-event count is invalid.");
        }

        var events = new Dictionary<string, int>(namedEventCount, StringComparer.Ordinal);
        for (int index = 0; index < namedEventCount; index++)
        {
            int instructionPointer = reader.ReadInt32();
            int parameterCount = reader.ReadInt32();
            int symbolOrdinal = reader.ReadInt32();
            ValidateInstructionPointer(instructionPointer, instructionCount, "named event");
            if (instructionPointer < 0 || parameterCount != 1 || (uint)symbolOrdinal >= symbols.Length)
            {
                throw new InvalidDataException($"Invalid named event record {index}.");
            }

            string? name = symbols[symbolOrdinal].InitialValue.Text;
            if (symbols[symbolOrdinal].InitialValue.Type != Level100ScriptValueType.String ||
                string.IsNullOrEmpty(name) ||
                !events.TryAdd(name, instructionPointer))
            {
                throw new InvalidDataException($"Invalid named event symbol {symbolOrdinal}.");
            }
        }

        int debugMode = reader.ReadInt32();
        int runInitializer = reader.ReadInt32();
        if (debugMode != 0 || runInitializer is not (0 or 1) || !reader.End)
        {
            throw new InvalidDataException("The released script object trailer is invalid.");
        }

        if (StringComparer.Ordinal.Equals(expectedName, "LevelScript"))
        {
            if (instructions.Length != 884 || symbols.Length != 334 ||
                builtInEvents[0] != 11 || builtInEvents.Skip(1).Any(value => value != -1) ||
                events.Count != s_levelScriptEvents.Length || runInitializer != 1)
            {
                throw new InvalidDataException("The released LevelScript structure changed.");
            }

            foreach ((string name, int instructionPointer) in s_levelScriptEvents)
            {
                if (!events.TryGetValue(name, out int actual) || actual != instructionPointer)
                {
                    throw new InvalidDataException(
                        $"The released event '{name}' does not match instruction {instructionPointer}.");
                }
            }
        }

        return new Level100MissionProgram(
            objectName,
            actualHash,
            instructions,
            builtInEvents,
            symbols,
            events,
            runInitializer != 0);
    }

    private static void ValidateInstructionPointer(int value, int count, string owner)
    {
        if (value < -1 || value >= count)
        {
            throw new InvalidDataException($"The released {owner} instruction pointer is invalid.");
        }
    }

    private readonly record struct ProgramIdentity(int Length, string Sha256);

    private ref struct Level100ObjectReader
    {
        private readonly ReadOnlySpan<byte> _data;
        private int _offset;

        internal Level100ObjectReader(ReadOnlySpan<byte> data)
        {
            _data = data;
            _offset = 0;
        }

        internal bool End => _offset == _data.Length;

        internal int ReadInt32()
        {
            Ensure(4);
            int value = BinaryPrimitives.ReadInt32LittleEndian(_data[_offset..]);
            _offset += 4;
            return value;
        }

        internal string ReadString()
        {
            int length = ReadInt32();
            if (length < 0)
            {
                throw new InvalidDataException("A released script string has a negative length.");
            }

            Ensure(length);
            string value = Encoding.ASCII.GetString(_data.Slice(_offset, length));
            _offset += length;
            return value;
        }

        internal Level100ScriptValue ReadValue()
        {
            Level100ScriptValueType type = (Level100ScriptValueType)ReadInt32();
            return type switch
            {
                Level100ScriptValueType.Unset => Level100ScriptValue.Unset,
                Level100ScriptValueType.Integer => new(type, ReadInt32(), 0, 0, null),
                Level100ScriptValueType.Float => new(type, ReadInt32(), 0, 0, null),
                Level100ScriptValueType.String => new(type, 0, 0, 0, ReadString()),
                Level100ScriptValueType.Boolean => new(type, ReadInt32(), 0, 0, null),
                Level100ScriptValueType.Thing => new(type, ReadInt32(), 0, 0, null),
                Level100ScriptValueType.Position =>
                    new(type, ReadInt32(), ReadInt32(), ReadInt32(), null),
                _ => throw new InvalidDataException($"Unsupported script datatype {(int)type}."),
            };
        }

        private void Ensure(int length)
        {
            if (length > _data.Length - _offset)
            {
                throw new EndOfStreamException("The released script object is truncated.");
            }
        }
    }
}

internal readonly record struct Level100Instruction(int Opcode, int Attribute);

internal readonly record struct Level100Symbol(
    string Name,
    Level100ScriptValue InitialValue,
    int Owner,
    int Ordinal);

internal readonly record struct Level100ScriptValue(
    Level100ScriptValueType Type,
    int Scalar,
    int ComponentY,
    int ComponentZ,
    string? Text)
{
    internal static Level100ScriptValue Unset =>
        new(Level100ScriptValueType.Unset, 0, 0, 0, null);

    internal static Level100ScriptValue Integer(int value) =>
        new(Level100ScriptValueType.Integer, value, 0, 0, null);

    internal static Level100ScriptValue Float(float value) =>
        new(Level100ScriptValueType.Float, BitConverter.SingleToInt32Bits(value), 0, 0, null);

    internal static Level100ScriptValue String(string value) =>
        new(Level100ScriptValueType.String, 0, 0, 0, value);

    internal static Level100ScriptValue Boolean(bool value) =>
        new(Level100ScriptValueType.Boolean, value ? 1 : 0, 0, 0, null);

    internal static Level100ScriptValue NullThing =>
        new(Level100ScriptValueType.Thing, 0, 0, 0, null);

    internal static Level100ScriptValue Thing(Level100ActorId actorId, uint thingTypeMask) =>
        new(Level100ScriptValueType.Thing, actorId.Value, unchecked((int)thingTypeMask), 0, null);

    internal static Level100ScriptValue ExternalThing(uint thingTypeMask) =>
        new(Level100ScriptValueType.Thing, 0, unchecked((int)thingTypeMask), 0, null);

    internal int AsInteger() => Type switch
    {
        Level100ScriptValueType.Integer or Level100ScriptValueType.Boolean => Scalar,
        _ => throw new InvalidOperationException($"Expected integer-compatible value, got {Type}."),
    };

    internal float AsFloat() => Type switch
    {
        Level100ScriptValueType.Float => BitConverter.Int32BitsToSingle(Scalar),
        Level100ScriptValueType.Integer => Scalar,
        _ => throw new InvalidOperationException($"Expected numeric value, got {Type}."),
    };

    internal bool AsBoolean() => Type switch
    {
        Level100ScriptValueType.Boolean or Level100ScriptValueType.Integer => Scalar != 0,
        _ => throw new InvalidOperationException($"Expected boolean-compatible value, got {Type}."),
    };

    internal string AsString() => Type == Level100ScriptValueType.String
        ? Text ?? string.Empty
        : throw new InvalidOperationException($"Expected string-compatible value, got {Type}.");

    internal uint AsThingTypeMask() =>
        Type == Level100ScriptValueType.Thing
            ? unchecked((uint)ComponentY)
            : throw new InvalidOperationException($"Expected thing value, got {Type}.");

    internal Level100ActorId AsActorId() =>
        Type == Level100ScriptValueType.Thing && Scalar > 0
            ? new Level100ActorId(Scalar)
            : throw new InvalidOperationException("Expected a resolved actor reference.");

    internal Level100ScriptValueSnapshot Snapshot =>
        new(Type, Scalar, ComponentY, ComponentZ, Text);
}
