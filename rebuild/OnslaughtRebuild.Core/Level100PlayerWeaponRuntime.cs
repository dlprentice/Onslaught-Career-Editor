// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The released Level 100 player's configured weapon slots, active flags and
/// current selection. Charge is the Pulse Cannon Pod accumulator advanced by
/// held <see cref="SimActions.ChargeWeapon"/>. Each weapon retains its own
/// float ready time. Heat, ammo stores, and complete launch/contact behavior
/// remain open. Selections are base slots: Walker slot zero may resolve to
/// the augmented weapon at runtime. Manual cycling is bounded to the active
/// flag represented here. The released heat/store eligibility test remains an
/// open extension for configurations whose next active weapon cannot fire.
/// </summary>
internal sealed class Level100PlayerWeaponRuntime
{
    private bool _pulseCannonActive;
    private bool _twinVulcanActive;
    private bool _mechVulcanActive;
    private bool _missilePodActive;
    private int _walkerSelection;
    private int _jetSelection;
    private RetailWeaponChargeTable _pulseCharge = Level100PulseCannonCharge.CreatePod();
    private float _twinVulcanReadyAt;
    private float _mechVulcanReadyAt;
    private float _missilePodReadyAt;

    // CWeapon constructor's +0x64 store at 0x00505e6e, also used by the admitted Unit
    // attachment constructor. Configured Level 100 weapons have a mode.
    private const float InitialReadyAt = -200f;
    // Both released Vulcan modes carry CWeaponReloadTime 0x3d4ccccd.
    private const float VulcanReloadTime = 0.05f;

    internal Level100PlayerWeaponRuntime() => ResetConfiguration();

    internal uint PulseCannonChargeBits =>
        BitConverter.SingleToUInt32Bits(_pulseCharge.Charge);

    internal Level100PlayerWeaponStateSnapshot Snapshot => new(
        PulseCannonChargeBits,
        BitConverter.SingleToUInt32Bits(_pulseCharge.ReadyAtTime),
        BitConverter.SingleToUInt32Bits(_twinVulcanReadyAt),
        BitConverter.SingleToUInt32Bits(_mechVulcanReadyAt),
        BitConverter.SingleToUInt32Bits(_missilePodReadyAt));

    internal Level100MissionWeapon WalkerSelectedWeapon =>
        WeaponAt(VehicleMode.Walker, _walkerSelection);

    internal Level100MissionWeapon JetSelectedWeapon =>
        WeaponAt(VehicleMode.Jet, _jetSelection);

    internal void ResetConfiguration()
    {
        _pulseCannonActive = true;
        _twinVulcanActive = true;
        _mechVulcanActive = true;
        _missilePodActive = true;
        _walkerSelection = 0;
        _jetSelection = 0;
        _pulseCharge = Level100PulseCannonCharge.CreatePod();
        _pulseCharge.ReadyAtTime = InitialReadyAt;
        _twinVulcanReadyAt = InitialReadyAt;
        _mechVulcanReadyAt = InitialReadyAt;
        _missilePodReadyAt = InitialReadyAt;
    }

    /// <summary>
    /// The held-input arm of Walker <c>0x00413CF0</c> and Jet
    /// <c>0x00411BF0</c>. Returns a Fire request for the two non-chargeable
    /// Vulcans; the caller uses the same Fire wrapper as a release. The Pulse
    /// increment is bounded here: store spend and overheat-to-fire remain open.
    /// </summary>
    internal bool AdvanceCharge(VehicleMode mode, VehicleTransition transition, float now)
    {
        Level100MissionWeapon selected = GetCurrentWeapon(mode);
        if (transition != VehicleTransition.None || !IsActive(selected) ||
            !ReadyToFire(selected, now))
        {
            return false;
        }

        if (selected is Level100MissionWeapon.MechTwinVulcanCannon or
            Level100MissionWeapon.MechVulcanCannon)
        {
            return true;
        }

        if (selected == Level100MissionWeapon.PulseCannonPod &&
            !RetailWeaponCharge.FullyCharged(_pulseCharge))
        {
            RetailWeaponCharge.Charge(_pulseCharge);
        }
        return false;
    }

