//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyCImageLoaderWave414 extends GhidraScript {
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
            "cimageloader-wave414",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004885e0",
                "CIBuffer__LockDirect",
                "__thiscall",
                intType,
                "Wave414 owner/signature correction: direct CIBuffer D3D index-buffer lock helper locks the D3D index-buffer pointer at +0x08 into out_data and returns the HRESULT; usage flags at +0x10 select 0x2800 when bit 0x200 is set or 0x800 otherwise. CVBufTexture index-buffer callers and CDXLandscape use this helper directly. Static retail evidence only; exact source body identity, concrete CIBuffer layout beyond observed offsets, runtime rendering behavior, and rebuild parity remain unproven.",
                false,
                tags("ibuffer", "owner-corrected", "lock-unlock", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("out_data", voidPtrPtr)}
            ),
            new Spec(
                "0x00488620",
                "CImageLoader__Constructor",
                "__thiscall",
                voidPtr,
                "Wave414 signature/comment hardening: CImageLoader constructor zeroes fields +0x04 through +0x14, installs vtable 0x005dbedc, and copies filename to +0x18. Static retail evidence only; Stuart source body is absent from the current source snapshot, exact class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "constructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("filename", charPtr)}
            ),
            new Spec(
                "0x00488670",
                "CImageLoader__GetFilenamePtr",
                "__thiscall",
                charPtr,
                "Wave414 recovered vtable function boundary: CImageLoader getter returns this +0x18 as the filename pointer. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                true,
                tags("imageloader", "function-boundary", "vtable-slot", "getter", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488680",
                "CImageLoader__GetWidth",
                "__thiscall",
                intType,
                "Wave414 recovered vtable function boundary: CImageLoader getter returns image width from +0x08. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                true,
                tags("imageloader", "function-boundary", "vtable-slot", "getter", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488690",
                "CImageLoader__GetHeight",
                "__thiscall",
                intType,
                "Wave414 recovered vtable function boundary: CImageLoader getter returns image height from +0x0c. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                true,
                tags("imageloader", "function-boundary", "vtable-slot", "getter", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004886a0",
                "CImageLoader__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave414 signature/comment hardening: CImageLoader scalar deleting destructor frees width and height buffers at +0x10/+0x14, then conditionally frees the object when flags bit 0 is set. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "destructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}
            ),
            new Spec(
                "0x00488700",
                "CImageLoader__Destructor",
                "__thiscall",
                voidType,
                "Wave414 signature/comment hardening: CImageLoader destructor restores the base vtable and frees width and height buffers at +0x10/+0x14. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "destructor", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488740",
                "CImageLoader__FreeWidthBuffer",
                "__thiscall",
                voidType,
                "Wave414 signature/comment hardening: CImageLoader width-buffer free helper releases the buffer pointer at +0x10 through the global memory manager and clears the field. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488760",
                "CImageLoader__FreeHeightBuffer",
                "__thiscall",
                voidType,
                "Wave414 signature/comment hardening: CImageLoader height-buffer free helper releases the buffer pointer at +0x14 through the global memory manager and clears the field. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x00488780",
                "CImageLoader__LoadWidthBuffer",
                "__thiscall",
                boolType,
                "Wave414 signature/comment hardening: CImageLoader width-buffer load helper calls vtable slot +0x24 to free the previous width buffer, allocates 0x80 bytes from the imageloader.cpp debug path line 0x2b using alloc_context, stores the result at +0x10, and returns allocation success. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("alloc_context", voidPtr)}
            ),
            new Spec(
                "0x004887c0",
                "CImageLoader__LoadHeightBuffer",
                "__thiscall",
                boolType,
                "Wave414 signature/comment hardening: CImageLoader height-buffer load helper calls vtable slot +0x28 to free the previous height buffer, allocates 0x80 bytes from the imageloader.cpp debug path line 0x32 using alloc_context, stores the result at +0x14, and returns allocation success. Static retail evidence only; exact source body identity, concrete class layout, runtime image loading, and rebuild parity remain unproven.",
                false,
                tags("imageloader", "buffer-lifecycle", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("alloc_context", voidPtr)}
            ),
            new Spec(
                "0x0052f540",
                "SharedVFunc__ReturnField04_0052f540",
                "__thiscall",
                voidPtr,
                "Wave414 recovered shared vtable function boundary: compact getter returns field +0x04 and is referenced by ImageLoader plus other vtables. Static retail evidence only; exact owning source method names, concrete class layouts, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "function-boundary", "vtable-slot", "getter", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}
            ),
            new Spec(
                "0x004de070",
                "SharedVFunc__ReturnField14_004de070",
                "__thiscall",
                voidPtr,
                "Wave414 recovered shared vtable function boundary: compact getter returns field +0x14 and is referenced by ImageLoader plus other vtables. Static retail evidence only; exact owning source method names, concrete class layouts, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "function-boundary", "vtable-slot", "getter", "comment-hardened"),
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
            throw new IllegalStateException("Wave414 CImageLoader apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
