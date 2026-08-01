using System;
using System.Buffers.Binary;
using System.Linq;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The trainer's music, which the app composes rather than ships.
    ///
    /// Trainers have had a soundtrack since the people writing them were the people tracking
    /// demoscene music. Those tunes belong to their musicians, so this project writes its own with
    /// the same means the originals used - square waves, a noise channel, a pattern table - and
    /// synthesizes it on demand, so a minute of audio is download that never has to exist.
    ///
    /// Determinism is the load-bearing property here. It is what makes generated audio testable at
    /// all, and it is the same rule <c>tools/generate_app_icon.py</c> follows for the app's own
    /// original artwork.
    /// </summary>
    public sealed class TrainerMusicSynthTests
    {
        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void TheSameTrackAlwaysRendersTheSameBytes(TrainerMusicTrack track)
        {
            byte[] first = TrainerMusicSynth.Render(track);
            byte[] second = TrainerMusicSynth.Render(track);

            Assert.Equal(first, second);
        }

        [Fact]
        public void TheTwoTracksAreActuallyDifferentPiecesOfMusic()
        {
            Assert.NotEqual(
                TrainerMusicSynth.Render(TrainerMusicTrack.Ascent),
                TrainerMusicSynth.Render(TrainerMusicTrack.Drift));
        }

        /// <summary>
        /// A player is handed these bytes directly, so the container has to be right or the failure
        /// is a silent no-sound rather than an exception.
        /// </summary>
        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void ItIsARealWavFileWithAHeaderThatDescribesIt(TrainerMusicTrack track)
        {
            byte[] wav = TrainerMusicSynth.Render(track);

            Assert.True(wav.Length > 44, "There has to be audio after the header.");
            Assert.Equal("RIFF", System.Text.Encoding.ASCII.GetString(wav, 0, 4));
            Assert.Equal("WAVE", System.Text.Encoding.ASCII.GetString(wav, 8, 4));
            Assert.Equal("fmt ", System.Text.Encoding.ASCII.GetString(wav, 12, 4));
            Assert.Equal("data", System.Text.Encoding.ASCII.GetString(wav, 36, 4));

            Assert.Equal(1, BinaryPrimitives.ReadUInt16LittleEndian(wav.AsSpan(20, 2)));
            Assert.Equal(1, BinaryPrimitives.ReadUInt16LittleEndian(wav.AsSpan(22, 2)));
            Assert.Equal((uint)TrainerMusicSynth.SampleRate, BinaryPrimitives.ReadUInt32LittleEndian(wav.AsSpan(24, 4)));
            Assert.Equal(16, BinaryPrimitives.ReadUInt16LittleEndian(wav.AsSpan(34, 2)));

            // The two sizes in the header have to agree with the file that actually arrived.
            Assert.Equal((uint)(wav.Length - 8), BinaryPrimitives.ReadUInt32LittleEndian(wav.AsSpan(4, 4)));
            Assert.Equal((uint)(wav.Length - 44), BinaryPrimitives.ReadUInt32LittleEndian(wav.AsSpan(40, 4)));
        }

        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void TheRenderedLengthMatchesTheDurationItAdvertises(TrainerMusicTrack track)
        {
            byte[] wav = TrainerMusicSynth.Render(track);
            double renderedSeconds = (wav.Length - 44) / 2.0 / TrainerMusicSynth.SampleRate;

            Assert.Equal(TrainerMusicSynth.GetDuration(track).TotalSeconds, renderedSeconds, precision: 1);
        }

        /// <summary>
        /// Long enough not to feel like a ringtone, short enough not to be a download in memory.
        /// </summary>
        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void ATrackIsBetweenTenSecondsAndAMinute(TrainerMusicTrack track)
        {
            double seconds = TrainerMusicSynth.GetDuration(track).TotalSeconds;

            Assert.InRange(seconds, 10, 60);
        }

        /// <summary>
        /// It loops, so the join has to be silent at both ends. Without the seam fade the three
        /// voices carry their phase across the boundary and the loop ticks once every pass.
        /// </summary>
        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void ItStartsAndEndsNearSilenceSoTheLoopDoesNotClick(TrainerMusicTrack track)
        {
            short[] samples = ReadSamples(TrainerMusicSynth.Render(track));

            Assert.InRange(Math.Abs((int)samples[0]), 0, 400);
            Assert.InRange(Math.Abs((int)samples[^1]), 0, 400);
        }

        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void ThereIsActuallyMusicInIt(TrainerMusicTrack track)
        {
            short[] samples = ReadSamples(TrainerMusicSynth.Render(track));

            Assert.True(samples.Any(sample => Math.Abs((int)sample) > 3000), "The track is silent.");

            // Nothing may clip: a square-wave stack that sums past full scale sounds like a fault
            // rather than like a chiptune.
            Assert.DoesNotContain(samples, sample => sample == short.MaxValue || sample == short.MinValue);
        }

        /// <summary>
        /// A trainer tune that sits under a game must not be the loudest thing on the desktop.
        /// </summary>
        [Theory]
        [InlineData(TrainerMusicTrack.Ascent)]
        [InlineData(TrainerMusicTrack.Drift)]
        public void ItIsMixedWellBelowFullScale(TrainerMusicTrack track)
        {
            short[] samples = ReadSamples(TrainerMusicSynth.Render(track));
            double peak = samples.Max(sample => Math.Abs((int)sample)) / (double)short.MaxValue;

            Assert.InRange(peak, 0.1, 0.9);
        }

        [Fact]
        public void EveryTrackHasAName()
        {
            foreach (TrainerMusicTrack track in Enum.GetValues<TrainerMusicTrack>())
            {
                Assert.False(string.IsNullOrWhiteSpace(TrainerMusicSynth.GetDisplayName(track)));
            }
        }

        private static short[] ReadSamples(byte[] wav)
        {
            int count = (wav.Length - 44) / 2;
            short[] samples = new short[count];
            for (int index = 0; index < count; index++)
            {
                samples[index] = BinaryPrimitives.ReadInt16LittleEndian(wav.AsSpan(44 + (index * 2), 2));
            }

            return samples;
        }
    }
}
