using System;
using System.Buffers.Binary;
using System.Collections.Generic;

namespace Onslaught___Career_Editor
{
    /// <summary>Which piece of music the trainer plays while it is holding.</summary>
    public enum TrainerMusicTrack
    {
        /// <summary>The default. Driving, major-key, the one that sounds like getting away with something.</summary>
        Ascent = 0,

        /// <summary>Slower, minor, fewer notes. For when the first one has been on for an hour.</summary>
        Drift = 1,
    }

    /// <summary>
    /// The trainer's music, generated rather than shipped.
    ///
    /// Trainers have had a soundtrack since the days when the people who wrote them were the same
    /// people writing demoscene music, and a trainer without one is missing something. But those
    /// tunes belong to the musicians who tracked them, and this project does not ship other
    /// people's work - so this composes its own, in the same spirit and by the same means the
    /// originals used: a handful of square waves, a noise channel, and a pattern table.
    ///
    /// Original to this project, and deliberately so. It borrows nothing from Battle Engine
    /// Aquila's soundtrack, which is the rights holders' - the app can play that too, from the
    /// player's own installation, and that is a different feature.
    ///
    /// It is synthesized on demand instead of being shipped as a file. A minute of audio is about
    /// two megabytes of download that never has to exist, and the same seed always produces the
    /// same bytes - <see cref="Render"/> is a pure function of the track, which is what makes it
    /// testable at all. The precedent is <c>tools/generate_app_icon.py</c>: original artwork,
    /// deterministic, generated rather than tracked.
    /// </summary>
    public static class TrainerMusicSynth
    {
        public const int SampleRate = 22050;

        /// <summary>16 bits, one channel. A chiptune does not need more and the memory shows.</summary>
        private const int BitsPerSample = 16;

        private const double Tau = Math.PI * 2;

        /// <summary>
        /// A pattern step. Note numbers are semitones above A2; -1 is a rest, which is as much of a
        /// tracker as this needs.
        /// </summary>
        private const int Rest = -1;

        /// <summary>
        /// Rendered WAV bytes for a track, ready to hand to a player. Deterministic.
        /// </summary>
        public static byte[] Render(TrainerMusicTrack track = TrainerMusicTrack.Ascent)
        {
            Composition composition = track switch
            {
                TrainerMusicTrack.Drift => Drift(),
                _ => Ascent(),
            };

            float[] samples = RenderSamples(composition);
            return ToWav(samples);
        }

        /// <summary>How long a track runs before it repeats.</summary>
        public static TimeSpan GetDuration(TrainerMusicTrack track = TrainerMusicTrack.Ascent)
        {
            Composition composition = track switch
            {
                TrainerMusicTrack.Drift => Drift(),
                _ => Ascent(),
            };

            return TimeSpan.FromSeconds(composition.TotalSteps * composition.SecondsPerStep);
        }

        public static string GetDisplayName(TrainerMusicTrack track) => track switch
        {
            TrainerMusicTrack.Drift => "Drift",
            _ => "Ascent",
        };

        // ------------------------------------------------------------------ the tunes

        /// <summary>
        /// Sixteen bars in A minor at 132 BPM: a walking bass, a triad arpeggio riding on top, and
        /// a lead that answers itself every four bars. The lead sits a fifth above the arp so the
        /// two never fight for the same frequency, which is the whole trick to making three square
        /// waves sound like more than three square waves.
        /// </summary>
        private static Composition Ascent()
        {
            // A minor: A C D E G. Semitones above A2. The low C is never played - the bass line
            // walks A-G-F-E and the melody takes C an octave up - so it is not bound here.
            const int a = 0, d = 5, e = 7, g = 10, aa = 12, cc = 15, dd = 17, ee = 19, gg = 22;

            int[] bass = Repeat(new[]
            {
                a, Rest, a, Rest, a, Rest, Rest, a,
                g, Rest, g, Rest, g, Rest, Rest, g,
                d, Rest, d, Rest, d, Rest, Rest, d,
                e, Rest, e, Rest, e, Rest, e, e,
            }, 4);

            int[] arp = Repeat(new[]
            {
                aa, cc, ee, cc, aa, cc, ee, cc,
                gg - 12, aa + 2, dd, aa + 2, gg - 12, aa + 2, dd, aa + 2,
                dd, gg - 12 + 5, aa + 2, gg - 12 + 5, dd, gg - 12 + 5, aa + 2, gg - 12 + 5,
                ee, gg, cc + 12, gg, ee, gg, cc + 12, gg,
            }, 4);

            int[] lead = Concat(
                Rests(32),
                new[]
                {
                    aa + 12, Rest, gg + 12 - 12, Rest, ee + 12, Rest, Rest, Rest,
                    dd + 12, Rest, ee + 12, Rest, gg + 12, Rest, Rest, Rest,
                    aa + 24, Rest, Rest, gg + 12, ee + 12, Rest, dd + 12, Rest,
                    cc + 12, Rest, dd + 12, Rest, ee + 12, Rest, Rest, Rest,
                },
                Rests(32),
                new[]
                {
                    ee + 12, Rest, dd + 12, Rest, cc + 12, Rest, aa + 12, Rest,
                    gg, Rest, aa + 12, Rest, cc + 12, Rest, Rest, Rest,
                    dd + 12, Rest, cc + 12, Rest, aa + 12, Rest, gg, Rest,
                    ee, Rest, Rest, Rest, Rest, Rest, Rest, Rest,
                });

            return new Composition(
                SecondsPerStep: 60.0 / 132.0 / 4.0,
                Bass: bass,
                Arp: arp,
                Lead: lead,
                HatEverySteps: 2,
                BassDuty: 0.5,
                ArpDuty: 0.25,
                LeadDuty: 0.5);
        }

