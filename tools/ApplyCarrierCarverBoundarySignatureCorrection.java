//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCarrierCarverBoundarySignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.parameters = parameters;
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

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            spec.parameters
        );
        fn.setComment(spec.comment);
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00421a80", "CCarrier__Init", "__thiscall", voidType,
                "Signature/comment correction: Carrier init takes this plus an init object, seeds init flags at +0x7c/+0x80/+0x70, calls CAirUnit__Init, allocates two Carrier.cpp child helper objects at +0x208 and +0x13c, and installs their vtables. Carrier.cpp source is absent from the current source snapshot; exact source identity, concrete layout, runtime carrier behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00421b80", "CCarrierAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CCarrierAI scalar-deleting destructor wrapper calls the CCarrierAI destructor-base body, frees this when flags bit 0 is set, and returns this. Corrects the stale VFunc_01 label; exact source virtual name, allocator ownership, and runtime AI behavior remain unproven.",
                new String[] {"CCarrierAI__VFunc_01_00421b80"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00421ba0", "CCarrierAI__dtor_base", "__fastcall", voidType,
                "Name/signature correction: CCarrierAI destructor-base body resets the base monitor-style vtable, removes linked reader slots at +0x28/+0x24/+0xc from their sets, then calls CMonitor__Shutdown. Corrects the stale ctor-like label; concrete CCarrierAI layout and source identity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00421ba0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00421c40", "CUnit__ApplyFlag4DampingAndScaleSpeed", "__fastcall", voidType,
                "Name/signature correction: applies the flag-bit-4 damping/reset path, scales field +0x11c by a Carver/Carrier-region constant, then calls CUnit__UpdateMotionAndTrailEffects. Exact owning virtual slot, source method name, concrete layout, and runtime movement behavior remain unproven.",
                new String[] {"CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422440", "CCarver__Init", "__thiscall", voidType,
                "Function-boundary recovery and signature correction: Carver init takes this plus an init object, calls CAirUnit__Init, allocates a CCarverGuide at +0x208 and a CCarverAI/Warspite-adjacent helper at +0x13c, starts the launch animation, and seeds Carver wing/attack state fields. Carver.cpp source is absent; exact source identity, concrete layout, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CCarver__Init_candidate"},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00422560", "CCarverAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Signature/comment correction: CCarverAI scalar-deleting destructor wrapper calls CCarverAI__dtor_base, frees this when flags bit 0 is set, and returns this. Exact allocator ownership and runtime AI behavior remain unproven.",
                new String[] {"CCarverAI__ScalarDeletingDestructor"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00422580", "CCarverAI__dtor_base", "__fastcall", voidType,
                "Signature/comment correction: CCarverAI destructor-base resets the base monitor-style vtable, removes linked reader slots at +0x28/+0x24/+0xc from their sets, and calls CMonitor__Shutdown. Exact CCarverAI layout, source identity, and runtime AI behavior remain unproven.",
                new String[] {"CCarverAI__Destructor"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422620", "CCarver__UpdateMotionAndWingPose", "__fastcall", voidType,
                "Function-boundary recovery and signature correction: Carver motion update handles flag-bit-4 rotation reset, calls CUnit__UpdateMotionAndTrailEffects, moves the wing/blend field toward its target, computes a speed-scaled vector, and dispatches vfunc +0x70. Exact source method name, concrete layout, runtime motion behavior, and rebuild parity remain unproven.",
                new String[] {"CCarver__Process_candidate"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422760", "CCarverAI__OpenWings", "__fastcall", voidType,
                "Signature/comment correction: when the Carver wing state is closed, resolves the wingopen animation, plays it through the owning unit animation vfunc, and marks state +0x27c as opening. Runtime animation behavior and concrete layout remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004227a0", "CCarverAI__CloseWings", "__fastcall", voidType,
                "Signature/comment correction: when the Carver wing state is attack/open, resolves the wingclose animation, plays it through the owning unit animation vfunc, and marks state +0x27c as closing. Runtime animation behavior and concrete layout remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004227e0", "CCarverAI__OnHit", "__thiscall", voidType,
                "Signature/comment correction: Carver hit override takes this, otherThing, and collisionReport; when support/gate fields allow and the other thing has unit-like type bits, it triggers the die vfunc before forwarding to the CThing hit helper. Exact source virtual name, type-bit labels, runtime hit behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("otherThing", voidPtr), param("collisionReport", voidPtr)}),
            new Spec("0x00422820", "CCarverAI__Fire", "__fastcall", intType,
                "Signature/comment correction: Carver AI fire helper checks the owner weapon/fire readiness vfunc, transitions wing/attack animation state from open to attack or closing to launch, and returns 0 in the current decompile. Runtime weapon/fire behavior and exact source identity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422930", "CCarverAI__SetLastAttackTime", "__fastcall", voidType,
                "Signature/comment correction: stores the current global time into the Carver AI last-attack timestamp field at +0x288. Exact field name, source identity, and runtime attack behavior remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422940", "CCarverAI__IsRecentlyAttacked", "__fastcall", intType,
                "Signature/comment correction: returns true while current time is still below last-attack timestamp plus the short cooldown constant. Exact field name, runtime attack behavior, and source identity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422970", "CCarverAI__CanStartAttack", "__fastcall", intType,
                "Function-boundary recovery and signature correction: returns true only when the wing/blend field is below the threshold and the longer attack cooldown from +0x288 has expired. Exact source method name, field semantics, and runtime attack behavior remain unproven.",
                new String[] {"CCarverAI__CanAttack_candidate"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004229b0", "CarverAimGlobals__ResetVector", "__cdecl", voidType,
                "Function-boundary recovery and signature correction: zeroes the three Carver aim/vector globals at 0x00662c60..0x00662c68. Exact source identity, global ownership, and runtime aiming behavior remain unproven.",
                new String[] {"CCarverAimGlobals__Reset_candidate"},
                new ParameterImpl[] {}),
            new Spec("0x004229d0", "CarverAimGlobals__InitMatrix", "__cdecl", voidType,
                "Function-boundary recovery and signature correction: initializes the Carver aim/orientation global matrix block at 0x00662c30..0x00662c5c to identity-style rows. Exact source identity, global ownership, and runtime aiming behavior remain unproven.",
                new String[] {"CCarverAimGlobals__InitMatrix_candidate"},
                new ParameterImpl[] {}),
            new Spec("0x00422aa0", "CCarverAI__RefreshTargetReaderAndScheduleMove", "__thiscall", voidType,
                "Function-boundary recovery and signature correction: Carver AI target-reader update handles an existing tracked target, retargets/clears the active reader when close enough, dispatches AI vfuncs, schedules event 0xbb9, and closes wings. Exact source virtual name, event semantics, runtime AI behavior, and rebuild parity remain unproven.",
                new String[] {"CCarverAI__Event3000Candidate"},
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)}),
            new Spec("0x00422b90", "CCarverAI__UpdateAttackAndReschedule", "__thiscall", voidType,
                "Function-boundary recovery and signature correction: Carver AI attack update checks nearby enemies, updates target tracking, opens/closes wings by target range, aims toward or away from the target, and reschedules event 3000 with a random delay. Exact source virtual name, runtime AI/weapon behavior, and rebuild parity remain unproven.",
                new String[] {"CCarverAI__UpdateAttackCandidate"},
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)}),
            new Spec("0x00422db0", "CCarverAI__CheckNearbyEnemies", "__fastcall", voidType,
                "Signature/comment correction: scans map-who entries around the Carver owner, checks nearby unit-like enemies tied to this owner and above a height/field threshold, and updates the last-attack timestamp on a qualifying candidate. Exact target semantics, source identity, and runtime AI behavior remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00422f90", "CCarverGuide__ctor", "__thiscall", voidPtr,
                "Signature/comment correction: CCarverGuide constructor delegates to CAirGuide__ctor with the guide target, then installs the CCarverGuide vtable. Exact source identity, concrete guide layout, and runtime navigation behavior remain unproven.",
                new String[] {"CCarverGuide__Constructor"},
                new ParameterImpl[] {param("this", voidPtr), param("guideTarget", voidPtr)}),
            new Spec("0x00422fb0", "CCarverGuide__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Signature/comment correction: CCarverGuide scalar-deleting destructor wrapper calls CCarverGuide__dtor_base, frees this when flags bit 0 is set, and returns this. Exact allocator ownership and runtime guide behavior remain unproven.",
                new String[] {"CCarverGuide__ScalarDeletingDestructor"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00422fd0", "CCarverGuide__dtor_base", "__fastcall", voidType,
                "Signature/comment correction: CCarverGuide destructor-base removes the active-reader slot at +0x2c when linked, then calls CMonitor__Shutdown. Exact concrete layout, source identity, and runtime guide behavior remain unproven.",
                new String[] {"CCarverGuide__Destructor"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00423490", "CCarverGuide__HandleEvent", "__thiscall", voidType,
                "Function-boundary recovery and signature correction: CCarverGuide event handler forwards non-0x7d1 events to CAirGuide__HandleEvent; for 0x7d1 it refreshes the nearest target reader and reschedules itself with a random delay. Exact source virtual name, runtime navigation behavior, and rebuild parity remain unproven.",
                new String[] {"CCarverGuide__HandleEvent_candidate"},
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
