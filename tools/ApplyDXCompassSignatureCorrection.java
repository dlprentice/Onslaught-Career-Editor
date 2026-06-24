//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyDXCompassSignatureCorrection extends GhidraScript {
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00426fd0", "OID__AllocObject_DefaultTag_00662b2c", "__cdecl", voidPtr,
                "Signature/comment correction: broad allocator wrapper that forwards sizeBytes, default type/tag 0, debug tag DAT_00662b2c, and allocator context 0x009c3df0 to OID__AllocObject. Xrefs span CFastVB, CDXTexture, mesh, and parser helpers, so this is not DXCompass-specific ownership proof. Runtime allocation behavior, exact tag meaning, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("sizeBytes", intType)}),
            new Spec("0x004270e0", "CDXCompass__InitMarkerArrays", "__fastcall", voidType,
                "Signature/comment correction: zeroes two 30-slot compass marker arrays starting at this+0x3c24 with 0x18 stride, then calls CDXCompass__Init. CHud__Init passes the compass object from CHud+0x60 in ECX. Exact marker layout, runtime HUD behavior, tags, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00427110", "CDXCompass__LoadTextures", "__fastcall", voidType,
                "Signature/comment correction: loads ThreatFlash, DamageFlash, BarLine, and CompassObjectiveMarker texture references into this+0x3ef4 through this+0x3f00. CHud__LoadTextures passes CHud+0x60 in ECX. Texture lifetime completeness, runtime rendering behavior, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00427190", "CDXCompass__DestroyTextures", "__fastcall", voidType,
                "Signature/comment correction: releases the four compass texture references at this+0x3ef4 through this+0x3f00 by calling the ref-count helper on texture+8 and then zeroing each slot. CHud__ShutDown is the observed caller. Ownership completeness, runtime rendering behavior, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00427200", "CDXCompass__Reset", "__fastcall", voidType,
                "Signature/comment correction: clears the compass render/state flag at this+0x3c10. The observed CHud reset helper then clears ring texture, vertex-buffer, and byte-sprite slots. Exact reset semantics, concrete layout, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00427210", "CDXCompass__Render", "__thiscall", voidType,
                "Signature/comment correction: main compass render path called from CDXBattleLine__RenderWorldSpaceOverlay with the compass object in ECX and a battle-engine/render context stack argument. The body draws threat, damage, bar-line, and objective compass sprites, calls tracked X/Y getters, toggles render state, and flushes CFastVB. Exact context layout, runtime HUD behavior, stack-local provenance, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("battleEngineContext", voidPtr)}),
            new Spec("0x0053be40", "CDXCompass__Init", "__fastcall", voidType,
                "Signature/comment correction: initializes the compass render resources by allocating/loading a CByteSprite, clamping ring texture dimensions against GPU caps, allocating two ring texture pairs and two CVBuffers, building outer/inner ring geometry, and assigning the byte-sprite target. Source body identity, runtime rendering behavior, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x0053c1d0", "CDXCompass__BuildRingGeometry", "__cdecl", voidType,
                "Signature/comment correction: fills a compass ring vertex strip from locked vertices, texture width/height, segment count, thickness percent, and UV scale using sin/cos, then copies the first pair of vertices to close the ring. Called twice by CDXCompass__Init for outer and inner rings. Vertex format, runtime render parity, concrete layout, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("vertices", voidPtr), param("textureWidth", intType), param("textureHeight", intType), param("segmentCount", intType), param("thicknessPercent", intType), param("uvScale", floatType)})
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
