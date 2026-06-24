//@category Symbol

import ghidra.app.script.GhidraScript;
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

public class ApplyMapWhoWave428 extends GhidraScript {
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

    private Function functionAtEntry(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Function fn = getFunctionAt(toAddr(addressText));
        if (fn == null) {
            fn = getFunctionContaining(toAddr(addressText));
            if (fn != null && !fn.getEntryPoint().equals(toAddr(addressText))) {
                fn = null;
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
            "mapwho-wave428",
            "spatial-query",
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
                println("FAIL: missing function at " + spec.address + " for " + spec.name);
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

            println("OK: " + spec.address + " " + spec.name + " -> " + readBack.getSignature().toString());
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
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00491900",
                "CMapWhoEntry__Init",
                "__fastcall",
                voidType,
                "Wave428 signature/comment correction: RET with no stack cleanup confirms a register-only entry initializer. The body clears +0x00/+0x04 next/previous links for the CMapWhoEntry-style record. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-init", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("entry", voidPtr)
                }
            ),
            new Spec(
                "0x00491930",
                "CMapWho__Destroy",
                "__fastcall",
                voidType,
                "Wave428 signature/comment correction: RET with no stack cleanup confirms a register-only destroy helper. The body walks the +0x90 level-array pointer slots, destroys each allocated entry array through CDXLandscape__DestroyArrayWithCallback, frees the vector blocks with OID__FreeObject, then clears +0x90. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("destroy", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004919b0",
                "CMapWho__Init",
                "__fastcall",
                voidType,
                "Wave428 signature/comment correction: RET with no stack cleanup confirms a register-only init helper. The body allocates five level arrays from 64x64 down to 4x4, stores the level pointer table at +0x90, writes shift/width/height metadata, links child sector groups, and emits the fatal construction warning if a child slot is already present. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("init", "quadtree-levels", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00491c50",
                "CMapWho__GetLevelForRadius",
                "__thiscall",
                intType,
                "Wave428 signature/comment correction: RET 0x4 confirms one radius stack argument. The body compares radius against scale-adjusted level cell sizes using level metadata near +0xa4 and warns when the object is too big for the map who system. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("radius-level", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("radius", floatType)
                }
            ),
            new Spec(
                "0x00491cd0",
                "CMapWho__AddEntry",
                "__thiscall",
                voidType,
                "Wave428 signature/comment correction: RET 0x4 confirms one entry stack argument. The body uses entry sector/level fields to locate the sector head under +0x90, inserts entry at the head of the doubly linked list, and fixes previous-link ownership when an old head exists. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-list", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("entry", voidPtr)
                }
            ),
            new Spec(
                "0x00491d20",
                "CMapWho__RemoveEntry",
                "__thiscall",
                voidType,
                "Wave428 signature/comment correction: RET 0x4 confirms one entry stack argument. The body unlinks entry through its next/previous links and clears the owning sector head when the removed entry was the current head under +0x90. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-list", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("entry", voidPtr)
                }
            ),
            new Spec(
                "0x00491d80",
                "CMapWho__SetIteratorFromSectorHead",
                "__thiscall",
                voidPtr,
                "Wave428 owner/signature correction: RET 0x4 confirms one sector_entry stack argument. The body writes the sector head at +0x04 into this +0x00 and returns the current entry through EAX. This supersedes the stale CCollisionSeekingRound owner because xrefs include collision, dynamic-unit rendering, and tree-geometry callers. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] { "CCollisionSeekingRound__IterSetHeadFromMapWhoEntry" },
                tags("iterator", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("sector_entry", voidPtr)
                }
            ),
            new Spec(
                "0x00491d90",
                "CMapWho__AdvanceIteratorAndGetCurrent",
                "__fastcall",
                voidPtr,
                "Wave428 owner/signature correction: RET with no stack cleanup confirms a register-only iterator helper. The body advances this +0x00 through the current entry next pointer when present and returns the current entry through EAX. This supersedes the stale CCollisionSeekingRound owner because xrefs include collision, dynamic-unit rendering, and tree-geometry callers. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] { "CCollisionSeekingRound__IterPopNextEntry" },
                tags("iterator", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00491da0",
                "CMapWho__IsSectorCoordInBounds",
                "__stdcall",
                intType,
                "Wave428 owner/signature correction: RET 0x4 confirms one sector_coord stack argument. The body validates level 0..4 and x/y sector bounds against 64 >> (4 - level). This narrows the previous CMapWho__IsEntryInBounds wording to sector-coordinate validation. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] { "CMapWho__IsEntryInBounds" },
                tags("sector-bounds", "owner-corrected", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("sector_coord", voidPtr)
                }
            ),
            new Spec(
                "0x00491df0",
                "CMapWho__SetupNextRadiusLevel",
                "__fastcall",
                intType,
                "Wave428 signature/comment correction: RET with no stack cleanup confirms a register-only radius-query helper. The body decrements the active level, uses the query radius at +0x28 plus level cell scale to compute sector bounds at +0x04/+0x08/+0x0c/+0x10, seeds the current sector coordinate at +0x2c/+0x2e, and returns 0 when levels are exhausted. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] { "CMapWho__SetupNextLevel" },
                tags("radius-query", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00491ea0",
                "CMapWho__GetFirstEntryWithinRadius",
                "__thiscall",
                voidPtr,
                "Wave428 signature/comment correction: RET 0x14 confirms query_x/query_y/query_z/query_w plus radius stack arguments. The body stores the four-dword query context at +0x14..+0x20, stores radius at +0x28, seeds radius-query state, calls CMapWho__SetupNextRadiusLevel, and returns the first non-null sector entry found. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("radius-query", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("query_x", floatType),
                    param("query_y", floatType),
                    param("query_z", floatType),
                    param("query_w", floatType),
                    param("radius", floatType)
                }
            ),
            new Spec(
                "0x00492020",
                "CMapWho__GetNextEntryWithinRadius",
                "__fastcall",
                voidPtr,
                "Wave428 signature/comment correction: RET with no stack cleanup confirms a register-only radius-query iterator helper. The body checks the active flag, emits the GetNextEntryWithinRadius not set up warning when absent, advances the current linked entry, walks sector coordinates, calls CMapWho__SetupNextRadiusLevel when a level is exhausted, and returns the next non-null entry. Static retail evidence only from mapwho.cpp debug-path context; runtime spatial-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("radius-query", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
            if (monitor.isCancelled()) {
                break;
            }
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave428 MapWho apply failed");
        }
    }
}
