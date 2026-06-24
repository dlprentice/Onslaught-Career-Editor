//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyBuildingByteSpriteAnimationSignatureCorrection extends GhidraScript {
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
        DataType byteType = ByteDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec("0x00417870", "CBuilding__VFuncSlot_02_RemoveFromWorldUpdateShadowAndForward", "__fastcall", voidType,
                "Name/signature correction: RTTI read-back places DATA refs for this slot in the CBuilding and CSimpleBuilding vtables; the body removes the object from the world occupancy grid, updates static-shadow visibility with enable=1, and forwards to the shared render/update slot at 0x004f95d0. Exact source method name, concrete CBuilding/CSimpleBuilding layout, runtime render/world behavior, and rebuild parity remain unproven.",
                new String[] {"VFuncSlot_02_00417870"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004178a0", "CBuilding__ProcessClosingAndUnshuttingAnimations", "__fastcall", voidType,
                "Owner/signature correction: CBuilding vtable DATA xref plus decompile evidence tie this body to closing/unshutting animation state gates, CUnit spawner checks, fields at +0x254/+0x25c/+0x260/+0x264/+0x268, and closing/unshutting animation dispatch. Exact source identity, field layout names, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CUnit__ProcessClosingAndUnshuttingAnimations"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00418120", "CBuilding__AdvanceOpenCloseAnimationState", "__fastcall", intType,
                "Owner/signature correction: CBuilding vtable DATA xref plus decompile evidence show an open/close/shut animation-state stepper that compares the active animation id through vfunc +0x58, dispatches opening/open/closing/closed/unshutting/notshut/shutting transitions through vfunc +0xf0, and updates state fields at +0x254/+0x264. Exact source identity, field layout names, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {"CCockpit__AdvanceOpenCloseAnimationState"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004183d0", "CBuildingNamedMesh__dtor_base", "__fastcall", voidType,
                "Owner/signature correction: RTTI read-back resolves vtable 0x005d910c as CBuildingNamedMesh, superseding the older CByteSprite deferral. The body resets CBuildingNamedMesh vtable slots and forwards to CActor__dtor_base. Exact source method name, class layout, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CByteSprite__dtor_base"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00418430", "CBuildingNamedMesh__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Owner/signature correction: scalar-deleting destructor wrapper for CBuildingNamedMesh calls CBuildingNamedMesh__dtor_base, tests scalar-delete flag bit 0, optionally frees this through OID__FreeObject, and returns this. Exact allocator ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                new String[] {"CByteSprite__scalar_deleting_dtor"},
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00418450", "CBuildingNamedMesh__VFuncSlot_02_RemoveFromWorldAndForwardNamedMesh", "__fastcall", voidType,
                "Owner/signature correction: RTTI read-back places DATA ref 0x005d9114 under the CBuildingNamedMesh vtable; the body removes the object from the world occupancy grid and forwards to CNamedMesh slot 2. Exact source method name, vtable-slot semantics, runtime render/world behavior, and rebuild parity remain unproven.",
                new String[] {"CByteSprite__vfunc_stub"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00418470", "CByteSprite__Init", "__fastcall", voidPtr,
                "Signature/comment hardening: CByteSprite init zeroes the sprite-data pointer, frame-offset pointer, and loaded-frame count fields, leaves EAX as this, and is used by CDXCompass initialization after allocating a 0x20-byte object. Concrete CByteSprite layout, exact source identity, runtime compass rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004184c0", "CByteSprite__Load", "__thiscall", intType,
                "Signature/comment hardening: CByteSprite load builds a data_%s.raw filename from rawName, opens it through DXMemBuffer, allocates temporary raw/frame-offset/RLE buffers, encodes frames with CByteSprite__EncodeFrame, copies compact sprite data and frame offsets into owned storage, frees temporary buffers, and returns the loaded frame count. CDXCompass passes compass, 16x16, 20 frames, threshold 4. Concrete layout, transparency semantics, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("rawName", charPtr), param("width", intType), param("height", intType), param("frameCount", intType), param("transparentThreshold", byteType)}),
            new Spec("0x00418720", "CByteSprite__SetTarget", "__thiscall", voidType,
                "Signature/comment hardening: stores the destination buffer, pitch, target width, target height, and wrap flag at CByteSprite fields +0xc/+0x10/+0x14/+0x18/+0x1c. CDXCompass sets a 512x512 target with height/window 30 and wrap enabled. Concrete layout, runtime target-buffer behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("targetBuffer", voidPtr), param("pitch", intType), param("width", intType), param("height", intType), param("wrapFlag", byteType)}),
            new Spec("0x00418750", "CByteSprite__DrawRLE_NoClip", "__thiscall", voidType,
                "Signature/comment hardening: draws one RLE byte-sprite span group without horizontal clipping, using rleData plus destination x/y/height against the current target buffer, pitch, and target height. Exact packet semantics, palette behavior, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("rleData", charPtr), param("x", intType), param("y", intType), param("height", intType)}),
            new Spec("0x004187e0", "CByteSprite__DrawRLE_ClipLeft", "__thiscall", voidType,
                "Signature/comment hardening: draws one RLE byte-sprite span group with left-edge clipping, skipping writes while destination x is negative and sharing the same rleData/x/y/height call shape as the no-clip helper. Exact packet semantics, palette behavior, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("rleData", charPtr), param("x", intType), param("y", intType), param("height", intType)}),
            new Spec("0x00418880", "CByteSprite__DrawRLE_ClipRight", "__thiscall", voidType,
                "Signature/comment hardening: draws one RLE byte-sprite span group with right-edge clipping, suppressing writes once destination x reaches the target width and sharing the same rleData/x/y/height call shape as the no-clip helper. Exact packet semantics, palette behavior, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("rleData", charPtr), param("x", intType), param("y", intType), param("height", intType)}),
            new Spec("0x00418920", "CByteSprite__DrawFrame", "__thiscall", voidType,
                "Signature/comment hardening: validates frameIndex, resolves the frame offset into compact RLE data, applies signed frame offsets to x/y, bounds-checks against target dimensions, dispatches to no-clip/left/right RLE draw helpers, and optionally wraps horizontally when the wrap flag is set. Exact CByteSprite layout, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("this", voidPtr), param("frameIndex", intType), param("x", intType), param("y", intType)}),
            new Spec("0x004189f0", "CByteSprite__EncodeFrame", "__fastcall", intType,
                "Signature/comment hardening: scans a temporary raw-frame work state for visible bounds using the threshold byte, writes a compact frame header and RLE packet stream, advances the output cursor and frame-offset pointer, and returns 1 for encoded content or 0 for an empty frame. Exact work-state layout, transparency semantics, runtime rendering behavior, and rebuild parity remain unproven.",
                new String[] {},
                new ParameterImpl[] {param("workState", voidPtr)})
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
