//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyD3DApplicationWindowDepthWave862 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedName;
        final String expectedPrototype;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String expectedName, String expectedPrototype, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedPrototype = expectedPrototype;
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
            "d3dapplication-window-depth-wave862",
            "wave862-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "important-connective-infrastructure"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Spec commentOnly(String address, String name, String prototype, String comment, String... extraTags) {
        return new Spec(address, name, prototype, null, null, null, comment, tags(extraTags));
    }

    private Spec signature(String address, String name, String prototype, String convention,
            DataType returnType, ParameterImpl[] parameters, String comment, String... extraTags) {
        String[] combined = new String[extraTags.length + 1];
        combined[0] = "signature-hardened";
        System.arraycopy(extraTags, 0, combined, 1, extraTags.length);
        return new Spec(address, name, prototype, convention, returnType, parameters, comment, tags(combined));
    }

    private Spec[] specs() throws Exception {
        DataType boolType = BooleanDataType.dataType;
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType voidPtr = new PointerDataType(VoidDataType.dataType);
        DataType intPtr = new PointerDataType(IntegerDataType.dataType);

        return new Spec[] {
            signature(
                "0x0052a830",
                "CD3DApplication__FindDepthStencilFormat",
                "bool CD3DApplication__FindDepthStencilFormat(void * this, uint adapter_index, int device_type, int target_format, int * out_depth_stencil_format)",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("adapter_index", uintType),
                    param("device_type", intType),
                    param("target_format", intType),
                    param("out_depth_stencil_format", intPtr)
                },
                "Wave862 static read-back/signature correction: source-aligned CD3DApplication depth/stencil format selector called only from CD3DApplication__BuildDeviceList at 0x00529f8f. Retail body is __thiscall with ECX=this and RET 0x10; reads this+0x330b4/this+0x330b8 min depth/stencil requirement fields and this+0x32e9c Direct3D object pointer; tests observed D3DFORMAT candidate constants through device vtable slots +0x28/+0x30 (CheckDeviceFormat/CheckDepthStencilMatch-like), writes the accepted value through out_depth_stencil_format, and returns true/false. Static retail/source-reference evidence only; exact CD3DApplication layout, exact D3D enum semantics, runtime device-selection behavior, BEA patching, and rebuild parity remain unproven.",
                "d3d",
                "device-list",
                "depth-stencil",
                "source-aligned"
            ),
            commentOnly(
                "0x0052aaf0",
                "CD3DApplication__MsgProc",
                "int CD3DApplication__MsgProc(void * this, void * hwnd, uint msg, uint wparam, int lparam)",
                "Wave862 static read-back/comment hardening: base CD3DApplication window-message handler with DATA vtable ref 0x005e4ae4 and raw WndProc-style callsite 0x00512fb5; source reference d3dapp.cpp MsgProc plus PCLTShell::MsgProc forwarding. Handles min-track-size, active/windowed flags, fullscreen cursor suppression, command/system-command filters, mouse-move client-coordinate forwarding, timer stop/start around sizing/move, client-size changes through CD3DApplication__Resize3DEnvironment, retail msg 0x10 reset marking via CEngine__MarkDeviceResetPending, and fallback DefWindowProcA. Static retail/source-reference evidence only; exact CD3DApplication layout, exact Windows-message labels for every numeric constant, runtime window/device-loss behavior, BEA patching, and rebuild parity remain unproven.",
                "d3d",
                "window-message",
                "device-reset",
                "source-aligned"
            )
        };
    }

    private Set<String> currentTags(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, String[] expected) {
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean applyTags(Function fn, String[] expected, boolean dryRun) {
        boolean changed = false;
        Set<String> actual = currentTags(fn);
        for (String tag : expected) {
            if (!actual.contains(tag)) {
                changed = true;
                if (!dryRun) {
                    fn.addTag(tag);
                }
            }
        }
        return changed;
    }

    private boolean conventionOk(Function fn, String expectedConvention) throws Exception {
        if (expectedConvention == null) {
            return true;
        }
        return expectedConvention.equals(fn.getCallingConventionName());
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address + " " + spec.expectedName);
            stats.missing++;
            stats.bad++;
            return;
        }

        boolean nameOk = fn.getName().equals(spec.expectedName);
        boolean prototypeOk = fn.getSignature().getPrototypeString().equals(spec.expectedPrototype);
        boolean conventionOk = conventionOk(fn, spec.callingConvention);
        boolean signatureOk = prototypeOk && conventionOk;
        boolean commentOk = spec.comment.equals(fn.getComment());
        boolean tagsOk = hasAllTags(fn, spec.tags);
        boolean canUpdateSignature = spec.callingConvention != null;

        if (!nameOk && !dryRun) {
            fn.setName(spec.expectedName, SourceType.USER_DEFINED);
        }
        if (!nameOk) {
            stats.wouldRename++;
            if (!dryRun) {
                stats.renamed++;
            }
        }

        if (!signatureOk && canUpdateSignature) {
            if (!dryRun) {
                fn.setCallingConvention(spec.callingConvention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
            }
            stats.signatureUpdated++;
        } else if (!signatureOk) {
            println("BADSIG: " + spec.address + " expected=" + spec.expectedPrototype + " convention=" + spec.callingConvention + " actual=" + fn.getSignature().getPrototypeString() + " convention=" + fn.getCallingConventionName());
            stats.bad++;
        }

        if (!commentOk && !dryRun) {
            fn.setComment(spec.comment);
        }
        if (!tagsOk) {
            applyTags(fn, spec.tags, dryRun);
        }

        if (commentOk && tagsOk && signatureOk && nameOk) {
            stats.skipped++;
            println("SKIP_OK: " + spec.address + " " + spec.expectedName);
        } else {
            stats.updated++;
            if (signatureOk || !canUpdateSignature) {
                stats.commentOnlyUpdated++;
            }
            println((dryRun ? "DRY_UPDATE: " : "APPLY_UPDATE: ") + spec.address + " " + spec.expectedName);
        }

        if (!dryRun) {
            Function readback = functionAtEntry(spec.address);
            String actualSignature = readback.getSignature().getPrototypeString();
            boolean readbackOk = readback.getName().equals(spec.expectedName)
                && actualSignature.equals(spec.expectedPrototype)
                && conventionOk(readback, spec.callingConvention)
                && spec.comment.equals(readback.getComment())
                && hasAllTags(readback, spec.tags);
            if (readbackOk) {
                println("READBACK_OK: " + spec.address + " " + actualSignature + " convention=" + readback.getCallingConventionName());
            } else {
                println("READBACK_BAD: " + spec.address + " name=" + readback.getName() + " signature=" + actualSignature + " convention=" + readback.getCallingConventionName());
                stats.bad++;
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        for (Spec spec : specs()) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
    }
}
