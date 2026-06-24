//@category Symbol

import ghidra.app.cmd.disassemble.DisassembleCommand;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyMatrixDispatchWave659 extends GhidraScript {
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
            "matrix-dispatch-wave659",
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

        String staticEvidence = "Static retail decompile/instruction/dispatch-table evidence only; exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.";

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005771af",
                null,
                null,
                "Math__BuildScaleMatrix4x4_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("scale_x", floatType),
                    param("scale_y", floatType),
                    param("scale_z", floatType)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 33 at 0x00656fb4 calls CFastVB__InitDispatchTableByCpuFeature(1), repacks out_matrix4x4 plus three scalar operands, then calls the active slot implementation. The paired default/source slot 33 at 0x006570d4 points to the recovered 0x005771dd scale-matrix builder. " + staticEvidence,
                new String[] { "CFastVB__DispatchIndirect_00656fb4" },
                tags("dispatch-table", "matrix4x4", "scale-matrix"),
                false
            ),
            new Spec(
                "0x005771dd",
                "0x00577236",
                "0x00577239",
                "Math__BuildScaleMatrix4x4",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("scale_x", floatType),
                    param("scale_y", floatType),
                    param("scale_z", floatType)
                },
                "Wave659 matrix dispatch boundary recovery: source/default dispatch-table slot 33 at 0x006570d4 points here; the body writes a 4x4 scale matrix with scale_x/scale_y/scale_z on the diagonal, zeros elsewhere, bottom-right 1.0, and RET 0x10 at 0x00577236. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "boundary-recovered", "matrix4x4", "scale-matrix"),
                true
            ),
            new Spec(
                "0x00577239",
                null,
                null,
                "Math__BuildTranslationMatrix4x4_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("translate_x", floatType),
                    param("translate_y", floatType),
                    param("translate_z", floatType)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 26 at 0x00656f98 calls CFastVB__InitDispatchTableByCpuFeature(1), repacks out_matrix4x4 plus three translation operands, then calls the active slot implementation. The paired default/source slot 26 at 0x006570b8 points to the recovered 0x0057726d translation-matrix builder. " + staticEvidence,
                new String[] { "CDXTexture__DispatchPtr00656f98_WithInit" },
                tags("dispatch-table", "matrix4x4", "translation-matrix"),
                false
            ),
            new Spec(
                "0x00577267",
                null,
                null,
                "Math__BuildTranslationMatrix4x4_Dispatch_Thunk",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("translate_x", floatType),
                    param("translate_y", floatType),
                    param("translate_z", floatType)
                },
                "Wave659 matrix dispatch hardening: pure jump thunk to runtime dispatch-table slot 26 at 0x00656f98, sharing the translation-matrix call contract with the initialized dispatcher at 0x00577239. " + staticEvidence,
                new String[] { "CDXTexture__DispatchPtr00656f98_WithInit_Thunk" },
                tags("dispatch-table", "matrix4x4", "translation-matrix", "jump-thunk"),
                false
            ),
            new Spec(
                "0x0057726d",
                "0x005772c6",
                "0x005772c9",
                "Math__BuildTranslationMatrix4x4",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("translate_x", floatType),
                    param("translate_y", floatType),
                    param("translate_z", floatType)
                },
                "Wave659 matrix dispatch boundary recovery: source/default dispatch-table slot 26 at 0x006570b8 points here; the body writes an identity 4x4 matrix, stores translate_x/translate_y/translate_z at offsets 0x30/0x34/0x38, and returns with RET 0x10 at 0x005772c6. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "boundary-recovered", "matrix4x4", "translation-matrix"),
                true
            ),
            new Spec(
                "0x005772c9",
                null,
                null,
                "Math__BuildRotationMatrixX_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 30 at 0x00656fa8 initializes the CPU-selected table, repacks out_matrix4x4 and angle_radians, and calls the active X-axis rotation-matrix implementation. The paired default/source slot 30 at 0x006570c8 points to 0x005772e5. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "x-axis"),
                false
            ),
            new Spec(
                "0x005772e5",
                null,
                null,
                "Math__BuildRotationMatrixX",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: source/default dispatch-table slot 30 at 0x006570c8 points here; the body uses FSINCOS and writes a 4x4 X-axis rotation matrix with bottom-right 1.0 and zeroed translation row/column. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "rotation-matrix", "x-axis"),
                false
            ),
            new Spec(
                "0x0057735f",
                null,
                null,
                "Math__BuildRotationMatrixY_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 31 at 0x00656fac initializes the CPU-selected table, repacks out_matrix4x4 and angle_radians, and calls the active Y-axis rotation-matrix implementation. The paired default/source slot 31 at 0x006570cc points to 0x0057737b. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "y-axis"),
                false
            ),
            new Spec(
                "0x0057737b",
                null,
                null,
                "Math__BuildRotationMatrixY",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: source/default dispatch-table slot 31 at 0x006570cc points here; the body uses FSINCOS and writes a 4x4 Y-axis rotation matrix with bottom-right 1.0 and zeroed translation row/column. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "rotation-matrix", "y-axis"),
                false
            ),
            new Spec(
                "0x005773f6",
                null,
                null,
                "Math__BuildRotationMatrixZ_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 32 at 0x00656fb0 initializes the CPU-selected table, repacks out_matrix4x4 and angle_radians, and calls the active Z-axis rotation-matrix implementation. The paired default/source slot 32 at 0x006570d0 points to 0x00577412. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "z-axis"),
                false
            ),
            new Spec(
                "0x00577412",
                null,
                null,
                "Math__BuildRotationMatrixZ",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: source/default dispatch-table slot 32 at 0x006570d0 points here; the body uses FSINCOS and writes a 4x4 Z-axis rotation matrix with bottom-right 1.0 and zeroed translation row/column. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "rotation-matrix", "z-axis"),
                false
            ),
            new Spec(
                "0x0057748e",
                null,
                null,
                "Math__BuildAxisAngleRotationMatrix_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("axis_vec3", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 42 at 0x00656fd8 initializes the CPU-selected table, repacks out_matrix4x4, axis_vec3, and angle_radians, then calls the active axis-angle rotation-matrix implementation. The paired default/source slot 42 at 0x006570f8 points to 0x005774ae. " + staticEvidence,
                new String[] {},
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "axis-angle"),
                false
            ),
            new Spec(
                "0x005774ae",
                null,
                null,
                "Math__BuildAxisAngleRotationMatrix",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("axis_vec3", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave659 matrix dispatch hardening: source/default dispatch-table slot 42 at 0x006570f8 points here; the body normalizes/uses axis_vec3, applies FSINCOS-derived angle terms, and writes a 4x4 axis-angle rotation matrix with bottom-right 1.0. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "matrix4x4", "rotation-matrix", "axis-angle"),
                false
            ),
            new Spec(
                "0x005775b0",
                null,
                null,
                "Math__BuildQuaternionRotationMatrix_Dispatch",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("quaternion_xyzw", voidPtr)
                },
                "Wave659 matrix dispatch hardening: runtime dispatch-table slot 38 at 0x00656fc8 calls CFastVB__InitDispatchTableByCpuFeature(1), then jumps through the active quaternion-to-matrix implementation. The paired default/source slot 38 at 0x006570e8 points to the recovered 0x005775c3 builder. " + staticEvidence,
                new String[] { "CFastVB__DispatchIndirect_00656fc8" },
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "quaternion"),
                false
            ),
            new Spec(
                "0x005775bd",
                null,
                null,
                "Math__BuildQuaternionRotationMatrix_Dispatch_Thunk",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("quaternion_xyzw", voidPtr)
                },
                "Wave659 matrix dispatch hardening: pure jump thunk to runtime dispatch-table slot 38 at 0x00656fc8, sharing the quaternion-to-matrix call contract with the initialized dispatcher at 0x005775b0. " + staticEvidence,
                new String[] { "CFastVB__DispatchIndirect_00656fc8" },
                tags("dispatch-table", "matrix4x4", "rotation-matrix", "quaternion", "jump-thunk"),
                false
            ),
            new Spec(
                "0x005775c3",
                "0x005776a2",
                "0x005776a5",
                "Math__BuildQuaternionRotationMatrix",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("out_matrix4x4", voidPtr),
                    param("quaternion_xyzw", voidPtr)
                },
                "Wave659 matrix dispatch boundary recovery: source/default dispatch-table slot 38 at 0x006570e8 points here; the body reads four quaternion floats from quaternion_xyzw, uses constant 0x005e9324, writes a 4x4 rotation matrix with zeroed translation row/column and bottom-right 1.0, and returns with RET 0x8 at 0x005776a2. " + staticEvidence,
                new String[] {},
                tags("source-dispatch-table", "boundary-recovered", "matrix4x4", "rotation-matrix", "quaternion"),
                true
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
