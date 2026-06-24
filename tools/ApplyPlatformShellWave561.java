//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyPlatformShellWave561 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "platform-shell-wave561",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
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

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        if (spec.params.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }
            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        DataType voidType = VoidDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00512130",
                "CLTShell__WinMain",
                "CLTShell__WinMain",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("module_handle", voidPtr()),
                    param("previous_instance", voidPtr()),
                    param("command_line", charPtr),
                    param("show_command", intType)
                },
                "Wave561 signature/comment hardening: the CRT entry passes four WinMain-style stack arguments and this function returns with RET 0x10. The body installs the unhandled-exception log filter, reads version and system-parameter settings, parses the command line, loads defaultoptions.bea through CCareer::Load(flag=0), blanks CAREER, creates the D3D application, initializes runtime resources, runs the frontend/game loop, then tears down D3D/window resources. Static retail-binary evidence only; exact CLTShell/global layout, runtime launch behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ltshell", "startup", "winmain", "signature-recovered")
            ),
            new Spec(
                "0x00512470",
                "PlatformInput__ClearTransientKeyStateTable",
                "PlatformInput__ClearTransientKeyStateTable",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave561 signature/comment hardening: CFrontEnd__Process and CGame__Update call this with ECX set to the platform singleton at 0x00855bb0. The body clears the 0x100-byte transient key-state table at this+0x332e4 with 0x40 dword stores. Static retail-binary evidence only; exact platform/input table layout, runtime input behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("platform-input", "key-state", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x00512490",
                "PLATFORM__ProcessSystemMessages",
                "PLATFORM__ProcessSystemMessages",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("poll_pad_edges", boolType)
                },
                "Wave561 signature/comment hardening: PLATFORM__Process passes the platform singleton in ECX and one stack byte flag. The body chooses GetMessageA or PeekMessageA, routes accelerator/TranslateMessage/DispatchMessage handling, recovers from D3D device-loss through CD3DApplication__Reset3DEnvironment, updates perf-timer fields, then polls four pad states with the stack flag. Static retail-binary evidence only; exact PLATFORM field layout, runtime message-pump/input behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("platform", "message-pump", "device-reset", "input-poll", "phantom-param-removed", "signature-recovered")
            ),
            new Spec(
                "0x00512630",
                "Platform__HandleDeviceLostAndRestore",
                "Platform__HandleDeviceLostAndRestore",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave561 signature/comment hardening: PCPlatform__DeviceFlip calls this with ECX set to the platform singleton. The body invokes the D3D device TestCooperativeLevel-style vfunc at this+0x32ea0 slot 0x44, waits in 100 ms sleeps while the global device reports not-ready, then sets DAT_0082b5b0 after restoration. Static retail-binary evidence only; exact Direct3D interface identity, runtime device-loss behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("platform", "direct3d", "device-loss", "signature-recovered")
            ),
            new Spec(
                "0x00512670",
                "PCLTShell__ctor",
                "PCLTShell__ctor_like_00512670",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave561 rename/signature/comment hardening: the global initialization thunk calls this with ECX=0x00855bb0, then the body initializes the CD3DApplication base path, installs the PCLTShell vtable at 0x005e488c, clears per-player input/shell fields, copies the Battle Engine Aquila window title, and returns this. Static retail-binary evidence only; exact CLTShell class layout, constructor source identity, runtime launch behavior, BEA patching, and rebuild parity remain unproven.",
                tags("ltshell", "constructor", "direct3d", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00512c40",
                "PCLTShell__ConfirmDevice",
                "PCLTShell__VFunc_01_00512c40",
                "__stdcall",
                intType,
                new ParameterImpl[] {
                    param("d3d_caps", voidPtr()),
                    param("behavior_flags", uintType)
                },
                "Wave561 rename/signature/comment hardening: PCLTShell vtable slot 1 points here. The body accepts devices only when D3D caps report texture dimensions above 255, rejects unsupported vertex-shader/caps combinations with E_FAIL (0x80004005), conditionally logs the software vertex-shader path, and returns S_OK on accepted caps. Static retail-binary evidence only; exact D3DCAPS field names, runtime adapter selection behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("ltshell", "direct3d", "confirm-device", "vtable-slot", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00512ca0",
                "CShaderBase__Init",
                "CShaderBase__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave561 signature/comment hardening: CVBuffer, CIBuffer, CVertexShader, CDXLandscape, CUMTexture, CDXMeshVB, CDXShadows, CTexture, CDXTrees, and CWaterRenderSystem constructors call this on the object being initialized. The body prepends this into the global render/device-object list rooted at DAT_00889074 by writing the previous head to this+0x04 and then updating the head. Static retail-binary evidence only; exact CShaderBase/device-object layout, runtime Direct3D behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("shader-base", "device-object", "render-list", "signature-recovered")
            ),
            new Spec(
                "0x00512cc0",
                "CShaderBase__UnlinkFromRenderObjectLists",
                "CDXLandscape__UnlinkNodeFromPrimaryAndSecondaryLists",
                "__stdcall",
                uintType,
                new ParameterImpl[] {
                    param("render_object", voidPtr())
                },
                "Wave561 rename/signature/comment hardening: destructors/resets for CUMTexture, CDXTrees, CIBuffer, CVBuffer, CVertexShader, CDXSurf, CDXLandscape, CDXShadows, CDXMeshVB, and CWaterRenderSystem call this with the object pointer on the stack. The body scans both global render/device-object lists at DAT_00889074 and DAT_00889078, unlinks the matching object by its +0x04 next pointer, and returns the OR of the two list-hit flags. Static retail-binary evidence only; exact CShaderBase/device-object list semantics, runtime Direct3D behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("shader-base", "device-object", "render-list", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00512dc0",
                "DeviceObject__scalar_deleting_dtor",
                "DeviceObject__VFunc_00_00512dc0",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("flags", byteType)
                },
                "Wave561 rename/signature/comment hardening: DeviceObject vtable slot 0 at 0x005e48c8 points here. The body restores the base DeviceObject vtable, removes this from both global render/device-object lists rooted at DAT_00889074 and DAT_00889078, frees this through CDXMemoryManager when flags bit 0 is set, and returns this. Static retail-binary evidence only; exact DeviceObject layout, runtime Direct3D behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("device-object", "scalar-deleting-dtor", "render-list", "renamed", "signature-recovered")
            ),
            new Spec(
                "0x00512fc0",
                "PlatformInput__ClearAllKeyStateTables",
                "PlatformInput__ClearAllKeyStateTables",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr())
                },
                "Wave561 signature/comment hardening: PlatformInput__ResetKeyStateTables calls this with ECX set to the platform singleton at 0x00855bb0. The body clears three adjacent 0x100-byte key-state tables at this+0x330e4, this+0x331e4, and this+0x332e4. Static retail-binary evidence only; exact platform/input table layout, runtime input behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("platform-input", "key-state", "signature-recovered")
            )
        };

        Stats stats = new Stats();
        println("ApplyPlatformShellWave561 mode=" + (dryRun ? "dry" : "apply") + " targets=" + specs.length);
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply") +
            " updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (stats.bad != 0 || stats.missing != 0) {
            throw new IllegalStateException("Wave561 had bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
