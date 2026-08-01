using System;
using System.IO;
using NAudio.Wave;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// Plays the trainer's music on a loop while the trainer is attached.
    ///
    /// The tune is synthesized rather than loaded, so there is no file and no packaged asset - the
    /// bytes come from <see cref="TrainerMusicSynth"/> and go straight into a reader. That also
    /// means switching tracks is a re-render, which at this size costs less than reading a file
    /// would.
    ///
    /// Everything here is disposable and idempotent. The trainer stops for reasons this class does
    /// not get told about - the mission ends, the game closes, the page is left - so
    /// <see cref="Stop"/> has to be safe to call at any time, from any of those paths, more than
    /// once.
    /// </summary>
    internal sealed class TrainerMusicPlayer : IDisposable
    {
        private readonly object _gate = new();
        private WaveOutEvent? _output;
        private LoopingWaveStream? _stream;
        private bool _disposed;

        public bool IsPlaying
        {
            get
            {
                lock (_gate)
                {
                    return _output is not null;
                }
            }
        }

        public TrainerMusicTrack Track { get; private set; } = TrainerMusicTrack.Ascent;

        /// <summary>Volume from 0 to 1. Applied live, so a slider can drive it.</summary>
        public float Volume
        {
            get => _volume;
            set
            {
                _volume = Math.Clamp(value, 0f, 1f);
                lock (_gate)
                {
                    if (_output is not null)
                    {
                        _output.Volume = _volume;
                    }
                }
            }
        }

        private float _volume = 0.5f;

        /// <summary>
        /// Start, or switch to a different track without a gap in the toggle's meaning. Returns
        /// false when audio could not be opened at all - a machine with no output device is an
        /// ordinary thing, and it must not take the trainer down with it.
        /// </summary>
        public bool Play(TrainerMusicTrack track)
        {
            lock (_gate)
            {
                ObjectDisposedException.ThrowIf(_disposed, this);
                StopCore();

                try
                {
                    byte[] wav = TrainerMusicSynth.Render(track);
                    _stream = new LoopingWaveStream(new WaveFileReader(new MemoryStream(wav)));
                    _output = new WaveOutEvent { Volume = _volume };
                    _output.Init(_stream);
                    _output.Play();
                    Track = track;
                    return true;
                }
                catch (Exception ex) when (ex is InvalidOperationException or NotSupportedException
                                            or ArgumentException or NAudio.MmException or IOException)
                {
                    StopCore();
                    return false;
                }
            }
        }

        public void Stop()
        {
            lock (_gate)
            {
                StopCore();
            }
        }

        private void StopCore()
        {
            try
            {
                _output?.Stop();
            }
            catch (Exception ex) when (ex is NAudio.MmException or InvalidOperationException)
            {
                // A device that has already gone is not a reason to fail a stop.
            }

            _output?.Dispose();
            _output = null;
            _stream?.Dispose();
            _stream = null;
        }

        public void Dispose()
        {
            lock (_gate)
            {
                if (_disposed)
                    return;

                _disposed = true;
                StopCore();
            }
        }

        /// <summary>
        /// Wraps a finite stream so reads never run out: at the end it seeks back to the start and
        /// keeps filling the buffer. NAudio has no built-in for this, and the alternative - handling
        /// PlaybackStopped and restarting - drops a buffer's worth of silence at every loop.
        /// </summary>
        private sealed class LoopingWaveStream : WaveStream
        {
            private readonly WaveStream _inner;

            public LoopingWaveStream(WaveStream inner)
            {
                _inner = inner ?? throw new ArgumentNullException(nameof(inner));
            }

            public override WaveFormat WaveFormat => _inner.WaveFormat;

            /// <summary>Effectively endless, which is what a loop is.</summary>
            public override long Length => long.MaxValue;

            public override long Position
            {
                get => _inner.Position;
                set => _inner.Position = value % Math.Max(1, _inner.Length);
            }

            public override int Read(byte[] buffer, int offset, int count)
            {
                int filled = 0;
                while (filled < count)
                {
                    int read = _inner.Read(buffer, offset + filled, count - filled);
                    if (read == 0)
                    {
                        if (_inner.Position == 0)
                        {
                            // An empty source would spin here forever.
                            break;
                        }

                        _inner.Position = 0;
                        continue;
                    }

                    filled += read;
                }

                return filled;
            }

            protected override void Dispose(bool disposing)
            {
                if (disposing)
                {
                    _inner.Dispose();
                }

                base.Dispose(disposing);
            }
        }
    }
}
