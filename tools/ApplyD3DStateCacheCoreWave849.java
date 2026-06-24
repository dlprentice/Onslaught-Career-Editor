//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
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

public class ApplyD3DStateCacheCoreWave849 extends GhidraScript {
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
            "d3d-state-cache-core-wave849",
            "wave849-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-hardened",
            "source-reference-ltshell",
            "direct3d-device"
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

        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00513640",
                "CEngine__GetConstant32",
                "CEngine__GetConstant32",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave849 static read-back/signature/comment hardening: constant helper returning 0x20. Xrefs are texture/resource paths including CDXTexture__Deserialize, CDXTexture__LoadTextureFromFile_Core, and CTextureSequence__EnsureLoaded. Static retail evidence only; exact semantic name for the 0x20 constant, texture policy meaning, runtime texture behavior, BEA patching, and rebuild parity remain deferred.",
                tags("engine-constant", "texture-resource")
            ),
            new Spec(
                "0x00513650",
                "CEngine__PrintGraphicsCardInfo",
                "CEngine__PrintGraphicsCardInfo",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave849 static read-back/signature/comment hardening: console graphics-card report matching source ltshell.cpp con_whatami/cg_whatami text. The body prints separator, Graphics card info, Description, Driver, Driver version, chooses Using pure device or Using impure device from DAT_00662f04, then prints a blank line. Static retail/source evidence only; exact adapter structure fields, runtime console command behavior, BEA patching, and rebuild parity remain deferred.",
                tags("graphics-card-info", "console-command", "source-con-whatami")
            ),
            new Spec(
                "0x00513730",
                "CEngine__MarkDeviceResetPending",
                "CEngine__MarkDeviceResetPending",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave849 static read-back/signature/comment hardening: device-reset/lost-device state marker reached from CD3DApplication__MsgProc. The body sets 0x008a9acc to 1, promotes 0x008a9ac0 to 9 when the prior value is below 4, and writes 0xffffffff to 0x008a956c. Source ltshell.cpp/d3dapp.cpp nearby evidence describes TestCooperativeLevel and D3DERR_DEVICELOST handling, but this saved claim is static retail state writes only; exact state-machine labels, runtime reset behavior, BEA patching, and rebuild parity remain deferred.",
                tags("device-reset", "lost-device", "state-machine")
            ),
            new Spec(
                "0x00513760",
                "CEngine__ReleaseField32FD4",
                "CEngine__TextureFormatField32FD4ToIndex",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave849 static read-back/name/signature correction: ECX-only helper loads the D3D texture-format field at this+0x32fd4 and calls CEngine__TextureFormatD3DToIndex. Callers use EAX as a texture-format index in CUMTexture__RecreateTextureResource, CDXTexture__LoadTextureFromFile_Core, and CTextureSequence__EnsureLoaded, so the old ReleaseField32FD4 name was misleading. Static retail evidence only; exact CEngine field name, full texture-format table semantics, runtime texture behavior, BEA patching, and rebuild parity remain deferred.",
                tags("name-corrected", "texture-format", "texture-resource")
            ),
            new Spec(
                "0x00513770",
                "CEngine__DeviceCall68_CheckError",
                "CEngine__DeviceCall68_CheckError",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr), param("arg2", intType), param("arg3", intType),
                    param("arg4", intType), param("arg5", intType), param("arg6", intType)
                },
                "Wave849 static read-back/signature/comment hardening: Direct3D device wrapper dispatches through this+0x32ea0 vtable slot 0x68 with five caller arguments plus trailing zero, returns the HRESULT-like value, and on failure logs D3D Error!, HResultToString, OutputDebugStringA, and a newline DebugTrace. Xrefs are mesh/vertex-buffer restore/create paths. Static retail/source evidence only; exact COM method identity, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("device-vtable-0x68", "hresult", "error-logging", "mesh-vbuffer")
            ),
            new Spec(
                "0x005137d0",
                "CEngine__DeviceCall6C",
                "CEngine__DeviceCall6C",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr), param("arg2", intType), param("arg3", intType),
                    param("arg4", intType), param("arg5", intType), param("arg6", intType)
                },
                "Wave849 static read-back/signature correction: unchecked Direct3D device wrapper dispatches through this+0x32ea0 vtable slot 0x6c with five caller arguments plus trailing zero and returns the HRESULT-like EAX value. Callsite instructions in CIBuffer__CreateDynamic, CIBuffer__CreateStatic, CDXMeshVB__BuildStaticVB, and CDXMeshVB__BuildSkeletalVB test EAX after the call. Static retail evidence only; exact COM method identity, runtime buffer behavior, BEA patching, and rebuild parity remain deferred.",
                tags("device-vtable-0x6c", "hresult", "buffer-create", "signature-corrected")
            ),
            new Spec(
                "0x00513800",
                "IUnknown__ReleaseIfNonNull_ReturnZero",
                "IUnknown__ReleaseIfNonNull_ReturnZero",
                "__stdcall",
                intType,
                new ParameterImpl[] { param("obj", voidPtr) },
                "Wave849 static read-back/signature/comment hardening: COM release helper checks obj for null, calls obj->vtable[8] when non-null, and returns zero. Xrefs are CVBuffer destructor/release paths and CDXMeshVB__ReleaseResources. Static retail evidence only; exact interface type, ownership contract, runtime resource lifetime behavior, BEA patching, and rebuild parity remain deferred.",
                tags("com-release", "resource-lifetime", "returns-zero")
            ),
            new Spec(
                "0x00513820",
                "D3DStateCache__SetStateCached",
                "D3DStateCache__SetStateCached",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("state_slot", intType), param("state_id", intType), param("value", intType) },
                "Wave849 static read-back/signature/comment hardening: cached texture-stage/render-state helper indexes DAT_008557f0 by state_id + state_slot*0x1e, skips the device call when the cached value already matches, otherwise updates the cache and calls DAT_00888a50 vtable slot 0x10c with state_slot/state_id/value. It has 419 xref rows across console, HUD, frontend, landscape, mesh, particle, water, and CDXEngine render paths. Static retail/source evidence only; exact state enum names, cache layout, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("state-cache", "vtable-0x10c", "render-state")
            ),
            new Spec(
                "0x00513870",
                "D3DStateCache__SetStateRaw",
                "D3DStateCache__SetStateRaw",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("state_slot", intType), param("state_id", intType), param("value", intType) },
                "Wave849 static read-back/signature/comment hardening: raw state helper writes DAT_008557f0[state_id + state_slot*0x1e] and always calls DAT_00888a50 vtable slot 0x10c with state_slot/state_id/value. Xrefs include default-state setup, landscape terrain, mesh layer passes, and CDXEngine pending render-state application. Static retail/source evidence only; exact state enum names, cache layout, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("state-cache", "vtable-0x10c", "raw-state")
            ),
            new Spec(
                "0x005138b0",
                "D3DStateCache__SetState114Cached",
                "D3DStateCache__SetState114Cached",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("state_slot", intType), param("state_id", intType), param("value", uintType) },
                "Wave849 static read-back/signature/comment hardening: policy-gated state helper for DAT_00888a50 vtable slot 0x114. It suppresses state_id 6 value 3 when DAT_00888a78 lacks flag 0x20000, always suppresses state_id 8, clamps state_id 10 through DAT_00888ac0 unless the same cap flag allows the caller value, writes DAT_008557f0[state_id + state_slot*0x1e], and calls slot 0x114. Source ltshell.h has SetTextureStageState/ForceTS wrappers for this class of operation. Static retail/source evidence only; exact D3D texture-stage enum names, capability-bit identity, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("state-cache", "vtable-0x114", "texture-stage-policy")
            ),
            new Spec(
                "0x00513930",
                "D3DStateCache__SetState114Raw",
                "D3DStateCache__SetState114Raw",
                "__stdcall",
                voidType,
                new ParameterImpl[] { param("state_slot", intType), param("state_id", intType), param("value", uintType) },
                "Wave849 static read-back/signature/comment hardening: raw policy-gated vtable slot 0x114 helper. It applies the same state_id 6/8/10 capability and clamp rules as D3DStateCache__SetState114Cached, but does not update DAT_008557f0 before calling DAT_00888a50 slot 0x114. It has 192 xref rows across frontend, HUD, CDXEngine render/postrender, landscape, imposter, particles, water, and tree render paths. Static retail/source evidence only; exact D3D texture-stage enum names, capability-bit identity, runtime D3D behavior, BEA patching, and rebuild parity remain deferred.",
                tags("state-cache", "vtable-0x114", "raw-policy-state")
            ),
            new Spec(
                "0x005139a0",
                "CEngine__CreateTextureOrFatal",
                "CEngine__CreateTextureOrFatal",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr), param("arg2", intType), param("arg3", intType),
                    param("arg4", intType), param("arg5", intType), param("arg6", intType),
                    param("arg7", intType), param("arg8", intType)
                },
                "Wave849 static read-back/signature/comment hardening: texture-create wrapper dispatches through this+0x32ea0 vtable slot 0x5c with seven caller arguments plus trailing zero, returns the HRESULT-like value, and on failure prints Create texture failed: %s through CConsole__Printf after HResultToString before FatalError_LocalizedStringId(0, 0xca, -1). Xrefs include CDXTexture__LoadTextureFromFile_Core and CTextureSequence__EnsureLoaded. Source ltshell.h D3D_CreateTexture is the source-reference analogue. Static retail/source evidence only; exact texture argument schema, runtime allocation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("texture-create", "device-vtable-0x5c", "fatal-on-failure")
            ),
            new Spec(
                "0x00513a10",
                "CEngine__CreateTextureUnchecked",
                "CEngine__CreateTextureUnchecked",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr), param("arg2", intType), param("arg3", intType),
                    param("arg4", intType), param("arg5", intType), param("arg6", intType),
                    param("arg7", intType), param("arg8", intType)
                },
                "Wave849 static read-back/signature correction: unchecked texture-create wrapper dispatches through this+0x32ea0 vtable slot 0x5c with seven caller arguments plus trailing zero and returns the HRESULT-like EAX value. Callsite instructions in CDXTexture__Deserialize, CDXTexture__CreateMipmaps, CUMTexture__RecreateTextureResource, and CDXTexture__LoadTextureFromFile_Core test EAX after the call. Source ltshell.h D3D_CreateTexture is the source-reference analogue. Static retail/source evidence only; exact texture argument schema, runtime allocation behavior, BEA patching, and rebuild parity remain deferred.",
                tags("texture-create", "device-vtable-0x5c", "hresult", "signature-corrected")
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
            throw new RuntimeException("Wave849 D3D state/cache core encountered missing/bad rows");
        }
    }
}
