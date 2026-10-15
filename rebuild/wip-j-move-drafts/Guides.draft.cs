// DRAFT (Peer J, 2026-10-15, internal disk while Archive B is read-only). NOT COMPILED. Reconcile with Things/Guide.cs.
// SPDX-License-Identifier: GPL-3.0-or-later   (TerrainGuide.cpp and AirGuide.cpp are not in Stuart's release: CHECK
// references/Onslaught for siblings before settling the licence)
// Adapted from bea-decomp src/TerrainGuide.cpp (CTerrainGuide::Unknown3 004f1ee0) and src/AirGuide.cpp
// (CAirGuide::Unknown3 00402280), src/maths.h (Azimuth, Elevation, AngleDifference).

namespace OnslaughtRebuild.Parity.Things;

using OnslaughtRebuild.Parity.Maths;
using OnslaughtRebuild.Parity.Numerics;

public partial class TerrainGuide   // RECONCILE: today cannons get BasicGuide("CTerrainGuide"); make this its own class
{
    /// <summary>CTerrainGuide::Unknown3 (004f1ee0): a cannon's (or other terrain unit's) steering.</summary>
    public override void Unknown3()
    {
        if (Unit.IsDying())
        {
            Unit.Stop();
            return;
        }

        Unit.Unknown14C = new FVector(0, 0, 0);
        FVector d = Destination - Unit.Pos;
        float current = Unit.CurrentOrientation.Yaw;
        if (Mode == 0)
        {
            return;
        }

        if (d.MagnitudeXYSq() < 0.01f || Unit.IsDeploying())
        {
            return;
        }

        float yaw;
        switch (Mode)
        {
            case 1:
            case 3:
                yaw = d.Azimuth();
                break;
            case 2:
                yaw = d.Azimuth() - MathConstants.Pi;                    // ORACLE (stored float?)
                break;
            default:
                // retail logs "ERROR : Unknown Terrain guide state!" and uses an uninitialised yaw
                throw new InvalidOperationException("CTerrainGuide: unknown mode (retail reads an uninitialised yaw)");
        }

        Unit.Unknown120 = Unit.Unknown120 with { Yaw = yaw };
        float distanceSq = d.MagnitudeXYSq();
        // d.Normalise(): its result is dead (the decomp's comment: retail stores a full distance it never reads).
        if (distanceSq < 0.01f)
        {
            Mode = 0;
            return;
        }

        if (MathF.Abs(MathsHelpers.AngleDifference(yaw, current)) > 0.2f && distanceSq < 0.1f)
        {
            return;
        }

        if (Mode == 3)
        {
            return;
        }

        float speed = Unit.Unknown111() / 5.0f;                          // ORACLE (reciprocal?)
        Unit.Unknown14C = Unit.Orientation.Transform(new FVector(0, speed, 0));   // ORACLE: Transform's order here
    }
}

public partial class AirGuide
{
    /// <summary>CAirGuide::Unknown3 (00402280): an aircraft's steering.</summary>
    public override void Unknown3()
    {
        Unit unit = Unit;
        if (unit.IsDying())
        {
            unit.Unknown174 = 0;
            Publish(unit);
            return;
        }

        FVector d = Destination - unit.Pos;
        float yaw = d.Azimuth();
        float pitch = (float)X87.Atan2(d.Z, d.MagnitudeXY());           // ORACLE: atan2 on the stack, then stored
        float course = unit.Velocity.Azimuth();
        float elevation = unit.Velocity.Elevation();                     // unused, but Elevation has no side effects
        _ = elevation;
        FVector right = unit.Orientation.GetColumnX();

        float heading;
        switch (Mode)
        {
            case 0:
                heading = course + MathConstants.PiOver2;
                pitch = 0;
                break;
            case 2:
                heading = yaw - MathConstants.Pi;
                break;
            default:
                heading = yaw;
                break;
        }

        if (heading > MathConstants.Pi)
        {
            heading -= MathConstants.TwoPi;
        }

        if (heading < -MathConstants.Pi)
        {
            heading += MathConstants.TwoPi;
        }

        if (pitch > MathConstants.Pi)
        {
            pitch -= MathConstants.TwoPi;
        }

        if (pitch < -MathConstants.Pi)
        {
            pitch += MathConstants.TwoPi;
        }

        if (unit.AI!.AIMode != 2)
        {
            Thing? nearest = Nearest;
            if (nearest is not null)
            {
                pitch = -MathConstants.Pi / 3;                           // RECONCILE: the folded constant's float bits
                if (!((nearest.Pos - unit.Pos).Z > 0))
                {
                    pitch = MathConstants.Pi / 3;
                }
            }

            if (Clearance < 5.0f)
            {
                pitch = -MathConstants.Pi / 4;
            }
            else if (Clearance < 15.0f && pitch > 0)
            {
                pitch = 0;
            }
            else if (Clearance > 50.0f)
            {
                pitch = MathConstants.Pi / 4;
            }

            if (unit.DeployState != 1 && unit.DeployState != 2)
            {
                if (unit.Pos.X < 10.0f)
                {
                    heading = -MathConstants.PiOver2;
                }
                else if (unit.Pos.X > 502.0f)
                {
                    heading = MathConstants.PiOver2;
                }
                else if (unit.Pos.Y < 10.0f)
                {
                    heading = 0;
                }
                else if (unit.Pos.Y > 502.0f)
                {
                    heading = MathConstants.Pi;
                }
            }
        }

        float diff = MathF.Abs(MathsHelpers.AngleDifference(course, heading));   // (float)fabs
        if (diff > MathConstants.PiOver2)
        {
            diff = MathConstants.PiOver2;
        }

        float roll = DotAt00402280(right, d) < 0 ? diff : -diff;        // order read from the instructions; still ORACLE the function
        unit.Unknown174 = MathF.Abs(roll) > 0.1f ? 1.0f : 0;
        unit.Unknown120 = new EulerAngles(heading, pitch, roll);
        Publish(unit);
    }

    // Both arms end the same way: the unit is pushed along its forward column at (max velocity / 20) * 4.
    private static void Publish(Unit unit)
    {
        float speed = (unit.GetMaxVelocity() / 20.0f) * 4.0f;            // ORACLE
        FMatrix ori = unit.Orientation;
        unit.Unknown14C = new FVector(speed * ori.Row0.Y, speed * ori.Row1.Y, speed * ori.Row2.Y);
    }

    // right * d as compiled at 00402553..0040256d (Steam BEA.exe, SHA-256 74154bfa…, = the pristine specimen): d is the
    // local at esp+0x20 and right at esp+0x30 (each built by FVector's constructor 00401ec0 after three pushes); the
    // products are Z, then Y, then X, summed (Z + Y) + X on the stack and compared with 0 without a store.
    private static float DotAt00402280(FVector right, FVector d) =>
        ((right.Z * d.Z) + (right.Y * d.Y)) + (right.X * d.X);
}
