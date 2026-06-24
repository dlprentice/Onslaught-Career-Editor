//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedCharDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyD3DShaderInputTailWave850 extends GhidraScript {
    private static class Spec {
        final String address;
        final String currentName;
        final String expectedName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String currentName, String expectedName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.currentName = currentName;
            this.expectedName = expectedName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "d3d-shader-input-tail-wave850",
            "wave850-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean sameDataType(DataType a, DataType b) {
        if (a == null || b == null) {
            return a == b;
        }
        return a.getName().equals(b.getName()) || a.getDisplayName().equals(b.getDisplayName()) || a.isEquivalent(b);
    }

    private boolean sameSignature(Function fn, Spec spec) {
        if (!fn.getCallingConventionName().equals(spec.callingConvention)) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        Parameter[] actualParams = fn.getParameters();
        if (actualParams.length != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < actualParams.length; i++) {
            Parameter actual = actualParams[i];
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

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> actual = tagNames(fn);
        for (String tag : tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean readBackMatches(Function fn, Spec spec, Stats stats) {
        boolean ok = true;
        if (!fn.getName().equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected=" + spec.expectedName + " actual=" + fn.getName());
            ok = false;
        }
        if (!sameSignature(fn, spec)) {
            println("BADSIG: " + spec.address + " actual=" + fn.getSignature() + " convention=" + fn.getCallingConventionName());
            ok = false;
        }
        if (!spec.comment.equals(fn.getComment())) {
            println("BADCOMMENT: " + spec.address);
            ok = false;
        }
        if (!hasAllTags(fn, spec.tags)) {
            println("BADTAGS: " + spec.address);
            ok = false;
        }
        if (!ok) {
            stats.bad++;
        }
        return ok;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            return;
        }
        String actualName = fn.getName();
        if (!actualName.equals(spec.currentName) && !actualName.equals(spec.expectedName)) {
            println("BADNAME: " + spec.address + " expected current=" + spec.currentName
                + " or final=" + spec.expectedName + " actual=" + actualName);
            stats.bad++;
            return;
        }

        boolean needsRename = !actualName.equals(spec.expectedName);
        boolean needsSignature = !sameSignature(fn, spec);
        boolean needsCommentOrTags = !spec.comment.equals(fn.getComment()) || !hasAllTags(fn, spec.tags);

        if (needsRename) {
            stats.wouldRename++;
        }
        if (needsSignature) {
            stats.signatureUpdated++;
        }
        if (needsCommentOrTags) {
            stats.commentOnlyUpdated++;
        }

        if (!needsRename && !needsSignature && !needsCommentOrTags) {
            println((dryRun ? "DRY" : "SKIP") + ": " + spec.address + " " + fn.getName() + " already matched");
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName()
                + " needsRename=" + needsRename
                + " needsSignature=" + needsSignature
                + " needsCommentOrTags=" + needsCommentOrTags);
            stats.skipped++;
            return;
        }

        if (needsRename) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsSignature) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
        }
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        if (readBackMatches(fn, spec, stats)) {
            println("APPLY_OK: " + spec.address + " " + spec.expectedName + " " + fn.getSignature());
        }
        stats.updated++;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType boolType = BooleanDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType ucharType = UnsignedCharDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType voidPtrPtr = new PointerDataType(voidPtr);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00513a80",
                "PlatformInput__GetKeyState3Core",
                "PlatformInput__GetKeyState3Core",
                "__thiscall",
                boolType,
                new ParameterImpl[] { param("this", voidPtr), param("key", intType) },
                "Wave850 static read-back/signature/comment hardening: PlatformInput key-state helper reached from CPCController__GetKeyState3 and source PCController/PCPlatform KeyOn -> LT.xKeyOn. The body returns the byte at this+0x332e4+key and RET 0x4. Static retail/source evidence only; exact key-table owner layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("input", "controller", "source-keyon")
            ),
            new Spec(
                "0x00513a90",
                "PlatformInput__GetKeyOnceCore",
                "PlatformInput__GetKeyOnceCore",
                "__thiscall",
                boolType,
                new ParameterImpl[] { param("this", voidPtr), param("key", intType) },
                "Wave850 static read-back/signature/comment hardening: PlatformInput one-shot key helper reached from CPCController__GetKeyOnce and source PCController/PCPlatform KeyOnce -> LT.xKeyOnce. The body reads and clears this+0x331e4+key, appends consumed keys to the 0x00855424 queue while PTR_DAT_0063dc1c is below PTR_DAT_005e4884, and also returns true for keys already present in that consumed-key queue. Static retail/source evidence only; exact key-table/queue layout, runtime input behavior, BEA patching, and rebuild parity remain deferred.",
                tags("input", "controller", "source-keyonce", "consumed-key-queue")
            ),
            new Spec(
                "0x00513b60",
                "D3DStateCache__ForceSlotMode4or5",
                "D3DStateCache__ForceSlotMode4or5",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("state_slot", intType) },
                "Wave850 static read-back/signature/comment hardening: forced state-cache mode helper called from CDXEngine__Render and CVBufTexture__SetStateCacheModeByFlag. It writes DAT_008557f4[state_slot*0x1e] to 5 when DAT_008554fc is non-zero, otherwise 4, then calls DAT_00888a50 vtable slot 0x10c with state_slot, state_id 1, and the chosen value. Static retail/source evidence only; exact texture-stage enum identity, runtime D3D state behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "state-cache", "vtable-0x10c", "force-mode")
            ),
            new Spec(
                "0x00513c70",
                "CEngine__DrawIndexedPrimitives",
                "CEngine__DrawIndexedPrimitives",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr), param("primitive_type", intType), param("arg2", intType),
                    param("arg3", intType), param("arg4", intType), param("arg5", intType)
                },
                "Wave850 static read-back/signature/comment hardening: Direct3D draw-indexed wrapper corresponding to source ltshell.h D3D_DrawIndexedPrimitive shape. The body calls the device at this+0x32ea0 vtable slot 0x148 with primitive_type, MinIndex forced to 0, and four caller values, then RET 0x14. Seventy-four xref-site instruction rows show callers do not consume EAX immediately after the wrapper. Static retail/source evidence only; exact Direct3D interface version/argument labels, runtime draw behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "draw-indexed", "source-reference-ltshell", "vtable-0x148")
            ),
            new Spec(
                "0x00513ca0",
                "CEngine__SetVertexShadersEnabled",
                "CEngine__SetVertexShadersEnabled",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("enabled", ucharType) },
                "Wave850 static read-back/signature/comment hardening: vertex-shader path toggle called by D3DStateCache__UseDefaultRenderState, mesh/landscape render paths, CDXEngine__ApplyPendingRenderState, and shader capability setup. When DAT_00889070 changes, it calls the device vtable slot 0x134 with enabled, clears DAT_0088906c, resets DAT_00889068 to 0x152, calls device slots 0x170 and 0x164, and returns the first device result; otherwise it returns 0. Static retail/source evidence only; exact Direct3D interface/version labels, runtime shader enablement behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "vertex-shader", "shader-path-toggle", "hresult")
            ),
            new Spec(
                "0x00513d20",
                "D3DBufferRegistry__MoveToFreeList",
                "D3DBufferRegistry__MoveToFreeList",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("buffer_node", intType) },
                "Wave850 static read-back/signature/comment hardening: D3D buffer registry list helper called from CFastVB__Create, CFastVB__Render, and CDXBitmapFont__Deserialize. It scans active list DAT_00889074 using node+4 links, unlinks the matching buffer_node when found, pushes it onto free list DAT_00889078 through node+4, and returns without change if the node is absent. Static retail evidence only; exact buffer-node layout, ownership contract, runtime resource lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "buffer-registry", "resource-lifetime", "free-list")
            ),
            new Spec(
                "0x00513e00",
                "CEngine__DeviceCall118_WithZeroOut",
                "CEngine__DeviceCall118_WithZeroOut",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave850 static read-back/signature/comment hardening: ECX-only device wrapper called from message-box, landscape validation, mesh, VBufTexture, and water render paths. The body creates a zeroed stack dword, passes its address to this+0x32ea0 vtable slot 0x118, and returns without exposing the device result. Static retail evidence only; exact Direct3D method identity, runtime device state behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "device-vtable-0x118", "stack-output")
            ),
            new Spec(
                "0x00513e20",
                "CEngine__SetShaderObject",
                "CEngine__SetShaderObject",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("shader_obj", voidPtr) },
                "Wave850 static read-back/signature/comment hardening: shader-object binding helper called by landscape shadow-map, mesh layer, particle, render-queue, pending-state, and water render paths. It caches shader_obj in DAT_0088906c with sentinel DAT_00889068=0xfedcba98, sends CVertexShader__GetVertexDeclarationToken(shader_obj) to device slot 0x164, sends shader_obj+0x28 to device slot 0x170, then calls CEngine__SetVertexShaderPathEnabled(0). Static retail/source evidence only; exact shader-object layout, Direct3D interface version, runtime shader behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "vertex-shader", "shader-object", "state-cache")
            ),
            new Spec(
                "0x00513e90",
                "CEngine__SetVertexShaderHandleCached",
                "CEngine__SetVertexShaderHandleCached",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("shader_handle", intType) },
                "Wave850 static read-back/signature/comment hardening: cached vertex-shader handle setter called by water and CDXSurf render paths. It compares shader_handle with DAT_00889068, skips the device call when unchanged, otherwise calls this+0x32ea0 vtable slot 0x164 with shader_handle and updates DAT_00889068. Static retail/source evidence only; exact shader-handle type, runtime shader behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "vertex-shader", "state-cache", "source-reference-ltshell")
            ),
            new Spec(
                "0x00513ec0",
                "CEngine__SetVertexShaderHandleRaw",
                "CEngine__SetVertexShaderHandleRaw",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("shader_handle", intType) },
                "Wave850 static read-back/signature/comment hardening: raw vertex-shader handle setter called by CFastVB render paths, CDXEngine__ApplyPendingRenderState, and CDXEngine__SetShaderMode. It clears DAT_0088906c when the handle or shader-object cache requires a transition, sends zero to device slot 0x170, sends shader_handle to device slot 0x164, then calls CEngine__SetVertexShaderPathEnabled(0). Static retail/source evidence only; exact shader-handle type, runtime shader behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "vertex-shader", "raw-state", "source-reference-ltshell")
            ),
            new Spec(
                "0x00513f20",
                "CEngine__CreatePixelShaderFromText",
                "CEngine__CreatePixelShaderFromText",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr), param("shader_text", charPtr), param("release_after_create", voidPtr) },
                "Wave850 static read-back/signature/comment hardening: pixel-shader creation helper called from DXParticleTexture__RestoreAll and two raw callsites guarded by shader-version checks. The body measures shader_text, calls CVertexShader__CompileScriptWithDirectiveParser, raises FatalError_LocalizedStringId(0,0xd2,500) on compile failure, calls this+0x32ea0 vtable slot 0x1a8 with compiled shader data/output, releases the local compile buffer when non-null, releases release_after_create when non-null, returns the device result, and RET 0x8. Static retail/source evidence only; exact compiler-buffer interface, Direct3D interface version, runtime shader compilation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "pixel-shader", "shader-compile", "hresult", "source-reference-ltshell")
            ),
            new Spec(
                "0x00513ff0",
                "CEngine__DeviceCall16C_Arg2Arg3",
                "CEngine__DeviceCall16C_CreateVertexShaderLike",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr), param("unused_arg1", intType), param("arg2", intType),
                    param("arg3", intType), param("unused_arg4", intType)
                },
                "Wave850 static read-back/name/signature correction: Direct3D device wrapper reached from CVertexShader__LoadCompiledShaderBlobFromVSOFile and shader setup callsites. Instruction evidence shows the wrapper cleans four caller stack arguments with RET 0x10, forwards only caller arg2 and arg3 to this+0x32ea0 vtable slot 0x16c, returns the device-call EAX value, and all three callsites test that result for failure. The CreateVertexShaderLike name is bounded: it reflects vertex-shader loader/callsite context and two-argument device-create shape, not proven exact Direct3D interface identity. Static retail/source evidence only; exact COM method name, argument schema, runtime shader creation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("direct3d-device", "vertex-shader", "device-vtable-0x16c", "hresult", "name-corrected")
            ),
            new Spec(
                "0x00514010",
                "IUnknown__ReleaseAndNull",
                "IUnknown__ReleaseAndNull",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("object_ptr", voidPtrPtr) },
                "Wave850 static read-back/signature/comment hardening: COM release-and-null helper called from DXParticleTexture render/release and CDXLandscape destructor/release paths. The body checks *object_ptr, calls vtable slot 8 Release when non-null, writes null back to *object_ptr, and RET 0x4. Static retail evidence only; exact interface type, ownership contract, runtime resource lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("com-release", "resource-lifetime", "release-and-null")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        if (!dryRun) {
            currentProgram.flushEvents();
            saveProgram(currentProgram);
            println("REPORT: Save succeeded");
        } else {
            println("REPORT: Dry run only; no changes saved");
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave850 D3D shader/input tail encountered missing/bad rows");
        }
    }
}
