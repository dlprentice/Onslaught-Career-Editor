//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMineMissileWave456 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
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
            "mine-missile-wave456",
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
            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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
            if (!spec.comment.equals(readBack.getComment())) {
                throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
            }
            Set<String> readBackTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!readBackTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
                }
            }

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(5000);
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
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004ba150",
                "CMine__Init",
                "CMine__Init",
                "__thiscall",
                voidType,
                "Wave456 signature/comment correction: CMine init marks init+0x70 with 0x20, derives orientation from heading at init+0x44 and the sampled heightfield normal, calls CGroundUnit__Init, allocates a CMCMine controller into this+0x70, clears this+0x260/+0x264, and sets the this+0x258 threshold flag. Static retail evidence only; runtime mine placement/water behavior remains unproven.",
                tags("mine", "init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init", voidPtr)
                }
            ),
            new Spec(
                "0x004ba490",
                "CMine__VFunc_02_004ba490",
                "CMine__VFunc02_CleanupLinkedParticleAndForward",
                "__fastcall",
                voidType,
                "Wave456 name/signature/comment correction: CMine virtual cleanup helper checks this+0x264, finalizes the linked unit/particle state through CUnit__FinalizeLinkedUnitStateAndClear, removes the node from the particle manager/global list, frees it, then forwards to VFuncSlot_02_004f95d0. Static retail evidence only; exact virtual slot and runtime cleanup behavior remain unproven.",
                tags("mine", "cleanup", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004ba9d0",
                "VTable_005e1c4c__Slot00_TryInvokeVFunc1D4",
                "CMine__TryDestroyedResetAndDispatchVFunc1D4",
                "__fastcall",
                intType,
                "Wave456 owner/name/signature correction: CMine-adjacent vtable data xref at 0x005e1c4c. The body calls CGroundUnit__MarkDestroyedAndResetState, returns 0 on failure, otherwise dispatches vfunc +0x1d4 and returns 1. Static retail evidence only; exact virtual slot/runtime lifecycle remains unproven.",
                tags("mine", "groundunit", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004baae0",
                "CMissile__Init",
                "CMissile__Init",
                "__thiscall",
                voidType,
                "Wave456 signature/comment correction: CMissile init optionally follows the resource pointer at this+0xf0+0x0c, allocates a 0x428 descriptor object with OID type 0x61 from Missile.cpp evidence, copies a CResourceDescriptor string, creates the linked object through PCRTID__CreateObject, stores it at this+0x30, invokes its descriptor load vfunc, frees the descriptor object, then calls CRound__Init. Static retail evidence only; runtime missile payload behavior remains unproven.",
                tags("missile", "init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init", voidPtr)
                }
            ),
            new Spec(
                "0x004bac10",
                "VTable_005e3cc0__Slot00_Dispatch68_AndPostHook",
                "CMissile__DispatchLinkedObjectVFunc68AndPostHook",
                "__thiscall",
                voidType,
                "Wave456 owner/name/signature correction: CMissile-adjacent vtable data xref at 0x005e3cc0. Ret 0x8 confirms two stack arguments; the body dispatches the linked object at this+0x30 through vfunc +0x68 with arg0/arg1, then calls SharedVFunc__NoOp_Ret08. Static retail evidence only; exact virtual slot/source identity remains unproven.",
                tags("missile", "dispatch", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("arg0", intType),
                    param("arg1", intType)
                }
            ),
            new Spec(
                "0x004bae10",
                "CMotionController__VFunc_01_004bae10",
                "CMotionController__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave456 name/signature/comment correction: scalar-deleting destructor wrapper for the base CMotionController vtable. It calls CMotionController__dtor_base, tests flags bit 0 from the ret 0x4 stack argument, optionally frees this through the memory manager, and returns this. Static retail evidence only; runtime ownership remains unproven.",
                tags("motion-controller", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004bae30",
                "CMotionController__ctor_like_004bae30",
                "CMotionController__ctor_base",
                "__fastcall",
                voidType,
                "Wave456 name/signature/comment correction: base CMotionController constructor helper. Instruction read-back shows it moves this into EAX, clears +0x04/+0x08 with zeroed ECX, and writes base vtable 0x005dc778. Static retail evidence only; concrete list semantics remain unproven.",
                tags("motion-controller", "constructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004bae50",
                "CMotionController__ctor_like_004bae50",
                "CMotionController__dtor_base",
                "__fastcall",
                voidType,
                "Wave456 name/signature/comment correction: base CMotionController destructor helper. The body restores base vtable 0x005dc778 and tails CMonitor__Shutdown. Static retail evidence only; runtime ownership remains unproven.",
                tags("motion-controller", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave456 apply had missing/bad entries");
        }
    }
}
