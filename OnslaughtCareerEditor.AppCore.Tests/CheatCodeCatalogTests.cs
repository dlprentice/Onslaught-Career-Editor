using System;
using System.Linq;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Pins the cheat catalog against the decoded retail table and against the two ways this
    /// feature can fail silently.
    ///
    /// The first is offering a cheat nothing in the game ever consults: index 2 decodes out of the
    /// table but has no known call site, so a toggle for it would look identical to a working one
    /// and do nothing. The second is encoding: index 5's third character is the single byte 0xEA,
    /// and if it ever reaches the game as the two UTF-8 bytes 0xC3 0xAA the cheat quietly stops
    /// matching while every C# string comparison still passes. Both are asserted here.
    ///
    /// Codes re-read from the pristine specimen
    /// local-lab/safe-copy-bea-pristine/BEA.exe.original.backup, sha256 74154bfa..., table at file
    /// offset 0x229464 with the key "HELP ME!!" at 0x229A64.
    /// </summary>
    public class CheatCodeCatalogTests
    {
        [Theory]
        [InlineData(CheatCodeCatalog.AllGoodiesId, 0, "MALLOY")]
        [InlineData(CheatCodeCatalog.AllLevelsId, 1, "TURKEY")]
        [InlineData(CheatCodeCatalog.GodModeId, 3, "Maladim")]
        [InlineData(CheatCodeCatalog.FreeCameraId, 4, "Aurore")]
        [InlineData(CheatCodeCatalog.GoodieGatingBypassId, 5, "lat\u00EAte")]
        public void EachOfferedCheatCarriesItsDecodedRetailCode(string id, int index, string code)
        {
            CheatCode? cheat = CheatCodeCatalog.FindById(id);

            Assert.NotNull(cheat);
            Assert.Equal(index, cheat!.RetailCheatIndex);
            Assert.Equal(code, cheat.Code);
        }

        [Fact]
        public void CheatIndexTwoIsNotOffered_BecauseNoCallSiteForItHasEverBeenFound()
        {
            Assert.DoesNotContain(2, CheatCodeCatalog.All.Select(cheat => cheat.RetailCheatIndex));
            Assert.DoesNotContain("V3R5IOF", CheatCodeCatalog.All.Select(cheat => cheat.Code));
        }

        [Fact]
        public void TheGoodieGatingCodeIsTheSingleByte0xEA_NotTheTwoUtf8BytesForTheSameLetter()
        {
            CheatCode cheat = CheatCodeCatalog.FindById(CheatCodeCatalog.GoodieGatingBypassId)!;

            byte[] bytes = CheatSaveNameComposer.ToGameComparisonBytes(cheat.Code);

            Assert.Equal(new byte[] { 0x6C, 0x61, 0x74, 0xEA, 0x74, 0x65 }, bytes);
            Assert.DoesNotContain(bytes, value => value == 0xC3);
        }

        [Fact]
        public void EveryCheatHasAnIdACodeAndBothHalvesOfItsCopy()
        {
            Assert.NotEmpty(CheatCodeCatalog.All);
            Assert.All(CheatCodeCatalog.All, cheat =>
            {
                Assert.False(string.IsNullOrWhiteSpace(cheat.Id));
                Assert.False(string.IsNullOrWhiteSpace(cheat.Code));
                Assert.False(string.IsNullOrWhiteSpace(cheat.DisplayName));
                Assert.False(string.IsNullOrWhiteSpace(cheat.WhatItDoes));
                Assert.False(string.IsNullOrWhiteSpace(cheat.WhatWeKnow));
            });
        }

        [Fact]
        public void IdsAndCodesAreUnique_SoOneTickBoxCannotStandForTwoCheats()
        {
            Assert.Equal(
                CheatCodeCatalog.All.Count,
                CheatCodeCatalog.All.Select(cheat => cheat.Id).Distinct(StringComparer.OrdinalIgnoreCase).Count());
            Assert.Equal(
                CheatCodeCatalog.All.Count,
                CheatCodeCatalog.All.Select(cheat => cheat.Code).Distinct(StringComparer.Ordinal).Count());
        }

        [Fact]
        public void NoCodeIsASubstringOfAnother_SoTickingOneCannotImplyAnother()
        {
            foreach (CheatCode outer in CheatCodeCatalog.All)
            {
                foreach (CheatCode inner in CheatCodeCatalog.All.Where(other => other.Id != outer.Id))
                {
                    Assert.False(
                        CheatSaveNameComposer.GameBytesContainCode(outer.Code, inner.Code),
                        $"{inner.Id} is a substring of {outer.Id}; the game would switch both on.");
                }
            }
        }

        [Fact]
        public void ResolveKeepsCatalogOrderAndIgnoresJunk()
        {
            var resolved = CheatCodeCatalog.Resolve(
            [
                CheatCodeCatalog.GodModeId,
                "not-a-cheat",
                "  ",
                CheatCodeCatalog.AllGoodiesId,
                CheatCodeCatalog.AllGoodiesId,
            ]);

            Assert.Equal(
                new[] { CheatCodeCatalog.AllGoodiesId, CheatCodeCatalog.GodModeId },
                resolved.Select(cheat => cheat.Id));
        }

        [Fact]
        public void ComposingEveryCheatAtOnceProducesOneUsableName()
        {
            CheatSaveName composed = CheatSaveNameComposer.Compose(
                baseName: null,
                CheatCodeCatalog.All.Select(cheat => cheat.Id));

            Assert.Null(composed.Problem);
            Assert.Equal(
                CheatCodeCatalog.All.Select(cheat => cheat.Id).OrderBy(id => id),
                composed.ActiveCheatIds.OrderBy(id => id));
        }
    }
}
