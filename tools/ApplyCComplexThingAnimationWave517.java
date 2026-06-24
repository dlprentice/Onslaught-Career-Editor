//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyCComplexThingAnimationWave517 extends GhidraScript {
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
            "ccomplexthing-animation-wave517",
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
        DataType boolType = BooleanDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType intPtr = new PointerDataType(intType);
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004046d0",
                "CAtmospheric__Constructor",
                "CAnimation__ctor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("owner_thing", voidPtr)},
                "Wave517 source-parity owner correction: CAnimation constructor, not a CAtmospheric constructor. The only current caller is CComplexThing__SetAnimMode; the body stores owner_thing at +0x20, clears animation frame/mode fields at +0x08/+0x0c/+0x10/+0x14/+0x18/+0x1c, and schedules event 3000. Static retail evidence only; exact CAnimation layout, event semantics, runtime animation behavior, and rebuild parity remain unproven.",
                tags("animation", "constructor", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x00404790",
                "CAtmospheric__UpdateBlendState",
                "CAnimation__Process",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 source-parity owner correction: CAnimation process/update helper, not an atmospheric blend-state helper. The body advances frame state, loops ordinary animation modes, dispatches the owner FinishedPlayingCurrentAnimation slot when a non-looped animation reaches the end, and resamples frame increment through CThing__GetRenderThingFrameIncrement for fallback mode handling. Static retail evidence only; exact CAnimation field layout, event cadence, runtime animation behavior, and rebuild parity remain unproven.",
                tags("animation", "owner-correction", "process", "source-parity")
            ),
            new Spec(
                "0x00404860",
                "CAtmospheric__ConfigureTrail",
                "CAnimation__SetAnimMode",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("anim_mode", intType), param("reset_frame", intType), param("force_looped", intType)},
                "Wave517 source-parity owner correction: CAnimation::SetAnimMode-style helper, not atmospheric trail configuration. RET 0x0c confirms three explicit arguments; the body optionally resets frame state, stores anim_mode, calls owner CThing__GetRenderThingFrameIncrement with an out real-index pointer, stores the returned frame increment, and returns true. Static retail evidence only; exact EAnimMode values, CAnimation layout, runtime animation behavior, and rebuild parity remain unproven.",
                tags("animation", "mode", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004048c0",
                "CAtmospheric__GetInterpolatedBlendValue",
                "CAnimation__GetRenderFrame",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 source-parity owner correction: CAnimation render-frame accessor, not an atmospheric blend accessor. The body returns the current frame directly when prior/current frame fields match, otherwise interpolates previous and current frame values using global frame factor 0x008a9e44. Ghidra models the x87 float return as double. Static retail evidence only; exact frame fields, renderer interpolation behavior, and rebuild parity remain unproven.",
                tags("animation", "frame", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f3c80",
                "CAtmospheric__GetSamplerValueOrDefault",
                "CThing__GetRenderThingFrameIncrement",
                "__thiscall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr), param("anim_mode", intType), param("out_real_index", intPtr)},
                "Wave517 source-parity owner correction: CThing::GetRenderThingFrameIncrement-style helper, not an atmospheric sampler. The body dispatches the render-thing +0x38 frame-increment lookup when this+0x30 is present, passing anim_mode and out_real_index, otherwise returns 0.0. Ghidra models the x87 float return as double. Static retail evidence only; exact render-thing type, animation mode table, runtime animation behavior, and rebuild parity remain unproven.",
                tags("animation", "cthing", "owner-correction", "render", "source-parity")
            ),
            new Spec(
                "0x004f3e10",
                "CThing__ctor_like_004f3e10",
                "CComplexThing__ctor_base",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 source-parity rename/signature/comment hardening: CComplexThing constructor body. The body chains through CThing construction, installs CComplexThing vtables, copies the identity orientation matrix into this+0x3c, clears animation/motion-controller/mission-script/name pointers at +0x6c/+0x70/+0x74/+0x78, and returns this. Static retail evidence only; exact constructor exception-state details, concrete CComplexThing layout, runtime object creation behavior, and rebuild parity remain unproven.",
                tags("ccomplexthing", "constructor", "source-parity")
            ),
            new Spec(
                "0x004f3ee0",
                "CComplexThing__scalar_deleting_dtor",
                "CComplexThing__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave517 signature/comment hardening: CComplexThing scalar deleting destructor. Vtable data points here; the body calls CComplexThing__dtor_base, frees this through CDXMemoryManager__Free only when delete_flags bit 0 is set, and returns this. Static retail evidence only; allocator ownership, exact compiler emission identity, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("ccomplexthing", "destructor", "vtable-slot-1")
            ),
            new Spec(
                "0x004f3f00",
                "CComplexThing__dtor_base",
                "CComplexThing__dtor_base",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 signature/comment hardening: CComplexThing destructor-base helper. The body deletes the mission script at +0x74, animation at +0x6c, and motion controller at +0x70 when present, then chains into the CThing destructor-base. Static retail evidence only; exact ownership transfer, runtime shutdown ordering, and rebuild parity remain unproven.",
                tags("ccomplexthing", "destructor", "source-parity")
            ),
            new Spec(
                "0x004f3fd0",
                "CComplexThing__Init",
                "CComplexThing__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init", voidPtr)},
                "Wave517 source-parity comment correction: CComplexThing::Init-style body. The body calls CComplexThing__SetName from init name data, calls CComplexThing__SetScript from init script data, builds orientation from init Euler values into this+0x3c, then delegates to CThing__Init. Static retail evidence only; exact init-structure layout, runtime script startup, orientation math parity, and rebuild parity remain unproven.",
                tags("ccomplexthing", "init", "source-parity")
            ),
            new Spec(
                "0x004f4120",
                "CThing__SetName",
                "CComplexThing__SetName",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("name", charPtr)},
                "Wave517 source-parity owner correction: CComplexThing::SetName-style helper, not a base CThing helper. RET 0x4 confirms one explicit name argument; the body removes the old name from noticeboard 0x00855130, frees the old this+0x78 string, allocates/copies the new non-empty name, stores it at +0x78, and re-adds this to the named-thing noticeboard. Static retail evidence only; exact noticeboard layout, string allocator ownership, runtime naming behavior, and rebuild parity remain unproven.",
                tags("ccomplexthing", "name", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f41b0",
                "VFuncSlot_02_004f41b0",
                "CComplexThing__Shutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 source-parity rename/signature/comment hardening: CComplexThing shutdown virtual. The body removes/frees this+0x78 name state, clears objective/list participation, shuts down monitor state, and dispatches the scalar-deleting destructor path as part of the optimized shutdown flow. Static retail evidence only; exact virtual-slot table contract, runtime shutdown order, and rebuild parity remain unproven.",
                tags("ccomplexthing", "shutdown", "source-parity", "vtable-slot")
            ),
            new Spec(
                "0x004f4230",
                "CThing__SetSound",
                "CComplexThing__SetScript",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("script_name", charPtr)},
                "Wave517 source-parity owner correction: CComplexThing::SetScript-style helper, not a CThing sound helper. RET 0x4 confirms one explicit script_name argument; the body deletes any old mission script at +0x74, clones script object code by name when the input string is non-empty, allocates an IScript-sized object, stores it at +0x74, and schedules INIT_SCRIPT event 0x7d1. Static retail evidence only; exact IScript layout, mission-script bytecode semantics, runtime script startup, and rebuild parity remain unproven.",
                tags("ccomplexthing", "mission-script", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f43d0",
                "VFuncSlot_14_004f43d0",
                "CComplexThing__AddShutdownEvent",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 source-parity rename/signature/comment hardening: CComplexThing shutdown-event helper. Before forwarding into the base shutdown-event path, the body checks whether shutdown was already declared and, when a mission script is present at +0x74, sends the script died/shutdown notification, deletes the script, and clears the pointer. Static retail evidence only; exact script callback identity, event queue ordering, runtime behavior, and rebuild parity remain unproven.",
                tags("ccomplexthing", "mission-script", "shutdown", "source-parity")
            ),
            new Spec(
                "0x004f4430",
                "CComplexThing__StartDieProcess",
                "CComplexThing__StartDieProcess",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 signature/comment hardening: CComplexThing death-process hook. The body calls the base CThing StartDieProcess path and, when a mission script exists at +0x74, sends the script StartedDying-style callback before returning the base result. Static retail evidence only; exact mission-script callback identity, runtime death sequencing, and rebuild parity remain unproven.",
                tags("ccomplexthing", "death", "mission-script", "source-parity")
            ),
            new Spec(
                "0x004f4480",
                "CComplexThing__Hit",
                "CComplexThing__Hit",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("other_thing", voidPtr), param("collision_report", voidPtr)},
                "Wave517 signature/comment hardening: CComplexThing mission-script hit callback. RET 0x8 confirms other_thing and collision_report arguments; the body requires a mission script at +0x74 and a complex-thing-compatible other_thing before dispatching the script hit callback. Static retail evidence only; exact thing-type mask, collision-report layout, runtime hit behavior, and rebuild parity remain unproven.",
                tags("ccomplexthing", "collision", "hit", "mission-script", "source-parity")
            ),
            new Spec(
                "0x004f44a0",
                "CThing__AddTrail",
                "CComplexThing__SetAnimMode",
                "__thiscall",
                boolType,
                new ParameterImpl[] {param("this", voidPtr), param("anim_mode", intType), param("reset_frame", intType), param("force_looped", intType)},
                "Wave517 source-parity owner correction: CComplexThing::SetAnimMode-style helper, not CThing trail setup. RET 0x0c confirms three explicit arguments; the body lazily allocates a 0x24-byte CAnimation at this+0x6c with owner this, then delegates anim_mode/reset_frame/force_looped to CAnimation__SetAnimMode. Static retail evidence only; exact animation ownership, runtime animation behavior, and rebuild parity remain unproven.",
                tags("animation", "ccomplexthing", "mode", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f45a0",
                "CUnit__ResumeSavedScriptIfPresent",
                "CComplexThing__FinishedPlayingCurrentAnimation",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave517 source-parity owner correction: CComplexThing::FinishedPlayingCurrentAnimation-style helper, not a CUnit saved-script resume helper. The body dispatches the mission script finished-animation callback when this+0x74 is present and returns TRUE. Static retail evidence only; current callee naming may still need a separate script-layer review, and runtime animation/script behavior plus rebuild parity remain unproven.",
                tags("animation", "ccomplexthing", "mission-script", "owner-correction", "source-parity")
            ),
            new Spec(
                "0x004f45e0",
                "CExplosionInitThing__InvokeAndWarnUnknownVar",
                "CComplexThing__SetVar",
                "__stdcall",
                voidType,
                new ParameterImpl[] {param("var_name", voidPtr), param("data", voidPtr)},
                "Wave517 source-parity owner correction: CComplexThing::SetVar warning fallback, not an explosion-init helper. RET 0x8 confirms two stack arguments; the optimized body only asks var_name for its string text through a virtual call and prints the warning for an unknown variable in a script call. Static retail evidence only; exact CStringDataType/CDataType layouts, virtual dispatch identity, runtime script variable behavior, and rebuild parity remain unproven.",
                tags("ccomplexthing", "mission-script", "owner-correction", "source-parity", "warning")
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
            throw new IllegalStateException("Wave517 CComplexThing/Animation apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
