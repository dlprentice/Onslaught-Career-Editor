//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCameraSourceSignatureCorrection extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.parameters = parameters;
        }
    }

    private static boolean isDryRun(String mode) {
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

    private Function getFunctionOrThrow(String addrText) throws Exception {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean nameAllowed(String currentName, Spec spec) {
        if (currentName.equals(spec.name)) {
            return true;
        }
        for (String previousName : spec.previousNames) {
            if (currentName.equals(previousName)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.callingConvention).append(" ").append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!nameAllowed(fn.getName(), spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName() + " != " + spec.name);
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            return false;
        }

        if (needsRename) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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
        println("OK: " + spec.address + " " + spec.name + " -> " + fn.getSignature().toString());
        return needsRename;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00418ef0", "CThing3rdPersonCamera__ctor", "__thiscall", voidPtr,
                "Source-parity Camera.cpp constructor: initializes the CThing3rdPersonCamera active reader, builds CBSpline control points from the tracked thing GetRadius result, and stores the curve. Static source/decompile/xref evidence only; concrete layout, runtime camera behavior, BEA launch, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("forThing", voidPtr)}),
            new Spec("0x00419120", "CThing3rdPersonCamera__scalar_deleting_dtor", "__thiscall", voidPtr,
                "MSVC scalar deleting destructor wrapper for CThing3rdPersonCamera: calls the local destructor body and frees the object when the delete flag is set. Static vtable/decompile evidence only; concrete layout and runtime behavior remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00419140", "CThing3rdPersonCamera__dtor", "__fastcall", voidType,
                "Source-parity destructor for CThing3rdPersonCamera: releases mCurve and unregisters the embedded active-reader link from the tracked thing. Static source/decompile evidence only; concrete layout and runtime behavior remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004198d0", "CPanCamera__ctor", "__thiscall", voidPtr,
                "Source-parity CPanCamera constructor: stores the tracked thing active reader, curve, event-manager start-time, and length, then seeds current/old camera state via Update. Static source/decompile/xref evidence only; runtime pan-camera behavior remains unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("forThing", voidPtr), param("curve", voidPtr), param("length", floatType)}),
            new Spec("0x00419a40", "CPanCamera__scalar_deleting_dtor", "__thiscall", voidPtr,
                "MSVC scalar deleting destructor wrapper for CPanCamera: calls the local destructor body and frees the object when the delete flag is set. Static vtable/decompile evidence only; concrete layout and runtime behavior remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec("0x00419a60", "CPanCamera__dtor", "__fastcall", voidType,
                "Source-parity CPanCamera destructor: deletes the owned curve, clears the curve field, and unregisters the active-reader link from the tracked thing. Static source/decompile evidence only; concrete layout and runtime behavior remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00419b00", "CPanCamera__Update", "__fastcall", voidType,
                "Source-parity CPanCamera update: samples the CBSpline by event-manager time, updates position/orientation, and schedules UPDATE_CAMERA for the next frame/end-of-frame path. Static source/decompile/xref evidence only; runtime pan-camera behavior remains unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00419e00", "CViewPointCamera__ctor", "__thiscall", voidPtr,
                "Name/signature correction: source-aligned CViewPointCamera constructor copies the look-at point, rotate-speed/start-distance/end-distance/time-between-distance reference values, default orientation, and cached old values. Static source/decompile/callsite evidence only; runtime death-camera behavior remains unproven.",
                new String[] {"CViewPointCamera__ctor_like_00419e00"},
                new ParameterImpl[] {param("this", voidPtr), param("point", voidPtr), param("rotateSpeed", floatPtr), param("startDistance", floatPtr), param("endDistance", floatPtr), param("timeBetweenDistance", floatPtr)}),
            new Spec("0x0041a740", "CControllableCamera__ctor", "__thiscall", voidPtr,
                "Signature hardening: source-aligned CControllableCamera constructor takes FVector pos and FMatrix orientation by value on the stack, seeds current/old/temp camera state, and stores the frame-count snapshot. Static source/decompile/callsite evidence only; runtime free-camera behavior remains unproven.",
                new String[] {},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("posX", floatType), param("posY", floatType), param("posZ", floatType), param("posW", floatType),
                    param("orientation00", floatType), param("orientation01", floatType), param("orientation02", floatType), param("orientation03", floatType),
                    param("orientation10", floatType), param("orientation11", floatType), param("orientation12", floatType), param("orientation13", floatType),
                    param("orientation20", floatType), param("orientation21", floatType), param("orientation22", floatType), param("orientation23", floatType)
                })
        };

        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        for (Spec spec : specs) {
            boolean didRename = applySpec(spec, dryRun);
            if (dryRun) {
                skipped++;
            }
            else {
                updated++;
                if (didRename) {
                    renamed++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("updated=" + updated + " skipped=" + skipped + " renamed=" + renamed + " missing=0 bad=0");
    }
}
