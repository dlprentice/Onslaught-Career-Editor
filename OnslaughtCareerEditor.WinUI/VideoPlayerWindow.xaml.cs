using System;
using System.IO;
using LibVLCSharp.Platforms.Windows;
using LibVLCSharp.Shared;
using Microsoft.UI.Text;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using VlcMedia = LibVLCSharp.Shared.Media;
using XamlBrush = Microsoft.UI.Xaml.Media.Brush;

namespace OnslaughtCareerEditor.WinUI
{
    public sealed class VideoPlayerWindow : Window
    {
        private readonly VideoView _videoView;
        private readonly TextBlock _statusTextBlock;

        private LibVLC? _libVlc;
        private MediaPlayer? _mediaPlayer;
        private string? _pendingMediaPath;
        private string? _currentMediaPath;
        private bool _isReady;
        private bool _isDisposed;
        private int _requestedVolume = 75;

        public event Action? PlaybackStateChanged;

        public VideoPlayerWindow()
        {
            Title = "Onslaught Career Editor - Video Player";

            _videoView = new VideoView
            {
                HorizontalAlignment = HorizontalAlignment.Stretch,
                VerticalAlignment = VerticalAlignment.Stretch,
            };
            _videoView.Initialized += VideoView_Initialized;

            _statusTextBlock = new TextBlock
            {
                Foreground = (XamlBrush)Application.Current.Resources["TextFillColorSecondaryBrush"],
                Text = "Preparing playback surface...",
                TextWrapping = TextWrapping.WrapWholeWords,
            };

            Content = BuildContent();
            Closed += VideoPlayerWindow_Closed;
        }

        public bool IsReady => _isReady && _mediaPlayer != null;
        public bool IsDisposed => _isDisposed;
        public bool IsPlaying => _mediaPlayer?.IsPlaying == true;
        public bool IsPaused => _mediaPlayer?.State == VLCState.Paused;
        public bool HasMediaLoaded => !string.IsNullOrWhiteSpace(CurrentMediaPath);
        public string? CurrentMediaPath => _pendingMediaPath ?? _currentMediaPath;
        public long CurrentTimeMs => Math.Max(0, _mediaPlayer?.Time ?? 0);
        public long LengthMs => Math.Max(0, _mediaPlayer?.Length ?? 0);

        public int Volume
        {
            get => _mediaPlayer?.Volume ?? _requestedVolume;
            set
            {
                _requestedVolume = Math.Clamp(value, 0, 100);
                if (_mediaPlayer != null)
                {
                    _mediaPlayer.Volume = _requestedVolume;
                }
            }
        }

        public void PlayFile(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                throw new ArgumentException("Video path is required.", nameof(path));
            }

            string fullPath = Path.GetFullPath(path);
            if (!File.Exists(fullPath))
            {
                throw new FileNotFoundException("The selected video file was not found.", fullPath);
            }

            if (!IsReady)
            {
                _pendingMediaPath = fullPath;
                _statusTextBlock.Text = "Preparing playback surface...";
                RaisePlaybackStateChanged();
                return;
            }

            PlayInternal(fullPath);
        }

        public void PauseOrResume()
        {
            if (_mediaPlayer == null)
            {
                return;
            }

            if (_mediaPlayer.IsPlaying)
            {
                _mediaPlayer.Pause();
            }
            else if (_mediaPlayer.State == VLCState.Paused)
            {
                _mediaPlayer.SetPause(false);
                _statusTextBlock.Text = "Playing video.";
                RaisePlaybackStateChanged();
            }
        }

        public void StopPlayback()
        {
            if (_mediaPlayer == null)
            {
                return;
            }

            if (_mediaPlayer.IsPlaying || _mediaPlayer.State == VLCState.Paused)
            {
                _mediaPlayer.Stop();
            }

            _statusTextBlock.Text = HasMediaLoaded ? "Video loaded and ready." : "Player ready.";
            RaisePlaybackStateChanged();
        }

        public void Seek(long timeMs)
        {
            if (_mediaPlayer == null)
            {
                return;
            }

            _mediaPlayer.Time = Math.Max(0, timeMs);
        }

