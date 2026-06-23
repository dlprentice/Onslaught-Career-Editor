using System;
using System.IO;
using Microsoft.UI.Xaml;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI
{
    public partial class App : Application
    {
        public static MainWindow? MainWindowInstance { get; private set; }
        public static GameProfileManagedProcessRegistry SafeGameCopyProcesses { get; } = new(BuildSafeCopyProcessLeasePath());

        public App()
        {
            InitializeComponent();
            UnhandledException += OnUnhandledException;
        }

        protected override void OnLaunched(LaunchActivatedEventArgs args)
        {
            MainWindowInstance = new MainWindow();
            MainWindowInstance.Activate();
            MainWindowInstance.MaximizeForUserWorkspace();
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

            try
            {
                AppStatusService.SetStatus("Unexpected app error. Restart the app; details were written to the local startup-error log.");
            }
            catch
            {
                // Best effort only.
            }
        }

        private static string BuildSafeCopyProcessLeasePath()
        {
            return Path.Combine(
                AppConfig.GetConfigDir(),
                "GameProfiles",
                GameProfileManagedProcessRegistry.LeaseFileName);
        }
    }
}
