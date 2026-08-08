using System;
using System.Collections.Generic;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>What a trainer hotkey does when it fires.</summary>
    public enum TrainerHotkeyAction
    {
        /// <summary>Turn hold on for a vital if it is off, off if it is on.</summary>
        ToggleHoldLife,
        ToggleHoldEnergy,
        ToggleHoldShields,

        /// <summary>Let go of everything. The panic button.</summary>
        ReleaseAll,
    }

    /// <summary>
    /// One key combination the trainer listens for while it is watching a running game.
    /// </summary>
    /// <param name="Action">What it does.</param>
    /// <param name="Modifiers">Win32 <c>MOD_*</c> flags, combined.</param>
    /// <param name="VirtualKey">The Win32 virtual-key code.</param>
    /// <param name="Display">How to write the combination for a person.</param>
    /// <param name="Description">What it does, in the words the page uses elsewhere.</param>
    public sealed record TrainerHotkey(
        TrainerHotkeyAction Action,
        uint Modifiers,
        uint VirtualKey,
        string Display,
        string Description)
    {
        /// <summary>
        /// The id passed to <c>RegisterHotKey</c> and returned in <c>WM_HOTKEY</c>. Derived from
        /// the action so it is stable across runs and cannot collide with itself.
        /// </summary>
        public int Id => (int)Action + TrainerHotkeys.IdBase;
    }

    /// <summary>
    /// The trainer's key combinations, and the rules about when they may exist.
    ///
    /// This is the part worth keeping away from the Win32 call, because the decisions in it are
    /// the ones that can be wrong in a way a person notices. A registered hotkey is taken from
    /// the whole machine: while it is live, the combination does not reach the game, the browser,
    /// or anything else. That is the entire reason these are modifier combinations rather than
    /// the bare function keys a 1990s trainer would have used - F1 belongs to whatever the user
    /// is doing, and a tool that quietly eats it has overstepped.
    ///
    /// Ctrl+Alt+digit was chosen because the game does not use it (Battle Engine Aquila's
    /// controls are mouse, WASD and the space bar) and Windows does not either. If one is
    /// already taken by another application, registration fails and the page says which one
    /// rather than leaving a key that looks live and does nothing.
    /// </summary>
    public static class TrainerHotkeys
    {
        /// <summary>Chosen to sit clear of the 0x0000-0x0100 range Windows reserves for itself.</summary>
        public const int IdBase = 0xB4A0;

        public const uint ModAlt = 0x0001;
        public const uint ModControl = 0x0002;
        public const uint ModShift = 0x0004;

        /// <summary>
        /// Stops Windows repeating the hotkey while the key is held down. Without it, leaning on
        /// the key toggles hold dozens of times a second, which reads as the switch not working.
        /// </summary>
        public const uint ModNoRepeat = 0x4000;

        private const uint VkDigit0 = 0x30;
        private const uint VkDigit1 = 0x31;
        private const uint VkDigit2 = 0x32;
        private const uint VkDigit3 = 0x33;

        private const uint CtrlAlt = ModControl | ModAlt | ModNoRepeat;

        private static readonly TrainerHotkey[] All =
        [
            new(
                TrainerHotkeyAction.ToggleHoldLife,
                CtrlAlt,
                VkDigit1,
                "Ctrl + Alt + 1",
                "Hold life at the value in the box, or let go of it."),
            new(
                TrainerHotkeyAction.ToggleHoldEnergy,
                CtrlAlt,
                VkDigit2,
                "Ctrl + Alt + 2",
                "Hold energy, or let go of it."),
            new(
                TrainerHotkeyAction.ToggleHoldShields,
                CtrlAlt,
                VkDigit3,
                "Ctrl + Alt + 3",
                "Hold shields, or let go of it. In walker mode hold energy as well."),
            new(
                TrainerHotkeyAction.ReleaseAll,
                CtrlAlt,
                VkDigit0,
                "Ctrl + Alt + 0",
                "Let go of everything at once."),
        ];

        public static IReadOnlyList<TrainerHotkey> Bindings => All;

        public static TrainerHotkey ForAction(TrainerHotkeyAction action) =>
            All.First(binding => binding.Action == action);

        /// <summary>The binding a <c>WM_HOTKEY</c> id belongs to, or null when it is not ours.</summary>
        public static TrainerHotkey? ForId(int id) =>
            All.FirstOrDefault(binding => binding.Id == id);

        /// <summary>
        /// The vital a hold action is about, or null for <see cref="TrainerHotkeyAction.ReleaseAll"/>.
        /// </summary>
        public static LiveTrainerVital? VitalFor(TrainerHotkeyAction action) => action switch
        {
            TrainerHotkeyAction.ToggleHoldLife => LiveTrainerVital.Life,
            TrainerHotkeyAction.ToggleHoldEnergy => LiveTrainerVital.Energy,
            TrainerHotkeyAction.ToggleHoldShields => LiveTrainerVital.Shields,
            _ => null,
        };
    }
}