    /// <summary>
    /// Shared Fire <c>0x00506010</c> samples charge, clears +0x60, selects its
    /// mode, then checks now &gt; +0x64. A refused Pulse release still loses its
    /// charge. This does not claim the subsequent ammo/launch effects.
    /// </summary>
    internal bool TryPrepareFire(VehicleMode mode, VehicleTransition transition,
        float now, out Level100ProjectileKind pulseRound)
    {
        pulseRound = Level100ProjectileKind.MechPulseBoltMedium;
        Level100MissionWeapon selected = GetCurrentWeapon(mode);
        if (transition != VehicleTransition.None || !IsActive(selected))
        {
            return false;
        }

        if (selected == Level100MissionWeapon.PulseCannonPod)
        {
            pulseRound = Level100PulseCannonCharge.SelectFireRound(_pulseCharge);
            RetailWeaponCharge.LoseCharge(_pulseCharge);
        }
        return ReadyToFire(selected, now);
    }

    internal bool ReadyToFire(Level100MissionWeapon weapon, float now) =>
        RetailWeaponCharge.ReadyTimeElapsed(now, weapon switch
        {
            Level100MissionWeapon.PulseCannonPod => _pulseCharge.ReadyAtTime,
            Level100MissionWeapon.MechTwinVulcanCannon => _twinVulcanReadyAt,
            Level100MissionWeapon.MechVulcanCannon => _mechVulcanReadyAt,
            Level100MissionWeapon.MissilePod => _missilePodReadyAt,
            _ => throw new ArgumentOutOfRangeException(nameof(weapon)),
        });

    /// <summary>
    /// Fire's <c>fld now / fadd mode+0x38 / fstp weapon+0x64</c> at
    /// <c>0x0050611A..0x00506132</c>. One float store follows the addition.
    /// </summary>
    internal void StampReadyAt(Level100MissionWeapon weapon, float now,
        Level100ProjectileKind pulseRound = Level100ProjectileKind.MechPulseBoltMedium)
    {
        float reload = weapon switch
        {
            Level100MissionWeapon.PulseCannonPod => pulseRound switch
            {
                Level100ProjectileKind.MechPulseBoltMedium => Level100PulseCannonCharge.ReloadTime,
                Level100ProjectileKind.MechPulseBoltLarge => Level100PulseCannonCharge.ChargedReloadTime,
                _ => throw new ArgumentOutOfRangeException(nameof(pulseRound)),
            },
            Level100MissionWeapon.MechTwinVulcanCannon or
                Level100MissionWeapon.MechVulcanCannon => VulcanReloadTime,
            _ => throw new NotSupportedException("The Missile Pod launch is not admitted."),
        };
        float readyAt = (float)((double)now + (double)reload);
        switch (weapon)
        {
            case Level100MissionWeapon.PulseCannonPod:
                _pulseCharge.ReadyAtTime = readyAt;
                break;
            case Level100MissionWeapon.MechTwinVulcanCannon:
                _twinVulcanReadyAt = readyAt;
                break;
            case Level100MissionWeapon.MechVulcanCannon:
                _mechVulcanReadyAt = readyAt;
                break;
        }
    }

    /// <summary>
    /// The common pre-direction work in retail <c>CBattleEngine::Morph</c>
    /// calls <c>LoseWeaponCharge</c> on both vehicle parts. Each part clears
    /// only its currently selected weapon. Level 100's Pulse Cannon Pod is the
    /// only represented charge accumulator; the modelled jet weapons have no
    /// charge table to clear.
    /// </summary>
    internal void LoseCurrentWeaponChargesForMorph()
    {
        if (WalkerSelectedWeapon == Level100MissionWeapon.PulseCannonPod)
        {
            RetailWeaponCharge.LoseCharge(_pulseCharge);
        }
    }