        /// <summary>
        /// The one for the second hour. Same key, half the tempo, no lead - just the bass and a
        /// sparse arpeggio, so it sits under a game instead of on top of it.
        /// </summary>
        private static Composition Drift()
        {
            const int a = 0, c = 3, e = 7, g = 10, aa = 12, cc = 15, ee = 19;

            int[] bass = Repeat(new[]
            {
                a, Rest, Rest, Rest, Rest, Rest, Rest, Rest,
                c, Rest, Rest, Rest, Rest, Rest, Rest, Rest,
                g, Rest, Rest, Rest, Rest, Rest, Rest, Rest,
                e, Rest, Rest, Rest, Rest, Rest, Rest, Rest,
            }, 2);

            int[] arp = Repeat(new[]
            {
                aa, Rest, cc, Rest, ee, Rest, cc, Rest,
                cc, Rest, ee, Rest, aa + 12, Rest, ee, Rest,
                ee, Rest, aa + 12, Rest, cc + 12, Rest, aa + 12, Rest,
                cc + 12, Rest, aa + 12, Rest, ee, Rest, cc, Rest,
            }, 2);

            return new Composition(
                SecondsPerStep: 60.0 / 96.0 / 4.0,
                Bass: bass,
                Arp: arp,
                Lead: Rests(bass.Length),
                HatEverySteps: 8,
                BassDuty: 0.5,
                ArpDuty: 0.5,
                LeadDuty: 0.5);
        }

        // ------------------------------------------------------------------ the synth

        private sealed record Composition(
            double SecondsPerStep,
            int[] Bass,
            int[] Arp,
            int[] Lead,
            int HatEverySteps,
            double BassDuty,
            double ArpDuty,
            double LeadDuty)
        {
            public int TotalSteps => Math.Max(Bass.Length, Math.Max(Arp.Length, Lead.Length));
        }

        private static float[] RenderSamples(Composition composition)
        {
            int stepSamples = (int)(composition.SecondsPerStep * SampleRate);
            int total = composition.TotalSteps * stepSamples;
            float[] buffer = new float[total];

            // Each voice runs its own phase across the whole track rather than restarting per note,
            // so a repeated note does not click at every step boundary.
            double bassPhase = 0, arpPhase = 0, leadPhase = 0;
            uint noise = 0x1BADC0DE;

            for (int step = 0; step < composition.TotalSteps; step++)
            {
                int bassNote = NoteAt(composition.Bass, step);
                int arpNote = NoteAt(composition.Arp, step);
                int leadNote = NoteAt(composition.Lead, step);
                bool hat = composition.HatEverySteps > 0 && step % composition.HatEverySteps == 0;

                double bassHz = Frequency(bassNote, -12);
                double arpHz = Frequency(arpNote, 0);
                double leadHz = Frequency(leadNote, 0);

                for (int sample = 0; sample < stepSamples; sample++)
                {
                    int index = (step * stepSamples) + sample;
                    if (index >= total)
                        break;

                    double position = sample / (double)stepSamples;
                    float value = 0f;

                    if (bassHz > 0)
                    {
                        bassPhase += bassHz / SampleRate;
                        value += 0.30f * Pulse(bassPhase, composition.BassDuty) * (float)Envelope(position, 0.85);
                    }

                    if (arpHz > 0)
                    {
                        arpPhase += arpHz / SampleRate;
                        value += 0.16f * Pulse(arpPhase, composition.ArpDuty) * (float)Envelope(position, 0.45);
                    }

                    if (leadHz > 0)
                    {
                        leadPhase += leadHz / SampleRate;
                        value += 0.20f * Pulse(leadPhase, composition.LeadDuty) * (float)Envelope(position, 0.95);
                    }

                    if (hat)
                    {
                        // xorshift, so the noise is deterministic like everything else here.
                        noise ^= noise << 13;
                        noise ^= noise >> 17;
                        noise ^= noise << 5;
                        float white = ((noise & 0xFFFF) / 32768f) - 1f;
                        value += 0.05f * white * (float)Envelope(position, 0.08);
                    }

                    buffer[index] = Math.Clamp(value, -1f, 1f);
                }
            }

            ApplyLoopSeam(buffer);
            return buffer;
        }

