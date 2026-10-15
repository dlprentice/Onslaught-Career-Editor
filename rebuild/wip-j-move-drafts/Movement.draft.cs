// DRAFT (Peer J, 2026-10-15, written on the internal disk while Archive B is read-only). NOT COMPILED.
// Reconcile member names with the checkout's Things/*.cs before applying (see RECONCILE.md beside this file).
// Every line marked ORACLE is a float site for D's per-function oracle before it counts as exact.
//
// SPDX-License-Identifier: GPL-3.0-only   (actor.cpp is in Stuart's release; the file adapting it is GPL-3.0-only)
// Adapted from bea-decomp src/actor.cpp (CActor::Move 004015e0, LowFidelityMove (inlined into HandleEvent 004019e0),
// DeclareOnGround 00402000, DeclareInWater 00402010, IsOnGround 00401f70, IsInWater 00401fa0), src/Unit.cpp
// (CUnit::Move 004fa8d0, UpdateTimer 004fa800, Unknown77 004fa4b0, Unknown111 004fe5c0, ObeyGravity 004fdc90,
// Stop 004fcf00), src/GroundUnit.cpp (CGroundUnit::Move 0047c970), src/GroundVehicle.cpp (0047d1c0),
// src/Cannon.cpp (0041b370), src/Building.cpp (004178a0), src/SimpleBuilding.cpp (004dfaa0, 004dfcb0, 004dfcc0),
// src/AirUnit.cpp (00402fa0, Gravity 00403b60), src/Plane.cpp (004d1cd0), src/unit.h (the per-class inlines),
// src/thing.h (the CThing defaults), src/maths.h (AngleDifference).

namespace OnslaughtRebuild.Parity.Things;

using OnslaughtRebuild.Parity.Maths;
using OnslaughtRebuild.Parity.Numerics;

// ---------------------------------------------------------------------------------------------------------------
// CThing defaults (thing.h 115-141) — check which already exist on Thing.
// ---------------------------------------------------------------------------------------------------------------
public partial class Thing
{
    public virtual bool ClipToGround() => true;          // slot 44
    public virtual float Gravity() => 0.01f;             // slot 45 (004014b0)
    public virtual bool ObeyGravity() => true;           // slot 46
    public virtual float BounceFactor() => 0;            // slot 47
    public virtual float COfGHeight() => 0;              // slot 48
}

public partial class Actor
{
    // mLastMoveTime, mLastTimeOnGround, mLastTimeInWater, mLastTimeOnObject: floats on CActor.
    public float LastMoveTime { get; set; }
    public float LastTimeOnGround { get; set; } = -1000.0f;   // RECONCILE: retail's constructor/Init value
    public float LastTimeInWater { get; set; } = -1000.0f;    // RECONCILE
    public float LastTimeOnObject { get; set; } = -1000.0f;   // RECONCILE

    public bool IsOnGround() => Context.Events.Time - LastTimeOnGround < 0.15f;   // 00401f70
    public bool IsInWater() => Context.Events.Time - LastTimeInWater < 0.25f;     // 00401fa0
    public bool IsOnObject() => Context.Events.Time - LastTimeOnObject < 0.15f;   // 00401fd0
    public virtual void DeclareOnGround() => LastTimeOnGround = Context.Events.Time;   // 00402000 (virtual: CDropship overrides)
    public void DeclareInWater() => LastTimeInWater = Context.Events.Time;              // 00402010

    /// <summary>CActor::Move (004015e0).</summary>
    public virtual void Move()
    {
        LastMoveTime = Context.Events.Time;
        OldPos = Pos;
        OldOrientation = Orientation;
        // previous sector: only for the collision-seeking thing's MovedSector (counted below)

        // CLIPARAMS.mDeveloperMode's velocity check: logging only, off in retail runs.

        // pos += velocity through the reference alias: X, then Y, then Z (ORACLE: the alias form is the decomp's stand-in)
        Pos = new FVector(Pos.X + Velocity.X, Pos.Y + Velocity.Y, Pos.Z + Velocity.Z);

        float waterHeight = Context.Map.WaterLevel - COfGHeight();   // ORACLE (stored float)
        if (ClipToGround())
        {
            float alt = Context.Map.Collide(Pos) - COfGHeight();      // ORACLE (Collide's return kept on the stack?)
            if (alt <= Pos.Z)
            {
                Pos = new FVector(Pos.X, Pos.Y, alt);
                if ((Flags & ThingFlags.Slide) != 0)
                {
                    // RECONCILE: no level-100 thing is known to take TF_SLIDE; throw until one is seen
                    throw new NotSupportedException("CActor::Move's TF_SLIDE branch (MAP.Normal backoff) is not ported");
                }

                DeclareOnGround();
                if (MathF.Abs(Velocity.Z) > Gravity() + 0.05f)               // ORACLE
                {
                    Velocity = new FVector(Velocity.X, Velocity.Y, -Velocity.Z * BounceFactor());
                }
                else
                {
                    Velocity = new FVector(Velocity.X, Velocity.Y, 0);
                }
            }

            if (waterHeight <= Pos.Z)
            {
                DeclareInWater();
            }
        }

        if (MapWhoEntry is not null && MapWhoEntry.UpdateEntry(OldPos) && HasCollisionSeekingThing)
        {
            Context.Skip("CCollisionSeekingThing::MovedSector");
        }
    }

