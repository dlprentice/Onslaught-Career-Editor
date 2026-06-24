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

public class ApplyPhysicsScriptStatementTranche2 extends GhidraScript {
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
        return new String[] {"static-reaudit", "physics-script-wave332", "physics-script", "statement-tranche", "retail-binary-evidence", extra};
    }

    private String[] tags2(String extra1, String extra2) {
        return new String[] {"static-reaudit", "physics-script-wave332", "physics-script", "statement-tranche", "retail-binary-evidence", extra1, extra2};
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
            new Spec("0x00430330", "CPhysicsRoundValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsRoundValueList node load helper reads a child statement type and serialized size, dispatches CreateStatementType5 load slot +0xc when present, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout, serialized format completeness, runtime physics behavior, and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsRoundValueList__ctor_like_00430330"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00430410", "CPhysicsRoundValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsRoundValueList nodes; it destroys child and next-node links through vtable slot 0, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsRoundValueList__VFunc_00_00430410"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430450", "CRoundStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CRoundStatement; it calls CRoundStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CRoundStatement__VFunc_00_00430450"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430470", "CRoundStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CRoundStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CRoundStatement__ctor_like_00430470"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004304d0", "CSpawnerStatement__CreateSpawnerAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CSpawnerStatement vtable slot +0x4 body creates/registers spawner data from the statement name, then propagates that context through child statement slot +0x4/list traversal. Exact statement layout, spawner data layout, runtime physics behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CSpawnerStatement__VFunc_01_004304d0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00430510", "CSpawnerData__CreateAndRegisterByName", "__cdecl", voidType,
                "Name/signature correction: creates a 0x3c spawner-data-like record by name, stores a copied name pointer, initializes default spawner fields including count/range-like constants, and appends the item to DAT_008553f4. Exact class layout, source identity, runtime spawner behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {"CSpawnerData__ctor_like_00430510"},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x00430610", "CSpawnerData__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for spawner-data-like records; it frees two owned pointer fields at +0x4 and +0x8, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CSpawnerData__VFunc_00_00430610"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430660", "CSpawnerStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/signature correction: recovered missing top-level CSpawnerStatement serialized-size body. It counts the statement name string, includes the first spawner value-list node payload size, and recursively adds chained value-list sizes. Exact serialized format completeness, concrete statement layout, and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004306b0", "CPhysicsSpawnerValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsSpawnerValueList serialized-size helper, not the top-level CSpawnerStatement size body. It starts with the node header size, adds child statement vtable slot +0x8 when present, and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CSpawnerStatement__GetSerializedSize"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004306e0", "CSpawnerStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/signature correction: recovered missing CSpawnerStatement load body. It reads the statement name from CDXMemBuffer, creates the first CPhysicsSpawnerValueList node, dispatches CreateStatementType6 load slot +0xc when available, skips unknown payload bytes otherwise, and handles recursive value-list loading. Exact file format, layout, and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00430800", "CPhysicsSpawnerValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsSpawnerValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType6 load slot +0xc when present, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsSpawnerValueList__ctor_like_00430800"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x004308e0", "CPhysicsSpawnerValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsSpawnerValueList nodes; it destroys child and next-node links, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsSpawnerValueList__VFunc_00_004308e0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430920", "CSpawnerStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CSpawnerStatement; it calls CSpawnerStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CSpawnerStatement__VFunc_00_00430920"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430940", "CSpawnerStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CSpawnerStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CSpawnerStatement__ctor_like_00430940"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004309a0", "CExplosionStatement__CreateExplosionAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CExplosionStatement vtable slot +0x4 body creates/registers explosion data from the statement name, then propagates that context through child statement slot +0x4/list traversal. Exact statement layout, explosion data layout, runtime physics behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CExplosionStatement__VFunc_01_004309a0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004309e0", "CExplosionStatement__Create", "__cdecl", voidType,
                "Signature/comment/tag hardening: creates a 0x50 explosion-like record by name, stores the copied name pointer at +0x30, initializes default scalar/vector fields and sentinel values, and appends it to DAT_008553f8. Exact class layout, source identity, runtime explosion behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {"CExplosionStatement__AllocObjectAndAddToSet"},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x00430ae0", "CExplosionStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/signature correction: recovered missing top-level CExplosionStatement serialized-size body. It counts the statement name string, includes the first explosion value-list node payload size, and recursively adds chained value-list sizes. Exact serialized format completeness, concrete statement layout, and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00430b30", "CPhysicsExplosionValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsExplosionValueList serialized-size helper, not a UnitAI recursive-node helper or top-level explosion statement size body. It adds child statement slot +0x8 size and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CUnitAI__ComputeRecursiveNodeSize_NodeTreeA"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00430b60", "CExplosionStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/signature correction: recovered missing CExplosionStatement load body. It reads the statement name from CDXMemBuffer, creates the first CPhysicsExplosionValueList node, dispatches CreateStatementType7 load slot +0xc when available, skips unknown payload bytes otherwise, and handles recursive value-list loading. Exact file format, layout, and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00430c80", "CPhysicsExplosionValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsExplosionValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType7 load slot +0xc when present, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsExplosionValueList__ctor_like_00430c80"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00430d60", "CPhysicsExplosionValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsExplosionValueList nodes; it destroys child and next-node links, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsExplosionValueList__VFunc_00_00430d60"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430da0", "CExplosionStatement__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CExplosionStatement; it calls CExplosionStatement__dtor, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class hierarchy and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CExplosionStatement__VFunc_00_00430da0"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00430dc0", "CExplosionStatement__dtor", "__fastcall", voidType,
                "Name/signature correction: CExplosionStatement destructor body sets the derived vtable, deletes the child pointer at +0x10c through vtable slot 0 when present, then restores the CPhysicsScriptStatement base vtable. Exact layout and runtime lifetime behavior remain unproven.",
                tags("destructor"),
                new String[] {"CExplosionStatement__ctor_like_00430dc0"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00430e20", "CComponentStatement__CreateComponentAndRecurse", "__fastcall", voidType,
                "Name/signature correction: CComponentStatement vtable slot +0x4 body creates/registers component data from the statement name, then propagates that context through child statement slot +0x4/list traversal. Exact statement layout, component data layout, runtime physics behavior, and rebuild parity remain unproven.",
                tags("statement-update"),
                new String[] {"CComponentStatement__VFunc_01_00430e20"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00430e60", "CComponentStatement__CreateAndRegisterByName", "__cdecl", voidType,
                "Name/signature correction: creates a 0x1ac component-data-like record by name, initializes several pointer sets and UnitAI-style default fields, applies the Fenrir/Fenrir Main Gun special-case flag, and appends it to DAT_00855400. Exact class layout, source identity, runtime component behavior, and rebuild parity remain unproven.",
                tags("physics-object-registry"),
                new String[] {"CComponentStatement__AllocObjectAndAddToSet"},
                new ParameterImpl[] {param("name", charPtr)}),
            new Spec("0x00430fa0", "CStatementChain__InvokeVFunc04OnNodes", "__thiscall", voidType,
                "Signature/comment/tag hardening: walks chained value-list nodes, calls child statement vtable slot +0x4 with the supplied context when a child is present, then advances through next-node pointers. Exact node layout, statement subtype ownership, runtime behavior, and rebuild parity remain unproven.",
                tags("statement-chain"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("context", voidPtr)}),
            new Spec("0x00430fd0", "CComponentStatement__GetSerializedSize", "__fastcall", intType,
                "Boundary/signature correction: recovered missing top-level CComponentStatement serialized-size body. It counts the statement name string, includes the first component value-list node payload size, and recursively adds chained value-list sizes. Exact serialized format completeness, concrete statement layout, and rebuild parity remain unproven.",
                tags2("statement-boundary", "serialized-size"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431020", "CPhysicsComponentValueList__GetSerializedSize", "__fastcall", intType,
                "Name/signature correction: recursive CPhysicsComponentValueList serialized-size helper, not the top-level CComponentStatement size body. It adds child statement slot +0x8 size and recurses through next value-list nodes. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "serialized-size"),
                new String[] {"CComponentStatement__GetSerializedSize"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00431050", "CComponentStatement__LoadFromMemBuffer", "__thiscall", voidType,
                "Boundary/signature correction: recovered missing CComponentStatement load body. It reads the statement name from CDXMemBuffer, creates the first CPhysicsComponentValueList node, dispatches CreateStatementType10 load slot +0xc when available, skips unknown payload bytes otherwise, and handles recursive value-list loading. Exact file format, layout, and runtime behavior remain unproven.",
                tags2("statement-boundary", "statement-load"),
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00431170", "CPhysicsComponentValueList__LoadFromMemBuffer", "__thiscall", voidType,
                "Name/signature correction: CPhysicsComponentValueList node load helper reads child statement type and serialized size, dispatches CreateStatementType10 load slot +0xc when present, skips unknown payload bytes otherwise, and recursively loads the next node when the terminator permits. Exact node layout and rebuild parity remain unproven.",
                tags2("value-list", "statement-load"),
                new String[] {"CPhysicsComponentValueList__ctor_like_00431170"},
                new ParameterImpl[] {param("this", voidPtr), param("memBuffer", voidPtr)}),
            new Spec("0x00431250", "CPhysicsComponentValueList__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper for CPhysicsComponentValueList nodes; it destroys child and next-node links, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. Exact class layout and runtime lifetime behavior remain unproven.",
                tags2("value-list", "destructor"),
                new String[] {"CPhysicsComponentValueList__VFunc_00_00431250"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
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

        println("ApplyPhysicsScriptStatementTranche2 complete: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + (dryRun ? 0 : specs.length - bad) +
            " skipped=" + skipped +
            " renamed=" + renamed +
            " missing=0 bad=" + bad);
        if (bad != 0) {
            throw new IllegalStateException("Bad specs encountered: " + bad);
        }
    }
}
