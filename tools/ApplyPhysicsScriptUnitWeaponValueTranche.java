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

public class ApplyPhysicsScriptUnitWeaponValueTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
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
        if (spec.parameters.length == 0) {
            sb.append("void");
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
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getFunctionOrThrow(spec.address);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return needsRename;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "physics-script-wave334",
            "physics-script",
            "unit-weapon-value-tranche",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00432a50", "CUnitAlligence__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CUnitAlligence; it calls CUnitAlligence__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. The Alligence spelling is retained from current binary/source-adjacent evidence; exact source identity, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitAlligence__VFunc_00_00432a50"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00432a70", "CUnitAlligence__dtor", "__fastcall", voidType,
                "Name/signature correction: CUnitAlligence destructor body sets the derived vtable, deletes the child value pointer at +0x8 through vtable slot 0 when present, then restores the CPhysicsUnitValue base vtable. Exact source identity, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitAlligence__ctor_like_00432a70"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00432c00", "CUnitSoundMaterial__ApplyToUnitData", "__thiscall", voidType,
                "Name/signature correction: CUnitSoundMaterial apply slot rounds the scalar at this +0x8 and writes it to the unit data/init-like field at +0xe4. Exact target structure, source identity, runtime sound-material behavior, and rebuild parity remain unproven.",
                tags("unit-data-apply"),
                new String[] {"CUnitSoundMaterial__VFunc_01_00432c00"},
                new ParameterImpl[] {param("this", voidPtr), param("unitData", voidPtr), param("context", voidPtr)}),
            new Spec("0x00432c70", "CUnitMaxLegsLifted__ApplyToUnitData", "__thiscall", voidType,
                "Name/signature correction: CUnitMaxLegsLifted apply slot rounds the scalar at this +0x8 and writes it to the unit data/init-like field at +0x140. Exact target structure, source identity, runtime leg-lift behavior, and rebuild parity remain unproven.",
                tags("unit-data-apply"),
                new String[] {"CUnitMaxLegsLifted__VFunc_01_00432c70"},
                new ParameterImpl[] {param("this", voidPtr), param("unitData", voidPtr), param("context", voidPtr)}),
            new Spec("0x00432cc0", "CPhysicsUnitValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: base destructor body for CPhysicsUnitValue restores the base value vtable. Exact source identity, concrete inheritance, and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base"),
                new String[] {"CPhysicsUnitValue__ctor_like_00432cc0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00432f70", "CUnitNavMap__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CUnitNavMap load slot reads a child statement type from CDXMemBuffer, dispatches CreateStatementType14, and stores the loaded child statement at +0x8. Exact format, target statement layout, runtime nav-map behavior, and rebuild parity remain unproven.",
                tags("statement-load"),
                new String[] {"CUnitNavMap__VFunc_03_00432f70"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00432fa0", "CUnitNavMap__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CUnitNavMap; it calls CUnitNavMap__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact source identity, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitNavMap__VFunc_00_00432fa0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00432fc0", "CUnitNavMap__dtor", "__fastcall", voidType,
                "Name/signature correction: CUnitNavMap destructor body sets the derived vtable, deletes the child statement pointer at +0x8 through vtable slot 0 when present, then restores the CPhysicsUnitValue base vtable. Exact source identity, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitNavMap__ctor_like_00432fc0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004330b0", "CUnitBehaviour__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CUnitBehaviour load slot reads a child statement type from CDXMemBuffer, dispatches CreateStatementType12, and stores the loaded child statement at +0x8. Exact format, target statement layout, runtime behaviour field semantics, and rebuild parity remain unproven.",
                tags("statement-load"),
                new String[] {"CUnitBehaviour__VFunc_03_004330b0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x004330e0", "CUnitBehaviour__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CUnitBehaviour; it calls CUnitBehaviour__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact source identity, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitBehaviour__VFunc_00_004330e0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00433100", "CUnitBehaviour__dtor", "__fastcall", voidType,
                "Name/signature correction: CUnitBehaviour destructor body sets the derived vtable, deletes the child statement pointer at +0x8 through vtable slot 0 when present, then restores the CPhysicsUnitValue base vtable. Exact source identity, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitBehaviour__ctor_like_00433100"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00434100", "CPhysicsUnitValue__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: shared scalar-deleting destructor wrapper used by many unit value vtables; it calls CPhysicsUnitValue__dtor_base, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact subtype coverage, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base"),
                new String[] {"VFuncSlot_00_00434100"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00434300", "CPhysicsScriptStatements__CreateStatementType3", "__cdecl", voidPtr,
                "Signature/comment/tag hardening: factory for PhysicsScript type-3/weapon value records; it switches through weapon value ids 0x74 through 0x81, allocates typed value objects, assigns value vtables, and returns null for unsupported ids. Exact value class names, complete layout, runtime behavior, and rebuild parity remain unproven.",
                tags("value-factory"),
                new String[] {},
                new ParameterImpl[] {param("valueType", intType)}),
            new Spec("0x00434770", "CWeaponChargeLevel__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CWeaponChargeLevel load slot reads a charge level scalar into +0x108 and a name string into the owned string field at +0x8. Exact format, string lifetime, runtime weapon-charge behavior, and rebuild parity remain unproven.",
                tags("statement-load", "weapon-value"),
                new String[] {"CWeaponChargeLevel__VFunc_03_00434770"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x004347a0", "CPhysicsWeaponValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: base destructor body for CPhysicsWeaponValue restores the base weapon value vtable. Exact source identity, concrete inheritance, and runtime lifetime behavior remain unproven.",
                tags("destructor", "weapon-value"),
                new String[] {"CPhysicsWeaponValue__ctor_like_004347a0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00434a80", "CPhysicsWeaponValue__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: shared scalar-deleting destructor wrapper used by weapon value vtables; it calls CPhysicsWeaponValue__dtor_base, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact subtype coverage, class layout, and runtime lifetime behavior remain unproven.",
                tags("destructor", "weapon-value"),
                new String[] {"VFuncSlot_00_00434a80"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00434f20", "CWeaponIconName__ApplyToWeaponByName", "__thiscall", voidType,
                "Name/signature correction: CWeaponIconName apply slot searches the global weapon list at DAT_008553e8 by weapon name and replaces the matching weapon record icon string with the string held at this +0x8. Exact weapon record layout, source identity, runtime UI behavior, and rebuild parity remain unproven.",
                tags("weapon-value", "unit-data-apply"),
                new String[] {"CWeaponIconName__VFunc_01_00434f20"},
                new ParameterImpl[] {param("this", voidPtr), param("weaponName", charPtr), param("context", voidPtr)}),
        };

        int renamed = 0;
        int skipped = 0;
        int bad = 0;
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            try {
                boolean didRename = applySpec(spec, dryRun);
                if (didRename) {
                    renamed++;
                } else {
                    skipped++;
                }
            } catch (Exception ex) {
                bad++;
                println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                if (!dryRun) {
                    throw ex;
                }
            }
        }

        println("ApplyPhysicsScriptUnitWeaponValueTranche complete: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + (dryRun ? 0 : specs.length - bad) +
            " skipped=" + skipped +
            " renamed=" + renamed +
            " missing=0 bad=" + bad);
        if (bad != 0) {
            throw new IllegalStateException("Bad specs encountered: " + bad);
        }
    }
}
