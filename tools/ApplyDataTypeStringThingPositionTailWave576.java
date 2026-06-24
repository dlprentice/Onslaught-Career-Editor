//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyDataTypeStringThingPositionTailWave576 extends GhidraScript {
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
            "datatype-string-thing-position-tail-wave576",
            "retail-binary-evidence",
            "mission-script",
            "datatype",
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

    private ParameterImpl[] unaryDatatypeParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("rhs", voidPtr)
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType byteType = ByteDataType.dataType;
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0052f2c0",
                "CStringDataType__Clone",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CStringDataType clone vtable slot at data pointer 0x005e4e94. ECX is this, the body allocates an 8-byte CStringDataType object, installs CStringDataType vtable 0x005e4e4c, allocates a heap buffer sized from the source string at this+0x04, copies the string, and null-terminates the clone buffer. Static retail evidence only; exact string allocator ownership, copy failure behavior, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__Clone"},
                tags("string-datatype", "clone", "vtable-slot"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x0052f360",
                "CStringDataType__Equals",
                "__thiscall",
                boolType,
                "Wave576 signature/comment hardening: CStringDataType equality vtable slot at data pointer 0x005e4e64. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x38 and compares that returned string with the string pointer stored at this+0x04. Static retail evidence only; exact bool ABI, string collation/locale behavior, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__Equals"},
                tags("string-datatype", "comparison", "equals", "vtable-slot"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f430",
                "CStringDataType__Print",
                "__thiscall",
                voidType,
                "Wave576 signature/comment hardening: CStringDataType print/reader bridge vtable slot observed at data pointer 0x005e4e0c in adjacent datatype tables. ECX is this, RET 0x4 confirms one rhs stack argument, the body calls rhs vtable slot +0x40 and passes the returned reader cell into CGenericActiveReader__SetReader for the string field at this+0x04. Static retail evidence only; exact active-reader semantics, output ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__Print"},
                tags("string-datatype", "reader-bridge", "vtable-slot"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f470",
                "CThingPtrDataType__Clone",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CThingPtrDataType clone vtable slot at data pointer 0x005e4e40. ECX is this, the body allocates an 8-byte thing-pointer datatype, copies the pointer stored at this+0x04, creates a CSPtrSet at pointed_object+0x04 when needed, registers the clone's pointer field with CSPtrSet__AddToHead, and installs CThingPtrDataType vtable 0x005e4df8. Static retail evidence only; exact pointed-object class/layout, pointer-set ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CThingPtrDataType__Clone"},
                tags("thingptr-datatype", "clone", "pointer-tracking", "vtable-slot"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x0052f550",
                "CThingPtrDataType__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CThingPtrDataType scalar-deleting destructor at vtable 0x005e4df8. ECX is this, RET 0x4 confirms the flags argument, the wrapper calls CThingPtrDataType__Destructor and frees this through CDXMemoryManager__Free when flags&1 is set. Static retail evidence only; exact MSVC deleting-destructor ABI details, allocator ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CThingPtrDataType__ScalarDeletingDestructor"},
                tags("thingptr-datatype", "destructor", "scalar-deleting-destructor", "vtable-slot"),
                scalarDeletingParams(voidPtr, byteType)
            ),
            new Spec(
                "0x0052f570",
                "CThingPtrDataType__Destructor",
                "__thiscall",
                voidType,
                "Wave576 signature/comment hardening: CThingPtrDataType destructor called by its scalar-deleting wrapper. ECX is this, the body checks this+0x04, removes this+0x04 from the pointed object's CSPtrSet at pointed_object+0x04 when present, and restores the base CDataType vtable pointer 0x005e4b4c. Static retail evidence only; exact pointed-object class/layout, pointer-set lifetime, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CThingPtrDataType__Destructor"},
                tags("thingptr-datatype", "destructor", "pointer-tracking"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x0052f670",
                "CDataType__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: shared CDataType scalar-deleting destructor wrapper reused by CIntDataType, CFloatDataType, CBoolDataType, and CPositionDataType vtable heads. ECX is this, RET 0x4 confirms the flags argument, the body calls CDataType__Destructor and frees this through CDXMemoryManager__Free when flags&1 is set. Static retail evidence only; exact MSVC deleting-destructor ABI details, concrete derived-type ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CDataType__ScalarDeletingDestructor"},
                tags("base-datatype", "destructor", "scalar-deleting-destructor", "shared-vtable-head"),
                scalarDeletingParams(voidPtr, byteType)
            ),
            new Spec(
                "0x0052f690",
                "CStringDataType__InitFromString",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CStringDataType constructor/init helper called from MissionScript string-return sites. ECX is this, RET 0x4 confirms one source_text stack argument, the body installs CStringDataType vtable 0x005e4e4c, allocates a heap buffer sized from source_text, copies the source string, null-terminates it, and returns this. Static retail evidence only; exact constructor identity, empty/null input behavior, allocator ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__InitFromString"},
                tags("string-datatype", "constructor-init", "string-copy"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("source_text", charPtr)
                }
            ),
            new Spec(
                "0x0052f720",
                "CStringDataType__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CStringDataType scalar-deleting destructor at vtable 0x005e4e4c. ECX is this, RET 0x4 confirms the flags argument, the wrapper calls CStringDataType__Destructor and frees this through CDXMemoryManager__Free when flags&1 is set. Static retail evidence only; exact MSVC deleting-destructor ABI details, string buffer ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__ScalarDeletingDestructor"},
                tags("string-datatype", "destructor", "scalar-deleting-destructor", "vtable-slot"),
                scalarDeletingParams(voidPtr, byteType)
            ),
            new Spec(
                "0x0052f740",
                "CStringDataType__Destructor",
                "__thiscall",
                voidType,
                "Wave576 signature/comment hardening: CStringDataType destructor called by its scalar-deleting wrapper and unwind cleanup sites. ECX is this, the body frees the string buffer at this+0x04 through CDXMemoryManager__Free and restores the base CDataType vtable pointer 0x005e4b4c. Static retail evidence only; exact string buffer ownership, null-pointer behavior, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__Destructor"},
                tags("string-datatype", "destructor", "string-buffer-free"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x0052f790",
                "CStringDataType__ReadFromBuffer",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CStringDataType bytecode-buffer read helper called from CWorld__LoadScriptEvents and CScriptObjectCode__ReadSymbolTable. ECX is this, RET 0x4 confirms one bytecode_reader stack argument, the body installs CStringDataType vtable 0x005e4e4c, reads a 4-byte string length, allocates length+1 bytes, reads that many bytes into the buffer, and appends a null terminator. Static retail evidence only; exact buffer class contract, length validation, allocator ownership, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CStringDataType__ReadFromBuffer"},
                tags("string-datatype", "buffer-read", "bytecode-read"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("bytecode_reader", voidPtr)
                }
            ),
            new Spec(
                "0x0052f8a0",
                "CPositionDataType__SubtractPosition",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CPositionDataType subtract vtable slot at data pointer 0x005e4dac. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x44, allocates a 0x14-byte CPositionDataType object, installs vtable 0x005e4da4, and stores the observed x/y/z differences from this+0x04/+0x08/+0x0c. Static retail evidence only; trailing dword semantics, exact vector layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CPositionDataType__SubtractPosition"},
                tags("position-datatype", "arithmetic", "subtract", "vtable-slot"),
                unaryDatatypeParams(voidPtr)
            ),
            new Spec(
                "0x0052f920",
                "CPositionDataType__ScaleByFloat",
                "__thiscall",
                voidPtr,
                "Wave576 signature/comment hardening: CPositionDataType scale-by-float vtable slot at data pointer 0x005e4db0. ECX is this, RET 0x4 confirms one rhs stack argument, the body reads rhs through datatype vtable slot +0x34, allocates a 0x14-byte CPositionDataType object, installs vtable 0x005e4da4, and stores x/y/z scaled from this+0x04/+0x08/+0x0c. Static retail evidence only; trailing dword semantics, exact float ABI, exact vector layout, source identity, runtime MissionScript behavior, and rebuild parity remain unproven.",
                new String[] {"CPositionDataType__ScaleByFloat"},
                tags("position-datatype", "arithmetic", "scale", "float-rhs", "vtable-slot"),
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
            throw new IllegalStateException("Wave576 datatype string/thing/position tail tranche failed");
        }
    }
}
