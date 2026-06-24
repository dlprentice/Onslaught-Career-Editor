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

public class ApplyBoatGuideBomberLifecycleSignatureCorrection extends GhidraScript {
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

        Spec[] specs = new Spec[] {
            new Spec("0x00415d70", "CBoatGuide__ctor", "__thiscall", voidPtr,
                "Name/signature correction: CBoatGuide constructor wrapper is called by CBoat__Init, passes one init/context pointer to CGuide__ctor_like_0047e290, writes vtable 0x005d8d5c, and returns this. Exact source identity, CGuide/CBoatGuide layout, runtime pathfinding behavior, and rebuild parity remain unproven.",
                new String[] {"CBoatGuide__ctor_like_00415d70"},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x004161a0", "CBomberAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CBomberAI vtable destructor wrapper calls the local destructor body at 0x004161c0, tests scalar-delete flag bit 0, optionally frees the object through OID__FreeObject, and returns this. Bomber.cpp source is missing; exact class hierarchy, allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CBomberAI__VFunc_01_004161a0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004161c0", "CBomberAI__dtor_body_004161c0", "__fastcall", voidType,
                "Name/signature correction: destructor body used by CBomberAI scalar deleting destructor sets the vtable to 0x005d8d1c, unregisters pointer-set links at +0x28/+0x24/+0xc through CSPtrSet__Remove, then calls CMonitor__Shutdown. Bomber.cpp source is missing; exact base-class ownership, duplicate destructor clone reason, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_004161c0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00416260", "CBomberGuide__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CBomberGuide vtable destructor wrapper calls the local destructor body at 0x00416280, tests scalar-delete flag bit 0, optionally frees the object through OID__FreeObject, and returns this. Bomber.cpp source is missing; exact class hierarchy, allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CBomberGuide__VFunc_01_00416260"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00416280", "CBomberGuide__dtor_body_00416280", "__fastcall", voidType,
                "Name/signature correction: destructor body used by CBomberGuide scalar deleting destructor unregisters the pointer-set link at +0x2c through CSPtrSet__Remove, then calls CMonitor__Shutdown. Bomber.cpp source is missing; exact guide layout, ownership semantics, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CBomberGuide__DetachFromSetAndShutdownMonitor"},
                new ParameterImpl[] {param("this", voidPtr)})
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
