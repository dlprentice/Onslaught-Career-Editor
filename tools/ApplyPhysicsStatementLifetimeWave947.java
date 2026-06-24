//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyPhysicsStatementLifetimeWave947 extends GhidraScript {
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
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
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

    private Set<String> tagNames(Function fn) {
        Set<String> result = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            result.add(tag.getName());
        }
        return result;
    }

    private boolean hasAllTags(Function fn, Spec spec) {
        Set<String> actual = tagNames(fn);
        for (String tag : spec.tags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private Function getOrCreate(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Address address = addr(spec.address);
        Function existing = functionAtEntry(address);
        if (existing != null) {
            return existing;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null) {
            throw new IllegalStateException("Address is inside existing function "
                + containing.getName() + " at " + containing.getEntryPoint());
        }
        if (dryRun) {
            stats.wouldCreate++;
            println("DRY_CREATE: " + spec.address + " -> " + expectedSignature(spec));
            return null;
        }

        boolean disasmOk = disassemble(address);
        Function created = createFunction(address, spec.name);
        if (created == null) {
            throw new IllegalStateException("createFunction returned null at " + spec.address + " (disassemble=" + disasmOk + ")");
        }
        stats.created++;
        return created;
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = getOrCreate(spec, dryRun, stats);
        if (fn == null) {
            return;
        }

        boolean renameNeeded = !fn.getName().equals(spec.name);
        boolean signatureNeedsUpdate = !signatureMatches(fn, spec);
        boolean commentOrTagsNeedUpdate = fn.getComment() == null
            || !fn.getComment().equals(spec.comment)
            || !hasAllTags(fn, spec);

        if (!renameNeeded && !signatureNeedsUpdate && !commentOrTagsNeedUpdate) {
            println("SKIP: " + spec.address + " " + spec.name);
            stats.skipped++;
            return;
        }
        if (dryRun) {
            println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            if (signatureNeedsUpdate) {
                stats.signatureUpdated++;
            } else if (commentOrTagsNeedUpdate) {
                stats.commentOnlyUpdated++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.name, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        if (signatureNeedsUpdate) {
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            stats.signatureUpdated++;
        }
        fn.setComment(spec.comment);
        Set<String> existingTags = tagNames(fn);
        for (String tag : spec.tags) {
            if (!existingTags.contains(tag)) {
                fn.addTag(tag);
            }
        }
        if (!signatureNeedsUpdate && commentOrTagsNeedUpdate) {
            stats.commentOnlyUpdated++;
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.name + " -> " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50L);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!fn.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + fn.getName());
        }
        if (!signatureMatches(fn, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + fn.getSignature());
        }
        if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(fn, spec)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "physics-statement-lifetime-wave947",
            "wave947-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "signature-hardened",
            "comment-hardened",
            "physics-script"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("ApplyPhysicsStatementLifetimeWave947 mode=" + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00432a20",
                "CUnitAlligence__LoadFromMemBuffer",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitAlligence vtable 0x005d9d28 slot 3 points at this load helper. The body reads a 4-byte child value type from CDXMemBuffer__Read, calls CPhysicsScriptStatements__CreateStatementType13, and stores the returned child value at this+0x8. The Alligence spelling is retained from current binary/source-adjacent evidence. Static retail Ghidra evidence only; exact source method name, serialized schema, concrete class layout, runtime physics behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "alligence", "vtable-slot-3", "load-helper"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("memBuffer", voidPtr)
                }
            ),
            new Spec(
                "0x00432ac0",
                "CPhysicsUnitValue__base_vtable_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CPhysicsUnitValue base vtable 0x005d9e54 slot 0 points at this compact scalar-deleting destructor wrapper. The body restores vtable 0x005d9e54, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. This is distinct from the shared leaf-value scalar-deleting wrapper at 0x00434100. Static retail Ghidra evidence only; exact source method name, subtype coverage, concrete class layout, runtime lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "base-vtable", "vtable-slot-0", "scalar-deleting-dtor"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", intType)
                }
            ),
            new Spec(
                "0x004347b0",
                "CPhysicsWeaponValue__base_vtable_scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CPhysicsWeaponValue base vtable 0x005d9f80 slot 0 points at this compact scalar-deleting destructor wrapper. The body restores vtable 0x005d9f80, tests the scalar-delete flag, optionally calls OID__FreeObject, and returns this. This is distinct from the shared weapon-value scalar-deleting wrapper at 0x00434a80. Static retail Ghidra evidence only; exact source method name, subtype coverage, concrete class layout, runtime lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("weapon-value", "base-vtable", "vtable-slot-0", "scalar-deleting-dtor"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", intType)
                }
            ),
            new Spec(
                "0x00432bd0",
                "CUnitImportance__ApplyToUnitData",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitImportance vtable 0x005d9cec slot 1 points at this compact apply helper. The body copies the value at this+0x8 into the unit/init-like record field at +0xf8 and returns with one stack argument. Static retail Ghidra evidence only; exact source method name, target structure layout, runtime importance behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "unit-data-apply", "vtable-slot-1", "importance"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unitData", voidPtr)
                }
            ),
            new Spec(
                "0x00432c60",
                "CUnitStandingLegPlacementArea__ApplyToUnitData",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitStandingLegPlacementArea vtable 0x005d9c24 slot 1 points at this compact apply helper. The body copies the value at this+0x8 into the unit/init-like record field at +0x150 and returns with one stack argument. Static retail Ghidra evidence only; exact source method name, target structure layout, runtime leg-placement behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "unit-data-apply", "vtable-slot-1", "leg-placement"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unitData", voidPtr)
                }
            ),
            new Spec(
                "0x00432f10",
                "CUnitStrafeChange__ApplyToUnitData",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitStrafeChange vtable 0x005d9bac slot 1 points at this compact apply helper. The body copies the value at this+0x8 into the unit/init-like record field at +0x180 and returns with one stack argument. Static retail Ghidra evidence only; exact source method name, target structure layout, runtime strafe-change behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "unit-data-apply", "vtable-slot-1", "strafe-change"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unitData", voidPtr)
                }
            ),
            new Spec(
                "0x00432f50",
                "CUnitNavMap__ApplyToUnitData",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitNavMap vtable 0x005d9b98 slot 1 points at this apply helper. The body reads the child value at this+0x8, calls that child's vtable slot +0x4 when present, and writes the returned value into the unit/init-like record field at +0xfc. Static retail Ghidra evidence only; exact source method name, target structure layout, runtime nav-map behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "unit-data-apply", "vtable-slot-1", "nav-map"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unitData", voidPtr)
                }
            ),
            new Spec(
                "0x00433010",
                "CUnitBehaviour__ApplyToUnitData",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitBehaviour vtable 0x005d9d50 slot 1 points at this apply helper. The body reads the child value at this+0x8, calls that child's vtable slot +0x4 when present, stores the returned behavior id into the unit/init-like record field at +0xe0, and maps selected ids into the related +0xfc field. Static retail Ghidra evidence only; exact source method name, target structure layout, runtime behavior semantics, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "unit-data-apply", "vtable-slot-1", "behaviour"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unitData", voidPtr)
                }
            ),
            new Spec(
                "0x00433150",
                "CUnitUse__ApplyToUnitData",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CUnitUse vtable 0x005d9d64 slot 1 points at this apply helper. The body passes this+0x8, unit/init-like record +0x108, and the value at this+0x208 into helper 0x005119e0, then returns with one stack argument. Static retail Ghidra evidence only; exact source method name, target structure layout, helper semantics, runtime use/spawner behavior, BEA patching, and rebuild parity remain unproven.",
                tags("unit-value", "unit-data-apply", "vtable-slot-1", "unit-use"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("unitData", voidPtr)
                }
            ),
            new Spec(
                "0x00434930",
                "CWeaponConsumption__ApplyToWeaponByName",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CWeaponConsumption vtable 0x005d9f30 slot 1 points at this weapon-list apply helper. The body searches the global weapon list at DAT_008553e8 by weapon name and applies the value payload to the matching weapon record. Static retail Ghidra evidence only; exact source method name, weapon record layout, runtime weapon consumption behavior, BEA patching, and rebuild parity remain unproven.",
                tags("weapon-value", "weapon-apply", "vtable-slot-1", "weapon-consumption"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("weaponName", charPtr)
                }
            ),
            new Spec(
                "0x00434de0",
                "CWeaponVersusAir__ApplyToWeaponByName",
                "__thiscall",
                voidType,
                "Wave947 PhysicsScript lifetime/apply boundary recovery: CWeaponVersusAir vtable 0x005d9e68 slot 1 points at this weapon-list apply helper. The body searches the global weapon list at DAT_008553e8 by weapon name and applies the value payload to the matching weapon record. Static retail Ghidra evidence only; exact source method name, weapon record layout, runtime versus-air behavior, BEA patching, and rebuild parity remain unproven.",
                tags("weapon-value", "weapon-apply", "vtable-slot-1", "versus-air"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("weaponName", charPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            try {
                applySpec(spec, dryRun, stats);
            } catch (Exception ex) {
                println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
                stats.bad++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " bad=" + stats.bad
        );
        if (stats.bad != 0) {
            throw new IllegalStateException("Wave947 PhysicsScript lifetime apply encountered bad rows");
        }
    }
}
