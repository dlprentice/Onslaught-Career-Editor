using System;
using System.IO;
using Microsoft.UI.Xaml;

namespace OnslaughtCareerEditor.WinUI
{
    public partial class App : Application
    {
        public static MainWindow? MainWindowInstance { get; private set; }

        public App()
        {
            InitializeComponent();
            UnhandledException += OnUnhandledException;
        }

        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            MainWindowInstance = new MainWindow();
            MainWindowInstance.Activate();
        }

        private static void OnUnhandledException(object sender, Microsoft.UI.Xaml.UnhandledExceptionEventArgs e)
        {
            string logPath = Path.Combine(Path.GetTempPath(), "OnslaughtCareerEditor.WinUI-startup-error.log");
            try
            {
                File.WriteAllText(
                    logPath,
                    $"{DateTimeOffset.Now:u}{Environment.NewLine}{e.Message}{Environment.NewLine}{e.Exception}");
            }
            catch
            {
                // Best effort only.
            }
        }
    }
}
