//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCWeaponDistanceProfileWave539 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final String[] allowedExistingNames;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags,
                String[] allowedExistingNames) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.allowedExistingNames = allowedExistingNames;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cweapon-distance-profile-wave539",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
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
        return !hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(spec.address);
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
        if (!hasAllTags(fn, spec.tags)) {
            throw new IllegalStateException("Readback missing tags at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!allowedName(spec, fn.getName())) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
        }

        boolean needsRename = !fn.getName().equals(spec.name);
        boolean update = needsUpdate(fn, spec);
        if (dryRun) {
            if (needsRename) {
                println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                stats.wouldRename++;
            } else {
                println((update ? "DRY: " : "SKIP: ") + spec.address + " " + expectedSignature(spec));
            }
            stats.skipped++;
            return;
        }
        if (!update) {
            println("SKIP: " + spec.address + " already current");
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
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType boolType = BooleanDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005061f0",
                "CWeapon__DoesTargetMaskMatchDistanceProfile",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("target_unit", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: BattleEngine firing callers pass the current weapon from CBattleEngineJetPart/WalkerPart GetCurrentWeapon as ECX, and RET 0x4 proves one explicit target_unit stack argument. The body rejects inactive/non-lockable target state, buckets weapon distance from this+0x60 through the table at this+0xa4, walks DAT_008553ec with fallback to lower distance buckets, then tests the selected profile entry mask at +0xa4 against target_unit+0x34. Static retail evidence only; concrete CWeapon/profile/target layouts, exact source identity, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "target-mask", "renamed"),
                new String[] {"CBattleEngine__DoesTargetMaskMatchProfileByDistance"}
            ),
            new Spec(
                "0x00506350",
                "CWeapon__GetDistanceProfileField90",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: register-only helper called from CBattleEngine firing loops with the current weapon pointer. The body buckets this+0x60 by hundreds, indexes the this+0xa4 distance table, walks DAT_008553ec with lower-bucket fallback, and returns selected profile entry +0x90 or 0 when no entry is found. Static retail evidence only; exact field semantics, concrete CWeapon/profile layout, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "field-90", "renamed"),
                new String[] {"CBattleEngine__GetProfileField90ByDistance"}
            ),
            new Spec(
                "0x00506440",
                "CWeapon__GetDistanceProfileField94",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: register-only helper called before CBattleEngine__AddProjectile with the current weapon pointer. The body buckets this+0x60 by hundreds, indexes the this+0xa4 distance table, walks DAT_008553ec with lower-bucket fallback, and returns selected profile float +0x94 as a double or 0.0 when no entry is found. Static retail evidence only; exact field semantics, concrete CWeapon/profile layout, runtime projectile behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "field-94", "renamed"),
                new String[] {"CBattleEngine__GetProfileField94ByDistance"}
            ),
            new Spec(
                "0x00506530",
                "CWeapon__GetDistanceProfileFieldA8",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: register-only helper used as a firing-mode selector by CBattleEngine__UpdateAutoTargetSetAndFireProjectiles with the current weapon pointer. The body buckets this+0x60 by hundreds, indexes the this+0xa4 distance table, walks DAT_008553ec with lower-bucket fallback, and returns selected profile entry +0xa8 or 0 when no entry is found. Static retail evidence only; exact field semantics, concrete CWeapon/profile layout, runtime firing-mode behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "field-a8", "renamed"),
                new String[] {"CBattleEngine__GetProfileFieldA8ByDistance"}
            ),
            new Spec(
                "0x00506620",
                "CWeapon__GetDistanceProfileField98",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: register-only helper called before cosine facing checks with the current weapon pointer. The body buckets this+0x60 by hundreds, indexes the this+0xa4 distance table, walks DAT_008553ec with lower-bucket fallback, and returns selected profile float +0x98 as a double or 0.0 when no entry is found. Static retail evidence only; exact angle/field semantics, concrete CWeapon/profile layout, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "field-98", "renamed"),
                new String[] {"CBattleEngine__GetProfileField98ByDistance"}
            ),
            new Spec(
                "0x00506710",
                "CWeapon__GetDistanceProfileField9C",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: register-only helper used as a target-search range scale by CBattleEngine firing helpers with the current weapon pointer. The body buckets this+0x60 by hundreds, indexes the this+0xa4 distance table, walks DAT_008553ec with lower-bucket fallback, and returns selected profile float +0x9c as a double or 0.0 when no entry is found. Static retail evidence only; exact range/field semantics, concrete CWeapon/profile layout, runtime target-selection behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "field-9c", "renamed"),
                new String[] {"CBattleEngine__GetProfileField9CByDistance"}
            ),
            new Spec(
                "0x00506800",
                "CWeapon__GetDistanceProfileFieldA0",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave539 CWeapon distance-profile owner/signature correction: register-only helper used as an alternate target-search range scale by CBattleEngine firing helpers with the current weapon pointer. The body buckets this+0x60 by hundreds, indexes the this+0xa4 distance table, walks DAT_008553ec with lower-bucket fallback, and returns selected profile float +0xa0 as a double or 0.0 when no entry is found. Static retail evidence only; exact range/field semantics, concrete CWeapon/profile layout, runtime target-selection behavior, and rebuild parity remain unproven.",
                tags("cweapon", "distance-profile", "field-a0", "renamed"),
                new String[] {"CBattleEngine__GetProfileFieldA0ByDistance"}
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped +
            " renamed=" + stats.renamed + " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing + " bad=" + stats.bad);
        if (!dryRun && stats.missing == 0 && stats.bad == 0) {
            println("REPORT: Save succeeded");
        }
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave539 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