    /// <summary>CActor::LowFidelityMove (actor.cpp 54; no address of its own: inlined into HandleEvent).</summary>
    public virtual void LowFidelityMove()
    {
        OldPos = Pos;
        Pos = new FVector(Pos.X + Velocity.X, Pos.Y + Velocity.Y, Pos.Z + Velocity.Z);   // ORACLE (FVector += order)
        if (ClipToGround())
        {
            float alt = Context.Map.Collide(Pos) - COfGHeight();
            if (alt <= Pos.Z)
            {
                Pos = new FVector(Pos.X, Pos.Y, alt);
                LastTimeOnGround = Context.Events.Time;
            }
        }
        // NOTE: no map-who update in the light move (retail's text has none).
    }
}

// ---------------------------------------------------------------------------------------------------------------
// CUnit (unit.h 44-261 inlines; Unit.cpp)
// ---------------------------------------------------------------------------------------------------------------
public partial class Unit
{
    public override bool ObeyGravity() => !(AI is not null && AI.AIMode == 2);          // 004fdc90
    public override float BounceFactor() => UnitData.BounceFactor;                      // 00417620
    public virtual float Unknown72() => 0.25f;                                          // 00405dc0: friction on the ground
    public virtual float Unknown73() => 0.98f;                                          // 00405dd0: friction in the air
    public virtual bool Unknown76() => !((Unknown168 != 0 || !Active) && (Flags & ThingFlags.Dying) == 0);   // 00405de0
    public virtual bool Unknown109() => Unknown168 == 0;                                // 00405e70

    /// <summary>CUnit::Unknown111 (004fe5c0): the top speed, half as much again while deploying.</summary>
    public float Unknown111() => (DeployState == 1 || DeployState == 2) ? UnitData.UnknownB4 * 1.5f : UnitData.UnknownB4;   // ORACLE

    /// <summary>CUnit::UpdateTimer (004fa800).</summary>
    public void UpdateTimer()
    {
        switch (Unknown168)
        {
            case 1:
                if (Unknown16C <= Context.Events.Time)
                {
                    if (Unknown1EC)
                    {
                        Unknown1E8 = 1;
                    }
                    else
                    {
                        Unknown87();
                    }

                    Unknown168 = 0;
                    return;
                }

                Unknown1E8 = 0;
                Stop();
                break;
            case 2:
                Unknown1E8 = 0;
                if (Unknown16C < Context.Events.Time)
                {
                    Unknown168 = 0;
                    return;
                }

                Stop();
                break;
            case 3:
                if (Unknown16C < Context.Events.Time)
                {
                    Unknown168 = 0;
                }

                Orientation = OldOrientation;
                break;
        }
    }

    /// <summary>CUnit::Unknown77 (004fa4b0): slews the current angles toward the target at the given rates.</summary>
    public void Unknown77(ref EulerAngles cur, EulerAngles target, EulerAngles rate, out FMatrix result)   // ORACLE (whole function)
    {
        float mult = GetMoveMultiplier();
        if (cur.Yaw != target.Yaw)
        {
            cur.Yaw = SlewAngle(cur.Yaw, target.Yaw, mult * rate.Yaw, mult);
        }

        if (cur.Pitch != target.Pitch)
        {
            float maxStep = mult * rate.Pitch;
            float step = MathF.Abs(MathF.Abs(cur.Pitch - target.Pitch)) * mult * 0.1f;   // ORACLE: (|d| * mult) * 0.1f
            if (step > maxStep)
            {
                step = maxStep;
            }

            cur.Pitch = cur.Pitch > target.Pitch ? cur.Pitch - step : cur.Pitch + step;
        }

        if (cur.Roll != target.Roll)
        {
            cur.Roll = SlewAngle(cur.Roll, target.Roll, mult * rate.Roll, mult);
        }

        result = FMatrix.FromYawPitchRoll(cur.Yaw, cur.Pitch, cur.Roll);
    }

