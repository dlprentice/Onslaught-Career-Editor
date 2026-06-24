//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
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

public class ApplyIScriptHeadWave578 extends GhidraScript {
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
            "iscript-head-wave578",
            "retail-binary-evidence",
            "mission-script",
            "iscript",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
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

            Function readBack = functionAtEntry(addr(spec.address));
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
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    private ParameterImpl[] thisOnly(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr)
        };
    }

    private ParameterImpl[] scalarDeletingParams(DataType voidPtr, DataType byteType) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("flags", byteType)
        };
    }

    private ParameterImpl[] thingRefParams(DataType voidPtr) throws Exception {
        return new ParameterImpl[] {
            param("this", voidPtr),
            param("referenced_thing", voidPtr)
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x005333b0",
                "IScript__Constructor",
                "__thiscall",
                voidPtr,
                "Wave578 owner/signature correction: this is the IScript constructor called by CComplexThing__SetScript after it allocates 0x3c bytes for the mission-script object. RET 0x8 proves ECX=this plus owner_complex_thing and script_object_code stack arguments. The body initializes the CMonitor base/list state, switches to vtable 0x005e4f08, stores owner_complex_thing at this+0x08 and this+0x10, stores script_object_code at this+0x0c, writes the script back-pointer at script_object_code+0x68, and clears local listener/state slots through this+0x38. Static retail evidence only; exact IScript layout names, exact source identity, runtime mission-script startup behavior, and rebuild parity remain unproven.",
                new String[] {"CMonitor__ctor_like_005333b0", "IScript__Constructor"},
                tags("constructor", "owner-correction", "rename-corrected", "monitor-base", "script-back-pointer"),
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("owner_complex_thing", voidPtr),
                    param("script_object_code", voidPtr)
                }
            ),
            new Spec(
                "0x00533430",
                "IScript__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                "Wave578 signature/comment hardening: IScript scalar-deleting destructor has ECX=this and RET 0x4 for one flags argument. It calls IScript__Destructor, frees this through DAT_009c3df0 when flags&1 is set, and returns this. Static retail evidence only; exact MSVC deleting-destructor ABI details, allocator ownership, runtime mission-script teardown behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__ScalarDeletingDestructor"},
                tags("destructor", "scalar-deleting-destructor", "vtable-slot"),
                scalarDeletingParams(voidPtr, byteType)
            ),
            new Spec(
                "0x00533450",
                "IScript__Destructor",
                "__thiscall",
                voidType,
                "Wave578 owner/signature correction: this is IScript teardown, not a constructor. It is called by IScript__ScalarDeletingDestructor, restores vtable 0x005e4f08, releases the script object at this+0x0c through its virtual destructor, walks the listener/state CSPtrSet at this+0x28, releases each contained object through virtual slot +4, clears the set, and finishes with CMonitor__Shutdown. Static retail evidence only; exact listener-node layout, why the set clear appears twice, runtime mission-script teardown behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__ctor_like_00533450", "IScript__Destructor"},
                tags("destructor", "rename-corrected", "listener-cleanup", "monitor-cleanup"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x00533500",
                "IScript__CallEvent0AndRegisterNestedListeners",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: IScript init-event helper has ECX=this and no stack cleanup. It resets when game state DAT_008a9ac0 equals 4; otherwise it calls CScriptObjectCode__CallEvent on this+0x0c with event id 0, then walks the script object-code list at +0x48/+0x50 and registers nested CScriptEventNB listeners through CScriptEventNB__RegisterEventListener. Static retail evidence only; exact list/member layouts, event-id enum names, runtime listener behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__CallEvent0AndRegisterNestedListeners"},
                tags("event-dispatch", "event-id-0", "listener-registration"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x005335a0",
                "IScript__CallEventId6_OrReset",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: IScript event-id-6 helper has ECX=this and no stack cleanup. It resets the script object-code VM when DAT_008a9ac0 equals 4; otherwise it calls CScriptObjectCode__CallEvent on this+0x0c with event id 6, DAT_0089c528 as the global result/object slot, and final flag 0. Static retail evidence only; exact event-id meaning, global-slot ownership, runtime event behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__CallEventId6_OrReset"},
                tags("event-dispatch", "event-id-6", "reset-gate"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x005335d0",
                "IScript__CreateThingRef",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: thing-ref event helper has ECX=this and RET 0x4 for one referenced_thing argument. It bails when script disable flag DAT_0089c7f0 is set or game state DAT_008a9ac0 equals 4, allocates an 8-byte datatype object from MissionScript/IScript.cpp line 0x10d, installs vtable 0x005e4af8, stores referenced_thing at +0x04, writes DAT_0089c528, then calls event id 1 through CScriptObjectCode__CallEvent on this+0x0c. Static retail evidence only; exact datatype class name, referenced thing layout, runtime event behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__CreateThingRef"},
                tags("thing-ref", "event-dispatch", "event-id-1", "script-result-object"),
                thingRefParams(voidPtr)
            ),
            new Spec(
                "0x00533660",
                "IScript__CallEventId5_OrReset",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: IScript event-id-5 helper has ECX=this and no stack cleanup. It resets the script object-code VM when DAT_008a9ac0 equals 4; otherwise it calls CScriptObjectCode__CallEvent on this+0x0c with event id 5, DAT_0089c528 as the global result/object slot, and final flag 0. Xrefs include CComplexThing and CUnit death/cleanup paths. Static retail evidence only; exact event-id meaning, runtime destruction behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__CallEventId5_OrReset"},
                tags("event-dispatch", "event-id-5", "reset-gate", "death-cleanup-callback"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x00533690",
                "IScript__CreateThingRefWithSquad",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: thing-ref-with-squad event helper has ECX=this and RET 0x4 for one referenced_thing argument. It allocates an 8-byte wrapper at IScript.cpp line 0x11e, temporarily installs vtable 0x005e4b4c, stores referenced_thing at +0x04, lazily creates a CSPtrSet at referenced_thing+0x04 when needed, registers the wrapper field in that set, switches to CThingPtrDataType vtable 0x005e4df8, writes DAT_0089c528, and calls event id 4 on this+0x0c. Static retail evidence only; exact squad/thing-pointer datatype identity, pointer-set ownership, runtime hit behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__CreateThingRefWithSquad"},
                tags("thing-ref", "event-dispatch", "event-id-4", "pointer-tracking", "script-result-object"),
                thingRefParams(voidPtr)
            ),
            new Spec(
                "0x005337e0",
                "IScript__CallEventId3_OrReset",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: IScript event-id-3 helper has ECX=this and no stack cleanup. It resets the script object-code VM when DAT_008a9ac0 equals 4; otherwise it calls CScriptObjectCode__CallEvent on this+0x0c with event id 3, DAT_0089c528 as the global result/object slot, and final flag 0. Xrefs include BattleEngine/CUnit/CComplexThing shutdown/deploy paths. Static retail evidence only; exact event-id meaning, runtime shutdown/deploy behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__CallEventId3_OrReset"},
                tags("event-dispatch", "event-id-3", "reset-gate", "shutdown-callback"),
                thisOnly(voidPtr)
            ),
            new Spec(
                "0x00533840",
                "IScript__RestoreSavedStateAndGotoInstruction",
                "__thiscall",
                voidType,
                "Wave578 signature/comment hardening: saved-state restore helper has ECX=this and no stack cleanup. When this+0x38 is non-null, it copies script state from that object, removes it from the CSPtrSet at this+0x28, releases the object through virtual slot +4, clears this+0x38, then either resets the VM when DAT_008a9ac0 equals 4 or resumes execution with CScriptObjectCode__GotoInstruction(DAT_0089c7f4). Static retail evidence only; exact saved-state object layout, instruction cursor semantics, runtime animation callback behavior, and rebuild parity remain unproven.",
                new String[] {"IScript__RestoreSavedStateAndGotoInstruction"},
                tags("state-restore", "goto-instruction", "animation-callback", "reset-gate"),
                thisOnly(voidPtr)
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.bad > 0 || stats.missing > 0) {
            throw new IllegalStateException("Wave578 IScript head tranche failed");
        }
    }
}
