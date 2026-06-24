//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
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

public class ApplyInfluenceMapFollowupWave455 extends GhidraScript {
    private static class Spec {
        final String address;
        final String expectedCurrentName;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final String[] tags;
        final ParameterImpl[] parameters;

        Spec(
                String address,
                String expectedCurrentName,
                String name,
                String callingConvention,
                DataType returnType,
                String comment,
                String[] tags,
                ParameterImpl[] parameters) {
            this.address = address;
            this.expectedCurrentName = expectedCurrentName;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address entry = addr(addressText);
        Function fn = getFunctionAt(entry);
        if (fn == null) {
            Function containing = getFunctionContaining(entry);
            if (containing != null && containing.getEntryPoint().equals(entry)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
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
            "influencemap-followup-wave455",
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
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            String currentName = fn.getName();
            if (!currentName.equals(spec.expectedCurrentName) && !currentName.equals(spec.name)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
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

            println("OK: " + spec.address + " " + readBack.getSignature());
            stats.updated++;
            Thread.sleep(5000);
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
        DataType byteType = ByteDataType.dataType;
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004ad7f0",
                "CInfluenceMap__SetTrackedThingAndClearCachedObject",
                "CInfluenceMap__SetTrackedThingAndClearCachedObject",
                "__thiscall",
                voidType,
                "Wave455 signature/comment correction: BattleEngine caller sets the tracked thing-like pointer at this+0x14 and clears/frees the cached pointer at this+0x24 when present. Ret 0x4 confirms one tracked_thing stack argument rather than the prior extra phantom parameter. Static retail evidence only; runtime handoff behavior remains unproven.",
                tags("influencemap", "battleengine-handoff", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tracked_thing", voidPtr)
                }
            ),
            new Spec(
                "0x004bf9e0",
                "OID__InitInfluenceMapObject",
                "OID__InitInfluenceMapObject",
                "__fastcall",
                voidPtr,
                "Wave455 signature/comment correction: OID factory init helper for an InfluenceMap-related CInitThing subobject. The body calls CInitThing__ctor, writes PTR_LAB_005dc1c0 at the object head, clears the dword at +0x3bc, and returns the init_subobject pointer. Static retail evidence only; runtime object identity remains unproven.",
                tags("oid", "initthing", "influencemap", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("init_subobject", voidPtr)
                }
            ),
            new Spec(
                "0x004d30d0",
                "CInfluenceMap__AccumulateThingFlags",
                "CInfluenceMap__AccumulateThingFlags",
                "__thiscall",
                voidType,
                "Wave455 signature/comment correction: InfluenceMap flag accumulator over thing+0x34. The body increments counters at this+0x08/+0x0c/+0x10/+0x14/+0x18 when bits 0x400, 0x20000, 0x40000, 0x4000, or 0x800 are set; ret 0x4 confirms one thing stack argument. Static retail evidence only; runtime category semantics remain unproven.",
                tags("influencemap", "flag-accumulator", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("thing", voidPtr)
                }
            ),
            new Spec(
                "0x004d38c0",
                "CInfluenceMap__TryUnitCleanupAndReturnTrue",
                "CUnit__TryDestroyedCleanupAndResetDeploymentGraph",
                "__fastcall",
                intType,
                "Wave455 owner/signature correction: this is a CUnit cleanup wrapper, not an InfluenceMap body. It calls CUnit__MarkDestroyedAndCleanupLinks, returns 0 on failure, otherwise calls CUnit__ResetDeploymentGraphAndScheduleEvent and returns 1; the only observed xref is a vtable data xref at 0x005e0054. Static retail evidence only; runtime unit lifecycle behavior remains unproven.",
                tags("unit", "cleanup", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d39d0",
                "CInfluenceMap__ResetRuntimeState",
                "CPolyBucket__InitFields",
                "__fastcall",
                voidType,
                "Wave455 owner/name/signature correction: CPolyBucket-style field initializer called from CMeshPart__CreatePolyBucket and CStaticShadows__BuildShadowMaps. The body clears fields around +0x40/+0x60/+0x78/+0x98/+0x9c and seeds +0x50 to 1.0. Static retail evidence only; concrete CPolyBucket layout and runtime render behavior remain unproven.",
                tags("polybucket", "init", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004d3a00",
                "CInfluenceMap__FreeRuntimeBuffers",
                "CPolyBucket__FreeBuffers",
                "__fastcall",
                voidType,
                "Wave455 owner/name/signature correction: CPolyBucket-style buffer cleanup called by CMeshPart, CMesh, and CStaticShadows paths. The body frees the +0x60 grid, optional +0x80/+0x84 arrays, +0x64 storage, and +0x98 object callback/free path. Static retail evidence only; concrete CPolyBucket layout and runtime render behavior remain unproven.",
                tags("polybucket", "cleanup", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x0050b930",
                "CInfluenceMap__VFunc_01_0050b930",
                "CInfluenceMapManager__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                "Wave455 owner/name/signature correction: scalar-deleting destructor wrapper for the InfluenceMap manager vtable 0x005dfcb4 used by DAT_0067a748. It calls CInfluenceMapManager__dtor, checks flags bit 0, optionally frees this through the memory manager, and returns this. Static retail evidence only; runtime cleanup behavior remains unproven.",
                tags("influencemap-manager", "destructor", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                }
            ),
            new Spec(
                "0x0050b950",
                "CInfluenceMap__ctor_like_0050b950",
                "CInfluenceMapManager__dtor",
                "__fastcall",
                voidType,
                "Wave455 owner/name/signature correction: destructor body for the InfluenceMap manager object stored in DAT_0067a748 and using vtable 0x005dfcb4. The body restores the manager vtable, calls CInfluenceMap__FreeObjectIfPresent, clears CSPtrSet members at +0x18 and +0x08, then calls CMonitor__Shutdown. Static retail evidence only; runtime cleanup behavior remains unproven.",
                tags("influencemap-manager", "destructor", "owner-corrected", "name-corrected", "signature-corrected", "comment-hardened"),
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
            + " created=0 would_create=0"
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave455 apply had missing/bad entries");
        }
    }
}
