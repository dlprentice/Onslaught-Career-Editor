//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCVBufferTailWave529 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean createIfMissing;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                boolean createIfMissing, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
            this.renameAllowed = renameAllowed;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int created = 0;
        int wouldCreate = 0;
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

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cvbuffer-tail-wave529",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        Function containing = getFunctionContaining(address);
        if (containing != null && !containing.getEntryPoint().equals(address)) {
            throw new IllegalStateException(
                "Address " + spec.address + " is inside existing function " + containing.getName());
        }
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = getFunctionAt(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        return fn;
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function fn = functionAtEntry(spec.address);
        boolean createdNow = false;

        if (fn == null) {
            if (!spec.createIfMissing) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (dryRun) {
                println("DRYCREATE: " + spec.address + " <missing> -> " + expectedSignature(spec));
                stats.wouldCreate++;
                stats.skipped++;
                return;
            }
            fn = createFunctionAt(spec, address);
            createdNow = true;
            stats.created++;
        }

        if (!fn.getName().equals(spec.name)) {
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (dryRun) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                stats.wouldRename++;
                stats.skipped++;
                return;
            }
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }

        boolean updateNeeded = createdNow || needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
            stats.skipped++;
            return;
        }

        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec) +
            (createdNow ? " created" : ""));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004fff00",
                "CVBuffer__ctor_base",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: constructor installs the CVBuffer vtable at 0x005dfb8c, clears the D3D vertex-buffer pointer at +0x08, initializes the shader/device-object base path through CShaderBase__Init, then clears the system-memory backing pointer at +0x24 and dirty byte +0x28. Static retail evidence only; exact source-body identity, concrete CVBuffer layout, runtime rendering behavior, device-loss behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "constructor", "vertex-buffer", "direct3d"),
                false,
                true
            ),
            new Spec(
                "0x004fff60",
                "CVBuffer__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)},
                "Wave529 CVBuffer tail signature/comment hardening: vtable slot 0 is the scalar-deleting destructor wrapper, not an unknown VFunc; it calls CVBuffer__dtor_base and frees this through CDXMemoryManager__Free when flags bit 0 is set. Static retail evidence only; exact allocator ownership, destructor call graph under every derived owner, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "destructor", "scalar-deleting-destructor", "vtable-slot"),
                false,
                true
            ),
            new Spec(
                "0x004fff80",
                "CVBuffer__dtor_base",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: destructor body restores the CVBuffer vtable, runs the base unlink/destruction helper, releases the D3D vertex-buffer interface for mode 0 or mode 1 buffers, clears +0x08/+0x28, frees backing storage +0x24 through the DX memory manager, and then runs the base device-object teardown path. Static retail evidence only; exact source-body identity, concrete CVBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "destructor", "vertex-buffer", "direct3d"),
                false,
                true
            ),
            new Spec(
                "0x00500020",
                "CVBuffer__CreateInternal",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("total_bytes", intType),
                    param("usage_flags", intType),
                    param("fvf_format", intType),
                    param("pool_mode", intType)
                },
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x10 proves four explicit stack arguments after ECX. The body stores total_bytes, usage_flags, fvf_format, stride zero, and pool_mode into +0x10/+0x14/+0x18/+0x1c/+0x20, dispatches vtable slot 1 for pool_mode 1 or slot 2 otherwise, checks the HRESULT through FatalError_LocalizedStringId text id 0xd2, and returns the HRESULT. Static retail evidence only; exact D3D pool enum names, runtime device behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "create", "direct3d", "vtable-dispatch"),
                false,
                false
            ),
            new Spec(
                "0x00500080",
                "CVBuffer__CreateDynamic",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("vertex_count", intType),
                    param("vertex_stride", intType),
                    param("fvf_format", intType)
                },
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x0c proves vertex_count, vertex_stride, and fvf_format stack arguments after ECX. The helper stores stride at +0x1c, total bytes at +0x10, usage flags 0x208 at +0x14, FVF at +0x18, default-pool mode 0 at +0x20, invokes vtable slot 2, and returns HRESULT >= 0 as bool. Static retail evidence only; exact source-body identity, runtime D3D behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "create", "dynamic-buffer", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x005000c0",
                "CVBuffer__Create",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("vertex_count", intType),
                    param("vertex_stride", intType),
                    param("fvf_format", intType)
                },
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x0c proves vertex_count, vertex_stride, and fvf_format stack arguments after ECX. The helper stores stride/FVF/total bytes, usage flag 8, managed mode 1, allocates a system-memory backing buffer through OID__AllocObject using vbuffer.cpp line 0x53 and pool token 0x2d, calls vtable slot 1, and returns HRESULT >= 0 as bool. Static retail evidence only; exact source-body identity, runtime D3D behavior, allocation lifetime, and rebuild parity remain unproven.",
                tags("cvbuffer", "create", "managed-buffer", "shadow-buffer"),
                false,
                false
            ),
            new Spec(
                "0x00500120",
                "CVBuffer__Restore",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: ECX-only vtable slot 1 restores mode 1 buffers by calling CEngine__DeviceCall68_CheckError with size/usage/FVF and pool token 1, locks the recreated D3D vertex buffer with flag 0x800 when backing storage +0x24 exists, copies +0x10 bytes from that backing store, unlocks, and returns the HRESULT or 0. Static retail evidence only; exact Direct3D wrapper identity, device-loss runtime behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "restore", "managed-buffer", "device-loss"),
                false,
                false
            ),
            new Spec(
                "0x005001b0",
                "CVBuffer__Lock",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("out_data", voidPtrPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x4 proves one out_data argument after ECX. If backing storage +0x24 exists, the helper returns that pointer through out_data, sets dirty byte +0x28, and returns 0; otherwise it locks the D3D vertex buffer at +0x08 with flag 0x800 and returns the D3D Lock HRESULT. Static retail evidence only; exact lock ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "lock-unlock", "shadow-buffer", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x005001e0",
                "CVBuffer__Unlock",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: ECX-only unlock returns 0 when no D3D buffer exists, directly unlocks the D3D vertex buffer when dirty byte +0x28 is clear, or clears the dirty byte, locks with flag 0x800, copies +0x10 bytes from backing storage +0x24 into the device buffer, and unlocks. Static retail evidence only; exact source-body identity, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "lock-unlock", "shadow-buffer", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x00500250",
                "CVBuffer__CreateDefaultPoolVertexBuffer",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 recovered function boundary: CVBuffer vtable slot 2 at 0x005dfb94 and the derived DXPatch-style vtable slot at 0x005e511c both point here. The ECX-only body returns 0 when pool mode +0x20 is nonzero, otherwise calls CEngine__DeviceCall68_CheckError with size +0x10, usage +0x14, FVF +0x18, pool token 0, and out pointer this+0x08, returning 0x80004005 on failure or 0 on success. Static retail evidence only; exact D3D pool naming, runtime device behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "create", "default-pool", "function-boundary", "vtable-slot"),
                true,
                true
            ),
            new Spec(
                "0x00500280",
                "CVBuffer__Release",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: ECX-only vtable slot 3 releases the D3D vertex-buffer interface at +0x08 only for mode 0 buffers, then clears +0x08 and dirty byte +0x28 and returns 0. Static retail evidence only; exact source-body identity, runtime device ownership, and rebuild parity remain unproven.",
                tags("cvbuffer", "release", "default-pool", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x005002b0",
                "CVBuffer__ReleaseManaged",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: ECX-only vtable slot 4 releases the D3D vertex-buffer interface at +0x08 only for mode 1 buffers, then clears +0x08 and dirty byte +0x28 and returns 0. Static retail evidence only; exact source-body identity, runtime device ownership, and rebuild parity remain unproven.",
                tags("cvbuffer", "release", "managed-buffer", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x005002e0",
                "CVBuffer__EnsureLock",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr), param("out_data", voidPtrPtr)},
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x4 proves one out_data argument after ECX. The helper locks the D3D vertex buffer at +0x08 with 0x2800 when usage flags +0x14 include 0x200, otherwise with 0x800, and callers test the carried D3D Lock HRESULT in EAX. Static retail evidence only; exact D3D lock flag names, runtime streaming behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "lock-unlock", "dynamic-buffer", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x00500320",
                "CVBuffer__SetStreamSource",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("stream_index", intType)},
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x4 proves one stream_index argument after ECX. The helper writes FVF +0x18 into global 0x009c73d4, sets stream-active global 0x009c741c to 1, and calls Direct3D device vtable offset 400 with stream_index, vertex buffer +0x08, offset 0, and stride +0x1c. Static retail evidence only; exact render-state ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "stream-source", "render-state", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x00500360",
                "CVBuffer__SetStreamSourceSimple",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("stream_index", intType)},
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x4 proves one stream_index argument after ECX. This simpler stream-source helper skips the global FVF/active-state writes and calls Direct3D device vtable offset 400 with stream_index, vertex buffer +0x08, offset 0, and stride +0x1c. Static retail evidence only; exact render-state ownership, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "stream-source", "direct3d"),
                false,
                false
            ),
            new Spec(
                "0x00500390",
                "CVBuffer__LockRange",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("offset_bytes", intType),
                    param("size_bytes", intType),
                    param("out_data", voidPtrPtr),
                    param("lock_flags", intType)
                },
                "Wave529 CVBuffer tail signature/comment hardening: RET 0x10 proves offset_bytes, size_bytes, out_data, and lock_flags stack arguments after ECX. The helper returns 0x80004005 when the D3D vertex buffer at +0x08 is null, otherwise forwards the range and flags to D3D Lock vtable offset 0x2c and returns its HRESULT. Static retail evidence only; exact caller ownership, runtime streaming behavior, and rebuild parity remain unproven.",
                tags("cvbuffer", "lock-unlock", "range-lock", "direct3d"),
                false,
                false
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " created=" + stats.created + " would_create=" + stats.wouldCreate +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave529 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
