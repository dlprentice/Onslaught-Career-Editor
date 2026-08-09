// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The released Level 100 player's configured weapon slots, active flags and
/// current selection. This intentionally stops before charge, heat, ammo and
/// launch behavior. Selections are base slots: Walker slot zero may resolve to
/// the augmented weapon at runtime. Manual cycling remains rejected, so its
/// resource-eligibility gate is intentionally not generalized here; for every
/// currently reachable Level 100 scripted disable, eligibility reduces to the
/// active flag represented below.
/// </summary>
internal sealed class Level100PlayerWeaponRuntime
{
    private bool _pulseCannonActive;
    private bool _twinVulcanActive;
    private bool _mechVulcanActive;
    private bool _missilePodActive;
    private int _walkerSelection;
    private int _jetSelection;

    internal Level100PlayerWeaponRuntime() => ResetConfiguration();

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
            TrySelectNextActive(mode);
        }
    }

    private void TrySelectNextActive(VehicleMode mode)
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
                return;
            }

            candidate = (candidate + 1) % 2;
        }
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