    internal Level100MissionWeapon GetCurrentWeapon(VehicleMode mode) => mode switch
    {
        VehicleMode.Walker => WalkerSelectedWeapon,
        VehicleMode.Jet => JetSelectedWeapon,
        _ => throw new ArgumentOutOfRangeException(nameof(mode)),
    };

    internal bool IsActive(Level100MissionWeapon weapon) => weapon switch
    {
        Level100MissionWeapon.PulseCannonPod => _pulseCannonActive,
        Level100MissionWeapon.MechTwinVulcanCannon => _twinVulcanActive,
        Level100MissionWeapon.MechVulcanCannon => _mechVulcanActive,
        Level100MissionWeapon.MissilePod => _missilePodActive,
        _ => throw new ArgumentOutOfRangeException(nameof(weapon)),
    };

    internal int CountActiveWeapons(VehicleMode mode) => mode switch
    {
        VehicleMode.Walker =>
            (_pulseCannonActive ? 1 : 0) + (_twinVulcanActive ? 1 : 0),
        VehicleMode.Jet =>
            (_mechVulcanActive ? 1 : 0) + (_missilePodActive ? 1 : 0),
        _ => throw new ArgumentOutOfRangeException(nameof(mode)),
    };

    internal bool SelectNextActive(VehicleMode mode)
    {
        if (CountActiveWeapons(mode) <= 1)
        {
            return false;
        }

        return TrySelectNextActive(mode);
    }

    internal void SetActive(Level100MissionWeapon weapon, bool active)
    {
        switch (weapon)
        {
            case Level100MissionWeapon.PulseCannonPod:
                _pulseCannonActive = active;
                ReselectIfDisabled(VehicleMode.Walker, weapon, active);
                break;
            case Level100MissionWeapon.MechTwinVulcanCannon:
                _twinVulcanActive = active;
                ReselectIfDisabled(VehicleMode.Walker, weapon, active);
                break;
            case Level100MissionWeapon.MechVulcanCannon:
                _mechVulcanActive = active;
                ReselectIfDisabled(VehicleMode.Jet, weapon, active);
                break;
            case Level100MissionWeapon.MissilePod:
                _missilePodActive = active;
                ReselectIfDisabled(VehicleMode.Jet, weapon, active);
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(weapon));
        }
    }

    private void ReselectIfDisabled(
        VehicleMode mode,
        Level100MissionWeapon weapon,
        bool active)
    {
        if (!active && GetCurrentWeapon(mode) == weapon)
        {
            _ = TrySelectNextActive(mode);
        }
    }

    private bool TrySelectNextActive(VehicleMode mode)
    {
        int current = mode == VehicleMode.Walker
            ? _walkerSelection
            : _jetSelection;
        int candidate = (current + 1) % 2;
        while (candidate != current)
        {
            if (IsActive(WeaponAt(mode, candidate)))
            {
                if (mode == VehicleMode.Walker)
                {
                    _walkerSelection = candidate;
                }
                else
                {
                    _jetSelection = candidate;
                }

                // ChangeWeapon's aftermath: LoseCharge on the newly selected
                // weapon. Level 100 only accumulates charge on the Pulse
                // Cannon Pod; resetting that table matches the store of +0.0f.
                if (WeaponAt(mode, candidate) == Level100MissionWeapon.PulseCannonPod)
                {
                    RetailWeaponCharge.LoseCharge(_pulseCharge);
                }
                return true;
            }

            candidate = (candidate + 1) % 2;
        }

        return false;
    }

    private static Level100MissionWeapon WeaponAt(VehicleMode mode, int index) =>
        (mode, index) switch
        {
            (VehicleMode.Walker, 0) => Level100MissionWeapon.PulseCannonPod,
            (VehicleMode.Walker, 1) => Level100MissionWeapon.MechTwinVulcanCannon,
            (VehicleMode.Jet, 0) => Level100MissionWeapon.MechVulcanCannon,
            (VehicleMode.Jet, 1) => Level100MissionWeapon.MissilePod,
            _ => throw new ArgumentOutOfRangeException(nameof(index)),
        };
}
