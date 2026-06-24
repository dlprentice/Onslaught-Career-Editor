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

public class ApplyPhysicsScriptStatementTranche extends GhidraScript {
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

    private String[] tags(String extra) {
        return new String[] {"static-reaudit", "physics-script-wave331", "physics-script", "statement-tranche", "retail-binary-evidence", extra};
    }

    private String[] tags2(String extra1, String extra2) {
        return new String[] {"static-reaudit", "physics-script-wave331", "physics-script", "statement-tranche", "retail-binary-evidence", extra1, extra2};
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
            new Spec("0x0042ede0", "CUnitStatement__CreateUnitAndRecurse", "__fastcall", voidType,
                "Boundary/name/signature correction: recovered missing CUnitStatement vtable slot +0x4 body. It creates/registers UnitAI by the statement name, resolves the created UnitAI from DAT_008553fc by name, then propagates that context through child statement slot +0x4/list traversal. Exact statement layout, UnitAI layout, runtime physics behavior, and rebuild parity remain unproven.",
                tags2("statement-boundary", "statement-update"),
                new String[] {"FUN_0042ede0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042ee90", "CUnitAI__CreateAndRegisterByName", "__cdecl", voidType,
                "Signature/comment/tag hardening: allocates a 0x1ac UnitAI-like record, initializes several pointer sets, copies the name at +0xb0, applies CUnitAI__InitDefaults, marks Fenrir/Fenrir Main Gun context at +0x1a4, and adds the item to DAT_008553fc. Exact class layout, source identity, runtime physics behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x0042efd0", "CUnitAI__InitDefaults", "__fastcall", voidType,
                "Signature/comment/tag hardening: initializes UnitAI-like default physics/configuration fields, including the m_b_rubble effect string, several pointer/list fields, integer defaults, angle/timing float constants, and sentinel values through +0x1a8. Exact class layout, source identity, runtime defaults, and rebuild parity remain unproven.",
                tags("unitai-defaults"),
                new String[] {},
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x0042f230", "CUnitStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/name/signature correction: recovered missing top-level CUnitStatement serialized-size body. It counts the statement name string, includes the first value-list node payload size, and recursively adds chained value-list sizes. Exact serialized format completeness, concrete statement layout, and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {"FUN_0042f230"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f280", "CPhysicsUnitValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsUnitValueList serialized-size helper, not a UnitAI recursive-node helper. It starts with the node header size, adds child statement vtable slot +0x8 when present, and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CUnitAI__ComputeRecursiveNodeSize_Base8"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f2b0", "CUnitStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/name/signature correction: recovered missing CUnitStatement load body. It reads the name from CDXMemBuffer, creates the first CPhysicsUnitValueList node, dispatches CreateStatementType2 children or skips unknown serialized payload bytes, and reads the chain terminator before optional recursion. Exact file format, layout, and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {"FUN_0042f2b0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x0042f3d0", "CPhysicsUnitValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsUnitValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType2 load slot +0xc when available, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsUnitValueList__ctor_like_0042f3d0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x0042f4b0", "CPhysicsUnitValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsUnitValueList nodes; it destroys child and next-node links, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsUnitValueList__VFunc_00_0042f4b0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042f4f0", "CUnitStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CUnitStatement; it calls CUnitStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitStatement__VFunc_00_0042f4f0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042f510", "CUnitStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CUnitStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CUnitStatement__ctor_like_0042f510"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f570", "CPhysicsScriptStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CPhysicsScriptStatement base destructor body observed from unwind references; it restores the base statement vtable at 0x005d9894. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CPhysicsScriptStatement__ctor_like_0042f570"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f580", "CPhysicsScriptStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Boundary/name/signature correction: recovered missing CPhysicsScriptStatement scalar-deleting destructor wrapper. It restores the base vtable, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags2("statement-boundary", "destructor"),
                new String[] {"FUN_0042f580"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042f5b0", "CWeaponStatement__CreateWeaponAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CWeaponStatement vtable slot +0x4 body creates/registers a weapon by the statement name, then propagates the generated context through child statement slot +0x4/list traversal. Exact statement layout, weapon registry layout, runtime behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CWeaponStatement__VFunc_01_0042f5b0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f5f0", "CWeaponStatement__Create", "__cdecl", voidType,
                "Signature/comment/tag hardening: creates a 0x4c weapon-like record by name, applies default scalar fields and sentinel values, then adds it to DAT_008553e8. Exact class layout, source identity, runtime weapon behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x0042f700", "CWeaponStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/name/signature correction: recovered missing top-level CWeaponStatement serialized-size body. It counts the statement name string, includes weapon value-list child payload size, and recursively adds chained value-list sizes. Exact serialized format completeness and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {"FUN_0042f700"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f750", "CPhysicsWeaponValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsWeaponValueList serialized-size helper, not the top-level CWeaponStatement size body. It adds child statement slot +0x8 size and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CWeaponStatement__GetSerializedSize"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042f780", "CWeaponStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/name/signature correction: recovered missing CWeaponStatement load body. It reads the name from CDXMemBuffer, creates the first CPhysicsWeaponValueList node, dispatches CreateStatementType3 children or skips unknown serialized payload bytes, and handles recursive value-list loading. Exact file format and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {"FUN_0042f780"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x0042f8a0", "CPhysicsWeaponValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsWeaponValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType3 load slot +0xc when available, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsWeaponValueList__ctor_like_0042f8a0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x0042f980", "CPhysicsWeaponValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsWeaponValueList nodes; it destroys child and next-node links, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsWeaponValueList__VFunc_00_0042f980"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042f9c0", "CWeaponStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CWeaponStatement; it calls CWeaponStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CWeaponStatement__VFunc_00_0042f9c0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042f9e0", "CWeaponStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CWeaponStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CWeaponStatement__ctor_like_0042f9e0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042fa40", "CWeaponModeStatement__CreateWeaponModeAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CWeaponModeStatement vtable slot +0x4 body creates/registers a weapon mode by the statement name, then propagates the generated context through child statement slot +0x4/list traversal. Exact statement layout, weapon-mode registry layout, runtime behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CWeaponModeStatement__VFunc_01_0042fa40"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042fa80", "CWeaponModeStatement__Create", "__cdecl", voidType,
                "Signature/comment/tag hardening: creates a 0xc0 weapon-mode-like record by name, initializes pointer sets and default scalar fields, then adds it to DAT_008553ec. Exact class layout, source identity, runtime weapon-mode behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x0042fc20", "CWeaponModeStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/name/signature correction: recovered missing top-level CWeaponModeStatement serialized-size body. It counts the statement name string, includes weapon-mode value-list child payload size, and recursively adds chained value-list sizes. Exact serialized format completeness and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {"FUN_0042fc20"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042fc70", "CPhysicsWeaponModeValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsWeaponModeValueList serialized-size helper, not the top-level CWeaponModeStatement size body. It adds child statement slot +0x8 size and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CWeaponModeStatement__GetSerializedSize"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042fca0", "CWeaponModeStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/name/signature correction: recovered missing CWeaponModeStatement load body. It reads the name from CDXMemBuffer, creates the first CPhysicsWeaponModeValueList node, dispatches CreateStatementType4 children or skips unknown serialized payload bytes, and handles recursive value-list loading. Exact file format and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {"FUN_0042fca0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x0042fdc0", "CPhysicsWeaponModeValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsWeaponModeValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType4 load slot +0xc when available, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsWeaponModeValueList__ctor_like_0042fdc0"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x0042fea0", "CPhysicsWeaponModeValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsWeaponModeValueList nodes; it destroys child and next-node links, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsWeaponModeValueList__VFunc_00_0042fea0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042fee0", "CWeaponModeStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CWeaponModeStatement; it calls CWeaponModeStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CWeaponModeStatement__VFunc_00_0042fee0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x0042ff00", "CWeaponModeStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CWeaponModeStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CWeaponModeStatement__ctor_like_0042ff00"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042ff60", "CRoundStatement__CreateRoundAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CRoundStatement vtable slot +0x4 body creates/registers a round by the statement name, then propagates the generated context through child statement slot +0x4/list traversal. Exact statement layout, round registry layout, runtime behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CRoundStatement__VFunc_01_0042ff60"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0042ffa0", "CRoundStatement__Create", "__cdecl", voidType,
                "Signature/comment/tag hardening: creates a 0xa8 round-like record by name, sets Stream_Laser and Gill_M_Breath special-case flags, initializes default scalar fields, then adds it to DAT_008553f0. Exact class layout, source identity, runtime projectile behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x00430190", "CRoundStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/name/signature correction: recovered missing top-level CRoundStatement serialized-size body. It counts the statement name string, includes round value-list child payload size, and recursively adds chained value-list sizes. Exact serialized format completeness and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {"FUN_00430190"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004301e0", "CPhysicsRoundValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsRoundValueList serialized-size helper, not the top-level CRoundStatement size body. It adds child statement slot +0x8 size, includes per-node overhead, and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CRoundStatement__GetSerializedSize"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00430210", "CRoundStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/name/signature correction: recovered missing CRoundStatement load body. It reads the name from CDXMemBuffer, creates the first CPhysicsRoundValueList node, dispatches CreateStatementType5 children or skips unknown serialized payload bytes, and handles recursive value-list loading. Exact file format and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {"FUN_00430210"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int missing = 0;
        int bad = 0;
        for (Spec spec : specs) {
            try {
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
            } catch (IllegalStateException ex) {
                if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                    missing++;
                } else {
                    bad++;
                }
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            } catch (Exception ex) {
                bad++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
            }
        }

        println("SUMMARY: updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=" + missing + " bad=" + bad);
        if (missing != 0 || bad != 0) {
            throw new IllegalStateException("PhysicsScript statement tranche failed: missing=" + missing + " bad=" + bad);
        }
    }
}