        /// <summary>
        /// A short fade across the very start and end so the loop point does not click.
        ///
        /// The track is written to land on the bar line, but the three voices carry their phase
        /// across it and will not be at zero when the buffer ends. Two milliseconds is under a
        /// hundredth of a beat - inaudible as a fade, and the difference between a loop and a tick
        /// every twenty seconds.
        /// </summary>
        private static void ApplyLoopSeam(float[] buffer)
        {
            int seam = Math.Min(SampleRate / 500, buffer.Length / 4);
            if (seam <= 0)
                return;

            for (int index = 0; index < seam; index++)
            {
                float gain = index / (float)seam;
                buffer[index] *= gain;
                buffer[buffer.Length - 1 - index] *= gain;
            }
        }

        private static int NoteAt(int[] pattern, int step) =>
            pattern.Length == 0 ? Rest : pattern[step % pattern.Length];

        /// <summary>Equal temperament from A2 = 110 Hz. Rest returns 0, meaning silent.</summary>
        private static double Frequency(int semitonesAboveA2, int octaveShift)
        {
            if (semitonesAboveA2 < 0)
                return 0;

            return 110.0 * Math.Pow(2, (semitonesAboveA2 + octaveShift) / 12.0);
        }

        /// <summary>A square wave with a duty cycle. 0.5 is a square; 0.25 is the thinner one.</summary>
        private static float Pulse(double phase, double duty)
        {
            double fraction = phase - Math.Floor(phase);
            return fraction < duty ? 1f : -1f;
        }

        /// <summary>
        /// Percussive decay across one step. Not a real ADSR - a chiptune's envelope is closer to
        /// "loud then less loud", and the shorter the decay the more it reads as plucked.
        /// </summary>
        private static double Envelope(double position, double decay)
        {
            double value = Math.Exp(-position / Math.Max(0.01, decay) * 3.0);

            // Taper the last tenth to zero so notes do not butt into each other.
            if (position > 0.9)
                value *= (1.0 - position) / 0.1;

            return value;
        }

        // ------------------------------------------------------------------ the container

        /// <summary>A minimal RIFF/WAVE wrapper - 16-bit PCM, one channel.</summary>
        internal static byte[] ToWav(float[] samples)
        {
            ArgumentNullException.ThrowIfNull(samples);

            int dataBytes = samples.Length * 2;
            byte[] wav = new byte[44 + dataBytes];
            Span<byte> span = wav;

            "RIFF"u8.CopyTo(span[..4]);
            BinaryPrimitives.WriteUInt32LittleEndian(span.Slice(4, 4), (uint)(36 + dataBytes));
            "WAVE"u8.CopyTo(span.Slice(8, 4));
            "fmt "u8.CopyTo(span.Slice(12, 4));
            BinaryPrimitives.WriteUInt32LittleEndian(span.Slice(16, 4), 16);
            BinaryPrimitives.WriteUInt16LittleEndian(span.Slice(20, 2), 1);
            BinaryPrimitives.WriteUInt16LittleEndian(span.Slice(22, 2), 1);
            BinaryPrimitives.WriteUInt32LittleEndian(span.Slice(24, 4), SampleRate);
            BinaryPrimitives.WriteUInt32LittleEndian(span.Slice(28, 4), SampleRate * 2);
            BinaryPrimitives.WriteUInt16LittleEndian(span.Slice(32, 2), 2);
            BinaryPrimitives.WriteUInt16LittleEndian(span.Slice(34, 2), BitsPerSample);
            "data"u8.CopyTo(span.Slice(36, 4));
            BinaryPrimitives.WriteUInt32LittleEndian(span.Slice(40, 4), (uint)dataBytes);

            for (int index = 0; index < samples.Length; index++)
            {
                short value = (short)Math.Clamp(samples[index] * short.MaxValue, short.MinValue, short.MaxValue);
                BinaryPrimitives.WriteInt16LittleEndian(span.Slice(44 + (index * 2), 2), value);
            }

            return wav;
        }

        // ------------------------------------------------------------------ pattern helpers

        private static int[] Repeat(int[] pattern, int times)
        {
            var result = new List<int>(pattern.Length * times);
            for (int index = 0; index < times; index++)
                result.AddRange(pattern);

            return result.ToArray();
        }

        private static int[] Rests(int count)
        {
            int[] result = new int[count];
            Array.Fill(result, Rest);
            return result;
        }

        private static int[] Concat(params int[][] parts)
        {
            var result = new List<int>();
            foreach (int[] part in parts)
                result.AddRange(part);

            return result.ToArray();
        }
    }
}
