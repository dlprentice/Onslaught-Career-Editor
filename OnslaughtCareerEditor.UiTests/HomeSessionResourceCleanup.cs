namespace OnslaughtCareerEditor.UiTests;

internal static class HomeSessionResourceCleanup
{
    internal static void Run(Action disposeAutomation, Action cleanupApp)
    {
        try
        {
            disposeAutomation();
        }
        finally
        {
            cleanupApp();
        }
    }
}
