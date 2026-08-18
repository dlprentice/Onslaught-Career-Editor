// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The released Level 100 player's configured weapon slots, active flags and
/// current selection. Charge is the Pulse Cannon Pod accumulator advanced by
/// held <see cref="SimActions.ChargeWeapon"/>. Heat, ammo stores, and launch
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

    internal Level100PlayerWeaponRuntime() => ResetConfiguration();

    internal uint PulseCannonChargeBits =>
        BitConverter.SingleToUInt32Bits(_pulseCharge.Charge);

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
    }

    /// <summary>
    /// The increment arm of <c>CBattleEngineWalkerPart::ChargeWeapon</c> at
    /// <c>0x00413CF0</c> for Level 100's Pulse Cannon Pod. ReadyToCharge,
    /// store spend, and overheat-to-fire are not modelled.
    /// </summary>
    internal void AdvanceCharge(VehicleMode mode, VehicleTransition transition)
    {
        if (mode != VehicleMode.Walker ||
            transition != VehicleTransition.None ||
            WalkerSelectedWeapon != Level100MissionWeapon.PulseCannonPod ||
            !_pulseCannonActive ||
            RetailWeaponCharge.FullyCharged(_pulseCharge))
        {
            return;
        }

        RetailWeaponCharge.Charge(_pulseCharge);
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
                RetailWeaponCharge.LoseCharge(_pulseCharge);
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
