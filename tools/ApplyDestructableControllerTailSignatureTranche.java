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

public class ApplyDestructableControllerTailSignatureTranche extends GhidraScript {
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
        Function fn = existingFunction(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + spec.address);
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

        Function readBack = existingFunction(addr(spec.address));
        if (readBack == null || !readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address);
        }
        println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
        Thread.sleep(50);
        return true;
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "destructable-controller-tail-wave350",
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
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec("0x00444450", "CDestructableSegmentsController__SetSegmentField0CByName", "__thiscall", voidType,
                "Name-dispatch controller helper: resolves the mesh root through this+0x10/+0x30, finds a child mesh by the supplied segmentName token, maps that mesh node's +0x88 index through the tracked segment array at this+0x04, and writes segmentValue to the segment field +0x0c. Callsite instruction evidence shows a two-stack-argument ABI with a float value and RET 0x8. Static retail evidence only; exact source identity, concrete field semantics, script wrapper source, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("name-dispatch", "segment-value", "signature-correction"),
                new String[] {"CDestructableSegmentsController__SetSegmentField0CByName"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentName", voidPtr), param("segmentValue", floatType)}),
            new Spec("0x004444b0", "CDestructableSegmentsController__SetSegmentFields0C10ByName", "__thiscall", voidType,
                "Name-dispatch controller helper: resolves a child mesh by segmentName, maps its +0x88 index to the tracked segment pointer, writes segmentValue to fields +0x0c and +0x10, then refreshes the cached active-value metric at this+0x18 from the root segment when present. Callsite instruction evidence shows a float value ABI with RET 0x8. Static retail evidence only; exact source identity, concrete field semantics, script wrapper source, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("name-dispatch", "segment-value", "cache-refresh", "signature-correction"),
                new String[] {"CDestructableSegmentsController__SetSegmentFields0C10ByName"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentName", voidPtr), param("segmentValue", floatType)}),
            new Spec("0x00444520", "CDestructableSegmentsController__FindSegmentByName", "__thiscall", voidPtr,
                "Name-dispatch controller lookup: resolves a child mesh by segmentName, maps its +0x88 index through the tracked segment array at this+0x04, returns the segment pointer, and emits the observed fatal warning path when no matching mesh segment is found. Static retail evidence only; exact source identity, concrete class layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("name-dispatch", "lookup", "signature-correction"),
                new String[] {"CDestructableSegmentsController__FindSegmentByName"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentName", voidPtr)}),
            new Spec("0x00444580", "CDestructableSegmentsController__SetAllSegmentsField0C", "__thiscall", voidType,
                "Bulk controller setter: walks every non-null tracked segment pointer in the this+0x04 array up to the segment count at this+0x08 and writes segmentValue to field +0x0c. Callsite instruction evidence shows a single float stack argument and RET 0x4. Static retail evidence only; exact source identity, concrete field semantics, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("bulk-setter", "segment-value", "signature-correction"),
                new String[] {"CDestructableSegmentsController__SetAllSegmentsField0C"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentValue", floatType)}),
            new Spec("0x004445b0", "CDestructableSegmentsController__SetSegmentActiveFlagByName", "__thiscall", voidType,
                "Name-dispatch controller helper: resolves a child mesh by segmentName, maps its +0x88 index to the tracked segment pointer, writes activeFlag to field +0x1c, then refreshes the cached active-value metric at this+0x18 from the root segment when present. Callsite instruction evidence shows a name plus byte/bool-derived flag ABI with RET 0x8. Static retail evidence only; exact source identity, concrete flag semantics, script wrapper source, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("name-dispatch", "active-flag", "cache-refresh", "signature-correction"),
                new String[] {"CDestructableSegmentsController__SetSegmentActiveFlagByName"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentName", voidPtr), param("activeFlag", intType)}),
            new Spec("0x00444660", "CDestructableSegmentsController__Init", "__fastcall", voidType,
                "Controller initialization pass reached from CUnit__Init through the unit's controller pointer at +0x178: obtains the mesh root, allocates and zeros the tracked segment array from the mesh node count, recursively processes the root mesh node, warns on primary-core anomalies, links secondary/core component monitor entries, dispatches per-segment behavior setup, and caches total root health/value at this+0x18. Stuart's matching controller source body is not present in the checked reference tree. Static retail evidence only; exact source identity, concrete layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("init", "mesh-walk", "component-link", "signature-correction"),
                new String[] {"CDestructableSegmentsController__Init"},
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec("0x004449c0", "CDestructableSegmentsController__CreateSegment", "__thiscall", voidPtr,
                "Controller segment factory: creates the concrete destroyable-segment object for a classified mesh node, with kind 0 routing to CDestroyableCoreSegment__Init and kinds 1/2/3 allocating vtable variants 0x005db148, 0x005db114, and 0x005db0e0 after CDestructableSegment__Init. The observed ABI takes segmentKind, meshNode, parentSegment, and segmentValue and returns the created segment pointer. Static retail evidence only; exact source identity, concrete class names for kind values, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("factory", "mesh-walk", "vtable-selection", "signature-correction"),
                new String[] {"CDestructableSegmentsController__CreateSegment"},
                new ParameterImpl[] {param("this", voidPtr), param("segmentKind", intType), param("meshNode", voidPtr), param("parentSegment", voidPtr), param("segmentValue", floatType)}),
            new Spec("0x00444c10", "CDestructableSegmentsController__ProcessNode", "__thiscall", voidType,
                "Recursive controller mesh-node processor: increments the global recursion-depth counter, selects mode-specific mesh data, classifies eligible mesh nodes from flags/name prefixes/child state, computes a segmentValue from node extents, creates/registers segment objects, maps mesh indices and alias children into the tracked segment array, recurses over child nodes, and decrements the depth counter on exit. Static retail evidence only; exact source identity, concrete node-type enum names, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("mesh-walk", "recursive", "factory-caller", "signature-correction"),
                new String[] {"CDestructableSegmentsController__ProcessNode"},
                new ParameterImpl[] {param("this", voidPtr), param("meshNode", voidPtr), param("parentSegment", voidPtr)})
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
            throw new IllegalStateException("Destructable controller tail tranche failed for " + failed + " target(s)");
        }
    }
}
