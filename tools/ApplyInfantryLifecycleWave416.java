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

public class ApplyInfantryLifecycleWave416 extends GhidraScript {
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
            "infantry-wave416",
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
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);

            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }

            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    stats.wouldRename++;
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                    stats.skipped++;
                    return;
                }
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }

            if (dryRun) {
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.skipped++;
                return;
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
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
            }
            String actualSignature = readBack.getSignature().toString();
            if (!actualSignature.equals(expectedSignature(spec))) {
                throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + actualSignature + " != " + expectedSignature(spec));
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
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00488bb0",
                "CInfantry__Init",
                "__thiscall",
                voidType,
                "Signature/comment correction: Infantry init takes an infantry init pointer, allocates collision seeking and guide helpers, applies 4.0/1.0 scale context, calls CGroundUnit__Init, and keeps runtime infantry behavior and rebuild parity unproven.",
                tags("infantry", "lifecycle", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("infantryInit", voidPtr)}),
            new Spec(
                "0x00488dc0",
                "CInfantryAI__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper calls CInfantryAI__dtor_body_00488de0, checks flags bit 0, optionally frees through OID__FreeObject, returns this, and keeps runtime cleanup behavior unproven.",
                tags("infantry", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec(
                "0x00488de0",
                "CInfantryAI__dtor_body_00488de0",
                "__fastcall",
                voidType,
                "Name/signature correction: destructor body reached by CInfantryAI scalar deleting destructor restores CUnitAI base vtable 0x005d8d1c, removes +0x28/+0x24/+0x0c pointer-set links through CSPtrSet__Remove, calls CMonitor__Shutdown, and keeps runtime cleanup behavior unproven.",
                tags("infantry", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x00488e80",
                "CCollisionSeekingInfantryBloke__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Name/signature correction: scalar-deleting destructor wrapper calls CCollisionSeekingInfantryBloke__dtor_body_00488ea0, checks flags bit 0, optionally frees through OID__FreeObject, returns this, and keeps runtime collision behavior unproven.",
                tags("collision", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr), param("flags", byteType)}),
            new Spec(
                "0x00488ea0",
                "CCollisionSeekingInfantryBloke__dtor_body_00488ea0",
                "__fastcall",
                voidType,
                "Name/signature correction: destructor body reached by the collision-seeking infantry bloke scalar wrapper shuts down the monitor at this+0x24, calls CCollisionSeekingRound__Destructor, and keeps runtime collision behavior unproven.",
                tags("collision", "destructor", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x00488ef0",
                "CCollisionSeekingThing__ctor_base",
                "__fastcall",
                voidType,
                "Name/signature correction: constructor-base helper zeros field +0x04 and installs the shared CCollisionSeekingThing vtable 0x005d9608; exact source identity and rebuild parity remain unproven.",
                tags("collision", "constructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x00488f00",
                "CHLCollisionDetector__ctor_base",
                "__fastcall",
                voidType,
                "Name/signature correction: constructor-base helper zeros field +0x04 and installs CHLCollisionDetector vtable 0x005dbf78; exact source identity and rebuild parity remain unproven.",
                tags("collision", "constructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x00489040",
                "CUnitAI__TryPlayActivateAnimation",
                "__fastcall",
                intType,
                "Signature/comment hardening: activation-animation helper checks fields +0x140/+0x26c/+0x2c, calls CUnitAI__TrySpawnOrFinalizeAttachedUnit, writes state +0x268 to 0x12, and keeps runtime AI behavior unproven.",
                tags("unitai", "animation", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x00489de0",
                "CUnitAI__PromoteDieAnimationToDeadVariant",
                "__fastcall",
                intType,
                "Signature/comment hardening: maps current die animation tokens die_up/die_back/die_left/die_right to dead_up/dead_back/dead_left/dead_right or dead_forward and keeps runtime death behavior unproven.",
                tags("unitai", "death-animation", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)}),
            new Spec(
                "0x00489ef0",
                "CUnitAI__ForceDeadForwardAndResetDeathState",
                "__fastcall",
                voidType,
                "Signature/comment hardening: if death flag bit +0x2c is set, selects dead_forward, clears +0x26c, refreshes the state timestamp, and keeps runtime death behavior unproven.",
                tags("unitai", "death-animation", "signature-hardened", "comment-hardened"),
                new ParameterImpl[] {param("this", voidPtr)})
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            if (monitor.isCancelled()) {
                throw new RuntimeException("Cancelled");
            }
            applySpec(spec, dryRun, stats);
        }

        println(
            "SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
    }
}
