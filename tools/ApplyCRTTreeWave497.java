//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyCRTTreeWave497 extends GhidraScript {
    private static class Spec {
        final String address;
        final String[] allowedExistingNames;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final boolean createIfMissing;
        final String[] tags;

        Spec(
                String address,
                String[] allowedExistingNames,
                String newName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                boolean createIfMissing,
                String[] tags) {
            this.address = address;
            this.allowedExistingNames = allowedExistingNames;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.createIfMissing = createIfMissing;
            this.tags = tags;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crttree-wave497",
            "retail-binary-evidence"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.newName)) {
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
            .append(spec.newName)
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
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

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.newName);
        if (fn == null) {
            fn = functionAtEntry(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.newName)) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
        }
        return fn;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            boolean createdNow = false;

            if (fn == null) {
                if (!spec.createIfMissing) {
                    stats.missing++;
                    println("MISSING: " + spec.address + " " + spec.newName);
                    return;
                }
                if (dryRun) {
                    stats.wouldCreate++;
                    println("DRY: " + spec.address + " <missing> -> create " + expectedSignature(spec));
                    return;
                }
                fn = createFunctionAt(spec, address);
                createdNow = true;
                stats.created++;
            }

            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }

            boolean renameNeeded = !fn.getName().equals(spec.newName);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (!updateNeeded) {
                println("SKIP: " + spec.address + " " + spec.newName);
                stats.skipped++;
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                return;
            }

            if (renameNeeded) {
                fn.setName(spec.newName, SourceType.USER_DEFINED);
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

            Function readBack = functionAtEntry(address);
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.newName)) {
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
            if (!hasAllTags(readBack, spec.tags)) {
                throw new IllegalStateException("Read-back missing one or more tags at " + spec.address);
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature + (createdNow ? " created" : ""));
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.newName + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
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
        DataType byteType = ByteDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004dd7b0",
                new String[] {},
                "CRTTree__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init", voidPtr)
                },
                "Wave497 recovered CRTTree vtable 0x005deb9c slot 1 boundary. The body calls CRenderThing__Init(this, init), resolves a tree/render resource through init+0x408, stores resource pointers at this+0x14/+0x18, falls back to DAT_0089c9c8 while bumping its +0x170 refcount, caches resource scalars from +0x164/+0x168, and initializes state bytes/slots at this+0x28 and this+0x1c. Static retail-binary evidence only; exact source name, concrete CRTTree/resource layouts, runtime tree rendering, and rebuild parity remain unproven.",
                true,
                tags("crttree", "vtable-slot-1", "boundary-recovered", "init", "render-resource")
            ),
            new Spec(
                "0x004dd850",
                new String[] {},
                "CRTTree__VFuncSlot03_UpdateVisibilityState",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave497 recovered CRTTree vtable 0x005deb9c slot 3 boundary. The body compares current camera/render context vectors with this+0x08 and tree-resource/falling-tree state, consults the global byte at DAT_0083cd58, conditionally calls a tree/render helper through this+0x18, and marks this+0x20 when complete. Static retail-binary evidence only; exact virtual name, concrete layout, runtime visibility behavior, and rebuild parity remain unproven.",
                true,
                tags("crttree", "vtable-slot-3", "boundary-recovered", "visibility-state")
            ),
            new Spec(
                "0x004dd960",
                new String[] {},
                "CRTTree__VFuncSlot02_BuildRenderOutputs",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("renderContext", voidPtr)
                },
                "Wave497 recovered CRTTree vtable 0x005deb9c slot 2 boundary. The body uses camera/context transforms, this+0x08, resource/falling-tree state, DAT_0083cd58, CMap/CRender-style helpers, and stack output records before returning with one stack argument. Static retail-binary evidence only; exact virtual name, output-record layout, runtime rendering behavior, and rebuild parity remain unproven.",
                true,
                tags("crttree", "vtable-slot-2", "boundary-recovered", "render-output")
            ),
            new Spec(
                "0x004ddfd0",
                new String[] {"CRTTree__Destructor"},
                "CRTTree__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave497 signature/comment hardening: resets the CRTTree vtable to 0x005deb9c, hides/unregisters the tree through CDXTrees__HideTree, decrements the resource refcount at this+0x14 -> +0x170 when present, clears this+0x14, restores the CRenderThing vtable 0x005deaac, and dispatches the child/owned pointer at this+0x10 with delete flag 1 when present. Static retail-binary evidence only; exact source name, concrete CRTTree layout, runtime tree lifetime behavior, and rebuild parity remain unproven.",
                false,
                tags("crttree", "destructor", "vtable-referenced", "signature-corrected", "comment-hardened")
            ),
            new Spec(
                "0x004de050",
                new String[] {},
                "CRTTree__VFuncSlot06_GetResourceScalar164",
                "__fastcall",
                floatType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave497 recovered CRTTree vtable 0x005deb9c slot 6 boundary. The compact body loads the resource pointer from this+0x14 and returns the float at resource+0x164. Static retail-binary evidence only; exact field name, runtime LOD/distance semantics, and rebuild parity remain unproven.",
                true,
                tags("crttree", "vtable-slot-6", "boundary-recovered", "float-getter")
            ),
            new Spec(
                "0x004de060",
                new String[] {},
                "SharedVFunc__ReturnResourceField150_004de060",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave497 recovered shared CRTMesh/CRTTree vtable helper boundary. The body loads this+0x14 as a resource pointer and returns resource+0x150; CRTMesh vtable 0x005deb1c and CRTTree vtable 0x005deb9c both reference it. Static retail-binary evidence only; exact owner contract, field type, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "rtmesh", "crttree", "boundary-recovered", "resource-getter")
            ),
            new Spec(
                "0x004de080",
                new String[] {"CRTTree__scalar_deleting_dtor"},
                "CRTTree__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                },
                "Wave497 name/signature/comment hardening: CRTTree vtable 0x005deb9c slot 0 points here. The wrapper calls CRTTree__Destructor(this), frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when flags bit 0 is set, and returns this. Static retail-binary evidence only; allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                false,
                tags("crttree", "scalar-deleting-destructor", "vtable-slot-0", "name-corrected", "signature-corrected")
            ),
            new Spec(
                "0x00516580",
                new String[] {"PCRTID__CreateObject"},
                "PCRTID__CreateObject",
                "__cdecl",
                voidPtr,
                new ParameterImpl[] {
                    param("typeId", intType)
                },
                "Wave497 signature/comment hardening: switch factory for PCRTID.cpp render objects. Type 1 allocates 0x50 and installs CRTMesh vtable 0x005deb1c, type 2 allocates 0x34 and installs CRTTree vtable 0x005deb9c, type 4 allocates 0x5c and installs CRTBuilding vtable 0x005de9c0, and type 5 allocates 0x28 then calls CRTCutscene__CRTCutscene. Static retail-binary evidence only; full factory ownership, allocation policy, runtime render-object behavior, and rebuild parity remain unproven.",
                false,
                tags("pcrtid", "factory", "signature-corrected", "comment-hardened", "crttree")
            ),
            new Spec(
                "0x004dbd40",
                new String[] {},
                "SharedVFunc__ReturnFloat0Ret8_004dbd40",
                "__thiscall",
                floatType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg0", voidPtr),
                    param("arg1", voidPtr)
                },
                "Wave497 recovered shared vtable helper boundary referenced by CRenderThing/CRTTree-style tables. The body returns the float constant at 0x005d856c and pops two stack arguments. Static retail-binary evidence only; exact virtual contract, owner coverage, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "boundary-recovered", "float-return", "vtable-referenced")
            ),
            new Spec(
                "0x004d6a50",
                new String[] {},
                "SharedVFunc__WriteDefaultTransformOutputsRet16_004d6a50",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("outMatrix", voidPtr),
                    param("outVec3", voidPtr),
                    param("outScalar", voidPtr),
                    param("arg3", voidPtr)
                },
                "Wave497 recovered shared CRenderThing/CRTTree vtable helper boundary. The body writes an identity-like 3x4 transform to outMatrix, zeros an outVec3 record, writes 0x42b40000 to outScalar, and returns with four stack arguments. Static retail-binary evidence only; exact output record types, virtual contract, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "crenderthing", "crttree", "boundary-recovered", "default-transform")
            ),
            new Spec(
                "0x004dbc00",
                new String[] {},
                "SharedVFunc__ReturnFalseRet4_004dbc00",
                "__thiscall",
                byteType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg0", voidPtr)
                },
                "Wave497 recovered broad shared vtable helper boundary. The body clears AL, returns false/0, and pops one stack argument; it is referenced by multiple render/sound-style vtables including CRTTree slot 20. Static retail-binary evidence only; exact owner coverage, virtual contract, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("shared-vfunc", "boundary-recovered", "return-false", "vtable-referenced")
            ),
            new Spec(
                "0x004db880",
                new String[] {},
                "CRenderThing__ForwardSlot26ToChildSlot68",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg0", voidPtr),
                    param("arg1", voidPtr)
                },
                "Wave497 recovered shared render-object forwarding helper boundary. The body reads the child/owned pointer at this+0x10, returns if it is null, and otherwise forwards two stack arguments through the child vtable slot at +0x68. It is referenced by several render-object vtables including CRTTree slot 26. Static retail-binary evidence only; exact child type, virtual contract, runtime behavior, and rebuild parity remain unproven.",
                true,
                tags("crenderthing", "shared-vfunc", "boundary-recovered", "child-forwarder")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (!dryRun && stats.bad > 0) {
            throw new IllegalStateException("Apply finished with bad=" + stats.bad);
        }
    }
}
