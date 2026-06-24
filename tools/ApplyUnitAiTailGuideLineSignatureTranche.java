//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

public class ApplyUnitAiTailGuideLineSignatureTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] previousNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] previousNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.previousNames = previousNames;
            this.tags = tags;
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

    private Function existingFunction(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrThrow(String addressText) throws Exception {
        Address address = addr(addressText);
        Function fn = existingFunction(address);
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addressText);
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
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
        if (!nameAllowed(fn.getName(), spec)) {
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

        Function readBack = existingFunction(addr(spec.address));
        if (readBack == null || !readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "unitai-tail-guide-line-wave359",
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00447b10", "CUnitAI__PlayWingUnfoldedAnimationAndSetState5", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI resolves wingunfolded, dispatches animation vfunc +0xf0, sets state field +0x27c to state 5, and removes the unit from the occupancy grid. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "animation"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00447b60", "CUnitAI__HasReachedCachedAnchorPoint", "__fastcall", intType,
                "Saved signature/comment correction: CUnitAI checks cached anchor flag +0x290 and compares current X/Y against cached +0x280/+0x284 using a distance threshold. Static retail evidence only; exact source identity, concrete layout, runtime movement behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "cached-anchor"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00447bb0", "CUnitAI__GetOrGenerateCachedAnchorPoint", "__thiscall", voidType,
                "Saved signature/comment correction: CUnitAI uses one stack argument (RET 0x4) as outAnchorPoint, seeds/regenerates cached anchor fields +0x280/+0x28c, calls CUnitAI__IsCachedAnchorPointValid, and copies the cached anchor to outAnchorPoint. Static retail evidence only; exact source identity, concrete layout, runtime pathing behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "cached-anchor"),
                new ParameterImpl[] {param("this", voidPtr), param("outAnchorPoint", voidPtr)}),
            new Spec("0x00447d50", "CUnitAI__IsCachedAnchorPointValid", "__fastcall", intType,
                "Saved signature/comment correction: CUnitAI validates the cached anchor by querying nearby CMapWho entries, checking collision/height context, and scanning an occupancy bitmask when states are not 2 or 3. Static retail evidence only; exact source identity, concrete layout, runtime collision behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "cached-anchor", "collision"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00447fa0", "CUnitAI__AdvanceDoorWingAnimationState", "__fastcall", intType,
                "Saved signature/comment correction: CUnitAI advances door-wing animation by recognizing dooropening, doorclosing, wingfolded, and wingunfolded states, dispatching vfunc +0xf0, and setting state +0x27c when appropriate. Static retail evidence only; exact source identity, concrete layout, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "animation-state"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00448110", "CUnitAI__SetDoorWingState6", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI narrow state helper writes state +0x27c to 6. Static retail evidence only; exact source identity, concrete layout, runtime transition behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "state-transition"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00448120", "CUnitAI__SetDoorWingState7AndMirrorYawOffset", "__fastcall", voidType,
                "Saved signature/comment correction: CUnitAI narrow state helper writes state +0x27c to 7 and mirrors yaw/offset field +0x2a4 around the 1.0-style constant. Static retail evidence only; exact source identity, concrete layout, runtime transition behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("unitai", "door-wing", "state-transition"),
                new ParameterImpl[] {param("unitAI", voidPtr)}),
            new Spec("0x00448170", "CDropship__TraceGroundAndSpawnThrusterDust", "__stdcall", voidType,
                "Saved name/signature correction: this helper was previously mislabeled as CLine__ctor_like_00448170, but retail evidence shows a stdcall helper (RET 0x8) that builds a stack-local CLine, samples/traces the static heightfield, and spawns thruster dust from a dropship transform. Static retail evidence only; exact source identity, concrete layout, runtime particle behavior, and rebuild parity remain unproven.",
                new String[] {"CLine__ctor_like_00448170"},
                tags("dropship", "thruster", "heightfield", "particle-effect"),
                new ParameterImpl[] {param("effectPoint", voidPtr), param("transformMatrix", voidPtr)}),
            new Spec("0x0047e290", "CGuide__ctor_base", "__thiscall", voidPtr,
                "Saved name/signature correction: CGuide base constructor uses one stack argument (RET 0x4) guideOwner, installs the base vtable, stores guideOwner at +0x18, copies guideOwner position/orientation fields into +0x8..+0x14, clears +0x1c, and returns this. Static retail evidence only; exact source identity, concrete layout, runtime guide/pathing behavior, and rebuild parity remain unproven.",
                new String[] {"CGuide__ctor_like_0047e290"},
                tags("guide", "constructor", "base-ctor"),
                new ParameterImpl[] {param("this", voidPtr), param("guideOwner", voidPtr)}),
            new Spec("0x00415d70", "CBoatGuide__ctor", "__thiscall", voidPtr,
                "Saved signature/comment correction: CBoatGuide constructor wrapper is called by CBoat__Init, passes guideOwner to CGuide__ctor_base, writes vtable 0x005d8d5c, and returns this. Exact source identity, CGuide/CBoatGuide layout, runtime pathfinding behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("boat-guide", "guide", "constructor"),
                new ParameterImpl[] {param("this", voidPtr), param("guideOwner", voidPtr)})
        };

        int updated = 0;
        int skipped = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun);
                if (dryRun) {
                    skipped++;
                }
                else {
                    updated++;
                }
            }
            catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + ex.getMessage());
            }
        }

        println("--- SUMMARY ---");
        println("targets=" + specs.length + " updated=" + updated + " skipped=" + skipped + " failed=" + failed + " dry=" + dryRun);
        if (failed != 0) {
            throw new IllegalStateException("Failed targets: " + failed);
        }
    }
}
