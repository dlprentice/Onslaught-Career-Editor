//@category Symbol

import ghidra.app.script.GhidraScript;
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

public class ApplyCmcBuggyWave430 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Function fn = getFunctionAt(toAddr(addressText));
        if (fn == null) {
            fn = getFunctionContaining(toAddr(addressText));
            if (fn != null && !fn.getEntryPoint().equals(toAddr(addressText))) {
                fn = null;
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
            "cmcbuggy-wave430",
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
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
                return;
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

            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00493020",
                "CMCBuggy__CMCBuggy",
                "__thiscall",
                voidPtr,
                "Wave430 signature/comment correction: RET 0x4 confirms one owner/model stack argument after the CMCBuggy this pointer. The constructor calls the base motion-controller constructor, installs vtable 0x005dc250, stores the owner pointer at +0x08, clears wheel buffer fields, seeds +0x3c with -1.0f, and leaves runtime wheel behavior/concrete layout/rebuild parity unproven.",
                new String[] {},
                tags("cmcbuggy", "constructor", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_model", voidPtr)
                }
            ),
            new Spec(
                "0x00493080",
                "CMCBuggy__scalar_deleting_destructor",
                "__thiscall",
                voidPtr,
                "Wave430 signature/comment correction: RET 0x4 confirms one delete-flags stack argument. The wrapper calls CMCBuggy__destructor, frees this through OID__FreeObject only when flags bit 0 is set, and returns this. Static retail evidence only; allocator identity beyond the observed call and runtime destruction behavior remain unproven.",
                new String[] {},
                tags("cmcbuggy", "destructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x004930a0",
                "CMCBuggy__destructor",
                "__fastcall",
                voidType,
                "Wave430 signature/comment correction: RET with no stack cleanup confirms a register-only destructor body. It restores vtable 0x005dc250, frees observed wheel/motion buffers at +0x0c/+0x10/+0x24/+0x28/+0x2c/+0x30/+0x34/+0x38 when non-null, and then calls the base motion-controller destructor. Static retail evidence only; concrete ownership semantics and runtime destruction coverage remain unproven.",
                new String[] {},
                tags("cmcbuggy", "destructor", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00493180",
                "CMCBuggy__SetFieldC0",
                "__thiscall",
                voidType,
                "Wave430 rename/signature correction: RET 0x4 confirms one stack value, and the entire body writes that value to CMCBuggy offset +0xc0. The old SetC0 label was retained only as an allowed preflight name; the field purpose, caller intent from CGroundVehicle__Init, runtime effect, and rebuild parity remain unproven.",
                new String[] { "CMCBuggy__SetC0" },
                tags("cmcbuggy", "field-setter", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("field_c0_value", intType)
                }
            ),
            new Spec(
                "0x00493190",
                "CMCBuggy__Init",
                "__thiscall",
                voidType,
                "Wave430 signature/comment correction: RET 0x4 confirms one mesh/model stack argument. The body lazily counts WheelBase slots, allocates wheel buffers, resolves the WheelMotion animation token, initializes -1.0f contact sentinels, and builds cached wheel motion pose data. Static retail evidence only from MCBuggy.cpp token/debug-path context; concrete mesh layout, runtime wheel initialization, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmcbuggy", "wheel-motion", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_model", voidPtr)
                }
            ),
            new Spec(
                "0x004934f0",
                "CMCBuggy__UpdateWheel",
                "__thiscall",
                voidType,
                "Wave430 signature/comment correction: RET 0x50 confirms twenty stack arguments after this: a position vector, twelve transform/basis floats, an owner vehicle pointer, a mesh-part/owner token, a wheel index, and a final context value. The body profiles with rdtsc, lazily calls CMCBuggy__Init, resolves WheelBase/WheelMotion data, samples heightfield normals, recurses through child wheel parts, and updates cached wheel transforms. Static retail evidence only; exact type layout, runtime vehicle behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmcbuggy", "wheel-motion", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position_x", floatType),
                    param("position_y", floatType),
                    param("position_z", floatType),
                    param("position_w", floatType),
                    param("basis0_x", floatType),
                    param("basis0_y", floatType),
                    param("basis0_z", floatType),
                    param("basis0_w", intType),
                    param("basis1_x", floatType),
                    param("basis1_y", floatType),
                    param("basis1_z", floatType),
                    param("basis1_w", intType),
                    param("basis2_x", floatType),
                    param("basis2_y", floatType),
                    param("basis2_z", floatType),
                    param("basis2_w", intType),
                    param("owner_vehicle", voidPtr),
                    param("mesh_part_owner", voidPtr),
                    param("wheel_index", intType),
                    param("context_value", intType)
                }
            ),
            new Spec(
                "0x00494310",
                "CMCBuggy__ProfileEnd",
                "__fastcall",
                voidType,
                "Wave430 signature/comment correction: RET with no stack cleanup confirms a register-only profiling epilogue helper. The body reads rdtsc, indexes profiler buckets by the first dword of the passed scope, accumulates elapsed cycles under DAT_0082ce84, and increments the matching call count under DAT_0082d054. Static retail evidence only; profiler bucket meaning and runtime timing coverage remain unproven.",
                new String[] {},
                tags("cmcbuggy", "profiling", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("profile_scope", voidPtr)
                }
            ),
            new Spec(
                "0x00494350",
                "Mat34__InvertBasisToOut",
                "__thiscall",
                voidType,
                "Wave430 owner/name correction: RET 0x4 confirms one output-matrix stack argument after the ECX/source matrix pointer, and xrefs from CDXEngine, CMCBuggy, and other mesh/math callers show this is not CMCBuggy-owned. The body computes a 3x3 adjugate/determinant from the source matrix, divides basis vectors through Vec3__DivideInPlaceByScalar, and copies twelve floats to the output matrix. Static retail evidence only; singular-matrix behavior and rebuild parity remain unproven.",
                new String[] { "CMCBuggy__InvertMatrix" },
                tags("math-helper", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "multi-caller"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("out_matrix", voidPtr)
                }
            ),
            new Spec(
                "0x004944b0",
                "Vec3__DivideInPlaceByScalar",
                "__thiscall",
                voidType,
                "Wave430 owner/name correction: RET 0x4 confirms one scalar stack argument after the ECX/vector pointer, and xrefs from CMeshPart, CMeshRenderer, CMCMech, CPDSimpleSprite, and Mat34__InvertBasisToOut show this is a shared vector helper rather than CMCBuggy-owned. The body divides the first three floats of the vector in place by the scalar. Static retail evidence only; divide-by-zero handling and rebuild parity remain unproven.",
                new String[] { "CMCBuggy__DivideVector" },
                tags("math-helper", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "multi-caller"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("scalar", floatType)
                }
            ),
            new Spec(
                "0x00494b00",
                "CMeshPart__NameAvoidsBodyAxleWheelTokens",
                "__cdecl",
                boolType,
                "Wave430 name/signature correction: RET with no stack cleanup plus caller cleanup confirm one cdecl mesh-part argument. String read-back proves the rejected tokens are Body, Axle, and Wheel; the function returns false for exact Body or names beginning Axle/Wheel and true otherwise. This corrects the older backward NameMatchesWheelTokenSet label. Static retail evidence only; optimization-policy meaning and rebuild parity remain unproven.",
                new String[] { "CMeshPart__NameMatchesWheelTokenSet" },
                tags("mesh-filter", "token-readback", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x00494b50",
                "CMeshPart__HasWheelMotionAnimation",
                "__cdecl",
                boolType,
                "Wave430 name/signature correction: the body loads one mesh-part argument from [ESP+4], pushes the WheelMotion token at 0x0062cb54, calls FindAnimationIndex, and returns true when the index is not -1. Caller cleanup and RET with no stack cleanup support cdecl. Static retail evidence only; animation-table layout and runtime optimization behavior remain unproven.",
                new String[] { "CMeshPart__HasAnimationToken_62cb54" },
                tags("mesh-filter", "wheel-motion", "token-readback", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x00494c60",
                "CDestructableSegmentsMotionController__Ctor",
                "__thiscall",
                voidPtr,
                "Wave430 signature/comment correction: RET 0x4 proves the earlier two-stack-argument signature was too wide. The constructor calls the base motion-controller constructor, installs vtable 0x005dc27c, stores the supplied segment/controller pointer at +0x0c, and caches +0x10+8 at +0x08 when present. Xrefs currently include CMCHiveBoss__ctor_like_00497090 and the vtable appears as a nested table after CMCBuggy slots; exact class ownership/layout and runtime behavior remain unproven.",
                new String[] { "CDestructableSegmentsMotionController__ctor_like_00494c60" },
                tags("destructable-segments", "constructor", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("segment_controller", voidPtr)
                }
            ),
            new Spec(
                "0x00494ca0",
                "CDestructableSegmentsMotionController__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave430 owner/signature correction: RET 0x4 confirms one delete-flags stack argument. Vtable read-back places this at 0x005dc27c slot 1, adjacent to the 0x00494c60 constructor and shared motion-controller slots, so the older CMCBuggy wheel-specific owner label was too narrow. The wrapper calls the local destructor and conditionally frees this when flags bit 0 is set. Static retail evidence only; exact class ownership and runtime destruction coverage remain unproven.",
                new String[] { "CMCBuggy__WheelScalarDelDtor" },
                tags("destructable-segments", "destructor", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                }
            ),
            new Spec(
                "0x00494cc0",
                "CDestructableSegmentsMotionController__Destructor",
                "__fastcall",
                voidType,
                "Wave430 owner/signature correction: the body has no stack cleanup, restores vtable 0x005dc27c, clears +0x08/+0x0c, and calls the base motion-controller destructor. Vtable/read-back context makes the older CMCBuggy wheel-specific owner label too narrow. Static retail evidence only; exact class ownership, duplicated destructor-like body at 0x00497130, and runtime destruction coverage remain unproven.",
                new String[] { "CMCBuggy__WheelDestructor" },
                tags("destructable-segments", "destructor", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00494ce0",
                "CDestructableSegmentsMotionController__ApplyRumbleTransform",
                "__thiscall",
                voidType,
                "Wave430 owner/signature correction: RET 0x10 confirms four stack arguments after this. Vtable read-back places this at 0x005dc27c slot 4. The body samples a target/fallback value, accumulates it into a per-segment state field, clamps/uses trigonometric rotation terms, writes rotated Mat34 rows back into the supplied transform, and clears the pointed source flag. Static retail evidence only; exact class ownership, target semantics, runtime rumble behavior, and rebuild parity remain unproven.",
                new String[] { "CMCBuggy__ApplyWheelRumble" },
                tags("destructable-segments", "rumble-transform", "owner-corrected", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("state_context", voidPtr),
                    param("segment_state", voidPtr),
                    param("transform", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave430 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
