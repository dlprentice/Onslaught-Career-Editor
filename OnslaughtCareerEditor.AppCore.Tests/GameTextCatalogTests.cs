using System;
using System.IO;
using System.Linq;
using System.Text;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Reading the game's own words instead of inventing labels for it.
    ///
    /// The Media page grouped voice lines under "Mission 211" because that is what the filename
    /// says. The game calls that mission "2.11 - Assault On Apollo", and always has - the name was
    /// sitting in `data/language/english.dat`, in a format this project had already worked out and
    /// written down in `tools/language_dat_decode.py`. This is that decoder in C#.
    ///
    /// The parser cases below are synthetic and deterministic. The cases that need a retail file
    /// use the machine's own installation read-only and return early without one, the same way the
    /// save suites handle real career bytes.
    /// </summary>
    public sealed class GameTextCatalogTests
    {
        // ------------------------------------------------------------------ the parse

        [Fact]
        public void DecodesTheIdsTextAndVoiceLineOfEveryEntry()
        {
            byte[] file = TestLanguageFile.Build(
                ("Aquila", "HUD_01"),
                ("Assault On Apollo", null));

            GameTextCatalog? catalog = GameTextCatalogService.Decode(file, @"X:\game\data\language\english.dat");

            Assert.NotNull(catalog);
            Assert.Equal("english", catalog!.LanguageName);
            Assert.Equal(2, catalog.Count);
            Assert.Equal("Aquila", catalog.Entries[0].Text);
            Assert.Equal("HUD_01", catalog.Entries[0].AudioName);
            Assert.Equal("Assault On Apollo", catalog.Entries[1].Text);
            Assert.Null(catalog.Entries[1].AudioName);
        }

        [Theory]
        [InlineData(new byte[0])]
        [InlineData(new byte[] { 0x01, 0x02, 0x03 })]
        public void RefusesSomethingTooSmallToBeALanguageFile(byte[] data)
        {
            Assert.Null(GameTextCatalogService.Decode(data, "x.dat"));
        }

        [Fact]
        public void RefusesAFileThatIsNotALanguageFileAtAll()
        {
            byte[] notALanguageFile = Encoding.ASCII.GetBytes("MZ this is an executable, not a text table");

            Assert.Null(GameTextCatalogService.Decode(notALanguageFile, "BEA.exe"));
        }

        /// <summary>
        /// A count read out of a file is a byte pattern until it has been checked. A hostile or
        /// corrupt one must not become an allocation.
        /// </summary>
        [Fact]
        public void RefusesACountThatWouldNeedMoreFileThanExists()
        {
            byte[] file = TestLanguageFile.Build(("Aquila", null));
            // Overwrite the entry count with something enormous.
            BitConverter.GetBytes(0x0FFFFFFFu).CopyTo(file, 0x08);

            Assert.Null(GameTextCatalogService.Decode(file, "english.dat"));
        }

        [Fact]
        public void RefusesATruncatedFileRatherThanReturningHalfATable()
        {
            byte[] file = TestLanguageFile.Build(("Aquila", null), ("Apollo", null));

            Assert.Null(GameTextCatalogService.Decode(file[..(file.Length / 2)], "english.dat"));
        }

        // ------------------------------------------------------------- the level names

        [Theory]
        [InlineData("2.11 - Assault On Apollo", "2.11", "Assault On Apollo", false)]
        [InlineData("1.00 - Training Level", "1.00", "Training Level", false)]
        [InlineData("5.24 - Enter The Gill-M (Evo)", "5.24", "Enter The Gill-M (Evo)", true)]
        [InlineData("8.00 - The Sentinel Awakes", "8.00", "The Sentinel Awakes", false)]
        public void RecognisesALevelNameByItsShape(string text, string code, string title, bool evolved)
        {
            Assert.True(GameTextCatalogService.TryParseLevelName(text, out GameLevelName? name));
            Assert.NotNull(name);
            Assert.Equal(code, name!.Code);
            Assert.Equal(title, name.Title);
            Assert.Equal(text, name.Display);
            Assert.Equal(evolved, name.IsEvolvedVariant);
        }

        [Theory]
        [InlineData("Episode 1")]
        [InlineData("SELECT LEVEL")]
        [InlineData("Multiplayer Level 1")]
        [InlineData("A Grade on Race Level 1")]
        [InlineData("Damage levels at 50%")]
        [InlineData("2.11 -")]
        [InlineData("2.1 - Too Few Digits")]
        [InlineData("2.111 - Too Many Digits")]
        [InlineData("Mission - Not A Code")]
        [InlineData("")]
        [InlineData(null)]
        public void DoesNotMistakeOtherGameTextForALevelName(string? text)
        {
            Assert.False(GameTextCatalogService.TryParseLevelName(text, out _));
        }

        [Theory]
        [InlineData(100, "1.00")]
        [InlineData(110, "1.10")]
        [InlineData(211, "2.11")]
        [InlineData(231, "2.31")]
        [InlineData(800, "8.00")]
        public void TurnsAFilenamesMissionNumberIntoTheGamesOwnCode(int missionNumber, string expected)
        {
            Assert.Equal(expected, GameTextCatalogService.TryGetLevelCodeForMissionNumber(missionNumber));
        }

        [Theory]
        [InlineData(0)]
        [InlineData(99)]
        [InlineData(1000)]
        [InlineData(-1)]
        public void RefusesToGuessACodeForAMissionNumberOfAShapeNobodyHasSeen(int missionNumber)
        {
            Assert.Null(GameTextCatalogService.TryGetLevelCodeForMissionNumber(missionNumber));
        }

        [Fact]
        public void LevelNamesAreEmptyRatherThanNullWithoutACatalog()
        {
            Assert.Empty(GameTextCatalogService.GetLevelNames(null));
        }

        [Fact]
        public void FindsTheLevelNamesAmongEverythingElseInTheTable()
        {
            byte[] file = TestLanguageFile.Build(
                ("Episode 1", null),
                ("2.11 - Assault On Apollo", null),
                ("HEAT LEVEL CRITICAL", null),
                ("1.00 - Training Level", null),
                ("SELECT LEVEL", null));

            var names = GameTextCatalogService.GetLevelNames(GameTextCatalogService.Decode(file, "english.dat"));

            Assert.Equal(2, names.Count);
            Assert.Equal("1.00", names[0].Code);
            Assert.Equal("2.11", names[1].Code);
        }

        // --------------------------------------------------- against a real installation

        /// <summary>
        /// The claim this whole file exists for, checked against retail bytes: the mission names
        /// are in there, and this decoder finds them.
        ///
        /// The numbers are pinned deliberately. 43 rows through Episode 8 is what
        /// `tools/language_dat_decode.py` produced from the same file on 2026-08-01; if the C# port
        /// ever disagrees with the Python one, that is the interesting failure.
        /// </summary>
        [Fact]
        public void ReadsTheRealMissionNamesOutOfAnInstalledGame()
        {
            string? gameDirectory = FindInstalledGameDirectory();
            if (gameDirectory is null)
                return;

            GameTextCatalog? catalog = GameTextCatalogService.TryLoadFromGameDirectory(gameDirectory);
            if (catalog is null)
                return;

            var names = GameTextCatalogService.GetLevelNames(catalog);

            Assert.Equal(43, names.Count);
            Assert.Contains(names, name => name.Display == "1.00 - Training Level");
            Assert.Contains(names, name => name.Display == "2.11 - Assault On Apollo");
            Assert.Contains(names, name => name.Display == "8.00 - The Sentinel Awakes");
            Assert.Contains(names, name => name.IsEvolvedVariant);

            // Every code has to be reachable from a three-digit filename number, because that is
            // the only join the Media page has.
            foreach (GameLevelName name in names)
            {
                Assert.Contains(
                    Enumerable.Range(100, 900),
                    number => GameTextCatalogService.TryGetLevelCodeForMissionNumber(number) == name.Code);
            }
        }

        [Fact]
        public void AnInstalledGameCarriesFarMoreThanLevelNames()
        {
            string? gameDirectory = FindInstalledGameDirectory();
            if (gameDirectory is null)
                return;

            GameTextCatalog? catalog = GameTextCatalogService.TryLoadFromGameDirectory(gameDirectory);
            if (catalog is null)
                return;

            // Roughly 2,571 strings in the retail English file - unit descriptions, briefing lines,
            // HUD text and backstory prose. This is the raw material for anything the app wants to
            // say in the game's own voice later, so the test states that it is there.
            Assert.True(catalog.Count > 2000, $"Expected a few thousand strings, found {catalog.Count}.");
            Assert.Contains(catalog.Entries, entry => entry.AudioName is { Length: > 0 });
        }

        [Fact]
        public void NoGameFolderMeansNoCatalogRatherThanAFailure()
        {
            Assert.Null(GameTextCatalogService.TryLoadFromGameDirectory(null));
            Assert.Null(GameTextCatalogService.TryLoadFromGameDirectory(string.Empty));
            Assert.Null(GameTextCatalogService.TryLoadFromGameDirectory(
                Path.Combine(Path.GetTempPath(), $"not-a-game-{Guid.NewGuid():N}")));
        }

        private static string? FindInstalledGameDirectory()
        {
            try
            {
                return AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
            }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException or ArgumentException)
            {
                return null;
            }
        }

    }
}
