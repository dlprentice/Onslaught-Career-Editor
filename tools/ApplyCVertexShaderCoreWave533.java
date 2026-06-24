//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyCVertexShaderCoreWave533 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.renameAllowed = renameAllowed;
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
            "cvertexshader-core-wave533",
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
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
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

        boolean updateNeeded = needsUpdate(fn, spec);
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
        println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType byteType = ByteDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00501800",
                "CVertexShader__CVertexShader",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave533 CVertexShader core signature/comment hardening: constructor installs vtable 0x005dfbc4, clears shader/resource fields, initializes the CShaderBase/device-object path, links the object into global shader list 0x00854e68, seeds shader type/version field +0x2c to 9, and returns this. Static retail evidence only; exact source-body identity, concrete CVertexShader/CShaderBase/device-object layouts, runtime shader behavior, runtime Direct3D behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "constructor", "shader-lifetime", "global-list"),
                false
            ),
            new Spec(
                "0x00501890",
                "CVertexShader__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave533 stale-vfunc correction: vtable slot 0 is the scalar-deleting destructor wrapper, not an unknown virtual. RET 0x4 proves one delete_flags argument after ECX; the body calls CVertexShader__dtor and frees this through CDXMemoryManager__Free when delete_flags bit 0 is set. Static retail evidence only; exact allocator ownership, complete destructor call graph, concrete CVertexShader layout, runtime shader behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "destructor", "name-corrected", "scalar-deleting-destructor", "vtable-slot"),
                true
            ),
            new Spec(
                "0x005018b0",
                "CVertexShader__dtor",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave533 stale-destructor-body correction: destructor body restores vtable 0x005dfbc4, unlinks this from global shader list 0x00854e68 and the base device-object lists, releases the device shader pointer at +0x28, frees constant/source/blob buffers at +0x38/+0x40/+0x44/+0x48/+0x50 when present, and chains to the base device-object teardown path. Static retail evidence only; exact source-body identity, concrete CVertexShader/CShaderBase/device-object layouts, runtime shader behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "destructor", "name-corrected", "resource-lifetime", "shader-lifetime"),
                true
            ),
            new Spec(
                "0x00501b60",
                "CVertexShader__VFunc_03_00501b60",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave533 CVertexShader core signature/comment hardening: vtable slot 3 releases the device shader-like pointer at +0x28 through its vtable +0x08 release call, clears +0x28, and returns 0. The exact source virtual method name remains deferred, and adjacent vtable slot 2 at 0x00501a10 is not recovered in this tranche. Static retail evidence only; concrete device-interface identity, runtime device-loss behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "device-shader", "release", "vtable-slot"),
                false
            ),
            new Spec(
                "0x00501ba0",
                "CVertexShader__GetVertexDeclarationToken",
                "__thiscall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave533 CVertexShader core signature/comment hardening: ECX-only getter maps shader type/version field +0x2c to Direct3D vertex-declaration tokens 0x152, 0x15a, 0x46, 0x102, or 0x142, and CEngine__SetShaderObject forwards the result with the shader object to the device call. Static retail evidence only; exact declaration enum names, concrete CVertexShader layout, runtime Direct3D behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "direct3d", "render-state", "vertex-declaration"),
                false
            ),
            new Spec(
                "0x00501cd0",
                "CVertexShader__ApplyRenderStateShaderConstants",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave533 CVertexShader core signature/comment hardening: ECX-only render-state constant uploader. When shaders are enabled it delegates to the custom constant path if flag +0x34 is set; otherwise it builds projection/view constant blocks from engine globals, dispatches CVertexShader table helpers, uploads multiple Direct3D vertex shader constants through device vtable +0x178, applies the CVBufTexture texture-transform thunk, and checks for ShadowShader by name. Static retail evidence only; exact constant-register semantics, matrix layout, runtime Direct3D behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "direct3d", "render-state", "shader-constants"),
                false
            ),
            new Spec(
                "0x00502060",
                "CVertexShader__Create",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("shader_name", charPtr),
                    param("shader_id", intType),
                    param("shader_type", intType),
                    param("compiled_blob", voidPtr),
                    param("compiled_blob_size", intType),
                    param("load_flags", intType)
                },
                "Wave533 CVertexShader core signature/comment hardening: cdecl factory returns null when shaders are disabled, searches global list 0x00854e68 by compiled-blob contents or by case-insensitive shader_name plus shader_id, allocates a 0x5c-byte CVertexShader when no cache hit exists, loads from file or copies the compiled blob, then increments live reference count +0x30 before returning the shader. Static retail evidence only; raw caller boundaries at 0x0055512a and 0x0055b3e3, exact source-body identity, concrete CVertexShader layout, runtime shader compilation behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "factory", "resource-cache", "shader-lifetime"),
                false
            ),
            new Spec(
                "0x00502290",
                "CVertexShader__DecrementLiveReferenceCount",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave533 CVertexShader core signature/comment hardening: ECX-only release helper decrements the live reference counter at +0x30; callers include pending render-state replacement, landscape shutdown, mesh VB release, and atmospherics resource release paths. Static retail evidence only; exact ownership rules, concrete CVertexShader layout, runtime shader lifetime behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "refcount", "resource-lifetime", "shader-lifetime"),
                false
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave533 CVertexShader core apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
