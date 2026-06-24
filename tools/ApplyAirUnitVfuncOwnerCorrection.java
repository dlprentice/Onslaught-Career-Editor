//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyAirUnitVfuncOwnerCorrection extends GhidraScript {

    private static class Target {
        final String address;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final String comment;

        Target(String address, String newName, String callingConvention, DataType returnType, String comment) {
            this.address = address;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
        }
    }

    private static boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String expectedSignature(Target target, ParameterImpl thisParam) {
        return target.returnType.getDisplayName() + " " + target.callingConvention + " " + target.newName +
            "(" + thisParam.getDataType().getDisplayName() + " " + thisParam.getName() + ")";
    }

    private void applyTarget(Target target, boolean dryRun, DataType voidPtr) throws Exception {
        Function fn = getFunctionOrThrow(target.address);
        ParameterImpl thisParam = param("this", voidPtr);

        if (dryRun) {
            println("DRY: " + target.address + " " + fn.getName() + " -> " +
                target.newName + " / " + expectedSignature(target, thisParam));
            return;
        }

        if (!fn.getName().equals(target.newName)) {
            fn.setName(target.newName, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(target.callingConvention);
        fn.setReturnType(target.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            thisParam
        );
        fn.setComment(target.comment);

        Function readBack = getFunctionOrThrow(target.address);
        if (!readBack.getName().equals(target.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + target.address);
        }
        String signature = readBack.getSignature().toString();
        if (!signature.contains(target.callingConvention) || !signature.contains(target.newName) || !signature.contains("void * this")) {
            throw new IllegalStateException("Read-back signature mismatch at " + target.address + ": " + signature);
        }
        String comment = readBack.getComment();
        if (comment == null || comment.trim().isEmpty()) {
            throw new IllegalStateException("Read-back comment missing at " + target.address);
        }
        println("OK: " + target.address + " " + target.newName + " -> " + signature);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;

        Target[] targets = new Target[] {
            new Target(
                "0x00402030",
                "CActor__VFunc_18_SyncOldVectorAfterBaseCall",
                "__thiscall",
                voidType,
                "Actor vtable slot 18 correction: CActor and actor-derived vtables point here. Calls base slot 18, then copies current vector dwords at this+0x1c..0x28 into previous/old vector storage at this+0x8c..0x98. Source method name and concrete layout remain provisional."
            ),
            new Target(
                "0x00402fa0",
                "CUnit__UpdateMotionAndTrailEffects",
                "__thiscall",
                voidType,
                "Unit motion/effects pass: air-unit vtable slot 66 references this body. Updates velocity/friction state, clamps motion, advances attachment/trail particle and mesh renderer state, and includes a low-altitude crash path. No runtime flight proof or concrete CUnit layout is implied."
            ),
            new Target(
                "0x00403730",
                "CAirUnit__VFunc_68_TimestampAndCrashIfNoAirSupport",
                "__thiscall",
                voidType,
                "Air-unit vtable slot 68 correction: CAirUnit, CBigAirUnit, CFenrir, CCarver, and CCarrier vtables point here. Sets a state timestamp, then triggers the explosion/death path when flag bit 4 is set and unit-data +0x11c is zero. Not a CExplosionInitThing method; support-field semantics remain provisional."
            ),
            new Target(
                "0x00403760",
                "CAirUnit__VFunc_69_ResetD0AndCrashIfNoSupportModes",
                "__thiscall",
                voidType,
                "Air-unit vtable slot 69 correction: same air-unit class family points here. Resets the D0 threshold helper, then triggers the explosion/death path when flag bit 4 is set and unit-data +0x11c/+0x124 are both zero. Corrects the duplicate CUnitAI wrapper label; field semantics remain provisional."
            ),
            new Target(
                "0x00403a50",
                "CAirUnit__VFunc_117_HasPositionDeltaWhileFlag4Clear",
                "__thiscall",
                intType,
                "Air-unit vtable slot 117 correction: air and plane subclass vtables point here. Returns true when current and previous/target position components differ and flag bit 4 is clear. Not a CFrontEndPage method; exact source virtual name remains provisional."
            ),
            new Target(
                "0x004d20a0",
                "CPlane__VFunc_68_CrashIfNoAirSupport",
                "__thiscall",
                voidType,
                "Plane-family vtable slot 68 override: CPlane, CDiveBomber, CGroundAttackAircraft, and CBomber vtables point here. Calls the CAirUnit slot-68 body, then triggers the explosion/death path when unit-data +0x11c is zero. Not a CExplosionInitThing method."
            ),
            new Target(
                "0x0047bf60",
                "CPlane__VFunc_69_CrashIfNoSupportModes",
                "__thiscall",
                voidType,
                "Plane-family vtable slot 69 override: CPlane, CDiveBomber, CGroundAttackAircraft, and CBomber vtables point here. Calls the CAirUnit slot-69 body, then triggers the explosion/death path when unit-data +0x11c/+0x124 are both zero. Corrects the previous generic CUnitAI owner label."
            ),
        };

        int updated = 0;
        int skipped = 0;
        for (Target target : targets) {
            applyTarget(target, dryRun, voidPtr);
            if (dryRun) {
                skipped++;
            } else {
                updated++;
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " missing=0 bad=0");
    }
}
