//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyParticleDescriptorWave468 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String oldName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.oldName = oldName;
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

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
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
            "particle-descriptor-wave468",
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
            if (!fn.getName().equals(spec.oldName) && !fn.getName().equals(spec.name)) {
                throw new IllegalStateException(
                    "Unexpected function name at " + spec.address + ": " + fn.getName()
                );
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                if (needsRename) {
                    stats.wouldRename++;
                }
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
            Set<String> actualTags = tagNames(readBack);
            for (String tag : spec.tags) {
                if (!actualTags.contains(tag)) {
                    throw new IllegalStateException("Read-back missing tag at " + spec.address + ": " + tag);
                }
            }

            stats.updated++;
            println("OK: " + spec.address + " " + readBack.getName() + " -> " + actualSignature);
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004c0370",
                "CParticleDescriptor__PushCurrentToHistoryAndSetNow",
                "CParticleDescriptor__PushCurrentToHistoryAndSetNow",
                "__thiscall",
                voidType,
                "Wave468 correction: particle descriptor value-history helper. If the live descriptor block has the 10000.0 first-sample sentinel in the current value, this seeds history/current slots from the incoming 4-dword value; otherwise it shifts current to previous and writes the new value. The timestamp/age field is refreshed from DAT_00672fd0 unless disabled by the -1.0 sentinel. Static retail-binary evidence only; exact CParticleDescriptor layout, token semantics, runtime particle behavior, and rebuild parity remain unproven.",
                tags("particle", "particle-descriptor", "value-history", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("value_vec4", voidPtr),
                    param("unused_context", voidPtr)
                }
            ),
            new Spec(
                "0x004c0450",
                "CParticleDescriptor__Load12DwordsAndMarkDirty",
                "CParticleDescriptor__Load12DwordsAndMarkDirty",
                "__thiscall",
                voidType,
                "Wave468 correction: particle descriptor transform/cache loader. Copies twelve dwords from src_block into the descriptor-owned block at +0x10 and marks the block dirty/active at +0xa0 when the backing block exists. Static retail-binary evidence only; exact descriptor block layout, token semantics, runtime particle behavior, and rebuild parity remain unproven.",
                tags("particle", "particle-descriptor", "transform-cache", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("src_block", voidPtr),
                    param("unused_context", voidPtr)
                }
            ),
            new Spec(
                "0x004c04c0",
                "VFuncSlot_23_004c04c0",
                "CParticleDescriptor__DispatchTimedParticleNodes",
                "__thiscall",
                voidType,
                "Wave468 correction: RTTI/vtable-backed shared CParticleDescriptor/CPD subclass slot 23. Iterates the descriptor-linked particle-node list at this+0x54 and dispatches each node's vfunc at +0x2c when the caller disables the time gate or the node time/sentinel at +0x60 passes the DAT_005d856c comparison. Static retail-binary evidence only; exact descriptor/node layouts, precise time-gate semantics, runtime particle behavior, and rebuild parity remain unproven.",
                tags("particle", "particle-descriptor", "vtable-slot", "rtti-backed", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("use_time_gate", intType),
                    param("unused_context", intType)
                }
            ),
            new Spec(
                "0x004c0510",
                "CParticleManager__LinkNodeFront",
                "CParticleManager__AppendNodeToActiveList",
                "__thiscall",
                voidType,
                "Wave468 correction: particle manager active-list append helper. Empty-list path links the manager into the global nonempty-manager list through CParticleManager__LinkNodeByOffset3C40, sets head/tail at +0x54/+0x50, and clears node prev/next; nonempty path appends the node after the current tail and updates the tail pointer. Static retail-binary evidence only; exact manager/node layouts, allocation policy, runtime particle behavior, and rebuild parity remain unproven.",
                tags("particle", "particle-manager", "active-list", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("node", voidPtr),
                    param("unused_context", voidPtr)
                }
            ),
            new Spec(
                "0x004c0560",
                "CEngine__RemoveNodeFromActiveList",
                "CParticleManager__UnlinkNodeFromActiveList",
                "__thiscall",
                voidType,
                "Wave468 correction: particle manager active-list unlink helper. Clears the selected/current node pointer at +0x58 when it matches, relinks neighbor prev/next fields, clears the removed node links, and unregisters the manager from the global nonempty-manager list when the active-list head at +0x54 becomes null. Static retail-binary evidence only; exact manager/node layouts, ownership semantics, runtime particle behavior, and rebuild parity remain unproven.",
                tags("particle", "particle-manager", "active-list", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("node", voidPtr),
                    param("unused_context", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.bad != 0 || stats.missing != 0) {
            throw new RuntimeException("Wave468 particle descriptor apply failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
