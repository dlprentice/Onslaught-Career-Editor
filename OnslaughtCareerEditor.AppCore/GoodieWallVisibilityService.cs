namespace Onslaught___Career_Editor
{
    public sealed record GoodieWallVisibility(
        string Summary,
        string EvidenceLabel,
        bool IsSourceGridVisible)
    {
        public static GoodieWallVisibility Unknown { get; } = new(
            "Goodies wall visibility is not mapped yet.",
            "RE follow-up required",
            false);
    }

    public static class GoodieWallVisibilityService
    {
        private const string GridEvidence = GoodieWallGridMappingService.EvidenceLabel;

        public static GoodieWallVisibility Describe(int index)
        {
            if (index is >= 0 and <= 70)
            {
                return Visible("Shown in the known in-game Goodies wall mapping.");
            }

            if (index is >= 71 and <= 73)
            {
                return new GoodieWallVisibility(
                    "Shipped archive exists, but the known in-game Goodies wall mapping does not expose this slot.",
                    GridEvidence,
                    IsSourceGridVisible: false);
            }

            if (index is >= 74 and <= 77)
            {
                return Visible("Shown in the known in-game Goodies wall mapping as a developer item.");
            }

            if (index is >= 78 and <= 200)
            {
                return Visible("Shown in the known in-game Goodies wall mapping as concept art.");
            }

            if (index is >= 201 and <= 231)
            {
                return Visible("Shown in the known in-game Goodies wall mapping as an FMV slot.");
            }

            if (index == 232)
            {
                return Visible("Shown in the known in-game Goodies wall as FMV slot 33; no matching Goodie resource archive is expected.");
            }

            if (index is >= 233 and <= 299)
            {
                return new GoodieWallVisibility(
                    "Reserved save slot, not part of the displayable Goodies wall.",
                    "CCareer::mGoodies[300] storage",
                    IsSourceGridVisible: false);
            }

            return GoodieWallVisibility.Unknown;
        }

        private static GoodieWallVisibility Visible(string summary)
        {
            return new GoodieWallVisibility(summary, GridEvidence, IsSourceGridVisible: true);
        }
    }

    public static class GoodieWallGridMappingService
    {
        public const string EvidenceLabel = "FEPGoodies get_goodie_number 0x0045cb80";

        public static int Resolve(int x, int y)
        {
            if (y == 0)
            {
                if (x is >= 0 and <= 7)
                {
                    return x;
                }

                if (x is >= 8 and <= 12)
                {
                    return x + 58;
                }

                return x switch
                {
                    13 => 74,
                    14 => 75,
                    15 => 76,
                    16 => 77,
                    _ => -1
                };
            }

            if (y == 1 && x is >= 0 and < 58)
            {
                return x + 8;
            }

            if (y == 2 && x is >= 0 and < 32)
            {
                return x + 201;
            }

            if (y == 3 && x is >= 0 and < 123)
            {
                return x + 78;
            }

            return -1;
        }

        public static bool IsSourceGridVisible(int index)
        {
            return index is >= 0 and <= 70 or >= 74 and <= 232;
        }

        public static GoodieWallSlot? Locate(int index)
        {
            if (!IsSourceGridVisible(index))
            {
                return null;
            }

            if (index is >= 0 and <= 7)
            {
                return Slot(index, x: index, y: 0, "Character bios");
            }

            if (index is >= 8 and <= 65)
            {
                return Slot(index, x: index - 8, y: 1, "Unit viewer");
            }

            if (index is >= 66 and <= 70)
            {
                return Slot(index, x: index - 58, y: 0, "Race levels");
            }

            if (index is >= 74 and <= 77)
            {
                return Slot(index, x: index - 61, y: 0, "Developer items");
            }

            if (index is >= 78 and <= 200)
            {
                return Slot(index, x: index - 78, y: 3, "Concept art");
            }

            if (index is >= 201 and <= 232)
            {
                return Slot(index, x: index - 201, y: 2, "Cutscenes");
            }

            return null;
        }

        private static GoodieWallSlot Slot(int index, int x, int y, string groupLabel)
        {
            return new GoodieWallSlot(
                index,
                x,
                y,
                groupLabel,
                $"row {y + 1}, slot {x + 1}");
        }
    }

    public sealed record GoodieWallSlot(
        int Index,
        int X,
        int Y,
        string GroupLabel,
        string PositionLabel);
}
