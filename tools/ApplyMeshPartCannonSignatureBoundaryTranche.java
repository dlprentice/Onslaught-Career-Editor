//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyMeshPartCannonSignatureBoundaryTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
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

    private Function getOrCreate(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
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
        Function fn = getOrCreate(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
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

        Function readBack = getOrCreate(spec, false);
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
            "meshpart-cannon-wave355",
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00495030", "CMeshPart__PassesBuggyCoreStateForStrictOptimize", "__cdecl", boolType,
                "Signature/comment/tag hardening: strict MeshPart optimization predicate that rejects names beginning with CORE or x1, considers the parent/subpart CORE relationship, and gates one mesh-kind/triangle-count case below 0x15. Static retail evidence only; exact source method identity, concrete MeshPart layout, runtime optimizer behavior, and rebuild parity remain unproven.",
                tags("meshpart", "signature-hardened", "optimizer-predicate"),
                false,
                new ParameterImpl[] {param("meshPart", voidPtr)}),
            new Spec("0x00495090", "CMeshPart__PassesBuggyCoreStateForMergeOptimize", "__cdecl", boolType,
                "Signature/comment/tag hardening: merge-pass MeshPart optimization predicate that rejects names beginning with CORE or x1 and gates one mesh-kind/triangle-count case below 0x15. Static retail evidence only; exact source method identity, concrete MeshPart layout, runtime optimizer behavior, and rebuild parity remain unproven.",
                tags("meshpart", "signature-hardened", "optimizer-predicate"),
                false,
                new ParameterImpl[] {param("meshPart", voidPtr)}),
            new Spec("0x004950f0", "CMeshPart__AnySubPartNameStartsWithCore", "__cdecl", boolType,
                "Rename/signature/comment hardening: walks the child/subpart pointer array at offsets +0x15c/+0x160 and returns whether any child name at +0xdc begins with the CORE token. Static retail evidence only; exact source method identity, concrete MeshPart container layout, runtime optimizer behavior, and rebuild parity remain unproven.",
                tags("meshpart", "signature-hardened", "core-token"),
                false,
                new ParameterImpl[] {param("partContainer", voidPtr)}),
            new Spec("0x00495230", "CMCCannon__Ctor", "__thiscall", voidPtr,
                "Signature/comment/tag hardening: CMCCannon constructor-style body called by CCannon::Init, initializes the CMotionController base, stores the owner/field pointer at +0x08, sets the CMCCannon vtable, and initializes +0x0c/+0x10 with 0xc479c000. Static retail evidence only; exact source constructor signature, concrete owner layout, runtime turret behavior, and rebuild parity remain unproven.",
                tags("cmccannon", "constructor", "signature-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("ownerField8", voidPtr)}),
            new Spec("0x00495260", "CMCCannon__ScalarDeletingDestructor", "__thiscall", voidPtr,
                "Rename/signature/comment hardening: scalar deleting destructor wrapper that calls CMCCannon__Dtor and frees this when flags bit 0 is set. Static retail evidence only; exact source destructor spelling, allocator ownership, runtime lifecycle behavior, and rebuild parity remain unproven.",
                tags("cmccannon", "destructor", "scalar-deleting", "signature-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", uintType)}),
            new Spec("0x00495280", "CMCCannon__Dtor", "__thiscall", voidType,
                "Rename/signature/comment hardening: CMCCannon destructor body that resets the CMCCannon vtable, clears field +0x08, and tail-calls the CMotionController base destructor body. Static retail evidence only; exact source destructor spelling, base-class lifecycle side effects, runtime behavior, and rebuild parity remain unproven.",
                tags("cmccannon", "destructor", "signature-hardened"),
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004bae60", "SharedMotionController__VFunc_NoOpFourArgs_004bae60", "__thiscall", voidType,
                "Recovered shared motion-controller vtable target used by CMCCannon slots 3 and 14: one-instruction no-op body returning with 0x10 bytes of caller arguments removed. Static retail evidence only; exact source virtual name, argument semantics, runtime behavior, and rebuild parity remain unproven.",
                tags("motion-controller", "function-boundary", "vtable-slot", "shared-vfunc", "no-op"),
                true,
                new ParameterImpl[] {param("this", voidPtr), param("arg0", voidPtr), param("arg1", voidPtr), param("arg2", voidPtr), param("arg3", voidPtr)}),
            new Spec("0x004952a0", "CMCCannon__VFunc_04_UpdateTurretBarrelTransform", "__thiscall", voidType,
                "Recovered CMCCannon vtable slot 4 boundary: uses the owner pointer at +0x08, checks MeshPart name tokens including turret and barrel, performs vector/matrix helper calls, writes transform/offset-style outputs, and returns with 0x10 bytes of caller arguments removed. Static retail evidence only; exact source virtual name, concrete transform/output layout, runtime turret animation behavior, and rebuild parity remain unproven.",
                tags("cmccannon", "motion-controller", "function-boundary", "vtable-slot", "turret-barrel"),
                true,
                new ParameterImpl[] {param("this", voidPtr), param("meshPart", voidPtr), param("heightAdjustOut", voidPtr), param("transformOut", voidPtr), param("reservedArg", intType)})
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
            throw new IllegalStateException("MeshPart/CMCCannon signature-boundary tranche failed for " + failed + " target(s)");
        }
    }
}
