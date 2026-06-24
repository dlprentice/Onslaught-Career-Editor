using System.IO;
using System.Windows;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {
        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            // Check if this is first launch (no config file exists)
            bool isFirstLaunch = !File.Exists(AppConfig.GetConfigPath());
            var config = AppConfig.Load();

            // Auto-detect game directory on first launch or if not set
            if (isFirstLaunch || string.IsNullOrEmpty(config.GameDirectory))
            {
                string? detected = AppConfig.DetectGameDirectory();
                if (!string.IsNullOrEmpty(detected))
                {
                    config.SetGameDir(detected);
                }
                else if (isFirstLaunch)
                {
                    // Show prompt on first launch if game not found
                    MessageBox.Show(
                        "Battle Engine Aquila installation was not detected automatically.\n\n" +
                        "You can set the game directory manually in the Settings tab.\n\n" +
                        "The Save Editor, Audio Player, and Video Player require the game directory to locate files.",
                        "Game Directory Not Found",
                        MessageBoxButton.OK,
                        MessageBoxImage.Information);
                }
            }

            var mainWindow = new MainWindow();
            mainWindow.Show();
        }
    }
}
