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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCMeshWave443 extends GhidraScript {
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
            "cmesh-wave443",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004a5020",
                "CMesh__Init",
                "__thiscall",
                voidPtr,
                "Wave443 signature/comment hardening: constructor-style CMesh initializer; zeros resource/count fields, sets default LOD +0x164 to 0.5f and field +0x16c to -2, allocates the +0x150 resource buffer, and links this at the head of DAT_00704ad8/g_pMeshList via next pointer +0x158. Static retail decompile/xref/instruction evidence only; exact field names, allocator ownership, runtime load behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "init", "resource-list", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a50b0",
                "CMesh__FreeResourcesAndUnlink",
                "__thiscall",
                voidType,
                "Wave443 signature/comment hardening: CMesh teardown helper; walks DAT_00704ad8/g_pMeshList to unlink this, frees the 0x24-byte material array with CMesh__ReleaseEmbeddedResources callbacks, frees CMeshPart pointer entries through CMeshPart__FreeResources, releases emitter/index/texture arrays, and decrements chained mesh refcount +0x170 before clearing +0x08. Static retail decompile/xref/instruction evidence only; exact field names, runtime destruction ordering, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "resource-cleanup", "linked-list", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a51f0",
                "CMeshPart__FreeResources",
                "__thiscall",
                voidType,
                "Wave443 signature/comment hardening: CMeshPart resource-free entry used by CMesh teardown; entry is a tail jump into the existing 0x004ae640 free-owned-resource helper, which releases cached positions/orientations, dynamic vertex/material arrays, bone/link arrays, influence-map runtime buffers, and vtable-owned field +0x138 when present. Static retail decompile/xref/instruction evidence only; exact CMeshPart field names, destructor ownership, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmeshpart", "resource-cleanup", "thunk", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a5200",
                "CMesh__InitStatic",
                "__cdecl",
                intType,
                "Wave443 signature/comment hardening: one-time/static mesh setup; releases prior DAT_00704adc default texture storage if present, allocates a 0x24-byte default entry, initializes single-vertex defaults, then resolves meshtex\\default.tga into DAT_00704adc and returns 1. Static retail decompile/xref/instruction evidence only; global lifetime, texture-cache ownership, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "static-init", "default-texture", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {}
            ),
            new Spec(
                "0x004a5500",
                "CMesh__MapStateNameToId",
                "__stdcall",
                voidType,
                "Wave443 signature/comment hardening: mesh animation/state-name mapper; compares an input state string against fixed retail tokens including STAND, SHOOT, SHOOT1, SHOOT2, HOVER, and SHOOTWALK, then stores the mapped state id at state_record+0x10. RET 0x8 and callsites from CMesh__Load confirm two stack arguments. Static retail decompile/xref/instruction evidence only; exact enum names and source parity remain unproven.",
                new String[] {},
                tags("cmesh", "animation-state", "state-map", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("state_name", charPtr),
                    param("state_record", voidPtr)
                }
            ),
            new Spec(
                "0x004a5670",
                "CMesh__OptimizeTextures",
                "__thiscall",
                voidType,
                "Wave443 signature/comment hardening: mesh material/texture dedup pass; scans the 0x24-byte material entries for identical texture and float payloads, rewrites matching dynamic-vertex material slots across CMeshPart entries to the earlier index, and emits the retail OptimiseTextures debug line. Static retail decompile/xref/instruction evidence only; exact material structure names, runtime visual equivalence, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "texture-dedup", "optimization", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004a5970",
                "CMesh__LoadByNameWithStatus",
                "__thiscall",
                intType,
                "Wave443 signature/comment hardening: named mesh load wrapper; logs/statuses the mesh name, builds a data\\Meshes path from the basename, copies that basename to this+0x24, opens a CDXMemBuffer from file mode 0x11, then calls CMesh__Load(this, mem_buffer, load_context) and returns its success status. RET 0x8 confirms two stack arguments after this. Static retail decompile/xref/instruction evidence only; load_context shape, archive fallback behavior, runtime IO behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "load-wrapper", "file-io", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mesh_name", charPtr),
                    param("load_context", voidPtr)
                }
            ),
            new Spec(
                "0x004a5b70",
                "CMesh__Load",
                "__thiscall",
                intType,
                "Wave443 signature/comment hardening: main CMesh stream loader; validates the mesh magic/version stream header against DAT_00704a90 and fixed version tokens, allocates material and part tables, supports old and newer CMeshPart load paths, maps animation state names through CMesh__MapStateNameToId, handles chained mesh loads, then runs CMesh__OptimizeTextures, part linking, bounds, vtable refresh, and frame-cache setup before returning success. Static retail decompile/xref/instruction evidence only; exact file-format field names, load_context shape, runtime asset behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("cmesh", "stream-load", "mesh-format", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mem_buffer", voidPtr),
                    param("load_context", voidPtr)
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
        if (stats.bad > 0 || stats.missing > 0) {
            throw new RuntimeException("ApplyCMeshWave443 failed: bad=" + stats.bad + " missing=" + stats.missing);
        }
    }
}
