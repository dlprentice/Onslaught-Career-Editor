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

public class ApplyCmcGroundAttackHiveBossWave432 extends GhidraScript {
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
            "cmcgroundattack-hiveboss-wave432",
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
                "0x004964d0",
                "CMCGroundAttack__Constructor",
                "__thiscall",
                voidPtr,
                "Wave432 lifecycle correction: RET 0x4 confirms one owner_aircraft stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc330, stores the owner pointer at +0x08, and seeds +0x0c/+0x10 with 0xc479c000 sentinels. Static retail evidence only; exact source identity, concrete layout, runtime ground-attack motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCGroundAttack__ctor_like_004964d0" },
                tags("cmcgroundattack", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_aircraft", voidPtr)
                }
            ),
            new Spec(
                "0x00496500",
                "CMCGroundAttack__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave432 lifecycle correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCGroundAttack__Destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] { "CMCGroundAttack__VFunc_01_00496500" },
                tags("cmcgroundattack", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x00496520",
                "CMCGroundAttack__Destructor",
                "__fastcall",
                voidType,
                "Wave432 lifecycle correction: register-only destructor body restores vtable 0x005dc330, clears +0x08, and tails into the base motion-controller destructor. Static retail evidence only; concrete cleanup ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCGroundAttack__ctor_like_00496520" },
                tags("cmcgroundattack", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00496540",
                "CMCGroundAttack__VFunc_04_UpdateTurretTransform_00496540",
                "__thiscall",
                voidType,
                "Wave432 recovered function boundary: CMCGroundAttack vtable 0x005dc330 slot 4 points here, and the body ends with RET 0x10 before the next known function at 0x004968a0. The function checks the mesh-part name against the turret token at 0x0062dd20, performs matrix/vector math through shared helpers, and refreshes cached owner values at +0x0c/+0x10. Static retail evidence only; exact virtual name, argument meanings, concrete layout, runtime transform behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcgroundattack", "function-boundary", "vtable-slot", "turret-token", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("transform_a", voidPtr),
                    param("transform_b", voidPtr),
                    param("context_value", intType)
                }
            ),
            new Spec(
                "0x004968a0",
                "CMCGroundAttack__VFunc_08_CheckCachedMotionState_004968a0",
                "__fastcall",
                boolType,
                "Wave432 recovered function boundary: CMCGroundAttack vtable 0x005dc330 slot 8 points here. The body reads the owner pointer from +0x08, compares owner fields +0xe0/+0xe4/+0x284 against cached values at this+0x0c/+0x10, returns false only when the checked values still match, and returns true otherwise. Static retail evidence only; exact virtual name, concrete layout, runtime state semantics, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcgroundattack", "function-boundary", "vtable-slot", "state-cache", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004968f0",
                "CMeshPart__NameIsNotTurret",
                "__cdecl",
                boolType,
                "Wave432 token/name correction: one cdecl mesh_part argument is read from ESP+4, and the body compares the mesh-part name at +0xdc against the turret token at 0x0062dd20. It returns true when the name is not turret. Static retail evidence only; optimization-policy meaning and runtime behavior remain unproven.",
                false,
                new String[] { "CMeshPart__NameIsNotToken_62dd20" },
                tags("mesh-filter", "turret-token", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x00496910",
                "CMeshPart__AnySubPartNameIsTurret",
                "__cdecl",
                boolType,
                "Wave432 token/name correction: one cdecl mesh_part argument is read from ESP+4, then child count +0x15c and child pointer table +0x160 are walked looking for a child name at +0xdc matching the turret token at 0x0062dd20. Static retail evidence only; optimization-policy meaning and runtime behavior remain unproven.",
                false,
                new String[] { "CMeshPart__AnySubPartEqualsToken_62dd20" },
                tags("mesh-filter", "turret-token", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x00496f60",
                "CMeshPart__NameAvoidsTurretAndBarrelPrefix",
                "__cdecl",
                boolType,
                "Wave432 token/name correction: one cdecl mesh_part argument is read from ESP+4, the body first rejects exact turret token 0x0062dd20, then rejects names matching the barrel prefix token at 0x0062dd18 through the observed strn-style helper. Static retail evidence only; optimization-policy meaning and runtime behavior remain unproven.",
                false,
                new String[] { "CMeshPart__NameIsBarrelAndNotToken_62dd20" },
                tags("mesh-filter", "turret-token", "barrel-token", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x00497090",
                "CMCHiveBoss__Constructor",
                "__thiscall",
                voidPtr,
                "Wave432 lifecycle correction: RET 0x4 confirms one owner_hiveboss stack argument after this. The constructor passes owner_hiveboss+0x178 into CDestructableSegmentsMotionController__Ctor, stores owner_hiveboss at +0x10, clears cached cylinder slots +0x14..+0x74, and installs vtable 0x005dc388. Static retail evidence only; exact source identity, concrete layout, runtime HiveBoss motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCHiveBoss__ctor_like_00497090" },
                tags("cmchiveboss", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_hiveboss", voidPtr)
                }
            ),
            new Spec(
                "0x00497110",
                "CMCHiveBoss__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave432 lifecycle correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CDestructableSegmentsMotionController__DestructorThunk_00497130, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] { "CMCHiveBoss__VFunc_01_00497110" },
                tags("cmchiveboss", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x004976d0",
                "CMCHiveBoss__VFunc_04_UpdateCylinderTransforms_004976d0",
                "__thiscall",
                voidType,
                "Wave432 recovered function boundary: CMCHiveBoss vtable 0x005dc388 slot 4 points here, and the body ends with RET 0x10 before CMCMech__HasAllCylinders at 0x00498080. The function lazily calls CDestructableSegmentsMotionController__CacheNamedCollisionCylinders, applies CDestructableSegmentsMotionController__ApplyRumbleTransform, branches through cached cylinder slots, and performs shared matrix/vector transforms. Static retail evidence only; exact virtual name, argument meanings, concrete layout, runtime cylinder behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmchiveboss", "function-boundary", "vtable-slot", "collision-cylinder-cache", "signature-corrected", "comment-hardened"),
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
            throw new IllegalStateException("Wave432 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
