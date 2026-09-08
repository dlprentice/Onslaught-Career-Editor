// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// The finite PC24/RN angle-update prefix of retail Unit 0x004fa4b0.
/// XYZ are retained retail yaw, pitch and roll words, not angles recovered
/// from a projected matrix. Matrix construction and actor integration remain
/// separate: this does not replace the approximate Level 100 Plane mover yet.
/// </summary>
/// <remarks>
/// The pinned partial source lacks Unit.cpp. The pristine 74154bfa…7750
/// instructions and isolated native oracle are recorded in the existing
/// reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md map.
/// PC24 models device-creation intent; the live gameplay FPU remains unmeasured.
/// </remarks>
public static class RetailUnitEuler
{
    private static readonly double HalfPi = Read(0x3fc90fdb);
    private static readonly double Pi = Read(0x40490fdb);
    private static readonly double TwoPi = Read(0x40c90fdb);
    private static readonly double Ease = Read(0x3dcccccd);

    public static Level100FloatVector3Bits Smooth(
        Level100FloatVector3Bits current,
        Level100FloatVector3Bits desired,
        Level100FloatVector3Bits maximumStep,
        float moveMultiplier)
    {
        if (!float.IsFinite(moveMultiplier) || moveMultiplier <= 0)
            throw new ArgumentOutOfRangeException(nameof(moveMultiplier));

        return new(
            SmoothAxis(current.X, desired.X, maximumStep.X, moveMultiplier, wrap: true),
            SmoothAxis(current.Y, desired.Y, maximumStep.Y, moveMultiplier, wrap: false),
            SmoothAxis(current.Z, desired.Z, maximumStep.Z, moveMultiplier, wrap: true));
    }

    private static int SmoothAxis(int currentBits, int desiredBits, int rateBits,
        double multiplier, bool wrap)
    {
        double current = Read(currentBits);
        double desired = Read(desiredBits);
        // Retail skips the whole axis, including wrapping and stores. In
        // particular, equal -0/+0 must retain the current negative-zero word.
        if (current == desired) return currentBits;

        double rate = Read(rateBits);
        if (rate < 0) throw new ArgumentOutOfRangeException(nameof(rateBits));
        double cap = (float)RetailFloat24.Multiply(multiplier, rate);
        double adjustedDesired = desired;
        if (wrap)
        {
            if (current < -HalfPi && desired > HalfPi)
                adjustedDesired = RetailFloat24.Subtract(desired, TwoPi);
            else if (current > HalfPi && desired < -HalfPi)
                adjustedDesired = RetailFloat24.Add(desired, TwoPi);
        }

        double step = RetailFloat24.Multiply(
            RetailFloat24.Multiply(
                Math.Abs(RetailFloat24.Subtract(current, adjustedDesired)), multiplier), Ease);
        // The cap is a float store; the calculated step stays on the x87
        // stack until the angle update, even when it is below float's range.
        if (step > cap) step = cap;

        bool add = current < desired;
        if (wrap)
        {
            double originalDifference = add
                ? RetailFloat24.Subtract(desired, current)
                : RetailFloat24.Subtract(current, desired);
            if (originalDifference > Pi) add = !add;
        }

        float updated = Store(add
            ? RetailFloat24.Add(current, step)
            : RetailFloat24.Subtract(current, step));
        if (wrap)
        {
            // Exactly one correction, after the first float32 store.
            if (updated > Pi) updated = Store(RetailFloat24.Subtract(updated, TwoPi));
            else if (updated < -Pi) updated = Store(RetailFloat24.Add(updated, TwoPi));
        }
        return BitConverter.SingleToInt32Bits(updated);
    }

    private static double Read(int bits)
    {
        float value = BitConverter.Int32BitsToSingle(bits);
        if (!float.IsFinite(value)) throw new ArgumentOutOfRangeException(nameof(bits));
        return value;
    }

    private static float Store(double value)
    {
        float stored = (float)value;
        if (!float.IsFinite(stored))
            throw new ArgumentOutOfRangeException(nameof(value), "Unit Euler output must remain finite.");
        return stored;
    }
}
