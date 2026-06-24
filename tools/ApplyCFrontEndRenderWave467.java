//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCFrontEndRenderWave467 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.oldName = oldName;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
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
            "cfrontend-render-wave467",
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
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.name)) {
                throw new IllegalStateException(
                    "Unexpected function name at " + spec.address + ": " + fn.getName()
                );
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
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

            Function readBack = functionAtEntry(spec.address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            String expectedSignature = expectedSignature(spec);
            if (!actualSignature.equals(expectedSignature)) {
                throw new IllegalStateException(
                    "Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature
                );
            }
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004662a0",
                "CFrontEnd__Init",
                "CFrontEnd__Init",
                "__thiscall",
                intType,
                "Wave467 correction: CFrontEnd startup initializer matching source CFrontEnd::Init(EFrontEndEntry, BOOL) at the coarse control-flow level: loading ranges, shared frontend resources, page table wiring, controller allocation, initial page selection, language text set initialization, and frontend music start. Static retail-binary/source-bridge evidence only; exact CFrontEnd layout, page enum values, platform-specific source identity, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("frontend", "source-bridge", "initialization", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("entry", intType),
                    param("in_loaded_system", intType)
                }
            ),
            new Spec(
                "0x00466990",
                "CFrontEnd__NumControllersPresent",
                "CFrontEnd__NumControllersPresent",
                "__thiscall",
                intType,
                "Wave467 correction: Retail PC frontend controller-count helper that returns fixed value 2 at call sites guarded by FRONTEND in ECX. Source CFrontEnd::NumControllersPresent counts present controllers, so this is source-adjacent naming only; runtime controller detection behavior and rebuild parity remain unproven.",
                tags("frontend", "controllers", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00466de0",
                "CFrontEnd__DrawLine",
                "CFrontEnd__DrawLine",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend line sprite helper matching source CFrontEnd::DrawLine stack cleanup and parameter order for endpoints, ARGB color, width, depth, and percent length; retail body computes angle/scale and draws the level-link surface. Static retail-binary/source-bridge evidence only; exact texture ids, render-state side effects, runtime visual behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("sx", floatType),
                    param("sy", floatType),
                    param("ex", floatType),
                    param("ey", floatType),
                    param("argb", uintType),
                    param("width", floatType),
                    param("depth", floatType),
                    param("percent", floatType)
                }
            ),
            new Spec(
                "0x00466e70",
                "CFrontEnd__DrawBox",
                "CFrontEnd__DrawBox",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend box outline helper matching source CFrontEnd::DrawBox stack cleanup and parameter order for top-left/bottom-right bounds, ARGB color, width, and depth; retail body inlines four line-sprite draws. Static retail-binary/source-bridge evidence only; exact texture ids, render-state side effects, runtime visual behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tlx", floatType),
                    param("tly", floatType),
                    param("brx", floatType),
                    param("bry", floatType),
                    param("argb", uintType),
                    param("width", floatType),
                    param("depth", floatType)
                }
            ),
            new Spec(
                "0x00467010",
                "CFrontEnd__DrawPanel",
                "CFrontEnd__DrawPanel",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend blank-panel helper matching source CFrontEnd::DrawPanel stack cleanup and parameter order for bounds, depth, and ARGB color; retail body clamps texture addressing, renders the blank panel surface, then restores wrapping. Static retail-binary/source-bridge evidence only; exact texture ids, render-state side effects, runtime visual behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tlx", floatType),
                    param("tly", floatType),
                    param("brx", floatType),
                    param("bry", floatType),
                    param("depth", floatType),
                    param("argb", uintType)
                }
            ),
            new Spec(
                "0x004670b0",
                "CFrontEnd__DrawBarGraph",
                "CFrontEnd__DrawBarGraph",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend bar-graph helper matching source CFrontEnd::DrawBarGraph stack cleanup and parameter order for bounds, numerator/max values, depth, border color, background color, and foreground color; retail body inlines panel rendering for background and nonzero filled bar. Static retail-binary/source-bridge evidence only; exact color semantics, runtime visual behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tlx", floatType),
                    param("tly", floatType),
                    param("brx", floatType),
                    param("bry", floatType),
                    param("num", floatType),
                    param("max", floatType),
                    param("depth", floatType),
                    param("border_argb", uintType),
                    param("back_argb", uintType),
                    param("fore_argb", uintType)
                }
            ),
            new Spec(
                "0x004679e0",
                "CFrontEnd__RenderPreCommonFade",
                "CFrontEnd__RenderPreCommonFade",
                "__stdcall",
                voidType,
                "Wave467 correction: Frontend/page pre-common fade helper that clamps transition-derived alpha, combines it with an incoming ARGB color, and renders a full-window/video quad. Static retail-binary evidence only; exact page ownership, color-channel intent, runtime transition visuals, source identity, and rebuild parity remain unproven.",
                tags("frontend", "pre-common-render", "fade", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("transition", floatType),
                    param("argb", uintType),
                    param("destination_page", intType)
                }
            ),
            new Spec(
                "0x00467ae0",
                "CFrontEnd__DrawBar",
                "CFrontEnd__DrawBar",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend header/bar strip helper matching source CFrontEnd::DrawBar stack cleanup and parameter order for start position, depth, segment count, ARGB color, and scale; retail body selects left/center/right bar textures while rendering segment_count + 2 sprites. Static retail-binary/source-bridge evidence only; exact texture ids, runtime visual behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-helper", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("sx", floatType),
                    param("sy", floatType),
                    param("depth", floatType),
                    param("segment_count", intType),
                    param("argb", uintType),
                    param("scale", floatType)
                }
            ),
            new Spec(
                "0x004681c0",
                "CFrontEnd__EnableAdditiveAlpha",
                "CFrontEnd__EnableAdditiveAlpha",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend blend-state helper matching source CFrontEnd::EnableAdditiveAlpha, setting source and destination blend to additive/one-style values in retail render state. Static retail-binary/source-bridge evidence only; exact render-state enum names, runtime blending behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-state", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004681e0",
                "CFrontEnd__EnableModulateAlpha",
                "CFrontEnd__EnableModulateAlpha",
                "__thiscall",
                voidType,
                "Wave467 correction: Frontend blend-state helper matching source CFrontEnd::EnableModulateAlpha, restoring source-alpha/inverse-source-alpha style blending in retail render state. Static retail-binary/source-bridge evidence only; exact render-state enum names, runtime blending behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-state", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004684d0",
                "CFrontEnd__Run",
                "CFrontEnd__Run",
                "__thiscall",
                intType,
                "Wave467 correction: Frontend main loop matching source CFrontEnd::Run(EFrontEndEntry, BOOL) at the coarse control-flow level: init, process/render loop while mQuit is -2, stress-test early quit handling, shutdown dispatch, and final quit-code return. Static retail-binary/source-bridge evidence only; exact CFrontEnd layout, enum values, runtime frontend behavior, and rebuild parity remain unproven.",
                tags("frontend", "main-loop", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("entry", intType),
                    param("in_loaded_system", intType)
                }
            ),
            new Spec(
                "0x004685a0",
                "CFrontEnd__SetRenderViewAndProjection",
                "CFrontEnd__UpdateCamera",
                "__thiscall",
                voidType,
                "Wave467 correction: Source-bridged CFrontEnd::UpdateCamera helper that fetches the frontend camera view matrix and installs view/projection state through the retail CDXEngine path. Static retail-binary/source-bridge evidence only; exact FED/ENGINE layout, camera state semantics, runtime visual behavior, and rebuild parity remain unproven.",
                tags("frontend", "camera", "source-bridge", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004685f0",
                "CFrontEnd__VFunc_06_004685f0",
                "CFrontEnd__RenderStart",
                "__thiscall",
                intType,
                "Wave467 correction: Source-bridged virtual CFrontEnd::RenderStart slot reached from CDXFrontEnd::RenderStart, beginning the scene, setting frontend projection/view/world render state, binding the frontend camera, applying render state, and returning begin-scene success. Static retail-binary/source-bridge evidence only; exact vtable layout beyond this slot, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("frontend", "render-start", "vtable-slot", "source-bridge", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00468730",
                "CFrontEnd__GetShadowOffsetX",
                "CFrontEnd__GetShadowOffsetX",
                "__thiscall",
                floatType,
                "Wave467 correction: Source-bridged frontend shadow X offset helper, using sin(frontend counter / period) scaled by the X shadow radius. Static retail-binary/source-bridge evidence only; exact constants, runtime animation behavior, and rebuild parity remain unproven.",
                tags("frontend", "shadow-offset", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00468750",
                "CFrontEnd__GetShadowOffsetY",
                "CFrontEnd__GetShadowOffsetY",
                "__thiscall",
                floatType,
                "Wave467 correction: Source-bridged frontend shadow Y offset helper, using cos(frontend counter / period) scaled by the Y shadow radius. Static retail-binary/source-bridge evidence only; exact constants, runtime animation behavior, and rebuild parity remain unproven.",
                tags("frontend", "shadow-offset", "source-bridge", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave467 apply had missing/bad targets");
        }
    }
}
