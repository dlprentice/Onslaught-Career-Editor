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

public class ApplyDataTypeFactoryFloatHeadWave575 extends GhidraScript {
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
            "datatype-factory-float-head-wave575",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String[] datatypeTags(String... extras) {
        String[] base = new String[] {
            "mission-script",
            "datatype",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[base.length + extras.length];
        System.arraycopy(base, 0, result, 0, base.length);
        System.arraycopy(extras, 0, result, base.length, extras.length);
        return tags(result);
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

    private ParameterImpl[] unaryDatatypeParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("rhs", voidPtr)
        };
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
                "0x0052ec60",
                "CDataType__CreateFromType",
                "__cdecl",
                voidPtr,
                "Wave575 signature/comment hardening: datatype factory called from CScriptObjectCode__ReadSymbolTable. It switches on serialized type_id 1..6, allocates an object, installs the observed vtable, and reads the initial payload from bytecode_reader: type 1 -> CIntDataType vtable 0x005e4af8, type 2 -> CFloatDataType vtable 0x005e4ea4, type 3 -> CStringDataType vtable 0x005e4e4c plus heap string copy, type 4 -> observed CBoolDataType vtable region 0x005e4d50, type 5 -> CThingPtrDataType vtable 0x005e4df8, and type 6 -> CPositionDataType vtable 0x005e4da4. Unknown type ids report the fatal unknown-data-type string and return null. Static retail evidence only; exact type enum names, allocator ownership, concrete layouts beyond observed fields, runtime MissionScript behavior, source identity, and rebuild parity remain unproven.",
                new String[] {"CDataType__CreateFromType"},
                datatypeTags("datatype-factory", "type-id-switch", "factory-type-cleanup"),
                new ParameterImpl[] {
                    param("type_id", intType),
                    param("bytecode_reader", voidPtr)
                }
            ),
            new Spec(
                "0x0052ef50",
                "CFloatDataType__Add",
                "__thiscall",
                voidPtr,
                "Wave575 signature/comment hardening: CFloatDataType arithmetic add vtable slot at data pointer 0x005e4ea8. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34, adds it to the float at this+0x04, allocates an 8-byte CFloatDataType object, installs vtable 0x005e4ea4, and stores the sum. Static retail evidence only; exact float ABI, exact datatype layout, allocation ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__Add"},
                datatypeTags("float-datatype", "vtable-slot", "arithmetic", "add"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052efc0",
                "CFloatDataType__Subtract",
                "__thiscall",
                voidPtr,
                "Wave575 signature/comment hardening: CFloatDataType arithmetic subtract vtable slot at data pointer 0x005e4eac. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34, subtracts rhs from the float at this+0x04, allocates an 8-byte CFloatDataType object, installs vtable 0x005e4ea4, and stores the difference. Static retail evidence only; exact float ABI, exact datatype layout, allocation ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__Subtract"},
                datatypeTags("float-datatype", "vtable-slot", "arithmetic", "subtract"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f030",
                "CFloatDataType__Multiply",
                "__thiscall",
                voidPtr,
                "Wave575 signature/comment hardening: CFloatDataType arithmetic multiply vtable slot at data pointer 0x005e4eb0. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34, multiplies it by the float at this+0x04, allocates an 8-byte CFloatDataType object, installs vtable 0x005e4ea4, and stores the product. Static retail evidence only; exact float ABI, exact datatype layout, allocation ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__Multiply"},
                datatypeTags("float-datatype", "vtable-slot", "arithmetic", "multiply"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f0a0",
                "CFloatDataType__Divide",
                "__thiscall",
                voidPtr,
                "Wave575 signature/comment hardening: CFloatDataType arithmetic divide vtable slot at data pointer 0x005e4eb4. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34, divides the float at this+0x04 by rhs, allocates an 8-byte CFloatDataType object, installs vtable 0x005e4ea4, and stores the quotient. Static retail evidence only; exact float ABI, exact datatype layout, divide-by-zero behavior, allocation ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__Divide"},
                datatypeTags("float-datatype", "vtable-slot", "arithmetic", "divide"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f110",
                "CFloatDataType__Equals",
                "__thiscall",
                boolType,
                "Wave575 signature/comment hardening: CFloatDataType equality vtable slot at data pointer 0x005e4ebc. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and returns whether it equals the float at this+0x04. Static retail evidence only; exact bool/float ABI, exact datatype layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__Equals"},
                datatypeTags("float-datatype", "vtable-slot", "comparison", "equals"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f140",
                "CFloatDataType__NotEquals",
                "__thiscall",
                boolType,
                "Wave575 signature/comment hardening: CFloatDataType inequality vtable slot at data pointer 0x005e4ec0. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and returns whether it differs from the float at this+0x04. Static retail evidence only; exact bool/float ABI, exact datatype layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__NotEquals"},
                datatypeTags("float-datatype", "vtable-slot", "comparison", "not-equals"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f170",
                "CFloatDataType__Assign",
                "__thiscall",
                voidType,
                "Wave575 signature/comment hardening: CFloatDataType assignment vtable slot at data pointer 0x005e4eb8. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and stores the returned float at this+0x04. Static retail evidence only; exact float ABI, exact datatype layout, assignment ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__Assign"},
                datatypeTags("float-datatype", "vtable-slot", "assignment"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f190",
                "CFloatDataType__LessThan",
                "__thiscall",
                boolType,
                "Wave575 signature/comment hardening: CFloatDataType less-than vtable slot at data pointer 0x005e4ec4. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and returns whether the float at this+0x04 is less than rhs. Static retail evidence only; exact bool/float ABI, exact datatype layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__LessThan"},
                datatypeTags("float-datatype", "vtable-slot", "comparison", "less-than"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f1c0",
                "CFloatDataType__GreaterThan",
                "__thiscall",
                boolType,
                "Wave575 signature/comment hardening: CFloatDataType greater-than vtable slot at data pointer 0x005e4ec8. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and returns whether the float at this+0x04 is greater than rhs. Static retail evidence only; exact bool/float ABI, exact datatype layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__GreaterThan"},
                datatypeTags("float-datatype", "vtable-slot", "comparison", "greater-than"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f1f0",
                "CFloatDataType__LessOrEqual",
                "__thiscall",
                boolType,
                "Wave575 signature/comment hardening: CFloatDataType less-or-equal vtable slot at data pointer 0x005e4ecc. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and returns whether the float at this+0x04 is less than or equal to rhs. Static retail evidence only; exact bool/float ABI, exact datatype layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__LessOrEqual"},
                datatypeTags("float-datatype", "vtable-slot", "comparison", "less-or-equal"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f220",
                "CFloatDataType__GreaterOrEqual",
                "__thiscall",
                boolType,
                "Wave575 signature/comment hardening: CFloatDataType greater-or-equal vtable slot at data pointer 0x005e4ed0. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34 and returns whether the float at this+0x04 is greater than or equal to rhs. Static retail evidence only; exact bool/float ABI, exact datatype layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CFloatDataType__GreaterOrEqual"},
                datatypeTags("float-datatype", "vtable-slot", "comparison", "greater-or-equal"),
                unaryDatatypeParams(voidPtr)
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
            throw new IllegalStateException("Wave575 datatype factory/float head tranche failed");
        }
    }
}
