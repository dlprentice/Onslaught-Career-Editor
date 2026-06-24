//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCmcMechWave433 extends GhidraScript {
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
            "cmcmech-wave433",
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
        DataType floatType = FloatDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00498080",
                "CMeshPart__NameIsNotAnyMechCylinderBone",
                "__cdecl",
                boolType,
                "Wave433 owner/name correction: one cdecl mesh_part argument is read from ESP+4, then the mesh-part name at +0xdc is compared against the 24 observed mech hydraulic-cylinder bone names from 0x0062de04..0x0062df18. The predicate returns false for matching cylinder names and true otherwise. Static retail evidence only; optimization-policy meaning, concrete mesh layout, runtime mech rendering behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCMech__HasAllCylinders" },
                tags("mesh-filter", "mech-cylinder-token", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x00498270",
                "CMeshPart__AnyChildNameIsNmidoutcyl",
                "__cdecl",
                boolType,
                "Wave433 owner/name correction: one cdecl mesh_part argument is read from ESP+4, child count +0x15c and child pointer table +0x160 are walked, and child names at +0xdc are compared against Nmidoutcyl at 0x0062df18. Static retail evidence only; optimization-policy meaning, concrete mesh layout, runtime child-bone behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMCMech__HasCylinderBones" },
                tags("mesh-filter", "mech-cylinder-token", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x004983b0",
                "CMCMech__Constructor",
                "__thiscall",
                voidPtr,
                "Wave433 lifecycle hardening: RET 0x4 confirms one float-like stack argument after this. The constructor calls the base motion-controller constructor, installs vtable 0x005dc3b4, seeds defaults including +0x08/+0x0c/+0x10/+0xc8, schedules the 3000 tick event through EVENT_MANAGER, and links this into global list 0x00704650. Static retail evidence only; exact source identity, concrete CMCMech layout, runtime leg-motion behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "constructor", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("initial_value", floatType)
                }
            ),
            new Spec(
                "0x00498510",
                "CMCMech__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave433 lifecycle hardening: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCMech__Destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership and runtime destruction behavior remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "destructor", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x00498530",
                "CMCMech__Destructor",
                "__fastcall",
                voidType,
                "Wave433 lifecycle hardening: register-only destructor restores vtable 0x005dc3b4, unlinks this from global list 0x00704650, frees shared leg/toe/matrix caches only when no remaining instance references the same +0xe4 shared block, frees instance arrays, and tails into the base motion-controller destructor. Static retail evidence only; concrete ownership, runtime cleanup behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "destructor", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00498870",
                "CMCMech__VFunc_00_OnTimedResetEvent_00498870",
                "__thiscall",
                voidType,
                "Wave433 recovered function boundary: CMCMech vtable 0x005dc3b4 slot 0 points here, the body compares event_record+4 against 0x0bb8, calls CMCMech__Reset(this,0,0), then requeues event 0x0bb8 with -1.0 timing through EVENT_MANAGER. Static retail evidence only; exact virtual name, event-record layout, runtime scheduling behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcmech", "function-boundary", "vtable-slot", "timed-event", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("event_record", voidPtr)
                }
            ),
            new Spec(
                "0x004988b0",
                "CMCMech__Reset",
                "__thiscall",
                voidType,
                "Wave433 reset hardening: RET 0x8 confirms two stack dwords after this. The first stack dword selects the alternate start-pose reset branch observed from vtable slots; callers pass (0,0) from the timed event and (1,0) from transform/value slots, while the second cleaned dword is not semantically isolated yet. The body gates repeated resets through +0x50/+0x54/+0xcc, pulls the owner's model child table, calls CMCMech__UpdateBone and CMCMech__UpdateBoneHierarchyRecursive, then refreshes +0x4c/+0x50/+0xc8. Static retail evidence only; exact source identity, concrete layout, runtime leg reset behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "reset", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("start_pose_flag", intType),
                    param("reserved_cleaned_arg", intType)
                }
            ),
            new Spec(
                "0x00498bf0",
                "CMCMech__SetParams",
                "__thiscall",
                voidType,
                "Wave433 parameter hardening: RET 0x1c confirms seven stack dwords after this. The body stores arguments into +0x98, +0x9c, +0xa0, +0x0c, +0x10, +0xa4, and +0xc4 in that observed order. Static retail evidence only; semantic parameter names, concrete layout, runtime tuning behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "parameters", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("value_98", floatType),
                    param("value_9c", floatType),
                    param("value_a0", floatType),
                    param("value_0c", floatType),
                    param("value_10", floatType),
                    param("value_a4", floatType),
                    param("value_c4", floatType)
                }
            ),
            new Spec(
                "0x00498c40",
                "CMCMech__Init",
                "__thiscall",
                voidType,
                "Wave433 init hardening: RET 0x4 confirms one mesh_model stack argument after this. The body stores mesh_model at +0xe8, reuses a shared +0xe4 cache from another instance with the same model when possible, allocates shared/instance leg arrays with MCMech.cpp file-line evidence, counts Footbase/toestop slots, resolves ToeMotion/LegMotion ranges, classifies mesh-part token groups, and seeds per-leg/toe data. Static retail evidence only; concrete layout, exact source parity, runtime leg IK behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "init", "signature-corrected", "comment-hardened", "source-path-evidence"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_model", voidPtr)
                }
            ),
            new Spec(
                "0x00499bc0",
                "CMCMech__GetFootHeight",
                "__thiscall",
                floatType,
                "Wave433 helper hardening: RET 0x0c confirms three stack dwords after the ECX height context. The body samples static-shadow height, optionally constructs a CLine trace with +10/-2 vertical offsets, calls OID__TraceLineAndSelectBestTargetHit, and returns the lower of sampled shadow/trace-derived heights. Static retail evidence only; exact context type, terrain semantics, runtime foot placement behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "terrain-height", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position_vec4", voidPtr),
                    param("trace_context", voidPtr),
                    param("shadow_only_flag", intType)
                }
            ),
            new Spec(
                "0x00499d60",
                "CMCMech__TranslatePositions",
                "__thiscall",
                voidType,
                "Wave433 helper hardening: RET 0x4 confirms one translation_vec3 stack argument after this. The body adds the translation to per-leg arrays at +0x14/+0x24 and, when an owner mesh exists at +0xe8, to the per-mesh-part array at +0x34 using owner child count +0x15c. Static retail evidence only; concrete array layout, runtime translation behavior, and rebuild parity remain unproven.",
                false,
                new String[] {},
                tags("cmcmech", "translation", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("translation_vec3", voidPtr)
                }
            ),
            new Spec(
                "0x0049bbb0",
                "MathMatrix3x3__DivideByScalarInPlace",
                "__thiscall",
                voidType,
                "Wave433 signature correction: RET 0x4 confirms one scalar stack float after this. The body divides the 3x3 matrix entries at offsets 0,4,8,0x10,0x14,0x18,0x20,0x24,0x28 by that scalar. Static retail evidence only; matrix storage convention and runtime math behavior remain unproven.",
                false,
                new String[] {},
                tags("matrix3x3", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("scalar", floatType)
                }
            ),
            new Spec(
                "0x0049bc10",
                "MathMatrix3x3__TransposeInPlace",
                "__fastcall",
                voidType,
                "Wave433 signature hardening: register-only helper swaps off-diagonal 3x3 entries at offsets 4/0x10, 8/0x20, and 0x18/0x24 in place. Static retail evidence only; matrix storage convention and runtime math behavior remain unproven.",
                false,
                new String[] {},
                tags("matrix3x3", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("matrix3x3", voidPtr)
                }
            ),
            new Spec(
                "0x0049bc40",
                "MathMatrix3x3__Determinant",
                "__fastcall",
                doubleType,
                "Wave433 signature hardening: register-only helper computes the 3x3 determinant from entries at offsets 0..0x28 and returns through the x87 path reflected by Ghidra as double. Static retail evidence only; matrix storage convention and runtime math behavior remain unproven.",
                false,
                new String[] {},
                tags("matrix3x3", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("matrix3x3", voidPtr)
                }
            ),
            new Spec(
                "0x0049bc80",
                "MathMatrix3x3__BuildCofactorMatrix",
                "__thiscall",
                voidType,
                "Wave433 signature correction: RET 0x4 confirms one out_matrix3x3 stack argument after this. The body computes cofactors from the source matrix in this and copies the 3x3 result to out_matrix3x3. Static retail evidence only; exact matrix convention and runtime math behavior remain unproven.",
                false,
                new String[] {},
                tags("matrix3x3", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_matrix3x3", voidPtr)
                }
            ),
            new Spec(
                "0x0049be00",
                "CMCMech__VFunc_04_UpdateInterpolatedBoneTransform_0049be00",
                "__thiscall",
                voidType,
                "Wave433 recovered function boundary: CMCMech vtable 0x005dc3b4 slot 4 points here, and the body ends with RET 0x10 before slot 5 at 0x0049c1d0. The function forces CMCMech__Reset(this,1,0) when +0x54 is clear, interpolates cached vector/matrix arrays through DAT_008a9e44, and calls the MathMatrix3x3 cofactor/transpose/determinant/divide helpers before writing an output transform. Static retail evidence only; exact virtual name, argument meanings, concrete layout, runtime bone-transform behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcmech", "function-boundary", "vtable-slot", "bone-transform", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("transform_a", voidPtr),
                    param("transform_b", voidPtr),
                    param("context_value", intType)
                }
            ),
            new Spec(
                "0x0049c1d0",
                "CMCMech__VFunc_05_WriteInterpolatedBoneFloat_0049c1d0",
                "__thiscall",
                voidType,
                "Wave433 vtable-slot correction: CMCMech vtable 0x005dc3b4 slot 5 points here, and RET 0x8 confirms two stack arguments after this. The body forces CMCMech__Reset(this,1,0) when +0x54 is clear, sets +0x50 and +0xc8 state, reads mesh_part+0x88 as an index, and writes either an interpolated value from +0x38/+0x44 using DAT_008a9e44 or the cached +0x38 value to out_value. Static retail evidence only; exact virtual name, output semantics, concrete layout, runtime bone-value behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "VFuncSlot_05_0049c1d0" },
                tags("cmcmech", "vtable-slot", "bone-value", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_part", voidPtr),
                    param("out_value", voidPtr)
                }
            ),
            new Spec(
                "0x0049c240",
                "CMCMech__VFunc_08_GetUpdateStateFlag_0049c240",
                "__fastcall",
                intType,
                "Wave433 recovered function boundary: CMCMech vtable 0x005dc3b4 slot 8 points here. The body is a one-dword getter that returns this+0xc8 and terminates before CMeshPart__NameAvoidsMechOptimizationTokens at 0x0049c250. Static retail evidence only; exact virtual name, flag semantics, runtime behavior, and rebuild parity remain unproven.",
                true,
                new String[] {},
                tags("cmcmech", "function-boundary", "vtable-slot", "state-flag", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049c250",
                "CMeshPart__NameAvoidsMechOptimizationTokens",
                "__cdecl",
                boolType,
                "Wave433 token/name correction: one cdecl mesh_part argument is read from ESP+4, the mesh-part name at +0xdc is checked against exact token 0x0062dcbc, prefixes 0x0062df3c/0x0062df34/0x0062df30, and exact token 0x0062dd20. The predicate returns false for matching protected names and true otherwise. Static retail evidence only; exact token strings, optimization-policy meaning, runtime mesh behavior, and rebuild parity remain unproven.",
                false,
                new String[] { "CMeshPart__NameMatchesTokenSet_62df3c_62df34_62df30" },
                tags("mesh-filter", "mech-token-filter", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
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
            throw new IllegalStateException("Wave433 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
