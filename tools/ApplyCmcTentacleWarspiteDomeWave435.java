//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCmcTentacleWarspiteDomeWave435 extends GhidraScript {
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
            "cmctentacle-warspitedome-wave435",
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
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0049cad0",
                "CMCTentacle__Constructor",
                "__thiscall",
                voidPtr,
                "Wave435 lifecycle correction: RET 0x4 confirms one owner_tentacle stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc450, stores the owner pointer at +0x08, clears the tentacle array/cache fields, and seeds +0x28 with 0xbf800000. Static retail evidence only; exact source identity, concrete CMCTentacle layout, runtime tentacle motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCTentacle__ctor_like_0049cad0" },
                tags("cmctentacle", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_tentacle", voidPtr)
                }
            ),
            new Spec(
                "0x0049cb20",
                "CMCTentacle__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave435 lifecycle correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCTentacle__Destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] { "CMCTentacle__VFunc_01_0049cb20" },
                tags("cmctentacle", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x0049cb40",
                "CMCTentacle__Destructor",
                "__fastcall",
                voidType,
                "Wave435 lifecycle correction: register-only destructor body restores vtable 0x005dc450, frees nine cached array pointers at +0x0c/+0x10/+0x14/+0x18/+0x1c/+0x20/+0xdc/+0xe0/+0xe4 when present, and tails into the base motion-controller destructor. Static retail evidence only; concrete cleanup ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCTentacle__scalar_deleting_dtor_0049cb40" },
                tags("cmctentacle", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049cc40",
                "CMCTentacle__Init",
                "__thiscall",
                voidType,
                "Wave435 signature hardening: RET 0x4 confirms one mesh_model stack argument after this. The body allocates per-bone position/matrix/timing arrays from mesh_model+0x15c/+0x160, scans names at bone+0xdc for tether/head/tethercp/headcp/tentacle/bone tokens, seeds uninitialized timing values with -1.0, and marks +0x2c initialized. Static retail evidence only; exact layout, allocator ownership, runtime initialization behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmctentacle", "init", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_model", voidPtr)
                }
            ),
            new Spec(
                "0x0049d280",
                "CMCTentacle__UpdateBone",
                "__thiscall",
                voidType,
                "Wave435 signature hardening: RET 0x4c confirms nineteen stack dwords after this. The recursive body lazily calls CMCTentacle__Init, updates tentacle bone transforms, handles tether/control/head/tentacle special cases, interpolates arrays through DAT_008a9e44, and recurses through child bones. Static retail evidence only; exact argument identities, concrete bone/layout types, runtime transform behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmctentacle", "bone-transform", "recursive", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("value_04", floatType),
                    param("value_08", floatType),
                    param("value_0c", floatType),
                    param("value_10", floatType),
                    param("value_14", floatType),
                    param("value_18", floatType),
                    param("value_1c", floatType),
                    param("value_20", intType),
                    param("value_24", floatType),
                    param("value_28", floatType),
                    param("value_2c", floatType),
                    param("value_30", intType),
                    param("value_34", floatType),
                    param("value_38", floatType),
                    param("value_3c", floatType),
                    param("value_40", intType),
                    param("value_44", intType),
                    param("value_48", intType),
                    param("value_4c", intType)
                }
            ),
            new Spec(
                "0x0049dc90",
                "CMCTentacle__Factorial",
                "__cdecl",
                intType,
                "Wave435 helper hardening: the cdecl body reads one stack integer, iteratively multiplies 2..n, and returns 1 for values below 2. The only observed callers are CMCTentacle Bezier/spline coefficient calculations. Static retail evidence only; overflow behavior and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmctentacle", "bezier-helper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("n", intType)
                }
            ),
            new Spec(
                "0x0049dcb0",
                "CMCTentacle__Power",
                "__cdecl",
                floatType,
                "Wave435 helper hardening: the cdecl body reads a float base and integer exponent from the stack, multiplies from 1.0 for each positive exponent step, and returns through the x87 float path. The observed callers use it for CMCTentacle Bezier basis terms. Static retail evidence only; edge-case math behavior and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmctentacle", "bezier-helper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("base_value", floatType),
                    param("exponent", intType)
                }
            ),
            new Spec(
                "0x0049dcd0",
                "CMCTentacle__UpdateSpline",
                "__thiscall",
                voidType,
                "Wave435 signature hardening: RET 0x4 confirms one mesh_model stack argument after this. The body lazily initializes the controller, samples tether/control/head anchors, evaluates cubic Bezier spline points with CMCTentacle__Factorial and CMCTentacle__Power, builds orientation matrices, and stores spline position/matrix arrays while using DAT_008a9e44 interpolation. Static retail evidence only; exact spline layout, runtime animation behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmctentacle", "spline", "bezier", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_model", voidPtr)
                }
            ),
            new Spec(
                "0x0049e4b0",
                "CMCTentacle__BuildOrientationMatrix",
                "__thiscall",
                voidType,
                "Wave435 signature hardening: RET 0x20 confirms eight stack dwords after the ECX output matrix pointer, represented as the this receiver for Ghidra calling-convention read-back. The body negates the direction vector, crosses it with the supplied up vector, normalizes the derived right/up/direction axes, and writes a 3x4-style basis at output offsets 0..0x28. Static retail evidence only; exact vector lane semantics, matrix convention, runtime math behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmctentacle", "matrix-helper", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", floatPtr),
                    param("dir_x", floatType),
                    param("dir_y", floatType),
                    param("dir_z", floatType),
                    param("dir_w", intType),
                    param("up_x", floatType),
                    param("up_y", floatType),
                    param("up_z", floatType),
                    param("up_w", intType)
                }
            ),
            new Spec(
                "0x0049e660",
                "CMCTentacle__VFunc_04_UpdateInterpolatedBoneTransform_0049e660",
                "__thiscall",
                voidType,
                "Wave435 recovered function boundary: CMCTentacle vtable 0x005dc450 slot 4 points here and the body ends with RET 0x10 before slot 5 at 0x0049ead0. The function lazily updates spline/bone state, calls CMCTentacle__UpdateSpline and CMCTentacle__UpdateBone, interpolates cached arrays through DAT_008a9e44, and writes an output transform. Static retail evidence only; exact virtual name, argument meanings, concrete layout, runtime tentacle transform behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmctentacle", "function-boundary", "vtable-slot", "bone-transform", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("transform_a", voidPtr),
                    param("transform_b", voidPtr),
                    param("context_value", intType)
                }
            ),
            new Spec(
                "0x0049ead0",
                "CMCTentacle__VFunc_05_WriteInterpolatedBoneFloat_0049ead0",
                "__thiscall",
                voidType,
                "Wave435 recovered function boundary: CMCTentacle vtable 0x005dc450 slot 5 points here and RET 0x8 confirms two stack arguments after this. The body updates spline/bone state when the cached +0x28 timestamp differs, reads mesh_part+0x88 as an index, and writes either an interpolated value using DAT_008a9e44 or a cached value to out_value. Static retail evidence only; exact virtual name, output semantics, concrete layout, runtime bone-value behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmctentacle", "function-boundary", "vtable-slot", "bone-value", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("out_value", voidPtr)
                }
            ),
            new Spec(
                "0x0049ec80",
                "CMCTentacle__VFunc_08_CheckCachedUpdateTime_0049ec80",
                "__fastcall",
                boolType,
                "Wave435 recovered function boundary: CMCTentacle vtable 0x005dc450 slot 8 points here. The short body compares global float 0x00672fd0 against cached this+0x28 and returns true when they differ, terminating before CMeshPart__NameAvoidsTentacleOptimizationTokens at 0x0049eca0. Static retail evidence only; exact virtual name, timestamp semantics, runtime behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmctentacle", "function-boundary", "vtable-slot", "state-flag", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049eca0",
                "CMeshPart__NameAvoidsTentacleOptimizationTokens",
                "__cdecl",
                boolType,
                "Wave435 owner/name correction: one cdecl mesh_part argument is read from ESP+4, the mesh-part name at +0xdc is checked against exact tether/head/tethercp/headcp/tentacle tokens and the four-byte prefix bone. The predicate returns false for matching protected names and true otherwise, matching CMeshPart optimization callers. Static retail evidence only; exact optimization-policy meaning, runtime mesh behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCTentacle__ValidateBoneStructure" },
                tags("mesh-filter", "tentacle-token-filter", "renamed", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x0049ed30",
                "CMesh__HasTentacleBone",
                "__cdecl",
                boolType,
                "Wave435 owner/name correction: one cdecl mesh_model argument is read from ESP+4. The body iterates mesh_model+0x15c bones through the +0x160 pointer table, compares each bone name at +0xdc against the exact tentacle token, and returns true on the first match. Static retail evidence only; exact mesh layout, optimization-policy meaning, runtime mesh behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCTentacle__HasTentacleBone" },
                tags("mesh-filter", "tentacle-token-filter", "renamed", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("mesh_model", voidPtr)
                }
            ),
            new Spec(
                "0x0049ef80",
                "CMCWarspiteDome__Constructor",
                "__thiscall",
                voidPtr,
                "Wave435 lifecycle correction: RET 0x4 confirms one owner_dome stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc484, and stores the owner pointer at +0x08. Static retail evidence only; exact source identity, concrete CMCWarspiteDome layout, runtime dome motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCWarspiteDome__ctor_like_0049ef80" },
                tags("cmcwarspitedome", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_dome", voidPtr)
                }
            ),
            new Spec(
                "0x0049efa0",
                "CMCWarspiteDome__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave435 lifecycle correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCWarspiteDome__Destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] { "CMCWarspiteDome__VFunc_01_0049efa0" },
                tags("cmcwarspitedome", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x0049efc0",
                "CMCWarspiteDome__Destructor",
                "__fastcall",
                voidType,
                "Wave435 lifecycle correction: register-only destructor body restores vtable 0x005dc484, clears +0x08, and tails into the base motion-controller destructor. Static retail evidence only; concrete cleanup ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCWarspiteDome__ctor_like_0049efc0" },
                tags("cmcwarspitedome", "destructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049efe0",
                "CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0",
                "__thiscall",
                voidType,
                "Wave435 recovered function boundary: CMCWarspiteDome vtable 0x005dc484 slot 4 points here and RET 0x10 confirms four stack arguments. The body checks the mesh-part name against the dome token at 0x0062e0cc, builds orientation/position transforms from owner fields, applies DAT_008a9e44 interpolation, and adjusts output height against owner +0x250 when context +0x88 is clear. Static retail evidence only; exact virtual name, argument meanings, concrete layout, runtime dome transform behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcwarspitedome", "function-boundary", "vtable-slot", "dome-token", "signature-corrected", "comment-hardened"),
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
            throw new IllegalStateException("Wave435 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
