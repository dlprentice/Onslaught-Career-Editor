// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The Level 100 <c>Pulse Cannon Pod</c> charge table, read out of
/// <c>data/default physics.dat</c> so the increment law in
/// <see cref="RetailWeaponCharge.Charge"/> can be aimed at the weapon a
/// cold-career player actually holds.
/// </summary>
/// <remarks>
/// <para>
/// Statement <c>Pulse Cannon Pod</c> at file offset <c>0x17463</c> of
/// <c>local-lab/safe-copy-bea-pristine/data/default physics.dat</c>
/// (175,603 bytes, SHA-256
/// <c>e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14</c>).
/// <c>CWeaponChargeRate</c> is the dword <c>00 00 20 41</c> = <c>10.0f</c>.
/// Two <c>CWeaponChargeLevel</c> nodes mark indices 0 and 1 present
/// (<c>Mech Pulse Cannon Charged</c> / <c>Mech Pulse Cannon Charged 2</c>);
/// indices 2..4 stay at the absent marker. That is why
/// <see cref="RetailWeaponCharge.MaxCharge"/> is 100 and
/// <see cref="RetailWeaponCharge.CanCharge"/> is true.
/// </para>
/// <para>
/// <b>Not established here.</b> The energy-store add of
/// <c>CWeaponConsumption</c> 4.0, overheat-to-fire, and which round
/// <c>Fire</c> selects at charge level 1 remain the next ChargeWeapon arms.
/// </para>
/// </remarks>
public static class Level100PulseCannonCharge
{
    /// <summary><c>CWeaponChargeRate</c> — <c>0x41200000</c> at the Pod record.</summary>
    public const uint ChargeRateBits = 0x41200000u;

    /// <summary>The same dword as a float — exactly 10.0.</summary>
    public const float ChargeRate = 10.0f;

    /// <summary>
    /// <c>CWeaponReloadTime</c> on <c>Mech Pulse Cannon Charged</c> @0x134E3
    /// — <c>0x3DCCCCCD</c> at file offset <c>0x1351D</c>.
    /// </summary>
    public const uint ReloadTimeBits = 0x3DCCCCCDu;

    /// <summary>The same dword as a float — exactly 0.1 seconds.</summary>
    public const float ReloadTime = 0.1f;

    /// <summary>
    /// A rest-state Pulse Cannon Pod: rate 10.0, levels 0 and 1 present,
    /// live charge <c>+0.0f</c>.
    /// </summary>
    public static RetailWeaponChargeTable CreatePod()
    {
        RetailWeaponChargeTable pod = new()
        {
            ChargeRate = ChargeRate,
            Charge = BitConverter.UInt32BitsToSingle(0u),
            ReadyAtTime = BitConverter.UInt32BitsToSingle(0u),
            ReadyToChargeGateActive = true,
        };
        pod.Levels[0] = 0;
        pod.Levels[1] = 1;
        return pod;
    }
}
