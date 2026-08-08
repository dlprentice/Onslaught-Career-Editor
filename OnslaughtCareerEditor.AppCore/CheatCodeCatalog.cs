using System;
using System.Collections.Generic;
using System.Linq;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// How far the evidence for one cheat actually goes. The page copy is written from this
    /// value, so a cheat cannot quietly be presented as tested when it was only read out of
    /// the executable.
    /// </summary>
    public enum CheatEvidenceLevel
    {
        /// <summary>Watched working in the released game on the supported Steam specimen.</summary>
        SeenWorkingInGame,

        /// <summary>Found in the game's own code. Nobody has watched it work here yet.</summary>
        FoundInGameCodeOnly,
    }

    /// <summary>
    /// One retail cheat that the released game turns on when the save game name contains a
    /// particular piece of text.
    /// </summary>
    /// <param name="Id">Stable identifier used by the UI and by saved selections.</param>
    /// <param name="RetailCheatIndex">The index this code occupies in the game's own cheat table.</param>
    /// <param name="Code">
    /// The exact text the game looks for. Case matters, and it is compared with
    /// <c>strstr</c>, so it only has to appear somewhere inside the name.
    /// </param>
    /// <param name="DisplayName">Short player-facing name.</param>
    /// <param name="WhatItDoes">One plain sentence describing the effect.</param>
    /// <param name="WhatWeKnow">
    /// The honest evidence sentence. This is shown next to the toggle; it must never
    /// promise more than the evidence supports.
    /// </param>
    /// <param name="Evidence">How far that evidence goes.</param>
    public sealed record CheatCode(
        string Id,
        int RetailCheatIndex,
        string Code,
        string DisplayName,
        string WhatItDoes,
        string WhatWeKnow,
        CheatEvidenceLevel Evidence);

    /// <summary>
    /// The cheats this app is willing to offer, and the evidence behind each.
    ///
    /// The mechanism is the game's own: <c>CCareer::IsCheatActive</c> (0x00465490) XOR-decrypts a
    /// small table with the plaintext key "HELP ME!!" and then calls
    /// <c>strstr(saveName, decryptedCode)</c>. A cheat is on when the save game name *contains*
    /// the code, so one name can carry several codes at once.
    /// (reverse-engineering/binary-analysis/functions/FEPSaveGame.cpp/IsCheatActive.md and
    /// reverse-engineering/game-mechanics/cheat-codes.md.)
    ///
    /// The six decoded codes were re-read from the pristine specimen
    /// local-lab/safe-copy-bea-pristine/BEA.exe.original.backup, sha256
    /// 74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750, 2,506,752 bytes: key at
    /// file offset 0x229A64, table at 0x229464, one 256-byte block per index, first nine bytes
    /// XORed with the key.
    ///
    /// Index 2 (<c>V3R5IOF</c>) is deliberately absent. It decodes out of the cheat table but no
    /// call site has ever been found for it, so offering it would be offering a switch wired to
    /// nothing (cheat-codes.md line 124).
    ///
    /// Index 5's third character is the single byte 0xEA. It is written here as the UTF-16
    /// character U+00EA, which is what a Windows file name stores and what the game's own
    /// WCHAR-to-byte conversion truncates back to 0xEA. See
    /// <see cref="CheatSaveNameComposer.ToGameComparisonBytes"/>.
    /// </summary>
    public static class CheatCodeCatalog
    {
        public const string AllGoodiesId = "all-goodies";
        public const string AllLevelsId = "all-levels";
        public const string GodModeId = "god-mode";
        public const string FreeCameraId = "free-camera";
        public const string GoodieGatingBypassId = "goodie-gating-bypass";

        private static readonly CheatCode[] s_all =
        {
            new(
                Id: AllGoodiesId,
                RetailCheatIndex: 0,
                Code: "MALLOY",
                DisplayName: "All goodies",
                WhatItDoes: "Opens up the Goodies gallery so the unlockable art and extras are all available.",
                WhatWeKnow: "Confirmed working in the Steam release. No patching needed - the game has always done this.",
                Evidence: CheatEvidenceLevel.SeenWorkingInGame),
            new(
                Id: AllLevelsId,
                RetailCheatIndex: 1,
                Code: "TURKEY",
                DisplayName: "All levels",
                WhatItDoes: "Unlocks every campaign mission, so you can jump straight to the one you want.",
                WhatWeKnow: "Confirmed working in the Steam release. No patching needed - the game has always done this.",
                Evidence: CheatEvidenceLevel.SeenWorkingInGame),
            new(
                Id: GodModeId,
                RetailCheatIndex: 3,
                Code: "Maladim",
                DisplayName: "God mode",
                WhatItDoes: "Adds a God ON / God OFF line to Controller Options in the pause menu.",
                WhatWeKnow: "Seen working: the line appears, and turning it on stops normal combat damage sticking. "
                    + "Hull you already lost is not repaired, and hazards other than combat damage were never tested.",
                Evidence: CheatEvidenceLevel.SeenWorkingInGame),
            new(
                Id: FreeCameraId,
                RetailCheatIndex: 4,
                Code: "Aurore",
                DisplayName: "Free camera",
                WhatItDoes: "Unlocks the developers' free-camera toggle, a debug button the game normally keeps switched off.",
                WhatWeKnow: "Found in the game's code, where it guards the free-camera button. We have not watched it "
                    + "work from a save name, and there is no evidence about how you move the camera once it is on.",
                Evidence: CheatEvidenceLevel.FoundInGameCodeOnly),
            new(
                Id: GoodieGatingBypassId,
                RetailCheatIndex: 5,
                // Written as an escape on purpose. The third character is the single byte 0xEA in
                // the game's table; spelling it out here keeps this source file pure ASCII so no
                // editor or encoding guess can turn it into the two UTF-8 bytes 0xC3 0xAA, which
                // would never match.
                Code: "lat\u00EAte",
                DisplayName: "Goodie gating bypass",
                WhatItDoes: "A second, different developer view of the Goodies wall - it skips the unlock rules and shows "
                    + "each goodie in a different state from the All goodies cheat.",
                WhatWeKnow: "Found in the game's code alongside All goodies. We have not watched it work. "
                    + "Its code contains an accented character, so the file name will too.",
                Evidence: CheatEvidenceLevel.FoundInGameCodeOnly),
        };

        /// <summary>The offered cheats, in the order the page shows them.</summary>
        public static IReadOnlyList<CheatCode> All => s_all;

        public static CheatCode? FindById(string? id)
        {
            if (string.IsNullOrWhiteSpace(id))
            {
                return null;
            }

            return s_all.FirstOrDefault(cheat =>
                string.Equals(cheat.Id, id.Trim(), StringComparison.OrdinalIgnoreCase));
        }

        /// <summary>
        /// Resolve ids to catalog entries in catalog order, ignoring blanks and unknown ids and
        /// collapsing duplicates. Catalog order is what makes a composed name deterministic.
        /// </summary>
        public static IReadOnlyList<CheatCode> Resolve(IEnumerable<string>? ids)
        {
            if (ids is null)
            {
                return Array.Empty<CheatCode>();
            }

            var wanted = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (string id in ids)
            {
                if (!string.IsNullOrWhiteSpace(id))
                {
                    wanted.Add(id.Trim());
                }
            }

            return s_all.Where(cheat => wanted.Contains(cheat.Id)).ToArray();
        }
    }
}
