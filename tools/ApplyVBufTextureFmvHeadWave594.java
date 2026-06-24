//@category Symbol

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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyVBufTextureFmvHeadWave594 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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
            "vbuftexture-fmv-head-wave594",
            "retail-binary-evidence",
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
        Set<String> existing = tagNames(fn);
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
        Set<String> readBackTags = tagNames(readBack);
        for (String tag : spec.tags) {
            if (!readBackTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
            }
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
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + expectedSignature(spec));
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
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
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0053f040",
                "CVBufTexture__SetStateCacheModeByFlag",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("state_cache_mode_flag", intType)
                },
                "Wave594 signature/comment hardening: CVBufTexture render-state helper called twice by CVBufTexture__RenderAndRestoreStateFlag4. RET 0x4 proves one stack flag; nonzero dispatches D3DStateCache__ForceSlotMode4or5(0), while zero marks state-cache slot/group 4 through D3DStateCache__SetStateCached(0,1,4). Static retail evidence only; exact D3D state enum names, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CVBufTexture__SetStateCacheModeByFlag"},
                tags("cvbuftexture", "d3d-state-cache", "ret-0x4")
            ),
            new Spec(
                "0x0053f0a0",
                "CDXFMV__DestructorBody",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave594 signature/comment hardening: CDXFMV destructor body reached by CDXFMV__scalar_deleting_dtor and the raw atexit-style thunk at 0x0053f090. ECX carries this; the SEH-wrapped body tears down the embedded video/device object at this+0x10, then calls CMonitor__Shutdown(this). Static retail evidence only; exact CDXFMV layout, exception-handler semantics, runtime FMV teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFMV__DestructorBody"},
                tags("dxfmv", "destructor-body", "monitor-shutdown")
            ),
            new Spec(
                "0x0053f0f0",
                "CDXFMV__ctor_base",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave594 name/signature/comment hardening: CDXFMV constructor body reached by the raw initializer at 0x0053f070 for global object DAT_0089d690. ECX carries this; the body clears this+0x04, installs the base CFMV vtable 0x005e5018, constructs the embedded CDXFrontEndVideo object at this+0x10, installs the CDXFMV vtable 0x005e4fe4, and returns this. Static retail evidence only; exact CFMV/CDXFMV class layouts, global lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CFMV__ctor_like_0053f0f0", "CDXFMV__ctor_base"},
                tags("dxfmv", "constructor", "global-fmv-object", "owner-corrected")
            ),
            new Spec(
                "0x0053f140",
                "CDXFMV__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                },
                "Wave594 name/signature/comment hardening: CDXFMV vtable 0x005e4fe4 slot 1 points here. The wrapper calls CDXFMV__DestructorBody(this), optionally frees this through CDXMemoryManager__Free when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail evidence only; exact virtual name, allocator ownership, runtime FMV destruction behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFMV__VFunc_01_0053f140", "CDXFMV__scalar_deleting_dtor"},
                tags("dxfmv", "scalar-deleting-dtor", "vtable-slot-1", "ret-0x4", "phantom-param-removed", "owner-corrected")
            ),
            new Spec(
                "0x0053f160",
                "VFuncSlot_01_0053f160",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                },
                "Wave594 signature/comment hardening: shared vtable slot-1 deleting-destructor wrapper referenced by multiple data/vtable slots, including the CFMV/base table at 0x005e5018. The wrapper calls CMonitor__Shutdown_Thunk(this), optionally frees this through CDXMemoryManager__Free when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail evidence only; concrete owning class names for all table xrefs, allocator ownership, runtime teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_01_0053f160"},
                tags("shared-vfunc-slot", "scalar-deleting-dtor-shape", "monitor-shutdown", "ret-0x4", "phantom-param-removed", "owner-unresolved")
            ),
            new Spec(
                "0x0053f180",
                "CDXFMV__VFunc_06_0053f180",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave594 signature/comment hardening: no-argument CDXFMV vtable slot 6 / direct runtime-init helper. CLTShell__InitializeRuntimeAndLoadCoreResources calls it in the FMV init timing block, and the body loads the PCPlatform singleton into ECX before tail-jumping to PlatformInput__ResetKeyStateTables. Static retail evidence only; exact virtual purpose, platform input side effects, runtime FMV initialization behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFMV__VFunc_06_0053f180"},
                tags("dxfmv", "vtable-slot-6", "platform-input", "tail-jump", "no-params")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave594 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
