// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class Level100PlayerWeaponRuntimeTests
{
    [Fact]
    public void ResetConfiguration_SelectsFirstReleasedSlotAndActivatesAllWeapons()
    {
        var weapons = new Level100PlayerWeaponRuntime();

        Assert.Equal(Level100MissionWeapon.PulseCannonPod, weapons.WalkerSelectedWeapon);
        Assert.Equal(Level100MissionWeapon.MechVulcanCannon, weapons.JetSelectedWeapon);
        Assert.Equal(2, weapons.CountActiveWeapons(VehicleMode.Walker));
        Assert.Equal(2, weapons.CountActiveWeapons(VehicleMode.Jet));

        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, false);
        weapons.SetActive(Level100MissionWeapon.MissilePod, false);
        weapons.ResetConfiguration();

        Assert.Equal(Level100MissionWeapon.PulseCannonPod, weapons.WalkerSelectedWeapon);
        Assert.Equal(Level100MissionWeapon.MechVulcanCannon, weapons.JetSelectedWeapon);
        Assert.Equal(2, weapons.CountActiveWeapons(VehicleMode.Walker));
        Assert.Equal(2, weapons.CountActiveWeapons(VehicleMode.Jet));
    }

    [Theory]
    [InlineData(
        VehicleMode.Walker,
        Level100MissionWeapon.PulseCannonPod,
        Level100MissionWeapon.MechTwinVulcanCannon)]
    [InlineData(
        VehicleMode.Jet,
        Level100MissionWeapon.MechVulcanCannon,
        Level100MissionWeapon.MissilePod)]
    public void DisablingSelectedWeapon_SelectsNextActiveSlot(
        VehicleMode mode,
        Level100MissionWeapon selected,
        Level100MissionWeapon expected)
    {
        var weapons = new Level100PlayerWeaponRuntime();

        weapons.SetActive(selected, false);

        Assert.Equal(expected, weapons.GetCurrentWeapon(mode));
        Assert.True(weapons.IsActive(expected));
        Assert.Equal(1, weapons.CountActiveWeapons(mode));
    }

    [Fact]
    public void EnablingWeapon_DoesNotStealCurrentSelection()
    {
        var weapons = new Level100PlayerWeaponRuntime();
        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, false);
        Assert.Equal(
            Level100MissionWeapon.MechTwinVulcanCannon,
            weapons.WalkerSelectedWeapon);

        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, true);

        Assert.Equal(
            Level100MissionWeapon.MechTwinVulcanCannon,
            weapons.WalkerSelectedWeapon);
        Assert.Equal(2, weapons.CountActiveWeapons(VehicleMode.Walker));
    }

    [Theory]
    [InlineData(
        VehicleMode.Walker,
        Level100MissionWeapon.MechTwinVulcanCannon,
        Level100MissionWeapon.PulseCannonPod)]
    [InlineData(
        VehicleMode.Jet,
        Level100MissionWeapon.MissilePod,
        Level100MissionWeapon.MechVulcanCannon)]
    public void ManualCycle_SelectsNextActiveReleasedSlotAndWraps(
        VehicleMode mode,
        Level100MissionWeapon next,
        Level100MissionWeapon wrapped)
    {
        var weapons = new Level100PlayerWeaponRuntime();

        Assert.True(weapons.SelectNextActive(mode));
        Assert.Equal(next, weapons.GetCurrentWeapon(mode));
        Assert.True(weapons.SelectNextActive(mode));
        Assert.Equal(wrapped, weapons.GetCurrentWeapon(mode));
    }

    [Fact]
    public void ManualCycle_WithOneActiveWeapon_DoesNotMoveSelection()
    {
        var weapons = new Level100PlayerWeaponRuntime();
        weapons.SetActive(Level100MissionWeapon.MechTwinVulcanCannon, false);

        Assert.False(weapons.SelectNextActive(VehicleMode.Walker));
        Assert.Equal(Level100MissionWeapon.PulseCannonPod, weapons.WalkerSelectedWeapon);
    }

    [Fact]
    public void NoActiveAlternative_PreservesBoundedCurrentSlot()
    {
        var weapons = new Level100PlayerWeaponRuntime();
        weapons.SetActive(Level100MissionWeapon.MechTwinVulcanCannon, false);
        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, false);

        Assert.Equal(Level100MissionWeapon.PulseCannonPod, weapons.WalkerSelectedWeapon);
        Assert.False(weapons.IsActive(weapons.WalkerSelectedWeapon));
        Assert.Equal(0, weapons.CountActiveWeapons(VehicleMode.Walker));
    }

    [Fact]
    public void ReleasedLevel100EnableDisableSequence_RetainsSelectionHistory()
    {
        var weapons = new Level100PlayerWeaponRuntime();

        weapons.SetActive(Level100MissionWeapon.MechTwinVulcanCannon, false);
        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, false);
        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, true);
        Assert.Equal(Level100MissionWeapon.PulseCannonPod, weapons.WalkerSelectedWeapon);

        weapons.SetActive(Level100MissionWeapon.MechTwinVulcanCannon, true);
        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, false);
        Assert.Equal(
            Level100MissionWeapon.MechTwinVulcanCannon,
            weapons.WalkerSelectedWeapon);

        weapons.SetActive(Level100MissionWeapon.PulseCannonPod, true);
        Assert.Equal(
            Level100MissionWeapon.MechTwinVulcanCannon,
            weapons.WalkerSelectedWeapon);
    }

    [Fact]
    public void StateHash_DistinguishesBothSelectedSlots()
    {
        WorldSnapshot state = new Simulation(
            0x1234U,
            Level100TestActorDefinitions.Create()).Snapshot;
        string baseline = StateHasher.ComputeHex(state);

        Assert.NotEqual(
            baseline,
            StateHasher.ComputeHex(state with
            {
                Level100WalkerSelectedWeapon =
                    Level100MissionWeapon.MechTwinVulcanCannon,
            }));
        Assert.NotEqual(
            baseline,
            StateHasher.ComputeHex(state with
            {
                Level100JetSelectedWeapon = Level100MissionWeapon.MissilePod,
            }));
        Assert.NotEqual(
            baseline,
            StateHasher.ComputeHex(state with
            {
                TwinVulcanReloadTicksRemaining = 1,
            }));
    }
}
