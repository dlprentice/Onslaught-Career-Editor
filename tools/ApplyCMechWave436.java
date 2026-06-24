//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMechWave436 extends GhidraScript {
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
            "cmech-wave436",
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0049f600",
                "CMeshPart__NameAvoidsBarrelSpinnerOptimizationTokens",
                "__cdecl",
                boolType,
                "Wave436 owner/name correction: one cdecl mesh_part argument is read from ESP+4, then the mesh-part name at +0xdc is compared against token 0x0062e0cc, the barrel prefix, the spinner token, and the three-byte prefix at 0x0062e0c0. The predicate returns false for matching protected barrel/spinner optimization names and true otherwise, matching CMeshPart optimization callers. Static retail evidence only; exact optimization-policy meaning, runtime mesh behavior, and rebuild parity remain unproven.",
                new String[] { "CMeshPart__NameMatchesBarrelSpinnerTokenSet" },
                tags("mesh-filter", "barrel-spinner-token", "renamed", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x0049f670",
                "CMeshPart__AnyChildNameMatchesBarrelSpinnerOptimizationTokens",
                "__cdecl",
                boolType,
                "Wave436 owner/name correction: one cdecl mesh_part argument is read from ESP+4, child count +0x15c and child pointer table +0x160 are walked, and child names at +0xdc are tested against the same token 0x0062e0cc, barrel prefix, spinner token, and three-byte prefix set. The predicate returns true on the first matching protected child name. Static retail evidence only; exact optimization-policy meaning, runtime child-name behavior, and rebuild parity remain unproven.",
                new String[] { "CMeshPart__AnySubPartMatchesBarrelSpinnerTokenSet" },
                tags("mesh-filter", "barrel-spinner-token", "renamed", "signature-corrected", "comment-hardened", "token-readback"),
                new ParameterImpl[] {
                    param("mesh_part", voidPtr)
                }
            ),
            new Spec(
                "0x0049f820",
                "SharedGroundUnit__VFunc_09_InitGroundedMotionComponents_0049f820",
                "__thiscall",
                voidType,
                "Wave436 shared slot-9 correction: RET 0x4 confirms one init_context stack argument after this. The body calls CGroundUnit__Init, copies initialization values from init_context+0x3bc into this+0x12c/+0x100 ranges, invokes vtable slots 117/118/119, and resolves a named child through CDestroyableSegment__FindChildByNameI. Vtable tables 0x005e0684 and 0x005e3074 both point slot 9 here, so concrete owner naming is intentionally conservative. Static retail evidence only; exact concrete layout, runtime grounded-unit behavior, and rebuild parity remain unproven.",
                new String[] { "VFuncSlot_09_0049f820" },
                tags("shared-ground-unit", "vtable-slot", "renamed", "signature-corrected", "comment-hardened", "vtable-readback"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_context", voidPtr)
                }
            ),
            new Spec(
                "0x0049f940",
                "CMech__InitLegMotion",
                "__thiscall",
                voidType,
                "Wave436 CMech slot hardening: RET 0x4 confirms one init_context stack argument after this. The body finds the LegMotion animation, allocates a 0xf0 CMCMech motion controller from Mech.cpp line 0x3d, stores it at this+0x70, and calls CMCMech__SetParams with init_context+0x3bc values plus 0.4/0.9 constants. Static retail evidence only; exact source-body identity, runtime leg-motion behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmech", "leg-motion", "signature-corrected", "comment-hardened", "source-path-evidence"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_context", voidPtr)
                }
            ),
            new Spec(
                "0x0049fa30",
                "CMech__InitCockpit",
                "__thiscall",
                voidType,
                "Wave436 CMech slot hardening: RET 0x4 confirms one init_context stack argument after this. CMech vtable 0x005e3074 slot 118 points here; the body allocates a 0x64 object from Mech.cpp line 0x48, calls CMechAI__ctor_like_004a02e0 with this and init_context, and stores the result at this+0x13c. Static retail evidence only; exact cockpit/AI semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmech", "cockpit", "ai", "vtable-slot", "signature-corrected", "comment-hardened", "source-path-evidence"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_context", voidPtr)
                }
            ),
            new Spec(
                "0x0049faa0",
                "CMech__InitTargeting",
                "__fastcall",
                voidType,
                "Wave436 CMech slot hardening: register-only body has no stack cleanup. Vtable tables 0x005e0684 and 0x005e3074 both point slot 119 here; the body allocates a 0x48 object from Mech.cpp line 0x4e, calls CMechGuide__ctor_like_004a0a20 with this, and stores the result at this+0x208. Static retail evidence only; exact targeting/guide semantics, runtime behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmech", "targeting", "guide", "vtable-slot", "signature-corrected", "comment-hardened", "source-path-evidence"),
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
            throw new IllegalStateException("Wave436 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
