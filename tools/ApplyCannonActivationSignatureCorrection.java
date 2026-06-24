//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCannonActivationSignatureCorrection extends GhidraScript {
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
        DataType floatPtr = new PointerDataType(FloatDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x0041b1a0", "CCannon__Init", "__thiscall", voidType,
                "Signature/comment hardening: CCannon init takes this plus an init object, sets the init flags, calls CGroundUnit__Init, chooses Active/Inactive animation state from +0x214, allocates 0x20/0x60/0x14 helper objects, stores key helpers at +0x208/+0x13c/+0x70, seeds +0x260/+0x264 state, and registers with the world occupancy grid. Exact source identity, class layout, runtime turret behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x0041b370", "CCannon__UpdateState", "__fastcall", voidType,
                "Signature/comment hardening: CCannon activation update tests enable/target-controller state through +0x214 and +0x13c, transitions through Activate/Deactivate animation states, updates state +0x260 and timestamp +0x264, and then calls the CGroundUnit linked-effects/height-clearance helper. Exact source method name, runtime turret behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0041b450", "CCannon__VFuncSlot_02_RemoveFromWorldAndForward", "__fastcall", voidType,
                "Name/signature correction: this is not a destructor body. RTTI read-back places the slot-2 entry in CCannon, CSentinel, and CWarspiteDome vtables; the body removes the unit from the world occupancy-grid wrapper and forwards to VFuncSlot_02_004f95d0. Exact owning base class, source virtual name, runtime world/render behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__Destructor"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0041b470", "CCannon__AdvanceActivationAnimationState", "__fastcall", intType,
                "Name/signature correction: this no-argument helper does not set an arbitrary state; it reads the current animation, resolves Activate/Deactivate/Active/Inactive animation ids, advances completed activation/deactivation transitions, and updates state +0x260. Exact source method name, return semantics, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__SetState"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0041b540", "CCannon__GetMidpoint", "__thiscall", voidType,
                "Signature/comment hardening: resolves a target position through CCannon__SelectTarget, adds this position at +0x1c/+0x20/+0x24, and scales the result by the 0.5 constant to produce an output midpoint. Exact vector type/layout, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("outMidpoint", floatPtr)}),
            new Spec("0x0041b590", "CCannon__VFuncSlot_50_MarkDestroyedResetDeployGraph", "__fastcall", intType,
                "Name/signature correction: current read-back does not support the old CanFire label. RTTI/vtable refs place this slot-50 entry in CCannon, CWarspiteDome, and CGroundVehicle vtables; the body calls CGroundUnit__MarkDestroyedAndResetState, then CUnit__ResetDeploymentGraphAndScheduleEvent on success. Exact owning base class, source virtual name, runtime destruction/deploy behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__CanFire"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0047c970", "CGroundUnit__UpdateLinkedEffectsByHeightClearance", "__fastcall", voidType,
                "Wave392 owner correction: CGroundUnit vtable 0x005e32d4 slot 66 points here, superseding the over-specific CCannon owner label. The helper samples height clearance, finalizes or updates the linked +0x1d4/+0x1e4 effect state, adjusts motion/attachment state including +0x25c, and calls CUnit__UpdateMotionAttachmentsAndEffects. Cross-subclass xrefs remain expected; GroundUnit.cpp source body is missing, so exact source identity, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__UpdateLinkedEffectsByHeightClearance"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0047ce80", "CGroundUnit__MarkDestroyedAndResetState", "__fastcall", intType,
                "Wave392 owner correction: CGroundUnit vtable 0x005e32d4 slot 50 points here, superseding the over-specific CCannon owner label. The body calls CUnit__MarkDestroyedAndCleanupLinks, returns 0 on failure, clears +0x25c on success, and returns 1. Cross-subclass xrefs remain expected; exact source identity, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CCannon__MarkDestroyedAndResetState"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004fd4d0", "CCannon__SelectTarget", "__thiscall", voidType,
                "Signature/comment hardening: takes this plus outTargetPosition; if linked target +0x178 exists, forwards to CDiveBomber__SelectTarget, otherwise writes this unit world/targeting position through CUnitAI__GetWorldPositionForTargeting. Exact source method name, target semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("outTargetPosition", floatPtr)})
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
