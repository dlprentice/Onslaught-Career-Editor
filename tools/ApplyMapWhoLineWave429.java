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

public class ApplyMapWhoLineWave429 extends GhidraScript {
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
            "mapwho-wave429",
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
                "0x00492110",
                "CMapWho__GetFirstEntryWithinLine",
                "__thiscall",
                voidPtr,
                "Wave429 signature/comment correction: RET 0x20 confirms eight float line_start/line_end stack arguments after the CMapWho context. The body clips the line through Geometry__ClipSegmentAgainstAABB3D, stores line_start/line_end context at +0x38..+0x54, seeds line-query state, and walks CMapWho__SetupLineLevel/CMapWho__AdvanceLineIterator until an entry or exhaustion. Static retail evidence only from mapwho.cpp debug-path context; runtime line-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("line-query", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("line_start_x", floatType),
                    param("line_start_y", floatType),
                    param("line_start_z", floatType),
                    param("line_start_w", floatType),
                    param("line_end_x", floatType),
                    param("line_end_y", floatType),
                    param("line_end_z", floatType),
                    param("line_end_w", floatType)
                }
            ),
            new Spec(
                "0x004922f0",
                "CMapWho__SetupLineLevel",
                "__fastcall",
                intType,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only line-level helper. The body decrements the active line level at +0x24, selects the major axis and step deltas at +0x68/+0x6c/+0x70/+0x74, backs up one step from the stored line start, converts that point through CMapWho__WorldToSector, and seeds current/base sector fields. Static retail evidence only from mapwho.cpp debug-path context; runtime line-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("line-query", "line-iterator", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004924b0",
                "CMapWho__AdvanceLineIterator",
                "__fastcall",
                intType,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only line iterator helper. The body advances the line iterator phase at +0x34, applies perpendicular sector probes in +0x5c/+0x5e/+0x60, advances sample index +0x58 against +0x74, refreshes base/current sector fields through CMapWho__WorldToSector, and returns 0 only when the level sample budget is exhausted. Static retail evidence only from mapwho.cpp debug-path context; runtime line-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("line-query", "line-iterator", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x004925a0",
                "CMapWho__GetNextEntryWithinLine",
                "__fastcall",
                voidPtr,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only line-query iterator. The body checks the active flag, emits the GetNextEntryWithinLine not-set-up warning when absent, advances the current entry link, then alternates CMapWho__AdvanceLineIterator and CMapWho__SetupLineLevel until it finds a sector entry or clears the active flag. Static retail evidence only from mapwho.cpp debug-path context; runtime line-query behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("line-query", "line-iterator", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00492670",
                "CMapWho__WorldToSector",
                "__thiscall",
                voidPtr,
                "Wave429 signature/comment correction: RET 0xc confirms sector_coord, position, and level stack arguments after the CMapWho context. The body rounds/clamps x/y using level metadata at +0x94, width bounds at +0xa8, and height bounds at +0xbc, writes sector x/y/level into sector_coord, and returns the output sector pointer through EAX. Static retail evidence only from mapwho.cpp debug-path context; runtime sector mapping, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("sector-conversion", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("sector_coord", voidPtr),
                    param("position", voidPtr),
                    param("level", intType)
                }
            ),
            new Spec(
                "0x004926e0",
                "CMapWho__Sort",
                "__fastcall",
                voidType,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only sector-sort helper. The body walks the five mapwho level grids, validates sector coordinates before list traversal, emits the invalid-sector warning on bad coordinates, calls CMapWhoEntry__GetOwner, and moves entries whose owner flag includes 0x2000000 toward the sector tail. Static retail evidence only from mapwho.cpp debug-path context; runtime sort behavior, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("sector-sort", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00492860",
                "CMapWho__DebugDrawSector",
                "__thiscall",
                voidType,
                "Wave429 signature/comment correction: RET 0x8 confirms packed_sector_coord and level stack arguments after the CMapWho context. The body unpacks sector x/y, scales by the selected level metadata, chooses a debug color by level, prepares a debug volume, and calls CThing__RenderDebugVolumeOverlay. Static retail evidence only from mapwho.cpp debug-path context; runtime debug rendering, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("debug-draw", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("packed_sector_coord", intType),
                    param("level", intType)
                }
            ),
            new Spec(
                "0x00492950",
                "CMapWho__DebugDraw",
                "__fastcall",
                voidType,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only debug-draw helper. The body resets render state/world matrix, iterates mapwho sectors across levels, calls CMapWhoEntry__GetOwner to filter entries, and calls CMapWho__DebugDrawSector for the first qualifying entry per sector. Static retail evidence only from mapwho.cpp debug-path context; runtime debug rendering, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("debug-draw", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr)
                }
            ),
            new Spec(
                "0x00492ba0",
                "CMapWhoEntry__SetPosition",
                "__thiscall",
                voidType,
                "Wave429 signature/comment correction: RET 0xc confirms position, owner, and explicit_radius stack arguments after the entry context. The body clears entry links, derives or overrides an object radius, selects a mapwho level through CMapWho__GetLevelForRadius, converts position with CMapWho__WorldToSector, stores sector x/y/level at entry offsets +0x08/+0x0a/+0x0c, and adds the entry to the global mapwho singleton. Static retail evidence only from mapwho.cpp debug-path context; runtime entry tracking, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-position", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position", voidPtr),
                    param("owner", voidPtr),
                    param("explicit_radius", floatType)
                }
            ),
            new Spec(
                "0x00492c60",
                "CMapWhoEntry__Invalidate",
                "__fastcall",
                voidType,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only entry invalidation helper. The body writes -1 to the entry level field at +0x0c. Static retail evidence only from mapwho.cpp debug-path context; runtime entry tracking, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-position", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("entry", voidPtr)
                }
            ),
            new Spec(
                "0x00492c70",
                "CMapWhoEntry__RemoveFromMap",
                "__fastcall",
                voidType,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only entry removal helper. The body checks whether the entry level is not -1 and removes the entry from the global mapwho singleton DAT_00704200 through CMapWho__RemoveEntry. Static retail evidence only from mapwho.cpp debug-path context; runtime entry tracking, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-position", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("entry", voidPtr)
                }
            ),
            new Spec(
                "0x00492c90",
                "CMapWhoEntry__GetOwner",
                "__fastcall",
                voidPtr,
                "Wave429 signature/comment correction: RET with no stack cleanup confirms a register-only owner helper. The body returns entry - 0x0c as the owning object pointer, matching callers that pass CMapWhoEntry pointers into sort/debug/collision/targeting readers. Static retail evidence only from mapwho.cpp debug-path context; runtime owner identity, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-owner", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("entry", voidPtr)
                }
            ),
            new Spec(
                "0x00492ca0",
                "CMapWhoEntry__UpdatePosition",
                "__thiscall",
                intType,
                "Wave429 signature/comment correction: RET 0x4 confirms one position stack argument after the entry context. The body recomputes sector x/y/level with CMapWho__WorldToSector, returns 0 when unchanged, removes the entry from its old map sector when valid, writes the new sector fields, re-adds through CMapWho__AddEntry, and returns 1 after movement. Static retail evidence only from mapwho.cpp debug-path context; runtime entry tracking, concrete layout beyond observed offsets, and rebuild parity remain unproven.",
                new String[] {},
                tags("entry-position", "signature-corrected", "comment-hardened"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("position", voidPtr)
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
            throw new RuntimeException("Wave429 MapWho line/entry apply failed");
        }
    }
}
