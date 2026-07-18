// SPDX-License-Identifier: GPL-3.0-or-later

using System.Security.Cryptography;
using System.Text;

namespace OnslaughtRebuild.Core;

public static class StateHasher
{
    private static readonly byte[] s_magic = Encoding.ASCII.GetBytes("ONSLAUGHT-REBUILD-STATE");

    public static string ComputeHex(WorldSnapshot state)
    {
        ArgumentNullException.ThrowIfNull(state);

        return Convert.ToHexString(SHA256.HashData(GetCanonicalBytes(state))).ToLowerInvariant();
    }

    internal static byte[] GetCanonicalBytes(WorldSnapshot state)
    {
        ArgumentNullException.ThrowIfNull(state);

        using var stream = new MemoryStream();
        using (var writer = new BinaryWriter(stream, Encoding.UTF8, leaveOpen: true))
        {
            writer.Write(s_magic);
            writer.Write(5);
            writer.Write(state.Tick);
            writer.Write(state.Seed);
            writer.Write((int)state.Mode);
            writer.Write((int)state.Transition);
            WriteVector(writer, state.PlayerPosition);
            WriteVector(writer, state.PlayerVelocity);
            writer.Write(state.FacingX);
            writer.Write(state.FacingZ);
            writer.Write(state.FacingYawMicroRad);
            writer.Write(state.WalkerYawVelocityMicroRadPerTick);
            writer.Write(state.Energy);
            writer.Write(state.Shield);
            writer.Write(state.Hull);
            writer.Write(state.TransformTicksRemaining);
            writer.Write(state.FireCooldownTicksRemaining);
            writer.Write((int)state.Level100Phase);
            writer.Write(state.Level100DispatchTicksRemaining);
            writer.Write(state.NextProjectileId);
            writer.Write(state.TargetsDestroyed);

            TargetSnapshot[] targets = state.Targets.OrderBy(target => target.Id).ToArray();
            writer.Write(targets.Length);
            foreach (TargetSnapshot target in targets)
            {
                writer.Write(target.Id);
                WriteVector(writer, target.Position);
                writer.Write(target.Hull);
                writer.Write(target.IsActive);
            }

            ProjectileSnapshot[] projectiles = state.Projectiles
                .OrderBy(projectile => projectile.Id)
                .ToArray();
            writer.Write(projectiles.Length);
            foreach (ProjectileSnapshot projectile in projectiles)
            {
                writer.Write(projectile.Id);
                WriteVector(writer, projectile.Position);
                WriteVector(writer, projectile.Velocity);
                writer.Write(projectile.RemainingTicks);
            }
        }

        return stream.ToArray();
    }

    private static void WriteVector(BinaryWriter writer, SimVector2 vector)
    {
        writer.Write(vector.X);
        writer.Write(vector.Z);
    }
}
