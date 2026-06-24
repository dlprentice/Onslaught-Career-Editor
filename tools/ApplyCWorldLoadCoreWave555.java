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

public class ApplyCWorldLoadCoreWave555 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String previousName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] params;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String previousName, String callingConvention,
                DataType returnType, ParameterImpl[] params, String comment, String[] tags) {
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

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private DataType charPtr() {
        return new PointerDataType(CharDataType.dataType);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cworld-load-core-wave555",
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
        if (spec.params.length == 0) {
            sb.append("void");
        }
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!fn.getName().equals(spec.name) && !fn.getName().equals(spec.previousName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + fn.getName());
            }
            boolean renameNeeded = !fn.getName().equals(spec.name);
            boolean updateNeeded = needsUpdate(fn, spec);
            if (dryRun) {
                if (renameNeeded) {
                    stats.wouldRename++;
                }
                if (updateNeeded) {
                    println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
                } else {
                    println("SKIP: " + spec.address + " already matches " + spec.name);
                }
                stats.skipped++;
                return;
            }
            if (!updateNeeded) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already matches " + spec.name);
                verifyReadBack(spec);
                return;
            }
            if (renameNeeded) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.params);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("APPLY: " + spec.address + " -> " + expectedSignature(spec));
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
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0050a870",
                "CWorld__ClearSetArrays",
                "CSPtrSetArray19__ClearAll",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("world", voidPtr())
                },
                "Wave555 owner/signature/comment hardening: raw singleton callsite loads ECX with DAT_00855090 before jumping here, and the body clears nineteen CSPtrSet slots at world +0x00 through +0x120 in 0x10 strides. Static retail-binary evidence only; exact CWorld member names, set element types, destructor ownership, runtime load/unload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "set-array", "owner-corrected")
            ),
            new Spec(
                "0x0050a9c0",
                "CWorld__InitSetArraysAndState",
                "CSPtrSetArray19__InitAndResetState",
                "__fastcall",
                voidPtr(),
                new ParameterImpl[] {
                    param("world", voidPtr())
                },
                "Wave555 owner/signature/comment hardening: raw singleton callsite loads ECX with DAT_00855090 before calling here. The body initializes nineteen CSPtrSet slots, zeros world state fields and arrays around +0x130, +0x200, and +0x20c, and sets load/resource sentinels at +0x26c through +0x278 to -1 before returning world. Static retail-binary evidence only; exact member names/layout, allocation ownership, runtime load/unload behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "set-array", "state-init", "owner-corrected")
            ),
            new Spec(
                "0x0050abb0",
                "CWorld__ShutdownAndClear_Thunk",
                "CWorld__ShutdownAndClear_Thunk",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("world", voidPtr())
                },
                "Wave555 signature/comment hardening: CGame__ShutdownRestartLoop loads ECX with DAT_00855090 and calls this entry, which is a pure jump thunk into CWorld__ShutdownAndClear. Static retail-binary evidence only; exact destructor ordering, global lifetime ownership, runtime shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "shutdown", "thunk")
            ),
            new Spec(
                "0x0050abc0",
                "CWorld__CloneScriptObjectCodeByName",
                "CWorld__CloneScriptObjectCodeByName",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("script_name", charPtr())
                },
                "Wave555 signature/comment hardening: RET 0x4 and CComplexThing__SetScript prove one explicit script_name argument after ECX; the older second explicit parameter was register carryover. The body scans the script-event set at this +0x120, compares each event name against script_name, clones the matching CScriptObjectCode, and fatal-errors when no script is found. Static retail-binary evidence only; exact script-event pair layout, clone ownership, runtime script binding behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "script-events", "clone", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ac70",
                "CWorld__LoadScriptEvents",
                "CWorld__LoadScriptEvents",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("mem_buffer", voidPtr())
                },
                "Wave555 signature/comment hardening: caller CWorld__LoadWorld pushes one buffer argument and RET 0x4 confirms a single explicit parameter after ECX. The body reads the script-event count from mem_buffer, allocates name/code pairs, appends them to the CWorld script-event set at this +0x120, and advances over the trailing per-event bytes. Static retail-binary evidence only; exact buffer type, script-event pair layout, event payload semantics, runtime script behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "script-events", "load-world", "phantom-param-removed")
            ),
            new Spec(
                "0x0050ada0",
                "CWorld__ShutdownAndClear",
                "CWorld__ShutdownAndClear",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("world", voidPtr())
                },
                "Wave555 signature/comment hardening: ECX-only CWorld shutdown routine reached through the 0x0050abb0 thunk. The body releases global/subobject pointers, destroys object sets and linked pairs, clears readers and pending waypoint objects, shuts down BattleEngineConfigurations, clears CWorldMeshList, frees resource fields, and resets world state. Static retail-binary evidence only; exact member names, destruction order invariants, runtime shutdown behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "shutdown", "cleanup")
            ),
            new Spec(
                "0x0050af70",
                "CWorld__FindThingByName",
                "CWorld__FindThingByName",
                "__thiscall",
                voidPtr(),
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("thing_name", charPtr())
                },
                "Wave555 signature/comment hardening: callers pass one name pointer after loading ECX with DAT_00855090, and RET 0x4 confirms a single explicit thing_name argument. The body iterates the CWorld thing set at this +0xa0, calls each entry's name vfunc, compares against thing_name, and returns the matching thing pointer or null. Static retail-binary evidence only; exact thing-set layout, vtable owner, name lifetime, runtime lookup behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "thing-lookup", "phantom-param-removed")
            ),
            new Spec(
                "0x0050b520",
                "CWorld__LoadWorldFile",
                "CWorld__LoadWorldFile",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("world_id", intType),
                    param("is_base_world", intType)
                },
                "Wave555 signature/comment hardening: CGame__LoadLevel and CWorld__LoadWorld callsites pass ECX plus two stack arguments, with the recursive/base load call pushing world_id and then is_base_world=1. The body resolves and opens the requested world resource, drives deserialize/load helpers, and returns a nonzero status on success. Static retail-binary evidence only; exact resource-id type, boolean return contract, base/current world ownership, runtime load behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "load-world", "resource-load")
            ),
            new Spec(
                "0x0050b780",
                "CWorld__DeserializeWorld",
                "CWorld__DeserializeWorld",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("chunk_reader", voidPtr())
                },
                "Wave555 signature/comment hardening: CResourceAccumulator__ReadResourceFile loads ECX with DAT_00855090 and passes one reader/buffer argument; RET 0x4 confirms the single explicit parameter. The body reads base/current world identifiers, stores resource handles at this +0x26c through +0x278, allocates world managers/objects, and deserializes base/current world data when present. Static retail-binary evidence only; exact chunk-reader type, manager layouts, resource handle semantics, runtime deserialize behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "deserialize", "resource-load", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d4c0",
                "CWorld__LoadWorldHeader",
                "CWorld__LoadWorldHeader",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr()),
                    param("mem_buffer", voidPtr()),
                    param("is_base_world", intType)
                },
                "Wave555 signature/comment hardening: CWorld__LoadWorld pushes mem_buffer and is_base_world before this call, and RET 0x8 confirms two explicit arguments after ECX. The body reads header/version fields from the buffer and, for the non-base world path, loads BattleEngineConfigurations and stores the current world field at this +0x27c. Static retail-binary evidence only; exact header layout, flag semantics, configuration side effects, runtime world-load behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "load-world", "world-header", "phantom-param-removed")
            ),
            new Spec(
                "0x0050d580",
                "CWorld__InitLODLists",
                "CWorld__InitLODLists",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("world", voidPtr())
                },
                "Wave555 signature/comment hardening: CWorld__LoadWorld calls this ECX-only helper. The body allocates three 0x2004-byte bitplane/LOD structures, initializes them with thresholds 35, 45, and 60, and stores them at world +0x200, +0x204, and +0x208. Static retail-binary evidence only; exact LOD/occupancy structure type, threshold units, runtime visibility behavior, BEA launch, patching, and rebuild parity remain unproven.",
                tags("cworld", "lod", "load-world")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: mode=" + (dryRun ? "dry" : "apply")
            + " updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave555 apply had missing/bad rows");
        }
    }
}
