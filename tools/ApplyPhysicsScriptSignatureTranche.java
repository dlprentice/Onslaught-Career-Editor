//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyPhysicsScriptSignatureTranche extends GhidraScript {
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

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrThrow(spec.address);
            if (!fn.getName().equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
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
            stats.updated++;
            Thread.sleep(50);
        } catch (IllegalStateException ex) {
            if (ex.getMessage() != null && ex.getMessage().startsWith("Function not found")) {
                stats.missing++;
            } else {
                stats.bad++;
            }
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
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

        String[] lifecycleTags = new String[] {"static-reaudit", "physics-script-wave330", "physics-script", "signature-hardened", "retail-binary-evidence", "manager-lifecycle"};
        String[] loadTags = new String[] {"static-reaudit", "physics-script-wave330", "physics-script", "signature-hardened", "retail-binary-evidence", "physics-script-load"};
        String[] updateTags = new String[] {"static-reaudit", "physics-script-wave330", "physics-script", "signature-hardened", "retail-binary-evidence", "physics-script-update"};
        String[] factoryTags = new String[] {"static-reaudit", "physics-script-wave330", "physics-script", "signature-hardened", "retail-binary-evidence", "statement-factory"};

        Spec[] specs = new Spec[] {
            new Spec("0x0042e880", "CPhysicsScript__Create", "__cdecl", voidType,
                "Signature/comment/tag hardening: retail CPhysicsScript manager singleton create path allocates 0x10 bytes with object type 0x18, initializes the CSPtrSet/list fields, stores g_pPhysicsScript, and clears the global on allocation failure. Exact source body identity, concrete class layout, runtime physics-script behavior, and rebuild parity remain unproven.",
                lifecycleTags, new ParameterImpl[] {}),
            new Spec("0x0042e8f0", "CPhysicsScript__Destroy", "__cdecl", voidType,
                "Signature/comment/tag hardening: retail CPhysicsScript manager destroy path iterates the statement list, removes each node, calls vtable slot 0 with delete flag 1, clears the set, calls OID__FreeObject on the manager, and nulls g_pPhysicsScript. Concrete list layout, lifetime semantics, runtime behavior, and rebuild parity remain unproven.",
                lifecycleTags, new ParameterImpl[] {}),
            new Spec("0x0042e950", "CPhysicsScript__Load", "__cdecl", boolType,
                "Signature/comment/tag hardening: retail CPhysicsScript load path destroys/recreates the singleton, reads the 0x12 header from memBuffer, loops statement type ids until -1, calls CreateStatement, dispatches statement load slot +0xc when created, and skips bytes when the factory returns null. Exact file-format completeness, statement layouts, runtime behavior, and rebuild parity remain unproven.",
                loadTags, new ParameterImpl[] {param("memBuffer", voidPtr)}),
            new Spec("0x0042ea60", "CPhysicsScript__Update", "__cdecl", voidType,
                "Signature/comment/tag hardening: retail CPhysicsScript update path iterates the g_pPhysicsScript statement list and calls vtable slot +0x4 for each statement. Null-singleton caller contract, concrete list layout, runtime physics behavior, and rebuild parity remain unproven.",
                updateTags, new ParameterImpl[] {}),
            new Spec("0x0042eb90", "CPhysicsScript__CreateStatement", "__cdecl", voidPtr,
                "Signature/comment/tag hardening: retail CPhysicsScript statement factory handles statementType 1..9, allocates 0x110-byte statement objects with object type ids 0x11..0x19, installs statement-specific vtables, initializes common fields, and returns null outside the known range. Exact statement subtype names, layouts, runtime behavior, and rebuild parity remain unproven.",
                factoryTags, new ParameterImpl[] {param("statementType", intType)}),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated + " skipped=" + stats.skipped + " renamed=0 missing=" + stats.missing + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("PhysicsScript signature tranche failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
