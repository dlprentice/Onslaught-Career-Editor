//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.ShortDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXPatchManagerWave613 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
            "cdxpatch-wave613",
            "retail-binary-evidence",
            "signature-corrected",
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
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
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
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType shortType = ShortDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00550380",
                "CDXPatch__Constructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave613 CDXPatch manager hardening: vector-constructor callsites 0x005504ab, 0x0055052a, and 0x005505ad pass this ECX-only constructor for each 0x50-byte CDXPatch pool entry. Body calls CVBuffer__ctor_base, installs vtable 0x005e5114, and returns this. Static retail decompile/instruction/xref/vtable evidence only; exact CDXPatch layout, vtable slot 0 boundary at 0x00550320, runtime terrain rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch", "constructor", "vtable-005e5114", "pool-entry", "callsite-verified")
            ),
            new Spec(
                "0x005503a0",
                "CDXPatch__Destructor_thunk",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave613 CDXPatch manager hardening: vector-destructor callsites 0x005504a6, 0x00550525, and 0x005505a8 pass this thunk beside CDXPatch__Constructor for pool cleanup. Body tail-jumps to CVBuffer__dtor_base and returns. Static retail decompile/instruction/xref/vtable evidence only; scalar-deleting vtable slot 0 remains an unbounded target at 0x00550320, and exact destructor ownership, runtime terrain rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch", "destructor-thunk", "cvbuffer", "pool-entry", "callsite-verified")
            ),
            new Spec(
                "0x005503b0",
                "CDXPatchManager__ReleasePatches",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("patch_pool_entry", voidPtr) },
                "Wave613 CDXPatch manager hardening: CDXPatchManager__Destroy passes this helper as a callback at callsite 0x005506f0 over the 8-byte patch-pool entries. Body reads the patch array pointer at entry +0x00, invokes its vtable slot 0 with delete flag 3 when non-null, clears the pointer, and returns. Static retail decompile/instruction/xref evidence only; exact pool-entry layout, scalar-delete boundary at 0x00550320, runtime terrain rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch-manager", "pool-release", "callback", "vtable-dispatch", "callsite-verified")
            ),
            new Spec(
                "0x005503d0",
                "CDXPatchManager__ResetPatchSlots",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("patch_pool", voidPtr) },
                "Wave613 CDXPatch manager hardening: CDXLandscape__Reset callsite 0x00545392 and CDXEngine__InvalidateLandscapeTilesAndPatchSlots callsite 0x005473d5 pass one patch-pool pointer in ECX. Body walks pool.count entries, advances by 0x50 bytes, and writes the free-slot marker 0xffff to each CDXPatch slot field at +0x3c. Static retail decompile/instruction/xref evidence only; exact pool/patch layout, runtime LOD behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch-manager", "patch-pool", "slot-reset", "slot-marker-ffff", "callsite-verified")
            ),
            new Spec(
                "0x00550400",
                "CDXPatchManager__AllocatePatchSlot",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("slot_id", shortType)
                },
                "Wave613 CDXPatch manager hardening: CDXLandscape__UpdateLOD callsite 0x00546fa6 passes a patch-pool pointer in ECX and one RET 0x4 slot_id argument. Body scans 0x50-byte CDXPatch entries until it finds +0x3c == -1, stores slot_id at +0x3c, returns that patch pointer, or returns null when the pool is exhausted. Static retail decompile/instruction/xref evidence only; exact slot ownership, runtime terrain LOD behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch-manager", "patch-pool", "slot-allocation", "ret-0004", "callsite-verified")
            ),
            new Spec(
                "0x00550430",
                "CDXPatchManager__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("lod2_patch_count", intType),
                    param("lod4_patch_count", intType),
                    param("lod8_patch_count", intType)
                },
                "Wave613 CDXPatch manager hardening: CDXEngine__Init callsite 0x0053d6c3 passes the engine-owned manager fields in ECX plus counts 800, 300, and 90. Body allocates the manager pool table from DXPatchManager.cpp line 0x54, allocates three patch arrays from line 0x11, constructs 0x50-byte CDXPatch entries, creates grid vertex buffers for LOD steps 2/4/8, allocates 48 CLandscapeTexture entries from line 0x5b, and initializes three 16-texture mip groups. Static retail decompile/instruction/xref evidence only; exact CDXPatchManager/CLandscapeTexture layouts, runtime terrain rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch-manager", "init", "patch-pools", "landscape-textures", "debug-path-0065211c", "callsite-verified")
            ),
            new Spec(
                "0x005506e0",
                "CDXPatchManager__Destroy",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave613 CDXPatch manager hardening: CDXEngine__Shutdown callsite 0x0053d467 passes the engine-owned manager fields in ECX. Body destroys the manager pool table through CDXLandscape__DestroyArrayWithCallback using CDXPatchManager__ReleasePatches, frees the count header through CDXMemoryManager__Free, clears the pool pointer, releases the landscape-texture vector through vtable slot 0 with delete flag 3, clears the texture pointer, and returns. Static retail decompile/instruction/xref evidence only; exact ownership, runtime terrain teardown, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch-manager", "destroy", "patch-pools", "landscape-textures", "callsite-verified")
            ),
            new Spec(
                "0x00550730",
                "CDXPatch__FreeData",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave613 CDXPatch manager hardening: unbounded callsite 0x005120cb reaches this ECX-only patch-data cleanup helper. Body frees the data pointer at CDXPatch +0x0c through CDXMemoryManager__Free when non-null, clears it, and returns. Static retail decompile/instruction/xref evidence only; exact data-buffer ownership, caller boundary, runtime terrain data lifecycle, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch", "data-buffer", "free-data", "memory-manager", "callsite-verified")
            ),
            new Spec(
                "0x00550750",
                "CDXPatch__LoadFromFile",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("chunk_reader", voidPtr)
                },
                "Wave613 CDXPatch manager hardening: CResourceAccumulator__ReadResourceFile callsite 0x004d7875 passes a CDXPatch in ECX and one chunk_reader argument. Body reads 3x16 four-byte values into the patch table at +0x10, reads a data count into +0xd0, allocates count*2 bytes from DXPatchManager.cpp line 0x94, reads 16-bit data into +0x0c, marks +0x08 loaded, and returns. Static retail decompile/instruction/xref evidence only; exact serialized patch format, runtime terrain data use, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxpatch", "load-from-file", "chunk-reader", "serialized-patch-data", "ret-0004", "callsite-verified")
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
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
