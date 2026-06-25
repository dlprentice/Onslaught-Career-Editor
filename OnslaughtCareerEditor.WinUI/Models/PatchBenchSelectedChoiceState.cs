namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchSelectedChoiceState(
        string NormalAutomationName,
        string SelectedAutomationName,
        bool IsSelected)
    {
        public string AutomationName => IsSelected ? SelectedAutomationName : NormalAutomationName;
    }
}
