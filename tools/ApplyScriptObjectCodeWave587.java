//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyScriptObjectCodeWave587 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
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
            "scriptobjectcode-wave587",
            "retail-binary-evidence",
            "mission-script",
            "script-object-code",
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00538ea0",
                "CScriptObjectCode__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", byteType) },
                "Wave587 signature/comment hardening: MSVC scalar deleting destructor wrapper for CScriptObjectCode. RET 0x4 confirms the delete_flags stack argument; the body calls CScriptObjectCode__Destructor and frees this through CDXMemoryManager__Free when delete_flags bit 0 is set. A data xref at 0x005e4f54 supports this function as the first observed CScriptObjectCode destructor/vtable slot, but the surrounding table bytes are not a proven full vtable boundary. Static retail evidence only; exact class layout, allocation owner, runtime mission-script behavior, BEA patching, source parity, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__scalar_deleting_dtor"},
                tags("destructor", "scalar-deleting-destructor", "ret-4", "vtable-slot")
            ),
            new Spec(
                "0x00538ec0",
                "CScriptObjectCode__CScriptObjectCode",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("bytecode_reader", voidPtr) },
                "Wave587 signature/comment hardening: CScriptObjectCode constructor reached from CWorld__LoadScriptEvents. RET 0x4 confirms one explicit bytecode_reader argument after ECX; the body reads the instruction count, creates instruction objects with CAsmInstruction__SpawnFromOpcode, reads 13 dwords per instruction, allocates the symbol table at the ScriptObjectCode.cpp line-0x39 site, calls CScriptObjectCode__ReadSymbolTable, then reads event-function count and allocates CEventFunction records at the line-0x43 site. Static retail evidence only; exact bytecode format, object layout, source parity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__CScriptObjectCode"},
                tags("constructor", "ret-4", "world-load-script-events", "bytecode-reader")
            ),
            new Spec(
                "0x00539040",
                "CScriptObjectCode__Clone",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("script_object_code", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only clone helper called by CWorld__CloneScriptObjectCodeByName. The body allocates a 0x70-byte CScriptObjectCode-like object, clones instruction entries through each instruction vtable slot +0x04, calls CScriptObjectCode__CloneSymbolTable, clones event functions with CEventFunction__Clone, and copies selected state fields. Static retail evidence only; exact layout, ownership, source parity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__Clone"},
                tags("clone", "ecx-only", "world-clone-script-object-code")
            ),
            new Spec(
                "0x005391a0",
                "CScriptObjectCode__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("script_object_code", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only destructor body called by the scalar deleting destructor. The body frees instruction pointers, event functions, the event set/flex array, and the symbol table through CScriptObjectCode__ClearSymbolTable before releasing table storage. Static retail evidence only; exact ownership ordering, source parity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__Destructor"},
                tags("destructor", "ecx-only", "symbol-table")
            ),
            new Spec(
                "0x005392a0",
                "CScriptObjectCode__CollectSpawnThings",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("script_object_code", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only helper called by CWorld__LoadWorld. The routine scans the script instruction array for opcode 0x18 / SpawnThing-style instructions, resolves referenced instruction/name data through CScriptObjectCode__GetInstruction, and adds names to CWorldMeshList__Add. Static retail evidence only; exact opcode semantics, source parity, runtime spawn behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__CollectSpawnThings"},
                tags("spawn-thing-scan", "world-load", "ecx-only")
            ),
            new Spec(
                "0x00539350",
                "CScriptObjectCode__RestoreStack",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("saved_stack", voidPtr) },
                "Wave587 signature/comment hardening: stack restore helper used by CScriptObjectCode__CopyState. RET 0x4 confirms one explicit saved_stack argument after ECX; the body clears the current stack, copies saved entries from saved_stack, zeros the saved stack count at saved_stack+0x200, and returns the destination stack. Static retail evidence only; exact stack owner/layout, source parity, runtime resume behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__RestoreStack"},
                tags("stack-restore", "ret-4", "copy-state")
            ),
            new Spec(
                "0x005393e0",
                "CScriptObjectCode__ClearStack",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("stack", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only stack cleanup helper called by CScriptObjectCode__Reset and CVM__Destructor. The body iterates non-null stack entries, destructs each entry through its vtable, and decrements the count at stack+0x200 to zero. Static retail evidence only; exact stack value type, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__ClearStack"},
                tags("stack-cleanup", "ecx-only", "vm-stack")
            ),
            new Spec(
                "0x00539420",
                "CScriptObjectCode__Push",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("value", voidPtr) },
                "Wave587 signature/comment hardening: VM stack push helper used by script opcode handlers and event-call setup. RET 0x4 confirms one explicit value argument after ECX; the body stores value at stack + count*4, increments stack+0x200, and emits the stack-out-of-memory fatal diagnostic before backing off if the count exceeds 128. Static retail evidence only; exact stack layout, value ownership, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__Push"},
                tags("stack-push", "ret-4", "vm-stack")
            ),
            new Spec(
                "0x00539470",
                "CScriptObjectCode__Pop",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("stack", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only VM stack pop helper used by arithmetic, comparison, jump, and call instruction handlers. The body prints the pop-empty fatal diagnostic and returns null on underflow; otherwise it decrements stack+0x200 and returns the removed top value. Static retail evidence only; exact value type, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__Pop"},
                tags("stack-pop", "ecx-only", "vm-stack")
            ),
            new Spec(
                "0x005394a0",
                "CScriptObjectCode__RemoveTop",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("stack", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only VM stack remove-top helper used by CScriptObjectCode__Run and nearby opcode handlers. The body prints the remove-top-empty fatal diagnostic on underflow; otherwise it decrements stack+0x200 and destructs the removed top value when non-null. Static retail evidence only; exact value type, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__RemoveTop"},
                tags("stack-remove-top", "ecx-only", "vm-stack")
            ),
            new Spec(
                "0x005394e0",
                "CScriptObjectCode__GetTop",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("offset_from_top", intType) },
                "Wave587 signature/comment hardening: VM stack peek helper used by compare-style instruction handlers. RET 0x4 confirms one explicit offset_from_top argument after ECX; the body computes the target index from stack+0x200, prints the invalid-stack-item fatal diagnostic on invalid offsets, and returns the selected value pointer otherwise. Static retail evidence only; exact stack value type, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__GetTop"},
                tags("stack-peek", "ret-4", "vm-stack")
            ),
            new Spec(
                "0x00539510",
                "CScriptObjectCode__ClearSymbolTable",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("symbol_table", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only symbol-table cleanup helper. The body iterates symbol entries, destructs nested datatype/value storage at +0x08, runs CStringDataType__Destructor on symbol names, frees each entry, clears the table pointers, and releases the flex-array storage. Static retail evidence only; exact symbol entry layout, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__ClearSymbolTable"},
                tags("symbol-table", "symbol-table-cleanup", "ecx-only")
            ),
            new Spec(
                "0x005395b0",
                "CScriptObjectCode__CloneSymbolTable",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("symbol_table", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only symbol-table clone helper used by CScriptObjectCode__Clone. The body allocates a 0x14-byte table, clones CStringDataType names and nested datatypes through vtable slot +0x48, preserves observed flags/index fields, and de-duplicates names while appending entries. Static retail evidence only; exact symbol entry layout, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__CloneSymbolTable"},
                tags("symbol-table", "symbol-table-clone", "ecx-only")
            ),
            new Spec(
                "0x00539760",
                "CScriptObjectCode__GetInstruction",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("instruction_index", intType) },
                "Wave587 signature/comment hardening: instruction-array accessor used by CEventFunction and CScriptObjectCode helpers. RET 0x4 confirms one explicit instruction_index argument after ECX; the tiny body returns the pointer at instruction_array data + instruction_index*4. Despite the current function name, ECX is only proven as the instruction array/flex-array pointer here, not a full CScriptObjectCode instance. Static retail evidence only; exact array owner/layout, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__GetInstruction"},
                tags("instruction-array", "ret-4", "accessor")
            ),
            new Spec(
                "0x00539770",
                "CScriptObjectCode__ReadSymbolTable",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("bytecode_reader", voidPtr) },
                "Wave587 signature/comment hardening: symbol-table reader called by the CScriptObjectCode constructor. RET 0x4 confirms one explicit bytecode_reader argument after ECX; the body initializes a CFlexArray, reads the symbol count, allocates 0x18-byte CStringDataType-derived symbol entries, reads names from the bytecode buffer, optionally creates nested datatypes with CDataType__CreateFromType, reads three dwords per entry, and finally reads the table field at +0x10. Static retail evidence only; exact bytecode schema, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__ReadSymbolTable"},
                tags("symbol-table", "bytecode-reader", "ret-4")
            ),
            new Spec(
                "0x005398d0",
                "CScriptObjectCode__InitRuntime",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("runtime_state", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only runtime-state initializer. The body installs the observed no-op/cleanup vtable-region pointer 0x005e4f1c, zeros stack count and current script/IP/run-state fields, and clears related runtime pointers/flags. Static retail evidence only; exact runtime-state layout, full vtable boundary, source parity, runtime VM behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__InitRuntime"},
                tags("runtime-state", "initializer", "ecx-only")
            ),
            new Spec(
                "0x00539910",
                "CScriptObjectCode__CopyState",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("source_state", voidPtr) },
                "Wave587 signature/comment hardening: runtime state copy helper used by IScript restore and CScriptEventNB handlers. RET 0x4 confirms one explicit source_state argument after ECX; the body copies selected state fields from source_state, restores the stack through CScriptObjectCode__RestoreStack, clears the running flag, and returns this. Static retail evidence only; exact runtime-state layout, source parity, runtime resume behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__CopyState"},
                tags("runtime-state", "copy-state", "ret-4")
            ),
            new Spec(
                "0x00539980",
                "CScriptObjectCode__Reset",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("stack", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only reset wrapper called by game, IScript, and CScriptEventNB paths. The routine forwards to CScriptObjectCode__ClearStack for the supplied stack/runtime-state stack field. Static retail evidence only; exact owner layout, source parity, runtime reset behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__Reset"},
                tags("runtime-state", "stack-cleanup", "ecx-only")
            ),
            new Spec(
                "0x00539990",
                "CScriptObjectCode__CallEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("script_object_code", voidPtr), param("event_index", intType), param("params", voidPtrPtr), param("param_count", intType) },
                "Wave587 signature/comment hardening: runtime event-call helper reached from IScript and CScriptEventNB call sites. RET 0x10 confirms four explicit stack arguments after ECX; the body requires an empty stack, stores the active script object, initializes by running from instruction 0 when needed, looks up the event instruction pointer from script_object_code+0x14+event_index*4, destroys params when the event IP is -1, otherwise pushes params and runs the VM. Static retail evidence only; exact event table layout, source parity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__CallEvent"},
                tags("runtime-state", "event-call", "ret-10", "vm-run")
            ),
            new Spec(
                "0x00539a60",
                "CScriptObjectCode__CallEventDirect",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("script_object_code", voidPtr), param("instruction_index", intType), param("params", voidPtrPtr), param("param_count", intType) },
                "Wave587 signature/comment hardening: direct event-call helper reached from CEventFunction__Execute. RET 0x10 confirms four explicit stack arguments after ECX; the body initializes by running from instruction 0 when needed, pushes params, sets the instruction pointer to instruction_index, and runs the VM. Static retail evidence only; exact event-function parameter ownership, source parity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__CallEventDirect"},
                tags("runtime-state", "event-call-direct", "ret-10", "vm-run")
            ),
            new Spec(
                "0x00539ae0",
                "CScriptObjectCode__GotoInstruction",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("instruction_index", intType) },
                "Wave587 signature/comment hardening: runtime jump helper used by IScript restore and CScriptEventNB paths. RET 0x4 confirms one explicit instruction_index argument after ECX; the body sets the runtime instruction pointer and calls CScriptObjectCode__Run. Static retail evidence only; exact runtime-state layout, source parity, runtime resume behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__GotoInstruction"},
                tags("runtime-state", "goto-instruction", "ret-4", "vm-run")
            ),
            new Spec(
                "0x00539b00",
                "CScriptObjectCode__Run",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("runtime_state", voidPtr) },
                "Wave587 signature/comment hardening: ECX-only VM run loop called by event-call and goto helpers. The body blocks recursive runs, sets the running flag, loops instructions until opcode 0x17/end with call-depth <= 0 or abort, invokes each instruction vtable slot 0 with the observed runtime/stack/context arguments, logs through DebugTrace when enabled, enforces the 10000-instruction limit, verifies final stack size, and removes remaining stack entries. Static retail evidence only; exact VM semantics, source parity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptObjectCode__Run"},
                tags("runtime-state", "vm-run", "instruction-dispatch", "ecx-only")
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
        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave587 apply encountered missing/bad rows");
        }
    }
}
