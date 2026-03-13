using Microsoft.UI;
using Microsoft.UI.Xaml.Media;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Models
{
    public sealed class BinaryPatchItemModel
    {
        public BinaryPatchItemModel(BinaryPatchSpec spec)
        {
            Spec = spec;
            Summary = spec.Key switch
            {
                "resolution_gate" => "Removes the retail 4:3-only display mode rejection gate.",
                "force_windowed" => "Biases startup toward a windowed launch when the runtime supports it.",
                "extra_graphics_default_on" => "Defaults extra graphics toggles on without cardid vendor matching.",
                "ignore_cardid_tweak_overrides" => "Skips cardid.txt vendor/device override reads and keeps executable defaults.",
                "skip_auto_toggle" => "Optional companion for setups that still force fullscreen after stable fixes.",
                _ => spec.DisplayName,
            };
        }

        public BinaryPatchSpec Spec { get; }

        public bool IsSelected { get; set; }

        public string DisplayName => Spec.DisplayName;

        public string Summary { get; }

        public string FunctionalArea => Spec.Key switch
        {
            "resolution_gate" => "Display & Startup",
            "force_windowed" => "Display & Startup",
            "skip_auto_toggle" => "Display & Startup",
            "extra_graphics_default_on" => "Graphics & Hardware Overrides",
            "ignore_cardid_tweak_overrides" => "Graphics & Hardware Overrides",
            _ => "Other",
        };

        public string TrackLabel => string.Equals(Spec.Track, "Experimental", System.StringComparison.OrdinalIgnoreCase)
            ? "EXPERIMENTAL"
            : string.Equals(Spec.Track, "Dangerous", System.StringComparison.OrdinalIgnoreCase)
                ? "DANGEROUS"
                : "STABLE";

        public Brush TrackBrush => string.Equals(Spec.Track, "Experimental", System.StringComparison.OrdinalIgnoreCase)
            ? new SolidColorBrush(ColorHelper.FromArgb(0xFF, 0xE0, 0xB8, 0x4B))
            : string.Equals(Spec.Track, "Dangerous", System.StringComparison.OrdinalIgnoreCase)
                ? new SolidColorBrush(ColorHelper.FromArgb(0xFF, 0xE4, 0x6B, 0x6B))
                : new SolidColorBrush(ColorHelper.FromArgb(0xFF, 0x71, 0xD2, 0x8F));

        public string OffsetText => $"Offset 0x{Spec.FileOffset:X}";
    }
}
