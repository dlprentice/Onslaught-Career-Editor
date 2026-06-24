using System.Reflection;
using System.Windows.Controls;

namespace Onslaught___Career_Editor.Views;

public partial class AboutView : UserControl
{
    public AboutView()
    {
        InitializeComponent();
        VersionTextBlock.Text = $"Version: {GetVersionLabel()}";
    }

    private static string GetVersionLabel()
    {
        var asm = Assembly.GetEntryAssembly() ?? Assembly.GetExecutingAssembly();
        string? informational = asm.GetCustomAttribute<AssemblyInformationalVersionAttribute>()?.InformationalVersion;
        if (!string.IsNullOrWhiteSpace(informational))
        {
            return informational;
        }

        return asm.GetName().Version?.ToString() ?? "unknown";
    }
}
