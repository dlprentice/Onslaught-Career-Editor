//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyD3DApplicationShellWave572 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.parameters = parameters;
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

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
            "d3d-application-shell-wave572",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                stats.skipped++;
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
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

            println("OK: " + spec.address + " " + readBack.getSignature());
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
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00528f80",
                "CD3DApplication__Init",
                "__thiscall",
                voidPtr,
                "Wave572 signature/comment hardening: CD3DApplication constructor/init body. ECX is this, EAX returns this, it constructs ten adapter-info blocks, installs the vtable, stores global DAT_0089c0f4, clears device/window/ready/timer fields, sets D3D8 Application title text, and seeds 640x480 creation dimensions plus depth/cursor defaults. Static retail evidence only; exact CD3DApplication layout, exact source identity, runtime D3D behavior, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__Init"},
                tags("display", "d3d-application", "constructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x005290a0",
                "CD3DApplication__Create",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: CD3DApplication creation path. RET 0x4 confirms one stack argument after this; the body calls Direct3DCreate9(0x1f), builds the device list, registers/creates the D3D Window when needed, captures window rectangles, initializes the 3D environment, starts the perf timer, and marks the app ready. Static retail evidence only; exact window style semantics, runtime device creation behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__Create"},
                tags("display", "d3d-application", "window-create", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("hinstance", voidPtr)
                }
            ),
            new Spec(
                "0x00529350",
                "CD3DApplication__BuildDeviceList",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: retail D3D adapter/device/mode enumeration path. ECX is this; it queries adapter count and display modes, filters small/non-allowed modes, honors DAT_0089c0ac widescreen allowance, probes HAL/REF format behavior, depth-stencil, texture, and multisample support, records default/friendly mode indexes, warns through DisplayErrorMsg, and returns D3DAPP-style HRESULT values. Static retail evidence only; exact structure layout, exact mode-list contract, runtime hardware behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__BuildDeviceList"},
                tags("display", "d3d-application", "device-enumeration", "mode-list", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0052af00",
                "CD3DApplication__Initialize3DEnvironment",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: retail D3D environment create/reset path. RET 0x4 confirms one stack bool after this; the body applies cardid.txt/CVar tweaks, builds presentation parameters, applies screen-shape scaling, creates or resets the D3D device, falls back from lockable backbuffer/multisampling/friendly modes, updates device stats/backbuffer/cursor state, calls init/restore vfuncs, and can retry through the REF device. Static retail evidence only; exact presentation-parameter layout, runtime D3D behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__Initialize3DEnvironment"},
                tags("display", "d3d-application", "device-create-reset", "cardid", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reuse_existing_device", boolType)
                }
            ),
            new Spec(
                "0x0052b760",
                "CD3DApplication__Resize3DEnvironment",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: ECX-only resize/reset helper. It invalidates device objects through the vtable, resets the D3D device with presentation parameters at this+0x32e58, refreshes the backbuffer description, optionally installs the fullscreen cursor, restores device objects, and restarts/stops the perf timer when frame movement is paused. Static retail evidence only; exact object layout, runtime reset behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__Resize3DEnvironment"},
                tags("display", "d3d-application", "device-reset", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0052b840",
                "CD3DApplication__ToggleFullscreen",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: ECX-only fullscreen/windowed toggle. It selects the current adapter/device/mode, falls back through ForceWindowed when the active device cannot window, toggles this+0x32e44 and device windowed state, rebuilds presentation parameters, recomputes aspect scale from g_ScreenShape, calls Resize3DEnvironment, restores saved window bounds on windowed success, and returns D3D-style status. Static retail evidence only; runtime fullscreen/windowed behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__ToggleFullscreen"},
                tags("display", "d3d-application", "fullscreen-toggle", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0052ba50",
                "CD3DApplication__ForceWindowed",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: forced-windowed fallback helper. RET 0x4 proves one stack argument after this; it keeps the current device when its windowable flag matches target_windowed_state, otherwise scans adapters/devices for a compatible windowable entry, marks the app not ready, invalidates/deletes device objects, calls Initialize3DEnvironment with reuse_existing_device=true, and reports failures through DisplayErrorMsg. Static retail evidence only; runtime windowed recovery behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__ForceWindowed"},
                tags("display", "d3d-application", "force-windowed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("target_windowed_state", boolType)
                }
            ),
            new Spec(
                "0x0052bb80",
                "CD3DApplication__Reset3DEnvironment",
                "__thiscall",
                intType,
                "Wave572 signature/comment hardening: device-selection/reset path. RET 0x8 proves two stack arguments after this; when show_device_dialog is false it may toggle out of fullscreen, opens the SelectDeviceProc dialog, commits selected adapter/device/mode state on IDOK, invalidates device objects with reset_context, calls Initialize3DEnvironment with reuse_existing_device=true, and restarts timer state when paused. Static retail evidence only; exact dialog contract, runtime device reset behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__Reset3DEnvironment"},
                tags("display", "d3d-application", "device-reset", "dialog", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("show_device_dialog", boolType),
                    param("reset_context", intType)
                }
            ),
            new Spec(
                "0x0052bc80",
                "CD3DApplication__SelectDeviceProc",
                "__stdcall",
                intType,
                "Wave572 signature/comment hardening: Win32 dialog proc for D3D adapter/device/mode/MSAA selection. RET 0x10 confirms four stdcall arguments; WM_INITDIALOG snapshots current globals, WM_COMMAND handles OK/Cancel and combo-box changes, repopulates adapter/device/mode/multisample controls, and writes selected state through DAT_0089c048 before Reset3DEnvironment commits it. Static retail evidence only; exact dialog resource layout, runtime UI behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__SelectDeviceProc"},
                tags("display", "d3d-application", "device-dialog", "stdcall-callback", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("dialog_hwnd", intType),
                    param("message", intType),
                    param("wparam", intType),
                    param("lparam", intType)
                }
            ),
            new Spec(
                "0x0052c430",
                "CD3DApplication__Cleanup3DEnvironment",
                "__thiscall",
                voidType,
                "Wave572 signature/comment hardening: ECX-only D3D cleanup helper. It clears active/ready flags, invalidates/deletes device objects when a D3D device exists, releases DAT_0089c04c plus device and D3D interfaces, logs d3ddev/d3d refcount text through DebugTrace, nulls the interface pointers, and calls the final-cleanup vfunc. Static retail evidence only; exact COM lifetime behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__Cleanup3DEnvironment"},
                tags("display", "d3d-application", "cleanup", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0052c4f0",
                "CD3DApplication__DisplayErrorMsg",
                "__stdcall",
                intType,
                "Wave572 signature/comment hardening: D3DAPP-style error-to-localized-fatal dispatcher. RET 0x8 confirms two stack arguments; retail uses the HRESULT-like error code to select localized string ids 0xb6-0xc5 and returns the input code, while message_type is preserved in the signature for callsite stack shape even though this decompile does not use it directly. Static retail evidence only; exact localization text, runtime fatal-message UX, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__DisplayErrorMsg"},
                tags("display", "d3d-application", "error-dispatch", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("error_code", intType),
                    param("message_type", intType)
                }
            ),
            new Spec(
                "0x0052c730",
                "CD3DApplication__SetResolution",
                "__thiscall",
                voidType,
                "Wave572 signature/comment hardening: resolution setter used by CLIParams__ParseCommandLine. RET 0x8 confirms width and height stack arguments after this; the body stores width at this+0x330bc and height at this+0x330c0 without an in-function clamp. Static retail evidence only; command-line validation, runtime resolution behavior, exact layout, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__SetResolution"},
                tags("display", "d3d-application", "resolution", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("width", intType),
                    param("height", intType)
                }
            ),
            new Spec(
                "0x0052c780",
                "ScreenShape_UpdateAspectScale",
                "__fastcall",
                voidType,
                "Wave572 signature hardening: ECX-carried aspect-scale helper called after g_ScreenShape changes and in D3D create/toggle paths. It stores this+0x32e90 from current backbuffer height/width and g_ScreenShape: 16:9 uses 1.7777778, mode 2 forces 1.0, and the fallback uses 1.3333334. Static retail evidence only; exact viewport math contract, runtime widescreen behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"ScreenShape_UpdateAspectScale"},
                tags("display", "d3d-application", "aspect-scale", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("d3d_app", voidPtr)
                }
            ),
            new Spec(
                "0x0052c8d0",
                "CD3DApplication__SetDeviceCursorFromIcon",
                "__cdecl",
                intType,
                "Wave572 signature/comment hardening: icon-to-D3D cursor helper. It reads ICONINFO, creates a D3D surface through the supplied device pointer, extracts mask/color bitmap bits through GDI, merges alpha/mask pixels into temporary buffers, uploads cursor data, releases DCs/bitmaps/temp allocations, releases the cursor surface, and returns HRESULT-style status. Static retail evidence only; exact pixel conversion contract, runtime cursor behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__SetDeviceCursorFromIcon"},
                tags("display", "d3d-application", "cursor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("d3d_device", voidPtr),
                    param("icon_handle", intType)
                }
            ),
            new Spec(
                "0x0052cd20",
                "CD3DApplication__PerfTimerCommand",
                "__stdcall",
                doubleType,
                "Wave572 signature/comment hardening: D3D application timer command helper. RET 0x4 confirms one stack command argument; command values start, stop, advance, get absolute time, get app time, or get elapsed time using QueryPerformanceCounter when available and falling back to timeGetTime-backed doubles otherwise. Static retail evidence only; exact timer semantics, runtime frame pacing behavior, exact source identity, and rebuild parity remain unproven.",
                new String[] {"CD3DApplication__PerfTimerCommand"},
                tags("display", "d3d-application", "perf-timer", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("command", intType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave572 D3D application shell tranche failed");
        }
    }
}
