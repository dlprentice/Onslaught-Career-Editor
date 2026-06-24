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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCUnitCtorMatrixWave548 extends GhidraScript {
    private static final String[] COMMON_TAGS = new String[] {
        "static-reaudit",
        "cunit-ctor-matrix-wave548",
        "retail-binary-evidence",
        "name-corrected",
        "signature-corrected",
        "comment-hardened"
    };

    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(
                String address,
                String name,
                String previousName,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] params,
                String comment,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.previousName = previousName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.params = params;
            this.comment = comment;
            this.tags = tags;
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

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private Address toAddress(String addressText) {
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function targetFunction(Spec spec) {
        Address address = toAddress(spec.address);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private boolean isAllowedName(Function fn, Spec spec) {
        return fn.getName().equals(spec.name) ||
            (spec.previousName != null && fn.getName().equals(spec.previousName));
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
        if (fn.getParameterCount() != spec.params.length) {
            return false;
        }
        for (int i = 0; i < spec.params.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.params[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private Set<String> expectedTags(Spec spec) {
        Set<String> result = new HashSet<>();
        for (String tag : COMMON_TAGS) {
            result.add(tag);
        }
        for (String tag : spec.tags) {
            result.add(tag);
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : expectedTags(spec)) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
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
        return !hasAllTags(fn, spec);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.params[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = targetFunction(spec);
        if (fn == null) {
            throw new IllegalStateException("Readback missing function at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Readback name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Readback signature mismatch at " + spec.address +
                ": expected " + expectedSignature(spec) + " got " + fn.getSignature());
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            throw new IllegalStateException("Readback comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
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
                "0x004f7e90",
                "CUnit__ctor_base",
                "CActor__ctor_like_004f7e90",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave548 CUnit constructor owner/signature/comment hardening: ECX carries the allocated unit object, the body calls CComplexThing__ctor_base, installs transient CActor vtables before installing CUnit primary/secondary vtables 0x005df998/0x005df920, initializes active-reader/list/health/orientation/state fields, calls Mat34__SetFromEulerDegrees twice for zeroed old/current orientation setup, and returns this. Xrefs are object/unit factory paths including OID__CreateObject, CGroundUnit__Constructor, CBigAirUnit/CAirUnit constructors, CWorldPhysicsManager__CreateThingByType, and CWorldPhysicsManager__CreateCharacter. Static retail evidence only; exact CUnit source body, concrete layout/field names, runtime construction behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"cunit", "constructor", "owner-corrected"}
            ),
            new Spec(
                "0x004f8140",
                "Mat34__SetFromEulerDegrees",
                "CActor__BuildOrientationFromEuler",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("yaw_deg", intType),
                    param("pitch_deg", intType),
                    param("roll_deg", intType)
                },
                "Wave548 owner/signature/comment correction: owner-neutral Mat34/FMatrix-style helper takes the destination matrix in ECX and integer yaw_deg, pitch_deg, roll_deg on the stack, converts degree inputs through constant 0x005dfb6c, builds basis rows through Vec3__SetXYZ/Mat34__SetRows/Mat34__MultiplyBasisToOut, copies 12 dwords into the destination, and returns with RET 0x0c. Broad xrefs from CUnit construction, CEquipment construction, CMonitor tracking, and ProjectileBurst spawning make the previous CActor-specific label too narrow. Static retail evidence only; exact source identity, angle order/convention, concrete matrix layout, runtime orientation behavior, and rebuild parity remain unproven.",
                new String[] {"mat34", "euler", "owner-corrected"}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            Function fn = targetFunction(spec);
            if (fn == null) {
                println("MISSING: " + spec.address);
                stats.missing++;
                continue;
            }
            if (!isAllowedName(fn, spec)) {
                println("BADNAME: " + spec.address + " " + fn.getName());
                stats.bad++;
                continue;
            }

            boolean rename = !fn.getName().equals(spec.name);
            boolean update = needsUpdate(fn, spec);
            if (dryRun) {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
                stats.skipped++;
                if (rename) {
                    stats.wouldRename++;
                }
                continue;
            }

            if (!update) {
                println("SKIP: " + spec.address + " already current");
                stats.skipped++;
                continue;
            }

            if (rename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params
            );
            fn.setComment(spec.comment);
            for (String tag : expectedTags(spec)) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + expectedSignature(spec));
            stats.updated++;
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
