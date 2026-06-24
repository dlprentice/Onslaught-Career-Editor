//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
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

public class ApplyCMechAIGuideWave437 extends GhidraScript {
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
            "cmech-ai-guide-wave437",
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
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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

            println("OK: " + spec.address + " " + readBack.getSignature());
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
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00499e30",
                "CMCMech__UpdateBone",
                "__thiscall",
                voidType,
                "Wave437 signature/comment hardening: CMCMech__Reset and CMCMech__UpdateBoneHierarchyRecursive call this large pose/bone updater. The body lazily initializes CMCMech state from mesh_part+0x128, updates one mesh/bone pose, blends current and previous pose/matrix caches, and writes per-part transform state before updating performance counters. Static retail evidence only; exact parameter roles, local structure names, runtime animation behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmcmech", "bone-update", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position", floatPtr),
                    param("matrix", floatPtr),
                    param("mesh_part", voidPtr),
                    param("pose_arg_a", voidPtr),
                    param("pose_arg_b", voidPtr),
                    param("blend_a", floatType),
                    param("blend_b", floatType)
                }
            ),
            new Spec(
                "0x0049fc10",
                "SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10",
                "__fastcall",
                voidType,
                "Wave437 owner/name correction: vtable tables 0x005e0684 and 0x005e3074 both point slot 66 here, while GillM/ThunderHead-style slot-66 overrides call into this body. The function updates vertical drift fields when flag bit 4 is set, dispatches vtable slot 95, optionally creates a pickup from the +0x70/+0xd0 state, then calls CGroundUnit__UpdateLinkedEffectsByHeightClearance. Static retail evidence only; exact concrete owner coverage, runtime pickup behavior, and rebuild parity remain unproven.",
                new String[] { "CExplosionInitThing__ctor_like_0049fc10" },
                tags("shared-ground-unit", "vtable-slot-66", "owner-corrected", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0049fdb0",
                "SharedGroundUnit__VFunc_71_SpawnGenericMeshBreakEffects_0049fdb0",
                "__fastcall",
                voidType,
                "Wave437 owner/name correction: vtable slot 71 in tables 0x005e0684, 0x005e3074, 0x005e0fe0, and 0x005e0b30 points here, covering the Mech/GillM/ThunderHead-style ground tables sampled this wave. The body searches the Generic Mesh node, iterates child mesh parts with flag +0x8c == 1, creates break effects, anchors them through CMCMech__BuildInterpolatedPoseAndAnchor, and randomizes effect velocity. Static retail evidence only; exact concrete owner coverage, mesh-effect runtime behavior, and rebuild parity remain unproven.",
                new String[] { "CComponent__SpawnGenericMeshBreakEffects" },
                tags("shared-ground-unit", "vtable-slot-71", "mesh-effects", "owner-corrected", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a02e0",
                "CMechAI__ctor",
                "__thiscall",
                voidPtr,
                "Wave437 constructor hardening: CMech__InitCockpit allocates a 0x64 object, calls this body, and stores the returned pointer at CMech+0x13c. The body calls the current CWarspite__Init-labeled helper with owner/init_context evidence, installs vtable 0x005dc4c0, clears +0x14, and randomizes the +0x60 state flag. Static retail evidence only; exact base/helper identity, reserved third argument meaning, runtime cockpit AI behavior, and rebuild parity remain unproven.",
                new String[] { "CMechAI__ctor_like_004a02e0" },
                tags("cmech-ai", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_unit", voidPtr),
                    param("init_context", voidPtr),
                    param("reserved_arg", intType)
                }
            ),
            new Spec(
                "0x004a0390",
                "CMechAI__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave437 destructor correction: CMechAI vtable 0x005dc4c0 slot 1 points here. The body calls CUnitAI__dtor_base and frees this when the scalar-deleting flags byte has bit 0 set, then returns this. Static retail evidence only; exact ownership/lifetime behavior and rebuild parity remain unproven.",
                new String[] { "CMechAI__VFunc_01_004a0390" },
                tags("cmech-ai", "destructor", "scalar-deleting-dtor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004a03b0",
                "CUnitAI__dtor_base",
                "__fastcall",
                voidType,
                "Wave437 destructor correction: called by CMechAI__scalar_deleting_dtor. The body restores vtable 0x005d8d1c, removes linked reader cells at +0x28, +0x24, and +0x0c when present, then calls CMonitor__Shutdown. Static retail evidence only; exact base-class identity, linked-set semantics, and rebuild parity remain unproven.",
                new String[] { "CUnitAI__ctor_like_004a03b0" },
                tags("unit-ai", "destructor", "dtor-base", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a0a20",
                "CMechGuide__ctor",
                "__thiscall",
                voidPtr,
                "Wave437 constructor hardening: CMech__InitTargeting allocates a 0x48 object, calls this body, and stores the returned pointer at CMech+0x208. The body calls CGuide__ctor_base, allocates two one-byte array buffers, initializes path/grid fields, installs vtable 0x005dc4f4, stores CUnit__GetGridMapByType(owner), clears the active reader, and schedules event 2000. Static retail evidence only; exact reserved argument meaning, targeting-guide runtime behavior, and rebuild parity remain unproven.",
                new String[] { "CMechGuide__ctor_like_004a0a20" },
                tags("cmech-guide", "constructor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_unit", voidPtr),
                    param("reserved_arg", voidPtr)
                }
            ),
            new Spec(
                "0x004a0b10",
                "CMechGuide__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave437 destructor correction: CMechGuide vtable 0x005dc4f4 slot 1 points here. The body calls CMechGuide__dtor_base and frees this when the scalar-deleting flags byte has bit 0 set, then returns this. Static retail evidence only; exact ownership/lifetime behavior and rebuild parity remain unproven.",
                new String[] { "CMechGuide__VFunc_01_004a0b10" },
                tags("cmech-guide", "destructor", "scalar-deleting-dtor", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x004a0b30",
                "CMechGuide__dtor_base",
                "__fastcall",
                voidType,
                "Wave437 destructor correction: called by CMechGuide__scalar_deleting_dtor. The body removes the active reader at +0x44 when linked, frees the two owned buffers at +0x3c and +0x34, then calls CMonitor__Shutdown. Static retail evidence only; exact guide cleanup semantics and rebuild parity remain unproven.",
                new String[] { "CMechGuide__ShutdownAndReleaseResources" },
                tags("cmech-guide", "destructor", "dtor-base", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a0bc0",
                "CMechGuide__VFunc_03_UpdateGuidanceState_004a0bc0",
                "__fastcall",
                voidType,
                "Wave437 name/comment hardening: CMechGuide vtable 0x005dc4f4 slot 3 points here. The body updates guidance state from the owner at +0x18, active reader at +0x44, CMechAI state at owner+0x13c, and path buffers at +0x34/+0x3c, then writes steering/target vectors back to owner fields before updating performance counters. Static retail evidence only; exact event contract, path semantics, runtime targeting behavior, and rebuild parity remain unproven.",
                new String[] { "CMechGuide__VFunc_03_004a0bc0" },
                tags("cmech-guide", "vtable-slot-03", "guidance", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a1270",
                "CMechGuide__SelectNearestHostileTargetReader",
                "__fastcall",
                voidType,
                "Wave437 owner/name correction: this helper clears CMechGuide active reader field +0x44, scans CMapWho entries around owner unit +0x18, filters out self and incompatible flags, then stores the nearest hostile reader within the distance threshold. It is reached from the CMechGuide guidance cluster near 0x004a1210. Static retail evidence only; exact hostility rules, range constant meaning, and rebuild parity remain unproven.",
                new String[] { "CMonitor__SelectNearestHostileTargetReader" },
                tags("cmech-guide", "target-selection", "active-reader", "renamed", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=0"
            + " would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave437 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
