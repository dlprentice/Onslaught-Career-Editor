//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
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

public class ApplyCIBufferIndexBufferWave413 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final boolean createIfMissing;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                boolean createIfMissing,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.createIfMissing = createIfMissing;
            this.tags = tags;
            this.parameters = parameters;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
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
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "cibuffer-index-buffer-wave413",
            "ibuffer",
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = functionAtEntry(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            boolean createdNow = false;

            if (fn == null) {
                if (!spec.createIfMissing) {
                    stats.missing++;
                    println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                    return;
                }
                if (dryRun) {
                    stats.wouldCreate++;
                    println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
                    return;
                }
                fn = createFunctionAt(spec, address);
                createdNow = true;
                stats.created++;
            }

            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                    stats.skipped++;
                    return;
                }
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
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

            println("OK: " + spec.address + " " + readBack.getSignature() + (createdNow ? " created" : ""));
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
                "0x00488210",
                "CIBuffer__Constructor",
                "__thiscall",
                voidPtr,
                "Wave413 signature/comment hardening: CIBuffer constructor sets the CIBuffer vtable 0x005dbec4, clears the D3D index-buffer pointer, initializes the base render/device object path, clears shadow-copy storage at +0x1c, and clears the lock flag at +0x20. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("constructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488270",
                "CIBuffer__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave413 signature/comment hardening: scalar deleting destructor wrapper calls CIBuffer__Destructor and conditionally frees the object when flags bit 0 is set. Static retail evidence only; exact source body identity, concrete allocator ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("destructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}
            ),
            new Spec(
                "0x00488290",
                "CIBuffer__Destructor",
                "__thiscall",
                voidType,
                "Wave413 signature/comment hardening: CIBuffer destructor restores the CIBuffer vtable, runs the base unlink/shutdown path, releases the D3D index-buffer interface when present for static or dynamic buffers, clears +0x08, frees shadow-copy storage at +0x1c, and then runs the base device-object destructor path. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("destructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488330",
                "CIBuffer__CreateConfigured",
                "__thiscall",
                intType,
                "Wave413 signature/comment correction: configured CIBuffer create stores size_bytes at +0x0c, usage_flags at +0x10, index_format at +0x14, and buffer_type at +0x18, then dispatches vtable slot +0x04 for dynamic buffers or vtable slot +0x08 for static buffers before the localized HRESULT fatal-check gate. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("create", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("size_bytes", intType),
                    param("usage_flags", intType),
                    param("index_format", intType),
                    param("buffer_type", intType)
                }
            ),
            new Spec(
                "0x00488380",
                "CIBuffer__Create",
                "__thiscall",
                intType,
                "Wave413 signature/comment hardening: default CIBuffer create allocates a shadow index buffer of index_count*2 bytes from the ibuffer.cpp debug path, stores size/usage/format/type fields, dispatches the dynamic create vtable slot, and checks the HRESULT with the localized fatal gate. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("create", "shadow-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("index_count", intType)}
            ),
            new Spec(
                "0x004883f0",
                "CIBuffer__Unlock",
                "__thiscall",
                intType,
                "Wave413 signature/comment hardening: CIBuffer unlock returns zero when no D3D buffer exists, directly unlocks when the shadow-copy dirty flag is clear, or locks the D3D buffer with 0x800, copies +0x0c bytes from shadow storage +0x1c, clears +0x20, and unlocks. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("lock-unlock", "shadow-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488460",
                "CIBuffer__CreateDynamic",
                "__thiscall",
                intType,
                "Wave413 recovered function boundary: CIBuffer dynamic-create vtable slot 1 checks buffer_type +0x18 == 1, calls the D3D CreateIndexBuffer wrapper at 0x005137d0 with size/usage/format and dynamic pool token 1, returns 0x80004005 on create or follow-up lock failure, and copies the shadow buffer into the locked D3D buffer before unlocking when shadow storage exists. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                true,
                tags("function-boundary", "vtable-slot", "create", "dynamic-buffer", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004884f0",
                "CIBuffer__CreateStatic",
                "__thiscall",
                intType,
                "Wave413 recovered function boundary: CIBuffer static-create vtable slot 2 checks buffer_type +0x18 == 0, calls the D3D CreateIndexBuffer wrapper at 0x005137d0 with size/usage/format and pool token 0, returns 0x80004005 on failure, and otherwise returns zero. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                true,
                tags("function-boundary", "vtable-slot", "create", "static-buffer", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488520",
                "CIBuffer__ReleaseStatic",
                "__thiscall",
                intType,
                "Wave413 signature/comment hardening: CIBuffer static-release vtable slot releases and clears +0x08 only when buffer_type +0x18 is static zero and the D3D index-buffer pointer is present; it returns zero. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("vtable-slot", "release", "static-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488550",
                "CIBuffer__ReleaseDynamic",
                "__thiscall",
                intType,
                "Wave413 signature/comment hardening: CIBuffer dynamic-release vtable slot releases and clears +0x08 only when buffer_type +0x18 is dynamic one and the D3D index-buffer pointer is present; it returns zero. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("vtable-slot", "release", "dynamic-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488580",
                "CIBuffer__Lock",
                "__thiscall",
                intType,
                "Wave413 signature/comment hardening: CIBuffer lock returns shadow storage +0x1c through out_data and sets dirty flag +0x20 when a shadow copy exists; otherwise it locks the D3D index buffer at +0x08 with 0x2800 when usage flag 0x200 is set or 0x800 otherwise. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("lock-unlock", "shadow-buffer", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("out_data", voidPtrPtr)}
            ),
            new Spec(
                "0x0048e350",
                "CIBuffer__Destructor_thunk",
                "__thiscall",
                voidType,
                "Wave413 signature/comment hardening: CIBuffer destructor thunk preserves the thiscall receiver and jumps to CIBuffer__Destructor. Static retail evidence only; exact source body identity, concrete caller ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("destructor", "thunk", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY updated=" + stats.updated
                + " skipped=" + stats.skipped
                + " created=" + stats.created
                + " would_create=" + stats.wouldCreate
                + " renamed=" + stats.renamed
                + " would_rename=" + stats.wouldRename
                + " missing=" + stats.missing
                + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave413 CIBuffer index-buffer apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
