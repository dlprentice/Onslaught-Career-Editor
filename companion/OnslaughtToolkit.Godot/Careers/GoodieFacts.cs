// SPDX-License-Identifier: MIT
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtToolkit.Companion.Careers;

public enum GoodieEvidence { SeenInGame, GameCodeChecked, DeveloperSource, NeverShown, Reserved }

/// <summary>
/// What is known about one Goodie: its unlock rule (the linked MIT GoodieUnlockRequirementService,
/// written from the developers' Career.cpp) and how far the evidence goes, per the RE lane's
/// 2026-09-25 review: only Goodie 2's load, gold display and new-to-viewed change were seen in the
/// Steam game; the rules for Goodies 0, 8, 74–78, 121 and 164 match the retail code; the rest,
/// including kill thresholds, script and cutscene Goodies, come from the developers' source only.
/// </summary>
public static class GoodieFacts
{
    public static string Rule(int index) => GoodieUnlockRequirementService.Describe(index).Summary;

    public static GoodieEvidence Evidence(int index) => index switch
    {
        >= CareerSave.GoodieTable => GoodieEvidence.Reserved,
        >= 71 and <= 73 => GoodieEvidence.NeverShown,
        2 => GoodieEvidence.SeenInGame,
        0 or 8 or (>= 74 and <= 78) or 121 or 164 => GoodieEvidence.GameCodeChecked,
        _ => GoodieEvidence.DeveloperSource,
    };

    public static string Describe(GoodieEvidence evidence) => evidence switch
    {
        GoodieEvidence.SeenInGame =>
            "Seen in the game: a career with this Goodie new loaded, showed it gold and marked it viewed when opened (Steam release).",
        GoodieEvidence.GameCodeChecked => "Checked in the game's code: this rule matches the retail executable. Not yet watched in play.",
        GoodieEvidence.DeveloperSource => "From the developers' source code; not yet checked in the retail game.",
        GoodieEvidence.NeverShown => "The game's gallery has no cell for this slot: its wall mapper skips 071–073 (the retail code " +
            "matches the developers' source). The game can still mark it new, so the save keeps a state for it; that state is preserved.",
        _ => "A reserved slot the game never displays; its bytes are preserved.",
    };

    public static string StateName(GoodieState state) => state switch
    {
        GoodieState.Locked => "Locked",
        GoodieState.Hint => "Locked, hint shown",
        GoodieState.New => "New (gold in the game)",
        GoodieState.Old => "Viewed (blue in the game)",
        GoodieState.Reserved => "Reserved",
        _ => "Unknown stored value",
    };
}
