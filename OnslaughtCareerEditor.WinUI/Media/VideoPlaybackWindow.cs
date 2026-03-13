using System;
using Microsoft.UI;
using Microsoft.UI.Windowing;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Microsoft.UI.Xaml.Media;
using Windows.Graphics;
using Windows.UI;
using WinRT.Interop;

namespace OnslaughtCareerEditor.WinUI.Media
{
    internal sealed class VideoPlaybackWindow : Window
    {
        private bool _isClosed;
        private bool _hasSizedWindow;

        public VideoPlaybackWindow()
        {
            Title = "Onslaught Career Editor Video Player";
            Content = new Grid
            {
                Background = new SolidColorBrush(ColorHelper.FromArgb(255, 0, 0, 0)),
                Children =
                {
                    new TextBlock
                    {
                        Text = "Preparing video playback...",
                        Foreground = new SolidColorBrush(Colors.White),
                        HorizontalAlignment = HorizontalAlignment.Center,
                        VerticalAlignment = VerticalAlignment.Center,
                        FontSize = 18
                    }
                }
            };

            Closed += (_, _) => _isClosed = true;
        }

        public bool IsClosed => _isClosed;

        public IntPtr WindowHandle => WindowNative.GetWindowHandle(this);

        public void ShowForPlayback(string? title)
        {
            if (_isClosed)
            {
                throw new InvalidOperationException("The video playback window has already been closed.");
            }

            Title = string.IsNullOrWhiteSpace(title)
                ? "Onslaught Career Editor Video Player"
                : $"Onslaught Career Editor Video Player - {title}";

            Activate();

            if (_hasSizedWindow)
            {
                return;
            }

            IntPtr handle = WindowHandle;
            if (handle == IntPtr.Zero)
            {
                return;
            }

            AppWindow appWindow = AppWindow.GetFromWindowId(Win32Interop.GetWindowIdFromWindow(handle));
            appWindow.Resize(new SizeInt32(1280, 720));
            _hasSizedWindow = true;
        }
    }
}
