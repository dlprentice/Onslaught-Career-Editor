using System.IO;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class HomePage : Page
    {
        public HomePage()
        {
            InitializeComponent();
            RefreshSetupStatus();
            AppStatusService.SetStatus("Home: choose a task");
        }

        private void RefreshSetupStatus()
        {
            string? gameDir = AppConfig.Load().GetGameDirOrDetect(persistDetection: true);
            if (string.IsNullOrWhiteSpace(gameDir))
            {
                SetupStatusTextBlock.Text = "Game directory not set. Choose your installed game folder in Settings. The app reads it to create playable copies; it does not edit that folder.";
                return;
            }

            string folderName = Path.GetFileName(gameDir.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
            SetupStatusTextBlock.Text = string.IsNullOrWhiteSpace(folderName)
                ? "Game directory configured."
                : $"Game directory configured: {folderName}.";
        }

        private void NavigateButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button { Tag: string tag })
            {
                App.MainWindowInstance?.NavigateToTag(tag);
            }
        }

        private void OpenConfigurationEditorButton_Click(object sender, RoutedEventArgs e)
        {
            App.MainWindowInstance?.NavigateToTag("saves", saveSubTab: 2);
        }
    }
}
