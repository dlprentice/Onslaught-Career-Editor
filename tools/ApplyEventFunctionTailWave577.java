//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyEventFunctionTailWave577 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int missing = 0;
        int bad = 0;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "eventfunction-tail-wave577",
            "retail-binary-evidence",
            "mission-script",
            "event-function",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] thisOnly(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr)
        };
    }

    private ParameterImpl[] scalarDeletingParams(DataType voidPtr, DataType byteType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("flags", byteType)
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0052f9a0",
                "CEventFunction__Destructor",
                "__thiscall",
                voidType,
                "Wave577 signature/comment hardening: CEventFunction destructor body entered with ECX=this and no stack cleanup. It installs CEventFunction vtable 0x005e4ef8, iterates the parameter CSPtrSet at this+0x0c through iterator slot this+0x14, clears and frees each 8-byte wrapper through DAT_009c3df0, clears the same CSPtrSet twice, then calls CMonitor__Shutdown on this. Static retail evidence only; exact CEventFunction layout names, why the set is cleared twice, source identity, runtime event behavior, and rebuild parity remain unproven.",
                new String[] {"CEventFunction__Destructor"},
                tags("destructor", "parameter-list-cleanup", "monitor-cleanup"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x0052fa50",
                "CEventFunction__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave577 signature/comment hardening: CEventFunction scalar-deleting destructor is the vtable slot at 0x005e4efc. RET 0x4 confirms one flags argument after ECX=this; the wrapper calls CEventFunction__Destructor and frees this through DAT_009c3df0 when flags&1 is set, then returns this. Static retail evidence only; exact MSVC deleting-destructor ABI details, allocator ownership, runtime event behavior, and rebuild parity remain unproven.",
                new String[] {"CEventFunction__ScalarDeletingDestructor"},
                tags("destructor", "scalar-deleting-destructor", "vtable-slot"),
                scalarDeletingParams(voidPtr, byteType)
            ),
            new Spec(
                "0x0052fa70",
                "CEventFunction__CEventFunction",
                "__thiscall",
                voidPtr,
                "Wave577 signature/comment hardening: CEventFunction constructor has RET 0x8, with ECX=this plus script_object_code and bytecode_reader stack arguments. It initializes the base/list state, switches from the CRelaxedSquad-like vtable 0x005d92d4 to CEventFunction vtable 0x005e4ef8, stores script_object_code at this+0x1c, reads the event id into this+0x08 and a parameter count from bytecode_reader, resolves each symbol-table index through CScriptObjectCode__GetInstruction, requires datatype id 3, and appends 8-byte wrappers allocated at EventFunction.cpp line 0x40. Static retail evidence only; exact source class hierarchy, concrete symbol/data layouts, runtime event behavior, and rebuild parity remain unproven.",
                new String[] {"CEventFunction__CEventFunction"},
                tags("constructor", "bytecode-read", "symbol-table", "parameter-list"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("script_object_code", voidPtr),
                    param("bytecode_reader", voidPtr)
                }
            ),
            new Spec(
                "0x0052fbb0",
                "CEventFunction__Clone",
                "__thiscall",
                voidPtr,
                "Wave577 signature/comment hardening: CEventFunction clone has RET 0x4, with ECX=this plus cloned_script_object_code. It allocates a 0x20-byte event function at EventFunction.cpp line 0x4e, copies the event id, initializes the parameter list, stores cloned_script_object_code at +0x1c, then walks the source parameter list, searches the source script symbol table at owner+0x58 through CScriptObjectCode__GetInstruction, verifies datatype id 3, compares string getter slot +0x38 results, and appends line-0x1b wrapper nodes to the clone. Static retail evidence only; exact symbol-table schema, clone ownership, string collation details, runtime event behavior, and rebuild parity remain unproven.",
                new String[] {"CEventFunction__Clone"},
                tags("clone", "symbol-table", "string-match", "parameter-list"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("cloned_script_object_code", voidPtr)
                }
            ),
            new Spec(
                "0x0052fda0",
                "CEventFunction__Execute",
                "__thiscall",
                voidType,
                "Wave577 signature/comment hardening: CEventFunction execute has ECX=this and no stack cleanup. It walks the parameter list at this+0x0c, allocates 8-byte CEventFunctionParam wrappers at EventFunction.cpp line 0x96 with vtable 0x005e4d50, copies the byte at wrapped_object+0x04+0x14 into the wrapper payload, stores up to the observed local 10-slot array, and calls CScriptObjectCode__CallEventDirect with owner this+0x1c, event id this+0x08, parameter array, and count. Static retail evidence only; exact payload semantics, parameter count safety, runtime event dispatch behavior, and rebuild parity remain unproven.",
                new String[] {"CEventFunction__Execute"},
                tags("execute", "event-dispatch", "parameter-wrapper"),
                thisOnly(voidPtr)
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave577 event-function tail tranche failed");
        }
    }
}
