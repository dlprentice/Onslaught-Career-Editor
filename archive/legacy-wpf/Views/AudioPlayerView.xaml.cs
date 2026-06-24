using NAudio.Wave;
using NAudio.Wave.SampleProviders;
using NAudio.Vorbis;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using System.Windows.Threading;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Audio Player tab - plays game music and voice files.
    /// </summary>
    public partial class AudioPlayerView : UserControl, ILazyLoadView
    {
        private WaveOutEvent? _waveOut;
        private VorbisWaveReader? _vorbisReader;
        private DispatcherTimer? _positionTimer;
        private bool _isDraggingSlider;
        private bool _isUpdatingSlider;
        private List<AudioFileItem> _allAudioFiles = new();
        private AudioFileItem? _currentFile;
        private bool _hasLoaded;
        private bool _isLoading;
        private CancellationTokenSource? _loadCts;
        private SampleChannel? _sampleChannel;
        private readonly List<Border> _visualizerBars = new();
        private readonly Queue<float> _visualizerHistory = new();
        private readonly object _visualizerLock = new();
        private float _latestMeterLevel;
        private const int VisualizerBarCount = 28;

        public AudioPlayerView()
        {
            InitializeComponent();
            BuildVisualizerBars();
            ResetVisualizer();

            // Set up position timer
            _positionTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromMilliseconds(100)
            };
            _positionTimer.Tick += PositionTimer_Tick;

            // Clean up resources when control is unloaded (respect background playback setting)
            Unloaded += (_, _) =>
            {
                var config = AppConfig.Load();
                if (!config.AllowBackgroundAudio)
                {
                    Stop();
                }
            };

            // Load config (defer heavy scanning until tab activated)
            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();
            if (!string.IsNullOrEmpty(gameDir))
            {
                GameDirTextBox.Text = gameDir;
            }
        }

        public void EnsureLoaded()
        {
            if (_hasLoaded || _isLoading)
            {
                return;
            }

            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir() ?? AppConfig.DetectGameDirectory();
            if (string.IsNullOrEmpty(gameDir))
            {
                MainWindow.SetStatus("Audio Player: Game directory not set");
                return;
            }

            if (string.IsNullOrEmpty(config.GetGameDir()))
            {
                config.SetGameDir(gameDir);
            }

            GameDirTextBox.Text = gameDir;
            LoadAudioFilesAsync(gameDir);
        }

        private void LoadAudioFilesAsync(string gameDir)
        {
            _loadCts?.Cancel();
            _loadCts = new CancellationTokenSource();
            var token = _loadCts.Token;

            _isLoading = true;
            MainWindow.SetStatus("Audio Player: Loading audio files...");

            Task.Run(() => BuildAudioCategories(gameDir, token), token)
                .ContinueWith(task =>
                {
                    _isLoading = false;

                    if (task.IsCanceled)
                    {
                        return;
                    }

                    if (task.Exception != null)
                    {
                        Dispatcher.Invoke(() =>
                        {
                            MainWindow.SetStatus("Audio Player: Failed to load audio files");
                        });
                        return;
                    }

                    var result = task.Result;
                    Dispatcher.Invoke(() =>
                    {
                        _allAudioFiles = result.Files;
                        AudioTree.ItemsSource = result.Categories;
                        _hasLoaded = true;

                        MainWindow.SetStatus($"Audio Player: Loaded {_allAudioFiles.Count} audio file(s)");

                        if (result.Categories.Count > 0)
                        {
                            Dispatcher.BeginInvoke(new Action(() =>
                            {
                                var container = AudioTree.ItemContainerGenerator.ContainerFromIndex(0) as TreeViewItem;
                                if (container != null) container.IsExpanded = true;
                            }), DispatcherPriority.Loaded);
                        }
                    });
                }, TaskScheduler.Default);
        }

        private AudioLoadResult BuildAudioCategories(string gameDir, CancellationToken token)
        {
            var allFiles = new List<AudioFileItem>();
            var categories = new List<AudioCategory>();

            // Music folder
            string musicDir = Path.Combine(gameDir, "data", "Music");
            if (Directory.Exists(musicDir))
            {
                var musicCategory = new AudioCategory { Name = "Music" };
                foreach (string file in Directory.GetFiles(musicDir, "*.ogg"))
                {
                    token.ThrowIfCancellationRequested();
                    string name = Path.GetFileNameWithoutExtension(file)
                        .Replace(" (Master)", "")
                        .Replace("_", " ");
                    var item = new AudioFileItem
                    {
                        Name = name,
                        FilePath = file,
                        Duration = TryGetDurationLabel(file)
                    };
                    musicCategory.Children.Add(item);
                    allFiles.Add(item);
                }
                if (musicCategory.Children.Count > 0)
                    categories.Add(musicCategory);
            }

            // Voice folder
            string voiceDir = Path.Combine(gameDir, "data", "sounds", "english", "MessageBox");
            if (Directory.Exists(voiceDir))
            {
                var voiceFiles = Directory.GetFiles(voiceDir, "*.ogg")
                    .Select(f => new AudioFileItem
                    {
                        Name = Path.GetFileNameWithoutExtension(f),
                        FilePath = f,
                        Duration = TryGetDurationLabel(f)
                    })
                    .ToList();

                if (voiceFiles.Count > 0)
                {
                    // Group by category (missions, tutorial, racing, status, other)
                    var grouped = voiceFiles
                        .GroupBy(f => GetVoiceCategory(f.Name))
                        .OrderBy(g => GetCategoryOrder(g.Key));

                    var voiceCategory = new AudioCategory { Name = $"Voice ({voiceFiles.Count} files)" };
                    foreach (var group in grouped)
                    {
                        // Add count to group name
                        var groupCategory = new AudioCategory { Name = $"{group.Key} ({group.Count()})" };
                        foreach (var file in group.OrderBy(f => f.Name))
                        {
                            groupCategory.Children.Add(file);
                            allFiles.Add(file);
                        }
                        voiceCategory.Children.Add(groupCategory);
                    }
                    categories.Add(voiceCategory);
                }
            }
            return new AudioLoadResult(categories, allFiles);
        }

        private void BuildVisualizerBars()
        {
            if (VisualizerBarsHost == null)
            {
                return;
            }

            VisualizerBarsHost.Children.Clear();
            VisualizerBarsHost.ColumnDefinitions.Clear();
            _visualizerBars.Clear();

            for (int i = 0; i < VisualizerBarCount; i++)
            {
                VisualizerBarsHost.ColumnDefinitions.Add(new ColumnDefinition());

                byte alpha = (byte)(120 + ((i % 4) * 20));
                var bar = new Border
                {
                    Margin = new Thickness(2, 0, 2, 0),
                    CornerRadius = new CornerRadius(4, 4, 0, 0),
                    VerticalAlignment = VerticalAlignment.Bottom,
                    Height = 150,
                    Background = new SolidColorBrush(Color.FromArgb(alpha, 76, 201, 240)),
                    Opacity = 0.35,
                    RenderTransformOrigin = new Point(0.5, 1),
                    RenderTransform = new ScaleTransform(1, 0.08)
                };

                Grid.SetColumn(bar, i);
                VisualizerBarsHost.Children.Add(bar);
                _visualizerBars.Add(bar);
            }
        }

        private void SampleChannel_PreVolumeMeter(object? sender, StreamVolumeEventArgs e)
        {
            float level = 0f;
            foreach (float sample in e.MaxSampleValues)
            {
                level = Math.Max(level, Math.Abs(sample));
            }

            lock (_visualizerLock)
            {
                _latestMeterLevel = Math.Clamp(level, 0f, 1f);
            }
        }

        private void PushVisualizerSample(float level)
        {
            while (_visualizerHistory.Count >= VisualizerBarCount)
            {
                _visualizerHistory.Dequeue();
            }

            _visualizerHistory.Enqueue(Math.Clamp(level, 0.03f, 1f));
        }

        private void RenderVisualizer()
        {
            if (_visualizerBars.Count == 0)
            {
                return;
            }

            float[] levels = _visualizerHistory.ToArray();
            int leadingBlanks = Math.Max(0, _visualizerBars.Count - levels.Length);

            for (int i = 0; i < _visualizerBars.Count; i++)
            {
                float level = i < leadingBlanks ? 0.03f : levels[i - leadingBlanks];
                if (_visualizerBars[i].RenderTransform is ScaleTransform transform)
                {
                    transform.ScaleY = Math.Clamp(0.08 + (level * 0.92), 0.08, 1.0);
                }

                _visualizerBars[i].Opacity = 0.28 + (level * 0.72);
            }
        }

        private void ResetVisualizer()
        {
            _visualizerHistory.Clear();
            for (int i = 0; i < VisualizerBarCount; i++)
            {
                _visualizerHistory.Enqueue(0.03f);
            }

            lock (_visualizerLock)
            {
                _latestMeterLevel = 0f;
            }

            RenderVisualizer();
        }

        private string GetVoiceCategory(string fileName)
        {
            string upper = fileName.ToUpper();

            // Check special categories first
            if (upper.StartsWith("TUTORIAL"))
                return "Tutorial";
            if (upper.StartsWith("RACING"))
                return "Racing";
            if (upper.StartsWith("HEALTH_") || upper.StartsWith("UNDER_") ||
                upper.StartsWith("BASE_") || upper.StartsWith("NEED_"))
                return "Status Messages";

            // Check for mission number prefix (e.g., "110_event_name")
            var parts = fileName.Split('_');
            if (parts.Length > 0 && int.TryParse(parts[0], out int missionNum))
            {
                return $"Mission {missionNum}";
            }

            return "Other";
        }

        private int GetCategoryOrder(string category)
        {
            // Sort order: Missions first (numerically), then special categories, then Other
            if (category.StartsWith("Mission "))
            {
                string numStr = category.Replace("Mission ", "");
                if (int.TryParse(numStr, out int num))
                    return num;
            }
            return category switch
            {
                "Tutorial" => 10000,
                "Racing" => 10001,
                "Status Messages" => 10002,
                "Other" => 99999,
                _ => 50000
            };
        }

        private void AudioTree_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            if (e.NewValue is AudioFileItem item)
            {
                _currentFile = item;
                NowPlayingLabel.Text = item.Name;
                FilePathLabel.Text = item.FilePath;
                PlayButton.IsEnabled = true;
                ResetVisualizer();
                MainWindow.SetStatus($"Audio Player: Selected {item.Name}");
            }
        }

        private void AudioTree_MouseDoubleClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            // Double-click to play - only if an audio file is selected (not a category)
            if (AudioTree.SelectedItem is AudioFileItem item)
            {
                _currentFile = item;
                NowPlayingLabel.Text = item.Name;
                FilePathLabel.Text = item.FilePath;
                PlayButton_Click(sender, e);
            }
        }

        private void PlayButton_Click(object sender, RoutedEventArgs e)
        {
            if (_currentFile == null) return;

            try
            {
                NowPlayingLabel.Text = _currentFile.Name;
                FilePathLabel.Text = _currentFile.FilePath;
                Stop();

                // Create reader and output
                _vorbisReader = new VorbisWaveReader(_currentFile.FilePath);
                _sampleChannel = new SampleChannel(_vorbisReader, forceStereo: true);
                _sampleChannel.PreVolumeMeter += SampleChannel_PreVolumeMeter;
                _waveOut = new WaveOutEvent();
                _waveOut.Init(new SampleToWaveProvider16(_sampleChannel));
                _waveOut.Volume = (float)(VolumeSlider.Value / 100.0);
                _waveOut.PlaybackStopped += WaveOut_PlaybackStopped;
                ResetVisualizer();

                // Set up progress slider
                ProgressSlider.Maximum = _vorbisReader.TotalTime.TotalSeconds;
                ProgressSlider.Value = 0;
                ProgressSlider.IsEnabled = true;
                TotalTimeLabel.Text = FormatTime(_vorbisReader.TotalTime);

                _waveOut.Play();
                _positionTimer?.Start();

                PlayButton.IsEnabled = false;
                PauseButton.IsEnabled = true;
                StopButton.IsEnabled = true;
                MainWindow.SetStatus($"Audio Player: Playing {_currentFile.Name}");
                NotifyPlaybackStarted();
            }
            catch (Exception ex)
            {
                MainWindow.SetStatus($"Audio Player: Error - {ex.Message}");
                MessageBox.Show($"Failed to play audio: {ex.Message}", "Error", MessageBoxButton.OK, MessageBoxImage.Error);
            }
        }

        private void PauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (_waveOut == null) return;

            if (_waveOut.PlaybackState == PlaybackState.Playing)
            {
                _waveOut.Pause();
                _positionTimer?.Stop();
                PauseButton.Content = "Resume";
                MainWindow.SetStatus("Audio Player: Paused");
            }
            else if (_waveOut.PlaybackState == PlaybackState.Paused)
            {
                _waveOut.Play();
                _positionTimer?.Start();
                PauseButton.Content = "Pause";
                MainWindow.SetStatus($"Audio Player: Playing {_currentFile?.Name}");
                NotifyPlaybackStarted();
            }
        }

        private void StopButton_Click(object sender, RoutedEventArgs e)
        {
            Stop();
            MainWindow.SetStatus("Audio Player: Stopped");
        }

        public void StopPlayback() => Stop();

        public bool IsPlaying => _waveOut?.PlaybackState == PlaybackState.Playing;

        private void Stop()
        {
            _positionTimer?.Stop();

            _waveOut?.Stop();
            _waveOut?.Dispose();
            _waveOut = null;

            if (_sampleChannel != null)
            {
                _sampleChannel.PreVolumeMeter -= SampleChannel_PreVolumeMeter;
                _sampleChannel = null;
            }

            _vorbisReader?.Dispose();
            _vorbisReader = null;
            ResetVisualizer();

            PlayButton.IsEnabled = _currentFile != null;
            PauseButton.IsEnabled = false;
            PauseButton.Content = "Pause";
            StopButton.IsEnabled = false;
            ProgressSlider.IsEnabled = false;
            ProgressSlider.Value = 0;
            CurrentTimeLabel.Text = "0:00";
        }

        private void WaveOut_PlaybackStopped(object? sender, StoppedEventArgs e)
        {
            if (sender != null && !ReferenceEquals(sender, _waveOut))
                return;
            Dispatcher.Invoke(() =>
            {
                _positionTimer?.Stop();
                ResetVisualizer();
                PlayButton.IsEnabled = true;
                PauseButton.IsEnabled = false;
                PauseButton.Content = "Pause";
                StopButton.IsEnabled = false;
                ProgressSlider.Value = 0;
                ProgressSlider.IsEnabled = false;
                CurrentTimeLabel.Text = "0:00";
                MainWindow.SetStatus("Audio Player: Playback finished");
            });
        }

        private void NotifyPlaybackStarted()
        {
            if (Window.GetWindow(this) is MainWindow mainWindow)
            {
                mainWindow.HandleMediaPlaybackStarted(MediaPlaybackKind.Audio);
            }
        }

        private void PositionTimer_Tick(object? sender, EventArgs e)
        {
            float levelSnapshot;
            lock (_visualizerLock)
            {
                levelSnapshot = _latestMeterLevel;
                _latestMeterLevel *= 0.7f;
            }

            PushVisualizerSample(levelSnapshot);
            RenderVisualizer();

            if (_vorbisReader != null && !_isDraggingSlider)
            {
                _isUpdatingSlider = true;
                ProgressSlider.Value = _vorbisReader.CurrentTime.TotalSeconds;
                CurrentTimeLabel.Text = FormatTime(_vorbisReader.CurrentTime);
                _isUpdatingSlider = false;
            }
        }

        private void ProgressSlider_PreviewMouseDown(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            _isDraggingSlider = true;
        }

        private void ProgressSlider_PreviewMouseUp(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            _isDraggingSlider = false;
            if (_vorbisReader != null)
            {
                _vorbisReader.CurrentTime = TimeSpan.FromSeconds(ProgressSlider.Value);
            }
        }

        private void ProgressSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (_isDraggingSlider)
            {
                // Update time label while dragging (seek happens on mouse up)
                CurrentTimeLabel.Text = FormatTime(TimeSpan.FromSeconds(ProgressSlider.Value));
            }
            else if (!_isUpdatingSlider && _vorbisReader != null)
            {
                // Keyboard seeking (arrow keys) - seek immediately since not dragging
                _vorbisReader.CurrentTime = TimeSpan.FromSeconds(ProgressSlider.Value);
                CurrentTimeLabel.Text = FormatTime(TimeSpan.FromSeconds(ProgressSlider.Value));
            }
        }

        private void VolumeSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            // Guard against event firing during XAML initialization
            if (VolumeLabel == null) return;

            VolumeLabel.Text = $"{(int)VolumeSlider.Value}%";
            if (_waveOut != null)
            {
                _waveOut.Volume = (float)(VolumeSlider.Value / 100.0);
            }
        }

        private void SearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            string query = SearchTextBox.Text.Trim().ToLower();

            if (string.IsNullOrEmpty(query))
            {
                // Reload all
                string? gameDir = GameDirTextBox.Text;
                if (!string.IsNullOrEmpty(gameDir))
                    LoadAudioFilesAsync(gameDir);
                return;
            }

            // Filter
            var filtered = _allAudioFiles.Where(f => f.Name.ToLower().Contains(query)).ToList();
            var category = new AudioCategory { Name = $"Search Results ({filtered.Count})" };
            category.Children.AddRange(filtered.Cast<object>());

            AudioTree.ItemsSource = new[] { category };
            MainWindow.SetStatus($"Audio Player: Found {filtered.Count} file(s)");
        }

        private void BrowseGameDir_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new System.Windows.Forms.FolderBrowserDialog
            {
                Description = "Select Battle Engine Aquila game directory",
                ShowNewFolderButton = false
            };

            if (dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                GameDirTextBox.Text = dialog.SelectedPath;
                var config = AppConfig.Load();
                config.SetGameDir(dialog.SelectedPath);
                LoadAudioFilesAsync(dialog.SelectedPath);
            }
        }

        private void ReloadAudio_Click(object sender, RoutedEventArgs e)
        {
            string? gameDir = GameDirTextBox.Text;
            if (!string.IsNullOrEmpty(gameDir) && Directory.Exists(gameDir))
            {
                LoadAudioFilesAsync(gameDir);
            }
        }

        private static string FormatTime(TimeSpan time)
        {
            return $"{(int)time.TotalMinutes}:{time.Seconds:D2}";
        }

        private static string TryGetDurationLabel(string filePath)
        {
            try
            {
                using var reader = new VorbisWaveReader(filePath);
                if (reader.TotalTime.TotalSeconds <= 0)
                    return "";
                return FormatTime(reader.TotalTime);
            }
            catch
            {
                return "";
            }
        }
    }

    /// <summary>
    /// Represents an audio file.
    /// </summary>
    public class AudioFileItem
    {
        public string Name { get; set; } = "";
        public string FilePath { get; set; } = "";
        public string Duration { get; set; } = "";
    }

    /// <summary>
    /// Represents a category in the audio tree.
    /// </summary>
    public class AudioCategory
    {
        public string Name { get; set; } = "";
        public List<object> Children { get; set; } = new();
    }

    internal sealed record AudioLoadResult(List<AudioCategory> Categories, List<AudioFileItem> Files);
}
