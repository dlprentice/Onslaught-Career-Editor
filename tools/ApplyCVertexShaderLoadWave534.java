//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCVertexShaderLoadWave534 extends GhidraScript {
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
            "cvertexshader-load-wave534",
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

        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00501730",
                "CVertexShader__ClearOut",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave534 CVertexShader load/compile hardening: shutdown helper walks global shader list 0x00854e68, reports zero-refcount leaks with DebugTrace/sprintf text, deletes zero-live-reference entries through vtable slot 0, then deletes remaining shader-list entries during CLTShell shutdown before CVBufTexture__ClearOut. Static retail evidence only; exact source-body identity, concrete CVertexShader/list layout, allocator ownership, runtime shutdown behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "global-list", "resource-lifetime", "shutdown"),
                false
            ),
            new Spec(
                "0x005019d0",
                "CVertexShader__QueryDeviceCapsAndSetGlobalSupportFlag",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave534 CVertexShader load/compile hardening: global helper queries Direct3D device caps when device global 0x00888c8c is present and updates vertex-shader support flag 0x00854e6c from the 0xfffe0101 capability comparison; CDXMeshVB__BuildSkeletalVB calls it before skeletal VB setup. Static retail evidence only; exact caps-field identity, runtime hardware behavior, Direct3D version semantics, and rebuild parity remain unproven.",
                tags("cvertexshader", "device-caps", "direct3d", "support-flag"),
                false
            ),
            new Spec(
                "0x005022a0",
                "CVertexShader__LoadFromFile",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("shader_name", charPtr),
                    param("source_or_blob", voidPtr),
                    param("shader_type", intType),
                    param("source_or_blob_size", intType)
                },
                "Wave534 CVertexShader load/compile hardening: thiscall loader/finalizer calls vtable +0x0c before loading, copies shader_name into object field +0x08, clears custom-state flag +0x34, stores shader_type at +0x2c, either assembles source when source_or_blob_size is -1 or stores/copies caller-provided blob bytes into +0x50/+0x54, then calls vtable +0x08 and returns 0 or 0x80004005. Static retail evidence only; exact file/source/blob ownership, concrete CVertexShader layout, source-body identity, runtime shader compilation behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "shader-load", "shader-source", "shader-bytecode"),
                false
            ),
            new Spec(
                "0x00502420",
                "CVertexShader__CompileShader",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave534 CVertexShader load/compile hardening: ECX-only compiler frees existing bytecode +0x50, detects vs.1.1 or vs.1.0 source, injects dcl_position plus optional blendweight/normal/color/texcoord declarations, blanks oFog.x references, assembles through the D3DX-style parser path, stores compiled bytecode at +0x50/+0x54, and frees source +0x48. Static retail evidence only; exact parser identity, concrete declaration-table semantics, runtime Direct3D behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "direct3d", "shader-compile", "shader-source"),
                false
            ),
            new Spec(
                "0x005027f0",
                "CVertexShader__LoadCompiledShaderBlobFromVSOFile",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("shader_name", charPtr),
                    param("shader_token", intType),
                    param("device_shader_out", voidPtr)
                },
                "Wave534 CVertexShader load/compile hardening: stack-cleaning helper (RET 0x0c) builds Shaders/%s.vso from shader_name, opens the compiled shader file, reads it through HeapAlloc/ReadFile, then calls the engine/device create-shader path with shader_token, bytecode, and device_shader_out before freeing the heap buffer. The raw vtable-slot-2 caller at 0x00501a10 seeds ECX with the CVertexShader object but this helper consumes only the three stack arguments. Static retail evidence only; the slot-2 boundary/name, exact device interface, runtime file behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "compiled-shader", "direct3d", "vtable-slot-2-caller"),
                false
            ),
            new Spec(
                "0x00502920",
                "CVertexShader__ApplyCustomRenderStateShaderConstants",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave534 CVertexShader load/compile hardening: ECX-only custom render-state constant uploader uses object constant-table/list fields +0x40/+0x38, projection/view/light/render-state globals, CVertexShader dispatch helpers, CVBufTexture texture-transform thunk, and Direct3D device vtable +0x178 uploads for custom shader tokens. Static retail evidence only; exact constant-register meanings, concrete table layouts, runtime render-state behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "direct3d", "render-state", "shader-constants"),
                false
            ),
            new Spec(
                "0x00503ac0",
                "CVertexShader__BuildAndCreateRenderInfoShader",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {},
                "Wave534 CVertexShader load/compile hardening: global render-info builder constructs a declaration/token stream from render-state globals, optional light/camera records, and feature flags, terminates it with zero, then calls CVertexShader__Create for either the custom-declaration or default RenderInfo shader path; caller CDXEngine__ApplyPendingRenderState consumes the returned shader pointer from EAX. Static retail evidence only; exact token enum names, runtime render-state coverage, concrete light/camera layouts, and rebuild parity remain unproven.",
                tags("cvertexshader", "factory", "render-info", "render-state"),
                false
            ),
            new Spec(
                "0x00503dd0",
                "CVertexShader__AppendDeclarationNamesToDebugString",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("out_buffer", charPtr),
                    param("declaration_tokens", voidPtr)
                },
                "Wave534 CVertexShader load/compile hardening: debug formatter initializes out_buffer, walks a zero-terminated declaration token stream, appends either matching names from the declaration-name table at 0x00634074..0x00634554 or Unknown lines, and is called from the raw declaration-dump helper near 0x00503f2f. Static retail evidence only; exact table enum names, raw caller boundary, output buffer size contract, and rebuild parity remain unproven.",
                tags("cvertexshader", "debug-format", "declaration-tokens", "render-state"),
                false
            ),
            new Spec(
                "0x00503f90",
                "CVertexShader__Clone",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("chunk_reader", voidPtr),
                    param("shader_index", intType)
                },
                "Wave534 CVertexShader load/compile hardening: cdecl chunk-reader clone allocates a 0x5c-byte CVertexShader, preserves constructor-owned vtable/list fields, reads serialized object/resource chunks, deep-copies compiled data, constant counts/tables, source and bytecode buffers, optionally reloads debug source shader%03d.i using shader_index when debug flag 0x00662f35 is set, recompiles, frees temporary source, finalizes through vtable +0x08, and returns the new shader. Static retail evidence only; exact chunk schema, concrete CVertexShader layout, allocator ownership, runtime debug reload behavior, and rebuild parity remain unproven.",
                tags("cvertexshader", "chunk-reader", "clone", "shader-compile"),
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
            throw new IllegalStateException("Wave534 CVertexShader load apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
