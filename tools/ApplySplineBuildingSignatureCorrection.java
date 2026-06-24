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

public class ApplySplineBuildingSignatureCorrection extends GhidraScript {
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
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);

        Spec[] specs = new Spec[] {
            new Spec("0x00416e30", "CBSpline__BasisFunction", "__thiscall", floatType,
                "Signature/comment hardening: Cox-de Boor B-spline basis recursion over the knot vector at this+0x8; base case tests the knot interval and recursive cases combine N(i,k-1,t) / N(i+1,k-1,t) while avoiding equal-knot divisions. Concrete CBSpline layout, exact source identity, local names, runtime camera/path behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("basisIndex", intType), param("order", intType), param("t", floatType)}),
            new Spec("0x00416fc0", "CBSpline__GetPoint", "__thiscall", voidType,
                "Signature/comment hardening: evaluates a CBSpline point by walking the control-point list, calling CBSpline__BasisFunction for each weighted contribution, and writing four float slots to outPoint. Concrete point/control-list layout, fourth-slot semantics, exact source identity, runtime camera/path behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("outPoint", floatPtr), param("t", floatType)}),
            new Spec("0x00417390", "CBuilding__CreateRepairPadAI", "__thiscall", voidType,
                "Signature/comment hardening: allocates a 0x60 repair-pad AI component using the Building.cpp debug path, compares the level-data model name with Forseti Repair Pad, stores the component at this+0x13c, and sets the this+0x1f4 flag on the Forseti branch. Exact CBuilding/repair-pad AI layout, constructor target identity, runtime repair behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00417480", "CRepairPadAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CRepairPadAI scalar-deleting destructor wrapper calls the local destructor body at 0x004174a0, tests scalar-delete flag bit 0, optionally frees the object through OID__FreeObject, and returns this. Exact class hierarchy, allocator ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CRepairPadAI__VFunc_01_00417480"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004174a0", "CRepairPadAI__dtor_body_004174a0", "__fastcall", voidType,
                "Name/signature correction: CRepairPadAI destructor body used by the scalar-deleting destructor sets the vtable to 0x005d8d1c, unregisters pointer-set links at +0x28/+0x24/+0xc through CSPtrSet__Remove, then calls CMonitor__Shutdown. Exact CRepairPadAI hierarchy/layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_004174a0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00417540", "CThing__RenderAndUpdateStaticShadow", "__thiscall", voidType,
                "Signature/comment correction: ret 0x4 render wrapper takes one stack renderContext argument, calls CThing__Render using the live ESI render flags/context, updates static-shadow visibility through CStaticShadows__UpdateVisibility, and runs the frame-gated callback while DAT_00660540 remains active. Exact render-call convention, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("renderContext", voidPtr)}),
            new Spec("0x00417590", "CBuilding__dtor_body_00417590", "__fastcall", voidType,
                "Name/signature correction: CBuilding destructor body resets the primary vtable to 0x005d8eb4, resets the render-position table pointer to 0x005d8e3c, then tail-calls the current CUnit cleanup target. Exact base destructor identity, CBuilding layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CBuilding__ctor_like_00417590"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004176a0", "CBuilding__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CBuilding scalar-deleting destructor wrapper calls the local destructor body at 0x00417590, tests scalar-delete flag bit 0, optionally frees the object through OID__FreeObject, and returns this. Exact class hierarchy, allocator ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CBuilding__VFunc_01_004176a0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x004176c0", "CThing__InitRenderThingFromInitMeshName", "__thiscall", voidType,
                "Signature/comment correction: ret 0x4 init helper takes one stack init pointer, builds %s.msh render names from init/profile data, creates the render object through PCRTID__CreateObject, and stores it at this+0x30. Exact render-object type, source identity, local temporary layouts, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)})
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
