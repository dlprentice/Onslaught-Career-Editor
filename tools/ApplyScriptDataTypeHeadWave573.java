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
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyScriptDataTypeHeadWave573 extends GhidraScript {
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
            "script-datatype-head-wave573",
            "retail-binary-evidence"
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
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0052d040",
                "CAsmInstruction__GetAttributeValue",
                "__stdcall",
                voidPtr,
                "Wave573 signature/comment hardening: stack-argument helper used by the OP_PUSH instruction handler to obtain an attribute value from an instruction record. RET 0x4 confirms one stack argument; the body calls the data object at instruction+0x08 through vtable slot +0x48 when present, otherwise reports the no-data-set fatal string and allocates an 8-byte zero-valued CIntDataType fallback. Static retail evidence only; exact instruction layout, exact data-type ownership, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__GetAttributeValue"},
                tags("mission-script", "asm-instruction", "bytecode-vm", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("instruction", voidPtr)
                }
            ),
            new Spec(
                "0x0052d0a0",
                "CIntDataType__Add",
                "__thiscall",
                voidPtr,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot arithmetic add. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30, adds this+0x04, allocates an 8-byte CIntDataType object, installs the CIntDataType vtable, and stores the summed integer. Static retail evidence only; exact CIntDataType layout, overflow semantics, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__Add"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d110",
                "CIntDataType__Subtract",
                "__thiscall",
                voidPtr,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot arithmetic subtract. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30, subtracts it from this+0x04, allocates an 8-byte CIntDataType object, installs the CIntDataType vtable, and stores the result. Static retail evidence only; exact CIntDataType layout, underflow semantics, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__Subtract"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d180",
                "CIntDataType__Multiply",
                "__thiscall",
                voidPtr,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot arithmetic multiply. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30, multiplies by this+0x04, allocates an 8-byte CIntDataType object, installs the CIntDataType vtable, and stores the product. Static retail evidence only; exact CIntDataType layout, overflow semantics, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__Multiply"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d1f0",
                "CIntDataType__Divide",
                "__thiscall",
                voidPtr,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot arithmetic divide. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30, divides this+0x04 by that rhs value, allocates an 8-byte CIntDataType object, installs the CIntDataType vtable, and stores the quotient. Static retail evidence only; exact CIntDataType layout, divide-by-zero behavior, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__Divide"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d260",
                "CIntDataType__Equals",
                "__thiscall",
                boolType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot equality compare. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and returns whether this+0x04 equals that integer value. Static retail evidence only; exact bool ABI, exact data-type layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__Equals"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "comparison", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d280",
                "CIntDataType__NotEquals",
                "__thiscall",
                boolType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot inequality compare. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and returns whether this+0x04 differs from that integer value. Static retail evidence only; exact bool ABI, exact data-type layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__NotEquals"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "comparison", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d2a0",
                "CIntDataType__Assign",
                "__thiscall",
                voidType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot assignment. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and stores the returned integer at this+0x04. Static retail evidence only; exact data-type layout, assignment ownership, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__Assign"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d2c0",
                "CIntDataType__LessThan",
                "__thiscall",
                boolType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot less-than compare. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and returns whether this+0x04 is less than that integer value. Static retail evidence only; exact bool ABI, exact data-type layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__LessThan"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "comparison", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d2e0",
                "CIntDataType__GreaterThan",
                "__thiscall",
                boolType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot greater-than compare. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and returns whether this+0x04 is greater than that integer value. Static retail evidence only; exact bool ABI, exact data-type layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__GreaterThan"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "comparison", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d300",
                "CIntDataType__LessOrEqual",
                "__thiscall",
                boolType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot less-or-equal compare. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and returns whether this+0x04 is less than or equal to that integer value. Static retail evidence only; exact bool ABI, exact data-type layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__LessOrEqual"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "comparison", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d320",
                "CIntDataType__GreaterOrEqual",
                "__thiscall",
                boolType,
                "Wave573 signature/comment hardening: CIntDataType vtable-slot greater-or-equal compare. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through vtable slot +0x30 and returns whether this+0x04 is greater than or equal to that integer value. Static retail evidence only; exact bool ABI, exact data-type layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CIntDataType__GreaterOrEqual"},
                tags("mission-script", "datatype", "int-datatype", "vtable-slot", "comparison", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("rhs", voidPtr)
                }
            ),
            new Spec(
                "0x0052d390",
                "CDataType__Destructor",
                "__thiscall",
                voidType,
                "Wave573 signature/comment hardening: CDataType base destructor reached from scalar-deleting destructor and unwind cleanup sites. ECX is this; the body only restores the base CDataType vtable pointer before returning. Static retail evidence only; exact inheritance layout, destructor ownership, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CDataType__Destructor"},
                tags("mission-script", "datatype", "destructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0052d3d0",
                "CAsmInstruction__SpawnFromOpcode",
                "__cdecl",
                voidPtr,
                "Wave573 signature/comment hardening: bytecode instruction factory called by CScriptObjectCode construction after reading an opcode. It reads a second dword attribute from the supplied bytecode reader, switches opcode values into 0x0c-byte instruction allocations with opcode-specific vtables and attribute storage, and reports a fatal unknown-instruction string before returning null for unsupported opcodes. Static retail evidence only; exact opcode enum, exact instruction object layout, source identity, runtime script behavior, and rebuild parity remain unproven.",
                new String[] {"CAsmInstruction__SpawnFromOpcode"},
                tags("mission-script", "asm-instruction", "opcode-factory", "bytecode-vm", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("opcode", intType),
                    param("bytecode_reader", voidPtr)
                }
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
            throw new IllegalStateException("Wave573 script/datatype head tranche failed");
        }
    }
}
