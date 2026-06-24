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

public class ApplyDestructableBridgeSignatureBoundaryTranche extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final String[] previousNames;
        final boolean createIfMissing;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                String[] previousNames,
                boolean createIfMissing,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.tags = tags;
            this.previousNames = previousNames;
            this.createIfMissing = createIfMissing;
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

    private Function getOrCreate(Spec spec, boolean dryRun) throws Exception {
        Address address = addr(spec.address);
        Function fn = existingFunction(address);
        if (fn != null) {
            return fn;
        }
        if (!spec.createIfMissing) {
            throw new IllegalStateException("Function not found at " + spec.address);
        }
        if (dryRun) {
            return null;
        }

        disassemble(address);
        fn = createFunction(address, spec.name);
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
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

    private boolean applySpec(Spec spec, boolean dryRun) throws Exception {
        Function fn = getOrCreate(spec, dryRun);
        if (fn == null) {
            println("DRY: " + spec.address + " <missing> -> create " + signatureText(spec));
            return true;
        }
        if (!allowedName(fn, spec)) {
            throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + signatureText(spec));
            return true;
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

        Function readBack = getOrCreate(spec, false);
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "destructable-bridge-wave351",
            "destructable-segments",
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
            new Spec("0x00444620", "CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric", "__thiscall", voidType,
                "Bulk controller active-flag helper: walks every non-null tracked segment pointer in the this+0x04 array up to the segment count at this+0x08, writes activeFlag to segment field +0x1c, then refreshes the cached active-value metric at this+0x18 from the root segment when present. This corrects the older CExplosionInitThing owner label. Static retail evidence only; exact source identity, concrete flag semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("owner-correction", "bulk-setter", "active-flag", "cache-refresh", "signature-correction"),
                new String[] {
                    "CExplosionInitThing__SetChildStateAndRefreshSegmentMetric",
                    "CExplosionInitThing__Unk_00444620",
                    "Auto_00444620",
                    "CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric"
                },
                false,
                new ParameterImpl[] {param("this", voidPtr), param("activeFlag", intType)}),
            new Spec("0x00444940", "CDestroyableSegmentComponent__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Component scalar-deleting destructor wrapper: calls CDestroyableSegmentComponent__dtor_base, frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact source identity, concrete component layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "vtable-slot", "signature-correction"),
                new String[] {
                    "CDestroyableSegmentComponent__VFunc_01_00444940",
                    "CDestroyableSegmentComponent__scalar_deleting_dtor",
                    "Auto_00444940"
                },
                false,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00444960", "CDestroyableSegmentComponent__dtor_base", "__fastcall", voidType,
                "Component destructor body: removes the owner-link cell at this+0x40 from the owning pointer set when present, then chains directly to the canonical CDestroyableSegment__dtor_base body at 0x00442660. Static retail evidence only; exact source identity, concrete component layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "owner-link", "signature-correction"),
                new String[] {
                    "CDestroyableSegmentComponent__RemoveOwnerLinkAndResetBase",
                    "CDestroyableSegmentComponent__Helper_00444960",
                    "CUnitAI__Unk_00444960",
                    "Auto_00444960",
                    "CDestroyableSegmentComponent__dtor_base"
                },
                false,
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x00444be0", "CDestroyableSegmentVariant__scalar_deleting_dtor", "__thiscall", voidPtr,
                "Recovered shared scalar-deleting destructor boundary used by the three observed non-core segment vtable slot-1 entries at 0x005db0e4, 0x005db118, and 0x005db14c: calls the destroyable-segment base destructor thunk, frees this through OID__FreeObject when flags bit 0 is set, and returns this. Static retail evidence only; exact concrete class names for the three variants, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("function-boundary", "destructor", "vtable-slot", "shared-variant", "signature-correction"),
                new String[] {
                    "CDestroyableSegmentVariant__scalar_deleting_dtor"
                },
                true,
                new ParameterImpl[] {param("this", voidPtr), param("flags", intType)}),
            new Spec("0x00444c00", "CDestroyableSegment__dtor_base_thunk", "__fastcall", voidType,
                "Small tail thunk that jumps to the canonical CDestroyableSegment__dtor_base body at 0x00442660. Keeping this as a thunk avoids duplicating the base destructor body name at two addresses. Static retail evidence only; exact source identity, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("destructor", "thunk", "name-correction", "signature-correction"),
                new String[] {
                    "CDestroyableSegment__dtor_base",
                    "CDestroyableSegment__ctor_like_00442660",
                    "Auto_00442660",
                    "CDestroyableSegment__dtor_base_thunk"
                },
                false,
                new ParameterImpl[] {param("this", voidPtr)})
        };

        int changedOrWouldChange = 0;
        int failed = 0;
        for (Spec spec : specs) {
            try {
                if (applySpec(spec, dryRun)) {
                    changedOrWouldChange++;
                }
            } catch (Exception ex) {
                failed++;
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
            }
        }
        println("--- SUMMARY ---");
        println("targets=" + specs.length + " changed_or_would_change=" + changedOrWouldChange + " failed=" + failed + " dry=" + dryRun);
        if (failed > 0) {
            throw new IllegalStateException("Destructable bridge signature/boundary tranche failed for " + failed + " target(s)");
        }
    }
}
