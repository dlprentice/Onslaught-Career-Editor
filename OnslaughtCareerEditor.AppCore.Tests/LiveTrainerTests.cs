using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The live trainer, exercised without a game.
    ///
    /// Everything worth being afraid of in this feature is decided before a single Win32 call:
    /// which process may be opened, whether the numbers that came back are believable, and whether
    /// a write is allowed to happen. All three are pure functions of an address space and a
    /// process record, so all three are pinned here against a fake.
    ///
    /// The one thing these tests cannot establish is whether the field positions are right. Nobody
    /// has read them from a running game, and no test in this repository can change that.
    /// </summary>
    public sealed class LiveTrainerTests
    {
        private const uint PlayerPointer = 0x0A000000;
        private const uint BattleEnginePointer = 0x0B000000;

        // ============================================================ the attach gate

        [Fact]
        public void AttachRefusesAProcessTheAppNeverLaunched_AndOpensNothing()
        {
            using var world = new TrainerWorld();
            GameProfileManagedProcess stranger = world.BuildProcessRecord(processId: 4242);
            // Deliberately not registered.

            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(
                stranger,
                world.Registry,
                world.LiveProbe(stranger));

            Assert.False(decision.Allowed);
            Assert.Equal(LiveTrainerAttachRefusal.NotAManagedProcess, decision.Refusal);

            LiveTrainerAttachOutcome outcome = LiveTrainerSession.Attach(
                stranger, world.Registry, world.Factory, world.LiveProbe(stranger));

            Assert.False(outcome.Success);
            Assert.Null(outcome.Session);
            Assert.Empty(world.Factory.Opens);
        }

        [Fact]
        public void AttachRefusesARegisteredRecordWhoseProcessStartedAtADifferentTime()
        {
            // The same process id, the same executable on disk, a different process. Only the
            // start-time comparison can tell these apart, and Windows recycles process ids.
            using var world = new TrainerWorld();
            GameProfileManagedProcess registered = world.RegisterProcess();
            var recycled = new FakeLivenessProbe(registered.StartedAt.AddSeconds(30), registered.ExecutablePath);

            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(registered, world.Registry, recycled);

            Assert.False(decision.Allowed);
            Assert.Equal(LiveTrainerAttachRefusal.ProcessIdentityChanged, decision.Refusal);
            Assert.Empty(world.Factory.Opens);
        }

        [Fact]
        public void AttachRefusesARegisteredRecordWhoseProcessIsNowADifferentExecutable()
        {
            using var world = new TrainerWorld();
            GameProfileManagedProcess registered = world.RegisterProcess();
            var impostor = new FakeLivenessProbe(
                registered.StartedAt,
                Path.Combine(Path.GetTempPath(), "somewhere-else", "BEA.exe"));

            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(registered, world.Registry, impostor);

            Assert.False(decision.Allowed);
            Assert.Equal(LiveTrainerAttachRefusal.ProcessIdentityChanged, decision.Refusal);
        }

        [Fact]
        public void AttachRefusesAProcessThatIsNoLongerRunning()
        {
            using var world = new TrainerWorld();
            GameProfileManagedProcess registered = world.RegisterProcess();

            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(
                registered, world.Registry, new FakeLivenessProbe());

            Assert.False(decision.Allowed);
            Assert.Equal(LiveTrainerAttachRefusal.NotRunning, decision.Refusal);
        }

        [Theory]
        [InlineData(@"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe")]
        [InlineData(@"D:\SteamLibrary\steamapps\common\Battle Engine Aquila\BEA.exe")]
        [InlineData(@"E:\Games\steamapps\common\Battle Engine Aquila\subdir\BEA.exe")]
        public void TheInstalledGameIsRefusedByName_NotJustByNotBeingRegistered(string installedExe)
        {
            using var world = new TrainerWorld();
            var installed = new GameProfileManagedProcess(
                ProcessId: 777,
                ExecutablePath: installedExe,
                WorkingDirectory: Path.GetDirectoryName(installedExe)!,
                Arguments: Array.Empty<string>(),
                StartedAt: DateTimeOffset.UtcNow,
                ManifestPath: Path.Combine(Path.GetDirectoryName(installedExe)!, "onslaught-profile-manifest.json"));

            LiveTrainerAttachDecision decision = LiveTrainerAttachPolicy.Decide(
                installed, world.Registry, new FakeLivenessProbe(installed.StartedAt, installedExe));

            Assert.False(decision.Allowed);
            Assert.Equal(LiveTrainerAttachRefusal.InstalledGameDirectory, decision.Refusal);
            Assert.Contains("installed game", decision.Message, StringComparison.OrdinalIgnoreCase);
            Assert.Empty(world.Factory.Opens);
        }

        [Fact]
        public void AnAppOwnedCopyIsNotMistakenForTheInstalledGame()
        {
            Assert.False(LiveTrainerAttachPolicy.LooksLikeAnInstalledGameDirectory(
                Path.Combine(Path.GetTempPath(), "GameProfiles", "safe-copy-1", "BEA.exe")));
        }

        [Fact]
        public void AttachOpensWithReadAccessOnly()
        {
            using var world = new TrainerWorld();
            GameProfileManagedProcess registered = world.RegisterProcess();

            LiveTrainerAttachOutcome outcome = LiveTrainerSession.Attach(
                registered, world.Registry, world.Factory, world.LiveProbe(registered));

            Assert.True(outcome.Success);
            using LiveTrainerSession session = outcome.Session!;
            Assert.Single(world.Factory.Opens);
            Assert.Equal(ProcessMemoryAccess.Read, world.Factory.Opens[0].Access);
            Assert.False(session.HasWriteAccess);
        }

        // ============================================================ reading

        [Fact]
        public void AnEmptyPlayerTableReadsAsNoMissionRunning_AndOffersNothing()
        {
            // This is the state the 2026-08-01 probe actually found: 32 bytes of zero.
            using var world = new TrainerWorld();
            world.Memory.Map(LiveTrainerAddresses.PlayerTable, LiveTrainerAddresses.PlayerTableByteCount);
            using LiveTrainerSession session = world.Attach();

            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.NoMissionRunning, reading.Status);
            Assert.Null(reading.Vitals);
            Assert.False(reading.WritingCanBeOffered);
            Assert.Contains("mission", reading.Message, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void AnUnreadablePlayerTableMeansTheProcessHasGone()
        {
            using var world = new TrainerWorld();
            using LiveTrainerSession session = world.Attach();

            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.ProcessGone, reading.Status);
            Assert.False(reading.WritingCanBeOffered);
        }

        [Fact]
        public void ReadingFollowsThePlayerToItsBattleEngine_NotTheVitalsOffThePlayerItself()
        {
            // The vitals hang off CBattleEngine at player+0x1c, not off the player. Skipping that
            // hop reads plausible-looking rubbish, which is the one failure this whole design is
            // built to make impossible - so it gets its own test with decoy values in place.
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 17.5f, shields: 8f, state: LiveTrainerBattleEngineState.Walker);
            world.Memory.PutSingle(PlayerPointer + LiveTrainerAddresses.LifeOffset, 999f);
            world.Memory.PutSingle(PlayerPointer + LiveTrainerAddresses.EnergyOffset, 998f);

            using LiveTrainerSession session = world.Attach();
            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.Read, reading.Status);
            LivePlayerVitals vitals = reading.Vitals!;
            Assert.Equal(PlayerPointer, vitals.PlayerPointer);
            Assert.Equal(BattleEnginePointer, vitals.BattleEnginePointer);
            Assert.Equal(42f, vitals.Life.AsSingle);
            Assert.Equal(17.5f, vitals.Energy.AsSingle);
            Assert.Equal(8f, vitals.Shields.AsSingle);
            Assert.Equal(BattleEnginePointer + LiveTrainerAddresses.LifeOffset, vitals.Life.Address);
            Assert.Equal(BattleEnginePointer + LiveTrainerAddresses.StateOffset, vitals.State.Address);
            Assert.Equal("walker", vitals.StateName);
            Assert.True(reading.WritingCanBeOffered);
        }

        [Fact]
        public void APlayerWithNoBattleEngineYetIsItsOwnAnswer()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 1f, shields: 1f, state: 2);
            world.Memory.PutUInt32(PlayerPointer + (uint)LiveTrainerAddresses.BattleEngineOffsetInPlayer, 0);

            using LiveTrainerSession session = world.Attach();
            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.NoBattleEngine, reading.Status);
            Assert.False(reading.WritingCanBeOffered);
        }

        [Theory]
        [InlineData(0x00000004u)]  // below the lowest user address
        [InlineData(0x0A000001u)]  // not four-byte aligned
        [InlineData(0xFFFFFFF0u)]  // kernel side
        public void APointerThatCannotBeAnObjectIsRefusedRatherThanFollowed(uint rubbish)
        {
            using var world = new TrainerWorld();
            world.Memory.Map(LiveTrainerAddresses.PlayerTable, LiveTrainerAddresses.PlayerTableByteCount);
            world.Memory.PutUInt32(LiveTrainerAddresses.PlayerTable, rubbish);

            using LiveTrainerSession session = world.Attach();
            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.PointerImplausible, reading.Status);
            Assert.False(reading.WritingCanBeOffered);
        }

        [Fact]
        public void APlayerThatVanishesBetweenTheTwoHopsIsReportedRatherThanGuessedAt()
        {
            using var world = new TrainerWorld();
            world.Memory.Map(LiveTrainerAddresses.PlayerTable, LiveTrainerAddresses.PlayerTableByteCount);
            world.Memory.PutUInt32(LiveTrainerAddresses.PlayerTable, PlayerPointer);
            // The player pointer is fine, but nothing is mapped behind it.

            using LiveTrainerSession session = world.Attach();
            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.PlayerUnreadable, reading.Status);
        }

        // ============================================================ the write gate

        [Fact]
        public void WholeNumberVitalsAreNotWrittenThrough_BecauseThatIsWhatAWrongGuessLooksLike()
        {
            // If the fields turn out to hold integers rather than floats, a health of 100 reads as
            // the subnormal float 1.4E-43. The plausibility rule rejects that, so the app refuses
            // to write exactly in the case where it has guessed the type wrong. This is the single
            // most important property in the feature and it is deliberately not a comment.
            using var world = new TrainerWorld();
            world.PutRunningMission(lifeBits: 100u, energyBits: 250u, shieldsBits: 50u, state: 2);

            using LiveTrainerSession session = world.Attach();
            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.Read, reading.Status);
            Assert.False(reading.Vitals!.Life.LooksLikeAVital);
            Assert.False(reading.WritingCanBeOffered);

            LiveTrainerWriteOutcome outcome = session.Write(LiveTrainerVital.Life, 500f);

            Assert.False(outcome.Success);
            Assert.Empty(world.Memory.Writes);
            Assert.False(session.HasWriteAccess);
        }

        [Fact]
        public void AllZeroVitalsAreNotAPlausibleRead()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 0f, energy: 0f, shields: 0f, state: 0);

            using LiveTrainerSession session = world.Attach();
            LiveTrainerReadResult reading = session.Read();

            Assert.Equal(LiveTrainerReadStatus.Read, reading.Status);
            Assert.False(reading.WritingCanBeOffered);
        }

        [Fact]
        public void WritingIsRefusedEntirelyWhenNoMissionIsRunning()
        {
            using var world = new TrainerWorld();
            world.Memory.Map(LiveTrainerAddresses.PlayerTable, LiveTrainerAddresses.PlayerTableByteCount);

            using LiveTrainerSession session = world.Attach();
            LiveTrainerWriteOutcome outcome = session.Write(LiveTrainerVital.Shields, 100f);

            Assert.False(outcome.Success);
            Assert.Empty(world.Memory.Writes);
            Assert.Single(world.Factory.Opens);
        }

        [Fact]
        public void AWriteReadsItsOwnAddressFirst_AndOnlyThenAsksForWriteAccess()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);

            using LiveTrainerSession session = world.Attach();
            Assert.Single(world.Factory.Opens);
            Assert.Equal(ProcessMemoryAccess.Read, world.Factory.Opens[0].Access);

            world.Memory.Reads.Clear();
            LiveTrainerWriteOutcome outcome = session.Write(LiveTrainerVital.Life, 500f);

            Assert.True(outcome.Success, outcome.Message);
            uint lifeAddress = BattleEnginePointer + LiveTrainerAddresses.LifeOffset;

            // The whole battle engine was read before the write, and that read covers the address.
            int firstWriteIndex = world.Memory.Operations.FindIndex(op => op.IsWrite && op.Address == lifeAddress);
            int coveringReadIndex = world.Memory.Operations.FindIndex(op =>
                !op.IsWrite && op.Address <= lifeAddress && op.Address + (uint)op.Length >= lifeAddress + 4);
            Assert.True(coveringReadIndex >= 0, "The write address must have been read.");
            Assert.True(coveringReadIndex < firstWriteIndex, "The read must happen before the write.");

            Assert.Equal(2, world.Factory.Opens.Count);
            Assert.Equal(ProcessMemoryAccess.ReadWrite, world.Factory.Opens[1].Access);
            Assert.True(session.HasWriteAccess);
            Assert.Equal(500f, BitConverter.ToSingle(world.Memory.Writes.Single().Data));
        }

        [Fact]
        public void AWriteReportsWhatItReadBackWithoutTreatingADifferenceAsFailure()
        {
            // The game simulates at 20 Hz and is entitled to have changed the value again by the
            // time the app looks. That is not a failed write and must not be reported as one.
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();

            world.Memory.OverwriteWritesWith = 7f;
            LiveTrainerWriteOutcome outcome = session.Write(LiveTrainerVital.Life, 500f);

            Assert.True(outcome.Success, outcome.Message);
            Assert.Equal(42f, outcome.Before!.AsSingle);
            Assert.Equal(7f, outcome.After!.AsSingle);
        }

        [Theory]
        [InlineData(float.NaN)]
        [InlineData(float.PositiveInfinity)]
        [InlineData(-1f)]
        [InlineData(999_999f)]
        public void ValuesTheGameCouldNotHoldAreRefusedBeforeAnythingIsOpened(float value)
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();

            LiveTrainerWriteOutcome outcome = session.Write(LiveTrainerVital.Life, value);

            Assert.False(outcome.Success);
            Assert.Empty(world.Memory.Writes);
            Assert.Single(world.Factory.Opens);
        }

        [Fact]
        public void DisposingTheSessionClosesEveryHandleItOpened()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);

            LiveTrainerSession session = world.Attach();
            session.Write(LiveTrainerVital.Life, 500f);
            Assert.Equal(2, world.Factory.Opens.Count);

            session.Dispose();

            Assert.All(world.Factory.Opens, accessor => Assert.True(accessor.Disposed));
        }

        // ============================================================ holding

        [Fact]
        public void HoldingWritesTheValueBackOnEveryTick_BecauseOnePokeIsANoOp()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();
            var hold = new LiveTrainerHold(session);

            Assert.True(hold.TryHold(LiveTrainerVital.Life, 500f, out _));
            Assert.True(hold.IsHolding);

            for (int tick = 0; tick < 3; tick++)
            {
                LiveTrainerHoldTick result = hold.Tick();
                Assert.Equal(1, result.Attempted);
                Assert.Equal(1, result.Succeeded);
                Assert.False(result.StoppedItself);
            }

            Assert.Equal(3, world.Memory.Writes.Count);
        }

        [Fact]
        public void HoldingStopsItselfWhenTheMissionEnds_AndHandsBackWriteAccess()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();
            var hold = new LiveTrainerHold(session);
            Assert.True(hold.TryHold(LiveTrainerVital.Life, 500f, out _));
            hold.Tick();
            Assert.True(session.HasWriteAccess);

            // The mission ends: slot 0 goes back to null.
            world.Memory.PutUInt32(LiveTrainerAddresses.PlayerTable, 0);
            LiveTrainerHoldTick result = hold.Tick();

            Assert.True(result.StoppedItself);
            Assert.False(hold.IsHolding);
            Assert.False(session.HasWriteAccess);
            Assert.Equal(LiveTrainerReadStatus.NoMissionRunning, result.Reading.Status);
        }

        [Fact]
        public void HoldingStopsItselfWhenTheProcessGoes()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();
            var hold = new LiveTrainerHold(session);
            Assert.True(hold.TryHold(LiveTrainerVital.Life, 500f, out _));
            hold.Tick();

            world.Memory.FailEverything = true;
            LiveTrainerHoldTick result = hold.Tick();

            Assert.True(result.StoppedItself);
            Assert.False(hold.IsHolding);
            Assert.Equal(LiveTrainerReadStatus.ProcessGone, result.Reading.Status);
        }

        [Fact]
        public void HoldingGivesUpAfterWritesStopLandingRatherThanRetryingForever()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();
            var hold = new LiveTrainerHold(session);
            Assert.True(hold.TryHold(LiveTrainerVital.Life, 500f, out _));

            world.Memory.RefuseWrites = true;
            for (int tick = 0; tick < LiveTrainerHold.ConsecutiveFailuresBeforeStopping - 1; tick++)
            {
                Assert.False(hold.Tick().StoppedItself);
            }

            LiveTrainerHoldTick last = hold.Tick();

            Assert.True(last.StoppedItself);
            Assert.False(hold.IsHolding);
        }

        [Fact]
        public void ReleasingTheLastHoldHandsBackWriteAccessWithoutEndingTheSession()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();
            var hold = new LiveTrainerHold(session);
            hold.TryHold(LiveTrainerVital.Life, 500f, out _);
            hold.TryHold(LiveTrainerVital.Energy, 200f, out _);
            hold.Tick();
            Assert.True(session.HasWriteAccess);

            hold.Release(LiveTrainerVital.Life);
            Assert.True(session.HasWriteAccess);

            hold.Release(LiveTrainerVital.Energy);

            Assert.False(hold.IsHolding);
            Assert.False(session.HasWriteAccess);
            Assert.Equal(LiveTrainerReadStatus.Read, session.Read().Status);
        }

        [Fact]
        public void ANotHoldingTickStillReadsButNeverWrites()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: 2);
            using LiveTrainerSession session = world.Attach();
            var hold = new LiveTrainerHold(session);

            LiveTrainerHoldTick result = hold.Tick();

            Assert.Equal(0, result.Attempted);
            Assert.Equal(LiveTrainerReadStatus.Read, result.Reading.Status);
            Assert.Empty(world.Memory.Writes);
        }

        [Fact]
        public void TheHoldRateIsTenHertzAndCannotBeDrivenIntoASpin()
        {
            Assert.Equal(TimeSpan.FromMilliseconds(100), LiveTrainerHold.DefaultInterval);
            Assert.Equal(TimeSpan.FromMilliseconds(500), LiveTrainerHold.IdleInterval);
            Assert.Equal(LiveTrainerHold.FastestInterval, LiveTrainerHold.ClampInterval(TimeSpan.Zero));
            Assert.Equal(LiveTrainerHold.FastestInterval, LiveTrainerHold.ClampInterval(TimeSpan.FromMilliseconds(1)));
            Assert.Equal(LiveTrainerHold.DefaultInterval, LiveTrainerHold.ClampInterval(LiveTrainerHold.DefaultInterval));
        }

        // ============================================================ what is not offered

        [Fact]
        public void OnlyTheThreeFieldsWithAddressEvidenceAreWritable()
        {
            // Ammunition and game speed have no address anywhere in the corpus. A control for
            // either would be a fabricated feature, so the enum that drives every write control
            // must not grow one.
            Assert.Equal(
                new[] { LiveTrainerVital.Life, LiveTrainerVital.Energy, LiveTrainerVital.Shields },
                Enum.GetValues<LiveTrainerVital>());
        }

        [Fact]
        public void ThePlayerStateIsReadableButHasNoWriteRoute()
        {
            using var world = new TrainerWorld();
            world.PutRunningMission(life: 42f, energy: 10f, shields: 5f, state: LiveTrainerBattleEngineState.Jet);
            using LiveTrainerSession session = world.Attach();

            LivePlayerVitals vitals = session.Read().Vitals!;

            Assert.Equal("jet", vitals.StateName);
            Assert.Throws<ArgumentOutOfRangeException>(() => vitals.Field((LiveTrainerVital)99));
        }

        [Fact]
        public void OnlyTheThreeWatchedStateValuesAreNamed()
        {
            Assert.Equal("walker", LiveTrainerBattleEngineState.Describe(2));
            Assert.Equal("changing to jet", LiveTrainerBattleEngineState.Describe(1));
            Assert.Equal("jet", LiveTrainerBattleEngineState.Describe(3));
            Assert.Null(LiveTrainerBattleEngineState.Describe(0));
            Assert.Null(LiveTrainerBattleEngineState.Describe(4));
        }

        // ============================================================ the damage switch

        [Fact]
        public void TheDamageSwitchIsDecodedAndItsPolarityIsZeroMeansInvulnerable()
        {
            // CBattleEngine::Damage reads this, and `jnz` skips the restore - so the restore runs
            // when the field is zero. Getting the polarity backwards would put "you are safe" on
            // screen for a player who is not, which is the worst thing this page could say.
            LivePlayerVitals invulnerable = DecodeWithVulnerable(0);
            Assert.True(invulnerable.VulnerableLooksLikeABool);
            Assert.True(invulnerable.IsInvulnerable);

            LivePlayerVitals mortal = DecodeWithVulnerable(1);
            Assert.False(mortal.IsInvulnerable);

            Assert.Equal(0x15C, LiveTrainerAddresses.VulnerableOffset);
        }

        [Fact]
        public void ADamageSwitchThatIsNotZeroOrOneIsRefusedRatherThanInterpreted()
        {
            LivePlayerVitals nonsense = DecodeWithVulnerable(0x4048F5C3);

            Assert.False(nonsense.VulnerableLooksLikeABool);
            Assert.Null(nonsense.IsInvulnerable);
        }

        [Fact]
        public void AReadTooShortToReachTheDamageSwitchReportsAbsenceRatherThanZero()
        {
            // Zero is a meaning on this field. A truncated buffer that decoded to zero would say
            // "damage will not stick" about a field nobody read, so it decodes to nothing at all.
            byte[] tooShort = new byte[LiveTrainerAddresses.VulnerableOffset];

            LivePlayerVitals vitals = LivePlayerVitalsDecoder.Decode(0x0A000000, 0x0B000000, tooShort);

            Assert.Null(vitals.Vulnerable);
            Assert.Null(vitals.IsInvulnerable);
            Assert.False(vitals.VulnerableLooksLikeABool);
        }

        [Fact]
        public void TheDamageSwitchIsInsideTheBlockTheTrainerAlreadyReads()
        {
            // It costs nothing to read: it sits below the state field, which the trainer has
            // always fetched. No second read, no wider window.
            Assert.True(
                LiveTrainerAddresses.VulnerableOffset + 4 <= LivePlayerVitalsDecoder.RequiredBattleEngineByteCount);
        }

        private static LivePlayerVitals DecodeWithVulnerable(uint raw)
        {
            byte[] block = new byte[LivePlayerVitalsDecoder.RequiredBattleEngineByteCount];
            BinaryPrimitives.WriteUInt32LittleEndian(
                block.AsSpan(LiveTrainerAddresses.VulnerableOffset, 4),
                raw);

            return LivePlayerVitalsDecoder.Decode(0x0A000000, 0x0B000000, block);
        }

        // ============================================================ fakes

        /// <summary>
        /// A registry with one real app-owned copy on disk, a fake address space, and a fake
        /// accessor factory. No process is started and no memory is opened.
        /// </summary>
        private sealed class TrainerWorld : IDisposable
        {
            private readonly string _tempRoot;

            public TrainerWorld()
            {
                _tempRoot = Path.Combine(Path.GetTempPath(), $"onslaught-trainer-{Guid.NewGuid():N}");
                ProfilesRoot = Path.Combine(_tempRoot, "GameProfiles");
                CopyRoot = Path.Combine(ProfilesRoot, "safe-copy-1");
                Directory.CreateDirectory(CopyRoot);
                File.WriteAllBytes(Path.Combine(CopyRoot, "BEA.exe"), new byte[] { 0x4D, 0x5A });
                File.WriteAllText(Path.Combine(CopyRoot, "onslaught-profile-manifest.json"), "{}");
                Registry = new GameProfileManagedProcessRegistry();
            }

            public string ProfilesRoot { get; }

            public string CopyRoot { get; }

            public GameProfileManagedProcessRegistry Registry { get; }

            public FakeMemory Memory { get; } = new();

            public FakeAccessorFactory Factory => field ??= new FakeAccessorFactory(Memory);

            public GameProfileManagedProcess BuildProcessRecord(int processId) => new(
                ProcessId: processId,
                ExecutablePath: Path.Combine(CopyRoot, "BEA.exe"),
                WorkingDirectory: CopyRoot,
                Arguments: Array.Empty<string>(),
                StartedAt: new DateTimeOffset(2026, 8, 1, 3, 0, 0, TimeSpan.Zero),
                ManifestPath: Path.Combine(CopyRoot, "onslaught-profile-manifest.json"));

            public GameProfileManagedProcess RegisterProcess(int processId = 1234)
            {
                GameProfileManagedProcess process = BuildProcessRecord(processId);
                Registry.Register(process, ProfilesRoot);
                return Registry.Snapshot().Single(row => row.Process.ProcessId == processId).Process;
            }

            public IGameProfileProcessLivenessProbe LiveProbe(GameProfileManagedProcess process) =>
                new FakeLivenessProbe(process.StartedAt, process.ExecutablePath);

            /// <summary>Registers a copy, attaches to it, and hands back the open session.</summary>
            public LiveTrainerSession Attach()
            {
                GameProfileManagedProcess process = RegisterProcess();
                LiveTrainerAttachOutcome outcome = LiveTrainerSession.Attach(
                    process, Registry, Factory, LiveProbe(process));
                Assert.True(outcome.Success, outcome.Message);
                return outcome.Session!;
            }

            /// <summary>Lays out a running mission: table, player, battle engine, and vitals.</summary>
            public void PutRunningMission(float life, float energy, float shields, int state) =>
                PutRunningMission(
                    unchecked((uint)BitConverter.SingleToInt32Bits(life)),
                    unchecked((uint)BitConverter.SingleToInt32Bits(energy)),
                    unchecked((uint)BitConverter.SingleToInt32Bits(shields)),
                    state);

            public void PutRunningMission(uint lifeBits, uint energyBits, uint shieldsBits, int state)
            {
                Memory.Map(LiveTrainerAddresses.PlayerTable, LiveTrainerAddresses.PlayerTableByteCount);
                Memory.PutUInt32(LiveTrainerAddresses.PlayerTable, PlayerPointer);

                Memory.Map(PlayerPointer, 0x400);
                Memory.PutUInt32(PlayerPointer + (uint)LiveTrainerAddresses.BattleEngineOffsetInPlayer, BattleEnginePointer);

                Memory.Map(BattleEnginePointer, LivePlayerVitalsDecoder.RequiredBattleEngineByteCount);
                Memory.PutUInt32(BattleEnginePointer + LiveTrainerAddresses.LifeOffset, lifeBits);
                Memory.PutUInt32(BattleEnginePointer + LiveTrainerAddresses.EnergyOffset, energyBits);
                Memory.PutUInt32(BattleEnginePointer + LiveTrainerAddresses.ShieldsOffset, shieldsBits);
                Memory.PutUInt32(BattleEnginePointer + LiveTrainerAddresses.StateOffset, unchecked((uint)state));
            }

            public void Dispose()
            {
                try
                {
                    if (Directory.Exists(_tempRoot))
                        Directory.Delete(_tempRoot, recursive: true);
                }
                catch (IOException)
                {
                    // A leftover temp directory is not a test failure.
                }
            }
        }

        private sealed record MemoryOperation(bool IsWrite, uint Address, int Length);

        /// <summary>
        /// An address space made of explicitly mapped regions. Reading outside a mapped region
        /// fails, exactly as ReadProcessMemory does, so "the mission ended and the object is gone"
        /// is reproducible without a game.
        /// </summary>
        private sealed class FakeMemory
        {
            private readonly List<(uint Start, uint End)> _mapped = new();
            private readonly Dictionary<uint, byte> _bytes = new();

            public List<MemoryOperation> Operations { get; } = new();

            public List<MemoryOperation> Reads { get; } = new();

            public List<(uint Address, byte[] Data)> Writes { get; } = new();

            public bool FailEverything { get; set; }

            public bool RefuseWrites { get; set; }

            /// <summary>Stands in for the game simulating over the top of what was just written.</summary>
            public float? OverwriteWritesWith { get; set; }

            public void Map(uint start, int length) => _mapped.Add((start, start + (uint)length));

            public void PutUInt32(uint address, uint value)
            {
                for (int i = 0; i < 4; i++)
                    _bytes[address + (uint)i] = (byte)(value >> (8 * i));
            }

            public void PutSingle(uint address, float value) =>
                PutUInt32(address, unchecked((uint)BitConverter.SingleToInt32Bits(value)));

            public bool TryRead(uint address, Span<byte> destination)
            {
                if (FailEverything || !IsMapped(address, destination.Length))
                    return false;

                Reads.Add(new MemoryOperation(false, address, destination.Length));
                Operations.Add(new MemoryOperation(false, address, destination.Length));
                for (int i = 0; i < destination.Length; i++)
                    destination[i] = _bytes.TryGetValue(address + (uint)i, out byte value) ? value : (byte)0;

                return true;
            }

            public bool TryWrite(uint address, ReadOnlySpan<byte> source)
            {
                if (FailEverything || RefuseWrites || !IsMapped(address, source.Length))
                    return false;

                Writes.Add((address, source.ToArray()));
                Operations.Add(new MemoryOperation(true, address, source.Length));
                for (int i = 0; i < source.Length; i++)
                    _bytes[address + (uint)i] = source[i];

                if (OverwriteWritesWith is not null && source.Length == 4)
                    PutSingle(address, OverwriteWritesWith.Value);

                return true;
            }

            private bool IsMapped(uint address, int length) =>
                _mapped.Any(region => address >= region.Start && (ulong)address + (ulong)length <= region.End);
        }

        private sealed class FakeAccessorFactory : IProcessMemoryAccessorFactory
        {
            private readonly FakeMemory _memory;

            public FakeAccessorFactory(FakeMemory memory) => _memory = memory;

            public List<FakeAccessor> Opens { get; } = new();

            public bool TryOpen(
                int processId,
                ProcessMemoryAccess access,
                out IProcessMemoryAccessor? accessor,
                out string failure)
            {
                failure = string.Empty;
                var opened = new FakeAccessor(processId, access, _memory);
                Opens.Add(opened);
                accessor = opened;
                return true;
            }
        }

        private sealed class FakeAccessor : IProcessMemoryAccessor
        {
            private readonly FakeMemory _memory;

            public FakeAccessor(int processId, ProcessMemoryAccess access, FakeMemory memory)
            {
                ProcessId = processId;
                Access = access;
                _memory = memory;
            }

            public int ProcessId { get; }

            public ProcessMemoryAccess Access { get; }

            public bool Disposed { get; private set; }

            public bool TryRead(uint address, Span<byte> destination) =>
                !Disposed && _memory.TryRead(address, destination);

            public bool TryWrite(uint address, ReadOnlySpan<byte> source) =>
                !Disposed && (Access & ProcessMemoryAccess.Write) != 0 && _memory.TryWrite(address, source);

            public void Dispose() => Disposed = true;
        }

        private sealed class FakeLivenessProbe : IGameProfileProcessLivenessProbe
        {
            private readonly GameProfileProcessLivenessProbeResult _result;

            public FakeLivenessProbe() => _result = new GameProfileProcessLivenessProbeResult(false, null, null);

            public FakeLivenessProbe(DateTimeOffset startedAt, string? mainModulePath) =>
                _result = new GameProfileProcessLivenessProbeResult(true, startedAt, mainModulePath);

            public GameProfileProcessLivenessProbeResult Probe(GameProfileManagedProcess process) => _result;
        }
    }
}
