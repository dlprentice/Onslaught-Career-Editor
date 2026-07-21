// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

public sealed record ReplayResult(
    WorldSnapshot FinalState,
    string FinalStateHash,
    string TraceHash);

public static class ReplayRunner
{
    private static readonly byte[] s_traceHeader = CreateTraceHeader();

    public static ReplayResult Run(CommandTape tape)
    {
        ArgumentNullException.ThrowIfNull(tape);
        tape.Validate();

        var simulation = new Simulation(tape.Seed);
        using IncrementalHash trace = IncrementalHash.CreateHash(HashAlgorithmName.SHA256);
        trace.AppendData(s_traceHeader);
        int spanIndex = 0;
        WorldSnapshot state = simulation.Snapshot;
        for (int tick = 0; tick < tape.DurationTicks; tick++)
        {
            while (spanIndex < tape.Spans.Count && tape.Spans[spanIndex].EndTickExclusive <= tick)
            {
                spanIndex++;
            }

            SimInput input = SimInput.Idle;
            if (spanIndex < tape.Spans.Count)
            {
                CommandSpan span = tape.Spans[spanIndex];
                if (tick >= span.StartTick && tick < span.EndTickExclusive)
                {
                    input = span.ToInput();
                }
            }

            state = simulation.Step(input);
            trace.AppendData(CreateTraceEntry(tick, input, state));
        }

        return new ReplayResult(
            state,
            StateHasher.ComputeHex(state),
            Convert.ToHexString(trace.GetHashAndReset()).ToLowerInvariant());
    }

    private static byte[] CreateTraceHeader()
    {
        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(Encoding.ASCII.GetBytes("ONSLAUGHT-REBUILD-TRACE"));
            writer.Write(3);
        }

        return stream.ToArray();
    }

    private static byte[] CreateTraceEntry(int inputSlot, SimInput input, WorldSnapshot state)
    {
        byte[] stateBytes = StateHasher.GetCanonicalBytes(state);
        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(inputSlot);
            writer.Write(input.MoveX);
            writer.Write(input.MoveZ);
            writer.Write(input.LookX);
            writer.Write(input.LookY);
            writer.Write(input.LookXAnalogPermille);
            writer.Write(input.LookYAnalogPermille);
            writer.Write((byte)input.Actions);
            writer.Write(stateBytes.Length);
            writer.Write(stateBytes);
        }

        return stream.ToArray();
    }
}
