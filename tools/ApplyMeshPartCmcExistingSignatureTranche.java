//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMeshPartCmcExistingSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private boolean isDryRun(String mode) {
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

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function existingFunction(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
        }

        if (!fn.getName().equals(spec.name)) {
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

        Function readBack = existingFunction(address);
        if (readBack == null || !readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "meshpart-cmc-wave356",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType boolType = BooleanDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x004956a0", "Mat34__Add", "__thiscall", voidType,
                "Signature/comment/tag hardening: Mat34 add helper. ECX is the left matrix, stack arg1 is the output matrix, stack arg2 is the right matrix, and the function returns with ret 0x8. Static retail evidence only; exact source identity, concrete matrix type, local names, runtime behavior, and rebuild parity remain unproven.",
                tags("math", "signature-hardened", "mat34"),
                new ParameterImpl[] {param("this", voidPtr), param("outMatrix", voidPtr), param("rhsMatrix", voidPtr)}),
            new Spec("0x004957d0", "CMeshPart__AnySubPartNameIsTurretOrStartsWithBarrel", "__cdecl", boolType,
                "Rename/signature/comment hardening: walks child/subpart pointers at +0x15c/+0x160 and returns whether any child name exactly matches turret or starts with barrel. Static retail evidence only; exact source identity, concrete MeshPart layout, runtime optimizer behavior, and rebuild parity remain unproven.",
                tags("meshpart", "signature-hardened", "token-predicate"),
                new ParameterImpl[] {param("partContainer", voidPtr)}),
            new Spec("0x00495930", "CMCComponent__Ctor", "__thiscall", voidPtr,
                "Rename/signature/comment hardening: CMCComponent constructor-style body initializes the CMotionController base, stores the owner/field pointer at +0x08, sets vtable 0x005dc2d8, and initializes +0x0c/+0x10 with 0xc479c000. Static retail evidence only; exact source constructor signature, concrete owner layout, runtime component behavior, and rebuild parity remain unproven.",
                tags("cmccomponent", "constructor", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("ownerField8", voidPtr)}),
            new Spec("0x00495960", "CMCComponent__ScalarDeletingDestructor", "__thiscall", voidPtr,
                "Rename/signature/comment hardening: scalar deleting destructor wrapper that calls CMCComponent__Dtor and frees this when flags bit 0 is set. Static retail evidence only; exact source destructor spelling, allocator ownership, runtime lifecycle behavior, and rebuild parity remain unproven.",
                tags("cmccomponent", "destructor", "scalar-deleting", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", uintType)}),
            new Spec("0x00495980", "CMCComponent__Dtor", "__thiscall", voidType,
                "Rename/signature/comment hardening: CMCComponent destructor body resets vtable 0x005dc2d8, clears field +0x08, and tail-calls the CMotionController base destructor body. Static retail evidence only; exact source destructor spelling, base-class lifecycle side effects, runtime behavior, and rebuild parity remain unproven.",
                tags("cmccomponent", "destructor", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00495e00", "Mat34__Subtract", "__thiscall", voidType,
                "Signature/comment/tag hardening: Mat34 subtract helper. ECX is the left matrix, stack arg1 is the output matrix, stack arg2 is the right matrix, and the function returns with ret 0x8. Static retail evidence only; exact source identity, concrete matrix type, local names, runtime behavior, and rebuild parity remain unproven.",
                tags("math", "signature-hardened", "mat34"),
                new ParameterImpl[] {param("this", voidPtr), param("outMatrix", voidPtr), param("rhsMatrix", voidPtr)}),
            new Spec("0x00495ed0", "Mat34__ScaleByScalar", "__thiscall", voidType,
                "Owner/signature/comment correction: matrix scale helper formerly labeled as CMCMech. ECX is the source matrix, stack arg1 is the output matrix, stack arg2 is the scalar float, and the function returns with ret 0x8. Static retail evidence only; exact source identity, concrete matrix type, local names, runtime behavior, and rebuild parity remain unproven.",
                tags("math", "signature-hardened", "mat34", "owner-corrected"),
                new ParameterImpl[] {param("this", voidPtr), param("outMatrix", voidPtr), param("scalar", floatType)}),
            new Spec("0x00496090", "CMCDropship__Ctor", "__thiscall", voidPtr,
                "Rename/signature/comment hardening: CMCDropship constructor-style body initializes the CMotionController base, stores the owner/field pointer at +0x08, sets vtable 0x005dc304, writes +0x10 with 0xc479c000, and initializes +0x0c to -1. Static retail evidence only; exact source constructor signature, concrete owner layout, runtime dropship behavior, and rebuild parity remain unproven.",
                tags("cmcdropship", "constructor", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("ownerField8", voidPtr)}),
            new Spec("0x004960c0", "CMCDropship__ScalarDeletingDestructor", "__thiscall", voidPtr,
                "Rename/signature/comment hardening: scalar deleting destructor wrapper that calls CMCDropship__Dtor and frees this when flags bit 0 is set. Static retail evidence only; exact source destructor spelling, allocator ownership, runtime lifecycle behavior, and rebuild parity remain unproven.",
                tags("cmcdropship", "destructor", "scalar-deleting", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", uintType)}),
            new Spec("0x004960e0", "CMCDropship__Dtor", "__thiscall", voidType,
                "Rename/signature/comment hardening: CMCDropship destructor body resets vtable 0x005dc304, clears field +0x08, and tail-calls the CMotionController base destructor body. Static retail evidence only; exact source destructor spelling, base-class lifecycle side effects, runtime behavior, and rebuild parity remain unproven.",
                tags("cmcdropship", "destructor", "signature-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00496250", "CMeshPart__NameDoesNotStartWithDoor", "__cdecl", boolType,
                "Rename/signature/comment hardening: returns the negated result of a four-character Door token prefix check against the MeshPart name at +0xdc. Static retail evidence only; exact source identity, concrete MeshPart layout, runtime optimizer behavior, and rebuild parity remain unproven.",
                tags("meshpart", "signature-hardened", "token-predicate"),
                new ParameterImpl[] {param("meshPart", voidPtr)}),
            new Spec("0x00496270", "CMeshPart__HasDoorOpeningOrClosingAnimation", "__cdecl", boolType,
                "Rename/signature/comment hardening: checks an animation set for DoorOpening and DoorClosing tokens through FindAnimationIndex. Static retail evidence only; exact source identity, concrete animation layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("meshpart", "signature-hardened", "animation-token"),
                new ParameterImpl[] {param("animationSet", voidPtr)})
        };

        int changedOrWouldChange = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changedOrWouldChange++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " changed_or_would_change=" + changedOrWouldChange + " failed=" + failed + " dry=" + dryRun);
        if (failed > 0) {
            throw new IllegalStateException("MeshPart/CMC existing signature tranche failed for " + failed + " target(s)");
        }
    }
}
