//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyAnimalLifecycleBoundaryWave946 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function existing = functionAtEntry(address);
        if (existing != null) {
            return existing;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = getOrCreate(spec, dryRun, stats);
        if (fn == null) {
            return;
        }

        boolean renameNeeded = !fn.getName().equals(spec.name);
        boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
        boolean commentOrTagsNeedUpdate = fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec);

        if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else if (commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (signatureNeedsUpdate) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        }
        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
            stats.commentOnlyUpdated++;
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50L);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "animal-lifecycle-boundary-wave946",
            "wave946-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened"
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
        println("ApplyAnimalLifecycleBoundaryWave946 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0044c140",
                "CAnimal__HandleEvent3000Dispatch",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 0 and a second DATA vtable xref at 0x005e4454 point at this event handler body. The body reads the event argument at ESP+4, checks event number 0xbb8/3000, forwards other events to CComplexThing__HandleEvent, and for event 3000 dispatches this vtable byte offset +0x108. Static retail Ghidra evidence only; exact source virtual name, concrete CAnimal event meaning, runtime scheduling behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "event-3000", "vtable-slot-0"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("event", voidPtr)
                }
            ),
            new Spec(
                "0x0043e9f0",
                "CThing__GetRenderPos",
                "__thiscall",
                voidType,
                "Wave946 inherited vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 3 and broad DATA vtable xrefs point at this shared render-position getter. The body copies four dwords from this+0x1c through this+0x28 into the caller-provided outRenderPos buffer and returns with RET 0x4, matching the Stuart-source CThing::GetRenderPos() inline shape. Static retail Ghidra evidence only; exact structure type, owner coverage across all vtables, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "render-position", "thing-source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outRenderPos", voidPtr)
                }
            ),
            new Spec(
                "0x0043ea20",
                "CComplexThing__GetRenderOrientation",
                "__thiscall",
                voidType,
                "Wave946 inherited vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 4 and broad DATA vtable xrefs point at this shared render-orientation getter. The body copies 0x30 bytes from this+0x3c into the caller-provided outRenderOrientation buffer and returns with RET 0x4, matching the Stuart-source CComplexThing::GetRenderOrientation() inline shape. Static retail Ghidra evidence only; exact matrix type, owner coverage across all vtables, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "render-orientation", "complexthing-source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outRenderOrientation", voidPtr)
                }
            ),
            new Spec(
                "0x00405e80",
                "SharedVFunc__WriteZeroVectorRet04_00405e80",
                "__thiscall",
                voidType,
                "Wave946 inherited vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 5 and 121 DATA vtable xrefs point at this shared zero-vector writer. The body writes three zero dwords to the caller-provided outVector buffer and returns with RET 0x4. Static retail Ghidra evidence only; exact virtual contract, source owner coverage, vector width naming, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "zero-vector", "ret04"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outVector", voidPtr)
                }
            ),
            new Spec(
                "0x004040f0",
                "CAnimal__GetClassNameString",
                "__thiscall",
                charPtr,
                "Wave946 CAnimal lifecycle vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 7 points at this compact constant-string getter. The body returns string 0x00622d70, dumped as \"CAnimal\", then returns. Static retail Ghidra evidence only; exact source virtual name, user-facing/debug-only role, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "class-name-string", "vtable-slot-7"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00404100",
                "CAnimal__GetTypeId1D",
                "__thiscall",
                intType,
                "Wave946 CAnimal lifecycle vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 8 points at this compact constant-id getter. The body returns literal 0x1d and terminates before the next code body at 0x00404110. Static retail Ghidra evidence only; exact enum name, source virtual name, runtime type/id semantics, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "constant-type-id", "vtable-slot-8"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401420",
                "CThing__GetCueFactorFromRenderThing",
                "__thiscall",
                floatType,
                "Wave946 inherited vtable-boundary recovery: CAnimal vtable 0x005d8698 slot 13 and 62 DATA vtable xrefs point at this shared float getter. The body loads the render-thing-like pointer at this+0x30, returns float [ptr+0x4] when non-null, otherwise returns fallback constant 0x005d8570; this matches the Stuart-source CThing::GetCueFactor() pattern at a bounded static level. Runtime render/cue behavior, exact field names, owner coverage across all vtables, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "cue-factor", "thing-source-parity"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401440",
                "CThing__GetRenderRadiusFromRenderThing",
                "__thiscall",
                floatType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 16 and 48 DATA vtable xrefs point at this shared render-radius getter. The body loads this+0x30, dispatches the render-thing vtable byte offset +0x18 when non-null, and otherwise returns fallback float constant 0x005d856c; this matches the Stuart-source CThing::GetRenderRadius() pattern at a bounded static level. Runtime render-radius behavior, exact render-thing layout, owner coverage across all vtables, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "render-radius", "thing-source-parity", "vtable-slot-16"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401460",
                "CThing__MakeVisible",
                "__thiscall",
                voidType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 32 and 61 DATA vtable xrefs point at this shared visibility helper. The body clears bit 0x10 from this+0x2c and returns, matching the Stuart-source CThing::MakeVisible() TF_INVISIBLE clear shape. Static retail Ghidra evidence only; exact flag enum coverage, runtime visibility behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "visibility", "thing-source-parity", "vtable-slot-32"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401470",
                "CThing__MakeInvisible",
                "__thiscall",
                voidType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 33 and 61 DATA vtable xrefs point at this shared visibility helper. The body sets bit 0x10 at this+0x2c and returns, matching the Stuart-source CThing::MakeInvisible() TF_INVISIBLE set shape. Static retail Ghidra evidence only; exact flag enum coverage, runtime visibility behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "visibility", "thing-source-parity", "vtable-slot-33"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401490",
                "CThing__Damage_NoOp",
                "__thiscall",
                voidType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 40 and 26 DATA vtable xrefs point at this shared no-op damage handler. The body is a single RET 0x10, matching a four-explicit-argument empty CThing::Damage-like virtual at a bounded ABI level. Static retail Ghidra evidence only; exact source owner coverage, gameplay damage behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "damage-noop", "ret10", "thing-source-parity", "vtable-slot-40"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("amount", floatType),
                    param("byThing", voidPtr),
                    param("damageShields", intType),
                    param("meshPartNo", intType)
                }
            ),
            new Spec(
                "0x004014b0",
                "CThing__GravityDefault",
                "__thiscall",
                floatType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 45 and 37 DATA vtable xrefs point at this shared constant-float getter. The body returns float constant 0x005d8574 and returns, matching the Stuart-source CThing::Gravity() default shape at a bounded static level. Static retail Ghidra evidence only; exact constant value naming, owner coverage across all vtables, runtime physics behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "gravity-default", "thing-source-parity", "vtable-slot-45"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004014e0",
                "CComplexThing__IsObjectiveFlagSet",
                "__thiscall",
                intType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 26 and 59 DATA vtable xrefs point at this shared objective-flag predicate. The body reads signed byte this+0x2c, masks bit 0x20, shifts it to a 0/1 return, matching the Stuart-source CComplexThing::IsObjective() flag-check shape at a bounded static level. Static retail Ghidra evidence only; exact bool type, flag enum coverage, runtime objective behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "objective-flag", "complexthing-source-parity", "vtable-slot-26"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401510",
                "SharedVFunc__ReturnField78_00401510",
                "__thiscall",
                intType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 41 and 59 DATA vtable xrefs point at this shared compact field getter. The body returns dword this+0x78. Static retail Ghidra evidence only; exact virtual contract, concrete field name, owner coverage across all vtables, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "field-78", "vtable-slot-41"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00401520",
                "SharedVFunc__NoOpFiveArgs_00401520",
                "__thiscall",
                voidType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 61 and 25 DATA vtable xrefs point at this shared empty virtual. The body is a single RET 0x14, proving five explicit stack arguments but not the semantic source method. Static retail Ghidra evidence only; exact virtual contract, owner coverage across all vtables, runtime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "noop", "ret14", "vtable-slot-61"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg1", voidPtr),
                    param("arg2", voidPtr),
                    param("arg3", voidPtr),
                    param("arg4", voidPtr),
                    param("arg5", voidPtr)
                }
            ),
            new Spec(
                "0x00404110",
                "CAnimal__SetThingTypeMask80000001",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 38 and 10 DATA vtable xrefs point at this compact type-mask setter. The body ORs the caller value with 0x80000001, stores the result at this+0x34, and returns with RET 0x4. Static retail Ghidra evidence only; exact enum name, source virtual name, runtime type behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "thing-type-mask", "vtable-slot-38"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("thingType", intType)
                }
            ),
            new Spec(
                "0x00404120",
                "CAnimal__CopyVector7CToOut",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 27 and 40 DATA vtable xrefs point at this CAnimal-local vector copy getter. The body copies four dwords from this+0x7c through this+0x88 into the caller-provided output buffer and returns with RET 0x4. Static retail Ghidra evidence only; exact vector type, field name, runtime animal movement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "vector-7c", "vtable-slot-27"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outVector", voidPtr)
                }
            ),
            new Spec(
                "0x00404150",
                "CAnimal__SetVector7CFromInput",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 67 and 43 DATA vtable xrefs point at this CAnimal-local vector setter. The body copies four dwords from the caller-provided input buffer into this+0x7c through this+0x88 and returns with RET 0x4. Static retail Ghidra evidence only; exact vector type, field name, runtime animal movement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "vector-7c", "vtable-slot-67"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("inVector", voidPtr)
                }
            ),
            new Spec(
                "0x00404170",
                "CAnimal__AddVectorTo7C",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 68 and 43 DATA vtable xrefs point at this CAnimal-local vector accumulator. The body adds the caller-provided three-float vector into this+0x7c, this+0x80, and this+0x84, then returns with RET 0x4. Static retail Ghidra evidence only; exact vector type, field name, runtime animal movement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "vector-7c", "vtable-slot-68"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("deltaVector", voidPtr)
                }
            ),
            new Spec(
                "0x004041a0",
                "CAnimal__CopyVector8CToOut",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 30 and 43 DATA vtable xrefs point at this CAnimal-local vector copy getter. The body copies four dwords from this+0x8c through this+0x98 into the caller-provided output buffer and returns with RET 0x4. Static retail Ghidra evidence only; exact vector type, field name, runtime animal movement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "vector-8c", "vtable-slot-30"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outVector", voidPtr)
                }
            ),
            new Spec(
                "0x004041d0",
                "CAnimal__CopyMatrix9CToOut",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 31 and 43 DATA vtable xrefs point at this CAnimal-local matrix copy getter. The body copies 0x30 bytes from this+0x9c into the caller-provided output buffer with MOVSD.REP and returns with RET 0x4. Static retail Ghidra evidence only; exact matrix type, field name, runtime animal orientation behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "matrix-9c", "vtable-slot-31"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outMatrix", voidPtr)
                }
            ),
            new Spec(
                "0x004045d0",
                "CAnimal__RenderViaCThingRender",
                "__thiscall",
                voidType,
                "Wave946 CAnimal lifecycle vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 36 is the only DATA xref to this one-argument render wrapper. The body forwards the caller render_flags argument to CThing__Render and returns with RET 0x4. Static retail Ghidra evidence only; exact source virtual name, animal render policy, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("animal", "render-wrapper", "vtable-slot-36"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("renderFlags", intType)
                }
            ),
            new Spec(
                "0x004f3d30",
                "CThing__DrawDebugStuff3d",
                "__thiscall",
                voidType,
                "Wave946 CAnimal vtable-boundary expansion: CAnimal vtable 0x005d8698 slot 52 and 58 DATA vtable xrefs point at this shared debug-volume renderer. The body copies identity matrices from 0x0083d9f0, copies this+0x1c position data, calls through vtable byte offset +0x40 for a radius-like float, then calls CThing__RenderDebugVolumeOverlay. This matches the Stuart-source CThing::DrawDebugStuff3d() debug-render role at a bounded static level. Runtime debug-render behavior, exact matrix/vector types, owner coverage across all vtables, BEA patching, and rebuild parity remain unproven.",
                tags("shared-vtable-target", "debug-render", "thing-source-parity", "vtable-slot-52"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                stats.bad++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave946 CAnimal lifecycle boundary apply encountered missing/bad rows");
        }
    }
}
