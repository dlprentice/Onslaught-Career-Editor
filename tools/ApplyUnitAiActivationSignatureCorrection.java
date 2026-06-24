//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyUnitAiActivationSignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.tags = tags;
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

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return addr;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = addr(addrText);
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

    private Function recreateBoundaryIfNeeded(boolean dryRun, Spec spec) throws Exception {
        Address newEntry = addr("0x00429270");
        Address oldEntry = addr("0x00429280");
        Function newFn = getFunctionAt(newEntry);
        Function oldFn = getFunctionAt(oldEntry);

        if (newFn != null) {
            if (!newFn.getName().equals(spec.name) && !nameAllowed(newFn.getName(), spec)) {
                throw new IllegalStateException("Unexpected function name at 0x00429270: " + newFn.getName());
            }
            println((dryRun ? "DRY: " : "OK: ") + "0x00429270 boundary already present");
            return newFn;
        }

        if (oldFn == null) {
            throw new IllegalStateException("Boundary move requires old function at 0x00429280 or new function at 0x00429270");
        }
        if (!oldFn.getName().equals(spec.name) && !nameAllowed(oldFn.getName(), spec)) {
            throw new IllegalStateException("Unexpected old boundary name at 0x00429280: " + oldFn.getName());
        }

        if (dryRun) {
            println("DRY: would remove 0x00429280 " + oldFn.getName() + " and recreate at 0x00429270");
            return oldFn;
        }

        FunctionManager fm = currentProgram.getFunctionManager();
        boolean removed = fm.removeFunction(oldEntry);
        if (!removed) {
            throw new IllegalStateException("Failed to remove old function at 0x00429280");
        }

        disassemble(newEntry);
        newFn = createFunction(newEntry, null);
        if (newFn == null) {
            newFn = getFunctionAt(newEntry);
        }
        if (newFn == null) {
            throw new IllegalStateException("Function not present after create at 0x00429270");
        }
        newFn.setName(spec.name, SourceType.USER_DEFINED);
        println("OK: moved boundary 0x00429280 -> 0x00429270");
        return newFn;
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn;
        boolean boundaryMove = spec.address.equals("0x00429270");
        if (boundaryMove) {
            fn = recreateBoundaryIfNeeded(dryRun, spec);
        } else {
            fn = getFunctionOrThrow(spec.address);
        }

        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return needsRename || boundaryMove;
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
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename || boundaryMove;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        String[] commonTags = new String[] {"static-reaudit", "unitai-activation-wave325", "unitai-system", "signature-hardened"};
        String[] ownerTags = new String[] {"static-reaudit", "unitai-activation-wave325", "unitai-system", "signature-hardened", "owner-corrected"};
        String[] boundaryTags = new String[] {"static-reaudit", "unitai-activation-wave325", "unitai-system", "signature-hardened", "boundary-corrected"};

        Spec[] specs = new Spec[] {
            new Spec("0x00428710", "CUnitAI__GetRenderPosFromActorOrCache", "__thiscall", voidPtr,
                "Signature/name/comment/tag correction: CUnitAI-adjacent render-position virtual slot returns the caller output buffer after either forwarding to CActor__GetRenderPos when actor render state is active or refreshing/copying the cached component position fields. Exact virtual source name, concrete layouts, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_00_00428710"},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr), param("outRenderPos", voidPtr), param("unused", voidPtr)}),
            new Spec("0x00428770", "CUnitAI__GetRenderOrientationFromActorOrCache", "__thiscall", voidPtr,
                "Signature/name/comment/tag correction: CUnitAI-adjacent render-orientation virtual slot returns the caller output buffer after either forwarding to CActor__GetRenderOrientation when actor render state is active or refreshing/copying the cached orientation matrix. Exact virtual source name, concrete layouts, runtime render behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_01_00428770"},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr), param("outRenderOrientation", voidPtr), param("unused", voidPtr)}),
            new Spec("0x00428800", "CUnitAI__HandleTriggerEventAndMoveToOffset", "__fastcall", boolType,
                "Signature/comment/tag correction: UnitAI trigger/event handler marks the unit destroyed, optionally resets deployment graph state, releases child units, schedules an event, or derives a normalized offset from the active reader before dispatching the movement callback. Runtime trigger/movement behavior, exact source identity, concrete layouts, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004289b0", "CUnitAI__AdvanceActivationAnimationState", "__fastcall", boolType,
                "Signature/comment/tag correction: UnitAI activation animation state machine compares current animation indexes against Hit/retract/normal/Activate/Activated/Deactivated tokens, plays the next animation, updates activation fields, and falls back to deploy/fire animation completion. Runtime animation behavior, exact source identity, concrete layouts, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428b50", "CUnit__SetReaderAndComputeRelativeYaw", "__thiscall", voidType,
                "Signature/comment/tag correction: CUnit active-reader setter stores the reader/context pair, queries the reader transform callback, computes relative yaw against reader heading, and mirrors flag 0x100000 when present. The third observed stack argument is unused in the current decompile. Runtime reader behavior, concrete layouts, exact source identity, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr), param("reader", voidPtr), param("readerContext", voidPtr), param("unusedMode", intType)}),
            new Spec("0x00428bc0", "CUnitAI__GetTargetHeadingWithOffset", "__fastcall", doubleType,
                "Signature/comment/tag correction: returns the active reader heading plus the CUnitAI relative-yaw offset when a reader exists, otherwise returns the zero heading constant. Runtime heading behavior, concrete layouts, exact source identity, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428c70", "CUnitAI__RunSharedStepAndMaybeTriggerFlag4Action", "__fastcall", voidType,
                "Signature/comment/tag correction: shared UnitAI step resets field D0 from the global threshold and dispatches vtable slot 0x38 when flag bit 4 is set. Runtime AI-step behavior, exact slot identity, concrete layouts, and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428cb0", "CUnitAI__PlayHitAnimationAndSetFlag", "__fastcall", voidType,
                "Owner/signature/comment/tag correction: neighboring UnitAI animation helper plays the Hit animation token and sets field +0x2bc to 1; the prior ExplosionInitThing owner was caller-derived and too narrow for this callee body. Runtime hit-animation behavior, exact source identity, concrete layouts, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__TriggerHitAnimationAndSetFlag"},
                ownerTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428cf0", "CUnitAI__ForwardCommandToAttachedNodeThenDispatch", "__thiscall", voidType,
                "Signature/comment/tag correction: forwards the command to the active reader vtable slot 0x1ac when config +0x134 and reader state allow it, then calls CUnitAI__AccumulateForwardedCommandScore. The decompile still carries an EDI-sourced score value, so caller-context and concrete parameter recovery remain open. Runtime command behavior and rebuild parity remain unproven.",
                new String[] {},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr), param("command", intType), param("unusedStackParam", intType)}),
            new Spec("0x00428d50", "CUnitAI__PlayActivateAnimationOrFinalizeActivated", "__fastcall", voidType,
                "Signature/name/comment/tag correction: activation helper looks up the Activate animation token, finalizes activation immediately when missing, or plays the Activate animation through vtable slot 0xf0. Exact virtual slot name, runtime animation behavior, concrete layouts, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_22_00428d50"},
                commonTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00428e80", "CComponentAI__ClearReaderIfTargetDestroyedThenForward", "__fastcall", voidType,
                "Owner/signature/comment/tag correction: shared Component AI vtable slot used by CComponentBomberAI and CFenrirMainGunAI clears the active reader when the reader target has flag bit 4 set, then forwards to vtable slot 0x2c. Exact subtype source identity, runtime cleanup behavior, concrete layouts, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_04_00428e80"},
                ownerTags,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00429270", "CUnitAI__UpdateHeadingTowardTargetClamped", "__fastcall", voidType,
                "Boundary/signature/comment/tag correction: recovered true entry at 0x00429270 so the prologue that loads the UnitAI pointer from the turn context is included before heading/clamp logic. The function updates UnitAI heading toward the active target with config turn-rate and clamp fields. Runtime steering behavior, exact source identity, concrete layouts, and rebuild parity remain unproven.",
                new String[] {},
                boundaryTags,
                new ParameterImpl[] {param("turnContext", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int renamedOrMoved = 0;
        for (Spec spec : specs) {
            boolean changedIdentity = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (changedIdentity) {
                    renamedOrMoved++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed_or_moved=" + renamedOrMoved + " missing=0 bad=0");
    }
}
