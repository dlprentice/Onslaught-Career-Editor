// SPDX-License-Identifier: MIT
using Godot;
using OnslaughtToolkit.Companion.Careers;

namespace OnslaughtToolkit.Companion.Ui;

/// <summary>One kill category. Only a checked row enters an edit plan.</summary>
internal sealed class KillEditRow
{
    private readonly Label _current;
    private readonly Label _packed;

    internal KillEditRow(int category, string name)
    {
        Category = category;
        Root = Build.Row(16);
        Root.Name = name;
        Root.CustomMinimumSize = new Vector2(0, 46);
        Selected = Root.Add(new CheckBox { Disabled = true, TooltipText = "Include only this category in the preview and copy." });
        Root.Add(Build.Fixed(name, 148));
        _current = Root.Add(Build.Fixed("—", 120));
        Target = Root.Add(new SpinBox
        {
            MaxValue = CareerSave.MaxKills, Editable = false, UpdateOnTextChanged = true, CustomMinimumSize = new Vector2(210, 0),
        });
        _packed = Root.Add(new Label { Text = "Packed byte kept", SizeFlagsHorizontal = Control.SizeFlags.ExpandFill });
        Selected.Toggled += _ => SelectionChanged?.Invoke();
        Target.ValueChanged += _ => SelectionChanged?.Invoke();
    }

    internal event Action? SelectionChanged;

    internal int Category { get; }
    internal HBoxContainer Root { get; }
    internal CheckBox Selected { get; }
    internal SpinBox Target { get; }
    internal bool IsSelected => Selected.ButtonPressed;
    internal int TargetValue => (int)Target.Value;

    internal void SetCurrent(int value, int packed)
    {
        _current.Text = value.ToString("N0");
        _packed.Text = $"0x{packed:X2} kept";
        Selected.SetPressedNoSignal(false);
        Target.SetValueNoSignal(value);
    }

    internal void SetLocked(bool locked)
    {
        Selected.Disabled = locked;
        Target.Editable = !locked;
    }
}