    // The yaw and roll arms of Unknown77 are the same text (Unit.cpp 004fa4b0); kept as one helper here.
    private static float SlewAngle(float c0, float t0, float maxStep, float mult)
    {
        float t = t0;
        float c = c0;
        if (c < -MathConstants.PiOver2 && t > MathConstants.PiOver2)        // RECONCILE: PI/2 as float constant (0x3fc90fdb)
        {
            t -= MathConstants.TwoPi;
        }
        else if (c > MathConstants.PiOver2 && t < -MathConstants.PiOver2)
        {
            t += MathConstants.TwoPi;
        }

        float step = MathF.Abs(c - t) * mult * 0.1f;                        // ORACLE
        if (step > maxStep)
        {
            step = maxStep;
        }

        float r = c0;
        if (c0 < t0)
        {
            r = t0 - c0 > MathConstants.Pi ? r - step : r + step;
        }
        else
        {
            r = c0 - t0 > MathConstants.Pi ? r + step : r - step;
        }

        if (r > MathConstants.Pi)
        {
            r -= MathConstants.TwoPi;
        }
        else if (r < -MathConstants.Pi)
        {
            r += MathConstants.TwoPi;
        }

        return r;
    }

    /// <summary>CUnit::Move (004fa8d0).</summary>
    public override void Move()
    {
        if (Guide is not null && (Active || IsDying()))
        {
            Guide.Unknown3();
        }
        else
        {
            Stop();
        }

        Unknown248 = 0;
        UpdateTimer();
        base.Move();

        if (Unknown76() && (Unknown120.Yaw != CurrentOrientation.Yaw || Unknown120.Pitch != CurrentOrientation.Pitch
            || Unknown120.Roll != CurrentOrientation.Roll))           // CEulerAngles::operator!= (maths.h 346)
        {
            EulerAngles cur = CurrentOrientation;
            Unknown77(ref cur, Unknown120, Unknown12C, out FMatrix ori);
            CurrentOrientation = cur;
            Orientation = ori;
        }

        if (!IsDying())
        {
            Shields += ShieldRegeneration;
            if (Shields > MaxShields)
            {
                Shields = MaxShields;
            }
        }
        else if (UnitData.Unknown124)
        {
            int n = X87.Fist(GetMoveMultiplier());
            for (int i = 0; i < n; i++)
            {
                Unknown95();
            }
        }

        if (Unknown170 + 0.1f < Unknown174)
        {
            Unknown170 += 0.1f;
        }
        else if (Unknown170 - 0.1f > Unknown174)
        {
            Unknown170 -= 0.1f;
        }
        else
        {
            Unknown170 = Unknown174;
        }

        // vents (GetEmitter 21), the firing effect, dust (GetEmitter 22): particle links only; GetEmitter makes no
        // draws or events. Counted until particles exist. RECONCILE: GetEmitter needs the motion controller for
        // cannons and vehicles (pose), which is NotSupported today — only call it once the controllers are ported.
        Context.Skip("CUnit::Move: vents, firing effect and dust (particles)");

        if (!IsDying() && !(Life < 0) && Unknown1F0)
        {
            foreach (var spawner in Spawners)
            {
                spawner.DoSpawn();          // RECONCILE: spawners are counted (UPhysicsManager::SpawnSpawner) today
            }
        }

        // the turret toward the target (ORACLE: the whole block)
        UnknownE4 = UnknownE0;
        UnknownF0 = UnknownE8;
        float mult = GetMoveMultiplier();
        if (AI is not null && !IsDying() && Unknown109())
        {
            float delta = UnknownE0;
            Unit? target = AI.Target.ToRead;
            if (target is not null)
            {
                FVector aim = target.GetTargetablePos();
                FVector muzzle = Orientation.Transform(Unknown1F8) + Pos;    // ORACLE: Transform's compiled order at this site
                delta = (aim - muzzle).Azimuth() - Unknown92();
                Unknown20C = Context.Events.Time + 10.0f;
            }
            else if (Unknown20C < Context.Events.Time)
            {
                delta = 0;
            }

            if (delta > MathConstants.Pi)
            {
                delta -= MathConstants.TwoPi;
            }
            else if (delta < -MathConstants.Pi)
            {
                delta += MathConstants.TwoPi;
            }

            float limit = mult * UnitData.UnknownDC;
            if (delta > limit)
            {
                delta = limit;
            }
            else if (delta < -limit)
            {
                delta = -limit;
            }

            float rate = mult * UnitData.UnknownBC;
            if (rate < MathF.Abs(MathsHelpers.AngleDifference(UnknownE0, delta)))
            {
                if (delta > UnknownE0)
                {
                    UnknownE0 = delta - UnknownE0 > MathConstants.Pi ? UnknownE0 - rate : UnknownE0 + rate;
                }
                else
                {
                    UnknownE0 = UnknownE0 - delta > MathConstants.Pi ? UnknownE0 + rate : UnknownE0 - rate;
                }

                if (UnknownE0 > MathConstants.Pi)
                {
                    UnknownE0 -= MathConstants.TwoPi;
                }
                else if (UnknownE0 < -MathConstants.Pi)
                {
                    UnknownE0 += MathConstants.TwoPi;
                }
            }
            else
            {
                UnknownE0 = delta;
            }

            if (UnknownE0 > UnitData.UnknownDC)
            {
                UnknownE0 = UnitData.UnknownDC;
            }
            else if (UnknownE0 < -UnitData.UnknownDC)
            {
                UnknownE0 = -UnitData.UnknownDC;
            }

            if (Unknown224)
            {
                float pitchRate = mult * UnitData.UnknownBC;
                if (pitchRate < MathF.Abs(UnknownE8 - UnknownEC))
                {
                    UnknownE8 = UnknownE8 < UnknownEC ? UnknownE8 + pitchRate : UnknownE8 - pitchRate;
                }
                else
                {
                    UnknownE8 = UnknownEC;
                }
            }
        }

        if (DeployState == 1)
        {
            if (Guide is not null)
            {
                FVector d = Pos - Guide.Destination;
                if (MathF.Sqrt((d.X * d.X) + (d.Y * d.Y)) < 4.0f)         // ORACLE (sqrtf inline)
                {
                    DeployState = 2;
                    FMatrix heading = Orientation;
                    GoToPoint(new FVector(heading.Row0.Y * 300.0f, heading.Row1.Y * 300.0f, 0) + Pos, false);
                }
            }
        }
        else if (DeployState == 2)
        {
            Unknown116();
        }
        else if (DeployState == 4)
        {
            if (GetCurrentTarget() is null)
            {
                StartUndeploying();
            }
        }

        if (UnitData.Sounds[1] is not null)
        {
            Context.Skip("CUnit::Move: the spawner's working noise (sound)");   // RECONCILE: Unknown230 state must still follow AnySpawnerBusy
        }

        // UpdatePosition: CRTMesh::UpdatePosition is empty in retail.
    }
}

