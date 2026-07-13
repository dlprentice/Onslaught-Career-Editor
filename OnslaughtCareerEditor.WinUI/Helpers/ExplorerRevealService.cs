using System.Diagnostics;

namespace OnslaughtCareerEditor.WinUI.Helpers;

internal static class ExplorerRevealService
{
    public static ProcessStartInfo BuildStartInfo(string filePath)
    {
        string fullPath = Path.GetFullPath(filePath.Trim());
        ProcessStartInfo startInfo = new("explorer.exe")
        {
            UseShellExecute = true,
        };
        startInfo.ArgumentList.Add($"/select,{fullPath}");
        return startInfo;
    }

    public static bool TryReveal(string filePath, Action<ProcessStartInfo>? launcher = null)
    {
        try
        {
            launcher ??= startInfo => Process.Start(startInfo);
            launcher(BuildStartInfo(filePath));
            return true;
        }
        catch
        {
            return false;
        }
    }
}
