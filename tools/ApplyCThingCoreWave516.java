//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCThingCoreWave516 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.callingConvention = callingConvention;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cthing-core-wave516",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.newName).append("(");
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
        if (!fn.getName().equals(spec.newName)) {
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
        if (!readBack.getName().equals(spec.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
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
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f33e0",
                "CThing__ctor_like_004f33e0",
                "CThing__ctor_base",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing constructor body. The body installs base and CThing vtables, invalidates the embedded CMapWhoEntry at +0x0c, clears render/collision pointers at +0x30/+0x38, initializes flags at +0x2c to TF_IN_MAP_WHO, and assigns/increments the global thing counter at 0x0083da30. Static retail evidence only; concrete CThing layout, constructor exception-state details, runtime object creation behavior, and rebuild parity remain unproven.",
                tags("cthing", "constructor", "source-parity")
            ),
            new Spec(
                "0x004f3480",
                "CThing__VFunc_01_004f3480",
                "CThing__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave516 rename/signature/comment hardening: CThing scalar deleting destructor. Vtable data at 0x005df5cc points here; the body calls CThing__dtor_base, frees this through CDXMemoryManager__Free only when delete_flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership, exact compiler emission identity, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("cthing", "destructor", "vtable-slot-1")
            ),
            new Spec(
                "0x004f34a0",
                "CThing__VFunc_09_004f34a0",
                "CThing__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing::Init-style body. RET 0x4 and CComplexThing__Init callsites show one init argument; the body lazily initializes render state, copies init position at +0x04 into this+0x1c, clips against ground/water, initializes map-who/collision-seeking state, marks renderable bit 0x800000 when a render thing exists, handles inactive init state, and adds this to the world set. Static retail evidence only; concrete CInitThing/CThing layouts, runtime spawn behavior, and rebuild parity remain unproven.",
                tags("cthing", "init", "source-parity", "map-who")
            ),
            new Spec(
                "0x004f35d0",
                "CThing__InitRenderThing",
                "CThing__InitRenderThing",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 signature/comment hardening: CThing render-object initialization helper. Broad vtable data points to this slot; the body calls the class-id virtual at +0x20, passes this+0x08 as owner context when this is non-null, instantiates the resource descriptor chain, and stores the render thing pointer at this+0x30. Static retail evidence only; exact CreateAndGetRenderThing/source helper identity, concrete render-object layout, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cthing", "render", "init", "vtable-slot")
            ),
            new Spec(
                "0x004f3600",
                "VFuncSlot_02_004f3600",
                "CThing__Shutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing shutdown path. The body removes this from the world thing set, removes it from the big-things set when flag 0x40 is present, shuts down monitor core state, then dispatches the scalar-deleting destructor through vtable slot 1. Static retail evidence only; exact world-set layout, event ordering, runtime shutdown behavior, and rebuild parity remain unproven.",
                tags("cthing", "shutdown", "source-parity", "world-list")
            ),
            new Spec(
                "0x004f3640",
                "CThing__ctor_like_004f3640",
                "CThing__dtor_base",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 rename/signature/comment hardening: CThing destructor-base body. The body restores CThing vtables, scalar-deletes the collision-seeking object at +0x38 and render thing at +0x30 when present, clears both fields, removes the embedded map-who entry, and shuts down monitor state. Static retail evidence only; exact compiler destructor emission identity, concrete field layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("cthing", "destructor", "source-parity")
            ),
            new Spec(
                "0x004f36d0",
                "CThing__Render",
                "CThing__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("render_flags", uintType)},
                "Wave516 signature/comment hardening: CThing render slot. RET 0x4 confirms one explicit render_flags argument; the body skips invisible flag 0x10, ORs highlight flag 0x2 when objective flag 0x20 is set, renders the object at +0x30 unless TF_DONT_RENDER bit 0x8 is present, and optionally draws the debug cuboid when global draw-debug bit 0x20 is set. Static retail evidence only; exact render flag enum, render-object layout, runtime rendering behavior, and rebuild parity remain unproven.",
                tags("cthing", "render", "source-parity", "vtable-slot")
            ),
            new Spec(
                "0x004f3710",
                "CThing__RenderImposter",
                "CThing__RenderImposter",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 signature/comment hardening: CThing imposter-render slot. Broad vtable data points here; the body calls the render thing's +0x0c imposter path only when this+0x30 is non-null and TF_DONT_RENDER bit 0x8 is clear. Static retail evidence only; exact render-object virtual contract, runtime imposter behavior, and rebuild parity remain unproven.",
                tags("cthing", "render", "imposter", "vtable-slot")
            ),
            new Spec(
                "0x004f3730",
                "VFuncSlot_00_004f3730",
                "CThing__HandleEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("event", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing event dispatcher. The body checks event+0x04 for 2000 and dispatches shutdown through vtable slot +0x08, checks 0x7d2 and dispatches StartDieProcess through vtable slot +0xc8, and otherwise returns without a visible base dispatch in this optimized retail body. Static retail evidence only; exact CEvent layout, omitted/default-event behavior, runtime event sequencing, and rebuild parity remain unproven.",
                tags("cthing", "event", "source-parity", "vtable-slot")
            ),
            new Spec(
                "0x004f37c0",
                "CThing__DrawDebugCuboid",
                "CThing__DrawDebugCuboid",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 signature/comment hardening: CThing debug-volume draw helper. The body copies the identity matrix, uses render-thing bounding-box data when available, sets the world matrix from this+0x1c/+0x28, draws a green outer box, then draws a white radius box from virtual radius/bounding-radius calls. Static retail evidence only; exact matrix/vector layouts, render debug material identity, runtime debug-overlay behavior, and rebuild parity remain unproven.",
                tags("cthing", "debug-render", "source-parity")
            ),
            new Spec(
                "0x004f3940",
                "VFuncSlot_17_004f3940",
                "CThing__GetBoundingRadius",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing bounding-radius helper. The body asks render thing +0x10 for a bounding box and returns its +0x24 radius when available, otherwise falls back to the virtual GetRadius slot at +0x40. Ghidra models the x87 float return as double. Static retail evidence only; exact CBoundingBox layout, float ABI details, runtime collision/render behavior, and rebuild parity remain unproven.",
                tags("cthing", "bounds", "render", "source-parity")
            ),
            new Spec(
                "0x004f3970",
                "CThing__SetObjective",
                "CThing__SetObjective",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("enabled", intType)},
                "Wave516 signature/comment hardening: CThing objective flag/list helper. RET 0x4 confirms one explicit enabled argument; enabled==1 adds this to global objective noticeboard 0x00855140 and sets flag 0x20 when not already marked, while false removes this and clears flag 0x20 when marked. Static retail evidence only; exact noticeboard layout, objective UI behavior, runtime mission behavior, and rebuild parity remain unproven.",
                tags("cthing", "objective", "world-list", "source-parity")
            ),
            new Spec(
                "0x004f39b0",
                "CUnit__DebugTraceIfFlag30Set",
                "CThing__UpdatePosition",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 source-parity owner correction: CThing::UpdatePosition-style helper, not a CUnit debug-trace helper. Current xrefs from movement/update paths and StickToGround/MoveTo-style callers match the source helper that updates the render thing when this+0x30 is non-null; the current callee name at the indirect target is still a separate symbol-quality issue. Static retail evidence only; exact CRTMesh update target identity, runtime transform propagation, and rebuild parity remain unproven.",
                tags("cthing", "position", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f39c0",
                "CThing__AddCollision",
                "CThing__InitCollisionSeekingThing",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init_collision", voidPtr)},
                "Wave516 source-parity owner/name correction: CThing::InitCollisionSeekingThing-style helper. RET 0x4 confirms one explicit init_collision argument; the body ignores disabled collision type -1, lazily allocates a 0x38-byte pool-0x0b collision-seeking object with thing.cpp line 0x136 evidence, downgrades mesh collision type 2 to 1 with a warning when no render thing exists, writes this into init_collision+0x00, and dispatches the collision init vtable slot. Static retail evidence only; concrete CInitCSThing/CCSPersistentThing layouts, runtime collision behavior, and rebuild parity remain unproven.",
                tags("cthing", "collision", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f3a50",
                "CCSPersistentThing__scalar_deleting_dtor",
                "CCSPersistentThing__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave516 signature/comment hardening: CCSPersistentThing scalar deleting destructor adjacent to the CThing collision-seeking allocation path. The body calls CCSPersistentThing__dtor_base, frees this only when delete_flags bit 0 is set, and returns this. Static retail evidence only; exact source class body, allocator ownership, runtime collision cleanup behavior, and rebuild parity remain unproven.",
                tags("collision", "persistent-collision", "destructor")
            ),
            new Spec(
                "0x004f3a70",
                "CCSPersistentThing__dtor",
                "CCSPersistentThing__dtor_base",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 rename/signature/comment hardening: CCSPersistentThing destructor-base helper. The body shuts down monitor state at this+0x24, then chains into CCollisionSeekingRound__Destructor for the base collision-seeking round fields. Static retail evidence only; exact CCSPersistentThing layout, source-body identity, runtime collision cleanup behavior, and rebuild parity remain unproven.",
                tags("collision", "persistent-collision", "destructor")
            ),
            new Spec(
                "0x004f3ac0",
                "CUnitAI__GetWorldPositionForTargeting",
                "CThing__GetCentrePos",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_pos", voidPtr)},
                "Wave516 source-parity owner correction: CThing::GetCentrePos-style helper, not a CUnitAI-specific function. The body writes a four-dword position/vector record to out_pos, uses type/flag bits to choose render-thing bounding-box origin, battle-engine/ground-unit center-height, or raw this+0x1c position, and is called by targeting, collision, HUD, shadow, and projectile helpers. Static retail evidence only; exact type-bit meanings, vector/matrix layouts, runtime targeting behavior, and rebuild parity remain unproven.",
                tags("cthing", "position", "targeting", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f3c50",
                "VFuncSlot_18_004f3c50",
                "CThing__StickToGround",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing::StickToGround-style helper. The body samples terrain/ground height for this+0x1c, writes the result to this+0x24, then updates render position when a render thing exists. Static retail evidence only; exact map-collision helper identity, render-update target naming, runtime terrain behavior, and rebuild parity remain unproven.",
                tags("cthing", "position", "ground", "source-parity")
            ),
            new Spec(
                "0x004f3cb0",
                "VFuncSlot_19_004f3cb0",
                "CThing__MoveTo",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("pos", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing::MoveTo-style helper. RET 0x4 confirms one explicit pos argument; the body copies four dwords from pos into this+0x1c and then updates render position when a render thing exists. Static retail evidence only; exact FVector/packed-position layout, render-update target naming, runtime movement behavior, and rebuild parity remain unproven.",
                tags("cthing", "position", "movement", "source-parity")
            ),
            new Spec(
                "0x004f3ce0",
                "VFuncSlot_20_004f3ce0",
                "CThing__Teleport",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("pos", voidPtr)},
                "Wave516 source-parity rename/signature/comment hardening: CThing::Teleport-style helper. RET 0x4 confirms one explicit pos argument; the body copies four dwords from pos into this+0x1c and then dispatches the MoveTo-style virtual slot at +0x4c with the same position. Static retail evidence only; exact FVector/packed-position layout, actor old-position semantics, runtime teleport behavior, and rebuild parity remain unproven.",
                tags("cthing", "position", "movement", "source-parity")
            ),
            new Spec(
                "0x004f3d10",
                "CCollisionSeekingRound__GetCollisionComponentOrNull",
                "CThing__GetPersistentCollisionSeekingThing",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 source-parity owner correction: CThing::GetCSPT-style helper. The body checks the collision-seeking pointer at this+0x38 and, when present, dispatches its +0x10 virtual to obtain a persistent collision-seeking thing; otherwise it returns NULL. Static retail evidence only; exact CCSPersistentThing/CCollisionSeekingThing layout, virtual contract, runtime collision behavior, and rebuild parity remain unproven.",
                tags("cthing", "collision", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f3de0",
                "CThing__IsOverWater",
                "CThing__IsOverWater",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave516 signature/comment hardening: CThing water/ground relation predicate. The body reads global water height 0x006fbdfc, samples terrain/ground height at this+0x1c, and returns 1 when water height is below the sampled ground height, otherwise 0. Static retail evidence only; exact map helper identity, source predicate naming nuance, runtime water behavior, and rebuild parity remain unproven.",
                tags("cthing", "water", "terrain", "source-parity")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave516 CThing core apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
