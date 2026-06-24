//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyGeneralVolumeBoatSignatureCorrection extends GhidraScript {
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00414970", "CGeneralVolume__EnableEntriesByName", "__thiscall", voidType,
                "Signature/comment correction: CGeneralVolume entry-name matcher walks linked entries plus the primary entry at +0x18, compares entryName against each payload name at +0xa4, and sets enable flag +0x9c on matches. Exact entry structure, string ownership, runtime volume behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("entryName", charPtr)}),
            new Spec("0x00414a40", "CGeneralVolume__DisableEntriesByNameAndReselect", "__thiscall", voidType,
                "Signature/comment correction: CGeneralVolume entry-name matcher walks linked entries plus the primary entry at +0x18, clears enable flag +0x9c on name matches, and reselects if the disabled entry was current. Exact entry structure, current-selection owner, runtime volume behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("entryName", charPtr)}),
            new Spec("0x00414b70", "CGeneralVolume__CountEnabledEntriesIncludingPrimary", "__fastcall", intType,
                "Name/signature correction: CGeneralVolume-style list helper counts linked entries whose flag +0x9c is set and includes the optional primary entry at +0x18 when enabled. Exact structure names, selection semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {"LinkedObjectList__CountFlag9C_IncludingExtra"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414cb0", "CDXBattleLine__PopulateBattleLineAndInfluenceOverlayVertices", "__thiscall", voidType,
                "Name/signature correction: CDXBattleLine overlay helper resets vertex count +0x60, walks the battle-line list at DAT_00855140 and influence/deferred list at DAT_008550a0, and appends colored overlay vertices via CDXBattleLine__AppendOverlayVertex. Exact list ownership, source identity, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {"CExplosionInitThing__PopulateBattleLinePoints"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00414e50", "CBoat__Init", "__thiscall", voidType,
                "Signature/comment correction: CBoat init takes a CBoat-like this and init pointer, applies boat init flags to the init object, calls CGroundUnit__Init, seeds speed/offset fields, allocates CBoatGuide/Warspite-adjacent helpers, and zeros state +0x260/+0x264/+0x268. Exact source identity, structure layouts, runtime boat behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)}),
            new Spec("0x00414fa0", "CBoatAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CBoatAI vtable destructor wrapper calls the local destructor body at 0x00414fc0, tests scalar-delete flag bit 0, optionally frees the object through OID__FreeObject, and returns this. Exact class hierarchy, allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CBoatAI__VFunc_01_00414fa0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00414fc0", "CBoatAI__dtor_body_00414fc0", "__fastcall", voidType,
                "Name/signature correction: destructor body used by CBoatAI scalar deleting destructor sets the vtable to 0x005d8d1c, unregisters pointer-set links at +0x28/+0x24/+0xc through CSPtrSet__Remove, then calls CMonitor__Shutdown. Exact base-class ownership, duplicate destructor clone reason, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00414fc0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00415060", "CUnitAI__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: CUnitAI vtable destructor wrapper calls the destructor body at 0x00415080, tests scalar-delete flag bit 0, optionally frees the object through OID__FreeObject, and returns this. Exact class hierarchy, allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__VFunc_01_00415060"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00415080", "CUnitAI__dtor_body_00415080", "__fastcall", voidType,
                "Name/signature correction: destructor body used by CUnitAI scalar deleting destructor sets the vtable to 0x005d8d1c, unregisters pointer-set links at +0x28/+0x24/+0xc through CSPtrSet__Remove, then calls CMonitor__Shutdown. Exact base-class ownership, duplicate destructor clone reason, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CUnitAI__ctor_like_00415080"},
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
