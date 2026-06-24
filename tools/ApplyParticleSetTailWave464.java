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

public class ApplyParticleSetTailWave464 extends GhidraScript {
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
            "particleset-tail-wave464",
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
                "0x004cc870",
                "CParticleDescriptor__ctor_like_004cc870",
                "CParticleSet__dtor_base",
                "__fastcall",
                voidType,
                "Wave464 correction: Base ParticleSet destructor-body helper that restores the base vtable pointer PTR_LAB_005ddad4 before scalar-deleting destructor paths return or free the object. Static retail-binary evidence only; source identity, exact layout, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-set", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle_set", voidPtr)
                }
            ),
            new Spec(
                "0x004ccb40",
                "VFuncSlot_00_004ccb40",
                "CParticleSet__shared_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave464 correction: Shared ParticleSet vtable slot-0 scalar-deleting destructor used by the observed particle-set type vtables; calls CParticleSet__dtor_base, frees this when flags bit 0 is set, and returns this. Static retail-binary evidence only; exact type ownership, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-set", "destructor", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", intType)
                }
            ),
            new Spec(
                "0x004ccc50",
                "CPDSelector__VFunc_08_004ccc50",
                "CPDSelector__DispatchChildVFunc20",
                "__thiscall",
                voidType,
                "Wave464 correction: CPDSelector child-dispatch helper that walks four descriptor pointer slots at +0x5c..+0x68 and dispatches each non-null child's vfunc +0x20 with dispatch_context. Static retail-binary evidence only; exact virtual meaning, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-descriptor", "selector", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("dispatch_context", intType)
                }
            ),
            new Spec(
                "0x004cd290",
                "CParticleSet__InitType11",
                "CParticleSet__InitType11",
                "__fastcall",
                voidType,
                "Wave464 correction: Initializes ParticleSet type 11 by clearing shared base fields, installing vtable PTR_CPDMesh__scalar_deleting_dtor_005ddb3c, and seeding observed defaults including +0x64=100 and +0x74=1. Static retail-binary evidence only; exact type semantics, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-set", "type-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle_set", voidPtr)
                }
            ),
            new Spec(
                "0x004cd2d0",
                "CParticleSet__InitType12",
                "CParticleSet__InitType12",
                "__fastcall",
                voidType,
                "Wave464 correction: Initializes ParticleSet type 12 by clearing shared base fields, installing vtable PTR_VFuncSlot_00_004ccb40_005ddfc8, and zeroing observed type-local defaults at +0x5c/+0x60/+0x64. Static retail-binary evidence only; exact type semantics, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-set", "type-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle_set", voidPtr)
                }
            ),
            new Spec(
                "0x004cd3c0",
                "CParticleSet__InitType13",
                "CParticleSet__InitType13",
                "__fastcall",
                voidType,
                "Wave464 correction: Initializes ParticleSet type 13 by clearing an extended field range, installing vtable PTR_VFuncSlot_00_004ccb40_005de030, and seeding observed scalar defaults including 1.0, 0.5, 5.0, 10, 180.0, and 360.0 constants. Static retail-binary evidence only; exact type semantics, source identity, runtime behavior, and rebuild parity remain unproven.",
                tags("particle-set", "type-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("particle_set", voidPtr)
                }
            ),
            new Spec(
                "0x004cd7f0",
                "CParticleSet__LoadFromArchive",
                "CParticleSet__LoadFromArchive",
                "__thiscall",
                intType,
                "Wave464 correction: Loads particle sets from a token/archive source after destroying the current list, allocating a 0x1388c archive workspace, validating token ids 0/1/2/3/4, creating each set by type/name, dispatching the created set vfunc +0x18 loader, resolving references, and returning success/failure. Static retail-binary evidence only; exact archive/object layout, source identity, runtime loading behavior, and rebuild parity remain unproven.",
                tags("particle-set", "archive-load", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("archive_source", voidPtr)
                }
            ),
            new Spec(
                "0x004cda60",
                "CParticleSet__LoadParticleSetFile",
                "CParticleSet__LoadParticleSetFile",
                "__thiscall",
                intType,
                "Wave464 correction: High-level ParticleSet file loader that destroys the current set list, allocates a 200-byte filename buffer, selects MainSet.par for modes 0/2 or Frontend.par otherwise, opens a stack CDXMemBuffer through CDXMemBuffer__OpenReadMode11, calls CParticleSet__LoadFromArchive when open succeeds, closes/destroys the buffer, frees the filename, and returns 1. Static retail-binary evidence only; runtime file loading behavior, source identity, and rebuild parity remain unproven.",
                tags("particle-set", "file-load", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("particle_set_mode", intType)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                break;
            }
            applySpec(spec, dryRun, stats);
        }

        println("--- SUMMARY ---");
        println(
            "updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave464 apply had missing/bad targets");
        }
    }
}
