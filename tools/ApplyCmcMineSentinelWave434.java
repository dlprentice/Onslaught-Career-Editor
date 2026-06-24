//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyCmcMineSentinelWave434 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final boolean createIfMissing;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                boolean createIfMissing,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.createIfMissing = createIfMissing;
            this.allowedExistingNames = allowedExistingNames;
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
        return toAddr(addressText);
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
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
            "cmcmine-sentinel-wave434",
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

    private Function createFunctionAt(Spec spec, Address address) throws Exception {
        DisassembleCommand cmd = new DisassembleCommand(address, null, true);
        cmd.applyTo(currentProgram, monitor);
        Function fn = createFunction(address, spec.name);
        if (fn == null) {
            fn = functionAtEntry(address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
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
                    println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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

            Function readBack = functionAtEntry(address);
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

            println("OK: " + spec.address + " " + readBack.getSignature() + (createdNow ? " created" : ""));
            stats.updated++;
            Thread.sleep(50);
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
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0049c3e0",
                "CMCMine__Constructor",
                "__thiscall",
                voidPtr,
                "Wave434 lifecycle correction: RET 0x4 confirms one owner_mine stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc3f4, and stores the owner pointer at +0x08. Static retail evidence only; exact source identity, concrete layout, runtime mine motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCMine__ctor_like_0049c3e0" },
                tags("cmcmine", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_mine", voidPtr)
                }
            ),
            new Spec(
                "0x0049c400",
                "CMCMine__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave434 lifecycle correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCMine__Destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] { "CMCMine__VFunc_01_0049c400" },
                tags("cmcmine", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x0049c420",
                "CMCMine__Destructor",
                "__fastcall",
                voidType,
                "Wave434 lifecycle correction: register-only destructor body restores vtable 0x005dc3f4, clears +0x08, seeds +0x0c with 0xc7c34ff3, and tails into the base motion-controller destructor. Static retail evidence only; concrete cleanup ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCMine__ctor_like_0049c420" },
                tags("cmcmine", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049c440",
                "CMCMine__VFunc_04_UpdateInterpolatedHeightOffset_0049c440",
                "__thiscall",
                voidType,
                "Wave434 slot correction: CMCMine vtable 0x005dc3f4 slot 4 points here and RET 0x10 confirms four stack arguments. The body reads the owner pointer at +0x08, checks the first stack argument at +0x88, subtracts an interpolated owner +0x250/+0x254 height value from the second stack argument at +0x08, and refreshes cached +0x0c. Static retail evidence only; exact virtual name, argument meanings, runtime mine height behavior, concrete layout, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCMine__VFunc_04_0049c440" },
                tags("cmcmine", "vtable-slot", "height-cache", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("transform_a", voidPtr),
                    param("transform_b", voidPtr),
                    param("context_value", intType)
                }
            ),
            new Spec(
                "0x0049c4b0",
                "CMCMine__VFunc_08_CheckCachedHeightState_0049c4b0",
                "__fastcall",
                boolType,
                "Wave434 recovered function boundary: CMCMine vtable 0x005dc3f4 slot 8 points here. The short body reads the owner pointer from +0x08, compares cached +0x0c against owner +0x250, returns true when the cached value differs, and false when it still matches. Static retail evidence only; exact virtual name, concrete layout, runtime state semantics, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcmine", "function-boundary", "vtable-slot", "height-cache", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049c5d0",
                "CMCSentinel__Constructor",
                "__thiscall",
                voidPtr,
                "Wave434 lifecycle correction: RET 0x4 confirms one owner_sentinel stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc420, stores the owner pointer at +0x08, and seeds cached +0x0c/+0x10 with 0xc479c000. Static retail evidence only; exact source identity, concrete layout, runtime sentinel motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCSentinel__ctor_like_0049c5d0" },
                tags("cmcsentinel", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_sentinel", voidPtr)
                }
            ),
            new Spec(
                "0x0049c600",
                "CMCSentinel__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave434 lifecycle correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCSentinel__Destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] { "CMCSentinel__VFunc_01_0049c600" },
                tags("cmcsentinel", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x0049c620",
                "CMCSentinel__Destructor",
                "__fastcall",
                voidType,
                "Wave434 lifecycle correction: register-only destructor body restores vtable 0x005dc420, clears +0x08, and tails into the base motion-controller destructor. Static retail evidence only; concrete cleanup ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCSentinel__ctor_like_0049c620" },
                tags("cmcsentinel", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049c640",
                "CMCSentinel__VFunc_04_UpdateX1TurretOrBarrelTransform_0049c640",
                "__thiscall",
                voidType,
                "Wave434 recovered function boundary: CMCSentinel vtable 0x005dc420 slot 4 points here and RET 0x10 confirms four stack arguments. The body reads the owner pointer at +0x08, checks mesh-part name tokens X1 turret (0x0062dfc8) and X1 barrel (0x0062dfbc), performs shared matrix/vector transform work, writes transform outputs, and refreshes cached +0x0c/+0x10 from owner fields +0xe0/+0xe8. Static retail evidence only; exact virtual name, argument meanings, concrete layout, runtime sentinel transform behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcsentinel", "function-boundary", "vtable-slot", "x1-turret-token", "x1-barrel-token", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("transform_a", voidPtr),
                    param("transform_b", voidPtr),
                    param("context_value", intType)
                }
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

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave434 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