// ---------------------------------------------------------------------------------------------------------------
// CGroundUnit (unit.h 353), CGroundVehicle (372), CCannon (447), CBuilding (507), CSimpleBuilding (836)
// ---------------------------------------------------------------------------------------------------------------
public partial class GroundUnit
{
    /// <summary>CGroundUnit::Move (0047c970).</summary>
    public override void Move()
    {
        float multiplier = GetMoveMultiplier();
        int steps = X87.Fist(multiplier);
        float gravity = 0;
        if (ObeyGravity())
        {
            gravity = Gravity();
        }

        FVector accel = new(0, 0, 0);
        float friction = Unknown73();
        if ((IsOnGround() || IsInWater() || !ObeyGravity()) && Unknown76())
        {
            friction = Unknown72();
            accel = Unknown14C * 0.4f;                                   // ORACLE
        }

        if ((Flags & ThingFlags.Dying) == 0 && UnitData.Parachute == 1)
        {
            // NOTE for the port: `friction /= 1.15f` compiles as fmul 0.8695652f (0x3f5e9bd4) at 0047cb1c.
            throw new NotSupportedException("CGroundUnit::Move's parachute thrusters are not ported (no level-100 unit is known to have one)");
        }

        accel = new FVector(accel.X, accel.Y, accel.Z + gravity);
        for (int step = 0; step < steps; step++)
        {
            Velocity += accel;                                           // ORACLE: += then *= per component
            Velocity *= friction;
        }

        // Read from the instructions at 0047cd3f..0047cd86 (Steam BEA.exe, SHA-256 74154bfa… = pristine): the division by
        // 20 is a multiply by the float 0.05f (0x3d4ccccd); the speed is fsqrt(Y*Y + X*X) on the stack; the ratio
        // top / speed is formed once and multiplies X and Y.
        FVector v = Velocity;
        float top = Unknown111() * 0.05f;
        float speed = MathF.Sqrt((v.Y * v.Y) + (v.X * v.X));             // PC24: fsqrt rounds to 24 bits = MathF.Sqrt
        if (speed > top)
        {
            float ratio = top / speed;
            Velocity = new FVector(ratio * v.X, ratio * v.Y, Velocity.Z);
        }

        base.Move();   // CUnit::Move

        if (UnitData.Unknown10C || Unknown258 != 0)
        {
            OldBob = Bob;
            if ((Flags & ThingFlags.Dying) != 0)
            {
                Bob = BobPhase + Bob;
                BobPhase -= multiplier * 0.005f;
                return;
            }

            if (IsDeploying() && BobPhase < 0.1f)
            {
                BobPhase = 0;
                return;
            }

            // 0047ce2a..0047ce4a: phase += multiplier * 0.1f (fst keeps it on the stack); fsin at full x87 precision
            // (precision control does not round transcendentals); fmul 0.05f rounds to 24 bits; stored.
            BobPhase += multiplier * 0.1f;
            Bob = (float)X87.Mul(X87.Sin(BobPhase), 0.05f);               // RECONCILE: X87 helper names/signatures
            if (BobPhase > MathConstants.TwoPi)
            {
                BobPhase -= MathConstants.TwoPi;
            }
        }
    }
}

