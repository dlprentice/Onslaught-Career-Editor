using Microsoft.UI.Xaml.Controls;
using System.Reflection;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class AboutPage : Page
    {
        public AboutPage()
        {
            InitializeComponent();
            VersionTextBlock.Text = $"Version: {GetVersionLabel()}";
            AppStatusService.SetStatus("About: product summary ready");
        }

        private static string GetVersionLabel()
        {
            Assembly asm = Assembly.GetEntryAssembly() ?? Assembly.GetExecutingAssembly();
            string? informational = asm.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion;
            if (!string.IsNullOrWhiteSpace(informational))
            {
                return informational;
            }

            return asm.GetName().Version?.ToString() ?? "unknown";
        }
    }
}
