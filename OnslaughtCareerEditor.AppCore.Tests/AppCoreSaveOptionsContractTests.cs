using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    public sealed class AppCoreSaveOptionsContractTests
    {
        [Fact]
        public void SaveAndSlotCodecsShareContainerConstants()
        {
            Assert.Equal(10004, BesFilePatcher.EXPECTED_FILE_SIZE);
            Assert.Equal(BesFilePatcher.EXPECTED_FILE_SIZE, MissionScriptSlotBitsetSaveCodec.ExpectedFileSize);
            Assert.Equal(0x4BD1, BesFilePatcher.VERSION_WORD);
            Assert.Equal(BesFilePatcher.VERSION_WORD, MissionScriptSlotBitsetSaveCodec.VersionWord);
            Assert.Equal(0x240A, MissionScriptSlotBitsetSaveCodec.CareerSlotsBaseOffset);
            Assert.Equal(0x248A, MissionScriptSlotBitsetSaveCodec.CareerSlotsEndExclusive);
        }

        [Theory]
        [InlineData(@"C:\temp\defaultoptions.bea")]
        [InlineData(@"C:\temp\defaultoptions.bea.20260609.bak")]
        [InlineData(@"C:\temp\settings.bea")]
        public void CommonSavePatchRejectsOptionsLikePaths(string path)
        {
            PatchResult result = SaveEditorService.PatchSave(new SavePatchRequest
            {
                InputPath = path,
                OutputPath = @"C:\temp\career_patched.bes",
                PatchKills = true,
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false
            });

            Assert.False(result.Success);
            Assert.Contains(".bes career save", result.Message);
        }

        [Fact]
        public void ConfigurationPendingChangeDetectionRequiresExplicitMutationIntent()
        {
            ConfigurationPatchRequest request = new();

            Assert.False(ConfigurationEditorService.HasPendingChanges(request));
            Assert.Contains("No pending configuration changes", ConfigurationEditorService.BuildPendingChangesSummary(request));
        }
    }
}
