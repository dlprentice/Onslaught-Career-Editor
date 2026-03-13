using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Threading;
using System.Threading.Tasks;
using LibVLCSharp.Shared;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Controls.Primitives;
using Microsoft.UI.Xaml.Input;
using Microsoft.UI.Xaml.Media;
using Microsoft.UI.Xaml.Media.Imaging;
using NAudio.Vorbis;
using NAudio.Wave;
using NAudio.Wave.SampleProviders;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;
using VlcMedia = LibVLCSharp.Shared.Media;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class MediaPage : Page
    {
        private const int AudioTabIndex = 0;
        private const int VideoTabIndex = 1;
        private const int VisualizerBarCount = 28;
        private static readonly string[] InlineVideoVlcOptions =
        {
            "--avcodec-hw=none",
            "--no-video-title-show",
            "--file-caching=1000",
            "--verbose=-1",
        };

        private readonly MediaCatalogService _catalogService = new();
        private readonly DispatcherTimer _audioTimer;
        private readonly DispatcherTimer _videoTimer;
        private readonly Dictionary<string, MediaAudioItem> _audioItemsByPath = new(StringComparer.OrdinalIgnoreCase);
        private readonly Dictionary<string, MediaVideoItem> _videoItemsByPath = new(StringComparer.OrdinalIgnoreCase);
        private readonly List<Border> _audioVisualizerBars = new();
        private readonly Queue<float> _audioVisualizerHistory = new();
        private readonly object _audioVisualizerLock = new();
        private readonly object _videoFrameLock = new();

        private MediaCatalogSnapshot _snapshot = MediaCatalogSnapshot.Empty;
        private MediaAudioItem? _selectedAudio;
        private MediaAudioItem? _currentAudioItem;
        private MediaVideoItem? _selectedVideo;
        private WaveOutEvent? _waveOut;
        private VorbisWaveReader? _vorbisReader;
        private SampleChannel? _sampleChannel;
        private LibVLC? _libVlc;
        private MediaPlayer? _videoPlayer;
        private WriteableBitmap? _videoBitmap;
        private byte[]? _videoFrameBytes;
        private IntPtr _videoFrameBuffer = IntPtr.Zero;
        private int _videoFrameBufferLength;
        private int _videoFrameWidth;
        private int _videoFrameHeight;
        private MediaPlayer.LibVLCVideoLockCb? _videoLockCallback;
        private MediaPlayer.LibVLCVideoUnlockCb? _videoUnlockCallback;
        private MediaPlayer.LibVLCVideoDisplayCb? _videoDisplayCallback;
        private MediaPlayer.LibVLCVideoFormatCb? _videoFormatCallback;
        private MediaPlayer.LibVLCVideoCleanupCb? _videoCleanupCallback;
        private string? _pendingVideoPath;
        private string? _currentVideoPath;
        private float _latestAudioMeterLevel;
        private bool _videoSurfaceReady;
        private bool _isStoppingAudio;
        private bool _isDraggingAudioSlider;
        private bool _isUpdatingAudioSlider;
        private bool _isDraggingVideoSlider;
        private bool _isUpdatingVideoSlider;
        private bool _hasLoaded;
        private bool _isLoading;
        private int _selectedMediaTabIndex;
        private int _videoFrameRenderQueued;

        public MediaPage()
        {
            InitializeComponent();

            _audioTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(100) };
            _audioTimer.Tick += AudioTimer_Tick;
            _videoTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(250) };
            _videoTimer.Tick += VideoTimer_Tick;
            BuildAudioVisualizerBars();
            ResetAudioVisualizer();

            Loaded += MediaPage_Loaded;
            Unloaded += MediaPage_Unloaded;
            AppConfigChangedService.ConfigChanged += HandleConfigChanged;
            AudioProgressSlider.AddHandler(UIElement.PointerPressedEvent, new PointerEventHandler(AudioProgressSlider_PointerPressed), true);
            AudioProgressSlider.AddHandler(UIElement.PointerReleasedEvent, new PointerEventHandler(AudioProgressSlider_PointerReleased), true);
            AudioProgressSlider.AddHandler(UIElement.PointerCanceledEvent, new PointerEventHandler(AudioProgressSlider_PointerCanceled), true);
            AudioProgressSlider.AddHandler(UIElement.PointerCaptureLostEvent, new PointerEventHandler(AudioProgressSlider_PointerCaptureLost), true);
            VideoProgressSlider.AddHandler(UIElement.PointerPressedEvent, new PointerEventHandler(VideoProgressSlider_PointerPressed), true);
            VideoProgressSlider.AddHandler(UIElement.PointerReleasedEvent, new PointerEventHandler(VideoProgressSlider_PointerReleased), true);
            VideoProgressSlider.AddHandler(UIElement.PointerCanceledEvent, new PointerEventHandler(VideoProgressSlider_PointerCanceled), true);
            VideoProgressSlider.AddHandler(UIElement.PointerCaptureLostEvent, new PointerEventHandler(VideoProgressSlider_PointerCaptureLost), true);

            AudioProgressSlider.Minimum = 0;
            AudioProgressSlider.Maximum = 1;
            VideoProgressSlider.Minimum = 0;
            VideoProgressSlider.Maximum = 1;
            AudioVolumeSlider.Value = 75;
            VideoVolumeSlider.Value = 75;
            AudioVolumeTextBlock.Text = $"{(int)AudioVolumeSlider.Value}%";
            VideoVolumeTextBlock.Text = $"{(int)VideoVolumeSlider.Value}%";

            int lastSubTab = AppConfig.Load().LastMediaSubTab;
            SelectMediaTab(lastSubTab, persistSelection: false);
            UpdateAudioControlsState();
            UpdateVideoControlsState();
        }

        private async void MediaPage_Loaded(object sender, RoutedEventArgs e)
        {
            EnsureInlineVideoPlayer();

            if (!_hasLoaded && !_isLoading)
            {
                await LoadMediaCatalogAsync();
            }

            RefreshPlaybackState();
            ApplyMediaPolicyNow(AppConfig.Load());
        }

        private void MediaPage_Unloaded(object sender, RoutedEventArgs e)
        {
            AppConfig config = AppConfig.Load();
            _audioTimer.Stop();
            _videoTimer.Stop();

            if (!config.AllowBackgroundAudio)
            {
                StopAudioPlayback();
            }

            if (!config.AllowBackgroundVideo)
            {
                StopVideoPlayback();
            }

            if (!config.AllowBackgroundVideo)
            {
                ReleaseVideoFrameResources();
                InlineVideoImage.Source = null;
                _videoBitmap = null;
            }
        }

        private void HandleConfigChanged(AppConfig config)
        {
            DispatcherQueue.TryEnqueue(async () =>
            {
                string? configuredGameDir = config.GetGameDir() ?? config.GameDirectory;
                if (!string.IsNullOrWhiteSpace(configuredGameDir) &&
                    !string.Equals(Path.GetFullPath(configuredGameDir), _snapshot.GameDirectory, StringComparison.OrdinalIgnoreCase))
                {
                    await LoadMediaCatalogAsync();
                }

                ApplyMediaPolicyNow(config);
            });
        }

        private async Task LoadMediaCatalogAsync()
        {
            if (_isLoading)
            {
                return;
            }

            _isLoading = true;
            MediaSummaryTextBlock.Text = "Loading media library...";
            AppStatusService.SetStatus("Media: loading library");

            try
            {
                AppConfig config = AppConfig.Load();
                string? gameDirectory = config.GetGameDir() ?? AppConfig.DetectGameDirectory();
                if (string.IsNullOrWhiteSpace(gameDirectory) || !MediaCatalogService.LooksLikeGameDirectory(gameDirectory))
                {
                    _snapshot = MediaCatalogSnapshot.Empty;
                    _hasLoaded = true;
                    ResetLibraryState();
                    MediaSummaryTextBlock.Text = "Game directory not set";
                    MediaGameDirectoryTextBlock.Text = "Set the game directory in Settings or browse here.";
                    AppStatusService.SetStatus("Media: game directory not configured");
                    return;
                }

                if (string.IsNullOrWhiteSpace(config.GetGameDir()))
                {
                    config.GameDirectory = gameDirectory;
                    config.Save();
                    App.MainWindowInstance?.RefreshFooter();
                }

                _snapshot = await Task.Run(() => _catalogService.Load(Path.GetFullPath(gameDirectory)));
                _hasLoaded = true;

                MediaGameDirectoryTextBlock.Text = _snapshot.GameDirectory;
                MediaSummaryTextBlock.Text = $"{_snapshot.AudioItems.Count} audio items, {_snapshot.VideoItems.Count} videos";

                ApplyAudioFilter();
                ApplyVideoFilter();
                RefreshPlaybackState();

                AppStatusService.SetStatus($"Media: {_snapshot.AudioItems.Count} audio items and {_snapshot.VideoItems.Count} videos ready");
            }
            catch (Exception ex)
            {
                _snapshot = MediaCatalogSnapshot.Empty;
                ResetLibraryState();
                MediaSummaryTextBlock.Text = "Media load failed";
                MediaGameDirectoryTextBlock.Text = ex.Message;
                AppStatusService.SetStatus("Media: load failed");
            }
            finally
            {
                _isLoading = false;
            }
        }

        private void ResetLibraryState()
        {
            _audioItemsByPath.Clear();
            _videoItemsByPath.Clear();
            AudioTreeView.RootNodes.Clear();
            VideoTreeView.RootNodes.Clear();
            SetSelectedAudio(null);
            SetSelectedVideo(null);
            StopAudioPlayback();
            StopVideoPlayback();
        }

        private void RefreshPlaybackState()
        {
            if (_waveOut?.PlaybackState == PlaybackState.Playing)
            {
                _audioTimer.Start();
            }
            else
            {
                _audioTimer.Stop();
            }

            if (_videoPlayer != null && (_videoPlayer.IsPlaying || _videoPlayer.State == VLCState.Paused || HasInlineVideoLoaded))
            {
                _videoTimer.Start();
            }
            else
            {
                _videoTimer.Stop();
            }

            UpdateAudioControlsState();
            UpdateVideoControlsState();
            UpdateAudioVisualizerState();
            UpdateVideoSurfaceState();
        }

        private bool HasInlineVideoLoaded => !string.IsNullOrWhiteSpace(_currentVideoPath);

        private void BuildAudioVisualizerBars()
        {
            AudioVisualizerBarsHost.Children.Clear();
            AudioVisualizerBarsHost.ColumnDefinitions.Clear();
            _audioVisualizerBars.Clear();

            for (int i = 0; i < VisualizerBarCount; i++)
            {
                AudioVisualizerBarsHost.ColumnDefinitions.Add(new ColumnDefinition());

                byte alpha = (byte)(120 + ((i % 4) * 20));
                Border bar = new()
                {
                    Margin = new Thickness(2, 0, 2, 0),
                    CornerRadius = new CornerRadius(4, 4, 0, 0),
                    VerticalAlignment = VerticalAlignment.Bottom,
                    Height = 180,
                    Background = new SolidColorBrush(Windows.UI.Color.FromArgb(alpha, 120, 170, 255)),
                    Opacity = 0.35,
                    RenderTransformOrigin = new Windows.Foundation.Point(0.5, 1),
                    RenderTransform = new ScaleTransform { ScaleY = 0.08 },
                };

                Grid.SetColumn(bar, i);
                AudioVisualizerBarsHost.Children.Add(bar);
                _audioVisualizerBars.Add(bar);
            }
        }

        private void PushAudioVisualizerSample(float level)
        {
            while (_audioVisualizerHistory.Count >= VisualizerBarCount)
            {
                _audioVisualizerHistory.Dequeue();
            }

            _audioVisualizerHistory.Enqueue(Math.Clamp(level, 0.03f, 1f));
        }

        private void RenderAudioVisualizer()
        {
            if (_audioVisualizerBars.Count == 0)
            {
                return;
            }

            float[] levels = _audioVisualizerHistory.ToArray();
            int leadingBlanks = Math.Max(0, _audioVisualizerBars.Count - levels.Length);

            for (int i = 0; i < _audioVisualizerBars.Count; i++)
            {
                float level = i < leadingBlanks ? 0.03f : levels[i - leadingBlanks];
                if (_audioVisualizerBars[i].RenderTransform is ScaleTransform transform)
                {
                    transform.ScaleY = Math.Clamp(0.08 + (level * 0.92), 0.08, 1.0);
                }

                _audioVisualizerBars[i].Opacity = 0.28 + (level * 0.72);
            }
        }

        private void ResetAudioVisualizer()
        {
            _audioVisualizerHistory.Clear();
            for (int i = 0; i < VisualizerBarCount; i++)
            {
                _audioVisualizerHistory.Enqueue(0.03f);
            }

            lock (_audioVisualizerLock)
            {
                _latestAudioMeterLevel = 0f;
            }

            RenderAudioVisualizer();
        }

        private void SampleChannel_PreVolumeMeter(object? sender, StreamVolumeEventArgs e)
        {
            float level = 0f;
            foreach (float sample in e.MaxSampleValues)
            {
                level = Math.Max(level, Math.Abs(sample));
            }

            lock (_audioVisualizerLock)
            {
                _latestAudioMeterLevel = Math.Clamp(level, 0f, 1f);
            }
        }

        private void UpdateAudioVisualizerState()
        {
            if (_currentAudioItem != null)
            {
                AudioVisualizerPlaceholderBorder.Visibility = Visibility.Collapsed;
                return;
            }

            AudioVisualizerPlaceholderBorder.Visibility = Visibility.Visible;
            if (_selectedAudio == null)
            {
                AudioVisualizerStatusTextBlock.Text = "Select a track";
                AudioVisualizerHintTextBlock.Text = "Choose a track from the library, then press Play or double-click it to begin.";
                return;
            }

            AudioVisualizerStatusTextBlock.Text = _selectedAudio.Name;
            AudioVisualizerHintTextBlock.Text = "Press Play or double-click the selected track to begin.";
        }

        private void EnsureInlineVideoPlayer()
        {
            if (_videoSurfaceReady && _videoPlayer != null && _libVlc != null)
            {
                return;
            }

            try
            {
                Core.Initialize();
                _libVlc ??= new LibVLC(false, InlineVideoVlcOptions);
                _videoPlayer ??= new MediaPlayer(_libVlc)
                {
                    Volume = (int)Math.Round(VideoVolumeSlider.Value),
                };

                if (!_videoSurfaceReady)
                {
                    _videoLockCallback = VideoBufferLock;
                    _videoUnlockCallback = VideoBufferUnlock;
                    _videoDisplayCallback = VideoBufferDisplay;
                    _videoFormatCallback = VideoBufferFormat;
                    _videoCleanupCallback = VideoBufferCleanup;

                    _videoPlayer.EnableMouseInput = false;
                    _videoPlayer.EnableKeyInput = false;
                    _videoPlayer.SetVideoCallbacks(_videoLockCallback, _videoUnlockCallback, _videoDisplayCallback);
                    _videoPlayer.SetVideoFormatCallbacks(_videoFormatCallback, _videoCleanupCallback);
                    _videoPlayer.Playing += VideoPlayer_Playing;
                    _videoPlayer.Paused += VideoPlayer_Paused;
                    _videoPlayer.Stopped += VideoPlayer_Stopped;
                    _videoPlayer.EndReached += VideoPlayer_EndReached;
                    _videoPlayer.EncounteredError += VideoPlayer_EncounteredError;
                    _videoPlayer.LengthChanged += VideoPlayer_LengthChanged;
                    _videoSurfaceReady = true;
                }

                RefreshPlaybackState();
                QueuePendingVideoPlayback();
            }
            catch (Exception ex)
            {
                _videoSurfaceReady = false;
                VideoPlaceholderBorder.Visibility = Visibility.Visible;
                VideoPlayerStatusTextBlock.Text = "Inline video unavailable";
                VideoPlaceholderBodyTextBlock.Text = ex.Message;
                AppStatusService.SetStatus("Media: video player initialization failed");
                UpdateVideoControlsState();
            }
        }

        private IntPtr VideoBufferLock(IntPtr opaque, IntPtr planes)
        {
            Monitor.Enter(_videoFrameLock);
            Marshal.WriteIntPtr(planes, _videoFrameBuffer);
            return IntPtr.Zero;
        }

        private void VideoBufferUnlock(IntPtr opaque, IntPtr picture, IntPtr planes)
        {
            Monitor.Exit(_videoFrameLock);
        }

        private void VideoBufferDisplay(IntPtr opaque, IntPtr picture)
        {
            if (Interlocked.Exchange(ref _videoFrameRenderQueued, 1) == 1)
            {
                return;
            }

            if (!DispatcherQueue.TryEnqueue(RenderInlineVideoFrame))
            {
                Interlocked.Exchange(ref _videoFrameRenderQueued, 0);
            }
        }

        private uint VideoBufferFormat(ref IntPtr opaque, IntPtr chroma, ref uint width, ref uint height, ref uint pitches, ref uint lines)
        {
            byte[] rv32 = { (byte)'R', (byte)'V', (byte)'3', (byte)'2' };
            Marshal.Copy(rv32, 0, chroma, rv32.Length);

            uint pitch = width * 4;
            int bufferLength = checked((int)(pitch * height));

            lock (_videoFrameLock)
            {
                ReleaseVideoFrameResourcesNoLock();
                _videoFrameBuffer = Marshal.AllocHGlobal(bufferLength);
                _videoFrameBytes = new byte[bufferLength];
                _videoFrameBufferLength = bufferLength;
                _videoFrameWidth = (int)width;
                _videoFrameHeight = (int)height;
            }

            pitches = pitch;
            lines = height;

            int pixelWidth = (int)width;
            int pixelHeight = (int)height;
            DispatcherQueue.TryEnqueue(() => EnsureVideoBitmap(pixelWidth, pixelHeight));
            return 1;
        }

        private void VideoBufferCleanup(ref IntPtr opaque)
        {
            lock (_videoFrameLock)
            {
                ReleaseVideoFrameResourcesNoLock();
            }

            DispatcherQueue.TryEnqueue(() =>
            {
                _videoBitmap = null;
                InlineVideoImage.Source = null;
            });
        }

        private void EnsureVideoBitmap(int width, int height)
        {
            if (width <= 0 || height <= 0)
            {
                return;
            }

            if (_videoBitmap != null &&
                _videoBitmap.PixelWidth == width &&
                _videoBitmap.PixelHeight == height)
            {
                return;
            }

            _videoBitmap = new WriteableBitmap(width, height);
            InlineVideoImage.Source = _videoBitmap;
        }

        private void RenderInlineVideoFrame()
        {
            try
            {
                WriteableBitmap? bitmap = _videoBitmap;
                byte[]? frameBytes = _videoFrameBytes;
                int frameLength = _videoFrameBufferLength;

                if (bitmap == null || frameBytes == null || _videoFrameBuffer == IntPtr.Zero || frameLength <= 0)
                {
                    return;
                }

                lock (_videoFrameLock)
                {
                    if (_videoFrameBuffer == IntPtr.Zero || _videoFrameBytes == null || _videoFrameBufferLength <= 0)
                    {
                        return;
                    }

                    Marshal.Copy(_videoFrameBuffer, frameBytes, 0, frameLength);
                }

                using Stream pixelStream = bitmap.PixelBuffer.AsStream();
                pixelStream.Position = 0;
                pixelStream.Write(frameBytes, 0, frameLength);
                bitmap.Invalidate();
            }
            finally
            {
                Interlocked.Exchange(ref _videoFrameRenderQueued, 0);
            }
        }

        private void ReleaseVideoFrameResources()
        {
            lock (_videoFrameLock)
            {
                ReleaseVideoFrameResourcesNoLock();
            }
        }

        private void ReleaseVideoFrameResourcesNoLock()
        {
            if (_videoFrameBuffer != IntPtr.Zero)
            {
                Marshal.FreeHGlobal(_videoFrameBuffer);
                _videoFrameBuffer = IntPtr.Zero;
            }

            _videoFrameBytes = null;
            _videoFrameBufferLength = 0;
            _videoFrameWidth = 0;
            _videoFrameHeight = 0;
        }

        private void QueuePendingVideoPlayback()
        {
            if (!_videoSurfaceReady || _videoPlayer == null || string.IsNullOrWhiteSpace(_pendingVideoPath))
            {
                UpdateVideoSurfaceState();
                return;
            }

            DispatcherQueue.TryEnqueue(() =>
            {
                if (!_videoSurfaceReady || _videoPlayer == null || string.IsNullOrWhiteSpace(_pendingVideoPath))
                {
                    UpdateVideoSurfaceState();
                    return;
                }

                string path = _pendingVideoPath!;
                _pendingVideoPath = null;

                try
                {
                    PlayInlineVideo(path);
                    AppStatusService.SetStatus(_selectedVideo == null
                        ? "Media: video playing"
                        : $"Media: playing {_selectedVideo.Name}");
                }
                catch (Exception ex)
                {
                    ResetVideoPlaybackState(stopPlayer: false);
                    VideoPathTextBlock.Text = ex.Message;
                    AppStatusService.SetStatus("Media: video playback failed");
                }
            });
        }

        private void PlayInlineVideo(string path)
        {
            if (_libVlc == null || _videoPlayer == null)
            {
                _pendingVideoPath = path;
                UpdateVideoSurfaceState();
                return;
            }

            using VlcMedia media = new(_libVlc, new Uri(path));
            if (!_videoPlayer.Play(media))
            {
                throw new InvalidOperationException("LibVLC did not accept the selected video.");
            }

            _currentVideoPath = path;
            _pendingVideoPath = null;
            UpdateVideoSurfaceState();
        }

        private void ResetVideoPlaybackState(bool stopPlayer)
        {
            _videoTimer.Stop();

            if (stopPlayer && _videoPlayer != null)
            {
                try
                {
                    if (_videoPlayer.IsPlaying || _videoPlayer.State == VLCState.Paused)
                    {
                        _videoPlayer.Stop();
                    }
                }
                catch
                {
                    // Native stop failures should never crash the page.
                }
            }

            _pendingVideoPath = null;
            _currentVideoPath = null;
            UpdateVideoControlsState();
            UpdateVideoSurfaceState();
        }

        private void UpdateVideoSurfaceState()
        {
            bool isReady = _videoSurfaceReady && _videoPlayer != null;
            bool isPlaying = _videoPlayer?.IsPlaying == true;
            bool isPaused = _videoPlayer?.State == VLCState.Paused;

            if (!isReady)
            {
                VideoPlaceholderBorder.Visibility = Visibility.Visible;
                VideoPlayerStatusTextBlock.Text = "Preparing inline player...";
                VideoPlaceholderBodyTextBlock.Text = "The playback surface is still initializing.";
                return;
            }

            if (isPlaying || isPaused)
            {
                VideoPlaceholderBorder.Visibility = Visibility.Collapsed;
                return;
            }

            VideoPlaceholderBorder.Visibility = Visibility.Visible;

            if (_selectedVideo == null)
            {
                VideoPlayerStatusTextBlock.Text = "Select a video";
                VideoPlaceholderBodyTextBlock.Text = "Choose a file from the library, then press Play or double-click it to start inline playback.";
                return;
            }

            VideoPlayerStatusTextBlock.Text = _selectedVideo.Name;
            VideoPlaceholderBodyTextBlock.Text = "Press Play or double-click the selected video to begin inline playback.";
        }

        private void VideoPlayer_Playing(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _videoTimer.Start();
                AppStatusService.SetStatus(_selectedVideo == null ? "Media: video playing" : $"Media: playing {_selectedVideo.Name}");
                RefreshPlaybackState();
            });
        }

        private void VideoPlayer_Paused(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                AppStatusService.SetStatus("Media: video paused");
                RefreshPlaybackState();
            });
        }

        private void VideoPlayer_Stopped(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                _currentVideoPath = null;
                RefreshPlaybackState();
            });
        }

        private void VideoPlayer_EndReached(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                ResetVideoPlaybackState(stopPlayer: false);
                AppStatusService.SetStatus("Media: video playback finished");
            });
        }

        private void VideoPlayer_EncounteredError(object? sender, EventArgs e)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                ResetVideoPlaybackState(stopPlayer: false);
                VideoPathTextBlock.Text = "Inline playback error.";
                AppStatusService.SetStatus("Media: video playback failed");
            });
        }

        private void VideoPlayer_LengthChanged(object? sender, MediaPlayerLengthChangedEventArgs e)
        {
            DispatcherQueue.TryEnqueue(RefreshPlaybackState);
        }

        private void ApplyAudioFilter()
        {
            string search = (AudioSearchTextBox.Text ?? string.Empty).Trim();
            bool expandGroups = !string.IsNullOrWhiteSpace(search);
            IEnumerable<MediaAudioItem> items = _snapshot.AudioItems;

            if (!string.IsNullOrWhiteSpace(search))
            {
                items = items.Where(item =>
                    item.Name.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    item.GroupName.Contains(search, StringComparison.OrdinalIgnoreCase));
            }

            List<MediaAudioItem> filtered = items.ToList();
            _audioItemsByPath.Clear();
            AudioTreeView.RootNodes.Clear();

            Dictionary<string, TreeViewNode> nodesByPath = new(StringComparer.OrdinalIgnoreCase);
            foreach (IGrouping<(int SortOrder, string GroupName), MediaAudioItem> group in filtered
                .GroupBy(static item => (item.GroupSortOrder, item.GroupName))
                .OrderBy(static group => group.Key.GroupSortOrder)
                .ThenBy(static group => group.Key.GroupName, StringComparer.OrdinalIgnoreCase))
            {
                List<MediaAudioItem> groupItems = group
                    .OrderBy(static item => item.Name, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                TreeViewNode groupNode = new()
                {
                    Content = new MediaTreeNodeTag($"{group.Key.GroupName} ({groupItems.Count})"),
                    IsExpanded = false
                };

                foreach (MediaAudioItem item in groupItems)
                {
                    string normalizedPath = NormalizeMediaPath(item.FilePath);
                    _audioItemsByPath[normalizedPath] = item;
                    TreeViewNode itemNode = new()
                    {
                        Content = new MediaTreeNodeTag(BuildAudioLeafLabel(item), normalizedPath),
                    };
                    groupNode.Children.Add(itemNode);
                    nodesByPath[normalizedPath] = itemNode;
                }

                AudioTreeView.RootNodes.Add(groupNode);
            }

            ApplyTreeExpansionState(AudioTreeView, expandGroups);

            if (_selectedAudio != null &&
                nodesByPath.TryGetValue(NormalizeMediaPath(_selectedAudio.FilePath), out TreeViewNode? selectedNode))
            {
                AudioTreeView.SelectedNode = selectedNode;
            }
            else if (_selectedAudio != null)
            {
                SetSelectedAudio(null);
            }
        }

        private void ApplyVideoFilter()
        {
            string search = (VideoSearchTextBox.Text ?? string.Empty).Trim();
            bool expandGroups = !string.IsNullOrWhiteSpace(search);
            IEnumerable<MediaVideoItem> items = _snapshot.VideoItems;

            if (!string.IsNullOrWhiteSpace(search))
            {
                items = items.Where(item =>
                    item.Name.Contains(search, StringComparison.OrdinalIgnoreCase) ||
                    item.SectionName.Contains(search, StringComparison.OrdinalIgnoreCase));
            }

            List<MediaVideoItem> filtered = items.ToList();
            _videoItemsByPath.Clear();
            VideoTreeView.RootNodes.Clear();

            Dictionary<string, TreeViewNode> nodesByPath = new(StringComparer.OrdinalIgnoreCase);
            foreach (IGrouping<(int SortOrder, string SectionName), MediaVideoItem> group in filtered
                .GroupBy(static item => (item.SectionSortOrder, item.SectionName))
                .OrderBy(static group => group.Key.SectionSortOrder)
                .ThenBy(static group => group.Key.SectionName, StringComparer.OrdinalIgnoreCase))
            {
                List<MediaVideoItem> groupItems = group
                    .OrderBy(static item => item.Name, StringComparer.OrdinalIgnoreCase)
                    .ToList();

                TreeViewNode groupNode = new()
                {
                    Content = new MediaTreeNodeTag($"{group.Key.SectionName} ({groupItems.Count})"),
                    IsExpanded = false
                };

                foreach (MediaVideoItem item in groupItems)
                {
                    string normalizedPath = NormalizeMediaPath(item.FilePath);
                    _videoItemsByPath[normalizedPath] = item;
                    TreeViewNode itemNode = new()
                    {
                        Content = new MediaTreeNodeTag(BuildVideoLeafLabel(item), normalizedPath),
                    };
                    groupNode.Children.Add(itemNode);
                    nodesByPath[normalizedPath] = itemNode;
                }

                VideoTreeView.RootNodes.Add(groupNode);
            }

            ApplyTreeExpansionState(VideoTreeView, expandGroups);

            if (_selectedVideo != null &&
                nodesByPath.TryGetValue(NormalizeMediaPath(_selectedVideo.FilePath), out TreeViewNode? selectedNode))
            {
                VideoTreeView.SelectedNode = selectedNode;
            }
            else if (_selectedVideo != null)
            {
                SetSelectedVideo(null);
            }
        }

        private void ApplyTreeExpansionState(TreeView treeView, bool expandGroups)
        {
            DispatcherQueue.TryEnqueue(() =>
            {
                foreach (TreeViewNode rootNode in treeView.RootNodes)
                {
                    rootNode.IsExpanded = expandGroups;
                }
            });
        }

        private static string BuildAudioLeafLabel(MediaAudioItem item)
        {
            return string.IsNullOrWhiteSpace(item.DurationLabel)
                ? item.Name
                : $"{item.Name}   {item.DurationLabel}";
        }

        private static string BuildVideoLeafLabel(MediaVideoItem item)
        {
            return string.IsNullOrWhiteSpace(item.SizeText)
                ? item.Name
                : $"{item.Name}   {item.SizeText}";
        }

        private static string NormalizeMediaPath(string filePath)
        {
            return Path.GetFullPath(filePath);
        }

        private static MediaTreeNodeTag? TryGetTreeTag(object? item)
        {
            return item switch
            {
                TreeViewNode node => node.Content as MediaTreeNodeTag,
                MediaTreeNodeTag tag => tag,
                _ => null,
            };
        }

        private bool TryGetAudioItem(object? source, out MediaAudioItem? item)
        {
            item = null;
            MediaTreeNodeTag? tag = TryGetTreeTag(source);
            if (tag?.FilePath == null)
            {
                return false;
            }

            return _audioItemsByPath.TryGetValue(tag.FilePath, out item);
        }

        private bool TryGetVideoItem(object? source, out MediaVideoItem? item)
        {
            item = null;
            MediaTreeNodeTag? tag = TryGetTreeTag(source);
            if (tag?.FilePath == null)
            {
                return false;
            }

            return _videoItemsByPath.TryGetValue(tag.FilePath, out item);
        }

        private void SetSelectedAudio(MediaAudioItem? item)
        {
            _selectedAudio = item;
            AudioNowPlayingTextBlock.Text = item?.Name ?? "No track selected";
            AudioPathTextBlock.Text = item?.FilePath ?? "Select a track from the left to start playback.";
            UpdateAudioControlsState();
            UpdateAudioVisualizerState();
        }

        private void SetSelectedVideo(MediaVideoItem? item)
        {
            _selectedVideo = item;
            VideoSelectedTextBlock.Text = item?.Name ?? "No video selected";
            VideoPathTextBlock.Text = item?.FilePath ?? "Select a video from the left to start playback or reveal the file in Explorer.";
            UpdateVideoControlsState();
            UpdateVideoSurfaceState();
        }

        private void UpdateAudioControlsState()
        {
            bool isPlaying = _waveOut?.PlaybackState == PlaybackState.Playing;
            bool isPaused = _waveOut?.PlaybackState == PlaybackState.Paused;
            bool selectedIsCurrent = _selectedAudio != null &&
                                     _currentAudioItem != null &&
                                     string.Equals(_selectedAudio.FilePath, _currentAudioItem.FilePath, StringComparison.OrdinalIgnoreCase);
            bool hasActiveTrack = _currentAudioItem != null && _vorbisReader != null;

            AudioPlayButton.IsEnabled = _selectedAudio != null && (!selectedIsCurrent || (!isPlaying && !isPaused));
            AudioPauseButton.IsEnabled = isPlaying || isPaused;
            AudioStopButton.IsEnabled = isPlaying || isPaused;
            AudioProgressSlider.IsEnabled = hasActiveTrack;
        }

        private void UpdateVideoControlsState()
        {
            bool isReady = _videoSurfaceReady && _videoPlayer != null;
            bool isPlaying = _videoPlayer?.IsPlaying == true;
            bool isPaused = _videoPlayer?.State == VLCState.Paused;
            bool hasMediaLoaded = HasInlineVideoLoaded;

            VideoPlayButton.IsEnabled = _selectedVideo != null && !isPlaying;
            VideoPauseButton.IsEnabled = isReady && hasMediaLoaded && (isPlaying || isPaused);
            VideoStopButton.IsEnabled = isReady && hasMediaLoaded;
            RevealVideoButton.IsEnabled = _selectedVideo != null;
            VideoProgressSlider.IsEnabled = isReady && hasMediaLoaded;
            VideoPauseButton.Content = isPaused ? "Resume" : "Pause";

            if (!isReady || !hasMediaLoaded)
            {
                VideoCurrentTimeTextBlock.Text = "0:00";
                VideoTotalTimeTextBlock.Text = "0:00";
                VideoProgressSlider.Maximum = 1;
                if (!_isDraggingVideoSlider)
                {
                    VideoProgressSlider.Value = 0;
                }
            }
        }

        private void StartAudioPlayback(MediaAudioItem item)
        {
            if (AppConfig.Load().PreventAudioVideoOverlap)
            {
                StopVideoPlayback();
            }

            StopAudioPlayback();

            _vorbisReader = new VorbisWaveReader(item.FilePath);
            _sampleChannel = new SampleChannel(_vorbisReader, forceStereo: true);
            _sampleChannel.PreVolumeMeter += SampleChannel_PreVolumeMeter;
            _waveOut = new WaveOutEvent();
            _waveOut.Init(new SampleToWaveProvider16(_sampleChannel));
            _waveOut.Volume = (float)(AudioVolumeSlider.Value / 100.0);
            _waveOut.PlaybackStopped += WaveOut_PlaybackStopped;

            _currentAudioItem = item;
            ResetAudioVisualizer();
            AudioProgressSlider.Maximum = Math.Max(1, _vorbisReader.TotalTime.TotalSeconds);
            AudioProgressSlider.IsEnabled = true;
            AudioCurrentTimeTextBlock.Text = "0:00";
            AudioTotalTimeTextBlock.Text = FormatTime(_vorbisReader.TotalTime);
            AudioPauseButton.Content = "Pause";

            _waveOut.Play();
            _audioTimer.Start();

            UpdateAudioControlsState();
            UpdateAudioVisualizerState();
            AppStatusService.SetStatus($"Media: playing {item.Name}");
        }

        public void StopAudioPlayback()
        {
            _audioTimer.Stop();

            if (_waveOut != null)
            {
                _isStoppingAudio = true;
                _waveOut.PlaybackStopped -= WaveOut_PlaybackStopped;

                try
                {
                    if (_waveOut.PlaybackState != PlaybackState.Stopped)
                    {
                        _waveOut.Stop();
                    }
                }
                catch
                {
                    // Best effort only.
                }

                _isStoppingAudio = false;
                _waveOut.Dispose();
                _waveOut = null;
            }

            _vorbisReader?.Dispose();
            _vorbisReader = null;
            if (_sampleChannel != null)
            {
                _sampleChannel.PreVolumeMeter -= SampleChannel_PreVolumeMeter;
                _sampleChannel = null;
            }
            _currentAudioItem = null;
            ResetAudioVisualizer();

            AudioPauseButton.Content = "Pause";
            AudioCurrentTimeTextBlock.Text = "0:00";
            AudioProgressSlider.IsEnabled = false;
            AudioProgressSlider.Value = 0;
            AudioTotalTimeTextBlock.Text = _selectedAudio?.DurationLabel ?? "0:00";
            UpdateAudioControlsState();
            UpdateAudioVisualizerState();
        }

        public void StopVideoPlayback()
        {
            ResetVideoPlaybackState(stopPlayer: true);
        }

        private void StartVideoPlayback(MediaVideoItem item)
        {
            if (AppConfig.Load().PreventAudioVideoOverlap)
            {
                StopAudioPlayback();
            }

            string fullPath = Path.GetFullPath(item.FilePath);
            if (!File.Exists(fullPath))
            {
                throw new FileNotFoundException("The selected video file was not found.", fullPath);
            }

            EnsureInlineVideoPlayer();
            _pendingVideoPath = fullPath;

            if (!_videoSurfaceReady)
            {
                UpdateVideoSurfaceState();
                AppStatusService.SetStatus("Media: preparing inline video surface");
                return;
            }

            if (_videoPlayer == null)
            {
                throw new InvalidOperationException("Inline video surface is not ready.");
            }

            _videoPlayer.Volume = (int)Math.Round(VideoVolumeSlider.Value);
            QueuePendingVideoPlayback();
        }

        private void ApplyMediaPolicyNow(AppConfig config)
        {
            if (!config.AllowBackgroundAudio &&
                _selectedMediaTabIndex != AudioTabIndex)
            {
                StopAudioPlayback();
            }

            if (!config.AllowBackgroundVideo &&
                _selectedMediaTabIndex != VideoTabIndex)
            {
                StopVideoPlayback();
            }

            if (config.PreventAudioVideoOverlap &&
                _waveOut?.PlaybackState == PlaybackState.Playing &&
                _videoPlayer?.IsPlaying == true)
            {
                StopVideoPlayback();
            }

            if (_videoPlayer != null)
            {
                _videoPlayer.Volume = (int)Math.Round(VideoVolumeSlider.Value);
            }

            RefreshPlaybackState();
        }

        private void AudioTimer_Tick(object? sender, object e)
        {
            float levelSnapshot;
            lock (_audioVisualizerLock)
            {
                levelSnapshot = _latestAudioMeterLevel;
                _latestAudioMeterLevel *= 0.7f;
            }

            PushAudioVisualizerSample(levelSnapshot);
            RenderAudioVisualizer();

            if (_vorbisReader == null || _waveOut == null)
            {
                return;
            }

            if (!_isDraggingAudioSlider)
            {
                _isUpdatingAudioSlider = true;
                AudioProgressSlider.Value = Math.Min(AudioProgressSlider.Maximum, _vorbisReader.CurrentTime.TotalSeconds);
                _isUpdatingAudioSlider = false;
            }
            AudioCurrentTimeTextBlock.Text = FormatTime(_vorbisReader.CurrentTime);
        }

        private void VideoTimer_Tick(object? sender, object e)
        {
            if (_videoPlayer == null)
            {
                _videoTimer.Stop();
                UpdateVideoControlsState();
                return;
            }

            long currentTimeMs = Math.Max(0, _videoPlayer.Time);
            long totalTimeMs = Math.Max(currentTimeMs, _videoPlayer.Length);

            if (!_isDraggingVideoSlider)
            {
                _isUpdatingVideoSlider = true;
                VideoProgressSlider.Maximum = Math.Max(1, totalTimeMs / 1000.0);
                VideoProgressSlider.Value = Math.Min(VideoProgressSlider.Maximum, currentTimeMs / 1000.0);
                _isUpdatingVideoSlider = false;
            }

            VideoCurrentTimeTextBlock.Text = FormatTime(TimeSpan.FromMilliseconds(currentTimeMs));
            VideoTotalTimeTextBlock.Text = FormatTime(TimeSpan.FromMilliseconds(totalTimeMs));
            UpdateVideoControlsState();
        }

        private void WaveOut_PlaybackStopped(object? sender, StoppedEventArgs e)
        {
            if (_isStoppingAudio)
            {
                return;
            }

            DispatcherQueue.TryEnqueue(() =>
            {
                StopAudioPlayback();
                AppStatusService.SetStatus(e.Exception == null ? "Media: audio playback finished" : "Media: audio playback error");
            });
        }

        private async void BrowseGameDirectoryButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
            if (string.IsNullOrWhiteSpace(path))
            {
                return;
            }

            if (!MediaCatalogService.LooksLikeGameDirectory(path))
            {
                AppStatusService.SetStatus("Media: selected folder does not look like a game install");
                return;
            }

            AppConfig config = AppConfig.Load();
            config.GameDirectory = path;
            config.Save();
            AppConfigChangedService.NotifyChanged(config);
            App.MainWindowInstance.RefreshFooter();
            MediaGameDirectoryTextBlock.Text = path;
            AppStatusService.SetStatus("Media: game directory selected");
            await LoadMediaCatalogAsync();
        }

        private async void ReloadLibraryButton_Click(object sender, RoutedEventArgs e)
        {
            await LoadMediaCatalogAsync();
        }

        private void AudioTabButton_Click(object sender, RoutedEventArgs e)
        {
            SelectMediaTab(AudioTabIndex);
        }

        private void VideoTabButton_Click(object sender, RoutedEventArgs e)
        {
            SelectMediaTab(VideoTabIndex);
        }

        private void SelectMediaTab(int tabIndex, bool persistSelection = true)
        {
            tabIndex = tabIndex == VideoTabIndex ? VideoTabIndex : AudioTabIndex;
            _selectedMediaTabIndex = tabIndex;

            AudioTabContentGrid.Visibility = tabIndex == AudioTabIndex ? Visibility.Visible : Visibility.Collapsed;
            VideoTabContentGrid.Visibility = tabIndex == VideoTabIndex ? Visibility.Visible : Visibility.Collapsed;

            if (Resources.TryGetValue(tabIndex == AudioTabIndex ? "MediaActiveTabButtonStyle" : "MediaInactiveTabButtonStyle", out object? audioStyle) &&
                audioStyle is Style audioButtonStyle)
            {
                AudioTabButton.Style = audioButtonStyle;
            }

            if (Resources.TryGetValue(tabIndex == VideoTabIndex ? "MediaActiveTabButtonStyle" : "MediaInactiveTabButtonStyle", out object? videoStyle) &&
                videoStyle is Style videoButtonStyle)
            {
                VideoTabButton.Style = videoButtonStyle;
            }

            AppConfig config = AppConfig.Load();
            if (persistSelection && config.LastMediaSubTab != tabIndex)
            {
                config.LastMediaSubTab = tabIndex;
                config.Save();
            }

            if (tabIndex == VideoTabIndex)
            {
                EnsureInlineVideoPlayer();
                QueuePendingVideoPlayback();
            }

            ApplyMediaPolicyNow(config);
        }

        private void AudioSearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            ApplyAudioFilter();
        }

        private void VideoSearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            ApplyVideoFilter();
        }

        private void AudioTreeView_SelectionChanged(TreeView sender, TreeViewSelectionChangedEventArgs args)
        {
            if (TryGetAudioItem(sender.SelectedNode, out MediaAudioItem? item) && item != null)
            {
                SetSelectedAudio(item);
                AppStatusService.SetStatus($"Media: selected {item.Name}");
            }
            else
            {
                SetSelectedAudio(null);
            }
        }

        private void AudioTreeView_ItemInvoked(TreeView sender, TreeViewItemInvokedEventArgs args)
        {
            if (TryGetAudioItem(args.InvokedItem, out MediaAudioItem? item) && item != null)
            {
                SetSelectedAudio(item);
                AppStatusService.SetStatus($"Media: selected {item.Name}");
            }
        }

        private void VideoTreeView_SelectionChanged(TreeView sender, TreeViewSelectionChangedEventArgs args)
        {
            if (TryGetVideoItem(sender.SelectedNode, out MediaVideoItem? item) && item != null)
            {
                SetSelectedVideo(item);
                AppStatusService.SetStatus($"Media: selected {item.Name}");
            }
            else
            {
                SetSelectedVideo(null);
            }
        }

        private void VideoTreeView_ItemInvoked(TreeView sender, TreeViewItemInvokedEventArgs args)
        {
            if (TryGetVideoItem(args.InvokedItem, out MediaVideoItem? item) && item != null)
            {
                SetSelectedVideo(item);
                AppStatusService.SetStatus($"Media: selected {item.Name}");
            }
        }

        private void AudioTreeView_DoubleTapped(object sender, DoubleTappedRoutedEventArgs e)
        {
            if (_selectedAudio == null)
            {
                return;
            }

            try
            {
                StartAudioPlayback(_selectedAudio);
            }
            catch (Exception ex)
            {
                StopAudioPlayback();
                AudioPathTextBlock.Text = ex.Message;
                AppStatusService.SetStatus("Media: audio playback failed");
            }
        }

        private void VideoTreeView_DoubleTapped(object sender, DoubleTappedRoutedEventArgs e)
        {
            if (_selectedVideo == null)
            {
                return;
            }

            try
            {
                StartVideoPlayback(_selectedVideo);
            }
            catch (Exception ex)
            {
                StopVideoPlayback();
                VideoPathTextBlock.Text = ex.Message;
                AppStatusService.SetStatus("Media: video playback failed");
            }
        }

        private void AudioPlayButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedAudio == null)
            {
                AppStatusService.SetStatus("Media: no audio track selected");
                return;
            }

            try
            {
                StartAudioPlayback(_selectedAudio);
            }
            catch (Exception ex)
            {
                StopAudioPlayback();
                AudioPathTextBlock.Text = ex.Message;
                AppStatusService.SetStatus("Media: audio playback failed");
            }
        }

        private void AudioPauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (_waveOut == null)
            {
                return;
            }

            if (_waveOut.PlaybackState == PlaybackState.Playing)
            {
                _waveOut.Pause();
                _audioTimer.Stop();
                AudioPauseButton.Content = "Resume";
                AppStatusService.SetStatus("Media: audio paused");
            }
            else if (_waveOut.PlaybackState == PlaybackState.Paused)
            {
                _waveOut.Play();
                _audioTimer.Start();
                AudioPauseButton.Content = "Pause";
                AppStatusService.SetStatus(_currentAudioItem == null ? "Media: audio resumed" : $"Media: resumed {_currentAudioItem.Name}");
            }

            UpdateAudioControlsState();
        }

        private void AudioStopButton_Click(object sender, RoutedEventArgs e)
        {
            StopAudioPlayback();
            AppStatusService.SetStatus("Media: audio stopped");
        }

        private void AudioVolumeSlider_ValueChanged(object sender, RangeBaseValueChangedEventArgs e)
        {
            int volume = (int)Math.Round(AudioVolumeSlider.Value);
            if (AudioVolumeTextBlock != null)
            {
                AudioVolumeTextBlock.Text = $"{volume}%";
            }
            if (_waveOut != null)
            {
                _waveOut.Volume = volume / 100f;
            }
        }

        private void AudioProgressSlider_PointerPressed(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingAudioSlider = true;
        }

        private void AudioProgressSlider_PointerReleased(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingAudioSlider = false;
            SeekAudioToSlider();
        }

        private void AudioProgressSlider_PointerCanceled(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingAudioSlider = false;
        }

        private void AudioProgressSlider_PointerCaptureLost(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingAudioSlider = false;
        }

        private void AudioProgressSlider_ValueChanged(object sender, RangeBaseValueChangedEventArgs e)
        {
            if (_isUpdatingAudioSlider)
            {
                return;
            }

            if (_isDraggingAudioSlider)
            {
                AudioCurrentTimeTextBlock.Text = FormatTime(TimeSpan.FromSeconds(AudioProgressSlider.Value));
            }
            else if (_vorbisReader != null && AudioProgressSlider.IsEnabled)
            {
                SeekAudioToSlider();
            }
        }

        private void SeekAudioToSlider()
        {
            if (_vorbisReader == null || !AudioProgressSlider.IsEnabled)
            {
                return;
            }

            double seconds = Math.Clamp(AudioProgressSlider.Value, 0, AudioProgressSlider.Maximum);
            _vorbisReader.CurrentTime = TimeSpan.FromSeconds(seconds);
            AudioCurrentTimeTextBlock.Text = FormatTime(_vorbisReader.CurrentTime);
        }

        private void VideoPlayButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedVideo == null)
            {
                AppStatusService.SetStatus("Media: no video selected");
                return;
            }

            try
            {
                StartVideoPlayback(_selectedVideo);
            }
            catch (Exception ex)
            {
                StopVideoPlayback();
                VideoPathTextBlock.Text = ex.Message;
                AppStatusService.SetStatus("Media: video playback failed");
            }
        }

        private void VideoPauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (_videoPlayer == null)
            {
                return;
            }

            if (_videoPlayer.IsPlaying)
            {
                _videoPlayer.Pause();
            }
            else if (_videoPlayer.State == VLCState.Paused)
            {
                _videoPlayer.SetPause(false);
                AppStatusService.SetStatus("Media: video resumed");
            }

            RefreshPlaybackState();
        }

        private void VideoStopButton_Click(object sender, RoutedEventArgs e)
        {
            StopVideoPlayback();
            AppStatusService.SetStatus("Media: video stopped");
        }

        private void VideoVolumeSlider_ValueChanged(object sender, RangeBaseValueChangedEventArgs e)
        {
            int volume = (int)Math.Round(VideoVolumeSlider.Value);
            if (VideoVolumeTextBlock != null)
            {
                VideoVolumeTextBlock.Text = $"{volume}%";
            }
            if (_videoPlayer != null)
            {
                _videoPlayer.Volume = volume;
            }
        }

        private void VideoProgressSlider_PointerPressed(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingVideoSlider = true;
        }

        private void VideoProgressSlider_PointerReleased(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingVideoSlider = false;
            SeekVideoToSlider();
        }

        private void VideoProgressSlider_PointerCanceled(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingVideoSlider = false;
        }

        private void VideoProgressSlider_PointerCaptureLost(object sender, PointerRoutedEventArgs e)
        {
            _isDraggingVideoSlider = false;
        }

        private void VideoProgressSlider_ValueChanged(object sender, RangeBaseValueChangedEventArgs e)
        {
            if (_isUpdatingVideoSlider)
            {
                return;
            }

            if (_videoPlayer == null || !VideoProgressSlider.IsEnabled)
            {
                return;
            }

            if (_isDraggingVideoSlider)
            {
                VideoCurrentTimeTextBlock.Text = FormatTime(TimeSpan.FromSeconds(VideoProgressSlider.Value));
            }
            else
            {
                SeekVideoToSlider();
            }
        }

        private void SeekVideoToSlider()
        {
            if (_videoPlayer == null || !VideoProgressSlider.IsEnabled)
            {
                return;
            }

            double seconds = Math.Clamp(VideoProgressSlider.Value, 0, VideoProgressSlider.Maximum);
            _videoPlayer.Time = Math.Max(0, (long)(seconds * 1000.0));
            VideoCurrentTimeTextBlock.Text = FormatTime(TimeSpan.FromSeconds(seconds));
        }

        private void RevealVideoButton_Click(object sender, RoutedEventArgs e)
        {
            if (_selectedVideo == null || !File.Exists(_selectedVideo.FilePath))
            {
                AppStatusService.SetStatus("Media: selected video is not available");
                return;
            }

            try
            {
                Process.Start(new ProcessStartInfo("explorer.exe", $"/select,\"{_selectedVideo.FilePath}\"")
                {
                    UseShellExecute = true,
                });
                AppStatusService.SetStatus($"Media: revealed {_selectedVideo.Name}");
            }
            catch
            {
                AppStatusService.SetStatus("Media: failed to reveal selected video");
            }
        }

        private static string FormatTime(TimeSpan time)
        {
            return time.TotalSeconds <= 0
                ? "0:00"
                : $"{(int)time.TotalMinutes}:{time.Seconds:D2}";
        }

        private sealed class MediaTreeNodeTag
        {
            public MediaTreeNodeTag(string displayText, string? filePath = null)
            {
                DisplayText = displayText;
                FilePath = filePath;
            }

            public string DisplayText { get; }

            public string? FilePath { get; }

            public override string ToString()
            {
                return DisplayText;
            }
        }
    }
}