public partial class GroundVehicle
{
    public override float COfGHeight() => 0.1f;   // unit.h 376

    /// <summary>CGroundVehicle::Move (0047d1c0): tilts with the ground when the vehicle data says so.</summary>
    public override void Move()
    {
        // GroundVehicleTiltsWithGround (GroundVehicle.cpp): ObeyGravity() first, then the byte flag Init sets (1, or 0
        // when the mesh has a "WheelMotion" mode and the vehicle gets a CMCBuggy instead of a CMCGroundVehicle).
        if (ObeyGravity() && TiltsWithGround != 0)
        {
            FMatrix ori = FMatrix.RotationYaw(CurrentOrientation.Yaw);   // MakeRotationYawF: ORACLE
            FVector forward = ori.Transform(new FVector(0, 1.0f, 0));
            FVector normal = Context.Map.Normal(Pos);
            forward = FVector.CrossAt0047d1c0(forward, normal);          // ORACLE: operator^ operand order at this site
            FVector up = FVector.CrossAt0047d1c0(forward, normal);
            up = up.Normalise();
            Unknown120 = Unknown120 with { Pitch = -up.Z };
            FVector side = forward.Normalise();
            Unknown120 = Unknown120 with { Roll = side.Z };
        }

        base.Move();
    }
}

public partial class Cannon
{
    public override float Gravity() => 0;   // inline, folded into 004bfc60

    /// <summary>CCannon::Move (0041b370): the Activate and Deactivate animations follow the AI's target.</summary>
    public override void Move()
    {
        if (Active && AI!.Target.ToRead is not null)
        {
            if (State != 0 && State != 3)
            {
                SetAnimMode(AnimModeByName("Activate"), true, false);
                State = 3;
            }

            if (AI.Target.ToRead is not null)
            {
                LastTargetTime = Context.Events.Time;
            }
        }
        else if (LastTargetTime + 10.0f < Context.Events.Time)
        {
            if (State != 1 && State != 2)
            {
                SetAnimMode(AnimModeByName("Deactivate"), true, false);
                State = 2;
            }
        }

        base.Move();
    }
}

public partial class Building
{
    /// <summary>CBuilding::Move (004178a0): never calls CUnit or CActor::Move — a building does not move.</summary>
    public override void Move()
    {
        UpdateTimer();
        if (Unknown254 == 2)
        {
            if (!AnySpawnerUnknown4e4420())
            {
                if (Unknown25C < Context.Events.Time && Unknown254 == 2)
                {
                    int anim = AnimModeByName("closing");
                    if (anim == AnimModes.Invalid)
                    {
                        Unknown254 = 3;
                    }
                    else
                    {
                        Unknown254 = 1;
                        SetAnimMode(anim, true, false);
                    }
                }
            }
            else
            {
                Unknown25C = Context.Events.Time + 8.0f;
            }
        }
        else if (AnySpawnerUnknown4e4420())
        {
            Unknown115();
        }

        if (Unknown260 && Unknown264 == 1 && Unknown268 + 15.0f < Context.Events.Time)
        {
            SetAnimMode(AnimModeByName("unshutting"), true, false);
            Unknown264 = 2;
        }
    }
}