        private UIElement BuildContent()
        {
            Grid root = new()
            {
                Background = (XamlBrush)Application.Current.Resources["ApplicationPageBackgroundThemeBrush"],
            };
            root.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            root.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });

            root.Children.Add(_videoView);

            Border footer = new()
            {
                Padding = new Thickness(16),
                BorderThickness = new Thickness(1),
                BorderBrush = (XamlBrush)Application.Current.Resources["CardStrokeColorDefaultBrush"],
                Background = (XamlBrush)Application.Current.Resources["LayerFillColorDefaultBrush"],
            };
            Grid.SetRow(footer, 1);

            StackPanel stack = new() { Spacing = 4 };
            stack.Children.Add(new TextBlock
            {
                FontSize = 18,
                FontWeight = FontWeights.SemiBold,
                Text = "Dedicated Video Window",
            });
            stack.Children.Add(new TextBlock
            {
                Text = "WinUI owns the playback surface here so the Media page can stay compact and the video viewport keeps its space.",
                TextWrapping = TextWrapping.WrapWholeWords,
            });
            stack.Children.Add(_statusTextBlock);
            footer.Child = stack;

            root.Children.Add(footer);
            return root;
        }

        private void VideoView_Initialized(object? sender, InitializedEventArgs e)
        {
            if (_isReady)
            {
                return;
            }

            try
            {
                Core.Initialize();
                _libVlc = new LibVLC(false, e.SwapChainOptions);
                _mediaPlayer = new MediaPlayer(_libVlc)
                {
                    Volume = _requestedVolume,
                };

                _mediaPlayer.Playing += MediaPlayer_Playing;
                _mediaPlayer.Paused += MediaPlayer_Paused;
                _mediaPlayer.Stopped += MediaPlayer_Stopped;
                _mediaPlayer.EndReached += MediaPlayer_EndReached;
                _mediaPlayer.EncounteredError += MediaPlayer_EncounteredError;
                _mediaPlayer.LengthChanged += MediaPlayer_LengthChanged;

                _videoView.MediaPlayer = _mediaPlayer;
                _isReady = true;
                _statusTextBlock.Text = "Player ready.";
                RaisePlaybackStateChanged();

                if (!string.IsNullOrWhiteSpace(_pendingMediaPath))
                {
                    string pendingPath = _pendingMediaPath;
                    _pendingMediaPath = null;
                    PlayInternal(pendingPath);
                }
            }
            catch (Exception ex)
            {
                _isReady = false;
                _statusTextBlock.Text = $"Video player initialization failed: {ex.Message}";
                RaisePlaybackStateChanged();
            }
        }

        private void PlayInternal(string path)
        {
            if (_libVlc == null || _mediaPlayer == null)
            {
                _pendingMediaPath = path;
                RaisePlaybackStateChanged();
                return;
            }

            using VlcMedia media = new(_libVlc, new Uri(path));
            if (!_mediaPlayer.Play(media))
            {
                throw new InvalidOperationException("LibVLC did not accept the selected video.");
            }

            _currentMediaPath = path;
            _pendingMediaPath = null;
            Title = $"Onslaught Career Editor - {Path.GetFileName(path)}";
            _statusTextBlock.Text = $"Opening {Path.GetFileName(path)}...";
            RaisePlaybackStateChanged();
        }

        private void MediaPlayer_Playing(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _statusTextBlock.Text = "Playing video.";
                RaisePlaybackStateChanged();
            });
        }

        private void MediaPlayer_Paused(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _statusTextBlock.Text = "Video paused.";
                RaisePlaybackStateChanged();
            });
        }

        private void MediaPlayer_Stopped(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _statusTextBlock.Text = HasMediaLoaded ? "Video stopped." : "Player ready.";
                RaisePlaybackStateChanged();
            });
        }

        private void MediaPlayer_EndReached(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _statusTextBlock.Text = "Playback finished.";
                RaisePlaybackStateChanged();
            });
        }

        private void MediaPlayer_EncounteredError(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _statusTextBlock.Text = "Playback error.";
                RaisePlaybackStateChanged();
            });
        }

        private void MediaPlayer_LengthChanged(object? sender, MediaPlayerLengthChangedEventArgs e)
        {
            DispatcherQueue.TryEnqueue(RaisePlaybackStateChanged);
        }

        private void VideoPlayerWindow_Closed(object sender, WindowEventArgs args)
        {
            _isDisposed = true;
            _videoView.Initialized -= VideoView_Initialized;

            if (_mediaPlayer != null)
            {
                _mediaPlayer.Playing -= MediaPlayer_Playing;
                _mediaPlayer.Paused -= MediaPlayer_Paused;
                _mediaPlayer.Stopped -= MediaPlayer_Stopped;
                _mediaPlayer.EndReached -= MediaPlayer_EndReached;
                _mediaPlayer.EncounteredError -= MediaPlayer_EncounteredError;
                _mediaPlayer.LengthChanged -= MediaPlayer_LengthChanged;
                _mediaPlayer.Dispose();
                _mediaPlayer = null;
            }

            _videoView.MediaPlayer = null;
            _libVlc?.Dispose();
            _libVlc = null;
            _isReady = false;
            RaisePlaybackStateChanged();
        }

        private void RaisePlaybackStateChanged()
        {
            PlaybackStateChanged?.Invoke();
        }
    }
}
