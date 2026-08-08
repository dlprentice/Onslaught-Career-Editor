using System;
using System.Buffers.Binary;
using System.Globalization;

namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// The addresses the live trainer uses, and exactly how far the evidence for each one goes.
    ///
    /// Three different confidence levels are mixed in here, and the difference between them is the
    /// entire reason the UI is shaped the way it is.
    ///
    /// MEASURED IN A LIVE PROCESS. The image loads at <see cref="ExpectedModuleBase"/> with no
    /// ASLR, so static virtual addresses from the RE corpus are live runtime addresses. Read on
    /// 2026-08-01 (local-lab/LIVE-MEMORY-PROBE-2026-08-01.md): MZ at the base, the cheat key at
    /// 0x00629A64, the cheat table decrypting to MALLOY. The pointer chain
    /// <see cref="PlayerTable"/> then <see cref="BattleEngineOffsetInPlayer"/>, and the state field
    /// at <see cref="StateOffset"/>, were separately observed live during the walker-transform
    /// timing runs (reverse-engineering/game-mechanics/campaign-scalar-status.md and
    /// walker-transform-morph-timing-v1.json).
    ///
    /// STATIC AND SOURCE CORRESPONDENCE ONLY. <see cref="LifeOffset"/>, <see cref="EnergyOffset"/>
    /// and <see cref="ShieldsOffset"/> come from the body of CBattleEngine::Damage at 0x0040A890
    /// matching BattleEngine.cpp field for field (reverse-engineering/source-code/stuart-source-synthesis.md, reverse-engineering/delta.md), corroborated by
    /// CUnit::ApplyDamage and by the HUD health getter reading a float at +0xf8. That is a strong
    /// correspondence and it is still not a live read: the 2026-08-01 probe found the player table
    /// null because no mission was running, so nobody has yet seen a value at any of these three.
    ///
    /// NOT PRESENT AT ALL. There is no identified live ammunition counter address and no game-speed
    /// or timescale field anywhere in the corpus. The trainer does not offer either, and must not.
    ///
    /// Nothing here may be described to a player as verified, confirmed, or proven. The read path
    /// is built so a wrong offset shows up as visible nonsense on screen before any control that
    /// could write is enabled; see <see cref="LiveTrainerPlausibility"/>.
    /// </summary>
    public static class LiveTrainerAddresses
    {
        /// <summary>Measured: the image loads here in the live process, with no ASLR.</summary>
        public const uint ExpectedModuleBase = 0x00400000;

        /// <summary>
        /// Player array base, read by IScript::GetPlayerBattleEngine (0x005363E0) and named in
        /// reverse-engineering/binary-analysis/functions/IScript.cpp.md. Observed live as Steam RVA
        /// +0x4a9d3c supplying the player-one root; and observed as 32 bytes of zero at the
        /// frontend, which is what it should look like with no mission running.
        /// </summary>
        public const uint PlayerTable = 0x008A9D3C;

        /// <summary>
        /// The active CBattleEngine hangs off the player root here. This hop is easy to miss and
        /// skipping it reads garbage: the vitals are fields of CBattleEngine, not of the player.
        /// IScript::GetPlayerBattleEngine wraps player+0x1c, and the runtime observer notes read
        /// "player one's BattleEngine at CPlayer + 0x1c".
        /// </summary>
        public const int BattleEngineOffsetInPlayer = 0x1C;

        /// <summary>The probe read this many bytes of the table; four bytes per slot pointer.</summary>
        public const int PlayerTableByteCount = 32;

        public const int PlayerSlotCount = PlayerTableByteCount / 4;

        /// <summary>Slot 0 is player one. The trainer follows this slot and no other.</summary>
        public const int PrimaryPlayerSlot = 0;

        /// <summary>Float. Static and source correspondence only; never read from a live process.</summary>
        public const int LifeOffset = 0xF8;

        /// <summary>Float. Static and source correspondence only; never read from a live process.</summary>
        public const int EnergyOffset = 0xFC;

        /// <summary>Float. Static and source correspondence only; never read from a live process.</summary>
        public const int ShieldsOffset = 0x100;

        /// <summary>
        /// Whole number. Unlike the three vitals this one has been sampled from a running game, and
        /// three of its values are known: see <see cref="LiveTrainerBattleEngineState"/>. It is
        /// displayed and never written - knowing what a value means is not the same as knowing what
        /// happens when you force it.
        /// </summary>
        public const int StateOffset = 0x260;

        /// <summary>
        /// <c>mVulnerable</c>. Whole number, and <b>zero means invulnerable</b>.
        ///
        /// MEASURED from the pristine specimen (<c>74154bfa…</c>) on 2026-08-01, in the same
        /// <c>CBattleEngine::Damage</c> the three vitals came from - file offset <c>0x00A890</c>,
        /// at <c>+0x035a</c>:
        /// <code>
        ///   mov  eax, [esi+0x15C]        ; this field
        ///   test eax, eax
        ///   jnz  skip                    ; non-zero: the damage stands
        ///   mov  edx, [esp+0x04]         ; life,    snapshotted in the prologue
        ///   mov  eax, [esp+0x08]         ; shields, snapshotted in the prologue
        ///   mov  ecx, [esp+0x0C]         ; energy,  snapshotted in the prologue
        ///   mov  [esi+0x0F8], edx
        ///   mov  [esi+0x100], eax
        ///   mov  [esi+0x0FC], ecx
        /// </code>
        /// The three restored slots are exactly the prologue's own snapshot of the vitals, which
        /// is what makes this conclusive rather than suggestive. It compiles
        /// <c>references/Onslaught/BattleEngine.cpp:2234</c>, <c>if (mVulnerable == FALSE)</c>,
        /// and it explains the live 2026-03-29 observation that god mode stops new damage but does
        /// not repair hull already lost: it is a per-hit undo, not a heal.
        ///
        /// <b>Read and displayed; never written.</b> The vitals earned their write controls with a
        /// live probe - read 20, wrote 100, watched the HUD follow. Nothing has yet written to this
        /// field in a running game, so it does not get the same offer. See
        /// <c>local-lab/GOD-MODE-OFFSET-2026-08-01.md</c> for what would settle it.
        /// </summary>
        public const int VulnerableOffset = 0x15C;

        /// <summary>Lowest address a 32-bit user-mode allocation can sit at.</summary>
        public const uint LowestUserAddress = 0x00010000;

        /// <summary>Highest usable 32-bit user-mode address.</summary>
        public const uint HighestUserAddress = 0x7FFEFFFF;

        public static int OffsetOf(LiveTrainerVital vital) => vital switch
        {
            LiveTrainerVital.Life => LifeOffset,
            LiveTrainerVital.Energy => EnergyOffset,
            LiveTrainerVital.Shields => ShieldsOffset,
            _ => throw new ArgumentOutOfRangeException(nameof(vital)),
        };

        public static string NameOf(LiveTrainerVital vital) => vital switch
        {
            LiveTrainerVital.Life => "life",
            LiveTrainerVital.Energy => "energy",
            LiveTrainerVital.Shields => "shields",
            _ => throw new ArgumentOutOfRangeException(nameof(vital)),
        };
    }

    /// <summary>The three fields the trainer will write. Player state is read-only and absent here.</summary>
    public enum LiveTrainerVital
    {
        Life,
        Energy,
        Shields,
    }

    /// <summary>
    /// The three battle-engine state values that were established from a running game, with the
    /// canonical Steam Morph body: 2 is walker, 1 is the walker-to-jet transition, 3 is jet
    /// (reverse-engineering/game-mechanics/walker-transform-morph-retail-to-core-translation-policy.md).
    ///
    /// Anything else is deliberately returned as null rather than guessed at. An older note in
    /// CBattleEngine__Init.md gives the opposite mapping; the runtime observation wins.
    /// </summary>
    public static class LiveTrainerBattleEngineState
    {
        public const int Walker = 2;
        public const int ChangingToJet = 1;
        public const int Jet = 3;

        public static string? Describe(int raw) => raw switch
        {
            Walker => "walker",
            ChangingToJet => "changing to jet",
            Jet => "jet",
            _ => null,
        };
    }

    /// <summary>
    /// One four-byte field, kept as the bits that were actually read rather than as a number
    /// somebody already decided how to interpret.
    ///
    /// The vitals were read out of a running mission on 2026-08-01 and read as floats there
    /// (0x41A00000 is exactly 20.0f), but both readings are still carried, because a wrong pointer
    /// hop returns plausible small floats - that is how the original brief was caught. Both: <see cref="AsSingle"/> is what the source correspondence
    /// says the field is - CUnit's health getter returns a float from +0xf8 - and is what the UI
    /// shows first; <see cref="AsInt32"/> and <see cref="RawHex"/> sit beside it so a player can
    /// see for themselves whether the float reading is nonsense.
    /// </summary>
    public sealed record LiveTrainerFieldReading(uint Address, uint RawBits)
    {
        public float AsSingle => BitConverter.Int32BitsToSingle(unchecked((int)RawBits));

        public int AsInt32 => unchecked((int)RawBits);

        public string RawHex => "0x" + RawBits.ToString("X8", CultureInfo.InvariantCulture);

        /// <summary>
        /// Whether this reading is a believable vital when read as a 32-bit float.
        ///
        /// It is deliberately strict about tiny values, and that strictness is doing real work: if
        /// the field turned out to be a whole number rather than a float, a normal health value -
        /// 100, say - reads as the subnormal float 1.4E-43 and fails this check. So the write
        /// controls stay disabled precisely in the case where the app has guessed the type wrong.
        /// </summary>
        public bool LooksLikeAVital => LiveTrainerPlausibility.IsPlausibleVital(AsSingle);
    }

    /// <summary>
    /// One reading of player one's battle engine, reached through the player table and the
    /// player's own battle-engine pointer.
    /// </summary>
    public sealed record LivePlayerVitals(
        uint PlayerPointer,
        uint BattleEnginePointer,
        LiveTrainerFieldReading Life,
        LiveTrainerFieldReading Energy,
        LiveTrainerFieldReading Shields,
        LiveTrainerFieldReading State,
        LiveTrainerFieldReading? Vulnerable = null)
    {
        /// <summary>
        /// True when the field reads 0 or 1, which is how a BOOL should look. Anything else means
        /// the pointer or the offset is wrong, and the page says so rather than interpreting it.
        /// </summary>
        public bool VulnerableLooksLikeABool =>
            Vulnerable is not null && Vulnerable.AsInt32 is 0 or 1;

        /// <summary>Null when the reading is not believable, so no caller can render a guess.</summary>
        public bool? IsInvulnerable =>
            VulnerableLooksLikeABool ? Vulnerable!.AsInt32 == 0 : null;

        public LiveTrainerFieldReading Field(LiveTrainerVital vital) => vital switch
        {
            LiveTrainerVital.Life => Life,
            LiveTrainerVital.Energy => Energy,
            LiveTrainerVital.Shields => Shields,
            _ => throw new ArgumentOutOfRangeException(nameof(vital)),
        };

        /// <summary>The known name for the state value, or null when it is not one of the three.</summary>
        public string? StateName => LiveTrainerBattleEngineState.Describe(State.AsInt32);

        /// <summary>
        /// True when at least one of the three vitals reads as a believable, non-zero float. All
        /// three reading exactly zero is what a freshly zeroed or wrongly-located object looks
        /// like, so that case is not a plausible read.
        /// </summary>
        public bool AnyVitalLooksPlausible =>
            (Life.LooksLikeAVital && Life.AsSingle > 0f) ||
            (Energy.LooksLikeAVital && Energy.AsSingle > 0f) ||
            (Shields.LooksLikeAVital && Shields.AsSingle > 0f);
    }

    /// <summary>
    /// The rules that decide whether something the app read is believable enough to be shown as a
    /// number and, separately, believable enough to allow a write on top of.
    ///
    /// These are not a claim that the offsets are right. They are the opposite: they are what lets
    /// the app ship an unconfirmed offset without being able to silently scribble on whatever
    /// happens to live there.
    /// </summary>
    public static class LiveTrainerPlausibility
    {
        /// <summary>Anything smaller than this and non-zero is a subnormal, not a vital.</summary>
        public const float SmallestNonZeroVital = 0.0001f;

        /// <summary>Above this and a "vital" is a pointer or a bit pattern, not a number of hit points.</summary>
        public const float LargestVital = 100_000f;

        /// <summary>The largest value the app is willing to write. Deliberately below <see cref="LargestVital"/>.</summary>
        public const float LargestWritableVital = 10_000f;

        public static bool IsPlausibleVital(float value)
        {
            if (!float.IsFinite(value) || value < 0f)
                return false;

            if (value > LargestVital)
                return false;

            return value == 0f || value >= SmallestNonZeroVital;
        }

        /// <summary>
        /// Whether a pointer read out of the game could be a real heap object: inside the 32-bit
        /// user address range and four-byte aligned, which any C++ object of this shape is.
        /// </summary>
        public static bool IsPlausiblePointer(uint pointer)
        {
            if (pointer == 0)
                return false;

            if (pointer < LiveTrainerAddresses.LowestUserAddress || pointer > LiveTrainerAddresses.HighestUserAddress)
                return false;

            return (pointer & 3u) == 0;
        }

        /// <summary>
        /// Whether the app is willing to write <paramref name="value"/> at all, before it even
        /// looks at what is currently there.
        /// </summary>
        public static bool IsWritableVital(float value, out string refusal)
        {
            refusal = string.Empty;

            if (!float.IsFinite(value))
            {
                refusal = "That value is not a number the game could hold.";
                return false;
            }

            if (value < 0f)
            {
                refusal = "A vital cannot be negative.";
                return false;
            }

            if (value > LargestWritableVital)
            {
                refusal = $"The largest value this will write is {LargestWritableVital:0}.";
                return false;
            }

            return true;
        }
    }

    /// <summary>
    /// Turns raw bytes into pointers and readings, with no Win32 anywhere. Every branch below is a
    /// pure function of its input, so all of them are reachable in a unit test with no game.
    /// </summary>
    public static class LivePlayerVitalsDecoder
    {
        /// <summary>Reads slot <paramref name="slot"/> out of the raw player table bytes.</summary>
        public static uint ReadSlotPointer(ReadOnlySpan<byte> playerTableBytes, int slot)
        {
            int start = slot * 4;
            if (slot < 0 || start + 4 > playerTableBytes.Length)
                return 0;

            return BinaryPrimitives.ReadUInt32LittleEndian(playerTableBytes.Slice(start, 4));
        }

        /// <summary>How many bytes of the battle engine have to be read to cover every field.</summary>
        public static int RequiredBattleEngineByteCount => LiveTrainerAddresses.StateOffset + 4;

        /// <summary>
        /// Builds the reading from a battle engine's bytes. <paramref name="battleEngineBytes"/>
        /// starts at the object's own address and must reach at least past the state field.
        /// </summary>
        public static LivePlayerVitals Decode(
            uint playerPointer,
            uint battleEnginePointer,
            ReadOnlySpan<byte> battleEngineBytes)
        {
            return new LivePlayerVitals(
                playerPointer,
                battleEnginePointer,
                Field(battleEnginePointer, battleEngineBytes, LiveTrainerAddresses.LifeOffset),
                Field(battleEnginePointer, battleEngineBytes, LiveTrainerAddresses.EnergyOffset),
                Field(battleEnginePointer, battleEngineBytes, LiveTrainerAddresses.ShieldsOffset),
                Field(battleEnginePointer, battleEngineBytes, LiveTrainerAddresses.StateOffset),
                OptionalField(battleEnginePointer, battleEngineBytes, LiveTrainerAddresses.VulnerableOffset));
        }

        /// <summary>
        /// A field that is absent rather than zero when the read did not reach it.
        ///
        /// <see cref="Field"/> zero-fills a short read, which is safe for the vitals: zero life is
        /// visibly wrong and the plausibility gate catches it. It is not safe for the damage
        /// switch, where zero is a meaning - "damage will not stick" - and a caller cannot tell a
        /// real zero from a truncated buffer. Absent says nothing, which is the truth in that case.
        /// </summary>
        private static LiveTrainerFieldReading? OptionalField(uint basePointer, ReadOnlySpan<byte> bytes, int offset)
        {
            return offset + 4 > bytes.Length
                ? null
                : Field(basePointer, bytes, offset);
        }

        private static LiveTrainerFieldReading Field(uint basePointer, ReadOnlySpan<byte> bytes, int offset)
        {
            uint address = unchecked(basePointer + (uint)offset);
            if (offset + 4 > bytes.Length)
                return new LiveTrainerFieldReading(address, 0);

            return new LiveTrainerFieldReading(
                address,
                BinaryPrimitives.ReadUInt32LittleEndian(bytes.Slice(offset, 4)));
        }
    }
}