public partial class SimpleBuilding
{
    public override bool ClipToGround() => !IsDying();                                 // 004dfcb0
    public override float Gravity() => (Flags & ThingFlags.Dying) != 0 ? 0.002f : 0;   // 004dfcc0

    /// <summary>CSimpleBuilding::Move (004dfaa0): nothing until it dies.</summary>
    public override void Move()
    {
        if ((Flags & ThingFlags.Dying) == 0)
        {
            return;
        }

        throw new NotSupportedException("CSimpleBuilding::Move while dying (surface points, explosions) is not ported");
    }
}

// ---------------------------------------------------------------------------------------------------------------
// CAirUnit (unit.h 262), CPlane (302)
// ---------------------------------------------------------------------------------------------------------------
public partial class AirUnit
{
    /// <summary>CAirUnit::Gravity (00403b60): a dying aircraft falls faster the smaller it is.</summary>
    public override float Gravity()
    {
        if ((Flags & ThingFlags.Dying) != 0)
        {
            float r = GetRadius();
            if (r > 39.0f)
            {
                r = 39.0f;
            }

            return (40.0f - r) * 0.0004f;                               // ORACLE
        }

        return 0.0f;
    }

    /// <summary>CAirUnit::Move (00402fa0).</summary>
    public override void Move()
    {
        if ((Flags & ThingFlags.Dying) != 0)
        {
            float turn = UnitData.TurnRate / 3.0f;                       // ORACLE (reciprocal?)
            Unknown12C = new EulerAngles(turn, turn, turn);
        }

        Velocity += Unknown14C;
        Velocity = new FVector(Velocity.X, Velocity.Y, Velocity.Z + Gravity());
        if (UnitData.Unknown124 && Pos.Z + (GetRadius() * 0.2f) > Context.Map.WaterLevel)   // ORACLE
        {
            Velocity *= 0.95f;
            if ((Flags & ThingFlags.Dying) != 0)
            {
                Unknown96();
            }
        }
        else
        {
            Velocity *= Unknown73();
        }

        float speed = Velocity.Magnitude();                              // ORACLE
        if (speed > 0)
        {
            float max = Unknown111() / 20.0f;
            if (speed > max)
            {
                Velocity *= max / speed;
            }
        }

        base.Move();   // CUnit::Move

        if (Unknown170 + 0.1f < Unknown174)
        {
            Unknown170 += 0.1f;
        }
        else if (Unknown170 - 0.1f > Unknown174)
        {
            Unknown170 -= 0.1f;
        }
        else
        {
            Unknown170 = Unknown174;
        }

        Unknown170 *= 1.0f - (GetStealth() / 100.0f);                    // ORACLE

        Context.Skip("CAirUnit::Move: trails and engines (particles)");
        if (Life < 0)
        {
            throw new NotSupportedException("CAirUnit::Move's dying explosions and smoke are not ported");
        }
    }
}

public partial class Plane
{
    public override float Gravity() => (Flags & ThingFlags.Dying) != 0 ? 0.025f : 0;   // unit.h 306

    /// <summary>CPlane::Move (004d1cd0).</summary>
    public override void Move()
    {
        if ((Flags & ThingFlags.Dying) != 0)
        {
            throw new NotSupportedException("CPlane::Move's death roll is not ported");
        }

        if (LaunchTime > Context.Events.Time)
        {
            Context.Skip("CPlane::Move: launch thrusters (particles)");
            ThrustersActive = true;
        }
        else if (ThrustersActive)
        {
            ThrustersActive = false;
        }

        if (AI!.AIMode != 2 && WingState == 0)
        {
            WingState = 1;
        }

        base.Move();

        float speed = Velocity.Magnitude();                              // ORACLE
        FVector v = new(speed * Orientation.Row0.Y, speed * Orientation.Row1.Y, speed * Orientation.Row2.Y);
        Velocity = v;   // SetVelocity
    }
}
