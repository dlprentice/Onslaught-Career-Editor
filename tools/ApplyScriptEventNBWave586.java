//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
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

public class ApplyScriptEventNBWave586 extends GhidraScript {
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
            "scripteventnb-wave586",
            "retail-binary-evidence",
            "mission-script",
            "scripteventnb",
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00538470",
                "CScriptEventNB__UpdateWaypointFollowing",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("event_nb", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only CScriptEventNB waypoint-following update helper. The body reads the controlled thing at event_nb+0x08 and current waypoint at +0x14, compares 2D distance against a default/custom/large-unit threshold, advances or clears the waypoint, calls object-code state helpers when the path ends, and schedules the next message-2000 tick through CEventManager__AddEvent_AtTime(&EVENT_MANAGER,2000,event_nb,-1.0,0,0,0). Static retail evidence only; exact CScriptEventNB layout, waypoint structure, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__UpdateWaypointFollowing"},
                tags("waypoint-following", "event-manager-tick", "ecx-only")
            ),
            new Spec(
                "0x005385e0",
                "CScriptEventNB__HandleMessage",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("message", voidPtr) },
                "Wave586 signature/comment hardening: CScriptEventNB message dispatch method. RET 0x4 confirms one explicit message argument after ECX; message id 2000 calls UpdateWaypointFollowing, 0x7d1 removes/copies state for the message payload object, and 0x7d2 conditionally resets or calls event id 2 on this+0x0c when DAT_0089c7f0 is clear. Static retail evidence only; exact message layout, state machine semantics, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__HandleMessage"},
                tags("message-dispatch", "ret-4", "event-message-2000")
            ),
            new Spec(
                "0x005386b0",
                "CScriptEventNB__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", byteType) },
                "Wave586 signature/comment hardening: MSVC scalar deleting destructor wrapper. RET 0x4 confirms the delete_flags stack argument; the body calls CScriptEventNB__Destructor and frees this through CDXMemoryManager__Free when delete_flags bit 0 is set. Static retail evidence only; exact allocation owner, destructor hierarchy, runtime lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__ScalarDeletingDestructor"},
                tags("destructor", "scalar-deleting-destructor", "ret-4")
            ),
            new Spec(
                "0x005386d0",
                "CScriptEventNB__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("event_nb", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only CScriptEventNB destructor body. The routine installs the base vtable at 0x005e4f34, destroys event_nb+0x08 when present, removes the object from DAT_00855190, and then calls CMonitor__Shutdown. Static retail evidence only; exact ownership/lifetime rules, monitor base-class identity, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__Destructor"},
                tags("destructor", "base-vtable", "monitor-shutdown", "ecx-only")
            ),
            new Spec(
                "0x00538760",
                "CScriptEventNB__Init",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("event_nb", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only initializer for a CScriptEventNB instance. The body zeros fields at +0x04 and +0x08, then installs the main CScriptEventNB vtable at 0x005e4f44. Static retail evidence only; exact class layout, constructor call provenance, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__Init"},
                tags("initializer", "vtable", "ecx-only")
            ),
            new Spec(
                "0x00538780",
                "CScriptEventNB__ScalarDeletingDestructor2",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("delete_flags", byteType) },
                "Wave586 signature/comment hardening: second MSVC scalar deleting destructor wrapper reached from the 0x005e4f44 vtable. RET 0x4 confirms the delete_flags stack argument; the body calls CScriptEventNB__BaseDestructor and frees this through CDXMemoryManager__Free when delete_flags bit 0 is set. Static retail evidence only; exact vtable/lifetime split, allocation owner, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__ScalarDeletingDestructor2"},
                tags("destructor", "scalar-deleting-destructor", "ret-4", "vtable-slot")
            ),
            new Spec(
                "0x005387b0",
                "CScriptEventNB__ClearEventListeners",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("listener_entry", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only listener-entry cleanup helper. The body destroys the stored event-name/object pointer, walks the listener_entry+0x04 CSPtrSet deleting monitor deletion-event wrappers with CMonitor__DeleteDeletionEvent and CDXMemoryManager__Free, then clears the set. Static retail evidence only; exact listener-entry layout, wrapper ownership, runtime event behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__ClearEventListeners"},
                tags("listener-cleanup", "csptrset", "ecx-only")
            ),
            new Spec(
                "0x00538860",
                "CScriptEventNB__CreateEventListener",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("event_nb", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only helper that allocates the CScriptEventNB listener set at event_nb+0x08. The body allocates 0x10 bytes with OID type 0x76 and ScriptEventNB.cpp line 0x42, initializes it with CSPtrSet__Init when allocation succeeds, and stores null on failure. Static retail evidence only; exact allocation type name, set layout, runtime event behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__CreateEventListener"},
                tags("listener-allocation", "csptrset", "ecx-only")
            ),
            new Spec(
                "0x005388d0",
                "CScriptEventNB__DestroyAllEvents",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("event_nb", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only vtable cleanup routine called by game shutdown and the 0x005e4f44 vtable. It calls CMonitor__Shutdown_Core, walks the event_nb+0x08 listener set, calls CScriptEventNB__ClearEventListeners for each listener entry, frees the entries, clears and frees the listener set, and nulls event_nb+0x08. Static retail evidence only; exact listener-set ownership, shutdown ordering, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__DestroyAllEvents"},
                tags("listener-cleanup", "vtable-slot", "shutdown", "ecx-only")
            ),
            new Spec(
                "0x00538950",
                "CScriptEventNB__BaseDestructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("event_nb", voidPtr) },
                "Wave586 signature/comment hardening: ECX-only base-destructor helper reached from CScriptEventNB__ScalarDeletingDestructor2 and a nearby tail-jump thunk. The routine restores the main vtable pointer at 0x005e4f44 and tail-calls CMonitor__Shutdown. Static retail evidence only; exact base-class role, vtable lifetime ordering, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__BaseDestructor"},
                tags("destructor", "monitor-shutdown", "ecx-only")
            ),
            new Spec(
                "0x00538960",
                "CScriptEventNB__RegisterEventListener",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr), param("event_name_ref", voidPtr), param("event_function", voidPtr) },
                "Wave586 signature/comment hardening: CScriptEventNB listener registration method. IScript__CallEvent0AndRegisterNestedListeners loads ECX=&DAT_0089c590 and pushes event_name_ref plus event_function before the call; RET 0x8 confirms two explicit stack arguments. The body searches existing listeners by vtable-name getter +0x38, appends wrapper records to matching listeners, or allocates a new 0x18 listener entry, clones the name through vtable slot +0x48, links monitor deletion records, and appends it to the listener set. Static retail evidence only; exact listener/event-function layouts, symbol ownership, runtime event behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__RegisterEventListener"},
                tags("listener-registration", "ret-8", "iscript-xref", "csptrset")
            ),
            new Spec(
                "0x00538b70",
                "CScriptEventNB__PostEvent",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("event_name", charPtr) },
                "Wave586 signature/comment hardening: CScriptEventNB named-event posting method. RET 0x4 confirms one explicit event_name argument after ECX; the body warns through CConsole__Printf when no listener-set game-playing flag is set and event_name is not \"game playing\", then scans listener names with vtable getter +0x38, marks matching listener entries as triggered, and executes each stored CEventFunction. Static retail evidence only; exact listener layout, string lifetime, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__PostEvent"},
                tags("post-event", "ret-4", "listener-dispatch", "event-function")
            ),
            new Spec(
                "0x00538c70",
                "CScriptEventNB__HandleEventMessage",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("message", voidPtr) },
                "Wave586 signature/comment hardening: CScriptEventNB event-manager message handler reached from the 0x005e4f44 vtable. RET 0x4 confirms one explicit message argument after ECX; message id 2000 extracts the payload event name through nested vtable getter +0x38, uses the same warning/listener scan/trigger/Execute loop as PostEvent, and then destroys the payload object. Static retail evidence only; exact event payload layout, vtable owner, runtime mission-script behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CScriptEventNB__HandleEventMessage"},
                tags("event-message-handler", "ret-4", "vtable-slot", "event-function")
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
        if (stats.missing > 0 || stats.bad > 0) {
            throw new RuntimeException("Wave586 apply encountered missing/bad rows");
        }
    }
}
