//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCRenderQueueCoreWave870 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String convention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String convention, DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.convention = convention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
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
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "crenderqueue-core-wave870",
            "wave870-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-reviewed",
            "important-renderer-infrastructure",
            "render-queue",
            "renderer-connective-code"
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
        if (!spec.convention.equals(fn.getCallingConventionName())) {
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

    private boolean alreadyApplied(Function fn, Spec spec) {
        return fn.getName().equals(spec.name)
            && signatureMatches(fn, spec)
            && spec.comment.equals(fn.getComment())
            && hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.convention).append(" ").append(spec.name).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                stats.bad++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }

            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsComment = !spec.comment.equals(fn.getComment());
            boolean needsTags = !hasAllTags(fn, spec.tags);

            if (!needsSignature && !needsComment && !needsTags) {
                println("SKIP_OK: " + spec.address + " " + spec.name + " already current");
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY_UPDATE: " + spec.address + " " + spec.name
                    + " -> " + expectedSignature(spec)
                    + " needsSignature=" + needsSignature
                    + " needsComment=" + needsComment
                    + " needsTags=" + needsTags);
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else if (needsComment || needsTags) {
                    stats.commentOnlyUpdated++;
                }
                return;
            }

            if (needsSignature) {
                fn.setCallingConvention(spec.convention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            } else if (needsComment || needsTags) {
                stats.commentOnlyUpdated++;
            }
            if (needsComment) {
                fn.setComment(spec.comment);
            }
            for (String tag : spec.tags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                }
            }

            Function readback = functionAtEntry(spec.address);
            if (readback == null || !alreadyApplied(readback, spec)) {
                println("READBACK_BAD: " + spec.address);
                if (readback != null) {
                    println("READBACK_GOT: " + readback.getName() + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
                }
                stats.bad++;
                return;
            }
            println("READBACK_OK: " + spec.address + " " + spec.name + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
            stats.updated++;
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
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
                "0x005515a0",
                "CDXEngine__InitConsoleVar_UseRenderQueue",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("storage", voidPtr)},
                "Wave870 CRenderQueue core static read-back: clears the storage byte, registers console variable cg_userenderqueue with description string \"Use the render queue\" through CConsole__RegisterVariable(&DAT_00663498, ..., type 3, storage, 0, 0), then clears storage+4. Xrefs are CGame__Init and CGame__InitRestartLoop; source-side DXEngine/PCEngine references show RENDERQUEUE.Init(), Render(), Reset(), and mUseQueue debug overlay concepts, but Steam retail Ghidra evidence remains authority. This is important renderer infrastructure, not low-importance filler. Static retail Ghidra evidence only; exact console variable storage layout, runtime toggling behavior, BEA patching, and rebuild parity remain unproven.",
                tags("render-queue-cvar", "console-variable", "game-init")
            ),
            new Spec(
                "0x005515d0",
                "CRenderQueueBucket__Reset",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("bucket", voidPtr)},
                "Wave870 CRenderQueue core static read-back: clears bucket+4 and returns. The saved xref is CDXEngine__Render at 0x0053e4da, placing this tiny helper in the per-frame render queue/bucket preparation path. Static retail Ghidra evidence only; exact bucket layout, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("bucket-reset", "cdxengine-render", "tiny-state-helper")
            ),
            new Spec(
                "0x005515e0",
                "CRenderQueueBucket__RenderAndRecycle",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("bucket_set", voidPtr), param("bucket_index", intType)},
                "Wave870 CRenderQueue core static read-back: walks a bucket-linked render-item list, updates cached shader object, animated texture frame, render state 0x3c, transform/matrix state, and world matrix when item fields differ from the queue cache, applies pending CDXEngine render state, issues CEngine__DrawIndexedPrimitives, frees each consumed item through CDXMemoryManager__Free, then clears the bucket head. The caller is CRenderQueue__BeginFrame. This is high-importance render batching/connective infrastructure. Static retail Ghidra evidence only; exact queue/bucket/item layout, exact D3D state enum names, runtime draw behavior, BEA patching, and rebuild parity remain unproven.",
                tags("bucket-render-recycle", "draw-indexed-primitives", "state-cache", "memory-recycle")
            ),
            new Spec(
                "0x00551920",
                "CRenderQueue__BeginFrame",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("queue", voidPtr)},
                "Wave870 CRenderQueue core static read-back: when queue byte 0 is enabled, resets cached texture/shader/material fields, seeds default scale/matrix values from DAT_009c7450/DAT_009c7480..8c, calls CDXEngine__SetWorldMatrixElements, applies stage/state defaults, dispatches CRenderQueueBucket__RenderAndRecycle(queue, 0, ...), then restores sampler/render states. Xrefs are two CDXEngine__Render sites. Static retail Ghidra evidence only; exact field names, frame-phase identity, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("begin-frame", "matrix-defaults", "cdxengine-render", "sampler-state")
            ),
            new Spec(
                "0x00551f20",
                "CRenderQueue__ctor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: installs the DeviceObject vtable during construction, vector-constructs two active-reader arrays at this+0x0c and this+0x10c with CGenericActiveReader__ctor_Zero/CGenericActiveReader__dtor, switches to the CRenderQueue vtable, then sets bytes this+0x704 and this+0x706 to 1. The callsite at 0x00551ef5 sits just before this function and lacks a containing function boundary. Static retail Ghidra evidence only; exact object layout, array purpose beyond active-reader storage, runtime lifecycle behavior, BEA patching, and rebuild parity remain unproven.",
                tags("constructor", "active-reader-array", "deviceobject-subobject", "vtable")
            ),
            new Spec(
                "0x00551fb0",
                "CRenderQueue__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("free_flag", intType)},
                "Wave870 CRenderQueue core static read-back: calls CRenderQueue__dtor(this), then frees this through CDXMemoryManager__Free(&DAT_009c3df0, this) when free_flag bit 0 is set. DATA xref 0x005e512c is the CRenderQueue scalar-deleting-dtor vtable slot. Static retail Ghidra evidence only; exact allocation ownership, runtime destruction order, BEA patching, and rebuild parity remain unproven.",
                tags("scalar-deleting-dtor", "vtable", "memory-free")
            ),
            new Spec(
                "0x00551fd0",
                "CGenericActiveReader__ctor_Zero",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: tiny shared constructor that zeroes the first dword of a CGenericActiveReader-like object. It is included in this wave because CRenderQueue__ctor uses it for both active-reader vector constructor ranges at this+0x0c and this+0x10c, though xrefs also include CHud__ctor_base, OID__CreateObject, CWorldPhysicsManager__CreateCharacter, and CDXLandscape__CreateMipLevels. Static retail Ghidra evidence only; exact active-reader object layout and runtime lifetime semantics remain unproven.",
                tags("active-reader", "shared-helper", "constructor", "crenderqueue-constructor")
            ),
            new Spec(
                "0x00551fe0",
                "CRenderQueue__dtor",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: sets the CRenderQueue vtable, destructs the active-reader vector range at this+0x10c and then the smaller active-reader vector range at this+0x0c through CRT__EhVectorDestructorIterator_WithUnwind and CGenericActiveReader__dtor, then calls DeviceObject__dtor_body. Xrefs are the adjacent no-boundary destructor thunk and CRenderQueue__scalar_deleting_dtor. Static retail Ghidra evidence only; exact object layout, runtime destruction behavior, BEA patching, and rebuild parity remain unproven.",
                tags("destructor", "active-reader-array", "deviceobject-subobject")
            ),
            new Spec(
                "0x00552660",
                "CRenderQueue__ResetOrPushSentinel",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: when DAT_0089d680 is clear and this+0x704 equals 1, walks the active sorted-reader/depth slots up to count this+0x5bc, clears each reader with CGenericActiveReader__SetReader(slot, NULL), and stores depth 0x46800000; otherwise it writes a -1.0 sentinel at the current count slot. The caller is CDXEngine__Render. Static retail Ghidra evidence only; exact sentinel/depth semantics, DAT_0089d680 meaning, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("depth-sentinel", "active-reader", "cdxengine-render", "dat-0089d680-gate")
            ),
            new Spec(
                "0x005526c0",
                "CRenderQueue__InsertSortedByDepth",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("item", voidPtr), param("depth", floatType)},
                "Wave870 CRenderQueue core static read-back: when DAT_0089d680 is clear, scans the depth array at this+0x10 in 8-byte entries until depth order requires insertion, shifts later entries down while preserving active-reader targets with CGenericActiveReader__SetReader, writes the new depth, then stores item into the matching active-reader slot at this+0x0c. Xrefs are CVBufTexture__RenderDynamicUnitPass and CRenderQueue__InsertIfDepthBelowIndexedLimit. Static retail Ghidra evidence only; exact sorted-list capacity/layout, DAT_0089d680 semantics, runtime LOD/render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("depth-sort", "active-reader", "dynamic-unit-render", "dat-0089d680-gate")
            ),
            new Spec(
                "0x00552740",
                "CRenderQueue__RecycleInactiveItems",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: when DAT_0089d680 is clear, scans the active 0x20-byte entries at this+0x10c, builds a free-entry pointer list at this+0x50c, marks live entries with byte +6, advances or decays state/timer bytes +5/+4 using DAT_00652230, clears readers that age out, and stores the free count at this+0x58c. It is called by CRenderQueue__RenderAll. Static retail Ghidra evidence only; exact fade/state byte meanings, DAT_00652230 timing semantics, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("recycle-inactive", "active-reader", "free-list", "frame-delta")
            ),
            new Spec(
                "0x00552800",
                "CRenderQueue__MergePendingItems",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: when DAT_0089d680 is clear, walks pending reader slots at this+0x0c, finds matching active entries under this+0x10c to clear stale byte +6 and promote state byte +5 from 1 to 2, or consumes a free entry from the this+0x50c list, sets state bytes +4/+5/+6/+8, and assigns the pending object through CGenericActiveReader__SetReader. It is called by CRenderQueue__RenderAll. Static retail Ghidra evidence only; exact active/pending entry layout, state byte semantics, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                tags("merge-pending", "active-reader", "free-list", "render-all-helper")
            ),
            new Spec(
                "0x005528b0",
                "CRenderQueue__RenderAll",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave870 CRenderQueue core static read-back: top-level queue render pass. It computes frame delta DAT_00652230 from PLATFORM__GetSysTimeFloat, exits early when DAT_0089d680 is set or queue byte this+0x704 is disabled, creates/uses fast VB DAT_00897a98, calls CRenderQueue__RecycleInactiveItems and CRenderQueue__MergePendingItems, updates active-entry age/state bytes, snapshots and restores render matrices/states, iterates active entries at this+0x10c with object pointers listed near this+0x640, samples static shadow height, computes distance/tint/alpha values, drives D3D device vtable calls, emits immediate triangle strips through CFastVB__LockAligned and CFastVB__RenderTriangleStripImmediate, restores render state, and resets global tint with CDXEngine__SetGlobalTintColorOpaque(0xe7). Static retail Ghidra evidence only; exact queue entry/object layout, exact Direct3D vtable semantics, runtime visual behavior, BEA patching, and rebuild parity remain unproven.",
                tags("render-all", "fast-vb", "static-shadow", "state-restore", "global-tint")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave870 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
