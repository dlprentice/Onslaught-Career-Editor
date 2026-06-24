//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
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

public class ApplyMathDispatchWave660 extends GhidraScript {
    private static class Spec {
        final String address;
        final String endAddress;
        final String nextAddress;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;
        final boolean createIfMissing;

        Spec(
                String address,
                String endAddress,
                String nextAddress,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags,
                boolean createIfMissing) {
            this.address = address;
            this.endAddress = endAddress;
            this.nextAddress = nextAddress;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
            this.tags = tags;
            this.createIfMissing = createIfMissing;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int created = 0;
        int wouldCreate = 0;
        int bodySet = 0;
        int wouldSetBody = 0;
        int signatureUpdated = 0;
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
            "math-dispatch-wave660",
            "retail-binary-evidence",
            "signature-hardened",
            "comment-hardened"
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
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsBodySet(Function fn, Spec spec) {
        if (!spec.createIfMissing) {
            return false;
        }
        return !fn.getBody().contains(addr(spec.address)) || !fn.getBody().contains(addr(spec.endAddress));
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        if (!hasAllTags(fn, spec.tags)) {
            return true;
        }
        return needsBodySet(fn, spec);
    }

    private void setBody(Function fn, Spec spec) throws Exception {
        if (!spec.createIfMissing) {
            return;
        }
        AddressSet body = new AddressSet(addr(spec.address), addr(spec.endAddress));
        fn.setBody(body);
    }

    private Function createFunctionAt(Spec spec) throws Exception {
        Address start = addr(spec.address);
        Address end = addr(spec.endAddress);
        AddressSet range = new AddressSet(start, end);
        DisassembleCommand disassemble = new DisassembleCommand(start, range, true);
        disassemble.applyTo(currentProgram, monitor);
        Function fn = createFunction(start, spec.name);
        if (fn == null) {
            fn = functionAtEntry(spec.address);
        }
        if (fn == null) {
            throw new IllegalStateException("Function create failed at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
        }
        setBody(fn, spec);
        return fn;
    }

    private void applyMetadata(Function fn, Spec spec, Stats stats) throws Exception {
        if (!fn.getName().equals(spec.name)) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (needsBodySet(fn, spec)) {
            setBody(fn, spec);
            stats.bodySet++;
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
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
        if (spec.createIfMissing) {
            Address start = addr(spec.address);
            Address end = addr(spec.endAddress);
            Address next = addr(spec.nextAddress);
            if (!readBack.getBody().contains(start)) {
                throw new IllegalStateException("Read-back body does not contain start " + spec.address);
            }
            if (!readBack.getBody().contains(end)) {
                throw new IllegalStateException("Read-back body does not contain terminal RET " + spec.endAddress);
            }
            Function nextFn = getFunctionAt(next);
            if (nextFn == null) {
                throw new IllegalStateException("Next function missing at " + spec.nextAddress);
            }
            if (readBack.getBody().contains(next)) {
                throw new IllegalStateException("Recovered body overlaps next function at " + spec.nextAddress);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Address start = addr(spec.address);
            Function containingStart = getFunctionContaining(start);
            if (containingStart != null && !containingStart.getEntryPoint().equals(start)) {
                stats.bad++;
                println("BAD: " + spec.address + " is inside " + containingStart.getName());
                return;
            }

            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                if (!spec.createIfMissing) {
                    stats.missing++;
                    println("MISSING: " + spec.address + " " + spec.name);
                    return;
                }
                if (dryRun) {
                    stats.wouldCreate++;
                    stats.wouldSetBody++;
                    stats.skipped++;
                    println("DRYCREATE: " + spec.address + " " + expectedSignature(spec)
                        + " body=" + spec.address + "-" + spec.endAddress);
                    return;
                }
                Function created = createFunctionAt(spec);
                stats.created++;
                stats.bodySet++;
                applyMetadata(created, spec, stats);
                verifyReadBack(spec);
                stats.updated++;
                println("OKCREATE: " + spec.address + " " + expectedSignature(spec)
                    + " body=" + spec.address + "-" + spec.endAddress);
                Thread.sleep(50);
                return;
            }

            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsBody = needsBodySet(fn, spec);
            if (!needsUpdate(fn, spec)) {
                verifyReadBack(spec);
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                if (needsSignature) {
                    stats.signatureUpdated++;
                }
                if (needsBody) {
                    stats.wouldSetBody++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getSignature()
                    + " -> " + expectedSignature(spec));
                return;
            }

            applyMetadata(fn, spec, stats);
            verifyReadBack(spec);
            stats.updated++;
            if (needsSignature) {
                stats.signatureUpdated++;
            }
            println("OK: " + spec.address + " " + expectedSignature(spec));
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " "
                + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType floatType = FloatDataType.dataType;
        DataType floatPtr = new PointerDataType(floatType);
        DataType intType = IntegerDataType.dataType;

        String staticEvidence = "Static retail decompile/instruction/dispatch-table evidence only; exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005776a5",
                null,
                null,
                "CTexture__DispatchPtr00656fd0_WithInit",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("slot_arg0", intType),
                    param("slot_arg1", intType),
                    param("slot_arg2", intType),
                    param("slot_arg3", intType)
                },
                "Wave660 math dispatch continuation: runtime dispatch-table slot 40 at 0x00656fd0 calls CFastVB__InitDispatchTableByCpuFeature(1), repacks four slot arguments, then calls the active slot implementation. The paired source/default slot 40 at 0x006570f0 points to 0x0057923a CTexture__DispatchMatrixOp00656f94_WithPostOp; this row keeps the existing owner label and defers the slot argument/storage contract. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "deferred-contract"),
                false
            ),
            new Spec(
                "0x0057798e",
                null,
                null,
                "CFastVB__BuildAxisAngleQuaternion_Dispatch",
                "__stdcall",
                floatPtr,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("axis_vec3", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave660 math dispatch continuation: runtime dispatch-table slot 29 at 0x00656fa4 initializes the CPU-selected table, repacks out_quaternion_xyzw, axis_vec3, and angle_radians, then calls the active implementation. The paired source/default slot 29 at 0x006570c4 points to 0x005779ae. " + staticEvidence,
                new String[] { "CFastVB__DispatchIndirect_00656fa4" },
                tags("dispatch-table", "quaternion", "axis-angle"),
                false
            ),
            new Spec(
                "0x005779ae",
                null,
                null,
                "CFastVB__BuildAxisAngleQuaternion",
                "__stdcall",
                floatPtr,
                new ParameterImpl[] {
                    param("out_quaternion_xyzw", voidPtr),
                    param("axis_vec3", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 29 at 0x006570c4 points here; the body calls Runtime__CallIndirectThunk_00575d99, uses x87 FSIN/FCOS operations over angle_radians scaled by 0x005e72d4, writes four quaternion floats, and returns the output pointer. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "quaternion", "axis-angle"),
                false
            ),
            new Spec(
                "0x00577a0a",
                null,
                null,
                "Math__BuildEulerRotationMatrix4x4_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_x_radians", floatType),
                    param("angle_y_radians", floatType),
                    param("angle_z_radians", floatType)
                },
                "Wave660 math dispatch continuation: runtime dispatch-table slot 25 at 0x00656f94 initializes the CPU-selected table, repacks out_matrix4x4 plus three angle operands, then calls the active implementation. The paired source/default slot 25 at 0x006570b4 points to the recovered 0x00577a3e Euler rotation matrix builder. " + staticEvidence,
                new String[] { "CFastVB__DispatchIndirect_00656f94" },
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "euler"),
                false
            ),
            new Spec(
                "0x00577a38",
                null,
                null,
                "Math__BuildEulerRotationMatrix4x4_Dispatch_Thunk",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_x_radians", floatType),
                    param("angle_y_radians", floatType),
                    param("angle_z_radians", floatType)
                },
                "Wave660 math dispatch continuation: pure jump thunk to runtime dispatch-table slot 25 at 0x00656f94, sharing the Euler rotation matrix call contract with the initialized dispatcher at 0x00577a0a. " + staticEvidence,
                new String[] { "CTexture__DispatchPtr00656f94_NoInit" },
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "euler", "jump-thunk"),
                false
            ),
            new Spec(
                "0x00577a3e",
                "0x00577b14",
                "0x00577b17",
                "Math__BuildEulerRotationMatrix4x4",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_x_radians", floatType),
                    param("angle_y_radians", floatType),
                    param("angle_z_radians", floatType)
                },
                "Wave660 math dispatch boundary recovery: source/default dispatch-table slot 25 at 0x006570b4 points here; the body uses repeated FSINCOS operations over three angles scaled by 0x005e72d4, writes a 4x4 rotation matrix, and returns with RET 0x10 at 0x00577b14. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "boundary-recovered", "matrix4x4", "rotation-matrix", "euler"),
                true
            ),
            new Spec(
                "0x00577e80",
                null,
                null,
                "Math__InterpolateVec4ByRatio_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("from_vec4", voidPtr),
                    param("to_vec4", voidPtr),
                    param("ratio", floatType)
                },
                "Wave660 math dispatch continuation: runtime dispatch-table slot 35 at 0x00656fbc initializes the CPU-selected table, repacks out_vec4/from_vec4/to_vec4/ratio, then calls the active vec4 interpolation implementation. The paired source/default slot 35 at 0x006570dc points to recovered 0x00577eaa. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "vec4", "interpolation"),
                false
            ),
            new Spec(
                "0x00577ea4",
                null,
                null,
                "Math__InterpolateVec4ByRatio_Dispatch_Thunk",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("from_vec4", voidPtr),
                    param("to_vec4", voidPtr),
                    param("ratio", floatType)
                },
                "Wave660 math dispatch continuation: pure jump thunk to runtime dispatch-table slot 35 at 0x00656fbc, sharing the vec4 interpolation call contract with the initialized dispatcher at 0x00577e80. " + staticEvidence,
                new String[] { "Math__InterpolateVec4ByRatio_Dispatch_00577ea4" },
                tags("dispatch-table", "vec4", "interpolation", "jump-thunk"),
                false
            ),
            new Spec(
                "0x00577eaa",
                "0x00577f8a",
                "0x00577f8d",
                "Math__InterpolateVec4ByRatio",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("from_vec4", voidPtr),
                    param("to_vec4", voidPtr),
                    param("ratio", floatType)
                },
                "Wave660 math dispatch boundary recovery: source/default dispatch-table slot 35 at 0x006570dc points here; the body computes vec4 dot/sign terms, applies sine-weighted ratio blending when needed, writes four floats to out_vec4, and returns with RET 0x10 at 0x00577f8a. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "boundary-recovered", "vec4", "interpolation"),
                true
            ),
            new Spec(
                "0x00577f8d",
                null,
                null,
                "Math__BezierBlendVec4_Dispatch",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("control0_vec4", voidPtr),
                    param("control1_vec4", voidPtr),
                    param("control2_vec4", voidPtr),
                    param("control3_vec4", voidPtr),
                    param("ratio", floatType)
                },
                "Wave660 math dispatch continuation: runtime dispatch-table slot 43 at 0x00656fdc initializes the CPU-selected table, repacks four vec4 controls plus ratio, then calls the active Bezier vec4 implementation. The paired source/default slot 43 at 0x006570fc points to 0x00577fb7. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "vec4", "bezier"),
                false
            ),
            new Spec(
                "0x00577fb7",
                null,
                null,
                "Math__BezierBlendVec4",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("control0_vec4", voidPtr),
                    param("control1_vec4", voidPtr),
                    param("control2_vec4", voidPtr),
                    param("control3_vec4", voidPtr),
                    param("ratio", floatType)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 43 at 0x006570fc points here; the body performs three interpolation calls through the vec4 ratio thunk, blending control0_vec4 through control3_vec4 and returning the output pointer. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "vec4", "bezier"),
                false
            ),
            new Spec(
                "0x0057804e",
                null,
                null,
                "Math__BlendVec4DualWeights",
                "__stdcall",
                voidPtr,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("base_vec4", voidPtr),
                    param("target_a_vec4", voidPtr),
                    param("target_b_vec4", voidPtr),
                    param("weight_a", floatType),
                    param("weight_b", floatType)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 36 at 0x006570e0 points here; the body blends two weighted target vec4 values through ratio interpolation, uses weight_b / (weight_a + weight_b) for the final mix, or copies base_vec4 when the combined weight is near zero. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "vec4", "interpolation", "dual-weight"),
                false
            ),
            new Spec(
                "0x00578555",
                null,
                null,
                "Math__TransformVec2ByMatrix4x4",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec4", voidPtr),
                    param("input_vec2", voidPtr),
                    param("matrix4x4", voidPtr)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 0 at 0x00657050 points here and CFastVB__InitDispatchTableByCpuFeature references this as a default implementation; the body writes a four-float output from input_vec2 and matrix4x4 terms. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "vec2", "transform"),
                false
            ),
            new Spec(
                "0x00578643",
                null,
                null,
                "Math__TransformVec2ByMatrixPerspective",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec2", voidPtr),
                    param("input_vec2", voidPtr),
                    param("matrix4x4", voidPtr)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 9 at 0x00657074 points here; the body transforms input_vec2 by matrix4x4 and performs a guarded perspective divide before writing out_vec2. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "vec2", "perspective-transform"),
                false
            ),
            new Spec(
                "0x00578758",
                null,
                null,
                "Math__TransformVec2ByMatrixLinear",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec2", voidPtr),
                    param("input_vec2", voidPtr),
                    param("matrix4x4", voidPtr)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 5 at 0x00657064 points here; the body performs a linear transform of input_vec2 by matrix4x4 terms without the guarded perspective divide used by the perspective variant. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "vec2", "linear-transform"),
                false
            ),
            new Spec(
                "0x005787e8",
                null,
                null,
                "Math__NormalizeVec3",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec3", voidPtr),
                    param("input_vec3", voidPtr)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 7 at 0x0065706c points here; the body measures input_vec3 length, guards near-zero values through Math__IsFloatDiffOutsideTolerance, writes a normalized vec3 when safe, or writes zeroes. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "vec3", "normalize"),
                false
            ),
            new Spec(
                "0x00578885",
                null,
                null,
                "Math__TransformVec3ByMatrixPerspective",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_vec3", voidPtr),
                    param("input_vec3", voidPtr),
                    param("matrix4x4", voidPtr)
                },
                "Wave660 math dispatch continuation: source/default dispatch-table slot 10 at 0x00657078 points here; the body transforms input_vec3 by matrix4x4 and performs a guarded perspective divide before writing out_vec3. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "vec3", "perspective-transform"),
                false
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " body_set=" + stats.bodySet +
            " would_set_body=" + stats.wouldSetBody +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun && (stats.bad != 0 || stats.missing != 0)) {
            throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
