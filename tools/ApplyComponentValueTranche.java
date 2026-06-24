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

public class ApplyComponentValueTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
            this.createIfMissing = createIfMissing;
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

    private Address parseTargetAddress(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return addr;
    }

    private Function getExistingFunction(Address addr) {
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getOrCreateFunction(Spec spec, boolean dryRun) throws Exception {
        Address addr = parseTargetAddress(spec.address);
        Function fn = getExistingFunction(addr);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        boolean disasmOk = disassemble(addr);
        fn = createFunction(addr, null);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address + " disassembleOk=" + disasmOk);
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
        Function fn = getOrCreateFunction(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
            return true;
        }
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return needsRename;
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

        Function readBack = getOrCreateFunction(spec, false);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String fun(String address) {
        String value = address.startsWith("0x") || address.startsWith("0X") ? address.substring(2) : address;
        return "FUN_" + value.toLowerCase();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "physics-script-wave343",
            "physics-script",
            "component-value-tranche",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec componentScalar(String address, String name, String recordOffset, DataType voidType, DataType voidPtr, DataType charPtr) throws Exception {
        return new Spec(address, name, "__thiscall", voidType,
            "Recovered function boundary: searches DAT_00855400 by componentName and writes the raw scalar at this+0x8 to component record+" + recordOffset + ". The field semantic is not yet proven beyond offset-backed scalar behavior.",
            tags("function-boundary", "component-apply", "offset-backed-scalar"),
            new String[] {fun(address)},
            true,
            new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)});
    }

    private Spec componentFlag(String address, String name, String recordOffset, DataType voidType, DataType voidPtr, DataType charPtr) throws Exception {
        return new Spec(address, name, "__thiscall", voidType,
            "Recovered function boundary: searches DAT_00855400 by componentName and writes component record+" + recordOffset + " as 1 when the scalar at this+0x8 is positive, otherwise 0. Exact flag semantics and runtime behavior remain unproven.",
            tags("function-boundary", "component-apply", "offset-backed-flag"),
            new String[] {fun(address)},
            true,
            new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)});
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
            new Spec("0x004175b0", "CPhysicsScriptValue__GetTwoScalarSerializedSize8", "__fastcall", intType,
                "Recovered shared serialization helper: returns fixed serialized size 8 for two-scalar PhysicsScript values. It is reached from the type-10/component value vtable at 0x005da96c slot 2; exact source owner and runtime script behavior remain unproven.",
                tags("function-boundary", "shared-serialization", "two-scalar-value"),
                new String[] {fun("0x004175b0")},
                true,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00433170", "CComponentValue02__LoadFromMemBuffer", "__thiscall", voidType,
                "Recovered function boundary: type-10 component value id 0x2 load helper reads the compound value payload through CDXMemBuffer into this+0x8/this+0x108-style storage. Exact field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-value", "statement-load"),
                new String[] {fun("0x00433170")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),

            new Spec("0x004331e0", "CComponentValue13__GetSerializedSize", "__fastcall", intType,
                "Recovered function boundary: type-10 component value id 0x13 serialized-size helper over compound string/value storage. Exact field semantics, file-format completeness, and runtime behavior remain unproven.",
                tags("function-boundary", "component-value", "serialized-size"),
                new String[] {fun("0x004331e0")},
                true,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x00433220", "CComponentValue13__LoadFromMemBuffer", "__thiscall", voidType,
                "Recovered function boundary: type-10 component value id 0x13 load helper reads the compound payload through CDXMemBuffer. Exact field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-value", "statement-load"),
                new String[] {fun("0x00433220")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),

            new Spec("0x0043c500", "CPhysicsScriptStatements__CreateStatementType10", "__cdecl", voidPtr,
                "Signature/comment correction: type-10 component-value factory over observed value ids 0x1..0x19 except 0x5; allocates scalar, flag, owned-string, based-on, indexed-scalar, and compound component values and installs vtables from 0x005da908 through 0x005daad4. Exact class layouts, field semantics, and runtime physics-script behavior remain unproven.",
                tags("value-factory", "component-value"),
                new String[] {"CPhysicsScriptStatements__CreateStatementType10"},
                false,
                new ParameterImpl[] {param("valueType", intType)}),

            componentScalar("0x0043ca70", "CComponentScalarD8__ApplyToComponentByName", "0xd8", voidType, voidPtr, charPtr),
            componentScalar("0x0043cb40", "CComponentScalarDC__ApplyToComponentByName", "0xdc", voidType, voidPtr, charPtr),
            componentScalar("0x0043cbe0", "CComponentScalarC0__ApplyToComponentByName", "0xc0", voidType, voidPtr, charPtr),
            componentScalar("0x0043cc80", "CComponentScalar158__ApplyToComponentByName", "0x158", voidType, voidPtr, charPtr),
            componentScalar("0x0043cd20", "CComponentScalarB8__ApplyToComponentByName", "0xb8", voidType, voidPtr, charPtr),
            componentScalar("0x0043cdc0", "CComponentScalarBC__ApplyToComponentByName", "0xbc", voidType, voidPtr, charPtr),
            componentFlag("0x0043ce60", "CComponentFlag124__ApplyToComponentByName", "0x124", voidType, voidPtr, charPtr),
            componentFlag("0x0043cf20", "CComponentFlag128__ApplyToComponentByName", "0x128", voidType, voidPtr, charPtr),
            componentFlag("0x0043cfe0", "CComponentFlag12C__ApplyToComponentByName", "0x12c", voidType, voidPtr, charPtr),
            componentFlag("0x0043d0a0", "CComponentFlag198__ApplyToComponentByName", "0x198", voidType, voidPtr, charPtr),
            componentFlag("0x0043d160", "CComponentFlag114__ApplyToComponentByName", "0x114", voidType, voidPtr, charPtr),
            componentFlag("0x0043d220", "CComponentFlag19C__ApplyToComponentByName", "0x19c", voidType, voidPtr, charPtr),
            componentFlag("0x0043d2e0", "CComponentFlag134__ApplyToComponentByName", "0x134", voidType, voidPtr, charPtr),
            componentFlag("0x0043d3a0", "CComponentFlag108__ApplyToComponentByName", "0x108", voidType, voidPtr, charPtr),
            componentScalar("0x0043d460", "CComponentScalar160__ApplyToComponentByName", "0x160", voidType, voidPtr, charPtr),

            new Spec("0x0043d500", "CComponentIndexedScalar164__ApplyToComponentByName", "__thiscall", voidType,
                "Recovered function boundary: searches DAT_00855400 by componentName and writes the raw scalar at this+0x8 into component record+0x164 plus the dword index at this+0xc. Exact indexed-field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-apply", "indexed-scalar"),
                new String[] {fun("0x0043d500")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043d5a0", "CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: shared scalar-deleting destructor wrapper used by type-10 component-value leaf vtables; calls CPhysicsComponentValue__dtor_base at 0x0043dcc0, optionally frees this via OID__FreeObject, and returns this. Specific leaf owner, concrete layouts, and runtime lifetime behavior remain unproven.",
                tags("destructor", "shared-vtable-slot"),
                new String[] {"VFuncSlot_00_0043d5a0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),

            new Spec("0x0043d5c0", "CComponentValue02__ApplyToComponentByName", "__thiscall", voidType,
                "Recovered function boundary: type-10 component value id 0x2 apply helper searches DAT_00855400 by componentName and dispatches a compound component update using this+0x8, this+0x108, and this+0x208-style payload fields. Exact field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-apply", "compound-component-value"),
                new String[] {fun("0x0043d5c0")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043d670", "CComponentValue02__GetSerializedSize", "__fastcall", intType,
                "Recovered function boundary: type-10 component value id 0x2 serialized-size helper over compound string/value storage. Exact field semantics, file-format completeness, and runtime behavior remain unproven.",
                tags("function-boundary", "component-value", "serialized-size"),
                new String[] {fun("0x0043d670")},
                true,
                new ParameterImpl[] {param("this", voidPtr)}),

            new Spec("0x0043d6b0", "CComponentValue13__ApplyToComponentByName", "__thiscall", voidType,
                "Recovered function boundary: type-10 component value id 0x13 apply helper searches DAT_00855400 by componentName and dispatches a compound component update using string/value payload fields. Exact field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-apply", "compound-component-value"),
                new String[] {fun("0x0043d6b0")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043d760", "CComponentMesh__ApplyToComponentByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_00855400 by componentName and replaces the owned mesh string at component record+0x2c from this+0x8. Exact record layout and runtime component behavior remain unproven.",
                tags("component-apply", "owned-string-copy"),
                new String[] {"CComponentMesh__VFunc_01_0043d760"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043d850", "CComponentValue04__ApplyToComponentByName", "__thiscall", voidType,
                "Recovered function boundary: type-10 component value id 0x4 apply helper searches DAT_00855400 by componentName and dispatches an owned-string component update through helper 0x00511720. Exact target field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-apply", "owned-string-helper"),
                new String[] {fun("0x0043d850")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043d8f0", "CComponentVent__ApplyToComponentByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_00855400 by componentName and replaces the owned vent string at component record+0x98 from this+0x8. Exact record layout and runtime component behavior remain unproven.",
                tags("component-apply", "owned-string-copy"),
                new String[] {"CComponentVent__VFunc_01_0043d8f0"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043d9f0", "CComponentValue0E__ApplyToComponentByName", "__thiscall", voidType,
                "Recovered function boundary: type-10 component value id 0xe apply helper searches DAT_00855400 by componentName and dispatches an owned-string component update through helper 0x005117c0. Exact target field semantics and runtime behavior remain unproven.",
                tags("function-boundary", "component-apply", "owned-string-helper"),
                new String[] {fun("0x0043d9f0")},
                true,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043da90", "CComponentNoise__ApplyToComponentByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_00855400 by componentName and replaces the owned noise string at component record+0xa8 from this+0x8. Exact record layout and runtime component behavior remain unproven.",
                tags("component-apply", "owned-string-copy"),
                new String[] {"CComponentNoise__VFunc_01_0043da90"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043db90", "CComponentBasedOn__ApplyToComponentByName", "__thiscall", voidType,
                "Name/signature correction: searches DAT_00855400 by componentName, resolves the based-on source name at this+0x8, and calls CComponentBasedOn__CopyFrom with the matched destination and source/null. Exact record layout and runtime component behavior remain unproven.",
                tags("component-apply", "based-on-copy"),
                new String[] {"CComponentBasedOn__VFunc_01_0043db90"},
                false,
                new ParameterImpl[] {param("this", voidPtr), param("componentName", charPtr)}),

            new Spec("0x0043dcc0", "CPhysicsComponentValue__dtor_base", "__fastcall", voidType,
                "Name/signature correction: base destructor body restores vtable 0x005daae8; type-10 leaf vtables use CPhysicsComponentValueLeaf__shared_scalar_deleting_dtor at 0x0043d5a0 before optional free. Exact source destructor identity and runtime lifetime behavior remain unproven.",
                tags("destructor", "value-base"),
                new String[] {"CPhysicsComponentValue__ctor_like_0043dcc0"},
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
        };

        int changed = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changed++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " :: " + ex.getMessage());
                if (!dryRun) {
                    throw ex;
                }
            }
        }

        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply")
            + " targets=" + specs.length
            + " changed_or_would_change=" + changed
            + " failed=" + failed);
        if (failed > 0) {
            throw new IllegalStateException("Failed specs: " + failed);
        }
    }
}
