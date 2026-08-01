using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The Cheats page makes exactly one promise: the file name you are shown is the file name that
/// gets written, and that name is what switches the cheats on. Everything the page does rests on
/// this class getting the name right, so the name rule is pinned here rather than left to the UI.
///
/// The awkward case is the goodie gating code, whose third character is the single byte 0xEA. A
/// C# string comparison passes for that code whatever the encoding, so the tests that matter for
/// it assert bytes, not strings. Encode that name as UTF-8 anywhere in the chain and the byte
/// becomes 0xC3 0xAA and the cheat silently does nothing - which is exactly the failure a string
/// assertion would not catch.
/// </summary>
public class CheatSaveNameComposerTests
{
    private static readonly string[] AllCheatIds =
    [
        CheatCodeCatalog.AllGoodiesId,
        CheatCodeCatalog.AllLevelsId,
        CheatCodeCatalog.GodModeId,
        CheatCodeCatalog.FreeCameraId,
        CheatCodeCatalog.GoodieGatingBypassId,
    ];

    [Test]
    public void ThreeCheatsWithNoNameOfYourOwn_ProduceTheFileNameTheUiPromises()
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            baseName: null,
            [CheatCodeCatalog.AllGoodiesId, CheatCodeCatalog.AllLevelsId, CheatCodeCatalog.GodModeId]);

        Assert.That(composed.IsUsable, Is.True, composed.Problem);
        Assert.That(composed.Name, Is.EqualTo("MALLOYTURKEYMaladim"));
        Assert.That(composed.FileName, Is.EqualTo("MALLOYTURKEYMaladim.bes"));
    }

    [Test]
    public void OneNameCarriesSeveralCodesAndSwitchesOnSeveralCheats()
    {
        // This is the whole reason the feature is one file rather than one file per cheat: the
        // game runs strstr once per code, so codes stack inside a single name.
        CheatSaveName composed = CheatSaveNameComposer.Compose("MyCareer", AllCheatIds);

        Assert.That(composed.IsUsable, Is.True, composed.Problem);
        Assert.That(composed.ActiveCheatIds, Is.EquivalentTo(AllCheatIds));
        Assert.That(composed.Name, Does.StartWith("MyCareer"));
    }

    [Test]
    public void CodesAreAppendedInCatalogOrderSoTheNameIsDeterministic()
    {
        CheatSaveName forwards = CheatSaveNameComposer.Compose(
            "X",
            [CheatCodeCatalog.GodModeId, CheatCodeCatalog.AllGoodiesId]);
        CheatSaveName backwards = CheatSaveNameComposer.Compose(
            "X",
            [CheatCodeCatalog.AllGoodiesId, CheatCodeCatalog.GodModeId]);

        Assert.That(forwards.Name, Is.EqualTo(backwards.Name));
        Assert.That(forwards.Name, Is.EqualTo("XMALLOYMaladim"));
    }

    [Test]
    public void ACodeAlreadyInsideTheTypedNameIsNotAppendedAgain()
    {
        // Substring matching means "MyMALLOYSave" already switches the cheat on. Appending the
        // code a second time would lengthen the name for nothing.
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            "MyMALLOYSave",
            [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(composed.IsUsable, Is.True, composed.Problem);
        Assert.That(composed.Name, Is.EqualTo("MyMALLOYSave"));
        Assert.That(composed.AppendedCheatIds, Is.Empty);
        Assert.That(composed.ActiveCheatIds, Is.EqualTo(new[] { CheatCodeCatalog.AllGoodiesId }));
    }

    [Test]
    public void ACheatHiddenInsideTheTypedNameIsReportedEvenThoughItWasNotAskedFor()
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            "TURKEYdinner",
            [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(composed.RequestedCheatIds, Is.EqualTo(new[] { CheatCodeCatalog.AllGoodiesId }));
        Assert.That(
            composed.ActiveCheatIds,
            Does.Contain(CheatCodeCatalog.AllLevelsId),
            "A name that already contains a code switches that cheat on whether the player meant it or not, " +
            "so the page has to be able to say so.");
    }

    [Test]
    public void TheGoodieGatingCodeReachesTheGameAsTheSingleByte0xEA()
    {
        // The bytes the game compares are the low byte of each UTF-16 unit of the file name
        // (FromWCHAR at 0x004f7d30, called from IsCheatActive at 0x004654f8). "lat" + 0xEA + "te"
        // is what has to be in there. Asserting the C# string would pass even for a name that
        // could never match.
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            baseName: null,
            [CheatCodeCatalog.GoodieGatingBypassId]);

        Assert.That(composed.IsUsable, Is.True, composed.Problem);

        byte[] bytes = CheatSaveNameComposer.ToGameComparisonBytes(composed.Name);
        Assert.That(
            bytes,
            Is.EqualTo(new byte[] { 0x6C, 0x61, 0x74, 0xEA, 0x74, 0x65 }),
            "The goodie gating code must reach the game as lat<0xEA>te. Two bytes 0xC3 0xAA here " +
            "would mean the name had been encoded as UTF-8 and the cheat would do nothing.");
    }

    [Test]
    public void EveryOfferedCodeSurvivesTheGamesOwnByteComparison()
    {
        foreach (CheatCode cheat in CheatCodeCatalog.All)
        {
            CheatSaveName composed = CheatSaveNameComposer.Compose("Save", [cheat.Id]);

            Assert.That(composed.IsUsable, Is.True, $"{cheat.Id}: {composed.Problem}");
            Assert.That(
                CheatSaveNameComposer.GameBytesContainCode(composed.Name, cheat.Code),
                Is.True,
                $"{cheat.Id} must be findable in the composed name by the byte comparison the game performs.");
        }
    }

    [Test]
    public void EveryCombinationOfCheatsProducesALegalWindowsFileName()
    {
        char[] invalid = Path.GetInvalidFileNameChars();

        foreach (string[] subset in NonEmptySubsets(AllCheatIds))
        {
            CheatSaveName composed = CheatSaveNameComposer.Compose("Save", subset);

            Assert.That(composed.IsUsable, Is.True, $"{string.Join("+", subset)}: {composed.Problem}");
            Assert.That(
                composed.FileName.IndexOfAny(invalid),
                Is.EqualTo(-1),
                $"{composed.FileName} is not a legal Windows file name.");
            Assert.That(composed.FileName, Does.EndWith(".bes"));
            Assert.That(Path.GetFileName(composed.FileName), Is.EqualTo(composed.FileName),
                "The composed name must be a bare file name, never a path.");
        }
    }

    [Test]
    public void EveryCombinationRoundTrips_TheNameReadsBackAsExactlyTheCheatsRequested()
    {
        foreach (string[] subset in NonEmptySubsets(AllCheatIds))
        {
            CheatSaveName composed = CheatSaveNameComposer.Compose("Save", subset);

            Assert.That(
                CheatSaveNameComposer.ActiveCheatIdsIn(composed.Name),
                Is.EquivalentTo(subset),
                $"Composing {string.Join("+", subset)} produced '{composed.Name}', which does not read back the same.");
        }
    }

    [TestCase("bad/name")]
    [TestCase("bad\\name")]
    [TestCase("bad:name")]
    [TestCase("bad*name")]
    [TestCase("bad?name")]
    public void FileNameCharactersWindowsForbids_AreRefusedWithAReason(string typed)
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose(typed, [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(composed.IsUsable, Is.False);
        Assert.That(composed.Problem, Is.Not.Null.And.Not.Empty);
    }

    [Test]
    public void AReservedWindowsDeviceNameIsRefused()
    {
        // "NUL" plus no cheats would be a file Windows will not let you create.
        CheatSaveName composed = CheatSaveNameComposer.Compose("NUL", Array.Empty<string>());

        Assert.That(composed.IsUsable, Is.False);
        Assert.That(composed.Problem, Does.Contain("NUL"));
    }

    [Test]
    public void CharactersTheGameCannotReadAreRefusedRatherThanSilentlyMangled()
    {
        // The game truncates each character to its low byte, so U+0100 would reach it as 0x00 and
        // the name it sees would not be the name the player typed.
        CheatSaveName composed = CheatSaveNameComposer.Compose(
            "Save\u0100",
            [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(composed.IsUsable, Is.False);
        Assert.That(composed.Problem, Is.Not.Null.And.Not.Empty);
    }

    [Test]
    public void NoCheatsAndNoNameIsRefusedInsteadOfWritingAnEmptyFileName()
    {
        CheatSaveName composed = CheatSaveNameComposer.Compose(null, Array.Empty<string>());

        Assert.That(composed.IsUsable, Is.False);
        Assert.That(composed.FileName, Is.Empty);
    }

    [Test]
    public void AnOverlongNameIsRefusedAndSaysHowLongItGot()
    {
        string typed = new('a', CheatSaveNameComposer.MaximumNameLength);
        CheatSaveName composed = CheatSaveNameComposer.Compose(typed, [CheatCodeCatalog.AllGoodiesId]);

        Assert.That(composed.IsUsable, Is.False);
        Assert.That(composed.Problem, Does.Contain(CheatSaveNameComposer.MaximumNameLength.ToString()));
    }

    [Test]
    public void MatchingIsCaseSensitiveBecauseTheGamesComparisonIs()
    {
        Assert.That(CheatSaveNameComposer.NameActivates("mymalloysave", CheatCodeCatalog.AllGoodiesId), Is.False);
        Assert.That(CheatSaveNameComposer.NameActivates("myMALLOYsave", CheatCodeCatalog.AllGoodiesId), Is.True);
    }

    private static IEnumerable<string[]> NonEmptySubsets(IReadOnlyList<string> values)
    {
        for (int mask = 1; mask < 1 << values.Count; mask++)
        {
            yield return Enumerable.Range(0, values.Count)
                .Where(index => (mask & (1 << index)) != 0)
                .Select(index => values[index])
                .ToArray();
        }
    }
}
