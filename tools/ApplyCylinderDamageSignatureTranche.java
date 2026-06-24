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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyCylinderDamageSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
            this.parameters = parameters;
        }
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

    private Address addr(String addrText) {
        if (!addrText.startsWith("0x") && !addrText.startsWith("0X")) {
            addrText = "0x" + addrText;
        }
        Address result = toAddr(addrText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        return result;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address address = addr(addrText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private boolean allowedName(Function fn, Spec spec) {
        if (fn.getName().equals(spec.name)) {
            return true;
        }
        for (String previous : spec.previousNames) {
            if (fn.getName().equals(previous)) {
                return true;
            }
        }
        return false;
    }

    private String signatureText(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getFunctionOrThrow(spec.address);
        if (!allowedName(fn, spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return;
        }

        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }

        Function readBack = getFunctionOrThrow(spec.address);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cylinder-damage-wave346",
            "cylinder-damage",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x0043fde0", "CCylinder__ctor", "__thiscall", voidType,
                "CCylinder constructor copies sourceCylinder radius context: installs CCylinder vtable 0x005d88cc, zeroes observed fields, and stores squared radius/radius-derived values. Static retail evidence only; exact layout, runtime collision behavior, and rebuild parity remain unproven.",
                tags("cylinder", "constructor", "signature-correction", "name-correction"),
                new String[] {"CCylinder__ctor_like_0043fde0", "CCylinder__ctor"},
                new ParameterImpl[] {param("this", voidPtr), param("sourceCylinder", voidPtr)}),
            new Spec("0x0043fe20", "CCylinder__ResolveCollisionVFunc02", "__thiscall", intType,
                "CCylinder collision vfunc slot 2 resolves moving-state/contact context and writes contact normal/contact output when collision conditions hold; caller CSphere__VFunc_02 pushes four stack args plus ECX this. Exact collision semantics, class layout, runtime behavior, and rebuild parity remain unproven.",
                tags("cylinder", "collision", "vtable-slot", "signature-correction", "name-correction"),
                new String[] {"CCylinder__VFunc_02_0043fe20", "CCylinder__ResolveCollisionVFunc02"},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("movingStateA", voidPtr),
                    param("movingStateB", voidPtr),
                    param("radiusContext", voidPtr),
                    param("contactOut", voidPtr)
                }),
            new Spec("0x00440b90", "CDamage__Init", "__fastcall", voidType,
                "Initializes CDamage: loads damage0.tga into owned texture-info, clears the observed damage table and lookup arrays, and initializes flags/counters. Static retail evidence only; exact layout, runtime terrain-damage behavior, and rebuild parity remain unproven.",
                tags("damage", "init", "signature-correction"),
                new String[] {"CDamage__Init"},
                new ParameterImpl[] {param("damage", voidPtr)}),
            new Spec("0x00440c00", "CDamage__FreeOwnedDamageObjects", "__fastcall", voidType,
                "Frees CDamage owned damage texture state: releases the nested texture object and outer texture-info record when present, then clears the stored pointers. Static retail evidence only; exact ownership model and runtime behavior remain unproven.",
                tags("damage", "cleanup", "signature-correction"),
                new String[] {"CDamage__FreeOwnedDamageObjects"},
                new ParameterImpl[] {param("damage", voidPtr)}),
            new Spec("0x00440c40", "CDamage__ResetDamageTables", "__fastcall", voidType,
                "Resets CDamage damage lookup state: clears the observed damage table/lookup arrays and restores the active/free-list flags. Static retail evidence only; exact layout and runtime behavior remain unproven.",
                tags("damage", "reset", "signature-correction"),
                new String[] {"CDamage__ResetDamageTables"},
                new ParameterImpl[] {param("damage", voidPtr)}),
            new Spec("0x00440c70", "CDamage__LoadDamageTexture", "__thiscall", voidType,
                "Loads a CDamage texture-info record from a TGA path: chooses mipmap level from texture dimensions, allocates the pixel buffer, copies/inverts source bytes, and builds mipmap data. Static retail evidence only; exact pixel semantics and runtime rendering behavior remain unproven.",
                tags("damage", "texture", "signature-correction"),
                new String[] {"CDamage__LoadDamageTexture"},
                new ParameterImpl[] {param("this", voidPtr), param("tgaPath", charPtr)}),
            new Spec("0x00440eb0", "CDamage__InsertCellEntry", "__thiscall", intType,
                "Inserts a CDamage per-cell entry; instruction evidence shows ret 0x10, with stack args for cellIndex, coordX, coordY, and stampValue. Static retail evidence only; exact terrain-damage semantics and rebuild parity remain unproven.",
                tags("damage", "cell-list", "signature-correction"),
                new String[] {"CDamage__InsertCellEntry"},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("cellIndex", intType),
                    param("coordX", intType),
                    param("coordY", intType),
                    param("stampValue", intType)
                }),
            new Spec("0x00440f80", "CDamage__RemoveCellEntryByCoords", "__thiscall", voidType,
                "Removes a matching CDamage per-cell entry by coordinates; instruction evidence shows ret 0xc, so the older fourth stack arg was stale. Static retail evidence only; exact terrain-damage semantics and rebuild parity remain unproven.",
                tags("damage", "cell-list", "signature-correction"),
                new String[] {"CDamage__RemoveCellEntryByCoords"},
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("cellIndex", intType),
                    param("coordX", intType),
                    param("coordY", intType)
                }),
            new Spec("0x00441000", "CDamage__CreateTextureBuffer", "__thiscall", voidType,
                "Creates a CDamage texture-info buffer from a CChunkReader stream, allocating the texture-info record and marking the damage texture state initialized. Static retail evidence only; exact resource format coverage and runtime rendering behavior remain unproven.",
                tags("damage", "texture", "chunk-reader", "signature-correction"),
                new String[] {"CDamage__CreateTextureBuffer"},
                new ParameterImpl[] {param("this", voidPtr), param("chunkReader", voidPtr)})
        };

        for (Spec spec : specs) {
            applySpec(spec, dryRun);
        }
        println("--- SUMMARY ---");
        println("targets=" + specs.length + " mode=" + (dryRun ? "dry" : "apply"));
    }
}
