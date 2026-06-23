namespace Onslaught___Career_Editor
{
    public sealed record GoodieUnlockRequirement(string Summary, string EvidenceLabel)
    {
        public static GoodieUnlockRequirement Unknown { get; } = new(
            "Unlock rule not mapped yet.",
            "RE follow-up required");
    }

    public static class GoodieUnlockRequirementService
    {
        private const string UpdateGoodieEvidence = "CCareer__UpdateGoodieStates 0x0041c470";
        private const string ScriptEvidence = "Mission script SetGoodieState";
        private const string CutsceneEvidence = "CGame cutscene handlers";

        private static readonly int[] CampaignWorldOrder =
        [
            100, 110, 200, 211, 212, 221, 222, 231, 232,
            300, 311, 312, 321, 322, 331, 332,
            400, 411, 412, 421, 422, 431, 432,
            500, 511, 512, 521, 522, 523, 524,
            600, 611, 612, 621, 622,
            700, 710, 720, 731, 732, 741, 742, 800
        ];

        private static readonly IReadOnlyDictionary<int, string> ExplicitRules = new Dictionary<int, string>
        {
            [0] = "Complete level 100.",
            [1] = "Earn C or better on level 110.",
            [2] = "Unlock Goodie 001, then earn C or better on level 200.",
            [3] = "Unlock Goodie 002, then earn C or better on level 231 or 232.",
            [4] = "Unlock Goodie 003, then earn C or better on level 321 or 322.",
            [5] = "Unlock Goodie 004, then earn C or better on level 321 or 322.",
            [6] = "Unlock Goodie 005, then earn C or better on level 621 or 622.",
            [7] = "Unlock Goodie 006, then earn C or better on level 741 or 742.",
            [8] = "Complete level 100.",
            [9] = "Complete level 211 or 212.",
            [10] = "Complete level 400.",
            [11] = "Complete level 710.",
            [12] = "Complete level 200.",
            [13] = "Complete level 331 or 332.",
            [14] = "Complete level 110.",
            [15] = "Complete level 621 or 622.",
            [16] = "Earn C or better on level 400.",
            [17] = "Earn C or better on level 300.",
            [18] = "Complete level 512.",
            [19] = "Complete level 221 or 222.",
            [20] = "Complete level 611 or 612.",
            [21] = "Complete level 211 or 212.",
            [22] = "Complete level 300.",
            [23] = "Earn C or better on level 200.",
            [24] = "Complete level 331 or 332.",
            [25] = "Complete level 400.",
            [26] = "Earn C or better on level 221 or 222.",
            [27] = "Complete level 221 or 222.",
            [28] = "Complete level 200.",
            [29] = "Complete level 300.",
            [30] = "Complete level 211 or 212.",
            [31] = "Complete level 211 or 212.",
            [32] = "Complete level 200.",
            [33] = "Defeat 40 infantry.",
            [34] = "Defeat 160 infantry.",
            [35] = "Defeat 80 infantry.",
            [36] = "Destroy 25 aircraft.",
            [37] = "Destroy 100 aircraft.",
            [38] = "Destroy 50 aircraft.",
            [39] = "Destroy 75 aircraft.",
            [40] = "Destroy 25 aircraft and defeat 80 infantry.",
            [41] = "Destroy 50 aircraft and defeat 100 infantry.",
            [42] = "Destroy 100 vehicles.",
            [43] = "Destroy 400 vehicles.",
            [44] = "Destroy 300 vehicles.",
            [45] = "Destroy 200 vehicles.",
            [46] = "Complete level 500.",
            [47] = "Destroy 20 mechs.",
            [48] = "Destroy 40 mechs.",
            [49] = "Destroy 80 mechs.",
            [50] = "Unlocked by mission script in level 521 or 522.",
            [51] = "Destroy 40 mechs.",
            [52] = "Unlocked by mission script in level 421 or 422.",
            [53] = "Destroy 50 emplacements and 25 aircraft.",
            [54] = "Destroy 50 emplacements.",
            [55] = "Destroy 25 emplacements.",
            [56] = "Destroy 75 emplacements and 100 vehicles.",
            [57] = "Destroy 25 emplacements and 25 aircraft.",
            [58] = "Earn A or better on level 331 or 332.",
            [59] = "Earn A or better on level 431 or 432.",
            [60] = "Complete level 523 or 524.",
            [61] = "Earn A or better on level 521 or 522.",
            [62] = "Earn A or better on level 523 or 524.",
            [63] = "Destroy 100 aircraft and earn C or better on level 621 or 622.",
            [64] = "Earn A or better on level 731 or 732.",
            [65] = "Earn A or better on level 800.",
            [66] = "Earn C or better on 26 campaign missions.",
            [67] = "Unlocked by mission script in Race 1.",
            [68] = "Unlocked by mission script in Race 2.",
            [69] = "Unlocked by mission script in Race 3.",
            [70] = "Unlocked by mission script in Race 4.",
            [71] = "Complete level 741 or 742.",
            [72] = "Complete level 741 or 742.",
            [73] = "Complete level 741 or 742.",
            [74] = "Earn S rank on 20 campaign missions.",
            [75] = "Earn S rank on 40 campaign missions.",
            [76] = "Earn S rank on 43 campaign missions.",
            [77] = "Earn S rank on 43 campaign missions."
        };

        public static GoodieUnlockRequirement Describe(int index)
        {
            if (ExplicitRules.TryGetValue(index, out string? rule))
            {
                string evidence = index is >= 50 and <= 52 or >= 67 and <= 70
                    ? ScriptEvidence
                    : UpdateGoodieEvidence;
                return new GoodieUnlockRequirement(rule, evidence);
            }

            if (index >= 78 && index <= 120)
            {
                return GradeRequirement(index, startIndex: 78, requiredGrade: "C");
            }

            if (index >= 121 && index <= 163)
            {
                return GradeRequirement(index, startIndex: 121, requiredGrade: "B");
            }

            if (index >= 164 && index <= 200)
            {
                return GradeRequirement(index, startIndex: 164, requiredGrade: "A");
            }

            if (index >= 201 && index <= 232)
            {
                int cutsceneId = index == 232 ? 33 : index - 200;
                return new GoodieUnlockRequirement(
                    $"Watch cutscene {cutsceneId} during normal play.",
                    CutsceneEvidence);
            }

            if (index >= 233 && index <= 299)
            {
                return new GoodieUnlockRequirement(
                    "Reserved save slot; preserve bytes.",
                    "CCareer::mGoodies[300] storage");
            }

            return GoodieUnlockRequirement.Unknown;
        }

        private static GoodieUnlockRequirement GradeRequirement(int index, int startIndex, string requiredGrade)
        {
            int offset = index - startIndex;
            if (offset < 0 || offset >= CampaignWorldOrder.Length)
            {
                return GoodieUnlockRequirement.Unknown;
            }

            return new GoodieUnlockRequirement(
                $"Earn {requiredGrade} or better on level {CampaignWorldOrder[offset]}.",
                UpdateGoodieEvidence);
        }
    }
}
