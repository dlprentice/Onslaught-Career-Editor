using System.Collections.Generic;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal sealed record PatchBenchChoiceButtonBinding(
        Button Button,
        PatchBenchSelectedChoiceState State);

    internal static class PatchBenchChoiceVisualState
    {
        public static PatchBenchChoiceButtonBinding Bind(
            Button button,
            string normalAutomationName,
            string selectedAutomationName,
            bool isSelected)
        {
            return new PatchBenchChoiceButtonBinding(
                button,
                new PatchBenchSelectedChoiceState(
                    normalAutomationName,
                    selectedAutomationName,
                    isSelected));
        }

        public static void Apply(
            IEnumerable<PatchBenchChoiceButtonBinding> bindings,
            Style selectedStyle,
            Style normalStyle)
        {
            foreach (PatchBenchChoiceButtonBinding binding in bindings)
            {
                binding.Button.Style = binding.State.IsSelected ? selectedStyle : normalStyle;
                AutomationProperties.SetName(binding.Button, binding.State.AutomationName);
            }
        }
    }
}
